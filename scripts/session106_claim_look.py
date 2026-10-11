"""Session 106: stage C's claim look script (DECISIONS D100.3 to D100.9). Offline.

It implements D100's frozen method and pre-registered test. At each airport:
D88.4's baseline, one LightGBM model per cycle hour (00, 06, 12, 18 UTC) and
lead 3 to 48 (184 models), trained once on the complete-case rows valid
before 2024-08-01T00:00 in ascending cycle time and then frozen; plus D97's
correction (w = 0.02, one tracker per cycle hour and lead, b = 0 at
2024-08-01T00:00, running without a break through both looks, using only
errors valid before the forecast's cycle). Rows with complete features and no
observation are predicted and corrected, never scored (D98.7). The daily
maximum is read off the curve (D98.10(a) to (c)) in the airport's own time
zone. Two looks by cycle (D100.4): A, cycles 2024-08-01T00 to 2025-07-31T18;
B, cycles 2025-08-01T00 to 2026-07-31T18. The bar (D100.5): per airport,
look and output, the curve's MAE strictly lower than raw GFS on the common
set and than persistence on the subset where persistence has a value, at
full precision. Verdicts (D100.6): PASS if both looks pass, SPLIT if one,
FAIL if neither. Margins as D79.1; the smallest margin per output is named
first. D100.8's descriptive figures are printed.

Modes (one per run):
  --gate          D100.9(c), the six development airports only (F138's and
                  F147's tables): 1. the tracker's self-check (session 104's
                  gate 1); 2. look A reproduces session 104's fold 2024-25
                  exactly (every cell's n and MAE for raw GFS, the baseline
                  and the curve; every 2024-25 day's cycle, observed, raw GFS
                  and curve maxima); 3. look B and both looks' bar and
                  persistence figures, as a smoke test on spent years,
                  descriptive only. Refuses any claim airport. Writes nothing.
  --look --confirm-look 107
                  The six claim airports only. Refuses without the flag, any
                  development airport, and if any output file exists. Writes
                  data/processed/session107_claim_scores.csv,
                  data/processed/session107_claim_days.csv and
                  data/processed/session107_claim_verdicts.csv. NOT RUN IN
                  SESSION 106 (D100.9(d)).
  --guard-check   Shows --look refusing without the flag and with a
                  development airport, and --gate refusing a claim airport,
                  with no data read.
  --meta          Prints the gate's meta (no file is written).

Imported read only, after its SHA-256 check: scripts/session104_curve_cv.py
(F147), and through it sessions 97, 100 and 103 (each checked by it). Used
from session 104: correct (the tracker on one cell, with session 103's track
unchanged), split_rows_leads (session 100's split_rows at leads 3 to 24),
gate_check (gate 1), day_cycle, local_day, usable_day, TZ, LEADS_A, LEADS_B,
LEADS_ALL, W, DAY_LAST_VALID; from session 97 fit_predict, mae, mean_error,
fold_role, parse_time, check_valid, check_obs_time, fval, fmt, csv_text,
write_new, TABLES, STAGEC_DIR, TABLE_COLUMNS, G15, LGB_PARAMS, CYCLE_HOURS,
STATIONS. Written here: the table loader for any table file and SHA-256 (as
session 97's load_table and session 104's load_table25), the frozen fit over
both looks, persistence, the look assignment, the day list over both looks,
the bar, margins, verdicts and the gate's comparisons. lightgbm is imported
directly (D93.3); this script never imports or calls the session-48 guard.

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


S104_SCRIPT_SHA256 = "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb"   # F147
if sha256_file(HERE / "session104_curve_cv.py") != S104_SCRIPT_SHA256:
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

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
STAGEC = s97.STAGEC_DIR
SCRIPT = Path(__file__).resolve()

# Session 104's outputs, for the gate (F147.7).
S104_SCORES = PROCESSED / "session104_curve_cv_scores.csv"
S104_SCORES_SHA256 = "69ec86bf600fcb2c5b8ad0f8ec0cb8ed69adb314813e9ab1ee4b578f0fffa35e"   # F147.7
S104_DAYS = PROCESSED / "session104_dailymax_days.csv"
S104_DAYS_SHA256 = "65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3"     # F147.7
GATE_FOLD = "2024-25"

# The development airports' tables: hours 0 to 24 from session 97's TABLES (F138.4); hours 25 to 48 (F147.2,
# data/processed/session104_stagec_f025_048_table.meta.txt).
DEV = list(s97.STATIONS)
DEV_TABLE25 = {
    "EGLC": ("stagec_dev_f025_048_EGLC.csv.gz", "947bf2f0920e1a1f972ea9297fcc9bdc5c987562e13ee5daa7ae5ab866066ea9"),
    "LFPG": ("stagec_dev_f025_048_LFPG.csv.gz", "04dbd411dbd683dfe3a09597ea8407cc75c8afc86100b31a8396caca0ff52c35"),
    "DSM": ("stagec_dev_f025_048_KDSM.csv.gz", "bd2d80c01211a3c399d6904068bfb9377b0ad9091e13878621526835434ee2f3"),
    "YSDU": ("stagec_dev_f025_048_YSDU.csv.gz", "b801fcc2d9e2c9dd843ea920e8dd8ac88f33f5db7057bb4ae1ca46a2b16981ac"),
    "RNO": ("stagec_dev_f025_048_KRNO.csv.gz", "3ca1d4ff8933f14c6e898525ba445af080b92c0545989fe39b3d7bdbfdd6bd58"),
    "SFO": ("stagec_dev_f025_048_KSFO.csv.gz", "2e355c0146e1bc8923f632d208c084f646ec3ebcd9dfa2bb22e22c363e81b84b"),
}
DEV_ICAO = {"EGLC": "EGLC", "LFPG": "LFPG", "DSM": "KDSM", "YSDU": "YSDU", "RNO": "KRNO", "SFO": "KSFO"}

# The claim airports (D82.7): ICAO -> (station code = IEM id, time zone). Time zones from
# data/processed/session90_airports.csv (F132; D100.3(e)), checked against it at run time.
CLAIM = {
    "EDDM": ("EDDM", "Europe/Berlin"),
    "KORD": ("ORD", "America/Chicago"),
    "CYYZ": ("CYYZ", "America/Toronto"),
    "ZGSZ": ("ZGSZ", "Asia/Shanghai"),
    "ZUCK": ("ZUCK", "Asia/Chongqing"),
    "NZWN": ("NZWN", "Pacific/Auckland"),
}
AIRPORTS_CSV = PROCESSED / "session90_airports.csv"
AIRPORTS_CSV_SHA256 = "b53b689f2226e043228725938ad7c47c2069f4831626cc662118559393465db7"   # F132
# The twelve claim tables (F149; data/processed/session106_claim_table.meta.txt): ICAO -> (0-24, 25-48).
CLAIM_TABLES = {
    "EDDM": ("9d9e38201d0aa63ae0da0a20c64254c172f57993df0d99dd767a567a5418c84d",
             "b5600c13948fd7ad6bd6411366b3676211b68dd332e37c3a409262eac3457c7b"),
    "KORD": ("51c69aa5b204f7991ae7522fd850b5b3c4715f017ed4ee2f1b4269a2d4a515ad",
             "2252e3ffb73294e31b4aba1e605f204f70ccc80cbbcb701f79173e0940770662"),
    "CYYZ": ("899e54777fdff5f8ac0b6cc78b15ebea6340a072b23c5acf6c39486c139c25d7",
             "ab631d6e43750071e9b7878cb24127269aae5a3831d1234a299c8a0ab2054b44"),
    "ZGSZ": ("1a83bb1ba7b7c2ed389244fd3362c32e6a641847b3b074680d00a84a858de011",
             "b70b5f4c648fa6e5971084e8993e99fa2d2fffd7394e6e7b262c06aa6d2df0f5"),
    "ZUCK": ("1be74331235cd973b919db7aa8a587b7065eaf154e95f08f03dbf62ac0a89379",
             "35e85af2c47df13afd0fbd8279aadd330157072bb8d1f17f800515619296b096"),
    "NZWN": ("f5c7a598cef58190e593d74cd961fd15912d9fd3ce196f149092807215a92e74",
             "4db4350540342b4a01502731a0daf5b943a6e619a0893ee6bf12ca6ade2f3fc0"),
}

LOOK_CONFIRM = "107"
SCORES_OUT = PROCESSED / "session107_claim_scores.csv"
DAYS_OUT = PROCESSED / "session107_claim_days.csv"
VERDICTS_OUT = PROCESSED / "session107_claim_verdicts.csv"

# D100.3(c), D100.4
T_TRAIN = dt.datetime(2024, 8, 1)          # models: complete-case rows valid before this; trackers start here
LOOKS = [("A", dt.datetime(2024, 8, 1), dt.datetime(2025, 8, 1)),
         ("B", dt.datetime(2025, 8, 1), dt.datetime(2026, 8, 1))]
T_END = LOOKS[-1][2]
CYCLE_HOURS = s97.CYCLE_HOURS
LEADS_A, LEADS_B, LEADS_ALL = s104.LEADS_A, s104.LEADS_B, s104.LEADS_ALL
METHODS = ("raw_gfs", "baseline", "curve")
OUTPUTS = ("hourly", "daily")
HALVES = ("raw_gfs", "persistence")
DAY = dt.timedelta(days=1)
HOUR = dt.timedelta(hours=1)

READ_ALLOWED = True     # --guard-check sets this False: any table read then stops the run


class Refusal(Exception):
    """A mode refused to run. Nothing was read."""


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lgb.__version__}"


# ------------------------------------------------------------------ pure rules (tested in tests/test_stagec.py)

def look_of(cycle):
    """D100.4: the look of a cycle, or None."""
    for label, t0, t1 in LOOKS:
        if t0 <= cycle < t1:
            return label
    return None


def persistence_k(cycle, valid):
    """D100.5: the smallest whole number of days k with valid - 24k hours before the cycle."""
    k = 1
    while not valid - k * DAY < cycle:
        k += 1
    return k


def hourly_persistence(cycle, valid, obs_by_valid):
    """D100.5: the table's observation at valid - 24k hours; None if missing (no older value is used)."""
    return obs_by_valid.get(valid - persistence_k(cycle, valid) * DAY)


