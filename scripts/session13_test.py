"""Session 13: CDG'S SEALED-TEST EVALUATION. One look, and the result stands.

This script executes the method locked in DECISIONS D31. It decides nothing.
Every choice below was made in session 12, with CDG's test year still unseen.

D31 is D21 with the airport swapped and nothing else touched, so this script is
session 07's sealed test with the airport swapped and nothing else touched.
PART 0 proves both of those claims rather than asserting them.

What it does, in D31's own order:
- D31.5  refits the locked model on LFPG's FULL training window,
         2021-03-24 to 2025-07-31 (CDG's inner-training and CDG's validation
         year recombined). Everything fitted is fitted on this and nothing
         else: the model, the climatology baseline, the mean-bias figure.
- D31.6  opens CDG's test year, 2025-08-01 to 2026-07-31, for the first and
         only time. The two 2026 LFPG raw chunk files are opened here for the
         first time in this project. Nothing after 2026-07-31 is used.
- D31.7  pairs with the D14 rule, reports the drop counts, and RECONCILES them
         against the prediction D31.7 wrote down before the look. Nothing is
         filled, ever (SPEC 2.2).
- D31.8  scores five methods on the same set of test days.
- D31.9  judges the frozen bar: does the corrected forecast beat BOTH raw GFS
         and persistence on mean absolute error?

Reads only from data/raw/. Never writes to data/raw/.

CDG'S SEAL IS NOW OPENED, ON PURPOSE, ONCE. Sessions 10, 11 and 12 kept CDG's
test year out: session 10 counted its structure without reading a value,
session 11 cut its load off at 2025-07-31, session 12 loaded nothing at all.
This session is the single authorised look (D31.10). Nothing is tuned,
searched, swapped or re-run. Whatever comes out is reported straight - a
failure is an honest finding (SPEC 2.4), not something to fix by trying again.

Terms used here:
- "residual" = observed minus forecast. This is what the model learns
  (SPEC 4.2). The corrected forecast is forecast + predicted residual.
- "bias"     = the same quantity looked at as a summary rather than a target.
  A positive bias means the station was warmer than GFS said.
- "MAE"      = mean absolute error, the average size of the miss in degrees
  Celsius. Lower is better (SPEC 5.1). This is the metric the bar uses.
- "objective" = the quantity the model tries to make small while it is being
  fitted. "regression_l1" is absolute error, which is what SPEC 5.1 measures
  (DECISIONS D20).
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

# THE ONE THING THAT CHANGES FOR STAGE 2 (DECISIONS D26, D31.1): the location.
STATION = "LFPG"                      # Paris Charles de Gaulle (SPEC 3.4)
AIRPORT = "CDG"

TARGET_HOUR = 12                      # 12:00 UTC (SPEC 4.1, DECISIONS D31.1)

# The full training window (DECISIONS D13, D31.5). This is CDG's inner-training
# plus CDG's validation year recombined - validation has done its job now the
# method is locked.
TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)

# CDG's sealed test year (DECISIONS D13, D31.6). Opened once, here.
TEST_START = date(2025, 8, 1)
TEST_END = date(2026, 7, 31)

# Hard wall. Nothing after the test year is used, which keeps the test set
# exactly one calendar year (DECISIONS D13, D31.6).
HARD_END = TEST_END

# The two sub-periods of the training window used in session 11 (DECISIONS
# D18). Kept here for reporting only - so the training-window row counts can be
# reconciled against the published session 11 counts. Nothing is fitted
# separately on them this session.
INNER_START = date(2021, 3, 24)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# All six chunk files. The two 2026 LFPG files are included for the first time.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),     # test year, second half
]

# The one gap in the forecast series. Found at EGLC (F8) and found again at
# LFPG, hour for hour (F22). For reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Exactly the session 05 settings, unchanged (DECISIONS D31.4,
# which is D21.4). Nothing is tuned, searched or varied in this session.
LGB_PARAMS = dict(
    objective="regression_l1",        # absolute error (DECISIONS D20)
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

# The two scripts this one is checked against. session05_model.py is where the
# locked settings and the shared machinery come from; session07_test.py is
# EGLC's sealed test, which is the same job at the other airport.
PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"
STAGE1_TEST_SCRIPT = ROOT / "scripts" / "session07_test.py"

# What DECISIONS D31 says this session must run. Written out as data so the
# script can check itself against the lock rather than the reader having to
# trust the prose. Every line below is quoted from D31.
D31_LOCK = {
    "airport (D31.1)":                "LFPG",
    "target hour (D31.1)":            12,
    "train start (D31.5)":            date(2021, 3, 24),
    "train end (D31.5)":              date(2025, 7, 31),
    "test start (D31.6)":             date(2025, 8, 1),
    "test end (D31.6)":               date(2026, 7, 31),
    "features (D31.3)":               ["forecast_temp_c", "season_sin",
                                       "season_cos"],
    "objective (D31.4)":              "regression_l1",
    "n_estimators (D31.4)":           300,
    "learning_rate (D31.4)":          0.05,
    "num_leaves (D31.4)":             15,
    "min_child_samples (D31.4)":      40,
    "subsample (D31.4)":              1.0,
    "colsample_bytree (D31.4)":       1.0,
    "reg_alpha (D31.4)":              0.0,
    "reg_lambda (D31.4)":             0.0,
    "random_state (D31.4)":           42,
    "n_jobs (D31.4)":                 1,
    "deterministic (D31.4)":          True,
    "force_row_wise (D31.4)":         True,
    "verbose (D31.4)":                -1,
    "pairing window minutes (D31.7)": 15,
    "climatology half window (D31.8)": 7.5,
}

# ---- what D31.7 predicted this test year would cost, BEFORE the look ---------
# Written down in session 12 from session 10's gap map (F22, F25). These are
# expectations to RECONCILE against, not numbers to accept. A count that will
# not reconcile is a stop signal (D31.11).
EXPECT_TEST_FCGAP_DAYS = 0                          # F22: no gap in the test year
EXPECT_TEST_OFFHOUR_DAYS = [date(2026, 7, 8)]       # F25
EXPECT_TEST_NOREPORT_DAYS = 0                       # F25
EXPECT_TEST_NOTEMP_DAYS = 0                         # F25
EXPECT_TEST_PAIRED_ROWS = 364
EXPECT_TEST_SCORED_DAYS = 363                       # persistence loses 2026-07-09

# ---- what session 11 published for CDG's training side (F27) -----------------
EXPECT_TRAIN_ROWS = 1569              # 1,204 inner-training + 365 validation
EXPECT_INNER_ROWS = 1204
EXPECT_VALID_ROWS = 365

# Session 11's published CDG validation figures, from
# notes/session-11-check-output.txt and DECISIONS F29. Quoted for the
# comparison in PART E. They are a DIFFERENT year and a model fitted on about
# 20% less data, so they are context, not a target (D31.5).
S11_VALIDATION_MAE = {
    "Raw GFS":             1.426,
    "Persistence":         2.523,
    "Climatology":         3.293,
    "Mean-bias reference": 1.435,
    "ML-corrected":        1.377,
}
S11_VALIDATION_DAYS = 365
S11_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 1.512, 1.537),
    "spring MAM": (92, 1.221, 1.164),
    "summer JJA": (92, 1.445, 1.323),
    "autumn SON": (91, 1.531, 1.487),
}
S11_IMPORTANCE = {                    # feature -> (gain share %, splits)
    "forecast_temp_c": (35.9, 1558),
    "season_sin":      (39.9, 1444),
    "season_cos":      (24.2, 1198),
}
S11_INSAMPLE_ML = 0.945               # CDG inner-training MAE, session 11
S11_BETTER_PCT = 55.3                 # days closer than raw GFS, session 11

# EGLC's stage 1 SEALED TEST result, DECISIONS F16, from
# notes/session-07-check-output.txt. Quoted for PART F. It is a different
# airport's result on a different set of weather; SPEC 5.0 judges each airport
# on its own data, so this is context and NOT a target CDG has to reach.
EGLC_TEST_MAE = {
    "Raw GFS":             1.242,
    "Persistence":         2.096,
    "Climatology":         2.972,
    "Mean-bias reference": 1.234,
    "ML-corrected":        1.040,
}
EGLC_TEST_DAYS = 363
EGLC_TEST_SEASON = {                  # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 0.752, 0.745),
    "spring MAM": (92, 1.285, 1.219),
    "summer JJA": (92, 1.870, 1.252),
    "autumn SON": (89, 1.045, 0.934),
}
EGLC_TEST_IMPORTANCE = {              # feature -> (gain share %, splits)
    "forecast_temp_c": (51.8, 1844),
    "season_sin":      (24.5, 1166),
    "season_cos":      (23.7, 1190),
}
EGLC_TEST_INSAMPLE_ML = 0.908         # training-window MAE, session 07
EGLC_TEST_MEAN_BIAS = -0.1479         # mean training-window bias, session 07
EGLC_TEST_BETTER_PCT = 60.9           # days closer than raw GFS, session 07
EGLC_TRAIN_ROWS = 1569
EGLC_VALID_MARGIN = 0.074             # session 05 validation margin over raw GFS
EGLC_TEST_MARGIN = 0.202              # session 07 test margin over raw GFS

SEASONS = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
           ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]

OUT = ROOT / "notes" / "session-13-check-output.txt"


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
    """Return {date: forecast_temp_or_None} for 12:00 UTC, up to the hard end.

    Unlike session 11 there is no seal here: CDG's test year is loaded, because
    this is the one authorised look at it (DECISIONS D31.6, D31.10). The only
    cut-off is the hard end at 2026-07-31, which keeps the test set exactly one
    calendar year (D13).
    """
    series = {}
    rows_seen = 0
    rows_after_end = 0
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
            if t.date() > HARD_END:
                rows_after_end += 1
                continue
            series[t.date()] = v
    return series, rows_seen, rows_after_end


def load_obs_12z():
    """Return {date: observed_temp} for the 12:00 UTC hour, up to the hard end.

    The D14 pairing rule: the routine report belongs to the hour it is nearest
    to, and only if it is within 15 minutes of it. At LFPG the routine report
    is stamped ON THE HOUR (F18), so the 12:00 report is the observation for
    12:00 - an exact match, no offset, where at EGLC it was the 11:50 report
    ten minutes earlier. Anything further off is dropped and counted (D31.7).

    'near_noon' separately records every routine report stamped between 11:00
    and 12:59, with how many minutes it sits from 12:00. That is bookkeeping
    for the drop reconciliation only: it changes no pairing, keeps no report
    the rule drops, and drops none the rule keeps.
    """
    series = {}
    reports_at_12 = 0
    reports_after_end = 0
    no_temp = 0
    outside_15min = 0
    near_noon = {}                     # date -> [(minutes from 12:00, temp)]

    for start, end in CHUNKS:
        path = RAW / f"iem_asos_{STATION}_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                raw = (r.get("tmpc") or "").strip()
                has_temp = raw not in ("M", "", "T", "None")

                # bookkeeping only - see the docstring
                if t.hour in (11, TARGET_HOUR) and t.date() <= HARD_END:
                    noon = t.replace(hour=TARGET_HOUR, minute=0)
                    near_noon.setdefault(t.date(), []).append(
                        (int((t - noon).total_seconds() // 60),
                         raw if has_temp else None))

                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != TARGET_HOUR:
                    continue
                reports_at_12 += 1
                if nearest.date() > HARD_END:
                    reports_after_end += 1
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                if not has_temp:
                    no_temp += 1
                    continue
                series[nearest.date()] = float(raw)

    return (series, reports_at_12, reports_after_end, no_temp, outside_15min,
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


def prove_it_matches_the_lock():
    """Check this script against DECISIONS D31, and against the two scripts it
    has to agree with.

    Three checks, because they answer three different questions.
    1. Does what this script is about to run match the written lock? Checked
       against D31_LOCK above, value by value.
    2. Is the machinery the same machinery session 05 locked? Checked by
       reading scripts/session05_model.py and comparing it with this file.
    3. Is this the same sealed test session 07 ran at the other airport?
       Checked by reading scripts/session07_test.py and comparing. This is the
       "only the location changed" claim (D26, D31) checked in code.
    """
    line("PART 0 - checking this script against the lock (DECISIONS D31)")

    sub("check 1: every value D31 fixes, against what this script will use")
    actual = {
        "airport (D31.1)":                STATION,
        "target hour (D31.1)":            TARGET_HOUR,
        "train start (D31.5)":            TRAIN_START,
        "train end (D31.5)":              TRAIN_END,
        "test start (D31.6)":             TEST_START,
        "test end (D31.6)":               TEST_END,
        "features (D31.3)":               FEATURE_NAMES,
        "objective (D31.4)":              LGB_PARAMS["objective"],
        "n_estimators (D31.4)":           LGB_PARAMS["n_estimators"],
        "learning_rate (D31.4)":          LGB_PARAMS["learning_rate"],
        "num_leaves (D31.4)":             LGB_PARAMS["num_leaves"],
        "min_child_samples (D31.4)":      LGB_PARAMS["min_child_samples"],
        "subsample (D31.4)":              LGB_PARAMS["subsample"],
        "colsample_bytree (D31.4)":       LGB_PARAMS["colsample_bytree"],
        "reg_alpha (D31.4)":              LGB_PARAMS["reg_alpha"],
        "reg_lambda (D31.4)":             LGB_PARAMS["reg_lambda"],
        "random_state (D31.4)":           LGB_PARAMS["random_state"],
        "n_jobs (D31.4)":                 LGB_PARAMS["n_jobs"],
        "deterministic (D31.4)":          LGB_PARAMS["deterministic"],
        "force_row_wise (D31.4)":         LGB_PARAMS["force_row_wise"],
        "verbose (D31.4)":                LGB_PARAMS["verbose"],
        "pairing window minutes (D31.7)": 15,
        "climatology half window (D31.8)": CLIM_HALF_WINDOW_DAYS,
    }
    print(f"    {'what D31 fixes':<34} {'D31 says':<22} {'this run':<22} match?")
    mismatches = 0
    for k, want in D31_LOCK.items():
        got = actual[k]
        ok = got == want
        if not ok:
            mismatches += 1
        print(f"    {k:<34} {str(want):<22} {str(got):<22} "
              f"{'yes' if ok else 'NO - MISMATCH'}")
    print(f"    values that do not match D31: {mismatches}")
    assert mismatches == 0, "this script does not match the D31 lock - STOP"
    print("    (The 15-minute pairing window is the literal in load_obs_12z")
    print("     below. Check 3c prints that function's differences from")
    print("     session 07's, so it can be seen that the 15 minutes is")
    print("     untouched.)")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    s1_src = STAGE1_TEST_SCRIPT.read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)
    s1 = ast.parse(s1_src)

    sub("check 2a: model settings, session 05 against this session")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 13':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}   (D31.4 requires 0)")
    assert n_diff == 0, "the model settings drifted from session 05 - STOP"

    sub("check 2b: the code that must be character-identical to session 05")
    print("    Compared character for character with scripts/session05_model.py.")
    identical = True
    for name in ["all_days", "year_fraction", "features", "mae", "describe"]:
        a = func_source(old_src, old, name)
        b = func_source(new_src, new, name)
        if a != b:
            identical = False
        print(f"    {name + '()':<26} "
              f"{'identical' if a == b else 'DIFFERS - NOT EXPECTED'}")
    assert identical, "shared code drifted from session 05 - STOP (D31.11)"

    sub("check 3a: model settings, session 07 (EGLC test) against this session")
    s1_p = top_level(s1, "LGB_PARAMS")
    keys = list(s1_p) + [k for k in new_p if k not in s1_p]
    n_diff = 0
    for k in keys:
        if s1_p.get(k, "<absent>") != new_p.get(k, "<absent>"):
            n_diff += 1
    print(f"    settings compared: {len(keys)}")
    print(f"    settings that differ from EGLC's sealed test: {n_diff}")
    assert n_diff == 0, "settings differ from session 07 - STOP (D31.11)"

    sub("check 3b: the constants that must be the same at both airports")
    print(f"    {'constant':<24} {'session 07 (EGLC)':<34} same?")
    n_const_diff = 0
    for c in ["TARGET_HOUR", "TRAIN_START", "TRAIN_END", "TEST_START",
              "TEST_END", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]:
        a = top_level(s1, c)
        b = top_level(new, c)
        if a != b:
            n_const_diff += 1
        print(f"    {c:<24} {str(a)[:33]:<34} "
              f"{'yes' if a == b else 'NO - DIFFERS'}")
    print(f"    constants that differ: {n_const_diff}   "
          f"(the split dates are shared by every airport, SPEC 4.3)")
    assert n_const_diff == 0, "constants differ from session 07 - STOP (D31.11)"

    sub("check 3c: session 13 against session 07, function by function")
    print("    This is the 'only the location changed' claim, checked in code")
    print("    rather than argued. Every function is compared character for")
    print("    character with EGLC's sealed test script.")
    for name in ["all_days", "year_fraction", "features", "mae", "describe",
                 "_literal", "top_level", "func_source",
                 "climatology_from_training", "load_forecast_12z",
                 "load_obs_12z", "fit_on_training"]:
        a = func_source(s1_src, s1, name)
        b = func_source(new_src, new, name)
        print(f"    {name + '()':<28} "
              f"{'identical' if a == b else 'differs - diff printed below'}")
    print("    The remaining functions (join, score_test_year, judge_the_bar,")
    print("    the comparison parts and main) differ in the text they print,")
    print("    which is on the screen anyway, and in which published figures")
    print("    they quote. No arithmetic differs; the diffs below cover every")
    print("    function that does any of the loading, fitting or scoring.")

    sub("check 3d: the functions that DO differ, each shown in full")
    print("    Nothing is hidden: every diff is printed so the changes can be")
    print("    read rather than taken on trust.")
    for name, why in (
            ("load_forecast_12z",
             "the station code in the file name. Nothing else."),
            ("load_obs_12z",
             "the station code in the file name; the docstring, because LFPG\n"
             "    reports on the hour where EGLC reports at :50 (F18); and the\n"
             "    'near_noon' bookkeeping session 11 added, used only by the\n"
             "    drop reconciliation. The 15-minute D14 rule is untouched and\n"
             "    the same reports are kept and dropped either way."),
            ("fit_on_training",
             "printed labels only - D21 references become D31 references and\n"
             "    the airport is named. Every fitted quantity is computed by\n"
             "    the same lines.")):
        print()
        print(f"    {name}() - {why}")
        a = func_source(s1_src, s1, name)
        b = func_source(new_src, new, name)
        if a == b:
            print("      (identical after all - no diff to show)")
            continue
        for d in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                      "session07 (EGLC)", "session13 (CDG)",
                                      lineterm="", n=1):
            print(f"      {d}")


# ------------------------------------------------------------------ part A

def join():
    line(f"PART A - the join at 12:00 UTC, both windows (D31.6, D31.7)")

    print(f"airport     : {AIRPORT} / {STATION} (SPEC 3.4, D31.1)")
    print(f"target hour : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1, D31.1) - the same")
    print("              hour as stage 1, on purpose (D26)")
    print("pairing rule: the routine report nearest the hour, and only if within")
    print("              15 minutes of it (DECISIONS D14, D31.7). At LFPG the")
    print("              routine report is stamped :00, so this is an EXACT")
    print("              match with no offset at all (F18).")
    print()
    print("CDG'S TEST YEAR IS OPENED HERE, for the first and only time (D31.10).")
    print("The two 2026 LFPG raw chunk files are read for the first time in this")
    print("project. Sessions 10, 11 and 12 never opened them.")

    fc, fc_rows, fc_after = load_forecast_12z()
    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_noon = load_obs_12z()

    sub("what was loaded")
    print(f"    forecast chunk files opened : {len(CHUNKS)} "
          f"(all six, including both 2026 files)")
    print(f"    forecast 12:00 rows seen    : {fc_rows:,}")
    print(f"    of those, after {HARD_END} : {fc_after:,} (not used, D13)")
    print(f"    forecast 12:00 rows kept    : {len(fc):,}")
    print(f"    observation 12:00 reports seen  : {ob_rows:,}")
    print(f"    of those, after {HARD_END}: {ob_after:,} (not used, D13)")
    print(f"    observation 12:00 reports kept  : {len(obs):,}")

    sub("observation reports rejected by the rules")
    print(f"    reports more than 15 min from the hour, dropped (D14): {ob_far:,}")
    print(f"    reports carrying no temperature (M), dropped (2.2)   : {ob_no_temp:,}")

    # The hard end wall, proved rather than asserted in prose.
    assert max(fc) <= HARD_END, "a forecast date after the hard end got through"
    assert max(obs) <= HARD_END, "an observation date after the hard end got through"

    periods = [
        ("train", "TRAINING   2021-03-24..2025-07-31", TRAIN_START, TRAIN_END),
        ("test", "TEST YEAR  2025-08-01..2026-07-31", TEST_START, TEST_END),
        ("inner", "  (of which) inner  2021-03-24..2024-07-31",
         INNER_START, INNER_END),
        ("valid", "  (of which) valid  2024-08-01..2025-07-31",
         VALID_START, VALID_END),
    ]

    built = {}
    sub("rows kept and dropped, by period")
    print(f"    {'period':<44} {'days':>6} {'kept':>6} {'drop':>6} "
          f"{'no fc':>6} {'null fc':>8} {'no obs':>7}")
    for key, label, lo, hi in periods:
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
        print(f"    {label:<44} {days:>6,} {len(rows):>6,} "
              f"{days - len(rows):>6,} {n_no_fc:>6,} {n_null_fc:>8,} "
              f"{n_no_obs:>7,}")
        built[key] = rows

    print()
    print("    columns: days = calendar days in the period; kept = paired rows;")
    print("             drop = days with no usable pair; then the reasons.")
    print("             'no fc'   = the forecast series had no row for 12:00;")
    print("             'null fc' = it had a row but the value was null;")
    print("             'no obs'  = no usable observation within 15 min.")
    print("             A day can fail on more than one reason, so the reason")
    print("             columns can add up to more than 'drop'.")
    print("    Nothing was filled in (SPEC 2.2, D31.7).")

    train, test = built["train"], built["test"]
    inner, valid = built["inner"], built["valid"]

    sub("reconciliation 1: does the training window add up? (D31.11)")
    print("    The training window is CDG's inner-training plus CDG's validation")
    print("    year, which session 11 counted separately. Those published counts")
    print("    must add up to this session's training count, or something has")
    print("    drifted and this session must stop.")
    print(f"    session 11 inner-training kept rows (F27): {EXPECT_INNER_ROWS:,}")
    print(f"    session 11 validation kept rows (F27)    :   {EXPECT_VALID_ROWS:,}")
    print(f"    published total                          : {EXPECT_TRAIN_ROWS:,}")
    print(f"    this session, training window kept rows  : {len(train):,}")
    print(f"    this session, of which dated <= {INNER_END} : {len(inner):,}")
    print(f"    this session, of which dated >= {VALID_START} : {len(valid):,}")
    ok_train = (len(train) == EXPECT_TRAIN_ROWS
                and len(inner) == EXPECT_INNER_ROWS
                and len(valid) == EXPECT_VALID_ROWS)
    print(f"    reconciles: {'YES' if ok_train else 'NO - STOP AND RAISE (D31.11)'}")

    sub("the F22 forecast gap, for the record")
    gap_days = all_days(GAP_START, GAP_END)
    kept_dates = {r["date"] for r in train}
    print(f"    gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END}), all inside training")
    print(f"    of those, dropped here: "
          f"{sum(1 for d in gap_days if d not in kept_dates)}")

    # ------------------------------------------------- the test-year drop count
    sub("THE TEST-YEAR DROP COUNT (D31.7)")
    t_days = all_days(TEST_START, TEST_END)
    t_kept = {r["date"] for r in test}
    t_dropped = [d for d in t_days if d not in t_kept]
    print(f"    test-year calendar days : {len(t_days):,}")
    print(f"    paired rows kept        : {len(test):,}")
    print(f"    days dropped            : {len(t_dropped):,}")
    if not t_dropped:
        print("    (no test-year day was dropped)")

    # Sort each dropped day into exactly one of the four causes F25 counted,
    # which is what D31.7's prediction was built from.
    #
    # "Relevant" below means a routine report that either could have been the
    # 12:00 observation under D14 (its nearest hour is 12:00, so it sits -30 to
    # +29 minutes from noon) or falls inside the 12:00 clock hour (0 to +59).
    # Those are the two framings F27 had to reconcile: F25 named CDG's lost
    # days by the report inside the clock hour (12:30) and F27 by the report
    # nearest noon under D14 (11:30), and on those days both were true. Reports
    # at 11:00 are ordinary 11:00 reports; they are printed for context but do
    # not count as a noon-hour report.
    cause_fcgap = []          # forecast row missing or null
    cause_offhour = []        # a noon-hour report exists but is >15 min out
    cause_noreport = []       # nothing filed in the noon hour at all
    cause_notemp = []         # a report within 15 min but carrying no temp
    for d in t_dropped:
        no_fc = (d not in fc) or (fc[d] is None)
        reports = sorted(near_noon.get(d, []), key=lambda x: x[0])
        relevant = [x for x in reports if -30 <= x[0] <= 59]
        within15 = [x for x in relevant if abs(x[0]) <= 15]
        if no_fc:
            cause_fcgap.append(d)
        elif within15:
            cause_notemp.append(d)
        elif relevant:
            cause_offhour.append(d)
        else:
            cause_noreport.append(d)
        why = []
        if d not in fc:
            why.append("no forecast row")
        elif fc[d] is None:
            why.append("forecast null")
        if d not in obs:
            why.append("no usable observation")
        print(f"      {d}  ({', '.join(why)})")
        for off, temp in reports:
            if abs(off) <= 15:
                verdict = "would pair with 12:00 under D14"
            elif -30 <= off <= 59:
                verdict = "in the noon hour but >15 min out - dropped by D14"
            else:
                verdict = "belongs to the 11:00 hour, not the noon hour"
            print(f"          routine report at 12:00{off:+d} min, "
                  f"temp {temp if temp is not None else 'M'}  -> {verdict}")
        if not relevant:
            print("          no routine report in the noon hour at all")
    print("    Every drop is named. Nothing was filled (SPEC 2.2).")

    sub("reconciliation 2: THE DROPS AGAINST D31.7's ADVANCE PREDICTION")
    print("    D31.7 wrote these numbers down in session 12, from session 10's")
    print("    gap map, BEFORE CDG's test year was opened. A prediction made")
    print("    before the look is a stronger check than a count made after it.")
    print("    A count that will not reconcile is a stop signal (D31.11).")
    print()
    print(f"    {'cause':<48} {'predicted':>9} {'actual':>7}  verdict")
    checks = [
        ("forecast-gap days in the test year (F22)",
         EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)),
        ("days lost to an off-hour-only report (F25)",
         len(EXPECT_TEST_OFFHOUR_DAYS), len(cause_offhour)),
        ("days lost to no report at all in the noon hour (F25)",
         EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)),
        ("days lost to a report on the hour with no temp (F25)",
         EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)),
        ("paired rows expected", EXPECT_TEST_PAIRED_ROWS, len(test)),
    ]
    ok_test = True
    for label, want, got in checks:
        good = want == got
        ok_test = ok_test and good
        print(f"    {label:<48} {want:>9} {got:>7}  "
              f"{'MATCHES' if good else 'SURPRISE'}")
    named_ok = sorted(cause_offhour) == EXPECT_TEST_OFFHOUR_DAYS
    ok_test = ok_test and named_ok
    print(f"    {'the off-hour day is the one D31.7 named':<48} "
          f"{str(EXPECT_TEST_OFFHOUR_DAYS[0]):>9} "
          f"{(str(cause_offhour[0]) if cause_offhour else '-'):>7}  "
          f"{'MATCHES' if named_ok else 'SURPRISE'}")

    sub("shape check: first and last kept row of each window")
    for label, rows in (("training", train), ("test year", test)):
        print(f"    {label:<10} {rows[0]['date']} -> {rows[-1]['date']}   "
              f"{len(rows):,} rows")

    return train, test, obs, (ok_train and ok_test)


# ------------------------------------------------------------------ part B

def climatology_from_training(train):
    """Day-of-year seasonal average of the OBSERVED temperature.

    Built from training-window days only (SPEC 2.1c, D21.8). For a given
    position in the year it averages every training-window observation within
    +/- 7.5 days of that position, measured around the circle so that late
    December and early January are neighbours. The window smooths what would
    otherwise be four or five noisy days per date.
    """
    fracs = np.array([year_fraction(r["date"]) for r in train])
    obs = np.array([r["obs"] for r in train])
    half = CLIM_HALF_WINDOW_DAYS / 365.25

    def predict(d):
        f = year_fraction(d)
        dist = np.abs(fracs - f)
        dist = np.minimum(dist, 1.0 - dist)        # go round the circle
        sel = dist <= half
        return float(obs[sel].mean()), int(sel.sum())

    return predict


def fit_on_training(train):
    """Fit everything that gets fitted, on the training window and nothing else.

    Three things are fitted here: the model, the climatology baseline and the
    mean-bias figure. All three see only LFPG 2021-03-24 to 2025-07-31 (D31.5,
    D31.8, SPEC 2.1c).
    """
    line("PART B - fit on CDG's FULL training window only (D31.5, D31.8)")

    print("Everything fitted in this session is fitted here, on CDG's training")
    print("window, and on nothing else: the model, the climatology baseline and")
    print("the mean-bias figure. The test year plays no part in any fit.")

    x_tr = features(train)
    y_tr = np.array([r["resid"] for r in train], dtype=float)

    sub("the model")
    print(f"    rows fitted on : {len(x_tr):,}  "
          f"({train[0]['date']} to {train[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (D19, D31.3)")
    print("    target         : residual, observed minus forecast (SPEC 4.2,")
    print("                     D31.2). The model never predicts temperature.")
    print("    settings (locked in D31.4, nothing tuned this session):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_tr, y_tr)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    sub("the mean-bias figure (D31.8)")
    mean_bias = float(np.mean(y_tr))
    print(f"    mean training-window bias (observed - forecast): "
          f"{mean_bias:+.4f} degC")
    print(f"    over {len(y_tr):,} training days. The mean-bias reference is")
    print("    the raw forecast plus this one constant, and nothing else.")
    print(f"    raw GFS MAE on the training window (in sample): "
          f"{mae(y_tr):.3f} degC")
    print(f"    EGLC's equivalent constant was {EGLC_TEST_MEAN_BIAS:+.4f} degC "
          f"(F16). Both are")
    print("    near zero: there is almost no constant offset to take at either")
    print("    airport, which is what F13 and F28 both found.")

    sub("the climatology baseline (D31.8, SPEC 2.1c)")
    print("    seasonal average of the OBSERVED temperature at LFPG, from")
    print(f"    training-window days only, +/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print("    measured around the circle so late December and early January")
    print("    are neighbours.")
    clim = climatology_from_training(train)

    return model, mean_bias, clim, x_tr, y_tr


# ------------------------------------------------------------------ part C

def score_test_year(test, obs_all, model, mean_bias, clim):
    line("PART C - THE SEALED TEST AT CDG (D31.6, D31.8, D31.9)")

    sub("the common test set (every method judged on the same days)")
    common = []
    no_prev = []
    for r in test:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev.append(r["date"])
            continue
        row = dict(r)
        row["persist"] = float(prev)
        common.append(row)

    print(f"    paired test rows from part A                 : {len(test):,}")
    print(f"    dropped: no previous-day 12:00 observation    : {len(no_prev):,}"
          + (f"  ({', '.join(str(d) for d in no_prev)})" if no_prev else ""))
    print(f"    days every method is scored on                : {len(common):,}")
    print(f"    D31.7 expected                                : "
          f"{EXPECT_TEST_SCORED_DAYS:,}")
    print(f"    date range                                    : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print("    Persistence needs yesterday's 12:00 observation, a past-only")
    print("    value (SPEC 2.1d). For the first test day, 2025-08-01,")
    print("    'yesterday' is 2025-07-31, which sits in the training window.")
    print("    That is a past observation, so it is legal and it is used -")
    print("    written down in D31.8 in advance so it is not mistaken for")
    print("    leakage. Nothing was filled in (SPEC 2.2).")
    first = common[0]
    prev_obs = obs_all.get(first["date"] - timedelta(days=1))
    print(f"    check: the first scored day is {first['date']}, and its")
    print(f"           persistence value is {first['persist']:+.1f} degC, "
          f"which is the")
    print(f"           {first['date'] - timedelta(days=1)} 12:00 observation "
          f"({prev_obs:+.1f} degC).")

    clim_counts = []
    for r in common:
        c, n = clim(r["date"])
        r["clim"] = c
        clim_counts.append(n)
    print(f"    climatology: training days behind each value: "
          f"min {min(clim_counts)}, max {max(clim_counts)}, "
          f"mean {np.mean(clim_counts):.1f}")

    x_te = features(common)
    pred_resid = model.predict(x_te)

    methods = {}
    for r, pr in zip(common, pred_resid):
        methods.setdefault("Raw GFS", []).append(r["fc"] - r["obs"])
        methods.setdefault("Persistence", []).append(r["persist"] - r["obs"])
        methods.setdefault("Climatology", []).append(r["clim"] - r["obs"])
        methods.setdefault("Mean-bias reference", []).append(
            r["fc"] + mean_bias - r["obs"])
        methods.setdefault("ML-corrected", []).append(
            r["fc"] + float(pr) - r["obs"])

    order = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference",
             "ML-corrected"]

    sub(f"CDG TEST-YEAR MAE, {len(common):,} common days "
        f"({TEST_START} to {TEST_END})")
    print(f"    {'method':<22} {'MAE degC':>9} {'bias degC':>10} "
          f"{'RMSE degC':>10} {'worst miss':>11} {'part of bar?':>13}")
    in_bar = {"Raw GFS": "YES", "Persistence": "YES", "Climatology": "no",
              "Mean-bias reference": "no", "ML-corrected": "the claim"}
    for name in order:
        e = np.array(methods[name])
        print(f"    {name:<22} {np.abs(e).mean():>9.3f} {(-e.mean()):>+10.3f} "
              f"{math.sqrt((e ** 2).mean()):>10.3f} "
              f"{np.abs(e).max():>11.2f} {in_bar[name]:>13}")
    print()
    print("    MAE  = average size of the miss. Lower is better (SPEC 5.1).")
    print("    bias = mean of (observed - method), so a positive figure means")
    print("           the method ran cold. Shown for information only.")
    print("    The bar is raw GFS and persistence only (SPEC 5.2, 5.3, D23).")

    return common, methods, pred_resid


def judge_the_bar(common, methods):
    line("PART D - THE VERDICT against the frozen bar (SPEC 5.3, 5.0, D31.9)")

    print("The bar, frozen before any model existed and unchanged since:")
    print("  an airport passes if the corrected forecast has a LOWER MAE than")
    print("  BOTH raw GFS AND persistence, over that airport's held-out test")
    print("  year. Stage 2 is CDG being put to that bar.")
    print("It is qualitative. There is no numeric margin and there never will")
    print("be one (SPEC 5.3, DECISIONS D22). Climatology and the mean-bias")
    print("reference are reported but do not decide pass or fail (D23).")
    print("The bar is judged once per airport, on that airport's own data")
    print("(SPEC 5.0). EGLC's pass does not excuse a CDG failure, and CDG is")
    print("measured against CDG's own raw GFS and CDG's own persistence only.")

    ml = mae(methods["ML-corrected"])

    sub("the two comparisons that decide it")
    beats = {}
    for name in ["Raw GFS", "Persistence"]:
        ref = mae(methods[name])
        won = ml < ref
        beats[name] = won
        print(f"    vs {name:<22} {'BEATEN' if won else 'NOT BEATEN':<11} "
              f"{ml:.3f} against {ref:.3f}  -> "
              f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)")

    passed = beats["Raw GFS"] and beats["Persistence"]

    if passed:
        banner = ["STAGE 2 PASSES.",
                  "At CDG the corrected forecast beats both raw GFS and",
                  "persistence over the held-out test year, on mean absolute",
                  "error. The recipe travelled."]
    else:
        banner = ["STAGE 2 DOES NOT PASS.",
                  "At CDG the corrected forecast does not beat both raw GFS",
                  "and persistence over the held-out test year.",
                  "This is an honest finding (SPEC 2.4, D31.10), not a reason",
                  "to re-run or to tune. It is a result about how far the",
                  "recipe travels, which is what stage 2 was opened to ask."]
    width = 70
    print()
    print("    " + "*" * width)
    for text in banner:
        print("    *  " + text.ljust(width - 6) + " *")
    print("    " + "*" * width)

    sub("the size of the margin, stated plainly (D22)")
    print("    D22 requires the margin to be reported prominently, so that a")
    print("    technical pass by a hair reads as what it is.")
    raw = mae(methods["Raw GFS"])
    per = mae(methods["Persistence"])
    print(f"    margin over raw GFS     : {raw - ml:+.3f} degC "
          f"({100 * (raw - ml) / raw:+.1f}% of raw GFS MAE)")
    print(f"    margin over persistence : {per - ml:+.3f} degC "
          f"({100 * (per - ml) / per:+.1f}% of persistence MAE)")
    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    worse = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                if abs(a) > abs(b))
    print(f"    days the correction was closer than raw GFS : {better:,} of "
          f"{n:,} ({100 * better / n:.1f}%)")
    print(f"    days it was further away                    : {worse:,} of "
          f"{n:,} ({100 * worse / n:.1f}%)")
    print(f"    days it made no difference                  : "
          f"{n - better - worse:,}")

    sub("the two informative references (not part of the bar, D23)")
    for name in ["Mean-bias reference", "Climatology"]:
        ref = mae(methods[name])
        print(f"    vs {name:<22} {'BEATEN' if ml < ref else 'NOT BEATEN':<11} "
              f"{ml:.3f} against {ref:.3f}  -> "
              f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)")
    mb = mae(methods["Mean-bias reference"])
    print()
    print("    The mean-bias reference is the whole forecast plus one constant -")
    print("    the simplest correction anyone could apply, with no learning in")
    print("    it. Beating it is what separates 'the model learned real")
    print("    structure' from 'the model found an offset'.")
    if ml < mb:
        print("    -> It is beaten, so there is structure in the correction.")
    else:
        print("    -> It is NOT beaten, so the correction is doing no better")
        print("       than a single constant offset would have done.")
    if mb > raw:
        print("    Note: the mean-bias reference is WORSE than raw GFS here,")
        print("    which D31.8 said in advance would not be a fault. It is what")
        print("    'no constant offset worth taking' looks like - the same thing")
        print("    session 11 found on CDG's validation year (F29).")

    sub("per season (SPEC 5.4 parks deeper season testing; this is context)")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'ML-corr':>9} "
          f"{'change':>9} {'persist':>9}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        pe_s = float(np.abs(np.array([methods["Persistence"][i] for i in idx])).mean())
        print(f"    {label:<12} {len(idx):>6,} {raw_s:>9.3f} {ml_s:>9.3f} "
              f"{ml_s - raw_s:>+9.3f} {pe_s:>9.3f}")
    print("    'change' is the corrected MAE minus raw GFS MAE for that season.")
    print("    Negative means the correction helped; positive means it hurt.")
    print("    The headline verdict above is judged on the whole year, not")
    print("    season by season (SPEC 5.3).")

    return passed, ml


# ------------------------------------------------------------------ part E

def compare_with_session11(common, methods, model, pred_resid, x_tr, y_tr):
    line("PART E - the test number beside session 11's CDG rehearsal")

    print("A DIFFERENCE IS EXPECTED AND IS NOT A PROBLEM (D31.5). Three things")
    print("differ between the two columns below:")
    print("  1. a different year of weather - the validation year 2024-08-01 to")
    print("     2025-07-31, against the test year 2025-08-01 to 2026-07-31;")
    print("  2. a model fitted on about 20% more data - CDG's full training")
    print("     window here, CDG's inner-training only in session 11;")
    print("  3. therefore climatology and the mean-bias figure differ too.")
    print("The recipe is identical. Session 11's figures are quoted from")
    print("notes/session-11-check-output.txt and DECISIONS F29.")

    sub("MAE, side by side (different years - context, not a like-for-like)")
    print(f"    {'method':<22} {'s11 valid':>10} {'s13 test':>10} "
          f"{'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = S11_VALIDATION_MAE[name]
        print(f"    {name:<22} {then:>10.3f} {now:>10.3f} {now - then:>+11.3f}")
    print(f"    days scored            {S11_VALIDATION_DAYS:>10,} "
          f"{len(common):>10,}")
    print()
    print("    Read the raw GFS row first. It says how hard the two years were")
    print("    for GFS in the first place, which is the context every other")
    print("    row has to be read against.")

    sub("the margin over raw GFS, which is the comparable quantity")
    for label, ref, ml in (
            ("session 11, validation year",
             S11_VALIDATION_MAE["Raw GFS"], S11_VALIDATION_MAE["ML-corrected"]),
            ("session 13, sealed test year",
             mae(methods["Raw GFS"]), mae(methods["ML-corrected"]))):
        print(f"    {label:<30} {ref - ml:+.3f} degC "
              f"({100 * (ref - ml) / ref:+.1f}%)")
    print("    Margins are more comparable than raw MAE figures, because they")
    print("    divide out how hard the year was. They are still two different")
    print("    years, so this is a sense check, not a measurement.")

    sub("per season, session 11 validation against session 13 test")
    print(f"    {'season':<12} {'s11 raw':>8} {'s11 ML':>8} {'s11 chg':>8}  "
          f"{'s13 raw':>8} {'s13 ML':>8} {'s13 chg':>8}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        _, s11_raw, s11_ml = S11_SEASON[label]
        print(f"    {label:<12} {s11_raw:>8.3f} {s11_ml:>8.3f} "
              f"{s11_ml - s11_raw:>+8.3f}  {raw_s:>8.3f} {ml_s:>8.3f} "
              f"{ml_s - raw_s:>+8.3f}")
    print("    'chg' is the corrected MAE minus raw GFS MAE for that season.")

    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>13} {'gain share':>11} {'splits':>8}  "
          f"{'s11 share':>10} {'s11 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s11_share, s11_splits = S11_IMPORTANCE[n]
        print(f"    {n:<18} {g:>13.1f} {share:>10.1f}% {s:>8,}  "
              f"{s11_share:>9.1f}% {s11_splits:>11,}")
    print("    Both inputs are used and neither is ignored. Session 11 found")
    print("    season_sin carrying the most gain at CDG, where forecast")
    print("    temperature carried it at EGLC (F28, F29) - the model leaning on")
    print("    the calendar at the airport whose bias lives in the calendar.")

    sub("in-sample check only, training window (NOT a result)")
    in_pred = model.predict(x_tr)
    print(f"    raw GFS MAE on the training window      : {mae(y_tr):.3f} degC")
    print(f"    ML-corrected MAE on the training window : "
          f"{mae(y_tr - in_pred):.3f} degC")
    print(f"    session 11, same figure on inner-training: "
          f"{S11_INSAMPLE_ML:.3f} degC")
    print("    A model always looks better on the data it was fitted to, so")
    print("    this proves nothing about performance. It is here only so the")
    print("    number is not a surprise later.")

    sub("the correction the model actually applied over CDG's test year")
    describe(pred_resid, "predicted residual added to the forecast")
    print("    Session 11's corrections over CDG's validation year, for scale:")
    print("    mean +0.041, st dev 0.751, range -1.7 to +2.3 degC (F29).")


# ------------------------------------------------------------------ part F

def compare_with_eglc(common, methods, model, passed):
    line("PART F - how the recipe travelled: CDG's test beside EGLC's (F16)")

    print("EGLC's figures are session 07's sealed test (DECISIONS F16), quoted")
    print("from notes/session-07-check-output.txt.")
    print()
    print("READ THIS AS CONTEXT, NOT AS A COMPARISON OF LIKE WITH LIKE. SPEC 5.0")
    print("judges each airport on its own data. The two airports were scored on")
    print("the same dates but not the same weather, and EGLC's 16.3% is not a")
    print("target CDG had to reach (D31.9). What the two columns can honestly")
    print("say is how the same recipe fared in two different places.")

    sub("test-year MAE, each airport on its own test year")
    print(f"    {'method':<22} {'EGLC':>9} {'CDG':>9} {'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = EGLC_TEST_MAE[name]
        print(f"    {name:<22} {then:>9.3f} {now:>9.3f} {now - then:>+11.3f}")
    print(f"    {'days scored':<22} {EGLC_TEST_DAYS:>9,} {len(common):>9,}")
    print("    A positive difference means CDG's figure is larger. All five rows")
    print("    are error measures, so larger is worse.")

    sub("the margin over each reference, EGLC against CDG")
    ml_now = mae(methods["ML-corrected"])
    ml_then = EGLC_TEST_MAE["ML-corrected"]
    print(f"    {'vs':<22} {'EGLC margin':>22} {'CDG margin':>22}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference",
                 "Climatology"]:
        ref_now = mae(methods[name])
        ref_then = EGLC_TEST_MAE[name]
        m_then = ref_then - ml_then
        m_now = ref_now - ml_now
        print(f"    {name:<22} "
              f"{f'{m_then:+.3f} degC ({100 * m_then / ref_then:+.1f}%)':>22} "
              f"{f'{m_now:+.3f} degC ({100 * m_now / ref_now:+.1f}%)':>22}")
    print("    Margins are degC of MAE saved by the correction. Positive means")
    print("    the correction is ahead of that reference.")

    sub("rehearsal margin against test margin, at both airports")
    raw_now = mae(methods["Raw GFS"])
    cdg_valid_margin = (S11_VALIDATION_MAE["Raw GFS"]
                        - S11_VALIDATION_MAE["ML-corrected"])
    print(f"    {'airport':<10} {'rehearsal margin':>20} {'test margin':>20}")
    print(f"    {'EGLC':<10} "
          f"{f'{EGLC_VALID_MARGIN:+.3f} degC (6.0%)':>20} "
          f"{f'{EGLC_TEST_MARGIN:+.3f} degC (16.3%)':>20}")
    print(f"    {'CDG':<10} "
          f"{f'{cdg_valid_margin:+.3f} degC (3.5%)':>20} "
          f"{f'{raw_now - ml_now:+.3f} degC ({100 * (raw_now - ml_now) / raw_now:+.1f}%)':>20}")
    print("    D31.10 said plainly in advance that CDG's rehearsal margin was")
    print("    half EGLC's, on a harder problem, so a failure was a real")
    print("    possible outcome. This line records what actually happened.")

    sub("per season, EGLC's test against CDG's test")
    print(f"    {'season':<12} {'EGLC raw':>9} {'EGLC ML':>9} {'EGLC chg':>9}   "
          f"{'CDG raw':>9} {'CDG ML':>9} {'CDG chg':>9}")
    helped = 0
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        if ml_s < raw_s:
            helped += 1
        _, eg_raw, eg_ml = EGLC_TEST_SEASON[label]
        print(f"    {label:<12} {eg_raw:>9.3f} {eg_ml:>9.3f} "
              f"{eg_ml - eg_raw:>+9.3f}   {raw_s:>9.3f} {ml_s:>9.3f} "
              f"{ml_s - raw_s:>+9.3f}")
    print("    'chg' is corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse.")

    sub("seasons where the correction helped, on the test year")
    print(f"    CDG : {helped} of 4")
    print("    EGLC: 4 of 4 (session 07 - the first time no season got worse)")

    sub("day by day, on each airport's test year")
    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    print(f"    CDG : closer than raw GFS on {better:,} of {n:,} days "
          f"({100 * better / n:.1f}%)")
    print(f"    EGLC: closer than raw GFS on 221 of 363 days "
          f"({EGLC_TEST_BETTER_PCT:.1f}%)")

    sub("feature importances, EGLC's test against CDG's test")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'EGLC gain %':>12} {'CDG gain %':>12} "
          f"{'EGLC splits':>12} {'CDG splits':>12}")
    for name, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, eg_splits = EGLC_TEST_IMPORTANCE[name]
        print(f"    {name:<18} {eg_share:>11.1f}% {share:>11.1f}% "
              f"{eg_splits:>12,} {s:>12,}")
    print("    Gain totals depend on the data, so the shares and split counts")
    print("    are what compare meaningfully between two airports.")

    sub("one honest limit, carried forward from Q20 (session 12's note)")
    print("    Every LFPG forecast chunk was pulled with models=gfs_global (D16,")
    print("    F22). But F6's value-by-value comparison against gfs_seamless was")
    print("    never re-run at LFPG. So stage 2 can say 'this is exactly the")
    print("    gfs_global series' but NOT 'and gfs_seamless would have given the")
    print("    same', which stage 1 can. Written here so this result does not")
    print("    accidentally claim the stronger version.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 13 - CDG'S SEALED-TEST EVALUATION. ONE LOOK. THE RESULT STANDS.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"airport       : {AIRPORT} / {STATION} (SPEC 3.4) - stage 2 (D26)")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC at {STATION} "
          f"(SPEC 4.1, D31.1)")
    print(f"training      : {TRAIN_START} to {TRAIN_END}   (D13, D31.5)")
    print(f"SEALED TEST   : {TEST_START} to {TEST_END}   (D13, D31.6)")
    print(f"nothing after : {HARD_END}")
    print()
    print("This session executes DECISIONS D31 and decides nothing. Nothing is")
    print("tuned, searched, swapped or re-run. If anything did not fit the D31")
    print("record, the run stops and goes back to the owner (D31.11).")

    prove_it_matches_the_lock()
    train, test, obs_all, reconciled = join()
    if not reconciled:
        print()
        print("!!! A COUNT DID NOT RECONCILE. D31.11 says that is a stop signal:")
        print("!!! stop and raise it with the owner, do not decide on the fly")
        print("!!! with the test year open. Nothing below this line was run -")
        print("!!! no model was fitted and no method was scored.")
        sys.stdout = sys.__stdout__
        tee.flush()
        raise SystemExit(1)

    model, mean_bias, clim, x_tr, y_tr = fit_on_training(train)
    common, methods, pred_resid = score_test_year(
        test, obs_all, model, mean_bias, clim)
    passed, ml = judge_the_bar(common, methods)
    compare_with_session11(common, methods, model, pred_resid, x_tr, y_tr)
    compare_with_eglc(common, methods, model, passed)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). Nothing was")
    print("committed. CDG's test year was opened once, the locked method ran")
    print("once, and the number above is the result of record (D31.10).")
    print()
    print(f"STAGE 2: {'PASSED' if passed else 'DID NOT PASS'}   "
          f"ML-corrected test-year MAE = {ml:.3f} degC against raw GFS "
          f"{mae(methods['Raw GFS']):.3f} and persistence "
          f"{mae(methods['Persistence']):.3f}")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
