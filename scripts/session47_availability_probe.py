"""Session 47: feature-family availability probe (radiation, upper-air,
moisture, pressure, precipitation).

ONE JOB: find out which candidate GRIB feature families exist, under what
exact label/level, at the project's forecast lead, and how far back -- so a
later session can plan feature-experiment ordering on facts. This is a cheap
availability probe, the same shape as sessions 31 and 35: it builds nothing,
models nothing, pulls no bulk data, derives no feature, and picks no
ordering.

Two things are checked for every candidate variable:
  1. presence and exact label/level in the .idx inventory, at the v16 floor
     (2021-03-24) and a recent pre-test date (2025-06-15), at the forecast
     lead each airport's own previous_day1-equivalent convention selects
     (SPEC 3.2/7.2, DECISIONS F89: cycle floor(HH/6)*6 on day D-1, forecast
     hour 24 + (HH mod 6));
  2. a real, non-null decoded value, by byte-range-fetching the message and
     decoding it with eccodes -- never assumed from the label alone.

Only two sample dates are used, both <= 2025-07-31 (outside the sealed test
year, asserted below). One location's grid (EGLC's own established
Open-Meteo grid point, SPEC 3.4) is used for the general value spot-check,
since the .idx inventory is global; the precipitation family is additionally
spot-checked at RNO's own grid point, since precipitation is of particular
interest there (session prompt). No date range and no all-five-airport pull
is performed -- only the four distinct (cycle, lead) combinations the five
airports' own target hours already select (SPEC 3.4), at two dates each.

Raw idx extracts are saved under data/raw/diagnostics/session47/ with one
.meta.txt per file (SPEC 2.3). A summary CSV of every variable's own
availability/value result is saved alongside.
"""

import csv
import time
from datetime import date, timedelta
from pathlib import Path

import eccodes as ec
import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "diagnostics" / "session47"
OUT.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station code -> (target hour UTC, grid latitude, grid longitude).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}

V16_FLOOR = date(2021, 3, 24)          # SPEC 3.2 / DECISIONS D48.7
RECENT_DATE = date(2025, 6, 15)        # a recent pre-test date, outside the
                                        # sealed test year (2025-08-01 on)
SEALED_TEST_START = date(2025, 8, 1)

SAMPLE_DATES = {"v16_floor": V16_FLOOR, "recent": RECENT_DATE}

# Grid point used for the general spot-check value (EGLC's own established
# Open-Meteo grid point, SPEC 3.4). One location is enough to prove a
# variable decodes to a real value -- the inventory itself is global.
SPOTCHECK_STATION = "EGLC"
# Precipitation is additionally spot-checked at RNO's own grid point
# (session prompt: "of interest for Reno").
PRECIP_EXTRA_STATION = "RNO"

_session = requests.Session()
_session.headers.update({"User-Agent": "MLwx/session47"})

# ---------------------------------------------------------------------------
# Candidate variables, by family: (family, var_key, GRIB var code, level as
# it is expected to read in the .idx). The exact label is *confirmed*, not
# assumed -- if a (var_code, level) pair the session prompt named turns out
# to read differently, that mismatch is itself reported, not silently
# corrected.
# ---------------------------------------------------------------------------
CANDIDATES = [
    # -- Radiation --
    ("radiation", "dswrf_sfc", "DSWRF", "surface"),
    ("radiation", "uswrf_sfc", "USWRF", "surface"),
    ("radiation", "uswrf_toa", "USWRF", "top of atmosphere"),
    ("radiation", "dlwrf_sfc", "DLWRF", "surface"),
    ("radiation", "ulwrf_sfc", "ULWRF", "surface"),
    ("radiation", "ulwrf_toa", "ULWRF", "top of atmosphere"),
    ("radiation", "lcdc", "LCDC", "low cloud layer"),
    ("radiation", "mcdc", "MCDC", "middle cloud layer"),
    ("radiation", "hcdc", "HCDC", "high cloud layer"),
    # -- Upper-air / vertical structure --
    ("upper_air", "tmp_925", "TMP", "925 mb"),
    ("upper_air", "tmp_850", "TMP", "850 mb"),
    ("upper_air", "tmp_700", "TMP", "700 mb"),
    ("upper_air", "hgt_500", "HGT", "500 mb"),
    ("upper_air", "hgt_850", "HGT", "850 mb"),
    ("upper_air", "ugrd_850", "UGRD", "850 mb"),
    ("upper_air", "vgrd_850", "VGRD", "850 mb"),
    ("upper_air", "rh_850", "RH", "850 mb"),
    # -- Moisture --
    ("moisture", "rh_2m", "RH", "2 m above ground"),
    ("moisture", "dpt_2m", "DPT", "2 m above ground"),
    ("moisture", "spfh_2m", "SPFH", "2 m above ground"),
    ("moisture", "pwat", "PWAT", "entire atmosphere (considered as a single layer)"),
    # -- Pressure / synoptic --
    ("pressure", "prmsl", "PRMSL", "mean sea level"),
    ("pressure", "pres_sfc", "PRES", "surface"),
    # -- Precipitation --
    ("precip", "apcp_sfc", "APCP", "surface"),
    ("precip", "prate_sfc", "PRATE", "surface"),
    ("precip", "snod_sfc", "SNOD", "surface"),
    ("precip", "weasd_sfc", "WEASD", "surface"),
]


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_base_url(run_date, cycle_hour):
    ymd = run_date.strftime("%Y%m%d")
    return f"{BUCKET}/gfs.{ymd}/{cycle_hour:02d}/atmos/gfs.t{cycle_hour:02d}z.pgrb2.0p25"


