"""Session 72: build RNO's observation, feature and persistence tables for
the clean-room rebuild of F109 (DECISIONS D64).

Offline. Written from SPEC.md, DECISIONS.md and DECISIONS-archive.md only,
and imports no other project script (D64.3). No model is fit and nothing is
scored. Missing values stay missing (SPEC 2.2).

Inputs (all raw, D64.6):
- observations: data/raw/iem_asos_RNO_<chunk>_routine.csv, 2021..2025;
- B: the session 37 GRIB cache, data/raw/grib/gfs_<run>_t18z_f026_*.grib2;
- L, D, T, R: this session's cache, data/raw/grib/session72/, checked
  against data/raw/diagnostics/session72/session72_pull_manifest.csv;
- RNO's elevation constant: data/raw/diagnostics/session37/
  session37_elevation_correction_params.csv.

Outputs, in data/rebuild/session72/:
- rno_observations.csv  one row per day: chosen report, time, value, target
- rno_features.csv      one row per day: B, L, D, T, R and intermediates,
                        plus the raw-GFS rung value
- rno_persistence.csv   one row per day: the previous day's observation

The recipe, the documentation gaps and the choices made are written out in
notes/session-72-output.txt (Step 1). Gap numbers (G1..G13) refer to it.
"""

import csv
import datetime as dt
import hashlib
import math
from pathlib import Path

import eccodes

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
B_CACHE = RAW / "grib"
NEW_CACHE = RAW / "grib" / "session72"
NEW_MANIFEST = RAW / "diagnostics" / "session72" / "session72_pull_manifest.csv"
PARAMS = RAW / "diagnostics" / "session37" / "session37_elevation_correction_params.csv"
OUT = ROOT / "data" / "rebuild" / "session72"

OBS_FILES = [
    "iem_asos_RNO_2021-03-24_2021-12-31_routine.csv",
    "iem_asos_RNO_2022-01-01_2022-12-31_routine.csv",
    "iem_asos_RNO_2023-01-01_2023-12-31_routine.csv",
    "iem_asos_RNO_2024-01-01_2024-12-31_routine.csv",
    "iem_asos_RNO_2025-01-01_2025-12-31_routine.csv",
]

STATION = "RNO"
TARGET_HOUR = 20                      # SPEC 3.4
GRID_LAT, GRID_LON = 39.537918, -119.765625   # SPEC 3.4 grid point
CYCLE = 18                            # floor(20/6)*6, SPEC 7.2
LEAD = 26                             # 24 + 20 mod 6, SPEC 7.2
TOL_MIN = 15                          # SPEC 4.5, inclusive (gap G3)

TRAIN = (dt.date(2021, 3, 24), dt.date(2024, 7, 31))   # SPEC 8.3
TEST = (dt.date(2024, 8, 1), dt.date(2025, 7, 31))

# Expected GRIB identity per field (SPEC 8.7 item 3; F111.4 for DSWRF's
# local NCEP code 0/4/192). Level-type codes: 1 surface, 10 entire
# atmosphere, 100 isobaric (hPa), 101 mean sea level, 103 height above ground.
# (file tag, discipline, category, number, level type, level, stepType,
#  startStep, endStep)
B_FIELDS = {
    "tmp2m": ("tmp2m", 0, 0, 0, 103, 2, "instant", LEAD, LEAD),
    "tcdc": ("tcdc", 0, 6, 1, 10, 0, "instant", LEAD, LEAD),
    "u10": ("ugrd10m", 0, 2, 2, 103, 10, "instant", LEAD, LEAD),
    "v10": ("vgrd10m", 0, 2, 3, 103, 10, "instant", LEAD, LEAD),
}
NEW_FIELDS = {
    "t925": ("f026_TMP_925mb", 0, 0, 0, 100, 925, "instant", 26, 26),
    "t850": ("f026_TMP_850mb", 0, 0, 0, 100, 850, "instant", 26, 26),
    "t700": ("f026_TMP_700mb", 0, 0, 0, 100, 700, "instant", 26, 26),
    "rh2m": ("f026_RH_2m", 0, 1, 1, 103, 2, "instant", 26, 26),
    "dpt2m": ("f026_DPT_2m", 0, 0, 6, 103, 2, "instant", 26, 26),
    "spfh2m": ("f026_SPFH_2m", 0, 1, 0, 103, 2, "instant", 26, 26),
    "prmsl": ("f026_PRMSL_msl", 0, 3, 1, 101, 0, "instant", 26, 26),
    "pres_sfc": ("f026_PRES_surface", 0, 3, 0, 1, 0, "instant", 26, 26),
    "dswrf": ("f026_DSWRF_surface", 0, 4, 192, 1, 0, "avg", 24, 26),
    "prmsl_m3": ("f023_PRMSL_msl", 0, 3, 1, 101, 0, "instant", 23, 23),
}


