"""Stage G checks: the live package src/mlwx (DECISIONS D103, session 109).
Offline; writes only to temporary folders, deleted after.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import csv
import datetime as dt
import hashlib
import io
import json
import math
import os
import random
import re
import shutil
import sys
import tempfile
import unittest
import urllib.error
from fractions import Fraction
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

import eccodes as ec  # noqa: E402
import numpy as np  # noqa: E402

from mlwx import (baseline, config, dailymax, features, gfs, observations, page, prediction_log,  # noqa: E402
                  runner, tables, tracker)
from mlwx import state as state_mod  # noqa: E402

import session96_stagec_table as s96  # noqa: E402
import session97_stagec_cv as s97  # noqa: E402
import session103_bias_drift_cv as s103  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
MODEL = config.GFS
AIRPORTS = config.load_airports(MODEL)
HOUR = dt.timedelta(hours=1)


def read_csv(path, key):
    with open(path, newline="") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def entry_text(entry_id):
    """One DECISIONS entry's text, from whichever file holds it (live or archive)."""
    for name in ("DECISIONS.md", "DECISIONS-archive.md"):
        text = (ROOT / name).read_text()
        m = re.search(rf"^\*\*{re.escape(entry_id)}\. ", text, re.M)
        if m:
            end = re.search(r"^## ", text[m.end():], re.M)
            return text[m.start(): m.end() + end.start() if end else len(text)]
    raise AssertionError(f"{entry_id} not found in either DECISIONS file")


# ------------------------------------------------------------------ synthetic GRIB messages

_MSG_CACHE = {}


def make_message(field, fh, cycle, tweak=None, tweak_id=None, values=None):
    """A synthetic GFS-shaped GRIB2 message (constant field) that passes the guard unless tweaked."""
    key = (field.name, fh, cycle, tweak_id, values is None)
    if key in _MSG_CACHE:
        return _MSG_CACHE[key]
    gid = ec.codes_grib_new_from_samples("regular_ll_sfc_grib2")
    try:
        ec.codes_set(gid, "Ni", 1440)
        ec.codes_set(gid, "Nj", 721)
        ec.codes_set(gid, "latitudeOfFirstGridPointInDegrees", 90.0)
        ec.codes_set(gid, "longitudeOfFirstGridPointInDegrees", 0.0)
        ec.codes_set(gid, "latitudeOfLastGridPointInDegrees", -90.0)
        ec.codes_set(gid, "longitudeOfLastGridPointInDegrees", 359.75)
        ec.codes_set(gid, "iDirectionIncrementInDegrees", 0.25)
        ec.codes_set(gid, "jDirectionIncrementInDegrees", 0.25)
        d, c, n, s, lvl = field.ident
        ec.codes_set(gid, "discipline", d)
        ec.codes_set(gid, "dataDate", int(f"{cycle:%Y%m%d}"))
        ec.codes_set(gid, "dataTime", cycle.hour * 100)
        ec.codes_set(gid, "productDefinitionTemplateNumber", 0 if field.kind == "instant" else 8)
        ec.codes_set(gid, "parameterCategory", c)
        ec.codes_set(gid, "parameterNumber", n)
        ec.codes_set(gid, "typeOfFirstFixedSurface", s)
        ec.codes_set(gid, "scaleFactorOfFirstFixedSurface", 0)
        ec.codes_set(gid, "scaledValueOfFirstFixedSurface", lvl * 100 if s == 100 else lvl)
        ec.codes_set(gid, "stepUnits", 1)
        st, a, b = gfs.expected_steps(field.kind, fh)
        if field.kind == "instant":
            ec.codes_set(gid, "forecastTime", fh)
        else:
            ec.codes_set(gid, "forecastTime", a)
            ec.codes_set(gid, "stepType", st)
            ec.codes_set(gid, "endStep", b)
        if tweak:
            tweak(gid)
        ec.codes_set_values(gid, values if values is not None else np.full(1440 * 721, 280.0))
        msg = ec.codes_get_message(gid)
    finally:
        ec.codes_release(gid)
    _MSG_CACHE[key] = msg
    return msg


def check(field_name, fh, cycle, tweak=None, tweak_id=None, values=None):
    field = next(f for f in MODEL.fields if f.name == field_name)
    gid = ec.codes_new_from_message(make_message(field, fh, cycle, tweak, tweak_id, values))
    try:
        return gfs.check_message(gid, field, fh, cycle, AIRPORTS, MODEL.grid)
    finally:
        ec.codes_release(gid)


class FakeHttp:
    """Serves synthetic GFS files and their .idx for fetch_file / fetch_cycle."""

    def __init__(self, cycle, tweaks=None, drop_idx=()):
        self.cycle = cycle
        self.tweaks = tweaks or {}          # (field name, fh) -> (tweak function, id)
        self.drop_idx = set(drop_idx)       # (field name, fh) whose .idx line is left out
        self.files = {}
        self.requests = []

    def _file(self, fh):
        if fh in self.files:
            return self.files[fh]
        body, lines, off = b"", [], 0
        for i, f in enumerate(MODEL.live_fields(), 1):
            step = gfs.selector(f.kind, fh)
            if step is None:
                continue
            tw, tid = self.tweaks.get((f.name, fh), (None, None))
            msg = make_message(f, fh, self.cycle, tw, tid)
            if (f.name, fh) not in self.drop_idx:
                lines.append(f"{i}:{off}:d={self.cycle:%Y%m%d%H}:{f.var}:{f.level}:{step}:")
            body += msg
            off += len(msg)
        self.files[fh] = (body, ("\n".join(lines) + "\n").encode("ascii"))
        return self.files[fh]

    def get(self, url, kind="idx", byte_range=None, expected_len=None):
        self.requests.append((url, kind, byte_range))
        m = re.search(r"\.f(\d{3})(\.idx)?$", url)
        body, idx = self._file(int(m.group(1)))
        if url.endswith(".idx"):
            return idx
        a, b = byte_range.split("-")
        a = int(a)
        b = int(b) if b else len(body) - 1
        out = body[a:b + 1]
        if expected_len is not None and len(out) != expected_len:
            raise gfs.FetchError("short")
        return out


# ------------------------------------------------------------------ synthetic cycles for the runner

def synthetic_cycle(cycle, seed=1):
    """A CycleValues with plausible raw values at every airport (4 points slightly apart)."""
    rng = random.Random(f"{seed}-{cycle:%Y%m%d%H}")
    values, status = {}, {}
    base = {"t2m": 285.0, "tcdc": 40.0, "u10": 2.0, "v10": -1.0, "d2m": 280.0, "t850": 280.0,
            "dswrf": 150.0, "prmsl": 101300.0}
    for fh in range(0, 49):
        for f in MODEL.live_fields():
            if gfs.selector(f.kind, fh) is None:
                status[(fh, f.name)] = "absent by design"
                continue
            vals = []
            for a in AIRPORTS:
                centre = base[f.name] + rng.uniform(-3, 3) * (0.01 if f.name == "prmsl" else 1) \
                    * (1000 if f.name == "prmsl" else 1)
                vals += [centre + rng.uniform(-0.2, 0.2) for _ in range(4)]
            values[(fh, f.name)] = vals
            status[(fh, f.name)] = "ok"
    return gfs.CycleValues(cycle, AIRPORTS, values, status)


class FakeModels:
    manifest_sha = "ab" * 32

    def baseline(self, icao, cycle_hour, lead, x, temp):
        return temp + 0.25 + 0.001 * lead


def obs_text(station, rows):
    """IEM-style text with one report per (time, value)."""
    out = ["station,valid,lon,lat,elevation,tmpc,dwpc"]
    for t, v in rows:
        out.append(f"{station},{t:%Y-%m-%d %H:%M},0,0,0,{'M' if v is None else format(v, '.2f')},M")
    return "\n".join(out) + "\n"


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_live_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)


# ------------------------------------------------------------------ config

