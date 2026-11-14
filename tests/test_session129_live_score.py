"""Session 129: checks of the live test's scoring script (DECISIONS D105.5, D123.4(b)).

Everything here runs on tiny synthetic logs and synthetic observations, in temporary git
repositories that are deleted after. No network call is made, no real observation is read and no
file of MLwx-live is opened. Where a date after 2026-10-12 appears, its values are made up.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import argparse
import contextlib
import datetime as dt
import io
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import session129_live_score as m  # noqa: E402
from mlwx import prediction_log  # noqa: E402

HOUR, DAY = m.HOUR, m.DAY
SHA, COMMIT = "a" * 64, "b" * 40
FAR = dt.datetime(2100, 1, 1)


def entry_text(entry_id):
    """One DECISIONS entry's text, from whichever file holds it (live or archive)."""
    for name in ("DECISIONS.md", "DECISIONS-archive.md"):
        text = (ROOT / name).read_text()
        hit = re.search(rf"^\*\*{re.escape(entry_id)}\. ", text, re.M)
        if hit:
            end = re.search(r"^## ", text[hit.end():], re.M)
            return text[hit.start(): hit.end() + end.start() if end else len(text)]
    raise AssertionError(f"{entry_id} not found in either DECISIONS file")


def run_git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=test", "-c", "user.email=test@example.invalid",
                    "-c", "commit.gpgsign=false", *args], check=True, capture_output=True)


def commit_all(repo, msg="change"):
    run_git(repo, "add", "-A")
    run_git(repo, "commit", "-q", "-m", msg)


def truth(valid):
    """A made-up temperature: a daily wave plus a rise of 1 degree a day (so persistence is wrong
    by about 1 degree)."""
    days = (valid - dt.datetime(2025, 1, 1)) / DAY
    return round(10.0 + days + 4.0 * math.sin(2 * math.pi * valid.hour / 24.0), 3)


def log_rows(icao, cycle, corr_err=0.1, raw_err=1.0, issued=None, leads=m.LEADS, sha=SHA, commit=COMMIT):
    """One airport's rows for one cycle: corrected is the truth plus corr_err, raw GFS plus raw_err."""
    issued = issued or cycle + dt.timedelta(hours=4, minutes=10)
    out = []
    for n in leads:
        v = cycle + n * HOUR
        base = truth(v) + corr_err - 0.05
        out.append({"airport": icao, "cycle": cycle, "lead": n, "valid": v, "raw_gfs": truth(v) + raw_err,
                    "baseline": base, "b": 0.05, "corrected": base + 0.05, "gfs_version": "v16",
                    "model_sha256": sha, "code_commit": commit, "issued": issued})
    return out


class Repo:
    """A temporary git repository shaped like MLwx-live."""

    def __init__(self, case):
        self.path = Path(tempfile.mkdtemp(prefix="session129_test_"))
        case.addCleanup(shutil.rmtree, self.path, ignore_errors=True)
        run_git(self.path, "init", "-q")

    def add_cycle(self, cycle, rows, commit=True):
        prediction_log.write_log(prediction_log.log_path(self.path, "gfs", cycle), rows)
        if commit:
            commit_all(self.path, f"cycle {cycle:%Y%m%d%H}")

    def write(self, rel, text, commit=True):
        p = self.path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
        if commit:
            commit_all(self.path, f"write {rel}")


def setup_for(aps, last_cycle, label="T", last_valid=FAR):
    return m.Setup(label, aps, last_cycle, last_valid, {})


def table_obs(first, last, limit=FAR, drop=()):
    by = {}
    t = first
    while t <= last:
        by[t] = None if t in drop else truth(t)
        t += HOUR
    return m.TableObs(by, limit)


C0 = dt.datetime(2025, 1, 1, 18)
AP = m.Ap("TEST", "TEST", "UTC", "g", C0)
OBS = table_obs(dt.datetime(2024, 12, 25), dt.datetime(2025, 1, 12))


def simple_repo(case, cycles, **kw):
    repo = Repo(case)
    for c in cycles:
        repo.add_cycle(c, log_rows("TEST", c, **kw))
    return repo


def score_one(repo, setup, obs=OBS):
    inv = m.inventory(repo.path, setup)
    return inv, m.score_setup(setup, inv, {a.icao: obs for a in setup.airports})


