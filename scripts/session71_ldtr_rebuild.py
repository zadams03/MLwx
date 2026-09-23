"""Session 71 Steps 3 and 4: rebuild L, D, T and R for audit 68a's 45
station-days from the GRIB bytes cached in Step 2, and compare each value
with every committed file that holds that station-day.

    .venv/bin/python scripts/session71_ldtr_rebuild.py

Offline: reads data/raw/grib/session71/ (checked against the committed
manifest's SHA-256 first), the committed family files, the committed B files
and the elevation-correction constants. No network. Writes nothing.

This is new code, written from the Step 1 recipe. It imports nothing from the
build scripts. Differences in method, on purpose:
  - the four surrounding grid points are found by grid arithmetic from the
    message's own grid definition, not by eccodes codes_grib_find_nearest;
  - each message's parameter (discipline/category/number), level type and
    value, step range and full validity date and hour are checked;
  - each grid value used must be finite and not the missing-value marker.
The bilinear weighting itself is the standard formula, written in the same
term order as the recipe so that floating-point order cannot create a
last-digit difference on its own.

Pass rule (session 71 Step 4): round the rebuilt value to the number of
decimals stored in that column of that file (the most found in any row) and
compare it with the stored value. No tolerance. No model is fit and nothing
is scored.
"""

import csv
import hashlib
import math
import sys
from datetime import datetime, timedelta
from pathlib import Path

import eccodes as ec
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session71_sample as smp  # noqa: E402

ROOT = smp.ROOT
CACHE = ROOT / "data" / "raw" / "grib" / "session71"
MANIFEST = ROOT / "data" / "raw" / "diagnostics" / "session71" / "session71_pull_manifest.csv"
ELEV = ROOT / "data" / "raw" / "diagnostics" / "session37" / "session37_elevation_correction_params.csv"

# GRIB2 (discipline, parameterCategory, parameterNumber) and level, per idx name.
# DSWRF in these NCEP files uses NCEP's local-table number 192 ("Surface
# downward short-wave radiation flux"), not the WMO number 7. The first run
# of this script assumed 7 and rejected every DSWRF message; see
# notes/session-71-output.txt.
PARAM = {"TMP": (0, 0, 0), "DPT": (0, 0, 6), "RH": (0, 1, 1), "SPFH": (0, 1, 0),
         "PRMSL": (0, 3, 1), "PRES": (0, 3, 0), "DSWRF": (0, 4, 192)}
LEVEL = {"925 mb": ("isobaricInhPa", 925), "850 mb": ("isobaricInhPa", 850),
         "700 mb": ("isobaricInhPa", 700), "2 m above ground": ("heightAboveGround", 2),
         "mean sea level": ("meanSea", 0), "surface": ("surface", 0)}

FEATURE = {"L": "lapse_rate_t2_t850", "D": "dewpoint_depression_t2m",
           "T": "pressure_tendency_3h_hpa", "R": "dswrf_2h_wm2"}
INTERMEDIATE = {
    "L": ["t2m_raw", "t925", "t850", "t700"],
    "D": ["t2m_raw", "relative_humidity_2m", "dew_point_2m", "specific_humidity_2m"],
    "T": ["pressure_msl_hpa", "pressure_surface_hpa", "pressure_msl_lead_minus3_hpa"],
    "R": ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2"],
}
BOOKKEEPING = ["target_hour", "run_date", "cycle", "lead"]