def observed_max(d, tzname, obs_by_valid):
    """D98.10(a): the observed maximum of local day d, or None if the day is not usable."""
    _, _, hours = s104.local_day(d, tzname)
    usable = [v for v in (obs_by_valid.get(h) for h in hours) if v is not None]
    return max(usable) if s104.usable_day(len(hours), len(usable)) else None


def persistence_day(cycle, tzname, before):
    """D100.5: the latest local day whose last hour is valid before the cycle, searching back from `before`."""
    d = before
    while True:
        _, _, hours = s104.local_day(d, tzname)
        if hours[-1] < cycle:
            return d
        d -= DAY


def daily_persistence(d, cycle, tzname, obs_by_valid):
    """D100.5: (the persistence day, its observed maximum or None)."""
    p = persistence_day(cycle, tzname, d - DAY)
    return p, observed_max(p, tzname, obs_by_valid)


def margin(m, b):
    """D79.1: 100 x (1 - MAE(method) / MAE(baseline)), and the difference in degrees C."""
    return 100.0 * (1.0 - m / b), b - m


def half_pass(m, b):
    """D100.5, D79.2: strictly lower at full precision; a tie fails; no rows cannot pass."""
    if m is None or b is None:
        return False
    return m < b


def look_pass(raw_half, pers_half):
    return raw_half and pers_half


