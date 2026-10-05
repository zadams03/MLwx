"""Session 91: the stage C GRIB pull (DECISIONS D82.4, D83).

It reads GFS 0.25 degree GRIB2 messages from the public bucket
`noaa-gfs-bdp-pds` by byte range, and keeps only the raw decoded values at
the four grid points around each of the 51 pull airports (D83.2, D83.3).
No global field is kept: each message is held in memory, read and dropped.

Modes (exactly one):
  --positions    Network (one .idx and one message). Writes the positions file
                 data/processed/session91_pull_airports.csv and its .meta.txt
                 (session 91, Step 3). Refuses if either exists.
  --plan         Offline. For every month 2021-03 to 2026-07: first and last
                 cycle, cycles, files, expected messages, earliest and latest
                 valid time.
  --chunk        Network. The pull for one month (--month YYYY-MM) or for a
                 list of cycle dates (--dates D1,D2,..., the test chunk), for
                 forecast hours --hours A-B, into --out DIR. Writes three files
                 (points, manifest, meta), only if every download succeeded.
  --gate         Offline. Rebuilds the record's seven GRIB-derived columns at
                 the six development airports from a finished chunk's files
                 and compares them with the committed training set (D83.6).
  --guard-check  Offline. Shows every refusal fires, and two allowed cases.

The chunk output has no interpolation, no derived field and no rounding:
values are the decoded numbers, written with repr so they read back
identically (D83.5(c)). Interpolation and derivation exist only in --gate.

Whole-file fallback (session 94, DECISIONS D86.2): when a message's byte range
still gives a broken body (no GRIB or 7777 marker) after its retries, the
file's .idx does not describe it (F135). The whole file is then downloaded,
its messages are found by walking the GRIB headers, and every planned field
of that file is taken from the one walked message that passes the same
per-message check, with status "ok (whole file)". Network errors, HTTP errors
and a missing .idx are handled as before.

Hard limits, enforced in code (D83.5(b)): no cycle after 2026-07-31T18 UTC;
no message valid after 2026-07-31T23:00 or before 2021-03-24T00:00 UTC; no
forecast hour outside 0 to 48.

Copied from record scripts (cited at each copy; nothing is imported from
them): `find_range`, `bilinear_from_gid`, the checks in `decode`,
`window_start`, `year_fraction`, `load_airports` and `derive`, all from
scripts/session86_forward_build.py (DECISIONS F128.3).

SPEC 8.7 build requirements: (2) a non-finite or missing grid value fails the
message's check and is never filled; (3) each message's run date and time and
its full validity date and hour are checked; (5) every output file is created
exclusively and nothing is written over.
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import math
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.dont_write_bytecode = True

import eccodes as ec  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT / "SPEC.md"
DECISIONS_FILE = ROOT / "DECISIONS.md"
AIRPORTS_90 = ROOT / "data" / "processed" / "session90_airports.csv"
POSITIONS = ROOT / "data" / "processed" / "session91_pull_airports.csv"
POSITIONS_META = ROOT / "data" / "processed" / "session91_pull_airports.csv.meta.txt"
TRAINING_SET = ROOT / "data" / "processed" / "session81_training_set.csv"
PARAMS_CSVS = [
    ROOT / "data" / "raw" / "diagnostics" / "session37" / "session37_elevation_correction_params.csv",
    ROOT / "data" / "raw" / "diagnostics" / "session76" / "session76_elevation_correction_params.csv",
]

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# D83.5(b): the window. Nothing outside it is requested; the guards refuse it.
FIRST_VALID = dt.datetime(2021, 3, 24, 0)
LAST_VALID = dt.datetime(2026, 7, 31, 23)
LAST_CYCLE = dt.datetime(2026, 7, 31, 18)
FIRST_MONTH, LAST_MONTH = (2021, 3), (2026, 7)
MAX_HOUR = 48
CYCLES = (0, 6, 12, 18)

# D83.2: the six development airports, by SPEC 3.4 station code -> ICAO code.
DEV = {"EGLC": "EGLC", "LFPG": "LFPG", "DSM": "KDSM", "YSDU": "YSDU", "RNO": "KRNO", "SFO": "KSFO"}

# The ten fields (D82.4), in output order. Each: short name, .idx variable,
# .idx level, kind, and the GRIB2 identity (discipline, category, number,
# type of first fixed surface, level). The identities of the record's eight
# are those of session86_forward_build.py l.373-389; TMAX and TMIN are
# parameter numbers 4 and 5 of the same category as TMP.
FIELDS = [
    ("t2m", "TMP", "2 m above ground", "instant", (0, 0, 0, 103, 2)),
    ("tcdc", "TCDC", "entire atmosphere", "instant", (0, 6, 1, 10, 0)),
    ("u10", "UGRD", "10 m above ground", "instant", (0, 2, 2, 103, 10)),
    ("v10", "VGRD", "10 m above ground", "instant", (0, 2, 3, 103, 10)),
    ("d2m", "DPT", "2 m above ground", "instant", (0, 0, 6, 103, 2)),
    ("t850", "TMP", "850 mb", "instant", (0, 0, 0, 100, 850)),
    ("dswrf", "DSWRF", "surface", "avg", (0, 4, 192, 1, 0)),
    ("prmsl", "PRMSL", "mean sea level", "instant", (0, 3, 1, 101, 0)),
    ("tmax2m", "TMAX", "2 m above ground", "max", (0, 0, 4, 103, 2)),
    ("tmin2m", "TMIN", "2 m above ground", "min", (0, 0, 5, 103, 2)),
]
FIELD_NAMES = [f[0] for f in FIELDS]
STEP_WORD = {"avg": "ave", "max": "max", "min": "min"}

POINT_COLS = ["cycle_utc", "fhour", "valid_utc", "icao"] + [f"{f}_{k}" for f in FIELD_NAMES for k in (1, 2, 3, 4)]
MAN_COLS = ["cycle_utc", "fhour", "field", "idx_line", "byte_range", "bytes", "status", "step_range",
            "process_type", "reason"]
STATUS_WHOLE = "ok (whole file)"    # session 94, D86.2
STATUSES = ["ok", "absent by design", "idx missing", "check failed", STATUS_WHOLE]
GEOM_KEYS = [("Ni", "Ni"), ("Nj", "Nj"), ("lat_first", "latitudeOfFirstGridPointInDegrees"),
             ("lon_first", "longitudeOfFirstGridPointInDegrees"), ("lat_last", "latitudeOfLastGridPointInDegrees"),
             ("lon_last", "longitudeOfLastGridPointInDegrees"), ("di", "iDirectionIncrementInDegrees"),
             ("dj", "jDirectionIncrementInDegrees")]

# The gate (D83.6).
GATE_DATES = [dt.date(2022, 1, 13), dt.date(2023, 7, 13), dt.date(2024, 4, 13)]
GATE_COLS = ["temperature_grib_c", "cloud_cover", "wind_speed_10m", "dewpoint_depression_t2m_floored",
             "lapse_rate_t2_t850", "pressure_tendency_3h_hpa", "dswrf_2h_wm2"]

RETRIES = 5              # retries after the first try: network errors, 429 and 5xx only
IDX_RESERVE = 50_000     # bytes reserved against the budget for one .idx request

_local = threading.local()
_ec_lock = threading.Lock()
_whole_lock = threading.Lock()   # D86.2: at most one whole file in memory across all workers


class GuardError(Exception):
    """A hard limit fired. The run stops."""


class DownloadError(Exception):
    """A download failed after its retries. The chunk fails and writes nothing."""


class BrokenBody(DownloadError):
    """A message's byte range still gave a broken body (no GRIB or 7777 marker)
    after its retries. process_file sends the file to the whole-file fallback
    (D86.2); anywhere else it stops the chunk as any DownloadError does."""


class BudgetStop(Exception):
    """The byte budget would be passed. The chunk stops and writes nothing."""


class NotFound(Exception):
    """HTTP 404."""


# ------------------------------------------------------------------ small helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def versions():
    return (f"python {sys.version.split()[0]}; eccodes (Python) {ec.__version__}; "
            f"ecCodes library {ec.codes_get_api_version()}; numpy {np.__version__}; requests {requests.__version__}")


def window_start(fh):
    """The 6-hour reset mark before a forecast hour, for averages, maxima and
    minima. Copied from session86_forward_build.py l.173-176."""
    return 6 * ((fh - 1) // 6)


def year_fraction(d):
    """Copied from session86_forward_build.py l.179-182 (record:
    session62_reserved_confirm.py l.217-219)."""
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


# ------------------------------------------------------------------ guards (D83.5(b), Step 4.5)

def check_hours(a, b):
    if not (isinstance(a, int) and isinstance(b, int)) or a < 0 or b > MAX_HOUR or a > b:
        raise GuardError(f"--hours {a}-{b} is outside 0 to {MAX_HOUR}")


def check_cycle(cycle):
    if cycle.hour not in CYCLES or cycle.minute or cycle.second:
        raise GuardError(f"cycle {iso(cycle)} is not a 00, 06, 12 or 18 UTC cycle")
    if cycle > LAST_CYCLE:
        raise GuardError(f"cycle {iso(cycle)} is after {iso(LAST_CYCLE)}")


def check_valid(valid):
    if valid > LAST_VALID:
        raise GuardError(f"valid time {iso(valid)} is after {iso(LAST_VALID)}")
    if valid < FIRST_VALID:
        raise GuardError(f"valid time {iso(valid)} is before {iso(FIRST_VALID)}")


def check_request(cycle, fh):
    """Every message request passes through here before any network call."""
    check_cycle(cycle)
    check_hours(fh, fh)
    check_valid(cycle + dt.timedelta(hours=fh))


def check_out_free(paths):
    """SPEC 8.7 item 5: refuse if any output file exists."""
    there = [str(p) for p in paths if p.exists()]
    if there:
        raise GuardError("an output file already exists, not writing over it: " + ", ".join(there))


def parse_hours(s):
    m = re.fullmatch(r"(\d+)-(\d+)", s or "")
    if not m:
        raise GuardError(f"--hours must be A-B, got {s!r}")
    a, b = int(m.group(1)), int(m.group(2))
    check_hours(a, b)
    return a, b


# ------------------------------------------------------------------ the request plan

def selector(kind, fh):
    """The .idx step text of a field at a forecast hour (Step 2). None means
    absent by design: GFS gives no average, maximum or minimum at f000."""
    if kind == "instant":
        return "anl" if fh == 0 else f"{fh} hour fcst"
    if fh == 0:
        return None
    return f"{window_start(fh)}-{fh} hour {STEP_WORD[kind]} fcst"


def expected_steps(kind, fh):
    """(stepType, startStep, endStep) the decoded message must carry."""
    if kind == "instant":
        return ("instant", fh, fh)
    return (kind, window_start(fh), fh)


def month_cycles(year, month):
    d = dt.date(year, month, 1)
    out = []
    while d.month == month:
        out += [dt.datetime(d.year, d.month, d.day, h) for h in CYCLES]
        d += dt.timedelta(days=1)
    return out


def plan_chunk(cycles, hours):
    """[(cycle, [fh, ...])] for the given cycles. A forecast hour whose valid
    time lies outside the window is not requested (D83.5(b)); a cycle with no
    such hour is left out. Every kept request passes check_request."""
    a, b = hours
    check_hours(a, b)
    plan = []
    for c in cycles:
        check_cycle(c)
        fhs = [fh for fh in range(a, b + 1) if FIRST_VALID <= c + dt.timedelta(hours=fh) <= LAST_VALID]
        for fh in fhs:
            check_request(c, fh)
        if fhs:
            plan.append((c, fhs))
    return plan


def parse_month(s):
    m = re.fullmatch(r"(\d{4})-(\d{2})", s or "")
    if not m:
        raise GuardError(f"--month must be YYYY-MM, got {s!r}")
    ym = (int(m.group(1)), int(m.group(2)))
    if not (1 <= ym[1] <= 12) or ym < FIRST_MONTH or ym > LAST_MONTH:
        raise GuardError(f"month {s} is outside {FIRST_MONTH[0]}-{FIRST_MONTH[1]:02d} to "
                         f"{LAST_MONTH[0]}-{LAST_MONTH[1]:02d}")
    return ym


def all_months():
    y, m = FIRST_MONTH
    while (y, m) <= LAST_MONTH:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def expected_messages(fh):
    return sum(1 for f in FIELDS if selector(f[3], fh) is not None)


# ------------------------------------------------------------------ HTTP with retries and a byte budget

class Fetcher:
    def __init__(self, budget=None):
        self.budget = budget
        self.lock = threading.Lock()
        self.reserved = 0
        self.bytes = {"idx": 0, "message": 0, "whole": 0}
        self.requests = {"idx": 0, "message": 0, "whole": 0}
        self.retries = 0
        self.not_found = 0
        self.whole = []     # D86.2: one record per file that fell back (see process_whole_file)

    def session(self):
        if not hasattr(_local, "s"):
            _local.s = requests.Session()
            _local.s.headers.update({"User-Agent": "MLwx/session91"})
        return _local.s

    def reserve(self, n):
        with self.lock:
            if self.budget is not None and self.reserved + n > self.budget:
                raise BudgetStop(f"the next request would pass the budget of {self.budget:,} bytes "
                                 f"({self.reserved:,} already reserved)")
            self.reserved += n

    def get(self, url, kind, byte_range=None, expected_len=None):
        """At most 1 + RETRIES tries. Retries only on network errors (including a
        short or broken body), HTTP 429 and 5xx, with a growing wait. A 404 raises
        NotFound at once. Anything else, or the last failure, raises DownloadError."""
        self.reserve(expected_len if expected_len is not None else IDX_RESERVE)
        headers = {"Range": f"bytes={byte_range}"} if byte_range else {}
        last = None
        broken = False      # D86.2: whether the last failure was a broken body
        for attempt in range(RETRIES + 1):
            if attempt:
                with self.lock:
                    self.retries += 1
                time.sleep(2.0 * 2 ** (attempt - 1))
            broken = False
            try:
                r = self.session().get(url, headers=headers, timeout=(20, 180))
            except requests.RequestException as e:
                last = f"network error {e!r}"
                continue
            if r.status_code == 404:
                with self.lock:
                    self.not_found += 1
                raise NotFound(url)
            if r.status_code == 429 or 500 <= r.status_code <= 599:
                last = f"HTTP {r.status_code}"
                continue
            if r.status_code != (206 if byte_range else 200):
                raise DownloadError(f"{url} {byte_range or ''}: HTTP {r.status_code}")
            body = r.content
            if expected_len is not None and len(body) != expected_len:
                last = f"short body {len(body)} of {expected_len} bytes"
                continue
            if kind == "message" and (body[:4] != b"GRIB" or body[-4:] != b"7777"):
                last = "broken body (no GRIB or 7777 marker)"
                broken = True
                continue
            with self.lock:
                self.bytes[kind] += len(body)
                self.requests[kind] += 1
            return body
        raise (BrokenBody if broken else DownloadError)(
            f"{url} {byte_range or ''}: failed after {RETRIES} retries: {last}")

    def get_whole(self, url):
        """D86.2: one whole GRIB file, in memory, with get's retry policy (network
        errors, 429 and 5xx retried; a 404 or any other status stops at once). The
        bytes received must equal the response's Content-Length; a shorter or
        longer body counts as a network error and is retried."""
        last = None
        reserved = False
        for attempt in range(RETRIES + 1):
            if attempt:
                with self.lock:
                    self.retries += 1
                time.sleep(2.0 * 2 ** (attempt - 1))
            try:
                with self.session().get(url, timeout=(20, 180), stream=True) as r:
                    if r.status_code == 404:
                        with self.lock:
                            self.not_found += 1
                        raise DownloadError(f"{url} (whole file): HTTP 404 for a file whose .idx exists")
                    if r.status_code == 429 or 500 <= r.status_code <= 599:
                        last = f"HTTP {r.status_code}"
                        continue
                    if r.status_code != 200:
                        raise DownloadError(f"{url} (whole file): HTTP {r.status_code}")
                    if "Content-Length" not in r.headers:
                        raise DownloadError(f"{url} (whole file): no Content-Length")
                    n = int(r.headers["Content-Length"])
                    if not reserved:
                        self.reserve(n)
                        reserved = True
                    body = r.content
            except requests.RequestException as e:
                last = f"network error {e!r}"
                continue
            if len(body) != n:
                last = f"body {len(body)} bytes, Content-Length {n}"
                continue
            with self.lock:
                self.bytes["whole"] += len(body)
                self.requests["whole"] += 1
            return body
        raise DownloadError(f"{url} (whole file): failed after {RETRIES} retries: {last}")


def whole_stats(fetcher):
    """D86.2: the fallback's counts, for the progress lines, the closing summary
    and the meta."""
    with fetcher.lock:
        recs = list(fetcher.whole)
    return (f"whole-file fallbacks {len(recs)} files, {sum(r['bytes'] for r in recs):,} B, "
            f"{sum(r['ok_whole'] for r in recs)} messages ok (whole file)")


def file_url(cycle, fh):
    return f"{BUCKET}/gfs.{cycle:%Y%m%d}/{cycle:%H}/atmos/gfs.t{cycle:%H}z.pgrb2.0p25.f{fh:03d}"


def parse_idx(text):
    rows = []
    for line in text.strip().splitlines():
        p = line.split(":")
        rows.append({"offset": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5], "line": line})
    return rows


def find_range(rows, var, level, step, cycle):
    """Copied from session86_forward_build.py l.409-421 (record:
    session76_grib_pull.py l.167-177): exactly one .idx line, with the run stamp
    checked. Returns (byte range, expected length or None, the line)."""
    hits = [i for i, r in enumerate(rows) if r["var"] == var and r["level"] == level and r["step"] == step]
    if len(hits) != 1:
        raise ValueError(f"expected 1 idx line for {var}:{level}:{step}, found {len(hits)}")
    i = hits[0]
    if rows[i]["d"] != f"d={cycle:%Y%m%d%H}":
        raise ValueError(f"idx run stamp {rows[i]['d']} does not match the run")
    start = rows[i]["offset"]
    if i + 1 < len(rows):
        return f"{start}-{rows[i + 1]['offset'] - 1}", rows[i + 1]["offset"] - start, rows[i]["line"]
    return f"{start}-", None, rows[i]["line"]


# ------------------------------------------------------------------ positions

def read_positions(path=POSITIONS):
    with open(path) as f:
        rows = list(csv.DictReader(f))
    if [r["icao"] for r in rows] != sorted(r["icao"] for r in rows) or len(rows) != 51:
        raise SystemExit(f"STOP: {path} must hold 51 rows sorted by ICAO code")
    geom = {k: rows[0][f"grid_{k}"] for k, _ in GEOM_KEYS}
    if any({k: r[f"grid_{k}"] for k, _ in GEOM_KEYS} != geom for r in rows):
        raise SystemExit("STOP: the grid geometry differs between rows of the positions file")
    geom = {k: (int(v) if k in ("Ni", "Nj") else float(v)) for k, v in geom.items()}
    for r in rows:
        r["indices"] = [int(r[f"p{k}_index"]) for k in (1, 2, 3, 4)]
    return rows, geom


def msg_geometry(gid):
    return {k: (ec.codes_get_long(gid, key) if k in ("Ni", "Nj") else ec.codes_get_double(gid, key))
            for k, key in GEOM_KEYS}


def load_airports():
    """Per-airport facts from committed files only: SPEC 3.4's two tables and the
    params CSVs. Copied from session86_forward_build.py l.226-263, without the
    observation and R columns this script does not use."""
    text = SPEC_FILE.read_text()
    block = text[text.index("**3.4 The airport table.**"):text.index("Notes on the table:")]
    header, t1, t2 = None, {}, {}
    for ln in block.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == "station code":
            header = cells
            continue
        if set(cells[0]) <= set("-") or header is None:
            continue
        row = dict(zip(header, cells))
        (t1 if "target hour (UTC)" in header else t2)[cells[0]] = row
    corr = {}
    for p in PARAMS_CSVS:
        with open(p) as f:
            for r in csv.DictReader(f):
                if r["station"] in corr:
                    raise SystemExit(f"STOP: two elevation constants for {r['station']}")
                corr[r["station"]] = float(r["correction_c"])
    out = {}
    for st in t1:
        hour = int(t1[st]["target hour (UTC)"].split(":")[0])
        out[st] = {"station": st, "target_hour": hour, "cycle": (hour // 6) * 6, "lead": 24 + hour % 6,
                   "grid_lat": float(t2[st]["grid latitude"]), "grid_lon": float(t2[st]["grid longitude"]),
                   "correction_c": corr[st]}
    if list(out) != list(DEV) or set(corr) != set(out):
        raise SystemExit(f"STOP: unexpected airport set {list(out)} / constants {sorted(corr)}")
    return out


def bilinear_from_gid(gid, lat, lon):
    """Copied from session86_forward_build.py l.424-451 (record:
    session49_upper_air_pull.py l.148-171, SPEC 8.8 G6). Used only for the
    development-airport check in --positions."""
    neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    missing = ec.codes_get_double(gid, "missingValue")
    bitmap = ec.codes_get_long(gid, "bitmapPresent")
    for n in neighbours:
        if not math.isfinite(n.value) or (bitmap and n.value == missing):
            raise ValueError("missing or non-finite grid value")
    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        lat_span = max(n.lat for n in neighbours) - min(n.lat for n in neighbours)
        lon_span = max(n.lon for n in neighbours) - min(n.lon for n in neighbours)
        if lat_span < 1e-6 or lon_span < 1e-6:
            return min(neighbours, key=lambda n: n.distance).value
        raise ValueError("unexpected neighbour layout")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    return ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
            + dlat * (1 - dlon) * v10 + dlat * dlon * v11)


def bilinear_weights(points, lat, lon):
    """The weight each of the 4 points gets under the record's bilinear (SPEC 8.8
    G6; the arithmetic of bilinear_from_gid above, so weight times value is the
    record's term). points: [(lat, lon)] in eccodes order."""
    lats = sorted(set(round(p[0], 6) for p in points))
    lons = sorted(set(round(p[1], 6) for p in points))
    if len(lats) != 2 or len(lons) != 2:
        raise ValueError("the 4 points do not form a 2 x 2 box")
    lat0, lat1 = lats
    lon0, lon1 = lons
    lon_q = lon + 360.0 if lon < 0 else lon
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    out = []
    for la, lo in points:
        wa = (1 - dlat) if round(la, 6) == lat0 else dlat
        wo = (1 - dlon) if round(lo, 6) == lon0 else dlon
        out.append(wa * wo)
    return out


