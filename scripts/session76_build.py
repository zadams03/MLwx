"""Session 76, Step 5: build KSFO's feature table and paired observations,
then run the counts, the reproduction gate and the feature sanity checks.

Offline. No model is fit. No MAE, and no forecast-minus-observation
statistic, is computed for any period. The reproduction gate compares GRIB
with Open-Meteo (two forecasts), before 2024-08-01 only, as F89/F90 did.
Rows from KSFO's held-out range (2024-08-01..2026-07-31, D67.6) are built
and written, but only their counts are printed.

Inputs:
- data/raw/diagnostics/session76/session76_decoded_point_values.csv
  (scripts/session76_grib_pull.py): one GRIB value per (day, field) at
  KSFO's grid point, full precision, GRIB units;
- data/raw/diagnostics/session76/session76_elevation_correction_params.csv
  (Step 2.5): KSFO's constant, read back from its 4-dp stored value
  (SPEC 8.8 G5);
- data/raw/iem_asos_SFO_<chunk>_routine.csv (Step 4.2);
- data/raw/openmeteo_previousruns_gfs_global_SFO_<chunk>.json (Step 4.3) and
  data/raw/features/..._SFO_2024-01-19_2024-07-31_cloudwind.json.

The recipe, with its rounding order (SPEC 8.1, 8.2, 8.8 G4, G5, G7):
- temperature_grib_c = round((K - 273.15) + correction_c, 3); the same
  value is the model column `temp` and the raw-GFS (GRIB) rung (SPEC 5.2);
- cloud_cover_grib_pct = round(TCDC, 3);
  wind_speed_grib_kmh = round(sqrt(u^2 + v^2) * 3.6, 3);
- season_sin/cos = sin/cos(2 pi (day_of_year - 1) / days_in_year);
- t2m_raw = round(temperature_grib_c - correction_c, 3);
- t925/t850/t700 = round(K - 273.15, 3); lapse_rate_t2_t850 =
  round(t2m_raw - t850_unrounded, 3);
- relative_humidity_2m, dew_point_2m (K -> degC) round 3,
  specific_humidity_2m round 6; dewpoint_depression_t2m =
  round(t2m_raw - dew_point_unrounded, 3); the model column
  dewpoint_depression_t2m_floored = max(that, 0);
- pressure_msl_hpa, pressure_surface_hpa, pressure_msl_lead_minus3_hpa =
  round(Pa / 100, 3); pressure_tendency_3h_hpa = round(msl - msl_m3, 3)
  of the rounded values;
- dswrf_ave_to_lead_wm2 = round(DSWRF 24-26 h, 3); at lead 26 no
  de-accumulation: dswrf_2h_wm2 = the same rounded value, and
  dswrf_ave_to_lead_minus2_wm2 is blank (not applicable, as at RNO).

Pairing (SPEC 4.5, 8.7 item 1, 8.8 G2, G3): the NEAREST routine report with a
usable, finite tmpc within 15 minutes of 20:00 UTC, inclusive. A tie in
distance is flagged and reported; the earlier report is kept (the session 72
clean-room precedent), and whether the tied temperatures differ is reported.

SPEC 8.7: non-finite values are rejected at load and counted (item 2); counts
are compared with the full expected count (item 4); outputs are new files
only, and the script refuses to overwrite (item 5).
"""

import csv
import datetime as dt
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DIAG = RAW / "diagnostics" / "session76"
PROCESSED = ROOT / "data" / "processed"
VALUES = DIAG / "session76_decoded_point_values.csv"
PARAMS = DIAG / "session76_elevation_correction_params.csv"
OUT_FEATURES = PROCESSED / "session76_ksfo_features.csv"
OUT_OBS = PROCESSED / "session76_ksfo_observations.csv"
OUT_DROPS = PROCESSED / "session76_ksfo_feature_drops.csv"