def verdict(look_a, look_b):
    """D100.6, D71.6."""
    n = int(look_a) + int(look_b)
    return "PASS" if n == 2 else "SPLIT" if n == 1 else "FAIL"


# ------------------------------------------------------------------ airports and tables

def airport_set(names, mode):
    """The airports a mode may run on, by station code or ICAO code. --gate: the
    development airports only; --look: the claim airports only."""
    dev_names = set(DEV) | set(DEV_ICAO.values())
    claim_names = set(CLAIM) | {v[0] for v in CLAIM.values()}
    if mode == "gate":
        bad = [n for n in names if n in claim_names or n not in dev_names]
        if bad:
            raise Refusal(f"--gate runs on the development airports only; refused: {bad}")
        inv = {v: k for k, v in DEV_ICAO.items()}
        return [inv.get(n, n) for n in names]
    bad = [n for n in names if n in dev_names or n not in claim_names]
    if bad:
        raise Refusal(f"--look runs on the claim airports only; refused: {bad}")
    inv = {v[0]: k for k, v in CLAIM.items()}
    return [inv.get(n, n) for n in names]


def tables_of(name):
    """(station code, time zone, [(path, SHA-256, leads in file)]) for one airport."""
    if name in DEV:
        return name, s104.TZ[name], [(STAGEC / s97.TABLES[name][0], s97.TABLES[name][1], range(0, 25)),
                                     (STAGEC / DEV_TABLE25[name][0], DEV_TABLE25[name][1], range(25, 49))]
    st, tz = CLAIM[name]
    h0, h25 = CLAIM_TABLES[name]
    return st, tz, [(STAGEC / f"stagec_claim_f000_024_{name}.csv.gz", h0, range(0, 25)),
                    (STAGEC / f"stagec_claim_f025_048_{name}.csv.gz", h25, range(25, 49))]


def check_claim_zones():
    if sha256_file(AIRPORTS_CSV) != AIRPORTS_CSV_SHA256:
        raise SystemExit("STOP: session90_airports.csv's SHA-256 is not F132's")
    with open(AIRPORTS_CSV, newline="") as f:
        a = {r["icao"]: r for r in csv.DictReader(f)}
    for ic, (st, tz) in CLAIM.items():
        if (a[ic]["iem_id"], a[ic]["time_zone"]) != (st, tz):
            raise SystemExit(f"STOP: {ic}'s IEM id or time zone differs from session90_airports.csv")


def load_rows(path, want, st, leads):
    """As session 97's load_table (and session 104's load_table25), for any table
    file: (cycle, valid, cycle_hour, lead, complete, obs, temp, x) per row, in
    file order, with the same checks."""
    if not READ_ALLOWED:
        raise SystemExit("STOP: a table read was attempted where none is allowed")
    got = sha256_file(path)
    if got != want:
        raise SystemExit(f"STOP: {path.name} SHA-256 {got} is not the recorded {want}")
    lead_set = set(leads)
    rows = []
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != s97.TABLE_COLUMNS:
            raise SystemExit(f"STOP: {path.name} header is not F138.4's")
        ix = {c: i for i, c in enumerate(head)}
        gi = [ix[c] for c in s97.G15]
        for r in rd:
            if r[ix["station"]] != st:
                raise SystemExit(f"STOP: {path.name} holds a row for station {r[ix['station']]}")
            valid = s97.parse_time(r[ix["valid_utc"]])
            s97.check_valid(valid)
            if r[ix["obs_time_utc"]]:
                s97.check_obs_time(s97.parse_time(r[ix["obs_time_utc"]]))
            lead = int(r[ix["lead"]])
            if lead not in lead_set:
                raise SystemExit(f"STOP: {path.name} lead {lead}")
            cycle = s97.parse_time(r[ix["cycle_utc"]])
            x = [s97.fval(r[i]) for i in gi]
            obs = s97.fval(r[ix["obs_tmpc"]])
            complete = r[ix["complete_case"]] == "true"
            if complete != (all(v is not None for v in x) and obs is not None):
                raise SystemExit(f"STOP: {path.name} complete_case disagrees with its columns")
            if x[0] is not None and float(r[ix["temperature_grib_c"]]) != x[0]:
                raise SystemExit(f"STOP: {path.name} temp differs from temperature_grib_c")
            rows.append((cycle, valid, int(r[ix["cycle_hour"]]), lead, complete, obs, x[0], x))
    return rows


# ------------------------------------------------------------------ the frozen method

def fit_part(st, rows, leads, timer):
    """D100.3(c), (d): per cycle hour and lead, one model trained on the
    complete-case rows valid before T_TRAIN (session 104's split_rows_leads with
    T0 = T_TRAIN and T1 = the end of look B), predicting every test row of both
    looks (scored rows, then rows with complete features and no observation) in
    one call; then one tracker through both looks (session 104's correct)."""
    cells, fits = {}, 0
    keep = set(leads)
    sub = [r for r in rows if r[3] in keep]
    train, test = s104.split_rows_leads(sub, T_TRAIN, T_END, leads)
    extra = {(h, n): [] for h in CYCLE_HOURS for n in leads}
    for cycle, valid, h, n, complete, obs, temp, x in sub:
        if not complete and obs is None and all(v is not None for v in x) \
                and s97.fold_role(cycle, valid, T_TRAIN, T_END) == "test":
            extra[(h, n)].append((cycle, x, temp, None))
    for k in extra:
        extra[k].sort(key=lambda r: r[0])
    for h in CYCLE_HOURS:
        for n in leads:
            tr, te, ex = train[(h, n)], test[(h, n)], extra[(h, n)]
            if not tr or not te:
                raise SystemExit(f"STOP: {st} {h}z lead {n}: train {len(tr)}, test {len(te)}")
            if tr[-1][0] >= te[0][0] or max(r[0] for r in tr) + dt.timedelta(hours=n) >= T_TRAIN:
                raise SystemExit(f"STOP: {st} {h}z lead {n}: training not before test")
            t = time.time()
            fc = s97.fit_predict([(r[1], r[2], r[3]) for r in tr],
                                 [(r[1], r[2], r[3]) for r in te] + [(r[1], r[2], r[3]) for r in ex])
            timer["fit"] += time.time() - t
            fits += 1
            base, xbase = fc[:len(te)], fc[len(te):]
            corr, n_used, latest, x_corr, x_n, x_latest = s104.correct(
                [(r[0], r[3], base[i]) for i, r in enumerate(te)], [(r[0], xbase[i]) for i, r in enumerate(ex)], n)
            cells[(h, n)] = {
                "cycles": [r[0] for r in te], "obs": [r[3] for r in te], "raw": [r[2] for r in te],
                "baseline": base, "curve": corr, "n_used": n_used, "latest": latest,
                "x_cycles": [r[0] for r in ex], "x_raw": [r[2] for r in ex], "x_baseline": xbase,
                "x_curve": x_corr, "x_n_used": x_n, "x_latest": x_latest, "n_train": len(tr)}
    return cells, fits


