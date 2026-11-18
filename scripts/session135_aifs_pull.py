#!/usr/bin/env python3
"""Session 135: the ECMWF AIFS Single pull for stage D (DECISIONS D130.8, D130.9).

Modes (docs/sessions/session-135.md, Steps 4 and 5):

  --plan  [--months A..B | --days LIST] [--outdir DIR]
          For each chunk (a month, or a day with --days): the cycles from
          the S3 listings, then each listed step's .index file, and from it
          the messages D130.9 needs. Writes <chunk>/plan.csv.gz. A chunk
          whose plan exists is skipped.
  --pull  [--months A..B | --days LIST] [--workers N] [--outdir DIR]
          Plans the chunk if needed, then fetches every planned message by
          byte range, checks it against its plan, and keeps its values at
          the four points of each of the 18 airports. A finished chunk
          (its done-marker) is skipped, so a re-run is safe. Files are
          written as *.partial and then renamed. A chunk that fails is
          tried again up to 3 times, 5 minutes apart (F156.9(8)); HTTP 503
          is retried with longer waits by session 113's `get`.
  --verify [--outdir DIR]
          The checks of D130.9 on everything pulled: every planned message
          is kept or is a gap with a reason (kept plus gaps equals
          planned); every kept message's SHA-256 is in the manifest and
          its rows are complete; gaps by reason, cycle hour and month; the
          guards again on every row. Writes verify.txt.
  --gate  [--outdir DIR]
          Step 5's gate on the test chunk: (a) 2 m temperature equal to
          session 113's stored values at the six development airports;
          (b) five messages fetched again, SHA-256 equal; (c) kept plus
          gaps equals planned; (d) every field present in both AIFS
          versions, names and units per version; (e) no row valid after
          2026-07-31T23:00 UTC. Writes gate.txt.

Default --outdir: data/processed/session135_pull_test (the session's test
chunk). The owner's full pull uses a folder outside the repo.

Guards (tests/test_session135_aifs.py): no cycle before 2025-02-26 00z; no
step valid after 2026-07-31T23:00 UTC; only the 18 airports of D130.9 (the
12 record airports and draw.csv's six); only the folder
aifs-single/0p25/oper/, never experimental. A failed check is a gap with a
reason, never a value. No GRIB file is kept: each message is decoded in
memory and dropped; only point values, unrounded, are written.

Positions (D130.8): each airport's four points and bilinear weights are
those of data/processed/session91_pull_airports.csv (its GFS table), found
on the AIFS grid by coordinates (longitudes modulo 360), separately for
each grid geometry the archive uses. The weights are not applied here; v1
to v4 are the four points in session 91's p1 to p4 order.

Session 113's script and this session's draw script are imported read only.

No em-dashes in any text here (D76.6).
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import json
import math
import os
import random
import sys
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session135_aifs_draw as draw_mod  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "processed" / "session135_pull_test"
DRAW_CSV = draw_mod.DRAW
S91_TABLE = draw_mod.S91_TABLE
S113_DIR = ROOT / "data" / "processed" / "session113"

FIRST_CYCLE = dt.datetime(2025, 2, 26, 0)         # D130.9: from 2025-02-26 00z
LIMIT = dt.datetime(2026, 7, 31, 23, 0)           # D130.9: nothing valid after this
LAST_CYCLE = dt.datetime(2026, 7, 31, 18)
CYCLE_HOURS = (0, 6, 12, 18)
STEPS = list(range(0, 49, 6))                     # D130.9: 0 to 48 every 6 hours
FOLDER_PART = "/aifs-single/0p25/oper/"
RECORD12 = draw_mod.RECORD12
DEV6 = RECORD12[:6]
MAX_WORKERS = 8
V2_FIRST = dt.date(2026, 5, 12)                   # D130.4: AIFS v2 live (label only)

# D130.9's fields: (param, levtype, level, steps). Level "sfc" for surface
# fields; "850" for the 850 hPa temperature. Surface geopotential at step 0 only.
FIELDS = [
    ("2t", "sfc", "sfc", "all"),
    ("2d", "sfc", "sfc", "all"),
    ("tcc", "sfc", "sfc", "all"),
    ("10u", "sfc", "sfc", "all"),
    ("10v", "sfc", "sfc", "all"),
    ("t", "pl", "850", "all"),
    ("msl", "sfc", "sfc", "all"),
    ("sp", "sfc", "sfc", "all"),
    ("ssrd", "sfc", "sfc", "all"),
    ("z", "sfc", "sfc", (0,)),
]

PLAN_COLS = ["chunk", "cycle", "step", "valid_utc", "param", "level", "status", "reason",
             "url", "offset", "length", "index_line"]
VAL_COLS = ["airport", "cycle", "step", "valid_utc", "param", "level", "v1", "v2", "v3", "v4", "units", "msg"]
MAN_COLS = ["msg", "cycle", "step", "valid_utc", "param", "level", "url", "byte_range", "bytes", "sha256",
            "shortName", "name", "units", "typeOfLevel", "levelValue", "stepRange",
            "generatingProcessIdentifier", "grid", "pulled_utc"]
GAP_COLS = ["cycle", "step", "valid_utc", "param", "level", "airport", "reason", "detail"]

_s113 = None
_lock = threading.Lock()


class GuardError(Exception):
    """A guard fired: nothing is requested, read or written."""


def s113():
    """Session 113's script, imported read only, on first use (it imports
    eccodes and requests)."""
    global _s113
    if _s113 is None:
        import session113_comparison_pull as m
        _s113 = m
        m.http().headers.update({"User-Agent": "MLwx/session135"})
    return _s113


def say(*a):
    print(*a, flush=True)


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def sha256_file(p):
    return draw_mod.sha256_file(p)


# ------------------------------------------------------------------ guards

def guard_cycle(c):
    if c < FIRST_CYCLE:
        raise GuardError(f"cycle {c} is before {FIRST_CYCLE}")
    if c.hour not in CYCLE_HOURS or c.minute or c.second:
        raise GuardError(f"cycle {c} is not a 00, 06, 12 or 18 UTC cycle")
    return c


def guard_valid(t):
    if t > LIMIT:
        raise GuardError(f"valid time {t} is after {LIMIT}")
    return t


def guard_url(url):
    if FOLDER_PART not in url or "experimental" in url:
        raise GuardError(f"not the operational AIFS Single folder: {url}")
    return url


def guard_airports(airports):
    drawn = [a for a in airports if a not in RECORD12]
    if sorted(airports[:12]) != sorted(RECORD12) or len(airports) != 18 or len(set(airports)) != 18 \
            or len(drawn) != 6:
        raise GuardError(f"not the 18 airports of D130.9: {airports}")
    return airports


def steps_kept(cyc):
    """D130.9: steps 0 to 48 every 6 hours, only those valid on or before LIMIT."""
    guard_cycle(cyc)
    return [s for s in STEPS if cyc + dt.timedelta(hours=s) <= LIMIT]


def fields_for(step):
    return [(p, lt, lv) for p, lt, lv, st in FIELDS if st == "all" or step in st]


def all_cycles():
    c, out = FIRST_CYCLE, []
    while c <= LAST_CYCLE:
        out.append(c)
        c += dt.timedelta(hours=6)
    return out


def chunks_from_args(months=None, days=None):
    """{chunk name: [cycles]}: months 'YYYY-MM..YYYY-MM' (or one month), or
    days 'YYYY-MM-DD[..YYYY-MM-DD],...' (day chunks). Every cycle passes the
    guards."""
    cy = all_cycles()
    out = {}
    if days:
        for part in days.split(","):
            a, _, b = part.partition("..")
            d0 = dt.date.fromisoformat(a)
            d1 = dt.date.fromisoformat(b) if b else d0
            for c in cy:
                if d0 <= c.date() <= d1:
                    out.setdefault(f"{c:%Y-%m-%d}", []).append(c)
            if d0 < FIRST_CYCLE.date() or d1 > LAST_CYCLE.date():
                raise GuardError(f"days {part} are outside {FIRST_CYCLE:%Y-%m-%d}..{LAST_CYCLE:%Y-%m-%d}")
    else:
        a, b = (months.split("..") + [None])[:2] if months else (f"{FIRST_CYCLE:%Y-%m}", f"{LAST_CYCLE:%Y-%m}")
        b = b or a
        for c in cy:
            if a <= f"{c:%Y-%m}" <= b:
                out.setdefault(f"{c:%Y-%m}", []).append(c)
        if months and (a < f"{FIRST_CYCLE:%Y-%m}" or b > f"{LAST_CYCLE:%Y-%m}"):
            raise GuardError(f"months {months} are outside {FIRST_CYCLE:%Y-%m}..{LAST_CYCLE:%Y-%m}")
    for cs in out.values():
        for c in cs:
            guard_cycle(c)
    return out


# ------------------------------------------------------------------ airports and positions (D130.8)

def load_airports():
    """The 18 airports of D130.9 with session 91's four points and weights."""
    drawn = [r["icao"] for r in draw_mod.read_csv(DRAW_CSV)]
    airports = guard_airports(list(RECORD12) + drawn)
    s91 = {r["icao"]: r for r in draw_mod.read_csv(S91_TABLE)}
    return airports, {a: draw_mod.points_of(s91[a]) for a in airports}, {a: s91[a] for a in airports}