class MessageError(Exception):
    pass


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(path, m):
    """Open one cached message, check what it is, and return
    (info, values 2-D array [row j, column i], grid dict)."""
    with open(path, "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
        if gid is None:
            raise MessageError("eccodes could not read a message")
        try:
            if ec.codes_grib_new_from_file(f) is not None:
                raise MessageError("more than one message in the file")
            g = lambda k: ec.codes_get(gid, k)  # noqa: E731
            info = {k: g(k) for k in (
                "discipline", "parameterCategory", "parameterNumber", "shortName", "units",
                "typeOfLevel", "level", "stepType", "startStep", "endStep",
                "dataDate", "dataTime", "validityDate", "validityTime")}
            grid = {k: g(k) for k in (
                "gridType", "Ni", "Nj", "latitudeOfFirstGridPointInDegrees",
                "longitudeOfFirstGridPointInDegrees", "iDirectionIncrementInDegrees",
                "jDirectionIncrementInDegrees", "iScansNegatively", "jScansPositively",
                "jPointsAreConsecutive", "missingValue")}
            values = np.asarray(ec.codes_get_values(gid), dtype=float)
        finally:
            ec.codes_release(gid)

    # what the message must be
    if (info["discipline"], info["parameterCategory"], info["parameterNumber"]) != PARAM[m["var"]]:
        raise MessageError(f"parameter {info['discipline']}/{info['parameterCategory']}/"
                           f"{info['parameterNumber']} is not {m['var']}")
    tol, lvl = LEVEL[m["level"]]
    if info["typeOfLevel"] != tol or (lvl and info["level"] != lvl):
        raise MessageError(f"level {info['typeOfLevel']} {info['level']} is not {m['level']}")
    if m["var"] == "DSWRF":
        want = (smp.radiation_reset(m["fhour"]), m["fhour"])
        if info["stepType"] != "avg" or (info["startStep"], info["endStep"]) != want:
            raise MessageError(f"step {info['stepType']} {info['startStep']}-{info['endStep']}, want avg {want}")
    elif info["stepType"] != "instant" or info["startStep"] != m["fhour"] or info["endStep"] != m["fhour"]:
        raise MessageError(f"step {info['stepType']} {info['startStep']}-{info['endStep']}, want instant {m['fhour']}")
    run = datetime.combine(m["run_date"], datetime.min.time()) + timedelta(hours=m["cycle"])
    got_run = datetime.strptime(f"{info['dataDate']}{info['dataTime']:04d}", "%Y%m%d%H%M")
    got_valid = datetime.strptime(f"{info['validityDate']}{info['validityTime']:04d}", "%Y%m%d%H%M")
    if got_run != run:
        raise MessageError(f"run {got_run} is not {run}")
    if got_valid != run + timedelta(hours=m["fhour"]):
        raise MessageError(f"valid {got_valid} is not {run + timedelta(hours=m['fhour'])}")

    # the grid layout this code knows how to index
    if (grid["gridType"] != "regular_ll" or grid["iScansNegatively"] != 0
            or grid["jScansPositively"] != 0 or grid["jPointsAreConsecutive"] != 0):
        raise MessageError(f"unexpected grid layout {grid}")
    if values.size != grid["Ni"] * grid["Nj"]:
        raise MessageError("value count does not match the grid size")
    info["valid"] = got_valid
    return info, values.reshape(grid["Nj"], grid["Ni"]), grid


def interpolate(values, grid, lat, lon):
    """Bilinear value at (lat, lon) from the four surrounding grid points.
    Rows run north to south from the first latitude; columns run east from
    the first longitude, wrapping at 360."""
    lat_first = grid["latitudeOfFirstGridPointInDegrees"]
    lon_first = grid["longitudeOfFirstGridPointInDegrees"]
    di = grid["iDirectionIncrementInDegrees"]
    dj = grid["jDirectionIncrementInDegrees"]
    ni = grid["Ni"]

    j_north = math.floor((lat_first - lat) / dj)
    lat1 = lat_first - j_north * dj          # the row at or north of lat
    lat0 = lat1 - dj                         # the row south of lat
    j_south = j_north + 1
    if not (lat0 <= lat <= lat1):
        raise MessageError("latitude bracketing failed")

    lon_q = lon % 360.0
    i_west = math.floor((lon_q - lon_first) / di)
    lon0 = lon_first + i_west * di
    lon1 = lon0 + di
    i_east = (i_west + 1) % ni
    if not (lon0 <= lon_q <= lon1):
        raise MessageError("longitude bracketing failed")

    v00 = values[j_south, i_west]   # (lat0, lon0)
    v01 = values[j_south, i_east]   # (lat0, lon1)
    v10 = values[j_north, i_west]   # (lat1, lon0)
    v11 = values[j_north, i_east]   # (lat1, lon1)
    for v in (v00, v01, v10, v11):
        if not math.isfinite(v) or v == grid["missingValue"]:
            raise MessageError(f"grid value {v} is missing or not finite")

    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    out = ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
           + dlat * (1 - dlon) * v10 + dlat * dlon * v11)
    return float(out), (lat0, lat1, lon0, lon1)


