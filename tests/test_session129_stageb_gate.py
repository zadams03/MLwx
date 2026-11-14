"""Session 129: checks of session 86's gate wrapper (DECISIONS D123.5, D118.10, D98.2).

Offline. The wrapper's constants are checked against both DECISIONS files and the committed files, and
session 86's own lookups are run against the wrapper's stand-in. Session 86's gate itself is never run
here (it needs the network).

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import contextlib
import hashlib
import io
import os
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # skip session 86's process restart (D93.3)

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session129_stageb_gate as w  # noqa: E402


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def both_decisions():
    return (ROOT / "DECISIONS.md").read_text() + "\n" + (ROOT / "DECISIONS-archive.md").read_text()


class Constants(unittest.TestCase):
    """Each constant equals the record (both DECISIONS files read together) and the committed file."""

    @classmethod
    def setUpClass(cls):
        cls.text = both_decisions()

    def test_training_set(self):
        found = re.findall(r"session81_training_set\.csv`,\s+([\d,]+) data rows,\s+SHA-256 `([0-9a-f]{64})`",
                           self.text)
        self.assertEqual(found, [(f"{w.TRAINING_ROWS:,}", w.p91.TRAINING_SET_SHA256)])
        self.assertEqual(sha256_of(w.s86.TRAINING_SET), w.p91.TRAINING_SET_SHA256)

    def test_manifest(self):
        found = re.findall(r"manifest\.json`, SHA-256\s+`([0-9a-f]{64})`", self.text)
        self.assertEqual(found, [w.MANIFEST_SHA256])
        self.assertEqual(sha256_of(w.s86.MODEL_DIR / "manifest.json"), w.MANIFEST_SHA256)

    def test_model_table(self):
        block = self.text[self.text.index("**F122.5"):self.text.index("**F122.6")]
        rows = re.findall(r"^\| (EGLC|LFPG|DSM|YSDU|RNO|KSFO \(SFO\)) \| (\d+) \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|",
                          block, re.M)
        self.assertEqual({r[0]: (int(r[1]), r[2], r[3]) for r in rows}, w.F122_5_MODELS)
        self.assertEqual(len(rows), 6)
        self.assertEqual(self.text.count("**F122.5"), 1)
        for label, (_, bdlrt, b) in w.F122_5_MODELS.items():
            st = w.station_of(label)
            self.assertEqual(sha256_of(w.s86.MODEL_DIR / f"{st}_bdlrt.txt"), bdlrt)
            self.assertEqual(sha256_of(w.s86.MODEL_DIR / f"{st}_b.txt"), b)

    def test_session_86_is_the_frozen_file(self):
        self.assertEqual(sha256_of(SCRIPTS / "session86_forward_build.py"), w.S86_SCRIPT_SHA256)
        self.assertIn(w.S86_SCRIPT_SHA256, (ROOT / "tests" / "test_frozen_scripts.py").read_text())


class Swap(unittest.TestCase):
    """Session 86's own lookups, run against the stand-in, give the constants."""

    def setUp(self):
        self.real = w.s86.DECISIONS_FILE
        self.addCleanup(setattr, w.s86, "DECISIONS_FILE", self.real)

    def test_session_86_reads_decisions_md_alone(self):
        self.assertEqual(self.real, ROOT / "DECISIONS.md")           # D96.3: why its gate needs the swap
        src = (SCRIPTS / "session86_forward_build.py").read_text()
        self.assertEqual(src.count("DECISIONS_FILE.read_text()"), 2)  # the pattern lookup, and plumbing
        self.assertEqual(src.count('expected_hash_from_decisions(r"'), 2)

    def test_the_wrapper_reads_no_decisions_file(self):
        src = (SCRIPTS / "session129_stageb_gate.py").read_text()
        for banned in ('"DECISIONS', "'DECISIONS", "DECISIONS_FILE.read", "read_decisions"):
            self.assertNotIn(banned, src)
        self.assertIn("s86.DECISIONS_FILE = ConstantRecord()", src)

    def test_pattern_lookups(self):
        w.swap()
        src = (SCRIPTS / "session86_forward_build.py").read_text()
        patterns = re.findall(r'expected_hash_from_decisions\(r"(.*)"\)', src)
        self.assertEqual(len(patterns), 2)
        self.assertEqual(w.s86.expected_hash_from_decisions(patterns[0]), w.p91.TRAINING_SET_SHA256)
        self.assertEqual(w.s86.expected_hash_from_decisions(patterns[1]), w.MANIFEST_SHA256)

    def test_plumbings_table_lookup(self):
        # Session 86's plumbing, with no station-day: it reads F122.5's table from the stand-in and
        # checks all twelve model files against it and against manifest.json, then stops for lack of
        # rows to compare. No network, no prediction.
        w.swap()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            w.s86.plumbing(w.s86.load_airports(), [], {}, {})
        self.assertEqual(out.getvalue().count("equals F122.5 and manifest.json: True"), 12)
        self.assertNotIn("False", out.getvalue())

    def test_plumbing_stops_on_a_wrong_value(self):
        w.swap()
        real = dict(w.F122_5_MODELS)
        self.addCleanup(w.F122_5_MODELS.update, real)
        rows, bdlrt, b = real["EGLC"]
        w.F122_5_MODELS["EGLC"] = (rows, "0" * 64, b)
        with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit):
            w.s86.plumbing(w.s86.load_airports(), [], {}, {})

    def test_check_mode(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = w.main(["--check"])
        self.assertEqual(code, 0)
        self.assertIn("CHECK: PASS", out.getvalue())
        self.assertEqual(out.getvalue().count("equal to the constant and to manifest.json: True"), 12)

    def test_without_the_swap_the_lookup_fails(self):
        # D96.3: F122 is archived, so session 86's lookup on the live file finds nothing.
        src = (SCRIPTS / "session86_forward_build.py").read_text()
        pattern = re.findall(r'expected_hash_from_decisions\(r"(.*)"\)', src)[0]
        with self.assertRaises(SystemExit):
            w.s86.expected_hash_from_decisions(pattern)


if __name__ == "__main__":
    unittest.main()
