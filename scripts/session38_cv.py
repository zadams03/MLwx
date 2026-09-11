"""Session 38, Task 3 (+ Task 5 headline): blocked seasonal cross-validation
of the richer-features recipe on the FULL v16 window (2021-03-24 to
2025-07-31, ~4.4 years), using GRIB-derived features throughout.

ONE JOB: F87 (session 33) ran this same blocked-CV design on the 1.5-year
Open-Meteo feature-complete window and found 3-feature recovers to beating
raw GFS at 4 of 5 airports, and 5-feature beats 3-feature at 4 of 5 and raw
GFS at 4 of 5 -- but that window was capped at ~1.5 years because cloud/wind
were only free on Open-Meteo from 2024-01-19 onward. The GRIB build (steps
1-2, sessions 36-37) removed that cap: cloud cover and wind speed are now
available from GRIB across the full ~4.4-year training window. This session
re-runs the same blocked-CV design on that full window, GRIB source
throughout (temperature, cloud cover, wind speed all GRIB-derived, so the
3-vs-5 comparison stays features-only, same source).

THIS IS A DIAGNOSTIC INSIDE THE TRAINING WINDOW. IT LOCKS NOTHING. THE SEALED
TEST YEAR (2025-08-01 -> 2026-07-31) IS NEVER LOADED -- the input file
(data/processed/session38_joined.csv, Task 2) ends 2025-07-31 by
construction, asserted below.

Leakage-safety justification for blocked CV (identical to F87's, restated):
every feature is a same-day GRIB forecast value (forecast_temp_c,
cloud_cover, wind_speed_10m) or a calendar-position encoding (season_sin,
season_cos) -- no lagged or autoregressive feature -- so a training row dated
outside a held-out block cannot encode that block's outcome. The sealed test
remains strictly train-past-only; this CV is an internal generalisation
estimate, not that test.

Window: 2021-03-24 to 2025-07-31 (1,591 days), tiled into 17 contiguous,
near-equal (~93-94 day) blocks -- no leftover stub block, unlike a fixed
91-day tiling of this same range, which would leave the final block only 44
days long. Every day is predicted out-of-fold exactly once.

Four rungs, identical locked LightGBM settings (D21.4) for both fitted
models -- nothing tuned, nothing hand-picked per airport:
    - raw GFS (GRIB)     (no fit -- the GRIB-derived, elevation-corrected
                           forecast temperature itself)
    - + mean-bias         (fit on the fold's training blocks only)
    - 3-feature           (forecast_temp_c, season_sin, season_cos)
    - 5-feature           (+ cloud_cover, wind_speed_10m)
Persistence (previous calendar day's IEM observation) is reported for
context only.
"""

import csv
import math
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

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

AIRPORTS = {  # SPEC 3.4: station code, target hour (UTC)
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

WINDOW_START = date(2021, 3, 24)
WINDOW_END = date(2025, 7, 31)
SEALED_FROM = date(2025, 8, 1)

OBS_CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
]

N_BLOCKS = 17


def build_blocks():
    """17 contiguous, near-equal blocks tiling WINDOW_START..WINDOW_END with
    no gap and no leftover stub (unlike a fixed 91-day step, which would
    leave a 44-day final block on this exact date range)."""
    total = (WINDOW_END - WINDOW_START).days + 1
    base, rem = divmod(total, N_BLOCKS)
    blocks = []
    d = WINDOW_START
    for i in range(N_BLOCKS):
        length = base + (1 if i < rem else 0)
        e = d + timedelta(days=length - 1)
        blocks.append((f"B{i + 1:02d}", d, e))
        d = e + timedelta(days=1)
    assert blocks[-1][2] == WINDOW_END
    return blocks


BLOCKS = build_blocks()
BLOCK_NAMES = [b[0] for b in BLOCKS]


def block_of(d):
    for name, s, e in BLOCKS:
        if s <= d <= e:
            return name
    raise ValueError(f"date {d} outside all blocks")


# The locked recipe's settings (DECISIONS D21.4), UNCHANGED, used for both
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

OUT = ROOT / "notes" / "session-38-cv-output.txt"


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

