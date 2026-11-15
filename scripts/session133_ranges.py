"""Session 133: stage H's first build choice, a central 80 % range for each forecast (DECISIONS D128).
Offline. Build-choice scores only, never results (SPEC 2.5). Data: the six development airports only
(EGLC, LFPG, KDSM, YSDU, KRNO, KSFO); nothing valid after 2026-07-31T23:00 UTC; no claim-airport file.

Modes (one per run):
  --gate   (a) with this script's own training-row loader, refit the baseline (LGB_PARAMS unchanged) at
           each development airport, fold 2025-26, cycle hour 12, leads 24 and 36; its predictions on
           that cell's test rows must equal the prediction file's `baseline` at full precision, row for
           row (this proves Q's rows, inputs and order). (b) every scored row of the six prediction
           files in the three test years has finite obs, curve, raw_gfs and b, and the counts per
           airport and period equal meta.txt's. (c) the daily-maximum file's `common` rows per airport
           and fold, reported. Writes nothing.
  --score  the gate again, then D128.5 to D128.9: the candidates, the rule, the descriptive figures,
           and the winners' coverage intervals. Writes data/processed/session133_ranges/ (a new folder,
           written once, only after every value is computed) with a meta file.

Imported read only, each after its SHA-256 is checked equal to HEAD's blob (D116.10, session 133's
Step 1): scripts/session97_stagec_cv.py, scripts/session104_curve_cv.py and
scripts/session112_analysis.py (which itself checks and imports session 106, and through it
sessions 104, 103, 100 and 97). Used from session 97: load_table, fit_predict, parse_time, fmt,
csv_text, FOLDS, CYCLE_HOURS, LGB_PARAMS, G15, LAST_VALID; from session 104: load_table25,
table25_hashes, split_rows_leads, LEADS_A, LEADS_B, LEADS_ALL, DAYS_OUT; from session 112:
load_pred_rows (its SHA-256 check against meta.txt), PRED_COLUMNS, PRED_META, DEV_ICAO, STATION,
S104_DAYS_SHA256, block_weights, ratio_interval, write_once_text, BLOCK, BANDS, SEASON_OF, SEASONS.
No function of theirs is changed. For Q, session 97's module constant LGB_PARAMS is set at run time to
a copy with objective "quantile" and alpha 0.1 or 0.9, session 97's fit_predict is called unchanged,
and the constant is put back (D128.6; the prompt's rule that a wrapper may set a module constant).

Readings fixed here, before --score runs (D128 leaves them open):
  1. D128.6's "15 recipe inputs in G15's order" is read as the recipe's inputs in SPEC 8.8 G15's list,
     which has nine columns (session 97's G15); gate (a) proves they are the baseline's.
  2. Q: l = raw_gfs + q0.1 + b is computed as fit_predict's output (raw_gfs + q0.1, since temp is
     raw_gfs) plus b, left to right as written. The swap is decided on those values: where
     raw_gfs + q0.1 > raw_gfs + q0.9 the pair is swapped and counted.
  3. Pooled coverage (D128.8 (iv)): the share of all rows of the six airports in that period
     (rows pooled), not the mean of six shares. The rule's headline is the mean of the six airport
     values (D128.5); (ii) compares each airport's mean over both scoring periods' rows; all
     comparisons are strict, so a tie fails the challenger. (iv) is inclusive: 0.75 <= c <= 0.85.
  4. Season is the month of `local_date` (hourly) or of the local day (daily maximum), by session
     112's SEASON_OF. Lead bands are session 112's BANDS.
  5. Tables: numpy.percentile(e, [10, 90]) (linear) per cell, from the rows whose period is earlier
     than the scoring period (2024-25 from 2023-24; 2025-26 from 2023-24 and 2024-25). A cell with
     no earlier row stops the run.
  6. Terciles (D128.9) for the hourly output only: D128.9 defines the run-to-run change per valid
     hour, and cloud cover is an hourly input; the daily maximum has neither per day. Edges per
     airport and scoring period from the earlier periods' scored rows, numpy.quantile at 1/3 and
     2/3 (linear). Level: low if v <= first edge, mid if v <= second edge, else high; except that
     where the second edge equals the earlier rows' largest value (cloud cover's 100 %), high is
     v >= second edge, so the top tercile is not left empty by ties. The earlier
     partner of a row (cycle c, lead L) is the prediction file's row at cycle c - 6 h, lead L + 6
     (so L + 6 <= 48), the same valid time, with a raw_gfs value, of any status or period. Rows with
     none are counted per airport and period and left out of the change terciles only.
  7. Breakdowns by cycle hour use the row's cycle hour (hourly) or the day's cycle (daily maximum).
     Breakdowns are per airport and for all six airports' rows pooled, per scoring period.
  8. The winners' coverage intervals: F125.3's moving-block bootstrap (session 112's block_weights,
     blocks of 7 days), 10,000 resamples, one generator numpy.random.default_rng(133), drawn in the
     order hourly then daily maximum, airports EGLC, LFPG, KDSM, YSDU, KRNO, KSFO, periods 2024-25
     then 2025-26; the resampled unit is the day (hourly: the cycle's UTC date, as session 112;
     daily maximum: the local day), in date order; coverage is sum(inside) / sum(rows) over the
     drawn days (session 112's ratio_interval); 2.5th and 97.5th percentiles. An output with no
     winner draws nothing.
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


# Session 133's Step 1: each equal to HEAD's blob at 38cf1b7. Checked before any import.
IMPORTED_SHA256 = {
    "session97_stagec_cv.py": "987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91",
    "session104_curve_cv.py": "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb",
    "session112_analysis.py": "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab",
}
for _name, _want in IMPORTED_SHA256.items():
    if sha256_file(HERE / _name) != _want:
        raise SystemExit(f"STOP: scripts/{_name}'s SHA-256 is not session 133's recorded value")
sys.path.insert(0, str(HERE))
import session112_analysis as s112  # noqa: E402

import argparse  # noqa: E402
import contextlib  # noqa: E402
import datetime as dt  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

s104 = s112.s104
s97 = s112.s97
for _mod, _name in ((s97, "session97_stagec_cv.py"), (s104, "session104_curve_cv.py")):
    if Path(_mod.__file__).resolve() != HERE / _name:
        raise SystemExit(f"STOP: {_name} was imported from {_mod.__file__}")

# ------------------------------------------------------------------ constants

DEV = list(s112.DEV_ICAO)                      # EGLC, LFPG, KDSM, YSDU, KRNO, KSFO
STATION = {ic: s112.STATION[ic] for ic in DEV}  # ICAO -> the tables' station code
ICAO_OF = {st: ic for ic, st in STATION.items()}
TEST_YEARS = tuple(f[0] for f in s97.FOLDS)    # D89.3: 2023-24, 2024-25, 2025-26
FOLD = {f[0]: (f[1], f[2]) for f in s97.FOLDS}
SCORING = ("2024-25", "2025-26")               # D128.5
EARLIER = {"2024-25": ("2023-24",), "2025-26": ("2023-24", "2024-25")}
PCT = (10, 90)                                 # D128.5: numpy's default (linear) 10th and 90th
ALPHAS = (0.1, 0.9)                            # D128.6
PENALTY = 10.0                                 # D128.5: 2 / 0.2
REL = 0.01                                     # D128.8 (i)
MIN_LOWER = 4                                  # D128.8 (ii)
COVER = (0.75, 0.85)                           # D128.8 (iv)
NOMINAL = 0.80
SEED = 133                                     # D128.9
REPS = 10_000                                  # F125.3
LEADS = s104.LEADS_ALL                         # 3 to 48
BANDS = s112.BANDS
SEASON_OF = s112.SEASON_OF
SEASONS = s112.SEASONS
CYCLE_HOURS = s97.CYCLE_HOURS
LAST_VALID = s97.LAST_VALID
LAST_DAY = dt.date(2026, 7, 31)
HOURLY = ("T1", "T2", "T3", "Q")               # D128.8's order
DAILY = ("M1", "M2")
RAW_HOURLY = ("RT1", "RT2", "RT3")             # D128.9: the same tables from raw GFS's own errors
RAW_DAILY = ("RM1", "RM2")
GATE_FOLD = "2025-26"
GATE_CELLS = ((12, 24), (12, 36))
TERC = ("low", "mid", "high")
PRED_DIR = s112.PRED_DIR
DAYS_FILE = s104.DAYS_OUT
DAYS_SHA256 = s112.S104_DAYS_SHA256
OUT_DIR = ROOT / "data" / "processed" / "session133_ranges"
SIX = 6


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


# ------------------------------------------------------------------ pure pieces (tested)

def interval_score(lo, hi, y):
    """D128.5: (u - l), plus 10 (l - y) when y < l, plus 10 (y - u) when y > u; per row."""
    lo, hi, y = (np.asarray(a, dtype=float) for a in (lo, hi, y))
    return (hi - lo) + PENALTY * np.where(y < lo, lo - y, 0.0) + PENALTY * np.where(y > hi, y - hi, 0.0)


def inside(lo, hi, y):
    """D128.5: l <= y <= u."""
    lo, hi, y = (np.asarray(a, dtype=float) for a in (lo, hi, y))
    return (lo <= y) & (y <= hi)


def summary(lo, hi, y):
    """(n, coverage, mean width, mean interval score) over the given rows."""
    n = len(y)
    if n == 0:
        return 0, None, None, None
    return (n, float(np.mean(inside(lo, hi, y))), float(np.mean(np.asarray(hi) - np.asarray(lo))),
            float(np.mean(interval_score(lo, hi, y))))


def band_index(lead):
    """Index into BANDS of each lead (3 to 12, 13 to 24, 25 to 36, 37 to 48)."""
    lead = np.asarray(lead)
    out = np.full(lead.shape, -1)
    for k, (a, b) in enumerate(BANDS):
        out[(lead >= a) & (lead <= b)] = k
    if np.any(out < 0):
        raise SystemExit("STOP: a lead outside the bands")
    return out


def season_index(month):
    month = np.asarray(month)
    return np.array([SEASONS.index(SEASON_OF[int(m)]) for m in month], dtype=int)


def build_table(e, code, period, earlier):
    """{code: (p10, p90, n)} from the rows whose period is in `earlier` only (D128.6, D128.7)."""
    e, code, period = np.asarray(e, dtype=float), np.asarray(code), np.asarray(period)
    m = np.isin(period, list(earlier))
    out = {}
    for c in np.unique(code[m]):
        v = e[m & (code == c)]
        p = np.percentile(v, PCT)
        out[int(c)] = (float(p[0]), float(p[1]), int(len(v)))
    return out


def apply_table(table, code, centre):
    """l = centre + P10, u = centre + P90 of each row's cell. A cell missing from the table stops."""
    code = np.asarray(code)
    missing = set(np.unique(code).tolist()) - set(table)
    if missing:
        raise SystemExit(f"STOP: no earlier row for table cell(s) {sorted(missing)}")
    p10 = np.array([table[int(c)][0] for c in code], dtype=float)
    p90 = np.array([table[int(c)][1] for c in code], dtype=float)
    centre = np.asarray(centre, dtype=float)
    return centre + p10, centre + p90


