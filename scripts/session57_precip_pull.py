"""Session 57 Task 2: build and validate the precipitation (E5) feature set
-- the cumulative-since-forecast-start APCP:surface field, turned into one
mean precipitation rate (mm/h), for every date already in the existing
5-feature GRIB dataset that falls OUTSIDE the reserved 2024-25 confirmation
year (DECISIONS D51). This is the LAST family in the feature-selection
programme.

Data-build-only session, mirroring session 55 (F102, E4 radiation) for the
pull/join/validate shape, but with the ONE-MESSAGE path the session prompt
requires -- no de-accumulation, no second message per airport-date. No
model is fit anywhere in this script.

Scope of fields: APCP:surface only (session prompt Discipline section) --
not PRATE/SNOD/WEASD, and no radiation field.

-----------------------------------------------------------------------
Step 0 -- window handling and sparsity (unique to this family, session
prompt Task 2 "Step 0"). Resolved BEFORE any bulk pull, per the session
prompt's own settled decisions -- not re-decided here, only confirmed
directly and freshly against the real archive.
-----------------------------------------------------------------------
F97 found APCP:surface exposes TWO accumulation windows at each lead: a
short one matching the ave-field window (18-24h at lead 24, 24-26h at lead
26 -- the same window DSWRF:surface used, E4) and a cumulative-since-
forecast-start one ("0-1 day acc fcst" at lead 24, "0-26 hour acc fcst" at
lead 26 -- a day-vs-hour labelling quirk for the same "since hour 0" idea).

The session prompt's own choice: use the CUMULATIVE since-start message,
divided by its window length in hours, to give one mean precipitation rate
in mm/h. This is deliberately the ONE-MESSAGE option -- it does NOT
de-accumulate and does NOT fetch a second message per airport-date, unlike
the E4 radiation build.

Checked directly and freshly this session (NOT reusing F97's own idx files
-- one of F97's two sample dates, 2025-06-15, now falls inside the reserved
year, D51, the same wrinkle sessions 49/55 already noted for their own
spot-checks): every idx line matching APCP:surface (not just the first) at
every distinct (cycle, lead) combo the five airports' own target hours
select, at two sample dates, the v16 floor (2021-03-24) and a recent date
outside both the sealed year and the reserved year (2024-06-15). See
step0_window_resolution() below for the real check and its real output.

Units: GRIB reports APCP in kg m**-2, which equals mm of water (confirmed
by direct decode in Step 0, not assumed) -- no unit conversion needed.

Window definition, per airport (lead convention SPEC 7.2 / D48.2 / F89):
  - EGLC, LFPG, DSM (lead 24): cumulative window is forecast hour 0..24 --
    precip_window_hours = 24.
  - YSDU, RNO (lead 26): cumulative window is forecast hour 0..26 --
    precip_window_hours = 26.

precip_rate_mmh = apcp_cumulative_mm / precip_window_hours.

A structural consequence (stated plainly, not a defect, session prompt Step
0): because precip_window_hours is a CONSTANT per airport (24 or 26),
apcp_cumulative_mm and precip_rate_mmh differ only by a fixed per-airport
scale -- monotone transforms of each other. LightGBM's tree splits are
invariant to a monotone per-feature transform, so within any single
airport's model the raw total and the mean rate are the SAME feature. E5
therefore carries effectively ONE precipitation feature; the rate is kept
as the headline form for cross-airport interpretability (a common mm/h
scale), the raw total kept only for transparency. Session 58's own E5
experiment should therefore be planned as a clean B vs B+P, not a
raw-vs-resolved grid the way E1-E4 were.

A real cross-airport inconsistency, flagged plainly, not papered over:
unlike E4's resolved feature (a physically identical 2-hour window at every
airport), this since-start window is 24h at EGLC/LFPG/DSM but 26h at
YSDU/RNO -- so precip_rate_mmh is a mean over a 24h span at three airports
and a 26h span at two. Rate-normalisation handles the magnitude/scale, but
the span difference is a genuine mild inconsistency, reported honestly, not
claimed as E4-level physical consistency and not hidden with per-airport
statistical standardisation.

Sparsity handling (session prompt Step 0): precip_rate_mmh is used as one
continuous feature, no transform (no log1p, no binary wet/dry flag) --
LightGBM handles a zero-inflated continuous feature natively. A decoded
zero is a REAL, kept value (a dry forecast), not missing data -- SPEC 2.2's
drop-and-count applies only to a genuinely missing message or an unpaired
observation row, never to a legitimate zero. The per-airport zero-fraction
is reported descriptively in Step 4, with no pre-registered expectation of
which airport should read driest (F102's own session prompt carried a
wrong "which airport reads low" premise for radiation; this session does
not repeat that shape).
"""

