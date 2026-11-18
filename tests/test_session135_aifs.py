"""Session 135: stage D's AIFS claim airports and the AIFS pull (DECISIONS D130.7 to D130.9).

- The pull's guards: no cycle before 2025-02-26 00z; no step valid after 2026-07-31T23:00 UTC;
  only the 18 airports of D130.9 (the 12 record airports and draw.csv's six); only the folder
  aifs-single/0p25/oper/, never experimental; chunk arguments outside the window stop.
- The draw: `draw` reproduces draw.csv from eligibility.csv, and its shortfall rule (D82.7(d)).
- The longitude mapping of D130.8: a point is found on a grid starting at 0 or at 180 degrees
  east, by its longitude modulo 360; a point between nodes is not a node.
- A gap is never written as a value: a missing or non-finite point gives no values; an index
  with no line, or two, for a field gives a gap with no byte range.

Offline: no network call, no GRIB file.
Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import csv
import datetime as dt
import json
import math
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import session135_aifs_draw as D  # noqa: E402
import session135_aifs_pull as P  # noqa: E402

DRAWN = ["EPWA", "KATL", "KDAL", "RJTT", "ZUUU", "SBGR"]     # session 135's draw (F179)


def meta(lo1):
    return {"Ni": 1440, "Nj": 721, "iDirectionIncrementInDegrees": 0.25, "jDirectionIncrementInDegrees": 0.25,
            "latitudeOfFirstGridPointInDegrees": 90.0, "longitudeOfFirstGridPointInDegrees": lo1,
            "scanningMode": 0, "gridType": "regular_ll"}


class GuardTests(unittest.TestCase):
    def test_first_cycle(self):
        P.guard_cycle(dt.datetime(2025, 2, 26, 0))
        with self.assertRaises(P.GuardError):
            P.guard_cycle(dt.datetime(2025, 2, 25, 18))
        with self.assertRaises(P.GuardError):
            P.guard_cycle(dt.datetime(2025, 3, 1, 3))
        with self.assertRaises(P.GuardError):
            P.chunks_from_args(days="2025-02-25..2025-02-27")
        with self.assertRaises(P.GuardError):
            P.chunks_from_args(months="2025-01..2025-03")

    def test_all_cycles(self):
        cy = P.all_cycles()
        self.assertEqual(cy[0], dt.datetime(2025, 2, 26, 0))
        self.assertEqual(cy[-1], dt.datetime(2026, 7, 31, 18))
        self.assertEqual(len(cy), 521 * 4)

    def test_last_valid(self):
        self.assertEqual(P.steps_kept(dt.datetime(2026, 7, 29, 18)), [0, 6, 12, 18, 24, 30, 36, 42, 48])
        self.assertEqual(P.steps_kept(dt.datetime(2026, 7, 30, 0)), [0, 6, 12, 18, 24, 30, 36, 42])
        self.assertEqual(P.steps_kept(dt.datetime(2026, 7, 31, 18)), [0])
        P.guard_valid(dt.datetime(2026, 7, 31, 23))
        with self.assertRaises(P.GuardError):
            P.guard_valid(dt.datetime(2026, 8, 1, 0))
        for c in P.all_cycles():
            for s in P.steps_kept(c):
                self.assertLessEqual(c + dt.timedelta(hours=s), P.LIMIT)
        with self.assertRaises(P.GuardError):
            P.chunks_from_args(days="2026-07-31..2026-08-01")

    def test_fields(self):
        self.assertEqual(len(P.fields_for(0)), 10)
        self.assertEqual(len(P.fields_for(6)), 9)
        self.assertNotIn("z", [p for p, _, _ in P.fields_for(6)])

    def test_airports(self):
        a = P.guard_airports(list(D.RECORD12) + DRAWN)
        self.assertEqual(len(a), 18)
        with self.assertRaises(P.GuardError):
            P.guard_airports(list(D.RECORD12) + DRAWN[:5] + ["EGLC"])
        with self.assertRaises(P.GuardError):
            P.guard_airports(list(D.RECORD12) + DRAWN + ["EHAM"])
        with self.assertRaises(P.GuardError):
            P.guard_airports(list(D.RECORD12[:11]) + DRAWN + ["EHAM"])

    def test_airports_from_draw(self):
        airports, pts, _ = P.load_airports()
        self.assertEqual(airports, list(D.RECORD12) + DRAWN)
        self.assertTrue(all(len(pts[a]) == 4 for a in airports))

    def test_folder(self):
        P.guard_url("https://x/20250301/00z/aifs-single/0p25/oper/20250301000000-6h-oper-fc.grib2")
        with self.assertRaises(P.GuardError):
            P.guard_url("https://x/20250210/00z/aifs-single/0p25/experimental/20250210000000-6h-oper-fc.grib2")
        with self.assertRaises(P.GuardError):
            P.guard_url("https://x/20250301/00z/ifs/0p25/oper/20250301000000-6h-oper-fc.grib2")


class DrawTests(unittest.TestCase):
    def test_reproduces_draw_csv(self):
        rows = D.read_csv(D.ELIG)
        self.assertEqual(len(rows), 36)
        got = D.draw(rows, D.SEED, log=lambda s: None)
        want = D.read_csv(D.DRAW)
        self.assertEqual([(a, s, h) for a, s, h in got], [(r["icao"], r["stratum"], r["how"]) for r in want])
        self.assertEqual([r["icao"] for r in want], DRAWN)

    def test_shortfall(self):
        rows = [dict(icao=a, stratum=s, eligible="1") for a, s in
                [("EAAA", "Europe"), ("KAAA", "North America"), ("KBBB", "North America"),
                 ("RAAA", "Asia"), ("RBBB", "Asia"), ("RCCC", "Asia"), ("EBBB", "Europe")]]
        got = D.draw(rows, 1, log=lambda s: None)
        self.assertEqual(len(got), 6)
        self.assertEqual(got[-1][2], "shortfall fill")
        with self.assertRaises(SystemExit):
            D.draw(rows[:5], 1, log=lambda s: None)


class LongitudeTests(unittest.TestCase):
    def test_grid_starting_at_0(self):
        m = meta(0.0)
        self.assertEqual(D.grid_index(m, 90.0, 0.0), 0)
        self.assertEqual(D.grid_index(m, 90.0, 280.25), 1121)
        self.assertEqual(D.grid_index(m, 90.0, -79.75), 1121)        # modulo 360
        self.assertEqual(D.grid_index(m, 43.5, 280.5), 186 * 1440 + 1122)

    def test_grid_starting_at_180(self):
        m = meta(180.0)
        self.assertEqual(D.grid_index(m, 90.0, 180.0), 0)
        self.assertEqual(D.grid_index(m, 90.0, -180.0), 0)
        self.assertEqual(D.grid_index(m, 90.0, 0.0), 720)
        self.assertEqual(D.grid_index(m, 90.0, 280.25), 401)         # 280.25 = -79.75
        self.assertEqual(D.grid_index(m, 90.0, 179.75), 1439)

    def test_not_a_node(self):
        self.assertIsNone(D.grid_index(meta(0.0), 43.6, 280.5))
        self.assertIsNone(D.grid_index(meta(0.0), 43.5, 280.3))

    def test_check_points_against_coordinates(self):
        m = meta(180.0)
        n = 1440 * 721
        lats = [0.0] * n
        lons = [0.0] * n
        row = {}
        for k, (la, lo) in enumerate([(43.5, 280.5), (43.5, 280.25), (43.75, 280.5), (43.75, 280.25)], 1):
            i = D.grid_index(m, la, lo)
            lats[i], lons[i] = la, lo - 360.0                       # the grid gives -79.5, a turn away
            row.update({f"p{k}_lat": la, f"p{k}_lon": lo, f"p{k}_weight": 0.25})
        ok, idx, note = D.check_points(m, lats, lons, row)
        self.assertTrue(ok, note)
        lats[idx[0]] = 43.25
        ok, _, _ = D.check_points(m, lats, lons, row)
        self.assertFalse(ok)


class GapTests(unittest.TestCase):
    def test_missing_value_is_no_value(self):
        vals = [1.0, 2.0, 9999.0, float("nan"), 5.0]
        self.assertEqual(P.point_values(vals, [0, 1, 4, 0], 9999.0), [1.0, 2.0, 5.0, 1.0])
        self.assertIsNone(P.point_values(vals, [0, 1, 2, 4], 9999.0))
        self.assertIsNone(P.point_values(vals, [0, 3, 1, 4], 9999.0))

    def test_index_gaps(self):
        cyc = dt.datetime(2025, 3, 1, 0)
        line = lambda p, lt="sfc", lv=None, off=0: dict(  # noqa: E731
            param=p, levtype=lt, date="20250301", time="0000", step="6", _offset=off, _length=10,
            **({"levelist": lv} if lv else {}))
        lines = [line("2t"), line("2t", off=10), line("t", "pl", "850"), line("t", "pl", "500"),
                 line("tcc"), line("10u"), line("10v"), line("msl"), line("sp"), line("ssrd")]
        out = {p: (st, why, off) for p, lv, st, why, off, ln, ln2 in P.index_select(lines, cyc, 6)}
        self.assertEqual(out["2t"][0], "gap")
        self.assertIsNone(out["2t"][2])
        self.assertEqual(out["2d"], ("gap", "0 index lines", None))
        self.assertEqual(out["t"][0], "planned")
        self.assertEqual(len(out), 9)
        wrong = [dict(line("tcc"), date="20250228")]
        o = P.index_select(wrong, cyc, 6)
        self.assertTrue(all(r[2] == "gap" and r[4] is None for r in o))

    def test_check_message(self):
        cyc = dt.datetime(2025, 3, 1, 0)
        m = {"shortName": "2t", "typeOfLevel": "heightAboveGround", "level": 2, "units": "K",
             "dataDate": 20250301, "dataTime": 0, "validityDate": 20250301, "validityTime": 600,
             "gridType": "regular_ll", "iDirectionIncrementInDegrees": 0.25,
             "jDirectionIncrementInDegrees": 0.25, "Ni": 1440, "Nj": 721}
        self.assertEqual(P.check_message(m, cyc, 6, "2t"), [])
        self.assertTrue(P.check_message(dict(m, units="C"), cyc, 6, "2t"))
        self.assertTrue(P.check_message(dict(m, validityTime=1200), cyc, 6, "2t"))
        self.assertTrue(P.check_message(dict(m, Ni=900), cyc, 6, "2t"))
        self.assertTrue(P.check_message(m, cyc, 6, "2d"))


class TestChunkFiles(unittest.TestCase):
    """The committed test chunk: every value row finite and inside the guards."""

    def test_rows(self):
        out = P.DEFAULT_OUT
        if not (out / "gate.txt").exists():
            self.skipTest("no test chunk")
        airports = list(D.RECORD12) + DRAWN
        for d in sorted(out.glob("*/done.txt")):
            for a in airports:
                for r in P.read_gz(d.parent / f"aifs_{a}.csv.gz"):
                    c = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ")
                    v = dt.datetime.strptime(r["valid_utc"], "%Y-%m-%dT%H:%MZ")
                    self.assertGreaterEqual(c, P.FIRST_CYCLE)
                    self.assertLessEqual(v, P.LIMIT)
                    self.assertTrue(all(math.isfinite(float(r[f"v{k}"])) for k in range(1, 5)))


if __name__ == "__main__":
    unittest.main()
