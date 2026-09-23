"""Verification addendum to session 63 (DECISIONS F107/F108). Saves, as a
committed script, the model-free wiring check F107 described running but
did not save as a script ("a separate, read-only, model-free script (not
committed -- a scratch check, csv-only, no lightgbm import)").

This reproduces scripts/session62_reserved_confirm.py's own load_family()
and build_complete_case() logic exactly, WITHOUT importing that module --
importing it pulls in lightgbm (plus an os.execv dylib-path restart), which
this check must avoid (it fits no model and must not fit one). Instead it
re-reads session60_combine_design.CANDIDATE_FEATURES (safe, no heavy
imports) and session62_reserved_confirm.py's own RESERVED_FAMILY_FILES
paths (copied here as plain constants, not imported, since importing that
module is exactly what this script avoids), and walks the same two-file
(v16_file/sealed_file, then the new per-family reserved-year file) logic
load_family() implements, line for line.

Confirms, per DECISIONS F107:
  1. 0 reserved-year hits in the two original (v16/sealed) committed files
     per family (unchanged, per D51/F98/F100/F101/F102's own design).
  2. 1,825 rows added from the four new session63_reserved_window_with_*.csv
     files (365 dates x 5 airports), per family.
  3. Exactly 365 complete-case reserved-year rows at every airport (mirroring
     build_complete_case()'s own intersection over base/L/D/T/R).
  4. 1,226/1,226/1,225/1,225/1,225 complete-case TRAINING-window rows at
     EGLC/LFPG/DSM/YSDU/RNO, matching D58 item 5's own already-verified count.

No model is fit anywhere in this script. No MAE, skill, or CV is computed.
lightgbm is never imported.
"""

import csv
import sys
import time
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
NOTES = ROOT / "notes"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session48_reserved_year import RESERVED_YEAR_START, RESERVED_YEAR_END  # noqa: E402
from session60_combine_design import CANDIDATE_FEATURES  # noqa: E402

AIRPORTS = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20}
FINAL_CODES = ["D", "L", "R", "T"]

FAMILY_COLUMNS = {
    "L": ["lapse_rate_t2_t850"],
    "D": ["dewpoint_depression_t2m"],
    "T": ["pressure_tendency_3h_hpa"],
    "R": ["dswrf_2h_wm2"],
}

# Copied verbatim from scripts/session62_reserved_confirm.py's own
# module-level RESERVED_FAMILY_FILES -- not imported (see module docstring:
# importing that module pulls in lightgbm).
RESERVED_FAMILY_FILES = {
    "L": PROCESSED / "session63_reserved_window_with_upper_air.csv",
    "D": PROCESSED / "session63_reserved_window_with_moisture.csv",
    "T": PROCESSED / "session63_reserved_window_with_pressure.csv",
    "R": PROCESSED / "session63_reserved_window_with_radiation.csv",
}

B_ONLY_PATHS = [
    PROCESSED / "grib_features_v16_window.csv",
    PROCESSED / "grib_features_sealed_window.csv",
]

CONFIRMATION_FOLD_TRAIN = (date(2021, 3, 24), date(2024, 7, 31))

OUT_LOG = NOTES / "session63-wiring-scratch-check-output.txt"


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


# ------------------------------------------------------------------ load_family(), reproduced

