"""Session 73, Steps 2-4: clean-room fit and score of F109 at RNO (D64).

Written from the docs alone (CLAUDE.md, SPEC.md, STATUS.md, DECISIONS.md,
DECISIONS-archive.md) and the session 72 rebuild tables. It imports no other
project script and reads nothing under scripts/, data/processed/ or notes/.

Three fits (session 73 prompt, "Pre-declared runs"):
  B            the 5 columns of SPEC 8.2 / D48.4
  BDLRT_P      B + L, D, T, R, Variant P (session 72 tables as built)
  BDLRT_G4alt  B + L, D, T, R, Variant G4-alt (L and D re-derived from
               t2m_raw_from_full)

Usage (offline):
  python scripts/session73_fit_score.py --run 1      Step 2: fit, score, write
  python scripts/session73_fit_score.py --run 2      Step 3: second fit, own process
  python scripts/session73_fit_score.py --compare-runs   Step 3: exact comparison
  python scripts/session73_fit_score.py --seal       Step 4: MAE table + SHA-256

Every output path is new. The script refuses to overwrite any existing file
(SPEC 8.7 item 5). Non-finite numbers are rejected at load, dropped and
counted (SPEC 8.7 item 2).
"""

import os
import sys

# --- OpenMP loader shim (DECISIONS-archive Q16/D24) -------------------------
# LightGBM's macOS build needs libomp.dylib. This machine has no Homebrew, so,
# as D24 describes, point the dynamic loader at the copy scikit-learn's wheel
# ships and restart the interpreter once. It changes nothing about the model.
if sys.platform == "darwin" and os.environ.get("S73_OMP_SHIM") != "1":
    _site = os.path.join(sys.prefix, "lib",
                         "python%d.%d" % sys.version_info[:2], "site-packages")
    _omp_dir = os.path.join(_site, "sklearn", ".dylibs")
    if os.path.exists(os.path.join(_omp_dir, "libomp.dylib")):
        _env = dict(os.environ)
        _env["S73_OMP_SHIM"] = "1"
        _env["DYLD_LIBRARY_PATH"] = _omp_dir + (
            ":" + _env["DYLD_LIBRARY_PATH"] if _env.get("DYLD_LIBRARY_PATH") else "")
        os.execve(sys.executable, [sys.executable] + sys.argv, _env)

import csv
import hashlib
import json
import math
import platform
from datetime import date

import numpy as np
import lightgbm
from lightgbm import LGBMRegressor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IN_DIR = os.path.join(ROOT, "data", "rebuild", "session72")
OUT_DIR = os.path.join(ROOT, "data", "rebuild", "session73")
RUN2_DIR = os.path.join(OUT_DIR, "run2")

TRAIN_START, TRAIN_END = "2021-03-24", "2024-07-31"
TEST_START, TEST_END = "2024-08-01", "2025-07-31"

# D21.4 / D48.6, exactly as written. Parameter names are LightGBM's
# scikit-learn API names, so the scikit-learn API is used (gap G14).
PARAMS = dict(
    objective="regression_l1", n_estimators=300, learning_rate=0.05,
    num_leaves=15, min_child_samples=40, subsample=1.0,
    colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0,
    random_state=42, n_jobs=1, deterministic=True, force_row_wise=True,
    verbose=-1,
)

# B's five columns in D48.4's order (gap G15). Variant P uses the stored
# 3-decimal GRIB columns (G4's choice, carried to cloud and wind: gap G16).
B_COLS = ["temperature_grib_c", "season_sin", "season_cos",
          "cloud_cover_grib_pct", "wind_speed_grib_kmh"]
# Added features in SPEC 8.1 / D58 item 3's table order L, D, T, R (G15).
# The model sees D floored; the complete-case mask uses D unfloored (D58.5).
ADD_MODEL = {"L": "lapse_rate_t2_t850", "D": "dewpoint_depression_t2m_floored",
             "T": "pressure_tendency_3h_hpa", "R": "dswrf_2h_wm2"}
ADD_MASK = {"L": "lapse_rate_t2_t850", "D": "dewpoint_depression_t2m",
            "T": "pressure_tendency_3h_hpa", "R": "dswrf_2h_wm2"}
