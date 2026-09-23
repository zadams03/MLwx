"""Verification addendum to session 63 (DECISIONS F107) -- closes with
finding F108. NOT a new session: no model fit, no reserved-year scoring, no
change to any prior finding or verdict.

Session 63's own module docstring (scripts/session63_reserved_year_build.py)
states its four join_* functions (join_L, join_D, join_T, join_R) were
"copied verbatim" from each family's own already-frozen build_joined()
(sessions 49/51/53/55) -- not imported. This script proves that copy is
exact, empirically, by feeding session 63's OWN join_* functions the raw
decoded input columns already stored in each family's committed v16_window
file, and comparing the recomputed derived column against that same file's
own already-committed derived column.

Task 1/2 -- per family (L, D, T, R), every row of the committed v16_window
file is used (no sample needed, no new GRIB pull needed -- the input columns
this check needs are already on disk, so Task 2's new-pull fallback is not
triggered). Session 63's actual join_L/join_D/join_T/join_R functions are
called directly (imported from scripts/session63_reserved_year_build.py,
not re-typed) so this is a literal execution of the same code session 63
used, not a hand copy of the formula. To avoid touching any committed file,
the module-level PROCESSED path those functions write their output CSV to
is temporarily redirected to a scratch directory for the duration of each
call, then restored -- the four session63_reserved_window_with_*.csv files
already on disk (session 63's own real output) are never opened for
writing by this script.

Task 3 -- on the new reserved-year moisture file
(data/processed/session63_reserved_window_with_moisture.csv), checks
dewpoint_depression_t2m == round(t2m_raw - dew_point_2m, 3) on every row.

Expect a max abs diff of exactly 0 everywhere. If any diff is nonzero, this
script reports it and stops -- it does not fix, adjust, or reinterpret
anything (per the session prompt).
"""

import csv
import shutil
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
NOTES = ROOT / "notes"

sys.path.insert(0, str(Path(__file__).resolve().parent))

import session63_reserved_year_build as s63  # noqa: E402
import session49_upper_air_pull as s49       # noqa: E402
import session51_moisture_pull as s51        # noqa: E402
import session53_pressure_pull as s53        # noqa: E402
import session55_radiation_pull as s55       # noqa: E402

AIRPORTS = ["EGLC", "LFPG", "DSM", "YSDU", "RNO"]

OUT_LOG = NOTES / "session63-join-equivalence-check-output.txt"


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
    print("=" * 90)
    print(title)
    print("=" * 90)


def sub(title):
    print()
    print(f"-- {title} --")


def run_join_in_scratch(join_fn, *args):
    """Calls one of session63_reserved_year_build.py's own join_* functions
    with s63.PROCESSED temporarily redirected to a scratch directory, so the
    real committed session63_reserved_window_with_*.csv files are never
    opened for writing. Returns the rows it wrote, read back from scratch."""
    real_processed = s63.PROCESSED
    with tempfile.TemporaryDirectory() as tmp:
        s63.PROCESSED = Path(tmp)
        try:
            out_csv, before, after, drops = join_fn(*args)
            rows = list(csv.DictReader(open(out_csv)))
        finally:
            s63.PROCESSED = real_processed
    return rows, before, after, drops


# ------------------------------------------------------------------ Task 1/2: L

def check_L():
    sub("family L (upper-air) -- source: session49_v16_window_with_upper_air.csv")
    src = PROCESSED / "session49_v16_window_with_upper_air.csv"
    rows = list(csv.DictReader(open(src)))
    print(f"    input rows (every row of the committed file, no sampling): {len(rows)}")

    per_station, decoded = {}, {}
    for row in rows:
        st, d = row["station"], date.fromisoformat(row["target_date"])
        per_station.setdefault(st, {})[d] = row
        decoded.setdefault(st, {})[d] = {
            "t925": float(row["t925"]),
            "t850": float(row["t850"]),
            "t700": float(row["t700"]),
        }
    elev_corr = s49.load_elevation_corrections()

    out_rows, before, after, drops = run_join_in_scratch(s63.join_L, per_station, decoded, elev_corr)
    print(f"    join drops while re-running: {len(drops)} (expect 0)")
    assert sum(before.values()) == sum(after.values()) == len(rows), "row count changed -- investigate"

    committed = {(r["station"], r["target_date"]): r for r in rows}
    max_diff = {c: 0.0 for c in ("t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850")}
    per_airport_max = {st: 0.0 for st in AIRPORTS}
    n_checked = 0
    for r in out_rows:
        key = (r["station"], r["target_date"])
        c = committed[key]
        n_checked += 1
        for col in max_diff:
            diff = abs(float(r[col]) - float(c[col]))
            max_diff[col] = max(max_diff[col], diff)
            if col == "lapse_rate_t2_t850":
                per_airport_max[r["station"]] = max(per_airport_max[r["station"]], diff)
    print(f"    rows compared: {n_checked}")
    for col, v in max_diff.items():
        print(f"      max_abs_diff {col:<20} = {v:.9f}")
    print(f"    max_abs_diff lapse_rate_t2_t850, per airport (this is the family's own "
          f"derived column the task asks about):")
    for st in AIRPORTS:
        print(f"      {st:<6} max_abs_diff = {per_airport_max[st]:.9f}")
    return per_airport_max, max_diff["lapse_rate_t2_t850"]


