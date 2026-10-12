"""Session 109: the live package's gates against the record (DECISIONS D103.11).

Every gate here uses the package's code (src/mlwx) for the arithmetic under test. This script
only reads files, loops over the record's plan and compares. It computes no score on any row
valid on or after 2026-08-01 (standing rule of session 109); the live adapters' gates (C, D)
touch the network only to the AWS GFS archive and IEM.

Modes (exactly one):
  --gate-a      Step 3, Gate A. Offline. Rebuilds the development tables (leads 0 to 24 and 25 to 48)
                and the six claim tables (both hour sets) from the committed pull extracts
                (MLwx-pull/, MLwx-pull-f025-048/) and the committed observation files, with
                mlwx.features, mlwx.observations and mlwx.tables. Each must equal the recorded
                table by SHA-256 (F138.4, F147.2, F149.2). Writes nothing.
  --trial       Offline. Gate A for 2022-01 only, compared line by line with the same rows of the
                recorded files (a quick check before the full run). Writes nothing.
  --gate-b      Step 3, Gate B. Offline. Reproduces F147's hourly curve scores (leads 3 to 48) and
                F147.6's daily maximum scores at the development airports, with mlwx.baseline,
                mlwx.tracker and mlwx.dailymax: every cell, every day, and the two recorded files
                by SHA-256. A build-choice reproduction (SPEC 2.5); the claim look is not run.
                Writes nothing.
  --gate-c      Step 5, Gate C. Network (AWS GFS archive only). See run_gate_c.
  --gate-d      Step 6, Gate D. Network (IEM only). See run_gate_d.

Nothing in the repository is written by any mode.
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import math
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from mlwx import baseline, config, dailymax, features, gfs, observations, tables, tracker  # noqa: E402

MODEL = config.GFS
AIRPORTS = config.load_airports(MODEL)
DEV = [a for a in AIRPORTS if a.role == "development"]

PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"
PULL_00 = ROOT.parent / "MLwx-pull"
PULL_25 = ROOT.parent / "MLwx-pull-f025-048"
STAGEC = ROOT.parent / "MLwx-stagec"

# The window of the pull (D83.5(b)) and the plan (session 91's plan_chunk, ported).
FIRST_VALID = dt.datetime(2021, 3, 24, 0)
LAST_VALID = dt.datetime(2026, 7, 31, 23)
LAST_OBS = dt.datetime(2026, 7, 31, 23, 59)
FIRST_CYCLE = MODEL.first_cycle
FIRST_MONTH, LAST_MONTH = (2021, 3), (2026, 7)
HOURSETS = {"f000_024": (0, 24), "f025_048": (25, 48)}
OBS_PIECES = ["2021-03-24_2021-12-31", "2022-01-01_2022-12-31", "2023-01-01_2023-12-31",
              "2024-01-01_2024-12-31", "2025-01-01_2025-12-31", "2026-01-01_2026-07-31"]
STATUS_WHOLE = "ok (whole file)"
OK_STATUSES = features.OK_STATUSES
MAN_COLS = ["cycle_utc", "fhour", "field", "idx_line", "byte_range", "bytes", "status", "step_range",
            "process_type", "reason"]
FIELD_NAMES = [f.name for f in MODEL.fields]
POINT_COLS = ["cycle_utc", "fhour", "valid_utc", "icao"] + [f"{n}_{k}" for n in FIELD_NAMES for k in (1, 2, 3, 4)]

# Recorded table SHA-256 (D98.2: held here as constants; tests/test_live.py checks them against the record).
DEV_0_24 = {   # F138.4
    "EGLC": "af8848e091c79aecac5f809536e4dec20757d288f7ebc1cf3e830d33a69c9126",
    "LFPG": "5b113123c7642eefb8d212cbe5151f43e8ba343a231dc90d4461ed104e6b661f",
    "KDSM": "17461736cd23585781ebf01a842469a1ea6b0e93571bea250869a23271dc0e32",
    "YSDU": "57a11a4f00250304f289de158223eff45f841d572e3c3c7f65e5b6fc6c0fa829",
    "KRNO": "6e2d0779f6b5ea92dc77e3b074030ac3676bd90cffe3b44ab6e3441c06831ec3",
    "KSFO": "11fa6385f05c57cf627734d9caed13927f1e176e07c5fc039f700d30fd1ceff8",
}
DEV_25_48 = {  # session104_stagec_f025_048_table.meta.txt (SHA-256 27622ada...5859, F147.2)
    "EGLC": "947bf2f0920e1a1f972ea9297fcc9bdc5c987562e13ee5daa7ae5ab866066ea9",
    "LFPG": "04dbd411dbd683dfe3a09597ea8407cc75c8afc86100b31a8396caca0ff52c35",
    "KDSM": "bd2d80c01211a3c399d6904068bfb9377b0ad9091e13878621526835434ee2f3",
    "YSDU": "b801fcc2d9e2c9dd843ea920e8dd8ac88f33f5db7057bb4ae1ca46a2b16981ac",
    "KRNO": "3ca1d4ff8933f14c6e898525ba445af080b92c0545989fe39b3d7bdbfdd6bd58",
    "KSFO": "2e355c0146e1bc8923f632d208c084f646ec3ebcd9dfa2bb22e22c363e81b84b",
}
CLAIM_TABLES = {   # F149.2: (0-24, 25-48)
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
# Recorded F147 files (F147.7).
F147_SCORES_SHA256 = "69ec86bf600fcb2c5b8ad0f8ec0cb8ed69adb314813e9ab1ee4b578f0fffa35e"
F147_DAYS_SHA256 = "65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3"
F147_CURVE_HEADLINE_3_48 = 1.0891748115841342          # F147.5, full precision
# F147.5 (leads 3 to 48) and F147.6 (daily maximum): MAE at 4 decimals, raw GFS / baseline / curve.
F147_HOURLY_3_48 = {"EGLC": (1.0425, 0.8375, 0.8386), "LFPG": (1.2336, 0.9596, 0.9544), "DSM": (1.8795, 1.3231, 1.3000),
                    "YSDU": (1.5226, 1.2631, 1.2304), "RNO": (2.2187, 1.2284, 1.2079), "SFO": (1.2923, 1.0848, 1.0037),
                    "headline": (1.5315, 1.1161, 1.0892)}
F147_DAILY = {"EGLC": (0.9460, 0.8479, 0.8410), "LFPG": (1.1968, 0.9780, 0.9558), "DSM": (1.7297, 1.2543, 1.2240),
              "YSDU": (1.0861, 1.0475, 1.0268), "RNO": (1.5511, 0.9490, 0.9477), "SFO": (1.6635, 1.2489, 1.2076),
              "headline": (1.3622, 1.0543, 1.0338)}
F147_DAYS_N = {"EGLC": 1095, "LFPG": 1094, "DSM": 1095, "YSDU": 1085, "RNO": 1093, "SFO": 1093}


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def table_name(a, hs):
    if a.role == "development":
        return f"stagec_dev_{a.icao}.csv.gz" if hs == "f000_024" else f"stagec_dev_f025_048_{a.icao}.csv.gz"
    return f"stagec_claim_{hs}_{a.icao}.csv.gz"


def recorded_sha(a, hs):
    if a.role == "development":
        return (DEV_0_24 if hs == "f000_024" else DEV_25_48)[a.icao]
    return CLAIM_TABLES[a.icao][0 if hs == "f000_024" else 1]


# ------------------------------------------------------------------ the plan (session 91's, ported)

def all_months():
    y, m = FIRST_MONTH
    while (y, m) <= LAST_MONTH:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def month_cycles(year, month):
    d = dt.date(year, month, 1)
    out = []
    while d.month == month:
        out += [dt.datetime(d.year, d.month, d.day, h) for h in MODEL.cycle_hours]
        d += dt.timedelta(days=1)
    return out


def plan_chunk(cycles, hours):
    """[(cycle, [fh, ...])]: a forecast hour whose valid time is outside the pull window is not in the
    plan; a cycle with none, or before the first v16 cycle, is left out."""
    a, b = hours
    plan = []
    for c in cycles:
        if c < FIRST_CYCLE:
            continue
        fhs = [fh for fh in range(a, b + 1) if FIRST_VALID <= c + dt.timedelta(hours=fh) <= LAST_VALID]
        if fhs:
            plan.append((c, fhs))
    return plan


def prior_needs(hours):
    """The forecast hours below hours[0] that R or T at any lead in hours needs."""
    need = set()
    for n in range(hours[0], hours[1] + 1):
        for fh in (features.r_inputs(n) or []) + (features.t_inputs(n) or []):
            if fh < hours[0]:
                need.add(fh)
    return need


# ------------------------------------------------------------------ reading the pull and the observations

def sha256_file(path):
    return tables.sha256_file(path)


def read_pull_month(d, month, icaos):
    """The manifest statuses and the kept airports' points rows of one month."""
    with gzip.open(d / f"manifest_{month}.csv.gz", "rt", newline="") as f:
        rd = csv.reader(f)
        if next(rd) != MAN_COLS:
            raise SystemExit(f"STOP: manifest_{month} header")
        mc = {c: i for i, c in enumerate(MAN_COLS)}
        status = {}
        for r in rd:
            k = (r[mc["cycle_utc"]], int(r[mc["fhour"]]), r[mc["field"]])
            if k in status:
                raise SystemExit(f"STOP: duplicate manifest key {k}")
            status[k] = r[mc["status"]]
    points = {}
    with gzip.open(d / f"gfs_points_{month}.csv.gz", "rt", newline="") as f:
        rd = csv.reader(f)
        if next(rd) != POINT_COLS:
            raise SystemExit(f"STOP: gfs_points_{month} header")
        for r in rd:
            if r[3] not in icaos:
                continue
            k = (r[0], int(r[1]), r[3])
            if k in points:
                raise SystemExit(f"STOP: duplicate points key {k}")
            points[k] = r
    return status, points