ADD_ORDER = ["L", "D", "T", "R"]

MODELS = ["B", "BDLRT_P", "BDLRT_G4alt"]

FILES_OPENED = []


def log_open(path, mode):
    FILES_OPENED.append((os.path.relpath(path, ROOT), mode))


def refuse_existing(path):
    if os.path.exists(path):
        raise SystemExit("refusing to overwrite existing file: %s"
                         % os.path.relpath(path, ROOT))


def read_csv(name):
    path = os.path.join(IN_DIR, name)
    log_open(path, "read")
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh))


def parse_num(s, counts, col):
    """Blank -> None. Non-finite -> None, counted (SPEC 8.7 item 2)."""
    if s is None or s == "":
        return None
    x = float(s)
    if not math.isfinite(x):
        counts[col] = counts.get(col, 0) + 1
        return None
    return x


NUMERIC_F = B_COLS + ["season_sin", "season_cos", "t2m_raw",
                      "t2m_raw_from_full", "t850", "dew_point_2m",
                      "lapse_rate_t2_t850", "dewpoint_depression_t2m",
                      "dewpoint_depression_t2m_floored",
                      "pressure_tendency_3h_hpa", "dswrf_2h_wm2",
                      "raw_gfs_rung_c"]
NUMERIC_O = ["obs_c", "forecast_c", "residual_c"]
NUMERIC_P = ["persistence_c"]


def load_tables():
    feats = read_csv("rno_features.csv")
    obs = read_csv("rno_observations.csv")
    pers = read_csv("rno_persistence.csv")
    nonfinite = {}
    rows = []
    for f, o, p in zip(feats, obs, pers):
        d = f["target_date"]
        if not (d == o["target_date"] == p["target_date"]):
            raise SystemExit("date misalignment at %s" % d)
        r = {"target_date": d, "window": f["window"],
             "pair_status": o["pair_status"], "pers_status": p["status"],
             "missing_inputs": f["missing_inputs"]}
        for c in dict.fromkeys(NUMERIC_F):
            r[c] = parse_num(f[c], nonfinite, "features." + c)
        for c in NUMERIC_O:
            r[c] = parse_num(o[c], nonfinite, "observations." + c)
        for c in NUMERIC_P:
            r[c] = parse_num(p[c], nonfinite, "persistence." + c)
        rows.append(r)
    counts = {
        "features": len(feats), "observations": len(obs),
        "persistence": len(pers),
        "train": sum(r["window"] == "train" for r in rows),
        "test": sum(r["window"] == "test" for r in rows),
    }
    if not (len(feats) == len(obs) == len(pers) == 1591
            and counts["train"] == 1226 and counts["test"] == 365):
        raise SystemExit("row counts differ from 1,591 / 1,226 / 365: %s"
                         % counts)
    for r in rows:
        win = ("train" if TRAIN_START <= r["target_date"] <= TRAIN_END else
               "test" if TEST_START <= r["target_date"] <= TEST_END else None)
        if win != r["window"]:
            raise SystemExit("window label disagrees with dates at %s"
                             % r["target_date"])
    return rows, counts, nonfinite


def add_g4alt(rows):
    """Variant G4-alt: L and D re-derived from t2m_raw_from_full (G7 stored
    rounded t850 and dew_point_2m), D floored at model time as in P."""
    for r in rows:
        tf, t850, dp = r["t2m_raw_from_full"], r["t850"], r["dew_point_2m"]
        r["L_g4"] = None if tf is None or t850 is None else round(tf - t850, 3)
        r["D_g4"] = None if tf is None or dp is None else round(tf - dp, 3)
        r["Dfl_g4"] = None if r["D_g4"] is None else max(r["D_g4"], 0.0)


def model_columns(model):
    """(model input columns, complete-case mask columns) per model."""
    if model == "B":
        feats = list(B_COLS)
        mask = list(B_COLS) + [ADD_MASK[k] for k in ADD_ORDER]
    elif model == "BDLRT_P":
        feats = list(B_COLS) + [ADD_MODEL[k] for k in ADD_ORDER]
        mask = list(B_COLS) + [ADD_MASK[k] for k in ADD_ORDER]
    elif model == "BDLRT_G4alt":
        sub = {"L": "L_g4", "D": "Dfl_g4"}
        subm = {"L": "L_g4", "D": "D_g4"}
        feats = list(B_COLS) + [sub.get(k, ADD_MODEL[k]) for k in ADD_ORDER]
        mask = list(B_COLS) + [subm.get(k, ADD_MASK[k]) for k in ADD_ORDER]
    else:
        raise ValueError(model)
    return feats, mask