def daily_rows(st, tzname, obs_by_valid, fc):
    """D98.10(a) to (c) over both looks: one row per local day whose cycle is in
    a look, with the raw GFS, baseline and curve maxima and D100.5's persistence."""
    rows, drops = [], {}
    d = LOOKS[0][1].date() - DAY
    while d <= T_END.date():
        s, e, hours = s104.local_day(d, tzname)
        c = s104.day_cycle(s)
        look = look_of(c)
        if look is None:
            if LOOKS[0][1].date() <= d < T_END.date():
                drops["cycle outside both looks"] = drops.get("cycle outside both looks", 0) + 1
            d += DAY
            continue
        if hours[-1] > s104.DAY_LAST_VALID:
            drops["last hour after 2026-07-31T23:00"] = drops.get("last hour after 2026-07-31T23:00", 0) + 1
            d += DAY
            continue
        leads = [int((h - c) / HOUR) for h in hours]
        if min(leads) < 4 or max(leads) > 33:
            raise SystemExit(f"STOP: {st} {d} leads {min(leads)} to {max(leads)}")
        if any(h not in obs_by_valid for h in hours):
            raise SystemExit(f"STOP: {st} {d}: an hour is not in the table")
        usable = [v for v in (obs_by_valid[h] for h in hours) if v is not None]
        obs_ok = s104.usable_day(len(hours), len(usable))
        row = {"station": st, "look": look, "local_date": d, "hours": len(hours), "usable_hours": len(usable),
               "obs_max": max(usable) if obs_ok else None, "obs_reason": "" if obs_ok else "too few usable hours",
               "cycle": c, "first_lead": leads[0], "last_lead": leads[-1]}
        for m in METHODS:
            f = [fc.get((c, n), {}).get(m) for n in leads]
            if any(v is None for v in f):
                row[m], row[m + "_reason"] = None, f"no forecast at {sum(v is None for v in f)} hours"
            else:
                row[m], row[m + "_reason"] = max(f), ""
        row["pers_date"], row["persistence"] = daily_persistence(d, c, tzname, obs_by_valid)
        row["common"] = row["obs_max"] is not None and row["raw_gfs"] is not None and row["curve"] is not None
        row["pers_subset"] = row["common"] and row["persistence"] is not None
        rows.append(row)
        d += DAY
    return rows, drops


def run_airport(name, timer, log=print):
    """Everything D100.3 needs at one airport: the cells, the hourly rows of both
    looks, the days, and the counts."""
    t = time.time()
    st, tzname, files = tables_of(name)
    (p0, h0, l0), (p25, h25, l25) = files
    rows_a = load_rows(p0, h0, st, l0)
    rows_b = load_rows(p25, h25, st, l25)
    cells = {}
    ca, fa = fit_part(st, rows_a, LEADS_A, timer)
    cb, fb = fit_part(st, rows_b, LEADS_B, timer)
    cells.update(ca)
    cells.update(cb)
    obs_map, fc, bad = {}, {}, 0
    for cycle, valid, h, n, complete, obs, temp, x in rows_a + rows_b:
        if valid in obs_map and obs_map[valid] != obs:
            bad += 1
        obs_map[valid] = obs
        if temp is not None:
            fc.setdefault((cycle, n), {})["raw_gfs"] = temp
    if bad:
        raise SystemExit(f"STOP: {st}: {bad} rows give a different observation for the same valid time")
    for (h, n), c in cells.items():
        for pre in ("", "x_"):
            for i, cy in enumerate(c[pre + "cycles"]):
                d = fc.setdefault((cy, n), {})
                d["baseline"] = c[pre + "baseline"][i]
                d["curve"] = c[pre + "curve"][i]
    # hourly rows of both looks, per cell in ascending cycle; persistence by D100.5
    hourly = {}
    late = 0
    for (h, n), c in cells.items():
        recs = []
        for i, cy in enumerate(c["cycles"]):
            valid = cy + n * HOUR
            recs.append((look_of(cy), cy, c["obs"][i], c["raw"][i], c["baseline"][i], c["curve"][i],
                         hourly_persistence(cy, valid, obs_map)))
        hourly[(h, n)] = recs
        for cy, lt in list(zip(c["cycles"], c["latest"])) + list(zip(c["x_cycles"], c["x_latest"])):
            late += lt is not None and not lt < cy
    if late:
        raise SystemExit(f"STOP: {st}: a correction used an error not before its cycle")
    # row counts by look and status (D100.8)
    counts = {}
    for cycle, valid, h, n, complete, obs, temp, x in rows_a + rows_b:
        if n not in LEADS_ALL:
            continue
        lk = look_of(cycle)
        if lk is None:
            continue
        feats = all(v is not None for v in x)
        why = "scored" if complete else "complete features, no observation (predicted, never scored)" \
            if feats and obs is None else "incomplete features"
        counts[(lk, why)] = counts.get((lk, why), 0) + 1
    days, drops = daily_rows(st, tzname, obs_map, fc)
    n_train = {k: c["n_train"] for k, c in cells.items()}
    log(f"  {name} ({st}, {tzname}): {fa + fb} models, training rows per model {min(n_train.values())} to "
        f"{max(n_train.values())}, {time.time() - t:.1f} s", flush=True)
    return {"name": name, "station": st, "tz": tzname, "cells": cells, "hourly": hourly, "days": days,
            "drops": drops, "counts": counts, "fits": fa + fb, "obs_map": obs_map}


