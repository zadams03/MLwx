"""Session 106: the stage C tables for the six claim airports (DECISIONS D100.3(a), D100.9(a), (b)).

For each claim airport (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN; D82.7), every GFS
cycle in the two pulls and every forecast hour 0 to 24 and 25 to 48, it
rebuilds D88.5's features from the stored grid values and pairs D88.7's
hourly observation, by session 96's and session 104's code, and writes two
files per airport in MLwx-stagec/:
stagec_claim_f000_024_<ICAO>.csv.gz and stagec_claim_f025_048_<ICAO>.csv.gz.
Same columns, column order, rounding, row rules and empty reasons as F138's
and F147's files. Offline: no network call. No model, no score.

What is used unchanged (imported after each script's SHA-256 check):
  from scripts/session96_stagec_table.py (F138): make_row (every column of
  one row, the empty reasons, the guards), load_obs and obs_files (by station
  code, which for a claim airport is its IEM id), check_pull_files, fmt,
  table_bytes, write_new_file, sha256_bytes, load_positions (development
  airports only, in --equiv), COLUMNS, GRIB_COLS, REASONS, GuardError,
  versions.
  from scripts/session104_stagec_table_f025_048.py (F147): load_values (it
  already takes the ICAO code and the position), prior_needs, check_pull_25,
  check_f138, F138_TABLES, PULL_00, PULL_25, STAGEC.
What is parameterised here (session 104's read_pull_month and build are
fixed to the development airports): read_pull_month takes the set of ICAO
codes whose points rows are kept; build takes a list of airport specs, each
with its station code (the IEM id, as the observation file names and the
table's station column use it), ICAO code, position (with its four grid
points and weights from the positions file) and elevation constant, in
place of session 96's load_positions and the params files. Otherwise the
two are copied line for line. derive (inside make_row) also reads a "lead"
key, used only for its own R value, which make_row never uses; a
placeholder (24) is given.

The elevation constant of a claim airport (D100.3(b)): round(7.429 x
height_diff_m / 1000, 4), height_diff_m from data/processed/session90_airports.csv
(F132.3), 4 decimals as the params files hold the development constants.

Modes (exactly one):
  --equiv    The new build, given EGLC's and RNO's own inputs (SPEC 3.4 grid
             point, params-file constant, committed observation files),
             month 2022-01, hours 0 to 24 and 25 to 48, in memory, against
             those rows of F138's and F147's files.
  --build    The twelve files. Refuses if any exists.
  --sanity   D100.9(b): per claim airport, complete-case rows at leads 3 to
             24 valid before 2024-08-01T00:00 only: n, raw GFS mean error
             and MAE. Rows valid on or after the cutoff are skipped on their
             valid time before any value is read, and the statistic refuses
             any such row.
  --records  Rebuild in memory and check byte-equality with the files;
             rebuild NZWN into a mktemp -d directory and check it, then
             delete it; write the counts file and the meta file.
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
S104_SHA256 = "77457e262aae6388495ebebac64c730bc82d82675a3802d89fbd5f7f09fc2222"   # F147 (session 104's table script)
S96_SHA256 = "40b63d006a3de4b4b796476c6b2408700bc9200a508feda804a187531b666eee"    # F138 (session 96's table script)


def _sha256_path(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


for _name, _want in (("session96_stagec_table.py", S96_SHA256), ("session104_stagec_table_f025_048.py", S104_SHA256)):
    if _sha256_path(SCRIPTS / _name) != _want:
        raise SystemExit(f"STOP: scripts/{_name} SHA-256 is not the recorded one")

import session104_stagec_table_f025_048 as s104  # noqa: E402

s96 = s104.s96
p91, s86 = s96.p91, s96.s86

STAGEC = s104.STAGEC
AIRPORTS_CSV = ROOT / "data" / "processed" / "session90_airports.csv"
AIRPORTS_CSV_SHA256 = "b53b689f2226e043228725938ad7c47c2069f4831626cc662118559393465db7"   # F132
COUNTS_OUT = ROOT / "data" / "processed" / "session106_claim_counts.csv"
META_OUT = ROOT / "data" / "processed" / "session106_claim_table.meta.txt"
CLAIM = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]                              # D82.7, F132.6
LAPSE_C_PER_KM = 7.429                                                               # SPEC 7.2
CUTOFF = dt.datetime(2024, 8, 1, 0, 0)                                               # D100.3(c)
DERIVE_LEAD_PLACEHOLDER = 24
# F147's two files used by --equiv (data/processed/session104_stagec_f025_048_table.meta.txt, F147.2).
F147_TABLES = {
    "EGLC": "947bf2f0920e1a1f972ea9297fcc9bdc5c987562e13ee5daa7ae5ab866066ea9",
    "RNO": "3ca1d4ff8933f14c6e898525ba445af080b92c0545989fe39b3d7bdbfdd6bd58",
}
# hour set: (hours, main pull, prior pull)
HOURSETS = {"f000_024": ((0, 24), s104.PULL_00, None), "f025_048": ((25, 48), s104.PULL_25, s104.PULL_00)}


def now_utc():
    return s96.now_utc()


def claim_name(icao, hs):
    return f"stagec_claim_{hs}_{icao}.csv.gz"


def claim_targets():
    return [STAGEC / claim_name(ic, hs) for ic in CLAIM for hs in HOURSETS]


def elevation_constant(height_diff_m):
    """D100.3(b): 7.429 degrees C per km times the height difference, held at 4 decimals."""
    return round(LAPSE_C_PER_KM * height_diff_m / 1000.0, 4)


def make_spec(station, icao, lat, lon, const, role):
    """One airport's inputs for build: the positions file row for icao (its four
    points and weights), checked to be at (lat, lon) with the given role."""
    rows, _ = p91.read_positions()
    hits = [r for r in rows if r["icao"] == icao]
    if len(hits) != 1:
        raise SystemExit(f"STOP: {icao} is not once in the positions file")
    p = hits[0]
    p["lat"], p["lon"] = float(p["lat_used"]), float(p["lon_used"])
    p["pts"] = [(float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"])) for k in (1, 2, 3, 4)]
    if (p["lat"], p["lon"]) != (lat, lon) or p["role"] != role:
        raise SystemExit(f"STOP: {icao}'s positions file row is not at {lat}, {lon} with role {role}")
    return {"station": station, "icao": icao, "p": p,
            "a": {"correction_c": const, "lead": DERIVE_LEAD_PLACEHOLDER}}


def claim_specs():
    """The six claim airports' inputs, from session90_airports.csv and the positions file."""
    if p91.sha256_file(AIRPORTS_CSV) != AIRPORTS_CSV_SHA256:
        raise SystemExit("STOP: session90_airports.csv SHA-256 is not F132's")
    with open(AIRPORTS_CSV, newline="") as f:
        a90 = {r["icao"]: r for r in csv.DictReader(f)}
    specs = []
    for ic in CLAIM:
        r = a90[ic]
        if r["drawn"] != "yes":
            raise SystemExit(f"STOP: {ic} is not drawn in session90_airports.csv")
        sp = make_spec(r["iem_id"], ic, float(r["latitude"]), float(r["longitude"]),
                       elevation_constant(float(r["height_diff_m"])), "claim batch")
        s90 = {(float(r[f"grid{k}_lat"]), float(r[f"grid{k}_lon"]), float(r[f"grid{k}_weight"])) for k in (1, 2, 3, 4)}
        s91 = {(float(sp["p"][f"p{k}_lat"]), float(sp["p"][f"p{k}_lon"]), float(sp["p"][f"p{k}_weight"]))
               for k in (1, 2, 3, 4)}
        if s90 != s91:
            raise SystemExit(f"STOP: {ic}'s grid points and weights differ between the two files")
        sp["height_diff_m"], sp["time_zone"] = float(r["height_diff_m"]), r["time_zone"]
        specs.append(sp)
    return specs


