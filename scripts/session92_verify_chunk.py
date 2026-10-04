"""Session 92: verify one month of the stage C GRIB pull (DECISIONS D84.4).

It reads a finished chunk's three files (points, manifest, meta) from --dir
and checks them against the session 91 plan. The plan, the field list, the
column layout and the absent-by-design rule are imported from
scripts/session91_grib_pull.py, the pull itself, so they cannot drift apart.
Nothing is typed in. Standard library only, plus what that script imports.

Usage:
  python scripts/session92_verify_chunk.py --dir DIR --month YYYY-MM --hours A-B
      The D84.4 checks. Exit status 0 only if every check passes. This is the
      form the workflow runs before any upload.
  ... --ranges
      Local use only. Also prints, per field, the count of values, the minimum
      and maximum and the count outside broad bounds, and checks that every
      value cell reads back with float and repr to the identical string
      (D83.5(c)). Never a fail rule: the exit status comes from the checks.
  ... --gate
      Local use only, and only this (the checks are not run). Rebuilds the
      record's seven GRIB-derived columns at the development airports whose
      lead lies inside --hours, for every target date whose cycle is in the
      month, and compares them with data/processed/session81_training_set.csv,
      exact equality. Uses session 91's gate arithmetic (imported), so the
      operation order is F133.7's.

The D84.4 fail rules, one named check each (expected and found are printed):
  layout          the two files' headers are session 91's columns
  cycles          the cycles in both files are the plan's
  files           the (cycle, forecast hour) pairs in both files are the plan's
  manifest rows   one row per file and field
  messages        rows that are not absent by design: the plan's message count
  points rows     one row per file and airport, airports as the positions file
  statuses        every status is one of session 91's four
  check failed    no message is "check failed"
  absent by design  exactly DSWRF, TMAX and TMIN at f000, and nothing else
  duplicate keys  no (cycle, hour, field) or (cycle, hour, airport) twice
  ok values       an ok message has all its cells filled and finite
  non-ok values   a non-ok message has no cell filled
  meta sha256     the meta's two data-file SHA-256 values equal the files'
"idx missing" messages do not fail the month: their count is printed.
The two value checks together reconcile the files: a points row's cells for
a field are filled exactly when that cycle, hour and field's status is ok.

No forecast value is printed by the checks, only counts and keys. --ranges
prints each field's minimum and maximum; --gate prints values only for a
mismatch.
"""

import argparse
import csv
import datetime as dt
import gzip
import math
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

import session91_grib_pull as p91  # noqa: E402

ROOT = p91.ROOT
TRAINING_SET = p91.TRAINING_SET

# --ranges: broad physical bounds (session 92 prompt, Step 3.5). Units as GRIB
# gives them: K, %, m/s, Pa, W/m2.
BOUNDS = {"t2m": (150.0, 350.0), "d2m": (150.0, 350.0), "t850": (150.0, 350.0),
          "tmax2m": (150.0, 350.0), "tmin2m": (150.0, 350.0), "tcdc": (0.0, 100.0),
          "u10": (-100.0, 100.0), "v10": (-100.0, 100.0), "prmsl": (85000.0, 110000.0),
          "dswrf": (0.0, 1500.0)}

# --gate: the key columns and the seven compared columns, read by name. No
# other column of the training set is kept (no observation or target column).
GATE_KEY_COLS = ["station", "target_date"]


def read_gz_csv(path):
    with gzip.open(path, "rt", newline="") as f:
        r = csv.reader(f)
        header = next(r)
        return header, list(r)


def the_files(d, name):
    return (d / f"gfs_points_{name}.csv.gz", d / f"manifest_{name}.csv.gz", d / f"chunk_{name}.meta.txt")


def expected(month, hours):
    """The session 91 plan for one month: everything the files must hold."""
    y, m = p91.parse_month(month)
    plan = p91.plan_chunk(p91.month_cycles(y, m), hours)
    units = [(p91.iso(c), fh) for c, fhs in plan for fh in fhs]
    positions, _ = p91.read_positions()
    icaos = [p["icao"] for p in positions]
    absent = {(c, fh, f[0]) for c, fh in units for f in p91.FIELDS if p91.selector(f[3], fh) is None}
    return {
        "cycles": {p91.iso(c) for c, _ in plan},
        "units": set(units),
        "n_units": len(units),
        "manifest_keys": {(c, fh, f) for c, fh in units for f in p91.FIELD_NAMES},
        "messages": sum(p91.expected_messages(fh) for _, fh in units),
        "absent": absent,
        "icaos": icaos,
        "points_keys": {(c, fh, i) for c, fh in units for i in icaos},
    }


