"""Session 11: the CDG (LFPG) join, bias look and validation rehearsal.

This is the first modelling session for the second airport, Paris Charles de
Gaulle. It mirrors session 04/05 for London City exactly. The method is already
locked (DECISIONS D21) and D26 says stage 2 changes the LOCATION AND NOTHING
ELSE, so nothing about the model, the features or the settings is chosen again
here. This script applies the locked recipe to CDG.

PART 0 proves that rather than claiming it: it reads scripts/session05_model.py
and compares it with this file, setting by setting, constant by constant, and
function source character by character. The only differences that should show
up are the station's file names and the labels that carry its name.

Reads only from data/raw/. Never writes to data/raw/. Fills nothing (SPEC 2.2).

CDG'S TEST YEAR IS SEALED. The test window (2025-08-01 to 2026-07-31, DECISIONS
D13) is filtered out at load time: the two 2026 LFPG raw chunk files are never
opened at all, and the 2025 chunk is cut off at 2025-07-31. No test-year value
is loaded, printed, averaged or fitted on.

The three periods used here (DECISIONS D18):
- inner-training : 2021-03-24 to 2024-07-31. Everything is fitted on this and
                   only this - the model, the climatology, the mean bias.
- validation     : 2024-08-01 to 2025-07-31. A practice stand-in for the sealed
                   test year, same August-to-July shape. Judged on, not
                   explored.
- test           : 2025-08-01 to 2026-07-31. Not touched this session.

Terms used here:
- "residual" = observed minus forecast. This is what the model learns
  (SPEC 4.2). The corrected forecast is forecast + predicted residual.
- "bias"     = the same quantity looked at as a summary rather than a target.
  A positive bias means the station was warmer than GFS said.
- "MAE"      = mean absolute error, the average size of the miss in degrees
  Celsius. Lower is better (SPEC 5.1).

A GOOD RESULT HERE DOES NOT MEAN STAGE 2 HAS PASSED. This is a rehearsal on the
validation year. The frozen bar (SPEC 5.3) is judged once, on CDG's own sealed
test year, in a later session.
"""

import ast
import csv
import difflib
import json
import math
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# --- making LightGBM importable on this machine -------------------------------
# LightGBM's macOS build needs the OpenMP runtime library (libomp.dylib), which
# is not installed system-wide here and has no Homebrew to install it from.
# scikit-learn's macOS wheel ships its own copy, so we point the dynamic loader
# at that copy and restart the interpreter once. This changes nothing about the
# model - it only lets the library load. (DECISIONS Q16, D24.)
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

# THE ONE THING THAT CHANGES FOR STAGE 2 (DECISIONS D26): the location.
STATION = "LFPG"                      # Paris Charles de Gaulle (SPEC 3.4)
AIRPORT = "CDG"

TARGET_HOUR = 12                      # 12:00 UTC (SPEC 4.1)

INNER_START = date(2021, 3, 24)       # DECISIONS D18
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# Hard wall. Nothing at or after this date is loaded (DECISIONS D13).
SEALED_FROM = date(2025, 8, 1)

# Only the chunks that hold data before the sealed test year. The two 2026
# files are deliberately absent from this list - they are entirely test year.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),     # cut off at 2025-07-31 on load
]

