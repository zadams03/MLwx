"""The onboarding tool (DECISIONS D104.6, D104.7): adds an airport of D83.2's 51 to the product.

For each airport named, it:

  0. refuses it, before any of its data is opened, unless its time zone is a whole number of hours
     from UTC on every day from 2021-03-01 to 2027-12-31 (owner's ruling at session 110's Step 4
     stop, F153: the daily maximum is read off whole hours, dailymax.local_day);
  1. makes its row of data/gfs_airports.csv (D104.6): station as the IEM id, the position used and
     its four grid points and weights from data/processed/session91_pull_airports.csv (D83.3), the
     time zone from data/processed/session90_airports.csv, and the elevation constant
     round(7.429 x height_diff_m / 1000, 4) from the same file (D100.3(b));
  2. builds its two tables (hours 0 to 24 and 25 to 48) from the pull's extracts (MLwx-pull/,
     MLwx-pull-f025-048/) and the saved IEM files (data/raw/), with the package's own code
     (features, observations, tables), as Gate A of session 109 did (scripts/session109_gates.py,
     build_tables, ported);
  3. counts the complete-case rows of each of its 184 model cells (4 cycle hours x leads 3 to 48),
     all valid up to 2026-07-31; counts only, no value is summarised;
  4. only if every cell has at least 1,200 rows (D104.7), fits its four model files by D103.5
     unchanged (baseline.fit, baseline.pack_bytes, as refit.py).

No error, MAE or mean error is computed (D104.8). Nothing is written over: tables and model files
are written once (tables.write_new_file). The six development airports are not onboarded: they are
in the product already, with SPEC 3.4's grid points and their own constants.

    python -m mlwx.onboard row ICAO ...                       # print the generated rows
    python -m mlwx.onboard tables --out DIR ICAO ...          # build the tables (and DIR/manifest.txt)
    python -m mlwx.onboard counts --tables DIR [--csv F] ICAO ...
    python -m mlwx.onboard counts --current                   # the 12 current airports' stage C tables
    python -m mlwx.onboard fit --tables DIR --out DIR [--jobs N] ICAO ...
    python -m mlwx.onboard run --tables DIR --out DIR ICAO ...  # all four steps, one airport after another
    python -m mlwx.onboard add-rows ICAO ...                  # append the rows to data/gfs_airports.csv
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
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

from . import baseline, config, features, observations, records, refit, tables

ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"
PULL_00 = ROOT.parent / "MLwx-pull"
PULL_25 = ROOT.parent / "MLwx-pull-f025-048"
STAGEC = ROOT.parent / "MLwx-stagec"
POSITIONS = PROCESSED / "session91_pull_airports.csv"
AIRPORTS_90 = PROCESSED / "session90_airports.csv"
INVENTORIES = {"f000_024": ("session95_pull_inventory.csv", None),
               "f025_048": ("session104_pull_f025_048_inventory.csv",
                            "5b6cd6f99dcadd0df5bbc313988514495d906126738df6f45944e2ce9208f9d1")}   # F147.2

MODEL = config.GFS
MIN_ROWS = 1200                       # D104.7: every model cell needs at least this many complete-case rows
LAPSE_C_PER_KM = 7.429                # SPEC 7.2, D100.3(b)
ROLES = {"claim batch": "claim", "new": "new"}   # the pull's role -> the airports file's (development: refused)
TABLE_MANIFEST = "manifest.txt"
TZ_FIRST_DAY, TZ_LAST_DAY = dt.date(2021, 3, 1), dt.date(2027, 12, 31)   # the time-zone rule's days (F153)

# The window of the pull (D83.5(b)) and its plan (session 91's plan_chunk), as scripts/session109_gates.py.
FIRST_VALID = dt.datetime(2021, 3, 24, 0)
LAST_VALID = dt.datetime(2026, 7, 31, 23)
LAST_OBS = dt.datetime(2026, 7, 31, 23, 59)
FIRST_MONTH, LAST_MONTH = (2021, 3), (2026, 7)
HOURSETS = {"f000_024": (0, 24), "f025_048": (25, 48)}
OBS_PIECES = ["2021-03-24_2021-12-31", "2022-01-01_2022-12-31", "2023-01-01_2023-12-31",
              "2024-01-01_2024-12-31", "2025-01-01_2025-12-31", "2026-01-01_2026-07-31"]
STATUS_WHOLE = "ok (whole file)"
MAN_COLS = ["cycle_utc", "fhour", "field", "idx_line", "byte_range", "bytes", "status", "step_range",
            "process_type", "reason"]
FIELD_NAMES = [f.name for f in MODEL.fields]
POINT_COLS = ["cycle_utc", "fhour", "valid_utc", "icao"] + [f"{n}_{k}" for n in FIELD_NAMES for k in (1, 2, 3, 4)]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_csv(path, key):
    with open(path, newline="") as f:
        return {r[key]: r for r in csv.DictReader(f)}


# ------------------------------------------------------------------ 1. the airports file row

def airport_columns():
    with open(config.DATA / MODEL.airports_file, newline="") as f:
        return next(csv.reader(f))


def resolve(name):
    """An ICAO code or IEM id of the pull's 51 airports -> its ICAO code."""
    pos = read_csv(POSITIONS, "icao")
    if name in pos:
        return name
    hits = [ic for ic, r in pos.items() if r["iem_id"] == name]
    if len(hits) != 1:
        raise SystemExit(f"STOP: {name} is not one of the pull's {len(pos)} airports")
    return hits[0]