def load_rows(name):
    with open(smp.PROCESSED / name) as f:
        rows = list(csv.DictReader(f))
    precision = {}
    for col in rows[0]:
        p = 0
        for r in rows:
            s = r[col]
            if "." in s and s.replace(".", "", 1).lstrip("-").isdigit():
                p = max(p, len(s.split(".")[1]))
        precision[col] = p
    return {(r["station"], r["target_date"]): r for r in rows}, precision


def rebuild_station_day(station, d, base_row, corr, cache_meta):
    """Returns ({column: value or None}, {message key: raw interpolated value},
    [missing reasons]). Values follow the recipe's own rounding."""
    _, lat, lon = smp.AIRPORTS[station]
    raw, info_by_key, missing = {}, {}, []
    for m in smp.messages_for(station, d):
        path = CACHE / smp.cache_name(m)
        try:
            if not path.exists():
                raise MessageError("not in the cache (failed pull)")
            if sha256(path) != cache_meta[path.name]:
                raise MessageError("SHA-256 differs from the manifest")
            info, values, grid = decode(path, m)
            raw[m["key"]], _ = interpolate(values, grid, lat, lon)
            info_by_key[m["key"]] = info
        except MessageError as e:
            missing.append(f"{m['key']}: {e}")

    target_hour = smp.AIRPORTS[station][0]
    cycle, lead = smp.cycle_and_lead(target_hour)
    out = {"target_hour": str(target_hour), "run_date": (d - timedelta(days=1)).isoformat(),
           "cycle": str(cycle), "lead": str(lead)}
    have = lambda *ks: all(k in raw for k in ks)  # noqa: E731

    t2m_raw = round(float(base_row["temperature_grib_c"]) - corr[station], 3)
    out["t2m_raw"] = t2m_raw

    # L
    for k in ("t925", "t850", "t700"):
        out[k] = round(raw[k] - 273.15, 3) if have(k) else None
    out["lapse_rate_t2_t850"] = round(t2m_raw - (raw["t850"] - 273.15), 3) if have("t850") else None
    # D
    out["relative_humidity_2m"] = round(raw["rh2m"], 3) if have("rh2m") else None
    out["dew_point_2m"] = round(raw["dpt2m"] - 273.15, 3) if have("dpt2m") else None
    out["specific_humidity_2m"] = round(raw["spfh2m"], 6) if have("spfh2m") else None
    out["dewpoint_depression_t2m"] = (round(t2m_raw - (raw["dpt2m"] - 273.15), 3)
                                      if have("dpt2m") else None)
    # T
    msl = round(raw["prmsl"] / 100.0, 3) if have("prmsl") else None
    msl_m3 = round(raw["prmsl_m3"] / 100.0, 3) if have("prmsl_m3") else None
    out["pressure_msl_hpa"] = msl
    out["pressure_surface_hpa"] = round(raw["pres_sfc"] / 100.0, 3) if have("pres_sfc") else None
    out["pressure_msl_lead_minus3_hpa"] = msl_m3
    out["pressure_tendency_3h_hpa"] = (round(msl - msl_m3, 3)
                                       if msl is not None and msl_m3 is not None else None)
    # R
    out["dswrf_ave_to_lead_wm2"] = round(raw["dswrf"], 3) if have("dswrf") else None
    if smp.needs_deaccumulation(lead):
        if have("dswrf", "dswrf_m2"):
            a, b = info_by_key["dswrf"], info_by_key["dswrf_m2"]
            if a["startStep"] != b["startStep"]:
                missing.append("dswrf: the two averages do not share a start")
                out["dswrf_2h_wm2"] = out["dswrf_ave_to_lead_minus2_wm2"] = None
            else:
                dur_full = a["endStep"] - a["startStep"]
                dur_part = b["endStep"] - b["startStep"]
                window = a["endStep"] - b["endStep"]
                energy = raw["dswrf"] * dur_full - raw["dswrf_m2"] * dur_part
                out["dswrf_2h_wm2"] = round(energy / window, 3)
                out["dswrf_ave_to_lead_minus2_wm2"] = round(raw["dswrf_m2"], 3)
        else:
            out["dswrf_2h_wm2"] = None
            out["dswrf_ave_to_lead_minus2_wm2"] = round(raw["dswrf_m2"], 3) if have("dswrf_m2") else None
    else:
        out["dswrf_2h_wm2"] = out["dswrf_ave_to_lead_wm2"]
        out["dswrf_ave_to_lead_minus2_wm2"] = ""  # blank by the recipe: native window is 2 h
    return out, raw, missing


