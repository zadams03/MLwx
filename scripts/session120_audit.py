"""Session 120: the project health check, audit part 1 (the code), D114.

Read-only audit helpers. No mode edits a tracked file other than this
session's own outputs in data/processed/session120_audit/ and
notes/session-120-register.csv.

Modes:
  --layout     tracked top-level items against D91.3 and the entries that
               added later items (Step 2)
  --paths      files holding the old repo path or any /Users/ path (Step 3)
  --inventory  one row per script, workflow and package file (Step 4),
               and the frozen scripts' SHA-256 against the recorded values
  --live DIR   MLwx-live checks on a fresh clone in DIR, with gh JSON files
               saved in DIR/_gh (Step 8)
  --t5         T5's two extra decode fetches (Step 9, network)
  --register   merge every step's rows into notes/session-120-register.csv

Prints short summaries; full tables go to data/processed/session120_audit/.
"""

import argparse
import ast
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "session120_audit"
REGISTER = ROOT / "notes" / "session-120-register.csv"

REG_COLS = ["id", "area", "file", "checked", "result", "severity",
            "proposed_fix", "touches_record", "touches_frozen",
            "touches_live_test", "needs_owner_ruling"]

# Frozen scripts (D62.3(a), D70.6, D80.1, D91.2; scripts/README.md) and the
# recorded SHA-256 of each, with where it is recorded. None means no value
# is recorded in DECISIONS, a meta file or an output file.
FROZEN = {
    "session39_sealed_test.py": (
        "375e4eb69bb06c006a97a4474abce0a6027670123093dc0df3cb5bc0c9da5fca",
        "notes/session-83-output.txt l.160 (no DECISIONS entry holds it)"),
    "session48_reserved_year.py": (None, "none found"),
    "session60_combine_design.py": (None, "none found"),
    "session62_reserved_confirm.py": (
        "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4",
        "F109, D70, F119 (DECISIONS-archive.md l.13499, 15881, 15985)"),
    "session77_ksfo_looks.py": (
        "e4ec113b0dcbc936550b382ffbcdd55d3049878c8b13d74cd83e867a6b3247c1",
        "D70, F119 (DECISIONS-archive.md l.15907, 15976)"),
    "session86_forward_build.py": (
        "da2ff50c8baa9a7bcbe1c5a6d4787d02e042de250143d3b067d10fcd27594125",
        "notes/session-86-output.txt l.149; session96/104/106 meta files"),
    "session87_forward_competitors.py": (
        "8f176562954b5b43bdf110bc292f5b04d6d728d2295df9a178d5a5ff5b23d55c",
        "F129.7 (DECISIONS-archive.md l.19166)"),
    "session87_forward_score.py": (
        "5a6f32c505a5c0a39577a05f2ac82bfac31994f600fe6edbba3f1e936171de6a",
        "F129.7 (DECISIONS-archive.md l.19168)"),
}

CHECK_WORDS = ("verify", "check", "gate", "guard")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True, check=True).stdout


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)


# ---------------------------------------------------------------- layout

# Top-level items present when D91.3 was recorded (session 98b's commit
# 5adf971), and the entry that added each later item.
D91_ITEMS = {".github", ".gitignore", "CLAUDE.md", "DECISIONS-archive.md",
             "DECISIONS.md", "LICENSE", "README.md", "RESULTS.md", "SPEC.md",
             "STATUS.md", "data", "docs", "figures", "notes",
             "requirements.txt", "scripts"}
ADDED = {
    "src": ("D90.12 (a src/ package only at stage G), D103.3 (src/mlwx/)",
            "0f89f01 session 109"),
    "tests": ("D90.12, D95.8 (the tests folder)", "fcbe761 session 101"),
    "deploy": ("D103.11 (the live repo's files, written but not deployed), "
               "F152.10, D104.5", "0f89f01 session 109"),
    "ANALYSIS.md": ("D106.14 (ANALYSIS.md at the repo root)",
                    "36b54a4 session 112"),
    "docs/sessions": ("D92.2 (the layout of docs/)", "0880e4c session 98c"),
    "docs/commits": ("D92.2 (the layout of docs/)", "0880e4c session 98c"),
    "figures/analysis": ("D106.14, F155.9", "36b54a4 session 112"),
    "figures/stagec_*.svg": ("D102.6, F151.4", "73d5fa7 session 108"),
}


def run_layout():
    files = git("ls-files").split("\n")
    files = [f for f in files if f]
    top = Counter(f.split("/")[0] for f in files)
    rows = []
    for item, n in sorted(top.items()):
        if item in D91_ITEMS:
            res, entry = "in D91.3 (present at 5adf971)", "D91.3"
        elif item in ADDED:
            res, entry = "added after D91.3 (" + ADDED[item][1] + ")", ADDED[item][0]
        else:
            res, entry = "added after D91.3, no entry found", ""
        rows.append({"item": item, "tracked_files": n, "result": res,
                     "entry": entry})
    for sub in ("docs/sessions", "docs/commits", "figures/analysis"):
        n = sum(1 for f in files if f.startswith(sub + "/"))
        rows.append({"item": sub, "tracked_files": n,
                     "result": "added after D91.3 (" + ADDED[sub][1] + ")",
                     "entry": ADDED[sub][0]})
    write_csv(OUT / "layout.csv", ["item", "tracked_files", "result",
                                   "entry"], rows)
    print(f"layout: {len(files)} tracked files, {len(top)} top-level items; "
          f"untraced: {sum(1 for r in rows if 'no entry' in r['result'])}")


# ----------------------------------------------------------------- paths

RECORD_PREFIXES = ("DECISIONS.md", "DECISIONS-archive.md", "docs/sessions/",
                   "docs/commits/", "notes/")
CODE_PREFIXES = ("scripts/", "src/", "deploy/", "tests/", ".github/")


def run_paths():
    old = set(git("grep", "-l", "-P", r"Coding Projects/MLwx(?!-all)")
              .split())
    users = git("grep", "-c", "/Users/").split("\n")
    rows = []
    for line in users:
        if not line:
            continue
        f, n = line.rsplit(":", 1)
        if f.startswith(RECORD_PREFIXES):
            cls = "record (never edited, D90.4)"
        elif f.startswith(CODE_PREFIXES):
            cls = "frozen script" if Path(f).name in FROZEN else "live code"
        else:
            cls = "live config or doc"
        runtime = "run time" if f.startswith(CODE_PREFIXES) else "text only"
        rows.append({"file": f, "class": cls, "use": runtime,
                     "old_repo_path": f in old, "users_lines": int(n)})
    write_csv(OUT / "old_paths.csv", ["file", "class", "use",
                                      "old_repo_path", "users_lines"], rows)
    c = Counter(r["class"] for r in rows)
    print(f"paths: old repo path in {len(old)} files (expect 48); /Users/ in "
          f"{len(rows)} files; by class {dict(c)}; run time "
          f"{sum(r['use'] == 'run time' for r in rows)}")


