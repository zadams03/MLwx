"""Session 46: multi-year rolling-origin generalisation backtest of the
EXISTING FROZEN recipes (3-feature and 5-feature, GRIB source, D21.4/D48.6
settings unchanged) at 24h lead, using only already-pulled GRIB data
(sessions 37 + 40). This is a DESCRIPTIVE MEASUREMENT, not a new sealed
test and not a pass/fail verdict -- see the integrity-boundary note printed
at the top of the output and DECISIONS F96.

ONE JOB: walk the train/test cutoff forward one year at a time (rolling
origin), refit the frozen recipes on each fold's own training window only,
score each fold's test year, and assemble a per-airport, per-year profile.
Nothing is tuned, added, or selected -- same features, same LightGBM
settings (D21.4), same elevation-corrected GRIB temperature already baked
into grib_features_v16_window.csv / grib_features_sealed_window.csv
(D48.3, session 37 decode). 24h lead only; no new pull.

Mid-session correction (recorded in DECISIONS F96): the session-46.md
prompt, as written, restricted the 5-feature folds to training windows
starting no earlier than 2024-01-19, citing F85 (cloud cover / wind speed
unavailable earlier). That citation is wrong for the GRIB source this
script uses -- F85 was about Open-Meteo's own coverage gap. The GRIB build
(sessions 36-38, F90/F91, now DECISIONS-archive.md; SPEC 7.2) pulled cloud
cover and wind speed across the FULL v16 window specifically to close that
gap, and this script's own data check (before any fold was built) confirms
grib_features_v16_window.csv carries real, non-null cloud_cover_grib_pct
and wind_speed_grib_kmh values back to 2021-03-24, the full training
window -- zero blank fields across all 7,952 + 1,825 rows in the two GRIB
feature files. The owner confirmed widening the 5-feature folds to the
full window, matching the 3-feature folds, subject to two conditions this
script honours: (1) the non-null check above, done before use; (2) no data
before 2021-03-24 is used anywhere -- that boundary is the v16 model-
version floor (D48.7), not a data-availability one, and stays fixed. The
two original thin 5-feature folds (2024-01-19 start) are KEPT, not
replaced, so the "more data helps" read has a within-recipe baseline to
compare against, and so the session-46.md prompt's own explicit fold list
is still fully present in the output.

Leakage safety: every feature is a same-day GRIB forecast value
(forecast_temp_c, cloud_cover, wind_speed_10m) or a calendar-position
encoding (season_sin, season_cos) -- no lagged/autoregressive feature -- so
a training row cannot encode a held-out test year's outcome (SPEC 2.1a).
Every fold's training window ends strictly before its test window begins
(train ends July 31, test begins the next day, August 1) and this is
asserted in code, per fold, per airport.
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

AIRPORTS = {  # SPEC 3.4, D48.2: station -> target hour (UTC)
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

V16_FLOOR = date(2021, 3, 24)          # D48.7 -- never use data before this
FULL_UNTIL = date(2026, 7, 31)         # end of the already-pulled sealed window

GRIB_PATHS = [
    PROCESSED / "grib_features_v16_window.csv",       # 2021-03-24 .. 2025-07-31
    PROCESSED / "grib_features_sealed_window.csv",    # 2025-08-01 .. 2026-07-31
]

OBS_CHUNKS = [  # existing IEM chunk files, unchanged naming (sessions 03b.. 26)
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

# D48.6 / D21.4: the locked LightGBM settings, identical for both fitted
# models, in every fold -- nothing tuned, nothing hand-picked.
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

# Rolling-origin folds: (label, train_start, train_end, test_start, test_end).
# Every train_end is one day before its test_start -- strict time order.
FOLDS_3 = [
    ("2022-23", date(2021, 3, 24), date(2022, 7, 31), date(2022, 8, 1), date(2023, 7, 31)),
    ("2023-24", date(2021, 3, 24), date(2023, 7, 31), date(2023, 8, 1), date(2024, 7, 31)),
    ("2024-25", date(2021, 3, 24), date(2024, 7, 31), date(2024, 8, 1), date(2025, 7, 31)),
    ("2025-26", date(2021, 3, 24), date(2025, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
]

# Widened per the owner's mid-session correction (see module docstring):
# the same four training starts as FOLDS_3, PLUS the two original
# session-46.md thin folds (2024-01-19 start), kept for comparison.
FOLDS_5 = [
    ("2022-23", date(2021, 3, 24), date(2022, 7, 31), date(2022, 8, 1), date(2023, 7, 31)),
    ("2023-24", date(2021, 3, 24), date(2023, 7, 31), date(2023, 8, 1), date(2024, 7, 31)),
    ("2024-25", date(2021, 3, 24), date(2024, 7, 31), date(2024, 8, 1), date(2025, 7, 31)),
    ("2025-26", date(2021, 3, 24), date(2025, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
    ("2024-25-thin", date(2024, 1, 19), date(2024, 7, 31), date(2024, 8, 1), date(2025, 7, 31)),
    ("2025-26-thin", date(2024, 1, 19), date(2025, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
]

THIN_DAYS = 730  # ~2 years -- folds trained on less than this are flagged

# F94 reference (DECISIONS, session 42) -- for the built-in consistency
# check only. Not used in any computation, just printed alongside.
F94_REFERENCE = {
    "EGLC": dict(raw=1.254, persist=2.096, f3=1.037, f5=1.000, n=364),
    "LFPG": dict(raw=1.382, persist=2.300, f3=1.177, f5=1.156, n=364),
    "DSM":  dict(raw=1.733, persist=4.003, f3=1.694, f5=1.636, n=365),
    "YSDU": dict(raw=1.317, persist=2.669, f3=1.283, f5=1.179, n=356),
    "RNO":  dict(raw=1.512, persist=2.490, f3=1.455, f5=1.346, n=365),
}

OUT = ROOT / "notes" / "session-46-backtest-output.txt"
PROFILE_CSV = PROCESSED / "session46_backtest_profile.csv"
FOLD_TABLE_CSV = PROCESSED / "session46_fold_table.csv"


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
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


def rmse(errors):
    return float(np.sqrt(np.mean(np.square(np.asarray(errors, dtype=float))))) if errors else float("nan")


def bias(errors):
    return float(np.mean(np.asarray(errors, dtype=float))) if errors else float("nan")


# ------------------------------------------------------------------ loading

def load_grib_features():
    """station -> {date: {fc, cloud, wind}}, the union of the training-
    window and sealed-window GRIB feature files (both already
    elevation-corrected, D48.3). Refuses any date before V16_FLOOR or after
    FULL_UNTIL -- this session pulls no new data and uses none outside what
    is already on disk. Also refuses any blank cloud/wind/temperature
    field, per the owner's condition (checked directly against the real
    files before this script was written: zero blanks found in either
    file, 7,952 + 1,825 rows)."""
    out = {st: {} for st in AIRPORTS}
    seen = {st: set() for st in AIRPORTS}
    for path in GRIB_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if d < V16_FLOOR or d > FULL_UNTIL:
                    raise ValueError(
                        f"{path.name}: {st} {d} falls outside "
                        f"[{V16_FLOOR}, {FULL_UNTIL}] -- refusing to use it.")
                if d in seen[st]:
                    raise ValueError(f"{path.name}: duplicate row for {st} {d}")
                seen[st].add(d)
                fc_raw = r["temperature_grib_c"].strip()
                cloud_raw = r["cloud_cover_grib_pct"].strip()
                wind_raw = r["wind_speed_grib_kmh"].strip()
                if not fc_raw or not cloud_raw or not wind_raw:
                    raise ValueError(
                        f"{path.name}: {st} {d} has a blank GRIB field -- "
                        "refusing to use it (SPEC 2.2, never fill).")
                out[st][d] = {
                    "fc": float(fc_raw),
                    "cloud": float(cloud_raw),
                    "wind": float(wind_raw),
                }
    return out


def load_obs_all(station, target_hour):
    """{date: temp} for the target hour, D14 pairing rule (SPEC 4.5), across
    the full available span. Used both for the join and for persistence's
    previous-day lookup."""
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
                if dt < V16_FLOOR or dt > FULL_UNTIL:
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


def join_rows(grib_for_station, obs_for_station, date_lo, date_hi):
    """One row per day with a GRIB feature row AND a usable observation,
    D14 drop-count rule (SPEC 2.2: nothing filled)."""
    rows = []
    no_grib = no_obs = 0
    for d in all_days(date_lo, date_hi):
        g = grib_for_station.get(d)
        if g is None:
            no_grib += 1
            continue
        o = obs_for_station.get(d)
        if o is None:
            no_obs += 1
            continue
        rows.append({
            "date": d,
            "fc": g["fc"],
            "cloud": g["cloud"],
            "wind": g["wind"],
            "obs": o,
            "resid": o - g["fc"],
        })
    return rows, no_grib, no_obs


# ------------------------------------------------------------------ per-fold run

def run_fold(station, feature_label, fold_label, train_start, train_end,
             test_start, test_end, joined_rows, obs_all, profile_rows,
             fold_table_rows):
    assert train_end < test_start, \
        f"{station} {feature_label} {fold_label}: train_end not before test_start"

    train_rows = [r for r in joined_rows if train_start <= r["date"] <= train_end]
    test_rows = [r for r in joined_rows if test_start <= r["date"] <= test_end]

    for r in train_rows:
        assert train_start <= r["date"] <= train_end, "a training row falls outside its own window"
        assert r["date"] < test_start, "a training row lands inside or after the test window"
    for r in test_rows:
        assert test_start <= r["date"] <= test_end, "a test row falls outside its own window"

    train_days = (train_end - train_start).days + 1
    thin = train_days < THIN_DAYS

    fold_table_rows.append(dict(
        feature_set=feature_label, fold=fold_label,
        train_start=train_start, train_end=train_end,
        train_days=train_days, train_years=round(train_days / 365.25, 2),
        test_start=test_start, test_end=test_end,
        train_rows=len(train_rows), test_rows=len(test_rows),
        thin="YES" if thin else "no",
    ))

    if not train_rows or not test_rows:
        print(f"    {station} {feature_label} {fold_label}: SKIPPED -- "
              f"no rows in train ({len(train_rows)}) or test ({len(test_rows)})")
        return

    feat_fn = features_3 if feature_label == "3-feature" else features_5

    x_tr = feat_fn(train_rows)
    y_tr = np.array([r["resid"] for r in train_rows], dtype=float)
    m = lgb.LGBMRegressor(**LGB_PARAMS)
    m.fit(x_tr, y_tr)

    x_te = feat_fn(test_rows)
    pred = m.predict(x_te)

    e_raw = [r["fc"] - r["obs"] for r in test_rows]
    e_model = [(r["fc"] + float(pred[i])) - r["obs"] for i, r in enumerate(test_rows)]

    common_persist = []
    no_prev = 0
    for r in test_rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        common_persist.append((r, float(prev)))
    e_persist = [p - r["obs"] for r, p in common_persist]

    raw_mae, raw_rmse, raw_bias = mae(e_raw), rmse(e_raw), bias(e_raw)
    persist_mae, persist_rmse, persist_bias = mae(e_persist), rmse(e_persist), bias(e_persist)
    model_mae, model_rmse, model_bias = mae(e_model), rmse(e_model), bias(e_model)

    skill_vs_raw = 100 * (1 - model_mae / raw_mae) if raw_mae else float("nan")
    skill_vs_persist = 100 * (1 - model_mae / persist_mae) if e_persist else float("nan")

    print(f"    {station} {feature_label} {fold_label:<14} "
          f"train={train_start}..{train_end} ({train_days}d{'  THIN' if thin else ''}) "
          f"test={test_start}..{test_end}")
    print(f"        n_train={len(train_rows)} n_test={len(test_rows)} "
          f"no_prev(persist)={no_prev}")
    print(f"        raw GFS (GRIB)  : MAE={raw_mae:.3f} RMSE={raw_rmse:.3f} bias={raw_bias:+.3f}")
    print(f"        persistence     : MAE={persist_mae:.3f} RMSE={persist_rmse:.3f} "
          f"bias={persist_bias:+.3f} (n={len(e_persist)})")
    print(f"        {feature_label:<15} : MAE={model_mae:.3f} RMSE={model_rmse:.3f} "
          f"bias={model_bias:+.3f}  skill vs raw={skill_vs_raw:+.1f}%  "
          f"skill vs persist={skill_vs_persist:+.1f}%")

    for rung, m_, r_, b_, skr, skp, n in (
        ("raw_gfs", raw_mae, raw_rmse, raw_bias, 0.0, float("nan"), len(e_raw)),
        ("persistence", persist_mae, persist_rmse, persist_bias, float("nan"), 0.0, len(e_persist)),
        (feature_label, model_mae, model_rmse, model_bias, skill_vs_raw, skill_vs_persist, len(e_model)),
    ):
        profile_rows.append(dict(
            station=station, feature_set=feature_label, fold=fold_label,
            train_start=train_start, train_end=train_end,
            test_start=test_start, test_end=test_end,
            train_rows=len(train_rows), test_rows=len(test_rows),
            rung=rung, mae=round(m_, 4), rmse=round(r_, 4),
            bias=round(b_, 4),
            skill_vs_raw=round(skr, 2) if skr == skr else "",
            skill_vs_persist=round(skp, 2) if skp == skp else "",
            n=n,
        ))


# ------------------------------------------------------------------ main

def main():
    if len(sys.argv) != 1:
        raise SystemExit("this script takes no arguments")

    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 46 -- multi-year rolling-origin generalisation backtest, "
         "24h lead, GRIB source, EXISTING FROZEN recipes only. "
         "DESCRIPTIVE PROFILE, NOT A NEW SEALED TEST OR VERDICT.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"v16 floor (never crossed): {V16_FLOOR}")
    print(f"data available through  : {FULL_UNTIL}")
    print(f"model settings (D48.6/D21.4, identical for every fold/airport/feature set): {LGB_PARAMS}")
    print(f"3-feature set: {FEATURES_3}")
    print(f"5-feature set: {FEATURES_5}")

    print()
    print("INTEGRITY BOUNDARY: reusing the sealed year here is legitimate only")
    print("because this is a profile, not a pass/fail -- the recipes are frozen")
    print("and refit-only, nothing is tuned or selected. This does not re-open,")
    print("re-litigate, or overwrite F94 or F16-F82. Feature *selection* work")
    print("later still needs its own fresh, untouched test year.")

    print()
    print("MID-SESSION CORRECTION (DECISIONS F96): session-46.md's own fold")
    print("list restricted 5-feature training to start no earlier than")
    print("2024-01-19, citing F85 (Open-Meteo's cloud/wind gap). That citation")
    print("does not apply to the GRIB source used throughout this project's")
    print("richer-features work -- GRIB cloud/wind exist back to 2021-03-24,")
    print("the full training window (checked directly against")
    print("grib_features_v16_window.csv before this script was written: zero")
    print("blank cloud/wind/temperature fields in 7,952 + 1,825 rows). The")
    print("owner confirmed widening the 5-feature folds to match 3-feature's")
    print("training starts, subject to (1) the non-null check above and (2)")
    print("never using data before 2021-03-24 (the v16 model-version floor,")
    print("D48.7 -- unrelated to data availability). The two original thin")
    print("2024-01-19-start folds are kept alongside the widened ones, not")
    print("replaced.")

    grib = load_grib_features()

    profile_rows = []
    fold_table_rows = []

    line("Per-airport, per-fold results")
    for station, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(station, target_hour)
        joined_rows, no_grib, no_obs = join_rows(
            grib[station], obs_all, V16_FLOOR, FULL_UNTIL)

        sub(f"{station} -- target hour {target_hour:02d}:00 UTC -- join over "
            f"the full available span {V16_FLOOR}..{FULL_UNTIL}")
        print(f"    joined rows: {len(joined_rows)}  "
              f"(no GRIB row: {no_grib}, no usable obs: {no_obs}, "
              f"of which >15min from target hour: {obs_far}, "
              f"of which report carried no temperature: {obs_no_temp})")

        print()
        print("    -- 3-feature folds --")
        for fold_label, tr_s, tr_e, te_s, te_e in FOLDS_3:
            run_fold(station, "3-feature", fold_label, tr_s, tr_e, te_s, te_e,
                     joined_rows, obs_all, profile_rows, fold_table_rows)

        print()
        print("    -- 5-feature folds (widened per F96; thin originals kept) --")
        for fold_label, tr_s, tr_e, te_s, te_e in FOLDS_5:
            run_fold(station, "5-feature", fold_label, tr_s, tr_e, te_s, te_e,
                     joined_rows, obs_all, profile_rows, fold_table_rows)

    # ------------------------------------------------------------ F94 consistency check

    line("Consistency check -- does the 2025-26 fold reproduce F94?")
    print("(3-feature full-window fold and 5-feature full-window fold both use")
    print(" exactly D48's own training window (2021-03-24..2025-07-31) and test")
    print(" window (2025-08-01..2026-07-31) -- this should closely reproduce")
    print(" F94's numbers, since it is the same recipe on the same data.)")
    max_abs_diff = 0.0
    for station in AIRPORTS:
        ref = F94_REFERENCE[station]
        got3 = next(p for p in profile_rows if p["station"] == station
                    and p["feature_set"] == "3-feature" and p["fold"] == "2025-26"
                    and p["rung"] == "3-feature")
        got5 = next(p for p in profile_rows if p["station"] == station
                    and p["feature_set"] == "5-feature" and p["fold"] == "2025-26"
                    and p["rung"] == "5-feature")
        gotraw = next(p for p in profile_rows if p["station"] == station
                      and p["feature_set"] == "3-feature" and p["fold"] == "2025-26"
                      and p["rung"] == "raw_gfs")
        gotpersist = next(p for p in profile_rows if p["station"] == station
                           and p["feature_set"] == "3-feature" and p["fold"] == "2025-26"
                           and p["rung"] == "persistence")
        diffs = dict(
            raw=gotraw["mae"] - ref["raw"],
            persist=gotpersist["mae"] - ref["persist"],
            f3=got3["mae"] - ref["f3"],
            f5=got5["mae"] - ref["f5"],
        )
        max_abs_diff = max(max_abs_diff, *(abs(v) for v in diffs.values()))
        n_match = (gotraw["n"] == ref["n"]) and (got3["n"] == ref["n"]) and (got5["n"] == ref["n"])
        print(f"    {station}: n(F94)={ref['n']} n(here)={gotraw['n']} "
              f"{'MATCH' if n_match else 'MISMATCH'}  "
              f"raw {gotraw['mae']:.3f} vs {ref['raw']:.3f} ({diffs['raw']:+.4f})  "
              f"persist {gotpersist['mae']:.3f} vs {ref['persist']:.3f} ({diffs['persist']:+.4f})  "
              f"f3 {got3['mae']:.3f} vs {ref['f3']:.3f} ({diffs['f3']:+.4f})  "
              f"f5 {got5['mae']:.3f} vs {ref['f5']:.3f} ({diffs['f5']:+.4f})")
    print(f"\n    largest absolute MAE difference from F94 across all airports/rungs: "
          f"{max_abs_diff:.4f} degC")
    print("    (nonzero rounding-level differences are expected: F94's own script "
          "reports MAE to 3 decimal places and this script recomputes from the "
          "same inputs independently; a difference at the thousandths place is "
          "reproduction, not divergence.)")

    # ------------------------------------------------------------ write tables

    with open(PROFILE_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "station", "feature_set", "fold", "train_start", "train_end",
            "test_start", "test_end", "train_rows", "test_rows", "rung",
            "mae", "rmse", "bias", "skill_vs_raw", "skill_vs_persist", "n"])
        w.writeheader()
        w.writerows(profile_rows)
    print(f"\nWrote profile table: {PROFILE_CSV} ({len(profile_rows)} rows)")

    with open(FOLD_TABLE_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "feature_set", "fold", "train_start", "train_end", "train_days",
            "train_years", "test_start", "test_end", "train_rows",
            "test_rows", "thin"])
        w.writeheader()
        w.writerows(fold_table_rows)
    print(f"Wrote fold table: {FOLD_TABLE_CSV} ({len(fold_table_rows)} rows)")

    line("END")
    print("This is a descriptive multi-year profile of the EXISTING frozen")
    print("recipes, not a new sealed test. It does not re-open, re-litigate, or")
    print("overwrite F94 or F16-F82, which stand exactly as reported. Feature")
    print("selection work later still needs its own fresh, untouched test year.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