_POS = {}


def positions_for(gid, meta, rows91, outdir):
    """{airport: [index x 4]} on this message's grid, or raises ValueError if
    any point is off it. Written once per grid geometry to
    positions_<label>.csv in outdir."""
    sig = s113().grid_signature(meta)
    label = "aifs_" + hashlib.sha256(sig.encode()).hexdigest()[:8]
    with _lock:
        if label in _POS:
            return label, _POS[label]
        import eccodes as ec
        lats = ec.codes_get_array(gid, "latitudes")
        lons = ec.codes_get_array(gid, "longitudes")
        pos, rows = {}, []
        for a, r in rows91.items():
            ok, idx, note = draw_mod.check_points(meta, lats, lons, r)
            if not ok:
                raise ValueError(f"{a}: {note}")
            pos[a] = idx
            pts = draw_mod.points_of(r)
            rows.append([a] + [x for k in range(4) for x in (idx[k], repr(pts[k][0]), repr(pts[k][1]),
                                                              repr(pts[k][2]))] + [sig])
        p = Path(outdir) / f"positions_{label}.csv"
        if not p.exists():
            cols = ["airport"] + [f"p{k}_{c}" for k in range(1, 5) for c in ("index", "lat", "lon", "weight")] + ["grid"]
            tmp = p.with_suffix(".csv.partial")
            tmp.unlink(missing_ok=True)
            draw_mod.write_new(tmp, draw_mod.csv_bytes(cols, rows))
            os.replace(tmp, p)
        _POS[label] = pos
        return label, pos


