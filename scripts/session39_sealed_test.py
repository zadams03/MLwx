"""Session 39 Task 2: the FROZEN sealed-test script for the 5-feature GRIB
recipe (DECISIONS D48). Written and verified in session 39; not run against
sealed data in session 39, because the sealed-year GRIB feature file this
script reads does not exist yet -- pulling it is session 40's own job.

ONE JOB, done once per airport in session 40: refit the 3-feature and
5-feature models on the FULL training window (D48.7), open each airport's
sealed test year for the first time (D48.8), score raw GFS (GRIB),
persistence, 3-feature and 5-feature on the same common days, and judge the
D48.11 bar. Nothing here is decided at run time -- every setting, feature,
window and constant is exactly D48's.

Deliberate deviation from the project's usual script shape: every earlier
session-3x script calls main() unconditionally at the bottom of the file.
This one guards it behind `if __name__ == "__main__":` on purpose, so that
session 39 can verify the script parses and imports cleanly (exercising the
LightGBM/libomp workaround, numpy, and every function definition) WITHOUT
executing any logic or touching the (as yet nonexistent) sealed-year file --
exactly the "parses/imports, not a full run" check the session-39 prompt
asked for. Session 40 runs it exactly as `python scripts/session39_sealed_test.py`,
same as any other script in this project.

Self-guards (D48.12, "deviation is a stop signal"):
  - refuses to run (raises, not a silent skip) if the sealed feature file is
    missing -- expected right now, an error in session 40 if still true then;
  - asserts every training-window row loaded has target_date < SEALED_FROM;
  - asserts every sealed-year row loaded falls inside
    [SEALED_FROM, SEALED_UNTIL], and raises on any date outside that window;
  - asserts the training-row count per airport matches D48.7's reconciled
    figure (from F91's own full-window join) before fitting anything;
  - refuses CLI arguments -- the sealed test runs exactly as locked, with no
    override.
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


# ------------------------------------------------------------------ D48.2/D48.7/D48.8 constants

TRAIN_START = date(2021, 3, 24)
TRAIN_END = date(2025, 7, 31)
SEALED_FROM = date(2025, 8, 1)
SEALED_UNTIL = date(2026, 7, 31)

AIRPORTS = {  # SPEC 3.4, D48.2: station -> target hour (UTC)
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

# D48.7: expected training-row count per airport, reused verbatim from F91's
# own full-window join (session38_joined.csv). A mismatch is a stop signal.
EXPECTED_TRAIN_ROWS = {
    "EGLC": 1589,
    "LFPG": 1589,
    "DSM": 1590,
    "YSDU": 1573,
    "RNO": 1587,
}

# D48.8 (CORRECTED, session 41, F93). The ceiling is each airport's own
# GRIB-side sealed-year availability -- the count of calendar days with a
# valid paired GRIB forecast AND a valid observation (D14) -- NOT the
# existing 3-feature/Open-Meteo recipe's own published scored-day count
# (F16/F30/F47/F64/F82), which is what this constant held before session 41.
# Session 41 (F93) verified, from the real sealed-year pull (session 40) and
# the real Open-Meteo sealed-year archive, that the ORIGINAL ceiling
# compared two different stages of the SAME pipeline -- this recipe's own
# pre-persistence join count against the old recipe's post-persistence
# "days every method is scored on" count (which drops one further day
# whenever YESTERDAY's observation is missing, for the persistence rung
# only) -- not two forecast sources' actual coverage. Open-Meteo's own
# sealed-year forecast series is, in fact, equally clean (365/365 present,
# non-null, at every airport); at the pre-persistence join stage the two
# recipes match EXACTLY, row for row, at all five airports. The "extra"
# days were never a GRIB-vs-Open-Meteo coverage difference.
# These corrected figures are session 41's own verified GRIB+obs join
# counts, fixed here as a pre-registered expectation -- the same role
# EXPECTED_TRAIN_ROWS plays for the training window -- not a live
# recomputation, since session 42 reads the identical, already-pulled
# sealed feature file session 40 produced.
SEALED_ROW_CEILING = {
    "EGLC": 364,
    "LFPG": 364,
    "DSM": 365,
    "YSDU": 356,
    "RNO": 365,
}

# The IEM observation chunks spanning the training window AND the sealed
# test year. All of these already exist under data/raw/ -- the sealed-year
# ones were pulled for each airport's own already-completed sealed test
# under the existing recipe (F16/F30/F47/F64/F82). Read-only, unchanged.
OBS_CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

# D48.6: the locked LightGBM settings, identical for both fitted models.
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

TRAIN_GRIB_PATH = PROCESSED / "grib_features_v16_window.csv"
SEALED_GRIB_PATH = PROCESSED / "grib_features_sealed_window.csv"

OUT = ROOT / "notes" / "session40-sealed-test-output.txt"
SUMMARY_CSV = PROCESSED / "session40_sealed_test_summary.csv"


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


# ------------------------------------------------------------------ D48.4 features

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


# ------------------------------------------------------------------ D48.5 loading

def load_grib_features(path, date_lo, date_hi, refuse_outside_window):
    """station -> {date: {fc, cloud, wind}}. D48 self-guard: every row's date
    must fall inside [date_lo, date_hi], or this raises rather than silently
    dropping / silently proceeding.

    `temperature_grib_c` is expected to already carry the D48.3 elevation/
    lapse-rate correction, exactly as `grib_features_v16_window.csv` already
    does (session37_decode.py, F90) -- this script does not apply the
    correction itself. Session 40's sealed-year pull/decode must apply the
    same five fixed per-airport constants (D48.3) before writing
    `grib_features_sealed_window.csv`, not a freshly refit lapse rate."""
    if not path.exists():
        raise FileNotFoundError(
            f"D48 self-guard: expected GRIB feature file not found: {path}\n"
            "This is expected as of session 39 for the sealed-year file -- "
            "pulling it is session 40's own job (D48.8), not this script's. "
            "If this is the TRAINING file and it is missing, something else "
            "is wrong; stop and raise it with the owner (D48.12).")
    out = {st: {} for st in AIRPORTS}
    with open(path) as f:
        for r in csv.DictReader(f):
            st = r["station"]
            if st not in out:
                continue
            d = date.fromisoformat(r["target_date"])
            if refuse_outside_window and not (date_lo <= d <= date_hi):
                raise ValueError(
                    f"D48 self-guard: {path.name} contains a date outside "
                    f"the expected window [{date_lo}, {date_hi}]: "
                    f"{st} {d}. Refusing to run.")
            out[st][d] = {
                "fc": float(r["temperature_grib_c"]),
                "cloud": float(r["cloud_cover_grib_pct"]),
                "wind": float(r["wind_speed_grib_kmh"]),
            }
    return out


def load_obs_all(station, target_hour):
    """{date: temp} for the target hour, D14 pairing rule (SPEC 4.5),
    across the full training-plus-sealed range. Used for both the join and
    the persistence baseline's previous-day lookup."""
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
                if dt < TRAIN_START or dt > SEALED_UNTIL:
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