# ------------------------------------------------------------------ Task 1/2: D

def check_D():
    sub("family D (moisture) -- source: session51_v16_window_with_moisture.csv")
    src = PROCESSED / "session51_v16_window_with_moisture.csv"
    rows = list(csv.DictReader(open(src)))
    print(f"    input rows (every row of the committed file, no sampling): {len(rows)}")

    per_station, decoded = {}, {}
    for row in rows:
        st, d = row["station"], date.fromisoformat(row["target_date"])
        per_station.setdefault(st, {})[d] = row
        decoded.setdefault(st, {})[d] = {
            "relative_humidity_2m": float(row["relative_humidity_2m"]),
            "dew_point_2m": float(row["dew_point_2m"]),
            "specific_humidity_2m": float(row["specific_humidity_2m"]),
        }
    elev_corr = s51.load_elevation_corrections()

    out_rows, before, after, drops = run_join_in_scratch(s63.join_D, per_station, decoded, elev_corr)
    print(f"    join drops while re-running: {len(drops)} (expect 0)")
    assert sum(before.values()) == sum(after.values()) == len(rows), "row count changed -- investigate"

    committed = {(r["station"], r["target_date"]): r for r in rows}
    cols = ["t2m_raw", "relative_humidity_2m", "dew_point_2m", "specific_humidity_2m",
            "dewpoint_depression_t2m"]
    max_diff = {c: 0.0 for c in cols}
    per_airport_max = {st: 0.0 for st in AIRPORTS}
    n_checked = 0
    for r in out_rows:
        key = (r["station"], r["target_date"])
        c = committed[key]
        n_checked += 1
        for col in cols:
            diff = abs(float(r[col]) - float(c[col]))
            max_diff[col] = max(max_diff[col], diff)
            if col == "dewpoint_depression_t2m":
                per_airport_max[r["station"]] = max(per_airport_max[r["station"]], diff)
    print(f"    rows compared: {n_checked}")
    for col, v in max_diff.items():
        print(f"      max_abs_diff {col:<24} = {v:.9f}")
    print(f"    max_abs_diff dewpoint_depression_t2m, per airport:")
    for st in AIRPORTS:
        print(f"      {st:<6} max_abs_diff = {per_airport_max[st]:.9f}")
    return per_airport_max, max_diff["dewpoint_depression_t2m"]


# ------------------------------------------------------------------ Task 1/2: T

