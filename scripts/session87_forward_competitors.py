"""Session 87: the 2026-27 NBM and GFS MOS (MAV) fetch (DECISIONS D77.6, D78.7, D79).

It fetches the two competitors' 2 m temperature values that D77.6 compares the
frozen F122 models against, for each target day of a period:
  NBM  CONUS `core`, at DSM, RNO and KSFO (station code SFO).
  MAV  GFS MOS, at DSM only (IEM api/1/mos.json, station KDSM).

Modes (exactly one):
  --guard-check  Offline. Calls the guards only, with fixed cases, and prints
                 each outcome. No network call, no data read.
  --gate         Network, spent years only. Fetches a fixed sample of 21 NBM and
                 5 MAV values with the same code as --fetch and compares each
                 with data/processed/session85_competitor_points.csv (exact
                 equality). Also exercises the --fetch writers in a temporary
                 directory. Writes nothing under data/: GRIB bytes and MAV
                 responses go to a temporary directory outside the repo, deleted
                 when the gate ends.
  --fetch        2026-27, period A or B. WRITTEN BUT NOT RUN IN SESSION 87. It
                 prints counts only, never a 2026-27 value, and writes only new
                 files (see the OUT_* names below). It refuses to run if any of
                 them exists.

Where the logic comes from (copied, not imported, because importing
scripts/session85_nbm_mos_comparison.py runs code at import: it reads sys.argv and
may restart the process for LightGBM). The function-by-function list with line
numbers is in DECISIONS F129.
  - the NBM plan, `.idx` lookup, byte range, message checks (valid time, units K,
    `2t`, `.idx` date) and nearest-neighbour value: session85_nbm_mos_comparison.py
    l.113-122, 281-310, 334-511;
  - the MAV query and matching: the same file, l.514-578;
  - the period days: scripts/session86_forward_build.py l.284-322 (`last_period_a_day`,
    `validate_build_request`), and its SPEC 3.4 table parser, l.226-263.

SPEC 8.7 build requirements met here:
2. a non-finite value is rejected at load, dropped and counted;
3. each message's full validity date AND hour, its run stamp, units and short name
   are checked before its value is read;
4. the closing counts compare the values with the expected full count;
5. no write to any committed record file: `--fetch` writes new files only, with
   exclusive-create, and refuses to run if any of them exists.
(Requirement 1, the nearest report, is about observations and does not apply.)

Hard limits: in `--gate`, no valid time on or after 2026-08-01T00:00 UTC may be
requested or kept. In `--fetch`, the limit is 2027-08-01T00:00 UTC. Every valid
time is checked before any value is read. Nothing is written under data/ by
`--gate` or `--guard-check`.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

import eccodes as ec  # noqa: E402
import requests  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT / "SPEC.md"
S85_POINTS = ROOT / "data" / "processed" / "session85_competitor_points.csv"
S85_POINTS_SHA256 = "681802a27338d0bafddabffdf1bd6d2168b6dd39a2460e07964340445819a63e"  # F127.3

NBM = "https://noaa-nbm-grib2-pds.s3.amazonaws.com/"
MOS_URL = "https://mesonet.agron.iastate.edu/api/1/mos.json"
RETRIES = 3
PAUSE = 0.2

PERIOD_A_START = dt.date(2026, 8, 1)
FORWARD_LAST_DAY = dt.date(2027, 7, 31)
FORWARD_LIMIT = dt.datetime(2027, 8, 1, 0, 0)     # nothing valid at or after this in --fetch
GATE_LAST_DAY = dt.date(2026, 7, 31)              # last spent-year day (SPEC 4.3)
GATE_LIMIT = dt.datetime(2026, 8, 1, 0, 0)        # nothing valid at or after this in --gate
DAYS_AFTER_LAST = 3                               # D78.7: observations are in

COMPETITOR_STATIONS = ["DSM", "RNO", "SFO"]       # NBM at all three (D77.1)
MAV_STATION = "DSM"                               # MAV at DSM only, IEM id KDSM
MAV_IEM_ID = "KDSM"

# The fixed gate sample (session prompt 2.4). Do not change it.
_SAMPLE_5 = [dt.date(2024, 8, 1), dt.date(2024, 11, 12), dt.date(2025, 2, 18),
             dt.date(2025, 5, 28), dt.date(2025, 7, 31)]
GATE_SAMPLE = {
    "DSM": _SAMPLE_5,
    "RNO": _SAMPLE_5,
    "SFO": _SAMPLE_5 + [dt.date(2025, 8, 1), dt.date(2025, 9, 3), dt.date(2026, 4, 22),
                        dt.date(2026, 5, 6), dt.date(2026, 7, 29), dt.date(2026, 7, 31)],
}
GATE_MAV_DATES = _SAMPLE_5
# F127.3's NBM grid points (latitude, longitude 0 to 360), rounded to 6 decimals.
F127_GRID = {"DSM": (41.541124, 266.34249), "RNO": (39.483896, 240.228363),
             "SFO": (37.619643, 237.629953)}

POINT_COLS = ["airport", "period", "target_date", "competitor", "cycle", "lead",
              "valid_time", "value_c", "grid_lat", "grid_lon"]
MANIFEST_COLS = ["station", "target_date", "url", "byte_range", "idx_line", "pulled_utc",
                 "bytes", "sha256"]
DROP_COLS = ["station", "competitor", "target_date", "reason", "detail"]

REQUEST_LOG = []    # (pulled_utc, kind, url, byte_range, bytes)


class GuardError(Exception):
    """A date guard fired. The run stops."""


class Missing(Exception):
    pass


# ------------------------------------------------------------------ small helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def cycle_and_lead(d, hour):
    """SPEC 7.2 / F5 / F89 (copied from session85 l.113-122): the run at floor(H/6)x6 UTC
    on D-1, forecast hour 24 + (H mod 6). Returns (cycle datetime, lead, valid datetime)."""
    cyc = dt.datetime.combine(d - dt.timedelta(days=1), dt.datetime.min.time()) \
        + dt.timedelta(hours=(hour // 6) * 6)
    lead = 24 + hour % 6
    valid = cyc + dt.timedelta(hours=lead)
    assert valid == dt.datetime.combine(d, dt.datetime.min.time()) + dt.timedelta(hours=hour)
    return cyc, lead, valid


def get(url, kind, **kw):
    """GET with at most 3 retries, politely spaced (copied from session85 l.285-305).
    403/404 -> Missing. Every request is logged with its pull time.
    Returns (response, pulled_utc)."""
    last = None
    for i in range(RETRIES + 1):
        pulled = now_utc()
        try:
            r = requests.get(url, timeout=(10, 120), **kw)
            if r.status_code in (403, 404):
                time.sleep(PAUSE)
                raise Missing(f"HTTP {r.status_code}")
            if r.status_code in (200, 206):
                REQUEST_LOG.append((pulled, kind, r.url, kw.get("headers", {}).get("Range", ""),
                                    len(r.content)))
                time.sleep(PAUSE)
                return r, pulled
            last = f"HTTP {r.status_code}"
        except requests.exceptions.RequestException as e:
            last = f"{type(e).__name__}: {e}"
        if i < RETRIES:
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"request failed after {RETRIES} retries: {url} ({last})")


# ------------------------------------------------------------------ SPEC 3.4 and the periods

def load_spec_airports():
    """SPEC 3.4's first table: station code, target hour, airport position. Nothing typed
    in (as session86 l.226-263, which reads the second table too)."""
    text = SPEC_FILE.read_text()
    block = text[text.index("**3.4 The airport table.**"):text.index("Notes on the table:")]
    header, out = None, {}
    for ln in block.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == "station code":
            header = cells
            continue
        if set(cells[0]) <= set("-") or header is None or "target hour (UTC)" not in header:
            continue
        row = dict(zip(header, cells))
        hour = int(row["target hour (UTC)"].split(":")[0])
        out[cells[0]] = {"station": cells[0], "target_hour": hour, "cycle": (hour // 6) * 6,
                         "lat": float(row["latitude"]), "lon": float(row["longitude"])}
    if list(out) != ["EGLC", "LFPG", "DSM", "YSDU", "RNO", "SFO"]:
        raise SystemExit(f"STOP: unexpected airport set {list(out)}")
    return out


def last_period_a_day(cycle_hour, first_v17):
    """Copied from session86_forward_build.py l.284-296. The last target day D whose
    forecasting cycle (floor(H/6)*6 UTC on D-1) is before the first v17 cycle. With no
    v17 (first_v17 None) it is the last day of the forward year."""
    if first_v17 is None:
        return FORWARD_LAST_DAY
    d, last = PERIOD_A_START, None
    while d < dt.date(2028, 1, 1):
        cyc_dt = dt.datetime(d.year, d.month, d.day, cycle_hour) - dt.timedelta(days=1)
        if cyc_dt >= first_v17:
            break
        last, d = d, d + dt.timedelta(days=1)
    return last


def period_range(period, cycle_hour, first_v17):
    """(first day, last day) of a period for an airport whose GFS cycle is cycle_hour
    (D77.2: the competitor days are the airport's GFS-defined days). None if empty."""
    last_a = last_period_a_day(cycle_hour, first_v17)
    if period == "A":
        return None if last_a is None else (PERIOD_A_START, last_a)
    first_b = PERIOD_A_START if last_a is None else last_a + dt.timedelta(days=1)
    return None if first_b > FORWARD_LAST_DAY else (first_b, FORWARD_LAST_DAY)


def validate_request(period, first_v17, no_v17, decision, run_date, cycles):
    """The --fetch guards, as a pure function (adapted from session86 l.299-322). `cycles`
    maps every airport to its GFS cycle hour: the timing guard reads the latest last
    day over ALL six airports. An empty reasons list means the guards allow the run.
    Returns (reasons, ranges)."""
    reasons, ranges = [], {}
    if period not in ("A", "B"):
        reasons.append("needs --period A or --period B")
    if first_v17 is None and not no_v17:
        reasons.append("needs --first-v17-cycle (from a DECISIONS entry, D73.3) or --no-v17")
    if first_v17 is not None and no_v17:
        reasons.append("--first-v17-cycle and --no-v17 are exclusive")
    if period == "B" and no_v17:
        reasons.append("period B needs --first-v17-cycle: --no-v17 with --period B is refused (D73.3)")
    if not decision:
        reasons.append("needs --decision <entry number>")
    if period in ("A", "B"):
        for st, cyc in cycles.items():
            rng = period_range(period, cyc, first_v17 if not no_v17 else None)
            ranges[st] = rng
            if rng is None:
                reasons.append(f"{st}: no period-{period} day")
            elif rng[1] >= FORWARD_LIMIT.date():
                reasons.append(f"{st}: last period-{period} target day {rng[1]} is on or after "
                               f"{FORWARD_LIMIT.date()}")
        known = [r[1] for r in ranges.values() if r is not None]
        if known and run_date < max(known) + dt.timedelta(days=DAYS_AFTER_LAST):
            reasons.append(f"run date {run_date} is before the latest last day {max(known)} "
                           f"plus {DAYS_AFTER_LAST} days")
    return reasons, ranges


def check_gate_date(d):
    """--gate hard-stops on any target date after 2026-07-31."""
    if d > GATE_LAST_DAY:
        raise GuardError(f"gate date {d} is after {GATE_LAST_DAY}")


def check_outputs_absent(paths):
    """--fetch refuses to run if any output path exists (SPEC 8.7 item 5)."""
    present = [str(p) for p in paths if Path(p).exists()]
    if present:
        raise GuardError("an output file already exists: " + ", ".join(present))


def output_paths(period):
    diag = ROOT / "data" / "raw" / "diagnostics" / "forward2627"
    return {
        "points": ROOT / "data" / "processed" / f"forward2627_period{period}_competitor_points.csv",
        "points_meta": ROOT / "data" / "processed" / f"forward2627_period{period}_competitor_points.csv.meta.txt",
        "manifest": diag / f"period{period}_nbm_manifest.csv",
        "drops": diag / f"period{period}_competitor_drop_log.csv",
        "mos": ROOT / "data" / "raw" / "iem_mos" / "forward2627" / f"period{period}",
    }


def guard_check():
    print("SESSION 87 competitors --guard-check (offline: no network call, no data read)")
    cycles = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 0, "RNO": 18, "SFO": 18}
    today = dt.datetime.now(dt.timezone.utc).date()
    print(f"run date (UTC): {today}")
    ok_all = True

    def show(label, refused, why, expect_refused, expect_text=None):
        nonlocal ok_all
        good = (refused == expect_refused) and (expect_text is None or any(expect_text in w for w in why))
        ok_all &= good
        print(f"  [{'OK ' if good else 'BAD'}] {label}: {'REFUSED' if refused else 'allowed'}"
              + (f" ({'; '.join(why)})" if why else ""))

    print("gate date guard:")
    for d, expect in ((dt.date(2026, 7, 31), False), (dt.date(2026, 8, 1), True)):
        try:
            check_gate_date(d)
            show(f"gate date {d}", False, [], expect)
        except GuardError as e:
            show(f"gate date {d}", True, [str(e)], expect)
    print("fetch guards (pure function; nothing is fetched):")
    r, _ = validate_request("A", None, False, "D79", today, cycles)
    show("--fetch with neither --first-v17-cycle nor --no-v17", bool(r), r, True, "needs --first-v17-cycle")
    r, _ = validate_request("B", None, True, "D79", dt.date(2028, 3, 1), cycles)
    show("--fetch --period B --no-v17", bool(r), r, True, "--no-v17 with --period B is refused")
    r, rng = validate_request("A", dt.datetime(2026, 11, 15, 0), False, "D79", today, cycles)
    print("    period-A range per airport for a first v17 cycle of 2026-11-15T00: "
          + ", ".join(f"{k} {v[0]}..{v[1]}" for k, v in rng.items()))
    show("--fetch whose last day + 3 days is after the run date", bool(r), r, True, "before the latest last day")
    r, _ = validate_request("A", dt.datetime(2027, 9, 1, 0), False, "D79", dt.date(2028, 3, 1), cycles)
    show("--fetch with a target date on or after 2027-08-01 (simulated run date 2028-03-01)", bool(r), r, True,
         "on or after 2027-08-01")
    print("positive controls (simulated run dates; the same pure function):")
    r, _ = validate_request("A", dt.datetime(2026, 11, 15, 0), False, "D79", dt.date(2026, 11, 18), cycles)
    show("period A, first v17 cycle 2026-11-15T00, run date 2026-11-18 (last day + 3)", bool(r), r, False)
    r, _ = validate_request("A", dt.datetime(2026, 11, 15, 0), False, "D79", dt.date(2026, 11, 17), cycles)
    show("period A, first v17 cycle 2026-11-15T00, run date 2026-11-17 (one day early)", bool(r), r, True,
         "before the latest last day")
    r, rng = validate_request("B", dt.datetime(2026, 11, 15, 0), False, "D79", dt.date(2027, 8, 3), cycles)
    print("    period-B range per airport for a first v17 cycle of 2026-11-15T00: "
          + ", ".join(f"{k} {v[0]}..{v[1]}" for k, v in rng.items()))
    show("period B, first v17 cycle 2026-11-15T00, run date 2027-08-03", bool(r), r, False)
    print("output files already exist (temporary directory outside the repo):")
    tmp = Path(tempfile.mkdtemp(prefix="session87_guard_"))
    try:
        paths = [tmp / "points.csv", tmp / "manifest.csv"]
        try:
            check_outputs_absent(paths)
            show("no output exists", False, [], False)
        except GuardError as e:
            show("no output exists", True, [str(e)], False)
        paths[1].write_text("x")
        try:
            check_outputs_absent(paths)
            show("one output exists", False, [], True)
        except GuardError as e:
            show("one output exists", True, [str(e)], True, "already exists")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  temporary directory deleted: {not tmp.exists()}")
    print("all cases behaved as the session prompt's Step 2.3 says" if ok_all
          else "A CASE DID NOT BEHAVE: FIX THE SCRIPT")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ NBM

