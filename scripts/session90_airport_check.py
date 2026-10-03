#!/usr/bin/env python3
"""Session 90: the stage C airport metadata check and the claim batch draw.

This is DECISIONS D82's Step 3 and Step 4 (docs/session-90.md). It has two
modes, run one after the other:

  --collect   Step 3. For the 47 airports of D82.6: IEM identity and position
              (3.1), the GFS grid box (3.2), the land-sea mask and model
              terrain height from one spent-year GRIB file (3.3), saved hourly
              observations and counts only (3.4), DWD MOSMIX stations and the
              NBM domain (3.5). Intermediate results go to a JSON state file
              outside the repo (--state).
  --decide    Step 4 and Step 5.1. Apply D82.7(a) and (b) to the counts, run
              D82.7(d)'s draw once, and write data/processed/session90_airports.csv.

Hard limits (docs/session-90.md):
  - Nothing valid after 2026-07-31T23:59 UTC is requested, kept or counted.
  - Observations are counted only. No temperature or dew point value is
    printed, stored in the state file or summarised: a report is kept in
    memory only as "has a usable temperature, yes or no".
  - From GFS, only two messages are read: LAND:surface and HGT:surface.
  - No forecast score of any kind is computed.
  - Committed files under data/ are never changed. New files are written
    with mode "x", so an existing file stops the run.

No em-dashes in any text here (D76.6).
"""
import argparse
import csv
import datetime as dt
import hashlib
import json
import math
import random
import re
import shutil
import sys
import tempfile
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
import eccodes as ec

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
OUT_CSV = ROOT / "data" / "processed" / "session90_airports.csv"

LIMIT = dt.datetime(2026, 7, 31, 23, 59)        # nothing later than this, UTC (D82.4, hard scope guard)
FIRST_UTC = dt.datetime(2021, 3, 24, 0, 0)
HELD_OUT_START = dt.date(2024, 8, 1)
SEED = 20261003                                  # D82.7(d)

# D82.6: the owner's 47 airports, in the owner's order, with the owner's region label.
REGIONS = [
    ("Europe", "EHAM LTAC EFHK LTFM EGLC LEMD LIMC UUWW EDDM LFPB EPWA"),
    ("North America", "KATL KAUS KORD KDAL KBKF KHOU KLAX MMMX KMIA KLGA KSFO KSEA CYYZ"),
    ("South America", "SAEZ SBGR"),
    ("Asia", "ZBAA RKPK ZUUU ZUCK ZGGG OEJN OPKC WMKK VILK RPLL ZSQD RKSI ZSPD ZGSZ WSSS RCSS LLBG RJTT ZHHH"),
    ("Africa", "FACT"),
    ("Oceania", "NZWN"),
]
AIRPORTS = [(code, region) for region, codes in REGIONS for code in codes.split()]
REGION_OF = dict(AIRPORTS)
# D82.7(c): strata in this order, with sizes. "South" is South America, Africa and Oceania together.
STRATA = [("Europe", 1), ("North America", 2), ("Asia", 2), ("South", 1)]
STRATUM_OF = {"Europe": "Europe", "North America": "North America", "Asia": "Asia",
              "South America": "South", "Africa": "South", "Oceania": "South"}
SPENT = {"EGLC": "spent (EGLC, D82.7(a))", "KSFO": "spent (KSFO, D82.7(a))"}
EXCLUDED = {"LFPB": "excluded (LFPB is about 9 km from LFPG, a development airport, D82.7(a))"}
COMMITTED = {"EGLC": "EGLC", "KSFO": "SFO"}      # airports whose observation files are already committed
# Committed airports used only to check the counting code against F131.6 (UTC day counts).
CODE_CHECK = {"EGLC": ("EGLC", 1933), "LFPG": ("LFPG", 1875), "DSM": ("DSM", 1946),
              "YSDU": ("YSDU", 1690), "RNO": ("RNO", 1930), "SFO": ("SFO", 1931)}
SPEC34 = {"EGLC": (51.5053, 0.0553, 5), "KSFO": (37.619, -122.3749, 5)}   # SPEC 3.4: lat, lon, elevation
LFPG_POS = (49.0153, 2.5344)                                              # SPEC 3.4
KSFO_GRID = (37.54637, -122.34375)                                        # SPEC 3.4 grid point (check only)

