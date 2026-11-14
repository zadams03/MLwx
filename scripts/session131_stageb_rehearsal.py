"""Session 131: a rehearsal of session 86's --build path on a spent fortnight (DECISIONS D125.8; register rows
SB09, SB08).

`scripts/session86_forward_build.py --build` (frozen) has never run its own path: the observation mode
'range' (one IEM request per airport for the whole window) and the per-cycle v17 guard; its gate used the
'gate' mode (F128). This script imports session 86 unchanged and calls its `build_rows` exactly as
`run_build` does (mode 'range', a first v17 cycle, session 86's default 4 workers), on a short spent window
at the six airports: 2025-06-01 to 2025-06-14. It writes the build's outputs with session 86's own
`write_outputs` into a folder given on the command line (never session 86's own output paths, never under
data/), then compares every rebuilt row with the committed training set
(`data/processed/session81_training_set.csv`) on the shared columns, by exact equality as F128 did, and runs
`session131_stageb_build_check.py` on the drop log and manifest.

Two settings differ from --build, both stricter, and are printed: the validity limit is session 86's
GATE_LIMIT (nothing valid on or after 2026-08-01 can be requested or read) rather than FORWARD_LIMIT; and the
first v17 cycle passed to the guard is REHEARSAL_V17, the day after the window, so the guard runs on every
station-day and must not fire.

NETWORK: NOAA's GFS archive on AWS (GRIB messages by byte range, nothing kept on disk, D47) and IEM; valid
times 2025-05-31 to 2025-06-14 only.

Usage:
  python3 scripts/session131_stageb_rehearsal.py --check            # offline: inputs only
  python3 scripts/session131_stageb_rehearsal.py --run OUT_DIR      # OUT_DIR: an empty folder outside data/
--run writes two small files, once, under data/processed/session131_rehearsal/: per-airport counts and a
meta file. No forecast, observation or error value is written there or printed.
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")   # session 86 loads without its restart (D93.3)

import argparse  # noqa: E402
import contextlib  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import resource  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


S86_SCRIPT_SHA256 = "da2ff50c8baa9a7bcbe1c5a6d4787d02e042de250143d3b067d10fcd27594125"   # D116.4
if sha256_file(HERE / "session86_forward_build.py") != S86_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session86_forward_build.py's SHA-256 is not the recorded one (D116.4)")

import session86_forward_build as s86  # noqa: E402
import session91_grib_pull as p91  # noqa: E402
import session131_stageb_build_check as bc  # noqa: E402

FIRST_DAY = dt.date(2025, 6, 1)
LAST_DAY = dt.date(2025, 6, 14)
REHEARSAL_V17 = dt.datetime(2025, 6, 15, 0)        # the day after the window: the guard runs and must not fire
WORKERS = 4                                         # session 86's --workers default
RESULT_DIR = ROOT / "data" / "processed" / "session131_rehearsal"
RESULT_CSV = RESULT_DIR / "rehearsal_counts.csv"
RESULT_META = RESULT_DIR / "rehearsal_counts.csv.meta.txt"
FEATURE_COLS = s86.G15 + ["temperature_grib_c"]
COUNT_COLS = ["airport", "expected", "rows", "dropped", "cells_compared", "cells_equal", "obs_compared",
              "obs_equal", "prev_obs_compared", "prev_obs_equal"]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def targets_of(airports):
    days = [FIRST_DAY + dt.timedelta(days=k) for k in range((LAST_DAY - FIRST_DAY).days + 1)]
    return [(st, d) for st in airports for d in days]


def inputs(print_=print):
    """The airports, the targets and the committed rows; stops if a committed row is missing."""
    have = sha256_file(s86.TRAINING_SET)
    if have != p91.TRAINING_SET_SHA256:
        raise SystemExit(f"STOP: the training set's SHA-256 {have} is not F122.3's")
    airports = s86.load_airports()
    targets = targets_of(airports)
    training = s86.read_training_set()
    missing = [k for k in targets if k not in training]
    print_(f"window {FIRST_DAY}..{LAST_DAY}, {len(airports)} airports, {len(targets)} station-days; training set "
           f"SHA-256 equal to F122.3; station-days with no committed row: {len(missing)}")
    if missing:
        raise SystemExit(f"STOP: no committed row for {missing[:10]}: report, and use the nearest whole "
                         "fortnight before 2025-07-31 that has every row (session 131, Step 7)")
    return airports, targets, training


def strict_compare(airports, targets, training, rebuilt):
    """Exact equality on every shared column, with no exception for the pairing rule. Returns per-airport
    counts and the differences [(station, date, column, committed, rebuilt)]."""
    counts = {st: dict.fromkeys(COUNT_COLS[1:], 0) for st in airports}
    diffs = []
    for st, d in targets:
        c = counts[st]
        c["expected"] += 1
        com, reb = training[(st, d)], rebuilt.get((st, d))
        if reb is None:
            c["dropped"] += 1
            continue
        c["rows"] += 1
        if int(com["target_hour"]) != reb["target_hour"]:
            diffs.append((st, d, "target_hour", com["target_hour"], reb["target_hour"]))
        for col in FEATURE_COLS:
            c["cells_compared"] += 1
            if float(com[col]) == reb[col]:
                c["cells_equal"] += 1
            else:
                diffs.append((st, d, col, com[col], repr(reb[col])))
        c["obs_compared"] += 1
        if float(com["obs_c"]) == reb["obs_c"]:
            c["obs_equal"] += 1
        else:
            diffs.append((st, d, "obs_c", com["obs_c"], repr(reb["obs_c"])))
        prev = training.get((st, d - dt.timedelta(days=1)))
        if prev is not None:
            c["prev_obs_compared"] += 1
            if reb["prev_obs_c"] is not None and float(prev["obs_c"]) == reb["prev_obs_c"]:
                c["prev_obs_equal"] += 1
            else:
                diffs.append((st, d, "prev_obs_c", prev["obs_c"], repr(reb["prev_obs_c"])))
    return counts, diffs


def write_once(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", newline="") as f:
        f.write(text)


def run(out_dir):
    out_dir = Path(out_dir).resolve()
    if not out_dir.is_dir() or any(out_dir.iterdir()):
        raise SystemExit(f"STOP: {out_dir} must be an existing, empty folder")
    if out_dir == ROOT or ROOT in out_dir.parents:
        raise SystemExit("STOP: the output folder must be outside the repository")
    if RESULT_CSV.exists() or RESULT_META.exists():
        raise SystemExit(f"STOP: {RESULT_DIR} already holds a result; not overwriting")
    airports, targets, training = inputs()
    print(f"session 86 SHA-256 {S86_SCRIPT_SHA256} (frozen); mode 'range'; validity limit {s86.GATE_LIMIT}; "
          f"first v17 cycle for the guard {REHEARSAL_V17}; workers {WORKERS}")
    started, t0 = now_utc(), time.perf_counter()
    built = s86.build_rows(airports, targets, s86.GATE_LIMIT, WORKERS, "range", REHEARSAL_V17)
    t_build = time.perf_counter() - t0
    dirs = {"rows": out_dir / "rows.csv", "rows_meta": out_dir / "rows.csv.meta.txt",
            "manifest": out_dir / "diag" / "periodA_grib_manifest.csv",
            "drops": out_dir / "diag" / "periodA_drop_log.csv", "iem": out_dir / "iem"}
    s86.write_outputs(built, dirs, "session 131 rehearsal of --build's path on 2025-06-01..2025-06-14 (spent)")
    rebuilt = {(r["station"], dt.date.fromisoformat(r["target_date"])): r for r in built["rows"]}
    counts, diffs = strict_compare(airports, targets, training, rebuilt)
    committed = {k: training[k] for k in targets}
    s86_out = io.StringIO()
    with contextlib.redirect_stdout(s86_out):
        s86.print_counts(built, airports, "rehearsal")
        s86_fail = s86.compare(airports, targets, committed, rebuilt, built, training)
    (out_dir / "session86_compare.txt").write_text(s86_out.getvalue())
    check = bc.check(dirs["drops"], dirs["manifest"])
    total = time.perf_counter() - t0
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss          # bytes on macOS, KiB on Linux
    peak_bytes = peak if sys.platform == "darwin" else peak * 1024
    req = s86.REQUEST_LOG
    kinds = {}
    for _, kind, _, _, n in req:
        k = kinds.setdefault(kind, [0, 0])
        k[0] += 1
        k[1] += n
    ok_msgs = [m for m in built["manifest"] if m[16] == "OK"]
    tot = {k: sum(c[k] for c in counts.values()) for k in COUNT_COLS[1:]}
    verdict = "PASS" if not diffs and s86_fail == 0 and check["verdict"] == "PASS" and tot["dropped"] == 0 else "FAIL"

    print(f"pull {built['started']} to {built['ended']}; build {t_build:.1f} s; total {total:.1f} s; "
          f"peak memory {peak_bytes / 1e9:.2f} GB")
    print(f"requests {len(req)}: " + ", ".join(f"{k} {v[0]} ({v[1]:,} bytes)" for k, v in sorted(kinds.items()))
          + f"; total bytes {sum(v[1] for v in kinds.values()):,}")
    print(f"GRIB messages {len(built['manifest'])}, OK {len(ok_msgs)}; IEM requests {len(built['raw_iem'])}")
    for st, c in counts.items():
        print(f"  {st:5s} rows {c['rows']} of {c['expected']}; feature cells equal {c['cells_equal']} of "
              f"{c['cells_compared']}; obs {c['obs_equal']} of {c['obs_compared']}; previous-day obs "
              f"{c['prev_obs_equal']} of {c['prev_obs_compared']}")
    print(f"strict differences: {len(diffs)}; session 86's compare failures: {s86_fail} "
          f"(its pairing-only differences are in session86_compare.txt)")
    for st, d, col, cv, rv in diffs[:10]:
        print(f"  DIFFERENCE {st} {d} {col}: committed {cv}, rebuilt {rv}")
    print(f"build check: {check['verdict']} (drops {check['drops']}; fetch {len(check['by_class']['fetch'])}, "
          f"absent {len(check['by_class']['absent'])}, data {len(check['by_class']['data'])})")
    print(f"REHEARSAL: {verdict}")

    rows = [[st] + [c[k] for k in COUNT_COLS[1:]] for st, c in counts.items()]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(COUNT_COLS)
    w.writerows(rows)
    write_once(RESULT_CSV, buf.getvalue())
    meta = [
        "Session 131, Step 7: a rehearsal of session 86's --build path on spent data (D125.8; SB09, SB08).",
        "Counts only: no forecast, observation or error value is in this file or its CSV.",
        f"session 86: scripts/session86_forward_build.py, SHA-256 {S86_SCRIPT_SHA256}, imported unchanged",
        f"called: build_rows(six airports, {len(targets)} station-days, GATE_LIMIT {s86.GATE_LIMIT}, "
        f"workers {WORKERS}, 'range', first v17 cycle {REHEARSAL_V17}); write_outputs into a temporary folder",
        f"window: {FIRST_DAY} to {LAST_DAY}",
        f"compared with: data/processed/session81_training_set.csv, SHA-256 {p91.TRAINING_SET_SHA256}",
        f"run started (UTC): {started}; pull {built['started']} to {built['ended']}",
        f"run time: build {t_build:.1f} s, total {total:.1f} s; peak memory (ru_maxrss) {peak_bytes:,} bytes",
        f"requests: {len(req)}; " + "; ".join(f"{k} {v[0]} requests, {v[1]:,} bytes" for k, v in sorted(kinds.items())),
        f"GRIB messages: {len(built['manifest'])} requested, {len(ok_msgs)} OK; IEM requests {len(built['raw_iem'])}",
        f"totals: " + ", ".join(f"{k} {tot[k]}" for k in COUNT_COLS[1:]),
        f"strict differences (every shared cell, exact): {len(diffs)}",
        f"session 86's compare (pairing-only observation differences not counted): failures {s86_fail}",
        f"build check (scripts/session131_stageb_build_check.py): {check['verdict']}; drop log rows {check['drops']}",
        f"verdict: {verdict}",
        f"python {sys.version.split()[0]}",
    ]
    write_once(RESULT_META, "\n".join(meta) + "\n")
    print(f"wrote {RESULT_CSV.relative_to(ROOT)} and {RESULT_META.relative_to(ROOT)}")
    return 0 if verdict == "PASS" else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="offline: the inputs and the window's committed rows")
    g.add_argument("--run", metavar="OUT_DIR", help="network: the rehearsal, outputs into OUT_DIR")
    a = ap.parse_args(argv)
    try:
        if a.check:
            inputs()
            print("CHECK: PASS (offline; nothing fetched or written)")
            return 0
        return run(a.run)
    except s86.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
