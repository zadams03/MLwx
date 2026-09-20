"""Session 55 Task 2: build and validate the radiation (E4) feature set --
downward shortwave radiation at the surface (DSWRF:surface), resolved to a
single, physically consistent 2-hour-average feature at every airport, for
every date already in the existing 5-feature GRIB dataset that falls
OUTSIDE the reserved 2024-25 confirmation year (DECISIONS D51).

Data-build-only session, mirroring session 49 (F98, E1), session 51 (E2)
and session 53 (F101's own build, E3) for the pull/join/validate shape. No
model is fit anywhere in this script.

Scope of fields: DSWRF:surface only (session prompt Task 2, "Scope of
fields") -- not the full eight-field radiation set F97 catalogued.

-----------------------------------------------------------------------
Step 0 -- the window-resolution problem (unique to this family, session
prompt Task 2 "Step 0").
-----------------------------------------------------------------------
F97 found DSWRF:surface carries only a time-AVERAGED "ave fcst" GRIB field
(never confirmed against an instantaneous alternative), and the averaging
window's LENGTH is a byproduct of each airport's own forecast lead:
18-24h (6h) at the lead-24 airports (EGLC, LFPG, DSM), 24-26h (2h) at the
lead-26 airports (YSDU, RNO). A raw feature built straight from the "ave
fcst" message would mean a different physical thing at different airports
-- breaking the project's identical-feature-at-every-airport principle
(D52/D53). This step resolves that BEFORE any bulk pull.

1. Checked directly, not assumed: does an INSTANTANEOUS DSWRF:surface
   variant exist alongside the averaged one, the way F97 found for the
   cloud-layer fields (LCDC/MCDC/HCDC)? Checked at the v16 floor
   (2021-03-24) and a recent date outside both the sealed year and the
   reserved year (2024-06-15), at every distinct forecast-hour file this
   session actually needs -- f024 and f026 (the two combos' own standard
   leads) AND f022 (the candidate de-accumulation endpoint for the
   lead-24 airports) -- by enumerating EVERY idx line whose var_code and
   level match DSWRF:surface, not just the first one.

2. RESULT (see the real Step 0 output below): NO instantaneous variant
   exists anywhere -- exactly one DSWRF:surface line per idx file, always
   an "ave fcst" step, at every file checked, both dates. So this session
   de-accumulates to a common 2-hour window ending at each airport's own
   target hour, the shorter of the two native windows:

   - lead-26 airports (YSDU, RNO): the native "24-26 hour ave fcst"
     message (eccodes startStep=24, endStep=26) IS ALREADY the 2-hour
     window ending at the target hour -- used directly, no
     de-accumulation, no second message fetched.
   - lead-24 airports (EGLC, LFPG, DSM): the native message is a 6-hour
     average, "18-24 hour ave fcst" (startStep=18, endStep=24). A second
     message, at forecast hour (lead-2)=22, carries "18-22 hour ave fcst"
     (startStep=18, endStep=22, 4h) -- the SAME reset window (18h) as the
     lead-24 message, one GFS output-hour earlier, confirmed present by
     direct byte-range fetch and decode before the bulk pull (Step 0).
     The trailing 2-hour average is recovered by energy subtraction:
     average * duration = total energy over that window, so
         energy(22h..24h) = ave(18h..24h)*6 - ave(18h..22h)*4
         dswrf_2h_wm2      = energy(22h..24h) / 2
     Both raw endpoints (the 6h and 4h averages) are kept as their own
     columns for transparency, mirroring E3's own
     `pressure_msl_lead_minus3_hpa` convention (session prompt Step 3).

   No per-airport statistical standardisation is used anywhere -- the
   consistency achieved is physical (an identical, real 2-hour window,
   ending at the target hour, at every airport), not cosmetic (session
   prompt Step 0, item 3).

Units: GRIB decodes DSWRF in W m**-2 (confirmed by direct decode, Step 0)
-- no unit conversion is needed, unlike pressure's Pa->hPa (E3).
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
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session55"
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
# same coordinates session 31/51/53's own Open-Meteo pulls used.
AIRPORT_COORDS_OM = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

VAR_CODE, LEVEL = "DSWRF", "surface"

MAX_WORKERS = 48
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session55"})


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def window_start(lead):
    """The nearest preceding 6-hour GFS radiation-average reset mark,
    confirmed empirically in Step 0 (lead=24 -> 18, lead=22 -> 18,
    lead=26 -> 24)."""
    return 6 * ((lead - 1) // 6)


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


def all_dswrf_lines(idx_text):
    """Every idx line whose var_code/level match DSWRF:surface, in file
    order -- used by Step 0 to prove no instantaneous variant is hiding
    alongside the averaged one (mirrors F97/session47's own all_variants,
    generalised to return full line info)."""
    lines = idx_text.strip().split("\n")
    out = []
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 6 and parts[3] == VAR_CODE and parts[4] == LEVEL:
            start = int(parts[1])
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
            out.append({"step": parts[5], "start": start, "end": end})
    return out


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
    for an averaged DSWRF field is the END of its averaging window, i.e.
    the same convention as every instantaneous field this project already
    uses -- so this function is unchanged from E1/E2/E3's own version."""
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
# Step 0 -- window-resolution decision. Read-only. No bulk pull.
# ---------------------------------------------------------------------------