# ------------------------------------------------------------- inventory

NET_RE = re.compile(r"^\s*(import|from)\s+(requests|urllib|http\.client|"
                    r"boto3|botocore|ecmwf|cdsapi|socket)\b", re.M)
NET_CALL_RE = re.compile(r"\"(curl|gh|wget)\"|'(curl|gh|wget)'|https?://")
CACHE_RE = re.compile(r"raw[\"' /,]+grib\b|\"grib\"\)|data/raw/grib|"
                      r"GRIB_CACHE|grib_cache|MY PASSPORT")
FWD_RE = re.compile(r"2026-27|2026-08-01|2027-07-31|FORWARD|forward_")
DEC_RE = re.compile(r"DECISIONS(-archive)?\.md|SPEC\.md")


def argparse_flags(src):
    """Option strings of every add_argument call, in order."""
    flags = []
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return None
    names = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                names[node.targets[0].id] = ast.literal_eval(node.value)
            except Exception:
                pass
    looped = set()
    for node in ast.walk(tree):
        # for m in (...): g.add_argument(f"--{m}", ...)
        if isinstance(node, ast.For):
            calls = [c for c in ast.walk(node) if isinstance(c, ast.Call)
                     and isinstance(c.func, ast.Attribute)
                     and c.func.attr == "add_argument" and c.args
                     and isinstance(c.args[0], (ast.JoinedStr, ast.BinOp))]
            if not calls:
                continue
            try:
                it = ast.literal_eval(node.iter)
            except Exception:
                it = names.get(getattr(node.iter, "id", None), [])
            for m in it if isinstance(it, (list, tuple)) else []:
                if isinstance(m, str):
                    flags.append("--" + m)
            looped.update(id(c) for c in calls)
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_parser" and node.args
                and isinstance(node.args[0], ast.Constant)):
            flags.append("sub:" + node.args[0].value)
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "add_argument" and id(node) not in looped):
            for a in node.args:
                if isinstance(a, ast.Constant) and isinstance(a.value, str):
                    flags.append(a.value)
                    break
    return flags


def sys_argv_flags(src):
    return sorted(set(re.findall(r"[\"'](--[a-z][a-z0-9-]*)[\"']", src)))


def run_inventory():
    files = [f for f in git("ls-files", "scripts", "src", "deploy",
                            ".github").split("\n")
             if f.endswith((".py", ".yml", ".yaml", ".sh"))]
    rows = []
    for f in files:
        src = (ROOT / f).read_text(errors="replace")
        name = Path(f).name
        flags = argparse_flags(src) if f.endswith(".py") else []
        how = "argparse"
        if f.endswith(".py") and not flags:
            flags = sys_argv_flags(src)
            how = "sys.argv" if flags else "none"
        if not f.endswith(".py"):
            how = "workflow"
        checks = [x for x in (flags or []) if any(w in x for w in CHECK_WORDS)]
        rows.append({
            "file": f,
            "frozen": "yes" if name in FROZEN else "no",
            "mode_parser": how,
            "modes": " ".join(flags or []),
            "check_modes": " ".join(checks),
            "reads_decisions_or_spec": "yes" if DEC_RE.search(src) else "no",
            "network": "yes" if (NET_RE.search(src) or NET_CALL_RE.search(src))
                       else "no",
            "cache": "yes" if CACHE_RE.search(src) else "no",
            "forward_2026_27": "yes" if FWD_RE.search(src) else "no",
            "sha256": sha256(ROOT / f),
        })
    notes = defaultdict(list)
    for f, label, _args, why in MODES:
        notes[f].append(f"{label}: " + (why or "run in Step 5"))
    for r in rows:
        r["check_mode_runs"] = "; ".join(notes.get(r["file"], []))
    cols = list(rows[0].keys())
    write_csv(OUT / "scripts.csv", cols, rows)
    srows = []
    for name, (rec, where) in FROZEN.items():
        now = sha256(ROOT / "scripts" / name)
        commits = git("log", "--format=%h", "--", "scripts/" + name).split()
        srows.append({"script": name, "sha256_now": now, "recorded": rec or "",
                      "where": where, "git_commits": " ".join(commits),
                      "result": ("equal" if rec == now else
                                 "no recorded value" if rec is None else
                                 "MISMATCH")})
    write_csv(OUT / "frozen_sha.csv", list(srows[0].keys()), srows)
    c = Counter(r["result"] for r in srows)
    print(f"inventory: {len(rows)} files; with check modes "
          f"{sum(bool(r['check_modes']) for r in rows)}; frozen "
          f"{len(srows)}: {dict(c)}")


# ---------------------------------------------------------------- checks

