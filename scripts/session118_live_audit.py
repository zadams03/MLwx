"""Session 118: a read-only audit of MLwx-live's runs (DECISIONS D112.5).

Reads only a fresh clone of zadams03/MLwx-live, `gh` output (the run list and each run's log) and
the public page, fetched once. Writes two CSVs and prints a short summary (D93.12).

No error is computed (D105.6). The log files are read only for their airport, cycle, lead,
issue time, code commit, model SHA-256 and GFS version columns; no forecast value is used. The
observation snapshots are counted by lines, never parsed. The page is read only for the cycle
and issue time it shows.

Usage:
  python3 scripts/session118_live_audit.py --clone /tmp/s118/live --work /tmp/s118

`--work` caches the run list (runs.json), each run's log (runlogs/<id>.txt) and the page
(page.html); a cached file is used as it is, so a rerun reads the same snapshot.
"""

import argparse
import csv
import datetime as dt
import json
import re
import statistics
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from mlwx import config                                    # noqa: E402
from mlwx.runner import AVAILABLE_AFTER                    # noqa: E402  the runner's rule, cycle + 4 h 10 min

REPO = "zadams03/MLwx-live"
PAGE_URL = "https://zadams03.github.io/MLwx-live/"
FIRST_CYCLE = dt.datetime(2026, 10, 12, 12)                # D105.5(d): the test starts at 2026-10-12 12z
RUNS_CSV = ROOT / "data/processed/session118_runs.csv"
CYCLES_CSV = ROOT / "data/processed/session118_cycles.csv"
HOUR = dt.timedelta(hours=1)
RUN_FIELDS = "databaseId,event,status,conclusion,createdAt,startedAt,updatedAt,headSha"
# The schedules in force, from the workflow's history in the clone: the v1 workflow (6cfb0d3) ran at
# 04:10, 10:10, 16:10 and 22:10 UTC; the redeploy commit 526fe80 (D105.2) set one hourly slot at :40.
HOURLY_FROM_COMMIT = "526fe80"


def parse_time(s):
    """An ISO time with Z or an offset, as naive UTC."""
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return t.astimezone(dt.timezone.utc).replace(tzinfo=None)


def iso(t):
    return "" if t is None else f"{t:%Y-%m-%dT%H:%M:%SZ}"


def git(clone, *args):
    return subprocess.run(["git", "-C", str(clone), *args], capture_output=True, text=True, check=True).stdout


def is_on_main(clone, sha):
    r = subprocess.run(["git", "-C", str(clone), "merge-base", "--is-ancestor", sha, "main"], capture_output=True)
    return r.returncode == 0


# ---------------------------------------------------------------------------------------------
# Inputs (cached)

def load_runs(work):
    path = work / "runs.json"
    if not path.exists():
        out = subprocess.run(["gh", "run", "list", "--repo", REPO, "--workflow", "live.yml", "--limit", "1000",
                              "--json", RUN_FIELDS], capture_output=True, text=True, check=True).stdout
        path.write_text(out)
    return json.loads(path.read_text())


def load_log(work, run_id):
    """The run's log text, or None if gh could not give it (counted, never guessed)."""
    d = work / "runlogs"
    d.mkdir(exist_ok=True)
    path = d / f"{run_id}.txt"
    if not path.exists() or path.stat().st_size == 0:
        r = subprocess.run(["gh", "run", "view", str(run_id), "--repo", REPO, "--log"], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            return None
        path.write_text(r.stdout)
    return path.read_text()


def load_page(work):
    path = work / "page.html"
    if not path.exists():
        with urllib.request.urlopen(PAGE_URL, timeout=60) as resp:
            path.write_bytes(resp.read())
    return path.read_text()


# ---------------------------------------------------------------------------------------------
# (a) Runs

LINE = re.compile(r"^[^\t]*\t[^\t]*\t(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z ?(.*)$")
ISSUED = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d)z: issued (\d+) rows to (\S+);")
ORDER = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d)z: not issued: a later cycle is already in the log")
NOTHING = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d)z: ISSUED NOTHING")
WAITING = re.compile(r"^(\d{4}-\d\d-\d\dT\d\d)z: issued nothing yet")
SUMMARY = re.compile(r"^issued (\d+), stopped (\d+), (?:not issued \(tracker order\) (\d+), )?waiting (True|False), "
                     r"already done (\d+)$")
