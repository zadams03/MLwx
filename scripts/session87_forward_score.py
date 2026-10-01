"""Session 87: the 2026-27 scoring script (DECISIONS D73.5, D73.6, D77.6, D78.7, D79).

It scores the frozen F122 models on a period of the 2026-27 forward test:
  D73    per airport (all six) and period: the frozen `B+D,L,R,T` model against raw
         GFS (GRIB, elevation-adjusted) and persistence (SPEC 5.3), with the plain `B`
         model and the mean-bias reference as descriptive rungs.
  D77.6  DSM, RNO and KSFO against NBM, and DSM against GFS MOS (MAV), on the days
         where the competitor value is present.

Modes (exactly one):
  --guard-check  Offline. Calls the guards only, with fixed cases, and prints each
                 outcome. No network call, no data file read.
  --gate         Offline, spent years only. Reproduces recorded results with the
                 scoring core (F119.3 at KSFO, F127.4 at DSM, RNO and KSFO), checks the
                 frozen-model plumbing without computing any error, and exercises the
                 --score writers in a temporary directory. Writes nothing under data/.
  --score        2026-27, period A or B. WRITTEN BUT NOT RUN IN SESSION 87. It reads the
                 rows file written by scripts/session86_forward_build.py and the points
                 file written by scripts/session87_forward_competitors.py, and writes
                 only new files (see the OUT_* names below). It refuses to run if any
                 exists: that is what makes each period a single look.

Where the logic comes from (copied, not imported, because importing the record scripts
runs code; the one exception is `session62_reserved_confirm`, imported read-only in
`--gate` G2 after its SHA-256 is checked, as session85_nbm_mos_comparison.py did). The
function-by-function list with line numbers is in DECISIONS F129.
  - the moving-block bootstrap: session85_nbm_mos_comparison.py l.685-718 (F125's, D75.2);
  - the F109 refit route: session85_nbm_mos_comparison.py l.156-196 and
    session62_reserved_confirm.py run_confirm() (F125.1);
  - the period days: session86_forward_build.py l.284-322;
  - the frozen-model checks: session86_forward_build.py l.1061-1101 (`plumbing`).

Prediction path (SPEC 8.8 G14, G15, G20; F122): a model's forecast is
`temperature_grib_c` plus the booster's prediction, made on a float64 array of the G15
columns in order (the first five for `B`), with no column names. Raw GFS (GRIB) is
`temperature_grib_c`. The mean-bias reference is `temperature_grib_c` plus the airport's
F122.5 constant. Persistence is the previous-day observation.

Hard limits: no row dated on or after 2027-08-01 may be scored. Nothing is written under
data/ by `--gate` or `--guard-check`.
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import math
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True

# --- making LightGBM importable on this machine (copied from
# session62_reserved_confirm.py l.89-99; see DECISIONS Q16/D24) -----------------
_SENTINEL = "MLWX_LIBOMP_PATH_SET"
if _SENTINEL not in os.environ:
    _omp = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" \
        / "site-packages" / "sklearn" / ".dylibs"
    if (_omp / "libomp.dylib").exists():
        os.environ[_SENTINEL] = "1"
        os.environ["DYLD_LIBRARY_PATH"] = \
            str(_omp) + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
        os.execv(sys.executable, [sys.executable] + sys.argv)

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
HERE = Path(__file__).resolve().parent
SPEC_FILE = ROOT / "SPEC.md"
DECISIONS_FILES = [ROOT / "DECISIONS.md", ROOT / "DECISIONS-archive.md"]
PROCESSED = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "data" / "models" / "session81"
TRAINING_SET = PROCESSED / "session81_training_set.csv"
TRAINING_SET_SHA256 = "ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a"   # F122.3
RECORD_F109 = HERE / "session62_reserved_confirm.py"
RECORD_F109_SHA256 = "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4"     # D70.2
KSFO_PRED = PROCESSED / "session78_ksfo_looks_predictions.csv"
KSFO_PRED_SHA256 = "b4b46adc266ecb5475f253e5b20d02c6505d02af2bd578426095d6ef7f8ad78e"       # F119.4
F109_GRID = PROCESSED / "session63_reserved_confirm_grid.csv"
F119_GRID = PROCESSED / "session78_ksfo_looks_grid.csv"
S85_POINTS = PROCESSED / "session85_competitor_points.csv"
S85_POINTS_SHA256 = "681802a27338d0bafddabffdf1bd6d2168b6dd39a2460e07964340445819a63e"       # F127.3
S85_NOTES = ROOT / "notes" / "session-85-output.txt"

AIRPORTS = ["EGLC", "LFPG", "DSM", "YSDU", "RNO", "SFO"]
COMP_PLAN = [("DSM", "nbm"), ("RNO", "nbm"), ("SFO", "nbm"), ("DSM", "mav")]   # D79.5's order
G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
       "pressure_tendency_3h_hpa"]                       # SPEC 8.8 G15, record order
ROW_COLS = (["station", "target_date", "target_hour"] + G15
            + ["temperature_grib_c", "obs_c", "prev_obs_c"])   # as session86_forward_build.py
POINT_COLS = ["airport", "period", "target_date", "competitor", "cycle", "lead",
              "valid_time", "value_c", "grid_lat", "grid_lon"]  # as session87_forward_competitors.py
PRED_COLS = ["station", "target_date", "obs_c", "prev_obs_c", "raw_gfs_c", "bdlrt_c", "b_c",
             "mean_bias_c", "nbm_c", "mav_c"]
SCORE_COLS = ["table", "station", "competitor", "metric", "value"]

PERIOD_A_START = dt.date(2026, 8, 1)
FORWARD_LAST_DAY = dt.date(2027, 7, 31)
FORWARD_LIMIT = dt.date(2027, 8, 1)
DAYS_AFTER_LAST = 3                                  # D78.7: observations are in

N_BOOT = 10_000                                      # F125 / D75.2
BLOCK = 7
SEED_FORWARD = 87                                    # D79.5
SEED_GATE = 85                                       # F127.4

# The 9 dates of F128's gate sample (session86_forward_build.py l.131-133), for G3.
GATE_DATES = [dt.date(2021, 4, 15), dt.date(2022, 1, 10), dt.date(2023, 7, 20),
              dt.date(2023, 10, 5), dt.date(2024, 11, 12), dt.date(2025, 2, 18),
              dt.date(2025, 9, 3), dt.date(2026, 4, 22), dt.date(2026, 7, 31)]
# F119.3's percentages (bar margins, 2 decimals): (raw GFS, persistence).
F119_MARGINS = {"A": ("11.83", "16.79"), "B": ("20.16", "19.46")}


class GuardError(Exception):
    """A guard fired. The run stops."""


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ------------------------------------------------------------------ SPEC 3.4 and the periods

def load_spec_cycles():
    """Each airport's GFS cycle hour, from SPEC 3.4's target hour column (SPEC 7.2:
    floor(H/6)*6). Nothing typed in (as session86_forward_build.py l.226-263)."""
    text = SPEC_FILE.read_text()
    block = text[text.index("**3.4 The airport table.**"):text.index("Notes on the table:")]
    header, out = None, {}
    for ln in block.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == "station code":
            header = cells
            continue
        if set(cells[0]) <= set("-") or header is None or "target hour (UTC)" not in header:
            continue
        hour = int(dict(zip(header, cells))["target hour (UTC)"].split(":")[0])
        out[cells[0]] = (hour // 6) * 6
    if list(out) != AIRPORTS:
        raise SystemExit(f"STOP: unexpected airport set {list(out)}")
    return out


def last_period_a_day(cycle_hour, first_v17):
    """Copied from session86_forward_build.py l.284-296. The last target day D whose
    forecasting cycle (floor(H/6)*6 UTC on D-1) is before the first v17 cycle. With no
    v17 (first_v17 None) it is the last day of the forward year."""
    if first_v17 is None:
        return FORWARD_LAST_DAY
    d, last = PERIOD_A_START, None
    while d < dt.date(2028, 1, 1):
        cyc_dt = dt.datetime(d.year, d.month, d.day, cycle_hour) - dt.timedelta(days=1)
        if cyc_dt >= first_v17:
            break
        last, d = d, d + dt.timedelta(days=1)
    return last


def period_range(period, cycle_hour, first_v17):
    """(first day, last day) of a period for an airport. None if the period is empty."""
    last_a = last_period_a_day(cycle_hour, first_v17)
    if period == "A":
        return None if last_a is None else (PERIOD_A_START, last_a)
    first_b = PERIOD_A_START if last_a is None else last_a + dt.timedelta(days=1)
    return None if first_b > FORWARD_LAST_DAY else (first_b, FORWARD_LAST_DAY)


def out_paths(period):
    return {
        "predictions": PROCESSED / f"forward2627_period{period}_predictions.csv",
        "scores": PROCESSED / f"forward2627_period{period}_scores.csv",
        "scores_meta": PROCESSED / f"forward2627_period{period}_scores.csv.meta.txt",
    }


def in_paths(period):
    return {"rows": PROCESSED / f"forward2627_period{period}_rows.csv",
            "points": PROCESSED / f"forward2627_period{period}_competitor_points.csv"}


def validate_request(period, first_v17, no_v17, decision, run_date, cycles, rows_sha, points_sha,
                     nbm_versions, mav_versions):
    """The --score guards, as a pure function (adapted from session86 l.299-322). The
    timing guard reads the latest last day over all six airports. An empty reasons list
    means the guards allow the run. Returns (reasons, ranges)."""
    reasons, ranges = [], {}
    if period not in ("A", "B"):
        reasons.append("needs --period A or --period B")
    if first_v17 is None and not no_v17:
        reasons.append("needs --first-v17-cycle (from a DECISIONS entry, D73.3) or --no-v17")
    if first_v17 is not None and no_v17:
        reasons.append("--first-v17-cycle and --no-v17 are exclusive")
    if period == "B" and no_v17:
        reasons.append("period B needs --first-v17-cycle: --no-v17 with --period B is refused (D73.3)")
    for val, name in ((decision, "--decision"), (rows_sha, "--rows-sha256"), (points_sha, "--points-sha256"),
                      (nbm_versions, "--nbm-versions"), (mav_versions, "--mav-versions")):
        if not val:
            reasons.append(f"needs {name}")
    if period in ("A", "B"):
        for st, cyc in cycles.items():
            rng = period_range(period, cyc, first_v17 if not no_v17 else None)
            ranges[st] = rng
            if rng is None:
                reasons.append(f"{st}: no period-{period} day")
            elif rng[1] >= FORWARD_LIMIT:
                reasons.append(f"{st}: last period-{period} target day {rng[1]} is on or after {FORWARD_LIMIT}")
        known = [r[1] for r in ranges.values() if r is not None]
        if known and run_date < max(known) + dt.timedelta(days=DAYS_AFTER_LAST):
            reasons.append(f"run date {run_date} is before the latest last day {max(known)} "
                           f"plus {DAYS_AFTER_LAST} days")
    return reasons, ranges


def check_input_file(path, label):
    """A period's input file must exist (a period-B rows file exists only after a later
    build mode made it, D79.6). Checks the path only; reads nothing."""
    if not Path(path).exists():
        raise GuardError(f"the {label} file does not exist: {path}")


def check_sha(path, want, label):
    have = sha256_file(path)
    if have != want:
        raise GuardError(f"{label} SHA-256 {have} differs from the value passed ({want})")


def check_outputs_absent(paths):
    present = [str(p) for p in paths if Path(p).exists()]
    if present:
        raise GuardError("an output file already exists: " + ", ".join(present))


def check_row_dates(dates_by_station, ranges):
    """Any row outside its airport's period range, or on or after 2027-08-01, stops the run."""
    for st, ds in dates_by_station.items():
        for d in ds:
            if d >= FORWARD_LIMIT:
                raise GuardError(f"{st}: a target date {d} is on or after {FORWARD_LIMIT}")
            rng = ranges.get(st)
            if rng is None or not (rng[0] <= d <= rng[1]):
                raise GuardError(f"{st}: target date {d} is outside its period range {rng}")