# Every verify, check, gate or guard mode (and whole-script check), with its
# arguments when it is run in Step 5, or the reason it is not run (D114.4 to
# D114.6). Arguments are run from the root of a temporary clone of HEAD, so
# any write lands in the clone; the sibling folders are linked beside it.
NOT_CACHE = "not run: needs cache (D114.6)"
NOT_NET = "not run: needs the network outside Steps 8 and 9 (D114.5)"
NOT_FWD = "not run: reads a file valid on or after 2026-08-01 (D114.4)"
NOT_STAGEB = "not run: stage B's frozen scripts run in offline guard modes only (Step 5)"
NOT_FROZEN = "not run: frozen script with no guard or gate mode (D114.4)"
NOT_LOOK = "not run: a look, not a check"
S = "scripts/"
MODES = [
    (S + "session86_forward_build.py", "--guard-check", ["--guard-check"], ""),
    (S + "session86_forward_build.py", "--gate", None, NOT_NET + "; " + NOT_STAGEB),
    (S + "session86_forward_build.py", "--build", None, NOT_FWD),
    (S + "session87_forward_competitors.py", "--guard-check", ["--guard-check"], ""),
    (S + "session87_forward_competitors.py", "--gate", None, NOT_NET + "; " + NOT_STAGEB),
    (S + "session87_forward_competitors.py", "--fetch", None, NOT_FWD),
    (S + "session87_forward_score.py", "--guard-check", ["--guard-check"], ""),
    (S + "session87_forward_score.py", "--gate", None, NOT_STAGEB),
    (S + "session87_forward_score.py", "--score", None, NOT_FWD),
    (S + "session39_sealed_test.py", "(whole script)", None, NOT_FROZEN),
    (S + "session48_reserved_year.py", "(module, imported by tests)", None,
     NOT_FROZEN + "; its guard is exercised by tests/test_guards.py (Step 6)"),
    (S + "session60_combine_design.py", "(whole script)", None, NOT_FROZEN),
    (S + "session62_reserved_confirm.py", "--confirm", None, NOT_LOOK + "; " + NOT_FROZEN),
    (S + "session77_ksfo_looks.py", "--dry-run, --run-looks", None, NOT_LOOK + "; " + NOT_FROZEN),
    (S + "archive_decisions.py", "--citations", ["--citations"], ""),
    (S + "archive_decisions.py", "--plan", ["--plan"], ""),
    (S + "session81_freeze_forward_models.py", "--gate", ["--gate"], ""),
    (S + "session85_nbm_mos_comparison.py", "--gate", ["--gate"], ""),
    (S + "session91_grib_pull.py", "--guard-check", ["--guard-check"], ""),
    (S + "session91_grib_pull.py", "--gate (chunk 2023-01)", ["--gate", "--extract", "{ONE}"], ""),
    (S + "session91_grib_pull.py", "--spot-check", None, NOT_NET),
    (S + "session92_verify_chunk.py", "verify, every month, MLwx-pull (0-24)", "LOOP00", ""),
    (S + "session92_verify_chunk.py", "verify, every month, MLwx-pull-f025-048 (25-48)", "LOOP25", ""),
    (S + "session92_verify_chunk.py", "--gate (2023-01)", ["--dir", "../MLwx-pull", "--month", "2023-01", "--hours", "0-24", "--gate"], ""),
    (S + "session95_check_release.py", "--gate", ["--gate"], ""),
    (S + "session96_stagec_table.py", "--gate", ["--gate"], ""),
    (S + "session96_stagec_table.py", "--guard-check", ["--guard-check"], ""),
    (S + "session97_stagec_cv.py", "--guard-check", ["--guard-check"], ""),
    (S + "session97_stagec_cv.py", "--gate", ["--gate"], ""),
    (S + "session100_structure_cv.py", "--gate", ["--gate"], ""),
    (S + "session103_bias_drift_cv.py", "--check", ["--check"], ""),
    (S + "session103_bias_drift_cv.py", "--gate", ["--gate"], ""),
    (S + "session104_curve_cv.py", "--gate", ["--gate"], ""),
    (S + "session104_stagec_table_f025_048.py", "--gate", ["--gate"], ""),
    (S + "session104_pull_check.py", "(whole script)", None, NOT_NET),
    (S + "session105_dailymax_cv.py", "--gate", ["--gate"], ""),
    (S + "session106_claim_look.py", "--guard-check", ["--guard-check"], ""),
    (S + "session106_claim_look.py", "--gate", ["--gate"], ""),
    (S + "session109_gates.py", "--gate-a", ["--gate-a"], ""),
    (S + "session109_gates.py", "--gate-b", ["--gate-b"], ""),
    (S + "session109_gates.py", "--gate-c", None, NOT_NET),
    (S + "session109_gates.py", "--gate-d", None, NOT_NET),
    (S + "session112_analysis.py", "--check", ["--check"], ""),
    (S + "session113_comparison_pull.py", "--check", ["--check"], ""),
    (S + "session114_comparisons.py", "--check", ["--check"], ""),
    (S + "session114_comparisons.py", "--gate", ["--gate"], ""),
    (S + "session114_comparisons.py", "--verify", ["--verify"], ""),
    (S + "session115_obs_check.py", "--check", ["--check"], ""),
    (S + "session115_obs_check.py", "--gate", ["--gate"], ""),
    (S + "session116_obs_check51.py", "--check", ["--check"], ""),
    (S + "session116_obs_check51.py", "--gate", ["--gate"], ""),
    (S + "session117_ifs_guide.py", "--verify", ["--verify"], ""),
    (S + "session119_ifs_check.py", "--gate", ["--gate"], ""),
    (S + "session119_ifs_check.py", "--decode", None, NOT_NET + " (Step 9 imports its functions instead)"),
    ("src/mlwx/refit.py", "--check-only", ["-m", "mlwx.refit", "--tables", "../MLwx-stagec",
                                          "--new-tables", "../MLwx-live-build/tables", "--check-only"], ""),
    (S + "session01_checks.py", "(whole script)", [], ""),
    (S + "session03_checks.py", "(whole script)", [], ""),
    (S + "session08_checks.py", "(whole script)", [], ""),
    (S + "session10_checks.py", "(whole script)", [], ""),
    (S + "session14_checks.py", "(whole script)", [], ""),
    (S + "session15_checks.py", "(whole script)", None,
     NOT_FWD + " (the DSM 2026-08-05 to 15 files, D73.10)"),
    (S + "session19_checks.py", "(whole script)", [], ""),
    (S + "session20_checks.py", "(whole script)", [], ""),
    (S + "session25_checks.py", "(whole script)", [], ""),
    (S + "session26_checks.py", "(whole script)", [], ""),
    (S + "session31_checks.py", "(whole script)", [], ""),
    (S + "session41_verify.py", "(whole script)", None,
     "not run: runs frozen session39_sealed_test.py's functions outside a guard or gate mode (D114.4)"),
    (S + "session42_scoring_check.py", "(whole script)", None,
     "not run: runs frozen session39_sealed_test.py's functions outside a guard or gate mode (D114.4)"),
    (S + "session63_join_equivalence_check.py", "(whole script)", [], ""),
    (S + "session63_wiring_scratch_check.py", "(whole script)", [], ""),
    (S + "session71_original_functions_check.py", "(whole script)", None, NOT_CACHE),
    (S + "session76_verify.py", "(whole script)", None, NOT_NET),
    (S + "session76b_check_a.py", "(whole script)", None, NOT_CACHE),
    (S + "session76b_check_b.py", "(whole script)", None, NOT_CACHE),
    (S + "session83_icon_route_check.py", "(whole script)", None, NOT_NET),
    (S + "session90_airport_check.py", "--collect, --decide", None, NOT_NET),
    (S + "session94_fallback_gate.py", "(whole script)", None, NOT_NET),
]

TIMEOUT = 1800


def first_fail(text):
    for line in text.splitlines():
        if re.search(r"FAIL|STOP|Traceback|Error|MISMATCH|mismatch", line) \
                and not re.search(r"\b0 (FAIL|mismatch)", line):
            return line.strip()[:200]
    return ""


