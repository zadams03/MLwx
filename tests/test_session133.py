"""Session 133's range comparison (DECISIONS D128), on made-up values.

- The interval score at 80 %: inside, below, above, and on an edge (D128.5).
- Table percentiles are built only from the earlier periods (D128.5, D128.6).
- The rule (D128.8): a challenger that passes all four parts replaces the incumbent; each part failing
  alone keeps the incumbent; a first candidate outside the coverage band means no choice.
- Q's swap where q0.1 > q0.9 (D128.6), counted.
- Tercile edges come from the earlier periods only (D128.9), and the tie rule at the top.
- The three imported scripts' SHA-256 equal session 133's Step 1 values, on disk and in the script.
"""

import hashlib
import os
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # skip session 62's process restart (D93.3)

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import numpy as np  # noqa: E402

import session133_ranges as r  # noqa: E402

# Session 133's Step 1, held here.
STEP1_SHA256 = {
    "session97_stagec_cv.py": "987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91",
    "session104_curve_cv.py": "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb",
    "session112_analysis.py": "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab",
}


class TestIntervalScore(unittest.TestCase):
    def test_four_cases(self):
        lo, hi = [1.0] * 5, [3.0] * 5
        y = [2.0, 0.5, 4.0, 1.0, 3.0]          # inside, below, above, on the lower edge, on the upper edge
        got = r.interval_score(lo, hi, y)
        np.testing.assert_allclose(got, [2.0, 2.0 + 10 * 0.5, 2.0 + 10 * 1.0, 2.0, 2.0])
        self.assertEqual(r.inside(lo, hi, y).tolist(), [True, False, False, True, True])

    def test_summary(self):
        n, cov, width, score = r.summary(np.array([0.0, 0.0]), np.array([2.0, 2.0]), np.array([1.0, 3.0]))
        self.assertEqual((n, cov, width), (2, 0.5, 2.0))
        self.assertAlmostEqual(score, (2.0 + 12.0) / 2)


class TestTables(unittest.TestCase):
    def test_earlier_periods_only(self):
        e = np.array([0.0, 1.0, 2.0, 3.0, 4.0, 100.0, 200.0, 300.0])
        period = np.array(["2023-24"] * 5 + ["2024-25"] * 3)
        code = np.zeros(8, dtype=int)
        tab = r.build_table(e, code, period, r.EARLIER["2024-25"])
        p10, p90 = np.percentile(e[:5], [10, 90])
        self.assertEqual(tab, {0: (float(p10), float(p90), 5)})
        tab2 = r.build_table(e, code, period, r.EARLIER["2025-26"])
        self.assertEqual(tab2[0][2], 8)
        lo, hi = r.apply_table(tab, np.array([0, 0]), np.array([10.0, 20.0]))
        self.assertEqual(lo.tolist(), [10.0 + p10, 20.0 + p10])
        self.assertEqual(hi.tolist(), [10.0 + p90, 20.0 + p90])

    def test_missing_cell_stops(self):
        tab = {0: (-1.0, 1.0, 3)}
        with self.assertRaises(SystemExit):
            r.apply_table(tab, np.array([0, 1]), np.array([0.0, 0.0]))


def made_up(air, head, cov):
    return {"air": list(air), "head": dict(zip(r.SCORING, head)), "cov": dict(zip(r.SCORING, cov))}


