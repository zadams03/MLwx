"""Session 29: RENO'S SEALED-TEST EVALUATION. One look, and the result stands.

This script executes the method locked in DECISIONS D44. It decides nothing.
Every choice below was made in session 28, with Reno's test year still
unseen.

D44 is D39 with the airport AND the target hour swapped and nothing else
touched, so this script is session 24's sealed test (Dubbo) with the airport
and the target hour swapped and nothing else touched. PART 0 proves both of
those claims rather than asserting them.

TWO THINGS DIFFER FROM DUBBO'S TEST, NOT ONE. D44 could not say "only Reno's
own two changes against Dubbo" either: Reno changes the location AND the
target hour against every earlier lock, because 20:00 UTC is local standard
noon at Reno, not 02:00 (D42, F74). That cost was accepted on purpose and in
advance, when the fifth airport was opened and then switched (D40, D42). A
Reno result answers "does the recipe travel to a mountain/terrain-affected
airport with a near-constant, persistently positive bias"; it must NOT be
quoted as the controlled, location-only comparison EGLC and CDG make between
them.

UNLIKE DUBBO, RENO'S TEST-YEAR PREDICTION IS CLEAN ON BOTH SIDES, NOT BOUNDED.
D39.7 could only bound Dubbo's test-year loss as a count (9 observation-side
losses) without naming dates in advance. D44.7 predicts a clean 365 of 365
paired rows AND 365 of 365 scored days - the cleanest test-year prediction of
any airport so far (F75, F77). A count other than 365/365 on either side is a
D44.11 stop signal, checked explicitly below.

RENO'S REHEARSAL WAS A LOSS, NOT A WIN - THE FIRST IN THE PROJECT (F80). D44.9
and D44.12 both record, in advance, that raw GFS is the half of the bar most
likely to fail here, and that a near-constant-bias / overfit pattern (F79,
F80, F81) is the pre-recorded expected reason if the sealed test also comes
back negative. Nothing about the recipe below is changed because of that.

What it does, in D44's own order:
- D44.5  refits the locked model on Reno's FULL training window,
         2021-03-24 to 2025-07-31 (Reno's inner-training and Reno's
         validation year recombined, 1,203 + 365 = 1,568 rows). Everything
         fitted is fitted on this and nothing else: the model, the
         climatology baseline, the mean-bias figure.
- D44.6  opens Reno's test year, 2025-08-01 to 2026-07-31, for the first
         and only time. The 2026 RNO raw chunk file's test-year rows are
         opened here for the first time in this project. Nothing after
         2026-07-31 is used.
- D44.7  pairs with the D14 rule, reports the drop counts on both sides, and
         RECONCILES both the paired-row count AND the scored-day count
         against the prediction D44.7 wrote down before the look. Nothing is
         filled, ever (SPEC 2.2).
- D44.8  scores five methods on the same set of test days.
- D44.9  judges the frozen bar: does the corrected forecast beat BOTH raw
         GFS and persistence on mean absolute error?

Reads only from data/raw/. Never writes to data/raw/.

RENO'S SEAL IS NOW OPENED, ON PURPOSE, ONCE. Session 25 sampled Reno only to
candidate-comparison depth, session 26 counted its structure without reading
a test-year value (explicitly asserting no date on or after 2025-08-01 ever
reached a table), and session 27's rehearsal stayed on the validation side.
This session is the single authorised look (D44.10). Nothing is tuned,
searched, swapped or re-run. Whatever comes out is reported straight - a
failure is an honest, EXPECTED finding here (SPEC 2.4, D44.12), not something
to fix by trying again.

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

# THE TWO THINGS THAT CHANGE FOR RENO (DECISIONS D40, D42, D44.1): the
# location, and the target hour. Nothing else in this file differs from
# Dubbo's sealed test.
STATION = "RNO"                       # IEM's own station id, not an ICAO code
AIRPORT = "RNO"                       # Reno, Nevada (SPEC 3.4)

TARGET_HOUR = 20                      # 20:00 UTC = local standard noon (D42, F74)

# The full training window (DECISIONS D13, D44.5). This is Reno's
# inner-training plus Reno's validation year recombined - validation has
# done its job now the method is locked.
TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)

# Reno's sealed test year (DECISIONS D13, D44.6). Opened once, here.
TEST_START = date(2025, 8, 1)
TEST_END = date(2026, 7, 31)

# Hard wall. Nothing after the test year is used, which keeps the test set
# exactly one calendar year (DECISIONS D13, D44.6).
HARD_END = TEST_END

# The two sub-periods of the training window used in session 27 (DECISIONS
# D18). Kept here for reporting only - so the training-window row counts can
# be reconciled against the published session 27 counts. Nothing is fitted
# separately on them this session.
INNER_START = date(2021, 3, 24)
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# All six chunk files. The test-year rows of the 2026 RNO file are included
# for the first time - they have never been opened by any session before
# this one (D44.6).
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),     # test year, second half
]

# The one gap in the forecast series. Found at EGLC (F8), LFPG (F22), DSM
# (F38), Dubbo (F57) and again at Reno, hour for hour (F75). For reporting
# only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Exactly the session 05 settings, unchanged (DECISIONS D44.4,
# which is D39.4, which is D35.4, which is D31.4, which is D21.4). Nothing
# is tuned, searched or varied here - explicitly despite the rehearsal loss
# (D44.11).
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
# the locked settings and the shared machinery come from; session24_test.py
# is Dubbo's sealed test, the same job at the previous airport and the one
# D44 is written as "D39 with the airport and hour swapped" against.
PREV_SCRIPT = ROOT / "scripts" / "session05_model.py"
SIBLING_TEST_SCRIPT = ROOT / "scripts" / "session24_test.py"

# What DECISIONS D44 says this session must run. Written out as data so the
# script can check itself against the lock rather than the reader having to
# trust the prose. Every line below is quoted from D44.
D44_LOCK = {
    "airport (D44.1)":                "RNO",
    "target hour (D44.1)":            20,
    "train start (D44.5)":            date(2021, 3, 24),
    "train end (D44.5)":              date(2025, 7, 31),
    "test start (D44.6)":             date(2025, 8, 1),
    "test end (D44.6)":               date(2026, 7, 31),
    "features (D44.3)":               ["forecast_temp_c", "season_sin",
                                       "season_cos"],
    "objective (D44.4)":              "regression_l1",
    "n_estimators (D44.4)":           300,
    "learning_rate (D44.4)":          0.05,
    "num_leaves (D44.4)":             15,
    "min_child_samples (D44.4)":      40,
    "subsample (D44.4)":              1.0,
    "colsample_bytree (D44.4)":       1.0,
    "reg_alpha (D44.4)":              0.0,
    "reg_lambda (D44.4)":             0.0,
    "random_state (D44.4)":           42,
    "n_jobs (D44.4)":                 1,
    "deterministic (D44.4)":          True,
    "force_row_wise (D44.4)":         True,
    "verbose (D44.4)":                -1,
    "pairing window minutes (D44.7)": 15,
    "climatology half window (D44.8)": 7.5,
}

# ---- what D44.5 predicted the training refit would hold, BEFORE the look ---
# Written down in session 28 from session 27's join (F78), which itself
# matched session 26's gap map (F77) exactly. Reconciled, not accepted.
EXPECT_TRAIN_ROWS = 1568              # F78: 1,203 inner-training + 365 valid
EXPECT_INNER_ROWS = 1203              # F78
EXPECT_VALID_ROWS = 365               # F78

# ---- what D44.7 predicted the test year would cost, BEFORE the look --------
# Written down in session 28 from session 26's gap map (F75, F77). These are
# expectations to RECONCILE against, not numbers to accept. A paired-row or
# scored-day count other than 365 is a D44.11 stop signal. UNLIKE DUBBO,
# D44.7 explicitly DOES predict a scored-day count too, because F77 found no
# forecast-gap and no observation-side loss anywhere near the test year - the
# cleanest test-year prediction of any airport so far.
EXPECT_TEST_FCGAP_DAYS = 0            # F75, F77: no forecast gap in test year
EXPECT_TEST_OFFHOUR_DAYS = 0          # F76, F77: zero off-hour reports, ever
EXPECT_TEST_NOREPORT_DAYS = 0         # F77: no observation-side loss expected
EXPECT_TEST_NOTEMP_DAYS = 0           # F77 names no such cause in the test year
EXPECT_TEST_PAIRED_ROWS = 365         # F77: 365 - 0 observation-side losses
EXPECT_TEST_SCORED_DAYS = 365         # F77: no persistence-lookback loss expected

# ---- what session 27 published for Reno's rehearsal (F78, F79, F80) --------
# Session 27's published Reno validation figures, from
# notes/session-27-check-output.txt and DECISIONS F78-F81. Quoted for the
# comparison in PART E. They are a DIFFERENT year and a model fitted on
# about 30% less data, so they are context, not a target (D44.5).
S27_VALIDATION_MAE = {
    "Raw GFS":             1.493,
    "Persistence":         2.756,
    "Climatology":         3.774,
    "Mean-bias reference": 1.524,
    "ML-corrected":        1.499,
}
S27_VALIDATION_DAYS = 365             # common scored days, F80 (0 drop to persist.)
S27_VALID_PAIRED_ROWS = 365           # F77/F78: paired rows before the persist. drop
S27_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 2.431, 2.275),
    "spring MAM": (92, 1.255, 1.233),
    "summer JJA": (92, 0.807, 0.919),
    "autumn SON": (91, 1.500, 1.586),
}
S27_IMPORTANCE = {                    # feature -> (gain share %, splits)
    "forecast_temp_c": (40.4, 1842),
    "season_sin":      (35.7, 1173),
    "season_cos":      (23.9, 1185),
}
S27_INSAMPLE_ML = 1.004               # Reno inner-training MAE, session 27
S27_BETTER_PCT = 47.1                 # days closer than raw GFS, session 27 (lowest of five)
S27_MEAN_BIAS = 0.4921                # mean Reno inner-training bias, F79/F80

# D44.12's near-constant-bias / overfit watch-item, all measured on Reno's
# VALIDATION year in session 27 (F79, F80, F81) and written into the lock
# BEFORE this look. Quoted in PART G so that any inspection after the test
# is against numbers written down in advance.
F79_WARMER_PCT = 67.7                 # station warmer than forecast, inner-training
F79_MEAN_ABS_BIAS = 1.390             # mean |bias|, inner-training
F79_SEASON_MEAN_ABS_BIAS = {          # Northern-calendar labels
    "winter DJF": 1.850,
    "spring MAM": 1.484,
    "summer JJA": 1.053,
    "autumn SON": 1.263,
}
F80_MARGIN_VS_RAWGFS_PCT = -0.4       # rehearsal margin, corrected vs raw GFS
F80_MARGIN_VS_MEANBIAS_PCT = 1.7      # rehearsal margin, corrected vs mean-bias ref
F80_INSAMPLE_IMPROVEMENT_PCT = 27.8   # (1.390 - 1.004) / 1.390, in-sample only

# EGLC's stage 1 sealed test (F16), CDG's stage 2 sealed test (F30), DSM's
# stage 2 sealed test (F47) and Dubbo's stage 2 sealed test (F64), quoted for
# PART F. Each airport is judged on its own data (SPEC 5.0), so these are
# context and NOT targets Reno has to reach (D44.9).
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

DUBBO_TEST_MAE = {
    "Raw GFS":             1.251,
    "Persistence":         2.669,
    "Climatology":         3.143,
    "Mean-bias reference": 1.238,
    "ML-corrected":        1.210,
}
DUBBO_TEST_DAYS = 347
DUBBO_TEST_SEASON = {                 # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (83, 1.325, 1.330),
    "spring MAM": (90, 1.010, 0.972),
    "summer JJA": (90, 1.194, 1.199),
    "autumn SON": (84, 1.498, 1.359),
}
DUBBO_TEST_IMPORTANCE = {             # feature -> (gain share %, splits)
    "forecast_temp_c": (45.3, 1560),
    "season_sin":      (30.3, 1480),
    "season_cos":      (24.4, 1160),
}
DUBBO_TEST_BETTER_PCT = 52.4          # days closer than raw GFS, session 24
DUBBO_TEST_BETTER_N = 182
DUBBO_TRAIN_ROWS = 1553
DUBBO_VALID_MARGIN = 0.114            # session 22 validation margin, raw GFS
DUBBO_TEST_MARGIN = 0.041             # session 24 test margin, raw GFS
DUBBO_TEST_MEAN_BIAS = -0.1914
DUBBO_SEASONS_HELPED = 2

SEASONS = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
           ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]

OUT = ROOT / "notes" / "session-29-check-output.txt"


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
    """Return {date: forecast_temp_or_None} for 20:00 UTC, up to the hard end.

    Unlike session 27 there is no seal here: Reno's test year is loaded,
    because this is the one authorised look at it (DECISIONS D44.6, D44.10).
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
    """Return {date: observed_temp} for the 20:00 UTC hour, up to the hard end.

    The D14 pairing rule: the routine report belongs to the hour it is
    nearest to, and only if it is within 15 minutes of it. At Reno the
    routine report is stamped 5 minutes before the hour (F76: `:55`, zero
    off-hour reports in five years), so the 20:00 report is served by the
    19:55 report - a steady 5-minute offset, the same shape DSM's `:54`
    reporting gave, only one minute closer. Anything more than 15 minutes
    off is dropped and counted.

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
    """The D19 minimal feature set: forecast temperature, and season as sin/cos.

    Season is encoded as the sine and cosine of the position in the year so
    that 31 December sits next to 1 January instead of at the opposite end of
    a number line. Hour of day is not a feature - the hour is fixed at that
    airport's target hour, 20:00 UTC at Reno.
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
    """Check this script against DECISIONS D44, and against the two scripts it
    has to agree with.

    Three checks, because they answer three different questions.
    1. Does what this script is about to run match the written lock? Checked
       against D44_LOCK above, value by value.
    2. Is the machinery the same machinery session 05 locked? Checked by
       reading scripts/session05_model.py and comparing it with this file.
    3. Is this the same sealed test session 24 ran at the previous airport?
       Checked by reading scripts/session24_test.py and comparing. Exactly
       one constant should differ - TARGET_HOUR - and that one is D42.
    """
    line("PART 0 - checking this script against the lock (DECISIONS D44)")

    sub("check 1: every value D44 fixes, against what this script will use")
    actual = {
        "airport (D44.1)":                STATION,
        "target hour (D44.1)":            TARGET_HOUR,
        "train start (D44.5)":            TRAIN_START,
        "train end (D44.5)":              TRAIN_END,
        "test start (D44.6)":             TEST_START,
        "test end (D44.6)":               TEST_END,
        "features (D44.3)":               FEATURE_NAMES,
        "objective (D44.4)":              LGB_PARAMS["objective"],
        "n_estimators (D44.4)":           LGB_PARAMS["n_estimators"],
        "learning_rate (D44.4)":          LGB_PARAMS["learning_rate"],
        "num_leaves (D44.4)":             LGB_PARAMS["num_leaves"],
        "min_child_samples (D44.4)":      LGB_PARAMS["min_child_samples"],
        "subsample (D44.4)":              LGB_PARAMS["subsample"],
        "colsample_bytree (D44.4)":       LGB_PARAMS["colsample_bytree"],
        "reg_alpha (D44.4)":              LGB_PARAMS["reg_alpha"],
        "reg_lambda (D44.4)":             LGB_PARAMS["reg_lambda"],
        "random_state (D44.4)":           LGB_PARAMS["random_state"],
        "n_jobs (D44.4)":                 LGB_PARAMS["n_jobs"],
        "deterministic (D44.4)":          LGB_PARAMS["deterministic"],
        "force_row_wise (D44.4)":         LGB_PARAMS["force_row_wise"],
        "verbose (D44.4)":                LGB_PARAMS["verbose"],
        "pairing window minutes (D44.7)": 15,
        "climatology half window (D44.8)": CLIM_HALF_WINDOW_DAYS,
    }
    print(f"    {'what D44 fixes':<34} {'D44 says':<22} {'this run':<22} match?")
    mismatches = 0
    for k, want in D44_LOCK.items():
        got = actual[k]
        ok = got == want
        if not ok:
            mismatches += 1
        print(f"    {k:<34} {str(want):<22} {str(got):<22} "
              f"{'yes' if ok else 'NO - MISMATCH'}")
    print(f"    values checked: {len(D44_LOCK)}")
    print(f"    values that do not match D44: {mismatches}")
    assert mismatches == 0, "this script does not match the D44 lock - STOP"
    print("    (The 15-minute pairing window is the literal in")
    print("     load_obs_target_hour below. Check 3d prints that function's")
    print("     differences from session 24's, so it can be seen that the")
    print("     15 minutes is untouched.)")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    s24_src = SIBLING_TEST_SCRIPT.read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)
    s24 = ast.parse(s24_src)

    sub("check 2a: model settings, session 05 against this session")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 05':<22} {'session 29':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}   (D44.4 requires 0)")
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
    assert identical, "shared code drifted from session 05 - STOP (D44.11)"
    print("    features() is handled separately below: its text differs from")
    print("    session 05's by docstring lines naming the fixed hour, and its")
    print("    executable code is compared with docstrings stripped out.")

    sub("check 3a: model settings, session 24 (Dubbo test) against this session")
    s24_p = top_level(s24, "LGB_PARAMS")
    keys = list(s24_p) + [k for k in new_p if k not in s24_p]
    n_diff = 0
    for k in keys:
        if s24_p.get(k, "<absent>") != new_p.get(k, "<absent>"):
            n_diff += 1
    print(f"    settings compared: {len(keys)}")
    print(f"    settings that differ from Dubbo's sealed test: {n_diff}")
    assert n_diff == 0, "settings differ from session 24 - STOP (D44.11)"

    sub("check 3b: the constants, session 24 (Dubbo) against session 29 (Reno)")
    print("    Exactly one constant should differ: TARGET_HOUR, 2 -> 20, which")
    print("    is D42 and nothing else. The split dates are shared by every")
    print("    airport (SPEC 4.3), so they must be identical.")
    print(f"    {'constant':<24} {'session 24 (Dubbo)':<34} "
          f"{'session 29 (Reno)':<20} same?")
    differing = []
    for c in ["TARGET_HOUR", "TRAIN_START", "TRAIN_END", "TEST_START",
              "TEST_END", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]:
        a = top_level(s24, c)
        b = top_level(new, c)
        if a != b:
            differing.append(c)
        print(f"    {c:<24} {str(a)[:33]:<34} "
              f"{(str(b)[:19] if a != b else ''):<20} "
              f"{'yes' if a == b else 'NO - DIFFERS'}")
    print(f"    constants that differ: {len(differing)}  {differing}")
    assert differing == ["TARGET_HOUR"], \
        "something other than the target hour differs from session 24 - STOP"

    sub("check 3c: session 29 against session 24, function by function")
    print("    This is the 'the airport and the hour changed, and nothing")
    print("    else' claim, checked in code rather than argued. Every")
    print("    function is compared character for character with Dubbo's")
    print("    sealed test script.")
    for name in ["all_days", "year_fraction", "mae", "describe",
                 "_literal", "top_level", "func_source",
                 "climatology_from_training", "fit_on_training"]:
        a = func_source(s24_src, s24, name)
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
         "docstring lines: the sentence naming the fixed hour says 20:00 UTC\n"
         "    at Reno instead of 02:00 (D42). No executable line differs -\n"
         "    proved below with docstrings stripped out."),
        ("load_forecast_target_hour", "load_forecast_target_hour",
         "the docstring's session number and airport name. The file-name\n"
         "    template already uses the STATION variable, so the executable\n"
         "    code is unchanged."),
        ("load_obs_target_hour", "load_obs_target_hour",
         "the docstring: Reno reports 5 minutes BEFORE the hour (:55), where\n"
         "    Dubbo reports ON the hour (:00). The D14 rule, the 15-minute\n"
         "    tolerance and the near-target bookkeeping are all unchanged -\n"
         "    proved below with docstrings stripped out."),
        ("fit_on_training", "fit_on_training",
         "printed labels only - D39 references become D44 references and\n"
         "    the airport is named. Every fitted quantity is computed by the\n"
         "    same lines."),
    ]
    for old_name, new_name, why in pairs:
        print()
        print(f"    {new_name}() - {why}")
        a = func_source(s24_src, s24, old_name)
        b = func_source(new_src, new, new_name)
        if a == b:
            print("      (identical after all - no diff to show)")
            continue
        for d in difflib.unified_diff(a.splitlines(), b.splitlines(),
                                      f"session24 {old_name}",
                                      f"session29 {new_name}",
                                      lineterm="", n=1):
            print(f"      {d}")

    sub("check 3e: executable code with docstrings removed")
    print("    A function whose text differs may still do exactly the same")
    print("    thing. This strips the docstring and the name and compares")
    print("    what is left, against session 24's.")
    for name in ["all_days", "year_fraction", "features", "mae", "describe",
                 "climatology_from_training", "load_forecast_target_hour",
                 "load_obs_target_hour"]:
        a = func_code_shape(s24_src, s24, name)
        b = func_code_shape(new_src, new, name)
        print(f"    {name + '()':<28} "
              f"{'IDENTICAL' if a == b else 'different - see the diff above'}")
    print("    Every loader is expected IDENTICAL here: the pairing itself -")
    print("    nearest report, 15-minute tolerance, drop and count - and the")
    print("    file-name template are unchanged; only the docstrings differ.")