def whole_hour_zone(tzname, first=TZ_FIRST_DAY, last=TZ_LAST_DAY):
    """True if the zone is a whole number of hours from UTC at every UTC hour of every day first..last
    (so every local day starts and ends on a whole UTC hour). Reads no data."""
    tz = ZoneInfo(tzname)
    t = dt.datetime(first.year, first.month, first.day, tzinfo=dt.timezone.utc) - dt.timedelta(days=1)
    end = dt.datetime(last.year, last.month, last.day, tzinfo=dt.timezone.utc) + dt.timedelta(days=2)
    while t < end:
        if t.astimezone(tz).utcoffset().total_seconds() % 3600:
            return False
        t += dt.timedelta(hours=1)
    return True


def time_zone_of(name):
    """The airport's time zone, from session90_airports.csv."""
    icao = resolve(name)
    a90 = read_csv(AIRPORTS_90, "icao")
    if icao not in a90:
        raise SystemExit(f"STOP: {icao} is not in session90_airports.csv")
    return a90[icao]["time_zone"]


def check_time_zone(name):
    """The owner's time-zone rule (F153), applied before any of the airport's data is opened."""
    tzname = time_zone_of(name)
    if not whole_hour_zone(tzname):
        raise SystemExit(f"STOP: {resolve(name)} is left out: its time zone {tzname} is not a whole number of hours "
                         f"from UTC on every day from {TZ_FIRST_DAY} to {TZ_LAST_DAY}")


def airport_row(name):
    """The airport's row of gfs_airports.csv as a list of strings, in the file's column order (D104.6)."""
    icao = resolve(name)
    p = read_csv(POSITIONS, "icao")[icao]
    a90 = read_csv(AIRPORTS_90, "icao")
    if p["role"] not in ROLES:
        raise SystemExit(f"STOP: {icao} is a {p['role']} airport; only claim-batch and new airports are onboarded")
    if icao not in a90 or a90[icao]["iem_id"] != p["iem_id"]:
        raise SystemExit(f"STOP: {icao} is not in session90_airports.csv with the same IEM id")
    check_time_zone(icao)
    r90 = a90[icao]
    corr = round(LAPSE_C_PER_KM * float(r90["height_diff_m"]) / 1000.0, 4)
    vals = {"station": p["iem_id"], "icao": icao, "role": ROLES[p["role"]], "time_zone": r90["time_zone"],
            "lat": p["lat_used"], "lon": p["lon_used"], "correction_c": repr(corr)}
    for k in (1, 2, 3, 4):
        for c in ("index", "lat", "lon", "weight"):
            vals[f"p{k}_{c}"] = p[f"p{k}_{c}"]
    cols = airport_columns()
    if set(cols) != set(vals):
        raise SystemExit("STOP: the airports file's columns are not the ones the tool fills")
    for v in vals.values():
        if "," in v or '"' in v or v == "":
            raise SystemExit(f"STOP: {icao}: a value that needs quoting or is empty: {v!r}")
    return [vals[c] for c in cols]