class TestLadder(unittest.TestCase):
    INC = made_up([5.0] * 6, (5.0, 5.0), (0.80, 0.80))
    GOOD = made_up([4.8] * 6, (4.8, 4.8), (0.80, 0.80))

    def run_two(self, ch):
        return r.ladder(("A", "B"), {"A": self.INC, "B": ch})

    def test_all_four_hold(self):
        win, steps = self.run_two(self.GOOD)
        self.assertEqual(win, "B")
        self.assertTrue(steps[1]["replaces"])

    def test_i_fails_alone(self):
        ch = made_up([4.96] * 6, (4.96, 4.96), (0.80, 0.80))   # 0.8 % lower: not more than 1 %
        win, steps = self.run_two(ch)
        self.assertEqual(win, "A")
        self.assertEqual([steps[1][k] for k in ("i", "ii", "iii", "iv")], [False, True, True, True])

    def test_ii_fails_alone(self):
        ch = made_up([4.0, 4.0, 4.0, 5.1, 5.1, 5.1], (4.8, 4.8), (0.80, 0.80))   # lower at 3 of 6
        win, steps = self.run_two(ch)
        self.assertEqual(win, "A")
        self.assertEqual([steps[1][k] for k in ("i", "ii", "iii", "iv")], [True, False, True, True])

    def test_iii_fails_alone(self):
        ch = made_up([4.8] * 6, (4.6, 5.0), (0.80, 0.80))     # a tie in 2025-26 fails
        win, steps = self.run_two(ch)
        self.assertEqual(win, "A")
        self.assertEqual([steps[1][k] for k in ("i", "ii", "iii", "iv")], [True, True, False, True])

    def test_iv_fails_alone(self):
        ch = made_up([4.8] * 6, (4.8, 4.8), (0.80, 0.86))
        win, steps = self.run_two(ch)
        self.assertEqual(win, "A")
        self.assertEqual([steps[1][k] for k in ("i", "ii", "iii", "iv")], [True, True, True, False])

    def test_iv_edges_inclusive(self):
        ch = made_up([4.8] * 6, (4.8, 4.8), (0.75, 0.85))
        self.assertEqual(self.run_two(ch)[0], "B")

    def test_first_candidate_outside_band(self):
        inc = made_up([5.0] * 6, (5.0, 5.0), (0.74, 0.80))
        win, steps = r.ladder(("A", "B"), {"A": inc, "B": self.GOOD})
        self.assertIsNone(win)
        self.assertEqual(len(steps), 1)

    def test_winner_carries_forward(self):
        better = made_up([4.5] * 6, (4.5, 4.5), (0.80, 0.80))
        win, steps = r.ladder(("A", "B", "C"), {"A": self.INC, "B": self.GOOD, "C": better})
        self.assertEqual(win, "C")
        self.assertEqual(steps[2]["incumbent"], "B")


class TestSwap(unittest.TestCase):
    def test_swap_counted(self):
        lo, hi, n = r.swap_pairs(np.array([1.0, 3.0, 2.0]), np.array([2.0, 1.0, 2.0]))
        self.assertEqual(lo.tolist(), [1.0, 1.0, 2.0])
        self.assertEqual(hi.tolist(), [2.0, 3.0, 2.0])
        self.assertEqual(n, 1)

    def test_params_put_back(self):
        base = r.s97.LGB_PARAMS
        with r.quantile_params(0.1):
            self.assertEqual(r.s97.LGB_PARAMS["objective"], "quantile")
            self.assertEqual(r.s97.LGB_PARAMS["alpha"], 0.1)
            self.assertEqual({k: v for k, v in r.s97.LGB_PARAMS.items() if k not in ("objective", "alpha")},
                             {k: v for k, v in base.items() if k != "objective"})
        self.assertIs(r.s97.LGB_PARAMS, base)
        self.assertEqual(base["objective"], "regression_l1")


class TestTerciles(unittest.TestCase):
    def test_edges_from_earlier_only(self):
        v = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 1000.0, 2000.0, np.nan])
        period = np.array(["2023-24"] * 6 + ["2024-25"] * 3)
        e1, e2, n, top = r.tercile_edges(v, period, r.EARLIER["2024-25"])
        q = np.quantile(v[:6], [1 / 3, 2 / 3])
        self.assertEqual((e1, e2, n, top), (float(q[0]), float(q[1]), 6, 6.0))
        self.assertEqual(r.tercile_edges(v, period, r.EARLIER["2025-26"])[2], 8)   # the nan is left out

    def test_levels_and_top_tie(self):
        self.assertEqual(r.tercile_level([0.0, 2.0, 3.0, 9.0, np.nan], (2.0, 5.0), 10.0).tolist(), [0, 0, 1, 2, -1])
        self.assertEqual(r.tercile_level([50.0, 99.0, 100.0], (40.0, 100.0), 100.0).tolist(), [1, 1, 2])


class TestFingerprints(unittest.TestCase):
    def test_imported_scripts(self):
        self.assertEqual(r.IMPORTED_SHA256, STEP1_SHA256)
        for name, want in STEP1_SHA256.items():
            self.assertEqual(hashlib.sha256((SCRIPTS / name).read_bytes()).hexdigest(), want, name)


if __name__ == "__main__":
    unittest.main()