def guard_check():
    print("SESSION 87 score --guard-check (offline: no network call, no data file read)")
    cycles = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 0, "RNO": 18, "SFO": 18}
    today = dt.datetime.now(dt.timezone.utc).date()
    print(f"run date (UTC): {today}")
    ok_all = True
    full = dict(decision="D79", rows_sha="x", points_sha="y", nbm_versions="n", mav_versions="m")

    def show(label, refused, why, expect_refused, expect_text=None):
        nonlocal ok_all
        good = (refused == expect_refused) and (expect_text is None or any(expect_text in w for w in why))
        ok_all &= good
        print(f"  [{'OK ' if good else 'BAD'}] {label}: {'REFUSED' if refused else 'allowed'}"
              + (f" ({'; '.join(why)})" if why else ""))

    print("score guards (pure function; nothing is read):")
    r, _ = validate_request("A", None, False, run_date=today, cycles=cycles, **full)
    show("--score with neither --first-v17-cycle nor --no-v17", bool(r), r, True, "needs --first-v17-cycle")
    r, _ = validate_request("B", None, True, run_date=dt.date(2028, 3, 1), cycles=cycles, **full)
    show("--score --period B --no-v17", bool(r), r, True, "--no-v17 with --period B is refused")
    try:
        check_input_file(in_paths("B")["rows"], "period-B rows")
        show("--score --period B when the period-B rows file does not exist", False, [], True)
    except GuardError as e:
        show("--score --period B when the period-B rows file does not exist", True, [str(e)], True,
             "does not exist")
    r, rng = validate_request("A", dt.datetime(2026, 11, 15, 0), False, run_date=today, cycles=cycles, **full)
    print("    period-A range per airport for a first v17 cycle of 2026-11-15T00: "
          + ", ".join(f"{k} {v[0]}..{v[1]}" for k, v in rng.items()))
    show("--score whose last day + 3 days is after the run date", bool(r), r, True, "before the latest last day")
    r, _ = validate_request("A", dt.datetime(2027, 9, 1, 0), False, run_date=dt.date(2028, 3, 1), cycles=cycles,
                            **full)
    show("--score with a target date on or after 2027-08-01 (period range, simulated run date 2028-03-01)",
         bool(r), r, True, "on or after 2027-08-01")
    try:
        check_row_dates({"DSM": [dt.date(2027, 8, 1)]}, {"DSM": (PERIOD_A_START, dt.date(2027, 8, 5))})
        show("a rows-file date of 2027-08-01", False, [], True)
    except GuardError as e:
        show("a rows-file date of 2027-08-01", True, [str(e)], True, "on or after 2027-08-01")
    try:
        check_row_dates({"DSM": [dt.date(2026, 7, 31)]}, {"DSM": (PERIOD_A_START, dt.date(2026, 11, 15))})
        show("a period-A rows-file date of 2026-07-31 (wrong period)", False, [], True)
    except GuardError as e:
        show("a period-A rows-file date of 2026-07-31 (wrong period)", True, [str(e)], True, "outside")
    r, _ = validate_request("A", dt.datetime(2026, 11, 15, 0), False, run_date=dt.date(2026, 11, 18),
                            cycles=cycles, **full)
    show("positive control: period A, first v17 cycle 2026-11-15T00, run date 2026-11-18", bool(r), r, False)
    r, _ = validate_request("A", dt.datetime(2026, 11, 15, 0), False, run_date=dt.date(2026, 11, 18),
                            cycles=cycles, **{**full, "nbm_versions": ""})
    show("--score without --nbm-versions", bool(r), r, True, "needs --nbm-versions")
    print("output files and the rows-file SHA-256 (temporary directory outside the repo):")
    tmp = Path(tempfile.mkdtemp(prefix="session87_score_guard_"))
    try:
        paths = [tmp / "predictions.csv", tmp / "scores.csv"]
        try:
            check_outputs_absent(paths)
            show("no output exists", False, [], False)
        except GuardError as e:
            show("no output exists", True, [str(e)], False)
        paths[0].write_text("x")
        try:
            check_outputs_absent(paths)
            show("one output exists", False, [], True)
        except GuardError as e:
            show("one output exists", True, [str(e)], True, "already exists")
        small = tmp / "rows.csv"
        small.write_text("station\n")
        good = hashlib.sha256(small.read_bytes()).hexdigest()
        try:
            check_input_file(small, "rows")
            check_sha(small, good, "rows file")
            show("a rows file whose SHA-256 equals --rows-sha256", False, [], False)
        except GuardError as e:
            show("a rows file whose SHA-256 equals --rows-sha256", True, [str(e)], False)
        try:
            check_sha(small, "0" * 64, "rows file")
            show("a rows file whose SHA-256 differs from --rows-sha256", False, [], True)
        except GuardError as e:
            show("a rows file whose SHA-256 differs from --rows-sha256", True, [str(e)], True, "differs")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  temporary directory deleted: {not tmp.exists()}")
    print("all cases behaved as the session prompt's Step 3.3 says" if ok_all
          else "A CASE DID NOT BEHAVE: FIX THE SCRIPT")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ the frozen models (F122.5)

