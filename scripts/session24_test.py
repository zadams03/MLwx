"""Session 24: DUBBO'S SEALED-TEST EVALUATION. One look, and the result stands.

This script executes the method locked in DECISIONS D39. It decides nothing.
Every choice below was made in session 23, with Dubbo's test year still
unseen.

D39 is D35 with the airport AND the target hour swapped and nothing else
touched, so this script is session 18's sealed test (DSM) with the airport
and the target hour swapped and nothing else touched. PART 0 proves both of
those claims rather than asserting them.

TWO THINGS DIFFER FROM DSM'S TEST, NOT ONE. D35 could say "only DSM's own two
changes against CDG" - this script cannot say "only the location changed"
either: Dubbo changes the location AND the target hour, because 02:00 UTC is
local standard noon at Dubbo, not 18:00 (D37, F50). That cost was accepted on
purpose and in advance, and is written into SPEC 4.1 and D37. A Dubbo result
answers "does the recipe travel to a fourth continent, a flipped hemisphere
and a flipped season cycle"; it must NOT be quoted as the controlled,
location-only comparison EGLC and CDG make between them (F63).

ONE STRUCTURAL DIFFERENCE FROM EVERY EARLIER LOCK, NAMED IN D39.7 AND NOT
SMOOTHED OVER HERE. CDG predicted one lost test day, DSM predicted zero, and
both landed exactly. Dubbo's lock could only predict the PAIRED-ROW count
(356 of 365) with that confidence - the SCORED-day count depends on which
of 9 scattered observation-side losses fall where, relative to persistence's
day-before dependency, and that needs the actual dates. This script names
every date it drops, on both sides, rather than checking a single scored-day
number against a prediction that the lock deliberately did not make.

What it does, in D39's own order:
- D39.5  refits the locked model on Dubbo's FULL training window,
         2021-03-24 to 2025-07-31 (Dubbo's inner-training and Dubbo's
         validation year recombined, 1,193 + 360 = 1,553 rows). Everything
         fitted is fitted on this and nothing else: the model, the
         climatology baseline, the mean-bias figure.
- D39.6  opens Dubbo's test year, 2025-08-01 to 2026-07-31, for the first
         and only time. The two 2026 YSDU raw chunk files are opened here
         for the first time in this project. Nothing after 2026-07-31 is
         used.
- D39.7  pairs with the D14 rule, reports the drop counts on both sides, and
         RECONCILES the paired-row count (not the scored-day count) against
         the prediction D39.7 wrote down before the look. Nothing is filled,
         ever (SPEC 2.2).
- D39.8  scores five methods on the same set of test days.
- D39.9  judges the frozen bar: does the corrected forecast beat BOTH raw
         GFS and persistence on mean absolute error?

Reads only from data/raw/. Never writes to data/raw/.

DUBBO'S SEAL IS NOW OPENED, ON PURPOSE, ONCE. Sessions 19, 20 and 22 kept
Dubbo's test year out: session 19 sampled outside it on purpose (closing
Q29, D39.6), session 20 counted its structure without reading a value,
session 22 cut its load off at 2025-07-31. This session is the single
authorised look (D39.10). Nothing is tuned, searched, swapped or re-run.
Whatever comes out is reported straight - a failure is an honest finding
(SPEC 2.4), not something to fix by trying again.

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

# THE TWO THINGS THAT CHANGE FOR DUBBO (DECISIONS D36, D37, D39.1): the
# location, and the target hour. Nothing else in this file differs from
# DSM's sealed test.
STATION = "YSDU"                      # IEM's own station id, an ICAO code here
AIRPORT = "YSDU"                      # Dubbo, Australia (SPEC 3.4)

TARGET_HOUR = 2                       # 02:00 UTC = local standard noon (D37)

# The full training window (DECISIONS D13, D39.5). This is Dubbo's
# inner-training plus Dubbo's validation year recombined - validation has
# done its job now the method is locked.
TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)

# Dubbo's sealed test year (DECISIONS D13, D39.6). Opened once, here.
TEST_START = date(2025, 8, 1)
TEST_END = date(2026, 7, 31)

# Hard wall. Nothing after the test year is used, which keeps the test set
# exactly one calendar year (DECISIONS D13, D39.6).
HARD_END = TEST_END

# The two sub-periods of the training window used in session 22 (DECISIONS
# D18). Kept here for reporting only - so the training-window row counts can
# be reconciled against the published session 22 counts. Nothing is fitted
# separately on them this session.
INNER_START = date(2021, 3, 24)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# All six chunk files. The two 2026 YSDU files are included for the first
# time - they have never been opened by any session before this one (D39.6).
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),     # test year, second half
]

# The one gap in the forecast series. Found at EGLC (F8), LFPG (F22), DSM
# (F38) and again at Dubbo, hour for hour (F57). For reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Exactly the session 05 settings, unchanged (DECISIONS D39.4,
# which is D35.4, which is D31.4, which is D21.4). Nothing is tuned, searched
# or varied here.
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

# The two scripts this one is checked against. session05_model.py is where
# the locked settings and the shared machinery come from; session18_test.py
# is DSM's sealed test, the same job at the previous airport and the one
# D39 is written as "D35 with the airport and hour swapped" against.
PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"
SIBLING_TEST_SCRIPT = ROOT / "scripts" / "session18_test.py"

# What DECISIONS D39 says this session must run. Written out as data so the
# script can check itself against the lock rather than the reader having to
# trust the prose. Every line below is quoted from D39.
D39_LOCK = {
    "airport (D39.1)":                "YSDU",
    "target hour (D39.1)":            2,
    "train start (D39.5)":            date(2021, 3, 24),
    "train end (D39.5)":              date(2025, 7, 31),
    "test start (D39.6)":             date(2025, 8, 1),
    "test end (D39.6)":               date(2026, 7, 31),
    "features (D39.3)":               ["forecast_temp_c", "season_sin",
                                       "season_cos"],
    "objective (D39.4)":              "regression_l1",
    "n_estimators (D39.4)":           300,
    "learning_rate (D39.4)":          0.05,
    "num_leaves (D39.4)":             15,
    "min_child_samples (D39.4)":      40,
    "subsample (D39.4)":              1.0,
    "colsample_bytree (D39.4)":       1.0,
    "reg_alpha (D39.4)":              0.0,
    "reg_lambda (D39.4)":             0.0,
    "random_state (D39.4)":           42,
    "n_jobs (D39.4)":                 1,
    "deterministic (D39.4)":          True,
    "force_row_wise (D39.4)":         True,
    "verbose (D39.4)":                -1,
    "pairing window minutes (D39.7)": 15,
    "climatology half window (D39.8)": 7.5,
}

# ---- what D39.5 predicted the training refit would hold, BEFORE the look ---
# Written down in session 23 from session 22's join (F60). Reconciled, not
# accepted.
EXPECT_TRAIN_ROWS = 1553              # F60: 1,193 inner-training + 360 valid
EXPECT_INNER_ROWS = 1193              # F60
EXPECT_VALID_ROWS = 360               # F60

# ---- what D39.7 predicted the test year would cost, BEFORE the look --------
# Written down in session 23 from session 20's gap map (F57, F59). These are
# expectations to RECONCILE against, not numbers to accept. A paired-row
# count other than 356 is a D39.11 stop signal. UNLIKE EVERY EARLIER AIRPORT,
# D39.7 explicitly does NOT predict a scored-day count - see the module
# docstring and D39.7 itself. That number is discovered below, not checked.
EXPECT_TEST_FCGAP_DAYS = 0            # F57, F59: no forecast gap in test year
EXPECT_TEST_OFFHOUR_DAYS = 1          # F59: 2025-08-30, off-hour report
EXPECT_TEST_NOREPORT_DAYS = 8         # F59: no report near 02:00 at all
EXPECT_TEST_NOTEMP_DAYS = 0           # F59 names no such cause in the test year
EXPECT_TEST_PAIRED_ROWS = 356         # F59: 365 - 9 observation-side losses

# ---- what session 22 published for Dubbo's training side (F60) -------------
# (EXPECT_TRAIN_ROWS etc. above are the same figures, named per D39.5's own
# wording; repeated here under F60's name so the reconciliation print can
# cite both.)

# Session 22's published Dubbo validation figures, from
# notes/session-22-check-output.txt and DECISIONS F62. Quoted for the
# comparison in PART E. They are a DIFFERENT year and a model fitted on
# about 30% less data, so they are context, not a target (D39.5).
S22_VALIDATION_MAE = {
    "Raw GFS":             1.397,
    "Persistence":         2.577,
    "Climatology":         2.888,
    "Mean-bias reference": 1.368,
    "ML-corrected":        1.283,
}
S22_VALIDATION_DAYS = 355             # common scored days, F62 (5 drop to persist.)
S22_VALID_PAIRED_ROWS = 360           # F60/F59: paired rows before the persist. drop
S22_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 1.344, 1.290),
    "spring MAM": (90, 1.219, 1.241),
    "summer JJA": (90, 1.170, 1.236),
    "autumn SON": (85, 1.884, 1.368),
}
S22_IMPORTANCE = {                    # feature -> (gain share %, splits)
    "forecast_temp_c": (47.8, 1633),
    "season_sin":      (30.2, 1555),
    "season_cos":      (22.0, 1012),
}
S22_INSAMPLE_ML = 0.961               # Dubbo inner-training MAE, session 22
S22_BETTER_PCT = 53.5                 # days closer than raw GFS, session 22
S22_MEAN_BIAS = -0.1360               # mean Dubbo inner-training bias, F62

# EGLC's stage 1 sealed test (F16), CDG's stage 2 sealed test (F30) and DSM's
# stage 2 sealed test (F47), quoted for PART F. Each airport is judged on its
# own data (SPEC 5.0), so these are context and NOT targets Dubbo has to
# reach (D39.9).
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
EGLC_TEST_BETTER_PCT = 60.9           # days closer than raw GFS, session 07
EGLC_TEST_BETTER_N = 221
EGLC_TRAIN_ROWS = 1569
EGLC_VALID_MARGIN = 0.074             # session 05 validation margin, raw GFS
EGLC_TEST_MARGIN = 0.202              # session 07 test margin, raw GFS
EGLC_TEST_MEAN_BIAS = -0.1479
EGLC_SEASONS_HELPED = 4

CDG_TEST_MAE = {
    "Raw GFS":             1.396,
    "Persistence":         2.300,
    "Climatology":         3.774,
    "Mean-bias reference": 1.389,
    "ML-corrected":        1.208,
}
CDG_TEST_DAYS = 363
CDG_TEST_SEASON = {                   # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 1.188, 1.198),
    "spring MAM": (92, 1.239, 1.135),
    "summer JJA": (90, 1.924, 1.397),
    "autumn SON": (91, 1.238, 1.104),
}
CDG_TEST_IMPORTANCE = {               # feature -> (gain share %, splits)
    "forecast_temp_c": (38.2, 1659),
    "season_sin":      (34.9, 1206),
    "season_cos":      (26.9, 1335),
}
CDG_TEST_BETTER_PCT = 58.7            # days closer than raw GFS, session 13
CDG_TEST_BETTER_N = 213
CDG_TRAIN_ROWS = 1569
CDG_VALID_MARGIN = 0.050              # session 11 validation margin, raw GFS
CDG_TEST_MARGIN = 0.188               # session 13 test margin, raw GFS
CDG_TEST_MEAN_BIAS = -0.0600
CDG_SEASONS_HELPED = 3

DSM_TEST_MAE = {
    "Raw GFS":             1.815,
    "Persistence":         4.003,
    "Climatology":         5.030,
    "Mean-bias reference": 1.760,
    "ML-corrected":        1.700,
}
DSM_TEST_DAYS = 365
DSM_TEST_SEASON = {                   # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 1.652, 1.639),
    "spring MAM": (92, 1.964, 2.159),
    "summer JJA": (92, 1.921, 1.590),
    "autumn SON": (91, 1.718, 1.408),
}
DSM_TEST_IMPORTANCE = {               # feature -> (gain share %, splits)
    "forecast_temp_c": (43.4, 1809),
    "season_sin":      (36.1, 1400),
    "season_cos":      (20.6, 991),
}
DSM_TEST_BETTER_PCT = 53.4            # days closer than raw GFS, session 18
DSM_TEST_BETTER_N = 195
DSM_TRAIN_ROWS = 1571
DSM_VALID_MARGIN = 0.282              # session 16 validation margin, raw GFS
DSM_TEST_MARGIN = 0.115               # session 18 test margin, raw GFS
DSM_TEST_MEAN_BIAS = -0.2715
DSM_SEASONS_HELPED = 3

# D39.12's single-season watch-item, measured on Dubbo's VALIDATION year in
# session 22 (F62) and written into the lock BEFORE this look. Quoted in
# PART G so that any inspection after the test is against a table written
# in advance. Northern-calendar labels, for column alignment with the other
# airports; "autumn SON" is Dubbo's own local spring (D37, F61, F62).
F62_SEASON_CHG = {                    # season -> corrected MAE minus raw GFS MAE
    "winter DJF": -0.055,
    "spring MAM": +0.022,
    "summer JJA": +0.066,
    "autumn SON": -0.516,
}
F62_SEASONS_HELPED = 2                # of 4, the fewest of any airport so far
F62_BETTER_PCT = 53.5                 # 190 of 355 days, the lowest of the four

SEASONS = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
           ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]

OUT = ROOT / "notes" / "session-24-check-output.txt"


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

def load_forecast_target_hour():
    """Return {date: forecast_temp_or_None} for 02:00 UTC, up to the hard end.

    Unlike session 22 there is no seal here: Dubbo's test year is loaded,
    because this is the one authorised look at it (DECISIONS D39.6, D39.10).
    The only cut-off is the hard end at 2026-07-31, which keeps the test set
    exactly one calendar year (D13).
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


