"""Session 97: stage C cross-validation of the curve's baseline (D88.4) under
D89's folds, metric and rule. Offline. Build-choice scores only, never results
(SPEC 2.5). No build choice is made here: only D88.4's baseline is fit, with
the record's settings.

Modes (one per run):
  --folds        count each model's training, test and boundary rows (D89.3);
                 no fit. Writes data/processed/session97_stagec_cv_folds.csv.
  --gate         D89.9: refit F109's fold at EGLC and LFPG (12z, lead 24) and
                 DSM (18z, lead 24) from the table's rows, and compare the raw
                 GFS and B+D,L,R,T MAEs with the stored grid, exact equality.
  --score        fit one baseline model per airport, fold, cycle hour and lead
                 3 to 24, and score it and raw GFS on the same rows (D89.5).
                 Writes data/processed/session97_stagec_cv_scores.csv, or the
                 same file under --out-dir. --airports limits the airports.
  --guard-check  the 2026-27 guard, on two made-up valid times (no data read).
  --meta         write data/processed/session97_stagec_cv.meta.txt.

Inputs, read only: the six table files in MLwx-stagec/ (F138.4),
data/processed/session81_training_set.csv (F122.3, for --gate),
data/processed/session63_reserved_confirm_grid.csv (F109, for --gate), and,
imported read only after its SHA-256 check (D70.2), LGB_PARAMS and the G15
column order from scripts/session62_reserved_confirm.py, as session 81 did
(F122.2). That record script imports the session-48 reserved-year module for
its own use; this script never calls its guard (D89.4).

Fit as the record does (SPEC 8.8): G15 columns in order, float64, no column
names (G15); target obs_tmpc - temp, unrounded (G20); training rows in
ascending cycle time (G19); lgb.LGBMRegressor(**LGB_PARAMS).fit(x, y) (G14,
G17). The forecast is temp plus the model's output. Error is obs_tmpc minus
the forecast. MAE is the NumPy mean of the absolute errors (G24).

Output files are written once and never overwritten (SPEC 8.7 item 5).
"""

import hashlib
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RECORD_SCRIPT = HERE / "session62_reserved_confirm.py"
RECORD_SCRIPT_SHA256 = "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4"   # D70.2


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


# The record script's SHA-256 is checked before it is imported. Importing it
# also runs its libomp loader shim, which lightgbm needs on this machine.
if sha256_file(RECORD_SCRIPT) != RECORD_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session62_reserved_confirm.py's SHA-256 is not D70.2's")
sys.path.insert(0, str(HERE))
import session62_reserved_confirm as rec  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import io  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

# ------------------------------------------------------------------ constants

STAGEC_DIR = ROOT.parent / "MLwx-stagec"
PROCESSED = ROOT / "data" / "processed"
TRAINING_SET = PROCESSED / "session81_training_set.csv"
TRAINING_SET_SHA256 = "ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a"   # F122.3
GRID = PROCESSED / "session63_reserved_confirm_grid.csv"
GRID_SHA256 = "0138ba039d0bd077e71b829789a8d3c93175e22493ed115f7503b2baa30f4ed3"   # notes/session-85-output.txt
FOLDS_OUT = PROCESSED / "session97_stagec_cv_folds.csv"
SCORES_NAME = "session97_stagec_cv_scores.csv"
SCORES_OUT = PROCESSED / SCORES_NAME
META_OUT = PROCESSED / "session97_stagec_cv.meta.txt"
SCRIPT = Path(__file__).resolve()