def read_decisions_text():
    return "\n".join(p.read_text() for p in DECISIONS_FILES if p.exists())


def load_frozen_models():
    """Checks every model file and manifest.json against F122.5 (the table in
    DECISIONS.md) and against manifest.json, then loads the boosters. Returns
    (models, mean_bias, hashes). Adapted from session86_forward_build.py l.1061-1084."""
    import json
    import lightgbm as lgb
    text = read_decisions_text()
    want_m = re.search(r"manifest\.json`, SHA-256\s+`([0-9a-f]{64})`", text).group(1)
    have_m = sha256_file(MODEL_DIR / "manifest.json")
    if have_m != want_m:
        raise GuardError(f"manifest.json SHA-256 {have_m} differs from F122.5 ({want_m})")
    block = text[text.index("**F122.5"):text.index("**F122.6")]
    table = {}
    for m in re.finditer(r"^\| (EGLC|LFPG|DSM|YSDU|RNO|KSFO \(SFO\)) \| \d+ \| `([0-9a-f]{64})` \| "
                         r"`([0-9a-f]{64})` \| (-?[0-9.]+) \|", block, re.M):
        table["SFO" if m.group(1).startswith("KSFO") else m.group(1)] = (m.group(2), m.group(3), float(m.group(4)))
    if set(table) != set(AIRPORTS):
        raise GuardError(f"F122.5 table has {sorted(table)}")
    manifest = json.load(open(MODEL_DIR / "manifest.json"))["airports"]
    models, mean_bias, hashes = {}, {}, {"manifest.json": have_m}
    for st in AIRPORTS:
        for kind, sha, fname in (("bdlrt", table[st][0], f"{st}_bdlrt.txt"), ("b", table[st][1], f"{st}_b.txt")):
            have = sha256_file(MODEL_DIR / fname)
            if have != sha or have != manifest[st][f"model_{kind}_sha256"]:
                raise GuardError(f"{fname} SHA-256 {have} differs from F122.5 or manifest.json")
            hashes[fname] = have
            models[(st, kind)] = lgb.Booster(model_file=str(MODEL_DIR / fname))
        if float(manifest[st]["mean_bias_c"]) != table[st][2]:
            raise GuardError(f"{st}: the mean-bias constant in manifest.json differs from F122.5")
        mean_bias[st] = float(manifest[st]["mean_bias_c"])
    return models, mean_bias, hashes


def g15_array(rows, cols):
    """SPEC 8.8 G15: a float64 array of the columns in order, with no column names."""
    return np.array([[float(r[c]) for c in cols] for r in rows], dtype=float).reshape(len(rows), len(cols))


def predict_correction(models, station, kind, rows):
    """The scoring script's own predict path. Returns the booster's prediction (the
    correction to temperature_grib_c), one per row."""
    cols = G15 if kind == "bdlrt" else G15[:5]
    if not rows:
        return np.array([], dtype=float)
    return np.asarray(models[(station, kind)].predict(g15_array(rows, cols)), dtype=float)


# ------------------------------------------------------------------ the scoring core

def bootstrap(rng, em, er):
    """Copied from session85_nbm_mos_comparison.py l.707-718: F125's moving-block
    bootstrap (D75.2), unchanged. em, er are absolute errors. Returns the 95% percentile
    intervals of d = mean(er) - mean(em) and skill = 100 x (1 - mean(em)/mean(er))."""
    n = len(em)
    k = math.ceil(n / BLOCK)
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, k))
    idx = (starts[:, :, None] + np.arange(BLOCK)).reshape(N_BOOT, k * BLOCK)
    idx = idx[:, :n]
    mm = em[idx].mean(axis=1)
    mr = er[idx].mean(axis=1)
    d = mr - mm
    skill = 100.0 * (1.0 - mm / mr)
    return (np.percentile(d, [2.5, 97.5]), np.percentile(skill, [2.5, 97.5]))


def pct(model_mae, base_mae):
    """D79.1: 100 x (1 - MAE(model)/MAE(baseline)) at full precision."""
    return float("nan") if not base_mae else 100.0 * (1.0 - model_mae / base_mae)