def load_joined():
    """station -> [rows], from Task 2's output. Every row already carries
    forecast_temp_c, cloud_cover, wind_speed_10m, obs_temp_c, resid."""
    by_station = {st: [] for st in AIRPORTS}
    with open(PROCESSED / "session38_joined.csv") as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["target_date"])
            assert WINDOW_START <= d <= WINDOW_END
            assert d < SEALED_FROM, "a sealed-test date is present in the joined file"
            by_station[r["station"]].append({
                "date": d,
                "fc": float(r["forecast_temp_c"]),
                "cloud": float(r["cloud_cover"]),
                "wind": float(r["wind_speed_10m"]),
                "obs": float(r["obs_temp_c"]),
                "resid": float(r["resid"]),
                "block": block_of(d),
            })
    return by_station


def load_obs_all(station, target_hour):
    """{date: temp} for the target hour, full window, D14 rule -- used only
    for the persistence baseline's previous-day lookup (independent of which
    rows the GRIB join kept)."""
    series = {}
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
                if dt < WINDOW_START or dt > WINDOW_END or dt >= SEALED_FROM:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    continue
                series[dt] = float(raw)
    return series


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


# ------------------------------------------------------------------ per-airport CV

def run_airport(station, target_hour, rows, results):
    line(f"{station} -- target hour {target_hour:02d}:00 UTC (SPEC 3.4), "
         f"GRIB source throughout")

    for r in rows:
        assert WINDOW_START <= r["date"] <= WINDOW_END
        assert r["date"] < SEALED_FROM

    by_block = {}
    for r in rows:
        by_block.setdefault(r["block"], []).append(r)

    sub("rows kept per block (Task 2's join, this airport)")
    print(f"    rows kept: {len(rows)} of "
          f"{(WINDOW_END - WINDOW_START).days + 1} window days")
    print("    " + ", ".join(f"{b}={len(by_block.get(b, []))}" for b in BLOCK_NAMES))

    oof = {name: {} for name in ("Raw GFS (GRIB)", "+ mean-bias", "3-feature", "5-feature")}
    per_fold_mae = {name: {} for name in oof}
    in_sample_errs = {"3-feature": [], "5-feature": []}
    oof_errs_pooled = {"3-feature": [], "5-feature": []}
    gain_shares = []
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

        pred3_tr = m3.predict(x3_tr)
        pred5_tr = m5.predict(x5_tr)
        for i, r in enumerate(train_rows):
            in_sample_errs["3-feature"].append((r["fc"] + float(pred3_tr[i])) - r["obs"])
            in_sample_errs["5-feature"].append((r["fc"] + float(pred5_tr[i])) - r["obs"])

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

            oof["Raw GFS (GRIB)"][r["date"]] = e_raw
            oof["+ mean-bias"][r["date"]] = e_mb
            oof["3-feature"][r["date"]] = e_3
            oof["5-feature"][r["date"]] = e_5

            fold_errs["Raw GFS (GRIB)"].append(e_raw)
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

    for name in oof:
        assert len(oof[name]) == len(rows), \
            f"{station} {name}: {len(oof[name])} OOF preds vs {len(rows)} rows"

    sub("per-block MAE (degC), four rungs")
    print(f"    {'block':<6} " + " ".join(f"{n:>16}" for n in oof))
    for b in BLOCK_NAMES:
        if b not in by_block:
            continue
        vals = [per_fold_mae[n].get(b, float('nan')) for n in oof]
        print(f"    {b:<6} " + " ".join(f"{v:>16.3f}" for v in vals))

    sub("pooled out-of-fold MAE and skill vs raw GFS (GRIB) -- the headline")
    pooled_mae = {}
    for name in oof:
        errs = [oof[name][d] for d in oof[name]]
        pooled_mae[name] = mae(errs)
    raw_mae = pooled_mae["Raw GFS (GRIB)"]
    print(f"    {'rung':<16} {'MAE degC':>9} {'skill vs raw GFS':>18} {'n days':>8}")
    for name in oof:
        skill = 100 * (1 - pooled_mae[name] / raw_mae) if name != "Raw GFS (GRIB)" else 0.0
        print(f"    {name:<16} {pooled_mae[name]:>9.3f} {skill:>17.1f}% {len(oof[name]):>8}")

    # -------------------------------------------------------- persistence
    obs_all = load_obs_all(station, target_hour)
    common = []
    no_prev = 0
    for r in rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        common.append((r, float(prev)))

    sub("Persistence (context only -- not part of the CV ladder)")
    print(f"    rows with a usable previous-day observation: {len(common)} of {len(rows)}")
    print(f"    dropped (no previous-day observation): {no_prev}")
    persist_errs = [p - r["obs"] for r, p in common]
    persist_mae = mae(persist_errs) if persist_errs else float("nan")
    print(f"    Persistence MAE: {persist_mae:.3f} degC (n={len(common)})")
    raw_on_common = mae([r["fc"] - r["obs"] for r, _ in common])
    print(f"    Raw GFS (GRIB) MAE on that same subset: {raw_on_common:.3f} degC "
          f"(for comparability with the persistence figure above)")

    sub("overfit diagnostic: pooled in-sample vs pooled out-of-fold MAE")
    for name, key in (("3-feature", "3-feature"), ("5-feature", "5-feature")):
        in_mae = mae(in_sample_errs[key])
        oof_mae = mae(oof_errs_pooled[key])
        print(f"    {name:<12} in-sample (pooled, {len(in_sample_errs[key])} "
              f"train-rows-across-folds) = {in_mae:.3f}   "
              f"out-of-fold (pooled, {len(oof_errs_pooled[key])} rows) = {oof_mae:.3f}   "
              f"gap = {oof_mae - in_mae:+.3f}")

    sub("5-feature importances, averaged across the 17 folds")
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