def run_positions(args):
    """Step 3: the positions file, from one decoded message (computed once)."""
    print("SESSION 91 --positions")
    check_out_free([POSITIONS, POSITIONS_META])
    started = now_utc()
    spec = load_airports()
    with open(AIRPORTS_90) as f:
        a90 = {r["icao"]: r for r in csv.DictReader(f)}
    if len(a90) != 47:
        raise SystemExit("STOP: session90_airports.csv must hold 47 airports")
    pos = []
    for st, icao in DEV.items():
        iem = st
        pos.append({"icao": icao, "iem_id": iem, "role": "development",
                    "position_source": "SPEC 3.4 grid point", "lat": spec[st]["grid_lat"], "lon": spec[st]["grid_lon"]})
    for icao, r in a90.items():
        if icao in DEV.values():
            if r["iem_id"] != [k for k, v in DEV.items() if v == icao][0]:
                raise SystemExit(f"STOP: IEM id of {icao} differs")
            continue
        role = "claim batch" if r["drawn"] == "yes" else "new"
        pos.append({"icao": icao, "iem_id": r["iem_id"], "role": role,
                    "position_source": "IEM airport position (session90_airports.csv)",
                    "lat": float(r["latitude"]), "lon": float(r["longitude"])})
    pos.sort(key=lambda p: p["icao"])
    roles = {k: sum(1 for p in pos if p["role"] == k) for k in ("development", "claim batch", "new")}
    print(f"airports: {len(pos)}; by role {roles}")
    if len(pos) != 51 or roles != {"development": 6, "claim batch": 6, "new": 39}:
        raise SystemExit("STOP: the pull list must be 51 airports: 6 development, 6 claim batch, 39 new")

    cycle, fh = dt.datetime(2023, 7, 12, 12), 0
    f = Fetcher()
    url = file_url(cycle, fh)
    rows = parse_idx(f.get(url + ".idx", "idx").decode("ascii"))
    rng, exp, line = find_range(rows, "TMP", "2 m above ground", "anl", cycle)
    data = f.get(url, "message", rng, exp)
    gid = ec.codes_new_from_message(data)
    try:
        got = tuple(ec.codes_get_long(gid, k) for k in ("discipline", "parameterCategory", "parameterNumber",
                                                         "typeOfFirstFixedSurface", "level"))
        if got != FIELDS[0][4] or ec.codes_get_long(gid, "dataDate") != 20230712 \
                or ec.codes_get_long(gid, "dataTime") != 1200 or ec.codes_get_long(gid, "validityDate") != 20230712 \
                or ec.codes_get_long(gid, "validityTime") != 1200 or ec.codes_get_string(gid, "gridType") != "regular_ll":
            raise SystemExit("STOP: the positions message failed its identity, run or validity check")
        geom = msg_geometry(gid)
        print("grid geometry: " + ", ".join(f"{k} {v!r}" for k, v in geom.items()))
        values = ec.codes_get_values(gid)
        for p in pos:
            lon_q = p["lon"] + 360.0 if p["lon"] < 0 else p["lon"]
            nb = ec.codes_grib_find_nearest(gid, p["lat"], lon_q, npoints=4)
            p["points"] = [(int(n.index), float(n.lat), float(n.lon)) for n in nb]
            p["weights"] = bilinear_weights([(q[1], q[2]) for q in p["points"]], p["lat"], p["lon"])
            if abs(sum(p["weights"]) - 1.0) > 1e-12:
                raise SystemExit(f"STOP: weights of {p['icao']} do not sum to 1")
        print("\ndevelopment-airport check: the four points against those the record's bilinear_from_gid uses "
              "(codes_grib_find_nearest at the unshifted SPEC 3.4 longitude), and the bilinear value from the "
              "stored indices and weights against bilinear_from_gid's value (equality only; no value printed)")
        dev_ok = True
        for p in pos:
            if p["role"] != "development":
                continue
            nb = ec.codes_grib_find_nearest(gid, p["lat"], p["lon"], npoints=4)
            rec = [(int(n.index), float(n.lat), float(n.lon)) for n in nb]
            same_pts = rec == p["points"]
            # the record's own term order: by (lat, lon) box corner, not eccodes order
            grid = {(round(q[1], 6), round(q[2], 6)): (w, float(values[q[0]])) for w, q in zip(p["weights"], p["points"])}
            keys = sorted(grid)
            ours_rec_order = 0.0
            for k in keys:
                ours_rec_order += grid[k][0] * grid[k][1]
            rec_val = bilinear_from_gid(gid, p["lat"], p["lon"])
            print(f"  {p['icao']}: points equal {same_pts}; indices {[q[0] for q in p['points']]}; "
                  f"bilinear equal (record term order) {ours_rec_order == rec_val}")
            dev_ok &= same_pts and ours_rec_order == rec_val
        if not dev_ok:
            raise SystemExit("STOP: the development-airport check failed")
    finally:
        ec.codes_release(gid)
    del data

    cols = (["icao", "iem_id", "role", "position_source", "lat_used", "lon_used"]
            + [f"p{k}_{c}" for k in (1, 2, 3, 4) for c in ("index", "lat", "lon", "weight")]
            + [f"grid_{k}" for k, _ in GEOM_KEYS])
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(cols)
    for p in pos:
        row = [p["icao"], p["iem_id"], p["role"], p["position_source"], repr(p["lat"]), repr(p["lon"])]
        for q, wt in zip(p["points"], p["weights"]):
            row += [q[0], repr(q[1]), repr(q[2]), repr(wt)]
        row += [repr(geom[k]) for k, _ in GEOM_KEYS]
        w.writerow(row)
    with open(POSITIONS, "x", newline="") as fh_:
        fh_.write(buf.getvalue())
    sha = sha256_file(POSITIONS)
    srcs = [SPEC_FILE, AIRPORTS_90]
    meta = ["Provenance (SPEC 2.3). Do not edit the data file.", "",
            f"file        : {POSITIONS.name}",
            "purpose     : session 91, Step 3 - the 51 pull airports (DECISIONS D83.2, D83.3): the position used, the",
            "              four GFS 0.25 degree grid points around it (index in the 721 x 1440 grid, latitude,",
            "              longitude, in the order eccodes returns them) and each point's bilinear weight (SPEC 8.8 G6).",
            f"written at  : {now_utc()} (run started {started})",
            "written by  : scripts/session91_grib_pull.py --positions",
            f"rows        : {len(pos)}",
            f"sha256      : {sha}", "",
            "positions   : development airports (EGLC, LFPG, KDSM, YSDU, KRNO, KSFO): SPEC 3.4's grid latitude and",
            "              longitude, read from SPEC.md by station code; the other 45: IEM's latitude and longitude",
            "              from data/processed/session90_airports.csv. lon_used is as the source gives it; a",
            "              negative longitude was shifted by +360 before codes_grib_find_nearest and the weights (G6).",
            "sources     : " + "; ".join(f"{s.relative_to(ROOT)} sha256 {sha256_file(s)}" for s in srcs),
            f"GRIB message: {url} bytes {rng} ({exp:,} B), idx line '{line}'",
            "              (one decoded message; the four points depend only on the grid geometry)",
            "grid        : " + ", ".join(f"{k} {geom[k]!r}" for k, _ in GEOM_KEYS),
            f"packages    : {versions()}",
            f"requests    : {sum(f.requests.values())} ({f.bytes['idx']:,} B idx, {f.bytes['message']:,} B message)"]
    with open(POSITIONS_META, "x") as fh_:
        fh_.write("\n".join(meta) + "\n")
    print(f"\nwrote {POSITIONS.relative_to(ROOT)} ({len(pos)} rows), SHA-256 {sha}")
    print(f"wrote {POSITIONS_META.relative_to(ROOT)}")
    print(f"requests {sum(f.requests.values())}; bytes {sum(f.bytes.values()):,}")
    return 0


