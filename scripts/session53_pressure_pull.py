"""Session 53 Task 2: build and validate the pressure/synoptic (E3) feature
set -- PRMSL and PRES:surface at each airport's own standard forecast lead,
plus PRMSL at lead-3 (same run) to derive a 3-hour pressure tendency -- for
every date already in the existing 5-feature GRIB dataset that falls OUTSIDE
the reserved 2024-25 confirmation year (DECISIONS D51).

Data-build-only session, mirroring session 49 (F98, E1) and session 51
(E2) exactly for the pull/join/validate shape. No model is fit anywhere in
this script.

Four design decisions, stated up front (session prompt Task 2, "Design
decisions"):

1. Pressure tendency is a SAME-RUN, two-lead-time difference, not a
   cross-run difference. For each airport's own (cycle, lead) combo (F89's
   lead convention), PRMSL is ALSO pulled at lead-3 from the identical run.
   `pressure_tendency_3h_hpa = pressure_msl_hpa - pressure_msl_lead_minus3_hpa`
   (positive = rising pressure into the target hour). Both values come from
   one forecast run made on day D-1, so this stays leakage-safe the same way
   every other feature in this project already is (SPEC 2.1b) -- it reads
   one run's own internal pressure trend, never a comparison across two
   separate model updates.
2. Raw companion fields, mirroring E1's raw pressure levels and E2's raw
   moisture fields, are pulled at the standard lead (no tendency):
   `pressure_msl_hpa`, `pressure_surface_hpa`.
3. NO elevation correction on any of the three new fields. PRMSL is
   mean-SEA-LEVEL pressure by definition, already elevation-normalized;
   PRES:surface and the tendency get bilinear horizontal interpolation only
   -- the same convention cloud/wind (F91), upper-air (F98), and moisture
   (E2, session 51) already use.
4. Units: GRIB decodes pressure in Pa; every new column is converted to hPa
   (divide by 100), matching standard synoptic-pressure convention.

The reserved confirmation year (2024-08-01..2025-07-31, DECISIONS D51) is
never loaded, never included in the pull's date list, and never joined --
enforced by filtering every date against scripts/session48_reserved_year.py's
own constants and guard function before anything else happens.
"""

import csv
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
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session53"
DIAG.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
OPENMETEO_MODEL = "gfs_global"  # pinned, DECISIONS D16

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
# same coordinates session 31/51's own Open-Meteo pulls used.
AIRPORT_COORDS_OM = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

# F97's own confirmed (var_code, level) labels -- reused verbatim.
STD_LEVELS = {
    "pressure_msl_hpa": ("PRMSL", "mean sea level"),
    "pressure_surface_hpa": ("PRES", "surface"),
}
TENDENCY_LEVELS = {
    "pressure_msl_lead_minus3_hpa": ("PRMSL", "mean sea level"),
}
ALL_FIELD_KEYS = list(STD_LEVELS) + list(TENDENCY_LEVELS)

MAX_WORKERS = 48
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session53"})


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