class ConfigTests(Case):
    def test_airports_are_the_twelve_of_d103_4_then_the_onboarded_ones(self):
        self.assertEqual([a.icao for a in AIRPORTS[:12]],
                         ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"])
        self.assertEqual([a.role for a in AIRPORTS[:12]], ["development"] * 6 + ["claim"] * 6)
        self.assertEqual([a.station for a in AIRPORTS[:12]],
                         ["EGLC", "LFPG", "DSM", "YSDU", "RNO", "SFO", "EDDM", "ORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"])
        # session 110 (D104.6, D104.7, F153): the airports that passed both rules, in the counts file's order
        with open(PROCESSED / "session110_onboard_counts.csv", newline="") as f:
            passed = [r["airport"] for r in csv.DictReader(f) if r["verdict"] == "pass"]
        self.assertEqual(len(passed), 37)
        self.assertEqual([a.icao for a in AIRPORTS[12:]], passed)
        self.assertEqual({a.role for a in AIRPORTS[12:]}, {"new"})
        self.assertNotIn("VILK", [a.icao for a in AIRPORTS])
        self.assertNotIn("MMMX", [a.icao for a in AIRPORTS])

    def test_airports_file_equals_its_committed_sources(self):
        """The package's airports file is rebuilt from the positions file, the params files and
        session90_airports.csv (F149.1, F138.2)."""
        pos = read_csv(PROCESSED / "session91_pull_airports.csv", "icao")
        a90 = read_csv(PROCESSED / "session90_airports.csv", "icao")
        corr = {}
        for p in (ROOT / "data/raw/diagnostics/session37/session37_elevation_correction_params.csv",
                  ROOT / "data/raw/diagnostics/session76/session76_elevation_correction_params.csv"):
            for r in read_csv(p, "station").values():
                corr[r["station"]] = float(r["correction_c"])
        by_icao = {a.icao: a for a in AIRPORTS}
        for st, ic in (("EGLC", "EGLC"), ("LFPG", "LFPG"), ("DSM", "KDSM"), ("YSDU", "YSDU"), ("RNO", "KRNO"),
                       ("SFO", "KSFO")):
            a, p = by_icao[ic], pos[ic]
            self.assertEqual(a.correction_c, corr[st])
            self.assertEqual((a.lat, a.lon), (float(p["lat_used"]), float(p["lon_used"])))
        for ic in ("EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"):
            a, p = by_icao[ic], pos[ic]
            self.assertEqual(a.correction_c, round(7.429 * float(a90[ic]["height_diff_m"]) / 1000.0, 4))
            self.assertEqual(a.time_zone, a90[ic]["time_zone"])
            self.assertEqual(a.station, a90[ic]["iem_id"])
        for ic, a in by_icao.items():
            p = pos[ic]
            self.assertEqual(a.indices, tuple(int(p[f"p{k}_index"]) for k in (1, 2, 3, 4)))
            self.assertEqual(a.points, tuple((float(p[f"p{k}_lat"]), float(p[f"p{k}_lon"])) for k in (1, 2, 3, 4)))
            self.assertEqual(a.weights, tuple(float(p[f"p{k}_weight"]) for k in (1, 2, 3, 4)))
            self.assertAlmostEqual(sum(a.weights), 1.0, places=12)
        self.assertEqual({"Ni": 1440, "Nj": 721, "lat_first": 90.0, "lon_first": 0.0, "lat_last": -90.0,
                          "lon_last": 359.75, "di": 0.25, "dj": 0.25}, MODEL.grid)
        row = next(iter(read_csv(PROCESSED / "session91_pull_airports.csv", "icao").values()))
        self.assertEqual({k[5:]: row[k] for k in row if k.startswith("grid_")},
                         {"Ni": "1440", "Nj": "721", "lat_first": "90.0", "lon_first": "0.0", "lat_last": "-90.0",
                          "lon_last": "359.75", "di": "0.25", "dj": "0.25"})

    def test_field_map_is_session_91s(self):
        import session91_grib_pull as p91
        self.assertEqual([(f.name, f.var, f.level, f.kind, f.ident) for f in MODEL.fields],
                         [(n, v, l, k, i) for n, v, l, k, i in p91.FIELDS])
        self.assertEqual([f.name for f in MODEL.live_fields()],
                         ["t2m", "tcdc", "u10", "v10", "d2m", "t850", "dswrf", "prmsl"])

    def test_version_table_is_v16_only(self):
        self.assertEqual(MODEL.version_of(dt.datetime(2021, 3, 22, 12)), "v16")
        self.assertEqual(MODEL.version_of(dt.datetime(2026, 10, 12, 6)), "v16")
        with self.assertRaises(ValueError):
            MODEL.version_of(dt.datetime(2021, 3, 22, 6))
        self.assertEqual(len(MODEL.versions), 1)

    def test_unknown_model(self):
        with self.assertRaises(KeyError):
            config.get_model("ecmwf")

    def test_file_url(self):
        self.assertEqual(MODEL.file_url(dt.datetime(2026, 10, 12, 6), 5),
                         "https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.20261012/06/atmos/gfs.t06z.pgrb2.0p25.f005")


# ------------------------------------------------------------------ the GRIB adapter and its guard

class IdxTests(Case):
    IDX = ("1:0:d=2026101206:PRMSL:mean sea level:anl:\n"
           "2:100:d=2026101206:TMP:2 m above ground:anl:\n"
           "3:250:d=2026101206:TMP:850 mb:anl:\n"
           "4:400:d=2026101206:DSWRF:surface:0-6 hour ave fcst:\n")

    def test_selector_and_steps(self):
        self.assertEqual(gfs.selector("instant", 0), "anl")
        self.assertEqual(gfs.selector("instant", 7), "7 hour fcst")
        self.assertIsNone(gfs.selector("avg", 0))
        self.assertEqual(gfs.selector("avg", 6), "0-6 hour ave fcst")
        self.assertEqual(gfs.selector("avg", 7), "6-7 hour ave fcst")
        self.assertEqual(gfs.selector("avg", 26), "24-26 hour ave fcst")
        self.assertEqual(gfs.selector("max", 12), "6-12 hour max fcst")
        self.assertEqual(gfs.expected_steps("instant", 5), ("instant", 5, 5))
        self.assertEqual(gfs.expected_steps("avg", 26), ("avg", 24, 26))
        self.assertEqual([gfs.window_start(n) for n in (1, 6, 7, 12, 13, 24, 25)], [0, 0, 6, 6, 12, 18, 24])

    def test_find_range(self):
        rows = gfs.parse_idx(self.IDX)
        cycle = dt.datetime(2026, 10, 12, 6)
        self.assertEqual(gfs.find_range(rows, "TMP", "2 m above ground", "anl", cycle)[:2], ("100-249", 150))
        self.assertEqual(gfs.find_range(rows, "DSWRF", "surface", "0-6 hour ave fcst", cycle)[:2], ("400-", None))

    def test_find_range_missing_or_wrong_run_is_a_stop(self):
        rows = gfs.parse_idx(self.IDX)
        with self.assertRaises(gfs.GuardStop):
            gfs.find_range(rows, "TMP", "2 m above ground", "3 hour fcst", dt.datetime(2026, 10, 12, 6))
        with self.assertRaises(gfs.GuardStop):
            gfs.find_range(rows, "TMP", "2 m above ground", "anl", dt.datetime(2026, 10, 12, 12))


class GuardTests(Case):
    """D103.10: an altered message key makes the cycle stop."""
    CYCLE = dt.datetime(2026, 10, 12, 6)

    def test_good_messages_pass_for_every_live_field_and_kind_of_step(self):
        for f in MODEL.live_fields():
            for fh in (0, 5, 26, 48):
                if gfs.selector(f.kind, fh) is None:
                    continue
                vals = check(f.name, fh, self.CYCLE)
                self.assertEqual(len(vals), 4 * len(AIRPORTS))
                self.assertEqual(set(vals), {280.0})

    def test_values_are_read_by_grid_index_in_airport_order(self):
        v = np.arange(1440 * 721, dtype=float)
        got = check("t2m", 5, self.CYCLE, values=v)
        want = [float(v[i]) for a in AIRPORTS for i in a.indices]
        self.assertEqual(got, want)

    def _stops(self, name, fh, tweak, tid):
        with self.assertRaises(gfs.GuardStop, msg=tid):
            check(name, fh, self.CYCLE, tweak, tid)

    def test_each_altered_key_stops(self):
        cases = [
            ("t2m", 5, lambda g: ec.codes_set(g, "parameterNumber", 1), "parameterNumber"),
            ("t2m", 5, lambda g: ec.codes_set(g, "parameterCategory", 1), "parameterCategory"),
            ("t2m", 5, lambda g: ec.codes_set(g, "discipline", 10), "discipline"),
            ("t2m", 5, lambda g: ec.codes_set(g, "typeOfFirstFixedSurface", 1), "typeOfFirstFixedSurface"),
            ("t2m", 5, lambda g: ec.codes_set(g, "scaledValueOfFirstFixedSurface", 10), "level"),
            ("t850", 5, lambda g: ec.codes_set(g, "scaledValueOfFirstFixedSurface", 70000), "level 700"),
            ("t2m", 5, lambda g: ec.codes_set(g, "dataTime", 1200), "dataTime"),
            ("t2m", 5, lambda g: ec.codes_set(g, "dataDate", 20261013), "dataDate"),
            ("t2m", 5, lambda g: ec.codes_set(g, "forecastTime", 6), "validity (step 6 for f005)"),
            ("t2m", 5, lambda g: ec.codes_set(g, "Ni", 720), "Ni"),
            ("t2m", 5, lambda g: ec.codes_set(g, "iDirectionIncrementInDegrees", 0.5), "grid increment"),
            ("dswrf", 26, lambda g: ec.codes_set(g, "startStep", 18), "avg window start"),
            ("dswrf", 26, lambda g: ec.codes_set(g, "stepType", "instant"), "stepType"),
        ]
        for name, fh, tweak, tid in cases:
            with self.subTest(tid):
                try:
                    self._stops(name, fh, tweak, tid)
                except ec.CodesInternalError:
                    self.skipTest("eccodes refused to build the altered message")

    def test_a_missing_value_at_an_airport_stops(self):
        v = np.full(1440 * 721, 280.0)
        v[AIRPORTS[3].indices[2]] = 9999.0

        def tweak(g):
            ec.codes_set(g, "bitmapPresent", 1)
            ec.codes_set(g, "missingValue", 9999.0)

        with self.assertRaises(gfs.GuardStop):
            check("t2m", 5, self.CYCLE, tweak, "bitmap", values=v)

    def test_a_message_that_is_not_grib_stops(self):
        field = MODEL.fields[0]
        # the adapter turns an unreadable message into a stop
        http = FakeHttp(self.CYCLE)
        http._file(5)
        body, idx = http.files[5]
        http.files[5] = (b"x" * len(body), idx)
        with self.assertRaises((gfs.GuardStop, gfs.FetchError)):
            gfs.fetch_file(http, MODEL, AIRPORTS, self.CYCLE, 5)
        self.assertIsNotNone(field)


class FetchFileTests(Case):
    CYCLE = dt.datetime(2026, 10, 12, 6)

    def test_fetch_file_reads_each_live_field(self):
        http = FakeHttp(self.CYCLE)
        values, status = gfs.fetch_file(http, MODEL, AIRPORTS, self.CYCLE, 5)
        self.assertEqual(sorted(k[1] for k in values), sorted(f.name for f in MODEL.live_fields()))
        self.assertTrue(all(s == "ok" for s in status.values()))
        self.assertEqual(sum(1 for _, k, _ in http.requests if k == "idx"), 1)
        self.assertEqual(sum(1 for _, k, _ in http.requests if k == "message"), 8)

    def test_f000_has_no_radiation_by_design(self):
        values, status = gfs.fetch_file(FakeHttp(self.CYCLE), MODEL, AIRPORTS, self.CYCLE, 0)
        self.assertEqual(status[(0, "dswrf")], "absent by design")
        self.assertNotIn((0, "dswrf"), values)

    def test_a_missing_idx_line_stops_the_cycle(self):
        http = FakeHttp(self.CYCLE, drop_idx=[("d2m", 5)])
        with self.assertRaises(gfs.GuardStop):
            gfs.fetch_file(http, MODEL, AIRPORTS, self.CYCLE, 5)

    def test_a_message_of_the_wrong_field_stops_the_cycle(self):
        t2m = next(f for f in MODEL.fields if f.name == "t2m")
        tw = {("tcdc", 5): (None, None)}
        http = FakeHttp(self.CYCLE, tweaks=tw)
        http._file(5)
        body, idx = http.files[5]
        # swap the first two messages' bytes: idx still says TMP first
        m0 = make_message(t2m, 5, self.CYCLE)
        m1 = make_message(next(f for f in MODEL.fields if f.name == "tcdc"), 5, self.CYCLE)
        self.assertEqual(len(m0), len(m1))
        http.files[5] = (m1 + m0 + body[len(m0) * 2:], idx)
        with self.assertRaises(gfs.GuardStop):
            gfs.fetch_file(http, MODEL, AIRPORTS, self.CYCLE, 5)

    def test_fetch_cycle_stops_on_one_altered_message(self):
        tw = {("u10", 2): (lambda g: ec.codes_set(g, "parameterNumber", 3), "u10-as-v10")}
        http = FakeHttp(self.CYCLE, tweaks=tw)
        with self.assertRaises(gfs.GuardStop):
            gfs.fetch_cycle(MODEL, AIRPORTS, self.CYCLE, http=http, workers=2, hours=[0, 1, 2])

    def test_fetch_cycle_returns_values_for_every_hour(self):
        cv = gfs.fetch_cycle(MODEL, AIRPORTS, self.CYCLE, http=FakeHttp(self.CYCLE), workers=2, hours=[0, 1, 2])
        self.assertEqual(sorted({k[0] for k in cv.values}), [0, 1, 2])
        self.assertEqual(cv.point_values("KSFO", 1, "t2m"), [280.0] * 4)
        self.assertEqual(list(cv.airport_view("EGLC")[(2, "prmsl")]), [280.0] * 4)


class HttpTests(Case):
    class Resp:
        def __init__(self, status, body):
            self.status, self._body = status, body

        def read(self):
            return self._body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def http(self):
        return gfs.Http(sleep=lambda s: None, retries=3)

    def test_retries_a_503_then_succeeds(self):
        calls = [urllib.error.HTTPError("u", 503, "x", {}, None), self.Resp(200, b"abc")]

        def fake(req, timeout=None):
            r = calls.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(self.http().get("http://x/f.idx"), b"abc")
        self.assertEqual(calls, [])

    def test_a_404_is_a_fetch_error_at_once(self):
        n = []

        def fake(req, timeout=None):
            n.append(1)
            raise urllib.error.HTTPError("u", 404, "x", {}, None)

        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(gfs.FetchError):
                self.http().get("http://x/f.idx")
        self.assertEqual(len(n), 1)

    def test_a_short_or_broken_body_is_retried_then_fails(self):
        n = []

        def fake(req, timeout=None):
            n.append(1)
            return self.Resp(206, b"GRIBxxxx")

        with mock.patch("urllib.request.urlopen", fake):
            with self.assertRaises(gfs.FetchError):
                self.http().get("http://x/f", "message", "0-99", 100)
            self.assertEqual(len(n), 4)
            n.clear()
            with self.assertRaises(gfs.FetchError):
                self.http().get("http://x/f", "message", "0-7", 8)     # right length, no 7777
            self.assertEqual(len(n), 4)

    def test_range_needs_a_206(self):
        with mock.patch("urllib.request.urlopen", lambda req, timeout=None: self.Resp(200, b"abc")):
            with self.assertRaises(gfs.FetchError):
                self.http().get("http://x/f", "idx", "0-2")

    def test_network_errors_are_retried(self):
        calls = [urllib.error.URLError("down"), TimeoutError("slow"), self.Resp(200, b"ok")]

        def fake(req, timeout=None):
            r = calls.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(self.http().get("http://x/f.idx"), b"ok")


# ------------------------------------------------------------------ the feature arithmetic

class FeatureArithmetic(Case):
    def test_r_and_t_inputs(self):
        self.assertIsNone(features.r_inputs(0))
        self.assertIsNone(features.r_inputs(1))
        self.assertEqual([features.r_inputs(n) for n in (2, 3, 7, 8, 24, 25, 26)],
                         [[2], [3, 1], [7, 6, 5], [8], [24, 22], [25, 24, 23], [26]])
        self.assertEqual([features.t_inputs(n) for n in (0, 1, 2)], [None] * 3)
        self.assertEqual(features.t_inputs(3), [3, 0])

    def test_r_recovers_the_two_hour_mean_exactly_at_every_lead(self):
        """D88.5(b), on a made-up hourly series, in exact fractions, leads 2 to 48."""
        h = {k: Fraction((37 * k * k + 11 * k) % 997, 7) + Fraction(k, 3) for k in range(1, 49)}
        a = {}
        for n in range(1, 49):
            w = features.window_start(n)
            a[n] = sum(h[k] for k in range(w + 1, n + 1)) / (n - w)
        for n in range(2, 49):
            got = features.r_raw(n, {k: a[k] for k in features.r_inputs(n)})
            self.assertEqual(got, (h[n - 1] + h[n]) / 2, n)

    def test_r_and_t_equal_session_96s(self):
        rng = random.Random(5)
        for n in range(2, 49):
            a = {k: rng.uniform(0, 900) for k in range(0, 49)}
            if features.r_inputs(n):
                self.assertEqual(features.r_value(n, a), s96.r_value(n, a))
            p = {k: rng.uniform(98000, 103000) for k in range(0, 49)}
            if features.t_inputs(n):
                self.assertEqual(features.t_value(n, p), s96.t_value(n, p))

    def test_bilinear_hand_case(self):
        pts = [(10.0, 20.25), (10.0, 20.0), (10.25, 20.25), (10.25, 20.0)]
        # position at the middle of the box: every weight 0.25
        self.assertAlmostEqual(features.bilinear_stored(pts, 10.125, 20.125, [1.0, 2.0, 3.0, 4.0]), 2.5, places=12)
        # on a corner: that corner's value
        self.assertAlmostEqual(features.bilinear_stored(pts, 10.0, 20.0, [1.0, 2.0, 3.0, 4.0]), 2.0, places=12)
        # a negative longitude is shifted by 360 (G6)
        pts2 = [(10.0, 340.25), (10.0, 340.0), (10.25, 340.25), (10.25, 340.0)]
        self.assertAlmostEqual(features.bilinear_stored(pts2, 10.125, -19.875, [1.0, 2.0, 3.0, 4.0]), 2.5, places=12)
        with self.assertRaises(ValueError):
            features.bilinear_stored([(1.0, 1.0)] * 4, 1.0, 1.0, [1, 2, 3, 4])

    def test_bilinear_equals_session_91s(self):
        import session91_grib_pull as p91
        rng = random.Random(9)
        for a in AIRPORTS:
            vals = [rng.uniform(250, 310) for _ in range(4)]
            p = {"lat": a.lat, "lon": a.lon, "pts": list(a.points)}
            self.assertEqual(features.bilinear_stored(a.point_list, a.lat, a.lon, vals), p91.bilinear_stored(p, vals))

    def test_columns_and_settings_equal_the_record(self):
        self.assertEqual(features.G15, s97.G15)
        self.assertEqual(tables.COLUMNS, s97.TABLE_COLUMNS)
        self.assertEqual(tables.COLUMNS, s96.COLUMNS)
        self.assertEqual(features.GRIB_COLS, s96.GRIB_COLS)
        self.assertEqual(baseline.LGB_PARAMS, s97.LGB_PARAMS)

    def test_build_row_equals_session_96s_make_row(self):
        """The port against the reference, over random inputs, every lead 0 to 48, several availability patterns."""
        rng = random.Random(11)
        cycle = dt.datetime(2023, 7, 12, 6)
        for trial in range(6):
            a = AIRPORTS[trial % len(AIRPORTS)]
            val, stat = {}, {}
            for fh in range(0, 49):
                for f in MODEL.fields:
                    key = (fh, f.name)
                    if gfs.selector(f.kind, fh) is None:
                        stat[key] = "absent by design"
                        continue
                    stat[key] = "ok" if rng.random() > (0.0 if trial < 3 else 0.02) else "check failed"
                    if stat[key] == "ok":
                        base = {"t2m": 285, "tcdc": 40, "u10": 2, "v10": -1, "d2m": 280, "t850": 280, "dswrf": 150,
                                "prmsl": 101300, "tmax2m": 288, "tmin2m": 281}[f.name]
                        val[key] = base + rng.uniform(-5, 5)
            in_plans = [set(range(0, 49)), set(range(0, 25)), set(range(25, 49)), set(range(3, 40))]
            for in_plan in in_plans:
                for n in sorted(in_plan):
                    out, reason, used = features.build_row(a, cycle, n, in_plan, val, stat)
                    line, complete = tables.table_line(a.station, cycle, n, out, None, None, False)
                    ref_a = {"correction_c": a.correction_c, "lead": 24}
                    ref_tally = {}
                    ref = s96.make_row(a.station, ref_a, cycle, n, in_plan,
                                       {k: v for k, v in val.items() if k[0] in in_plan}, stat,
                                       ([], []), {}, {"ties": 0}, ref_tally)
                    whole = False
                    ref_fields = ref.split(",")
                    # the reference row carries the same station..complete columns; compare all but the
                    # last four (observation, its time, whole-file flag, complete case), which need data we pass empty
                    self.assertEqual(line.split(",")[:-4], ref_fields[:-4], (trial, n, sorted(in_plan)[:2]))
                    self.assertFalse(whole)

    def test_feature_vector(self):
        out = {c: 1.0 for c in features.G15}
        self.assertEqual(features.feature_vector(out), [1.0] * 9)
        out["dswrf_2h_wm2"] = None
        self.assertIsNone(features.feature_vector(out))

    def test_airport_values_skips_not_ok_and_rejects_non_finite(self):
        a = AIRPORTS[0]
        raw = {(1, "t2m"): [280.0] * 4, (1, "tcdc"): [1.0] * 4}
        out = features.airport_values(a, raw, {(1, "t2m"): "ok", (1, "tcdc"): "check failed"})
        self.assertEqual(list(out), [(1, "t2m")])
        with self.assertRaises(ValueError):
            features.airport_values(a, {(1, "t2m"): [280.0, float("nan"), 1.0, 2.0]})


class TableFormat(Case):
    def test_fmt_and_bytes_equal_session_96s(self):
        for v in (None, True, False, 0.1, 1e-7, 3, "x", -0.0):
            self.assertEqual(tables.fmt(v), s96.fmt(v))
        lines = ["a,b", "1,2"]
        self.assertEqual(tables.table_bytes(lines), s96.table_bytes(lines))

    def test_write_new_file_never_overwrites(self):
        p = self.tmp / "t.csv.gz"
        tables.write_new_file(p, b"one")
        with self.assertRaises(FileExistsError):
            tables.write_new_file(p, b"two")
        self.assertEqual(p.read_bytes(), b"one")
        self.assertEqual(sorted(x.name for x in self.tmp.iterdir()), ["t.csv.gz"])

    def test_round_trip_through_read_table_rows(self):
        a = AIRPORTS[0]
        cycle = dt.datetime(2023, 7, 12, 6)
        out = {c: 1.5 for c in features.GRIB_COLS}
        out["temperature_grib_c"] = out["temp"] = 12.25
        lines = [",".join(tables.COLUMNS)]
        l1, c1 = tables.table_line(a.station, cycle, 7, out, 11.0, cycle + 7 * HOUR, False)
        l2, c2 = tables.table_line(a.station, cycle, 8, dict(out, dswrf_2h_wm2=None), 11.5, None, False)
        lines += [l1, l2]
        p = self.tmp / "t.csv.gz"
        p.write_bytes(tables.table_bytes(lines))
        rows = tables.read_table_rows(p, a.station)
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[0][4] and not rows[1][4])
        self.assertEqual(rows[0][5:7], (11.0, 12.25))
        with self.assertRaises(ValueError):
            tables.read_table_rows(p, "XXXX")