# ------------------------------------------------------------------ per-airport run

def run_airport(station, target_hour, results):
    line(f"{station} -- target hour {target_hour:02d}:00 UTC (SPEC 3.4, D48.2)")

    obs_full, obs_far, obs_no_temp = load_obs_all(station, target_hour)

    train_grib = load_grib_features(TRAIN_GRIB_PATH, TRAIN_START, TRAIN_END,
                                     refuse_outside_window=True)[station]
    sealed_grib = load_grib_features(SEALED_GRIB_PATH, SEALED_FROM, SEALED_UNTIL,
                                      refuse_outside_window=True)[station]

    train_rows, train_no_grib, train_no_obs = join_rows(
        train_grib, obs_full, TRAIN_START, TRAIN_END)
    test_rows, test_no_grib, test_no_obs = join_rows(
        sealed_grib, obs_full, SEALED_FROM, SEALED_UNTIL)

    for r in train_rows:
        assert r["date"] < SEALED_FROM, "D48 self-guard: a training row is inside the sealed year"
    for r in test_rows:
        assert SEALED_FROM <= r["date"] <= SEALED_UNTIL, \
            "D48 self-guard: a test row is outside the sealed year"

    sub("D48.7 -- training-row count reconciliation")
    print(f"    training rows kept : {len(train_rows)} "
          f"(no GRIB row: {train_no_grib}, no usable obs: {train_no_obs})")
    expected = EXPECTED_TRAIN_ROWS[station]
    print(f"    expected (F91, session38_joined.csv): {expected}")
    if len(train_rows) != expected:
        raise AssertionError(
            f"D48.12 STOP SIGNAL: {station} training-row count {len(train_rows)} "
            f"!= expected {expected}. Stop and raise this with the owner. "
            "Do not proceed, do not adjust the recipe to match.")
    print("    reconciled: MATCH")

    sub("D48.8 -- sealed-year row count, reported and reconciled against "
        "the CORRECTED ceiling (session 41, F93 -- GRIB+obs availability, "
        "not the old recipe's scored-day count)")
    print(f"    sealed-year rows kept : {len(test_rows)} "
          f"(no GRIB row: {test_no_grib}, no usable obs: {test_no_obs})")
    ceiling = SEALED_ROW_CEILING[station]
    print(f"    corrected ceiling -- GRIB+obs availability (F93): {ceiling}")
    if len(test_rows) > ceiling:
        raise AssertionError(
            f"D48.12 STOP SIGNAL: {station} sealed-year row count "
            f"{len(test_rows)} exceeds the corrected D48.8 ceiling "
            f"{ceiling} (F93). Stop and raise this with the owner.")
    print("    reconciled: within bound (<=)")

    x3_tr = features_3(train_rows)
    x5_tr = features_5(train_rows)
    y_tr = np.array([r["resid"] for r in train_rows], dtype=float)

    m3 = lgb.LGBMRegressor(**LGB_PARAMS)
    m3.fit(x3_tr, y_tr)
    m5 = lgb.LGBMRegressor(**LGB_PARAMS)
    m5.fit(x5_tr, y_tr)

    x3_te = features_3(test_rows)
    x5_te = features_5(test_rows)
    pred3 = m3.predict(x3_te)
    pred5 = m5.predict(x5_te)

    e_raw = [r["fc"] - r["obs"] for r in test_rows]
    e_3 = [(r["fc"] + float(pred3[i])) - r["obs"] for i, r in enumerate(test_rows)]
    e_5 = [(r["fc"] + float(pred5[i])) - r["obs"] for i, r in enumerate(test_rows)]

    common_persist = []
    no_prev = 0
    for r in test_rows:
        prev = obs_full.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        common_persist.append((r, float(prev)))
    e_persist = [p - r["obs"] for r, p in common_persist]

    raw_mae = mae(e_raw)
    f3_mae = mae(e_3)
    f5_mae = mae(e_5)
    persist_mae = mae(e_persist) if e_persist else float("nan")

    sub("D48.10 -- sealed-year MAE, four rungs")
    print(f"    Raw GFS (GRIB)  : {raw_mae:.3f}  (n={len(e_raw)})")
    print(f"    Persistence     : {persist_mae:.3f}  (n={len(e_persist)}, "
          f"dropped for no previous-day obs: {no_prev})")
    print(f"    3-feature       : {f3_mae:.3f}  (n={len(e_3)})")
    print(f"    5-feature       : {f5_mae:.3f}  (n={len(e_5)})")

    passes_raw = f5_mae < raw_mae
    passes_persist = f5_mae < persist_mae
    verdict = "PASS" if (passes_raw and passes_persist) else "FAIL"

    sub("D48.11 -- the bar: 5-feature vs raw GFS (GRIB) and persistence")
    print(f"    5-feature beats raw GFS (GRIB)?  {'YES' if passes_raw else 'no'} "
          f"({f5_mae:.3f} vs {raw_mae:.3f}, "
          f"{100 * (1 - f5_mae / raw_mae):+.1f}% skill)")
    print(f"    5-feature beats persistence?     {'YES' if passes_persist else 'no'} "
          f"({f5_mae:.3f} vs {persist_mae:.3f}, "
          f"{100 * (1 - f5_mae / persist_mae):+.1f}% skill)")
    print(f"    VERDICT: {verdict}")

    sub("5-vs-3-feature comparison (reported alongside the bar, not part of it)")
    print(f"    3-feature : {f3_mae:.3f}")
    print(f"    5-feature : {f5_mae:.3f}  "
          f"({'beats' if f5_mae < f3_mae else 'does not beat'} 3-feature, "
          f"{100 * (1 - f5_mae / f3_mae):+.1f}% skill vs 3-feature)")

    results[station] = dict(
        train_rows=len(train_rows),
        test_rows=len(test_rows),
        raw_mae=raw_mae,
        persist_mae=persist_mae,
        f3_mae=f3_mae,
        f5_mae=f5_mae,
        passes_raw=passes_raw,
        passes_persist=passes_persist,
        verdict=verdict,
    )