def find_message_range(idx_text, var_code, level, lead):
    """Exact-match the message whose step field is 'N hour fcst' -- F97
    confirmed PRMSL/PRES:surface are both instantaneous, no averaging-window
    complication, but the exact-step match is kept anyway so a surprise is
    reported, not silently mismatched."""
    lines = idx_text.strip().split("\n")
    wanted_step = f"{lead} hour fcst"
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 6 and parts[3] == var_code and parts[4] == level and parts[5] == wanted_step:
            start = int(parts[1])
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
            return start, end
    return None, None


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
    valid at. For the standard lead this equals target_date/target_hour;
    for lead-3 it is 3 hours earlier IN ABSOLUTE TIME, which can land on the
    PREVIOUS calendar date (e.g. YSDU: cycle 00z, lead 26 -> valid 02:00 next
    day; lead-3=23 -> valid 23:00 the SAME day as the run, i.e. one calendar
    day before target_date). Computed from absolute time, never assumed."""
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
            }
            return gid, info
    finally:
        tmp_path.unlink(missing_ok=True)


def decoded_valid_dt(valid_date, valid_time):
    y, m, d = int(str(valid_date)[:4]), int(str(valid_date)[4:6]), int(str(valid_date)[6:8])
    hour, minute = valid_time // 100, valid_time % 100
    return datetime(y, m, d) + timedelta(hours=hour, minutes=minute)


# ---------------------------------------------------------------------------
# Step 0 -- availability check (read-only, mirrors F97's method). Confirms
# PRMSL is present, correctly labelled, and decodes to a real value at the
# lead-3 offset, at two sample dates, before any bulk pull runs.
# ---------------------------------------------------------------------------

AVAIL_V16_DATE = date(2021, 3, 24)   # v16 floor, D48.7
AVAIL_RECENT_DATE = date(2024, 6, 15)  # outside sealed year AND reserved year


def availability_check():
    print("=" * 78)
    print("STEP 0 -- availability check: PRMSL at lead-3 (f021/f023), two dates.")
    print("Read-only. No bulk pull. Mirrors F97's own method.")
    print("=" * 78)

    assert AVAIL_RECENT_DATE < RESERVED_YEAR_START, (
        "availability-check recent date must fall before the reserved year starts"
    )
    print(f"\nv16-floor sample date : {AVAIL_V16_DATE}  (D48.7)")
    print(f"recent sample date    : {AVAIL_RECENT_DATE}  "
          f"(before reserved year {RESERVED_YEAR_START}, before sealed year "
          f"{date(2025, 8, 1)} -- confirmed by the assertion above)")

    combos = {}  # (cycle, lead) -> stations
    for station, (target_hour, _, _) in AIRPORTS.items():
        cycle, lead = cycle_and_lead(target_hour)
        combos.setdefault((cycle, lead), set()).add(station)
    print(f"\nDistinct (cycle, lead) combinations across the five airports: {len(combos)}")

    rows = []
    all_present_and_decoded = True
    for sample_name, target_date in (("v16_floor", AVAIL_V16_DATE), ("recent", AVAIL_RECENT_DATE)):
        run_date = target_date - timedelta(days=1)
        for (cycle, lead), stations in sorted(combos.items()):
            lead_m3 = lead - 3
            base_url = grib_base_url(run_date, cycle)
            idx_url = f"{base_url}.f{lead_m3:03d}.idx"
            try:
                idx_text = _get_with_retries(idx_url).decode("utf-8")
            except Exception as e:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead-3=f{lead_m3:03d} "
                      f"({','.join(sorted(stations))}): IDX FETCH FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead_m3,
                             ",".join(sorted(stations)), "FAIL", f"idx fetch failed: {e}"])
                all_present_and_decoded = False
                continue

            start, end = find_message_range(idx_text, "PRMSL", "mean sea level", lead_m3)
            if start is None:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead-3=f{lead_m3:03d} "
                      f"({','.join(sorted(stations))}): PRMSL NOT FOUND in idx")
                rows.append([sample_name, run_date.isoformat(), cycle, lead_m3,
                             ",".join(sorted(stations)), "FAIL", "PRMSL:mean sea level not found in idx"])
                all_present_and_decoded = False
                continue

            grib_url = f"{base_url}.f{lead_m3:03d}"
            range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
            try:
                content = _get_with_retries(grib_url, headers={"Range": range_hdr})
                if content[:4] != b"GRIB" or content[-4:] != b"7777":
                    raise ValueError("bad magic markers (not a complete GRIB2 message)")
                gid, info = decode_message(content)
                station = sorted(stations)[0]
                _, lat, lon = AIRPORTS[station]
                value_pa = bilinear_from_gid(gid, lat, lon)
                ec.codes_release(gid)
                expected_dt = expected_valid_dt(run_date, cycle, lead_m3)
                got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
                match = "OK" if got_dt == expected_dt else "VALID-TIME MISMATCH"
                print(f"  [{sample_name}] cycle={cycle:02d}z lead-3=f{lead_m3:03d} "
                      f"({','.join(sorted(stations))}): PRESENT, decoded "
                      f"{info['short_name']}={value_pa / 100.0:.2f} hPa "
                      f"(expected valid {expected_dt.isoformat()}, got {got_dt.isoformat()}) -- {match}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead_m3,
                             ",".join(sorted(stations)), "OK",
                             f"value={value_pa / 100.0:.3f}hPa expected_valid={expected_dt.isoformat()} "
                             f"got_valid={got_dt.isoformat()} match={match}"])
                if match != "OK":
                    all_present_and_decoded = False
            except Exception as e:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead-3=f{lead_m3:03d} "
                      f"({','.join(sorted(stations))}): DECODE FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead_m3,
                             ",".join(sorted(stations)), "FAIL", str(e)])
                all_present_and_decoded = False

    out_csv = DIAG / "session53_availability_check.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample", "run_date", "cycle", "lead_minus3", "stations", "status", "detail"])
        w.writerows(rows)
    print(f"\nWrote availability check: {out_csv} ({len(rows)} rows)")

    if not all_present_and_decoded:
        print("\nSTOP: PRMSL at lead-3 is not confirmed present/decodable/correctly-timed "
              "at every combo x sample date. Refusing to proceed to the bulk pull.")
        sys.exit(1)
    print("\nStep 0 PASSED: PRMSL at lead-3 is present, decodes to a real value, and "
          "lands at the expected valid time at every (cycle, lead) combo, both sample "
          "dates. Proceeding to the bulk pull.")


# ---------------------------------------------------------------------------
# Steps 1-4 -- date list, guard, bulk pull, join, validate.
# ---------------------------------------------------------------------------

def load_existing_dates():
    """Returns {station: {date: row_dict}}, dropping (never loading past this
    function) any row whose target_date falls inside the reserved
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