def d73_core(obs, raw, model, bmod, meanbias, pers):
    """D73.5 and D79. Arrays are aligned by day. `pers` is NaN on days with no previous-day
    observation. Raw GFS, the models and the mean-bias reference use every day; persistence
    uses the days that have a previous-day observation. PASS needs the model's MAE strictly
    lower than both raw GFS's and persistence's (D79.2). No days, or no persistence day:
    "no verdict (0 days)" (D79.3)."""
    obs, raw, model = (np.asarray(x, dtype=float) for x in (obs, raw, model))
    n = len(obs)
    has_p = np.isfinite(np.asarray(pers, dtype=float))
    out = {"n": n, "n_pers": int(has_p.sum())}
    if n == 0:
        out.update(verdict="no verdict (0 days)")
        return out
    mae = lambda f, o: float(np.mean(np.abs(np.asarray(f, dtype=float) - o)))  # noqa: E731
    out["mae_raw"], out["mae_model"] = mae(raw, obs), mae(model, obs)
    out["mae_b"] = None if bmod is None else mae(bmod, obs)
    out["mae_meanbias"] = None if meanbias is None else mae(meanbias, obs)
    out["margin_raw_pct"] = pct(out["mae_model"], out["mae_raw"])
    out["margin_raw_c"] = out["mae_raw"] - out["mae_model"]
    if out["n_pers"] == 0:
        out.update(verdict="no verdict (0 days)", mae_pers=None, margin_pers_pct=None, margin_pers_c=None)
        return out
    pv = np.asarray(pers, dtype=float)[has_p]
    out["mae_pers"] = float(np.mean(np.abs(pv - obs[has_p])))
    out["margin_pers_pct"] = pct(out["mae_model"], out["mae_pers"])      # model on every day (D73.5)
    out["margin_pers_c"] = out["mae_pers"] - out["mae_model"]
    out["verdict"] = "PASS" if (out["mae_model"] < out["mae_raw"] and out["mae_model"] < out["mae_pers"]) else "FAIL"
    return out


def d77_core(rng, obs, comp, model, raw, bmod=None):
    """D77.6 and D79. Arrays are aligned by day and hold only days where the competitor value
    is present. PASS if the model's MAE is strictly lower than the competitor's (D79.2). No
    days: "void". The intervals use F125's method (D79.5); with fewer than 7 days they are not
    computed and no draws are consumed."""
    obs, comp, model, raw = (np.asarray(x, dtype=float) for x in (obs, comp, model, raw))
    n = len(obs)
    if n == 0:
        return {"n": 0, "verdict": "void"}
    em, ec_, er = model - obs, comp - obs, raw - obs
    out = {"n": n, "mae_model": float(np.mean(np.abs(em))), "mae_comp": float(np.mean(np.abs(ec_))),
           "mae_raw": float(np.mean(np.abs(er))), "me_model": float(np.mean(em)),
           "me_comp": float(np.mean(ec_)), "me_raw": float(np.mean(er))}
    if bmod is not None:
        eb = np.asarray(bmod, dtype=float) - obs
        out["mae_b"], out["me_b"] = float(np.mean(np.abs(eb))), float(np.mean(eb))
    out["d"] = out["mae_comp"] - out["mae_model"]
    out["skill_pct"] = pct(out["mae_model"], out["mae_comp"])
    out["verdict"] = "PASS" if out["mae_model"] < out["mae_comp"] else "FAIL"
    if n >= BLOCK:
        (dl, dh), (sl, sh) = bootstrap(rng, np.abs(em), np.abs(ec_))
        out.update(d_lo=float(dl), d_hi=float(dh), skill_lo=float(sl), skill_hi=float(sh))
    else:
        out.update(d_lo=None, d_hi=None, skill_lo=None, skill_hi=None)
    return out


MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def season_label(dates):
    """D79.4: the first and last target date and the calendar months between them, for
    example "2026-08-01 to 2026-11-10 (Aug, Sep, Oct, Nov)"."""
    if not dates:
        return "no days"
    a, b = min(dates), max(dates)
    y, m, names = a.year, a.month, []
    while (y, m) <= (b.year, b.month):
        names.append(MONTHS[m - 1])
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return f"{a} to {b} ({', '.join(names)})"


def fmt(x, spec):
    return "n/a" if x is None else format(x, spec)


def d77_lines(cp_name, r):
    """The per-comparison print block, in the format session 85 printed (F127.4)."""
    cp = cp_name.upper()
    return [
        f"MAE  model {r['mae_model']:.4f}  {cp} {r['mae_comp']:.4f}  raw GFS {r['mae_raw']:.4f}",
        f"mean error (forecast - obs)  model {r['me_model']:+.4f}  {cp} {r['me_comp']:+.4f}  "
        f"raw GFS {r['me_raw']:+.4f}",
        f"d     = MAE({cp}) - MAE(model) = {r['d']:+.4f} degC   95% [{fmt(r['d_lo'], '+.4f')}, "
        f"{fmt(r['d_hi'], '+.4f')}]   wholly above zero: {'yes' if r['d_lo'] is not None and r['d_lo'] > 0 else 'no'}",
        f"skill = 1 - model/{cp} = {r['skill_pct']:+.2f}%   95% [{fmt(r['skill_lo'], '+.2f')}%, "
        f"{fmt(r['skill_hi'], '+.2f')}%]",
    ]


# ------------------------------------------------------------------ reading the inputs

def finite(s):
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def load_rows(path, ranges):
    """The build script's rows file, grouped by station and sorted by date. Stops on a missing
    column, an unknown station, a duplicate day, a non-finite value (SPEC 8.7 item 2), or a
    date outside the airport's period range."""
    by = {st: [] for st in AIRPORTS}
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        missing = [c for c in ROW_COLS if c not in (rd.fieldnames or [])]
        if missing:
            raise GuardError(f"the rows file lacks columns {missing}")
        for r in rd:
            if r["station"] not in by:
                raise GuardError(f"the rows file has an unknown station {r['station']!r}")
            row = {"station": r["station"], "date": dt.date.fromisoformat(r["target_date"])}
            for c in G15 + ["temperature_grib_c", "obs_c"]:
                v = finite(r[c])
                if v is None:
                    raise GuardError(f"{r['station']} {r['target_date']}: non-finite or missing {c}")
                row[c] = v
            row["prev_obs_c"] = finite(r["prev_obs_c"]) if r["prev_obs_c"] != "" else None
            by[r["station"]].append(row)
    check_row_dates({st: [r["date"] for r in rs] for st, rs in by.items()}, ranges)
    for st, rs in by.items():
        rs.sort(key=lambda r: r["date"])
        if len({r["date"] for r in rs}) != len(rs):
            raise GuardError(f"{st}: a duplicate target date in the rows file")
    return by


def load_points(path, ranges):
    """The competitor points file: {(airport, competitor): {date: value_c}}."""
    out = {}
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        missing = [c for c in POINT_COLS if c not in (rd.fieldnames or [])]
        if missing:
            raise GuardError(f"the points file lacks columns {missing}")
        for r in rd:
            k = (r["airport"], r["competitor"])
            if k not in COMP_PLAN:
                raise GuardError(f"the points file has an unexpected row {k}")
            d = dt.date.fromisoformat(r["target_date"])
            v = finite(r["value_c"])
            if v is None:
                raise GuardError(f"{k} {d}: non-finite value in the points file")
            if d in out.setdefault(k, {}):
                raise GuardError(f"{k} {d}: duplicate row in the points file")
            out[k][d] = v
    for (st, _), dv in out.items():
        check_row_dates({st: list(dv)}, ranges)
    return out


# ------------------------------------------------------------------ the writers (SPEC 8.7 item 5)

