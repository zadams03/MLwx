"""Stage B's rules, through the frozen scripts' own code, on made-up arrays (DECISIONS D73.3, D73.5, D79.2,
D79.3; register row TE05; session 131, Step 6(c)).

Offline. Imports `session87_forward_score.py` and `session86_forward_build.py` unchanged (they are frozen,
D62.3(a); their SHA-256 is checked by tests/test_frozen_scripts.py) and calls their scoring core, period
functions and guards on made-up numbers; no real 2026-27 value exists or is read. Then runs the three
`--guard-check` modes of stage B's scripts as separate processes: each must exit 0.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import csv
import datetime as dt
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # skip the frozen scripts' process restart (D93.3)

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import numpy as np  # noqa: E402

import session86_forward_build as s86  # noqa: E402
import session87_forward_score as s87  # noqa: E402

NAN = float("nan")
CYCLES = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 0, "RNO": 18, "SFO": 18}   # SPEC 3.4, as session 87's guard


class Ties(unittest.TestCase):
    """D79.2: PASS needs the model's MAE strictly lower; a tie fails."""

    def test_a_tie_with_raw_gfs_fails(self):
        obs = [10.0, 12.0, 14.0]
        r = s87.d73_core(obs, [11.0, 13.0, 15.0], [9.0, 11.0, 13.0], None, None, [0.0, 0.0, 0.0])
        self.assertEqual(r["mae_model"], r["mae_raw"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_a_tie_with_persistence_fails(self):
        obs = [10.0, 12.0]
        r = s87.d73_core(obs, [15.0, 17.0], [11.0, 13.0], None, None, [9.0, 13.0])
        self.assertEqual(r["mae_model"], r["mae_pers"])
        self.assertEqual(r["verdict"], "FAIL")

    def test_strictly_lower_passes(self):
        r = s87.d73_core([10.0, 12.0], [15.0, 17.0], [10.5, 12.5], None, None, [9.0, 13.0])
        self.assertEqual(r["verdict"], "PASS")

    def test_a_competitor_tie_fails(self):
        rng = np.random.default_rng(0)
        r = s87.d77_core(rng, [10.0, 12.0], [11.0, 13.0], [9.0, 11.0], [12.0, 14.0])
        self.assertEqual((r["mae_model"], r["verdict"]), (r["mae_comp"], "FAIL"))


class DayBasis(unittest.TestCase):
    """D73.5: raw GFS and the models on every day; persistence on the days with a previous-day observation;
    the persistence margin compares the model's MAE on every day with persistence's on its days."""

    def test_persistence_uses_only_days_with_a_previous_observation(self):
        obs = [10.0, 20.0, 30.0, 40.0]
        model = [11.0, 21.0, 31.0, 45.0]                 # errors 1, 1, 1, 5: MAE 2 over all four days
        pers = [NAN, 18.0, NAN, 37.0]                    # errors 2 and 3 on its two days: MAE 2.5
        r = s87.d73_core(obs, [14.0, 24.0, 34.0, 44.0], model, None, None, pers)
        self.assertEqual((r["n"], r["n_pers"]), (4, 2))
        self.assertEqual(r["mae_model"], 2.0)
        self.assertEqual(r["mae_pers"], 2.5)
        self.assertEqual(r["margin_pers_pct"], 100.0 * (1.0 - 2.0 / 2.5))
        self.assertEqual(r["verdict"], "PASS")

    def test_descriptive_rungs_do_not_enter_the_verdict(self):
        obs = [10.0, 20.0]
        r = s87.d73_core(obs, [12.0, 22.0], [11.0, 21.0], [10.0, 20.0], [10.0, 20.0], [13.0, 23.0])
        self.assertEqual((r["mae_b"], r["mae_meanbias"]), (0.0, 0.0))
        self.assertEqual(r["verdict"], "PASS")


class NoVerdict(unittest.TestCase):
    """D79.3: no days, or no persistence day, gives "no verdict (0 days)"; a competitor with no day is void."""

    def test_no_days(self):
        r = s87.d73_core([], [], [], None, None, [])
        self.assertEqual((r["n"], r["verdict"]), (0, "no verdict (0 days)"))

    def test_no_persistence_day(self):
        r = s87.d73_core([10.0, 12.0], [15.0, 17.0], [10.5, 12.5], None, None, [NAN, NAN])
        self.assertEqual((r["n_pers"], r["verdict"]), (0, "no verdict (0 days)"))

    def test_competitor_with_no_day_is_void(self):
        self.assertEqual(s87.d77_core(np.random.default_rng(0), [], [], [], [])["verdict"], "void")


class PeriodSplit(unittest.TestCase):
    """D73.3: a target day is in period B if the cycle that forecasts it (day D-1 at the airport's cycle hour)
    is at or after the first operational v17 cycle; period A otherwise. Sessions 86 and 87 agree."""

    def test_split_at_a_first_v17_cycle(self):
        v17 = dt.datetime(2026, 11, 15, 12)
        want = {0: dt.date(2026, 11, 16), 12: dt.date(2026, 11, 15), 18: dt.date(2026, 11, 15)}
        for hour, last_a in want.items():
            for mod in (s86, s87):
                with self.subTest(script=mod.__name__, cycle=hour):
                    self.assertEqual(mod.last_period_a_day(hour, v17), last_a)
            cyc = dt.datetime.combine(last_a - dt.timedelta(days=1), dt.time(hour))
            self.assertLess(cyc, v17)
            self.assertGreaterEqual(cyc + dt.timedelta(days=1), v17)
            self.assertEqual(s87.period_range("A", hour, v17), (dt.date(2026, 8, 1), last_a))
            self.assertEqual(s87.period_range("B", hour, v17), (last_a + dt.timedelta(days=1), dt.date(2027, 7, 31)))

    def test_no_v17_makes_period_a_the_whole_year_and_b_empty(self):
        for hour in (0, 12, 18):
            self.assertEqual(s87.period_range("A", hour, None), (dt.date(2026, 8, 1), dt.date(2027, 7, 31)))
            self.assertIsNone(s87.period_range("B", hour, None))
            self.assertEqual(s86.last_period_a_day(hour, None), dt.date(2027, 7, 31))

    def test_v17_before_the_year_leaves_no_period_a(self):
        self.assertIsNone(s87.period_range("A", 18, dt.datetime(2026, 7, 31, 0)))
        reasons, _ = s87.validate_request("A", dt.datetime(2026, 7, 31, 0), False, "D", dt.date(2028, 1, 1),
                                          CYCLES, "x", "y", "n", "m")
        self.assertTrue(any("no period-A day" in r for r in reasons))


class RowsFileDates(unittest.TestCase):
    """The rows file's date check: a date outside the airport's period, or on or after 2027-08-01, stops the
    run; so does a repeated day."""

    RANGES = {st: (dt.date(2026, 8, 1), dt.date(2026, 11, 15)) for st in s87.AIRPORTS}

    def write_rows(self, rows):
        f = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, newline="")
        self.addCleanup(os.unlink, f.name)
        w = csv.writer(f)
        w.writerow(s87.ROW_COLS)
        for st, d in rows:
            w.writerow([st, d, 12] + ["1.0"] * len(s87.G15) + ["10.0", "11.0", ""])
        f.close()
        return f.name

    def test_dates_inside_load(self):
        by = s87.load_rows(self.write_rows([("DSM", "2026-11-15"), ("DSM", "2026-08-01")]), self.RANGES)
        self.assertEqual([r["date"] for r in by["DSM"]], [dt.date(2026, 8, 1), dt.date(2026, 11, 15)])
        self.assertIsNone(by["DSM"][0]["prev_obs_c"])

    def test_a_date_outside_the_period_stops(self):
        for bad in ("2026-07-31", "2026-11-16"):
            with self.subTest(date=bad), self.assertRaises(s87.GuardError):
                s87.load_rows(self.write_rows([("DSM", bad)]), self.RANGES)

    def test_a_date_on_or_after_2027_08_01_stops(self):
        with self.assertRaises(s87.GuardError) as cm:
            s87.check_row_dates({"DSM": [dt.date(2027, 8, 1)]}, {"DSM": (dt.date(2026, 8, 1), dt.date(2027, 8, 5))})
        self.assertIn("on or after 2027-08-01", str(cm.exception))

    def test_a_repeated_day_stops(self):
        with self.assertRaises(s87.GuardError):
            s87.load_rows(self.write_rows([("DSM", "2026-09-01"), ("DSM", "2026-09-01")]), self.RANGES)

    def test_a_non_finite_value_stops(self):
        path = self.write_rows([("DSM", "2026-09-01")])
        text = Path(path).read_text().replace("10.0,11.0", "nan,11.0")
        Path(path).write_text(text)
        with self.assertRaises(s87.GuardError):
            s87.load_rows(path, self.RANGES)


class GuardChecks(unittest.TestCase):
    """The three --guard-check modes of stage B's scripts exit 0 (offline; no data file read)."""

    def test_three_guard_checks_exit_0(self):
        env = {**os.environ, "MLWX_LIBOMP_PATH_SET": "1", "PYTHONDONTWRITEBYTECODE": "1"}
        for script in ("session86_forward_build.py", "session87_forward_competitors.py",
                       "session87_forward_score.py"):
            with self.subTest(script=script):
                r = subprocess.run([sys.executable, str(SCRIPTS / script), "--guard-check"], cwd=ROOT, env=env,
                                   capture_output=True, text=True, timeout=300)
                self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
                self.assertIn("all cases behaved", r.stdout)
                self.assertNotIn("[BAD]", r.stdout)


if __name__ == "__main__":
    unittest.main()