def swap_pairs(lo, hi):
    """D128.6: where lo > hi the two are swapped. Returns (lo, hi, number swapped)."""
    lo, hi = np.asarray(lo, dtype=float), np.asarray(hi, dtype=float)
    s = lo > hi
    return np.where(s, hi, lo), np.where(s, lo, hi), int(s.sum())


def tercile_edges(v, period, earlier):
    """Edges at 1/3 and 2/3 (numpy.quantile, linear) of the finite values in the earlier periods, their
    count and their largest value."""
    v, period = np.asarray(v, dtype=float), np.asarray(period)
    m = np.isin(period, list(earlier)) & np.isfinite(v)
    q = np.quantile(v[m], [1 / 3, 2 / 3])
    return float(q[0]), float(q[1]), int(m.sum()), float(np.max(v[m]))


def tercile_level(v, edges, top=None):
    """0 (low) if v <= e1, 1 (mid) if v <= e2, 2 (high) otherwise; where e2 equals `top` (the earlier
    rows' largest value), high is v >= e2. -1 where v is not finite."""
    v = np.asarray(v, dtype=float)
    hi_ = (v >= edges[1]) if (top is not None and edges[1] >= top) else (v > edges[1])
    out = np.where(hi_, 2, np.where(v <= edges[0], 0, 1))
    return np.where(np.isfinite(v), out, -1)