def row_line(name):
    return ",".join(airport_row(name))


def airport_of(name):
    """The config.Airport the tool makes for this airport (the row read the way config.load_airports reads it)."""
    r = dict(zip(airport_columns(), airport_row(name)))
    return config.Airport(
        station=r["station"], icao=r["icao"], role=r["role"], time_zone=r["time_zone"],
        lat=float(r["lat"]), lon=float(r["lon"]), correction_c=float(r["correction_c"]),
        indices=tuple(int(r[f"p{k}_index"]) for k in (1, 2, 3, 4)),
        points=tuple((float(r[f"p{k}_lat"]), float(r[f"p{k}_lon"])) for k in (1, 2, 3, 4)),
        weights=tuple(float(r[f"p{k}_weight"]) for k in (1, 2, 3, 4)))


def add_rows(names, path=None):
    """Append the airports' rows to gfs_airports.csv. The existing bytes are kept as they are; an airport
    already in the file is refused."""
    path = Path(path or config.DATA / MODEL.airports_file)
    before = path.read_bytes()
    if not before.endswith(b"\n"):
        raise SystemExit(f"STOP: {path} does not end with a newline")
    have = {r["icao"] for r in csv.DictReader(io.StringIO(before.decode("ascii")))}
    lines = []
    for n in names:
        icao = resolve(n)
        if icao in have:
            raise SystemExit(f"STOP: {icao} is already in {path.name}")
        have.add(icao)
        lines.append(row_line(icao) + "\n")
    with open(path, "ab") as f:
        f.write("".join(lines).encode("ascii"))
    if path.read_bytes()[:len(before)] != before:
        raise SystemExit(f"STOP: the existing rows of {path.name} changed")
    return len(lines)


# ------------------------------------------------------------------ 2. the tables

def table_name(icao, hour_set):
    return f"onboard_{hour_set}_{icao}.csv.gz"


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
        if c < MODEL.first_cycle:
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


def check_pull(hour_set, pull_00=PULL_00, pull_25=PULL_25, log=print):
    """The pull folders this hour set reads, each file against its inventory (bytes and SHA-256)."""
    dirs = [("f000_024", pull_00)] + ([("f025_048", pull_25)] if hour_set == "f025_048" else [])
    for hs, d in dirs:
        name, want = INVENTORIES[hs]
        rows = list(csv.DictReader(open(PROCESSED / name, newline="")))
        have = sorted(p.name for p in Path(d).iterdir())
        bad = [r["asset"] for r in rows if (Path(d) / r["asset"]).stat().st_size != int(r["bytes"])
               or tables.sha256_file(Path(d) / r["asset"]) != r["sha256"]]
        if bad or have != sorted(r["asset"] for r in rows) or (want and tables.sha256_file(PROCESSED / name) != want):
            raise SystemExit(f"STOP: a file of {Path(d).name} differs from its inventory {name}")
        log(f"  pull folder {Path(d).name}: {len(have)} files equal to {name} (bytes and SHA-256)")


def read_pull_month(d, month, icaos):
    """The manifest statuses and the kept airports' points rows of one month."""
    with gzip.open(Path(d) / f"manifest_{month}.csv.gz", "rt", newline="") as f:
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
    with gzip.open(Path(d) / f"gfs_points_{month}.csv.gz", "rt", newline="") as f:
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
            if s in features.OK_STATUSES:
                v4 = [float(x) for x in cells]
                if not all(math.isfinite(x) for x in v4):
                    raise SystemExit(f"STOP: non-finite stored value at {c_iso} f{fh:03d} {fname}")
                val[(fh, fname)] = features.bilinear_stored(a.point_list, a.lat, a.lon, v4)
            elif any(x != "" for x in cells):
                raise SystemExit(f"STOP: a filled cell in a non-ok message at {c_iso} f{fh:03d} {fname}")


def obs_files(a):
    return [RAW / f"iem_asos_{a.station}_{piece}_routine.csv" for piece in OBS_PIECES]


