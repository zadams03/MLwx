"""Session 134: the frozen 80 % ranges and how the page shows them (DECISIONS D129).

- The frozen file: its SHA-256 equals `ranges.RANGES_SHA256`, the value held here and the one in
  session 134's meta file; 48 rows, the 12 airports in D103.4's order, p10 < p90 in every row.
- The freeze on made-up errors: the percentiles, the row order, and refusing to overwrite.
- The page on a made-up log: the band's ends equal corrected + P10 and corrected + P90 at a range
  airport, the y-axis takes the band in, and the daily maximum column equals the maximum read off
  the curve plus the pair; no band or column at an airport without a range; a missing or altered
  file gives no band, one status line and no exception; the "not yet verified" label is there.
- Session 133's and session 112's SHA-256 equal session 134's Step 1 values.

Offline. The page is built from made-up logs only; nothing from MLwx-live is opened (D105.6).
Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import csv
import datetime as dt
import hashlib
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # skip session 62's process restart (D93.3)

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(SCRIPTS))

import numpy as np  # noqa: E402

from mlwx import config, dailymax, page, prediction_log, ranges  # noqa: E402
from mlwx import state as state_mod  # noqa: E402

import session134_freeze_ranges as fz  # noqa: E402

# Session 134's freeze (F178), held here (D98.2, D129.4).
RANGES_SHA256 = "e8ab9438b390c3c45de0821c8823a98e2ffa9adc42d6a4f19b396af11e2c9eba"
# Session 134's Step 1, held here.
STEP1_SHA256 = {
    "session133_ranges.py": "4bbe4ceaec5c72057bba0ad8f6f744b7a634016e6fcd935412db3436d28875b2",
    "session112_analysis.py": "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab",
}
# D103.4's order.
TWELVE = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]
CSV_PATH = ROOT / "src" / "mlwx" / "data" / "gfs_ranges.csv"
META_PATH = ROOT / "data" / "processed" / "session134_ranges" / "meta.txt"

MODEL = config.GFS
AIRPORTS = config.load_airports(MODEL)
HOUR = dt.timedelta(hours=1)
CYCLE = dt.datetime(2026, 10, 12, 6)
NOW = dt.datetime(2026, 10, 12, 10, 30)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def file_rows():
    with open(CSV_PATH, newline="") as f:
        return list(csv.DictReader(f))


class FrozenFile(unittest.TestCase):
    def test_sha256_equals_the_constant_and_the_meta_file(self):
        have = sha256(CSV_PATH)
        self.assertEqual(have, RANGES_SHA256)
        self.assertEqual(ranges.RANGES_SHA256, RANGES_SHA256)
        self.assertIn(f"output src/mlwx/data/gfs_ranges.csv  rows 48  sha256 {RANGES_SHA256}\n",
                      META_PATH.read_text())

    def test_48_rows_in_the_fixed_order(self):
        rows = file_rows()
        self.assertEqual(list(rows[0]), ["airport", "output", "kind", "p10", "p90", "n"])
        want = [(ic, o, k) for ic in TWELVE for o in ("hourly", "daily_max") for k in ("range", "reference")]
        self.assertEqual([(r["airport"], r["output"], r["kind"]) for r in rows], want)
        self.assertEqual(len(rows), 48)
        self.assertEqual(fz.AIRPORTS, TWELVE)

    def test_p10_below_p90_and_floats_written_by_repr(self):
        for r in file_rows():
            with self.subTest(row=(r["airport"], r["output"], r["kind"])):
                self.assertLess(float(r["p10"]), float(r["p90"]))
                self.assertEqual(repr(float(r["p10"])), r["p10"])
                self.assertEqual(repr(float(r["p90"])), r["p90"])
                self.assertGreater(int(r["n"]), 0)

    def test_the_12_airports_are_live_airports(self):
        self.assertEqual([a.icao for a in AIRPORTS[:12]], TWELVE)

    def test_loader_gives_the_file(self):
        table = ranges.load()
        self.assertEqual(len(table), 48)
        for r in file_rows():
            self.assertEqual(table[(r["airport"], r["output"], r["kind"])], (float(r["p10"]), float(r["p90"])))


class FreezeOnMadeUpErrors(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_s134_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def errors(self):
        rng = np.random.default_rng(1)
        return {ic: {o: {k: rng.normal(size=50 + i) for k in ("reference", "range")}
                     for o in ("daily_max", "hourly")} for i, ic in enumerate(("BBBB", "AAAA"))}

    def test_pair_is_numpys_linear_10th_and_90th_percentile(self):
        self.assertEqual(fz.pair(np.arange(11.0)), (1.0, 9.0, 11))
        e = np.array([3.0, -1.0, 0.5, 7.25, 2.0, -4.0, 1.0])
        p10, p90, n = fz.pair(e)
        self.assertEqual((p10, p90), tuple(float(v) for v in np.percentile(e, [10, 90])))
        self.assertEqual(n, 7)

    def test_pair_uses_only_the_named_periods(self):
        e = np.array([0.0, 1.0, 2.0, 100.0, 200.0])
        period = np.array(["a", "a", "b", "c", "c"])
        self.assertEqual(fz.pair(e, period, ("a", "b")), (0.2, 1.8, 3))

    def test_rows_follow_the_given_airport_order_hourly_first_range_first(self):
        E = self.errors()
        rows = fz.freeze_rows(E)
        self.assertEqual([r[:3] for r in rows],
                         [(ic, o, k) for ic in ("BBBB", "AAAA") for o in ("hourly", "daily_max")
                          for k in ("range", "reference")])
        for ic, o, k, p10, p90, n in rows:
            want = np.percentile(E[ic][o][k], [10, 90])
            self.assertEqual((p10, p90, n), (float(want[0]), float(want[1]), len(E[ic][o][k])))

    def test_an_error_that_is_not_finite_stops(self):
        E = self.errors()
        E["AAAA"]["hourly"]["range"][3] = np.nan
        with self.assertRaises(SystemExit):
            fz.freeze_rows(E)

    def test_text_reads_back_to_the_same_numbers(self):
        rows = fz.freeze_rows(self.errors())
        text = fz.ranges_csv_text(rows)
        back = list(csv.reader(text.splitlines()))
        self.assertEqual(back[0], fz.COLUMNS)
        self.assertEqual([(a, o, k, float(p), float(q), int(n)) for a, o, k, p, q, n in back[1:]], rows)

    def test_write_once_refuses_to_overwrite(self):
        path = self.tmp / "sub" / "gfs_ranges.csv"
        text = fz.ranges_csv_text(fz.freeze_rows(self.errors()))
        self.assertEqual(fz.write_once(path, text), sha256(path))
        with self.assertRaises(SystemExit):
            fz.write_once(path, "other\n")
        self.assertEqual(path.read_text(), text)

    def test_the_real_freeze_refuses_because_the_file_exists(self):
        self.assertTrue(fz.OUT_CSV.exists())
        self.assertEqual(fz.OUT_CSV, CSV_PATH)
        with self.assertRaises(SystemExit):
            fz.write_once(fz.OUT_CSV, "x\n")
        self.assertEqual(sha256(CSV_PATH), RANGES_SHA256)


def made_up_rows(icao, k):
    """A made-up curve for one airport: no real value."""
    out = []
    for n in range(3, 49):
        raw = 10.0 + k / 4 + 6.0 * np.sin((n + k) / 24 * 2 * np.pi)
        out.append({"airport": icao, "cycle": CYCLE, "lead": n, "valid": CYCLE + n * HOUR, "raw_gfs": float(raw),
                    "baseline": float(raw) + 0.5, "b": 0.25, "corrected": float(raw) + 0.75, "gfs_version": "v16",
                    "model_sha256": "cd" * 32, "code_commit": "made-up",
                    "issued": CYCLE + dt.timedelta(hours=4, minutes=12)})
    return out


def sections(text):
    """{ICAO: that airport's section of the page}."""
    out = {}
    for part in text.split("<section>")[1:]:
        part = part.split("</section>")[0]
        out[re.match(r"<h2>([A-Z0-9]+)</h2>", part).group(1)] = part
    return out


def axis(svg):
    """(a, b) with pixel y = a + b * value, from the chart's horizontal grid lines and their labels."""
    ticks = re.findall(r'<line class="grid" x1="46" x2="708" y1="([\d.]+)" y2="[\d.]+"/>'
                       r'<text [^>]*text-anchor="end">(-?[\d.]+)</text>', svg)
    (y0, v0), (y1, v1) = [(float(y), float(v)) for y, v in (ticks[0], ticks[-1])]
    b = (y1 - y0) / (v1 - v0)
    return y0 - b * v0, b, min(float(v) for _, v in ticks), max(float(v) for _, v in ticks)


class PageRanges(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp(prefix="test_s134_page_"))
        cls.addClassCleanup(shutil.rmtree, cls.tmp, True)
        cls.rows = {a.icao: made_up_rows(a.icao, k) for k, a in enumerate(AIRPORTS)}
        prediction_log.write_log(prediction_log.log_path(cls.tmp, "gfs", CYCLE),
                                 [r for a in AIRPORTS for r in cls.rows[a.icao]])
        cls.state = state_mod.State("gfs")
        cls.table = ranges.load()
        cls.text = page.build_page(cls.tmp, MODEL, AIRPORTS, cls.state, NOW)
        cls.missing = page.build_page(cls.tmp, MODEL, AIRPORTS, cls.state, NOW, ranges_path=cls.tmp / "none.csv")
        altered = cls.tmp / "altered.csv"
        altered.write_bytes(CSV_PATH.read_bytes().replace(b"EGLC,hourly,range,-1.3", b"EGLC,hourly,range,-1.4", 1))
        cls.altered_path = altered
        cls.altered = page.build_page(cls.tmp, MODEL, AIRPORTS, cls.state, NOW, ranges_path=altered)

    def test_band_ends_equal_corrected_plus_p10_and_p90(self):
        for icao in ("EGLC", "KORD", "NZWN"):
            with self.subTest(airport=icao):
                p10, p90 = self.table[(icao, "hourly", "range")]
                svg = sections(self.text)[icao]
                a, b, lo, hi = axis(svg)
                pts = re.search(r'<polygon class="band" points="([^"]+)"/>', svg).group(1).split()
                ys = [float(p.split(",")[1]) for p in pts]
                rows = self.rows[icao]
                self.assertEqual(len(ys), 2 * len(rows))
                want = [a + b * (r["corrected"] + p90) for r in rows] + \
                       [a + b * (r["corrected"] + p10) for r in reversed(rows)]
                np.testing.assert_allclose(ys, want, atol=0.051)       # the page rounds to 0.1 pixel
                # The y-axis takes in the band.
                self.assertLessEqual(lo, min(r["corrected"] + p10 for r in rows))
                self.assertGreaterEqual(hi, max(r["corrected"] + p90 for r in rows))
                # The band is drawn before the two lines.
                self.assertLess(svg.index('class="band"'), svg.index('<polyline class="raw"'))
                self.assertLess(svg.index('class="band"'), svg.index('<polyline class="cor"'))

    def test_the_chart_is_given_the_hourly_range_pair(self):
        seen = {}
        real = page.chart_svg

        def spy(rows, band=None):
            seen[rows[0]["airport"]] = band
            return real(rows, band)

        with mock.patch.object(page, "chart_svg", spy):
            page.build_page(self.tmp, MODEL, AIRPORTS, self.state, NOW)
        for a in AIRPORTS:
            self.assertEqual(seen[a.icao], self.table.get((a.icao, "hourly", "range")))
        self.assertEqual(sorted(k for k, v in seen.items() if v is not None), sorted(TWELVE))

    def test_daily_maximum_column_is_the_read_off_maximum_plus_the_pair(self):
        for a in AIRPORTS[:12]:
            with self.subTest(airport=a.icao):
                p10, p90 = self.table[(a.icao, "daily_max", "range")]
                curve = {r["valid"]: r["corrected"] for r in self.rows[a.icao]}
                maxima = dailymax.daily_maxima(CYCLE, a.time_zone, curve, 3, 48)
                self.assertTrue(maxima)
                sec = sections(self.text)[a.icao]
                self.assertEqual(sec.count("<th>8-in-10 range, &#176;C</th>"), 1)
                for d, m in maxima.items():
                    self.assertIn(f"<td>{m:.1f}</td><td>{m + p10:.1f} to {m + p90:.1f}</td></tr>", sec)
                self.assertEqual(sec.count(" to "), len(maxima))

    def test_no_band_or_column_at_an_airport_without_a_range(self):
        secs, plain = sections(self.text), sections(self.missing)
        others = [a.icao for a in AIRPORTS if a.icao not in TWELVE]
        self.assertEqual(len(others), 37)
        for icao in others:
            with self.subTest(airport=icao):
                self.assertNotIn("band", secs[icao])
                self.assertNotIn("8-in-10", secs[icao])
                self.assertEqual(secs[icao], plain[icao])       # unchanged by the ranges
        self.assertEqual(self.text.count('<polygon class="band"'), 12)
        self.assertEqual(self.text.count("<th>8-in-10 range, &#176;C</th>"), 12)

    def test_not_yet_verified_label_and_the_top_note(self):
        for icao in TWELVE:
            self.assertIn('<b class="g"></b>8-in-10 range (not yet verified)</p>', sections(self.text)[icao])
        self.assertEqual(self.text.count("about 8 times in 10"), 1)
        self.assertIn("is not yet verified.</p>", self.text)
        self.assertNotIn(page.NO_RANGES, self.text)

    def test_no_percent_sign_or_accuracy_word_on_the_page(self):
        body = re.sub(r"<style>.*?</style>", "", self.text.lower(), flags=re.S)
        for word in ("%", "percent", "mae", "skill", "improvement", "better than", "coverage", "interval score"):
            self.assertNotIn(word, body)

    def test_a_missing_or_altered_file_gives_no_band_and_one_status_line(self):
        self.assertIsNone(ranges.load(self.tmp / "none.csv"))
        self.assertIsNone(ranges.load(self.altered_path))
        self.assertIsNone(ranges.load(self.tmp))                 # a folder, not a file: still no exception
        for text in (self.missing, self.altered):
            self.assertEqual(text.count("<polygon"), 0)
            self.assertNotIn("8-in-10 range,", text)
            self.assertNotIn("not yet verified", text)
            self.assertEqual(text.count(f'<p class="status">{page.NO_RANGES}</p>'), 1)
            self.assertEqual(text.count("<svg"), len(AIRPORTS))
        self.assertEqual(self.missing, self.altered)

    def test_without_ranges_the_sections_are_as_before_session_134(self):
        """With no table, an airport's chart and table have no trace of the ranges."""
        sec = sections(self.missing)["EGLC"]
        self.assertIn('<p class="legend"><b></b>corrected<b class="r"></b>raw GFS</p>', sec)
        self.assertIn("<th>Corrected max, &#176;C</th></tr>", sec)
        self.assertIn('aria-label="Raw GFS and corrected 2 m temperature, degrees C">', sec)

    def test_write_page_never_stops_on_a_bad_ranges_file(self):
        out = page.write_page(self.tmp, MODEL, AIRPORTS, self.state, NOW, ranges_path=self.altered_path)
        self.assertEqual(out.read_text(), self.altered)


class ImportedScripts(unittest.TestCase):
    def test_sha256_equal_step_1(self):
        self.assertEqual(fz.IMPORTED_SHA256, STEP1_SHA256)
        for name, want in STEP1_SHA256.items():
            with self.subTest(script=name):
                self.assertEqual(sha256(SCRIPTS / name), want)

    def test_meta_records_this_script(self):
        self.assertIn(f"script SHA-256 {sha256(SCRIPTS / 'session134_freeze_ranges.py')}\n", META_PATH.read_text())


if __name__ == "__main__":
    unittest.main()
