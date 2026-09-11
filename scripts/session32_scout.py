"""Session 32: richer-features scout (validation-year only, sealed test NOT
opened).

A SCOUT experiment, not a lock and not a test. It asks one question: does
adding cloud_cover and wind_speed_10m to the locked 3-feature model
(forecast_temp_c, season_sin, season_cos -- DECISIONS D19, D21.3) improve the
temperature-residual correction, judged ONCE on the validation year, at all
five airports? This is a rehearsal-stage experiment (DECISIONS D18's shape),
run on data no session has fitted a model on before.

THE SEALED TEST YEAR (2025-08-01 -> 2026-07-31, DECISIONS D13) IS NOT OPENED,
TOUCHED, PULLED OR EVALUATED IN THIS SESSION, FOR ANY AIRPORT. This script
never reads a forecast chunk or observation chunk dated 2026, and every date
loaded is asserted to fall before 2025-08-01 before anything is fitted.

WHY A SHORT WINDOW. cloud_cover and wind_speed_10m only exist on this API from
2024-01-19 12:00 UTC onward, at every airport (DECISIONS F85). So this script
does a TWO-TIER SAME-WINDOW COMPARISON: both the 3-feature model and the
5-feature model are trained on the identical short inner-training window,
2024-01-19 to 2024-07-31 (~6 months, deliberately thin -- this is why the
result is a scout, not a lock). The existing locked 3-feature model was
trained on 2021-03-24 to 2024-07-31 and its validation figures (F15, F29, F45,
F62) are NOT reused here for the ladder: reusing them would confound the
feature-set change with a window-length change. A fresh 3-feature model is
fitted on the same short window as the 5-feature model, so any difference
between the two is attributable to the two extra features alone.

Same feature set at every airport (no per-airport hand-picking). Same
LightGBM settings as the locked recipe (D21.4) for BOTH models -- nothing is
tuned. Missing data is dropped and counted, never filled (SPEC 2.2). Raw
pulls for the two new features are saved under data/raw/features/ with
provenance (scripts/session32_pull.py, already run).

Reads only from data/raw/ (existing full pulls) and data/raw/features/ (this
session's new cloud/wind pulls). Writes nothing to either.

Terms used here:
- "residual" = observed minus forecast (SPEC 4.2).
- "MAE"      = mean absolute error, degrees Celsius. Lower is better (5.1).
- "skill vs raw GFS" = 1 - (model MAE / raw GFS MAE), the fraction of raw
  GFS's error removed. Reported per Task 2's request.
"""

import ast
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

# The short, feature-complete window (session 32 prompt; cloud/wind free from
# 2024-01-19 12:00 UTC onward at every airport, DECISIONS F85).
INNER_START = date(2024, 1, 19)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# Hard wall. Nothing at or after this date is loaded, for any series, at any
# airport (DECISIONS D13). This is the hard line of the session.
SEALED_FROM = date(2025, 8, 1)

# The two yearly chunk files that cover the short window, for every airport
# (the naming convention is identical across all five: see sessions 03b, 10,
# 15, 20, 26).
FC_CHUNKS = [("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31")]
OBS_CHUNKS = [("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31")]

CLOUDWIND_START = "2024-01-19"
CLOUDWIND_END = "2025-07-31"

# The locked recipe's settings (DECISIONS D21.4), UNCHANGED, used for BOTH
# models in the ladder. Nothing is tuned between the 3-feature and 5-feature
# models; only the feature set (and the necessarily shorter window) differ
# from the locked recipe.
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

# Existing locked 3-feature validation MAE, for context ONLY (DECISIONS F15,
# F29, F45, F62) -- NOT used anywhere in the ladder computation. Printed once
# for the reader, clearly labelled, because the prompt forbids reusing these
# numbers as the comparison (they were fitted on the full 2021-2024 window).
LOCKED_3FEATURE_VALIDATION_MAE_CONTEXT_ONLY = {
    "EGLC": 1.165,   # F15, validation 2024-08-01..2025-07-31
    "LFPG": 1.377,   # F29
    "DSM": 1.466,    # F45
    "YSDU": 1.283,   # F62
    "RNO": 1.499,    # F80
}