def dev_spec(st):
    """A development airport's own inputs: SPEC 3.4's grid point and its params-file constant."""
    airports, pos, _ = s96.load_positions()
    a = airports[st]
    sp = make_spec(st, p91.DEV[st], a["grid_lat"], a["grid_lon"], a["correction_c"], "development")
    if sp["p"]["pts"] != pos[st]["pts"]:
        raise SystemExit(f"STOP: {st}'s grid points differ from session 96's")
    return sp


def read_pull_month(d, month, icaos):
    """Session 104's read_pull_month, with the kept ICAO codes as an input."""
    pts_path, man_path, _ = s104.s92.the_files(d, month)
    m_head, m_rows = s104.s92.read_gz_csv(man_path)
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
            if r[3] not in icaos:
                continue
            k = (r[0], int(r[1]), r[3])
            if k in points:
                raise SystemExit(f"STOP: duplicate points key {k}")
            points[k] = r
    return status, points


def build(specs, hours, main_dir, prior_dir=None, month_list=None, log=print):
    """Session 104's build, with the airports as inputs. Returns (lines, tallies,
    obs stats, plan rows, split) keyed by ICAO; split counts complete-case rows
    valid before and from 2024-08-01T00:00 (counts only)."""
    need = s104.prior_needs(hours) if prior_dir is not None else set()
    icaos = {sp["icao"] for sp in specs}
    obs, obs_stats, caches, lines, tallies, split = {}, {}, {}, {}, {}, {}
    for sp in specs:
        ic = sp["icao"]
        times, vals, _, stats = s96.load_obs(sp["station"])
        stats["ties"] = 0
        obs[ic], obs_stats[ic], caches[ic] = (times, vals), stats, {}
        lines[ic] = [",".join(s96.COLUMNS)]
        tallies[ic], split[ic] = {}, {"before": 0, "from": 0}
    expected_rows = 0
    cut = p91.iso(CUTOFF)
    for y, m in p91.all_months():
        month = f"{y}-{m:02d}"
        if month_list is not None and month not in month_list:
            continue
        plan = p91.plan_chunk(p91.month_cycles(y, m), hours)
        status, points = read_pull_month(main_dir, month, icaos)
        if need:
            prior_plan = {c: fhs for c, fhs in p91.plan_chunk(p91.month_cycles(y, m), s104.PRIOR_HOURS)}
            p_status, p_points = read_pull_month(prior_dir, month, icaos)
        for cycle, fhs in plan:
            c_iso = p91.iso(cycle)
            prior = sorted(need & set(prior_plan.get(cycle, []))) if need else []
            in_plan = set(fhs) | set(prior)
            expected_rows += len(fhs)
            for sp in specs:
                ic, p, a = sp["icao"], sp["p"], sp["a"]
                val, stat = {}, {}
                s104.load_values(c_iso, cycle, fhs, status, points, ic, p, val, stat)
                if prior:
                    s104.load_values(c_iso, cycle, prior, p_status, p_points, ic, p, val, stat)
                for n in fhs:
                    ln = s96.make_row(sp["station"], a, cycle, n, in_plan, val, stat, obs[ic], caches[ic],
                                      obs_stats[ic], tallies[ic])
                    lines[ic].append(ln)
                    if ln.endswith(",true"):
                        split[ic]["before" if ln.split(",", 5)[4] < cut else "from"] += 1
        log(f"  {month}: {len(plan)} cycles, {sum(len(f) for _, f in plan)} rows per airport ({now_utc()})")
    for sp in specs:
        if len(lines[sp["icao"]]) - 1 != expected_rows:
            raise SystemExit(f"STOP: {sp['icao']} has {len(lines[sp['icao']]) - 1} rows, the plan {expected_rows}")
    return lines, tallies, obs_stats, expected_rows, split


