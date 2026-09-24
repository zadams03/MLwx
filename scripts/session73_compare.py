"""Session 73, Step 5: compare the clean-room rebuild with the F109 record at
RNO, stage by stage (D64.4). The clean room lifts here: this is the only
session 73 code that opens scripts/, data/processed/ or notes/.

Report only. Nothing is fixed, re-run or tuned (D64.5). No model is fitted.

Match rule (session 73 prompt): round the rebuild value to the record's
stored precision, then test for equality. If the rebuild stores fewer
decimals than the record, compare at the coarser of the two and say so.

Record-side values that no committed file stores per day (the F109 script
computed them in memory) are rebuilt here from committed record inputs by
re-applying the record script's own logic, and are labelled so:
  - observation and report time: session62_reserved_confirm.py
    load_obs_all() (lines 321-344) applied to the committed raw IEM files;
  - season terms: its year_fraction()/make_feature_vector() (lines 217-236);
  - complete-case set: its build_complete_case()/join_obs() (347-377);
  - persistence: its raw_persist() (394-404).

Usage: python scripts/session73_compare.py
"""

import csv
import hashlib
import math
import os
import re
import sys
from datetime import date, datetime, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REB72 = os.path.join(ROOT, "data", "rebuild", "session72")
REB73 = os.path.join(ROOT, "data", "rebuild", "session73")
CMP = os.path.join(REB73, "comparison")
PROC = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")

TRAIN = ("2021-03-24", "2024-07-31")
TEST = ("2024-08-01", "2025-07-31")
F109 = {"raw_gfs": "1.6135", "persistence": "2.7563", "B": "1.4272",
        "BDLRT": "1.2742"}

REC = {
    "base": os.path.join(PROC, "grib_features_v16_window.csv"),
    "joined38": os.path.join(PROC, "session38_joined.csv"),
    "L_tr": os.path.join(PROC, "session49_v16_window_with_upper_air.csv"),
    "D_tr": os.path.join(PROC, "session51_v16_window_with_moisture.csv"),
    "T_tr": os.path.join(PROC, "session53_v16_window_with_pressure.csv"),
    "R_tr": os.path.join(PROC, "session55_v16_window_with_radiation.csv"),
    "L_te": os.path.join(PROC, "session63_reserved_window_with_upper_air.csv"),
    "D_te": os.path.join(PROC, "session63_reserved_window_with_moisture.csv"),
    "T_te": os.path.join(PROC, "session63_reserved_window_with_pressure.csv"),
    "R_te": os.path.join(PROC, "session63_reserved_window_with_radiation.csv"),
    "grid": os.path.join(PROC, "session63_reserved_confirm_grid.csv"),
    "script": os.path.join(ROOT, "scripts", "session62_reserved_confirm.py"),
    "confirm_out": os.path.join(ROOT, "notes", "session-64-confirm-output.txt"),
    "s72_out": os.path.join(ROOT, "notes", "session-72-output.txt"),
}
OBS_CHUNKS = [("2021-03-24", "2021-12-31"), ("2022-01-01", "2022-12-31"),
              ("2023-01-01", "2023-12-31"), ("2024-01-01", "2024-12-31"),
              ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]

OPENED = []
SUMMARY = []


def rel(p):
    return os.path.relpath(p, ROOT)


def opened(p, mode="read"):
    OPENED.append((rel(p), mode))


