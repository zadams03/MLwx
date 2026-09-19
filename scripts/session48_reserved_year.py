"""Session 48: reserves 2024-08-01..2025-07-31 as the untouched confirmation
year for the upcoming feature-selection programme, and enforces the
reservation in code (DECISIONS D51).

This module is SETUP ONLY. It fits no model, pulls no data, and computes no
result on 2024-25 or on any other year. It exists to be imported by a LATER
feature-experiment session, which must build its own folds from
EXPERIMENT_FOLDS below (or pass its own fold dates through
assert_reserved_year_excluded()) rather than re-deriving the F96 rolling-
origin fold list from scratch and risking the reserved year slipping back
in.

Why a year had to be carved out at all (DECISIONS F96, D51): F96's own
rolling-origin backtest already used every year 2022-2026 descriptively (as
training data, test data, or both) for the existing frozen recipes. That
backtest was legitimate because it tuned nothing. A feature-selection
programme is different -- it *chooses* between feature sets on the basis of
held-out performance, which is a form of fitting to data. Without a fresh,
never-touched year, any "winner" chosen from F96's own years would be
chosen in the light of data already seen, the same leakage-by-selection
problem the sealed test (SPEC 5.3, D22) exists to prevent for the final
recipe. 2024-25 is reserved for exactly that role, distinct from and
without disturbing the 2025-26 sealed year (F94).

The rule (D51): no feature experiment (train or test, any feature set) may
touch 2024-08-01..2025-07-31 until a single, pre-chosen final feature set is
confirmed on it once, at the end of the programme, and that result stands
as reported -- the same one-look discipline as every other frozen-bar test
in this project (D21, D31, D35, D39, D44, D48.13).
"""

from datetime import date, timedelta

# ------------------------------------------------------------------ the reservation

RESERVED_YEAR_START = date(2024, 8, 1)
RESERVED_YEAR_END = date(2025, 7, 31)

# For reference only -- the other years already in play elsewhere in the
# project. Not used by the guard; the guard checks only against the
# reserved year, by design (SPEC 4.3's own training/sealed windows are a
# separate, already-frozen boundary this module does not re-police).
SEALED_YEAR_START = date(2025, 8, 1)   # SPEC 4.3, D13 -- untouched, F94
SEALED_YEAR_END = date(2026, 7, 31)
V16_FLOOR = date(2021, 3, 24)          # D48.7


def _ranges_overlap(a_start, a_end, b_start, b_end):
    return a_start <= b_end and b_start <= a_end


def assert_reserved_year_excluded(fold_label, train_start, train_end,
                                   test_start, test_end):
    """Raises ValueError if either the training window or the test window
    of a proposed feature-experiment fold touches any part of the reserved
    2024-25 confirmation year. Call this on every fold BEFORE it is used
    for anything -- fitting, scoring, or even loading rows -- the same
    "stop rather than allow" discipline as the sealed-test self-guards
    (e.g. D48.8/F93). Checks are inclusive on both ends."""
    if _ranges_overlap(train_start, train_end,
                        RESERVED_YEAR_START, RESERVED_YEAR_END):
        raise ValueError(
            f"{fold_label}: training window {train_start}..{train_end} "
            f"overlaps the reserved confirmation year "
            f"{RESERVED_YEAR_START}..{RESERVED_YEAR_END} -- refusing (D51).")
    if _ranges_overlap(test_start, test_end,
                        RESERVED_YEAR_START, RESERVED_YEAR_END):
        raise ValueError(
            f"{fold_label}: test window {test_start}..{test_end} "
            f"overlaps the reserved confirmation year "
            f"{RESERVED_YEAR_START}..{RESERVED_YEAR_END} -- refusing (D51).")


# ------------------------------------------------------------------ the experiment folds