PIECES = [("2021-03-24", "2021-12-31"), ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"),
          ("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]
IEM_STATION = "https://mesonet.agron.iastate.edu/api/1/station/{}.json"
IEM_ASOS = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
HEADER = "station,valid,lon,lat,elevation,tmpc,dwpc"

GFS_BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
GFS_RUN = (dt.date(2024, 3, 14), 0)              # run date, cycle (a spent-year file, D82 prompt Step 3.3)
CFG = "https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/mosmix_stationskatalog.cfg?view=nasPublication"

LOG = []                                          # (utc time, source, url, status, bytes)
_last_iem = [0.0]


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def get(url, source, headers=None, iem=False, timeout=300):
    """One request at a time. IEM calls are at least 1.2 s apart. Retry only
    on network errors, HTTP 429 and 5xx, with a growing wait, at most 5 times."""
    waits = [2, 4, 8, 16, 32]
    for attempt in range(6):
        if iem:
            gap = time.time() - _last_iem[0]
            if gap < 1.2:
                time.sleep(1.2 - gap)
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
        except requests.RequestException as e:
            if iem:
                _last_iem[0] = time.time()
            LOG.append((now(), source, url, "network error: " + type(e).__name__, 0))
            if attempt == 5:
                raise
            time.sleep(waits[attempt])
            continue
        if iem:
            _last_iem[0] = time.time()
        LOG.append((now(), source, url, r.status_code, len(r.content)))
        if (r.status_code == 429 or r.status_code >= 500) and attempt < 5:
            time.sleep(waits[attempt])
            continue
        return r
    raise RuntimeError("unreachable")


def hav(a, b, c, d):
    p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(x))


def dm(s):
    """The cfg lists degrees and minutes as DD.MM (copied from session88_competitor_probe.py)."""
    v = float(s)
    sg = -1 if v < 0 else 1
    v = abs(v)
    d = int(v)
    return sg * (d + round((v - d) * 100, 4) / 60)


def hr(title):
    print("\n" + "=" * 78 + "\n" + title + "\n" + "=" * 78)


# ---------------------------------------------------------------------------
# Step 3.1: identity and position from IEM
# ---------------------------------------------------------------------------

def iem_lookup(icao):
    """IEM station rows for an ICAO code. US airports are tried by the ICAO code
    and by its three-letter form. Only *_ASOS networks count as matches."""
    cands = [icao] + ([icao[1:]] if icao.startswith("K") and len(icao) == 4 else [])
    rows, other, seen = [], 0, set()
    for cid in cands:
        url = IEM_STATION.format(cid)
        r = get(url, "IEM station metadata", iem=True, timeout=60)
        if r.status_code == 404:
            continue
        if r.status_code != 200:
            raise RuntimeError(f"IEM station lookup {url}: HTTP {r.status_code}")
        for row in r.json().get("data", []):
            if not str(row.get("network", "")).endswith("_ASOS"):
                other += 1
                continue
            key = (row["id"], row["network"])
            if key in seen:
                continue
            seen.add(key)
            rows.append({k: row.get(k) for k in ("id", "network", "name", "latitude", "longitude",
                                                 "elevation", "tzname", "archive_begin", "archive_end",
                                                 "online", "country", "state")})
    return rows, other


# ---------------------------------------------------------------------------
# Step 3.2 and 3.3: the grid box, land-sea mask and model terrain
# ---------------------------------------------------------------------------

def box_from_gid(gid, lat, lon):
    """The four surrounding points and bilinear weights, as SPEC 8.8 G6
    (copied from bilinear_from_gid in session76_grib_pull.py, with the weights
    returned instead of the value). Order: (lat0,lon0), (lat0,lon1),
    (lat1,lon0), (lat1,lon1). Longitudes shifted by +360 where negative."""
    nb = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    missing = ec.codes_get_double(gid, "missingValue")
    bitmap = ec.codes_get_long(gid, "bitmapPresent")
    for n in nb:
        if not math.isfinite(n.value) or (bitmap and n.value == missing):
            raise ValueError("missing or non-finite grid value")
    lats = sorted(set(round(n.lat, 6) for n in nb))
    lons = sorted(set(round(n.lon, 6) for n in nb))
    if len(lats) != 2 or len(lons) != 2:
        raise ValueError(f"neighbours do not form a 2 x 2 box: {[(n.lat, n.lon) for n in nb]}")
    lat0, lat1 = lats
    lon0, lon1 = lons
    if abs((lat1 - lat0) - 0.25) > 1e-6 or abs((lon1 - lon0) - 0.25) > 1e-6:
        raise ValueError(f"box is not 0.25 degrees: {lats} {lons}")
    lon_q = lon + 360.0 if lon < 0 else lon
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    val = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in nb}
    pts = [(lat0, lon0), (lat0, lon1), (lat1, lon0), (lat1, lon1)]
    w = [(1 - dlat) * (1 - dlon), (1 - dlat) * dlon, dlat * (1 - dlon), dlat * dlon]
    return {"points": pts, "weights": w, "values": [val[p] for p in pts]}


def read_two_messages(tmp):
    """Read LAND:surface and HGT:surface from the one spent-year file, by byte range."""
    run_date, cycle = GFS_RUN
    base = f"{GFS_BUCKET}/gfs.{run_date:%Y%m%d}/{cycle:02d}/atmos/gfs.t{cycle:02d}z.pgrb2.0p25."
    out = {"fhour": None, "msgs": {}}
    for fh in (0, 1):
        idx_url = f"{base}f{fh:03d}.idx"
        r = get(idx_url, "GFS GRIB idx", timeout=120)
        if r.status_code != 200:
            raise RuntimeError(f"idx {idx_url}: HTTP {r.status_code}")
        rows = []
        for line in r.text.strip().splitlines():
            p = line.split(":")
            rows.append({"offset": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5]})
        need = {"LAND": "surface", "HGT": "surface"}
        found = {}
        for var, level in need.items():
            hits = [i for i, x in enumerate(rows) if x["var"] == var and x["level"] == level]
            if len(hits) == 1:
                found[var] = hits[0]
        if len(found) < 2:
            print(f"  f{fh:03d}: LAND:surface and HGT:surface not both present once "
                  f"(found {sorted(found)}); idx lines {len(rows)}")
            continue
        out["fhour"] = fh
        out["idx_url"] = idx_url
        out["file_url"] = f"{base}f{fh:03d}"
        for var, i in found.items():
            x = rows[i]
            if x["d"] != f"d={run_date:%Y%m%d}{cycle:02d}":
                raise RuntimeError(f"idx run stamp {x['d']} does not match the run")
            start = x["offset"]
            end = rows[i + 1]["offset"] - 1
            rng = f"{start}-{end}"
            rr = get(out["file_url"], "GFS GRIB message", headers={"Range": f"bytes={rng}"}, timeout=120)
            if rr.status_code != 206:
                raise RuntimeError(f"range {rng}: HTTP {rr.status_code}")
            data = rr.content
            if len(data) != end - start + 1 or data[:4] != b"GRIB" or data[-4:] != b"7777":
                raise RuntimeError(f"{var}: message is not well formed")
            (Path(tmp) / f"{var}.grib2").write_bytes(data)
            out["msgs"][var] = {"range": rng, "bytes": len(data), "idx_line": f"{x['var']}:{x['level']}:{x['step']}",
                                "sha256": sha256(data)}
        return out, {v: (Path(tmp) / f"{v}.grib2").read_bytes() for v in found}
    raise RuntimeError("LAND:surface and HGT:surface were in neither f000 nor f001")