def complete_case(rows, window, mask_cols):
    """SPEC 8.3 / D58 item 5: keep a row only if every mask column and the
    target (residual_c) has a value. Returns kept rows and dropped reasons."""
    kept, dropped = [], []
    for r in rows:
        if r["window"] != window:
            continue
        miss = [c for c in mask_cols if r[c] is None]
        reasons = []
        if miss:
            reasons.append("feature missing: " + ",".join(miss)
                           + (" (" + r["missing_inputs"].split(";")[0]
                              + "; ...)" if r["missing_inputs"] else ""))
        if r["residual_c"] is None:
            reasons.append("no target: " + r["pair_status"])
        if reasons:
            dropped.append({"target_date": r["target_date"],
                            "window": window, "reason": " | ".join(reasons)})
        else:
            kept.append(r)
    return kept, dropped


def fit_predict(train, test, feats):
    X = np.array([[r[c] for c in feats] for r in train], dtype=np.float64)
    y = np.array([r["residual_c"] for r in train], dtype=np.float64)
    Xt = np.array([[r[c] for c in feats] for r in test], dtype=np.float64)
    m = LGBMRegressor(**PARAMS)
    m.fit(X, y)
    return m, m.predict(Xt)


def fmt(x):
    return "" if x is None else repr(float(x))


def write_csv(path, header, rows):
    refuse_existing(path)
    log_open(path, "write")
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def booster_params_block(m):
    text = m.booster_.model_to_string()
    start = text.find("parameters:")
    end = text.find("end of parameters")
    return text[start:end].strip().splitlines() if start >= 0 else []


