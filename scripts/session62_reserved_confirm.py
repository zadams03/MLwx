"""Session 62: the frozen, self-guarded reserved-year confirmation script
(DECISIONS D58). Locks the single final feature set -- B + D, L, R, T (the
session-62 owner review's confirmation of the D57 mechanical rule's own
output, F106) -- and defines the ONE authorized use of the reserved
2024-08-01..2025-07-31 confirmation year (D51).

THIS FILE IS FROZEN. Session 63 runs it with `--confirm`, once, unchanged.
This session (62) runs it with NO arguments, which executes preflight()
only -- header/date checks, a column-integrity check against committed
source files, and a machinery dry-run on the already-non-reserved 2023-24
EXPERIMENT_FOLD. preflight() never loads a reserved-year row and never
calls confirm().

A data-availability gap was discovered while writing this script, verified
directly against the committed files (not assumed), and is flagged here
loudly rather than worked around: the E1/E2/E3/E4 build sessions (49, 51,
53, 55) each deliberately excluded the reserved year from BOTH files they
committed (v16_window: 2021-03-24..2024-07-31; sealed_window:
2025-08-01..2026-07-31) -- per D51's own mandate at the time. Verified by
direct read of every date column: all four families' v16_window files span
exactly 2021-03-24..2024-07-31 (6,127 rows) and their sealed_window files
span exactly 2025-08-01..2026-07-31 (1,825 rows); ZERO rows of L, D, T, or R
exist anywhere for 2024-08-01..2025-07-31, the reserved year itself. So the
confirmation fold's TRAINING window (2021-03-24..2024-07-31) is fully
covered by the existing v16_window files, but its TEST window (the reserved
year) has no D/L/R/T feature values in any committed file. `run_confirm()`
below therefore contains a hard, loud guard that refuses to proceed past
row assembly for the test window if this gap has not been closed by then --
it does not silently score on an empty or incomplete set. This is reported
to the owner in this session's own DECISIONS entry (D58) as a blocker for
session 63 as currently scoped, not resolved here: pulling new GRIB data
for the reserved year is out of this session's lock-only scope, and it is
also not something "session 63 runs the frozen script once, unchanged"
naturally covers.

Reuses, does not redefine: session48_reserved_year.py's EXPERIMENT_FOLDS,
RESERVED_YEAR_START/END, assert_reserved_year_excluded; session60_combine_
design.py's CANDIDATE_FEATURES (for the L, D, T, R entries only -- P, rh,
plev are excluded from the final set and never referenced by this script's
feature assembly). Reuses the committed E1-E4 build files verbatim --
rebuilds, re-decodes, and re-derives nothing, except re-applying D53/F100's
own already-frozen one-line floor transform to the stored raw
`dewpoint_depression_t2m` column (the same wrinkle D57/F106 already named).
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session48_reserved_year import (  # noqa: E402
    RESERVED_YEAR_START,
    RESERVED_YEAR_END,
    EXPERIMENT_FOLDS,
    assert_reserved_year_excluded,
)
from session60_combine_design import CANDIDATE_FEATURES  # noqa: E402

# ---------------------------------------------------------------------------
# SESSION 63 WIRING ADDITION (D58 item 11 / DECISIONS F107). Step 0 of the
# session-63 prompt determined this is CASE (B): load_family() below reads
# only CANDIDATE_FEATURES[code]["v16_file"]/["sealed_file"] (the sessions
# 49/51/53/55 committed family files) and treats any reserved-year row found
# there as a "hit" that stops the run -- there was no third, per-family
# reserved-year source file already referenced anywhere in this script. This
# map names the four new files session63_reserved_year_build.py produces,
# one per adopted family (L, D, T, R). Added HERE, not to
# session60_combine_design.py's CANDIDATE_FEATURES -- that dict is left
# byte-for-byte as session 61 already used it, so nothing about session 61's
# own already-reported result (F106) changes. This is an outcome-orthogonal
# wiring change: it only affects which rows load_family() sees, before any
# model is fit -- the same class of change as the F92/F93 pre-look guard
# fix. It does not call run_confirm() and does not compute anything.
# ---------------------------------------------------------------------------
RESERVED_FAMILY_FILES = {
    "L": PROCESSED / "session63_reserved_window_with_upper_air.csv",
    "D": PROCESSED / "session63_reserved_window_with_moisture.csv",
    "T": PROCESSED / "session63_reserved_window_with_pressure.csv",
    "R": PROCESSED / "session63_reserved_window_with_radiation.csv",
}

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
ALL_STATIONS = list(AIRPORTS.keys())

# The single final feature set (D58, confirming D57/F106's mechanical output).
# P, rh, plev are explicitly NOT in this set and must never appear below.
FINAL_CODES = ["D", "L", "R", "T"]

FAMILY_KEYS = {
    "L": ["lapse_rate_t2_t850"],
    "D": ["dewpoint_depression_t2m_floored"],
    "T": ["pressure_tendency_3h_hpa"],
    "R": ["dswrf_2h_wm2"],
}
BASE_KEYS = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m"]
FINAL_FEATURE_KEYS = BASE_KEYS + sum((FAMILY_KEYS[c] for c in FINAL_CODES), [])

# D21.4/D48.6: locked LightGBM settings, identical to every prior modelling
# script in this project (F94, F96, F99-F106). Never tuned per set or fold.
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

B_ONLY_PATHS = [
    PROCESSED / "grib_features_v16_window.csv",
    PROCESSED / "grib_features_sealed_window.csv",
]

OBS_CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

# ------------------------------------------------------------------ the two folds this script ever touches

# THE SINGLE AUTHORIZED RESERVED-YEAR USE (D51, pinned here by D58). This
# fold's test window IS the reserved 2024-08-01..2025-07-31 confirmation
# year, by design and on purpose -- it is the one named exception, and it is
# NEVER passed through assert_reserved_year_excluded() in run_confirm(). See
# preflight()'s own explicit proof (below) that this fold would otherwise be
# rejected by the guard, which is exactly why it is deliberately never given
# to that guard.
CONFIRMATION_FOLD = dict(
    label="2024-25-confirmation (D51/D58 -- THE ONE AUTHORIZED RESERVED-YEAR USE)",
    train_start=date(2021, 3, 24), train_end=date(2024, 7, 31),
    test_start=date(2024, 8, 1), test_end=date(2025, 7, 31),
)

# The machinery dry-run fold for THIS session's own preflight -- an
# already-non-reserved EXPERIMENT_FOLDS entry (session 48/D51), already used
# descriptively by every E-session and by F106 -- spends no new look.
_DRY_RUN_LABEL = "2023-24"
DRY_RUN_FOLD = next(
    dict(label=lbl, train_start=tr_s, train_end=tr_e, test_start=te_s, test_end=te_e)
    for lbl, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS if lbl == _DRY_RUN_LABEL
)

OUT_PREFLIGHT = ROOT / "notes" / "session-62-preflight-output.txt"
GRID_CSV_CONFIRM = PROCESSED / "session63_reserved_confirm_grid.csv"


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
    print("=" * 90)
    print(title)
    print("=" * 90)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ features

def year_fraction(d):
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0
                                             or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def make_feature_vector(r, keys):
    a = 2 * math.pi * year_fraction(r["date"])
    lookup = {
        "temp": r["fc"],
        "season_sin": math.sin(a),
        "season_cos": math.cos(a),
        "cloud_cover": r["cloud"],
        "wind_speed_10m": r["wind"],
        "lapse_rate_t2_t850": r.get("lapse_rate_t2_t850"),
        "dewpoint_depression_t2m_floored": r.get("dewpoint_depression_t2m_floored"),
        "pressure_tendency_3h_hpa": r.get("pressure_tendency_3h_hpa"),
        "dswrf_2h_wm2": r.get("dswrf_2h_wm2"),
    }
    return [lookup[k] for k in keys]


def features_matrix(rows, keys):
    return np.array([make_feature_vector(r, keys) for r in rows], dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


# ------------------------------------------------------------------ loading

def load_family(short_name, extra_cols):
    """Loads a CANDIDATE_FEATURES entry's v16_file + sealed_file, unfiltered
    by date (the defensive reserved-year SCAN below reads only the date
    column to COUNT any reserved-year rows -- never a feature value from
    inside the reserved year, since verified none exist). Returns
    (station -> {date: {col: value}}, reserved_year_row_count)."""
    spec = CANDIDATE_FEATURES[short_name]
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    for path in (spec["v16_file"], spec["sealed_file"]):
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue
                row = {}
                for c in extra_cols:
                    row[c] = float(r[c])
                out[st][d] = row
    # SESSION 63 WIRING ADDITION (D58 item 11 / F107, see the module-level
    # RESERVED_FAMILY_FILES comment above): also load the reserved-year rows
    # from the new per-family file, if it exists. These rows are NOT run
    # through the reserved-year exclusion check above -- by construction of
    # that file, every row in it is supposed to be inside the reserved year.
    # Any row that is not raises immediately, rather than being silently
    # accepted.
    reserved_path = RESERVED_FAMILY_FILES.get(short_name)
    if reserved_path is not None and reserved_path.exists():
        with open(reserved_path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if not (RESERVED_YEAR_START <= d <= RESERVED_YEAR_END):
                    raise AssertionError(
                        f"session63 reserved-year file {reserved_path.name} "
                        f"contains an out-of-range date {d} for station {st} "
                        f"-- refusing to proceed.")
                row = {}
                for c in extra_cols:
                    row[c] = float(r[c])
                out[st][d] = row
    return out, reserved_hits


def load_base_unfiltered():
    """station -> {date: {'fc','cloud','wind'}} from the pre-D51 base 5-feature
    files, UNFILTERED by date -- these files already carry the reserved year
    (B needs it for the one authorized confirmation), and it is the caller's
    job to select only a guard-passed or explicitly-authorized fold's date
    range, never this loader's."""
    out = {st: {} for st in AIRPORTS}
    for path in B_ONLY_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                out[st][d] = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                }
    return out