def recorded_obs_sha(path):
    """The SHA-256 written in the file's .meta.txt."""
    meta = Path(str(path) + ".meta.txt").read_text()
    hits = [ln.split(":", 1)[1].strip() for ln in meta.splitlines() if ln.startswith("sha256")]
    if len(hits) != 1:
        raise SystemExit(f"STOP: {path.name}.meta.txt has {len(hits)} sha256 lines")
    return hits[0]


def load_reports(a):
    """The six yearly routine files of one airport as one ReportSet, each checked against its .meta.txt
    first. Every report's time is checked against the limit before any temperature is read."""
    stats = observations.new_stats()
    reports = []
    for path in obs_files(a):
        if tables.sha256_file(path) != recorded_obs_sha(path):
            raise SystemExit(f"STOP: {path.name} SHA-256 differs from its .meta.txt")
        text = path.read_text()
        for r in csv.DictReader(io.StringIO(text)):
            if dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M") > LAST_OBS:
                raise SystemExit(f"STOP: an observation after {LAST_OBS} in {path.name}")
        reports += observations.parse_reports(text, a.station, stats)
    return observations.ReportSet(reports, stats)


def build_lines(hour_set, airports, months=None, pull_00=PULL_00, pull_25=PULL_25, log=print):
    """Rows of every airport's table for one hour set, as the package builds them (Gate A's build_tables).
    Returns ({icao: lines}, {icao: observation stats}, rows in the plan per airport)."""
    hours = HOURSETS[hour_set]
    main_dir, prior_dir = (pull_00, None) if hour_set == "f000_024" else (pull_25, pull_00)
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
        log(f"  {hour_set} {month}: {len(plan)} cycles, {sum(len(f) for _, f in plan)} rows per airport ({now_utc()})")
    for a in airports:
        if len(lines[a.icao]) - 1 != expected:
            raise SystemExit(f"STOP: {a.icao} has {len(lines[a.icao]) - 1} rows, the plan {expected}")
    return lines, {a.icao: reports[a.icao].stats for a in airports}, expected


def build_tables(names, out_dir, pull_00=PULL_00, pull_25=PULL_25, log=print):
    """Build and write both tables of each airport into out_dir (created if needed; no file is written
    over) and add them to out_dir/manifest.txt. Returns {(icao, hour set): (rows, bytes, sha256)}."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    airports = [airport_of(n) for n in names]
    for a in airports:
        for hs in HOURSETS:
            if (out / table_name(a.icao, hs)).exists():
                raise SystemExit(f"STOP: {out / table_name(a.icao, hs)} already exists")
    got = {}
    for hs in HOURSETS:
        check_pull(hs, pull_00, pull_25, log)
        lines, ostats, n_plan = build_lines(hs, airports, pull_00=pull_00, pull_25=pull_25, log=log)
        for a in airports:
            data = tables.table_bytes(lines[a.icao])
            path = out / table_name(a.icao, hs)
            tables.write_new_file(path, data)
            got[(a.icao, hs)] = (len(lines[a.icao]) - 1, len(data), tables.sha256_bytes(data))
            s = ostats[a.icao]
            log(f"  {path.name}: rows {len(lines[a.icao]) - 1} (plan {n_plan}), bytes {len(data):,}, "
                f"SHA-256 {got[(a.icao, hs)][2]}; observations: reports {s['rows']}, no usable tmpc {s['no_temp']}, "
                f"repeated timestamps {s['duplicates']}, ties {s['ties']}")
        del lines
    add_to_manifest(out, {table_name(i, hs): v[2] for (i, hs), v in got.items()})
    return got


def add_to_manifest(folder, entries):
    """Add (file, SHA-256) lines to folder/manifest.txt, sorted by name; an existing line is never changed."""
    path = Path(folder) / TABLE_MANIFEST
    have = read_manifest(path) if path.exists() else {}
    for name, sha in entries.items():
        if name in have and have[name] != sha:
            raise SystemExit(f"STOP: {name} is in {path} with another SHA-256")
        have[name] = sha
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(baseline.manifest_text(have))
    tmp.replace(path)


def read_manifest(path):
    out = {}
    for line in Path(path).read_text().splitlines():
        sha, name = line.split("  ", 1)
        out[name] = sha
    return out


def table_files(icao, table_dir, station):
    """[(path, station, leads)] of one onboarded airport, each table checked against the folder's manifest."""
    man = read_manifest(Path(table_dir) / TABLE_MANIFEST)
    files = []
    for hs, leads in refit.HOUR_SETS:
        path = Path(table_dir) / table_name(icao, hs)
        if tables.sha256_file(path) != man.get(path.name):
            raise SystemExit(f"STOP: {path.name} SHA-256 is not the one in {TABLE_MANIFEST}")
        files.append((path, station, leads))
    return files