def ladder(order, stats):
    """D128.8. stats[c] = {"air": six airport values (both periods), "head": {period: headline},
    "cov": {period: pooled coverage}}. Returns (winner or None, steps)."""
    def cov_ok(c):
        return all(COVER[0] <= stats[c]["cov"][p] <= COVER[1] for p in SCORING)

    inc = order[0]
    steps = [{"step": 0, "incumbent": inc, "challenger": "", "iv": cov_ok(inc), "replaces": False}]
    if not cov_ok(inc):
        return None, steps
    for k, ch in enumerate(order[1:], 1):
        hi_, hc = float(np.mean(stats[inc]["air"])), float(np.mean(stats[ch]["air"]))
        rel = (hi_ - hc) / hi_
        lower = sum(c < a for a, c in zip(stats[inc]["air"], stats[ch]["air"]))
        s = {"step": k, "incumbent": inc, "challenger": ch, "head_inc": hi_, "head_ch": hc, "rel": rel,
             "lower": lower, "i": rel > REL, "ii": lower >= MIN_LOWER,
             "iii": all(stats[ch]["head"][p] < stats[inc]["head"][p] for p in SCORING),
             "iv": cov_ok(ch)}
        s["replaces"] = s["i"] and s["ii"] and s["iii"] and s["iv"]
        steps.append(s)
        if s["replaces"]:
            inc = ch
    return inc, steps


def day_coverage_interval(rng, day, ins, reps=REPS):
    """F125.3 on daily sums: coverage = sum(inside) / sum(rows) over the drawn days. Returns (lo, hi)."""
    days, inv = np.unique(np.asarray(day), return_inverse=True)
    num = np.bincount(inv, weights=np.asarray(ins, dtype=float), minlength=len(days))
    den = np.bincount(inv, minlength=len(days)).astype(float)
    w = s112.block_weights(rng, len(days), reps)
    lo, hi = s112.ratio_interval(w, num[:, None], den[:, None])
    return float(lo[0]), float(hi[0])


@contextlib.contextmanager
def quantile_params(alpha):
    """Session 97's LGB_PARAMS set at run time to a copy with objective quantile and this alpha, then put back."""
    base = s97.LGB_PARAMS
    if base.get("objective") != "regression_l1" or "alpha" in base:
        raise SystemExit("STOP: session 97's LGB_PARAMS is not the record's")
    s97.LGB_PARAMS = dict(base, objective="quantile", alpha=alpha)
    try:
        yield
    finally:
        s97.LGB_PARAMS = base


# ------------------------------------------------------------------ reading

def fast_time(s):
    """'YYYY-MM-DDTHH:MMZ' to a datetime, as session 97's parse_time (minutes are always 00 here)."""
    if len(s) != 17 or s[13:] != ":00Z":
        return s97.parse_time(s)
    return dt.datetime(int(s[0:4]), int(s[5:7]), int(s[8:10]), int(s[11:13]))


def meta_counts():
    """{(ICAO, period, status): rows} for the six development files, from meta.txt."""
    out, cur = {}, None
    for line in s112.PRED_META.read_text().splitlines():
        p = line.split()
        if p and p[0].startswith("pred_") and p[0].endswith(".csv.gz"):
            cur = p[0][5:-7]
            continue
        if cur in DEV and line.startswith("    "):
            for part in line.strip().split("; "):
                per, status, n = part.split()
                out[(cur, per, status)] = int(n.replace(",", ""))
    return out