def load_values(c_iso, cycle, fhs, status, points, a, val, stat):
    """Bilinear on the four stored values of every ok message (the package's arithmetic)."""
    col_i = {c: i for i, c in enumerate(POINT_COLS)}
    for fh in fhs:
        r = points[(c_iso, fh, a.icao)]
        if r[2] != tables.iso(cycle + dt.timedelta(hours=fh)):
            raise SystemExit(f"STOP: valid_utc {r[2]} at {c_iso} f{fh:03d}")
        for fname in FIELD_NAMES:
            s = status[(c_iso, fh, fname)]
            stat[(fh, fname)] = s
            cells = [r[col_i[f"{fname}_{k}"]] for k in (1, 2, 3, 4)]
            if s in OK_STATUSES:
                v4 = [float(x) for x in cells]
                if not all(math.isfinite(x) for x in v4):
                    raise SystemExit(f"STOP: non-finite stored value at {c_iso} f{fh:03d} {fname}")
                val[(fh, fname)] = features.bilinear_stored(a.point_list, a.lat, a.lon, v4)
            elif any(x != "" for x in cells):
                raise SystemExit(f"STOP: a filled cell in a non-ok message at {c_iso} f{fh:03d} {fname}")


def load_reports(a):
    """The six yearly routine files of one airport as one ReportSet. Every report's time is checked
    against the limit before any temperature is read."""
    stats = observations.new_stats()
    reports = []
    for piece in OBS_PIECES:
        text = (RAW / f"iem_asos_{a.station}_{piece}_routine.csv").read_text()
        for r in csv.DictReader(io.StringIO(text)):
            if dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M") > LAST_OBS:
                raise SystemExit(f"STOP: an observation after {LAST_OBS} in {a.station} {piece}")
        reports += observations.parse_reports(text, a.station, stats)
    return observations.ReportSet(reports, stats)


