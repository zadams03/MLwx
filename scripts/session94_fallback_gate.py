"""Session 94: the gate for the whole-file fallback (DECISIONS D86.3).

Network: only noaa-gfs-bdp-pds (.idx files, byte ranges and whole-file GETs for
the five files below). Every downloaded byte is held in memory only. The one
temporary directory (mktemp) holds only the committed (HEAD) copy of the pull
script, and is deleted at the end.

Step 4, the normal path is unchanged. The HEAD version of
scripts/session91_grib_pull.py (via git show) and the edited version each run
their normal entry point, process_file, on three healthy files: 2022-11-29T18
f000, f001 and f010. Pass rule: the manifest rows and the points rows, written
as the pull's run_chunk writes them, are string-equal, and no file falls back.

Step 5.1, the fallback on healthy files (forced; this gate only). The edited
script's process_whole_file runs on 2022-11-29T18 f000 and f001. Pass rule:
for every planned field, exactly one walked message passes the check, its
SHA-256 equals the SHA-256 of the bytes at the field's .idx range, and the
points rows equal Step 4's.

Step 5.2, the fallback on broken files (F135). The edited script's normal
entry point, process_file, runs on 2022-11-29T18 f002 and 2022-11-30T06 f024.
Pass rule: each falls back by itself, its walk ends at the file's last byte,
and every planned field has exactly one passing message and the status
"ok (whole file)". No value is printed.

A failure is reported in full and the run stops. Nothing under data/ is
written. Run once:  python scripts/session94_fallback_gate.py
"""

import csv
import datetime as dt
import hashlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
PULL = ROOT / "scripts" / "session91_grib_pull.py"
POSITIONS = ROOT / "data" / "processed" / "session91_pull_airports.csv"
HEAD_SHA = "72c263b24b06d2e6ab8d1a9c9be3444ddc3ee1c4a8b2cf445556cbedddd1652e"   # F133, F134, F135

CYCLE_A = dt.datetime(2022, 11, 29, 18)
STEP4_FILES = [(CYCLE_A, 0), (CYCLE_A, 1), (CYCLE_A, 10)]
STEP51_FILES = [(CYCLE_A, 0), (CYCLE_A, 1)]
STEP52_FILES = [(CYCLE_A, 2), (dt.datetime(2022, 11, 30, 6), 24)]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def as_rows(mod, results, positions):
    """Manifest and points rows as strings, built and written exactly as the
    pull's run_chunk builds and writes them (csv module, '\\n' line ends)."""
    man_rows, point_rows = [], []
    for (c, fh), (m, vals, _) in results:
        man_rows += m
        valid = c + dt.timedelta(hours=fh)
        for k, p in enumerate(positions):
            row = [mod.iso(c), fh, mod.iso(valid), p["icao"]]
            for f_ in mod.FIELD_NAMES:
                v = vals.get(f_)
                row += ([repr(x) for x in v[4 * k:4 * k + 4]] if v is not None else ["", "", "", ""])
            point_rows.append(row)

    def text(rows):
        buf = io.StringIO()
        csv.writer(buf, lineterminator="\n").writerows(rows)
        return buf.getvalue().splitlines()
    return text(man_rows), text(point_rows)


def fetch_stats(f):
    return (f"requests {f.requests}; bytes {f.bytes} (total {sum(f.bytes.values()):,}); retries {f.retries}; "
            f"HTTP 404 {f.not_found}")


def stop(msg):
    print(f"\nGATE STOPPED: {msg}")
    return 1


def main():
    t0 = time.time()
    print(f"SESSION 94 fallback gate; started {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ}")
    tmp = Path(tempfile.mkdtemp(prefix="session94_gate_"))
    print(f"temporary directory: {tmp}")
    try:
        return run(tmp, t0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"temporary directory deleted: {not tmp.exists()}")
        print(f"seconds: {time.time() - t0:,.0f}")


