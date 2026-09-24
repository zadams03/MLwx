"""Session 74, Step 4: the three diagnostic fits of D65.4 at RNO.

A verification only, with D64.1's standing (D65.1): it changes no verdict,
claim or figure. The reserved year is scored only to reproduce F109.

Each cell uses session 72's tables and session 73's own code path (imported
from scripts/session73_fit_score.py: load_tables, model_columns,
complete_case, PARAMS), Variant P, and changes only the named detail:
  C1  G15 flipped: record column order B, D, L, R, T. Target as session 73
      (residual_c, 3 dp).
  C2  G20 flipped: record target, obs_c - forecast_c unrounded (record
      script line 376). Column order as session 73 (B, L, D, T, R).
  C3  both flipped.

Usage (offline):
  python scripts/session74_diagnose.py --run       C1, C2, C3, one process
  python scripts/session74_diagnose.py --repeat    C3 again, own process
  python scripts/session74_diagnose.py --report    print and compare

No other fit. Every output path is new; the script refuses to overwrite
(SPEC 8.7 item 5).
"""

import sys

sys.dont_write_bytecode = True
import os  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Importing session 73 runs its libomp loader shim (D24) first.
import session73_fit_score as s73  # noqa: E402

import csv  # noqa: E402
import json  # noqa: E402
import platform  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm  # noqa: E402
from lightgbm import LGBMRegressor  # noqa: E402

ROOT = s73.ROOT
OUT_DIR = os.path.join(ROOT, "data", "rebuild", "session74")
RUN2_DIR = os.path.join(OUT_DIR, "run2")

# The record's F109 RNO value (data/processed/
# session63_reserved_confirm_grid.csv, RNO final_mae; F109 4 dp 1.2742).
RECORD_UNROUNDED = 1.2741517803385958
RECORD_4DP = "1.2742"
SESSION73_4DP = "1.2703"

# Session 73's added-feature order and the record's (FINAL_CODES, line 118).
S73_ORDER = ["L", "D", "T", "R"]
RECORD_ORDER = ["D", "L", "R", "T"]

CELLS = {
    "C1": {"order": RECORD_ORDER, "target": "rounded"},
    "C2": {"order": S73_ORDER, "target": "unrounded"},
    "C3": {"order": RECORD_ORDER, "target": "unrounded"},
}


def refuse_existing(path):
    if os.path.exists(path):
        raise SystemExit("refusing to overwrite existing file: %s"
                         % os.path.relpath(path, ROOT))


def cell_data(rows, cell):
    """Session 73's Variant P rows, mask and columns; only the added-feature
    order and the target differ by cell."""
    spec = CELLS[cell]
    _, mask = s73.model_columns("BDLRT_P")  # same mask as session 73
    feats = list(s73.B_COLS) + [s73.ADD_MODEL[k] for k in spec["order"]]
    train, _ = s73.complete_case(rows, "train", mask)
    test, _ = s73.complete_case(rows, "test", mask)
    if spec["target"] == "rounded":
        y = [r["residual_c"] for r in train]
    else:
        y = [r["obs_c"] - r["forecast_c"] for r in train]
    return feats, train, test, y


def fit_cell(rows, cell):
    feats, train, test, y = cell_data(rows, cell)
    X = np.array([[r[c] for c in feats] for r in train], dtype=np.float64)
    Xt = np.array([[r[c] for c in feats] for r in test], dtype=np.float64)
    m = LGBMRegressor(**s73.PARAMS)
    m.fit(X, np.array(y, dtype=np.float64))
    pred = m.predict(Xt)
    out = []
    for r, p in zip(test, pred):
        p = float(p)
        corrected = r["forecast_c"] + p
        out.append([cell, r["target_date"], s73.fmt(r["obs_c"]),
                    s73.fmt(r["forecast_c"]), s73.fmt(p), s73.fmt(corrected),
                    s73.fmt(abs(r["obs_c"] - corrected))])
    return feats, len(train), len(test), out


def run(cells, out_dir, label):
    rows, counts, nonfinite = s73.load_tables()
    print("session 74 %s, python %s, numpy %s, lightgbm %s"
          % (label, platform.python_version(), np.__version__,
             lightgbm.__version__))
    print("loaded rows:", counts, "non-finite dropped:",
          sum(nonfinite.values()))
    os.makedirs(out_dir, exist_ok=True)
    pred_path = os.path.join(out_dir, "rno_cell_predictions.csv")
    meta_path = os.path.join(out_dir, "rno_cell_metadata.json")
    refuse_existing(pred_path)
    refuse_existing(meta_path)
    all_rows, meta = [], {"session": 74, "run": label,
                          "purpose": "D65.4 diagnostic fits; changes no "
                          "verdict, claim or figure (D64.1, D65.1)",
                          "versions": {"python": platform.python_version(),
                                       "numpy": np.__version__,
                                       "lightgbm": lightgbm.__version__},
                          "params": s73.PARAMS, "cells": {}}
    for cell in cells:
        feats, n_tr, n_te, out = fit_cell(rows, cell)
        all_rows += out
        meta["cells"][cell] = {"feature_order": feats,
                               "target": CELLS[cell]["target"],
                               "n_train": n_tr, "n_test": n_te}
        print("%s fitted: n_train=%d n_test=%d order=%s target=%s"
              % (cell, n_tr, n_te, CELLS[cell]["order"],
                 CELLS[cell]["target"]))
    with open(pred_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cell", "target_date", "obs_c", "forecast_c",
                    "predicted_residual_c", "corrected_forecast_c",
                    "abs_error_c"])
        w.writerows(all_rows)
    with open(meta_path, "w") as fh:
        json.dump(meta, fh, indent=1)
    print("wrote", os.path.relpath(pred_path, ROOT), "and",
          os.path.relpath(meta_path, ROOT))


