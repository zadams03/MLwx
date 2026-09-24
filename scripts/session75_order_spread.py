"""Session 75: how much does column order alone move the fit? (Q33, D66.3)

Descriptive only. It changes no verdict, claim or figure; F109 stands.
Nothing is selected, tuned or adopted on these results.

Folds: `2022-23` and `2023-24` of D51's EXPERIMENT_FOLDS, all five
airports. Models: B (5 columns) and B+D,L,R,T (9 columns). Only the order
of the input columns varies:
  B+D,L,R,T  the record order (SPEC 8.8 G15), session 73's order (B, then
             L, D, T, R), and 100 orderings drawn with default_rng(75),
             redrawing any repeat, so 102 distinct orderings;
  B          all 120 orderings of its 5 columns.

No row dated 2024-08-01 or later is used. The feature loaders below read
only the committed v16-window files and drop any such row as it is read.
The observation series is filtered the same way straight after the
record's own loader returns it, before anything else touches it. Both
counts are printed.

Reused read-only by import from the record script
(scripts/session62_reserved_confirm.py): LGB_PARAMS, BASE_KEYS,
FAMILY_KEYS, FINAL_FEATURE_KEYS, features_matrix, mae, load_obs_all
(the record's pairing, SPEC 8.8 G1-G3), build_complete_case and join_obs
(complete-case rule, SPEC 8.3; unrounded target, G20; ascending date
order, G19). The fit is the record's call (G14):
LGBMRegressor(**LGB_PARAMS).fit(x, y) on a float64 array with no column
names.

Usage (offline):
  python scripts/session75_order_spread.py --anchors   2a: anchor fits and
                                                       the check against
                                                       the session 61 grid
  python scripts/session75_order_spread.py --repeat    2a: record-order
                                                       B+D,L,R,T again, in
                                                       its own process
  python scripts/session75_order_spread.py --spread    2b: every ordering
  python scripts/session75_order_spread.py --report    summary tables

Every output path is new; the script refuses to overwrite (SPEC 8.7
item 5). Printed output is appended to notes/session-75-output.txt.
"""

import sys

sys.dont_write_bytecode = True
import os  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Importing the record script runs its libomp loader shim (D24) first.
import session62_reserved_confirm as rec  # noqa: E402
from session48_reserved_year import (  # noqa: E402
    EXPERIMENT_FOLDS,
    assert_reserved_year_excluded,
)
from session60_combine_design import CANDIDATE_FEATURES  # noqa: E402

import csv  # noqa: E402
import itertools  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
from datetime import date  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm  # noqa: E402

ROOT = str(rec.ROOT)
OUT_DIR = os.path.join(ROOT, "data", "rebuild", "session75")
RUN2_DIR = os.path.join(OUT_DIR, "run2")
LOG_PATH = os.path.join(ROOT, "notes", "session-75-output.txt")

CUTOFF = date(2024, 8, 1)  # no row on or after this date is used (D66.3)
FOLD_LABELS = ["2022-23", "2023-24"]
FOLDS = {f[0]: f for f in EXPERIMENT_FOLDS if f[0] in FOLD_LABELS}

B_FILE = rec.PROCESSED / "grib_features_v16_window.csv"
SESSION61_GRID = rec.PROCESSED / "session61_combine_sweep_grid.csv"

RECORD_ORDER = list(rec.FINAL_FEATURE_KEYS)  # B, then D, L, R, T (G15)
S73_ORDER = list(rec.BASE_KEYS) + sum(
    (rec.FAMILY_KEYS[c] for c in ["L", "D", "T", "R"]), [])
B_CANONICAL = list(rec.BASE_KEYS)
N_DRAWN = 100
SEED = 75

# F109's margins over B (SPEC 8.5, B MAE minus B+D,L,R,T MAE, deg C) and
# F114's column-order shift. For the scale table only.
F109_MARGIN = {"EGLC": 0.0853, "LFPG": 0.0916, "DSM": 0.0279,
               "YSDU": 0.0387, "RNO": 0.1530}