def load_obs_target_hour():
    """Return {date: observed_temp} for the 02:00 UTC hour, up to the hard end.

    The D14 pairing rule: the routine report belongs to the hour it is
    nearest to, and only if it is within 15 minutes of it. At Dubbo the
    routine report is stamped on the hour (F53), so the 02:00 report is
    itself the observation for 02:00 - an exact match, no offset, the same
    shape as LFPG. Anything more than 15 minutes off is dropped and counted.

    'near_target' separately records every routine report whose nearest
    whole hour is the target hour, with how many minutes it sits from it.
    That is bookkeeping for the drop reconciliation only - it changes no
    pairing, keeps no report the rule drops, and drops none the rule keeps.
    """
    series = {}
    reports_at_target = 0
    reports_after_end = 0
    no_temp = 0
    outside_15min = 0
    near_target = {}                   # date -> [(minute offset, temp or None)]

    for start, end in CHUNKS:
        path = RAW / f"iem_asos_{STATION}_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != TARGET_HOUR:
                    continue
                reports_at_target += 1
                if nearest.date() > HARD_END:
                    reports_after_end += 1
                    continue
                off = int((t - nearest).total_seconds() // 60)
                raw = (r.get("tmpc") or "").strip()
                near_target.setdefault(nearest.date(), []).append(
                    (off, raw if raw not in ("M", "", "T", "None") else None))
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[nearest.date()] = float(raw)

    return (series, reports_at_target, reports_after_end, no_temp,
            outside_15min, near_target)


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
    a number line. Hour of day is not a feature - the hour is fixed at that
    airport's target hour, 02:00 UTC at Dubbo. The encoding is calendar
    position only - it does not know which hemisphere it is in, which is the
    property session 22's flipped-season check (F61) tested.
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


def func_code_shape(src, tree, name):
    """The function's executable code with its docstring and its name removed.

    Two functions with the same shape do the same thing even if their
    comments, their docstrings or their names differ. This is used only to
    say something precise about a function whose source text is NOT
    character-identical: is the difference wording, or is it behaviour?
    """
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            copy = ast.parse(ast.get_source_segment(src, node)).body[0]
            copy.name = "_"
            body = copy.body
            if (body and isinstance(body[0], ast.Expr)
                    and isinstance(body[0].value, ast.Constant)
                    and isinstance(body[0].value.value, str)):
                copy.body = body[1:]
            return ast.dump(copy)
    return None


def prove_it_matches_the_lock():
    """Check this script against DECISIONS D39, and against the two scripts it
    has to agree with.

    Three checks, because they answer three different questions.
    1. Does what this script is about to run match the written lock? Checked
       against D39_LOCK above, value by value.
    2. Is the machinery the same machinery session 05 locked? Checked by
       reading scripts/session05_model.py and comparing it with this file.
    3. Is this the same sealed test session 18 ran at the previous airport?
       Checked by reading scripts/session18_test.py and comparing. Exactly
       one constant should differ - TARGET_HOUR - and that one is D37.
    """
    line("PART 0 - checking this script against the lock (DECISIONS D39)")

    sub("check 1: every value D39 fixes, against what this script will use")
    actual = {
        "airport (D39.1)":                STATION,
        "target hour (D39.1)":            TARGET_HOUR,
        "train start (D39.5)":            TRAIN_START,
        "train end (D39.5)":              TRAIN_END,
        "test start (D39.6)":             TEST_START,
        "test end (D39.6)":               TEST_END,
        "features (D39.3)":               FEATURE_NAMES,
        "objective (D39.4)":              LGB_PARAMS["objective"],
        "n_estimators (D39.4)":           LGB_PARAMS["n_estimators"],
        "learning_rate (D39.4)":          LGB_PARAMS["learning_rate"],
        "num_leaves (D39.4)":             LGB_PARAMS["num_leaves"],
        "min_child_samples (D39.4)":      LGB_PARAMS["min_child_samples"],
        "subsample (D39.4)":              LGB_PARAMS["subsample"],
        "colsample_bytree (D39.4)":       LGB_PARAMS["colsample_bytree"],
        "reg_alpha (D39.4)":              LGB_PARAMS["reg_alpha"],
        "reg_lambda (D39.4)":             LGB_PARAMS["reg_lambda"],
        "random_state (D39.4)":           LGB_PARAMS["random_state"],
        "n_jobs (D39.4)":                 LGB_PARAMS["n_jobs"],
        "deterministic (D39.4)":          LGB_PARAMS["deterministic"],
        "force_row_wise (D39.4)":         LGB_PARAMS["force_row_wise"],
        "verbose (D39.4)":                LGB_PARAMS["verbose"],
        "pairing window minutes (D39.7)": 15,
        "climatology half window (D39.8)": CLIM_HALF_WINDOW_DAYS,
    }
    print(f"    {'what D39 fixes':<34} {'D39 says':<22} {'this run':<22} match?")
    mismatches = 0
    for k, want in D39_LOCK.items():
        got = actual[k]
        ok = got == want
        if not ok:
            mismatches += 1
        print(f"    {k:<34} {str(want):<22} {str(got):<22} "
              f"{'yes' if ok else 'NO - MISMATCH'}")
    print(f"    values checked: {len(D39_LOCK)}")
    print(f"    values that do not match D39: {mismatches}")
    assert mismatches == 0, "this script does not match the D39 lock - STOP"
    print("    (The 15-minute pairing window is the literal in")
    print("     load_obs_target_hour below. Check 3d prints that function's")
    print("     differences from session 18's, so it can be seen that the")
    print("     15 minutes is untouched.)")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    s18_src = SIBLING_TEST_SCRIPT.read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)
    s18 = ast.parse(s18_src)

    sub("check 2a: model settings, session 05 against this session")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 24':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}   (D39.4 requires 0)")
    assert n_diff == 0, "the model settings drifted from session 05 - STOP"

    sub("check 2b: the code that must be character-identical to session 05")
    print("    Compared character for character with scripts/session05_model.py.")
    identical = True
    for name in ["all_days", "year_fraction", "mae", "describe"]:
        a = func_source(old_src, old, name)
        b = func_source(new_src, new, name)
        if a != b:
            identical = False
        print(f"    {name + '()':<26} "
              f"{'identical' if a == b else 'DIFFERS - NOT EXPECTED'}")
    assert identical, "shared code drifted from session 05 - STOP (D39.11)"
    print("    features() is handled separately below: its text differs from")
    print("    session 05's by docstring lines naming the fixed hour and the")
    print("    flipped-season check, and its executable code is compared with")
    print("    docstrings stripped out.")

    sub("check 3a: model settings, session 18 (DSM test) against this session")
    s18_p = top_level(s18, "LGB_PARAMS")
    keys = list(s18_p) + [k for k in new_p if k not in s18_p]
    n_diff = 0
    for k in keys:
        if s18_p.get(k, "<absent>") != new_p.get(k, "<absent>"):
            n_diff += 1
    print(f"    settings compared: {len(keys)}")
    print(f"    settings that differ from DSM's sealed test: {n_diff}")
    assert n_diff == 0, "settings differ from session 18 - STOP (D39.11)"

    sub("check 3b: the constants, session 18 (DSM) against session 24 (Dubbo)")
    print("    Exactly one constant should differ: TARGET_HOUR, 18 -> 2, which")
    print("    is D37 and nothing else. The split dates are shared by every")
    print("    airport (SPEC 4.3), so they must be identical.")
    print(f"    {'constant':<24} {'session 18 (DSM)':<34} "
          f"{'session 24 (Dubbo)':<20} same?")
    differing = []
    for c in ["TARGET_HOUR", "TRAIN_START", "TRAIN_END", "TEST_START",
              "TEST_END", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]:
        a = top_level(s18, c)
        b = top_level(new, c)
        if a != b:
            differing.append(c)
        print(f"    {c:<24} {str(a)[:33]:<34} "
              f"{(str(b)[:19] if a != b else ''):<20} "
              f"{'yes' if a == b else 'NO - DIFFERS'}")
    print(f"    constants that differ: {len(differing)}  {differing}")
    assert differing == ["TARGET_HOUR"], \
        "something other than the target hour differs from session 18 - STOP"

    sub("check 3c: session 24 against session 18, function by function")
    print("    This is the 'the airport and the hour changed, and nothing")
    print("    else' claim, checked in code rather than argued. Every")
    print("    function is compared character for character with DSM's")
    print("    sealed test script.")
    for name in ["all_days", "year_fraction", "mae", "describe",
                 "_literal", "top_level", "func_source",
                 "climatology_from_training", "fit_on_training"]:
        a = func_source(s18_src, s18, name)
        b = func_source(new_src, new, name)
        print(f"    {name + '()':<28} "
              f"{'identical' if a == b else 'differs - shown below'}")
    print("    The remaining functions (join, score_test_year, judge_the_bar,")
    print("    the comparison parts and main) differ in the text they print,")
    print("    which is on the screen anyway, and in which published figures")
    print("    they quote. No arithmetic differs; the diffs below cover every")
    print("    function that does any of the loading, fitting or scoring.")

    sub("check 3d: the functions that DO differ, each shown in full")
    print("    Nothing is hidden: every diff is printed so the changes can be")
    print("    read rather than taken on trust.")
    pairs = [
        ("features", "features",
         "docstring lines: the sentence naming the fixed hour says 02:00 UTC\n"
         "    at Dubbo instead of 18:00 (D37), plus a line naming the\n"
         "    flipped-season check (F61) that DSM's docstring has no reason\n"
         "    to mention. No executable line differs - proved below with\n"
         "    docstrings stripped out."),
        ("load_forecast_target_hour", "load_forecast_target_hour",
         "the docstring's session number and airport name. The file-name\n"
         "    template already uses the STATION variable, so the executable\n"
         "    code is unchanged."),
        ("load_obs_target_hour", "load_obs_target_hour",
         "the docstring: Dubbo reports ON the hour (:00, the same shape as\n"
         "    LFPG), where DSM reports at :54. The D14 rule, the 15-minute\n"
         "    tolerance and the near-target bookkeeping are all unchanged -\n"
         "    proved below with docstrings stripped out."),
        ("fit_on_training", "fit_on_training",
         "printed labels only - D35 references become D39 references and\n"
         "    the airport is named. Every fitted quantity is computed by the\n"
         "    same lines."),
    ]
    for old_name, new_name, why in pairs:
        print()
        print(f"    {new_name}() - {why}")
        a = func_source(s18_src, s18, old_name)
        b = func_source(new_src, new, new_name)
        if a == b:
            print("      (identical after all - no diff to show)")
            continue
        for d in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                      f"session18 {old_name}",
                                      f"session24 {new_name}",
                                      lineterm="", n=1):
            print(f"      {d}")

    sub("check 3e: executable code with docstrings removed")
    print("    A function whose text differs may still do exactly the same")
    print("    thing. This strips the docstring and the name and compares")
    print("    what is left, against session 18's.")
    for name in ["all_days", "year_fraction", "features", "mae", "describe",
                 "climatology_from_training", "load_forecast_target_hour",
                 "load_obs_target_hour"]:
        a = func_code_shape(s18_src, s18, name)
        b = func_code_shape(new_src, new, name)
        print(f"    {name + '()':<28} "
              f"{'IDENTICAL' if a == b else 'different - see the diff above'}")
    print("    Every loader is expected IDENTICAL here: the pairing itself -")
    print("    nearest report, 15-minute tolerance, drop and count - and the")
    print("    file-name template are unchanged; only the docstrings differ.")