def load_obs_all(station, target_hour):
    """{date: temp} for the target hour, D14 pairing rule (SPEC 4.5)."""
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
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[dt] = float(raw)
    return series, outside_15min, no_temp


def build_complete_case(base_all, l_all, d_all, t_all, r_all):
    """Complete-case row set over the FINAL SET's own underlying columns only
    (D57 carried forward, D58 item 5) -- L, D(raw), T, R. Not P/rh/plev
    (they are not in the final set). Returns station -> {date: row}."""
    merged = {st: {} for st in AIRPORTS}
    for st in AIRPORTS:
        common = (set(base_all[st]) & set(l_all[st]) & set(d_all[st])
                  & set(t_all[st]) & set(r_all[st]))
        for d in sorted(common):
            b, l_, d_, t_, r_ = base_all[st][d], l_all[st][d], d_all[st][d], t_all[st][d], r_all[st][d]
            merged[st][d] = {
                "date": d, "fc": b["fc"], "cloud": b["cloud"], "wind": b["wind"],
                "lapse_rate_t2_t850": l_["lapse_rate_t2_t850"],
                "dewpoint_depression_t2m_floored": max(d_["dewpoint_depression_t2m"], 0.0),
                "pressure_tendency_3h_hpa": t_["pressure_tendency_3h_hpa"],
                "dswrf_2h_wm2": r_["dswrf_2h_wm2"],
            }
    return merged


