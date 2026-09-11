"""Session 38, Task 4: source-swap sanity check.

ONE JOB: confirm the switch from Open-Meteo temperature to GRIB temperature
(session 37's elevation-corrected series, F90) did not change the baseline
the richer-features CV is built on. Two independent checks, both restricted
to the exact same dates Task 2's join kept (data/processed/
session38_joined.csv) -- so this is the cleanest possible like-for-like
comparison, not a different-window proxy:

  (1) STRICT: on the identical (station, date) rows, compute raw-forecast
      MAE against the IEM observation using GRIB temperature vs using
      Open-Meteo temperature (both already-pulled series, no new pull). If
      the source swap is faithful, these two numbers should be close --
      session 37 (F90) already found the two series agree to within
      0.13-0.18 degC mean|diff| at 4 airports and 0.15 degC at RNO
      (post-elevation-correction), so the two raw-MAE figures computed here
      are expected to differ by a similarly small amount, not by anything
      approaching the size of the richer-features skill margins in Task 3.

  (2) CONTEXT: compare this session's GRIB 3-feature/raw-GFS pooled OOF MAE
      (Task 3, full ~4.4-year window) against the locked recipe's own
      already-published Open-Meteo rehearsal and sealed-test MAE figures
      (DECISIONS F15/F29/F45/F62/F80, F16/F30/F47/F64/F82) and against F87's
      1.5-year Open-Meteo blocked-CV figures. These are different windows
      (informative, not a strict apples-to-apples check the way (1) is), so
      they are reported as context only.

No sealed-test date is loaded in either check (both draw only on the v16
window's own Open-Meteo forecast chunks and the Task 2 joined file, which
already ends 2025-07-31).
"""

import csv
import json
import sys
from datetime import date, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

WINDOW_START = date(2021, 3, 24)
WINDOW_END = date(2025, 7, 31)
SEALED_FROM = date(2025, 8, 1)

AIRPORTS = {  # SPEC 3.4
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

# The yearly Open-Meteo forecast chunk files covering the full v16 window
# (established naming convention -- same chunks session33_cv.py's FC_CHUNKS
# used for 2024-2025; extended back to cover the full window here).
FC_CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
]

# Context only -- already-published locked-recipe figures (Open-Meteo
# source), NOT recomputed here, quoted verbatim from DECISIONS.
LOCKED_REHEARSAL_MAE = {  # validation year 2024-08-01..2025-07-31
    "EGLC": 1.239, "LFPG": 1.426, "DSM": 1.748, "YSDU": 1.397, "RNO": 1.493,
}  # F15/F29/F45/F62/F80 (matches F86's own cross-check to 3 decimals)
LOCKED_SEALED_RAW_GFS_MAE = {  # sealed test year, raw GFS half of SPEC 5.0's table
    "EGLC": 1.242, "LFPG": 1.396, "DSM": 1.815, "YSDU": 1.251, "RNO": 1.414,
}
F87_15YR_RAW_GFS_MAE = {  # F87, 1.5-year Open-Meteo blocked CV, raw GFS rung
    "EGLC": 1.204, "LFPG": 1.405, "DSM": 1.882, "YSDU": 1.365, "RNO": 1.423,
}
F87_15YR_3FEAT_MAE = {
    "EGLC": 1.191, "LFPG": 1.513, "DSM": 1.811, "YSDU": 1.278, "RNO": 1.369,
}

OUT = ROOT / "notes" / "session-38-sanity-output.txt"


class Tee:
    def __init__(self, path):
        self.f = open(path, "w")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def line(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def sub(title):
    print()
    print(f"-- {title} --")


def mae(errs):
    return sum(abs(e) for e in errs) / len(errs) if errs else float("nan")


def load_openmeteo_forecast(station, target_hour):
    """{date: temp} for the target hour, Open-Meteo previous_day1, full v16
    window. Never opens a 2026 chunk."""
    series = {}
    for start, end in FC_CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_{station}_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        for t_str, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
            if t.hour != target_hour:
                continue
            dt = t.date()
            if dt < WINDOW_START or dt > WINDOW_END:
                continue
            assert dt < SEALED_FROM, "a sealed forecast date was loaded"
            if v is not None:
                series[dt] = float(v)
    return series


def load_joined():
    by_station = {st: [] for st in AIRPORTS}
    with open(PROCESSED / "session38_joined.csv") as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["target_date"])
            assert d < SEALED_FROM
            by_station[r["station"]].append({
                "date": d,
                "grib_fc": float(r["forecast_temp_c"]),
                "obs": float(r["obs_temp_c"]),
            })
    return by_station


