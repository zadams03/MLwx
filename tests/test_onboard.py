"""Tests of the onboarding tool (src/mlwx/onboard.py; DECISIONS D104.6, D104.7, D103.6).

Offline; writes only to temporary folders, deleted after. The full gate (NZWN and ORD rebuilt as if new:
their rows, tables and model files byte for byte) is run in session 110, Step 4; these tests check the
parts that need no pull.

Run from the repo root: python3 -m unittest discover -s tests -v
"""

import csv
import datetime as dt
import random
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from mlwx import config, features, gfs, onboard, prediction_log, runner, tables  # noqa: E402
from mlwx import state as state_mod  # noqa: E402

MODEL = config.GFS
AIRPORTS_FILE = config.DATA / MODEL.airports_file
TWELVE_BYTES = b"".join(AIRPORTS_FILE.read_bytes().splitlines(keepends=True)[:13])   # header + the 12 of D103.4
CURRENT = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]


def read_csv(path, key):
    with open(path, newline="") as f:
        return {r[key]: r for r in csv.DictReader(f)}


def pull_airports():
    return read_csv(onboard.POSITIONS, "icao")


COUNTS_FILE = ROOT / "data" / "processed" / "session110_onboard_counts.csv"


def onboarded_new():
    """The new airports that pass both rules: the time-zone rule (F153) and, once session 110's counts
    file exists, D104.7 as recorded there."""
    new = [ic for ic, r in pull_airports().items() if r["role"] == "new"]
    new = [ic for ic in new if onboard.whole_hour_zone(onboard.time_zone_of(ic))]
    if COUNTS_FILE.exists():
        verdict = {r["airport"]: r["verdict"] for r in csv.DictReader(open(COUNTS_FILE, newline=""))}
        new = [ic for ic in new if verdict.get(ic) == "pass"]
    return new


class Case(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_onboard_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)


class RuleTests(Case):
    def test_the_fixed_numbers(self):
        self.assertEqual(onboard.MIN_ROWS, 1200)                 # D104.7
        self.assertEqual(onboard.LAPSE_C_PER_KM, 7.429)          # SPEC 7.2, D100.3(b)
        self.assertEqual(len(onboard.model_cells()), 184)        # 4 cycle hours x leads 3 to 48
        self.assertEqual(onboard.LAST_VALID, dt.datetime(2026, 7, 31, 23))

    def test_every_cell_needs_1200_rows(self):
        counts = {c: 1200 for c in onboard.model_cells()}
        self.assertTrue(onboard.passes(counts))
        counts[(18, 48)] = 1199
        self.assertFalse(onboard.passes(counts))
        s = onboard.summary(counts)
        self.assertEqual((s["smallest"], s["largest"], s["below"], s["pass"]), (1199, 1200, 1, False))
        counts.pop((18, 48))
        self.assertFalse(onboard.passes(counts))                 # a missing cell fails

    def test_the_time_zone_rule(self):
        self.assertEqual((onboard.TZ_FIRST_DAY, onboard.TZ_LAST_DAY), (dt.date(2021, 3, 1), dt.date(2027, 12, 31)))
        for z in ("UTC", "Europe/London", "America/Chicago", "Pacific/Auckland", "Asia/Karachi", "Australia/Sydney"):
            self.assertTrue(onboard.whole_hour_zone(z), z)
        for z in ("Asia/Kolkata", "Asia/Kathmandu", "Australia/Adelaide", "America/St_Johns"):
            self.assertFalse(onboard.whole_hour_zone(z), z)

    def test_vilk_is_the_only_airport_left_out_by_the_time_zone_rule_and_before_any_data(self):
        a90 = read_csv(onboard.AIRPORTS_90, "icao")
        self.assertEqual(len(a90), 47)
        bad = [ic for ic in a90 if not onboard.whole_hour_zone(onboard.time_zone_of(ic))]
        self.assertEqual(bad, ["VILK"])
        with mock.patch.object(onboard, "load_reports", side_effect=AssertionError("data opened")), \
                mock.patch.object(onboard, "read_pull_month", side_effect=AssertionError("data opened")):
            for call in (lambda: onboard.airport_row("VILK"), lambda: onboard.build_tables(["VILK"], self.tmp / "t"),
                         lambda: onboard.fit_airports(["VILK"], self.tmp / "t", self.tmp / "m")):
                with self.assertRaises(SystemExit) as e:
                    call()
                self.assertIn("time zone Asia/Kolkata", str(e.exception))
        self.assertFalse((self.tmp / "t").exists() and any((self.tmp / "t").iterdir()))