# ------------------------------------------------------------------ part A

def join():
    line(f"PART A - the join at {TARGET_HOUR:02d}:00 UTC, both windows "
         f"(D39.6, D39.7)")

    print(f"airport     : {AIRPORT} - Dubbo, Australia (SPEC 3.4, D39.1)")
    print(f"target hour : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1, D37, D39.1) -")
    print("              local standard noon at Dubbo, NOT 12:00 or 18:00")
    print("              UTC. Daylight saving is deliberately ignored, so the")
    print("              clock reads 12:00 AEST in winter and 13:00 AEDT in")
    print("              summer either way (D37).")
    print("pairing rule: the routine report nearest the hour, and only if")
    print("              within 15 minutes of it (DECISIONS D14, D39.7). At")
    print("              Dubbo the routine report is stamped on the hour")
    print("              (F53), so 02:00 UTC is served by the 02:00 report -")
    print("              an exact match, no offset, the same shape as LFPG.")
    print()
    print("DUBBO'S TEST YEAR IS OPENED HERE, for the first and only time")
    print("(D39.10). The two 2026 YSDU raw chunk files are read for the")
    print("first time in this project. Sessions 19, 20 and 22 never opened")
    print("them.")

    fc, fc_rows, fc_after = load_forecast_target_hour()
    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_target = \
        load_obs_target_hour()

    sub("what was loaded")
    print(f"    forecast chunk files opened : {len(CHUNKS)} "
          f"(all six, including both 2026 files)")
    print(f"    forecast {TARGET_HOUR}:00 rows seen    : {fc_rows:,}")
    print(f"    of those, after {HARD_END} : {fc_after:,} (not used, D13)")
    print(f"    forecast {TARGET_HOUR}:00 rows kept    : {len(fc):,}")
    print(f"    observation {TARGET_HOUR}:00 reports seen  : {ob_rows:,}")
    print(f"    of those, after {HARD_END}: {ob_after:,} (not used, D13)")
    print(f"    observation {TARGET_HOUR}:00 reports kept  : {len(obs):,}")

    sub("observation reports rejected by the rules")
    print(f"    reports more than 15 min from the hour, dropped (D14): {ob_far:,}")
    print(f"    reports carrying no temperature (M), dropped (2.2)   : {ob_no_temp:,}")

    # The hard end wall, proved rather than asserted in prose.
    assert max(fc) <= HARD_END, "a forecast date after the hard end got through"
    assert max(obs) <= HARD_END, "an observation date after the hard end got through"

    sub("the pairing offset actually used, every kept day")
    offsets = {}
    test_offsets = {}
    for d, recs in near_target.items():
        if d not in obs:
            continue
        best = min((r for r in recs if abs(r[0]) <= 15 and r[1] is not None),
                   key=lambda r: abs(r[0]))
        offsets[best[0]] = offsets.get(best[0], 0) + 1
        if TEST_START <= d <= TEST_END:
            test_offsets[best[0]] = test_offsets.get(best[0], 0) + 1
    print(f"    {'offset from ' + f'{TARGET_HOUR:02d}:00 UTC':<28} "
          f"{'all loaded days':>16} {'of which test year':>19}")
    for off in sorted(offsets):
        print(f"    {off:+d} minutes{'':<18} {offsets[off]:>16,} "
              f"{test_offsets.get(off, 0):>19,}")
    print("    F53 and F60 predicted 0 minutes on every kept day. So the")
    print("    pairing at Dubbo is never a matter of choosing the nearer of")
    print("    two reports - the target-hour report either exists or it")
    print("    does not.")
    ambiguous = sum(1 for recs in near_target.values()
                    if len([r for r in recs
                            if abs(r[0]) <= 15 and r[1] is not None]) > 1)
    print(f"    days with MORE THAN ONE report inside D14's 15-minute window: "
          f"{ambiguous:,}")
    print("    So the pairing is essentially never ambiguous at Dubbo either.")

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
    print(f"             'no fc'   = the forecast series had no row for "
          f"{TARGET_HOUR}:00;")
    print("             'null fc' = it had a row but the value was null;")
    print("             'no obs'  = no usable observation within 15 min.")
    print("             A day can fail on more than one reason, so the reason")
    print("             columns can add up to more than 'drop'.")
    print("    Nothing was filled in (SPEC 2.2, D39.7).")

    train, test = built["train"], built["test"]
    inner, valid = built["inner"], built["valid"]

    sub("reconciliation 1: does the training window add up? (D39.5, D39.11)")
    print("    The training window is Dubbo's inner-training plus Dubbo's")
    print("    validation year, which session 22 counted separately. Those")
    print("    published counts must add up to this session's training")
    print("    count, or something has drifted and this session must stop.")
    print(f"    session 22 inner-training kept rows (F60): {EXPECT_INNER_ROWS:,}")
    print(f"    session 22 validation kept rows (F60)    :   {EXPECT_VALID_ROWS:,}")
    print(f"    published total                          : {EXPECT_TRAIN_ROWS:,}")
    print(f"    this session, training window kept rows  : {len(train):,}")
    print(f"    this session, of which dated <= {INNER_END} : {len(inner):,}")
    print(f"    this session, of which dated >= {VALID_START} : {len(valid):,}")
    ok_train = (len(train) == EXPECT_TRAIN_ROWS
                and len(inner) == EXPECT_INNER_ROWS
                and len(valid) == EXPECT_VALID_ROWS)
    print(f"    reconciles: {'YES' if ok_train else 'NO - STOP AND RAISE (D39.11)'}")
    print(f"    (1,553, not 1,571 like DSM or 1,569 like the two European")
    print(f"     airports: Dubbo loses 21 gap days instead of 20 - its")
    print(f"     02:00 target falls before the gap's last missing hour,")
    print(f"     11:00 UTC - plus 17 real observation-side losses, the first")
    print(f"     time any airport's training refit loses meaningful rows to")
    print(f"     something other than the shared gap. D39.5, F59, F60.)")

    sub("the F57/F59 forecast gap, for the record")
    gap_days = all_days(GAP_START, GAP_END)
    kept_dates = {r["date"] for r in train}
    print(f"    gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END}), all inside training")
    print(f"    of those, dropped here: "
          f"{sum(1 for d in gap_days if d not in kept_dates)}")
    print(f"    (21, one more than EGLC/LFPG/DSM's 20: Dubbo's 02:00 target")
    print(f"     falls BEFORE the gap's last missing hour, 2024-01-19 11:00")
    print(f"     UTC, so that date is still inside the gap at 02:00 - F59.)")

    # ------------------------------------------------- the test-year drop count
    sub("THE TEST-YEAR DROP COUNT (D39.7) - every date named, both causes")
    t_days = all_days(TEST_START, TEST_END)
    t_kept = {r["date"] for r in test}
    t_dropped = [d for d in t_days if d not in t_kept]
    print(f"    test-year calendar days : {len(t_days):,}")
    print(f"    paired rows kept        : {len(test):,}")
    print(f"    days dropped            : {len(t_dropped):,}")
    print("    UNLIKE EVERY EARLIER AIRPORT, D39.7 predicted this would NOT")
    print("    be zero - Dubbo's own gap map (F59) found 9 observation-side")
    print("    losses inside the test year, with the individual 'no report'")
    print("    dates deliberately left unnamed until this session opened the")
    print("    test year (D39.7). They are named below, for the first time")
    print("    anywhere in this project.")

    # Sort each dropped day into exactly one of the four causes F59 counted,
    # which is what D39.7's prediction was built from. "Near the target hour"
    # means the report's nearest whole hour is 02:00, which is the framing
    # session 20 used.
    cause_fcgap = []          # forecast row missing or null
    cause_offhour = []        # a report near the hour exists but is >15 min out
    cause_noreport = []       # nothing filed near the target hour at all
    cause_notemp = []         # a report within 15 min but carrying no temp
    for d in t_dropped:
        no_fc = (d not in fc) or (fc[d] is None)
        reports = sorted(near_target.get(d, []), key=lambda x: x[0])
        within15 = [x for x in reports if abs(x[0]) <= 15]
        if no_fc:
            cause_fcgap.append(d)
        elif within15:
            cause_notemp.append(d)
        elif reports:
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
                verdict = f"would pair with {TARGET_HOUR}:00 under D14"
            else:
                verdict = "nearest the target hour but >15 min out - dropped"
            print(f"          routine report at {TARGET_HOUR}:00{off:+d} min, "
                  f"temp {temp if temp is not None else 'M'}  -> {verdict}")
        if not reports:
            print(f"          no routine report near the {TARGET_HOUR}:00 hour "
                  f"at all")
    print("    Every drop is named. Nothing was filled (SPEC 2.2).")

    sub("reconciliation 2: THE PAIRED-ROW COUNT AGAINST D39.7's ADVANCE "
        "PREDICTION")
    print("    D39.7 wrote these numbers down in session 23, from session 20's")
    print("    gap map, BEFORE Dubbo's test year was opened. A prediction made")
    print("    before the look is a stronger check than a count made after it.")
    print("    A PAIRED-ROW count that will not reconcile is a D39.11 stop")
    print("    signal. D39.7 explicitly did NOT predict a scored-day count -")
    print("    that is reported separately below, not checked here.")
    print()
    print(f"    {'cause':<52} {'predicted':>9} {'actual':>7}  verdict")
    checks = [
        ("forecast-gap days in the test year (F57, F59)",
         EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)),
        ("days lost to an off-hour-only report (F59)",
         EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)),
        ("days lost to no report near the 02:00 hour (F59)",
         EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)),
        ("days lost to a report in place with no temperature",
         EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)),
        ("paired rows expected (F59)", EXPECT_TEST_PAIRED_ROWS, len(test)),
    ]
    ok_test = True
    for label, want, got in checks:
        good = want == got
        ok_test = ok_test and good
        print(f"    {label:<52} {want:>9} {got:>7}  "
              f"{'MATCHES' if good else 'SURPRISE'}")

    sub("shape check: first and last kept row of each window")
    for label, rows in (("training", train), ("test year", test)):
        print(f"    {label:<10} {rows[0]['date']} -> {rows[-1]['date']}   "
              f"{len(rows):,} rows")

    return train, test, obs, (ok_train and ok_test)