def nbm_url(cyc, lead):
    """Copied from session85 l.308-310."""
    return (f"{NBM}blend.{cyc:%Y%m%d}/{cyc:%H}/core/"
            f"blend.t{cyc:%H}z.core.f{lead:03d}.co.grib2")


META_KEYS = ["shortName", "name", "units", "typeOfLevel", "level", "stepType", "stepRange",
             "dataDate", "dataTime", "validityDate", "validityTime", "gridType", "Nx", "Ny",
             "DxInMetres", "DyInMetres", "latitudeOfFirstGridPointInDegrees",
             "longitudeOfFirstGridPointInDegrees", "LoVInDegrees", "Latin1InDegrees",
             "Latin2InDegrees", "packingType", "numberOfDataPoints", "discipline",
             "parameterCategory", "parameterNumber", "missingValue"]


def grib_meta(gid):
    """Copied from session85 l.323-331."""
    k = {}
    for key in META_KEYS:
        try:
            k[key] = ec.codes_get(gid, key)
        except Exception:  # noqa: BLE001
            k[key] = None
    return k


def add_drop(drops, counts, st, comp, d, reason, detail=""):
    counts.setdefault((st, comp), {}).setdefault(reason, 0)
    counts[(st, comp)][reason] += 1
    drops.append([st, comp, d.isoformat(), reason, detail])


