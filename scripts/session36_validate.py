"""Session 36, Tasks 4-5: grid->point interpolation, lead-time convention,
and the reproduce-the-results gate.

ONE JOB: decode every GRIB2 extract session36_grib_pull.py saved, bilinear-
interpolate the 0.25 deg field to each airport's own established Open-Meteo
grid point (SPEC 3.4's "grid latitude"/"grid longitude" columns -- the exact
point Open-Meteo's own temperature series already answers for), and compare
against the existing, already-validated Open-Meteo temperature_2m_previous_day1
value at the same valid hour. This is the pipeline validation gate: if the
GRIB-derived value matches Open-Meteo closely, the interpolation and lead-time
logic are trustworthy for the later cloud/wind bulk pull (which has no such
answer key).

Reads existing Open-Meteo raw pulls for comparison ONLY -- nothing in
data/raw/ is modified, re-pulled, or overwritten.
"""

import json
import math
from datetime import date, timedelta
from pathlib import Path

import eccodes as ec

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session36"

# SPEC 3.4: station code -> (target hour UTC, grid latitude, grid longitude)
# grid lat/lon is Open-Meteo's own established point for this airport -- the
# exact point this pipeline must reproduce, not the raw airport position.
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}

# Existing local Open-Meteo full-window pull files that cover each sample
# window, per airport. Read-only.
OPENMETEO_FILES = {
    "early": {  # covers 2021-03-24 .. 2021-03-28
        "EGLC": "openmeteo_previousruns_gfs_global_EGLC_2021-03-24_2021-12-31.json",
        "LFPG": "openmeteo_previousruns_gfs_global_LFPG_2021-03-24_2021-12-31.json",
        "DSM": "openmeteo_previousruns_gfs_global_DSM_2021-03-24_2021-12-31.json",
        "YSDU": "openmeteo_previousruns_gfs_global_YSDU_2021-03-24_2021-12-31.json",
        "RNO": "openmeteo_previousruns_gfs_global_RNO_2021-03-24_2021-12-31.json",
    },
    "recent": {  # covers 2025-06-01 .. 2025-06-14
        "EGLC": "openmeteo_previousruns_gfs_global_EGLC_2025-01-01_2025-12-31.json",
        "LFPG": "openmeteo_previousruns_gfs_global_LFPG_2025-01-01_2025-12-31.json",
        "DSM": "openmeteo_previousruns_gfs_global_DSM_2025-01-01_2025-12-31.json",
        "YSDU": "openmeteo_previousruns_gfs_global_YSDU_2025-01-01_2025-12-31.json",
        "RNO": "openmeteo_previousruns_gfs_global_RNO_2025-01-01_2025-12-31.json",
    },
}

EARLY_SAMPLE = [date(2021, 3, 24) + timedelta(days=i) for i in range(5)]
RECENT_SAMPLE = [date(2025, 6, 1) + timedelta(days=i) for i in range(14)]


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_extract_path(run_date, cycle, lead):
    fname = f"gfs_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{lead:03d}_tmp2m.grib2"
    return DIAG / fname


def bilinear_from_grib(path, lat, lon):
    """Decode the single TMP:2m message in `path` and bilinear-interpolate
    to (lat, lon) using the four surrounding 0.25 deg grid points."""
    with open(path, "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
        if gid is None:
            raise ValueError(f"no GRIB message decoded from {path}")
        short_name = ec.codes_get(gid, "shortName")
        valid_date = ec.codes_get(gid, "validityDate")
        valid_time = ec.codes_get(gid, "validityTime")
        neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
        ec.codes_release(gid)

    if short_name != "2t":
        raise ValueError(f"expected shortName '2t', got '{short_name}' in {path}")

    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    if len(lats) != 2 or len(lons) != 2:
        # target sits exactly on a grid line in one dimension (find_nearest
        # can return duplicate points in that case) -- fall back to the
        # single nearest value, which is exact in that dimension already.
        lat_span = (max(n.lat for n in neighbours) - min(n.lat for n in neighbours))
        lon_span = (max(n.lon for n in neighbours) - min(n.lon for n in neighbours))
        if lat_span < 1e-6 or lon_span < 1e-6:
            best = min(neighbours, key=lambda n: n.distance)
            return best.value - 273.15, valid_date, valid_time
        raise ValueError(f"unexpected neighbour layout for {path}: {[(n.lat, n.lon) for n in neighbours]}")

    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00 = grid[(lat0, lon0)]
    v01 = grid[(lat0, lon1)]
    v10 = grid[(lat1, lon0)]
    v11 = grid[(lat1, lon1)]

    # The GRIB grid's longitudes come back in 0-360 convention (eccodes
    # handles a negative query lon internally for find_nearest, but the
    # returned neighbour lons -- and hence lon0/lon1 here -- are always
    # 0-360), so the query lon must be normalised the same way before it is
    # used in the weight arithmetic below.
    lon_q = lon + 360.0 if lon < 0 else lon

    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)

    value_k = (
        (1 - dlat) * (1 - dlon) * v00
        + (1 - dlat) * dlon * v01
        + dlat * (1 - dlon) * v10
        + dlat * dlon * v11
    )
    return value_k - 273.15, valid_date, valid_time


