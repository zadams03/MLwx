"""Session 51 Task 2/3: build and validate the moisture/humidity (E2)
feature set -- RH, DPT and SPFH at 2 m, plus a derived dew-point-depression
feature -- for every date already in the existing 5-feature GRIB dataset
that falls OUTSIDE the reserved 2024-25 confirmation year (DECISIONS D51).

Data-build-only session, mirroring session 49 (F98) exactly for the pull/
join/validate shape. No model is fit anywhere in this script.

Three design decisions, stated up front (session prompt Task 2, "Three
design decisions"):

1. The dew-point depression uses the RAW 2 m temperature (`t2m_raw`),
   recovered algebraically exactly as session 49 did
   (`t2m_raw = temperature_grib_c - correction_c`, each airport's own fixed
   D48.3/F90 constant) -- NOT the elevation-corrected `temperature_grib_c`.
   Reason: the depression must be a difference of two fields on the SAME
   (raw, grid-elevation) basis. Subtracting a raw dew point from the
   elevation-corrected temperature would leak each airport's own correction
   constant into the depression as a spurious offset. No new 2 m-temperature
   GRIB pull is needed -- t2m_raw is recovered from data already on disk.
2. NO elevation/lapse-rate correction on RH, DPT or SPFH. SPEC 7.2's
   7.429 degC/km correction fixes a *surface grid-cell elevation mismatch
   for temperature*. It does not apply to a humidity ratio, a specific
   humidity, or a dew point used to form a depression -- these three fields
   get bilinear horizontal interpolation ONLY, the same way cloud cover and
   wind speed are used as-is (SPEC 7.2, F91) and the upper-air pressure
   levels were (F98).
3. No raw GRIB2 bytes are kept on disk (disk-space-forced, as in F98). Each
   message is byte-range-fetched, decoded immediately with eccodes, and the
   bytes discarded -- the same fetch-decode-discard pattern session 49
   used. A per-request manifest (no bytes) stands in as the provenance
   record.

The reserved confirmation year (2024-08-01..2025-07-31, DECISIONS D51) is
never loaded, never included in the pull's date list, and never joined --
enforced by filtering every date against scripts/session48_reserved_year.py's
own constants and guard function before anything else happens.
"""

import csv
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
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
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session51"
DIAG.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
OPENMETEO_MODEL = "gfs_global"  # pinned, DECISIONS D16

EXISTING_V16_CSV = PROCESSED / "grib_features_v16_window.csv"
EXISTING_SEALED_CSV = PROCESSED / "grib_features_sealed_window.csv"
ELEV_CORR_CSV = (
    ROOT / "data" / "raw" / "diagnostics" / "session37"
    / "session37_elevation_correction_params.csv"
)

# SPEC 3.4: station -> (target hour UTC, grid latitude, grid longitude).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}
# IEM lat/lon, used only for the Open-Meteo cross-check pull (job 5), the
# same coordinates session 31/32's own Open-Meteo pulls used.
AIRPORT_COORDS_OM = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

# F97's own confirmed (var_code, level) labels -- reused verbatim.
LEVELS = {
    "relative_humidity_2m": ("RH", "2 m above ground"),
    "dew_point_2m": ("DPT", "2 m above ground"),
    "specific_humidity_2m": ("SPFH", "2 m above ground"),
}