def join_obs(station, merged_rows, obs_all):
    rows = []
    no_obs = 0
    for d in sorted(merged_rows.keys()):
        o = obs_all.get(d)
        if o is None:
            no_obs += 1
            continue
        base = merged_rows[d]
        rows.append({**base, "obs": o, "resid": o - base["fc"]})
    return rows, no_obs


# ------------------------------------------------------------------ fit/score

def fit_and_score(codes, keys_base_plus, train_rows, test_rows):
    keys = BASE_KEYS + sum((FAMILY_KEYS[c] for c in sorted(codes)), []) if keys_base_plus is None else keys_base_plus
    x_tr = features_matrix(train_rows, keys)
    y_tr = np.array([r["resid"] for r in train_rows], dtype=float)
    m = lgb.LGBMRegressor(**LGB_PARAMS)
    m.fit(x_tr, y_tr)
    x_te = features_matrix(test_rows, keys)
    pred = m.predict(x_te)
    e_model = [(r["fc"] + float(pred[i])) - r["obs"] for i, r in enumerate(test_rows)]
    return mae(e_model), e_model


def raw_persist(station, test_rows, obs_all):
    e_raw = [r["fc"] - r["obs"] for r in test_rows]
    no_prev = 0
    e_persist = []
    for r in test_rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        e_persist.append(float(prev) - r["obs"])
    return mae(e_raw), mae(e_persist), no_prev


