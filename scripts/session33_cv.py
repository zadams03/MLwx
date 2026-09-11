"""Session 33: seasonal cross-validation on the 1.5-year feature-complete
window (sealed test year NOT opened).

ONE JOB: answer whether the session-32 scout's 4-of-5-losing-to-raw-GFS
result was an artefact of its ~6-month inner-training window (Jan-Jul 2024,
no autumn/winter) rather than a real limit of the recipe. This session
removes that artifact with BLOCKED CROSS-VALIDATION across the whole
1.5-year feature-complete window, so every fold trains on ~15 months
spanning all calendar positions.

THIS IS A DIAGNOSTIC INSIDE THE TRAINING WINDOW. IT LOCKS NOTHING. THE SEALED
TEST YEAR (2025-08-01 -> 2026-07-31, DECISIONS D13) IS NEVER LOADED, PULLED,
JOINED, OR SCORED, FOR ANY AIRPORT OR FOLD. Every date loaded is asserted to
fall before 2025-08-01.

No new data is pulled: this reuses the cloud/wind raw already saved under
data/raw/features/ (session 32) plus the existing temperature/observation
rows under data/raw/.

METHODOLOGY NOTE -- why blocked CV is leakage-safe here (see also the
DECISIONS finding this session writes). Blocked leave-one-block-out CV
trains on data temporally surrounding each held-out block, which departs
from the strict train-earlier/test-later split used for the sealed test
(SPEC 2.1a). That is acceptable for this diagnostic, and ONLY because no
feature carries temporal memory: every feature is a same-day GFS forecast
value or a calendar-position encoding (forecast_temp_c, season_sin,
season_cos, cloud_cover, wind_speed_10m -- all _previous_day1, all same-day
values), so a training row dated after a held-out block cannot encode that
block's outcome -- there is no autoregressive or lagged channel to leak
through. The sealed test remains strictly train-past-only; this CV is an
internal generalization estimate, not that test.

Window (all folds live here): 2024-01-19 to 2025-07-31 (~18 months,
feature-complete at every airport, DECISIONS F85).

Six contiguous ~3-month calendar blocks (not named seasons, so the scheme is
hemisphere-agnostic):
    A  2024-01-19 -> 2024-04-18
    B  2024-04-19 -> 2024-07-18
    C  2024-07-19 -> 2024-10-18
    D  2024-10-19 -> 2025-01-18
    E  2025-01-19 -> 2025-04-18
    F  2025-04-19 -> 2025-07-31

Each fold holds out one block and trains on the other five (~15 months,
spanning the full calendar cycle). Every calendar month is a held-out test
in at least one fold; the training set always covers all seasons.

Four rungs, identical locked LightGBM settings (D21.4) for both fitted
models -- nothing tuned, nothing hand-picked per airport:
    - raw GFS        (no fit)
    - + mean-bias    (fit on the fold's training blocks only)
    - 3-feature      (forecast_temp_c, season_sin, season_cos)
    - 5-feature      (+ cloud_cover, wind_speed_10m)
Persistence (previous calendar day's observation) is reported for context
only -- it needs no fitting and is not part of the CV ladder.
"""

import csv
import json
import math
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
FEAT = ROOT / "data" / "raw" / "features"

# --- making LightGBM importable on this machine -------------------------------
# See DECISIONS Q16/D24. Unchanged from every earlier modelling script.
_SENTINEL = "MLWX_LIBOMP_PATH_SET"
if _SENTINEL not in os.environ:
    _omp = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" \
        / "site-packages" / "sklearn" / ".dylibs"
    if (_omp / "libomp.dylib").exists():
        os.environ[_SENTINEL] = "1"
        os.environ["DYLD_LIBRARY_PATH"] = \
            str(_omp) + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
        os.execv(sys.executable, [sys.executable] + sys.argv)

import numpy as np                                        # noqa: E402
import lightgbm as lgb                                    # noqa: E402


# ------------------------------------------------------------------ constants

