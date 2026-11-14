"""Session 129: the live test's scoring script (DECISIONS D105.5, D123).

It will judge the pre-registered test of the live forecasts (D105.5): the
`corrected` column of MLwx-live's prediction log, as issued, against raw GFS
and persistence, per airport, period and output (the hourly curve at leads 3
to 48, and the daily maximum read off the logged curve). It implements D105.5
exactly and adds no rule (D123.2). Once committed it is not edited (D62.3(a));
a fix goes in a new script that imports it (D116.10).

Modes (one per run):
  --inventory LIVE_CLONE [--detail FILE]
        D105.5(a) and (h), with no observation. Reads only log/, state/ and
        the git history of a clone of MLwx-live. Lists the names under obs/
        and never opens one. Checks that every log file was added once and
        never changed or deleted; counts, per group (the 12 and the 37),
        cycles with and without a log file, with the state file's reasons;
        each cycle's issue lag; rows issued after their valid time, by lead.
  --gate
        D123.4(a), on spent data only. Builds synthetic logs in MLwx-live's
        format from session 112's regenerated claim predictions, with periods
        set to stage C's two looks and observations taken from the same
        folder's obs_ files, and must reproduce session 107's scores and
        verdicts exactly. Writes to data/processed/session129_gate/.
  --score LIVE_CLONE --period A|B --first-v17-cycle YYYYMMDDHH|none
        The look (D105.5(l)), once per period. It refuses to run unless this
        file is tracked by git and equal to its committed version; the value
        of --first-v17-cycle is `none` or a cycle hour after 2026-10-12T12;
        the period's last valid hour plus 7 days is in the past; no output
        file exists; and the inventory passes in the same run. Only then does
        it fetch the period's observations fresh from IEM. The comparison
        with the obs/ snapshots is made only after the scores are written.
        NOT RUN IN SESSION 129.

Where each rule's code comes from (D123.2):
- imported from scripts/session106_claim_look.py, after its SHA-256 check
  (F150.4): persistence_k and hourly_persistence, observed_max,
  persistence_day and daily_persistence (D100.5, D98.10(a)), margin (D79.1),
  half_pass (D79.2), look_pass, verdict (gate only), hourly_sets, daily_sets,
  hourly_errors, daily_errors, mae_or_none, HIDX; and through it session 97's
  mae, mean_error, fmt, csv_text and write_new;
- imported from src/mlwx: observations.fetch_reports, parse_reports and
  ReportSet(live=True) (D88.7, F152.7 ruling 2); dailymax.local_day,
  day_cycle and read_off (D98.10(b), (c)); prediction_log's columns, time
  format and writer (D103.8); config.load_airports; records.has_stagec_tables
  and new_tables (the 12 and the 37, D103.4, D105.8);
- written here, each with a test: the git history check, the log reader, the
  windows and periods, the counts of D105.5(h), the groupings of D105.5(i)
  (the edge-of-day rule is session 112's reading, D106.7(f), checked by a
  test against its functions), the observation requests, the snapshot
  comparison, the refusals and the gate's comparison.

The design note, with every reading taken where D105.5 leaves a choice open,
is in notes/session-129-output.txt (Step 3) and DECISIONS F172.
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")     # lightgbm loads without the shim (D93.3)

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = Path(__file__).resolve()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


S106_SCRIPT_SHA256 = "5e046acffc6eb28619d1883c8b93b6ff97bc3305addade56be5ab30af169281a"   # F149, F150.4
if sha256_file(HERE / "session106_claim_look.py") != S106_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session106_claim_look.py's SHA-256 is not F150.4's")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))
import session106_claim_look as s106  # noqa: E402

import argparse  # noqa: E402
import collections  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import statistics  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

from mlwx import config, dailymax, observations, prediction_log, records  # noqa: E402

s97 = s106.s97

# ------------------------------------------------------------------ constants

MODEL = "gfs"
CYCLE_HOURS = (0, 6, 12, 18)
LEADS = tuple(range(3, 49))                              # D105.5(b)
LEADS_A, LEADS_B = tuple(range(3, 25)), tuple(range(25, 49))   # D105.5(i)
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)
STEP = dt.timedelta(hours=6)

START_12 = dt.datetime(2026, 10, 12, 12)                 # D105.5(d): the 12 of D103.4
START_37 = dt.datetime(2026, 10, 13, 18)                 # F154.2: the first 49-airport cycle
WINDOW_LAST_CYCLE = dt.datetime(2027, 7, 31, 18)         # D105.5(e)
LAST_VALID = dt.datetime(2027, 7, 31, 23, 0)             # D105.5(e): nothing valid after this is used
LIVE_OBS_FROM = dt.datetime(2026, 10, 12, 0, 0)          # D105.5(l): no observation from here on before the look
WAIT = dt.timedelta(days=7)                              # D105.5(f)
OBS_LEAD_IN = dt.timedelta(days=4)                       # early enough for every persistence value (D123.3)
EXPECTED_12 = 12                                         # D105.5(j): both outputs pass at all 12, period A

METHODS = ("raw_gfs", "baseline", "curve")               # "curve" is the log's `corrected` column
OUTPUTS = ("hourly", "daily")
HALVES = ("raw_gfs", "persistence")
HIDX = s106.HIDX
LIVE_NAME = {"curve": "corrected"}                       # the name written in the live result files

LOG_PATH = re.compile(r"^log/(\d{4})/(\d{2})/" + MODEL + r"_(\d{10})\.csv$")
STAMP = re.compile(r"(\d{10})")
STATE_PATH = f"state/tracker_{MODEL}.json"
NO_REASON = "no reason in the state file"

# --gate (D123.4(a)): spent data only.
PRED_DIR = s97.STAGEC_DIR / "analysis112"
GATE_DIR = ROOT / "data" / "processed" / "session129_gate"
GATE_LIMIT = dt.datetime(2026, 8, 1)                     # the gate reads nothing valid at or after this
GATE_LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)        # D100.4
GATE_PRED = {   # ../MLwx-stagec/analysis112/meta.txt
    "EDDM": "787ad4462fc5af9abf8ea3fccfb9d06ca7df072565e185a8441b4c730899a83f",
    "KORD": "fd0538334adcfb3f0224cb3b9d39e441dba700779a299a97511d77fbc085dece",
    "CYYZ": "44cdd38036e04d0ca73026b6a84b4748b4568f39aace9c9b637cd414906145cd",
    "ZGSZ": "3c0c840a8fc4f30aa673901fa5ddfd636304665ba0b40ab5fa61793c5eb8364e",
    "ZUCK": "71b466a574c923bf937476aee91c48909f6b918b61afc649b37fa41508678b3f",
    "NZWN": "cc1f51923a2347b256341d1b52a70c6265bda841fb921f773ff5e725236b7262",
}
GATE_OBS = {    # ../MLwx-stagec/analysis112/refs_meta.txt
    "EDDM": "068d23c0d3add90c417d1bf8c41670199ca36e925a6aebc9a0654a81e22d3796",
    "KORD": "aaf4401edd1763ac994607f034f9536b4c0feea9720a219bb925cdbfeabb1823",
    "CYYZ": "fd314dc593fd1b9ccd7ea14813d3eb177e55342b8735c80625c2143c1ecf3b68",
    "ZGSZ": "619eb016df4df546a7961d338b7d7cd8d1cb95d80f2992fa8bb089edb5081d8f",
    "ZUCK": "2c73a9347556eeaed707697b06a6af22769088a37bf76fe11d980785f17a1c38",
    "NZWN": "1b114a3ab6cb13f682032d8cf57ae6a425d5a496e8b6dee82024b0b1e1216ebe",
}
S107_SCORES_SHA256 = "2918fff42ab17ff2fce55260d7d0d757638b989943324ddceb3e1a7ff59488ca"     # F150.4
S107_DAYS_SHA256 = "3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297"       # F150.4
S107_VERDICTS_SHA256 = "0a9c1dc80a1e052c5b98a117b6c42cbd9811c160a944be959dca0e4575e319da"   # F150.4
GATE_ISSUE_AFTER = dt.timedelta(hours=4, minutes=10)     # the synthetic issue time (D103.9)

Ap = collections.namedtuple("Ap", "icao station tz group start")
Setup = collections.namedtuple("Setup", "label airports last_cycle last_valid recorded_starts")


class Refusal(Exception):
    """A mode refused to run. No observation was fetched."""


class GitError(Exception):
    """A git command on the clone failed."""


def now_utc():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def cell_text(v):
    return "" if v is None else "true" if v is True else "false" if v is False else s97.fmt(v)


# ------------------------------------------------------------------ airports, windows and periods (D105.5(d), (e))

def live_airports():
    """The 49 airports of the test, fixed by the record: the 12 with stage C tables (D103.4) and the 37
    of session111_new_tables.csv (D105.8). An airport added later to gfs_airports.csv is not in the test."""
    by_icao = {a.icao: a for a in config.load_airports(config.GFS)}
    twelve = [a.icao for a in by_icao.values() if records.has_stagec_tables(a)]
    new = {k[0] for k in records.new_tables()}
    thirty_seven = [ic for ic in by_icao if ic in new]
    if len(twelve) != 12 or len(new) != 37 or len(thirty_seven) != 37 or set(twelve) & new:
        raise SystemExit(f"STOP: the record gives {len(twelve)} and {len(thirty_seven)} airports, not 12 and 37")
    return ([Ap(ic, by_icao[ic].station, by_icao[ic].time_zone, "12", START_12) for ic in twelve]
            + [Ap(ic, by_icao[ic].station, by_icao[ic].time_zone, "37", START_37) for ic in thirty_seven])


def parse_v17(text):
    """--first-v17-cycle: None for `none`, or a cycle hour after 2026-10-12T12 and inside the window."""
    if text == "none":
        return None
    if text is None or not re.fullmatch(r"\d{10}", text):
        raise Refusal(f"--first-v17-cycle must be YYYYMMDDHH or none; got {text!r}")
    try:
        t = dt.datetime.strptime(text, "%Y%m%d%H")
    except ValueError:
        raise Refusal(f"--first-v17-cycle {text!r} is not a date and hour") from None
    if t.hour not in CYCLE_HOURS:
        raise Refusal(f"--first-v17-cycle {text} is not a cycle hour (00, 06, 12 or 18 UTC)")
    if not t > START_12:
        raise Refusal(f"--first-v17-cycle {text} is not after 2026-10-12T12 (D123.3)")
    if t > WINDOW_LAST_CYCLE:
        raise Refusal(f"--first-v17-cycle {text} is after the window's last cycle 2027-07-31T18: "
                      "pass `none` (D105.5(e))")
    return t


def live_setup(period, first_v17, last_cycle=None):
    """The airports, their first cycles and the last cycle of one period (D105.5(d), (e))."""
    aps = live_airports()
    recorded = {"37": START_37}
    if period == "A":
        end = WINDOW_LAST_CYCLE if first_v17 is None else first_v17 - STEP
    elif period == "B":
        if first_v17 is None:
            raise Refusal("period B exists only if GFS v17 starts in the window (D105.5(e)); "
                          "--first-v17-cycle is none")
        aps = [a._replace(start=max(a.start, first_v17)) for a in aps]
        end = WINDOW_LAST_CYCLE
    elif period == "so far":
        end = last_cycle
    else:
        raise Refusal(f"--period must be A or B; got {period!r}")
    return Setup(period, aps, end, LAST_VALID, recorded)


def period_last_valid(setup):
    """The period's last valid hour: its last cycle plus 48 hours, or the limit if that is earlier."""
    return min(setup.last_cycle + LEADS[-1] * HOUR, setup.last_valid)


