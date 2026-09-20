"""Session 56: the staged E4 (radiation) feature experiment. A LEARNING
experiment, not a pass/fail gate -- runs ONLY on the three non-reserved
EXPERIMENT_FOLDS (scripts/session48_reserved_year.py). The reserved 2024-25
confirmation year (D51) is never read, at all, by this script. This is the
direct analogue of session 50/F99 (E1), session 52/F100 (E2), and session
54/F101 (E3), for the E4 (radiation) family.

Fits four variants per airport, per fold, all on the SAME LightGBM settings
(D21.4/D48.6, unchanged) and the SAME features across every airport (no
per-airport feature selection, RNO included):

  B     -- the frozen 5-feature baseline (temp, season_sin, season_cos,
            cloud_cover, wind_speed_10m), REFIT on these three folds. Not a
            reuse of F94/F96/F99/F100/F101, which were fit on different
            windows. Not B+L, B+D, or B+T either -- D52/D53/D54's own
            "measurement baseline is unchanged" rule: B stays the frozen
            5-feature set only.
  B+R   -- B plus the resolved dswrf_2h_wm2 feature (F102's own single
            physically-consistent 2-hour-window shortwave feature).
  B+Rv  -- B+R plus the two raw de-accumulation-endpoint columns,
            dswrf_ave_to_lead_wm2 and dswrf_ave_to_lead_minus2_wm2.
  B+v   -- B plus those two raw endpoint columns, WITHOUT the resolved
            dswrf_2h_wm2.

NOTE (session prompt's own framing, restated here): E4's "raw" set differs
in KIND from E1/E2/E3's. E1-E3's raw fields were independent physical
variables (t925/t850/t700; RH/DPT/SPFH; PRMSL/PRES:surface). E4's two raw
endpoints are instead the two accumulation-window averages the resolved
feature dswrf_2h_wm2 is ITSELF DERIVED FROM (F102: dswrf_2h_wm2 = (to_lead*6
- to_lead_minus2*4)/2 at the lead-24 airports; dswrf_2h_wm2 == to_lead
directly at the lead-26 airports, no second endpoint exists there). So B+Rv
and B+v test whether the model does better with the raw energy endpoints
than with the clean, physically-resolved 2-hour rate -- not whether a
genuinely independent variable adds anything.

A design decision this session had to make, not specified by the session
prompt: dswrf_ave_to_lead_minus2_wm2 is blank in the session-55 output files
at YSDU and RNO (the lead-26 airports), because F102's own build never
fetched a second message there -- the native window is already the target
2-hour window, so no de-accumulation, and no second endpoint, exists. To
give B+Rv/B+v a well-defined, identically-shaped feature vector at all five
airports without inventing a number (SPEC 2.2), dswrf_ave_to_lead_minus2_wm2
is set equal to dswrf_ave_to_lead_wm2 at those two airports -- the honest
statement that there IS no earlier, distinct endpoint there, not a filled
gap. This is reported plainly below (see load_radiation_features()) and
affects only the B+Rv/B+v feature vectors, never dswrf_2h_wm2 or B/B+R.

Two sanity checks run before any model is fit (session prompt, both must
PASS):
  1. The reserved-year guard: every EXPERIMENT_FOLDS entry is run through
     assert_reserved_year_excluded() before anything is loaded or fit, plus
     a defensive per-row scan of the loaded data.
  2. Feature-resolution check, on EVERY row (not a spot check): at the
     lead-24 airports (EGLC, LFPG, DSM), dswrf_2h_wm2 == (dswrf_ave_to_lead_
     wm2*6 - dswrf_ave_to_lead_minus2_wm2*4) / 2, within rounding tolerance;
     at the lead-26 airports (YSDU, RNO), dswrf_2h_wm2 == dswrf_ave_to_lead_
     wm2 directly. Re-confirms the committed session-55 files are the ones
     being read.

Reports raw GFS and persistence alongside the four variants, for context
only (matching the project's own convention). No pass/fail verdict is
computed anywhere in this script (session prompt: "the E4 family call is
the owner's review decision in the NEXT session").
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

LEAD24_STATIONS = {"EGLC", "LFPG", "DSM"}   # native 6h window, de-accumulated
LEAD26_STATIONS = {"YSDU", "RNO"}           # native 2h window, used directly

RADIATION_PATHS = [
    PROCESSED / "session55_v16_window_with_radiation.csv",
    PROCESSED / "session55_sealed_window_with_radiation.csv",
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
# and airport -- nothing tuned, nothing hand-picked.
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

# Feature keys -> looked up from each row dict via make_feature_vector().
KEYS_B = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m"]
KEYS_BR = KEYS_B + ["dswrf_2h_wm2"]
KEYS_BRV = KEYS_BR + ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2"]
KEYS_BV = KEYS_B + ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2"]

VARIANTS = [
    ("B", KEYS_B),
    ("B+R", KEYS_BR),
    ("B+Rv", KEYS_BRV),
    ("B+v", KEYS_BV),
]

OUT = ROOT / "notes" / "session-56-e4-experiment-output.txt"
GRID_CSV = PROCESSED / "session56_e4_experiment_grid.csv"
SUMMARY_CSV = PROCESSED / "session56_e4_experiment_summary.csv"


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
        "dswrf_2h_wm2": r["dswrf_2h"],
        "dswrf_ave_to_lead_wm2": r["dswrf_to_lead"],
        "dswrf_ave_to_lead_minus2_wm2": r["dswrf_to_lead_minus2"],
    }
    return [lookup[k] for k in keys]


def features_matrix(rows, keys):
    return np.array([make_feature_vector(r, keys) for r in rows], dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


# ------------------------------------------------------------------ sanity checks

def sanity_check_feature_resolution():
    """Session prompt item 2: re-confirm, on EVERY row (not a spot check),
    that dswrf_2h_wm2 really is what F102 says it is -- the de-accumulation
    identity at the three lead-24 airports, direct equality at the two
    lead-26 airports. STOP if any airport exceeds a small rounding
    tolerance (values are stored rounded to 3 decimal places, so a
    tolerance a little above the largest possible rounding error is used)."""
    n_checked = {st: 0 for st in AIRPORTS}
    max_abs_diff = {st: 0.0 for st in AIRPORTS}
    failures = []
    tol = 0.01  # W/m2 -- comfortably above the ~0.0025 max rounding error
    for path in RADIATION_PATHS:
        with open(path) as f:
            for row in csv.DictReader(f):
                st = row["station"]
                if st not in AIRPORTS:
                    continue
                dswrf_2h = float(row["dswrf_2h_wm2"])
                to_lead = float(row["dswrf_ave_to_lead_wm2"])
                if st in LEAD24_STATIONS:
                    to_lead_m2 = float(row["dswrf_ave_to_lead_minus2_wm2"])
                    expected = (to_lead * 6 - to_lead_m2 * 4) / 2
                else:
                    expected = to_lead
                diff = abs(expected - dswrf_2h)
                n_checked[st] += 1
                max_abs_diff[st] = max(max_abs_diff[st], diff)
                if diff > tol:
                    failures.append((st, row["target_date"], to_lead, expected, dswrf_2h, diff))
    print(f"    {'station':<8} {'method':<28} {'n_checked':>10} {'max_abs_diff':>14}")
    for st in AIRPORTS:
        method = "de-accum (6h-4h)/2" if st in LEAD24_STATIONS else "direct equality"
        print(f"    {st:<8} {method:<28} {n_checked[st]:>10} {max_abs_diff[st]:>14.9f}")
    if failures:
        print(f"\n    {len(failures)} row(s) FAILED the feature-resolution check "
              f"(tolerance {tol} W/m2):")
        for f_ in failures[:20]:
            print(f"      {f_}")
        raise AssertionError(
            "SESSION 56 STOP SIGNAL: dswrf_2h_wm2's resolution from the raw "
            "endpoint columns does not hold within tolerance at one or more "
            "rows -- see failures printed above. Stopping before fitting any "
            "model, per the session prompt.")
    print(f"\n    PASS -- dswrf_2h_wm2 matches its own resolution formula "
          f"(de-accumulation at the three lead-24 airports, direct equality "
          f"at the two lead-26 airports) within {tol} W/m2 at all "
          f"{sum(n_checked.values())} rows checked, across all five airports.")


def sanity_check_guard():
    """Session prompt item 1: every EXPERIMENT_FOLDS entry must pass
    assert_reserved_year_excluded() before anything is loaded or fit."""
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e}  test={te_s}..{te_e}  "
              f"-- PASS (guard did not raise)")
    print(f"\n    PASS -- all {len(EXPERIMENT_FOLDS)} EXPERIMENT_FOLDS entries "
          f"cleared assert_reserved_year_excluded() before any data was loaded.")


# ------------------------------------------------------------------ loading

def load_radiation_features():
    """station -> {date: {fc, cloud, wind, dswrf_2h, dswrf_to_lead,
    dswrf_to_lead_minus2}}. Reads session55's own output files, which
    already exclude every date in the reserved 2024-08-01..2025-07-31 year
    (D51) -- verified here with a defensive per-row scan, not assumed.

    Design decision (module docstring, above): at the two lead-26 airports
    (YSDU, RNO) dswrf_ave_to_lead_minus2_wm2 is blank in the source files
    (no second message was ever fetched -- F102). Here it is set equal to
    dswrf_ave_to_lead_wm2 -- the honest statement that no distinct earlier
    endpoint exists there, not an invented value. This affects only the
    B+Rv/B+v feature vectors."""
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    n_minus2_substituted = {st: 0 for st in AIRPORTS}
    for path in RADIATION_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue  # defensive only -- session55's own output should have none
                to_lead = float(r["dswrf_ave_to_lead_wm2"])
                m2_raw = (r.get("dswrf_ave_to_lead_minus2_wm2") or "").strip()
                if m2_raw == "":
                    to_lead_m2 = to_lead  # design decision -- see docstring
                    n_minus2_substituted[st] += 1
                else:
                    to_lead_m2 = float(m2_raw)
                out[st][d] = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                    "dswrf_2h": float(r["dswrf_2h_wm2"]),
                    "dswrf_to_lead": to_lead,
                    "dswrf_to_lead_minus2": to_lead_m2,
                }
    if reserved_hits:
        raise AssertionError(
            f"SESSION 56 STOP SIGNAL: {reserved_hits} row(s) inside the "
            "reserved 2024-25 confirmation year were found in session55's "
            "own output files -- refusing to proceed (D51).")
    print("    dswrf_ave_to_lead_minus2_wm2 substitution count (design "
          "decision, module docstring -- expected: 0 at the three lead-24 "
          "airports, every row at the two lead-26 airports):")
    for st in AIRPORTS:
        expected_kind = "0 (lead-24, real de-accum endpoint)" if st in LEAD24_STATIONS \
            else "every row (lead-26, no second endpoint exists)"
        print(f"      {st}: substituted {n_minus2_substituted[st]} row(s)  "
              f"(expected: {expected_kind})")
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


def all_days(start, end):
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def join_rows(feat_for_station, obs_for_station, date_lo, date_hi):
    """One row per day with a radiation feature row AND a usable
    observation, D14 drop-count rule (SPEC 2.2: nothing filled)."""
    rows = []
    no_feat = no_obs = 0
    for d in all_days(date_lo, date_hi):
        g = feat_for_station.get(d)
        if g is None:
            no_feat += 1
            continue
        o = obs_for_station.get(d)
        if o is None:
            no_obs += 1
            continue
        rows.append({
            "date": d,
            "fc": g["fc"], "cloud": g["cloud"], "wind": g["wind"],
            "dswrf_2h": g["dswrf_2h"], "dswrf_to_lead": g["dswrf_to_lead"],
            "dswrf_to_lead_minus2": g["dswrf_to_lead_minus2"],
            "obs": o, "resid": o - g["fc"],
        })
    return rows, no_feat, no_obs


# ------------------------------------------------------------------ per fold/airport run

def run_fold(station, fold_label, train_start, train_end, test_start, test_end,
             joined_rows, obs_all, grid_rows):
    assert train_end < test_start, \
        f"{station} {fold_label}: train_end not before test_start"

    train_rows = [r for r in joined_rows if train_start <= r["date"] <= train_end]
    test_rows = [r for r in joined_rows if test_start <= r["date"] <= test_end]
    for r in train_rows:
        assert train_start <= r["date"] <= train_end and r["date"] < test_start
    for r in test_rows:
        assert test_start <= r["date"] <= test_end

    if not train_rows or not test_rows:
        print(f"    {station} {fold_label}: SKIPPED -- no rows "
              f"(train={len(train_rows)}, test={len(test_rows)})")
        return

    e_raw = [r["fc"] - r["obs"] for r in test_rows]
    common_persist = []
    no_prev = 0
    for r in test_rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        common_persist.append((r, float(prev)))
    e_persist = [p - r["obs"] for r, p in common_persist]
    raw_mae = mae(e_raw)
    persist_mae = mae(e_persist)

    print(f"    {station} {fold_label:<10} train={train_start}..{train_end} "
          f"({len(train_rows)}d) test={test_start}..{test_end} ({len(test_rows)}d) "
          f"no_prev(persist)={no_prev}")
    print(f"        raw GFS (GRIB) : {raw_mae:.3f}   persistence: {persist_mae:.3f}")

    variant_mae = {}
    for variant_label, keys in VARIANTS:
        x_tr = features_matrix(train_rows, keys)
        y_tr = np.array([r["resid"] for r in train_rows], dtype=float)
        m = lgb.LGBMRegressor(**LGB_PARAMS)
        m.fit(x_tr, y_tr)

        x_te = features_matrix(test_rows, keys)
        pred = m.predict(x_te)
        e_model = [(r["fc"] + float(pred[i])) - r["obs"] for i, r in enumerate(test_rows)]
        model_mae = mae(e_model)
        variant_mae[variant_label] = model_mae

    b_mae = variant_mae["B"]
    for variant_label, _ in VARIANTS:
        m_mae = variant_mae[variant_label]
        delta = m_mae - b_mae
        skill_vs_b = 100 * (1 - m_mae / b_mae) if b_mae else float("nan")
        print(f"        {variant_label:<5} MAE={m_mae:.3f}  "
              f"delta_vs_B={delta:+.3f}  skill_vs_B={skill_vs_b:+.1f}%")
        grid_rows.append(dict(
            station=station, fold=fold_label, variant=variant_label,
            n_train=len(train_rows), n_test=len(test_rows),
            raw_mae=round(raw_mae, 4), persist_mae=round(persist_mae, 4),
            mae=round(m_mae, 4), delta_vs_B=round(delta, 4),
            skill_vs_B_pct=round(skill_vs_b, 2) if skill_vs_b == skill_vs_b else "",
        ))


# ------------------------------------------------------------------ main

def main():
    if len(sys.argv) != 1:
        raise SystemExit("this script takes no arguments")

    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 56 -- E4 (radiation) staged feature experiment. A "
         "LEARNING READING, NOT A PASS/FAIL GATE. Runs ONLY on the three "
         "non-reserved EXPERIMENT_FOLDS. The reserved 2024-25 confirmation "
         "year (D51) is never read this session.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"reserved confirmation year (never touched): {RESERVED_YEAR_START} .. {RESERVED_YEAR_END}")
    print(f"model settings (D48.6/D21.4, identical for every variant/fold/airport): {LGB_PARAMS}")
    print(f"B     features: {KEYS_B}")
    print(f"B+R   features: {KEYS_BR}")
    print(f"B+Rv  features: {KEYS_BRV}")
    print(f"B+v   features: {KEYS_BV}")
    print("NOTE: B is the frozen 5-feature set only -- E1's lapse_rate_t2_t850")
    print("(D52), E2's dewpoint_depression_t2m_floored (D53), and E3's")
    print("pressure_tendency_3h_hpa (D54) are NOT added to B here; they enter")
    print("only at the combine phase.")
    print()
    print("THE SPECIFIC QUESTION THIS EXPERIMENT ANSWERS: cloud_cover is")
    print("ALREADY in the frozen baseline B, and cloud is the dominant control")
    print("on how much shortwave reaches the ground (F97). So this is")
    print("specifically a test of whether radiation adds skill BEYOND the")
    print("cloud feature already present -- a marginal-over-cloud test, not a")
    print("from-scratch test. A small or null B+R result is a plausible,")
    print("honest outcome (radiation largely redundant with cloud), not a")
    print("failure. DSM is read as the diagnostic airport (F96: most")
    print("headroom, where cloud/wind were already marginal).")
    print()
    print("NOTE on the E4 'v' set's own KIND (differs from E1-E3): E1-E3's raw")
    print("fields were independent physical variables. E4's two raw endpoints")
    print("(dswrf_ave_to_lead_wm2, dswrf_ave_to_lead_minus2_wm2) are instead")
    print("the two accumulation-window averages the resolved dswrf_2h_wm2 is")
    print("ITSELF DERIVED FROM. So B+Rv/B+v test whether the model does")
    print("better with the raw energy endpoints than with the clean,")
    print("physically-resolved 2-hour rate -- not whether an independent")
    print("variable adds anything.")

    line("Sanity check 1 -- the reserved-year guard, run on every "
         "EXPERIMENT_FOLDS entry before anything is loaded or fit")
    sanity_check_guard()

    line("Sanity check 2 -- feature-resolution check, checked on EVERY row "
         "of both session55 output files (not a spot check)")
    sanity_check_feature_resolution()

    line("Loading radiation features and observations (both sanity checks passed)")
    radiation = load_radiation_features()
    print("    radiation feature files loaded, reserved-year rows: 0 found "
          "(defensive scan, per load_radiation_features()).")

    grid_rows = []

    line("Per-airport, per-fold, per-variant results")
    for station, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(station, target_hour)
        span_lo = min(radiation[station])
        span_hi = max(radiation[station])
        joined_rows, no_feat, no_obs = join_rows(radiation[station], obs_all, span_lo, span_hi)

        sub(f"{station} -- target hour {target_hour:02d}:00 UTC -- join over "
            f"{span_lo}..{span_hi} (session55's own available span, "
            f"reserved year already excluded)")
        print(f"    joined rows: {len(joined_rows)}  "
              f"(no radiation row: {no_feat}, no usable obs: {no_obs})")

        for fold_label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
            run_fold(station, fold_label, tr_s, tr_e, te_s, te_e,
                     joined_rows, obs_all, grid_rows)

    # ------------------------------------------------------------ write the grid

    with open(GRID_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "station", "fold", "variant", "n_train", "n_test", "raw_mae",
            "persist_mae", "mae", "delta_vs_B", "skill_vs_B_pct"])
        w.writeheader()
        w.writerows(grid_rows)
    print(f"\nWrote grid: {GRID_CSV} ({len(grid_rows)} rows)")

    # ------------------------------------------------------------ fold-averaged per airport

    line("Fold-averaged per airport (mean across the three EXPERIMENT_FOLDS)")
    summary_rows = []
    fold_labels = [f[0] for f in EXPERIMENT_FOLDS]
    for station in AIRPORTS:
        print(f"\n    {station}:")
        b_mean = None
        for variant_label, _ in VARIANTS:
            maes = [r["mae"] for r in grid_rows
                    if r["station"] == station and r["variant"] == variant_label]
            mean_mae = sum(maes) / len(maes) if maes else float("nan")
            if variant_label == "B":
                b_mean = mean_mae
            delta = mean_mae - b_mean
            skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
            print(f"        {variant_label:<5} mean_MAE={mean_mae:.3f}  "
                  f"delta_vs_B={delta:+.3f}  skill_vs_B={skill:+.1f}%  "
                  f"(n_folds={len(maes)})")
            summary_rows.append(dict(
                level="fold_averaged_per_airport", station=station, fold="",
                variant=variant_label, mean_mae=round(mean_mae, 4),
                delta_vs_B=round(delta, 4),
                skill_vs_B_pct=round(skill, 2) if skill == skill else "",
            ))

    # ------------------------------------------------------------ airport-averaged per fold

    line("Airport-averaged per fold (mean across the five airports)")
    for fold_label in fold_labels:
        print(f"\n    {fold_label}:")
        b_mean = None
        for variant_label, _ in VARIANTS:
            maes = [r["mae"] for r in grid_rows
                    if r["fold"] == fold_label and r["variant"] == variant_label]
            mean_mae = sum(maes) / len(maes) if maes else float("nan")
            if variant_label == "B":
                b_mean = mean_mae
            delta = mean_mae - b_mean
            skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
            print(f"        {variant_label:<5} mean_MAE={mean_mae:.3f}  "
                  f"delta_vs_B={delta:+.3f}  skill_vs_B={skill:+.1f}%  "
                  f"(n_airports={len(maes)})")
            summary_rows.append(dict(
                level="airport_averaged_per_fold", station="", fold=fold_label,
                variant=variant_label, mean_mae=round(mean_mae, 4),
                delta_vs_B=round(delta, 4),
                skill_vs_B_pct=round(skill, 2) if skill == skill else "",
            ))

    # ------------------------------------------------------------ grand overall

    line("Grand overall (mean across all five airports and all three folds)")
    b_mean = None
    grand_skill = {}
    for variant_label, _ in VARIANTS:
        maes = [r["mae"] for r in grid_rows if r["variant"] == variant_label]
        mean_mae = sum(maes) / len(maes)
        if variant_label == "B":
            b_mean = mean_mae
        delta = mean_mae - b_mean
        skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
        grand_skill[variant_label] = skill
        print(f"    {variant_label:<5} mean_MAE={mean_mae:.3f}  "
              f"delta_vs_B={delta:+.3f}  skill_vs_B={skill:+.1f}%  (n={len(maes)})")
        summary_rows.append(dict(
            level="grand_overall", station="", fold="", variant=variant_label,
            mean_mae=round(mean_mae, 4), delta_vs_B=round(delta, 4),
            skill_vs_B_pct=round(skill, 2) if skill == skill else "",
        ))

    with open(SUMMARY_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "level", "station", "fold", "variant", "mean_mae", "delta_vs_B",
            "skill_vs_B_pct"])
        w.writeheader()
        w.writerows(summary_rows)
    print(f"\nWrote summary: {SUMMARY_CSV} ({len(summary_rows)} rows)")

    # ------------------------------------------------------------ E1/E2/E3/E4 comparison

    line("E4's own max grand-overall skill against E1/E2/E3 (session prompt's "
         "own instruction -- state plainly, no verdict)")
    e4_max_label = max(("B+R", "B+Rv", "B+v"), key=lambda v: grand_skill[v])
    e4_max_skill = grand_skill[e4_max_label]
    print(f"    E1 max grand-overall skill (B+Lv, F99) : +2.0%")
    print(f"    E2 max grand-overall skill (B+Dv, F100): +4.1%")
    print(f"    E3 max grand-overall skill (B+T,  F101): +0.9%")
    print(f"    E4 max grand-overall skill ({e4_max_label:<4}, this session): "
          f"{e4_max_skill:+.1f}%")

    # ------------------------------------------------------------ internal consistency check

    line("Free internal-consistency check (as F99/F100/F101 did): does the "
         "2025-26 fold's B variant reproduce F94/F96/F99/F100/F101's own "
         "raw-GFS and persistence MAE and row counts at every airport?")
    f94_reference = {
        # station: (raw_mae, persist_mae, n)
        "EGLC": (1.254, 2.096, 364),
        "LFPG": (1.382, 2.300, 364),
        "DSM": (1.733, 4.003, 365),
        "YSDU": (1.317, 2.669, 356),
        "RNO": (1.512, 2.490, 365),
    }
    for station in AIRPORTS:
        row = next(r for r in grid_rows
                   if r["station"] == station and r["fold"] == "2025-26"
                   and r["variant"] == "B")
        ref_raw, ref_persist, ref_n = f94_reference[station]
        print(f"    {station}: this session raw={row['raw_mae']:.4f} "
              f"persist={row['persist_mae']:.4f} n={row['n_test']}   |   "
              f"F94/F96/F99/F100/F101 raw={ref_raw:.3f} persist={ref_persist:.3f} n={ref_n}")

    # ------------------------------------------------------------ DSM / framing notes

    line("Framing notes (session prompt's own reading guidance, printed "
         "with the real numbers behind them -- no verdict computed)")
    print("\n    DSM is the diagnostic (F96: most headroom, cloud/wind already")
    print("    marginal there). Its fold-averaged deltas vs. B, printed above under")
    print("    'Fold-averaged per airport', are the figures to read with that")
    print("    history in mind -- if radiation helps anywhere despite the marginal")
    print("    cloud/wind read, DSM is the airport most likely to show it.")
    print("\n    Per-fold spread: the fold-by-fold grid (session56_e4_experiment_grid.csv)")
    print("    and the 'Airport-averaged per fold' table above both carry the raw")
    print("    per-fold numbers, so any airport whose fold-averaged result is carried by")
    print("    a single fold (2025-26 or the thin 2022-23 fold in particular, per")
    print("    F96/D52/D53/D54) can be read directly rather than only from the")
    print("    fold-averaged summary -- a benefit that reverses in one fold is")
    print("    fold-quality, not family weakness.")

    line("Preamble cleanup -- confirmation")
    print("    scripts/session55_radiation_pull.py's Step-0 printed DECISION summary")
    print("    was a print-text-only fix: the final per-combo summary loop now")
    print("    iterates over the real top-level (cycle, lead) airport combos")
    print("    (the 4 entries in `combos`) instead of over `windows_seen` (which also")
    print("    contained the lead-2 helper file, e.g. f022, and so wrongly described")
    print("    f022 itself as needing de-accumulation against a nonexistent f020).")
    print("    No data-path logic changed: build_combos, process_combo, build_joined,")
    print("    the lead/window arithmetic functions, and the fetch counts are")
    print("    byte-for-byte unchanged. The session-55 pull was not re-run; this")
    print("    session reads session55's already-committed output files unchanged.")

    line("END")
    print("This session reports the four-variant grid only. NO pass/fail verdict")
    print("was computed anywhere in this script -- the E4 family call is the")
    print("owner's review decision in session 57. No row of the reserved")
    print("2024-08-01..2025-07-31 confirmation year was read, loaded, or scored at")
    print("any point.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
