"""The runner (DECISIONS D103.7, D103.8, D103.9).

Processes every cycle of the past 24 hours that has arrived and is not yet in the log, in time
order. For each cycle:

  1. fetch the GFS values (gfs.fetch_cycle) and build the features (features.build_row) for the
     airports and leads 3 to 48; any fetch error, guard failure or missing field means the cycle
     issues nothing;
  2. bring each drift tracker up to the cycle: the baseline's errors from earlier log rows whose
     observation has arrived and is valid before the cycle starts, in ascending valid time, each
     once (tracker.advance); observations are IEM routine reports, the nearest within 15 minutes
     of the valid hour (observations.py);
  3. predict the baseline with the frozen models, add b, and write the log file (written once);
  4. save the tracker state.

A cycle is only issued if it is newer than every cycle already in the log, so a tracker never
holds an error from after a forecast it helped to make. A cycle that cannot be issued is recorded
in the state file with the reason, and the page says so. A network or file-not-there-yet problem
is tried again at the next run, and later cycles wait, until the cycle is 12 hours old; a guard
failure is final for that cycle and later cycles go on. Errors older than 7 days in the log are not
used (a gap that long is skipped, like a missing observation).
"""

import argparse
import copy
import datetime as dt
import subprocess
import sys
from pathlib import Path

from . import baseline, config, dailymax, features, gfs, observations, page, prediction_log, tracker
from . import state as state_mod

AVAILABLE_AFTER = dt.timedelta(hours=4, minutes=10)    # D103.9: a run is used about cycle + 4 h 10 min
CATCH_UP = dt.timedelta(hours=24)                      # D103.9: any cycle of the past 24 hours missing from the log
GIVE_UP_AFTER = dt.timedelta(hours=12)                 # a fetch problem older than this is final for the cycle
LOOKBACK = dt.timedelta(days=7)
HOUR = dt.timedelta(hours=1)


def utc_now():
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None, second=0, microsecond=0)


def available_cycles(model, now, catch_up=CATCH_UP):
    """The cycles that started in the past `catch_up` and have arrived by `now`, in time order."""
    out = []
    t = (now - catch_up).replace(minute=0, second=0, microsecond=0)
    while t <= now:
        if t.hour in model.cycle_hours and t >= now - catch_up and t + AVAILABLE_AFTER <= now:
            out.append(t)
        t += HOUR
    return out


def code_commit():
    """The repo's HEAD commit, with '-dirty' if the working tree has changes."""
    here = Path(__file__).resolve().parent
    try:
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=here, capture_output=True, text=True, check=True).stdout.strip()
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=here, capture_output=True, text=True, check=True).stdout.strip()
        return head + ("-dirty" if dirty else "")
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


class Issued:
    def __init__(self, cycle, path, rows, applied, obs_requests):
        self.cycle, self.path, self.rows, self.applied, self.obs_requests = cycle, path, rows, applied, obs_requests


def pending_baselines(root, model_name, cycle, lookback=LOOKBACK):
    """The baseline rows of earlier logs at the same cycle hour: {(icao, lead): [(valid, baseline)]} with
    valid before the cycle."""
    out = {}
    for c, path in sorted(prediction_log.logged_cycles(root, model_name).items()):
        if c >= cycle or c < cycle - lookback or c.hour != cycle.hour:
            continue
        for r in prediction_log.read_log(path):
            if r["valid"] < cycle:
                out.setdefault((r["airport"], r["lead"]), []).append((r["valid"], r["baseline"]))
    return out


def bring_trackers_up(root, model, airports, state, cycle, fetch_obs, stats):
    """Apply the arrived errors to every cell of this cycle hour, up to the cycle. Returns the number applied."""
    pend = pending_baselines(root, model.name, cycle)
    applied = 0
    by_airport = {}
    for (icao, lead), rows in pend.items():
        cell = state.cell(icao, cycle.hour, lead)
        rows = [(v, b) for v, b in rows if cell.last_valid is None or v > cell.last_valid]
        if rows:
            by_airport.setdefault(icao, {})[lead] = rows
    for a in airports:
        leads = by_airport.get(a.icao)
        if not leads:
            continue
        valids = [v for rows in leads.values() for v, _ in rows]
        first_day = (min(valids) - dt.timedelta(days=1)).date()
        last_day = cycle.date()
        text = fetch_obs(a.station, first_day, last_day)
        stats["obs_requests"] += 1
        reports = observations.ReportSet.from_text(text, a.station, live=True)   # owner's ruling at the Step 6 stop
        for lead, rows in leads.items():
            errors = []
            for v, b in rows:
                o, _ = reports.nearest(v)
                if o is not None:
                    errors.append((v, o - b))
            applied += tracker.advance(state.cell(a.icao, cycle.hour, lead), errors, cycle)
    return applied


def build_cycle_rows(model, airports, cycle, cv):
    """{icao: {lead: (x, temp)}} for leads 3 to 48 from the fetched cycle. Raises GuardStop if any
    feature is empty (a missing field): the cycle then issues nothing."""
    in_plan = set(range(model.first_lead, model.last_lead + 1))
    out = {}
    for a in airports:
        val = features.airport_values(a, cv.airport_view(a.icao), cv.status)
        per = {}
        for n in range(model.curve_first_lead, model.last_lead + 1):
            row, reason, _ = features.build_row(a, cycle, n, in_plan, val, cv.status)
            x = features.feature_vector(row)
            if x is None:
                raise gfs.GuardStop(f"{a.icao} lead {n}: features empty ({', '.join(sorted(set(reason.values())))})")
            per[n] = (x, row["temperature_grib_c"])
        out[a.icao] = per
    return out