# ------------------------------------------------------------------ scoring and the bar

def hourly_sets(res, look, leads=LEADS_ALL, hours=CYCLE_HOURS):
    """The common set's records (cycle hour, lead, then cycle order) and the persistence subset's."""
    common = [r for h in hours for n in leads for r in res["hourly"][(h, n)] if r[0] == look]
    return common, [r for r in common if r[6] is not None]


def hourly_errors(recs, idx):
    return [r[2] - r[idx] for r in recs]


HIDX = {"raw_gfs": 3, "baseline": 4, "curve": 5, "persistence": 6}


def daily_sets(res, look):
    common = [d for d in res["days"] if d["look"] == look and d["common"]]
    return common, [d for d in common if d["pers_subset"]]


def daily_errors(days, m):
    return [d["obs_max"] - d[m] for d in days]


def mae_or_none(e):
    return s97.mae(e) if e else None


def bar_rows(results):
    """D100.5 per airport, look and output: both halves, margins, look pass; then D100.6's verdicts."""
    out, verdicts = [], []
    for res in results:
        for output in OUTPUTS:
            passes = {}
            for look, _, _ in LOOKS:
                if output == "hourly":
                    common, subset = hourly_sets(res, look)
                    e = {m: hourly_errors(common, HIDX[m]) for m in METHODS}
                    ep = {"curve": hourly_errors(subset, HIDX["curve"]),
                          "persistence": hourly_errors(subset, HIDX["persistence"])}
                else:
                    common, subset = daily_sets(res, look)
                    e = {m: daily_errors(common, m) for m in METHODS}
                    ep = {"curve": daily_errors(subset, "curve"), "persistence": daily_errors(subset, "persistence")}
                halves = {}
                for half in HALVES:
                    if half == "raw_gfs":
                        n, m, b = len(common), mae_or_none(e["curve"]), mae_or_none(e["raw_gfs"])
                    else:
                        n, m, b = len(subset), mae_or_none(ep["curve"]), mae_or_none(ep["persistence"])
                    ok = half_pass(m, b)
                    mg, df = margin(m, b) if m is not None and b is not None else (None, None)
                    halves[half] = ok
                    out.append({"icao": res["name"], "station": res["station"], "output": output, "look": look,
                                "half": half, "n": n, "curve_mae": m, "baseline_mae": b, "margin_pct": mg,
                                "diff_c": df, "half_pass": ok})
                passes[look] = look_pass(halves["raw_gfs"], halves["persistence"])
            verdicts.append({"icao": res["name"], "station": res["station"], "output": output,
                             "look_A": passes["A"], "look_B": passes["B"],
                             "verdict": verdict(passes["A"], passes["B"])})
    return out, verdicts


def fmt_opt(v, spec):
    return "none" if v is None else format(v, spec)


def print_bar(results, label):
    rows, verdicts = bar_rows(results)
    print("\n" + "=" * 100)
    print(label)
    print("=" * 100)
    for output in OUTPUTS:
        rs = [r for r in rows if r["output"] == output]
        known = [r for r in rs if r["margin_pct"] is not None]
        print(f"\n{output.upper()}")
        if known:
            s = min(known, key=lambda r: r["margin_pct"])
            print(f"  SMALLEST MARGIN (D79.1, over {len(rs)} values): {s['margin_pct']:+.3f} % "
                  f"({s['diff_c']:+.4f} degrees C), {s['icao']} look {s['look']} against {s['half']}")
        none = [r for r in rs if r["margin_pct"] is None]
        if none:
            print(f"  HALVES WITH NO ROWS (cannot pass): {[(r['icao'], r['look'], r['half']) for r in none]}")
        print(f"  {'airport':<7} {'look':<4} {'half':<12} {'n':>7} {'curve MAE':>19} {'other MAE':>19} "
              f"{'margin %':>9} {'diff C':>8} pass")
        for r in rs:
            print(f"  {r['icao']:<7} {r['look']:<4} {r['half']:<12} {r['n']:>7} {fmt_opt(r['curve_mae'], '>19.16f')} "
                  f"{fmt_opt(r['baseline_mae'], '>19.16f')} {fmt_opt(r['margin_pct'], '>+9.3f')} "
                  f"{fmt_opt(r['diff_c'], '>+8.4f')} {r['half_pass']}")
        vs = [v for v in verdicts if v["output"] == output]
        print("  verdicts (D100.6): " + "; ".join(f"{v['icao']} {v['verdict']} (A {v['look_A']}, B {v['look_B']})"
                                                 for v in vs))
        print(f"  passes at {sum(v['verdict'] == 'PASS' for v in vs)} of {len(vs)} airports in both looks")
    return rows, verdicts