# ------------------------------------------------------------------ main

def main():
    if len(sys.argv) != 1:
        raise SystemExit(
            "D48 self-guard: this script takes no arguments -- the sealed "
            "test runs exactly as locked, with no override.")

    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 40 -- sealed test of the LOCKED 5-feature GRIB recipe "
         "(DECISIONS D48). ONE LOOK PER AIRPORT.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"training window : {TRAIN_START} to {TRAIN_END} (D48.7)")
    print(f"sealed test year: {SEALED_FROM} to {SEALED_UNTIL} (D48.8) -- "
          "OPENED ONCE, THIS RUN")
    print(f"model settings (D48.6, identical for both fitted models): {LGB_PARAMS}")
    print(f"3-feature set: {FEATURES_3}")
    print(f"5-feature set: {FEATURES_5}")

    results = {}
    for station, target_hour in AIRPORTS.items():
        run_airport(station, target_hour, results)

    line("Summary -- all five airports (D48.11 verdicts)")
    print(f"    {'airport':<8} {'raw GFS':>9} {'persist':>9} {'3-feat':>9} "
          f"{'5-feat':>9} {'verdict':>8}")
    n_pass = 0
    for st, r in results.items():
        n_pass += r["verdict"] == "PASS"
        print(f"    {st:<8} {r['raw_mae']:>9.3f} {r['persist_mae']:>9.3f} "
              f"{r['f3_mae']:>9.3f} {r['f5_mae']:>9.3f} {r['verdict']:>8}")
    print(f"\n    {n_pass} of {len(results)} airports PASS the D48.11 bar.")
    print("    Pre-registered expectation (D48.12, from F91): PASS at all "
          "five airports, including LFPG and RNO.")

    with open(SUMMARY_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "train_rows", "test_rows", "raw_mae",
                    "persist_mae", "f3_mae", "f5_mae", "passes_raw",
                    "passes_persist", "verdict"])
        for st, r in results.items():
            w.writerow([st, r["train_rows"], r["test_rows"],
                        f"{r['raw_mae']:.4f}", f"{r['persist_mae']:.4f}",
                        f"{r['f3_mae']:.4f}", f"{r['f5_mae']:.4f}",
                        r["passes_raw"], r["passes_persist"], r["verdict"]])
    print(f"\nWrote summary: {SUMMARY_CSV}")

    line("END")
    print("This is the one authorised look at the sealed test year for the "
          "5-feature GRIB recipe (D48.13), per airport. The result stands "
          "exactly as reported above -- no re-tuning, no re-run, no "
          "retroactive adjustment. It does not alter any airport's existing "
          "sealed-test verdict under the existing 3-feature/Open-Meteo "
          "recipe (F16/F30/F47/F64/F82).")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
