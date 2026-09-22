"""Session 61: runs the pre-registered combine-phase feature-selection sweep
(DECISIONS D57), using the frozen manifest scripts/session60_combine_design.py.
Fits the 14-variant ladder on the three non-reserved EXPERIMENT_FOLDS
(session48_reserved_year.py), applies the mechanical selection rule with its
correlated-feature safeguard and joint backstop, and reports the grid. This
script computes NO verdict and NEVER reads the reserved 2024-08-01..2025-07-31
confirmation year (D51) -- the single final feature set is the session-62
owner review's call, per the session prompt.

Two interpretation decisions were required to turn D57's English rule into
code, both stated here explicitly (not a SPEC/prompt disagreement, a judgment
call in operationalizing prose -- flagged for the session-62 review to check):

1. "DSM is diagnostic only -- never a keep/drop vote" (D57, session-61.md),
   read together with "all keep/drop reads are at the airport-averaged
   level" immediately before it: every mechanical keep/drop/adopt/backstop
   decision computes its airport-averaged quantity over the FOUR non-DSM
   airports (EGLC, LFPG, YSDU, RNO). DSM is still fit and reported in the
   full grid/summary (all five airports) for context, exactly as every prior
   E-session did -- only the votes themselves exclude it.
2. `plev`'s own explicit override -- "must clear the bar airport-averaged
   ACROSS ALL FIVE AIRPORTS (the recipe-travels tax -- an RNO-only gain does
   not qualify)" -- is read as overriding rule (1) specifically for `plev`'s
   own adoption test: `plev` is voted on using all five airports, including
   DSM, unlike every other keep/drop/adopt decision in this script.

Reuses, does not redefine: session48_reserved_year.py's EXPERIMENT_FOLDS,
RESERVED_YEAR_START/END, assert_reserved_year_excluded (via session60's own
re-export); session60_combine_design.py's CANDIDATE_FEATURES, VARIANT_LADDER,
TAU_SKILL, ROW_COST_GUARD_FRAC, DROP_ORDER. Reuses the committed E1-E5 build
files verbatim -- rebuilds, re-decodes, and re-derives nothing, except
re-applying D53/F100's own already-frozen one-line floor transform to the
stored raw `dewpoint_depression_t2m` column (D57's own named wrinkle).
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
from session60_combine_design import (  # noqa: E402
    CANDIDATE_FEATURES,
    VARIANT_LADDER,
    TAU_SKILL,
    ROW_COST_GUARD_FRAC,
    DROP_ORDER,
)

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
NON_DSM = ["EGLC", "LFPG", "YSDU", "RNO"]  # D57: DSM is diagnostic only, never a vote

FOLD_LABELS = [label for label, *_ in EXPERIMENT_FOLDS]
FOLD_BOUNDS = {label: (tr_s, tr_e, te_s, te_e) for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS}

TAU_PCT = TAU_SKILL * 100  # 0.4 percentage points

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

# D48.6/D21.4: locked LightGBM settings, identical for every variant, fold,
# airport, and any ad hoc variant the selection rule needs to fit.
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

BASE_KEYS = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m"]
FAMILY_KEYS = {
    "L": ["lapse_rate_t2_t850"],
    "D": ["dewpoint_depression_t2m_floored"],
    "T": ["pressure_tendency_3h_hpa"],
    "R": ["dswrf_2h_wm2"],
    "P": ["precip_rate_mmh"],
    "rh": ["relative_humidity_2m"],
    "plev": ["t850", "t925", "t700"],
}
CORR_COLS = ["lapse_rate_t2_t850", "dewpoint_depression_t2m_floored",
             "pressure_tendency_3h_hpa", "dswrf_2h_wm2", "precip_rate_mmh",
             "relative_humidity_2m", "t850", "t925", "t700"]

OUT = ROOT / "notes" / "session-61-combine-sweep-output.txt"
GRID_CSV = PROCESSED / "session61_combine_sweep_grid.csv"
SUMMARY_CSV = PROCESSED / "session61_combine_sweep_summary.csv"
ROWCOST_CSV = PROCESSED / "session61_row_cost_guard.csv"
CORR_CSV = PROCESSED / "session61_correlation_matrix.csv"


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
        "lapse_rate_t2_t850": r["lapse_rate_t2_t850"],
        "dewpoint_depression_t2m_floored": r["dewpoint_depression_t2m_floored"],
        "pressure_tendency_3h_hpa": r["pressure_tendency_3h_hpa"],
        "dswrf_2h_wm2": r["dswrf_2h_wm2"],
        "precip_rate_mmh": r["precip_rate_mmh"],
        "relative_humidity_2m": r["relative_humidity_2m"],
        "t850": r["t850"], "t925": r["t925"], "t700": r["t700"],
    }
    return [lookup[k] for k in keys]


def features_matrix(rows, keys):
    return np.array([make_feature_vector(r, keys) for r in rows], dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


def codes_to_variant_name(codes):
    order = ["L", "D", "T", "R", "P", "rh", "plev"]
    picked = [c for c in order if c in codes]
    if not picked:
        return "B"
    return "B+" + "".join(c if c not in ("rh", "plev") else f"+{c}" for c in picked).replace("++", "+")


def codes_label(codes):
    if not codes:
        return "B"
    return "B+" + ",".join(sorted(codes))


# ------------------------------------------------------------------ loading

def load_full_file(v16_path, sealed_path, extra_cols):
    """station -> {date: {'fc','cloud','wind', **extra_cols}}. Defensive
    reserved-year scan on every row; returns (data, reserved_hits)."""
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    for path in (v16_path, sealed_path):
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue
                row = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                }
                for c in extra_cols:
                    row[c] = float(r[c])
                out[st][d] = row
    return out, reserved_hits


def load_b_only_dates():
    """station -> set(date), from the true base 5-feature dataset
    (grib_features_v16_window.csv / grib_features_sealed_window.csv), with
    the reserved 2024-25 year excluded by a defensive per-row scan (that
    base dataset predates D51 and still carries the reserved year inside
    its own v16-window file)."""
    out = {st: set() for st in AIRPORTS}
    reserved_hits = 0
    for path in B_ONLY_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue
                out[st].add(d)
    return out, reserved_hits


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


# ------------------------------------------------------------------ main

def main():
    if len(sys.argv) != 1:
        raise SystemExit("this script takes no arguments")

    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 61 -- combine-phase feature-selection sweep (DECISIONS D57). "
         "Runs ONLY on the three non-reserved EXPERIMENT_FOLDS. The reserved "
         "2024-08-01..2025-07-31 confirmation year (D51) is never read this "
         "session. NO VERDICT is computed -- the single final feature set is "
         "the session-62 owner review's call.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"TAU_SKILL     : {TAU_SKILL} ({TAU_PCT}pp)")
    print(f"ROW_COST_GUARD_FRAC: {ROW_COST_GUARD_FRAC}")
    print(f"DROP_ORDER    : {DROP_ORDER}")
    print(f"VARIANT_LADDER: {len(VARIANT_LADDER)} variants (imported, not redefined)")
    for name, feats in VARIANT_LADDER:
        print(f"    {name:<16} = B + {feats}")
    print("\nInterpretation decisions made to operationalize D57's English rule")
    print("into code (see this script's own module docstring for the full text):")
    print("  1. All mechanical keep/drop/adopt/backstop votes average over the")
    print("     FOUR non-DSM airports (EGLC, LFPG, YSDU, RNO). DSM is still fit")
    print("     and reported in the full grid/summary (all five airports).")
    print("  2. plev's own adoption vote uses all FIVE airports (its own")
    print("     explicit 'across all five airports' override in D57).")

    # ------------------------------------------------------------ Step 2: reserved-year guard FIRST
    line("Reserved-year guard -- cleared on all three EXPERIMENT_FOLDS entries "
         "BEFORE any data is loaded (D57 Step 2 / session prompt Step 2)")
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e}  test={te_s}..{te_e}  "
              f"-- PASS (guard did not raise)")
    print(f"\n    PASS -- all {len(EXPERIMENT_FOLDS)} EXPERIMENT_FOLDS entries "
          f"cleared assert_reserved_year_excluded() before any data was loaded.")

    # ------------------------------------------------------------ load the five distinct family source files
    line("Loading the five distinct committed E1-E5 source files (reusing "
         "committed columns only -- nothing rebuilt, re-decoded, or re-derived, "
         "except D53/F100's own frozen one-line floor transform, applied below)")

    l_spec = CANDIDATE_FEATURES["L"]
    UPPER_AIR, hits_ua = load_full_file(l_spec["v16_file"], l_spec["sealed_file"],
                                         ["lapse_rate_t2_t850", "t850", "t925", "t700"])
    d_spec = CANDIDATE_FEATURES["D"]
    MOISTURE, hits_mo = load_full_file(d_spec["v16_file"], d_spec["sealed_file"],
                                        ["dewpoint_depression_t2m", "relative_humidity_2m"])
    t_spec = CANDIDATE_FEATURES["T"]
    PRESSURE, hits_pr = load_full_file(t_spec["v16_file"], t_spec["sealed_file"],
                                        ["pressure_tendency_3h_hpa"])
    r_spec = CANDIDATE_FEATURES["R"]
    RADIATION, hits_ra = load_full_file(r_spec["v16_file"], r_spec["sealed_file"],
                                         ["dswrf_2h_wm2"])
    p_spec = CANDIDATE_FEATURES["P"]
    PRECIP, hits_pc = load_full_file(p_spec["v16_file"], p_spec["sealed_file"],
                                      ["precip_rate_mmh"])

    total_reserved_hits = hits_ua + hits_mo + hits_pr + hits_ra + hits_pc
    print(f"    upper-air (L, plev)  : {sum(len(v) for v in UPPER_AIR.values())} rows loaded, "
          f"reserved-year hits: {hits_ua}")
    print(f"    moisture (D, rh)     : {sum(len(v) for v in MOISTURE.values())} rows loaded, "
          f"reserved-year hits: {hits_mo}")
    print(f"    pressure (T)         : {sum(len(v) for v in PRESSURE.values())} rows loaded, "
          f"reserved-year hits: {hits_pr}")
    print(f"    radiation (R)        : {sum(len(v) for v in RADIATION.values())} rows loaded, "
          f"reserved-year hits: {hits_ra}")
    print(f"    precip (P)           : {sum(len(v) for v in PRECIP.values())} rows loaded, "
          f"reserved-year hits: {hits_pc}")
    if total_reserved_hits:
        raise AssertionError(
            f"SESSION 61 STOP SIGNAL: {total_reserved_hits} row(s) inside the "
            "reserved 2024-25 confirmation year were found in the E1-E5 "
            "committed source files -- refusing to proceed (D51).")
    print(f"\n    PASS -- 0 reserved-year rows found across all five source files "
          f"(defensive per-row scan).")

    # ------------------------------------------------------------ complete-case row set
    line("Building the single complete-case row set (session prompt Step 4): "
         "one row per (station, date) present in ALL SEVEN candidate features' "
         "underlying columns (L, D, T, R, P, rh, plev)")
    MERGED = {st: {} for st in AIRPORTS}
    base_max_diff = 0.0
    for st in AIRPORTS:
        common_dates = (set(UPPER_AIR[st]) & set(MOISTURE[st]) & set(PRESSURE[st])
                         & set(RADIATION[st]) & set(PRECIP[st]))
        for d in sorted(common_dates):
            ua, mo, pr, ra, pc = (UPPER_AIR[st][d], MOISTURE[st][d], PRESSURE[st][d],
                                   RADIATION[st][d], PRECIP[st][d])
            for a, b in ((ua, mo), (ua, pr), (ua, ra), (ua, pc)):
                base_max_diff = max(base_max_diff, abs(a["fc"] - b["fc"]),
                                     abs(a["cloud"] - b["cloud"]), abs(a["wind"] - b["wind"]))
            MERGED[st][d] = {
                "date": d,
                "fc": ua["fc"], "cloud": ua["cloud"], "wind": ua["wind"],
                "lapse_rate_t2_t850": ua["lapse_rate_t2_t850"],
                "t850": ua["t850"], "t925": ua["t925"], "t700": ua["t700"],
                "dewpoint_depression_t2m": mo["dewpoint_depression_t2m"],
                "dewpoint_depression_t2m_floored": max(mo["dewpoint_depression_t2m"], 0.0),
                "relative_humidity_2m": mo["relative_humidity_2m"],
                "pressure_tendency_3h_hpa": pr["pressure_tendency_3h_hpa"],
                "dswrf_2h_wm2": ra["dswrf_2h_wm2"],
                "precip_rate_mmh": pc["precip_rate_mmh"],
            }
    for st in AIRPORTS:
        print(f"    {st:<6} complete-case rows: {len(MERGED[st])}")
    print(f"\n    Base-column (temp/cloud/wind) cross-file consistency check "
          f"(bonus, beyond the session prompt's own item (i)): max abs diff "
          f"across all 5 source files, all complete-case rows = {base_max_diff:.9f} "
          f"-- {'PASS' if base_max_diff == 0.0 else 'FAIL'}")
    if base_max_diff != 0.0:
        raise AssertionError("SESSION 61 STOP SIGNAL: base-column mismatch across "
                              "the five E1-E5 source files -- see max abs diff above.")

    # ------------------------------------------------------------ row-cost guard
    line("Row-cost guard (session prompt Step 5): per airport per fold, "
         "complete-case row count vs a B-only mask (grib_features_v16_window/"
         "sealed_window.csv, reserved year excluded)")
    b_only_dates, b_only_reserved_hits = load_b_only_dates()
    print(f"    B-only source rows filtered out as inside the reserved year: "
          f"{b_only_reserved_hits}")
    print("    (expected and correct, not a stop condition: grib_features_v16_window.csv")
    print("    is the pre-D51 raw base dataset and still carries the reserved year inside")
    print("    its own file -- load_b_only_dates() filters those dates out before building")
    print("    the B-only mask below, exactly as intended. Contrast the E1-E5 committed")
    print("    build files above, which were built AFTER D51 and should carry zero")
    print("    reserved-year rows already -- that check above is the real stop condition.)")

    rowcost_rows = []
    guard_tripped = []
    print(f"\n    {'station':<8}{'fold':<10}{'b_only_n':>10}{'complete_n':>12}{'dropped':>10}{'drop_frac':>12}")
    for st in AIRPORTS:
        for fold_label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
            b_n = sum(1 for d in b_only_dates[st] if tr_s <= d <= te_e)
            c_n = sum(1 for d in MERGED[st] if tr_s <= d <= te_e)
            dropped = b_n - c_n
            frac = dropped / b_n if b_n else float("nan")
            print(f"    {st:<8}{fold_label:<10}{b_n:>10}{c_n:>12}{dropped:>10}{frac:>12.4f}")
            rowcost_rows.append(dict(station=st, fold=fold_label, b_only_n=b_n,
                                      complete_case_n=c_n, dropped=dropped,
                                      drop_frac=round(frac, 4) if frac == frac else ""))
            if frac == frac and frac > ROW_COST_GUARD_FRAC:
                guard_tripped.append((st, fold_label, frac))

    with open(ROWCOST_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["station", "fold", "b_only_n", "complete_case_n",
                                           "dropped", "drop_frac"])
        w.writeheader()
        w.writerows(rowcost_rows)
    print(f"\n    Wrote row-cost table: {ROWCOST_CSV}")

    if guard_tripped:
        print(f"\n    ROW-COST GUARD TRIPPED at {len(guard_tripped)} airport-fold(s) "
              f"(> {ROW_COST_GUARD_FRAC:.0%}): {guard_tripped}")
        print("    HALTING per D57 Step 5 -- not proceeding to fitting.")
        sys.stdout = sys.__stdout__
        tee.flush()
        return
    print(f"\n    PASS -- no airport-fold exceeds ROW_COST_GUARD_FRAC "
          f"({ROW_COST_GUARD_FRAC:.0%}). Proceeding to fitting.")

    # ------------------------------------------------------------ correlation matrix (up front)
    line("Pairwise-correlation matrix among the candidate features (session "
         "prompt Step 7-iii), computed up front, pooled across all complete-case "
         "rows, all five airports")
    pooled = [MERGED[st][d] for st in AIRPORTS for d in MERGED[st]]
    corr_matrix_data = np.array([[r[c] for c in CORR_COLS] for r in pooled], dtype=float)
    corr = np.corrcoef(corr_matrix_data, rowvar=False)
    header = "".join(f"{c:>14}" for c in CORR_COLS)
    print(f"\n    n = {len(pooled)} pooled rows")
    print(f"    {'':<28}{header}")
    for i, c in enumerate(CORR_COLS):
        row_str = "".join(f"{corr[i, j]:>14.3f}" for j in range(len(CORR_COLS)))
        print(f"    {c:<28}{row_str}")

    with open(CORR_CSV, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["feature"] + CORR_COLS)
        for i, c in enumerate(CORR_COLS):
            w.writerow([c] + [round(float(corr[i, j]), 6) for j in range(len(CORR_COLS))])
    print(f"\n    Wrote correlation matrix: {CORR_CSV}")

    # ------------------------------------------------------------ obs join
    line("Loading observations and joining onto the complete-case feature rows "
         "(D14 pairing rule, SPEC 4.5; SPEC 2.2 drop-and-count, nothing filled)")
    OBS_ALL = {}
    JOINED = {}
    for st, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(st, target_hour)
        OBS_ALL[st] = obs_all
        rows = []
        no_obs = 0
        for d in sorted(MERGED[st].keys()):
            o = obs_all.get(d)
            if o is None:
                no_obs += 1
                continue
            base = MERGED[st][d]
            rows.append({**base, "obs": o, "resid": o - base["fc"]})
        JOINED[st] = rows
        print(f"    {st:<6} complete-case rows={len(MERGED[st]):<6} "
              f"joined (usable obs)={len(rows):<6} no usable obs={no_obs} "
              f"(obs-record diagnostics: outside_15min={obs_far}, no_temp_field={obs_no_temp})")

    # ------------------------------------------------------------ fit/score machinery

    FIT_CACHE = {}   # (frozenset(codes), station, fold_label) -> mae
    RAW_PERSIST_CACHE = {}  # (station, fold_label) -> (raw_mae, persist_mae, n_train, n_test, no_prev)
    ad_hoc_fits = []  # log of variants fit beyond the 14-variant ladder
    LADDER_CODE_SETS = {frozenset(c) for _, c in VARIANT_LADDER}

    def get_train_test_rows(station, fold_label):
        tr_s, tr_e, te_s, te_e = FOLD_BOUNDS[fold_label]
        assert tr_e < te_s, f"{station} {fold_label}: train_end not before test_start"
        train_rows = [r for r in JOINED[station] if tr_s <= r["date"] <= tr_e]
        test_rows = [r for r in JOINED[station] if te_s <= r["date"] <= te_e]
        return train_rows, test_rows

    def raw_persist(station, fold_label):
        key = (station, fold_label)
        if key in RAW_PERSIST_CACHE:
            return RAW_PERSIST_CACHE[key]
        train_rows, test_rows = get_train_test_rows(station, fold_label)
        e_raw = [r["fc"] - r["obs"] for r in test_rows]
        no_prev = 0
        e_persist = []
        for r in test_rows:
            prev = OBS_ALL[station].get(r["date"] - timedelta(days=1))
            if prev is None:
                no_prev += 1
                continue
            e_persist.append(float(prev) - r["obs"])
        result = (mae(e_raw), mae(e_persist), len(train_rows), len(test_rows), no_prev)
        RAW_PERSIST_CACHE[key] = result
        return result

    def fit_and_score(codes, station, fold_label):
        key = (frozenset(codes), station, fold_label)
        if key in FIT_CACHE:
            return FIT_CACHE[key]
        train_rows, test_rows = get_train_test_rows(station, fold_label)
        keys = BASE_KEYS + sum((FAMILY_KEYS[c] for c in sorted(codes)), [])
        x_tr = features_matrix(train_rows, keys)
        y_tr = np.array([r["resid"] for r in train_rows], dtype=float)
        m = lgb.LGBMRegressor(**LGB_PARAMS)
        m.fit(x_tr, y_tr)
        x_te = features_matrix(test_rows, keys)
        pred = m.predict(x_te)
        e_model = [(r["fc"] + float(pred[i])) - r["obs"] for i, r in enumerate(test_rows)]
        result = mae(e_model)
        FIT_CACHE[key] = result
        if frozenset(codes) not in LADDER_CODE_SETS:
            ad_hoc_fits.append((codes_label(codes), station, fold_label))
        return result

    def avg_mae(codes, fold_label, airports):
        return sum(fit_and_score(codes, st, fold_label) for st in airports) / len(airports)

    def skill_pct(codes, fold_label, airports):
        b = avg_mae([], fold_label, airports)
        m_ = avg_mae(codes, fold_label, airports)
        return 100 * (1 - m_ / b)

    def fold_averaged_skill(codes, airports):
        skills = [skill_pct(codes, fl, airports) for fl in FOLD_LABELS]
        return sum(skills) / len(skills), skills

    # ------------------------------------------------------------ Step 6: the 14-variant ladder grid

    line("Fitting the 14-variant ladder on all three folds, all five airports "
         "(D21.4/D48.6 frozen LightGBM settings, identical features at every "
         "airport, no per-airport selection)")
    grid_rows = []
    for name, codes in VARIANT_LADDER:
        for st in ALL_STATIONS:
            for fold_label in FOLD_LABELS:
                m_mae = fit_and_score(codes, st, fold_label)
                raw_mae, persist_mae, n_tr, n_te, no_prev = raw_persist(st, fold_label)
                b_mae = fit_and_score([], st, fold_label)
                delta = m_mae - b_mae
                skill = 100 * (1 - m_mae / b_mae) if b_mae else float("nan")
                grid_rows.append(dict(
                    station=st, fold=fold_label, variant=name, codes=",".join(codes),
                    n_train=n_tr, n_test=n_te, no_prev=no_prev,
                    raw_mae=round(raw_mae, 4), persist_mae=round(persist_mae, 4),
                    mae=round(m_mae, 4), delta_vs_B=round(delta, 4),
                    skill_vs_B_pct=round(skill, 2) if skill == skill else "",
                ))
    print(f"    Fit {len(VARIANT_LADDER)} variants x {len(ALL_STATIONS)} airports "
          f"x {len(FOLD_LABELS)} folds = {len(grid_rows)} rows.")
    for r in grid_rows:
        print(f"    {r['station']:<6}{r['fold']:<10}{r['variant']:<16}"
              f"MAE={r['mae']:.3f}  delta_vs_B={r['delta_vs_B']:+.3f}  "
              f"skill_vs_B={r['skill_vs_B_pct']}%")

    with open(GRID_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["station", "fold", "variant", "codes", "n_train",
                                           "n_test", "no_prev", "raw_mae", "persist_mae",
                                           "mae", "delta_vs_B", "skill_vs_B_pct"])
        w.writeheader()
        w.writerows(grid_rows)
    print(f"\n    Wrote grid: {GRID_CSV} ({len(grid_rows)} rows)")

    # ------------------------------------------------------------ summary tables (all five airports)

    def summarize(level_name, group_key, group_values, airports):
        rows = []
        for gv in group_values:
            print(f"\n    {gv}:")
            b_mean = None
            for name, codes in VARIANT_LADDER:
                if group_key == "station":
                    maes = [r["mae"] for r in grid_rows if r["station"] == gv and r["variant"] == name]
                else:
                    maes = [r["mae"] for r in grid_rows if r["fold"] == gv and r["variant"] == name]
                mean_mae = sum(maes) / len(maes) if maes else float("nan")
                if name == "B":
                    b_mean = mean_mae
                delta = mean_mae - b_mean
                skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
                print(f"        {name:<16} mean_MAE={mean_mae:.3f}  "
                      f"delta_vs_B={delta:+.3f}  skill_vs_B={skill:+.1f}%  (n={len(maes)})")
                rows.append(dict(level=level_name, station=gv if group_key == "station" else "",
                                  fold=gv if group_key == "fold" else "", variant=name,
                                  mean_mae=round(mean_mae, 4), delta_vs_B=round(delta, 4),
                                  skill_vs_B_pct=round(skill, 2) if skill == skill else ""))
        return rows

    line("Fold-averaged per airport (mean across the three folds, all five airports)")
    summary_rows = summarize("fold_averaged_per_airport", "station", ALL_STATIONS, ALL_STATIONS)

    line("Airport-averaged per fold (mean across the five airports)")
    summary_rows += summarize("airport_averaged_per_fold", "fold", FOLD_LABELS, ALL_STATIONS)

    line("Grand overall (mean across all five airports and all three folds, n=15 airport-folds)")
    grand_skill = {}
    b_mean = None
    for name, codes in VARIANT_LADDER:
        maes = [r["mae"] for r in grid_rows if r["variant"] == name]
        mean_mae = sum(maes) / len(maes)
        if name == "B":
            b_mean = mean_mae
        delta = mean_mae - b_mean
        skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
        grand_skill[name] = skill
        print(f"    {name:<16} mean_MAE={mean_mae:.3f}  delta_vs_B={delta:+.3f}  "
              f"skill_vs_B={skill:+.1f}%  (n={len(maes)})")
        summary_rows.append(dict(level="grand_overall", station="", fold="", variant=name,
                                  mean_mae=round(mean_mae, 4), delta_vs_B=round(delta, 4),
                                  skill_vs_B_pct=round(skill, 2) if skill == skill else ""))

    with open(SUMMARY_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["level", "station", "fold", "variant", "mean_mae",
                                           "delta_vs_B", "skill_vs_B_pct"])
        w.writeheader()
        w.writerows(summary_rows)
    print(f"\n    Wrote summary: {SUMMARY_CSV} ({len(summary_rows)} rows)")

    # ------------------------------------------------------------ Step 7-i: per-row feature-integrity check

    line("Integrity check (i) -- per-row feature-integrity: every feature "
         "column in the assembled table matches its committed source file, "
         "checked on every row (not a spot check)")
    max_diffs = {c: 0.0 for c in CORR_COLS}
    n_checked = 0
    for st in AIRPORTS:
        for d, row in MERGED[st].items():
            ua, mo, pr, ra, pc = (UPPER_AIR[st][d], MOISTURE[st][d], PRESSURE[st][d],
                                   RADIATION[st][d], PRECIP[st][d])
            n_checked += 1
            max_diffs["lapse_rate_t2_t850"] = max(max_diffs["lapse_rate_t2_t850"],
                                                   abs(row["lapse_rate_t2_t850"] - ua["lapse_rate_t2_t850"]))
            max_diffs["t850"] = max(max_diffs["t850"], abs(row["t850"] - ua["t850"]))
            max_diffs["t925"] = max(max_diffs["t925"], abs(row["t925"] - ua["t925"]))
            max_diffs["t700"] = max(max_diffs["t700"], abs(row["t700"] - ua["t700"]))
            max_diffs["relative_humidity_2m"] = max(max_diffs["relative_humidity_2m"],
                                                      abs(row["relative_humidity_2m"] - mo["relative_humidity_2m"]))
            max_diffs["pressure_tendency_3h_hpa"] = max(max_diffs["pressure_tendency_3h_hpa"],
                                                          abs(row["pressure_tendency_3h_hpa"] - pr["pressure_tendency_3h_hpa"]))
            max_diffs["dswrf_2h_wm2"] = max(max_diffs["dswrf_2h_wm2"],
                                             abs(row["dswrf_2h_wm2"] - ra["dswrf_2h_wm2"]))
            max_diffs["precip_rate_mmh"] = max(max_diffs["precip_rate_mmh"],
                                                abs(row["precip_rate_mmh"] - pc["precip_rate_mmh"]))
            expected_floor = max(mo["dewpoint_depression_t2m"], 0.0)
            max_diffs["dewpoint_depression_t2m_floored"] = max(
                max_diffs["dewpoint_depression_t2m_floored"],
                abs(row["dewpoint_depression_t2m_floored"] - expected_floor))
    print(f"\n    n_checked = {n_checked} rows")
    for c in CORR_COLS:
        print(f"    {c:<32} max_abs_diff = {max_diffs[c]:.9f}")
    overall_pass = all(v == 0.0 for v in max_diffs.values())
    print(f"\n    {'PASS' if overall_pass else 'FAIL'} -- every candidate feature column "
          f"matches its committed source file (or D53/F100's own frozen floor transform "
          f"applied to the stored raw column) exactly, on every row.")
    if not overall_pass:
        raise AssertionError("SESSION 61 STOP SIGNAL: feature-integrity check failed -- see diffs above.")

    # ------------------------------------------------------------ Step 7-ii: internal-consistency check

    line("Integrity check (ii) -- internal-consistency: the refit-B 2025-26 "
         "fold reproduces F94/F96/F99-F105's own raw-GFS and persistence MAE "
         "and row counts at every airport, within rounding")
    reference = {
        "EGLC": (1.254, 2.096, 364), "LFPG": (1.382, 2.300, 364),
        "DSM": (1.733, 4.003, 365), "YSDU": (1.317, 2.669, 356), "RNO": (1.512, 2.490, 365),
    }
    for st in ALL_STATIONS:
        raw_m, persist_m, n_tr, n_te, no_prev = raw_persist(st, "2025-26")
        ref_raw, ref_persist, ref_n = reference[st]
        match = (abs(raw_m - ref_raw) < 0.001 and abs(persist_m - ref_persist) < 0.001
                 and n_te == ref_n)
        print(f"    {st}: this session raw={raw_m:.4f} persist={persist_m:.4f} n={n_te}   |   "
              f"reference raw={ref_raw:.3f} persist={ref_persist:.3f} n={ref_n}   "
              f"-- {'MATCH' if match else 'MISMATCH'}")

    # ------------------------------------------------------------ selection rule (steps 8-12)

    line("Selection rule (D57 Steps 8-12), applied mechanically. All keep/drop "
         "votes average over the four non-DSM airports (EGLC, LFPG, YSDU, RNO) "
         "-- see this script's own module docstring, interpretation decision 1.")

    full_codes = {"L", "D", "T", "R", "P"}
    core = set(full_codes)
    round_num = 1
    while True:
        full_skill, full_perfold = fold_averaged_skill(sorted(core), NON_DSM)
        sub(f"Round {round_num} -- current set B+{','.join(sorted(core))}, "
            f"fold-averaged skill vs B (non-DSM) = {full_skill:+.2f}%, "
            f"per-fold = {[round(s, 2) for s in full_perfold]}")
        detail = {}
        droppable = []
        for feat in sorted(core):
            reduced = core - {feat}
            red_label = codes_label(reduced)
            red_skill, red_perfold = fold_averaged_skill(sorted(reduced), NON_DSM)
            magnitude = full_skill - red_skill
            robust = all(full_perfold[i] > red_perfold[i] for i in range(3))
            keep = (magnitude >= TAU_PCT) and robust
            detail[feat] = dict(reduced=red_label, magnitude=magnitude, robust=robust,
                                 keep=keep, red_skill=red_skill, red_perfold=red_perfold)
            print(f"        remove {feat:<5} -> {red_label:<20} skill={red_skill:+.2f}%  "
                  f"magnitude(loss if removed)={magnitude:+.2f}pp  "
                  f"robust(worse in all 3 folds)={robust}  "
                  f"-> {'KEEP' if keep else 'DROP CANDIDATE'}")
            if not keep:
                droppable.append(feat)
        if not droppable:
            print(f"\n    Round {round_num}: nothing flagged droppable -- core set is final.")
            break
        if len(droppable) == 1:
            chosen = droppable[0]
            print(f"\n    Round {round_num}: one droppable feature -- dropping {chosen}.")
        else:
            def sort_key(f_):
                return (detail[f_]["magnitude"], DROP_ORDER.index(f_))
            chosen = min(droppable, key=sort_key)
            print(f"\n    Round {round_num}: correlated-feature safeguard triggered -- "
                  f"{len(droppable)} features flagged droppable together "
                  f"({droppable}). Dropping only the least-damage one: {chosen} "
                  f"(magnitude={detail[chosen]['magnitude']:+.2f}pp).")
        core = core - {chosen}
        round_num += 1
        if round_num > 10:
            raise RuntimeError("SESSION 61 STOP SIGNAL: selection loop did not converge.")

    core_set = core
    print(f"\n    CORE SET (survivors of leave-one-out backward elimination): "
          f"B+{','.join(sorted(core_set)) if core_set else '(none)'}")

    # ------------------------------------------------------------ parked options (step 11)

    line("Parked-option tests (D57 Step 11): B+core+rh (non-DSM vote) and "
         "B+core+plev (ALL FIVE airports -- plev's own explicit override)")

    core_skill_nondsm, core_perfold_nondsm = fold_averaged_skill(sorted(core_set), NON_DSM)
    rh_set = core_set | {"rh"}
    rh_skill, rh_perfold = fold_averaged_skill(sorted(rh_set), NON_DSM)
    rh_magnitude = rh_skill - core_skill_nondsm
    rh_robust = all(rh_perfold[i] > core_perfold_nondsm[i] for i in range(3))
    rh_adopt = (rh_magnitude >= TAU_PCT) and rh_robust
    print(f"    rh   : core skill(non-DSM)={core_skill_nondsm:+.2f}%  "
          f"core+rh skill(non-DSM)={rh_skill:+.2f}%  magnitude={rh_magnitude:+.2f}pp  "
          f"robust(helps in all 3 folds)={rh_robust}  -> {'ADOPT' if rh_adopt else 'DO NOT ADOPT'}")

    core_skill_all5, core_perfold_all5 = fold_averaged_skill(sorted(core_set), ALL_STATIONS)
    plev_set = core_set | {"plev"}
    plev_skill, plev_perfold = fold_averaged_skill(sorted(plev_set), ALL_STATIONS)
    plev_magnitude = plev_skill - core_skill_all5
    plev_robust = all(plev_perfold[i] > core_perfold_all5[i] for i in range(3))
    plev_adopt = (plev_magnitude >= TAU_PCT) and plev_robust
    print(f"    plev : core skill(ALL 5) ={core_skill_all5:+.2f}%  "
          f"core+plev skill(ALL 5)={plev_skill:+.2f}%  magnitude={plev_magnitude:+.2f}pp  "
          f"robust(helps in all 3 folds)={plev_robust}  -> {'ADOPT' if plev_adopt else 'DO NOT ADOPT'}")

    final_set = set(core_set)
    if rh_adopt:
        final_set.add("rh")
    if plev_adopt:
        final_set.add("plev")
    print(f"\n    FINAL SET (mechanical rule output, NOT a verdict): "
          f"B+{','.join(sorted(final_set))}")

    # ------------------------------------------------------------ joint backstop (steps 13-14)

    line("Joint backstop (D57 Steps 13-14): refit the exact final set and "
         "check (a) beats B, worse-by-sign in no fold; (b) not meaningfully "
         "worse than the full B+LDTRP model. Non-DSM basis, per interpretation "
         "decision 1.")

    final_skill, final_perfold = fold_averaged_skill(sorted(final_set), NON_DSM)
    final_skill_all5, final_perfold_all5 = fold_averaged_skill(sorted(final_set), ALL_STATIONS)
    full5_skill, full5_perfold = fold_averaged_skill(sorted(full_codes), NON_DSM)

    check_a_beats_b = final_skill >= TAU_PCT
    check_a_no_worse_fold = all(s >= 0 for s in final_perfold)
    check_a = check_a_beats_b and check_a_no_worse_fold
    gap_vs_full = full5_skill - final_skill
    check_b = gap_vs_full <= TAU_PCT

    print(f"    final set skill vs B (non-DSM, fold-averaged): {final_skill:+.2f}%  "
          f"per-fold: {[round(s, 2) for s in final_perfold]}")
    print(f"    final set skill vs B (ALL 5, fold-averaged)   : {final_skill_all5:+.2f}%  "
          f"per-fold: {[round(s, 2) for s in final_perfold_all5]}")
    print(f"    full B+LDTRP skill vs B (non-DSM, fold-averaged): {full5_skill:+.2f}%  "
          f"per-fold: {[round(s, 2) for s in full5_perfold]}")
    print(f"\n    check (a) beats B by >= {TAU_PCT}pp fold-averaged: {check_a_beats_b}  "
          f"AND worse-by-sign in no fold: {check_a_no_worse_fold}  => {check_a}")
    print(f"    check (b) not meaningfully worse than full B+LDTRP "
          f"(gap={gap_vs_full:+.2f}pp <= {TAU_PCT}pp): {check_b}")

    backstop_pass = check_a and check_b
    if backstop_pass:
        line(f"JOINT BACKSTOP: PASS. Mechanically-produced set: "
             f"B+{','.join(sorted(final_set))}. This is the selection rule's "
             f"mechanical OUTPUT, not a verdict or a decision -- the session-62 "
             f"owner review makes the call.")
    else:
        line("JOINT BACKSTOP: FAILED -- HALT AND SURFACE (D57 Step 14). Per D57, "
             "this script does NOT auto-unwind and does NOT auto-pick a "
             "different set. The failure and the full grid above are surfaced "
             "for the session-62 owner review to resolve.")
        print(f"    check (a) = {check_a}, check (b) = {check_b}")
        print(f"    Mechanically-produced candidate set (NOT adopted, backstop failed): "
              f"B+{','.join(sorted(final_set))}")

    # ------------------------------------------------------------ ad hoc fit log

    line("Ad hoc fits beyond the 14-variant ladder, logged for transparency "
         "(needed by the selection rule's own iterative LOO / parked-option / "
         "backstop steps)")
    distinct_ad_hoc = sorted(set(ad_hoc_fits))
    print(f"    {len(distinct_ad_hoc)} distinct ad hoc (variant, station, fold) fits beyond the ladder:")
    for v, st, fl in distinct_ad_hoc:
        print(f"        {v:<24} {st:<6} {fl}")

    line("END")
    print("This script reports the 14-variant grid, the selection trace, and the")
    print("joint-backstop outcome. NO VERDICT was computed -- the single final")
    print("feature set is the session-62 owner review's call, per the session")
    print("prompt. No row of the reserved 2024-08-01..2025-07-31 confirmation")
    print("year (D51) was read, loaded, or scored at any point in this script.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