def run_one(clone, args, env):
    import time
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, *args], cwd=clone, env=env,
                           capture_output=True, text=True, timeout=TIMEOUT)
        code, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        code = "timeout"
        out = (e.stdout or b"").decode(errors="replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
    return code, round(time.time() - t0, 1), out


def run_checks(clone):
    import os
    clone = Path(clone).resolve()
    env = dict(os.environ, PYTHONPATH=str(clone / "src"), MPLBACKEND="Agg")
    logdir = clone.parent / "logs"
    logdir.mkdir(exist_ok=True)
    rows = []
    # Resume: modes already run (a line in run_checks.out) keep that result;
    # the first failing line is read back from the mode's log.
    done = {}
    prev = clone.parent / "run_checks.out"
    if prev.exists():
        for ln in prev.read_text().splitlines():
            m = re.match(r"^(\S+) (.+): (PASS|FAIL|not run: over 30 min) \(exit (\S+), ([\d.]+) s\)$", ln)
            if m:
                done[(m.group(1), m.group(2))] = m.groups()[2:]
            m = re.match(r"^(verify, every month, .+): (PASS|FAIL \(\d+ of \d+\)) ([\d.]+) s$", ln)
            if m:
                done[(S + "session92_verify_chunk.py", m.group(1))] = (m.group(2), "0", m.group(3))
    for f, label, args, why in MODES:
        if (f, label) in done:
            res, code, t = done[(f, label)]
            name = re.sub(r"[^A-Za-z0-9]+", "_", f"{Path(f).stem}_{label}")[:80]
            log = logdir / f"{name}.log"
            out = log.read_text() if log.exists() else ""
            if isinstance(args, str):
                cmd = f"{f} --dir ../MLwx-pull{'' if args == 'LOOP00' else '-f025-048'} --month M --hours {'0-24' if args == 'LOOP00' else '25-48'} (each month)"
            else:
                a2 = [x.replace("{ONE}", str(clone.parent / "one_chunk")) for x in args]
                cmd = " ".join(a2 if a2 and a2[0] == "-m" else [f, *a2])
            rows.append({"file": f, "mode": label, "command": cmd, "exit": code,
                         "seconds": t, "result": res,
                         "first_failing_line": first_fail(out) if res != "PASS" else ""})
            continue
        if args is None:
            rows.append({"file": f, "mode": label, "command": "", "exit": "",
                         "seconds": "", "result": why, "first_failing_line": ""})
            continue
        if isinstance(args, str):            # session 92's verifier per month
            pull, hours = (("../MLwx-pull", "0-24") if args == "LOOP00"
                           else ("../MLwx-pull-f025-048", "25-48"))
            months = sorted(p.name[len("chunk_"):-len(".meta.txt")]
                            for p in (clone / pull).glob("chunk_*.meta.txt"))
            bad, secs, first, codes = [], 0.0, "", Counter()
            for m in months:
                code, t, out = run_one(clone, [f, "--dir", pull, "--month", m,
                                               "--hours", hours], env)
                secs += t
                codes[code] += 1
                if code != 0:
                    bad.append(m)
                    first = first or f"{m}: {first_fail(out)}"
            rows.append({"file": f, "mode": label,
                         "command": f"{f} --dir {pull} --month M --hours {hours} (x{len(months)})",
                         "exit": " ".join(f"{k}:{v}" for k, v in codes.items()),
                         "seconds": round(secs, 1),
                         "result": "PASS" if not bad else f"FAIL ({len(bad)} of {len(months)})",
                         "first_failing_line": first})
            print(f"{label}: {rows[-1]['result']} {rows[-1]['seconds']} s", flush=True)
            continue
        args = [a.replace("{ONE}", str(clone.parent / "one_chunk")) for a in args]
        cmd = args if args and args[0] == "-m" else [f, *args]
        code, t, out = run_one(clone, cmd, env)
        name = re.sub(r"[^A-Za-z0-9]+", "_", f"{Path(f).stem}_{label}")[:80]
        (logdir / f"{name}.log").write_text(out)
        res = ("not run: over 30 min" if code == "timeout" else
               "PASS" if code == 0 else "FAIL")
        rows.append({"file": f, "mode": label, "command": " ".join(cmd),
                     "exit": code, "seconds": t, "result": res,
                     "first_failing_line": first_fail(out) if res != "PASS" else ""})
        print(f"{f} {label}: {res} (exit {code}, {t} s)", flush=True)
    st = subprocess.run(["git", "status", "--porcelain"], cwd=clone,
                        capture_output=True, text=True).stdout
    (OUT / "checks_clone_status.txt").write_text(st or "(clean)\n")
    write_csv(OUT / "checks.csv", list(rows[0].keys()), rows)
    c = Counter(r["result"].split(" (")[0] if r["result"].startswith(("PASS", "FAIL")) else "not run"
                for r in rows)
    print(f"checks: {len(rows)} modes; {dict(c)}; clone writes: "
          f"{len(st.splitlines())} paths")


# -------------------------------------------------------------------- T5

def t5_picks(head, man):
    """The two picks of F162.9(6), fixed before any fetch: the main 0.25
    degree grid is the grid label with the most 2t messages; its first and
    last dates with a 00z 2t message; on each, the 00z 2t step nearest 24 h
    that exists (a tie goes to the earlier step)."""
    col = {c: i for i, c in enumerate(head)}
    n = Counter(r[col["grid"]] for r in man if r[col["param"]] == "2t")
    grid = n.most_common(1)[0][0]
    z = [r for r in man if r[col["grid"]] == grid and r[col["param"]] == "2t"
         and r[col["cycle"]].endswith("T00:00Z")]
    dates = sorted({r[col["cycle"]][:10] for r in z})
    picks = []
    for d in (dates[0], dates[-1]):
        cand = [r for r in z if r[col["cycle"]] == f"{d}T00:00Z"]
        steps = sorted({int(r[col["step"]]) for r in cand})
        s = min(steps, key=lambda x: (abs(x - 24), x))
        hit = [r for r in cand if int(r[col["step"]]) == s]
        if len(hit) != 1:
            raise SystemExit(f"STOP: {grid} {d} step {s}: {len(hit)} messages")
        picks.append((hit[0], steps))
    return grid, n, picks


def run_t5(fetch):
    """F162.9(6), judged by D113.6(e)'s mark, with session 119's helpers
    imported read-only (session 119's own --decode is not run: it takes
    only step 24)."""
    import shutil
    import struct
    import tempfile
    sys.path.insert(0, str(ROOT / "scripts"))
    import session119_ifs_check as s119
    s113, s114 = s119.s113, s119.s114
    import eccodes as ec
    head, man = s114.read_s113("ifs_manifest.csv.gz")
    col = {c: i for i, c in enumerate(head)}
    grid, n, picks = t5_picks(head, man)
    print(f"grids (2t messages): {dict(n)}; main grid {grid}")
    for r, steps in picks:
        print(f"pick {r[col['msg']]} {r[col['cycle']]} step {r[col['step']]} (00z 2t steps that day: {steps})")
    if not fetch:
        return
    want = {r[col["msg"]] for r, _ in picks}
    stored = defaultdict(list)
    for ic in s119.AIRPORTS:
        h, rows = s114.read_s113(f"ifs_{ic}.csv.gz")
        c = {k: i for i, k in enumerate(h)}
        for x in rows:
            if x[c["msg"]] in want:
                stored[x[c["msg"]]].append((x[c["airport"]], x[c["position_set"]], x[c["grid"]], x[c["cycle"]],
                                            x[c["step"]], x[c["param"]], [x[c[f"v{k}"]] for k in range(1, 5)],
                                            x[c["units"]]))
    posr = {(p["airport"], p["position_set"]): [int(p[f"p{k}_index"]) for k in range(1, 5)]
            for p in s114.read_s113_dicts(f"positions_{grid}.csv")}
    tmp = Path(tempfile.mkdtemp(prefix="session120_t5_"))
    out, nbad = [], 0
    for r, _ in picks:
        mid, cyc, step, url = r[col["msg"]], r[col["cycle"]], r[col["step"]], r[col["url"]]
        a, b = (int(x) for x in r[col["byte_range"]].split("-"))
        s113.guard_valid(s114.ptime(cyc) + timedelta(hours=int(step)))
        data = s113.get(url, byte_range=(a, b), tries=2).content
        (tmp / f"{mid}.grib2").write_bytes(data)
        sha_ok = hashlib.sha256(data).hexdigest() == r[col["sha256"]]
        gid = ec.codes_new_from_message(data)
        try:
            m = s113.grib_meta(gid)
            vals = ec.codes_get_values(gid)
        finally:
            ec.codes_release(gid)
        cdt = s114.ptime(cyc)
        meta_ok = (m["shortName"] == "2t" and m["units"] == "K"
                   and int(m["dataDate"]) == int(f"{cdt:%Y%m%d}") and int(m["dataTime"]) == 0
                   and int(m["endStep"]) == int(step) and s113.grid_label("ifs", m) == grid)
        nrow = nok = 0
        why = []
        for (ap, ps, rg, rc, rs, rp, vs, un) in stored[mid]:
            nrow += 1
            if (rg, rc, rs, rp, un) != (grid, cyc, step, "2t", "K"):
                why.append(f"{ap} {ps} row keys")
                continue
            dec = [float(vals[k]) for k in posr[(ap, ps)]]
            same = all(struct.pack("<d", x) == struct.pack("<d", float(y)) for x, y in zip(dec, vs))
            nok += same
            if not same:
                why.append(f"{ap} {ps} values")
        ok = sha_ok and meta_ok and nrow > 0 and nok == nrow
        nbad += not ok
        out.append({"msg": mid, "grid": grid, "cycle": cyc, "step": step, "byte_range": r[col["byte_range"]],
                    "bytes": len(data), "sha256": "equal" if sha_ok else "DIFFERS",
                    "decoded": f"{m['shortName']} {m['units']} {m['dataDate']} {int(m['dataTime']):04d} "
                               f"{m['endStep']} {s113.grid_label('ifs', m)}",
                    "meta": "equal" if meta_ok else "DIFFERS", "stored_rows": nrow, "rows_bit_equal": nok,
                    "result": "PASS" if ok else "FAIL: " + "; ".join(why or ["sha or meta"])})
        print(f"{mid} {cyc} step {step}: sha {out[-1]['sha256']}, meta {out[-1]['meta']}, rows {nok}/{nrow} "
              f"bit-equal: {out[-1]['result']}")
    files = sorted(p.name for p in tmp.iterdir())
    shutil.rmtree(tmp)
    write_csv(OUT / "t5_extra.csv", list(out[0].keys()), out)
    print(f"deleted {len(files)} files under {tmp}; exists after: {tmp.exists()}")
    print(f"T5 extra: messages {len(out)}, failing {nbad}; mark {'SHOWN' if nbad else 'NOT SHOWN'}")


# ------------------------------------------------------------------ live

REDEPLOY_RUN = 39488813037           # D113.2
REDEPLOY_COMMIT = "0d77fb0"
SINCE_CYCLE = "2026-10-19T12"        # Step 8: cycles from here, by F161.3's method


def run_live(tmp):
    """Step 8 on a fresh clone in TMP/live, with gh JSON and run logs in
    TMP/live_work. Reuses session 118's functions read-only; its main() is
    not called (it writes session 118's committed tables)."""
    import statistics
    sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
    import session118_live_audit as a118
    from mlwx import config
    tmp = Path(tmp)
    clone, work = tmp / "live", tmp / "live_work"
    model = config.get_model("gfs")
    head_sha, head_time = a118.git(clone, "log", "-1", "--format=%H %cI").split()
    head_time = a118.parse_time(head_time)
    runs = a118.load_runs(work)
    since = [r for r in runs if r["createdAt"] >= "2026-10-19T12:00:00Z"]
    run_rows = a118.audit_runs(clone, work, since)
    state = json.loads((clone / "state" / "tracker_gfs.json").read_text())
    cyc = [r for r in a118.audit_cycles(clone, model, head_time, run_rows, state)
           if r["cycle"] >= SINCE_CYCLE]
    page = a118.page_check(a118.load_page(work), cyc)

    # Runs after the redeploy.
    red = [r for r in run_rows if r["run_id"] >= REDEPLOY_RUN]
    sched = [r for r in red if r["event"] == "schedule"]
    redeploy_t = a118.parse_time(a118.git(clone, "log", "-1", "--format=%cI",
                                          REDEPLOY_COMMIT).strip())
    cutoff = datetime.fromtimestamp((work / "runs.json").stat().st_mtime,
                                    timezone.utc).replace(tzinfo=None)
    slots, t = [], redeploy_t.replace(minute=0, second=0)
    while t <= cutoff:
        for m in (15, 40):
            s = t.replace(minute=m)
            if redeploy_t <= s <= cutoff:
                slots.append(s)
        t += timedelta(hours=1)
    per_slot, delays = Counter(), []
    for r in sched:
        c = a118.parse_time(r["created_utc"])
        s = max(x for x in [c.replace(minute=15, second=0), c.replace(minute=40, second=0),
                            (c - timedelta(hours=1)).replace(minute=40, second=0)] if x <= c)
        per_slot[f":{s.minute:02d}"] += 1
        delays.append((c - s).total_seconds() / 60)
        r["slot"] = f"{s:%H:%M}"
    times = [a118.parse_time(r["created_utc"]) for r in red]
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]

    # Commits on main since the redeploy: which changed only the state file,
    # and in it only the last_run line (the changed lines are matched by key
    # only; no value is read).
    commits = a118.git(clone, "rev-list", "--reverse", f"{REDEPLOY_COMMIT}..main").split()
    crow = []
    for c in commits:
        files = a118.git(clone, "show", "--format=", "--name-only", c).split()
        diff = a118.git(clone, "show", "--format=", "-U0", c, "--", "state/tracker_gfs.json")
        changed = [l for l in diff.splitlines() if l[:1] in "+-" and l[:3] not in ("+++", "---")]
        keys = sorted({(re.match(r'^[+-]\s*"([^"]+)"', l) or [None, "?"])[1] for l in changed})
        # "at" is last_run's key when the line above the hunk is '"last_run": {'.
        new_lines = a118.git(clone, "show", f"{c}:state/tracker_gfs.json").splitlines()
        for h in re.findall(r"^@@ -\S+ \+(\d+)", diff, re.M):
            if keys == ["at"] and '"last_run"' in new_lines[int(h) - 2]:
                keys = ["last_run.at"]
        crow.append({"commit": c[:7], "files": " ".join(files),
                     "state_only": files == ["state/tracker_gfs.json"],
                     "state_keys_changed": " ".join(keys)})
    state_only = [r for r in crow if r["state_only"] and r["state_keys_changed"] == "last_run.at"]

    lags = {r["cycle"]: r.get("issue_lag_hours", "") for r in cyc}
    write_csv(OUT / "live_runs.csv", sorted({k for r in run_rows for k in r}), run_rows)
    write_csv(OUT / "live_cycles.csv", sorted({k for r in cyc for k in r}), cyc)
    write_csv(OUT / "live_commits.csv", list(crow[0].keys()), crow)
    print(f"clone HEAD {head_sha[:7]} at {head_time:%Y-%m-%dT%H:%M}Z; runs listed {len(runs)}; "
          f"since 2026-10-19T12Z {len(since)}; since the redeploy {len(red)} "
          f"({len(sched)} scheduled); run list fetched {cutoff:%Y-%m-%dT%H:%M}Z")
    print(f"slots :15/:40 from the redeploy ({redeploy_t:%Y-%m-%dT%H:%M}Z) to the cutoff: {len(slots)}; "
          f"scheduled runs by slot {dict(per_slot)}; delay to slot (min) "
          f"{[round(d, 1) for d in delays]}; runs' slots {[r['slot'] for r in sched]}")
    print(f"gaps between runs since the redeploy (h): {[round(g, 2) for g in gaps]}; "
          f"last run to cutoff {(cutoff - times[-1]).total_seconds() / 3600:.2f} h")
    print(f"commits since {REDEPLOY_COMMIT}: {len(crow)}; state file only, last_run only: "
          f"{len(state_only)}; push outcomes {dict(Counter(r.get('push_outcome') for r in red))}")
    print(f"cycles {cyc[0]['cycle']} to {cyc[-1]['cycle']}: {len(cyc)}; logged "
          f"{sum(r['log_present'] for r in cyc)}; added once never changed "
          f"{sum(bool(r.get('log_added_once_never_changed')) for r in cyc)}; leads complete "
          f"{sum(bool(r.get('leads_3_48_complete')) for r in cyc)}; claimed by >1 run "
          f"{sum(len(r['runs_claiming_issue'].split()) > 1 for r in cyc)}; snapshots "
          f"{sum(r['snapshot_present'] for r in cyc)}; stops {[r['cycle'] for r in cyc if r['stop_reason']]}")
    print("issue lag (h) per cycle: " + ", ".join(f"{k[5:]} {v}" for k, v in lags.items()))
    print(f"stale checkouts (by log) {sum(bool(r.get('stale_by_log')) for r in red)}; silent push "
          f"failures {sum(bool(r.get('silent_push_failure')) for r in red)}")
    print(f"page: latest {page['latest_line']}, airport lines {page['airport_lines']}; log latest "
          f"{page['log_latest_cycle']} issued {page['log_latest_issued']}: "
          f"{'MATCH' if page['match'] else 'NO MATCH'}")