# F96's own rolling-origin fold list, MINUS the fold that tests 2024-25,
# and with the fold that tests 2025-26 truncated so its training window
# stops before the reserved year starts -- so the reserved year never
# enters any experiment's training pool either, per the session-48 prompt.
# A future feature-experiment session should build its folds from this
# list (for either a 3-feature-style or any other feature set -- these are
# date windows only, not tied to a specific feature count).
#
#   (label, train_start, train_end, test_start, test_end)
EXPERIMENT_FOLDS = [
    ("2022-23", V16_FLOOR, date(2022, 7, 31), date(2022, 8, 1), date(2023, 7, 31)),
    ("2023-24", V16_FLOOR, date(2023, 7, 31), date(2023, 8, 1), date(2024, 7, 31)),
    # Truncated vs. F96's own "2025-26" fold (which trained through
    # 2025-07-31, running straight through the reserved year). Training
    # stops at 2024-07-31 -- the same train_end as the "2023-24" fold
    # above -- so this fold's training pool never includes a single day of
    # 2024-08-01..2025-07-31. The gap between train_end and test_start is
    # the reserved year itself, held out on purpose.
    ("2025-26", V16_FLOOR, date(2024, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
]

# For the report only: F96's own original fold this session's "2025-26"
# fold replaces, so the training-data cost of the reservation is visible
# rather than hidden.
_F96_ORIGINAL_2025_26_FOLD = (
    "2025-26 (F96, pre-reservation)", V16_FLOOR, date(2025, 7, 31),
    date(2025, 8, 1), date(2026, 7, 31))


def _train_days(train_start, train_end):
    return (train_end - train_start).days + 1


# ------------------------------------------------------------------ by-construction verification

def main():
    print("=" * 78)
    print("SESSION 48 -- reserved-confirmation-year guard, verified BY")
    print("CONSTRUCTION ONLY. No data loaded, no model fit, no result")
    print("computed on 2024-25 or any other year.")
    print("=" * 78)
    print(f"\nreserved confirmation year : {RESERVED_YEAR_START} .. {RESERVED_YEAR_END} (D51)")
    print(f"sealed test year (untouched, separate, F94): {SEALED_YEAR_START} .. {SEALED_YEAR_END}")
    print(f"v16 floor (D48.7)          : {V16_FLOOR}")

    print("\n-- Positive check: every EXPERIMENT_FOLDS entry must pass the guard --")
    for label, tr_s, tr_e, te_s, te_e in EXPERIMENT_FOLDS:
        assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
        print(f"    {label:<10} train={tr_s}..{tr_e} ({_train_days(tr_s, tr_e)}d)  "
              f"test={te_s}..{te_e}  -- PASS (guard did not raise)")

    print("\n-- Negative check: deliberately reserved-year-touching folds must raise --")
    violations = [
        ("2025-26 (F96 original, train crosses the reserved year)",
         V16_FLOOR, date(2025, 7, 31), date(2025, 8, 1), date(2026, 7, 31)),
        ("hypothetical test-on-reserved-year fold",
         V16_FLOOR, date(2024, 7, 31), RESERVED_YEAR_START, RESERVED_YEAR_END),
        ("hypothetical train-into-reserved-year fold",
         V16_FLOOR, date(2025, 1, 1), date(2025, 8, 1), date(2026, 7, 31)),
    ]
    for label, tr_s, tr_e, te_s, te_e in violations:
        try:
            assert_reserved_year_excluded(label, tr_s, tr_e, te_s, te_e)
            print(f"    {label}: DID NOT RAISE -- guard failure, this is a bug")
            raise SystemExit(1)
        except ValueError as e:
            print(f"    {label}: raised as expected -- {e}")

    print("\n-- Honest cost: training data lost to the reservation --")
    orig_label, orig_s, orig_e, _, _ = _F96_ORIGINAL_2025_26_FOLD
    new_label, new_s, new_e, _, _ = EXPERIMENT_FOLDS[2]
    orig_days = _train_days(orig_s, orig_e)
    new_days = _train_days(new_s, new_e)
    print(f"    F96's own fold that tested 2025-26 trained on {orig_s}..{orig_e} "
          f"({orig_days} days).")
    print(f"    The equivalent session-48 experiment fold trains on {new_s}..{new_e} "
          f"({new_days} days) -- {orig_days - new_days} fewer days "
          f"({(orig_days - new_days) / 365.25:.2f} years), because training may not "
          f"reach into the reserved year.")
    print(f"    The '2022-23' fold remains the thinnest ({_train_days(EXPERIMENT_FOLDS[0][1], EXPERIMENT_FOLDS[0][2])} days, "
          f"~{_train_days(EXPERIMENT_FOLDS[0][1], EXPERIMENT_FOLDS[0][2]) / 365.25:.2f} years) -- unchanged by the "
          f"reservation, since it never reached 2024-25 in the first place.")
    print("    Net effect: the feature-selection programme runs on three folds")
    print("    (2022-23, 2023-24, 2025-26-truncated) instead of F96's four, and the")
    print("    fold nearest the sealed year loses about a year of training data --")
    print("    the price of a clean, genuinely out-of-sample confirmation year.")

    print("\n" + "=" * 78)
    print("END -- guard verified by construction only. No feature experiment was")
    print("run. No result was computed on 2024-25.")
    print("=" * 78)


if __name__ == "__main__":
    main()