def issue_cycle(root, model, airports, models, state, cycle, now, commit, fetch_gfs, fetch_obs):
    """Issue one cycle: write its log file and advance `state` in place. Raises gfs.GuardStop,
    gfs.FetchError or observations.ObsFetchError, leaving `state` as the caller passed it only if the
    caller passed a copy (run() does)."""
    cv = fetch_gfs(model, airports, cycle)
    per = build_cycle_rows(model, airports, cycle, cv)
    stats = {"obs_requests": 0}
    applied = bring_trackers_up(root, model, airports, state, cycle, fetch_obs, stats)
    version = model.version_of(cycle)
    rows = []
    for a in airports:
        for n in range(model.curve_first_lead, model.last_lead + 1):
            x, temp = per[a.icao][n]
            base = models.baseline(a.icao, cycle.hour, n, x, temp)
            b = state.cell(a.icao, cycle.hour, n).b
            rows.append({"airport": a.icao, "cycle": cycle, "lead": n, "valid": cycle + n * HOUR, "raw_gfs": temp,
                         "baseline": base, "b": b, "corrected": base + b, "gfs_version": version,
                         "model_sha256": models.manifest_sha, "code_commit": commit, "issued": now})
    path = prediction_log.log_path(root, model.name, cycle)
    prediction_log.write_log(path, rows)
    state.last_cycle = cycle
    return Issued(cycle, path, rows, applied, stats["obs_requests"])


def run(root, models_dir, now=None, model_name="gfs", latest_only=False, commit=None, fetch_gfs=None,
        fetch_obs=None, write_page=True, log=print, models=None):
    """One run. Returns a dict: issued (cycles), stopped ([(cycle, reason)]), waiting ((cycle, why) or None),
    skipped (cycles already done). `models` replaces the folder of frozen models (tests only)."""
    now = now or utc_now()
    model = config.get_model(model_name)
    airports = config.load_airports(model)
    fetch_gfs = fetch_gfs or (lambda m, a, c: gfs.fetch_cycle(m, a, c))
    fetch_obs = fetch_obs or (lambda st, d1, d2: observations.fetch_reports(st, d1, d2))
    commit = commit or code_commit()
    models = models or baseline.ModelSet(models_dir, model_name)
    state = state_mod.load_state(root, model_name)
    result = {"issued": [], "stopped": [], "waiting": None, "skipped": []}

    cycles = available_cycles(model, now)
    if latest_only and cycles:
        cycles = cycles[-1:]
    for cycle in cycles:
        logged = prediction_log.logged_cycles(root, model_name)
        if cycle in logged or cycle in state.stopped():
            result["skipped"].append(cycle)
            continue
        if logged and cycle < max(logged):
            reason = "not issued: a later cycle is already in the log (tracker order)"
            state.add_stop(cycle, reason, now)
            result["stopped"].append((cycle, reason))
            log(f"{cycle:%Y-%m-%dT%H}z: {reason}")
            continue
        work = copy.deepcopy(state)
        try:
            issued = issue_cycle(root, model, airports, models, work, cycle, now, commit, fetch_gfs, fetch_obs)
        except gfs.GuardStop as e:
            reason = f"guard stop: {e}"
            state.add_stop(cycle, reason, now)
            result["stopped"].append((cycle, reason))
            log(f"{cycle:%Y-%m-%dT%H}z: ISSUED NOTHING. {reason}")
            continue
        except (gfs.FetchError, observations.ObsFetchError) as e:
            if now - cycle >= GIVE_UP_AFTER:
                reason = f"fetch problem, gave up after 12 hours: {e}"
                state.add_stop(cycle, reason, now)
                result["stopped"].append((cycle, reason))
                log(f"{cycle:%Y-%m-%dT%H}z: ISSUED NOTHING. {reason}")
                continue
            result["waiting"] = (cycle, str(e))
            log(f"{cycle:%Y-%m-%dT%H}z: issued nothing yet, will try again: {e}")
            break
        state = work
        state_mod.save_state(root, state)
        result["issued"].append(cycle)
        log(f"{cycle:%Y-%m-%dT%H}z: issued {len(issued.rows)} rows to {issued.path}; errors applied "
            f"{issued.applied}; IEM requests {issued.obs_requests}")
    state.last_run = {"at": state_mod.iso(now), "status": ("waiting" if result["waiting"] else
                                                          "stopped" if result["stopped"] else "ok")}
    state_mod.save_state(root, state)
    if write_page:
        page.write_page(root, model, airports, state, now)
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description="Issue every GFS cycle of the past 24 hours that is not yet logged.")
    ap.add_argument("--root", required=True, help="folder holding log/, state/ and site/")
    ap.add_argument("--models", required=True, help="folder with the product models and their manifest")
    ap.add_argument("--model", default="gfs")
    ap.add_argument("--now", help="UTC time YYYY-MM-DDTHH:MM (default: the clock)")
    ap.add_argument("--latest-only", action="store_true", help="only the latest available cycle (the dry run)")
    ap.add_argument("--commit", help="the code commit to write in the log (default: git HEAD of this package)")
    a = ap.parse_args(argv)
    now = dt.datetime.strptime(a.now, "%Y-%m-%dT%H:%M") if a.now else utc_now()
    res = run(Path(a.root), Path(a.models), now, a.model, a.latest_only, a.commit)
    print(f"issued {len(res['issued'])}, stopped {len(res['stopped'])}, waiting {res['waiting'] is not None}, "
          f"already done {len(res['skipped'])}")
    if res["stopped"]:
        return 3
    if res["waiting"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