# -------------------------------------------------------------- register

# One row per item checked in Steps 2 to 9 (D114.7). Flags: R a record file
# (never edited, D90.4, D90.6), F a frozen script, L the live test
# (D105.5(k)), O needs an owner ruling.
REG = [
    # id, area, file, checked, result, severity, proposed fix, flags
    ("L01", "layout", "(root)", "tracked top-level items against D91.3",
     "16 of 16 D91.3 items present (5adf971); 20 items in all", "OK", "", ""),
    ("L02", "layout", "src/", "traced to its entry", "D90.12, D103.3 (0f89f01, session 109)", "OK", "", ""),
    ("L03", "layout", "tests/", "traced to its entry", "D90.12, D95.8 (fcbe761, session 101)", "OK", "", ""),
    ("L04", "layout", "deploy/", "traced to its entry", "D103.11, F152.10, D104.5 (0f89f01)", "OK", "", ""),
    ("L05", "layout", "ANALYSIS.md", "traced to its entry", "D106.14 (36b54a4, session 112)", "OK", "", ""),
    ("L06", "layout", "docs/sessions/, docs/commits/", "traced to its entry", "D92.2 (0880e4c, session 98c)", "OK", "", ""),
    ("L07", "layout", "figures/analysis/, figures/stagec_*.svg", "traced to its entry",
     "D106.14, F155.9; D102.6, F151.4", "OK", "", ""),
    ("L08", "layout", ".gitignore", "untracked and ignored items covered",
     ".DS_Store (11), .claude/, .pytest_cache/, .venv/, __pycache__/ (3): all covered; data/raw/grib absent (drive, D102.3)",
     "OK", "", ""),
    ("L09", "layout", ".gitignore", "comment text against D102.3",
     "comment says 'the ~20 GB GFS GRIB cache'; D102.3 says about 39 GB", "cosmetic",
     "edit the comment (no rule changes)", ""),
    ("L10", "layout", "(record) D109.8, D112.2", "baseline named for the layout check",
     "D109.8 and D112.2 cite D90.5's layout; D91.3 replaced it (D91.4); the repo matches D91.3 plus the traced items (answered as a reading, D114.2)",
     "OK", "", ""),
    ("P01", "old paths", "48 files (DECISIONS-archive.md 1, docs/sessions/ 6, notes/ 41)",
     "old repo path 'Coding Projects/MLwx' not followed by -all", "48 files (expected 48); all record files; text only",
     "OK", "none: record files are never edited (D90.4)", "R"),
    ("P02", "old paths", "5 more files (docs/commits/commit-84.txt, docs/sessions/session-67, 84, 98.md, notes/session-84-output.txt)",
     "any other /Users/ path", "53 files with /Users/ in all; all record files; text only; 0 frozen; 0 live code",
     "OK", "none (D90.4)", "R"),
    ("P03", "old paths", "src/mlwx/refit.py, baseline.py", "sibling-folder paths in live code",
     "relative only (../MLwx-live-build, ../MLwx-stagec); both exist after the folder move", "OK", "", ""),
    ("S01", "scripts", "data/processed/session120_audit/scripts.csv", "inventory",
     "145 rows: 127 scripts, 16 src/mlwx, 2 workflows; modes, check modes, SPEC or DECISIONS reads, frozen, network, cache, 2026-27",
     "OK", "", ""),
    ("S02", "scripts", "8 frozen scripts", "SHA-256 against recorded values",
     "6 of 8 equal (session62, 77, 86, 87 x2, 39); 0 mismatches", "OK", "", "F"),
    ("S03", "scripts", "scripts/session48_reserved_year.py, scripts/session60_combine_design.py",
     "recorded SHA-256", "no recorded value anywhere; one git commit each (74e7077, 0e29835), so unchanged since added",
     "stale", "record each SHA-256 as a constant with a test (D98.2), in its own entry", "FO"),
    ("S04", "scripts", "scripts/session39_sealed_test.py", "recorded SHA-256",
     "equal, but held only in notes/session-83-output.txt l.160, no DECISIONS entry", "stale",
     "same as S03 (constant and test)", "FO"),
    ("S05", "scripts", "session86, 87 competitors, 87 score (frozen); session89, 91, 113",
     "SPEC text read by path (F151.6)",
     "all read SPEC 3.4's table by the markers '**3.4 The airport table.**' and 'Notes on the table:' (both present); an edit there would break stage B's frozen scripts",
     "OK", "session 121 (record audit) keeps SPEC 3.4's two markers and table format; optional test that the table parses", ""),
    ("S06", "scripts", "scripts/session86_forward_build.py --gate", "DECISIONS text read by path",
     "F122.3 and F122.5 searched in DECISIONS.md only; both archived, so --gate cannot run as it stands (D96.3); --build reads only SPEC",
     "stale", "none (frozen); if stage B needs its gate before period A, the owner rules how", "FO"),
    ("S07", "scripts", "scripts/session87_forward_score.py", "DECISIONS text read by path",
     "reads both DECISIONS files for F122.5; checked by tests/test_record.py", "OK", "", "F"),
    ("C01", "checks", "session86, 87 competitors, 87 score", "--guard-check after the folder move",
     "PASS x3 (0.6, 0.2, 0.1 s)", "OK", "", "F"),
    ("C02", "checks", "scripts/session92_verify_chunk.py", "the workflow's verify form on every month",
     "PASS: 65 of 65 months MLwx-pull (0-24, 216 s); 65 of 65 MLwx-pull-f025-048 (25-48, 203 s)", "OK", "", ""),
    ("C03", "checks", "sessions 81, 85, 97, 100, 103, 104, 104_f025_048, 105, 106, 109 (a, b), 114, 115, 116, 119; refit",
     "offline gate and check modes",
     "PASS: 81, 85, 97, 100, 103 (check, gate), 104, 104_f025_048, 105, 106 (gate, guard), 109 gate-a (1761.6 s) and gate-b, 112-116 --check, 114/115/116/119 --gate, refit --check-only, 91/96/97 --guard-check, archive_decisions --citations and --plan",
     "OK", "", ""),
    ("C04", "checks", "scripts/session01..31_checks.py, session63_wiring_scratch_check.py", "old whole-script checks",
     "11 of 11 PASS (session15_checks not run: reads the DSM 2026-08 files)", "OK", "", ""),
    ("C05", "checks", "scripts/session91_grib_pull.py --gate", "offline gate",
     "needs D83.6's three-date test chunk (only a network pull makes it); a try on month 2023-01 rebuilt 0 of 18 (wrong input, 0 mismatches)",
     "OK", "run only with a fresh test chunk (network), if ever needed", ""),
    ("C06", "checks", "scripts/session92_verify_chunk.py l.285-288, scripts/session95_check_release.py",
     "--gate", "FAIL, known (D98.2): F122.3 searched in DECISIONS.md, archived; AttributeError at l.288",
     "stale", "hold F122.3's SHA-256 as a constant (session 91's TRAINING_SET_SHA256 already is, with a test); D98.2 says these are not edited, so an owner ruling", "O"),
    ("C07", "checks", "scripts/session96_stagec_table.py l.615", "--gate",
     "FAIL, new: same cause, through session86's expected_hash_from_decisions; not named in D98.2 or D96.3",
     "stale", "as C06 (a constant), or record it beside D98.2 as not re-runnable", "O"),
    ("C08", "checks", "scripts/session114_comparisons.py l.1956, 1960, 1978, 2309", "--verify",
     "FAIL, known (F160.9(4)): template says IFS pending; 818 numbers in Part 1 against 783 re-rendered, 757 positional mismatches, text not identical",
     "stale", "with A01: add IFS to PART1_TEMPLATE from session 117's tables, or point --verify at the IFS-free text", "O"),
    ("C09", "checks", "scripts/session117_ifs_guide.py --verify", "re-run after commit",
     "FAIL, new: rebuilds from git HEAD and expects the pre-117 sentence; HEAD holds the edit, so it cannot be re-run",
     "stale", "base the re-render on session 117's parent commit (5df783a^) instead of HEAD", ""),
    ("C10", "checks", "scripts/session63_join_equivalence_check.py", "whole-script check",
     "STOP as recorded (F108: R 0.002 double rounding); the committed output shows the same", "OK", "", ""),
    ("C11", "checks", "scripts/session63_join_equivalence_check.py, session63_wiring_scratch_check.py",
     "what a run writes", "each run rewrites its committed notes/ output (run time and path lines); seen in the clone only",
     "cosmetic", "note in scripts/README.md: run only in a clone; the notes files are not edited", "R"),
    ("C12", "checks", "session71_original_functions_check.py, session76b_check_a.py, session76b_check_b.py",
     "modes needing the cache", "not run: needs cache (D114.6)", "OK", "run when the owner attaches the drive (D114.3)", ""),
    ("C13", "checks", "session86 and 87 competitors --gate; 91 --spot-check; 104_pull_check; 109 gate-c, gate-d; 119 --decode; 76_verify; 83; 90; 94",
     "modes needing the network", "not run (D114.5)", "OK", "", ""),
    ("C14", "checks", "session39, 48, 60, 62 --confirm, 77 looks; session41_verify, 42_scoring_check; 86 --build, 87 --fetch/--score, 15_checks, 87 score --gate",
     "frozen, look or 2026-27 modes", "not run by the limits (D114.4); stage B's guard modes ran (C01)", "OK", "", "F"),
    ("T01", "tests", "tests/", "suite in the venv",
     "181 OK at HEAD (Step 0); after D114 one transient failure (citation of F163 before it was written), re-run after F163 at the end",
     "OK", "", ""),
    ("T02", "tests", ".venv, session prompts", "pytest", "not installed (F161.1); the suite runs with unittest",
     "stale", "owner chooses: install pytest (and pin it) or keep unittest and say so in prompts and tests/README.md", "O"),
    ("T03", "tests", "requirements.txt l.104-110", "requirements against pip freeze",
     "20 equal, 0 missing, 0 version differences; matplotlib's 9 dependencies unpinned; matplotlib listed under 'pulled in by requests'",
     "stale", "pin contourpy, cycler, fonttools, kiwisolver, packaging, pillow, pyparsing, python-dateutil, six under a matplotlib heading", ""),
    ("T04", "tests", "tests/README.md", "text against the run", "says the tests 'finish in seconds'; about 43 s",
     "cosmetic", "say 'in under a minute'", ""),
    ("T05", "tests", "tests/", "coverage",
     "no test for the two workflows, session92's checks, session87's guard modes, the scripts of sessions 112 to 119, ANALYSIS.md against its tables, session118's audit",
     "cosmetic", "optional tests (the live.yml commit step; ANALYSIS.md numbers via C08 and C09)", ""),
    ("A01", "session 114", "data/processed/session114_comparisons/part1.md l.19, 90-101, 108-119, 125, 128; part2_comparisons.md l.3 and missing ANALYSIS.md l.1282-1599",
     "against ANALYSIS.md", "out of date: IFS text and Tables E10 to E16 missing; both written once (write_once_bytes l.1703, 1706)",
     "stale", "re-render after C08 into new files, or mark them superseded; replacing a write-once file needs a ruling", "O"),
    ("A02", "session 114", "scripts/session114_comparisons.py l.1540 (FIG_SOURCES), l.1585; figures/analysis/comparison_*.svg",
     "IFS figure", "none: FIG_SOURCES excludes ifs", "stale", "add IFS: new figure files, or redraw the five (replaces committed figures: ruling)", "O"),
    ("A03", "session 114", "scripts/session114_comparisons.py l.587-597 (subdaily_max)", "every window present",
     "docstring says the day must hold every window; the code does not check; no effect (0 of 3,301 days lack a window, F160.6)",
     "cosmetic", "add the count check; rerun --dailymax --source ifs into a trial folder to show no change", ""),
    ("A04", "session 114", "scripts/session114_comparisons.py l.161-172 (F156_4), l.932", "IFS cycle counts",
     "no ifs key, so the loader check is skipped for IFS (F160.3)", "cosmetic",
     "add ifs from F160.3 (dev 1,461 / 1,460 / 1,460; claim 1,460 / 1,460) with a test (D98.2); rerun --match into a trial folder", ""),
    ("M01", "MLwx-live", ".github/workflows/live.yml (deployed) against deploy/mlwx-live/.github/workflows/live.yml",
     "diff", "only l.31-32 (MLWX_COMMIT d6ca3e4, MODELS_TAG gfs-models-49) differ (D113.2); requirements.txt and .gitignore equal",
     "OK", "", ""),
    ("M02", "MLwx-live", "deploy/mlwx-live/README.md l.65-68", "text against D112.6",
     "'every hour at 40 minutes past'; 'fails only if ... exit code 3'; 'tried again the next hour'",
     "stale", "say :15 and :40, and that the job also fails when the push does not land", ""),
    ("M03", "MLwx-live", "MLwx-live README.md (deployed)", "text against the template and D105",
     "session 109's v1 file (6cfb0d3): 'for 12 airports', test 'will be written down', no snapshot section, old schedule line",
     "stale", "after M02, the owner copies the template README at the next redeploy", "O"),
    ("M04", "MLwx-live", "deploy/mlwx-live/.github/workflows/live.yml l.3-4", "header comment",
     "'A run with nothing new to issue only republishes the page': it also commits the state's last_run (M07)",
     "cosmetic", "fix the comment with M07", ""),
    ("M05", "MLwx-live", "deploy/mlwx-live/.github/workflows/live.yml l.59, 65, 72, 81, 134, 137, 143",
     "actions on Node.js 20 (F161.10(4))",
     "checkout@v4, setup-python@v5, cache@v4, configure-pages@v5, upload-pages-artifact@v3 (upload-artifact@v4 inside), deploy-pages@v4 forced to Node.js 24; first node24 majors: checkout v5, setup-python v6, cache v5, configure-pages v6, deploy-pages v5, upload-pages-artifact v5 (uses upload-artifact v7)",
     "stale", "move to those majors in the template, test, owner redeploys; issue times only, so D112.7's treatment", "O"),
    ("M06", "MLwx-live", "deploy/mlwx-live/.github/workflows/live.yml l.74", "setup-python version",
     "python-version '3.12' floats; all 5 runs since the redeploy used CPython 3.12.15 (as F161.10(5))",
     "stale", "pin '3.12.15'; a future patch could change a logged value, so judge under D105.5(k)", "LO"),
    ("M07", "MLwx-live", "src/mlwx/runner.py (state last_run), live.yml commit step", "runs committing only last_run",
     "2 of 5 runs since the redeploy (7b4a349, 1bbbb95) changed only state's last_run.at; any two overlapping runs conflict on the state file (F161.10(2))",
     "stale", "do not commit when only last_run changed (or keep last_run out of the committed state); no logged value changes", "LO"),
    ("M08", "MLwx-live", "log/, obs/ in the clone", "cycles 2026-10-19T12z to 2026-10-21T06z (F161.3's method)",
     "8 of 8 logged, added once, never changed, leads 3-48 complete, snapshots 8; 0 lost; 0 issued twice; 0 stale checkouts; 0 silent push failures",
     "OK", "", "L"),
    ("M09", "MLwx-live", "gh run list", "cadence since the redeploy (F161.8's method)",
     "4 scheduled runs in 43 slots (9 %; :15 3, :40 1) over about 21.6 h; gaps 2.43 to 5.79 h; issue lag 5.18, 6.57, 6.35 h; 21T12z not yet issued at the cutoff (5.27 h after the last run); about one day of data",
     "OK", "reading: re-measure after more days before D112.6(d)'s outside-scheduler question", "O"),
    ("M10", "MLwx-live", "MLwx-live page", "latest cycle against the log", "2026-10-21 06z issued 12:21 UTC, 49 lines: MATCH",
     "OK", "", ""),
    ("M11", "MLwx-live", "scripts/session118_live_audit.py (parse_run_log)", "parses every run log",
     "the redeploy run's log came with named steps, not 'UNKNOWN STEP'; its commit and page were missed and read by hand",
     "cosmetic", "split sections by step name too, if the audit script is reused", ""),
    ("X01", "IFS T5", "data/processed/session120_audit/t5_extra.csv", "F162.9(6): 2 fetches on the main 0.25 degree grid",
     "2024-02-03T00z step 24 and 2026-07-31T00z step 21: SHA-256, metadata and 30 of 30 rows bit-equal; D113.6(e)'s mark not shown",
     "OK", "", ""),
]


