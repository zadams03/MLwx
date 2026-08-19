"""Session 18: DSM'S SEALED-TEST EVALUATION. One look, and the result stands.

This script executes the method locked in DECISIONS D35. It decides nothing.
Every choice below was made in session 17, with DSM's test year still unseen.

D35 is D31 with the airport AND the target hour swapped and nothing else
touched, so this script is session 13's sealed test with the airport and the
target hour swapped and nothing else touched. PART 0 proves both of those
claims rather than asserting them.

TWO THINGS DIFFER FROM CDG'S TEST, NOT ONE. D31 could say "only the location
changed" (D26). D35 cannot: DSM changes the location AND the target hour,
because 12:00 UTC at Des Moines is 06:00 local - dawn, the part of the day
SPEC 4.1 chose 12:00 UTC to avoid in Europe (D33, F32). That cost was accepted
on purpose and in advance, and is written into SPEC 4.1 and D33. A DSM result
answers "does the recipe travel to a different region at a comparable local
time"; it must NOT be quoted as the controlled, location-only comparison EGLC
and CDG make between them (F46).

What it does, in D35's own order:
- D35.5  refits the locked model on DSM's FULL training window,
         2021-03-24 to 2025-07-31 (DSM's inner-training and DSM's validation
         year recombined). Everything fitted is fitted on this and nothing
         else: the model, the climatology baseline, the mean-bias figure.
- D35.6  opens DSM's test year, 2025-08-01 to 2026-07-31, for the first and
         only time. The two 2026 DSM raw chunk files are opened here for the
         first time in this project. Nothing after 2026-07-31 is used.
- D35.7  pairs with the D14 rule, reports the drop counts, and RECONCILES them
         against the prediction D35.7 wrote down before the look. Nothing is
         filled, ever (SPEC 2.2).
- D35.8  scores five methods on the same set of test days.
- D35.9  judges the frozen bar: does the corrected forecast beat BOTH raw GFS
         and persistence on mean absolute error?

Reads only from data/raw/. Never writes to data/raw/.

DSM'S SEAL IS NOW OPENED, ON PURPOSE, ONCE. Sessions 15, 16 and 17 kept DSM's
test year out: session 15 counted its structure without reading a value,
session 16 cut its load off at 2025-07-31, session 17 loaded nothing at all.
This session is the single authorised look (D35.10). Nothing is tuned,
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

# THE TWO THINGS THAT CHANGE FOR DSM (DECISIONS D32, D33, D35.1): the location,
# and the target hour. Nothing else in this file differs from CDG's sealed test.
STATION = "DSM"                       # IEM's own station id, not an ICAO code
AIRPORT = "DSM"                       # Des Moines, Iowa (SPEC 3.4)

TARGET_HOUR = 18                      # 18:00 UTC = local standard noon (D33)

# The full training window (DECISIONS D13, D35.5). This is DSM's inner-training
# plus DSM's validation year recombined - validation has done its job now the
# method is locked.
TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)

# DSM's sealed test year (DECISIONS D13, D35.6). Opened once, here.
TEST_START = date(2025, 8, 1)
TEST_END = date(2026, 7, 31)

# Hard wall. Nothing after the test year is used, which keeps the test set
# exactly one calendar year (DECISIONS D13, D35.6).
HARD_END = TEST_END

# The two sub-periods of the training window used in session 16 (DECISIONS
# D18). Kept here for reporting only - so the training-window row counts can be
# reconciled against the published session 16 counts. Nothing is fitted
# separately on them this session.
INNER_START = date(2021, 3, 24)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# All six chunk files. The two 2026 DSM files are included for the first time.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),     # test year, second half
]

# The one gap in the forecast series. Found at EGLC (F8), at LFPG (F22) and
# again at DSM, hour for hour (F38). For reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Exactly the session 05 settings, unchanged (DECISIONS D35.4,
# which is D31.4, which is D21.4). Nothing is tuned, searched or varied here.
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
# locked settings and the shared machinery come from; session13_test.py is
# CDG's sealed test, which is the same job at the previous airport.
PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"
STAGE2_TEST_SCRIPT = ROOT / "scripts" / "session13_test.py"

# What DECISIONS D35 says this session must run. Written out as data so the
# script can check itself against the lock rather than the reader having to
# trust the prose. Every line below is quoted from D35.
D35_LOCK = {
    "airport (D35.1)":                "DSM",
    "target hour (D35.1)":            18,
    "train start (D35.5)":            date(2021, 3, 24),
    "train end (D35.5)":              date(2025, 7, 31),
    "test start (D35.6)":             date(2025, 8, 1),
    "test end (D35.6)":               date(2026, 7, 31),
    "features (D35.3)":               ["forecast_temp_c", "season_sin",
                                       "season_cos"],
    "objective (D35.4)":              "regression_l1",
    "n_estimators (D35.4)":           300,
    "learning_rate (D35.4)":          0.05,
    "num_leaves (D35.4)":             15,
    "min_child_samples (D35.4)":      40,
    "subsample (D35.4)":              1.0,
    "colsample_bytree (D35.4)":       1.0,
    "reg_alpha (D35.4)":              0.0,
    "reg_lambda (D35.4)":             0.0,
    "random_state (D35.4)":           42,
    "n_jobs (D35.4)":                 1,
    "deterministic (D35.4)":          True,
    "force_row_wise (D35.4)":         True,
    "verbose (D35.4)":                -1,
    "pairing window minutes (D35.7)": 15,
    "climatology half window (D35.8)": 7.5,
}

# ---- what D35.7 predicted this test year would cost, BEFORE the look ---------
# Written down in session 17 from session 15's gap map (F38, F41). These are
# expectations to RECONCILE against, not numbers to accept. A count that will
# not reconcile is a stop signal (D35.11).
EXPECT_TEST_FCGAP_DAYS = 0            # F38: no forecast gap in the test year
EXPECT_TEST_OFFHOUR_DAYS = 0          # F41: no off-hour-only day
EXPECT_TEST_NOREPORT_DAYS = 0         # F41
EXPECT_TEST_NOTEMP_DAYS = 0           # F41
EXPECT_TEST_PAIRED_ROWS = 365
EXPECT_TEST_SCORED_DAYS = 365         # nothing lost, so nothing follows

# ---- what session 16 published for DSM's training side (F42) -----------------
EXPECT_TRAIN_ROWS = 1571              # 1,206 inner-training + 365 validation
EXPECT_INNER_ROWS = 1206
EXPECT_VALID_ROWS = 365

# Session 16's published DSM validation figures, from
# notes/session-16-check-output.txt and DECISIONS F45. Quoted for the
# comparison in PART E. They are a DIFFERENT year and a model fitted on about
# 30% less data, so they are context, not a target (D35.5).
S16_VALIDATION_MAE = {
    "Raw GFS":             1.748,
    "Persistence":         4.108,
    "Climatology":         4.772,
    "Mean-bias reference": 1.723,
    "ML-corrected":        1.466,
}
S16_VALIDATION_DAYS = 365
S16_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 1.687, 1.273),
    "spring MAM": (92, 1.958, 1.774),
    "summer JJA": (92, 1.532, 1.593),
    "autumn SON": (91, 1.816, 1.218),
}
S16_IMPORTANCE = {                    # feature -> (gain share %, splits)
    "forecast_temp_c": (45.0, 1850),
    "season_sin":      (37.3, 1366),
    "season_cos":      (17.7, 984),
}
S16_INSAMPLE_ML = 1.221               # DSM inner-training MAE, session 16
S16_BETTER_PCT = 55.6                 # days closer than raw GFS, session 16
S16_MEAN_BIAS = -0.2305               # mean DSM inner-training bias, F45

# EGLC's stage 1 sealed test (F16) and CDG's stage 2 sealed test (F30), quoted
# for PART F. Each airport is judged on its own data (SPEC 5.0), so these are
# context and NOT targets DSM has to reach (D35.9).
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
EGLC_TRAIN_ROWS = 1569
EGLC_VALID_MARGIN = 0.074             # session 05 validation margin, raw GFS
EGLC_TEST_MARGIN = 0.202              # session 07 test margin, raw GFS
EGLC_TEST_MEAN_BIAS = -0.1479

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
CDG_TRAIN_ROWS = 1569
CDG_VALID_MARGIN = 0.050              # session 11 validation margin, raw GFS
CDG_TEST_MARGIN = 0.188               # session 13 test margin, raw GFS
CDG_TEST_MEAN_BIAS = -0.0600

# D35.12's warm-end watch-item, measured on DSM's INNER-TRAINING rows in
# session 16 (F44) and written into the lock BEFORE this look. Quoted in PART G
# so that any inspection after the test is against a table written in advance.
F44_WARM_END = [                      # (threshold degC, days, mean bias, mean |bias|)
    (30, 114, -3.089, 3.449),
    (32,  57, -4.331, 4.360),
    (34,  37, -4.838, 4.838),
    (36,  21, -5.818, 5.818),
    (38,  13, -6.438, 6.438),
    (40,   5, -7.068, 7.068),
]
F44_INNER_FC_RANGE = (-21.70, 42.70)  # forecast range at 18:00, inner-training
F44_INNER_OBS_RANGE = (-23.28, 36.67)  # observed range at 18:00, inner-training

SEASONS = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
           ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]

OUT = ROOT / "notes" / "session-18-check-output.txt"


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
    """Return {date: forecast_temp_or_None} for 18:00 UTC, up to the hard end.

    Unlike session 16 there is no seal here: DSM's test year is loaded, because
    this is the one authorised look at it (DECISIONS D35.6, D35.10). The only
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