# ------------------------------------------------------------------ Task 5 headline

def headline(results):
    line("Task 5 -- headline reads (report, do NOT decide)")

    sub("does 5-feature beat 3-feature out-of-fold, and does 3-feature "
        "(and 5-feature) beat raw GFS (GRIB), on the full window?")
    print(f"    {'airport':<8} {'raw GFS':>9} {'3-feat':>9} {'5-feat':>9} "
          f"{'3 beats raw?':>13} {'5 beats 3?':>11} {'5 beats raw?':>13}")
    n_3beatsraw = n_5beats3 = n_5beatsraw = 0
    for st, r in results.items():
        b3raw = r["f3_mae"] < r["raw_mae"]
        b53 = r["f5_mae"] < r["f3_mae"]
        b5raw = r["f5_mae"] < r["raw_mae"]
        n_3beatsraw += b3raw
        n_5beats3 += b53
        n_5beatsraw += b5raw
        print(f"    {st:<8} {r['raw_mae']:>9.3f} {r['f3_mae']:>9.3f} "
              f"{r['f5_mae']:>9.3f} {('YES' if b3raw else 'no'):>13} "
              f"{('YES' if b53 else 'no'):>11} {('YES' if b5raw else 'no'):>13}")
    print(f"    3-feature beats raw GFS (GRIB) at {n_3beatsraw} of {len(results)} airports "
          f"(F87, 1.5-year Open-Meteo window: 4 of 5)")
    print(f"    5-feature beats 3-feature at {n_5beats3} of {len(results)} airports "
          f"(F87: 4 of 5)")
    print(f"    5-feature beats raw GFS (GRIB) at {n_5beatsraw} of {len(results)} airports "
          f"(F87: 4 of 5)")

    sub("overfit gap summary, all airports")
    print(f"    {'airport':<8} {'3-feat gap':>11} {'5-feat gap':>11}")
    for st, r in results.items():
        print(f"    {st:<8} {r['oof3'] - r['in3']:>+11.3f} {r['oof5'] - r['in5']:>+11.3f}")

    sub("LFPG specifically -- does the full window recover it?")
    r = results["LFPG"]
    beats = r["f3_mae"] < r["raw_mae"]
    print(f"    LFPG raw GFS (GRIB) pooled OOF MAE : {r['raw_mae']:.3f}")
    print(f"    LFPG 3-feature pooled OOF MAE      : {r['f3_mae']:.3f}  "
          f"(beats raw GFS: {'YES' if beats else 'no'})")
    print(f"    LFPG 5-feature pooled OOF MAE      : {r['f5_mae']:.3f}  "
          f"(beats 3-feature: {'YES' if r['f5_mae'] < r['f3_mae'] else 'no'}; "
          f"beats raw GFS: {'YES' if r['f5_mae'] < r['raw_mae'] else 'no'})")
    print("    context: on the 1.5-year Open-Meteo window (F87), LFPG's "
          "3-feature model was the one airport that still lost to raw GFS "
          "(-7.7%), and 5-feature narrowed but did not close that loss "
          "(-2.1%).")

    sub("Reno specifically -- does the short-window rescue signal hold on "
        "the full window? (the headline question for the whole "
        "richer-features phase)")
    r = results["RNO"]
    print(f"    RNO raw GFS (GRIB) pooled OOF MAE : {r['raw_mae']:.3f}")
    print(f"    RNO 3-feature pooled OOF MAE      : {r['f3_mae']:.3f}  "
          f"(beats raw GFS: {'YES' if r['f3_mae'] < r['raw_mae'] else 'no'})")
    print(f"    RNO 5-feature pooled OOF MAE      : {r['f5_mae']:.3f}  "
          f"(beats 3-feature: {'YES' if r['f5_mae'] < r['f3_mae'] else 'no'}; "
          f"beats raw GFS: {'YES' if r['f5_mae'] < r['raw_mae'] else 'no'})")
    print(f"    RNO 5-feature cloud_cover gain share  : {r['gain5']['cloud_cover']:.1f}%")
    print(f"    RNO 5-feature wind_speed_10m gain share: {r['gain5']['wind_speed_10m']:.1f}%")
    print("    context: F87 (1.5-year Open-Meteo window) found 5-feature "
          "beat both 3-feature (+3.8% skill) and raw GFS (+7.3% skill) at "
          "Reno -- the scout's own short window (F86) had found no such "
          "rescue. This is the same question asked again on the full "
          "4.4-year GRIB window.")

    sub("one-line synthesis (report only, the owner decides)")
    print(f"    3-feature beats raw GFS (GRIB) at {n_3beatsraw} of {len(results)} "
          f"airports on the full ~4.4-year window (F87's 1.5-year window: "
          f"4 of 5).")
    print(f"    5-feature beats 3-feature at {n_5beats3} of {len(results)} and "
          f"beats raw GFS (GRIB) at {n_5beatsraw} of {len(results)} airports.")
    print("    Whether this is now enough evidence to lock the richer method, "
          "and on which window, is flagged for the owner in the DECISIONS "
          "finding, not decided here.")

    return dict(n_3beatsraw=n_3beatsraw, n_5beats3=n_5beats3, n_5beatsraw=n_5beatsraw)


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 38 TASK 3/5 -- seasonal blocked cross-validation, FULL "
         "v16 window, GRIB source throughout. SEALED TEST NOT OPENED.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"CV window     : {WINDOW_START} to {WINDOW_END} ({(WINDOW_END - WINDOW_START).days + 1} days)")
    print(f"sealed test   : {SEALED_FROM} onward -- NOT LOADED")
    print(f"blocks ({N_BLOCKS}): " + ", ".join(f"{n} [{s}..{e}, {(e-s).days+1}d]" for n, s, e in BLOCKS))
    print(f"model settings (identical for both fitted models, D21.4): {LGB_PARAMS}")
    print(f"3-feature set: {FEATURES_3}")
    print(f"5-feature set: {FEATURES_5}")

    by_station = load_joined()

    results = {}
    for station, target_hour in AIRPORTS.items():
        run_airport(station, target_hour, by_station[station], results)

    synth = headline(results)

    # small machine-readable summary for the DECISIONS write-up
    summary_path = PROCESSED / "session38_cv_summary.csv"
    with open(summary_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "raw_mae", "mean_bias_mae", "f3_mae", "f5_mae",
                    "persist_mae", "n_days", "in3", "oof3", "in5", "oof5",
                    "gain_cloud_pct", "gain_wind_pct"])
        for st, r in results.items():
            w.writerow([st, f"{r['raw_mae']:.4f}", f"{r['mean_bias_mae']:.4f}",
                        f"{r['f3_mae']:.4f}", f"{r['f5_mae']:.4f}",
                        f"{r['persist_mae']:.4f}", r["n_days"],
                        f"{r['in3']:.4f}", f"{r['oof3']:.4f}",
                        f"{r['in5']:.4f}", f"{r['oof5']:.4f}",
                        f"{r['gain5']['cloud_cover']:.2f}",
                        f"{r['gain5']['wind_speed_10m']:.2f}"])
    print(f"Wrote CV summary table: {summary_path}")

    line("END")
    print("Input file untouched (read-only). No forecast or observation date "
          "on or after 2025-08-01 was loaded, printed, averaged or fitted "
          "on, at any airport or fold. No recipe was locked. Nothing was "
          "committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