def read_csv(p, station=None):
    opened(p)
    with open(p, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if station:
        rows = [r for r in rows if r.get("station") == station]
    return rows


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def decimals(s):
    s = s.strip()
    if s == "" or "e" in s.lower():
        return None
    return len(s.split(".")[1]) if "." in s else 0


def col_precision(strings):
    ds = [decimals(s) for s in strings if s not in ("", None)]
    ds = [d for d in ds if d is not None]
    return max(ds) if ds else None


def win(d):
    return ("train" if TRAIN[0] <= d <= TRAIN[1] else
            "test" if TEST[0] <= d <= TEST[1] else None)


# ------------------------------------------------------------------ helpers

def compare_values(stage, name, reb, rec, reb_prec, rec_prec, note=""):
    """reb, rec: {date: string or None}. Exact match after rounding to the
    record's precision (or the coarser of the two)."""
    k = rec_prec
    coarser = False
    if reb_prec is not None and (rec_prec is None or reb_prec < rec_prec):
        k, coarser = reb_prec, True
    dates = sorted(set(reb) | set(rec))
    n = nm = 0
    mism = []
    maxd = 0.0
    for d in dates:
        a, b = reb.get(d), rec.get(d)
        if a in (None, "") and b in (None, ""):
            continue
        n += 1
        if a in (None, "") or b in (None, ""):
            mism.append((d, a, b, "present in one side only"))
            continue
        fa, fb = float(a), float(b)
        if k is None:
            ok = fa == fb
        else:
            ok = round(fa, k) == round(fb, k)
        diff = abs(fa - fb)
        if ok:
            nm += 1
        else:
            maxd = max(maxd, abs(round(fa, k) - round(fb, k))
                       if k is not None else diff)
            mism.append((d, a, b, "differs at %s decimals" % k))
    res = dict(stage=stage, item=name, n=n, matched=nm, mismatched=len(mism),
               max_abs_diff=maxd, precision=k, coarser=coarser, note=note,
               mismatches=mism)
    report(res)
    return res


def compare_sets(stage, name, reb_set, rec_set, note=""):
    both = reb_set & rec_set
    only_reb = sorted(reb_set - rec_set)
    only_rec = sorted(rec_set - reb_set)
    mism = [(d, "in rebuild", "absent", "rebuild only") for d in only_reb] + \
           [(d, "absent", "in record", "record only") for d in only_rec]
    res = dict(stage=stage, item=name, n=len(reb_set | rec_set),
               matched=len(both), mismatched=len(mism), max_abs_diff=None,
               precision="set", coarser=False, note=note,
               mismatches=sorted(mism))
    report(res)
    return res


def report(res):
    SUMMARY.append(res)
    print("  [%s] %-44s n=%d matched=%d mismatched=%d max_abs_diff=%s "
          "precision=%s%s%s" % (
              res["stage"], res["item"], res["n"], res["matched"],
              res["mismatched"], res["max_abs_diff"], res["precision"],
              " (coarser: rebuild stores fewer decimals)" if res["coarser"]
              else "", ("  -- " + res["note"]) if res["note"] else ""))
    for m in res["mismatches"][:20]:
        print("      mismatch %s  rebuild=%s  record=%s  (%s)" % m)
    if res["mismatches"]:
        safe = re.sub(r"[^A-Za-z0-9_]+", "_", "%s_%s" % (res["stage"],
                                                        res["item"]))
        p = os.path.join(CMP, "mismatch_%s.csv" % safe.strip("_"))
        if os.path.exists(p):
            raise SystemExit("refusing to overwrite " + rel(p))
        opened(p, "write")
        with open(p, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["stage", "item", "target_date", "rebuild", "record",
                        "detail"])
            for m in res["mismatches"]:
                w.writerow([res["stage"], res["item"]] + list(m))


# ------------------------------------------------------------------ record-side logic (from session62_reserved_confirm.py)

def record_obs():
    """load_obs_all() rule, lines 321-344, with the report time kept.
    Keeps the LAST qualifying report per day, as the historical code does
    (SPEC 4.5 note, D62)."""
    series, times = {}, {}
    for s, e in OBS_CHUNKS:
        p = os.path.join(RAW, "iem_asos_RNO_%s_%s_routine.csv" % (s, e))
        opened(p)
        with open(p, newline="") as fh:
            for r in csv.DictReader(fh):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != 20:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    continue
                series[nearest.date().isoformat()] = raw
                times[nearest.date().isoformat()] = t.strftime("%Y-%m-%d %H:%M")
    return series, times


def record_season(d):
    dd = date.fromisoformat(d)
    yd = 366 if (dd.year % 4 == 0 and (dd.year % 100 != 0
                                        or dd.year % 400 == 0)) else 365
    a = 2 * math.pi * ((dd.timetuple().tm_yday - 1) / yd)
    return math.sin(a), math.cos(a)


# ------------------------------------------------------------------ main

def main():
    print("SESSION 73 STEP 5 -- comparison with the record (D64.4)")
    if os.path.exists(CMP):
        raise SystemExit("refusing: %s already exists" % rel(CMP))

    # 0. Seal re-check.
    seal = os.path.join(REB73, "SEAL_SHA256.txt")
    opened(seal)
    lines = [ln for ln in open(seal).read().splitlines() if ln.strip()]
    bad = 0
    print("Seal re-check (%d files):" % len(lines))
    for ln in lines:
        h, p = ln.split("  ", 1)
        now = sha256(os.path.join(ROOT, p))
        print("  %s %s" % ("unchanged" if now == h else "CHANGED  ", p))
        bad += now != h
    present = sorted(rel(os.path.join(dp, f)) for dp, _, fs in os.walk(REB73)
                     for f in fs)
    extra = [p for p in present if p not in [l.split("  ", 1)[1]
                                              for l in lines]
             and not p.endswith("SEAL_SHA256.txt")]
    print("  files changed: %d; files not in the seal list: %s" % (bad, extra))
    if bad or extra:
        raise SystemExit("seal broken -- stopping before any comparison")
    os.makedirs(CMP)

    # Load rebuild.
    f72 = {r["target_date"]: r for r in read_csv(os.path.join(REB72, "rno_features.csv"))}
    o72 = {r["target_date"]: r for r in read_csv(os.path.join(REB72, "rno_observations.csv"))}
    p72 = {r["target_date"]: r for r in read_csv(os.path.join(REB72, "rno_persistence.csv"))}
    rungs = {r["target_date"]: r for r in read_csv(os.path.join(REB73, "rno_test_rungs.csv"))}
    mae73 = {r["rung"]: r for r in read_csv(os.path.join(REB73, "rno_mae_table.csv"))}
    preds73 = read_csv(os.path.join(REB73, "rno_test_predictions.csv"))
    dates = sorted(f72)

    # G4-alt derived columns (as session73_fit_score.py derives them).
    g4 = {}
    for d, r in f72.items():
        if r["t2m_raw_from_full"] == "":
            g4[d] = {"L": "", "D": "", "Dfl": ""}
            continue
        tf = float(r["t2m_raw_from_full"])
        L = round(tf - float(r["t850"]), 3)
        D = round(tf - float(r["dew_point_2m"]), 3)
        g4[d] = {"L": repr(L), "D": repr(D), "Dfl": repr(max(D, 0.0))}

    # Load record.
    base = {r["target_date"]: r for r in read_csv(REC["base"], "RNO")}
    j38 = {r["target_date"]: r for r in read_csv(REC["joined38"], "RNO")}
    fam = {}
    for k in "LDTR":
        rows = read_csv(REC[k + "_tr"], "RNO") + read_csv(REC[k + "_te"], "RNO")
        fam[k] = {r["target_date"]: r for r in rows if win(r["target_date"])}
    grid = read_csv(REC["grid"], "RNO")[0]
    opened(REC["script"])
    opened(REC["confirm_out"])
    confirm_txt = open(REC["confirm_out"]).read()
    rec_obs, rec_time = record_obs()

    inwin = lambda m: {d: v for d, v in m.items() if win(d)}

    # ---------------- Stage 1: observations and targets
    print("\nSTAGE 1 -- observations and targets")
    compare_values("1", "obs_c vs record rule on raw IEM (load_obs_all)",
                   inwin({d: o72[d]["obs_c"] for d in dates}),
                   inwin(rec_obs),
                   col_precision(o72[d]["obs_c"] for d in dates),
                   col_precision(rec_obs.values()))
    compare_values("1", "obs_c vs session38_joined.obs_temp_c",
                   inwin({d: o72[d]["obs_c"] for d in dates}),
                   inwin({d: r["obs_temp_c"] for d, r in j38.items()}),
                   col_precision(o72[d]["obs_c"] for d in dates),
                   col_precision(r["obs_temp_c"] for r in j38.values()))
    # report time: compare as strings
    reb_t = inwin({d: o72[d]["report_time_utc"] for d in dates
                   if o72[d]["report_time_utc"]})
    rt_mism = [(d, reb_t.get(d, ""), rec_time.get(d, ""), "time differs")
               for d in sorted(set(reb_t) | set(inwin(rec_time)))
               if reb_t.get(d) != rec_time.get(d)]
    report(dict(stage="1", item="report_time_utc vs record rule",
                n=len(set(reb_t) | set(inwin(rec_time))),
                matched=len(set(reb_t) | set(inwin(rec_time))) - len(rt_mism),
                mismatched=len(rt_mism), max_abs_diff=None,
                precision="minute", coarser=False,
                note="record rule keeps the last qualifying report",
                mismatches=rt_mism))
    compare_values("1", "residual_c vs session38_joined.resid",
                   inwin({d: o72[d]["residual_c"] for d in dates}),
                   inwin({d: r["resid"] for d, r in j38.items()}),
                   col_precision(o72[d]["residual_c"] for d in dates),
                   col_precision(r["resid"] for r in j38.values()))
    rec_resid = {d: repr(float(rec_obs[d]) - float(base[d]["temperature_grib_c"]))
                 for d in rec_obs if d in base and win(d)}
    compare_values("1", "residual_c vs record in-memory obs - fc (unrounded)",
                   inwin({d: o72[d]["residual_c"] for d in dates}), rec_resid,
                   3, None,
                   note="record stores no rounded residual; rebuild stores 3 "
                        "dp, so compared at 3 dp (coarser)")

    # ---------------- Stage 2: pairing and day set
    print("\nSTAGE 2 -- pairing and the day set")
    reb_paired = {d for d in dates if o72[d]["pair_status"] == "paired"}
    compare_sets("2", "paired days vs record rule on raw IEM", reb_paired,
                 set(inwin(rec_obs)))
    compare_sets("2", "paired days vs session38_joined days", reb_paired,
                 {d for d in j38 if win(d)} | ({"2022-11-30"} if "2022-11-30"
                                              in rec_obs else set()),
                 note="session38_joined needs a forecast too; 2022-11-30 "
                      "(no B forecast) is added back to the record side "
                      "when the raw rule pairs it")
    compare_sets("2", "calendar day set (features table) vs record B file",
                 {d for d in dates if f72[d]["missing_inputs"] == ""},
                 {d for d in base if win(d)})

    # ---------------- Stage 3: feature columns
    def stage3(variant):
        print("\nSTAGE 3 -- feature columns, Variant %s" % variant)
        out = []
        b_cols = [("temperature_grib_c", "temperature_grib_c"),
                  ("cloud_cover_grib_pct", "cloud_cover_grib_pct"),
                  ("wind_speed_grib_kmh", "wind_speed_grib_kmh")]
        for rc, cc in b_cols:
            out.append(compare_values(
                "3" + variant, "B " + rc,
                {d: f72[d][rc] for d in dates},
                {d: base[d][cc] for d in base if win(d)},
                col_precision(f72[d][rc] for d in dates),
                col_precision(r[cc] for r in base.values())))
        for i, nm in enumerate(["season_sin", "season_cos"]):
            out.append(compare_values(
                "3" + variant, "B " + nm + " (record code, recomputed)",
                {d: f72[d][nm] for d in dates},
                {d: repr(record_season(d)[i]) for d in dates}, None, None,
                note="not stored in any record file; exact float equality"))
        if variant == "P":
            t2m = {d: f72[d]["t2m_raw"] for d in dates}
            L = {d: f72[d]["lapse_rate_t2_t850"] for d in dates}
            D = {d: f72[d]["dewpoint_depression_t2m"] for d in dates}
            Dfl = {d: f72[d]["dewpoint_depression_t2m_floored"] for d in dates}
        else:
            t2m = {d: f72[d]["t2m_raw_from_full"] for d in dates}
            L = {d: g4[d]["L"] for d in dates}
            D = {d: g4[d]["D"] for d in dates}
            Dfl = {d: g4[d]["Dfl"] for d in dates}
        rec_dfl = {d: repr(max(float(r["dewpoint_depression_t2m"]), 0.0))
                   for d, r in fam["D"].items()}
        items = [
            ("L lapse_rate_t2_t850", L, fam["L"], "lapse_rate_t2_t850"),
            ("D dewpoint_depression_t2m", D, fam["D"], "dewpoint_depression_t2m"),
            ("T pressure_tendency_3h_hpa", {d: f72[d]["pressure_tendency_3h_hpa"] for d in dates},
             fam["T"], "pressure_tendency_3h_hpa"),
            ("R dswrf_2h_wm2", {d: f72[d]["dswrf_2h_wm2"] for d in dates},
             fam["R"], "dswrf_2h_wm2"),
            ("input t2m_raw (L file)", t2m, fam["L"], "t2m_raw"),
            ("input t2m_raw (D file)", t2m, fam["D"], "t2m_raw"),
            ("input t850", {d: f72[d]["t850"] for d in dates}, fam["L"], "t850"),
            ("input dew_point_2m", {d: f72[d]["dew_point_2m"] for d in dates},
             fam["D"], "dew_point_2m"),
            ("input pressure_msl_hpa", {d: f72[d]["pressure_msl_hpa"] for d in dates},
             fam["T"], "pressure_msl_hpa"),
            ("input pressure_surface_hpa", {d: f72[d]["pressure_surface_hpa"] for d in dates},
             fam["T"], "pressure_surface_hpa"),
            ("input pressure_msl_lead_minus3_hpa",
             {d: f72[d]["pressure_msl_lead_minus3_hpa"] for d in dates},
             fam["T"], "pressure_msl_lead_minus3_hpa"),
            ("input dswrf_ave_to_lead_wm2",
             {d: f72[d]["dswrf_ave_to_lead_wm2"] for d in dates},
             fam["R"], "dswrf_ave_to_lead_wm2"),
        ]
        for nm, rebm, recrows, col in items:
            reb_strings = [v for v in rebm.values() if v]
            out.append(compare_values(
                "3" + variant, nm, rebm,
                {d: r[col] for d, r in recrows.items()},
                col_precision(reb_strings),
                col_precision(r[col] for r in recrows.values())))
        out.append(compare_values(
            "3" + variant, "D floored (model input; record floors in memory)",
            Dfl, rec_dfl, 3, 3))
        return out

    s3 = {"P": stage3("P"), "G4alt": stage3("G4alt")}

    # ---------------- Stage 4: complete-case row set and counts
    print("\nSTAGE 4 -- complete-case row set and counts")
    rec_cc = set(base) & set(fam["L"]) & set(fam["D"]) & set(fam["T"]) & set(fam["R"])
    rec_cc = {d for d in rec_cc if win(d)}
    rec_joined = {d for d in rec_cc if d in rec_obs}
    reb_cc = {d for d in dates if f72[d]["missing_inputs"] == ""}
    reb_joined = {d for d in reb_cc if o72[d]["residual_c"] != ""}
    for w in ("train", "test"):
        compare_sets("4", "feature complete-case set, %s" % w,
                     {d for d in reb_cc if win(d) == w},
                     {d for d in rec_cc if win(d) == w})
        compare_sets("4", "complete-case with observation, %s" % w,
                     {d for d in reb_joined if win(d) == w},
                     {d for d in rec_joined if win(d) == w})
    m = re.search(r"RNO: n_train=(\d+) n_test=(\d+) no_obs_dropped=(\d+) "
                  r"no_prev=(\d+)", confirm_txt)
    f109_counts = dict(zip(["n_train", "n_test", "no_obs_dropped", "no_prev"],
                           map(int, m.groups())))
    reb_counts = {"n_train": sum(win(d) == "train" for d in reb_joined),
                  "n_test": sum(win(d) == "test" for d in reb_joined),
                  "no_obs_dropped": sum(win(d) == "test" for d in reb_cc - reb_joined),
                  "no_prev": sum(1 for d in reb_joined if win(d) == "test"
                                 and p72[d]["persistence_c"] == "")}
    cmis = [(k, str(reb_counts[k]), str(v), "count differs")
            for k, v in f109_counts.items() if reb_counts[k] != v]
    report(dict(stage="4", item="counts vs F109 (session-64-confirm-output.txt)",
                n=4, matched=4 - len(cmis), mismatched=len(cmis),
                max_abs_diff=None, precision="integer", coarser=False,
                note="rebuild %s; record %s" % (reb_counts, f109_counts),
                mismatches=cmis))
    fit_counts = {}
    import json
    mp = os.path.join(REB73, "rno_fit_metadata.json")
    opened(mp)
    meta = json.load(open(mp))
    for mdl, info in meta["models"].items():
        fit_counts[mdl] = (info["n_train"], info["n_test"])
    print("  fitted-model counts (rebuild metadata): %s" % fit_counts)

    # ---------------- Stage 5: raw GFS and persistence values
    print("\nSTAGE 5 -- raw GFS and persistence values (test window)")
    test_rows = sorted(d for d in rec_joined if win(d) == "test")
    compare_values("5", "raw GFS (record fc = temperature_grib_c)",
                   {d: rungs[d]["raw_gfs_c"] for d in rungs},
                   {d: base[d]["temperature_grib_c"] for d in test_rows},
                   3, col_precision(base[d]["temperature_grib_c"] for d in test_rows))
    rec_pers = {}
    for d in test_rows:
        prev = (date.fromisoformat(d) - timedelta(days=1)).isoformat()
        if prev in rec_obs:
            rec_pers[d] = rec_obs[prev]
    compare_values("5", "persistence (record raw_persist rule)",
                   {d: rungs[d]["persistence_c"] for d in rungs}, rec_pers,
                   col_precision(r["persistence_c"] for r in rungs.values()),
                   col_precision(rec_pers.values()))

    # ---------------- Stage 6: model predictions
    print("\nSTAGE 6 -- model predictions")
    report(dict(stage="6", item="per-day model predictions", n=0, matched=0,
                mismatched=0, max_abs_diff=None, precision="n/a",
                coarser=False, mismatches=[],
                note="NOT COMPARABLE: no record file stores per-day "
                     "predictions (run_confirm() writes only per-airport MAEs "
                     "to session63_reserved_confirm_grid.csv)"))

    # ---------------- Stage 7: MAE
    print("\nSTAGE 7 -- MAE")
    rows7 = []
    for variant, mdl in (("P", "BDLRT_P"), ("G4alt", "BDLRT_G4alt")):
        pairs = [("raw_gfs", "raw_mae", "raw_gfs"),
                 ("persistence", "persist_mae", "persistence"),
                 ("B", "b_mae", "B"), (mdl, "final_mae", "BDLRT")]
        for rung, gcol, fkey in pairs:
            reb = mae73[rung]
            ok4 = reb["mae_4dp"] == F109[fkey]
            okfull = float(reb["mae_unrounded"]) == float(grid[gcol])
            diff = abs(float(reb["mae_unrounded"]) - float(grid[gcol]))
            rows7.append([variant, rung, reb["n"], reb["mae_unrounded"],
                          reb["mae_4dp"], F109[fkey], grid[gcol],
                          "match" if ok4 else "MISMATCH",
                          "match" if okfull else "MISMATCH", repr(diff)])
            print("  [7%s] %-12s rebuild %s (%s) | F109 %s %s | grid %s %s | "
                  "abs diff %r" % (variant, rung, reb["mae_unrounded"],
                                   reb["mae_4dp"], F109[fkey],
                                   "match" if ok4 else "MISMATCH", grid[gcol],
                                   "match" if okfull else "MISMATCH", diff))
            res = dict(stage="7" + variant, item="MAE " + rung, n=1,
                       matched=int(ok4), mismatched=int(not ok4),
                       max_abs_diff=diff, precision=4, coarser=False,
                       note="full-precision grid: %s" % ("match" if okfull
                                                          else "MISMATCH"),
                       mismatches=[] if ok4 else [
                           ("reserved year", reb["mae_4dp"], F109[fkey],
                            "4 dp; unrounded rebuild %s vs grid %s"
                            % (reb["mae_unrounded"], grid[gcol]))])
            SUMMARY.append(res)
            if not ok4:
                p = os.path.join(CMP, "mismatch_7%s_MAE_%s.csv" % (variant, rung))
                opened(p, "write")
                with open(p, "w", newline="") as fh:
                    w = csv.writer(fh)
                    w.writerow(["stage", "item", "target_date", "rebuild",
                                "record", "detail"])
                    w.writerow(["7" + variant, "MAE " + rung] +
                               list(res["mismatches"][0]))
    p = os.path.join(CMP, "stage7_mae.csv")
    opened(p, "write")
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["variant", "rung", "n", "rebuild_unrounded", "rebuild_4dp",
                    "f109_4dp", "record_grid_unrounded", "match_4dp",
                    "match_full", "abs_diff_full"])
        w.writerows(rows7)

    # ---------------- Record facts relevant to the fit (reported only)
    print("\nRECORD FACTS (from session62_reserved_confirm.py; reported only)")
    src = open(REC["script"]).read()
    for pat in [r'FINAL_CODES = .*', r'BASE_KEYS = .*',
                r'FINAL_FEATURE_KEYS = .*',
                r'rows.append\(\{\*\*base, "obs": o, "resid": .*',
                r'e_model = .*', r'm = lgb\.LGBMRegressor.*',
                r'"dewpoint_depression_t2m_floored": max.*']:
        mm = re.search(pat, src)
        ln = src[:mm.start()].count("\n") + 1
        print("  line %d: %s" % (ln, mm.group(0).strip()))
    reb_order = meta["models"]["BDLRT_P"]["feature_order"]
    print("  rebuild B+D,L,R,T column order: %s" % reb_order)
    print("  record  B+D,L,R,T column order: temp, season_sin, season_cos, "
          "cloud_cover, wind_speed_10m, dewpoint_depression_t2m_floored, "
          "lapse_rate_t2_t850, dswrf_2h_wm2, pressure_tendency_3h_hpa")

    # ---------------- Diagnostics
    print("\nDIAGNOSTIC G4 (report only)")
    diff655 = {d for d in dates if f72[d]["t2m_raw"] != f72[d]["t2m_raw_from_full"]}
    print("  rows where t2m_raw != t2m_raw_from_full: %d" % len(diff655))
    for variant in ("P", "G4alt"):
        for res in s3[variant]:
            if res["item"].startswith(("L ", "D ", "input t2m_raw", "D floored")):
                md = {m_[0] for m_ in res["mismatches"]}
                print("  Variant %-5s %-36s mismatched %4d; inside the 655: %d;"
                      " outside: %d" % (variant, res["item"], len(md),
                                        len(md & diff655), len(md - diff655)))

    print("\nDIAGNOSTIC G5 (report only): 2.0436 vs 2.04356932")
    n = same_a = same_b = both = 0
    flips = []
    for d in dates:
        r = f72[d]
        if r["t2m_grib_uncorrected_c_full"] == "" or d not in base:
            continue
        n += 1
        u = float(r["t2m_grib_uncorrected_c_full"])
        a = round(u + 2.0436, 3)
        b = round(u + 2.04356932, 3)
        rec = float(base[d]["temperature_grib_c"])
        same_a += a == rec
        same_b += b == rec
        both += (a == rec) and (b == rec)
        if a != b:
            flips.append((d, a, b, rec))
    print("  rows checked %d; record temperature_grib_c equals "
          "round(u+2.0436,3) on %d, round(u+2.04356932,3) on %d, both on %d"
          % (n, same_a, same_b, both))
    print("  rows where the two constants give different 3-dp values: %d"
          % len(flips))
    for f in flips[:20]:
        print("    %s  2.0436->%.3f  2.04356932->%.3f  record %.3f" % f)
    b_mis = sum(r["mismatched"] for r in SUMMARY
                if r["item"] in ("B temperature_grib_c",
                                 "residual_c vs session38_joined.resid",
                                 "raw GFS (record fc = temperature_grib_c)"))
    print("  mismatches in B temperature, target (3 dp) or raw GFS: %d" % b_mis)

    print("\nDIAGNOSTIC: session 72's clean room (read log in "
          "notes/session-72-output.txt)")
    opened(REC["s72_out"])
    s72 = open(REC["s72_out"]).read().splitlines()
    hits = [(i + 1, ln) for i, ln in enumerate(s72)
            if re.search(r"(scripts/|data/processed/|notes/)", ln)]
    params = [(i + 1, ln) for i, ln in enumerate(s72)
              if re.search(r"params.*\.csv|\.csv.*params", ln, re.I)]
    print("  lines naming scripts/, data/processed/ or notes/: %d" % len(hits))
    for i, ln in hits:
        print("    line %d: %s" % (i, ln.strip()[:160]))
    print("  lines naming a params CSV: %d" % len(params))
    for i, ln in params:
        print("    line %d: %s" % (i, ln.strip()[:160]))

    # ---------------- Summary
    p = os.path.join(CMP, "stage_summary.csv")
    opened(p, "write")
    with open(p, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "item", "n", "matched", "mismatched",
                    "max_abs_diff", "precision", "coarser", "note"])
        for r in SUMMARY:
            w.writerow([r["stage"], r["item"], r["n"], r["matched"],
                        r["mismatched"], r["max_abs_diff"], r["precision"],
                        r["coarser"], r["note"]])
    print("\nFILES OPENED BY THIS SCRIPT")
    for p_, mode in OPENED:
        print("  %-5s %s" % (mode, p_))


if __name__ == "__main__":
    main()