def build_all(specs, log=print):
    out = {}
    for hs, (hours, main_dir, prior_dir) in HOURSETS.items():
        log(f"hours {hours[0]} to {hours[1]}:")
        out[hs] = build(specs, hours, main_dir, prior_dir, log=log)
    return out


def check_dev_tables(label):
    """F138's and F147's two files used by --equiv, and F138's six, unchanged."""
    s104.check_f138(label)
    bad = [st for st, h in F147_TABLES.items() if p91.sha256_file(STAGEC / s104.table_name(st)) != h]
    print(f"F147's EGLC and KRNO files, SHA-256 equal to session 104's meta ({label}): {not bad} {bad or ''}")
    if bad:
        raise SystemExit("STOP: an F147 table file differs")


def check_inputs():
    s104.check_pull_25(verbose=False)
    s96.check_pull_files(verbose=False)
    print("pull files (both pulls) equal to their inventories: True")


def empty_counts(tt):
    emp = {}
    for t in tt.values():
        for k, v in t["empty"].items():
            emp[k] = emp.get(k, 0) + v
    return emp


def print_counts(built, specs):
    print("\nper airport and file: rows against the plan; complete-case rows valid before / from 2024-08-01 "
          "(counts only); no observation; whole file; empty cells by column and reason")
    for sp in specs:
        ic = sp["icao"]
        for hs in HOURSETS:
            lines, tallies, ostats, n_plan, split = built[hs]
            tt = tallies[ic]
            rows = sum(t["rows"] for t in tt.values())
            comp = sum(t["complete"] for t in tt.values())
            print(f"  {claim_name(ic, hs)}: rows {rows} (plan {n_plan}, equal {rows == n_plan}); complete case {comp} "
                  f"= before {split[ic]['before']} + from {split[ic]['from']}; no observation "
                  f"{sum(t['no_obs'] for t in tt.values())}; uses whole file {sum(t['whole'] for t in tt.values())}; "
                  f"obs ties {ostats[ic]['ties']}")
            for (col, why), v in sorted(empty_counts(tt).items()):
                print(f"      {col} empty, {why}: {v}")
        s = built["f000_024"][2][ic]
        print(f"      observations ({sp['station']}): reports read {s['rows']}, no usable tmpc {s['no_temp']} "
              f"(non-finite {s['nonfinite']}), repeated timestamps skipped {s['duplicates']}, file order sorted "
              f"{s['file_order_sorted']}")


