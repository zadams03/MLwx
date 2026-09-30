"""Session 86: the 2026-27 forward test's data-build script (DECISIONS D73, D78.7).

It builds the inputs of the forward test (D73) with the same logic as the
record pipelines. For each airport and target day it builds the nine G15
columns (SPEC 8.8), `temperature_grib_c`, the paired observation and the
previous day's paired observation (for persistence).

Modes (exactly one):
  --guard-check  Offline. Calls the date guards only, with fixed cases, and
                 prints each outcome. No network call, no data read.
  --gate         Network, spent years only. Rebuilds a fixed sample of 54
                 spent-year station-days and compares every value with the
                 committed training set (F122). Then checks the frozen F122
                 models give the same predictions on the committed and the
                 rebuilt rows (plumbing check: no error is computed). Writes
                 nothing under data/: GRIB bytes and fresh IEM responses go to
                 a temporary directory outside the repo, deleted at the end.
  --build        2026-27 period A. WRITTEN BUT NOT RUN IN SESSION 86. It builds
                 rows for period A only, prints counts only (never a 2026-27
                 value), and writes only new files (see OUT_* below). It
                 refuses to run if any of them exists.

Where the logic comes from (copied, not imported; each copy names its source):
- the recipe per field: `scripts/session76_grib_pull.py` (fields, byte-range
  fetch from the .idx, identity, run and validity checks, bilinear) and
  `scripts/session76_build.py` (derived columns, rounding order), which are
  the newest copies of `session37_decode.py`, `session40_decode.py`,
  `session49_upper_air_pull.py`, `session51_moisture_pull.py`,
  `session53_pressure_pull.py`, `session55_radiation_pull.py` and
  `session63_reserved_year_build.py`. R's de-accumulation at the lead-24
  airports is `session55_radiation_pull.py` l.517-560.
- the historical observation pairing (gate comparison only):
  `session62_reserved_confirm.py` l.321-344.
- the record's pairing of the observation and the previous-day observation:
  `session62_reserved_confirm.py` l.394-404 (`obs_all.get(date - 1 day)`).
The function-by-function list with line numbers is in DECISIONS F128.

SPEC 8.7 build requirements met here:
1. the observation is paired to the NEAREST usable routine report, explicitly
   (a tie keeps the earlier report, as `session76_build.py` does, and is
   counted);
2. a non-finite value is rejected at load, dropped and counted;
3. each GRIB message's run date and time, and its full validity date AND hour,
   are checked, as are its parameter, level and step;
4. the closing counts compare rows with the expected full count, not zero;
5. no write to any committed record file. `--build` writes new files only,
   with exclusive-create, and refuses to run if any of them exists.

Hard limits: in `--gate`, no valid time on or after 2026-08-01T00:00 UTC may be
requested or kept. Each message's validity is checked before its value is
read; an offending message is discarded unread and the run stops. In `--build`
the limit is 2027-08-01T00:00 UTC. Parallel ("para") data is never requested.
"""

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import re
import shutil
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True

# --- making LightGBM importable on this machine (copied from
# session62_reserved_confirm.py l.89-99; see DECISIONS Q16/D24) -----------------
_SENTINEL = "MLWX_LIBOMP_PATH_SET"
if _SENTINEL not in os.environ:
    _omp = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" \
        / "site-packages" / "sklearn" / ".dylibs"
    if (_omp / "libomp.dylib").exists():
        os.environ[_SENTINEL] = "1"
        os.environ["DYLD_LIBRARY_PATH"] = \
            str(_omp) + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
        os.execv(sys.executable, [sys.executable] + sys.argv)

import eccodes as ec  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT / "SPEC.md"
DECISIONS_FILE = ROOT / "DECISIONS.md"
TRAINING_SET = ROOT / "data" / "processed" / "session81_training_set.csv"
MODEL_DIR = ROOT / "data" / "models" / "session81"
PARAMS_CSVS = [
    ROOT / "data" / "raw" / "diagnostics" / "session37" / "session37_elevation_correction_params.csv",
    ROOT / "data" / "raw" / "diagnostics" / "session76" / "session76_elevation_correction_params.csv",
]

# The files --build writes. All are new; --build refuses to run if any exists.
OUT_ROWS = ROOT / "data" / "processed" / "forward2627_periodA_rows.csv"
OUT_ROWS_META = ROOT / "data" / "processed" / "forward2627_periodA_rows.csv.meta.txt"
OUT_DIAG = ROOT / "data" / "raw" / "diagnostics" / "forward2627"
OUT_MANIFEST = OUT_DIAG / "periodA_grib_manifest.csv"
OUT_DROPS = OUT_DIAG / "periodA_drop_log.csv"
OUT_IEM = ROOT / "data" / "raw" / "iem" / "forward2627"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
IEM_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"

FIRST_DAY = dt.date(2021, 3, 24)
GATE_LAST_DAY = dt.date(2026, 7, 31)          # last spent-year day (SPEC 4.3)
GATE_LIMIT = dt.datetime(2026, 8, 1, 0, 0)    # nothing valid at or after this in --gate
PERIOD_A_START = dt.date(2026, 8, 1)
FORWARD_LAST_DAY = dt.date(2027, 7, 31)
FORWARD_LIMIT = dt.datetime(2027, 8, 1, 0, 0)  # nothing valid at or after this in --build
TOL_MIN = 15                                   # SPEC 4.5, inclusive (8.8 G3)
DAYS_AFTER_LAST = 3                            # D78.7: observations are in

G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
       "pressure_tendency_3h_hpa"]                # SPEC 8.8 G15, record order
ROW_COLS = (["station", "target_date", "target_hour"] + G15
            + ["temperature_grib_c", "obs_c", "prev_obs_c"])
B_COLS = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m", "temperature_grib_c"]
GROUPS = {"B": B_COLS, "L": ["lapse_rate_t2_t850"], "D": ["dewpoint_depression_t2m_floored"],
          "T": ["pressure_tendency_3h_hpa"], "R": ["dswrf_2h_wm2"],
          "obs": ["obs_c"], "prev_obs": ["prev_obs_c"]}

# The fixed gate sample (session prompt 5.1): 9 dates at all 6 airports.
GATE_DATES = [dt.date(2021, 4, 15), dt.date(2022, 1, 10), dt.date(2023, 7, 20),
              dt.date(2023, 10, 5), dt.date(2024, 11, 12), dt.date(2025, 2, 18),
              dt.date(2025, 9, 3), dt.date(2026, 4, 22), dt.date(2026, 7, 31)]