def cycles_between(first, last):
    out, t = [], first
    while t <= last:
        out.append(t)
        t += STEP
    return out


# ------------------------------------------------------------------ the clone: git history and committed files

def git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), "-c", "core.quotePath=false", *args], capture_output=True)
    if r.returncode:
        raise GitError(f"git {' '.join(args)}: {r.stderr.decode(errors='replace').strip()}")
    return r.stdout.decode()


class Blobs:
    """Reads committed files from the clone with `git cat-file --batch`. Only paths under log/ and
    state/ can be read; obs/ only after `allow_obs()` (the look, after the scores are written).
    `opened` counts the files read, by top folder."""

    def __init__(self, repo):
        self.repo = str(repo)
        self.proc = subprocess.Popen(["git", "-C", self.repo, "cat-file", "--batch"],
                                     stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        self.opened = collections.Counter()
        self.allowed = {"log", "state"}

    def allow_obs(self):
        self.allowed.add("obs")

    def read(self, rev, path):
        top = path.split("/", 1)[0]
        if top not in self.allowed:
            raise SystemExit(f"STOP: a read of {path} was attempted; only {sorted(self.allowed)} may be read")
        self.proc.stdin.write(f"{rev}:{path}\n".encode())
        self.proc.stdin.flush()
        head = self.proc.stdout.readline().split()
        if len(head) != 3 or head[1] != b"blob":
            raise GitError(f"{rev}:{path} is not a committed file")
        data = self.proc.stdout.read(int(head[2]))
        self.proc.stdout.read(1)
        self.opened[top] += 1
        return data

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            self.proc.wait()
        self.proc.stdout.close()


def history_events(repo):
    """Every change to every path in every commit reachable from HEAD: (commits newest first as
    (sha, commit time), {path: [(sha, status)]}). A merge shows only what it changed itself (-c)."""
    out = git(repo, "log", "--root", "--no-renames", "-c", "--name-status", "--format=@%H %ct", "HEAD")
    commits, events, sha = [], {}, None
    for line in out.splitlines():
        if not line:
            continue
        if line.startswith("@"):
            sha, ct = line[1:].split()
            commits.append((sha, int(ct)))
            continue
        status, path = line.split("\t", 1)
        events.setdefault(path, []).append((sha, status))
    return commits, events


def cycle_of_path(path):
    """The cycle of a log file at its own path log/YYYY/MM/gfs_YYYYMMDDHH.csv, or None."""
    m = LOG_PATH.match(path)
    if not m or m.group(3)[:4] != m.group(1) or m.group(3)[4:6] != m.group(2):
        return None
    try:
        t = dt.datetime.strptime(m.group(3), "%Y%m%d%H")
    except ValueError:
        return None
    return t if t.hour in CYCLE_HOURS else None


def parse_log_text(text, cycle):
    """One log file's rows as (airport, lead, raw_gfs, baseline, corrected, issued, (gfs version,
    model SHA-256, code commit)), and the problems found. The columns and time format are the
    log's own (mlwx.prediction_log). A row must name the file's cycle, a lead from 3 to 48 and the
    valid time cycle + lead, once per airport and lead."""
    rows, problems, seen = [], [], set()
    rd = csv.reader(io.StringIO(text))
    if next(rd, None) != prediction_log.LOG_COLUMNS:
        return rows, ["its columns are not the log's"]
    for i, r in enumerate(rd, start=2):
        try:
            icao, cy, lead, valid, raw, base, _b, corr, version, sha, commit, issued = r
            cy, valid, issued = (prediction_log.parse_time(x) for x in (cy, valid, issued))
            lead, raw, base, corr = int(lead), float(raw), float(base), float(corr)
        except ValueError:
            problems.append(f"line {i} cannot be read as a log row")
            continue
        if cy != cycle:
            problems.append(f"line {i} names another cycle")
        elif lead not in LEADS:
            problems.append(f"line {i} has lead {lead}")
        elif valid != cycle + lead * HOUR:
            problems.append(f"line {i}: the valid time is not cycle + lead")
        elif not all(math.isfinite(v) for v in (raw, base, corr)):
            problems.append(f"line {i} holds a value that is not a finite number")
        elif (icao, lead) in seen:
            problems.append(f"line {i} repeats {icao} lead {lead}")
        else:
            seen.add((icao, lead))
            rows.append((icao, lead, raw, base, corr, issued, (version, sha, commit)))
    return rows, problems


def state_stops(blobs, events):
    """{cycle: [reason, ...]} from the stop list of every committed version of the state file (the
    file keeps only its last 100 stops)."""
    stops, unread = {}, 0
    for sha, status in events.get(STATE_PATH, []):
        if "D" in status:
            continue
        try:
            d = json.loads(blobs.read(sha, STATE_PATH))
            for s in d.get("stops", []):
                c = dt.datetime.strptime(s["cycle"], prediction_log.TIME_FORMAT)
                if s["reason"] not in stops.setdefault(c, []):
                    stops[c].append(s["reason"])
        except (ValueError, KeyError, TypeError, GitError):
            unread += 1
    return stops, unread


def inventory(repo, setup, blobs=None):
    """D105.5(a) and (h) with no observation. Returns a dict; `passes` is True only if the clone is
    complete, every log file was added once and never changed or deleted, and every cycle file is a
    log file whose rows fit its name. Missing cycles, second files and late rows are counted and
    never fail it. No file under obs/ is opened: only their names are listed."""
    own = blobs is None
    blobs = blobs or Blobs(repo)
    try:
        inv = {"head": git(repo, "rev-parse", "HEAD").strip(),
               "shallow": git(repo, "rev-parse", "--is-shallow-repository").strip() == "true"}
        commits, events = history_events(repo)
        inv["commits"] = len(commits)
        inv["head_time"] = dt.datetime.fromtimestamp(commits[0][1], dt.timezone.utc).replace(tzinfo=None)
        log_events = {p: [s for _, s in e] for p, e in events.items() if p.startswith("log/")}
        inv["history_paths"] = len(log_events)
        inv["not_write_once"] = sorted((p, "".join(f"[{s}]" for s in reversed(e)))
                                       for p, e in log_events.items() if e != ["A"])
        at_head = [p for p in git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", "log/").splitlines() if p]
        inv["obs_names"] = len([p for p in git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--",
                                                 "obs/").splitlines() if p])
        files, others = {}, []
        for p in at_head:
            c = cycle_of_path(p)
            if c is None:
                m = STAMP.search(p.rsplit("/", 1)[-1])
                others.append((p, m.group(1) if m else ""))
            else:
                files[c] = p
        inv["files"], inv["other_files"] = files, others
        in_test = {a.icao: a for a in setup.airports}
        rows = {a.icao: [] for a in setup.airports}
        info, problems, outside = {}, [], collections.Counter()
        for c in sorted(files):
            p = files[c]
            added = [sha for sha, s in events.get(p, []) if s == "A"]
            if not added:
                problems.append(f"{p}: no commit adds it")
                continue
            got, bad = parse_log_text(blobs.read(added[-1], p).decode("utf-8", errors="replace"), c)
            problems += [f"{p}: {b}" for b in bad[:5]] + ([f"{p}: and {len(bad) - 5} more"] if len(bad) > 5 else [])
            per = collections.Counter()
            issued = set()
            for icao, lead, raw, base, corr, iss, meta in got:
                issued.add(iss)
                if icao in in_test:
                    rows[icao].append((c, lead, raw, base, corr, iss, meta))
                    per[icao] += 1
                else:
                    outside[icao] += 1
            info[c] = {"path": p, "issued": sorted(issued), "per_airport": per, "rows": len(got)}
        inv["rows"], inv["info"], inv["rows_outside"] = rows, info, outside
        for group, want in setup.recorded_starts.items():
            for a in setup.airports:
                if a.group != group:
                    continue
                first = min((r[0] for r in rows[a.icao]), default=None)
                if first != want:
                    problems.append(f"{a.icao}: first logged cycle {first} is not the recorded {want} (F154.2)")
        inv["problems"] = problems
        inv["stops"], inv["state_unread"] = state_stops(blobs, events)
        inv["state_versions"] = len([1 for _, s in events.get(STATE_PATH, []) if "D" not in s])
        last = setup.last_cycle
        if last is None and files:              # "so far": to the newest logged cycle, inside the window
            last = min(max(files), WINDOW_LAST_CYCLE)
        inv["last_cycle"] = last
        groups = {}
        for g in dict.fromkeys(a.group for a in setup.airports):
            aps = [a for a in setup.airports if a.group == g]
            start = min(a.start for a in aps)
            window = cycles_between(start, last) if last is not None else []
            have = [c for c in window if c in info]
            missing = [(c, inv["stops"].get(c, [NO_REASON])) for c in window if c not in info]
            lags = [(c, (info[c]["issued"][-1] - c) / HOUR) for c in have if info[c]["issued"]]
            late, short, before = collections.Counter(), collections.Counter(), collections.Counter()
            for a in aps:
                for c, lead, _, _, _, iss, _ in rows[a.icao]:
                    if c < a.start:
                        before[a.icao] += 1
                    elif last is not None and c <= last and iss > c + lead * HOUR:
                        late[lead] += 1
                for c in have:
                    if c >= a.start and info[c]["per_airport"][a.icao] != len(LEADS):
                        short[a.icao] += 1
            logged = sorted(c for c in info if any(info[c]["per_airport"][a.icao] for a in aps))
            groups[g] = {"airports": len(aps), "start": start, "first_logged": logged[0] if logged else None,
                         "window": len(window), "with_file": len(have), "missing": missing, "lags": lags,
                         "late_by_lead": dict(sorted(late.items())), "short": dict(short), "before": dict(before),
                         "several_issue_times": [c for c in have if len(info[c]["issued"]) > 1]}
        inv["groups"] = groups
        inv["opened"] = dict(blobs.opened)
        inv["passes"] = not inv["shallow"] and not inv["not_write_once"] and not problems
        return inv
    finally:
        if own:
            blobs.close()


def inventory_lines(inv, setup, full=False):
    """The inventory as text: a short summary, or with every cycle (full)."""
    out = [f"clone HEAD {inv['head']} (committed {stamp(inv['head_time'])}); commits {inv['commits']}; "
           f"shallow clone: {inv['shallow']}",
           f"log files at HEAD: {len(inv['files'])} cycle files, {len(inv['other_files'])} other files; "
           f"paths under log/ in the history: {inv['history_paths']}",
           f"write-once (every log path added once, never changed or deleted): "
           f"{'PASS' if not inv['not_write_once'] else 'FAIL'} ({len(inv['not_write_once'])} paths fail)"]
    out += [f"  NOT WRITE-ONCE: {p} events {e}" for p, e in inv["not_write_once"][:20]]
    out += [f"  other file under log/, reported and never scored: {p}"
            + (f" (a second file for cycle {s})" if s else "") for p, s in inv["other_files"][:20]]
    out.append(f"problems with a cycle file's form or an airport's recorded first cycle: {len(inv['problems'])}")
    out += [f"  PROBLEM: {p}" for p in inv["problems"][:20]]
    out.append(f"state file versions read: {inv['state_versions']} ({inv['state_unread']} unreadable); "
               f"cycles with a stop reason: {len(inv['stops'])}")
    out.append(f"rows of airports not in this test: {sum(inv['rows_outside'].values())} "
               f"({len(inv['rows_outside'])} airports)")
    for g, d in inv["groups"].items():
        lags = [x for _, x in d["lags"]]
        out.append(f"group of {g} ({d['airports']} airports): window {stamp(d['start'])} to "
                   f"{stamp(inv['last_cycle']) if inv['last_cycle'] else 'none'}; first logged cycle "
                   f"{stamp(d['first_logged']) if d['first_logged'] else 'none'}; cycles {d['window']}, with a log "
                   f"file {d['with_file']}, without {len(d['missing'])}")
        reasons = collections.Counter(r for _, rs in d["missing"] for r in rs)
        for r, n in reasons.most_common():
            out.append(f"  missing, reason: {n} x {r}")
        if lags:
            out.append(f"  issue lag in hours: median {statistics.median(lags):.2f}, maximum {max(lags):.2f} "
                       f"(cycle {stamp(max(d['lags'], key=lambda x: x[1])[0])}); the five latest cycles: "
                       + ", ".join(f"{stamp(c)} {x:.2f}" for c, x in d["lags"][-5:]))
        out.append("  rows issued after their valid time, by lead: "
                   + (", ".join(f"lead {k}: {v}" for k, v in d["late_by_lead"].items()) or "none"))
        out.append(f"  logged cycles that lack rows for an airport: {sum(d['short'].values())} airport-cycles at "
                   f"{len(d['short'])} airports; rows before an airport's first cycle: {sum(d['before'].values())}; "
                   f"cycle files with more than one issue time: {len(d['several_issue_times'])}")
        if full:
            out += [f"    missing {stamp(c)}: {'; '.join(rs)}" for c, rs in d["missing"]]
            out += [f"    lag {stamp(c)} {x:.2f} h" for c, x in d["lags"]]
            out += [f"    short {ic}: {n} cycles" for ic, n in d["short"].items()]
    out.append(f"names listed under obs/: {inv['obs_names']}; obs/ files opened: {inv['opened'].get('obs', 0)}; "
               f"files read: log {inv['opened'].get('log', 0)}, state {inv['opened'].get('state', 0)}")
    out.append(f"INVENTORY: {'PASS' if inv['passes'] else 'FAIL'}")
    return out


# ------------------------------------------------------------------ observations (D105.5(f))

class ObsLookup:
    """The fresh IEM reports of one airport, paired by the live rule (ReportSet(live=True)).
    `get` is what session 106's persistence and observed-maximum functions call."""

    def __init__(self, report_set, last_valid):
        self.reports, self.last_valid = report_set, last_valid

    def get(self, valid, default=None):
        if valid > self.last_valid:
            raise SystemExit(f"STOP: an observation valid at {valid} was asked for; nothing valid after "
                             f"{self.last_valid} is used (D105.5(e))")
        v = self.reports.nearest(valid)[0]
        return default if v is None else v

    def report(self, valid):
        return self.reports.nearest(valid)


class TableObs:
    """Observations given as {valid: value or None} (the gate and the tests). Refuses any time at or
    after `limit`."""

    def __init__(self, by_valid, limit):
        self.by_valid, self.limit = by_valid, limit

    def get(self, valid, default=None):
        if valid >= self.limit:
            raise SystemExit(f"STOP: an observation valid at {valid} was asked for; the limit is {self.limit}")
        v = self.by_valid.get(valid)
        return default if v is None else v

    def report(self, valid):
        return self.get(valid), None


def month_chunks(first_day, last_day):
    """[(first, last)] by calendar month, covering every day once."""
    out, a = [], first_day
    while a <= last_day:
        nxt = (a.replace(day=1) + dt.timedelta(days=32)).replace(day=1)
        out.append((a, min(last_day, nxt - DAY)))
        a = nxt
    return out


def fetch_observations(setup, raw_dir, fetch, log=print):
    """One IEM request per airport and calendar month, from 4 days before the airport's first cycle
    to the day after the period's last valid hour. Each response is saved unchanged, written once,
    with its query, time and SHA-256 in requests.csv (SPEC 2.3)."""
    raw_dir = Path(raw_dir)
    raw_dir.mkdir(parents=True, exist_ok=False)
    last_day = (period_last_valid(setup) + DAY).date()
    out, req = {}, []
    for a in setup.airports:
        reports, stats = [], observations.new_stats()
        for d0, d1 in month_chunks((a.start - OBS_LEAD_IN).date(), last_day):
            text = fetch(a.station, d0, d1)
            name = f"{a.icao}_{d0:%Y%m%d}_{d1:%Y%m%d}.csv"
            s97.write_new(raw_dir / name, text)
            got = observations.parse_reports(text, a.station, stats)
            reports += got
            req.append([a.icao, a.station, d0.isoformat(), d1.isoformat(), observations.iem_query(a.station, d0, d1),
                        stamp(now_utc()), name, len(text.encode()), hashlib.sha256(text.encode()).hexdigest(),
                        len(got)])
        out[a.icao] = ObsLookup(observations.ReportSet(reports, stats, live=True), setup.last_valid)
        log(f"  {a.icao}: {stats['rows']} reports, {stats['no_temp']} with no temperature, "
            f"{out[a.icao].reports.stats['ambiguous']} repeated times ignored (F152.7)", flush=True)
    s97.write_new(raw_dir / "requests.csv", s97.csv_text(
        ["icao", "station", "first_day", "last_day", "url", "pulled_utc", "file", "bytes", "sha256", "reports"], req))
    return out


# ------------------------------------------------------------------ scoring (D105.5(b), (c), (h), (i))

def peak_hour(vals):
    """The index of the first hour holding the maximum; None values are skipped (D106.7(e))."""
    best = None
    for i, v in enumerate(vals):
        if v is not None and (best is None or v > vals[best]):
            best = i
    return best


def edge_hour(index, n_hours):
    """D105.5(i), D106.7(f): the maximum falls in the first or last hour of the local day."""
    return index is not None and (index == 0 or index == n_hours - 1)


def score_airport(ap, rows, obs, setup, logged):
    """One airport, one period: the hourly rows in session 106's form (period, cycle, observation,
    raw GFS, baseline, corrected, persistence, issued late, model and code), per cycle hour and lead
    in ascending cycle; the local days (D98.10(a) to (c)); and D105.5(h)'s counts. Nothing is filled
    and nothing is dropped without a count."""
    label = setup.label
    hourly = {(h, n): [] for h in CYCLE_HOURS for n in LEADS}
    counts, late_by_lead = collections.Counter(), collections.Counter()
    fc, issued_at = {}, {}
    for cycle, lead, raw, base, corr, issued, meta in sorted(rows, key=lambda r: (r[0], r[1])):
        if cycle < ap.start:
            counts["rows before the airport's first cycle"] += 1
            continue
        if cycle > setup.last_cycle:
            counts["rows after the period's last cycle"] += 1
            continue
        counts["rows logged in the period"] += 1
        valid = cycle + lead * HOUR
        late = issued > valid
        if late:
            counts["rows issued after their valid time"] += 1
            late_by_lead[lead] += 1
        if valid > setup.last_valid:
            counts["rows valid after the last valid hour (not used)"] += 1
            continue
        fc.setdefault(cycle, {})[valid] = (raw, base, corr)
        issued_at[cycle] = (issued, meta)
        o = obs.get(valid)
        if o is None:
            counts["rows with no observation"] += 1
            continue
        p = s106.hourly_persistence(cycle, valid, obs)
        counts["rows scored (the common set)"] += 1
        counts["rows with a persistence value"] += p is not None
        hourly[(cycle.hour, lead)].append((label, cycle, o, raw, base, corr, p, late, meta))
    days = []
    d = (ap.start - 2 * DAY).date()
    while d <= (setup.last_cycle + 3 * DAY).date():
        s, _, hours = dailymax.local_day(d, ap.tz)
        c = dailymax.day_cycle(s)
        if not ap.start <= c <= setup.last_cycle:
            d += DAY
            continue
        if hours[-1] > setup.last_valid:
            counts["days whose last hour is after the last valid hour (not used)"] += 1
            d += DAY
            continue
        ov = [obs.get(h) for h in hours]
        obs_max = s106.observed_max(d, ap.tz, obs)
        row = {"station": ap.station, "look": label, "local_date": d, "hours": len(hours),
               "usable_hours": sum(v is not None for v in ov), "obs_max": obs_max,
               "obs_reason": "" if obs_max is not None else "too few usable hours", "cycle": c,
               "first_lead": int((hours[0] - c) / HOUR), "last_lead": int((hours[-1] - c) / HOUR),
               "obs_edge": obs_max is not None and edge_hour(peak_hour(ov), len(hours)),
               "meta": issued_at.get(c, (None, None))[1],
               "issued_after_start": c in issued_at and issued_at[c][0] > s}
        got = fc.get(c, {})
        for i, m in enumerate(METHODS):
            curve = {h: got[h][i] for h in hours if h in got}
            row[m] = dailymax.read_off(hours, curve)
            row[m + "_reason"] = "" if row[m] is not None else "no log file for the day's cycle" \
                if c not in logged else f"no forecast at {len(hours) - len(curve)} hours"
            row[m + "_edge"] = row[m] is not None and edge_hour(peak_hour([curve[h] for h in hours]), len(hours))
        row["pers_date"], row["persistence"] = s106.daily_persistence(d, c, ap.tz, obs)
        row["common"] = row["obs_max"] is not None and row["raw_gfs"] is not None and row["curve"] is not None
        row["pers_subset"] = row["common"] and row["persistence"] is not None
        row["edge_day"] = row["obs_edge"] or row["raw_gfs_edge"] or row["curve_edge"]
        counts["local days in the period"] += 1
        counts["days with no usable observed maximum"] += row["obs_max"] is None
        counts["days with no forecast maximum"] += row["curve"] is None or row["raw_gfs"] is None
        counts["days scored (the common set)"] += row["common"]
        counts["days with a persistence value"] += row["pers_subset"]
        counts["days whose cycle was issued after the day began"] += row["issued_after_start"]
        counts["scored days with a maximum in the first or last hour"] += row["common"] and row["edge_day"]
        days.append(row)
        d += DAY
    return {"name": ap.icao, "station": ap.station, "group": ap.group, "tz": ap.tz, "hourly": hourly, "days": days,
            "counts": counts, "late_by_lead": late_by_lead}


def score_cells(res, label):
    """The scores file's rows for one airport, in session 106's order (its run_look)."""
    sc = []
    lead = [res["name"], res["station"], res["group"], label]

    def add(output, m, row_set, h, n, e):
        sc.append(lead + [output, m, row_set, h, n, len(e), s106.mae_or_none(e), s97.mean_error(e) if e else None])

    for h in CYCLE_HOURS:
        for n in LEADS:
            recs = [r for r in res["hourly"][(h, n)] if r[0] == label]
            sub = [r for r in recs if r[6] is not None]
            for m in METHODS:
                add("hourly", m, "common", h, n, s106.hourly_errors(recs, HIDX[m]))
            for m in ("curve", "persistence"):
                add("hourly", m, "persistence_subset", h, n, s106.hourly_errors(sub, HIDX[m]))
    dc, dsub = s106.daily_sets(res, label)
    for m in METHODS:
        add("daily", m, "common", "", "", s106.daily_errors(dc, m))
    for m in ("curve", "persistence"):
        add("daily", m, "persistence_subset", "", "", s106.daily_errors(dsub, m))
    return sc


def bar_rows(res, label):
    """D100.5 and D105.5(c), (g) for one airport and period: per output, both halves with their
    margins (D79.1), and PASS only if both halves pass (a tie fails, D79.2)."""
    out = []
    for output in OUTPUTS:
        if output == "hourly":
            common, subset = s106.hourly_sets(res, label, LEADS, CYCLE_HOURS)
            e = {m: s106.hourly_errors(common, HIDX[m]) for m in ("raw_gfs", "curve")}
            ep = {m: s106.hourly_errors(subset, HIDX[m]) for m in ("curve", "persistence")}
        else:
            common, subset = s106.daily_sets(res, label)
            e = {m: s106.daily_errors(common, m) for m in ("raw_gfs", "curve")}
            ep = {m: s106.daily_errors(subset, m) for m in ("curve", "persistence")}
        halves = []
        for half in HALVES:
            if half == "raw_gfs":
                n, m, b = len(common), s106.mae_or_none(e["curve"]), s106.mae_or_none(e["raw_gfs"])
            else:
                n, m, b = len(subset), s106.mae_or_none(ep["curve"]), s106.mae_or_none(ep["persistence"])
            mg, df = s106.margin(m, b) if m is not None and b is not None else (None, None)
            halves.append({"icao": res["name"], "station": res["station"], "group": res["group"], "period": label,
                           "output": output, "half": half, "n": n, "curve_mae": m, "other_mae": b,
                           "margin_pct": mg, "diff_c": df, "half_pass": s106.half_pass(m, b)})
        ok = s106.look_pass(halves[0]["half_pass"], halves[1]["half_pass"])
        for h in halves:
            h["period_pass"] = ok
            h["verdict"] = "PASS" if ok else "FAIL"
        out += halves
    return out


def descriptive_rows(res, label):
    """D105.5(i): never part of the bar. Per airport: every method's MAE and mean error on the
    common set; leads 3 to 24 and 25 to 48; per cycle hour; per model manifest and code commit; and
    days with a maximum in the first or last hour of the local day, counted and scored separately."""
    out = []
    lead = [res["name"], res["station"], res["group"], label]

    def add(output, split, value, m, e):
        out.append(lead + [output, split, value, LIVE_NAME.get(m, m), len(e), s106.mae_or_none(e),
                           s97.mean_error(e) if e else None])

    def hourly(split, value, common):
        subset = [r for r in common if r[6] is not None]
        for m in METHODS:
            add("hourly", split, value, m, s106.hourly_errors(common, HIDX[m]))
        add("hourly", split, value, "persistence", s106.hourly_errors(subset, HIDX["persistence"]))

    def daily(split, value, common):
        subset = [d for d in common if d["pers_subset"]]
        for m in METHODS:
            add("daily", split, value, m, s106.daily_errors(common, m))
        add("daily", split, value, "persistence", s106.daily_errors(subset, "persistence"))

    common, _ = s106.hourly_sets(res, label, LEADS, CYCLE_HOURS)
    hourly("all", "", common)
    for band, leads in (("3-24", LEADS_A), ("25-48", LEADS_B)):
        hourly("leads", band, s106.hourly_sets(res, label, leads, CYCLE_HOURS)[0])
    for h in CYCLE_HOURS:
        hourly("cycle_hour", f"{h:02d}", s106.hourly_sets(res, label, LEADS, (h,))[0])
    for meta in sorted({r[8] for r in common}):
        hourly("model_and_code", " ".join(meta), [r for r in common if r[8] == meta])
    hourly("issued_after_valid", "true", [r for r in common if r[7]])
    hourly("issued_after_valid", "false", [r for r in common if not r[7]])
    dc, _ = s106.daily_sets(res, label)
    daily("all", "", dc)
    for h in CYCLE_HOURS:
        daily("cycle_hour", f"{h:02d}", [d for d in dc if d["cycle"].hour == h])
    for meta in sorted({d["meta"] for d in dc if d["meta"]}):
        daily("model_and_code", " ".join(meta), [d for d in dc if d["meta"] == meta])
    for name, key in (("edge_day", "edge_day"), ("obs_edge", "obs_edge"), ("raw_gfs_edge", "raw_gfs_edge"),
                      ("corrected_edge", "curve_edge")):
        for flag in (True, False):
            daily(name, cell_text(flag), [d for d in dc if d[key] is flag])
    return out


def score_setup(setup, inv, obs_by_icao, log=print):
    """Every airport of one period: (results, score rows, bar rows, descriptive rows)."""
    logged = set(inv["info"])
    results, cells, bars, desc = [], [], [], []
    for a in setup.airports:
        res = score_airport(a, inv["rows"][a.icao], obs_by_icao[a.icao], setup, logged)
        results.append(res)
        cells += score_cells(res, setup.label)
        bars += bar_rows(res, setup.label)
        desc += descriptive_rows(res, setup.label)
    return results, cells, bars, desc


SCORE_COLS = ["icao", "station", "group", "period", "output", "method", "row_set", "cycle_hour", "lead", "n", "mae",
              "mean_error"]
VERDICT_COLS = ["icao", "station", "group", "period", "output", "half", "n", "corrected_mae", "other_mae",
                "margin_pct", "diff_c", "half_pass", "verdict"]
DAY_COLS = ["icao", "station", "group", "period", "local_date", "hours", "usable_hours", "obs_max", "obs_reason",
            "cycle", "first_lead", "last_lead", "raw_gfs_max", "raw_gfs_reason", "baseline_max", "baseline_reason",
            "corrected_max", "corrected_reason", "persistence_date", "persistence_max", "common",
            "persistence_subset", "obs_edge", "raw_gfs_edge", "corrected_edge", "cycle_issued_after_day_start"]
DESC_COLS = ["icao", "station", "group", "period", "output", "split", "value", "method", "n", "mae", "mean_error"]


def day_values(res, d):
    return ([res["name"], d["station"], res["group"], d["look"], d["local_date"].isoformat(), d["hours"],
             d["usable_hours"], d["obs_max"], d["obs_reason"], stamp(d["cycle"]), d["first_lead"], d["last_lead"]]
            + [x for m in METHODS for x in (d[m], d[m + "_reason"])]
            + [d["pers_date"].isoformat(), d["persistence"], d["common"], d["pers_subset"], d["obs_edge"],
               d["raw_gfs_edge"], d["curve_edge"], d["issued_after_start"]])


def claim_lines(bars, setup):
    """D105.5(g): per output and group, "passes at N of M airports", led by the smallest margin as a
    percentage (D79.1). Nothing is averaged across airports."""
    out = []
    for output in OUTPUTS:
        for g in dict.fromkeys(a.group for a in setup.airports):
            rs = [r for r in bars if r["output"] == output and r["group"] == g]
            airports = list(dict.fromkeys(r["icao"] for r in rs))
            passed = [ic for ic in airports if all(r["period_pass"] for r in rs if r["icao"] == ic)]
            known = [r for r in rs if r["margin_pct"] is not None]
            line = f"period {setup.label}, {output}, group of {g}: "
            if known:
                s = min(known, key=lambda r: r["margin_pct"])
                line += (f"smallest margin {s['margin_pct']:+.3f} % ({s['diff_c']:+.4f} degrees C), {s['icao']} "
                         f"against {s['half']}; ")
            line += f"passes at {len(passed)} of {len(airports)} airports"
            none = [(r["icao"], r["half"]) for r in rs if r["margin_pct"] is None]
            if none:
                line += f"; halves with no rows (cannot pass): {none}"
            failed = [ic for ic in airports if ic not in passed]
            if failed:
                line += f"; FAIL: {', '.join(failed)}"
            out.append(line)
    twelve = [r for r in bars if r["group"] == "12"]
    if setup.label == "A" and twelve:
        met = len({r["icao"] for r in twelve}) == EXPECTED_12 and all(r["period_pass"] for r in twelve)
        out.append(f"expectation (D105.5(j)): both outputs pass at all 12 airports of D103.4 in period A: "
                   f"{'MET' if met else 'NOT MET'}")
    return out


def count_rows(results, label):
    out = []
    for res in results:
        for k, v in res["counts"].items():
            out.append([res["name"], res["group"], label, k, "", v])
        for lead, v in sorted(res["late_by_lead"].items()):
            out.append([res["name"], res["group"], label, "rows issued after their valid time", lead, v])
    return out


def snapshot_agreement(blobs, repo, setup, obs_by_icao):
    """D105.5(f): the obs/ snapshots against the fresh pairing. Counts only; no forecast is read.
    Called only after the score files are written."""
    blobs.allow_obs()
    names = [p for p in git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", "obs/").splitlines() if p]
    first = min(a.start for a in setup.airports)
    tally = collections.Counter()
    for p in names:
        m = re.match(r"^obs/\d{4}/\d{2}/" + MODEL + r"_(\d{10})\.csv$", p)
        c = dt.datetime.strptime(m.group(1), "%Y%m%d%H") if m else None
        if c is None or not first <= c <= setup.last_cycle:
            tally["snapshot files outside the period"] += 1
            continue
        tally["snapshot files compared"] += 1
        for r in csv.DictReader(io.StringIO(blobs.read("HEAD", p).decode())):
            look = obs_by_icao.get(r["airport"])
            valid = prediction_log.parse_time(r["valid_utc"])
            if look is None or valid > setup.last_valid:
                tally["snapshot rows not compared (airport or time outside the test)"] += 1
                continue
            fresh, when = look.report(valid)
            snap = float(r["obs_c"]) if r["obs_c"] else None
            tally["snapshot rows compared"] += 1
            tally["equal" if snap == fresh else "snapshot empty, fresh present" if snap is None else
                  "snapshot present, fresh empty" if fresh is None else "different values"] += 1
            if snap == fresh and snap is not None and when is not None:
                tally["equal value, another report time"] += r["report_utc"] != stamp(when)
    return tally


# ------------------------------------------------------------------ --inventory

def run_inventory(args):
    repo = Path(args.inventory)
    print(f"SESSION 129 --inventory (no observation is read), {stamp(now_utc())}; clone {repo}")
    setup = live_setup("so far", None)
    inv = inventory(repo, setup)
    print("\n".join(inventory_lines(inv, setup)))
    if args.detail:
        s97.write_new(Path(args.detail), "\n".join(inventory_lines(inv, setup, full=True)) + "\n")
        print(f"full table written to {args.detail}")
    return 0 if inv["passes"] else 1


# ------------------------------------------------------------------ --score (the look; not run in session 129)

def script_committed(script, repo_root):
    """The script's SHA-256, if the file is tracked by git and equal to its committed version."""
    rel = str(Path(script).resolve().relative_to(Path(repo_root).resolve()))
    tracked = subprocess.run(["git", "-C", str(repo_root), "ls-files", "--error-unmatch", "--", rel],
                             capture_output=True).returncode == 0
    if not tracked:
        raise Refusal(f"{rel} is not committed (D105.5(l), D123.2)")
    if subprocess.run(["git", "-C", str(repo_root), "diff", "--quiet", "HEAD", "--", rel]).returncode != 0:
        raise Refusal(f"{rel} differs from its committed version (D123.3)")
    return sha256_file(script)


def score_dirs(out_root, period):
    out_root = Path(out_root)
    return (out_root / "data" / "processed" / f"live_test_period_{period}",
            out_root / "data" / "raw" / "iem" / f"live_test_period_{period}")


def run_score(args, now=None, fetch=None, out_root=ROOT, script=SCRIPT, repo_root=ROOT):
    """The look. Every refusal is checked before any observation is fetched (D123.3)."""
    t0 = time.time()
    now = now or now_utc()
    fetch = fetch or observations.fetch_reports
    sha = script_committed(script, repo_root)
    first_v17 = parse_v17(args.first_v17_cycle)
    setup = live_setup(args.period, first_v17)
    ends = period_last_valid(setup)
    if not now >= ends + WAIT:
        raise Refusal(f"period {setup.label}'s last valid hour is {stamp(ends)}; the look is not run before "
                      f"{stamp(ends + WAIT)} (D105.5(f)); it is now {stamp(now)}")
    out_dir, raw_dir = score_dirs(out_root, setup.label)
    if out_dir.exists() or raw_dir.exists():
        raise Refusal(f"an output folder already exists: {out_dir} or {raw_dir}; each look is run once")
    repo = Path(args.score)
    blobs = Blobs(repo)
    try:
        inv = inventory(repo, setup, blobs)
        print(f"SESSION 129 --score, period {setup.label}, start {stamp(now_utc())}")
        print(f"script SHA-256 {sha} (equal to its committed version)")
        print(f"--first-v17-cycle {args.first_v17_cycle}; period {setup.label}: cycles to {stamp(setup.last_cycle)}, "
              f"last valid hour {stamp(ends)}")
        print("\n".join(inventory_lines(inv, setup)))
        if not inv["passes"]:
            raise Refusal("the inventory fails (D105.5(a)); no observation was fetched")
        print("\nfetching observations from IEM (fresh, D105.5(f)):")
        obs = fetch_observations(setup, raw_dir, fetch)
        results, cells, bars, desc = score_setup(setup, inv, obs)
        out_dir.mkdir(parents=True)
        files = {
            "scores.csv": s97.csv_text(SCORE_COLS, [[cell_text(LIVE_NAME.get(v, v) if i == 5 else v)
                                                     for i, v in enumerate(r)] for r in cells]),
            "verdicts.csv": s97.csv_text(VERDICT_COLS, [[cell_text(r[k]) for k in (
                "icao", "station", "group", "period", "output", "half", "n", "curve_mae", "other_mae", "margin_pct",
                "diff_c", "half_pass", "verdict")] for r in bars]),
            "days.csv": s97.csv_text(DAY_COLS, [[cell_text(v) for v in day_values(res, d)]
                                                for res in results for d in res["days"]]),
            "counts.csv": s97.csv_text(["icao", "group", "period", "count", "lead", "n"],
                                       [[cell_text(v) for v in r] for r in count_rows(results, setup.label)]),
            "descriptive.csv": s97.csv_text(DESC_COLS, [[cell_text(v) for v in r] for r in desc]),
            "inventory.txt": "\n".join(inventory_lines(inv, setup, full=True)) + "\n",
        }
        for name, text in files.items():
            s97.write_new(out_dir / name, text)
        print("\nTHE LIVE TEST (DECISIONS D105.5), RUN ONCE PER PERIOD.")
        lines = claim_lines(bars, setup)
        print("\n".join(lines))
        tally = snapshot_agreement(blobs, repo, setup, obs)
        agree = [f"{k}: {v}" for k, v in sorted(tally.items())]
        print("\nobs/ snapshots against the fresh observations (D105.5(f), after the scores were written):")
        print("\n".join("  " + a for a in agree))
        meta = [f"Session 129's scoring script, --score, period {setup.label} (DECISIONS D105.5, D123).",
                f"run: {stamp(now)} to {stamp(now_utc())}; {s106.versions()}",
                f"script SHA-256 {sha}; clone HEAD {inv['head']}; --first-v17-cycle {args.first_v17_cycle}",
                f"period {setup.label}: cycles to {stamp(setup.last_cycle)}; last valid hour {stamp(ends)}",
                "the claim:"] + ["  " + x for x in lines] + ["snapshot agreement:"] + ["  " + a for a in agree]
        meta += ["files:"] + [f"  {n} sha256 {sha256_file(out_dir / n)}" for n in files]
        s97.write_new(out_dir / "meta.txt", "\n".join(meta) + "\n")
        print(f"\nwrote {out_dir} and {raw_dir}; run time {time.time() - t0:.0f} s")
        return 0
    finally:
        blobs.close()


# ------------------------------------------------------------------ --gate (D123.4(a); spent data only)

def gate_time(text):
    t = prediction_log.parse_time(text)
    if t >= GATE_LIMIT:
        raise SystemExit(f"STOP: the gate met a time {text} at or after its limit {GATE_LIMIT}")
    return t


def read_gz(path, want):
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"STOP: {path.name} SHA-256 {got} is not the recorded {want}")
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.DictReader(f))