def run_register():
    rows = []
    for (i, area, f, chk, res, sev, fix, fl) in REG:
        rows.append({"id": i, "area": area, "file": f, "checked": chk, "result": res, "severity": sev,
                     "proposed_fix": fix, "touches_record": "yes" if "R" in fl else "no",
                     "touches_frozen": "yes" if "F" in fl else "no",
                     "touches_live_test": "yes" if "L" in fl else "no",
                     "needs_owner_ruling": "yes" if "O" in fl else "no"})
    write_csv(REGISTER, REG_COLS, rows)
    c = Counter(r["severity"] for r in rows)
    print(f"register: {len(rows)} rows; by severity {dict(c)}; owner ruling "
          f"{sum(r['needs_owner_ruling'] == 'yes' for r in rows)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--register", action="store_true")
    ap.add_argument("--t5-picks", action="store_true", help="Step 9's two picks, no network")
    ap.add_argument("--t5", action="store_true", help="Step 9's two fetches (network)")
    ap.add_argument("--live", metavar="TMP", help="Step 8 on TMP/live and TMP/live_work")
    ap.add_argument("--layout", action="store_true")
    ap.add_argument("--paths", action="store_true")
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--run-checks", metavar="CLONE",
                    help="run Step 5's modes in this temporary clone of HEAD")
    a = ap.parse_args()
    if a.register:
        run_register()
    if a.t5_picks or a.t5:
        run_t5(a.t5)
    if a.live:
        run_live(a.live)
    if a.run_checks:
        run_checks(a.run_checks)
    if a.layout:
        run_layout()
    if a.paths:
        run_paths()
    if a.inventory:
        run_inventory()


if __name__ == "__main__":
    main()