def run_checks(args, hours):
    d = Path(args.dir)
    pts_path, man_path, meta_path = the_files(d, args.month)
    print(f"SESSION 92 verify chunk {args.month}, hours {hours[0]}-{hours[1]}, in {d}")
    for p in (pts_path, man_path, meta_path):
        if not p.exists():
            print(f"STOP: {p.name} is missing")
            return 1
    exp = expected(args.month, hours)
    print(f"plan (session 91): {len(exp['cycles'])} cycles, {exp['n_units']} files, {exp['messages']} messages, "
          f"{len(exp['absent'])} absent by design, {len(exp['manifest_keys'])} manifest rows, "
          f"{len(exp['points_keys'])} points rows ({exp['n_units']} files x {len(exp['icaos'])} airports)")

    p_head, p_rows = read_gz_csv(pts_path)
    m_head, m_rows = read_gz_csv(man_path)
    results = []

    def check(name, expect, found, ok):
        results.append((name, ok))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:17s} expected {expect}; found {found}")

    print("\nchecks (D84.4):")
    lay_ok = p_head == p91.POINT_COLS and m_head == p91.MAN_COLS
    check("layout", "session 91's points and manifest columns",
          f"points header equal {p_head == p91.POINT_COLS}, manifest header equal {m_head == p91.MAN_COLS}", lay_ok)
    if not lay_ok:
        print("STOP: the layout differs, so no other check can be read")
        print("RESULT: FAIL")
        return 1
    pc = {c: i for i, c in enumerate(p_head)}
    mc = {c: i for i, c in enumerate(m_head)}

    def mkey(r):
        return (r[mc["cycle_utc"]], int(r[mc["fhour"]]), r[mc["field"]])

    def pkey(r):
        return (r[pc["cycle_utc"]], int(r[pc["fhour"]]), r[pc["icao"]])

    m_keys = [mkey(r) for r in m_rows]
    p_keys = [pkey(r) for r in p_rows]
    m_set, p_set = set(m_keys), set(p_keys)

    cyc_m, cyc_p = {k[0] for k in m_set}, {k[0] for k in p_set}
    check("cycles", f"{len(exp['cycles'])}", f"manifest {len(cyc_m)}, points {len(cyc_p)}; both the plan's cycles "
          f"{cyc_m == exp['cycles'] and cyc_p == exp['cycles']}", cyc_m == exp["cycles"] and cyc_p == exp["cycles"])
    un_m, un_p = {k[:2] for k in m_set}, {k[:2] for k in p_set}
    check("files", f"{exp['n_units']}", f"manifest {len(un_m)}, points {len(un_p)}; both the plan's files "
          f"{un_m == exp['units'] and un_p == exp['units']}", un_m == exp["units"] and un_p == exp["units"])
    check("manifest rows", f"{len(exp['manifest_keys'])}", f"{len(m_rows)}; keys the plan's {m_set == exp['manifest_keys']}",
          len(m_rows) == len(exp["manifest_keys"]) and m_set == exp["manifest_keys"])
    status = {}
    for r, k in zip(m_rows, m_keys):
        status.setdefault(k, []).append(r[mc["status"]])
    n_msg = sum(1 for r in m_rows if r[mc["status"]] != "absent by design")
    check("messages", f"{exp['messages']}", f"{n_msg}", n_msg == exp["messages"])
    check("points rows", f"{len(exp['points_keys'])}", f"{len(p_rows)}; keys the plan's {p_set == exp['points_keys']}",
          len(p_rows) == len(exp["points_keys"]) and p_set == exp["points_keys"])
    unknown = sorted({r[mc["status"]] for r in m_rows} - set(p91.STATUSES))
    check("statuses", f"only {p91.STATUSES}", f"unknown {unknown or 'none'}", not unknown)
    n_cf = sum(1 for r in m_rows if r[mc["status"]] == "check failed")
    check("check failed", "0", f"{n_cf}", n_cf == 0)
    absent_found = {k for r, k in zip(m_rows, m_keys) if r[mc["status"]] == "absent by design"}
    extra, lacking = absent_found - exp["absent"], exp["absent"] - absent_found
    check("absent by design", f"{len(exp['absent'])} (dswrf, tmax2m, tmin2m at f000 only)",
          f"{len(absent_found)}; not expected {len(extra)}, expected but not absent {len(lacking)}",
          not extra and not lacking)
    dup_m = len(m_keys) - len(m_set)
    dup_p = len(p_keys) - len(p_set)
    check("duplicate keys", "0", f"manifest {dup_m}, points {dup_p}", dup_m == 0 and dup_p == 0)

    # The two value checks, which reconcile the points file with the manifest.
    ok_bad, nonok_bad, ok_cells, nonok_cells, no_status = [], [], 0, 0, 0
    for r, k in zip(p_rows, p_keys):
        c, fh, icao = k
        for f in p91.FIELD_NAMES:
            sts = status.get((c, fh, f))
            if not sts:
                no_status += 1
                continue
            cells = [r[pc[f"{f}_{j}"]] for j in (1, 2, 3, 4)]
            if sts == ["ok"]:
                ok_cells += 4
                for s in cells:
                    try:
                        good = s != "" and math.isfinite(float(s))
                    except ValueError:
                        good = False
                    if not good:
                        ok_bad.append((c, fh, icao, f))
            else:
                nonok_cells += 4
                if any(s != "" for s in cells):
                    nonok_bad.append((c, fh, icao, f))
    check("ok values", f"{ok_cells} cells filled and finite",
          f"{len(ok_bad)} cells empty, non-finite or unreadable; {no_status} field cells with no manifest row",
          not ok_bad and no_status == 0)
    check("non-ok values", f"{nonok_cells} cells empty", f"{len(nonok_bad)} field groups with a cell filled",
          not nonok_bad)
    for label, bad in (("ok values", ok_bad), ("non-ok values", nonok_bad)):
        for b in bad[:10]:
            print(f"      {label} at cycle {b[0]} f{b[1]:03d} {b[2]} {b[3]}")
        if len(bad) > 10:
            print(f"      ... and {len(bad) - 10} more")

    meta = meta_path.read_text()
    found_sha, meta_ok = [], True
    for p in (pts_path, man_path):
        m = re.search(rf"^{re.escape(p.name)} sha256 ([0-9a-f]{{64}}) ", meta, re.M)
        have = p91.sha256_file(p)
        same = m is not None and m.group(1) == have
        meta_ok &= same
        found_sha.append(f"{p.name} {'equal' if same else 'NOT EQUAL' if m else 'NOT IN META'}")
    check("meta sha256", "both data files' SHA-256 as in the meta", "; ".join(found_sha), meta_ok)

    n_idx = sum(1 for r in m_rows if r[mc["status"]] == "idx missing")
    print(f"\n\"idx missing\" messages (published, left empty, not a fail): {n_idx}")
    for s in p91.STATUSES:
        print(f"  status {s!r}: {sum(1 for r in m_rows if r[mc['status']] == s)}")
    n_fail = sum(1 for _, ok in results if not ok)
    print(f"\nchecks passed {len(results) - n_fail} of {len(results)}"
          + ("" if not n_fail else "; failed: " + ", ".join(n for n, ok in results if not ok)))
    print("RESULT: PASS" if not n_fail else "RESULT: FAIL")

    if args.ranges:
        print_ranges(p_head, p_rows)
    return 0 if not n_fail else 1