# ------------------------------------------------------------------ part B

def climatology_from_training(train):
    """Day-of-year seasonal average of the OBSERVED temperature.

    Built from training-window days only (SPEC 2.1c, D21.8). For a given
    position in the year it averages every training-window observation
    within +/- 7.5 days of that position, measured around the circle so
    that late December and early January are neighbours. The window
    smooths what would otherwise be four or five noisy days per date.
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

    Three things are fitted here: the model, the climatology baseline and
    the mean-bias figure. All three see only Dubbo 2021-03-24 to
    2025-07-31 (D39.5, D39.8, SPEC 2.1c).
    """
    line("PART B - fit on Dubbo's FULL training window only (D39.5, D39.8)")

    print("Everything fitted in this session is fitted here, on Dubbo's")
    print("training window, and on nothing else: the model, the climatology")
    print("baseline and the mean-bias figure. The test year plays no part in")
    print("any fit.")

    x_tr = features(train)
    y_tr = np.array([r["resid"] for r in train], dtype=float)

    sub("the model")
    print(f"    rows fitted on : {len(x_tr):,}  "
          f"({train[0]['date']} to {train[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (D19, D39.3)")
    print("    target         : residual, observed minus forecast (SPEC 4.2,")
    print("                     D39.2). The model never predicts temperature.")
    print("    settings (locked in D39.4, nothing tuned this session):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_tr, y_tr)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    sub("the mean-bias figure (D39.8)")
    mean_bias = float(np.mean(y_tr))
    print(f"    mean training-window bias (observed - forecast): "
          f"{mean_bias:+.4f} degC")
    print(f"    over {len(y_tr):,} training days. The mean-bias reference is")
    print("    the raw forecast plus this one constant, and nothing else.")
    print(f"    raw GFS MAE on the training window (in sample): "
          f"{mae(y_tr):.3f} degC")
    print(f"    session 22's inner-training figure was {S22_MEAN_BIAS:+.4f} degC")
    print(f"    (F62). EGLC's constant was {EGLC_TEST_MEAN_BIAS:+.4f} (F16),")
    print(f"    CDG's {CDG_TEST_MEAN_BIAS:+.4f} (F30) and DSM's "
          f"{DSM_TEST_MEAN_BIAS:+.4f} (F47).")

    sub("the climatology baseline (D39.8, SPEC 2.1c)")
    print("    seasonal average of the OBSERVED temperature at Dubbo, from")
    print(f"    training-window days only, +/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print("    measured around the circle so late December and early January")
    print("    are neighbours.")
    clim = climatology_from_training(train)

    return model, mean_bias, clim, x_tr, y_tr


# ------------------------------------------------------------------ part C

def score_test_year(test, obs_all, model, mean_bias, clim):
    line("PART C - THE SEALED TEST AT DUBBO (D39.6, D39.8, D39.9)")

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
    print(f"    dropped: no previous-day {TARGET_HOUR}:00 observation "
          f"   : {len(no_prev):,}"
          + (f"  ({', '.join(str(d) for d in no_prev)})" if no_prev else ""))
    print(f"    days every method is scored on                : {len(common):,}")
    print("    D39.7 did NOT predict this number in advance - unlike every")
    print("    earlier airport, it could only be pinned once the test year's")
    print("    actual dates were known (module docstring, D39.7). The dates")
    print("    above, if any, are how far below the 356 paired rows it fell,")
    print("    and each is a day whose PREVIOUS calendar day was itself one")
    print("    of the observation-side losses named in PART A.")
    print(f"    date range                                    : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print(f"    Persistence needs yesterday's {TARGET_HOUR}:00 observation, a")
    print("    past-only value (SPEC 2.1d). For the first test day,")
    print("    2025-08-01, 'yesterday' is 2025-07-31, which sits in the")
    print("    training window and is not one of F60's named observation-")
    print("    side losses. That is a past observation, so it is legal and")
    print("    it is used - written down in D39.8 in advance so it is not")
    print("    mistaken for leakage. Nothing was filled in (SPEC 2.2).")
    first = common[0]
    prev_obs = obs_all.get(first["date"] - timedelta(days=1))
    print(f"    check: the first scored day is {first['date']}, and its")
    print(f"           persistence value is {first['persist']:+.1f} degC, "
          f"which is the")
    print(f"           {first['date'] - timedelta(days=1)} {TARGET_HOUR}:00 "
          f"observation ({prev_obs:+.1f} degC).")

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

    sub(f"DUBBO TEST-YEAR MAE, {len(common):,} common days "
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
    line("PART D - THE VERDICT against the frozen bar (SPEC 5.3, 5.0, D39.9)")

    print("The bar, frozen before any model existed and unchanged since:")
    print("  an airport passes if the corrected forecast has a LOWER MAE than")
    print("  BOTH raw GFS AND persistence, over that airport's held-out test")
    print("  year. Stage 2 is each further individual airport put to that bar,")
    print("  one at a time; Dubbo is the airport in it now.")
    print("It is qualitative. There is no numeric margin and there never will")
    print("be one (SPEC 5.3, DECISIONS D22). Climatology and the mean-bias")
    print("reference are reported but do not decide pass or fail (D23).")
    print("The bar is judged once per airport, on that airport's own data")
    print("(SPEC 5.0). EGLC's, CDG's and DSM's passes do not excuse a Dubbo")
    print("failure, and Dubbo is measured against Dubbo's own raw GFS and")
    print("Dubbo's own persistence only. Stage 1's 16.3% and stage 2's")
    print("13.5%/6.3% are not targets (D39.9).")

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
        banner = ["DUBBO PASSES.",
                  "At Dubbo the corrected forecast beats both raw GFS and",
                  "persistence over the held-out test year, on mean absolute",
                  "error. The recipe travelled to a fourth continent, a",
                  "flipped hemisphere and a flipped season cycle, at a",
                  "third distinct target hour."]
    else:
        banner = ["DUBBO DOES NOT PASS.",
                  "At Dubbo the corrected forecast does not beat both raw",
                  "GFS and persistence over the held-out test year.",
                  "This is an honest finding (SPEC 2.4, D39.10), not a reason",
                  "to re-run or to tune. It is a result about how far the",
                  "recipe travels, and D39.12's single-season watch-item is",
                  "the first place to look for why - as description only."]
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
    print()
    print("    D39.8 said in advance which half of the bar binds at Dubbo:")
    print("    persistence is far weaker than raw GFS there (2.577 against")
    print("    1.397 on the validation year, F62), so THE RAW-GFS MARGIN IS")
    print("    THE ONE THAT DECIDES THE VERDICT IN PRACTICE. Both halves are")
    print("    still required by the bar.")
    print(f"    raw GFS MAE       : {raw:.3f} degC")
    print(f"    persistence MAE   : {per:.3f} degC  "
          f"({per / raw:.2f}x raw GFS)")
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
    if mb < raw:
        print("    Note: the mean-bias reference is BETTER than raw GFS here,")
        print("    as D39.8 said it was on Dubbo's validation year (F62,")
        print("    -0.136 on inner-training). So a small constant is worth")
        print("    taking at Dubbo, as at EGLC and DSM and unlike CDG - which")
        print("    makes the margin over this reference the sharper test of")
        print("    whether the model found structure.")
    else:
        print("    Note: the mean-bias reference is WORSE than raw GFS here,")
        print("    which is what 'no constant offset worth taking' looks like.")

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
    print("    Season labels are Northern-calendar, for column alignment with")
    print("    the other airports; 'autumn SON' is Dubbo's own local spring")
    print("    (D37, F61) - the season D39.12's watch-item names (PART G).")
    print("    The headline verdict above is judged on the whole year, not")
    print("    season by season (SPEC 5.3).")

    return passed, ml


# ------------------------------------------------------------------ part E

def compare_with_session22(common, methods, model, pred_resid, x_tr, y_tr):
    line("PART E - the test number beside session 22's Dubbo rehearsal")

    print("A DIFFERENCE IS EXPECTED AND IS NOT A PROBLEM (D39.5). Three things")
    print("differ between the two columns below:")
    print("  1. a different year of weather - the validation year 2024-08-01 to")
    print("     2025-07-31, against the test year 2025-08-01 to 2026-07-31;")
    print("  2. a model fitted on about 30% more data - Dubbo's full training")
    print("     window here (1,553 rows), Dubbo's inner-training only in")
    print("     session 22 (1,193 rows);")
    print("  3. therefore climatology and the mean-bias figure differ too.")
    print("The recipe is identical. Session 22's figures are quoted from")
    print("notes/session-22-check-output.txt and DECISIONS F62.")

    sub("MAE, side by side (different years - context, not a like-for-like)")
    print(f"    {'method':<22} {'s22 valid':>10} {'s24 test':>10} "
          f"{'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = S22_VALIDATION_MAE[name]
        print(f"    {name:<22} {then:>10.3f} {now:>10.3f} {now - then:>+11.3f}")
    print(f"    days scored            {S22_VALIDATION_DAYS:>10,} "
          f"{len(common):>10,}")
    print()
    print("    Read the raw GFS row first. It says how hard the two years were")
    print("    for GFS in the first place, which is the context every other")
    print("    row has to be read against.")

    sub("the margin over raw GFS, which is the comparable quantity")
    for label, ref, ml in (
            ("session 22, validation year",
             S22_VALIDATION_MAE["Raw GFS"], S22_VALIDATION_MAE["ML-corrected"]),
            ("session 24, sealed test year",
             mae(methods["Raw GFS"]), mae(methods["ML-corrected"]))):
        print(f"    {label:<30} {ref - ml:+.3f} degC "
              f"({100 * (ref - ml) / ref:+.1f}%)")
    print("    Margins are more comparable than raw MAE figures, because they")
    print("    divide out how hard the year was. They are still two different")
    print("    years, so this is a sense check, not a measurement.")

    sub("per season, session 22 validation against session 24 test")
    print(f"    {'season':<12} {'s22 raw':>8} {'s22 ML':>8} {'s22 chg':>8}  "
          f"{'s24 raw':>8} {'s24 ML':>8} {'s24 chg':>8}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        _, s22_raw, s22_ml = S22_SEASON[label]
        print(f"    {label:<12} {s22_raw:>8.3f} {s22_ml:>8.3f} "
              f"{s22_ml - s22_raw:>+8.3f}  {raw_s:>8.3f} {ml_s:>8.3f} "
              f"{ml_s - raw_s:>+8.3f}")
    print("    'chg' is the corrected MAE minus raw GFS MAE for that season.")
    print("    F62 found Dubbo's win concentrated almost entirely in 'autumn")
    print("    SON' (Dubbo's own local spring) on the rehearsal. This line")
    print("    says what the test year did in the same season.")

    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>13} {'gain share':>11} {'splits':>8}  "
          f"{'s22 share':>10} {'s22 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s22_share, s22_splits = S22_IMPORTANCE[n]
        print(f"    {n:<18} {g:>13.1f} {share:>10.1f}% {s:>8,}  "
              f"{s22_share:>9.1f}% {s22_splits:>11,}")
    print("    Both inputs are used and neither is ignored. Session 22 found")
    print("    forecast temperature carrying the largest share of any airport")
    print("    yet, with season_sin second (F62).")

    sub("in-sample check only, training window (NOT a result)")
    in_pred = model.predict(x_tr)
    print(f"    raw GFS MAE on the training window      : {mae(y_tr):.3f} degC")
    print(f"    ML-corrected MAE on the training window : "
          f"{mae(y_tr - in_pred):.3f} degC")
    print(f"    session 22, same figure on inner-training: "
          f"{S22_INSAMPLE_ML:.3f} degC")
    print("    A model always looks better on the data it was fitted to, so")
    print("    this proves nothing about performance. It is here only so the")
    print("    number is not a surprise later.")

    sub("the correction the model actually applied over Dubbo's test year")
    describe(pred_resid, "predicted residual added to the forecast")
    print("    Session 22's corrections over Dubbo's validation year, for")
    print("    scale, are in notes/session-22-check-output.txt.")


# ------------------------------------------------------------------ part F

def compare_with_prior_airports(common, methods, model):
    line("PART F - how the recipe travelled: Dubbo beside EGLC (F16), "
         "CDG (F30) and DSM (F47)")

    print("EGLC's figures are session 07's sealed test (F16), CDG's are")
    print("session 13's (F30) and DSM's are session 18's (F47), quoted from")
    print("their notes files.")
    print()
    print("READ THIS AS CONTEXT, NOT AS A COMPARISON OF LIKE WITH LIKE. SPEC")
    print("5.0 judges each airport on its own data. Three cautions, all")
    print("written down before this look:")
    print("  1. Dubbo changes the LOCATION AND THE TARGET HOUR against every")
    print("     earlier airport (D37, SPEC 4.1, F63) - the same honest caveat")
    print("     D33 attaches to DSM, now doubled: this is the first airport")
    print("     compared against two prior locations that were EACH already")
    print("     not the controlled EGLC/CDG comparison.")
    print("  2. All four airports were tested on THE SAME TWELVE MONTHS,")
    print("     because D13's split dates are shared. Dubbo answers the")
    print("     hemisphere/season-cycle axis (F63) and not the year axis.")
    print("  3. EGLC's 16.3%, CDG's 13.5% and DSM's 6.3% are not targets")
    print("     Dubbo had to reach (D39.9).")

    sub("test-year MAE, each airport on its own test year")
    print(f"    {'method':<22} {'EGLC':>9} {'CDG':>9} {'DSM':>9} {'Dubbo':>9}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        print(f"    {name:<22} {EGLC_TEST_MAE[name]:>9.3f} "
              f"{CDG_TEST_MAE[name]:>9.3f} {DSM_TEST_MAE[name]:>9.3f} "
              f"{mae(methods[name]):>9.3f}")
    print(f"    {'days scored':<22} {EGLC_TEST_DAYS:>9,} {CDG_TEST_DAYS:>9,} "
          f"{DSM_TEST_DAYS:>9,} {len(common):>9,}")
    print(f"    {'training rows fitted':<22} {EGLC_TRAIN_ROWS:>9,} "
          f"{CDG_TRAIN_ROWS:>9,} {DSM_TRAIN_ROWS:>9,} {EXPECT_TRAIN_ROWS:>9,}")
    print("    All five rows are error measures, so larger is worse.")

    sub("the margin over each reference, all four airports")
    ml_now = mae(methods["ML-corrected"])
    print(f"    {'vs':<22} {'EGLC':>18} {'CDG':>18} {'DSM':>18} {'Dubbo':>18}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference",
                 "Climatology"]:
        m_e = EGLC_TEST_MAE[name] - EGLC_TEST_MAE["ML-corrected"]
        m_c = CDG_TEST_MAE[name] - CDG_TEST_MAE["ML-corrected"]
        m_d = DSM_TEST_MAE[name] - DSM_TEST_MAE["ML-corrected"]
        ref_now = mae(methods[name])
        m_y = ref_now - ml_now
        print(f"    {name:<22} "
              f"{f'{m_e:+.3f} ({100 * m_e / EGLC_TEST_MAE[name]:+.1f}%)':>18} "
              f"{f'{m_c:+.3f} ({100 * m_c / CDG_TEST_MAE[name]:+.1f}%)':>18} "
              f"{f'{m_d:+.3f} ({100 * m_d / DSM_TEST_MAE[name]:+.1f}%)':>18} "
              f"{f'{m_y:+.3f} ({100 * m_y / ref_now:+.1f}%)':>18}")
    print("    Margins are degC of MAE saved by the correction. Positive means")
    print("    the correction is ahead of that reference. The PERCENTAGE is")
    print("    the comparable figure across airports, because it divides out")
    print("    how hard each airport's problem is.")

    sub("rehearsal margin against test margin, at all four airports")
    raw_now = mae(methods["Raw GFS"])
    dubbo_test_margin = raw_now - ml_now
    dubbo_valid_margin = (S22_VALIDATION_MAE["Raw GFS"]
                          - S22_VALIDATION_MAE["ML-corrected"])
    print(f"    {'airport':<10} {'rehearsal margin':>24} {'test margin':>24}")
    print(f"    {'EGLC':<10} "
          f"{f'{EGLC_VALID_MARGIN:+.3f} degC (6.0%)':>24} "
          f"{f'{EGLC_TEST_MARGIN:+.3f} degC (16.3%)':>24}")
    print(f"    {'CDG':<10} "
          f"{f'{CDG_VALID_MARGIN:+.3f} degC (3.5%)':>24} "
          f"{f'{CDG_TEST_MARGIN:+.3f} degC (13.5%)':>24}")
    print(f"    {'DSM':<10} "
          f"{f'{DSM_VALID_MARGIN:+.3f} degC (16.1%)':>24} "
          f"{f'{DSM_TEST_MARGIN:+.3f} degC (6.3%)':>24}")
    dubbo_test_pct = 100 * dubbo_test_margin / raw_now
    dubbo_test_str = f"{dubbo_test_margin:+.3f} degC ({dubbo_test_pct:+.1f}%)"
    print(f"    {'Dubbo':<10} "
          f"{f'{dubbo_valid_margin:+.3f} degC (8.2%)':>24} "
          f"{dubbo_test_str:>24}")
    print("    D39.10 named Dubbo's rehearsal margin (8.2%) as sitting")
    print("    between CDG's and DSM's, and said explicitly that this was NOT")
    print("    a reason to expect a pass either way. This line records what")
    print("    actually happened.")

    sub("per season, all four sealed tests")
    print(f"    {'season':<12} {'EGLC chg':>9} {'CDG chg':>9} {'DSM chg':>9} "
          f"{'Dubbo raw':>10} {'Dubbo ML':>9} {'Dubbo chg':>10}")
    helped = 0
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        if ml_s < raw_s:
            helped += 1
        _, eg_raw, eg_ml = EGLC_TEST_SEASON[label]
        _, cd_raw, cd_ml = CDG_TEST_SEASON[label]
        _, ds_raw, ds_ml = DSM_TEST_SEASON[label]
        print(f"    {label:<12} {eg_ml - eg_raw:>+9.3f} {cd_ml - cd_raw:>+9.3f} "
              f"{ds_ml - ds_raw:>+9.3f} {raw_s:>10.3f} {ml_s:>9.3f} "
              f"{ml_s - raw_s:>+10.3f}")
    print("    'chg' is corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse. Labels are")
    print("    Northern-calendar; 'autumn SON' is Dubbo's own local spring.")

    sub("seasons where the correction helped, on the sealed test year")
    print(f"    EGLC: {EGLC_SEASONS_HELPED} of 4   CDG: {CDG_SEASONS_HELPED} "
          f"of 4   DSM: {DSM_SEASONS_HELPED} of 4   Dubbo: {helped} of 4")
    print("    D39.12's watch-item named the validation-year rehearsal's 2-of-4")
    print("    seasons-helped as the fewest of any airport so far (F62). This")
    print("    line is the SAME question asked of the test year.")

    sub("day by day, on each airport's test year")
    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    print(f"    EGLC : closer than raw GFS on {EGLC_TEST_BETTER_N} of "
          f"{EGLC_TEST_DAYS:,} days ({EGLC_TEST_BETTER_PCT:.1f}%)")
    print(f"    CDG  : closer than raw GFS on {CDG_TEST_BETTER_N} of "
          f"{CDG_TEST_DAYS:,} days ({CDG_TEST_BETTER_PCT:.1f}%)")
    print(f"    DSM  : closer than raw GFS on {DSM_TEST_BETTER_N} of "
          f"{DSM_TEST_DAYS:,} days ({DSM_TEST_BETTER_PCT:.1f}%)")
    print(f"    Dubbo: closer than raw GFS on {better:,} of {n:,} days "
          f"({100 * better / n:.1f}%)")

    sub("feature importances, all four sealed tests")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'EGLC gain %':>12} {'CDG gain %':>12} "
          f"{'DSM gain %':>12} {'Dubbo gain %':>13} {'Dubbo splits':>13}")
    for name, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, _ = EGLC_TEST_IMPORTANCE[name]
        cd_share, _ = CDG_TEST_IMPORTANCE[name]
        ds_share, _ = DSM_TEST_IMPORTANCE[name]
        print(f"    {name:<18} {eg_share:>11.1f}% {cd_share:>11.1f}% "
              f"{ds_share:>11.1f}% {share:>12.1f}% {s:>13,}")
    print("    Gain totals depend on the data, so the shares and split counts")
    print("    are what compare meaningfully between airports.")

    sub("one data-source fact that is STRONGER at Dubbo than at DSM (D39.13)")
    print("    Every Dubbo forecast chunk was pulled with models=gfs_global")
    print("    (D16, F57, read back out of the saved .meta.txt URLs). At DSM")
    print("    the gfs_global versus gfs_seamless comparison found the two")
    print("    strings DIFFER on recent dates - 259 of 264 hours, by up to")
    print("    12.3 degC (F40), because Des Moines is inside CONUS. At Dubbo")
    print("    the same comparison (run in the SAME session as verify-on-")
    print("    contact, F52, rather than deferred) found the two strings")
    print("    IDENTICAL in both windows tested, 312 and 264 hours compared,")
    print("    0 differences in either, at the same grid point throughout.")
    print("    So Dubbo's dataset is confirmed identical to what gfs_seamless")
    print("    would have given - a stronger claim than DSM's data can make")
    print("    and one LFPG's still cannot (Q20 was never re-checked there).")
    print("    Every Dubbo chunk was still pulled with gfs_global regardless,")
    print("    so nothing in the project depends on this result either way.")


# ------------------------------------------------------------------ part G

def single_season_watch_item(common, methods, train):
    line("PART G - D39.12's single-season watch-item, described (NOT acted on)")

    print("D39.12 named this before the look, so that any inspection after")
    print("the test is honest: the place to look was written down before")
    print("anyone knew what the result was. F62 measured, on Dubbo's")
    print("validation year, that the correction's win is carried almost")
    print("entirely by one Northern-labelled season (autumn SON, Dubbo's own")
    print("local spring, -0.516 degC of the average improvement) while the")
    print("other three seasons are close to flat or very slightly worse.")
    print()
    print("THIS IS A DESCRIPTION AND NOTHING ELSE. The method is locked, it")
    print("did not change, and nothing here licenses a re-run or an")
    print("adjustment (D39.10, D39.11, D39.12).")

    sub("what F62 measured on the VALIDATION year, quoted from the lock")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'ML-corr':>9} "
          f"{'change':>9}")
    for label, months in SEASONS:
        days, raw_v, ml_v = S22_SEASON[label]
        print(f"    {label:<12} {days:>6,} {raw_v:>9.3f} {ml_v:>9.3f} "
              f"{F62_SEASON_CHG[label]:>+9.3f}")
    print(f"    seasons helped, validation year : {F62_SEASONS_HELPED} of 4")
    print(f"      (the fewest of any airport so far - EGLC, CDG and DSM each")
    print(f"       improved in 3 of 4)")
    print(f"    day-by-day win rate, validation year : {F62_BETTER_PCT:.1f}% "
          f"(190 of 355 days, also the lowest of the four)")

    sub("the same seasons, on the TEST year - what actually happened")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'ML-corr':>9} "
          f"{'change':>9}   validation chg   moved?")
    n_helped_test = 0
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        chg = ml_s - raw_s
        if chg < 0:
            n_helped_test += 1
        val_chg = F62_SEASON_CHG[label]
        same_dir = (chg < 0) == (val_chg < 0)
        print(f"    {label:<12} {len(idx):>6,} {raw_s:>9.3f} {ml_s:>9.3f} "
              f"{chg:>+9.3f}   {val_chg:>+14.3f}   "
              f"{'same direction' if same_dir else 'FLIPPED'}")
    print(f"    seasons helped, test year : {n_helped_test} of 4")
    print()
    print("    'autumn SON' (Dubbo's own local spring, D37, F61) is the")
    print("    season the watch-item names as the one to look at first if")
    print("    the overall result swings either way. Its test-year 'change'")
    print("    row, above, is that look - a description, not an adjustment.")

    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    print()
    print(f"    day-by-day win rate, test year : {100 * better / n:.1f}% "
          f"({better:,} of {n:,} days)")
    print(f"    day-by-day win rate, validation year : {F62_BETTER_PCT:.1f}% "
          f"(190 of 355 days)")

    sub("the worst single misses of the test year, for the record")
    ml_err = np.abs(np.array(methods["ML-corrected"]))
    raw_err = np.abs(np.array(methods["Raw GFS"]))
    idx = np.argsort(-raw_err)[:5]
    print(f"    {'date':<12} {'forecast':>9} {'observed':>9} {'raw err':>9} "
          f"{'ML err':>9}")
    for i in idx:
        r = common[i]
        print(f"    {str(r['date']):<12} {r['fc']:>9.2f} {r['obs']:>9.2f} "
              f"{raw_err[i]:>9.2f} {ml_err[i]:>9.2f}")
    print("    Listed because D39.12 asked for the single-season watch-item")
    print("    to be the first place to look if the result behaved oddly.")
    print("    Looking is describing; it changes nothing.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 24 - DUBBO'S SEALED-TEST EVALUATION. ONE LOOK. THE RESULT "
         "STANDS.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"airport       : {AIRPORT} - Dubbo, Australia (SPEC 3.4) - stage 2")
    print(f"                (D36, the fourth airport)")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC at {STATION} "
          f"(SPEC 4.1, D37, D39.1)")
    print(f"training      : {TRAIN_START} to {TRAIN_END}   (D13, D39.5)")
    print(f"SEALED TEST   : {TEST_START} to {TEST_END}   (D13, D39.6)")
    print(f"nothing after : {HARD_END}")
    print()
    print("This session executes DECISIONS D39 and decides nothing. Nothing is")
    print("tuned, searched, swapped or re-run. If anything did not fit the D39")
    print("record, the run stops and goes back to the owner (D39.11).")
    print()
    print("TWO THINGS DIFFER FROM DSM'S TEST, NOT ONE: the location AND the")
    print("target hour (D37). This result must not be quoted as though only")
    print("the location had moved (F63).")

    prove_it_matches_the_lock()
    train, test, obs_all, reconciled = join()
    if not reconciled:
        print()
        print("!!! A COUNT DID NOT RECONCILE. D39.11 says that is a stop signal:")
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
    compare_with_session22(common, methods, model, pred_resid, x_tr, y_tr)
    compare_with_prior_airports(common, methods, model)
    single_season_watch_item(common, methods, train)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). Nothing was")
    print("committed. Dubbo's test year was opened once, the locked method")
    print("ran once, and the number above is the result of record (D39.10).")
    print()
    print(f"DUBBO: {'PASSED' if passed else 'DID NOT PASS'}   "
          f"ML-corrected test-year MAE = {ml:.3f} degC against raw GFS "
          f"{mae(methods['Raw GFS']):.3f} and persistence "
          f"{mae(methods['Persistence']):.3f}")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