def print_descriptive(results, label):
    """D100.8: never part of the bar."""
    print("\n" + "-" * 100)
    print(label + " D100.8 DESCRIPTIVE FIGURES (never part of the bar).")
    print("-" * 100)
    for res in results:
        nm = res["name"]
        for look, _, _ in LOOKS:
            common, subset = hourly_sets(res, look)
            print(f"  {nm} look {look} hourly: rows " + ", ".join(f"{k[1]} {v}" for k, v in sorted(res["counts"].items())
                                                             if k[0] == look))
            print(f"    common set n {len(common)}: " + ", ".join(
                f"{m} MAE {fmt_opt(mae_or_none(hourly_errors(common, HIDX[m])), '.4f')} mean error "
                f"{fmt_opt(s97.mean_error(hourly_errors(common, HIDX[m])) if common else None, '+.4f')}"
                for m in METHODS))
            print(f"    persistence subset n {len(subset)}: persistence MAE "
                  f"{fmt_opt(mae_or_none(hourly_errors(subset, 6)), '.4f')} mean error "
                  f"{fmt_opt(s97.mean_error(hourly_errors(subset, 6)) if subset else None, '+.4f')}")
            for band, leads in (("3-24", LEADS_A), ("25-48", LEADS_B)):
                cb, _ = hourly_sets(res, look, leads)
                print(f"    leads {band} n {len(cb)}: " + ", ".join(
                    f"{m} {fmt_opt(mae_or_none(hourly_errors(cb, HIDX[m])), '.4f')}" for m in METHODS))
            for h in CYCLE_HOURS:
                ch, _ = hourly_sets(res, look, LEADS_ALL, (h,))
                print(f"    {h:02d}z n {len(ch)}: " + ", ".join(
                    f"{m} {fmt_opt(mae_or_none(hourly_errors(ch, HIDX[m])), '.4f')}" for m in METHODS))
            dc, dsub = daily_sets(res, look)
            alld = [d for d in res["days"] if d["look"] == look]
            print(f"  {nm} look {look} daily: local days {len(alld)}, common {len(dc)}, persistence subset {len(dsub)}; "
                  + ", ".join(f"{m} MAE {fmt_opt(mae_or_none(daily_errors(dc, m)), '.4f')} mean error "
                              f"{fmt_opt(s97.mean_error(daily_errors(dc, m)) if dc else None, '+.4f')}" for m in METHODS)
                  + f"; persistence MAE {fmt_opt(mae_or_none(daily_errors(dsub, 'persistence')), '.4f')}")
            reasons = {}
            for d in alld:
                if d["obs_max"] is None:
                    reasons["observed: " + d["obs_reason"]] = reasons.get("observed: " + d["obs_reason"], 0) + 1
                for m in METHODS:
                    if d[m] is None:
                        reasons[m + ": " + d[m + "_reason"]] = reasons.get(m + ": " + d[m + "_reason"], 0) + 1
                if d["common"] and d["persistence"] is None:
                    reasons["no persistence value"] = reasons.get("no persistence value", 0) + 1
            ch = {}
            for d in dc:
                ch[d["cycle"].hour] = ch.get(d["cycle"].hour, 0) + 1
            print(f"    days dropped or short, by reason: {reasons or 'none'}; cycle hours used: "
                  + ", ".join(f"{h:02d}z {v}" for h, v in sorted(ch.items())))
        print(f"  {nm}: days outside the looks, by reason: {res['drops'] or 'none'}")


# ------------------------------------------------------------------ --gate

def gate_compare(results):
    """D100.9(c)(2): look A against session 104's fold 2024-25."""
    print(f"\nGate 2 (D100.9(c)): look A against session 104's fold {GATE_FOLD}")
    for p, want in ((S104_SCORES, S104_SCORES_SHA256), (S104_DAYS, S104_DAYS_SHA256)):
        got = sha256_file(p)
        if got != want:
            raise SystemExit(f"STOP: {p.name} SHA-256 {got} is not F147.7's")
    rec = {}
    with open(S104_SCORES, newline="") as f:
        for r in csv.DictReader(f):
            if r["fold"] == GATE_FOLD:
                rec[(r["station"], int(r["cycle_hour"]), int(r["lead"]), r["method"])] = (int(r["n"]), float(r["mae"]))
    by = {res["name"]: res for res in results}
    equal, compared, bad = 0, 0, []
    for (st, h, n, m), (rn, rm) in rec.items():
        if st not in by:
            continue
        recs = [r for r in by[st]["hourly"][(h, n)] if r[0] == "A"]
        e = hourly_errors(recs, HIDX[m])
        compared += 1
        if len(e) == rn and s97.mae(e) == rm:
            equal += 1
        else:
            bad.append((st, h, n, m, len(e), rn))
    print(f"  hourly cells (airport, cycle hour, lead 3 to 48, method raw_gfs / baseline / curve): "
          f"{equal} of {compared} equal (n and MAE, exact); expected {len(by) * 4 * 46 * 3}")
    for b in bad[:20]:
        print("    MISMATCH", b)
    # days
    want_days = {}
    with open(S104_DAYS, newline="") as f:
        for r in csv.DictReader(f):
            if r["fold"] == GATE_FOLD and r["station"] in by:
                want_days[(r["station"], r["local_date"])] = r
    got_days = {(res["name"], d["local_date"].isoformat()): d for res in results for d in res["days"]
                if d["look"] == "A"}

    def val(s):
        return None if s == "" else float(s)

    d_eq, d_bad = 0, []
    for k, r in want_days.items():
        g = got_days.get(k)
        same = g is not None and g["cycle"].strftime("%Y-%m-%dT%H:%MZ") == r["cycle"] \
            and g["obs_max"] == val(r["obs_max"]) and g["raw_gfs"] == val(r["raw_gfs_max"]) \
            and g["curve"] == val(r["curve_max"])
        d_eq += same
        if not same:
            d_bad.append(k)
    extra = sorted(set(got_days) - set(want_days))
    print(f"  {GATE_FOLD} days (cycle, observed, raw GFS and curve maxima, exact): {d_eq} of {len(want_days)} equal; "
          f"look A days not in session 104's file: {len(extra)}")
    for b in (d_bad + extra)[:20]:
        print("    MISMATCH", b)
    ok = equal == compared == len(by) * 4 * 46 * 3 and d_eq == len(want_days) and not extra and want_days
    if not ok:
        raise SystemExit("STOP: gate 2 (look A against session 104's fold 2024-25) failed")
    print("Gate 2: PASS")
    return compared, len(want_days)