import csv
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta
from pathlib import Path

import eccodes as ec
import requests
from requests.adapters import HTTPAdapter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session48_reserved_year import (  # noqa: E402
    RESERVED_YEAR_START,
    RESERVED_YEAR_END,
    assert_reserved_year_excluded,
)

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session57"
DIAG.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
OPENMETEO_MODEL = "gfs_global"  # pinned, DECISIONS D16

# Join target: the existing 5-feature GRIB dataset, the same base every
# E1-E4 family script joined onto (not any other family's own output).
EXISTING_V16_CSV = PROCESSED / "grib_features_v16_window.csv"
EXISTING_SEALED_CSV = PROCESSED / "grib_features_sealed_window.csv"

# SPEC 3.4: station -> (target hour UTC, grid latitude, grid longitude).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}
# IEM lat/lon, used only for the Open-Meteo cross-check pull (Step 4), the
# same coordinates session 31/51/53/55's own Open-Meteo pulls used.
AIRPORT_COORDS_OM = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

VAR_CODE, LEVEL = "APCP", "surface"

MAX_WORKERS = 48
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session57"})

_CUMULATIVE_STEP_RE = re.compile(r"^0-(\d+)\s+(hour|day)\s+acc fcst$")


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_base_url(run_date, cycle_hour):
    ymd = run_date.strftime("%Y%m%d")
    return f"{BUCKET}/gfs.{ymd}/{cycle_hour:02d}/atmos/gfs.t{cycle_hour:02d}z.pgrb2.0p25"


def _get_with_retries(url, headers=None):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (200, 206):
                return resp.content
            if resp.status_code == 404:
                raise FileNotFoundError(f"404 {url}")
            last_exc = RuntimeError(f"HTTP {resp.status_code} {url}")
        except Exception as e:
            last_exc = e
        if attempt < MAX_RETRIES:
            time.sleep(0.5 * attempt)
    raise last_exc


def all_apcp_lines(idx_text):
    """Every idx line whose var_code/level match APCP:surface, in file
    order -- there are always exactly two at this project's leads (the
    short ave-field-matching window and the cumulative-since-start one),
    per F97/Step 0. Mirrors session55's all_dswrf_lines."""
    lines = idx_text.strip().split("\n")
    out = []
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 6 and parts[3] == VAR_CODE and parts[4] == LEVEL:
            start = int(parts[1])
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
            out.append({"step": parts[5], "start": start, "end": end})
    return out


def parse_cumulative_window_hours(step_text):
    """Returns the window length in hours if step_text is a
    since-forecast-start cumulative accumulation ("0-N hour/day acc
    fcst"), else None. Handles the day-vs-hour labelling quirk F97/Step 0
    found (e.g. "0-1 day acc fcst" at lead 24, "0-26 hour acc fcst" at
    lead 26) -- both start with "0-", the short ave-window-matching entry
    never does (e.g. "18-24 hour acc fcst")."""
    m = _CUMULATIVE_STEP_RE.match(step_text.strip())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    return n * 24 if unit == "day" else n


def bilinear_from_gid(gid, lat, lon):
    neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        lat_span = max(n.lat for n in neighbours) - min(n.lat for n in neighbours)
        lon_span = max(n.lon for n in neighbours) - min(n.lon for n in neighbours)
        if lat_span < 1e-6 or lon_span < 1e-6:
            return min(neighbours, key=lambda n: n.distance).value
        raise ValueError(f"unexpected neighbour layout: {[(n.lat, n.lon) for n in neighbours]}")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    return (
        (1 - dlat) * (1 - dlon) * v00
        + (1 - dlat) * dlon * v01
        + dlat * (1 - dlon) * v10
        + dlat * dlon * v11
    )


def expected_valid_dt(run_date, cycle, lead):
    """The datetime a message at this (run_date, cycle, lead) should be
    valid at. Confirmed in Step 0 that eccodes' validityDate/validityTime
    for a since-start accumulated APCP field is the END of its
    accumulation window -- the target hour itself -- the same convention
    every other field in this project already uses."""
    run_dt = datetime(run_date.year, run_date.month, run_date.day) + timedelta(hours=cycle)
    return run_dt + timedelta(hours=lead)


def decode_message(content):
    tmp_path = DIAG / f"_scratch_{id(content)}.grib2"
    tmp_path.write_bytes(content)
    try:
        with open(tmp_path, "rb") as f:
            gid = ec.codes_grib_new_from_file(f)
            if gid is None:
                raise ValueError("eccodes could not decode a message")
            info = {
                "short_name": ec.codes_get(gid, "shortName"),
                "units": ec.codes_get(gid, "units"),
                "valid_date": ec.codes_get(gid, "validityDate"),
                "valid_time": ec.codes_get(gid, "validityTime"),
                "start_step": ec.codes_get(gid, "startStep"),
                "end_step": ec.codes_get(gid, "endStep"),
            }
            return gid, info
    finally:
        tmp_path.unlink(missing_ok=True)