def run(tmp, t0):
    head_path = tmp / "session91_grib_pull_head.py"
    head_path.write_bytes(subprocess.run(["git", "-C", str(ROOT), "show", "HEAD:scripts/session91_grib_pull.py"],
                                         check=True, capture_output=True).stdout)
    head_sha = sha256_bytes(head_path.read_bytes())
    edit_sha = sha256_bytes(PULL.read_bytes())
    print(f"HEAD script SHA-256 {head_sha} (F133/F134/F135 {HEAD_SHA}): equal {head_sha == HEAD_SHA}")
    print(f"edited script SHA-256 {edit_sha}")
    print(f"positions file SHA-256 {sha256_bytes(POSITIONS.read_bytes())}")
    if head_sha != HEAD_SHA:
        return stop("the HEAD script is not the one F133 to F135 record")
    head = load("pull_head", head_path)
    new = load("pull_edited", PULL)
    print(f"packages: {new.versions()}")
    # Both read the committed positions file (the HEAD copy's own ROOT is the temporary directory).
    pos_h, geom_h = head.read_positions(POSITIONS)
    pos_n, geom_n = new.read_positions(POSITIONS)

    # ------------------------------------------------------------------ Step 4
    print("\n=== Step 4: the normal path is unchanged (HEAD vs edited, process_file) ===")
    out = {}
    for label, mod, pos, geom in (("HEAD", head, pos_h, geom_h), ("edited", new, pos_n, geom_n)):
        f = mod.Fetcher()
        res = []
        for c, fh in STEP4_FILES:
            try:
                res.append(((c, fh), mod.process_file(f, c, fh, pos, geom)))
            except Exception as e:  # noqa: BLE001
                return stop(f"{label} process_file {mod.iso(c)} f{fh:03d} raised {type(e).__name__}: {e}")
        man, pts = as_rows(mod, res, pos)
        fallbacks = len(getattr(f, "whole", []))
        statuses = {}
        for (_, (m, _, _)) in res:
            for r in m:
                statuses[r[6]] = statuses.get(r[6], 0) + 1
        out[label] = (man, pts, fallbacks)
        print(f"{label:6s}: {len(man)} manifest rows, {len(pts)} points rows; statuses {statuses}; "
              f"files fallen back {fallbacks}; {fetch_stats(f)}")
    man_eq = out["HEAD"][0] == out["edited"][0]
    pts_eq = out["HEAD"][1] == out["edited"][1]
    no_fb = out["edited"][2] == 0
    print(f"manifest rows string-equal: {man_eq}; points rows string-equal: {pts_eq}; no file fell back: {no_fb}")
    if not (man_eq and pts_eq and no_fb):
        for i, (a, b) in enumerate(zip(out["HEAD"][0], out["edited"][0])):
            if a != b:
                print(f"  manifest row {i + 1} differs:\n    HEAD   {a}\n    edited {b}")
        for i, (a, b) in enumerate(zip(out["HEAD"][1], out["edited"][1])):
            if a != b:
                print(f"  points row {i + 1} differs:\n    HEAD   {a}\n    edited {b}")
        return stop("Step 4 did not pass")
    print("STEP 4 PASSED")
    step4_pts = out["edited"][1]
    n_air = len(pos_n)

    # ------------------------------------------------------------------ Step 5.1
    print("\n=== Step 5.1: the fallback forced on healthy files (gate only) ===")
    f = new.Fetcher()
    ok51 = True
    res51 = []
    for c, fh in STEP51_FILES:
        url = new.file_url(c, fh)
        rows = new.parse_idx(f.get(url + ".idx", "idx").decode("ascii"))
        idx_info = {}
        for name, var, level, kind, ident in new.FIELDS:
            step = new.selector(kind, fh)
            if step is None:
                continue
            rng, exp, _ = new.find_range(rows, var, level, step, c)
            body = f.get(url, "message", rng, exp)
            idx_info[name] = (rng, exp, sha256_bytes(body))
            del body
        man, vals = new.process_whole_file(f, c, fh, pos_n, geom_n, "forced by the session 94 gate (Step 5.1)")
        res51.append(((c, fh), (man, vals, [])))
        rec = [r for r in f.whole if r["cycle"] == new.iso(c) and r["fh"] == fh][-1]
        print(f"\n{new.iso(c)} f{fh:03d}: whole file {rec['bytes']:,} B; .idx lines {len(rows)}; messages walked "
              f"{rec['walked']}; walk ends at the last byte {rec['ends_at_last_byte']}; walk error "
              f"{rec['walk_error'] or 'none'}")
        print(f"  {'field':7s} {'.idx range':>23s} {'walk offset-end':>23s} {'passing':>7s} {'status':16s} "
              f"{'SHA-256 equal':>13s}  SHA-256 (walk)")
        status = {r[2]: r[6] for r in man}
        for name, var, level, kind, ident in new.FIELDS:
            if name not in idx_info:
                print(f"  {name:7s} {'-':>23s} {'-':>23s} {'-':>7s} {status[name]:16s}")
                ok51 &= status[name] == "absent by design"
                continue
            rng, exp, isha = idx_info[name]
            sel = rec["selected"].get(name)
            k = rec["passes"][name]
            walk_rng = f"{sel['offset']}-{sel['offset'] + sel['length'] - 1}" if sel else "-"
            eq = sel is not None and sel["sha256"] == isha
            good = k == 1 and eq and walk_rng == rng and status[name] == new.STATUS_WHOLE
            ok51 &= good
            print(f"  {name:7s} {rng:>23s} {walk_rng:>23s} {k:>7d} {status[name]:16s} {str(eq):>13s}  "
                  f"{sel['sha256'] if sel else '-'}" + ("" if good else "   <-- FAIL"))
    _, pts51 = as_rows(new, res51, pos_n)
    want = step4_pts[:len(STEP51_FILES) * n_air]
    pts_eq = pts51 == want
    print(f"\npoints rows of the forced fallback string-equal to Step 4's (same {len(want)} rows): {pts_eq}")
    print(fetch_stats(f))
    if not (ok51 and pts_eq):
        for i, (a, b) in enumerate(zip(want, pts51)):
            if a != b:
                print(f"  points row {i + 1} differs:\n    Step 4   {a}\n    fallback {b}")
        return stop("Step 5.1 did not pass")
    print("STEP 5.1 PASSED")

    # ------------------------------------------------------------------ Step 5.2
    print("\n=== Step 5.2: the broken files, through the edited pull's normal entry point (process_file) ===")
    f = new.Fetcher()
    ok52 = True
    for c, fh in STEP52_FILES:
        t1 = time.time()
        man, vals, _ = new.process_file(f, c, fh, pos_n, geom_n)
        recs = [r for r in f.whole if r["cycle"] == new.iso(c) and r["fh"] == fh]
        fell = len(recs) == 1
        print(f"\n{new.iso(c)} f{fh:03d}: fell back by itself {fell} ({time.time() - t1:,.0f} s)")
        if not fell:
            ok52 = False
            print("  statuses: " + ", ".join(f"{r[2]} {r[6]}" for r in man))
            continue
        rec = recs[0]
        print(f"  trigger: {rec['trigger']}")
        print(f"  whole file {rec['bytes']:,} B; messages walked {rec['walked']}; walk ends at the last byte "
              f"{rec['ends_at_last_byte']}; walk error {rec['walk_error'] or 'none'}")
        print(f"  {'field':7s} {'passing':>7s} {'status':16s} {'range in file':>23s}")
        ok52 &= rec["ends_at_last_byte"]
        for r in man:
            name, st = r[2], r[6]
            k = rec["passes"].get(name)
            if k is None:
                good = st == "absent by design"
            else:
                good = k == 1 and st == new.STATUS_WHOLE and name in vals
            ok52 &= good
            print(f"  {name:7s} {('-' if k is None else str(k)):>7s} {st:16s} {r[4] or '-':>23s}"
                  + ("" if good else "   <-- FAIL: " + r[9]))
    print(f"\n{fetch_stats(f)}")
    print("whole-file records: " + "; ".join(f"{r['cycle']} f{r['fh']:03d} {r['bytes']:,} B" for r in f.whole))
    if not ok52:
        return stop("Step 5.2 did not pass")
    print("STEP 5.2 PASSED")
    print("\nALL GATE STEPS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
