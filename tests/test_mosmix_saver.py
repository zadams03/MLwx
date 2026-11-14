"""The MOSMIX saver template (DECISIONS D122; session 128, Step 5; session 131, Step 5: MS05, MS06, TE07).
Offline only: small synthetic .kmz files are built in a temporary folder and a fake server stands in for DWD.
No network, no real MOSMIX file. No YAML parser is installed in this project, so the workflow is checked by
text (and also parsed if a parser is ever installed).

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import contextlib
import csv
import importlib.util
import io
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
import urllib.error
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "deploy/mlwx-mosmix"
WORKFLOW = TEMPLATE / ".github/workflows/save.yml"
STATIONS = TEMPLATE / "stations.csv"
SESSION90 = ROOT / "data/processed/session90_airports.csv"
LIVE_AIRPORTS = ROOT / "src/mlwx/data/gfs_airports.csv"

CRON = "50 */3 * * *"                     # D122.6
EXTRA_STATIONS = {                         # D122.3 (F130.4): live airports not in the 47-airport table
    "LFPG": ("07157", "0.17"),
    "KDSM": ("72546", "0.27"),
    "KRNO": ("72488", "2.08"),
}
FORECAST_VALUE = "987.65"                  # a marker inside the synthetic KML: it must never be printed

spec = importlib.util.spec_from_file_location("mosmix_saver", TEMPLATE / "saver.py")
saver = importlib.util.module_from_spec(spec)
spec.loader.exec_module(saver)


def utc(s):
    return datetime.strptime(s, "%Y%m%d%H").replace(tzinfo=timezone.utc)


def kml_text(station, issue_iso, extra_issue=False):
    more = f"<dwd:IssueTime>{issue_iso}</dwd:IssueTime>" if extra_issue else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<kml:kml xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:dwd="https://example.invalid/dwd">'
        "<kml:Document><kml:ExtendedData><dwd:ProductDefinition>"
        f"<dwd:IssueTime>{issue_iso}</dwd:IssueTime>{more}"
        "</dwd:ProductDefinition></kml:ExtendedData>"
        f"<kml:Placemark><kml:name>{station}</kml:name><kml:ExtendedData>"
        f'<dwd:Forecast dwd:elementName="TTT"><dwd:value>{FORECAST_VALUE}</dwd:value></dwd:Forecast>'
        "</kml:ExtendedData></kml:Placemark></kml:Document></kml:kml>"
    )


def make_kmz(station, issue, issue_iso=None, kml_station=None, members=None):
    """Bytes of a .kmz. `issue` is YYYYMMDDHH; the KML says what the arguments say (right by default)."""
    iso = issue_iso or f"{issue[:4]}-{issue[4:6]}-{issue[6:8]}T{issue[8:10]}:00:00.000Z"
    members = members if members is not None else {f"MOSMIX_L_{issue}_{station}.kml": kml_text(kml_station or station, iso)}
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for name, text in members.items():
            z.writestr(name, text)
    return buf.getvalue()


def listing_html(station, issues, sizes=None, extra_names=()):
    lines = ['<html><body><pre><a href="../">../</a>']
    for issue in issues:
        name = f"MOSMIX_L_{issue}_{station}.kmz"
        size = (sizes or {}).get(issue, 1234)
        lines.append(f'<a href="{name}">{name}</a>                      12-Nov-2026 16:15:48               {size}')
    for name in extra_names:
        lines.append(f'<a href="{name}">{name}</a>                      12-Nov-2026 16:15:48               99')
    lines.append(f'<a href="MOSMIX_L_LATEST_{station}.kmz">MOSMIX_L_LATEST_{station}.kmz</a>      14-Nov-2026 10:13:48               555')
    lines.append("</pre></body></html>")
    return "\n".join(lines)


class FakeServer:
    """get(url) like saver.http_get: serves listings and files from a dict, counts every request."""

    def __init__(self, stations):
        self.pages = {}          # url -> bytes
        self.missing = set()     # urls that raise NotFound
        self.requests = []
        for station, issues in stations.items():
            self.set_station(station, issues)

    def set_station(self, station, issues, kmz=None):
        """issues: list of YYYYMMDDHH. kmz: {issue: bytes} to override a file."""
        kmz = kmz or {}
        files = {i: kmz.get(i) or make_kmz(station, i) for i in issues}
        sizes = {i: len(b) for i, b in files.items()}
        self.pages[f"{saver.BASE}{station}/kml/"] = listing_html(station, issues, sizes).encode()
        for i, b in files.items():
            self.pages[f"{saver.BASE}{station}/kml/MOSMIX_L_{i}_{station}.kmz"] = b

    def __call__(self, url):
        self.requests.append(url)
        if url in self.missing or url not in self.pages:
            raise saver.NotFound(url)
        return self.pages[url]

    def file_requests(self):
        return [u for u in self.requests if u.endswith(".kmz")]


# ---------------------------------------------------------------- the listing parser

class TestListing(unittest.TestCase):
    def test_real_form_names_are_found(self):
        html = listing_html("10870", ["2026111215", "2026111409"], {"2026111215": 19843, "2026111409": 19771})
        got = saver.parse_listing(html, "10870")
        self.assertEqual(sorted(got), [utc("2026111215"), utc("2026111409")])
        self.assertEqual(got[utc("2026111409")], ("MOSMIX_L_2026111409_10870.kmz", 19771))

    def test_latest_is_ignored(self):
        got = saver.parse_listing(listing_html("10870", ["2026111409"]), "10870")
        self.assertEqual(len(got), 1)
        self.assertNotIn("LATEST", " ".join(n for n, _ in got.values()))

    def test_other_names_are_ignored(self):
        extra = ["MOSMIX_L_2026111409_99999.kmz",        # another station
                 "MOSMIX_L_2026111409_10870.kml",        # wrong extension
                 "MOSMIX_S_2026111409_10870.kmz",        # another product
                 "MOSMIX_L_20261114_10870.kmz",          # too few digits
                 "MOSMIX_L_2026131409_10870.kmz",        # not a real date
                 "readme.txt"]
        got = saver.parse_listing(listing_html("10870", ["2026111403"], extra_names=extra), "10870")
        self.assertEqual(list(got), [utc("2026111403")])

    def test_letter_station_ids(self):
        got = saver.parse_listing(listing_html("P0478", ["2026111409"]), "P0478")
        self.assertEqual(list(got), [utc("2026111409")])


# ---------------------------------------------------------------- the file checks (D122.4)

class TestFileChecks(unittest.TestCase):
    def check(self, data, station="10870", issue="2026111409"):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "f.kmz"
            p.write_bytes(data)
            return saver.check_kmz(p, station, utc(issue))

    def test_a_good_file_passes(self):
        self.assertEqual(self.check(make_kmz("10870", "2026111409")), (True, ""))

    def test_rejects_a_bad_zip(self):
        ok, why = self.check(b"this is not a zip file at all")
        self.assertFalse(ok)
        self.assertIn("not a zip", why)

    def test_rejects_a_truncated_zip(self):
        good = make_kmz("10870", "2026111409")
        ok, _ = self.check(good[:len(good) // 2])
        self.assertFalse(ok)

    def test_rejects_a_missing_kml(self):
        ok, why = self.check(make_kmz("10870", "2026111409", members={"readme.txt": "no kml here"}))
        self.assertFalse(ok)
        self.assertIn("0 KML", why)

    def test_rejects_two_kml_files(self):
        members = {"a.kml": kml_text("10870", "2026-11-14T09:00:00.000Z"), "b.kml": kml_text("10870", "2026-11-14T09:00:00.000Z")}
        ok, why = self.check(make_kmz("10870", "2026111409", members=members))
        self.assertFalse(ok)
        self.assertIn("2 KML", why)

    def test_rejects_a_mismatched_issue_time(self):
        ok, why = self.check(make_kmz("10870", "2026111409", issue_iso="2026-11-14T03:00:00.000Z"))
        self.assertFalse(ok)
        self.assertIn("issue time", why)

    def test_rejects_a_mismatched_station_id(self):
        ok, why = self.check(make_kmz("10870", "2026111409", kml_station="72530"))
        self.assertFalse(ok)
        self.assertIn("station ids", why)

    def test_rejects_a_repeated_issue_time(self):
        members = {"a.kml": kml_text("10870", "2026-11-14T09:00:00.000Z", extra_issue=True)}
        ok, why = self.check(make_kmz("10870", "2026111409", members=members))
        self.assertFalse(ok)
        self.assertIn("IssueTime", why)

    def test_rejects_a_kml_that_is_not_xml(self):
        ok, why = self.check(make_kmz("10870", "2026111409", members={"a.kml": "<kml:kml><unclosed>"}))
        self.assertFalse(ok)
        self.assertIn("cannot be read", why)


# ---------------------------------------------------------------- saving

class TestSave(unittest.TestCase):
    STATIONS = [("EDDM", "10870"), ("KORD", "72530")]
    ISSUES = ["2026111315", "2026111321", "2026111403", "2026111409"]

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.out = Path(self.tmp.name) / "out"
        self.manifest = Path(self.tmp.name) / "manifest"
        self.server = FakeServer({"10870": self.ISSUES, "72530": self.ISSUES})
        self.lines = []

    def run_save(self, run_id="r1", stations=None, newest=None):
        return saver.save(stations or self.STATIONS, self.out, self.manifest, run_id, newest, self.server, self.lines.append)

    def rows(self):
        return saver.read_manifest(self.manifest)

    def test_saves_every_issue_with_one_tar_per_issue(self):
        failures, tars = self.run_save()
        self.assertEqual(failures, [])
        self.assertEqual(sorted(tars), [f"MOSMIX_L_{i}_runr1.tar" for i in self.ISSUES])
        self.assertEqual(len(self.rows()), 8)
        for r in self.rows():
            tar = self.out / "tars" / r["asset"]
            with tarfile.open(tar) as t:
                self.assertIn(Path(r["url"]).name, t.getnames())
            self.assertNotEqual(tar.read_bytes()[:2], b"\x1f\x8b", "the tar is not compressed")
        by_name = {p.name: p for p in (self.out / "kmz").rglob("*.kmz")}
        for r in self.rows():
            self.assertEqual(saver.sha256_of(by_name[Path(r["url"]).name]), r["sha256"])
            self.assertEqual(int(r["bytes"]), by_name[Path(r["url"]).name].stat().st_size)

    def test_manifest_columns_and_month_files(self):
        self.server.set_station("10870", ["2026103121", "2026110103"])
        self.run_save(stations=[("EDDM", "10870")])
        self.assertEqual(sorted(p.name for p in self.manifest.glob("*.csv")), ["2026-10.csv", "2026-11.csv"])
        with open(self.manifest / "2026-11.csv", newline="") as f:
            self.assertEqual(csv.DictReader(f).fieldnames, saver.MANIFEST_COLUMNS)

    def test_nothing_in_the_manifest_is_downloaded_again(self):
        self.run_save()
        before = len(self.server.file_requests())
        failures, tars = self.run_save(run_id="r2")
        self.assertEqual((failures, tars), ([], []))
        self.assertEqual(len(self.server.file_requests()), before, "a file was requested again")
        self.assertEqual(len(self.rows()), 8)

    def test_only_the_new_issue_is_downloaded(self):
        self.run_save()
        before = len(self.server.file_requests())
        self.server.set_station("10870", self.ISSUES + ["2026111415"])
        failures, tars = self.run_save(run_id="r2")
        self.assertEqual(failures, [])
        self.assertEqual(tars, ["MOSMIX_L_2026111415_runr2.tar"])
        self.assertEqual([Path(u).name for u in self.server.file_requests()[before:]], ["MOSMIX_L_2026111415_10870.kmz"])
        self.assertEqual(len(self.rows()), 9)

    def test_newest_option(self):
        failures, tars = self.run_save(newest=2)
        self.assertEqual(sorted(tars), ["MOSMIX_L_2026111403_runr1.tar", "MOSMIX_L_2026111409_runr1.tar"])
        self.assertEqual(len(self.rows()), 4)

    def test_a_failed_check_is_not_kept_and_is_reported(self):
        bad = make_kmz("72530", "2026111409", kml_station="10870")
        self.server.set_station("72530", self.ISSUES, kmz={"2026111409": bad})
        failures, tars = self.run_save()
        self.assertEqual(len(failures), 1)
        self.assertIn("KORD", failures[0])
        self.assertIn("failed the check", failures[0])
        self.assertFalse((self.out / "kmz/2026111409/MOSMIX_L_2026111409_72530.kmz").exists())
        self.assertFalse(list((self.out / "kmz").rglob("*.part")))
        held = saver.held_keys(self.rows())
        self.assertNotIn(("72530", "2026-11-14T09:00Z"), held)
        self.assertIn(("10870", "2026-11-14T09:00Z"), held, "the good file of that issue is still saved")
        self.assertEqual(len(tars), 4)

    def test_a_size_that_differs_from_the_listing_is_not_kept(self):
        url = f"{saver.BASE}10870/kml/MOSMIX_L_2026111409_10870.kmz"
        self.server.pages[url] = self.server.pages[url] + b"extra"
        failures, _ = self.run_save(newest=1)
        self.assertEqual(len(failures), 1)
        self.assertIn("the listing said", failures[0])
        self.assertNotIn(("10870", "2026-11-14T09:00Z"), saver.held_keys(self.rows()))

    def test_a_station_with_no_directory_is_reported(self):
        self.server.missing.add(f"{saver.BASE}72530/kml/")
        failures, tars = self.run_save()
        self.assertEqual(len(failures), 1)
        self.assertIn("no directory", failures[0])
        self.assertEqual(len(tars), 4)
        self.assertEqual(len(self.rows()), 4)

    def test_an_existing_file_is_never_overwritten(self):
        target = self.out / "kmz/2026111409/MOSMIX_L_2026111409_10870.kmz"
        target.parent.mkdir(parents=True)
        target.write_bytes(b"precious")
        failures, _ = self.run_save(newest=1)
        self.assertTrue(any("not overwritten" in f for f in failures))
        self.assertEqual(target.read_bytes(), b"precious")
        self.assertNotIn(("10870", "2026-11-14T09:00Z"), saver.held_keys(self.rows()))

    def test_an_existing_tar_is_never_overwritten(self):
        tar = self.out / "tars/MOSMIX_L_2026111409_runr1.tar"
        tar.parent.mkdir(parents=True)
        tar.write_bytes(b"precious tar")
        failures, tars = self.run_save(newest=1)
        self.assertTrue(any("not overwritten" in f for f in failures))
        self.assertEqual(tar.read_bytes(), b"precious tar")
        self.assertEqual(tars, [])
        self.assertEqual(self.rows(), [], "no rows are written for an issue whose tar was not made")

    def test_write_new_refuses_an_existing_file(self):
        p = Path(self.tmp.name) / "x"
        saver.write_new(p, b"one")
        with self.assertRaises(FileExistsError):
            saver.write_new(p, b"two")
        self.assertEqual(p.read_bytes(), b"one")

    def test_the_manifest_is_only_added_to(self):
        self.run_save(newest=1)
        first = (self.manifest / "2026-11.csv").read_text()
        self.run_save(run_id="r2")
        second = (self.manifest / "2026-11.csv").read_text()
        self.assertTrue(second.startswith(first))
        with self.assertRaises(RuntimeError):
            saver.append_rows(self.manifest, [self.rows()[0]])

    def test_no_forecast_value_is_ever_printed(self):
        self.run_save()
        self.assertTrue(self.lines)
        self.assertFalse([ln for ln in self.lines if FORECAST_VALUE in ln])


class TestCommandLine(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.stations = self.dir / "stations.csv"
        self.stations.write_text("icao,station_id,distance_km,note\nEDDM,10870,1.1,\nKORD,72530,3.7,\n")
        self.server = FakeServer({"10870": ["2026111403", "2026111409"], "72530": ["2026111403", "2026111409"]})
        self.lines = []

    def main(self, *args):
        return saver.main([*args, "--stations", str(self.stations)], self.server, self.lines.append)

    def test_list_prints_issues_newest_first_and_no_values(self):
        self.assertEqual(self.main("--list"), 0)
        self.assertIn("EDDM 10870: 2 issues: 2026111409 2026111403", self.lines)
        self.assertFalse([ln for ln in self.lines if FORECAST_VALUE in ln])

    def test_list_fails_on_a_missing_directory(self):
        self.server.missing.add(f"{saver.BASE}72530/kml/")
        self.assertEqual(self.main("--list"), 1)
        self.assertIn("KORD 72530: NO DIRECTORY", self.lines)

    def test_save_then_save_again(self):
        out, man = self.dir / "out", self.dir / "man"
        self.assertEqual(self.main("--save", str(out), "--manifest-dir", str(man), "--run-id", "a"), 0)
        n = len(self.server.file_requests())
        self.assertEqual(n, 4)
        self.assertEqual(self.main("--save", str(out), "--manifest-dir", str(man), "--run-id", "b"), 0)
        self.assertEqual(len(self.server.file_requests()), n)
        self.assertFalse([ln for ln in self.lines if FORECAST_VALUE in ln])

    def test_save_exits_non_zero_on_any_failure(self):
        self.server.set_station("72530", ["2026111403", "2026111409"], kmz={"2026111409": b"junk"})
        rc = self.main("--save", str(self.dir / "out"), "--manifest-dir", str(self.dir / "man"), "--run-id", "a")
        self.assertEqual(rc, 1)
        self.assertEqual(len(saver.read_manifest(self.dir / "man")), 3)

    def test_manifest_dir_is_required(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            self.main("--save", str(self.dir / "out"))

    def test_only_option(self):
        self.assertEqual(self.main("--list", "--only", "KORD"), 0)
        self.assertEqual([ln for ln in self.lines if ln.startswith("EDDM")], [])


# ---------------------------------------------------------------- the 12-hour rule (D122.6)

class TestFreshness(unittest.TestCase):
    LISTED = utc("2026111409")

    def test_boundaries(self):
        self.assertTrue(saver.fresh_ok(self.LISTED, self.LISTED))
        self.assertTrue(saver.fresh_ok(self.LISTED - timedelta(hours=12), self.LISTED))
        self.assertFalse(saver.fresh_ok(self.LISTED - timedelta(hours=12, minutes=1), self.LISTED))
        self.assertFalse(saver.fresh_ok(utc("2026111203"), self.LISTED))

    def test_nothing_held_fails_when_something_is_listed(self):
        self.assertFalse(saver.fresh_ok(None, self.LISTED))

    def test_nothing_listed_is_not_late(self):
        self.assertTrue(saver.fresh_ok(utc("2026111203"), None))

    def check(self, held_issues, listed_issues):
        with tempfile.TemporaryDirectory() as d:
            server = FakeServer({"10870": listed_issues})
            man = Path(d) / "manifest"
            if held_issues:
                saver.append_rows(man, [{"station": "10870", "icao": "EDDM", "issue": saver.issue_text(utc(i)), "url": "u",
                                         "bytes": 1, "sha256": "0", "saved_utc": "t", "asset": "a", "run_id": "r"}
                                        for i in held_issues])
            return saver.check_fresh([("EDDM", "10870")], man, server, lambda s: None)

    def test_check_fresh_passes_when_held_is_recent(self):
        self.assertEqual(self.check(["2026111403"], ["2026111403", "2026111409", "2026111415"]), (True, []))

    def test_check_fresh_fails_when_held_is_old(self):
        ok, failures = self.check(["2026111321"], ["2026111403", "2026111409", "2026111415"])
        self.assertFalse(ok)

    def test_check_fresh_fails_on_an_empty_manifest(self):
        self.assertFalse(self.check([], ["2026111409"])[0])

    def check_many(self, held, listed):
        """held: {station: [issues]}; listed: {station: [issues]} (two stations)."""
        stations = [("EDDM", "10870"), ("EGLC", "03779")]
        with tempfile.TemporaryDirectory() as d:
            server = FakeServer(listed)
            man = Path(d) / "manifest"
            rows = [{"station": st, "icao": ic, "issue": saver.issue_text(utc(i)), "url": "u", "bytes": 1,
                     "sha256": "0", "saved_utc": "t", "asset": "a", "run_id": "r"}
                    for ic, st in stations for i in held.get(st, [])]
            if rows:
                saver.append_rows(man, rows)
            out = []
            return saver.check_fresh(stations, man, server, out.append), out

    def test_one_station_behind_fails_while_the_newest_overall_is_fresh(self):
        """MS06: EGLC's directory stays but its newest issue held is 18 h behind the newest listed."""
        listed = {"10870": ["2026111403", "2026111409", "2026111415"], "03779": ["2026111321"]}
        (ok, failures), out = self.check_many({"10870": ["2026111415"], "03779": ["2026111321"]}, listed)
        self.assertFalse(ok)
        self.assertEqual(failures, [])
        self.assertIn("EGLC 03779: newest issue held 2026-11-13T21:00Z, more than 12 h behind the newest issue listed", out)
        self.assertIn("stations more than 12 h behind: 1 of 2: FAIL", out)
        self.assertTrue(any("rule: held no more than 12 h behind listed: PASS" in line for line in out))

    def test_per_station_boundary_is_12_hours(self):
        listed = {"10870": ["2026111415"], "03779": ["2026111403"]}
        (ok, _), out = self.check_many({"10870": ["2026111415"], "03779": ["2026111403"]}, listed)
        self.assertTrue(ok)
        self.assertIn("stations more than 12 h behind: 0 of 2: PASS", out)
        listed = {"10870": ["2026111416"], "03779": ["2026111403"]}
        (ok, _), _ = self.check_many({"10870": ["2026111416"], "03779": ["2026111403"]}, listed)
        self.assertFalse(ok)

    def test_a_station_with_nothing_held_is_behind(self):
        listed = {"10870": ["2026111415"], "03779": ["2026111415"]}
        (ok, _), out = self.check_many({"10870": ["2026111415"]}, listed)
        self.assertFalse(ok)
        self.assertIn("EGLC 03779: newest issue held none, more than 12 h behind the newest issue listed", out)

    def test_stale_stations_with_nothing_listed_is_empty(self):
        self.assertEqual(saver.stale_stations([], [("EDDM", "10870")], None), [])

    def test_command_exit_code(self):
        with tempfile.TemporaryDirectory() as d:
            st = Path(d) / "stations.csv"
            st.write_text("icao,station_id,distance_km,note\nEDDM,10870,1.1,\n")
            server = FakeServer({"10870": ["2026111409"]})
            rc = saver.main(["--check-fresh", "--manifest-dir", str(Path(d) / "m"), "--stations", str(st)], server, lambda s: None)
            self.assertEqual(rc, 1)


