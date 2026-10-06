"""Session 96: the stage C development table and its gate (DECISIONS D88).

For each development airport (EGLC, LFPG, DSM, YSDU, RNO, KSFO), every GFS
cycle in the pull's plan and every forecast hour 0 to 24, it rebuilds the
record's features from the stored grid values of the stage C pull
(MLwx-pull/, F137) and pairs the hourly observation at the valid time.
It fits no model and computes no score. Offline: no network call.

Modes (exactly one):
  --inputs       Step 3. Checks the 195 pull files against the committed
                 inventory (name, bytes, SHA-256), reports what the
                 observation files' .meta.txt record, and reads the six
                 development airports' grid points and weights.
  --test-rt      Step 4. Tests the new R and T arithmetic on its own, on
                 made-up numbers only.
  --build        Step 5. Builds the table and writes one gzip file per airport
                 into --out (default MLwx-stagec/ beside the repo). Refuses if
                 --out exists. --station limits the build to one airport (used
                 for the repeatability check, Step 7.3).
  --gate         Step 6. Reads the written table back and compares it with
                 data/processed/session81_training_set.csv at EGLC and LFPG 12z
                 lead 24 and DSM 18z lead 24, exact equality.
  --records      Step 7.1 and 7.2. Rebuilds the table in memory, checks it is
                 byte-equal to the files in --out, and writes the counts file
                 and the table's meta file under data/processed/.
  --guard-check  Step 7.4. Shows the 2026-27 guards refuse, with no data.

What is imported, so it stays identical to the gated record code:
  from scripts/session86_forward_build.py (F128): load_airports (SPEC 3.4 and
  the params CSVs), year_fraction, window_start, parse_reports, pair_nearest,
  pair_historical, derive (only in --test-rt, as the reference).
  from scripts/session92_verify_chunk.py and, through it,
  scripts/session91_grib_pull.py (F134, F137): the plan (all_months,
  month_cycles, plan_chunk), FIELDS, the column lists, the statuses,
  read_positions, DEV, bilinear_stored (bilinear on the four stored values)
  and derive (the instantaneous columns, as F137.8's gate used it).
Written new (D88.5): R and T at every lead (r_inputs, r_raw, r_value,
t_inputs, t_value), and the raw columns t2m_raw, dew_point_2m, t850,
tmax2m_c and tmin2m_c, each one rounding of a decoded value as SPEC 8.8 G4
and G7 and D88.5(e) state it.

SPEC 8.7 build requirements: (1) the observation is the nearest usable
report (D88.7); (2) a non-finite value is never used and never filled;
(3) each message's checks were made by the pull and its verifier, and its
status is read here; (4) row counts are compared with the plan's full count;
(5) every output file is new: written to a temporary name and linked to its
final name, which never overwrites.

Hard limits, in code: no valid time after 2026-07-31T23:00 UTC is built, and
no observation after 2026-07-31T23:59 UTC is read (check_valid_time,
check_obs_time). Only the six development airports' rows are used from the
points files, and only their observation files are opened.
"""

import argparse
import bisect
import csv
import datetime as dt
import gzip
import hashlib
import io
import math
import os
import sys
import time
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True

import session86_forward_build as s86  # noqa: E402  (its libomp shim may re-run this script once)
import session92_verify_chunk as s92  # noqa: E402

p91 = s92.p91

ROOT = Path(__file__).resolve().parent.parent
PULL_DIR = ROOT.parent / "MLwx-pull"
OUT_DEFAULT = ROOT.parent / "MLwx-stagec"
INVENTORY = ROOT / "data" / "processed" / "session95_pull_inventory.csv"
TRAINING_SET = ROOT / "data" / "processed" / "session81_training_set.csv"
COUNTS_OUT = ROOT / "data" / "processed" / "session96_stagec_dev_counts.csv"
META_OUT = ROOT / "data" / "processed" / "session96_stagec_dev_table.meta.txt"
RAW = ROOT / "data" / "raw"
OBS_PIECES = ["2021-03-24_2021-12-31", "2022-01-01_2022-12-31", "2023-01-01_2023-12-31",
              "2024-01-01_2024-12-31", "2025-01-01_2025-12-31", "2026-01-01_2026-07-31"]

LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)     # nothing valid after this is built
LAST_OBS = dt.datetime(2026, 7, 31, 23, 59)      # no observation after this is read
HOURS = (0, 24)
TOL = dt.timedelta(minutes=s86.TOL_MIN)

STATIONS = list(p91.DEV)                         # SPEC 3.4 station codes, in SPEC order
DEV_ICAOS = set(p91.DEV.values())
OK_STATUSES = s92.OK_STATUSES                    # "ok" and "ok (whole file)"

GRIB_COLS = ["temp", "temperature_grib_c", "t2m_raw", "cloud_cover", "wind_speed_10m", "dew_point_2m", "t850",
             "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
             "pressure_tendency_3h_hpa", "season_sin", "season_cos", "tmax2m_c", "tmin2m_c"]
COLUMNS = (["station", "cycle_utc", "cycle_hour", "lead", "valid_utc"] + GRIB_COLS
           + ["obs_tmpc", "obs_time_utc", "uses_whole_file", "complete_case"])
G15 = list(s86.G15)                              # SPEC 8.8 G15, record order
REASONS = ["absent by design", "lead too short", "outside pull window", "message not ok"]