# ------------------------------------------------------------------ observations

class ObservationTests(Case):
    def test_iem_query_equals_the_committed_request(self):
        meta = (ROOT / "data/raw/iem_asos_EDDM_2023-01-01_2023-12-31_routine.csv.meta.txt").read_text()
        url = re.search(r"exact URL requested:\n(\S+)", meta).group(1)
        self.assertEqual(observations.iem_query("EDDM", dt.date(2023, 1, 1), dt.date(2023, 12, 31)), url)

    def test_parse_and_pair_rules(self):
        h = dt.datetime(2026, 10, 12, 12)
        text = obs_text("EGLC", [(h - dt.timedelta(minutes=20), 9.0), (h - dt.timedelta(minutes=15), 10.0),
                                 (h + dt.timedelta(minutes=10), 11.0), (h + dt.timedelta(minutes=16), 12.0)])
        rs = observations.ReportSet.from_text(text, "EGLC")
        self.assertEqual(rs.nearest(h), (11.0, h + dt.timedelta(minutes=10)))
        # exactly 15 minutes is kept (G3)
        rs2 = observations.ReportSet.from_text(obs_text("EGLC", [(h - dt.timedelta(minutes=15), 10.0)]), "EGLC")
        self.assertEqual(rs2.nearest(h)[0], 10.0)
        rs3 = observations.ReportSet.from_text(obs_text("EGLC", [(h - dt.timedelta(minutes=16), 10.0)]), "EGLC")
        self.assertEqual(rs3.nearest(h), (None, None))

    def test_a_tie_keeps_the_earlier_report_and_unusable_reports_are_skipped(self):
        h = dt.datetime(2026, 10, 12, 12)
        text = obs_text("EGLC", [(h - dt.timedelta(minutes=10), 5.0), (h + dt.timedelta(minutes=10), 6.0)])
        rs = observations.ReportSet.from_text(text, "EGLC")
        self.assertEqual(rs.nearest(h)[0], 5.0)
        self.assertEqual(rs.stats["ties"], 1)
        text = obs_text("EGLC", [(h, None), (h + dt.timedelta(minutes=14), 7.0)])
        rs = observations.ReportSet.from_text(text, "EGLC")
        self.assertEqual(rs.nearest(h)[0], 7.0)              # the unusable report at :00 is skipped (G2)
        self.assertEqual(rs.stats["no_temp"], 1)

    def test_non_finite_and_foreign_stations_are_rejected(self):
        h = dt.datetime(2026, 10, 12, 12)
        text = "station,valid,lon,lat,elevation,tmpc,dwpc\nEGLC,2026-10-12 12:00,0,0,0,nan,M\nEGLC,2026-10-12 12:05,0,0,0,8.00,M\n"
        rs = observations.ReportSet.from_text(text, "EGLC")
        self.assertEqual(rs.stats["nonfinite"], 1)
        self.assertEqual(rs.nearest(h)[0], 8.0)
        with self.assertRaises(RuntimeError):
            observations.ReportSet.from_text(obs_text("KJFK", [(h, 1.0)]), "EGLC")

    def test_repeated_timestamp_keeps_the_first(self):
        h = dt.datetime(2026, 10, 12, 12)
        rs = observations.ReportSet.from_text(obs_text("EGLC", [(h, 3.0), (h, 4.0)]), "EGLC")
        self.assertEqual(rs.nearest(h)[0], 3.0)
        self.assertEqual(rs.stats["duplicates"], 1)

    def test_live_pairing_ignores_a_repeated_timestamp_whose_values_differ(self):
        """The owner's ruling at the Step 6 stop: live pairing only; the record's first-row rule is the default."""
        h = dt.datetime(2026, 10, 12, 12)
        t10 = h - dt.timedelta(minutes=10)
        for rows in ([(t10, 21.67), (t10, None)], [(t10, None), (t10, 21.67)], [(t10, 21.67), (t10, 20.0)]):
            text = obs_text("DSM", rows)
            record = observations.ReportSet.from_text(text, "DSM")
            live = observations.ReportSet.from_text(text, "DSM", live=True)
            self.assertEqual(record.nearest(h)[0], rows[0][1])            # the record keeps the first row
            self.assertEqual(live.nearest(h), (None, None))               # live ignores the timestamp, nothing else near
            self.assertEqual(live.stats["ambiguous"], 1)
        # the nearest OTHER report within 15 minutes is used instead
        text = obs_text("DSM", [(t10, 21.67), (t10, None), (h + dt.timedelta(minutes=14), 19.5)])
        self.assertEqual(observations.ReportSet.from_text(text, "DSM", live=True).nearest(h),
                         (19.5, h + dt.timedelta(minutes=14)))
        # rows with the same value are one report, not ambiguous
        text = obs_text("DSM", [(t10, 21.67), (t10, 21.67)])
        live = observations.ReportSet.from_text(text, "DSM", live=True)
        self.assertEqual(live.nearest(h)[0], 21.67)
        self.assertEqual(live.stats["ambiguous"], 0)
        # two rows missing at one timestamp are the same (missing); the timestamp has no value either way
        text = obs_text("DSM", [(t10, None), (t10, None)])
        self.assertEqual(observations.ReportSet.from_text(text, "DSM", live=True).stats["ambiguous"], 0)

    def test_the_runner_pairs_live(self):
        import inspect
        self.assertIn("live=True", inspect.getsource(runner.bring_trackers_up))

    def test_pairing_equals_session_96s_on_random_reports(self):
        rng = random.Random(3)
        start = dt.datetime(2025, 1, 1)
        reports = []
        t = start
        while t < start + dt.timedelta(days=5):
            t += dt.timedelta(minutes=rng.choice([20, 30, 50, 60]))
            reports.append((t, None if rng.random() < 0.1 else round(rng.uniform(-5, 20), 2)))
        rs = observations.ReportSet(reports)
        times, vals = [t for t, _ in reports], [v for _, v in reports]
        cache, stats = {}, {"ties": 0}
        for k in range(120):
            v = start + k * HOUR
            ref = s96.nearest_obs(times, vals, v, cache, stats)
            self.assertEqual(rs.nearest(v), ref)

    def test_fetch_reports_retries_and_reports_failure(self):
        class R:
            status = 200

            def read(self):
                return b"station,valid\n"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        seq = [urllib.error.HTTPError("u", 503, "x", {}, None), R()]

        def fake(req, timeout=None):
            r = seq.pop(0)
            if isinstance(r, Exception):
                raise r
            return r

        with mock.patch("urllib.request.urlopen", fake):
            self.assertEqual(observations.fetch_reports("EGLC", dt.date(2026, 10, 1), dt.date(2026, 10, 2),
                                                        sleep=lambda s: None), "station,valid\n")
        with mock.patch("urllib.request.urlopen", lambda req, timeout=None: (_ for _ in ()).throw(urllib.error.URLError("x"))):
            with self.assertRaises(observations.ObsFetchError):
                observations.fetch_reports("EGLC", dt.date(2026, 10, 1), dt.date(2026, 10, 2), sleep=lambda s: None)