# ------------------------------------------------------------------ files

def write_gz(path, cols, rows):
    """Through *.partial, then renamed (equal content gives equal bytes)."""
    path = Path(path)
    tmp = path.with_name(path.name + ".partial")
    tmp.unlink(missing_ok=True)
    s113().write_csv_gz(tmp, cols, rows)
    os.replace(tmp, path)


def read_gz(path):
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ plan

def index_select(lines, cyc, step):
    """The planned messages of one file from its .index lines: one row per
    field of D130.9 at this step, 'planned' with offset and length, or a gap
    with its reason."""
    out = []
    for p, lt, lv in fields_for(step):
        hit = [x for x in lines if x.get("param") == p and x.get("levtype") == lt
               and (lt != "pl" or str(x.get("levelist")) == lv)]
        if len(hit) != 1:
            out.append((p, lv, "gap", f"{len(hit)} index lines", None, None, ""))
            continue
        x = hit[0]
        if x.get("date") != f"{cyc:%Y%m%d}" or x.get("time") != f"{cyc:%H}00" or int(x.get("step")) != step:
            out.append((p, lv, "gap", f"index line date/time/step {x.get('date')} {x.get('time')} {x.get('step')}",
                        None, None, ""))
            continue
        out.append((p, lv, "planned", "", int(x["_offset"]), int(x["_length"]), json.dumps(x, sort_keys=True)))
    return out


def plan_chunk(name, cycs, outdir):
    d = Path(outdir) / name
    d.mkdir(parents=True, exist_ok=True)
    pp = d / "plan.csv.gz"
    if pp.exists():
        return read_gz(pp)
    S = s113()
    rows = []
    for cyc in cycs:
        guard_cycle(cyc)
        folder, _ = S.ecmwf_folder("aifs-single", cyc)
        guard_url(folder)
        keys = {k for k, _, _ in S.s3_list(S.ECMWF, folder)}
        for step in steps_kept(cyc):
            valid = guard_valid(cyc + dt.timedelta(hours=step))
            path = S.ecmwf_file("aifs-single", cyc, step, folder)
            url = guard_url(S.ECMWF + path + ".grib2")
            base = [name, iso(cyc), step, iso(valid)]
            if path + ".grib2" not in keys or path + ".index" not in keys:
                for p, lt, lv in fields_for(step):
                    rows.append(base + [p, lv, "gap", "not listed", url, "", "", ""])
                continue
            try:
                lines, _ = S.ecmwf_index_lines(path)
            except S.Missing as e:
                for p, lt, lv in fields_for(step):
                    rows.append(base + [p, lv, "gap", f"no index ({e})", url, "", "", ""])
                continue
            for p, lv, st, why, off, ln, line in index_select(lines, cyc, step):
                rows.append(base + [p, lv, st, why, url, "" if off is None else off, "" if ln is None else ln, line])
    write_gz(pp, PLAN_COLS, rows)
    return read_gz(pp)