PUSHED = re.compile(r"^\s+([0-9a-f]{7,40})\.\.([0-9a-f]{7,40})\s+main\s+->\s+main\s*$")
LOCAL_COMMIT = re.compile(r"^\[main ([0-9a-f]{7,40})\] Cycles issued")
LATEST_ONLY = re.compile(r'if \[ "([a-z]*)" = "true" \]')


def log_lines(text):
    """[(time, message)] from `gh run view --log`: job, step, timestamp and message per line."""
    out = []
    for raw in text.splitlines():
        m = LINE.match(raw)
        if m:
            out.append((dt.datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S"), m.group(2)))
    return out


def sections(lines):
    """Split the log at each '##[group]Run <first line>' into (header, [messages])."""
    out, cur = [], ("(setup)", [])
    for _, msg in lines:
        if msg.startswith("##[group]Run "):
            out.append(cur)
            cur = (msg[len("##[group]Run "):], [])
        else:
            cur[1].append(msg)
    out.append(cur)
    return out


def parse_checkout(msgs):
    """From the first checkout (this repo): the remote main the fetch saw, and the commit checked out."""
    remote_main = checked_out = None
    forced = False
    for i, m in enumerate(msgs):
        if m.endswith("git rev-parse refs/remotes/origin/main") and i + 1 < len(msgs):
            remote_main = msgs[i + 1].strip()
        if m.endswith("git log -1 --format=%H") and i + 1 < len(msgs):
            checked_out = msgs[i + 1].strip()
        if "(forced update)" in m and "-> origin/main" in m:
            forced = True
    return remote_main, checked_out, forced


def parse_run_log(text):
    lines = log_lines(text)
    secs = sections(lines)
    r = {"job_start": lines[0][0] if lines else None, "latest_only": "", "issued": [], "order": [], "nothing": [],
         "waiting": [], "summary": "", "exit_code": "", "remote_main_at_checkout": "", "checked_out": "",
         "checkout_forced_back": False, "commit_step": False, "nothing_to_commit": False, "local_commit": "",
         "push_rejects": 0, "rebase_conflict": False, "pushed_sha": "", "page_published": False,
         "fail_step_code3": False}
    checkouts = [m for h, m in secs if h.startswith("actions/checkout")]
    if checkouts:
        rm, co, forced = parse_checkout(checkouts[0])
        r["remote_main_at_checkout"], r["checked_out"], r["checkout_forced_back"] = rm or "", co or "", forced
    for head, msgs in secs:
        body = [head] + msgs
        if head.startswith("set +e"):
            for m in body:
                mm = LATEST_ONLY.search(m)
                if mm:
                    r["latest_only"] = mm.group(1) or "(none: not a manual run)"
                for rx, key in ((ISSUED, "issued"), (ORDER, "order"), (NOTHING, "nothing"), (WAITING, "waiting")):
                    mm = rx.match(m)
                    if mm:
                        r[key].append(mm.group(1) + "z" + (f" ({mm.group(2)} rows)" if key == "issued" else ""))
                mm = SUMMARY.match(m)
                if mm:
                    r["summary"] = m
                    stopped, waiting = int(mm.group(2)), mm.group(4) == "True"
                    r["exit_code"] = 3 if stopped else 2 if waiting else 0        # runner.main's rule
        elif head.startswith('git config user.name "mlwx-live"'):
            r["commit_step"] = True
            for m in msgs:
                if m.strip() == "nothing new to commit":
                    r["nothing_to_commit"] = True
                mm = LOCAL_COMMIT.match(m)
                if mm:
                    r["local_commit"] = mm.group(1)
                if "! [rejected]" in m:
                    r["push_rejects"] += 1
                if m.startswith("CONFLICT") or m.startswith("error: could not apply"):
                    r["rebase_conflict"] = True
                mm = PUSHED.match(m)
                if mm:
                    r["pushed_sha"] = mm.group(2)
        elif head.startswith("actions/deploy-pages"):
            r["page_published"] = any(m.strip() == "Reported success!" for m in msgs)
        elif head.startswith("echo \"The runner finished with exit code 3"):
            r["fail_step_code3"] = True
    return r


def main_commits(clone):
    """[(committer time, sha)] on main's first-parent line, oldest first."""
    out = []
    for ln in git(clone, "log", "--first-parent", "main", "--format=%H %cI").splitlines():
        sha, t = ln.split()
        out.append((parse_time(t), sha))
    return sorted(out)


def head_at(commits, t):
    """The latest main commit with committer time at or before t."""
    best = None
    for ct, sha in commits:
        if ct <= t:
            best = sha
    return best


def push_outcome(r):
    if not r["commit_step"]:
        return "no commit step (job ended before it)"
    if r["nothing_to_commit"]:
        return "nothing to commit"
    if r["pushed_sha"]:
        return "pushed" if r["push_rejects"] == 0 else f"pushed after {r['push_rejects']} rejected push(es)"
    if r["rebase_conflict"]:
        return "not pushed: rebase conflict"
    return "not pushed: no push line"


def audit_runs(clone, work, runs):
    commits = main_commits(clone)
    shas = [s for _, s in commits]
    rows, prev_end = [], None
    for run in sorted(runs, key=lambda x: x["createdAt"]):
        rid = run["databaseId"]
        created, started = parse_time(run["createdAt"]), parse_time(run["startedAt"])
        text = load_log(work, rid)
        p = parse_run_log(text) if text is not None else None
        head_started = head_at(commits, started)
        head_job = head_at(commits, p["job_start"]) if p and p["job_start"] else None

        def older(head):
            if head is None or run["headSha"] == head:
                return False
            return run["headSha"] in shas and shas.index(run["headSha"]) < shas.index(head)

        row = {"run_id": rid, "event": run["event"], "status": run["status"], "conclusion": run["conclusion"],
               "created_utc": iso(created), "started_utc": iso(started), "updated_utc": iso(parse_time(run["updatedAt"])),
               "head_sha": run["headSha"], "main_head_at_started": head_started or "",
               "stale_by_started": older(head_started), "log_available": p is not None,
               "queued_behind_previous_run": prev_end is not None and created < prev_end}
        prev_end = parse_time(run["updatedAt"])
        if p:
            pushed_on_main = bool(p["pushed_sha"]) and is_on_main(clone, p["pushed_sha"])
            local_on_main = bool(p["local_commit"]) and is_on_main(clone, p["local_commit"])
            row.update({
                "job_start_utc": iso(p["job_start"]), "main_head_at_job_start": head_job or "",
                "stale_by_job_start": older(head_job),
                "remote_main_at_checkout": p["remote_main_at_checkout"], "checked_out": p["checked_out"],
                "checkout_forced_back": p["checkout_forced_back"],
                "stale_by_log": bool(p["remote_main_at_checkout"]) and p["remote_main_at_checkout"] != p["checked_out"],
                "latest_only": p["latest_only"], "cycles_issued": " ".join(p["issued"]),
                "tracker_order": " ".join(p["order"]), "issued_nothing": " ".join(p["nothing"]),
                "waiting": " ".join(p["waiting"]), "runner_summary": p["summary"],
                "exit_code_from_summary": p["exit_code"], "fail_step_code3": p["fail_step_code3"],
                "local_commit": p["local_commit"], "push_rejects": p["push_rejects"],
                "rebase_conflict": p["rebase_conflict"], "pushed_sha": p["pushed_sha"],
                "push_outcome": push_outcome(p), "pushed_on_main": pushed_on_main, "local_commit_on_main": local_on_main,
                "page_published": p["page_published"],
                "silent_push_failure": (run["conclusion"] == "success" and bool(p["issued"]) and not pushed_on_main),
            })
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------------------------
# (b) Cycles

def cycle_list(model, now):
    """Every cycle hour from FIRST_CYCLE that has arrived by `now` (runner.available_cycles' rule
    without its 24-hour window)."""
    out, t = [], FIRST_CYCLE
    while t + AVAILABLE_AFTER <= now:
        if t.hour in model.cycle_hours:
            out.append(t)
        t += HOUR
    return out


def file_history(clone, path):
    """[(status, sha, committer time)] for every commit that touched the path, oldest first."""
    out = []
    txt = git(clone, "log", "--follow", "--format=@%H %cI", "--name-status", "--", path)
    sha = t = None
    for ln in txt.splitlines():
        if ln.startswith("@"):
            sha, t = ln[1:].split()
        elif ln.strip():
            out.append((ln.split("\t")[0], sha, t))
    return list(reversed(out))


def read_log_columns(path):
    """Only the non-forecast columns of a log file (no forecast value is used, D105.6)."""
    keep = ["airport", "cycle_utc", "lead", "issued_utc", "code_commit", "model_sha256", "gfs_version"]
    with open(path, newline="") as f:
        rd = csv.reader(f)
        header = next(rd)
        idx = [header.index(k) for k in keep]
        return [dict(zip(keep, (row[i] for i in idx))) for row in rd]


def audit_cycles(clone, model, now, run_rows, state):
    stops = {s["cycle"]: s for s in state.get("stops", [])}
    claims = {}
    for r in run_rows:
        for item in re.findall(r"(\d{4}-\d\d-\d\dT\d\d)z \((\d+) rows\)", r.get("cycles_issued", "")):
            claims.setdefault(item[0], []).append(str(r["run_id"]))
    rows = []
    for c in cycle_list(model, now):
        name = f"{model.name}_{c:%Y%m%d%H}.csv"
        lpath = f"log/{c:%Y}/{c:%m}/{name}"
        opath = f"obs/{c:%Y}/{c:%m}/{name}"
        key = f"{c:%Y-%m-%dT%H}"
        row = {"cycle": f"{key}z", "log_present": (clone / lpath).exists()}
        if row["log_present"]:
            hist = file_history(clone, lpath)
            recs = read_log_columns(clone / lpath)
            per_airport = {}
            for x in recs:
                per_airport.setdefault(x["airport"], []).append(int(x["lead"]))
            full = sorted(range(model.curve_first_lead, model.last_lead + 1))
            issued = sorted({x["issued_utc"] for x in recs})
            lags = [(parse_time(i) - c).total_seconds() / 3600 for i in issued]
            row.update({
                "log_commits": " ".join(f"{s}:{sha[:7]}@{t}" for s, sha, t in hist),
                "log_added_once_never_changed": [s for s, _, _ in hist] == ["A"],
                "rows": len(recs), "airports": len(per_airport),
                "leads_3_48_complete": all(sorted(v) == full for v in per_airport.values()),
                "cycle_column_matches": all(x["cycle_utc"] == f"{key}:00Z" for x in recs),
                "issued": " ".join(issued), "issue_lag_hours": " ".join(f"{x:.2f}" for x in lags),
                "code_commit": " ".join(sorted({x["code_commit"] for x in recs})),
                "model_sha256": " ".join(sorted({x["model_sha256"][:12] for x in recs})),
                "gfs_version": " ".join(sorted({x["gfs_version"] for x in recs})),
            })
        row["snapshot_present"] = (clone / opath).exists()
        if row["snapshot_present"]:
            with open(clone / opath) as f:
                row["snapshot_rows"] = sum(1 for _ in f) - 1           # lines counted, never parsed
            row["snapshot_added_once_never_changed"] = [s for s, _, _ in file_history(clone, opath)] == ["A"]
        s = stops.get(f"{key}:00Z")
        row["stop_reason"] = s["reason"] if s else ""
        row["runs_claiming_issue"] = " ".join(claims.get(key, []))
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------------------------
# (c) Cadence

def schedule_slots(t, hourly):
    """The latest slot of the schedule in force at or before t."""
    if hourly:
        s = t.replace(minute=40, second=0)
        return s if s <= t else s - HOUR
    for back in range(0, 25):
        cand = (t - back * HOUR).replace(minute=10, second=0)
        if cand.hour in (4, 10, 16, 22) and cand <= t:
            return cand
    return None


def slots_between(t0, t1, hourly_from):
    """Every slot of the schedule in force from t0 up to t1."""
    out, t = [], t0.replace(minute=0, second=0)
    while t <= t1:
        for m in (10, 40):
            s = t.replace(minute=m)
            if t0 <= s <= t1 and ((s >= hourly_from and m == 40) or (s < hourly_from and m == 10 and s.hour in (4, 10, 16, 22))):
                out.append(s)
        t += HOUR
    return out


def cadence(clone, run_rows, cutoff):
    hourly_from = parse_time(git(clone, "log", "-1", "--format=%cI", HOURLY_FROM_COMMIT).strip())
    sched = [r for r in run_rows if r["event"] == "schedule"]
    out_rows, prev_created = [], None
    for r in sched:
        t = parse_time(r["created_utc"])
        hourly = t >= hourly_from
        slot = schedule_slots(t, hourly)
        period = HOUR if hourly else dt.timedelta(hours=6)
        delay = (t - slot).total_seconds() / 60
        # Ambiguous: an earlier slot had no run of its own, so this run may belong to it (a delay over 60 min).
        ambiguous = prev_created is None or prev_created < slot - period or delay > 60
        r["schedule_slot_utc"], r["schedule_delay_min"], r["delay_ambiguous"] = iso(slot), round(delay, 1), ambiguous
        out_rows.append(r)
        prev_created = t
    # Per UTC day, from the first schedule slot after the v1 deploy to the audit cutoff: runs and slots.
    first = parse_time(git(clone, "log", "--reverse", "--format=%cI", "--", ".github/workflows/live.yml").split()[0])
    slots = slots_between(first, cutoff, hourly_from)
    per_day = {}
    for s in slots:
        per_day.setdefault(f"{s:%Y-%m-%d}", [0, 0])[1] += 1
    for r in sched:
        per_day.setdefault(r["created_utc"][:10], [0, 0])[0] += 1
    times = [parse_time(r["created_utc"]) for r in run_rows]
    gaps = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:])]
    q = statistics.quantiles(gaps, n=10)
    hg = [(b - a).total_seconds() / 3600 for a, b in zip(times, times[1:]) if a >= hourly_from]
    return {"hourly_from": hourly_from, "per_day": per_day, "slots": len(slots), "gaps": gaps, "gap_median": statistics.median(gaps),
            "gap_p90": q[8], "gap_max": max(gaps), "gaps_over_20h": [g for g in gaps if g > 20],
            "hourly_gap_median": statistics.median(hg), "hourly_gap_p90": statistics.quantiles(hg, n=10)[8],
            "hourly_gap_max": max(hg),
            "delays": [r["schedule_delay_min"] for r in sched], "ambiguous": sum(r["delay_ambiguous"] for r in sched),
            "since_last_run_h": (cutoff - times[-1]).total_seconds() / 3600}