# The one gap in the forecast series. Found at EGLC (F8) and found again at
# LFPG, hour for hour (F22). For reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. IDENTICAL to session 05 (DECISIONS D21.4). Nothing is tuned,
# searched or varied for the second airport - that is the whole point of D26.
LGB_PARAMS = dict(
    objective="regression_l1",        # absolute error (D20)
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

CLIM_HALF_WINDOW_DAYS = 7.5           # climatology smoothing window, +/- days

PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"

# What session 10's gap map predicts this join will drop (STATUS "Next", F22,
# F25). These are expectations to RECONCILE against, not numbers to accept.
EXPECT_GAP_DAYS = 20                  # F22: the gap resumes at the target hour
EXPECT_OFFHOUR_DAYS = [date(2022, 7, 23), date(2022, 7, 25)]   # F25

# ---- EGLC's published figures, for the side-by-side comparison ---------------
# Inner-training bias at EGLC (DECISIONS F13).
EGLC_BIAS = dict(n=1205, mean=-0.108, median=0.000, sd=1.551,
                 lo=-7.0, hi=+5.6, mean_abs=1.172, warmer=587, warmer_pct=48.7)
EGLC_BANDS = {                        # band label -> (days, mean bias)
    "0 to 5":   (47, -0.049),
    "5 to 10":  (220, +0.361),
    "10 to 15": (356, +0.387),
    "15 to 20": (276, -0.287),
    "20 to 25": (223, -0.746),
    "25 to 45": (83, -1.201),
}
EGLC_TAILS = {                        # tail -> (n, fc lo, fc hi, mean bias)
    "coldest 10% of forecasts": (120, +1.0, +7.3, +0.097),
    "warmest 10% of forecasts": (120, +23.1, +39.4, -1.155),
}
EGLC_BIAS_SEASON = {                  # season -> (days, mean bias, sd, mean|b|)
    "winter DJF": (251, +0.356, 1.340, 1.065),
    "spring MAM": (345, -0.061, 1.624, 1.203),
    "summer JJA": (336, -0.549, 1.755, 1.437),
    "autumn SON": (273, -0.052, 1.194, 0.907),
}
# EGLC's validation rehearsal, session 05 (DECISIONS F15).
EGLC_MAE = {
    "Raw GFS":             dict(mae=1.239, bias=-0.278, rmse=1.630, worst=4.90),
    "Persistence":         dict(mae=2.226, bias=-0.017, rmse=2.928, worst=12.00),
    "Climatology":         dict(mae=2.865, bias=+0.020, rmse=3.656, worst=11.65),
    "Mean-bias reference": dict(mae=1.231, bias=-0.170, rmse=1.615, worst=4.79),
    "ML-corrected":        dict(mae=1.165, bias=-0.221, rmse=1.571, worst=5.42),
}
EGLC_SEASON = {                       # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 0.972, 1.059),
    "spring MAM": (92, 1.337, 1.322),
    "summer JJA": (90, 1.498, 1.177),
    "autumn SON": (91, 1.147, 1.098),
}
EGLC_IMPORTANCE = {                   # feature -> (gain share %, splits)
    "forecast_temp_c": (44.3, 1614),
    "season_sin":      (26.7, 1337),
    "season_cos":      (29.0, 1249),
}
EGLC_INSAMPLE_ML = 0.879              # inner-training MAE, session 05
EGLC_DAYS_SCORED = 363
EGLC_INNER_ROWS = 1205
EGLC_VALID_ROWS = 364

OUT = ROOT / "notes" / "session-11-check-output.txt"


class Tee:
    """Print to the screen and to the notes file at the same time."""

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
    print("=" * 76)
    print(title)
    print("=" * 76)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ loading

def load_forecast_12z():
    """Return {date: forecast_temp_or_None} for 12:00 UTC, before the seal."""
    series = {}
    rows_seen = 0
    rows_sealed = 0
    for start, end in CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_{STATION}_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        for t_str, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
            if t.hour != TARGET_HOUR:
                continue
            rows_seen += 1
            if t.date() >= SEALED_FROM:
                rows_sealed += 1
                continue
            series[t.date()] = v
    return series, rows_seen, rows_sealed


def load_obs_12z():
    """Return {date: observed_temp} for the 12:00 UTC hour, before the seal.

    The D14 pairing rule: the routine report belongs to the hour it is nearest
    to, and only if it is within 15 minutes of it. At LFPG the routine report
    is stamped ON THE HOUR (F18), so the 12:00 report is the observation for
    12:00 - an exact match, no offset. Anything further off is dropped and
    counted.
    """
    series = {}
    reports_at_12 = 0
    reports_sealed = 0
    no_temp = 0
    outside_15min = 0
    near_noon = {}                     # date -> [(minute offset, temp or None)]

    for start, end in CHUNKS:
        path = RAW / f"iem_asos_{STATION}_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != TARGET_HOUR:
                    continue
                reports_at_12 += 1
                if nearest.date() >= SEALED_FROM:
                    reports_sealed += 1
                    continue
                off = int((t - nearest).total_seconds() // 60)
                raw = (r.get("tmpc") or "").strip()
                near_noon.setdefault(nearest.date(), []).append(
                    (off, raw if raw not in ("M", "", "T", "None") else None))
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[nearest.date()] = float(raw)

    return (series, reports_at_12, reports_sealed, no_temp, outside_15min,
            near_noon)


def all_days(start, end):
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------------ features

def year_fraction(d):
    """Where in the year this date sits, 0.0 to 1.0. Leap-year safe."""
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0
                                             or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def features(rows):
    """The D19 feature set: forecast temperature, and season as sin/cos.

    Season is encoded as the sine and cosine of the position in the year so
    that 31 December sits next to 1 January instead of at the opposite end of
    a number line. Hour of day is not a feature - the hour is fixed at 12:00.
    """
    x = []
    for r in rows:
        a = 2 * math.pi * year_fraction(r["date"])
        x.append([r["fc"], math.sin(a), math.cos(a)])
    return np.array(x, dtype=float)


FEATURE_NAMES = ["forecast_temp_c", "season_sin", "season_cos"]


# ------------------------------------------------------------------ helpers

def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


def describe(vals, label, indent="    "):
    a = np.asarray(vals, dtype=float)
    print(f"{indent}{label}")
    print(f"{indent}  n      = {len(a):,}")
    print(f"{indent}  mean   = {a.mean():+.3f} degC")
    print(f"{indent}  median = {np.median(a):+.3f} degC")
    print(f"{indent}  st dev = {a.std(ddof=1):.3f} degC")
    print(f"{indent}  min    = {a.min():+.1f} degC   max = {a.max():+.1f} degC")
    print(f"{indent}  5th pct = {np.percentile(a, 5):+.2f}   "
          f"25th = {np.percentile(a, 25):+.2f}   "
          f"75th = {np.percentile(a, 75):+.2f}   "
          f"95th = {np.percentile(a, 95):+.2f}")
    print(f"{indent}  mean absolute size = {np.abs(a).mean():.3f} degC")


# ------------------------------------------------------------------ part 0

def _literal(node):
    """Read a constant out of the parsed source.

    Handles plain literals and the two call shapes these scripts use for
    constants: date(y, m, d) and dict(...).
    """
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "date":
        return date(*[ast.literal_eval(a) for a in node.args])
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "dict":
        return {k.arg: ast.literal_eval(k.value) for k in node.keywords}
    return ast.literal_eval(node)


def top_level(tree, name):
    """The value assigned to a module-level constant, or a marker if absent."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return _literal(node.value)
    return "<not found>"


def func_source(src, tree, name):
    """The exact source text of a top-level function, or None."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    return None


def prove_only_location_changed():
    """Compare this script with session 05's, and show what differs."""
    line("PART 0 - proving ONLY THE LOCATION changed (DECISIONS D26)")
    print("This does not just claim the method is reused unchanged. It reads")
    print(f"{PREV_SCRIPT.relative_to(ROOT)} and compares it with this file.")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)

    sub("model settings, session 05 (EGLC) against session 11 (CDG)")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 11':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}   "
          f"(D21.4 requires 0 - the method is locked)")

    sub("everything else that must be identical")
    consts = ["TARGET_HOUR", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "SEALED_FROM", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]
    print(f"    {'constant':<24} {'session 05':<34} same?")
    n_const_diff = 0
    for c in consts:
        a = top_level(old, c)
        b = top_level(new, c)
        if a != b:
            n_const_diff += 1
        print(f"    {c:<24} {str(a):<34} {'yes' if a == b else 'NO - CHANGED'}")
    print(f"    constants that differ: {n_const_diff}")

    sub("the code that builds the features, the baselines and the model")
    print("    Compared character for character between the two scripts.")
    same_funcs = ["all_days", "year_fraction", "features", "mae", "describe",
                  "climatology_from_inner"]
    for name in same_funcs:
        a = func_source(old_src, old, name)
        b = func_source(new_src, new, name)
        verdict = "identical" if a == b else "DIFFERS"
        print(f"    {name + '()':<26} {verdict}")

    sub("the two loaders, which DO differ - the difference shown in full")
    print("    This is where the location lives. Everything the loaders do is")
    print("    the same; the file names and the labels carry the station code.")
    for name in ("load_forecast_12z", "load_obs_12z"):
        a = func_source(old_src, old, name).splitlines()
        b = func_source(new_src, new, name).splitlines()
        diff = list(difflib.unified_diff(a, b, f"session05 {name}",
                                         f"session11 {name}", lineterm="", n=1))
        print()
        if not diff:
            print(f"    {name}(): identical")
        for d in diff:
            print(f"    {d}")
    print()
    print("    load_obs_12z also gained a 'near_noon' record of every report")
    print("    near the target hour with its minute offset. That is bookkeeping")
    print("    for PART A's drop reconciliation - it changes no pairing and no")
    print("    value: the same reports are kept and the same ones are dropped.")