# ------------------------------------------------------------------ fetch and check

EXPECT = {  # D130.9's plan per parameter: (shortName, typeOfLevel, level or None)
    "2t": ("2t", "heightAboveGround", 2), "2d": ("2d", "heightAboveGround", 2),
    "tcc": ("tcc", None, None), "10u": ("10u", "heightAboveGround", 10),
    "10v": ("10v", "heightAboveGround", 10), "t": ("t", "isobaricInhPa", 850),
    "msl": ("msl", None, None), "sp": ("sp", "surface", None),
    "ssrd": ("ssrd", "surface", None), "z": ("z", "surface", None),
}
UNITS = {"2t": {"K"}, "2d": {"K"}, "tcc": {"%"}, "10u": {"m s**-1"}, "10v": {"m s**-1"}, "t": {"K"},
         "msl": {"Pa"}, "sp": {"Pa"}, "ssrd": {"J m**-2"}, "z": {"m**2 s**-2"}}


def check_message(m, cyc, step, param):
    """D130.9's checks of a decoded message against its plan, before any
    value is read: parameter, level, units, run, step (valid time), grid."""
    S = s113()
    errs = []
    sn, tol, lev = EXPECT[param]
    if m.get("shortName") != sn:
        errs.append(f"shortName {m.get('shortName')}")
    if tol is not None and m.get("typeOfLevel") != tol:
        errs.append(f"typeOfLevel {m.get('typeOfLevel')}")
    if lev is not None and m.get("level") != lev:
        errs.append(f"level {m.get('level')}")
    if m.get("units") not in UNITS[param]:
        errs.append(f"units {m.get('units')}")
    if S.msg_run(m) != cyc:
        errs.append(f"run {S.msg_run(m)}")
    if S.msg_valid(m) != cyc + dt.timedelta(hours=step):
        errs.append(f"valid {S.msg_valid(m)}")
    if m.get("gridType") != "regular_ll" or m.get("iDirectionIncrementInDegrees") != 0.25 \
            or m.get("jDirectionIncrementInDegrees") != 0.25 or m.get("Ni") != 1440 or m.get("Nj") != 721:
        errs.append(f"grid {m.get('gridType')} {m.get('Ni')}x{m.get('Nj')} {m.get('iDirectionIncrementInDegrees')}")
    return errs


def point_values(vals, idx, missing):
    """The four values, or None if any is missing or not finite (a gap,
    never a value)."""
    pts = [float(vals[k]) for k in idx]
    if any((not math.isfinite(x)) or x == missing for x in pts):
        return None
    return pts


def do_message(row, airports, rows91, outdir):
    """One planned message. Returns (vals, man, gaps). A fetch failure after
    session 113's retries raises (the chunk fails and is tried again)."""
    import eccodes as ec
    S = s113()
    cyc = guard_cycle(dt.datetime.strptime(row["cycle"], "%Y-%m-%dT%H:%MZ"))
    step = int(row["step"])
    valid = guard_valid(cyc + dt.timedelta(hours=step))
    url = guard_url(row["url"])
    base = [row["cycle"], step, row["valid_utc"], row["param"], row["level"]]
    off, ln = int(row["offset"]), int(row["length"])
    pulled = now_utc()
    try:
        gid, m, b = S.fetch_message(url, off, ln, valid)
    except S.Missing as e:
        return [], [], [base + ["*", "no file", str(e)]]
    except S.IndexMismatch as e:
        return [], [], [base + ["*", "index offset does not match the file", str(e)]]
    try:
        errs = check_message(m, cyc, step, row["param"])
        label, pos = "", None
        if not errs:
            try:
                label, pos = positions_for(gid, m, rows91, outdir)
            except ValueError as e:
                errs.append(f"positions: {e}")
        if errs:
            return [], [], [base + ["*", "failed check", "; ".join(errs)]]
        v = ec.codes_get_values(gid)
        missing = ec.codes_get_double(gid, "missingValue")
        digest = hashlib.sha256(b).hexdigest()
        mid = digest[:16]
        man = [mid] + base + [url, f"{off}-{off + ln - 1}", len(b), digest, m.get("shortName"), m.get("name"),
                              m.get("units"), m.get("typeOfLevel"), m.get("level"), m.get("stepRange"),
                              m.get("generatingProcessIdentifier"), label, pulled]
        vals, gaps = [], []
        for a in airports:
            pts = point_values(v, pos[a], missing)
            if pts is None:
                gaps.append(base + [a, "missing value", ""])
                continue
            vals.append([a] + base + [repr(x) for x in pts] + [m.get("units"), mid])
        return vals, [man], gaps
    finally:
        ec.codes_release(gid)