def decode_two(msgs, positions):
    """Check identity and validity of the two messages, then interpolate at each position.
    positions: {key: (lat, lon)}. Returns {key: {...}} and the message facts."""
    run_date, cycle = GFS_RUN
    gids, facts = {}, {}
    expect = {"LAND": (2, 0, 0, 1), "HGT": (0, 3, 5, 1)}     # discipline, category, number, surface type
    try:
        for var, data in msgs.items():
            gid = ec.codes_new_from_message(data)
            gids[var] = gid
            got = (ec.codes_get_long(gid, "discipline"), ec.codes_get_long(gid, "parameterCategory"),
                   ec.codes_get_long(gid, "parameterNumber"), ec.codes_get_long(gid, "typeOfFirstFixedSurface"))
            vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
            facts[var] = {"identity": got, "level": ec.codes_get_long(gid, "level"),
                          "stepType": ec.codes_get_string(gid, "stepType"),
                          "units": ec.codes_get_string(gid, "units"),
                          "shortName": ec.codes_get_string(gid, "shortName"),
                          "dataDate": ec.codes_get_long(gid, "dataDate"), "dataTime": ec.codes_get_long(gid, "dataTime"),
                          "validityDate": vd, "validityTime": vt,
                          "Ni": ec.codes_get_long(gid, "Ni"), "Nj": ec.codes_get_long(gid, "Nj")}
            if got != expect[var]:
                raise ValueError(f"{var}: identity {got} != expected {expect[var]}")
            if facts[var]["dataDate"] != int(f"{run_date:%Y%m%d}") or facts[var]["dataTime"] != cycle * 100:
                raise ValueError(f"{var}: run date or time mismatch")
            # f000 or f001: validity must be the run time plus the forecast hour (SPEC 8.7 item 3)
            if vd != int(f"{run_date:%Y%m%d}") or vt not in (cycle * 100, cycle * 100 + 100):
                raise ValueError(f"{var}: validity {vd} {vt:04d} unexpected")
        res = {}
        for key, (lat, lon) in positions.items():
            bl = box_from_gid(gids["LAND"], lat, lon)
            bh = box_from_gid(gids["HGT"], lat, lon)
            if bl["points"] != bh["points"]:
                raise ValueError(f"{key}: the two messages gave different boxes")
            res[key] = {"points": bl["points"], "weights": bl["weights"], "mask": bl["values"],
                        "hgt": bh["values"]}
        return res, facts
    finally:
        for g in gids.values():
            ec.codes_release(g)


# ---------------------------------------------------------------------------
# Step 3.4: hourly observations (download, save, count)
# ---------------------------------------------------------------------------

def piece_name(station, a, b):
    return f"iem_asos_{station}_{a}_{b}_routine.csv"


def piece_url(station, a, b):
    d0 = dt.date.fromisoformat(a)
    d1 = dt.date.fromisoformat(b) + dt.timedelta(days=1)      # IEM treats its end date as exclusive
    return (f"{IEM_ASOS}?station={station}&data=tmpc&data=dwpc&year1={d0.year}&month1={d0.month}&day1={d0.day}"
            f"&year2={d1.year}&month2={d1.month}&day2={d1.day}&tz=UTC&format=onlycomma&latlon=yes&elev=yes"
            f"&missing=M&trace=T&direct=no&report_type=3")


def meta_text(fname, icao, station, a, b, url, pulled, status, rows, dropped, digest, nbytes):
    return (
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
        f"file        : {fname}\n"
        f"purpose     : session 90, Step 3.4 - hourly routine reports for {icao} (IEM id {station}),\n"
        "              saved for the stage C airport check (DECISIONS D82). Counted only; no value is\n"
        "              printed or summarised.\n"
        f"pulled at   : {pulled}\n"
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download service\n"
        "tool        : python requests (scripts/session90_airport_check.py)\n\n"
        "exact URL requested:\n"
        f"{url}\n\n"
        "parameters:\n"
        f"  station     = {station}\n"
        "  data        = tmpc, dwpc  (tmpc = air temperature degC, dwpc = dew point degC)\n"
        f"  date range  = {a} to {b} inclusive. IEM treats its end date as exclusive, so the\n"
        "                request asks for the day after.\n"
        "  tz          = UTC\n"
        "  format      = onlycomma\n"
        "  latlon      = yes\n"
        "  elev        = yes\n"
        "  missing     = M\n"
        "  trace       = T\n"
        "  report_type = 3   (routine METAR only)\n\n"
        f"HTTP status : {status}\n"
        f"bytes       : {nbytes}\n"
        f"data rows   : {rows} (header excluded)\n"
        f"sha256      : {digest}\n"
        f"rows dropped for being later than 2026-07-31 23:59 UTC: {dropped}\n\n"
        "notes:\n"
        "- Same request as the committed IEM files (for example the DSM files), with a different\n"
        "  station.\n"
        "- Rows marked M are left exactly as they arrived. Nothing was filled in (SPEC 2.2).\n"
        "- The first hour of a request window has no report inside that window, so the very first\n"
        "  hour of 2021-03-24 may be missing. Nothing is filled to cover it.\n"
    )


