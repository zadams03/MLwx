"""Session 132's three scripts (DECISIONS D127.4 to D127.6).

- The Gates C and D wrapper's airport list is the 12 record airports of D103.4.
- The three imported scripts' SHA-256 equal the values held here (D127.4, D127.5(c) and the prompt's start check),
  in the wrappers' constants and on disk; D127's two named values are in its text.
- The revision script's pairing and sign share on made-up rows.
- The revision script's prediction-file SHA-256 constants equal session 112's meta.txt (D98.2), when that folder
  is present.
"""

import ast
import datetime as dt
import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# D127.4 and D127.5(c), held here.
D127_SHA256 = {
    "session109_gates.py": "8ac5a567fb4356db61136db4db7783eae381500a2f0314ad9d5a08cee726f59b",
    "session112_analysis.py": "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab",
    "session114_comparisons.py": "5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52",
}
RECORD_12 = {"EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def constant(script, name):
    """A module-level constant read from the script's source, without importing it."""
    tree = ast.parse((SCRIPTS / script).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise KeyError(name)


class TestFingerprints(unittest.TestCase):
    def test_files_on_disk(self):
        for name, want in D127_SHA256.items():
            self.assertEqual(sha256(SCRIPTS / name), want, name)

    def test_wrapper_constants(self):
        self.assertEqual(constant("session132_gates_cd.py", "S109_SHA256"), D127_SHA256["session109_gates.py"])
        self.assertEqual(constant("session132_iem_rows.py", "S114_SHA256"), D127_SHA256["session114_comparisons.py"])
        self.assertEqual(constant("session114_comparisons.py", "S112_SCRIPT_SHA256"),
                         D127_SHA256["session112_analysis.py"])

    def test_values_in_d127(self):
        text = (ROOT / "DECISIONS.md").read_text() + (ROOT / "DECISIONS-archive.md").read_text()
        start = text.index("**D127. ")
        d127 = text[start:text.index("\n---", start)]
        for name in ("session109_gates.py", "session114_comparisons.py"):     # the two D127 names by SHA-256
            self.assertTrue(D127_SHA256[name] in d127, name)


class TestGatesWrapper(unittest.TestCase):
    def test_record_airports(self):
        self.assertEqual(set(constant("session132_gates_cd.py", "RECORD_ICAOS")), RECORD_12)
        self.assertEqual(len(constant("session132_gates_cd.py", "RECORD_ICAOS")), 12)

    def test_wrapper_sets_module_constant(self):
        import session132_gates_cd as w
        self.assertEqual({a.icao for a in w.RECORD_AIRPORTS}, RECORD_12)
        self.assertGreater(len(w.CONFIGURED), 12)
        saved = w.s109.AIRPORTS
        try:
            w.use_record_airports()
            self.assertEqual({a.icao for a in w.s109.AIRPORTS}, RECORD_12)
        finally:
            w.s109.AIRPORTS = saved


class TestRevision(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import session132_revision as rv
        cls.rv = rv

    def rows(self):
        t0 = dt.datetime(2025, 7, 31, 12)
        step = dt.timedelta(hours=6)
        rows = {}

        def put(c, L, period, status="scored", raw=10.0):
            rows[(c, L)] = (period, status, c + dt.timedelta(hours=L), repr(raw), "10.5", "11.0")

        for L in range(3, 49):
            put(t0, L, "A", raw=10.0 + L / 10)
            put(t0 + step, L, "A", raw=10.5 + L / 10)
            put(t0 + 2 * step, L, "B", raw=11.0 + L / 10)
        del rows[(t0 + step, 20)]
        put(t0 + step, 21, "A", status="incomplete")
        return t0, step, rows

    def test_pairing(self):
        rv = self.rv
        t0, step, rows = self.rows()
        pairs, cnt = rv.pair_rows(rows)
        keys = {(p[0], p[1]) for p in pairs}
        self.assertIn((t0, 9), keys)
        self.assertNotIn((t0, 8), keys)
        self.assertTrue(all(9 <= L <= 48 for _, L in keys))
        self.assertNotIn((t0, 26), keys)                      # next row missing
        self.assertNotIn((t0, 27), keys)                      # next row incomplete
        self.assertFalse(any(c == t0 + step for c, _ in keys))  # next cycle in another period
        self.assertEqual(cnt[rv.REASONS[0]], 18)
        self.assertEqual(cnt[rv.REASONS[1]], 40)
        self.assertEqual(cnt[rv.REASONS[2]], 1)
        self.assertEqual(cnt[rv.REASONS[3]], 1)
        self.assertEqual(cnt[rv.REASONS[4]], 38)
        self.assertEqual(cnt["paired"], 38)
        self.assertEqual(cnt["rows in (a)"], cnt["paired"] + sum(cnt[k] for k in rv.REASONS))
        p = next(x for x in pairs if (x[0], x[1]) == (t0, 30))
        self.assertAlmostEqual(p[6] - p[3], (10.5 + 2.4) - (10.0 + 3.0), places=12)

    def test_limit(self):
        rv = self.rv
        c = dt.datetime(2026, 7, 31, 18)
        rows = {(c, 6): ("B", "scored", c + dt.timedelta(hours=6), "1.0", "1.0", "1.0")}
        _, cnt = rv.pair_rows(rows)
        self.assertEqual(cnt["rows not in (a)"], 1)

    def test_sign_share_with_zeros(self):
        import numpy as np
        rv = self.rv
        k = np.array([1.0, -1.0, 0.0, 2.0, -2.0, 0.5])
        r = np.array([2.0, -0.5, 1.0, 0.0, 1.0, 0.25])
        S = rv.StatSet(dict(k=k, r=r, kb=k / 2, b=k / 2), np.ones(6, dtype=bool))
        st = S.stats(np.ones(6))
        self.assertAlmostEqual(st["sign_share"], 0.75, places=12)
        c = S.counts()
        self.assertEqual((c["k_zero"], c["r_zero"], c["both_nonzero"]), (1, 1, 4))
        self.assertAlmostEqual(st["mean_abs_r"], float(np.mean(np.abs(r))), places=12)
        self.assertAlmostEqual(st["mean_abs_r_minus_k"], float(np.mean(np.abs(r - k))), places=12)

    def test_pred_constants_equal_meta(self):
        meta = self.rv.PRED_DIR / "meta.txt"
        if not meta.exists():
            self.skipTest("../MLwx-stagec/analysis112 is not present")
        self.assertEqual(self.rv.meta_sha256(), self.rv.PRED_SHA256)
        self.assertEqual(list(self.rv.PRED_SHA256), self.rv.AIRPORTS)


if __name__ == "__main__":
    unittest.main()