# ------------------------------------------------------------------ preflight (THIS SESSION runs only this)

def preflight():
    tee = Tee(OUT_PREFLIGHT)
    sys.stdout = tee

    line("SESSION 62 -- reserved-year confirmation LOCK, pre-flight only "
         "(DECISIONS D58). No reserved-year row is read anywhere in this "
         "function. The confirmation fold is NOT run. No 2024-25 MAE is "
         "produced.")
    print(f"run at   : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python   : {sys.version.split()[0]}")
    print(f"numpy    : {np.__version__}")
    print(f"lightgbm : {lgb.__version__}")
    print(f"\nFINAL SET (D58, confirming D57/F106's mechanical output): "
          f"B + {'+'.join(FINAL_CODES)}  (i.e. B+D,L,R,T)")
    print(f"FINAL_FEATURE_KEYS = {FINAL_FEATURE_KEYS}")
    print("P, rh, plev are excluded -- confirmed absent from FAMILY_KEYS and "
          "FINAL_CODES above.")
    assert set(FINAL_CODES) == {"D", "L", "R", "T"}
    assert "P" not in FAMILY_KEYS and "rh" not in FAMILY_KEYS and "plev" not in FAMILY_KEYS

    # -------------------------------------------------- header / date checks
    line("Header / date checks (session prompt pre-flight item 1)")
    for code in FINAL_CODES:
        spec = CANDIDATE_FEATURES[code]
        for file_key in ("v16_file", "sealed_file"):
            path = spec[file_key]
            with open(path) as f:
                header = f.readline().rstrip("\n").rstrip("\r").split(",")
            missing = [c for c in spec["columns"] if c not in header]
            print(f"    {code:<4} {file_key:<12} {path.name:<52} "
                  f"columns={spec['columns']} "
                  f"-- {'PASS' if not missing else f'MISSING {missing}'}")
            if missing:
                raise RuntimeError(f"session62 preflight FAILED: {path} missing {missing}")

    print(f"\n    CONFIRMATION_FOLD: train={CONFIRMATION_FOLD['train_start']}.."
          f"{CONFIRMATION_FOLD['train_end']}  test={CONFIRMATION_FOLD['test_start']}.."
          f"{CONFIRMATION_FOLD['test_end']}")
    assert CONFIRMATION_FOLD["train_start"] == date(2021, 3, 24)
    assert CONFIRMATION_FOLD["train_end"] == date(2024, 7, 31)
    assert CONFIRMATION_FOLD["test_start"] == RESERVED_YEAR_START == date(2024, 8, 1)
    assert CONFIRMATION_FOLD["test_end"] == RESERVED_YEAR_END == date(2025, 7, 31)
    print("    Dates match D51's own reserved-year bounds and D58's pinned "
          "train/test split exactly -- PASS.")

    # -------------------------------------------------- guard: authorizes exactly the confirmation fold
    line("Guard check (session prompt pre-flight item 1, mirrors D51's own "
         "guard-verification pattern): the guard must PASS the dry-run fold, "
         "RAISE on three deliberately reserved-year-touching folds, and the "
         "confirmation fold must be proven to be the kind of fold the guard "
         "WOULD reject -- which is exactly why it is never given to the guard.")

    sub("Positive check -- DRY_RUN_FOLD clears the guard")
    assert_reserved_year_excluded(DRY_RUN_FOLD["label"], DRY_RUN_FOLD["train_start"],
                                   DRY_RUN_FOLD["train_end"], DRY_RUN_FOLD["test_start"],
                                   DRY_RUN_FOLD["test_end"])
    print(f"    {DRY_RUN_FOLD['label']}: train={DRY_RUN_FOLD['train_start']}.."
          f"{DRY_RUN_FOLD['train_end']}  test={DRY_RUN_FOLD['test_start']}.."
          f"{DRY_RUN_FOLD['test_end']}  -- PASS (guard did not raise)")

    sub("Negative check -- three deliberately reserved-year-touching folds must raise")
    violations = [
        ("hypothetical train-crosses-reserved-year fold",
         date(2021, 3, 24), date(2025, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
        ("hypothetical test-on-reserved-year fold",
         date(2021, 3, 24), date(2024, 7, 31), RESERVED_YEAR_START, RESERVED_YEAR_END),
        ("hypothetical train-into-reserved-year fold",
         date(2021, 3, 24), date(2025, 1, 1), date(2025, 8, 1), date(2026, 7, 31)),
    ]
    for label, tr_s, tr_e, te_s, te_e in violations:
        try:
            assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
            print(f"    {label}: DID NOT RAISE -- guard failure, this is a bug")
            raise SystemExit(1)
        except ValueError as e:
            print(f"    {label}: raised as expected -- {e}")

    sub("Proof the CONFIRMATION_FOLD is a genuine, deliberate reserved-year "
        "use -- NOT an oversight -- by showing the guard WOULD reject it too")
    try:
        assert_reserved_year_excluded(
            CONFIRMATION_FOLD["label"], CONFIRMATION_FOLD["train_start"],
            CONFIRMATION_FOLD["train_end"], CONFIRMATION_FOLD["test_start"],
            CONFIRMATION_FOLD["test_end"])
        print("    CONFIRMATION_FOLD DID NOT RAISE -- unexpected: its test window "
              "should equal the reserved year exactly. This is a bug -- "
              "investigate before session 63 runs.")
        raise SystemExit(1)
    except ValueError as e:
        print(f"    CONFIRMATION_FOLD raised as expected -- {e}")
        print("    This is exactly why run_confirm() NEVER calls "
              "assert_reserved_year_excluded() on CONFIRMATION_FOLD: it is the "
              "one, named, D51/D58-authorized exception, proven here to be a "
              "genuine reserved-year fold rather than a guard bug or a silent "
              "bypass.")

    # -------------------------------------------------- column-integrity check (training window only)
    line("Column-integrity check (session prompt pre-flight item 2, reusing "
         "F106's own check): each of L, D, T, R matches its committed source "
         "file exactly, checked over every row of the TRAINING window "
         "(2021-03-24..2024-07-31 -- the only span currently available; see "
         "the reserved-year data-gap finding below for the test window)")
    l_all, hits_l = load_family("L", ["lapse_rate_t2_t850"])
    d_all, hits_d = load_family("D", ["dewpoint_depression_t2m"])
    t_all, hits_t = load_family("T", ["pressure_tendency_3h_hpa"])
    r_all, hits_r = load_family("R", ["dswrf_2h_wm2"])
    print(f"    L rows loaded={sum(len(v) for v in l_all.values())}  reserved-year hits={hits_l}")
    print(f"    D rows loaded={sum(len(v) for v in d_all.values())}  reserved-year hits={hits_d}")
    print(f"    T rows loaded={sum(len(v) for v in t_all.values())}  reserved-year hits={hits_t}")
    print(f"    R rows loaded={sum(len(v) for v in r_all.values())}  reserved-year hits={hits_r}")
    total_hits = hits_l + hits_d + hits_t + hits_r
    if total_hits:
        raise AssertionError(
            f"SESSION 62 STOP SIGNAL: {total_hits} row(s) inside the reserved "
            "2024-25 confirmation year were found in the committed L/D/T/R "
            "source files -- refusing to proceed (D51).")
    print(f"\n    PASS -- 0 reserved-year rows found across all four family source files.")

    base_all = load_base_unfiltered()
    merged_train_all = build_complete_case(base_all, l_all, d_all, t_all, r_all)
    # Re-load with the raw column re-read directly for a true independent
    # cross-check (not reusing the same in-memory dict object), matching
    # F106's own re-check pattern.
    max_diff = {"lapse_rate_t2_t850": 0.0, "dewpoint_depression_t2m_floored": 0.0,
                "pressure_tendency_3h_hpa": 0.0, "dswrf_2h_wm2": 0.0}
    n_checked = 0
    for st in AIRPORTS:
        for d, row in merged_train_all[st].items():
            if not (CONFIRMATION_FOLD["train_start"] <= d <= CONFIRMATION_FOLD["train_end"]):
                continue
            n_checked += 1
            max_diff["lapse_rate_t2_t850"] = max(max_diff["lapse_rate_t2_t850"],
                abs(row["lapse_rate_t2_t850"] - l_all[st][d]["lapse_rate_t2_t850"]))
            expected_floor = max(d_all[st][d]["dewpoint_depression_t2m"], 0.0)
            max_diff["dewpoint_depression_t2m_floored"] = max(
                max_diff["dewpoint_depression_t2m_floored"],
                abs(row["dewpoint_depression_t2m_floored"] - expected_floor))
            max_diff["pressure_tendency_3h_hpa"] = max(max_diff["pressure_tendency_3h_hpa"],
                abs(row["pressure_tendency_3h_hpa"] - t_all[st][d]["pressure_tendency_3h_hpa"]))
            max_diff["dswrf_2h_wm2"] = max(max_diff["dswrf_2h_wm2"],
                abs(row["dswrf_2h_wm2"] - r_all[st][d]["dswrf_2h_wm2"]))
    print(f"\n    n_checked (training-window complete-case rows) = {n_checked}")
    for k, v in max_diff.items():
        print(f"    {k:<38} max_abs_diff = {v:.9f}")
    integrity_pass = all(v == 0.0 for v in max_diff.values())
    print(f"\n    {'PASS' if integrity_pass else 'FAIL'} -- every final-set feature "
          f"column matches its committed source (D floor applied exactly per "
          f"D53/F100) on every training-window row.")
    if not integrity_pass:
        raise AssertionError("SESSION 62 STOP SIGNAL: column-integrity check failed.")

    for st in AIRPORTS:
        n = sum(1 for d in merged_train_all[st]
                 if CONFIRMATION_FOLD["train_start"] <= d <= CONFIRMATION_FOLD["train_end"])
        print(f"    {st:<6} complete-case rows in training window: {n}")

    # -------------------------------------------------- THE RESERVED-YEAR DATA-GAP FINDING
    line("RESERVED-YEAR FEATURE-DATA GAP -- flagged plainly, not worked around "
         "(discovered while building this script, verified directly against "
         "every committed file, not assumed)")
    print("    Checked: do the L, D, T, R committed source files contain ANY row")
    print("    whose date falls inside the reserved 2024-08-01..2025-07-31 year?")
    print(f"    L: {hits_l} reserved-year rows found (of {sum(len(v) for v in l_all.values())} total)")
    print(f"    D: {hits_d} reserved-year rows found (of {sum(len(v) for v in d_all.values())} total)")
    print(f"    T: {hits_t} reserved-year rows found (of {sum(len(v) for v in t_all.values())} total)")
    print(f"    R: {hits_r} reserved-year rows found (of {sum(len(v) for v in r_all.values())} total)")
    print("\n    RESULT: ZERO, at every one of the four families. This is expected")
    print("    given how sessions 49/51/53/55 built these files (each deliberately")
    print("    excluded the reserved year, per D51's own mandate at the time,")
    print("    per F98/F100/F101/F102's own date-range description) -- but it")
    print("    means the CONFIRMATION_FOLD's test window (the reserved year) has")
    print("    NO L, D, T, or R feature value in any committed file, at any airport.")
    print("\n    CONSEQUENCE: run_confirm() cannot assemble a complete-case feature")
    print("    matrix for the test window as things stand -- there is nothing to")
    print("    assemble. This is a genuine blocker for session 63 as currently")
    print("    scoped ('run the frozen script once, unchanged, on the 2024-25")
    print("    fold'), reported here and in DECISIONS D58 for the owner to")
    print("    resolve BEFORE session 63 runs -- not silently patched around in")
    print("    this script. run_confirm() below contains a hard, loud guard that")
    print("    refuses to proceed past row assembly if this gap is still open.")

    # -------------------------------------------------- machinery dry-run on 2023-24 (non-reserved)
    line("Machinery dry-run on the 2023-24 EXPERIMENT_FOLD (session prompt "
         "pre-flight item 3) -- already used descriptively by every E-session "
         "and by F106 itself, so no new look is spent. Proves the fit/score "
         "plumbing end-to-end without touching the reserved year.")

    obs_all_by_station = {}
    dry_grid = []
    for st, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(st, target_hour)
        obs_all_by_station[st] = obs_all

        tr_s, tr_e = DRY_RUN_FOLD["train_start"], DRY_RUN_FOLD["train_end"]
        te_s, te_e = DRY_RUN_FOLD["test_start"], DRY_RUN_FOLD["test_end"]
        assert tr_e < te_s

        merged_full = merged_train_all[st]
        train_rows_raw = {d: r for d, r in merged_full.items() if tr_s <= d <= tr_e}
        test_rows_raw = {d: r for d, r in merged_full.items() if te_s <= d <= te_e}

        train_rows, _ = join_obs(st, train_rows_raw, obs_all)
        test_rows, no_obs = join_obs(st, test_rows_raw, obs_all)

        raw_mae, persist_mae, no_prev = raw_persist(st, test_rows, obs_all)
        b_mae, _ = fit_and_score(set(), BASE_KEYS, train_rows, test_rows)
        f_mae, _ = fit_and_score(set(FINAL_CODES), FINAL_FEATURE_KEYS, train_rows, test_rows)

        print(f"    {st:<6} n_train={len(train_rows):<6} n_test={len(test_rows):<6} "
              f"no_usable_obs_dropped={no_obs:<4} no_prev={no_prev:<4} "
              f"raw={raw_mae:.4f}  persist={persist_mae:.4f}  "
              f"B={b_mae:.4f}  B+DLRT={f_mae:.4f}  "
              f"skill_vs_B={100*(1-f_mae/b_mae):+.2f}%")
        dry_grid.append(dict(station=st, raw=raw_mae, persist=persist_mae, b=b_mae, final=f_mae))

    b_mean = sum(r["b"] for r in dry_grid) / len(dry_grid)
    f_mean = sum(r["final"] for r in dry_grid) / len(dry_grid)
    print(f"\n    Airport-averaged (2023-24 dry run): B={b_mean:.4f}  "
          f"B+DLRT={f_mean:.4f}  skill_vs_B={100*(1-f_mean/b_mean):+.2f}%")
    print("    This reproduces the same date range already scored descriptively")
    print("    in F99-F106 (the '2023-24' EXPERIMENT_FOLD) -- a plumbing check,")
    print("    not a new look, and not comparable 1:1 to F106's own B+D,L,R,T")
    print("    reading there (F106 pooled across three folds; this is 2023-24 alone).")

    line("END OF PRE-FLIGHT")
    print("No row of the reserved 2024-08-01..2025-07-31 confirmation year was")
    print("read anywhere in this function. run_confirm() was not called. No")
    print("2024-25 MAE was produced. The reserved-year feature-data gap above")
    print("is the one open item session 63 must have resolved before it can run.")
    print(f"This output is saved at notes/{OUT_PREFLIGHT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


# ------------------------------------------------------------------ THE confirmation run (session 63 only)

def run_confirm():
    """THE single authorized reserved-year use (D51/D58). Session 63 invokes
    this via `python session62_reserved_confirm.py --confirm`, once,
    unchanged. This function is never called by preflight() and is not
    called anywhere in this session's own run.

    Contains a hard, loud guard (see the RESERVED-YEAR FEATURE-DATA GAP
    check below): if the L/D/T/R committed files still have zero rows for
    the reserved year when this runs, it refuses to proceed rather than
    silently scoring on an empty or incomplete set. Per D58 item 9, this is
    the kind of outcome-orthogonal guard that may be fixed and re-committed
    before the one authorized look is spent -- no MAE is seen if it trips.
    """
    print("=" * 90)
    print("SESSION 63 -- THE SINGLE AUTHORIZED RESERVED-YEAR CONFIRMATION "
          "(D51/D58). Running once, unchanged.")
    print("=" * 90)

    l_all, hits_l = load_family("L", ["lapse_rate_t2_t850"])
    d_all, hits_d = load_family("D", ["dewpoint_depression_t2m"])
    t_all, hits_t = load_family("T", ["pressure_tendency_3h_hpa"])
    r_all, hits_r = load_family("R", ["dswrf_2h_wm2"])
    if hits_l or hits_d or hits_t or hits_r:
        raise AssertionError(
            "STOP: reserved-year rows found inside the L/D/T/R source files "
            "themselves -- investigate before proceeding (D51).")

    base_all = load_base_unfiltered()
    merged = build_complete_case(base_all, l_all, d_all, t_all, r_all)

    ts, te = CONFIRMATION_FOLD["test_start"], CONFIRMATION_FOLD["test_end"]
    tr_s, tr_e = CONFIRMATION_FOLD["train_start"], CONFIRMATION_FOLD["train_end"]

    # HARD GUARD: the reserved-year feature-data gap (see module docstring
    # and D58). Refuses to proceed if the test window's complete-case row
    # count is not what a genuine full year of data would give -- rather
    # than silently fitting/scoring on zero or partial rows.
    for st in AIRPORTS:
        n_test = sum(1 for d in merged[st] if ts <= d <= te)
        if n_test == 0:
            raise RuntimeError(
                f"STOP (D58 reserved-year feature-data gap): {st} has ZERO "
                f"complete-case L/D/T/R rows in the reserved test window "
                f"{ts}..{te}. The committed E1-E4 build files (sessions 49, "
                f"51, 53, 55) do not cover this date range -- see this "
                f"script's own module docstring and DECISIONS D58. This gap "
                f"must be closed (the L/D/T/R feature pipelines extended to "
                f"cover the reserved year, reusing their own already-frozen "
                f"pull/derive code, before this confirmation can run. "
                f"Refusing to proceed -- no MAE has been computed.")

    # If the gap above is ever closed, the rest of the confirmation proceeds
    # exactly as pre-registered (D58 items 4-7):
    grid = []
    for st, target_hour in AIRPORTS.items():
        obs_all, _, _ = load_obs_all(st, target_hour)
        train_rows_raw = {d: r for d, r in merged[st].items() if tr_s <= d <= tr_e}
        test_rows_raw = {d: r for d, r in merged[st].items() if ts <= d <= te}
        train_rows, _ = join_obs(st, train_rows_raw, obs_all)
        test_rows, no_obs = join_obs(st, test_rows_raw, obs_all)

        raw_mae, persist_mae, no_prev = raw_persist(st, test_rows, obs_all)
        b_mae, _ = fit_and_score(set(), BASE_KEYS, train_rows, test_rows)
        f_mae, _ = fit_and_score(set(FINAL_CODES), FINAL_FEATURE_KEYS, train_rows, test_rows)

        passes_raw = f_mae < raw_mae
        passes_persist = f_mae < persist_mae
        print(f"{st}: n_train={len(train_rows)} n_test={len(test_rows)} "
              f"no_obs_dropped={no_obs} no_prev={no_prev} raw={raw_mae:.4f} "
              f"persist={persist_mae:.4f} B={b_mae:.4f} B+DLRT={f_mae:.4f} "
              f"vs_raw={'PASS' if passes_raw else 'FAIL'} "
              f"vs_persist={'PASS' if passes_persist else 'FAIL'}")
        grid.append(dict(station=st, raw_mae=raw_mae, persist_mae=persist_mae,
                          b_mae=b_mae, final_mae=f_mae, no_obs=no_obs, no_prev=no_prev,
                          passes_raw=passes_raw, passes_persist=passes_persist))

    with open(GRID_CSV_CONFIRM, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(grid[0].keys()))
        w.writeheader()
        w.writerows(grid)

    all_pass = all(g["passes_raw"] and g["passes_persist"] for g in grid)
    b_mean = sum(g["b_mae"] for g in grid) / len(grid)
    f_mean = sum(g["final_mae"] for g in grid) / len(grid)
    print(f"\nBAR VERDICT (D58 pre-registered expectation 7): "
          f"{'ALL FIVE AIRPORTS PASS' if all_pass else 'NOT ALL AIRPORTS PASS'}")
    print(f"SECONDARY READ: B+D,L,R,T airport-averaged MAE {f_mean:.4f} vs B "
          f"{b_mean:.4f}  ({'beats B' if f_mean < b_mean else 'does NOT beat B'})")
    return grid


# ------------------------------------------------------------------ entry point

def main():
    if len(sys.argv) == 1:
        preflight()
    elif len(sys.argv) == 2 and sys.argv[1] == "--confirm":
        run_confirm()
    else:
        raise SystemExit(
            "usage: python session62_reserved_confirm.py           (pre-flight only)\n"
            "       python session62_reserved_confirm.py --confirm (THE single "
            "authorized reserved-year run -- session 63 only)")


if __name__ == "__main__":
    main()