def fetch_nbm(targets, spec, period, tmpdir, valid_limit, vcheck_report=False):
    """NBM 2 m temperature for the (station, day) targets. Adapted from session85
    pull_nbm l.334-511. Every message's validity is checked before its value is read
    (a message on or after valid_limit is discarded unread and the step stops with
    GuardError). Returns dict(points, manifest, drops, dropcounts, gridpts, files,
    bytes, idx_info)."""
    plan = {}
    for st, d in targets:
        cyc, lead, valid = cycle_and_lead(d, spec[st]["target_hour"])
        if valid >= valid_limit:
            raise GuardError(f"planned valid time {valid} is on or after {valid_limit}; nothing requested")
        plan.setdefault((cyc, lead), []).append((st, d, valid))
    points, manifest, drops, dropcounts = [], [], [], {}
    gridpts = {st: {} for st in COMPETITOR_STATIONS}
    idx_info, n_bytes, n_ok = {}, 0, 0
    for (cyc, lead), items in sorted(plan.items()):
        url = nbm_url(cyc, lead)
        want = f"TMP:2 m above ground:{lead} hour fcst:"

        def drop_all(reason, detail):
            for st, d, _ in items:
                add_drop(drops, dropcounts, st, "nbm", d, reason, detail)

        try:
            r, _ = get(url + ".idx", "nbm idx")
        except Missing as e:
            drop_all("no .idx", f"{url}.idx {e}")
            continue
        lines = r.text.splitlines()
        parsed = []
        for ln in lines:
            f = ln.split(":")
            parsed.append((int(f[0]), int(f[1]), f[2], ":".join(f[3:]), ln))
        hits = [j for j, p in enumerate(parsed) if p[3] == want]
        if len(hits) != 1:
            drop_all("no matching .idx line" if not hits else "several matching .idx lines",
                     f"{url} {len(hits)} idx lines match")
            continue
        j = hits[0]
        if parsed[j][2] != f"d={cyc:%Y%m%d%H}":
            drop_all("failed check", f"{url} idx date {parsed[j][2]}")
            continue
        off = parsed[j][1]
        if j + 1 < len(parsed):
            end = parsed[j + 1][1] - 1
        else:
            end = int(requests.head(url, timeout=(10, 60)).headers["Content-Length"]) - 1
        try:
            r, pulled = get(url, "nbm message", headers={"Range": f"bytes={off}-{end}"})
        except Missing as e:
            drop_all("no file", f"{url} {e}")
            continue
        if len(r.content) != end - off + 1:
            raise RuntimeError(f"short read {len(r.content)} B for {url}")
        n_bytes += len(r.content)
        path = os.path.join(tmpdir, "msg.grib2")
        with open(path, "wb") as fh:
            fh.write(r.content)
        digest = sha256_bytes(r.content)
        with open(path, "rb") as fh:
            gid = ec.codes_grib_new_from_file(fh)
            try:
                meta = grib_meta(gid)
                vd, vt = meta["validityDate"], meta["validityTime"]
                valid = dt.datetime.strptime(f"{vd}{int(vt):04d}", "%Y%m%d%H%M")
                if valid >= valid_limit:       # SPEC 8.7 item 3: full date and hour, before any value
                    raise GuardError(f"a message is valid at {valid}, on or after {valid_limit}; "
                                     f"discarded unread ({url})")
                exp_valid = items[0][2]
                if not (valid == exp_valid and meta["units"] == "K" and meta["shortName"] == "2t"):
                    drop_all("failed check", f"{url}: valid {valid}, units {meta['units']}, "
                             f"shortName {meta['shortName']}")
                    continue
                idx_info[(cyc, lead)] = dict(url=url, idx_lines=len(lines), meta=meta)
                for st, d, v in items:
                    nn = ec.codes_grib_find_nearest(gid, spec[st]["lat"], spec[st]["lon"])[0]
                    val = float(nn.value)
                    if not math.isfinite(val) or val == meta["missingValue"]:
                        add_drop(drops, dropcounts, st, "nbm", d, "missing value", url)
                        continue
                    gp = (round(nn.lat, 6), round(nn.lon, 6))
                    gridpts[st].setdefault(gp, [0, nn.distance])
                    gridpts[st][gp][0] += 1
                    points.append(dict(airport=st, period=period, target_date=d.isoformat(),
                                       competitor="nbm", cycle=cyc.strftime("%Y-%m-%dT%H:%MZ"),
                                       lead=lead, valid_time=v.strftime("%Y-%m-%dT%H:%MZ"),
                                       value_c=repr(val - 273.15), grid_lat=repr(nn.lat),
                                       grid_lon=repr(nn.lon)))
            finally:
                ec.codes_release(gid)
                os.remove(path)
        n_ok += 1
        manifest.append([",".join(sorted({st for st, _, _ in items})),
                         ",".join(sorted({d.isoformat() for _, d, _ in items})),
                         url, f"{off}-{end}", parsed[j][4], pulled, len(r.content), digest])
    return dict(points=points, manifest=manifest, drops=drops, dropcounts=dropcounts,
                gridpts=gridpts, files=len(plan), files_ok=n_ok, bytes=n_bytes, idx_info=idx_info)