def compare(rebuilt, stored, p):
    """(status, rebuilt shown at precision p, difference)."""
    if rebuilt == "":
        return ("match" if stored == "" else "MISMATCH"), "(blank)", ""
    if rebuilt is None:
        return "MISSING", "(missing)", ""
    if stored == "":
        return "MISMATCH", f"{round(rebuilt, p):.{p}f}", "stored blank"
    r = round(rebuilt, p)
    s = float(stored)
    return ("match" if r == s else "MISMATCH"), f"{r:.{p}f}", f"{r - s:+.{p}f}"


def main():
    print("=" * 78)
    print("SESSION 71 STEPS 3-4 -- independent rebuild and compare (offline)")
    print("=" * 78)
    sample = smp.recover_sample()

    with open(MANIFEST) as f:
        cache_meta = {r["file"]: r["sha256"] for r in csv.DictReader(f)}
    print(f"\nManifest rows: {len(cache_meta)}. Every message is checked against its "
          f"SHA-256 before it is decoded.")

    with open(ELEV) as f:
        corr = {r["station"]: float(r["correction_c"]) for r in csv.DictReader(f)}
    print("correction_c (session37_elevation_correction_params.csv), used only to "
          "recover t2m_raw from B:")
    print("  " + "  ".join(f"{s} {c:+.4f}" for s, c in corr.items()))

    base = {w: load_rows(n)[0] for w, n in smp.BASE_FILES.items()}
    fam_rows = {fam: {w: load_rows(n) for w, n in files.items()}
                for fam, files in smp.FAMILY_FILES.items()}

    print("\nStored precision (decimals) per column, per committed file:")
    for fam, files in smp.FAMILY_FILES.items():
        for w, name in files.items():
            prec = fam_rows[fam][w][1]
            cols = INTERMEDIATE[fam] + [FEATURE[fam]]
            print(f"  {name:48s} " + ", ".join(f"{c}={prec[c]}" for c in cols))

    results = []   # (family, kind, column, window, station, date, file, stored, shown, status, diff)
    all_missing = []
    decoded_messages = set()
    for window, station, d in sample:
        ds = d.isoformat()
        base_row = base[window].get((station, ds))
        if base_row is None:
            all_missing.append(f"{station} {ds}: no B row in {smp.BASE_FILES[window]}")
            continue
        out, raw, missing = rebuild_station_day(station, d, base_row, corr, cache_meta)
        decoded_messages.update((smp.cache_name(m) for m in smp.messages_for(station, d)
                                 if m["key"] in raw))
        all_missing.extend(f"{station} {ds} {x}" for x in missing)
        for fam in FAMILY_FILES_ORDER:
            name = smp.FAMILY_FILES[fam][window]
            rows, prec = fam_rows[fam][window]
            row = rows.get((station, ds))
            if row is None:
                results.append((fam, "feature", FEATURE[fam], window, station, ds, name,
                                "(no row)", "", "MISSING", ""))
                continue
            for col in BOOKKEEPING:
                st = "match" if row[col] == out[col] else "MISMATCH"
                results.append((fam, "bookkeeping", col, window, station, ds, name,
                                row[col], out[col], st, ""))
            for kind, cols in (("intermediate", INTERMEDIATE[fam]), ("feature", [FEATURE[fam]])):
                for col in cols:
                    st, shown, diff = compare(out[col], row[col], prec[col])
                    results.append((fam, kind, col, window, station, ds, name,
                                    row[col], shown, st, diff))

    print(f"\nMessages decoded and used: {len(decoded_messages)} of {len(cache_meta)} in the manifest.")
    print(f"Missing values (SPEC 2.2, counted, never filled): {len(all_missing)}")
    for x in all_missing:
        print(f"  {x}")

    print("\nPer value (features first, then intermediates), stored vs rebuilt:")
    for fam in FAMILY_FILES_ORDER:
        for kind in ("feature", "intermediate"):
            cols = [FEATURE[fam]] if kind == "feature" else INTERMEDIATE[fam]
            for col in cols:
                print(f"\n== {fam} {kind}: {col} ==")
                for r in results:
                    if r[0] == fam and r[1] == kind and r[2] == col:
                        print(f"  {r[3]:8s} {r[4]:4s} {r[5]}  stored {r[7]:>12s}  rebuilt {r[8]:>12s}  {r[9]}")

    def tally(rows):
        return sum(1 for r in rows if r[9] == "match"), len(rows)

    print("\n" + "=" * 78)
    print("STEP 4 VERDICT -- exact match at the recorded precision, no tolerance")
    print("=" * 78)
    feats = [r for r in results if r[1] == "feature"]
    for fam in FAMILY_FILES_ORDER:
        ok, n = tally([r for r in feats if r[0] == fam])
        by_ap = "  ".join(f"{s} {tally([r for r in feats if r[0] == fam and r[4] == s])[0]}/"
                          f"{tally([r for r in feats if r[0] == fam and r[4] == s])[1]}"
                          for s in smp.AIRPORTS)
        print(f"  {fam} ({FEATURE[fam]}): {ok} of {n}    by airport: {by_ap}")
    ok, n = tally(feats)
    print(f"  TOTAL over the four features: {ok} of {n}")
    by_w = "  ".join(f"{w} {tally([r for r in feats if r[3] == w])[0]}/{tally([r for r in feats if r[3] == w])[1]}"
                     for w, _, _ in smp.WINDOWS)
    print(f"  by window: {by_w}")

    print("\nIntermediate columns (reported separately, not part of the 180):")
    inter = [r for r in results if r[1] == "intermediate"]
    for fam in FAMILY_FILES_ORDER:
        for col in INTERMEDIATE[fam]:
            ok, n = tally([r for r in inter if r[0] == fam and r[2] == col])
            print(f"  {fam} {col:30s} {ok} of {n}")
    ok, n = tally(inter)
    print(f"  all intermediate values: {ok} of {n}")

    book = [r for r in results if r[1] == "bookkeeping"]
    ok, n = tally(book)
    print(f"\nBookkeeping columns (target_hour, run_date, cycle, lead): {ok} of {n}")

    bad = [r for r in results if r[9] != "match"]
    print(f"\nMismatches and missing values: {len(bad)}")
    for r in bad:
        print(f"  {r[9]} {r[4]} {r[5]} {r[6]} {r[2]}: stored {r[7]} rebuilt {r[8]} difference {r[10]}")
    print("\nNo model was fit and nothing was scored. Nothing was written.")


FAMILY_FILES_ORDER = ["L", "D", "T", "R"]

if __name__ == "__main__":
    main()