class WriteOnce(unittest.TestCase):
    """D105.5(a), D123.4(b): a log file changed or deleted in history stops the look."""

    def test_clean_history_passes(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        self.assertTrue(inv["passes"])
        self.assertEqual((len(inv["files"]), inv["not_write_once"], inv["problems"]), (2, [], []))

    def test_a_changed_file_fails(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        p = prediction_log.log_path(repo.path, "gfs", C0)
        p.write_text(p.read_text() + "\n")
        commit_all(repo.path)
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        self.assertFalse(inv["passes"])
        self.assertEqual([x[0] for x in inv["not_write_once"]], ["log/2025/01/gfs_2025010118.csv"])

    def test_a_file_changed_and_put_back_still_fails(self):
        repo = simple_repo(self, [C0])
        p = prediction_log.log_path(repo.path, "gfs", C0)
        text = p.read_text()
        p.write_text(text.replace("v16", "v17"))
        commit_all(repo.path)
        p.write_text(text)
        commit_all(repo.path)
        self.assertFalse(m.inventory(repo.path, setup_for([AP], C0))["passes"])

    def test_a_deleted_file_fails(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        prediction_log.log_path(repo.path, "gfs", C0).unlink()
        commit_all(repo.path)
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        self.assertFalse(inv["passes"])
        self.assertEqual(len(inv["not_write_once"]), 1)

    def test_a_renamed_file_fails(self):
        repo = simple_repo(self, [C0])
        run_git(repo.path, "mv", "log/2025/01/gfs_2025010118.csv", "log/2025/01/gfs_2025010200.csv")
        commit_all(repo.path)
        self.assertFalse(m.inventory(repo.path, setup_for([AP], C0))["passes"])

    def test_a_merge_that_changes_no_log_file_passes(self):
        repo = simple_repo(self, [C0])
        run_git(repo.path, "checkout", "-q", "-b", "side")
        repo.write("README.md", "side\n")
        run_git(repo.path, "checkout", "-q", "-")
        repo.add_cycle(C0 + m.STEP, log_rows("TEST", C0 + m.STEP))
        run_git(repo.path, "merge", "-q", "--no-ff", "-m", "merge", "side")
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        self.assertTrue(inv["passes"])
        self.assertEqual(inv["commits"], 4)

    def test_a_shallow_clone_fails(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        shallow = Path(tempfile.mkdtemp(prefix="session129_test_"))
        self.addCleanup(shutil.rmtree, shallow, ignore_errors=True)
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{repo.path}", str(shallow / "c")], check=True,
                       capture_output=True)
        inv = m.inventory(shallow / "c", setup_for([AP], C0 + m.STEP))
        self.assertTrue(inv["shallow"])
        self.assertFalse(inv["passes"])

    def test_a_file_not_in_the_logs_form_fails(self):
        repo = simple_repo(self, [C0])
        bad = log_rows("TEST", C0 + m.STEP)
        bad[0]["valid"] += HOUR                      # not cycle + lead
        bad.append(dict(bad[5]))                     # the same airport and lead twice
        repo.add_cycle(C0 + m.STEP, bad)
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        self.assertFalse(inv["passes"])
        self.assertEqual(len(inv["problems"]), 2)

    def test_parse_log_text_problems(self):
        good = "\n".join([",".join(prediction_log.LOG_COLUMNS)]
                         + [",".join(prediction_log.row_values(r)) for r in log_rows("TEST", C0)]) + "\n"
        rows, problems = m.parse_log_text(good, C0)
        self.assertEqual((len(rows), problems), (46, []))
        self.assertEqual(m.parse_log_text(good, C0 + m.STEP)[0], [])           # every row names another cycle
        self.assertEqual(len(m.parse_log_text(good, C0 + m.STEP)[1]), 46)
        self.assertEqual(m.parse_log_text("a,b\n1,2\n", C0), ([], ["its columns are not the log's"]))
        self.assertEqual(len(m.parse_log_text(good.replace(",3,", ",2,", 1), C0)[1]), 1)     # lead 2
        self.assertEqual(len(m.parse_log_text(good + "x,y\n", C0)[1]), 1)

    def test_cycle_of_path(self):
        self.assertEqual(m.cycle_of_path("log/2026/10/gfs_2026101212.csv"), dt.datetime(2026, 10, 12, 12))
        for p in ("log/2026/10/gfs_2026101212_fix.csv", "log/2026/11/gfs_2026101212.csv",
                  "log/2026/10/gfs_2026101203.csv", "log/gfs_2026101212.csv", "log/2026/10/ifs_2026101212.csv",
                  "log/2026/13/gfs_2026131212.csv", "obs/2026/10/gfs_2026101212.csv"):
            self.assertIsNone(m.cycle_of_path(p), p)


class SecondFile(unittest.TestCase):
    """D105.5(a), D123.4(b): a second file for one cycle is reported, never scored."""

    def test_reported_and_not_scored(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        setup = setup_for([AP], C0 + m.STEP)
        _, before = score_one(repo, setup)
        own = prediction_log.log_path(repo.path, "gfs", C0)
        repo.write("log/2025/01/gfs_2025010118_corrected.csv", own.read_text().replace("v16", "v99"))
        repo.write("log/notes.txt", "not a log file\n")
        inv, after = score_one(repo, setup)
        self.assertTrue(inv["passes"])
        self.assertEqual(sorted(inv["other_files"]), [("log/2025/01/gfs_2025010118_corrected.csv", "2025010118"),
                                                      ("log/notes.txt", "")])
        self.assertEqual(len(inv["files"]), 2)
        self.assertEqual(before[1:], after[1:])                  # scores, bar and descriptive rows unchanged
        text = "\n".join(m.inventory_lines(inv, setup))
        self.assertIn("a second file for cycle 2025010118", text)
        self.assertIn("never scored", text)


class Windows(unittest.TestCase):
    """D105.5(d), (e), D123.3: the periods, the v17 boundary and the last valid hour."""

    def test_parse_v17(self):
        self.assertIsNone(m.parse_v17("none"))
        self.assertEqual(m.parse_v17("2027020112"), dt.datetime(2027, 2, 1, 12))
        self.assertEqual(m.parse_v17("2026101218"), dt.datetime(2026, 10, 12, 18))
        self.assertEqual(m.parse_v17("2027073118"), dt.datetime(2027, 7, 31, 18))
        for bad in ("2026101212", "2026101206", "2026080100", "2027020113", "2027080100", "2027-02-01T12",
                    "20270201", "v17", "", None, "2027023012", "None"):
            with self.assertRaises(m.Refusal, msg=repr(bad)):
                m.parse_v17(bad)

    def test_periods(self):
        v17 = dt.datetime(2027, 2, 1, 12)
        a, b, whole = m.live_setup("A", v17), m.live_setup("B", v17), m.live_setup("A", None)
        self.assertEqual(a.last_cycle, dt.datetime(2027, 2, 1, 6))
        self.assertEqual(b.last_cycle, dt.datetime(2027, 7, 31, 18))
        self.assertEqual(whole.last_cycle, dt.datetime(2027, 7, 31, 18))
        self.assertEqual({x.start for x in b.airports}, {v17})
        self.assertEqual({(x.group, x.start) for x in a.airports},
                         {("12", dt.datetime(2026, 10, 12, 12)), ("37", dt.datetime(2026, 10, 13, 18))})
        self.assertEqual(m.period_last_valid(a), dt.datetime(2027, 2, 3, 6))
        self.assertEqual(m.period_last_valid(whole), dt.datetime(2027, 7, 31, 23))
        with self.assertRaises(m.Refusal):
            m.live_setup("B", None)
        with self.assertRaises(m.Refusal):
            m.live_setup("C", v17)

    def test_the_12_and_the_37(self):
        aps = m.live_airports()
        self.assertEqual([a.group for a in aps].count("12"), 12)
        self.assertEqual([a.group for a in aps].count("37"), 37)
        self.assertEqual(len({a.icao for a in aps}), 49)
        self.assertEqual({a.icao for a in aps if a.group == "12"},
                         {"EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK",
                          "NZWN"})                                # D103.4

    def test_v17_splits_rows_and_days_by_their_cycle(self):
        v17 = dt.datetime(2027, 2, 1, 12)
        cycles = [v17 - 3 * m.STEP + k * m.STEP for k in range(8)]         # 01-31T18 ... 02-02T12
        repo = Repo(self)
        for c in cycles:
            repo.add_cycle(c, log_rows("EGLC", c), commit=False)
        commit_all(repo.path)
        obs = table_obs(dt.datetime(2027, 1, 20), dt.datetime(2027, 2, 10))
        base = [a for a in m.live_airports() if a.icao == "EGLC"]
        res = {}
        for label in ("A", "B"):
            full = m.live_setup(label, v17)
            setup = full._replace(airports=[a._replace(start=max(a.start, cycles[0])) for a in full.airports
                                            if a.icao == "EGLC"], recorded_starts={})
            inv = m.inventory(repo.path, setup)
            res[label] = m.score_airport(setup.airports[0], inv["rows"]["EGLC"], obs, setup, set(inv["info"]))
        self.assertEqual(len(base), 1)
        cyc = {k: sorted({r[1] for recs in res[k]["hourly"].values() for r in recs}) for k in res}
        self.assertEqual(cyc["A"], cycles[:3])
        self.assertEqual(cyc["B"], cycles[3:])
        # A's last cycle (02-01T06) keeps its rows valid after the boundary, to lead 48
        last_a = [r for recs in res["A"]["hourly"].values() for r in recs if r[1] == cycles[2]]
        self.assertEqual(len(last_a), 46)
        # EGLC's local day 2027-02-02 starts at 00:00 UTC, so its cycle is 02-01T18: period B.
        # Local day 2027-02-01 has cycle 01-31T18: period A, though its hours run past the boundary.
        self.assertEqual([(d["local_date"].isoformat(), stamp) for d, stamp in
                          ((d, d["cycle"].strftime("%m-%dT%H")) for d in res["A"]["days"])], [("2027-02-01", "01-31T18")])
        self.assertEqual([d["local_date"].isoformat() for d in res["B"]["days"][:2]], ["2027-02-02", "2027-02-03"])
        self.assertEqual([d["local_date"].isoformat() for d in res["B"]["days"] if d["curve"] is not None],
                         ["2027-02-02"])                             # later days have no logged cycle here
        self.assertEqual(res["B"]["counts"]["rows before the airport's first cycle"], 3 * 46)
        self.assertEqual(res["A"]["counts"]["rows after the period's last cycle"], 5 * 46)

    def test_nothing_valid_after_the_last_hour_is_used(self):
        cycles = [dt.datetime(2027, 7, 30, 18) + k * m.STEP for k in range(5)]      # to 07-31T18
        repo = Repo(self)
        for c in cycles:
            repo.add_cycle(c, log_rows("EGLC", c), commit=False)
        commit_all(repo.path)
        seen = []

        class Watch(m.TableObs):
            def get(self, valid, default=None):
                seen.append(valid)
                return super().get(valid, default)

        by = table_obs(dt.datetime(2027, 7, 20), dt.datetime(2027, 8, 5)).by_valid
        full = m.live_setup("A", None)
        setup = full._replace(airports=[a._replace(start=cycles[0]) for a in full.airports if a.icao == "EGLC"],
                              recorded_starts={})
        inv = m.inventory(repo.path, setup)
        res = m.score_airport(setup.airports[0], inv["rows"]["EGLC"], Watch(by, FAR), setup, set(inv["info"]))
        self.assertEqual(setup.last_valid, dt.datetime(2027, 7, 31, 23))
        self.assertLessEqual(max(seen), setup.last_valid)
        used = [r[1] + n * HOUR for (h, n), recs in res["hourly"].items() for r in recs]
        self.assertEqual(max(used), setup.last_valid)
        late = sum(1 for c in cycles for n in m.LEADS if c + n * HOUR > setup.last_valid)
        self.assertEqual(res["counts"]["rows valid after the last valid hour (not used)"], late)
        self.assertEqual(len(used), 5 * 46 - late)
        # EGLC is on summer time: local 08-01 runs 07-31T23 to 08-01T22 UTC, so it is not used.
        self.assertEqual([d["local_date"].isoformat() for d in res["days"]], ["2027-07-31"])
        self.assertEqual(res["counts"]["days whose last hour is after the last valid hour (not used)"], 1)
        with self.assertRaises(SystemExit):
            m.ObsLookup(None, setup.last_valid).get(setup.last_valid + HOUR)
        with self.assertRaises(SystemExit):
            m.TableObs({}, m.GATE_LIMIT).get(m.GATE_LIMIT)


class Bar(unittest.TestCase):
    """D105.5(c), (g), D79.1, D79.2: the bar, on numbers small enough to check by hand."""

    def setUp(self):
        self.cycles = [C0 + k * m.STEP for k in range(8)]          # 01-01T18 ... 01-03T12

    def test_numbers(self):
        repo = simple_repo(self, self.cycles, corr_err=0.1, raw_err=1.0)
        setup = setup_for([AP], self.cycles[-1])
        _, (results, cells, bars, desc) = score_one(repo, setup)
        hourly = {r["half"]: r for r in bars if r["output"] == "hourly"}
        self.assertEqual(hourly["raw_gfs"]["n"], 8 * 46)
        self.assertAlmostEqual(hourly["raw_gfs"]["curve_mae"], 0.1, places=9)
        self.assertAlmostEqual(hourly["raw_gfs"]["other_mae"], 1.0, places=9)
        self.assertAlmostEqual(hourly["raw_gfs"]["margin_pct"], 90.0, places=6)
        self.assertAlmostEqual(hourly["raw_gfs"]["diff_c"], 0.9, places=9)
        # 1 degree a day: 21 leads at 1 day back, 24 at 2 days and lead 48 at 3 days (D100.5)
        self.assertAlmostEqual(hourly["persistence"]["other_mae"], (21 * 1 + 24 * 2 + 3) / 46, places=6)
        self.assertTrue(all(r["half_pass"] and r["verdict"] == "PASS" for r in bars))
        daily = {r["half"]: r for r in bars if r["output"] == "daily"}
        self.assertEqual(daily["raw_gfs"]["n"], 2)                                     # local days 01-02, 01-03
        self.assertAlmostEqual(daily["raw_gfs"]["curve_mae"], 0.1, places=9)
        self.assertEqual(len(cells), 4 * 46 * 5 + 5)
        self.assertEqual(sum(r[9] for r in cells if r[4:7] == ["hourly", "curve", "common"]), 8 * 46)
        base = [r for r in desc if r[4:8] == ["hourly", "all", "", "baseline"]][0]
        self.assertAlmostEqual(base[9], 0.05, places=9)                                # the baseline without b
        self.assertAlmostEqual(base[10], -0.05, places=9)                              # mean error, obs - forecast
        bands = {r[6]: r[8] for r in desc if r[4:6] == ["hourly", "leads"] and r[7] == "corrected"}
        self.assertEqual(bands, {"3-24": 8 * 22, "25-48": 8 * 24})
        hours = {r[6]: r[8] for r in desc if r[4:6] == ["hourly", "cycle_hour"] and r[7] == "corrected"}
        self.assertEqual(hours, {"00": 92, "06": 92, "12": 92, "18": 92})
        lines = m.claim_lines(bars, setup)
        self.assertIn("smallest margin +90.000 % (+0.9000 degrees C), TEST against", lines[0])
        self.assertIn("passes at 1 of 1 airports", lines[0])

    def test_a_tie_fails(self):
        repo = simple_repo(self, self.cycles, corr_err=1.0, raw_err=1.0)
        # make corrected equal raw GFS exactly
        repo2 = Repo(self)
        for c in self.cycles:
            rows = log_rows("TEST", c)
            for r in rows:
                r["corrected"] = r["raw_gfs"]
            repo2.add_cycle(c, rows, commit=False)
        commit_all(repo2.path)
        del repo
        _, (_, _, bars, _) = score_one(repo2, setup_for([AP], self.cycles[-1]))
        raw = [r for r in bars if r["half"] == "raw_gfs"]
        self.assertEqual([(r["curve_mae"] == r["other_mae"], r["half_pass"], r["margin_pct"]) for r in raw],
                         [(True, False, 0.0)] * 2)
        self.assertEqual({r["verdict"] for r in bars}, {"FAIL"})
        self.assertFalse(m.s106.half_pass(1.0, 1.0))
        self.assertFalse(m.s106.half_pass(None, 1.0))

    def test_a_half_with_no_rows_cannot_pass(self):
        repo = simple_repo(self, self.cycles[:1])
        setup = setup_for([AP], self.cycles[0])
        _, (_, _, bars, _) = score_one(repo, setup, table_obs(C0, C0 + 60 * HOUR))     # nothing before the cycle
        pers = [r for r in bars if r["output"] == "hourly" and r["half"] == "persistence"][0]
        self.assertEqual((pers["n"], pers["curve_mae"], pers["margin_pct"], pers["half_pass"]), (0, None, None, False))
        self.assertEqual({r["verdict"] for r in bars}, {"FAIL"})
        self.assertIn("halves with no rows (cannot pass)", m.claim_lines(bars, setup)[0])

    def test_persistence_uses_the_cycle_not_the_issue_time(self):
        late = C0 + dt.timedelta(hours=30)
        repo = Repo(self)
        repo.add_cycle(C0, log_rows("TEST", C0, issued=late))
        _, (results, _, _, _) = score_one(repo, setup_for([AP], C0))
        for (h, n), recs in results[0]["hourly"].items():
            for r in recs:
                k = 1 if n <= 23 else 2 if n <= 47 else 3                               # D100.5
                self.assertEqual(r[6], truth(r[1] + n * HOUR - k * DAY), (n, k))
        self.assertEqual(results[0]["late_by_lead"], {n: 1 for n in range(3, 30)})      # issued after valid
        self.assertEqual(results[0]["counts"]["rows scored (the common set)"], 46)     # counted, never dropped

    def test_two_groups_are_reported_apart(self):
        aps = [m.Ap("AAAA", "AAAA", "UTC", "12", C0), m.Ap("BBBB", "BBBB", "UTC", "37", C0),
               m.Ap("CCCC", "CCCC", "UTC", "37", C0)]
        repo = Repo(self)
        for c in self.cycles:
            repo.add_cycle(c, log_rows("AAAA", c) + log_rows("BBBB", c) + log_rows("CCCC", c, corr_err=2.0),
                           commit=False)
        commit_all(repo.path)
        setup = setup_for(aps, self.cycles[-1], label="A")
        _, (_, _, bars, _) = score_one(repo, setup)
        lines = m.claim_lines(bars, setup)
        self.assertEqual(len(lines), 5)
        self.assertIn("period A, hourly, group of 12:", lines[0])
        self.assertIn("passes at 1 of 1 airports", lines[0])
        self.assertIn("period A, hourly, group of 37:", lines[1])
        self.assertIn("passes at 1 of 2 airports; FAIL: CCCC", lines[1])
        self.assertIn("smallest margin -100.000 %", lines[1])                           # the failing margin leads
        self.assertIn("NOT MET", lines[4])                                              # 1 airport is not all 12


class Counted(unittest.TestCase):
    """D105.5(h), D123.4(b): a missing cycle and a late row are counted, never dropped."""

    def test_missing_cycle_and_its_reason(self):
        cycles = [C0 + k * m.STEP for k in range(6)]
        repo = Repo(self)
        for c in cycles:
            if c not in (cycles[2], cycles[4]):
                repo.add_cycle(c, log_rows("TEST", c))
        repo.write("state/tracker_gfs.json", '{"stops": [{"cycle": "2025-01-02T06:00Z", "reason": "guard stop: x", '
                   '"at": "2025-01-02T12:00Z"}]}\n')
        repo.write("state/tracker_gfs.json", '{"stops": []}\n')                        # the stop has dropped off
        setup = setup_for([AP], cycles[-1])
        inv = m.inventory(repo.path, setup)
        g = inv["groups"]["g"]
        self.assertTrue(inv["passes"])
        self.assertEqual((g["window"], g["with_file"]), (6, 4))
        self.assertEqual(g["missing"], [(cycles[2], ["guard stop: x"]), (cycles[4], [m.NO_REASON])])
        self.assertEqual(inv["state_versions"], 2)
        text = "\n".join(m.inventory_lines(inv, setup))
        self.assertIn("with a log file 4, without 2", text)
        self.assertIn("1 x guard stop: x", text)

    def test_a_day_whose_cycle_is_missing_is_counted_not_filled(self):
        cycles = [C0 + k * m.STEP for k in range(9)]                # 01-01T18 ... 01-03T18
        repo = Repo(self)
        for c in cycles:
            if c != cycles[4]:                                      # 01-02T18, the cycle of local day 01-03
                repo.add_cycle(c, log_rows("TEST", c), commit=False)
        commit_all(repo.path)
        _, (results, _, bars, _) = score_one(repo, setup_for([AP], cycles[-1]))
        days = {d["local_date"].isoformat(): d for d in results[0]["days"]}
        self.assertEqual(sorted(days), ["2025-01-02", "2025-01-03", "2025-01-04"])
        self.assertIsNone(days["2025-01-03"]["curve"])
        self.assertEqual(days["2025-01-03"]["curve_reason"], "no log file for the day's cycle")
        self.assertFalse(days["2025-01-03"]["common"])
        self.assertEqual(results[0]["counts"]["days with no forecast maximum"], 1)
        self.assertEqual([r["n"] for r in bars if r["output"] == "daily" and r["half"] == "raw_gfs"], [2])

    def test_missing_rows_and_missing_observations(self):
        repo = Repo(self)
        repo.add_cycle(C0, log_rows("TEST", C0, leads=[n for n in m.LEADS if n != 10]))
        gap = {C0 + 5 * HOUR, C0 + 20 * HOUR}
        obs = table_obs(dt.datetime(2024, 12, 25), dt.datetime(2025, 1, 12), drop=gap)
        setup = setup_for([AP], C0)
        inv, (results, _, _, _) = score_one(repo, setup, obs)
        self.assertEqual(inv["groups"]["g"]["short"], {"TEST": 1})
        c = results[0]["counts"]
        self.assertEqual((c["rows logged in the period"], c["rows with no observation"],
                          c["rows scored (the common set)"]), (45, 2, 43))
        day = results[0]["days"][0]
        self.assertEqual((day["local_date"].isoformat(), day["curve"], day["curve_reason"]),
                         ("2025-01-02", None, "no forecast at 1 hours"))
        self.assertEqual((day["hours"], day["usable_hours"]), (24, 23))                 # 01-02T14 has no report
        self.assertIsNotNone(day["obs_max"])                                            # 23 of 24 is usable

    def test_issue_lag(self):
        repo = Repo(self)
        repo.add_cycle(C0, log_rows("TEST", C0, issued=C0 + dt.timedelta(hours=9, minutes=30)))
        repo.add_cycle(C0 + m.STEP, log_rows("TEST", C0 + m.STEP))
        inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        g = inv["groups"]["g"]
        self.assertEqual([round(x, 3) for _, x in g["lags"]], [9.5, 4.167])
        self.assertEqual(g["late_by_lead"], {3: 2, 4: 2, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1})


class EdgeDays(unittest.TestCase):
    """D105.5(i), D123.4(b): a day whose maximum is at a local-day edge is counted and scored apart."""

    def test_rule_equals_session_112(self):
        import session112_analysis as s112
        rng = random.Random(129)
        for _ in range(300):
            n = rng.choice((23, 24, 25))
            vals = [rng.choice((1.0, 2.0, 3.0, 3.0)) for _ in range(n)]
            self.assertEqual(m.peak_hour(vals), s112.peak_index(vals))
            self.assertEqual(m.edge_hour(m.peak_hour(vals), n), s112.is_edge(s112.peak_index(vals), n))
        self.assertEqual(m.peak_hour([None, 2.0, 2.0, None]), 1)                        # the first hour wins
        self.assertEqual(m.peak_hour([None, None]), None)
        self.assertFalse(m.edge_hour(None, 24))

    def test_edge_day_counted_and_scored_apart(self):
        cycles = [C0 + k * m.STEP for k in range(5)]                # days 01-02 (cycle 01-01T18), 01-03
        repo = simple_repo(self, cycles)
        by = dict(OBS.by_valid)
        by[dt.datetime(2025, 1, 2, 0)] = 99.0                       # the first hour of local day 01-02
        setup = setup_for([AP], cycles[-1])
        _, (results, _, bars, desc) = score_one(repo, setup, m.TableObs(by, FAR))
        days = {d["local_date"].isoformat(): d for d in results[0]["days"]}
        self.assertEqual([(d["obs_edge"], d["edge_day"], d["common"]) for d in days.values()],
                         [(True, True, True), (False, False, True)])
        self.assertEqual(results[0]["counts"]["scored days with a maximum in the first or last hour"], 1)
        self.assertEqual([r["n"] for r in bars if r["output"] == "daily" and r["half"] == "raw_gfs"], [2])  # in the bar
        split = {(r[5], r[6]): r[8] for r in desc if r[4] == "daily" and r[7] == "corrected"}
        self.assertEqual((split[("edge_day", "true")], split[("edge_day", "false")]), (1, 1))
        self.assertEqual((split[("obs_edge", "true")], split[("corrected_edge", "true")]), (1, 0))

    def test_forecast_edge(self):
        repo = Repo(self)
        rows = log_rows("TEST", C0)
        rows[26]["corrected"] = 99.0                                # lead 29: 01-02T23:00, the last hour
        repo.add_cycle(C0, rows)
        _, (results, _, _, _) = score_one(repo, setup_for([AP], C0))
        d = results[0]["days"][0]
        self.assertEqual((d["curve"], d["curve_edge"], d["raw_gfs_edge"], d["obs_edge"], d["edge_day"]),
                         (99.0, True, False, False, True))


class NoObsFolderRead(unittest.TestCase):
    """D105.6, the session's rule: --inventory lists the names under obs/ and never opens one."""

    def test_inventory_never_opens_an_obs_file(self):
        repo = simple_repo(self, [C0, C0 + m.STEP])
        repo.write("obs/2025/01/gfs_2025010118.csv", "airport,valid_utc,obs_c,report_utc\nTEST,2025-01-01T12:00Z,1.0,\n")
        repo.write("obs/2025/01/gfs_2025010200.csv", "airport,valid_utc,obs_c,report_utc\n")
        read = []
        real = m.Blobs.read

        def spy(self_, rev, path):
            read.append(path)
            return real(self_, rev, path)

        m.Blobs.read = spy
        try:
            inv = m.inventory(repo.path, setup_for([AP], C0 + m.STEP))
        finally:
            m.Blobs.read = real
        self.assertEqual((inv["obs_names"], inv["opened"].get("obs", 0), inv["opened"]["log"]), (2, 0, 2))
        self.assertEqual(sorted({p.split("/")[0] for p in read}), ["log"])
        self.assertIn("names listed under obs/: 2; obs/ files opened: 0", "\n".join(
            m.inventory_lines(inv, setup_for([AP], C0 + m.STEP))))

    def test_the_reader_refuses_obs(self):
        repo = simple_repo(self, [C0])
        repo.write("obs/2025/01/gfs_2025010118.csv", "airport,valid_utc,obs_c,report_utc\n")
        blobs = m.Blobs(repo.path)
        self.addCleanup(blobs.close)
        with self.assertRaises(SystemExit):
            blobs.read("HEAD", "obs/2025/01/gfs_2025010118.csv")
        with self.assertRaises(SystemExit):
            blobs.read("HEAD", "README.md")
        self.assertEqual(blobs.opened.get("obs", 0), 0)
        self.assertTrue(blobs.read("HEAD", "log/2025/01/gfs_2025010118.csv").startswith(b"airport,"))

    def test_run_inventory_source_has_no_obs_read(self):
        src = (ROOT / "scripts" / "session129_live_score.py").read_text()
        self.assertEqual(src.count("allow_obs()"), 1 + 1)           # its definition and the one call, in the look
        body = src[src.index("def snapshot_agreement"):src.index("# ------------------------------------------------------------------ --inventory")]
        self.assertIn("blobs.allow_obs()", body)


def iem_text(station, d0, d1, shift=0.0, extra=""):
    """A made-up IEM response: one report on every hour."""
    out = ["station,valid,lon,lat,elevation,tmpc,dwpc"]
    t = dt.datetime(d0.year, d0.month, d0.day)
    while t < dt.datetime(d1.year, d1.month, d1.day) + DAY:
        out.append(f"{station},{t:%Y-%m-%d %H:%M},0,0,0,{truth(t) + shift:.3f},M")
        t += HOUR
    return "\n".join(out) + "\n" + extra


class Observations(unittest.TestCase):
    """D105.5(f): the requests, and the live pairing (F152.7 ruling 2)."""

    def test_month_chunks(self):
        got = m.month_chunks(dt.date(2026, 10, 8), dt.date(2027, 1, 3))
        self.assertEqual(got, [(dt.date(2026, 10, 8), dt.date(2026, 10, 31)), (dt.date(2026, 11, 1), dt.date(2026, 11, 30)),
                               (dt.date(2026, 12, 1), dt.date(2026, 12, 31)), (dt.date(2027, 1, 1), dt.date(2027, 1, 3))])
        self.assertEqual(m.month_chunks(dt.date(2027, 2, 3), dt.date(2027, 2, 3)), [(dt.date(2027, 2, 3),) * 2])

    def test_fetch_uses_the_live_pairing_and_saves_the_raw_text(self):
        tmp = Path(tempfile.mkdtemp(prefix="session129_test_"))
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        calls = []

        def fetch(station, d0, d1):
            calls.append((station, d0, d1))
            # two rows share 2025-01-02 05:00 with different values: that time is ignored (F152.7)
            return iem_text(station, d0, d1, extra=f"{station},2025-01-02 05:00,0,0,0,50.0,M\n"
                                                   f"{station},2025-01-02 05:10,0,0,0,7.5,M\n"
                            if d0.month == 1 else "")

        setup = setup_for([AP], C0, last_valid=dt.datetime(2025, 1, 3, 18))
        obs = m.fetch_observations(setup, tmp / "raw", fetch, log=lambda *a, **k: None)
        self.assertEqual(calls, [("TEST", dt.date(2024, 12, 28), dt.date(2024, 12, 31)),
                                 ("TEST", dt.date(2025, 1, 1), dt.date(2025, 1, 4))])
        look = obs["TEST"]
        self.assertTrue(look.reports.live)
        self.assertEqual(look.get(dt.datetime(2025, 1, 2, 5)), 7.5)
        self.assertEqual(look.get(dt.datetime(2025, 1, 2, 6)), truth(dt.datetime(2025, 1, 2, 6)))
        self.assertEqual(look.get(dt.datetime(2024, 12, 31, 23)), truth(dt.datetime(2024, 12, 31, 23)))
        self.assertIsNone(look.get(dt.datetime(2024, 12, 20, 0)))                        # no report: never filled
        with self.assertRaises(SystemExit):
            look.get(dt.datetime(2025, 1, 3, 19))
        names = sorted(p.name for p in (tmp / "raw").iterdir())
        self.assertEqual(names, ["TEST_20241228_20241231.csv", "TEST_20250101_20250104.csv", "requests.csv"])
        with self.assertRaises(FileExistsError):
            m.fetch_observations(setup, tmp / "raw", fetch, log=lambda *a, **k: None)


class ScoreRefusals(unittest.TestCase):
    """D123.3: --score's refusals, each before any observation is fetched. No network."""

    def setUp(self):
        self.home = Path(tempfile.mkdtemp(prefix="session129_test_"))
        self.addCleanup(shutil.rmtree, self.home, ignore_errors=True)
        run_git(self.home, "init", "-q")
        (self.home / "scripts").mkdir()
        self.script = self.home / "scripts" / "the_script.py"
        self.script.write_text("# a stand-in for the committed script\n")
        commit_all(self.home)
        self.fetched = []

    def fetch(self, station, d0, d1):
        self.fetched.append(station)
        raise AssertionError("an observation was fetched")

    def score(self, clone, period="A", v17="none", now=dt.datetime(2027, 9, 1), fetch=None):
        args = argparse.Namespace(score=str(clone), period=period, first_v17_cycle=v17)
        with contextlib.redirect_stdout(io.StringIO()):
            return m.run_score(args, now=now, fetch=fetch or self.fetch, out_root=self.home, script=self.script,
                               repo_root=self.home)

    def test_script_committed(self):
        self.assertEqual(m.script_committed(self.script, self.home), m.sha256_file(self.script))
        self.script.write_text("# edited\n")
        with self.assertRaisesRegex(m.Refusal, "differs from its committed version"):
            m.script_committed(self.script, self.home)
        new = self.home / "scripts" / "untracked.py"
        new.write_text("# new\n")
        with self.assertRaisesRegex(m.Refusal, "is not committed"):
            m.script_committed(new, self.home)

    def test_dirty_script_refused_first(self):
        self.script.write_text("# edited\n")
        with self.assertRaisesRegex(m.Refusal, "differs from its committed version"):
            self.score(self.home / "no-such-clone", v17="garbage", now=dt.datetime(2026, 11, 14))
        self.assertEqual(self.fetched, [])

    def test_bad_v17_refused(self):
        for bad in ("2026101212", "2027020113", "tomorrow", "2027080100"):
            with self.assertRaises(m.Refusal):
                self.score(self.home / "no-such-clone", v17=bad)
        with self.assertRaisesRegex(m.Refusal, "period B exists only if"):
            self.score(self.home / "no-such-clone", period="B", v17="none")
        self.assertEqual(self.fetched, [])

    def test_period_not_ended_refused(self):
        with self.assertRaisesRegex(m.Refusal, r"not run before 2027-08-07T23:00Z"):
            self.score(self.home / "no-such-clone", now=dt.datetime(2026, 11, 14))
        with self.assertRaisesRegex(m.Refusal, "D105.5\\(f\\)"):
            self.score(self.home / "no-such-clone", now=dt.datetime(2027, 8, 7, 22, 59))
        # period A ends at v17: last cycle 2027-02-01T06, last valid hour +48 h, then 7 days
        with self.assertRaisesRegex(m.Refusal, r"not run before 2027-02-10T06:00Z"):
            self.score(self.home / "no-such-clone", v17="2027020112", now=dt.datetime(2027, 2, 10, 5))
        self.assertEqual(self.fetched, [])

    def test_failed_inventory_refused(self):
        clone = simple_repo(self, [C0])
        p = prediction_log.log_path(clone.path, "gfs", C0)
        p.write_text(p.read_text().replace("v16", "v17"))
        commit_all(clone.path)
        with self.assertRaisesRegex(m.Refusal, "the inventory fails"):
            self.score(clone.path)
        self.assertEqual(self.fetched, [])
        self.assertFalse((self.home / "data").exists())

    def test_existing_output_refused(self):
        out_dir, _ = m.score_dirs(self.home, "A")
        out_dir.mkdir(parents=True)
        with self.assertRaisesRegex(m.Refusal, "already exists"):
            self.score(self.home / "no-such-clone")

    def test_command_line_needs_period_and_v17(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(m.main(["--score", str(self.home)]), 2)
            self.assertEqual(m.main(["--score", str(self.home), "--period", "A"]), 2)


class WholeLook(ScoreRefusals):
    """The whole --score path on a made-up clone of 49 airports, with a made-up IEM. It checks
    that the look runs end to end, writes each file once, and opens obs/ only after the scores."""

    def test_end_to_end(self):
        aps = m.live_airports()
        clone = Repo(self)
        c = m.START_12
        v17 = dt.datetime(2026, 10, 14, 0)
        while c < v17 + 2 * m.STEP:                                  # two cycles of period B as well
            rows = []
            for a in aps:
                if c >= a.start:
                    rows += log_rows(a.icao, c, sha=SHA if c < m.START_37 else "c" * 64)
            clone.add_cycle(c, rows, commit=False)
            c += m.STEP
        commit_all(clone.path)
        valid = dt.datetime(2026, 10, 13, 12)
        clone.write("obs/2026/10/gfs_2026101318.csv", "airport,valid_utc,obs_c,report_utc\n"
                    f"EGLC,{m.stamp(valid)},{truth(valid)!r},{m.stamp(valid)}\n"
                    f"EGLC,{m.stamp(valid + HOUR)},{truth(valid + HOUR) + 1!r},{m.stamp(valid + HOUR)}\n"
                    f"EGLC,{m.stamp(valid + 2 * HOUR)},,\n")
        clone.write("obs/2026/10/gfs_2026101406.csv", "airport,valid_utc,obs_c,report_utc\n")   # period B
        out_dir, raw_dir = m.score_dirs(self.home, "A")
        calls, order = [], []
        real = m.Blobs.read

        def spy(self_, rev, path):
            order.append((path.split("/")[0], (out_dir / "scores.csv").exists()))
            return real(self_, rev, path)

        def fetch(station, d0, d1):
            calls.append((station, d0, d1))
            return iem_text(station, d0, d1)

        m.Blobs.read = spy
        try:
            code = self.score(clone.path, v17="2026101400", now=dt.datetime(2026, 11, 1), fetch=fetch)
        finally:
            m.Blobs.read = real
        self.assertEqual(code, 0)
        self.assertEqual(len(calls), 49)
        self.assertEqual({(d0, d1) for _, d0, d1 in calls},
                         {(dt.date(2026, 10, 8), dt.date(2026, 10, 16)), (dt.date(2026, 10, 9), dt.date(2026, 10, 16))})
        self.assertEqual({top for top, _ in order}, {"log", "obs"})
        self.assertTrue(all(done for top, done in order if top == "obs"))             # obs/ only after the scores
        self.assertEqual(sum(top == "obs" for top, _ in order), 1)                     # the period's snapshot only
        names = sorted(p.name for p in out_dir.iterdir())
        self.assertEqual(names, ["counts.csv", "days.csv", "descriptive.csv", "inventory.txt", "meta.txt",
                                 "scores.csv", "verdicts.csv"])
        import csv

        def table(name):
            with open(out_dir / name, newline="") as f:
                return list(csv.DictReader(f))

        verdicts = table("verdicts.csv")
        self.assertEqual(len(verdicts), 49 * 2 * 2)
        hourly = [r for r in verdicts if r["output"] == "hourly"]
        self.assertEqual({r["verdict"] for r in hourly}, {"PASS"})
        self.assertEqual({r["period"] for r in verdicts}, {"A"})
        twelve = [r for r in hourly if r["group"] == "12" and r["half"] == "raw_gfs"]
        self.assertEqual({r["n"] for r in twelve}, {str(6 * 46)})                      # cycles 10-12T12 to 10-13T18
        self.assertEqual({r["n"] for r in hourly if r["group"] == "37" and r["half"] == "raw_gfs"}, {"46"})
        scores = table("scores.csv")
        self.assertEqual({r["method"] for r in scores}, {"raw_gfs", "baseline", "corrected", "persistence"})
        meta = (out_dir / "meta.txt").read_text()
        self.assertIn("period A, hourly, group of 12: smallest margin +90.000 %", meta)
        self.assertIn("passes at 12 of 12 airports", meta)
        self.assertIn("period A, hourly, group of 37:", meta)
        self.assertIn("passes at 37 of 37 airports", meta)
        self.assertIn("expectation (D105.5(j))", meta)
        self.assertIn("different values: 1", meta)
        self.assertIn("equal: 1", meta)
        self.assertIn("snapshot empty, fresh present: 1", meta)
        self.assertIn("snapshot files outside the period: 1", meta)
        desc = table("descriptive.csv")
        models = {r["value"] for r in desc if r["split"] == "model_and_code" and r["icao"] == "EGLC"}
        self.assertEqual(len(models), 2)                                               # per manifest and commit
        self.assertEqual(len(list(raw_dir.iterdir())), 50)
        with self.assertRaisesRegex(m.Refusal, "already exists"):                      # each look is run once
            self.score(clone.path, v17="2026101400", now=dt.datetime(2026, 11, 1), fetch=fetch)

    def test_the_37_must_start_where_the_record_says(self):
        aps = m.live_airports()
        clone = Repo(self)
        late = m.START_37 + m.STEP
        for c in (m.START_37, late):
            clone.add_cycle(c, [r for a in aps if a.group == "12" or c == late for r in log_rows(a.icao, c)],
                            commit=False)
        commit_all(clone.path)
        with self.assertRaisesRegex(m.Refusal, "the inventory fails"):
            self.score(clone.path, v17="2026101412", now=dt.datetime(2026, 11, 1))
        self.assertEqual(self.fetched, [])


class RecordedValues(unittest.TestCase):
    """D98.2: every recorded value the script holds, against the record."""

    def test_start_of_the_37(self):
        self.assertIn("**First 49-airport cycle: 2026-10-13 18z** (D105.5(d))", entry_text("F154"))
        self.assertEqual(m.START_37, dt.datetime(2026, 10, 13, 18))
        d105 = entry_text("D105")
        self.assertIn("The 12 of D103.4 start at 2026-10-12 12z", d105)
        self.assertEqual(m.START_12, dt.datetime(2026, 10, 12, 12))
        self.assertIn("or to 2027-07-31 18z if none is", d105)
        self.assertIn("Nothing valid after 2027-07-31T23:00 UTC is used", d105)
        self.assertIn("no sooner than 7 days after its last valid hour", d105)
        self.assertEqual((m.WINDOW_LAST_CYCLE, m.LAST_VALID, m.WAIT),
                         (dt.datetime(2027, 7, 31, 18), dt.datetime(2027, 7, 31, 23), dt.timedelta(days=7)))
        self.assertIn("before it reads any observation valid on or after 2026-10-12", d105)
        self.assertEqual(m.LIVE_OBS_FROM, dt.datetime(2026, 10, 12))

    def test_session_107_files(self):
        f150 = entry_text("F150")
        for name, sha in (("scores", m.S107_SCORES_SHA256), ("days", m.S107_DAYS_SHA256),
                          ("verdicts", m.S107_VERDICTS_SHA256)):
            self.assertIn(f"`data/processed/session107_claim_{name}.csv` (`{sha}`)", f150)
            self.assertEqual(m.sha256_file(ROOT / "data" / "processed" / f"session107_claim_{name}.csv"), sha)
        self.assertIn(f"`scripts/session106_claim_look.py` (`{m.S106_SCRIPT_SHA256}`)", f150)

    def test_gate_inputs(self):
        if not m.PRED_DIR.exists():
            self.skipTest("the stage C analysis folder is not on this machine")
        meta = (m.PRED_DIR / "meta.txt").read_text() + (m.PRED_DIR / "refs_meta.txt").read_text()
        for kind, table in (("pred", m.GATE_PRED), ("obs", m.GATE_OBS)):
            self.assertEqual(list(table), list(m.s106.CLAIM))
            for ic, sha in table.items():
                self.assertRegex(meta, rf"{kind}_{ic}\.csv\.gz\s.*sha256 {sha}")

    def test_the_gates_result_files(self):
        gate = ROOT / "data" / "processed" / "session129_gate"
        self.assertEqual(m.sha256_file(gate / "claim_scores_recomputed.csv"), m.S107_SCORES_SHA256)
        self.assertEqual(m.sha256_file(gate / "claim_verdicts_recomputed.csv"), m.S107_VERDICTS_SHA256)
        text = (gate / "comparison.txt").read_text()
        self.assertIn("GATE (a): PASS", text)
        self.assertNotIn("DIFFERENT:", text)

    def test_the_gate_reads_only_spent_data(self):
        self.assertEqual(m.GATE_LIMIT, dt.datetime(2026, 8, 1))
        with self.assertRaises(SystemExit):
            m.gate_time("2026-08-01T00:00Z")
        self.assertEqual(m.gate_time("2026-07-31T23:00Z"), dt.datetime(2026, 7, 31, 23))
        self.assertEqual([(l, t1 - m.STEP) for l, _, t1 in m.s106.LOOKS],
                         [("A", dt.datetime(2025, 7, 31, 18)), ("B", dt.datetime(2026, 7, 31, 18))])


if __name__ == "__main__":
    unittest.main()