# ------------------------------------------------------------------ Gate A

def build_tables(hs, airports, months=None, log=print):
    """Rows of every airport's table for one hour set, as the package builds them. Returns
    ({icao: lines}, {icao: observation stats}, plan rows)."""
    hours = HOURSETS[hs]
    main_dir, prior_dir = (PULL_00, None) if hs == "f000_024" else (PULL_25, PULL_00)
    need = prior_needs(hours) if prior_dir is not None else set()
    icaos = {a.icao for a in airports}
    reports = {a.icao: load_reports(a) for a in airports}
    lines = {a.icao: [",".join(tables.COLUMNS)] for a in airports}
    expected = 0
    for y, m in all_months():
        month = f"{y}-{m:02d}"
        if months is not None and month not in months:
            continue
        plan = plan_chunk(month_cycles(y, m), hours)
        status, points = read_pull_month(main_dir, month, icaos)
        prior_plan = {}
        if need:
            prior_plan = {c: fhs for c, fhs in plan_chunk(month_cycles(y, m), (0, 24))}
            p_status, p_points = read_pull_month(prior_dir, month, icaos)
        for cycle, fhs in plan:
            c_iso = tables.iso(cycle)
            prior = sorted(need & set(prior_plan.get(cycle, []))) if need else []
            in_plan = set(fhs) | set(prior)
            expected += len(fhs)
            for a in airports:
                val, stat = {}, {}
                load_values(c_iso, cycle, fhs, status, points, a, val, stat)
                if prior:
                    load_values(c_iso, cycle, prior, p_status, p_points, a, val, stat)
                for n in fhs:
                    valid = cycle + dt.timedelta(hours=n)
                    if valid > LAST_VALID:
                        raise SystemExit(f"STOP: valid time {valid} is after {LAST_VALID}")
                    out, reason, used = features.build_row(a, cycle, n, in_plan, val, stat)
                    o, o_time = reports[a.icao].nearest(valid)
                    whole = any(stat[k] == STATUS_WHOLE for k in used)
                    line, _ = tables.table_line(a.station, cycle, n, out, o, o_time, whole)
                    lines[a.icao].append(line)
        log(f"  {hs} {month}: {len(plan)} cycles, {sum(len(f) for _, f in plan)} rows per airport ({now_utc()})")
    for a in airports:
        if len(lines[a.icao]) - 1 != expected:
            raise SystemExit(f"STOP: {a.icao} has {len(lines[a.icao]) - 1} rows, the plan {expected}")
    return lines, {a.icao: reports[a.icao].stats for a in airports}, expected


def run_trial(args):
    print(f"SESSION 109 --trial (offline), {now_utc()}: 2022-01, every airport, both hour sets, against the recorded files")
    ok = True
    for hs in HOURSETS:
        lines, _, n = build_tables(hs, AIRPORTS, months={"2022-01"}, log=lambda *a: None)
        for a in AIRPORTS:
            with gzip.open(STAGEC / table_name(a, hs), "rt", newline="") as f:
                old = [ln.rstrip("\n") for ln in f]
            old_rows = [old[0]] + [ln for ln in old[1:] if ln.split(",", 2)[1].startswith("2022-01")]
            same = old_rows == lines[a.icao]
            diff = sum(1 for x, y in zip(old_rows, lines[a.icao]) if x != y)
            ok &= same
            print(f"  {hs} {a.icao}: rebuilt {len(lines[a.icao]) - 1} rows; recorded file's 2022-01 rows "
                  f"{len(old_rows) - 1}; lines differing {diff}; equal {same}")
    print("TRIAL: PASS" if ok else "TRIAL: FAIL")
    return 0 if ok else 1


def run_gate_a(args):
    t0 = time.time()
    print(f"SESSION 109 --gate-a (offline), {now_utc()}: the package rebuilds the development and claim tables")
    inv = {PULL_00: ("session95_pull_inventory.csv", None),
           PULL_25: ("session104_pull_f025_048_inventory.csv", "5b6cd6f99dcadd0df5bbc313988514495d906126738df6f45944e2ce9208f9d1")}
    for d, (name, want) in inv.items():
        rows = list(csv.DictReader(open(PROCESSED / name, newline="")))
        have = sorted(p.name for p in d.iterdir())
        bad = [r["asset"] for r in rows if (d / r["asset"]).stat().st_size != int(r["bytes"])
               or sha256_file(d / r["asset"]) != r["sha256"]]
        print(f"pull folder {d.name}: {len(have)} files, inventory {name} rows {len(rows)}; names equal "
              f"{have == sorted(r['asset'] for r in rows)}; bytes and SHA-256 equal for all: {not bad}"
              + (f"; inventory SHA-256 equal to the record: {sha256_file(PROCESSED / name) == want}" if want else ""))
        if bad or have != sorted(r["asset"] for r in rows) or (want and sha256_file(PROCESSED / name) != want):
            raise SystemExit("STOP: a pull file differs from its inventory")
    results = []
    for hs in HOURSETS:
        lines, ostats, n_plan = build_tables(hs, AIRPORTS)
        for a in AIRPORTS:
            data = tables.table_bytes(lines[a.icao])
            sha = tables.sha256_bytes(data)
            want = recorded_sha(a, hs)
            on_disk = sha256_file(STAGEC / table_name(a, hs))
            good = sha == want
            results.append((hs, a.icao, good))
            s = ostats[a.icao]
            print(f"  {table_name(a, hs)}: rows {len(lines[a.icao]) - 1} (plan {n_plan}), bytes {len(data):,}, SHA-256 {sha}; "
                  f"recorded equal {good}; recorded file on disk equal {on_disk == want}; observations: reports {s['rows']}, "
                  f"no usable tmpc {s['no_temp']}, non-finite {s['nonfinite']}, repeated timestamps {s['duplicates']}, ties {s['ties']}")
        del lines
    n_ok = sum(1 for *_, g in results if g)
    print(f"\nGate A: {n_ok} of {len(results)} tables byte-equal to the record by SHA-256 "
          f"({sum(1 for h, i, g in results if g and h == 'f000_024')} of 12 at hours 0 to 24, "
          f"{sum(1 for h, i, g in results if g and h == 'f025_048')} of 12 at hours 25 to 48); run time {time.time() - t0:.1f} s")
    print("GATE A: PASS" if n_ok == len(results) == 24 else "GATE A: FAIL")
    return 0 if n_ok == len(results) == 24 else 1


