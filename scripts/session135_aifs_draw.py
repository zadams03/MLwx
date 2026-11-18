#!/usr/bin/env python3
"""Session 135: stage D's claim airports for ECMWF AIFS (DECISIONS D130.7, D130.8).

Modes (docs/sessions/session-135.md, Steps 2 and 3):

  --eligible   Step 2. (a) The grid check: one AIFS 2 m temperature message
               (2025-03-01 00z, step 6) is fetched by byte range and only
               its grid's coordinates are read. Every one of the four grid
               points that data/processed/session91_pull_airports.csv gives
               for the 36 pool airports and the 12 record airports must be a
               point of that grid (longitudes compared modulo 360, D130.8).
               (b) Eligibility (D130.7(b)) of the 36 pool airports from their
               saved hourly observations: usable local days in
               2025-02-26..2026-07-31 and in 2025-08-01..2026-07-31, counted
               with session 90's functions, unchanged. Writes
               data/processed/session135_draw/eligibility.csv and its
               .meta.txt.
  --draw       Step 3. D130.7(c) and (d) applied to eligibility.csv, once.
               Writes data/processed/session135_draw/draw.csv and its
               .meta.txt. A second run stops (the files are written with
               mode "x").

Hard limits: no observation value is read as a value, only whether each
report has a usable temperature (session 90's `usable`); no AIFS value is
read, only the grid's latitudes and longitudes; no IEM call; nothing valid
after 2026-07-31T23:00 UTC is requested.

Session 90's script and session 113's script are imported read only and
not edited. Session 90's `local_day_counts` reads its window from two
module constants (FIRST_UTC and HELD_OUT_START); this script sets them on
the imported module to D130.7(b)'s dates before counting, so the function's
code is used unchanged. LIMIT (2026-07-31T23:59 UTC) is session 90's own and
is D130.7(b)'s end, so it is left as it is.

No em-dashes in any text here (D76.6).
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

OUT = ROOT / "data" / "processed" / "session135_draw"
ELIG = OUT / "eligibility.csv"
DRAW = OUT / "draw.csv"
S90_TABLE = ROOT / "data" / "processed" / "session90_airports.csv"
S91_TABLE = ROOT / "data" / "processed" / "session91_pull_airports.csv"
S110_COUNTS = ROOT / "data" / "processed" / "session110_onboard_counts.csv"
S90_SCRIPT = SCRIPTS / "session90_airport_check.py"
S113_SCRIPT = SCRIPTS / "session113_comparison_pull.py"

SEED = 20261117                                         # D130.7(d)
WINDOW_FIRST = dt.datetime(2025, 2, 26, 0, 0)           # D130.7(b): whole window starts
YEAR_FIRST = dt.date(2025, 8, 1)                        # D130.7(b): the look year starts
THRESHOLD = 90.0                                        # percent, both windows
STRATA = [("Europe", 1), ("North America", 2), ("Asia", 2), ("South", 1)]   # D130.7(c)
EXCLUDED = {"LFPB"}                                     # D82.7(a), D130.7(a)
RECORD12 = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO",
            "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]          # D103.4
GRID_MSG = (dt.datetime(2025, 3, 1, 0), 6, "2t")        # Step 2(a)

ELIG_COLS = ["icao", "stratum", "iem_id", "time_zone",
             "days_window", "usable_days_window", "pct_window",
             "days_year", "usable_days_year", "pct_year",
             "obs_ok", "grid_ok", "eligible", "reason"]
DRAW_COLS = ["order", "icao", "stratum", "how"]


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def read_csv(p):
    with open(p, newline="") as f:
        return list(csv.DictReader(f))


def csv_bytes(cols, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    w.writerows(rows)
    return buf.getvalue().encode()


def write_new(path, data):
    """Mode x: an existing file stops the run."""
    with open(path, "xb") as f:
        f.write(data)


# ------------------------------------------------------------------ pool

def pool():
    """D130.7(a): the 37 airports onboarded in session 110 (F153.6), minus
    LFPB. Their ICAO codes as session 90's table writes them."""
    passed = [r["airport"] for r in read_csv(S110_COUNTS) if r["verdict"] == "pass"]
    s90 = {r["icao"]: r for r in read_csv(S90_TABLE)}
    out = []
    for a in passed:
        icao = a if a in s90 else None
        if icao is None:
            raise SystemExit(f"stop: {a} from session 110's counts is not in session 90's table")
        if icao not in EXCLUDED:
            out.append(icao)
    return sorted(out), len(passed), s90