def days(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)


def window_of(d):
    if TRAIN[0] <= d <= TRAIN[1]:
        return "train"
    if TEST[0] <= d <= TEST[1]:
        return "test"
    return "outside"


def r3(x):
    return None if x is None else round(x, 3)


def fmt(x):
    if x is None:
        return ""
    if isinstance(x, float):
        return repr(x)
    return str(x)


# ---------------------------------------------------------------- observations

def load_reports():
    """All routine reports in the five chunk files. Non-finite or 'M'
    temperatures are kept as None and counted (SPEC 8.7 item 2)."""
    reports, stats = {}, {"rows": 0, "no_temp": 0, "duplicates": 0, "minutes": {}}
    for name in OBS_FILES:
        with open(RAW / name) as f:
            for r in csv.DictReader(f):
                if r["station"] != STATION:
                    raise ValueError(f"unexpected station in {name}: {r['station']}")
                stats["rows"] += 1
                t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                try:
                    v = float(r["tmpc"])
                    if not math.isfinite(v):
                        v = None
                except ValueError:
                    v = None
                if v is None:
                    stats["no_temp"] += 1
                if t in reports:
                    stats["duplicates"] += 1
                    continue
                reports[t] = v
                stats["minutes"][t.minute] = stats["minutes"].get(t.minute, 0) + 1
    return reports, stats


def pair_day(d, reports):
    """Nearest routine report with a finite temperature within 15 minutes of
    the target hour (SPEC 4.5, 8.7 item 1). Ties go to the earlier report
    (gap G1). Also reports what 'nearest report of any kind' would give (G2)."""
    target = dt.datetime(d.year, d.month, d.day, TARGET_HOUR)
    cands = []
    for m in range(-TOL_MIN, TOL_MIN + 1):
        t = target + dt.timedelta(minutes=m)
        if t in reports:
            cands.append((abs(m), m, t, reports[t]))
    cands.sort()                       # by distance, then earlier first
    usable = [c for c in cands if c[3] is not None]
    out = {"n_reports_in_window": len(cands), "n_usable_in_window": len(usable),
           "tie": 0, "nearest_any_differs": 0}
    if usable:
        best = usable[0]
        if len(usable) > 1 and usable[1][0] == best[0]:
            out["tie"] = 1
        out.update(report_time=best[2].strftime("%Y-%m-%d %H:%M"), offset_min=best[1],
                   obs_c=best[3], pair_status="paired")
    else:
        out.update(report_time=None, offset_min=None, obs_c=None,
                   pair_status="no usable routine report within 15 min")
    if cands and cands[0][3] is None:
        out["nearest_any_differs"] = 1
    return out


# ------------------------------------------------------------------------ GRIB

def grid_weights():
    """Standard bilinear weights on the regular 0.25 deg grid (gap G6).
    Longitudes in 0..360 form (F89)."""
    lon360 = GRID_LON % 360.0
    x = lon360 / 0.25
    i0 = math.floor(x)
    fx = x - i0
    lat_lo = math.floor(GRID_LAT / 0.25) * 0.25
    fy = (GRID_LAT - lat_lo) / 0.25
    j_lo = round((90.0 - lat_lo) / 0.25)        # row of the southern latitude
    j_hi = j_lo - 1                              # row 0.25 deg further north
    pts = [(j_lo, i0, (1 - fx) * (1 - fy)), (j_lo, i0 + 1, fx * (1 - fy)),
           (j_hi, i0, (1 - fx) * fy), (j_hi, i0 + 1, fx * fy)]
    return pts, {"i0": i0, "fx": fx, "lat_lo": lat_lo, "fy": fy, "j_lo": j_lo}


