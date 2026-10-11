"""Session 105: two daily-maximum challengers (DECISIONS D99). Offline.
Build-choice scores only, never results (SPEC 2.5).

Challenger 1 (D99.3): a daily-maximum model of its own. For the local day D
and its cycle c (D98.10(b)), with H the day's whole UTC hours (leads 4 to 33
of c): raw_max is the highest temperature_grib_c over H; the peak hour p is
the hour with that value (the earliest on a tie); gfs_tmax is the highest
tmax2m_c over H. Features, in this order: raw_max, gfs_tmax, then the other
eight G15 columns at p. Target: observed maximum minus raw_max; forecast:
raw_max plus the model's output. One model per airport and fold, the record's
settings, training days whose last hour is valid before the fold's T0.
Test 1 (D99.4): D89.6 against the curve's read-off maximum; M is the winner.

Challenger 2 (D99.5): M plus b, b a decaying average (w = 0.02) of M's own
daily-maximum errors, one tracker per airport and fold, starting at 0 at T0,
using only errors of days whose last hour is valid before the forecast's
cycle. Test 2 (D99.6): D89.6 against M.

Modes (one per run):
  --gate   the reproduction (D99.8): 1. from the days file alone, F147.6's
           MAEs, headlines, fold levels and day counts at 4 decimals (owner
           ruling at session 105's stop, recorded in F148); 2. the day list
           rebuilt from the tables' observations equals the file's; 3. raw_max
           equals the file's raw_gfs_max. Writes nothing.
  --score  the gate again, then challenger 1 and test 1, challenger 2 and
           test 2. Writes data/processed/session105_dailymax_cv_days.csv.
  --meta   writes data/processed/session105_dailymax_cv.meta.txt.

Imported read only, after its SHA-256 check: scripts/session104_curve_cv.py
(F147), which checks its own imports. Used from session 104: day_cycle,
local_day, usable_day, fold_of, TZ, DAY_LAST_VALID, table25_hashes,
load_table25, TABLE25, sha256_file, now_utc, versions; through it, from
session 97: load_table, fit_predict, mae, mean_error, csv_text, fmt,
write_new, parse_time, check_valid, fval, STATIONS, TABLES, STAGEC_DIR,
FOLDS, LGB_PARAMS, G15; from session 100: print_test. tmax2m_c is not in
those loaders' output: read_tmax reads it from the same files, after the same
SHA-256 check, keyed by (cycle, lead). This script never imports or calls the
session-48 guard itself (D90.1); lightgbm is imported directly (D93.3).

Output files are written once and never overwritten (SPEC 8.7 item 5).
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

S104_SCRIPT = HERE / "session104_curve_cv.py"
S104_SCRIPT_SHA256 = "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb"   # F147


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256_file(S104_SCRIPT) != S104_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session104_curve_cv.py's SHA-256 is not F147's")
sys.path.insert(0, str(HERE))
import session104_curve_cv as s104  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

s97 = s104.s97
s100 = s104.s100

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
S104_DAYS = PROCESSED / "session104_dailymax_days.csv"
S104_DAYS_SHA256 = "65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3"   # F147.7
DAYS_OUT = PROCESSED / "session105_dailymax_cv_days.csv"
META_OUT = PROCESSED / "session105_dailymax_cv.meta.txt"
SCRIPT = Path(__file__).resolve()

STATIONS = s97.STATIONS
FOLDS = s97.FOLDS
LGB_PARAMS = s97.LGB_PARAMS
G15 = s97.G15
FEATURES = ["raw_max", "gfs_tmax"] + G15[1:]   # D99.3(b): ten features, in this order
W = 0.02                                       # D99.5: D97.4's value, not tuned
S104_METHODS = ("raw_gfs", "baseline", "curve")
FIRST_VALID = dt.datetime(2021, 3, 24, 0, 0)  # the pull window's first valid hour (D82.4)

# F147.6, at 4 decimals (owner ruling at session 105's Step 2 stop).
F147_6_MAE = {   # airport: (raw GFS, baseline, curve)
    "EGLC": ("0.9460", "0.8479", "0.8410"), "LFPG": ("1.1968", "0.9780", "0.9558"),
    "DSM": ("1.7297", "1.2543", "1.2240"), "YSDU": ("1.0861", "1.0475", "1.0268"),
    "RNO": ("1.5511", "0.9490", "0.9477"), "SFO": ("1.6635", "1.2489", "1.2076"),
}
F147_6_HEADLINE = ("1.3622", "1.0543", "1.0338")
F147_6_FOLD = {"2023-24": ("1.4509", "1.0508", "1.0212"), "2024-25": ("1.3405", "1.0857", "1.0630"),
               "2025-26": ("1.2947", "1.0260", "1.0171")}
F147_6_DAYS = {"EGLC": 1095, "LFPG": 1094, "DSM": 1095, "YSDU": 1085, "RNO": 1093, "SFO": 1093}


# ------------------------------------------------------------------ inputs

def read_s104_days():
    """Session 104's days file (SHA-256 checked), as dicts in file order."""
    got = sha256_file(S104_DAYS)
    if got != S104_DAYS_SHA256:
        raise SystemExit(f"STOP: {S104_DAYS.name} SHA-256 {got} is not F147.7's")
    with open(S104_DAYS, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for k in ("obs_max", "raw_gfs_max", "baseline_max", "curve_max"):
            r[k] = s97.fval(r[k])
        r["common"] = r["common"] == "true"
        r["cycle"] = s97.parse_time(r["cycle"])
    return rows


def read_tmax(path, want):
    """tmax2m_c from one table file, keyed by (cycle, lead), after the file's
    SHA-256 check (the same check as load_table and load_table25). Every valid
    time passes the 2026-27 guard."""
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"STOP: {path.name} SHA-256 {got} is not the recorded {want}")
    out = {}
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != s97.TABLE_COLUMNS:
            raise SystemExit(f"STOP: {path.name} header is not F138.4's")
        ix = {c: i for i, c in enumerate(head)}
        for r in rd:
            s97.check_valid(s97.parse_time(r[ix["valid_utc"]]))
            out[(s97.parse_time(r[ix["cycle_utc"]]), int(r[ix["lead"]]))] = s97.fval(r[ix["tmax2m_c"]])
    return out