# ------------------------------------------------------------------ the baseline

class BaselineTests(Case):
    def rows(self, n=120, seed=2):
        rng = random.Random(seed)
        out = []
        for i in range(n):
            x = [rng.uniform(-5, 20), rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(0, 100), rng.uniform(0, 30),
                 rng.uniform(0, 8), rng.uniform(-2, 8), rng.uniform(0, 500), rng.uniform(-5, 5)]
            out.append((x, x[0], x[0] + 0.3 * x[8] + rng.gauss(0, 0.2)))
        return out

    def test_fit_predict_equals_session_97s(self):
        rows = self.rows()
        self.assertEqual(baseline.fit_predict(rows[:90], rows[90:]), s97.fit_predict(rows[:90], rows[90:]))

    def test_saved_models_predict_exactly_like_the_fitted_ones(self):
        rows = self.rows()
        m1, m2 = baseline.fit(rows[:100]), baseline.fit(rows[20:])
        data = baseline.pack_bytes("EGLC", 6, {3: m1, 4: m2})
        self.assertEqual(data, baseline.pack_bytes("EGLC", 6, {4: m2, 3: m1}))      # equal models, equal bytes
        folder = self.tmp / "models"
        folder.mkdir()
        name = baseline.pack_name("gfs", "EGLC", 6)
        (folder / name).write_bytes(data)
        text = baseline.manifest_text({name: hashlib.sha256(data).hexdigest()})
        (folder / baseline.MANIFEST_NAME).write_text(text)
        with self.assertRaises(ValueError):                       # not the product models: the constant refuses it
            baseline.ModelSet(folder, "gfs")
        ms = baseline.ModelSet(folder, "gfs", expected_manifest_sha=baseline.manifest_sha256(text))
        self.assertEqual(ms.manifest_sha, baseline.manifest_sha256(text))
        self.assertEqual(ms.check_all(), 1)
        for lead, m in ((3, m1), (4, m2)):
            want = baseline.predict(m, rows[100:])
            got = [ms.baseline("EGLC", 6, lead, r[0], r[1]) for r in rows[100:]]
            self.assertEqual(got, want)
        with self.assertRaises(KeyError):
            ms.baseline("EGLC", 12, 3, rows[0][0], rows[0][1])

    def test_a_changed_file_or_manifest_is_refused(self):
        rows = self.rows()
        data = baseline.pack_bytes("EGLC", 6, {3: baseline.fit(rows)})
        folder = self.tmp / "models"
        folder.mkdir()
        name = baseline.pack_name("gfs", "EGLC", 6)
        (folder / name).write_bytes(data)
        text = baseline.manifest_text({name: hashlib.sha256(data).hexdigest()})
        (folder / baseline.MANIFEST_NAME).write_text(text)
        with self.assertRaises(ValueError):
            baseline.ModelSet(folder, "gfs", expected_manifest_sha="0" * 64)
        (folder / name).write_bytes(data + b"x")
        with self.assertRaises(ValueError):
            baseline.ModelSet(folder, "gfs", expected_manifest_sha=baseline.manifest_sha256(text)).baseline("EGLC", 6, 3, rows[0][0], rows[0][1])

    def test_manifest_constant_is_a_sha256(self):
        self.assertRegex(baseline.MANIFEST_SHA256, r"^[0-9a-f]{64}$")

    def test_manifest_constant_equals_the_record(self):
        """D98.2: the constant equals the value in F153 (the 49-airport set, D104.9), in whichever DECISIONS
        file holds it."""
        self.assertTrue(baseline.MANIFEST_SHA256 in entry_text("F153"))

    def test_manifest_constant_equals_the_manifest_file_when_the_build_folder_is_there(self):
        manifest = ROOT.parent / "MLwx-live-build" / "models-49" / baseline.MANIFEST_NAME
        if not manifest.exists():
            self.skipTest("the live build folder is not on this machine")
        self.assertEqual(baseline.manifest_sha256(manifest.read_text()), baseline.MANIFEST_SHA256)