STATION = "SFO"
TARGET_HOUR, CYCLE, LEAD = 20, 18, 26
FIRST, LAST = dt.date(2021, 3, 24), dt.date(2026, 7, 31)
HELD_OUT_START = dt.date(2024, 8, 1)
TOL_MIN = 15
OBS_CHUNKS = [("2021-03-24", "2021-12-31"), ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"),
              ("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]
OM_TEMP = ["openmeteo_previousruns_gfs_global_SFO_2021-03-24_2021-12-31.json",
           "openmeteo_previousruns_gfs_global_SFO_2022-01-01_2022-12-31.json",
           "openmeteo_previousruns_gfs_global_SFO_2023-01-01_2023-12-31.json",
           "openmeteo_previousruns_gfs_global_SFO_2024-01-01_2024-07-31.json"]
OM_CLOUDWIND = RAW / "features" / "openmeteo_previousruns_gfs_global_SFO_2024-01-19_2024-07-31_cloudwind.json"

FIELDS = ["tmp2m", "tcdc", "ugrd10m", "vgrd10m", "t925", "t850", "t700", "rh2m", "dpt2m",
          "spfh2m", "prmsl", "pres_sfc", "dswrf", "prmsl_m3"]
MODEL_COLS = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
              "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
              "pressure_tendency_3h_hpa"]   # SPEC 8.8 G15, record order
UNDERLYING = ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh",
              "t2m_raw", "t925", "t850", "t700",
              "relative_humidity_2m", "dew_point_2m", "specific_humidity_2m", "dewpoint_depression_t2m",
              "pressure_msl_hpa", "pressure_surface_hpa", "pressure_msl_lead_minus3_hpa",
              "dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2"]
FEATURE_COLS = (["station", "target_date", "target_hour", "run_date", "cycle", "lead"]
                + MODEL_COLS + UNDERLYING + ["complete_case"])
SANITY_COLS = MODEL_COLS + [c for c in UNDERLYING if c != "dswrf_ave_to_lead_minus2_wm2"]

# Rehearsal folds, D51 EXPERIMENT_FOLDS (D67.4); counts only here.
FOLDS = {"2022-23": ((dt.date(2021, 3, 24), dt.date(2022, 7, 31)), (dt.date(2022, 8, 1), dt.date(2023, 7, 31))),
         "2023-24": ((dt.date(2021, 3, 24), dt.date(2023, 7, 31)), (dt.date(2023, 8, 1), dt.date(2024, 7, 31)))}
WINDOWS = {"before 2024-08-01": (FIRST, dt.date(2024, 7, 31)),
           "held-out 2024-25": (dt.date(2024, 8, 1), dt.date(2025, 7, 31)),
           "held-out 2025-26": (dt.date(2025, 8, 1), dt.date(2026, 7, 31))}


def days(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)