def process_combo(run_date, cycle, lead, stations):
    """Fetches TWO idx files (the standard lead and lead-3, same run) and
    decodes THREE messages total: PRMSL@lead, PRES:surface@lead, and
    PRMSL@lead-3. No raw GRIB2 bytes survive past this function (design
    decision 3, mirroring F98/E2's fetch-decode-discard pattern). Returns
    (results, manifest_rows) where results[field_key] is either a
    {station: value_Pa} dict or None (failed)."""
    lead_m3 = lead - 3
    stations_str = ",".join(sorted(stations))
    manifest_rows = []
    results = {}

    # -- standard-lead file: PRMSL + PRES:surface --
    base_url = grib_base_url(run_date, cycle)
    idx_url = f"{base_url}.f{lead:03d}.idx"
    try:
        idx_text = _get_with_retries(idx_url).decode("utf-8")
    except Exception as e:
        for field_key in STD_LEVELS:
            manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                   stations_str, "FAIL", f"idx fetch failed: {e}"])
        for field_key in STD_LEVELS:
            results[field_key] = None
        idx_text = None

    if idx_text is not None:
        expected_dt = expected_valid_dt(run_date, cycle, lead)
        for field_key, (var_code, level) in STD_LEVELS.items():
            try:
                start, end = find_message_range(idx_text, var_code, level, lead)
                if start is None:
                    raise ValueError(f"'{var_code}:{level}:{lead} hour fcst' not found in idx")
                grib_url = f"{base_url}.f{lead:03d}"
                range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
                content = _get_with_retries(grib_url, headers={"Range": range_hdr})
                if content[:4] != b"GRIB" or content[-4:] != b"7777":
                    raise ValueError("bad magic markers (not a complete GRIB2 message)")
                gid, info = decode_message(content)
                got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
                if got_dt != expected_dt:
                    ec.codes_release(gid)
                    raise ValueError(f"valid-time mismatch: expected {expected_dt}, got {got_dt}")
                station_values = {}
                for station in stations:
                    _, lat, lon = AIRPORTS[station]
                    station_values[station] = bilinear_from_gid(gid, lat, lon)
                ec.codes_release(gid)
                results[field_key] = station_values
                manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                       stations_str, "OK",
                                       f"short_name={info['short_name']} units={info['units']} "
                                       f"valid={got_dt.isoformat()} bytes={len(content)}"])
            except Exception as e:
                results[field_key] = None
                manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                       stations_str, "FAIL", str(e)])

    # -- lead-3 file: PRMSL only --
    idx_url_m3 = f"{base_url}.f{lead_m3:03d}.idx"
    try:
        idx_text_m3 = _get_with_retries(idx_url_m3).decode("utf-8")
    except Exception as e:
        for field_key in TENDENCY_LEVELS:
            manifest_rows.append([run_date.isoformat(), cycle, lead_m3, field_key,
                                   stations_str, "FAIL", f"idx fetch failed: {e}"])
            results[field_key] = None
        idx_text_m3 = None

    if idx_text_m3 is not None:
        expected_dt_m3 = expected_valid_dt(run_date, cycle, lead_m3)
        for field_key, (var_code, level) in TENDENCY_LEVELS.items():
            try:
                start, end = find_message_range(idx_text_m3, var_code, level, lead_m3)
                if start is None:
                    raise ValueError(f"'{var_code}:{level}:{lead_m3} hour fcst' not found in idx")
                grib_url = f"{base_url}.f{lead_m3:03d}"
                range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
                content = _get_with_retries(grib_url, headers={"Range": range_hdr})
                if content[:4] != b"GRIB" or content[-4:] != b"7777":
                    raise ValueError("bad magic markers (not a complete GRIB2 message)")
                gid, info = decode_message(content)
                got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
                if got_dt != expected_dt_m3:
                    ec.codes_release(gid)
                    raise ValueError(f"valid-time mismatch: expected {expected_dt_m3}, got {got_dt}")
                station_values = {}
                for station in stations:
                    _, lat, lon = AIRPORTS[station]
                    station_values[station] = bilinear_from_gid(gid, lat, lon)
                ec.codes_release(gid)
                results[field_key] = station_values
                manifest_rows.append([run_date.isoformat(), cycle, lead_m3, field_key,
                                       stations_str, "OK",
                                       f"short_name={info['short_name']} units={info['units']} "
                                       f"valid={got_dt.isoformat()} bytes={len(content)}"])
            except Exception as e:
                results[field_key] = None
                manifest_rows.append([run_date.isoformat(), cycle, lead_m3, field_key,
                                       stations_str, "FAIL", str(e)])

    return results, manifest_rows