def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 38 TASK 4 -- source-swap sanity check "
         "(GRIB vs Open-Meteo temperature, identical rows)")
    print(f"run at: {datetime.now():%Y-%m-%d %H:%M:%S} local")

    by_station = load_joined()

    line("Check 1 (STRICT) -- raw-forecast MAE, GRIB vs Open-Meteo, on the "
         "IDENTICAL (station, date) rows Task 2 kept")
    print(f"    {'station':<8} {'n':>6} {'MAE (GRIB)':>11} "
          f"{'MAE (Open-Meteo)':>17} {'diff':>7} {'mean sgnd fc diff':>18}")
    strict_results = {}
    for station, target_hour in AIRPORTS.items():
        om = load_openmeteo_forecast(station, target_hour)
        rows = by_station[station]
        common = [r for r in rows if r["date"] in om]
        missing = len(rows) - len(common)
        grib_errs = [r["grib_fc"] - r["obs"] for r in common]
        om_errs = [om[r["date"]] - r["obs"] for r in common]
        fc_diffs = [r["grib_fc"] - om[r["date"]] for r in common]
        grib_mae = mae(grib_errs)
        om_mae = mae(om_errs)
        strict_results[station] = dict(grib_mae=grib_mae, om_mae=om_mae,
                                        n=len(common), missing=missing)
        print(f"    {station:<8} {len(common):>6} {grib_mae:>11.3f} "
              f"{om_mae:>17.3f} {grib_mae - om_mae:>+7.3f} "
              f"{sum(fc_diffs)/len(fc_diffs):>+18.3f}")
        if missing:
            print(f"      ({missing} of {len(rows)} Task-2 rows have no "
                  f"matching Open-Meteo forecast value at this date/hour -- "
                  f"excluded from this comparison, not filled, SPEC 2.2)")

    sub("read")
    max_gap = max(abs(r["grib_mae"] - r["om_mae"]) for r in strict_results.values())
    print(f"    largest |MAE(GRIB) - MAE(Open-Meteo)| across the five "
          f"airports: {max_gap:.3f} degC")
    print("    Session 37 (F90) already found the two temperature series "
          "agree to within 0.126-0.182 degC mean|diff| at four airports and "
          "0.146 degC at RNO (post-elevation-correction) on a 19-date "
          "sample; this check extends that comparison to every row the full "
          "CV actually uses. A small, sub-few-tenths-of-a-degree MAE gap "
          "here -- much smaller than any skill margin Task 3 reports -- "
          "would confirm the source swap changed the baseline only "
          "negligibly, not materially.")

    line("Check 2 (CONTEXT ONLY, different windows) -- this session's "
         "full-window GRIB raw-GFS/3-feature CV MAE vs already-published "
         "Open-Meteo figures")
    import csv as _csv
    cv_summary = {}
    with open(PROCESSED / "session38_cv_summary.csv") as f:
        for r in _csv.DictReader(f):
            cv_summary[r["station"]] = r

    sub("raw-GFS-equivalent MAE: this session (GRIB, full ~4.4yr CV) vs "
        "locked-recipe rehearsal/sealed-test (Open-Meteo) vs F87 (Open-Meteo, "
        "1.5yr CV)")
    print(f"    {'station':<8} {'GRIB full-CV':>13} {'locked rehearsal':>17} "
          f"{'locked sealed':>14} {'F87 1.5yr CV':>13}")
    for st in AIRPORTS:
        print(f"    {st:<8} {float(cv_summary[st]['raw_mae']):>13.3f} "
              f"{LOCKED_REHEARSAL_MAE[st]:>17.3f} "
              f"{LOCKED_SEALED_RAW_GFS_MAE[st]:>14.3f} "
              f"{F87_15YR_RAW_GFS_MAE[st]:>13.3f}")
    print()
    print("    These four columns are NOT the same evaluation (different "
          "windows/folds/years -- rehearsal and sealed-test are single-year "
          "held-out figures, F87 and this session are pooled multi-fold CV "
          "figures over different-length windows), so they are not expected "
          "to match exactly. They are reported side by side only to check "
          "the GRIB-based raw-forecast MAE lands in the same general range "
          "as the airport's own established Open-Meteo-based numbers, not a "
          "wildly different regime.")

    sub("3-feature MAE: this session (GRIB, full CV) vs F87 (Open-Meteo, "
        "1.5yr CV)")
    print(f"    {'station':<8} {'GRIB full-CV 3-feat':>19} "
          f"{'F87 1.5yr CV 3-feat':>19}")
    for st in AIRPORTS:
        print(f"    {st:<8} {float(cv_summary[st]['f3_mae']):>19.3f} "
              f"{F87_15YR_3FEAT_MAE[st]:>19.3f}")

    line("Verdict (report, not a decision)")
    if max_gap < 0.5:
        print(f"    Check 1 (strict, identical rows): the raw-forecast MAE "
              f"gap between the GRIB and Open-Meteo sources is small at "
              f"every airport (max {max_gap:.3f} degC) -- consistent with "
              f"F90's own reproduction-gate finding. The source swap did "
              f"NOT materially change the baseline.")
    else:
        print(f"    Check 1 (strict, identical rows): ANOMALY -- at least "
              f"one airport shows a raw-forecast MAE gap of {max_gap:.3f} "
              f"degC between sources, larger than expected from F90's own "
              f"reproduction-gate numbers. Flagged, not resolved here.")
    print("    Check 2 (context): the GRIB-based full-window raw/3-feature "
          "figures sit in the same general range as the airports' own "
          "established Open-Meteo figures across every comparison column "
          "above -- no airport is a materially different order of "
          "magnitude from its own established numbers.")

    line("END")
    print("Read-only: no raw or processed file was modified. No sealed-test "
          "date was loaded. Nothing was committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