F114_SHIFT = 0.0038


# ------------------------------------------------------------------ output

class Tee:
    def __init__(self, path):
        self.f = open(path, "a")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def refuse_existing(path):
    if os.path.exists(path):
        raise SystemExit("refusing to overwrite existing file: %s"
                         % os.path.relpath(path, ROOT))


def rel(path):
    return os.path.relpath(path, ROOT)


# ------------------------------------------------------------------ loading

def finite_float(s):
    """float(s) if it is a finite number, else None (SPEC 8.7 item 2)."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def load_file(path, cols, counts, tag):
    """station -> {date: {col: value}} from one committed CSV. A row dated
    on or after CUTOFF is dropped as it is read, before any value in it is
    parsed. A row with a non-finite or unparseable value in a used column
    is dropped. Both are counted."""
    out = {st: {} for st in rec.AIRPORTS}
    counts[tag] = {"read": 0, "removed_on_or_after_cutoff": 0,
                   "non_finite_dropped": 0, "kept": 0}
    c = counts[tag]
    with open(path) as fh:
        for r in csv.DictReader(fh):
            st = r["station"]
            if st not in out:
                continue
            c["read"] += 1
            d = date.fromisoformat(r["target_date"])
            if d >= CUTOFF:
                c["removed_on_or_after_cutoff"] += 1
                continue
            vals = {k: finite_float(r[k]) for k in cols}
            if any(v is None for v in vals.values()):
                c["non_finite_dropped"] += 1
                continue
            out[st][d] = vals
            c["kept"] += 1
    return out


def load_all():
    counts = {}
    b = load_file(B_FILE, ["temperature_grib_c", "cloud_cover_grib_pct",
                           "wind_speed_grib_kmh"], counts, "B")
    base = {st: {d: {"fc": v["temperature_grib_c"],
                     "cloud": v["cloud_cover_grib_pct"],
                     "wind": v["wind_speed_grib_kmh"]}
                 for d, v in rows.items()} for st, rows in b.items()}
    fam = {}
    for code, col in [("L", "lapse_rate_t2_t850"),
                      ("D", "dewpoint_depression_t2m"),
                      ("T", "pressure_tendency_3h_hpa"),
                      ("R", "dswrf_2h_wm2")]:
        fam[code] = load_file(CANDIDATE_FEATURES[code]["v16_file"], [col],
                              counts, code)
    merged = rec.build_complete_case(base, fam["L"], fam["D"], fam["T"],
                                     fam["R"])
    joined = {}
    obs_counts = {}
    for st, hour in rec.AIRPORTS.items():
        obs_all, far, no_temp = rec.load_obs_all(st, hour)
        removed = sum(1 for d in obs_all if d >= CUTOFF)
        nonfinite = sum(1 for d, v in obs_all.items()
                        if d < CUTOFF and not math.isfinite(v))
        obs = {d: v for d, v in obs_all.items()
               if d < CUTOFF and math.isfinite(v)}
        rows, no_obs = rec.join_obs(st, merged[st], obs)
        joined[st] = rows
        obs_counts[st] = {"obs_days_removed_on_or_after_cutoff": removed,
                          "obs_non_finite_dropped": nonfinite,
                          "complete_case_rows": len(merged[st]),
                          "no_usable_obs_dropped": no_obs,
                          "joined_rows": len(rows)}
    for st in joined:
        assert all(r["date"] < CUTOFF for r in joined[st])
    return joined, counts, obs_counts


def fold_rows(joined, st, label):
    _, tr_s, tr_e, te_s, te_e = FOLDS[label]
    assert tr_e < te_s < CUTOFF and te_e < CUTOFF
    train = [r for r in joined[st] if tr_s <= r["date"] <= tr_e]
    test = [r for r in joined[st] if te_s <= r["date"] <= te_e]
    return train, test


def print_load(counts, obs_counts):
    print("\nrows read, per committed file (all five airports):")
    for tag, c in counts.items():
        print("  %-2s read=%d removed_on_or_after_2024-08-01=%d "
              "non_finite_dropped=%d kept=%d" % (
                  tag, c["read"], c["removed_on_or_after_cutoff"],
                  c["non_finite_dropped"], c["kept"]))
    print("observations and joined rows, per airport:")
    for st, c in obs_counts.items():
        print("  %-4s obs days removed (on or after 2024-08-01)=%d "
              "obs non-finite dropped=%d complete-case rows=%d "
              "no usable obs dropped=%d joined=%d" % (
                  st, c["obs_days_removed_on_or_after_cutoff"],
                  c["obs_non_finite_dropped"], c["complete_case_rows"],
                  c["no_usable_obs_dropped"], c["joined_rows"]))


# ------------------------------------------------------------------ fitting

def fit_predict(train, test, keys):
    """The record's fit and score (G14, G20, G24), returning predictions."""
    x_tr = rec.features_matrix(train, keys)
    y_tr = np.array([r["resid"] for r in train], dtype=float)
    m = rec.lgb.LGBMRegressor(**rec.LGB_PARAMS)
    m.fit(x_tr, y_tr)
    pred = m.predict(rec.features_matrix(test, keys))
    errors = [(r["fc"] + float(pred[i])) - r["obs"]
              for i, r in enumerate(test)]
    return rec.mae(errors), pred