def load_airport(st, hashes):
    """Both tables at one airport: the observation at every valid hour, and per
    (cycle, lead) the G15 values x and tmax2m_c."""
    rows = s97.load_table(st, leads=tuple(range(0, 25))) + s104.load_table25(st, hashes[st])
    obs_map, x_map, bad = {}, {}, 0
    for cycle, valid, h, n, complete, obs, temp, x in rows:
        if valid in obs_map and obs_map[valid] != obs:
            bad += 1
        obs_map[valid] = obs
        x_map[(cycle, n)] = x
    if bad:
        raise SystemExit(f"STOP: {st}: {bad} rows give a different observation for the same valid time")
    name_a, want_a = s97.TABLES[st]
    tmax = read_tmax(s97.STAGEC_DIR / name_a, want_a)
    tmax.update(read_tmax(s97.STAGEC_DIR / s104.TABLE25[st], hashes[st]))
    if set(tmax) != set(x_map):
        raise SystemExit(f"STOP: {st}: the tmax2m_c keys differ from the tables' rows")
    return obs_map, x_map, tmax


# ------------------------------------------------------------------ days and inputs

def peak(temps):
    """D99.3(b): the index of the highest value; on a tie, the earliest. Also
    whether a tie was broken."""
    top = max(temps)
    i = temps.index(top)
    return i, temps.count(top) > 1


def day_inputs(c, hours, x_map, tmax):
    """D99.3(b) and (d) for one day: (features, raw_max, gfs_tmax, peak lead,
    tie, reason). features is None, with a reason, if the day has no inputs."""
    leads = [int((h - c) / dt.timedelta(hours=1)) for h in hours]
    xs = [x_map.get((c, n)) for n in leads]
    temps = [None if x is None else x[0] for x in xs]
    tmaxs = [tmax.get((c, n)) for n in leads]
    raw_max = None if any(v is None for v in temps) else max(temps)
    gfs_tmax = None if any(v is None for v in tmaxs) else max(tmaxs)
    if raw_max is None:
        return None, None, gfs_tmax, None, False, "temperature_grib_c missing at some hour"
    i, tie = peak(temps)
    if gfs_tmax is None:
        return None, raw_max, None, leads[i], tie, "tmax2m_c missing at some hour"
    rest = xs[i][1:]
    if any(v is None for v in rest):
        return None, raw_max, gfs_tmax, leads[i], tie, "a G15 column missing at the peak hour"
    return [raw_max, gfs_tmax] + list(rest), raw_max, gfs_tmax, leads[i], tie, ""