# ---------------------------------------------------------------- the network layer

class FakeResponse:
    def __init__(self, data, headers=None):
        self.data, self.headers = data, headers or {}

    def read(self, n=-1):
        return self.data if n < 0 else self.data[:n]

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class TestHttpGet(unittest.TestCase):
    def test_retries_three_times_with_a_back_off(self):
        calls, naps = [], []

        def opener(req, timeout):
            calls.append(1)
            raise urllib.error.URLError("down")

        with self.assertRaises(RuntimeError):
            saver.http_get("https://x.invalid/", sleep=naps.append, opener=opener)
        self.assertEqual(len(calls), 3)
        self.assertEqual(naps, [2, 4])

    def test_succeeds_on_the_third_try(self):
        calls = []

        def opener(req, timeout):
            calls.append(1)
            if len(calls) < 3:
                raise TimeoutError("slow")
            return FakeResponse(b"ok")

        self.assertEqual(saver.http_get("https://x.invalid/", sleep=lambda s: None, opener=opener), b"ok")
        self.assertEqual(len(calls), 3)

    def test_a_404_is_not_retried(self):
        calls = []

        def opener(req, timeout):
            calls.append(1)
            raise urllib.error.HTTPError("https://x.invalid/", 404, "nope", {}, None)

        with self.assertRaises(saver.NotFound):
            saver.http_get("https://x.invalid/", sleep=lambda s: None, opener=opener)
        self.assertEqual(len(calls), 1)

    def test_a_short_read_is_a_failure(self):
        def opener(req, timeout):
            return FakeResponse(b"abc", {"Content-Length": "10"})

        with self.assertRaises(RuntimeError):
            saver.http_get("https://x.invalid/", sleep=lambda s: None, opener=opener)