def run_chunk(name, cycs, outdir, workers):
    S = s113()
    d = Path(outdir) / name
    airports, _, rows91 = load_airports()
    plan = plan_chunk(name, cycs, outdir)
    todo = [r for r in plan if r["status"] == "planned"]
    plan_gaps = [[r["cycle"], r["step"], r["valid_utc"], r["param"], r["level"], "*", "plan: " + r["reason"], ""]
                 for r in plan if r["status"] != "planned"]
    res = S.pmap(lambda r: do_message(r, airports, rows91, outdir), todo, workers)
    vals = [x for v, _, _ in res for x in v]
    man = [x for _, m, _ in res for x in m]
    gaps = plan_gaps + [x for _, _, g in res for x in g]
    by_air = defaultdict(list)
    for r in vals:
        by_air[r[0]].append(r)
    for a in airports:
        write_gz(d / f"aifs_{a}.csv.gz", VAL_COLS, by_air.get(a, []))
    write_gz(d / "manifest.csv.gz", MAN_COLS, man)
    write_gz(d / "gaps.csv.gz", GAP_COLS, gaps)
    msg_gaps = sum(1 for g in gaps if g[5] == "*")
    done = d / "done.txt"
    tmp = d / "done.txt.partial"
    tmp.write_text(f"{now_utc()} cycles {len(cycs)} planned {len(plan)} kept {len(man)} message_gaps {msg_gaps} "
                   f"value_gaps {len(gaps) - msg_gaps} rows {len(vals)}\n")
    os.replace(tmp, done)
    return len(plan), len(man), msg_gaps, len(vals)


def run_pull(chunks, outdir, workers):
    S = s113()
    Path(outdir).mkdir(parents=True, exist_ok=True)
    say(f"== --pull: {sum(len(c) for c in chunks.values())} cycles in {len(chunks)} chunks into {outdir}; "
        f"{workers} workers")
    failed = []
    t0 = time.time()
    n0, b0 = S.REQUESTS["n"], S.REQUESTS["bytes"]
    for name, cs in sorted(chunks.items()):
        if (Path(outdir) / name / "done.txt").exists():
            say(f"  {name}: done, skipped")
            continue
        for attempt in range(1, 4):
            try:
                t1 = time.time()
                pl, kept, mg, nv = run_chunk(name, cs, outdir, workers)
                say(f"  {name}: planned {pl}, kept {kept}, message gaps {mg}, rows {nv}, {time.time() - t1:.0f} s")
                break
            except GuardError:
                raise
            except Exception as e:  # noqa: BLE001 - the chunk is tried again, then reported
                say(f"  {name}: attempt {attempt} failed: {type(e).__name__}: {e}")
                if attempt < 3:
                    time.sleep(300)
        else:
            failed.append(name)
    el = time.time() - t0
    nreq, nb = S.REQUESTS["n"] - n0, S.REQUESTS["bytes"] - b0
    say(f"requests {nreq}, bytes {nb}, {el:.0f} s; failed chunks {failed or 'none'}")
    with open(Path(outdir) / "pull_log.txt", "a") as f:
        f.write(f"{now_utc()} chunks {sorted(chunks)} workers {workers} requests {nreq} bytes {nb} "
                f"seconds {el:.1f} failed {failed}\n")
    write_meta(outdir)
    if failed:
        raise SystemExit(f"chunks failed: {failed}; run the same command again (finished chunks are skipped)")