# ------------------------------------------------------------------ part A

def join():
    line(f"PART A - join {AIRPORT}'s two series at 12:00 UTC")

    print(f"airport     : {AIRPORT} / {STATION} (SPEC 3.4)")
    print(f"target hour : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1) - the same hour as")
    print("              stage 1, on purpose (D26)")
    print("pairing rule: the routine report nearest the hour, and only if within")
    print("              15 minutes of it (DECISIONS D14). At LFPG the routine")
    print("              report is stamped :00, so this is an EXACT match with")
    print("              no offset at all (F18).")

    fc, fc_rows, fc_sealed = load_forecast_12z()
    obs, ob_rows, ob_sealed, ob_no_temp, ob_far, near_noon = load_obs_12z()

    sub("the seal on the test year")
    print(f"    forecast chunk files opened : {len(CHUNKS)} "
          f"(the two 2026 files were not opened at all)")
    print(f"    forecast 12:00 rows seen    : {fc_rows:,}")
    print(f"    of those, dropped as sealed : {fc_sealed:,} "
          f"(dated {SEALED_FROM} or later)")
    print(f"    forecast 12:00 rows kept    : {len(fc):,}")
    print(f"    observation 12:00 reports seen   : {ob_rows:,}")
    print(f"    of those, dropped as sealed      : {ob_sealed:,}")
    print(f"    observation 12:00 reports kept   : {len(obs):,}")

    sub("observation reports rejected by the rules (not sealed, just unusable)")
    print(f"    reports more than 15 min from the hour, dropped (D14): {ob_far:,}")
    print(f"    reports carrying no temperature (M), dropped (2.2)   : {ob_no_temp:,}")

    periods = [
        ("inner-training 2021-03-24..2024-07-31", INNER_START, INNER_END),
        ("validation     2024-08-01..2025-07-31", VALID_START, VALID_END),
    ]

    built = {}
    sub("rows kept and dropped, by period")
    header = (f"    {'period':<38} {'days':>6} {'kept':>6} {'drop':>6} "
              f"{'no fc':>6} {'null fc':>8} {'no obs':>7}")
    print(header)
    for label, lo, hi in periods:
        rows = []
        n_no_fc = n_null_fc = n_no_obs = 0
        for d in all_days(lo, hi):
            f_val = fc.get(d, "absent")
            o_val = obs.get(d)
            bad = False
            if f_val == "absent":
                n_no_fc += 1
                bad = True
            elif f_val is None:
                n_null_fc += 1
                bad = True
            if o_val is None:
                n_no_obs += 1
                bad = True
            if bad:
                continue
            rows.append({"date": d, "fc": float(f_val), "obs": float(o_val),
                         "resid": float(o_val) - float(f_val)})
        days = len(all_days(lo, hi))
        dropped = days - len(rows)
        print(f"    {label:<38} {days:>6,} {len(rows):>6,} {dropped:>6,} "
              f"{n_no_fc:>6,} {n_null_fc:>8,} {n_no_obs:>7,}")
        built[label.split()[0]] = rows

    print()
    print("    columns: days = calendar days in the period; kept = paired rows;")
    print("             drop = days with no usable pair; then the reasons.")
    print("             'no fc'    = the forecast series had no row for 12:00;")
    print("             'null fc'  = it had a row but the value was null;")
    print("             'no obs'   = no usable observation within 15 min.")
    print("             A day can fail on more than one reason, so the reason")
    print("             columns can add up to more than 'drop'.")
    print("    Nothing was filled in (SPEC 2.2).")

    inner, valid = built["inner-training"], built["validation"]

    # Prove the seal held rather than just asserting it in prose.
    assert max(fc) < SEALED_FROM, "a sealed forecast date got through"
    assert max(obs) < SEALED_FROM, "a sealed observation date got through"
    assert max(r["date"] for r in valid) < SEALED_FROM

    # ------------------------------------------------------- reconciliation
    sub("RECONCILING THE DROPS against session 10's gap map (F22, F25)")
    print("    The drops are not just accepted. Session 10 mapped every hour of")
    print("    both LFPG series before anything was joined, so it predicted what")
    print("    this join should lose. Anything else is a surprise to stop on.")

    kept_dates = {r["date"] for r in inner} | {r["date"] for r in valid}
    all_dropped = [d for d in all_days(INNER_START, VALID_END)
                   if d not in kept_dates]

    gap_dropped = [d for d in all_dropped if GAP_START <= d <= GAP_END]
    other_dropped = [d for d in all_dropped if not (GAP_START <= d <= GAP_END)]

    print()
    print(f"    {'cause':<44} {'expected':>9} {'actual':>8}  verdict")
    v1 = "MATCHES" if len(gap_dropped) == EXPECT_GAP_DAYS else "SURPRISE"
    print(f"    {'the 492-hour forecast gap (F22)':<44} "
          f"{EXPECT_GAP_DAYS:>9} {len(gap_dropped):>8}  {v1}")
    v2 = "MATCHES" if sorted(other_dropped) == EXPECT_OFFHOUR_DAYS else "SURPRISE"
    print(f"    {'off-hour reports, training window (F25)':<44} "
          f"{len(EXPECT_OFFHOUR_DAYS):>9} {len(other_dropped):>8}  {v2}")
    print(f"    {'anything else':<44} {0:>9} "
          f"{len([d for d in other_dropped if d not in EXPECT_OFFHOUR_DAYS]):>8}"
          f"  {'MATCHES' if all(d in EXPECT_OFFHOUR_DAYS for d in other_dropped) else 'SURPRISE'}")
    print(f"    {'TOTAL days dropped':<44} "
          f"{EXPECT_GAP_DAYS + len(EXPECT_OFFHOUR_DAYS):>9} "
          f"{len(all_dropped):>8}  "
          f"{'MATCHES' if len(all_dropped) == EXPECT_GAP_DAYS + len(EXPECT_OFFHOUR_DAYS) else 'SURPRISE'}")

    print()
    print(f"    the F22 forecast gap covers "
          f"{len([d for d in all_days(GAP_START, GAP_END)])} calendar days "
          f"({GAP_START} to {GAP_END});")
    print(f"    {len(gap_dropped)} of them are dropped here. The gap ends at "
          f"2024-01-19 11:00 UTC and the")
    print("    series resumes at 12:00, which is exactly the target hour, so")
    print("    2024-01-19 survives - the same arithmetic F12 found at EGLC.")
    print(f"    Predicted by F22 in advance: {EXPECT_GAP_DAYS} days. "
          f"Found: {len(gap_dropped)}.")

    print()
    print("    every dropped day that is NOT the forecast gap, with the reports")
    print("    the station actually filed near noon:")
    if not other_dropped:
        print("      (none)")
    for d in other_dropped:
        why = []
        if d not in fc:
            why.append("no forecast row")
        elif fc[d] is None:
            why.append("forecast null")
        if d not in obs:
            why.append("no usable observation")
        where = "inner-training" if d <= INNER_END else "validation"
        expected = "expected (F25)" if d in EXPECT_OFFHOUR_DAYS else "NOT EXPECTED"
        print(f"      {d}  [{where}]  {', '.join(why)}  -> {expected}")
        for off, temp in sorted(near_noon.get(d, [])):
            sign = f"{off:+d}"
            print(f"          report at 12:00{sign} min, "
                  f"temp {temp if temp is not None else 'M'}  "
                  f"-> {'kept' if abs(off) <= 15 else 'dropped by D14 (>15 min)'}")
        if not near_noon.get(d):
            print("          no routine report nearest the 12:00 hour at all")

    sub("the dropped validation days, named")
    v_kept = {r["date"] for r in valid}
    v_dropped = [d for d in all_days(VALID_START, VALID_END) if d not in v_kept]
    if not v_dropped:
        print("    (none)")
    for d in v_dropped:
        why = []
        if d not in fc:
            why.append("no forecast row")
        elif fc[d] is None:
            why.append("forecast null")
        if d not in obs:
            why.append("no usable observation")
        print(f"    {d}  ({', '.join(why)})")

    sub("first and last kept rows of each period (a shape check)")
    for label, rows in (("inner-training", inner), ("validation", valid)):
        print(f"    {label:<15} {rows[0]['date']} -> {rows[-1]['date']}   "
              f"{len(rows):,} rows")

    sub("row counts beside EGLC's (F12), for context only")
    print(f"    {'period':<16} {'EGLC kept':>10} {'CDG kept':>10} {'difference':>11}")
    print(f"    {'inner-training':<16} {EGLC_INNER_ROWS:>10,} {len(inner):>10,} "
          f"{len(inner) - EGLC_INNER_ROWS:>+11,}")
    print(f"    {'validation':<16} {EGLC_VALID_ROWS:>10,} {len(valid):>10,} "
          f"{len(valid) - EGLC_VALID_ROWS:>+11,}")

    surprises = (len(gap_dropped) != EXPECT_GAP_DAYS
                 or sorted(other_dropped) != EXPECT_OFFHOUR_DAYS)
    return inner, valid, obs, surprises