def load_hourly(ic):
    """The scored rows of one development airport's prediction file in the three test years, as arrays,
    and the raw GFS of every row with one ({(cycle, lead): raw_gfs}). Every valid time passes the guard."""
    if ic not in DEV:
        raise SystemExit(f"STOP: {ic} is not a development airport")
    rows = s112.load_pred_rows(ic)
    ix = {c: i for i, c in enumerate(s112.PRED_COLUMNS)}
    raw_any, keep = {}, []
    for r in rows:
        cyc, lead, val = fast_time(r[ix["cycle_utc"]]), int(r[ix["lead"]]), fast_time(r[ix["valid_utc"]])
        if val > LAST_VALID:
            raise SystemExit(f"STOP: {ic} row valid at {val} is after {LAST_VALID}")
        if val != cyc + dt.timedelta(hours=lead):
            raise SystemExit(f"STOP: {ic} valid time is not cycle plus lead")
        if r[ix["raw_gfs"]] != "":
            raw_any[(cyc, lead)] = float(r[ix["raw_gfs"]])
        if r[ix["status"]] == "scored":
            if r[ix["period"]] not in TEST_YEARS:
                raise SystemExit(f"STOP: {ic} scored row in period {r[ix['period']]}")
            keep.append((r, cyc, lead))
    del rows

    def col(name):
        return np.array([float(r[ix[name]]) if r[ix[name]] != "" else np.nan for r, _, _ in keep])

    H = {"period": np.array([r[ix["period"]] for r, _, _ in keep]),
         "cycle": [c for _, c, _ in keep],
         "ch": np.array([int(r[ix["cycle_hour"]]) for r, _, _ in keep]),
         "lead": np.array([n for _, _, n in keep]),
         "month": np.array([int(r[ix["local_date"]][5:7]) for r, _, _ in keep]),
         "day": np.array([c.toordinal() for _, c, _ in keep]),
         "obs": col("obs"), "raw": col("raw_gfs"), "baseline": col("baseline"), "b": col("b"),
         "curve": col("curve"), "cloud": col("cloud_cover")}
    H["index"] = {(c, n): i for i, (_, c, n) in enumerate(keep)}
    return H, raw_any


def load_daily():
    """The rows of session 104's days file with common true, per ICAO, as arrays (D128.4)."""
    data = DAYS_FILE.read_bytes()
    if hashlib.sha256(data).hexdigest() != DAYS_SHA256:
        raise SystemExit(f"STOP: {DAYS_FILE.name}'s SHA-256 is not the recorded value")
    import csv
    import io
    rd = csv.DictReader(io.StringIO(data.decode()))
    per = {ic: [] for ic in DEV}
    for r in rd:
        if r["common"] not in ("true", "false"):
            raise SystemExit("STOP: days file common is not true or false")
        if r["common"] != "true":
            continue
        d = dt.date.fromisoformat(r["local_date"])
        if d > LAST_DAY:
            raise SystemExit(f"STOP: day {d} after {LAST_DAY}")
        per[ICAO_OF[r["station"]]].append(r)
    D = {}
    for ic, rows in per.items():
        rows.sort(key=lambda r: r["local_date"])
        D[ic] = {"period": np.array([r["fold"] for r in rows]),
                 "month": np.array([int(r["local_date"][5:7]) for r in rows]),
                 "day": np.array([dt.date.fromisoformat(r["local_date"]).toordinal() for r in rows]),
                 "ch": np.array([fast_time(r["cycle"]).hour for r in rows]),
                 "obs": np.array([float(r["obs_max"]) for r in rows]),
                 "raw": np.array([float(r["raw_gfs_max"]) for r in rows]),
                 "curve": np.array([float(r["curve_max"]) for r in rows])}
        for k in ("obs", "raw", "curve"):
            if not np.all(np.isfinite(D[ic][k])):
                raise SystemExit(f"STOP: {ic} a common day lacks {k}")
    return D


def training_cells(st, hashes, labels):
    """This script's training-row loader: per fold label, session 104's split (session 100's for leads
    3 to 24) of session 97's and session 104's table rows. {label: (train, test)}, each {(h, n): rows
    (cycle, x, temp, obs) in ascending cycle time}."""
    rows_a = s97.load_table(st, leads=s104.LEADS_A)
    rows_b = s104.load_table25(st, hashes[st])
    out = {}
    for label in labels:
        t0, t1 = FOLD[label]
        tr_a, te_a = s104.split_rows_leads(rows_a, t0, t1, s104.LEADS_A)
        tr_b, te_b = s104.split_rows_leads(rows_b, t0, t1, s104.LEADS_B)
        out[label] = ({**tr_a, **tr_b}, {**te_a, **te_b})
    return out


def file_rows(H, label, h, n):
    """Indices of the prediction file's scored rows of one cell, in ascending cycle time."""
    m = np.nonzero((H["period"] == label) & (H["ch"] == h) & (H["lead"] == n))[0]
    return sorted(m.tolist(), key=lambda i: H["cycle"][i])


def aligned(H, idx, test):
    """The table's test rows and the file's rows agree: same cycles, temp equal raw_gfs, obs equal."""
    return len(idx) == len(test) and all(
        H["cycle"][i] == r[0] and H["raw"][i] == r[2] and H["obs"][i] == r[3] for i, r in zip(idx, test))


# ------------------------------------------------------------------ the gate