# ------------------------------------------------------------------ part A

def join():
    line(f"PART A - the join at {TARGET_HOUR:02d}:00 UTC, both windows "
         f"(D44.6, D44.7)")

    print(f"airport     : {AIRPORT} - Reno, Nevada (SPEC 3.4, D44.1)")
    print(f"target hour : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1, D42, D44.1) -")
    print("              local standard noon at Reno, NOT 12:00, 18:00 or")
    print("              02:00 UTC. Daylight saving is deliberately ignored,")
    print("              so the clock reads 12:00 PST in winter and 13:00")
    print("              PDT in summer either way (D42).")
    print("pairing rule: the routine report nearest the hour, and only if")
    print("              within 15 minutes of it (DECISIONS D14, D44.7). At")
    print("              Reno the routine report is stamped 5 minutes before")
    print("              the hour (F76), so 20:00 UTC is served by the")
    print("              19:55 report - a steady 5-minute offset.")
    print()
    print("RENO'S TEST YEAR IS OPENED HERE, for the first and only time")
    print("(D44.10). The test-year rows of the 2026 RNO raw chunk file are")
    print("read for the first time in this project. Sessions 25, 26 and 27")
    print("never opened them.")

    fc, fc_rows, fc_after = load_forecast_target_hour()
    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_target = \
        load_obs_target_hour()

    sub("what was loaded")
    print(f"    forecast chunk files opened : {len(CHUNKS)} "
          f"(all six, including the 2026 file's test-year rows)")
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
    print("    F76 and F78 predicted a steady -5 minutes on every kept day,")
    print("    with zero off-hour reports in five years. So the pairing at")
    print("    Reno is never a matter of choosing the nearer of two reports -")
    print("    the target-hour report either exists or it does not.")
    ambiguous = sum(1 for recs in near_target.values()
                    if len([r for r in recs
                            if abs(r[0]) <= 15 and r[1] is not None]) > 1)
    print(f"    days with MORE THAN ONE report inside D14's 15-minute window: "
          f"{ambiguous:,}")
    print("    So the pairing is essentially never ambiguous at Reno either.")

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
    print("    Nothing was filled in (SPEC 2.2, D44.7).")

    train, test = built["train"], built["test"]
    inner, valid = built["inner"], built["valid"]

    sub("reconciliation 1: does the training window add up? (D44.5, D44.11)")
    print("    The training window is Reno's inner-training plus Reno's")
    print("    validation year, which session 27 counted separately. Those")
    print("    published counts must add up to this session's training")
    print("    count, or something has drifted and this session must stop.")
    print(f"    session 27 inner-training kept rows (F78): {EXPECT_INNER_ROWS:,}")
    print(f"    session 27 validation kept rows (F78)    :   {EXPECT_VALID_ROWS:,}")
    print(f"    published total                          : {EXPECT_TRAIN_ROWS:,}")
    print(f"    this session, training window kept rows  : {len(train):,}")
    print(f"    this session, of which dated <= {INNER_END} : {len(inner):,}")
    print(f"    this session, of which dated >= {VALID_START} : {len(valid):,}")
    ok_train = (len(train) == EXPECT_TRAIN_ROWS
                and len(inner) == EXPECT_INNER_ROWS
                and len(valid) == EXPECT_VALID_ROWS)
    print(f"    reconciles: {'YES' if ok_train else 'NO - STOP AND RAISE (D44.11)'}")
    print(f"    (1,568, not 1,553 like Dubbo: Reno's 20:00 target falls AFTER")
    print(f"     the gap's last missing hour, 11:00 UTC, the same shape EGLC,")
    print(f"     LFPG and DSM share, so it loses 20 gap days, not 21. D44.5,")
    print(f"     F75, F77, F78.)")

    sub("the F75/F77 forecast gap, for the record")
    gap_days = all_days(GAP_START, GAP_END)
    kept_dates = {r["date"] for r in train}
    print(f"    gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END}), all inside training")
    print(f"    of those, dropped here: "
          f"{sum(1 for d in gap_days if d not in kept_dates)}")
    print(f"    (20, matching EGLC/LFPG/DSM rather than Dubbo's 21: Reno's")
    print(f"     20:00 target falls AFTER the gap's last missing hour,")
    print(f"     2024-01-19 11:00 UTC, so that date already carries a value")
    print(f"     and survives - F75, F77.)")

    # ------------------------------------------------- the test-year drop count
    sub("THE TEST-YEAR DROP COUNT (D44.7) - every date named, both causes")
    t_days = all_days(TEST_START, TEST_END)
    t_kept = {r["date"] for r in test}
    t_dropped = [d for d in t_days if d not in t_kept]
    print(f"    test-year calendar days : {len(t_days):,}")
    print(f"    paired rows kept        : {len(test):,}")
    print(f"    days dropped            : {len(t_dropped):,}")
    print("    UNLIKE DUBBO, D44.7 predicted this WOULD be zero - Reno's own")
    print("    gap map (F75, F77) found no forecast-gap day and no")
    print("    observation-side loss anywhere near the test year, and F76")
    print("    found zero off-hour reports in Reno's whole five-year record.")
    print("    Any date named below is a surprise against that prediction.")

    # Sort each dropped day into exactly one of the four causes F77's
    # prediction was built from. "Near the target hour" means the report's
    # nearest whole hour is 20:00, the same framing session 26 used.
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
    if not t_dropped:
        print("      (none - every test-year day paired cleanly)")
    print("    Every drop, if any, is named. Nothing was filled (SPEC 2.2).")

    sub("reconciliation 2: THE PAIRED-ROW COUNT AGAINST D44.7's ADVANCE "
        "PREDICTION")
    print("    D44.7 wrote these numbers down in session 28, from session 26's")
    print("    gap map, BEFORE Reno's test year was opened. A prediction made")
    print("    before the look is a stronger check than a count made after it.")
    print("    A count that will not reconcile is a D44.11 stop signal.")
    print()
    print(f"    {'cause':<52} {'predicted':>9} {'actual':>7}  verdict")
    checks = [
        ("forecast-gap days in the test year (F75, F77)",
         EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)),
        ("days lost to an off-hour-only report (F76, F77)",
         EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)),
        ("days lost to no report near the 20:00 hour (F77)",
         EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)),
        ("days lost to a report in place with no temperature",
         EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)),
        ("paired rows expected (F77)", EXPECT_TEST_PAIRED_ROWS, len(test)),
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

    Built from training-window days only (SPEC 2.1c, D44.8). For a given
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
    the mean-bias figure. All three see only Reno 2021-03-24 to
    2025-07-31 (D44.5, D44.8, SPEC 2.1c).
    """
    line("PART B - fit on Reno's FULL training window only (D44.5, D44.8)")

    print("Everything fitted in this session is fitted here, on Reno's")
    print("training window, and on nothing else: the model, the climatology")
    print("baseline and the mean-bias figure. The test year plays no part in")
    print("any fit.")

    x_tr = features(train)
    y_tr = np.array([r["resid"] for r in train], dtype=float)

    sub("the model")
    print(f"    rows fitted on : {len(x_tr):,}  "
          f"({train[0]['date']} to {train[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (D19, D44.3)")
    print("    target         : residual, observed minus forecast (SPEC 4.2,")
    print("                     D44.2). The model never predicts temperature.")
    print("    settings (locked in D44.4, nothing tuned this session, despite")
    print("    the rehearsal loss - D44.11):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_tr, y_tr)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    sub("the mean-bias figure (D44.8)")
    mean_bias = float(np.mean(y_tr))
    print(f"    mean training-window bias (observed - forecast): "
          f"{mean_bias:+.4f} degC")
    print(f"    over {len(y_tr):,} training days. The mean-bias reference is")
    print("    the raw forecast plus this one constant, and nothing else.")
    print(f"    raw GFS MAE on the training window (in sample): "
          f"{mae(y_tr):.3f} degC")
    print(f"    session 27's inner-training figure was {S27_MEAN_BIAS:+.4f} degC")
    print(f"    (F79/F80). EGLC's constant was {EGLC_TEST_MEAN_BIAS:+.4f} (F16),")
    print(f"    CDG's {CDG_TEST_MEAN_BIAS:+.4f} (F30), DSM's "
          f"{DSM_TEST_MEAN_BIAS:+.4f} (F47) and Dubbo's "
          f"{DUBBO_TEST_MEAN_BIAS:+.4f} (F64).")
    print("    Reno's is the first POSITIVE training-window constant of the")
    print("    five - the station runs warmer than GFS on average, not colder.")

    sub("the climatology baseline (D44.8, SPEC 2.1c)")
    print("    seasonal average of the OBSERVED temperature at Reno, from")
    print(f"    training-window days only, +/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print("    measured around the circle so late December and early January")
    print("    are neighbours.")
    clim = climatology_from_training(train)

    return model, mean_bias, clim, x_tr, y_tr


# ------------------------------------------------------------------ part C

def score_test_year(test, obs_all, model, mean_bias, clim):
    line("PART C - THE SEALED TEST AT RENO (D44.6, D44.8, D44.9)")

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
    ok_scored = len(common) == EXPECT_TEST_SCORED_DAYS
    print(f"    D44.7 predicted this would be {EXPECT_TEST_SCORED_DAYS} - "
          f"{'MATCHES' if ok_scored else 'SURPRISE (D44.11 stop signal)'}")
    print(f"    date range                                    : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print(f"    Persistence needs yesterday's {TARGET_HOUR}:00 observation, a")
    print("    past-only value (SPEC 2.1d). For the first test day,")
    print("    2025-08-01, 'yesterday' is 2025-07-31, which sits in the")
    print("    training window and is not one of F78's named observation-")
    print("    side losses. That is a past observation, so it is legal and")
    print("    it is used - written down in D44.8 in advance so it is not")
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

    sub(f"RENO TEST-YEAR MAE, {len(common):,} common days "
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
    line("PART D - THE VERDICT against the frozen bar (SPEC 5.3, 5.0, D44.9)")

    print("The bar, frozen before any model existed and unchanged since:")
    print("  an airport passes if the corrected forecast has a LOWER MAE than")
    print("  BOTH raw GFS AND persistence, over that airport's held-out test")
    print("  year. Stage 2 is each further individual airport put to that bar,")
    print("  one at a time; Reno is the airport in it now.")
    print("It is qualitative. There is no numeric margin and there never will")
    print("be one (SPEC 5.3, DECISIONS D22). Climatology and the mean-bias")
    print("reference are reported but do not decide pass or fail (D23).")
    print("The bar is judged once per airport, on that airport's own data")
    print("(SPEC 5.0). EGLC's, CDG's, DSM's and Dubbo's passes do not excuse")
    print("a Reno failure, and Reno is measured against Reno's own raw GFS")
    print("and Reno's own persistence only.")
    print("D44 recorded, in advance, that raw GFS is the half of the bar most")
    print("likely to fail here, given session 27's rehearsal loss (F80).")

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
        banner = ["RENO PASSES.",
                  "At Reno the corrected forecast beats both raw GFS and",
                  "persistence over the held-out test year, on mean absolute",
                  "error. This is despite session 27's negative rehearsal -",
                  "a difference D18 exists precisely to allow for, and D44.10",
                  "named as possible without licensing any change either way."]
    else:
        banner = ["RENO DOES NOT PASS.",
                  "At Reno the corrected forecast does not beat both raw GFS",
                  "and persistence over the held-out test year.",
                  "This is an honest, EXPECTED finding (SPEC 2.4, D44.9,",
                  "D44.12) - not a bug and not a reason to re-run or tune.",
                  "D44.12's near-constant-bias / overfit pattern is the",
                  "pre-recorded expected reason; PART G looks at it, as",
                  "description only."]
    width = 70
    print()
    print("    " + "*" * width)
    for text in banner:
        print("    *  " + text.ljust(width - 6) + " *")
    print("    " + "*" * width)

    sub("the size of the margin, stated plainly (D22)")
    print("    D22 requires the margin to be reported prominently, so that a")
    print("    technical pass by a hair reads as what it is, and so does a")
    print("    technical failure.")
    raw = mae(methods["Raw GFS"])
    per = mae(methods["Persistence"])
    print(f"    margin over raw GFS     : {raw - ml:+.3f} degC "
          f"({100 * (raw - ml) / raw:+.1f}% of raw GFS MAE)")
    print(f"    margin over persistence : {per - ml:+.3f} degC "
          f"({100 * (per - ml) / per:+.1f}% of persistence MAE)")
    print()
    print("    D44.8 said in advance which half of the bar binds at Reno:")
    print("    persistence is far weaker than raw GFS there (2.756 against")
    print("    1.493 on the rehearsal, F80), so THE RAW-GFS MARGIN IS THE ONE")
    print("    THAT DECIDES THE VERDICT IN PRACTICE. Both halves are still")
    print("    required by the bar.")
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
    print("    structure' from 'the model found an offset'. On the rehearsal")
    print("    (F80) this margin was the thinnest of any airport's, +1.7%.")
    if ml < mb:
        print("    -> It is beaten, so there is structure in the correction.")
    else:
        print("    -> It is NOT beaten, so the correction is doing no better")
        print("       than a single constant offset would have done.")
    if mb < raw:
        print("    Note: the mean-bias reference is BETTER than raw GFS here.")
        print("    On the rehearsal (F80) it was WORSE than raw GFS (1.524")
        print("    against 1.493) - unlike EGLC, DSM and Dubbo and more like")
        print("    CDG. This line says what the test year did.")
    else:
        print("    Note: the mean-bias reference is WORSE than raw GFS here,")
        print("    matching what the rehearsal found (F80: 1.524 against")
        print("    1.493) - the constant offset was not enough there either.")

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
    print("    Winter is the season D44.12 names as the first place to look")
    print("    if the result behaves oddly - it was Reno's worst-bias season")
    print("    (F79) and the rehearsal's only clear winning season (F80).")
    print("    The headline verdict above is judged on the whole year, not")
    print("    season by season (SPEC 5.3).")

    return passed, ml


# ------------------------------------------------------------------ part E

def compare_with_session27(common, methods, model, pred_resid, x_tr, y_tr):
    line("PART E - the test number beside session 27's Reno rehearsal")

    print("A DIFFERENCE IS EXPECTED AND IS NOT A PROBLEM (D44.5). Three things")
    print("differ between the two columns below:")
    print("  1. a different year of weather - the validation year 2024-08-01 to")
    print("     2025-07-31, against the test year 2025-08-01 to 2026-07-31;")
    print("  2. a model fitted on about 30% more data - Reno's full training")
    print("     window here (1,568 rows), Reno's inner-training only in")
    print("     session 27 (1,203 rows);")
    print("  3. therefore climatology and the mean-bias figure differ too.")
    print("The recipe is identical. Session 27's figures are quoted from")
    print("notes/session-27-check-output.txt and DECISIONS F80.")
    print()
    print("GIVEN F80's FINDING THAT RENO'S IN-SAMPLE GAIN DID NOT SURVIVE TO")
    print("VALIDATION (overfitting a near-constant signal, F81), D44.5 named")
    print("the direction of this shift as genuinely unpredictable in advance -")
    print("unlike the four passed airports, where the same move never flipped")
    print("a pass to a fail or back.")

    sub("MAE, side by side (different years - context, not a like-for-like)")
    print(f"    {'method':<22} {'s27 valid':>10} {'s29 test':>10} "
          f"{'difference':>11}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        now = mae(methods[name])
        then = S27_VALIDATION_MAE[name]
        print(f"    {name:<22} {then:>10.3f} {now:>10.3f} {now - then:>+11.3f}")
    print(f"    days scored            {S27_VALIDATION_DAYS:>10,} "
          f"{len(common):>10,}")
    print()
    print("    Read the raw GFS row first. It says how hard the two years were")
    print("    for GFS in the first place, which is the context every other")
    print("    row has to be read against.")

    sub("the margin over raw GFS, which is the comparable quantity")
    for label, ref, ml in (
            ("session 27, validation year",
             S27_VALIDATION_MAE["Raw GFS"], S27_VALIDATION_MAE["ML-corrected"]),
            ("session 29, sealed test year",
             mae(methods["Raw GFS"]), mae(methods["ML-corrected"]))):
        print(f"    {label:<30} {ref - ml:+.3f} degC "
              f"({100 * (ref - ml) / ref:+.1f}%)")
    print("    Margins are more comparable than raw MAE figures, because they")
    print("    divide out how hard the year was. They are still two different")
    print("    years, so this is a sense check, not a measurement.")

    sub("per season, session 27 validation against session 29 test")
    print(f"    {'season':<12} {'s27 raw':>8} {'s27 ML':>8} {'s27 chg':>8}  "
          f"{'s29 raw':>8} {'s29 ML':>8} {'s29 chg':>8}")
    for label, months in SEASONS:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw_s = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        ml_s = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        _, s27_raw, s27_ml = S27_SEASON[label]
        print(f"    {label:<12} {s27_raw:>8.3f} {s27_ml:>8.3f} "
              f"{s27_ml - s27_raw:>+8.3f}  {raw_s:>8.3f} {ml_s:>8.3f} "
              f"{ml_s - raw_s:>+8.3f}")
    print("    'chg' is the corrected MAE minus raw GFS MAE for that season.")
    print("    F80 found winter the rehearsal's only clear winning season.")
    print("    This line says what the test year did in the same season.")

    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>13} {'gain share':>11} {'splits':>8}  "
          f"{'s27 share':>10} {'s27 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s27_share, s27_splits = S27_IMPORTANCE[n]
        print(f"    {n:<18} {g:>13.1f} {share:>10.1f}% {s:>8,}  "
              f"{s27_share:>9.1f}% {s27_splits:>11,}")
    print("    Both inputs are used and neither is ignored. Session 27 found")
    print("    forecast temperature carrying the largest share, season_sin")
    print("    second (F80).")

    sub("in-sample check only, training window (NOT a result)")
    in_pred = model.predict(x_tr)
    print(f"    raw GFS MAE on the training window      : {mae(y_tr):.3f} degC")
    print(f"    ML-corrected MAE on the training window : "
          f"{mae(y_tr - in_pred):.3f} degC")
    print(f"    session 27, same figure on inner-training: "
          f"{S27_INSAMPLE_ML:.3f} degC")
    print("    A model always looks better on the data it was fitted to, so")
    print("    this proves nothing about performance. It is here only so the")
    print("    number is not a surprise later. F80/F81 already flagged the")
    print("    gap between this figure and the rehearsal's out-of-sample")
    print("    result as the largest of any airport - PART G returns to it.")

    sub("the correction the model actually applied over Reno's test year")
    describe(pred_resid, "predicted residual added to the forecast")
    print("    Session 27's corrections over Reno's validation year, for")
    print("    scale, are in notes/session-27-check-output.txt.")


# ------------------------------------------------------------------ part F

def compare_with_prior_airports(common, methods, model):
    line("PART F - how the recipe travelled: Reno beside EGLC (F16), "
         "CDG (F30), DSM (F47) and Dubbo (F64)")

    print("EGLC's figures are session 07's sealed test (F16), CDG's are")
    print("session 13's (F30), DSM's are session 18's (F47) and Dubbo's are")
    print("session 24's (F64), quoted from their notes files.")
    print()
    print("READ THIS AS CONTEXT, NOT AS A COMPARISON OF LIKE WITH LIKE. SPEC")
    print("5.0 judges each airport on its own data. Cautions, all written")
    print("down before this look:")
    print("  1. Reno changes the LOCATION AND THE TARGET HOUR against every")
    print("     earlier airport (D42, SPEC 4.1) - the same honest caveat")
    print("     D33/D37 attach to DSM and Dubbo.")
    print("  2. All five airports were tested on THE SAME TWELVE MONTHS,")
    print("     because D13's split dates are shared. Reno answers the")
    print("     terrain/mountain axis, not the year axis.")
    print("  3. EGLC's 16.3%, CDG's 13.5%, DSM's 6.3% and Dubbo's 3.3% are")
    print("     not targets Reno had to reach (D44.9).")
    print("  4. Reno's rehearsal (F80) was the first NEGATIVE one in the")
    print("     project (-0.4%), unlike every prior airport's positive")
    print("     rehearsal margin - so a below-zero test margin here would")
    print("     not be the surprise it would have been for the other four.")

    sub("test-year MAE, each airport on its own test year")
    print(f"    {'method':<22} {'EGLC':>9} {'CDG':>9} {'DSM':>9} "
          f"{'Dubbo':>9} {'Reno':>9}")
    for name in ["Raw GFS", "Persistence", "Climatology",
                 "Mean-bias reference", "ML-corrected"]:
        print(f"    {name:<22} {EGLC_TEST_MAE[name]:>9.3f} "
              f"{CDG_TEST_MAE[name]:>9.3f} {DSM_TEST_MAE[name]:>9.3f} "
              f"{DUBBO_TEST_MAE[name]:>9.3f} {mae(methods[name]):>9.3f}")
    print(f"    {'days scored':<22} {EGLC_TEST_DAYS:>9,} {CDG_TEST_DAYS:>9,} "
          f"{DSM_TEST_DAYS:>9,} {DUBBO_TEST_DAYS:>9,} {len(common):>9,}")
    print(f"    {'training rows fitted':<22} {EGLC_TRAIN_ROWS:>9,} "
          f"{CDG_TRAIN_ROWS:>9,} {DSM_TRAIN_ROWS:>9,} {DUBBO_TRAIN_ROWS:>9,} "
          f"{EXPECT_TRAIN_ROWS:>9,}")
    print("    All five rows are error measures, so larger is worse.")

    sub("the margin over each reference, all five airports")
    ml_now = mae(methods["ML-corrected"])
    print(f"    {'vs':<22} {'EGLC':>16} {'CDG':>16} {'DSM':>16} "
          f"{'Dubbo':>16} {'Reno':>16}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference",
                 "Climatology"]:
        m_e = EGLC_TEST_MAE[name] - EGLC_TEST_MAE["ML-corrected"]
        m_c = CDG_TEST_MAE[name] - CDG_TEST_MAE["ML-corrected"]
        m_d = DSM_TEST_MAE[name] - DSM_TEST_MAE["ML-corrected"]
        m_u = DUBBO_TEST_MAE[name] - DUBBO_TEST_MAE["ML-corrected"]
        ref_now = mae(methods[name])
        m_y = ref_now - ml_now
        print(f"    {name:<22} "
              f"{f'{100 * m_e / EGLC_TEST_MAE[name]:+.1f}%':>16} "
              f"{f'{100 * m_c / CDG_TEST_MAE[name]:+.1f}%':>16} "
              f"{f'{100 * m_d / DSM_TEST_MAE[name]:+.1f}%':>16} "
              f"{f'{100 * m_u / DUBBO_TEST_MAE[name]:+.1f}%':>16} "
              f"{f'{100 * m_y / ref_now:+.1f}%':>16}")
    print("    Percentages divide out how hard each airport's problem is, so")
    print("    they are the comparable figure across airports.")

    sub("rehearsal margin against test margin, all five airports")
    raw_now = mae(methods["Raw GFS"])
    reno_test_margin = raw_now - ml_now
    reno_valid_margin = (S27_VALIDATION_MAE["Raw GFS"]
                         - S27_VALIDATION_MAE["ML-corrected"])
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
    print(f"    {'Dubbo':<10} "
          f"{f'{DUBBO_VALID_MARGIN:+.3f} degC (8.2%)':>24} "
          f"{f'{DUBBO_TEST_MARGIN:+.3f} degC (3.3%)':>24}")
    reno_test_pct = 100 * reno_test_margin / raw_now
    reno_test_str = f"{reno_test_margin:+.3f} degC ({reno_test_pct:+.1f}%)"
    print(f"    {'Reno':<10} "
          f"{f'{reno_valid_margin:+.3f} degC (-0.4%)':>24} "
          f"{reno_test_str:>24}")
    print("    D44.10 named Reno's rehearsal margin (-0.4%) as the first")
    print("    negative one in the project, and said explicitly that a test")
    print("    result repeating OR reversing that loss should not be treated")
    print("    as a surprise either way. This line records what happened.")

    sub("per season, all five sealed tests")
    print(f"    {'season':<12} {'EGLC chg':>9} {'CDG chg':>9} {'DSM chg':>9} "
          f"{'Dubbo chg':>10} {'Reno raw':>9} {'Reno ML':>8} {'Reno chg':>9}")
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
        _, db_raw, db_ml = DUBBO_TEST_SEASON[label]
        print(f"    {label:<12} {eg_ml - eg_raw:>+9.3f} {cd_ml - cd_raw:>+9.3f} "
              f"{ds_ml - ds_raw:>+9.3f} {db_ml - db_raw:>+10.3f} "
              f"{raw_s:>9.3f} {ml_s:>8.3f} {ml_s - raw_s:>+9.3f}")
    print("    'chg' is corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse. Labels are")
    print("    Northern-calendar throughout; Reno (Northern Hemisphere) uses")
    print("    them literally, unlike Dubbo's.")

    sub("seasons where the correction helped, on the sealed test year")
    print(f"    EGLC: {EGLC_SEASONS_HELPED} of 4   CDG: {CDG_SEASONS_HELPED} "
          f"of 4   DSM: {DSM_SEASONS_HELPED} of 4   Dubbo: "
          f"{DUBBO_SEASONS_HELPED} of 4   Reno: {helped} of 4")
    print("    F80's rehearsal found Reno helped in 2 of 4 seasons (winter and")
    print("    spring), tied with Dubbo's validation rehearsal for the fewest")
    print("    of any airport so far. This line is the SAME question asked of")
    print("    the test year.")

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
    print(f"    Dubbo: closer than raw GFS on {DUBBO_TEST_BETTER_N} of "
          f"{DUBBO_TEST_DAYS:,} days ({DUBBO_TEST_BETTER_PCT:.1f}%)")
    print(f"    Reno : closer than raw GFS on {better:,} of {n:,} days "
          f"({100 * better / n:.1f}%)")
    print(f"    Reno's rehearsal win rate (F80) was 47.1% - the only one of")
    print(f"    the five below half.")

    sub("feature importances, all five sealed tests")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'EGLC gain %':>12} {'CDG gain %':>12} "
          f"{'DSM gain %':>12} {'Dubbo gain %':>13} {'Reno gain %':>12} "
          f"{'Reno splits':>12}")
    for name, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        eg_share, _ = EGLC_TEST_IMPORTANCE[name]
        cd_share, _ = CDG_TEST_IMPORTANCE[name]
        ds_share, _ = DSM_TEST_IMPORTANCE[name]
        db_share, _ = DUBBO_TEST_IMPORTANCE[name]
        print(f"    {name:<18} {eg_share:>11.1f}% {cd_share:>11.1f}% "
              f"{ds_share:>11.1f}% {db_share:>12.1f}% {share:>11.1f}% "
              f"{s:>12,}")
    print("    Gain totals depend on the data, so the shares and split counts")
    print("    are what compare meaningfully between airports.")


# ------------------------------------------------------------------ part G

def near_constant_bias_watch_item(common, methods, train):
    line("PART G - D44.12's near-constant-bias / overfit watch-item, "
         "described (NOT acted on)")

    print("D44.12 named this before the look, so that any inspection after")
    print("the test is honest: the place to look was written down before")
    print("anyone knew the result, mirroring D39.12's single-season")
    print("watch-item for Dubbo.")
    print()
    print("F79 and F80 together found, on Reno's rehearsal: the correction")
    print("lost to raw GFS outright (-0.4%); its margin over the mean-bias")
    print("reference was the thinnest of any airport (+1.7%); its day-by-day")
    print("win rate was the lowest of any airport (47.1%, below half); and")
    print("its in-sample-to-validation gap was the largest of any airport")
    print("(27.8% in-sample 'improvement' collapsing to -0.4% out-of-sample).")
    print("F79 explains the likely mechanism: Reno's bias is unusually close")
    print("to a CONSTANT - warmer than GFS in 67.7% of inner-training days")
    print("(against 45-52% elsewhere) and positive in almost every")
    print("forecast-temperature band and every season.")
    print()
    print("THIS IS A DESCRIPTION AND NOTHING ELSE. The method is locked, it")
    print("did not change, and nothing here licenses a re-run or an")
    print("adjustment (D44.10, D44.11, D44.12).")

    sub("what F79/F80 measured on the VALIDATION year, quoted from the lock")
    print(f"    station warmer than forecast, inner-training : "
          f"{F79_WARMER_PCT:.1f}% (against 45-52% at the four flat airports)")
    print(f"    mean |bias|, inner-training                  : "
          f"{F79_MEAN_ABS_BIAS:.3f} degC")
    print(f"    margin vs raw GFS, rehearsal (F80)            : "
          f"{F80_MARGIN_VS_RAWGFS_PCT:+.1f}%  (the only negative rehearsal)")
    print(f"    margin vs mean-bias reference, rehearsal (F80): "
          f"{F80_MARGIN_VS_MEANBIAS_PCT:+.1f}%  (thinnest of any airport)")
    print(f"    day-by-day win rate, rehearsal (F80)          : "
          f"{S27_BETTER_PCT:.1f}%  (the only one below half)")
    print(f"    in-sample improvement over raw GFS, training  : "
          f"{F80_INSAMPLE_IMPROVEMENT_PCT:.1f}%  "
          f"(collapsed to {F80_MARGIN_VS_RAWGFS_PCT:+.1f}% out-of-sample)")

    sub("mean |bias| by season, inner-training (F79) - winter is the outlier")
    print(f"    {'season':<12} {'mean |bias| degC':>17}")
    for label, _ in SEASONS:
        print(f"    {label:<12} {F79_SEASON_MEAN_ABS_BIAS[label]:>17.3f}")
    print("    Winter's bias is the largest of the four by a wide margin, and")
    print("    it was also the rehearsal's only clear winning season (F80) -")
    print("    the one measure that lined up with the terrain hypothesis")
    print("    (D42). D44.12 names it as the first place to look if the test")
    print("    result behaves oddly.")

    sub("the SAME four measures, on the TEST year - what actually happened")
    ml = mae(methods["ML-corrected"])
    raw = mae(methods["Raw GFS"])
    mb = mae(methods["Mean-bias reference"])
    n = len(common)
    better = sum(1 for a, b in zip(methods["ML-corrected"], methods["Raw GFS"])
                 if abs(a) < abs(b))
    test_vs_raw_pct = 100 * (raw - ml) / raw
    test_vs_mb_pct = 100 * (mb - ml) / mb
    test_win_pct = 100 * better / n
    print(f"    {'measure':<44} {'rehearsal':>12} {'test year':>12}")
    print(f"    {'margin vs raw GFS':<44} "
          f"{F80_MARGIN_VS_RAWGFS_PCT:>+11.1f}% {test_vs_raw_pct:>+11.1f}%")
    print(f"    {'margin vs mean-bias reference':<44} "
          f"{F80_MARGIN_VS_MEANBIAS_PCT:>+11.1f}% {test_vs_mb_pct:>+11.1f}%")
    print(f"    {'day-by-day win rate':<44} "
          f"{S27_BETTER_PCT:>11.1f}% {test_win_pct:>11.1f}%")
    print("    In-sample improvement is unchanged from PART E (the model is")
    print("    the same fit): "
          f"{F80_INSAMPLE_IMPROVEMENT_PCT:.1f}% in-sample against "
          f"{test_vs_raw_pct:+.1f}% here, out-of-sample.")

    sub("winter, named in advance as the first place to look")
    idx = [i for i, r in enumerate(common) if r["date"].month in (12, 1, 2)]
    raw_w = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
    ml_w = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
    _, s27_raw_w, s27_ml_w = S27_SEASON["winter DJF"]
    print(f"    {'':<20} {'rehearsal':>12} {'test year':>12}")
    print(f"    {'winter raw GFS MAE':<20} {s27_raw_w:>12.3f} {raw_w:>12.3f}")
    print(f"    {'winter ML-corr MAE':<20} {s27_ml_w:>12.3f} {ml_w:>12.3f}")
    print(f"    {'winter change':<20} {s27_ml_w - s27_raw_w:>+12.3f} "
          f"{ml_w - raw_w:>+12.3f}")
    print("    'change' is corrected MAE minus raw GFS MAE. Negative means the")
    print("    correction helped. Looking here is a description, never a")
    print("    licence to re-run or adjust anything (D44.10, D44.11).")

    sub("the worst single misses of the test year, for the record")
    ml_err = np.abs(np.array(methods["ML-corrected"]))
    raw_err = np.abs(np.array(methods["Raw GFS"]))
    idx_worst = np.argsort(-raw_err)[:5]
    print(f"    {'date':<12} {'forecast':>9} {'observed':>9} {'raw err':>9} "
          f"{'ML err':>9}")
    for i in idx_worst:
        r = common[i]
        print(f"    {str(r['date']):<12} {r['fc']:>9.2f} {r['obs']:>9.2f} "
              f"{raw_err[i]:>9.2f} {ml_err[i]:>9.2f}")
    print("    Listed because D44.12 asked for the watch-item's place to look")
    print("    to be described if the result behaved oddly. Looking is")
    print("    describing; it changes nothing.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 29 - RENO'S SEALED-TEST EVALUATION. ONE LOOK. THE RESULT "
         "STANDS.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"airport       : {AIRPORT} - Reno, Nevada (SPEC 3.4) - stage 2")
    print(f"                (D40, D42, the fifth airport)")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC at {STATION} "
          f"(SPEC 4.1, D42, D44.1)")
    print(f"training      : {TRAIN_START} to {TRAIN_END}   (D13, D44.5)")
    print(f"SEALED TEST   : {TEST_START} to {TEST_END}   (D13, D44.6)")
    print(f"nothing after : {HARD_END}")
    print()
    print("This session executes DECISIONS D44 and decides nothing. Nothing is")
    print("tuned, searched, swapped or re-run. If anything did not fit the D44")
    print("record, the run stops and goes back to the owner (D44.11).")
    print()
    print("TWO THINGS DIFFER FROM DUBBO'S TEST, NOT ONE: the location AND the")
    print("target hour (D42). Session 27's rehearsal did NOT beat raw GFS")
    print("(1.499 against 1.493, -0.4%) - the first such rehearsal result in")
    print("the project. A sealed-test failure here is an expected, legitimate")
    print("outcome, recorded in advance (D44, D44.12), not a bug.")

    prove_it_matches_the_lock()
    train, test, obs_all, reconciled = join()
    if not reconciled:
        print()
        print("!!! A COUNT DID NOT RECONCILE. D44.11 says that is a stop signal:")
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
    compare_with_session27(common, methods, model, pred_resid, x_tr, y_tr)
    compare_with_prior_airports(common, methods, model)
    near_constant_bias_watch_item(common, methods, train)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). Nothing was")
    print("committed. Reno's test year was opened once, the locked method")
    print("ran once, and the number above is the result of record (D44.10).")
    print()
    print(f"RENO: {'PASSED' if passed else 'DID NOT PASS'}   "
          f"ML-corrected test-year MAE = {ml:.3f} degC against raw GFS "
          f"{mae(methods['Raw GFS']):.3f} and persistence "
          f"{mae(methods['Persistence']):.3f}")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