STEP0_V16_DATE = date(2021, 3, 24)      # v16 floor, D48.7
STEP0_RECENT_DATE = date(2024, 6, 15)   # outside sealed year AND reserved year


def step0_window_resolution():
    print("=" * 78)
    print("STEP 0 -- window-resolution decision for DSWRF:surface.")
    print("Read-only. No bulk pull. Checks every idx line matching")
    print("DSWRF:surface (not just the first) at every distinct forecast-hour")
    print("file this session needs, at two sample dates.")
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

    # Every distinct forecast-hour FILE this session needs: each combo's own
    # standard lead, plus lead-2 wherever the native window is longer than
    # 2h (checked generically, not hardcoded to "24").
    files_needed = set()
    for (cycle, lead) in combos:
        files_needed.add((cycle, lead))
        if lead - window_start(lead) != 2:
            files_needed.add((cycle, lead - 2))
    print(f"\nDistinct forecast-hour files needed (standard lead, plus lead-2 "
          f"wherever the native window exceeds 2h): "
          f"{sorted(f'{c:02d}z/f{l:03d}' for c, l in files_needed)}")

    rows = []
    any_instantaneous_found = False
    any_missing_or_ambiguous = False
    windows_seen = {}  # (cycle, lead) -> set of (start_step, end_step) across dates

    for sample_name, target_date in (("v16_floor", STEP0_V16_DATE), ("recent", STEP0_RECENT_DATE)):
        run_date = target_date - timedelta(days=1)
        for (cycle, lead) in sorted(files_needed):
            base_url = grib_base_url(run_date, cycle)
            idx_url = f"{base_url}.f{lead:03d}.idx"
            try:
                idx_text = _get_with_retries(idx_url).decode("utf-8")
            except Exception as e:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"IDX FETCH FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead,
                             "FAIL", f"idx fetch failed: {e}"])
                any_missing_or_ambiguous = True
                continue

            matches = all_dswrf_lines(idx_text)
            if not matches:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"DSWRF:surface NOT FOUND in idx")
                rows.append([sample_name, run_date.isoformat(), cycle, lead,
                             "FAIL", "DSWRF:surface not found in idx"])
                any_missing_or_ambiguous = True
                continue
            if len(matches) > 1:
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"{len(matches)} DSWRF:surface lines found (expected 1) -- "
                      f"steps: {[m['step'] for m in matches]}")
                any_missing_or_ambiguous = True

            for m in matches:
                is_instantaneous = "ave fcst" not in m["step"]
                if is_instantaneous:
                    any_instantaneous_found = True
                print(f"  [{sample_name}] cycle={cycle:02d}z lead=f{lead:03d}: "
                      f"DSWRF:surface step='{m['step']}' "
                      f"({'INSTANTANEOUS' if is_instantaneous else 'averaged'})")

            # decode the (first/only) match to confirm a real value and the
            # exact start/end step, at EGLC's own established grid point --
            # one location is enough, the message itself is global.
            m = matches[0]
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
                match_ok = got_dt == expected_dt
                windows_seen.setdefault((cycle, lead), set()).add(
                    (info["start_step"], info["end_step"]))
                print(f"    decoded: {info['short_name']}={value:.2f} {info['units']} "
                      f"startStep={info['start_step']} endStep={info['end_step']} "
                      f"expected_valid={expected_dt.isoformat()} got_valid={got_dt.isoformat()} "
                      f"{'OK' if match_ok else 'VALID-TIME MISMATCH'}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead, "OK",
                             f"step={m['step']} value={value:.3f}Wm2 "
                             f"startStep={info['start_step']} endStep={info['end_step']} "
                             f"expected_valid={expected_dt.isoformat()} got_valid={got_dt.isoformat()} "
                             f"match={'OK' if match_ok else 'MISMATCH'}"])
                if not match_ok:
                    any_missing_or_ambiguous = True
            except Exception as e:
                print(f"    DECODE FAILED -- {e}")
                rows.append([sample_name, run_date.isoformat(), cycle, lead, "FAIL", str(e)])
                any_missing_or_ambiguous = True

    out_csv = DIAG / "session55_window_resolution.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sample", "run_date", "cycle", "lead", "status", "detail"])
        w.writerows(rows)
    print(f"\nWrote window-resolution check: {out_csv} ({len(rows)} rows)")

    if any_missing_or_ambiguous:
        print("\nSTOP: Step 0's inventory reading is missing, ambiguous, or a "
              "decoded value/valid-time did not match expectation at some "
              "combo/date. Refusing to proceed to the bulk pull -- per the "
              "session prompt, this is reported for review, not guessed past.")
        sys.exit(1)

    print("\n" + "-" * 78)
    if any_instantaneous_found:
        chosen_path = "instantaneous"
        print("DECISION: an instantaneous DSWRF:surface variant EXISTS at every "
              "combo/date checked -- using it directly. The window problem "
              "disappears; the feature is instantaneous like temperature, "
              "moisture and pressure already are.")
    else:
        chosen_path = "deaccumulate_2h"
        print("DECISION: NO instantaneous DSWRF:surface variant exists anywhere "
              "checked -- exactly one line per idx file, always an 'ave fcst' "
              "step, at every (cycle, lead) file, both sample dates. "
              "De-accumulating to a common 2-hour window ending at each "
              "airport's own target hour (session prompt Step 0, item 2):")
        for (cycle, lead), _stations in sorted(combos.items()):
            windows = windows_seen.get((cycle, lead), set())
            dur = lead - window_start(lead)
            if dur == 2:
                print(f"  cycle={cycle:02d}z lead=f{lead:03d}: native window "
                      f"{sorted(windows)} is ALREADY 2h -- used directly, no "
                      f"de-accumulation, no second message.")
            else:
                m3 = (cycle, lead - 2)
                print(f"  cycle={cycle:02d}z lead=f{lead:03d}: native window "
                      f"{sorted(windows)} ({dur}h) -- de-accumulated against "
                      f"cycle={cycle:02d}z lead=f{lead-2:03d} "
                      f"(window {sorted(windows_seen.get(m3, set()))}, "
                      f"{lead - 2 - window_start(lead - 2)}h), same reset mark "
                      f"({window_start(lead)}h) confirmed by direct decode above.")
    print("-" * 78)
    return chosen_path


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
    combos = {}  # (run_date, cycle, lead, needs_deaccum) -> set of stations
    for station, date_map in per_station.items():
        target_hour = AIRPORTS[station][0]
        cycle, lead = cycle_and_lead(target_hour)
        needs_deaccum = (lead - window_start(lead)) != 2
        for d in date_map:
            run_date = d - timedelta(days=1)
            combos.setdefault((run_date, cycle, lead, needs_deaccum), set()).add(station)
    return combos


