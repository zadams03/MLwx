"""Session 104: the stage C development table for leads 25 to 48 (DECISIONS D98.4).

For each development airport (EGLC, LFPG, DSM, YSDU, RNO, KSFO), every GFS
cycle in the f025 to f048 pull's plan and every forecast hour 25 to 48, it
rebuilds D88.5's features from the stored grid values and pairs D88.7's
hourly observation, by session 96's code and rules, and writes six new files
in MLwx-stagec/ (stagec_dev_f025_048_<ICAO>.csv.gz). F138's six files are
never changed: their SHA-256 are checked before and after every mode that
writes. Offline: no network call. No model, no score.

Inputs before forecast hour 25 (T at leads 25 to 27, which needs PRMSL at
22 to 24; R at lead 25, which needs DSWRF at 24 and 23) come from the f000 to
f024 pull (MLwx-pull/, F137), same cycle. Where that pull has no such value
(cycles before its first planned hour), the feature is empty with reason
"outside pull window", and counted (D98.4).

What is used from scripts/session96_stagec_table.py, unchanged (imported):
make_row (every column of one row: session 91's derive for the
instantaneous columns, r_inputs and r_value for R, t_inputs and t_value for
T, nearest_obs for the observation, the empty reasons and the guards),
load_obs, load_positions, check_pull_files (the f000 to f024 files against
session 95's inventory), fmt, table_bytes, write_new_file, read_table,
COLUMNS, GRIB_COLS, REASONS, OK_STATUSES, STATIONS, DEV_ICAOS, GuardError,
check_valid_time, check_obs_time and versions. Written here: reading the two
pulls for one month, the loop over the 25-48 plan, the inputs check against
the new inventory, the equivalence check, the gate at lead 26 and the
records.

Modes (exactly one):
  --inputs   Every 25-48 pull file against the new inventory, and every
             f000 to f024 file against session 95's inventory.
  --equiv    The builder run on hours 0 to 24 for EGLC and RNO, month
             2022-01, in memory, against those rows of F138's files.
  --build    The six files. Refuses if any exists.
  --gate     YSDU 00z lead 26, RNO and KSFO 18z lead 26 against every
             committed station-day of session81_training_set.csv.
  --records  Rebuild in memory and check byte-equality with the files;
             rebuild DSM into a mktemp -d directory and check it, then delete
             it; write the counts file and the meta file.
"""

import argparse
import csv
import datetime as dt
import gzip
import math
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

import session96_stagec_table as s96  # noqa: E402

s92, p91, s86 = s96.s92, s96.p91, s96.s86

ROOT = s96.ROOT
PULL_25 = ROOT.parent / "MLwx-pull-f025-048"
PULL_00 = s96.PULL_DIR                       # MLwx-pull/, the f000 to f024 pull
STAGEC = s96.OUT_DEFAULT                     # MLwx-stagec/
INVENTORY_25 = ROOT / "data" / "processed" / "session104_pull_f025_048_inventory.csv"
COUNTS_OUT = ROOT / "data" / "processed" / "session104_stagec_f025_048_counts.csv"
META_OUT = ROOT / "data" / "processed" / "session104_stagec_f025_048_table.meta.txt"
TRAINING_SET = s96.TRAINING_SET
HOURS = (25, 48)
PRIOR_HOURS = (0, 24)

# F138.4's six files, by SPEC 3.4 station code (also in session97_stagec_cv.py's TABLES).
F138_TABLES = {
    "EGLC": "af8848e091c79aecac5f809536e4dec20757d288f7ebc1cf3e830d33a69c9126",
    "LFPG": "5b113123c7642eefb8d212cbe5151f43e8ba343a231dc90d4461ed104e6b661f",
    "DSM": "17461736cd23585781ebf01a842469a1ea6b0e93571bea250869a23271dc0e32",
    "YSDU": "57a11a4f00250304f289de158223eff45f841d572e3c3c7f65e5b6fc6c0fa829",
    "RNO": "6e2d0779f6b5ea92dc77e3b074030ac3676bd90cffe3b44ab6e3441c06831ec3",
    "SFO": "11fa6385f05c57cf627734d9caed13927f1e176e07c5fc039f700d30fd1ceff8",
}
TRAINING_SET_SHA256 = "ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a"   # F122.3
GATED = [("YSDU", 0, 26), ("RNO", 18, 26), ("SFO", 18, 26)]                          # D98.4