# ------------------------------------------------------------------ MAV

def fetch_mav(days, spec, period, valid_limit, check_all_times):
    """MAV (GFS MOS) at KDSM for each day. Adapted from session85 pull_mav l.514-578.
    Only the one projection valid at the target hour is read (its `tmp`). Every other
    projection's TIME fields are read (to match, and to check the UTC fields); their values
    are never read, printed or used. If check_all_times, any projection valid on or after
    valid_limit stops the step (used by --gate). The raw response body is kept unchanged.
    Returns dict(got, points, drops, dropcounts, utc_rows, utc_bad)."""
    hour = spec[MAV_STATION]["target_hour"]
    got, points, drops, dropcounts = [], [], [], {}
    utc_rows = utc_bad = 0
    for d in days:
        cyc, lead, valid = cycle_and_lead(d, hour)
        if valid >= valid_limit:
            raise GuardError(f"planned MAV valid time {valid} is on or after {valid_limit}; nothing requested")
        rt = cyc.strftime("%Y-%m-%d %H:%MZ")
        try:
            r, pulled = get(MOS_URL, "mav", params={"station": MAV_IEM_ID, "model": "GFS", "runtime": rt})
        except Missing as e:
            add_drop(drops, dropcounts, MAV_STATION, "mav", d, "no MAV run", f"{rt}: {e}")
            continue
        body = r.content
        rows = json.loads(body).get("data", [])
        got.append(dict(day=d, runtime=rt, url=r.url, pulled=pulled, body=body, n_rows=len(rows)))
        fts = []
        for x in rows:                              # time fields only
            s = str(x["ftime"]).replace("T", " ").rstrip("Z")[:16]
            fts.append(dt.datetime.strptime(s, "%Y-%m-%d %H:%M"))
        if check_all_times and any(t >= valid_limit for t in fts):
            raise GuardError(f"MAV run {rt} has a projection valid on or after {valid_limit}; "
                             "discarded without reading values")
        if not rows:
            add_drop(drops, dropcounts, MAV_STATION, "mav", d, "no MAV run", f"{rt}: no rows")
            continue
        bad = 0
        for x in rows:                              # UTC fields equal the plain ones (as session 85)
            utc_rows += 1
            for a, b in (("ftime", "ftime_utc"), ("runtime", "runtime_utc")):
                if b in x and str(x[a]).replace(" ", "T")[:16] != str(x[b])[:16]:
                    bad += 1
        utc_bad += bad
        rts = {str(x.get("runtime", "")) for x in rows} - {""}
        if bad or any(not t.startswith(cyc.strftime("%Y-%m-%d")) or cyc.strftime("%H:%M") not in t
                      for t in rts):
            add_drop(drops, dropcounts, MAV_STATION, "mav", d, "failed check",
                     f"{rt}: runtime field {sorted(rts)}, UTC-field mismatches {bad}")
            continue
        match = [x for x, t in zip(rows, fts) if t == valid]
        if len(match) != 1:
            add_drop(drops, dropcounts, MAV_STATION, "mav", d, "no projection", f"{len(match)} rows at {valid}")
            continue
        if valid >= valid_limit:
            raise GuardError(f"the projection valid at {valid} is on or after {valid_limit}; discarded unread")
        raw = match[0].get("tmp")
        try:
            tmp_f = float(raw)
        except (TypeError, ValueError):
            tmp_f = float("nan")
        if raw in (None, "", "M") or not math.isfinite(tmp_f):
            add_drop(drops, dropcounts, MAV_STATION, "mav", d, "missing value", f"{rt}: tmp {raw!r}")
            continue
        points.append(dict(airport=MAV_STATION, period=period, target_date=d.isoformat(),
                           competitor="mav", cycle=cyc.strftime("%Y-%m-%dT%H:%MZ"), lead=lead,
                           valid_time=valid.strftime("%Y-%m-%dT%H:%MZ"),
                           value_c=repr((tmp_f - 32.0) * 5.0 / 9.0), grid_lat="", grid_lon=""))
    return dict(got=got, points=points, drops=drops, dropcounts=dropcounts,
                utc_rows=utc_rows, utc_bad=utc_bad)


