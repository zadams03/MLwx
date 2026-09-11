"""Session 37, Task 1: RNO elevation/lapse-rate downscaling, then re-run the
session-36 reproduction gate at all five airports.

ONE JOB: session 36 (DECISIONS F89) found the GRIB->point temperature
pipeline reproduces Open-Meteo cleanly at EGLC/LFPG/DSM/YSDU but fails at
RNO with a clean, one-sided ~-2.04 degC bias, traced to real terrain: the
raw GRIB grid points around RNO's own established grid point carry model
orography 246-570 m higher than RNO's real/grid elevation. This script:

1. fetches the HGT:surface (model terrain) message for the four airports
   that did not already get one in session 36 (RNO's is reused as-is,
   byte-range only, no re-fetch);
2. bilinear-interpolates it to each airport's own established grid point,
   the same way temperature is interpolated;
3. computes each airport's static grid-orography-vs-Open-Meteo-grid-
   elevation gap (SPEC 3.4's "grid elevation" column -- the elevation
   Open-Meteo's own downscaled value is evidently referenced to, per F89);
4. tries two lapse rates -- the standard environmental lapse rate
   (6.5 degC/km) and one solved exactly to zero out RNO's own measured
   mean bias -- applies each to session 36's already-saved 95-row
   comparison table (data/raw/diagnostics/session36/
   session36_grib_vs_openmeteo_comparison.csv), and reports which
   reproduces Open-Meteo best, at RNO specifically and at all five
   airports together (the flat airports' own tiny gaps must not break
   their existing PASS).

This does not touch the sealed test year, does not pull the Task 2 bulk
feature set, and does not join or fit anything -- it only establishes the
correction (a per-airport constant: grid elevation gap, plus the chosen
lapse rate) that session37_decode.py then applies to every temperature
extract Task 2 pulls.
"""

import csv
import time
import urllib.request
from pathlib import Path

import eccodes as ec

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DIAG36 = RAW / "diagnostics" / "session36"
DIAG37 = RAW / "diagnostics" / "session37"
DIAG37.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station -> (target hour UTC, grid latitude, grid longitude,
# grid elevation m -- Open-Meteo's own reported elevation for this exact
# grid point, which is what F89 read as the elevation Open-Meteo's
# downscaled value is referenced to).
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0, 4.0),
    "LFPG": (12, 49.027008, 2.578125, 109.0),
    "DSM":  (18, 41.52945, -93.63281, 285.0),
    "YSDU": (2, -32.274643, 148.59375, 279.0),
    "RNO":  (20, 39.537918, -119.765625, 1344.0),
}

# One representative run used to sample HGT:surface (model terrain is a
# static field -- the same physical orography value at a given grid point
# comes back from any run/lead of the same model version, so one sample
# per airport is sufficient; RNO's own sample is session 36's existing
# diagnostic pull, reused byte-for-byte, not re-fetched).
SAMPLE_RUN_DATE = "20250610"

RNO_EXISTING_HGT = DIAG36 / "gfs_20250610_t18z_f026_hgt_surface_RNO_diagnostic.grib2"


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_url(run_date_str, cycle_hour):
    return f"{BUCKET}/gfs.{run_date_str}/{cycle_hour:02d}/atmos/gfs.t{cycle_hour:02d}z.pgrb2.0p25"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "MLwx/session37"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_hgt_surface(station, cycle, lead):
    base_url = grib_url(SAMPLE_RUN_DATE, cycle)
    idx_url = f"{base_url}.f{lead:03d}.idx"
    idx_text = _get(idx_url).decode("utf-8")
    lines = idx_text.strip().split("\n")
    start = end = None
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 5 and parts[3] == "HGT" and parts[4] == "surface":
            start = int(parts[1])
            if i + 1 < len(lines):
                end = int(lines[i + 1].split(":")[1]) - 1
            break
    if start is None:
        raise ValueError(f"HGT:surface not found in {idx_url}")
    grib_url_ = f"{base_url}.f{lead:03d}"
    range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
    content = _get(grib_url_, headers={"User-Agent": "MLwx/session37", "Range": range_hdr})

    fname_base = f"gfs_{SAMPLE_RUN_DATE}_t{cycle:02d}z_f{lead:03d}_hgt_surface_{station}_diagnostic"
    out_grib = DIAG37 / f"{fname_base}.grib2"
    out_meta = DIAG37 / f"{fname_base}.grib2.meta.txt"
    out_grib.write_bytes(content)
    pull_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    out_meta.write_text(
        f"source: {grib_url_}\n"
        f"idx source: {idx_url}\n"
        f"byte range requested: {start}-{end}\n"
        f"variable: HGT:surface (model terrain elevation), forecast hour f{lead:03d}, "
        f"cycle {cycle:02d}z, run date {SAMPLE_RUN_DATE}\n"
        f"purpose: session 37 Task 1 -- one static-terrain sample per airport, to "
        f"compute the grid-orography-vs-Open-Meteo-grid-elevation gap used for the "
        f"elevation/lapse-rate downscaling correction.\n"
        f"pulled (UTC): {pull_time}\n"
        f"bytes saved: {len(content)}\n"
        f"first 4 bytes: {content[:4]!r}  last 4 bytes: {content[-4:]!r}\n"
    )
    return out_grib