# ------------------------------------------------------------------ one file: .idx, messages, values

def check_message(gid, ident, steps, cycle, valid, positions, geom):
    """Session 91's per-message check, moved here unchanged from process_file so
    the whole-file fallback (D86.2) applies the same check. Tests identity
    (discipline, category, number, surface type, level), stepType, startStep
    and endStep, run date and time, full validity date and hour, grid geometry,
    and a finite value at every airport's four grid indices. Raises ValueError
    (or an eccodes error) if the message fails, GuardError if a hard limit
    fires. Returns the 4 values per airport, read by grid index."""
    got = (tuple(ec.codes_get_long(gid, k) for k in ("discipline", "parameterCategory", "parameterNumber",
                                                      "typeOfFirstFixedSurface", "level"))
           + (ec.codes_get_string(gid, "stepType"), ec.codes_get_long(gid, "startStep"),
              ec.codes_get_long(gid, "endStep")))
    vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
    if got != ident + steps:
        raise ValueError(f"identity {got} != expected {ident + steps}")
    if (ec.codes_get_long(gid, "dataDate") != int(f"{cycle:%Y%m%d}")
            or ec.codes_get_long(gid, "dataTime") != cycle.hour * 100):
        raise ValueError("run date or time mismatch")
    if vd != int(f"{valid:%Y%m%d}") or vt != valid.hour * 100:
        raise ValueError(f"validity {vd} {vt:04d} != expected {valid:%Y%m%d %H%M}")
    check_valid(dt.datetime(vd // 10000, (vd // 100) % 100, vd % 100, vt // 100, vt % 100))
    g = msg_geometry(gid)
    if g != geom or ec.codes_get_string(gid, "gridType") != "regular_ll":
        raise ValueError(f"grid geometry {g} differs from the positions file")
    values = ec.codes_get_values(gid)
    missing = ec.codes_get_double(gid, "missingValue")
    bitmap = ec.codes_get_long(gid, "bitmapPresent")
    out = []
    for p in positions:
        for i in p["indices"]:
            v = float(values[i])
            if not math.isfinite(v) or (bitmap and v == missing):
                raise ValueError(f"missing or non-finite value at grid index {i} ({p['icao']})")
            out.append(v)
    return out


def walk_messages(data):
    """D86.2: the file's message boundaries from its own GRIB headers, not the
    .idx. From byte 0: "GRIB", edition 2, the 8-byte total length (section 0,
    bytes 8 to 15), "7777" at that message's end, then the next. The walk must
    end exactly at the file's last byte. Returns [(offset, length)]; raises
    ValueError if any of this fails."""
    out, pos, n = [], 0, len(data)
    while pos < n:
        if n - pos < 16:
            raise ValueError(f"{n - pos} bytes left at offset {pos}, too few for a section 0")
        if data[pos:pos + 4] != b"GRIB":
            raise ValueError(f"no 'GRIB' at offset {pos}")
        if data[pos + 7] != 2:
            raise ValueError(f"edition {data[pos + 7]} at offset {pos}, not 2")
        length = int.from_bytes(data[pos + 8:pos + 16], "big")
        if length < 20 or pos + length > n:
            raise ValueError(f"total length {length} at offset {pos} does not fit a file of {n} bytes")
        if data[pos + length - 4:pos + length] != b"7777":
            raise ValueError(f"no '7777' at the end of the message at offset {pos} (length {length})")
        out.append((pos, length))
        pos += length
    if not out or pos != n:
        raise ValueError(f"the walk ended at byte {pos}, not at the file's end ({n})")
    return out


def process_whole_file(fetcher, cycle, fh, positions, geom, trigger):
    """D86.2: the whole-file fallback for one GRIB file whose .idx ranges give a
    persistently broken body. Downloads the whole file (one at a time across all
    workers, in memory only), walks its GRIB headers, and for each planned field
    applies check_message to every walked message: exactly one must pass. That
    message's values are used, with status "ok (whole file)". If the walk fails,
    every planned field is "check failed"; so is a field with none or more than
    one passing message. Fields absent by design stay so. Returns (manifest
    rows, {field: values}) as process_file does, and adds one record to
    fetcher.whole."""
    valid = cycle + dt.timedelta(hours=fh)
    url = file_url(cycle, fh)
    planned = [f for f in FIELDS if selector(f[3], fh) is not None]
    passes = {f[0]: [] for f in planned}
    chosen = {}
    with _whole_lock:
        data = fetcher.get_whole(url)
        size = len(data)
        try:
            walk, walk_err = walk_messages(data), None
        except ValueError as e:
            walk, walk_err = None, str(e)
        for off, n in walk or []:
            with _ec_lock:
                gid = ec.codes_new_from_message(data[off:off + n])
                try:
                    for name, var, level, kind, ident in planned:
                        try:
                            got_vals = check_message(gid, ident, expected_steps(kind, fh), cycle, valid,
                                                     positions, geom)
                        except GuardError:
                            raise
                        except Exception:  # noqa: BLE001
                            continue
                        passes[name].append(off)
                        step_range = ec.codes_get_string(gid, "stepRange")
                        ptype = ec.codes_get_string(gid, "stepType")
                        if ec.codes_is_defined(gid, "typeOfStatisticalProcessing"):
                            ptype += (f" (typeOfStatisticalProcessing "
                                      f"{ec.codes_get_long(gid, 'typeOfStatisticalProcessing')})")
                        chosen[name] = (off, n, step_range, ptype, got_vals,
                                        hashlib.sha256(data[off:off + n]).hexdigest())
                finally:
                    ec.codes_release(gid)
        del data
    n_walk = len(walk) if walk is not None else None
    man, vals = [], {}
    for name, var, level, kind, ident in FIELDS:
        base = [iso(cycle), fh, name]
        if selector(kind, fh) is None:
            man.append(base + ["", "", "", "absent by design", "", "", f"GFS gives no {kind} {var} at f000"])
            continue
        if walk is None:
            man.append(base + ["", "", "", "check failed", "", "",
                               f"whole file ({size} B): the header walk failed: {walk_err}; trigger: {trigger}"])
            continue
        k = len(passes[name])
        if k != 1:
            man.append(base + ["", "", "", "check failed", "", "",
                               f"whole file ({size} B, {n_walk} messages walked): {k} messages pass the check, "
                               f"not exactly 1; trigger: {trigger}"])
            continue
        off, n, step_range, ptype, got_vals, _ = chosen[name]
        man.append(base + ["", f"{off}-{off + n - 1}", n, STATUS_WHOLE, step_range, ptype,
                           f"whole file ({size} B, {n_walk} messages walked; range is within the file); "
                           f"trigger: {trigger}"])
        vals[name] = got_vals
    with fetcher.lock:
        fetcher.whole.append({
            "url": url, "cycle": iso(cycle), "fh": fh, "bytes": size, "trigger": trigger,
            "walked": n_walk, "walk_error": walk_err, "ends_at_last_byte": walk is not None,
            "passes": {name: len(v) for name, v in passes.items()},
            "selected": {name: {"offset": c[0], "length": c[1], "sha256": c[5]} for name, c in chosen.items()
                         if len(passes[name]) == 1},
            "ok_whole": len(vals)})
    return man, vals


def process_file(fetcher, cycle, fh, positions, geom, spot=None):
    """Fetches the .idx and every needed message of one GRIB file, checks each
    message and reads the 4 values per airport by grid index. Returns
    (manifest rows, {field: [value or None] * (4 * airports)}, spot results).
    Raises DownloadError, BudgetStop or GuardError, which stop the chunk."""
    check_request(cycle, fh)
    valid = cycle + dt.timedelta(hours=fh)
    url = file_url(cycle, fh)
    man, vals, spot_out = [], {}, []
    try:
        rows = parse_idx(fetcher.get(url + ".idx", "idx").decode("ascii"))
        idx_err = None
    except NotFound:
        rows, idx_err = None, "idx missing (HTTP 404)"
    except (ValueError, IndexError, UnicodeDecodeError) as e:
        rows, idx_err = None, f"unreadable idx: {e!r}"
    for name, var, level, kind, ident in FIELDS:
        step = selector(kind, fh)
        base = [iso(cycle), fh, name]
        if step is None:
            man.append(base + ["", "", "", "absent by design", "", "", f"GFS gives no {kind} {var} at f000"])
            continue
        if rows is None:
            st = "idx missing" if idx_err.startswith("idx missing") else "check failed"
            man.append(base + ["", "", "", st, "", "", idx_err])
            continue
        try:
            rng, exp, line = find_range(rows, var, level, step, cycle)
        except ValueError as e:
            man.append(base + ["", "", "", "check failed", "", "", str(e)])
            continue
        try:
            data = fetcher.get(url, "message", rng, exp)
        except NotFound:
            raise DownloadError(f"{url} {rng}: HTTP 404 for a message listed in its .idx")
        except BrokenBody as e:
            # D86.2: the .idx does not describe this file. Every planned field,
            # including any already read by range, comes from the whole file.
            man, vals = process_whole_file(fetcher, cycle, fh, positions, geom, f"{name} {rng}: {e}")
            return man, vals, []
        stype, s0, s1 = expected_steps(kind, fh)
        status, reason, step_range, ptype, got_vals = "ok", "", "", "", None
        with _ec_lock:
            gid = ec.codes_new_from_message(data)
            try:
                step_range = ec.codes_get_string(gid, "stepRange")
                ptype = ec.codes_get_string(gid, "stepType")
                if ec.codes_is_defined(gid, "typeOfStatisticalProcessing"):
                    ptype += f" (typeOfStatisticalProcessing {ec.codes_get_long(gid, 'typeOfStatisticalProcessing')})"
                got_vals = check_message(gid, ident, (stype, s0, s1), cycle, valid, positions, geom)
            except GuardError:
                ec.codes_release(gid)
                raise
            except Exception as e:  # noqa: BLE001
                status, reason = "check failed", repr(e)
            try:
                # The spot check (session 91, Step 6.3) sits outside the message
                # checks, so an error in it stops the run instead of marking data.
                if spot is not None and got_vals is not None:
                    for k, p in enumerate(positions):
                        if p["icao"] not in spot["icao"]:
                            continue
                        lat, lon = float(p["lat_used"]), float(p["lon_used"])
                        lon_q = lon + 360.0 if lon < 0 else lon
                        nb = ec.codes_grib_find_nearest(gid, lat, lon_q, npoints=4)
                        same_idx = [int(n.index) for n in nb] == p["indices"]
                        same_val = [float(n.value) for n in nb] == got_vals[4 * k:4 * k + 4]
                        spot_out.append((name, iso(cycle), fh, p["icao"], same_idx, same_val))
            finally:
                ec.codes_release(gid)
        del data
        man.append(base + [line, rng, exp if exp is not None else "", status, step_range, ptype, reason])
        if status == "ok" and got_vals is not None:
            vals[name] = got_vals
    return man, vals, spot_out


def write_gz(path, text):
    with open(path, "xb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            gz.write(text.encode("utf-8"))


def run_chunk(args):
    t0 = time.time()
    started = now_utc()
    hours = parse_hours(args.hours)
    if bool(args.month) == bool(args.dates):
        raise GuardError("give exactly one of --month or --dates")
    if args.month:
        y, m = parse_month(args.month)
        cycles, name = month_cycles(y, m), f"{y}-{m:02d}"
    else:
        days = [dt.date.fromisoformat(s) for s in args.dates.split(",")]
        cycles, name = [dt.datetime(d.year, d.month, d.day, h) for d in days for h in CYCLES], "test"
    out = Path(args.out)
    files = [out / f"gfs_points_{name}.csv.gz", out / f"manifest_{name}.csv.gz", out / f"chunk_{name}.meta.txt"]
    check_out_free(files)
    plan = plan_chunk(cycles, hours)
    units = [(c, fh) for c, fhs in plan for fh in fhs]
    positions, geom = read_positions()
    spot = None
    if args.spot_check:
        spot = {"icao": set(args.spot_check.split(",")), "unit": units[-1] if plan else None}
    print(f"SESSION 91 --chunk {name}: hours {hours[0]}-{hours[1]}; {len(plan)} cycles; {len(units)} files; "
          f"{sum(expected_messages(fh) for _, fh in units)} expected messages; {len(positions)} airports; "
          f"workers {args.workers}; budget {args.budget_bytes or 'none'}")
    if not units:
        raise GuardError("nothing to request")
    print(f"first cycle {iso(plan[0][0])}, last cycle {iso(plan[-1][0])}; "
          f"valid {iso(min(c + dt.timedelta(hours=f) for c, f in units))} to "
          f"{iso(max(c + dt.timedelta(hours=f) for c, f in units))}")
    fetcher = Fetcher(args.budget_bytes)
    results, spots = {}, []
    ex = ThreadPoolExecutor(max_workers=args.workers)
    futs = {ex.submit(process_file, fetcher, c, fh, positions, geom,
                      spot if spot and (c, fh) == spot["unit"] else None): (c, fh) for c, fh in units}
    done = 0
    try:
        for fut in as_completed(futs):
            results[futs[fut]] = fut.result()
            done += 1
            if done % 50 == 0 or done == len(units):
                print(f"  {done}/{len(units)} files; {sum(fetcher.bytes.values()):,} bytes; "
                      f"{time.time() - t0:,.0f} s; {whole_stats(fetcher)}", flush=True)
    except (DownloadError, BudgetStop, GuardError) as e:
        ex.shutdown(wait=True, cancel_futures=True)
        print(f"\nCHUNK FAILED, NOTHING WRITTEN: {type(e).__name__}: {e}")
        print(f"read before the stop: files done {done} of {len(units)}; requests {fetcher.requests}; "
              f"bytes {fetcher.bytes} (total {sum(fetcher.bytes.values()):,}); retries {fetcher.retries}; "
              f"seconds {time.time() - t0:,.0f}; {whole_stats(fetcher)}")
        return 2
    ex.shutdown(wait=True)

    man_rows, point_rows = [], []
    for c, fh in units:
        m, vals, sp = results[(c, fh)]
        man_rows += m
        spots += sp
        valid = c + dt.timedelta(hours=fh)
        for k, p in enumerate(positions):
            row = [iso(c), fh, iso(valid), p["icao"]]
            for f_ in FIELD_NAMES:
                v = vals.get(f_)
                row += ([repr(x) for x in v[4 * k:4 * k + 4]] if v is not None else ["", "", "", ""])
            point_rows.append(row)
    counts = {s: sum(1 for r in man_rows if r[6] == s) for s in STATUSES}
    for p_ in files:     # check again just before writing
        if p_.exists():
            raise GuardError(f"{p_} appeared during the run; not writing over it")
    out.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(POINT_COLS)
    w.writerows(point_rows)
    write_gz(files[0], buf.getvalue())
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(MAN_COLS)
    w.writerows(man_rows)
    write_gz(files[1], buf.getvalue())
    secs = time.time() - t0
    meta = [f"stage C GRIB pull, chunk {name} (DECISIONS D82.4, D83.5)",
            f"run start (UTC)   : {started}", f"run end (UTC)     : {now_utc()}", f"seconds           : {secs:.1f}",
            f"arguments         : {' '.join(sys.argv[1:])}",
            f"cycles            : {len(plan)} ({iso(plan[0][0])} to {iso(plan[-1][0])})",
            f"files             : {len(units)}",
            f"messages          : {len(man_rows)} manifest rows; " + "; ".join(f"{s} {n}" for s, n in counts.items()),
            f"points rows       : {len(point_rows)} ({len(units)} files x {len(positions)} airports)",
            f"requests          : idx {fetcher.requests['idx']}, message {fetcher.requests['message']}, "
            f"whole file {fetcher.requests['whole']}; retries {fetcher.retries}; HTTP 404 {fetcher.not_found}",
            f"bytes downloaded  : idx {fetcher.bytes['idx']:,}, message {fetcher.bytes['message']:,}, "
            f"whole file {fetcher.bytes['whole']:,}, total {sum(fetcher.bytes.values()):,}",
            f"whole-file fallback (D86.2): {whole_stats(fetcher)}"]
    for rec in sorted(fetcher.whole, key=lambda r: (r["cycle"], r["fh"])):
        meta.append(f"  fallback {rec['cycle']} f{rec['fh']:03d}: {rec['bytes']:,} B; messages walked "
                    f"{rec['walked']}; ends at last byte {rec['ends_at_last_byte']}; ok (whole file) {rec['ok_whole']}"
                    + (f"; walk error {rec['walk_error']}" if rec["walk_error"] else ""))
    meta += [f"{files[0].name} sha256 {sha256_file(files[0])} ({files[0].stat().st_size:,} B)",
            f"{files[1].name} sha256 {sha256_file(files[1])} ({files[1].stat().st_size:,} B)",
            f"script sha256     : {sha256_file(Path(__file__))} (scripts/session91_grib_pull.py)",
            f"positions sha256  : {sha256_file(POSITIONS)} ({POSITIONS.name})",
            f"packages          : {versions()}",
            f"source            : {BUCKET}/gfs.YYYYMMDD/HH/atmos/gfs.tHHz.pgrb2.0p25.fFFF (+ .idx), byte ranges as "
            "in the manifest (for \"ok (whole file)\", the range within the whole file)"]
    if spot is not None:
        meta.append("spot check (values read by grid index vs codes_grib_find_nearest's four values): "
                    + "; ".join(f"{n} {c} f{f:03d} {i}: indices equal {a}, values equal {b}" for n, c, f, i, a, b in spots))
    with open(files[2], "x") as fh_:
        fh_.write("\n".join(meta) + "\n")
    print("\n".join(meta))
    return 0


# ------------------------------------------------------------------ --plan

def run_plan(args):
    hours = parse_hours(args.hours)
    print(f"SESSION 91 --plan (offline): forecast hours {hours[0]}-{hours[1]}; window "
          f"{iso(FIRST_VALID)} to {iso(LAST_VALID)}; last cycle {iso(LAST_CYCLE)}")
    print("absent by design (Step 2): dswrf, tmax2m, tmin2m at f000; every other field at every hour")
    print(f"{'month':7s} {'first cycle':17s} {'last cycle':17s} {'cycles':>6s} {'files':>6s} {'messages':>8s} "
          f"{'earliest valid':17s} {'latest valid':17s}")
    tot = [0, 0, 0]
    lo = hi = None
    outside = 0
    for y, m in all_months():
        plan = plan_chunk(month_cycles(y, m), hours)
        units = [(c, fh) for c, fhs in plan for fh in fhs]
        vt = [c + dt.timedelta(hours=fh) for c, fh in units]
        outside += sum(1 for v in vt if v < FIRST_VALID or v > LAST_VALID)
        msgs = sum(expected_messages(fh) for _, fh in units)
        print(f"{y}-{m:02d} {iso(plan[0][0]):17s} {iso(plan[-1][0]):17s} {len(plan):>6d} {len(units):>6d} "
              f"{msgs:>8d} {iso(min(vt)):17s} {iso(max(vt)):17s}")
        tot[0] += len(plan)
        tot[1] += len(units)
        tot[2] += msgs
        lo = min(vt) if lo is None else min(lo, min(vt))
        hi = max(vt) if hi is None else max(hi, max(vt))
    print(f"{'total':7s} {'':17s} {'':17s} {tot[0]:>6d} {tot[1]:>6d} {tot[2]:>8d} {iso(lo):17s} {iso(hi):17s}")
    print(f"valid times outside the window: {outside}")
    return 0 if outside == 0 else 1


# ------------------------------------------------------------------ --guard-check

def run_guard_check(args):
    print("SESSION 91 --guard-check (offline: no network call, no data read)")
    ok_all = True

    def case(label, fn, expect_refused):
        nonlocal ok_all
        try:
            fn()
            refused, why = False, ""
        except GuardError as e:
            refused, why = True, str(e)
        good = refused == expect_refused
        ok_all &= good
        print(f"  [{'OK ' if good else 'BAD'}] {label}: {'REFUSED' if refused else 'allowed'}"
              + (f" ({why})" if why else ""))

    case("cycle 2026-07-31T18 f006 (valid 2026-08-01T00)",
         lambda: check_request(dt.datetime(2026, 7, 31, 18), 6), True)
    case("cycle 2026-08-01T00 f000", lambda: check_request(dt.datetime(2026, 8, 1, 0), 0), True)
    case("valid 2021-03-23T23 (cycle 2021-03-23T18 f005)",
         lambda: check_request(dt.datetime(2021, 3, 23, 18), 5), True)
    case("--hours 0-49", lambda: parse_hours("0-49"), True)
    tmp = Path(tempfile.mkdtemp(prefix="session91_guard_"))
    try:
        existing = tmp / "gfs_points_test.csv.gz"
        existing.write_bytes(b"")
        case("writing over an existing output file", lambda: check_out_free([existing]), True)
        case("writing to an absent output file", lambda: check_out_free([tmp / "absent.csv.gz"]), False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    case("cycle 2026-07-31T18 f005 (valid 2026-07-31T23)",
         lambda: check_request(dt.datetime(2026, 7, 31, 18), 5), False)
    case("cycle 2021-03-23T00 f024 (valid 2021-03-24T00)",
         lambda: check_request(dt.datetime(2021, 3, 23, 0), 24), False)
    case("--month 2026-08", lambda: parse_month("2026-08"), True)
    case("--chunk --dates 2026-08-01 (cycles after the last)",
         lambda: plan_chunk([dt.datetime(2026, 8, 1, h) for h in CYCLES], (0, 24)), True)
    print(f"temporary directory deleted: {not tmp.exists()}")
    print("all cases behaved as specified" if ok_all else "A CASE DID NOT BEHAVE: FIX THE SCRIPT")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ --gate (D83.6)

def derive(a, target_date, got):
    """The seven compared columns, with the record's rounding order (SPEC 8.8 G4,
    G5, G7). Copied from session86_forward_build.py l.559-594 (itself from
    session76_build.py l.155-198 and session55_radiation_pull.py l.541-562),
    without the season columns and without the finiteness check of the five
    fields this pull does not hold (t925, t700, rh2m, spfh2m, pres_sfc)."""
    corr, lead = a["correction_c"], a["lead"]
    tg = round((got["tmp2m"] - 273.15) + corr, 3)
    cc = round(got["tcdc"], 3)
    ws = round(((got["ugrd10m"] ** 2 + got["vgrd10m"] ** 2) ** 0.5) * 3.6, 3)
    t2m_raw = round(tg - corr, 3)
    lapse = round(t2m_raw - (got["t850"] - 273.15), 3)
    dd = round(t2m_raw - (got["dpt2m"] - 273.15), 3)
    msl = round(got["prmsl"] / 100.0, 3)
    m3 = round(got["prmsl_m3"] / 100.0, 3)
    tend = round(msl - m3, 3)
    if lead - window_start(lead) == 2:
        dswrf_2h = round(got["dswrf"], 3)
    else:
        dur_full = lead - window_start(lead)
        dur_partial = (lead - 2) - window_start(lead - 2)
        dswrf_2h = round((got["dswrf"] * dur_full - got["dswrf_m2"] * dur_partial) / 2.0, 3)
    row = {"temperature_grib_c": tg, "cloud_cover": cc, "wind_speed_10m": ws,
           "dewpoint_depression_t2m_floored": max(dd, 0.0), "lapse_rate_t2_t850": lapse,
           "pressure_tendency_3h_hpa": tend, "dswrf_2h_wm2": dswrf_2h}
    for c, v in row.items():
        if not math.isfinite(v):
            raise ValueError(f"non-finite {c}")
    return row


def bilinear_stored(p, vals):
    """The record's bilinear (bilinear_from_gid above, SPEC 8.8 G6) on the 4
    stored values, with the stored points' latitude and longitude and the
    position used. Same arithmetic and term order."""
    lats = sorted(set(round(q[0], 6) for q in p["pts"]))
    lons = sorted(set(round(q[1], 6) for q in p["pts"]))
    lat, lon = p["lat"], p["lon"]
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        raise ValueError("unexpected neighbour layout")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(q[0], 6), round(q[1], 6)): v for q, v in zip(p["pts"], vals)}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    return ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
            + dlat * (1 - dlon) * v10 + dlat * dlon * v11)


def run_gate(args):
    print("SESSION 91 --gate (offline; reads a finished chunk's files and committed files only)")
    ext = Path(args.extract)
    pts_files = sorted(ext.glob("gfs_points_*.csv.gz"))
    if len(pts_files) != 1:
        raise SystemExit(f"STOP: expected one gfs_points_*.csv.gz in {ext}")
    name = pts_files[0].name[len("gfs_points_"):-len(".csv.gz")]
    meta_txt = (ext / f"chunk_{name}.meta.txt").read_text()
    pos_sha = sha256_file(POSITIONS)
    print(f"chunk {name}; positions file SHA-256 {pos_sha}; recorded in the chunk's meta: {pos_sha in meta_txt}")
    if pos_sha not in meta_txt:
        raise SystemExit("STOP: the chunk was not made with this positions file")
    m = re.search(r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`",
                  DECISIONS_FILE.read_text())
    have = sha256_file(TRAINING_SET)
    print(f"training set SHA-256 {have}; F122.3 {m.group(1)}; equal: {have == m.group(1)}")
    if have != m.group(1):
        raise SystemExit("STOP: the training set differs from F122.3")
    airports = load_airports()
    positions, _ = read_positions()
    pos = {p["icao"]: p for p in positions}
    for p in positions:
        p["lat"], p["lon"] = float(p["lat_used"]), float(p["lon_used"])
        p["pts"] = [(float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"])) for k in (1, 2, 3, 4)]
    for st, a in airports.items():
        p = pos[DEV[st]]
        if (p["lat"], p["lon"]) != (a["grid_lat"], a["grid_lon"]) or p["role"] != "development":
            raise SystemExit(f"STOP: {st}'s position in the positions file is not SPEC 3.4's grid point")
    with gzip.open(pts_files[0], "rt") as f:
        points = {(r["cycle_utc"], int(r["fhour"]), r["icao"]): r for r in csv.DictReader(f)}
    with open(TRAINING_SET) as f:
        training = {(r["station"], r["target_date"]): r for r in csv.DictReader(f)}
    need = {"tmp2m": ("t2m", 0), "tcdc": ("tcdc", 0), "ugrd10m": ("u10", 0), "vgrd10m": ("v10", 0),
            "t850": ("t850", 0), "dpt2m": ("d2m", 0), "prmsl": ("prmsl", 0), "prmsl_m3": ("prmsl", -3),
            "dswrf": ("dswrf", 0), "dswrf_m2": ("dswrf", -2)}
    passed = {st: {c: [0, 0] for c in GATE_COLS} for st in airports}
    mism, no_row, not_built = [], [], []
    print(f"\n{'station':7s} {'target date':11s} {'cycle':17s} {'lead':>4s}  result")
    for st, a in airports.items():
        p = pos[DEV[st]]
        for d in GATE_DATES:
            cycle = dt.datetime(d.year, d.month, d.day, a["cycle"]) - dt.timedelta(days=1)
            com = training.get((st, d.isoformat()))
            if com is None:
                no_row.append((st, d))
                print(f"{st:7s} {d}  {iso(cycle):17s} f{a['lead']:03d}  no committed row")
                continue
            got = {}
            try:
                for key, (fname, off) in need.items():
                    if key == "dswrf_m2" and a["lead"] - window_start(a["lead"]) == 2:
                        continue
                    r = points[(iso(cycle), a["lead"] + off, p["icao"])]
                    raw = [r[f"{fname}_{k}"] for k in (1, 2, 3, 4)]
                    if "" in raw:
                        raise ValueError(f"{fname} at f{a['lead'] + off:03d} is empty in the extract")
                    got[key] = bilinear_stored(p, [float(x) for x in raw])
                reb = derive(a, d, got)
            except (KeyError, ValueError) as e:
                not_built.append((st, d, repr(e)))
                print(f"{st:7s} {d}  {iso(cycle):17s} f{a['lead']:03d}  NOT REBUILT: {e!r}")
                continue
            bad = []
            for c in GATE_COLS:
                passed[st][c][1] += 1
                cv = float(com[c])
                if cv == reb[c]:
                    passed[st][c][0] += 1
                else:
                    bad.append(c)
                    mism.append((st, d, c, cv, reb[c]))
            print(f"{st:7s} {d}  {iso(cycle):17s} f{a['lead']:03d}  "
                  + ("all 7 columns equal" if not bad else "MISMATCH in " + ", ".join(bad)))
    print("\npass table by column (exact equality, no tolerance):")
    for c in GATE_COLS:
        print(f"  {c:34s} {sum(passed[s][c][0] for s in airports)} of {sum(passed[s][c][1] for s in airports)}")
    print("pass table by airport (station-days with all 7 columns equal, and values equal):")
    for st in airports:
        vals_ok = sum(passed[st][c][0] for c in GATE_COLS)
        vals_n = sum(passed[st][c][1] for c in GATE_COLS)
        bad_days = len({d for s, d, *_ in mism if s == st})
        n_days = len(GATE_DATES) - len([1 for s, d in no_row if s == st]) - len([1 for s, *_ in not_built if s == st])
        print(f"  {st:5s} ({DEV[st]}): station-days {n_days - bad_days} of {n_days}; values {vals_ok} of {vals_n}")
    print(f"station-days with no committed row: {len(no_row)} {no_row or ''}")
    print(f"station-days not rebuilt: {len(not_built)} {not_built or ''}")
    print(f"mismatches: {len(mism)}")
    for st, d, c, cv, rv in mism:
        print(f"  MISMATCH {st} {d} {c}: committed {cv!r}, rebuilt {rv!r}")
    ok = not mism and not not_built and not no_row
    print("GATE PASSED" if ok else "GATE NOT PASSED")
    return 0 if ok else 1


# ------------------------------------------------------------------ entry point

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--positions", action="store_true")
    g.add_argument("--plan", action="store_true")
    g.add_argument("--chunk", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--guard-check", action="store_true")
    ap.add_argument("--month", help="--chunk: YYYY-MM, by the cycle's initialisation date")
    ap.add_argument("--dates", help="--chunk: cycle dates D1,D2,... (the test chunk), all four cycles each")
    ap.add_argument("--hours", default="0-24", help="--chunk, --plan: forecast hours A-B (0 to 48)")
    ap.add_argument("--out", help="--chunk: output directory")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--budget-bytes", type=int, default=None, help="--chunk: stop cleanly before passing this")
    ap.add_argument("--spot-check", default=None, help="--chunk: ICAO,ICAO for the index-read spot check")
    ap.add_argument("--extract", help="--gate: a finished chunk's directory")
    a = ap.parse_args()
    try:
        if a.positions:
            return run_positions(a)
        if a.plan:
            return run_plan(a)
        if a.chunk:
            if not a.out:
                raise GuardError("--chunk needs --out")
            return run_chunk(a)
        if a.gate:
            return run_gate(a)
        return run_guard_check(a)
    except GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
