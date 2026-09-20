"""Session 49: build and validate the upper-air/vertical-structure (E1)
feature set -- TMP at 925, 850, and 700 hPa, plus a derived lapse-rate
feature -- for every date already in the existing 5-feature GRIB dataset
that falls OUTSIDE the reserved 2024-25 confirmation year (DECISIONS D51).

Data-build-only session. No model fit, no MAE, no CV -- session 50 runs the
actual staged E1 experiment on the output of this script.

Design choices, stated up front (session prompt Step 3/4):

- 925/850/700 hPa are FIXED PRESSURE SURFACES, not tied to surface terrain.
  Unlike the existing 5-feature model's surface 2 m temperature, they get
  bilinear horizontal interpolation ONLY -- SPEC 7.2's 7.429 degC/km
  elevation/lapse-rate correction exists to fix a *surface* grid-cell
  elevation mismatch and does NOT apply to a fixed pressure level. It is
  not applied to t925/t850/t700 anywhere in this script.
- The lapse-rate feature (`lapse_rate_t2_t850`) is derived from the RAW,
  uncorrected 2 m GFS forecast temperature (`t2m_raw`), not the
  elevation-corrected `temperature_grib_c` the existing 5-feature model
  already uses as `temp`. Rather than re-pulling 2 m temperature (already
  decoded once for the existing dataset), `t2m_raw` is recovered
  algebraically from data already on disk:
      t2m_raw = temperature_grib_c - correction_c
  using each airport's own fixed per-airport elevation-correction constant
  (DECISIONS D48.3/F90, session37_elevation_correction_params.csv). This
  needs no new GRIB pull for 2 m temperature.
- No raw GRIB2 bytes are kept on disk for this pull. Free disk space is
  currently ~11 GiB (session 37's own ~20 GB surface-field raw cache,
  gitignored under D47, already sits on this disk). A second full-window,
  3-level raw cache the same way session 37/40 did it would need on the
  order of 15+ GB more, which this environment does not have. Each message
  is byte-range-fetched, decoded immediately with eccodes, and the bytes
  discarded -- the same fetch-decode-discard pattern session 47's own probe
  already used, not session 37/40's fetch-then-decode-later pattern. A
  per-request manifest (no bytes) is kept instead, per SPEC 2.3's
  provenance intent and D47's "manifest, not bytes" policy for large,
  re-fetchable sources -- carried one step further here, since not even a
  disposable local cache is kept.
- The reserved confirmation year (2024-08-01..2025-07-31, DECISIONS D51) is
  never loaded from the existing dataset, never included in the pull's date
  list, and never joined -- enforced by filtering every date against
  scripts/session48_reserved_year.py's own constants and guard function
  before anything else happens.
"""

import csv
import sys
import time
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
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session49"
DIAG.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

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

# F97's own confirmed (var_code, level) labels -- reused verbatim, not
# re-derived (session prompt Step 1).
LEVELS = {
    "t925": ("TMP", "925 mb"),
    "t850": ("TMP", "850 mb"),
    "t700": ("TMP", "700 mb"),
}