# ------------------------------------------------------------------ Gate B

FOLDS = [("2023-24", dt.datetime(2023, 8, 1), dt.datetime(2024, 8, 1)),
         ("2024-25", dt.datetime(2024, 8, 1), dt.datetime(2025, 8, 1)),
         ("2025-26", dt.datetime(2025, 8, 1), dt.datetime(2026, 8, 1))]    # D89.3
CYCLE_HOURS = MODEL.cycle_hours
LEADS_A, LEADS_B = tuple(range(3, 25)), tuple(range(25, 49))
LEADS_ALL = LEADS_A + LEADS_B
METHODS = ("raw_gfs", "baseline", "curve")
DAY_LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)


def mae(errors):
    """G24: the NumPy mean of the absolute errors, full precision."""
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


def mean_error(errors):
    return float(np.mean(np.asarray(errors, dtype=float)))


def fold_role(cycle, valid, t0, t1):
    """D89.3: 'train' if valid < T0; 'test' if T0 <= cycle < T1; 'boundary' if cycle < T0 <= valid."""
    if valid < t0:
        return "train"
    if t0 <= cycle < t1:
        return "test"
    if cycle < t0:
        return "boundary"
    return None


def fmt(v):
    return repr(v) if isinstance(v, float) else str(v)


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


def correct(scored, extra, lead):
    """The tracker on one cell, as the record runs it: scored rows (cycle, obs, baseline) are
    corrected by tracker.track; a row with complete features and no observation is corrected by
    running track on the scored rows from earlier cycles followed by that row, so it gets b from
    exactly the errors valid before its cycle and its own (absent) error is never queued."""
    rows = [(c, lead, o, f) for c, o, f in scored]
    corr, n_used, latest, _ = tracker.track(rows)
    x_corr = []
    for c, f in extra:
        pre = [r for r in rows if r[0] < c] + [(c, lead, f, f)]
        cc, _, _, _ = tracker.track(pre)
        x_corr.append(cc[-1])
    return corr, n_used, x_corr


def score_airport(rows_all, leads, timer):
    """Per fold, cycle hour and lead: one baseline model fitted on the complete-case rows valid before
    T0, predicting the scored test rows and the rows with complete features and no observation in one
    call, then the tracker. rows_all: table rows (cycle, valid, h, n, complete, obs, temp, x)."""
    cells, fits = {}, 0
    keep = set(leads)
    sub = [r for r in rows_all if r[3] in keep]
    for label, t0, t1 in FOLDS:
        train = {(h, n): [] for h in CYCLE_HOURS for n in leads}
        test = {(h, n): [] for h in CYCLE_HOURS for n in leads}
        extra = {(h, n): [] for h in CYCLE_HOURS for n in leads}
        for cycle, valid, h, n, complete, obs, temp, x in sub:
            role = fold_role(cycle, valid, t0, t1)
            if complete:
                if role == "train":
                    if not valid < t0:
                        raise SystemExit("STOP: a training row is not before T0")
                    train[(h, n)].append((cycle, x, temp, obs))
                elif role == "test":
                    test[(h, n)].append((cycle, x, temp, obs))
            elif obs is None and all(v is not None for v in x) and role == "test":
                extra[(h, n)].append((cycle, x, temp, None))
        for d in (train, test, extra):
            for k in d:
                d[k].sort(key=lambda r: r[0])
        for h in CYCLE_HOURS:
            for n in leads:
                tr, te, ex = train[(h, n)], test[(h, n)], extra[(h, n)]
                if not tr or not te:
                    raise SystemExit(f"STOP: {label} {h}z lead {n}: train {len(tr)}, test {len(te)}")
                if tr[-1][0] >= te[0][0] or max(r[0] for r in tr) + dt.timedelta(hours=n) >= t0:
                    raise SystemExit(f"STOP: {label} {h}z lead {n}: training not before test")
                t = time.time()
                fc = baseline.fit_predict([(r[1], r[2], r[3]) for r in tr],
                                          [(r[1], r[2], r[3]) for r in te] + [(r[1], r[2], r[3]) for r in ex])
                timer["fit"] += time.time() - t
                fits += 1
                base, xbase = fc[:len(te)], fc[len(te):]
                corr, n_used, x_corr = correct([(r[0], r[3], base[i]) for i, r in enumerate(te)],
                                               [(r[0], xbase[i]) for i, r in enumerate(ex)], n)
                cells[(label, h, n)] = {
                    "cycles": [r[0] for r in te], "obs": [r[3] for r in te], "raw": [r[2] for r in te],
                    "baseline": base, "curve": corr, "n_used": n_used,
                    "x_cycles": [r[0] for r in ex], "x_raw": [r[2] for r in ex], "x_baseline": xbase, "x_curve": x_corr}
    return cells, fits


