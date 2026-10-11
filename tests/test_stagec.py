"""Stage C checks added in session 104 (DECISIONS D98.2, D98.10, D97, D98.5)
and session 105 (D99.3, D99.5), and session 106 (D100.3 to D100.6, D98.2).
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
import session105_dailymax_cv as s105  # noqa: E402
import session106_claim_table as s106t  # noqa: E402
import session106_claim_look as s106l  # noqa: E402


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


class DailyMaxConstants(unittest.TestCase):
    """D98.2: session 105's recorded SHA-256 constants equal the values in F147."""

    def test_s104_script_sha(self):
        m = re.search(r"`scripts/session104_curve_cv\.py` \(`([0-9a-f]{64})`\)", entry_text("F147"))
        self.assertIsNotNone(m)
        self.assertEqual(s105.S104_SCRIPT_SHA256, m.group(1))

    def test_s104_days_sha(self):
        m = re.search(r"`data/processed/session104_dailymax_days\.csv` \([\d,]+ rows, `([0-9a-f]{64})`\)",
                      entry_text("F147"))
        self.assertIsNotNone(m)
        self.assertEqual(s105.S104_DAYS_SHA256, m.group(1))


class DailyMaxPeakHour(unittest.TestCase):
    """D99.3(b) on a made-up day: a tie gives the earlier hour; gfs_tmax is the
    highest tmax2m_c over the hours, not the value at the peak hour."""

    def test_peak_and_gfs_tmax(self):
        c = dt.datetime(2024, 1, 14, 18)
        hours = [c + dt.timedelta(hours=n) for n in (5, 6, 7, 8)]
        temps = {5: 10.0, 6: 12.5, 7: 12.5, 8: 11.0}
        tmaxs = {5: 16.0, 6: 13.0, 7: 14.0, 8: 12.0}
        x_map = {(c, n): [temps[n], 0.1, 0.2, 30.0, 10.0, 2.0, 5.0, 100.0, -1.0] for n in temps}
        tmax = {(c, n): v for n, v in tmaxs.items()}
        feats, raw_max, gfs_tmax, p_lead, tie, why = s105.day_inputs(c, hours, x_map, tmax)
        self.assertEqual(p_lead, 6)
        self.assertTrue(tie)
        self.assertEqual(raw_max, 12.5)
        self.assertEqual(gfs_tmax, 16.0)
        self.assertNotEqual(gfs_tmax, tmaxs[p_lead])
        self.assertEqual(feats, [12.5, 16.0, 0.1, 0.2, 30.0, 10.0, 2.0, 5.0, 100.0, -1.0])
        self.assertEqual(why, "")


class DailyMaxTrainingDay(unittest.TestCase):
    """D99.3(e), D89.3: a training day's last hour is valid before T0."""

    def test_rule(self):
        t0 = dt.datetime(2024, 8, 1, 0, 0)
        self.assertTrue(s105.training_day(dt.datetime(2024, 7, 31, 23, 0), t0))
        self.assertFalse(s105.training_day(dt.datetime(2024, 8, 1, 0, 0), t0))


class DailyTracker(unittest.TestCase):
    """D99.5: EGLC in winter, cycles at 18z the evening before each day, error
    1.0 each day: corrections 0, 0, 0.02, 0.0396; the day before is never used."""

    def test_eglc_winter(self):
        days = []
        for d in (1, 2, 3, 4):
            s, _, hours = s104c.local_day(dt.date(2024, 1, d), s104c.TZ["EGLC"])
            c = s104c.day_cycle(s)
            self.assertEqual(c, dt.datetime(2024, 1, d - 1, 18) if d > 1 else dt.datetime(2023, 12, 31, 18))
            days.append((c, hours[-1], 11.0, 10.0))
        out, _ = s105.daily_track(days)
        for got, want in zip([o[0] for o in out], [0.0, 0.0, 0.02, 0.0396]):
            self.assertAlmostEqual(got, want, places=12)
        for i, (b, fc2, used, latest) in enumerate(out):
            self.assertAlmostEqual(fc2, 10.0 + b, places=12)
            self.assertTrue(latest is None or latest < days[i][0])
            if i > 0:
                self.assertNotEqual(latest, days[i - 1][1])


class ClaimHourlyPersistence(unittest.TestCase):
    """D100.5: hourly persistence uses the observation k days before the valid
    time, k the smallest whole number of days before the cycle; a missing
    observation gives none, never an older one."""

    def test_leads(self):
        c = dt.datetime(2024, 1, 10, 0)
        start = c - dt.timedelta(days=5)
        # every hour's made-up observation is its hour count from start, so each value names its hour
        obs = {start + dt.timedelta(hours=i): float(i) for i in range(0, 24 * 8)}
        for n, k in ((3, 1), (23, 1), (24, 2), (47, 2), (48, 3)):
            with self.subTest(lead=n):
                v = c + dt.timedelta(hours=n)
                want = v - dt.timedelta(days=k)
                self.assertEqual(s106l.persistence_k(c, v), k)
                self.assertEqual(s106l.hourly_persistence(c, v, obs), obs[want])
                self.assertLess(want, c)
                self.assertGreaterEqual(want + dt.timedelta(days=1), c)

    def test_missing_gives_none(self):
        c = dt.datetime(2024, 1, 10, 0)
        v = c + dt.timedelta(hours=3)
        obs = {v - dt.timedelta(days=1): None, v - dt.timedelta(days=2): 5.0}
        self.assertIsNone(s106l.hourly_persistence(c, v, obs))
        del obs[v - dt.timedelta(days=1)]
        self.assertIsNone(s106l.hourly_persistence(c, v, obs))