# ------------------------------------------------------------------ the tracker

class TrackerTests(Case):
    def rows(self, seed, n=60, lead=7):
        rng = random.Random(seed)
        out, c = [], dt.datetime(2025, 1, 1, 6)
        for _ in range(n):
            c += dt.timedelta(days=1)
            fc = rng.uniform(0, 20)
            out.append((c, lead, fc + rng.gauss(0.5, 1.0), fc))
        return out

    def test_track_equals_session_103s_exactly(self):
        for lead in (3, 23, 24, 25, 47, 48):
            rows = self.rows(lead, lead=lead)
            self.assertEqual(tracker.track(rows), s103.track(rows))

    def test_hand_case_lead_3(self):
        days = [dt.datetime(2024, 1, d, 12) for d in (1, 2, 3, 4)]
        rows = [(c, 3, 11.0, 10.0) for c in days]
        corrected, n_used, latest, b = tracker.track(rows)
        self.assertEqual(n_used, [0, 1, 2, 3])
        for got, want in zip(corrected, [10.0, 10.02, 10.0396, 10.058808]):
            self.assertAlmostEqual(got, want, places=12)
        self.assertAlmostEqual(b, 0.98 * 0.058808 + 0.02, places=12)

    def test_leads_47_and_48_use_older_errors(self):
        days = [dt.datetime(2024, 1, d, 12) for d in (1, 2, 3, 4)]
        for lead, want in ((47, [0.0, 0.0, 0.02, 0.0396]), (48, [0.0, 0.0, 0.0, 0.02])):
            corrected, n_used, latest, _ = tracker.track([(c, lead, 11.0, 10.0) for c in days])
            for got, w in zip(corrected, want):
                self.assertAlmostEqual(got - 10.0, w, places=12)
            self.assertTrue(all(lt is None or lt < c for lt, c in zip(latest, days)))

    def test_live_steps_reproduce_the_batch_exactly(self):
        """advance() fed the errors that have arrived, one cycle at a time, gives track()'s b at every cycle."""
        rows = self.rows(7, lead=24)
        corrected, n_used, latest, _ = tracker.track(rows)
        cell = tracker.Cell()
        seen = []
        for k, (c, lead, obs, fc) in enumerate(rows):
            errors = [(rc + dt.timedelta(hours=rl), ro - rf) for rc, rl, ro, rf in rows[:k]]
            tracker.advance(cell, errors, c)
            self.assertEqual(fc + cell.b, corrected[k], k)
            self.assertEqual(cell.n, n_used[k])
            self.assertEqual(cell.last_valid, latest[k])
            seen.append(cell.n)

    def test_no_error_is_used_twice_or_out_of_order(self):
        cell = tracker.Cell()
        c = dt.datetime(2024, 1, 10, 0)
        e = [(dt.datetime(2024, 1, 9, 3), 1.0), (dt.datetime(2024, 1, 9, 4), 2.0)]
        self.assertEqual(tracker.advance(cell, e, c), 2)
        b = cell.b
        self.assertEqual(tracker.advance(cell, e, c), 0)                  # the same errors again: none used
        self.assertEqual(cell.b, b)
        # a late error from before the last one applied is never used
        self.assertEqual(tracker.advance(cell, [(dt.datetime(2024, 1, 9, 3, 30), 5.0)], c), 0)
        # an error valid at or after the cycle is not used yet
        self.assertEqual(tracker.advance(cell, [(c, 5.0)], c), 0)
        self.assertEqual(tracker.advance(cell, [(c, 5.0)], c + HOUR), 1)
        self.assertEqual(cell.n, 3)

    def test_errors_are_applied_in_ascending_valid_time_whatever_the_input_order(self):
        e = [(dt.datetime(2024, 1, 9, h), float(h)) for h in (5, 3, 4)]
        a, b = tracker.Cell(), tracker.Cell()
        tracker.advance(a, e, dt.datetime(2024, 1, 10))
        tracker.advance(b, sorted(e), dt.datetime(2024, 1, 10))
        self.assertEqual(a.b, b.b)
        self.assertEqual(a.last_valid, dt.datetime(2024, 1, 9, 5))

    def test_weight_is_noaas_0_02(self):
        self.assertEqual(tracker.W, 0.02)
        self.assertEqual(tracker.W, s103.W)

    def test_rows_out_of_order_are_refused(self):
        c = dt.datetime(2024, 1, 1)
        with self.assertRaises(ValueError):
            tracker.track([(c, 3, 1.0, 1.0), (c, 3, 1.0, 1.0)])


# ------------------------------------------------------------------ the daily maximum

class DailyMaxTests(Case):
    def test_day_cycle_equals_session_104s(self):
        import session104_curve_cv as s104
        for st, d in (("EGLC", dt.date(2024, 1, 15)), ("YSDU", dt.date(2024, 1, 15)), ("RNO", dt.date(2024, 3, 10))):
            s, e, hours = dailymax.local_day(d, s104.TZ[st])
            self.assertEqual(dailymax.day_cycle(s), s104.day_cycle(s))
            self.assertEqual((s, e, hours), s104.local_day(d, s104.TZ[st]))

    def test_days_wholly_inside_a_cycle(self):
        # London is UTC+1 on 2026-10-12: leads 3..48 of the 06z run cover 09Z 10-12 to 06Z 10-14.
        days = dailymax.days_inside(dt.datetime(2026, 10, 12, 6), "Europe/London")
        self.assertEqual([d for d, _ in days], [dt.date(2026, 10, 13)])
        self.assertEqual(len(days[0][1]), 24)
        # the 00z run covers 03Z 10-12 to 00Z 10-14: London days 10-12 start 23Z 10-11 (outside), 10-13 inside
        days = dailymax.days_inside(dt.datetime(2026, 10, 12, 0), "Europe/London")
        self.assertEqual([d for d, _ in days], [dt.date(2026, 10, 13)])
        # a zone far ahead of UTC: Auckland (UTC+13 in October)
        days = dailymax.days_inside(dt.datetime(2026, 10, 12, 0), "Pacific/Auckland")
        self.assertEqual([d for d, _ in days], [dt.date(2026, 10, 13)])

    def test_clock_change_days_have_23_or_25_hours(self):
        self.assertEqual(len(dailymax.local_day(dt.date(2026, 3, 29), "Europe/London")[2]), 23)
        self.assertEqual(len(dailymax.local_day(dt.date(2026, 10, 25), "Europe/London")[2]), 25)

    def test_read_off_is_the_highest_hourly_value_and_a_hole_gives_none(self):
        cycle = dt.datetime(2026, 10, 12, 6)
        (d, hours), = dailymax.days_inside(cycle, "Europe/London")
        curve = {h: 10.0 + (k % 7) for k, h in enumerate(hours)}
        self.assertEqual(dailymax.read_off(hours, curve), 16.0)
        self.assertEqual(dailymax.daily_maxima(cycle, "Europe/London", curve), {d: 16.0})
        del curve[hours[10]]
        self.assertIsNone(dailymax.read_off(hours, curve))
        self.assertEqual(dailymax.daily_maxima(cycle, "Europe/London", curve), {})

    def test_usable_day(self):
        self.assertTrue(dailymax.usable_day(24, 22))
        self.assertFalse(dailymax.usable_day(24, 21))
        self.assertTrue(dailymax.usable_day(23, 21))
        self.assertTrue(dailymax.usable_day(25, 23))


# ------------------------------------------------------------------ the log and the state

def log_rows(cycle, airport="EGLC", leads=range(3, 49), commit="abc"):
    return [{"airport": airport, "cycle": cycle, "lead": n, "valid": cycle + n * HOUR, "raw_gfs": 10.0 + n / 10,
             "baseline": 10.5 + n / 10, "b": 0.0, "corrected": 10.5 + n / 10, "gfs_version": "v16",
             "model_sha256": "cd" * 32, "code_commit": commit, "issued": cycle + dt.timedelta(hours=4, minutes=12)}
            for n in leads]