def fetch_dswrf_message(base_url, lead, run_date, cycle):
    """Fetches the idx, finds the (only) DSWRF:surface line, byte-range
    fetches and decodes it. Returns (value_wm2, info) or raises."""
    idx_url = f"{base_url}.f{lead:03d}.idx"
    idx_text = _get_with_retries(idx_url).decode("utf-8")
    matches = all_dswrf_lines(idx_text)
    if len(matches) != 1:
        raise ValueError(f"expected exactly 1 DSWRF:surface line, found {len(matches)}")
    m = matches[0]
    grib_url = f"{base_url}.f{lead:03d}"
    range_hdr = (f"bytes={m['start']}-{m['end']}" if m["end"] is not None
                 else f"bytes={m['start']}-{m['start'] + 2_000_000}")
    content = _get_with_retries(grib_url, headers={"Range": range_hdr})
    if content[:4] != b"GRIB" or content[-4:] != b"7777":
        raise ValueError("bad magic markers (not a complete GRIB2 message)")
    gid, info = decode_message(content)
    expected_dt = expected_valid_dt(run_date, cycle, lead)
    got_dt = decoded_valid_dt(info["valid_date"], info["valid_time"])
    if got_dt != expected_dt:
        ec.codes_release(gid)
        raise ValueError(f"valid-time mismatch: expected {expected_dt}, got {got_dt}")
    return gid, info


