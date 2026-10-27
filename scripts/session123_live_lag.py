"""Session 123: the issue lag re-measured after the redeploy (DECISIONS D117.3, D112.5's method).

Read-only, on a fresh clone of zadams03/MLwx-live and `gh` output (the run list and each run's log)
plus one fetch of the public page. Imports session 118's audit script and does not change it: its
main() is not called (it writes session 118's committed tables, and its slot model knows only :40).

The window runs from the redeploy's check run (39488813037, 2026-10-20) to the latest cycle
available when the run list was fetched. Scheduled and manual runs are reported apart; the
2026-10-21 18z cycle counts as manual (owner ruling, D117.3).

No error is computed (D105.6). The log files are read only for their non-forecast columns, the
observation snapshots are counted by lines, and the state file is compared by key path only (no
value is printed or written).

Usage:
  python3 scripts/session123_live_lag.py --clone TMP/live --work TMP/work

`--work` holds runs.json, runlogs/<id>.txt and page.html, as session 118's script caches them.
"""

import argparse
import datetime as dt
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import session118_live_audit as a118                       # noqa: E402  read-only
from mlwx import config                                    # noqa: E402
from mlwx.runner import AVAILABLE_AFTER                    # noqa: E402

REDEPLOY_RUN = 39488813037           # D113.2, D117.3
REDEPLOY_COMMIT = "0d77fb0"          # D113.2: MLwx-live's redeploy commit
OWNER_MANUAL = {"2026-10-21T18z"}    # D117.3: issued by a manual run, counted as manual
SLOT_MINUTES = (15, 40)              # D112.6(d)
STATE = "state/tracker_gfs.json"
RUNS_CSV = ROOT / "data/processed/session123_runs.csv"
CYCLES_CSV = ROOT / "data/processed/session123_cycles.csv"
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(hours=24)

# Each step's first log line starts with a byte-order mark before the timestamp, which session 118's
# line pattern does not allow; strip it before its parser sees the text (swapped at run time).
_parse = a118.parse_run_log
a118.parse_run_log = lambda text: _parse(text.replace("﻿", ""))


def python_version(text):
    for ln in text.replace("﻿", "").splitlines():
        if "Successfully set up CPython (" in ln:
            return ln.split("CPython (")[1].split(")")[0]
    return ""


def latest_slot(t):
    cands = [t.replace(minute=m, second=0, microsecond=0) for m in SLOT_MINUTES]
    cands += [(t - HOUR).replace(minute=m, second=0, microsecond=0) for m in SLOT_MINUTES]
    return max(c for c in cands if c <= t)


def slots_between(t0, t1):
    out, t = [], t0.replace(minute=0, second=0, microsecond=0)
    while t <= t1:
        out += [t.replace(minute=m) for m in SLOT_MINUTES if t0 <= t.replace(minute=m) <= t1]
        t += HOUR
    return out