# SPEC 3.4 station code -> (table file, its SHA-256 in F138.4). SPEC order.
TABLES = {
    "EGLC": ("stagec_dev_EGLC.csv.gz", "af8848e091c79aecac5f809536e4dec20757d288f7ebc1cf3e830d33a69c9126"),
    "LFPG": ("stagec_dev_LFPG.csv.gz", "5b113123c7642eefb8d212cbe5151f43e8ba343a231dc90d4461ed104e6b661f"),
    "DSM": ("stagec_dev_KDSM.csv.gz", "17461736cd23585781ebf01a842469a1ea6b0e93571bea250869a23271dc0e32"),
    "YSDU": ("stagec_dev_YSDU.csv.gz", "57a11a4f00250304f289de158223eff45f841d572e3c3c7f65e5b6fc6c0fa829"),
    "RNO": ("stagec_dev_KRNO.csv.gz", "6e2d0779f6b5ea92dc77e3b074030ac3676bd90cffe3b44ab6e3441c06831ec3"),
    "SFO": ("stagec_dev_KSFO.csv.gz", "11fa6385f05c57cf627734d9caed13927f1e176e07c5fc039f700d30fd1ceff8"),
}
STATIONS = list(TABLES)

TABLE_COLUMNS = ["station", "cycle_utc", "cycle_hour", "lead", "valid_utc", "temp", "temperature_grib_c",
                 "t2m_raw", "cloud_cover", "wind_speed_10m", "dew_point_2m", "t850",
                 "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850", "dswrf_2h_wm2",
                 "pressure_tendency_3h_hpa", "season_sin", "season_cos", "tmax2m_c", "tmin2m_c", "obs_tmpc",
                 "obs_time_utc", "uses_whole_file", "complete_case"]

# G15, imported from the record script, and checked against D70.1's list.
G15 = list(rec.FINAL_FEATURE_KEYS)
G15_D70 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m", "dewpoint_depression_t2m_floored",
           "lapse_rate_t2_t850", "dswrf_2h_wm2", "pressure_tendency_3h_hpa"]
if G15 != G15_D70:
    raise SystemExit("STOP: the record script's G15 order is not D70.1's")
LGB_PARAMS = dict(rec.LGB_PARAMS)

CYCLE_HOURS = (0, 6, 12, 18)
LEADS = tuple(range(3, 25))     # D89.5: leads 3 to 24
METHODS = ("raw_gfs", "baseline")

# D89.3: three time-ordered folds. T0 is the test year's start (1 August,
# 00:00 UTC); the test year ends at the next 1 August, 00:00 UTC.
FOLDS = [
    ("2023-24", dt.datetime(2023, 8, 1), dt.datetime(2024, 8, 1)),
    ("2024-25", dt.datetime(2024, 8, 1), dt.datetime(2025, 8, 1)),
    ("2025-26", dt.datetime(2025, 8, 1), dt.datetime(2026, 8, 1)),
]

LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)     # nothing valid after this is read or scored
LAST_OBS = dt.datetime(2026, 7, 31, 23, 59)      # no observation after this is read

# D89.9: F109's fold, by valid date, at the record's cycle hour and lead.
GATE = [("EGLC", 12, 24), ("LFPG", 12, 24), ("DSM", 18, 24)]
GATE_TRAIN = (dt.date(2021, 3, 24), dt.date(2024, 7, 31))
GATE_TEST = (dt.date(2024, 8, 1), dt.date(2025, 7, 31))
# F109 (DECISIONS-archive.md): n_test per airport, and F122.4's training rows.
F109_N_TEST = {"EGLC": 364, "LFPG": 365, "DSM": 365}
F122_N_TRAIN = {"EGLC": 1225, "LFPG": 1224, "DSM": 1225}


class GuardError(Exception):
    pass


# ------------------------------------------------------------------ helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


def parse_time(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")


def check_valid(valid):
    """The 2026-27 guard: refuse any valid time after 2026-07-31T23:00 UTC."""
    if valid > LAST_VALID:
        raise GuardError(f"valid time {valid:%Y-%m-%dT%H:%M} is after {LAST_VALID:%Y-%m-%dT%H:%M} UTC")


def check_obs_time(t):
    if t > LAST_OBS:
        raise GuardError(f"observation at {t:%Y-%m-%dT%H:%M} is after {LAST_OBS:%Y-%m-%dT%H:%M} UTC")


def mae(errors):
    """G24: the NumPy mean of the absolute errors, full precision."""
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


def mean_error(errors):
    return float(np.mean(np.asarray(errors, dtype=float)))


def fval(s):
    return float(s) if s != "" else None


def write_new(path, text):
    """Write once: a temporary name, then a hard link to the final name, which never overwrites."""
    path = Path(path)
    if path.exists():
        raise SystemExit(f"STOP: {path} already exists; not overwriting it")
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "x", newline="") as f:
        f.write(text)
        f.flush()
        os.fsync(f.fileno())
    os.link(tmp, path)
    os.unlink(tmp)


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def fmt(v):
    return repr(v) if isinstance(v, float) else str(v)


