"""Session 07: THE SEALED-TEST EVALUATION. One look, and the result stands.

This script executes the method locked in DECISIONS D21. It decides nothing.
Every choice below was made in session 06, with the test year still unseen.

What it does, in D21's own order:
- D21.5  refits the locked model on the FULL training window,
         2021-03-24 to 2025-07-31 (inner-training and the validation year
         recombined). Everything fitted is fitted on this and nothing else:
         the model, the climatology baseline, the mean-bias figure.
- D21.6  opens the test year, 2025-08-01 to 2026-07-31, for the first and only
         time. The two 2026 raw chunk files are opened here for the first time.
         Nothing after 2026-07-31 is used.
- D21.7  pairs with the D14 rule and reports the drop counts. Nothing is
         filled, ever (SPEC 2.2).
- D21.8  scores five methods on the same set of test days.
- D21.9  judges the frozen bar: does the corrected forecast beat BOTH raw GFS
         and persistence on mean absolute error?

Reads only from data/raw/. Never writes to data/raw/.

THE SEAL IS NOW OPENED, ON PURPOSE, ONCE. Sessions 04 and 05 kept the test year
out of the script entirely. This session is the single authorised look
(D21.10). Nothing is tuned, searched, swapped or re-run. Whatever comes out is
reported straight - a failure is an honest finding (SPEC 2.4), not something to
fix by trying again.

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

TARGET_HOUR = 12                      # 12:00 UTC (SPEC 4.1, DECISIONS D21.1)

# The full training window (DECISIONS D13, D21.5). This is inner-training plus
# the validation year recombined - validation has done its job now the method
# is locked.
TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)

# The sealed test year (DECISIONS D13, D21.6). Opened once, here.
TEST_START = date(2025, 8, 1)
TEST_END = date(2026, 7, 31)

# Hard wall. Nothing after the test year is used, which keeps the test set
# exactly one calendar year (DECISIONS D13, D21.6).
HARD_END = TEST_END

# The two sub-periods of the training window used in sessions 04 and 05
# (DECISIONS D18). Kept here for reporting only - so the training-window row
# counts can be reconciled against the published session 04/05 counts. Nothing
# is fitted separately on them this session.
INNER_START = date(2021, 3, 24)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# All six chunk files. The two 2026 files are included for the first time.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),     # test year, second half
]

# The one gap in the forecast series (DECISIONS F8), for reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Exactly the session 05 settings, unchanged (DECISIONS D21.4).
# Nothing is tuned, searched or varied in this session.
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

PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"

# What DECISIONS D21 says this session must run. Written out as data so the
# script can check itself against the lock rather than the reader having to
# trust the prose. Every line below is quoted from D21.
D21_LOCK = {
    "target hour (D21.1)":            12,
    "train start (D21.5)":            date(2021, 3, 24),
    "train end (D21.5)":              date(2025, 7, 31),
    "test start (D21.6)":             date(2025, 8, 1),
    "test end (D21.6)":               date(2026, 7, 31),
    "features (D21.3)":               ["forecast_temp_c", "season_sin",
                                       "season_cos"],
    "objective (D21.4)":              "regression_l1",
    "n_estimators (D21.4)":           300,
    "learning_rate (D21.4)":          0.05,
    "num_leaves (D21.4)":             15,
    "min_child_samples (D21.4)":      40,
    "subsample (D21.4)":              1.0,
    "colsample_bytree (D21.4)":       1.0,
    "reg_alpha (D21.4)":              0.0,
    "reg_lambda (D21.4)":             0.0,
    "random_state (D21.4)":           42,
    "n_jobs (D21.4)":                 1,
    "deterministic (D21.4)":          True,
    "force_row_wise (D21.4)":         True,
    "verbose (D21.4)":                -1,
    "pairing window minutes (D21.7)": 15,
    "climatology half window (D21.8)": 7.5,
}

# Session 05's published validation figures, from notes/session-05-check-output
# .txt and DECISIONS F15. Quoted for the comparison in PART E. They are a
# DIFFERENT year and a model fitted on about 20% less data, so they are context,
# not a target (D21.5).
S05_VALIDATION_MAE = {
    "Raw GFS":             1.239,
    "Persistence":         2.226,
    "Climatology":         2.865,
    "Mean-bias reference": 1.231,
    "ML-corrected":        1.165,
}
S05_VALIDATION_DAYS = 363
S05_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 0.972, 1.059),
    "spring MAM": (92, 1.337, 1.322),
    "summer JJA": (90, 1.498, 1.177),
    "autumn SON": (91, 1.147, 1.098),
}
S05_IMPORTANCE = {                    # feature -> (gain share %, splits)
    "forecast_temp_c": (44.3, 1614),
    "season_sin":      (26.7, 1337),
    "season_cos":      (29.0, 1249),
}
S05_INSAMPLE_ML = 0.879               # inner-training MAE, session 05

SEASONS = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
           ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]

OUT = ROOT / "notes" / "session-07-check-output.txt"


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

    Unlike sessions 04 and 05 there is no seal here: the test year is loaded,
    because this is the one authorised look at it (DECISIONS D21.6, D21.10).
    The only cut-off is the hard end at 2026-07-31, which keeps the test set
    exactly one calendar year (D13).
    """
    series = {}
    rows_seen = 0
    rows_after_end = 0
    for start, end in CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_EGLC_{start}_{end}.json"
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

    The D14 pairing rule: the routine :50 report belongs to the hour it is
    nearest to, and only if it is within 15 minutes of it. So EGLC's 11:50
    report is the observation for 12:00. Anything further off is dropped and
    counted.
    """
    series = {}
    reports_at_12 = 0
    reports_after_end = 0
    no_temp = 0
    outside_15min = 0

    for start, end in CHUNKS:
        path = RAW / f"iem_asos_EGLC_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
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
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[nearest.date()] = float(raw)

    return series, reports_at_12, reports_after_end, no_temp, outside_15min


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
    """Check this script against DECISIONS D21, and against session 05's code.

    Two separate checks, because they answer two different questions.
    1. Does what this script is about to run match the written lock? Checked
       against D21_LOCK above, value by value.
    2. Is the machinery the same machinery session 05 used? Checked by reading
       scripts/session05_model.py and comparing it with this file.
    """
    line("PART 0 - checking this script against the lock (DECISIONS D21)")

    sub("check 1: every value D21 fixes, against what this script will use")
    actual = {
        "target hour (D21.1)":            TARGET_HOUR,
        "train start (D21.5)":            TRAIN_START,
        "train end (D21.5)":              TRAIN_END,
        "test start (D21.6)":             TEST_START,
        "test end (D21.6)":               TEST_END,
        "features (D21.3)":               FEATURE_NAMES,
        "objective (D21.4)":              LGB_PARAMS["objective"],
        "n_estimators (D21.4)":           LGB_PARAMS["n_estimators"],
        "learning_rate (D21.4)":          LGB_PARAMS["learning_rate"],
        "num_leaves (D21.4)":             LGB_PARAMS["num_leaves"],
        "min_child_samples (D21.4)":      LGB_PARAMS["min_child_samples"],
        "subsample (D21.4)":              LGB_PARAMS["subsample"],
        "colsample_bytree (D21.4)":       LGB_PARAMS["colsample_bytree"],
        "reg_alpha (D21.4)":              LGB_PARAMS["reg_alpha"],
        "reg_lambda (D21.4)":             LGB_PARAMS["reg_lambda"],
        "random_state (D21.4)":           LGB_PARAMS["random_state"],
        "n_jobs (D21.4)":                 LGB_PARAMS["n_jobs"],
        "deterministic (D21.4)":          LGB_PARAMS["deterministic"],
        "force_row_wise (D21.4)":         LGB_PARAMS["force_row_wise"],
        "verbose (D21.4)":                LGB_PARAMS["verbose"],
        "pairing window minutes (D21.7)": 15,
        "climatology half window (D21.8)": CLIM_HALF_WINDOW_DAYS,
    }
    print(f"    {'what D21 fixes':<34} {'D21 says':<22} {'this run':<22} match?")
    mismatches = 0
    for k, want in D21_LOCK.items():
        got = actual[k]
        ok = got == want
        if not ok:
            mismatches += 1
        print(f"    {k:<34} {str(want):<22} {str(got):<22} "
              f"{'yes' if ok else 'NO - MISMATCH'}")
    print(f"    values that do not match D21: {mismatches}")
    assert mismatches == 0, "this script does not match the D21 lock - STOP"
    print("    (The 15-minute pairing window is the literal in load_obs_12z")
    print("     below. Check 2d prints that function's only difference from")
    print("     session 05's, so it can be seen that the 15 minutes is")
    print("     untouched.)")

    sub("check 2a: model settings, session 05 against this session")
    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 07':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}")
    assert n_diff == 0, "the model settings drifted from session 05 - STOP"

    sub("check 2b: the constants that must not have moved")
    for c in ["TARGET_HOUR", "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES",
              "GAP_START", "GAP_END", "INNER_START", "INNER_END",
              "VALID_START", "VALID_END"]:
        a = top_level(old, c)
        b = top_level(new, c)
        print(f"    {c:<24} {str(a):<34} {'same' if a == b else 'DIFFERS'}")

    sub("check 2c: the code that must be character-identical, and is")
    print("    Compared character for character with session 05.")
    identical = True
    for name in ["all_days", "year_fraction", "features", "mae", "describe"]:
        a = func_source(old_src, old, name)
        b = func_source(new_src, new, name)
        if a != b:
            identical = False
        print(f"    {name + '()':<26} "
              f"{'identical' if a == b else 'DIFFERS - NOT EXPECTED'}")
    assert identical, "shared code drifted from session 05 - STOP (D21.11)"

    sub("check 2d: the three functions that DO differ, each shown in full")
    print("    Nothing is hidden: every diff is printed so the changes can be")
    print("    read rather than taken on trust.")
    for old_name, new_name, why in (
            ("load_forecast_12z", "load_forecast_12z",
             "the seal on the test year is lifted - the whole point of this\n"
             "    session (D21.6, D21.10). A hard end at 2026-07-31 replaces"
             " it."),
            ("load_obs_12z", "load_obs_12z",
             "the same change, on the observation side. The 15-minute pairing\n"
             "    rule (D14, D21.7) is not touched."),
            ("climatology_from_inner", "climatology_from_training",
             "renamed, because it is now fitted on the full training window\n"
             "    (D21.5, D21.8). The arithmetic is untouched.")):
        print()
        print(f"    {new_name}() - {why}")
        a = func_source(old_src, old, old_name).splitlines()
        b = func_source(new_src, new, new_name).splitlines()
        for d in difflib.unified_diff(a, b, "session05", "session07",
                                      lineterm="", n=1):
            print(f"      {d}")
    print()
    print("    Everything else in this script is new: it scores the test year")
    print("    instead of the validation year, which is what D21 asks for.")


# ------------------------------------------------------------------ part A

def join():
    line("PART A - the join at 12:00 UTC, both windows (D21.6, D21.7)")

    print(f"target hour: {TARGET_HOUR:02d}:00 UTC (SPEC 4.1, D21.1)")
    print("pairing rule: the routine :50 report nearest the hour, and only if")
    print("              within 15 minutes of it (DECISIONS D14, D21.7). In")
    print("              practice the 11:50 report is the observation for 12:00.")
    print()
    print("THE TEST YEAR IS OPENED HERE, for the first and only time (D21.10).")
    print("The two 2026 raw chunk files are read for the first time in this")
    print("project. Sessions 04 and 05 never opened them.")

    fc, fc_rows, fc_after = load_forecast_12z()
    obs, ob_rows, ob_after, ob_no_temp, ob_far = load_obs_12z()

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
    print("             'no obs'  = no usable :50 observation within 15 min.")
    print("             A day can fail on more than one reason, so the reason")
    print("             columns can add up to more than 'drop'.")
    print("    Nothing was filled in (SPEC 2.2, D21.7).")

    train, test = built["train"], built["test"]
    inner, valid = built["inner"], built["valid"]

    sub("reconciliation: does the training window add up? (D21.11)")
    print("    The training window is inner-training plus the validation year,")
    print("    which sessions 04 and 05 counted separately. Those published")
    print("    counts must add up to this session's training count, or")
    print("    something has drifted and this session must stop.")
    print(f"    session 04/05 inner-training kept rows (F12): 1,205")
    print(f"    session 04/05 validation kept rows (F12)    :   364")
    print(f"    published total                              : 1,569")
    print(f"    this session, training window kept rows      : {len(train):,}")
    print(f"    this session, of which dated <= {INNER_END} : {len(inner):,}")
    print(f"    this session, of which dated >= {VALID_START} : {len(valid):,}")
    ok = len(train) == 1569 and len(inner) == 1205 and len(valid) == 364
    print(f"    reconciles: {'YES' if ok else 'NO - STOP AND RAISE (D21.11)'}")
    assert ok, "training-window row counts do not match F12 - STOP (D21.11)"

    sub("the F8 forecast gap, for the record (Q10)")
    gap_days = [d for d in all_days(GAP_START, GAP_END)]
    kept_dates = {r["date"] for r in train}
    print(f"    gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END}), all inside training")
    print(f"    of those, dropped here: "
          f"{sum(1 for d in gap_days if d not in kept_dates)}")

    sub("THE TEST-YEAR DROP COUNT (D21.7)")
    t_kept = {r["date"] for r in test}
    t_dropped = [d for d in all_days(TEST_START, TEST_END) if d not in t_kept]
    print(f"    test-year calendar days : {len(all_days(TEST_START, TEST_END)):,}")
    print(f"    paired rows kept        : {len(test):,}")
    print(f"    days dropped            : {len(t_dropped):,}")
    if not t_dropped:
        print("    (no test-year day was dropped)")
    for d in t_dropped:
        why = []
        if d not in fc:
            why.append("no forecast row")
        elif fc[d] is None:
            why.append("forecast null")
        if d not in obs:
            why.append("no usable observation")
        print(f"      {d}  ({', '.join(why)})")
    print("    Every drop is named. Nothing was filled (SPEC 2.2).")

    sub("shape check: first and last kept row of each window")
    for label, rows in (("training", train), ("test year", test)):
        print(f"    {label:<10} {rows[0]['date']} -> {rows[-1]['date']}   "
              f"{len(rows):,} rows")

    return train, test, obs


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
    mean-bias figure. All three see only 2021-03-24 to 2025-07-31 (D21.5,
    D21.8, SPEC 2.1c).
    """
    line("PART B - fit on the FULL training window only (D21.5, D21.8)")

    print("Everything fitted in this session is fitted here, on the training")
    print("window, and on nothing else: the model, the climatology baseline and")
    print("the mean-bias figure. The test year plays no part in any fit.")

    x_tr = features(train)
    y_tr = np.array([r["resid"] for r in train], dtype=float)

    sub("the model")
    print(f"    rows fitted on : {len(x_tr):,}  "
          f"({train[0]['date']} to {train[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (D19, D21.3)")
    print("    target         : residual, observed minus forecast (SPEC 4.2,")
    print("                     D21.2). The model never predicts temperature.")
    print("    settings (locked in D21.4, nothing tuned this session):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_tr, y_tr)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    sub("the mean-bias figure (D21.8)")
    mean_bias = float(np.mean(y_tr))
    print(f"    mean training-window bias (observed - forecast): "
          f"{mean_bias:+.4f} degC")
    print(f"    over {len(y_tr):,} training days. The mean-bias reference is")
    print("    the raw forecast plus this one constant, and nothing else.")
    print(f"    raw GFS MAE on the training window (in sample): "
          f"{mae(y_tr):.3f} degC")

    sub("the climatology baseline (D21.8, SPEC 2.1c)")
    print(f"    seasonal average of the OBSERVED temperature, from")
    print(f"    training-window days only, +/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print("    measured around the circle so late December and early January")
    print("    are neighbours.")
    clim = climatology_from_training(train)

    return model, mean_bias, clim, x_tr, y_tr


# ------------------------------------------------------------------ part C

def score_test_year(test, obs_all, model, mean_bias, clim):
    line("PART C - THE SEALED TEST (D21.6, D21.8, D21.9)")

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
    print(f"    date range                                    : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print("    Persistence needs yesterday's 12:00 observation, a past-only")
    print("    value (SPEC 2.1d). For the first test day, 2025-08-01,")
    print("    'yesterday' is 2025-07-31, which sits in the training window.")
    print("    That is a past observation, so it is legal and it is used -")
    print("    written down in D21.8 in advance so it is not mistaken for")
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

    sub(f"TEST-YEAR MAE, {len(common):,} common days "
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
    line("PART D - THE VERDICT against the frozen bar (SPEC 5.3, D21.9)")

    print("The bar, frozen before any model existed and unchanged since:")
    print("  stage 1 passes if the corrected forecast has a LOWER MAE than")
    print("  BOTH raw GFS AND persistence, over the held-out test year.")
    print("It is qualitative. There is no numeric margin and there never will")
    print("be one (SPEC 5.3, DECISIONS D22). Climatology and the mean-bias")
    print("reference are reported but do not decide pass or fail (D23).")

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
        banner = ["STAGE 1 PASSES.",
                  "The corrected forecast beats both raw GFS and persistence",
                  "over the held-out test year, on mean absolute error."]
    else:
        banner = ["STAGE 1 DOES NOT PASS.",
                  "The corrected forecast does not beat both raw GFS and",
                  "persistence over the held-out test year.",
                  "This is an honest finding (SPEC 2.4), not a reason to",
                  "re-run or to tune."]
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

def compare_with_session05(common, methods, model, pred_resid, x_tr, y_tr):
    line("PART E - the test number beside session 05's validation number")

    print("A DIFFERENCE IS EXPECTED AND IS NOT A PROBLEM (D21.5). Three things")
    print("differ between the two columns below:")
    print("  1. a different year of weather - the validation year 2024-08-01 to")
    print("     2025-07-31, against the test year 2025-08-01 to 2026-07-31;")
    print("  2. a model fitted on about 20% more data - the full training")
    print("     window here, inner-training only in session 05;")
    print("  3. therefore climatology and the mean-bias figure differ too.")
    print("The recipe is identical. Session 05's figures are quoted from")
    print("notes/session-05-check-output.txt and DECISIONS F15.")

    sub("MAE, side by side (different years - context, not a like-for-like)")
    print(f"    {'method':<22} {'s05 valid':>10} {'s07 test':>10} "
          f"{'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = S05_VALIDATION_MAE[name]
        print(f"    {name:<22} {then:>10.3f} {now:>10.3f} {now - then:>+11.3f}")
    print(f"    days scored            {S05_VALIDATION_DAYS:>10,} "
          f"{len(common):>10,}")
    print()
    print("    Read the raw GFS row first. It says how hard the two years were")
    print("    for GFS in the first place, which is the context every other")
    print("    row has to be read against.")

    sub("the margin over raw GFS, which is the comparable quantity")
    for label, ref, ml in (
            ("session 05, validation year",
             S05_VALIDATION_MAE["Raw GFS"], S05_VALIDATION_MAE["ML-corrected"]),
            ("session 07, sealed test year",
             mae(methods["Raw GFS"]), mae(methods["ML-corrected"]))):
        print(f"    {label:<30} {ref - ml:+.3f} degC "
              f"({100 * (ref - ml) / ref:+.1f}%)")
    print("    Margins are more comparable than raw MAE figures, because they")
    print("    divide out how hard the year was. They are still two different")
    print("    years, so this is a sense check, not a measurement.")

    sub("per season, session 05 validation against session 07 test")
    print(f"    {'season':<12} {'s05 raw':>8} {'s05 ML':>8} {'s05 chg':>8}  "
          f"{'s07 raw':>8} {'s07 ML':>8} {'s07 chg':>8}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        _, s05_raw, s05_ml = S05_SEASON[label]
        print(f"    {label:<12} {s05_raw:>8.3f} {s05_ml:>8.3f} "
              f"{s05_ml - s05_raw:>+8.3f}  {raw_s:>8.3f} {ml_s:>8.3f} "
              f"{ml_s - raw_s:>+8.3f}")
    print("    'chg' is the corrected MAE minus raw GFS MAE for that season.")

    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>13} {'gain share':>11} {'splits':>8}  "
          f"{'s05 share':>10} {'s05 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s05_share, s05_splits = S05_IMPORTANCE[n]
        print(f"    {n:<18} {g:>13.1f} {share:>10.1f}% {s:>8,}  "
              f"{s05_share:>9.1f}% {s05_splits:>11,}")
    print("    Both inputs are used and neither is ignored, which is what the")
    print("    F13 bias picture predicts: the bias depends on both how warm it")
    print("    is and what time of year it is. The split counts are higher than")
    print("    session 05's because there are more training rows to split on.")

    sub("in-sample check only, training window (NOT a result)")
    in_pred = model.predict(x_tr)
    print(f"    raw GFS MAE on the training window      : {mae(y_tr):.3f} degC")
    print(f"    ML-corrected MAE on the training window : "
          f"{mae(y_tr - in_pred):.3f} degC")
    print(f"    session 05, same figure on inner-training: "
          f"{S05_INSAMPLE_ML:.3f} degC")
    print("    A model always looks better on the data it was fitted to, so")
    print("    this proves nothing about performance. It is here only so the")
    print("    number is not a surprise later.")

    sub("the correction the model actually applied over the test year")
    describe(pred_resid, "predicted residual added to the forecast")
    print("    Session 05's corrections over its validation year, for scale:")
    print("    mean -0.057, st dev 0.720, range -1.8 to +1.8 degC (F15).")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 07 - THE SEALED-TEST EVALUATION. ONE LOOK. THE RESULT STANDS.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC at EGLC (SPEC 4.1, D21.1)")
    print(f"training      : {TRAIN_START} to {TRAIN_END}   (D13, D21.5)")
    print(f"SEALED TEST   : {TEST_START} to {TEST_END}   (D13, D21.6)")
    print(f"nothing after : {HARD_END}")
    print()
    print("This session executes DECISIONS D21 and decides nothing. Nothing is")
    print("tuned, searched, swapped or re-run. If anything did not fit the D21")
    print("record, the run would stop and go back to the owner (D21.11).")

    prove_it_matches_the_lock()
    train, test, obs_all = join()
    model, mean_bias, clim, x_tr, y_tr = fit_on_training(train)
    common, methods, pred_resid = score_test_year(
        test, obs_all, model, mean_bias, clim)
    passed, ml = judge_the_bar(common, methods)
    compare_with_session05(common, methods, model, pred_resid, x_tr, y_tr)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). Nothing was")
    print("committed. The test year was opened once, the locked method ran")
    print("once, and the number above is the result of record (D21.10).")
    print()
    print(f"STAGE 1: {'PASSED' if passed else 'DID NOT PASS'}   "
          f"ML-corrected test-year MAE = {ml:.3f} degC against raw GFS "
          f"{mae(methods['Raw GFS']):.3f} and persistence "
          f"{mae(methods['Persistence']):.3f}")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