def check_T():
    sub("family T (pressure) -- source: session53_v16_window_with_pressure.csv")
    src = PROCESSED / "session53_v16_window_with_pressure.csv"
    rows = list(csv.DictReader(open(src)))
    print(f"    input rows (every row of the committed file, no sampling): {len(rows)}")
    print("    NOTE: join_T's own dec[...] fields are in Pa (raw GRIB units); the")
    print("    committed file stores hPa (already /100, already rounded to 3dp).")
    print("    Reconstructed as Pa = hpa_stored * 100.0 -- an exact, invertible")
    print("    round-trip at 3-decimal-place precision, not a re-decode.")

    per_station, decoded = {}, {}
    for row in rows:
        st, d = row["station"], date.fromisoformat(row["target_date"])
        per_station.setdefault(st, {})[d] = row
        decoded.setdefault(st, {})[d] = {
            "pressure_msl_hpa": float(row["pressure_msl_hpa"]) * 100.0,
            "pressure_surface_hpa": float(row["pressure_surface_hpa"]) * 100.0,
            "pressure_msl_lead_minus3_hpa": float(row["pressure_msl_lead_minus3_hpa"]) * 100.0,
        }

    out_rows, before, after, drops = run_join_in_scratch(s63.join_T, per_station, decoded)
    print(f"    join drops while re-running: {len(drops)} (expect 0)")
    assert sum(before.values()) == sum(after.values()) == len(rows), "row count changed -- investigate"

    committed = {(r["station"], r["target_date"]): r for r in rows}
    cols = ["pressure_msl_hpa", "pressure_surface_hpa", "pressure_msl_lead_minus3_hpa",
            "pressure_tendency_3h_hpa"]
    max_diff = {c: 0.0 for c in cols}
    per_airport_max = {st: 0.0 for st in AIRPORTS}
    n_checked = 0
    for r in out_rows:
        key = (r["station"], r["target_date"])
        c = committed[key]
        n_checked += 1
        for col in cols:
            diff = abs(float(r[col]) - float(c[col]))
            max_diff[col] = max(max_diff[col], diff)
            if col == "pressure_tendency_3h_hpa":
                per_airport_max[r["station"]] = max(per_airport_max[r["station"]], diff)
    print(f"    rows compared: {n_checked}")
    for col, v in max_diff.items():
        print(f"      max_abs_diff {col:<28} = {v:.9f}")
    print(f"    max_abs_diff pressure_tendency_3h_hpa, per airport:")
    for st in AIRPORTS:
        print(f"      {st:<6} max_abs_diff = {per_airport_max[st]:.9f}")
    return per_airport_max, max_diff["pressure_tendency_3h_hpa"]


# ------------------------------------------------------------------ Task 1/2: R

def check_R():
    sub("family R (radiation) -- source: session55_v16_window_with_radiation.csv")
    src = PROCESSED / "session55_v16_window_with_radiation.csv"
    rows = list(csv.DictReader(open(src)))
    print(f"    input rows (every row of the committed file, no sampling): {len(rows)}")

    per_station, decoded = {}, {}
    for row in rows:
        st, d = row["station"], date.fromisoformat(row["target_date"])
        per_station.setdefault(st, {})[d] = row
        entry = {"to_lead": float(row["dswrf_ave_to_lead_wm2"])}
        m2 = row["dswrf_ave_to_lead_minus2_wm2"]
        if m2 not in ("", None):
            entry["to_lead_minus2"] = float(m2)
        decoded.setdefault(st, {})[d] = entry

    out_rows, before, after, drops = run_join_in_scratch(s63.join_R, per_station, decoded)
    print(f"    join drops while re-running: {len(drops)} (expect 0)")
    assert sum(before.values()) == sum(after.values()) == len(rows), "row count changed -- investigate"

    committed = {(r["station"], r["target_date"]): r for r in rows}
    main_cols = ("dswrf_ave_to_lead_wm2", "dswrf_2h_wm2")
    max_diff = {c: 0.0 for c in main_cols}
    max_diff["dswrf_ave_to_lead_minus2_wm2"] = 0.0
    per_airport_max = {st: 0.0 for st in AIRPORTS}
    n_checked = 0
    for r in out_rows:
        key = (r["station"], r["target_date"])
        c = committed[key]
        n_checked += 1
        for col in main_cols:
            diff = abs(float(r[col]) - float(c[col]))
            max_diff[col] = max(max_diff[col], diff)
            if col == "dswrf_2h_wm2":
                per_airport_max[r["station"]] = max(per_airport_max[r["station"]], diff)
        # dswrf_ave_to_lead_minus2_wm2 is blank at YSDU/RNO by construction (F102) --
        # compare only where both sides carry a value.
        rv = r["dswrf_ave_to_lead_minus2_wm2"]
        cv = c["dswrf_ave_to_lead_minus2_wm2"]
        if (rv in ("", None)) != (cv in ("", None)):
            raise AssertionError(f"blank/non-blank mismatch at {key}: {rv!r} vs {cv!r}")
        if rv not in ("", None):
            diff = abs(float(rv) - float(cv))
            max_diff["dswrf_ave_to_lead_minus2_wm2"] = max(max_diff["dswrf_ave_to_lead_minus2_wm2"], diff)
    print(f"    rows compared: {n_checked}")
    for col, v in max_diff.items():
        print(f"      max_abs_diff {col:<26} = {v:.9f}")
    print(f"    max_abs_diff dswrf_2h_wm2, per airport:")
    for st in AIRPORTS:
        print(f"      {st:<6} max_abs_diff = {per_airport_max[st]:.9f}")
    return per_airport_max, max_diff["dswrf_2h_wm2"]