def load_preds(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    by = {}
    for r in rows:
        by.setdefault(r["cell"], []).append(r)
    return by


def mae_of(rows):
    return float(np.mean(np.array([float(r["abs_error_c"]) for r in rows],
                                  dtype=np.float64)))


def compare(a, b, col="predicted_residual_c"):
    if [r["target_date"] for r in a] != [r["target_date"] for r in b]:
        raise SystemExit("row keys differ")
    same = sum(float(x[col]) == float(y[col]) for x, y in zip(a, b))
    mx = max(abs(float(x[col]) - float(y[col])) for x, y in zip(a, b))
    return same, len(a), mx


def report():
    with open(os.path.join(OUT_DIR, "rno_cell_metadata.json")) as fh:
        meta = json.load(fh)
    with open(os.path.join(RUN2_DIR, "rno_cell_metadata.json")) as fh:
        meta2 = json.load(fh)
    p1 = load_preds(os.path.join(OUT_DIR, "rno_cell_predictions.csv"))
    p2 = load_preds(os.path.join(RUN2_DIR, "rno_cell_predictions.csv"))
    maes = {}
    print("Step 4 results (RNO, B+D,L,R,T, test 2024-08-01..2025-07-31)")
    print("  %-10s %7s %6s  %-22s %s" % ("cell", "n_train", "n_test",
                                         "MAE unrounded", "4 dp"))
    for cell, preds, md in [("C1", p1["C1"], meta), ("C2", p1["C2"], meta),
                            ("C3", p1["C3"], meta),
                            ("C3 repeat", p2["C3"], meta2)]:
        key = cell.split()[0]
        m = mae_of(preds)
        maes[cell] = m
        print("  %-10s %7d %6d  %-22r %.4f"
              % (cell, md["cells"][key]["n_train"],
                 md["cells"][key]["n_test"], m, m))

    same, n, mx = compare(p1["C3"], p2["C3"])
    same_c, _, mx_c = compare(p1["C3"], p2["C3"], "corrected_forecast_c")
    print("\nC3 vs its repeat: predicted residual equal %d of %d, max abs "
          "diff %r; corrected forecast equal %d of %d, max abs diff %r"
          % (same, n, mx, same_c, n, mx_c))
    print("C3 vs R0: not comparable -- R0 was skipped (Step 3).")

    print("\nEach cell against the record (1.2742; unrounded %r):"
          % RECORD_UNROUNDED)
    for cell in ["C1", "C2", "C3", "C3 repeat"]:
        m = maes[cell]
        print("  %-10s 4dp equal: %-5s  unrounded equal: %-5s  diff "
              "(cell - record) %r"
              % (cell, "%.4f" % m == RECORD_4DP, m == RECORD_UNROUNDED,
                 m - RECORD_UNROUNDED))

    print("\nCell-to-cell prediction comparisons (report only):")
    for a, b in [("C1", "C3"), ("C2", "C1"), ("C2", "C3")]:
        s, n, mx = compare(p1[a], p1[b])
        print("  %s vs %s: predicted residual equal %d of %d, max abs diff %r"
              % (a, b, s, n, mx))

    c3 = maes["C3"]
    c3_ok = ("%.4f" % c3 == RECORD_4DP and c3 == RECORD_UNROUNDED
             and maes["C3 repeat"] == c3)
    if c3_ok:
        cls = "A (explained): C3 matches the record at 4 dp and unrounded; R0 did not run"
    else:
        cls = ("not A: C3 does not match the record. B and C are defined by "
               "R0, which did not run, so they cannot be told apart")
    print("\nOutcome class (D65.6):", cls)
    c1, c2 = maes["C1"], maes["C2"]
    print("Attribution: C1 (G15 only) %.4f, C2 (G20 only) %.4f, C3 (both) "
          "%.4f; session 73 (neither) %s."
          % (c1, c2, c3, SESSION73_4DP))
    print("D65.7 Q33 trigger: C1 4 dp %.4f vs 1.2703 -> %s"
          % (c1, "FIRES" if "%.4f" % c1 != SESSION73_4DP
             else "does not fire"))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args == ["--run"]:
        run(["C1", "C2", "C3"], OUT_DIR, "run 1")
    elif args == ["--repeat"]:
        run(["C3"], RUN2_DIR, "run 2 (C3 repeat)")
    elif args == ["--report"]:
        report()
    else:
        raise SystemExit(__doc__)
