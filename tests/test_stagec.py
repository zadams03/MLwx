"""Stage C checks added in session 104 (DECISIONS D98.2, D98.10, D97, D98.5).
Offline; reads no table and writes nothing.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import datetime as dt
import re
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import session104_pull_check as s104p  # noqa: E402
import session104_curve_cv as s104c  # noqa: E402


def entry_text(entry_id):
    """One DECISIONS entry's text, from whichever file holds it (live or archive)."""
    for name in ("DECISIONS.md", "DECISIONS-archive.md"):
        text = (ROOT / name).read_text()
        m = re.search(rf"^\*\*{re.escape(entry_id)}\. ", text, re.M)
        if m:
            end = re.search(r"^## ", text[m.end():], re.M)
            return text[m.start(): m.end() + end.start() if end else len(text)]
    raise AssertionError(f"{entry_id} not found in either DECISIONS file")


class PullScriptConstant(unittest.TestCase):
    """D98.2: the script's F145 pull-script SHA-256 equals the value in F145."""

    def test_f145_pull_script_sha(self):
        m = re.search(r"Pull script SHA-256 `([0-9a-f]{64})`", entry_text("F145"))
        self.assertIsNotNone(m)
        self.assertEqual(s104p.PULL_SCRIPT_SHA256, m.group(1))


class DailyMaximumRun(unittest.TestCase):
    """D98.10(b): the run for a local day, worked out by hand."""

    CASES = [
        ("EGLC", dt.date(2024, 1, 15), dt.datetime(2024, 1, 14, 18), 6, 29),
        ("EGLC", dt.date(2024, 7, 15), dt.datetime(2024, 7, 14, 18), 5, 28),
        ("EGLC", dt.date(2024, 3, 31), dt.datetime(2024, 3, 30, 18), 6, 28),    # 23 hours
        ("EGLC", dt.date(2024, 10, 27), dt.datetime(2024, 10, 26, 18), 5, 29),  # 25 hours
        ("DSM", dt.date(2024, 1, 15), dt.datetime(2024, 1, 15, 0), 6, 29),
        ("YSDU", dt.date(2024, 1, 15), dt.datetime(2024, 1, 14, 6), 7, 30),
        ("RNO", dt.date(2024, 1, 15), dt.datetime(2024, 1, 15, 0), 8, 31),
    ]

    def test_cycle_and_leads(self):
        for st, d, cycle, first, last in self.CASES:
            with self.subTest(station=st, day=d):
                s, _, hours = s104c.local_day(d, s104c.TZ[st])
                c = s104c.day_cycle(s)
                leads = [int((h - c) / dt.timedelta(hours=1)) for h in hours]
                self.assertEqual(c, cycle)
                self.assertEqual((leads[0], leads[-1]), (first, last))
                self.assertEqual(leads, list(range(first, last + 1)))


class DailyMaximumUsable(unittest.TestCase):
    """D98.10(a), D82.8: usable hours at least the day's hours minus 2."""

    def test_24_hour_day(self):
        self.assertTrue(s104c.usable_day(24, 22))
        self.assertFalse(s104c.usable_day(24, 21))

    def test_23_hour_day(self):
        self.assertTrue(s104c.usable_day(23, 21))
        self.assertFalse(s104c.usable_day(23, 20))

    def test_25_hour_day(self):
        self.assertTrue(s104c.usable_day(25, 23))
        self.assertFalse(s104c.usable_day(25, 22))


class TrackerLongLeads(unittest.TestCase):
    """D97.6, D98.5: daily cycles, errors 1.0 each day, at leads 47 and 48."""

    def corrections(self, lead):
        rows = [(dt.datetime(2024, 1, d, 12), lead, 11.0, 10.0) for d in (1, 2, 3, 4)]
        corrected, _, latest, _ = s104c.s103.track(rows)
        for lt, r in zip(latest, rows):
            self.assertTrue(lt is None or lt < r[0])
        return [corrected[i] - r[3] for i, r in enumerate(rows)]

    def test_lead_47(self):
        for got, want in zip(self.corrections(47), [0.0, 0.0, 0.02, 0.0396]):
            self.assertAlmostEqual(got, want, places=12)

    def test_lead_48(self):
        for got, want in zip(self.corrections(48), [0.0, 0.0, 0.0, 0.02]):
            self.assertAlmostEqual(got, want, places=12)


if __name__ == "__main__":
    unittest.main()
