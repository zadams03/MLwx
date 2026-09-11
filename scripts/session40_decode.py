"""Session 40, Task 1 (part 2): decode every sealed-year GRIB2 extract
(session40_grib_pull.py), apply the D48.3 elevation correction to
temperature, derive wind speed from u/v, and assemble the sealed-year GRIB
feature file the frozen sealed-test script (scripts/session39_sealed_test.py)
expects -- the identical decode logic session37_decode.py's Task 4 used for
the training window, restricted to the sealed test year and with no fresh
elevation-rate fit (D48.3's five constants are frozen and reused unchanged).

ONE JOB: build one row per (station, target_date) over 2025-08-01..
2026-07-31 (D48.8), with elevation-corrected temperature, cloud cover, and
wind speed, all GRIB-derived, in the identical column layout as
grib_features_v16_window.csv (D48.8: "same column layout as the training
file"). Report per-airport row and drop counts (SPEC 2.2 -- nothing is
filled). Does NOT join to any observation, fit any model, or touch any date
outside the sealed test year -- asserted before use.

No cloud/wind-vs-Open-Meteo validation here: that diagnostic was step 3's
job (F91) and only needed data through 2025-07-31 to compare against
Open-Meteo's own free-from-2024-01-19 cloud/wind series. Nothing in this
window is compared to Open-Meteo.
"""

import csv
from datetime import date, timedelta
from pathlib import Path

import eccodes as ec

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GRIB = RAW / "grib"
DIAG37 = RAW / "diagnostics" / "session37"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

WINDOW_START = date(2025, 8, 1)   # D48.8: sealed test year start (SPEC 4.3)
WINDOW_END = date(2026, 7, 31)    # D48.8: sealed test year end (SPEC 4.3)

# SPEC 3.4 / D48.2: station -> (target hour UTC, grid latitude, grid longitude).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def load_elevation_corrections():
    """D48.3: the five FROZEN elevation/lapse-rate constants (F90). Reused
    verbatim from session 37's own params file -- not refit."""
    path = DIAG37 / "session37_elevation_correction_params.csv"
    out = {}
    with open(path) as f:
        for row in csv.DictReader(f):
            out[row["station"]] = float(row["correction_c"])
    return out


def bilinear_value(path, lat, lon, expected_short_name):
    with open(path, "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
        if gid is None:
            raise ValueError(f"no GRIB message decoded from {path}")
        short_name = ec.codes_get(gid, "shortName")
        valid_date = ec.codes_get(gid, "validityDate")
        valid_time = ec.codes_get(gid, "validityTime")
        neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
        ec.codes_release(gid)

    if short_name != expected_short_name:
        raise ValueError(f"expected shortName '{expected_short_name}', got '{short_name}' in {path}")

    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        lat_span = max(n.lat for n in neighbours) - min(n.lat for n in neighbours)
        lon_span = max(n.lon for n in neighbours) - min(n.lon for n in neighbours)
        if lat_span < 1e-6 or lon_span < 1e-6:
            best = min(neighbours, key=lambda n: n.distance)
            return best.value, valid_date, valid_time
        raise ValueError(f"unexpected neighbour layout for {path}: {[(n.lat, n.lon) for n in neighbours]}")

    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    value = (
        (1 - dlat) * (1 - dlon) * v00
        + (1 - dlat) * dlon * v01
        + dlat * (1 - dlon) * v10
        + dlat * dlon * v11
    )
    return value, valid_date, valid_time


def grib_files_for(run_date, cycle, lead):
    prefix = f"gfs_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{lead:03d}"
    return {
        "tmp2m": GRIB / f"{prefix}_tmp2m.grib2",
        "tcdc": GRIB / f"{prefix}_tcdc.grib2",
        "ugrd10m": GRIB / f"{prefix}_ugrd10m.grib2",
        "vgrd10m": GRIB / f"{prefix}_vgrd10m.grib2",
    }


def decode_row(station, target_hour, lat, lon, target_date, elev_corr):
    run_date = target_date - timedelta(days=1)
    cycle, lead = cycle_and_lead(target_hour)
    files = grib_files_for(run_date, cycle, lead)

    missing = [k for k, p in files.items() if not p.exists()]
    if missing:
        return None, f"missing extract(s): {','.join(missing)}"

    try:
        tmp_k, vd, vt = bilinear_value(files["tmp2m"], lat, lon, "2t")
        tcc_pct, _, _ = bilinear_value(files["tcdc"], lat, lon, "tcc")
        u_ms, _, _ = bilinear_value(files["ugrd10m"], lat, lon, "10u")
        v_ms, _, _ = bilinear_value(files["vgrd10m"], lat, lon, "10v")
    except Exception as e:
        return None, f"decode error: {e}"

    expected_valid = target_date.isoformat()
    got_valid = f"{str(vd)[:4]}-{str(vd)[4:6]}-{str(vd)[6:8]}"
    valid_hour = vt // 100
    if got_valid != expected_valid or valid_hour != target_hour:
        return None, f"valid-time mismatch: got {got_valid}T{valid_hour:02d}:00, expected {expected_valid}T{target_hour:02d}:00"

    temp_c = (tmp_k - 273.15) + elev_corr
    wind_kmh = ((u_ms ** 2 + v_ms ** 2) ** 0.5) * 3.6

    return {
        "station": station,
        "target_date": expected_valid,
        "target_hour": target_hour,
        "run_date": run_date.isoformat(),
        "cycle": cycle,
        "lead": lead,
        "temperature_grib_c": round(temp_c, 3),
        "cloud_cover_grib_pct": round(tcc_pct, 3),
        "wind_speed_grib_kmh": round(wind_kmh, 3),
    }, None


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    assert WINDOW_START == date(2025, 8, 1), "sealed test year start does not match D48.8/SPEC 4.3"
    assert WINDOW_END == date(2026, 7, 31), "sealed test year end does not match D48.8/SPEC 4.3"

    elev_corr = load_elevation_corrections()
    print("Elevation corrections (degC, D48.3 -- frozen, reused from session37_elevation_fix.py, NOT refit):")
    for s, c in elev_corr.items():
        print(f"  {s}: {c:+.4f}")

    all_rows = []
    drop_log = []
    for station, (target_hour, lat, lon) in AIRPORTS.items():
        n_kept = n_dropped = 0
        for target_date in daterange(WINDOW_START, WINDOW_END):
            row, err = decode_row(station, target_hour, lat, lon, target_date, elev_corr[station])
            if row is None:
                n_dropped += 1
                drop_log.append([station, target_date.isoformat(), err])
                continue
            n_kept += 1
            all_rows.append(row)
        print(f"{station}: {n_kept} kept, {n_dropped} dropped "
              f"(of {(WINDOW_END - WINDOW_START).days + 1} window days)")

    out_csv = PROCESSED / "grib_features_sealed_window.csv"
    fieldnames = ["station", "target_date", "target_hour", "run_date", "cycle", "lead",
                  "temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nWrote assembled sealed-year dataset: {out_csv} ({len(all_rows)} rows)")

    out_drops = PROCESSED / "grib_features_sealed_window_drops.csv"
    with open(out_drops, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "reason"])
        w.writerows(drop_log)
    print(f"Wrote drop log: {out_drops} ({len(drop_log)} rows)")


if __name__ == "__main__":
    main()