PTS, WINFO = grid_weights()


def decode_point(path, spec, run_date, valid):
    """Decode one single-message GRIB file, check its identity and full
    validity date and hour (SPEC 8.7 item 3), and interpolate to the grid
    point. Returns (value, None) or (None, reason)."""
    _, disc, cat, num, ltype, level, step_type, s0, s1 = spec
    with open(path, "rb") as f:
        g = eccodes.codes_grib_new_from_file(f)
        if g is None:
            return None, "no message in file"
        extra = eccodes.codes_grib_new_from_file(f)
        if extra is not None:
            eccodes.codes_release(extra)
            eccodes.codes_release(g)
            return None, "more than one message in file"
        try:
            got = (eccodes.codes_get_long(g, "discipline"),
                   eccodes.codes_get_long(g, "parameterCategory"),
                   eccodes.codes_get_long(g, "parameterNumber"),
                   eccodes.codes_get_long(g, "typeOfFirstFixedSurface"),
                   eccodes.codes_get_long(g, "level"),
                   eccodes.codes_get_string(g, "stepType"),
                   eccodes.codes_get_long(g, "startStep"),
                   eccodes.codes_get_long(g, "endStep"))
            if got != (disc, cat, num, ltype, level, step_type, s0, s1):
                return None, f"identity {got} != expected"
            if (eccodes.codes_get_long(g, "dataDate") != int(run_date.strftime("%Y%m%d"))
                    or eccodes.codes_get_long(g, "dataTime") != CYCLE * 100):
                return None, "run date/time mismatch"
            if (eccodes.codes_get_long(g, "validityDate") != int(valid.strftime("%Y%m%d"))
                    or eccodes.codes_get_long(g, "validityTime") != valid.hour * 100):
                return None, "validity date/hour mismatch"
            grid = (eccodes.codes_get_long(g, "Ni"), eccodes.codes_get_long(g, "Nj"),
                    eccodes.codes_get_double(g, "latitudeOfFirstGridPointInDegrees"),
                    eccodes.codes_get_double(g, "longitudeOfFirstGridPointInDegrees"),
                    eccodes.codes_get_double(g, "iDirectionIncrementInDegrees"),
                    eccodes.codes_get_long(g, "iScansNegatively"),
                    eccodes.codes_get_long(g, "jScansPositively"),
                    eccodes.codes_get_long(g, "jPointsAreConsecutive"))
            if grid != (1440, 721, 90.0, 0.0, 0.25, 0, 0, 0):
                return None, f"unexpected grid {grid}"
            vals = eccodes.codes_get_values(g)
            missing = eccodes.codes_get_double(g, "missingValue")
            bitmap = eccodes.codes_get_long(g, "bitmapPresent")
            total = 0.0
            for j, i, w in PTS:
                v = float(vals[j * 1440 + i])
                if not math.isfinite(v) or (bitmap and v == missing):
                    return None, "missing or non-finite grid value"
                total += w * v
            return total, None
        finally:
            eccodes.codes_release(g)


def load_new_manifest():
    with open(NEW_MANIFEST) as f:
        return {r["file"]: r for r in csv.DictReader(f)}


