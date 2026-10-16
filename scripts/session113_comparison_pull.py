#!/usr/bin/env python3
"""Session 113: the probe and pull of comparison forecasts and the official
daily maximum on spent years (DECISIONS D107).

Modes (docs/sessions/session-113.md):

  --check          Step 2. No network. The airport table, the weights
                   functions on the GFS grid and on made-up regular and
                   Lambert grids, the date guards, degrees F to C, and the
                   cycle lists.
  --probe          Step 3. Metadata and counts only, on spent dates: archive
                   listings (coverage, steps, write times), index files,
                   a few decoded messages' metadata, the MOS and climate
                   archives. Writes data/processed/session113/probe.csv.
  --cost           Step 4. Throughput on at least 50 spent-date messages per
                   gridded source; the D107.7 gate. Writes cost.csv.
  --pull SOURCE    Steps 5 to 9. SOURCE is ifs, aifs, nbs, nbm, mav or
                   official. Monthly chunks with a done-marker each.
  --latency        Step 10. Archive write times and product times.

Hard limits (D107.2, D107.5):
  - Nothing is scored. No observation file, stage C table or prediction file
    is opened. Nothing from the 37 airports of F153.6 is read: the two
    airport files are filtered to the 12 airports of D103.4 on reading.
  - No value valid after 2026-07-31T23:00 UTC is requested, kept or used,
    and no maximum whose window ends after it. Every planned GRIB request is
    checked before it is sent, and every decoded message again before its
    values are read. MOS runs come whole: projections after the limit are
    dropped in memory, unread, and counted.
  - No forecast or observed value is printed.
  - At most 8 requests at once (D107.7).
  - No GRIB file is kept (D47): messages are fetched by byte range, decoded
    in memory and dropped. Point values only, as gzipped CSVs.

Owner rulings in this session (recorded in F156):
  - At the six development airports the four points and weights are kept
    around both GFS's position (the positions file's lat_used, lon_used,
    SPEC 3.4's grid point) and IEM's position, each labelled ("gfs",
    "iem"). The claim airports use IEM's position only, which is GFS's.
  - Time zones come from D98.10(a) (development) and session90_airports.csv
    (claim), and must agree with src/mlwx/data/gfs_airports.csv. IEM
    positions for LFPG, KDSM, YSDU and KRNO come from SPEC 3.4's first
    table; their height_diff_m is recorded as absent.

Functions taken from the record (read only): bilinear_from_gid
(session76_grib_pull.py) and box_from_gid (session90_airport_check.py) for
the weights check; s3list, ecmwf_index, ecmwf_path and idx_lines
(session82_source_probe.py) for listings and index files. New code is
written only where no function exists (see the checkpoint lines).

No em-dashes in any text here (D76.6).
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import math
import os
import random
import re
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path
from zoneinfo import ZoneInfo

sys.dont_write_bytecode = True

import eccodes as ec  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
OUT = ROOT / "data" / "processed" / "session113"
WORK = OUT / "work"                      # chunk files and done-markers, deleted after each merge
AIRPORTS_90 = ROOT / "data" / "processed" / "session90_airports.csv"
POSITIONS_91 = ROOT / "data" / "processed" / "session91_pull_airports.csv"
GFS_CONFIG = ROOT / "src" / "mlwx" / "data" / "gfs_airports.csv"   # read only, time-zone check
SPEC_FILE = ROOT / "SPEC.md"

# ------------------------------------------------------------------ limits

LIMIT = dt.datetime(2026, 7, 31, 23, 0)           # nothing valid after this (D107.5)
DEV_FIRST = dt.datetime(2023, 8, 1, 0)            # D89.3's test years
CLAIM_FIRST = dt.datetime(2024, 8, 1, 0)          # D100.4's looks
LAST_CYCLE = dt.datetime(2026, 7, 31, 18)
CYCLE_HOURS = (0, 6, 12, 18)
LEAD_MIN, LEAD_MAX = 3, 48
MAX_WORKERS = 8                                   # D107.7
COST_GB, COST_HOURS = 250.0, 24.0                 # D107.7

DEV = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO"]
CLAIM = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]
ALL12 = CLAIM + DEV                               # claim airports lead (D107.9(f))
TZ_D98 = {"EGLC": "Europe/London", "LFPG": "Europe/Paris", "KDSM": "America/Chicago",
          "YSDU": "Australia/Sydney", "KRNO": "America/Los_Angeles",
          "KSFO": "America/Los_Angeles"}          # D98.10(a)
SPEC_CODE = {"LFPG": "LFPG", "KDSM": "DSM", "YSDU": "YSDU", "KRNO": "RNO"}   # SPEC 3.4, first table
US4 = ["KDSM", "KRNO", "KSFO", "KORD"]            # NBM, MAV and the official maximum (D107.5, D107.8)


class GuardError(Exception):
    """A date guard fired. Nothing is requested or read."""


def say(*a):
    print(*a, flush=True)


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


# ------------------------------------------------------------------ guards

def guard_valid(t):
    """A forecast value's valid time (UTC, naive)."""
    if t > LIMIT:
        raise GuardError(f"valid time {t} is after {LIMIT}")
    return t


def guard_window_end(t):
    """A maximum field's window end (UTC, naive)."""
    if t > LIMIT:
        raise GuardError(f"maximum window ends {t}, after {LIMIT}")
    return t


def standard_offset(tzname, day):
    """The zone's standard-time offset on that day (UTC offset minus DST)."""
    z = ZoneInfo(tzname)
    noon = dt.datetime(day.year, day.month, day.day, 12, tzinfo=z)
    return noon.utcoffset() - noon.dst()


def climate_day_window(day, tzname):
    """The climate day: midnight to midnight local standard time (D107.8),
    as a UTC window (naive). Recorded, not adjusted."""
    off = standard_offset(tzname, day)
    s = dt.datetime(day.year, day.month, day.day) - off
    return s, s + dt.timedelta(days=1)


def guard_climate_day(day, tzname):
    s, e = climate_day_window(day, tzname)
    if e > LIMIT:
        raise GuardError(f"climate day {day} ({tzname}) ends {e} UTC, after {LIMIT}")
    return s, e


def f_to_c(f):
    """Degrees F (whole, as issued) to degrees C, exact formula, no rounding."""
    return (float(f) - 32.0) * 5.0 / 9.0


# ------------------------------------------------------------------ airports

def read_spec_iem_positions():
    """IEM's latitude and longitude from SPEC 3.4's first table, by station code."""
    text = SPEC_FILE.read_text(encoding="utf-8")
    i = text.index("**3.4 The airport table.**")
    j = text.index("| station code | airport | stage |", i)
    out = {}
    for line in text[j:].splitlines()[2:]:
        if not line.startswith("|"):
            break
        c = [x.strip() for x in line.strip("|").split("|")]
        out[c[0]] = (float(c[5]), float(c[6]))
    return out


def load_airports():
    """The 12 airports of D103.4. Reads two files under data/ only, filtered
    to the 12 on reading, plus SPEC 3.4 and (check only) the live config."""
    with open(AIRPORTS_90, newline="") as f:
        a90 = {r["icao"]: r for r in csv.DictReader(f) if r["icao"] in ALL12}
    with open(POSITIONS_91, newline="") as f:
        p91 = {r["icao"]: r for r in csv.DictReader(f) if r["icao"] in ALL12}
    with open(GFS_CONFIG, newline="") as f:
        cfg = {r["icao"]: r for r in csv.DictReader(f) if r["icao"] in ALL12}
    spec = read_spec_iem_positions()
    if set(p91) != set(ALL12) or set(cfg) != set(ALL12):
        raise SystemExit("STOP: the positions file or the config lacks one of the 12 airports")
    table = {}
    for icao in ALL12:
        p = p91[icao]
        role = "development" if icao in DEV else "claim"
        if icao in a90:
            r = a90[icao]
            iem = (float(r["latitude"]), float(r["longitude"]))
            iem_src = "session90_airports.csv"
            hd = r["height_diff_m"]
            hd_src = "session90_airports.csv (model terrain at IEM position minus elevation)"
            tz90 = r["time_zone"]
        else:
            iem = spec[SPEC_CODE[icao]]
            iem_src = "SPEC 3.4 first table"
            hd, hd_src, tz90 = "", "absent (not in session90_airports.csv; owner ruling)", None
        tz = TZ_D98[icao] if role == "development" else tz90
        if tz != cfg[icao]["time_zone"]:
            raise SystemExit(f"STOP: {icao} time zone {tz} differs from gfs_airports.csv "
                             f"{cfg[icao]['time_zone']}")
        sets = {"gfs": (float(p["lat_used"]), float(p["lon_used"]))}
        if role == "development":
            sets["iem"] = iem
        else:
            if (float(p["lat_used"]), float(p["lon_used"])) != iem:
                raise SystemExit(f"STOP: {icao} claim airport's lat_used is not IEM's position")
            sets = {"iem": iem}
        table[icao] = dict(
            icao=icao, iem_id=p["iem_id"], role=role, tz=tz, iem_lat=iem[0], iem_lon=iem[1],
            iem_source=iem_src, height_diff_m=hd, height_diff_source=hd_src,
            first_cycle=DEV_FIRST if role == "development" else CLAIM_FIRST,
            last_cycle=LAST_CYCLE, sets=sets, p91=p)
    return table


def cycles(first, last=LAST_CYCLE):
    out, t = [], first
    while t <= last:
        if t.hour in CYCLE_HOURS:
            out.append(t)
        t += dt.timedelta(hours=6)
    return out


def test_year(t):
    y = t.year if t.month >= 8 else t.year - 1
    return f"{y}-{(y + 1) % 100:02d}"


def leads_kept(cyc, steps):
    """The steps of a run within leads 3 to 48 whose valid time is on or
    before the limit. Steps after the limit are never requested."""
    return [s for s in steps if LEAD_MIN <= s <= LEAD_MAX and cyc + dt.timedelta(hours=s) <= LIMIT]


# ------------------------------------------------------------------ weights

def box_regular(gid, lat, lon):
    """The four points around (lat, lon) on a regular latitude-longitude grid
    and their bilinear weights, by the formula of session 76's
    bilinear_from_gid (SPEC 8.8 G6): codes_grib_find_nearest's four points,
    dlat and dlon from the two latitudes and two longitudes. The query
    longitude is moved by whole turns into the box's longitude range (on the
    GFS grid this is lon + 360 for a negative longitude, as in
    bilinear_from_gid; on a -180 to 180 grid it stays as it is). Returned in
    eccodes' order: list of dict(index, lat, lon, weight, distance_km)."""
    nb = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    lats = sorted(set(round(n.lat, 6) for n in nb))
    lons = sorted(set(round(n.lon, 6) for n in nb))
    if len(lats) != 2 or len(lons) != 2:
        raise ValueError(f"neighbours do not form a 2 x 2 box: {[(n.lat, n.lon) for n in nb]}")
    lat0, lat1 = lats
    lon0, lon1 = lons
    lon_q = lon
    while lon_q < lon0:
        lon_q += 360.0
    while lon_q > lon1:
        lon_q -= 360.0
    if not (lat0 <= lat <= lat1 and lon0 <= lon_q <= lon1):
        raise ValueError("the point is not inside its four neighbours")
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    out = []
    for n in nb:
        hi_lat = round(n.lat, 6) == lat1
        hi_lon = round(n.lon, 6) == lon1
        w = (dlat if hi_lat else 1 - dlat) * (dlon if hi_lon else 1 - dlon)
        out.append(dict(index=int(n.index), lat=n.lat, lon=n.lon, weight=w, distance_km=n.distance))
    return out


def lambert_params(gid):
    g = lambda k: ec.codes_get(gid, k)  # noqa: E731
    p = dict(Nx=g("Nx"), Ny=g("Ny"), lat1=g("latitudeOfFirstGridPointInDegrees"),
             lon1=g("longitudeOfFirstGridPointInDegrees"), LaD=g("LaDInDegrees"),
             LoV=g("LoVInDegrees"), latin1=g("Latin1InDegrees"), latin2=g("Latin2InDegrees"),
             Dx=g("DxInMetres"), Dy=g("DyInMetres"), R=float(g("radius")),
             iNeg=g("iScansNegatively"), jPos=g("jScansPositively"),
             jCons=g("jPointsAreConsecutive"), alt=g("alternativeRowScanning"))
    if p["iNeg"] != 0 or p["jPos"] != 1 or p["jCons"] != 0:
        raise ValueError(f"unexpected Lambert scanning mode: {p}")
    return p


def lcc_xy(p, lat, lon):
    """Lambert conformal conic on a sphere (Snyder 1987, eq. 15-1 to 15-4)."""
    r = math.radians
    f1, f2 = r(p["latin1"]), r(p["latin2"])
    if abs(f1 - f2) < 1e-12:
        n = math.sin(f1)
    else:
        n = (math.log(math.cos(f1) / math.cos(f2))
             / math.log(math.tan(math.pi / 4 + f2 / 2) / math.tan(math.pi / 4 + f1 / 2)))
    F = math.cos(f1) * math.tan(math.pi / 4 + f1 / 2) ** n / n
    rho = p["R"] * F / math.tan(math.pi / 4 + r(lat) / 2) ** n
    rho0 = p["R"] * F / math.tan(math.pi / 4 + r(p["LaD"]) / 2) ** n
    dl = ((lon - p["LoV"] + 180.0) % 360.0) - 180.0
    th = n * r(dl)
    return rho * math.sin(th), rho0 - rho * math.cos(th)


def haversine_km(a, b, c, d):
    r = math.radians
    h = (math.sin(r(c - a) / 2) ** 2
         + math.cos(r(a)) * math.cos(r(c)) * math.sin(r(d - b) / 2) ** 2)
    return 2 * 6371.0 * math.asin(math.sqrt(h))


def box_lambert(gid, lat, lon):
    """The four grid points around (lat, lon) on a Lambert conformal grid and
    their bilinear weights. New code (no record function handles a Lambert
    grid): the same formula as bilinear_from_gid, applied on the grid's own
    axes (x, y in metres) instead of latitude and longitude. Each corner's
    position from eccodes is projected back and must sit on its grid node
    within 1 m; otherwise ValueError."""
    p = lambert_params(gid)
    # NBM sets alternativeRowScanning: odd rows are stored right to left.
    # eccodes' latitudes and longitudes do not reverse them, but the decoded
    # values keep the stored order (found by this probe), so the value of node
    # (j, i) on an odd row is at j * Nx + (Nx - 1 - i).
    x0, y0 = lcc_xy(p, p["lat1"], p["lon1"])
    x, y = lcc_xy(p, lat, lon)
    fi, fj = (x - x0) / p["Dx"], (y - y0) / p["Dy"]
    i0, j0 = math.floor(fi), math.floor(fj)
    if not (0 <= i0 < p["Nx"] - 1 and 0 <= j0 < p["Ny"] - 1):
        raise ValueError("outside the grid")
    di, dj = fi - i0, fj - j0
    corners = [(j0, i0, (1 - dj) * (1 - di)), (j0, i0 + 1, (1 - dj) * di),
               (j0 + 1, i0, dj * (1 - di)), (j0 + 1, i0 + 1, dj * di)]
    idx = [j * p["Nx"] + i for j, i, _ in corners]
    lats = ec.codes_get_double_elements(gid, "latitudes", idx)
    lons = ec.codes_get_double_elements(gid, "longitudes", idx)
    out = []
    for (j, i, w), k, la, lo in zip(corners, idx, lats, lons):
        cx, cy = lcc_xy(p, la, lo)
        if abs(cx - (x0 + i * p["Dx"])) > 1.0 or abs(cy - (y0 + j * p["Dy"])) > 1.0:
            raise ValueError(f"corner {k} does not sit on its grid node")
        vk = j * p["Nx"] + (p["Nx"] - 1 - i) if (p["alt"] and j % 2 == 1) else k
        out.append(dict(index=vk, geo_index=k, lat=la, lon=lo, weight=w,
                        distance_km=haversine_km(lat, lon, la, lo)))
    return out


def box_any(gid, lat, lon):
    gt = ec.codes_get(gid, "gridType")
    if gt == "regular_ll":
        return box_regular(gid, lat, lon)
    if gt == "lambert":
        return box_lambert(gid, lat, lon)
    raise ValueError(f"grid type {gt} not handled")


def mark_nearest(box):
    k = min(range(4), key=lambda i: box[i]["distance_km"])
    for i, b in enumerate(box):
        b["nearest"] = int(i == k)
    return box


# ------------------------------------------------------------------ synthetic grids (check only)

def synthetic_regular(ni, nj, la1, lo1, la2, lo2, di, dj):
    g = ec.codes_grib_new_from_samples("GRIB2")
    for k, v in [("Ni", ni), ("Nj", nj), ("latitudeOfFirstGridPointInDegrees", la1),
                 ("longitudeOfFirstGridPointInDegrees", lo1),
                 ("latitudeOfLastGridPointInDegrees", la2),
                 ("longitudeOfLastGridPointInDegrees", lo2),
                 ("iDirectionIncrementInDegrees", di), ("jDirectionIncrementInDegrees", dj)]:
        ec.codes_set(g, k, v)
    ec.codes_set_values(g, np.arange(ni * nj, dtype=float) % 997.0)
    return g