def print_ranges(p_head, p_rows):
    """Local use only; never a fail rule."""
    pc = {c: i for i, c in enumerate(p_head)}
    print("\nranges (local use only, not a fail rule). Units as GRIB gives them.")
    print(f"  {'field':7s} {'values':>9s} {'minimum':>22s} {'maximum':>22s} {'bounds':>20s} {'outside':>8s}")
    not_identical = 0
    total = 0
    for f in p91.FIELD_NAMES:
        lo, hi = BOUNDS[f]
        cols = [pc[f"{f}_{j}"] for j in (1, 2, 3, 4)]
        n, vmin, vmax, out = 0, math.inf, -math.inf, 0
        for r in p_rows:
            for i in cols:
                s = r[i]
                if s == "":
                    continue
                v = float(s)
                if repr(v) != s:
                    not_identical += 1
                n += 1
                vmin, vmax = min(vmin, v), max(vmax, v)
                if not (lo <= v <= hi):
                    out += 1
        total += n
        print(f"  {f:7s} {n:>9d} {vmin!r:>22s} {vmax!r:>22s} {f'{lo:g} to {hi:g}':>20s} {out:>8d}")
    print(f"read-back: {total} value cells; float then repr gives a different string in {not_identical}")


def run_gate(args, hours):
    """Session 92, Step 5: the extended gate, with session 91's gate arithmetic
    (load_airports, bilinear_stored, derive, imported). Same operation order as
    F133.7: bilinear on the four stored values of each needed message, then derive."""
    d = Path(args.dir)
    pts_path, man_path, meta_path = the_files(d, args.month)
    print(f"SESSION 92 --gate (offline): chunk {args.month} in {d}; hours {hours[0]}-{hours[1]}")
    meta = meta_path.read_text()
    pos_sha = p91.sha256_file(p91.POSITIONS)
    print(f"positions file SHA-256 {pos_sha}; recorded in the chunk's meta: {pos_sha in meta}")
    if pos_sha not in meta:
        raise SystemExit("STOP: the chunk was not made with this positions file")
    m = re.search(r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`",
                  p91.DECISIONS_FILE.read_text())
    have = p91.sha256_file(TRAINING_SET)
    print(f"training set SHA-256 {have}; F122.3 {m.group(1)}; equal: {have == m.group(1)}")
    if have != m.group(1):
        raise SystemExit("STOP: the training set differs from F122.3")

    airports = p91.load_airports()
    positions, _ = p91.read_positions()
    pos = {p["icao"]: p for p in positions}
    for p in positions:
        p["lat"], p["lon"] = float(p["lat_used"]), float(p["lon_used"])
        p["pts"] = [(float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"])) for k in (1, 2, 3, 4)]
    for st, a in airports.items():
        p = pos[p91.DEV[st]]
        if (p["lat"], p["lon"]) != (a["grid_lat"], a["grid_lon"]) or p["role"] != "development":
            raise SystemExit(f"STOP: {st}'s position in the positions file is not SPEC 3.4's grid point")

    gated = {st: a for st, a in airports.items() if a["lead"] <= hours[1]}
    skipped = [f"{st} (lead {a['lead']})" for st, a in airports.items() if a["lead"] > hours[1]]
    names = [f"{st} {a['cycle']:02d}z lead {a['lead']}" for st, a in gated.items()]
    print(f"gated airports (lead within hours): {', '.join(names)}")
    print(f"not gated (lead outside hours {hours[0]}-{hours[1]}): {', '.join(skipped) or 'none'}")

    # Committed rows: an explicit column list. Only these columns are kept.
    want = GATE_KEY_COLS + p91.GATE_COLS
    with open(TRAINING_SET, newline="") as f:
        r = csv.reader(f)
        header = next(r)
        idx = [header.index(c) for c in want]
        training = {}
        for row in r:
            keep = [row[i] for i in idx]
            training[(keep[0], keep[1])] = dict(zip(p91.GATE_COLS, keep[2:]))
    print(f"training set columns read: {want}")

    y, mo = p91.parse_month(args.month)
    cycles_in_month = {c for c, _ in p91.plan_chunk(p91.month_cycles(y, mo), hours)}
    _, m_rows = read_gz_csv(man_path)
    status = {(r[0], int(r[1]), r[2]): r[6] for r in m_rows}
    _, p_rows = read_gz_csv(pts_path)
    points = {(r[0], int(r[1]), r[3]): dict(zip(p91.POINT_COLS, r)) for r in p_rows}

    need = {"tmp2m": ("t2m", 0), "tcdc": ("tcdc", 0), "ugrd10m": ("u10", 0), "vgrd10m": ("v10", 0),
            "t850": ("t850", 0), "dpt2m": ("d2m", 0), "prmsl": ("prmsl", 0), "prmsl_m3": ("prmsl", -3),
            "dswrf": ("dswrf", 0), "dswrf_m2": ("dswrf", -2)}
    passed = {st: {c: [0, 0] for c in p91.GATE_COLS} for st in gated}
    days = {st: 0 for st in gated}
    mism, no_row, not_built = [], [], []
    for st, a in gated.items():
        p = pos[p91.DEV[st]]
        for c in sorted(x for x in cycles_in_month if x.hour == a["cycle"]):
            target = (c + dt.timedelta(days=1)).date()
            com = training.get((st, target.isoformat()))
            if com is None:
                no_row.append((st, target.isoformat()))
                continue
            got = {}
            try:
                for key, (fname, off) in need.items():
                    if key == "dswrf_m2" and a["lead"] - p91.window_start(a["lead"]) == 2:
                        continue
                    k = (p91.iso(c), a["lead"] + off)
                    s = status.get(k + (fname,))
                    if s != "ok":
                        raise ValueError(f"{fname} at {k[0]} f{k[1]:03d} has status {s!r}")
                    row = points[k + (p["icao"],)]
                    got[key] = p91.bilinear_stored(p, [float(row[f"{fname}_{j}"]) for j in (1, 2, 3, 4)])
                reb = p91.derive(a, target, got)
            except (KeyError, ValueError) as e:
                not_built.append((st, target.isoformat(), repr(e)))
                continue
            days[st] += 1
            for col in p91.GATE_COLS:
                passed[st][col][1] += 1
                cv = float(com[col])
                if cv == reb[col]:
                    passed[st][col][0] += 1
                else:
                    mism.append((st, target.isoformat(), p91.iso(c), col, cv, reb[col]))
    print("\npass table by column (exact equality, no tolerance):")
    print(f"  {'column':34s} " + " ".join(f"{st:>9s}" for st in gated) + f" {'all':>9s}")
    for col in p91.GATE_COLS:
        print(f"  {col:34s} " + " ".join(f"{passed[st][col][0]:>4d} / {passed[st][col][1]:<2d}" for st in gated)
              + f" {sum(passed[s][col][0] for s in gated):>4d} / {sum(passed[s][col][1] for s in gated)}")
    print("pass table by airport:")
    for st in gated:
        bad_days = len({t for s, t, *_ in mism if s == st})
        vals = sum(passed[st][c][0] for c in p91.GATE_COLS), sum(passed[st][c][1] for c in p91.GATE_COLS)
        print(f"  {st:5s} ({p91.DEV[st]}): station-days rebuilt {days[st]}, all 7 columns equal {days[st] - bad_days}; "
              f"values {vals[0]} of {vals[1]}")
    n_try = sum(days.values()) + len(no_row) + len(not_built)
    print(f"station-days in the month: {n_try}; rebuilt and compared {sum(days.values())}")
    print(f"station-days with no committed row (not a failure): {len(no_row)} {no_row or ''}")
    print(f"station-days not rebuilt (a needed message not ok): {len(not_built)} {not_built or ''}")
    print(f"mismatches: {len(mism)}")
    for st, t, c, col, cv, rv in mism:
        print(f"  MISMATCH {st} {t} (cycle {c}) {col}: committed {cv!r}, rebuilt {rv!r}")
    ok = not mism and not not_built
    print("EXTENDED GATE PASSED" if ok else "EXTENDED GATE NOT PASSED")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--dir", required=True, help="the directory holding the chunk's three files")
    ap.add_argument("--month", required=True, help="YYYY-MM")
    ap.add_argument("--hours", required=True, help="forecast hours A-B, as the chunk was pulled")
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--ranges", action="store_true", help="local use only: also print ranges and the read-back count")
    g.add_argument("--gate", action="store_true", help="local use only: the extended gate (Step 5) instead")
    a = ap.parse_args()
    try:
        hours = p91.parse_hours(a.hours)
        p91.parse_month(a.month)
    except p91.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3
    if a.gate:
        return run_gate(a, hours)
    return run_checks(a, hours)


if __name__ == "__main__":
    sys.exit(main())