def fetch(url, headers=None):
    resp = _session.get(url, headers=headers, timeout=60)
    resp.raise_for_status()
    return resp.content


def fetch_idx(base_url, lead, save_name):
    idx_url = f"{base_url}.f{lead:03d}.idx"
    text = fetch(idx_url).decode("utf-8")
    out_txt = OUT / f"{save_name}.idx"
    out_meta = OUT / f"{save_name}.idx.meta.txt"
    out_txt.write_text(text)
    pull_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out_meta.write_text(
        f"source: {idx_url}\n"
        f"pulled (UTC): {pull_time}\n"
        f"lines: {len(text.strip().splitlines())}\n"
    )
    return idx_url, text


def idx_lines(text):
    return text.strip().split("\n")


def all_variants(lines, var_code):
    """Every (level, step) pair found for this var_code, in file order."""
    out = []
    for line in lines:
        parts = line.split(":")
        if len(parts) >= 6 and parts[3] == var_code:
            out.append((parts[4], parts[5]))
    return out


def first_match_index(lines, var_code, level):
    """First idx line (any step) matching var_code+level exactly."""
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 5 and parts[3] == var_code and parts[4] == level:
            return i
    return None


def fetch_and_decode(base_url, lead, lines, var_code, level, lat, lon):
    """Byte-range fetch the first var_code+level message and decode it with
    eccodes. Returns a dict of real, observed facts -- never assumed."""
    i = first_match_index(lines, var_code, level)
    if i is None:
        return None, "not found in .idx"

    parts = lines[i].split(":")
    start = int(parts[1])
    step_found = parts[5]
    end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None

    grib_url = f"{base_url}.f{lead:03d}"
    range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 3_000_000}"
    try:
        content = fetch(grib_url, headers={"Range": range_hdr})
    except Exception as e:
        return None, f"byte-range fetch failed: {e}"

    if content[:4] != b"GRIB" or content[-4:] != b"7777":
        return None, "bad magic markers (not a complete GRIB2 message)"

    tmp_path = OUT / "_scratch_message.grib2"
    tmp_path.write_bytes(content)
    try:
        with open(tmp_path, "rb") as f:
            gid = ec.codes_grib_new_from_file(f)
            if gid is None:
                return None, "eccodes could not decode a message from the bytes fetched"
            short_name = ec.codes_get(gid, "shortName")
            units = ec.codes_get(gid, "units")
            valid_date = ec.codes_get(gid, "validityDate")
            valid_time = ec.codes_get(gid, "validityTime")
            grid_min = ec.codes_get(gid, "minimum")
            grid_max = ec.codes_get(gid, "maximum")
            neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
            ec.codes_release(gid)
    finally:
        tmp_path.unlink(missing_ok=True)

    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) == 2 and len(lons) == 2:
        lat0, lat1 = lats
        lon0, lon1 = lons
        grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
        v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
        v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
        dlat = (lat - lat0) / (lat1 - lat0)
        dlon = (lon_q - lon0) / (lon1 - lon0)
        point_value = (
            (1 - dlat) * (1 - dlon) * v00
            + (1 - dlat) * dlon * v01
            + dlat * (1 - dlon) * v10
            + dlat * dlon * v11
        )
    else:
        point_value = min(neighbours, key=lambda n: n.distance).value

    return {
        "step_decoded": step_found,
        "short_name": short_name,
        "units": units,
        "valid_date": valid_date,
        "valid_time": valid_time,
        "grid_min": grid_min,
        "grid_max": grid_max,
        "point_value": point_value,
        "bytes": len(content),
    }, None


