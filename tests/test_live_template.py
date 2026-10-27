"""MLwx-live's workflow template (DECISIONS D117.5; session 123, Steps 4 and 5).
Offline; reads deploy/mlwx-live/.github/workflows/live.yml as text (no YAML
parser is installed) and runs its skip step in temporary git repos.

The action majors are held as constants (D98.2), each the first major whose
action.yml runs on Node.js 24, confirmed from its tag in session 123.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

WORKFLOW = Path(__file__).resolve().parent.parent / "deploy/mlwx-live/.github/workflows/live.yml"

CRON = "15,40 * * * *"                  # D112.6(d)
PYTHON_VERSION = "3.12.15"              # D117.5(b); every run so far (F161.10(5), F163.8, session 123)
ACTION_MAJORS = {                       # D117.5(a); notes/session-123-output.txt, Step 4(a)
    "actions/checkout": "v5",
    "actions/setup-python": "v6",
    "actions/cache": "v5",
    "actions/configure-pages": "v6",
    "actions/upload-pages-artifact": "v5",   # pins upload-artifact v7.0.0 (node24); v4 pins v4.6.2 (node20)
    "actions/deploy-pages": "v5",
}
SKIP_IF = "if: steps.changes.outputs.commit == 'true'"
GATED_STEPS = ["Commit the log and the tracker state", "Prepare the page", "Upload the page", "Publish the page"]
STATE = "state/tracker_gfs.json"
STATE0 = {"version": 1, "model": "gfs", "last_cycle": "2026-10-27T06:00Z",
          "last_run": {"at": "2026-10-27T10:34:00Z", "status": "ok"}, "stops": [], "cells": {}}


def text():
    return WORKFLOW.read_text()


def steps(t):
    """{step name: its lines} for each '- name:' block under steps."""
    out, name = {}, None
    for ln in t.splitlines():
        m = re.match(r"^      - name: (.+)$", ln)
        if m:
            name = m.group(1)
            out[name] = []
        elif name is not None:
            out[name].append(ln)
    return out


def skip_script(t):
    """The Python of the step 'Decide whether anything besides last_run.at changed'."""
    body = "\n".join(steps(t)["Decide whether anything besides last_run.at changed"])
    m = re.search(r"python - <<'PY'\n(.*?)\n\s*PY\n", body, re.S)
    return textwrap.dedent(m.group(1))


def git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class TestTemplateText(unittest.TestCase):
    def test_cron(self):
        self.assertEqual(re.findall(r'cron: "([^"]+)"', text()), [CRON])

    def test_python_version(self):
        self.assertEqual(re.findall(r'python-version: "([^"]+)"', text()), [PYTHON_VERSION])

    def test_action_majors(self):
        uses = re.findall(r"uses: (actions/[\w-]+)@(\S+)", text())
        self.assertEqual({a for a, _ in uses}, set(ACTION_MAJORS))
        for action, major in uses:
            self.assertEqual(major, ACTION_MAJORS[action], action)

    def test_set_at_deploy_lines(self):
        t = text()
        self.assertIn('  MLWX_COMMIT: "SET-AT-DEPLOY"', t)
        self.assertIn('  MODELS_TAG: "SET-AT-DEPLOY"', t)

    def test_skip_condition_present(self):
        s = steps(text())
        self.assertIn("        id: changes", s["Decide whether anything besides last_run.at changed"])
        for name in GATED_STEPS:
            self.assertIn("        " + SKIP_IF, s[name], name)
        self.assertNotIn("        " + SKIP_IF, s["Fail the job if a cycle issued nothing (exit code 3)"])


class TestSkipStep(unittest.TestCase):
    """The skip step on synthetic state files in a temporary git repo."""

    def decide(self, change):
        with tempfile.TemporaryDirectory() as d:
            (Path(d) / "state").mkdir()
            (Path(d) / STATE).write_text(json.dumps(STATE0))
            git(d, "init", "-q")
            git(d, "add", ".")
            git(d, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "seed")
            state = json.loads(json.dumps(STATE0))
            change(d, state)
            (Path(d) / STATE).write_text(json.dumps(state))
            out = Path(d) / "github_output"
            subprocess.run([sys.executable, "-c", skip_script(text())], cwd=d, check=True, capture_output=True,
                           env={**os.environ, "GITHUB_OUTPUT": str(out)})
            return out.read_text().strip()

    def test_skips_on_last_run_at_only(self):
        def change(d, s):
            s["last_run"]["at"] = "2026-10-27T15:15:00Z"
        self.assertEqual(self.decide(change), "commit=false")

    def test_skips_when_nothing_changed(self):
        self.assertEqual(self.decide(lambda d, s: None), "commit=false")

    def test_commits_on_last_run_status(self):
        def change(d, s):
            s["last_run"] = {"at": "2026-10-27T15:15:00Z", "status": "waiting"}
        self.assertEqual(self.decide(change), "commit=true")

    def test_commits_on_added_stop(self):
        def change(d, s):
            s["last_run"]["at"] = "2026-10-27T15:15:00Z"
            s["stops"].append({"cycle": "2026-10-27T06:00Z", "reason": "test", "at": "2026-10-27T15:15:00Z"})
        self.assertEqual(self.decide(change), "commit=true")

    def test_commits_on_new_log_file(self):
        def change(d, s):
            s["last_run"]["at"] = "2026-10-27T15:15:00Z"
            (Path(d) / "log").mkdir()
            (Path(d) / "log/gfs_2026102706.csv").write_text("a,b\n")
        self.assertEqual(self.decide(change), "commit=true")


if __name__ == "__main__":
    unittest.main()