def run_gate(args):
    t0 = time.time()
    names = airport_set(args.airports or DEV, "gate")
    print(f"SESSION 106 --gate (offline), start {now_utc()}; {versions()}")
    print(f"scripts' SHA-256 checked before import: session104_curve_cv.py {S104_SCRIPT_SHA256} (it checks "
          f"sessions 97, 100 and 103: {s104.IMPORTED})")
    print(f"LGB_PARAMS: {s97.LGB_PARAMS}; w = {s104.W}; training rows valid before {T_TRAIN:%Y-%m-%dT%H:%M}; "
          f"looks {[(l, f'{a:%Y-%m-%d}', f'{b:%Y-%m-%d}') for l, a, b in LOOKS]}")
    print(f"airports: {names} (development airports only)")
    s104.gate_check()
    # the loader against session 97's own, on F138's tables
    timer = {"fit": 0.0}
    print("\nFrozen fits (184 models per airport) and trackers through both looks:")
    results = [run_airport(nm, timer) for nm in names]
    fits = sum(r["fits"] for r in results)
    print(f"fits {fits}; fit time {timer['fit']:.1f} s")
    for res in results:
        mine = load_rows(*tables_of(res["name"])[2][0][:2], res["station"], range(0, 25))
        ref = s97.load_table(res["name"], leads=tuple(range(0, 25)))
        if mine != ref:
            raise SystemExit(f"STOP: the loader differs from session 97's load_table at {res['name']}")
    print("loader check: this script's load_rows equals session 97's load_table on F138's six tables: True")
    n_cells, n_days = gate_compare(results)
    label = "Gate 3: DEVELOPMENT AIRPORTS, SPENT YEARS, DESCRIPTIVE ONLY, NOT A RESULT (look B smoke test and both " \
            "looks' bar)."
    print_bar(results, label)
    print_descriptive(results, "DEVELOPMENT AIRPORTS, SPENT YEARS, DESCRIPTIVE ONLY, NOT A RESULT.")
    print(f"\nGATE PASS: gate 1 tracker self-check; gate 2 {n_cells} cells and {n_days} days equal; gate 3 smoke test "
          f"ran. Fits {fits}; end {now_utc()}; run time {time.time() - t0:.1f} s")
    return 0


# ------------------------------------------------------------------ --look (session 107 only)

def look_refusals(args):
    """D100.9(d): every refusal is checked before any data is read."""
    if args.confirm_look != LOOK_CONFIRM:
        raise Refusal(f"--look needs --confirm-look {LOOK_CONFIRM} (D100.9(d), D100.12); got {args.confirm_look!r}")
    names = airport_set(args.airports or list(CLAIM), "look")
    there = [p.name for p in (SCORES_OUT, DAYS_OUT, VERDICTS_OUT) if p.exists()
             or p.with_name(p.name + ".partial").exists()]
    if there:
        raise Refusal(f"an output file already exists: {there}")
    return names


def run_look(args):
    names = look_refusals(args)
    t0 = time.time()
    print(f"SESSION 107 --look (offline), start {now_utc()}; {versions()}")
    print("STAGE C'S CLAIM LOOK (DECISIONS D100), RUN ONCE.")
    check_claim_zones()
    s104.gate_check()
    timer = {"fit": 0.0}
    results = [run_airport(nm, timer) for nm in names]
    rows, verdicts = print_bar(results, "STAGE C CLAIM LOOK (D100.5, D100.6): the curve against raw GFS and "
                                        "persistence, per airport, look and output.")
    print_descriptive(results, "CLAIM AIRPORTS.")
    # scores
    sc = []
    for res in results:
        for look, _, _ in LOOKS:
            for h in CYCLE_HOURS:
                for n in LEADS_ALL:
                    recs = [r for r in res["hourly"][(h, n)] if r[0] == look]
                    sub = [r for r in recs if r[6] is not None]
                    for m in METHODS:
                        e = hourly_errors(recs, HIDX[m])
                        sc.append([res["name"], res["station"], look, "hourly", m, "common", h, n, len(e),
                                   mae_or_none(e), s97.mean_error(e) if e else None])
                    for m in ("curve", "persistence"):
                        e = hourly_errors(sub, HIDX[m])
                        sc.append([res["name"], res["station"], look, "hourly", m, "persistence_subset", h, n, len(e),
                                   mae_or_none(e), s97.mean_error(e) if e else None])
            dc, dsub = daily_sets(res, look)
            for m in METHODS:
                e = daily_errors(dc, m)
                sc.append([res["name"], res["station"], look, "daily", m, "common", "", "", len(e), mae_or_none(e),
                           s97.mean_error(e) if e else None])
            for m in ("curve", "persistence"):
                e = daily_errors(dsub, m)
                sc.append([res["name"], res["station"], look, "daily", m, "persistence_subset", "", "", len(e),
                           mae_or_none(e), s97.mean_error(e) if e else None])
    head = ["icao", "station", "look", "output", "method", "row_set", "cycle_hour", "lead", "n", "mae", "mean_error"]
    s97.write_new(SCORES_OUT, s97.csv_text(head, [["" if v is None else s97.fmt(v) for v in r] for r in sc]))
    # days
    dcols = ["icao", "station", "look", "local_date", "hours", "usable_hours", "obs_max", "obs_reason", "cycle",
             "first_lead", "last_lead"] + [x for m in METHODS for x in (m + "_max", m + "_reason")] + \
        ["persistence_date", "persistence_max", "common", "persistence_subset"]
    drows = []
    for res in results:
        for d in res["days"]:
            drows.append([res["name"], d["station"], d["look"], d["local_date"].isoformat(), d["hours"],
                          d["usable_hours"], d["obs_max"], d["obs_reason"], d["cycle"].strftime("%Y-%m-%dT%H:%MZ"),
                          d["first_lead"], d["last_lead"]]
                         + [x for m in METHODS for x in (d[m], d[m + "_reason"])]
                         + [d["pers_date"].isoformat(), d["persistence"], d["common"], d["pers_subset"]])
    s97.write_new(DAYS_OUT, s97.csv_text(dcols, [["" if v is None else "true" if v is True else "false"
                                                  if v is False else s97.fmt(v) for v in r] for r in drows]))
    # verdicts
    vcols = ["icao", "station", "output", "look", "half", "n", "curve_mae", "other_mae", "margin_pct", "diff_c",
             "half_pass", "look_pass", "verdict"]
    vrows = []
    vmap = {(v["icao"], v["output"]): v for v in verdicts}
    for r in rows:
        v = vmap[(r["icao"], r["output"])]
        vrows.append([r["icao"], r["station"], r["output"], r["look"], r["half"], r["n"], r["curve_mae"],
                      r["baseline_mae"], r["margin_pct"], r["diff_c"], r["half_pass"], v["look_" + r["look"]],
                      v["verdict"]])
    s97.write_new(VERDICTS_OUT, s97.csv_text(vcols, [["" if v is None else "true" if v is True else "false"
                                                      if v is False else s97.fmt(v) for v in r] for r in vrows]))
    for p in (SCORES_OUT, DAYS_OUT, VERDICTS_OUT):
        print(f"wrote {p.relative_to(ROOT)}: SHA-256 {sha256_file(p)}")
    print(f"\nend {now_utc()}; run time {time.time() - t0:.1f} s; fits {sum(r['fits'] for r in results)}")
    return 0