class RowTests(Case):
    def test_the_claim_airports_rows_are_reproduced_byte_for_byte(self):
        lines = AIRPORTS_FILE.read_text().splitlines()
        by_icao = {ln.split(",")[1]: ln for ln in lines[1:]}
        for icao in ("EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"):
            self.assertEqual(onboard.row_line(icao), by_icao[icao], icao)
        self.assertEqual(onboard.row_line("ORD"), by_icao["KORD"])    # an IEM id is accepted

    def test_development_airports_are_refused(self):
        for icao in ("EGLC", "KDSM", "KSFO"):
            with self.assertRaises(SystemExit):
                onboard.airport_row(icao)

    def test_an_unknown_airport_is_refused(self):
        with self.assertRaises(SystemExit):
            onboard.airport_row("XXXX")

    def test_the_38_new_airports_rows_come_from_their_sources(self):
        pos = pull_airports()
        a90 = read_csv(onboard.AIRPORTS_90, "icao")
        new = [ic for ic, r in pos.items() if r["role"] == "new"]
        self.assertEqual(len(new), 39)
        self.assertEqual(len(pos), 51)
        cols = onboard.airport_columns()
        for ic in new:
            if ic == "VILK":
                continue
            r = dict(zip(cols, onboard.airport_row(ic)))
            self.assertEqual((r["station"], r["icao"], r["role"]), (pos[ic]["iem_id"], ic, "new"))
            self.assertEqual(r["time_zone"], a90[ic]["time_zone"])
            self.assertEqual(float(r["correction_c"]), round(7.429 * float(a90[ic]["height_diff_m"]) / 1000.0, 4))
            self.assertEqual((r["lat"], r["lon"]), (pos[ic]["lat_used"], pos[ic]["lon_used"]))
            for k in (1, 2, 3, 4):
                for c in ("index", "lat", "lon", "weight"):
                    self.assertEqual(r[f"p{k}_{c}"], pos[ic][f"p{k}_{c}"])
            a = onboard.airport_of(ic)
            self.assertAlmostEqual(sum(a.weights), 1.0, places=12)

    def test_add_rows_keeps_the_existing_bytes_and_refuses_an_airport_twice(self):
        p = self.tmp / "gfs_airports.csv"
        p.write_bytes(TWELVE_BYTES)
        before = p.read_bytes()
        self.assertEqual(onboard.add_rows(["EHAM", "KATL"], p), 2)
        after = p.read_bytes()
        self.assertEqual(after[:len(before)], before)
        self.assertEqual(after[len(before):].decode().splitlines(), [onboard.row_line("EHAM"), onboard.row_line("KATL")])
        for again in (["EHAM"], ["NZWN"], ["LTAC", "LTAC"]):
            with self.assertRaises(SystemExit):
                onboard.add_rows(again, p)
        self.assertEqual(p.read_bytes(), after)


def table_file(path, station, rows):
    """A small table: rows of (cycle, lead, complete)."""
    lines = [",".join(tables.COLUMNS)]
    for cycle, n, complete in rows:
        out = {c: None for c in features.GRIB_COLS}
        for c in features.G15:
            out[c] = 1.5
        out["temperature_grib_c"] = 1.5
        line, _ = tables.table_line(station, cycle, n, out, 2.0 if complete else None,
                                    cycle + dt.timedelta(hours=n) if complete else None, False)
        lines.append(line)
    tables.write_new_file(path, tables.table_bytes(lines))