def bdlrt_orderings():
    """The 102 B+D,L,R,T orderings of D66.3: two anchors, then 100 draws."""
    out = [("record", RECORD_ORDER), ("session73", S73_ORDER)]
    seen = {tuple(RECORD_ORDER), tuple(S73_ORDER)}
    rng = np.random.default_rng(SEED)
    redrawn = 0
    while len(out) < 2 + N_DRAWN:
        perm = rng.permutation(len(RECORD_ORDER))
        keys = [RECORD_ORDER[i] for i in perm]
        if tuple(keys) in seen:
            redrawn += 1
            continue
        seen.add(tuple(keys))
        out.append(("draw%03d" % (len(out) - 1), keys))
    return out, redrawn


def b_orderings():
    out = []
    for i, p in enumerate(itertools.permutations(B_CANONICAL)):
        name = "canonical" if list(p) == B_CANONICAL else "perm%03d" % i
        out.append((name, list(p)))
    assert len(out) == 120 and out[0][0] == "canonical"
    return out


def header(label):
    print("\n" + "=" * 78)
    print("session 75 %s  python %s  numpy %s  lightgbm %s" % (
        label, platform.python_version(), np.__version__,
        lightgbm.__version__))
    print("=" * 78)


def check_folds():
    for label in FOLD_LABELS:
        assert_reserved_year_excluded(*FOLDS[label])
        print("fold %s: %s..%s train, %s..%s test; guard: no raise" % (
            label, *[str(x) for x in FOLDS[label][1:]]))


# ------------------------------------------------------------------ 2a