def write_meta(outdir):
    S = s113()
    import eccodes
    import numpy
    import requests
    airports, _, _ = load_airports()
    lines = [
        "AIFS Single pull for stage D (DECISIONS D130.9), by scripts/session135_aifs_pull.py",
        f"written {now_utc()}",
        f"python {sys.version.split()[0]}, eccodes {eccodes.__version__}, numpy {numpy.__version__}, "
        f"requests {requests.__version__}",
        f"script sha256 {sha256_file(Path(__file__))}",
        f"session 113 script (imported, unchanged) sha256 {sha256_file(SCRIPTS / 'session113_comparison_pull.py')}",
        f"session 135 draw script (imported) sha256 {sha256_file(SCRIPTS / 'session135_aifs_draw.py')}",
        f"draw.csv sha256 {sha256_file(DRAW_CSV)}",
        f"session91_pull_airports.csv sha256 {sha256_file(S91_TABLE)}",
        f"airports (18): {' '.join(airports)}",
        f"source {S.ECMWF}<YYYYMMDD>/<HH>z/aifs-single/0p25/oper/, from {iso(FIRST_CYCLE)}; "
        f"steps {STEPS} valid on or before {iso(LIMIT)}",
        "fields: " + "; ".join(f"{p} {lv} steps {st}" for p, _, lv, st in FIELDS),
        "chunks: " + " ".join(sorted(p.parent.name for p in Path(outdir).glob("*/done.txt"))),
        "files per chunk: plan.csv.gz, aifs_<ICAO>.csv.gz, manifest.csv.gz, gaps.csv.gz, done.txt",
    ]
    p = Path(outdir) / "meta.txt"
    tmp = Path(outdir) / "meta.txt.partial"
    tmp.write_text("\n".join(lines) + "\n")
    os.replace(tmp, p)


# ------------------------------------------------------------------ verify

def load_chunks(outdir):
    out = {}
    for done in sorted(Path(outdir).glob("*/done.txt")):
        d = done.parent
        out[d.name] = d
    return out


def verify(outdir, quiet=False):
    """Returns (ok, lines)."""
    airports, _, _ = load_airports()
    L, ok = [], True
    reasons, by_hour, by_month = Counter(), Counter(), Counter()
    tot = Counter()
    for name, d in load_chunks(outdir).items():
        plan = read_gz(d / "plan.csv.gz")
        man = read_gz(d / "manifest.csv.gz")
        gaps = read_gz(d / "gaps.csv.gz")
        mg = [g for g in gaps if g["airport"] == "*"]
        vg = [g for g in gaps if g["airport"] != "*"]
        key = lambda r: (r["cycle"], r["step"], r["param"], r["level"])  # noqa: E731
        planned = {key(r) for r in plan}
        kept = {key(r) for r in man}
        gapk = {key(g) for g in mg}
        if len(planned) != len(plan) or kept & gapk or (kept | gapk) != planned or len(man) + len(mg) != len(plan):
            ok = False
            L.append(f"FAIL {name}: planned {len(plan)}, kept {len(man)}, gaps {len(mg)} do not add up")
        # every row: guards, a kept message, finite values, 18 airports
        mids = {r["msg"]: r for r in man}
        nrows = 0
        for a in airports:
            p = d / f"aifs_{a}.csv.gz"
            rows = read_gz(p) if p.exists() else []
            for r in rows:
                nrows += 1
                c = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ")
                v = dt.datetime.strptime(r["valid_utc"], "%Y-%m-%dT%H:%MZ")
                try:
                    guard_cycle(c)
                    guard_valid(v)
                except GuardError as e:
                    ok = False
                    L.append(f"FAIL {name} {a}: {e}")
                if r["airport"] != a or r["msg"] not in mids or not all(
                        math.isfinite(float(r[f"v{k}"])) for k in range(1, 5)):
                    ok = False
                    L.append(f"FAIL {name} {a}: bad row {r['cycle']} {r['step']} {r['param']}")
        extra = {p.name for p in d.glob("aifs_*.csv.gz")} - {f"aifs_{a}.csv.gz" for a in airports}
        if extra:
            ok = False
            L.append(f"FAIL {name}: files for other airports {sorted(extra)}")
        if nrows != len(man) * len(airports) - len(vg):
            ok = False
            L.append(f"FAIL {name}: rows {nrows} != kept {len(man)} x 18 - value gaps {len(vg)}")
        for r in man:
            if r["sha256"][:16] != r["msg"] or len(r["sha256"]) != 64:
                ok = False
                L.append(f"FAIL {name}: manifest row {r['msg']}")
            guard_url(r["url"])
        for g in gaps:
            reasons[g["reason"] if g["airport"] == "*" else "value: " + g["reason"]] += 1
            by_hour[g["cycle"][11:13]] += 1
            by_month[g["cycle"][:7]] += 1
        tot["chunks"] += 1
        tot["planned"] += len(plan)
        tot["kept"] += len(man)
        tot["message_gaps"] += len(mg)
        tot["value_gaps"] += len(vg)
        tot["rows"] += nrows
        tot["bytes"] += sum(int(r["bytes"]) for r in man)
    L.insert(0, f"totals: {dict(tot)}")
    L.append(f"gaps by reason: {dict(reasons) or 'none'}")
    L.append(f"gaps by cycle hour: {dict(sorted(by_hour.items())) or 'none'}")
    L.append(f"gaps by month: {dict(sorted(by_month.items())) or 'none'}")
    L.append(f"kept plus gaps equals planned in every chunk: {'PASS' if ok else 'FAIL'}")
    return ok, L


