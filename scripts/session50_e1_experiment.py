"""Session 50: the staged E1 (upper-air/vertical-structure) feature
experiment. A LEARNING experiment, not a pass/fail gate -- runs ONLY on the
three non-reserved EXPERIMENT_FOLDS (scripts/session48_reserved_year.py).
The reserved 2024-25 confirmation year (D51) is never read, at all, by this
script.

Fits four variants per airport, per fold, all on the SAME LightGBM settings
(D21.4/D48.6, unchanged) and the SAME features across every airport (no
per-airport feature selection):

  B     -- the frozen 5-feature baseline (temp, season_sin, season_cos,
            cloud_cover, wind_speed_10m), REFIT on these three folds. Not a
            reuse of F94/F96 -- those were fit on different windows.
  B+L   -- B plus the derived lapse_rate_t2_t850 (one added feature).
  B+Lv  -- B+L plus the raw levels t850, t925, t700 (four added total).
  B+v   -- B plus the raw levels only, WITHOUT the derived lapse rate.

Two sanity checks run before any model is fit (session prompt "First"):
  1. t2m_raw's derivation: t2m_raw == temperature_grib_c - elevation_constant
     (D48.3/F90), checked on EVERY row of both session49 output files, not a
     spot check. STOP if it does not hold exactly (to rounding) anywhere.
  2. The reserved-year guard: every EXPERIMENT_FOLDS entry is run through
     assert_reserved_year_excluded() before anything is loaded or fit.

Reports raw GFS and persistence alongside the four variants, for context
only (matching the project's own convention, F94/F96) -- the deliverable is
the four-variant grid and its deltas vs. B, not a raw/persistence verdict.

No pass/fail verdict is computed anywhere in this script (session prompt:
"the family call is made in review").
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

UPPER_AIR_PATHS = [
    PROCESSED / "session49_v16_window_with_upper_air.csv",
    PROCESSED / "session49_sealed_window_with_upper_air.csv",
]

ELEV_CORR_CSV = (
    ROOT / "data" / "raw" / "diagnostics" / "session37"
    / "session37_elevation_correction_params.csv"
)

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
KEYS_BL = KEYS_B + ["lapse_rate_t2_t850"]
KEYS_BLV = KEYS_BL + ["t850", "t925", "t700"]
KEYS_BV = KEYS_B + ["t850", "t925", "t700"]

VARIANTS = [
    ("B", KEYS_B),
    ("B+L", KEYS_BL),
    ("B+Lv", KEYS_BLV),
    ("B+v", KEYS_BV),
]

OUT = ROOT / "notes" / "session-50-e1-experiment-output.txt"
GRID_CSV = PROCESSED / "session50_e1_experiment_grid.csv"
SUMMARY_CSV = PROCESSED / "session50_e1_experiment_summary.csv"


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
        "lapse_rate_t2_t850": r["lapse"],
        "t850": r["t850"],
        "t925": r["t925"],
        "t700": r["t700"],
    }
    return [lookup[k] for k in keys]


def features_matrix(rows, keys):
    return np.array([make_feature_vector(r, keys) for r in rows], dtype=float)


def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float("nan")


# ------------------------------------------------------------------ loading

def load_elevation_corrections():
    out = {}
    with open(ELEV_CORR_CSV) as f:
        for row in csv.DictReader(f):
            out[row["station"]] = float(row["correction_c"])
    return out


def sanity_check_t2m_raw(elev_corr):
    """Session prompt, sanity check 1: t2m_raw == temperature_grib_c -
    elevation_constant, at EVERY row of both session49 output files, not a
    spot check. STOP (raise) if it does not hold exactly (to rounding) at
    any airport."""
    n_checked = {st: 0 for st in AIRPORTS}
    max_abs_diff = {st: 0.0 for st in AIRPORTS}
    failures = []
    for path in UPPER_AIR_PATHS:
        with open(path) as f:
            for row in csv.DictReader(f):
                st = row["station"]
                if st not in AIRPORTS:
                    continue
                temp_c = float(row["temperature_grib_c"])
                correction = elev_corr[st]
                expected = round(temp_c - correction, 3)
                actual = float(row["t2m_raw"])
                diff = abs(expected - actual)
                n_checked[st] += 1
                max_abs_diff[st] = max(max_abs_diff[st], diff)
                if diff > 1e-6:
                    failures.append((st, row["target_date"], temp_c, correction, expected, actual, diff))
    print(f"    {'station':<8} {'correction_c':>13} {'sign':>6} {'n_checked':>10} "
          f"{'max_abs_diff':>14}")
    for st in AIRPORTS:
        c = elev_corr[st]
        print(f"    {st:<8} {c:>13.4f} {'+' if c >= 0 else '-':>6} "
              f"{n_checked[st]:>10} {max_abs_diff[st]:>14.9f}")
    if failures:
        print(f"\n    {len(failures)} row(s) FAILED the derivation check:")
        for f_ in failures[:20]:
            print(f"      {f_}")
        raise AssertionError(
            "SESSION 50 STOP SIGNAL: t2m_raw's derivation does not hold "
            "exactly at one or more rows -- see failures printed above. "
            "The lapse-rate feature is built on t2m_raw, so a sign or "
            "offset error here invalidates the whole experiment. Stopping "
            "before fitting any model, per the session prompt.")
    print(f"\n    PASS -- t2m_raw == round(temperature_grib_c - correction_c, 3) "
          f"exactly (within 1e-6 float tolerance) at all "
          f"{sum(n_checked.values())} rows checked, across all five airports.")


def sanity_check_guard():
    """Session prompt, sanity check 2: every EXPERIMENT_FOLDS entry must
    pass assert_reserved_year_excluded() before anything is loaded or fit."""
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e}  test={te_s}..{te_e}  "
              f"-- PASS (guard did not raise)")
    print(f"\n    PASS -- all {len(EXPERIMENT_FOLDS)} EXPERIMENT_FOLDS entries "
          f"cleared assert_reserved_year_excluded() before any data was loaded.")


def load_upper_air_features():
    """station -> {date: {fc, cloud, wind, lapse, t850, t925, t700}}.
    Reads session49's own output files, which already exclude every date in
    the reserved 2024-08-01..2025-07-31 year (D51) -- verified here with a
    defensive per-row scan, not assumed."""
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    for path in UPPER_AIR_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue  # defensive only -- session49's own output should have none
                out[st][d] = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                    "lapse": float(r["lapse_rate_t2_t850"]),
                    "t850": float(r["t850"]),
                    "t925": float(r["t925"]),
                    "t700": float(r["t700"]),
                }
    if reserved_hits:
        raise AssertionError(
            f"SESSION 50 STOP SIGNAL: {reserved_hits} row(s) inside the "
            "reserved 2024-25 confirmation year were found in session49's "
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
    """One row per day with an upper-air feature row AND a usable
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
            "lapse": g["lapse"], "t850": g["t850"], "t925": g["t925"],
            "t700": g["t700"],
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

    line("SESSION 50 -- E1 (upper-air/vertical-structure) staged feature "
         "experiment. A LEARNING READING, NOT A PASS/FAIL GATE. Runs ONLY "
         "on the three non-reserved EXPERIMENT_FOLDS. The reserved 2024-25 "
         "confirmation year (D51) is never read this session.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"reserved confirmation year (never touched): {RESERVED_YEAR_START} .. {RESERVED_YEAR_END}")
    print(f"model settings (D48.6/D21.4, identical for every variant/fold/airport): {LGB_PARAMS}")
    print(f"B     features: {KEYS_B}")
    print(f"B+L   features: {KEYS_BL}")
    print(f"B+Lv  features: {KEYS_BLV}")
    print(f"B+v   features: {KEYS_BV}")

    line("Sanity check 1 -- t2m_raw's derivation "
         "(t2m_raw == temperature_grib_c - elevation_constant, D48.3/F90), "
         "checked on EVERY row of both session49 output files")
    elev_corr = load_elevation_corrections()
    sanity_check_t2m_raw(elev_corr)

    line("Sanity check 2 -- the reserved-year guard, run on every "
         "EXPERIMENT_FOLDS entry before anything is loaded or fit")
    sanity_check_guard()

    line("Loading upper-air features and observations (both sanity checks passed)")
    upper_air = load_upper_air_features()
    print("    upper-air feature files loaded, reserved-year rows: 0 found "
          "(defensive scan, per load_upper_air_features()).")

    grid_rows = []

    line("Per-airport, per-fold, per-variant results")
    for station, target_hour in AIRPORTS.items():
        obs_all, obs_far, obs_no_temp = load_obs_all(station, target_hour)
        span_lo = min(upper_air[station])
        span_hi = max(upper_air[station])
        joined_rows, no_feat, no_obs = join_rows(upper_air[station], obs_all, span_lo, span_hi)

        sub(f"{station} -- target hour {target_hour:02d}:00 UTC -- join over "
            f"{span_lo}..{span_hi} (session49's own available span, "
            f"reserved year already excluded)")
        print(f"    joined rows: {len(joined_rows)}  "
              f"(no upper-air row: {no_feat}, no usable obs: {no_obs})")

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

    # ------------------------------------------------------------ DSM / RNO framing

    line("Framing notes (session prompt's own reading guidance, printed "
         "with the real numbers behind them -- no verdict computed)")
    print("\n    DSM is the diagnostic (F96: cloud/wind were marginal-to-slightly-")
    print("    negative there). Its fold-averaged deltas vs. B, printed above under")
    print("    'Fold-averaged per airport', are the figures to read with that in mind.")
    print("\n    RNO is expected to behave oddly (F98: t925 there is a below-ground")
    print("    extrapolation, and lapse_rate_t2_t850 is partly degenerate). It ran")
    print("    with the SAME features as every other airport -- no exclusion, no")
    print("    RNO-specific feature. Its fold-averaged deltas are printed above under")
    print("    'Fold-averaged per airport'; a small, null, or negative upper-air")
    print("    effect there is EXPECTED, not a failure of the family.")

    line("END")
    print("This session reports the four-variant grid only. NO pass/fail verdict")
    print("was computed anywhere in this script -- the family call is made in")
    print("review (session prompt). No row of the reserved 2024-08-01..2025-07-31")
    print("confirmation year was read, loaded, or scored at any point.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