def sha256_file(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def b_file_ok(path):
    """The session 37 sidecars carry no SHA-256; check the saved size and the
    GRIB/7777 markers they record (bytes verified by audit 68a, D62.1)."""
    meta = Path(str(path) + ".meta.txt")
    if not path.exists() or not meta.exists():
        return False, "file or sidecar absent"
    text = meta.read_text()
    size = None
    for line in text.splitlines():
        if line.startswith("bytes saved:"):
            size = int(line.split(":", 1)[1])
    data = path.read_bytes()
    if size != len(data):
        return False, "size differs from sidecar"
    if data[:4] != b"GRIB" or data[-4:] != b"7777":
        return False, "bad magic markers"
    return True, None


# ----------------------------------------------------------------------- build

def season(d):
    n = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
    yf = (d.timetuple().tm_yday - 1) / n
    return math.sin(2 * math.pi * yf), math.cos(2 * math.pi * yf)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with open(PARAMS) as f:
        corr = {r["station"]: r for r in csv.DictReader(f)}[STATION]
    correction_c = float(corr["correction_c"])      # gap G5: CSV value
    print(f"RNO correction_c (params CSV): {correction_c}  "
          f"(D48.3 formula would give {float(corr['gap_m']) / 1000 * float(corr['lapse_c_per_km']):.8f})")
    print(f"grid weights: {WINFO}  points(j,i,w): {PTS}")

    reports, ostats = load_reports()
    print(f"observation files: {len(OBS_FILES)}  rows: {ostats['rows']:,}  "
          f"no temperature: {ostats['no_temp']}  duplicate timestamps: {ostats['duplicates']}")
    print(f"report minutes: {dict(sorted(ostats['minutes'].items()))}")

    manifest = load_new_manifest()
    all_days = list(days(TRAIN[0], TEST[1]))
    obs_rows, feat_rows, pers_rows = [], [], []
    pair_cache = {}
    reasons = {}

    def paired(d):
        if d not in pair_cache:
            pair_cache[d] = pair_day(d, reports)
        return pair_cache[d]

    for d in all_days:
        w = window_of(d)
        run = d - dt.timedelta(days=1)
        valid = dt.datetime(d.year, d.month, d.day, TARGET_HOUR)
        row = {"target_date": d.isoformat(), "window": w, "run_date": run.isoformat(),
               "cycle": CYCLE, "lead": LEAD}
        miss = []

        # B from the session 37 cache
        b = {}
        for key, spec in B_FIELDS.items():
            p = B_CACHE / f"gfs_{run:%Y%m%d}_t{CYCLE:02d}z_f{LEAD:03d}_{spec[0]}.grib2"
            ok, why = b_file_ok(p)
            if not ok:
                b[key] = None
                miss.append(f"B {key}: {why}")
                continue
            v, why = decode_point(p, spec, run, valid)
            b[key] = v
            if why:
                miss.append(f"B {key}: {why}")
        t2m_raw_full = None if b["tmp2m"] is None else b["tmp2m"] - 273.15
        temp_full = None if t2m_raw_full is None else t2m_raw_full + correction_c
        wind_full = (None if b["u10"] is None or b["v10"] is None
                     else math.hypot(b["u10"], b["v10"]) * 3.6)
        s_sin, s_cos = season(d)
        row.update({
            "t2m_grib_uncorrected_c_full": t2m_raw_full,
            "temperature_grib_c_full": temp_full,
            "temperature_grib_c": r3(temp_full),
            "cloud_cover_grib_pct_full": b["tcdc"],
            "cloud_cover_grib_pct": r3(b["tcdc"]),
            "u10_ms_full": b["u10"], "v10_ms_full": b["v10"],
            "wind_speed_grib_kmh_full": wind_full,
            "wind_speed_grib_kmh": r3(wind_full),
            "season_sin": s_sin, "season_cos": s_cos,
        })

        # L, D, T, R from this session's cache
        n = {}
        for key, spec in NEW_FIELDS.items():
            fh = 23 if key == "prmsl_m3" else 26
            vt = valid - dt.timedelta(hours=3) if key == "prmsl_m3" else valid
            name = f"gfs_{run:%Y%m%d}_t{CYCLE:02d}z_{spec[0]}.grib2"
            p = NEW_CACHE / name
            m = manifest.get(name)
            if m is None or not p.exists():
                n[key] = None
                miss.append(f"{key}: not in pull manifest (failed or not pulled)")
                continue
            if sha256_file(p) != m["sha256"]:
                n[key] = None
                miss.append(f"{key}: SHA-256 differs from manifest")
                continue
            v, why = decode_point(p, spec, run, vt)
            n[key] = v
            if why:
                miss.append(f"{key}: {why}")
            assert int(m["fhour"]) == fh

        def k2c(v):
            return None if v is None else r3(v - 273.15)

        def pa2hpa(v):
            return None if v is None else r3(v / 100.0)

        t2m_raw = (None if row["temperature_grib_c"] is None
                   else r3(row["temperature_grib_c"] - correction_c))        # G4
        t2m_raw_from_full = None if temp_full is None else r3(temp_full - correction_c)
        t925, t850, t700 = k2c(n["t925"]), k2c(n["t850"]), k2c(n["t700"])
        dpt = k2c(n["dpt2m"])
        msl, sfc, msl3 = pa2hpa(n["prmsl"]), pa2hpa(n["pres_sfc"]), pa2hpa(n["prmsl_m3"])
        ddep = None if t2m_raw is None or dpt is None else r3(t2m_raw - dpt)          # G7
        row.update({
            "t2m_raw": t2m_raw, "t2m_raw_from_full": t2m_raw_from_full,
            "t925": t925, "t850": t850, "t700": t700,
            "lapse_rate_t2_t850": None if t2m_raw is None or t850 is None else r3(t2m_raw - t850),
            "relative_humidity_2m": r3(n["rh2m"]),
            "dew_point_2m": dpt,
            "specific_humidity_2m": None if n["spfh2m"] is None else round(n["spfh2m"], 6),
            "dewpoint_depression_t2m": ddep,
            "dewpoint_depression_t2m_floored": None if ddep is None else max(ddep, 0.0),
            "pressure_msl_hpa": msl, "pressure_surface_hpa": sfc,
            "pressure_msl_lead_minus3_hpa": msl3,
            "pressure_tendency_3h_hpa": None if msl is None or msl3 is None else r3(msl - msl3),
            "dswrf_ave_to_lead_wm2": r3(n["dswrf"]),
            "dswrf_ave_to_lead_minus2_wm2": None,     # blank by recipe at RNO (F107)
            "dswrf_2h_wm2": r3(n["dswrf"]),
            "raw_gfs_rung_c": row["temperature_grib_c"],
            "missing_inputs": "; ".join(miss),
        })
        for x in miss:
            reasons[x] = reasons.get(x, 0) + 1
        feat_rows.append(row)

        # observation and target
        pr = paired(d)
        obs = {"target_date": d.isoformat(), "window": w,
               "target_time_utc": valid.strftime("%Y-%m-%d %H:%M"),
               "report_time_utc": pr["report_time"], "offset_min": pr["offset_min"],
               "obs_c": pr["obs_c"], "n_reports_in_window": pr["n_reports_in_window"],
               "n_usable_in_window": pr["n_usable_in_window"], "tie": pr["tie"],
               "nearest_any_differs": pr["nearest_any_differs"],
               "pair_status": pr["pair_status"],
               "forecast_c": row["temperature_grib_c"],
               "residual_c": (None if pr["obs_c"] is None or row["temperature_grib_c"] is None
                              else r3(pr["obs_c"] - row["temperature_grib_c"]))}
        obs_rows.append(obs)

        # persistence: previous calendar day's paired observation (SPEC 2.1d)
        prev = d - dt.timedelta(days=1)
        pp = paired(prev)
        pers_rows.append({"target_date": d.isoformat(), "window": w,
                          "prev_date": prev.isoformat(),
                          "prev_report_time_utc": pp["report_time"],
                          "persistence_c": pp["obs_c"],
                          "status": "ok" if pp["obs_c"] is not None else
                          ("previous day outside the observation files"
                           if prev < dt.date(2021, 3, 24) else pp["pair_status"])})

    write(OUT / "rno_observations.csv", obs_rows)
    write(OUT / "rno_features.csv", feat_rows)
    write(OUT / "rno_persistence.csv", pers_rows)
    print(f"wrote {len(obs_rows)} / {len(feat_rows)} / {len(pers_rows)} rows to {OUT.relative_to(ROOT)}")
    print("missing-input reasons (row count):")
    for k in sorted(reasons):
        print(f"  {reasons[k]:5d}  {k}")
    report(obs_rows, feat_rows, pers_rows, ostats, reports)


def write(path, rows):
    cols = list(rows[0].keys())
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([fmt(r[c]) for c in cols])


# --------------------------------------------------------------------- counts

B_COLS = ["temperature_grib_c", "season_sin", "season_cos", "cloud_cover_grib_pct",
          "wind_speed_grib_kmh"]
DLRT_COLS = ["dewpoint_depression_t2m", "lapse_rate_t2_t850", "dswrf_2h_wm2",
             "pressure_tendency_3h_hpa"]


def report(obs_rows, feat_rows, pers_rows, ostats, reports):
    print("\n=== COUNTS PER TABLE AND WINDOW ===")
    for name, rows, skip in [("observations", obs_rows, {"target_date", "window", "target_time_utc"}),
                             ("features", feat_rows, {"target_date", "window", "run_date", "cycle",
                                                      "lead", "missing_inputs",
                                                      "dswrf_ave_to_lead_minus2_wm2"}),
                             ("persistence", pers_rows, {"target_date", "window", "prev_date",
                                                         "status"})]:
        for w in ("train", "test"):
            rs = [r for r in rows if r["window"] == w]
            print(f"\n[{name}] window={w} rows={len(rs)}")
            for c in rs[0]:
                if c in skip:
                    continue
                m = sum(1 for r in rs if r[c] is None)
                print(f"  missing {c:36s} {m}")
            if name == "features":
                print(f"  (dswrf_ave_to_lead_minus2_wm2 blank by recipe: "
                      f"{sum(1 for r in rs if r['dswrf_ave_to_lead_minus2_wm2'] is None)})")

    print("\n=== COMPLETE-CASE ROW COUNTS ===")
    obs_by = {r["target_date"]: r for r in obs_rows}
    pers_by = {r["target_date"]: r for r in pers_rows}
    for w in ("train", "test"):
        fs = [r for r in feat_rows if r["window"] == w]
        b_ok = [r for r in fs if all(r[c] is not None for c in B_COLS)]
        f_ok = [r for r in b_ok if all(r[c] is not None for c in DLRT_COLS)]
        fo_ok = [r for r in f_ok if obs_by[r["target_date"]]["obs_c"] is not None]
        fop_ok = [r for r in fo_ok if pers_by[r["target_date"]]["persistence_c"] is not None]
        print(f"window={w}: days={len(fs)}  B complete={len(b_ok)}  "
              f"B+D,L,R,T complete={len(f_ok)}  dropped vs B-only mask={len(b_ok) - len(f_ok)}  "
              f"+ observation={len(fo_ok)}  + persistence={len(fop_ok)}")
        print(f"    no observation among feature-complete rows: {len(f_ok) - len(fo_ok)}"
              f"  -> dates: {[r['target_date'] for r in f_ok if obs_by[r['target_date']]['obs_c'] is None]}")
        print(f"    no previous-day observation among those: {len(fo_ok) - len(fop_ok)}")
        print(f"    feature-incomplete dates: {[r['target_date'] for r in fs if r not in f_ok]}")

    print("\n=== PAIRING DETAIL ===")
    for w in ("train", "test"):
        rs = [r for r in obs_rows if r["window"] == w]
        offs = {}
        for r in rs:
            offs[r["offset_min"]] = offs.get(r["offset_min"], 0) + 1
        print(f"window={w}: paired={sum(1 for r in rs if r['obs_c'] is not None)}  "
              f"unpaired={sum(1 for r in rs if r['obs_c'] is None)}  offsets={offs}")
        print(f"    unpaired dates: {[r['target_date'] for r in rs if r['obs_c'] is None]}")
        print(f"    days with >1 report in the 15-min window: "
              f"{sum(1 for r in rs if r['n_reports_in_window'] > 1)}  ties: {sum(r['tie'] for r in rs)}"
              f"  days where nearest-any-report reading differs (G2): "
              f"{sum(r['nearest_any_differs'] for r in rs)}")

    # Whole-hour coverage, for comparison with F76's training-window figure.
    start = dt.datetime(2021, 3, 24, 0)
    end = dt.datetime(2025, 7, 31, 23)
    hours = usable = 0
    t = start
    while t <= end:
        hours += 1
        if any(reports.get(t + dt.timedelta(minutes=m)) is not None
               for m in range(-TOL_MIN, TOL_MIN + 1)):
            usable += 1
        t += dt.timedelta(hours=1)
    print(f"\nwhole-hour coverage 2021-03-24 00:00 .. 2025-07-31 23:00: expected={hours:,} "
          f"usable={usable:,} missing={hours - usable}")


if __name__ == "__main__":
    main()