# ------------------------------------------------------------------ part B

def bias_look(inner):
    line(f"PART B - {AIRPORT}'s raw bias, INNER-TRAINING ONLY")
    print("bias = observed minus forecast. Positive means the station was")
    print("warmer than GFS predicted. Inner-training days only; the validation")
    print("year's values are not looked at here, and the test year not at all.")

    resid = [r["resid"] for r in inner]

    sub("overall")
    describe(resid, f"bias (observed - forecast), {AIRPORT} inner-training")

    print()
    print(f"    raw GFS MAE on inner-training (in sample): "
          f"{mae(resid):.3f} degC")
    warm = sum(1 for v in resid if v > 0)
    print(f"    days the station was warmer than the forecast: {warm:,} "
          f"of {len(resid):,} ({100 * warm / len(resid):.1f}%)")

    print()
    print("    beside EGLC's inner-training bias (DECISIONS F13):")
    a = np.asarray(resid, dtype=float)
    print(f"      {'':<22} {'EGLC':>9} {'CDG':>9}")
    print(f"      {'days':<22} {EGLC_BIAS['n']:>9,} {len(a):>9,}")
    print(f"      {'mean bias degC':<22} {EGLC_BIAS['mean']:>+9.3f} "
          f"{a.mean():>+9.3f}")
    print(f"      {'median degC':<22} {EGLC_BIAS['median']:>+9.3f} "
          f"{np.median(a):>+9.3f}")
    print(f"      {'st dev degC':<22} {EGLC_BIAS['sd']:>9.3f} "
          f"{a.std(ddof=1):>9.3f}")
    print(f"      {'mean |bias| degC':<22} {EGLC_BIAS['mean_abs']:>9.3f} "
          f"{np.abs(a).mean():>9.3f}")
    print(f"      {'station warmer, %':<22} {EGLC_BIAS['warmer_pct']:>9.1f} "
          f"{100 * warm / len(resid):>9.1f}")

    sub("bias against forecast temperature (warm end or cold end?)")
    edges = [-10, 0, 5, 10, 15, 20, 25, 45]
    print(f"    {'forecast band (degC)':<22} {'days':>6} {'mean bias':>10} "
          f"{'st dev':>8} {'mean |bias|':>12} {'EGLC mean bias':>15}")
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r["resid"] for r in inner if lo <= r["fc"] < hi]
        if not sel:
            continue
        a = np.array(sel)
        label = f"{lo} to {hi}"
        eg = EGLC_BANDS.get(label)
        eg_txt = f"{eg[1]:+.3f}" if eg else "-"
        print(f"    {label:<22} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{(a.std(ddof=1) if len(a) > 1 else float('nan')):>8.3f} "
              f"{np.abs(a).mean():>12.3f} {eg_txt:>15}")

    print()
    print("    the coldest and warmest tenths of forecast days, side by side:")
    by_fc = sorted(inner, key=lambda r: r["fc"])
    tenth = max(1, len(by_fc) // 10)
    for label, sel in (("coldest 10% of forecasts", by_fc[:tenth]),
                       ("warmest 10% of forecasts", by_fc[-tenth:])):
        a = np.array([r["resid"] for r in sel])
        f = np.array([r["fc"] for r in sel])
        eg = EGLC_TAILS[label]
        print(f"      {label:<26} n={len(sel):>4,}  forecast "
              f"{f.min():+.1f} to {f.max():+.1f} degC   "
              f"mean bias {a.mean():+.3f}   mean |bias| {np.abs(a).mean():.3f}")
        print(f"      {'  EGLC, same tail (F13)':<26} n={eg[0]:>4,}  forecast "
              f"{eg[1]:+.1f} to {eg[2]:+.1f} degC   mean bias {eg[3]:+.3f}")

    sub("bias by month")
    print(f"    {'month':<8} {'days':>6} {'mean bias':>10} {'st dev':>8} "
          f"{'mean |bias|':>12} {'mean forecast':>14}")
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m in range(1, 13):
        sel = [r for r in inner if r["date"].month == m]
        if not sel:
            continue
        a = np.array([r["resid"] for r in sel])
        f = np.array([r["fc"] for r in sel])
        print(f"    {names[m - 1]:<8} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{a.std(ddof=1):>8.3f} {np.abs(a).mean():>12.3f} "
              f"{f.mean():>+14.2f}")

    sub("bias by season (three-month groups), CDG beside EGLC")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    print(f"    {'season':<12} {'days':>6} {'mean bias':>10} {'st dev':>8} "
          f"{'mean |bias|':>12} {'EGLC bias':>10} {'EGLC |bias|':>12}")
    for label, months in groups:
        sel = [r["resid"] for r in inner if r["date"].month in months]
        a = np.array(sel)
        eg = EGLC_BIAS_SEASON[label]
        print(f"    {label:<12} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{a.std(ddof=1):>8.3f} {np.abs(a).mean():>12.3f} "
              f"{eg[1]:>+10.3f} {eg[3]:>12.3f}")

    return float(np.mean(resid))


# ------------------------------------------------------------------ part C

def climatology_from_inner(inner):
    """Day-of-year seasonal average of the OBSERVED temperature.

    Built from inner-training days only (SPEC 2.1c). For a given position in
    the year it averages every inner-training observation within +/- 7.5 days
    of that position, measured around the circle so that late December and
    early January are neighbours. The window smooths what would otherwise be
    three or four noisy days per date.
    """
    fracs = np.array([year_fraction(r["date"]) for r in inner])
    obs = np.array([r["obs"] for r in inner])
    half = CLIM_HALF_WINDOW_DAYS / 365.25

    def predict(d):
        f = year_fraction(d)
        dist = np.abs(fracs - f)
        dist = np.minimum(dist, 1.0 - dist)        # go round the circle
        sel = dist <= half
        return float(obs[sel].mean()), int(sel.sum())

    return predict


def model_and_evaluate(inner, valid, obs_all, inner_mean_bias):
    line(f"PART C - run the locked method at {AIRPORT} and rehearse on validation")

    # ---------------------------------------------------------------- the model
    sub("the model (fitted on CDG inner-training only)")
    x_in = features(inner)
    y_in = np.array([r["resid"] for r in inner], dtype=float)
    print(f"    rows fitted on : {len(x_in):,}  "
          f"({inner[0]['date']} to {inner[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (DECISIONS D19)")
    print("    target         : residual, observed minus forecast (SPEC 4.2)")
    print("    settings       : the locked D21.4 set, unchanged from session 05:")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_in, y_in)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    # ------------------------------------------------- the common validation set
    sub("the common validation set (every method judged on the same days)")
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

    print(f"    paired validation rows from part A           : {len(valid):,}")
    print(f"    dropped: no previous-day 12:00 observation   : {len(no_prev):,}"
          + (f"  ({', '.join(str(d) for d in no_prev)})" if no_prev else ""))
    print(f"    days every method is scored on               : {len(common):,}")
    print(f"    date range                                   : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print("    Persistence needs yesterday's observation, which is a past-only")
    print("    value (SPEC 2.1d). Nothing was filled in (SPEC 2.2).")

    # ------------------------------------------------------------- the methods
    clim = climatology_from_inner(inner)
    clim_counts = []
    for r in common:
        c, n = clim(r["date"])
        r["clim"] = c
        clim_counts.append(n)
    print(f"    climatology: built from CDG inner-training only (SPEC 2.1c), "
          f"+/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print(f"                 inner-training days behind each value: "
          f"min {min(clim_counts)}, max {max(clim_counts)}, "
          f"mean {np.mean(clim_counts):.1f}")

    print(f"    mean-bias reference: forecast + {inner_mean_bias:+.4f} degC, "
          f"that figure being the")
    print("                 mean CDG inner-training bias and nothing else.")

    x_va = features(common)
    pred_resid = model.predict(x_va)

    methods = {}
    for r, pr in zip(common, pred_resid):
        methods.setdefault("Raw GFS", []).append(r["fc"] - r["obs"])
        methods.setdefault("Persistence", []).append(r["persist"] - r["obs"])
        methods.setdefault("Climatology", []).append(r["clim"] - r["obs"])
        methods.setdefault("Mean-bias reference", []).append(
            r["fc"] + inner_mean_bias - r["obs"])
        methods.setdefault("ML-corrected", []).append(
            r["fc"] + float(pr) - r["obs"])

    order = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference",
             "ML-corrected"]

    sub(f"CDG VALIDATION-YEAR MAE, {len(common):,} common days "
        f"({VALID_START} to {VALID_END})")
    print(f"    {'method':<22} {'MAE degC':>9} {'bias degC':>10} "
          f"{'RMSE degC':>10} {'worst miss':>11}")
    for name in order:
        e = np.array(methods[name])
        print(f"    {name:<22} {np.abs(e).mean():>9.3f} {(-e.mean()):>+10.3f} "
              f"{math.sqrt((e ** 2).mean()):>10.3f} "
              f"{np.abs(e).max():>11.2f}")
    print()
    print("    MAE  = average size of the miss. Lower is better (SPEC 5.1).")
    print("    bias = mean of (observed - method), so a positive figure means")
    print("           the method ran cold. Shown for information only.")

    # ------------------------------------------------------------ the verdicts
    ml = mae(methods["ML-corrected"])

    sub("does the correction beat each reference on CDG's validation MAE?")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference"]:
        ref = mae(methods[name])
        won = ml < ref
        print(f"    vs {name:<22} {'YES' if won else 'NO ':<4} "
              f"{ml:.3f} against {ref:.3f}  -> "
              f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)")
    ref = mae(methods["Climatology"])
    print(f"    vs {'Climatology':<22} {'YES' if ml < ref else 'NO ':<4} "
          f"{ml:.3f} against {ref:.3f}  -> "
          f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)   "
          f"(optional third check, SPEC 5.2)")

    print()
    print("    This is a VALIDATION REHEARSAL, not the frozen bar (SPEC 5.3).")
    print("    The frozen bar is judged once per airport (SPEC 5.0), on that")
    print("    airport's own sealed test year, in a later session. A good number")
    print("    here means the recipe travels and is ready for CDG's single look.")
    print("    IT DOES NOT MEAN STAGE 2 HAS PASSED.")

    # ---------------------------------------------------- what the model used
    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>14} {'gain share':>11} {'splits':>8} "
          f"{'EGLC share':>11} {'EGLC splits':>12}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, eg_splits = EGLC_IMPORTANCE[n]
        print(f"    {n:<18} {g:>14.1f} {share:>10.1f}% {s:>8,} "
              f"{eg_share:>10.1f}% {eg_splits:>12,}")

    sub("in-sample check only (CDG inner-training, NOT a result)")
    in_pred = model.predict(x_in)
    print(f"    raw GFS MAE on inner-training      : {mae(y_in):.3f} degC")
    print(f"    ML-corrected MAE on inner-training : "
          f"{mae(y_in - in_pred):.3f} degC")
    print(f"    EGLC's equivalent (session 05)     : "
          f"{EGLC_INSAMPLE_ML:.3f} degC")
    print("    Shown only to confirm the fit did something. A model always")
    print("    looks better on the data it was fitted to, so this number")
    print("    proves nothing about performance.")

    sub("how the correction behaved across CDG's validation year, by season")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'ML-corr':>9} "
          f"{'change':>9}")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    for label, months in groups:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw = np.array([methods["Raw GFS"][i] for i in idx])
        mlv = np.array([methods["ML-corrected"][i] for i in idx])
        print(f"    {label:<12} {len(idx):>6,} {np.abs(raw).mean():>9.3f} "
              f"{np.abs(mlv).mean():>9.3f} "
              f"{np.abs(mlv).mean() - np.abs(raw).mean():>+9.3f}")
    print("    ('change' is corrected MAE minus raw GFS MAE for that season.")
    print("     Negative means better than raw GFS.)")

    sub("day by day, not just on average")
    raw_e = np.abs(np.array(methods["Raw GFS"]))
    ml_e = np.abs(np.array(methods["ML-corrected"]))
    better = int((ml_e < raw_e).sum())
    worse = int((ml_e > raw_e).sum())
    same = len(ml_e) - better - worse
    print(f"    closer to the truth than raw GFS : {better:,} of {len(ml_e):,} "
          f"days ({100 * better / len(ml_e):.1f}%)")
    print(f"    further away                     : {worse:,} "
          f"({100 * worse / len(ml_e):.1f}%)")
    print(f"    exactly the same                 : {same:,}")

    sub("the predicted correction itself, CDG validation year")
    describe(pred_resid, "predicted residual applied to the forecast")

    return dict(common=common, methods=methods, model=model,
                in_sample_ml=mae(y_in - in_pred))