def build_synthetic_logs(repo, log=print):
    """Synthetic logs in MLwx-live's format (D103.8), written by the live writer itself
    (mlwx.prediction_log.write_log): one file per cycle, the six claim airports, every row of
    session 112's predictions that has a curve value (status scored or extra). Committed once to a
    new git repository at `repo`. Returns (cycles written, rows written, rows left out)."""
    by_cycle, left_out = {}, collections.Counter()
    sha = hashlib.sha256(b"session 129 synthetic models").hexdigest()
    commit = hashlib.sha1(b"session 129 synthetic code").hexdigest()
    for ic in s106.CLAIM:
        for r in read_gz(PRED_DIR / f"pred_{ic}.csv.gz", GATE_PRED[ic]):
            if r["status"] == "incomplete" or r["curve"] == "":
                left_out[r["status"]] += 1
                continue
            cycle = gate_time(r["cycle_utc"])
            by_cycle.setdefault(cycle, []).append({
                "airport": ic, "cycle": cycle, "lead": int(r["lead"]), "valid": gate_time(r["valid_utc"]),
                "raw_gfs": float(r["raw_gfs"]), "baseline": float(r["baseline"]), "b": float(r["b"]),
                "corrected": float(r["curve"]), "gfs_version": "v16", "model_sha256": sha, "code_commit": commit,
                "issued": cycle + GATE_ISSUE_AFTER})
    n_rows = 0
    for cycle in sorted(by_cycle):
        rows = by_cycle[cycle]
        if any(r["valid"] != cycle + r["lead"] * HOUR or r["valid"] >= GATE_LIMIT for r in rows):
            raise SystemExit(f"STOP: {cycle}: a prediction row's valid time is wrong or after the gate's limit")
        prediction_log.write_log(prediction_log.log_path(repo, MODEL, cycle), rows)
        n_rows += len(rows)
    git(repo, "init", "-q")
    git(repo, "add", "log")
    git(repo, "-c", "user.name=session 129 gate", "-c", "user.email=gate@example.invalid", "commit", "-q", "-m",
        "synthetic logs (session 129 gate)")
    digest = hashlib.sha256()
    for p in sorted(Path(repo, "log").rglob("*.csv")):
        digest.update(f"{p.relative_to(repo)} {sha256_file(p)}\n".encode())
    log(f"synthetic logs: {len(by_cycle)} cycle files, {n_rows} rows; rows left out (no curve value): "
        f"{dict(left_out) or 'none'}; SHA-256 over the list of file names and hashes: {digest.hexdigest()}")
    return len(by_cycle), n_rows, left_out