def run_gate_checks(H_all, D_all, hashes, log):
    ok = True
    # (b)
    want = meta_counts()
    log("Gate (b): scored rows with finite obs, curve, raw_gfs and b, per airport and period (meta.txt's count):")
    for ic in DEV:
        H = H_all[ic]
        parts = []
        for p in TEST_YEARS:
            m = H["period"] == p
            fin = int(np.sum(m & np.isfinite(H["obs"]) & np.isfinite(H["curve"]) & np.isfinite(H["raw"])
                             & np.isfinite(H["b"])))
            n = int(m.sum())
            good = fin == n == want.get((ic, p, "scored"))
            ok &= good
            parts.append(f"{p} {fin:,} of {n:,} (meta {want.get((ic, p, 'scored'), 0):,}) {'ok' if good else 'FAIL'}")
        log(f"  {ic}: " + "; ".join(parts))
    log(f"Gate (b): {'PASS' if ok else 'FAIL'}")
    # (c)
    log("Gate (c): the daily-maximum file's common rows per airport and fold (reported):")
    for ic in DEV:
        D = D_all[ic]
        log(f"  {ic}: " + "; ".join(f"{p} {int(np.sum(D['period'] == p)):,}" for p in TEST_YEARS)
            + f"; total {len(D['period']):,}")
    # (a)
    if s97.LGB_PARAMS.get("objective") != "regression_l1":
        raise SystemExit("STOP: LGB_PARAMS is not the record's")
    a_ok = True
    log(f"Gate (a): baseline refit, fold {GATE_FOLD}, cycle hour 12, leads 24 and 36, against the file's baseline:")
    for ic in DEV:
        cells = training_cells(STATION[ic], hashes, (GATE_FOLD,))
        train, test = cells[GATE_FOLD]
        H = H_all[ic]
        for h, n in GATE_CELLS:
            tr, te = train[(h, n)], test[(h, n)]
            idx = file_rows(H, GATE_FOLD, h, n)
            fc = s97.fit_predict([(r[1], r[2], r[3]) for r in tr], [(r[1], r[2], r[3]) for r in te])
            eq = sum(1 for i, f in zip(idx, fc) if H["baseline"][i] == f)
            good = aligned(H, idx, te) and eq == len(idx) == len(fc) and len(fc) > 0
            a_ok &= good
            log(f"  {ic} {h}z lead {n}: train {len(tr):,}, test {len(te):,}, equal {eq:,} of {len(idx):,} "
                f"{'ok' if good else 'FAIL'}")
    log(f"Gate (a): {'PASS' if a_ok else 'FAIL'}")
    return ok and a_ok


def load_all(log):
    t = time.time()
    H_all, raw_all = {}, {}
    for ic in DEV:
        H_all[ic], raw_all[ic] = load_hourly(ic)
    D_all = load_daily()
    log(f"read the six prediction files and the days file ({time.time() - t:.0f} s)")
    return H_all, raw_all, D_all