def anchor_run(out_dir, repeat):
    os.makedirs(out_dir, exist_ok=True)
    pred_path = os.path.join(out_dir, "anchor_predictions.csv")
    mae_path = os.path.join(out_dir, "anchor_mae.csv")
    refuse_existing(pred_path)
    if not repeat:
        refuse_existing(mae_path)
    check_folds()
    joined, counts, obs_counts = load_all()
    print_load(counts, obs_counts)
    cells = [("B+D,L,R,T", "record", RECORD_ORDER)]
    if not repeat:
        cells.append(("B", "canonical", B_CANONICAL))
    preds, maes = [], []
    for st in rec.AIRPORTS:
        for label in FOLD_LABELS:
            train, test = fold_rows(joined, st, label)
            for model, oname, keys in cells:
                m, pred = fit_predict(train, test, keys)
                maes.append([st, label, model, oname, len(train), len(test),
                             repr(m), "%.4f" % m])
                for r, p in zip(test, pred):
                    preds.append([st, label, model, oname,
                                  r["date"].isoformat(), repr(float(p))])
                print("%-4s %s %-9s %-9s n_train=%d n_test=%d MAE=%r (%.4f)"
                      % (st, label, model, oname, len(train), len(test), m, m))
    with open(pred_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["station", "fold", "model", "ordering", "target_date",
                    "predicted_residual_c"])
        w.writerows(preds)
    if not repeat:
        with open(mae_path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["station", "fold", "model", "ordering", "n_train",
                        "n_test", "mae", "mae_4dp"])
            w.writerows(maes)
        meta = {"session": 75, "purpose": "Q33, descriptive only (D66.3); "
                "changes no verdict, claim or figure",
                "versions": {"python": platform.python_version(),
                             "numpy": np.__version__,
                             "lightgbm": lightgbm.__version__},
                "lgb_params": rec.LGB_PARAMS, "cutoff": str(CUTOFF),
                "folds": {k: [str(x) for x in v[1:]]
                          for k, v in FOLDS.items()},
                "load_counts": counts, "obs_counts": obs_counts}
        with open(os.path.join(out_dir, "metadata.json"), "w") as fh:
            json.dump(meta, fh, indent=1)
    print("wrote", rel(pred_path), "" if repeat else "and " + rel(mae_path))


def session61_reference():
    """Session 61's committed grid: B and B+LDTR on these folds. Its fit
    orders the added columns by sorted(codes) = D, L, R, T, the record
    order, and B at BASE_KEYS order (session61_combine_sweep.py l.545)."""
    ref = {}
    with open(SESSION61_GRID) as fh:
        for r in csv.DictReader(fh):
            if r["fold"] in FOLD_LABELS and r["variant"] in ("B", "B+LDTR"):
                model = "B" if r["variant"] == "B" else "B+D,L,R,T"
                ref[(r["station"], r["fold"], model)] = r
    return ref


def compare_anchors():
    """Returns True only if every recorded value matches at 4 dp."""
    ref = session61_reference()
    ok = True
    print("\nanchor MAE against session 61's committed grid "
          "(same model, fold, airport, column order):")
    print("  %-4s %-7s %-9s %8s %8s %8s %8s %9s %9s  %s" % (
        "stn", "fold", "model", "n_train", "s61", "n_test", "s61",
        "MAE 4dp", "s61 4dp", "match"))
    with open(os.path.join(OUT_DIR, "anchor_mae.csv")) as fh:
        for r in csv.DictReader(fh):
            s = ref[(r["station"], r["fold"], r["model"])]
            match = (r["mae_4dp"] == "%.4f" % float(s["mae"])
                     and r["n_train"] == s["n_train"]
                     and r["n_test"] == s["n_test"])
            ok &= match
            print("  %-4s %-7s %-9s %8s %8s %8s %8s %9s %9s  %s" % (
                r["station"], r["fold"], r["model"], r["n_train"],
                s["n_train"], r["n_test"], s["n_test"], r["mae_4dp"],
                "%.4f" % float(s["mae"]), "yes" if match else "NO"))
    return ok


def compare_repeat():
    def load(path):
        with open(path) as fh:
            return {(r["station"], r["fold"], r["model"], r["ordering"],
                     r["target_date"]): float(r["predicted_residual_c"])
                    for r in csv.DictReader(fh)}
    a = load(os.path.join(OUT_DIR, "anchor_predictions.csv"))
    b = load(os.path.join(RUN2_DIR, "anchor_predictions.csv"))
    print("\ndeterminism: record-order B+D,L,R,T, run 1 against run 2 "
          "(separate process):")
    for st in rec.AIRPORTS:
        for label in FOLD_LABELS:
            keys = [k for k in b if k[0] == st and k[1] == label]
            diffs = [abs(a[k] - b[k]) for k in keys]
            equal = sum(1 for k in keys if a[k] == b[k])
            print("  %-4s %s  %d of %d predictions equal, max abs diff %r"
                  % (st, label, equal, len(keys), max(diffs)))