# ---------------------------------------------------------------------------------------------
# (d) The page

def page_check(html, cycle_rows):
    latest = re.search(r"Latest cycle issued: (\d{4}-\d\d-\d\d \d\d)z\. Page built (\d{4}-\d\d-\d\d \d\d:\d\d) UTC", html)
    shown = re.findall(r"cycle (\d{4}-\d\d-\d\d \d\d)z \| GFS (\S+) \| issued (\d{4}-\d\d-\d\d \d\d:\d\d) UTC", html)
    if not shown:
        shown = re.findall(r"cycle (\d{4}-\d\d-\d\d \d\d)z[^<]*?GFS (\S+)[^<]*?issued (\d{4}-\d\d-\d\d \d\d:\d\d) UTC", html)
    logged = [r for r in cycle_rows if r["log_present"]]
    last = logged[-1]
    want_cycle = last["cycle"].replace("T", " ").rstrip("z")
    want_issued = last["issued"].replace("T", " ").rstrip("Z")
    pairs = sorted({(c, i) for c, _, i in shown})
    return {"latest_line": latest.groups() if latest else None, "airport_lines": len(shown), "distinct_shown": pairs,
            "log_latest_cycle": want_cycle, "log_latest_issued": want_issued,
            "match": bool(latest) and latest.group(1) == want_cycle and pairs == [(want_cycle, want_issued)]}


