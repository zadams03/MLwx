"""Session 76b, Check B: the four 0.25 degree grid points around KSFO.

B.1 bilinear weights of the four points at KSFO's Open-Meteo grid point, as
    session 76's bilinear_from_gid computes them, and the nearest point;
B.2 the land value (from session76b_land_pull.py's LAND:surface message) and
    the model terrain (session 76's HGT diagnostic) at each point;
B.3 TMP 2 m at each point, no interpolation and no elevation constant,
    from the SHA-verified cached copies (session76b_cache.py), target dates
    before 2024-08-01 only; per month and per year: each point's mean, the
    bilinear blend, and Open-Meteo minus each point and minus the blend, on
    F116.5's identical-row set.

Offline. A forecast is compared with a forecast. No observation is read, no
model is fit. Every file read is filtered to dates before 2024-08-01 as it
is read. Writes only to data/rebuild/session76b/.
"""

import csv
import datetime as dt
import json
import sys
from pathlib import Path

import eccodes as ec

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session76_build as b76          # noqa: E402  read-only import
import session76_grib_pull as p76      # noqa: E402  read-only import
from session76b_cache import CUTOFF, cached_messages, ROOT   # noqa: E402

OUT = ROOT / "data" / "rebuild" / "session76b"
POINTS_OUT = OUT / "check_b_ksfo_point_temps.csv"
MONTH_OUT = OUT / "check_b_ksfo_monthly.csv"
LAND = ROOT / "data" / "raw" / "diagnostics" / "session76b" / "gfs_20240609_t18z_f026_land_surface_SFO_diagnostic.grib2"
HGT = ROOT / "data" / "raw" / "diagnostics" / "session76" / "gfs_20240609_t18z_f026_hgt_surface_SFO_diagnostic.grib2"
FEATURES = ROOT / "data" / "processed" / "session76_ksfo_features.csv"
S76_VALUES = ROOT / "data" / "raw" / "diagnostics" / "session76" / "session76_decoded_point_values.csv"
PARAMS = ROOT / "data" / "raw" / "diagnostics" / "session76" / "session76_elevation_correction_params.csv"
LAT, LON = p76.GRID_LAT, p76.GRID_LON     # KSFO, SPEC 3.4
NAMES = ["SW", "SE", "NW", "NE"]          # (lat0,lon0) (lat0,lon1) (lat1,lon0) (lat1,lon1)


def four(gid):
    """The four neighbours as session 76's bilinear_from_gid orders them, and
    its weights. Returns {name: (lat, lon, value, weight, distance_km)}."""
    nb = ec.codes_grib_find_nearest(gid, LAT, LON, npoints=4)
    lats = sorted(set(round(n.lat, 6) for n in nb))
    lons = sorted(set(round(n.lon, 6) for n in nb))
    assert len(lats) == 2 and len(lons) == 2
    lon_q = LON + 360.0 if LON < 0 else LON
    dlat = (LAT - lats[0]) / (lats[1] - lats[0])
    dlon = (lon_q - lons[0]) / (lons[1] - lons[0])
    w = {"SW": (1 - dlat) * (1 - dlon), "SE": (1 - dlat) * dlon, "NW": dlat * (1 - dlon), "NE": dlat * dlon}
    pos = {"SW": (lats[0], lons[0]), "SE": (lats[0], lons[1]), "NW": (lats[1], lons[0]), "NE": (lats[1], lons[1])}
    by = {(round(n.lat, 6), round(n.lon, 6)): n for n in nb}
    return {k: (pos[k][0], pos[k][1], by[pos[k]].value, w[k], by[pos[k]].distance) for k in NAMES}