OUT = ROOT / "notes" / "session-32-check-output.txt"


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
    """{date: temp_or_None} for the target hour, 2024-2025 chunks only,
    restricted to [INNER_START, VALID_END]. Never opens a 2026 file."""
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
            if dt < INNER_START or dt > VALID_END:
                continue
            assert dt < SEALED_FROM, "a sealed forecast date was loaded"
            series[dt] = v
    return series


def load_cloud_wind(station, target_hour):
    """{date: (cloud_or_None, wind_or_None)} for the target hour, this
    session's own pull only, restricted to [INNER_START, VALID_END]."""
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
        if dt < INNER_START or dt > VALID_END:
            continue
        assert dt < SEALED_FROM, "a sealed forecast date was loaded"
        series[dt] = (c, w)
    return series


def load_obs(station, target_hour):
    """{date: temp} for the target hour, the D14 pairing rule (SPEC 4.5):
    nearest routine report, dropped if more than 15 minutes from the hour.
    2024-2025 chunks only, restricted to [INNER_START, VALID_END]."""
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
                if dt < INNER_START or dt > VALID_END:
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


# ------------------------------------------------------------------ per-airport

def join_airport(station, target_hour):
    fc = load_forecast_temp(station, target_hour)
    cw = load_cloud_wind(station, target_hour)
    obs, obs_far, obs_no_temp = load_obs(station, target_hour)

    counts = dict(no_fc=0, null_fc=0, no_cloudwind=0, null_cloud=0,
                  null_wind=0, no_obs=0)
    rows = {"inner": [], "valid": []}
    for d in all_days(INNER_START, VALID_END):
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
               "cloud": float(cw_val[0]), "wind": float(cw_val[1])}
        if d <= INNER_END:
            rows["inner"].append(row)
        else:
            rows["valid"].append(row)

    return rows["inner"], rows["valid"], obs, counts, obs_far, obs_no_temp


# ------------------------------------------------------------------ main per airport