def bilinear_value(path, lat, lon, expected_short_name):
    with open(path, "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
        if gid is None:
            raise ValueError(f"no GRIB message decoded from {path}")
        short_name = ec.codes_get(gid, "shortName")
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
            return best.value
        raise ValueError(f"unexpected neighbour layout for {path}: {[(n.lat, n.lon) for n in neighbours]}")

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


def evaluate(lapse_c_per_km, gaps, rows):
    """Apply a constant per-airport elevation correction and recompute the
    reproduction-gate table. gaps: station -> orog_interp_m - grid_elev_m."""
    per_station = {}
    for station in AIRPORTS:
        diffs = []
        for r in rows:
            if r["station"] != station or r["diff_c"] == "":
                continue
            corr = lapse_c_per_km / 1000.0 * gaps[station]
            corrected_diff = float(r["diff_c"]) + corr
            diffs.append(corrected_diff)
        if not diffs:
            continue
        mean_abs = sum(abs(d) for d in diffs) / len(diffs)
        mean_signed = sum(diffs) / len(diffs)
        max_abs = max(abs(d) for d in diffs)
        verdict = "PASS" if (mean_abs < 1.0 and abs(mean_signed) < 1.0) else "FAIL"
        per_station[station] = (len(diffs), mean_abs, mean_signed, max_abs, verdict)
    return per_station


def main():
    print("=== Task 1: HGT:surface pull for the four airports without one ===")
    hgt_paths = {"RNO": RNO_EXISTING_HGT}
    for station, (target_hour, lat, lon, grid_elev) in AIRPORTS.items():
        if station == "RNO":
            print(f"  {station}: reusing session 36's existing diagnostic pull (no re-fetch)")
            continue
        cycle, lead = cycle_and_lead(target_hour)
        path = fetch_hgt_surface(station, cycle, lead)
        hgt_paths[station] = path
        print(f"  {station}: fetched {path.name} (cycle {cycle:02d}z f{lead:03d}, run {SAMPLE_RUN_DATE})")

    print("\n=== Interpolated model orography at each airport's grid point ===")
    print(f"{'station':6s} {'orog_interp_m':>14s} {'om_grid_elev_m':>15s} {'gap_m':>10s}")
    gaps = {}
    orog_interp = {}
    for station, (target_hour, lat, lon, grid_elev) in AIRPORTS.items():
        orog = bilinear_value(hgt_paths[station], lat, lon, "orog")
        gap = orog - grid_elev
        orog_interp[station] = orog
        gaps[station] = gap
        print(f"{station:6s} {orog:14.2f} {grid_elev:15.1f} {gap:10.2f}")

    print("\n=== Reproduction gate BEFORE correction (session 36 as-published) ===")
    with open(DIAG36 / "session36_grib_vs_openmeteo_comparison.csv") as f:
        rows = list(csv.DictReader(f))
    before = evaluate(0.0, gaps, rows)
    print(f"{'station':6s} {'n':>3s} {'mean|diff|':>10s} {'mean diff':>10s} {'max|diff|':>10s} {'verdict':>8s}")
    for station, (n, ma, ms, mx, v) in before.items():
        print(f"{station:6s} {n:3d} {ma:10.3f} {ms:10.3f} {mx:10.3f} {v:>8s}")

    # Candidate 1: standard environmental lapse rate, 6.5 degC/km.
    # Candidate 2: exact fit to RNO's own measured mean bias (F89: -2.044
    # degC, essentially a pure offset -- mean|diff| == |mean diff| already),
    # solved as lapse_c_per_km = 1000 * mean_bias_magnitude / gap_m(RNO).
    rno_mean_bias = before["RNO"][2]  # signed mean diff, degC (negative: GRIB colder)
    fit_lapse = 1000.0 * (-rno_mean_bias) / gaps["RNO"]

    candidates = {"standard (6.5 degC/km)": 6.5, f"RNO-fit ({fit_lapse:.3f} degC/km)": fit_lapse}

    best_name, best_lapse, best_result = None, None, None
    for name, lapse in candidates.items():
        print(f"\n=== Reproduction gate AFTER correction: {name} ===")
        result = evaluate(lapse, gaps, rows)
        print(f"{'station':6s} {'n':>3s} {'mean|diff|':>10s} {'mean diff':>10s} {'max|diff|':>10s} {'verdict':>8s}")
        for station, (n, ma, ms, mx, v) in result.items():
            print(f"{station:6s} {n:3d} {ma:10.3f} {ms:10.3f} {mx:10.3f} {v:>8s}")
        all_pass = all(v == "PASS" for (_, _, _, _, v) in result.values())
        rno_mean_abs = result["RNO"][1]
        print(f"all five PASS: {all_pass}   RNO mean|diff|: {rno_mean_abs:.3f}")
        if best_result is None or rno_mean_abs < best_result["RNO"][1]:
            best_name, best_lapse, best_result = name, lapse, result

    print(f"\n=== Chosen correction: {best_name} ===")
    all_pass = all(v == "PASS" for (_, _, _, _, v) in best_result.values())
    print(f"all five PASS: {all_pass}")

    # Save the chosen per-airport correction parameters for session37_decode.py.
    out_params = DIAG37 / "session37_elevation_correction_params.csv"
    with open(out_params, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "orog_interp_m", "om_grid_elev_m", "gap_m", "lapse_c_per_km", "correction_c"])
        for station in AIRPORTS:
            corr = best_lapse / 1000.0 * gaps[station]
            w.writerow([station, round(orog_interp[station], 2), AIRPORTS[station][3],
                        round(gaps[station], 2), round(best_lapse, 4), round(corr, 4)])
    print(f"\nWrote correction parameters: {out_params}")
    return best_name, best_lapse, gaps, best_result


if __name__ == "__main__":
    main()