# ------------------------------------------------------------------ the table

def load_table(st, leads=LEADS):
    """Rows of one airport's table at the given leads, in file order (cycle, then lead).

    Each row: (cycle, valid, cycle_hour, lead, complete, obs, temp, x), where x
    is the nine G15 values (None where empty). The file's SHA-256 is checked
    against F138.4 first. Every valid time and observation time passes the
    2026-27 guard, and complete_case is checked against the nine columns and
    the observation."""
    name, want = TABLES[st]
    path = STAGEC_DIR / name
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"STOP: {name} SHA-256 {got} is not F138.4's {want}")
    lead_set = set(leads)
    rows = []
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != TABLE_COLUMNS:
            raise SystemExit(f"STOP: {name} header is not F138.4's")
        ix = {c: i for i, c in enumerate(head)}
        gi = [ix[c] for c in G15]
        for r in rd:
            if r[ix["station"]] != st:
                raise SystemExit(f"STOP: {name} holds a row for station {r[ix['station']]}")
            valid = parse_time(r[ix["valid_utc"]])
            check_valid(valid)
            if r[ix["obs_time_utc"]]:
                check_obs_time(parse_time(r[ix["obs_time_utc"]]))
            lead = int(r[ix["lead"]])
            if lead not in lead_set:
                continue
            cycle = parse_time(r[ix["cycle_utc"]])
            x = [fval(r[i]) for i in gi]
            obs = fval(r[ix["obs_tmpc"]])
            complete = r[ix["complete_case"]] == "true"
            if complete != (all(v is not None for v in x) and obs is not None):
                raise SystemExit(f"STOP: {name} complete_case disagrees with its columns at {r[ix['cycle_utc']]} "
                                 f"lead {lead}")
            if x[0] is not None and float(r[ix["temperature_grib_c"]]) != x[0]:
                raise SystemExit(f"STOP: {name} temp differs from temperature_grib_c")
            rows.append((cycle, valid, int(r[ix["cycle_hour"]]), lead, complete, obs, x[0], x))
    return rows


def fold_role(cycle, valid, t0, t1):
    """D89.3: 'train' if valid < T0; 'test' if T0 <= cycle < T1; 'boundary' if
    cycle < T0 <= valid; None otherwise (a cycle on or after T1)."""
    if valid < t0:
        return "train"
    if t0 <= cycle < t1:
        return "test"
    if cycle < t0:
        return "boundary"
    return None


def fit_predict(train, test):
    """train, test: lists of (x, temp, obs), train in ascending time. Returns
    the model's forecast (temp plus the model's output) for each test row."""
    x = np.array([r[0] for r in train], dtype=float)
    y = np.array([r[2] - r[1] for r in train], dtype=float)
    m = lgb.LGBMRegressor(**LGB_PARAMS)
    m.fit(x, y)
    pred = m.predict(np.array([r[0] for r in test], dtype=float))
    return [r[1] + float(pred[i]) for i, r in enumerate(test)]


# ------------------------------------------------------------------ --folds (Step 2)