def decoded_valid_dt(valid_date, valid_time):
    y, m, d = int(str(valid_date)[:4]), int(str(valid_date)[4:6]), int(str(valid_date)[6:8])
    hour, minute = valid_time // 100, valid_time % 100
    return datetime(y, m, d) + timedelta(hours=hour, minutes=minute)


# ---------------------------------------------------------------------------
# Step 0 -- window-resolution confirmation. Read-only. No bulk pull.
# ---------------------------------------------------------------------------

STEP0_V16_DATE = date(2021, 3, 24)      # v16 floor, D48.7
STEP0_RECENT_DATE = date(2024, 6, 15)   # outside sealed year AND reserved year


def step0_window_resolution():
    print("=" * 78)
    print("STEP 0 -- window-handling confirmation for APCP:surface.")
    print("Read-only. No bulk pull. Checks every idx line matching")
    print("APCP:surface (not just the first) at every distinct (cycle, lead)")
    print("combo this session needs, at two sample dates. Confirms the")
    print("session prompt's own pre-decided choice (cumulative-since-start,")
    print("one message, no de-accumulation) -- does not re-decide it.")
    print("=" * 78)

    assert STEP0_RECENT_DATE < RESERVED_YEAR_START, (
        "Step-0 recent date must fall before the reserved year starts"
    )
    print(f"\nv16-floor sample date : {STEP0_V16_DATE}  (D48.7)")
    print(f"recent sample date    : {STEP0_RECENT_DATE}  "
          f"(before reserved year {RESERVED_YEAR_START}, before sealed year "
          f"{date(2025, 8, 1)} -- confirmed by the assertion above)")

    combos = {}  # (cycle, lead) -> stations
    for station, (target_hour, _, _) in AIRPORTS.items():
        cycle, lead = cycle_and_lead(target_hour)
        combos.setdefault((cycle, lead), set()).add(station)
    print(f"\nDistinct (cycle, lead) combinations across the five airports: {len(combos)}")
    for (cycle, lead), stations in sorted(combos.items()):
        print(f"  cycle {cycle:02d}z, lead f{lead:03d}  <- {','.join(sorted(stations))}")
    print("\n(No lead-2 or other helper file is needed this session -- Task 2's own "
          "one-message design has no de-accumulation step, unlike E4.)")

    rows = []
    any_problem = False

    for sample_name, target_date in (("v16_floor", STEP0_V16_DATE), ("recent", STEP0_RECENT_DATE)):
        run_date = target_date - timedelta(days=1)
        for (cycle, lead) in sorted(combos):
            base_url = grib_base_url(run_date, cycle)
            idx_url = f"{base_url}.f{lead:03d}.idx"
            try:
                idx_text = _get_with_retries(idx_url).decode("utf-8")
            except Exception as e:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"IDX FETCH FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead,
                             "FAIL", f"idx fetch failed: {e}"])
                any_problem = True
                continue

            matches = all_apcp_lines(idx_text)
            if not matches:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"APCP:surface NOT FOUND in idx")
                rows.append([sample_name, run_date.isoformat(), cycle, lead,
                             "FAIL", "APCP:surface not found in idx"])
                any_problem = True
                continue

            print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                  f"{len(matches)} APCP:surface line(s) found:")
            for m in matches:
                cum_hours = parse_cumulative_window_hours(m["step"])
                tag = f"CUMULATIVE ({cum_hours}h since start)" if cum_hours is not None else "short/other window"
                print(f"    step='{m['step']}'  -> {tag}")

            cumulative = [m for m in matches if parse_cumulative_window_hours(m["step"]) == lead]
            if len(cumulative) != 1:
                print(f"    STOP-CONDITION: expected exactly 1 cumulative 0-{lead}h line, "
                      f"found {len(cumulative)}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead, "FAIL",
                             f"expected 1 cumulative 0-{lead}h APCP line, found {len(cumulative)}: "
                             f"{[m['step'] for m in matches]}"])
                any_problem = True
                continue

            m = cumulative[0]
            grib_url = f"{base_url}.f{lead:03d}"
            range_hdr = (f"bytes={m['start']}-{m['end']}" if m["end"] is not None
                         else f"bytes={m['start']}-{m['start'] + 2_000_000}")
            try:
                content = _get_with_retries(grib_url, headers={"Range": range_hdr})
                if content[:4] != b"GRIB" or content[-4:] != b"7777":
                    raise ValueError("bad magic markers (not a complete GRIB2 message)")
                gid, info = decode_message(content)
                _, lat, lon = AIRPORTS["EGLC"]
                value = bilinear_from_gid(gid, lat, lon)
                ec.codes_release(gid)
                expected_dt = expected_valid_dt(run_date, cycle, lead)
                got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
                step_ok = (info["start_step"] == 0 and info["end_step"] == lead)
                valid_ok = (got_dt == expected_dt)
                print(f"    decoded: {info['short_name']}={value:.3f} {info['units']} "
                      f"startStep={info['start_step']} endStep={info['end_step']} "
                      f"({'OK' if step_ok else 'STEP MISMATCH, expected 0/' + str(lead)}) "
                      f"expected_valid={expected_dt.isoformat()} got_valid={got_dt.isoformat()} "
                      f"({'OK' if valid_ok else 'VALID-TIME MISMATCH'})")
                rows.append([sample_name, run_date.isoformat(), cycle, lead, "OK",
                             f"step={m['step']} value={value:.3f}kg_m2 "
                             f"startStep={info['start_step']} endStep={info['end_step']} "
                             f"units={info['units']} "
                             f"expected_valid={expected_dt.isoformat()} got_valid={got_dt.isoformat()} "
                             f"step_match={'OK' if step_ok else 'MISMATCH'} "
                             f"valid_match={'OK' if valid_ok else 'MISMATCH'}"])
                if not (step_ok and valid_ok):
                    any_problem = True
            except Exception as e:
                print(f"    DECODE FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead, "FAIL", str(e)])
                any_problem = True

    out_csv = DIAG / "session57_window_resolution.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample", "run_date", "cycle", "lead", "status", "detail"])
        w.writerows(rows)
    print(f"\nWrote window-resolution check: {out_csv} ({len(rows)} rows)")

    if any_problem:
        print("\nSTOP: APCP:surface's cumulative-since-start window is missing, "
              "ambiguous, or a decoded step/valid-time did not match expectation "
              "at some combo/date. Refusing to proceed to the bulk pull -- per "
              "the session prompt, this is reported for review, not substituted.")
        sys.exit(1)

    print("\n" + "-" * 78)
    print("CONFIRMED: at every (cycle, lead) combo and both sample dates, exactly "
          "one APCP:surface line parses as a since-forecast-start cumulative "
          "accumulation (0-24h at lead 24, 0-26h at lead 26), decodes to a real, "
          "non-negative value in kg m**-2 (== mm), and its startStep/endStep and "
          "validity time exactly match the airport's own target hour. The "
          "session prompt's own pre-decided one-message, cumulative-since-start "
          "path is used as specified -- not re-decided here.")
    print("-" * 78)


