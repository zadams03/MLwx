"""Session 60: pre-registers the combine-phase feature-selection sweep
(DECISIONS D57), before it is run (session 61). This module is the frozen
spec-in-code session 61 must import -- it defines the candidate features,
the variant ladder, and the pre-registered thresholds, and runs a
HEADER-ONLY pre-flight check confirming every source file and column
exists. It fits no model, loads no data rows, and computes no MAE.

Reuses, does not redefine, session 48's fold list and reserved-year guard
(scripts/session48_reserved_year.py): EXPERIMENT_FOLDS, RESERVED_YEAR_START,
RESERVED_YEAR_END, assert_reserved_year_excluded.

One known wrinkle, flagged here rather than hidden (see the session-60
report to the owner): the E2 (moisture) family's adopted feature,
`dewpoint_depression_t2m_floored` (D53), is NOT itself a stored column in
either committed moisture file. D53/F100 (session 52) computed it as an
in-memory floor of the stored `dewpoint_depression_t2m` column
(`floored = max(dewpoint_depression_t2m, 0)`, changing exactly 1 of 7,952
rows) and explicitly kept the original column intact on disk ("the
original column is kept intact; the floor applies only in the feature
matrix"). So CANDIDATE_FEATURES['D'] below names the stored raw column
plus the exact, already-frozen one-line transform session 61 must apply --
this is not a re-derivation from GRIB, just reapplying D53's own pinned
formula, but it is a real gap between "committed column" and "adopted
feature name" worth naming explicitly rather than assuming a column that
does not exist. No other candidate feature has this wrinkle -- L, T, R, P,
rh and plev are all stored verbatim under the exact names below.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session48_reserved_year import (  # noqa: E402
    RESERVED_YEAR_START,
    RESERVED_YEAR_END,
    EXPERIMENT_FOLDS,
    assert_reserved_year_excluded,
)

# ------------------------------------------------------------------ candidate features
#
# Each entry names the two committed files a fold may need (train rows can
# fall in the v16 window; the 2025-26-truncated fold's test rows fall in the
# sealed window, F94's own window) and the exact column(s) already built and
# committed by the E1-E5 build sessions. Nothing here is rebuilt, re-decoded,
# or re-derived from raw GRIB -- see the module docstring for the one named
# exception (D's floor transform, applied to an already-committed column).

CANDIDATE_FEATURES = {
    "L": {
        "decision": "D52 (adopted)",
        "v16_file": PROCESSED / "session49_v16_window_with_upper_air.csv",
        "sealed_file": PROCESSED / "session49_sealed_window_with_upper_air.csv",
        "columns": ["lapse_rate_t2_t850"],
        "transform": None,
    },
    "D": {
        "decision": "D53 (adopted)",
        "v16_file": PROCESSED / "session51_v16_window_with_moisture.csv",
        "sealed_file": PROCESSED / "session51_sealed_window_with_moisture.csv",
        "columns": ["dewpoint_depression_t2m"],
        "transform": (
            "dewpoint_depression_t2m_floored = max(dewpoint_depression_t2m, 0) "
            "-- D53/F100's own frozen formula. The floored column is NOT "
            "stored on disk; apply this exact one-line floor to the stored "
            "raw column, nothing else."
        ),
    },
    "T": {
        "decision": "D54 (adopted)",
        "v16_file": PROCESSED / "session53_v16_window_with_pressure.csv",
        "sealed_file": PROCESSED / "session53_sealed_window_with_pressure.csv",
        "columns": ["pressure_tendency_3h_hpa"],
        "transform": None,
    },
    "R": {
        "decision": "D55 (adopted)",
        "v16_file": PROCESSED / "session55_v16_window_with_radiation.csv",
        "sealed_file": PROCESSED / "session55_sealed_window_with_radiation.csv",
        "columns": ["dswrf_2h_wm2"],
        "transform": None,
    },
    "P": {
        "decision": "D56 (adopted)",
        "v16_file": PROCESSED / "session57_v16_window_with_precip.csv",
        "sealed_file": PROCESSED / "session57_sealed_window_with_precip.csv",
        "columns": ["precip_rate_mmh"],
        "transform": None,
    },
    "rh": {
        "decision": "D53 (parked)",
        "v16_file": PROCESSED / "session51_v16_window_with_moisture.csv",
        "sealed_file": PROCESSED / "session51_sealed_window_with_moisture.csv",
        "columns": ["relative_humidity_2m"],
        "transform": None,
    },
    "plev": {
        "decision": "D52 (parked)",
        "v16_file": PROCESSED / "session49_v16_window_with_upper_air.csv",
        "sealed_file": PROCESSED / "session49_sealed_window_with_upper_air.csv",
        "columns": ["t850", "t925", "t700"],
        "transform": None,
    },
}

# ------------------------------------------------------------------ the variant ladder (D57)
#
# Exactly 14 variants, no more, no fewer. feature_set is given as short
# names layered on top of frozen baseline B (SPEC section 7).

VARIANT_LADDER = [
    ("B", []),
    ("B+L", ["L"]),
    ("B+D", ["D"]),
    ("B+T", ["T"]),
    ("B+R", ["R"]),
    ("B+P", ["P"]),
    ("B+LDTRP", ["L", "D", "T", "R", "P"]),
    ("B+DTRP", ["D", "T", "R", "P"]),
    ("B+LTRP", ["L", "T", "R", "P"]),
    ("B+LDRP", ["L", "D", "R", "P"]),
    ("B+LDTP", ["L", "D", "T", "P"]),
    ("B+LDTR", ["L", "D", "T", "R"]),
    ("B+LDTRP+rh", ["L", "D", "T", "R", "P", "rh"]),
    ("B+LDTRP+plev", ["L", "D", "T", "R", "P", "plev"]),
]

assert len(VARIANT_LADDER) == 14, f"expected 14 variants, got {len(VARIANT_LADDER)}"

# ------------------------------------------------------------------ pre-registered constants (D57)

TAU_SKILL = 0.004  # minimum practical skill change (0.4%), fold-averaged, for "clearly worse/better"
ROW_COST_GUARD_FRAC = 0.05  # complete-case row-cost guard, vs a B-only mask
DROP_ORDER = ["T", "P", "R", "L", "D"]  # weakest-adopted-family first; backward-elimination tie-break


# ------------------------------------------------------------------ header-only pre-flight

def _read_header(path):
    with open(path, "r", newline="") as f:
        first_line = f.readline()
    return [c.strip() for c in first_line.rstrip("\n").rstrip("\r").split(",")]


def preflight():
    """Confirms every CANDIDATE_FEATURES source file exists and contains its
    named column(s). Reads ONLY the header line of each file (zero data
    rows) -- loads no data, fits nothing. Raises with a clear message on
    any missing file or column; otherwise prints a pass table."""
    header_cache = {}
    rows = []
    problems = []

    for short_name, spec in CANDIDATE_FEATURES.items():
        for file_key in ("v16_file", "sealed_file"):
            path = spec[file_key]
            if path not in header_cache:
                header_cache[path] = _read_header(path) if path.exists() else None
            header = header_cache[path]
            for col in spec["columns"]:
                present = header is not None and col in header
                rows.append((short_name, file_key, path.name, col, present))
                if not present:
                    reason = "file missing" if header is None else "column missing"
                    problems.append(
                        f"{short_name} / {file_key}: {reason} -- {path} :: {col}")

    print("=" * 90)
    print("SESSION 60 -- combine-phase manifest header-only pre-flight.")
    print("Reads column headers ONLY (zero data rows). Loads no data. Fits nothing.")
    print("=" * 90)
    print(f"\n{'feature':<8}{'file_key':<12}{'file':<48}{'column':<28}{'present'}")
    for short_name, file_key, fname, col, present in rows:
        print(f"{short_name:<8}{file_key:<12}{fname:<48}{col:<28}{present}")

    if problems:
        print("\nPRE-FLIGHT FAILED -- missing file(s) or column(s):")
        for p in problems:
            print(f"    {p}")
        raise RuntimeError(
            "session60_combine_design pre-flight failed -- see problems above")

    print(f"\nAll {len(rows)} (feature, file, column) checks PASS.")
    print(f"\nCANDIDATE_FEATURES keys: {sorted(CANDIDATE_FEATURES.keys())}")
    print(f"VARIANT_LADDER: {len(VARIANT_LADDER)} variants "
          f"(expected 14) -- {'PASS' if len(VARIANT_LADDER) == 14 else 'FAIL'}")
    for name, feats in VARIANT_LADDER:
        print(f"    {name:<16} = B + {feats}")
    print(f"\nTAU_SKILL = {TAU_SKILL}")
    print(f"ROW_COST_GUARD_FRAC = {ROW_COST_GUARD_FRAC}")
    print(f"DROP_ORDER = {DROP_ORDER}")
    print(f"\nRESERVED_YEAR = {RESERVED_YEAR_START} .. {RESERVED_YEAR_END} "
          f"(imported from session48_reserved_year, not redefined)")
    print(f"EXPERIMENT_FOLDS labels = {[label for label, *_ in EXPERIMENT_FOLDS]} "
          f"(imported from session48_reserved_year, not redefined)")

    print("\n-- Reserved-year guard, re-checked against EXPERIMENT_FOLDS "
          "(date arithmetic only, same check D51 itself ran) --")
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e}  test={te_s}..{te_e}  "
              f"-- PASS (guard did not raise)")

    print("\nKnown wrinkle (see module docstring): CANDIDATE_FEATURES['D']'s "
          "column is the stored raw 'dewpoint_depression_t2m'; the adopted "
          "feature 'dewpoint_depression_t2m_floored' (D53) requires applying "
          "the frozen one-line floor transform noted above -- it is not "
          "itself a stored column, by design (F100).")

    print("\n" + "=" * 90)
    print("END -- pre-flight only. No data row was read. No model was fit.")
    print("=" * 90)


def main():
    preflight()


if __name__ == "__main__":
    main()