GATE_WINDOWS = {dt.date(2021, 4, 15): "v16 window", dt.date(2022, 1, 10): "v16 window",
                dt.date(2023, 7, 20): "v16 window", dt.date(2023, 10, 5): "v16 window",
                dt.date(2024, 11, 12): "reserved year", dt.date(2025, 2, 18): "reserved year",
                dt.date(2025, 9, 3): "sealed year", dt.date(2026, 4, 22): "sealed year",
                dt.date(2026, 7, 31): "sealed year, last day"}
SIZE_LIMIT_BYTES = 5 * 1024 ** 3

_local = threading.local()
_lock = threading.Lock()
REQUEST_LOG = []          # (pulled_utc, kind, url, byte_range, bytes)


class GuardError(Exception):
    """A date guard fired. The run stops."""


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


def cycle_and_lead(target_hour):
    """SPEC 7.2: the run of day D-1 at floor(H/6)*6, forecast hour 24 + H mod 6."""
    return (target_hour // 6) * 6, 24 + (target_hour % 6)


def window_start(lead):
    """The 6-hour DSWRF average reset mark before a forecast hour
    (session55_radiation_pull.py l.137-141)."""
    return 6 * ((lead - 1) // 6)


def year_fraction(d):
    """Copied from session62_reserved_confirm.py l.217-219."""
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def http():
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
        _local.s.headers.update({"User-Agent": "MLwx/session86"})
    return _local.s


def http_get(url, headers=None, kind="", byte_range=None, pause=0.15):
    """At most 3 tries, spaced. A 404 is final. Every request is logged with
    its pull time. Returns (content, pulled_utc)."""
    last = None
    for attempt in range(1, 4):
        pulled = now_utc()
        try:
            r = http().get(url, headers=headers or {}, timeout=120)
            if r.status_code in (200, 206):
                with _lock:
                    REQUEST_LOG.append((pulled, kind, url, byte_range or "", len(r.content)))
                time.sleep(pause)
                return r.content, pulled
            last = RuntimeError(f"HTTP {r.status_code}")
            if r.status_code not in (429, 500, 502, 503, 504):
                break
        except requests.RequestException as e:
            last = e
        if attempt < 3:
            time.sleep(2.0 * attempt)
    raise RuntimeError(f"failed: {last!r}")


def finite_float(s):
    """SPEC 8.7 item 2: None for a missing or non-finite value."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


# ------------------------------------------------------------------ airports

def load_airports():
    """Per-airport facts from committed files only: SPEC 3.4's two tables (station
    code, target hour, grid point) and the params CSVs (elevation constant)."""
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
                corr[r["station"]] = (float(r["correction_c"]), float(r["lapse_c_per_km"]))
    out = {}
    for st in t1:
        hour = int(t1[st]["target hour (UTC)"].split(":")[0])
        cyc, lead = cycle_and_lead(hour)
        out[st] = {"station": st, "target_hour": hour, "cycle": cyc, "lead": lead,
                   "grid_lat": float(t2[st]["grid latitude"]),
                   "grid_lon": float(t2[st]["grid longitude"]),
                   "grid_elev_m": float(t2[st]["grid elevation"].split()[0]),
                   "reports_at": t2[st]["reports at"], "pairing_offset": t2[st]["pairing offset"],
                   "correction_c": corr[st][0], "lapse": corr[st][1],
                   "r_mode": "native window" if lead - window_start(lead) == 2 else "de-accumulate"}
    if list(out) != ["EGLC", "LFPG", "DSM", "YSDU", "RNO", "SFO"] or set(corr) != set(out):
        raise SystemExit(f"STOP: unexpected airport set {list(out)} / constants {sorted(corr)}")
    return out


def print_airports(airports):
    print("Per-airport parameters (SPEC 3.4 tables and the two params CSVs; nothing typed in):")
    print(f"{'station':7s} {'hour':>4s} {'cycle':>5s} {'lead':>4s} {'grid lat':>11s} {'grid lon':>12s} "
          f"{'grid elev':>9s} {'const degC':>10s} {'reports':>7s} {'offset':>10s}  R at this lead")
    for a in airports.values():
        print(f"{a['station']:7s} {a['target_hour']:>4d} {a['cycle']:>4d}z f{a['lead']:03d} "
              f"{a['grid_lat']:>11.6f} {a['grid_lon']:>12.6f} {a['grid_elev_m']:>8.0f}m "
              f"{a['correction_c']:>+10.4f} {a['reports_at']:>7s} {a['pairing_offset']:>10s}  {a['r_mode']}")


# ------------------------------------------------------------------ the date guards

def check_gate_date(d):
    """--gate hard-stops on any target date after 2026-07-31."""
    if d > GATE_LAST_DAY:
        raise GuardError(f"gate date {d} is after {GATE_LAST_DAY}")


def last_period_a_day(cycle_hour, first_v17):
    """The last target day D whose forecasting cycle (floor(H/6)*6 UTC on D-1)
    is before the first v17 cycle. With no v17 (first_v17 None) it is the last
    day of the forward year. Returns None if no day qualifies."""
    if first_v17 is None:
        return FORWARD_LAST_DAY
    d, last = PERIOD_A_START, None
    while d < dt.date(2028, 1, 1):
        cyc_dt = dt.datetime(d.year, d.month, d.day, cycle_hour) - dt.timedelta(days=1)
        if cyc_dt >= first_v17:
            break
        last, d = d, d + dt.timedelta(days=1)
    return last


def validate_build_request(period, first_v17, no_v17, decision, run_date, airports):
    """The --build guards, as a pure function. Returns (reasons, last_days).
    An empty reasons list means the guards allow the run."""
    reasons, last_days = [], {}
    if period != "A":
        reasons.append("period B needs D73.4's v17 entry first")
    if first_v17 is None and not no_v17:
        reasons.append("needs --first-v17-cycle (from a DECISIONS entry, D73.3) or --no-v17")
    if first_v17 is not None and no_v17:
        reasons.append("--first-v17-cycle and --no-v17 are exclusive")
    if not decision:
        reasons.append("needs --decision <entry number>")
    for st, a in airports.items():
        last = last_period_a_day(a["cycle"], first_v17 if not no_v17 else None)
        last_days[st] = last
        if last is None:
            reasons.append(f"{st}: no period-A day (the first v17 cycle is too early)")
        elif last >= FORWARD_LIMIT.date():
            reasons.append(f"{st}: last period-A target day {last} is on or after {FORWARD_LIMIT.date()}")
    known = [d for d in last_days.values() if d is not None]
    if known and run_date < max(known) + dt.timedelta(days=DAYS_AFTER_LAST):
        reasons.append(f"run date {run_date} is before the latest last day {max(known)} "
                       f"plus {DAYS_AFTER_LAST} days")
    return reasons, last_days


def guard_check():
    print("SESSION 86 --guard-check (offline: no network call, no data read)")
    airports = {"EGLC": {"cycle": 12}, "LFPG": {"cycle": 12}, "DSM": {"cycle": 18},
                "YSDU": {"cycle": 0}, "RNO": {"cycle": 18}, "SFO": {"cycle": 18}}
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
    print("build guards (pure function; nothing is fetched):")
    r, _ = validate_build_request("A", None, False, "D79", today, airports)
    show("--build with no first-v17-cycle and no --no-v17", bool(r), r, True, "needs --first-v17-cycle")
    r, _ = validate_build_request("B", dt.datetime(2026, 11, 15, 0), False, "D79", dt.date(2028, 3, 1), airports)
    show("--build --period B", bool(r), r, True, "period B needs D73.4")
    r, last = validate_build_request("A", dt.datetime(2026, 11, 15, 0), False, "D79", today, airports)
    print("    last period-A day per airport for a first v17 cycle of 2026-11-15T00: "
          + ", ".join(f"{k} {v}" for k, v in last.items()))
    show("--build whose last day + 3 days is after the run date", bool(r), r, True, "before the latest last day")
    r, _ = validate_build_request("A", dt.datetime(2027, 9, 1, 0), False, "D79", dt.date(2028, 3, 1), airports)
    show("--build with a date on or after 2027-08-01 (simulated run date 2028-03-01)", bool(r), r, True,
         "on or after 2027-08-01")
    print("all cases behaved as the session prompt's Step 3.2 says" if ok_all else "A CASE DID NOT BEHAVE: FIX THE SCRIPT")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ GRIB: fields and decode

def field_plan(lead):
    """The messages one target day needs, per SPEC 8.2 and F98, F100 to F102 (the
    same 14 fields session76_grib_pull.py pulls at lead 26, plus R's second
    message at the lead-24 airports). Each: (name, forecast hour, idx var,
    idx level, idx step, identity codes)."""
    L = lead
    fc = f"{L} hour fcst"
    plan = [
        ("tmp2m", L, "TMP", "2 m above ground", fc, (0, 0, 0, 103, 2, "instant", L, L)),
        ("tcdc", L, "TCDC", "entire atmosphere", fc, (0, 6, 1, 10, 0, "instant", L, L)),
        ("ugrd10m", L, "UGRD", "10 m above ground", fc, (0, 2, 2, 103, 10, "instant", L, L)),
        ("vgrd10m", L, "VGRD", "10 m above ground", fc, (0, 2, 3, 103, 10, "instant", L, L)),
        ("t925", L, "TMP", "925 mb", fc, (0, 0, 0, 100, 925, "instant", L, L)),
        ("t850", L, "TMP", "850 mb", fc, (0, 0, 0, 100, 850, "instant", L, L)),
        ("t700", L, "TMP", "700 mb", fc, (0, 0, 0, 100, 700, "instant", L, L)),
        ("rh2m", L, "RH", "2 m above ground", fc, (0, 1, 1, 103, 2, "instant", L, L)),
        ("dpt2m", L, "DPT", "2 m above ground", fc, (0, 0, 6, 103, 2, "instant", L, L)),
        ("spfh2m", L, "SPFH", "2 m above ground", fc, (0, 1, 0, 103, 2, "instant", L, L)),
        ("prmsl", L, "PRMSL", "mean sea level", fc, (0, 3, 1, 101, 0, "instant", L, L)),
        ("pres_sfc", L, "PRES", "surface", fc, (0, 3, 0, 1, 0, "instant", L, L)),
        ("prmsl_m3", L - 3, "PRMSL", "mean sea level", f"{L - 3} hour fcst",
         (0, 3, 1, 101, 0, "instant", L - 3, L - 3)),
    ]
    ws = window_start(L)
    plan.append(("dswrf", L, "DSWRF", "surface", f"{ws}-{L} hour ave fcst", (0, 4, 192, 1, 0, "avg", ws, L)))
    if L - ws != 2:           # lead 24: also the 18-22 h average (F102)
        ws2 = window_start(L - 2)
        plan.append(("dswrf_m2", L - 2, "DSWRF", "surface", f"{ws2}-{L - 2} hour ave fcst",
                     (0, 4, 192, 1, 0, "avg", ws2, L - 2)))
    return plan


def file_url(run_date, cycle, fh):
    return f"{BUCKET}/gfs.{run_date:%Y%m%d}/{cycle:02d}/atmos/gfs.t{cycle:02d}z.pgrb2.0p25.f{fh:03d}"


def parse_idx(text):
    rows = []
    for line in text.strip().splitlines():
        p = line.split(":")
        rows.append({"offset": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5]})
    return rows


def find_range(rows, var, level, step, run_date, cycle):
    """Copied from session76_grib_pull.py l.167-177: exactly one idx line, with
    the run stamp checked."""
    hits = [i for i, r in enumerate(rows) if r["var"] == var and r["level"] == level and r["step"] == step]
    if len(hits) != 1:
        raise RuntimeError(f"expected 1 idx line for {var}:{level}:{step}, found {len(hits)}")
    i = hits[0]
    if rows[i]["d"] != f"d={run_date:%Y%m%d}{cycle:02d}":
        raise RuntimeError(f"idx run stamp {rows[i]['d']} does not match the run")
    start = rows[i]["offset"]
    if i + 1 < len(rows):
        return f"{start}-{rows[i + 1]['offset'] - 1}", rows[i + 1]["offset"] - start
    return f"{start}-", None


def bilinear_from_gid(gid, lat, lon):
    """Copied from session76_grib_pull.py l.180-207 (itself the record's
    session49_upper_air_pull.py l.148-171, SPEC 8.8 G6), with SPEC 8.7 item 2:
    each neighbour value must be finite and not the message's missing value."""
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


def decode(data, identity, run_date, cycle, fh, lat, lon, valid_limit):
    """Checks the message's identity, run, and full validity date and hour
    (SPEC 8.7 item 3), and the validity limit BEFORE any value is read, then
    interpolates. Adapted from session76_grib_pull.py l.210-233."""
    gid = ec.codes_new_from_message(data)
    try:
        got = (ec.codes_get_long(gid, "discipline"), ec.codes_get_long(gid, "parameterCategory"),
               ec.codes_get_long(gid, "parameterNumber"), ec.codes_get_long(gid, "typeOfFirstFixedSurface"),
               ec.codes_get_long(gid, "level"), ec.codes_get_string(gid, "stepType"),
               ec.codes_get_long(gid, "startStep"), ec.codes_get_long(gid, "endStep"))
        if got != identity:
            raise ValueError(f"identity {got} != expected {identity}")
        if (ec.codes_get_long(gid, "dataDate") != int(f"{run_date:%Y%m%d}")
                or ec.codes_get_long(gid, "dataTime") != cycle * 100):
            raise ValueError("run date/time mismatch")
        valid = dt.datetime(run_date.year, run_date.month, run_date.day, cycle) + dt.timedelta(hours=fh)
        vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
        if vd != int(f"{valid:%Y%m%d}") or vt != valid.hour * 100:
            raise ValueError(f"validity {vd} {vt:04d} != expected {valid:%Y%m%d %H%M}")
        got_valid = dt.datetime(vd // 10000, (vd // 100) % 100, vd % 100, vt // 100, vt % 100)
        if got_valid >= valid_limit:
            raise GuardError(f"a message is valid at {got_valid:%Y-%m-%d %H:%M}, on or after "
                             f"{valid_limit:%Y-%m-%d %H:%M}; discarded unread")
        value = bilinear_from_gid(gid, lat, lon)
        if not math.isfinite(value):
            raise ValueError("non-finite interpolated value")
        return value
    finally:
        ec.codes_release(gid)


def fetch_message(url, byte_range, expected_len, kind):
    data, pulled = http_get(url, headers={"Range": f"bytes={byte_range}"}, kind=kind, byte_range=byte_range)
    if expected_len is not None and len(data) != expected_len:
        raise RuntimeError(f"got {len(data)} bytes, expected {expected_len}")
    if data[:4] != b"GRIB" or data[-4:] != b"7777":
        raise RuntimeError("bad magic markers (not a complete GRIB2 message)")
    return data, pulled


def pull_station_day(a, target_date, valid_limit, first_v17):
    """Fetch, check and decode every message one target day needs, for one
    airport. Nothing is kept on disk. Returns (values, manifest_rows, failures)
    where values maps field name to the interpolated value (GRIB units) and
    failures maps field name to a reason. A GuardError propagates."""
    if dt.datetime(target_date.year, target_date.month, target_date.day, a["target_hour"]) >= valid_limit:
        raise GuardError(f"target {target_date} is on or after {valid_limit}")
    run_date = target_date - dt.timedelta(days=1)
    cycle = a["cycle"]
    if first_v17 is not None and dt.datetime(run_date.year, run_date.month, run_date.day, cycle) >= first_v17:
        raise GuardError(f"cycle {run_date} {cycle:02d}z is at or after the first v17 cycle")
    plan = field_plan(a["lead"])
    idx, values, man, fails = {}, {}, [], {}
    for fh in sorted({p[1] for p in plan}):
        url = file_url(run_date, cycle, fh) + ".idx"
        try:
            raw, pulled = http_get(url, kind="idx")
            text = raw.decode("ascii")
            if not text.startswith("1:0:"):
                raise RuntimeError("idx does not start with '1:0:'")
            idx[fh] = (parse_idx(text), sha256_bytes(raw), url, None)
        except GuardError:
            raise
        except Exception as e:  # noqa: BLE001
            idx[fh] = (None, "", url, repr(e))
    for name, fh, var, level, step, identity in plan:
        url = file_url(run_date, cycle, fh)
        base = [a["station"], target_date.isoformat(), name, run_date.isoformat(), cycle, fh, var, level, step, url]
        rows, idx_sha, idx_url, idx_err = idx[fh]
        if rows is None:
            fails[name] = f"idx: {idx_err}"
            man.append(base + ["", idx_url, "", now_utc(), "", "", "FAIL", fails[name]])
            continue
        try:
            byte_range, expected = find_range(rows, var, level, step, run_date, cycle)
        except Exception as e:  # noqa: BLE001
            fails[name] = repr(e)
            man.append(base + ["", idx_url, idx_sha, now_utc(), "", "", "FAIL", fails[name]])
            continue
        pulled = now_utc()
        try:
            data, pulled = fetch_message(url, byte_range, expected, "message")
        except Exception as e:  # noqa: BLE001
            fails[name] = f"fetch: {e!r}"
            man.append(base + [byte_range, idx_url, idx_sha, pulled, "", "", "FAIL", fails[name]])
            continue
        digest = sha256_bytes(data)
        try:
            values[name] = decode(data, identity, run_date, cycle, fh, a["grid_lat"], a["grid_lon"], valid_limit)
        except GuardError:
            raise
        except Exception as e:  # noqa: BLE001
            fails[name] = f"decode: {e!r}"
            man.append(base + [byte_range, idx_url, idx_sha, pulled, len(data), digest, "FAIL", fails[name]])
            continue
        man.append(base + [byte_range, idx_url, idx_sha, pulled, len(data), digest, "OK", ""])
    return values, man, fails


MAN_COLS = ["station", "target_date", "field", "run_date", "cycle", "fhour", "variable", "level", "idx_step",
            "url", "byte_range", "idx_url", "idx_sha256", "pulled_utc", "bytes", "sha256", "status", "detail"]


# ------------------------------------------------------------------ derived columns

def derive(a, target_date, got):
    """The nine G15 columns and temperature_grib_c from the decoded GRIB values,
    with the record's rounding order (SPEC 8.8 G4, G5, G7). Copied from
    session76_build.py l.155-198, with R's de-accumulation at the lead-24
    airports from session55_radiation_pull.py l.541-562. Raises ValueError if
    any result is not finite (SPEC 8.7 item 2)."""
    corr, lead = a["correction_c"], a["lead"]
    ang = 2 * math.pi * year_fraction(target_date)
    tg = round((got["tmp2m"] - 273.15) + corr, 3)
    cc = round(got["tcdc"], 3)
    ws = round(((got["ugrd10m"] ** 2 + got["vgrd10m"] ** 2) ** 0.5) * 3.6, 3)
    t2m_raw = round(tg - corr, 3)
    lapse = round(t2m_raw - (got["t850"] - 273.15), 3)
    dd = round(t2m_raw - (got["dpt2m"] - 273.15), 3)
    msl = round(got["prmsl"] / 100.0, 3)
    m3 = round(got["prmsl_m3"] / 100.0, 3)
    tend = round(msl - m3, 3)
    if a["r_mode"] == "native window":
        dswrf_2h = round(got["dswrf"], 3)
    else:
        dur_full = lead - window_start(lead)
        dur_partial = (lead - 2) - window_start(lead - 2)
        dswrf_2h = round((got["dswrf"] * dur_full - got["dswrf_m2"] * dur_partial) / 2.0, 3)
    row = {"station": a["station"], "target_date": target_date.isoformat(), "target_hour": a["target_hour"],
           "temp": tg, "season_sin": math.sin(ang), "season_cos": math.cos(ang), "cloud_cover": cc,
           "wind_speed_10m": ws, "dewpoint_depression_t2m_floored": max(dd, 0.0),
           "lapse_rate_t2_t850": lapse, "dswrf_2h_wm2": dswrf_2h, "pressure_tendency_3h_hpa": tend,
           "temperature_grib_c": tg}
    # the other decoded messages must be finite too (they gate the row, as in the record)
    for k in ("t925", "t700", "rh2m", "spfh2m", "pres_sfc"):
        if not math.isfinite(got[k]):
            raise ValueError(f"non-finite {k}")
    for c in G15 + ["temperature_grib_c"]:
        if not math.isfinite(row[c]):
            raise ValueError(f"non-finite {c}")
    return row


# ------------------------------------------------------------------ observations

def iem_query(station, first_day, last_day):
    """The record's query form (see any data/raw/iem_asos_*.meta.txt): report_type=3,
    UTC, and an exclusive end date, so the request ends after last_day."""
    end = last_day + dt.timedelta(days=1)
    return (f"{IEM_URL}?station={station}&data=tmpc&data=dwpc"
            f"&year1={first_day.year}&month1={first_day.month}&day1={first_day.day}"
            f"&year2={end.year}&month2={end.month}&day2={end.day}"
            "&tz=UTC&format=onlycomma&latlon=yes&elev=yes&missing=M&trace=T&direct=no&report_type=3")


def fetch_iem(station, first_day, last_day, valid_limit):
    """One IEM request. Every returned `valid` is checked against the limit
    BEFORE any temperature is read. Returns (text, url, pulled_utc)."""
    url = iem_query(station, first_day, last_day)
    content, pulled = http_get(url, kind="iem", pause=1.5)
    text = content.decode("utf-8")
    for r in csv.DictReader(io.StringIO(text)):
        if dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M") >= valid_limit:
            raise GuardError(f"IEM returned a report valid at {r['valid']}, on or after {valid_limit}; "
                             "discarded unread")
    return text, url, pulled


def parse_reports(text, station, stats):
    """Reports in file order. SPEC 8.7 item 2: non-finite tmpc is rejected and
    counted; a missing tmpc (M, blank, T, None) is unusable (G2)."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        if r["station"] != station:
            raise RuntimeError(f"unexpected station {r['station']}")
        t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
        raw = (r.get("tmpc") or "").strip()
        v = None
        if raw not in ("M", "", "T", "None"):
            v = finite_float(raw)
            if v is None:
                stats["nonfinite"] += 1
        if v is None:
            stats["no_temp"] += 1
        out.append((t, v))
        stats["rows"] += 1
    return out


def pair_nearest(reports, target_dt):
    """SPEC 4.5 and 8.7 item 1: the NEAREST report with a usable finite tmpc within
    15 minutes of the target hour, inclusive (G3). A tie keeps the earlier report
    (as session76_build.py l.230-256 does) and is flagged."""
    cands = sorted((abs((t - target_dt).total_seconds()) / 60.0, t, v) for t, v in reports
                   if abs((t - target_dt).total_seconds()) <= TOL_MIN * 60)
    usable = [c for c in cands if c[2] is not None]
    res = {"n_in_window": len(cands), "n_usable": len(usable), "tie": 0, "obs": None,
           "report_time": None, "status": "paired"}
    if usable:
        best = usable[0]
        res["obs"], res["report_time"] = best[2], best[1]
        if len(usable) > 1 and usable[1][0] == best[0]:
            res["tie"] = 1
        return res
    res["status"] = ("no routine report within 15 min" if not cands else "no usable temperature within 15 min")
    return res


def pair_historical(reports, target_dt):
    """The record's pairing, for the gate comparison only: the LAST qualifying
    report in file order. Copied from session62_reserved_confirm.py l.321-344:
    each report goes to its nearest whole hour, and is kept if that hour is the
    target and it is within 15 minutes, and its tmpc is usable."""
    kept = None
    for t, v in reports:
        nearest = (t + dt.timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)
        if nearest != target_dt:
            continue
        if abs((t - nearest).total_seconds()) > 15 * 60:
            continue
        if v is None:
            continue
        kept = (t, v)
    return kept


# ------------------------------------------------------------------ the shared build function (Step 3.1)

def build_rows(airports, targets, valid_limit, workers, obs_mode, first_v17=None):
    """Builds rows for the given (station, target_date) list.
    targets: list of (station, date). obs_mode: 'gate' (one 2-day IEM request per
    target date) or 'range' (one request per airport). Missing values are dropped
    and counted by reason, never filled (SPEC 2.2). Returns a dict with rows,
    manifest, drops, counts, the raw IEM responses and the pairing details."""
    t_start = now_utc()
    # ---- GRIB
    results = {}

    def work(item):
        st, d = item
        return item, pull_station_day(airports[st], d, valid_limit, first_v17)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        for item, res in ex.map(work, targets):
            results[item] = res
    # ---- observations
    windows = {}
    for st in airports:
        days = sorted(d for s, d in targets if s == st)
        if not days:
            continue
        if obs_mode == "gate":
            windows[st] = [(d - dt.timedelta(days=1), d) for d in days]
        else:
            windows[st] = [(days[0] - dt.timedelta(days=1), days[-1])]
    raw_iem, reports, ostats = [], {}, {}
    for st, wins in windows.items():
        ostats[st] = {"rows": 0, "no_temp": 0, "nonfinite": 0, "duplicates": 0}
        reports[st] = {}
        for a_day, b_day in wins:
            text, url, pulled = fetch_iem(st, a_day, b_day, valid_limit)
            raw_iem.append({"station": st, "first": a_day, "last": b_day, "text": text, "url": url,
                            "pulled": pulled})
            for t, v in parse_reports(text, st, ostats[st]):
                if t in reports[st]:
                    ostats[st]["duplicates"] += 1
                    continue
                reports[st][t] = v
    # ---- assemble
    rows, man, drops, pairs = [], [], [], {}
    counts = {}
    for st, d in sorted(targets, key=lambda x: (list(airports).index(x[0]), x[1])):
        a = airports[st]
        c = counts.setdefault(st, {"expected": 0, "rows": 0, "drops": {}, "ties": 0, "no_prev_obs": 0})
        c["expected"] += 1
        values, m, fails = results[(st, d)]
        man.extend(m)
        rep_list = sorted(reports[st].items())
        tgt = dt.datetime(d.year, d.month, d.day, a["target_hour"])
        prv = tgt - dt.timedelta(days=1)
        p_now, p_prev = pair_nearest(rep_list, tgt), pair_nearest(rep_list, prv)
        pairs[(st, d)] = {"today": p_now, "prev": p_prev, "reports": rep_list}
        c["ties"] += p_now["tie"]

        def drop(reason, detail):
            c["drops"][reason] = c["drops"].get(reason, 0) + 1
            drops.append([st, d.isoformat(), reason, detail])

        if fails:
            drop("no GRIB message", ";".join(sorted(fails)))
            continue
        try:
            row = derive(a, d, values)
        except (ValueError, KeyError, ZeroDivisionError) as e:
            drop("non-finite value", repr(e))
            continue
        if p_now["obs"] is None:
            drop(p_now["status"], "")
            continue
        row["obs_c"], row["prev_obs_c"] = p_now["obs"], p_prev["obs"]
        if p_prev["obs"] is None:
            c["no_prev_obs"] += 1
        rows.append(row)
        c["rows"] += 1
    return {"rows": rows, "manifest": man, "drops": drops, "counts": counts, "raw_iem": raw_iem,
            "pairs": pairs, "ostats": ostats, "started": t_start, "ended": now_utc()}


def write_new(path, data):
    """Exclusive create: never overwrites (SPEC 8.7 item 5)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", newline="") as f:
        f.write(data)


def csv_text(cols, rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    for r in rows:
        w.writerow(r)
    return buf.getvalue()


def write_outputs(built, dirs, header_note):
    """Writes the rows CSV and its .meta.txt, the GRIB manifest, the drop log and
    the raw IEM responses (each with its .meta.txt, SPEC 2.3), as new files only.
    `dirs` holds the five target paths, so --gate can exercise this in a temporary
    directory. Values are written with repr so they read back exactly."""
    for p in (dirs["rows"], dirs["rows_meta"], dirs["manifest"], dirs["drops"]):
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists; not overwriting (SPEC 8.7 item 5)")
    if dirs["iem"].exists():
        raise SystemExit(f"STOP: {dirs['iem']} already exists; not overwriting")
    rows = [[(repr(r[c]) if isinstance(r[c], float) else ("" if r.get(c) is None else r[c])) for c in ROW_COLS]
            for r in built["rows"]]
    write_new(dirs["rows"], csv_text(ROW_COLS, rows))
    write_new(dirs["manifest"], csv_text(MAN_COLS, built["manifest"]))
    write_new(dirs["drops"], csv_text(["station", "target_date", "reason", "detail"], built["drops"]))
    for r in built["raw_iem"]:
        name = f"iem_asos_{r['station']}_{r['first']}_{r['last']}_routine.csv"
        write_new(dirs["iem"] / name, r["text"])
        write_new(dirs["iem"] / (name + ".meta.txt"),
                  "Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
                  f"file        : {name}\nsource      : Iowa Environmental Mesonet ASOS download service\n"
                  f"pulled at   : {r['pulled']} (UTC)\ntool        : python requests (scripts/session86_forward_build.py)\n"
                  f"exact URL requested:\n{r['url']}\n")
    meta = [header_note, f"rows: {len(built['rows'])}", f"pull started (UTC): {built['started']}",
            f"pull ended (UTC): {built['ended']}",
            f"GRIB manifest: {dirs['manifest'].name} ({len(built['manifest'])} messages)",
            f"drop log: {dirs['drops'].name} ({len(built['drops'])} rows)"]
    write_new(dirs["rows_meta"], "\n".join(meta) + "\n")


def print_counts(built, airports, label):
    print(f"\n{label}: rows per airport against the expected full count")
    tot_e = tot_r = 0
    for st, c in built["counts"].items():
        print(f"  {st:5s} rows {c['rows']:>4d} of {c['expected']:>4d}; dropped {c['expected'] - c['rows']}; "
              f"drops by reason {c['drops'] or 'none'}; tie days {c['ties']}; rows with no previous-day obs {c['no_prev_obs']}")
        tot_e += c["expected"]
        tot_r += c["rows"]
    print(f"  total rows {tot_r} of {tot_e}")
    ok = [m for m in built["manifest"] if m[16] == "OK"]
    print(f"  GRIB messages: {len(built['manifest'])} requested, {len(ok)} OK, {len(built['manifest']) - len(ok)} failed; "
          f"bytes {sum(int(m[14]) for m in ok):,}")
    for st, s in built["ostats"].items():
        print(f"  IEM {st}: reports read {s['rows']}, no usable tmpc {s['no_temp']} "
              f"(non-finite {s['nonfinite']}), duplicate timestamps skipped {s['duplicates']}")


# ------------------------------------------------------------------ --build (written, not run in session 86)

def parse_v17(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H")


def run_build(args):
    airports = load_airports()
    run_date = dt.datetime.now(dt.timezone.utc).date()
    first_v17 = parse_v17(args.first_v17_cycle) if args.first_v17_cycle else None
    reasons, last_days = validate_build_request(args.period, first_v17, args.no_v17, args.decision, run_date, airports)
    print(f"--build period {args.period}; decision {args.decision}; run date (UTC) {run_date}; "
          f"first v17 cycle {args.first_v17_cycle or 'none (--no-v17)'}")
    print("last period-A target day per airport: " + ", ".join(f"{k} {v}" for k, v in last_days.items()))
    if reasons:
        raise SystemExit("REFUSED: " + "; ".join(reasons))
    outs = [OUT_ROWS, OUT_ROWS_META, OUT_MANIFEST, OUT_DROPS, OUT_IEM]
    if any(p.exists() for p in outs):
        raise SystemExit("REFUSED: an output file already exists: " + ", ".join(str(p) for p in outs if p.exists()))
    targets = []
    for st, a in airports.items():
        d = PERIOD_A_START
        while d <= last_days[st]:
            targets.append((st, d))
            d += dt.timedelta(days=1)
    built = build_rows(airports, targets, FORWARD_LIMIT, args.workers, "range", first_v17)
    write_outputs(built, {"rows": OUT_ROWS, "rows_meta": OUT_ROWS_META, "manifest": OUT_MANIFEST,
                          "drops": OUT_DROPS, "iem": OUT_IEM},
                  f"Period A rows for the 2026-27 forward test (D73). Decision entry: {args.decision}. "
                  f"First v17 cycle: {args.first_v17_cycle or 'none'}.")
    print_counts(built, airports, "period A")
    return 0


# ------------------------------------------------------------------ --gate (spent years only)

def expected_hash_from_decisions(pattern):
    m = re.search(pattern, DECISIONS_FILE.read_text())
    if not m:
        raise SystemExit(f"STOP: could not find {pattern} in DECISIONS.md")
    return m.group(1)


def read_training_set():
    """The committed training set, as {(station, date): row}. Any row dated
    2026-08-01 or later stops the run."""
    out = {}
    with open(TRAINING_SET) as f:
        for r in csv.DictReader(f):
            d = dt.date.fromisoformat(r["target_date"])
            if d > GATE_LAST_DAY:
                raise SystemExit(f"STOP: training set row dated {d}")
            out[(r["station"], d)] = r
    return out


def run_gate(args):
    print("SESSION 86 --gate (network; spent years only)")
    print(f"gate start (UTC): {now_utc()}")
    airports = load_airports()
    print_airports(airports)
    for d in GATE_DATES:
        check_gate_date(d)
    if len(GATE_DATES) != 9:
        raise SystemExit("STOP: the gate sample must be 9 dates")

    print("\n--- checks on the committed inputs")
    want = expected_hash_from_decisions(r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`")
    have = sha256_file(TRAINING_SET)
    print(f"training set SHA-256 {have}; F122.3 {want}; equal: {have == want}")
    want_m = expected_hash_from_decisions(r"manifest\.json`, SHA-256\s+`([0-9a-f]{64})`")
    have_m = sha256_file(MODEL_DIR / "manifest.json")
    print(f"models manifest.json SHA-256 {have_m}; F122.5 {want_m}; equal: {have_m == want_m}")
    if have != want or have_m != want_m:
        raise SystemExit("STOP: a committed file differs from its F122 SHA-256")
    training = read_training_set()
    hours = {}
    for (st, _), r in training.items():
        hours.setdefault(st, set()).add(int(r["target_hour"]))
    print("target hour per airport, training set vs SPEC 3.4: "
          + ", ".join(f"{st} {sorted(hours[st])} vs {airports[st]['target_hour']}" for st in airports))
    if any(hours[st] != {airports[st]["target_hour"]} for st in airports):
        raise SystemExit("STOP: a target hour in the training set differs from SPEC 3.4")

    targets = [(st, d) for st in airports for d in GATE_DATES]
    print(f"\nsample: {len(GATE_DATES)} dates x {len(airports)} airports = {len(targets)} station-days")
    print("dates: " + ", ".join(f"{d} ({GATE_WINDOWS[d]})" for d in GATE_DATES))
    committed = {k: training.get(k) for k in targets}
    no_row = [k for k, v in committed.items() if v is None]
    print(f"station-days with no committed row: {len(no_row)}" + (f" {no_row}" if no_row else ""))

    print("\n--- 5.2 size trial")
    per_station = {st: len(field_plan(airports[st]["lead"])) for st in airports}
    total_msgs = sum(per_station[st] * len(GATE_DATES) for st in airports)
    print("messages per station-day: " + ", ".join(f"{st} {n}" for st, n in per_station.items())
          + f"; total messages {total_msgs}")
    a0, d0 = airports["EGLC"], GATE_DATES[0]
    run0 = d0 - dt.timedelta(days=1)
    plan0 = field_plan(a0["lead"])
    trial = [p for p in plan0 if p[0] in ("tmp2m", "t850", "dswrf")]
    sizes = []
    for name, fh, var, level, step, identity in trial:
        url = file_url(run0, a0["cycle"], fh)
        raw, _ = http_get(url + ".idx", kind="idx")
        rng, exp = find_range(parse_idx(raw.decode("ascii")), var, level, step, run0, a0["cycle"])
        data, _ = fetch_message(url, rng, exp, "message (size trial)")
        sizes.append(len(data))
        print(f"  trial message {name} ({var}:{level}:{step}) EGLC {d0}: {len(data):,} bytes")
    mean = sum(sizes) / len(sizes)
    projected = mean * total_msgs
    print(f"bytes per message (mean of 3): {mean:,.0f}; projected total {projected:,.0f} bytes "
          f"({projected / 1024 ** 3:.2f} GiB); limit {SIZE_LIMIT_BYTES / 1024 ** 3:.0f} GiB")
    if projected > SIZE_LIMIT_BYTES:
        raise SystemExit("STOP: projected size is over 5 GiB")

    print("\n--- 5.3 rebuild from fresh GRIB and IEM pulls")
    tmp = Path(tempfile.mkdtemp(prefix="session86_gate_"))
    print(f"temporary directory (outside the repo, deleted at the end): {tmp}")
    try:
        built = build_rows(airports, targets, GATE_LIMIT, args.workers, "gate")
        print(f"pull started {built['started']}, ended {built['ended']}")
        print_counts(built, airports, "gate rebuild")
        rebuilt = {(r["station"], dt.date.fromisoformat(r["target_date"])): r for r in built["rows"]}
        n_fail = compare(airports, targets, committed, rebuilt, built, training)
        print("\n--- 5.4 frozen-model plumbing check (no error is computed)")
        plumbing(airports, targets, committed, rebuilt)
        print("\n--- exercising the --build writers in the temporary directory (nothing is written under data/)")
        dirs = {"rows": tmp / "rows.csv", "rows_meta": tmp / "rows.csv.meta.txt",
                "manifest": tmp / "diag" / "manifest.csv", "drops": tmp / "diag" / "drops.csv", "iem": tmp / "iem"}
        write_outputs(built, dirs, "gate exercise (spent years)")
        back = list(csv.DictReader(open(dirs["rows"])))
        same = all(float(b[c]) == r[c] for b, r in zip(back, built["rows"]) for c in G15 + ["temperature_grib_c"])
        print(f"wrote rows, manifest, drop log and {len(built['raw_iem'])} raw IEM files; rows read back equal: {same}")
        try:
            write_outputs(built, dirs, "second write")
            print("BAD: a second write did not refuse")
        except SystemExit as e:
            print(f"a second write refused, as required: {e}")
        print("\n--- every request made (pull time UTC, kind, URL, byte range, bytes)")
        for pulled, kind, url, rng, n in sorted(REQUEST_LOG):
            print(f"{pulled}  {kind:18s} {url}  {rng}  {n}")
        print(f"requests: {len(REQUEST_LOG)}; GRIB manifest rows: {len(built['manifest'])}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\ntemporary directory deleted: {not tmp.exists()}")
    print(f"gate end (UTC): {now_utc()}")
    return 0 if n_fail == 0 else 1


def num(x):
    return None if x is None or x == "" else float(x)


def compare(airports, targets, committed, rebuilt, built, training):
    """Step 5.3. Exact equality at the stored precision. Returns the number of
    failures (pairing-only observation differences are not failures)."""
    cols = G15 + ["temperature_grib_c"]
    passed = {st: {c: [0, 0] for c in cols + ["obs_c", "prev_obs_c"]} for st in airports}
    group_ok = {g: [0, 0] for g in GROUPS}
    per_air_group = {st: {g: [0, 0] for g in GROUPS} for st in airports}
    mism, pairing_only, not_rebuilt = [], [], []
    for st, d in targets:
        com, reb = committed[(st, d)], rebuilt.get((st, d))
        if com is None:
            continue
        if reb is None:
            not_rebuilt.append((st, d))
            continue
        pinfo = built["pairs"][(st, d)]
        day_bad = {g: False for g in GROUPS}
        day_cmp = {g: False for g in GROUPS}
        for c in cols:
            passed[st][c][1] += 1
            cv, rv = float(com[c]), reb[c]
            for g, gc in GROUPS.items():
                if c in gc:
                    day_cmp[g] = True
            if cv == rv:
                passed[st][c][0] += 1
            else:
                mism.append((st, d, c, cv, rv, rv - cv))
                for g, gc in GROUPS.items():
                    if c in gc:
                        day_bad[g] = True
        # observation, and the previous-day observation (against the committed row of D-1)
        tgt = dt.datetime(d.year, d.month, d.day, airports[st]["target_hour"])
        for c, key, day, when in (("obs_c", "today", d, tgt),
                                  ("prev_obs_c", "prev", d - dt.timedelta(days=1), tgt - dt.timedelta(days=1))):
            comm = com if c == "obs_c" else training.get((st, day))
            if comm is None:
                continue       # "where that row exists"
            passed[st][c][1] += 1
            day_cmp["obs" if c == "obs_c" else "prev_obs"] = True
            cv = float(comm["obs_c"])
            rv = reb["obs_c"] if c == "obs_c" else reb["prev_obs_c"]
            if rv is not None and cv == rv:
                passed[st][c][0] += 1
                continue
            hist = pair_historical(pinfo["reports"], when)
            near = pinfo[key]
            if rv is not None and hist is not None and hist[1] == cv:
                pairing_only.append((st, day, c, near["report_time"], rv, hist[0], hist[1]))
                passed[st][c][0] += 1      # not counted as a failure
                continue
            mism.append((st, day, c, cv, rv, None if rv is None else rv - cv))
            day_bad["obs" if c == "obs_c" else "prev_obs"] = True
        for g in GROUPS:
            if not day_cmp[g]:
                continue
            group_ok[g][1] += 1
            per_air_group[st][g][1] += 1
            if not day_bad[g]:
                group_ok[g][0] += 1
                per_air_group[st][g][0] += 1
    print("\nPass counts per column (exact equality; observation columns include the listed pairing-only differences):")
    for c in cols + ["obs_c", "prev_obs_c"]:
        ok = sum(passed[st][c][0] for st in airports)
        n = sum(passed[st][c][1] for st in airports)
        print(f"  {c:34s} {ok} of {n}")
    print("Pass counts per feature group (a station-day passes if all its columns are equal):")
    for g in GROUPS:
        print(f"  {g}: {group_ok[g][0]} of {group_ok[g][1]}")
    print("Pass counts per airport and group:")
    print(f"  {'':6s}" + "".join(f"{g:>10s}" for g in GROUPS))
    for st in airports:
        print(f"  {st:6s}" + "".join(f"{per_air_group[st][g][0]:>4d} of {per_air_group[st][g][1]:<3d}" for g in GROUPS))
    print(f"\nstation-days not rebuilt although a committed row exists: {len(not_rebuilt)} {not_rebuilt or ''}")
    print(f"pairing-only observation differences (nearest vs the record's last report; not failures): {len(pairing_only)}")
    for st, day, c, ntime, nval, htime, hval in pairing_only:
        print(f"  {st} {day} {c}: nearest {ntime} = {nval}; record's last report {htime} = {hval}")
    print(f"mismatches: {len(mism)}")
    for st, d, c, cv, rv, diff in mism:
        print(f"  MISMATCH {st} {d} {c}: committed {cv!r}, rebuilt {rv!r}, difference {diff!r}")
    return len(mism) + len(not_rebuilt)


def plumbing(airports, targets, committed, rebuilt):
    """Step 5.4: the frozen F122 models predict the same on a committed row and on
    its rebuilt row. Each model file's SHA-256 is checked against F122.5 (the
    table in DECISIONS.md) and against manifest.json first. No error is computed
    and no prediction is printed."""
    import lightgbm as lgb
    text = DECISIONS_FILE.read_text()
    block = text[text.index("**F122.5"):text.index("**F122.6")]
    table = {}
    for m in re.finditer(r"^\| (EGLC|LFPG|DSM|YSDU|RNO|KSFO \(SFO\)) \| \d+ \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|",
                         block, re.M):
        table["SFO" if m.group(1).startswith("KSFO") else m.group(1)] = (m.group(2), m.group(3))
    manifest = json.load(open(MODEL_DIR / "manifest.json"))["airports"]
    if set(table) != set(airports):
        raise SystemExit(f"STOP: F122.5 table has {sorted(table)}")
    models = {}
    for st in airports:
        for kind, sha, fname in (("bdlrt", table[st][0], f"{st}_bdlrt.txt"), ("b", table[st][1], f"{st}_b.txt")):
            have = sha256_file(MODEL_DIR / fname)
            ok = have == sha and have == manifest[st][f"model_{kind}_sha256"]
            print(f"  {fname:16s} SHA-256 {have}  equals F122.5 and manifest.json: {ok}")
            if not ok:
                raise SystemExit(f"STOP: {fname} differs from F122.5")
            models[(st, kind)] = lgb.Booster(model_file=str(MODEL_DIR / fname))
    worst = {}
    n_used = {}
    for st, d in targets:
        com, reb = committed[(st, d)], rebuilt.get((st, d))
        if com is None or reb is None:
            continue
        n_used[st] = n_used.get(st, 0) + 1
        for kind, cols in (("bdlrt", G15), ("b", G15[:5])):
            xc = np.array([[float(com[c]) for c in cols]], dtype=float)
            xr = np.array([[reb[c] for c in cols]], dtype=float)
            diff = abs(float(models[(st, kind)].predict(xc)[0]) - float(models[(st, kind)].predict(xr)[0]))
            worst[(st, kind)] = max(worst.get((st, kind), 0.0), diff)
    print("maximum absolute difference between the predictions on the committed and the rebuilt row (expected 0.0):")
    print(f"  {'airport':8s} {'station-days':>12s} {'B+D,L,R,T':>14s} {'B':>14s}")
    for st in airports:
        print(f"  {st:8s} {n_used.get(st, 0):>12d} {worst.get((st, 'bdlrt'), float('nan')):>14.17g} "
              f"{worst.get((st, 'b'), float('nan')):>14.17g}")


# ------------------------------------------------------------------ entry point

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--guard-check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--build", action="store_true")
    ap.add_argument("--period", default=None, help="--build only: A (B is refused)")
    ap.add_argument("--first-v17-cycle", default=None, help="--build only: YYYY-MM-DDTHH, from a DECISIONS entry")
    ap.add_argument("--no-v17", action="store_true", help="--build only: no operational v17 cycle by 2027-07-31")
    ap.add_argument("--decision", default=None, help="--build only: the DECISIONS entry number, printed in the output")
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    try:
        if a.guard_check:
            return guard_check()
        if a.gate:
            return run_gate(a)
        return run_build(a)
    except GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
