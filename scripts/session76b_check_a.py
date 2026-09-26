"""Session 76b, Check A: is the session 76 pipeline correct?

Re-decodes RNO from the SHA-verified cached copies of session 76's GRIB
messages (session76b_cache.py), using session 76's OWN code, imported
read-only, with only the station parameters changed:
- session76_grib_pull.decode()  (identity, run and validity checks, then
  bilinear_from_gid) with GRID_LAT/GRID_LON set to RNO's grid point;
- session76_build.build_features() with STATION = "RNO", LAST = 2024-07-31
  and RNO's constant read from session37_elevation_correction_params.csv.
Then compares every field both hold with RNO's record rows,
2021-03-24..2024-07-31.

Offline. No model, no observation, no MAE. Rows dated 2024-08-01 or later
are dropped from the record files as each row is read, before anything
else. Writes only to data/rebuild/session76b/.
"""

import csv
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session76_build as b76          # noqa: E402  read-only import
import session76_grib_pull as p76      # noqa: E402  read-only import
from session76b_cache import CUTOFF, cached_messages, ROOT   # noqa: E402

OUT = ROOT / "data" / "rebuild" / "session76b"
VALUES = OUT / "check_a_rno_decoded_values.csv"
RESULT = OUT / "check_a_rno_compare.csv"

# RNO's station parameters, as the record has them (SPEC 3.4; session37 params).
RNO_GRID = (39.537918, -119.765625)
PARAMS = ROOT / "data" / "raw" / "diagnostics" / "session37" / "session37_elevation_correction_params.csv"
FIRST, LAST = dt.date(2021, 3, 24), dt.date(2024, 7, 31)

RECORD = {
    "B": ("grib_features_v16_window.csv",
          ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]),
    "L": ("session49_v16_window_with_upper_air.csv",
          ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh",
           "t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850"]),
    "D": ("session51_v16_window_with_moisture.csv",
          ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh",
           "t2m_raw", "relative_humidity_2m", "dew_point_2m", "specific_humidity_2m",
           "dewpoint_depression_t2m"]),
    "T": ("session53_v16_window_with_pressure.csv",
          ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh",
           "pressure_msl_hpa", "pressure_surface_hpa", "pressure_msl_lead_minus3_hpa",
           "pressure_tendency_3h_hpa"]),
    "R": ("session55_v16_window_with_radiation.csv",
          ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh",
           "dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"]),
}


def load_record(name, cols):
    rows = {}
    with open(ROOT / "data" / "processed" / name) as f:
        for r in csv.DictReader(f):
            if r["station"] != "RNO":
                continue
            d = dt.date.fromisoformat(r["target_date"])
            if d >= CUTOFF:          # dropped before anything else reads it
                continue
            if d < FIRST:
                continue
            rows[d.isoformat()] = {c: r[c] for c in cols}
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in (VALUES, RESULT):
        if p.exists():
            sys.exit(f"STOP: {p.relative_to(ROOT)} exists; not overwriting.")
    with open(PARAMS) as f:
        correction = float([r for r in csv.DictReader(f) if r["station"] == "RNO"][0]["correction_c"])
    print("=" * 78)
    print("SESSION 76b - Check A: RNO re-decoded with session 76's code, vs the record")
    print("=" * 78)
    print(f"RNO grid point {RNO_GRID}; constant {correction} (read from {PARAMS.name})")

    # ---- decode, with session 76's decode(), station parameters changed ----
    p76.GRID_LAT, p76.GRID_LON = RNO_GRID
    assert p76.CYCLE == 18
    pairs, skipped = cached_messages()
    print(f"cached messages used (SHA-256 re-verified at load): {len(pairs)}")
    print(f"skipped: {len(skipped)}")
    for s in skipped:
        print(f"  skipped: {s}")
    rows, fails = [], []
    for r, data in pairs:
        fh, _, _, _, identity = p76.FIELDS[r["field"]]
        try:
            v, units, validity = p76.decode(data, identity, dt.date.fromisoformat(r["run_date"]), fh)
        except Exception as e:  # noqa: BLE001
            fails.append((r["target_date"], r["field"], repr(e)))
            continue
        rows.append(["RNO", r["target_date"], r["field"], repr(v), units, validity])
    print(f"decoded: {len(rows)}; decode failures: {len(fails)}")
    for x in fails:
        print(f"  decode failure: {x}")
    rows.sort(key=lambda x: (x[1], x[2]))
    with open(VALUES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(p76.VAL_COLS)
        w.writerows(rows)

    # ---- build, with session 76's build_features(), station parameters changed ----
    b76.VALUES, b76.STATION, b76.FIRST, b76.LAST = VALUES, "RNO", FIRST, LAST
    built, drops, nonfinite = b76.build_features(correction)
    print(f"built rows: {len(built)} of {(LAST - FIRST).days + 1} days; drop-log rows: {len(drops)}; "
          f"non-finite: {nonfinite}")
    for d in drops:
        print(f"  build drop: {d}")
    built = {r["target_date"]: r for r in built}

    # ---- compare ----
    print("\nper field: rows compared / rows differing at stored precision / max |diff| / "
          "missing days match")
    print(f"{'file':3s} {'field':30s} {'compared':>8s} {'differ':>6s} {'max|diff|':>10s}  missing days")
    out, differing, all_pass = [], [], True
    for key, (name, cols) in RECORD.items():
        rec = load_record(name, cols)
        for c in cols:
            rec_missing = {d for d in (dt.date.fromordinal(i).isoformat()
                                       for i in range(FIRST.toordinal(), LAST.toordinal() + 1))
                           if d not in rec or rec[d][c] == ""}
            new_missing = {d for d in (dt.date.fromordinal(i).isoformat()
                                       for i in range(FIRST.toordinal(), LAST.toordinal() + 1))
                           if d not in built or built[d][c] is None}
            n, nd, mx = 0, 0, 0.0
            for d in sorted(set(rec) & set(built)):
                a, bv = rec[d][c], built[d][c]
                if a == "" or bv is None:
                    continue
                n += 1
                diff = abs(float(a) - bv)
                mx = max(mx, diff)
                if float(a) != bv:
                    nd += 1
                    differing.append((key, c, d, a, repr(bv)))
            same = rec_missing == new_missing
            if nd or not same:
                all_pass = False
            miss_txt = ("match: " + (",".join(sorted(rec_missing)) if len(rec_missing) <= 3
                                     else f"{len(rec_missing)} days") if same
                        else f"DIFFER record={sorted(rec_missing)[:5]} new={sorted(new_missing)[:5]}")
            print(f"{key:3s} {c:30s} {n:>8d} {nd:>6d} {mx:>10.6f}  {miss_txt}")
            out.append([key, name, c, n, nd, repr(mx), same, ";".join(sorted(rec_missing)),
                        ";".join(sorted(new_missing))])
    with open(RESULT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["family", "record_file", "field", "rows_compared", "rows_differing", "max_abs_diff",
                    "missing_days_match", "record_missing_days", "rebuilt_missing_days"])
        w.writerows(out)
    if differing:
        print("\nfirst ten differing rows (family, field, date, record, rebuilt):")
        for x in differing[:10]:
            print(f"  {x}")
    print(f"\nCheck A: {'PASS' if all_pass else 'FAIL'} (pass = zero differing rows in every field "
          f"and matching missing days)")
    print(f"outputs: {VALUES.relative_to(ROOT)}, {RESULT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