def download_station(icao, station):
    """Save the six yearly pieces for one station. Returns (requests made, bytes, rows dropped, skipped)."""
    nreq = nbytes = dropped_total = skipped = 0
    for a, b in PIECES:
        fname = piece_name(station, a, b)
        fpath = RAW / fname
        mpath = RAW / (fname + ".meta.txt")
        url = piece_url(station, a, b)
        if fpath.exists() or mpath.exists():
            # Only files this script wrote on an earlier run are accepted, and only if they check out.
            if not (fpath.exists() and mpath.exists()):
                raise RuntimeError(f"{fname}: only one of the data file and its meta file exists")
            m = re.search(r"sha256\s+: (\w+)", mpath.read_text())
            if not m or m.group(1) != sha256(fpath.read_bytes()) or "session 90" not in mpath.read_text():
                raise RuntimeError(f"{fname} exists and is not a session 90 file that checks out; not touched")
            skipped += 1
            continue
        pulled = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        r = get(url, "IEM ASOS download", iem=True, timeout=600)
        nreq += 1
        if r.status_code != 200:
            raise RuntimeError(f"{fname}: HTTP {r.status_code}")
        nbytes += len(r.content)
        text = r.content.decode("utf-8", errors="replace")
        lines = text.splitlines()
        if not lines or lines[0].strip() != HEADER:
            raise RuntimeError(f"{fname}: unexpected first line {lines[:1]!r}")
        kept, dropped = [lines[0]], 0
        for ln in lines[1:]:
            if not ln.strip():
                continue
            valid = dt.datetime.strptime(ln.split(",")[1], "%Y-%m-%d %H:%M")
            if valid > LIMIT:
                dropped += 1
                continue
            kept.append(ln)
        data = r.content if dropped == 0 else ("\n".join(kept) + "\n").encode("utf-8")
        with open(fpath, "xb") as f:
            f.write(data)
        with open(mpath, "x", encoding="utf-8") as f:
            f.write(meta_text(fname, icao, station, a, b, url, pulled, r.status_code, len(kept) - 1, dropped,
                              sha256(data), len(data)))
        dropped_total += dropped
    return nreq, nbytes, dropped_total, skipped


def usable(tmpc):
    """True if tmpc is a finite number. A value is parsed and discarded, never kept."""
    if tmpc in ("M", "", "T", None):
        return False, False
    try:
        v = float(tmpc)
    except ValueError:
        return False, False
    if not math.isfinite(v):
        return False, True          # (usable, non-finite)
    return True, False


def load_reports(station):
    """Read the six saved pieces. Returns a list of (valid datetime, usable) and counts. No value is kept."""
    reps, nonfinite = [], 0
    for a, b in PIECES:
        p = RAW / piece_name(station, a, b)
        if not p.exists():
            raise RuntimeError(f"missing file {p.name}")
        with open(p, newline="", encoding="utf-8") as f:
            rd = csv.reader(f)
            head = next(rd)
            if ",".join(head) != HEADER:
                raise RuntimeError(f"{p.name}: header {head}")
            for row in rd:
                if not row:
                    continue
                valid = dt.datetime.strptime(row[1], "%Y-%m-%d %H:%M")
                if valid > LIMIT:
                    raise RuntimeError(f"{p.name}: a row later than the limit is on disk")
                ok, nf = usable(row[5])
                nonfinite += int(nf)
                reps.append((valid, ok))
    return reps, nonfinite


def hour_of(valid):
    """SPEC 8.8 G2 and G3: each report goes to its nearest whole hour (:30 goes up); it is
    dropped if it is more than 15 minutes from that hour (15 exactly is kept)."""
    m = valid.minute
    if m >= 30:
        return valid.replace(minute=0) + dt.timedelta(hours=1) if 60 - m <= 15 else None
    return valid.replace(minute=0) if m <= 15 else None


def utc_day_counts(reps):
    """Days (UTC) with a usable report within 15 minutes of each whole hour."""
    hours = set()
    for valid, ok in reps:
        if ok:
            h = hour_of(valid)
            if h is not None:
                hours.add(h)
    d0, d1 = dt.date(2021, 3, 24), dt.date(2026, 7, 31)
    ndays = (d1 - d0).days + 1
    per_hour = [0] * 24
    all24 = 0
    for i in range(ndays):
        d = d0 + dt.timedelta(days=i)
        n = 0
        for h in range(24):
            if dt.datetime(d.year, d.month, d.day, h) in hours:
                per_hour[h] += 1
                n += 1
        all24 += int(n == 24)
    return hours, per_hour, all24, ndays


def local_day_counts(hours, tzname):
    """D82.8 and D82.7(b). Local calendar days in the airport's own time zone. A day counts only
    if it starts on or after 2021-03-24T00:00 UTC and ends (its last minute, 23:59 local) on or
    before 2026-07-31T23:59 UTC. A day is usable if usable hours >= its hours minus 2."""
    tz = ZoneInfo(tzname)
    utc = dt.timezone.utc
    res = {"all": [0, 0], "held": [0, 0]}      # [local days, usable local days]
    d = dt.date(2021, 3, 21)
    while d <= dt.date(2026, 8, 3):
        d2 = d + dt.timedelta(days=1)
        s_local = dt.datetime(d.year, d.month, d.day, tzinfo=tz)
        e_local = dt.datetime(d2.year, d2.month, d2.day, tzinfo=tz)
        s = s_local.astimezone(utc).replace(tzinfo=None)
        e = e_local.astimezone(utc).replace(tzinfo=None)
        # the local midnight must exist, or the arithmetic above is wrong
        if s_local.astimezone(utc).astimezone(tz).replace(tzinfo=None) != dt.datetime(d.year, d.month, d.day):
            raise RuntimeError(f"{tzname}: local midnight of {d} does not exist")
        nh = (e - s) / dt.timedelta(hours=1)
        if nh not in (23.0, 24.0, 25.0):
            raise RuntimeError(f"{tzname}: local day {d} has {nh} hours")
        nh = int(nh)
        last_minute = e - dt.timedelta(minutes=1)
        if s >= FIRST_UTC and last_minute <= LIMIT:
            # Whole UTC hours inside the local day. Where the zone is not a whole number of hours from
            # UTC (for example India, +5:30) the first whole hour is after local midnight; the day still
            # holds nh whole hours.
            first = s if s.minute == 0 else s.replace(minute=0) + dt.timedelta(hours=1)
            slots = []
            h = first
            while h < e:
                slots.append(h)
                h += dt.timedelta(hours=1)
            if len(slots) != nh:
                raise RuntimeError(f"{tzname}: local day {d} has {len(slots)} whole hours, expected {nh}")
            have = sum(1 for h in slots if h in hours)
            ok = int(have >= nh - 2)
            res["all"][0] += 1
            res["all"][1] += ok
            if d >= HELD_OUT_START:
                res["held"][0] += 1
                res["held"][1] += ok
        d = d2
    return res


