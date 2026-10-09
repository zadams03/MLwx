"""The archive tool, figures and lookups already on record (DECISIONS D95.8, D96).
Offline; writes only to temporary folders.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import csv
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
PROCESSED = ROOT / "data" / "processed"
ARCHIVE_TOOL = SCRIPTS / "archive_decisions.py"
SIZE_LIMIT = 80_000   # D93.9

# F139.4 at full precision.
F139_BASELINE = 1.049777501605027
F139_RAW_GFS = 1.4616990883475995
# F122.4 / F139.3: EGLC B+D,L,R,T on F109's fold.
F122_EGLC = 1.0007550363323212


def run_tool(*args):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run([sys.executable, str(ARCHIVE_TOOL), *args],
                          capture_output=True, text=True, env=env)


class ArchiveTool(unittest.TestCase):
    """scripts/archive_decisions.py (D93.8), on temporary copies."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="mlwx_test_archive_"))
        for name in ("DECISIONS.md", "DECISIONS-archive.md"):
            shutil.copyfile(ROOT / name, self.tmp / name)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_plan_passes(self):
        r = run_tool("--plan", "--root", str(self.tmp))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("plan: spans", r.stdout)

    def test_apply_rebuilds_original(self):
        # Take the first ID out of the copy's Live index, so at least one span
        # moves whatever the real index holds; the tool's four checks then run.
        live = self.tmp / "DECISIONS.md"
        lines = live.read_text(encoding="utf-8").split("\n")
        start = lines.index("<!-- live-index-start -->")
        self.assertTrue(lines[start + 1].startswith("- "))
        del lines[start + 1]
        live.write_text("\n".join(lines), encoding="utf-8")
        before_live = live.read_bytes()
        before_arch = (self.tmp / "DECISIONS-archive.md").read_bytes()

        r = run_tool("--apply", "--session", "test", "--root", str(self.tmp))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        for k in (1, 2, 3, 4):
            self.assertRegex(r.stdout, rf"check {k} \(.*\): PASS")
        self.assertIn("moved ", r.stdout)
        # The archive starts with the old archive, byte for byte.
        after_arch = (self.tmp / "DECISIONS-archive.md").read_bytes()
        self.assertEqual(after_arch[:len(before_arch)], before_arch)
        self.assertNotEqual((self.tmp / "DECISIONS.md").read_bytes(), before_live)
        # A second run moves nothing.
        r2 = run_tool("--apply", "--session", "test", "--root", str(self.tmp))
        self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
        self.assertIn("nothing to move", r2.stdout)

    def test_citations_real_files_resolve(self):
        out = self.tmp / "citations.txt"
        r = run_tool("--citations", "--out", str(out))
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        listed = out.read_text().split("Unresolved (number: where cited):\n")[1].split("Found in both")[0]
        self.assertIn("unresolved 0,", r.stdout, "unresolved: " + listed.strip())
        self.assertIn("found in both files 0", r.stdout)

    def test_decisions_size(self):
        size = (ROOT / "DECISIONS.md").stat().st_size
        self.assertLess(size, SIZE_LIMIT, f"DECISIONS.md is {size} bytes")


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.reader(f))


class F139Headline(unittest.TestCase):
    """F139.4's headline from the committed cell scores (D89.5)."""

    def headline(self, method):
        rows = read_rows(PROCESSED / "session97_stagec_cv_scores.csv")
        head = rows[0]
        self.assertEqual(head, ["station", "fold", "cycle_hour", "lead", "method", "n", "mae", "mean_error"])
        n_sum, w_sum = defaultdict(int), defaultdict(list)
        for r in rows[1:]:
            if r[4] == method:
                n = int(r[5])
                n_sum[r[0]] += n
                w_sum[r[0]].append(n * float(r[6]))
        self.assertEqual(len(n_sum), 6)
        airport = [math.fsum(w_sum[s]) / n_sum[s] for s in n_sum]
        return sum(airport) / len(airport)

    def test_baseline_headline(self):
        self.assertAlmostEqual(self.headline("baseline"), F139_BASELINE, delta=1e-12)

    def test_raw_gfs_headline(self):
        self.assertAlmostEqual(self.headline("raw_gfs"), F139_RAW_GFS, delta=1e-12)