def key_paths(obj, prefix=""):
    """{path: leaf value} for every leaf of a JSON object (values are compared, never shown)."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out.update(key_paths(v, f"{prefix}.{k}" if prefix else k))
        return out
    if isinstance(obj, list):
        out = {}
        for i, v in enumerate(obj):
            out.update(key_paths(v, f"{prefix}[{i}]"))
        return out or {prefix: []}
    return {prefix: obj}


def generalise(path):
    """A changed path with its airport key folded, so a change at 49 airports counts as one kind."""
    parts = path.split(".")
    return ".".join("<airport>" if len(p) == 4 and p.isupper() and p.isalpha() else p for p in parts)


def commits_since(clone):
    rows = []
    for c in a118.git(clone, "rev-list", "--reverse", f"{REDEPLOY_COMMIT}..main").split():
        files = a118.git(clone, "show", "--format=", "--name-only", c).split()
        row = {"commit": c[:7], "time": a118.git(clone, "log", "-1", "--format=%cI", c).strip(),
               "files": len(files), "state_only": all(f.startswith("state/") for f in files),
               "touches_log_obs": any(f.startswith(("log/", "obs/")) for f in files)}
        if row["state_only"]:
            before = key_paths(json.loads(a118.git(clone, "show", f"{c}^:{STATE}")))
            after = key_paths(json.loads(a118.git(clone, "show", f"{c}:{STATE}")))
            changed = sorted(p for p in before.keys() | after.keys() if before.get(p, "<none>") != after.get(p, "<none>"))
            row["state_paths_changed"] = " ".join(changed)
            row["state_kinds_changed"] = " ".join(sorted({generalise(p) for p in changed}))
        rows.append(row)
    return rows


def q90(xs):
    return statistics.quantiles(xs, n=10)[8] if len(xs) > 1 else xs[0]


def lag_line(name, xs):
    return (f"{name}: n {len(xs)}, median {statistics.median(xs):.2f} h, p90 {q90(xs):.2f} h, "
            f"min {min(xs):.2f} h, max {max(xs):.2f} h")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--clone", required=True, type=Path)
    ap.add_argument("--work", required=True, type=Path)
    a = ap.parse_args(argv)
    model = config.get_model("gfs")
    clone, work = a.clone, a.work

    head_sha, head_time = a118.git(clone, "log", "-1", "--format=%H %cI").split()
    redeploy_t = a118.parse_time(a118.git(clone, "log", "-1", "--format=%cI", REDEPLOY_COMMIT).strip())
    cutoff = dt.datetime.fromtimestamp((work / "runs.json").stat().st_mtime, dt.timezone.utc).replace(tzinfo=None)
    runs = [r for r in a118.load_runs(work) if r["databaseId"] >= REDEPLOY_RUN]

    # Runs.
    run_rows = a118.audit_runs(clone, work, runs)
    for r in run_rows:
        text = a118.load_log(work, r["run_id"])
        r["python_version"] = python_version(text) if text else ""
        if r["event"] == "schedule":
            c = a118.parse_time(r["created_utc"])
            s = latest_slot(c)
            r["slot_utc"], r["slot_minute"], r["delay_min"] = a118.iso(s), f":{s.minute:02d}", round((c - s).total_seconds() / 60, 1)
    sched = [r for r in run_rows if r["event"] == "schedule"]
    slots = slots_between(redeploy_t, cutoff)
    per_day = {}
    for s in slots:
        per_day.setdefault(f"{s:%Y-%m-%d}", [0, 0])[1] += 1
    for r in sched:
        per_day.setdefault(r["created_utc"][:10], [0, 0])[0] += 1
    times = [a118.parse_time(r["created_utc"]) for r in run_rows]
    gaps = [(b - c).total_seconds() / 3600 for c, b in zip(times, times[1:])]
    delays = [r["delay_min"] for r in sched]

    # Cycles: every cycle first available at or after the redeploy, up to the cutoff.
    state = json.loads((clone / STATE).read_text())
    event = {str(r["run_id"]): r["event"] for r in run_rows}
    cyc = [r for r in a118.audit_cycles(clone, model, cutoff, run_rows, state)
           if a118.parse_time(r["cycle"][:13].replace("T", " ") + ":00") + AVAILABLE_AFTER >= redeploy_t]
    for r in cyc:
        c = dt.datetime.strptime(r["cycle"], "%Y-%m-%dT%Hz")
        claim = r["runs_claiming_issue"].split()
        r["issued_by_event"] = " ".join(event.get(x, "?") for x in claim)
        by_log = "manual" if r["issued_by_event"] == "workflow_dispatch" else "scheduled" if r["issued_by_event"] == "schedule" else ""
        r["counted_as"] = "manual" if r["cycle"] in OWNER_MANUAL else by_log
        r["owner_ruling_agrees_with_log"] = (r["cycle"] not in OWNER_MANUAL) or by_log == "manual"
        r["first_lag_h"] = float(r["issue_lag_hours"].split()[0]) if r.get("issue_lag_hours") else ""
        r["lost"] = not r["log_present"] and c + DAY <= cutoff
        r["pending"] = not r["log_present"] and c + DAY > cutoff
    logged = [r for r in cyc if r["log_present"]]
    lags_all = [r["first_lag_h"] for r in logged]
    lags_sched = [r["first_lag_h"] for r in logged if r["counted_as"] == "scheduled"]
    lags_man = [r["first_lag_h"] for r in logged if r["counted_as"] == "manual"]
    twice = [r["cycle"] for r in cyc if len(r["runs_claiming_issue"].split()) > 1
             or (r["log_present"] and not r["log_added_once_never_changed"])]
    changed_hist = [ln for ln in a118.git(clone, "log", "--format=", "--name-status", "--", "log", "obs").splitlines()
                    if ln and ln[0] in "MDR"]
    commits = commits_since(clone)
    state_only = [c for c in commits if c["state_only"]]

    page = a118.page_check(a118.load_page(work), cyc)
    a118.write_csv(RUNS_CSV, run_rows)
    a118.write_csv(CYCLES_CSV, cyc)

    print(f"clone HEAD {head_sha[:7]} at {head_time}; redeploy commit {REDEPLOY_COMMIT} at {a118.iso(redeploy_t)}; "
          f"run list fetched (cutoff) {a118.iso(cutoff)}")
    print(f"runs since {REDEPLOY_RUN}: {len(run_rows)} (scheduled {len(sched)}, manual "
          f"{sum(r['event'] == 'workflow_dispatch' for r in run_rows)}); conclusions "
          f"{dict(Counter(r['conclusion'] for r in run_rows))}; logs {sum(r['log_available'] for r in run_rows)}")
    print(f"slots :15 and :40 in the window: {len(slots)}; scheduled runs {len(sched)} ({100 * len(sched) / len(slots):.0f} %); "
          f"by slot {dict(sorted(Counter(r['slot_minute'] for r in sched).items()))} of "
          f"{dict(sorted(Counter(f':{s.minute:02d}' for s in slots).items()))}")
    print("per UTC day, scheduled runs (slots): " + ", ".join(f"{d[5:]} {n} ({k})" for d, (n, k) in sorted(per_day.items())))
    print(f"delay to the latest slot: median {statistics.median(delays):.1f} min, max {max(delays):.1f} min; "
          f"gaps between runs: median {statistics.median(gaps):.2f} h, p90 {q90(gaps):.2f} h, max {max(gaps):.2f} h; "
          f"last run to cutoff {(cutoff - times[-1]).total_seconds() / 3600:.2f} h")
    print(f"cycles {cyc[0]['cycle']} to {cyc[-1]['cycle']}: {len(cyc)}; logged {len(logged)}; lost "
          f"{sum(r['lost'] for r in cyc)}; pending {[r['cycle'] for r in cyc if r['pending']]}; issued twice {twice}; "
          f"leads complete {sum(bool(r.get('leads_3_48_complete')) for r in logged)}; snapshots "
          f"{sum(r['snapshot_present'] for r in cyc)}; stops {[r['cycle'] for r in cyc if r['stop_reason']]}")
    print(f"counted as manual {[r['cycle'] for r in cyc if r['counted_as'] == 'manual']}; owner ruling agrees "
          f"with the run log {all(r['owner_ruling_agrees_with_log'] for r in cyc)}")
    print("issue lag, " + lag_line("all cycles", lags_all))
    print("issue lag, " + lag_line("scheduled-issued", lags_sched))
    if lags_man:
        print("issue lag, manual-issued: " + ", ".join(f"{x:.2f}" for x in lags_man) + " h")
    print(f"log/ or obs/ files modified, deleted or renamed, whole history: {len(changed_hist)}")
    print(f"commits since {REDEPLOY_COMMIT}: {len(commits)}; touching log/ or obs/ {sum(c['touches_log_obs'] for c in commits)}; "
          f"state/ only {len(state_only)}; state/ only, kinds of path changed "
          f"{dict(Counter(c['state_kinds_changed'] for c in state_only))}")
    print(f"python versions {dict(Counter(r['python_version'] for r in run_rows))}")
    print(f"push outcomes {dict(Counter(r.get('push_outcome') for r in run_rows))}; stale by log "
          f"{sum(bool(r.get('stale_by_log')) for r in run_rows)}; silent push failures "
          f"{sum(bool(r.get('silent_push_failure')) for r in run_rows)}; pages published "
          f"{sum(bool(r.get('page_published')) for r in run_rows)}")
    print(f"page: latest {page['latest_line']}, airport lines {page['airport_lines']}; log latest "
          f"{page['log_latest_cycle']} issued {page['log_latest_issued']}: {'MATCH' if page['match'] else 'NO MATCH'}")
    stop = sum(r["lost"] for r in cyc) or twice or changed_hist
    print(f"D112.7 stop condition (lost, issued twice, log or obs changed): {'STOP' if stop else 'none'}")
    return 1 if stop else 0


if __name__ == "__main__":
    sys.exit(main())
