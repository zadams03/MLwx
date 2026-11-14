"""Session 131: checks of stage B's build check and scoring wrapper (DECISIONS D125.5(b), D125.5(d); register
rows SB07, SB10; D98.2).

Offline. The build check is run on drop logs and GRIB manifests that session 86's own `build_rows` and
`write_outputs` write in a temporary folder, with its requests replaced by fakes that fail in each way a
real request can (no network). The scoring wrapper's constants are checked against both DECISIONS files,
session 129's wrapper and the committed files; session 87's own model check is run through the wrapper.
No error is computed.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import contextlib
import csv
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # skip sessions 86 and 87's process restart (D93.3)

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import session131_stageb_build_check as bc  # noqa: E402
import session131_stageb_score as sw  # noqa: E402
import session86_forward_build as s86  # noqa: E402
import session129_stageb_gate as w129  # noqa: E402


def sha256_of(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def both_decisions():
    return (ROOT / "DECISIONS.md").read_text() + "\n" + (ROOT / "DECISIONS-archive.md").read_text()


# ------------------------------------------------------------------ the build check (D125.5(b))

AIRPORTS = s86.load_airports()
HEADER = "station,valid,lon,lat,elevation,tmpc,dwpc\n"


def idx_text(a, run_date, drop=()):
    """A GFS .idx for the airport's plan, every field 100 bytes long, without the fields in `drop`."""
    lines, off = [], 0
    plan = s86.field_plan(a["lead"])
    out = {}
    for fh in sorted({p[1] for p in plan}):
        lines, off, i = [], 0, 1
        for name, f, var, level, step, _ in plan:
            if f != fh or name in drop:
                continue
            lines.append(f"{i}:{off}:d={run_date:%Y%m%d}{a['cycle']:02d}:{var}:{level}:{step}:")
            off += 100
            i += 1
        lines.append(f"{i}:{off}:d={run_date:%Y%m%d}{a['cycle']:02d}:END:end:end:")
        out[fh] = ("\n".join(lines) + "\n").encode("ascii")
    return out


class FakeArchive:
    """Stands in for session 86's http_get. `days` maps a target date to how its requests behave:
    'idx404' (.idx not in the archive), 'idxnet' (.idx network failure after 3 tries), 'noline' (an .idx
    with no line for any field: a real absence, no message is requested), 'msg503' (a message request fails with HTTP 503 after 3 tries), 'msg404',
    'short' (a message shorter than its .idx says), 'decode' (a complete-looking message that does not
    decode)."""

    def __init__(self, a, days):
        self.a, self.days = a, days

    def __call__(self, url, headers=None, kind="", byte_range=None, pause=0.15):
        run_date = dt.datetime.strptime(re.search(r"gfs\.(\d{8})/", url).group(1), "%Y%m%d").date()
        how = self.days[run_date + dt.timedelta(days=1)]
        fh = int(re.search(r"\.f(\d{3})", url).group(1))
        if url.endswith(".idx"):
            if how == "idx404":
                raise RuntimeError("failed: RuntimeError('HTTP 404')")
            if how == "idxnet":
                raise RuntimeError("failed: ConnectionError('Connection reset by peer')")
            drop = [p[0] for p in s86.field_plan(self.a["lead"])] if how == "noline" else ()
            return idx_text(self.a, run_date, drop=drop)[fh], "t"
        if how == "msg503":
            raise RuntimeError("failed: RuntimeError('HTTP 503')")
        if how == "msg404":
            raise RuntimeError("failed: RuntimeError('HTTP 404')")
        if how == "short":
            return b"GRIB" + b"\0" * 10 + b"7777", "t"
        return b"GRIB" + b"\0" * 92 + b"7777", "t"          # 'decode'


def fake_iem(station, first_day, last_day, valid_limit):
    return HEADER, "iem-url", "t"


