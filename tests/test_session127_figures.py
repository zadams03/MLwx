"""Session 127's figure script (DECISIONS D121.5): its input constants, its gate, and the
recorded values and dates it holds. Offline; writes nothing inside the repo.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import hashlib
import importlib.util
import os
import re
import subprocess
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "session127_readme_figures.py"

spec = importlib.util.spec_from_file_location("session127_readme_figures", SCRIPT)
fig = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fig)


def entry(label):
    """The text of one record entry (from the line that starts it to the next '---'), looked up in
    DECISIONS.md and then DECISIONS-archive.md. Returns (text with line breaks joined, section heading)."""
    for name in ("DECISIONS.md", "DECISIONS-archive.md"):
        lines = (ROOT / name).read_text(encoding="utf-8").split("\n")
        for i, ln in enumerate(lines):
            if ln.startswith(f"**{label}. "):
                j = i
                while j < len(lines) and lines[j] != "---":
                    j += 1
                heading = next(lines[k] for k in range(i, -1, -1) if lines[k].startswith("## "))
                return " ".join(" ".join(lines[i:j]).split()), heading
    raise AssertionError(f"entry {label} not found")


class Inputs(unittest.TestCase):
    def test_every_input_constant_equals_the_file(self):
        for rel, want in fig.INPUTS.items():
            got = hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()
            self.assertEqual(got, want, rel)

    def test_verdicts_constant_equals_F150_4(self):
        text, _ = entry("F150")
        self.assertIn(fig.INPUTS[fig.VERDICTS], text)

    def test_two_session_112_constants_equal_its_meta_file(self):
        meta = (ROOT / "data/processed/session112_analysis/analyse_meta.txt").read_text(encoding="utf-8")
        for name in ("hourly_headline.csv", "hourly_curve_skill.csv"):
            self.assertIn(fig.INPUTS[fig.S112 + name], meta, name)


class RecordedValues(unittest.TestCase):
    def test_F150_2_constants_equal_the_entry(self):
        text, _ = entry("F150")
        for output, per in fig.F150_2_RAW.items():
            for ic, (a, b) in per.items():
                m = re.search(rf"{ic} PASS ([0-9.]+), ([0-9.]+), ([0-9.]+), ([0-9.]+)", text.split(
                    "Daily maximum (n per half" if output == "hourly" else "Daily maximum (n per half")[
                        0 if output == "hourly" else 1])
                self.assertIsNotNone(m, (output, ic))
                self.assertEqual((m.group(1), m.group(3)), (a, b), (output, ic))

    def test_spec_9_5_smallest_margins(self):
        spec_text = " ".join((ROOT / "SPEC.md").read_text(encoding="utf-8").split())
        self.assertIn(f"+{fig.SPEC_9_5_SMALLEST['hourly']} percent", spec_text)
        self.assertIn(f"+{fig.SPEC_9_5_SMALLEST['daily']} percent", spec_text)

    def test_table_constants_equal_analysis_md(self):
        lines = (ROOT / "ANALYSIS.md").read_text(encoding="utf-8").split("\n")
        for head, table in (("**Table 2a. Hourly.**", fig.TABLE_2A), ("**Table 2b. Daily maximum**", fig.TABLE_2B)):
            i = next(k for k, ln in enumerate(lines) if ln.startswith(head))
            rows = [ln for ln in lines[i + 2:i + 2 + 40] if ln.startswith("|")][2:14]
            self.assertEqual(len(rows), 12)
            got = {}
            for ln in rows:
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                got[cells[0].split(" ")[0]] = tuple(cells[1:])
            self.assertEqual(got, table, head)

    def test_dates_equal_the_record_entries(self):
        d = fig.DATES
        d100, d100_heading = entry("D100")
        self.assertIn(f"before {d['train_before']}T00:00 UTC", d100)
        self.assertIn(f"look A, cycles {d['look_a'][0]}T00 to {d['look_a'][1]}T18", d100)
        self.assertIn(f"look B, cycles {d['look_b'][0]}T00 to {d['look_b'][1]}T18", d100)
        self.assertIn(d["claim_rules"], d100_heading)
        f150, _ = entry("F150")
        self.assertIn(f"Run {d['claim_look']}", f150)
        d105, d105_heading = entry("D105")
        self.assertIn(f"start at {d['live_first_cycle']} 12z", d105)
        self.assertIn(f"to {d['live_end']} 18z", d105)
        self.assertIn(d["live_rules"], d105_heading)


class Script(unittest.TestCase):
    def test_gate_passes(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, str(SCRIPT), "--gate"], capture_output=True, text=True, env=env, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("--gate: PASS", r.stdout)

    def test_alt_text_is_one_sentence_each_and_plain(self):
        self.assertEqual(set(fig.ALT), set(fig.FIGURES))
        for name, alt in fig.ALT.items():
            self.assertTrue(alt.endswith("."), name)
            self.assertEqual(alt.count(". "), 0, name)
            self.assertNotIn(chr(0x2014), alt)

    def test_committed_figures_equal_a_fresh_build(self):
        figs, _ = fig.build_all()
        for name, svg in figs.items():
            path = ROOT / "figures" / "readme" / name
            self.assertTrue(path.exists(), name)
            self.assertEqual(path.read_bytes(), svg.encode("utf-8"), name)
            self.assertNotIn(chr(0x2014), svg)

    def test_refuses_to_overwrite(self):
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        r = subprocess.run([sys.executable, str(SCRIPT), "--draw", str(ROOT / "figures" / "readme")],
                           capture_output=True, text=True, env=env, cwd=ROOT)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("written once", r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