class ClaimDailyPersistence(unittest.TestCase):
    """D100.5: daily persistence is the observed maximum of the latest local day
    whose last hour is valid before the run's cycle."""

    @staticmethod
    def full_days(tzname, days, value_of):
        obs = {}
        for d in days:
            _, _, hours = s104c.local_day(d, tzname)
            for i, h in enumerate(hours):
                obs[h] = value_of(d) + 0.01 * i
        return obs

    def check(self, st, tzname, d, cycle, want):
        s, _, _ = s104c.local_day(d, tzname)
        self.assertEqual(s104c.day_cycle(s), cycle)
        days = [d - dt.timedelta(days=k) for k in range(1, 5)]
        obs = self.full_days(tzname, days, lambda x: float(x.day))
        p, v = s106l.daily_persistence(d, cycle, tzname, obs)
        self.assertEqual(p, want)
        _, _, hours = s104c.local_day(want, tzname)
        self.assertEqual(v, max(obs[h] for h in hours))
        return obs

    def test_eglc(self):
        self.check("EGLC", s104c.TZ["EGLC"], dt.date(2024, 1, 15), dt.datetime(2024, 1, 14, 18),
                   dt.date(2024, 1, 13))

    def test_dsm(self):
        self.check("DSM", s104c.TZ["DSM"], dt.date(2024, 1, 15), dt.datetime(2024, 1, 15, 0),
                   dt.date(2024, 1, 13))

    def test_unusable_day_gives_none(self):
        tz = s104c.TZ["EGLC"]
        d, c = dt.date(2024, 1, 15), dt.datetime(2024, 1, 14, 18)
        obs = self.full_days(tz, [d - dt.timedelta(days=k) for k in range(1, 5)], lambda x: float(x.day))
        _, _, hours = s104c.local_day(dt.date(2024, 1, 13), tz)
        for h in hours[:3]:
            obs[h] = None
        p, v = s106l.daily_persistence(d, c, tz, obs)
        self.assertEqual(p, dt.date(2024, 1, 13))
        self.assertIsNone(v)


class ClaimLookAssignment(unittest.TestCase):
    """D100.4: a row or day belongs to the look of its cycle."""

    def test_cycles(self):
        for c, want in ((dt.datetime(2024, 7, 31, 18), None), (dt.datetime(2024, 8, 1, 0), "A"),
                        (dt.datetime(2025, 7, 31, 18), "A"), (dt.datetime(2025, 8, 1, 0), "B"),
                        (dt.datetime(2026, 7, 31, 18), "B")):
            with self.subTest(cycle=c):
                self.assertEqual(s106l.look_of(c), want)


class ClaimBar(unittest.TestCase):
    """D100.5, D100.6, D79.2: strictly lower on both halves; PASS, SPLIT, FAIL."""

    def test_tie_fails(self):
        self.assertFalse(s106l.half_pass(1.25, 1.25))
        self.assertTrue(s106l.half_pass(1.2499999999999998, 1.25))

    def test_both_halves_needed(self):
        raw = s106l.half_pass(1.0, 1.2)
        pers = s106l.half_pass(1.3, 1.2)
        self.assertTrue(raw)
        self.assertFalse(pers)
        self.assertFalse(s106l.look_pass(raw, pers))
        self.assertTrue(s106l.look_pass(True, True))

    def test_no_rows_cannot_pass(self):
        self.assertFalse(s106l.half_pass(None, 1.0))
        self.assertFalse(s106l.half_pass(1.0, None))

    def test_verdicts(self):
        self.assertEqual(s106l.verdict(True, True), "PASS")
        self.assertEqual(s106l.verdict(True, False), "SPLIT")
        self.assertEqual(s106l.verdict(False, True), "SPLIT")
        self.assertEqual(s106l.verdict(False, False), "FAIL")

    def test_margin(self):
        m, d = s106l.margin(0.9, 1.2)
        self.assertAlmostEqual(m, 25.0, places=12)
        self.assertAlmostEqual(d, 0.3, places=12)
        self.assertLess(s106l.margin(1.3, 1.2)[0], 0)


class ClaimTableConstants(unittest.TestCase):
    """D98.2: the look script's twelve claim-table SHA-256 equal the values in F149."""

    def test_f149(self):
        text = entry_text("F149")
        for ic, (h0, h25) in s106l.CLAIM_TABLES.items():
            with self.subTest(icao=ic):
                m = re.search(rf"{ic} `([0-9a-f]{{64}})`, `([0-9a-f]{{64}})`", text)
                self.assertIsNotNone(m)
                self.assertEqual((h0, h25), m.groups())


class ClaimElevationConstant(unittest.TestCase):
    """D100.3(b): 7.429 x height difference / 1000 at 4 decimals; KSFO's check
    (SPEC 3.4, 5.2) and the six claim constants against the table meta."""

    def test_ksfo(self):
        self.assertEqual(s106t.elevation_constant(93.47), 0.6944)
        self.assertEqual(f"{7.429 * 93.47 / 1000:.4f}", "0.6944")

    def test_claim_meta(self):
        meta = (ROOT / "data" / "processed" / "session106_claim_table.meta.txt").read_text()
        got = {sp["icao"]: sp["a"]["correction_c"] for sp in s106t.claim_specs()}
        self.assertEqual(sorted(got), sorted(s106l.CLAIM))
        for ic, v in got.items():
            with self.subTest(icao=ic):
                m = re.search(rf"^  {ic}  height_diff_m \S+  correction_c (\S+)$", meta, re.M)
                self.assertIsNotNone(m)
                self.assertEqual(float(m.group(1)), v)


if __name__ == "__main__":
    unittest.main()