def run_folds(args):
    t_start = time.time()
    print(f"SESSION 97 --folds (offline, no fit), start {now_utc()}")
    print(f"versions: {versions()}")
    print("D89.3: train = complete-case rows with valid < T0; test = rows with T0 <= cycle < T1; "
          "boundary = rows with cycle < T0 <= valid (in neither, counted).")
    for label, t0, t1 in FOLDS:
        print(f"  fold {label}: T0 {t0:%Y-%m-%dT%H:%MZ}, T1 {t1:%Y-%m-%dT%H:%MZ}")
    out_rows = []
    summary = []
    problems = 0
    for st in STATIONS:
        rows = load_table(st)
        test_keys = {}
        for label, t0, t1 in FOLDS:
            cells = {(h, n): [0, 0, 0, 0] for h in CYCLE_HOURS for n in LEADS}
            keys = set()
            for cycle, valid, h, n, complete, obs, temp, x in rows:
                role = fold_role(cycle, valid, t0, t1)
                c = cells[(h, n)]
                if role == "train":
                    if complete:
                        c[0] += 1
                        if not valid < t0:
                            problems += 1
                elif role == "test":
                    if complete:
                        c[1] += 1
                        keys.add((cycle, n))
                    else:
                        c[2] += 1
                elif role == "boundary":
                    c[3] += 1
            test_keys[label] = keys
            for (h, n), c in cells.items():
                out_rows.append([st, label, h, n] + c)
            tr = [c[0] for c in cells.values()]
            summary.append((st, label, sum(tr), sum(c[1] for c in cells.values()),
                            sum(c[2] for c in cells.values()), sum(c[3] for c in cells.values()), min(tr),
                            min(cells, key=lambda k: (cells[k][0], k))))
        labels = [f[0] for f in FOLDS]
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                both = test_keys[labels[i]] & test_keys[labels[j]]
                if both:
                    problems += 1
                    print(f"  OVERLAP: {st} folds {labels[i]} and {labels[j]} share {len(both)} test rows")
        print(f"  {st}: test-row overlap between folds: "
              f"{sum(len(test_keys[a] & test_keys[b]) for a in labels for b in labels if a < b)}")
    print("\nper airport and fold (complete-case rows, leads 3 to 24, all four cycle hours):")
    print(f"  {'airport':<7} {'fold':<8} {'train':>8} {'test':>7} {'test dropped':>13} {'boundary':>9} "
          f"{'smallest model train':>21}  (cycle hour, lead)")
    for st, label, tr, te, dropped, bd, mn, cell in summary:
        print(f"  {st:<7} {label:<8} {tr:>8,} {te:>7,} {dropped:>13,} {bd:>9,} {mn:>21,}  {cell}")
    print(f"\nchecks: every training row's valid time is before its fold's T0 (violations {problems if problems else 0}); "
          "test rows of the three folds never overlap (see per-airport lines)")
    if problems:
        raise SystemExit(f"STOP: {problems} fold check failures")
    header = ["station", "fold", "cycle_hour", "lead", "train_rows", "test_rows", "test_dropped_not_complete",
              "boundary_rows"]
    text = csv_text(header, out_rows)
    out = Path(args.out) if args.out else FOLDS_OUT
    write_new(out, text)
    print(f"\nwrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}: {len(out_rows)} rows, "
          f"{len(text.encode())} bytes, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    print(f"end {now_utc()}; run time {time.time() - t_start:.1f} s")


# ------------------------------------------------------------------ --gate (Step 3)

def run_gate(args):
    t_start = time.time()
    print(f"SESSION 97 --gate (D89.9; offline), start {now_utc()}")
    print(f"versions: {versions()}")
    print(f"record script SHA-256 checked before import: {RECORD_SCRIPT_SHA256} (D70.2)")
    for path, want in ((TRAINING_SET, TRAINING_SET_SHA256), (GRID, GRID_SHA256)):
        got = sha256_file(path)
        print(f"{path.relative_to(ROOT)} SHA-256 {got} ({'equal' if got == want else 'NOT EQUAL'} to the record)")
        if got != want:
            raise SystemExit("STOP: input SHA-256")
    print(f"G15 (from the record script): {G15}")
    print(f"LGB_PARAMS (from the record script): {LGB_PARAMS}")
    keys = {}
    with open(TRAINING_SET, newline="") as f:
        for r in csv.DictReader(f):
            keys.setdefault(r["station"], set()).add(dt.date.fromisoformat(r["target_date"]))
    grid = {}
    with open(GRID, newline="") as f:
        for r in csv.DictReader(f):
            grid[r["station"]] = r
    all_equal = True
    for st, hour, lead in GATE:
        rows = load_table(st, leads=(lead,))
        sel = [r for r in rows if r[2] == hour and r[1].date() in keys.get(st, set())]
        sel.sort(key=lambda r: r[0])
        not_complete = [r for r in sel if not r[4]]
        train = [(r[7], r[6], r[5]) for r in sel if GATE_TRAIN[0] <= r[1].date() <= GATE_TRAIN[1] and r[4]]
        test = [(r[7], r[6], r[5]) for r in sel if GATE_TEST[0] <= r[1].date() <= GATE_TEST[1] and r[4]]
        fc = fit_predict(train, test)
        e_model = [r[2] - fc[i] for i, r in enumerate(test)]
        e_raw = [r[2] - r[1] for r in test]
        m_model, m_raw = mae(e_model), mae(e_raw)
        g = grid[st]
        rec_final, rec_raw = float(g["final_mae"]), float(g["raw_mae"])
        eq_final, eq_raw = m_model == rec_final, m_raw == rec_raw
        all_equal &= eq_final and eq_raw
        print(f"\n{st} (cycle hour {hour:02d}z, lead {lead}): table rows on the training set's dates "
              f"{len(sel)} (not complete case {len(not_complete)}); train {len(train)} "
              f"(F122.4 {F122_N_TRAIN[st]}); test {len(test)} (F109 n_test {F109_N_TEST[st]}; grid no_obs "
              f"{g['no_obs']})")
        print(f"  B+D,L,R,T  this fit {m_model!r}  grid final_mae {g['final_mae']}  equal: {'yes' if eq_final else 'NO'}")
        print(f"  raw GFS    this fit {m_raw!r}  grid raw_mae   {g['raw_mae']}  equal: {'yes' if eq_raw else 'NO'}")
        print(f"  at 4 decimals: B+D,L,R,T {m_model:.4f}, raw GFS {m_raw:.4f}")
        if len(test) != F109_N_TEST[st] or len(train) != F122_N_TRAIN[st]:
            print("  ROW COUNT DIFFERS from the record (reported; a stop only if an MAE also differs)")
    print(f"\nGATE {'PASSED: all six values equal, exact equality' if all_equal else 'FAILED'}")
    print(f"end {now_utc()}; run time {time.time() - t_start:.1f} s")
    if not all_equal:
        raise SystemExit(1)


# ------------------------------------------------------------------ --score (Step 4)

def score_airport(st):
    """Per fold, cycle hour and lead: fit one baseline model and score it and
    raw GFS on the same test rows. Returns {(fold, h, n): (obs list, raw fc, baseline fc)}."""
    rows = load_table(st)
    out = {}
    for label, t0, t1 in FOLDS:
        by_cell_train = {(h, n): [] for h in CYCLE_HOURS for n in LEADS}
        by_cell_test = {(h, n): [] for h in CYCLE_HOURS for n in LEADS}
        for cycle, valid, h, n, complete, obs, temp, x in rows:
            if not complete:
                continue
            role = fold_role(cycle, valid, t0, t1)
            if role == "train":
                if not valid < t0:
                    raise SystemExit("STOP: a training row is not before T0")
                by_cell_train[(h, n)].append((cycle, x, temp, obs))
            elif role == "test":
                by_cell_test[(h, n)].append((cycle, x, temp, obs))
        for h in CYCLE_HOURS:
            for n in LEADS:
                tr = sorted(by_cell_train[(h, n)], key=lambda r: r[0])
                te = sorted(by_cell_test[(h, n)], key=lambda r: r[0])
                if not tr or not te:
                    raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: train {len(tr)}, test {len(te)}")
                if tr[-1][0] >= te[0][0] or max(r[0] for r in tr) + dt.timedelta(hours=n) >= t0:
                    raise SystemExit(f"STOP: {st} {label} {h}z lead {n}: training not before test")
                fc = fit_predict([(r[1], r[2], r[3]) for r in tr], [(r[1], r[2], r[3]) for r in te])
                out[(label, h, n)] = ([r[3] for r in te], [r[2] for r in te], fc, len(tr))
    return out


def run_score(args):
    t_start = time.time()
    stations = args.airports.split(",") if args.airports else STATIONS
    if any(s not in STATIONS for s in stations):
        raise SystemExit(f"STOP: unknown airport in {args.airports}")
    out_dir = Path(args.out_dir) if args.out_dir else PROCESSED
    out_path = out_dir / SCORES_NAME
    if out_path.exists():
        raise SystemExit(f"STOP: {out_path} already exists; not overwriting it")
    print(f"SESSION 97 --score (offline), start {now_utc()}; airports {','.join(stations)}; out {out_path}")
    print(f"versions: {versions()}")
    print(f"G15: {G15}")
    print(f"LGB_PARAMS: {LGB_PARAMS}")
    print("BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5).")
    cells = {}
    fits = 0
    for st in stations:
        t_st = time.time()
        res = score_airport(st)
        for k, v in res.items():
            cells[(st,) + k] = v
        fits += len(res)
        print(f"  {st}: {len(res)} models fit, {time.time() - t_st:.1f} s")
    rows = []
    n_unequal = 0
    errs = {}
    for st in stations:
        for label, _, _ in FOLDS:
            for h in CYCLE_HOURS:
                for n in LEADS:
                    obs, raw, base, n_train = cells[(st, label, h, n)]
                    e = {"raw_gfs": [o - raw[i] for i, o in enumerate(obs)],
                         "baseline": [o - base[i] for i, o in enumerate(obs)]}
                    if len(e["raw_gfs"]) != len(e["baseline"]):
                        n_unequal += 1
                    for meth in METHODS:
                        errs[(st, label, h, n, meth)] = e[meth]
                        rows.append([st, label, h, n, meth, len(e[meth]), mae(e[meth]), mean_error(e[meth])])
    header = ["station", "fold", "cycle_hour", "lead", "method", "n", "mae", "mean_error"]
    text = csv_text(header, [[fmt(v) for v in r] for r in rows])
    out_dir.mkdir(parents=True, exist_ok=True)
    write_new(out_path, text)
    print(f"\nfits: {fits}; cells where the two methods' n differ: {n_unequal}")
    print(f"wrote {out_path}: {len(rows)} rows, {len(text.encode())} bytes, "
          f"SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    if n_unequal:
        raise SystemExit("STOP: the two methods' n differ in some cell")
    if stations == STATIONS:
        summarise(errs)
    print(f"\nend {now_utc()}; run time {time.time() - t_start:.1f} s")


def pooled(errs, meth, st, folds=None, hours=None, leads=None):
    """One MAE over the concatenated errors, in fold, cycle hour, lead, then row order."""
    e = []
    for label, _, _ in FOLDS:
        if folds and label not in folds:
            continue
        for h in CYCLE_HOURS:
            if hours and h not in hours:
                continue
            for n in LEADS:
                if leads and n not in leads:
                    continue
                e.extend(errs[(st, label, h, n, meth)])
    return mae(e), len(e)


def summarise(errs):
    print("\n" + "=" * 90)
    print("SUMMARY. BUILD-CHOICE SCORES, NOT RESULTS (SPEC 2.5). MAE in degrees C, 4 decimals.")
    print("Common row set: complete-case test rows (D89.5). raw_gfs = temp; baseline = temp + model.")
    print("=" * 90)
    print("\nPer airport, pooled over the three folds, four cycle hours and leads 3 to 24 (D89.5):")
    print(f"  {'airport':<7} {'n':>8} {'raw_gfs':>8} {'baseline':>9}")
    head = {}
    for st in STATIONS:
        r, n = pooled(errs, "raw_gfs", st)
        b, _ = pooled(errs, "baseline", st)
        head[st] = (r, b)
        print(f"  {st:<7} {n:>8,} {r:>8.4f} {b:>9.4f}")
    hr = sum(v[0] for v in head.values()) / len(STATIONS)
    hb = sum(v[1] for v in head.values()) / len(STATIONS)
    print(f"  HEADLINE (unweighted mean of the six airport MAEs): raw_gfs {hr:.4f}  baseline {hb:.4f}")
    print(f"  (full precision: raw_gfs {hr!r}, baseline {hb!r})")

    print("\nPer fold: each airport's MAE over that fold's rows, and the fold-level MAE (unweighted mean of six):")
    print(f"  {'fold':<8} {'method':<9} " + " ".join(f"{s:>7}" for s in STATIONS) + f" {'fold-level':>11}")
    for label, _, _ in FOLDS:
        for meth in METHODS:
            vals = [pooled(errs, meth, st, folds=[label])[0] for st in STATIONS]
            print(f"  {label:<8} {meth:<9} " + " ".join(f"{v:>7.4f}" for v in vals)
                  + f" {sum(vals) / len(vals):>11.4f}")
    print("  rows per airport and fold: " + "; ".join(
        f"{st} " + "/".join(f"{pooled(errs, 'raw_gfs', st, folds=[lb])[1]:,}" for lb, _, _ in FOLDS)
        for st in STATIONS))

    print("\nSix-airport mean MAE per lead (each airport pooled over folds and cycle hours; unweighted mean of six):")
    print(f"  {'lead':>4} {'raw_gfs':>8} {'baseline':>9}")
    for n in LEADS:
        r = sum(pooled(errs, "raw_gfs", st, leads=[n])[0] for st in STATIONS) / len(STATIONS)
        b = sum(pooled(errs, "baseline", st, leads=[n])[0] for st in STATIONS) / len(STATIONS)
        print(f"  {n:>4} {r:>8.4f} {b:>9.4f}")

    print("\nSix-airport mean MAE per cycle hour (each airport pooled over folds and leads 3 to 24):")
    print(f"  {'hour':>4} {'raw_gfs':>8} {'baseline':>9}")
    for h in CYCLE_HOURS:
        r = sum(pooled(errs, "raw_gfs", st, hours=[h])[0] for st in STATIONS) / len(STATIONS)
        b = sum(pooled(errs, "baseline", st, hours=[h])[0] for st in STATIONS) / len(STATIONS)
        print(f"  {h:>2}z  {r:>8.4f} {b:>9.4f}")

    print("\nPer airport, the leads where the baseline's MAE is not below raw GFS's (pooled over folds and cycle hours):")
    for st in STATIONS:
        bad = []
        for n in LEADS:
            r = pooled(errs, "raw_gfs", st, leads=[n])[0]
            b = pooled(errs, "baseline", st, leads=[n])[0]
            if not b < r:
                bad.append(f"lead {n} (raw_gfs {r:.4f}, baseline {b:.4f})")
        print(f"  {st}: {', '.join(bad) if bad else 'none'}")

    print("\nPer airport and lead (pooled over folds and cycle hours), raw_gfs / baseline:")
    print(f"  {'lead':>4} " + " ".join(f"{s:>15}" for s in STATIONS))
    for n in LEADS:
        cells = []
        for st in STATIONS:
            r = pooled(errs, "raw_gfs", st, leads=[n])[0]
            b = pooled(errs, "baseline", st, leads=[n])[0]
            cells.append(f"{r:.4f}/{b:.4f}")
        print(f"  {n:>4} " + " ".join(f"{c:>15}" for c in cells))


# ------------------------------------------------------------------ --guard-check (Step 5.2)

def run_guard_check(args):
    print(f"SESSION 97 --guard-check (no data read), {now_utc()}")
    cases = [(dt.datetime(2026, 8, 1, 0, 0), False), (dt.datetime(2026, 7, 31, 23, 0), True)]
    ok = 0
    for t, allowed in cases:
        try:
            check_valid(t)
            got = True
            why = ""
        except GuardError as e:
            got = False
            why = f" ({e})"
        good = got == allowed
        ok += good
        print(f"  valid {t:%Y-%m-%dT%H:%M}: {'allowed' if got else 'refused'}{why}; expected "
              f"{'allowed' if allowed else 'refused'}: {'as expected' if good else 'NOT AS EXPECTED'}")
    print(f"{ok} of {len(cases)} as expected")
    if ok != len(cases):
        raise SystemExit(1)


# ------------------------------------------------------------------ --meta (Step 5.3)

def run_meta(args):
    for p in (FOLDS_OUT, SCORES_OUT):
        if not p.exists():
            raise SystemExit(f"STOP: {p} does not exist")
    lines = [
        "session97_stagec_cv.meta.txt",
        f"written {now_utc()} by scripts/session97_stagec_cv.py --meta",
        "",
        "What the files are (BUILD-CHOICE SCORES, NOT RESULTS, SPEC 2.5):",
        "  session97_stagec_cv_folds.csv: per airport, fold, cycle hour (0, 6, 12, 18) and lead (3 to 24),",
        "    training rows (complete case), test rows (complete case), test rows dropped as not complete case,",
        "    and rows in neither (the boundary rule), under DECISIONS D89.3. No fit.",
        "  session97_stagec_cv_scores.csv: per airport, fold, cycle hour, lead and method (raw_gfs, baseline),",
        "    n, MAE and mean error (obs_tmpc minus forecast), full precision. raw_gfs is temp, the",
        "    elevation-adjusted GRIB temperature; baseline is temp plus D88.4's model, one model per airport,",
        "    fold, cycle hour and lead (1,584 fits).",
        "",
        "Folds, metric and rule: DECISIONS D89.3 (folds), D89.5 (metric), D89.6 (rule; not applied here, no",
        "  build choice is made), D89.9 (the gate, F139).",
        "",
        "Inputs and their SHA-256:",
    ]
    for st in STATIONS:
        name, want = TABLES[st]
        lines.append(f"  MLwx-stagec/{name} {sha256_file(STAGEC_DIR / name)}")
    for p in (TRAINING_SET, GRID, RECORD_SCRIPT):
        lines.append(f"  {p.relative_to(ROOT)} {sha256_file(p)}")
    lines += [
        "",
        f"Script: scripts/session97_stagec_cv.py {sha256_file(SCRIPT)}",
        "",
        "Outputs and their SHA-256:",
        f"  {FOLDS_OUT.relative_to(ROOT)} {sha256_file(FOLDS_OUT)}",
        f"  {SCORES_OUT.relative_to(ROOT)} {sha256_file(SCORES_OUT)}",
        "",
        f"LGB_PARAMS as passed (imported from scripts/session62_reserved_confirm.py): {LGB_PARAMS}",
        f"G15 column order (imported from the same script): {G15}",
        f"Versions: {versions()}",
    ]
    text = "\n".join(lines) + "\n"
    write_new(META_OUT, text)
    print(text)
    print(f"wrote {META_OUT.relative_to(ROOT)}, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--folds", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    g.add_argument("--guard-check", action="store_true")
    g.add_argument("--meta", action="store_true")
    ap.add_argument("--airports", help="--score only: comma-separated SPEC 3.4 codes (default: all six)")
    ap.add_argument("--out-dir", help="--score only: directory for the scores file (default data/processed)")
    ap.add_argument("--out", help="--folds only: path for the folds file (default data/processed)")
    args = ap.parse_args()
    if args.folds:
        run_folds(args)
    elif args.gate:
        run_gate(args)
    elif args.score:
        run_score(args)
    elif args.guard_check:
        run_guard_check(args)
    elif args.meta:
        run_meta(args)


if __name__ == "__main__":
    main()