def build_joined(span_name, existing_csv, decoded):
    with open(existing_csv) as f:
        existing_rows = list(csv.DictReader(f))
    new_cols = ["pressure_msl_hpa", "pressure_surface_hpa",
                "pressure_msl_lead_minus3_hpa", "pressure_tendency_3h_hpa"]
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
        dec = decoded.get(station, {}).get(d)
        missing = [fk for fk in ALL_FIELD_KEYS if dec is None or dec.get(fk) is None]
        if missing:
            drop_log.append([station, d.isoformat(), span_name, f"missing decoded field(s): {missing}"])
            continue
        msl_hpa = round(dec["pressure_msl_hpa"] / 100.0, 3)
        sfc_hpa = round(dec["pressure_surface_hpa"] / 100.0, 3)
        msl_m3_hpa = round(dec["pressure_msl_lead_minus3_hpa"] / 100.0, 3)
        new_row = dict(row)
        new_row["pressure_msl_hpa"] = msl_hpa
        new_row["pressure_surface_hpa"] = sfc_hpa
        new_row["pressure_msl_lead_minus3_hpa"] = msl_m3_hpa
        new_row["pressure_tendency_3h_hpa"] = round(msl_hpa - msl_m3_hpa, 3)
        out_rows.append(new_row)
        per_station_after[station] = per_station_after.get(station, 0) + 1

    out_csv = PROCESSED / f"session53_{span_name}_with_pressure.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, per_station_before, per_station_after, drop_log