MAX_WORKERS = 48
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session49"})


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
    """Exact-match the message whose step field is 'N hour fcst' (same
    disambiguation session 37 used for TCDC). F97 found upper-air TMP has no
    averaging-window complication, but the exact-step match is kept anyway
    so a surprise is reported, not silently mismatched."""
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
    levels once, bilinear-interpolating to every station sharing this
    combo. No raw GRIB2 bytes survive past this function (module docstring).
    Returns (results, manifest_rows) where results[level_key] is either a
    {station: value_kelvin} dict or None (failed)."""
    base_url = grib_base_url(run_date, cycle)
    idx_url = f"{base_url}.f{lead:03d}.idx"
    manifest_rows = []
    results = {}
    stations_str = ",".join(sorted(stations))

    try:
        idx_text = _get_with_retries(idx_url).decode("utf-8")
    except Exception as e:
        for level_key in LEVELS:
            manifest_rows.append([run_date.isoformat(), cycle, lead, level_key,
                                   stations_str, "FAIL", f"idx fetch failed: {e}"])
        return {lk: None for lk in LEVELS}, manifest_rows

    target_date_str = (run_date + timedelta(days=1)).isoformat()

    for level_key, (var_code, level) in LEVELS.items():
        try:
            start, end = find_message_range(idx_text, var_code, level, lead)
            if start is None:
                raise ValueError(f"'{var_code}:{level}:{lead} hour fcst' not found in idx")
            grib_url = f"{base_url}.f{lead:03d}"
            range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
            content = _get_with_retries(grib_url, headers={"Range": range_hdr})
            if content[:4] != b"GRIB" or content[-4:] != b"7777":
                raise ValueError("bad magic markers (not a complete GRIB2 message)")

            tmp_path = DIAG / f"_scratch_{run_date.isoformat()}_{cycle:02d}_{lead:03d}_{level_key}.grib2"
            tmp_path.write_bytes(content)
            try:
                with open(tmp_path, "rb") as f:
                    gid = ec.codes_grib_new_from_file(f)
                    if gid is None:
                        raise ValueError("eccodes could not decode a message")
                    short_name = ec.codes_get(gid, "shortName")
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

            results[level_key] = station_values  # Kelvin, converted later
            manifest_rows.append([run_date.isoformat(), cycle, lead, level_key,
                                   stations_str, "OK",
                                   f"short_name={short_name} valid={got_valid}T{valid_hour:02d}:00 bytes={len(content)}"])
        except Exception as e:
            results[level_key] = None
            manifest_rows.append([run_date.isoformat(), cycle, lead, level_key,
                                   stations_str, "FAIL", str(e)])

    return results, manifest_rows


def build_joined(span_name, existing_csv, decoded, elev_corr):
    with open(existing_csv) as f:
        existing_rows = list(csv.DictReader(f))
    fieldnames = list(existing_rows[0].keys()) + ["t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850"]
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
        missing = [lk for lk in LEVELS if dec is None or dec.get(lk) is None]
        if missing:
            drop_log.append([station, d.isoformat(), span_name, f"missing decoded field(s): {missing}"])
            continue
        t2m_raw = round(float(row["temperature_grib_c"]) - elev_corr[station], 3)
        new_row = dict(row)
        new_row["t2m_raw"] = t2m_raw
        new_row["t925"] = round(dec["t925"], 3)
        new_row["t850"] = round(dec["t850"], 3)
        new_row["t700"] = round(dec["t700"], 3)
        new_row["lapse_rate_t2_t850"] = round(t2m_raw - dec["t850"], 3)
        out_rows.append(new_row)
        per_station_after[station] = per_station_after.get(station, 0) + 1

    out_csv = PROCESSED / f"session49_{span_name}_with_upper_air.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, per_station_before, per_station_after, drop_log


def main():
    print("=" * 78)
    print("SESSION 49 -- upper-air (E1) feature build. Data-build only: no")
    print("model fit, no MAE, no CV. The reserved year (2024-08-01..2025-07-31,")
    print("DECISIONS D51) is never loaded, pulled, or joined.")
    print("=" * 78)

    print("\nUnderstanding confirmed before any pull runs (session prompt Step 3):")
    print("  925/850/700 hPa are FIXED PRESSURE SURFACES, not surface-terrain-tied.")
    print("  They get bilinear horizontal interpolation ONLY. The 7.429 degC/km")
    print("  surface elevation/lapse-rate correction (SPEC 7.2) is NOT applied to")
    print("  t925/t850/t700 anywhere in this script -- applying it here would be")
    print("  a real error, not a style choice, since these levels are not tied")
    print("  to the airport's own surface elevation at all.")

    per_station = load_existing_dates()

    all_dates = sorted({d for dm in per_station.values() for d in dm})
    train_dates = sorted({d for d in all_dates if d < RESERVED_YEAR_START})
    sealed_dates = sorted({d for d in all_dates if d > RESERVED_YEAR_END})
    print("\nDate list built from the existing 5-feature dataset, reserved year excluded:")
    print(f"  train span : {train_dates[0]} .. {train_dates[-1]}  ({len(train_dates)} distinct dates)")
    print(f"  sealed span: {sealed_dates[0]} .. {sealed_dates[-1]}  ({len(sealed_dates)} distinct dates)")

    # Guard check, per session prompt Step 5: exercise the shared guard
    # function on both spans (train==test here, since this is a single
    # continuous span being pulled, not a train/test fold).
    assert_reserved_year_excluded("session49-train-span", train_dates[0], train_dates[-1],
                                   train_dates[0], train_dates[-1])
    assert_reserved_year_excluded("session49-sealed-span", sealed_dates[0], sealed_dates[-1],
                                   sealed_dates[0], sealed_dates[-1])
    # Defensive per-date check too (the "equivalent per-date check" the
    # session prompt allows), independent of the two range checks above.
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
    print(f"3 levels/combo -> up to {n_combos} idx fetches + {n_combos * 3} message fetches "
          f"({n_combos * 4} total requests)")

    # ---- pull + decode; no raw bytes kept on disk (module docstring) ------
    manifest_rows = []
    per_field_counts = {lk: {"requested": 0, "ok": 0} for lk in LEVELS}
    decoded = {s: {} for s in AIRPORTS}  # decoded[station][date][level_key] = value_c

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
            for level_key in LEVELS:
                per_field_counts[level_key]["requested"] += len(stations)
                vals_k = results.get(level_key)
                if vals_k is not None:
                    per_field_counts[level_key]["ok"] += len(stations)
                    for station in stations:
                        decoded[station].setdefault(target_date, {})[level_key] = vals_k[station] - 273.15
            n_done += 1
            if n_done % 500 == 0 or n_done == n_combos:
                elapsed = time.time() - t0
                rate = n_done / elapsed if elapsed > 0 else 0
                eta = (n_combos - n_done) / rate if rate > 0 else float("inf")
                print(f"  {n_done}/{n_combos} combos  elapsed={elapsed/60:.1f}min  "
                      f"rate={rate:.2f}/s  eta={eta/60:.1f}min", flush=True)

    elapsed = time.time() - t0
    print(f"\nPull+decode done in {elapsed/60:.1f} min.")

    # ---- Step 7 (validation), part a: requested vs decoded per field ------
    print("\n=== Validation (a): messages requested vs. decoded, per field ===")
    print("(counted per station-instance -- a shared combo like EGLC+LFPG counts twice)")
    for level_key, counts in per_field_counts.items():
        failed = counts["requested"] - counts["ok"]
        print(f"  {level_key} ({LEVELS[level_key][0]}:{LEVELS[level_key][1]}): "
              f"requested={counts['requested']} decoded_ok={counts['ok']} failed={failed}")

    manifest_csv = DIAG / "session49_pull_manifest.csv"
    with open(manifest_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run_date", "cycle", "lead", "level_key", "stations", "status", "detail"])
        w.writerows(manifest_rows)
    n_fail_rows = sum(1 for r in manifest_rows if r[5] == "FAIL")
    print(f"\nWrote pull manifest (provenance record, no raw bytes kept): "
          f"{manifest_csv} ({len(manifest_rows)} rows, {n_fail_rows} FAIL)")
    if n_fail_rows:
        print("  Failure reasons (SPEC 2.2 -- every drop is counted and given a reason):")
        for r in manifest_rows:
            if r[5] == "FAIL":
                print(f"    {r[0]} cycle={r[1]:02d}z lead=f{r[2]:03d} {r[3]} stations={r[4]}: {r[6]}")

    # ---- derive t2m_raw + lapse rate, join onto existing dataset ----------
    elev_corr = load_elevation_corrections()
    print("\nElevation corrections used to recover t2m_raw (D48.3/F90, unchanged, NOT")
    print("applied to t925/t850/t700): t2m_raw = temperature_grib_c - correction_c")
    for s, c in elev_corr.items():
        print(f"  {s}: {c:+.4f} degC")

    print("\n=== Validation (b): row counts before/after the join, per airport ===")
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

    drops_csv = PROCESSED / "session49_upper_air_join_drops.csv"
    with open(drops_csv, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "span", "reason"])
        w.writerows(all_drop_log)
    print(f"\nWrote join-drop log: {drops_csv} ({len(all_drop_log)} rows)")

    # ---- Validation (c): sanity ranges per new column ----------------------
    print("\n=== Validation (c): sanity ranges per new column, per airport (both spans combined) ===")
    combined_rows = []
    for out_csv in joined_files:
        with open(out_csv) as f:
            combined_rows.extend(csv.DictReader(f))

    cols = ["t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850"]
    for station in AIRPORTS:
        srows = [r for r in combined_rows if r["station"] == station]
        print(f"\n  {station} (n={len(srows)}):")
        means = {}
        for col in cols:
            vals = [float(r[col]) for r in srows if r[col] not in ("", None)]
            n_null = len(srows) - len(vals)
            if vals:
                mean_v = sum(vals) / len(vals)
                means[col] = mean_v
                print(f"    {col:20s}: min={min(vals):8.2f} max={max(vals):8.2f} "
                      f"mean={mean_v:8.2f} n_null={n_null}")
            else:
                means[col] = None
                print(f"    {col:20s}: NO VALUES n_null={n_null}")
        ordered = [means["t2m_raw"], means["t925"], means["t850"], means["t700"]]
        monotonic = all(
            ordered[i] is not None and ordered[i + 1] is not None and ordered[i] > ordered[i + 1]
            for i in range(len(ordered) - 1)
        )
        print(f"    colder-with-height (mean t2m_raw > t925 > t850 > t700): "
              f"{'YES' if monotonic else 'NO -- FLAG'}  "
              f"{[round(v, 2) if v is not None else None for v in ordered]}")

    # ---- Validation (d): spot-check against F97's own confirmed sample ----
    print("\n=== Validation (d): spot-check against F97's own confirmed sample ===")
    print("  F97's own decoded-value sample date was 2025-06-15 -- that date now")
    print("  falls INSIDE the reserved 2024-25 confirmation year (D51, decided one")
    print("  session after F97 ran) and is therefore correctly absent from this")
    print("  session's own output. The spot-check below instead uses F97's OTHER")
    print("  confirmed date, the v16 floor (2021-03-24), which F97 confirmed as")
    print("  PRESENT for TMP:925/850/700 mb at EGLC's own combo but did not decode")
    print("  a value for (F97's own decode call used the recent-date idx only).")
    v16_floor_row = next(
        (r for r in combined_rows if r["station"] == "EGLC" and r["target_date"] == "2021-03-24"), None)
    if v16_floor_row:
        print(f"  This session's own EGLC 2021-03-24 row (the date F97 confirmed present): "
              f"t925={v16_floor_row['t925']} t850={v16_floor_row['t850']} t700={v16_floor_row['t700']}")
        t925, t850, t700 = float(v16_floor_row["t925"]), float(v16_floor_row["t850"]), float(v16_floor_row["t700"])
        plausible = (-60 <= t700 <= 25) and (-50 <= t850 <= 30) and (-45 <= t925 <= 35) and (t925 > t850 > t700)
        print(f"  Physically plausible and colder-with-height: {'YES' if plausible else 'NO -- FLAG'}")
    else:
        print("  EGLC 2021-03-24 row not found in this session's own output -- FLAG")

    print("\n" + "=" * 78)
    print("END. No model was fit. The reserved year (2024-08-01..2025-07-31) was")
    print("never loaded, pulled, or referenced by any date used above.")
    print("=" * 78)


if __name__ == "__main__":
    main()
