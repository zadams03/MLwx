"""Session 103: the bias-drift test (D97) under D89's folds, metric and rule.
Offline. Build-choice scores only, never results (SPEC 2.5).

One challenger, `drift`: the baseline's forecast (D88.4) plus b, a decaying
average of the baseline's own recent errors (observation minus baseline
forecast). After each new error e: b = (1 - w) x b + w x e, with w = 0.02
(D97.4). One tracker per airport, fold, cycle hour and lead (D97.5), updated
only by that cell's scored test rows, in ascending valid time. The forecast
from the cycle starting at c uses only errors whose valid time is before c
(D97.6). Every tracker starts at b = 0 at its fold's T0 (D97.7).

Modes (one per run):
  --check  the tracker on hand-made cells, each with an answer worked out by
           hand below. Reads no table. Writes nothing.
  --gate   refit the baseline as session 100's --gate does and check every
           cell's n and MAE, the headline and the per-airport n against F139,
           exact equality. Writes nothing.
  --score  fit the baseline, check it again, run the tracker, score raw_gfs,
           baseline and drift (D89.5), and apply D89.6 (D97.8). Writes
           data/processed/session103_bias_drift_cv_scores.csv.
  --meta   write data/processed/session103_bias_drift_cv.meta.txt.

Imported read only, after its SHA-256 check: scripts/session100_structure_cv.py
(F143), which checks and imports scripts/session97_stagec_cv.py itself. Used
from it: score_airport (through run_all), errors, check_against_s97 and d89_6.
This script never imports or calls the session-48 guard itself (D90.1).
lightgbm is imported directly (D93.3).

Output files are written once and never overwritten (SPEC 8.7 item 5).
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
S100_SCRIPT = HERE / "session100_structure_cv.py"
S100_SCRIPT_SHA256 = "67e709ea0925d84b4e257c44c5a95211f46a5ff5443408d7c526dbffb28d6957"   # F143


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256_file(S100_SCRIPT) != S100_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session100_structure_cv.py's SHA-256 is not F143's")
sys.path.insert(0, str(HERE))
import session100_structure_cv as s100  # noqa: E402

import argparse  # noqa: E402
import bisect  # noqa: E402
import datetime as dt  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

s97 = s100.s97

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
SCORES_OUT = PROCESSED / "session103_bias_drift_cv_scores.csv"
META_OUT = PROCESSED / "session103_bias_drift_cv.meta.txt"
SCRIPT = Path(__file__).resolve()

STATIONS = s100.STATIONS
FOLDS = s100.FOLDS
CYCLE_HOURS = s100.CYCLE_HOURS
LEADS = s100.LEADS
LGB_PARAMS = s100.LGB_PARAMS
METHODS = ("raw_gfs", "baseline", "drift")

W = 0.02   # D97.4: NOAA's NAEFS bias-correction weight, fixed in advance, not tuned


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


# ------------------------------------------------------------------ the tracker

def track(rows, w=W):
    """One cell's tracker (D97.5 to D97.7). rows: (cycle, lead, obs, baseline
    forecast), in ascending cycle time. A row's valid time is its cycle plus its
    lead in hours. Before a row from cycle c is corrected, every error not yet
    applied whose valid time is before c is applied, in ascending valid time;
    then the row's own error (obs minus baseline forecast) is queued.

    Returns, per row, the corrected forecast, the number of errors used and the
    latest valid time used (None if none); and b after all the cell's errors
    are applied (descriptive, D97.9)."""
    b = 0.0
    pending = []   # (valid time, error), in ascending valid time
    used, latest = 0, None
    corrected, n_used, latest_used = [], [], []
    prev = None
    for cycle, lead, obs, fc in rows:
        if prev is not None and not prev < cycle:
            raise SystemExit("STOP: tracker rows are not in ascending cycle time")
        prev = cycle
        while pending and pending[0][0] < cycle:
            valid, e = pending.pop(0)
            b = (1 - w) * b + w * e
            used += 1
            latest = valid
        corrected.append(fc + b)
        n_used.append(used)
        latest_used.append(latest)
        bisect.insort(pending, (cycle + dt.timedelta(hours=lead), obs - fc))
    for _, e in pending:
        b = (1 - w) * b + w * e
    return corrected, n_used, latest_used, b


# ------------------------------------------------------------------ --check

def run_check(args):
    print(f"SESSION 103 --check (offline, no table read), start {now_utc()}; w = {W}")

    def days(*ds, hour=12):
        return [dt.datetime(2024, 1, d, hour) for d in ds]

    # Each case: rows, expected correction (corrected minus baseline) and errors used, per row.
    cases = []
    # 1. Daily cycles, lead 3, errors 1.0 each (obs 11.0, baseline 10.0).
    #    b: 0; 0.02 x 1 = 0.02; 0.98 x 0.02 + 0.02 = 0.0396; 0.98 x 0.0396 + 0.02 = 0.058808.
    cases.append(("daily, lead 3, errors 1.0 x 4",
                  [(c, 3, 11.0, 10.0) for c in days(1, 2, 3, 4)],
                  [0.0, 0.02, 0.0396, 0.058808], [0, 1, 2, 3]))
    # 2. Daily cycles, lead 24, errors 1.0 each. Day k's error is valid at day k + 1's
    #    cycle time, which is not before it, so it is first used on day k + 2: 0, 0, 0.02.
    cases.append(("daily, lead 24, errors 1.0 x 3",
                  [(c, 24, 11.0, 10.0) for c in days(1, 2, 3)],
                  [0.0, 0.0, 0.02], [0, 0, 1]))
    # 3. A missing day: lead 3 on days 1, 2 and 4, errors 1.0, 2.0, 0.5. Day 4 uses both
    #    earlier errors: 0.98 x (0.02 x 1.0) + 0.02 x 2.0 = 0.0196 + 0.04 = 0.0596.
    cases.append(("missing day, lead 3, days 1, 2, 4",
                  [(c, 3, 10.0 + e, 10.0) for c, e in zip(days(1, 2, 4), (1.0, 2.0, 0.5))],
                  [0.0, 0.02, 0.0596], [0, 1, 2]))

    all_ok = True
    latest_ok, latest_rows = 0, 0
    for name, rows, want, want_n in cases:
        corrected, n_used, latest_used, _ = track(rows)
        got = [corrected[i] - r[3] for i, r in enumerate(rows)]
        ok = all(abs(g - x) <= 1e-12 for g, x in zip(got, want)) and n_used == want_n and len(got) == len(want)
        all_ok &= ok
        print(f"  {'PASS' if ok else 'FAIL'}: {name}: corrections {[round(g, 12) for g in got]}, "
              f"expected {want}; errors used {n_used}, expected {want_n}")
        for i, r in enumerate(rows):
            latest_rows += 1
            latest_ok += latest_used[i] is None or latest_used[i] < r[0]
    ok = latest_ok == latest_rows
    all_ok &= ok
    print(f"  {'PASS' if ok else 'FAIL'}: latest valid time used is before the row's cycle: "
          f"{latest_ok} of {latest_rows} rows")
    print(f"CHECK {'PASS' if all_ok else 'FAIL'}")
    if not all_ok:
        raise SystemExit(1)


# ------------------------------------------------------------------ --gate

def gate_counts(errs):
    equal, total, head, head_eq, n_eq = s100.check_against_s97(errs)
    ok = equal == total == 3168 and head_eq == 2 and n_eq == 6
    return ok, equal, total, head, head_eq, n_eq


def run_gate(args):
    t_start = time.time()
    print(f"SESSION 103 --gate (offline), start {now_utc()}; {versions()}")
    print(f"session100_structure_cv.py SHA-256 checked before import: {S100_SCRIPT_SHA256}")
    cells, _, fits, timer = s100.run_all(("baseline",))
    errs = s100.errors(cells, STATIONS, ("raw_gfs", "baseline"))
    ok, equal, total, head, head_eq, n_eq = gate_counts(errs)
    print(f"baseline fits: {fits['baseline']}; fit time {timer['baseline']:.1f} s")
    print(f"cells equal to session97_stagec_cv_scores.csv (n and MAE, raw_gfs and baseline): {equal} of {total}")
    print(f"headline equal to F139 at full precision: {head_eq} of 2 "
          f"(raw_gfs {head['raw_gfs']!r}, baseline {head['baseline']!r})")
    print(f"per-airport n equal to F139.4: {n_eq} of 6")
    print(f"GATE {'PASS' if ok else 'FAIL'}; end {now_utc()}; run time {time.time() - t_start:.1f} s")
    if not ok:
        raise SystemExit(1)


# ------------------------------------------------------------------ --score

def pooled_me(errs, meth, st, folds=None, leads=None):
    """Mean error over the concatenated errors (same order as s97.pooled)."""
    e = []
    for label, _, _ in FOLDS:
        if folds and label not in folds:
            continue
        for h in CYCLE_HOURS:
            for n in LEADS:
                if leads and n not in leads:
                    continue
                e.extend(errs[(st, label, h, n, meth)])
    return s97.mean_error(e)


def run_score(args):
    t_start = time.time()
    if SCORES_OUT.exists():
        raise SystemExit(f"STOP: {SCORES_OUT} already exists; not overwriting it")
    print(f"SESSION 103 --score (offline), start {now_utc()}; {versions()}")
    print(f"LGB_PARAMS: {LGB_PARAMS}; w = {W}")
    print("BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5).")
    cells, _, fits, timer = s100.run_all(("baseline",))
    errs = s100.errors(cells, STATIONS, ("raw_gfs", "baseline"))
    ok, equal, total, head, head_eq, n_eq = gate_counts(errs)
    print(f"baseline refit against F139: cells equal {equal} of {total}; headline {head_eq} of 2 "
          f"(baseline {head['baseline']!r}); n {n_eq} of 6")
    if not ok or head["baseline"] != s100.F139_HEADLINE["baseline"]:
        raise SystemExit("STOP: the baseline refit does not reproduce F139")
    print(f"baseline fits: {fits['baseline']}; fit time {timer['baseline']:.1f} s")

    # The tracker, one per airport, fold, cycle hour and lead.
    t = time.time()
    rows_total, b_zero, late = 0, {label: 0 for label, _, _ in FOLDS}, 0
    end_b = {}
    for (st, label, h, n), c in cells.items():
        rows = [(cy, n, o, f) for cy, o, f in zip(c["cycles"], c["obs"], c["baseline"])]
        corrected, n_used, latest_used, b_end = track(rows)
        for i, r in enumerate(rows):
            if latest_used[i] is not None and not latest_used[i] < r[0]:
                late += 1
        if late:
            raise SystemExit(f"STOP: a correction used an error not before its cycle at {st} {label} {h}z lead {n}")
        rows_total += len(rows)
        b_zero[label] += sum(k == 0 for k in n_used)
        c["drift"] = corrected
        end_b[(st, label, h, n)] = b_end
    print(f"tracker: {len(cells)} cells, {rows_total:,} rows, {time.time() - t:.1f} s; rows whose latest "
          f"error used is not before their cycle: {late}")
    print("rows corrected with b = 0 (no error yet), by fold: "
          + ", ".join(f"{k} {v}" for k, v in b_zero.items()) + f"; total {sum(b_zero.values())}")

    errs = s100.errors(cells, STATIONS, METHODS)
    rows = []
    for m in METHODS:
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

    print("\n" + "=" * 90)
    print("SUMMARY. BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C. Common row set (D89.5).")
    print("=" * 90)
    print("\nPer airport, pooled over folds, cycle hours and leads 3 to 24:")
    print(f"  {'airport':<7} {'n':>8} " + " ".join(f"{m:>9}" for m in METHODS))
    for st in STATIONS:
        print(f"  {st:<7} {s97.pooled(errs, 'baseline', st)[1]:>8,} "
              + " ".join(f"{s97.pooled(errs, m, st)[0]:>9.4f}" for m in METHODS))
    hl = {m: sum(s97.pooled(errs, m, st)[0] for st in STATIONS) / len(STATIONS) for m in METHODS}
    print(f"  {'HEADLINE':<16} " + " ".join(f"{hl[m]:>9.4f}" for m in METHODS))
    print("  full precision: " + ", ".join(f"{m} {hl[m]!r}" for m in METHODS))

    print("\nPer fold: each airport's MAE over the fold's rows, and the fold-level MAE (unweighted mean of six):")
    print(f"  {'fold':<8} {'method':<9} " + " ".join(f"{s:>7}" for s in STATIONS) + f" {'fold-level':>11}")
    for label, _, _ in FOLDS:
        for m in METHODS:
            vals = [s97.pooled(errs, m, st, folds=[label])[0] for st in STATIONS]
            print(f"  {label:<8} {m:<9} " + " ".join(f"{v:>7.4f}" for v in vals) + f" {sum(vals) / 6:>11.4f}")

    print("\nD89.6 test, drift against the baseline (incumbent minus challenger, over incumbent; "
          "ties keep the incumbent):")
    td = s100.d89_6(errs, "baseline", "drift")
    s100.print_test("drift against the baseline", td)
    outcome = ("drift passes: the curve becomes the baseline plus this correction, identically at every "
               "airport, cycle hour and lead" if td["pass"] else "drift does not pass: the baseline stays")
    print(f"\nD97.8 OUTCOME: {outcome} (a build choice, not a result)")

    print("\nDESCRIPTIVE (D97.9), not used by the rule.")
    print("\nMean error (observation minus forecast), degrees C, per airport and fold:")
    print(f"  {'airport':<7} {'fold':<8} " + " ".join(f"{m:>9}" for m in METHODS))
    for st in STATIONS:
        for label, _, _ in FOLDS:
            print(f"  {st:<7} {label:<8} " + " ".join(f"{pooled_me(errs, m, st, folds=[label]):>9.4f}"
                                                     for m in METHODS))
        print(f"  {st:<7} {'all':<8} " + " ".join(f"{pooled_me(errs, m, st):>9.4f}" for m in METHODS))

    print("\nb at the end of each fold (after all the fold's errors), over each airport's 88 cells, degrees C:")
    print(f"  {'airport':<7} {'fold':<8} {'mean':>8} {'min':>8} {'max':>8}")
    for st in STATIONS:
        for label, _, _ in FOLDS:
            v = [end_b[(st, label, h, n)] for h in CYCLE_HOURS for n in LEADS]
            print(f"  {st:<7} {label:<8} {sum(v) / len(v):>8.4f} {min(v):>8.4f} {max(v):>8.4f}")

    print("\nSix-airport mean MAE per lead (each airport pooled over folds and cycle hours):")
    print(f"  {'lead':>4} " + " ".join(f"{m:>9}" for m in METHODS))
    for n in LEADS:
        print(f"  {n:>4} " + " ".join(
            f"{sum(s97.pooled(errs, m, st, leads=[n])[0] for st in STATIONS) / 6:>9.4f}" for m in METHODS))
    print(f"\nend {now_utc()}; run time {time.time() - t_start:.1f} s")


# ------------------------------------------------------------------ --meta

def run_meta(args):
    if not SCORES_OUT.exists():
        raise SystemExit(f"STOP: {SCORES_OUT} does not exist")
    lines = [
        "session103_bias_drift_cv.meta.txt",
        f"written {now_utc()} by scripts/session103_bias_drift_cv.py --meta",
        "",
        "What the file is (BUILD-CHOICE SCORES, NOT RESULTS, SPEC 2.5):",
        "  session103_bias_drift_cv_scores.csv: per method (raw_gfs, baseline, drift), airport, fold, cycle",
        "    hour and lead 3 to 24: n, MAE and mean error (obs_tmpc minus forecast), full precision.",
        "    Columns are session 100's; model repeats the method's name. Common row set (D89.5).",
        "  baseline: D88.4, one model per airport, fold, cycle hour and lead (1,584 fits).",
        f"  drift: the baseline plus b, b = (1 - w) x b + w x e after each baseline error e, w = {W} (D97.4),",
        "    one tracker per airport, fold, cycle hour and lead, b = 0 at each fold's T0, errors used only",
        "    when their valid time is before the cycle (D97.5 to D97.7).",
        "",
        "Rules: DECISIONS D97 (the challenger and its rule), D89.3 (folds), D89.5 (metric), D89.6 (rule).",
        "",
        "Inputs and their SHA-256:",
    ]
    for st in STATIONS:
        name, _ = s97.TABLES[st]
        lines.append(f"  MLwx-stagec/{name} {sha256_file(s97.STAGEC_DIR / name)}")
    for p in (s100.S97_SCORES, S100_SCRIPT, s100.S97_SCRIPT, s97.RECORD_SCRIPT):
        lines.append(f"  {p.relative_to(ROOT)} {sha256_file(p)}")
    lines += [
        "",
        f"Script: scripts/session103_bias_drift_cv.py {sha256_file(SCRIPT)}",
        "",
        "Outputs and their SHA-256:",
        f"  {SCORES_OUT.relative_to(ROOT)} {sha256_file(SCORES_OUT)}",
        "",
        f"LGB_PARAMS as passed (from session 97, which takes them from scripts/session62_reserved_confirm.py): "
        f"{LGB_PARAMS}",
        f"G15 column order (same source): {s100.G15}",
        f"w: {W}",
        "Fit counts: --gate baseline 1,584; --score baseline 1,584. drift fits no model. No model saved.",
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
    g.add_argument("--check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    g.add_argument("--meta", action="store_true")
    ap.add_argument("--run-times", default="not given", help="--meta only: the run times the runs printed")
    args = ap.parse_args()
    if args.check:
        run_check(args)
    elif args.gate:
        run_gate(args)
    elif args.score:
        run_score(args)
    elif args.meta:
        run_meta(args)


if __name__ == "__main__":
    main()