# ------------------------------------------------------------------ writers (SPEC 2.3, 8.7 item 5)

def write_new(path, data, binary=False):
    """Exclusive create: never overwrites."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "xb" if binary else "x", **({} if binary else {"newline": ""})) as f:
        f.write(data)


def csv_text(cols, rows):
    import io
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def write_outputs(period, nbm, mav, paths, header_note, args_text):
    """Writes the points CSV and its .meta.txt, the NBM manifest, the drop log, and
    the raw MAV responses (each with its .meta.txt), as new files only. `paths` holds the
    five targets, so --gate can exercise this in a temporary directory."""
    for k in ("points", "points_meta", "manifest", "drops"):
        if paths[k].exists():
            raise SystemExit(f"STOP: {paths[k]} already exists; not overwriting (SPEC 8.7 item 5)")
    if paths["mos"].exists():
        raise SystemExit(f"STOP: {paths['mos']} already exists; not overwriting")
    pts = nbm["points"] + mav["points"]
    write_new(paths["points"], csv_text(POINT_COLS, [[p[c] for c in POINT_COLS] for p in pts]))
    write_new(paths["manifest"], csv_text(MANIFEST_COLS, nbm["manifest"]))
    write_new(paths["drops"], csv_text(DROP_COLS, nbm["drops"] + mav["drops"]))
    for g in mav["got"]:
        fn = f"{MAV_IEM_ID}_GFS_{g['runtime'][:10].replace('-', '')}T{g['runtime'][11:13]}Z.json"
        write_new(paths["mos"] / fn, g["body"], binary=True)
        write_new(paths["mos"] / (fn + ".meta.txt"),
                  "Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
                  f"file        : {fn}\nsource      : Iowa Environmental Mesonet MOS archive (GFS MOS, MAV)\n"
                  f"pulled at   : {g['pulled']} (UTC)\ntool        : python requests "
                  f"(scripts/session87_forward_competitors.py)\nexact URL requested:\n{g['url']}\n")
    meta = [header_note, f"period: {period}", args_text,
            f"NBM bucket: {NBM} (anonymous HTTPS)",
            "NBM message: the one .idx line exactly 'TMP:2 m above ground:<lead> hour fcst:'; value at "
            "the nearest grid point to the SPEC 3.4 station position (eccodes codes_grib_find_nearest), "
            "K - 273.15.",
            f"MAV: {MOS_URL}, station {MAV_IEM_ID}, model GFS, 18z runs; tmp in whole degF, (F - 32) * 5 / 9; "
            f"raw responses under {paths['mos'].name}/ with the query and pull time in each .meta.txt.",
            f"values: nbm {sum(1 for p in nbm['points'])}, mav {len(mav['points'])}",
            f"drops: {len(nbm['drops']) + len(mav['drops'])} (see {paths['drops'].name})",
            f"NBM files: {nbm['files']} planned, {nbm['files_ok']} read, bytes {nbm['bytes']}",
            f"MAV responses: {len(mav['got'])}", "", "NBM files read (URL, byte range, .idx line):"]
    meta += [f"{m[2]} bytes={m[3]} idx: {m[4]}" for m in nbm["manifest"]]
    meta += ["", "MAV queries (file, pull time, exact URL):"]
    meta += [f"{g['runtime']}  {g['pulled']}  {g['url']}" for g in mav["got"]]
    write_new(paths["points_meta"], "\n".join(meta) + "\n")


def expected_counts(spec, ranges):
    """Expected full value counts: NBM at each of DSM, RNO, SFO; MAV at DSM."""
    out = {}
    for st in COMPETITOR_STATIONS:
        out[(st, "nbm")] = (ranges[st][1] - ranges[st][0]).days + 1
    out[(MAV_STATION, "mav")] = out[(MAV_STATION, "nbm")]
    return out


# ------------------------------------------------------------------ --fetch (written, not run in session 87)

def run_fetch(args):
    spec = load_spec_airports()
    cycles = {st: a["cycle"] for st, a in spec.items()}
    run_date = dt.datetime.now(dt.timezone.utc).date()
    first_v17 = dt.datetime.strptime(args.first_v17_cycle, "%Y-%m-%dT%H") if args.first_v17_cycle else None
    reasons, ranges = validate_request(args.period, first_v17, args.no_v17, args.decision, run_date, cycles)
    print(f"--fetch period {args.period}; decision {args.decision}; run date (UTC) {run_date}; "
          f"first v17 cycle {args.first_v17_cycle or 'none (--no-v17)'}")
    print("target-day range per airport: "
          + ", ".join(f"{k} {v[0]}..{v[1]}" if v else f"{k} none" for k, v in ranges.items()))
    if reasons:
        raise SystemExit("REFUSED: " + "; ".join(reasons))
    paths = output_paths(args.period)
    try:
        check_outputs_absent(list(paths.values()))
    except GuardError as e:
        raise SystemExit("REFUSED: " + str(e))
    targets = []
    for st in COMPETITOR_STATIONS:
        d = ranges[st][0]
        while d <= ranges[st][1]:
            targets.append((st, d))
            d += dt.timedelta(days=1)
    tmpdir = tempfile.mkdtemp(prefix="session87_fetch_")
    try:
        nbm = fetch_nbm(targets, spec, args.period, tmpdir, FORWARD_LIMIT)
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)
    mav_days = [d for st, d in targets if st == MAV_STATION]
    mav = fetch_mav(mav_days, spec, args.period, FORWARD_LIMIT, check_all_times=False)
    write_outputs(args.period, nbm, mav, paths,
                  f"Period {args.period} competitor values for the 2026-27 tests (D77.6). "
                  f"Decision entry: {args.decision}.",
                  f"first v17 cycle: {args.first_v17_cycle or 'none'}; run date (UTC) {run_date}")
    print_counts(nbm, mav, expected_counts(spec, ranges))
    return 0


def print_counts(nbm, mav, expected):
    """Counts only. Never a value."""
    print("\nvalues per airport and competitor against the expected full count:")
    have = {}
    for p in nbm["points"] + mav["points"]:
        have[(p["airport"], p["competitor"])] = have.get((p["airport"], p["competitor"]), 0) + 1
    for k, n in expected.items():
        print(f"  {k[0]:4s} {k[1]:4s} values {have.get(k, 0):>4d} of {n:>4d}; dropped {n - have.get(k, 0)}")
    reasons = {}
    for row in nbm["drops"] + mav["drops"]:
        reasons[(row[0], row[1], row[3])] = reasons.get((row[0], row[1], row[3]), 0) + 1
    print(f"  drops by reason: {dict(sorted(reasons.items())) or 'none'}")
    print(f"  NBM files: {nbm['files']} planned, {nbm['files_ok']} read; bytes {nbm['bytes']:,}; "
          f"MAV responses {len(mav['got'])}")
    print("  NBM grid point per station (eccodes nearest neighbour):")
    for st, g in nbm["gridpts"].items():
        for (la, lo), (n, dist) in g.items():
            print(f"    {st}: {la}, {lo}, distance {dist:.3f} km, used {n} times")
        print(f"    {st}: {'unchanged across the window' if len(g) == 1 else 'CHANGES across the window'}"
              f" ({len(g)} distinct)")


# ------------------------------------------------------------------ --gate (spent years only)

def run_gate(args):
    print("SESSION 87 competitors --gate (network; spent years only)")
    print(f"gate start (UTC): {now_utc()}")
    import eccodes
    print(f"python {sys.version.split()[0]}, eccodes {eccodes.__version__}, requests {requests.__version__}")
    spec = load_spec_airports()
    for st, ds in GATE_SAMPLE.items():
        for d in ds:
            check_gate_date(d)
    n_nbm = sum(len(v) for v in GATE_SAMPLE.values())
    print(f"sample: NBM {n_nbm} values (DSM {len(GATE_SAMPLE['DSM'])}, RNO {len(GATE_SAMPLE['RNO'])}, "
          f"SFO {len(GATE_SAMPLE['SFO'])}); MAV {len(GATE_MAV_DATES)} values (DSM)")
    have = sha256_file(S85_POINTS)
    print(f"{S85_POINTS.relative_to(ROOT)} SHA-256 {have}; F127.3 {S85_POINTS_SHA256}; equal: "
          f"{have == S85_POINTS_SHA256}")
    if have != S85_POINTS_SHA256:
        raise SystemExit("STOP: the session 85 points file differs from F127.3")
    stored = {}
    with open(S85_POINTS) as f:
        for r in csv.DictReader(f):
            stored[(r["airport"], r["target_date"], r["competitor"])] = r
    targets = [(st, d) for st in COMPETITOR_STATIONS for d in GATE_SAMPLE[st]]
    tmp = Path(tempfile.mkdtemp(prefix="session87_gate_"))
    print(f"temporary directory (outside the repo, deleted at the end): {tmp}")
    n_bad = 0
    try:
        nbm = fetch_nbm(targets, spec, "gate", str(tmp), GATE_LIMIT)
        mav = fetch_mav(GATE_MAV_DATES, spec, "gate", GATE_LIMIT, check_all_times=True)
        print(f"\nNBM: files planned {nbm['files']}, read {nbm['files_ok']}, bytes {nbm['bytes']:,}; "
              f"values {len(nbm['points'])} of {n_nbm}; drops {nbm['dropcounts'] or 'none'}")
        print(f"MAV: responses {len(mav['got'])}, values {len(mav['points'])} of {len(GATE_MAV_DATES)}; "
              f"drops {mav['dropcounts'] or 'none'}; UTC fields checked on {mav['utc_rows']} projections, "
              f"unequal {mav['utc_bad']} (time fields only)")
        print("\ncomparison with the session 85 points (exact equality of the stored value; NBM grid point):")
        n_val_ok = n_grid_ok = 0
        for p in nbm["points"] + mav["points"]:
            s = stored.get((p["airport"], p["target_date"], p["competitor"]))
            if s is None:
                print(f"  NO STORED ROW {p['airport']} {p['target_date']} {p['competitor']}")
                n_bad += 1
                continue
            v_eq = float(p["value_c"]) == float(s["value_c"])
            g_eq = (p["grid_lat"] == s["grid_lat"] and p["grid_lon"] == s["grid_lon"]) \
                if p["competitor"] == "nbm" else True
            n_val_ok += v_eq
            n_grid_ok += g_eq
            n_bad += (not v_eq) + (not g_eq)
            print(f"  {p['airport']:4s} {p['competitor']:4s} {p['target_date']}  value equal: {v_eq}  "
                  f"grid point equal: {g_eq if p['competitor'] == 'nbm' else 'n/a'}"
                  + ("" if v_eq else f"  fetched {p['value_c']} stored {s['value_c']}"))
        n_nbm_ok = sum(1 for p in nbm["points"]
                       if float(p["value_c"]) == float(stored[(p["airport"], p["target_date"], "nbm")]["value_c"]))
        n_mav_ok = sum(1 for p in mav["points"]
                       if float(p["value_c"]) == float(stored[(p["airport"], p["target_date"], "mav")]["value_c"]))
        print(f"NBM values equal: {n_nbm_ok} of {n_nbm}; MAV values equal: {n_mav_ok} of {len(GATE_MAV_DATES)}")
        print("NBM grid point against F127.3's table (6 decimals):")
        for st, g in nbm["gridpts"].items():
            for (la, lo), (n, dist) in g.items():
                same = (la, lo) == F127_GRID[st]
                n_bad += not same
                print(f"  {st}: {la}, {lo} (F127.3 {F127_GRID[st]}), distance {dist:.3f} km, used {n}; equal: {same}")
        print("NBM version check per file read (name, units, level, grid, packing):")
        for (cyc, lead), info in sorted(nbm["idx_info"].items()):
            m = info["meta"]
            print(f"  {cyc:%Y-%m-%d %H}z f{lead:03d}: .idx lines {info['idx_lines']}; message name "
                  f"{m['name']!r}, shortName {m['shortName']}, units {m['units']}, level {m['typeOfLevel']} "
                  f"{m['level']}, grid {m['gridType']} {m['Nx']}x{m['Ny']} dx {m['DxInMetres']}, packing "
                  f"{m['packingType']}")
        print("\n--- exercising the --fetch writers in the temporary directory (nothing is written under data/)")
        paths = {"points": tmp / "w" / "points.csv", "points_meta": tmp / "w" / "points.csv.meta.txt",
                 "manifest": tmp / "w" / "diag" / "manifest.csv", "drops": tmp / "w" / "diag" / "drops.csv",
                 "mos": tmp / "w" / "mos"}
        write_outputs("gate", nbm, mav, paths, "gate exercise (spent years)", "arguments: --gate")
        back = list(csv.DictReader(open(paths["points"])))
        pts = nbm["points"] + mav["points"]
        same = len(back) == len(pts) and all(b[c] == str(p[c]) for b, p in zip(back, pts) for c in POINT_COLS)
        print(f"wrote points, manifest, drop log and {len(mav['got'])} raw MAV responses; points read back "
              f"equal: {same}")
        raw_same = all((paths["mos"] / f"{MAV_IEM_ID}_GFS_{g['runtime'][:10].replace('-', '')}T"
                        f"{g['runtime'][11:13]}Z.json").read_bytes() == g["body"] for g in mav["got"])
        print(f"raw MAV responses read back byte-equal: {raw_same}")
        n_bad += (not same) + (not raw_same)
        try:
            write_outputs("gate", nbm, mav, paths, "second write", "arguments: --gate")
            print("BAD: a second write did not refuse")
            n_bad += 1
        except SystemExit as e:
            print(f"a second write refused, as required: {e}")
        print("\n--- every request made (pull time UTC, kind, URL, byte range, bytes)")
        for pulled, kind, url, rng, n in sorted(REQUEST_LOG):
            print(f"{pulled}  {kind:12s} {url}  {rng}  {n}")
        by = {}
        for _, kind, _, _, n in REQUEST_LOG:
            by.setdefault(kind, [0, 0])
            by[kind][0] += 1
            by[kind][1] += n
        print(f"requests: {len(REQUEST_LOG)}; by kind (count, bytes): {by}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\ntemporary directory deleted: {not tmp.exists()}")
    print(f"mismatches: {n_bad}")
    print(f"GATE: {'PASSED' if n_bad == 0 else 'FAILED'}")
    print(f"gate end (UTC): {now_utc()}")
    return 0 if n_bad == 0 else 1


# ------------------------------------------------------------------ entry point

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--guard-check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--fetch", action="store_true")
    ap.add_argument("--period", default=None, help="--fetch only: A or B")
    ap.add_argument("--first-v17-cycle", default=None, help="--fetch only: YYYY-MM-DDTHH, from a DECISIONS entry")
    ap.add_argument("--no-v17", action="store_true", help="--fetch only: no operational v17 cycle by 2027-07-31")
    ap.add_argument("--decision", default=None, help="--fetch only: the DECISIONS entry, printed in the output")
    a = ap.parse_args()
    try:
        if a.guard_check:
            return guard_check()
        if a.gate:
            return run_gate(a)
        return run_fetch(a)
    except GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