class F143BaselineRows(unittest.TestCase):
    """F143.6: session 100's baseline rows equal session 97's (first eight columns)."""

    def test_baseline_rows_equal(self):
        s97 = [r for r in read_rows(PROCESSED / "session97_stagec_cv_scores.csv")[1:] if r[4] == "baseline"]
        s100 = [r[:8] for r in read_rows(PROCESSED / "session100_structure_cv_scores.csv")[1:]
                if r[8] == "baseline"]
        self.assertEqual(len(s97), 1584)
        self.assertEqual(s100, s97)


class F122EglcGate(unittest.TestCase):
    """F122.4's gate at EGLC: B+D,L,R,T refit on F109's training rows from
    session81_training_set.csv, with the record's settings, gives the recorded
    test MAE exactly. Uses session81_freeze_forward_models.py's own functions
    (load_training_set, fit, matrix) and its fold dates; importing it runs no
    mode and writes nothing."""

    @classmethod
    def setUpClass(cls):
        # See test_guards.py: skip the libomp shim's process restart (D93.3).
        os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")
        sys.path.insert(0, str(SCRIPTS))
        import session81_freeze_forward_models as s81
        cls.s81 = s81

    def test_eglc_mae(self):
        s81 = self.s81
        tr_s, tr_e, te_s, te_e, stations = s81.GATE_FOLDS["F109"]
        self.assertIn("EGLC", stations)
        data = s81.load_training_set()["EGLC"]
        train = [r for r in data if tr_s <= r["date"] <= tr_e]
        test = [r for r in data if te_s <= r["date"] <= te_e]
        self.assertEqual((len(train), len(test)), (1225, 364))
        m = s81.fit(train, s81.G15)
        pred = m.predict(s81.matrix(test, s81.G15))
        errs = [(r["temperature_grib_c"] + float(pred[i])) - r["obs_c"] for i, r in enumerate(test)]
        self.assertEqual(s81.rec.mae(errs), F122_EGLC)


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RecordLookups(unittest.TestCase):
    """The record lookups that the stage C pull and stage B depend on (D96.2,
    D96.3). F122 is in DECISIONS-archive.md, so both files are read together.
    Importing these scripts runs no mode and writes nothing."""

    @classmethod
    def setUpClass(cls):
        # See test_guards.py: skip the libomp shim's process restart (D93.3).
        os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")
        sys.path.insert(0, str(SCRIPTS))
        import session87_forward_score as s87
        import session91_grib_pull as s91
        cls.s87, cls.s91 = s87, s91

    def test_s91_training_set_sha_matches_f122_3(self):
        text = self.s87.read_decisions_text()
        found = re.findall(r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`", text)
        self.assertEqual(len(found), 1)
        self.assertEqual(self.s91.TRAINING_SET_SHA256, found[0])
        self.assertEqual(self.s91.TRAINING_SET_SHA256, sha256_of(PROCESSED / "session81_training_set.csv"))

    def test_s87_manifest_pattern_finds_f122_5_value(self):
        # The pattern in session87_forward_score.load_frozen_models.
        text = self.s87.read_decisions_text()
        found = re.findall(r"manifest\.json`, SHA-256\s+`([0-9a-f]{64})`", text)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0], sha256_of(ROOT / "data" / "models" / "session81" / "manifest.json"))

    def test_s87_f122_5_table_has_all_six_airports(self):
        # The slice and row pattern in session87_forward_score.load_frozen_models.
        text = self.s87.read_decisions_text()
        self.assertEqual(text.count("**F122.5"), 1)
        self.assertEqual(text.count("**F122.6"), 1)
        block = text[text.index("**F122.5"):text.index("**F122.6")]
        rows = re.findall(r"^\| (EGLC|LFPG|DSM|YSDU|RNO|KSFO \(SFO\)) \| \d+ \| `[0-9a-f]{64}` \| "
                          r"`[0-9a-f]{64}` \| -?[0-9.]+ \|", block, re.M)
        self.assertEqual(sorted(rows), sorted(["EGLC", "LFPG", "DSM", "YSDU", "RNO", "KSFO (SFO)"]))


if __name__ == "__main__":
    unittest.main()
