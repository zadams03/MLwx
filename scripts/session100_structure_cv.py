"""Session 100: stage C's model-structure comparisons (D94) under D89's folds,
metric and rule. Offline. Build-choice scores only, never results (SPEC 2.5).

Three structures, each fit per fold (D89.3) with the record's settings:
  baseline  D88.4: one model per airport, cycle hour and lead (1,584 fits).
  A         one model per airport and lead, trained on all four cycle hours'
            rows at that lead; inputs G15 then cycle_hour (396 fits).
  B         one model per airport, trained on all cycle hours and leads 3 to
            24; inputs G15, cycle_hour, then lead (18 fits).
cycle_hour (0, 6, 12, 18) and lead (3 to 24) are plain numbers (D94.4).

Modes (one per run):
  --gate   refit the baseline as session 97 does and check every cell's n and
           MAE, the headline and the per-airport n against the record (F139),
           exact equality. Writes nothing.
  --score  fit the baseline, A and B, check the common row set, score them
           (D89.5) and apply D94.6. Writes
           data/processed/session100_structure_cv_scores.csv.
  --meta   write data/processed/session100_structure_cv.meta.txt.

Imported read only, after its SHA-256 check: scripts/session97_stagec_cv.py
(its table loader with the 2026-27 guard, table SHA-256 and complete_case
checks; its fold rule; its baseline fit; LGB_PARAMS and G15, which it takes
from the record script). This script never imports or calls the session-48
guard itself (D90.1). lightgbm is imported directly (D93.3).

Output files are written once and never overwritten (SPEC 8.7 item 5).
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
S97_SCRIPT = HERE / "session97_stagec_cv.py"
S97_SCRIPT_SHA256 = "987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91"   # F139


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256_file(S97_SCRIPT) != S97_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session97_stagec_cv.py's SHA-256 is not F139's")
sys.path.insert(0, str(HERE))
import session97_stagec_cv as s97  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
S97_SCORES = PROCESSED / "session97_stagec_cv_scores.csv"
S97_SCORES_SHA256 = "5604ccd16118fe772cd24a7be83b36ee62e500c78b3ed5bf55c76ed4e78d9d76"   # F139.4
SCORES_OUT = PROCESSED / "session100_structure_cv_scores.csv"
META_OUT = PROCESSED / "session100_structure_cv.meta.txt"
SCRIPT = Path(__file__).resolve()

STATIONS = s97.STATIONS
FOLDS = s97.FOLDS
CYCLE_HOURS = s97.CYCLE_HOURS
LEADS = s97.LEADS
G15 = s97.G15
LGB_PARAMS = s97.LGB_PARAMS
MODELS = ("baseline", "A", "B")

# F139.4: headline at full precision, and n per airport.
F139_HEADLINE = {"raw_gfs": 1.4616990883475995, "baseline": 1.049777501605027}
F139_N = {"EGLC": 96368, "LFPG": 96188, "DSM": 96389, "YSDU": 95645, "RNO": 96342, "SFO": 96330}


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


# ------------------------------------------------------------------ fitting

def split_rows(rows, t0, t1):
    """Session 97's selection (score_airport): complete-case rows only; per
    (cycle hour, lead) cell, training rows (valid < T0) and test rows
    (T0 <= cycle < T1), each in ascending cycle time. Rows are
    (cycle, x, temp, obs)."""
    train = {(h, n): [] for h in CYCLE_HOURS for n in LEADS}
    test = {(h, n): [] for h in CYCLE_HOURS for n in LEADS}
    for cycle, valid, h, n, complete, obs, temp, x in rows:
        if not complete:
            continue
        role = s97.fold_role(cycle, valid, t0, t1)
        if role == "train":
            if not valid < t0:
                raise SystemExit("STOP: a training row is not before T0")
            train[(h, n)].append((cycle, x, temp, obs))
        elif role == "test":
            test[(h, n)].append((cycle, x, temp, obs))
    for d in (train, test):
        for k in d:
            d[k].sort(key=lambda r: r[0])
    return train, test


def fit_baseline(st, label, t0, train, test, timer):
    """D88.4, as session 97 fits it: one model per cycle hour and lead.
    Returns {(h, n): forecasts} and {(h, n): training count}."""
    fc, ntr = {}, {}
    for h in CYCLE_HOURS:
        for n in LEADS:
            tr, te = train[(h, n)], test[(h, n)]
            if not tr or not te:
                raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: train {len(tr)}, test {len(te)}")
            if tr[-1][0] >= te[0][0] or max(r[0] for r in tr) + dt.timedelta(hours=n) >= t0:
                raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: training not before test")
            t = time.time()
            fc[(h, n)] = s97.fit_predict([(r[1], r[2], r[3]) for r in tr], [(r[1], r[2], r[3]) for r in te])
            timer["baseline"] += time.time() - t
            ntr[(h, n)] = len(tr)
    return fc, ntr


def fit_pooled(cells, train, test, extra, timer, name):
    """One model over the given (cycle hour, lead) cells. Training rows in
    ascending cycle time, then lead (G19). Inputs: G15 then extra(h, n)
    (D94.4). Returns {(h, n): (test cycle times, forecasts)} and the training
    count."""
    tr = sorted(((r[0], n, r[1] + extra(h, n), r[2], r[3]) for (h, n) in cells for r in train[(h, n)]),
                key=lambda r: (r[0], r[1]))
    te = sorted(((r[0], n, r[1] + extra(h, n), r[2], r[3], h) for (h, n) in cells for r in test[(h, n)]),
                key=lambda r: (r[0], r[1]))
    t = time.time()
    fc = s97.fit_predict([(r[2], r[3], r[4]) for r in tr], [(r[2], r[3], r[4]) for r in te])
    timer[name] += time.time() - t
    out = {k: ([], []) for k in cells}
    for i, r in enumerate(te):
        out[(r[5], r[1])][0].append(r[0])
        out[(r[5], r[1])][1].append(fc[i])
    return out, len(tr)


def score_airport(st, models, timer):
    """Per fold: fit each requested structure. Returns
    cells {(fold, h, n): {"obs", "raw", model: forecasts}}, train counts
    {model: [(count, fold, key)]} and the number of fits per model."""
    rows = s97.load_table(st)
    cells, ntrain, fits = {}, {m: [] for m in models}, {m: 0 for m in models}
    for label, t0, t1 in FOLDS:
        train, test = split_rows(rows, t0, t1)
        base_fc, base_n = fit_baseline(st, label, t0, train, test, timer)
        fits["baseline"] += len(base_fc)
        for (h, n), c in base_n.items():
            ntrain["baseline"].append((c, label, (h, n)))
        for (h, n) in base_fc:
            te = test[(h, n)]
            cells[(label, h, n)] = {"obs": [r[3] for r in te], "raw": [r[2] for r in te],
                                    "cycles": [r[0] for r in te], "baseline": base_fc[(h, n)]}
        pooled_out = []
        if "A" in models:
            for n in LEADS:
                out, c = fit_pooled([(h, n) for h in CYCLE_HOURS], train, test, lambda h, n: [float(h)], timer, "A")
                fits["A"] += 1
                ntrain["A"].append((c, label, n))
                pooled_out.append(("A", out))
        if "B" in models:
            out, c = fit_pooled([(h, n) for h in CYCLE_HOURS for n in LEADS], train, test,
                                lambda h, n: [float(h), float(n)], timer, "B")
            fits["B"] += 1
            ntrain["B"].append((c, label, None))
            pooled_out.append(("B", out))
        # The common row set: each cell's test rows are exactly the baseline's.
        for m, out in pooled_out:
            for (h, n), (cyc, fc) in out.items():
                cell = cells[(label, h, n)]
                if cyc != cell["cycles"]:
                    raise SystemExit(f"STOP: {m} test rows differ from the baseline's at {st} {label} {h}z lead {n}")
                cell[m] = fc
    return cells, ntrain, fits


def errors(cells, stations, methods):
    """{(st, fold, h, n, method): errors (obs minus forecast)}; raw_gfs is temp."""
    errs = {}
    for st in stations:
        for label, _, _ in FOLDS:
            for h in CYCLE_HOURS:
                for n in LEADS:
                    c = cells[(st, label, h, n)]
                    for m in methods:
                        fc = c["raw"] if m == "raw_gfs" else c[m]
                        if len(fc) != len(c["obs"]):
                            raise SystemExit(f"STOP: {m} n differs at {st} {label} {h}z lead {n}")
                        errs[(st, label, h, n, m)] = [o - fc[i] for i, o in enumerate(c["obs"])]
    return errs


def run_all(models):
    cells, ntrain, fits = {}, {}, {}
    timer = {m: 0.0 for m in models}
    for st in STATIONS:
        t = time.time()
        c, nt, f = score_airport(st, models, timer)
        for k, v in c.items():
            cells[(st,) + k] = v
        for m in models:
            ntrain.setdefault(m, []).extend((cnt, st, fold, key) for cnt, fold, key in nt[m])
            fits[m] = fits.get(m, 0) + f[m]
        print(f"  {st}: " + ", ".join(f"{m} {f[m]}" for m in models) + f" fits, {time.time() - t:.1f} s")
    return cells, ntrain, fits, timer


# ------------------------------------------------------------------ the gate

def check_against_s97(errs):
    """Every (airport, fold, cycle hour, lead) cell's n and MAE, for raw_gfs and
    the baseline, against session 97's scores file; headline and per-airport n
    against F139. Returns (cells equal, cells compared, headline equal,
    airports' n equal)."""
    got = sha256_file(S97_SCORES)
    if got != S97_SCORES_SHA256:
        raise SystemExit(f"STOP: {S97_SCORES.name} SHA-256 {got} is not F139.4's")
    rec = {}
    with open(S97_SCORES, newline="") as f:
        for r in csv.DictReader(f):
            rec[(r["station"], r["fold"], int(r["cycle_hour"]), int(r["lead"]), r["method"])] = \
                (int(r["n"]), float(r["mae"]))
    equal = 0
    for k, (n, m) in rec.items():
        e = errs[k]
        if len(e) == n and s97.mae(e) == m:
            equal += 1
    head = {m: sum(s97.pooled(errs, m, st)[0] for st in STATIONS) / len(STATIONS) for m in ("raw_gfs", "baseline")}
    head_eq = sum(head[m] == F139_HEADLINE[m] for m in head)
    n_eq = sum(s97.pooled(errs, "baseline", st)[1] == F139_N[st] for st in STATIONS)
    return equal, len(rec), head, head_eq, n_eq


def run_gate(args):
    t_start = time.time()
    print(f"SESSION 100 --gate (offline), start {now_utc()}; {versions()}")
    print(f"session97_stagec_cv.py SHA-256 checked before import: {S97_SCRIPT_SHA256}")
    cells, ntrain, fits, timer = run_all(("baseline",))
    errs = errors(cells, STATIONS, ("raw_gfs", "baseline"))
    equal, total, head, head_eq, n_eq = check_against_s97(errs)
    print(f"baseline fits: {fits['baseline']}")
    print(f"cells equal to session97_stagec_cv_scores.csv (n and MAE, raw_gfs and baseline): {equal} of {total}")
    print(f"headline equal to F139 at full precision: {head_eq} of 2 "
          f"(raw_gfs {head['raw_gfs']!r}, baseline {head['baseline']!r})")
    print(f"per-airport n equal to F139.4: {n_eq} of 6")
    ok = equal == total == 3168 and head_eq == 2 and n_eq == 6
    print(f"GATE {'PASS' if ok else 'FAIL'}; end {now_utc()}; run time {time.time() - t_start:.1f} s")
    if not ok:
        raise SystemExit(1)


# ------------------------------------------------------------------ --score

def d89_6(errs, inc, ch):
    """D89.6, challenger ch against incumbent inc. Ties keep the incumbent."""
    hi = sum(s97.pooled(errs, inc, st)[0] for st in STATIONS) / len(STATIONS)
    hc = sum(s97.pooled(errs, ch, st)[0] for st in STATIONS) / len(STATIONS)
    red = (hi - hc) / hi
    airports = sum(s97.pooled(errs, ch, st)[0] < s97.pooled(errs, inc, st)[0] for st in STATIONS)
    folds = 0
    for label, _, _ in FOLDS:
        fi = sum(s97.pooled(errs, inc, st, folds=[label])[0] for st in STATIONS) / len(STATIONS)
        fc = sum(s97.pooled(errs, ch, st, folds=[label])[0] for st in STATIONS) / len(STATIONS)
        folds += fc < fi
    parts = (red > 0.01, airports >= 4, folds >= 2)
    return {"red": red, "airports": airports, "folds": folds, "parts": parts, "pass": all(parts)}


def print_test(name, t, note=""):
    a, b, c = t["parts"]
    print(f"  {name}{note}:")
    print(f"    (a) headline reduction {t['red']:.6f} ({100 * t['red']:.3f} %), above 0.01: {'yes' if a else 'no'}")
    print(f"    (b) airports where the challenger is lower: {t['airports']} of 6, 4 or more: {'yes' if b else 'no'}")
    print(f"    (c) folds where the challenger is lower: {t['folds']} of 3, 2 or more: {'yes' if c else 'no'}")
    print(f"    => {'PASS: the challenger replaces the incumbent' if t['pass'] else 'not passed: the incumbent stays'}")


def run_score(args):
    t_start = time.time()
    if SCORES_OUT.exists():
        raise SystemExit(f"STOP: {SCORES_OUT} already exists; not overwriting it")
    print(f"SESSION 100 --score (offline), start {now_utc()}; {versions()}")
    print(f"G15 + extras (D94.4): A {G15 + ['cycle_hour']}; B {G15 + ['cycle_hour', 'lead']}")
    print(f"LGB_PARAMS (D94.5): {LGB_PARAMS}")
    print("BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5).")
    cells, ntrain, fits, timer = run_all(MODELS)
    print("common row set: every cell's A and B test rows equal the baseline's (count and cycle times): yes")
    errs = errors(cells, STATIONS, ("raw_gfs",) + MODELS)
    equal, total, head, head_eq, n_eq = check_against_s97(errs)
    print(f"baseline refit against session 97: cells equal {equal} of {total}; headline {head_eq} of 2; n {n_eq} of 6")
    if not (equal == total == 3168 and head_eq == 2 and n_eq == 6):
        raise SystemExit("STOP: the baseline refit does not reproduce session 97")
    print("fits: " + ", ".join(f"{m} {fits[m]}" for m in MODELS)
          + "; fit time: " + ", ".join(f"{m} {timer[m]:.1f} s" for m in MODELS))

    rows = []
    for m in MODELS:
        for st in STATIONS:
            for label, _, _ in FOLDS:
                for h in CYCLE_HOURS:
                    for n in LEADS:
                        e = errs[(st, label, h, n, m)]
                        rows.append([st, label, h, n, m, len(e), s97.mae(e), s97.mean_error(e), m])
    header = ["station", "fold", "cycle_hour", "lead", "method", "n", "mae", "mean_error", "model"]
    text = s97.csv_text(header, [[s97.fmt(v) for v in r] for r in rows])
    s97.write_new(SCORES_OUT, text)
    print(f"wrote {SCORES_OUT.relative_to(ROOT)}: {len(rows)} rows, SHA-256 "
          f"{hashlib.sha256(text.encode()).hexdigest()}")

    methods = ("raw_gfs",) + MODELS
    print("\n" + "=" * 90)
    print("SUMMARY. BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C. Common row set (D89.5).")
    print("=" * 90)
    print("\nPer airport, pooled over folds, cycle hours and leads 3 to 24:")
    print(f"  {'airport':<7} {'n':>8} " + " ".join(f"{m:>9}" for m in methods))
    for st in STATIONS:
        print(f"  {st:<7} {s97.pooled(errs, 'baseline', st)[1]:>8,} "
              + " ".join(f"{s97.pooled(errs, m, st)[0]:>9.4f}" for m in methods))
    hl = {m: sum(s97.pooled(errs, m, st)[0] for st in STATIONS) / len(STATIONS) for m in methods}
    print(f"  {'HEADLINE':<16} " + " ".join(f"{hl[m]:>9.4f}" for m in methods))
    print("  full precision: " + ", ".join(f"{m} {hl[m]!r}" for m in methods))

    print("\nPer fold: each airport's MAE over the fold's rows, and the fold-level MAE (unweighted mean of six):")
    print(f"  {'fold':<8} {'method':<9} " + " ".join(f"{s:>7}" for s in STATIONS) + f" {'fold-level':>11}")
    for label, _, _ in FOLDS:
        for m in methods:
            vals = [s97.pooled(errs, m, st, folds=[label])[0] for st in STATIONS]
            print(f"  {label:<8} {m:<9} " + " ".join(f"{v:>7.4f}" for v in vals) + f" {sum(vals) / 6:>11.4f}")

    print("\nSix-airport mean MAE per lead (each airport pooled over folds and cycle hours):")
    print(f"  {'lead':>4} " + " ".join(f"{m:>9}" for m in methods))
    for n in LEADS:
        print(f"  {n:>4} " + " ".join(
            f"{sum(s97.pooled(errs, m, st, leads=[n])[0] for st in STATIONS) / 6:>9.4f}" for m in methods))

    print("\nSmallest training count of any single model (ties: first in airport, fold, key order):")
    for m in MODELS:
        c, st, fold, key = min(ntrain[m], key=lambda r: r[0])
        print(f"  {m:<8} {c:>7,}  ({st}, fold {fold}, {'(cycle hour, lead) ' + str(key) if m == 'baseline' else 'lead ' + str(key) if m == 'A' else 'all cells'})")

    print("\nD89.6 tests (incumbent minus challenger, over incumbent; ties keep the incumbent):")
    ta = d89_6(errs, "baseline", "A")
    tb = d89_6(errs, "baseline", "B")
    tab = d89_6(errs, "B", "A")
    print_test("A against the baseline", ta)
    print_test("B against the baseline", tb)
    both = ta["pass"] and tb["pass"]
    print_test("A against B (incumbent B)", tab, "" if both else " [DESCRIPTIVE: D94.6 does not use it]")
    if not ta["pass"] and not tb["pass"]:
        chosen = "baseline"
    elif ta["pass"] != tb["pass"]:
        chosen = "A" if ta["pass"] else "B"
    else:
        chosen = "A" if tab["pass"] else "B"
    print(f"\nD94.6 CHOSEN STRUCTURE: {chosen} (a build choice, not a result)")
    print(f"\nend {now_utc()}; run time {time.time() - t_start:.1f} s")


# ------------------------------------------------------------------ --meta

def run_meta(args):
    if not SCORES_OUT.exists():
        raise SystemExit(f"STOP: {SCORES_OUT} does not exist")
    lines = [
        "session100_structure_cv.meta.txt",
        f"written {now_utc()} by scripts/session100_structure_cv.py --meta",
        "",
        "What the file is (BUILD-CHOICE SCORES, NOT RESULTS, SPEC 2.5):",
        "  session100_structure_cv_scores.csv: per model (baseline, A, B), airport, fold, cycle hour and",
        "    lead 3 to 24: n, MAE and mean error (obs_tmpc minus forecast), full precision. Columns are",
        "    session 97's plus model; method repeats the model's name, so the baseline rows' first eight",
        "    columns match session 97's baseline rows. Common row set (D89.5).",
        "  baseline: D88.4, one model per airport, fold, cycle hour and lead (1,584 fits).",
        "  A: one model per airport, fold and lead; G15 then cycle_hour (396 fits).",
        "  B: one model per airport and fold; G15, cycle_hour, then lead (18 fits).",
        "",
        "Rules: DECISIONS D94 (structures, inputs, settings, choice), D89.3 (folds), D89.5 (metric),",
        "  D89.6 (rule).",
        "",
        "Inputs and their SHA-256:",
    ]
    for st in STATIONS:
        name, _ = s97.TABLES[st]
        lines.append(f"  MLwx-stagec/{name} {sha256_file(s97.STAGEC_DIR / name)}")
    for p in (S97_SCORES, S97_SCRIPT, s97.RECORD_SCRIPT):
        lines.append(f"  {p.relative_to(ROOT)} {sha256_file(p)}")
    lines += [
        "",
        f"Script: scripts/session100_structure_cv.py {sha256_file(SCRIPT)}",
        "",
        "Outputs and their SHA-256:",
        f"  {SCORES_OUT.relative_to(ROOT)} {sha256_file(SCORES_OUT)}",
        "",
        f"LGB_PARAMS as passed (from session 97, which takes them from scripts/session62_reserved_confirm.py): "
        f"{LGB_PARAMS}",
        f"G15 column order (same source): {G15}",
        "Fit counts: --gate baseline 1,584; --score baseline 1,584, A 396, B 18. No model saved.",
        f"Run times (as printed by the runs): {args.run_times}",
        f"Versions: {versions()}",
    ]
    text = "\n".join(lines) + "\n"
    s97.write_new(META_OUT, text)
    print(f"wrote {META_OUT.relative_to(ROOT)}: {len(lines)} lines, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    g.add_argument("--meta", action="store_true")
    ap.add_argument("--run-times", default="not given", help="--meta only: the run times the runs printed")
    args = ap.parse_args()
    if args.gate:
        run_gate(args)
    elif args.score:
        run_score(args)
    elif args.meta:
        run_meta(args)


if __name__ == "__main__":
    main()