# The pull field each instantaneous column needs, at the row's own lead.
INST_NEEDS = {"temp": ["t2m"], "temperature_grib_c": ["t2m"], "t2m_raw": ["t2m"], "cloud_cover": ["tcdc"],
              "wind_speed_10m": ["u10", "v10"], "dew_point_2m": ["d2m"], "t850": ["t850"],
              "dewpoint_depression_t2m_floored": ["t2m", "d2m"], "lapse_rate_t2_t850": ["t2m", "t850"],
              "tmax2m_c": ["tmax2m"], "tmin2m_c": ["tmin2m"], "season_sin": [], "season_cos": []}
# derive's input names (session91_grib_pull.py derive, from session86 l.559-594) for each pull field.
DERIVE_KEY = {"t2m": "tmp2m", "tcdc": "tcdc", "u10": "ugrd10m", "v10": "vgrd10m", "t850": "t850", "d2m": "dpt2m",
              "prmsl": "prmsl"}
PLACEHOLDER = 0.0     # given to derive for an input whose output is not used; never reaches the table


class GuardError(Exception):
    """A 2026-27 guard fired. The run stops."""


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def check_valid_time(valid):
    if valid > LAST_VALID:
        raise GuardError(f"valid time {valid:%Y-%m-%dT%H:%M} is after {LAST_VALID:%Y-%m-%dT%H:%M} UTC")


def check_obs_time(t):
    if t > LAST_OBS:
        raise GuardError(f"observation at {t:%Y-%m-%dT%H:%M} is after {LAST_OBS:%Y-%m-%dT%H:%M} UTC")


def versions():
    import numpy as np
    import eccodes as ec
    return (f"python {sys.version.split()[0]}; numpy {np.__version__}; eccodes (Python) {ec.__version__}; "
            f"ecCodes library {ec.codes_get_api_version()}")


# ------------------------------------------------------------------ R and T (D88.5(b), (c)), written new

def r_inputs(n):
    """The forecast hours whose DSWRF average R at lead n needs, or None when R
    does not exist (leads 0 and 1). W = 6 x floor((n-1)/6) (window_start)."""
    if n < 2:
        return None
    w = s86.window_start(n)
    if n - w >= 2:
        return [n] if n - 2 == w else [n, n - 2]
    return [n, w, w - 1]


def r_raw(n, a):
    """D88.5(b), unrounded. a maps forecast hour to A(hour), the GFS average
    over (W, hour]. Works on floats and on exact fractions."""
    w = s86.window_start(n)
    if n - w >= 2:
        if n - 2 == w:
            return a[n]                                   # R = A(N) at leads 2, 8, 14, 20
        return ((n - w) * a[n] - (n - 2 - w) * a[n - 2]) / 2
    return (a[n] + 6 * a[w] - 5 * a[w - 1]) / 2          # N - W = 1: leads 7, 13, 19


def r_value(n, a):
    """R as stored: rounded to 3 decimals, as the record stores dswrf_2h_wm2."""
    return round(r_raw(n, a), 3)


def t_inputs(n):
    """The forecast hours T at lead n needs, or None (leads 0 to 2)."""
    return None if n < 3 else [n, n - 3]


def t_value(n, p):
    """D88.5(c): sea level pressure at n minus that at n-3, in hPa, from the two
    rounded pressures, as the record does. p maps forecast hour to PRMSL in Pa."""
    msl = round(p[n] / 100.0, 3)
    m3 = round(p[n - 3] / 100.0, 3)
    return round(msl - m3, 3)


# ------------------------------------------------------------------ inputs

def obs_files(st):
    return [RAW / f"iem_asos_{st}_{piece}_routine.csv" for piece in OBS_PIECES]


def check_pull_files(verbose=True):
    """Step 3.1: every file in MLwx-pull/ against the inventory."""
    with open(INVENTORY, newline="") as f:
        inv = list(csv.DictReader(f))
    have = sorted(p.name for p in PULL_DIR.iterdir())
    want = sorted(r["asset"] for r in inv)
    bad = []
    if have != want:
        bad.append(f"file names differ: extra {sorted(set(have) - set(want))}, missing {sorted(set(want) - set(have))}")
    for r in inv:
        p = PULL_DIR / r["asset"]
        if not p.exists():
            continue
        size, sha = p.stat().st_size, p91.sha256_file(p)
        if size != int(r["bytes"]) or sha != r["sha256"]:
            bad.append(f"{r['asset']}: bytes {size} vs {r['bytes']}, sha256 equal {sha == r['sha256']}")
    if verbose:
        print(f"pull files: {len(have)} in {PULL_DIR}; inventory rows {len(inv)}; "
              f"names, bytes and SHA-256 all equal: {not bad}")
    if bad:
        for b in bad:
            print("  DIFFERENCE:", b)
        raise SystemExit("STOP: a pull file differs from the inventory")
    return inv