# ------------------------------------------------------------------ modes

def run_equiv(args):
    print(f"SESSION 106 --equiv (offline), {now_utc()}: the new build on EGLC's and RNO's own inputs, 2022-01")
    check_dev_tables("before")
    specs = [dev_spec("EGLC"), dev_spec("RNO")]
    for sp in specs:
        print(f"  {sp['station']} ({sp['icao']}): grid point {sp['p']['lat']}, {sp['p']['lon']}; constant "
              f"{sp['a']['correction_c']}; observation files {[f.name for f in s96.obs_files(sp['station'])]}")
    ok = True
    for hs, (hours, main_dir, prior_dir) in HOURSETS.items():
        lines = build(specs, hours, main_dir, prior_dir, ["2022-01"], log=lambda *a: None)[0]
        for sp in specs:
            st = sp["station"]
            path = STAGEC / (s96.table_name(st) if hs == "f000_024" else s104.table_name(st))
            with gzip.open(path, "rt", newline="") as f:
                old = [ln.rstrip("\n") for ln in f]
            old_rows = [old[0]] + [ln for ln in old[1:] if ln.split(",", 2)[1].startswith("2022-01")]
            new = lines[sp["icao"]]
            same = old_rows == new
            diff = sum(1 for a, b in zip(old_rows, new) if a != b)
            print(f"  hours {hours[0]}-{hours[1]} {st}: rebuilt rows {len(new) - 1}; {path.name} rows with a 2022-01 "
                  f"cycle {len(old_rows) - 1}; header equal {old_rows[0] == new[0]}; lines differing {diff}; "
                  f"byte-equal {same}")
            ok &= same
    check_dev_tables("after")
    print("EQUIVALENCE: PASS" if ok else "EQUIVALENCE: FAIL, STOP")
    return 0 if ok else 1


def run_build(args):
    t0 = time.time()
    print(f"SESSION 106 --build (offline), start {now_utc()}; out {STAGEC}")
    there = [p.name for p in claim_targets() if p.exists() or p.with_name(p.name + ".partial").exists()]
    if there:
        raise SystemExit(f"STOP: already exists: {there}")
    check_dev_tables("before")
    check_inputs()
    specs = claim_specs()
    for sp in specs:
        print(f"  {sp['icao']}: station (IEM id) {sp['station']}; position {sp['p']['lat']}, {sp['p']['lon']}; "
              f"height_diff_m {sp['height_diff_m']}; elevation constant {sp['a']['correction_c']}")
    built = build_all(specs)
    print()
    for sp in specs:
        for hs in HOURSETS:
            lines = built[hs][0][sp["icao"]]
            data = s96.table_bytes(lines)
            path = STAGEC / claim_name(sp["icao"], hs)
            s96.write_new_file(path, data)
            print(f"  {path.name}: rows {len(lines) - 1}, bytes {len(data):,}, SHA-256 {s96.sha256_bytes(data)}")
    print_counts(built, specs)
    check_dev_tables("after")
    print(f"leftover partial files: {sorted(p.name for p in STAGEC.glob('*.partial')) or 'none'}")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


def training_sanity(rows):
    """D100.9(b). rows: (valid time, observation, temperature_grib_c). Refuses any
    row valid on or after 2024-08-01T00:00. Returns (n, mean error obs minus
    forecast, MAE)."""
    for v, _, _ in rows:
        if v >= CUTOFF:
            raise s96.GuardError(f"row valid {v:%Y-%m-%dT%H:%M} is not before {CUTOFF:%Y-%m-%dT%H:%M}")
    err = [o - f for _, o, f in rows]
    n = len(err)
    return n, sum(err) / n, sum(abs(e) for e in err) / n