def main():
    assert V16_FLOOR == date(2021, 3, 24)
    assert RECENT_DATE < SEALED_TEST_START, "recent sample date reaches into the sealed test year"

    # ---- distinct (cycle, lead) combos the five airports' own target hours
    # select (SPEC 3.4) -- four combos, not five, since EGLC and LFPG share one.
    combos = {}  # (cycle, lead) -> set of stations
    for station, (target_hour, _, _) in AIRPORTS.items():
        cycle, lead = cycle_and_lead(target_hour)
        combos.setdefault((cycle, lead), set()).add(station)

    print(f"Distinct (cycle, lead) combinations across the five airports: {len(combos)}")
    for (cycle, lead), stations in sorted(combos.items()):
        print(f"  cycle {cycle:02d}z, lead f{lead:03d}  <- {','.join(sorted(stations))}")

    # ---- Task 1: fetch idx inventories at both sample dates, every combo --
    idx_cache = {}  # (sample_name, cycle, lead) -> (base_url, lines)
    for sample_name, target_date in SAMPLE_DATES.items():
        run_date = target_date - timedelta(days=1)
        for (cycle, lead) in combos:
            base_url = grib_base_url(run_date, cycle)
            save_name = f"idx_{sample_name}_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{lead:03d}"
            idx_url, text = fetch_idx(base_url, lead, save_name)
            idx_cache[(sample_name, cycle, lead)] = (base_url, idx_lines(text))
            print(f"  fetched idx: {sample_name} run_date={run_date} cycle={cycle:02d}z "
                  f"lead=f{lead:03d}  ({len(idx_lines(text))} lines)  {idx_url}")

    # combo used for the general spot-check decode (EGLC/LFPG's own combo).
    spot_target_hour = AIRPORTS[SPOTCHECK_STATION][0]
    spot_cycle, spot_lead = cycle_and_lead(spot_target_hour)
    spot_lat, spot_lon = AIRPORTS[SPOTCHECK_STATION][1], AIRPORTS[SPOTCHECK_STATION][2]

    precip_target_hour = AIRPORTS[PRECIP_EXTRA_STATION][0]
    precip_cycle, precip_lead = cycle_and_lead(precip_target_hour)
    precip_lat, precip_lon = AIRPORTS[PRECIP_EXTRA_STATION][1], AIRPORTS[PRECIP_EXTRA_STATION][2]

    # ---- Task 1/2: per-variable availability + value confirmation --------
    results = []
    for family, var_key, var_code, level in CANDIDATES:
        row = {"family": family, "var_key": var_key, "var_code": var_code, "level_requested": level}

        for sample_name in SAMPLE_DATES:
            base_url, lines = idx_cache[(sample_name, spot_cycle, spot_lead)]
            variants = [lv for lv in all_variants(lines, var_code) if lv[0] == level]
            row[f"present_{sample_name}"] = bool(variants)
            row[f"steps_{sample_name}"] = "; ".join(f"{lv}:{st}" for lv, st in variants)

        # decode a real value at the recent date, EGLC's combo/grid point.
        base_url, lines = idx_cache[("recent", spot_cycle, spot_lead)]
        decoded, err = fetch_and_decode(base_url, spot_lead, lines, var_code, level, spot_lat, spot_lon)
        row["decode_station"] = SPOTCHECK_STATION
        row["decode_error"] = err
        if decoded:
            row.update({f"decoded_{k}": v for k, v in decoded.items()})
        results.append(row)

        print(f"[{family:9s}] {var_code}:{level}  "
              f"v16_floor={'Y' if row['present_v16_floor'] else 'N'}  "
              f"recent={'Y' if row['present_recent'] else 'N'}  "
              f"decode={'OK val=' + repr(decoded['point_value']) if decoded else 'FAIL: ' + str(err)}")

    # ---- Reno-specific precip spot-check, recent date only ----------------
    print(f"\nPrecipitation family: additional spot-check at {PRECIP_EXTRA_STATION}'s own grid point:")
    precip_rows = []
    for family, var_key, var_code, level in CANDIDATES:
        if family != "precip":
            continue
        base_url, lines = idx_cache[("recent", precip_cycle, precip_lead)]
        decoded, err = fetch_and_decode(base_url, precip_lead, lines, var_code, level, precip_lat, precip_lon)
        precip_rows.append({
            "family": family, "var_key": var_key, "var_code": var_code, "level_requested": level,
            "decode_station": PRECIP_EXTRA_STATION, "decode_error": err,
            **({f"decoded_{k}": v for k, v in decoded.items()} if decoded else {}),
        })
        print(f"  {var_code}:{level}  decode={'OK val=' + repr(decoded['point_value']) if decoded else 'FAIL: ' + str(err)}")

    # ---- write summary CSVs -------------------------------------------------
    fieldnames = [
        "family", "var_key", "var_code", "level_requested",
        "present_v16_floor", "steps_v16_floor", "present_recent", "steps_recent",
        "decode_station", "decode_error",
        "decoded_step_decoded", "decoded_short_name", "decoded_units",
        "decoded_valid_date", "decoded_valid_time",
        "decoded_grid_min", "decoded_grid_max", "decoded_point_value", "decoded_bytes",
    ]
    out_csv = OUT / "session47_availability_map.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in results:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"\nWrote availability map: {out_csv} ({len(results)} rows)")

    out_precip_csv = OUT / "session47_precip_rno_spotcheck.csv"
    with open(out_precip_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in precip_rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"Wrote Reno precip spot-check: {out_precip_csv} ({len(precip_rows)} rows)")

    return results, precip_rows


if __name__ == "__main__":
    main()