def training_day(last_hour, t0):
    """D99.3(e), D89.3: a day may train a fold's model only if its last hour is
    valid before the fold's T0."""
    return last_hour < t0


def all_days(st, obs_map, x_map, tmax):
    """Every local day whose hours lie in the pull window (first hour on or
    after 2021-03-24T00:00, last on or before 2026-07-31T23:00), with its cycle
    (D98.10(b)), fold (D98.10(d)), observed maximum (D98.10(a)) and challenger
    1's inputs. Ascending local date."""
    tzname = s104.TZ[st]
    out = []
    d = FIRST_VALID.date() - dt.timedelta(days=1)
    while True:
        s, e, hours = s104.local_day(d, tzname)
        if hours[-1] > s104.DAY_LAST_VALID:
            break
        if s < FIRST_VALID:
            d += dt.timedelta(days=1)
            continue
        c = s104.day_cycle(s)
        if any(h not in obs_map for h in hours):
            raise SystemExit(f"STOP: {st} {d}: an hour is not in the tables")
        vals = [obs_map[h] for h in hours]
        usable = [v for v in vals if v is not None]
        obs_max = max(usable) if s104.usable_day(len(hours), len(usable)) else None
        feats, raw_max, gfs_tmax, p_lead, tie, why = day_inputs(c, hours, x_map, tmax)
        out.append({"station": st, "local_date": d, "cycle": c, "fold": s104.fold_of(c), "last_hour": hours[-1],
                    "obs_max": obs_max, "x": feats, "raw_max": raw_max, "gfs_tmax": gfs_tmax, "peak_lead": p_lead,
                    "tie": tie, "why": why})
        d += dt.timedelta(days=1)
    return out


# ------------------------------------------------------------------ the gate (D99.8)

def gate1(s104_days):
    """From the days file alone, F147.6 at 4 decimals."""
    compared, bad = 0, []

    def mae_of(st, m, label=None):
        e = [r["obs_max"] - r[m + "_max"] for r in s104_days if r["station"] == st and r["common"]
             and (label is None or r["fold"] == label)]
        return s97.mae(e), len(e)

    def check(name, got, want):
        nonlocal compared
        compared += 1
        if got != want:
            bad.append(f"{name}: {got} against {want}")

    heads = {}
    for i, m in enumerate(S104_METHODS):
        for st in STATIONS:
            check(f"{st} {m}", f"{mae_of(st, m)[0]:.4f}", F147_6_MAE[st][i])
        heads[m] = sum(mae_of(st, m)[0] for st in STATIONS) / 6
        check(f"headline {m}", f"{heads[m]:.4f}", F147_6_HEADLINE[i])
        for label, _, _ in FOLDS:
            fl = sum(mae_of(st, m, label)[0] for st in STATIONS) / 6
            check(f"fold {label} {m}", f"{fl:.4f}", F147_6_FOLD[label][i])
    for st in STATIONS:
        check(f"{st} days", mae_of(st, "curve")[1], F147_6_DAYS[st])
    print(f"  gate 1 (F147.6 at 4 decimals): {compared} values compared, mismatches {len(bad)}")
    for b in bad:
        print(f"    MISMATCH {b}")
    print("  headlines at full precision (for F148): " + ", ".join(f"{m} {heads[m]!r}" for m in S104_METHODS))
    return not bad