class CountTests(Case):
    def test_counts_only_complete_case_rows_per_cell(self):
        c0, c1 = dt.datetime(2024, 1, 1, 0), dt.datetime(2024, 1, 1, 6)
        a = self.tmp / "a.csv.gz"
        b = self.tmp / "b.csv.gz"
        table_file(a, "XX", [(c0, 0, False), (c0, 3, True), (c0, 3, True), (c0, 24, False), (c1, 3, True)])
        table_file(b, "XX", [(c0, 25, True), (c0, 48, True), (c1, 48, False)])
        got = onboard.cell_counts([(a, "XX", range(3, 25)), (b, "XX", range(25, 49))])
        self.assertEqual(len(got), 184)
        self.assertEqual((got[(0, 3)], got[(6, 3)], got[(0, 24)], got[(0, 25)], got[(0, 48)], got[(6, 48)]),
                         (2, 1, 0, 1, 1, 0))
        self.assertEqual(sum(got.values()), 5)

    def test_a_row_valid_after_july_2026_is_refused(self):
        a = self.tmp / "a.csv.gz"
        table_file(a, "XX", [(dt.datetime(2026, 7, 31, 18), 6, True)])
        with self.assertRaises(SystemExit):
            onboard.cell_counts([(a, "XX", range(3, 25))])

    def test_too_few_rows_are_never_fitted(self):
        a = self.tmp / "a.csv.gz"
        table_file(a, "XX", [(dt.datetime(2024, 1, d, 0), 3, True) for d in range(1, 11)])
        with self.assertRaises(SystemExit):
            onboard.fit_pack(("XXXX", 0, [(a, "XX", range(3, 25))]))

    def test_tables_are_checked_against_their_manifest(self):
        for hs in onboard.HOURSETS:
            table_file(self.tmp / onboard.table_name("EHAM", hs), "EHAM", [(dt.datetime(2024, 1, 1, 0), 3, True)])
        onboard.add_to_manifest(self.tmp, {onboard.table_name("EHAM", hs): tables.sha256_file(self.tmp / onboard.table_name("EHAM", hs))
                                           for hs in onboard.HOURSETS})
        self.assertEqual(len(onboard.table_files("EHAM", self.tmp, "EHAM")), 2)
        with self.assertRaises(SystemExit):                           # a manifest line never changes
            onboard.add_to_manifest(self.tmp, {onboard.table_name("EHAM", "f000_024"): "0" * 64})
        p = self.tmp / onboard.table_name("EHAM", "f025_048")
        p.unlink()
        table_file(p, "EHAM", [(dt.datetime(2024, 1, 1, 0), 25, False)])
        with self.assertRaises(SystemExit):
            onboard.table_files("EHAM", self.tmp, "EHAM")

    def test_build_tables_never_writes_over_a_table(self):
        p = self.tmp / onboard.table_name("EHAM", "f000_024")
        p.write_bytes(b"x")
        with self.assertRaises(SystemExit):
            onboard.build_tables(["EHAM"], self.tmp)
        self.assertEqual(p.read_bytes(), b"x")


# ------------------------------------------------------------------ the trackers of new airports (D103.6)

class FakeModels:
    manifest_sha = "cd" * 32

    def baseline(self, icao, cycle_hour, lead, x, temp):
        return temp + 0.5


def synthetic_cycle(cycle, airports):
    rng = random.Random(f"onboard-{cycle:%Y%m%d%H}")
    values, status = {}, {}
    base = {"t2m": 285.0, "tcdc": 40.0, "u10": 2.0, "v10": -1.0, "d2m": 280.0, "t850": 280.0,
            "dswrf": 150.0, "prmsl": 101300.0}
    for fh in range(0, 49):
        for f in MODEL.live_fields():
            if gfs.selector(f.kind, fh) is None:
                status[(fh, f.name)] = "absent by design"
                continue
            values[(fh, f.name)] = [base[f.name] + rng.uniform(-0.2, 0.2) for _ in airports for _ in range(4)]
            status[(fh, f.name)] = "ok"
    return gfs.CycleValues(cycle, airports, values, status)