def now_utc():
    return s96.now_utc()


def s97_time(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")


def table_name(st):
    return f"stagec_dev_f025_048_{p91.DEV[st]}.csv.gz"


def check_f138(label):
    """F138's six files are unchanged."""
    bad = [st for st, h in F138_TABLES.items() if p91.sha256_file(STAGEC / s96.table_name(st)) != h]
    print(f"F138's six table files, SHA-256 equal to F138.4 ({label}): {not bad} {bad or ''}")
    if bad:
        raise SystemExit("STOP: an F138 table file differs from F138.4")


def check_pull_25(verbose=True):
    """Every file in MLwx-pull-f025-048/ against this session's inventory."""
    with open(INVENTORY_25, newline="") as f:
        inv = list(csv.DictReader(f))
    have = sorted(p.name for p in PULL_25.iterdir())
    want = sorted(r["asset"] for r in inv)
    bad = []
    if have != want:
        bad.append(f"file names differ: extra {sorted(set(have) - set(want))}, missing {sorted(set(want) - set(have))}")
    for r in inv:
        p = PULL_25 / r["asset"]
        if p.exists() and (p.stat().st_size != int(r["bytes"]) or p91.sha256_file(p) != r["sha256"]):
            bad.append(f"{r['asset']}: differs")
    if verbose:
        print(f"25-48 pull files: {len(have)} in {PULL_25.name}/; inventory rows {len(inv)}; names, bytes and "
              f"SHA-256 all equal: {not bad}")
    if bad:
        for b in bad:
            print("  DIFFERENCE:", b)
        raise SystemExit("STOP: a 25-48 pull file differs from the inventory")


def read_pull_month(d, month):
    """As session 96's read_month, for any pull folder: the manifest statuses
    and the development airports' points rows. Other airports' rows are skipped
    on the icao field."""
    pts_path, man_path, _ = s92.the_files(d, month)
    m_head, m_rows = s92.read_gz_csv(man_path)
    if m_head != p91.MAN_COLS:
        raise SystemExit(f"STOP: {man_path.name} header")
    mc = {c: i for i, c in enumerate(m_head)}
    status = {}
    for r in m_rows:
        k = (r[mc["cycle_utc"]], int(r[mc["fhour"]]), r[mc["field"]])
        if k in status:
            raise SystemExit(f"STOP: duplicate manifest key {k}")
        status[k] = r[mc["status"]]
    points = {}
    with gzip.open(pts_path, "rt", newline="") as f:
        rd = csv.reader(f)
        if next(rd) != p91.POINT_COLS:
            raise SystemExit(f"STOP: {pts_path.name} header")
        for r in rd:
            if r[3] not in s96.DEV_ICAOS:
                continue
            k = (r[0], int(r[1]), r[3])
            if k in points:
                raise SystemExit(f"STOP: duplicate points key {k}")
            points[k] = r
    return status, points


def prior_needs(hours):
    """The forecast hours below hours[0] that R or T at any lead in hours needs."""
    need = set()
    for n in range(hours[0], hours[1] + 1):
        for fh in (s96.r_inputs(n) or []) + (s96.t_inputs(n) or []):
            if fh < hours[0]:
                need.add(fh)
    return need


def load_values(c_iso, cycle, fhs, status, points, icao, p, val, stat):
    """Bilinear on the four stored values of every ok message, as session 96's build."""
    col_i = {c: i for i, c in enumerate(p91.POINT_COLS)}
    for fh in fhs:
        r = points[(c_iso, fh, icao)]
        if r[2] != p91.iso(cycle + dt.timedelta(hours=fh)):
            raise SystemExit(f"STOP: valid_utc {r[2]} at {c_iso} f{fh:03d}")
        for fname in p91.FIELD_NAMES:
            s = status[(c_iso, fh, fname)]
            stat[(fh, fname)] = s
            cells = [r[col_i[f"{fname}_{k}"]] for k in (1, 2, 3, 4)]
            if s in s96.OK_STATUSES:
                v4 = [float(x) for x in cells]
                if not all(math.isfinite(x) for x in v4):
                    raise SystemExit(f"STOP: non-finite stored value at {c_iso} f{fh:03d} {fname}")
                val[(fh, fname)] = p91.bilinear_stored(p, v4)
            elif any(x != "" for x in cells):
                raise SystemExit(f"STOP: a filled cell in a non-ok message at {c_iso} f{fh:03d} {fname}")


def build(stations, hours, main_dir, prior_dir=None, month_list=None, log=print):
    """Every row for the given stations and hours. Inputs inside `hours` come
    from main_dir; inputs below hours[0] come from prior_dir (the f000 to f024
    pull), only for the hours R and T need. Returns (lines, tallies, obs stats,
    plan rows)."""
    airports, pos, _ = s96.load_positions()
    need = prior_needs(hours) if prior_dir is not None else set()
    obs, obs_stats, caches, lines, tallies = {}, {}, {}, {}, {}
    for st in stations:
        times, vals, _, stats = s96.load_obs(st)
        stats["ties"] = 0
        obs[st], obs_stats[st], caches[st] = (times, vals), stats, {}
        lines[st] = [",".join(s96.COLUMNS)]
        tallies[st] = {}
    expected_rows = 0
    for y, m in p91.all_months():
        month = f"{y}-{m:02d}"
        if month_list is not None and month not in month_list:
            continue
        plan = p91.plan_chunk(p91.month_cycles(y, m), hours)
        status, points = read_pull_month(main_dir, month)
        if need:
            prior_plan = {c: fhs for c, fhs in p91.plan_chunk(p91.month_cycles(y, m), PRIOR_HOURS)}
            p_status, p_points = read_pull_month(prior_dir, month)
        for cycle, fhs in plan:
            c_iso = p91.iso(cycle)
            prior = sorted(need & set(prior_plan.get(cycle, []))) if need else []
            in_plan = set(fhs) | set(prior)
            expected_rows += len(fhs)
            for st in stations:
                a, p, icao = airports[st], pos[st], p91.DEV[st]
                val, stat = {}, {}
                load_values(c_iso, cycle, fhs, status, points, icao, p, val, stat)
                if prior:
                    load_values(c_iso, cycle, prior, p_status, p_points, icao, p, val, stat)
                for n in fhs:
                    lines[st].append(s96.make_row(st, a, cycle, n, in_plan, val, stat, obs[st], caches[st],
                                                  obs_stats[st], tallies[st]))
        log(f"  {month}: {len(plan)} cycles, {sum(len(f) for _, f in plan)} rows per airport ({now_utc()})")
    for st in stations:
        if len(lines[st]) - 1 != expected_rows:
            raise SystemExit(f"STOP: {st} has {len(lines[st]) - 1} rows, the plan {expected_rows}")
    return lines, tallies, obs_stats, expected_rows


# ------------------------------------------------------------------ modes

def run_inputs(args):
    print(f"SESSION 104 --inputs (offline), {now_utc()}")
    print(f"inventory {INVENTORY_25.relative_to(ROOT)} SHA-256 {p91.sha256_file(INVENTORY_25)}")
    check_pull_25()
    print(f"inventory {s96.INVENTORY.relative_to(ROOT)} SHA-256 {p91.sha256_file(s96.INVENTORY)}")
    s96.check_pull_files()
    print(f"forecast hours read from the f000 to f024 pull for leads 25 to 48: {sorted(prior_needs(HOURS))}")
    print("INPUTS: PASS")
    return 0


def run_equiv(args):
    print(f"SESSION 104 --equiv (offline), {now_utc()}: the builder on hours 0 to 24, EGLC and RNO, 2022-01")
    lines, _, _, n = build(["EGLC", "RNO"], PRIOR_HOURS, PULL_00, None, ["2022-01"], log=lambda *a: None)
    ok = True
    for st in ("EGLC", "RNO"):
        path = STAGEC / s96.table_name(st)
        if p91.sha256_file(path) != F138_TABLES[st]:
            raise SystemExit(f"STOP: {path.name} is not F138's")
        with gzip.open(path, "rt", newline="") as f:
            old = [ln.rstrip("\n") for ln in f]
        old_rows = [old[0]] + [ln for ln in old[1:] if ln.split(",", 2)[1].startswith("2022-01")]
        same = old_rows == lines[st]
        diff = sum(1 for a, b in zip(old_rows, lines[st]) if a != b)
        print(f"  {st}: rebuilt rows {len(lines[st]) - 1}; F138 rows with a 2022-01 cycle {len(old_rows) - 1}; "
              f"header equal {old_rows[0] == lines[st][0]}; lines differing {diff}; byte-equal {same}")
        ok &= same
    print("EQUIVALENCE: PASS" if ok else "EQUIVALENCE: FAIL, STOP")
    return 0 if ok else 1


def run_build(args):
    t0 = time.time()
    print(f"SESSION 104 --build (offline), start {now_utc()}; out {STAGEC}")
    targets = [STAGEC / table_name(st) for st in s96.STATIONS]
    there = [p.name for p in targets if p.exists() or p.with_name(p.name + ".partial").exists()]
    if there:
        raise SystemExit(f"STOP: already exists: {there}")
    check_f138("before")
    check_pull_25()
    s96.check_pull_files()
    lines, tallies, ostats, n_plan = build(s96.STATIONS, HOURS, PULL_25, PULL_00)
    print(f"\nplan rows per airport: {n_plan}; all {n_plan * 6}")
    for st in s96.STATIONS:
        data = s96.table_bytes(lines[st])
        path = STAGEC / table_name(st)
        s96.write_new_file(path, data)
        print(f"  {path.name}: rows {len(lines[st]) - 1}, bytes {len(data):,}, SHA-256 {s96.sha256_bytes(data)}")
    print_counts(tallies, ostats)
    check_f138("after")
    print(f"leftover partial files: {sorted(p.name for p in STAGEC.glob('*.partial')) or 'none'}")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


def print_counts(tallies, ostats):
    print("\nper airport: rows; complete-case rows; no observation; uses whole file; empty cells by column and reason")
    for st in s96.STATIONS:
        tt = tallies[st]
        emp = {}
        for t in tt.values():
            for k, v in t["empty"].items():
                emp[k] = emp.get(k, 0) + v
        s = ostats[st]
        print(f"  {st}: rows {sum(t['rows'] for t in tt.values())}; complete case "
              f"{sum(t['complete'] for t in tt.values())}; no observation {sum(t['no_obs'] for t in tt.values())}; "
              f"uses whole file {sum(t['whole'] for t in tt.values())}; obs ties {s['ties']}")
        for (col, why), v in sorted(emp.items()):
            print(f"      {col} empty, {why}: {v}")


def early_inputs(col, cycle, lead):
    """The input valid times before the pull window (2021-03-24T00:00, D82.4)
    that a column needs at this cycle and lead: only R and T read other leads."""
    leads = s96.r_inputs(lead) if col == "dswrf_2h_wm2" else s96.t_inputs(lead) \
        if col == "pressure_tendency_3h_hpa" else [lead]
    return [cycle + dt.timedelta(hours=fh) for fh in (leads or [])
            if cycle + dt.timedelta(hours=fh) < p91.FIRST_VALID]


def run_gate(args):
    print(f"SESSION 104 --gate (offline), {now_utc()}")
    have = p91.sha256_file(TRAINING_SET)
    print(f"training set SHA-256 {have}; F122.3 {TRAINING_SET_SHA256}; equal {have == TRAINING_SET_SHA256}")
    if have != TRAINING_SET_SHA256:
        raise SystemExit("STOP: the training set differs from F122.3")
    airports = s86.load_airports()
    with open(TRAINING_SET, newline="") as f:
        rd = csv.DictReader(f)
        tcols = rd.fieldnames
        committed = {}
        for r in rd:
            committed[(r["station"], r["target_date"])] = r
    shared = [c for c in tcols if c in s96.COLUMNS and c != "station"]
    print(f"columns compared (held by both): {shared}")
    fails = 0
    early = []
    for st, ch, lead in GATED:
        a = airports[st]
        if (a["cycle"], a["lead"]) != (ch, lead):
            raise SystemExit(f"STOP: {st}'s record cycle and lead are not {ch}z lead {lead}")
        rows = s96.read_table(STAGEC / table_name(st))
        table = {}
        for r in rows:
            if int(r["cycle_hour"]) == ch and int(r["lead"]) == lead:
                v = dt.datetime.strptime(r["valid_utc"], "%Y-%m-%dT%H:%MZ")
                if v.hour != a["target_hour"]:
                    raise SystemExit(f"STOP: {st} valid hour {v.hour}")
                table[v.date().isoformat()] = r
        com = {d: r for (s, d), r in committed.items() if s == st}
        no_table = sorted(set(com) - set(table))
        no_com = sorted(set(table) - set(com))
        res = {c: [0, 0] for c in shared}
        mism = []
        obs_diff, obs_none = 0, 0
        for d in sorted(set(com) & set(table)):
            c, t = com[d], table[d]
            if int(c["target_hour"]) != a["target_hour"]:
                raise SystemExit("STOP: target hour")
            for col in shared:
                res[col][1] += 1
                if t[col] != "" and float(c[col]) == float(t[col]):
                    res[col][0] += 1
                elif t[col] == "" and early_inputs(col, s97_time(t["cycle_utc"]), lead):
                    # Owner ruling at session 104's stop (recorded in F147): the cell is empty with reason
                    # "outside pull window" and its missing input is valid before 2021-03-24T00:00.
                    early.append((st, d, col, c[col], [p91.iso(v) for v in
                                                      early_inputs(col, s97_time(t["cycle_utc"]), lead)]))
                else:
                    mism.append((d, col, c[col], t[col]))
            if t["obs_tmpc"] == "":
                obs_none += 1
            elif float(t["obs_tmpc"]) != float(c["obs_c"]):
                obs_diff += 1
        n_cmp = len(set(com) & set(table))
        print(f"\n{st} ({p91.DEV[st]}) {ch:02d}z lead {lead}: committed station-days {len(com)}; table rows "
              f"{len(table)}; compared {n_cmp}; committed with no table row {len(no_table)} {no_table or ''}; "
              f"table with no committed row {len(no_com)} {no_com or ''}")
        print(f"  {'column':34s} {'compared':>8s} {'equal':>8s} {'mismatched':>10s}")
        for col in shared:
            print(f"  {col:34s} {res[col][1]:>8d} {res[col][0]:>8d} {res[col][1] - res[col][0]:>10d}")
        print(f"  observation: table's obs_tmpc differs from the record's obs_c on {obs_diff} days; table has no "
              f"observation on {obs_none} days; equal on {n_cmp - obs_diff - obs_none} (count only, D98.4)")
        for d, col, cv, tv in mism:
            print(f"  MISMATCH {st} {d} {col}: committed {cv!r}, table {tv!r}")
        fails += len(mism) + len(no_table)
    print(f"\ncells accepted by the owner's ruling (table empty, reason outside pull window, input valid before "
          f"2021-03-24T00:00): {len(early)}")
    for st, d, col, cv, ins in early:
        print(f"  ACCEPTED {st} {d} {col}: committed {cv!r}, table empty; input valid {ins}")
    print(f"feature mismatches plus committed rows with no table row: {fails}")
    print("GATE PASSED" if fails == 0 else "GATE NOT PASSED: STOP")
    return 0 if fails == 0 else 1


def run_records(args):
    t0 = time.time()
    print(f"SESSION 104 --records (offline), start {now_utc()}")
    p91.check_out_free([COUNTS_OUT, META_OUT])
    check_f138("before")
    check_pull_25(verbose=False)
    s96.check_pull_files(verbose=False)
    lines, tallies, ostats, n_plan = build(s96.STATIONS, HOURS, PULL_25, PULL_00, log=lambda *a: None)
    files = []
    for st in s96.STATIONS:
        data = s96.table_bytes(lines[st])
        same = data == (STAGEC / table_name(st)).read_bytes()
        print(f"in-memory rebuild of {table_name(st)} byte-equal to the file: {same}")
        if not same:
            raise SystemExit("STOP: the rebuild differs from the written table")
        files.append((table_name(st), len(lines[st]) - 1, len(data), s96.sha256_bytes(data)))
    # DSM rebuilt into a new temporary directory, written as --build writes
    tmp = Path(tempfile.mkdtemp(prefix="session104_dsm_"))
    try:
        l2, _, _, _ = build(["DSM"], HOURS, PULL_25, PULL_00, log=lambda *a: None)
        s96.write_new_file(tmp / table_name("DSM"), s96.table_bytes(l2["DSM"]))
        same = (tmp / table_name("DSM")).read_bytes() == (STAGEC / table_name("DSM")).read_bytes()
        print(f"DSM rebuilt alone into {tmp}: byte-equal to {table_name('DSM')}: {same}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"temporary directory deleted: {not tmp.exists()}")
    if not same:
        raise SystemExit("STOP: the DSM rebuild differs")
    head = ["station", "icao", "lead", "rows"]
    for col in s96.GRIB_COLS:
        head += [f"{col}_empty_{r.replace(' ', '_')}" for r in s96.REASONS]
    head += ["no_observation", "uses_whole_file", "complete_case"]
    rows = []
    for st in s96.STATIONS:
        for n in range(HOURS[0], HOURS[1] + 1):
            t = tallies[st][n]
            r = [st, p91.DEV[st], n, t["rows"]]
            for col in s96.GRIB_COLS:
                r += [t["empty"].get((col, why), 0) for why in s96.REASONS]
            r += [t["no_obs"], t["whole"], t["complete"]]
            rows.append(r)
    s96.write_new_file(COUNTS_OUT, ("\n".join(",".join(str(x) for x in r) for r in [head] + rows) + "\n").encode())
    print(f"wrote {COUNTS_OUT.relative_to(ROOT)}: {len(rows)} rows, {len(head)} columns, "
          f"SHA-256 {p91.sha256_file(COUNTS_OUT)}")
    print_counts(tallies, ostats)
    meta = [
        "Provenance (SPEC 2.3). Do not edit the data files.",
        "",
        "files       : stagec_dev_f025_048_<ICAO>.csv.gz, one per development airport",
        "purpose     : session 104 (DECISIONS D98.4): the stage C development table for forecast hours 25 to 48:",
        "              for each development airport, every GFS cycle in the f025 to f048 pull's plan and every",
        "              forecast hour 25 to 48, D88.5's features rebuilt from the stored grid values and D88.7's",
        "              hourly observation, by session 96's code (make_row, imported unchanged). No model, no score.",
        f"where       : {STAGEC.name}/ beside the repository (not tracked, D88.8), next to F138's six files,",
        "              which are unchanged. Rebuilt exactly by scripts/session104_stagec_table_f025_048.py --build.",
        f"written by  : scripts/session104_stagec_table_f025_048.py --build; this meta by --records at {now_utc()}",
        f"script sha256: {p91.sha256_file(Path(__file__).resolve())}",
        "",
        "table files :",
    ]
    meta += [f"  {name}  rows {n:,}  bytes {b:,}  sha256 {sha}" for name, n, b, sha in files]
    meta += [
        f"  rows per airport {n_plan:,} (session91_grib_pull.py's plan, hours 25 to 48); all {n_plan * 6:,}",
        "  columns, column order, row rules, gzip and number format exactly as F138's files (session 96's",
        "  COLUMNS, make_row, fmt, table_bytes); rows in cycle, then lead order.",
        "  Inputs below forecast hour 25 (PRMSL at 22 to 24 for T at leads 25 to 27; DSWRF at 23 and 24 for R",
        "  at lead 25) come from the f000 to f024 pull, same cycle; where that pull's plan has no such hour,",
        "  the feature is empty with reason 'outside pull window' (D98.4).",
        "",
        "inputs      :",
        f"  {INVENTORY_25.relative_to(ROOT)} sha256 {p91.sha256_file(INVENTORY_25)} (MLwx-pull-f025-048/,",
        "  195 files, each checked against it before the build)",
        f"  {s96.INVENTORY.relative_to(ROOT)} sha256 {p91.sha256_file(s96.INVENTORY)} (MLwx-pull/, 195 files,",
        "  each checked against it before the build)",
        f"  {p91.POSITIONS.relative_to(ROOT)} sha256 {p91.sha256_file(p91.POSITIONS)}",
    ]
    meta += [f"  {p.relative_to(ROOT)} sha256 {p91.sha256_file(p)}" for p in s86.PARAMS_CSVS]
    meta += ["  observation files (as F138):"]
    meta += [f"  {f.relative_to(ROOT)} sha256 {p91.sha256_file(f)}" for st in s96.STATIONS for f in s96.obs_files(st)]
    meta += [
        "imported code:",
    ]
    for name in ("session96_stagec_table.py", "session86_forward_build.py", "session92_verify_chunk.py",
                 "session91_grib_pull.py"):
        meta.append(f"  scripts/{name} sha256 {p91.sha256_file(ROOT / 'scripts' / name)}")
    meta.append(f"versions    : {s96.versions()}")
    s96.write_new_file(META_OUT, ("\n".join(meta) + "\n").encode())
    print(f"wrote {META_OUT.relative_to(ROOT)}: SHA-256 {p91.sha256_file(META_OUT)}")
    check_f138("after")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("inputs", "equiv", "build", "gate", "records"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    fn = {"inputs": run_inputs, "equiv": run_equiv, "build": run_build, "gate": run_gate, "records": run_records}
    try:
        return fn[next(k for k in fn if getattr(a, k))](a)
    except (s96.GuardError, p91.GuardError) as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