MAX_WORKERS = 48
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session51"})


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
    confirmed RH:2m/DPT:2m/SPFH:2m are all instantaneous, no averaging-
    window complication, but the exact-step match is kept anyway so a
    surprise is reported, not silently mismatched."""
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


def load_elevation_corrections():
    out = {}
    with open(ELEV_CORR_CSV) as f:
        for row in csv.DictReader(f):
            out[row["station"]] = float(row["correction_c"])
    return out


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
    """Fetch the idx once, then byte-range fetch + decode each of the 3
    moisture fields once, bilinear-interpolating to every station sharing
    this combo. No raw GRIB2 bytes survive past this function (design
    decision 3). Returns (results, manifest_rows) where results[field_key]
    is either a {station: value} dict (native GRIB units) or None (failed)."""
    base_url = grib_base_url(run_date, cycle)
    idx_url = f"{base_url}.f{lead:03d}.idx"
    manifest_rows = []
    results = {}
    stations_str = ",".join(sorted(stations))

    try:
        idx_text = _get_with_retries(idx_url).decode("utf-8")
    except Exception as e:
        for field_key in LEVELS:
            manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                   stations_str, "FAIL", f"idx fetch failed: {e}"])
        return {fk: None for fk in LEVELS}, manifest_rows

    target_date_str = (run_date + timedelta(days=1)).isoformat()

    for field_key, (var_code, level) in LEVELS.items():
        try:
            start, end = find_message_range(idx_text, var_code, level, lead)
            if start is None:
                raise ValueError(f"'{var_code}:{level}:{lead} hour fcst' not found in idx")
            grib_url = f"{base_url}.f{lead:03d}"
            range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
            content = _get_with_retries(grib_url, headers={"Range": range_hdr})
            if content[:4] != b"GRIB" or content[-4:] != b"7777":
                raise ValueError("bad magic markers (not a complete GRIB2 message)")

            tmp_path = DIAG / f"_scratch_{run_date.isoformat()}_{cycle:02d}_{lead:03d}_{field_key}.grib2"
            tmp_path.write_bytes(content)
            try:
                with open(tmp_path, "rb") as f:
                    gid = ec.codes_grib_new_from_file(f)
                    if gid is None:
                        raise ValueError("eccodes could not decode a message")
                    short_name = ec.codes_get(gid, "shortName")
                    units = ec.codes_get(gid, "units")
                    valid_date = ec.codes_get(gid, "validityDate")
                    valid_time = ec.codes_get(gid, "validityTime")
                    station_values = {}
                    for station in stations:
                        _, lat, lon = AIRPORTS[station]
                        station_values[station] = bilinear_from_gid(gid, lat, lon)
                    ec.codes_release(gid)
            finally:
                tmp_path.unlink(missing_ok=True)

            got_valid = f"{str(valid_date)[:4]}-{str(valid_date)[4:6]}-{str(valid_date)[6:8]}"
            valid_hour = valid_time // 100
            if got_valid != target_date_str:
                raise ValueError(f"valid-date mismatch: got {got_valid}, expected {target_date_str}")

            results[field_key] = station_values
            manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                   stations_str, "OK",
                                   f"short_name={short_name} units={units} "
                                   f"valid={got_valid}T{valid_hour:02d}:00 bytes={len(content)}"])
        except Exception as e:
            results[field_key] = None
            manifest_rows.append([run_date.isoformat(), cycle, lead, field_key,
                                   stations_str, "FAIL", str(e)])

    return results, manifest_rows


def build_joined(span_name, existing_csv, decoded, elev_corr):
    with open(existing_csv) as f:
        existing_rows = list(csv.DictReader(f))
    new_cols = ["t2m_raw", "relative_humidity_2m", "dew_point_2m",
                "specific_humidity_2m", "dewpoint_depression_t2m"]
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
        missing = [fk for fk in LEVELS if dec is None or dec.get(fk) is None]
        if missing:
            drop_log.append([station, d.isoformat(), span_name, f"missing decoded field(s): {missing}"])
            continue
        t2m_raw = round(float(row["temperature_grib_c"]) - elev_corr[station], 3)
        new_row = dict(row)
        new_row["t2m_raw"] = t2m_raw
        new_row["relative_humidity_2m"] = round(dec["relative_humidity_2m"], 3)
        new_row["dew_point_2m"] = round(dec["dew_point_2m"], 3)
        new_row["specific_humidity_2m"] = round(dec["specific_humidity_2m"], 6)
        new_row["dewpoint_depression_t2m"] = round(t2m_raw - dec["dew_point_2m"], 3)
        out_rows.append(new_row)
        per_station_after[station] = per_station_after.get(station, 0) + 1

    out_csv = PROCESSED / f"session51_{span_name}_with_moisture.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, per_station_before, per_station_after, drop_log


# ---------------------------------------------------------------------------
# Task 3, check 5: Open-Meteo cross-check pull. Only the portion of the
# 2024-01-19-onward Open-Meteo overlap that falls OUTSIDE the reserved year
# is pulled: 2024-01-19..2024-07-31 (before the reservation starts) and
# 2025-08-01..2026-07-31 (the sealed span, entirely after it ends). Mirrors
# session 31's pull_forecast shape.
# ---------------------------------------------------------------------------

OM_PAUSE_SECONDS = 3.0
OM_WINDOWS = [
    ("pre_reserved", date(2024, 1, 19), date(2024, 7, 31)),
    ("sealed", date(2025, 8, 1), date(2026, 7, 31)),
]


def _om_fetch(url, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session51"})
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


def pull_openmeteo_moisture(station, tag, start, end):
    lat, lon = AIRPORT_COORDS_OM[station]
    variables = ["dew_point_2m", "relative_humidity_2m"]
    hourly = ",".join(f"{v}_previous_day1" for v in variables)
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
        f"purpose     : session 51 Task 3 check 5 -- Open-Meteo DPT/RH cross-check, "
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


def load_openmeteo_moisture(station, tag, start, end):
    path = DIAG / f"openmeteo_previousruns_{OPENMETEO_MODEL}_{station}_{start}_{end}_{tag}.json"
    import json
    d = json.load(open(path))
    h = d["hourly"]
    dpt = dict(zip(h["time"], h["dew_point_2m_previous_day1"]))
    rh = dict(zip(h["time"], h["relative_humidity_2m_previous_day1"]))
    return dpt, rh


def magnus_rh(t_c, td_c):
    """Relative humidity (%) from temperature and dew point via the Magnus
    approximation, a = 17.625, b = 243.04 (deg C), Alduchov & Eskridge 1996."""
    a, b = 17.625, 243.04
    gamma_td = (a * td_c) / (b + td_c)
    gamma_t = (a * t_c) / (b + t_c)
    return 100.0 * math.exp(gamma_td - gamma_t)


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    print("=" * 78)
    print("SESSION 51 Task 2/3 -- moisture (E2) feature build + validation.")
    print("Data-build only: no model fit, no MAE, no CV. The reserved year")
    print("(2024-08-01..2025-07-31, DECISIONS D51) is never loaded, pulled, or")
    print("joined.")
    print("=" * 78)

    print("\nThree design decisions confirmed before any pull runs (session prompt")
    print("Task 2):")
    print("  1. dewpoint_depression_t2m uses the RAW 2 m temperature (t2m_raw),")
    print("     recovered algebraically as t2m_raw = temperature_grib_c -")
    print("     correction_c (each airport's own fixed D48.3/F90 constant) --")
    print("     NOT the elevation-corrected temperature_grib_c. No new 2 m-")
    print("     temperature GRIB pull is needed.")
    print("  2. NO elevation/lapse-rate correction is applied to RH, DPT or SPFH")
    print("     anywhere in this script. SPEC 7.2's 7.429 degC/km correction is a")
    print("     temperature-only fix for a surface grid-cell elevation mismatch;")
    print("     it does not apply to a humidity ratio, a specific humidity, or a")
    print("     dew point used to form a depression -- bilinear horizontal")
    print("     interpolation only, same as cloud cover/wind speed (F91) and the")
    print("     upper-air pressure levels (F98).")
    print("  3. No raw GRIB2 bytes are kept on disk (disk-space-forced, as in")
    print("     F98) -- fetch, decode with eccodes, discard; a per-request")
    print("     manifest (no bytes) stands in as the provenance record.")

    import shutil
    total, used, free = shutil.disk_usage(ROOT)
    print(f"\nFree disk space BEFORE pull: {free / (1024**3):.2f} GiB")

    per_station = load_existing_dates()

    all_dates = sorted({d for dm in per_station.values() for d in dm})
    train_dates = sorted({d for d in all_dates if d < RESERVED_YEAR_START})
    sealed_dates = sorted({d for d in all_dates if d > RESERVED_YEAR_END})
    print("\nDate list built from the existing 5-feature dataset, reserved year excluded:")
    print(f"  train span : {train_dates[0]} .. {train_dates[-1]}  ({len(train_dates)} distinct dates)")
    print(f"  sealed span: {sealed_dates[0]} .. {sealed_dates[-1]}  ({len(sealed_dates)} distinct dates)")

    # Guard check (session prompt: "before any pull request is made").
    assert_reserved_year_excluded("session51-train-span", train_dates[0], train_dates[-1],
                                   train_dates[0], train_dates[-1])
    assert_reserved_year_excluded("session51-sealed-span", sealed_dates[0], sealed_dates[-1],
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
    print(f"\nDistinct (run_date, cycle, lead) combos to fetch: {n_combos}")
    print(f"3 fields/combo -> up to {n_combos} idx fetches + {n_combos * 3} message fetches "
          f"({n_combos * 4} total requests)")

    # ---- pull + decode; no raw bytes kept on disk (design decision 3) -----
    manifest_rows = []
    per_field_counts = {fk: {"requested": 0, "ok": 0} for fk in LEVELS}
    decoded = {s: {} for s in AIRPORTS}  # decoded[station][date][field_key] = native-unit value

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
            for field_key in LEVELS:
                per_field_counts[field_key]["requested"] += len(stations)
                vals = results.get(field_key)
                if vals is not None:
                    per_field_counts[field_key]["ok"] += len(stations)
                    for station in stations:
                        v = vals[station]
                        # dew_point_2m decodes in Kelvin (eccodes units=K,
                        # confirmed by a smoke test before the full pull ran)
                        # -- converted to degC so it is on the same basis as
                        # t2m_raw (degC) for the depression, design decision
                        # 1. relative_humidity_2m (%) and specific_humidity_2m
                        # (kg/kg) need no unit conversion.
                        if field_key == "dew_point_2m":
                            v = v - 273.15
                        decoded[station].setdefault(target_date, {})[field_key] = v
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
    for field_key, counts in per_field_counts.items():
        failed = counts["requested"] - counts["ok"]
        print(f"  {field_key} ({LEVELS[field_key][0]}:{LEVELS[field_key][1]}): "
              f"requested={counts['requested']} decoded_ok={counts['ok']} failed={failed}")

    manifest_csv = DIAG / "session51_pull_manifest.csv"
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

    # ---- derive t2m_raw + depression, join onto existing dataset ----------
    elev_corr = load_elevation_corrections()
    print("\nElevation corrections used to recover t2m_raw (D48.3/F90, unchanged, NOT")
    print("applied to relative_humidity_2m/dew_point_2m/specific_humidity_2m):")
    for s, c in elev_corr.items():
        print(f"  {s}: {c:+.4f} degC")

    print("\n=== Task 3 check 1: row counts before/after the join, per airport ===")
    all_drop_log = []
    joined_files = []
    for span_name, existing_csv in [("v16_window", EXISTING_V16_CSV), ("sealed_window", EXISTING_SEALED_CSV)]:
        out_csv, before, after, drops = build_joined(span_name, existing_csv, decoded, elev_corr)
        joined_files.append(out_csv)
        all_drop_log.extend(drops)
        print(f"\n  span={span_name} -> {out_csv.name}")
        for station in AIRPORTS:
            b = before.get(station, 0)
            a = after.get(station, 0)
            flag = "  <-- JOIN DROPPED ROWS vs. existing dataset" if a < b else ""
            print(f"    {station}: before={b} after={a}{flag}")

    drops_csv = PROCESSED / "session51_moisture_join_drops.csv"
    with open(drops_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "span", "reason"])
        w.writerows(all_drop_log)
    print(f"\nWrote join-drop log: {drops_csv} ({len(all_drop_log)} rows)")

    combined_rows = []
    for out_csv in joined_files:
        with open(out_csv) as f:
            combined_rows.extend(csv.DictReader(f))

    # ---- Task 3 check 2: availability, zero blanks -------------------------
    print("\n=== Task 3 check 2: availability -- zero blanks across the whole "
          "v16 window, per airport ===")
    new_cols = ["t2m_raw", "relative_humidity_2m", "dew_point_2m",
                "specific_humidity_2m", "dewpoint_depression_t2m"]
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

    # ---- Task 3 check 3: physical sanity -----------------------------------
    print("\n=== Task 3 check 3: physical sanity ===")
    dpt_violations, rh_violations, spfh_violations = [], [], []
    for r in combined_rows:
        t2m = float(r["t2m_raw"])
        dpt = float(r["dew_point_2m"])
        rh = float(r["relative_humidity_2m"])
        spfh = float(r["specific_humidity_2m"])
        if dpt > t2m:
            dpt_violations.append((r["station"], r["target_date"], dpt, t2m))
        if not (0.0 <= rh <= 100.0):
            rh_violations.append((r["station"], r["target_date"], rh))
        if spfh < 0.0:
            spfh_violations.append((r["station"], r["target_date"], spfh))

    print(f"  dew_point_2m > t2m_raw (violates dew_point_2m <= t2m_raw): "
          f"{len(dpt_violations)} row(s)")
    for v in dpt_violations[:10]:
        print(f"    {v}")
    print(f"  relative_humidity_2m outside [0, 100]: {len(rh_violations)} row(s)")
    for v in rh_violations[:10]:
        print(f"    {v}")
    print(f"  specific_humidity_2m < 0: {len(spfh_violations)} row(s)")
    for v in spfh_violations[:10]:
        print(f"    {v}")
    if not (dpt_violations or rh_violations or spfh_violations):
        print("  No violations of any of the three physical-sanity checks, at any row.")

    # ---- Task 3 check 4: internal-consistency Magnus self-check -----------
    print("\n=== Task 3 check 4: internal-consistency self-check -- RH recomputed "
          "from t2m_raw and dew_point_2m via the Magnus relation, vs. pulled "
          "relative_humidity_2m ===")
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        diffs = []
        for r in srows:
            t2m = float(r["t2m_raw"])
            dpt = float(r["dew_point_2m"])
            rh_pulled = float(r["relative_humidity_2m"])
            rh_computed = magnus_rh(t2m, dpt)
            diffs.append(rh_computed - rh_pulled)
        mean_abs = sum(abs(d) for d in diffs) / len(diffs)
        max_abs = max(abs(d) for d in diffs)
        mean_signed = sum(diffs) / len(diffs)
        print(f"  {station} (n={len(diffs)}): mean|diff|={mean_abs:.3f} pct  "
              f"max|diff|={max_abs:.3f} pct  mean_diff={mean_signed:+.3f} pct")

    # ---- Task 3 check 5: cross-check against Open-Meteo --------------------
    print("\n=== Task 3 check 5: cross-check against Open-Meteo, non-reserved "
          "overlap only ===")
    print("  Open-Meteo carries dew_point_2m and relative_humidity_2m from "
          "2024-01-19 (F85). Compared only on the portion of that overlap "
          "OUTSIDE the reserved year: 2024-01-19..2024-07-31 (pre-reservation) "
          "and 2025-08-01..2026-07-31 (the sealed span, entirely after the "
          "reservation ends). specific_humidity_2m has no Open-Meteo "
          "counterpart and is checked only by checks 3 and 4 above.")
    for tag, w_start, w_end in OM_WINDOWS:
        print(f"\n  -- window {tag}: {w_start} .. {w_end} --")
        for station in AIRPORTS:
            path, status = pull_openmeteo_moisture(station, tag, w_start, w_end)
            print(f"    {station}: {status} -> {path.name}")

    print("\n  Per-airport agreement, combined across both non-reserved windows:")
    for station in AIRPORTS:
        om_dpt_all, om_rh_all = {}, {}
        for tag, w_start, w_end in OM_WINDOWS:
            dpt_d, rh_d = load_openmeteo_moisture(station, tag, w_start, w_end)
            om_dpt_all.update(dpt_d)
            om_rh_all.update(rh_d)
        srows = [r for r in combined_rows if r["station"] == station]
        dpt_diffs, rh_diffs = [], []
        n_compared = 0
        n_no_om = 0
        for r in srows:
            d = date.fromisoformat(r["target_date"])
            in_pre = OM_WINDOWS[0][1] <= d <= OM_WINDOWS[0][2]
            in_sealed = OM_WINDOWS[1][1] <= d <= OM_WINDOWS[1][2]
            if not (in_pre or in_sealed):
                continue
            key = f"{r['target_date']}T{int(r['target_hour']):02d}:00"
            om_dpt = om_dpt_all.get(key)
            om_rh = om_rh_all.get(key)
            if om_dpt is None or om_rh is None:
                n_no_om += 1
                continue
            n_compared += 1
            dpt_diffs.append(float(r["dew_point_2m"]) - om_dpt)
            rh_diffs.append(float(r["relative_humidity_2m"]) - om_rh)

        def summarize(diffs, label):
            if not diffs:
                return f"{label}: NO COMPARABLE ROWS"
            mean_abs = sum(abs(x) for x in diffs) / len(diffs)
            max_abs = max(abs(x) for x in diffs)
            mean_signed = sum(diffs) / len(diffs)
            return (f"{label}: n={len(diffs)} mean|diff|={mean_abs:.3f} "
                    f"max|diff|={max_abs:.3f} mean_diff={mean_signed:+.3f}")

        print(f"  {station}: n_compared={n_compared} n_no_openmeteo_value={n_no_om}")
        print(f"    {summarize(dpt_diffs, 'dew_point_2m (degC, GRIB - OpenMeteo)')}")
        print(f"    {summarize(rh_diffs, 'relative_humidity_2m (pct, GRIB - OpenMeteo)')}")

    print("\n" + "=" * 78)
    print("END. No model was fit. The reserved year (2024-08-01..2025-07-31) was")
    print("never loaded, pulled, or referenced by any date used above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