def year_fraction(d):
    """Copied from session62_reserved_confirm.py l.217-219."""
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0 or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def finite_float(s):
    """SPEC 8.7 item 2: None for a missing or non-finite value."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def fmt(v):
    return "" if v is None else repr(v)


def build_features(correction):
    raw = {}
    nonfinite = {f: 0 for f in FIELDS}
    with open(VALUES) as f:
        for r in csv.DictReader(f):
            if r["station"] != STATION:
                sys.exit(f"STOP: unexpected station {r['station']}")
            d = dt.date.fromisoformat(r["target_date"])
            if not (FIRST <= d <= LAST):
                sys.exit(f"STOP: value dated {d} outside the window")
            v = finite_float(r["value"])
            if v is None:
                nonfinite[r["field"]] += 1
                continue
            key = (d, r["field"])
            if key in raw:
                sys.exit(f"STOP: duplicate value for {key}")
            raw[key] = v

    rows, drops = [], []
    for d in days(FIRST, LAST):
        got = {f: raw.get((d, f)) for f in FIELDS}
        missing = [f for f in FIELDS if got[f] is None]
        if len(missing) == len(FIELDS):
            drops.append([STATION, d.isoformat(), "no field decoded", ";".join(missing)])
            continue
        row = {"station": STATION, "target_date": d.isoformat(), "target_hour": TARGET_HOUR,
               "run_date": (d - dt.timedelta(days=1)).isoformat(), "cycle": CYCLE, "lead": LEAD}
        a = 2 * math.pi * year_fraction(d)
        row["season_sin"], row["season_cos"] = math.sin(a), math.cos(a)
        # B
        tg = None
        if got["tmp2m"] is not None:
            tg = round((got["tmp2m"] - 273.15) + correction, 3)
        row["temperature_grib_c"] = row["temp"] = tg
        cc = None if got["tcdc"] is None else round(got["tcdc"], 3)
        row["cloud_cover_grib_pct"] = row["cloud_cover"] = cc
        ws = None
        if got["ugrd10m"] is not None and got["vgrd10m"] is not None:
            ws = round(((got["ugrd10m"] ** 2 + got["vgrd10m"] ** 2) ** 0.5) * 3.6, 3)
        row["wind_speed_grib_kmh"] = row["wind_speed_10m"] = ws
        t2m_raw = None if tg is None else round(tg - correction, 3)
        row["t2m_raw"] = t2m_raw
        # L
        for k in ("t925", "t850", "t700"):
            row[k] = None if got[k] is None else round(got[k] - 273.15, 3)
        row["lapse_rate_t2_t850"] = (None if t2m_raw is None or got["t850"] is None
                                     else round(t2m_raw - (got["t850"] - 273.15), 3))
        # D
        row["relative_humidity_2m"] = None if got["rh2m"] is None else round(got["rh2m"], 3)
        row["dew_point_2m"] = None if got["dpt2m"] is None else round(got["dpt2m"] - 273.15, 3)
        row["specific_humidity_2m"] = None if got["spfh2m"] is None else round(got["spfh2m"], 6)
        dd = (None if t2m_raw is None or got["dpt2m"] is None
              else round(t2m_raw - (got["dpt2m"] - 273.15), 3))
        row["dewpoint_depression_t2m"] = dd
        row["dewpoint_depression_t2m_floored"] = None if dd is None else max(dd, 0.0)
        # T
        msl = None if got["prmsl"] is None else round(got["prmsl"] / 100.0, 3)
        m3 = None if got["prmsl_m3"] is None else round(got["prmsl_m3"] / 100.0, 3)
        row["pressure_msl_hpa"] = msl
        row["pressure_surface_hpa"] = None if got["pres_sfc"] is None else round(got["pres_sfc"] / 100.0, 3)
        row["pressure_msl_lead_minus3_hpa"] = m3
        row["pressure_tendency_3h_hpa"] = None if msl is None or m3 is None else round(msl - m3, 3)
        # R (lead 26: native 24-26 h window, no de-accumulation)
        rr = None if got["dswrf"] is None else round(got["dswrf"], 3)
        row["dswrf_ave_to_lead_wm2"] = row["dswrf_2h_wm2"] = rr
        row["dswrf_ave_to_lead_minus2_wm2"] = None
        # complete case over every underlying column of the nine (the minus-2
        # DSWRF column is not applicable at lead 26)
        need = [row[c] for c in SANITY_COLS]
        row["complete_case"] = int(all(v is not None for v in need))
        if missing:
            drops.append([STATION, d.isoformat(), "field(s) not decoded", ";".join(missing)])
        rows.append(row)
    return rows, drops, nonfinite


def load_reports():
    reports, stats = {}, {"rows": 0, "no_temp": 0, "nonfinite": 0, "duplicates": 0}
    for a, b in OBS_CHUNKS:
        with open(RAW / f"iem_asos_{STATION}_{a}_{b}_routine.csv") as f:
            for r in csv.DictReader(f):
                if r["station"] != STATION:
                    sys.exit(f"STOP: unexpected station {r['station']}")
                stats["rows"] += 1
                t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                raw = (r.get("tmpc") or "").strip()
                v = None
                if raw not in ("M", "", "T", "None"):
                    v = finite_float(raw)
                    if v is None:
                        stats["nonfinite"] += 1
                if v is None:
                    stats["no_temp"] += 1
                if t in reports:
                    stats["duplicates"] += 1
                    continue
                reports[t] = v
    return reports, stats


def pair_all(reports):
    out = []
    for d in days(FIRST, LAST):
        target = dt.datetime(d.year, d.month, d.day, TARGET_HOUR)
        cands = []
        for m in range(-TOL_MIN, TOL_MIN + 1):
            t = target + dt.timedelta(minutes=m)
            if t in reports:
                cands.append((abs(m), m, t, reports[t]))
        cands.sort()
        usable = [c for c in cands if c[3] is not None]
        row = {"station": STATION, "target_date": d.isoformat(), "target_hour": TARGET_HOUR,
               "n_reports_in_window": len(cands), "n_usable_in_window": len(usable),
               "tie": 0, "tie_temps_differ": 0}
        if usable:
            best = usable[0]
            if len(usable) > 1 and usable[1][0] == best[0]:
                row["tie"] = 1
                row["tie_temps_differ"] = int(usable[1][3] != best[3])
            row.update(report_time=best[2].strftime("%Y-%m-%d %H:%M"), offset_min=best[1],
                       obs_c=best[3], pair_status="paired")
        else:
            row.update(report_time="", offset_min="", obs_c=None,
                       pair_status=("no routine report within 15 min" if not cands
                                    else "no usable temperature within 15 min"))
        out.append(row)
    return out


def write_new(path, cols, rows):
    if path.exists():
        sys.exit(f"STOP: {path.relative_to(ROOT)} already exists; not overwriting (SPEC 8.7 item 5).")
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([fmt(r[c]) if isinstance(r[c], float) or r[c] is None else r[c] for c in cols])


def in_range(s, rng):
    d = dt.date.fromisoformat(s)
    return rng[0] <= d <= rng[1]


def main():
    for p in (OUT_FEATURES, OUT_OBS, OUT_DROPS):
        if p.exists():
            sys.exit(f"STOP: {p.relative_to(ROOT)} already exists; not overwriting.")
    with open(PARAMS) as f:
        prow = list(csv.DictReader(f))[0]
    correction = float(prow["correction_c"])
    print("=" * 78)
    print("SESSION 76 - Step 5: build and checks (offline). Counts only for held-out rows.")
    print("=" * 78)
    print(f"KSFO elevation constant read back from {PARAMS.name}: {correction} degC")

    # ---- 5.1 features --------------------------------------------------------
    rows, drops, nonfinite = build_features(correction)
    write_new(OUT_FEATURES, FEATURE_COLS, rows)
    with open(OUT_DROPS, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "target_date", "reason", "missing_fields"])
        w.writerows(drops)
    print(f"\n--- 5.1 feature table: {OUT_FEATURES.relative_to(ROOT)} ---")
    print(f"columns ({len(FEATURE_COLS)}): {FEATURE_COLS}")
    print(f"non-finite GRIB values rejected at load, per field: {nonfinite}")
    print(f"rows written: {len(rows)} of 1956 calendar days; drop-log rows: {len(drops)} "
          f"({OUT_DROPS.relative_to(ROOT)})")
    for r in drops:
        print(f"  drop: {r[1]}  {r[2]}  missing={r[3]}")
    dd_floor = sum(1 for r in rows if r["dewpoint_depression_t2m"] is not None
                   and r["dewpoint_depression_t2m"] < 0)
    print(f"D floor transform: rows with dewpoint_depression_t2m < 0 (changed by the floor): {dd_floor}")
    t2_check = sum(1 for r in rows if r["t2m_raw"] is not None
                   and r["t2m_raw"] != round(r["temperature_grib_c"] - correction, 3))
    t_check = sum(1 for r in rows if r["pressure_tendency_3h_hpa"] is not None and
                  r["pressure_tendency_3h_hpa"] != round(r["pressure_msl_hpa"] - r["pressure_msl_lead_minus3_hpa"], 3))
    print(f"identity checks: t2m_raw == round(temperature_grib_c - c, 3) fails on {t2_check} rows; "
          f"tendency == round(msl - msl_m3, 3) fails on {t_check} rows")

    # ---- 5.2 observations ----------------------------------------------------
    reports, ostats = load_reports()
    pairs = pair_all(reports)
    obs_cols = ["station", "target_date", "target_hour", "report_time", "offset_min", "obs_c",
                "n_reports_in_window", "n_usable_in_window", "tie", "tie_temps_differ", "pair_status"]
    write_new(OUT_OBS, obs_cols, pairs)
    print(f"\n--- 5.2 paired observations: {OUT_OBS.relative_to(ROOT)} ---")
    print(f"routine rows read: {ostats['rows']}; rows with no usable tmpc: {ostats['no_temp']} "
          f"(of which non-finite: {ostats['nonfinite']}); duplicate timestamps skipped: {ostats['duplicates']}")
    paired = [p for p in pairs if p["pair_status"] == "paired"]
    offs = {}
    for p in paired:
        offs[p["offset_min"]] = offs.get(p["offset_min"], 0) + 1
    print(f"days: {len(pairs)}; paired {len(paired)}; dropped {len(pairs) - len(paired)}")
    print(f"paired offsets (minutes, signed, report minus 20:00): {dict(sorted(offs.items()))}")
    ties = [p for p in pairs if p["tie"]]
    print(f"tie days (two usable reports equally near): {len(ties)}; "
          f"with differing temperatures: {sum(p['tie_temps_differ'] for p in ties)}")
    for p in ties:
        print(f"  tie: {p['target_date']} (kept {p['report_time']})")
    reasons = {}
    for p in pairs:
        if p["pair_status"] != "paired":
            reasons[p["pair_status"]] = reasons.get(p["pair_status"], 0) + 1
    print(f"dropped days by reason: {reasons}")
    for p in pairs:
        if p["pair_status"] != "paired":
            print(f"  dropped: {p['target_date']}  {p['pair_status']}  "
                  f"(reports in window {p['n_reports_in_window']})")
    multi = sum(1 for p in pairs if p["n_usable_in_window"] > 1)
    print(f"days with more than one usable report in the window: {multi}")

    # ---- 5.3 counts ------------------------------------------------------------
    print("\n--- 5.3 counts (counts only) ---")
    feat = {r["target_date"]: r for r in rows}
    cc = {k for k, r in feat.items() if r["complete_case"] == 1}
    pd_ = {p["target_date"] for p in paired}
    brow = {k for k, r in feat.items() if r["temperature_grib_c"] is not None
            and r["cloud_cover_grib_pct"] is not None and r["wind_speed_grib_kmh"] is not None}

    def count_line(label, rng, expected):
        f_ = sum(1 for k in feat if in_range(k, rng))
        b_ = sum(1 for k in brow if in_range(k, rng))
        c_ = sum(1 for k in cc if in_range(k, rng))
        o_ = sum(1 for k in pd_ if in_range(k, rng))
        both = sum(1 for k in cc & pd_ if in_range(k, rng))
        print(f"{label:28s} {expected:>6d} {f_:>8d} {b_:>7d} {c_:>9d} {o_:>7d} {both:>7d}")

    print(f"{'period':28s} {'days':>6s} {'feature':>8s} {'B':>7s} {'complete':>9s} {'paired':>7s} {'both':>7s}")
    for y in range(2021, 2027):
        a, b = max(FIRST, dt.date(y, 1, 1)), min(LAST, dt.date(y, 12, 31))
        count_line(f"{y} ({a}..{b})", (a, b), (b - a).days + 1)
    for label, rng in WINDOWS.items():
        count_line(label, rng, (rng[1] - rng[0]).days + 1)
    count_line("whole window", (FIRST, LAST), (LAST - FIRST).days + 1)
    for fold, (tr, te) in FOLDS.items():
        count_line(f"fold {fold} train", tr, (tr[1] - tr[0]).days + 1)
        count_line(f"fold {fold} test", te, (te[1] - te[0]).days + 1)

    # ---- 5.4 reproduction gate (before 2024-08-01 only) ------------------------
    print("\n--- 5.4 reproduction gate: GRIB (elevation-adjusted) vs Open-Meteo, before 2024-08-01 ---")
    om = {}
    null_hours = []
    for name in OM_TEMP:
        d = json.load(open(RAW / name))
        for t, v in zip(d["hourly"]["time"], d["hourly"]["temperature_2m_previous_day1"]):
            if v is None:
                null_hours.append(t)
            else:
                om[t] = v
    print(f"Open-Meteo hours: {len(om) + len(null_hours)}; null {len(null_hours)}"
          + (f", first null {min(null_hours)}, last null {max(null_hours)}" if null_hours else ""))
    if null_hours:
        a = dt.datetime.fromisoformat(min(null_hours))
        b = dt.datetime.fromisoformat(max(null_hours))
        span = int((b - a).total_seconds() // 3600) + 1
        print(f"null hours contiguous: {span == len(null_hours)} (span {span} hours)")
    diffs, raw_diffs, n_no_om = [], [], 0
    for k, r in feat.items():
        if dt.date.fromisoformat(k) >= HELD_OUT_START or r["temperature_grib_c"] is None:
            continue
        o = om.get(f"{k}T{TARGET_HOUR:02d}:00")
        if o is None:
            n_no_om += 1
            continue
        diffs.append(r["temperature_grib_c"] - o)
        raw_diffs.append(r["t2m_raw"] - o)

    def gate(ds, label):
        ma = sum(abs(x) for x in ds) / len(ds)
        ms = sum(ds) / len(ds)
        mx = max(abs(x) for x in ds)
        v = "PASS" if (ma < 1.0 and abs(ms) < 1.0) else "FAIL"
        print(f"{label}: n={len(ds)} mean|diff|={ma:.3f} mean diff={ms:+.3f} max|diff|={mx:.3f} -> {v}")
        return v
    print(f"identical rows (both present): {len(diffs)}; GRIB rows with no Open-Meteo value: {n_no_om}")
    print("diff = GRIB minus Open-Meteo, degC; gate (F89/F90): mean|diff| < 1.0 and |mean diff| < 1.0")
    gate(raw_diffs, "before the elevation constant (t2m_raw)   ")
    verdict = gate(diffs, "after the elevation constant (temp), GATE")
    # Description only (two forecasts, before 2024-08-01): where the gap sits.
    by = {}
    for k, r in feat.items():
        o = om.get(f"{k}T{TARGET_HOUR:02d}:00")
        if dt.date.fromisoformat(k) >= HELD_OUT_START or r["temperature_grib_c"] is None or o is None:
            continue
        for key in (f"month {k[5:7]}", f"year {k[:4]}"):
            by.setdefault(key, []).append(r["temperature_grib_c"] - o)
    print("mean diff (GRIB minus Open-Meteo) by calendar month and by year, description only:")
    for key in sorted(by):
        ds = by[key]
        print(f"  {key:10s} n={len(ds):4d} mean diff={sum(ds) / len(ds):+.3f} "
              f"mean|diff|={sum(abs(x) for x in ds) / len(ds):.3f}")
    if verdict != "PASS":
        print("\nREPRODUCTION GATE FAILED. Stopping after reporting (Step 5.4): the constant and")
        print("the pipeline are not changed, and Step 5.5 is not run.")
        return 2

    # ---- 5.5 feature sanity (before 2024-08-01 only) ----------------------------
    print("\n--- 5.5 feature sanity, before 2024-08-01 only ---")
    pre = [r for k, r in feat.items() if dt.date.fromisoformat(k) < HELD_OUT_START]
    print(f"{'column':34s} {'count':>6s} {'min':>11s} {'max':>11s}")
    for c in SANITY_COLS:
        vs = [r[c] for r in pre if r[c] is not None]
        print(f"{c:34s} {len(vs):>6d} {min(vs):>11.4f} {max(vs):>11.4f}")
    print(f"non-finite values dropped at load (all periods, per GRIB field): {nonfinite}")
    colder = sum(1 for r in pre if None not in (r["t925"], r["t850"], r["t700"])
                 and r["t925"] > r["t850"] > r["t700"])
    print(f"rows with t925 > t850 > t700 (colder with height aloft): {colder} of {len(pre)}")
    dp_over = sum(1 for r in pre if None not in (r["dew_point_2m"], r["t2m_raw"])
                  and r["dew_point_2m"] > r["t2m_raw"])
    print(f"rows with dew_point_2m > t2m_raw: {dp_over}")
    neg_r = sum(1 for r in pre if r["dswrf_2h_wm2"] is not None and r["dswrf_2h_wm2"] < 0)
    print(f"rows with negative dswrf_2h_wm2: {neg_r}")

    print("\ncloud and wind against Open-Meteo, 2024-01-19..2024-07-31 (F90's method and thresholds)")
    d = json.load(open(OM_CLOUDWIND))
    h = d["hourly"]
    omc = dict(zip(h["time"], h["cloud_cover_previous_day1"]))
    omw = dict(zip(h["time"], h["wind_speed_10m_previous_day1"]))
    print(f"Open-Meteo units: {d.get('hourly_units')}")
    cdf, wdf = [], []
    for k, r in feat.items():
        if not in_range(k, (dt.date(2024, 1, 19), dt.date(2024, 7, 31))):
            continue
        key = f"{k}T{TARGET_HOUR:02d}:00"
        if omc.get(key) is not None and r["cloud_cover_grib_pct"] is not None:
            cdf.append(r["cloud_cover_grib_pct"] - omc[key])
        if omw.get(key) is not None and r["wind_speed_grib_kmh"] is not None:
            wdf.append(r["wind_speed_grib_kmh"] - omw[key])

    def summ(ds, label, thr):
        ma = sum(abs(x) for x in ds) / len(ds)
        ms = sum(ds) / len(ds)
        mx = max(abs(x) for x in ds)
        print(f"{label}: n={len(ds)} mean|diff|={ma:.3f} mean_diff={ms:+.3f} max|diff|={mx:.3f} "
              f"-> {'PASS' if ma < thr else 'FAIL'} (threshold {thr}, session37_decode.py)")
    summ(cdf, "cloud_cover (pct) ", 15.0)
    summ(wdf, "wind_speed (km/h) ", 3.0)
    s = sorted(abs(x) for x in cdf)
    print("cloud |diff| percentiles p50/p75/p90/p95/p99: "
          + "/".join(f"{s[min(len(s) - 1, int(q * len(s)))]:.1f}" for q in (0.5, 0.75, 0.9, 0.95, 0.99)))

    print(f"\nreproduction gate verdict: {verdict}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
