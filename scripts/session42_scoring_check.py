"""Session 42 Task 2: read-only scoring-consistency check.

Imports scripts/session39_sealed_test.py UNMODIFIED as a library (same
pattern session41_verify.py used) and does not touch, patch, or re-run any
part of it as a script. Fits nothing new that the frozen script did not
already fit -- it reuses the frozen script's own functions with the same
inputs and the same deterministic LightGBM settings (random_state=42,
deterministic=True), so predictions reproduce exactly.

Question: the frozen script's own `passes_persist = f5_mae < persist_mae`
compares f5_mae (computed over ALL of `test_rows`) against persist_mae
(computed over the narrower `common_persist` subset -- days with a usable
previous-day observation). Where `no_prev > 0` this is two different day
sets. This script recomputes raw/3-feature/5-feature MAE restricted to
exactly the common_persist day set, so the 5-vs-persistence comparison is
judged on a day set both members are actually defined on -- and reports
whether that changes any airport's verdict. No model is refit with
different settings; the model objects themselves are the frozen script's
own fitted models, evaluated on a different (smaller) slice of the same
already-computed predictions.
"""

import sys
from pathlib import Path
from datetime import timedelta

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import session39_sealed_test as s39  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402


def run_airport(station, target_hour):
    obs_full, _, _ = s39.load_obs_all(station, target_hour)

    train_grib = s39.load_grib_features(
        s39.TRAIN_GRIB_PATH, s39.TRAIN_START, s39.TRAIN_END,
        refuse_outside_window=True)[station]
    sealed_grib = s39.load_grib_features(
        s39.SEALED_GRIB_PATH, s39.SEALED_FROM, s39.SEALED_UNTIL,
        refuse_outside_window=True)[station]

    train_rows, _, _ = s39.join_rows(train_grib, obs_full, s39.TRAIN_START, s39.TRAIN_END)
    test_rows, _, _ = s39.join_rows(sealed_grib, obs_full, s39.SEALED_FROM, s39.SEALED_UNTIL)

    x3_tr = s39.features_3(train_rows)
    x5_tr = s39.features_5(train_rows)
    y_tr = np.array([r["resid"] for r in train_rows], dtype=float)

    m3 = lgb.LGBMRegressor(**s39.LGB_PARAMS)
    m3.fit(x3_tr, y_tr)
    m5 = lgb.LGBMRegressor(**s39.LGB_PARAMS)
    m5.fit(x5_tr, y_tr)

    x3_te = s39.features_3(test_rows)
    x5_te = s39.features_5(test_rows)
    pred3 = m3.predict(x3_te)
    pred5 = m5.predict(x5_te)

    e_raw = [r["fc"] - r["obs"] for r in test_rows]
    e_3 = [(r["fc"] + float(pred3[i])) - r["obs"] for i, r in enumerate(test_rows)]
    e_5 = [(r["fc"] + float(pred5[i])) - r["obs"] for i, r in enumerate(test_rows)]

    raw_mae_full = s39.mae(e_raw)
    f3_mae_full = s39.mae(e_3)
    f5_mae_full = s39.mae(e_5)

    # Same common_persist construction as the frozen script's run_airport.
    common_idx = []
    no_prev = 0
    for i, r in enumerate(test_rows):
        prev = obs_full.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev += 1
            continue
        common_idx.append((i, prev))

    e_persist_common = [prev - test_rows[i]["obs"] for i, prev in common_idx]
    e_raw_common = [e_raw[i] for i, _ in common_idx]
    e_3_common = [e_3[i] for i, _ in common_idx]
    e_5_common = [e_5[i] for i, _ in common_idx]

    persist_mae = s39.mae(e_persist_common) if e_persist_common else float("nan")
    raw_mae_common = s39.mae(e_raw_common)
    f3_mae_common = s39.mae(e_3_common)
    f5_mae_common = s39.mae(e_5_common)

    return dict(
        station=station,
        n_full=len(test_rows),
        n_common=len(common_idx),
        no_prev=no_prev,
        raw_mae_full=raw_mae_full,
        f3_mae_full=f3_mae_full,
        f5_mae_full=f5_mae_full,
        persist_mae=persist_mae,
        raw_mae_common=raw_mae_common,
        f3_mae_common=f3_mae_common,
        f5_mae_common=f5_mae_common,
        frozen_passes_persist=f5_mae_full < persist_mae,
        common_passes_persist=f5_mae_common < persist_mae,
        frozen_passes_raw=f5_mae_full < raw_mae_full,
        common_passes_raw=f5_mae_common < raw_mae_common,
    )


def main():
    print("Session 42 Task 2 -- scoring-consistency check (read-only, no frozen-script change)")
    print("Reproduces the frozen script's own fitted models and predictions; compares the")
    print("frozen script's own day-mismatched 5-vs-persistence comparison against an")
    print("apples-to-apples version restricted to the days persistence is actually defined on.")
    print()
    header = (f"{'station':<8} {'n_full':>6} {'n_common':>8} {'no_prev':>7} | "
              f"{'raw(full)':>10} {'3f(full)':>9} {'5f(full)':>9} | "
              f"{'raw(cmn)':>9} {'3f(cmn)':>8} {'5f(cmn)':>8} {'persist':>8} | "
              f"{'frozen>persist?':>16} {'common>persist?':>16} {'same verdict?':>14}")
    print(header)
    all_same = True
    for station, target_hour in s39.AIRPORTS.items():
        r = run_airport(station, target_hour)
        same_persist_verdict = r["frozen_passes_persist"] == r["common_passes_persist"]
        same_raw_verdict = r["frozen_passes_raw"] == r["common_passes_raw"]
        same_overall = same_persist_verdict and same_raw_verdict
        all_same = all_same and same_overall
        print(f"{r['station']:<8} {r['n_full']:>6} {r['n_common']:>8} {r['no_prev']:>7} | "
              f"{r['raw_mae_full']:>10.3f} {r['f3_mae_full']:>9.3f} {r['f5_mae_full']:>9.3f} | "
              f"{r['raw_mae_common']:>9.3f} {r['f3_mae_common']:>8.3f} {r['f5_mae_common']:>8.3f} "
              f"{r['persist_mae']:>8.3f} | "
              f"{'YES' if r['frozen_passes_persist'] else 'no':>16} "
              f"{'YES' if r['common_passes_persist'] else 'no':>16} "
              f"{'SAME' if same_overall else 'DIFFERENT':>14}")
    print()
    print(f"All five airports give the SAME pass/fail verdict under both day bases: {all_same}")


if __name__ == "__main__":
    main()