class LogTests(Case):
    def test_path_and_columns(self):
        p = prediction_log.log_path(self.tmp, "gfs", dt.datetime(2026, 10, 12, 6))
        self.assertEqual(p, self.tmp / "log" / "2026" / "10" / "gfs_2026101206.csv")
        self.assertEqual(prediction_log.LOG_COLUMNS,
                         ["airport", "cycle_utc", "lead", "valid_utc", "raw_gfs", "baseline", "b", "corrected",
                          "gfs_version", "model_sha256", "code_commit", "issued_utc"])

    def test_written_once_and_never_overwritten(self):
        c = dt.datetime(2026, 10, 12, 6)
        p = prediction_log.log_path(self.tmp, "gfs", c)
        prediction_log.write_log(p, log_rows(c))
        before = p.read_bytes()
        with self.assertRaises(prediction_log.LogExists):
            prediction_log.write_log(p, log_rows(c, commit="other"))
        self.assertEqual(p.read_bytes(), before)
        self.assertEqual([x.name for x in p.parent.iterdir()], [p.name])      # no partial file left

    def test_floats_read_back_identically(self):
        c = dt.datetime(2026, 10, 12, 6)
        rows = log_rows(c)
        rows[0]["baseline"] = 0.1 + 0.2
        rows[0]["b"] = 1 / 3
        rows[0]["corrected"] = rows[0]["baseline"] + rows[0]["b"]
        p = prediction_log.log_path(self.tmp, "gfs", c)
        prediction_log.write_log(p, rows)
        back = prediction_log.read_log(p)
        self.assertEqual(back, rows)

    def test_logged_cycles_lists_files(self):
        for c in (dt.datetime(2026, 10, 12, 6), dt.datetime(2026, 11, 1, 18)):
            prediction_log.write_log(prediction_log.log_path(self.tmp, "gfs", c), log_rows(c))
        self.assertEqual(sorted(prediction_log.logged_cycles(self.tmp, "gfs")),
                         [dt.datetime(2026, 10, 12, 6), dt.datetime(2026, 11, 1, 18)])
        self.assertEqual(prediction_log.logged_cycles(self.tmp, "ecmwf"), {})


class StateTests(Case):
    def test_fresh_state_starts_at_zero_and_round_trips(self):
        s = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(s.cells, {})
        cell = s.cell("EGLC", 6, 3)
        self.assertEqual((cell.b, cell.last_valid, cell.n), (0.0, None, 0))
        tracker.advance(cell, [(dt.datetime(2026, 10, 11, 9), 0.7)], dt.datetime(2026, 10, 12, 6))
        s.last_cycle = dt.datetime(2026, 10, 12, 6)
        s.add_stop(dt.datetime(2026, 10, 12, 12), "guard stop: x", dt.datetime(2026, 10, 12, 16))
        state_mod.save_state(self.tmp, s)
        back = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(back.to_json(), s.to_json())
        self.assertEqual(back.cell("EGLC", 6, 3).b, cell.b)
        self.assertEqual(back.stopped(), {dt.datetime(2026, 10, 12, 12)})
        self.assertEqual([x.name for x in (self.tmp / "state").iterdir()], ["tracker_gfs.json"])

    def test_wrong_version_or_model_is_refused(self):
        s = state_mod.State("gfs")
        state_mod.save_state(self.tmp, s)
        p = state_mod.state_path(self.tmp, "gfs")
        d = json.loads(p.read_text())
        d["version"] = 99
        p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):
            state_mod.load_state(self.tmp, "gfs")


# ------------------------------------------------------------------ the runner

def fake_gfs(calls=None, fail=None):
    def fetch(model, airports, cycle):
        if calls is not None:
            calls.append(cycle)
        if fail and cycle in fail:
            raise fail[cycle]
        return synthetic_cycle(cycle)
    return fetch


def fake_obs_for(logs_root, offset=1.0, calls=None):
    """Obs for every logged baseline: baseline + offset at its valid time (2 decimals, as IEM)."""
    def fetch(station, d1, d2):
        if calls is not None:
            calls.append((station, d1, d2))
        icao = next(a.icao for a in AIRPORTS if a.station == station)
        rows = {}
        for c, p in prediction_log.logged_cycles(logs_root, "gfs").items():
            for r in prediction_log.read_log(p):
                if r["airport"] == icao:
                    rows[r["valid"]] = round(r["baseline"] + offset, 2)
        return obs_text(station, sorted(rows.items()))
    return fetch