# ---------------------------------------------------------------------------------------------

def write_csv(path, rows):
    fields = []
    for r in rows:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def quantile(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p * (len(xs) - 1))))]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    a = ap.parse_args(argv)
    model = config.get_model("gfs")

    head_sha, head_time = git(a.clone, "log", "-1", "--format=%H %cI").split()
    head_time = parse_time(head_time)
    runs = load_runs(a.work)
    run_rows = audit_runs(a.clone, a.work, runs)
    state = json.loads((a.clone / "state" / "tracker_gfs.json").read_text())
    cycle_rows = audit_cycles(a.clone, model, head_time, run_rows, state)
    cutoff = dt.datetime.fromtimestamp((a.work / "runs.json").stat().st_mtime, dt.timezone.utc).replace(tzinfo=None)
    cad = cadence(a.clone, run_rows, cutoff)
    page = page_check(load_page(a.work), cycle_rows)
    write_csv(RUNS_CSV, run_rows)
    write_csv(CYCLES_CSV, cycle_rows)

    # Whole-history check of log/ and obs/: any file modified, deleted or renamed after it was added.
    changed = [ln for ln in git(a.clone, "log", "--format=", "--name-status", "--", "log", "obs").splitlines()
               if ln and ln[0] in "MDR"]

    with_log = [r for r in run_rows if r["log_available"]]
    out_by = {}
    for r in with_log:
        out_by[r["push_outcome"]] = out_by.get(r["push_outcome"], 0) + 1
    issued_claims = sum(len(re.findall(r"z \(", r["cycles_issued"])) for r in with_log)
    lags = [float(x) for r in cycle_rows if r["log_present"] for x in r["issue_lag_hours"].split()]

    print(f"clone HEAD {head_sha[:7]} at {iso(head_time)}; runs {len(runs)}, rows {len(run_rows)}, logs "
          f"{len(with_log)}, missing {len(run_rows) - len(with_log)}")
    print(f"cycles {cycle_rows[0]['cycle']} to {cycle_rows[-1]['cycle']}: {len(cycle_rows)} rows; logged "
          f"{sum(r['log_present'] for r in cycle_rows)}; not logged {sum(not r['log_present'] for r in cycle_rows)}; "
          f"added once, never changed {sum(bool(r.get('log_added_once_never_changed')) for r in cycle_rows)}; "
          f"leads complete {sum(bool(r.get('leads_3_48_complete')) for r in cycle_rows)}; snapshots "
          f"{sum(r['snapshot_present'] for r in cycle_rows)}")
    print(f"issue claims in run logs {issued_claims}; cycles claimed by more than one run "
          f"{sum(len(r['runs_claiming_issue'].split()) > 1 for r in cycle_rows)}; log/ or obs/ changes after add "
          f"{len(changed)}")
    print(f"stale checkout: by startedAt {sum(r['stale_by_started'] for r in run_rows)}, by job start "
          f"{sum(bool(r.get('stale_by_job_start')) for r in with_log)}, by log {sum(bool(r.get('stale_by_log')) for r in with_log)}")
    print("push outcomes: " + "; ".join(f"{k} {v}" for k, v in sorted(out_by.items())) +
          f"; silent push failures {sum(bool(r.get('silent_push_failure')) for r in with_log)}")
    print(f"latest_only true: {[r['run_id'] for r in with_log if r['latest_only'] == 'true']}")
    print(f"audit cutoff (run list fetched) {iso(cutoff)}; scheduled runs per UTC day (slots in force): " +
          ", ".join(f"{d[5:]} {n} ({k})" for d, (n, k) in sorted(cad["per_day"].items())) +
          f"; total {len(cad['delays'])} of {cad['slots']} slots")
    dl = cad["delays"]
    print(f"delay to the latest slot (a minimum; ambiguous {cad['ambiguous']} of {len(dl)}): median "
          f"{statistics.median(dl):.1f} min, max {max(dl):.1f}; gaps between runs: median {cad['gap_median']:.2f} h, "
          f"p90 {cad['gap_p90']:.2f} h, max {cad['gap_max']:.2f} h, over 20 h {len(cad['gaps_over_20h'])}; "
          f"last run to cutoff {cad['since_last_run_h']:.2f} h")
    print(f"gaps from the hourly schedule on ({iso(cad['hourly_from'])}): median {cad['hourly_gap_median']:.2f} h, "
          f"p90 {cad['hourly_gap_p90']:.2f} h, max {cad['hourly_gap_max']:.2f} h; runs queued behind another "
          f"{[r['run_id'] for r in run_rows if r['queued_behind_previous_run']]}")
    print(f"issue lag: median {statistics.median(lags):.2f} h, min {min(lags):.2f} h, max {max(lags):.2f} h over "
          f"{len(lags)} cycles")
    print(f"page: latest line {page['latest_line']}, airport lines {page['airport_lines']}, shown {page['distinct_shown']}; "
          f"log latest {page['log_latest_cycle']} issued {page['log_latest_issued']}: "
          f"{'MATCH' if page['match'] else 'NO MATCH'}")
    ok = (len(run_rows) == len(runs) and len(cycle_rows) == len(cycle_list(model, head_time))
          and sum(out_by.values()) == len(with_log))
    print(f"checks (a row per run, a row per cycle, push outcomes add up): {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