def gate23(s104_days, days):
    """2. the day list; 3. raw_max against raw_gfs_max."""
    mine = [r for st in STATIONS for r in days[st] if r["fold"] is not None]
    if [(r["station"], r["local_date"].isoformat()) for r in mine] != [(r["station"], r["local_date"])
                                                                        for r in s104_days]:
        print(f"  gate 2: day keys differ ({len(mine)} rebuilt against {len(s104_days)} in the file)")
        return False
    bad2, n3, bad3 = 0, 0, 0
    for a, b in zip(mine, s104_days):
        if (a["cycle"], a["fold"], a["obs_max"]) != (b["cycle"], b["fold"], b["obs_max"]):
            bad2 += 1
        if a["raw_max"] is not None and b["raw_gfs_max"] is not None:
            n3 += 1
            bad3 += a["raw_max"] != b["raw_gfs_max"]
        elif (a["raw_max"] is None) != (b["raw_gfs_max"] is None):
            print(f"  note: {a['station']} {a['local_date']} raw_max {a['raw_max']} against file "
                  f"{b['raw_gfs_max']}")
    print(f"  gate 2 (station, local date, cycle, fold, observed maximum): {len(mine)} days compared, "
          f"mismatches {bad2}")
    print(f"  gate 3 (raw_max = raw_gfs_max, exact): {n3} days compared, mismatches {bad3}")
    return bad2 == 0 and bad3 == 0


def run_gate_all():
    print("GATE (D99.8, with the owner ruling at session 105's stop)")
    s104_days = read_s104_days()
    print(f"  {S104_DAYS.relative_to(ROOT)}: {len(s104_days)} rows, SHA-256 equal to F147.7")
    if not gate1(s104_days):
        raise SystemExit("STOP: gate 1 failed")
    hashes = s104.table25_hashes()
    days, data = {}, {}
    for st in STATIONS:
        t = time.time()
        obs_map, x_map, tmax = load_airport(st, hashes)
        days[st] = all_days(st, obs_map, x_map, tmax)
        print(f"  {st}: tables loaded, {len(days[st])} local days in the window, {time.time() - t:.1f} s", flush=True)
    if not gate23(s104_days, days):
        raise SystemExit("STOP: gate 2 or 3 failed")
    print("GATE PASSED")
    return s104_days, days, hashes


# ------------------------------------------------------------------ the tracker (D99.5)

def daily_track(days, w=W):
    """One airport and fold. days: (cycle, last hour valid, observed maximum or
    None, M's forecast or None), in ascending local date. Before the day whose
    cycle is c is corrected, every error not yet applied from a day whose last
    hour is valid before c is applied, in ascending last-hour order; then the
    day's own error (observed maximum minus M's forecast) is queued if both
    exist. Returns per day (b, M plus b or None, errors used, latest last hour
    used or None), and b after every error is applied."""
    b, used, latest = 0.0, 0, None
    pending, out = [], []
    prev = None
    for c, last, obs, fc in days:
        if prev is not None and not prev < c:
            raise SystemExit("STOP: tracker days are not in ascending cycle time")
        prev = c
        while pending and pending[0][0] < c:
            v, e = pending.pop(0)
            b = (1 - w) * b + w * e
            used += 1
            latest = v
        out.append((b, None if fc is None else fc + b, used, latest))
        if obs is not None and fc is not None:
            pending.append((last, obs - fc))
            pending.sort()
    for _, e in pending:
        b = (1 - w) * b + w * e
    return out, b


# ------------------------------------------------------------------ scoring helpers

def dmae(rows, m, st=None, label=None):
    e = [r["obs_max"] - r[m] for r in rows if (st is None or r["station"] == st)
         and (label is None or r["fold"] == label)]
    return s97.mae(e), len(e), s97.mean_error(e)


def headline(rows, m, label=None):
    return sum(dmae(rows, m, st, label)[0] for st in STATIONS) / 6


def d89_6(rows, inc, ch):
    hi, hc = headline(rows, inc), headline(rows, ch)
    red = (hi - hc) / hi
    airports = sum(dmae(rows, ch, st)[0] < dmae(rows, inc, st)[0] for st in STATIONS)
    folds = sum(headline(rows, ch, label) < headline(rows, inc, label) for label, _, _ in FOLDS)
    parts = (red > 0.01, airports >= 4, folds >= 2)
    return {"red": red, "airports": airports, "folds": folds, "parts": parts, "pass": all(parts)}