class RunnerTests(Case):
    NOW = dt.datetime(2026, 10, 12, 10, 30)         # the 06z cycle is 4h30m old: available

    def run_at(self, now, **kw):
        kw.setdefault("models", FakeModels())
        kw.setdefault("fetch_gfs", fake_gfs())
        kw.setdefault("fetch_obs", fake_obs_for(self.tmp))
        kw.setdefault("commit", "deadbeef")
        kw.setdefault("log", lambda *a: None)
        return runner.run(self.tmp, self.tmp / "models", now, **kw)

    def test_available_cycles_are_the_past_24_hours_after_4h10m(self):
        got = runner.available_cycles(MODEL, dt.datetime(2026, 10, 12, 10, 12))
        self.assertEqual(got, [dt.datetime(2026, 10, 11, 12), dt.datetime(2026, 10, 11, 18),
                               dt.datetime(2026, 10, 12, 0), dt.datetime(2026, 10, 12, 6)])
        got = runner.available_cycles(MODEL, dt.datetime(2026, 10, 12, 10, 9))
        self.assertEqual(got[-1], dt.datetime(2026, 10, 12, 0))
        self.assertEqual(len(runner.available_cycles(MODEL, dt.datetime(2026, 10, 12, 10, 12), dt.timedelta(hours=24))), 4)

    def test_first_run_writes_one_file_with_all_airports_and_leads_and_b_zero(self):
        res = self.run_at(self.NOW, latest_only=True)
        self.assertEqual(res["issued"], [dt.datetime(2026, 10, 12, 6)])
        files = sorted((self.tmp / "log").rglob("*.csv"))
        self.assertEqual([f.name for f in files], ["gfs_2026101206.csv"])
        rows = prediction_log.read_log(files[0])
        self.assertEqual(len(rows), len(AIRPORTS) * 46)
        self.assertEqual({r["airport"] for r in rows}, {a.icao for a in AIRPORTS})
        self.assertEqual({r["lead"] for r in rows}, set(range(3, 49)))
        self.assertEqual({r["b"] for r in rows}, {0.0})
        self.assertTrue(all(r["corrected"] == r["baseline"] + r["b"] for r in rows))
        self.assertEqual({r["gfs_version"] for r in rows}, {"v16"})
        self.assertEqual({r["model_sha256"] for r in rows}, {"ab" * 32})
        self.assertEqual({r["code_commit"] for r in rows}, {"deadbeef"})
        self.assertEqual({r["issued"] for r in rows}, {self.NOW})
        self.assertTrue((self.tmp / "site" / "index.html").exists())
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(st.last_cycle, dt.datetime(2026, 10, 12, 6))
        self.assertEqual(st.last_run["status"], "ok")

    def test_a_second_run_does_nothing_and_never_touches_the_log(self):
        self.run_at(self.NOW, latest_only=True)
        f = next((self.tmp / "log").rglob("*.csv"))
        before = f.read_bytes()
        calls = []
        res = self.run_at(self.NOW, latest_only=True, fetch_gfs=fake_gfs(calls))
        self.assertEqual((res["issued"], calls), ([], []))
        self.assertEqual(res["skipped"], [dt.datetime(2026, 10, 12, 6)])
        self.assertEqual(f.read_bytes(), before)

    def test_catch_up_processes_missing_cycles_in_time_order(self):
        calls = []
        res = self.run_at(dt.datetime(2026, 10, 12, 10, 30), fetch_gfs=fake_gfs(calls))
        self.assertEqual(res["issued"], runner.available_cycles(MODEL, dt.datetime(2026, 10, 12, 10, 30)))
        self.assertEqual(calls, sorted(calls))
        self.assertEqual(len(calls), 4)

    def test_trackers_use_each_error_once_in_the_right_cells(self):
        """Cycle 00z on day 1, then 00z on day 2 (D97.6): at day 2, leads 3 to 23 hold one error, lead 24 and above none."""
        day1, day2 = dt.datetime(2026, 10, 11, 0), dt.datetime(2026, 10, 12, 0)
        self.run_at(day1 + dt.timedelta(hours=4, minutes=30), latest_only=True)
        obs_calls = []
        res = self.run_at(day2 + dt.timedelta(hours=4, minutes=30), latest_only=True,
                          fetch_obs=fake_obs_for(self.tmp, calls=obs_calls))
        self.assertEqual(res["issued"], [day2])
        log1 = {(r["airport"], r["lead"]): r for r in prediction_log.read_log(prediction_log.log_path(self.tmp, "gfs", day1))}
        log2 = prediction_log.read_log(prediction_log.log_path(self.tmp, "gfs", day2))
        for r in log2:
            first = log1[(r["airport"], r["lead"])]
            err = round(first["baseline"] + 1.0, 2) - first["baseline"]
            if r["lead"] <= 23:
                self.assertEqual(r["b"], tracker.update(0.0, err), (r["airport"], r["lead"]))
            else:
                self.assertEqual(r["b"], 0.0, (r["airport"], r["lead"]))
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(st.cells["EGLC|00|3"].n, 1)
        self.assertEqual(st.cells["EGLC|00|3"].last_valid, day1 + 3 * HOUR)
        self.assertEqual(st.cells["EGLC|00|24"].n, 0)
        self.assertEqual({c[0] for c in obs_calls}, {a.station for a in AIRPORTS})
        self.assertEqual(len(obs_calls), len(AIRPORTS))

    def test_no_observation_fetch_when_nothing_is_pending(self):
        calls = []
        self.run_at(self.NOW, latest_only=True, fetch_obs=fake_obs_for(self.tmp, calls=calls))
        self.assertEqual(calls, [])

    def test_a_missing_observation_is_skipped_not_filled(self):
        day1, day2 = dt.datetime(2026, 10, 11, 0), dt.datetime(2026, 10, 12, 0)
        self.run_at(day1 + dt.timedelta(hours=4, minutes=30), latest_only=True)
        full = fake_obs_for(self.tmp)

        def holes(station, d1, d2):
            text = full(station, d1, d2).splitlines()
            return "\n".join(l for l in text if not l.startswith(f"{station},2026-10-11 05:") ) + "\n"

        self.run_at(day2 + dt.timedelta(hours=4, minutes=30), latest_only=True, fetch_obs=holes)
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(st.cells["EGLC|00|5"].n, 0)        # valid 05Z: no report, no update
        self.assertEqual(st.cells["EGLC|00|6"].n, 1)

    def test_a_guard_stop_issues_nothing_records_it_and_later_cycles_go_on(self):
        c6, c12 = dt.datetime(2026, 10, 12, 6), dt.datetime(2026, 10, 12, 12)
        now = dt.datetime(2026, 10, 12, 16, 30)
        res = self.run_at(now, fetch_gfs=fake_gfs(fail={c6: gfs.GuardStop("t2m f005: identity changed")}))
        self.assertIn(c6, [c for c, _ in res["stopped"]])
        self.assertIn(c12, res["issued"])
        logged = prediction_log.logged_cycles(self.tmp, "gfs")
        self.assertNotIn(c6, logged)
        self.assertIn(c12, logged)
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertIn(c6, st.stopped())
        html_text = (self.tmp / "site" / "index.html").read_text()
        self.assertIn("issued nothing", html_text)
        self.assertIn("identity changed", html_text)
        # the next run does not try the stopped cycle again
        calls = []
        self.run_at(now, fetch_gfs=fake_gfs(calls))
        self.assertNotIn(c6, calls)

    def test_a_fetch_problem_waits_and_blocks_later_cycles_until_12_hours(self):
        c0, c6 = dt.datetime(2026, 10, 12, 0), dt.datetime(2026, 10, 12, 6)
        now = dt.datetime(2026, 10, 12, 10, 30)
        res = self.run_at(now, fetch_gfs=fake_gfs(fail={c0: gfs.FetchError("HTTP 404")}))
        self.assertEqual(res["issued"], [c for c in res["issued"] if c < c0])          # nothing from c0 on
        self.assertEqual(res["waiting"][0], c0)
        self.assertNotIn(c6, prediction_log.logged_cycles(self.tmp, "gfs"))
        # at c0 + 12 h the problem is final for that cycle and c6 goes ahead
        later = dt.datetime(2026, 10, 12, 12, 30)
        res = self.run_at(later, fetch_gfs=fake_gfs(fail={c0: gfs.FetchError("HTTP 404")}))
        self.assertIn(c0, [c for c, _ in res["stopped"]])
        self.assertIn(c6, res["issued"])

    def test_an_observation_fetch_error_issues_nothing_yet(self):
        day1, day2 = dt.datetime(2026, 10, 11, 0), dt.datetime(2026, 10, 12, 0)
        self.run_at(day1 + dt.timedelta(hours=4, minutes=30), latest_only=True)

        def broken(station, d1, d2):
            raise observations.ObsFetchError("IEM down")

        res = self.run_at(day2 + dt.timedelta(hours=4, minutes=30), latest_only=True, fetch_obs=broken)
        self.assertEqual(res["issued"], [])
        self.assertEqual(res["waiting"][0], day2)
        self.assertNotIn(day2, prediction_log.logged_cycles(self.tmp, "gfs"))
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertEqual(st.cells.get("EGLC|00|3").n, 0 if "EGLC|00|3" in st.cells else 0)

    def test_a_cycle_older_than_the_newest_logged_one_is_not_issued_out_of_order(self):
        c12 = dt.datetime(2026, 10, 12, 12)
        self.run_at(dt.datetime(2026, 10, 12, 16, 30), latest_only=True)         # logs the 12z cycle only
        res = self.run_at(dt.datetime(2026, 10, 12, 16, 30))                      # 00z, 06z are now older than the log
        self.assertEqual(res["issued"], [])
        self.assertEqual(res["stopped"], [])
        self.assertEqual(len(res["out_of_order"]), 3)
        self.assertTrue(all("tracker order" in why for _, why in res["out_of_order"]))
        self.assertEqual(set(prediction_log.logged_cycles(self.tmp, "gfs")), {c12})

    # D104.4: the exit code, through main(), with the fetches and the models faked.
    def main_at(self, now, fetch_gfs=None, latest_only=False):
        args = ["--root", str(self.tmp), "--models", str(self.tmp / "models"), "--now", f"{now:%Y-%m-%dT%H:%M}",
                "--commit", "deadbeef"] + (["--latest-only"] if latest_only else [])
        out = io.StringIO()
        with mock.patch.object(baseline, "ModelSet", lambda *a, **k: FakeModels()), \
                mock.patch.object(gfs, "fetch_cycle", fetch_gfs or fake_gfs()), \
                mock.patch.object(observations, "fetch_reports", fake_obs_for(self.tmp)), \
                mock.patch("sys.stdout", out):
            code = runner.main(args)
        return code, out.getvalue()

    def test_last_nights_case_a_tracker_order_skip_exits_0(self):
        """D104.3(b): 12z logged by hand, then the 18z run: 06z is in the window and older than the log, 18z is new."""
        c6, c12, c18 = (dt.datetime(2026, 10, 12, h) for h in (6, 12, 18))
        code, _ = self.main_at(dt.datetime(2026, 10, 12, 20, 0), latest_only=True)
        self.assertEqual(code, 0)
        self.assertEqual(set(prediction_log.logged_cycles(self.tmp, "gfs")), {c12})
        code, out = self.main_at(dt.datetime(2026, 10, 13, 2, 58))
        self.assertEqual(code, 0)
        self.assertEqual(set(prediction_log.logged_cycles(self.tmp, "gfs")), {c12, c18})
        self.assertIn("2026-10-12T06z: not issued: a later cycle is already in the log (tracker order)", out)
        self.assertIn("2026-10-12T18z: issued", out)
        self.assertIn("issued 1, stopped 0, not issued (tracker order) 1, waiting False", out)
        st = state_mod.load_state(self.tmp, "gfs")
        self.assertIn(c6, st.stopped())
        self.assertEqual(st.last_run["status"], "ok")
        html_text = (self.tmp / "site" / "index.html").read_text()
        self.assertIn("cycle 2026-10-12 06z issued nothing: not issued: a later cycle is already in the log", html_text)

    def test_a_guard_stop_still_exits_3(self):
        c6 = dt.datetime(2026, 10, 12, 6)
        code, out = self.main_at(self.NOW, fetch_gfs=fake_gfs(fail={c6: gfs.GuardStop("t2m f005: identity changed")}),
                                 latest_only=True)
        self.assertEqual(code, 3)
        self.assertIn("ISSUED NOTHING. guard stop", out)

    def test_a_fetch_that_never_succeeded_exits_3(self):
        c0 = dt.datetime(2026, 10, 12, 0)
        code, out = self.main_at(dt.datetime(2026, 10, 12, 12, 30), fetch_gfs=fake_gfs(fail={c0: gfs.FetchError("HTTP 404")}))
        self.assertEqual(code, 3)
        self.assertIn("gave up after 12 hours", out)

    def test_a_waiting_fetch_still_exits_2(self):
        c6 = dt.datetime(2026, 10, 12, 6)
        code, out = self.main_at(self.NOW, fetch_gfs=fake_gfs(fail={c6: gfs.FetchError("HTTP 404")}), latest_only=True)
        self.assertEqual(code, 2)
        self.assertIn("issued nothing yet, will try again", out)

    def test_incomplete_features_stop_the_cycle(self):
        def holey(model, airports, cycle):
            cv = synthetic_cycle(cycle)
            del cv.values[(30, "prmsl")]
            del cv.status[(30, "prmsl")]
            return cv

        res = self.run_at(self.NOW, latest_only=True, fetch_gfs=holey)
        self.assertEqual(res["issued"], [])
        self.assertEqual(len(res["stopped"]), 1)
        self.assertEqual(list((self.tmp / "log").rglob("*.csv")) if (self.tmp / "log").exists() else [], [])

    def test_the_runner_never_overwrites_an_existing_log_file(self):
        c = dt.datetime(2026, 10, 12, 6)
        p = prediction_log.log_path(self.tmp, "gfs", c)
        prediction_log.write_log(p, log_rows(c))
        before = p.read_bytes()
        self.run_at(self.NOW, latest_only=True)
        self.assertEqual(p.read_bytes(), before)

    def test_cli_main_runs_with_injected_models_folder_check(self):
        with self.assertRaises(FileNotFoundError):
            runner.main(["--root", str(self.tmp), "--models", str(self.tmp / "nope"), "--now", "2026-10-12T10:30"])


# ------------------------------------------------------------------ the page

