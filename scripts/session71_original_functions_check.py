"""Session 71 Step 5 (diagnostic only; Step 4 is the verdict): run the
original build scripts' own functions on the Step 2 cached bytes.

    .venv/bin/python scripts/session71_original_functions_check.py

Only functions that make no network call and write or delete no file are
used:
  - find_message_range (s49, s51, s53) and all_dswrf_lines (s55), on the
    cached .idx text: does the original lookup give the byte range Step 2 used?
  - bilinear_from_gid (s49, s51, s53, s55), on an eccodes handle opened from
    the cached message: does the original interpolation give the same value
    as the Step 3 rebuild, and the committed value?
Not usable, and not called: process_combo (fetches over the network),
decode_message in s53/s55 (writes and deletes a scratch file), build_joined
(writes a processed CSV). So the derivation arithmetic (L, D, T, R from the
fields) cannot be run from the originals; the committed comparison below
applies the recipe's own rounding to each single-field column.

Importing the four modules runs only DIAG.mkdir(exist_ok=True) on folders
that already exist, and builds a requests.Session without using it.
Writes nothing.
"""

import csv
import sys
from pathlib import Path

import eccodes as ec

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session71_sample as smp  # noqa: E402
import session71_ldtr_rebuild as rb  # noqa: E402

for sub in ("session49", "session51", "session53", "session55"):
    if not (smp.ROOT / "data" / "raw" / "diagnostics" / sub).is_dir():
        sys.exit(f"STOP: diagnostics/{sub} is missing; importing would create it.")

import session49_upper_air_pull as s49  # noqa: E402
import session51_moisture_pull as s51  # noqa: E402
import session53_pressure_pull as s53  # noqa: E402
import session55_radiation_pull as s55  # noqa: E402

MODULE = {"L": s49, "D": s51, "T": s53, "R": s55}

# single-message column -> (message key, recipe transform, committed column)
DIRECT = [
    ("L", "t925", lambda v: round(v - 273.15, 3), "t925"),
    ("L", "t850", lambda v: round(v - 273.15, 3), "t850"),
    ("L", "t700", lambda v: round(v - 273.15, 3), "t700"),
    ("D", "rh2m", lambda v: round(v, 3), "relative_humidity_2m"),
    ("D", "dpt2m", lambda v: round(v - 273.15, 3), "dew_point_2m"),
    ("D", "spfh2m", lambda v: round(v, 6), "specific_humidity_2m"),
    ("T", "prmsl", lambda v: round(v / 100.0, 3), "pressure_msl_hpa"),
    ("T", "pres_sfc", lambda v: round(v / 100.0, 3), "pressure_surface_hpa"),
    ("T", "prmsl_m3", lambda v: round(v / 100.0, 3), "pressure_msl_lead_minus3_hpa"),
    ("R", "dswrf", lambda v: round(v, 3), "dswrf_ave_to_lead_wm2"),
    ("R", "dswrf_m2", lambda v: round(v, 3), "dswrf_ave_to_lead_minus2_wm2"),
]


def main():
    print("=" * 78)
    print("SESSION 71 STEP 5 -- original functions on the same bytes (diagnostic)")
    print("=" * 78)
    sample = smp.recover_sample()
    with open(rb.MANIFEST) as f:
        manifest = {r["file"]: r for r in csv.DictReader(f)}

    # (a) byte ranges
    plan = smp.build_plan(sample)
    same_range, n_range = 0, 0
    for m, _ in plan.values():
        idx = (rb.CACHE / smp.idx_cache_name(m["run_date"], m["cycle"], m["fhour"])).read_text()
        if m["var"] == "DSWRF":
            lines = s55.all_dswrf_lines(idx)
            start, end = (lines[0]["start"], lines[0]["end"]) if len(lines) == 1 else (None, None)
        else:
            start, end = MODULE[m["family"]].find_message_range(idx, m["var"], m["level"], m["fhour"])
        n_range += 1
        if f"{start}-{end}" == manifest[smp.cache_name(m)]["byte_range"]:
            same_range += 1
        else:
            print(f"  RANGE DIFFERS {smp.cache_name(m)}: original {start}-{end}, "
                  f"pulled {manifest[smp.cache_name(m)]['byte_range']}")
    print(f"\n(a) original idx lookup gives the pulled byte range: {same_range} of {n_range} messages")

    # (b) interpolated values
    fam_rows = {fam: {w: rb.load_rows(n) for w, n in files.items()}
                for fam, files in smp.FAMILY_FILES.items()}
    same_raw = n_raw = same_committed = n_committed = 0
    for window, station, d in sample:
        _, lat, lon = smp.AIRPORTS[station]
        for m in smp.messages_for(station, d):
            path = rb.CACHE / smp.cache_name(m)
            _, values, grid = rb.decode(path, m)
            mine, _ = rb.interpolate(values, grid, lat, lon)
            with open(path, "rb") as f:
                gid = ec.codes_grib_new_from_file(f)
                orig = MODULE[m["family"]].bilinear_from_gid(gid, lat, lon)
                ec.codes_release(gid)
            n_raw += 1
            if orig == mine:
                same_raw += 1
            else:
                print(f"  VALUE DIFFERS {station} {d} {m['key']}: original {orig!r} rebuild {mine!r} "
                      f"difference {orig - mine:+.3e}")
            for fam, key, transform, col in DIRECT:
                if key != m["key"]:
                    continue
                rows, prec = fam_rows[fam][window]
                stored = rows[(station, d.isoformat())][col]
                n_committed += 1
                if round(transform(orig), prec[col]) == float(stored):
                    same_committed += 1
                else:
                    print(f"  COMMITTED DIFFERS {station} {d} {col}: stored {stored}, "
                          f"original function {transform(orig)}")
    print(f"(b) original bilinear_from_gid equals the Step 3 rebuild, bit for bit: "
          f"{same_raw} of {n_raw} station-day messages")
    print(f"(c) original bilinear_from_gid, rounded as the recipe rounds, equals the "
          f"committed single-field column: {same_committed} of {n_committed}")
    print("\nDerived features (L, D, T, R) were not run through the originals: their")
    print("arithmetic lives only inside build_joined, which writes a processed CSV.")
    print("Nothing was written.")


if __name__ == "__main__":
    main()