def write_new(path, data):
    """Exclusive create: never overwrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", newline="") as f:
        f.write(data)


def csv_text(cols, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def cell(v):
    """Floats are written with repr so they read back exactly; None is blank."""
    if v is None:
        return ""
    return repr(float(v)) if isinstance(v, float) else str(v)   # float(): numpy 2 reprs np.float64(...)


def write_score_outputs(paths, pred_rows, score_rows, meta_lines):
    """Writes the predictions file, the scores file and its .meta.txt, as new files only. `paths`
    holds the three targets, so --gate can exercise this in a temporary directory."""
    for k in ("predictions", "scores", "scores_meta"):
        if paths[k].exists():
            raise SystemExit(f"STOP: {paths[k]} already exists; not overwriting (SPEC 8.7 item 5)")
    write_new(paths["predictions"], csv_text(PRED_COLS, [[cell(r.get(c)) for c in PRED_COLS] for r in pred_rows]))
    write_new(paths["scores"], csv_text(SCORE_COLS, [[cell(v) for v in r] for r in score_rows]))
    write_new(paths["scores_meta"], "\n".join(meta_lines) + "\n")


def d73_score_rows(station, r, label):
    rows = [("d73", station, "", "label", label)]
    for k in ("n", "n_pers", "mae_raw", "mae_pers", "mae_meanbias", "mae_b", "mae_model", "margin_raw_pct",
              "margin_raw_c", "margin_pers_pct", "margin_pers_c", "verdict"):
        if k in r:
            rows.append(("d73", station, "", k, r[k]))
    return rows


def d77_score_rows(station, cp, r, label):
    rows = [("d77", station, cp, "label", label)]
    for k in ("n", "mae_model", "mae_comp", "mae_b", "mae_raw", "me_model", "me_comp", "me_raw", "me_b", "d",
              "d_lo", "d_hi", "skill_pct", "skill_lo", "skill_hi", "verdict"):
        if k in r:
            rows.append(("d77", station, cp, k, r[k]))
    return rows


# ------------------------------------------------------------------ --score (written, not run in session 87)

def build_arrays(models, mean_bias, st, rows):
    """Per-day arrays and the prediction rows for one airport."""
    raw = np.array([r["temperature_grib_c"] for r in rows], dtype=float)
    obs = np.array([r["obs_c"] for r in rows], dtype=float)
    prev = np.array([np.nan if r["prev_obs_c"] is None else r["prev_obs_c"] for r in rows], dtype=float)
    bdlrt = raw + predict_correction(models, st, "bdlrt", rows)
    b = raw + predict_correction(models, st, "b", rows)
    mb = raw + mean_bias[st]
    return dict(dates=[r["date"] for r in rows], obs=obs, prev=prev, raw=raw, bdlrt=bdlrt, b=b, mb=mb)


def run_score(args):
    cycles = load_spec_cycles()
    run_date = dt.datetime.now(dt.timezone.utc).date()
    first_v17 = dt.datetime.strptime(args.first_v17_cycle, "%Y-%m-%dT%H") if args.first_v17_cycle else None
    reasons, ranges = validate_request(args.period, first_v17, args.no_v17, args.decision, run_date, cycles,
                                       args.rows_sha256, args.points_sha256, args.nbm_versions, args.mav_versions)
    print(f"--score period {args.period}; decision {args.decision}; run date (UTC) {run_date}; "
          f"first v17 cycle {args.first_v17_cycle or 'none (--no-v17)'}")
    print("target-day range per airport: "
          + ", ".join(f"{k} {v[0]}..{v[1]}" if v else f"{k} none" for k, v in ranges.items()))
    if reasons:
        raise SystemExit("REFUSED: " + "; ".join(reasons))
    ins, outs = in_paths(args.period), out_paths(args.period)
    try:
        check_outputs_absent(list(outs.values()))
        for k, label in (("rows", "rows"), ("points", "competitor points")):
            check_input_file(ins[k], label)
        check_sha(ins["rows"], args.rows_sha256, "rows file")
        check_sha(ins["points"], args.points_sha256, "points file")
        models, mean_bias, model_hashes = load_frozen_models()     # stops before computing anything
        rows = load_rows(ins["rows"], ranges)
        points = load_points(ins["points"], ranges)
    except GuardError as e:
        raise SystemExit("REFUSED: " + str(e))
    print(f"rows file {ins['rows'].name} SHA-256 {args.rows_sha256} (equal to the value passed)")
    print(f"points file {ins['points'].name} SHA-256 {args.points_sha256} (equal to the value passed)")
    print(f"frozen models: 12 model files and manifest.json equal F122.5")
    print(f"NBM versions (from DECISIONS, verbatim): {args.nbm_versions}")
    print(f"MAV versions (from DECISIONS, verbatim): {args.mav_versions}")

    arr, pred_rows = {}, []
    for st in AIRPORTS:
        arr[st] = build_arrays(models, mean_bias, st, rows[st])
    comp_vals = {}
    for st in AIRPORTS:
        for i, d in enumerate(arr[st]["dates"]):
            pr = {"station": st, "target_date": d.isoformat(), "obs_c": arr[st]["obs"][i],
                  "prev_obs_c": None if np.isnan(arr[st]["prev"][i]) else float(arr[st]["prev"][i]),
                  "raw_gfs_c": float(arr[st]["raw"][i]), "bdlrt_c": float(arr[st]["bdlrt"][i]),
                  "b_c": float(arr[st]["b"][i]), "mean_bias_c": float(arr[st]["mb"][i])}
            pr["obs_c"] = float(pr["obs_c"])
            for cp in ("nbm", "mav"):
                pr[f"{cp}_c"] = points.get((st, cp), {}).get(d)
            pred_rows.append(pr)

    score_rows = []
    print("\n" + "=" * 78)
    print(f"D73, period {args.period}: the frozen B+D,L,R,T model against raw GFS (GRIB) and persistence")
    print("=" * 78)
    d73, margins = {}, []
    for st in AIRPORTS:
        a = arr[st]
        exp = (ranges[st][1] - ranges[st][0]).days + 1
        r = d73_core(a["obs"], a["raw"], a["bdlrt"], a["b"], a["mb"], a["prev"])
        label = season_label(a["dates"])
        d73[st] = r
        score_rows += d73_score_rows(st, r, label)
        score_rows.append(("d73", st, "", "expected_days", exp))
        print(f"\n  {st}{' (D71.5 framing applies)' if st == 'SFO' else ''}: {label}")
        print(f"    rows {r['n']} of {exp} expected; days with a previous-day observation {r['n_pers']}")
        if r["n"]:
            print(f"    MAE  raw GFS {r['mae_raw']:.4f}  persistence {fmt(r.get('mae_pers'), '.4f')}  "
                  f"mean-bias {r['mae_meanbias']:.4f}  B {r['mae_b']:.4f}  B+D,L,R,T {r['mae_model']:.4f}")
        print(f"    verdict: {r['verdict']}")
        if r["verdict"] in ("PASS", "FAIL"):
            print(f"    margin over raw GFS {r['margin_raw_pct']:+.4f}% ({r['margin_raw_c']:+.4f} degC); "
                  f"over persistence {r['margin_pers_pct']:+.4f}% ({r['margin_pers_c']:+.4f} degC)")
            margins += [(r["margin_raw_pct"], r["margin_raw_c"], st, "raw GFS (GRIB)"),
                        (r["margin_pers_pct"], r["margin_pers_c"], st, "persistence")]
    margins.sort()
    print("\n  Smallest margin first (D79.1: 100 x (1 - MAE(model)/MAE(baseline)), difference beside it):")
    for p, c, st, half in margins:
        print(f"    {st:5s} vs {half:16s} {p:+.4f}%  ({c:+.4f} degC)")
    if not margins:
        print("    no airport has a verdict")

    print("\n" + "=" * 78)
    print(f"D77.6, period {args.period}: the frozen B+D,L,R,T model against NBM and GFS MOS (MAV)")
    print("=" * 78)
    rng = np.random.default_rng(SEED_FORWARD)          # D79.5: a new generator for each period
    print(f"intervals: 7-day moving blocks, {N_BOOT:,} resamples, 95% percentile, numpy.random.default_rng"
          f"({SEED_FORWARD}); order DSM/NBM, RNO/NBM, KSFO/NBM, DSM/MAV")
    margins77 = []
    for st, cp in COMP_PLAN:
        a = arr[st]
        cv = points.get((st, cp), {})
        keep = [i for i, d in enumerate(a["dates"]) if d in cv]
        name = f"{'KSFO' if st == 'SFO' else st} vs {cp.upper()}"
        r = d77_core(rng, a["obs"][keep], [cv[a["dates"][i]] for i in keep], a["bdlrt"][keep], a["raw"][keep],
                     a["b"][keep])
        label = season_label([a["dates"][i] for i in keep])
        score_rows += d77_score_rows(st, cp, r, label)
        print(f"\n  {name}{' (D71.5 framing applies)' if st == 'SFO' else ''}: {label}")
        print(f"    D73 complete-case days {len(a['dates'])}; competitor present on {len(keep)}; "
              f"dropped {len(a['dates']) - len(keep)}")
        if r["verdict"] == "void":
            print("    verdict: void (the competitor has no value in this period; not a fail)")
            continue
        for ln in d77_lines(cp, r):
            print(f"    {ln}")
        print(f"    B MAE {r['mae_b']:.4f}, mean error {r['me_b']:+.4f}")
        print(f"    verdict: {r['verdict']}")
        print(f"    margin {r['skill_pct']:+.4f}% ({r['d']:+.4f} degC)")
        margins77.append((r["skill_pct"], r["d"], name))
    margins77.sort()
    print("\n  Smallest margin first (D79.1):")
    for p, c, name in margins77:
        print(f"    {name:16s} {p:+.4f}%  ({c:+.4f} degC)")
    if not margins77:
        print("    no comparison has a verdict")

    meta = [f"Period {args.period} scores for the 2026-27 tests (D73, D77.6, D79). Decision entry: {args.decision}.",
            f"run at (UTC): {now_utc()}", f"run date (UTC): {run_date}",
            f"first v17 cycle: {args.first_v17_cycle or 'none (--no-v17)'}",
            f"rows file SHA-256: {args.rows_sha256}", f"points file SHA-256: {args.points_sha256}",
            f"NBM versions: {args.nbm_versions}", f"MAV versions: {args.mav_versions}",
            f"python {sys.version.split()[0]}, numpy {np.__version__}", "frozen model files (F122.5):"]
    meta += [f"  {k} {v}" for k, v in model_hashes.items()]
    write_score_outputs(outs, pred_rows, score_rows, meta)
    print(f"\nwrote {outs['predictions'].name}, {outs['scores'].name} and {outs['scores_meta'].name} "
          f"under {PROCESSED.relative_to(ROOT)}/")
    return 0


# ------------------------------------------------------------------ --gate (recorded results only)

def load_ksfo_looks():
    """F119's saved predictions, by look: dates and the columns the scoring core needs."""
    out = {"A": [], "B": []}
    with open(KSFO_PRED, newline="") as f:
        for r in csv.DictReader(f):
            out[r["look"]].append(dict(
                date=dt.date.fromisoformat(r["target_date"]), obs=float(r["obs_c"]), raw=float(r["raw_gfs_c"]),
                pers=(float(r["persistence_c"]) if r["persistence_c"] != "" else float("nan")),
                mb=float(r["mean_bias_c"]), b=float(r["B_c"]), model=float(r["BDLRT_c"])))
    for k in out:
        if any(r["date"] > dt.date(2026, 7, 31) for r in out[k]):
            raise SystemExit("STOP: a KSFO prediction row is dated after 2026-07-31")
        out[k].sort(key=lambda r: r["date"])
    return out