def run_verify(outdir):
    ok, L = verify(outdir)
    (Path(outdir) / "verify.txt").write_text(f"{now_utc()}\n" + "\n".join(L) + "\n")
    for x in L:
        say(x)
    say("VERIFY " + ("PASS" if ok else "FAIL"))
    if not ok:
        raise SystemExit(1)


# ------------------------------------------------------------------ gate (Step 5)

def s113_positions():
    """Session 113's AIFS positions files: {label: {(airport, set): [(lat, lon360) x 4 in v1..v4 order]}}."""
    out = {}
    for p in sorted(S113_DIR.glob("positions_aifs_*.csv")):
        lab = p.stem[len("positions_"):]
        d = {}
        for r in draw_mod.read_csv(p):
            d[(r["airport"], r["position_set"])] = [(round(float(r[f"p{k}_lat"]), 6),
                                                      round(float(r[f"p{k}_lon"]) % 360, 6)) for k in range(1, 5)]
        out[lab] = d
    return out


def gate_a(outdir, L):
    """2 m temperature at the six development airports equal to session 113's
    stored v1..v4 for the same cycles and steps, matched point by point by
    coordinates. Values compared bit for bit; nothing scored."""
    _, pts91, _ = load_airports()
    pos113 = s113_positions()
    chunks = load_chunks(outdir)
    ok = True
    for a in DEV6:
        mine = {}
        for d in chunks.values():
            for r in read_gz(d / f"aifs_{a}.csv.gz"):
                if r["param"] == "2t":
                    mine[(r["cycle"], int(r["step"]))] = [r[f"v{k}"] for k in range(1, 5)]
        cyc_set = {k[0] for k in mine}
        ref = [r for r in read_gz(S113_DIR / f"aifs_{a}.csv.gz")
               if r["position_set"] == "gfs" and r["param"] == "2t" and r["cycle"] in cyc_set]
        ours = [(round(la, 6), round(lo % 360, 6)) for la, lo, _ in pts91[a]]
        n_eq = n_cmp = n_ne = 0
        same_points = True
        for r in ref:
            k = (r["cycle"], int(r["step"]))
            p113 = pos113[r["grid"]][(a, "gfs")]
            if sorted(p113) != sorted(ours):
                same_points = False
                continue
            if k not in mine:
                continue
            n_cmp += 1
            m = dict(zip(ours, mine[k]))
            theirs = [r[f"v{j}"] for j in range(1, 5)]
            eq = all(float(m[p]).hex() == float(t).hex() for p, t in zip(p113, theirs))
            n_eq += eq
            n_ne += not eq
        mine_steps = sum(1 for k in mine if k[1] > 0)
        if not same_points:
            L.append(f"(a) {a}: session 113's gfs points differ from session 91's: reported, not compared")
            continue
        res = n_cmp > 0 and n_ne == 0
        ok &= res
        L.append(f"(a) {a}: {n_cmp} (cycle, step) pairs compared, {n_eq} equal in every bit, {n_ne} not; "
                 f"this pull's 2t steps 6 to 48: {mine_steps}; session 113 rows for these cycles: {len(ref)} "
                 f"{'PASS' if res else 'FAIL'}")
    return ok


def gate_b(outdir, L):
    S = s113()
    man = []
    for d in load_chunks(outdir).values():
        man += read_gz(d / "manifest.csv.gz")
    man.sort(key=lambda r: r["msg"])
    pick = random.Random(135).sample(man, 5)
    ok = True
    for r in pick:
        a, b = map(int, r["byte_range"].split("-"))
        got = S.get(guard_url(r["url"]), byte_range=(a, b)).content
        eq = hashlib.sha256(got).hexdigest() == r["sha256"]
        ok &= eq
        L.append(f"(b) {r['msg']} {r['cycle']} step {r['step']} {r['param']}: sha256 {'equal' if eq else 'DIFFERS'}")
    return ok