# ---------------------------------------------------------------- stations.csv (D122.3)

def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


class TestStations(unittest.TestCase):
    def expected(self):
        live = {r["icao"] for r in read_rows(LIVE_AIRPORTS)}
        out = {}
        for r in read_rows(SESSION90):
            if r["mosmix_within_10km"] == "yes" and r["icao"] in live:
                out[r["icao"]] = (r["mosmix_station_id"], r["mosmix_distance_km"])
        out.update(EXTRA_STATIONS)
        return out

    def test_equals_the_two_sources_exactly(self):
        got = {r["icao"]: (r["station_id"], r["distance_km"]) for r in read_rows(STATIONS)}
        self.assertEqual(got, self.expected())

    def test_38_rows_38_distinct_stations_sorted(self):
        rows = read_rows(STATIONS)
        self.assertEqual(len(rows), 38)
        self.assertEqual(len({r["station_id"] for r in rows}), 38)
        self.assertEqual([r["icao"] for r in rows], sorted(r["icao"] for r in rows))
        self.assertEqual(list(rows[0]), ["icao", "station_id", "distance_km", "note"])

    def test_every_station_is_a_live_airport(self):
        live = {r["icao"] for r in read_rows(LIVE_AIRPORTS)}
        self.assertTrue({r["icao"] for r in read_rows(STATIONS)} <= live)

    def test_ysdu_is_not_listed_and_eglc_has_its_note(self):
        by = {r["icao"]: r for r in read_rows(STATIONS)}
        self.assertNotIn("YSDU", by)
        self.assertEqual(by["EGLC"]["station_id"], "P0478")
        self.assertIn("longitude", by["EGLC"]["note"])
        flagged = [r["icao"] for r in read_rows(SESSION90) if r["mosmix_lon_sign_flag"] == "yes"]
        self.assertEqual(flagged, ["EGLC"])

    def test_station_ids_keep_their_leading_zeros(self):
        by = {r["icao"]: r["station_id"] for r in read_rows(STATIONS)}
        self.assertEqual(by["LFPG"], "07157")
        self.assertEqual(by["EHAM"], "06240")

    def test_saver_reads_the_same_list(self):
        self.assertEqual(saver.read_stations(), [(r["icao"], r["station_id"]) for r in read_rows(STATIONS)])


