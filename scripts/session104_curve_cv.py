"""Session 104: the curve at leads 3 to 48 and the daily maximum (DECISIONS D98).
Offline. Build-choice scores only, never results (SPEC 2.5). No build choice
is made here.

The curve is D88.4's baseline (one model per airport, cycle hour and lead,
the record's settings) plus D97's correction: b, a decaying average of the
baseline's own recent errors, w = 0.02, one tracker per airport, fold, cycle
hour and lead, using only errors whose valid time is before the forecast's
cycle (D97.4 to D97.7, D98.5). Each model also predicts test rows whose
features are complete but which have no observation (D98.7); those rows never
enter an hourly score and never update a tracker, and the correction is
applied to them too.

Modes (one per run):
  --gate   1. the tracker's self-check (session 103's four cases and two more
           at leads 47 and 48); 2. D98.6: the baseline and the correction at
           leads 3 to 24 reproduce F139 and F146 exactly; 3. D98.5's fitting
           gate at YSDU (00z, lead 26) and RNO (18z, lead 26) against F109's
           raw GFS and B+D,L,R,T MAEs, exact. Writes nothing.
  --score  gates 1 and 2 again, then the baseline at leads 25 to 48, the
           trackers, the hourly scores at leads 3 to 48 and the daily maximum
           (D98.10). Writes data/processed/session104_curve_cv_scores.csv and
           data/processed/session104_dailymax_days.csv.
  --meta   writes data/processed/session104_curve_cv.meta.txt.

Imported read only, each after its SHA-256 check: scripts/session97_stagec_cv.py
(F139), scripts/session100_structure_cv.py (F143) and
scripts/session103_bias_drift_cv.py (F146); for the daily maximum's
cross-check, scripts/session96_stagec_table.py (F138; its load_obs, the
reports the table was paired from) and scripts/session90_airport_check.py
(hour_of and local_day_counts). Used: from session 97 load_table, fold_role,
fit_predict, mae, mean_error, csv_text, fmt, write_new, parse_time,
check_valid, check_obs_time, TABLE_COLUMNS, G15, LGB_PARAMS, FOLDS,
CYCLE_HOURS, GATE_TRAIN, GATE_TEST; from session 100 split_rows,
check_against_s97 and the F139 constants; from session 103 track (the
tracker, unchanged) and run_check. This script never imports or calls the
session-48 guard itself (D90.1); lightgbm is imported directly (D93.3).

Output files are written once and never overwritten (SPEC 8.7 item 5).
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# Checked before any of them is imported.
IMPORTED = {
    "session97_stagec_cv.py": "987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91",       # F139
    "session100_structure_cv.py": "67e709ea0925d84b4e257c44c5a95211f46a5ff5443408d7c526dbffb28d6957",   # F143
    "session103_bias_drift_cv.py": "56460a0a3eb91f4ab1d427f3ad1631e1e7b58c692be8e8e4b48829c90d0c0e83",  # F146
}
for _name, _want in IMPORTED.items():
    if sha256_file(HERE / _name) != _want:
        raise SystemExit(f"STOP: scripts/{_name}'s SHA-256 is not the recorded value")
sys.path.insert(0, str(HERE))
import session103_bias_drift_cv as s103  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

s100 = s103.s100
s97 = s100.s97

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
S103_SCORES = PROCESSED / "session103_bias_drift_cv_scores.csv"
S103_SCORES_SHA256 = "dcae3a8a66349fcccb261aebd60213936e4fb05e1431fe2df7b08997c7059ec5"   # F146.6
F146_HEADLINE = 1.019044682206963                                                        # F146.3, D98.6
TABLE25_META = PROCESSED / "session104_stagec_f025_048_table.meta.txt"
SCORES_OUT = PROCESSED / "session104_curve_cv_scores.csv"
DAYS_OUT = PROCESSED / "session104_dailymax_days.csv"
META_OUT = PROCESSED / "session104_curve_cv.meta.txt"
SCRIPT = Path(__file__).resolve()
S96_SCRIPT_SHA256 = "40b63d006a3de4b4b796476c6b2408700bc9200a508feda804a187531b666eee"     # F138
S90_SCRIPT = HERE / "session90_airport_check.py"

STATIONS = s97.STATIONS
FOLDS = s97.FOLDS
CYCLE_HOURS = s97.CYCLE_HOURS
LGB_PARAMS = s97.LGB_PARAMS
LEADS_A = tuple(range(3, 25))      # F138's table
LEADS_B = tuple(range(25, 49))     # this session's table
LEADS_ALL = LEADS_A + LEADS_B      # D98.8: the product's horizon
METHODS = ("raw_gfs", "baseline", "curve")
W = s103.W

TABLE25 = {st: f"stagec_dev_f025_048_{s97.TABLES[st][0][len('stagec_dev_'):]}" for st in STATIONS}

# D98.5's fitting gate: F109's fold at the record's cycle hour and lead 26.
GATE25 = [("YSDU", 0, 26), ("RNO", 18, 26)]
# Owner ruling at session 104's stop (recorded in F147): for gate 3 only, this one cell, empty in the table
# ("outside pull window"), takes the committed value from session81_training_set.csv, so the training rows
# match F109's. It is never used in any cross-validation fit or score.
GATE_FILL = {("YSDU", dt.date(2021, 3, 24), "pressure_tendency_3h_hpa"): -0.921}

# D98.10(a): time zones.
TZ = {"EGLC": "Europe/London", "LFPG": "Europe/Paris", "DSM": "America/Chicago", "YSDU": "Australia/Sydney",
      "RNO": "America/Los_Angeles", "SFO": "America/Los_Angeles"}
DAY_LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)
ARRIVAL = dt.timedelta(hours=4)     # D98.10(b): c + 4 hours <= the day's start


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


# ------------------------------------------------------------------ tables

def table25_hashes():
    """The new table files' SHA-256, from this session's table meta."""
    text = TABLE25_META.read_text()
    out = {}
    for st, name in TABLE25.items():
        m = re.search(rf"^  {re.escape(name)}  rows [\d,]+  bytes [\d,]+  sha256 ([0-9a-f]{{64}})$", text, re.M)
        if not m:
            raise SystemExit(f"STOP: {name} not in {TABLE25_META.name}")
        out[st] = m.group(1)
    return out


def load_table25(st, want):
    """As session 97's load_table, for the 25-48 table: (cycle, valid, cycle_hour,
    lead, complete, obs, temp, x) per row, in file order, with the same checks
    (SHA-256 first, the 2026-27 guard, complete_case against the nine columns
    and the observation, temp equal to temperature_grib_c)."""
    name = TABLE25[st]
    path = s97.STAGEC_DIR / name
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"STOP: {name} SHA-256 {got} is not the table meta's {want}")
    rows = []
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != s97.TABLE_COLUMNS:
            raise SystemExit(f"STOP: {name} header is not F138.4's")
        ix = {c: i for i, c in enumerate(head)}
        gi = [ix[c] for c in s97.G15]
        for r in rd:
            if r[ix["station"]] != st:
                raise SystemExit(f"STOP: {name} holds a row for station {r[ix['station']]}")
            valid = s97.parse_time(r[ix["valid_utc"]])
            s97.check_valid(valid)
            if r[ix["obs_time_utc"]]:
                s97.check_obs_time(s97.parse_time(r[ix["obs_time_utc"]]))
            lead = int(r[ix["lead"]])
            if lead not in LEADS_B:
                raise SystemExit(f"STOP: {name} lead {lead}")
            cycle = s97.parse_time(r[ix["cycle_utc"]])
            x = [s97.fval(r[i]) for i in gi]
            obs = s97.fval(r[ix["obs_tmpc"]])
            complete = r[ix["complete_case"]] == "true"
            if complete != (all(v is not None for v in x) and obs is not None):
                raise SystemExit(f"STOP: {name} complete_case disagrees with its columns")
            if x[0] is not None and float(r[ix["temperature_grib_c"]]) != x[0]:
                raise SystemExit(f"STOP: {name} temp differs from temperature_grib_c")
            rows.append((cycle, valid, int(r[ix["cycle_hour"]]), lead, complete, obs, x[0], x))
    return rows


# ------------------------------------------------------------------ fitting and the tracker

def correct(scored, extra, lead):
    """The tracker (session 103's track, unchanged) on one cell. scored: (cycle,
    obs, baseline fc) of the scored test rows, extra: (cycle, baseline fc) of
    the rows with complete features and no observation, each in ascending cycle
    time. Scored rows are corrected by track itself; an extra row is corrected
    by running track on the scored rows from earlier cycles followed by the
    extra row, so it gets b from exactly the errors valid before its cycle and
    its own (absent) error is never queued. Returns (scored corrected, scored
    errors used, scored latest used, extra corrected, extra errors used, extra
    latest used)."""
    rows = [(c, lead, o, f) for c, o, f in scored]
    corr, n_used, latest, _ = s103.track(rows)
    x_corr, x_n, x_latest = [], [], []
    for c, f in extra:
        pre = [r for r in rows if r[0] < c] + [(c, lead, f, f)]
        cc, nn, ll, _ = s103.track(pre)
        x_corr.append(cc[-1])
        x_n.append(nn[-1])
        x_latest.append(ll[-1])
    return corr, n_used, latest, x_corr, x_n, x_latest


def score_part(st, rows, leads, timer):
    """Per fold, cycle hour and lead: one baseline model (session 97's fit_predict),
    fitted on session 100's split_rows selection, predicting the scored test rows
    and then the extra rows (complete features, no observation) in one call; then
    the tracker. Returns {(fold, h, n): cell} and the fit count."""
    cells, fits = {}, 0
    keep = set(leads)
    for label, t0, t1 in FOLDS:
        sub = [r for r in rows if r[3] in keep]
        train, test = split_rows_leads(sub, t0, t1, leads)
        extra = {(h, n): [] for h in CYCLE_HOURS for n in leads}
        for cycle, valid, h, n, complete, obs, temp, x in sub:
            if not complete and obs is None and all(v is not None for v in x) \
                    and s97.fold_role(cycle, valid, t0, t1) == "test":
                extra[(h, n)].append((cycle, x, temp, None))
        for k in extra:
            extra[k].sort(key=lambda r: r[0])
        for h in CYCLE_HOURS:
            for n in leads:
                tr, te, ex = train[(h, n)], test[(h, n)], extra[(h, n)]
                if not tr or not te:
                    raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: train {len(tr)}, test {len(te)}")
                if tr[-1][0] >= te[0][0] or max(r[0] for r in tr) + dt.timedelta(hours=n) >= t0:
                    raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: training not before test")
                t = time.time()
                fc = s97.fit_predict([(r[1], r[2], r[3]) for r in tr],
                                     [(r[1], r[2], r[3]) for r in te] + [(r[1], r[2], r[3]) for r in ex])
                timer["fit"] += time.time() - t
                fits += 1
                base, xbase = fc[:len(te)], fc[len(te):]
                corr, n_used, latest, x_corr, x_n, x_latest = correct(
                    [(r[0], r[3], base[i]) for i, r in enumerate(te)], [(r[0], xbase[i]) for i, r in enumerate(ex)], n)
                cells[(label, h, n)] = {
                    "cycles": [r[0] for r in te], "obs": [r[3] for r in te], "raw": [r[2] for r in te],
                    "baseline": base, "curve": corr, "n_used": n_used, "latest": latest,
                    "x_cycles": [r[0] for r in ex], "x_raw": [r[2] for r in ex], "x_baseline": xbase,
                    "x_curve": x_corr, "x_n_used": x_n, "x_latest": x_latest, "n_train": len(tr)}
    return cells, fits


def split_rows_leads(rows, t0, t1, leads):
    """Session 100's split_rows for leads 3 to 24; the same rule written for
    any leads otherwise (its cells are fixed to leads 3 to 24)."""
    if tuple(leads) == s97.LEADS:
        return s100.split_rows(rows, t0, t1)
    train = {(h, n): [] for h in CYCLE_HOURS for n in leads}
    test = {(h, n): [] for h in CYCLE_HOURS for n in leads}
    for cycle, valid, h, n, complete, obs, temp, x in rows:
        if not complete:
            continue
        role = s97.fold_role(cycle, valid, t0, t1)
        if role == "train":
            if not valid < t0:
                raise SystemExit("STOP: a training row is not before T0")
            train[(h, n)].append((cycle, x, temp, obs))
        elif role == "test":
            test[(h, n)].append((cycle, x, temp, obs))
    for d in (train, test):
        for k in d:
            d[k].sort(key=lambda r: r[0])
    return train, test


def errors(cells, leads, methods=METHODS):
    """{(st, fold, h, n, method): errors (obs minus forecast)} over the scored rows."""
    errs = {}
    for (st, label, h, n), c in cells.items():
        if n not in leads:
            continue
        for m in methods:
            fc = c["raw"] if m == "raw_gfs" else c[m]
            if len(fc) != len(c["obs"]):
                raise SystemExit(f"STOP: {m} n differs at {st} {label} {h}z lead {n}")
            errs[(st, label, h, n, m)] = [o - fc[i] for i, o in enumerate(c["obs"])]
    return errs


def pooled(errs, meth, st, folds=None, leads=LEADS_ALL):
    """One MAE (and n) over the concatenated errors, in fold, cycle hour, lead,
    then row order (session 97's pooled, over any leads)."""
    e = []
    for label, _, _ in FOLDS:
        if folds and label not in folds:
            continue
        for h in CYCLE_HOURS:
            for n in leads:
                e.extend(errs[(st, label, h, n, meth)])
    return s97.mae(e), len(e), s97.mean_error(e) if e else float("nan")


def headline(errs, meth, leads, folds=None):
    return sum(pooled(errs, meth, st, folds, leads)[0] for st in STATIONS) / len(STATIONS)


def d89_6(errs, inc, ch, leads):
    """D89.6, as session 100's d89_6, over the given leads."""
    hi, hc = headline(errs, inc, leads), headline(errs, ch, leads)
    red = (hi - hc) / hi
    airports = sum(pooled(errs, ch, st, None, leads)[0] < pooled(errs, inc, st, None, leads)[0] for st in STATIONS)
    folds = sum(headline(errs, ch, leads, [label]) < headline(errs, inc, leads, [label]) for label, _, _ in FOLDS)
    parts = (red > 0.01, airports >= 4, folds >= 2)
    return {"red": red, "airports": airports, "folds": folds, "parts": parts, "pass": all(parts)}


# ------------------------------------------------------------------ gates

def gate_check():
    """Gate 1: session 103's self-check (four cases), then leads 47 and 48."""
    print("Gate 1: the tracker's self-check")
    s103.run_check(argparse.Namespace())
    days = [dt.datetime(2024, 1, d, 12) for d in (1, 2, 3, 4)]
    ok = True
    for lead, want, want_n in ((47, [0.0, 0.0, 0.02, 0.0396], [0, 0, 1, 2]),
                               (48, [0.0, 0.0, 0.0, 0.02], [0, 0, 0, 1])):
        rows = [(c, lead, 11.0, 10.0) for c in days]
        corrected, n_used, latest, _ = s103.track(rows)
        got = [corrected[i] - r[3] for i, r in enumerate(rows)]
        good = all(abs(g - x) <= 1e-12 for g, x in zip(got, want)) and n_used == want_n \
            and all(lt is None or lt < r[0] for lt, r in zip(latest, rows))
        ok &= good
        print(f"  {'PASS' if good else 'FAIL'}: daily, lead {lead}, errors 1.0 x 4: corrections "
              f"{[round(g, 12) for g in got]}, expected {want}; errors used {n_used}, expected {want_n}")
    if not ok:
        raise SystemExit("STOP: the tracker's extended self-check failed")
    print("Gate 1: PASS (session 103's four cases and the two at leads 47 and 48)")


def gate_reproduce(timer):
    """Gate 2 (D98.6): leads 3 to 24, F139 and F146 exact. Returns the cells."""
    print("\nGate 2 (D98.6): the baseline and the correction at leads 3 to 24")
    cells, fits = {}, 0
    for st in STATIONS:
        t = time.time()
        c, f = score_part(st, s97.load_table(st), LEADS_A, timer)
        cells.update({(st,) + k: v for k, v in c.items()})
        fits += f
        print(f"  {st}: {f} fits, {time.time() - t:.1f} s", flush=True)
    errs = errors(cells, LEADS_A)
    equal, total, head, head_eq, n_eq = s100.check_against_s97(errs)
    ok139 = equal == total == 3168 and head_eq == 2 and n_eq == 6
    print(f"  baseline fits {fits}; F139: cells equal (n and MAE, raw_gfs and baseline) {equal} of {total}; "
          f"headline {head_eq} of 2 (raw_gfs {head['raw_gfs']!r}, baseline {head['baseline']!r}); n {n_eq} of 6")
    got = sha256_file(S103_SCORES)
    if got != S103_SCORES_SHA256:
        raise SystemExit(f"STOP: {S103_SCORES.name} SHA-256 {got} is not F146.6's")
    rec = {}
    with open(S103_SCORES, newline="") as f:
        for r in csv.DictReader(f):
            if r["method"] == "drift":
                rec[(r["station"], r["fold"], int(r["cycle_hour"]), int(r["lead"]))] = (int(r["n"]), float(r["mae"]))
    eq146 = sum(len(errs[k + ("curve",)]) == n and s97.mae(errs[k + ("curve",)]) == m for k, (n, m) in rec.items())
    h146 = headline(errs, "curve", LEADS_A)
    ok146 = eq146 == len(rec) == 1584 and h146 == F146_HEADLINE
    print(f"  F146: drift cells equal to session 103's file (n and MAE) {eq146} of {len(rec)}; headline "
          f"{h146!r} (F146 {F146_HEADLINE!r}) equal {h146 == F146_HEADLINE}")
    if not (ok139 and ok146):
        raise SystemExit("STOP: gate 2 (D98.6) failed")
    print("Gate 2: PASS")
    return cells, fits


def gate_fit25(hashes):
    """Gate 3 (D98.5): YSDU and RNO at lead 26, F109's fold, against the grid."""
    print("\nGate 3 (D98.5): the fitting gate at YSDU (00z, lead 26) and RNO (18z, lead 26)")
    for path, want in ((s97.TRAINING_SET, s97.TRAINING_SET_SHA256), (s97.GRID, s97.GRID_SHA256)):
        if sha256_file(path) != want:
            raise SystemExit(f"STOP: {path.name} SHA-256")
    keys, rec_obs, rec_rows = {}, {}, {}
    with open(s97.TRAINING_SET, newline="") as f:
        for r in csv.DictReader(f):
            d = dt.date.fromisoformat(r["target_date"])
            keys.setdefault(r["station"], set()).add(d)
            rec_obs[(r["station"], d)] = float(r["obs_c"])
            rec_rows[(r["station"], d)] = r
    for (st, d, col), v in GATE_FILL.items():
        if float(rec_rows[(st, d)][col]) != v:
            raise SystemExit(f"STOP: the committed {col} at {st} {d} is not {v}")
    grid = {}
    with open(s97.GRID, newline="") as f:
        for r in csv.DictReader(f):
            grid[r["station"]] = r
    results = {}
    for use_record_obs in (False, True):
        all_equal = True
        label = "the record's obs_c" if use_record_obs else "the table's observation"
        print(f"  observations: {label}")
        for st, hour, lead in GATE25:
            rows = [r for r in load_table25(st, hashes[st]) if r[3] == lead and r[2] == hour
                    and r[1].date() in keys.get(st, set())]
            rows.sort(key=lambda r: r[0])
            sel = []
            filled = []
            for cycle, valid, h, n, complete, obs, temp, x in rows:
                for (fst, fd, col), v in GATE_FILL.items():
                    if fst == st and fd == valid.date():
                        i = s97.G15.index(col)
                        if x[i] is not None:
                            raise SystemExit(f"STOP: {st} {fd} {col} is not empty in the table")
                        x = list(x)
                        x[i] = v
                        complete = obs is not None and all(u is not None for u in x)
                        filled.append(f"{st} {fd} {col} = {v!r} (committed value, gate only)")
                if use_record_obs:
                    obs = rec_obs[(st, valid.date())]
                    complete = all(v is not None for v in x)
                if complete:
                    sel.append((valid.date(), x, temp, obs))
            train = [(r[1], r[2], r[3]) for r in sel if s97.GATE_TRAIN[0] <= r[0] <= s97.GATE_TRAIN[1]]
            test = [(r[1], r[2], r[3]) for r in sel if s97.GATE_TEST[0] <= r[0] <= s97.GATE_TEST[1]]
            fc = s97.fit_predict(train, test)
            m_model = s97.mae([r[2] - fc[i] for i, r in enumerate(test)])
            m_raw = s97.mae([r[2] - r[1] for r in test])
            g = grid[st]
            eq_f, eq_r = m_model == float(g["final_mae"]), m_raw == float(g["raw_mae"])
            all_equal &= eq_f and eq_r
            print(f"    {st} {hour:02d}z lead {lead}: table rows on the training set's dates {len(rows)}; train "
                  f"{len(train)}; test {len(test)} (grid no_obs {g['no_obs']})")
            for line in filled:
                print(f"      owner ruling, gate only: {line}")
            print(f"      B+D,L,R,T this fit {m_model!r}, grid final_mae {g['final_mae']}: {'equal' if eq_f else 'NOT EQUAL'}")
            print(f"      raw GFS   this fit {m_raw!r}, grid raw_mae {g['raw_mae']}: {'equal' if eq_r else 'NOT EQUAL'}")
        results[use_record_obs] = all_equal
        print(f"  with {label}: {'all four values equal' if all_equal else 'NOT all equal'}")
        if all_equal and not use_record_obs:
            break
    if results.get(False):
        print("Gate 3: PASS (the table's own observations)")
        return "pass"
    if results.get(True):
        print("Gate 3: the table's observations differ from the record's; with the record's obs_c all four values "
              "are equal (D98.5: both results reported)")
        return "pass with the record's observations"
    raise SystemExit("STOP: gate 3 (D98.5) failed with the record's observations too")


def run_gate(args):
    t0 = time.time()
    print(f"SESSION 104 --gate (offline), start {now_utc()}; {versions()}")
    print("scripts' SHA-256 checked before import: " + "; ".join(f"{k} {v}" for k, v in IMPORTED.items()))
    gate_check()
    timer = {"fit": 0.0}
    _, fits = gate_reproduce(timer)
    hashes = table25_hashes()
    outcome = gate_fit25(hashes)
    print(f"\nGATE PASS (gate 3: {outcome}); fits: gate 2 {fits}, gate 3 2 or 4; fit time {timer['fit']:.1f} s; "
          f"end {now_utc()}; run time {time.time() - t0:.1f} s")


# ------------------------------------------------------------------ the daily maximum (D98.10)

def day_cycle(s):
    """D98.10(b): the latest cycle c (00, 06, 12, 18 UTC) with c + 4 hours <= s."""
    t = s - ARRIVAL
    return t.replace(hour=6 * (t.hour // 6), minute=0, second=0, microsecond=0)


def local_day(d, tzname):
    """The UTC start, the UTC end (exclusive) and the whole UTC hours of local day d."""
    tz = ZoneInfo(tzname)
    utc = dt.timezone.utc
    d2 = d + dt.timedelta(days=1)
    s = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(utc).replace(tzinfo=None)
    e = dt.datetime(d2.year, d2.month, d2.day, tzinfo=tz).astimezone(utc).replace(tzinfo=None)
    if s.minute or e.minute:
        raise SystemExit(f"STOP: {tzname} is not a whole number of hours from UTC on {d}")
    hours = [s + dt.timedelta(hours=k) for k in range(int((e - s) / dt.timedelta(hours=1)))]
    if len(hours) not in (23, 24, 25):
        raise SystemExit(f"STOP: {tzname} local day {d} has {len(hours)} hours")
    return s, e, hours


def usable_day(n_hours, n_usable):
    """D82.8, D98.10(a): usable hours at least the day's hours minus 2."""
    return n_usable >= n_hours - 2


def fold_of(c):
    for label, t0, t1 in FOLDS:
        if t0 <= c < t1:
            return label
    return None


def daily_max(st, obs_by_valid, fc):
    """One airport's days. obs_by_valid: {valid: obs or None}, every whole hour
    of the window; fc: {(cycle, lead): {method: forecast}}. Returns the day rows
    and the drop counts."""
    tzname = TZ[st]
    rows, drops = [], {}
    first = FOLDS[0][1].date() - dt.timedelta(days=1)
    d = first
    while d <= FOLDS[-1][2].date():
        s, e, hours = local_day(d, tzname)
        c = day_cycle(s)
        label = fold_of(c)
        # A candidate: its cycle is in a fold, or its local date is in a test year.
        candidate = label is not None or FOLDS[0][1].date() <= d < FOLDS[-1][2].date()
        why = None
        if not candidate:
            pass
        elif hours[-1] > DAY_LAST_VALID:
            why = "last hour after 2026-07-31T23:00"
        elif label is None:
            why = "cycle before its fold's T0 (in neither)"
        if why:
            drops[why] = drops.get(why, 0) + 1
        if why or not candidate:
            d += dt.timedelta(days=1)
            continue
        leads = [int((h - c) / dt.timedelta(hours=1)) for h in hours]
        if min(leads) < 4 or max(leads) > 33:
            raise SystemExit(f"STOP: {st} {d} leads {min(leads)} to {max(leads)}")
        if any(h not in obs_by_valid for h in hours):
            raise SystemExit(f"STOP: {st} {d}: an hour is not in the table")
        vals = [obs_by_valid[h] for h in hours]
        usable = [v for v in vals if v is not None]
        obs_ok = usable_day(len(hours), len(usable))
        obs_max = max(usable) if obs_ok else None
        row = {"station": st, "fold": label, "local_date": d.isoformat(), "hours": len(hours),
               "usable_hours": len(usable), "obs_max": obs_max,
               "obs_reason": "" if obs_ok else "too few usable hours", "cycle": c, "first_lead": leads[0],
               "last_lead": leads[-1]}
        for m in METHODS:
            f = [fc.get((c, n), {}).get(m) for n in leads]
            if any(v is None for v in f):
                row[m] = None
                row[m + "_reason"] = f"no forecast at {sum(v is None for v in f)} hours"
            else:
                row[m] = max(f)
                row[m + "_reason"] = ""
        row["common"] = obs_max is not None and all(row[m] is not None for m in METHODS)
        rows.append(row)
        d += dt.timedelta(days=1)
    return rows, drops


def cross_check(st, obs_by_valid, s96, s90):
    """Session 90's hour_of and local_day_counts on the reports the table was
    paired from (session 96's load_obs), against the same counts from the
    table's hourly observations."""
    _, _, file_order, _ = s96.load_obs(st)
    reps = [(t, v is not None) for t, v in file_order]   # parse_reports keeps unusable reports, value None
    # Whole hours of the window only (a report just before 2026-08-01T00:00 maps to that hour, outside it).
    hours90 = {h for h in (s90.hour_of(t) for t, ok in reps if ok)
               if h is not None and s90.FIRST_UTC <= h <= DAY_LAST_VALID}
    r90 = s90.local_day_counts(hours90, TZ[st])
    hours_table = {v for v, o in obs_by_valid.items() if o is not None}
    rt = s90.local_day_counts(hours_table, TZ[st])
    return r90, rt, hours90 == hours_table


# ------------------------------------------------------------------ --score

def run_score(args):
    t_start = time.time()
    for p in (SCORES_OUT, DAYS_OUT):
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists; not overwriting it")
    print(f"SESSION 104 --score (offline), start {now_utc()}; {versions()}")
    print(f"LGB_PARAMS: {LGB_PARAMS}; w = {W}")
    print("BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5).")
    gate_check()
    timer = {"fit": 0.0}
    cells, fits_a = gate_reproduce(timer)
    hashes = table25_hashes()

    # The baseline at leads 25 to 48, and the daily maximum's inputs.
    print("\nThe baseline and the correction at leads 25 to 48")
    if sha256_file(HERE / "session96_stagec_table.py") != S96_SCRIPT_SHA256:
        raise SystemExit("STOP: scripts/session96_stagec_table.py's SHA-256 is not F138's")
    import session96_stagec_table as s96
    import session90_airport_check as s90
    fits_b = 0
    obs_maps, fcs = {}, {}
    for st in STATIONS:
        t = time.time()
        rows_b = load_table25(st, hashes[st])
        c, f = score_part(st, rows_b, LEADS_B, timer)
        cells.update({(st,) + k: v for k, v in c.items()})
        fits_b += f
        # every whole hour's observation (the table's pairing), from both tables
        obs_map = {}
        rows_a = s97.load_table(st, leads=tuple(range(0, 25)))
        bad = 0
        fc = {}
        for cycle, valid, h, n, complete, obs, temp, x in rows_a + rows_b:
            if valid in obs_map and obs_map[valid] != obs:
                bad += 1
            obs_map[valid] = obs
            if temp is not None:
                fc.setdefault((cycle, n), {})["raw_gfs"] = temp
        if bad:
            raise SystemExit(f"STOP: {st}: {bad} rows give a different observation for the same valid time")
        obs_maps[st] = obs_map
        fcs[st] = fc
        print(f"  {st}: {f} fits, {time.time() - t:.1f} s", flush=True)
    for (st, label, h, n), c in cells.items():
        for pre in ("", "x_"):
            for i, cy in enumerate(c[pre + "cycles"]):
                d = fcs[st].setdefault((cy, n), {})
                d["baseline"] = c[pre + "baseline"][i]
                d["curve"] = c[pre + "curve"][i]
    fits = fits_a + fits_b
    print(f"baseline fits: leads 3 to 24 {fits_a}, leads 25 to 48 {fits_b}, all {fits}; fit time "
          f"{timer['fit']:.1f} s")

    # D98.5 and D98.7 checks on every tracker
    late, n_rows, n_extra, b0 = 0, 0, 0, {}
    for (st, label, h, n), c in cells.items():
        for cy, lt in list(zip(c["cycles"], c["latest"])) + list(zip(c["x_cycles"], c["x_latest"])):
            late += lt is not None and not lt < cy
        n_rows += len(c["cycles"])
        n_extra += len(c["x_cycles"])
        key = (label, "3-24" if n <= 24 else "25-48")
        b0[key] = b0.get(key, 0) + sum(k == 0 for k in c["n_used"]) + sum(k == 0 for k in c["x_n_used"])
    print(f"trackers: {len(cells)} cells; scored rows {n_rows:,}; rows with complete features and no observation "
          f"(predicted and corrected, never scored, D98.7) {n_extra:,}; rows that used an error whose valid time is "
          f"not before their cycle: {late}")
    print("rows corrected with b = 0, by fold and lead band: " + ", ".join(f"{k[0]} {k[1]} {v}"
                                                                         for k, v in sorted(b0.items())))
    if late:
        raise SystemExit("STOP: a correction used an error not before its cycle")

    # Hourly scores
    errs = errors(cells, LEADS_ALL)
    out = []
    for m in METHODS:
        for st in STATIONS:
            for label, _, _ in FOLDS:
                for h in CYCLE_HOURS:
                    for n in LEADS_ALL:
                        e = errs[(st, label, h, n, m)]
                        out.append([st, label, h, n, m, len(e), s97.mae(e), s97.mean_error(e), m])
    header = ["station", "fold", "cycle_hour", "lead", "method", "n", "mae", "mean_error", "model"]
    text = s97.csv_text(header, [[s97.fmt(v) for v in r] for r in out])
    s97.write_new(SCORES_OUT, text)
    print(f"\nwrote {SCORES_OUT.relative_to(ROOT)}: {len(out)} rows, SHA-256 "
          f"{hashlib.sha256(text.encode()).hexdigest()}")

    print("\n" + "=" * 90)
    print("HOURLY. BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C. Common row set (D89.5, D98.8).")
    print("=" * 90)
    bands = (("3-48", LEADS_ALL), ("3-24", LEADS_A), ("25-48", LEADS_B))
    for name, leads in bands:
        print(f"\nPer airport, pooled over folds, cycle hours and leads {name}:")
        print(f"  {'airport':<7} {'n':>8} " + " ".join(f"{m:>9}" for m in METHODS))
        for st in STATIONS:
            print(f"  {st:<7} {pooled(errs, 'baseline', st, None, leads)[1]:>8,} "
                  + " ".join(f"{pooled(errs, m, st, None, leads)[0]:>9.4f}" for m in METHODS))
        print(f"  {'HEADLINE':<16} " + " ".join(f"{headline(errs, m, leads):>9.4f}" for m in METHODS))
        print("  full precision: " + ", ".join(f"{m} {headline(errs, m, leads)!r}" for m in METHODS))
    print("\nFold level, leads 3 to 48 (each airport's MAE over the fold's rows; unweighted mean of six):")
    print(f"  {'fold':<8} {'method':<9} " + " ".join(f"{s:>7}" for s in STATIONS) + f" {'fold-level':>11}")
    for label, _, _ in FOLDS:
        for m in METHODS:
            vals = [pooled(errs, m, st, [label], LEADS_ALL)[0] for st in STATIONS]
            print(f"  {label:<8} {m:<9} " + " ".join(f"{v:>7.4f}" for v in vals) + f" {sum(vals) / 6:>11.4f}")
    print("\nMean error (observation minus forecast), leads 3 to 48, per airport:")
    for st in STATIONS:
        print(f"  {st:<7} " + " ".join(f"{m} {pooled(errs, m, st, None, LEADS_ALL)[2]:+.4f}" for m in METHODS))
    print("\nD89.6's three parts, the curve against the baseline at leads 25 to 48 (DESCRIPTIVE ONLY, D98.9; "
          "nothing is decided):")
    s100.print_test("curve against the baseline, leads 25 to 48", d89_6(errs, "baseline", "curve", LEADS_B))
    print("\nSix-airport mean MAE per lead 25 to 48 (each airport pooled over folds and cycle hours):")
    print(f"  {'lead':>4} " + " ".join(f"{m:>9}" for m in METHODS))
    for n in LEADS_B:
        print(f"  {n:>4} " + " ".join(f"{sum(pooled(errs, m, st, None, (n,))[0] for st in STATIONS) / 6:>9.4f}"
                                       for m in METHODS))

    # The daily maximum
    print("\n" + "=" * 90)
    print("DAILY MAXIMUM (D98.10). BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C.")
    print("=" * 90)
    print("Cross-check: usable local days, session 90's hour_of and local_day_counts on the reports (session 96's "
          "load_obs), against the table's hourly observations:")
    all_days, drops_all = [], {}
    for st in STATIONS:
        r90, rt, same_hours = cross_check(st, obs_maps[st], s96, s90)
        agree = r90 == rt and same_hours
        print(f"  {st}: session 90 rule {r90}; table {rt}; hour sets equal {same_hours}; agree {agree}")
        if not agree:
            raise SystemExit(f"STOP: the usable-day cross-check differs at {st}")
        rows, drops = daily_max(st, obs_maps[st], fcs[st])
        all_days += rows
        for k, v in drops.items():
            drops_all[(st, k)] = v
    cols = ["station", "fold", "local_date", "hours", "usable_hours", "obs_max", "obs_reason", "cycle",
            "first_lead", "last_lead"] + [x for m in METHODS for x in (m + "_max", m + "_reason")] + ["common"]
    drows = []
    for r in all_days:
        drows.append([r["station"], r["fold"], r["local_date"], r["hours"], r["usable_hours"],
                      "" if r["obs_max"] is None else s97.fmt(r["obs_max"]), r["obs_reason"],
                      r["cycle"].strftime("%Y-%m-%dT%H:%MZ"), r["first_lead"], r["last_lead"]]
                     + [x for m in METHODS for x in ("" if r[m] is None else s97.fmt(r[m]), r[m + "_reason"])]
                     + ["true" if r["common"] else "false"])
    dtext = s97.csv_text(cols, drows)
    s97.write_new(DAYS_OUT, dtext)
    print(f"\nwrote {DAYS_OUT.relative_to(ROOT)}: {len(drows)} rows, SHA-256 "
          f"{hashlib.sha256(dtext.encode()).hexdigest()}")

    def dmae(st, m, folds=None):
        e = [r["obs_max"] - r[m] for r in all_days if r["station"] == st and r["common"]
             and (folds is None or r["fold"] in folds)]
        return s97.mae(e), len(e), s97.mean_error(e)

    print("\nPer airport, common day set, pooled over folds:")
    print(f"  {'airport':<7} {'days':>5} " + " ".join(f"{m:>9}" for m in METHODS) + "   mean error "
          + " ".join(f"{m:>9}" for m in METHODS))
    for st in STATIONS:
        print(f"  {st:<7} {dmae(st, 'baseline')[1]:>5} " + " ".join(f"{dmae(st, m)[0]:>9.4f}" for m in METHODS)
              + "              " + " ".join(f"{dmae(st, m)[2]:>+9.4f}" for m in METHODS))
    dh = {m: sum(dmae(st, m)[0] for st in STATIONS) / 6 for m in METHODS}
    print(f"  {'HEADLINE':<13} " + " ".join(f"{dh[m]:>9.4f}" for m in METHODS))
    print("  full precision: " + ", ".join(f"{m} {dh[m]!r}" for m in METHODS))
    print("Fold level (unweighted mean of the six airports' MAE over the fold's days):")
    for label, _, _ in FOLDS:
        print(f"  {label}: " + ", ".join(f"{m} {sum(dmae(st, m, [label])[0] for st in STATIONS) / 6:.4f}"
                                         for m in METHODS)
              + "; days " + ", ".join(f"{st} {dmae(st, 'baseline', [label])[1]}" for st in STATIONS))
    print("Cycle hours used (days in the common set, by cycle hour):")
    for st in STATIONS:
        ch = {}
        for r in all_days:
            if r["station"] == st and r["common"]:
                ch[r["cycle"].hour] = ch.get(r["cycle"].hour, 0) + 1
        print(f"  {st}: " + ", ".join(f"{h:02d}z {v}" for h, v in sorted(ch.items())))
    print("Days dropped, by reason:")
    for st in STATIONS:
        in_fold = [r for r in all_days if r["station"] == st]
        reasons = {}
        for r in in_fold:
            if r["obs_max"] is None:
                reasons["observed: " + r["obs_reason"]] = reasons.get("observed: " + r["obs_reason"], 0) + 1
            for m in METHODS:
                if r[m] is None:
                    reasons[m + ": no forecast at some hour"] = reasons.get(m + ": no forecast at some hour", 0) + 1
        not_common = sum(not r["common"] for r in in_fold)
        before = {k: v for (s, k), v in drops_all.items() if s == st}
        print(f"  {st}: local days in a fold {len(in_fold)}; not in the common set {not_common}; "
              f"{reasons or 'no other reason'}; outside the folds {before}")
    print("\nNo build choice is made. D98.10(g)'s incumbent for later daily-maximum build choices: the curve's "
          "read-off maximum.")
    print(f"\nend {now_utc()}; run time {time.time() - t_start:.1f} s; fits {fits}")


# ------------------------------------------------------------------ --meta

def run_meta(args):
    for p in (SCORES_OUT, DAYS_OUT):
        if not p.exists():
            raise SystemExit(f"STOP: {p} does not exist")
    hashes = table25_hashes()
    lines = [
        "session104_curve_cv.meta.txt",
        f"written {now_utc()} by scripts/session104_curve_cv.py --meta",
        "",
        "What the files are (BUILD-CHOICE SCORES, NOT RESULTS, SPEC 2.5):",
        "  session104_curve_cv_scores.csv: per method (raw_gfs, baseline, curve), airport, fold, cycle hour and",
        "    lead 3 to 48: n, MAE and mean error (obs_tmpc minus forecast), full precision; session 103's columns,",
        "    model repeats the method's name. Common row set (D89.5, D98.8). curve is session 103's drift.",
        "  session104_dailymax_days.csv: one row per airport and local day in a test fold (D98.10): hours in the",
        "    day, usable hours, observed maximum (or why none), the cycle and its first and last lead, the three",
        "    methods' forecast maxima (or why none), and whether the day is in the common day set.",
        "  baseline: D88.4, one model per airport, fold, cycle hour and lead; it also predicts test rows with",
        "    complete features and no observation (D98.7). curve: the baseline plus b, w = 0.02 (D97.4 to D97.7,",
        "    D98.5), session 103's track unchanged.",
        "",
        "Rules: DECISIONS D98 (D98.5 to D98.10), D97, D89.3, D89.5, D89.6.",
        "",
        "Inputs and their SHA-256:",
    ]
    for st in STATIONS:
        name, _ = s97.TABLES[st]
        lines.append(f"  MLwx-stagec/{name} {sha256_file(s97.STAGEC_DIR / name)}")
    for st in STATIONS:
        lines.append(f"  MLwx-stagec/{TABLE25[st]} {sha256_file(s97.STAGEC_DIR / TABLE25[st])} (meta: {hashes[st]})")
    for p in (TABLE25_META, s97.TRAINING_SET, s97.GRID, s100.S97_SCORES, S103_SCORES,
              HERE / "session103_bias_drift_cv.py", HERE / "session100_structure_cv.py",
              HERE / "session97_stagec_cv.py", s97.RECORD_SCRIPT, HERE / "session96_stagec_table.py", S90_SCRIPT):
        lines.append(f"  {p.relative_to(ROOT)} {sha256_file(p)}")
    lines += [
        "",
        f"Script: scripts/session104_curve_cv.py {sha256_file(SCRIPT)}",
        "",
        "Outputs and their SHA-256:",
        f"  {SCORES_OUT.relative_to(ROOT)} {sha256_file(SCORES_OUT)}",
        f"  {DAYS_OUT.relative_to(ROOT)} {sha256_file(DAYS_OUT)}",
        "",
        f"LGB_PARAMS as passed (from session 97, which takes them from scripts/session62_reserved_confirm.py): "
        f"{LGB_PARAMS}",
        f"G15 column order (same source): {s97.G15}",
        f"w: {W}",
        f"Fit counts: {args.fit_counts}. No model saved.",
        f"Run times (as printed by the runs): {args.run_times}",
        f"Versions: {versions()}",
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
        run_gate(args)
    elif args.score:
        run_score(args)
    else:
        run_meta(args)


if __name__ == "__main__":
    main()