def gate_g1():
    print("=" * 78)
    print("G1: F119.3 (KSFO, both looks) through the D73 scoring core")
    print("=" * 78)
    if sha256_file(KSFO_PRED) != KSFO_PRED_SHA256:
        raise SystemExit("STOP: the KSFO predictions SHA-256 is not F119.4's")
    print(f"  {KSFO_PRED.relative_to(ROOT)} SHA-256 {KSFO_PRED_SHA256} (F119.4: equal)")
    print("  columns used, and their source (all in that file): obs_c (observation), raw_gfs_c (raw GFS),")
    print("    persistence_c (persistence, blank on days with no previous-day observation), mean_bias_c,")
    print("    B_c (plain B), BDLRT_c (B+D,L,R,T). The core needs nothing else, so no file that")
    print("    session77_ksfo_looks.py reads is opened.")
    grid = {}
    with open(F119_GRID, newline="") as f:
        for r in csv.DictReader(f):
            if r["row_type"] == "rung":
                grid[(r["look"], r["name"])] = (r["value"], int(r["n"]))
    looks = load_ksfo_looks()
    ok_all, results = True, {}
    for lk in "AB":
        rs = looks[lk]
        r = d73_core([x["obs"] for x in rs], [x["raw"] for x in rs], [x["model"] for x in rs],
                     [x["b"] for x in rs], [x["mb"] for x in rs], [x["pers"] for x in rs])
        results[lk] = r
        print(f"\n  look {lk}: rows {r['n']}, persistence days {r['n_pers']}")
        for label, key, name, n_want in (("raw GFS", "mae_raw", "raw_gfs", r["n"]),
                                         ("persistence", "mae_pers", "persistence", r["n_pers"]),
                                         ("mean-bias", "mae_meanbias", "mean_bias", r["n"]),
                                         ("B", "mae_b", "B", r["n"]), ("B+D,L,R,T", "mae_model", "B+D,L,R,T", r["n"])):
            want, n_rec = grid[(lk, name)]
            eq = repr(float(r[key])) == repr(float(want)) and n_want == n_rec
            ok_all &= eq
            print(f"    {label:12s} recomputed {r[key]!r:<22} recorded {want:<22} n {n_want} (recorded {n_rec})  "
                  f"{'equal' if eq else 'DIFFERS'}")
        m_raw, m_pers = f"{r['margin_raw_pct']:.2f}", f"{r['margin_pers_pct']:.2f}"
        mg = (m_raw, m_pers) == F119_MARGINS[lk]
        ok_all &= mg and r["verdict"] == "PASS"
        print(f"    verdict {r['verdict']} (F119.3: PASS); margins over raw GFS {m_raw}% and over persistence "
              f"{m_pers}% (F119.3: {F119_MARGINS[lk][0]}% and {F119_MARGINS[lk][1]}%): "
              f"{'equal at 2 decimals' if mg else 'DIFFER'}")
    print(f"  G1: {'PASSED' if ok_all else 'FAILED'}")
    return ok_all, results, looks