def load_openmeteo_series(path):
    d = json.load(open(path))
    h = d["hourly"]
    return dict(zip(h["time"], h["temperature_2m_previous_day1"]))


def main():
    rows = []
    om_cache = {}

    for sample_name, sample_dates in (("early", EARLY_SAMPLE), ("recent", RECENT_SAMPLE)):
        for station, (target_hour, grid_lat, grid_lon) in AIRPORTS.items():
            om_key = (sample_name, station)
            if om_key not in om_cache:
                om_cache[om_key] = load_openmeteo_series(RAW / OPENMETEO_FILES[sample_name][station])
            om_series = om_cache[om_key]

            cycle, lead = cycle_and_lead(target_hour)
            for target_date in sample_dates:
                run_date = target_date - timedelta(days=1)
                grib_path = grib_extract_path(run_date, cycle, lead)
                if not grib_path.exists():
                    rows.append({
                        "sample": sample_name, "station": station,
                        "target_date": target_date.isoformat(), "target_hour": target_hour,
                        "error": f"missing GRIB extract {grib_path.name}",
                    })
                    continue

                grib_temp_c, valid_date, valid_time = bilinear_from_grib(grib_path, grid_lat, grid_lon)

                expected_valid = f"{target_date.isoformat()}"
                got_valid = f"{str(valid_date)[:4]}-{str(valid_date)[4:6]}-{str(valid_date)[6:8]}"
                valid_hour = valid_time // 100
                valid_ok = (got_valid == expected_valid) and (valid_hour == target_hour)

                om_time_key = f"{target_date.isoformat()}T{target_hour:02d}:00"
                om_temp_c = om_series.get(om_time_key)

                rows.append({
                    "sample": sample_name, "station": station,
                    "target_date": target_date.isoformat(), "target_hour": target_hour,
                    "run_date": run_date.isoformat(), "cycle": cycle, "lead": lead,
                    "grib_valid": f"{got_valid}T{valid_hour:02d}:00", "valid_ok": valid_ok,
                    "grib_temp_c": round(grib_temp_c, 3),
                    "openmeteo_temp_c": om_temp_c,
                    "diff_c": None if om_temp_c is None else round(grib_temp_c - om_temp_c, 3),
                    "error": None,
                })

    # ---- write comparison table -----------------------------------------
    out_csv = DIAG / "session36_grib_vs_openmeteo_comparison.csv"
    fieldnames = ["sample", "station", "target_date", "target_hour", "run_date",
                  "cycle", "lead", "grib_valid", "valid_ok", "grib_temp_c",
                  "openmeteo_temp_c", "diff_c", "error"]
    import csv
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})
    print(f"Wrote comparison table: {out_csv}  ({len(rows)} rows)")

    # ---- per-airport summary + PASS/FAIL ----------------------------------
    print("\nPer-airport reproduction check (GRIB-derived vs existing Open-Meteo temperature_2m_previous_day1):")
    print(f"{'station':6s} {'n':>3s} {'mean|diff|':>10s} {'mean diff':>10s} {'max|diff|':>10s} {'verdict':>8s}")
    verdicts = {}
    for station in AIRPORTS:
        diffs = [r["diff_c"] for r in rows if r["station"] == station and r.get("diff_c") is not None]
        bad_valid = [r for r in rows if r["station"] == station and r.get("valid_ok") is False]
        errors = [r for r in rows if r["station"] == station and r.get("error")]
        if not diffs:
            print(f"{station:6s}   0          -          -          -     FAIL (no comparable rows)")
            verdicts[station] = "FAIL (no comparable rows)"
            continue
        mean_abs = sum(abs(d) for d in diffs) / len(diffs)
        mean_signed = sum(diffs) / len(diffs)
        max_abs = max(abs(d) for d in diffs)
        # PASS: sub-degree mean absolute difference, no large systematic bias.
        verdict = "PASS" if (mean_abs < 1.0 and abs(mean_signed) < 1.0) else "FAIL"
        if bad_valid or errors:
            verdict = "FAIL"
        print(f"{station:6s} {len(diffs):3d} {mean_abs:10.3f} {mean_signed:10.3f} {max_abs:10.3f} {verdict:>8s}"
              + (f"  [{len(bad_valid)} valid-time mismatches]" if bad_valid else "")
              + (f"  [{len(errors)} errors]" if errors else ""))
        verdicts[station] = verdict

    overall = "PROVEN" if all(v == "PASS" for v in verdicts.values()) else "NOT PROVEN"
    print(f"\nOverall pipeline verdict: {overall}")

    errs = [r for r in rows if r.get("error")]
    if errs:
        print(f"\n{len(errs)} rows had errors:")
        for r in errs[:20]:
            print(f"  {r['sample']} {r['station']} {r['target_date']}: {r['error']}")

    return rows, verdicts, overall


if __name__ == "__main__":
    main()