class PageTests(Case):
    def build(self, version="v16", n_errors=0, stops=(), now=dt.datetime(2026, 10, 12, 10, 30)):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_live_page_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        c = dt.datetime(2026, 10, 12, 6)
        rows = []
        for a in AIRPORTS:
            rs = log_rows(c, a.icao)
            for r in rs:
                r["gfs_version"] = version
                r["corrected"] = r["baseline"] = r["raw_gfs"] + 1.0
            rows += rs
        prediction_log.write_log(prediction_log.log_path(self.tmp, "gfs", c), rows)
        st = state_mod.State("gfs")
        for a in AIRPORTS:
            for n in range(3, 49):
                st.cell(a.icao, 6, n).n = n_errors
        for cyc, why in stops:
            st.add_stop(cyc, why, now)
        return page.build_page(self.tmp, MODEL, AIRPORTS, st, now)

    def test_page_holds_every_airport_the_curve_and_the_daily_maxima(self):
        html_text = self.build()
        for a in AIRPORTS:
            self.assertIn(f"<h2>{a.icao}</h2>", html_text)
        self.assertEqual(html_text.count("<svg"), len(AIRPORTS))
        self.assertIn("cycle 2026-10-12 06z", html_text)
        self.assertIn("GFS v16", html_text)
        self.assertIn("issued 2026-10-12 10:12 UTC", html_text)
        self.assertIn("Local day (Europe/London)", html_text)
        self.assertIn("<td>2026-10-13</td>", html_text)

    def test_warming_up_flag_while_a_cell_has_fewer_than_50_errors(self):
        self.assertIn("drift warming up", self.build(n_errors=49))
        self.assertNotIn("drift warming up", self.build(n_errors=50))

    def test_v17_is_marked_not_validated(self):
        self.assertIn("not validated on v17", self.build(version="v17", n_errors=50))
        self.assertNotIn("not validated on v17", self.build(version="v16", n_errors=50))

    def test_a_stop_is_shown(self):
        text = self.build(stops=[(dt.datetime(2026, 10, 12, 12), "guard stop: t2m f005 identity changed")])
        self.assertIn("cycle 2026-10-12 12z issued nothing: guard stop: t2m f005 identity changed", text)

    def test_no_accuracy_figure_anywhere(self):
        text = self.build(n_errors=10).lower()
        body = re.sub(r"<style>.*?</style>", "", text, flags=re.S)
        for word in ("mae", "skill", "improvement", "better than", "percent", "accuracy figure is shown"):
            if word == "accuracy figure is shown":
                self.assertIn(word, body)      # the page says it shows none
            else:
                self.assertNotIn(word, body)
        self.assertNotIn("%", body)

    def test_an_empty_log_gives_a_page(self):
        st = state_mod.State("gfs")
        text = page.build_page(self.tmp, MODEL, AIRPORTS, st, dt.datetime(2026, 10, 12, 10, 30))
        self.assertIn("No cycle has been issued yet", text)
        self.assertEqual(text.count("<svg"), 0)

    def test_page_is_one_standard_library_file_with_no_external_resources(self):
        text = self.build()
        self.assertNotRegex(text, r"(src|href)=\"https?://")
        self.assertNotIn("<script", text)


# ------------------------------------------------------------------ the record

class RecordTests(Case):
    def test_d103_is_in_decisions_and_the_package_cites_its_rules(self):
        t = entry_text("D103")
        for rule in ("D103.5", "D103.6", "D103.8", "D103.10"):
            self.assertIn(rule, t)
        self.assertNotIn(chr(0x2014), t)

    def test_log_columns_are_d103_8s(self):
        t = " ".join(entry_text("D103").split())
        for col in ("airport", "cycle", "lead", "valid time", "raw GFS", "baseline", "b,", "corrected value",
                    "GFS version", "model SHA-256", "code commit", "issue time"):
            self.assertIn(col, t)
        self.assertEqual(len(prediction_log.LOG_COLUMNS), 12)


# ------------------------------------------------------------------ recorded constants and the refit

class RecordedConstants(Case):
    def test_table_hashes_equal_the_record(self):
        from mlwx import records
        f138 = entry_text("F138")
        for icao, sha in records.DEV_0_24.items():
            m = re.search(rf"`stagec_dev_{icao}\.csv\.gz` \| 195,600 \| [\d,]+ \| `([0-9a-f]{{64}})`", f138)
            self.assertIsNotNone(m, icao)
            self.assertEqual(sha, m.group(1), icao)
        f149 = entry_text("F149")
        for icao, (a, b) in records.CLAIM_TABLES.items():
            m = re.search(rf"^\s+{icao} `([0-9a-f]{{64}})`, `([0-9a-f]{{64}})`", f149, re.M)
            self.assertIsNotNone(m, icao)
            self.assertEqual((a, b), m.groups(), icao)

    def test_25_48_table_hashes_equal_session_104s_meta_and_the_meta_equals_f147(self):
        from mlwx import records
        meta = (PROCESSED / "session104_stagec_f025_048_table.meta.txt").read_bytes()
        self.assertTrue(hashlib.sha256(meta).hexdigest().startswith("27622ada"))
        self.assertTrue(hashlib.sha256(meta).hexdigest().endswith("5859"))
        self.assertIn("27622ada", entry_text("F147"))
        text = meta.decode()
        for icao, sha in records.DEV_25_48.items():
            m = re.search(rf"stagec_dev_f025_048_{icao}\.csv\.gz  rows [\d,]+  bytes [\d,]+  sha256 ([0-9a-f]{{64}})", text)
            self.assertEqual(sha, m.group(1), icao)

    def test_the_gates_script_holds_the_same_constants(self):
        import session109_gates as g
        from mlwx import records
        self.assertEqual(g.DEV_0_24, records.DEV_0_24)
        self.assertEqual(g.DEV_25_48, records.DEV_25_48)
        self.assertEqual(g.CLAIM_TABLES, records.CLAIM_TABLES)
        for a in AIRPORTS[:12]:          # the record's airports (the onboarded ones have their own tables)
            for hs in ("f000_024", "f025_048"):
                self.assertEqual(g.table_name(a, hs), records.table_name(a, hs))
                self.assertEqual(g.recorded_sha(a, hs), records.recorded_sha(a, hs))

    def test_f147_constants_in_the_gates_script(self):
        import session109_gates as g
        f147 = " ".join(entry_text("F147").split())

        def has(needle):
            self.assertTrue(needle in f147, f"not in F147: {needle}")      # never print F147 itself

        has(g.F147_SCORES_SHA256)
        has(g.F147_DAYS_SHA256)
        has(repr(g.F147_CURVE_HEADLINE_3_48))
        for key, vals in g.F147_HOURLY_3_48.items():        # F147.5, leads 3 to 48: "raw / baseline / curve" per airport
            has(" / ".join(f"{v:.4f}" for v in vals))
        for st, vals in g.F147_DAILY.items():               # F147.6: "EGLC 0.9460 / 0.8479 / 0.8410;" and the headline
            has(("KSFO" if st == "SFO" else st) + " " + " / ".join(f"{v:.4f}" for v in vals))
        has("Days: " + ", ".join(f"{'KSFO' if st == 'SFO' else st} {n:,}" for st, n in g.F147_DAYS_N.items()))
        sha = hashlib.sha256((PROCESSED / "session104_curve_cv_scores.csv").read_bytes()).hexdigest()
        self.assertEqual(sha, g.F147_SCORES_SHA256)
        sha = hashlib.sha256((PROCESSED / "session104_dailymax_days.csv").read_bytes()).hexdigest()
        self.assertEqual(sha, g.F147_DAYS_SHA256)


class RefitTests(Case):
    def synthetic_tables(self, airport, seed=4):
        """Two tiny table files for one airport: 150 daily cycles at 00z, lead 3 only."""
        rng = random.Random(seed)
        d = self.tmp / "tables"
        d.mkdir()
        for hs in ("f000_024", "f025_048"):
            lines = [",".join(tables.COLUMNS)]
            if hs == "f000_024":
                c = dt.datetime(2022, 1, 1, 0)
                for _ in range(150):
                    c += dt.timedelta(days=1)
                    out = {col: None for col in features.GRIB_COLS}
                    t = rng.uniform(-3, 20)
                    out.update({"temp": t, "temperature_grib_c": t, "season_sin": 0.1, "season_cos": 0.9,
                                "cloud_cover": rng.uniform(0, 100), "wind_speed_10m": rng.uniform(0, 30),
                                "dewpoint_depression_t2m_floored": rng.uniform(0, 8), "lapse_rate_t2_t850": rng.uniform(-2, 8),
                                "dswrf_2h_wm2": rng.uniform(0, 500), "pressure_tendency_3h_hpa": rng.uniform(-4, 4)})
                    line, complete = tables.table_line(airport.station, c, 3, out, t + rng.gauss(0.3, 0.5), c, False)
                    self.assertTrue(complete)
                    lines.append(line)
            (d / records_name(airport, hs)).write_bytes(tables.table_bytes(lines))
        return d

    def test_refit_is_deterministic_checks_its_tables_and_never_overwrites(self):
        import dataclasses
        from mlwx import records, refit
        a = AIRPORTS[0]
        small = dataclasses.replace(MODEL, cycle_hours=(0,), last_lead=3)
        d = self.synthetic_tables(a)
        real = records.recorded_sha
        with mock.patch.object(records, "recorded_sha", lambda ap, hs: tables.sha256_file(d / records.table_name(ap, hs))):
            e1, sha1, info1 = refit.refit(d, self.tmp / "m1", [a], log=lambda *x: None, model=small)
            e2, sha2, info2 = refit.refit(d, self.tmp / "m2", [a], log=lambda *x: None, model=small)
            self.assertEqual((e1, sha1, info1), (e2, sha2, info2))
            self.assertEqual(info1, [("EGLC", 0, 3, 150)])
            self.assertEqual(sorted(p.name for p in (self.tmp / "m1").iterdir()), ["gfs_EGLC_00z.json.gz", "manifest.txt"])
            self.assertEqual((self.tmp / "m1" / "gfs_EGLC_00z.json.gz").read_bytes(),
                             (self.tmp / "m2" / "gfs_EGLC_00z.json.gz").read_bytes())
            self.assertEqual(baseline.manifest_sha256((self.tmp / "m1" / "manifest.txt").read_text()), sha1)
            with self.assertRaises(SystemExit):
                refit.refit(d, self.tmp / "m1", [a], log=lambda *x: None, model=small)
            ms = baseline.ModelSet(self.tmp / "m1", "gfs", expected_manifest_sha=sha1)
            self.assertEqual(ms.manifest_sha, sha1)
            rows = tables.read_table_rows(d / records.table_name(a, "f000_024"), a.station)
            tr = [(r[7], r[6], r[5]) for r in rows]
            direct = baseline.predict(baseline.fit(tr), tr[:5])
            via_pack = [ms.baseline("EGLC", 0, 3, r[0], r[1]) for r in tr[:5]]
            self.assertEqual(direct, via_pack)
        # a table that is not the recorded one is refused
        self.assertIs(records.recorded_sha, real)
        with self.assertRaises(SystemExit):
            refit.refit(d, self.tmp / "m3", [a], log=lambda *x: None, model=small)


def records_name(airport, hs):
    from mlwx import records
    return records.table_name(airport, hs)


if __name__ == "__main__":
    unittest.main()