def print_table(rows, methods, title):
    print(f"\n{title}")
    print(f"  {'airport':<7} {'days':>5} " + " ".join(f"{m:>10}" for m in methods))
    for st in STATIONS:
        print(f"  {st:<7} {dmae(rows, methods[0], st)[1]:>5} "
              + " ".join(f"{dmae(rows, m, st)[0]:>10.4f}" for m in methods))
    print(f"  {'HEADLINE':<13} " + " ".join(f"{headline(rows, m):>10.4f}" for m in methods))
    print("  full precision: " + ", ".join(f"{m} {headline(rows, m)!r}" for m in methods))
    print("  fold level:")
    for label, _, _ in FOLDS:
        print(f"    {label}: " + ", ".join(f"{m} {headline(rows, m, label):.4f}" for m in methods)
              + "; days " + ", ".join(f"{st} {dmae(rows, methods[0], st, label)[1]}" for st in STATIONS))
    print("  mean error (observed minus forecast):")
    for st in STATIONS:
        print(f"    {st:<7} " + " ".join(f"{m} {dmae(rows, m, st)[2]:+.4f}" for m in methods))


# ------------------------------------------------------------------ --score

def run_score(args):
    t_start = time.time()
    if DAYS_OUT.exists():
        raise SystemExit(f"STOP: {DAYS_OUT} already exists; not overwriting it")
    print(f"SESSION 105 --score (offline), start {s104.now_utc()}; {s104.versions()}")
    print(f"LGB_PARAMS: {LGB_PARAMS}; features: {FEATURES}; w = {W}")
    print("BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5).")
    s104_days, days, hashes = run_gate_all()

    # Challenger 1's inputs (D99.3)
    print("\nCHALLENGER 1'S INPUTS (D99.3), every local day in the window")
    for st in STATIONS:
        dd = days[st]
        reasons = {}
        for r in dd:
            if r["x"] is None:
                reasons[r["why"]] = reasons.get(r["why"], 0) + 1
        ties = sum(r["tie"] for r in dd)
        first = dd[0]
        print(f"  {st}: days {len(dd)} ({first['local_date']} to {dd[-1]['local_date']}); complete inputs "
              f"{sum(r['x'] is not None for r in dd)}; without {sum(r['x'] is None for r in dd)} "
              f"{reasons or ''}; peak-hour ties broken {ties}; usable observed maximum "
              f"{sum(r['obs_max'] is not None for r in dd)}")

    # Fits: one model per airport and fold (D99.3(e)), with session 97's fit_predict
    print("\nFITS (one per airport and fold; session 97's fit_predict, LGB_PARAMS unchanged)")
    t_fit, fits = 0.0, 0
    ch1 = {}      # (station, local date) -> forecast
    ntrain = {}
    for st in STATIONS:
        for label, t0, t1 in FOLDS:
            train = [r for r in days[st] if training_day(r["last_hour"], t0) and r["obs_max"] is not None
                     and r["x"] is not None]
            if any(not r["last_hour"] < t0 for r in train):
                raise SystemExit("STOP: a training day's last hour is not before T0")
            if any(not a["local_date"] < b["local_date"] for a, b in zip(train, train[1:])):
                raise SystemExit("STOP: training days are not in ascending date")
            test = [r for r in days[st] if r["fold"] == label and r["x"] is not None]
            t = time.time()
            pred = s97.fit_predict([(r["x"], r["raw_max"], r["obs_max"]) for r in train],
                                   [(r["x"], r["raw_max"], 0.0) for r in test])
            t_fit += time.time() - t
            fits += 1
            ntrain[(st, label)] = (len(train), train[0]["local_date"], train[-1]["local_date"], len(test))
            for r, p in zip(test, pred):
                ch1[(st, r["local_date"])] = p
    for st in STATIONS:
        print(f"  {st}: training days " + "; ".join(
            f"{label} {ntrain[(st, label)][0]} ({ntrain[(st, label)][1]} to {ntrain[(st, label)][2]}), "
            f"test days with inputs {ntrain[(st, label)][3]}" for label, _, _ in FOLDS))
    print(f"  fits {fits}; fit time {t_fit:.1f} s; every training day's last hour is before its T0: yes")

    # Join to session 104's days (the gate has shown the day lists equal)
    rows = []
    by_key = {(r["station"], r["local_date"]): r for st in STATIONS for r in days[st] if r["fold"] is not None}
    lost = {st: {} for st in STATIONS}
    for f in s104_days:
        mine = by_key[(f["station"], dt.date.fromisoformat(f["local_date"]))]
        r = {"station": f["station"], "fold": f["fold"], "local_date": f["local_date"], "cycle": f["cycle"],
             "last_hour": mine["last_hour"], "obs_max": f["obs_max"], "raw_max": mine["raw_max"],
             "gfs_tmax": mine["gfs_tmax"], "peak_lead": mine["peak_lead"], "raw_gfs": f["raw_gfs_max"],
             "baseline": f["baseline_max"], "curve": f["curve_max"],
             "ch1": ch1.get((f["station"], mine["local_date"])), "ch1_why": mine["why"], "f147": f["common"]}
        if mine["x"] is None and f["common"]:
            lost[f["station"]][mine["why"]] = lost[f["station"]].get(mine["why"], 0) + 1
        r["common"] = f["common"] and r["ch1"] is not None
        rows.append(r)
    common = [r for r in rows if r["common"]]
    print("\nTest days lost for missing inputs (in F147.6's common set, no challenger 1 forecast): "
          + "; ".join(f"{st} {sum(lost[st].values())} {lost[st] or ''}" for st in STATIONS))

    # Test 1 (D99.4)
    print("\n" + "=" * 90)
    print("TEST 1 (D99.4). BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C.")
    print("=" * 90)
    print_table(common, ("raw_gfs", "baseline", "curve", "ch1"), "Common day set (D99.4), pooled over folds:")
    t1 = d89_6(common, "curve", "ch1")
    print("\nD89.6, challenger 1 against the curve's read-off maximum:")
    s100.print_test("challenger 1 (daily-maximum model) against the curve", t1)
    m_name = "challenger 1" if t1["pass"] else "the curve's read-off maximum"
    for r in rows:
        r["M"] = r["ch1"] if t1["pass"] else r["curve"]
    print(f"M = {m_name}")

    # Challenger 2 (D99.5)
    print("\n" + "=" * 90)
    print("TEST 2 (D99.6). BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C.")
    print("=" * 90)
    late, b0, b_end = 0, 0, {}
    for st in STATIONS:
        for label, _, _ in FOLDS:
            fr = [r for r in rows if r["station"] == st and r["fold"] == label]
            out, b_last = daily_track([(r["cycle"], r["last_hour"], r["obs_max"], r["M"]) for r in fr])
            b_end[(st, label)] = b_last
            for r, (b, fc2, used, latest) in zip(fr, out):
                r["b"], r["ch2"] = b, fc2
                late += latest is not None and not latest < r["cycle"]
                b0 += r["common"] and used == 0
    print(f"trackers: {len(b_end)}; forecasts that used an error from a day whose last hour is not before "
          f"their cycle: {late}; common days corrected with b = 0: {b0}")
    if late:
        raise SystemExit("STOP: a correction used an error not before its cycle")
    print("b at the end of each fold:")
    for st in STATIONS:
        print(f"  {st:<7} " + ", ".join(f"{label} {b_end[(st, label)]:+.4f}" for label, _, _ in FOLDS))
    print_table(common, ("M", "ch2"), "Common day set (as test 1), pooled over folds:")
    t2 = d89_6(common, "M", "ch2")
    print("\nD89.6, challenger 2 (M plus b) against M:")
    s100.print_test("challenger 2 (daily drift) against M", t2)
    final = (f"{m_name} plus D99.5's correction" if t2["pass"] else m_name)
    print(f"\nThe daily maximum's incumbent after session 105: {final}")

    # Days file
    def f_(v):
        return "" if v is None else s97.fmt(v)

    cols = ["station", "fold", "local_date", "cycle", "obs_max", "raw_max", "gfs_tmax", "peak_lead", "curve_max",
            "ch1_forecast", "ch1_reason", "M_forecast", "b", "ch2_forecast", "common"]
    out_rows = [[r["station"], r["fold"], r["local_date"], r["cycle"].strftime("%Y-%m-%dT%H:%MZ"), f_(r["obs_max"]),
                 f_(r["raw_max"]), f_(r["gfs_tmax"]), f_(r["peak_lead"]), f_(r["curve"]), f_(r["ch1"]),
                 r["ch1_why"], f_(r["M"]), f_(r["b"]), f_(r["ch2"]), "true" if r["common"] else "false"]
                for r in rows]
    text = s97.csv_text(cols, out_rows)
    s97.write_new(DAYS_OUT, text)
    print(f"\nwrote {DAYS_OUT.relative_to(ROOT)}: {len(out_rows)} rows, SHA-256 "
          f"{hashlib.sha256(text.encode()).hexdigest()}")

    # D99.10's descriptive figures
    print("\nDESCRIPTIVE (D99.10), not used by the rules")
    print("MAE on F147.6's own day set (each method where it has a forecast; days in brackets) beside the new "
          "common set:")
    f147 = [r for r in rows if r["f147"]]
    for m in ("raw_gfs", "baseline", "curve", "ch1", "M", "ch2"):
        sub = [r for r in f147 if r[m] is not None]
        print(f"  {m:<9} F147.6 set: headline {headline(sub, m):.4f} ("
              + ", ".join(f"{st} {dmae(sub, m, st)[0]:.4f} [{dmae(sub, m, st)[1]}]" for st in STATIONS)
              + f"); new common set: headline {headline(common, m):.4f}")
    print(f"\nend {s104.now_utc()}; run time {time.time() - t_start:.1f} s; fits {fits}; fit time {t_fit:.1f} s")