class NewTrackerTests(Case):
    def setUp(self):
        super().setUp()
        data = self.tmp / "data"
        data.mkdir()
        (data / MODEL.airports_file).write_bytes(TWELVE_BYTES)
        self.new = onboarded_new()
        onboard.add_rows(self.new, data / MODEL.airports_file)
        p = mock.patch.object(config, "DATA", data)
        p.start()
        self.addCleanup(p.stop)
        self.airports = config.load_airports(MODEL)
        self.root = self.tmp / "live"

    def old_state(self):
        """A state file holding cells of the 12 current airports only, with b, last valid time and count set."""
        rng = random.Random(7)
        s = state_mod.State("gfs")
        s.last_cycle = dt.datetime(2026, 10, 11, 18)
        for icao in CURRENT:
            for h in MODEL.cycle_hours:
                for n in range(3, 49):
                    c = s.cell(icao, h, n)
                    c.b, c.n, c.last_valid = rng.uniform(-1, 1), rng.randint(1, 60), dt.datetime(2026, 10, 11, h) - dt.timedelta(hours=1)
        state_mod.save_state(self.root, s)
        return state_mod.state_path(self.root, "gfs").read_text()

    def test_the_onboarded_airports_are_configured_with_the_12_first_and_unchanged(self):
        self.assertEqual(len(self.airports), 12 + len(self.new))
        self.assertNotIn("VILK", [a.icao for a in self.airports])
        self.assertEqual([a.icao for a in self.airports[:12]], CURRENT)
        self.assertEqual(config.DATA.joinpath(MODEL.airports_file).read_bytes()[:len(TWELVE_BYTES)], TWELVE_BYTES)

    def test_the_package_airports_file_is_the_12_then_the_onboarded_rows(self):
        lines = AIRPORTS_FILE.read_text().splitlines()
        self.assertEqual(lines[13:], [onboard.row_line(ic) for ic in self.new])
        self.assertEqual(len(lines), 1 + 12 + 37)

    def test_old_state_read_with_all_onboarded_airports_keeps_old_cells_and_starts_new_ones_at_zero(self):
        text = self.old_state()
        saved = state_mod.State.from_json(__import__("json").loads(text))
        st = state_mod.load_state(self.root, "gfs")
        for a in self.airports:
            for h in MODEL.cycle_hours:
                for n in range(3, 49):
                    key = state_mod.cell_key(a.icao, h, n)
                    c = st.cell(a.icao, h, n)
                    if a.icao in CURRENT:
                        self.assertEqual(c, saved.cells[key])
                    else:
                        self.assertEqual((c.b, c.n, c.last_valid), (0.0, 0, None), key)
        self.assertEqual(len(saved.cells), 12 * 184)

    def test_a_run_with_all_onboarded_airports_issues_new_airports_at_b_zero_and_leaves_old_cells_unchanged(self):
        text = self.old_state()
        saved = state_mod.State.from_json(__import__("json").loads(text))
        cycle = dt.datetime(2026, 10, 12, 6)
        res = runner.run(self.root, self.tmp / "models", cycle + dt.timedelta(hours=4, minutes=30), latest_only=True,
                         commit="deadbeef", models=FakeModels(), fetch_gfs=lambda m, a, c: synthetic_cycle(c, a),
                         fetch_obs=lambda *a: self.fail("no observation is needed"), log=lambda *a: None)
        self.assertEqual(res["issued"], [cycle])
        rows = prediction_log.read_log(prediction_log.log_path(self.root, "gfs", cycle))
        self.assertEqual(len(rows), len(self.airports) * 46)
        for r in rows:
            key = state_mod.cell_key(r["airport"], 6, r["lead"])
            self.assertEqual(r["b"], saved.cells[key].b if r["airport"] in CURRENT else 0.0, key)
        st = state_mod.load_state(self.root, "gfs")
        for key, c in saved.cells.items():
            self.assertEqual(st.cells[key], c, key)
        self.assertTrue(all(st.cells[k].b == 0.0 and st.cells[k].n == 0 for k in st.cells if k.split("|")[0] not in CURRENT))
        html_text = (self.root / "site" / "index.html").read_text()
        self.assertTrue(all(f">{a.icao}" in html_text or a.icao in html_text for a in self.airports))


if __name__ == "__main__":
    unittest.main()