# ------------------------------------------------------------------ 2b

def spread_run():
    path = os.path.join(OUT_DIR, "spread_mae.csv")
    ord_path = os.path.join(OUT_DIR, "orderings.csv")
    refuse_existing(path)
    refuse_existing(ord_path)
    if not compare_anchors():
        raise SystemExit("STOP (session prompt 2a): a recorded MAE at the "
                         "same column order does not match. 2b not run.")
    check_folds()
    joined, counts, obs_counts = load_all()
    print_load(counts, obs_counts)
    bd, redrawn = bdlrt_orderings()
    bo = b_orderings()
    print("\norderings: B+D,L,R,T %d (2 anchors + %d drawn, %d redrawn), "
          "B %d" % (len(bd), len(bd) - 2, redrawn, len(bo)))
    with open(ord_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["model", "ordering", "columns"])
        for name, keys in bd:
            w.writerow(["B+D,L,R,T", name, "|".join(keys)])
        for name, keys in bo:
            w.writerow(["B", name, "|".join(keys)])
    rows = []
    n_fits = 0
    for st in rec.AIRPORTS:
        for label in FOLD_LABELS:
            train, test = fold_rows(joined, st, label)
            for model, orders in (("B+D,L,R,T", bd), ("B", bo)):
                for name, keys in orders:
                    m, _ = fit_predict(train, test, keys)
                    rows.append([st, label, model, name, len(train),
                                 len(test), repr(m)])
                    n_fits += 1
            print("  %-4s %s done (%d fits so far)" % (st, label, n_fits))
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["station", "fold", "model", "ordering", "n_train",
                    "n_test", "mae"])
        w.writerows(rows)
    print("fits run: %d. wrote %s and %s" % (n_fits, rel(path),
                                              rel(ord_path)))


# ------------------------------------------------------------------ report