# ------------------------------------------------------------------ Task 3

def check_reserved_moisture_arithmetic():
    line("TASK 3 -- reserved-year moisture file: dewpoint_depression_t2m == "
         "round(t2m_raw - dew_point_2m, 3) on every row")
    path = PROCESSED / "session63_reserved_window_with_moisture.csv"
    rows = list(csv.DictReader(open(path)))
    print(f"    file: {path.name}  rows: {len(rows)}")

    per_airport_max = {st: 0.0 for st in AIRPORTS}
    n_violations = 0
    for r in rows:
        expected = round(float(r["t2m_raw"]) - float(r["dew_point_2m"]), 3)
        actual = float(r["dewpoint_depression_t2m"])
        diff = abs(actual - expected)
        per_airport_max[r["station"]] = max(per_airport_max[r["station"]], diff)
        if diff != 0.0:
            n_violations += 1
    print(f"    rows checked: {len(rows)}   violations (diff != 0): {n_violations}")
    for st in AIRPORTS:
        print(f"      {st:<6} max_abs_diff = {per_airport_max[st]:.9f}")
    return per_airport_max


def main():
    tee = Tee(OUT_LOG)
    sys.stdout = tee

    line("SESSION 63 VERIFICATION ADDENDUM -- join/derive arithmetic equivalence "
         "check (see F108, not a new session; addendum to F107). No model fit, "
         "no reserved-year scoring, no change to any prior finding.")
    print(f"run at: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')} local")

    line("TASK 1/2 -- per family, feed session 63's own join_* function the raw "
         "decoded input columns already stored in that family's committed "
         "v16_window file, and compare its derived output to the committed "
         "derived column. Every row is used (no new pull needed, so Task 2's "
         "fallback -- a 5-non-reserved-training-date re-run -- is not triggered).")

    all_per_airport = {}
    l_air, l_overall = check_L()
    d_air, d_overall = check_D()
    t_air, t_overall = check_T()
    r_air, r_overall = check_R()
    all_per_airport["L"] = l_air
    all_per_airport["D"] = d_air
    all_per_airport["T"] = t_air
    all_per_airport["R"] = r_air

    line("SUMMARY TABLE -- max abs diff per family per airport (own derived column)")
    header = f"{'family':<8}" + "".join(f"{st:<12}" for st in AIRPORTS) + f"{'overall':<12}"
    print(header)
    overalls = {"L": l_overall, "D": d_overall, "T": t_overall, "R": r_overall}
    for fam in ("L", "D", "T", "R"):
        row = f"{fam:<8}" + "".join(f"{all_per_airport[fam][st]:<12.9f}" for st in AIRPORTS) + f"{overalls[fam]:<12.9f}"
        print(row)

    all_zero = all(v == 0.0 for fam in all_per_airport.values() for v in fam.values())
    print(f"\n    {'PASS -- every max abs diff is exactly 0' if all_zero else 'NONZERO DIFF FOUND -- see above, STOP (per session prompt: report, do not fix)'}")

    d_moist = check_reserved_moisture_arithmetic()
    moist_zero = all(v == 0.0 for v in d_moist.values())
    print(f"\n    {'PASS -- every max abs diff is exactly 0' if moist_zero else 'NONZERO DIFF FOUND -- see above, STOP (per session prompt: report, do not fix)'}")

    line("END")
    print("No model was fit. No reserved-year row was scored, fit on, or selected")
    print("on. This script only recomputes already-frozen, already-pinned")
    print("arithmetic and compares it to already-committed values. Nothing")
    print("committed by session 49/51/53/55/63 was modified -- all join_*")
    print("re-runs above wrote to a temporary scratch directory, never to")
    print("data/processed/session63_reserved_window_with_*.csv.")
    print(f"\nThis output is saved at {OUT_LOG}")

    sys.stdout = sys.__stdout__
    tee.flush()

    return all_zero and moist_zero


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