# ---------------------------------------------------------------- the workflow (text; no YAML parser is installed)

def steps(t):
    """[(step name, its lines)] for each '- name:' block under steps."""
    out, name = [], None
    for ln in t.splitlines():
        m = re.match(r"^      - name: (.+)$", ln)
        if m:
            name = m.group(1)
            out.append((name, []))
        elif name is not None:
            out[-1][1].append(ln)
    return out


class TestWorkflow(unittest.TestCase):
    def setUp(self):
        self.t = WORKFLOW.read_text()

    def test_cron_and_manual_trigger(self):
        self.assertEqual(re.findall(r'cron: "([^"]+)"', self.t), [CRON])
        self.assertIn("\n  workflow_dispatch:", self.t)

    def test_permissions(self):
        self.assertIn("      contents: write", self.t)
        self.assertEqual(len(re.findall(r"^\s+permissions:", self.t, re.M)), 1)

    def test_no_overwrite_flag(self):
        self.assertNotIn("--clobber", self.t)

    def test_action_majors_and_python(self):
        self.assertEqual(sorted(re.findall(r"uses: (actions/[\w-]+@\S+)", self.t)),
                         ["actions/checkout@v5", "actions/setup-python@v6"])
        self.assertEqual(re.findall(r'python-version: "([^"]+)"', self.t), ["3.12"])

    def test_upload_is_before_commit(self):
        names = [n for n, _ in steps(self.t)]
        up = [i for i, n in enumerate(names) if n.startswith("Upload")]
        commit = [i for i, n in enumerate(names) if n.startswith("Commit")]
        self.assertEqual((len(up), len(commit)), (1, 1))
        self.assertLess(up[0], commit[0])
        text_up = "\n".join(dict(steps(self.t))[names[up[0]]])
        self.assertIn("gh release upload", text_up)
        self.assertIn("gh release create", text_up)

    def test_step_order_and_commands(self):
        names = [n for n, _ in steps(self.t)]
        self.assertEqual(names[0], "Check out this repo (the manifest)")
        s = dict(steps(self.t))
        body = {n: "\n".join(lines) for n, lines in s.items()}
        self.assertIn("python saver.py --save out --manifest-dir manifest", body["Save the new issues"])
        self.assertIn("python saver.py --check-fresh --manifest-dir manifest", body["Check that the newest issue held is fresh"])
        self.assertLess(names.index("Commit and push the manifest"), names.index("Check that the newest issue held is fresh"))
        self.assertIn("git pull --rebase", body["Commit and push the manifest"])
        self.assertIn("git add manifest", body["Commit and push the manifest"])
        self.assertIn("exit 1", body["Commit and push the manifest"])

    def test_save_failure_fails_the_job_at_the_end(self):
        names = [n for n, _ in steps(self.t)]
        self.assertEqual(names[-1], "Fail the job if the save had a failure")
        self.assertIn("always()", self.t)

    def test_text_shape(self):
        self.assertNotIn("\t", self.t)
        for key in ("\nname: save", "\non:", "\nconcurrency:", "\njobs:"):
            self.assertIn(key, "\n" + self.t)
        self.assertEqual(len(set(n for n, _ in steps(self.t))), len(steps(self.t)), "step names are unique")

    def test_parses_as_yaml_if_a_parser_is_installed(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("no YAML parser installed; the workflow is checked by text above")
        doc = yaml.safe_load(self.t)
        self.assertEqual(doc["on"]["schedule"][0]["cron"], CRON)
        self.assertIn("workflow_dispatch", doc["on"])
        self.assertEqual(doc["jobs"]["save"]["permissions"], {"contents": "write"})


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class TestCommitStep(unittest.TestCase):
    """TE07, MS05: the step 'Commit and push the manifest' from the YAML, run under GitHub's default bash
    (bash --noprofile --norc -eo pipefail) in a clone of a temporary bare repository, with and without
    manifest/."""

    def run_step(self, make_manifest):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            git(d, "init", "-q", "--bare", "-b", "main", "origin.git")
            git(d, "clone", "-q", str(d / "origin.git"), "work")
            work = d / "work"
            (work / "saver.py").write_text("# seed\n")
            git(work, "add", ".")
            git(work, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
            git(work, "push", "-q", "origin", "HEAD:main")
            git(work, "branch", "--set-upstream-to=origin/main")
            if make_manifest:
                (work / "manifest").mkdir()
                (work / "manifest" / "2026-11.csv").write_text(",".join(saver.MANIFEST_COLUMNS) + "\n")
            body = dict(steps(WORKFLOW.read_text()))["Commit and push the manifest"]
            i = body.index("        run: |")
            script = d / "step.sh"
            script.write_text("\n".join(ln[10:] for ln in body[i + 1:]) + "\n")
            r = subprocess.run(["bash", "--noprofile", "--norc", "-eo", "pipefail", str(script)], cwd=work,
                               capture_output=True, text=True, env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1"})
            files = git(d / "origin.git", "ls-tree", "-r", "--name-only", "main").splitlines()
            return r, files

    def test_without_manifest_folder_exits_0_and_commits_nothing(self):
        r, files = self.run_step(False)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("The manifest did not change: nothing to commit.", r.stdout)
        self.assertEqual(files, ["saver.py"])

    def test_with_manifest_folder_commits_and_pushes(self):
        r, files = self.run_step(True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(files, ["manifest/2026-11.csv", "saver.py"])

    def test_the_guard_line(self):
        self.assertIn("if [ -d manifest ]; then git add manifest; fi", WORKFLOW.read_text())


class TestFiles(unittest.TestCase):
    def test_template_files_exist(self):
        for rel in ("saver.py", "stations.csv", "README.md", ".gitignore", ".github/workflows/save.yml"):
            self.assertTrue((TEMPLATE / rel).is_file(), rel)

    def test_saver_uses_only_the_standard_library(self):
        text = (TEMPLATE / "saver.py").read_text()
        mods = set(re.findall(r"^(?:import|from) ([\w.]+)", text, re.M))
        stdlib = set(sys.stdlib_module_names)
        self.assertEqual({m for m in mods if m.split(".")[0] not in stdlib}, set())

    def test_gitignore_keeps_downloads_out(self):
        g = (TEMPLATE / ".gitignore").read_text().splitlines()
        for pat in ("out/", "*.tar", "*.kmz"):
            self.assertIn(pat, g)

    def test_no_em_dash(self):
        for p in [TEMPLATE / n for n in ("saver.py", "stations.csv", "README.md", ".gitignore")] + [WORKFLOW, Path(__file__)]:
            self.assertNotIn(chr(0x2014), p.read_text(), p.name)


if __name__ == "__main__":
    unittest.main()