def run_fit(run_id):
    out = OUT_DIR if run_id == 1 else RUN2_DIR
    rows, counts, nonfinite = load_tables()
    add_g4alt(rows)
    print("session 73 fit/score, run %d, python %s, numpy %s, lightgbm %s"
          % (run_id, platform.python_version(), np.__version__,
             lightgbm.__version__))
    print("loaded rows:", counts)
    print("non-finite values dropped at load:",
          sum(nonfinite.values()), nonfinite)

    # Consistency checks on the stored P columns (report only).
    chk = {"L_stored_eq_round(t2m_raw-t850,3)": 0,
           "D_stored_eq_round(t2m_raw-dew_point_2m,3)": 0,
           "Dfloored_stored_eq_max(D,0)": 0, "rows_checked": 0,
           "D_floor_changes_P": 0, "D_floor_changes_G4alt": 0,
           "L_P_ne_G4alt": 0, "D_P_ne_G4alt": 0,
           "t2m_raw_ne_t2m_raw_from_full": 0}
    for r in rows:
        if r["t2m_raw"] is None:
            continue
        chk["rows_checked"] += 1
        chk["L_stored_eq_round(t2m_raw-t850,3)"] += (
            r["lapse_rate_t2_t850"] == round(r["t2m_raw"] - r["t850"], 3))
        chk["D_stored_eq_round(t2m_raw-dew_point_2m,3)"] += (
            r["dewpoint_depression_t2m"]
            == round(r["t2m_raw"] - r["dew_point_2m"], 3))
        chk["Dfloored_stored_eq_max(D,0)"] += (
            r["dewpoint_depression_t2m_floored"]
            == max(r["dewpoint_depression_t2m"], 0.0))
        chk["D_floor_changes_P"] += (r["dewpoint_depression_t2m"] < 0)
        chk["D_floor_changes_G4alt"] += (r["D_g4"] < 0)
        chk["L_P_ne_G4alt"] += (r["lapse_rate_t2_t850"] != r["L_g4"])
        chk["D_P_ne_G4alt"] += (r["dewpoint_depression_t2m"] != r["D_g4"])
        chk["t2m_raw_ne_t2m_raw_from_full"] += (
            r["t2m_raw"] != r["t2m_raw_from_full"])
    print("stored-column checks:", chk)

    results, meta_models, dropped_all = {}, {}, []
    for model in MODELS:
        feats, mask = model_columns(model)
        train, dtr = complete_case(rows, "train", mask)
        test, dte = complete_case(rows, "test", mask)
        # B-only mask, for the D58 item 5 "0 dropped against B-only" check.
        btr, _ = complete_case(rows, "train", B_COLS)
        bte, _ = complete_case(rows, "test", B_COLS)
        m, pred = fit_predict(train, test, feats)
        results[model] = (test, pred)
        meta_models[model] = {
            "feature_order": feats, "complete_case_mask": mask + ["residual_c"],
            "n_train": len(train), "n_test": len(test),
            "n_train_B_only_mask": len(btr), "n_test_B_only_mask": len(bte),
            "dropped_train": dtr, "dropped_test": dte,
            "booster_parameters": booster_params_block(m),
            "sklearn_get_params": {k: (v if isinstance(v, (int, float, str,
                                   bool, type(None))) else str(v))
                                   for k, v in m.get_params().items()},
            "num_trees": m.booster_.num_trees(),
        }
        for d in dtr + dte:
            dropped_all.append(dict(d, model=model))
        print("%-12s n_train=%d n_test=%d (B-only mask: %d/%d) trees=%d"
              % (model, len(train), len(test), len(btr), len(bte),
                 m.booster_.num_trees()))

    os.makedirs(out, exist_ok=True)

    # Per-day model predictions, full precision (repr).
    pred_rows = []
    for model in MODELS:
        test, pred = results[model]
        for r, p in zip(test, pred):
            p = float(p)
            corrected = r["forecast_c"] + p
            pred_rows.append([model, r["target_date"], fmt(r["obs_c"]),
                              fmt(r["forecast_c"]), fmt(r["residual_c"]),
                              fmt(p), fmt(corrected),
                              fmt(abs(r["obs_c"] - corrected))])
    write_csv(os.path.join(out, "rno_test_predictions.csv"),
              ["model", "target_date", "obs_c", "forecast_c",
               "residual_obs_minus_forecast_c", "predicted_residual_c",
               "corrected_forecast_c", "abs_error_c"], pred_rows)

    abs_err = {m: [] for m in MODELS}
    for row in pred_rows:
        abs_err[row[0]].append(abs(float(row[2]) - float(row[6])))

    mae_rows = []
    if run_id == 1:
        # Rungs: raw GFS on every test day with an observation; persistence
        # on test days with a previous-day observation (SPEC 8.5, D58.6).
        base_rows, raw_err, per_err = [], [], []
        for r in rows:
            if r["window"] != "test":
                continue
            re_ = (None if r["obs_c"] is None or r["raw_gfs_rung_c"] is None
                   else abs(r["obs_c"] - r["raw_gfs_rung_c"]))
            pe_ = (None if r["obs_c"] is None or r["persistence_c"] is None
                   else abs(r["obs_c"] - r["persistence_c"]))
            if re_ is not None:
                raw_err.append(re_)
            if pe_ is not None:
                per_err.append(pe_)
            base_rows.append([r["target_date"], fmt(r["obs_c"]),
                              fmt(r["raw_gfs_rung_c"]), fmt(re_),
                              fmt(r["persistence_c"]), r["pers_status"],
                              fmt(pe_)])
        write_csv(os.path.join(out, "rno_test_rungs.csv"),
                  ["target_date", "obs_c", "raw_gfs_c", "raw_gfs_abs_error_c",
                   "persistence_c", "persistence_status",
                   "persistence_abs_error_c"], base_rows)
        table = [("raw_gfs", raw_err), ("persistence", per_err)] + [
            (m, abs_err[m]) for m in MODELS]
        for name, errs in table:
            mae = float(np.mean(np.array(errs, dtype=np.float64)))
            mae_rows.append([name, len(errs), repr(mae), "%.4f" % mae])
        write_csv(os.path.join(out, "rno_mae_table.csv"),
                  ["rung", "n", "mae_unrounded", "mae_4dp"], mae_rows)
        print("MAE table written (not printed here; printed only at Step 4).")

    meta = {
        "session": 73, "run": run_id, "purpose": "D64 clean-room rebuild, "
        "fit and score only; changes no verdict, claim or figure (D64.1)",
        "versions": {"python": platform.python_version(),
                     "numpy": np.__version__,
                     "lightgbm": lightgbm.__version__,
                     "platform": platform.platform()},
        "lightgbm_api": "lightgbm.LGBMRegressor (scikit-learn API)",
        "settings_D21.4_D48.6": PARAMS,
        "train_window": [TRAIN_START, TRAIN_END],
        "test_window": [TEST_START, TEST_END],
        "input_row_counts": counts,
        "non_finite_dropped_at_load": nonfinite,
        "stored_column_checks": chk,
        "corrected_forecast": "forecast_c + predicted residual, full precision",
        "mae_basis": "mean(|obs_c - corrected_forecast_c|), numpy float64 mean;"
                     " 4 dp via '%.4f'",
        "models": meta_models,
        "files_opened": FILES_OPENED,
    }
    meta_path = os.path.join(out, "rno_fit_metadata.json")
    refuse_existing(meta_path)
    log_open(meta_path, "write")
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=1, sort_keys=False)
    if run_id == 1:
        write_csv(os.path.join(out, "rno_dropped_rows.csv"),
                  ["model", "window", "target_date", "reason"],
                  [[d["model"], d["window"], d["target_date"], d["reason"]]
                   for d in dropped_all])
    print("files opened by this run:")
    for p, mode in FILES_OPENED:
        print("  %-5s %s" % (mode, p))