def pooled(errs, meth, st, leads, folds=None):
    e = []
    for label, _, _ in FOLDS:
        if folds and label not in folds:
            continue
        for h in CYCLE_HOURS:
            for n in leads:
                e.extend(errs[(st, label, h, n, meth)])
    return mae(e), len(e), mean_error(e)


def fold_of(c):
    for label, t0, t1 in FOLDS:
        if t0 <= c < t1:
            return label
    return None


def daily_rows(st, tzname, obs_by_valid, fc):
    """One airport's days (D98.10, as the record's daily_max), with the package's local_day, usable_day
    and day_cycle. fc: {(cycle, lead): {method: forecast}}."""
    rows, drops = [], {}
    d = FOLDS[0][1].date() - dt.timedelta(days=1)
    while d <= FOLDS[-1][2].date():
        s, e, hours = dailymax.local_day(d, tzname)
        c = dailymax.day_cycle(s)
        label = fold_of(c)
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
        usable = [obs_by_valid[h] for h in hours if obs_by_valid[h] is not None]
        obs_ok = dailymax.usable_day(len(hours), len(usable))
        row = {"station": st, "fold": label, "local_date": d.isoformat(), "hours": len(hours),
               "usable_hours": len(usable), "obs_max": max(usable) if obs_ok else None,
               "obs_reason": "" if obs_ok else "too few usable hours", "cycle": c, "first_lead": leads[0],
               "last_lead": leads[-1]}
        for m in METHODS:
            curve = {h: fc.get((c, int((h - c) / dt.timedelta(hours=1))), {}).get(m) for h in hours}
            mx = dailymax.read_off(hours, curve)
            row[m] = mx
            row[m + "_reason"] = "" if mx is not None else \
                f"no forecast at {sum(v is None for v in curve.values())} hours"
        row["common"] = row["obs_max"] is not None and all(row[m] is not None for m in METHODS)
        rows.append(row)
        d += dt.timedelta(days=1)
    return rows, drops