def gate_d(outdir, L):
    """Every field present in both AIFS versions, names and units per version.
    Versions by the messages' generatingProcessIdentifier and by date
    (v2 from 2026-05-12, D130.4)."""
    seen = defaultdict(set)
    for d in load_chunks(outdir).values():
        for r in read_gz(d / "manifest.csv.gz"):
            ver = "v2" if r["cycle"][:10] >= f"{V2_FIRST:%Y-%m-%d}" else "v1"
            seen[(ver, r["param"], r["level"])].add((r["shortName"], r["name"], r["units"],
                                                     r["typeOfLevel"], r["levelValue"],
                                                     r["generatingProcessIdentifier"]))
    ok = True
    for p, _, lv, _ in FIELDS:
        a, b = seen.get(("v1", p, lv), set()), seen.get(("v2", p, lv), set())
        present = bool(a) and bool(b)
        ok &= present
        strip = lambda s: {x[:5] for x in s}  # noqa: E731 - names and units, without the process id
        change = "" if strip(a) == strip(b) else "  CHANGE between versions (a reading)"
        L.append(f"(d) {p} {lv}: v1 {sorted(a) or 'ABSENT'}; v2 {sorted(b) or 'ABSENT'}{change}")
    return ok


def run_gate(outdir):
    L = []
    oka = gate_a(outdir, L)
    okb = gate_b(outdir, L)
    okc, V = verify(outdir)
    L += ["(c) " + x for x in V]
    okd = gate_d(outdir, L)
    late = 0
    for d in load_chunks(outdir).values():
        for p in d.glob("aifs_*.csv.gz"):
            late += sum(1 for r in read_gz(p)
                        if dt.datetime.strptime(r["valid_utc"], "%Y-%m-%dT%H:%MZ") > LIMIT)
    oke = late == 0
    L.append(f"(e) rows valid after {iso(LIMIT)}: {late} {'PASS' if oke else 'FAIL'}")
    res = {"a": oka, "b": okb, "c": okc, "d": okd, "e": oke}
    L.append("GATE: " + ", ".join(f"({k}) {'PASS' if v else 'FAIL'}" for k, v in res.items()))
    (Path(outdir) / "gate.txt").write_text(f"{now_utc()}\n" + "\n".join(L) + "\n")
    for x in L:
        say(x)
    if not (oka and okb and okc and oke):
        raise SystemExit("gate FAIL (a, b, c or e)")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("plan", "pull", "verify", "gate"):
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--months", help="YYYY-MM..YYYY-MM (default: all months of D130.9)")
    ap.add_argument("--days", help="YYYY-MM-DD[..YYYY-MM-DD],... (day chunks)")
    ap.add_argument("--workers", type=int, default=MAX_WORKERS)
    ap.add_argument("--outdir", default=str(DEFAULT_OUT))
    a = ap.parse_args()
    if a.workers < 1 or a.workers > MAX_WORKERS:
        raise SystemExit(f"--workers must be 1 to {MAX_WORKERS}")
    outdir = Path(a.outdir).resolve()
    if a.plan or a.pull:
        chunks = chunks_from_args(a.months, a.days)
        load_airports()
        if a.plan:
            outdir.mkdir(parents=True, exist_ok=True)
            n = Counter()
            for name, cs in sorted(chunks.items()):
                for attempt in range(1, 4):
                    try:
                        rows = plan_chunk(name, cs, outdir)
                        break
                    except GuardError:
                        raise
                    except Exception as e:  # noqa: BLE001 - tried again, as --pull does
                        say(f"  {name}: plan attempt {attempt} failed: {type(e).__name__}: {e}")
                        if attempt == 3:
                            raise SystemExit(f"plan of {name} failed 3 times; run the same command again")
                        time.sleep(300)
                c = Counter(r["status"] for r in rows)
                n.update(c)
                say(f"  {name}: {len(cs)} cycles, planned {c['planned']}, gaps {c['gap']}")
            say(f"plan: {dict(n)}")
        else:
            run_pull(chunks, outdir, a.workers)
    elif a.verify:
        run_verify(outdir)
    else:
        run_gate(outdir)


if __name__ == "__main__":
    main()