def obs_counts(station, tzname):
    reps, nonfinite = load_reports(station)
    reps.sort(key=lambda x: x[0])
    mins = {}
    for v, _ in reps:
        mins[v.minute] = mins.get(v.minute, 0) + 1
    usual = max(mins, key=mins.get)
    hours, per_hour, all24, ndays = utc_day_counts(reps)
    out = {"rows": len(reps), "first": reps[0][0].strftime("%Y-%m-%d %H:%M") if reps else None,
           "last": reps[-1][0].strftime("%Y-%m-%d %H:%M") if reps else None,
           "no_usable_temp": sum(1 for _, ok in reps if not ok), "non_finite": nonfinite,
           "usual_minute": usual if reps else None,
           "share_not_usual_minute": (1 - mins[usual] / len(reps)) if reps else None,
           "per_hour_days": per_hour, "days_all24": all24, "utc_days": ndays}
    if tzname and reps:
        out["local"] = local_day_counts(hours, tzname)
    return out


# ---------------------------------------------------------------------------
# Step 3.5: MOSMIX stations
# ---------------------------------------------------------------------------

def parse_cfg(tmp):
    r = get(CFG, "DWD MOSMIX station catalogue", timeout=120)
    if r.status_code != 200 or len(r.content) < 100000:
        raise RuntimeError(f"station catalogue: HTTP {r.status_code}, {len(r.content)} bytes")
    p = Path(tmp) / "mosmix_stationskatalog.cfg"
    p.write_bytes(r.content)
    rows = []
    for ln in p.read_bytes().decode("latin-1").splitlines()[2:]:
        m = re.match(r"^\s*(\S+)\s+(\S+)\s+(.*?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+)\s*$", ln)
        if m:
            rows.append({"id": m.group(1), "icao": m.group(2), "name": m.group(3),
                         "lat": dm(m.group(4)), "lon": dm(m.group(5)), "elev": int(m.group(6))})
    return rows, len(r.content)


# From NBM's documentation page "NBM v5.0 Data Availability" (https://vlab.noaa.gov/web/mdl/nbm-data-availability-v5.0,
# read 2026-10-03): the domains are CONUS, Alaska, Hawaii, Puerto Rico, Guam, Oceanic and Global Upper Air. The page
# gives no extents in its text. An airport in the contiguous United States is tagged CONUS by its location. Toronto
# and Mexico City could lie inside the rectangular CONUS grid, and the text does not say, so they are unknown. The
# Global Upper Air domain has no 2 m temperature (F123.3). Every other airport is outside all named domains.
NBM_CONUS = set("KATL KAUS KORD KDAL KBKF KHOU KLAX KMIA KLGA KSFO KSEA".split())
NBM_UNKNOWN = {"CYYZ", "MMMX"}


def nbm_domain(icao):
    if icao in NBM_CONUS:
        return "CONUS"
    if icao in NBM_UNKNOWN:
        return "unknown"
    return "none"


# ---------------------------------------------------------------------------
# collect
# ---------------------------------------------------------------------------