def training_rows(path):
    """Complete-case rows at leads 3 to 24 valid before the cutoff. A row's valid
    time and lead are read first; a row valid on or after the cutoff is skipped
    before any other cell is read, and counted."""
    rows, skipped = [], 0
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != s96.COLUMNS:
            raise SystemExit(f"STOP: {path.name} header")
        ci = {c: i for i, c in enumerate(head)}
        for r in rd:
            valid = s104.s97_time(r[ci["valid_utc"]])
            if valid >= CUTOFF:
                skipped += 1
                continue
            if not 3 <= int(r[ci["lead"]]) <= 24 or r[ci["complete_case"]] != "true":
                continue
            rows.append((valid, float(r[ci["obs_tmpc"]]), float(r[ci["temperature_grib_c"]])))
    return rows, skipped


def run_sanity(args):
    print(f"SESSION 106 --sanity (offline), {now_utc()}: D100.9(b), training rows only (valid before "
          f"{CUTOFF:%Y-%m-%dT%H:%M} UTC), leads 3 to 24, complete case; raw GFS = temperature_grib_c")
    try:
        training_sanity([(CUTOFF, 0.0, 0.0)])
        print("refusal test (one made-up row valid 2024-08-01T00:00): NOT REFUSED, STOP")
        return 1
    except s96.GuardError as e:
        print(f"refusal test (one made-up row valid 2024-08-01T00:00): refused ({e})")
    stop = False
    for ic in CLAIM:
        path = STAGEC / claim_name(ic, "f000_024")
        rows, skipped = training_rows(path)
        n, me, mae = training_sanity(rows)
        gross = abs(me) > 8 or abs(mae) > 8
        stop |= gross
        print(f"  {ic}: n {n}; mean error (obs minus raw GFS) {me:+.4f}; MAE {mae:.4f}; rows skipped on valid time "
              f"(not read) {skipped}; gross (above 8 degrees C) {gross}")
    print("SANITY: STOP (a gross value)" if stop else "SANITY: PASS (no value above 8 degrees C in size)")
    return 1 if stop else 0