def run_gate_b(args):
    t_start = time.time()
    print(f"SESSION 109 --gate-b (offline), {now_utc()}: the package reproduces F147's curve and daily-maximum scores")
    print(f"LGB_PARAMS: {baseline.LGB_PARAMS}; w = {tracker.W}")
    print("BUILD-CHOICE REPRODUCTION (SPEC 2.5); the claim look is not run (D101.2). Rows valid before 2026-08-01 only.")
    for a in DEV:
        for hs in HOURSETS:
            got, want = sha256_file(STAGEC / table_name(a, hs)), recorded_sha(a, hs)
            if got != want:
                raise SystemExit(f"STOP: {table_name(a, hs)} SHA-256 {got} is not the recorded {want}")
    print("the twelve development table files: SHA-256 equal to the record")
    timer = {"fit": 0.0}
    cells, fits = {}, 0
    obs_maps, fcs = {}, {}
    for a in DEV:
        t = time.time()
        rows_a = tables.read_table_rows(STAGEC / table_name(a, "f000_024"), a.station)
        rows_b = tables.read_table_rows(STAGEC / table_name(a, "f025_048"), a.station)
        for r in rows_a + rows_b:
            if r[1] > DAY_LAST_VALID:
                raise SystemExit("STOP: a row valid after 2026-07-31T23:00")
        ca, fa = score_airport(rows_a, LEADS_A, timer)
        cb, fb = score_airport(rows_b, LEADS_B, timer)
        fits += fa + fb
        for k, v in list(ca.items()) + list(cb.items()):
            cells[(a.station,) + k] = v
        obs_map, fc = {}, {}
        for cycle, valid, h, n, complete, obs, temp, x in rows_a + rows_b:
            if valid in obs_map and obs_map[valid] != obs:
                raise SystemExit(f"STOP: {a.station}: two observations for {valid}")
            obs_map[valid] = obs
            if temp is not None:
                fc.setdefault((cycle, n), {})["raw_gfs"] = temp
        obs_maps[a.station], fcs[a.station] = obs_map, fc
        print(f"  {a.station}: {fa + fb} fits, {time.time() - t:.1f} s", flush=True)
    for (st, label, h, n), c in cells.items():
        for pre in ("", "x_"):
            for i, cy in enumerate(c[pre + "cycles"]):
                d = fcs[st].setdefault((cy, n), {})
                d["baseline"] = c[pre + "baseline"][i]
                d["curve"] = c[pre + "curve"][i]
    stations = [a.station for a in DEV]
    print(f"fits {fits} (expected 3,312); fit time {timer['fit']:.1f} s")

    errs = {}
    for (st, label, h, n), c in cells.items():
        for m in METHODS:
            fc_ = c["raw"] if m == "raw_gfs" else c[m]
            errs[(st, label, h, n, m)] = [o - fc_[i] for i, o in enumerate(c["obs"])]
    out = []
    for m in METHODS:
        for st in stations:
            for label, _, _ in FOLDS:
                for h in CYCLE_HOURS:
                    for n in LEADS_ALL:
                        e = errs[(st, label, h, n, m)]
                        out.append([st, label, h, n, m, len(e), mae(e), mean_error(e), m])
    header = ["station", "fold", "cycle_hour", "lead", "method", "n", "mae", "mean_error", "model"]
    text = csv_text(header, [[fmt(v) for v in r] for r in out])
    sha_scores = hashlib.sha256(text.encode()).hexdigest()
    rec = {}
    with open(PROCESSED / "session104_curve_cv_scores.csv", newline="") as f:
        for r in csv.DictReader(f):
            rec[(r["station"], r["fold"], int(r["cycle_hour"]), int(r["lead"]), r["method"])] = (r["n"], r["mae"], r["mean_error"])
    if sha256_file(PROCESSED / "session104_curve_cv_scores.csv") != F147_SCORES_SHA256:
        raise SystemExit("STOP: the committed scores file is not F147.7's")
    eq = sum(1 for r in out if rec.get((r[0], r[1], r[2], r[3], r[4])) == (fmt(r[5]), fmt(r[6]), fmt(r[7])))
    print(f"\nhourly cells (3 to 48; raw GFS, baseline, curve): n, MAE and mean error equal to the recorded file "
          f"{eq} of {len(out)}; the scores text's SHA-256 {sha_scores}; recorded {F147_SCORES_SHA256}; equal "
          f"{sha_scores == F147_SCORES_SHA256}")

    print("\nHourly, MAE at 4 decimals, leads 3 to 48 (raw GFS / baseline / curve), against F147.5:")
    ok_hour = True
    heads = {m: 0.0 for m in METHODS}
    for st in stations:
        vals = tuple(pooled(errs, m, st, LEADS_ALL)[0] for m in METHODS)
        for m, v in zip(METHODS, vals):
            heads[m] += v / len(stations)
        want = F147_HOURLY_3_48[st]
        good = tuple(round(v, 4) for v in vals) == want
        ok_hour &= good
        print(f"  {st}: " + " / ".join(f"{v:.4f}" for v in vals) + f"   F147.5 {want}   equal {good}")
    hv = tuple(sum(pooled(errs, m, st, LEADS_ALL)[0] for st in stations) / len(stations) for m in METHODS)
    good = tuple(round(v, 4) for v in hv) == F147_HOURLY_3_48["headline"]
    ok_hour &= good
    print(f"  headline: " + " / ".join(f"{v:.4f}" for v in hv) + f"   F147.5 {F147_HOURLY_3_48['headline']}   equal {good}")
    print(f"  curve headline, full precision: {hv[2]!r}; F147.5 {F147_CURVE_HEADLINE_3_48!r}; equal {hv[2] == F147_CURVE_HEADLINE_3_48}")
    ok_hour &= hv[2] == F147_CURVE_HEADLINE_3_48

    # daily maximum
    all_days, drops_all = [], {}
    for a in DEV:
        rows, drops = daily_rows(a.station, a.time_zone, obs_maps[a.station], fcs[a.station])
        all_days += rows
        drops_all[a.station] = drops
    cols = ["station", "fold", "local_date", "hours", "usable_hours", "obs_max", "obs_reason", "cycle",
            "first_lead", "last_lead"] + [x for m in METHODS for x in (m + "_max", m + "_reason")] + ["common"]
    drows = []
    for r in all_days:
        drows.append([r["station"], r["fold"], r["local_date"], r["hours"], r["usable_hours"],
                      "" if r["obs_max"] is None else fmt(r["obs_max"]), r["obs_reason"],
                      r["cycle"].strftime("%Y-%m-%dT%H:%MZ"), r["first_lead"], r["last_lead"]]
                     + [x for m in METHODS for x in ("" if r[m] is None else fmt(r[m]), r[m + "_reason"])]
                     + ["true" if r["common"] else "false"])
    dtext = csv_text(cols, drows)
    sha_days = hashlib.sha256(dtext.encode()).hexdigest()
    if sha256_file(PROCESSED / "session104_dailymax_days.csv") != F147_DAYS_SHA256:
        raise SystemExit("STOP: the committed days file is not F147.7's")
    with open(PROCESSED / "session104_dailymax_days.csv", newline="") as f:
        rec_days = [r for r in csv.reader(f)][1:]
    eq_days = sum(1 for a_, b_ in zip(drows, rec_days) if [str(x) for x in a_] == b_)
    print(f"\ndays: {len(drows)} (recorded {len(rec_days)}); every field equal to the recorded file {eq_days} of {len(rec_days)}; "
          f"the days text's SHA-256 {sha_days}; recorded {F147_DAYS_SHA256}; equal {sha_days == F147_DAYS_SHA256}")

    def dmae(st, m):
        e = [r["obs_max"] - r[m] for r in all_days if r["station"] == st and r["common"]]
        return mae(e), len(e), mean_error(e)

    print("\nDaily maximum, common day set, MAE at 4 decimals (raw GFS / baseline / curve), against F147.6:")
    ok_day = True
    for st in stations:
        vals = tuple(dmae(st, m)[0] for m in METHODS)
        n_days = dmae(st, "baseline")[1]
        want = F147_DAILY[st]
        good = tuple(round(v, 4) for v in vals) == want and n_days == F147_DAYS_N[st]
        ok_day &= good
        print(f"  {st}: days {n_days} (F147.6 {F147_DAYS_N[st]}) " + " / ".join(f"{v:.4f}" for v in vals)
              + f"   F147.6 {want}   equal {good}")
    dh = tuple(sum(dmae(st, m)[0] for st in stations) / len(stations) for m in METHODS)
    good = tuple(round(v, 4) for v in dh) == F147_DAILY["headline"]
    ok_day &= good
    print(f"  headline: " + " / ".join(f"{v:.4f}" for v in dh) + f"   F147.6 {F147_DAILY['headline']}   equal {good}")
    print("  full precision: " + ", ".join(f"{m} {v!r}" for m, v in zip(METHODS, dh)))

    all_ok = (eq == len(out) == len(rec) == 9936 and sha_scores == F147_SCORES_SHA256 and ok_hour
              and eq_days == len(rec_days) == len(drows) == 6570 and sha_days == F147_DAYS_SHA256 and ok_day
              and fits == 3312)
    print(f"\nrun time {time.time() - t_start:.1f} s")
    print("GATE B: PASS" if all_ok else "GATE B: FAIL")
    return 0 if all_ok else 1