# ------------------------------------------------------------------ grid check (D130.8)

def lon360(x):
    return float(x) % 360.0


def grid_index(meta, lat, lon):
    """Index of (lat, lon) in a regular latitude-longitude grid's values
    array (scanning mode 0: west to east, north to south), or None if the
    point is not a grid node. Longitudes are compared modulo 360."""
    ni, nj = int(meta["Ni"]), int(meta["Nj"])
    di, dj = float(meta["iDirectionIncrementInDegrees"]), float(meta["jDirectionIncrementInDegrees"])
    la1 = float(meta["latitudeOfFirstGridPointInDegrees"])
    lo1 = float(meta["longitudeOfFirstGridPointInDegrees"])
    if int(meta["scanningMode"]) != 0 or meta["gridType"] != "regular_ll":
        raise ValueError(f"unexpected grid {meta['gridType']} scanning {meta['scanningMode']}")
    fj = (la1 - float(lat)) / dj
    fi = ((lon360(lon) - lon360(lo1)) % 360.0) / di
    j, i = round(fj), round(fi)
    if abs(fj - j) > 1e-6 or abs(fi - i) > 1e-6 or not (0 <= j < nj and 0 <= i < ni):
        return None
    return j * ni + i


def points_of(row):
    """The four (lat, lon, weight) of a session 91 row, in its p1..p4 order."""
    return [(float(row[f"p{k}_lat"]), float(row[f"p{k}_lon"]), float(row[f"p{k}_weight"])) for k in range(1, 5)]


def check_points(meta, lats, lons, row):
    """Every point of a session 91 row must be a node of this grid, and the
    grid's own coordinates at that node must equal it (lon modulo 360).
    Returns (ok, indices, note)."""
    idx = []
    for k, (la, lo, _) in enumerate(points_of(row), start=1):
        i = grid_index(meta, la, lo)
        if i is None:
            return False, None, f"p{k} ({la}, {lo}) is not a grid node"
        if abs(float(lats[i]) - la) > 1e-6 or abs(lon360(lons[i]) - lon360(lo)) > 1e-6:
            return False, None, f"p{k} ({la}, {lo}) does not match the grid's ({lats[i]}, {lons[i]})"
        idx.append(i)
    return True, idx, ""


def fetch_grid_message():
    import eccodes as ec
    import session113_comparison_pull as s113
    cyc, step, param = GRID_MSG
    path = s113.ecmwf_file("aifs-single", cyc, step)
    lines, _ = s113.ecmwf_index_lines(path)
    hit = [x for x in lines if x["param"] == param and x.get("levtype") == "sfc"]
    if len(hit) != 1:
        raise SystemExit(f"stop: {len(hit)} index lines for {param} in {path}")
    x = hit[0]
    url = s113.ECMWF + path + ".grib2"
    gid, m, b = s113.fetch_message(url, x["_offset"], x["_length"], cyc + dt.timedelta(hours=step))
    try:
        if m["shortName"] != "2t" or s113.msg_run(m) != cyc or s113.msg_valid(m) != cyc + dt.timedelta(hours=step):
            raise SystemExit(f"stop: message identity {m['shortName']} {s113.msg_run(m)} {s113.msg_valid(m)}")
        lats = ec.codes_get_array(gid, "latitudes")
        lons = ec.codes_get_array(gid, "longitudes")
    finally:
        ec.codes_release(gid)
    info = dict(url=url, byte_range=f"{x['_offset']}-{x['_offset'] + x['_length'] - 1}",
                sha256=hashlib.sha256(b).hexdigest(), signature=s113.grid_signature(m))
    return m, lats, lons, info


# ------------------------------------------------------------------ eligibility (D130.7(b))

def count_obs(iem_id, tzname):
    """Session 90's obs_counts with D130.7(b)'s windows. Returns
    (days_window, usable_window, days_year, usable_year)."""
    import session90_airport_check as s90
    s90.FIRST_UTC = WINDOW_FIRST
    s90.HELD_OUT_START = YEAR_FIRST
    res = s90.obs_counts(iem_id, tzname)
    loc = res["local"]
    return loc["all"][0], loc["all"][1], loc["held"][0], loc["held"][1]


def pct(n, d):
    return 100.0 * n / d if d else 0.0