def run_records(args):
    t0 = time.time()
    print(f"SESSION 106 --records (offline), start {now_utc()}")
    p91.check_out_free([COUNTS_OUT, META_OUT])
    check_dev_tables("before")
    check_inputs()
    specs = claim_specs()
    built = build_all(specs, log=lambda *a: None)
    files = []
    for sp in specs:
        for hs in HOURSETS:
            lines = built[hs][0][sp["icao"]]
            data = s96.table_bytes(lines)
            name = claim_name(sp["icao"], hs)
            same = data == (STAGEC / name).read_bytes()
            print(f"in-memory rebuild of {name} byte-equal to the file: {same}")
            if not same:
                raise SystemExit("STOP: the rebuild differs from the written table")
            files.append((name, len(lines) - 1, len(data), s96.sha256_bytes(data)))
    nz = [sp for sp in specs if sp["icao"] == "NZWN"]
    tmp = Path(tempfile.mkdtemp(prefix="session106_nzwn_"))
    same = True
    try:
        for hs, (hours, main_dir, prior_dir) in HOURSETS.items():
            l2 = build(nz, hours, main_dir, prior_dir, log=lambda *a: None)[0]
            s96.write_new_file(tmp / claim_name("NZWN", hs), s96.table_bytes(l2["NZWN"]))
            eq = (tmp / claim_name("NZWN", hs)).read_bytes() == (STAGEC / claim_name("NZWN", hs)).read_bytes()
            print(f"NZWN rebuilt alone into {tmp}: byte-equal to {claim_name('NZWN', hs)}: {eq}")
            same &= eq
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"temporary directory deleted: {not tmp.exists()}")
    if not same:
        raise SystemExit("STOP: the NZWN rebuild differs")
    head = ["station", "icao", "file", "lead", "rows"]
    for col in s96.GRIB_COLS:
        head += [f"{col}_empty_{r.replace(' ', '_')}" for r in s96.REASONS]
    head += ["no_observation", "uses_whole_file", "complete_case"]
    rows = []
    for sp in specs:
        for hs, (hours, _, _) in HOURSETS.items():
            tallies = built[hs][1][sp["icao"]]
            for n in range(hours[0], hours[1] + 1):
                t = tallies[n]
                r = [sp["station"], sp["icao"], claim_name(sp["icao"], hs), n, t["rows"]]
                for col in s96.GRIB_COLS:
                    r += [t["empty"].get((col, why), 0) for why in s96.REASONS]
                r += [t["no_obs"], t["whole"], t["complete"]]
                rows.append(r)
    s96.write_new_file(COUNTS_OUT, ("\n".join(",".join(str(x) for x in r) for r in [head] + rows) + "\n").encode())
    print(f"wrote {COUNTS_OUT.relative_to(ROOT)}: {len(rows)} rows, {len(head)} columns, "
          f"SHA-256 {p91.sha256_file(COUNTS_OUT)}")
    print_counts(built, specs)
    meta = [
        "Provenance (SPEC 2.3). Do not edit the data files.",
        "",
        "files       : stagec_claim_f000_024_<ICAO>.csv.gz and stagec_claim_f025_048_<ICAO>.csv.gz, two per claim airport",
        "purpose     : session 106 (DECISIONS D100.3(a)): stage C's tables for the six claim airports (D82.7): every GFS",
        "              cycle in the two pulls and every forecast hour 0 to 24 and 25 to 48, D88.5's features rebuilt",
        "              from the stored grid values and D88.7's hourly observation, by session 96's make_row and",
        "              session 104's load_values (imported unchanged). No model, no score.",
        f"where       : {STAGEC.name}/ beside the repository (not tracked, D88.8), next to F138's and F147's files,",
        "              which are unchanged. Rebuilt exactly by scripts/session106_claim_table.py --build.",
        f"written by  : scripts/session106_claim_table.py --build; this meta by --records at {now_utc()}",
        f"script sha256: {p91.sha256_file(Path(__file__).resolve())}",
        "",
        "table files :",
    ]
    meta += [f"  {name}  rows {n:,}  bytes {b:,}  sha256 {sha}" for name, n, b, sha in files]
    meta += [
        f"  rows per airport: hours 0 to 24 {built['f000_024'][3]:,}, hours 25 to 48 {built['f025_048'][3]:,} "
        "(session91_grib_pull.py's plan)",
        "  columns, column order, row rules, gzip and number format exactly as F138's and F147's files; rows in",
        "  cycle, then lead order. The station column holds the IEM id (ORD for KORD).",
        "",
        "elevation constants (D100.3(b): round(7.429 x height_diff_m / 1000, 4), height_diff_m from session90_airports.csv):",
    ]
    meta += [f"  {sp['icao']}  height_diff_m {sp['height_diff_m']!r}  correction_c {sp['a']['correction_c']}" for sp in specs]
    meta += [
        "",
        "time zones (session90_airports.csv, for D100.3(e)):",
        "  " + "; ".join(f"{sp['icao']} {sp['time_zone']}" for sp in specs),
        "",
        "inputs      :",
        f"  {s104.INVENTORY_25.relative_to(ROOT)} sha256 {p91.sha256_file(s104.INVENTORY_25)} (MLwx-pull-f025-048/)",
        f"  {s96.INVENTORY.relative_to(ROOT)} sha256 {p91.sha256_file(s96.INVENTORY)} (MLwx-pull/)",
        "  (every pull file checked against its inventory before the build)",
        f"  {p91.POSITIONS.relative_to(ROOT)} sha256 {p91.sha256_file(p91.POSITIONS)}",
        f"  {AIRPORTS_CSV.relative_to(ROOT)} sha256 {p91.sha256_file(AIRPORTS_CSV)}",
        "  observation files (session 90, F132.4):",
    ]
    meta += [f"  {f.relative_to(ROOT)} sha256 {p91.sha256_file(f)}" for sp in specs for f in s96.obs_files(sp["station"])]
    meta += ["imported code:"]
    for name in ("session104_stagec_table_f025_048.py", "session96_stagec_table.py", "session86_forward_build.py",
                 "session92_verify_chunk.py", "session91_grib_pull.py"):
        meta.append(f"  scripts/{name} sha256 {p91.sha256_file(SCRIPTS / name)}")
    meta.append(f"counts      : {COUNTS_OUT.relative_to(ROOT)} sha256 {p91.sha256_file(COUNTS_OUT)}")
    meta.append(f"versions    : {s96.versions()}")
    s96.write_new_file(META_OUT, ("\n".join(meta) + "\n").encode())
    print(f"wrote {META_OUT.relative_to(ROOT)}: SHA-256 {p91.sha256_file(META_OUT)}")
    check_dev_tables("after")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("equiv", "build", "sanity", "records"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    fn = {"equiv": run_equiv, "build": run_build, "sanity": run_sanity, "records": run_records}
    try:
        return fn[next(k for k in fn if getattr(a, k))](a)
    except (s96.GuardError, p91.GuardError) as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