def collect(state_path):
    if Path(state_path).exists():
        raise SystemExit(f"{state_path} exists; remove it to collect again")
    tmp = tempfile.mkdtemp(prefix="s90_")
    print(f"temporary directory: {tmp}")
    print(f"python {sys.version.split()[0]}, eccodes {ec.__version__}, requests {requests.__version__}")
    st = {"started": now(), "airports": {}}
    try:
        hr("3.1 Identity and position (IEM station metadata)")
        print("source: " + IEM_STATION.format("<id>") + " (IEM's own station metadata; the id is the ICAO code, and for")
        print("US airports its three-letter form too). Only *_ASOS networks count as matches.\n")
        for icao, region in AIRPORTS:
            rows, other = iem_lookup(icao)
            a = {"icao": icao, "region": region, "stratum": STRATUM_OF[region], "iem_rows": rows,
                 "other_network_rows": other}
            if len(rows) == 1:
                a["match"] = "one"
                a.update({k: rows[0][k] for k in ("id", "network", "name", "latitude", "longitude",
                                                  "elevation", "tzname")})
            elif len(rows) == 0:
                a["match"] = "missing"
            else:
                a["match"] = "ambiguous"
            st["airports"][icao] = a
            if a["match"] == "one":
                r0 = rows[0]
                print(f"{icao:5s} {region:13s} id {r0['id']:5s} {r0['network']:11s} {r0['name'][:28]:28s} "
                      f"lat {r0['latitude']:.4f} lon {r0['longitude']:.4f} elev {r0['elevation']} m  "
                      f"{r0['tzname']}  archive {r0['archive_begin']}..{r0['archive_end']} online {r0['online']}"
                      f"  (other-network rows ignored: {other})")
            else:
                print(f"{icao:5s} {region:13s} {a['match'].upper()}: {[(x['id'], x['network'], x['name']) for x in rows]}"
                      f" (other-network rows ignored: {other})")
        miss = [c for c, a in st["airports"].items() if a["match"] == "missing"]
        amb = [c for c, a in st["airports"].items() if a["match"] == "ambiguous"]
        print(f"\nmissing from IEM: {miss or 'none'}; ambiguous: {amb or 'none'}")

        print("\nEGLC and KSFO against SPEC 3.4:")
        for icao, (lat, lon, el) in SPEC34.items():
            a = st["airports"][icao]
            if a["match"] != "one":
                print(f"  {icao}: no single IEM match")
                continue
            same = (round(a["latitude"], 4) == lat and round(a["longitude"], 4) == lon and round(a["elevation"]) == el)
            print(f"  {icao}: IEM lat {a['latitude']} lon {a['longitude']} elev {a['elevation']} m; "
                  f"SPEC 3.4 lat {lat} lon {lon} elev {el} m; same at SPEC 3.4's precision: {same}; "
                  f"offset {hav(lat, lon, a['latitude'], a['longitude']) * 1000:.1f} m")
        lfpb = st["airports"]["LFPB"]
        if lfpb["match"] == "one":
            d = hav(lfpb["latitude"], lfpb["longitude"], *LFPG_POS)
            st["lfpb_to_lfpg_km"] = d
            print(f"\nLFPB to LFPG (SPEC 3.4 position {LFPG_POS}): {d:.2f} km")
        for c, a in st["airports"].items():
            if a["match"] == "one":
                try:
                    ZoneInfo(a["tzname"])
                except Exception as e:                      # noqa: BLE001
                    print(f"  time zone {a['tzname']} of {c} cannot be loaded: {e!r}")
                    raise

        hr("3.2 and 3.3 GFS grid box, land-sea mask and model terrain (two messages, one spent-year file)")
        info, msgs = read_two_messages(tmp)
        print(f"file: {info['file_url']} (run {GFS_RUN[0]} {GFS_RUN[1]:02d}z, f{info['fhour']:03d})")
        print(f"idx: {info['idx_url']}")
        for v, m in info["msgs"].items():
            print(f"  {v}: idx line {m['idx_line']}, byte range {m['range']}, {m['bytes']} bytes, sha256 {m['sha256']}")
        positions = {c: (a["latitude"], a["longitude"]) for c, a in st["airports"].items() if a["match"] == "one"}
        positions["KSFO@grid"] = KSFO_GRID
        res, facts = decode_two(msgs, positions)
        for v, f in facts.items():
            print(f"  {v} message: {f}")
        st["gfs"] = {"info": info, "facts": {k: {kk: (list(vv) if isinstance(vv, tuple) else vv)
                                                 for kk, vv in f.items()} for k, f in facts.items()}}
        for c, r_ in res.items():
            if c == "KSFO@grid":
                continue
            a = st["airports"][c]
            w = r_["weights"]
            land = sum(wi * mi for wi, mi in zip(w, r_["mask"]))
            height = sum(wi * hi for wi, hi in zip(w, r_["hgt"]))
            a["grid"] = {"points": [list(p) for p in r_["points"]], "weights": w, "mask": r_["mask"],
                         "hgt": r_["hgt"], "land_fraction": land, "model_height": height,
                         "height_diff": height - a["elevation"], "sea_flag": land < 1.0 - 1e-9}
            pts = " ".join(f"({p[0]:.2f},{p[1]:.2f}) w{wi:.4f} m{mi:.0f}"
                           for p, wi, mi in zip(r_["points"], w, r_["mask"]))
            print(f"{c:5s} {pts}  land {land:.4f}  model height {height:.2f} m  station {a['elevation']} m  "
                  f"diff {height - a['elevation']:+.2f} m  {'SEA IN THE GRID BOX' if land < 1.0 - 1e-9 else ''}")
        k = res["KSFO@grid"]
        kl = sum(wi * mi for wi, mi in zip(k["weights"], k["mask"]))
        kh = sum(wi * hi for wi, hi in zip(k["weights"], k["hgt"]))
        st["ksfo_grid_check"] = {"sea_weight": 1 - kl, "model_height": kh}
        print(f"\ncode check at KSFO's SPEC 3.4 grid point {KSFO_GRID}: sea weight {1 - kl:.4f} "
              f"(F117.3: 0.375), model height {kh:.2f} m (SPEC 3.4 notes: 94.47 m)")

        hr("3.4 Hourly observations: download the 45 new airports, then counts only")
        nreq = nbytes = ndrop = nskip = 0
        for icao, a in st["airports"].items():
            if icao in COMMITTED:
                continue
            if a["match"] != "one":
                print(f"{icao}: no single IEM match, not downloaded")
                continue
            q, b, d, s = download_station(icao, a["id"])
            nreq, nbytes, ndrop, nskip = nreq + q, nbytes + b, ndrop + d, nskip + s
            print(f"{icao:5s} id {a['id']:5s} requests {q}, bytes {b}, rows dropped for the limit {d}, "
                  f"pieces already saved {s}")
        st["download"] = {"requests": nreq, "bytes": nbytes, "dropped": ndrop, "skipped_pieces": nskip}
        print(f"\ndownload totals this run: {nreq} requests, {nbytes} bytes, rows dropped for the 2026-07-31 limit: {ndrop},"
              f" pieces already saved by an earlier run: {nskip}")

        print("\nCounting-code check against F131.6 (days with all 24 UTC hours covered, committed files):")
        for name, (sid, expect) in CODE_CHECK.items():
            reps, _ = load_reports(sid)
            _, _, all24, _ = utc_day_counts(reps)
            print(f"  {name:5s} counted {all24}, F131.6 {expect}: {'equal' if all24 == expect else 'DIFFERENT'}")

        print("\nCounts per airport (no value of any report is printed):")
        for icao, a in st["airports"].items():
            sid = COMMITTED.get(icao, a.get("id"))
            if a["match"] != "one":
                continue
            c = obs_counts(sid, a["tzname"])
            a["obs"] = c
            loc = c.get("local")
            print(f"{icao:5s} rows {c['rows']}, first {c['first']}, last {c['last']}, no usable temperature "
                  f"{c['no_usable_temp']}, non-finite {c['non_finite']}")
            print(f"      usual minute :{c['usual_minute']:02d}, share not at it {100 * c['share_not_usual_minute']:.2f}%;"
                  f" UTC days with all 24 hours {c['days_all24']} of {c['utc_days']}")
            print(f"      days per whole hour 00..23: {c['per_hour_days']}")
            if loc:
                for k, label in (("all", "2021-03-24..2026-07-31"), ("held", "2024-08-01..2026-07-31")):
                    n, u = loc[k]
                    print(f"      daily maximum usable local days {label}: {u} of {n} ({100 * u / n:.2f}%)" if n else
                          f"      daily maximum usable local days {label}: none")

        hr("3.5 MOSMIX stations (DWD catalogue) and NBM domain")
        cfg, nb = parse_cfg(tmp)
        st["cfg"] = {"url": CFG, "bytes": nb, "rows": len(cfg), "accessed": now()}
        print(f"catalogue {CFG}\n  accessed {st['cfg']['accessed']}, {nb} bytes, {len(cfg)} stations parsed")
        print("  The cfg gives latitude and longitude as degrees.minutes (DWD procedure documentation FAQ 9.1);")
        print("  converted here. A longitude sign is flagged when the station of the same ICAO code would be at least")
        print("  2 km nearer the airport with its longitude sign flipped.")
        for icao, a in st["airports"].items():
            if a["match"] != "one":
                continue
            lat, lon = a["latitude"], a["longitude"]
            near = min(cfg, key=lambda r: hav(lat, lon, r["lat"], r["lon"]))
            d = hav(lat, lon, near["lat"], near["lon"])
            same = [r for r in cfg if r["icao"] == icao]
            sm = []
            for r in same:
                d1 = hav(lat, lon, r["lat"], r["lon"])
                d2 = hav(lat, lon, r["lat"], -r["lon"])
                sm.append({"id": r["id"], "name": r["name"], "dist_km": d1, "flipped_dist_km": d2,
                           "sign_flag": (d1 - d2) >= 2.0})
            a["mosmix"] = {"nearest_id": near["id"], "nearest_name": near["name"], "nearest_icao": near["icao"],
                           "dist_km": d, "within_10km": d <= 10.0, "same_icao": sm}
            a["nbm"] = nbm_domain(icao)
            s_txt = "; ".join(f"same ICAO {x['id']} {x['dist_km']:.2f} km, flipped {x['flipped_dist_km']:.2f} km"
                              f"{' SIGN FLAG' if x['sign_flag'] else ''}" for x in sm) or "no catalogue entry with this ICAO code"
            print(f"{icao:5s} nearest {near['id']:6s} {near['icao']:5s} {near['name'][:26]:26s} {d:8.2f} km "
                  f"{'within 10 km' if d <= 10 else 'beyond 10 km':12s} | {s_txt} | NBM {a['nbm']}")
        print("\nNBM domains (documentation only; see the note in the script above nbm_domain): CONUS for the contiguous US,")
        print("unknown for CYYZ and MMMX, none for every other airport.")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\ntemporary directory removed: {not Path(tmp).exists()}")
    st["requests"] = [list(x) for x in LOG]
    with open(state_path, "x") as f:
        json.dump(st, f)
    hr("Request and byte totals by source (this run)")
    by = {}
    for t, src, url, status, n in LOG:
        by.setdefault(src, [0, 0, 0])
        by[src][0] += 1
        by[src][1] += n
        by[src][2] += int(not (status in (200, 206) or status == 404))
    for src, (n, b, bad) in by.items():
        print(f"  {src:34s} requests {n:5d}  bytes {b:12d}  not 200/206 (404 for station lookups is expected): {bad}")
    print(f"  total requests {sum(v[0] for v in by.values())}, bytes {sum(v[1] for v in by.values())}")
    print(f"state saved to {state_path}")