def report():
    path = os.path.join(OUT_DIR, "summary.csv")
    refuse_existing(path)
    data = {}
    with open(os.path.join(OUT_DIR, "spread_mae.csv")) as fh:
        for r in csv.DictReader(fh):
            data.setdefault((r["station"], r["fold"], r["model"]), {})[
                r["ordering"]] = float(r["mae"])
    with open(os.path.join(OUT_DIR, "anchor_mae.csv")) as fh:
        for r in csv.DictReader(fh):
            ref = "record" if r["model"] == "B+D,L,R,T" else "canonical"
            got = data[(r["station"], r["fold"], r["model"])][ref]
            assert got == float(r["mae"]), "spread anchor != 2a anchor"
    print("\nthe spread's anchor fits equal the 2a anchor fits exactly "
          "(all 20)")
    out = []
    print("\nper airport, per fold. MAE in deg C. '%' columns are relative "
          "to that model's record-order MAE (B: canonical order).")
    for model, ref in (("B", "canonical"), ("B+D,L,R,T", "record")):
        print("\n%s (%d orderings)" % (model, 120 if model == "B" else 102))
        print("  %-4s %-7s %8s %8s %8s %8s %8s %8s %8s %8s %8s" % (
            "stn", "fold", "rec", "min", "max", "range", "sd", "min%",
            "max%", "range%", "sd%"))
        for st in rec.AIRPORTS:
            for label in FOLD_LABELS:
                v = data[(st, label, model)]
                a = np.array(list(v.values()))
                r0 = v[ref]
                lo, hi, sd = a.min(), a.max(), a.std()
                print("  %-4s %-7s %8.4f %8.4f %8.4f %8.4f %8.4f %+7.2f%% "
                      "%+7.2f%% %7.2f%% %7.2f%%" % (
                          st, label, r0, lo, hi, hi - lo, sd,
                          100 * (lo - r0) / r0, 100 * (hi - r0) / r0,
                          100 * (hi - lo) / r0, 100 * sd / r0))
                out.append({"station": st, "fold": label, "model": model,
                            "n_orderings": len(a), "record_order_mae": r0,
                            "min": lo, "max": hi, "range": hi - lo, "sd": sd,
                            "min_pct": 100 * (lo - r0) / r0,
                            "max_pct": 100 * (hi - r0) / r0,
                            "range_pct": 100 * (hi - lo) / r0,
                            "sd_pct": 100 * sd / r0})
    print("\nwin share and reading (D66.3 rule). Margin = canonical B MAE "
          "minus record-order B+D,L,R,T MAE.")
    print("  %-4s %-7s %10s %9s %9s %8s  %s" % (
        "stn", "fold", "wins", "share", "margin", "margin%", "reading"))
    wins_out = []
    for st in rec.AIRPORTS:
        for label in FOLD_LABELS:
            bd = np.array(list(data[(st, label, "B+D,L,R,T")].values()))
            b = np.array(list(data[(st, label, "B")].values()))
            wins = int((bd[:, None] < b[None, :]).sum())
            pairs = bd.size * b.size
            share = wins / pairs
            if wins == pairs:
                reading = ("B+D,L,R,T beats B by more than the column-order "
                           "spread, on this fold")
            elif wins == 0:
                reading = "B beats B+D,L,R,T by more than the spread"
            else:
                reading = "within the column-order spread"
            b0 = data[(st, label, "B")]["canonical"]
            f0 = data[(st, label, "B+D,L,R,T")]["record"]
            print("  %-4s %-7s %5d/%5d %8.2f%% %9.4f %+7.2f%%  %s" % (
                st, label, wins, pairs, 100 * share, b0 - f0,
                100 * (b0 - f0) / b0, reading))
            wins_out.append({"station": st, "fold": label, "wins": wins,
                             "pairs": pairs, "win_share": share,
                             "margin_c": b0 - f0,
                             "margin_pct": 100 * (b0 - f0) / b0,
                             "reading": reading})
    print("\nscale comparison (rough, different year). F109 is 2024-25 "
          "(training 1,226 days); these folds are 2022-23 (495 days) and "
          "2023-24 (860 days). A guide to scale only.")
    print("  %-4s %12s %11s %16s %16s" % (
        "stn", "F109 margin", "F114 shift", "BDLRT range 22-23",
        "BDLRT range 23-24"))
    rng_of = {(o["station"], o["fold"]): o["range"] for o in out
              if o["model"] == "B+D,L,R,T"}
    for st in rec.AIRPORTS:
        print("  %-4s %12.4f %11.4f %16.4f %16.4f" % (
            st, F109_MARGIN[st], F114_SHIFT, rng_of[(st, "2022-23")],
            rng_of[(st, "2023-24")]))
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    wpath = os.path.join(OUT_DIR, "win_share.csv")
    refuse_existing(wpath)
    with open(wpath, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(wins_out[0].keys()))
        w.writeheader()
        w.writerows(wins_out)
    print("\nwrote", rel(path), "and", rel(wpath))


def main():
    modes = {"--anchors", "--repeat", "--spread", "--report"}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        raise SystemExit("usage: session75_order_spread.py "
                         "--anchors | --repeat | --spread | --report")
    mode = sys.argv[1]
    if mode == "--anchors" and os.path.exists(LOG_PATH):
        raise SystemExit("refusing to overwrite existing file: %s"
                         % rel(LOG_PATH))
    sys.stdout = Tee(LOG_PATH)
    header(mode)
    if mode == "--anchors":
        anchor_run(OUT_DIR, repeat=False)
        compare_anchors()
    elif mode == "--repeat":
        anchor_run(RUN2_DIR, repeat=True)
        compare_repeat()
    elif mode == "--spread":
        spread_run()
    else:
        report()
    sys.stdout.flush()
    sys.stdout = sys.__stdout__


if __name__ == "__main__":
    main()