def gate_setup(look, t0, t1):
    aps = [Ap(ic, st, tz, "claim", t0) for ic, (st, tz) in s106.CLAIM.items()]
    return Setup(look, aps, t1 - STEP, GATE_LAST_VALID, {})


def compare_csv(name, recorded_text, mine_text, key_cols, skip=()):
    """Cell by cell, as text (both sides write floats with repr, so equal text is equal at full
    precision). Returns (cells compared, cells equal, differences, recorded rows, recomputed rows)."""
    rec = list(csv.DictReader(io.StringIO(recorded_text)))
    got = list(csv.DictReader(io.StringIO(mine_text)))
    cols = [c for c in rec[0] if c not in skip]
    index = {tuple(r[k] for k in key_cols): r for r in got}
    compared, equal, diffs = 0, 0, []
    for r in rec:
        key = tuple(r[k] for k in key_cols)
        g = index.pop(key, None)
        for c in cols:
            compared += 1
            if g is not None and g.get(c) == r[c]:
                equal += 1
            else:
                diffs.append((name, key, c, r[c], None if g is None else g.get(c)))
    diffs += [(name, k, "(row not in the record)", "", "") for k in index]
    return compared, equal, diffs, len(rec), len(got)


def run_gate(args):
    t_start = time.time()
    print(f"SESSION 129 --gate (D123.4(a); spent data and synthetic logs only), start {stamp(now_utc())}; "
          f"{s106.versions()}")
    print("SPENT YEARS (stage C's two looks, F150). Not a new result.")
    s106.check_claim_zones()
    recorded = {}
    for name, want in (("scores", S107_SCORES_SHA256), ("days", S107_DAYS_SHA256),
                       ("verdicts", S107_VERDICTS_SHA256)):
        p = s106.PROCESSED / f"session107_claim_{name}.csv"
        if sha256_file(p) != want:
            raise SystemExit(f"STOP: {p.name}'s SHA-256 is not F150.4's")
        recorded[name] = p.read_text()
    if GATE_DIR.exists() and any(GATE_DIR.iterdir()):
        raise Refusal(f"{GATE_DIR} already holds files; the gate does not overwrite them")
    tmp = Path(tempfile.mkdtemp(prefix="session129_gate_"))
    if ROOT in tmp.resolve().parents:
        raise SystemExit("STOP: the temporary folder is inside the repo")
    print(f"temporary folder (outside the repo, deleted at the end): {tmp}")
    try:
        repo = tmp / "synthetic-live"
        repo.mkdir()
        build_synthetic_logs(repo)
        obs = {}
        for ic in s106.CLAIM:
            rows = read_gz(PRED_DIR / f"obs_{ic}.csv.gz", GATE_OBS[ic])
            obs[ic] = TableObs({gate_time(r["valid_utc"]): s97.fval(r["obs"]) for r in rows}, GATE_LIMIT)
        per = {}
        blobs = Blobs(repo)
        try:
            for look, t0, t1 in s106.LOOKS:
                setup = gate_setup(look, t0, t1)
                inv = inventory(repo, setup, blobs)
                print(f"\nlook {look} as a period: cycles {stamp(t0)} to {stamp(setup.last_cycle)}")
                print("\n".join("  " + x for x in inventory_lines(inv, setup)))
                if not inv["passes"]:
                    raise SystemExit("STOP: the inventory of the synthetic logs fails")
                per[look] = score_setup(setup, inv, obs)
                print("\n".join("  " + x for x in claim_lines(per[look][2], setup)))
            opened = dict(blobs.opened)
        finally:
            blobs.close()
        # session 107's layouts, from the same rows --score writes
        looks = [l for l, _, _ in s106.LOOKS]
        sc, days, vr = [], [], []
        for i, ic in enumerate(s106.CLAIM):
            for look in looks:
                results, cells, bars, _ = per[look]
                sc += [[r[0], r[1], r[3]] + r[4:] for r in cells if r[0] == ic]
                days += [day_values(results[i], d)[:2] + day_values(results[i], d)[3:22] for d in results[i]["days"]]
            for output in OUTPUTS:
                ok = {look: next(r["period_pass"] for r in per[look][2] if r["icao"] == ic and r["output"] == output)
                      for look in looks}
                for look in looks:
                    for r in per[look][2]:
                        if r["icao"] == ic and r["output"] == output:
                            vr.append([r["icao"], r["station"], r["output"], look, r["half"], r["n"], r["curve_mae"],
                                       r["other_mae"], r["margin_pct"], r["diff_c"], r["half_pass"], ok[look],
                                       s106.verdict(ok["A"], ok["B"])])
        texts = {
            "scores": s97.csv_text(recorded["scores"].split("\n", 1)[0].split(","),
                                   [[cell_text(v) for v in r] for r in sc]),
            "verdicts": s97.csv_text(recorded["verdicts"].split("\n", 1)[0].split(","),
                                     [[cell_text(v) for v in r] for r in vr]),
            "days": s97.csv_text(recorded["days"].split("\n", 1)[0].split(","),
                                 [[cell_text(v) for v in r] for r in days]),
        }
        keys = {"scores": ["icao", "look", "output", "method", "row_set", "cycle_hour", "lead"],
                "verdicts": ["icao", "output", "look", "half"], "days": ["icao", "local_date"]}
        skip = {"days": ("raw_gfs_reason", "baseline_reason", "curve_reason")}
        lines = ["Session 129 gate (a) (D123.4(a)): the live scoring script on synthetic logs built from session "
                 "112's claim predictions,", "against session 107's files (F150.4). Cell by cell, as text at full "
                 "precision.", f"run {stamp(now_utc())}; script SHA-256 {sha256_file(SCRIPT)}; {s106.versions()}", ""]
        all_diffs, required_ok = [], True
        for name in ("scores", "verdicts", "days"):
            compared, equal, diffs, n_rec, n_got = compare_csv(name, recorded[name], texts[name], keys[name],
                                                               skip.get(name, ()))
            same_bytes = texts[name] == recorded[name]
            lines.append(f"{name}: recorded rows {n_rec}, recomputed rows {n_got}; cells compared {compared}, equal "
                         f"{equal}, different {len(diffs)}; whole file byte-equal: {same_bytes}"
                         + ("" if name != "days" else " (extra check, not part of D123.4(a); the three forecast "
                            "reason columns are not compared: their wording differs by design)"))
            all_diffs += diffs
            if name != "days" and (diffs or n_rec != n_got):
                required_ok = False
        lines.append("")
        lines += [f"DIFFERENT: {d[0]} {d[1]} column {d[2]}: recorded {d[3]!r}, recomputed {d[4]!r}"
                  for d in all_diffs[:200]]
        days_ok = not [d for d in all_diffs if d[0] == "days"]
        lines.append(f"GATE (a): {'PASS' if required_ok else 'FAIL'} (scores and verdicts); days extra check: "
                     f"{'PASS' if days_ok else 'DIFFERENCES'}")
        GATE_DIR.mkdir(parents=True, exist_ok=True)
        s97.write_new(GATE_DIR / "claim_scores_recomputed.csv", texts["scores"])
        s97.write_new(GATE_DIR / "claim_verdicts_recomputed.csv", texts["verdicts"])
        s97.write_new(GATE_DIR / "comparison.txt", "\n".join(lines) + "\n")
        print()
        print("\n".join(l for l in lines[4:] if not l.startswith("DIFFERENT")))
        for d in all_diffs[:10]:
            print(f"  DIFFERENT: {d[0]} {d[1]} column {d[2]}: recorded {d[3]!r}, recomputed {d[4]!r}")
        print(f"files read from the synthetic clone: {opened}")
        for n in ("claim_scores_recomputed.csv", "claim_verdicts_recomputed.csv", "comparison.txt"):
            print(f"wrote {(GATE_DIR / n).relative_to(ROOT)}: SHA-256 {sha256_file(GATE_DIR / n)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"temporary folder deleted: {not tmp.exists()}; run time {time.time() - t_start:.0f} s")
    return 0 if required_ok else 1


# ------------------------------------------------------------------ entry point

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--inventory", metavar="LIVE_CLONE", help="a clone of MLwx-live; no observation is read")
    g.add_argument("--gate", action="store_true", help="D123.4(a), on spent data and synthetic logs")
    g.add_argument("--score", metavar="LIVE_CLONE", help="the look (D105.5(l)); needs --period and --first-v17-cycle")
    ap.add_argument("--period", choices=("A", "B"), help="--score: the period judged")
    ap.add_argument("--first-v17-cycle", help="--score: YYYYMMDDHH from a DECISIONS entry (D103.10), or none")
    ap.add_argument("--detail", help="--inventory: also write the full table to this new file")
    a = ap.parse_args(argv)
    try:
        if a.inventory:
            return run_inventory(a)
        if a.gate:
            return run_gate(a)
        if a.period is None or a.first_v17_cycle is None:
            raise Refusal("--score needs --period and --first-v17-cycle")
        return run_score(a)
    except Refusal as e:
        print(f"REFUSED: {e}")
        return 2
    except GitError as e:
        print(f"STOP: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