def load_positions():
    """Step 3.3: the six development airports' grid points and weights, read as
    the verifier's --gate does, and checked against SPEC 3.4's grid point."""
    airports = s86.load_airports()
    a91 = p91.load_airports()
    positions, geom = p91.read_positions()
    pos = {p["icao"]: p for p in positions}
    out = {}
    for st in STATIONS:
        a = airports[st]
        if (a91[st]["grid_lat"], a91[st]["grid_lon"], a91[st]["correction_c"], a91[st]["lead"]) != \
                (a["grid_lat"], a["grid_lon"], a["correction_c"], a["lead"]):
            raise SystemExit(f"STOP: session 86's and session 91's parsing differ at {st}")
        p = pos[p91.DEV[st]]
        p["lat"], p["lon"] = float(p["lat_used"]), float(p["lon_used"])
        p["pts"] = [(float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"])) for k in (1, 2, 3, 4)]
        if (p["lat"], p["lon"]) != (a["grid_lat"], a["grid_lon"]) or p["role"] != "development":
            raise SystemExit(f"STOP: {st}'s position in the positions file is not SPEC 3.4's grid point")
        out[st] = p
    return airports, out, geom


def run_inputs(args):
    print(f"SESSION 96 --inputs (offline), {now_utc()}")
    print("\n3.1 pull files against data/processed/session95_pull_inventory.csv "
          f"(SHA-256 {p91.sha256_file(INVENTORY)})")
    check_pull_files()
    print("\n3.2 observation files (only the six development airports' files are opened):")
    none = 0
    for st in STATIONS:
        for f in obs_files(st):
            meta = Path(str(f) + ".meta.txt").read_text()
            has = "sha256" in meta.lower() or "sha-256" in meta.lower()
            none += not has
            print(f"  {f.name}: SHA-256 {p91.sha256_file(f)}; its .meta.txt records a SHA-256: {has}")
    print(f"observation files whose .meta.txt records no SHA-256: {none} of {len(STATIONS) * len(OBS_PIECES)}")
    print("\n3.3 grid points and weights (positions file "
          f"{p91.POSITIONS.name}, SHA-256 {p91.sha256_file(p91.POSITIONS)}):")
    airports, pos, geom = load_positions()
    print(f"  grid geometry: {geom}")
    for st in STATIONS:
        p, a = pos[st], airports[st]
        pts = "; ".join(f"index {p[f'p{k}_index']} ({p[f'p{k}_lat']}, {p[f'p{k}_lon']}) weight {p[f'p{k}_weight']}"
                        for k in (1, 2, 3, 4))
        print(f"  {st} ({p['icao']}): position used {p['lat_used']}, {p['lon_used']} = SPEC 3.4 grid point; "
              f"elevation constant {a['correction_c']:+.4f} degC; record lead {a['lead']}\n      {pts}")
    return 0


# ------------------------------------------------------------------ --test-rt (Step 4)

def run_test_rt(args):
    print(f"SESSION 96 --test-rt (offline, made-up numbers only), {now_utc()}")
    airports = s86.load_airports()
    ok_all = True

    def report(label, good):
        nonlocal ok_all
        ok_all &= good
        print(f"  [{'PASS' if good else 'FAIL'}] {label}")

    print("\n4.1 record leads: the new R against session 86's derive (F128.3), same made-up inputs")
    print(f"  r_inputs(24) = {r_inputs(24)} (W = {s86.window_start(24)}); r_inputs(26) = {r_inputs(26)} "
          f"(W = {s86.window_start(26)})")
    cases = [(612.375, 488.1640625, 101325.5, 101412.75), (0.0, 0.0, 99876.0, 99912.25),
             (35.5, 120.8125, 102003.875, 101998.5), (803.44, 790.2, 100512.0, 100649.6875),
             (5.0625, 0.25, 98765.4321, 98760.0)]
    base = {"tmp2m": 285.4, "tcdc": 37.5, "ugrd10m": 3.2, "vgrd10m": -1.7, "t925": 280.1, "t850": 276.9,
            "t700": 268.3, "rh2m": 71.0, "dpt2m": 280.2, "spfh2m": 0.0061, "pres_sfc": 100800.0}
    d = dt.date(2023, 7, 13)
    for a24, a22, p24, p21 in cases:
        got = dict(base, dswrf=a24, dswrf_m2=a22, prmsl=p24, prmsl_m3=p21)
        ref = s86.derive(airports["EGLC"], d, got)
        new_r = r_value(24, {24: a24, 22: a22})
        new_t = t_value(24, {24: p24, 21: p21})
        print(f"  lead 24 (EGLC's derive): A(24) {a24!r}, A(22) {a22!r}, PRMSL(24) {p24!r} Pa, PRMSL(21) {p21!r} Pa")
        report(f"R: new {new_r!r}, derive {ref['dswrf_2h_wm2']!r}, identical float "
               f"{new_r == ref['dswrf_2h_wm2'] and type(new_r) is type(ref['dswrf_2h_wm2'])}",
               new_r == ref["dswrf_2h_wm2"])
        report(f"T (4.3): new {new_t!r}, derive {ref['pressure_tendency_3h_hpa']!r}",
               new_t == ref["pressure_tendency_3h_hpa"])
    for a26 in (612.375, 0.0, 803.44):
        got = dict(base, dswrf=a26, prmsl=101000.0, prmsl_m3=101010.0)
        ref = s86.derive(airports["YSDU"], d, got)
        new_r = r_value(26, {26: a26})
        report(f"lead 26 (native window, YSDU's derive): A(26) {a26!r}; new R {new_r!r} = A(26) rounded "
               f"{new_r == round(a26, 3)}; derive {ref['dswrf_2h_wm2']!r}", new_r == ref["dswrf_2h_wm2"]
               and new_r == round(a26, 3))
    report("lead 26: r_raw returns A(26) itself (no arithmetic)", r_raw(26, {26: 803.44}) == 803.44)

    print("\n4.2 exact algebra (fractions): a made-up hourly radiation series h(1..24) for one cycle")
    h = {k: Fraction((37 * k * k + 11 * k) % 997, 7) + Fraction(k, 3) for k in range(1, 25)}
    print("  h = " + ", ".join(f"{k}:{h[k]}" for k in range(1, 25)))
    a = {}
    for n in range(1, 25):
        w = s86.window_start(n)
        a[n] = sum(h[k] for k in range(w + 1, n + 1)) / (n - w)   # GFS: the average over (W, N]
    bad = []
    for n in range(2, 25):
        true = (h[n - 1] + h[n]) / 2
        got = r_raw(n, {k: a[k] for k in r_inputs(n)})
        if got != true or not isinstance(got, Fraction):
            bad.append((n, got, true))
    report(f"R recovers the true 2-hour mean (h(N-1) + h(N)) / 2 exactly at every lead 2 to 24: "
           f"{23 - len(bad)} of 23" + (f"; wrong at {bad}" if bad else ""), not bad)
    kinds = {}
    for n in range(2, 25):
        w = s86.window_start(n)
        kinds.setdefault("N-W=1 (3 terms)" if n - w == 1 else "N-2=W (A(N))" if n - 2 == w else "N-W>=3 (2 terms)",
                         []).append(n)
    print("  leads by form: " + "; ".join(f"{k}: {v}" for k, v in kinds.items()))
    report(f"R missing at leads 0 and 1: r_inputs(0) {r_inputs(0)}, r_inputs(1) {r_inputs(1)}",
           r_inputs(0) is None and r_inputs(1) is None)
    report(f"T missing at leads 0 to 2: {[t_inputs(n) for n in (0, 1, 2)]}; t_inputs(3) {t_inputs(3)} (uses f000)",
           all(t_inputs(n) is None for n in (0, 1, 2)) and t_inputs(3) == [3, 0])
    print("\nALL STEP 4 TESTS PASSED" if ok_all else "\nA STEP 4 TEST FAILED: STOP")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ observations

def load_obs(st):
    """The six yearly routine files of one development airport. Every report's
    time is checked against the limit before any temperature is read (as
    session 86's fetch_iem does). Reports are parsed by session 86's
    parse_reports (G2: M, blank, T, None and non-finite are unusable). A
    repeated timestamp keeps the first report, as session 86's build_rows
    does, and is counted. Returns (sorted times, values, file-order list, stats)."""
    stats = {"rows": 0, "no_temp": 0, "nonfinite": 0, "duplicates": 0}
    by_time, file_order = {}, []
    for f in obs_files(st):
        text = f.read_text()
        for r in csv.DictReader(io.StringIO(text)):
            check_obs_time(dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M"))
        for t, v in s86.parse_reports(text, st, stats):
            file_order.append((t, v))
            if t in by_time:
                stats["duplicates"] += 1
                continue
            by_time[t] = v
    times = sorted(by_time)
    stats["file_order_sorted"] = all(file_order[i][0] <= file_order[i + 1][0] for i in range(len(file_order) - 1))
    return times, [by_time[t] for t in times], file_order, stats


def nearest_obs(times, vals, valid, cache, stats):
    """D88.7: session 86's pair_nearest on the reports within 15 minutes
    (inclusive). Passing only those reports gives the same result as passing
    all, since pair_nearest keeps only reports within 15 minutes and sorts them."""
    if valid in cache:
        return cache[valid]
    i, j = bisect.bisect_left(times, valid - TOL), bisect.bisect_right(times, valid + TOL)
    res = s86.pair_nearest(list(zip(times[i:j], vals[i:j])), valid)
    stats["ties"] += res["tie"]
    cache[valid] = (res["obs"], res["report_time"])
    return cache[valid]


# ------------------------------------------------------------------ the build

def fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def read_month(month):
    """One month's manifest statuses and the development airports' points rows.
    Other airports' rows are skipped on the icao field; none of their values is
    converted or kept."""
    pts_path, man_path, _ = s92.the_files(PULL_DIR, month)
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
            if r[3] not in DEV_ICAOS:
                continue
            k = (r[0], int(r[1]), r[3])
            if k in points:
                raise SystemExit(f"STOP: duplicate points key {k}")
            points[k] = r
    return status, points


def build(stations, out_lines, tallies, log=print):
    """Builds every row for the given stations. out_lines[st] collects the CSV
    text lines; tallies[st] the counts. Returns the obs stats."""
    airports, pos, _ = load_positions()
    col_i = {c: i for i, c in enumerate(p91.POINT_COLS)}
    obs, obs_stats, caches = {}, {}, {}
    for st in stations:
        times, vals, _, stats = load_obs(st)
        stats["ties"] = 0
        obs[st], obs_stats[st], caches[st] = (times, vals), stats, {}
        out_lines[st] = [",".join(COLUMNS)]
        tallies[st] = {}
    expected_rows = 0
    for y, m in p91.all_months():
        month = f"{y}-{m:02d}"
        plan = p91.plan_chunk(p91.month_cycles(y, m), HOURS)
        status, points = read_month(month)
        for cycle, fhs in plan:
            c_iso = p91.iso(cycle)
            in_plan = set(fhs)
            expected_rows += len(fhs)
            for st in stations:
                a, p, icao = airports[st], pos[st], p91.DEV[st]
                # bilinear on the four stored values of every ok message of this cycle
                val, stat = {}, {}
                for fh in fhs:
                    r = points[(c_iso, fh, icao)]
                    if r[2] != p91.iso(cycle + dt.timedelta(hours=fh)):
                        raise SystemExit(f"STOP: valid_utc {r[2]} at {c_iso} f{fh:03d}")
                    for fname in p91.FIELD_NAMES:
                        s = status[(c_iso, fh, fname)]
                        stat[(fh, fname)] = s
                        cells = [r[col_i[f"{fname}_{k}"]] for k in (1, 2, 3, 4)]
                        if s in OK_STATUSES:
                            v4 = [float(x) for x in cells]
                            if not all(math.isfinite(x) for x in v4):
                                raise SystemExit(f"STOP: non-finite stored value at {c_iso} f{fh:03d} {fname}")
                            val[(fh, fname)] = p91.bilinear_stored(p, v4)
                        elif any(x != "" for x in cells):
                            raise SystemExit(f"STOP: a filled cell in a non-ok message at {c_iso} f{fh:03d} {fname}")
                for n in fhs:
                    out_lines[st].append(make_row(st, a, cycle, n, in_plan, val, stat, obs[st], caches[st],
                                                  obs_stats[st], tallies[st]))
        log(f"  {month}: {len(plan)} cycles, {sum(len(f) for _, f in plan)} rows per airport ({now_utc()})")
    for st in stations:
        n_rows = len(out_lines[st]) - 1
        if n_rows != expected_rows:
            raise SystemExit(f"STOP: {st} has {n_rows} rows, the plan {expected_rows}")
    return obs_stats, expected_rows


def make_row(st, a, cycle, n, in_plan, val, stat, obs_pair, cache, ostats, tally):
    valid = cycle + dt.timedelta(hours=n)
    check_valid_time(valid)
    used, reason, out = set(), {}, {}

    def need(fields_at):
        """None if every (hour, field) is available; else the empty reason."""
        for fh, fname in fields_at:
            if fh not in in_plan:
                return "outside pull window"
        for fh, fname in fields_at:
            if stat[(fh, fname)] == "absent by design":
                return "absent by design"
        for fh, fname in fields_at:
            if stat[(fh, fname)] not in OK_STATUSES:
                return "message not ok"
        return None

    # instantaneous columns: session 91's derive (as F137.8's gate), on the row's own lead
    got = {}
    for fname, key in DERIVE_KEY.items():
        got[key] = val.get((n, fname), PLACEHOLDER)
    got.update({"prmsl_m3": PLACEHOLDER, "dswrf": PLACEHOLDER, "dswrf_m2": PLACEHOLDER})
    der = p91.derive(a, valid.date(), got)
    corr = a["correction_c"]
    for col, fields in INST_NEEDS.items():
        why = need([(n, f) for f in fields])
        if why:
            reason[col] = why
            out[col] = None
            continue
        used.update((n, f) for f in fields)
        if col in ("temp", "temperature_grib_c"):
            out[col] = der["temperature_grib_c"]
        elif col == "t2m_raw":
            out[col] = round(der["temperature_grib_c"] - corr, 3)          # SPEC 8.8 G4
        elif col in ("cloud_cover", "wind_speed_10m", "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850"):
            out[col] = der[col]
        elif col == "dew_point_2m":
            out[col] = round(val[(n, "d2m")] - 273.15, 3)                    # SPEC 8.8 G7
        elif col == "t850":
            out[col] = round(val[(n, "t850")] - 273.15, 3)                   # SPEC 8.8 G7
        elif col in ("tmax2m_c", "tmin2m_c"):
            out[col] = round(val[(n, col[:6])] - 273.15, 3)                  # D88.5(e), no constant
        elif col == "season_sin":
            out[col] = math.sin(2 * math.pi * s86.year_fraction(valid.date()))
        elif col == "season_cos":
            out[col] = math.cos(2 * math.pi * s86.year_fraction(valid.date()))
    # R (D88.5(b))
    leads = r_inputs(n)
    why = "lead too short" if leads is None else need([(fh, "dswrf") for fh in leads])
    if why:
        reason["dswrf_2h_wm2"], out["dswrf_2h_wm2"] = why, None
    else:
        used.update((fh, "dswrf") for fh in leads)
        out["dswrf_2h_wm2"] = r_value(n, {fh: val[(fh, "dswrf")] for fh in leads})
    # T (D88.5(c))
    leads = t_inputs(n)
    why = "lead too short" if leads is None else need([(fh, "prmsl") for fh in leads])
    if why:
        reason["pressure_tendency_3h_hpa"], out["pressure_tendency_3h_hpa"] = why, None
    else:
        used.update((fh, "prmsl") for fh in leads)
        out["pressure_tendency_3h_hpa"] = t_value(n, {fh: val[(fh, "prmsl")] for fh in leads})
    for col in GRIB_COLS:
        if out[col] is not None and not math.isfinite(out[col]):
            raise SystemExit(f"STOP: non-finite {col} at {st} {cycle} f{n:03d}")
    # observation (D88.7)
    o, o_time = nearest_obs(obs_pair[0], obs_pair[1], valid, cache, ostats)
    whole = any(stat[k] == p91.STATUS_WHOLE for k in used)
    complete = all(out[c] is not None for c in G15) and o is not None
    t = tally.setdefault(n, {"rows": 0, "no_obs": 0, "whole": 0, "complete": 0, "empty": {}})
    t["rows"] += 1
    t["no_obs"] += o is None
    t["whole"] += whole
    t["complete"] += complete
    for col, why in reason.items():
        t["empty"][(col, why)] = t["empty"].get((col, why), 0) + 1
    row = [st, p91.iso(cycle), cycle.hour, n, p91.iso(valid)] + [out[c] for c in GRIB_COLS] + \
          [o, None if o_time is None else p91.iso(o_time), whole, complete]
    return ",".join(fmt(v) for v in row)


def table_bytes(lines):
    """Equal content gives equal bytes: no file name and a zero timestamp in the gzip header."""
    return gzip.compress(("\n".join(lines) + "\n").encode("ascii"), compresslevel=9, mtime=0)


def write_new_file(path, data):
    """Temporary name first, then a hard link to the final name (never overwrites)."""
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.link(tmp, path)
    os.unlink(tmp)


def table_name(st):
    return f"stagec_dev_{p91.DEV[st]}.csv.gz"


def run_build(args):
    t0 = time.time()
    out = Path(args.out)
    print(f"SESSION 96 --build (offline), start {now_utc()}; out {out}")
    if out.exists():
        raise SystemExit(f"STOP: {out} already exists; not writing into it")
    stations = [args.station] if args.station else STATIONS
    if any(s not in STATIONS for s in stations):
        raise SystemExit(f"STOP: unknown station {args.station}")
    check_pull_files()
    lines, tallies = {}, {}
    ostats, n_plan = build(stations, lines, tallies)
    out.mkdir()
    print(f"\nplan rows per airport: {n_plan}; airports {len(stations)}; all rows {n_plan * len(stations)}")
    print(f"columns ({len(COLUMNS)}): {', '.join(COLUMNS)}")
    for st in stations:
        data = table_bytes(lines[st])
        path = out / table_name(st)
        write_new_file(path, data)
        s = ostats[st]
        print(f"  {path.name}: rows {len(lines[st]) - 1}, bytes {len(data):,}, SHA-256 {sha256_bytes(data)}")
        print(f"      observations: reports read {s['rows']}, no usable tmpc {s['no_temp']} (non-finite "
              f"{s['nonfinite']}), repeated timestamps skipped {s['duplicates']}, file order sorted "
              f"{s['file_order_sorted']}, tie hours (two equally near usable reports, earlier kept) {s['ties']}")
    print(f"leftover partial files: {sorted(p.name for p in out.glob('*.partial')) or 'none'}")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


# ------------------------------------------------------------------ --gate (Step 6)

def read_table(path):
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != COLUMNS:
            raise SystemExit(f"STOP: {path.name} header")
        return [dict(zip(head, r)) for r in rd]


def run_gate(args):
    print(f"SESSION 96 --gate (offline), {now_utc()}")
    out = Path(args.out)
    want = s86.expected_hash_from_decisions(r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`")
    have = p91.sha256_file(TRAINING_SET)
    print(f"training set SHA-256 {have}; F122.3 {want}; equal {have == want}")
    if have != want:
        raise SystemExit("STOP: the training set differs from F122.3")
    airports = s86.load_airports()
    gated = ["EGLC", "LFPG", "DSM"]
    print("gated: " + ", ".join(f"{st} {airports[st]['cycle']:02d}z lead {airports[st]['lead']}" for st in gated)
          + "; not gated: " + ", ".join(f"{st} (record lead {airports[st]['lead']}, not in this table)"
                                        for st in STATIONS if st not in gated))
    with open(TRAINING_SET, newline="") as f:
        rd = csv.DictReader(f)
        tcols = rd.fieldnames
        committed = {}
        for r in rd:
            if r["station"] in gated:
                committed[(r["station"], r["target_date"])] = r
    shared = [c for c in tcols if c in COLUMNS and c != "station"]
    print(f"columns compared (held by both): {shared}; plus the observation: committed obs_c against the "
          "record's pairing (pair_historical) of the same reports")
    total_fail = 0
    summary = {}
    for st in gated:
        a = airports[st]
        rows = read_table(out / table_name(st))
        table = {}
        for r in rows:
            if int(r["cycle_hour"]) == a["cycle"] and int(r["lead"]) == a["lead"]:
                v = dt.datetime.strptime(r["valid_utc"], "%Y-%m-%dT%H:%MZ")
                if v.hour != a["target_hour"]:
                    raise SystemExit(f"STOP: {st} valid hour {v.hour}")
                table[v.date().isoformat()] = r
        com = {d: r for (s, d), r in committed.items() if s == st}
        no_table = sorted(set(com) - set(table))
        no_com = sorted(set(table) - set(com))
        _, _, file_order, ostats = load_obs(st)
        if not ostats["file_order_sorted"]:
            raise SystemExit("STOP: observation file order is not sorted; the windowed historical pairing needs it")
        ftimes = [t for t, _ in file_order]
        res = {c: [0, 0] for c in shared + ["obs_c"]}
        mism, nearest_diff_report, nearest_diff_value = [], 0, 0
        for d in sorted(set(com) & set(table)):
            c, t = com[d], table[d]
            if int(c["target_hour"]) != a["target_hour"]:
                raise SystemExit("STOP: target hour")
            for col in shared:
                res[col][1] += 1
                if t[col] != "" and float(c[col]) == float(t[col]):
                    res[col][0] += 1
                else:
                    mism.append((d, col, c[col], t[col]))
            tgt = dt.datetime.fromisoformat(d) + dt.timedelta(hours=a["target_hour"])
            i = bisect.bisect_left(ftimes, tgt - dt.timedelta(minutes=30))
            j = bisect.bisect_right(ftimes, tgt + dt.timedelta(minutes=30))
            hist = s86.pair_historical(file_order[i:j], tgt)
            res["obs_c"][1] += 1
            if hist is not None and float(c["obs_c"]) == hist[1]:
                res["obs_c"][0] += 1
            else:
                mism.append((d, "obs_c (record pairing)", c["obs_c"], None if hist is None else repr(hist[1])))
            near_time = t["obs_time_utc"]
            hist_time = None if hist is None else p91.iso(hist[0])
            if near_time != (hist_time or ""):
                nearest_diff_report += 1
                if (t["obs_tmpc"] or None) is None or hist is None or float(t["obs_tmpc"]) != hist[1]:
                    nearest_diff_value += 1
        summary[st] = (len(com), len(table), len(set(com) & set(table)))
        print(f"\n{st} ({p91.DEV[st]}): committed rows {len(com)}; table rows at {a['cycle']:02d}z lead "
              f"{a['lead']} {len(table)}; compared {len(set(com) & set(table))}")
        print(f"  committed rows with no table row: {len(no_table)} {no_table or ''}")
        print(f"  table rows with no committed row: {len(no_com)} {no_com or ''}")
        print(f"  {'column':34s} {'compared':>8s} {'equal':>8s} {'mismatched':>10s}")
        for col in shared + ["obs_c"]:
            print(f"  {col:34s} {res[col][1]:>8d} {res[col][0]:>8d} {res[col][1] - res[col][0]:>10d}")
        print(f"  station-days where the nearest report (the table's) is not the record's choice: "
              f"{nearest_diff_report} (of which with a different value {nearest_diff_value}); count only")
        for d, col, cv, tv in mism:
            print(f"  MISMATCH {st} {d} {col}: committed {cv!r}, table {tv!r}")
        total_fail += len(mism) + len(no_table)
    n_cmp = sum(v[2] for v in summary.values())
    print(f"\nstation-days compared: {n_cmp} (F137.8: 5,861 at lead 24); "
          f"failures (mismatches plus committed rows with no table row): {total_fail}")
    print("GATE PASSED" if total_fail == 0 else "GATE NOT PASSED: STOP")
    return 0 if total_fail == 0 else 1


# ------------------------------------------------------------------ --records (Step 7.1, 7.2)

def run_records(args):
    t0 = time.time()
    out = Path(args.out)
    print(f"SESSION 96 --records (offline), start {now_utc()}")
    for p in (COUNTS_OUT, META_OUT):
        if p.exists():
            raise SystemExit(f"STOP: {p} exists")
    check_pull_files()
    lines, tallies = {}, {}
    ostats, n_plan = build(STATIONS, lines, tallies, log=lambda *a: None)
    files = []
    for st in STATIONS:
        data = table_bytes(lines[st])
        disk = (out / table_name(st)).read_bytes()
        same = data == disk
        print(f"in-memory rebuild of {table_name(st)} byte-equal to the file in {out.name}/: {same}")
        if not same:
            raise SystemExit("STOP: the rebuild differs from the written table")
        files.append((table_name(st), len(lines[st]) - 1, len(data), sha256_bytes(data)))
    # counts: one row per airport and lead
    head = ["station", "icao", "lead", "rows"]
    for col in GRIB_COLS:
        head += [f"{col}_empty_{r.replace(' ', '_')}" for r in REASONS]
    head += ["no_observation", "uses_whole_file", "complete_case"]
    rows = []
    for st in STATIONS:
        for n in range(HOURS[0], HOURS[1] + 1):
            t = tallies[st][n]
            r = [st, p91.DEV[st], n, t["rows"]]
            for col in GRIB_COLS:
                r += [t["empty"].get((col, why), 0) for why in REASONS]
            r += [t["no_obs"], t["whole"], t["complete"]]
            rows.append(r)
    counts_text = "\n".join(",".join(str(x) for x in r) for r in [head] + rows) + "\n"
    write_new_file(COUNTS_OUT, counts_text.encode("ascii"))
    print(f"wrote {COUNTS_OUT.relative_to(ROOT)}: {len(rows)} rows, {len(head)} columns, "
          f"SHA-256 {p91.sha256_file(COUNTS_OUT)}")
    print_counts_summary(tallies)
    # meta
    script = Path(__file__).resolve()
    obs_lines = [f"              {f.name} sha256 {p91.sha256_file(f)}" for st in STATIONS for f in obs_files(st)]
    meta = [
        "Provenance (SPEC 2.3). Do not edit the data files.",
        "",
        "files       : stagec_dev_<ICAO>.csv.gz, one per development airport",
        "purpose     : session 96, Step 5 - the stage C development table (DECISIONS D88.3): for each development",
        "              airport (EGLC, LFPG, DSM, YSDU, RNO, KSFO), every GFS cycle in the pull's plan and every",
        "              forecast hour 0 to 24, the record's features rebuilt from the stored grid values (D88.5)",
        "              and the hourly observation at the valid time (D88.7). No model, no score.",
        f"where       : {OUT_DEFAULT.name}/ beside the repository (not tracked, D88.8). Rebuilt exactly from the",
        "              Release (MLwx-pull/, F137) and the committed observation files by",
        "              scripts/session96_stagec_table.py --build.",
        f"written by  : scripts/session96_stagec_table.py --build; this meta by --records at {now_utc()}",
        f"script sha256: {p91.sha256_file(script)}",
        "",
        "table files :",
    ]
    meta += [f"  {name}  rows {n:,}  bytes {b:,}  sha256 {sha}" for name, n, b, sha in files]
    meta += [
        f"  rows per airport {n_plan:,} (the plan of session91_grib_pull.py, hours 0 to 24); all {n_plan * 6:,}",
        "  row order: cycle, then lead. gzip with no file name and a zero timestamp, so equal content gives",
        "  equal bytes. Floats written with repr, so they read back to the identical number. Empty = no value",
        "  (never filled, SPEC 2.2).",
        "",
        f"columns     : {', '.join(COLUMNS)}",
        "  station is SPEC 3.4's station code (DSM, RNO, SFO for KDSM, KRNO, KSFO); cycle_utc, valid_utc and",
        "  obs_time_utc as YYYY-MM-DDTHH:MMZ. Names from session81_training_set.csv: temp,",
        "  temperature_grib_c, cloud_cover, wind_speed_10m, dewpoint_depression_t2m_floored, lapse_rate_t2_t850,",
        "  dswrf_2h_wm2, pressure_tendency_3h_hpa, season_sin, season_cos. From SPEC 8.8 G4 and G7: t2m_raw,",
        "  dew_point_2m, t850 (degC, 3 decimals). From D88.5(e): tmax2m_c, tmin2m_c (degC, 3 decimals, no",
        "  elevation constant). obs_tmpc is float(tmpc) of the nearest usable report within 15 minutes",
        "  (inclusive; a tie keeps the earlier). uses_whole_file: a message used has status 'ok (whole file)'.",
        "  complete_case: the nine SPEC 8.8 G15 columns and the observation are all present.",
        "",
        "inputs      :",
        f"  {INVENTORY.relative_to(ROOT)} sha256 {p91.sha256_file(INVENTORY)} (the 195 pull files, each",
        "  checked against it by name, bytes and SHA-256 before the build)",
        f"  {p91.POSITIONS.relative_to(ROOT)} sha256 {p91.sha256_file(p91.POSITIONS)}",
        f"  SPEC.md section 3.4 and the params CSVs, parsed by session86_forward_build.load_airports:",
    ]
    meta += [f"  {p.relative_to(ROOT)} sha256 {p91.sha256_file(p)}" for p in s86.PARAMS_CSVS]
    meta += ["  observation files (the six yearly routine files per airport; their .meta.txt record no SHA-256):"]
    meta += obs_lines
    meta += [
        "imported code:",
        f"  scripts/session86_forward_build.py sha256 {p91.sha256_file(ROOT / 'scripts' / 'session86_forward_build.py')}",
        f"  scripts/session92_verify_chunk.py sha256 {p91.sha256_file(ROOT / 'scripts' / 'session92_verify_chunk.py')}",
        f"  scripts/session91_grib_pull.py sha256 {p91.sha256_file(ROOT / 'scripts' / 'session91_grib_pull.py')}",
        f"versions    : {versions()}",
    ]
    write_new_file(META_OUT, ("\n".join(meta) + "\n").encode("ascii"))
    print(f"wrote {META_OUT.relative_to(ROOT)}: SHA-256 {p91.sha256_file(META_OUT)}")
    print(f"end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


def print_counts_summary(tallies):
    print("\ncounts summary (rows; empty cells by reason, summed over leads; no observation; whole file; complete case)")
    for st in STATIONS:
        tt = tallies[st]
        rows = sum(t["rows"] for t in tt.values())
        emp = {}
        for t in tt.values():
            for k, v in t["empty"].items():
                emp[k] = emp.get(k, 0) + v
        print(f"  {st}: rows {rows}; no observation {sum(t['no_obs'] for t in tt.values())}; uses whole file "
              f"{sum(t['whole'] for t in tt.values())}; complete case all leads "
              f"{sum(t['complete'] for t in tt.values())}, leads 3 to 24 "
              f"{sum(tt[n]['complete'] for n in range(3, 25))} of {sum(tt[n]['rows'] for n in range(3, 25))}")
        for (col, why), v in sorted(emp.items()):
            print(f"      {col} empty, {why}: {v}")
    print("\ncomplete-case rows per lead (EGLC, LFPG, DSM, YSDU, RNO, SFO):")
    for n in range(HOURS[0], HOURS[1] + 1):
        print(f"  lead {n:2d}: " + ", ".join(f"{tallies[st][n]['complete']}/{tallies[st][n]['rows']}"
                                              for st in STATIONS)
              + f"; no observation: " + ", ".join(str(tallies[st][n]['no_obs']) for st in STATIONS))


# ------------------------------------------------------------------ --guard-check (Step 7.4)

def run_guard_check(args):
    print(f"SESSION 96 --guard-check (offline, no data read), {now_utc()}")
    ok_all = True
    for label, fn, t, refuse in (
            ("valid time 2026-07-31T23:00", check_valid_time, dt.datetime(2026, 7, 31, 23, 0), False),
            ("valid time 2026-08-01T00:00", check_valid_time, dt.datetime(2026, 8, 1, 0, 0), True),
            ("observation 2026-07-31T23:59", check_obs_time, dt.datetime(2026, 7, 31, 23, 59), False),
            ("observation 2026-08-01T00:00", check_obs_time, dt.datetime(2026, 8, 1, 0, 0), True)):
        try:
            fn(t)
            got, why = False, ""
        except GuardError as e:
            got, why = True, str(e)
        good = got == refuse
        ok_all &= good
        print(f"  [{'OK ' if good else 'BAD'}] {label}: {'REFUSED' if got else 'allowed'} {why}")
    print("all guard cases behaved as required" if ok_all else "A GUARD CASE DID NOT BEHAVE")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("inputs", "test-rt", "build", "gate", "records", "guard-check"):
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--out", default=str(OUT_DEFAULT), help="the table folder (default MLwx-stagec/ beside the repo)")
    ap.add_argument("--station", default=None, help="--build only: one SPEC 3.4 station code")
    a = ap.parse_args()
    try:
        if a.inputs:
            return run_inputs(a)
        if a.test_rt:
            return run_test_rt(a)
        if a.build:
            return run_build(a)
        if a.gate:
            return run_gate(a)
        if a.records:
            return run_records(a)
        return run_guard_check(a)
    except GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
