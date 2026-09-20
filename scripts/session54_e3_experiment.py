"""Session 54: the staged E3 (pressure/synoptic) feature experiment. A
LEARNING experiment, not a pass/fail gate -- runs ONLY on the three
non-reserved EXPERIMENT_FOLDS (scripts/session48_reserved_year.py). The
reserved 2024-25 confirmation year (D51) is never read, at all, by this
script. This is the direct analogue of session 50 / F99 (E1, upper-air) and
session 52 / F100 (E2, moisture), for the E3 (pressure/synoptic) family.

Fits four variants per airport, per fold, all on the SAME LightGBM settings
(D21.4/D48.6, unchanged) and the SAME features across every airport (no
per-airport feature selection, RNO included):

  B     -- the frozen 5-feature baseline (temp, season_sin, season_cos,
            cloud_cover, wind_speed_10m), REFIT on these three folds. Not a
            reuse of F94/F96/F99/F100, which were fit on different windows.
            Not B+L or B+D either -- D52/D53's own "measurement baseline is
            unchanged" rule: B stays the frozen 5-feature set only.
  B+T   -- B plus the derived pressure_tendency_3h_hpa (one added feature --
            the derived form, led with, per the programme's derived-first
            rule).
  B+Tv  -- B+T plus the two raw pressure fields pressure_msl_hpa and
            pressure_surface_hpa (three added total).
  B+v   -- B plus the two raw pressure fields only, WITHOUT the derived
            tendency.

pressure_msl_lead_minus3_hpa (the tendency's raw ingredient) is never used
as a model feature in any variant -- kept in the dataset for transparency
only, per the session prompt.

Two sanity checks run before any model is fit (session prompt, both must
PASS):
  1. Tendency arithmetic, on EVERY row (not a spot check): pressure_
     tendency_3h_hpa == round(pressure_msl_hpa - pressure_msl_lead_minus3_hpa,
     N) across all rows of both session53 output files, at every airport.
  2. The reserved-year guard: every EXPERIMENT_FOLDS entry is run through
     assert_reserved_year_excluded() before anything is loaded or fit, plus
     a defensive per-row scan of the loaded data.

Reports raw GFS and persistence alongside the four variants, for context
only (matching the project's own convention, F94/F96/F99/F100) -- the
deliverable is the four-variant grid and its deltas vs. B, not a
raw/persistence verdict.

Also reports, for B+T and B+v, per-airport LightGBM feature importances
(gain-based, percent of the variant's own total gain, averaged across the
three folds) -- session prompt item 3's own instruction.

No pass/fail verdict is computed anywhere in this script (session prompt:
"the family call is made by the owner in review afterwards").
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

PRESSURE_PATHS = [
    PROCESSED / "session53_v16_window_with_pressure.csv",
    PROCESSED / "session53_sealed_window_with_pressure.csv",
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
KEYS_BT = KEYS_B + ["pressure_tendency_3h_hpa"]
KEYS_BTV = KEYS_BT + ["pressure_msl_hpa", "pressure_surface_hpa"]
KEYS_BV = KEYS_B + ["pressure_msl_hpa", "pressure_surface_hpa"]

VARIANTS = [
    ("B", KEYS_B),
    ("B+T", KEYS_BT),
    ("B+Tv", KEYS_BTV),
    ("B+v", KEYS_BV),
]

IMPORTANCE_VARIANTS = ("B+T", "B+v")

OUT = ROOT / "notes" / "session-54-e3-experiment-output.txt"
GRID_CSV = PROCESSED / "session54_e3_experiment_grid.csv"
SUMMARY_CSV = PROCESSED / "session54_e3_experiment_summary.csv"


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
        "pressure_tendency_3h_hpa": r["tendency"],
        "pressure_msl_hpa": r["msl"],
        "pressure_surface_hpa": r["surface"],
    }
    return [lookup[k] for k in keys]


def features_matrix(rows, keys):
    return np.array([make_feature_vector(r, keys) for r in rows], dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


# ------------------------------------------------------------------ sanity checks

def sanity_check_tendency_arithmetic():
    """Session prompt item 1: verify pressure_tendency_3h_hpa ==
    round(pressure_msl_hpa - pressure_msl_lead_minus3_hpa, N) on EVERY row of
    both session53 output files, at every airport -- not a spot check,
    mirroring session53's own already-passed check. STOP if any row
    mismatches."""
    n_checked = {st: 0 for st in AIRPORTS}
    max_abs_diff = {st: 0.0 for st in AIRPORTS}
    failures = []
    for path in PRESSURE_PATHS:
        with open(path) as f:
            for row in csv.DictReader(f):
                st = row["station"]
                if st not in AIRPORTS:
                    continue
                msl = float(row["pressure_msl_hpa"])
                msl_m3 = float(row["pressure_msl_lead_minus3_hpa"])
                tendency = float(row["pressure_tendency_3h_hpa"])
                expected = round(msl - msl_m3, 3)
                diff = abs(expected - tendency)
                n_checked[st] += 1
                max_abs_diff[st] = max(max_abs_diff[st], diff)
                if diff > 1e-6:
                    failures.append((st, row["target_date"], msl, msl_m3, expected, tendency, diff))
    print(f"    {'station':<8} {'n_checked':>10} {'max_abs_diff':>14}")
    for st in AIRPORTS:
        print(f"    {st:<8} {n_checked[st]:>10} {max_abs_diff[st]:>14.9f}")
    if failures:
        print(f"\n    {len(failures)} row(s) FAILED the tendency-arithmetic check:")
        for f_ in failures[:20]:
            print(f"      {f_}")
        raise AssertionError(
            "SESSION 54 STOP SIGNAL: pressure_tendency_3h_hpa's derivation "
            "does not hold exactly at one or more rows -- see failures "
            "printed above. Stopping before fitting any model, per the "
            "session prompt.")
    print(f"\n    PASS -- pressure_tendency_3h_hpa == round(pressure_msl_hpa - "
          f"pressure_msl_lead_minus3_hpa, 3) exactly (within 1e-6 float "
          f"tolerance) at all {sum(n_checked.values())} rows checked, "
          f"across all five airports.")


def sanity_check_guard():
    """Session prompt item 2: every EXPERIMENT_FOLDS entry must pass
    assert_reserved_year_excluded() before anything is loaded or fit."""
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e}  test={te_s}..{te_e}  "
              f"-- PASS (guard did not raise)")
    print(f"\n    PASS -- all {len(EXPERIMENT_FOLDS)} EXPERIMENT_FOLDS entries "
          f"cleared assert_reserved_year_excluded() before any data was loaded.")


# ------------------------------------------------------------------ loading

def load_pressure_features():
    """station -> {date: {fc, cloud, wind, tendency, msl, surface}}. Reads
    session53's own output files, which already exclude every date in the
    reserved 2024-08-01..2025-07-31 year (D51) -- verified here with a
    defensive per-row scan, not assumed."""
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    for path in PRESSURE_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue  # defensive only -- session53's own output should have none
                out[st][d] = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                    "tendency": float(r["pressure_tendency_3h_hpa"]),
                    "msl": float(r["pressure_msl_hpa"]),
                    "surface": float(r["pressure_surface_hpa"]),
                }
    if reserved_hits:
        raise AssertionError(
            f"SESSION 54 STOP SIGNAL: {reserved_hits} row(s) inside the "
            "reserved 2024-25 confirmation year were found in session53's "
            "own output files -- refusing to proceed (D51).")
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
    """One row per day with a pressure feature row AND a usable observation,
    D14 drop-count rule (SPEC 2.2: nothing filled)."""
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
            "tendency": g["tendency"], "msl": g["msl"], "surface": g["surface"],
            "obs": o, "resid": o - g["fc"],
        })
    return rows, no_feat, no_obs


# ------------------------------------------------------------------ per fold/airport run

def run_fold(station, fold_label, train_start, train_end, test_start, test_end,
             joined_rows, obs_all, grid_rows, importance_records):
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

        if variant_label in IMPORTANCE_VARIANTS:
            gains = m.booster_.feature_importance(importance_type="gain")
            total = float(np.sum(gains))
            pct = {k: (100.0 * g / total if total else 0.0) for k, g in zip(keys, gains)}
            importance_records.setdefault(station, {}).setdefault(
                variant_label, {}).setdefault(fold_label, pct)

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

    line("SESSION 54 -- E3 (pressure/synoptic) staged feature experiment. A "
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
    print(f"B+T   features: {KEYS_BT}")
    print(f"B+Tv  features: {KEYS_BTV}")
    print(f"B+v   features: {KEYS_BV}")
    print("NOTE: B is the frozen 5-feature set only -- E1's lapse_rate_t2_t850")
    print("(D52) and E2's dewpoint_depression_t2m_floored (D53) are NOT added to")
    print("B here; they enter only at the combine phase.")
    print("NOTE: pressure_msl_lead_minus3_hpa (the tendency's raw ingredient) is")
    print("never used as a model feature in any variant.")

    line("Sanity check 1 -- tendency arithmetic, checked on EVERY row of "
         "both session53 output files (not a spot check)")
    sanity_check_tendency_arithmetic()

    line("Sanity check 2 -- the reserved-year guard, run on every "
         "EXPERIMENT_FOLDS entry before anything is loaded or fit")
    sanity_check_guard()

    line("Loading pressure features and observations (both sanity checks passed)")
    pressure = load_pressure_features()
    print("    pressure feature files loaded, reserved-year rows: 0 found "
          "(defensive scan, per load_pressure_features()).")

    grid_rows = []
    importance_records = {}

    line("Per-airport, per-fold, per-variant results")
    for station, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(station, target_hour)
        span_lo = min(pressure[station])
        span_hi = max(pressure[station])
        joined_rows, no_feat, no_obs = join_rows(pressure[station], obs_all, span_lo, span_hi)

        sub(f"{station} -- target hour {target_hour:02d}:00 UTC -- join over "
            f"{span_lo}..{span_hi} (session53's own available span, "
            f"reserved year already excluded)")
        print(f"    joined rows: {len(joined_rows)}  "
              f"(no pressure row: {no_feat}, no usable obs: {no_obs})")

        for fold_label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
            run_fold(station, fold_label, tr_s, tr_e, te_s, te_e,
                     joined_rows, obs_all, grid_rows, importance_records)

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
    for variant_label, _ in VARIANTS:
        maes = [r["mae"] for r in grid_rows if r["variant"] == variant_label]
        mean_mae = sum(maes) / len(maes)
        if variant_label == "B":
            b_mean = mean_mae
        delta = mean_mae - b_mean
        skill = 100 * (1 - mean_mae / b_mean) if b_mean else float("nan")
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

    # ------------------------------------------------------------ feature importances

    line("Per-airport LightGBM feature importances for B+T and B+v "
         "(gain-based, percent of the variant's own total gain, averaged "
         "across the three EXPERIMENT_FOLDS). Session prompt item 3's own "
         "instruction.")
    for variant_label in IMPORTANCE_VARIANTS:
        print(f"\n    -- {variant_label} --")
        _, keys = next(v for v in VARIANTS if v[0] == variant_label)
        for station in AIRPORTS:
            per_fold = importance_records.get(station, {}).get(variant_label, {})
            print(f"      {station}:")
            for k in keys:
                vals = [per_fold[fl][k] for fl in fold_labels if fl in per_fold]
                mean_pct = sum(vals) / len(vals) if vals else float("nan")
                per_fold_str = ", ".join(f"{v:.1f}" for v in vals)
                print(f"          {k:<32} {mean_pct:6.1f}%  "
                      f"(per fold: [{per_fold_str}])")

    # ------------------------------------------------------------ internal consistency check

    line("Free internal-consistency check (as F99/F100 did): does the "
         "2025-26 fold's B variant reproduce F94/F96/F99/F100's own raw-GFS "
         "and persistence MAE and row counts at every airport?")
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
              f"F94/F96/F99/F100 raw={ref_raw:.3f} persist={ref_persist:.3f} n={ref_n}")

    # ------------------------------------------------------------ DSM / RNO framing

    line("Framing notes (session prompt's own reading guidance, printed "
         "with the real numbers behind them -- no verdict computed)")
    print("\n    DSM is the diagnostic (F96: most headroom). Its fold-averaged deltas")
    print("    vs. B, printed above under 'Fold-averaged per airport', are the figures")
    print("    to read with that history in mind.")
    print("\n    RNO: PRMSL is sea-level-normalised by definition, so it may be the one")
    print("    family that does NOT show an RNO anomaly, unlike the below-ground upper-")
    print("    air extrapolation (F98/F99). RNO ran with the identical feature set as")
    print("    every other airport throughout -- no exclusion, no RNO-specific feature.")
    print("    Its fold-averaged deltas are printed above under 'Fold-averaged per")
    print("    airport'.")
    print("\n    Per-fold spread: the fold-by-fold grid (session54_e3_experiment_grid.csv)")
    print("    and the 'Airport-averaged per fold' table above both carry the raw")
    print("    per-fold numbers, so any airport whose fold-averaged result is carried by")
    print("    a single fold (2025-26 or the thin 2022-23 fold in particular, per")
    print("    F96/D52/D53) can be read directly rather than only from the fold-averaged")
    print("    summary -- a benefit that reverses in one fold is fold-quality, not")
    print("    family weakness.")

    line("END")
    print("This session reports the four-variant grid only. NO pass/fail verdict")
    print("was computed anywhere in this script -- the family call is made by the")
    print("owner in review (session prompt). No row of the reserved")
    print("2024-08-01..2025-07-31 confirmation year was read, loaded, or scored at")
    print("any point.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