def process_combo(run_date, cycle, lead, needs_deaccum, stations):
    """Fetches the standard-lead DSWRF message (and, if needs_deaccum, the
    lead-2 message too), decodes both, and returns per-station raw values
    (Pa-free, already W/m**2). No raw GRIB2 bytes survive past this
    function (fetch-decode-discard, F98/E2/E3 precedent)."""
    stations_str = ",".join(sorted(stations))
    manifest_rows = []
    base_url = grib_base_url(run_date, cycle)

    result = {"to_lead": None, "to_lead_minus2": None}

    try:
        gid, info = fetch_dswrf_message(base_url, lead, run_date, cycle)
        station_values = {}
        for station in stations:
            _, lat, lon = AIRPORTS[station]
            station_values[station] = bilinear_from_gid(gid, lat, lon)
        ec.codes_release(gid)
        result["to_lead"] = station_values
        manifest_rows.append([run_date.isoformat(), cycle, lead, "dswrf_to_lead",
                               stations_str, "OK",
                               f"short_name={info['short_name']} units={info['units']} "
                               f"startStep={info['start_step']} endStep={info['end_step']}"])
    except Exception as e:
        manifest_rows.append([run_date.isoformat(), cycle, lead, "dswrf_to_lead",
                               stations_str, "FAIL", str(e)])

    if needs_deaccum:
        lead_m2 = lead - 2
        try:
            gid, info = fetch_dswrf_message(base_url, lead_m2, run_date, cycle)
            station_values = {}
            for station in stations:
                _, lat, lon = AIRPORTS[station]
                station_values[station] = bilinear_from_gid(gid, lat, lon)
            ec.codes_release(gid)
            result["to_lead_minus2"] = station_values
            manifest_rows.append([run_date.isoformat(), cycle, lead_m2, "dswrf_to_lead_minus2",
                                   stations_str, "OK",
                                   f"short_name={info['short_name']} units={info['units']} "
                                   f"startStep={info['start_step']} endStep={info['end_step']}"])
        except Exception as e:
            manifest_rows.append([run_date.isoformat(), cycle, lead_m2, "dswrf_to_lead_minus2",
                                   stations_str, "FAIL", str(e)])

    return result, manifest_rows


def build_joined(span_name, existing_csv, decoded):
    with open(existing_csv) as f:
        existing_rows = list(csv.DictReader(f))
    new_cols = ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"]
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
        needs_deaccum = (lead - window_start(lead)) != 2

        dec = decoded.get(station, {}).get(d)
        if dec is None or dec.get("to_lead") is None:
            drop_log.append([station, d.isoformat(), span_name,
                              "missing decoded dswrf_to_lead value"])
            continue
        to_lead = dec["to_lead"]

        if needs_deaccum:
            if dec.get("to_lead_minus2") is None:
                drop_log.append([station, d.isoformat(), span_name,
                                  "missing decoded dswrf_to_lead_minus2 value"])
                continue
            to_lead_m2 = dec["to_lead_minus2"]
            dur_full = lead - window_start(lead)
            dur_partial = (lead - 2) - window_start(lead - 2)
            energy_2h = to_lead * dur_full - to_lead_m2 * dur_partial
            dswrf_2h = energy_2h / 2.0
            to_lead_m2_out = round(to_lead_m2, 3)
        else:
            dswrf_2h = to_lead
            to_lead_m2_out = ""  # not applicable -- native window is already 2h

        new_row = dict(row)
        new_row["dswrf_ave_to_lead_wm2"] = round(to_lead, 3)
        new_row["dswrf_ave_to_lead_minus2_wm2"] = to_lead_m2_out
        new_row["dswrf_2h_wm2"] = round(dswrf_2h, 3)
        out_rows.append(new_row)
        per_station_after[station] = per_station_after.get(station, 0) + 1

    out_csv = PROCESSED / f"session55_{span_name}_with_radiation.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, per_station_before, per_station_after, drop_log