# SPEC 3.4: station code, target hour (UTC).
AIRPORTS = {
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

WINDOW_START = date(2024, 1, 19)
WINDOW_END = date(2025, 7, 31)

# Hard wall. Nothing at or after this date is loaded, for any series, at any
# airport (DECISIONS D13). This is the hard line of the session.
SEALED_FROM = date(2025, 8, 1)

BLOCKS = [
    ("A", date(2024, 1, 19), date(2024, 4, 18)),
    ("B", date(2024, 4, 19), date(2024, 7, 18)),
    ("C", date(2024, 7, 19), date(2024, 10, 18)),
    ("D", date(2024, 10, 19), date(2025, 1, 18)),
    ("E", date(2025, 1, 19), date(2025, 4, 18)),
    ("F", date(2025, 4, 19), date(2025, 7, 31)),
]
BLOCK_NAMES = [b[0] for b in BLOCKS]


def block_of(d):
    for name, s, e in BLOCKS:
        if s <= d <= e:
            return name
    raise ValueError(f"date {d} outside all blocks")


# The two yearly chunk files that cover the window, for every airport (same
# naming convention as sessions 03b/10/15/20/26/32).
FC_CHUNKS = [("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31")]
OBS_CHUNKS = [("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31")]

CLOUDWIND_START = "2024-01-19"
CLOUDWIND_END = "2025-07-31"

# The locked recipe's settings (DECISIONS D21.4), UNCHANGED, used for BOTH
# fitted models in every fold. Nothing is tuned; no hyperparameter search.
LGB_PARAMS = dict(
    objective="regression_l1",
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=15,
    min_child_samples=40,
    subsample=1.0,
    colsample_bytree=1.0,
    reg_alpha=0.0,
    reg_lambda=0.0,
    random_state=42,
    n_jobs=1,
    deterministic=True,
    force_row_wise=True,
    verbose=-1,
)

FEATURES_3 = ["forecast_temp_c", "season_sin", "season_cos"]
FEATURES_5 = FEATURES_3 + ["cloud_cover", "wind_speed_10m"]

OUT = ROOT / "notes" / "session-33-check-output.txt"


class Tee:
    def __init__(self, path):
        self.f = open(path, "w")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def line(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ loading

def load_forecast_temp(station, target_hour):
    """{date: temp_or_None} for the target hour, restricted to the CV
    window. Never opens a 2026 file."""
    series = {}
    for start, end in FC_CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_{station}_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        for t_str, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
            if t.hour != target_hour:
                continue
            dt = t.date()
            if dt < WINDOW_START or dt > WINDOW_END:
                continue
            assert dt < SEALED_FROM, "a sealed forecast date was loaded"
            series[dt] = v
    return series


def load_cloud_wind(station, target_hour):
    """{date: (cloud_or_None, wind_or_None)} for the target hour, session
    32's own pull, restricted to the CV window."""
    path = FEAT / (f"openmeteo_previousruns_gfs_global_{station}_"
                   f"{CLOUDWIND_START}_{CLOUDWIND_END}_cloudwind.json")
    with open(path) as f:
        d = json.load(f)
    h = d["hourly"]
    series = {}
    for t_str, c, w in zip(h["time"], h["cloud_cover_previous_day1"],
                            h["wind_speed_10m_previous_day1"]):
        t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
        if t.hour != target_hour:
            continue
        dt = t.date()
        if dt < WINDOW_START or dt > WINDOW_END:
            continue
        assert dt < SEALED_FROM, "a sealed forecast date was loaded"
        series[dt] = (c, w)
    return series


def load_obs(station, target_hour):
    """{date: temp} for the target hour, the D14 pairing rule (SPEC 4.5):
    nearest routine report, dropped if more than 15 minutes from the hour.
    Restricted to the CV window."""
    series = {}
    outside_15min = 0
    no_temp = 0
    for start, end in OBS_CHUNKS:
        path = RAW / f"iem_asos_{station}_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != target_hour:
                    continue
                dt = nearest.date()
                if dt < WINDOW_START or dt > WINDOW_END:
                    continue
                if dt >= SEALED_FROM:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[dt] = float(raw)
    return series, outside_15min, no_temp


def all_days(start, end):
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------------ features

def year_fraction(d):
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0
                                             or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def features_3(rows):
    x = []
    for r in rows:
        a = 2 * math.pi * year_fraction(r["date"])
        x.append([r["fc"], math.sin(a), math.cos(a)])
    return np.array(x, dtype=float)


def features_5(rows):
    x = []
    for r in rows:
        a = 2 * math.pi * year_fraction(r["date"])
        x.append([r["fc"], math.sin(a), math.cos(a), r["cloud"], r["wind"]])
    return np.array(x, dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


# ------------------------------------------------------------------ join

def join_airport(station, target_hour):
    fc = load_forecast_temp(station, target_hour)
    cw = load_cloud_wind(station, target_hour)
    obs, obs_far, obs_no_temp = load_obs(station, target_hour)

    counts = dict(no_fc=0, null_fc=0, no_cloudwind=0, null_cloud=0,
                  null_wind=0, no_obs=0)
    rows = []
    for d in all_days(WINDOW_START, WINDOW_END):
        bad = []
        f_val = fc.get(d, "absent")
        if f_val == "absent":
            counts["no_fc"] += 1
            bad.append("no forecast row")
        elif f_val is None:
            counts["null_fc"] += 1
            bad.append("forecast null")

        cw_val = cw.get(d, "absent")
        if cw_val == "absent":
            counts["no_cloudwind"] += 1
            bad.append("no cloud/wind row")
        else:
            c, w = cw_val
            if c is None:
                counts["null_cloud"] += 1
                bad.append("cloud null")
            if w is None:
                counts["null_wind"] += 1
                bad.append("wind null")

        o_val = obs.get(d)
        if o_val is None:
            counts["no_obs"] += 1
            bad.append("no usable observation")

        if bad:
            continue

        row = {"date": d, "fc": float(f_val), "obs": float(o_val),
               "resid": float(o_val) - float(f_val),
               "cloud": float(cw_val[0]), "wind": float(cw_val[1]),
               "block": block_of(d)}
        rows.append(row)

    return rows, obs, counts, obs_far, obs_no_temp


# ------------------------------------------------------------------ per-airport CV

def run_airport(station, target_hour, results):
    line(f"{station} -- target hour {target_hour:02d}:00 UTC (SPEC 3.4)")

    rows, obs_all, counts, obs_far, obs_no_temp = join_airport(station, target_hour)

    for r in rows:
        assert WINDOW_START <= r["date"] <= WINDOW_END
        assert r["date"] < SEALED_FROM

    sub("Task 1 -- pull/join drop counts (whole 1.5-year window)")
    total_days = len(all_days(WINDOW_START, WINDOW_END))
    print(f"    calendar days in the window ({WINDOW_START} to {WINDOW_END}): "
          f"{total_days}")
    print(f"    no forecast row                : {counts['no_fc']}")
    print(f"    forecast row present but null  : {counts['null_fc']}")
    print(f"    no cloud/wind row               : {counts['no_cloudwind']}")
    print(f"    cloud value null                : {counts['null_cloud']}")
    print(f"    wind value null                 : {counts['null_wind']}")
    print(f"    no usable observation           : {counts['no_obs']}")
    print(f"      (of which, obs >15 min from hour, dropped by D14: {obs_far})")
    print(f"      (of which, obs report carried no temperature: {obs_no_temp})")
    print(f"    rows kept (usable in at least one fold): {len(rows)} of {total_days}")

    by_block = {}
    for r in rows:
        by_block.setdefault(r["block"], []).append(r)
    print(f"    rows kept per block: " +
          ", ".join(f"{b}={len(by_block.get(b, []))}" for b in BLOCK_NAMES))

    # -------------------------------------------------------- blocked CV
    oof = {name: {} for name in ("Raw GFS", "+ mean-bias", "3-feature", "5-feature")}
    per_fold_mae = {name: {} for name in oof}
    in_sample_errs = {"3-feature": [], "5-feature": []}
    oof_errs_pooled = {"3-feature": [], "5-feature": []}
    gain_shares = []  # list of dict(feature -> pct) per fold
    split_counts = []

    for held_out in BLOCK_NAMES:
        train_rows = [r for r in rows if r["block"] != held_out]
        test_rows = by_block.get(held_out, [])
        if not test_rows:
            continue

        y_train = np.array([r["resid"] for r in train_rows], dtype=float)
        mean_bias = float(np.mean(y_train)) if len(y_train) else float("nan")

        x3_tr = features_3(train_rows)
        x5_tr = features_5(train_rows)
        m3 = lgb.LGBMRegressor(**LGB_PARAMS)
        m3.fit(x3_tr, y_train)
        m5 = lgb.LGBMRegressor(**LGB_PARAMS)
        m5.fit(x5_tr, y_train)

        # in-sample (training-fold) errors, pooled across folds (Task 3)
        pred3_tr = m3.predict(x3_tr)
        pred5_tr = m5.predict(x5_tr)
        for i, r in enumerate(train_rows):
            in_sample_errs["3-feature"].append(
                (r["fc"] + float(pred3_tr[i])) - r["obs"])
            in_sample_errs["5-feature"].append(
                (r["fc"] + float(pred5_tr[i])) - r["obs"])

        x3_te = features_3(test_rows)
        x5_te = features_5(test_rows)
        pred3_te = m3.predict(x3_te)
        pred5_te = m5.predict(x5_te)

        fold_errs = {name: [] for name in oof}
        for i, r in enumerate(test_rows):
            e_raw = r["fc"] - r["obs"]
            e_mb = (r["fc"] + mean_bias) - r["obs"]
            e_3 = (r["fc"] + float(pred3_te[i])) - r["obs"]
            e_5 = (r["fc"] + float(pred5_te[i])) - r["obs"]

            oof["Raw GFS"][r["date"]] = e_raw
            oof["+ mean-bias"][r["date"]] = e_mb
            oof["3-feature"][r["date"]] = e_3
            oof["5-feature"][r["date"]] = e_5

            fold_errs["Raw GFS"].append(e_raw)
            fold_errs["+ mean-bias"].append(e_mb)
            fold_errs["3-feature"].append(e_3)
            fold_errs["5-feature"].append(e_5)

            oof_errs_pooled["3-feature"].append(e_3)
            oof_errs_pooled["5-feature"].append(e_5)

        for name in oof:
            per_fold_mae[name][held_out] = mae(fold_errs[name]) if fold_errs[name] else float("nan")

        gain = m5.booster_.feature_importance(importance_type="gain")
        split = m5.booster_.feature_importance(importance_type="split")
        gshare = gain / gain.sum() * 100 if gain.sum() else np.zeros_like(gain)
        gain_shares.append(dict(zip(FEATURES_5, gshare)))
        split_counts.append(dict(zip(FEATURES_5, split)))

    # every row must have received exactly one OOF prediction from each rung
    for name in oof:
        assert len(oof[name]) == len(rows), \
            f"{station} {name}: {len(oof[name])} OOF preds vs {len(rows)} rows"

    sub("Task 2 -- per-fold MAE (degC), four rungs")
    print(f"    {'block':<6} " + " ".join(f"{n:>16}" for n in oof))
    for b in BLOCK_NAMES:
        if b not in by_block:
            continue
        vals = [per_fold_mae[n].get(b, float('nan')) for n in oof]
        print(f"    {b:<6} " + " ".join(f"{v:>16.3f}" for v in vals))

    sub("Task 2 -- pooled out-of-fold MAE and skill vs raw GFS (headline)")
    pooled_mae = {}
    for name in oof:
        errs = [oof[name][d] for d in oof[name]]
        pooled_mae[name] = mae(errs)
    raw_mae = pooled_mae["Raw GFS"]
    print(f"    {'rung':<14} {'MAE degC':>9} {'skill vs raw GFS':>18} {'n days':>8}")
    for name in oof:
        skill = 100 * (1 - pooled_mae[name] / raw_mae) if name != "Raw GFS" else 0.0
        print(f"    {name:<14} {pooled_mae[name]:>9.3f} {skill:>17.1f}% {len(oof[name]):>8}")

    # -------------------------------------------------------- persistence
    common = []
    no_prev = []
    for r in rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev.append(r["date"])
            continue
        common.append((r, float(prev)))

    sub("Persistence (context only -- not part of the CV ladder)")
    print(f"    rows with a usable previous-day observation: {len(common)} of {len(rows)}")
    print(f"    dropped (no previous-day observation in the window): {len(no_prev)}")
    persist_errs = [p - r["obs"] for r, p in common]
    persist_mae = mae(persist_errs) if persist_errs else float("nan")
    print(f"    Persistence MAE: {persist_mae:.3f} degC  (n={len(common)})")
    # raw GFS on the exact same common subset, for a fair side-by-side
    raw_on_common = mae([r["fc"] - r["obs"] for r, _ in common])
    print(f"    Raw GFS MAE on that same subset: {raw_on_common:.3f} degC "
          f"(for comparability with the persistence figure above)")

    # -------------------------------------------------------- Task 3: overfit
    sub("Task 3 -- overfit diagnostic: pooled in-sample vs pooled out-of-fold MAE")
    for name, key in (("3-feature", "3-feature"), ("5-feature", "5-feature")):
        in_mae = mae(in_sample_errs[key])
        oof_mae = mae(oof_errs_pooled[key])
        print(f"    {name:<12} in-sample (pooled, {len(in_sample_errs[key])} "
              f"train-rows-across-folds) = {in_mae:.3f}   "
              f"out-of-fold (pooled, {len(oof_errs_pooled[key])} rows) = {oof_mae:.3f}   "
              f"gap = {oof_mae - in_mae:+.3f}")

    sub("Task 3 -- 5-feature feature importances, averaged across the six folds")
    avg_gain = {f: float(np.mean([g[f] for g in gain_shares])) for f in FEATURES_5}
    avg_split = {f: float(np.mean([s[f] for s in split_counts])) for f in FEATURES_5}
    print(f"    {'feature':<18} {'mean gain share':>16} {'mean splits':>12}")
    for f in FEATURES_5:
        print(f"    {f:<18} {avg_gain[f]:>15.1f}% {avg_split[f]:>12.1f}")

    results[station] = dict(
        raw_mae=raw_mae,
        mean_bias_mae=pooled_mae["+ mean-bias"],
        f3_mae=pooled_mae["3-feature"],
        f5_mae=pooled_mae["5-feature"],
        persist_mae=persist_mae,
        n_days=len(rows),
        per_fold_mae=per_fold_mae,
        gain5=avg_gain,
        in3=mae(in_sample_errs["3-feature"]),
        in5=mae(in_sample_errs["5-feature"]),
        oof3=mae(oof_errs_pooled["3-feature"]),
        oof5=mae(oof_errs_pooled["5-feature"]),
    )


# ------------------------------------------------------------------ headline

def headline(results):
    line("Task 4 -- the two branch reads (report, do NOT decide)")

    sub("Branch A -- trained on a full calendar cycle, does 3-feature beat raw GFS?")
    print(f"    {'airport':<8} {'raw GFS':>9} {'3-feature':>10} {'beats?':>8} {'skill %':>9}")
    n_3beatsraw = 0
    for st, r in results.items():
        beats = r["f3_mae"] < r["raw_mae"]
        n_3beatsraw += beats
        skill = 100 * (1 - r["f3_mae"] / r["raw_mae"])
        print(f"    {st:<8} {r['raw_mae']:>9.3f} {r['f3_mae']:>10.3f} "
              f"{('YES' if beats else 'no'):>8} {skill:>+8.1f}")
    print(f"    3-feature beats raw GFS (full-cycle CV) at {n_3beatsraw} of "
          f"{len(results)} airports")
    print("    Session 32's scout (6-month window): 3-feature lost to raw GFS at "
          "4 of 5 airports (EGLC, LFPG, DSM, RNO).")

    sub("Branch B -- does 5-feature beat 3-feature out-of-fold, and beat raw GFS?")
    print(f"    {'airport':<8} {'3-feat':>9} {'5-feat':>9} {'5 beats 3?':>11} "
          f"{'5 beats raw?':>13}")
    n_5beats3 = 0
    n_5beatsraw = 0
    for st, r in results.items():
        b3 = r["f5_mae"] < r["f3_mae"]
        braw = r["f5_mae"] < r["raw_mae"]
        n_5beats3 += b3
        n_5beatsraw += braw
        print(f"    {st:<8} {r['f3_mae']:>9.3f} {r['f5_mae']:>9.3f} "
              f"{('YES' if b3 else 'no'):>11} {('YES' if braw else 'no'):>13}")
    print(f"    5-feature beats 3-feature at {n_5beats3} of {len(results)} airports")
    print(f"    5-feature beats raw GFS at {n_5beatsraw} of {len(results)} airports")

    sub("Reno specifically")
    r = results["RNO"]
    print(f"    RNO raw GFS pooled OOF MAE      : {r['raw_mae']:.3f}")
    print(f"    RNO 3-feature pooled OOF MAE    : {r['f3_mae']:.3f}")
    print(f"    RNO 5-feature pooled OOF MAE    : {r['f5_mae']:.3f}")
    print(f"    RNO 5-feature cloud_cover gain share  : {r['gain5']['cloud_cover']:.1f}%")
    print(f"    RNO 5-feature wind_speed_10m gain share: {r['gain5']['wind_speed_10m']:.1f}%")

    sub("overfit gap summary, all airports")
    print(f"    {'airport':<8} {'3-feat gap':>11} {'5-feat gap':>11}")
    for st, r in results.items():
        print(f"    {st:<8} {r['oof3'] - r['in3']:>+11.3f} {r['oof5'] - r['in5']:>+11.3f}")

    sub("one-line synthesis (report only, the owner decides)")
    print(f"    Branch A: 3-feature beats raw GFS at {n_3beatsraw} of "
          f"{len(results)} airports with a full seasonal cycle in training "
          f"(against 1 of 5 on the session-32 short window).")
    print(f"    Branch B: 5-feature beats 3-feature at {n_5beats3} of "
          f"{len(results)} airports and beats raw GFS at {n_5beatsraw} of "
          f"{len(results)} airports.")
    print("    Whether this points to \"the 1.5-year window is workable\" or "
          "\"a deeper source is needed\" is flagged for the owner in the "
          "DECISIONS finding, not decided here.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 33 -- seasonal blocked cross-validation, 1.5-year window. "
         "SEALED TEST NOT OPENED.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"CV window     : {WINDOW_START} to {WINDOW_END}")
    print(f"sealed test   : {SEALED_FROM} onward -- NOT LOADED")
    print(f"blocks        : " + ", ".join(f"{n} [{s}..{e}]" for n, s, e in BLOCKS))
    print(f"model settings (identical for both fitted models, D21.4): {LGB_PARAMS}")
    print(f"3-feature set: {FEATURES_3}")
    print(f"5-feature set: {FEATURES_5}")

    results = {}
    for station, target_hour in AIRPORTS.items():
        run_airport(station, target_hour, results)

    headline(results)

    line("END")
    print("Raw files untouched (no new raw pulled or written). Nothing was "
          "filled (SPEC 2.2). No forecast or observation date on or after "
          "2025-08-01 was loaded, printed, averaged or fitted on, at any "
          "airport or fold. No recipe was locked. Nothing was committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