def synthetic_lambert():
    g = ec.codes_grib_new_from_samples("GRIB2")
    ec.codes_set(g, "gridDefinitionTemplateNumber", 30)
    for k, v in [("shapeOfTheEarth", 6), ("Nx", 160), ("Ny", 110),
                 ("latitudeOfFirstGridPointInDegrees", 20.0),
                 ("longitudeOfFirstGridPointInDegrees", 235.0), ("LaDInDegrees", 25.0),
                 ("LoVInDegrees", 265.0), ("Latin1InDegrees", 25.0), ("Latin2InDegrees", 25.0),
                 ("DxInMetres", 40000.0), ("DyInMetres", 40000.0), ("scanningMode", 64)]:
        ec.codes_set(g, k, v)
    ec.codes_set_values(g, np.arange(160 * 110, dtype=float))
    return g


def import_record(name):
    """Import a record script read only, with no bytecode written."""
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    return __import__(name)


# ------------------------------------------------------------------ --check

def run_check():
    res = []

    def rec(name, ok, detail=""):
        res.append((name, ok))
        say(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f": {detail}" if detail else ""))

    say("== --check (no network) ==")
    A = load_airports()
    say(f"  airport table: {len(A)} airports; claim {CLAIM}; development {DEV}")
    for a in A.values():
        say(f"    {a['icao']:5s} {a['role']:11s} tz {a['tz']:20s} IEM {a['iem_lat']}, {a['iem_lon']} "
            f"({a['iem_source']}); height_diff_m {a['height_diff_m'] or 'absent'}; "
            f"sets {list(a['sets'])}; window {iso(a['first_cycle'])} to {iso(a['last_cycle'])}")
    rec("time zones: 12 of 12 agree with src/mlwx/data/gfs_airports.csv", len(A) == 12)

    # (1) the GFS 0.25 degree grid, recorded points and weights
    s76 = import_record("session76_grib_pull")
    s90 = import_record("session90_airport_check")
    p0 = A["KDSM"]["p91"]
    gfs = synthetic_regular(int(p0["grid_Ni"]), int(p0["grid_Nj"]), float(p0["grid_lat_first"]),
                            float(p0["grid_lon_first"]), float(p0["grid_lat_last"]),
                            float(p0["grid_lon_last"]), float(p0["grid_di"]), float(p0["grid_dj"]))
    vals = ec.codes_get_values(gfs)
    n_eq = n_set = n_blend = 0
    for a in A.values():
        p = a["p91"]
        rec_pts = [(int(p[f"p{k}_index"]), float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"]),
                    float(p[f"p{k}_weight"])) for k in range(1, 5)]
        lat, lon = float(p["lat_used"]), float(p["lon_used"])
        box = box_regular(gfs, lat, lon)
        mine = [(b["index"], round(b["lat"], 6), round(b["lon"], 6), b["weight"]) for b in box]
        rp = [(i, round(la, 6), round(lo, 6), w) for i, la, lo, w in rec_pts]
        n_eq += mine == rp
        n_set += sorted(mine) == sorted(rp)
        # the blend in bilinear_from_gid's order equals bilinear_from_gid's value exactly
        srt = sorted(box, key=lambda b: (round(b["lat"], 6), round(b["lon"], 6)))
        blend = sum(b["weight"] * vals[b["index"]] for b in srt)
        bl = s76.bilinear_from_gid(gfs, lat, lon)
        n_blend += blend == bl
    rec("(1) GFS set: positions file's four points and weights reproduced exactly, in order",
        n_eq == 12, f"{n_eq} of 12 (as sets {n_set} of 12)")
    rec("(1) GFS set: blend equals session 76's bilinear_from_gid", n_blend == 12,
        f"{n_blend} of 12, exact")
    # (1, extended by the owner's ruling) the IEM set at the development airports
    n_iem = n_iem90 = n_iem90_n = 0
    for icao in DEV:
        a = A[icao]
        lat, lon = a["sets"]["iem"]
        box = box_regular(gfs, lat, lon)
        ref = s90.box_from_gid(gfs, lat, lon)        # sorted order, 0.25 degree check
        srt = sorted(box, key=lambda b: (round(b["lat"], 6), round(b["lon"], 6)))
        lon_conv = [(round(b["lat"], 6), round(b["lon"], 6)) for b in srt]
        ok = lon_conv == [(round(x, 6), round(y, 6)) for x, y in ref["points"]] and \
            [b["weight"] for b in srt] == ref["weights"]
        n_iem += ok
        r90 = None
        if a["iem_source"] == "session90_airports.csv":
            with open(AIRPORTS_90, newline="") as f:
                r90 = next(r for r in csv.DictReader(f) if r["icao"] == icao)
        if r90:
            n_iem90_n += 1
            rec_pts = sorted((round(float(r90[f"grid{k}_lat"]), 6),
                              round(float(r90[f"grid{k}_lon"]) % 360.0, 6),
                              float(r90[f"grid{k}_weight"])) for k in range(1, 5))
            mine = sorted((round(b["lat"], 6), round(b["lon"], 6) % 360.0, b["weight"]) for b in box)
            n_iem90 += rec_pts == mine
    rec("(1) IEM set (development): equals session 90's box_from_gid exactly", n_iem == 6,
        f"{n_iem} of 6")
    rec("(1) IEM set: equals session90_airports.csv's recorded box where recorded",
        n_iem90 == n_iem90_n, f"{n_iem90} of {n_iem90_n} (EGLC, KSFO)")
    ec.codes_release(gfs)

    # (2) made-up grids
    ok2 = []
    for name, args, pts in [
        ("1.0 deg, -180 to 179", (360, 181, 90.0, -180.0, -90.0, 179.0, 1.0, 1.0),
         [(41.5, -93.65), (-41.33, 174.8), (51.5, 0.05), (37.6, -122.37), (0.2, -0.3)]),
        ("0.4 deg, -180 to 179.6", (900, 451, 90.0, -180.0, -90.0, 179.6, 0.4, 0.4),
         [(41.53, -93.65), (22.63, 113.81), (-32.22, 148.57)]),
        ("0.25 deg, 0 to 359.75", (1440, 721, 90.0, 0.0, -90.0, 359.75, 0.25, 0.25),
         [(43.68, -79.63), (29.52, 106.48)])]:
        g = synthetic_regular(*args)
        di = args[6]
        for la, lo in pts:
            box = box_regular(g, la, lo)
            sw = sum(b["weight"] for b in box)
            la0 = math.floor(la / di) * di
            lo0 = math.floor(lo / di) * di
            want = {(round(la0, 6), round(lo0 % 360, 6)), (round(la0 + di, 6), round(lo0 % 360, 6)),
                    (round(la0, 6), round((lo0 + di) % 360, 6)),
                    (round(la0 + di, 6), round((lo0 + di) % 360, 6))}
            got = {(round(b["lat"], 6), round(b["lon"] % 360, 6)) for b in box}
            ok2.append(abs(sw - 1) < 1e-12 and got == want)
        ec.codes_release(g)
    rec("(2) made-up regular grids: weights sum to 1 and the right corners", all(ok2),
        f"{sum(ok2)} of {len(ok2)} points")
    g = synthetic_lambert()
    p = lambert_params(g)
    lats = ec.codes_get_array(g, "latitudes")
    lons = ec.codes_get_array(g, "longitudes")
    okl = []
    for la, lo in [(41.53, -93.65), (39.48, -119.77), (37.62, -122.37), (41.96, -87.93),
                   (43.68, -79.63)]:
        box = box_lambert(g, la, lo)
        sw = sum(b["weight"] for b in box)
        # the right corners: brute force over every grid node, the cell whose
        # projected corners enclose the point
        x, y = lcc_xy(p, la, lo)
        x0, y0 = lcc_xy(p, p["lat1"], p["lon1"])
        ii = int((x - x0) // p["Dx"])
        jj = int((y - y0) // p["Dy"])
        want = {jj * p["Nx"] + ii, jj * p["Nx"] + ii + 1, (jj + 1) * p["Nx"] + ii,
                (jj + 1) * p["Nx"] + ii + 1}
        nn = ec.codes_grib_find_nearest(g, la, lo, npoints=1)[0]
        # the eccodes nearest node is among the four, and the four enclose the point
        d = [haversine_km(la, lo, lats[k], lons[k]) for k in want]
        okl.append(abs(sw - 1) < 1e-12 and {b["index"] for b in box} == want
                   and int(nn.index) in want and min(d) <= p["Dx"] / 1000 * 0.75)
    # alternative row scanning: values stored with odd rows reversed; the
    # value index of each corner must give the value made for its position
    ec.codes_set(g, "alternativeRowScanning", 1)
    nx, ny = p["Nx"], p["Ny"]
    # each node's value is its own position number in eccodes' geography
    # (integers, which the packing keeps exactly), stored with odd rows reversed
    stored = np.empty(nx * ny)
    for j in range(ny):
        for i in range(nx):
            k = j * nx + i
            stored[j * nx + (nx - 1 - i) if j % 2 else k] = float(k)
    ec.codes_set_values(g, stored)
    v = ec.codes_get_values(g)
    oka = []
    for la, lo in [(41.53, -93.65), (39.48, -119.77), (37.62, -122.37), (41.96, -87.93)]:
        box = box_lambert(g, la, lo)
        oka.append(all(v[b["index"]] == float(b["geo_index"]) and
                       abs(lats[b["geo_index"]] - b["lat"]) < 1e-9 for b in box)
                   and any(b["index"] != b["geo_index"] for b in box))
    ec.codes_release(g)
    rec("(2) made-up Lambert grid: weights sum to 1 and the right corners", all(okl),
        f"{sum(okl)} of {len(okl)} points")
    rec("(2) made-up Lambert grid with alternate row scanning: each corner's value index is right", all(oka),
        f"{sum(oka)} of {len(oka)} points")

    # (3) guards
    cases = [("valid 2026-08-01T00:00 refused", guard_valid, (dt.datetime(2026, 8, 1, 0),), False),
             ("valid 2026-07-31T23:00 allowed", guard_valid, (dt.datetime(2026, 7, 31, 23),), True),
             ("maximum window ending 2026-08-01T00:00 refused", guard_window_end,
              (dt.datetime(2026, 8, 1, 0),), False),
             ("maximum window ending 2026-07-31T23:00 allowed", guard_window_end,
              (dt.datetime(2026, 7, 31, 23),), True),
             ("climate day 2026-07-31 at KDSM (ends 2026-08-01T06:00 UTC) refused",
              guard_climate_day, (dt.date(2026, 7, 31), "America/Chicago"), False),
             ("climate day 2026-07-30 at KDSM (ends 2026-07-31T06:00 UTC) allowed",
              guard_climate_day, (dt.date(2026, 7, 30), "America/Chicago"), True),
             ("climate day 2026-07-30 at KSFO (ends 2026-07-31T08:00 UTC) allowed",
              guard_climate_day, (dt.date(2026, 7, 30), "America/Los_Angeles"), True),
             ("climate day 2026-07-31 at KRNO (ends 2026-08-01T08:00 UTC) refused",
              guard_climate_day, (dt.date(2026, 7, 31), "America/Los_Angeles"), False)]
    n3 = 0
    for name, fn, args, allowed in cases:
        try:
            fn(*args)
            got = True
        except GuardError:
            got = False
        n3 += got == allowed
    s, e = climate_day_window(dt.date(2026, 1, 15), "America/Chicago")
    s2, e2 = climate_day_window(dt.date(2026, 7, 15), "America/Chicago")
    std_ok = (s.hour, e.hour, s2.hour, e2.hour) == (6, 6, 6, 6)
    rec("(3) guards", n3 == len(cases) and std_ok,
        f"{n3} of {len(cases)} cases; climate day is local standard time in winter and summer: {std_ok}")
    try:
        leads_ok = leads_kept(dt.datetime(2026, 7, 31, 18), range(3, 49)) == [3, 4, 5] and \
            leads_kept(dt.datetime(2026, 7, 31, 12), range(3, 49, 3)) == [3, 6, 9] and \
            leads_kept(dt.datetime(2026, 7, 30, 0), range(3, 49)) == list(range(3, 48))
    except Exception:
        leads_ok = False
    rec("(3) the planned steps stop at the limit", leads_ok, "cycles 2026-07-31 18z, 12z and 2026-07-30 00z")

    # (4) degrees F to C
    pairs = [(32, Fraction(0)), (212, Fraction(100)), (-40, Fraction(-40)), (50, Fraction(10)),
             (33, Fraction(5, 9)), (0, Fraction(-160, 9)), (99, Fraction(335, 9))]
    n4 = sum(abs(Fraction(f_to_c(f)) - want) <= Fraction(math.ulp(max(abs(float(want)), 1.0)))
             for f, want in pairs)
    rec("(4) degrees F to C exact (within 1 ulp of the exact fraction)", n4 == len(pairs),
        f"{n4} of {len(pairs)}")

    # (3b, owner's ruling) the CLI filter reads only the date field, and keeps
    # no climate day ending after the limit
    class DateOnly(dict):
        def __getitem__(self, k):
            if k != "valid":
                raise AssertionError(f"field {k} read before the date filter")
            return dict.__getitem__(self, k)
    fake = [DateOnly(valid=d, high="x") for d in
            ["2026-07-29", "2026-07-30", "2026-07-31", "2026-08-01", "2026-10-01", "2023-07-31"]]
    try:
        kept, after, before = cli_keep(fake, "America/Chicago", dt.date(2023, 8, 1))
        okc = ([dict.__getitem__(r, "valid") for r in kept] == ["2026-07-29", "2026-07-30"]
               and after == 3 and before == 1)
    except AssertionError:
        okc = False
    rec("(3b) CLI filter: a made-up response with days after the limit keeps none of them",
        okc, "6 made-up records: 2 kept, 3 after the limit dropped unread, 1 before the window")

    # (5) cycle lists
    n5 = []
    for a in A.values():
        cy = cycles(a["first_cycle"])
        want = 4384 if a["role"] == "development" else 2920
        per = {h: sum(1 for c in cy if c.hour == h) for h in CYCLE_HOURS}
        n5.append(len(cy) == want and set(per.values()) == {want // 4}
                  and cy[0] == a["first_cycle"] and cy[-1] == LAST_CYCLE)
    rec("(5) cycle lists: development 4,384 (1,096 per cycle hour), claim 2,920 (730)", all(n5),
        f"{sum(n5)} of 12")
    bad = [n for n, ok in res if not ok]
    say(f"== --check: {len(res) - len(bad)} of {len(res)} PASS" + (f"; FAIL: {bad}" if bad else ""))
    return not bad


# ------------------------------------------------------------------ network helpers

ECMWF = "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/"
NBM = "https://noaa-nbm-grib2-pds.s3.amazonaws.com/"
GFS = "https://noaa-gfs-bdp-pds.s3.amazonaws.com/"
IEM = "https://mesonet.agron.iastate.edu"
NCEI_DATA = "https://www.ncei.noaa.gov/access/services/data/v1"
GHCND_STATIONS = "https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-stations.txt"
TMP = None                                        # the one temporary folder (--tmp)
_local = threading.local()
_iem_lock = threading.Lock()
_iem_last = [0.0]
IEM_GAP = 4.0                                     # seconds between IEM requests (IEM throttles, HTTP 429)
REQUESTS = {"n": 0, "bytes": 0}
_req_lock = threading.Lock()


def http():
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
        _local.s.headers.update({"User-Agent": "MLwx/session113"})
    return _local.s


class Missing(Exception):
    pass


class IndexMismatch(Exception):
    """The index's byte range does not hold one GRIB message (owner's ruling,
    session 113: counted as a gap, nothing filled)."""


def get(url, params=None, byte_range=None, tries=5, iem=False, timeout=(10, 180)):
    """GET with up to `tries` attempts. 403/404 -> Missing. Throttling
    answers (429, 500, 502, 503, 504) wait longer. IEM requests are serial
    and spaced, with long back-off on HTTP 429."""
    headers = {"Range": f"bytes={byte_range[0]}-{byte_range[1]}"} if byte_range else {}
    last = None
    for i in range(tries):
        if iem:
            with _iem_lock:
                w = _iem_last[0] + IEM_GAP - time.time()
                if w > 0:
                    time.sleep(w)
                _iem_last[0] = time.time()
        try:
            r = http().get(url, params=params, headers=headers, timeout=timeout)
            if r.status_code in (403, 404):
                raise Missing(f"HTTP {r.status_code}")
            if r.status_code == 200 or (byte_range and r.status_code == 206):
                if byte_range and len(r.content) != byte_range[1] - byte_range[0] + 1:
                    raise RuntimeError(f"short read {len(r.content)} B")
                with _req_lock:
                    REQUESTS["n"] += 1
                    REQUESTS["bytes"] += len(r.content)
                return r
            last = f"HTTP {r.status_code}"
            if r.status_code == 429:
                time.sleep(60 * (i + 1))
                continue
            if r.status_code in (500, 502, 503, 504):
                time.sleep(20 * (i + 1))
                continue
        except Missing:
            raise
        except Exception as e:  # noqa: BLE001 - every failure is retried, then reported
            last = f"{type(e).__name__}: {e}"
        time.sleep(5 * (i + 1))
    raise RuntimeError(f"failed {tries} times: {url} {params or ''} ({last})")


def s3_list(base, prefix):
    """S3 ListObjectsV2 (anonymous), all pages: [(key, size, last_modified)].
    The record's session82 s3list is used by the probe's layout checks; this
    copy uses the pooled session and the retry rule above, for bulk listing."""
    keys, token = [], None
    while True:
        p = {"list-type": "2", "prefix": prefix}
        if token:
            p["continuation-token"] = token
        t = get(base, params=p).text
        for c in re.findall(r"<Contents>(.*?)</Contents>", t, re.S):
            keys.append((re.search(r"<Key>([^<]*)", c).group(1),
                         int(re.search(r"<Size>(\d+)", c).group(1)),
                         re.search(r"<LastModified>([^<]*)", c).group(1)))
        m = re.search(r"<NextContinuationToken>([^<]*)", t)
        if not m:
            return keys
        token = m.group(1)


def record82():
    """session82_source_probe, imported read only. Its module makes a
    temporary folder on import; tempfile.tempdir points it inside --tmp."""
    tempfile.tempdir = str(TMP)
    return import_record("session82_source_probe")


WORKERS = [MAX_WORKERS]     # 8 (D107.7); the owner allowed 16 or 32 for the IFS re-measurement and pull only
OVERRIDE = [""]             # the owner's override text, recorded in the meta file


def pmap(fn, items, workers=None):
    with ThreadPoolExecutor(max_workers=workers or WORKERS[0]) as ex:
        return list(ex.map(fn, items))


META_KEYS = ["shortName", "name", "units", "typeOfLevel", "level", "stepType", "stepRange",
             "startStep", "endStep", "typeOfStatisticalProcessing", "lengthOfTimeRange",
             "dataDate", "dataTime", "validityDate", "validityTime", "gridType", "Ni", "Nj",
             "Nx", "Ny", "latitudeOfFirstGridPointInDegrees", "longitudeOfFirstGridPointInDegrees",
             "latitudeOfLastGridPointInDegrees", "longitudeOfLastGridPointInDegrees",
             "iDirectionIncrementInDegrees", "jDirectionIncrementInDegrees", "DxInMetres",
             "DyInMetres", "LaDInDegrees", "LoVInDegrees", "Latin1InDegrees", "Latin2InDegrees",
             "shapeOfTheEarth", "radius", "scanningMode", "packingType", "numberOfDataPoints",
             "bitmapPresent", "centre", "generatingProcessIdentifier", "edition",
             "discipline", "parameterCategory", "parameterNumber"]


def grib_meta(gid):
    k = {}
    for key in META_KEYS:
        try:
            k[key] = ec.codes_get(gid, key)
        except Exception:  # noqa: BLE001 - a key a grid type lacks
            k[key] = None
    return k


def grid_signature(m):
    keys = ["gridType", "Ni", "Nj", "Nx", "Ny", "latitudeOfFirstGridPointInDegrees",
            "longitudeOfFirstGridPointInDegrees", "latitudeOfLastGridPointInDegrees",
            "longitudeOfLastGridPointInDegrees", "iDirectionIncrementInDegrees",
            "jDirectionIncrementInDegrees", "DxInMetres", "DyInMetres", "LaDInDegrees",
            "LoVInDegrees", "Latin1InDegrees", "Latin2InDegrees", "scanningMode", "radius"]
    return "|".join(f"{k}={m.get(k)}" for k in keys if m.get(k) is not None)


def msg_valid(m):
    return dt.datetime.strptime(f"{m['validityDate']}{int(m['validityTime']):04d}", "%Y%m%d%H%M")


def msg_run(m):
    return dt.datetime.strptime(f"{m['dataDate']}{int(m['dataTime']):04d}", "%Y%m%d%H%M")


def fetch_message(url, off, length, planned_valid, planned_window_end=None):
    """One GRIB message by byte range, guarded before the request (planned
    valid time and window end) and after decoding (the message's own valid
    time). Returns (gid, meta, bytes); the caller releases gid."""
    guard_valid(planned_valid)
    if planned_window_end is not None:
        guard_window_end(planned_window_end)
    r = get(url, byte_range=(off, off + length - 1))
    if r.content[:4] != b"GRIB" or r.content[-4:] != b"7777":
        raise IndexMismatch("index offset does not match the file (no GRIB message at the index's byte range)")
    gid = ec.codes_new_from_message(r.content)
    m = grib_meta(gid)
    try:
        guard_valid(msg_valid(m))
    except GuardError:
        ec.codes_release(gid)
        raise
    return gid, m, r.content


# ------------------------------------------------------------------ source layouts

IFS_STEPS = list(range(3, 49, 3))
AIFS_STEPS = list(range(6, 49, 6))


def ecmwf_folder(model, cyc, stream=None):
    """Folder of a cycle's files, by session 82's ecmwf_path (record). IFS 06
    and 18 UTC runs are under scda until 2026-05-11 and under oper from
    2026-05-12 (found by this probe's listing); the listing tries both and
    records the folder each cycle uses."""
    if model == "aifs-single":
        # the operational folder only (session 82's ecmwf_path gives the
        # experimental folder before 2025-02-26, which is not operational)
        return f"{cyc:%Y%m%d}/{cyc:%H}z/aifs-single/0p25/oper/", "oper"
    s82 = record82()
    if stream is None:
        stream = "oper" if cyc.hour in (0, 12) else "scda"
    p = s82.ecmwf_path(cyc.date(), model, 0, f"{cyc.hour:02d}", stream)
    return p.rsplit("/", 1)[0] + "/", stream


def ecmwf_file(model, cyc, step, folder=None):
    if folder is None:
        folder, stream = ecmwf_folder(model, cyc)
    else:
        stream = folder.rstrip("/").split("/")[-1]
    return f"{folder}{cyc:%Y%m%d%H}0000-{step}h-{stream}-fc"


def ifs_grid_label(cyc):
    return "0p4" if cyc.date() < dt.date(2024, 2, 1) else "0p25"


def nbm_file(cyc, lead):
    return f"blend.{cyc:%Y%m%d}/{cyc:%H}/core/blend.t{cyc:%H}z.core.f{lead:03d}.co.grib2"


def ecmwf_index_lines(path):
    r = get(ECMWF + path + ".index")
    return [json.loads(x) for x in r.text.splitlines() if x.strip().startswith("{")], r.text


def idx_parse(text):
    out = []
    for ln in text.splitlines():
        f = ln.split(":")
        out.append(dict(n=int(f[0]), off=int(f[1]), d=f[2], desc=":".join(f[3:]), line=ln))
    return out


# ------------------------------------------------------------------ table writers

def write_csv_gz(path, cols, rows):
    """New gzipped CSV (mode x: an existing file stops the run), fixed mtime
    so equal content gives equal bytes."""
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    w.writerows(rows)
    data = buf.getvalue().encode()
    with open(path, "xb") as f:
        with gzip.GzipFile(fileobj=f, mode="wb", mtime=0, filename="") as gz:
            gz.write(data)
    return path


def write_csv(path, cols, rows):
    with open(path, "x", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(cols)
        w.writerows(rows)
    return path


def read_csv_gz(path):
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ CLI filter (owner's ruling)

def cli_keep(records, tzname, first_day):
    """Keep CLI records by their date field alone, before any other field is
    read: a record whose climate day ends after the limit, or is before the
    window, is dropped unread. Returns (kept, n_dropped_after, n_before)."""
    kept, after, before = [], 0, 0
    for rec in records:
        day = dt.date.fromisoformat(str(rec["valid"])[:10])
        if climate_day_window(day, tzname)[1] > LIMIT:
            after += 1
            continue
        if day < first_day:
            before += 1
            continue
        kept.append(rec)
    return kept, after, before


# ------------------------------------------------------------------ --probe

PROBE_ROWS = []


def prow(source, topic, key, value, note=""):
    PROBE_ROWS.append([source, topic, key, value, note])


def list_cycle(args):
    """One cycle's listing: (cycle, {step: (size, last_modified)} for grib2,
    set of steps with an index file, error)."""
    source, cyc = args
    try:
        if source in ("ifs", "aifs"):
            model = "ifs" if source == "ifs" else "aifs-single"
            folder, stream = ecmwf_folder(model, cyc)
            keys = s3_list(ECMWF, folder)
            if not keys and model == "ifs" and cyc.hour in (6, 18):
                folder, stream = ecmwf_folder(model, cyc, "oper")
                keys = s3_list(ECMWF, folder)
            g, ix = {}, set()
            for k, size, lm in keys:
                m = re.search(r"-(\d+)h-" + stream + r"-fc\.(grib2|index)$", k)
                if not m:
                    continue
                s = int(m.group(1))
                if m.group(2) == "grib2":
                    g[s] = (size, lm)
                else:
                    ix.add(s)
            return cyc, g, ix, "", folder
        if source == "nbm48":
            keys = s3_list(NBM, nbm_file(cyc, 48))
            g = {48: (size, lm) for k, size, lm in keys if k.endswith(".co.grib2")}
            ix = {48 for k, _, _ in keys if k.endswith(".co.grib2.idx")}
            return cyc, g, ix, "", ""
        if source == "nbmfull":
            keys = s3_list(NBM, f"blend.{cyc:%Y%m%d}/{cyc:%H}/core/")
            g, ix = {}, set()
            for k, size, lm in keys:
                m = re.search(r"\.f(\d{3})\.co\.grib2(\.idx)?$", k)
                if m:
                    if m.group(2):
                        ix.add(int(m.group(1)))
                    else:
                        g[int(m.group(1))] = (size, lm)
            return cyc, g, ix, "", ""
        if source == "gfs":
            keys = s3_list(GFS, f"gfs.{cyc:%Y%m%d}/{cyc:%H}/atmos/gfs.t{cyc:%H}z.pgrb2.0p25.f048")
            g = {48: (size, lm) for k, size, lm in keys if k.endswith(".f048")}
            ix = {48 for k, _, _ in keys if k.endswith(".f048.idx")}
            return cyc, g, ix, "", ""
    except Missing as e:
        return cyc, {}, set(), f"missing: {e}", ""
    except Exception as e:  # noqa: BLE001 - recorded, the probe goes on
        return cyc, {}, set(), f"error: {e}", ""
    raise ValueError(source)


def listing(source, cycs, path):
    """List every cycle (8 at once) and write the listing table. Reuses an
    existing listing file (a rerun does not list again)."""
    if path.exists():
        rows = read_csv_gz(path)
        say(f"  {source}: listing reused from {path.name} ({len(rows)} cycles)")
        return rows
    t0 = time.time()
    res = pmap(list_cycle, [(source, c) for c in cycs])
    rows = []
    for cyc, g, ix, err, folder in res:
        steps = sorted(s for s in g if s <= LEAD_MAX)
        rows.append([iso(cyc), " ".join(map(str, steps)),
                     " ".join(map(str, sorted(s for s in ix if s <= LEAD_MAX))),
                     " ".join(f"{s}:{g[s][0]}" for s in steps),
                     g[48][1] if 48 in g else "", err, folder])
    write_csv_gz(path, ["cycle", "grib_steps", "index_steps", "sizes", "last_modified_48", "error", "folder"],
                 rows)
    say(f"  {source}: listed {len(cycs)} cycles in {time.time() - t0:.0f} s; "
        f"errors {sum(1 for r in rows if r[5])}")
    return read_csv_gz(path)


def coverage(source, rows, nominal, first_by_group):
    """Present and missing cycles per airport group, cycle hour and test year.
    A cycle is complete if every nominal step within leads 3 to 48 and on or
    before the limit has both its GRIB file and its index; partial if some do."""
    by = {}
    for r in rows:
        cyc = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ")
        g = set(int(x) for x in r["grib_steps"].split()) if r["grib_steps"] else set()
        ix = set(int(x) for x in r["index_steps"].split()) if r["index_steps"] else set()
        need = set(leads_kept(cyc, nominal(cyc)))
        have = need & g & ix
        state = "complete" if have == need else ("partial" if have else "missing")
        for grp, first in first_by_group.items():
            if cyc >= first:
                key = (grp, cyc.hour, test_year(cyc))
                d = by.setdefault(key, {"complete": 0, "partial": 0, "missing": 0,
                                        "steps_missing": 0})
                d[state] += 1
                d["steps_missing"] += len(need - have)
    for (grp, h, ty), d in sorted(by.items()):
        prow(source, "coverage", f"{grp}|{h:02d}z|{ty}",
             f"complete {d['complete']}; partial {d['partial']}; missing {d['missing']}",
             f"nominal steps missing {d['steps_missing']}")
    tot = {}
    for (grp, _, _), d in by.items():
        t = tot.setdefault(grp, [0, 0, 0, 0])
        t[0] += d["complete"]
        t[1] += d["partial"]
        t[2] += d["missing"]
        t[3] += d["steps_missing"]
    for grp, t in tot.items():
        say(f"  {source} coverage {grp}: complete {t[0]}, partial {t[1]}, missing {t[2]} "
            f"(nominal steps missing {t[3]})")
    return by


def ifs_nominal(cyc):
    return IFS_STEPS


def aifs_nominal(cyc):
    return AIFS_STEPS


def nbm_nominal(cyc, hourly_to_48_from=None):
    if hourly_to_48_from and cyc >= hourly_to_48_from:
        return list(range(3, 49))
    return list(range(3, 37)) + [39, 42, 45, 48]


def ecmwf_index_any(model, cyc, step):
    """The index of a file, trying the oper folder for an IFS 06/18 UTC run
    whose scda folder is missing (from 2026-05-12)."""
    path = ecmwf_file(model, cyc, step)
    try:
        return path, ecmwf_index_lines(path)[0]
    except Missing:
        if model != "ifs" or cyc.hour not in (6, 18):
            raise
        path = ecmwf_file(model, cyc, step, ecmwf_folder(model, cyc, "oper")[0])
        return path, ecmwf_index_lines(path)[0]


def decode_index_message(model, cyc, step, param, levtype="sfc", window_hours=None):
    """Find one param in an ECMWF index and decode its metadata (no value)."""
    path, L = ecmwf_index_any(model, cyc, step)
    m = [x for x in L if x["param"] == param and x.get("levtype") == levtype]
    if len(m) != 1:
        return None, len(m)
    valid = cyc + dt.timedelta(hours=step)
    gid, meta, b = fetch_message(ECMWF + path + ".grib2", m[0]["_offset"], m[0]["_length"],
                                 valid, valid if window_hours else None)
    meta["_bytes"] = len(b)
    meta["_url"] = ECMWF + path + ".grib2"
    meta["_range"] = f"{m[0]['_offset']}-{m[0]['_offset'] + m[0]['_length'] - 1}"
    return (gid, meta), 1


def index_params(model, cyc, step):
    try:
        _, L = ecmwf_index_any(model, cyc, step)
    except Missing:
        return None
    return {(x["param"], x.get("levtype")) for x in L}, {x["param"]: x["_length"] for x in L
                                                       if x.get("levtype") == "sfc"}


def bisect_dates(lo, hi, test):
    """lo: test False, hi: test True (as session 82's bisect); None = skip a day.
    The ends are tested first: (None, lo) if present at lo, (hi, None) if absent at hi."""
    if test(lo):
        return None, lo
    if not test(hi):
        return hi, None
    while (hi - lo).days > 1:
        mid = lo + dt.timedelta((hi - lo).days // 2)
        v = test(mid)
        while v is None and mid < hi - dt.timedelta(1):
            mid += dt.timedelta(1)
            v = test(mid)
        if v is None:
            break
        if v:
            hi = mid
        else:
            lo = mid
    return lo, hi


_pos_lock = threading.Lock()
_POS = {}            # grid label -> {(airport, set): [value indices]}
POS_COLS = ["airport", "position_set", "lat", "lon"] + [
    f"p{k}_{c}" for k in range(1, 5)
    for c in ("index", "geo_index", "lat", "lon", "weight", "distance_km", "nearest")] + ["grid"]


def grid_res(m):
    if m["gridType"] == "lambert":
        return "lambert"
    return {0.25: "0p25", 0.4: "0p4"}.get(m["iDirectionIncrementInDegrees"], f"{m['iDirectionIncrementInDegrees']}deg")


def grid_label(source, m):
    """A grid's name: source, resolution and the first 8 hex digits of the
    SHA-256 of its geometry keys (a grid that changes gets a new name)."""
    return f"{source}_{grid_res(m)}_{hashlib.sha256(grid_signature(m).encode()).hexdigest()[:8]}"


def ensure_positions(source, gid, meta, A, airports, note=None):
    """The four points and weights of every airport and position set on this
    message's grid, the nearest marked, written once to
    positions_<label>.csv; later calls read the cache. `index` is the
    position in the decoded values array, `geo_index` in eccodes'
    latitudes and longitudes (they differ only on a grid with alternate row
    scanning). Returns (label, {(airport, set): [index x 4]})."""
    label = grid_label(source, meta)
    with _pos_lock:
        if label in _POS:
            return label, _POS[label]
        path = OUT / f"positions_{label}.csv"
        pos = {}
        if path.exists():
            with open(path, newline="") as f:
                for r in csv.DictReader(f):
                    pos[(r["airport"], r["position_set"])] = [int(r[f"p{k}_index"]) for k in range(1, 5)]
        else:
            rows = []
            for icao in airports:
                for setname, (lat, lon) in A[icao]["sets"].items():
                    try:
                        box = mark_nearest(box_any(gid, lat, lon))
                    except ValueError as e:
                        if note is not None:
                            note.append((icao, setname, str(e)))
                        continue
                    pos[(icao, setname)] = [b["index"] for b in box]
                    row = [icao, setname, repr(lat), repr(lon)]
                    for b in box:
                        row += [b["index"], b.get("geo_index", b["index"]), repr(b["lat"]), repr(b["lon"]),
                                repr(b["weight"]), repr(b["distance_km"]), b["nearest"]]
                    rows.append(row + [grid_signature(meta)])
            write_csv(path, POS_COLS, rows)
        _POS[label] = pos
        return label, pos


def read_positions_rows(label):
    with open(OUT / f"positions_{label}.csv", newline="") as f:
        return list(csv.DictReader(f))


def version_changes(source, model, first):
    """generatingProcessIdentifier and grid name of the 00z step-0 land-sea
    mask on the 1st of each month, then each change dated to the day by
    bisection (archive evidence of a model or grid change)."""
    def look(d):
        try:
            got, _ = decode_index_message(model, dt.datetime(d.year, d.month, d.day, 0), 0, "lsm")
        except Missing:
            return None
        if not got:
            return None
        ec.codes_release(got[0])
        return got[1]["generatingProcessIdentifier"], grid_label(source, got[1])
    pts = []
    d = first
    while d <= dt.date(2026, 7, 30):
        v = look(d)
        if v:
            pts.append((d, v))
        d = (d.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    v = look(dt.date(2026, 7, 30))
    if v:
        pts.append((dt.date(2026, 7, 30), v))
    prow(source, "version (archive)", "start", f"{pts[0][0]}: generatingProcessIdentifier {pts[0][1][0]}, "
         f"grid {pts[0][1][1]}", f"{len(pts)} dates decoded (1st of each month, 00z, lsm step 0)")
    for (d0, v0), (d1, v1) in zip(pts, pts[1:]):
        for k, what in ((0, "generatingProcessIdentifier"), (1, "grid")):
            if v0[k] != v1[k]:
                lo, hi = bisect_dates(d0, d1, lambda d: (lambda v: None if v is None else v[k] == v1[k])(look(d)))
                prow(source, "version (archive)", f"{what} {v0[k]} -> {v1[k]}",
                     f"last old {lo}, first new {hi}", "00z runs, by bisection")
                say(f"  {source} {what} {v0[k]} -> {v1[k]}: first new 00z run {hi}")


def run_probe():
    say("== --probe (metadata and counts only; spent dates) ==")
    OUT.mkdir(exist_ok=True)
    A = load_airports()
    s82 = record82()
    dev_cycles = cycles(DEV_FIRST)
    groups = {"development": DEV_FIRST, "claim": CLAIM_FIRST}

    # ---- ECMWF layout facts (session 82's helpers)
    say("-- ECMWF layout")
    for d, c in [(dt.date(2023, 8, 1), "06"), (dt.date(2024, 3, 1), "18"), (dt.date(2025, 3, 1), "06")]:
        sub = s82.s3list(ECMWF, f"{d:%Y%m%d}/{c}z/")[0]
        prow("ecmwf", "layout", f"{d}|{c}z", " ".join(p.split("/")[-2] for p in sub))
    prow("ecmwf", "layout", "stream", "IFS 00/12 UTC: oper; IFS 06/18 UTC: scda; AIFS all cycles: oper",
         "listing")

    # ---- IFS
    say("-- IFS listing (every cycle in the development window)")
    rows_ifs = listing("ifs", dev_cycles, OUT / "listing_ifs.csv.gz")
    coverage("ifs", rows_ifs, ifs_nominal, groups)
    errs = [r for r in rows_ifs if r["error"]]
    prow("ifs", "listing", "errors", len(errs), "; ".join(f"{r['cycle']} {r['error'][:60]}" for r in errs[:5]))
    sizes = [int(x.split(":")[1]) for r in rows_ifs for x in r["sizes"].split()]
    prow("ifs", "listing", "grib files listed", len(sizes),
         f"median file {sorted(sizes)[len(sizes) // 2] if sizes else 0} B")

    say("-- IFS metadata (decoded headers only)")
    labels = {}
    for cyc in [dt.datetime(2023, 8, 1, 0), dt.datetime(2024, 2, 1, 0), dt.datetime(2024, 3, 1, 0)]:
        (gid, m), _ = decode_index_message("ifs", cyc, 3, "2t")
        lab, pos = ensure_positions("ifs", gid, m, A, ALL12)
        labels[lab] = cyc
        ec.codes_release(gid)
        prow("ifs", "grid", f"{lab} (2t, {iso(cyc)} step 3)", grid_signature(m),
             f"2t {m['_bytes']} B; {m['_url']} {m['_range']}; positions_{lab}.csv, {len(pos)} boxes")
        prow("ifs", "2t message", lab, f"shortName {m['shortName']}, units {m['units']}, "
             f"stepType {m['stepType']}, packing {m['packingType']}, bitmap {m['bitmapPresent']}")
    for d in [dt.date(2023, 8, 1), dt.date(2023, 11, 1), dt.date(2024, 1, 31)]:
        for c in (0, 6):
            cyc = dt.datetime(d.year, d.month, d.day, c)
            p0 = index_params("ifs", cyc, 0)
            p3 = index_params("ifs", cyc, 3)
            mx = sorted(p for p, lt in (p3[0] if p3 else set()) if p.startswith("mx"))
            zs = ("z", "sfc") in (p0[0] if p0 else set())
            prow("ifs", "0p4 fields", f"{d}|{c:02d}z", f"maximum params {mx or 'none'}; z sfc at step 0 {zs}")

    def has(param, step, cyc_hour, levtype="sfc"):
        def t(d):
            p = index_params("ifs", dt.datetime(d.year, d.month, d.day, cyc_hour), step)
            if p is None:
                return None
            ok = (param, levtype) in p[0]
            if ok and param.startswith("mx"):
                ok = p[1].get(param, 0) > 1000        # a 224-byte message is empty
            return ok
        return t
    for param, step in [("mx2t3", 3), ("z", 0), ("mx2t3", 48)]:
        for ch in (0, 6):
            lo, hi = bisect_dates(dt.date(2024, 2, 1), dt.date(2026, 7, 30), has(param, step, ch))
            prow("ifs", "field first present", f"{param}|step {step}|{ch:02d}z",
                 f"last absent {lo}, first present {hi}", "bisection over index files, 2024-02-01 to 2026-07-30")
            say(f"  IFS {param} step {step} {ch:02d}z: last absent {lo}, first present {hi}")
    # the maximum field and orography metadata
    for cyc, step in [(dt.datetime(2025, 3, 1, 0), 3), (dt.datetime(2025, 3, 1, 0), 48),
                      (dt.datetime(2025, 3, 1, 6), 6), (dt.datetime(2025, 3, 1, 0), 0)]:
        try:
            got, n = decode_index_message("ifs", cyc, step, "mx2t3", window_hours=3)
        except Exception as e:  # noqa: BLE001 - an empty step-0 message may not decode
            got, n = None, f"not decoded ({str(e)[:60]})"
        if got:
            gid, m = got
            prow("ifs", "maximum field", f"mx2t3|{iso(cyc)}|step {step}",
                 f"name '{m['name']}', stepType {m['stepType']}, stepRange {m['stepRange']}, "
                 f"units {m['units']}, {m['_bytes']} B", "window (step-3, step] UTC from stepRange")
            ec.codes_release(gid)
        else:
            prow("ifs", "maximum field", f"mx2t3|{iso(cyc)}|step {step}", f"index lines {n}")
    got, n = decode_index_message("ifs", dt.datetime(2025, 3, 1, 0), 0, "z")
    if got:
        gid, m = got
        prow("ifs", "orography", "z sfc step 0 (2025-03-01 00z)", f"name '{m['name']}', units {m['units']}, "
             f"{m['_bytes']} B, grid {grid_label('ifs', m)}",
             "surface geopotential; height = z / 9.80665")
        ec.codes_release(gid)
    version_changes("ifs", "ifs", dt.date(2023, 8, 1))
    for lab in labels:
        rows = read_positions_rows(lab)
        n_same = 0
        for icao in ALL12:
            p = A[icao]["p91"]
            setname = "gfs" if icao in DEV else "iem"
            r = next(x for x in rows if (x["airport"], x["position_set"]) == (icao, setname))
            gfs_pts = sorted((round(float(p[f"p{k}_lat"]), 6), round(float(p[f"p{k}_lon"]) % 360, 6))
                             for k in range(1, 5))
            mine = sorted((round(float(r[f"p{k}_lat"]), 6), round(float(r[f"p{k}_lon"]) % 360, 6))
                          for k in range(1, 5))
            n_same += gfs_pts == mine
        prow("ifs", "positions", f"{lab}: four points equal GFS's (gfs set, or iem at claim airports)",
             f"{n_same} of 12")

    # ---- AIFS
    say("-- AIFS listing")
    aifs_cycles = [c for c in dev_cycles if c.date() >= dt.date(2025, 2, 1)]
    rows_aifs = listing("aifs", aifs_cycles, OUT / "listing_aifs.csv.gz")
    first_oper = next((r["cycle"] for r in rows_aifs if r["grib_steps"]), None)
    prow("aifs", "first operational run", "first cycle with files under aifs-single/0p25/oper/", first_oper)
    fo = dt.datetime.strptime(first_oper, "%Y-%m-%dT%H:%MZ")
    exp = 0
    for d in [dt.date(2025, 2, 10), dt.date(2025, 2, 25)]:
        exp += bool(s3_list(ECMWF, f"{d:%Y%m%d}/00z/aifs-single/0p25/experimental/"))
    prow("aifs", "layout", "experimental folder present on 2025-02-10 and 2025-02-25 (00z)", f"{exp} of 2",
         "not used: not operational")
    coverage("aifs", [r for r in rows_aifs if r["cycle"] >= first_oper], aifs_nominal,
             {"development": fo, "claim": fo})
    (gid, m), _ = decode_index_message("aifs-single", dt.datetime(2025, 3, 1, 0), 6, "2t")
    lab, pos = ensure_positions("aifs", gid, m, A, ALL12)
    prow("aifs", "grid", f"{lab} (2t, 2025-03-01 00z step 6)", grid_signature(m),
         f"2t {m['_bytes']} B; positions_{lab}.csv, {len(pos)} boxes")
    ec.codes_release(gid)
    for cyc in [dt.datetime(2025, 3, 1, 0), dt.datetime(2025, 3, 1, 6), dt.datetime(2026, 7, 1, 12)]:
        p6 = index_params("aifs-single", cyc, 6)
        p0 = index_params("aifs-single", cyc, 0)
        if p6 is None or p0 is None:
            prow("aifs", "fields", iso(cyc), "index missing")
            continue
        mx = sorted(p for p, lt in p6[0] if p.startswith("mx") or p.startswith("mn"))
        prow("aifs", "fields", iso(cyc), f"maximum params {mx or 'none'}; z sfc at step 0 {('z', 'sfc') in p0[0]}")
    got, n = decode_index_message("aifs-single", dt.datetime(2025, 3, 1, 0), 0, "z")
    if got:
        prow("aifs", "orography", "z sfc step 0", f"name '{got[1]['name']}', units {got[1]['units']}, "
             f"{got[1]['_bytes']} B", "surface geopotential; height = z / 9.80665")
        ec.codes_release(got[0])
    version_changes("aifs", "aifs-single", (fo + dt.timedelta(days=1)).date())
    for cyc in [dt.datetime(2025, 3, 1, 0), dt.datetime(2026, 7, 1, 0)]:
        L, _ = ecmwf_index_lines(ecmwf_file("aifs-single", cyc, 6))
        prow("aifs", "index 'model' key", iso(cyc), sorted({x.get("model", "(none)") for x in L}))

    # ---- NBM grid
    say("-- NBM listing (f048 every cycle; all steps on the 1st of each month)")
    rows_n48 = listing("nbm48", dev_cycles, OUT / "listing_nbm48.csv.gz")
    month_cycles = [c for c in dev_cycles if c.day == 1]
    rows_nf = listing("nbmfull", month_cycles, OUT / "listing_nbm_monthly.csv.gz")
    dist = {}
    for r in rows_nf:
        st = tuple(s for s in (int(x) for x in r["grib_steps"].split()) if 3 <= s <= 48)
        dist.setdefault(st, []).append(r["cycle"])
    for st, cs in sorted(dist.items(), key=lambda x: x[1][0]):
        prow("nbm", "steps 3 to 48 (monthly sample)", f"{len(st)} steps: {st[0] if st else '-'}..{st[-1] if st else '-'}"
             f"{' hourly' if st and len(st) == st[-1] - st[0] + 1 else ''}",
             f"{len(cs)} cycles, {cs[0]} to {cs[-1]}")
    hourly48 = [r["cycle"] for r in rows_nf if all(str(s) in r["grib_steps"].split() for s in range(37, 49))]
    h48 = dt.datetime.strptime(hourly48[0], "%Y-%m-%dT%H:%MZ") if hourly48 else None
    if h48:
        lo, hi = bisect_dates(h48.date() - dt.timedelta(days=40), h48.date(),
                              lambda d: bool(s3_list(NBM, nbm_file(dt.datetime(d.year, d.month, d.day, 0), 37))))
        prow("nbm", "hourly to 48 h", "f037 first present (00z, bisection)", f"last absent {lo}, first present {hi}")
        if hi:
            h48 = dt.datetime(hi.year, hi.month, hi.day, 0)
    nom = lambda c: nbm_nominal(c, h48)  # noqa: E731
    # coverage from the f048 listing (cycle present) plus the monthly step listing
    cov48 = [{"cycle": r["cycle"], "grib_steps": r["grib_steps"], "index_steps": r["index_steps"]} for r in rows_n48]
    by = {}
    for r in cov48:
        cyc = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ")
        ok = "48" in r["grib_steps"].split() and "48" in r["index_steps"].split()
        for grp, first in groups.items():
            if cyc >= first:
                k = (grp, cyc.hour, test_year(cyc))
                by.setdefault(k, [0, 0])[0 if ok else 1] += 1
    for (grp, h, ty), (a, b) in sorted(by.items()):
        prow("nbm", "coverage (f048 file and index)", f"{grp}|{h:02d}z|{ty}", f"present {a}; missing {b}",
             "steps per cycle from the monthly sample")
    say(f"  nbm f048 present {sum(v[0] for k, v in by.items() if k[0] == 'development')} of "
        f"{sum(sum(v) for k, v in by.items() if k[0] == 'development')} development-window cycles")
    # idx lines: TMP, TMAX windows, any terrain field
    cyc0 = dt.datetime(2025, 3, 1, 0)
    tmax = {}
    terrain = set()
    for ch in CYCLE_HOURS:
        cyc = cyc0.replace(hour=ch)
        for lead in nbm_nominal(cyc, None):
            try:
                L = idx_parse(get(NBM + nbm_file(cyc, lead) + ".idx").text)
            except Missing:
                continue
            for x in L:
                if x["desc"].startswith("TMAX:2 m above ground:") and not x["desc"].endswith("std dev"):
                    tmax.setdefault(ch, []).append(x["desc"].split(":")[2])
                if x["desc"].split(":")[0] in ("HGT", "OROG", "ORO", "HSURF", "ELEV", "DIST") and \
                        "surface" == x["desc"].split(":")[1]:
                    terrain.add(x["desc"].split(":")[0])
    for ch, w in sorted(tmax.items()):
        prow("nbm", "maximum field", f"TMAX windows, {ch:02d}z run (2025-03-01)", "; ".join(w),
             "window = the hours after the cycle; in UTC: cycle + start to cycle + end")
    prow("nbm", "orography", "terrain field in core .co idx (HGT/OROG/ELEV:surface)",
         sorted(terrain) or "absent", "every lead 3 to 48 of four cycles checked")
    root = s82.s3list(NBM, "")[0]
    prow("nbm", "orography", "bucket top-level prefixes", " ".join(root), "a static terrain file would be listed here")
    # decode TMP 2 m and TMAX metadata; positions; CYYZ inside the grid
    L = idx_parse(get(NBM + nbm_file(cyc0, 24) + ".idx").text)
    for want in ["TMP:2 m above ground:24 hour fcst:", "TMAX:2 m above ground:12-24 hour max fcst:"]:
        j = [i for i, x in enumerate(L) if x["desc"] == want]
        if len(j) != 1:
            prow("nbm", "message", want, f"{len(j)} idx lines")
            continue
        i = j[0]
        off, end = L[i]["off"], L[i + 1]["off"] - 1
        gid, m, b = fetch_message(NBM + nbm_file(cyc0, 24), off, end - off + 1, cyc0 + dt.timedelta(hours=24),
                                  cyc0 + dt.timedelta(hours=24) if "TMAX" in want else None)
        prow("nbm", "message", want, f"name '{m['name']}', units {m['units']}, stepType {m['stepType']}, "
             f"stepRange {m['stepRange']}, {len(b)} B", grid_signature(m))
        if want.startswith("TMP"):
            outside = []
            lab, pos = ensure_positions("nbm", gid, m, A, US4 + ["CYYZ"], note=outside)
            prow("nbm", "grid", lab, grid_signature(m), f"positions_{lab}.csv, {len(pos)} boxes")
            vals = ec.codes_get_values(gid)
            miss = ec.codes_get_double(gid, "missingValue")
            rows_p = read_positions_rows(lab)
            for icao, setname, why in outside:
                prow("nbm", "inside CONUS grid", f"{icao}|{setname}", "no", why)
            for r in rows_p:
                idx = pos[(r["airport"], r["position_set"])]
                ok = all(math.isfinite(vals[k]) and vals[k] != miss for k in idx)
                prow("nbm", "inside CONUS grid", f"{r['airport']}|{r['position_set']}",
                     f"yes; four points with values: {ok}",
                     f"nearest {min(float(r[f'p{k}_distance_km']) for k in range(1, 5)):.3f} km")
            # alternate row scanning: smoothness as decoded and with odd rows
            # reversed (a ratio only; no value is printed)
            ny, nx = ec.codes_get(gid, "Ny"), ec.codes_get(gid, "Nx")
            a2 = vals.reshape(ny, nx)
            alt = a2.copy()
            alt[1::2] = alt[1::2, ::-1]
            r_dec = float(np.mean(np.abs(np.diff(a2, axis=0))))
            r_alt = float(np.mean(np.abs(np.diff(alt, axis=0))))
            prow("nbm", "row order", "alternativeRowScanning", ec.codes_get(gid, "alternativeRowScanning"),
                 f"mean row-to-row change as decoded is {r_dec / r_alt:.1f} times that with odd rows reversed; "
                 "eccodes' latitudes/longitudes are not reversed, so values on odd rows are mapped "
                 "by j*Nx + (Nx-1-i)")
            # what codes_grib_find_nearest returns (as sessions 85 and 87 used it), at
            # F127.3's three stations: which array position its value equals
            for icao in ("KDSM", "KRNO", "KSFO"):
                la, lo = A[icao]["sets"]["iem"]
                nn = ec.codes_grib_find_nearest(gid, la, lo)[0]
                j, i = divmod(int(nn.index), nx)
                mapped = j * nx + (nx - 1 - i) if j % 2 else int(nn.index)
                prow("nbm", "row order", f"codes_grib_find_nearest at {icao} (IEM position)",
                     f"node row {j} ({'odd' if j % 2 else 'even'}); its value equals the value at the "
                     f"geography index: {nn.value == vals[int(nn.index)]}; equals the row-mapped "
                     f"value: {nn.value == vals[mapped]}",
                     "report only: sessions 85 and 87 read NBM through codes_grib_find_nearest (F127.3)")
        ec.codes_release(gid)

    # ---- MOS (MAV, NBS): structure on one spent day; coverage is counted in the pull
    say("-- MOS (IEM archive; time fields and column names only)")
    for model, stations in [("GFS", US4), ("NBS", US4 + ["CYYZ"])]:
        for st in stations:
            rows = []
            for day in ("2025-03-01", "2026-07-15"):
                try:
                    r = get(f"{IEM}/cgi-bin/request/mos.py", iem=True, tries=4,
                            params=dict(station=st, model=model, sts=f"{day}T00:00Z",
                                        ets=f"{day}T23:59Z", format="csv"))
                    rows += [x for x in csv.DictReader(io.StringIO(r.text))
                             if dt.datetime.strptime(x["ftime"][:16], "%Y-%m-%d %H:%M") <= LIMIT]
                except Missing as e:
                    prow("mos", model, f"{st} {day}", f"missing {e}")
            rts = sorted({x["runtime"] for x in rows})
            proj = {}
            for x in rows:
                rt = dt.datetime.strptime(x["runtime"][:16], "%Y-%m-%d %H:%M")
                ft = dt.datetime.strptime(x["ftime"][:16], "%Y-%m-%d %H:%M")
                lead = int((ft - rt).total_seconds() // 3600)
                proj.setdefault(rt.hour, []).append(lead)
            col = "n_x" if model == "GFS" else "txn"
            mx_hours = sorted({x["ftime"][11:13] for x in rows if x.get(col) not in (None, "")})
            prow("mos", model, st, f"runs {[x[:13] for x in rts]}; rows {len(rows)}",
                 f"leads per run {[(h, min(v), max(v), len(v)) for h, v in sorted(proj.items())]}; "
                 f"{col} at ftime hours {mx_hours}; columns {list(rows[0].keys()) if rows else []}; "
                 f"leadlist {json.dumps({h: sorted(set(v)) for h, v in sorted(proj.items())})}")
            rows = None
    for u in ["https://vlab.noaa.gov/web/mdl/mav-card",
              "https://vlab.noaa.gov/web/mdl/weather-elements",
              "https://vlab.noaa.gov/web/mdl/nbm-textcard-v5.0"]:
        try:
            t = get(u, tries=2).text
            t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", t)
            t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
            hits = [t[max(0, m.start() - 160): m.start() + 260] for m in
                    re.finditer(r"(N/X = |\(7 a\.m\. - 7 p\.m\. LST\) maximum|TXN = |generated from 0000)", t)][:3]
            prow("mos", "documentation", u, "read", " || ".join(hits)[:900])
        except Exception as e:  # noqa: BLE001
            prow("mos", "documentation", u, "not read", str(e)[:120])
    for pil, cccc in [("MAVDSM", None), ("NBSUSA", None)]:
        try:
            p = dict(pil=pil, date="2025-03-01")
            j = get(f"{IEM}/api/1/nws/afos/list.json", params=p, iem=True).json()
            prow("mos", "AFOS product list", f"{pil} 2025-03-01", f"{len(j.get('data', []))} products",
                 str([(x.get("entered"), x.get("product_id")) for x in j.get("data", [])][:4]))
        except Exception as e:  # noqa: BLE001
            prow("mos", "AFOS product list", pil, "error", str(e)[:120])

    # ---- the official maximum: identity and day counts
    say("-- official maximum (identity, day counts; no value read)")
    ghc = TMP / "ghcnd-stations.txt"
    if not ghc.exists():
        ghc.write_bytes(get(GHCND_STATIONS).content)
    stations = []
    for ln in ghc.read_text(errors="replace").splitlines():
        try:
            stations.append((ln[0:11], float(ln[12:20]), float(ln[21:30]), ln[41:71].strip()))
        except ValueError:
            continue
    for icao in US4:
        meta = [x for x in get(f"{IEM}/api/1/station/{icao}.json", iem=True).json().get("data", [])
                if x.get("network") == "NWSCLI"]
        if len(meta) != 1:
            prow("official", "CLI identity", icao, f"{len(meta)} NWSCLI rows")
            continue
        m = meta[0]
        d_iem = haversine_km(m["latitude"], m["longitude"], A[icao]["iem_lat"], A[icao]["iem_lon"])
        prow("official", "CLI identity", icao, f"{m['name']}; {m['latitude']}, {m['longitude']}; "
             f"elevation {m['elevation']} m; tz {m['tzname']}",
             f"{d_iem:.2f} km from the airport's IEM position; tz equals the airport's: {m['tzname'] == A[icao]['tz']}")
        near = sorted((haversine_km(m["latitude"], m["longitude"], la, lo), sid, name, la, lo)
                      for sid, la, lo, name in stations
                      if abs(la - m["latitude"]) < 0.2 and abs(lo - m["longitude"]) < 0.2)
        usw = [x for x in near if x[1].startswith("USW")]
        prow("official", "GHCN-Daily candidates", icao,
             "; ".join(f"{sid} {name} {dk:.2f} km" for dk, sid, name, _, _ in near[:4]))
        if usw and usw[0][0] <= 5.0:
            prow("official", "GHCN-Daily station", icao, usw[0][1],
                 f"{usw[0][2]}; {usw[0][0]:.2f} km from the CLI position (nearest USW station within 5 km)")
            A[icao]["ghcn"] = usw[0][1]
        else:
            prow("official", "GHCN-Daily station", icao, "none within 5 km")
    for icao in US4:
        first = (DEV_FIRST if icao in DEV else CLAIM_FIRST).date()
        cnt, dropped = {}, 0
        for yr in range(first.year, 2027):
            j = get(f"{IEM}/json/cli.py", params=dict(station=icao, year=yr, fmt="json"), iem=True).json()
            kept, after, before = cli_keep(j.get("results", []), A[icao]["tz"], first)
            j = None
            dropped += after
            for rec in kept:
                day = dt.date.fromisoformat(str(rec["valid"])[:10])
                ty = test_year(dt.datetime(day.year, day.month, day.day))
                c = cnt.setdefault(ty, [0, 0])
                c[0] += 1
                c[1] += rec.get("high") not in (None, "", "M")
        for ty, (a, b) in sorted(cnt.items()):
            prow("official", "CLI days", f"{icao}|{ty}", f"records {a}; with a maximum {b}")
        prow("official", "CLI days", f"{icao}|dropped unread after the limit", dropped,
             "owner's ruling: filtered on the date field alone, in memory")
        if A[icao].get("ghcn"):
            last = dt.date(2026, 7, 30)
            guard_climate_day(last, A[icao]["tz"])
            r = get(NCEI_DATA, params=dict(dataset="daily-summaries", stations=A[icao]["ghcn"],
                                           startDate=first.isoformat(), endDate=last.isoformat(),
                                           dataTypes="TMAX", format="json", units="metric"))
            rows = r.json()
            cnt = {}
            for x in rows:
                day = dt.date.fromisoformat(x["DATE"][:10])
                if day > last:
                    raise SystemExit("STOP: NCEI returned a day after the requested end")
                ty = test_year(dt.datetime(day.year, day.month, day.day))
                cnt[ty] = cnt.get(ty, 0) + (x.get("TMAX") not in (None, ""))
            for ty, n in sorted(cnt.items()):
                prow("official", "GHCN-Daily TMAX days", f"{icao}|{ty}", n)
            rows = None
    # ---- version documentation
    say("-- version documentation")
    for u, pat in [("https://www.ecmwf.int/en/forecasts/documentation-and-support/changes-ecmwf-model",
                    r"(?i)(cycle 4[89]r1|cycle 50r1|AIFS)"),
                   ("https://vlab.noaa.gov/web/mdl/nbm-versions", r"(?i)(v4\.[123]|v5\.0)"),
                   ("https://vlab.noaa.gov/web/mdl/nbm-data-availability-v5.0", r"(?i)(v4\.[123]|v5\.0|July 28)")]:
        try:
            t = get(u, tries=2).text
            t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", t)
            t = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))
            hits = [t[max(0, m.start() - 120): m.start() + 200] for m in re.finditer(pat, t)][:6]
            prow("versions", "documentation", u, "read", " || ".join(hits)[:1500])
        except Exception as e:  # noqa: BLE001
            prow("versions", "documentation", u, "not read", str(e)[:120])
    prow("versions", "record", "NBM", "v4.1 before 2024-05-15 (listing, F123.3: v4.2 2024-05-15); "
         "v4.3 2025-05-27 12z (D77.7); v5.0 2026-04-30 13z (F127.7 correction); v5.0.14 2026-07-28 12z (F127.7)",
         "record entries, planning-chat web searches; v4.1's start is before the window")
    prow("versions", "record", "IFS", "48r1 2023-06-27; 49r1 about Oct 2024; 50r1 with AIFS v2 2026-05-12 (F123.3, documentation)")

    path = OUT / "probe.csv"
    if path.exists():
        path.unlink()           # the probe's own file, rewritten whole on a rerun
    write_csv(path, ["source", "topic", "key", "value", "note"], PROBE_ROWS)
    say(f"== --probe: {len(PROBE_ROWS)} rows written to {path.relative_to(ROOT)}; "
        f"requests {REQUESTS['n']}, {REQUESTS['bytes'] / 1e6:.1f} MB")
    return True


# ------------------------------------------------------------------ gridded sources

VAL_COLS = ["airport", "position_set", "grid", "cycle", "step", "valid_utc", "param",
            "window_start_utc", "window_end_utc", "v1", "v2", "v3", "v4", "units", "msg"]
MAN_COLS = ["msg", "source", "grid", "cycle", "step", "param", "url", "byte_range", "index_line",
            "bytes", "sha256", "pulled_utc"]
GAP_COLS = ["source", "cycle", "step", "param", "reason", "detail"]


def probe_value(source, topic, key):
    with open(OUT / "probe.csv", newline="") as f:
        for r in csv.DictReader(f):
            if (r["source"], r["topic"], r["key"]) == (source, topic, key):
                return r["value"]
    raise SystemExit(f"STOP: probe.csv has no row {source}|{topic}|{key}")


class Source:
    """What differs between the gridded sources. `units(cyc)` yields the
    (cycle, step) work units; `messages(cyc, step, index_text)` the wanted
    messages of one file as dicts (param, off, length, line, window)."""

    def __init__(self, name):
        self.name = name
        A = load_airports()
        self.A = A
        if name == "ifs":
            self.airports = ALL12
            self.first = {a: A[a]["first_cycle"] for a in ALL12}
            self.steps = IFS_STEPS
            self.listing = read_csv_gz(OUT / "listing_ifs.csv.gz")

        elif name == "aifs":
            self.airports = ALL12
            fo = dt.datetime.strptime(probe_value("aifs", "first operational run",
                                                  "first cycle with files under aifs-single/0p25/oper/"),
                                      "%Y-%m-%dT%H:%MZ")
            self.first = {a: max(A[a]["first_cycle"], fo) for a in ALL12}
            self.steps = AIFS_STEPS
            self.listing = read_csv_gz(OUT / "listing_aifs.csv.gz")
        elif name == "nbm":
            inside = []
            with open(OUT / "probe.csv", newline="") as f:
                for r in csv.DictReader(f):
                    if r["topic"] == "inside CONUS grid" and r["value"].startswith("yes; four points with values: True"):
                        inside.append(tuple(r["key"].split("|")))
            self.airports = [a for a in US4 + ["CYYZ"] if any(x[0] == a for x in inside)]
            self.sets = [x for x in inside]
            self.first = {a: A[a]["first_cycle"] for a in self.airports}
            self.listing = read_csv_gz(OUT / "listing_nbm48.csv.gz")
            h = probe_value("nbm", "hourly to 48 h", "f037 first present (00z, bisection)")
            d = h.split("first present ")[1]
            self.h48 = dt.datetime.fromisoformat(d) if d != "None" else None
        else:
            raise ValueError(name)
        if name != "nbm":
            self.sets = [(a, s) for a in self.airports for s in A[a]["sets"]]
        self.lst = {r["cycle"]: r for r in self.listing}

    def res_of(self, cyc):
        """The resolution a cycle's grid must have."""
        if self.name == "ifs":
            return ifs_grid_label(cyc)
        return "0p25" if self.name == "aifs" else "lambert"

    def nominal(self, cyc):
        if self.name == "nbm":
            return nbm_nominal(cyc, self.h48)
        return self.steps

    def cycles(self):
        f0 = min(self.first.values())
        return [c for c in cycles(f0)]

    def file_url(self, cyc, step):
        if self.name == "nbm":
            return NBM + nbm_file(cyc, step)
        r = self.lst.get(iso(cyc))
        folder = r["folder"] if r and r["folder"] else None
        return ECMWF + ecmwf_file("ifs" if self.name == "ifs" else "aifs-single", cyc, step, folder) + ".grib2"

    def index_url(self, cyc, step):
        u = self.file_url(cyc, step)
        return u + ".idx" if self.name == "nbm" else u[:-len(".grib2")] + ".index"

    def listed(self, cyc, step):
        r = self.lst.get(iso(cyc))
        if r is None:
            return False
        if self.name == "nbm":
            return "48" in r["grib_steps"].split()       # f048 listed: the cycle exists
        return str(step) in r["grib_steps"].split() and str(step) in r["index_steps"].split()

    def messages(self, cyc, step, text):
        """The wanted messages in one file: 2 m temperature and the maximum
        field. Each: dict(param, off, length, line, wstart, wend)."""
        valid = cyc + dt.timedelta(hours=step)
        out = []
        if self.name in ("ifs", "aifs"):
            L = [json.loads(x) for x in text.splitlines() if x.strip().startswith("{")]
            want = ["2t"] + (["mx2t3"] if self.name == "ifs" else [])
            for p in want:
                m = [x for x in L if x["param"] == p and x.get("levtype") == "sfc"]
                if len(m) != 1:
                    out.append(dict(param=p, missing=f"{len(m)} index lines"))
                    continue
                x = m[0]
                if x["date"] != f"{cyc:%Y%m%d}" or x["time"] != f"{cyc:%H}00" or int(x["step"]) != step:
                    out.append(dict(param=p, missing=f"index line date/time/step {x['date']} {x['time']} {x['step']}"))
                    continue
                if p == "mx2t3" and x["_length"] < 1000:
                    out.append(dict(param=p, missing=f"empty message ({x['_length']} B)"))
                    continue
                line = json.dumps({k: v for k, v in x.items()}, sort_keys=True)
                ws = valid - dt.timedelta(hours=3) if p == "mx2t3" else None
                out.append(dict(param=p, off=x["_offset"], length=x["_length"], line=line,
                                wstart=ws, wend=valid if p == "mx2t3" else None))
            return out
        L = idx_parse(text)
        for i, x in enumerate(L):
            p = None
            if x["desc"] == f"TMP:2 m above ground:{step} hour fcst:":
                p = "TMP"
            elif re.fullmatch(r"TMAX:2 m above ground:\d+-\d+ hour max fcst:", x["desc"]):
                p = "TMAX"
            if p is None:
                continue
            if x["d"] != f"d={cyc:%Y%m%d%H}":
                out.append(dict(param=p, missing=f"idx date {x['d']}"))
                continue
            if i + 1 >= len(L):
                out.append(dict(param=p, missing="last idx line (length unknown)"))
                continue
            ws = we = None
            if p == "TMAX":
                a, b = map(int, x["desc"].split(":")[2].split(" ")[0].split("-"))
                ws, we = cyc + dt.timedelta(hours=a), cyc + dt.timedelta(hours=b)
                if b != step:
                    out.append(dict(param=p, missing=f"window end {b} is not the step"))
                    continue
            out.append(dict(param=p, off=x["off"], length=L[i + 1]["off"] - x["off"], line=x["line"],
                            wstart=ws, wend=we))
        if not any(m["param"] == "TMP" for m in out):
            out.append(dict(param="TMP", missing="no idx line"))
        return out


def check_message(src, m, cyc, step, want):
    """Identity checks before any value is read (SPEC 8.7 item 3)."""
    errs = []
    if msg_run(m) != cyc:
        errs.append(f"run {msg_run(m)}")
    if msg_valid(m) != cyc + dt.timedelta(hours=step):
        errs.append(f"valid {msg_valid(m)}")
    sn = {"2t": "2t", "mx2t3": "mx2t3", "TMP": "2t", "TMAX": "tmax"}[want["param"]]
    if want["param"] == "TMAX":
        if m["stepType"] != "max":
            errs.append(f"stepType {m['stepType']}")
    elif m["shortName"] != sn:
        errs.append(f"shortName {m['shortName']}")
    if m["units"] != "K":
        errs.append(f"units {m['units']}")
    if grid_res(m) != src.res_of(cyc):
        errs.append(f"grid {grid_res(m)} is not the expected {src.res_of(cyc)}")
    return errs


def do_unit(src, cyc, step):
    """One file: its index, then each wanted message. Returns (vals, man, gaps).
    A fetch failure after 3 tries raises (the chunk fails)."""
    vals, man, gaps = [], [], []
    valid = cyc + dt.timedelta(hours=step)
    guard_valid(valid)
    need = [(a, s) for (a, s) in src.sets if cyc >= src.first[a]]
    if not src.listed(cyc, step):
        gaps.append([src.name, iso(cyc), step, "*", "not listed", ""])
        return vals, man, gaps
    try:
        text = get(src.index_url(cyc, step)).text
    except Missing as e:
        gaps.append([src.name, iso(cyc), step, "*", "no index", str(e)])
        return vals, man, gaps
    for w in src.messages(cyc, step, text):
        if "missing" in w:
            gaps.append([src.name, iso(cyc), step, w["param"], "no message", w["missing"]])
            continue
        if w["wend"] is not None:
            guard_window_end(w["wend"])
        url = src.file_url(cyc, step)
        pulled = now_utc()
        try:
            gid, m, b = fetch_message(url, w["off"], w["length"], valid, w["wend"])
        except Missing as e:
            gaps.append([src.name, iso(cyc), step, w["param"], "no file", str(e)])
            continue
        except IndexMismatch as e:
            gaps.append([src.name, iso(cyc), step, w["param"], "index offset does not match the file", str(e)])
            continue
        try:
            errs = check_message(src, m, cyc, step, w)
            if not errs:
                grid, pos = ensure_positions(src.name, gid, m, src.A, src.airports)
                if any(x not in pos for x in need):
                    errs.append(f"positions missing on grid {grid}")
            if errs:
                gaps.append([src.name, iso(cyc), step, w["param"], "failed check", "; ".join(errs)])
                continue
            v = ec.codes_get_values(gid)
            missing = m["missingValue"] if "missingValue" in m else ec.codes_get_double(gid, "missingValue")
            digest = sha256_bytes(b)
            mid = digest[:16]
            man.append([mid, src.name, grid, iso(cyc), step, w["param"], url,
                        f"{w['off']}-{w['off'] + w['length'] - 1}", w["line"], len(b), digest, pulled])
            for a, s in need:
                idx = pos[(a, s)]
                pts = [float(v[k]) for k in idx]
                if any((not math.isfinite(x)) or x == missing for x in pts):
                    gaps.append([src.name, iso(cyc), step, w["param"], "missing value", f"{a} {s}"])
                    continue
                vals.append([a, s, grid, iso(cyc), step, iso(valid), w["param"],
                             iso(w["wstart"]) if w["wstart"] else "", iso(w["wend"]) if w["wend"] else "",
                             repr(pts[0]), repr(pts[1]), repr(pts[2]), repr(pts[3]), m["units"], mid])
        finally:
            ec.codes_release(gid)
    return vals, man, gaps


def month_key(c):
    return f"{c:%Y-%m}"


def run_chunk(src, month, cycs):
    d = WORK / src.name
    units = [(c, s) for c in cycs for s in leads_kept(c, src.nominal(c))]
    res = pmap(lambda u: do_unit(src, *u), units)
    vals = [r for v, _, _ in res for r in v]
    man = [r for _, m, _ in res for r in m]
    gaps = [r for _, _, g in res for r in g]
    for nm, cols, rows in [("values", VAL_COLS, vals), ("manifest", MAN_COLS, man), ("gaps", GAP_COLS, gaps)]:
        p = d / f"{month}.{nm}.csv.gz"
        if p.exists():
            p.unlink()          # a partial file from a failed attempt
        write_csv_gz(p, cols, rows)
    (d / f"{month}.done").write_text(f"{now_utc()} units {len(units)} values {len(vals)} "
                                     f"messages {len(man)} gaps {len(gaps)}\n")
    return len(units), len(vals), len(man), len(gaps)


def pull_gridded(name):
    src = Source(name)
    d = WORK / name
    d.mkdir(parents=True, exist_ok=True)
    cy = src.cycles()
    months = {}
    for c in cy:
        months.setdefault(month_key(c), []).append(c)
    say(f"== --pull {name}: {len(cy)} cycles in {len(months)} monthly chunks; airports {src.airports}")
    failed = []
    t0 = time.time()
    for mk, cs in sorted(months.items()):
        if (d / f"{mk}.done").exists():
            continue
        for attempt in range(1, 4):
            try:
                t1 = time.time()
                n = run_chunk(src, mk, cs)
                say(f"  {mk}: units {n[0]}, value rows {n[1]}, messages {n[2]}, gaps {n[3]}; "
                    f"{time.time() - t1:.0f} s; requests so far {REQUESTS['n']}, "
                    f"{REQUESTS['bytes'] / 1e9:.2f} GB; elapsed {(time.time() - t0) / 3600:.2f} h")
                break
            except GuardError:
                raise
            except Exception as e:  # noqa: BLE001 - recorded, retried, then the pull goes on
                say(f"  {mk}: attempt {attempt} failed: {str(e)[:200]}")
                if attempt == 3:
                    failed.append(mk)
                    with open(d / "failed.txt", "a") as f:
                        f.write(f"{now_utc()} {mk} {str(e)[:300]}\n")
                else:
                    time.sleep(300)     # let the archive's throttling ease before the retry
    done = sorted(p.name.split(".")[0] for p in d.glob("*.done"))
    say(f"  chunks done {len(done)} of {len(months)}; failed this run {failed}")
    return src, months, failed


def iter_csv_gz(path):
    with gzip.open(path, "rt", newline="") as f:
        yield from csv.DictReader(f)


def finish_gridded(name):
    """Merge the chunks into per-airport files, run the checks, write the meta
    file, delete the work folder. Runs only when every chunk is done. Streams
    the chunk files (the value rows do not fit comfortably in memory)."""
    src = Source(name)
    d = WORK / name
    cy = src.cycles()
    months = sorted({month_key(c) for c in cy})
    missing = [m for m in months if not (d / f"{m}.done").exists()]
    if missing:
        say(f"  STOP: chunks not done: {missing}")
        return False
    man, gaps = [], []
    for m in months:
        man += read_csv_gz(d / f"{m}.manifest.csv.gz")
        gaps += read_csv_gz(d / f"{m}.gaps.csv.gz")
    rng = random.Random(113)
    sample = rng.sample(man, min(20, len(man)))
    sample_ids = {r["msg"] for r in sample}
    by_msg = {}
    main_param = "TMP" if name == "nbm" else "2t"
    got, n_vals, n_out, lv, lw = {}, 0, 0, "", ""
    tmp_files = {a: (OUT / f"{name}_{a}.csv.gz.partial") for a in src.airports}
    for p in tmp_files.values():
        if p.exists():
            p.unlink()
    writers = {}
    raw = {}
    for a, p in tmp_files.items():
        raw[a] = open(p, "xb")
        gz = gzip.GzipFile(fileobj=raw[a], mode="wb", mtime=0, filename="")
        tw = io.TextIOWrapper(gz, newline="")
        w = csv.writer(tw, lineterminator="\n")
        w.writerow(VAL_COLS)
        writers[a] = (w, tw)
    counts = {a: 0 for a in src.airports}
    for m in months:
        for r in iter_csv_gz(d / f"{m}.values.csv.gz"):
            n_vals += 1
            writers[r["airport"]][0].writerow([r[c] for c in VAL_COLS])
            counts[r["airport"]] += 1
            if r["param"] == main_param:
                k = (r["airport"], r["position_set"], int(r["cycle"][11:13]))
                got[k] = got.get(k, 0) + 1
            lv = max(lv, r["valid_utc"])
            if r["window_end_utc"]:
                lw = max(lw, r["window_end_utc"])
            for k in ("v1", "v2", "v3", "v4"):
                if not (-70.0 <= float(r[k]) - 273.15 <= 60.0):
                    n_out += 1
            if r["msg"] in sample_ids:
                by_msg.setdefault(r["msg"], []).append(r)
    for a, (w, tw) in writers.items():
        tw.close()
        raw[a].close()
    say(f"  merged: value rows {n_vals}, messages {len(man)}, gaps {len(gaps)}")
    ok = True
    exp = {}
    gap_units = {}
    for g in gaps:
        gap_units.setdefault((g["cycle"], int(g["step"])), set()).add(g["param"])
    for a in src.airports:
        for s_ in list(src.A[a]["sets"]):
            if (a, s_) not in src.sets:
                continue
            for c in cycles(src.first[a]):
                for st in leads_kept(c, src.nominal(c)):
                    k = (a, s_, c.hour)
                    exp[k] = exp.get(k, 0) + (0 if gap_units.get((iso(c), st), set()) & {"*", main_param} else 1)
    miss_val = {}
    for g in gaps:
        if g["reason"] == "missing value" and g["param"] == main_param:
            a, s_ = g["detail"].split()
            k = (a, s_, int(g["cycle"][11:13]))
            miss_val[k] = miss_val.get(k, 0) + 1
    bad = [(k, exp[k], miss_val.get(k, 0), got.get(k, 0)) for k in exp
           if exp[k] - miss_val.get(k, 0) != got.get(k, 0)]
    say(f"  check rows ({main_param}) per airport, set and cycle hour = expected minus gaps: "
        f"{len(exp) - len(bad)} of {len(exp)} cells equal")
    for b in bad[:10]:
        say(f"    differs (cell, expected, missing values, got): {b}")
    ok &= not bad
    lim_ok = lv <= iso(LIMIT) and (lw == "" or lw <= iso(LIMIT))
    say(f"  check latest valid {lv}, latest maximum window end {lw or 'none'}: on or before {iso(LIMIT)}: {lim_ok}")
    ok &= lim_ok
    n_all = 4 * n_vals
    frac = n_out / n_all if n_all else 0
    say(f"  check values outside -70 to 60 C: {n_out} of {n_all} ({100 * frac:.4f} %; stop above 0.1 %)")
    ok &= frac <= 0.001
    n_same = 0
    for mrow in sample:
        cyc = dt.datetime.strptime(mrow["cycle"], "%Y-%m-%dT%H:%MZ")
        st = int(mrow["step"])
        a0, a1 = map(int, mrow["byte_range"].split("-"))
        rws = by_msg.get(mrow["msg"], [])
        wend = rws[0]["window_end_utc"] if rws else ""
        we = dt.datetime.strptime(wend, "%Y-%m-%dT%H:%MZ") if wend else None
        gid, m, b = fetch_message(mrow["url"], a0, a1 - a0 + 1, cyc + dt.timedelta(hours=st), we)
        try:
            v = ec.codes_get_values(gid)
            _, pos = ensure_positions(src.name, gid, m, src.A, src.airports)
            same = bool(rws) and all(r["grid"] == mrow["grid"] for r in rws) and \
                sha256_bytes(b) == mrow["sha256"] and all(
                [repr(float(v[k])) for k in pos[(r["airport"], r["position_set"])]] ==
                [r["v1"], r["v2"], r["v3"], r["v4"]] for r in rws)
            n_same += same
        finally:
            ec.codes_release(gid)
    say(f"  check 20 random messages re-fetched and re-decoded: {n_same} of {len(sample)} identical")
    ok &= n_same == len(sample)
    if not ok:
        for p in tmp_files.values():
            p.unlink()
        say("  STOP: a check failed; the merged files were removed; the chunks are kept")
        return False
    files = []
    for a, p in tmp_files.items():
        final = OUT / f"{name}_{a}.csv.gz"
        if final.exists():
            raise SystemExit(f"STOP: {final.name} exists")
        p.rename(final)
        files.append((final, counts[a]))
    p = write_csv_gz(OUT / f"{name}_manifest.csv.gz", MAN_COLS, [[r[c] for c in MAN_COLS] for r in man])
    files.append((p, len(man)))
    p = write_csv(OUT / f"{name}_gaps.csv", GAP_COLS, [[r[c] for c in GAP_COLS] for r in gaps])
    files.append((p, len(gaps)))
    big = [p.name for p, _ in files if p.stat().st_size > 50e6]
    if big:
        say(f"  STOP: files over 50 MB: {big}")
        return False
    gap_count = {}
    for g in gaps:
        gap_count[(g["param"], g["reason"])] = gap_count.get((g["param"], g["reason"]), 0) + 1
    pulled = sorted(r["pulled_utc"] for r in man)
    terrain = OUT / f"{name}_terrain.csv"
    lines = ["Provenance (SPEC 2.3, D47, D107.6). Do not edit the data files.", "",
             f"source      : {name}", f"written by  : scripts/session113_comparison_pull.py --pull {name}",
             f"written at  : {now_utc()}",
             f"pulled      : {pulled[0]} to {pulled[-1]}" if pulled else "pulled      : nothing",
             f"airports    : {' '.join(src.airports)}",
             "windows     : " + "; ".join(f"{a} {iso(src.first[a])} to {iso(LAST_CYCLE)}" for a in src.airports),
             f"columns     : {', '.join(VAL_COLS)}",
             "values      : v1..v4 at the four points of positions_<source>_<grid>.csv (same order), "
             "full precision, in the message's own units (K); window_* only for maximum fields",
             f"rows        : value rows {n_vals}; messages {len(man)}; gaps {len(gaps)}",
             "gaps        : " + ("; ".join(f"{p_} {r_} {n_}" for (p_, r_), n_ in sorted(gap_count.items())) or "none"),
             f"terrain     : {terrain.name if terrain.exists() else 'absent (no orography field in the source)'}",
             f"packages    : python {sys.version.split()[0]}; eccodes {ec.__version__}; numpy {np.__version__}; "
             f"requests {requests.__version__}",
             "versions    : " + VERSION_NOTE.get(name, ""),
             f"requests    : at most {WORKERS[0]} at once" + (f"; owner's override: {OVERRIDE[0]}" if OVERRIDE[0] else ""),
             "", "files (SHA-256, rows):"]
    for p, n in files + ([(terrain, "")] if terrain.exists() else []):
        lines.append(f"  {p.name}  {sha256_file(p)}  {n}")
    (OUT / f"{name}_meta.txt").write_text("\n".join(lines) + "\n")
    shutil.rmtree(d)
    say(f"  merged files written; work folder {d.relative_to(ROOT)} deleted")
    return True


VERSION_NOTE = {
    "ifs": "0.4 degree to 2024-01-31 (grid 0p4), 0.25 degree from 2024-02-01; IFS cycles per probe.csv "
           "(48r1 from 2023-06-27, 49r1, 50r1 with dates as documented there)",
    "aifs": "AIFS Single from its first operational run (probe.csv); versions per probe.csv",
    "nbm": "NBM v4.1, v4.2 (2024-05-15), v4.3 (2025-05-27 12z), v5.0 (2026-04-30 13z), v5.0.14 (2026-07-28 12z) "
           "(D77.7 with F127.7's corrections)",
}


# ------------------------------------------------------------------ terrain heights (once per grid)

def pull_terrain(name):
    """Surface geopotential (z, step 0) at each position's four points, once
    per grid of the pulled 2 m temperature messages: from the first 00z run
    on or after the grid's first cycle (and after the probe's first-present
    date) whose step-0 file carries z on the same grid; also decoded at the
    grid's last such run to see whether it changed. Absent if none."""
    src = Source(name)
    model = "ifs" if name == "ifs" else "aifs-single"
    d = WORK / name
    span = {}
    for mf in sorted(d.glob("*.manifest.csv.gz")):
        for r in iter_csv_gz(mf):
            if r["param"] == "2t":
                a, b = span.get(r["grid"], (r["cycle"], r["cycle"]))
                span[r["grid"]] = (min(a, r["cycle"]), max(b, r["cycle"]))
    zfirst = None
    if name == "ifs":
        v = probe_value("ifs", "field first present", "z|step 0|00z")
        zfirst = dt.date.fromisoformat(v.split("first present ")[1]) if "None" not in v.split("first present ")[1] else None
    rows = []
    for label, (c0s, c1s) in sorted(span.items()):
        c0 = dt.datetime.strptime(c0s, "%Y-%m-%dT%H:%MZ").date()
        c1 = dt.datetime.strptime(c1s, "%Y-%m-%dT%H:%MZ").date()
        if zfirst:
            c0 = max(c0, zfirst)
        found = []
        for days in (range((c1 - c0).days + 1), range((c1 - c0).days, -1, -1)):
            for k in days:
                day = c0 + dt.timedelta(days=k)
                cyc = dt.datetime(day.year, day.month, day.day, 0)
                try:
                    path, L = ecmwf_index_any(model, cyc, 0)
                except Missing:
                    continue
                m = [x for x in L if x["param"] == "z" and x.get("levtype") == "sfc"]
                if len(m) != 1:
                    continue
                gid, meta, b = fetch_message(ECMWF + path + ".grib2", m[0]["_offset"], m[0]["_length"], cyc)
                try:
                    if grid_label(name, meta) != label:
                        continue
                    _, pos = ensure_positions(name, gid, meta, src.A, src.airports)
                    v = ec.codes_get_values(gid)
                    found.append((cyc, {key: [float(v[i]) for i in idx] for key, idx in pos.items()},
                                  f"{ECMWF}{path}.grib2 {m[0]['_offset']}-{m[0]['_offset'] + m[0]['_length'] - 1} "
                                  f"sha256 {sha256_bytes(b)}"))
                finally:
                    ec.codes_release(gid)
                break
            if not found:
                break
        if not found:
            say(f"  terrain {name} {label}: no surface z at step 0 on this grid ({c0s} to {c1s}): absent")
            rows.append([label, "", "", "", "", "", "", "", f"absent: no z (surface) on this grid, {c0s} to {c1s}", ""])
            continue
        (cz, z0, src0) = found[0]
        same = len(found) > 1 and found[1][1] == z0
        say(f"  terrain {name} {label}: from {iso(cz)}; equal at {iso(found[-1][0])}: {same}")
        for (a, s_), zz in sorted(z0.items()):
            rows.append([label, a, s_, iso(cz)] + [repr(x / 9.80665) for x in zz] +
                        [f"z / 9.80665 m; equal at {iso(found[-1][0])}: {same}", src0])
    p = OUT / f"{name}_terrain.csv"
    if p.exists():
        p.unlink()
    write_csv(p, ["grid", "airport", "position_set", "cycle", "h1_m", "h2_m", "h3_m", "h4_m", "note", "source"], rows)
    return rows


# ------------------------------------------------------------------ --cost

def run_cost(only=None):
    w = WORKERS[0]
    say(f"== --cost (D107.7): throughput on spent-date messages, {w} at once ==")
    rows = []
    for name in ([only] if only else ("ifs", "aifs", "nbm")):
        src = Source(name)
        cy = src.cycles()
        rng = random.Random(1130 + len(name) + (w if only else 0))
        units = []
        while len(units) < 60:
            c = rng.choice(cy)
            st = rng.choice(leads_kept(c, src.nominal(c)))
            if src.listed(c, st):
                units.append((c, st))
        req0, b0 = REQUESTS["n"], REQUESTS["bytes"]
        t0 = time.time()
        res = pmap(lambda u: do_unit(src, *u), units)
        wall = time.time() - t0
        nreq, nb = REQUESTS["n"] - req0, REQUESTS["bytes"] - b0
        nmsg = sum(len(m) for _, m, _ in res)
        total_units = sum(len(leads_kept(c, src.nominal(c))) for c in cy)
        est_req = total_units * nreq / len(units)
        est_gb = total_units * nb / len(units) / 1e9
        est_h = total_units * wall / len(units) / 3600
        passed = est_gb <= COST_GB and est_h <= COST_HOURS
        rows.append([name, len(units), nmsg, nreq, nb, f"{wall:.1f}", total_units, f"{est_req:.0f}",
                     f"{est_gb:.1f}", f"{est_h:.2f}", "PASS" if passed else "NOT PULLED (owner decides)"])
        say(f"  {name}: sample {len(units)} files, {nmsg} messages, {nreq} requests, {nb / 1e6:.1f} MB in "
            f"{wall:.1f} s -> total {total_units} files, ~{est_req:.0f} requests, {est_gb:.1f} GB, "
            f"{est_h:.2f} h: {'PASS' if passed else 'over the gate'}")
    p = OUT / ("cost.csv" if not only else f"cost_{only}_w{w}.csv")
    if p.exists():
        p.unlink()
    write_csv(p, ["source", "sample_files", "sample_messages", "sample_requests", "sample_bytes",
                  "sample_seconds", "total_files", "est_requests", "est_GB", "est_hours", "gate"], rows)
    say("  table: data/processed/session113/cost.csv (terrain fields add one message per grid)")
    return rows


# ------------------------------------------------------------------ MOS text sources (MAV, NBS)

MOS_COLS = ["airport", "mos_station", "model", "cycle", "cycle_label", "nominal_cycle", "ftime_utc",
            "lead", "lead_from_nominal", "element", "value_f", "value_c", "window_start_utc",
            "window_end_utc", "definition"]
MAX_ELEMENT = {"GFS": ("n_x", "X"), "NBS": ("txn", "TXN")}
# The maximum's window, from the documentation read by the probe (probe.csv):
MAX_DEF = {
    "GFS": "N/X daytime maximum, 7 a.m. to 7 p.m. local standard time (MDL weather elements page); "
           "value at the 00 UTC projection (MAV card: HR is the end of the period)",
    "NBS": "TXN maximum between 12Z (current day) and 06Z (next day), reported at 00Z (NBM text card v5.0; "
           "earlier versions' card not read)"}
# Run hour -> the nominal GFS cycle hour it pairs with (owner's ruling for NBS:
# 01, 07, 13 and 19 UTC runs pair with 00, 06, 12 and 18, labelled one hour later).
RUN_TO_NOMINAL = {"GFS": {0: 0, 6: 6, 12: 12, 18: 18},
                  "NBS": {0: 0, 6: 6, 12: 12, 18: 18, 1: 0, 7: 6, 13: 12, 19: 18}}


def mos_max_window(model, ftime, tzname):
    if model == "NBS":
        return ftime - dt.timedelta(hours=12), ftime + dt.timedelta(hours=6)
    # MAV: the local standard-time day before the 00 UTC projection, 7 am to 7 pm
    loc_day = (ftime + standard_offset(tzname, ftime.date()) - dt.timedelta(hours=1)).date()
    off = standard_offset(tzname, loc_day)
    s_ = dt.datetime(loc_day.year, loc_day.month, loc_day.day, 7) - off
    return s_, s_ + dt.timedelta(hours=12)


def mos_month(model, icao, first, month_start):
    """One station-month from IEM's MOS archive. Rows are filtered on their
    time fields (runtime, ftime) before any value field is read: runs not
    paired with a nominal cycle in the window, projections outside leads 3
    to 48 of the nominal cycle, and projections valid after the limit are
    dropped unread and counted."""
    nxt = (month_start.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    sts = max(month_start, first)
    ets = min(nxt - dt.timedelta(minutes=1), LAST_CYCLE + dt.timedelta(hours=1))
    params = dict(station=icao, model=model, sts=f"{sts:%Y-%m-%dT%H:%MZ}", ets=f"{ets:%Y-%m-%dT%H:%MZ}",
                  format="csv")
    pulled = now_utc()
    r = get(f"{IEM}/cgi-bin/request/mos.py", params=params, iem=True)
    rows = list(csv.DictReader(io.StringIO(r.text)))
    kept, drop = [], {"run not paired or outside the window": 0, "lead outside 3-48": 0, "after the limit": 0}
    rmap = RUN_TO_NOMINAL[model]
    for x in rows:
        rt = dt.datetime.strptime(x["runtime"][:16], "%Y-%m-%d %H:%M")
        ft = dt.datetime.strptime(x["ftime"][:16], "%Y-%m-%d %H:%M")
        if rt.minute or rt.hour not in rmap:
            drop["run not paired or outside the window"] += 1
            continue
        nom = rt - dt.timedelta(hours=rt.hour - rmap[rt.hour])
        if not (first <= nom <= LAST_CYCLE):
            drop["run not paired or outside the window"] += 1
            continue
        ln = (ft - nom).total_seconds() / 3600
        if not (LEAD_MIN <= ln <= LEAD_MAX):
            drop["lead outside 3-48"] += 1
            continue
        if ft > LIMIT:
            drop["after the limit"] += 1
            continue
        kept.append((rt, nom, ft, x))
    q = dict(url=r.url, pulled=pulled, bytes=len(r.content), sha256=sha256_bytes(r.content),
             rows=len(rows), kept=len(kept))
    return kept, drop, q


def mos_rows(model, icao, kept, tz):
    col, el = MAX_ELEMENT[model]
    out = []
    for rt, nom, ft, x in kept:
        lab = "nominal" if rt == nom else "one hour later than the nominal cycle"
        base = [icao, icao, model, iso(rt), lab, iso(nom), iso(ft), int((ft - rt).total_seconds() // 3600),
                int((ft - nom).total_seconds() // 3600)]
        t = x.get("tmp")
        if t not in (None, "", "M"):
            out.append(base + ["TMP", t, repr(f_to_c(t)), "", "", "2 m temperature at the projection hour"])
        v = x.get(col)
        if v not in (None, "", "M") and ft.hour == 0:
            ws, we = mos_max_window(model, ft, tz)
            if we > LIMIT:
                continue                       # a maximum whose window ends after the limit is not kept
            out.append(base + [el, v, repr(f_to_c(v)), iso(ws), iso(we), MAX_DEF[model]])
    return out


def mos_months(A, icao):
    first = A[icao]["first_cycle"]
    m = dt.datetime(first.year, first.month, 1)
    out = []
    while m <= LAST_CYCLE:
        out.append(m)
        m = (m.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
    return out


def pull_mos(name):
    model = {"mav": "GFS", "nbs": "NBS"}[name]
    A = load_airports()
    stations = list(US4)
    if name == "nbs":
        with open(OUT / "probe.csv", newline="") as f:
            ok = {r["key"] for r in csv.DictReader(f) if r["source"] == "mos" and r["topic"] == "NBS"
                  and "rows 0" not in r["value"]}
        stations = [s_ for s_ in US4 + ["CYYZ"] if s_ in ok]
    d = WORK / name
    d.mkdir(parents=True, exist_ok=True)
    say(f"== --pull {name} (IEM MOS archive, model {model}): stations {stations}")
    for icao in stations:
        first = A[icao]["first_cycle"]
        for m in mos_months(A, icao):
            key = f"{icao}_{m:%Y-%m}"
            if (d / f"{key}.done").exists():
                continue
            for attempt in range(1, 4):
                try:
                    kept, drop, q = mos_month(model, icao, first, m)
                    out = mos_rows(model, icao, kept, A[icao]["tz"])
                    p_ = d / f"{key}.csv.gz"
                    if p_.exists():
                        p_.unlink()
                    write_csv_gz(p_, MOS_COLS, out)
                    (d / f"{key}.done").write_text(json.dumps(dict(q, drop=drop, rows_out=len(out))) + "\n")
                    break
                except GuardError:
                    raise
                except Exception as e:  # noqa: BLE001
                    say(f"  {key}: attempt {attempt} failed: {str(e)[:160]}")
                    if attempt == 3:
                        with open(d / "failed.txt", "a") as f:
                            f.write(f"{now_utc()} {key} {str(e)[:300]}\n")
        say(f"  {icao}: months done {len(list(d.glob(f'{icao}_*.done')))} of {len(mos_months(A, icao))}")
    return finish_mos(name, model, stations, A)


def probe_mos_leads(model, icao):
    """Each run hour's own leads, from the probe's structure rows (one day in
    2025 and one in 2026)."""
    with open(OUT / "probe.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["source"] == "mos" and r["topic"] == model and r["key"] == icao:
                m = re.search(r"leadlist (\{.*?\})$", r["note"])
                if m:
                    return {int(k): v for k, v in json.loads(m.group(1)).items()}
    raise SystemExit(f"STOP: no nominal leads for {model} {icao} in probe.csv")


def dedupe_runs(rows, icao, notes):
    """Owner's ruling (session 113): a run IEM holds more than once. If its
    copies are identical, one is kept. If any element and projection differ
    between copies, the whole run is dropped and counted as a gap ("issued
    twice with differing values"); nothing is filled. IEM gives no issuance
    time, so the copies cannot be ordered. Notes name the element and
    projection that differ, never the values. Returns (rows, {nominal: run})."""
    by_run = {}
    for r in rows:
        by_run.setdefault(r["cycle"], []).append(r)
    out, dup_gap = [], {}
    for rc, rs in by_run.items():
        grp = {}
        for r in rs:
            grp.setdefault((r["element"], r["ftime_utc"]), []).append(r)
        if all(len(g) == 1 for g in grp.values()):
            out += rs
            continue
        differ = sorted(k for k, g in grp.items() if len({tuple(x.values()) for x in g}) > 1)
        copies = max(len(g) for g in grp.values())
        if differ:
            dup_gap[rs[0]["nominal_cycle"]] = rc
            notes.append([icao, rc, copies, "dropped, counted as a gap",
                          "; ".join(f"{e} at {ft} (lead {grp[(e, ft)][0]['lead']})" for e, ft in differ)])
        else:
            seen = set()
            for r in rs:
                k = tuple(r.values())
                if k not in seen:
                    seen.add(k)
                    out.append(r)
            notes.append([icao, rc, copies, "identical copies, one kept", ""])
    return out, dup_gap


def finish_mos(name, model, stations, A):
    d = WORK / name
    col, el = MAX_ELEMENT[model]
    missing = [f"{s_}_{m:%Y-%m}" for s_ in stations for m in mos_months(A, s_)
               if not (d / f"{s_}_{m:%Y-%m}.done").exists()]
    if missing:
        say(f"  STOP: months not done: {missing[:10]} ({len(missing)})")
        return False
    ok = True
    files, queries, drops, gaps_rows, switch, dup_notes = [], [], {}, [], [], []
    rmap = RUN_TO_NOMINAL[model]
    for icao in stations:
        rows = []
        for m in mos_months(A, icao):
            k = f"{icao}_{m:%Y-%m}"
            rows += read_csv_gz(d / f"{k}.csv.gz")
            q = json.loads((d / f"{k}.done").read_text())
            queries.append([k, q["url"], q["pulled"], q["bytes"], q["sha256"], q["rows"], q["kept"]])
            for a, b in q["drop"].items():
                drops[a] = drops.get(a, 0) + b
        rows, dup_gap = dedupe_runs(rows, icao, dup_notes)
        for n_ in dup_notes:
            if n_[0] == icao:
                say(f"    {icao}: run {n_[1]} held {n_[2]} times: {n_[3]}" + (f"; differ: {n_[4]}" if n_[4] else ""))
        leads = probe_mos_leads(model, icao)
        runs = {}
        for r in rows:
            if r["element"] == "TMP":
                runs.setdefault(r["nominal_cycle"], {}).setdefault(r["cycle"], 0)
                runs[r["nominal_cycle"]][r["cycle"]] += 1
        exp = got = ngap = 0
        per = {}
        state = {}
        for c in cycles(A[icao]["first_cycle"]):
            have = runs.get(iso(c), {})
            labs = sorted("nominal" if rc == iso(c) else "later" for rc in have)
            st_ = "+".join(labs) if labs else "neither"
            state.setdefault(st_, []).append(c)
            if not have:
                gaps_rows.append([name, icao, iso(c), dup_gap.get(iso(c), ""),
                                  "issued twice with differing values" if iso(c) in dup_gap
                                  else "no run paired with this nominal cycle"])
            hcell = per.setdefault(c.hour, [0, 0, 0])
            cand = [h for h, n in rmap.items() if n == c.hour]
            if not have:
                # expected: the nominal run's leads if its hour is known, else the later run's
                h = cand[0]
                e = [l for l in leads.get(h, []) if LEAD_MIN <= l + (h - c.hour) <= LEAD_MAX
                     and c + dt.timedelta(hours=l + h - c.hour) <= LIMIT]
                hcell[0] += len(e)
                hcell[1] += len(e)
                continue
            for rc, n in have.items():
                rct = dt.datetime.strptime(rc, "%Y-%m-%dT%H:%MZ")
                h = rct.hour
                e = [l for l in leads.get(h, []) if LEAD_MIN <= l + (h - c.hour) <= LEAD_MAX
                     and rct + dt.timedelta(hours=l) <= LIMIT]
                hcell[0] += len(e)
                hcell[2] += n
                if n < len(e):
                    hcell[1] += len(e) - n
                    gaps_rows.append([name, icao, iso(c), rc, f"{len(e) - n} TMP projections missing"])
        cells = [(h, a, b, c_) for h, (a, b, c_) in sorted(per.items())]
        eq = all(a - b == c_ for _, a, b, c_ in cells)
        say(f"  {icao}: TMP rows per nominal cycle hour (expected, gaps, got): {cells}: {'equal' if eq else 'DIFFER'}")
        ok &= eq
        for st_, cs in sorted(state.items()):
            switch.append([icao, st_, len(cs), iso(cs[0]), iso(cs[-1])])
            say(f"    {icao} runs paired per nominal cycle: {st_}: {len(cs)} cycles, {iso(cs[0])} to {iso(cs[-1])}")
        p_ = write_csv_gz(OUT / f"{name}_{icao}.csv.gz", MOS_COLS, [[r[c] for c in MOS_COLS] for r in rows])
        files.append((p_, len(rows)))
        lv = max(r["ftime_utc"] for r in rows)
        lw = max((r["window_end_utc"] for r in rows if r["window_end_utc"]), default="none")
        n_out = sum(1 for r in rows if not (-70 <= float(r["value_c"]) <= 60))
        say(f"  {icao}: latest projection {lv}, latest maximum window end {lw}; outside -70 to 60 C: {n_out} of {len(rows)}")
        ok &= lv <= iso(LIMIT) and (lw == "none" or lw <= iso(LIMIT)) and n_out <= 0.001 * len(rows)
    rng = random.Random(113)
    allk = [(s_, m) for s_ in stations for m in mos_months(A, s_)]
    sample = rng.sample(allk, min(20, len(allk)))
    n_same = 0
    for icao, m in sample:
        kept, _, _ = mos_month(model, icao, A[icao]["first_cycle"], m)
        new = mos_rows(model, icao, kept, A[icao]["tz"])
        old = read_csv_gz(d / f"{icao}_{m:%Y-%m}.csv.gz")
        n_same += [[str(x) for x in r] for r in new] == [[r[c] for c in MOS_COLS] for r in old]
    say(f"  check 20 random station-months re-fetched: {n_same} of {len(sample)} identical")
    ok &= n_same == len(sample)
    if not ok:
        for p_, _ in files:
            p_.unlink()
        say("  STOP: a check failed; merged files removed, chunks kept")
        return False
    p_ = write_csv_gz(OUT / f"{name}_queries.csv.gz", ["chunk", "url", "pulled_utc", "bytes", "sha256",
                                                      "rows_returned", "rows_kept"], queries)
    files.append((p_, len(queries)))
    p_ = write_csv(OUT / f"{name}_gaps.csv", ["source", "airport", "nominal_cycle", "run", "reason"], gaps_rows)
    files.append((p_, len(gaps_rows)))
    p_ = write_csv(OUT / f"{name}_runs.csv", ["airport", "runs_paired", "nominal_cycles", "first", "last"], switch)
    files.append((p_, len(switch)))
    p_ = write_csv(OUT / f"{name}_duplicates.csv", ["airport", "run", "copies", "action",
                                                    "differing element and projection"], dup_notes)
    files.append((p_, len(dup_notes)))
    lines = ["Provenance (SPEC 2.3, D107.6). Do not edit the data files.", "",
             f"source      : IEM MOS archive, model {model} ({name}), {IEM}/cgi-bin/request/mos.py",
             f"written by  : scripts/session113_comparison_pull.py --pull {name}", f"written at  : {now_utc()}",
             f"stations    : {' '.join(stations)}",
             "windows     : " + "; ".join(f"{s_} nominal cycles {iso(A[s_]['first_cycle'])} to {iso(LAST_CYCLE)}"
                                         for s_ in stations),
             f"runs        : {RUN_TO_NOMINAL[model]} (run hour -> nominal GFS cycle hour)"
             + ("; owner's ruling: 01/07/13/19 UTC runs kept, labelled one hour later than the nominal cycle; "
                "matching by valid time, never by lead; these runs hold one hour more data than the GFS cycle"
                if model == "NBS" else ""),
             f"columns     : {', '.join(MOS_COLS)}",
             "leads       : projections whose valid time is 3 to 48 h after the nominal cycle and on or before "
             "2026-07-31T23:00 UTC",
             "values      : as issued, whole degrees F (value_f), and converted exactly (value_c = (F - 32) * 5 / 9)",
             f"dropped     : rows filtered on time fields before any value was read: {drops}",
             f"maximum     : {el}: {MAX_DEF[model]}; a maximum whose window ends after the limit is not kept",
             f"gaps        : {len(gaps_rows)} rows in {name}_gaps.csv (counted, never filled)",
             f"duplicates  : {len(dup_notes)} runs IEM holds more than once ({name}_duplicates.csv); owner's "
             "ruling: identical copies, one kept; differing copies, the run dropped and counted as a gap "
             "('issued twice with differing values'); IEM gives no issuance time to order the copies",
             f"packages    : python {sys.version.split()[0]}; requests {requests.__version__}", "",
             "files (SHA-256, rows):"]
    for p_, n in files:
        lines.append(f"  {p_.name}  {sha256_file(p_)}  {n}")
    (OUT / f"{name}_meta.txt").write_text("\n".join(lines) + "\n")
    shutil.rmtree(d)
    say(f"  {name}: files written; dropped before reading values {drops}; gap rows {len(gaps_rows)}")
    return True


# ------------------------------------------------------------------ the official maximum

CLI_COLS = ["airport", "cli_station", "climate_day", "window_start_utc", "window_end_utc", "high_f",
            "high_c", "high_time", "product"]
GHCN_COLS = ["airport", "ghcn_station", "date", "tmax_c_as_given", "tmax_c", "attributes"]


def pull_official():
    A = load_airports()
    say("== --pull official (CLI from IEM, GHCN-Daily TMAX from NCEI; D107.8)")
    ghcn = {}
    with open(OUT / "probe.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["source"] == "official" and r["topic"] == "GHCN-Daily station" and r["value"].startswith("USW"):
                ghcn[r["key"]] = r["value"]
    cli_rows, gh_rows, queries = [], [], []
    dropped = {}
    summary = []
    for icao in US4:
        tz = A[icao]["tz"]
        first = A[icao]["first_cycle"].date()
        last = dt.date(2026, 7, 31)
        while climate_day_window(last, tz)[1] > LIMIT:
            last -= dt.timedelta(days=1)
        guard_climate_day(last, tz)
        for yr in range(first.year, last.year + 1):
            pulled = now_utc()
            r = get(f"{IEM}/json/cli.py", params=dict(station=icao, year=yr, fmt="json"), iem=True)
            kept, after, before = cli_keep(r.json().get("results", []), tz, first)
            queries.append(["cli", icao, r.url, pulled, len(r.content), sha256_bytes(r.content) if yr < 2026 else
                            "(2026 response: not kept, not hashed to disk; owner's ruling)"])
            r = None
            dropped[icao] = dropped.get(icao, 0) + after
            for rec in kept:
                day = dt.date.fromisoformat(str(rec["valid"])[:10])
                s, e = guard_climate_day(day, tz)
                h = rec.get("high")
                hc = repr(f_to_c(h)) if h not in (None, "", "M") else ""
                cli_rows.append([icao, rec.get("station"), day.isoformat(), iso(s), iso(e),
                                 "" if h is None else h, hc, rec.get("high_time") or "", rec.get("product") or ""])
        if icao in ghcn:
            pulled = now_utc()
            r = get(NCEI_DATA, params=dict(dataset="daily-summaries", stations=ghcn[icao],
                                           startDate=first.isoformat(), endDate=last.isoformat(),
                                           dataTypes="TMAX", format="json", units="metric",
                                           includeAttributes="true"))
            rows = r.json()
            queries.append(["ghcn", icao, r.url, pulled, len(r.content), sha256_bytes(r.content)])
            for x in rows:
                day = dt.date.fromisoformat(x["DATE"][:10])
                if day > last or day < first:
                    raise SystemExit("STOP: NCEI returned a day outside the request")
                v = x.get("TMAX")
                gh_rows.append([icao, ghcn[icao], day.isoformat(), "" if v is None else str(v).strip(),
                                repr(float(v)) if v not in (None, "") else "", x.get("TMAX_ATTRIBUTES", "")])
        # report only: days per source and test year, days with both, agreement
        cd = {r[2]: r for r in cli_rows if r[0] == icao and r[6] != ""}
        gd = {r[2]: r for r in gh_rows if r[0] == icao and r[4] != ""}
        per = {}
        for day in sorted(set(cd) | set(gd)):
            d0 = dt.date.fromisoformat(day)
            ty = test_year(dt.datetime(d0.year, d0.month, d0.day))
            c = per.setdefault(ty, [0, 0, 0, 0])
            c[0] += day in cd
            c[1] += day in gd
            if day in cd and day in gd:
                c[2] += 1
                c[3] += abs(float(cd[day][6]) - float(gd[day][4])) < 0.05
        for ty, (a, b, both, agree) in sorted(per.items()):
            summary.append([icao, ty, a, b, both, agree])
            say(f"  {icao} {ty}: CLI days {a}, GHCN days {b}, both {both}, agree after exact conversion {agree}")
        say(f"  {icao}: CLI climate days dropped unread after the limit: {dropped[icao]}; last day kept {last}")
    p1 = write_csv_gz(OUT / "official_cli.csv.gz", CLI_COLS, cli_rows)
    p2 = write_csv_gz(OUT / "official_ghcn.csv.gz", GHCN_COLS, gh_rows)
    p3 = write_csv(OUT / "official_agreement.csv", ["airport", "test_year", "cli_days", "ghcn_days", "both",
                                                     "agree_after_exact_conversion"], summary)
    lines = ["Provenance (SPEC 2.3, D107.8). Do not edit the data files.", "",
             f"written by  : scripts/session113_comparison_pull.py --pull official", f"written at  : {now_utc()}",
             "CLI         : IEM json/cli.py by calendar year; each record filtered on its date field alone, "
             "in memory, before any other field (owner's ruling); climate days whose window ends after "
             f"2026-07-31T23:00 UTC dropped unread: {dropped}",
             "climate day : midnight to midnight local standard time (recorded, not adjusted)",
             f"GHCN-Daily  : {NCEI_DATA} dataset daily-summaries, TMAX, units metric (degrees C as given), "
             f"stations {ghcn}",
             "agreement   : a day agrees if |CLI high converted exactly to C - GHCN TMAX| < 0.05 C (GHCN's precision; "
             "no ties are possible for whole degrees F)", "", "queries:"]
    for q in queries:
        lines.append("  " + " | ".join(str(x) for x in q))
    lines += ["", "files (SHA-256, rows):"]
    for p, n in [(p1, len(cli_rows)), (p2, len(gh_rows)), (p3, len(summary))]:
        lines.append(f"  {p.name}  {sha256_file(p)}  {n}")
    (OUT / "official_meta.txt").write_text("\n".join(lines) + "\n")
    return True


# ------------------------------------------------------------------ --latency

def run_latency():
    say("== --latency (D107.10): archive write time of each cycle's 48 h file minus the cycle")
    dev_cycles = cycles(DEV_FIRST)
    rows_g = listing("gfs", dev_cycles, OUT / "listing_gfs.csv.gz")
    out = []
    for src, path, first in [("gfs", "listing_gfs.csv.gz", DEV_FIRST), ("ifs", "listing_ifs.csv.gz", DEV_FIRST),
                             ("aifs", "listing_aifs.csv.gz", None), ("nbm", "listing_nbm48.csv.gz", DEV_FIRST)]:
        rows = read_csv_gz(OUT / path)
        per = {}
        for r in rows:
            if not r["last_modified_48"]:
                continue
            c = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ")
            lm = dt.datetime.strptime(r["last_modified_48"][:19], "%Y-%m-%dT%H:%M:%S")
            per.setdefault(c.hour, []).append((lm - c).total_seconds() / 3600)
        for h, v in sorted(per.items()):
            v.sort()
            med = v[len(v) // 2] if len(v) % 2 else (v[len(v) // 2 - 1] + v[len(v) // 2]) / 2
            out.append([src, f"{h:02d}", len(v), f"{med:.2f}", f"{v[0]:.2f}", f"{v[-1]:.2f}",
                        f"{v[int(0.05 * (len(v) - 1))]:.2f}", f"{v[int(0.95 * (len(v) - 1))]:.2f}",
                        "archive write time (S3 LastModified of the 48 h file) minus cycle; may be later than public release"])
            say(f"  {src} {h:02d}z: n {len(v)}, median {med:.2f} h, range {v[0]:.2f} to {v[-1]:.2f} h")
    with open(OUT / "probe.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["source"] == "mos" and r["topic"] in ("AFOS product list", "issuance"):
                out.append(["mos", r["key"], "", "", "", "", "", "", f"{r['value']}: {r['note']}"[:400]])
    for src, note in LATENCY_TEXT.items():
        out.append([src, "all", "", "", "", "", "", "", note])
        say(f"  {src}: {note}")
    p = OUT / "latency.csv"
    if p.exists():
        p.unlink()
    write_csv(p, ["source", "cycle_hour", "n", "median_h", "min_h", "max_h", "p05_h", "p95_h", "label"], out)
    return out


LATENCY_TEXT = {
    "mav": "documented time only: MAV is generated from 00, 06, 12 and 18 UTC GFS output (MDL MAV card); "
           "no issuance time is given in the documentation read; IEM's AFOS list holds no MAV product "
           "(probe), so no product-header time exists here",
    "nbs": "documented time only: no issuance time is given in the NBM text card v5.0; IEM's AFOS list holds "
           "no NBS product (probe); runs are labelled by the run time IEM gives",
}


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--probe", action="store_true")
    g.add_argument("--cost", action="store_true")
    g.add_argument("--pull", choices=["ifs", "aifs", "nbs", "nbm", "mav", "official"])
    g.add_argument("--latency", action="store_true")
    ap.add_argument("--tmp", help="the one temporary folder for downloads in flight")
    ap.add_argument("--source", choices=["ifs"], help="--cost for one source only (owner's IFS re-measurement)")
    ap.add_argument("--workers", type=int, default=MAX_WORKERS,
                    help="requests at once; above 8 only for the IFS re-measurement and pull (owner's ruling)")
    ap.add_argument("--override", default="", help="the owner's D107.7 override, recorded in the meta file")
    args = ap.parse_args()
    if args.check:
        sys.exit(0 if run_check() else 1)
    global TMP
    if not args.tmp:
        raise SystemExit("--tmp is required for network modes")
    TMP = Path(args.tmp)
    TMP.mkdir(parents=True, exist_ok=True)
    say(f"run start {now_utc()}; python {sys.version.split()[0]}, eccodes {ec.__version__}, "
        f"numpy {np.__version__}, requests {requests.__version__}")
    if args.probe:
        sys.exit(0 if run_probe() else 1)
    if args.workers != MAX_WORKERS and not ((args.cost and args.source == "ifs") or args.pull == "ifs"):
        raise SystemExit("STOP: more than 8 requests at once only for the IFS re-measurement and pull")
    if args.workers not in (MAX_WORKERS, 16, 32):
        raise SystemExit("STOP: workers must be 8, 16 or 32")
    WORKERS[0] = args.workers
    OVERRIDE[0] = args.override
    if args.cost:
        run_cost(args.source)
        sys.exit(0)
    if args.pull in ("ifs", "aifs", "nbm"):
        gate = {r["source"]: r["gate"] for r in csv.DictReader(open(OUT / "cost.csv", newline=""))}
        g = gate.get(args.pull)
        if args.pull == "ifs" and args.workers != MAX_WORKERS:
            pth = OUT / f"cost_ifs_w{args.workers}.csv"
            g = next(csv.DictReader(open(pth, newline="")))["gate"] if pth.exists() else "not measured"
        # an owner's D107.7 override lifts the gate for the NBM grid (session 113) and for
        # IFS's follow-up session (owner's ruling: --pull ifs unchanged, with the override text)
        if g != "PASS" and not (args.pull in ("nbm", "ifs") and args.override):
            raise SystemExit(f"STOP: {args.pull} did not pass the cost gate (D107.7): {g}")
        say(f"  gate: {g}; requests at once {args.workers}; owner's override: {args.override or 'none'}")
        src, months, failed = pull_gridded(args.pull)
        if failed:
            say(f"  chunks failed 3 times: {failed}; rerun to retry them; not merged")
            sys.exit(2)
        if args.pull in ("ifs", "aifs"):
            pull_terrain(args.pull)
        sys.exit(0 if finish_gridded(args.pull) else 1)
    if args.pull in ("mav", "nbs"):
        sys.exit(0 if pull_mos(args.pull) else 1)
    if args.pull == "official":
        sys.exit(0 if pull_official() else 1)
    if args.latency:
        run_latency()
        sys.exit(0)


if __name__ == "__main__":
    main()