# ------------------------------------------------------------------ Gate C (network: the AWS GFS archive only)

# Three cycles from inside the pull window (D83.5(b)), one each from 2021, 2023 and July 2026, with the
# cycle hour chosen here (session 109, Step 5). None is among the 27 files of 2022-11 that needed the
# whole-file fallback (F135, D86.2).
GATE_C_CYCLES = [dt.datetime(2021, 9, 15, 18), dt.datetime(2023, 3, 8, 6), dt.datetime(2026, 7, 14, 12)]


def pull_rows_for(cycle):
    """The recorded extract's rows for one cycle: ({(fh, icao): row}, {(fh, field): status}) from both pulls."""
    month = f"{cycle.year}-{cycle.month:02d}"
    icaos = {a.icao for a in AIRPORTS}
    rows, stat = {}, {}
    col_i = {c: i for i, c in enumerate(POINT_COLS)}
    for d in (PULL_00, PULL_25):
        status, points = read_pull_month(d, month, icaos)
        c_iso = tables.iso(cycle)
        for (c, fh, ic), r in points.items():
            if c == c_iso:
                rows[(fh, ic)] = {f: [float(r[col_i[f"{f}_{k}"]]) if r[col_i[f"{f}_{k}"]] != "" else None for k in (1, 2, 3, 4)]
                                  for f in FIELD_NAMES}
        for (c, fh, f), s in status.items():
            if c == c_iso:
                stat[(fh, f)] = s
    return rows, stat


def synthetic_guard_demo():
    """Step 5's offline guard test: a synthetic GFS-shaped message passes the guard, and the same message
    with one key altered stops it. Returns (passed, [(key, stopped)])."""
    import eccodes as ec
    field = next(f for f in MODEL.fields if f.name == "t2m")
    cycle = dt.datetime(2026, 10, 12, 6)

    def message(tweak=None):
        gid = ec.codes_grib_new_from_samples("regular_ll_sfc_grib2")
        try:
            for k, v in (("Ni", 1440), ("Nj", 721), ("latitudeOfFirstGridPointInDegrees", 90.0),
                         ("longitudeOfFirstGridPointInDegrees", 0.0), ("latitudeOfLastGridPointInDegrees", -90.0),
                         ("longitudeOfLastGridPointInDegrees", 359.75), ("iDirectionIncrementInDegrees", 0.25),
                         ("jDirectionIncrementInDegrees", 0.25), ("discipline", field.ident[0]),
                         ("dataDate", int(f"{cycle:%Y%m%d}")), ("dataTime", cycle.hour * 100),
                         ("productDefinitionTemplateNumber", 0), ("parameterCategory", field.ident[1]),
                         ("parameterNumber", field.ident[2]), ("typeOfFirstFixedSurface", field.ident[3]),
                         ("scaleFactorOfFirstFixedSurface", 0), ("scaledValueOfFirstFixedSurface", field.ident[4]),
                         ("stepUnits", 1), ("forecastTime", 5)):
                ec.codes_set(gid, k, v)
            if tweak:
                tweak(gid)
            ec.codes_set_values(gid, np.full(1440 * 721, 280.0))
            return ec.codes_get_message(gid)
        finally:
            ec.codes_release(gid)

    def run(tweak=None):
        gid = ec.codes_new_from_message(message(tweak))
        try:
            return gfs.check_message(gid, field, 5, cycle, AIRPORTS, MODEL.grid)
        finally:
            ec.codes_release(gid)

    good = len(run()) == 4 * len(AIRPORTS)
    results = []
    for key, val in (("parameterNumber", 1), ("typeOfFirstFixedSurface", 1), ("dataTime", 1200), ("Ni", 720),
                     ("forecastTime", 6)):
        try:
            run(lambda g, key=key, val=val: ec.codes_set(g, key, val))
            results.append((f"{key}={val}", False))
        except gfs.GuardStop:
            results.append((f"{key}={val}", True))
    return good, results