def f109_rows(s62, stations):
    """DSM and RNO per-day rows, following run_confirm() step by step (F125.1). Copied from
    session85_nbm_mos_comparison.py l.156-196."""
    l_all, hits_l = s62.load_family("L", ["lapse_rate_t2_t850"])
    d_all, hits_d = s62.load_family("D", ["dewpoint_depression_t2m"])
    t_all, hits_t = s62.load_family("T", ["pressure_tendency_3h_hpa"])
    r_all, hits_r = s62.load_family("R", ["dswrf_2h_wm2"])
    if hits_l or hits_d or hits_t or hits_r:  # run_confirm()'s first guard
        raise AssertionError("STOP: reserved-year rows found inside the L/D/T/R source files themselves (D51).")
    base_all = s62.load_base_unfiltered()
    merged = s62.build_complete_case(base_all, l_all, d_all, t_all, r_all)
    fold = s62.CONFIRMATION_FOLD
    ts, te = fold["test_start"], fold["test_end"]
    tr_s, tr_e = fold["train_start"], fold["train_end"]
    for st in s62.AIRPORTS:  # run_confirm()'s second guard, all airports
        if sum(1 for d in merged[st] if ts <= d <= te) == 0:
            raise RuntimeError(f"STOP (D58 reserved-year feature-data gap): {st}")
    out = {}
    for st in stations:
        obs_all, _, _ = s62.load_obs_all(st, s62.AIRPORTS[st])
        train_raw = {d: r for d, r in merged[st].items() if tr_s <= d <= tr_e}
        test_raw = {d: r for d, r in merged[st].items() if ts <= d <= te}
        train_rows, _ = s62.join_obs(st, train_raw, obs_all)
        test_rows, _ = s62.join_obs(st, test_raw, obs_all)
        for r in test_rows:
            if r["date"] > dt.date(2026, 7, 31):
                raise SystemExit("STOP: a date after 2026-07-31")
        _, e_model = s62.fit_and_score(set(s62.FINAL_CODES), s62.FINAL_FEATURE_KEYS, train_rows, test_rows)
        out[st] = [dict(date=r["date"], obs=r["obs"], model=r["obs"] + em, raw=r["fc"])
                   for r, em in zip(test_rows, e_model)]
    return out


def parse_s85_notes():
    """The per-comparison lines session 85 printed (F127.4), at their printed precision."""
    text = S85_NOTES.read_text()
    text = text[text.index("Step 4: the comparison"):text.index("Summary table")]
    blocks, cur = {}, None
    for ln in text.splitlines():
        m = re.match(r"^  (DSM \(F109\)|RNO \(F109\)|KSFO look A|KSFO look B) vs (NBM|MAV)$", ln)
        if m:
            cur = (m.group(1), m.group(2).lower())
            blocks[cur] = []
        elif cur and ln.startswith("    ") and not ln.startswith("     ") and "version segments" not in ln:
            blocks[cur].append(ln.strip())
    return blocks


def gate_g2():
    print("\n" + "=" * 78)
    print("G2: F127.4 (all five rows) through the D77.6 core and the interval function")
    print("=" * 78)
    for p, want, name in ((RECORD_F109, RECORD_F109_SHA256, "session62_reserved_confirm.py (D70.2)"),
                          (KSFO_PRED, KSFO_PRED_SHA256, "the KSFO predictions (F119.4)"),
                          (S85_POINTS, S85_POINTS_SHA256, "the session 85 points (F127.3)")):
        have = sha256_file(p)
        print(f"  {p.relative_to(ROOT)} SHA-256 {have} ({name}: {'equal' if have == want else 'DIFFERS'})")
        if have != want:
            raise SystemExit(f"STOP: {p.name} differs from its recorded SHA-256")
    sys.path.insert(0, str(HERE))
    import session62_reserved_confirm as s62  # noqa: E402  (after the SHA-256 check)
    print("  DSM and RNO: refit by F125.1's route (functions imported read-only from the record script,")
    print("  run_confirm()'s steps and both guards, B+D,L,R,T only)")
    rows = {("DSM", "F109"): None, ("RNO", "F109"): None}
    fr = f109_rows(s62, ["DSM", "RNO"])
    rows[("DSM", "F109")], rows[("RNO", "F109")] = fr["DSM"], fr["RNO"]
    looks = load_ksfo_looks()
    rows[("SFO", "A")] = [dict(date=x["date"], obs=x["obs"], model=x["model"], raw=x["raw"]) for x in looks["A"]]
    rows[("SFO", "B")] = [dict(date=x["date"], obs=x["obs"], model=x["model"], raw=x["raw"]) for x in looks["B"]]
    points = {}
    with open(S85_POINTS, newline="") as f:
        for r in csv.DictReader(f):
            points.setdefault((r["airport"], r["look"], r["competitor"]), {})[dt.date.fromisoformat(r["target_date"])] \
                = float(r["value_c"])
    rec_full = {}
    with open(F109_GRID, newline="") as f:
        for r in csv.DictReader(f):
            if r["station"] in ("DSM", "RNO"):
                rec_full[(r["station"], "F109")] = (r["final_mae"], r["raw_mae"])
    with open(F119_GRID, newline="") as f:
        for r in csv.DictReader(f):
            if r["row_type"] == "rung" and r["name"] in ("B+D,L,R,T", "raw_gfs"):
                k = ("SFO", r["look"])
                cur = list(rec_full.get(k, ("", "")))
                cur[0 if r["name"] == "B+D,L,R,T" else 1] = r["value"]
                rec_full[k] = tuple(cur)
    notes = parse_s85_notes()
    order = [(("DSM", "F109"), "nbm", "DSM (F109)"), (("RNO", "F109"), "nbm", "RNO (F109)"),
             (("SFO", "A"), "nbm", "KSFO look A"), (("SFO", "B"), "nbm", "KSFO look B"),
             (("DSM", "F109"), "mav", "DSM (F109)")]
    rng = np.random.default_rng(SEED_GATE)
    ok_all, results = True, {}
    for (st, lk), cp, nname in order:
        rs = rows[(st, lk)]
        cv = points[(st, lk, cp)]
        use = [x for x in rs if x["date"] in cv]
        use.sort(key=lambda x: x["date"])
        r = d77_core(rng, [x["obs"] for x in use], [cv[x["date"]] for x in use], [x["model"] for x in use],
                     [x["raw"] for x in use])
        results[(nname, cp)] = (use, r)
        print(f"\n  {nname} vs {cp.upper()}: recorded test days {len(rs)}; competitor missing on "
              f"{len(rs) - len(use)}; n = {r['n']}")
        got = [f"recorded test days {len(rs)}; competitor missing on {len(rs) - len(use)}; n = {r['n']}"] \
            + d77_lines(cp, r)
        want = notes[(nname, cp)]
        for g, w in zip(got, want):
            eq = g == w
            ok_all &= eq
            print(f"    {'equal ' if eq else 'DIFFERS'} recomputed: {g}")
            if not eq:
                print(f"            recorded:   {w}")
        if len(got) != len(want):
            ok_all = False
            print("    DIFFERS: a different number of recorded lines")
        mfull, rfull = rec_full[(st, lk)]
        for label, val, rec in (("model MAE", r["mae_model"], mfull), ("raw GFS MAE", r["mae_raw"], rfull)):
            eq = repr(float(val)) == repr(float(rec))
            ok_all &= eq
            print(f"    {label} at full precision: recomputed {val!r} recorded {rec}: {'equal' if eq else 'DIFFERS'}")
    print("  precision used per figure: model, competitor and raw GFS MAEs at 4 decimals (session 85's print) and,")
    print("  for the model and raw GFS, at full precision against the two grid files; mean errors at 4 decimals;")
    print("  d and its interval at 4 decimals; skill and its interval at 2 decimals; n exact.")
    print(f"  G2: {'PASSED' if ok_all else 'FAILED'}")
    return ok_all, results