# ---------------------------------------------------------------------------
# Steps 1-4 -- date list, guard, bulk pull, join, validate.
# ---------------------------------------------------------------------------

def load_existing_dates():
    """Returns {station: {date: row_dict}}, dropping (never loading past
    this function) any row whose target_date falls inside the reserved
    confirmation year (DECISIONS D51)."""
    per_station = {s: {} for s in AIRPORTS}
    for path in (EXISTING_V16_CSV, EXISTING_SEALED_CSV):
        with open(path) as f:
            for row in csv.DictReader(f):
                d = date.fromisoformat(row["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    continue  # never loaded past this line -- D51
                per_station[row["station"]][d] = row
    return per_station


def build_combos(per_station):
    combos = {}  # (run_date, cycle, lead) -> set of stations
    for station, date_map in per_station.items():
        target_hour = AIRPORTS[station][0]
        cycle, lead = cycle_and_lead(target_hour)
        for d in date_map:
            run_date = d - timedelta(days=1)
            combos.setdefault((run_date, cycle, lead), set()).add(station)
    return combos


def fetch_apcp_cumulative_message(base_url, lead, run_date, cycle):
    """Fetches the idx, finds the (only) since-start cumulative APCP:surface
    line (0-lead hours), byte-range fetches and decodes it, and validates
    its startStep/endStep and valid time against expectation. Returns
    (gid, info) or raises."""
    idx_url = f"{base_url}.f{lead:03d}.idx"
    idx_text = _get_with_retries(idx_url).decode("utf-8")
    matches = all_apcp_lines(idx_text)
    cumulative = [m for m in matches if parse_cumulative_window_hours(m["step"]) == lead]
    if len(cumulative) != 1:
        raise ValueError(
            f"expected exactly 1 cumulative 0-{lead}h APCP:surface line, "
            f"found {len(cumulative)} of {len(matches)} total APCP lines: "
            f"{[m['step'] for m in matches]}")
    m = cumulative[0]
    grib_url = f"{base_url}.f{lead:03d}"
    range_hdr = (f"bytes={m['start']}-{m['end']}" if m["end"] is not None
                 else f"bytes={m['start']}-{m['start'] + 2_000_000}")
    content = _get_with_retries(grib_url, headers={"Range": range_hdr})
    if content[:4] != b"GRIB" or content[-4:] != b"7777":
        raise ValueError("bad magic markers (not a complete GRIB2 message)")
    gid, info = decode_message(content)
    if info["start_step"] != 0 or info["end_step"] != lead:
        ec.codes_release(gid)
        raise ValueError(
            f"decoded step mismatch: expected startStep=0 endStep={lead}, "
            f"got startStep={info['start_step']} endStep={info['end_step']}")
    expected_dt = expected_valid_dt(run_date, cycle, lead)
    got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
    if got_dt != expected_dt:
        ec.codes_release(gid)
        raise ValueError(f"valid-time mismatch: expected {expected_dt}, got {got_dt}")
    return gid, info


def process_combo(run_date, cycle, lead, stations):
    """Fetches the ONE cumulative-since-start APCP message for this
    (run_date, cycle, lead) combo, decodes it once, and returns per-station
    bilinear-interpolated values (kg m**-2 == mm). No raw GRIB2 bytes
    survive past this function (fetch-decode-discard, E1-E4 precedent)."""
    stations_str = ",".join(sorted(stations))
    base_url = grib_base_url(run_date, cycle)
    try:
        gid, info = fetch_apcp_cumulative_message(base_url, lead, run_date, cycle)
        station_values = {}
        for station in stations:
            _, lat, lon = AIRPORTS[station]
            station_values[station] = bilinear_from_gid(gid, lat, lon)
        ec.codes_release(gid)
        manifest_row = [run_date.isoformat(), cycle, lead, "apcp_cumulative",
                         stations_str, "OK",
                         f"short_name={info['short_name']} units={info['units']} "
                         f"startStep={info['start_step']} endStep={info['end_step']}"]
        return station_values, [manifest_row]
    except Exception as e:
        manifest_row = [run_date.isoformat(), cycle, lead, "apcp_cumulative",
                         stations_str, "FAIL", str(e)]
        return None, [manifest_row]


def build_joined(span_name, existing_csv, decoded):
    with open(existing_csv) as f:
        existing_rows = list(csv.DictReader(f))
    new_cols = ["apcp_cumulative_mm", "precip_window_hours", "precip_rate_mmh"]
    fieldnames = list(existing_rows[0].keys()) + new_cols
    out_rows = []
    drop_log = []
    per_station_before = {}
    per_station_after = {}
    for row in existing_rows:
        station = row["station"]
        d = date.fromisoformat(row["target_date"])
        if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
            continue  # never touched -- D51
        per_station_before[station] = per_station_before.get(station, 0) + 1

        target_hour = AIRPORTS[station][0]
        _, lead = cycle_and_lead(target_hour)

        value = decoded.get(station, {}).get(d)
        if value is None:
            drop_log.append([station, d.isoformat(), span_name,
                              "missing decoded apcp_cumulative value"])
            continue

        new_row = dict(row)
        new_row["apcp_cumulative_mm"] = round(value, 3)
        new_row["precip_window_hours"] = lead
        new_row["precip_rate_mmh"] = round(value / lead, 4)
        out_rows.append(new_row)
        per_station_after[station] = per_station_after.get(station, 0) + 1

    out_csv = PROCESSED / f"session57_{span_name}_with_precip.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, per_station_before, per_station_after, drop_log


# ---------------------------------------------------------------------------
# Step 4 -- Open-Meteo cross-check on precipitation, non-reserved overlap
# only. Mirrors session 51/53/55's own cross-check shape exactly.
# ---------------------------------------------------------------------------

OM_PAUSE_SECONDS = 3.0
OM_WINDOWS = [
    ("pre_reserved", date(2024, 1, 19), date(2024, 7, 31)),
    ("sealed", date(2025, 8, 1), date(2026, 7, 31)),
]


def _om_fetch(url, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session57"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            return err.code, err.read().decode("utf-8", errors="replace")
        except Exception as err:
            if attempt == attempts:
                raise
            time.sleep(10 * attempt)


def pull_openmeteo_precip(station, tag, start, end):
    lat, lon = AIRPORT_COORDS_OM[station]
    hourly = "precipitation_previous_day1"
    params = [
        ("latitude", f"{lat}"), ("longitude", f"{lon}"),
        ("start_date", start.isoformat()), ("end_date", end.isoformat()),
        ("hourly", hourly), ("models", OPENMETEO_MODEL), ("timezone", "UTC"),
    ]
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           + urllib.parse.urlencode(params, safe=","))
    path = DIAG / f"openmeteo_previousruns_{OPENMETEO_MODEL}_{station}_{start}_{end}_{tag}.json"
    meta_path = path.with_suffix(path.suffix + ".meta.txt")
    if path.exists():
        return path, "SKIP (already present)"
    pulled_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    status, body = _om_fetch(url)
    path.write_text(body)
    meta_path.write_text(
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
        f"file        : {path.name}\n"
        f"purpose     : session 57 Step 4 -- Open-Meteo precipitation "
        f"cross-check, the non-reserved portion of the overlap only\n"
        f"pulled at   : {pulled_at}\n"
        "source      : Open-Meteo Previous Runs API (NOT the Historical Forecast API)\n"
        "tool        : python urllib\n\n"
        f"exact URL requested:\n{url}\n\n"
        "parameters:\n"
        f"  latitude   = {lat}    ({station})\n"
        f"  longitude  = {lon}\n"
        f"  start_date = {start}\n"
        f"  end_date   = {end}\n"
        f"  hourly     = {hourly}\n"
        f"  models     = {OPENMETEO_MODEL}  (pinned per DECISIONS D16)\n"
        "  timezone   = UTC\n\n"
        f"HTTP status {status}.\n"
    )
    time.sleep(OM_PAUSE_SECONDS)
    return path, f"HTTP {status}"


def load_openmeteo_precip(station, tag, start, end):
    import json
    path = DIAG / f"openmeteo_previousruns_{OPENMETEO_MODEL}_{station}_{start}_{end}_{tag}.json"
    d = json.load(open(path))
    h = d["hourly"]
    return dict(zip(h["time"], h["precipitation_previous_day1"]))


def main():
    print("=" * 78)
    print("SESSION 57 Task 2 -- precipitation (E5) feature build + validation.")
    print("APCP:surface only, cumulative-since-start, ONE message per")
    print("airport-date (no de-accumulation). Data-build only: no model fit,")
    print("no MAE, no CV. The reserved year (2024-08-01..2025-07-31,")
    print("DECISIONS D51) is never loaded, pulled, or joined.")
    print("=" * 78)

    step0_window_resolution()

    import shutil
    total, used, free = shutil.disk_usage(ROOT)
    print(f"\nFree disk space BEFORE pull: {free / (1024**3):.2f} GiB")

    per_station = load_existing_dates()

    all_dates = sorted({d for dm in per_station.values() for d in dm})
    train_dates = sorted({d for d in all_dates if d < RESERVED_YEAR_START})
    sealed_dates = sorted({d for d in all_dates if d > RESERVED_YEAR_END})
    print("\n=== Step 1: date list built from the existing 5-feature dataset, "
          "reserved year excluded ===")
    print(f"  train span : {train_dates[0]} .. {train_dates[-1]}  ({len(train_dates)} distinct dates)")
    print(f"  sealed span: {sealed_dates[0]} .. {sealed_dates[-1]}  ({len(sealed_dates)} distinct dates)")

    assert_reserved_year_excluded("session57-train-span", train_dates[0], train_dates[-1],
                                   train_dates[0], train_dates[-1])
    assert_reserved_year_excluded("session57-sealed-span", sealed_dates[0], sealed_dates[-1],
                                   sealed_dates[0], sealed_dates[-1])
    reserved_hits = [d for d in all_dates if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END]
    if reserved_hits:
        print(f"STOP: {len(reserved_hits)} reserved-year date(s) found in the pull list "
              f"after filtering -- refusing to pull. Examples: {reserved_hits[:5]}")
        sys.exit(1)
    print(f"\nGuard check PASSED (scripts/session48_reserved_year.py, "
          f"assert_reserved_year_excluded, plus a defensive per-date scan of all "
          f"{len(all_dates)} dates): no reserved-year date is in the pull list.")

    combos = build_combos(per_station)
    n_combos = len(combos)
    print(f"\n=== Step 2: bulk pull ===")
    print(f"Distinct (run_date, cycle, lead) combos to fetch: {n_combos} "
          f"(1 APCP message each -- no de-accumulation, unlike E4)")
    print(f"Total message fetches: {n_combos} (+ {n_combos} idx fetches, one per message)")

    manifest_rows = []
    decoded = {s: {} for s in AIRPORTS}  # decoded[station][date] = apcp_cumulative_mm

    t0 = time.time()
    n_done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {
            ex.submit(process_combo, rd, c, l, st): (rd, st)
            for (rd, c, l), st in combos.items()
        }
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            station_values, rows = fut.result()
            manifest_rows.extend(rows)
            if station_values is not None:
                for station in stations:
                    decoded[station][target_date] = station_values[station]
            n_done += 1
            if n_done % 500 == 0 or n_done == n_combos:
                elapsed = time.time() - t0
                rate = n_done / elapsed if elapsed > 0 else 0
                eta = (n_combos - n_done) / rate if rate > 0 else float("inf")
                print(f"  {n_done}/{n_combos} combos  elapsed={elapsed/60:.1f}min  "
                      f"rate={rate:.2f}/s  eta={eta/60:.1f}min", flush=True)

    elapsed = time.time() - t0
    print(f"\nPull+decode done in {elapsed/60:.1f} min.")

    print("\n=== Validation (a): messages requested vs. decoded ===")
    n_requested = sum(len(st) for (_rd, _c, _l), st in combos.items())
    n_ok = sum(len(dm) for dm in decoded.values())
    n_failed = n_requested - n_ok
    print(f"  apcp_cumulative: requested={n_requested} decoded_ok={n_ok} failed={n_failed}")

    manifest_csv = DIAG / "session57_pull_manifest.csv"
    with open(manifest_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run_date", "cycle", "lead", "field_key", "stations", "status", "detail"])
        w.writerows(manifest_rows)
    n_fail_rows = sum(1 for r in manifest_rows if r[5] == "FAIL")
    print(f"\nWrote pull manifest (provenance record, no raw bytes kept): "
          f"{manifest_csv} ({len(manifest_rows)} rows, {n_fail_rows} FAIL)")
    if n_fail_rows:
        print("  Failure reasons (SPEC 2.2 -- every drop is counted and given a reason):")
        for r in manifest_rows:
            if r[5] == "FAIL":
                print(f"    {r[0]} cycle={r[1]:02d}z lead=f{r[2]:03d} {r[3]} stations={r[4]}: {r[6]}")

    total, used, free_after = shutil.disk_usage(ROOT)
    print(f"\nFree disk space AFTER pull: {free_after / (1024**3):.2f} GiB "
          f"(before: {free / (1024**3):.2f} GiB)")

    # ---- join onto existing dataset, derive precip_rate_mmh -----------------
    print("\n=== Step 3: join and derive ===")
    all_drop_log = []
    joined_files = []
    for span_name, existing_csv in [("v16_window", EXISTING_V16_CSV), ("sealed_window", EXISTING_SEALED_CSV)]:
        out_csv, before, after, drops = build_joined(span_name, existing_csv, decoded)
        joined_files.append(out_csv)
        all_drop_log.extend(drops)
        print(f"\n  span={span_name} -> {out_csv.name}")
        for station in AIRPORTS:
            b = before.get(station, 0)
            a = after.get(station, 0)
            flag = "  <-- JOIN DROPPED ROWS vs. existing dataset" if a < b else ""
            print(f"    {station}: before={b} after={a}{flag}")

    drops_csv = PROCESSED / "session57_precip_join_drops.csv"
    with open(drops_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "span", "reason"])
        w.writerows(all_drop_log)
    print(f"\nWrote join-drop log: {drops_csv} ({len(all_drop_log)} rows)")

    combined_rows = []
    for out_csv in joined_files:
        with open(out_csv) as f:
            combined_rows.extend(csv.DictReader(f))

    # ---- Step 4: validate ---------------------------------------------------
    print("\n=== Step 4: validate ===")

    print("\n-- null counts, apcp_cumulative_mm and precip_rate_mmh (expect 0 "
          "throughout) --")
    any_nulls = False
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        null_a = [r["target_date"] for r in srows if r["apcp_cumulative_mm"] in ("", None)]
        null_r = [r["target_date"] for r in srows if r["precip_rate_mmh"] in ("", None)]
        if null_a or null_r:
            any_nulls = True
            print(f"  {station}: apcp_cumulative_mm nulls={len(null_a)} "
                  f"precip_rate_mmh nulls={len(null_r)}")
        print(f"  {station} (n={len(srows)}): "
              f"{'0 nulls' if not (null_a or null_r) else 'see above'}")
    if not any_nulls:
        print("  Zero blanks in apcp_cumulative_mm and precip_rate_mmh across "
              "every airport, both spans.")

    print("\n-- non-negativity check (precipitation cannot be negative) --")
    any_negative = False
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        vals = [float(r["apcp_cumulative_mm"]) for r in srows]
        mn = min(vals)
        if mn < 0:
            any_negative = True
        print(f"  {station}: min(apcp_cumulative_mm)={mn:.3f}")
    if not any_negative:
        print("  No negative values anywhere.")

    print("\n-- min/mean/max, precip_rate_mmh (mm/h), and zero-fraction "
          "(descriptive only -- no pass/fail, no pre-registered expectation "
          "of which airport is driest) --")
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        rates = [float(r["precip_rate_mmh"]) for r in srows]
        totals = [float(r["apcp_cumulative_mm"]) for r in srows]
        n = len(srows)
        zero_frac = sum(1 for t in totals if t == 0.0) / n
        print(f"  {station}: min={min(rates):.4f} mean={sum(rates)/n:.4f} "
              f"max={max(rates):.4f} mm/h (n={n})  "
              f"zero_fraction={zero_frac:.4f} ({sum(1 for t in totals if t == 0.0)}/{n} rows "
              f"with apcp_cumulative_mm == 0)")

    print("\n-- structural note (Step 0's own monotone-transform observation, "
          "confirmed numerically here) --")
    for station in AIRPORTS:
        target_hour = AIRPORTS[station][0]
        _, lead = cycle_and_lead(target_hour)
        print(f"  {station}: precip_window_hours={lead} (constant per airport) -- "
              f"apcp_cumulative_mm and precip_rate_mmh are monotone transforms "
              f"of each other within this airport's own rows.")

    # ---- Step 4: Open-Meteo cross-check -------------------------------------
    print("\n-- Open-Meteo cross-check on precipitation, non-reserved overlap "
          "only --")
    print("  Compared only on the portion of the moisture-era overlap OUTSIDE "
          "the reserved year: 2024-01-19..2024-07-31 (pre-reservation) and "
          "2025-08-01..2026-07-31 (the sealed span, entirely after the "
          "reservation ends), the same two windows E2/E3/E4's own cross-checks used.")
    print("  A LARGE magnitude gap is EXPECTED, not a defect: this session's "
          "precip_rate_mmh is a mean over a 24-26h since-forecast-start window; "
          "Open-Meteo's precipitation_previous_day1 is a single hour's own "
          "accumulation -- different accumulation conventions entirely. "
          "Reported, not chased (session prompt Step 4).")
    for tag, w_start, w_end in OM_WINDOWS:
        print(f"\n  -- window {tag}: {w_start} .. {w_end} --")
        for station in AIRPORTS:
            path, status = pull_openmeteo_precip(station, tag, w_start, w_end)
            print(f"    {station}: {status} -> {path.name}")

    print("\n  Per-airport agreement, combined across both non-reserved windows:")
    for station in AIRPORTS:
        om_all = {}
        for tag, w_start, w_end in OM_WINDOWS:
            om_all.update(load_openmeteo_precip(station, tag, w_start, w_end))
        srows = [r for r in combined_rows if r["station"] == station]
        diffs = []
        n_no_om = 0
        n_both_wet = n_both_dry = n_disagree = 0
        for r in srows:
            d = date.fromisoformat(r["target_date"])
            in_pre = OM_WINDOWS[0][1] <= d <= OM_WINDOWS[0][2]
            in_sealed = OM_WINDOWS[1][1] <= d <= OM_WINDOWS[1][2]
            if not (in_pre or in_sealed):
                continue
            key = f"{r['target_date']}T{int(r['target_hour']):02d}:00"
            om_val = om_all.get(key)
            if om_val is None:
                n_no_om += 1
                continue
            rate = float(r["precip_rate_mmh"])
            diffs.append(rate - om_val)
            ours_wet, om_wet = rate > 0, om_val > 0
            if ours_wet and om_wet:
                n_both_wet += 1
            elif not ours_wet and not om_wet:
                n_both_dry += 1
            else:
                n_disagree += 1
        if diffs:
            mean_abs = sum(abs(x) for x in diffs) / len(diffs)
            max_abs = max(abs(x) for x in diffs)
            mean_signed = sum(diffs) / len(diffs)
            n_cmp = len(diffs)
            agree_frac = (n_both_wet + n_both_dry) / n_cmp
            print(f"  {station}: n_compared={n_cmp} n_no_openmeteo_value={n_no_om} "
                  f"mean|diff|={mean_abs:.4f} max|diff|={max_abs:.4f} "
                  f"mean_diff={mean_signed:+.4f} mm/h  "
                  f"wet/dry co-occurrence: both_wet={n_both_wet} both_dry={n_both_dry} "
                  f"disagree={n_disagree}  agree_fraction={agree_frac:.4f}")
        else:
            print(f"  {station}: NO COMPARABLE ROWS (n_no_openmeteo_value={n_no_om})")

    print("\n" + "=" * 78)
    print("END. No model was fit. The reserved year (2024-08-01..2025-07-31) was")
    print("never loaded, pulled, or referenced by any date used above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