def current_table_files(a, table_dir=STAGEC):
    """[(path, station, leads)] of a current airport's stage C tables, each checked against its recorded SHA-256."""
    files = []
    for hs, leads in refit.HOUR_SETS:
        path = Path(table_dir) / records.table_name(a, hs)
        if tables.sha256_file(path) != records.recorded_sha(a, hs):
            raise SystemExit(f"STOP: {path.name} SHA-256 is not the recorded one")
        files.append((path, a.station, leads))
    return files


# ------------------------------------------------------------------ 3. the counts (D104.7)

def model_cells():
    return [(h, n) for h in MODEL.cycle_hours for n in range(MODEL.curve_first_lead, MODEL.last_lead + 1)]


def cell_counts(files):
    """{(cycle hour, lead): complete-case rows} over the 184 model cells, from the table files. Every
    complete-case row must be valid up to 2026-07-31T23:00 (D103.5). Counts only."""
    counts = {c: 0 for c in model_cells()}
    for path, station, leads in files:
        for cycle, valid, h, n, complete, obs, temp, x in tables.read_table_rows(path, station, leads):
            if not complete:
                continue
            if valid > baseline.LAST_TRAIN_VALID:
                raise SystemExit(f"STOP: {path.name} holds a complete-case row valid after 2026-07-31T23:00")
            if (h, n) not in counts:
                raise SystemExit(f"STOP: {path.name}: a row outside the model cells ({h}z lead {n})")
            counts[(h, n)] += 1
    return counts


def passes(counts):
    """D104.7: every one of the 184 cells has at least MIN_ROWS complete-case rows."""
    return len(counts) == len(model_cells()) and min(counts.values()) >= MIN_ROWS


def summary(counts):
    return {"smallest": min(counts.values()), "largest": max(counts.values()),
            "below": sum(1 for v in counts.values() if v < MIN_ROWS), "pass": passes(counts)}


# ------------------------------------------------------------------ 4. the models (D103.5 unchanged)

def fit_pack(args):
    """One airport and cycle hour: fit its 46 models and return (file name, bytes)."""
    icao, h, files = args
    cells = baseline.training_rows(files)
    models = {}
    for n in range(MODEL.curve_first_lead, MODEL.last_lead + 1):
        rows = cells.get((h, n))
        if not rows or len(rows) < MIN_ROWS:
            raise SystemExit(f"STOP: {icao} {h}z lead {n}: {len(rows or [])} rows, under {MIN_ROWS}")
        if rows[-1][0] + dt.timedelta(hours=n) > baseline.LAST_TRAIN_VALID:
            raise SystemExit(f"STOP: {icao} {h}z lead {n} holds a row valid after 2026-07-31T23:00")
        models[n] = baseline.fit([(r[1], r[2], r[3]) for r in rows])
    return baseline.pack_name(MODEL.name, icao, h), baseline.pack_bytes(icao, h, models)