# ------------------------------------------------------------------ part D

def compare_with_eglc(res):
    """CDG's rehearsal beside EGLC's - how well did the recipe travel?"""
    line("PART D - how the recipe travelled: CDG beside EGLC")
    print("EGLC's figures are session 05's validation rehearsal (DECISIONS F15),")
    print("quoted from notes/session-05-check-output.txt. The two airports are")
    print("NOT scored on the same weather, so this is a comparison of results,")
    print("not a controlled difference. Only the location changed in the method")
    print("(D26); everything the weather did is free to differ.")

    common, methods = res["common"], res["methods"]
    order = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference",
             "ML-corrected"]

    sub("validation MAE, each airport on its own validation year")
    print(f"    {'method':<22} {'EGLC':>9} {'CDG':>9} {'difference':>11}")
    for name in order:
        now = mae(methods[name])
        then = EGLC_MAE[name]["mae"]
        print(f"    {name:<22} {then:>9.3f} {now:>9.3f} {now - then:>+11.3f}")
    print(f"    {'days scored':<22} {EGLC_DAYS_SCORED:>9,} {len(common):>9,}")
    print("    A positive difference means CDG's figure is larger (worse for")
    print("    every row here, since all five are error measures).")

    sub("the margin over each reference, EGLC against CDG")
    ml_now = mae(methods["ML-corrected"])
    ml_then = EGLC_MAE["ML-corrected"]["mae"]
    print(f"    {'vs':<22} {'EGLC margin':>22} {'CDG margin':>22}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference", "Climatology"]:
        ref_now = mae(methods[name])
        ref_then = EGLC_MAE[name]["mae"]
        m_then = ref_then - ml_then
        m_now = ref_now - ml_now
        print(f"    {name:<22} "
              f"{f'{m_then:+.3f} degC ({100 * m_then / ref_then:+.1f}%)':>22} "
              f"{f'{m_now:+.3f} degC ({100 * m_now / ref_now:+.1f}%)':>22}")
    print("    Margins are degC of MAE saved by the correction. Positive means")
    print("    the correction is ahead of that reference.")

    sub("per season, EGLC against CDG")
    print(f"    {'season':<12} {'EGLC raw':>9} {'EGLC ML':>9} {'EGLC chg':>9}   "
          f"{'CDG raw':>9} {'CDG ML':>9} {'CDG chg':>9}")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    for label, months in groups:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        mlv = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        eg_days, eg_raw, eg_ml = EGLC_SEASON[label]
        print(f"    {label:<12} {eg_raw:>9.3f} {eg_ml:>9.3f} "
              f"{eg_ml - eg_raw:>+9.3f}   {raw:>9.3f} {mlv:>9.3f} "
              f"{mlv - raw:>+9.3f}")
    print("    'chg' is corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse.")

    sub("seasons where the correction helped")
    helped = 0
    for label, months in groups:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        mlv = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        if mlv < raw:
            helped += 1
    print(f"    CDG : {helped} of 4")
    print("    EGLC: 3 of 4 (session 05 - winter was the one it made worse)")

    sub("feature importances, EGLC against CDG")
    model = res["model"]
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'EGLC gain %':>12} {'CDG gain %':>12} "
          f"{'EGLC splits':>12} {'CDG splits':>12}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, eg_splits = EGLC_IMPORTANCE[n]
        print(f"    {n:<18} {eg_share:>11.1f}% {share:>11.1f}% "
              f"{eg_splits:>12,} {s:>12,}")
    print("    Gain totals depend on the data, so the shares and split counts")
    print("    are what compare meaningfully between two airports.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line(f"SESSION 11 - {AIRPORT} ({STATION}) join, bias look and validation "
         f"rehearsal")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"airport       : {AIRPORT} / {STATION} (SPEC 3.4) - stage 2 (D26)")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1)")
    print(f"inner-training: {INNER_START} to {INNER_END}   (DECISIONS D18)")
    print(f"validation    : {VALID_START} to {VALID_END}   (DECISIONS D18)")
    print(f"sealed test   : {SEALED_FROM} onward - NOT LOADED THIS SESSION")
    print("what changed  : the location, and nothing else (DECISIONS D26)")

    prove_only_location_changed()
    inner, valid, obs_all, surprises = join()
    if surprises:
        print()
        print("!!! The drop reconciliation did not match session 10's gap map.")
        print("!!! The session prompt says to stop and flag that rather than")
        print("!!! proceed. Nothing below this line was run.")
        sys.stdout = sys.__stdout__
        tee.flush()
        raise SystemExit(1)

    inner_mean_bias = bias_look(inner)
    res = model_and_evaluate(inner, valid, obs_all, inner_mean_bias)
    compare_with_eglc(res)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). No CDG test-year")
    print("value was loaded, printed or fitted on. Nothing was committed.")
    print("This is a rehearsal on CDG's validation year. The frozen bar")
    print("(SPEC 5.3) has NOT been judged and STAGE 2 HAS NOT PASSED.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