# ---------------------------------------------------------------------------
# decide
# ---------------------------------------------------------------------------

def decide(state_path):
    if OUT_CSV.exists() or Path(str(OUT_CSV) + ".meta.txt").exists():
        raise SystemExit("data/processed/session90_airports.csv or its meta file already exists; stop")
    st = json.load(open(state_path))
    A = st["airports"]
    hr("Step 4.1 Eligibility (D82.7(a) and (b), applied mechanically)")
    verdict = {}
    for icao, region in AIRPORTS:
        a = A[icao]
        reason = None
        if icao in SPENT:
            reason = SPENT[icao]
        elif icao in EXCLUDED:
            reason = EXCLUDED[icao]
        elif a["match"] == "missing":
            reason = "no IEM archive (no matching station in IEM)"
        elif a["match"] == "ambiguous":
            reason = "ambiguous IEM match, not resolved (no observations saved)"
        elif not a.get("obs") or a["obs"]["rows"] == 0:
            reason = "no IEM archive (no routine reports returned)"
        else:
            (n1, u1), (n2, u2) = a["obs"]["local"]["all"], a["obs"]["local"]["held"]
            if n1 == 0 or n2 == 0:
                reason = "no local days in a window"
            elif u1 * 10 < n1 * 9 or u2 * 10 < n2 * 9:
                bad = []
                if u1 * 10 < n1 * 9:
                    bad.append(f"all window {100 * u1 / n1:.2f}%")
                if u2 * 10 < n2 * 9:
                    bad.append(f"held-out window {100 * u2 / n2:.2f}%")
                reason = "daily maximum usable on under 90% of local days: " + ", ".join(bad)
        verdict[icao] = reason
        loc = a.get("obs", {}).get("local") if a.get("obs") else None
        pct = (f"{100 * loc['all'][1] / loc['all'][0]:6.2f}% of {loc['all'][0]}  held-out "
               f"{100 * loc['held'][1] / loc['held'][0]:6.2f}% of {loc['held'][0]}") if loc and loc["all"][0] else "no counts"
        print(f"{icao:5s} {A[icao]['stratum']:13s} all {pct}  -> {'eligible' if reason is None else 'NOT eligible: ' + reason}")

    hr("Step 4.2 The draw (D82.7(d)), run once")
    print(f"python {sys.version.split()[0]}, random.Random({SEED})")
    rng = random.Random(SEED)
    drawn, shortfall = [], 0
    for stratum, size in STRATA:
        elig = sorted(c for c, _ in AIRPORTS if STRATUM_OF[REGION_OF[c]] == stratum and verdict[c] is None)
        print(f"\nstratum {stratum} (size {size}): {len(elig)} eligible, sorted: {elig}")
        if len(elig) >= size:
            pick = rng.sample(elig, size)
            print(f"  sample({len(elig)} eligible, {size}) returned {pick}")
        else:
            pick = list(elig)
            shortfall += size - len(elig)
            print(f"  fewer eligible than {size}: take all {pick}; shortfall so far {shortfall}")
        drawn += pick
    if shortfall:
        rest = sorted(c for c, _ in AIRPORTS if verdict[c] is None and c not in drawn)
        print(f"\nshortfall {shortfall}; remaining eligible, sorted: {rest}")
        if len(rest) < shortfall:
            raise SystemExit("stop and report: fewer than six eligible airports in total")
        fill = rng.sample(rest, shortfall)
        print(f"  sample({len(rest)}, {shortfall}) returned {fill}")
        drawn += fill
    print(f"\nTHE CLAIM BATCH ({len(drawn)} airports): {drawn}")
    if len(drawn) != 6:
        raise SystemExit("stop and report: the batch does not have six airports")

    hr("Step 5.1 data/processed/session90_airports.csv")
    cols = ["icao", "region", "stratum", "iem_id", "iem_network", "name", "latitude", "longitude", "elevation_m", "time_zone"]
    for i in range(1, 5):
        cols += [f"grid{i}_lat", f"grid{i}_lon", f"grid{i}_weight", f"grid{i}_land_mask"]
    cols += ["land_fraction", "model_height_m", "height_diff_m", "sea_flag", "mosmix_station_id", "mosmix_distance_km",
             "mosmix_within_10km", "mosmix_lon_sign_flag", "nbm_domain", "dailymax_pct_all", "dailymax_days_all",
             "dailymax_pct_heldout", "dailymax_days_heldout", "eligible_or_reason", "drawn"]
    rows = []
    for icao, region in AIRPORTS:
        a = A[icao]
        r = {"icao": icao, "region": region, "stratum": STRATUM_OF[region]}
        if a["match"] == "one":
            r.update({"iem_id": a["id"], "iem_network": a["network"], "name": a["name"], "latitude": a["latitude"],
                      "longitude": a["longitude"], "elevation_m": a["elevation"], "time_zone": a["tzname"]})
            g = a["grid"]
            for i in range(4):
                r[f"grid{i + 1}_lat"], r[f"grid{i + 1}_lon"] = g["points"][i]
                r[f"grid{i + 1}_weight"] = g["weights"][i]
                r[f"grid{i + 1}_land_mask"] = g["mask"][i]
            r.update({"land_fraction": g["land_fraction"], "model_height_m": g["model_height"],
                      "height_diff_m": g["height_diff"], "sea_flag": "sea in the grid box" if g["sea_flag"] else "no"})
            m = a["mosmix"]
            r.update({"mosmix_station_id": m["nearest_id"], "mosmix_distance_km": round(m["dist_km"], 3),
                      "mosmix_within_10km": "yes" if m["within_10km"] else "no",
                      "mosmix_lon_sign_flag": "yes" if any(x["sign_flag"] for x in m["same_icao"]) else "no",
                      "nbm_domain": a["nbm"]})
            loc = a["obs"]["local"] if a.get("obs") and "local" in a["obs"] else None
            if loc:
                r.update({"dailymax_days_all": loc["all"][0], "dailymax_pct_all": round(100 * loc["all"][1] / loc["all"][0], 2),
                          "dailymax_days_heldout": loc["held"][0],
                          "dailymax_pct_heldout": round(100 * loc["held"][1] / loc["held"][0], 2)})
        r["eligible_or_reason"] = "eligible" if verdict[icao] is None else verdict[icao]
        r["drawn"] = "yes" if icao in drawn else "no"
        rows.append(r)
    with open(OUT_CSV, "x", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    data = OUT_CSV.read_bytes()
    digest = sha256(data)
    with open(str(OUT_CSV) + ".meta.txt", "x", encoding="utf-8") as f:
        f.write("Provenance (SPEC 2.3). Do not edit the data file.\n\n"
                "file        : session90_airports.csv\n"
                "purpose     : session 90, Step 5.1 - the 47 airports of DECISIONS D82.6: IEM identity, GFS grid box,\n"
                "              land and sea, MOSMIX station, NBM domain, daily-maximum counts, eligibility and the draw.\n"
                "              No temperature or dew point value is in it.\n"
                f"written at  : {now()}\n"
                "written by  : scripts/session90_airport_check.py --decide\n"
                f"rows        : {len(rows)}\n"
                f"sha256      : {digest}\n\n"
                "sources: IEM station metadata and saved routine hourly reports (data/raw/iem_asos_*); NOAA GFS file\n"
                f"{st['gfs']['info']['file_url']} (LAND:surface and HGT:surface only); DWD MOSMIX station catalogue\n"
                f"{CFG} (accessed {st['cfg']['accessed']}); NBM documentation (domain names only).\n"
                "The draw is DECISIONS D82.7(d) with random.Random(20261003).\n")
    print(f"wrote {OUT_CSV.relative_to(ROOT)}: {len(rows)} rows, sha256 {digest}")
    st["drawn"] = drawn
    st["verdict"] = verdict
    return drawn


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--collect", action="store_true")
    ap.add_argument("--decide", action="store_true")
    ap.add_argument("--state", required=True, help="state file outside the repo")
    args = ap.parse_args()
    if args.collect == args.decide:
        raise SystemExit("choose exactly one of --collect and --decide")
    if args.collect:
        collect(args.state)
    else:
        decide(args.state)


if __name__ == "__main__":
    main()