def run_eligible():
    if ELIG.exists():
        raise SystemExit(f"stop: {ELIG} exists; eligibility is written once")
    OUT.mkdir(parents=True, exist_ok=True)
    airports, n_pass, s90 = pool()
    print(f"== --eligible: pool {len(airports)} airports (session 110 onboarded {n_pass}, minus LFPB)")
    if len(airports) != 36:
        raise SystemExit(f"stop: the pool has {len(airports)} airports, not 36")
    s91 = {r["icao"]: r for r in read_csv(S91_TABLE)}
    missing91 = [a for a in airports + RECORD12 if a not in s91]
    if missing91:
        raise SystemExit(f"stop: not in session 91's table: {missing91}")

    # (a) grid check
    m, lats, lons, info = fetch_grid_message()
    print(f"grid of {info['url']} [{info['byte_range']}]: {info['signature']}")
    grid = {}
    for a in RECORD12 + airports:
        ok, _, note = check_points(m, lats, lons, s91[a])
        grid[a] = (ok, note)
    rec_fail = [a for a in RECORD12 if not grid[a][0]]
    pool_fail = [a for a in airports if not grid[a][0]]
    print(f"grid check: record airports on the grid {12 - len(rec_fail)} of 12; "
          f"pool airports {len(airports) - len(pool_fail)} of {len(airports)}")
    for a in rec_fail + pool_fail:
        print(f"  {a}: {grid[a][1]}")
    if rec_fail:
        raise SystemExit(f"stop: record airports off the AIFS grid: {rec_fail}")

    # (b) observation counts
    rows = []
    for a in airports:
        r = s90[a]
        try:
            dw, uw, dy, uy = count_obs(r["iem_id"], r["time_zone"])
        except RuntimeError as e:
            raise SystemExit(f"stop: {a}: {e}")
        pw, py = pct(uw, dw), pct(uy, dy)
        obs_ok = pw >= THRESHOLD and py >= THRESHOLD
        gok = grid[a][0]
        reasons = []
        if pw < THRESHOLD:
            reasons.append(f"window {pw:.2f} < 90")
        if py < THRESHOLD:
            reasons.append(f"year {py:.2f} < 90")
        if not gok:
            reasons.append(f"grid: {grid[a][1]}")
        el = obs_ok and gok
        rows.append([a, r["stratum"], r["iem_id"], r["time_zone"], dw, uw, f"{pw:.4f}", dy, uy, f"{py:.4f}",
                     int(obs_ok), int(gok), int(el), "; ".join(reasons)])
        print(f"  {a:5s} {r['stratum']:14s} window {uw}/{dw} {pw:6.2f}%  year {uy}/{dy} {py:6.2f}%  "
              f"grid {'ok' if gok else 'NO'}  {'eligible' if el else 'not eligible'}")
    data = csv_bytes(ELIG_COLS, rows)
    write_new(ELIG, data)
    per = {s: sum(1 for x in rows if x[1] == s and x[12]) for s, _ in STRATA}
    meta = [
        "eligibility.csv: D130.7(b) for the 36 pool airports (D130.7(a)), and D130.8's grid check.",
        f"written {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} by scripts/session135_aifs_draw.py --eligible",
        f"sha256 {hashlib.sha256(data).hexdigest()}",
        f"rows {len(rows)}",
        f"python {sys.version.split()[0]}",
        f"script sha256 {sha256_file(Path(__file__))}",
        f"session 90 script (imported, unchanged) sha256 {sha256_file(S90_SCRIPT)}",
        f"session 113 script (imported, unchanged) sha256 {sha256_file(S113_SCRIPT)}",
        f"input {S90_TABLE.relative_to(ROOT)} sha256 {sha256_file(S90_TABLE)}",
        f"input {S91_TABLE.relative_to(ROOT)} sha256 {sha256_file(S91_TABLE)}",
        f"input {S110_COUNTS.relative_to(ROOT)} sha256 {sha256_file(S110_COUNTS)}",
        "input data/raw/iem_asos_<iem_id>_<piece>_routine.csv, six pieces per airport (session 90's PIECES)",
        f"windows: local days starting on or after {WINDOW_FIRST:%Y-%m-%dT%H:%M} UTC and ending on or before "
        "2026-07-31T23:59 UTC; the year from local day 2025-08-01. Usable day: D82.8.",
        "counting: session 90's obs_counts and local_day_counts, with its FIRST_UTC and HELD_OUT_START set to these dates",
        "eligible: pct_window >= 90 and pct_year >= 90 and grid_ok",
        f"grid message: {info['url']} bytes {info['byte_range']} sha256 {info['sha256']}",
        f"grid signature: {info['signature']}",
        f"grid check: record airports {12 - len(rec_fail)} of 12 on the grid; pool {len(airports) - len(pool_fail)} of {len(airports)}",
        "eligible per stratum: " + ", ".join(f"{s} {n}" for s, n in per.items()),
    ]
    write_new(ELIG.with_suffix(".csv.meta.txt"), ("\n".join(meta) + "\n").encode())
    print(f"eligible per stratum: {per}")
    print(f"wrote {ELIG.relative_to(ROOT)} ({len(rows)} rows)")