def run_airport(station, target_hour, results):
    line(f"{station} -- target hour {target_hour:02d}:00 UTC (SPEC 3.4)")

    inner, valid, obs_all, counts, obs_far, obs_no_temp = join_airport(
        station, target_hour)

    sub("Task 1 -- pull/join drop counts")
    total_days = len(all_days(INNER_START, VALID_END))
    print(f"    calendar days in the short window ({INNER_START} to "
          f"{VALID_END}): {total_days}")
    print(f"    no forecast row                : {counts['no_fc']}")
    print(f"    forecast row present but null  : {counts['null_fc']}")
    print(f"    no cloud/wind row               : {counts['no_cloudwind']}")
    print(f"    cloud value null                : {counts['null_cloud']}")
    print(f"    wind value null                 : {counts['null_wind']}")
    print(f"    no usable observation           : {counts['no_obs']}")
    print(f"      (of which, obs >15 min from hour, dropped by D14: "
          f"{obs_far})")
    print(f"      (of which, obs report carried no temperature: "
          f"{obs_no_temp})")
    print(f"    inner-training rows kept (2024-01-19..2024-07-31): "
          f"{len(inner)} of {len(all_days(INNER_START, INNER_END))}")
    print(f"    validation rows kept     (2024-08-01..2025-07-31): "
          f"{len(valid)} of {len(all_days(VALID_START, VALID_END))}")
    if inner:
        print(f"    inner-training date range kept: {inner[0]['date']} to "
              f"{inner[-1]['date']}")
    if valid:
        print(f"    validation date range kept    : {valid[0]['date']} to "
              f"{valid[-1]['date']}")

    assert max((r["date"] for r in valid), default=date(1900, 1, 1)) < SEALED_FROM
    assert max((r["date"] for r in inner), default=date(1900, 1, 1)) < SEALED_FROM

    # ---------------------------------------------------- persistence, common set
    common = []
    no_prev = []
    for r in valid:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev.append(r["date"])
            continue
        row = dict(r)
        row["persist"] = float(prev)
        common.append(row)

    sub("common validation set (every rung scored on the same days)")
    print(f"    paired validation rows                       : {len(valid)}")
    print(f"    dropped: no previous-day observation for persistence: "
          f"{len(no_prev)}"
          + (f"  ({', '.join(str(d) for d in no_prev)})" if no_prev else ""))
    print(f"    days every rung is scored on                 : {len(common)}")

    # ---------------------------------------------------------------- Task 2
    sub("Task 2 -- the baseline ladder, validation-year MAE + skill vs raw GFS")

    inner_mean_bias = float(np.mean([r["resid"] for r in inner])) if inner else float("nan")

    x3_in = features_3(inner)
    y_in = np.array([r["resid"] for r in inner], dtype=float)
    m3 = lgb.LGBMRegressor(**LGB_PARAMS)
    m3.fit(x3_in, y_in)

    x5_in = features_5(inner)
    m5 = lgb.LGBMRegressor(**LGB_PARAMS)
    m5.fit(x5_in, y_in)

    x3_va = features_3(common)
    x5_va = features_5(common)
    pred3 = m3.predict(x3_va)
    pred5 = m5.predict(x5_va)

    errs = {}
    for i, r in enumerate(common):
        errs.setdefault("Raw GFS", []).append(r["fc"] - r["obs"])
        errs.setdefault("+ mean-bias", []).append(
            r["fc"] + inner_mean_bias - r["obs"])
        errs.setdefault("3-feature (short)", []).append(
            r["fc"] + float(pred3[i]) - r["obs"])
        errs.setdefault("5-feature (richer)", []).append(
            r["fc"] + float(pred5[i]) - r["obs"])
        errs.setdefault("Persistence", []).append(r["persist"] - r["obs"])

    raw_mae = mae(errs["Raw GFS"])
    order = ["Raw GFS", "+ mean-bias", "3-feature (short)",
             "5-feature (richer)", "Persistence"]
    print(f"    inner-training rows fitted on: {len(inner)}  "
          f"({INNER_START} to {INNER_END} -- ~6 months, deliberately thin)")
    print(f"    mean-bias constant (inner-training only): "
          f"{inner_mean_bias:+.4f} degC")
    print()
    print(f"    {'rung':<22} {'MAE degC':>9} {'skill vs raw GFS':>18}")
    for name in order:
        m = mae(errs[name])
        skill = 100 * (1 - m / raw_mae) if name != "Raw GFS" else 0.0
        print(f"    {name:<22} {m:>9.3f} {skill:>17.1f}%")

    print()
    print("    context only, NOT part of this ladder -- the EXISTING locked")
    print("    3-feature model's validation MAE, fitted on the full "
          "2021-2024")
    print("    window (a different window, so not comparable to the rungs "
          "above):")
    print(f"      locked 3-feature (full window) validation MAE: "
          f"{LOCKED_3FEATURE_VALIDATION_MAE_CONTEXT_ONLY[station]:.3f} degC")

    # ---------------------------------------------------------------- Task 3
    sub("Task 3 -- the overfitting diagnostic")
    in3 = mae(y_in - m3.predict(x3_in))
    in5 = mae(y_in - m5.predict(x5_in))
    va3 = mae(errs["3-feature (short)"])
    va5 = mae(errs["5-feature (richer)"])
    print(f"    {'model':<22} {'in-sample MAE':>14} {'validation MAE':>15} "
          f"{'gap':>8}")
    print(f"    {'3-feature (short)':<22} {in3:>14.3f} {va3:>15.3f} "
          f"{va3 - in3:>+8.3f}")
    print(f"    {'5-feature (richer)':<22} {in5:>14.3f} {va5:>15.3f} "
          f"{va5 - in5:>+8.3f}")
    print("    A bigger gap here means the model fits noise in-sample that")
    print("    does not generalise -- the risk this scout exists to catch,")
    print("    on a training window of only ~6 months.")

    sub("Task 3 -- 5-feature model's feature importances")
    gain = m5.booster_.feature_importance(importance_type="gain")
    split = m5.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>14} {'gain share':>11} "
          f"{'splits':>8}")
    for n, g, s in zip(FEATURES_5, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        print(f"    {n:<18} {g:>14.1f} {share:>10.1f}% {s:>8,}")

    results[station] = dict(
        raw_mae=raw_mae,
        mean_bias_mae=mae(errs["+ mean-bias"]),
        f3_mae=va3, f5_mae=va5, persist_mae=mae(errs["Persistence"]),
        in3=in3, in5=in5, days=len(common),
        gain5=dict(zip(FEATURES_5, (100 * gain / gain.sum()).round(1))),
        inner_rows=len(inner), valid_rows=len(valid),
    )


# ------------------------------------------------------------------ headline

def headline(results):
    line("Task 4 -- headline read (report only, do NOT decide)")

    sub("does 5-feature beat 3-feature (short), per airport?")
    print(f"    {'airport':<8} {'3-feat MAE':>11} {'5-feat MAE':>11} "
          f"{'5 beats 3?':>11} {'change':>9}")
    for st, r in results.items():
        beats = r["f5_mae"] < r["f3_mae"]
        print(f"    {st:<8} {r['f3_mae']:>11.3f} {r['f5_mae']:>11.3f} "
              f"{('YES' if beats else 'no'):>11} "
              f"{r['f5_mae'] - r['f3_mae']:>+9.3f}")

    sub("does 5-feature beat raw GFS, per airport?")
    print(f"    {'airport':<8} {'raw GFS':>9} {'5-feat':>9} {'beats?':>8} "
          f"{'skill %':>9}")
    for st, r in results.items():
        beats = r["f5_mae"] < r["raw_mae"]
        skill = 100 * (1 - r["f5_mae"] / r["raw_mae"])
        print(f"    {st:<8} {r['raw_mae']:>9.3f} {r['f5_mae']:>9.3f} "
              f"{('YES' if beats else 'no'):>8} {skill:>+8.1f}")

    sub("in-sample / validation gap, sane or blown out?")
    print(f"    {'airport':<8} {'3-feat gap':>11} {'5-feat gap':>11}")
    for st, r in results.items():
        print(f"    {st:<8} {r['f3_mae'] - r['in3']:>+11.3f} "
              f"{r['f5_mae'] - r['in5']:>+11.3f}")

    sub("Reno specifically -- any sign cloud/wind add structure?")
    r = results["RNO"]
    print(f"    RNO 3-feature (short) validation MAE : {r['f3_mae']:.3f}")
    print(f"    RNO 5-feature (richer) validation MAE: {r['f5_mae']:.3f}")
    print(f"    RNO 5-feature cloud_cover gain share : "
          f"{r['gain5']['cloud_cover']:.1f}%")
    print(f"    RNO 5-feature wind_speed_10m gain share: "
          f"{r['gain5']['wind_speed_10m']:.1f}%")
    print("    Reno's target is local noon (20:00 UTC); the clear-calm")
    print("    cold-pool / downslope effect cloud and wind are most likely")
    print("    to capture is largely a nocturnal phenomenon, so a null or")
    print("    weak result here would be an EXPECTED finding, not a")
    print("    surprising one (see the session prompt).")

    sub("overall, across all five airports")
    n_5beats3 = sum(1 for r in results.values() if r["f5_mae"] < r["f3_mae"])
    n_5beatsraw = sum(1 for r in results.values() if r["f5_mae"] < r["raw_mae"])
    print(f"    5-feature beats 3-feature (short) at {n_5beats3} of "
          f"{len(results)} airports")
    print(f"    5-feature beats raw GFS at {n_5beatsraw} of {len(results)} "
          f"airports")
    print()
    print("    This is a REPORT, not a decision. Go/no-go on a full locked")
    print("    sealed-test cycle for the richer features, and whether the")
    print("    result justifies chasing a deeper cloud/wind source, are the")
    print("    owner's calls -- flagged in the DECISIONS finding, not made")
    print("    here.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 32 -- richer-features scout. VALIDATION YEAR ONLY. "
         "SEALED TEST NOT OPENED.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"short window inner-training: {INNER_START} to {INNER_END}")
    print(f"short window validation    : {VALID_START} to {VALID_END}")
    print(f"sealed test                : {SEALED_FROM} onward -- NOT LOADED")
    print(f"model settings (identical for both models, D21.4): {LGB_PARAMS}")
    print(f"3-feature set: {FEATURES_3}")
    print(f"5-feature set: {FEATURES_5}")

    results = {}
    for station, target_hour in AIRPORTS.items():
        run_airport(station, target_hour, results)

    headline(results)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). No forecast")
    print("or observation date on or after 2025-08-01 was loaded, printed,")
    print("averaged or fitted on, at any airport. No recipe was locked.")
    print("Nothing was committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