def read_one(path):
    with open(path, "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
    return gid


def mean(xs):
    return sum(xs) / len(xs) if xs else float("nan")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in (POINTS_OUT, MONTH_OUT):
        if p.exists():
            sys.exit(f"STOP: {p.relative_to(ROOT)} exists; not overwriting.")
    with open(PARAMS) as f:
        correction = float(list(csv.DictReader(f))[0]["correction_c"])
    print("=" * 78)
    print("SESSION 76b - Check B: the four 0.25 degree points around KSFO")
    print("=" * 78)
    print(f"KSFO Open-Meteo grid point {LAT}, {LON}; constant {correction}")

    # ---- B.1 / B.2 ----
    gl, gh = read_one(LAND), read_one(HGT)
    land, hgt = four(gl), four(gh)
    for g in (gl, gh):
        ec.codes_release(g)
    print(f"\n--- B.1 weights (session 76's bilinear_from_gid) and B.2 land / terrain ---")
    print(f"{'point':5s} {'lat':>10s} {'lon (0-360)':>12s} {'lon':>11s} {'weight':>9s} {'dist km':>8s} "
          f"{'LAND':>5s} {'HGT m':>8s}")
    for k in NAMES:
        la, lo, lv, w, dist = land[k]
        assert (la, lo) == hgt[k][:2]
        print(f"{k:5s} {la:>10.4f} {lo:>12.4f} {lo - 360:>11.4f} {w:>9.4f} {dist:>8.3f} {lv:>5.0f} {hgt[k][2]:>8.2f}")
    print(f"weights sum: {sum(land[k][3] for k in NAMES):.12f}")
    nearest = min(NAMES, key=lambda k: land[k][4])
    print(f"nearest point: {nearest} ({land[nearest][0]}, {land[nearest][1] - 360:.4f}), "
          f"{land[nearest][4]:.3f} km, weight {land[nearest][3]:.4f}")
    land_w = sum(land[k][3] * land[k][2] for k in NAMES)
    print(f"weight on land points (LAND=1): {land_w:.4f}; on sea points (LAND=0): {1 - land_w:.4f}")
    hb = sum(hgt[k][3] * hgt[k][2] for k in NAMES)
    print(f"terrain blend from these weights: {hb:.4f} m (session 76 F116.2: 94.4704 m)")

    # ---- B.3 ----
    pairs, skipped = cached_messages({"tmp2m"})
    print(f"\n--- B.3 TMP 2 m at each point, before 2024-08-01 ---")
    print(f"cached tmp2m messages used (SHA-256 re-verified at load): {len(pairs)}; skipped: {len(skipped)}")
    for s in skipped:
        print(f"  skipped: {s}")
    s76 = {}
    with open(S76_VALUES) as f:
        for r in csv.DictReader(f):
            if dt.date.fromisoformat(r["target_date"]) >= CUTOFF:
                continue
            if r["field"] == "tmp2m":
                s76[r["target_date"]] = float(r["value"])
    feats = {}
    with open(FEATURES) as f:
        for r in csv.DictReader(f):
            if dt.date.fromisoformat(r["target_date"]) >= CUTOFF:
                continue
            feats[r["target_date"]] = r
    om = {}
    for name in b76.OM_TEMP:
        d = json.load(open(b76.RAW / name))
        for t, v in zip(d["hourly"]["time"], d["hourly"]["temperature_2m_previous_day1"]):
            if t.endswith("T20:00") and dt.date.fromisoformat(t[:10]) < CUTOFF and v is not None:
                om[t[:10]] = v

    rows, blend_ok, blend_bad, temp_ok, temp_bad = [], 0, [], 0, []
    for r, data in pairs:
        run = dt.date.fromisoformat(r["run_date"])
        gid = ec.codes_new_from_message(data)
        try:
            vd = ec.codes_get_long(gid, "validityDate")
            vt = ec.codes_get_long(gid, "validityTime")
            want = dt.datetime(run.year, run.month, run.day, 18) + dt.timedelta(hours=26)
            assert vd == int(f"{want:%Y%m%d}") and vt == 2000, (vd, vt)
            pts = four(gid)
            blend_k = p76.bilinear_from_gid(gid, LAT, LON)
        finally:
            ec.codes_release(gid)
        d = r["target_date"]
        if blend_k == s76[d]:
            blend_ok += 1
        else:
            blend_bad.append((d, blend_k, s76[d]))
        temp = round((blend_k - 273.15) + correction, 3)
        if temp == float(feats[d]["temperature_grib_c"]):
            temp_ok += 1
        else:
            temp_bad.append((d, temp, feats[d]["temperature_grib_c"]))
        row = {"target_date": d}
        for k in NAMES:
            row[k] = pts[k][2] - 273.15
        row["blend_raw"] = blend_k - 273.15
        row["temp"] = float(feats[d]["temperature_grib_c"])
        row["om"] = om.get(d)
        rows.append(row)
    rows.sort(key=lambda x: x["target_date"])
    print(f"blend == session 76 decoded tmp2m value (exact, K): {blend_ok} of {len(rows)}; "
          f"mismatches {len(blend_bad)} {blend_bad[:5]}")
    print(f"round(blend - 273.15 + c, 3) == session 76 temperature_grib_c: {temp_ok} of {len(rows)}; "
          f"mismatches {len(temp_bad)} {temp_bad[:5]}")
    with open(POINTS_OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["target_date"] + [f"{k}_c" for k in NAMES] + ["blend_c_no_constant", "temperature_grib_c",
                                                                   "openmeteo_c"])
        for x in rows:
            w.writerow([x["target_date"]] + [repr(x[k]) for k in NAMES]
                       + [repr(x["blend_raw"]), repr(x["temp"]), "" if x["om"] is None else repr(x["om"])])

    ident = [x for x in rows if x["om"] is not None]
    print(f"identical rows (GRIB and Open-Meteo both present, F116.5's set): {len(ident)}")
    chk = [x["temp"] - x["om"] for x in ident]
    print(f"cross-check vs F116.5 on this set: mean|temp - OM| = {mean([abs(v) for v in chk]):.3f}, "
          f"mean(temp - OM) = {mean(chk):+.3f}")

    def table(groups, label):
        print(f"\nBy {label}. All in degC. n = identical rows. Point means are raw TMP 2 m (no constant).")
        print("'blend' = bilinear blend, no constant; 'temp' = blend + constant (session 76's "
              "temperature_grib_c).")
        print("'spread' = max minus min of the four point means; 'day spread' = mean over days of the "
              "daily max minus min.")
        hdr = (f"{'':8s} {'n':>4s} " + " ".join(f"{k:>6s}" for k in NAMES)
               + f" {'blend':>6s} {'temp':>6s} {'OM':>6s} {'spread':>6s} {'dspr':>6s} "
               + " ".join(f"{'OM-' + k:>6s}" for k in NAMES) + f" {'OM-bl':>6s} {'OM-tmp':>6s}")
        print(hdr)
        out = []
        for key in sorted(groups):
            g = groups[key]
            pm = {k: mean([x[k] for x in g]) for k in NAMES}
            bl, tp, o = mean([x["blend_raw"] for x in g]), mean([x["temp"] for x in g]), mean([x["om"] for x in g])
            spread = max(pm.values()) - min(pm.values())
            dspr = mean([max(x[k] for k in NAMES) - min(x[k] for k in NAMES) for x in g])
            omk = {k: mean([x["om"] - x[k] for x in g]) for k in NAMES}
            ob, ot = mean([x["om"] - x["blend_raw"] for x in g]), mean([x["om"] - x["temp"] for x in g])
            print(f"{key:8s} {len(g):>4d} " + " ".join(f"{pm[k]:>6.2f}" for k in NAMES)
                  + f" {bl:>6.2f} {tp:>6.2f} {o:>6.2f} {spread:>6.2f} {dspr:>6.2f} "
                  + " ".join(f"{omk[k]:>+6.2f}" for k in NAMES) + f" {ob:>+6.2f} {ot:>+6.2f}")
            out.append([label, key, len(g)] + [pm[k] for k in NAMES] + [bl, tp, o, spread, dspr]
                       + [omk[k] for k in NAMES] + [ob, ot])
        return out

    months, years = {}, {}
    for x in ident:
        months.setdefault(x["target_date"][5:7], []).append(x)
        years.setdefault(x["target_date"][:4], []).append(x)
    allrows = table(months, "calendar month") + table(years, "year") + table({"all": ident}, "whole period")
    with open(MONTH_OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "key", "n"] + [f"mean_{k}" for k in NAMES]
                   + ["mean_blend_no_constant", "mean_temp", "mean_openmeteo", "spread_of_point_means",
                      "mean_daily_spread"] + [f"om_minus_{k}" for k in NAMES]
                   + ["om_minus_blend", "om_minus_temp"])
        for r in allrows:
            w.writerow(r[:3] + [repr(v) for v in r[3:]])
    print(f"\noutputs: {POINTS_OUT.relative_to(ROOT)}, {MONTH_OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