def load_family(short_name, extra_cols):
    """Line-for-line reproduction of scripts/session62_reserved_confirm.py's
    own load_family(): reads CANDIDATE_FEATURES[code]'s v16_file/sealed_file
    (counting, not loading, any reserved-year row found there -- expect 0),
    then loads the matching RESERVED_FAMILY_FILES entry if present (every
    row there must be inside the reserved year, or this raises). Returns
    (station -> {date: {col: value}}, reserved_year_hits_in_original_files,
    rows_added_from_the_new_reserved_file)."""
    spec = CANDIDATE_FEATURES[short_name]
    out = {st: {} for st in AIRPORTS}
    reserved_hits = 0
    n_original_rows = 0
    for path in (spec["v16_file"], spec["sealed_file"]):
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                n_original_rows += 1
                d = date.fromisoformat(r["target_date"])
                if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                    reserved_hits += 1
                    continue
                row = {}
                for c in extra_cols:
                    row[c] = float(r[c])
                out[st][d] = row

    n_added_from_reserved_file = 0
    reserved_path = RESERVED_FAMILY_FILES.get(short_name)
    if reserved_path is not None and reserved_path.exists():
        with open(reserved_path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                if not (RESERVED_YEAR_START <= d <= RESERVED_YEAR_END):
                    raise AssertionError(
                        f"session63 reserved-year file {reserved_path.name} "
                        f"contains an out-of-range date {d} for station {st} "
                        f"-- refusing to proceed.")
                row = {}
                for c in extra_cols:
                    row[c] = float(r[c])
                out[st][d] = row
                n_added_from_reserved_file += 1
    return out, reserved_hits, n_original_rows, n_added_from_reserved_file


def load_base_unfiltered():
    """Line-for-line reproduction of session62_reserved_confirm.py's own
    load_base_unfiltered(): station -> {date: {'fc','cloud','wind'}} from the
    pre-D51 base 5-feature files, unfiltered by date."""
    out = {st: {} for st in AIRPORTS}
    for path in B_ONLY_PATHS:
        with open(path) as f:
            for r in csv.DictReader(f):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                out[st][d] = {
                    "fc": float(r["temperature_grib_c"]),
                    "cloud": float(r["cloud_cover_grib_pct"]),
                    "wind": float(r["wind_speed_grib_kmh"]),
                }
    return out


def complete_case_dates(base_all, l_all, d_all, t_all, r_all, station):
    """Mirrors build_complete_case()'s own per-station intersection (over
    base/L/D/T/R date sets) -- returns the set of dates common to all five,
    for one station. No model row is built; this is date-set arithmetic
    only, the same shape build_complete_case() uses before it assembles any
    feature vector."""
    return (set(base_all[station]) & set(l_all[station]) & set(d_all[station])
            & set(t_all[station]) & set(r_all[station]))


def main():
    tee = Tee(OUT_LOG)
    sys.stdout = tee

    line("SESSION 63 VERIFICATION ADDENDUM -- wiring scratch check (F107/F108). "
         "Reproduces scripts/session62_reserved_confirm.py's own load_family() "
         "and build_complete_case() logic without importing that module (avoids "
         "lightgbm entirely). No model is fit anywhere in this script.")
    print(f"run at: {time.strftime('%Y-%m-%d %H:%M:%S')} local")
    print("lightgbm imported by this script: NO (checked: 'lightgbm' not in sys.modules "
          f"after all imports above -- {'lightgbm' not in sys.modules})")

    line("Per-family load_family() reproduction")
    all_families = {}
    for code in FINAL_CODES:
        out, hits, n_original, n_added = load_family(code, FAMILY_COLUMNS[code])
        all_families[code] = out
        sub(f"family {code}")
        print(f"    original files (v16_file + sealed_file): {n_original} rows read, "
              f"{hits} reserved-year hits (expect 0, unchanged)")
        print(f"    reserved-year file ({RESERVED_FAMILY_FILES[code].name}): "
              f"{n_added} rows added (expect 1825 = 365 dates x 5 airports)")
        per_airport_reserved = {
            st: sum(1 for d in out[st] if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END)
            for st in AIRPORTS
        }
        for st in AIRPORTS:
            print(f"      {st:<6} reserved-year rows now loaded: {per_airport_reserved[st]} (expect 365)")

    line("Base (B) load -- unfiltered, already carries the reserved year (pre-D51 file)")
    base_all = load_base_unfiltered()
    for st in AIRPORTS:
        n_reserved = sum(1 for d in base_all[st] if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END)
        print(f"    {st:<6} base reserved-year rows: {n_reserved} (expect 365)")

    line("Complete-case row counts -- RESERVED-YEAR test window "
         f"({RESERVED_YEAR_START}..{RESERVED_YEAR_END})")
    for st in AIRPORTS:
        common = complete_case_dates(base_all, all_families["L"], all_families["D"],
                                      all_families["T"], all_families["R"], st)
        n_reserved_complete = sum(1 for d in common if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END)
        print(f"    {st:<6} complete-case reserved-year rows: {n_reserved_complete} "
              f"(D58 item 11's own blocker: this was 0 before session 63's build; expect 365 now)")

    line("Complete-case row counts -- TRAINING window "
         f"({CONFIRMATION_FOLD_TRAIN[0]}..{CONFIRMATION_FOLD_TRAIN[1]}), cross-check "
         "against D58 item 5's own already-verified count")
    tr_s, tr_e = CONFIRMATION_FOLD_TRAIN
    expected = {"EGLC": 1226, "LFPG": 1226, "DSM": 1225, "YSDU": 1225, "RNO": 1225}
    all_match = True
    for st in AIRPORTS:
        common = complete_case_dates(base_all, all_families["L"], all_families["D"],
                                      all_families["T"], all_families["R"], st)
        n_train = sum(1 for d in common if tr_s <= d <= tr_e)
        match = "MATCH" if n_train == expected[st] else "MISMATCH"
        all_match = all_match and (n_train == expected[st])
        print(f"    {st:<6} complete-case training-window rows: {n_train} "
              f"(D58 item 5 expects {expected[st]}) -- {match}")

    line("END")
    print(f"Training-window row counts vs D58 item 5: {'ALL MATCH' if all_match else 'MISMATCH -- investigate'}")
    print("No model was fit. No MAE, skill, or CV was computed. lightgbm was never")
    print("imported. This script only counts rows and dates.")
    print(f"\nThis output is saved at {OUT_LOG}")

    sys.stdout = sys.__stdout__
    tee.flush()
    return all_match


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