def load_obs_target_hour():
    """Return {date: observed_temp} for the 18:00 UTC hour, up to the hard end.

    The D14 pairing rule: the routine report belongs to the hour it is nearest
    to, and only if it is within 15 minutes of it. At DSM the routine report is
    stamped at :54 (F34), so the 17:54 report is the observation for 18:00 - a
    six-minute offset, smaller than EGLC's ten. The next report, 18:54, is 54
    minutes out, so the rule picks 17:54 without ambiguity. Anything further off
    is dropped and counted (D35.7).

    'near_target' separately records every routine report whose nearest whole
    hour is the target hour, with how many minutes it sits from it. That is
    bookkeeping for the drop reconciliation only - it is the same framing
    session 15 counted F41 in - and it changes no pairing, keeps no report the
    rule drops, and drops none the rule keeps.
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
    airport's target hour, 18:00 UTC at DSM.
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

    Two functions with the same shape do the same thing even if their comments,
    their docstrings or their names differ. This is used only to say something
    precise about a function whose source text is NOT character-identical: is
    the difference wording, or is it behaviour?
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
    """Check this script against DECISIONS D35, and against the two scripts it
    has to agree with.

    Three checks, because they answer three different questions.
    1. Does what this script is about to run match the written lock? Checked
       against D35_LOCK above, value by value.
    2. Is the machinery the same machinery session 05 locked? Checked by
       reading scripts/session05_model.py and comparing it with this file.
    3. Is this the same sealed test session 13 ran at the previous airport?
       Checked by reading scripts/session13_test.py and comparing. Exactly one
       constant should differ - TARGET_HOUR - and that one is D33.
    """
    line("PART 0 - checking this script against the lock (DECISIONS D35)")

    sub("check 1: every value D35 fixes, against what this script will use")
    actual = {
        "airport (D35.1)":                STATION,
        "target hour (D35.1)":            TARGET_HOUR,
        "train start (D35.5)":            TRAIN_START,
        "train end (D35.5)":              TRAIN_END,
        "test start (D35.6)":             TEST_START,
        "test end (D35.6)":               TEST_END,
        "features (D35.3)":               FEATURE_NAMES,
        "objective (D35.4)":              LGB_PARAMS["objective"],
        "n_estimators (D35.4)":           LGB_PARAMS["n_estimators"],
        "learning_rate (D35.4)":          LGB_PARAMS["learning_rate"],
        "num_leaves (D35.4)":             LGB_PARAMS["num_leaves"],
        "min_child_samples (D35.4)":      LGB_PARAMS["min_child_samples"],
        "subsample (D35.4)":              LGB_PARAMS["subsample"],
        "colsample_bytree (D35.4)":       LGB_PARAMS["colsample_bytree"],
        "reg_alpha (D35.4)":              LGB_PARAMS["reg_alpha"],
        "reg_lambda (D35.4)":             LGB_PARAMS["reg_lambda"],
        "random_state (D35.4)":           LGB_PARAMS["random_state"],
        "n_jobs (D35.4)":                 LGB_PARAMS["n_jobs"],
        "deterministic (D35.4)":          LGB_PARAMS["deterministic"],
        "force_row_wise (D35.4)":         LGB_PARAMS["force_row_wise"],
        "verbose (D35.4)":                LGB_PARAMS["verbose"],
        "pairing window minutes (D35.7)": 15,
        "climatology half window (D35.8)": CLIM_HALF_WINDOW_DAYS,
    }
    print(f"    {'what D35 fixes':<34} {'D35 says':<22} {'this run':<22} match?")
    mismatches = 0
    for k, want in D35_LOCK.items():
        got = actual[k]
        ok = got == want
        if not ok:
            mismatches += 1
        print(f"    {k:<34} {str(want):<22} {str(got):<22} "
              f"{'yes' if ok else 'NO - MISMATCH'}")
    print(f"    values checked: {len(D35_LOCK)}")
    print(f"    values that do not match D35: {mismatches}")
    assert mismatches == 0, "this script does not match the D35 lock - STOP"
    print("    (The 15-minute pairing window is the literal in")
    print("     load_obs_target_hour below. Check 3d prints that function's")
    print("     differences from session 13's, so it can be seen that the")
    print("     15 minutes is untouched.)")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    s2_src = STAGE2_TEST_SCRIPT.read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)
    s2 = ast.parse(s2_src)

    sub("check 2a: model settings, session 05 against this session")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 18':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}   (D35.4 requires 0)")
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
    assert identical, "shared code drifted from session 05 - STOP (D35.11)"
    print("    features() is handled separately below: its text differs from")
    print("    session 05's by one docstring line naming the fixed hour, and")
    print("    its executable code is compared with docstrings stripped out.")

    sub("check 3a: model settings, session 13 (CDG test) against this session")
    s2_p = top_level(s2, "LGB_PARAMS")
    keys = list(s2_p) + [k for k in new_p if k not in s2_p]
    n_diff = 0
    for k in keys:
        if s2_p.get(k, "<absent>") != new_p.get(k, "<absent>"):
            n_diff += 1
    print(f"    settings compared: {len(keys)}")
    print(f"    settings that differ from CDG's sealed test: {n_diff}")
    assert n_diff == 0, "settings differ from session 13 - STOP (D35.11)"

    sub("check 3b: the constants, session 13 (CDG) against session 18 (DSM)")
    print("    Exactly one constant should differ: TARGET_HOUR, 12 -> 18, which")
    print("    is D33 and nothing else. The split dates are shared by every")
    print("    airport (SPEC 4.3), so they must be identical.")
    print(f"    {'constant':<24} {'session 13 (CDG)':<34} "
          f"{'session 18 (DSM)':<18} same?")
    differing = []
    for c in ["TARGET_HOUR", "TRAIN_START", "TRAIN_END", "TEST_START",
              "TEST_END", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]:
        a = top_level(s2, c)
        b = top_level(new, c)
        if a != b:
            differing.append(c)
        print(f"    {c:<24} {str(a)[:33]:<34} "
              f"{(str(b)[:17] if a != b else ''):<18} "
              f"{'yes' if a == b else 'NO - DIFFERS'}")
    print(f"    constants that differ: {len(differing)}  {differing}")
    assert differing == ["TARGET_HOUR"], \
        "something other than the target hour differs from session 13 - STOP"

    sub("check 3c: session 18 against session 13, function by function")
    print("    This is the 'the airport and the hour changed, and nothing else'")
    print("    claim, checked in code rather than argued. Every function is")
    print("    compared character for character with CDG's sealed test script.")
    for name in ["all_days", "year_fraction", "features", "mae", "describe",
                 "_literal", "top_level", "func_source",
                 "climatology_from_training", "fit_on_training"]:
        a = func_source(s2_src, s2, name)
        b = func_source(new_src, new, name)
        print(f"    {name + '()':<28} "
              f"{'identical' if a == b else 'differs - shown below'}")
    print("    The two loaders are renamed, because '12z' would be a false name")
    print("    at an airport whose target hour is 18:00 UTC, so they are")
    print("    compared by an explicit old-name/new-name pair below.")
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
         "one docstring line: the sentence naming the fixed hour says 18:00\n"
         "    UTC at DSM instead of 12:00 (D33). No executable line differs -\n"
         "    proved below with docstrings stripped out."),
        ("load_forecast_12z", "load_forecast_target_hour",
         "the station code in the file name, the function name, and the\n"
         "    docstring naming the hour and the session that held the seal.\n"
         "    Nothing else."),
        ("load_obs_12z", "load_obs_target_hour",
         "the station code in the file name, the function name, and DSM's :54\n"
         "    reporting: the near-target bookkeeping is keyed on the report's\n"
         "    NEAREST whole hour, which is the framing session 15 counted F41\n"
         "    in, rather than CDG's dual clock-hour/nearest-hour framing that\n"
         "    F25 needed. The 15-minute D14 rule is untouched."),
        ("fit_on_training", "fit_on_training",
         "printed labels only - D31 references become D35 references and the\n"
         "    airport is named. Every fitted quantity is computed by the same\n"
         "    lines."),
    ]
    for old_name, new_name, why in pairs:
        print()
        print(f"    {new_name}() - {why}")
        a = func_source(s2_src, s2, old_name)
        b = func_source(new_src, new, new_name)
        if a == b:
            print("      (identical after all - no diff to show)")
            continue
        for d in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                      f"session13 {old_name}",
                                      f"session18 {new_name}",
                                      lineterm="", n=1):
            print(f"      {d}")

    sub("check 3e: executable code with docstrings removed")
    print("    A function whose text differs may still do exactly the same")
    print("    thing. This strips the docstring and the name and compares what")
    print("    is left, against session 13's.")
    for old_name, new_name in [("all_days", "all_days"),
                               ("year_fraction", "year_fraction"),
                               ("features", "features"),
                               ("mae", "mae"),
                               ("describe", "describe"),
                               ("climatology_from_training",
                                "climatology_from_training"),
                               ("load_forecast_12z",
                                "load_forecast_target_hour")]:
        a = func_code_shape(s2_src, s2, old_name)
        b = func_code_shape(new_src, new, new_name)
        print(f"    {new_name + '()':<28} "
              f"{'IDENTICAL' if a == b else 'different - see the diff above'}")
    print("    load_obs_target_hour() is expected to differ here as well as in")
    print("    text: its bookkeeping records reports by nearest hour, which is")
    print("    what F41 counted. The pairing itself - nearest report, 15-minute")
    print("    tolerance, drop and count - is unchanged and is visible in the")
    print("    diff above.")


# ------------------------------------------------------------------ part A

def join():
    line(f"PART A - the join at {TARGET_HOUR:02d}:00 UTC, both windows "
         f"(D35.6, D35.7)")

    print(f"airport     : {AIRPORT} - Des Moines, Iowa (SPEC 3.4, D35.1)")
    print(f"target hour : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1, D33, D35.1) -")
    print("              local standard noon at Des Moines, NOT the 12:00 UTC")
    print("              the two European airports use. 12:00 UTC there is")
    print("              06:00 local, which is dawn (F32).")
    print("pairing rule: the routine report nearest the hour, and only if within")
    print("              15 minutes of it (DECISIONS D14, D35.7). At DSM the")
    print("              routine report is stamped :54 (F34), so 18:00 UTC is")
    print("              served by the 17:54 report - a 6-minute offset,")
    print("              smaller than EGLC's ten and inside D14's tolerance.")
    print()
    print("DSM'S TEST YEAR IS OPENED HERE, for the first and only time (D35.10).")
    print("The two 2026 DSM raw chunk files are read for the first time in this")
    print("project. Sessions 15, 16 and 17 never opened them.")

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
    print("    F34 predicted -6 minutes from DSM's :54 report, and F42 found")
    print("    -6 on 1,590 of 1,591 training days (2024-06-07 filed at 17:58).")
    ambiguous = sum(1 for recs in near_target.values()
                    if len([r for r in recs
                            if abs(r[0]) <= 15 and r[1] is not None]) > 1)
    print(f"    days with MORE THAN ONE report inside D14's 15-minute window: "
          f"{ambiguous:,}")
    print("    So the pairing is never ambiguous at DSM: where a day has a")
    print("    usable observation, exactly one report qualifies and the rule")
    print("    never has to choose between two.")

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
    print("    Nothing was filled in (SPEC 2.2, D35.7).")

    train, test = built["train"], built["test"]
    inner, valid = built["inner"], built["valid"]

    sub("reconciliation 1: does the training window add up? (D35.5, D35.11)")
    print("    The training window is DSM's inner-training plus DSM's validation")
    print("    year, which session 16 counted separately. Those published counts")
    print("    must add up to this session's training count, or something has")
    print("    drifted and this session must stop.")
    print(f"    session 16 inner-training kept rows (F42): {EXPECT_INNER_ROWS:,}")
    print(f"    session 16 validation kept rows (F42)    :   {EXPECT_VALID_ROWS:,}")
    print(f"    published total                          : {EXPECT_TRAIN_ROWS:,}")
    print(f"    this session, training window kept rows  : {len(train):,}")
    print(f"    this session, of which dated <= {INNER_END} : {len(inner):,}")
    print(f"    this session, of which dated >= {VALID_START} : {len(valid):,}")
    ok_train = (len(train) == EXPECT_TRAIN_ROWS
                and len(inner) == EXPECT_INNER_ROWS
                and len(valid) == EXPECT_VALID_ROWS)
    print(f"    reconciles: {'YES' if ok_train else 'NO - STOP AND RAISE (D35.11)'}")
    print(f"    (1,571, not the 1,569 both European airports fitted: DSM loses")
    print(f"     only the 20 shared gap days, because its observation record")
    print(f"     loses no day at all in the training window - F41, F42, D35.5.)")

    sub("the F38 forecast gap, for the record")
    gap_days = all_days(GAP_START, GAP_END)
    kept_dates = {r["date"] for r in train}
    print(f"    gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END}), all inside training")
    print(f"    of those, dropped here: "
          f"{sum(1 for d in gap_days if d not in kept_dates)}")

    # ------------------------------------------------- the test-year drop count
    sub("THE TEST-YEAR DROP COUNT (D35.7)")
    t_days = all_days(TEST_START, TEST_END)
    t_kept = {r["date"] for r in test}
    t_dropped = [d for d in t_days if d not in t_kept]
    print(f"    test-year calendar days : {len(t_days):,}")
    print(f"    paired rows kept        : {len(test):,}")
    print(f"    days dropped            : {len(t_dropped):,}")
    if not t_dropped:
        print("    (no test-year day was dropped - which is what D35.7")
        print("     predicted, and would make DSM the first airport to lose no")
        print("     test day at all)")

    # Sort each dropped day into exactly one of the four causes F41 counted,
    # which is what D35.7's prediction was built from. "Near the target hour"
    # means the report's nearest whole hour is 18:00, which is the framing
    # session 15 used.
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

    sub("reconciliation 2: THE DROPS AGAINST D35.7's ADVANCE PREDICTION")
    print("    D35.7 wrote these numbers down in session 17, from session 15's")
    print("    gap map, BEFORE DSM's test year was opened. A prediction made")
    print("    before the look is a stronger check than a count made after it.")
    print("    A count that will not reconcile is a stop signal (D35.11).")
    print()
    print(f"    {'cause':<52} {'predicted':>9} {'actual':>7}  verdict")
    checks = [
        ("forecast-gap days in the test year (F38)",
         EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)),
        ("days lost to an off-hour-only report (F41)",
         EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)),
        ("days lost to no report near the 18:00 hour (F41)",
         EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)),
        ("days lost to a report in place with no temperature (F41)",
         EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)),
        ("paired rows expected", EXPECT_TEST_PAIRED_ROWS, len(test)),
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
    mean-bias figure. All three see only DSM 2021-03-24 to 2025-07-31 (D35.5,
    D35.8, SPEC 2.1c).
    """
    line("PART B - fit on DSM's FULL training window only (D35.5, D35.8)")

    print("Everything fitted in this session is fitted here, on DSM's training")
    print("window, and on nothing else: the model, the climatology baseline and")
    print("the mean-bias figure. The test year plays no part in any fit.")

    x_tr = features(train)
    y_tr = np.array([r["resid"] for r in train], dtype=float)

    sub("the model")
    print(f"    rows fitted on : {len(x_tr):,}  "
          f"({train[0]['date']} to {train[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (D19, D35.3)")
    print("    target         : residual, observed minus forecast (SPEC 4.2,")
    print("                     D35.2). The model never predicts temperature.")
    print("    settings (locked in D35.4, nothing tuned this session):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_tr, y_tr)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    sub("the mean-bias figure (D35.8)")
    mean_bias = float(np.mean(y_tr))
    print(f"    mean training-window bias (observed - forecast): "
          f"{mean_bias:+.4f} degC")
    print(f"    over {len(y_tr):,} training days. The mean-bias reference is")
    print("    the raw forecast plus this one constant, and nothing else.")
    print(f"    raw GFS MAE on the training window (in sample): "
          f"{mae(y_tr):.3f} degC")
    print(f"    session 16's inner-training figure was {S16_MEAN_BIAS:+.4f} degC")
    print(f"    (F45). EGLC's constant was {EGLC_TEST_MEAN_BIAS:+.4f} (F16) and")
    print(f"    CDG's {CDG_TEST_MEAN_BIAS:+.4f} (F30). DSM's is the largest of")
    print("    the three, so there is a little more constant offset to take")
    print("    here than in Europe - which is what F43 found on the training")
    print("    side, and it is still small beside a mean |bias| near 2 degC.")

    sub("the climatology baseline (D35.8, SPEC 2.1c)")
    print("    seasonal average of the OBSERVED temperature at DSM, from")
    print(f"    training-window days only, +/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print("    measured around the circle so late December and early January")
    print("    are neighbours.")
    clim = climatology_from_training(train)

    return model, mean_bias, clim, x_tr, y_tr


# ------------------------------------------------------------------ part C

def score_test_year(test, obs_all, model, mean_bias, clim):
    line("PART C - THE SEALED TEST AT DSM (D35.6, D35.8, D35.9)")

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
    print(f"    D35.7 expected                                : "
          f"{EXPECT_TEST_SCORED_DAYS:,}")
    print(f"    date range                                    : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print(f"    Persistence needs yesterday's {TARGET_HOUR}:00 observation, a")
    print("    past-only value (SPEC 2.1d). For the first test day,")
    print("    2025-08-01, 'yesterday' is 2025-07-31, which sits in the")
    print("    training window. That is a past observation, so it is legal and")
    print("    it is used - written down in D35.8 in advance so it is not")
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

    sub(f"DSM TEST-YEAR MAE, {len(common):,} common days "
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
    line("PART D - THE VERDICT against the frozen bar (SPEC 5.3, 5.0, D35.9)")

    print("The bar, frozen before any model existed and unchanged since:")
    print("  an airport passes if the corrected forecast has a LOWER MAE than")
    print("  BOTH raw GFS AND persistence, over that airport's held-out test")
    print("  year. Stage 2 is each further individual airport put to that bar,")
    print("  one at a time; DSM is the airport in it now.")
    print("It is qualitative. There is no numeric margin and there never will")
    print("be one (SPEC 5.3, DECISIONS D22). Climatology and the mean-bias")
    print("reference are reported but do not decide pass or fail (D23).")
    print("The bar is judged once per airport, on that airport's own data")
    print("(SPEC 5.0). EGLC's and CDG's passes do not excuse a DSM failure, and")
    print("DSM is measured against DSM's own raw GFS and DSM's own persistence")
    print("only. Stage 1's 16.3% and stage 2's 13.5% are not targets (D35.9).")

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
        banner = ["DSM PASSES.",
                  "At Des Moines the corrected forecast beats both raw GFS and",
                  "persistence over the held-out test year, on mean absolute",
                  "error. The recipe travelled to a different region, at a",
                  "different target hour."]
    else:
        banner = ["DSM DOES NOT PASS.",
                  "At Des Moines the corrected forecast does not beat both raw",
                  "GFS and persistence over the held-out test year.",
                  "This is an honest finding (SPEC 2.4, D35.10), not a reason",
                  "to re-run or to tune. It is a result about how far the",
                  "recipe travels, which is what a third airport was for."]
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
    print("    D35.8 said in advance which half of the bar binds at DSM:")
    print("    persistence is far weaker in the continental interior (4.108 on")
    print("    the validation year against 2.523 at CDG and 2.226 at EGLC,")
    print("    F45), so THE RAW-GFS MARGIN IS THE ONE THAT DECIDES THE VERDICT")
    print("    IN PRACTICE. Both halves are still required by the bar.")
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
        print("    as D35.8 said it was on DSM's validation year (F45). So a")
        print("    small constant is worth taking at DSM, unlike at CDG - which")
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
    print("    The headline verdict above is judged on the whole year, not")
    print("    season by season (SPEC 5.3).")

    return passed, ml


# ------------------------------------------------------------------ part E

def compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr):
    line("PART E - the test number beside session 16's DSM rehearsal")

    print("A DIFFERENCE IS EXPECTED AND IS NOT A PROBLEM (D35.5). Three things")
    print("differ between the two columns below:")
    print("  1. a different year of weather - the validation year 2024-08-01 to")
    print("     2025-07-31, against the test year 2025-08-01 to 2026-07-31;")
    print("  2. a model fitted on about 30% more data - DSM's full training")
    print("     window here (1,571 rows), DSM's inner-training only in session")
    print("     16 (1,206 rows);")
    print("  3. therefore climatology and the mean-bias figure differ too.")
    print("The recipe is identical. Session 16's figures are quoted from")
    print("notes/session-16-check-output.txt and DECISIONS F45.")

    sub("MAE, side by side (different years - context, not a like-for-like)")
    print(f"    {'method':<22} {'s16 valid':>10} {'s18 test':>10} "
          f"{'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = S16_VALIDATION_MAE[name]
        print(f"    {name:<22} {then:>10.3f} {now:>10.3f} {now - then:>+11.3f}")
    print(f"    days scored            {S16_VALIDATION_DAYS:>10,} "
          f"{len(common):>10,}")
    print()
    print("    Read the raw GFS row first. It says how hard the two years were")
    print("    for GFS in the first place, which is the context every other")
    print("    row has to be read against.")

    sub("the margin over raw GFS, which is the comparable quantity")
    for label, ref, ml in (
            ("session 16, validation year",
             S16_VALIDATION_MAE["Raw GFS"], S16_VALIDATION_MAE["ML-corrected"]),
            ("session 18, sealed test year",
             mae(methods["Raw GFS"]), mae(methods["ML-corrected"]))):
        print(f"    {label:<30} {ref - ml:+.3f} degC "
              f"({100 * (ref - ml) / ref:+.1f}%)")
    print("    Margins are more comparable than raw MAE figures, because they")
    print("    divide out how hard the year was. They are still two different")
    print("    years, so this is a sense check, not a measurement.")

    sub("per season, session 16 validation against session 18 test")
    print(f"    {'season':<12} {'s16 raw':>8} {'s16 ML':>8} {'s16 chg':>8}  "
          f"{'s18 raw':>8} {'s18 ML':>8} {'s18 chg':>8}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        _, s16_raw, s16_ml = S16_SEASON[label]
        print(f"    {label:<12} {s16_raw:>8.3f} {s16_ml:>8.3f} "
              f"{s16_ml - s16_raw:>+8.3f}  {raw_s:>8.3f} {ml_s:>8.3f} "
              f"{ml_s - raw_s:>+8.3f}")
    print("    'chg' is the corrected MAE minus raw GFS MAE for that season.")
    print("    F45 found DSM's losing season was SUMMER, the first airport")
    print("    where it was not winter. This line says what the test year did.")

    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>13} {'gain share':>11} {'splits':>8}  "
          f"{'s16 share':>10} {'s16 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s16_share, s16_splits = S16_IMPORTANCE[n]
        print(f"    {n:<18} {g:>13.1f} {share:>10.1f}% {s:>8,}  "
              f"{s16_share:>9.1f}% {s16_splits:>11,}")
    print("    Both inputs are used and neither is ignored. Session 16 found")
    print("    forecast temperature leading with season_sin close behind, which")
    print("    is what an airport carrying a strong version of BOTH bias")
    print("    structures should look like (F43, F45).")

    sub("in-sample check only, training window (NOT a result)")
    in_pred = model.predict(x_tr)
    print(f"    raw GFS MAE on the training window      : {mae(y_tr):.3f} degC")
    print(f"    ML-corrected MAE on the training window : "
          f"{mae(y_tr - in_pred):.3f} degC")
    print(f"    session 16, same figure on inner-training: "
          f"{S16_INSAMPLE_ML:.3f} degC")
    print("    A model always looks better on the data it was fitted to, so")
    print("    this proves nothing about performance. It is here only so the")
    print("    number is not a surprise later.")

    sub("the correction the model actually applied over DSM's test year")
    describe(pred_resid, "predicted residual added to the forecast")
    print("    Session 16's corrections over DSM's validation year, for scale:")
    print("    mean -0.116, st dev 1.607, range -5.3 to +3.1 degC (F45).")
    print("    Both are much larger than Europe's (st dev 0.720 at EGLC and")
    print("    0.751 at CDG), which is what a larger bias should look like.")


# ------------------------------------------------------------------ part F

def compare_with_europe(common, methods, model):
    line("PART F - how the recipe travelled: DSM beside EGLC (F16) and CDG (F30)")

    print("EGLC's figures are session 07's sealed test (F16) and CDG's are")
    print("session 13's (F30), quoted from their notes files.")
    print()
    print("READ THIS AS CONTEXT, NOT AS A COMPARISON OF LIKE WITH LIKE. SPEC")
    print("5.0 judges each airport on its own data. Three cautions, all written")
    print("down before this look:")
    print("  1. DSM changes the LOCATION AND THE TARGET HOUR against the two")
    print("     European airports (D33, SPEC 4.1, F46). It is not the")
    print("     controlled, location-only comparison EGLC and CDG make between")
    print("     themselves, and must not be quoted as if it were.")
    print("  2. All three airports were tested on THE SAME TWELVE MONTHS,")
    print("     because D13's split dates are shared. DSM answers the region")
    print("     half of F30's caveat and not the year half (F46).")
    print("  3. EGLC's 16.3% and CDG's 13.5% are not targets DSM had to reach")
    print("     (D35.9).")

    sub("test-year MAE, each airport on its own test year")
    print(f"    {'method':<22} {'EGLC':>9} {'CDG':>9} {'DSM':>9}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        print(f"    {name:<22} {EGLC_TEST_MAE[name]:>9.3f} "
              f"{CDG_TEST_MAE[name]:>9.3f} {mae(methods[name]):>9.3f}")
    print(f"    {'days scored':<22} {EGLC_TEST_DAYS:>9,} {CDG_TEST_DAYS:>9,} "
          f"{len(common):>9,}")
    print(f"    {'training rows fitted':<22} {EGLC_TRAIN_ROWS:>9,} "
          f"{CDG_TRAIN_ROWS:>9,} {EXPECT_TRAIN_ROWS:>9,}")
    print("    All five rows are error measures, so larger is worse. Every")
    print("    reference is worse at DSM, which is what a continental interior")
    print("    means: there is more error there to begin with.")

    sub("the margin over each reference, all three airports")
    ml_now = mae(methods["ML-corrected"])
    print(f"    {'vs':<22} {'EGLC':>20} {'CDG':>20} {'DSM':>20}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference",
                 "Climatology"]:
        m_e = EGLC_TEST_MAE[name] - EGLC_TEST_MAE["ML-corrected"]
        m_c = CDG_TEST_MAE[name] - CDG_TEST_MAE["ML-corrected"]
        ref_now = mae(methods[name])
        m_d = ref_now - ml_now
        print(f"    {name:<22} "
              f"{f'{m_e:+.3f} ({100 * m_e / EGLC_TEST_MAE[name]:+.1f}%)':>20} "
              f"{f'{m_c:+.3f} ({100 * m_c / CDG_TEST_MAE[name]:+.1f}%)':>20} "
              f"{f'{m_d:+.3f} ({100 * m_d / ref_now:+.1f}%)':>20}")
    print("    Margins are degC of MAE saved by the correction. Positive means")
    print("    the correction is ahead of that reference. The PERCENTAGE is the")
    print("    comparable figure across airports, because it divides out how")
    print("    hard each airport's problem is.")

    sub("rehearsal margin against test margin, at all three airports")
    raw_now = mae(methods["Raw GFS"])
    dsm_valid_margin = (S16_VALIDATION_MAE["Raw GFS"]
                        - S16_VALIDATION_MAE["ML-corrected"])
    print(f"    {'airport':<10} {'rehearsal margin':>24} {'test margin':>24}")
    print(f"    {'EGLC':<10} "
          f"{f'{EGLC_VALID_MARGIN:+.3f} degC (6.0%)':>24} "
          f"{f'{EGLC_TEST_MARGIN:+.3f} degC (16.3%)':>24}")
    print(f"    {'CDG':<10} "
          f"{f'{CDG_VALID_MARGIN:+.3f} degC (3.5%)':>24} "
          f"{f'{CDG_TEST_MARGIN:+.3f} degC (13.5%)':>24}")
    print(f"    {'DSM':<10} "
          f"{f'{dsm_valid_margin:+.3f} degC (16.1%)':>24} "
          f"{f'{raw_now - ml_now:+.3f} degC ({100 * (raw_now - ml_now) / raw_now:+.1f}%)':>24}")
    print("    D35.10 said in advance that DSM's rehearsal margin being the")
    print("    widest of the three was NOT a reason to expect a pass. This line")
    print("    records what actually happened.")

    sub("per season, all three sealed tests")
    print(f"    {'season':<12} {'EGLC chg':>9} {'CDG chg':>9} "
          f"{'DSM raw':>9} {'DSM ML':>9} {'DSM chg':>9}")
    helped = 0
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        if ml_s < raw_s:
            helped += 1
        _, eg_raw, eg_ml = EGLC_TEST_SEASON[label]
        _, cd_raw, cd_ml = CDG_TEST_SEASON[label]
        print(f"    {label:<12} {eg_ml - eg_raw:>+9.3f} {cd_ml - cd_raw:>+9.3f} "
              f"{raw_s:>9.3f} {ml_s:>9.3f} {ml_s - raw_s:>+9.3f}")
    print("    'chg' is corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse.")

    sub("seasons where the correction helped, on the sealed test year")
    print(f"    EGLC: 4 of 4   CDG: 3 of 4   DSM: {helped} of 4")
    print("    At EGLC and CDG the season the correction hurt was winter. DSM's")
    print("    rehearsal flipped that - winter was its second-best season and")
    print("    summer was its only loss (F45).")

    sub("day by day, on each airport's test year")
    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    print(f"    EGLC: closer than raw GFS on 221 of {EGLC_TEST_DAYS:,} days "
          f"({EGLC_TEST_BETTER_PCT:.1f}%)")
    print(f"    CDG : closer than raw GFS on 213 of {CDG_TEST_DAYS:,} days "
          f"({CDG_TEST_BETTER_PCT:.1f}%)")
    print(f"    DSM : closer than raw GFS on {better:,} of {n:,} days "
          f"({100 * better / n:.1f}%)")

    sub("feature importances, all three sealed tests")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'EGLC gain %':>12} {'CDG gain %':>12} "
          f"{'DSM gain %':>12} {'DSM splits':>12}")
    for name, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, _ = EGLC_TEST_IMPORTANCE[name]
        cd_share, _ = CDG_TEST_IMPORTANCE[name]
        print(f"    {name:<18} {eg_share:>11.1f}% {cd_share:>11.1f}% "
              f"{share:>11.1f}% {s:>12,}")
    print("    Gain totals depend on the data, so the shares and split counts")
    print("    are what compare meaningfully between airports.")

    sub("one data-source fact that is STRONGER at DSM than at CDG (D35.13)")
    print("    Every DSM forecast chunk was pulled with models=gfs_global (D16,")
    print("    F38, read back out of the saved .meta.txt URLs). At DSM the")
    print("    gfs_global versus gfs_seamless comparison WAS run (F40), and it")
    print("    gave a different answer from EGLC's: on recent dates the two")
    print("    strings return DIFFERENT data - 259 of 264 hours differing by up")
    print("    to 12.3 degC, from a different grid point, because Des Moines is")
    print("    inside CONUS where gfs_seamless may prefer a higher-resolution")
    print("    non-GFS model. So this result is genuine NCEP GFS BY")
    print("    CONSTRUCTION of the D16 pin, and it must NOT be said that the")
    print("    two strings agree at DSM - they do not. At LFPG the comparison")
    print("    was never run at all (Q20), so stage 2's first airport cannot")
    print("    make the by-construction claim stage 1 and DSM can.")


# ------------------------------------------------------------------ part G

def warm_end_watch_item(common, methods, train, pred_resid):
    line("PART G - D35.12's warm-end watch-item, described (NOT acted on)")

    print("D35.12 named this before the look, so that any inspection after the")
    print("test is honest: the place to look was written down before anyone")
    print("knew the result. F44 measured, on DSM's inner-training rows at")
    print("18:00 UTC, that the forecast overshoots badly at the warm extreme")
    print("and that the overshoot grows with the forecast.")
    print()
    print("THIS IS A DESCRIPTION AND NOTHING ELSE. The method is locked, it did")
    print("not change, and nothing here licenses a re-run or an adjustment")
    print("(D35.10, D35.11, D35.12).")

    sub("what F44 measured on inner-training, quoted from the lock")
    print(f"    {'selection':<26} {'days':>6} {'mean bias':>11} "
          f"{'mean |bias|':>12}")
    for thr, days, mb, mab in F44_WARM_END:
        print(f"    forecast >= {thr} degC{'':<9} {days:>6,} {mb:>+11.3f} "
              f"{mab:>12.3f}")
    print(f"    forecast range at 18:00 UTC, inner-training : "
          f"{F44_INNER_FC_RANGE[0]:+.2f} to {F44_INNER_FC_RANGE[1]:+.2f} degC")
    print(f"    observed range at 18:00 UTC, inner-training : "
          f"{F44_INNER_OBS_RANGE[0]:+.2f} to {F44_INNER_OBS_RANGE[1]:+.2f} degC")

    tr_fc = np.array([r["fc"] for r in train])
    tr_obs = np.array([r["obs"] for r in train])
    sub("the same ranges on the FULL training window the test model was fitted on")
    print(f"    forecast range at 18:00 UTC, training window: "
          f"{tr_fc.min():+.2f} to {tr_fc.max():+.2f} degC")
    print(f"    observed range at 18:00 UTC, training window: "
          f"{tr_obs.min():+.2f} to {tr_obs.max():+.2f} degC")
    print("    A tree model cannot extrapolate past the range it was fitted on,")
    print("    so on a test day hotter than anything in training it applies the")
    print("    correction it learned at the top of that range (D35.12).")

    sub("the warm end of the TEST year, by the same thresholds")
    fc_te = np.array([r["fc"] for r in common])
    resid_te = np.array([r["obs"] - r["fc"] for r in common])
    ml_err = np.abs(np.array(methods["ML-corrected"]))
    raw_err = np.abs(np.array(methods["Raw GFS"]))
    print(f"    {'selection':<26} {'days':>6} {'mean bias':>11} "
          f"{'raw MAE':>9} {'ML MAE':>9} {'change':>9}")
    for thr, _, _, _ in F44_WARM_END:
        sel = fc_te >= thr
        if not sel.any():
            print(f"    forecast >= {thr} degC{'':<9} {0:>6,} "
                  f"{'-':>11} {'-':>9} {'-':>9} {'-':>9}")
            continue
        print(f"    forecast >= {thr} degC{'':<9} {int(sel.sum()):>6,} "
              f"{resid_te[sel].mean():>+11.3f} {raw_err[sel].mean():>9.3f} "
              f"{ml_err[sel].mean():>9.3f} "
              f"{ml_err[sel].mean() - raw_err[sel].mean():>+9.3f}")
    print("    'change' is the corrected MAE minus raw GFS MAE on those days.")
    print("    Negative means the correction helped there.")

    above = int((fc_te > tr_fc.max()).sum())
    print()
    print(f"    test days with a forecast above the training-window maximum "
          f"({tr_fc.max():.2f}): {above:,}")
    print("    Those are the days where the model is applying the correction it")
    print("    learned at the very top of its training range, because it cannot")
    print("    extrapolate past it. Counted, named, and not acted on.")

    sub("the worst single misses of the test year, for the record")
    idx = np.argsort(-raw_err)[:5]
    print(f"    {'date':<12} {'forecast':>9} {'observed':>9} {'raw err':>9} "
          f"{'ML err':>9} {'correction':>11}")
    for i in idx:
        r = common[i]
        print(f"    {str(r['date']):<12} {r['fc']:>9.2f} {r['obs']:>9.2f} "
              f"{raw_err[i]:>9.2f} {ml_err[i]:>9.2f} {pred_resid[i]:>+11.2f}")
    print("    Listed because D35.12 asked for the warm days to be the first")
    print("    place to look if the result behaved oddly. Looking is describing;")
    print("    it changes nothing.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 18 - DSM'S SEALED-TEST EVALUATION. ONE LOOK. THE RESULT STANDS.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"airport       : {AIRPORT} - Des Moines, Iowa (SPEC 3.4) - stage 2")
    print(f"                (D32, the third airport)")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC at {STATION} "
          f"(SPEC 4.1, D33, D35.1)")
    print(f"training      : {TRAIN_START} to {TRAIN_END}   (D13, D35.5)")
    print(f"SEALED TEST   : {TEST_START} to {TEST_END}   (D13, D35.6)")
    print(f"nothing after : {HARD_END}")
    print()
    print("This session executes DECISIONS D35 and decides nothing. Nothing is")
    print("tuned, searched, swapped or re-run. If anything did not fit the D35")
    print("record, the run stops and goes back to the owner (D35.11).")
    print()
    print("TWO THINGS DIFFER FROM CDG'S TEST, NOT ONE: the location AND the")
    print("target hour (D33). D26's 'only the location changed' does not hold")
    print("for DSM, and this result must not be quoted as if it did (F46).")

    prove_it_matches_the_lock()
    train, test, obs_all, reconciled = join()
    if not reconciled:
        print()
        print("!!! A COUNT DID NOT RECONCILE. D35.11 says that is a stop signal:")
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
    compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr)
    compare_with_europe(common, methods, model)
    warm_end_watch_item(common, methods, train, pred_resid)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). Nothing was")
    print("committed. DSM's test year was opened once, the locked method ran")
    print("once, and the number above is the result of record (D35.10).")
    print()
    print(f"DSM: {'PASSED' if passed else 'DID NOT PASS'}   "
          f"ML-corrected test-year MAE = {ml:.3f} degC against raw GFS "
          f"{mae(methods['Raw GFS']):.3f} and persistence "
          f"{mae(methods['Persistence']):.3f}")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
