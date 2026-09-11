"""Session 37, Tasks 3-4: decode every pulled GRIB2 extract, apply the
Task-1 elevation correction to temperature, derive wind speed from u/v,
validate cloud cover and wind speed against Open-Meteo on the overlap
window, and assemble the final validated GRIB feature dataset.

ONE JOB, in three parts:

Task 3 (validate cloud/wind): on 2024-01-19..2025-07-31, where Open-Meteo
also has cloud_cover_previous_day1 and wind_speed_10m_previous_day1 (SPEC
3.2, DECISIONS F85), compare the GRIB-derived values (bilinear-interpolated
to each airport's established grid point, SPEC 3.4) against Open-Meteo's
own already-pulled series (data/raw/features/*_cloudwind.json). Read-only:
nothing under data/raw/features/ is modified.

Task 4 (assemble): build one row per (station, target_date) over the full
v16-only training window (2021-03-24..2025-07-31), with elevation-corrected
temperature, cloud cover and wind speed, all GRIB-derived. Report
per-airport row and drop counts (SPEC 2.2 -- nothing is filled). Save as
clearly-labelled processed data, separate from the raw GRIB extracts and
from the existing Open-Meteo files.

Does NOT join to any observation, fit any model, or touch the sealed test
year (2025-08-01 onward) at any point -- both bounds are asserted before
use.
"""

import csv
import json
from datetime import date, timedelta
from pathlib import Path

import eccodes as ec

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
GRIB = RAW / "grib"
FEATURES = RAW / "features"
DIAG37 = RAW / "diagnostics" / "session37"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

WINDOW_START = date(2021, 3, 24)
WINDOW_END = date(2025, 7, 31)
OVERLAP_START = date(2024, 1, 19)   # cloud/wind's own first real hour (F85)
OVERLAP_END = WINDOW_END

# SPEC 3.4: station -> (target hour UTC, grid latitude, grid longitude).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}

OPENMETEO_CLOUDWIND_FILES = {
    "EGLC": "openmeteo_previousruns_gfs_global_EGLC_2024-01-19_2025-07-31_cloudwind.json",
    "LFPG": "openmeteo_previousruns_gfs_global_LFPG_2024-01-19_2025-07-31_cloudwind.json",
    "DSM": "openmeteo_previousruns_gfs_global_DSM_2024-01-19_2025-07-31_cloudwind.json",
    "YSDU": "openmeteo_previousruns_gfs_global_YSDU_2024-01-19_2025-07-31_cloudwind.json",
    "RNO": "openmeteo_previousruns_gfs_global_RNO_2024-01-19_2025-07-31_cloudwind.json",
}


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def load_elevation_corrections():
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


def load_openmeteo_cloudwind(station):
    path = FEATURES / OPENMETEO_CLOUDWIND_FILES[station]
    d = json.load(open(path))
    h = d["hourly"]
    cloud = dict(zip(h["time"], h["cloud_cover_previous_day1"]))
    wind = dict(zip(h["time"], h["wind_speed_10m_previous_day1"]))
    return cloud, wind


def daterange(start, end):
    d = start
    while d <= end:
        yield d
        d += timedelta(days=1)


def main():
    assert WINDOW_START == date(2021, 3, 24)
    assert WINDOW_END == date(2025, 7, 31)
    assert OVERLAP_START == date(2024, 1, 19)
    assert OVERLAP_END <= date(2025, 7, 31), "overlap window reaches into the sealed test year"

    elev_corr = load_elevation_corrections()
    print("Elevation corrections (degC, from session37_elevation_fix.py):")
    for s, c in elev_corr.items():
        print(f"  {s}: {c:+.4f}")

    # ---- decode every row over the full window (Task 4's dataset) --------
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

    out_csv = PROCESSED / "grib_features_v16_window.csv"
    fieldnames = ["station", "target_date", "target_hour", "run_date", "cycle", "lead",
                  "temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nWrote assembled dataset: {out_csv} ({len(all_rows)} rows)")

    out_drops = PROCESSED / "grib_features_v16_window_drops.csv"
    with open(out_drops, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "reason"])
        w.writerows(drop_log)
    print(f"Wrote drop log: {out_drops} ({len(drop_log)} rows)")

    # ---- Task 3: validate cloud/wind against Open-Meteo on the overlap ---
    print("\n=== Task 3: cloud/wind validation against Open-Meteo "
          f"({OVERLAP_START} .. {OVERLAP_END}) ===")
    validation_rows = []
    for station, (target_hour, lat, lon) in AIRPORTS.items():
        om_cloud, om_wind = load_openmeteo_cloudwind(station)
        cloud_diffs, wind_diffs = [], []
        for r in all_rows:
            if r["station"] != station:
                continue
            td = date.fromisoformat(r["target_date"])
            if not (OVERLAP_START <= td <= OVERLAP_END):
                continue
            key = f"{r['target_date']}T{r['target_hour']:02d}:00"
            om_c = om_cloud.get(key)
            om_w = om_wind.get(key)
            if om_c is not None:
                cloud_diffs.append(r["cloud_cover_grib_pct"] - om_c)
            if om_w is not None:
                wind_diffs.append(r["wind_speed_grib_kmh"] - om_w)
            validation_rows.append({
                "station": station, "target_date": r["target_date"],
                "cloud_grib": r["cloud_cover_grib_pct"], "cloud_openmeteo": om_c,
                "wind_grib_kmh": r["wind_speed_grib_kmh"], "wind_openmeteo_kmh": om_w,
            })

        def summarize(diffs, label, pass_threshold):
            if not diffs:
                return f"{label}: NO COMPARABLE ROWS -> FAIL"
            mean_abs = sum(abs(d) for d in diffs) / len(diffs)
            mean_signed = sum(diffs) / len(diffs)
            max_abs = max(abs(d) for d in diffs)
            verdict = "PASS" if mean_abs < pass_threshold else "FAIL"
            return (f"{label}: n={len(diffs)} mean|diff|={mean_abs:.3f} "
                    f"mean_diff={mean_signed:+.3f} max|diff|={max_abs:.3f} -> {verdict}")

        # Thresholds set this session for this diagnostic only (not a SPEC-
        # frozen bar): cloud cover is a noisier, more definitional quantity
        # than temperature (instantaneous total-column fraction vs whatever
        # exact vertical/temporal aggregation Open-Meteo's own field uses),
        # so 15 percentage points is used as "close enough to trust the
        # pre-2024 period"; wind speed similarly allows 3 km/h for grid/
        # interpolation-method differences. Both are reported in full either
        # way, so the reader is never dependent on the threshold alone.
        print(f"{station}: {summarize(cloud_diffs, 'cloud_cover (pct)', 15.0)}")
        print(f"{station}: {summarize(wind_diffs, 'wind_speed (km/h)', 3.0)}")

    out_val = PROCESSED / "grib_vs_openmeteo_cloudwind_validation.csv"
    fieldnames_v = ["station", "target_date", "cloud_grib", "cloud_openmeteo",
                     "wind_grib_kmh", "wind_openmeteo_kmh"]
    with open(out_val, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames_v)
        w.writeheader()
        w.writerows(validation_rows)
    print(f"\nWrote cloud/wind validation table: {out_val} ({len(validation_rows)} rows)")


if __name__ == "__main__":
    main()