# ---------------------------------------------------------------------------
# Step 4 check -- Open-Meteo cross-check on pressure_msl_hpa, non-reserved
# overlap only. Mirrors session 51's own cross-check shape exactly.
# ---------------------------------------------------------------------------

OM_PAUSE_SECONDS = 3.0
OM_WINDOWS = [
    ("pre_reserved", date(2024, 1, 19), date(2024, 7, 31)),
    ("sealed", date(2025, 8, 1), date(2026, 7, 31)),
]


def _om_fetch(url, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session53"})
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


def pull_openmeteo_pressure(station, tag, start, end):
    lat, lon = AIRPORT_COORDS_OM[station]
    hourly = "pressure_msl_previous_day1"
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
        f"purpose     : session 53 Step 4 -- Open-Meteo pressure_msl cross-check, "
        f"the non-reserved portion of the overlap only\n"
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


def load_openmeteo_pressure(station, tag, start, end):
    import json
    path = DIAG / f"openmeteo_previousruns_{OPENMETEO_MODEL}_{station}_{start}_{end}_{tag}.json"
    d = json.load(open(path))
    h = d["hourly"]
    return dict(zip(h["time"], h["pressure_msl_previous_day1"]))


def main():
    print("=" * 78)
    print("SESSION 53 Task 2 -- pressure/synoptic (E3) feature build + validation.")
    print("Data-build only: no model fit, no MAE, no CV. The reserved year")
    print("(2024-08-01..2025-07-31, DECISIONS D51) is never loaded, pulled, or")
    print("joined.")
    print("=" * 78)

    print("\nFour design decisions confirmed before any pull runs (session prompt")
    print("Task 2, 'Design decisions'):")
    print("  1. pressure_tendency_3h_hpa is a SAME-RUN, two-lead-time difference")
    print("     (lead vs lead-3, one run made on day D-1) -- not a cross-run")
    print("     comparison. Leakage-safe the same way every other feature already")
    print("     is (SPEC 2.1b).")
    print("  2. Raw companion fields pressure_msl_hpa and pressure_surface_hpa are")
    print("     pulled at the standard lead, mirroring E1's raw pressure levels")
    print("     and E2's raw moisture fields.")
    print("  3. NO elevation correction on any of the three new fields. PRMSL is")
    print("     mean-sea-level by definition (already elevation-normalized);")
    print("     PRES:surface and the tendency get bilinear horizontal")
    print("     interpolation only, same as cloud/wind (F91), upper-air (F98) and")
    print("     moisture (E2).")
    print("  4. Units: GRIB Pa -> hPa (divide by 100) for every new column.")

    availability_check()

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

    # Guard check (session prompt: "before any pull request is made").
    assert_reserved_year_excluded("session53-train-span", train_dates[0], train_dates[-1],
                                   train_dates[0], train_dates[-1])
    assert_reserved_year_excluded("session53-sealed-span", sealed_dates[0], sealed_dates[-1],
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
    print(f"Distinct (run_date, cycle, lead) combos to fetch: {n_combos}")
    print(f"Each combo needs 2 idx fetches (lead, lead-3) + 3 message fetches "
          f"(PRMSL@lead, PRES:surface@lead, PRMSL@lead-3) "
          f"-> {n_combos * 2} idx + {n_combos * 3} message = {n_combos * 5} total requests")

    manifest_rows = []
    per_field_counts = {fk: {"requested": 0, "ok": 0} for fk in ALL_FIELD_KEYS}
    decoded = {s: {} for s in AIRPORTS}  # decoded[station][date][field_key] = Pa

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
            results, rows = fut.result()
            manifest_rows.extend(rows)
            for field_key in ALL_FIELD_KEYS:
                per_field_counts[field_key]["requested"] += len(stations)
                vals = results.get(field_key)
                if vals is not None:
                    per_field_counts[field_key]["ok"] += len(stations)
                    for station in stations:
                        decoded[station].setdefault(target_date, {})[field_key] = vals[station]
            n_done += 1
            if n_done % 500 == 0 or n_done == n_combos:
                elapsed = time.time() - t0
                rate = n_done / elapsed if elapsed > 0 else 0
                eta = (n_combos - n_done) / rate if rate > 0 else float("inf")
                print(f"  {n_done}/{n_combos} combos  elapsed={elapsed/60:.1f}min  "
                      f"rate={rate:.2f}/s  eta={eta/60:.1f}min", flush=True)

    elapsed = time.time() - t0
    print(f"\nPull+decode done in {elapsed/60:.1f} min.")

    print("\n=== Validation (a): messages requested vs. decoded, per field ===")
    print("(counted per station-instance -- a shared combo like EGLC+LFPG counts twice)")
    all_levels = {**STD_LEVELS, **TENDENCY_LEVELS}
    for field_key, counts in per_field_counts.items():
        failed = counts["requested"] - counts["ok"]
        print(f"  {field_key} ({all_levels[field_key][0]}:{all_levels[field_key][1]}): "
              f"requested={counts['requested']} decoded_ok={counts['ok']} failed={failed}")

    manifest_csv = DIAG / "session53_pull_manifest.csv"
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

    # ---- join onto existing dataset, derive tendency -----------------------
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

    drops_csv = PROCESSED / "session53_pressure_join_drops.csv"
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
    new_cols = ["pressure_msl_hpa", "pressure_surface_hpa",
                "pressure_msl_lead_minus3_hpa", "pressure_tendency_3h_hpa"]

    print("\n-- null counts (expect 0 throughout) --")
    any_nulls = False
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        for col in new_cols:
            null_rows = [r["target_date"] for r in srows if r[col] in ("", None)]
            if null_rows:
                any_nulls = True
                print(f"  {station} {col}: {len(null_rows)} null(s), e.g. {null_rows[:5]}")
        print(f"  {station} (n={len(srows)}): "
              f"{'0 nulls in every new column' if not any_nulls else 'see above'}")
    if not any_nulls:
        print("  Zero blanks across every new column, every airport, both spans.")

    print("\n-- min/mean/max, pressure_msl_hpa and pressure_surface_hpa (sanity "
          "range roughly 950-1050 hPa at sea level; pressure_surface_hpa should "
          "sit visibly lower at RNO given its elevation) --")
    surface_means = {}
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        for col in ("pressure_msl_hpa", "pressure_surface_hpa"):
            vals = [float(r[col]) for r in srows]
            mn, mean, mx = min(vals), sum(vals) / len(vals), max(vals)
            print(f"  {station} {col}: min={mn:.2f} mean={mean:.2f} max={mx:.2f} (n={len(vals)})")
            if col == "pressure_surface_hpa":
                surface_means[station] = mean

    print(f"\n  pressure_surface_hpa means, all airports: "
          f"{', '.join(f'{s}={m:.1f}' for s, m in surface_means.items())}")
    rno_lowest = surface_means["RNO"] == min(surface_means.values())
    print(f"  RNO's own mean surface pressure is the LOWEST of the five airports: "
          f"{rno_lowest} (RNO sits at 1,345 m elevation, SPEC 3.4's highest by a "
          f"wide margin -- lower surface pressure there is the expected physical "
          f"signature of elevation, reported not corrected, per design decision 3).")

    print("\n-- min/mean/max, pressure_tendency_3h_hpa (sanity range roughly "
          "-15 to +15 hPa per 3h; outliers reported plainly, not clipped or "
          "dropped) --")
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        vals = [float(r["pressure_tendency_3h_hpa"]) for r in srows]
        mn, mean, mx = min(vals), sum(vals) / len(vals), max(vals)
        outliers = [(r["target_date"], float(r["pressure_tendency_3h_hpa"]))
                    for r in srows if not (-15.0 <= float(r["pressure_tendency_3h_hpa"]) <= 15.0)]
        print(f"  {station}: min={mn:.3f} mean={mean:.3f} max={mx:.3f} (n={len(vals)}) "
              f"outside_[-15,15]={len(outliers)}")
        if outliers:
            print(f"    outlier rows (date, value): {outliers[:10]}"
                  f"{' ...' if len(outliers) > 10 else ''}")

    # ---- Step 4: Open-Meteo cross-check -------------------------------------
    print("\n-- Open-Meteo cross-check on pressure_msl_hpa, non-reserved overlap "
          "only --")
    print("  Compared only on the portion of the moisture-era overlap OUTSIDE "
          "the reserved year: 2024-01-19..2024-07-31 (pre-reservation) and "
          "2025-08-01..2026-07-31 (the sealed span, entirely after the "
          "reservation ends), the same two windows E2's own cross-check used.")
    for tag, w_start, w_end in OM_WINDOWS:
        print(f"\n  -- window {tag}: {w_start} .. {w_end} --")
        for station in AIRPORTS:
            path, status = pull_openmeteo_pressure(station, tag, w_start, w_end)
            print(f"    {station}: {status} -> {path.name}")

    print("\n  Per-airport agreement, combined across both non-reserved windows:")
    rno_meandiff = None
    for station in AIRPORTS:
        om_msl_all = {}
        for tag, w_start, w_end in OM_WINDOWS:
            om_msl_all.update(load_openmeteo_pressure(station, tag, w_start, w_end))
        srows = [r for r in combined_rows if r["station"] == station]
        diffs = []
        n_no_om = 0
        for r in srows:
            d = date.fromisoformat(r["target_date"])
            in_pre = OM_WINDOWS[0][1] <= d <= OM_WINDOWS[0][2]
            in_sealed = OM_WINDOWS[1][1] <= d <= OM_WINDOWS[1][2]
            if not (in_pre or in_sealed):
                continue
            key = f"{r['target_date']}T{int(r['target_hour']):02d}:00"
            om_val = om_msl_all.get(key)
            if om_val is None:
                n_no_om += 1
                continue
            diffs.append(float(r["pressure_msl_hpa"]) - om_val)
        if diffs:
            mean_abs = sum(abs(x) for x in diffs) / len(diffs)
            max_abs = max(abs(x) for x in diffs)
            mean_signed = sum(diffs) / len(diffs)
            print(f"  {station}: n_compared={len(diffs)} n_no_openmeteo_value={n_no_om} "
                  f"mean|diff|={mean_abs:.3f} max|diff|={max_abs:.3f} mean_diff={mean_signed:+.3f} hPa")
            if station == "RNO":
                rno_meandiff = mean_abs
        else:
            print(f"  {station}: NO COMPARABLE ROWS (n_no_openmeteo_value={n_no_om})")

    if rno_meandiff is not None:
        print(f"\n  Design decision 3's own report-only question: RNO's PRMSL "
              f"cross-check gap is mean|diff|={rno_meandiff:.3f} hPa. This is a "
              f"different physical quantity (mean-sea-level pressure, already "
              f"elevation-normalized) than E1's below-ground-extrapolation "
              f"anomaly (F98) or E2's larger Open-Meteo dew-point/RH gap (F91's "
              f"own moisture cross-check) -- not directly comparable in units, "
              f"reported here as its own number, not scaled against those.")

    print("\n" + "=" * 78)
    print("END. No model was fit. The reserved year (2024-08-01..2025-07-31) was")
    print("never loaded, pulled, or referenced by any date used above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
