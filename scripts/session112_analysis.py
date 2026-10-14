"""Session 112: a descriptive analysis of the stage C curve and its daily maximum (DECISIONS D106). Offline.

Descriptive only (D106.2, SPEC 2.5). It changes no verdict, model, setting,
rule, bar or table. It is not stage C's look: session 106's --look mode is
never called and no session107_* file is written; the claim airports' frozen
models are refitted by the look's route only to regenerate predictions
already scored, which must reproduce F150 exactly. Data: the 12 airports of
D103.4 only. Nothing valid after 2026-07-31T23:00 UTC is read.

Modes (one per run):
  --regen    Step 2. Development airports: session 104's route (score_part,
             three folds, leads 3 to 48, the tracker). Claim airports:
             session 106's route (run_airport: frozen fit before 2024-08-01,
             one tracker through both looks). Gate D: every cell's n and MAE
             and every day equal session 104's files. Gate C: every n and MAE
             and every day equal session 107's files. Then writes the
             predictions, gzipped, to MLwx-stagec/analysis112/ with a meta file.
  --refs     Step 3. The references of D106.4 from each fold's or look's own
             training rows (climatology, constant bias, linear MOS) and
             persistence by D100.5; the tercile and decile edges of D106.5
             and D106.6, written to data/processed/session112_analysis/
             bin_edges.csv before any test error is computed.
  --check    Step 4. Self-checks of the statistics on synthetic data only.
  --analyse  Steps 5 to 8. Tables in data/processed/session112_analysis/ and
             figures in figures/analysis/.
  --contrib  Step 7, D106.10. Refits the baseline at leads 6, 12, 18, 24, 36
             and 48 (every cycle hour, fold and look), checks each refit
             reproduces the stored baseline exactly, then LightGBM's own
             feature contributions (pred_contrib=True) on the scored test rows.
  --zuck     Step 9, D106.13. Plots one logged cycle (downloaded by hand into
             a temporary folder and passed with --zuck-file). Forecast columns
             only; no observation is read.

Imported read only, each after its SHA-256 check: scripts/session104_curve_cv.py
(F147) and scripts/session106_claim_look.py (F149, F150.4), and through them
sessions 97, 100 and 103. Used from session 104: score_part, load_table25,
table25_hashes, errors, daily_max, split_rows_leads, local_day, usable_day,
day_cycle, TZ, LEADS_A, LEADS_B, LEADS_ALL, DAY_LAST_VALID; from session 106:
run_airport, tables_of, load_rows, hourly_errors, daily_sets, daily_errors,
mae_or_none, hourly_persistence, daily_persistence, persistence_day,
observed_max, CLAIM, LOOKS, T_TRAIN, HIDX; from session 97: load_table,
fold_role, fit_predict, mae, mean_error, fmt, csv_text, FOLDS, G15,
LGB_PARAMS, CYCLE_HOURS, STAGEC_DIR, parse_time. New code here (no function
existed): the gates' comparisons against the record files (session 106's
scoring loop in run_look is not a function, so its loop is restated), the
prediction writer, the references, the bin edges, every statistic, figure
and table of D106.5 to D106.13, the model refit that returns the model for
pred_contrib, and the synthetic self-checks.

Every output file is written once and never overwritten.
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


S104_SCRIPT_SHA256 = "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb"   # F147
S106_SCRIPT_SHA256 = "5e046acffc6eb28619d1883c8b93b6ff97bc3305addade56be5ab30af169281a"   # F149, F150.4
if sha256_file(HERE / "session104_curve_cv.py") != S104_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session104_curve_cv.py's SHA-256 is not F147's")
if sha256_file(HERE / "session106_claim_look.py") != S106_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session106_claim_look.py's SHA-256 is not F150.4's")
sys.path.insert(0, str(HERE))
import session106_claim_look as s106  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import io  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from zoneinfo import ZoneInfo  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

s104 = s106.s104
s97 = s106.s97

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
OUT_DIR = PROCESSED / "session112_analysis"
FIG_DIR = ROOT / "figures" / "analysis"
PRED_DIR = s97.STAGEC_DIR / "analysis112"
PRED_META = PRED_DIR / "meta.txt"
REFS_META = PRED_DIR / "refs_meta.txt"
EDGES_OUT = OUT_DIR / "bin_edges.csv"

S104_SCORES, S104_SCORES_SHA256 = s106.S104_SCORES, s106.S104_SCORES_SHA256
S104_DAYS, S104_DAYS_SHA256 = s106.S104_DAYS, s106.S104_DAYS_SHA256
S107_SCORES = PROCESSED / "session107_claim_scores.csv"
S107_SCORES_SHA256 = "2918fff42ab17ff2fce55260d7d0d757638b989943324ddceb3e1a7ff59488ca"   # F150.4
S107_DAYS = PROCESSED / "session107_claim_days.csv"
S107_DAYS_SHA256 = "3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297"     # F150.4

# The 12 airports of D103.4. Claim airports lead every summary (D106.3).
CLAIM_ICAO = list(s106.CLAIM)                                   # EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN
DEV_ST = list(s97.STATIONS)                                     # EGLC, LFPG, DSM, YSDU, RNO, SFO
DEV_ICAO = [s106.DEV_ICAO[s] for s in DEV_ST]                   # EGLC, LFPG, KDSM, YSDU, KRNO, KSFO
AIRPORTS = CLAIM_ICAO + DEV_ICAO
STATION = {**{ic: s106.CLAIM[ic][0] for ic in CLAIM_ICAO}, **{s106.DEV_ICAO[s]: s for s in DEV_ST}}
TZNAME = {**{ic: s106.CLAIM[ic][1] for ic in CLAIM_ICAO}, **{s106.DEV_ICAO[s]: s104.TZ[s] for s in DEV_ST}}
GROUP = {ic: ("claim" if ic in CLAIM_ICAO else "dev") for ic in AIRPORTS}
SEA = ("KSFO", "CYYZ", "ZGSZ", "NZWN")                          # D106.11: sea in the grid box
DEV_FLAG = "development airport: its build choices used these folds (D106.3)"

# Periods: (label, training T0, test start, test end). Dev: each fold trains before its own T0 and its
# tracker starts there (D97.7). Claim: one frozen fit before 2024-08-01, trackers from then (D100.3).
DEV_PERIODS = [(lab, t0, t0, t1) for lab, t0, t1 in s97.FOLDS]
CLAIM_PERIODS = [(lab, s106.T_TRAIN, t0, t1) for lab, t0, t1 in s106.LOOKS]


def periods(ic):
    return CLAIM_PERIODS if GROUP[ic] == "claim" else DEV_PERIODS


LEADS = s104.LEADS_ALL
G15 = list(s97.G15)
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)
LAST_VALID = s104.DAY_LAST_VALID

PRED_COLUMNS = ["icao", "station", "group", "period", "cycle_utc", "cycle_hour", "lead", "valid_utc", "local_date",
                "local_hour", "status", "obs", "raw_gfs", "baseline", "b", "curve", "n_used"] + G15


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    import matplotlib
    return (f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}; "
            f"matplotlib {matplotlib.__version__}")


def fmt(v):
    return "" if v is None else s97.fmt(v)


def tstr(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


def write_once_bytes(path, data):
    """Write once: a temporary name, then a hard link to the final name, which never overwrites."""
    path = Path(path)
    if path.exists():
        raise SystemExit(f"STOP: {path} already exists; not overwriting it")
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.link(tmp, path)
    os.unlink(tmp)


def write_once_text(path, text):
    write_once_bytes(path, text.encode())


def gzip_bytes(text):
    """gzip with a fixed header (no name, mtime 0), so equal text gives equal bytes."""
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0, filename="") as g:
        g.write(text.encode())
    return buf.getvalue()


_LOCAL = {}


def local_of(valid, tzname):
    """(local date, local hour) of a UTC valid time."""
    k = (valid, tzname)
    if k not in _LOCAL:
        t = valid.replace(tzinfo=dt.timezone.utc).astimezone(ZoneInfo(tzname))
        _LOCAL[k] = (t.date(), t.hour)
    return _LOCAL[k]


# ------------------------------------------------------------------ Step 2: regenerate (the record's routes)

def regen_dev(st, hashes, timer):
    """Session 104's route at one development airport. Returns the rows (both
    tables), the cells {(fold, h, n): cell}, the obs map, the forecast map and
    the days (session 104's daily_max)."""
    rows_a = s97.load_table(st, leads=tuple(range(0, 25)))
    rows_b = s104.load_table25(st, hashes[st])
    cells = {}
    for rows, leads in ((rows_a, s104.LEADS_A), (rows_b, s104.LEADS_B)):
        c, _ = s104.score_part(st, rows, leads, timer)
        cells.update(c)
    obs_map, fc, bad = {}, {}, 0
    for cycle, valid, h, n, complete, obs, temp, x in rows_a + rows_b:
        if valid in obs_map and obs_map[valid] != obs:
            bad += 1
        obs_map[valid] = obs
        if temp is not None:
            fc.setdefault((cycle, n), {})["raw_gfs"] = temp
    if bad:
        raise SystemExit(f"STOP: {st}: {bad} rows give a different observation for the same valid time")
    for (label, h, n), c in cells.items():
        for pre in ("", "x_"):
            for i, cy in enumerate(c[pre + "cycles"]):
                d = fc.setdefault((cy, n), {})
                d["baseline"] = c[pre + "baseline"][i]
                d["curve"] = c[pre + "curve"][i]
    days, drops = s104.daily_max(st, obs_map, fc)
    return rows_a + rows_b, cells, obs_map, fc, days


def gate_d(st, cells, days, rec_scores, rec_days):
    """Gate D at one development airport: (cells compared, cells equal, days compared, days equal)."""
    errs = s104.errors({(st,) + k: v for k, v in cells.items()}, LEADS)
    comp = eq = 0
    bad = []
    for (s, label, h, n, m), e in errs.items():
        comp += 1
        r = rec_scores.get((s, label, h, n, m))
        same = r is not None and len(e) == r[0] and s97.mae(e) == r[1] and s97.mean_error(e) == r[2]
        eq += same
        if not same:
            bad.append((s, label, h, n, m))
    want = {k: v for k, v in rec_days.items() if k[0] == st}
    got = {(r["station"], r["local_date"]): r for r in days}
    d_eq = 0
    for k, r in want.items():
        g = got.get(k)
        d_eq += g is not None and g["fold"] == r["fold"] and tstr(g["cycle"]) == r["cycle"] \
            and g["obs_max"] == r["obs_max"] and g["raw_gfs"] == r["raw_gfs_max"] \
            and g["baseline"] == r["baseline_max"] and g["curve"] == r["curve_max"] and g["common"] == r["common"]
    extra = len(set(got) - set(want))
    return comp, eq, len(want), d_eq, extra, bad[:5]


def claim_score_rows(res):
    """Session 106's run_look scoring loop, restated (it is not a function there): the
    rows of session107_claim_scores.csv for one airport, keyed for comparison."""
    out = {}
    for look, _, _ in s106.LOOKS:
        for h in s97.CYCLE_HOURS:
            for n in LEADS:
                recs = [r for r in res["hourly"][(h, n)] if r[0] == look]
                sub = [r for r in recs if r[6] is not None]
                for m in s106.METHODS:
                    e = s106.hourly_errors(recs, s106.HIDX[m])
                    out[(res["name"], look, "hourly", m, "common", str(h), str(n))] = \
                        (len(e), s106.mae_or_none(e), s97.mean_error(e) if e else None)
                for m in ("curve", "persistence"):
                    e = s106.hourly_errors(sub, s106.HIDX[m])
                    out[(res["name"], look, "hourly", m, "persistence_subset", str(h), str(n))] = \
                        (len(e), s106.mae_or_none(e), s97.mean_error(e) if e else None)
        dc, dsub = s106.daily_sets(res, look)
        for m in s106.METHODS:
            e = s106.daily_errors(dc, m)
            out[(res["name"], look, "daily", m, "common", "", "")] = \
                (len(e), s106.mae_or_none(e), s97.mean_error(e) if e else None)
        for m in ("curve", "persistence"):
            e = s106.daily_errors(dsub, m)
            out[(res["name"], look, "daily", m, "persistence_subset", "", "")] = \
                (len(e), s106.mae_or_none(e), s97.mean_error(e) if e else None)
    return out


def gate_c(res, rec_scores, rec_days):
    got = claim_score_rows(res)
    want = {k: v for k, v in rec_scores.items() if k[0] == res["name"]}
    eq = sum(k in got and got[k][0] == v[0] and got[k][1] == v[1] and got[k][2] == v[2] for k, v in want.items())
    bad = [k for k, v in want.items() if not (k in got and got[k] == v)][:5]
    keys_same = set(got) == set(want)
    wd = {k: v for k, v in rec_days.items() if k[0] == res["name"]}
    gd = {(res["name"], d["local_date"].isoformat()): d for d in res["days"]}
    d_eq = 0
    for k, r in wd.items():
        g = gd.get(k)
        d_eq += g is not None and g["look"] == r["look"] and tstr(g["cycle"]) == r["cycle"] \
            and g["obs_max"] == r["obs_max"] and g["raw_gfs"] == r["raw_gfs_max"] \
            and g["baseline"] == r["baseline_max"] and g["curve"] == r["curve_max"] \
            and g["pers_date"].isoformat() == r["persistence_date"] and g["persistence"] == r["persistence_max"] \
            and g["common"] == r["common"] and g["pers_subset"] == r["persistence_subset"]
    return len(want), eq, keys_same, len(wd), d_eq, len(set(gd) - set(wd)), bad


def _val(s):
    return None if s == "" else float(s)


def _bool(s):
    return {"true": True, "false": False}[s]


def read_records():
    for p, want in ((S104_SCORES, S104_SCORES_SHA256), (S104_DAYS, S104_DAYS_SHA256),
                    (S107_SCORES, S107_SCORES_SHA256), (S107_DAYS, S107_DAYS_SHA256)):
        if sha256_file(p) != want:
            raise SystemExit(f"STOP: {p.name}'s SHA-256 is not the recorded value")
    d_sc, d_days, c_sc, c_days = {}, {}, {}, {}
    with open(S104_SCORES, newline="") as f:
        for r in csv.DictReader(f):
            d_sc[(r["station"], r["fold"], int(r["cycle_hour"]), int(r["lead"]), r["method"])] = \
                (int(r["n"]), float(r["mae"]), float(r["mean_error"]))
    with open(S104_DAYS, newline="") as f:
        for r in csv.DictReader(f):
            d_days[(r["station"], r["local_date"])] = {
                "fold": r["fold"], "cycle": r["cycle"], "obs_max": _val(r["obs_max"]),
                "raw_gfs_max": _val(r["raw_gfs_max"]), "baseline_max": _val(r["baseline_max"]),
                "curve_max": _val(r["curve_max"]), "common": _bool(r["common"])}
    with open(S107_SCORES, newline="") as f:
        for r in csv.DictReader(f):
            c_sc[(r["icao"], r["look"], r["output"], r["method"], r["row_set"], r["cycle_hour"], r["lead"])] = \
                (int(r["n"]), _val(r["mae"]), _val(r["mean_error"]))
    with open(S107_DAYS, newline="") as f:
        for r in csv.DictReader(f):
            c_days[(r["icao"], r["local_date"])] = {
                "look": r["look"], "cycle": r["cycle"], "obs_max": _val(r["obs_max"]),
                "raw_gfs_max": _val(r["raw_gfs_max"]), "baseline_max": _val(r["baseline_max"]),
                "curve_max": _val(r["curve_max"]), "persistence_date": r["persistence_date"],
                "persistence_max": _val(r["persistence_max"]), "common": _bool(r["common"]),
                "persistence_subset": _bool(r["persistence_subset"])}
    return d_sc, d_days, c_sc, c_days


def prediction_rows(ic, rows, fcmap, nused, period_of):
    """The prediction file's rows: every table row whose cycle is in a test period, at leads 3 to 48,
    in cycle then lead order. fcmap: {(cycle, lead): (baseline, curve)}; nused: {(cycle, lead): errors used}."""
    tz = TZNAME[ic]
    out, counts = [], {}
    seen = set()
    for cycle, valid, h, n, complete, obs, temp, x in sorted(rows, key=lambda r: (r[0], r[3])):
        if n not in LEADS:
            continue
        p = period_of(cycle)
        if p is None:
            continue
        if (cycle, n) in seen:
            raise SystemExit(f"STOP: {ic}: two rows for cycle {cycle} lead {n}")
        seen.add((cycle, n))
        feats = all(v is not None for v in x)
        status = "scored" if complete else "extra" if (feats and obs is None) else "incomplete"
        bc = fcmap.get((cycle, n))
        if (status in ("scored", "extra")) != (bc is not None):
            raise SystemExit(f"STOP: {ic} {cycle} lead {n}: status {status} but forecast {bc}")
        base, curve = bc if bc else (None, None)
        ld, lh = local_of(valid, tz)
        counts[(p, status)] = counts.get((p, status), 0) + 1
        out.append([ic, STATION[ic], GROUP[ic], p, tstr(cycle), h, n, tstr(valid), ld.isoformat(), lh, status,
                    obs, temp, base, None if base is None else curve - base, curve, nused.get((cycle, n))] + x)
    return out, counts


def run_regen(args):
    t_start = time.time()
    print(f"SESSION 112 --regen (offline), start {now_utc()}; {versions()}")
    print("DESCRIPTIVE ONLY (D106.2). Session 106's --look is not called; no session107_* file is written.")
    if PRED_DIR.exists():
        raise SystemExit(f"STOP: {PRED_DIR} already exists")
    d_sc, d_days, c_sc, c_days = read_records()
    s106.check_claim_zones()
    timer = {"fit": 0.0}
    hashes = s104.table25_hashes()
    files, meta_rows = {}, []
    gate_ok = True
    tot = {"D cells": [0, 0], "D days": [0, 0], "C rows": [0, 0], "C days": [0, 0]}
    for ic in AIRPORTS:
        t = time.time()
        if GROUP[ic] == "dev":
            st = STATION[ic]
            rows, cells, obs_map, fc, days = regen_dev(st, hashes, timer)
            comp, eq, nd, d_eq, extra, bad = gate_d(st, cells, days, d_sc, d_days)
            ok = comp == eq == 3 * 4 * 46 * 3 and nd == d_eq and extra == 0 and nd > 0
            tot["D cells"][0] += comp
            tot["D cells"][1] += eq
            tot["D days"][0] += nd
            tot["D days"][1] += d_eq
            print(f"  {ic}: Gate D cells {eq} of {comp} equal (n, MAE, mean error); days {d_eq} of {nd} equal, "
                  f"{extra} extra; {'PASS' if ok else 'FAIL'} ({time.time() - t:.0f} s)", flush=True)
            fcmap = {(cy, n): (c[pre + "baseline"][i], c[pre + "curve"][i])
                     for (lab, h, n), c in cells.items() for pre in ("", "x_") for i, cy in enumerate(c[pre + "cycles"])}
            nused = {(cy, n): c[pre + "n_used"][i]
                     for (lab, h, n), c in cells.items() for pre in ("", "x_") for i, cy in enumerate(c[pre + "cycles"])}
            period_of = s104.fold_of
        else:
            res = s106.run_airport(ic, timer, log=lambda *a, **k: None)
            st, tz, tfiles = s106.tables_of(ic)
            rows = s106.load_rows(*tfiles[0][:2], st, tfiles[0][2]) + s106.load_rows(*tfiles[1][:2], st, tfiles[1][2])
            nrow, eq, keys_same, nd, d_eq, extra, bad = gate_c(res, c_sc, c_days)
            ok = nrow == eq and keys_same and nd == d_eq and extra == 0 and nd > 0
            tot["C rows"][0] += nrow
            tot["C rows"][1] += eq
            tot["C days"][0] += nd
            tot["C days"][1] += d_eq
            print(f"  {ic}: Gate C score rows {eq} of {nrow} equal (n, MAE, mean error), key sets equal {keys_same}; "
                  f"days {d_eq} of {nd} equal, {extra} extra; {'PASS' if ok else 'FAIL'} ({time.time() - t:.0f} s)",
                  flush=True)
            cells = res["cells"]
            fcmap = {(cy, n): (c[pre + "baseline"][i], c[pre + "curve"][i])
                     for (h, n), c in cells.items() for pre in ("", "x_") for i, cy in enumerate(c[pre + "cycles"])}
            nused = {(cy, n): c[pre + "n_used"][i]
                     for (h, n), c in cells.items() for pre in ("", "x_") for i, cy in enumerate(c[pre + "cycles"])}
            period_of = s106.look_of
        if not ok:
            gate_ok = False
            print(f"    first mismatches: {bad}")
            continue
        out, counts = prediction_rows(ic, rows, fcmap, nused, period_of)
        n_cells = sum(len(c["cycles"]) for c in cells.values())
        n_x = sum(len(c["x_cycles"]) for c in cells.values())
        if sum(v for (p, s), v in counts.items() if s == "scored") != n_cells or \
                sum(v for (p, s), v in counts.items() if s == "extra") != n_x:
            raise SystemExit(f"STOP: {ic}: prediction rows do not match the cells' counts")
        files[ic] = (len(out), gzip_bytes(s97.csv_text(PRED_COLUMNS, [[fmt(v) for v in r] for r in out])), counts)
        del out, rows, cells, fcmap, nused
    print(f"Gate D: cells {tot['D cells'][1]} of {tot['D cells'][0]}, days {tot['D days'][1]} of {tot['D days'][0]}; "
          f"Gate C: score rows {tot['C rows'][1]} of {tot['C rows'][0]}, days {tot['C days'][1]} of "
          f"{tot['C days'][0]}; fit time {timer['fit']:.0f} s")
    if not gate_ok:
        raise SystemExit("STOP: Gate D or Gate C differs; nothing written")
    print("Gate D: PASS; Gate C: PASS")
    PRED_DIR.mkdir()
    for ic in AIRPORTS:
        n_out, data, counts = files[ic]
        path = PRED_DIR / f"pred_{ic}.csv.gz"
        write_once_bytes(path, data)
        meta_rows.append((path.name, n_out, len(data), hashlib.sha256(data).hexdigest(), counts))
    lines = [f"Session 112 predictions (D106.3), written by scripts/session112_analysis.py --regen.",
             f"run {now_utc()}; run time {time.time() - t_start:.0f} s; {versions()}",
             f"script SHA-256 {sha256_file(Path(__file__))}",
             "Gate D (session 104's files) and Gate C (session 107's files): PASS, every value equal at full precision.",
             "columns: " + ",".join(PRED_COLUMNS),
             "status: scored (complete case), extra (complete features, no observation; predicted, never scored),"
             " incomplete (incomplete features; raw GFS only). b = curve minus baseline.", "files:"]
    for name, n, nb, h, counts in meta_rows:
        lines.append(f"  {name}  rows {n:,}  bytes {nb:,}  sha256 {h}")
        lines.append("    " + "; ".join(f"{p} {s} {v:,}" for (p, s), v in sorted(counts.items())))
    write_once_text(PRED_META, "\n".join(lines) + "\n")
    print(f"wrote {len(meta_rows)} prediction files and meta.txt to {PRED_DIR}; rows "
          f"{sum(m[1] for m in meta_rows):,}; run time {time.time() - t_start:.0f} s")
    return 0


# ------------------------------------------------------------------ reading the predictions

def pred_hashes(meta=PRED_META):
    out = {}
    for line in meta.read_text().splitlines():
        p = line.split()
        if p and p[0].endswith(".csv.gz") and "sha256" in p:
            out[p[0]] = p[p.index("sha256") + 1]
    return out


def read_gz_csv(path, want):
    data = path.read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != want:
        raise SystemExit(f"STOP: {path.name} SHA-256 {got} is not its meta's {want}")
    rd = csv.reader(io.StringIO(gzip.decompress(data).decode()))
    head = next(rd)
    return head, list(rd)


def load_pred_rows(ic):
    """The prediction file's rows as lists of strings, after the SHA-256 check against meta.txt."""
    name = f"pred_{ic}.csv.gz"
    head, rows = read_gz_csv(PRED_DIR / name, pred_hashes()[name])
    if head != PRED_COLUMNS:
        raise SystemExit(f"STOP: {name} header differs")
    return rows


# ------------------------------------------------------------------ Step 3: the references and the bin edges

REF_COLUMNS = ["cycle_utc", "lead", "climatology", "constant_bias", "linear_mos", "persistence", "raw_range",
               "raw_change24", "obs_range", "obs_change24"]
TERCILE_CONDITIONS = ("cloud_cover", "wind_speed_10m", "raw_range", "raw_change24", "abs_b", "curve_minus_raw",
                      "obs_range", "obs_change24")
FROM_TEST = ("abs_b", "curve_minus_raw")     # no value on training rows: edges from the test forecasts (F155)


def table_rows(ic):
    """Both tables' rows (leads 0 to 48) by the record's loaders."""
    if GROUP[ic] == "dev":
        st = STATION[ic]
        return s97.load_table(st, leads=tuple(range(0, 25))) + s104.load_table25(st, s104.table25_hashes()[st])
    st, tz, tf = s106.tables_of(ic)
    return s106.load_rows(*tf[0][:2], st, tf[0][2]) + s106.load_rows(*tf[1][:2], st, tf[1][2])


def doy365(d):
    """Day of year in a 365-day year (29 February counts as 28 February)."""
    if d.month == 2 and d.day == 29:
        d = d - DAY
    return dt.date(2001, d.month, d.day).timetuple().tm_yday


def climatology_table(obs_map, t0):
    """D106.4: the mean training observation (valid before t0) per UTC hour and day of year, within
    15 days (circular, 365-day year). Returns a 24 x 366 array (index 1 to 365) and the training count."""
    s = np.zeros((24, 366))
    c = np.zeros((24, 366))
    n = 0
    for v, o in obs_map.items():
        if o is None or not v < t0:
            continue
        s[v.hour, doy365(v.date())] += o
        c[v.hour, doy365(v.date())] += 1
        n += 1
    out = np.full((24, 366), np.nan)
    for k in range(1, 366):
        idx = [((k - 1 + j) % 365) + 1 for j in range(-15, 16)]
        cs = c[:, idx].sum(axis=1)
        ss = s[:, idx].sum(axis=1)
        with np.errstate(invalid="ignore", divide="ignore"):
            out[:, k] = np.where(cs > 0, ss / np.where(cs > 0, cs, 1), np.nan)
    return out, n


def ols_fit(x, y):
    """Ordinary least squares with an intercept: coefficients [intercept, b1..b9]."""
    a = np.column_stack([np.ones(len(x)), np.asarray(x, dtype=float)])
    coef, *_ = np.linalg.lstsq(a, np.asarray(y, dtype=float), rcond=None)
    return coef


class DayValues:
    """Raw GFS's range over a local day from one cycle, and the observed range, cached."""

    def __init__(self, tzname, raw, obs_map):
        self.tz, self.raw, self.obs = tzname, raw, obs_map
        self.rr, self.orr = {}, {}

    def raw_range(self, cycle, d):
        k = (cycle, d)
        if k not in self.rr:
            _, _, hours = s104.local_day(d, self.tz)
            v = [self.raw.get((cycle, h)) for h in hours]
            ok = all(0 <= (h - cycle) / HOUR <= 48 for h in hours) and all(x is not None for x in v)
            self.rr[k] = max(v) - min(v) if ok else None
        return self.rr[k]

    def obs_range(self, d):
        if d not in self.orr:
            _, _, hours = s104.local_day(d, self.tz)
            if hours[-1] > LAST_VALID or any(h not in self.obs for h in hours):
                self.orr[d] = None
            else:
                u = [o for o in (self.obs[h] for h in hours) if o is not None]
                self.orr[d] = max(u) - min(u) if s104.usable_day(len(hours), len(u)) else None
        return self.orr[d]


def conditions_of(cycle, valid, n, dv, obs_map):
    """The table-based conditions of one row: raw range, raw 24 h change (leads 24 to 48), observed
    range and observed 24 h change."""
    ld, _ = local_of(valid, dv.tz)
    rr = dv.raw_range(cycle, ld)
    rc = None
    if n >= 24:
        a, b = dv.raw.get((cycle, valid)), dv.raw.get((cycle, valid - 24 * HOUR))
        rc = a - b if a is not None and b is not None else None
    orr = dv.obs_range(ld)
    o1, o0 = obs_map.get(valid), obs_map.get(valid - 24 * HOUR)
    oc = o1 - o0 if o1 is not None and o0 is not None else None
    return rr, rc, orr, oc


def edges_of(values, k):
    v = np.asarray([x for x in values if x is not None], dtype=float)
    q = np.quantile(v, [j / k for j in range(1, k)]) if len(v) else np.full(k - 1, np.nan)
    return [float(x) for x in q], len(v)


def run_refs(args):
    t_start = time.time()
    print(f"SESSION 112 --refs (offline), start {now_utc()}; {versions()}")
    if not PRED_META.exists():
        raise SystemExit("STOP: run --regen first")
    for p in (EDGES_OUT, REFS_META):
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    edge_rows, meta, checks = [], [], []
    ref_files, obs_files = {}, {}
    for ic in AIRPORTS:
        t = time.time()
        rows = table_rows(ic)
        obs_map, raw = {}, {}
        for cycle, valid, h, n, complete, obs, temp, x in rows:
            obs_map[valid] = obs
            if temp is not None:
                raw[(cycle, valid)] = temp
        dv = DayValues(TZNAME[ic], raw, obs_map)
        pred = load_pred_rows(ic)
        ix = {c: i for i, c in enumerate(PRED_COLUMNS)}
        # Training sets: one per fold (dev) or one (claim, before 2024-08-01).
        trains = sorted({(t0, t1) for _, t0, _, t1 in periods(ic)}) if GROUP[ic] == "dev" \
            else [(s106.T_TRAIN, s106.T_END)]
        models = {}
        for t0, t1 in trains:
            cb, mos, ntr = {}, {}, {}
            tr_rows = []
            # the check: the baseline's own selection, counted independently (complete case, valid before T0)
            indep = {}
            for r in rows:
                if r[4] and r[1] < t0:
                    indep[(r[2], r[3])] = indep.get((r[2], r[3]), 0) + 1
            for leads in (s104.LEADS_A, s104.LEADS_B):
                keep = set(leads)
                sub = [r for r in rows if r[3] in keep]
                train, _ = s104.split_rows_leads(sub, t0, t1, leads)
                for (h, n), tr in train.items():
                    if len(tr) != indep.get((h, n), 0) or not tr:
                        raise SystemExit(f"STOP: {ic} {h}z lead {n}: training rows {len(tr)}, independent "
                                         f"{indep.get((h, n), 0)}")
                    if max(r[0] for r in tr) + n * HOUR >= t0:
                        raise SystemExit(f"STOP: {ic} {h}z lead {n}: a training row is not valid before T0")
                    resid = [r[3] - r[2] for r in tr]
                    cb[(h, n)] = float(np.mean(resid))
                    mos[(h, n)] = ols_fit([r[1] for r in tr], resid)
                    ntr[(h, n)] = len(tr)
            for cycle, valid, h, n, complete, obs, temp, x in rows:
                if complete and valid < t0 and n in LEADS:
                    tr_rows.append((cycle, valid, n, obs, temp, x))
            clim, nclim = climatology_table(obs_map, t0)
            models[t0] = (cb, mos, clim, ntr)
            # bin edges from the training rows (D106.5, D106.6), before any test error is computed
            label = "A+B" if GROUP[ic] == "claim" else next(p for p, a, _, _ in periods(ic) if a == t0)
            conds = {"cloud_cover": [], "wind_speed_10m": [], "raw_range": [], "raw_change24": [],
                     "obs_range": [], "obs_change24": []}
            for cycle, valid, n, obs, temp, x in tr_rows:
                rr, rc, orr, oc = conditions_of(cycle, valid, n, dv, obs_map)
                conds["cloud_cover"].append(x[G15.index("cloud_cover")])
                conds["wind_speed_10m"].append(x[G15.index("wind_speed_10m")])
                conds["raw_range"].append(rr)
                conds["raw_change24"].append(rc)
                conds["obs_range"].append(orr)
                conds["obs_change24"].append(oc)
            for c, vals in conds.items():
                e, nv = edges_of(vals, 3)
                edge_rows.append([ic, label, c, "training rows", nv] + e + [""] * 7)
            e, nv = edges_of([r[4] for r in tr_rows], 10)
            edge_rows.append([ic, label, "forecast_decile", "training rows (raw GFS)", nv] + e)
            # the test forecasts' own values, forecast side only, for the two conditions with none on training rows
            ab, cmr = [], []
            for r in pred:
                if r[ix["status"]] != "scored":
                    continue
                pc = s97.parse_time(r[ix["cycle_utc"]])
                if not t0 <= pc < t1 or (GROUP[ic] == "dev" and r[ix["period"]] != label):
                    continue
                ab.append(abs(float(r[ix["b"]])))
                cmr.append(float(r[ix["curve"]]) - float(r[ix["raw_gfs"]]))
            for c, vals in (("abs_b", ab), ("curve_minus_raw", cmr)):
                e, nv = edges_of(vals, 3)
                edge_rows.append([ic, label, c, "test forecasts (forecast side only, no observation)", nv]
                                 + e + [""] * 7)
            checks.append(f"{ic} {label}: training rows (complete case, leads 3 to 48) {len(tr_rows):,}, cells 184, "
                          f"each equal to an independent count; climatology training hours {nclim:,}; latest "
                          f"training valid time {max(r[1] for r in tr_rows):%Y-%m-%dT%H:%M} < T0 {t0:%Y-%m-%d}")
        # the reference values on every prediction row
        out, missing = [], {}
        t0_of = {p: a for p, a, _, _ in periods(ic)}
        for r in pred:
            cycle = s97.parse_time(r[ix["cycle_utc"]])
            valid = s97.parse_time(r[ix["valid_utc"]])
            n, h = int(r[ix["lead"]]), int(r[ix["cycle_hour"]])
            cb, mos, clim, _ = models[t0_of[r[ix["period"]]]]
            temp = s97.fval(r[ix["raw_gfs"]])
            x = [s97.fval(r[ix[c]]) for c in G15]
            cl = clim[valid.hour, doy365(valid.date())]
            cl = None if np.isnan(cl) else float(cl)
            cbv = temp + cb[(h, n)] if temp is not None else None
            lm = None
            if all(v is not None for v in x):
                lm = temp + float(mos[(h, n)][0] + np.dot(mos[(h, n)][1:], x))
            pe = s106.hourly_persistence(cycle, valid, obs_map)
            rr, rc, orr, oc = conditions_of(cycle, valid, n, dv, obs_map)
            if r[ix["status"]] == "scored":
                for name, v in (("climatology", cl), ("constant_bias", cbv), ("linear_mos", lm), ("persistence", pe)):
                    if v is None:
                        missing[(r[ix["period"]], name)] = missing.get((r[ix["period"]], name), 0) + 1
            out.append([r[ix["cycle_utc"]], n, cl, cbv, lm, pe, rr, rc, orr, oc])
        data = gzip_bytes(s97.csv_text(REF_COLUMNS, [[fmt(v) for v in rr_] for rr_ in out]))
        ref_files[ic] = data
        # every whole hour's observation in the tables (the table's pairing), for daily persistence (D100.5)
        obs_files[ic] = gzip_bytes(s97.csv_text(["valid_utc", "obs"], [[tstr(v), fmt(o)] for v, o in
                                                                     sorted(obs_map.items())]))
        meta.append((ic, len(out), len(data), hashlib.sha256(data).hexdigest(), missing))
        print(f"  {ic}: {len(out):,} rows; missing on scored rows: "
              f"{', '.join(f'{p} {k} {v}' for (p, k), v in sorted(missing.items())) or 'none'} "
              f"({time.time() - t:.0f} s)", flush=True)
    head = ["icao", "edges_for", "condition", "source", "n_values"] + [f"edge_{k}" for k in range(1, 10)]
    text = s97.csv_text(head, [[fmt(v) if not isinstance(v, str) else v for v in r] for r in edge_rows])
    write_once_text(EDGES_OUT, text)
    print(f"wrote {EDGES_OUT.relative_to(ROOT)}: {len(edge_rows)} rows, SHA-256 {sha256_file(EDGES_OUT)}")
    lines = ["Session 112 references (D106.4) and table-based conditions (D106.6), written by --refs.",
             f"run {now_utc()}; {versions()}; script SHA-256 {sha256_file(Path(__file__))}",
             "rows aligned one to one with pred_<ICAO>.csv.gz. columns: " + ",".join(REF_COLUMNS), "checks:"]
    lines += ["  " + c for c in checks]
    lines.append("files:")
    for ic, n, nb, h, missing in meta:
        write_once_bytes(PRED_DIR / f"refs_{ic}.csv.gz", ref_files[ic])
        lines.append(f"  refs_{ic}.csv.gz  rows {n:,}  bytes {nb:,}  sha256 {h}")
        write_once_bytes(PRED_DIR / f"obs_{ic}.csv.gz", obs_files[ic])
        lines.append(f"  obs_{ic}.csv.gz  bytes {len(obs_files[ic]):,}  sha256 "
                     f"{hashlib.sha256(obs_files[ic]).hexdigest()}")
        lines.append("    missing on scored rows: " + ("; ".join(f"{p} {k} {v}" for (p, k), v in sorted(missing.items()))
                                                      or "none"))
    write_once_text(REFS_META, "\n".join(lines) + "\n")
    print(f"wrote 12 refs files and refs_meta.txt; run time {time.time() - t_start:.0f} s")
    return 0


# ------------------------------------------------------------------ statistics (D106.5, D106.7, D106.12)

SEED = 112
BLOCK = 7
NW_LAGS = 7
REPS_HEAD = 10_000
REPS_CELL = 2_000


def block_weights(rng, n, reps, block=BLOCK):
    """F125.3's moving-block bootstrap: ceil(n / 7) blocks of 7 consecutive days, starts uniform on
    0..n-7, truncated to n. Returns a (reps x n) matrix of how often each day is drawn."""
    if n < block:
        block = max(n, 1)
    nb = math.ceil(n / block)
    starts = rng.integers(0, n - block + 1, size=(reps, nb))
    idx = (starts[:, :, None] + np.arange(block)).reshape(reps, nb * block)[:, :n]
    flat = (np.arange(reps)[:, None] * n + idx).ravel()
    return np.bincount(flat, minlength=reps * n).reshape(reps, n).astype(float)


def ratio_interval(w, num, den):
    """95 % interval of sum(num) / sum(den) over the resampled days. num, den: (days x cells)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        r = (w @ num) / (w @ den)
    return np.nanpercentile(r, 2.5, axis=0), np.nanpercentile(r, 97.5, axis=0)


def skill_interval(w, num_a, num_ref):
    """95 % interval of 1 - sum(|e_a|) / sum(|e_ref|) over the resampled days (paired rows)."""
    with np.errstate(invalid="ignore", divide="ignore"):
        r = 1.0 - (w @ num_a) / (w @ num_ref)
    return np.nanpercentile(r, 2.5, axis=0), np.nanpercentile(r, 97.5, axis=0)


def dm_test(d, lags=NW_LAGS):
    """Diebold-Mariano on a daily series d (mean of |e_A| - |e_B|): the mean over its standard error
    with a Newey-West (Bartlett) variance at `lags` lags; two-sided normal p-value. (stat, p)."""
    d = np.asarray(d, dtype=float)
    t = len(d)
    m = float(d.mean())
    u = d - m
    v = float(u @ u) / t
    for k in range(1, lags + 1):
        if k < t:
            v += 2.0 * (1.0 - k / (lags + 1)) * float(u[k:] @ u[:-k]) / t
    if v <= 0:
        return (0.0, 1.0) if m == 0 else (math.copysign(math.inf, m), 0.0)
    z = m / math.sqrt(v / t)
    return z, math.erfc(abs(z) / math.sqrt(2.0))


def benjamini_hochberg(p, q=0.05):
    """Step-up: reject the k smallest p-values, k the largest rank with p_(k) <= k q / m."""
    p = np.asarray(p, dtype=float)
    m = len(p)
    order = np.argsort(p, kind="stable")
    ok = p[order] <= q * np.arange(1, m + 1) / m
    rej = np.zeros(m, dtype=bool)
    if ok.any():
        rej[order[:np.nonzero(ok)[0].max() + 1]] = True
    return rej


def peak_index(vals):
    """D106.7(e): the hour of the maximum; on a tie the first hour wins."""
    return int(np.argmax(np.asarray(vals, dtype=float)))


def is_edge(idx, n_hours):
    """D106.7(f): the maximum in the first or last local hour."""
    return idx == 0 or idx == n_hours - 1


def decompose(obs_max, obs_peak, fvals):
    """D106.7(d): e_max = [observed max - f at the observed peak hour] - [f max - f at the observed
    peak hour]. Returns (e_max, level term, timing term)."""
    f_at = fvals[obs_peak]
    fmax = max(fvals)
    return obs_max - fmax, obs_max - f_at, fmax - f_at


def metrics(e):
    """D106.5 on one error vector (observed minus forecast)."""
    e = np.asarray(e, dtype=float)
    a = np.abs(e)
    if not len(e):
        return {k: None for k in ("n", "mae", "me", "rmse", "med", "p90", "p95", "le1", "le2")}
    return {"n": len(e), "mae": float(a.mean()), "me": float(e.mean()), "rmse": float(np.sqrt((e * e).mean())),
            "med": float(np.median(a)), "p90": float(np.percentile(a, 90)), "p95": float(np.percentile(a, 95)),
            "le1": float((a <= 1).mean()), "le2": float((a <= 2).mean())}


# ------------------------------------------------------------------ Step 4: --check (synthetic data only)

def run_check(args):
    print(f"SESSION 112 --check (synthetic data only, no table or prediction read), start {now_utc()}")
    results = []

    def rep(name, ok, detail):
        results.append(ok)
        print(f"  {'PASS' if ok else 'FAIL'}: {name}: {detail}")

    # 1. bootstrap: a known mean's interval width. 100 independent series of 365 iid N(0, 1) days; the
    # mean width should be about 2 x 1.96 / sqrt(365) = 0.2052. (One series alone can carry chance
    # autocorrelation, which the block bootstrap rightly reflects, so the check averages over 100.)
    rng = np.random.default_rng(1)
    w = block_weights(np.random.default_rng(SEED), 365, REPS_CELL)
    widths = []
    for k in range(100):
        x = rng.normal(0.0, 1.0, 365)
        lo, hi = ratio_interval(w, x[:, None], np.ones((365, 1)))
        widths.append(float(hi[0] - lo[0]))
    want = 2 * 1.959964 / math.sqrt(365)
    got = float(np.mean(widths))
    rep("bootstrap width", abs(got / want - 1) < 0.10, f"mean width over 100 series {got:.4f}, normal theory "
        f"{want:.4f}, ratio {got / want:.3f} (tolerance 10 %)")
    w = block_weights(np.random.default_rng(SEED), 365, REPS_HEAD)
    rep("bootstrap blocks", bool((w.sum(1) == 365).all()) and w.shape == (REPS_HEAD, 365),
        "each of 10,000 resamples has 365 days")
    # 2. Diebold-Mariano
    e = rng.normal(0, 1, 730)
    z, p = dm_test(np.abs(e) - np.abs(e))
    rep("DM identical errors", 0.5 <= p <= 1.0, f"z {z}, p {p}")
    ps = []
    for k in range(200):
        r2 = np.random.default_rng(1000 + k)
        a, b = r2.normal(0, 1, 730), r2.normal(0, 1, 730)
        ps.append(dm_test(np.abs(a) - np.abs(b))[1])
    rep("DM same-distribution errors (200 pairs)", 0.4 <= float(np.mean(ps)) <= 0.6 and
        0.02 <= float(np.mean(np.asarray(ps) < 0.05)) <= 0.09,
        f"mean p {np.mean(ps):.3f}, share p < 0.05 {np.mean(np.asarray(ps) < 0.05):.3f}")
    z, p = dm_test(np.abs(e) - np.abs(e + 1.0) + 0 * e)
    a = rng.normal(0, 1, 730)
    z2, p2 = dm_test(np.abs(a) - (np.abs(a) + 0.5))
    rep("DM large constant gap", p2 < 0.01 and p < 0.01, f"gap 0.5: z {z2}, p {p2}; errors shifted by 1: z {z:.2f}, "
        f"p {p:.2e}")
    # 3. Benjamini-Hochberg, two hand-worked examples
    r1 = benjamini_hochberg([0.01, 0.04, 0.03, 0.005, 0.20])
    r2 = benjamini_hochberg([0.001, 0.012, 0.02, 0.035, 0.04, 0.3])
    rep("BH example 1", list(r1) == [True, True, True, True, False],
        "p 0.01 0.04 0.03 0.005 0.20 at q 0.05: thresholds 0.01 0.02 0.03 0.04 0.05 on the sorted p; "
        f"reject the four smallest; got {list(map(bool, r1))}")
    rep("BH example 2 (step-up)", list(r2) == [True, True, True, True, True, False],
        "p 0.001 0.012 0.02 0.035 0.04 0.3: p(4) = 0.035 > 0.0333 but p(5) = 0.04 <= 0.0417, so the five "
        f"smallest are rejected; got {list(map(bool, r2))}")
    # 4. the decomposition on made-up curves
    f = [10.0, 12.5, 15.25, 17.75, 17.5, 16.0, 13.0]
    o = [9.0, 11.0, 14.0, 16.5, 18.25, 17.0, 12.0]
    op = peak_index(o)
    em, lv, tm = decompose(max(o), op, f)
    rep("decomposition, exact values", em == lv - tm and em == max(o) - max(f) and op == 4 and tm == 0.25,
        f"e_max {em}, level {lv}, timing {tm}, level - timing {lv - tm}")
    worst = 0.0
    for k in range(1000):
        r3 = np.random.default_rng(5000 + k)
        f = list(r3.normal(15, 5, 24))
        o = list(r3.normal(15, 5, 24))
        em, lv, tm = decompose(max(o), peak_index(o), f)
        worst = max(worst, abs(em - (lv - tm)))
    rep("decomposition, 1,000 random curves", worst <= 1e-12, f"largest |e_max - (level - timing)| {worst:.2e}")
    # 5. peak hour and edge-of-day: ties (first wins), 23-hour and 25-hour days
    rep("peak tie", peak_index([1, 3, 3, 2]) == 1 and peak_index([5, 1, 5]) == 0,
        "[1, 3, 3, 2] -> 1; [5, 1, 5] -> 0 (an edge)")
    rep("edge rule", is_edge(0, 24) and is_edge(23, 24) and not is_edge(22, 24) and is_edge(22, 23)
        and is_edge(24, 25) and not is_edge(23, 25), "first and last hour of 23, 24 and 25-hour days")
    short = s104.local_day(dt.date(2024, 3, 31), "Europe/London")[2]
    long_ = s104.local_day(dt.date(2024, 10, 27), "Europe/London")[2]
    v23 = [1.0] * 22 + [2.0]
    v25 = [3.0] + [1.0] * 23 + [3.0]
    rep("23-hour and 25-hour days", len(short) == 23 and len(long_) == 25 and peak_index(v23) == 22
        and is_edge(peak_index(v23), len(short)) and peak_index(v25) == 0 and is_edge(peak_index(v25), len(long_)),
        f"Europe/London 2024-03-31 {len(short)} h, 2024-10-27 {len(long_)} h; last-hour peak on the 23-hour day "
        "is an edge; a tie between the first and last hour of the 25-hour day goes to the first")
    zones = {ic: sorted({len(s104.local_day(dt.date(2024, 1, 1) + k * DAY, TZNAME[ic])[2]) for k in range(366)})
             for ic in AIRPORTS}
    rep("day lengths per airport, 2024", all(set(v) <= {23, 24, 25} for v in zones.values()),
        "; ".join(f"{ic} {v}" for ic, v in zones.items()))
    # 6. metrics on a made-up vector
    m = metrics([1.0, -1.0, 2.0, -2.0, 0.5])
    rep("metrics", m["mae"] == 1.3 and m["me"] == 0.1 and m["le1"] == 0.6 and m["le2"] == 1.0,
        f"MAE {m['mae']}, mean error {m['me']}, share <= 1 {m['le1']}, share <= 2 {m['le2']}")
    ok = all(results)
    print(f"--check: {sum(results)} of {len(results)} PASS")
    return 0 if ok else 1


# ------------------------------------------------------------------ Steps 5 to 8: --analyse

FORECASTS = ["curve", "baseline", "linear_mos", "constant_bias", "raw_gfs", "climatology", "persistence"]
REFERENCES = ["raw_gfs", "persistence", "climatology", "constant_bias", "linear_mos", "baseline"]
LABEL = {"curve": "curve", "baseline": "baseline", "linear_mos": "linear MOS", "constant_bias": "constant bias",
         "raw_gfs": "raw GFS", "climatology": "climatology", "persistence": "persistence"}
# The validated reference palette (categorical slots in fixed order), light mode.
COLOR = {"curve": "#2a78d6", "raw_gfs": "#eb6834", "baseline": "#1baf7a", "linear_mos": "#eda100",
         "constant_bias": "#e87ba4", "climatology": "#008300", "persistence": "#6250d6"}
INK, INK2, GRIDC, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
MAIN4 = ["curve", "baseline", "linear_mos", "raw_gfs"]
BANDS = [(3, 12), (13, 24), (25, 36), (37, 48)]
SEASON_OF = {12: "Dec-Feb", 1: "Dec-Feb", 2: "Dec-Feb", 3: "Mar-May", 4: "Mar-May", 5: "Mar-May",
             6: "Jun-Aug", 7: "Jun-Aug", 8: "Jun-Aug", 9: "Sep-Nov", 10: "Sep-Nov", 11: "Sep-Nov"}
SEASONS = ["Dec-Feb", "Mar-May", "Jun-Aug", "Sep-Nov"]
DSS_BANDS = [(0, 30), (31, 90), (91, 180), (181, 365), (366, 10 ** 6)]
DSS_NAMES = ["0-30", "31-90", "91-180", "181-365", "over 365"]
TERC = ["low", "mid", "high"]
PCTS = [5, 10, 25, 50, 75, 90, 95]
EPOCH = dt.datetime(1970, 1, 1)
CONTRIB_LEADS = (6, 12, 18, 24, 36, 48)


def h_of(t):
    return int((t - EPOCH).total_seconds()) // 3600


def dt_of(h):
    return EPOCH + dt.timedelta(hours=int(h))


def tohours(strs):
    return np.array([s[:16] for s in strs], dtype="datetime64[m]").astype("datetime64[h]").astype(np.int64)


def fl(col):
    return np.array([float(x) if x != "" else np.nan for x in col])


def refs_hashes():
    return pred_hashes(REFS_META)


def load_edges():
    out = {}
    with open(EDGES_OUT, newline="") as f:
        for r in csv.DictReader(f):
            k = 2 if r["condition"] != "forecast_decile" else 9
            out[(r["icao"], r["edges_for"], r["condition"])] = [float(r[f"edge_{j}"]) for j in range(1, k + 1)]
    return out


def edges_label(ic, period):
    return "A+B" if GROUP[ic] == "claim" else period


def load_airport(ic, edges):
    """Every prediction row of one airport, with its references and conditions, as arrays."""
    pred = load_pred_rows(ic)
    name = f"refs_{ic}.csv.gz"
    head, refs = read_gz_csv(PRED_DIR / name, refs_hashes()[name])
    if head != REF_COLUMNS or len(refs) != len(pred):
        raise SystemExit(f"STOP: {name} does not align with the predictions")
    pc = dict(zip(PRED_COLUMNS, zip(*pred)))
    rc = dict(zip(REF_COLUMNS, zip(*refs)))
    if pc["cycle_utc"] != rc["cycle_utc"] or pc["lead"] != rc["lead"]:
        raise SystemExit(f"STOP: {name} rows are not in the predictions' order")
    A = {"period": np.array(pc["period"]), "cycle": tohours(pc["cycle_utc"]), "valid": tohours(pc["valid_utc"]),
         "ch": np.array(pc["cycle_hour"], dtype=int), "lead": np.array(pc["lead"], dtype=int),
         "lhour": np.array(pc["local_hour"], dtype=int),
         "month": np.array([int(s[5:7]) for s in pc["local_date"]]),
         "status": np.array(pc["status"]), "obs": fl(pc["obs"]), "raw_gfs": fl(pc["raw_gfs"]),
         "baseline": fl(pc["baseline"]), "b": fl(pc["b"]), "curve": fl(pc["curve"]),
         "cloud_cover": fl(pc["cloud_cover"]), "wind_speed_10m": fl(pc["wind_speed_10m"])}
    for c in ("climatology", "constant_bias", "linear_mos", "persistence", "raw_range", "raw_change24", "obs_range",
              "obs_change24"):
        A[c] = fl(rc[c])
    A["abs_b"] = np.abs(A["b"])
    A["curve_minus_raw"] = A["curve"] - A["raw_gfs"]
    A["scored"] = A["status"] == "scored"
    starts = {p: h_of(t0) for p, t0, _, _ in periods(ic)}      # the tracker's start (D97.7, D100.3)
    A["dss"] = (A["cycle"] - np.array([starts[p] for p in A["period"]])) // 24
    A["day"] = A["cycle"] // 24                                     # the bootstrap's day: the cycle's UTC date
    A["season"] = np.array([SEASONS.index(SEASON_OF[m]) for m in A["month"]])
    # bins
    B = {"lead": A["lead"], "lead_band": np.select([A["lead"] <= hi for _, hi in BANDS], range(4), -1),
         "cycle_hour": A["ch"], "local_hour": A["lhour"], "month": A["month"], "season": A["season"],
         "days_since_start": np.select([A["dss"] <= hi for _, hi in DSS_BANDS], range(5), -1)}
    el = np.array([edges_label(ic, p) for p in A["period"]])
    for c in TERCILE_CONDITIONS:
        b = np.full(len(el), -1)
        for lab in set(el):
            m = (el == lab) & np.isfinite(A[c])
            b[m] = np.searchsorted(edges[(ic, lab, c)], A[c][m], side="right")
        B[c] = b
    A["dec"] = {}
    for f in FORECASTS:
        b = np.full(len(el), -1)
        for lab in set(el):
            m = (el == lab) & np.isfinite(A[f])
            b[m] = np.searchsorted(edges[(ic, lab, "forecast_decile")], A[f][m], side="right")
        A["dec"][f] = b
    obs = {}
    name = f"obs_{ic}.csv.gz"
    head, orows = read_gz_csv(PRED_DIR / name, refs_hashes()[name])
    for v, o in orows:
        obs[s97.parse_time(v)] = None if o == "" else float(o)
    return A, B, obs


BIN_NAMES = {"lead_band": [f"{a}-{b}" for a, b in BANDS], "days_since_start": DSS_NAMES, "season": SEASONS,
             **{c: TERC for c in TERCILE_CONDITIONS}}
COND_ORDER = ["lead", "lead_band", "cycle_hour", "local_hour", "month", "season", "cloud_cover", "wind_speed_10m",
              "raw_range", "raw_change24", "abs_b", "curve_minus_raw", "obs_range", "obs_change24", "days_since_start"]
SECONDARY = ("obs_range", "obs_change24")


def bin_label(c, b):
    return BIN_NAMES[c][b] if c in BIN_NAMES else str(int(b))


class Sums:
    """Per-day sums of |e|, e and counts for many cells, for the bootstrap (D106.12)."""

    def __init__(self, day, n_days):
        self.day, self.nd = day, n_days
        self.abs, self.e, self.c, self.keys = [], [], [], []

    def add(self, key, mask, err):
        d = self.day[mask]
        self.keys.append(key)
        self.abs.append(np.bincount(d, weights=np.abs(err[mask]), minlength=self.nd))
        self.e.append(np.bincount(d, weights=err[mask], minlength=self.nd))
        self.c.append(np.bincount(d, minlength=self.nd).astype(float))

    def mats(self):
        return np.array(self.abs).T, np.array(self.e).T, np.array(self.c).T


def save_fig(fig, name, figs):
    import matplotlib.pyplot as plt
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", metadata={"Date": None})
    plt.close(fig)
    data = buf.getvalue()
    write_once_bytes(FIG_DIR / name, data)
    figs.append((name, len(data), hashlib.sha256(data).hexdigest()))


def plt_setup():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"svg.hashsalt": "session112", "font.size": 7.5, "axes.titlesize": 8,
                         "axes.edgecolor": INK2, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
                         "text.color": INK, "axes.grid": True, "grid.color": GRIDC, "grid.linewidth": 0.6,
                         "axes.spines.top": False, "axes.spines.right": False, "lines.linewidth": 1.4,
                         "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "legend.frameon": False,
                         "svg.fonttype": "none"})
    return plt


def grid12(plt, title, sharey=False, sharex=True, h=11.0):
    fig, axes = plt.subplots(4, 3, figsize=(10, h), sharex=sharex, sharey=sharey, constrained_layout=True)
    for ax, ic in zip(axes.flat, AIRPORTS):
        ax.set_title(ic + ("" if GROUP[ic] == "claim" else " (dev)") + (", sea" if ic in SEA else ""), loc="left")
    import textwrap
    fig.suptitle(textwrap.fill(title, 140) + "\nClaim airports in rows 1 and 2. (dev) = " + DEV_FLAG, fontsize=8.5,
                 x=0.01, ha="left")
    return fig, dict(zip(AIRPORTS, axes.flat))


def legend_below(fig, ax_map, n=4):
    h, l = next(iter(ax_map.values())).get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=n, bbox_to_anchor=(0.5, -0.01))


def plain(v):
    """numpy scalars as Python numbers, so that fmt gives plain text."""
    if isinstance(v, np.bool_):
        return bool(v)
    if isinstance(v, np.integer):
        return int(v)
    if isinstance(v, np.floating):
        return float(v)
    return v


def write_table(name, header, rows, tables):
    text = s97.csv_text(header, [[v if isinstance(v, str) else fmt(plain(v)) for v in r] for r in rows])
    write_once_text(OUT_DIR / name, text)
    tables.append((name, len(rows), hashlib.sha256(text.encode()).hexdigest()))


def pct_row(e):
    e = np.asarray(e, dtype=float)
    return [len(e)] + ([float(x) for x in np.percentile(e, PCTS)] if len(e) else [None] * len(PCTS))


class DayBuilder:
    """Local days of D106.7: their observed maximum, peak hour and range, and each forecast's maximum,
    peak hour, value at the observed peak hour and range."""

    def __init__(self, ic, A, obs):
        self.ic, self.tz, self.obs = ic, TZNAME[ic], obs
        self.obs_h = {h_of(t): o for t, o in obs.items()}
        self.ix = {(int(c), int(n)): i for i, (c, n) in enumerate(zip(A["cycle"], A["lead"]))}
        self.f = {f: A[f].tolist() for f in FORECASTS if f != "persistence"}
        self._ld = {}

    def local_day(self, d):
        if d not in self._ld:
            s, e, hours = s104.local_day(d, self.tz)
            self._ld[d] = (s, hours, [h_of(h) for h in hours])
        return self._ld[d]

    def record(self, c, d, day_no, period):
        s, hours, hh = self.local_day(d)
        ch_ = h_of(c)
        idx = [self.ix.get((ch_, h - ch_)) for h in hh]
        ov = [self.obs_h.get(h) for h in hh]
        usable = [i for i, v in enumerate(ov) if v is not None]
        ok = hours[-1] <= LAST_VALID and all(h in self.obs_h for h in hh) and s104.usable_day(len(hh), len(usable))
        r = {"date": d, "period": period, "cycle": c, "ch": c.hour, "day_no": day_no, "hours": len(hh),
             "obs_max": None, "obs_pk": None, "obs_rng": None}
        if ok:
            om = max(ov[i] for i in usable)
            r["obs_max"] = om
            r["obs_pk"] = next(i for i in usable if ov[i] == om)          # first hour wins (D106.7(e))
            r["obs_rng"] = om - min(ov[i] for i in usable)
            r["obs_edge"] = is_edge(r["obs_pk"], len(hh))
        for f, vals in self.f.items():
            v = [vals[i] if i is not None else math.nan for i in idx]
            if any(math.isnan(x) for x in v):
                r[f] = None
                continue
            pk = peak_index(v)
            r[f], r[f + "_pk"], r[f + "_rng"] = v[pk], pk, max(v) - min(v)
            r[f + "_edge"] = is_edge(pk, len(hh))
            if ok:
                r[f + "_at"] = v[r["obs_pk"]]
        pd_, pv = s106.daily_persistence(d, c, self.tz, self.obs)
        r["persistence"] = pv
        return r


def scored_days(ic, A, db):
    """D98.10's days (D106.7(a)): one cycle per day, the latest with c + 4 h <= the day's start."""
    period_of = s106.look_of if GROUP[ic] == "claim" else s104.fold_of
    first = periods(ic)[0][2].date() - DAY
    last = periods(ic)[-1][3].date()
    out = []
    d = first
    while d <= last:
        s, hours, hh = db.local_day(d)
        c = s104.day_cycle(s)
        p = period_of(c)
        if p is not None and hours[-1] <= LAST_VALID:
            out.append(db.record(c, d, 1, p))
        d += DAY
    return out


def every_cycle_days(ic, A, db):
    """D106.7(b): for each cycle, every local day wholly inside leads 3 to 48, numbered in run order."""
    out = []
    cyc = sorted(set(zip(A["cycle"].tolist(), A["period"].tolist())))
    for c_h, p in cyc:
        c = dt_of(c_h)
        d0 = local_of(c + 3 * HOUR, db.tz)[0]
        d1 = local_of(c + 48 * HOUR, db.tz)[0]
        k = 0
        d = d0
        while d <= d1:
            s, hours, hh = db.local_day(d)
            if hh[0] - c_h >= 3 and hh[-1] - c_h <= 48:
                k += 1
                r = db.record(c, d, k, p)
                r["first_lead"] = hh[0] - c_h
                out.append(r)
            d += DAY
    return out


def days_arrays(days):
    keys = set()
    for r in days:
        keys |= set(r)
    out = {}
    for k in keys:
        vals = [r.get(k) for r in days]
        if k in ("date", "cycle", "period"):
            out[k] = vals
        else:
            out[k] = np.array([np.nan if v is None else float(v) for v in vals])
    return out


def record_days_check(ic, days, rec_d, rec_c):
    """The scored days against the record's day files (F147.6, F150): (compared, equal)."""
    want = rec_c if GROUP[ic] == "claim" else rec_d
    key0 = ic if GROUP[ic] == "claim" else STATION[ic]
    eq = comp = 0
    got = {r["date"].isoformat(): r for r in days}
    for (k, date), w in want.items():
        if k != key0:
            continue
        comp += 1
        g = got.get(date)
        eq += g is not None and tstr(g["cycle"]) == w["cycle"] and g["obs_max"] == w["obs_max"] \
            and g["raw_gfs"] == w["raw_gfs_max"] and g["curve"] == w["curve_max"] \
            and g["baseline"] == w["baseline_max"]
    return comp, eq, len(got)


def run_analyse(args):
    t_start = time.time()
    plt = plt_setup()
    print(f"SESSION 112 --analyse (offline), start {now_utc()}; {versions()}")
    print("DESCRIPTIVE ONLY (D106.2). Nothing is selected or tuned.")
    for p in (EDGES_OUT, REFS_META, PRED_META):
        if not p.exists():
            raise SystemExit(f"STOP: {p} is missing; run --regen and --refs first")
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    edges = load_edges()
    _, rec_d, _, rec_c = read_records()
    rng = np.random.default_rng(SEED)
    T = {k: [] for k in ("head", "skill", "brk", "cbias", "dhead", "dskill", "devery", "dext", "ddec", "dpeak",
                         "dpeakhist", "dedge", "drng", "dlead", "hrng", "shape", "smooth", "r2r", "dr2r", "limits", "bsum",
                         "dm")}
    F = {}            # figure data per airport
    checks = []
    for ic in AIRPORTS:
        t = time.time()
        A, B, obs = load_airport(ic, edges)
        S = A["scored"]
        if not np.all(np.isfinite(A["obs"][S]) & np.isfinite(A["curve"][S]) & np.isfinite(A["raw_gfs"][S])):
            raise SystemExit(f"STOP: {ic}: a scored row lacks the observation, raw GFS or the curve")
        E = {f: A["obs"] - A[f] for f in FORECASTS}
        days_u, day_idx = np.unique(A["day"][S], return_inverse=True)
        nD = len(days_u)
        di = np.full(len(S), -1)
        di[np.nonzero(S)[0]] = day_idx
        plist = [p for p, _, _, _ in periods(ic)]
        fd = F[ic] = {}
        # ---------------- hourly headline (D106.5), per period (10,000 resamples) and pooled
        for p in plist + ["all"]:
            mp = S & ((A["period"] == p) if p != "all" else True)
            dsel = np.unique(di[mp])
            remap = np.full(nD, -1)
            remap[dsel] = np.arange(len(dsel))
            sm = Sums(remap[np.where(di >= 0, di, 0)], len(dsel))
            for f in FORECASTS:
                m = mp & np.isfinite(E[f])
                sm.add(("f", f), m, E[f])
            for r in REFERENCES:
                m = mp & np.isfinite(E[r]) & np.isfinite(E["curve"])
                sm.add(("sk_c", r), m, E["curve"])
                sm.add(("sk_r", r), m, E[r])
            for f in FORECASTS:
                if f == "raw_gfs":
                    continue
                m = mp & np.isfinite(E[f])
                sm.add(("rv_f", f), m, E[f])
                sm.add(("rv_r", f), m, E["raw_gfs"])
            w = block_weights(rng, len(dsel), REPS_HEAD)
            ma, me, mc = sm.mats()
            lo_a, hi_a = ratio_interval(w, ma, mc)
            lo_e, hi_e = ratio_interval(w, me, mc)
            K = {k: j for j, k in enumerate(sm.keys)}
            for f in FORECASTS:
                m = mp & np.isfinite(E[f])
                mt = metrics(E[f][m])
                j = K[("f", f)]
                sk = sk_lo = sk_hi = None
                if f != "raw_gfs":
                    a, b = K[("rv_f", f)], K[("rv_r", f)]
                    sk = 1 - ma[:, a].sum() / ma[:, b].sum()
                    l_, h_ = skill_interval(w, ma[:, [a]], ma[:, [b]])
                    sk_lo, sk_hi = float(l_[0]), float(h_[0])
                T["head"].append([ic, GROUP[ic], p, f, mt["n"], mt["mae"], float(lo_a[j]), float(hi_a[j]), mt["me"],
                                  float(lo_e[j]), float(hi_e[j]), mt["rmse"], mt["med"], mt["p90"], mt["p95"],
                                  mt["le1"], mt["le2"], sk, sk_lo, sk_hi, int((S & ((A["period"] == p) if p != "all"
                                                                                       else True)).sum() - mt["n"])])
            for r in REFERENCES:
                a, b = K[("sk_c", r)], K[("sk_r", r)]
                sk = 1 - ma[:, a].sum() / ma[:, b].sum()
                l_, h_ = skill_interval(w, ma[:, [a]], ma[:, [b]])
                T["skill"].append([ic, GROUP[ic], p, r, int(mc[:, a].sum()), sk, float(l_[0]), float(h_[0])])
            if p == "all":
                w_all = w
        # ---------------- breakdowns (D106.6, D106.9), pooled over periods, 2,000 resamples
        sm = Sums(np.where(di >= 0, di, 0), nD)
        per_period = []
        for c in COND_ORDER:
            for b in sorted(set(B[c][S].tolist()) - {-1}):
                mb = S & (B[c] == b)
                for f in FORECASTS:
                    m = mb & np.isfinite(E[f])
                    if not m.any():
                        continue
                    sm.add((c, b, f), m, E[f])
                    per_period.append([float(np.mean(np.abs(E[f][m & (A["period"] == p)])))
                                       if (m & (A["period"] == p)).any() else None for p in plist])
        w = block_weights(rng, nD, REPS_CELL)
        ma, me, mc = sm.mats()
        lo_a, hi_a = ratio_interval(w, ma, mc)
        lo_e, hi_e = ratio_interval(w, me, mc)
        for j, (c, b, f) in enumerate(sm.keys):
            n = mc[:, j].sum()
            pp = per_period[j]
            ppv = [v for v in pp if v is not None]
            T["brk"].append([ic, GROUP[ic], c, "secondary" if c in SECONDARY else "primary", bin_label(c, b), f,
                             int(n), ma[:, j].sum() / n, float(lo_a[j]), float(hi_a[j]), me[:, j].sum() / n,
                             float(lo_e[j]), float(hi_e[j]), min(ppv), max(ppv),
                             ";".join(f"{p}:{'' if v is None else round(v, 4)}" for p, v in zip(plist, pp))])
        fd["brk"] = {(c, b, f): (ma[:, j].sum() / mc[:, j].sum(), me[:, j].sum() / mc[:, j].sum(),
                                 float(lo_a[j]), float(hi_a[j])) for j, (c, b, f) in enumerate(sm.keys)}
        # ---------------- conditional bias (D106.5)
        for f in ("raw_gfs", "linear_mos", "baseline", "curve"):
            m = S & np.isfinite(E[f])
            x, y = A[f][m], A["obs"][m]
            slope = float(np.cov(x, y, bias=True)[0, 1] / np.var(x))
            fd.setdefault("cb", {})[f] = []
            for dcl in range(10):
                md = m & (A["dec"][f] == dcl)
                if md.any():
                    T["cbias"].append([ic, GROUP[ic], f, dcl + 1, int(md.sum()), float(A[f][md].mean()),
                                       float(A["obs"][md].mean()), float(E[f][md].mean()), slope])
                    fd["cb"][f].append((float(A[f][md].mean()), float(E[f][md].mean())))
        # ---------------- distributions for the figures
        q = np.linspace(0, 1, 201)
        fd["box"] = {f: np.percentile(E[f][S & np.isfinite(E[f])], [5, 25, 50, 75, 95]) for f in FORECASTS}
        fd["ecdf"] = {f: np.quantile(np.abs(E[f][S & np.isfinite(E[f])]), q) for f in MAIN4}
        # ---------------- hourly ranges (D106.7(g)), curve and raw GFS
        for f in ("curve", "raw_gfs"):
            for n in LEADS:
                m = S & (A["lead"] == n)
                T["hrng"].append([ic, GROUP[ic], f, str(n), "all", *pct_row(E[f][m])])
                for si, sn in enumerate(SEASONS):
                    T["hrng"].append([ic, GROUP[ic], f, str(n), sn, *pct_row(E[f][m & (A["season"] == si)])])
            for lo_, hi_ in BANDS:
                m = S & (A["lead"] >= lo_) & (A["lead"] <= hi_)
                T["hrng"].append([ic, GROUP[ic], f, f"band {lo_}-{hi_}", "all", *pct_row(E[f][m])])
        fd["hfan"] = np.array([np.percentile(E["curve"][S & (A["lead"] == n)], PCTS) for n in LEADS])
        # ---------------- drift: b over time (D106.9)
        bd = {}
        for p in plist:
            m = S & (A["period"] == p)
            T["bsum"].append([ic, GROUP[ic], p, int(m.sum()), float(A["b"][m].mean()), float(np.abs(A["b"][m]).mean()),
                              float(np.percentile(np.abs(A["b"][m]), 95))])
        u, inv = np.unique(A["day"][S], return_inverse=True)
        bd = (u, np.bincount(inv, weights=A["b"][S]) / np.bincount(inv))
        fd["b_time"] = bd
        # ---------------- smoothness and run-to-run (D106.8)
        same = (A["cycle"][1:-1] == A["cycle"][:-2]) & (A["cycle"][1:-1] == A["cycle"][2:]) & \
            (A["lead"][2:] - A["lead"][:-2] == 2)
        sd = {}
        fin = np.isfinite(A["raw_gfs"]) & np.isfinite(A["curve"]) & np.isfinite(A["obs"])
        okt = same & fin[1:-1] & fin[:-2] & fin[2:]
        for f in ("raw_gfs", "curve", "obs"):
            x = A[f]
            d2 = x[2:] - 2 * x[1:-1] + x[:-2]
            sd[f] = float(np.mean(np.abs(d2[okt])))
        T["smooth"].append([ic, GROUP[ic], int(okt.sum()), sd["raw_gfs"], sd["curve"], sd["obs"]])
        fd["smooth"] = sd
        key = A["cycle"] * 64 + A["lead"]
        order = np.argsort(key)
        pk = (A["cycle"] - 6) * 64 + A["lead"] + 6
        pos = np.searchsorted(key[order], pk)
        pos = np.clip(pos, 0, len(key) - 1)
        hit = key[order][pos] == pk
        partner = np.where(hit, order[pos], -1)
        fd["r2r"] = {}
        for f in ("raw_gfs", "curve"):
            v = np.where(partner >= 0, A[f][np.clip(partner, 0, None)], np.nan)
            ch = np.abs(A[f] - v)
            fd["r2r"][f] = []
            for n in range(3, 43):
                m = (A["lead"] == n) & np.isfinite(ch)
                T["r2r"].append([ic, GROUP[ic], f, n, int(m.sum()), float(ch[m].mean())])
                fd["r2r"][f].append(float(ch[m].mean()))
        # ---------------- limits (D106.11)
        ob = A["obs"][S]
        whole = float(np.mean(ob == np.round(ob)))
        T["limits"].append([ic, GROUP[ic], "yes" if ic in SEA else "no", int(S.sum()), whole, 0.25,
                            float(np.mean(np.abs(E["curve"][S]))), float(np.mean(np.abs(E["raw_gfs"][S])))])
        # ---------------- DM, hourly families (D106.12); interval with the pooled headline's resamples
        for fam, a, b in ((1, "curve", "raw_gfs"), (3, "curve", "linear_mos"), (4, "curve", "baseline")):
            m = S & np.isfinite(E[a]) & np.isfinite(E[b])
            dd = np.abs(E[a][m]) - np.abs(E[b][m])
            ds = np.bincount(di[m], weights=dd, minlength=nD)
            dc = np.bincount(di[m], minlength=nD)
            keep = dc > 0
            series = ds[keep] / dc[keep]
            z, pv = dm_test(series)
            if keep.all():
                lo_, hi_ = ratio_interval(w_all, series[:, None], np.ones((nD, 1)))
            else:
                ww = block_weights(rng, int(keep.sum()), REPS_HEAD)
                lo_, hi_ = ratio_interval(ww, series[:, None], np.ones((int(keep.sum()), 1)))
            T["dm"].append([fam, ic, GROUP[ic], LABEL[a], LABEL[b], "hourly", int(keep.sum()), int(m.sum()),
                            float(series.mean()), float(lo_[0]), float(hi_[0]), z, pv])
        # ---------------- the daily maximum (D106.7)
        db = DayBuilder(ic, A, obs)
        sdays = scored_days(ic, A, db)
        comp, eq, ngot = record_days_check(ic, sdays, rec_d, rec_c)
        checks.append(f"{ic}: scored days against the record's day file: {eq} of {comp} equal (cycle, observed, raw "
                      f"GFS, baseline and curve maxima); days built {ngot}")
        if not (comp == eq == ngot):
            raise SystemExit(f"STOP: {ic}: the scored days do not reproduce the record")
        D = days_arrays(sdays)
        common = np.isfinite(D["obs_max"]) & np.isfinite(D["raw_gfs"]) & np.isfinite(D["baseline"]) & \
            np.isfinite(D["curve"])
        DE = {f: D["obs_max"] - D[f] for f in FORECASTS}
        dates = np.array([d.toordinal() for d in D["date"]])
        dper = np.array(D["period"])
        for p in plist + ["all"]:
            mp = common & ((dper == p) if p != "all" else True)
            nd_ = int(mp.sum())
            sm = Sums(np.cumsum(mp) - 1, nd_)
            for f in FORECASTS:
                m = mp & np.isfinite(DE[f])
                sm.add(("f", f), m, DE[f])
            for r in REFERENCES:
                m = mp & np.isfinite(DE[r])
                sm.add(("sk_c", r), m, DE["curve"])
                sm.add(("sk_r", r), m, DE[r])
            w = block_weights(rng, nd_, REPS_HEAD)
            ma, me, mc = sm.mats()
            lo_a, hi_a = ratio_interval(w, ma, mc)
            lo_e, hi_e = ratio_interval(w, me, mc)
            K = {k: j for j, k in enumerate(sm.keys)}
            for f in FORECASTS:
                m = mp & np.isfinite(DE[f])
                mt = metrics(DE[f][m])
                j = K[("f", f)]
                T["dhead"].append([ic, GROUP[ic], p, f, mt["n"], mt["mae"], float(lo_a[j]), float(hi_a[j]), mt["me"],
                                   float(lo_e[j]), float(hi_e[j]), mt["rmse"], mt["med"], mt["p90"], mt["p95"],
                                   mt["le1"], mt["le2"], int(mp.sum() - mt["n"])])
            for r in REFERENCES:
                a, b = K[("sk_c", r)], K[("sk_r", r)]
                l_, h_ = skill_interval(w, ma[:, [a]], ma[:, [b]])
                T["dskill"].append([ic, GROUP[ic], p, r, int(mc[:, a].sum()), 1 - ma[:, a].sum() / ma[:, b].sum(),
                                    float(l_[0]), float(h_[0])])
            if p == "all":
                w_dall = w
        mall = common
        dseries = (np.abs(DE["curve"]) - np.abs(DE["raw_gfs"]))[mall]
        z, pv = dm_test(dseries)
        lo_, hi_ = ratio_interval(w_dall, dseries[:, None], np.ones((len(dseries), 1)))
        T["dm"].append([2, ic, GROUP[ic], "curve", "raw GFS", "daily maximum", len(dseries), len(dseries),
                        float(dseries.mean()), float(lo_[0]), float(hi_[0]), z, pv])
        fd["dbox"] = {f: DE[f][common & np.isfinite(DE[f])] for f in FORECASTS}
        # (c) extremes, (d) decomposition, (e) peak hour, (f) edge-of-day: on the scored days, 2,000 resamples
        nd_ = int(common.sum())
        w = block_weights(rng, nd_, REPS_CELL)
        cidx = np.cumsum(common) - 1
        sm = Sums(cidx, nd_)
        for by, src in (("forecast maximum (curve)", D["curve"]), ("observed maximum", D["obs_max"])):
            lo_t, hi_t = np.percentile(src[common], [10, 90])
            for tail, sel in (("hottest 10 %", src >= hi_t), ("coldest 10 %", src <= lo_t)):
                for f in FORECASTS:
                    m = common & sel & np.isfinite(DE[f])
                    sm.add((by, tail, float(hi_t if tail.startswith("hot") else lo_t), f), m, DE[f])
        ma, me, mc = sm.mats()
        lo_a, hi_a = ratio_interval(w, ma, mc)
        lo_e, hi_e = ratio_interval(w, me, mc)
        fd["ext"] = {}
        for j, (by, tail, thr, f) in enumerate(sm.keys):
            n = mc[:, j].sum()
            T["dext"].append([ic, GROUP[ic], by, tail, thr, f, int(n), ma[:, j].sum() / n, float(lo_a[j]),
                              float(hi_a[j]), me[:, j].sum() / n, float(lo_e[j]), float(hi_e[j])])
            fd["ext"][(by, tail, f)] = (me[:, j].sum() / n, float(lo_e[j]), float(hi_e[j]))
        fd["dec"] = {}
        for f in ("raw_gfs", "linear_mos", "baseline", "curve"):
            m = common & np.isfinite(D.get(f + "_at", np.full(len(common), np.nan)))
            em = D["obs_max"][m] - D[f][m]
            lv = D["obs_max"][m] - D[f + "_at"][m]
            tm = D[f][m] - D[f + "_at"][m]
            T["ddec"].append([ic, GROUP[ic], f, int(m.sum()), float(em.mean()), float(lv.mean()), float(tm.mean()),
                              float(np.mean(tm > 0)), float(np.max(np.abs(em - (lv - tm))))])
            fd["dec"][f] = (float(em.mean()), float(lv.mean()), float(tm.mean()))
        fd["peak"] = {}
        for f in ("raw_gfs", "baseline", "curve"):
            m = common
            dh = D[f + "_pk"][m] - D["obs_pk"][m]
            a = np.abs(dh)
            T["dpeak"].append([ic, GROUP[ic], f, int(m.sum()), float(dh.mean()), float(a.mean()), float(np.mean(a == 0)),
                               float(np.mean(a <= 1)), float(np.mean(a <= 2)), float(np.mean(a <= 3))])
            vals, cnts = np.unique(dh.astype(int), return_counts=True)
            for v_, c_ in zip(vals, cnts):
                T["dpeakhist"].append([ic, GROUP[ic], f, int(v_), int(c_)])
            fd["peak"][f] = dh
        # every cycle (D106.7(b))
        edays = every_cycle_days(ic, A, db)
        V = days_arrays(edays)
        VE = {f: V["obs_max"] - V[f] for f in FORECASTS}
        vok = np.isfinite(V["obs_max"]) & np.isfinite(V["curve"]) & np.isfinite(V["raw_gfs"])
        vdates, vdi = np.unique(np.array([d.toordinal() for d in V["date"]])[vok], return_inverse=True)
        vday = np.full(len(vok), 0)
        vday[np.nonzero(vok)[0]] = vdi
        sm = Sums(vday, len(vdates))
        for ch in s97.CYCLE_HOURS:
            for k in (1, 2):
                for f in FORECASTS:
                    m = vok & (V["ch"] == ch) & (V["day_no"] == k) & np.isfinite(VE[f])
                    if m.any():
                        sm.add((ch, k, f), m, VE[f])
        for k in (1, 2):
            for f in FORECASTS:
                m = vok & (V["day_no"] == k) & np.isfinite(VE[f])
                if m.any():
                    sm.add(("all", k, f), m, VE[f])
        for ch in s97.CYCLE_HOURS:
            m = V["ch"] == ch
            fl_ = V["first_lead"][m]
            T["dlead"].append([ic, GROUP[ic], ch, int(m.sum()), int((m & vok).sum()),
                               int(fl_.min()) if m.any() else None, int(fl_.max()) if m.any() else None])
        w = block_weights(rng, len(vdates), REPS_CELL)
        ma, me, mc = sm.mats()
        lo_a, hi_a = ratio_interval(w, ma, mc)
        lo_e, hi_e = ratio_interval(w, me, mc)
        fd["every"] = {}
        for j, (ch, k, f) in enumerate(sm.keys):
            n = mc[:, j].sum()
            T["devery"].append([ic, GROUP[ic], str(ch), k, f, int(n), ma[:, j].sum() / n, float(lo_a[j]),
                                float(hi_a[j]), me[:, j].sum() / n, float(lo_e[j]), float(hi_e[j])])
            fd["every"][(ch, k, f)] = (ma[:, j].sum() / n, float(lo_a[j]), float(hi_a[j]))
        checks.append(f"{ic}: every-cycle days {len(edays):,} (day 1 {int((V['day_no'] == 1).sum()):,}, day 2 "
                      f"{int((V['day_no'] == 2).sum()):,}); with an observed maximum and both raw GFS and curve "
                      f"maxima {int(vok.sum()):,}; scored days that are day 1 of their cycle: "
                      f"{int((D['day_no'] == 1).sum())} of {len(sdays)}")
        # (f) edge-of-day, on the scored days and on every cycle's day 1 and day 2
        fd["edge"] = {}
        for setname, X, XE, ok_ in [("scored days", D, DE, common), ("every cycle", V, VE, vok)] + \
                [(f"every cycle, {ch:02d}z", V, VE, vok & (V["ch"] == ch)) for ch in s97.CYCLE_HOURS]:
            oe = (X["obs_edge"] == 1) & ok_
            ce = (X["curve_edge"] == 1) & ok_
            re_ = (X["raw_gfs_edge"] == 1) & ok_
            anye = oe | ce | re_
            row = [ic, GROUP[ic], setname, int(ok_.sum()), int(oe.sum()), int(ce.sum()), int(re_.sum()), int(anye.sum()),
                   int((ce & oe).sum()), int((ce & ~oe).sum()), int((~ce & oe & ok_).sum()),
                   int((~ce & ~oe & ok_).sum()), int((re_ & oe).sum()), int((re_ & ~oe).sum()),
                   int((~re_ & oe & ok_).sum()), int((~re_ & ~oe & ok_).sum())]
            for f in ("curve", "raw_gfs"):
                for sel in (anye, ok_ & ~anye):
                    e_ = XE[f][sel]
                    row += [float(np.mean(np.abs(e_))) if len(e_) else None, float(np.mean(e_)) if len(e_) else None]
            T["dedge"].append(row)
            fd["edge"][setname] = row
        # (g) ranges of e_max per season (every cycle; day 1 only exists, so also per cycle hour), curve and raw
        vseason = np.array([SEASONS.index(SEASON_OF[d.month]) for d in V["date"]])
        fd["dfan"] = {}
        for f in ("curve", "raw_gfs"):
            for si, sn in enumerate(["all"] + SEASONS):
                ms = vok & ((vseason == si - 1) if si else True)
                for k in (1, 2):
                    T["drng"].append([ic, GROUP[ic], f, sn, str(k), "all", *pct_row(VE[f][ms & (V["day_no"] == k)])])
                for ch in s97.CYCLE_HOURS:
                    m = ms & (V["ch"] == ch)
                    T["drng"].append([ic, GROUP[ic], f, sn, "1", str(ch), *pct_row(VE[f][m])])
                    if f == "curve" and sn != "all" and m.any():
                        fd["dfan"][(sn, ch)] = np.percentile(VE[f][m], PCTS)
        # shape (D106.8): diurnal range and run-to-run change of the maximum
        fd["shape"] = {}
        for f in ("raw_gfs", "baseline", "curve"):
            m = common & np.isfinite(D[f + "_rng"]) & np.isfinite(D["obs_rng"])
            fr, orng = D[f + "_rng"][m], D["obs_rng"][m]
            T["shape"].append([ic, GROUP[ic], f, int(m.sum()), float(fr.mean()), float(orng.mean()),
                               float((orng - fr).mean()), float(np.mean(np.abs(orng - fr))),
                               float(np.corrcoef(fr, orng)[0, 1])])
            fd["shape"][f] = (float(fr.mean()), float(orng.mean()))
        vkey = {(d.toordinal(), h_of(c)): j for j, (d, c) in enumerate(zip(V["date"], V["cycle"]))}
        for f in ("raw_gfs", "curve"):
            for ch in s97.CYCLE_HOURS:
                diffs = []
                for (dd_, c_), j in vkey.items():
                    if c_ % 24 != ch:
                        continue
                    j0 = vkey.get((dd_, c_ - 6))
                    if j0 is not None and np.isfinite(V[f][j]) and np.isfinite(V[f][j0]):
                        diffs.append(abs(V[f][j] - V[f][j0]))
                T["dr2r"].append([ic, GROUP[ic], f, ch, len(diffs), float(np.mean(diffs)) if diffs else None])
        print(f"  {ic}: {int(S.sum()):,} scored rows, {nD} days; {len(sdays)} scored days ({int(common.sum())} common); "
              f"{len(edays):,} every-cycle days ({time.time() - t:.0f} s)", flush=True)
        del A, B, obs, E, db
    # ---------------- Benjamini-Hochberg per family (D106.12)
    for fam in (1, 2, 3, 4):
        rows = [r for r in T["dm"] if r[0] == fam]
        rej = benjamini_hochberg([r[12] for r in rows])
        for r, x in zip(rows, rej):
            r.append(bool(x))
    T["dm"].sort(key=lambda r: (r[0], AIRPORTS.index(r[1])))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tables, figs = [], []
    H = ["icao", "group", "period", "forecast", "n", "mae", "mae_lo", "mae_hi", "mean_error", "me_lo", "me_hi",
         "rmse", "median_abs", "p90_abs", "p95_abs", "share_abs_le1", "share_abs_le2"]
    write_table("hourly_headline.csv", H + ["skill_vs_raw", "skill_vs_raw_lo", "skill_vs_raw_hi",
                                             "scored_rows_without_value"], T["head"], tables)
    write_table("hourly_curve_skill.csv", ["icao", "group", "period", "reference", "n_paired", "skill", "lo", "hi"],
                T["skill"], tables)
    write_table("hourly_breakdowns.csv", ["icao", "group", "condition", "kind", "bin", "forecast", "n", "mae", "mae_lo",
                                          "mae_hi", "mean_error", "me_lo", "me_hi", "mae_period_min",
                                          "mae_period_max", "mae_by_period"], T["brk"], tables)
    write_table("hourly_conditional_bias.csv", ["icao", "group", "forecast", "decile", "n", "mean_forecast",
                                                "mean_observed", "mean_error", "slope_obs_on_forecast"],
                T["cbias"], tables)
    write_table("hourly_ranges.csv", ["icao", "group", "forecast", "lead", "season", "n"] + [f"p{p}" for p in PCTS],
                T["hrng"], tables)
    write_table("b_summary.csv", ["icao", "group", "period", "n", "mean_b", "mean_abs_b", "p95_abs_b"], T["bsum"],
                tables)
    write_table("smoothness.csv", ["icao", "group", "n_triples", "raw_gfs", "curve", "observed"], T["smooth"], tables)
    write_table("run_to_run_hourly.csv", ["icao", "group", "forecast", "lead", "n", "mean_abs_change_from_6h_earlier"],
                T["r2r"], tables)
    write_table("limits.csv", ["icao", "group", "sea_in_grid_box", "scored_rows", "share_whole_degree_obs",
                               "rounding_floor_c", "curve_mae", "raw_gfs_mae"], T["limits"], tables)
    write_table("dailymax_headline.csv", H + ["common_days_without_value"], T["dhead"], tables)
    write_table("dailymax_curve_skill.csv", ["icao", "group", "period", "reference", "n_paired", "skill", "lo", "hi"],
                T["dskill"], tables)
    write_table("dailymax_every_cycle.csv", ["icao", "group", "cycle_hour", "day", "forecast", "n", "mae", "mae_lo",
                                             "mae_hi", "mean_error", "me_lo", "me_hi"], T["devery"], tables)
    write_table("dailymax_extremes.csv", ["icao", "group", "selected_by", "tail", "threshold", "forecast", "n", "mae",
                                          "mae_lo", "mae_hi", "mean_error", "me_lo", "me_hi"], T["dext"], tables)
    write_table("dailymax_decomposition.csv", ["icao", "group", "forecast", "days", "mean_e_max", "mean_peak_level",
                                               "mean_timing", "share_timing_above_0", "max_abs_sum_check"],
                T["ddec"], tables)
    write_table("dailymax_peak_hour.csv", ["icao", "group", "forecast", "days", "mean_forecast_minus_observed_h",
                                           "mean_abs_h", "share_0h", "share_le1h", "share_le2h", "share_le3h"],
                T["dpeak"], tables)
    write_table("dailymax_peak_hour_hist.csv", ["icao", "group", "forecast", "forecast_minus_observed_h", "days"],
                T["dpeakhist"], tables)
    write_table("dailymax_edge.csv", ["icao", "group", "day_set", "days", "obs_edge", "curve_edge", "raw_edge",
                                      "any_edge", "curve_edge_obs_edge", "curve_edge_obs_not", "curve_not_obs_edge",
                                      "curve_not_obs_not", "raw_edge_obs_edge", "raw_edge_obs_not",
                                      "raw_not_obs_edge", "raw_not_obs_not", "curve_mae_edge_days",
                                      "curve_me_edge_days", "curve_mae_other_days", "curve_me_other_days",
                                      "raw_mae_edge_days", "raw_me_edge_days", "raw_mae_other_days",
                                      "raw_me_other_days"], T["dedge"], tables)
    write_table("dailymax_ranges.csv", ["icao", "group", "forecast", "season", "day", "cycle_hour", "n"]
                + [f"p{p}" for p in PCTS], T["drng"], tables)
    write_table("dailymax_whole_day_leads.csv", ["icao", "group", "cycle_hour", "whole_days", "with_obs_raw_curve",
                                                 "first_lead_min", "first_lead_max"], T["dlead"], tables)
    write_table("shape_diurnal_range.csv", ["icao", "group", "forecast", "days", "mean_forecast_range",
                                            "mean_observed_range", "mean_obs_minus_forecast", "mae_range",
                                            "correlation"], T["shape"], tables)
    write_table("run_to_run_dailymax.csv", ["icao", "group", "forecast", "later_cycle_hour", "pairs",
                                            "mean_abs_change_from_6h_earlier"], T["dr2r"], tables)
    write_table("dm_tests.csv", ["family", "icao", "group", "a", "b", "output", "days", "rows", "mean_daily_diff",
                                 "lo", "hi", "dm_stat", "p_value", "bh_reject_q005"], T["dm"], tables)
    make_figures(plt, F, T, figs)
    lines = [f"run {now_utc()}; run time {time.time() - t_start:.0f} s; {versions()}; seed {SEED}",
             f"script SHA-256 {sha256_file(Path(__file__))}"] + checks
    lines += [f"table {n}: rows {r:,}, SHA-256 {h}" for n, r, h in tables]
    lines += [f"figure {n}: bytes {b:,}, SHA-256 {h}" for n, b, h in figs]
    write_once_text(OUT_DIR / "analyse_meta.txt", "\n".join(lines) + "\n")
    for c in checks:
        print("  " + c)
    print(f"wrote {len(tables)} tables and {len(figs)} figures; run time {time.time() - t_start:.0f} s")
    return 0


def make_figures(plt, F, T, figs):
    def lead_lines(metric, name, title, ylab):
        fig, ax = grid12(plt, title, sharey=False)
        for ic in AIRPORTS:
            for f in MAIN4:
                y = [F[ic]["brk"][("lead", n, f)][metric] for n in LEADS]
                ax[ic].plot(LEADS, y, color=COLOR[f], label=LABEL[f])
            if metric == 1:
                ax[ic].axhline(0, color=INK2, lw=0.8)
            ax[ic].set_xticks([3, 12, 24, 36, 48])
        for ic in AIRPORTS[-3:]:
            ax[ic].set_xlabel("lead (hours)")
        for ic in AIRPORTS[::3]:
            ax[ic].set_ylabel(ylab)
        legend_below(fig, ax)
        save_fig(fig, name, figs)

    def cond_lines(cond, xs, xl, metric, name, title, ylab):
        fig, ax = grid12(plt, title)
        for ic in AIRPORTS:
            for f in MAIN4:
                y = [F[ic]["brk"].get((cond, x, f), (np.nan,) * 4)[metric] for x in xs]
                ax[ic].plot(range(len(xs)), y, color=COLOR[f], label=LABEL[f], marker="o", ms=2.5)
            if metric == 1:
                ax[ic].axhline(0, color=INK2, lw=0.8)
            ax[ic].set_xticks(range(len(xs))[::max(1, len(xs) // 6)])
            ax[ic].set_xticklabels(xl[::max(1, len(xs) // 6)])
        for ic in AIRPORTS[::3]:
            ax[ic].set_ylabel(ylab)
        legend_below(fig, ax)
        save_fig(fig, name, figs)

    # Step 5
    fig, ax = grid12(plt, "Hourly errors (observed minus forecast, degrees C), scored rows, leads 3 to 48. "
                          "Box 25th to 75th percentile, whiskers 5th to 95th.", sharex=False)
    for ic in AIRPORTS:
        for j, f in enumerate(FORECASTS):
            p5, p25, p50, p75, p95 = F[ic]["box"][f]
            ax[ic].add_patch(plt.Rectangle((j - 0.3, p25), 0.6, p75 - p25, color=COLOR[f], alpha=0.85, lw=0))
            ax[ic].plot([j, j], [p5, p25], color=COLOR[f], lw=1)
            ax[ic].plot([j, j], [p75, p95], color=COLOR[f], lw=1)
            ax[ic].plot([j - 0.3, j + 0.3], [p50, p50], color=INK, lw=1)
        ax[ic].axhline(0, color=INK2, lw=0.8)
        ax[ic].set_xticks(range(len(FORECASTS)))
        ax[ic].set_xticklabels([LABEL[f] for f in FORECASTS], rotation=60, ha="right")
        ax[ic].set_xlim(-0.6, len(FORECASTS) - 0.4)
    save_fig(fig, "hourly_error_box.svg", figs)
    fig, ax = grid12(plt, "Hourly |error| ECDF (share of rows with |error| at most x), scored rows.")
    for ic in AIRPORTS:
        for f in MAIN4:
            ax[ic].plot(F[ic]["ecdf"][f], np.linspace(0, 1, 201), color=COLOR[f], label=LABEL[f])
        ax[ic].set_xlim(0, 5)
        ax[ic].axvline(0.25, color=INK2, lw=0.6, ls=":")
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("|error| (degrees C); dotted line: rounding floor 0.25")
    legend_below(fig, ax)
    save_fig(fig, "hourly_abs_error_ecdf.svg", figs)
    lead_lines(0, "hourly_mae_by_lead.svg", "Hourly MAE by lead (degrees C), pooled over test years and cycle hours.",
               "MAE")
    lead_lines(1, "hourly_me_by_lead.svg", "Hourly mean error by lead (observed minus forecast, degrees C).",
               "mean error")
    cond_lines("local_hour", list(range(24)), [str(h) for h in range(24)], 0, "hourly_mae_by_local_hour.svg",
               "Hourly MAE by local hour of the valid time (degrees C).", "MAE")
    cond_lines("local_hour", list(range(24)), [str(h) for h in range(24)], 1, "hourly_me_by_local_hour.svg",
               "Hourly mean error by local hour of the valid time (degrees C).", "mean error")
    cond_lines("month", list(range(1, 13)), [str(m) for m in range(1, 13)], 0, "hourly_mae_by_month.svg",
               "Hourly MAE by local month of the valid time (degrees C).", "MAE")
    cond_lines("month", list(range(1, 13)), [str(m) for m in range(1, 13)], 1, "hourly_me_by_month.svg",
               "Hourly mean error by local month of the valid time (degrees C).", "mean error")
    fig, ax = grid12(plt, "Conditional bias: mean error per decile of the forecast value (decile edges from training "
                          "rows' raw GFS).", sharex=False)
    for ic in AIRPORTS:
        for f in ("raw_gfs", "linear_mos", "curve"):
            xy = F[ic]["cb"][f]
            ax[ic].plot([a for a, _ in xy], [b for _, b in xy], color=COLOR[f], label=LABEL[f], marker="o", ms=2.5)
        ax[ic].axhline(0, color=INK2, lw=0.8)
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("mean forecast in the decile (degrees C)")
    legend_below(fig, ax, 3)
    save_fig(fig, "hourly_conditional_bias.svg", figs)
    conds = ["cloud_cover", "wind_speed_10m", "raw_range", "raw_change24", "abs_b", "curve_minus_raw", "obs_range",
             "obs_change24"]
    fig, axes = plt.subplots(4, 2, figsize=(10, 11), constrained_layout=True)
    for axx, c in zip(axes.flat, conds):
        for k, ic in enumerate(AIRPORTS):
            for b in range(3):
                for f, off in (("raw_gfs", -0.12), ("curve", 0.12)):
                    v = F[ic]["brk"].get((c, b, f))
                    if v is None:
                        continue
                    x = k * 4 + b + off
                    axx.plot([x, x], [v[2], v[3]], color=COLOR[f], lw=1)
                    axx.plot([x], [v[0]], "o", color=COLOR[f], ms=2.5, label=LABEL[f] if (k, b) == (0, 0) else None)
        axx.set_xticks([k * 4 + 1 for k in range(len(AIRPORTS))])
        axx.set_xticklabels(AIRPORTS, rotation=60, ha="right")
        axx.set_title(f"{c} ({'secondary, known afterwards' if c in SECONDARY else 'primary'}): low, mid, high tercile",
                      loc="left")
        axx.set_ylabel("MAE")
        axx.axvline(23.5, color=INK2, lw=0.6, ls=":")
    axes.flat[0].legend(loc="upper right")
    fig.suptitle("Hourly MAE by regime tercile (edges per airport from training rows; abs_b and curve_minus_raw from "
                 "the test forecasts), with 95 % intervals.\nLeft of the dotted line: claim airports; right: "
                 "development airports (" + DEV_FLAG + ").", fontsize=8.5, x=0.01, ha="left")
    save_fig(fig, "hourly_regimes.svg", figs)
    fig, ax = grid12(plt, "Drift: hourly MAE of the curve and the baseline by days since the tracker started, "
                          "with 95 % intervals.")
    for ic in AIRPORTS:
        for f, off in (("baseline", -0.1), ("curve", 0.1)):
            xs, ys, lo, hi = [], [], [], []
            for b in range(5):
                v = F[ic]["brk"].get(("days_since_start", b, f))
                if v:
                    xs.append(b + off)
                    ys.append(v[0])
                    lo.append(v[2])
                    hi.append(v[3])
            ax[ic].errorbar(xs, ys, yerr=[np.subtract(ys, lo), np.subtract(hi, ys)], fmt="o-", ms=3, color=COLOR[f],
                            label=LABEL[f], lw=1)
        ax[ic].set_xticks(range(5))
        ax[ic].set_xticklabels(DSS_NAMES, rotation=30)
    legend_below(fig, ax, 2)
    save_fig(fig, "drift_by_days_since_start.svg", figs)
    fig, ax = grid12(plt, "b over time: the daily mean of b (degrees C) over all scored rows of each cycle date.",
                     sharex=False)
    for ic in AIRPORTS:
        u, bb = F[ic]["b_time"]
        x = (u * 24 * 3600).astype("datetime64[s]")
        ax[ic].plot(x, bb, color=COLOR["curve"], lw=0.7)
        ax[ic].axhline(0, color=INK2, lw=0.8)
        ax[ic].tick_params(axis="x", labelrotation=30)
    save_fig(fig, "b_over_time.svg", figs)
    # Step 6
    fig, ax = grid12(plt, "Daily maximum errors (observed minus forecast maximum, degrees C), scored days. "
                          "Box 25th to 75th percentile, whiskers 5th to 95th.", sharex=False)
    for ic in AIRPORTS:
        for j, f in enumerate(FORECASTS):
            p5, p25, p50, p75, p95 = np.percentile(F[ic]["dbox"][f], [5, 25, 50, 75, 95])
            ax[ic].add_patch(plt.Rectangle((j - 0.3, p25), 0.6, p75 - p25, color=COLOR[f], alpha=0.85, lw=0))
            ax[ic].plot([j, j], [p5, p25], color=COLOR[f], lw=1)
            ax[ic].plot([j, j], [p75, p95], color=COLOR[f], lw=1)
            ax[ic].plot([j - 0.3, j + 0.3], [p50, p50], color=INK, lw=1)
        ax[ic].axhline(0, color=INK2, lw=0.8)
        ax[ic].set_xticks(range(len(FORECASTS)))
        ax[ic].set_xticklabels([LABEL[f] for f in FORECASTS], rotation=60, ha="right")
        ax[ic].set_xlim(-0.6, len(FORECASTS) - 0.4)
    save_fig(fig, "dailymax_error_box.svg", figs)
    fig, ax = grid12(plt, "Daily maximum error histograms (0.5 degree C bins), scored days: raw GFS and the curve.")
    bins = np.arange(-8, 8.01, 0.5)
    for ic in AIRPORTS:
        for f in ("raw_gfs", "curve"):
            ax[ic].hist(F[ic]["dbox"][f], bins=bins, histtype="step", color=COLOR[f], label=LABEL[f], lw=1.2)
        ax[ic].axvline(0, color=INK2, lw=0.8)
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("observed minus forecast maximum (degrees C)")
    legend_below(fig, ax, 2)
    save_fig(fig, "dailymax_error_hist.svg", figs)
    fig, ax = grid12(plt, "Daily maximum MAE from every cycle, by cycle hour (UTC), with 95 % intervals. Each "
                          "run holds one whole local day (day 1); no day 2 exists.", sharex=False)
    for ic in AIRPORTS:
        for f, off in (("raw_gfs", -0.12), ("curve", 0.12)):
            for k, mk in ((1, "o"),):
                xs, ys, lo, hi = [], [], [], []
                for j, ch in enumerate(s97.CYCLE_HOURS):
                    v = F[ic]["every"].get((ch, k, f))
                    if v:
                        xs.append(j + off)
                        ys.append(v[0])
                        lo.append(v[1])
                        hi.append(v[2])
                ax[ic].errorbar(xs, ys, yerr=[np.subtract(ys, lo), np.subtract(hi, ys)], fmt=mk, ms=3,
                                color=COLOR[f], lw=1, label=LABEL[f])
        ax[ic].set_xticks(range(4))
        ax[ic].set_xticklabels([f"{h:02d}z" for h in s97.CYCLE_HOURS])
    legend_below(fig, ax, 2)
    save_fig(fig, "dailymax_by_cycle_hour.svg", figs)
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for axx, (by, tail) in zip(axes.flat, [(b, t) for b in ("forecast maximum (curve)", "observed maximum")
                                           for t in ("hottest 10 %", "coldest 10 %")]):
        for k, ic in enumerate(AIRPORTS):
            for f, off in (("raw_gfs", -0.15), ("linear_mos", 0.0), ("curve", 0.15)):
                v = F[ic]["ext"][(by, tail, f)]
                axx.plot([k + off] * 2, [v[1], v[2]], color=COLOR[f], lw=1)
                axx.plot([k + off], [v[0]], "o", color=COLOR[f], ms=3, label=LABEL[f] if k == 0 else None)
        axx.axhline(0, color=INK2, lw=0.8)
        axx.axvline(5.5, color=INK2, lw=0.6, ls=":")
        axx.set_xticks(range(len(AIRPORTS)))
        axx.set_xticklabels(AIRPORTS, rotation=60, ha="right")
        axx.set_title(f"{tail} of days by {by}: mean error with 95 % interval", loc="left")
        axx.set_ylabel("mean error (degrees C)")
    axes.flat[0].legend()
    fig.suptitle("Daily maximum on extreme days (scored days). Left of the dotted line: claim airports.",
                 fontsize=8.5, x=0.01, ha="left")
    save_fig(fig, "dailymax_extremes.svg", figs)
    fig, axx = plt.subplots(figsize=(10, 4.2), constrained_layout=True)
    for k, ic in enumerate(AIRPORTS):
        for f, off in (("raw_gfs", -0.2), ("curve", 0.2)):
            em, lv, tm = F[ic]["dec"][f]
            axx.bar(k + off - 0.09, lv, width=0.17, color=COLOR[f], label=f"{LABEL[f]}: peak level" if k == 0 else None)
            axx.bar(k + off + 0.09, -tm, width=0.17, color=COLOR[f], alpha=0.45,
                    label=f"{LABEL[f]}: minus timing" if k == 0 else None)
            axx.plot([k + off], [em], "D", color=INK, ms=3, label="e_max (sum)" if (k, f) == (0, "curve") else None)
    axx.axhline(0, color=INK2, lw=0.8)
    axx.axvline(5.5, color=INK2, lw=0.6, ls=":")
    axx.set_xticks(range(len(AIRPORTS)))
    axx.set_xticklabels(AIRPORTS)
    axx.set_ylabel("degrees C")
    axx.legend(ncol=5, loc="upper left", fontsize=7)
    axx.set_title("Why the maximum reads low (D106.7(d)), scored days: mean e_max = mean peak level term "
                  "[observed max - forecast at the observed peak hour]\nminus mean timing term [forecast max - "
                  "forecast at the observed peak hour]. Left of the dotted line: claim airports.", loc="left",
                  fontsize=8)
    save_fig(fig, "dailymax_decomposition.svg", figs)
    fig, ax = grid12(plt, "Peak hour error (forecast peak hour minus observed peak hour, hours), scored days.")
    for ic in AIRPORTS:
        for f in ("raw_gfs", "curve"):
            ax[ic].hist(F[ic]["peak"][f], bins=np.arange(-12.5, 12.6, 1), histtype="step", color=COLOR[f],
                        label=LABEL[f], lw=1.2)
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("hours")
    legend_below(fig, ax, 2)
    save_fig(fig, "dailymax_peak_hour.svg", figs)
    edge_figure(plt, F, AIRPORTS, "dailymax_edge_of_day.svg", figs)
    fig, ax = grid12(plt, "Ranges of the curve's daily maximum error (observed minus forecast, degrees C), every "
                          "cycle, by season and cycle hour (day 1 only exists). Bands: 5 to 95, 10 to 90, 25 "
                          "to 75; line: median.",
                     sharex=False)
    for ic in AIRPORTS:
        xs = [(sn, ch) for sn in SEASONS for ch in s97.CYCLE_HOURS]
        P = np.array([F[ic]["dfan"].get(x, np.full(len(PCTS), np.nan)) for x in xs])   # no whole day: a gap
        for lo_i, hi_i, al in ((0, 6, 0.18), (1, 5, 0.3), (2, 4, 0.5)):
            ax[ic].fill_between(range(len(xs)), P[:, lo_i], P[:, hi_i], color=COLOR["curve"], alpha=al, lw=0,
                                step="mid")
        ax[ic].plot(range(len(xs)), P[:, 3], color=INK, lw=1, drawstyle="steps-mid")
        ax[ic].axhline(0, color=INK2, lw=0.8)
        ax[ic].set_xticks(range(len(xs)))
        ax[ic].set_xticklabels([f"{sn[:3]} {ch:02d}z" for sn, ch in xs], rotation=90, fontsize=6)
    save_fig(fig, "dailymax_ranges_fan.svg", figs)
    fig, ax = grid12(plt, "Ranges of the curve's hourly error by single lead (observed minus forecast, degrees C), "
                          "all seasons. Bands: 5 to 95, 10 to 90, 25 to 75; line: median.")
    for ic in AIRPORTS:
        P = F[ic]["hfan"]
        for lo_i, hi_i, al in ((0, 6, 0.18), (1, 5, 0.3), (2, 4, 0.5)):
            ax[ic].fill_between(LEADS, P[:, lo_i], P[:, hi_i], color=COLOR["curve"], alpha=al, lw=0)
        ax[ic].plot(LEADS, P[:, 3], color=INK, lw=1)
        ax[ic].axhline(0, color=INK2, lw=0.8)
        ax[ic].set_xticks([3, 12, 24, 36, 48])
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("lead (hours)")
    save_fig(fig, "hourly_ranges_fan.svg", figs)
    # Step 7
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    for k, ic in enumerate(AIRPORTS):
        o = F[ic]["shape"]["curve"][1]
        axes[0].plot([k], [o], "s", color=INK, ms=4, label="observed" if k == 0 else None)
        for f, off in (("raw_gfs", -0.15), ("curve", 0.15)):
            axes[0].plot([k + off], [F[ic]["shape"][f][0]], "o", color=COLOR[f], ms=4,
                         label=LABEL[f] if k == 0 else None)
        for f, off in (("raw_gfs", -0.2), ("curve", 0.0), ("obs", 0.2)):
            axes[1].bar(k + off, F[ic]["smooth"][f], width=0.2, color=COLOR.get(f, INK2),
                        label=(LABEL.get(f, "observed")) if k == 0 else None)
    for axx, tl in zip(axes, ("Mean diurnal range on scored days (degrees C)",
                              "Smoothness: mean |second difference| over consecutive leads (degrees C)")):
        axx.set_xticks(range(len(AIRPORTS)))
        axx.set_xticklabels(AIRPORTS, rotation=60, ha="right")
        axx.axvline(5.5, color=INK2, lw=0.6, ls=":")
        axx.set_title(tl, loc="left")
        axx.legend(fontsize=7)
    save_fig(fig, "shape_range_smoothness.svg", figs)
    fig, ax = grid12(plt, "Run-to-run change: mean |forecast for a valid time from cycle c minus that from cycle "
                          "c - 6 h| by lead from c (degrees C).")
    for ic in AIRPORTS:
        for f in ("raw_gfs", "curve"):
            ax[ic].plot(range(3, 43), F[ic]["r2r"][f], color=COLOR[f], label=LABEL[f])
    for ic in AIRPORTS[-3:]:
        ax[ic].set_xlabel("lead (hours)")
    legend_below(fig, ax, 2)
    save_fig(fig, "run_to_run_hourly.svg", figs)
    # Step 8
    fig, axes = plt.subplots(2, 2, figsize=(10, 7), constrained_layout=True)
    for axx, fam in zip(axes.flat, (1, 2, 3, 4)):
        rows = [r for r in T["dm"] if r[0] == fam]
        for k, r in enumerate(rows):
            col = COLOR["curve"] if r[13] else INK2
            axx.plot([k, k], [r[9], r[10]], color=col, lw=1.2)
            axx.plot([k], [r[8]], "o", color=col, ms=4)
        axx.axhline(0, color=INK2, lw=0.8)
        axx.axvline(5.5, color=INK2, lw=0.6, ls=":")
        axx.set_xticks(range(len(rows)))
        axx.set_xticklabels([r[1] for r in rows], rotation=60, ha="right")
        axx.set_title(f"family {fam}: {rows[0][3]} against {rows[0][4]}, {rows[0][5]}", loc="left")
        axx.set_ylabel("mean daily |e_a| - |e_b| (degrees C)")
    fig.suptitle("Diebold-Mariano: mean daily difference in |error| with 95 % intervals. Blue: rejected by "
                 "Benjamini-Hochberg at 0.05 within the family; grey: not. Below 0: the curve has the smaller "
                 "error.", fontsize=8.5, x=0.01, ha="left")
    save_fig(fig, "dm_tests.svg", figs)


def edge_figure(plt, F, airports, name, figs):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
    for k, ic in enumerate(airports):
        r = F[ic]["edge"]["scored days"]
        n = r[3]
        for j, (lab, v) in enumerate((("observed", r[4]), ("curve", r[5]), ("raw GFS", r[6]))):
            axes[0].bar(k + (j - 1) * 0.25, 100 * v / n, width=0.24, color=(INK2, COLOR["curve"], COLOR["raw_gfs"])[j],
                        label=lab if k == 0 else None)
        for j, (lab, v) in enumerate((("curve, edge days", r[16]), ("curve, other days", r[18]),
                                      ("raw GFS, edge days", r[20]), ("raw GFS, other days", r[22]))):
            col = COLOR["curve"] if j < 2 else COLOR["raw_gfs"]
            axes[1].bar(k + (j - 1.5) * 0.2, v if v is not None else 0, width=0.19, color=col,
                        alpha=1.0 if j % 2 == 0 else 0.45, label=lab if k == 0 else None)
    for axx, tl in zip(axes, ("Share of scored days (%) whose maximum is in the first or last local hour",
                              "Daily maximum MAE on days with any edge maximum against other days (degrees C)")):
        axx.set_xticks(range(len(airports)))
        axx.set_xticklabels(airports, rotation=60, ha="right")
        if len(airports) == 12:
            axx.axvline(5.5, color=INK2, lw=0.6, ls=":")
        axx.set_title(tl, loc="left", fontsize=7.5)
        axx.legend(fontsize=6.5)
    save_fig(fig, name, figs)


# ------------------------------------------------------------------ Step 7: --contrib (D106.10)

def fit_model(train):
    """Session 97's fit_predict, returning the fitted model (fit_predict returns only the forecasts):
    G15 columns as float64, target obs minus temp, rows in ascending cycle time, the record's settings."""
    x = np.array([r[0] for r in train], dtype=float)
    y = np.array([r[2] - r[1] for r in train], dtype=float)
    m = lgb.LGBMRegressor(**s97.LGB_PARAMS)
    m.fit(x, y)
    return m


def run_contrib(args):
    t_start = time.time()
    plt = plt_setup()
    print(f"SESSION 112 --contrib (offline), start {now_utc()}; {versions()}")
    out_t, out_m = OUT_DIR / "contrib_shares.csv", OUT_DIR / "contrib_meta.txt"
    for p in (out_t, out_m):
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists")
    rows_out, figs, tables, scat = [], [], [], {}
    fits = mism = 0
    worst_sum = 0.0
    for ic in AIRPORTS:
        t = time.time()
        rows = table_rows(ic)
        pred = load_pred_rows(ic)
        ix = {c: i for i, c in enumerate(PRED_COLUMNS)}
        stored = {(r[ix["cycle_utc"]], int(r[ix["lead"]])): float(r[ix["baseline"]])
                  for r in pred if r[ix["status"]] == "scored" and int(r[ix["lead"]]) in CONTRIB_LEADS}
        sets = [(t0, t1) for _, t0, _, t1 in DEV_PERIODS] if GROUP[ic] == "dev" else [(s106.T_TRAIN, s106.T_END)]
        acc = {n: [] for n in CONTRIB_LEADS}
        sc = {"temp": [], "c_temp": [], "cloud": [], "c_cloud": []}
        for t0, t1 in sets:
            for n in CONTRIB_LEADS:
                leads = s104.LEADS_A if n <= 24 else s104.LEADS_B
                sub = [r for r in rows if r[3] in set(leads) and r[3] == n]
                train, test = s104.split_rows_leads(sub, t0, t1, leads)
                for h in s97.CYCLE_HOURS:
                    tr, te = train[(h, n)], test[(h, n)]
                    m = fit_model([(r[1], r[2], r[3]) for r in tr])
                    fits += 1
                    xt = np.array([r[1] for r in te], dtype=float)
                    fc = [r[2] + float(v) for r, v in zip(te, m.predict(xt))]
                    want = [stored[(tstr(r[0]), n)] for r in te]
                    mism += sum(a != b for a, b in zip(fc, want))
                    cb = m.predict(xt, pred_contrib=True)
                    worst_sum = max(worst_sum, float(np.max(np.abs(cb.sum(axis=1) - m.predict(xt)))))
                    acc[n].append(np.abs(cb[:, :9]))
                    if n == 24:
                        sc["temp"] += list(xt[:, G15.index("temp")])
                        sc["c_temp"] += list(cb[:, G15.index("temp")])
                        sc["cloud"] += list(xt[:, G15.index("cloud_cover")])
                        sc["c_cloud"] += list(cb[:, G15.index("cloud_cover")])
        shares = {}
        for n in CONTRIB_LEADS:
            a = np.vstack(acc[n])
            mabs = a.mean(axis=0)
            shares[n] = mabs / mabs.sum()
            rows_out.append([ic, GROUP[ic], n, len(a)] + [float(v) for v in shares[n]] + [float(v) for v in mabs])
        scat[ic] = (shares, {k: np.array(v) for k, v in sc.items()})
        print(f"  {ic}: {len(sets) * 24} refits; refit forecasts not equal to the stored baseline so far {mism} "
              f"({time.time() - t:.0f} s)", flush=True)
    if mism:
        raise SystemExit(f"STOP: {mism} refit forecasts differ from the stored baseline")
    write_table("contrib_shares.csv", ["icao", "group", "lead", "rows"] + [f"share_{f}" for f in G15]
                + [f"mean_abs_{f}" for f in G15], rows_out, tables)
    fig, ax = grid12(plt, "Model internals (D106.10): share of mean |LightGBM contribution| per feature, by lead "
                          "(all cycle hours and test years). Darker = larger share.", sharex=False, h=12)
    for ic in AIRPORTS:
        M = np.array([scat[ic][0][n] for n in CONTRIB_LEADS]).T
        ax[ic].imshow(M, cmap="Blues", vmin=0, vmax=0.6, aspect="auto")
        for i in range(M.shape[0]):
            for j in range(M.shape[1]):
                ax[ic].text(j, i, f"{100 * M[i, j]:.0f}", ha="center", va="center", fontsize=6,
                            color="white" if M[i, j] > 0.35 else INK)
        ax[ic].set_xticks(range(len(CONTRIB_LEADS)))
        ax[ic].set_xticklabels(CONTRIB_LEADS)
        ax[ic].set_yticks(range(9))
        ax[ic].set_yticklabels([g.replace("dewpoint_depression_t2m_floored", "dewpoint depr.")
                                .replace("pressure_tendency_3h_hpa", "pressure tend.")
                                .replace("lapse_rate_t2_t850", "lapse rate").replace("dswrf_2h_wm2", "radiation")
                                for g in G15])
        ax[ic].grid(False)
    save_fig(fig, "contrib_shares.svg", figs)
    for key, xl, name in (("temp", "raw GFS temperature (degrees C)", "contrib_vs_temperature.svg"),
                          ("cloud", "forecast cloud cover (%)", "contrib_vs_cloud.svg")):
        fig, ax = grid12(plt, f"Model internals: the {key if key == 'cloud' else 'temperature'} feature's "
                              f"contribution to the correction (degrees C) against its value, lead 24, all cycle "
                              f"hours (every 5th row).", sharex=False)
        for ic in AIRPORTS:
            s = scat[ic][1]
            ax[ic].scatter(s[key][::5], s["c_" + key][::5], s=2, color=COLOR["curve"], alpha=0.25, lw=0,
                           rasterized=False)
            ax[ic].axhline(0, color=INK2, lw=0.8)
        for ic in AIRPORTS[-3:]:
            ax[ic].set_xlabel(xl)
        save_fig(fig, name, figs)
    lines = [f"run {now_utc()}; run time {time.time() - t_start:.0f} s; {versions()}",
             f"script SHA-256 {sha256_file(Path(__file__))}",
             f"refits {fits}; refit forecasts different from the stored baseline: {mism}; largest |sum of "
             f"contributions - prediction| {worst_sum:.2e}"]
    lines += [f"table {n}: rows {r:,}, SHA-256 {h}" for n, r, h in tables]
    lines += [f"figure {n}: bytes {b:,}, SHA-256 {h}" for n, b, h in figs]
    write_once_text(out_m, "\n".join(lines) + "\n")
    print("\n".join(lines[2:3]))
    print(f"wrote {len(tables)} table and {len(figs)} figures; run time {time.time() - t_start:.0f} s")
    return 0


# ------------------------------------------------------------------ Step 9: --zuck (D106.13)

ZUCK_URL = "https://raw.githubusercontent.com/zadams03/MLwx-live/main/log/2026/10/gfs_2026101306.csv"
ZUCK_COLS = ("airport", "cycle", "lead", "valid", "raw_gfs", "baseline", "b", "corrected")


def run_zuck(args):
    plt = plt_setup()
    print(f"SESSION 112 --zuck (offline; the file was downloaded beforehand), start {now_utc()}")
    if not args.zuck_file:
        raise SystemExit("STOP: give --zuck-file")
    path = Path(args.zuck_file)
    data = path.read_bytes()
    print(f"file {path.name}: bytes {len(data):,}, SHA-256 {hashlib.sha256(data).hexdigest()}")
    rd = csv.DictReader(io.StringIO(data.decode()))
    head = rd.fieldnames
    col = {}
    for want in ZUCK_COLS:
        hits = [h for h in head if h == want or h.startswith(want + "_")]
        if len(hits) != 1:
            raise SystemExit(f"STOP: column {want} not found once in {head}")
        col[want] = hits[0]
    print(f"columns read: {[col[c] for c in ZUCK_COLS]} (of {len(head)})")
    rows = [{c: r[col[c]] for c in ZUCK_COLS} for r in rd if r[col["airport"]] == "ZUCK"]
    if not rows:
        raise SystemExit("STOP: no ZUCK rows")
    tz = ZoneInfo("Asia/Chongqing")
    vt = [dt.datetime.strptime(r["valid"][:16].replace("Z", ""), "%Y-%m-%dT%H:%M").replace(tzinfo=dt.timezone.utc)
          for r in rows]
    if max(vt).replace(tzinfo=None) < dt.datetime(2026, 8, 1):
        raise SystemExit("STOP: unexpected valid times")
    loc = [v.astimezone(tz).replace(tzinfo=None) for v in vt]
    raw = [float(r["raw_gfs"]) for r in rows]
    cor = [float(r["corrected"]) for r in rows]
    leads = [int(r["lead"]) for r in rows]
    cyc = dt.datetime.strptime(rows[0]["cycle"][:16].replace("Z", ""), "%Y-%m-%dT%H:%M")
    days = {}
    for i, t in enumerate(loc):
        days.setdefault(t.date(), []).append(i)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1.7, 1]}, constrained_layout=True)
    ax0 = axes[0]
    ax0.plot(loc, raw, color=COLOR["raw_gfs"], label="raw GFS")
    ax0.plot(loc, cor, color=COLOR["curve"], label="corrected (the curve)")
    summary = []
    for k, (d, ii) in enumerate(sorted(days.items())):
        whole = len(ii) == 24
        s = dt.datetime(d.year, d.month, d.day)
        ax0.axvspan(s, s + DAY, color=INK2, alpha=0.07 if k % 2 == 0 else 0.0, lw=0)
        if whole:
            for vals, f in ((raw, "raw_gfs"), (cor, "curve")):
                j = ii[peak_index([vals[i] for i in ii])]
                ax0.plot([loc[j]], [vals[j]], "o", color=COLOR[f], ms=6, mec=SURFACE, mew=1.5)
                ax0.annotate(f"{vals[j]:.1f} at {loc[j]:%H}:00", (loc[j], vals[j]), textcoords="offset points",
                             xytext=(4, 6), fontsize=7, color=INK)
                summary.append((d.isoformat(), f, vals[j], loc[j].hour, is_edge(ii.index(j), 24)))
    ax0.set_title(f"ZUCK, cycle {cyc:%Y-%m-%d %H}z (MLwx-live log, forecast columns only), leads {min(leads)} to "
                  f"{max(leads)}.\nLocal days (Asia/Chongqing) shaded alternately; dots: each whole day's maximum "
                  "and its hour.", loc="left", fontsize=8)
    ax0.set_ylabel("2 m temperature (degrees C)")
    ax0.legend(loc="lower left")
    ax0.tick_params(axis="x", labelrotation=30)
    # beside it: ZUCK's spent-data edge-of-day figures (Step 6)
    ed = {}
    with open(OUT_DIR / "dailymax_edge.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["icao"] == "ZUCK":
                ed[r["day_set"]] = r
    ax1 = axes[1]
    sets = ["scored days", "every cycle"]
    for j, (lab, key, c) in enumerate((("observed", "obs_edge", INK2), ("curve", "curve_edge", COLOR["curve"]),
                                       ("raw GFS", "raw_edge", COLOR["raw_gfs"]))):
        ax1.bar([k + (j - 1) * 0.26 for k in range(2)], [100 * int(ed[s][key]) / int(ed[s]["days"]) for s in sets],
                width=0.25, color=c, label=lab)
    ax1.set_xticks(range(2))
    ax1.set_xticklabels(sets)
    ax1.set_ylabel("% of days")
    ax1.set_title("ZUCK, spent data (2024-08 to 2026-07): share of days whose maximum is in\nthe first or last "
                  "local hour (dailymax_edge.csv; whole figure for all airports: dailymax_edge_of_day.svg)",
                  loc="left", fontsize=8)
    ax1.legend()
    figs = []
    save_fig(fig, "zuck_case_2026101306.svg", figs)
    print(f"ZUCK rows {len(rows)}; local days {len(days)}; whole days {sum(len(v) == 24 for v in days.values())}")
    for s in summary:
        print(f"  {s[0]} {s[1]}: maximum {s[2]:.3f} at local {s[3]:02d}:00, edge hour {s[4]}")
    print(f"figure {figs[0][0]}: bytes {figs[0][1]:,}, SHA-256 {figs[0][2]}")
    return 0


# ------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("regen", "refs", "check", "analyse", "contrib", "zuck"):
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--zuck-file", default=None)
    ap.add_argument("--trial-dir", default=None, help="--analyse only: a trial on ZUCK and EGLC, writing to this "
                                                       "folder instead of the repo")
    a = ap.parse_args()
    if a.trial_dir:
        global OUT_DIR, FIG_DIR, AIRPORTS
        OUT_DIR = FIG_DIR = Path(a.trial_dir)
        AIRPORTS = ["ZUCK", "EGLC"]
    fn = {"regen": run_regen}
    for k in ("refs", "check", "analyse", "contrib", "zuck"):
        if f"run_{k}" in globals():
            fn[k] = globals()[f"run_{k}"]
    try:
        return fn[next(k for k in fn if getattr(a, k))](a)
    except s97.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