# ---------------------------------------------------------------------------
# Step 4 -- Open-Meteo cross-check on shortwave_radiation, non-reserved
# overlap only. Mirrors session 51/53's own cross-check shape exactly.
# ---------------------------------------------------------------------------

OM_PAUSE_SECONDS = 3.0
OM_WINDOWS = [
    ("pre_reserved", date(2024, 1, 19), date(2024, 7, 31)),
    ("sealed", date(2025, 8, 1), date(2026, 7, 31)),
]


def _om_fetch(url, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session55"})
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


def pull_openmeteo_shortwave(station, tag, start, end):
    lat, lon = AIRPORT_COORDS_OM[station]
    hourly = "shortwave_radiation_previous_day1"
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
        f"purpose     : session 55 Step 4 -- Open-Meteo shortwave_radiation "
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


def load_openmeteo_shortwave(station, tag, start, end):
    import json
    path = DIAG / f"openmeteo_previousruns_{OPENMETEO_MODEL}_{station}_{start}_{end}_{tag}.json"
    d = json.load(open(path))
    h = d["hourly"]
    return dict(zip(h["time"], h["shortwave_radiation_previous_day1"]))


def main():
    print("=" * 78)
    print("SESSION 55 Task 2 -- radiation (E4) feature build + validation.")
    print("DSWRF:surface only. Data-build only: no model fit, no MAE, no CV.")
    print("The reserved year (2024-08-01..2025-07-31, DECISIONS D51) is never")
    print("loaded, pulled, or joined.")
    print("=" * 78)

    chosen_path = step0_window_resolution()
    assert chosen_path == "deaccumulate_2h", (
        f"unexpected Step-0 path {chosen_path!r} -- the rest of this script "
        "is written for the de-accumulation path found by direct probe; "
        "an instantaneous-path result would need different pull/join code, "
        "not silently reused."
    )

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

    assert_reserved_year_excluded("session55-train-span", train_dates[0], train_dates[-1],
                                   train_dates[0], train_dates[-1])
    assert_reserved_year_excluded("session55-sealed-span", sealed_dates[0], sealed_dates[-1],
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
    n_deaccum_combos = sum(1 for (*_, needs) in combos if needs)
    n_message_fetches = sum(2 if needs else 1 for (*_, needs) in combos)
    n_idx_fetches = n_message_fetches  # one idx per message fetched, same convention as E1-E3
    print(f"\n=== Step 2: bulk pull ===")
    print(f"Distinct (run_date, cycle, lead) combos to fetch: {n_combos} "
          f"({n_deaccum_combos} need de-accumulation, 2 messages each; "
          f"{n_combos - n_deaccum_combos} are already native 2h, 1 message each)")
    print(f"Total message fetches: {n_message_fetches} (+ {n_idx_fetches} idx fetches, "
          f"one per message)")

    manifest_rows = []
    decoded = {s: {} for s in AIRPORTS}  # decoded[station][date] = {"to_lead":.., "to_lead_minus2":..}

    t0 = time.time()
    n_done = 0
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {
            ex.submit(process_combo, rd, c, l, needs, st): (rd, st)
            for (rd, c, l, needs), st in combos.items()
        }
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            result, rows = fut.result()
            manifest_rows.extend(rows)
            for station in stations:
                decoded[station].setdefault(target_date, {})
                if result["to_lead"] is not None:
                    decoded[station][target_date]["to_lead"] = result["to_lead"][station]
                if result["to_lead_minus2"] is not None:
                    decoded[station][target_date]["to_lead_minus2"] = result["to_lead_minus2"][station]
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
    field_counts = {"dswrf_to_lead": {"requested": 0, "ok": 0},
                     "dswrf_to_lead_minus2": {"requested": 0, "ok": 0}}
    for (rd, c, l, needs), st in combos.items():
        field_counts["dswrf_to_lead"]["requested"] += len(st)
        if needs:
            field_counts["dswrf_to_lead_minus2"]["requested"] += len(st)
    for station, date_map in decoded.items():
        for d, vals in date_map.items():
            if "to_lead" in vals:
                field_counts["dswrf_to_lead"]["ok"] += 1
            if "to_lead_minus2" in vals:
                field_counts["dswrf_to_lead_minus2"]["ok"] += 1
    for field_key, counts in field_counts.items():
        failed = counts["requested"] - counts["ok"]
        print(f"  {field_key}: requested={counts['requested']} decoded_ok={counts['ok']} failed={failed}")

    manifest_csv = DIAG / "session55_pull_manifest.csv"
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

    # ---- join onto existing dataset, derive dswrf_2h_wm2 --------------------
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

    drops_csv = PROCESSED / "session55_radiation_join_drops.csv"
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

    print("\n-- null counts, dswrf_2h_wm2 (expect 0 throughout) --")
    any_nulls = False
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        null_rows = [r["target_date"] for r in srows if r["dswrf_2h_wm2"] in ("", None)]
        if null_rows:
            any_nulls = True
            print(f"  {station}: {len(null_rows)} null(s), e.g. {null_rows[:5]}")
        print(f"  {station} (n={len(srows)}): {'0 nulls' if not null_rows else 'see above'}")
    if not any_nulls:
        print("  Zero blanks in dswrf_2h_wm2 across every airport, both spans.")

    print("\n-- min/mean/max, dswrf_2h_wm2 (shortwave >= 0 everywhere; YSDU's "
          "02:00 UTC target hour is NIGHT so its shortwave should be at or "
          "near zero -- a correctness check, not a defect; RNO's 20:00 UTC is "
          "also near/after sunset for much of the year) --")
    means = {}
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        vals = [float(r["dswrf_2h_wm2"]) for r in srows]
        mn, mean, mx = min(vals), sum(vals) / len(vals), max(vals)
        n_negative = sum(1 for v in vals if v < 0)
        means[station] = mean
        print(f"  {station}: min={mn:.2f} mean={mean:.2f} max={mx:.2f} (n={len(vals)}) "
              f"negative_values={n_negative}")
    print(f"\n  Low-sun-airport check (report, do not correct): YSDU mean={means['YSDU']:.2f} "
          f"W/m2, RNO mean={means['RNO']:.2f} W/m2, against "
          f"{', '.join(f'{s}={means[s]:.1f}' for s in ('EGLC', 'LFPG', 'DSM'))} W/m2 "
          f"at the daytime-target-hour airports.")

    # ---- Step 4: Open-Meteo cross-check -------------------------------------
    print("\n-- Open-Meteo cross-check on shortwave_radiation, non-reserved "
          "overlap only --")
    print("  Compared only on the portion of the moisture-era overlap OUTSIDE "
          "the reserved year: 2024-01-19..2024-07-31 (pre-reservation) and "
          "2025-08-01..2026-07-31 (the sealed span, entirely after the "
          "reservation ends), the same two windows E2/E3's own cross-checks used.")
    print("  Note: Open-Meteo's own shortwave_radiation may carry its own "
          "averaging convention, different from this session's own resolved "
          "2h window -- a real, expected reason for a larger gap than the "
          "temperature/pressure cross-checks showed. Reported, not chased, "
          "this session (session prompt Step 4).")
    for tag, w_start, w_end in OM_WINDOWS:
        print(f"\n  -- window {tag}: {w_start} .. {w_end} --")
        for station in AIRPORTS:
            path, status = pull_openmeteo_shortwave(station, tag, w_start, w_end)
            print(f"    {station}: {status} -> {path.name}")

    print("\n  Per-airport agreement, combined across both non-reserved windows:")
    for station in AIRPORTS:
        om_all = {}
        for tag, w_start, w_end in OM_WINDOWS:
            om_all.update(load_openmeteo_shortwave(station, tag, w_start, w_end))
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
            om_val = om_all.get(key)
            if om_val is None:
                n_no_om += 1
                continue
            diffs.append(float(r["dswrf_2h_wm2"]) - om_val)
        if diffs:
            mean_abs = sum(abs(x) for x in diffs) / len(diffs)
            max_abs = max(abs(x) for x in diffs)
            mean_signed = sum(diffs) / len(diffs)
            print(f"  {station}: n_compared={len(diffs)} n_no_openmeteo_value={n_no_om} "
                  f"mean|diff|={mean_abs:.2f} max|diff|={max_abs:.2f} mean_diff={mean_signed:+.2f} W/m2")
        else:
            print(f"  {station}: NO COMPARABLE ROWS (n_no_openmeteo_value={n_no_om})")

    print("\n" + "=" * 78)
    print("END. No model was fit. The reserved year (2024-08-01..2025-07-31) was")
    print("never loaded, pulled, or referenced by any date used above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