# ------------------------------------------------------------------ the draw (D130.7(c), (d))

def draw(elig_rows, seed=SEED, log=print):
    """D130.7(c) and (d), with D82.7(d)'s shortfall rule. elig_rows: dicts
    with icao, stratum, eligible ("1" or "0"). Returns [(icao, stratum, how)]."""
    log(f"python {sys.version.split()[0]}, random.Random({seed})")
    rng = random.Random(seed)
    stratum_of = {r["icao"]: r["stratum"] for r in elig_rows}
    ok = sorted(r["icao"] for r in elig_rows if str(r["eligible"]) == "1")
    drawn, shortfall = [], 0
    for stratum, size in STRATA:
        elig = sorted(a for a in ok if stratum_of[a] == stratum)
        log(f"stratum {stratum} (size {size}): {len(elig)} eligible, sorted: {elig}")
        if len(elig) >= size:
            pick = rng.sample(elig, size)
            log(f"  sample({len(elig)} eligible, {size}) returned {pick}")
        else:
            pick = list(elig)
            shortfall += size - len(elig)
            log(f"  fewer eligible than {size}: take all {pick}; shortfall so far {shortfall}")
        drawn += [(a, stratum, "stratum") for a in pick]
    if shortfall:
        taken = {a for a, _, _ in drawn}
        rest = sorted(a for a in ok if a not in taken)
        log(f"shortfall {shortfall}; remaining eligible, sorted: {rest}")
        if len(rest) < shortfall:
            raise SystemExit("stop: fewer than six eligible airports in total")
        fill = rng.sample(rest, shortfall)
        log(f"  sample({len(rest)}, {shortfall}) returned {fill}")
        drawn += [(a, stratum_of[a], "shortfall fill") for a in fill]
    return drawn


def run_draw():
    if DRAW.exists():
        raise SystemExit(f"stop: {DRAW} exists; the draw runs once (D130.7(d))")
    rows = read_csv(ELIG)
    if len(rows) != 36:
        raise SystemExit(f"stop: eligibility.csv has {len(rows)} rows")
    lines = []

    def log(s):
        print(s, flush=True)
        lines.append(s)
    print("== --draw (D130.7(c), (d)), run once")
    drawn = draw(rows, SEED, log)
    log(f"THE AIFS CLAIM AIRPORTS ({len(drawn)}): {[a for a, _, _ in drawn]}")
    if len(drawn) != 6:
        raise SystemExit("stop: the draw did not give six airports")
    data = csv_bytes(DRAW_COLS, [[k, a, s, h] for k, (a, s, h) in enumerate(drawn, start=1)])
    write_new(DRAW, data)
    meta = [
        "draw.csv: stage D's six claim airports for AIFS (D130.7(c), (d)).",
        f"written {dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} by scripts/session135_aifs_draw.py --draw",
        f"sha256 {hashlib.sha256(data).hexdigest()}",
        f"python {sys.version.split()[0]}",
        f"random.Random({SEED}), one generator; strata {STRATA}",
        f"script sha256 {sha256_file(Path(__file__))}",
        f"input {ELIG.relative_to(ROOT)} sha256 {sha256_file(ELIG)}",
        "the draw as printed:",
    ] + ["  " + s for s in lines]
    write_new(DRAW.with_suffix(".csv.meta.txt"), ("\n".join(meta) + "\n").encode())
    print(f"wrote {DRAW.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--eligible", action="store_true")
    g.add_argument("--draw", action="store_true")
    a = ap.parse_args()
    if a.eligible:
        run_eligible()
    else:
        run_draw()


if __name__ == "__main__":
    main()