def run_gate_c(args):
    t0 = time.time()
    print(f"SESSION 109 --gate-c (network: the AWS GFS archive only), {now_utc()}")
    good, demo = synthetic_guard_demo()
    print(f"offline guard test (synthetic message): unaltered message passes {good}; altered key stops: "
          + ", ".join(f"{k} {'STOPPED' if s else 'NOT STOPPED'}" for k, s in demo))
    if not good or not all(s for _, s in demo):
        raise SystemExit("STOP: the guard did not behave")
    print("cycles (chosen by the session): " + ", ".join(f"{c:%Y-%m-%d %Hz}" for c in GATE_C_CYCLES))
    live_fields = [f.name for f in MODEL.live_fields()]
    all_ok = True
    for cycle in GATE_C_CYCLES:
        rows, stat = pull_rows_for(cycle)
        http = gfs.Http()
        t = time.time()
        cv = gfs.fetch_cycle(MODEL, AIRPORTS, cycle, http=http, workers=8)
        n_cmp = n_bad = n_missing = 0
        status_bad = 0
        for fh in range(0, 49):
            for f in live_fields:
                s_live, s_pull = cv.status[(fh, f)], stat[(fh, f)]
                if s_live != ("ok" if s_pull in OK_STATUSES else s_pull):
                    status_bad += 1
                if s_live != "ok":
                    continue
                for a in AIRPORTS:
                    pulled = rows[(fh, a.icao)][f]
                    live = cv.point_values(a.icao, fh, f)
                    if None in pulled:
                        n_missing += 1
                        continue
                    for lv, pv in zip(live, pulled):
                        n_cmp += 1
                        n_bad += lv != pv
        ok = n_bad == 0 and n_missing == 0 and status_bad == 0 and n_cmp > 0
        all_ok &= ok
        print(f"  {cycle:%Y-%m-%d %Hz}: files 49, requests {http.requests}, bytes {http.bytes:,}, {time.time() - t:.0f} s; "
              f"values compared {n_cmp:,} (49 hours x fields x 12 airports x 4 points); not equal {n_bad}; "
              f"pull cell empty {n_missing}; status differences {status_bad}; {'EQUAL' if ok else 'NOT EQUAL'}")
    print(f"run time {time.time() - t0:.0f} s")
    print("GATE C: PASS" if all_ok else "GATE C: FAIL")
    return 0 if all_ok else 1


# ------------------------------------------------------------------ Gate D (network: IEM only)

GATE_D_MONTH = (2023, 6)       # inside the training window


def ambiguous_times(text):
    """Timestamps with two or more rows whose values differ (one missing counts as different)."""
    by = {}
    for r in csv.DictReader(io.StringIO(text)):
        v = (r.get("tmpc") or "").strip()
        by.setdefault(dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M"), []).append("M" if v in ("", "T", "None") else v)
    return {t for t, v in by.items() if len(set(v)) > 1}


def run_gate_d(args):
    t0 = time.time()
    y, m = GATE_D_MONTH
    first, last = dt.date(y, m, 1), (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1))
    # Owner's ruling 1 at the Step 6 stop: the request starts one day earlier; only the hours of the month are compared.
    req_first = first - dt.timedelta(days=1)
    print(f"SESSION 109 --gate-d (network: IEM only), {now_utc()}: request {req_first} to {last}, compare the hours of "
          f"{first} to {last}, for the 12 airports; live pairing (repeated timestamps with different values ignored)")
    month_start = dt.datetime(y, m, 1)
    month_end = dt.datetime(last.year, last.month, last.day, 23)
    equal_total = hours_total = design_total = other_total = 0
    for a in AIRPORTS:
        text = observations.fetch_reports(a.station, req_first, last)
        live = observations.ReportSet.from_text(text, a.station, live=True)
        # the committed file of the year, restricted to the month, in the same CSV form
        committed_text = (RAW / f"iem_asos_{a.station}_{y}-01-01_{y}-12-31_routine.csv").read_text()
        committed_all = observations.ReportSet.from_text(committed_text, a.station)       # the record's pairing
        live_rows = {tuple(r.values()) for r in csv.DictReader(io.StringIO(text))
                     if first <= dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M").date() <= last}
        com_rows = {tuple(r.values()) for r in csv.DictReader(io.StringIO(committed_text))
                    if first <= dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M").date() <= last}
        only_live, only_com = live_rows - com_rows, com_rows - live_rows
        by_valid_live = {r[1]: r for r in live_rows}
        differing = sum(1 for r in only_com if r[1] in by_valid_live)
        # the pairing, hour by hour, over the whole month
        hours = [month_start + dt.timedelta(hours=k) for k in range(int((month_end - month_start) / dt.timedelta(hours=1)) + 1)]
        diff_h = [h for h in hours if live.nearest(h) != committed_all.nearest(h)]
        # by design (ruling 2): the record's pairing used a report whose timestamp is repeated with different values
        amb = ambiguous_times(text)
        by_design = [h for h in diff_h if committed_all.nearest(h)[1] in amb]
        other = [h for h in diff_h if h not in by_design]
        paired = sum(1 for h in hours if committed_all.nearest(h)[0] is not None)
        equal_total += len(hours) - len(diff_h)
        hours_total += len(hours)
        design_total += len(by_design)
        other_total += len(other)
        print(f"  {a.station}: raw rows live {len(live_rows)}, committed (same days) {len(com_rows)}; only in live {len(only_live)}, "
              f"only in committed {len(only_com)} (same time, different row {differing}); pairing over {len(hours)} hours "
              f"({paired} paired in the committed file): differing {len(diff_h)}, of which by design {len(by_design)}"
              + (f" at {[f'{h:%m-%d %H}' for h in by_design]}" if by_design else "")
              + (f"; OTHER {[f'{h:%m-%d %H}' for h in other[:5]]}" if other else "")
              + f"; repeated timestamps ignored in the request window: {live.stats['ambiguous']}")
    print(f"pairing equal at {equal_total} of {hours_total} hour-airport cases; differing by design (ruling 2) {design_total}; "
          f"differing for any other reason {other_total}")
    all_ok = other_total == 0
    print(f"run time {time.time() - t0:.0f} s")
    print("GATE D (pairing): PASS" if all_ok else "GATE D (pairing): FAIL")
    return 0 if all_ok else 1


# ------------------------------------------------------------------ entry point

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for name in ("gate-a", "trial", "gate-b", "gate-c", "gate-d"):
        g.add_argument("--" + name, action="store_true")
    a = ap.parse_args()
    if a.trial:
        return run_trial(a)
    if a.gate_a:
        return run_gate_a(a)
    if a.gate_b:
        return run_gate_b(a)
    if a.gate_c:
        return run_gate_c(a)
    return run_gate_d(a)


if __name__ == "__main__":
    sys.exit(main())