def fit_airports(names, table_dir, out_dir, jobs=1, log=print):
    """Fit the four model files of each airport into out_dir (created if needed; no file is written
    over). Refuses an airport that fails D104.7. Returns {file name: SHA-256}."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    work = []
    for name in names:
        a = airport_of(name)
        files = table_files(a.icao, table_dir, a.station)
        if not passes(cell_counts(files)):
            raise SystemExit(f"STOP: {a.icao} fails D104.7; its models are not fitted")
        for h in MODEL.cycle_hours:
            if (out / baseline.pack_name(MODEL.name, a.icao, h)).exists():
                raise SystemExit(f"STOP: {out / baseline.pack_name(MODEL.name, a.icao, h)} already exists")
            work.append((a.icao, h, files))
    entries = {}
    t0 = time.time()

    def keep(fname, data):
        tables.write_new_file(out / fname, data)
        entries[fname] = hashlib.sha256(data).hexdigest()
        log(f"  {fname}: {len(data):,} bytes, SHA-256 {entries[fname]} ({time.time() - t0:.0f} s)")

    if jobs > 1:
        with ProcessPoolExecutor(max_workers=jobs) as ex:
            for fname, data in ex.map(fit_pack, work):
                keep(fname, data)
    else:
        for w in work:
            keep(*fit_pack(w))
    return entries


# ------------------------------------------------------------------ the command line

def main(argv=None):
    ap = argparse.ArgumentParser(description="Onboard airports of D83.2's 51 (D104.6, D104.7).")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("row", help="print the generated gfs_airports.csv rows")
    p.add_argument("airports", nargs="+")
    p = sub.add_parser("tables", help="build the two tables of each airport")
    p.add_argument("--out", required=True)
    p.add_argument("airports", nargs="+")
    p = sub.add_parser("counts", help="complete-case rows per model cell and the D104.7 verdict")
    p.add_argument("--tables")
    p.add_argument("--current", action="store_true", help="the current airports' stage C tables")
    p.add_argument("--csv", help="write the per-airport summary here (written once)")
    p.add_argument("airports", nargs="*")
    p = sub.add_parser("fit", help="fit the four model files of each passing airport")
    p.add_argument("--tables", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("airports", nargs="+")
    p = sub.add_parser("run", help="row, tables, counts and (if it passes) models, for each airport")
    p.add_argument("--tables", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--jobs", type=int, default=1)
    p.add_argument("airports", nargs="+")
    p = sub.add_parser("add-rows", help="append the airports' rows to data/gfs_airports.csv")
    p.add_argument("airports", nargs="+")
    a = ap.parse_args(argv)

    if a.cmd == "row":
        for n in a.airports:
            print(row_line(n))
    elif a.cmd == "tables":
        got = build_tables(a.airports, a.out)
        print(f"tables written: {len(got)}")
    elif a.cmd == "counts":
        if a.current:
            todo = [(x, current_table_files(x)) for x in config.load_airports(MODEL)]
        else:
            todo = []
            for n in a.airports:
                x = airport_of(n)
                todo.append((x, table_files(x.icao, a.tables, x.station)))
        out = []
        for x, files in todo:
            s = summary(cell_counts(files))
            out.append((x.icao, s))
            print(f"  {x.icao}: smallest {s['smallest']:,}, largest {s['largest']:,}, cells below {MIN_ROWS:,} "
                  f"{s['below']}, {'PASS' if s['pass'] else 'FAIL'}")
        print(f"airports {len(out)}; over all cells: smallest {min(s['smallest'] for _, s in out):,}, largest "
              f"{max(s['largest'] for _, s in out):,}; pass {sum(s['pass'] for _, s in out)}, fail "
              f"{sum(not s['pass'] for _, s in out)}")
        if a.csv:
            with open(a.csv, "x") as f:
                f.write("airport,smallest_cell_rows,largest_cell_rows,cells_below_1200,verdict\n")
                for icao, s in out:
                    f.write(f"{icao},{s['smallest']},{s['largest']},{s['below']},{'pass' if s['pass'] else 'fail'}\n")
    elif a.cmd == "fit":
        entries = fit_airports(a.airports, a.tables, a.out, a.jobs)
        print(f"model files written: {len(entries)}")
    elif a.cmd == "run":
        for n in a.airports:
            print(f"{n}: row {row_line(n)}")
            build_tables([n], a.tables)
            x = airport_of(n)
            s = summary(cell_counts(table_files(x.icao, a.tables, x.station)))
            print(f"{x.icao}: smallest {s['smallest']:,}, largest {s['largest']:,}, cells below {MIN_ROWS:,} "
                  f"{s['below']}, {'PASS' if s['pass'] else 'FAIL'}")
            if s["pass"]:
                fit_airports([n], a.tables, a.out, a.jobs)
            else:
                print(f"{x.icao}: fails D104.7; no models fitted")
    elif a.cmd == "add-rows":
        print(f"rows added: {add_rows(a.airports)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