def run_gate(args):
    print(f"SESSION 133 --gate (offline), start {now_utc()}; {versions()}")
    H_all, _, D_all = load_all(print)
    ok = run_gate_checks(H_all, D_all, s104.table25_hashes(), print)
    print(f"GATE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------------------------------------ scoring

def fit_q(ic, H, hashes, timer, log):
    """Q at one airport, folds 2024-25 and 2025-26 (D128.6). Returns lo, hi arrays (nan in 2023-24) and
    swaps per period."""
    lo = np.full(len(H["obs"]), np.nan)
    hi = np.full(len(H["obs"]), np.nan)
    swaps, fits = {}, 0
    cells = training_cells(STATION[ic], hashes, SCORING)
    for label in SCORING:
        train, test = cells[label]
        n_sw = 0
        for h in CYCLE_HOURS:
            for n in LEADS:
                tr, te = train[(h, n)], test[(h, n)]
                idx = file_rows(H, label, h, n)
                if not tr or not te or not aligned(H, idx, te):
                    raise SystemExit(f"STOP: {ic} {label} {h}z lead {n}: the table's rows and the file's differ")
                if max(r[0] for r in tr) + dt.timedelta(hours=n) >= FOLD[label][0]:
                    raise SystemExit(f"STOP: {ic} {label} {h}z lead {n}: training not before T0")
                t = time.time()
                q = {}
                for a in ALPHAS:
                    with quantile_params(a):
                        q[a] = s97.fit_predict([(r[1], r[2], r[3]) for r in tr], [(r[1], r[2], r[3]) for r in te])
                    fits += 1
                timer["fit"] += time.time() - t
                b = H["b"][idx]
                l_, u_, s = swap_pairs(np.array(q[ALPHAS[0]]), np.array(q[ALPHAS[1]]))
                n_sw += s
                lo[idx] = l_ + b
                hi[idx] = u_ + b
        swaps[label] = n_sw
    if s97.LGB_PARAMS.get("objective") != "regression_l1":
        raise SystemExit("STOP: LGB_PARAMS was not put back")
    log(f"  {ic}: Q {fits} fits; swaps " + ", ".join(f"{p} {swaps[p]:,}" for p in SCORING))
    return lo, hi, swaps, fits


def hourly_codes(H):
    band = band_index(H["lead"])
    season = season_index(H["month"])
    return {"1": np.zeros(len(band), dtype=int), "2": band, "3": band * 4 + season}


def daily_codes(D):
    return {"1": np.zeros(len(D["obs"]), dtype=int), "2": season_index(D["month"])}


def ranges_from_tables(X, codes, cand, centre_key, tables_out, ic):
    """lo, hi arrays (nan outside the scoring periods) for one table candidate at one airport."""
    lvl = cand[-1]
    code = codes[lvl]
    centre = X[centre_key]
    e = X["obs"] - centre
    lo = np.full(len(e), np.nan)
    hi = np.full(len(e), np.nan)
    for p in SCORING:
        tab = build_table(e, code, X["period"], EARLIER[p])
        for c, (a, b, n) in sorted(tab.items()):
            tables_out.append([cand, ic, p, c, n, a, b])
        m = X["period"] == p
        lo[m], hi[m] = apply_table(tab, code[m], centre[m])
    return lo, hi


def code_label(cand, c):
    lvl = cand[-1]
    hourly = cand[0] in "TR" and cand[:2] != "RM"
    if lvl == "1":
        return "all"
    if hourly and lvl == "2":
        return f"lead {BANDS[c][0]}-{BANDS[c][1]}"
    if hourly and lvl == "3":
        b, s = divmod(c, 4)
        return f"lead {BANDS[b][0]}-{BANDS[b][1]} {SEASONS[s]}"
    return SEASONS[c]


def stats_for(R, X, cands, airports=DEV):
    """The rule's figures: per candidate, six airport values over both periods, per-period headlines
    (mean of six) and per-period pooled coverage (rows pooled)."""
    out = {}
    for c in cands:
        air, head, cov = [], {}, {}
        for ic in airports:
            m = np.isin(X[ic]["period"], SCORING)
            air.append(summary(R[c][ic][0][m], R[c][ic][1][m], X[ic]["obs"][m])[3])
        for p in SCORING:
            vals, n_in, n_all = [], 0, 0
            for ic in airports:
                m = X[ic]["period"] == p
                s = summary(R[c][ic][0][m], R[c][ic][1][m], X[ic]["obs"][m])
                vals.append(s[3])
                n_in += int(np.sum(inside(R[c][ic][0][m], R[c][ic][1][m], X[ic]["obs"][m])))
                n_all += s[0]
            head[p] = float(np.mean(vals))
            cov[p] = n_in / n_all
        out[c] = {"air": air, "head": head, "cov": cov}
    return out


def score_rows(output, R, X, cands, family):
    """scores.csv rows: per candidate, airport (and all rows pooled, and the headline mean of six),
    period (each scoring period and both)."""
    rows = []
    for c in cands:
        for p in SCORING + ("both",):
            per = []
            L, U, Y = [], [], []
            for ic in DEV:
                m = np.isin(X[ic]["period"], SCORING if p == "both" else (p,))
                lo, hi, y = R[c][ic][0][m], R[c][ic][1][m], X[ic]["obs"][m]
                s = summary(lo, hi, y)
                per.append(s)
                L.append(lo), U.append(hi), Y.append(y)
                rows.append([output, c, family, ic, p] + list(s))
            rows.append([output, c, family, "all", p] + list(summary(np.concatenate(L), np.concatenate(U),
                                                                       np.concatenate(Y))))
            rows.append([output, c, family, "headline", p, sum(s[0] for s in per)]
                        + [float(np.mean([s[k] for s in per])) for k in (1, 2, 3)])
    return rows


def breakdown_rows(output, R, X, cands, family, dims):
    """breakdown.csv rows: per candidate, airport (and all), scoring period, dimension and level."""
    rows = []
    for c in cands:
        for p in SCORING:
            for dim, (key, names) in dims.items():
                for k, name in enumerate(names):
                    L, U, Y = [], [], []
                    for ic in DEV:
                        m = (X[ic]["period"] == p) & (X[ic][key] == k)
                        lo, hi, y = R[c][ic][0][m], R[c][ic][1][m], X[ic]["obs"][m]
                        rows.append([output, c, family, ic, p, dim, name] + list(summary(lo, hi, y)))
                        L.append(lo), U.append(hi), Y.append(y)
                    rows.append([output, c, family, "all", p, dim, name]
                                + list(summary(np.concatenate(L), np.concatenate(U), np.concatenate(Y))))
    return rows


def run_score(args):
    t_start = time.time()
    log_lines = []

    def log(s=""):
        print(s, flush=True)
        log_lines.append(s)

    log(f"SESSION 133 --score (offline), start {now_utc()}; {versions()}")
    log("BUILD-CHOICE SCORES ONLY, NEVER RESULTS (SPEC 2.5). Development airports only.")
    if OUT_DIR.exists():
        raise SystemExit(f"STOP: {OUT_DIR} already exists")
    hashes = s104.table25_hashes()
    H_all, raw_all, D_all = load_all(log)
    if not run_gate_checks(H_all, D_all, hashes, log):
        raise SystemExit("STOP: the gate failed; nothing written")
    log("GATE: PASS")

    # ---------------- hourly: conditions for the breakdowns
    terc_rows, no_partner = [], {}
    for ic in DEV:
        H = H_all[ic]
        H["band_k"] = band_index(H["lead"])
        H["season_k"] = season_index(H["month"])
        H["ch_k"] = np.array([CYCLE_HOURS.index(h) for h in H["ch"]])
        ra = raw_all[ic]
        prev = np.array([ra.get((c - dt.timedelta(hours=6), n + 6), np.nan) if n + 6 <= LEADS[-1] else np.nan
                         for c, n in zip(H["cycle"], H["lead"])])
        H["change"] = np.abs(H["raw"] - prev)
        H["cloud_k"] = np.full(len(prev), -1)
        H["change_k"] = np.full(len(prev), -1)
        for p in SCORING:
            m = H["period"] == p
            for var in ("cloud", "change"):
                e1, e2, n_e, top = tercile_edges(H[var], H["period"], EARLIER[p])
                H[var + "_k"][m] = tercile_level(H[var][m], (e1, e2), top)
                terc_rows.append([ic, p, var, e1, e2, n_e, top])
            no_partner[(ic, p)] = int(np.sum(m & ~np.isfinite(H["change"])))
    log("Rows with no earlier partner (left out of the change terciles): " + "; ".join(
        f"{ic} {p} {no_partner[(ic, p)]:,}" for ic in DEV for p in SCORING))

    # ---------------- hourly candidates
    tables = []
    R = {c: {} for c in HOURLY + RAW_HOURLY}
    for ic in DEV:
        H = H_all[ic]
        codes = hourly_codes(H)
        for c in ("T1", "T2", "T3"):
            R[c][ic] = ranges_from_tables(H, codes, c, "curve", tables, ic)
        for c in RAW_HOURLY:
            R[c][ic] = ranges_from_tables(H, codes, c, "raw", tables, ic)
    log(f"Q: fitting {len(DEV)} airports x {len(SCORING)} folds x {len(CYCLE_HOURS)} cycle hours x "
        f"{len(LEADS)} leads x 2 models ...")
    timer, swaps, q_fits = {"fit": 0.0}, {}, 0
    t_q = time.time()
    for ic in DEV:
        lo, hi, sw, f = fit_q(ic, H_all[ic], hashes, timer, log)
        R["Q"][ic] = (lo, hi)
        swaps[ic] = sw
        q_fits += f
    q_time = time.time() - t_q
    log(f"Q: {q_fits:,} models, fit time {timer['fit']:.0f} s, wall {q_time:.0f} s; swaps total "
        f"{sum(sum(v.values()) for v in swaps.values()):,}")
    for ic in DEV:
        m = np.isin(H_all[ic]["period"], SCORING)
        if not (np.all(np.isfinite(R["Q"][ic][0][m])) and np.all(np.isfinite(R["Q"][ic][1][m]))):
            raise SystemExit(f"STOP: {ic}: a scored row in a scoring period has no Q range")

    # ---------------- daily candidates
    RD = {c: {} for c in DAILY + RAW_DAILY}
    for ic in DEV:
        D = D_all[ic]
        D["season_k"] = season_index(D["month"])
        D["ch_k"] = np.array([CYCLE_HOURS.index(h) for h in D["ch"]])
        codes = daily_codes(D)
        for c in DAILY:
            RD[c][ic] = ranges_from_tables(D, codes, c, "curve", tables, ic)
        for c in RAW_DAILY:
            RD[c][ic] = ranges_from_tables(D, codes, c, "raw", tables, ic)

    # ---------------- the rule (D128.8)
    ladder_rows, winners = [], {}
    for output, order, RR, XX in (("hourly", HOURLY, R, H_all), ("daily_max", DAILY, RD, D_all)):
        st = stats_for(RR, XX, order)
        win, steps = ladder(order, st)
        winners[output] = win
        log(f"Rule, {output}: incumbent {order[0]}: pooled coverage "
            + ", ".join(f"{p} {st[order[0]]['cov'][p]:.4f}" for p in SCORING)
            + f"; (iv) {'holds' if steps[0]['iv'] else 'FAILS: no choice is made'}")
        ladder_rows.append([output, 0, order[0], "", repr(float(np.mean(st[order[0]]["air"]))), "", "", "",
                            repr(st[order[0]]["head"][SCORING[0]]), repr(st[order[0]]["head"][SCORING[1]]),
                            repr(st[order[0]]["cov"][SCORING[0]]), repr(st[order[0]]["cov"][SCORING[1]]),
                            "", "", "", steps[0]["iv"], ""])
        for s in steps[1:]:
            ch, inc = s["challenger"], s["incumbent"]
            log(f"  step {s['step']}: {ch} against {inc}: headline {s['head_ch']:.4f} vs {s['head_inc']:.4f} "
                f"({100 * s['rel']:+.2f} % lower) (i) {s['i']}; lower at {s['lower']} of 6 (ii) {s['ii']}; "
                f"per period {st[ch]['head'][SCORING[0]]:.4f} vs {st[inc]['head'][SCORING[0]]:.4f}, "
                f"{st[ch]['head'][SCORING[1]]:.4f} vs {st[inc]['head'][SCORING[1]]:.4f} (iii) {s['iii']}; "
                f"coverage {st[ch]['cov'][SCORING[0]]:.4f}, {st[ch]['cov'][SCORING[1]]:.4f} (iv) {s['iv']}: "
                f"{'REPLACES' if s['replaces'] else 'stays'}")
            ladder_rows.append([output, s["step"], ch, inc, repr(s["head_ch"]), repr(s["head_inc"]), repr(s["rel"]),
                                s["lower"], repr(st[ch]["head"][SCORING[0]]), repr(st[ch]["head"][SCORING[1]]),
                                repr(st[ch]["cov"][SCORING[0]]), repr(st[ch]["cov"][SCORING[1]]),
                                s["i"], s["ii"], s["iii"], s["iv"], s["replaces"]])
        log(f"Rule, {output}: winner {win if win else 'NONE (no choice made)'}")

    # ---------------- descriptive tables
    score_tab = (score_rows("hourly", R, H_all, HOURLY, "curve") + score_rows("hourly", R, H_all, RAW_HOURLY, "raw_gfs")
                 + score_rows("daily_max", RD, D_all, DAILY, "curve")
                 + score_rows("daily_max", RD, D_all, RAW_DAILY, "raw_gfs"))
    hdims = {"lead_band": ("band_k", [f"{a}-{b}" for a, b in BANDS]), "season": ("season_k", SEASONS),
             "cycle_hour": ("ch_k", [f"{h:02d}z" for h in CYCLE_HOURS]),
             "cloud_tercile": ("cloud_k", list(TERC)), "change_tercile": ("change_k", list(TERC))}
    ddims = {"season": ("season_k", SEASONS), "cycle_hour": ("ch_k", [f"{h:02d}z" for h in CYCLE_HOURS])}
    brk = (breakdown_rows("hourly", R, H_all, HOURLY, "curve", hdims)
           + breakdown_rows("hourly", R, H_all, RAW_HOURLY, "raw_gfs", hdims)
           + breakdown_rows("daily_max", RD, D_all, DAILY, "curve", ddims)
           + breakdown_rows("daily_max", RD, D_all, RAW_DAILY, "raw_gfs", ddims))

    # ---------------- the winners' coverage with its interval (F125.3, seed 133)
    rng = np.random.default_rng(SEED)
    win_rows = []
    for output, RR, XX in (("hourly", R, H_all), ("daily_max", RD, D_all)):
        w = winners[output]
        if w is None:
            log(f"Winner's coverage, {output}: no winner, nothing drawn")
            continue
        raw_twin = {"T1": "RT1", "T2": "RT2", "T3": "RT3", "M1": "RM1", "M2": "RM2"}.get(w, "")
        for ic in DEV:
            for p in SCORING:
                X = XX[ic]
                m = X["period"] == p
                ins = inside(RR[w][ic][0][m], RR[w][ic][1][m], X["obs"][m])
                lo, hi = day_coverage_interval(rng, X["day"][m], ins)
                s = summary(RR[w][ic][0][m], RR[w][ic][1][m], X["obs"][m])
                rs = summary(RR[raw_twin][ic][0][m], RR[raw_twin][ic][1][m], X["obs"][m]) if raw_twin \
                    else (None,) * 4
                win_rows.append([output, w, ic, p, s[0], len(np.unique(X["day"][m])), s[1], lo, hi,
                                 lo <= NOMINAL <= hi, s[2], s[3], raw_twin, rs[1], rs[2], rs[3]])
                log(f"  {output} {w} {ic} {p}: coverage {s[1]:.4f} [{lo:.4f}, {hi:.4f}] "
                    f"{'contains' if lo <= NOMINAL <= hi else 'EXCLUDES'} 0.80; width {s[2]:.3f}, IS {s[3]:.3f}"
                    + (f"; {raw_twin} coverage {rs[1]:.4f}, width {rs[2]:.3f}, IS {rs[3]:.3f}" if raw_twin else ""))

    # ---------------- write (only now)
    run_time = time.time() - t_start
    f = s97.fmt

    def fm(v):
        return "" if v is None else f(v)

    files = {
        "scores.csv": s97.csv_text(["output", "candidate", "centre", "airport", "period", "n", "coverage",
                                    "mean_width", "interval_score"], [[fm(v) for v in r] for r in score_tab]),
        "breakdown.csv": s97.csv_text(["output", "candidate", "centre", "airport", "period", "dimension", "level",
                                       "n", "coverage", "mean_width", "interval_score"],
                                      [[fm(v) for v in r] for r in brk]),
        "ladder.csv": s97.csv_text(["output", "step", "candidate", "incumbent", "headline", "headline_incumbent",
                                    "relative_lower", "airports_lower", "headline_2024-25", "headline_2025-26",
                                    "pooled_coverage_2024-25", "pooled_coverage_2025-26", "part_i", "part_ii",
                                    "part_iii", "part_iv", "replaces"], [[str(v) for v in r] for r in ladder_rows]),
        "tables.csv": s97.csv_text(["candidate", "airport", "scoring_period", "cell", "n_earlier", "p10", "p90"],
                                   [[r[0], r[1], r[2], code_label(r[0], r[3]), r[4], f(r[5]), f(r[6])]
                                    for r in tables]),
        "q_swaps.csv": s97.csv_text(["airport", "period", "rows", "swapped"],
                                    [[ic, p, int(np.sum(H_all[ic]["period"] == p)), swaps[ic][p]]
                                     for ic in DEV for p in SCORING]),
        "terciles.csv": s97.csv_text(["airport", "scoring_period", "variable", "edge_1", "edge_2", "n_earlier",
                                      "earlier_max", "rows_without_partner"],
                                     [[r[0], r[1], r[2], f(r[3]), f(r[4]), r[5], f(r[6]),
                                       no_partner[(r[0], r[1])] if r[2] == "change" else ""] for r in terc_rows]),
        "winner_coverage.csv": s97.csv_text(["output", "candidate", "airport", "period", "n", "days", "coverage",
                                             "ci_low", "ci_high", "contains_0.80", "mean_width", "interval_score",
                                             "raw_twin", "raw_coverage", "raw_mean_width", "raw_interval_score"],
                                            [[fm(v) for v in r] for r in win_rows]),
    }
    inputs = [(PRED_DIR / f"pred_{ic}.csv.gz").relative_to(ROOT.parent) for ic in DEV] + \
        [DAYS_FILE.relative_to(ROOT.parent)] + \
        [(s97.STAGEC_DIR / s97.TABLES[STATION[ic]][0]).relative_to(ROOT.parent) for ic in DEV] + \
        [(s97.STAGEC_DIR / s104.TABLE25[STATION[ic]]).relative_to(ROOT.parent) for ic in DEV]
    meta = [f"Session 133 range comparison (DECISIONS D128), written by scripts/session133_ranges.py --score.",
            "Build-choice scores only, never results (SPEC 2.5).",
            f"run {now_utc()}; run time {run_time:.0f} s; Q {q_fits:,} models, fit time {timer['fit']:.0f} s; "
            f"{versions()}",
            f"script SHA-256 {sha256_file(Path(__file__))}",
            "imported, SHA-256 checked: " + "; ".join(f"{k} {v}" for k, v in IMPORTED_SHA256.items()),
            f"seed {SEED}; resamples {REPS}; percentiles {PCT}; penalty {PENALTY}",
            f"winners: hourly {winners['hourly'] or 'none'}; daily maximum {winners['daily_max'] or 'none'}",
            "inputs (path from MLwx-all, SHA-256):"]
    for p in inputs:
        meta.append(f"  {p}  sha256 {sha256_file(ROOT.parent / p)}")
    meta.append("files:")
    for name, text in files.items():
        meta.append(f"  {name}  bytes {len(text.encode()):,}  sha256 {hashlib.sha256(text.encode()).hexdigest()}")
    OUT_DIR.mkdir()
    for name, text in files.items():
        s112.write_once_text(OUT_DIR / name, text)
    s112.write_once_text(OUT_DIR / "run_log.txt", "\n".join(log_lines) + "\n")
    s112.write_once_text(OUT_DIR / "meta.txt", "\n".join(meta) + "\n")
    print(f"wrote {len(files) + 2} files to {OUT_DIR}; run time {run_time:.0f} s")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    args = ap.parse_args()
    return run_gate(args) if args.gate else run_score(args)


if __name__ == "__main__":
    sys.exit(main())
