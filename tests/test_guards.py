"""The leakage guards (DECISIONS D95.8): each refuses what it must and allows
the case just inside its limit. Offline; nothing is written in the repo.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import datetime as dt
import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

# Importing session62_reserved_confirm.py (through session 97's script) or
# session86_forward_build.py runs a libomp loader shim that restarts the
# process unless this variable is set. lightgbm imports without the shim on
# this machine (D93.3), so the restart is skipped.
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")

import session48_reserved_year as s48  # noqa: E402
import session86_forward_build as s86  # noqa: E402
import session91_grib_pull as s91  # noqa: E402
import session97_stagec_cv as s97  # noqa: E402


class Session97Guard(unittest.TestCase):
    """The 2026-27 guard used by session97_stagec_cv.py (F139.5)."""

    def test_refuses_2026_08_01(self):
        with self.assertRaises(s97.GuardError):
            s97.check_valid(dt.datetime(2026, 8, 1, 0, 0))

    def test_allows_2026_07_31_23(self):
        s97.check_valid(dt.datetime(2026, 7, 31, 23, 0))


class Session86GateDate(unittest.TestCase):
    """session86_forward_build.check_gate_date (F128.4)."""

    def test_refuses_2026_08_01(self):
        with self.assertRaises(s86.GuardError):
            s86.check_gate_date(dt.date(2026, 8, 1))

    def test_allows_2026_07_31(self):
        s86.check_gate_date(dt.date(2026, 7, 31))


class Session48ReservedYear(unittest.TestCase):
    """The session-48 reserved-year guard (D51)."""

    def test_refuses_training_inside_reserved_year(self):
        with self.assertRaises(ValueError):
            s48.assert_reserved_year_excluded(
                "train inside", s48.V16_FLOOR, dt.date(2025, 1, 1),
                dt.date(2025, 8, 1), dt.date(2026, 7, 31))

    def test_refuses_testing_inside_reserved_year(self):
        with self.assertRaises(ValueError):
            s48.assert_reserved_year_excluded(
                "test inside", s48.V16_FLOOR, dt.date(2024, 7, 31),
                dt.date(2024, 8, 1), dt.date(2025, 7, 31))

    def test_passes_experiment_folds(self):
        self.assertEqual(len(s48.EXPERIMENT_FOLDS), 3)
        for fold in s48.EXPERIMENT_FOLDS:
            s48.assert_reserved_year_excluded(*fold)


class Session91PullGuards(unittest.TestCase):
    """The stage C pull script's guards (D83.5(b), D95.5)."""

    def test_refuses_cycle_after_last(self):
        with self.assertRaises(s91.GuardError):
            s91.check_request(dt.datetime(2026, 8, 1, 0), 0)

    def test_refuses_valid_after_last(self):
        # Cycle 2026-07-31T18 is allowed; f006 is valid at 2026-08-01T00.
        with self.assertRaises(s91.GuardError):
            s91.check_request(dt.datetime(2026, 7, 31, 18), 6)

    def test_allows_last_cycle_and_valid_time(self):
        s91.check_request(dt.datetime(2026, 7, 31, 18), 5)

    def test_refuses_cycles_before_first_v16_run(self):
        # Every cycle before 2021-03-22T12 at hours 25 to 48 whose valid time
        # is inside the window (D84.2, D95.5); the others fail on valid time.
        for c in (dt.datetime(2021, 3, 21, 18), dt.datetime(2021, 3, 22, 0), dt.datetime(2021, 3, 22, 6)):
            for fh in range(25, 49):
                with self.assertRaises(s91.GuardError):
                    s91.check_request(c, fh)

    def test_plan_leaves_out_cycles_before_first_v16_run(self):
        plan = s91.plan_chunk(s91.month_cycles(2021, 3), (25, 48))
        self.assertEqual(plan[0][0], dt.datetime(2021, 3, 22, 12))
        self.assertTrue(all(c >= s91.FIRST_CYCLE for c, _ in plan))

    def test_allows_first_v16_run(self):
        s91.check_request(dt.datetime(2021, 3, 22, 12), 36)


if __name__ == "__main__":
    unittest.main()