def gate_g3():
    print("\n" + "=" * 78)
    print("G3: frozen-model plumbing (no error is computed)")
    print("=" * 78)
    import lightgbm as lgb
    have = sha256_file(TRAINING_SET)
    print(f"  {TRAINING_SET.relative_to(ROOT)} SHA-256 {have} (F122.3: {'equal' if have == TRAINING_SET_SHA256 else 'DIFFERS'})")
    if have != TRAINING_SET_SHA256:
        raise SystemExit("STOP: the training set differs from F122.3")
    models, mean_bias, hashes = load_frozen_models()
    print(f"  12 model files and manifest.json equal F122.5 ({len(hashes)} hashes checked)")
    want_dates = set(GATE_DATES)
    by = {st: [] for st in AIRPORTS}
    with open(TRAINING_SET, newline="") as f:
        for r in csv.DictReader(f):
            d = dt.date.fromisoformat(r["target_date"])
            if d > dt.date(2026, 7, 31):
                raise SystemExit(f"STOP: training-set row dated {d}")
            if d in want_dates:
                by[r["station"]].append({"date": d, **{c: r[c] for c in G15}})
    ok_all = True
    print(f"  {'airport':8s} {'station-days':>12s} {'B+D,L,R,T max abs diff':>26s} {'B max abs diff':>18s}")
    for st in AIRPORTS:
        rows = sorted(by[st], key=lambda r: r["date"])
        worst = {}
        for kind, cols, fname in (("bdlrt", G15, f"{st}_bdlrt.txt"), ("b", G15[:5], f"{st}_b.txt")):
            own = predict_correction(models, st, kind, rows)                        # the script's own predict path
            direct = lgb.Booster(model_file=str(MODEL_DIR / fname)).predict(       # a fresh booster, called directly
                np.array([[float(r[c]) for c in cols] for r in rows], dtype=np.float64))
            worst[kind] = float(np.max(np.abs(own - np.asarray(direct))))
        ok_all &= worst["bdlrt"] == 0.0 and worst["b"] == 0.0 and len(rows) == len(GATE_DATES)
        print(f"  {st:8s} {len(rows):>12d} {worst['bdlrt']:>26.17g} {worst['b']:>18.17g}")
    print(f"  G3: {'PASSED' if ok_all else 'FAILED'}")
    return ok_all


def gate_g4(g1, g2):
    print("\n" + "=" * 78)
    print("G4: the --score writers, in a temporary directory outside the repo")
    print("=" * 78)
    _, r1, looks = g1
    _, r2 = g2
    pred_rows, score_rows = [], []
    for lk in "AB":
        for x in looks[lk]:
            pred_rows.append({"station": "SFO", "target_date": x["date"].isoformat(), "obs_c": x["obs"],
                              "prev_obs_c": None, "raw_gfs_c": x["raw"], "bdlrt_c": x["model"], "b_c": x["b"],
                              "mean_bias_c": x["mb"], "nbm_c": None, "mav_c": None})
        score_rows += d73_score_rows("SFO", r1[lk], f"KSFO look {lk} (stand-in)")
    for (nname, cp), (use, r) in r2.items():
        st = "SFO" if nname.startswith("KSFO") else nname.split(" ")[0]
        score_rows += d77_score_rows(st, cp, r, f"{nname} (stand-in)")
        for x in use[:3]:
            pred_rows.append({"station": st, "target_date": x["date"].isoformat(), "obs_c": x["obs"],
                              "prev_obs_c": None, "raw_gfs_c": x["raw"], "bdlrt_c": x["model"], "b_c": None,
                              "mean_bias_c": None, "nbm_c": None, "mav_c": None})
    tmp = Path(tempfile.mkdtemp(prefix="session87_score_gate_"))
    print(f"  temporary directory (deleted at the end): {tmp}")
    ok = True
    try:
        paths = {"predictions": tmp / "p" / "predictions.csv", "scores": tmp / "p" / "scores.csv",
                 "scores_meta": tmp / "p" / "scores.csv.meta.txt"}
        write_score_outputs(paths, pred_rows, score_rows, ["gate exercise (spent years)"])
        back_p = list(csv.DictReader(open(paths["predictions"], newline="")))
        back_s = list(csv.DictReader(open(paths["scores"], newline="")))
        eq_p = len(back_p) == len(pred_rows) and all(
            all(b[c] == cell(r.get(c)) for c in PRED_COLS) for b, r in zip(back_p, pred_rows))
        eq_p_float = all(float(b["obs_c"]) == r["obs_c"] and float(b["bdlrt_c"]) == r["bdlrt_c"]
                         for b, r in zip(back_p, pred_rows))
        eq_s = len(back_s) == len(score_rows) and all(
            [b[c] for c in SCORE_COLS] == [cell(v) for v in r] for b, r in zip(back_s, score_rows))
        eq_s_float = all(float(b["value"]) == v for b, (_, _, _, m, v) in zip(back_s, score_rows)
                         if isinstance(v, float))
        print(f"  wrote {len(pred_rows)} prediction rows and {len(score_rows)} score rows; read back equal: "
              f"predictions {eq_p} (floats exact {eq_p_float}), scores {eq_s} (floats exact {eq_s_float})")
        ok &= eq_p and eq_p_float and eq_s and eq_s_float
        try:
            write_score_outputs(paths, pred_rows, score_rows, ["second write"])
            print("  BAD: a second write did not refuse")
            ok = False
        except SystemExit as e:
            print(f"  a second write refused, as required: {e}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  temporary directory deleted: {not tmp.exists()}")
    print(f"  G4: {'PASSED' if ok else 'FAILED'}")
    return ok


def run_gate(args):
    import lightgbm as lgb
    print("SESSION 87 score --gate (offline; recorded results only; writes nothing under data/)")
    print(f"gate start (UTC): {now_utc()}")
    print(f"python {sys.version.split()[0]}, numpy {np.__version__}, lightgbm {lgb.__version__}")
    g1 = gate_g1()
    g2 = gate_g2()
    g3 = gate_g3()
    g4 = gate_g4(g1, g2)
    allok = g1[0] and g2[0] and g3 and g4
    print(f"\nGATE: G1 {'PASSED' if g1[0] else 'FAILED'}, G2 {'PASSED' if g2[0] else 'FAILED'}, "
          f"G3 {'PASSED' if g3 else 'FAILED'}, G4 {'PASSED' if g4 else 'FAILED'}")
    print(f"gate end (UTC): {now_utc()}")
    return 0 if allok else 1


# ------------------------------------------------------------------ entry point

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--guard-check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    ap.add_argument("--period", default=None, help="--score only: A or B")
    ap.add_argument("--first-v17-cycle", default=None, help="--score only: YYYY-MM-DDTHH, from a DECISIONS entry")
    ap.add_argument("--no-v17", action="store_true", help="--score only: no operational v17 cycle by 2027-07-31")
    ap.add_argument("--rows-sha256", default=None, help="--score only: from the finding that recorded the build")
    ap.add_argument("--points-sha256", default=None, help="--score only: from the finding that recorded the fetch")
    ap.add_argument("--nbm-versions", default=None, help="--score only: label text copied from a DECISIONS entry")
    ap.add_argument("--mav-versions", default=None, help="--score only: label text copied from a DECISIONS entry")
    ap.add_argument("--decision", default=None, help="--score only: the DECISIONS entry, printed in the output")
    a = ap.parse_args()
    try:
        if a.guard_check:
            return guard_check()
        if a.gate:
            return run_gate(a)
        return run_score(a)
    except GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