def build_files(folder, days):
    """Session 86's own build_rows and write_outputs, on EGLC target days in 2025, with fake requests."""
    a = AIRPORTS["EGLC"]
    targets = [("EGLC", d) for d in sorted(days)]
    with mock.patch.object(s86, "http_get", FakeArchive(a, days)), mock.patch.object(s86, "fetch_iem", fake_iem), \
            contextlib.redirect_stderr(io.StringIO()):
        built = s86.build_rows({"EGLC": a}, targets, s86.GATE_LIMIT, 1, "range")
    folder = Path(folder)
    dirs = {"rows": folder / "rows.csv", "rows_meta": folder / "rows.csv.meta.txt",
            "manifest": folder / "manifest.csv", "drops": folder / "drops.csv", "iem": folder / "iem"}
    s86.write_outputs(built, dirs, "session 131 test")
    return dirs


D1, D2, D3, D4 = (dt.date(2025, 6, k) for k in (2, 3, 4, 5))


class BuildCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="test_s131_"))
        self.addCleanup(shutil.rmtree, self.tmp, True)

    def run_check(self, days):
        dirs = build_files(self.tmp / "out", days)
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = bc.main(["--drops", str(dirs["drops"]), "--manifest", str(dirs["manifest"])])
        return code, out.getvalue(), bc.check(dirs["drops"], dirs["manifest"])

    def test_absent_fields_pass(self):
        """An .idx not in the archive, a missing .idx line and a message 404 are real absences: counted, PASS."""
        code, out, r = self.run_check({D1: "idx404", D2: "noline", D3: "msg404"})
        self.assertEqual(code, 0, out)
        self.assertEqual(r["by_reason"], {"no GRIB message": 3})
        self.assertEqual([len(r["by_class"][c]) for c in ("absent", "data", "fetch")], [3, 0, 0])
        self.assertIn("BUILD CHECK: PASS", out)

    def test_a_network_failure_on_an_idx_fails(self):
        code, out, r = self.run_check({D1: "idx404", D2: "idxnet"})
        self.assertEqual(code, 1, out)
        self.assertEqual(r["by_class"]["fetch"], [("EGLC", D2.isoformat())])
        self.assertIn("BUILD CHECK: FAIL", out)
        self.assertIn("move its outputs aside and keep them", out)

    def test_a_5xx_or_short_message_fails(self):
        for how in ("msg503", "short"):
            with self.subTest(how=how):
                shutil.rmtree(self.tmp / "out", ignore_errors=True)
                code, out, r = self.run_check({D1: how})
                self.assertEqual(code, 1, out)
                self.assertEqual(r["by_class"]["fetch"], [("EGLC", D1.isoformat())])

    def test_a_decode_failure_is_data_not_fetch(self):
        code, out, r = self.run_check({D1: "decode", D2: "noline"})
        self.assertEqual(code, 0, out)
        self.assertEqual(r["by_class"]["data"], [("EGLC", D1.isoformat())])
        self.assertEqual(r["by_class"]["absent"], [("EGLC", D2.isoformat())])
        self.assertIn("data (for the owner): EGLC 2025-06-02", out)

    def test_classify_texts(self):
        """The failure texts session 86 writes (its pull_station_day and http_get), and an unknown one."""
        self.assertEqual(bc.classify("idx: RuntimeError(\"failed: RuntimeError('HTTP 404')\")"), "absent")
        self.assertEqual(bc.classify("fetch: RuntimeError(\"failed: ConnectionError('x')\")"), "fetch")
        self.assertEqual(bc.classify("RuntimeError('expected 1 idx line for TMP:2 m above ground:24 hour fcst, "
                                     "found 0')"), "absent")
        self.assertEqual(bc.classify("RuntimeError('expected 1 idx line for TMP:2 m above ground:24 hour fcst, "
                                     "found 2')"), "data")
        self.assertEqual(bc.classify("RuntimeError('idx run stamp d=2025060112 does not match the run')"), "data")
        self.assertEqual(bc.classify("decode: ValueError('identity')"), "data")
        self.assertEqual(bc.classify("something new"), "fetch")              # never passes on a doubt

    def test_observation_drops_are_counted_and_pass(self):
        """With no GRIB failure at all a drop can only be an observation one; written by hand in session 86's
        form (a real message cannot be made offline here)."""
        drops, man = self.tmp / "d.csv", self.tmp / "m.csv"
        with open(drops, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(bc.DROP_COLS)
            w.writerow(["EGLC", "2025-06-02", "no routine report within 15 min", ""])
        with open(man, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(bc.MAN_COLS)
            w.writerow(["EGLC", "2025-06-02", "tmp2m"] + [""] * 13 + ["OK", ""])
        r = bc.check(drops, man)
        self.assertEqual((r["verdict"], r["by_reason"]), ("PASS", {"no routine report within 15 min": 1}))

    def test_one_fetch_field_makes_the_day_a_fetch_drop(self):
        """A day with absent fields and one fetch failure is a fetch drop (a manifest edited by hand from
        session 86's own output)."""
        dirs = build_files(self.tmp / "out", {D1: "noline"})
        rows = list(csv.DictReader(open(dirs["manifest"])))
        rows[0]["detail"] = "fetch: RuntimeError(\"failed: ConnectionError('reset')\")"
        with open(dirs["manifest"], "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=bc.MAN_COLS)
            w.writeheader()
            w.writerows(rows)
        r = bc.check(dirs["drops"], dirs["manifest"])
        self.assertEqual((r["verdict"], r["by_class"]["fetch"]), ("FAIL", [("EGLC", D1.isoformat())]))
        self.assertEqual(r["fail_rows_by_class"]["absent"], len(rows) - 1)

    def test_files_that_do_not_agree_fail(self):
        dirs = build_files(self.tmp / "out", {D1: "idx404"})
        rows = list(csv.reader(open(dirs["drops"])))
        with open(dirs["drops"], "w", newline="") as f:
            csv.writer(f).writerows(rows[:1])                    # the drop removed, the FAIL rows kept
        r = bc.check(dirs["drops"], dirs["manifest"])
        self.assertEqual(r["verdict"], "FAIL")
        self.assertEqual(r["unmatched_fails"], [("EGLC", D1.isoformat())])

    def test_missing_or_foreign_files_exit_2(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(bc.main(["--drops", str(self.tmp / "none.csv"), "--manifest", str(self.tmp / "m")]), 2)
        bad = self.tmp / "bad.csv"
        bad.write_text("a,b\n")
        with contextlib.redirect_stdout(out):
            self.assertEqual(bc.main(["--drops", str(bad), "--manifest", str(bad)]), 2)

    def test_paths_and_columns_equal_session_86s(self):
        self.assertEqual(bc.DEFAULT_DROPS, s86.OUT_DROPS)
        self.assertEqual(bc.DEFAULT_MANIFEST, s86.OUT_MANIFEST)
        self.assertEqual(bc.MAN_COLS, s86.MAN_COLS)
        src = (SCRIPTS / "session86_forward_build.py").read_text()
        self.assertIn(f'csv_text({bc.DROP_COLS!r}, built["drops"])'.replace("'", '"'), src)
        self.assertIn(f'drop("{bc.GRIB_DROP}", ";".join(sorted(fails)))', src)

    def test_writes_nothing(self):
        src = (SCRIPTS / "session131_stageb_build_check.py").read_text()
        self.assertNotIn("open(path, \"w", src)
        self.assertNotIn("write_text", src)


# ------------------------------------------------------------------ the scoring wrapper (D125.5(d))

class ScoreConstants(unittest.TestCase):
    """Each constant equals the record (both DECISIONS files read together), session 129's wrapper and the
    committed files."""

    @classmethod
    def setUpClass(cls):
        cls.text = both_decisions()

    def test_manifest(self):
        found = re.findall(r"manifest\.json`, SHA-256\s+`([0-9a-f]{64})`", self.text)
        self.assertEqual(found, [sw.MANIFEST_SHA256])
        self.assertEqual(sw.MANIFEST_SHA256, w129.MANIFEST_SHA256)
        self.assertEqual(sha256_of(sw.s87.MODEL_DIR / "manifest.json"), sw.MANIFEST_SHA256)

    def test_model_table(self):
        block = self.text[self.text.index("**F122.5"):self.text.index("**F122.6")]
        rows = re.findall(r"^\| (EGLC|LFPG|DSM|YSDU|RNO|KSFO \(SFO\)) \| (\d+) \| `([0-9a-f]{64})` \| "
                          r"`([0-9a-f]{64})` \| (-?[0-9.]+) \|", block, re.M)
        self.assertEqual({r[0]: (int(r[1]), r[2], r[3], r[4]) for r in rows}, sw.F122_5_TABLE)
        self.assertEqual(len(rows), 6)
        self.assertEqual({k: v[:3] for k, v in sw.F122_5_TABLE.items()}, w129.F122_5_MODELS)
        manifest = json.loads((sw.s87.MODEL_DIR / "manifest.json").read_text())["airports"]
        for label, (_, bdlrt, b, mb) in sw.F122_5_TABLE.items():
            st = w129.station_of(label)
            self.assertEqual(sha256_of(sw.s87.MODEL_DIR / f"{st}_bdlrt.txt"), bdlrt)
            self.assertEqual(sha256_of(sw.s87.MODEL_DIR / f"{st}_b.txt"), b)
            self.assertEqual(float(manifest[st]["mean_bias_c"]), float(mb))

    def test_session_87_is_the_frozen_file(self):
        self.assertEqual(sha256_of(SCRIPTS / "session87_forward_score.py"), sw.S87_SCRIPT_SHA256)
        self.assertIn(sw.S87_SCRIPT_SHA256, (ROOT / "tests" / "test_frozen_scripts.py").read_text())


class ScoreSwap(unittest.TestCase):
    """Session 87's own lookups, run against the stand-in, give the record's values; no DECISIONS file is
    read once the swap is in place."""

    def setUp(self):
        self.real = sw.s87.read_decisions_text
        self.addCleanup(setattr, sw.s87, "read_decisions_text", self.real)
        files = sw.s87.DECISIONS_FILES
        self.addCleanup(setattr, sw.s87, "DECISIONS_FILES", files)

    def test_session_87_reads_both_decisions_files(self):
        self.assertEqual(sw.s87.DECISIONS_FILES, [ROOT / "DECISIONS.md", ROOT / "DECISIONS-archive.md"])

    def test_check_passes_with_no_decisions_file(self):
        sw.s87.DECISIONS_FILES = [Path("/nonexistent/DECISIONS.md")]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(sw.main(["--check"]), 0)
        self.assertIn("CHECK: PASS", out.getvalue())
        self.assertIs(sw.s87.read_decisions_text, sw.record_text)

    def test_stand_in_gives_what_the_real_record_gives(self):
        models_r, mb_r, h_r = sw.s87.load_frozen_models()          # the real lookups, both files
        sw.swap()
        models_s, mb_s, h_s = sw.s87.load_frozen_models()
        self.assertEqual((mb_r, h_r), (mb_s, h_s))
        self.assertEqual(sorted(models_r), sorted(models_s))

    def test_a_wrong_constant_stops(self):
        sw.s87.read_decisions_text = lambda: sw.record_text().replace(sw.MANIFEST_SHA256, "0" * 64)
        with self.assertRaises(sw.s87.GuardError):
            sw.s87.load_frozen_models()

    def test_guard_check_passes_through(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(sw.main(["--guard-check"]), 0)
        self.assertIn("all cases behaved", out.getvalue())

    def test_score_refuses_without_its_arguments(self):
        """--score reaches session 87's own guards (nothing is read or written)."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out), self.assertRaises(SystemExit) as cm:
            sw.main(["--score", "--period", "A"])
        self.assertIn("REFUSED", str(cm.exception))


if __name__ == "__main__":
    unittest.main()