# ------------------------------------------------------------------ --guard-check and --meta

def run_guard_check(args):
    global READ_ALLOWED
    READ_ALLOWED = False
    print(f"SESSION 106 --guard-check (offline, no data read), {now_utc()}")
    cases = [
        ("--look without --confirm-look", argparse.Namespace(confirm_look=None, airports=None), run_look),
        ("--look --confirm-look 107 with a development airport (KDSM)",
         argparse.Namespace(confirm_look=LOOK_CONFIRM, airports=["KDSM"]), run_look),
        ("--look --confirm-look 106 (wrong session)", argparse.Namespace(confirm_look="106", airports=None), run_look),
        ("--gate with a claim airport (EDDM)", argparse.Namespace(airports=["EDDM"]), run_gate),
        ("--gate with a claim airport by IEM id (ORD)", argparse.Namespace(airports=["ORD"]), run_gate),
    ]
    ok = True
    for label, ns, fn in cases:
        try:
            fn(ns)
            print(f"  NOT REFUSED: {label}")
            ok = False
        except Refusal as e:
            print(f"  refused: {label}: {e}")
    print(f"output files present: {[p.name for p in (SCORES_OUT, DAYS_OUT, VERDICTS_OUT) if p.exists()] or 'none'}")
    print("GUARD CHECK: PASS (every case refused before any read)" if ok else "GUARD CHECK: FAIL")
    return 0 if ok else 1


def run_meta(args):
    lines = [
        "Meta of scripts/session106_claim_look.py (session 106; printed into notes/session-106-output.txt only).",
        f"written     : {now_utc()}",
        f"script sha256: {sha256_file(SCRIPT)}",
        f"imported    : scripts/session104_curve_cv.py sha256 {S104_SCRIPT_SHA256} (F147), which checks "
        + "; ".join(f"{k} {v}" for k, v in s104.IMPORTED.items()),
        f"versions    : {versions()}",
        f"LGB_PARAMS  : {s97.LGB_PARAMS}",
        f"w           : {s104.W}",
        f"G15 order   : {s97.G15}",
        f"training    : complete-case rows valid before {T_TRAIN:%Y-%m-%dT%H:%M} UTC; 184 models per airport; frozen",
        f"looks       : " + "; ".join(f"{l} cycles {a:%Y-%m-%dT%H} to {(b - dt.timedelta(hours=6)):%Y-%m-%dT%H}"
                                      for l, a, b in LOOKS),
        "gate inputs :",
        f"  {S104_SCORES.relative_to(ROOT)} sha256 {S104_SCORES_SHA256} (F147.7)",
        f"  {S104_DAYS.relative_to(ROOT)} sha256 {S104_DAYS_SHA256} (F147.7)",
    ]
    lines += [f"  {s97.TABLES[st][0]} sha256 {s97.TABLES[st][1]} (F138.4)" for st in DEV]
    lines += [f"  {DEV_TABLE25[st][0]} sha256 {DEV_TABLE25[st][1]} (F147.2)" for st in DEV]
    lines += ["claim inputs (for --look, session 107; F149):"]
    lines += [f"  stagec_claim_{hs}_{ic}.csv.gz sha256 {h}" for ic, hh in CLAIM_TABLES.items()
              for hs, h in zip(("f000_024", "f025_048"), hh)]
    lines += [f"  time zones: " + "; ".join(f"{ic} ({st}) {tz}" for ic, (st, tz) in CLAIM.items())]
    lines += [f"look outputs (refused if present): {SCORES_OUT.name}, {DAYS_OUT.name}, {VERDICTS_OUT.name}"]
    print("\n".join(lines))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("gate", "look", "guard-check", "meta"):
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--confirm-look", default=None)
    ap.add_argument("--airports", nargs="+", default=None)
    a = ap.parse_args()
    fn = {"gate": run_gate, "look": run_look, "guard_check": run_guard_check, "meta": run_meta}
    try:
        return fn[next(k for k in fn if getattr(a, k))](a)
    except Refusal as e:
        print(f"REFUSED: {e}")
        return 2
    except s97.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