def compare_runs():
    def load(p):
        log_open(p, "read")
        with open(p, newline="") as fh:
            return list(csv.DictReader(fh))
    a = load(os.path.join(OUT_DIR, "rno_test_predictions.csv"))
    b = load(os.path.join(RUN2_DIR, "rno_test_predictions.csv"))
    if [(r["model"], r["target_date"]) for r in a] != \
            [(r["model"], r["target_date"]) for r in b]:
        raise SystemExit("run 1 and run 2 row keys differ")
    out_rows = []
    print("Step 3 determinism: run 1 vs run 2, exact float equality")
    for model in MODELS:
        ra = [r for r in a if r["model"] == model]
        rb = [r for r in b if r["model"] == model]
        for col in ["predicted_residual_c", "corrected_forecast_c"]:
            same = sum(float(x[col]) == float(y[col]) for x, y in zip(ra, rb))
            mx = max(abs(float(x[col]) - float(y[col]))
                     for x, y in zip(ra, rb))
            print("  %-12s %-22s identical %d of %d, max abs diff %r"
                  % (model, col, same, len(ra), mx))
            out_rows.append([model, col, len(ra), same, repr(mx)])
    write_csv(os.path.join(OUT_DIR, "rno_determinism.csv"),
              ["model", "column", "n", "n_identical", "max_abs_diff"],
              out_rows)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def seal():
    path = os.path.join(OUT_DIR, "rno_mae_table.csv")
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    print("Step 4 sealed MAE table (test window %s..%s)" % (TEST_START,
                                                           TEST_END))
    print("  %-12s %4s  %-22s %s" % ("rung", "n", "unrounded", "4 dp"))
    for r in rows:
        print("  %-12s %4s  %-22s %s" % (r["rung"], r["n"], r["mae_unrounded"],
                                         r["mae_4dp"]))
    seal_path = os.path.join(OUT_DIR, "SEAL_SHA256.txt")
    refuse_existing(seal_path)
    lines = []
    for dp, _, fns in os.walk(OUT_DIR):
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            lines.append("%s  %s" % (sha256(p), os.path.relpath(p, ROOT)))
    lines.sort(key=lambda s: s.split("  ", 1)[1])
    print("SHA-256 of every file in data/rebuild/session73/:")
    for ln in lines:
        print("  " + ln)
    with open(seal_path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print("seal list written to", os.path.relpath(seal_path, ROOT))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--run"] and len(args) == 2 and args[1] in ("1", "2"):
        run_fit(int(args[1]))
    elif args == ["--compare-runs"]:
        compare_runs()
    elif args == ["--seal"]:
        seal()
    else:
        raise SystemExit(__doc__)