# ------------------------------------------------------------------ --meta

def run_meta(args):
    if not DAYS_OUT.exists():
        raise SystemExit(f"STOP: {DAYS_OUT} does not exist")
    hashes = s104.table25_hashes()
    lines = [
        "session105_dailymax_cv.meta.txt",
        f"written {s104.now_utc()} by scripts/session105_dailymax_cv.py --meta",
        "",
        "What the file is (BUILD-CHOICE SCORES, NOT RESULTS, SPEC 2.5):",
        "  session105_dailymax_cv_days.csv: one row per airport and local day in a test fold (D98.10(d)): the",
        "    cycle, the observed maximum, raw_max, gfs_tmax and the peak hour's lead (D99.3(b)), the curve's",
        "    read-off maximum (session 104's days file), challenger 1's forecast (or why none), M's forecast",
        "    (D99.4), b and challenger 2's forecast (D99.5), and whether the day is in D99.4's common day set.",
        "",
        "Rules: DECISIONS D99, D98.10, D89.3, D89.6, D97.4.",
        "",
        "Inputs and their SHA-256:",
    ]
    for st in STATIONS:
        name, _ = s97.TABLES[st]
        lines.append(f"  MLwx-stagec/{name} {sha256_file(s97.STAGEC_DIR / name)}")
    for st in STATIONS:
        lines.append(f"  MLwx-stagec/{s104.TABLE25[st]} {sha256_file(s97.STAGEC_DIR / s104.TABLE25[st])} "
                     f"(meta: {hashes[st]})")
    for p in (S104_DAYS, s104.TABLE25_META, S104_SCRIPT, HERE / "session103_bias_drift_cv.py",
              HERE / "session100_structure_cv.py", HERE / "session97_stagec_cv.py", s97.RECORD_SCRIPT):
        lines.append(f"  {p.relative_to(ROOT)} {sha256_file(p)}")
    lines += [
        "",
        f"Script: scripts/session105_dailymax_cv.py {sha256_file(SCRIPT)}",
        "",
        "Output and its SHA-256:",
        f"  {DAYS_OUT.relative_to(ROOT)} {sha256_file(DAYS_OUT)}",
        "",
        f"LGB_PARAMS as passed (from session 97, which takes them from scripts/session62_reserved_confirm.py): "
        f"{LGB_PARAMS}",
        f"Feature order (D99.3(b)): {FEATURES}",
        f"w: {W}",
        f"Fit counts: {args.fit_counts}. No model saved.",
        f"Run times (as printed by the runs): {args.run_times}",
        f"Versions: {s104.versions()}",
    ]
    text = "\n".join(lines) + "\n"
    s97.write_new(META_OUT, text)
    print(f"wrote {META_OUT.relative_to(ROOT)}: {len(lines)} lines, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    g.add_argument("--meta", action="store_true")
    ap.add_argument("--run-times", default="not given", help="--meta only")
    ap.add_argument("--fit-counts", default="not given", help="--meta only")
    args = ap.parse_args()
    if args.gate:
        t = time.time()
        print(f"SESSION 105 --gate (offline, no fit), start {s104.now_utc()}; {s104.versions()}")
        run_gate_all()
        print(f"run time {time.time() - t:.1f} s")
    elif args.score:
        run_score(args)
    else:
        run_meta(args)


if __name__ == "__main__":
    main()
