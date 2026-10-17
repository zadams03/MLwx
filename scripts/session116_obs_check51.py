"""Session 116: the observation plausibility check at all 51 airports, with a dew point cross-check of every stuck run
(DECISIONS D110, which extends D109).

Flag and count only (D109.6, D110.8). No raw or processed file is changed. No value is removed, replaced or filled. No
model is fitted. No error metric is computed. Nothing is scored. No forecast value is read: from the tables, only the
valid time, the lead (a row label) and the observation column are used. Nothing valid after 2026-07-31T23:00 UTC is
read. No network access. The MLwx-live repo is not read.

Modes (one per run):
  --check     Synthetic self-checks of D110.4's four classes, the dew point being taken from the same report as the
              temperature, the stuck-run extraction, the table reader and the date guard. No real value is read.
  --gate      Real data at the 12 airports of F158: checks (a), (b) and (c) run here give exactly the hours of
              data/processed/session115_obs_check/flags.csv for those checks, and the usable hours (and the hours
              check (b) could not test) equal counts.csv's.
  --flag      Checks (a), (b), (c) and D110.4's classes at the 51 airports (runs the gate first). Writes flags.csv,
              stuck_runs.csv and counts.csv.
  --exposure  D110.5 (runs the gate first, recomputes the flags and checks them against flags.csv, and checks the
              12 airports' exposure against session 115's exposure.csv). Writes exposure.csv and listing.txt.

Imported read only, unchanged, from scripts/session115_obs_check.py (after its SHA-256 check): the hourly series
builder build_hourly, the checks check_a, check_b and check_c, raw_files, local_days, day_max, hour_index, table_files,
the constants (thresholds, window, SPLIT), AIRPORTS, GROUP, IEM_ID, TZNAME and the output helpers fmt and tstr; and,
through it, scripts/session97_stagec_cv.py (write_new, csv_text, check_valid, check_obs_time, parse_time, GuardError).
From src/mlwx/observations.py: ReportSet, parse_reports, new_stats, finite_float.

New code here (no function existed): the dew point series (dew_series), D110.4's classes (classify_run), the extraction
of the stuck runs (stuck_runs), the 51-airport list and its groups (load_airports; it adds the other airports' time
zones to s115.TZNAME so that s115.local_days can be used for them), the three-column table reader (target_rows_from_lines
and its callers), the exposure counts, the gate against session 115's files, the self-checks and the outputs.

Every output file is written once and never overwritten.
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

S115_SCRIPT_SHA256 = "cc4fffdc673cd3dce9e95d099846b3040f4f53b6781c8fbd99f3fea73b64ff86"    # F158, flags.csv.meta.txt


def _sha_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if _sha_of(HERE / "session115_obs_check.py") != S115_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session115_obs_check.py's SHA-256 is not F158's")
sys.path.insert(0, str(HERE))
import session115_obs_check as s115  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402

from mlwx.observations import ReportSet, finite_float, new_stats, parse_reports  # noqa: E402

s97 = s115.s97
GuardError = s115.GuardError
sha256_file = s115.sha256_file
fmt = s115.fmt
tstr = s115.tstr
N_HOURS, HOUR, FIRST_VALID, LAST_VALID, SPLIT = s115.N_HOURS, s115.HOUR, s115.FIRST_VALID, s115.LAST_VALID, s115.SPLIT
DECIMALS = s115.DECIMALS
hour_index = s115.hour_index

OUT_DIR = ROOT / "data" / "processed" / "session116_obs_check"
S115_DIR = ROOT / "data" / "processed" / "session115_obs_check"
PULL_CSV = ROOT / "data" / "processed" / "session91_pull_airports.csv"       # D83: the 51 airports
S90_CSV = ROOT / "data" / "processed" / "session90_airports.csv"             # time zones of the 45 other airports
NEW_TABLES_CSV = ROOT / "data" / "processed" / "session111_new_tables.csv"   # D105.8: the 37 product tables' SHA-256
PRODUCT_TABLES = ROOT.parent / "MLwx-live-build" / "tables"

CHECKS = ("a", "b", "c")                      # D110.3: check (d) is not run
ALL_CHECKS = CHECKS + ("any",)
FLAG_COLUMN = {"a": "flag_a_out_of_range", "b": "flag_b_spike", "c": "flag_c_stuck"}     # session 115's flags.csv

# D110.4's classes, in the order the rule applies them.
CLASSES = (("i", "no dew point"), ("ii", "dew point varies"), ("iii", "saturated"), ("iv", "suspect"))
CLASS_NAME = dict(CLASSES)


# ------------------------------------------------------------------ the 51 airports

def load_airports():
    """The 51 airports of D83 in report order: the 12 of F158 (claim first, then development), the 37 product
    airports (in the order of session111_new_tables.csv), then the other two (MMMX and VILK). Returns
    (order, info) where info[icao] = {iem, group, tz, tables}; tables is None for the airports without any."""
    pull = list(csv.DictReader(open(PULL_CSV, newline="")))
    s90 = {r["icao"]: r for r in csv.DictReader(open(S90_CSV, newline=""))}
    by = {r["icao"]: r for r in pull}
    if len(pull) != 51 or len(by) != 51:
        raise SystemExit(f"STOP: {PULL_CSV.name} does not hold 51 distinct airports")
    new_rows = list(csv.DictReader(open(NEW_TABLES_CSV, newline="")))
    product = []
    for r in new_rows:
        if r["airport"] not in product:
            product.append(r["airport"])
    twelve = list(s115.AIRPORTS)
    for ic in twelve:
        if by[ic]["iem_id"] != s115.IEM_ID[ic]:
            raise SystemExit(f"STOP: {ic}: the IEM id in {PULL_CSV.name} is not session 115's")
    if len(product) != 37 or set(product) & set(twelve) or not set(product) <= set(by):
        raise SystemExit("STOP: the product airports are not 37 distinct airports of D83 outside the 12")
    other = [r["icao"] for r in pull if r["icao"] not in twelve and r["icao"] not in product]
    if sorted(other) != ["MMMX", "VILK"]:
        raise SystemExit(f"STOP: the airports left after the 12 and the 37 are {other}, not MMMX and VILK")
    order = twelve + product + sorted(other)
    info = {}
    for ic in order:
        if ic in twelve:
            group, tz = s115.GROUP[ic], s115.TZNAME[ic]
        else:
            group = "product" if ic in product else "other"
            if ic not in s90 or s90[ic]["iem_id"] != by[ic]["iem_id"]:
                raise SystemExit(f"STOP: {ic} is not in {S90_CSV.name} with the same IEM id")
            tz = s90[ic]["time_zone"]
            s115.TZNAME[ic] = tz            # so that s115.local_days can be used (read-only use of s115's helper)
        info[ic] = {"iem": by[ic]["iem_id"], "group": group, "tz": tz, "tables": None}
    for r in new_rows:
        if info[r["airport"]]["tables"] is None:
            info[r["airport"]]["tables"] = []
        info[r["airport"]]["tables"].append((PRODUCT_TABLES / r["file"], r["sha256"]))
    for ic in twelve:
        info[ic]["tables"] = list(s115.table_files(ic))
    return order, info


# ------------------------------------------------------------------ the dew point series and D110.4's classes

def clean_dew(raw):
    """A dew point as the temperature is read (SPEC 8.8 G2): M, blank, T and None are missing; a non-finite
    value is missing."""
    raw = (raw or "").strip()
    if raw in ("M", "", "T", "None"):
        return None
    return finite_float(raw)


def dew_series(texts, iem_id, vals):
    """The dew point (dwpc) of the report used for each hour's temperature, aligned to the series (value or None).
    The report used is the one ReportSet.nearest returns: the nearest usable report within 15 minutes of the hour
    (inclusive), the first row of a repeated timestamp kept. Its own dwpc is taken, never another report's: a report
    whose dwpc is missing gives None for that hour. vals is the temperature series (s115.build_hourly) and must
    agree with the temperature this pairing returns."""
    stats = new_stats()
    reports, dew_at = [], {}
    for text in texts:
        for r in csv.DictReader(io.StringIO(text)):
            s97.check_obs_time(dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M"))
        reports.extend(parse_reports(text, iem_id, stats))
        for r in csv.DictReader(io.StringIO(text)):
            t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
            if t not in dew_at:                 # the first row of a repeated timestamp, as ReportSet keeps
                dew_at[t] = clean_dew(r.get("dwpc"))
    rs = ReportSet(reports, stats, live=False)
    out = []
    for k in range(N_HOURS):
        h = FIRST_VALID + k * HOUR
        s97.check_valid(h)
        obs, rep_time = rs.nearest(h)
        if obs != vals[k]:
            raise SystemExit(f"STOP: {iem_id}: the pairing for the dew point gave a different temperature at {tstr(h)}")
        out.append(dew_at[rep_time] if rep_time is not None else None)
    return out


def classify_run(temp, dews):
    """D110.4's class of one stuck run, in the rule's order. temp is the run's temperature; dews are the dew points of
    the run's hours (value or None). Returns the class id: 'i', 'ii', 'iii' or 'iv'."""
    present = [d for d in dews if d is not None]
    if 2 * len(present) < len(dews):                         # (i) fewer than half the run's hours have a dew point
        return "i"
    distinct = {round(d, DECIMALS) for d in present}
    if len(distinct) > 1:                                    # (ii) the dew points present are not all equal
        return "ii"
    if distinct == {round(temp, DECIMALS)}:                  # (iii) all equal, and equal to the run's temperature
        return "iii"
    return "iv"                                              # (iv) all equal, and different from the run's temperature


def stuck_runs(vals, flag_c, run_len):
    """[(first index, last index)] of every stuck run of D109.4(c), from check_c's flags. Neighbouring flagged hours
    with different values are different runs."""
    runs, i = [], 0
    while i < len(vals):
        if not flag_c[i]:
            i += 1
            continue
        j = i
        while j + 1 < len(vals) and flag_c[j + 1] and vals[j + 1] == vals[i]:
            j += 1
        if j - i + 1 != run_len[i]:
            raise SystemExit(f"STOP: a stuck run at index {i} has length {j - i + 1}, check (c) says {run_len[i]}")
        runs.append((i, j))
        i = j + 1
    return runs


def checks_abc(vals):
    """D109.4 (a), (b) and (c) by session 115's functions, unchanged, and their union (check (d) is not run)."""
    fa = s115.check_a(vals)
    fb, unt, unt_pairs, kind = s115.check_b(vals)
    fc, run = s115.check_c(vals)
    union = [x or y or z for x, y, z in zip(fa, fb, fc)]
    return {"a": fa, "b": fb, "c": fc, "any": union, "b_kind": kind, "run": run, "unt_b": unt, "unt_pairs": unt_pairs}


def run_records(ic, vals, dews, fl):
    """One dict per stuck run: id, indices, length, temperature, dew points, class."""
    out = []
    for n, (i, j) in enumerate(stuck_runs(vals, fl["c"], fl["run"]), 1):
        d = dews[i:j + 1]
        present = [x for x in d if x is not None]
        out.append({"id": f"{ic}-{n}", "i": i, "j": j, "length": j - i + 1, "temp": vals[i], "dews": d,
                    "n_present": len(present), "distinct": sorted({round(x, DECIMALS) for x in present}),
                    "cls": classify_run(vals[i], d)})
    return out


# ------------------------------------------------------------------ real data

def load_one(ic, info):
    files = s115.raw_files(info[ic]["iem"])
    texts = [f.read_text() for f in files]
    vals, stats = s115.build_hourly(texts, info[ic]["iem"])       # guards every report time first
    dews = dew_series(texts, info[ic]["iem"], vals)
    return {"vals": vals, "dews": dews, "stats": stats, "files": files}


def load_all(order, info):
    data = {}
    for ic in order:
        data[ic] = load_one(ic, info)
        data[ic]["fl"] = checks_abc(data[ic]["vals"])
        data[ic]["runs"] = run_records(ic, data[ic]["vals"], data[ic]["dews"], data[ic]["fl"])
    return data


def meta_file_sha(path):
    m = re.search(r"file SHA-256 ([0-9a-f]{64})", Path(str(path) + ".meta.txt").read_text())
    return m.group(1) if m else None


def run_gate_on(order, info, data):
    """Checks (a), (b), (c) and the usable hours at the 12 airports against session 115's flags.csv and counts.csv."""
    flags_p, counts_p = S115_DIR / "flags.csv", S115_DIR / "counts.csv"
    for p in (flags_p, counts_p):
        if sha256_file(p) != meta_file_sha(p):
            print(f"STOP: {p.name}'s SHA-256 is not the value in its .meta.txt")
            return False
    rec = {}
    with open(flags_p, newline="") as f:
        for r in csv.DictReader(f):
            for c in CHECKS:
                if r[FLAG_COLUMN[c]] == "true":
                    rec.setdefault((r["airport"], c), set()).add(r["valid_utc"])
    cnt = {}
    with open(counts_p, newline="") as f:
        for r in csv.DictReader(f):
            cnt[(r["airport"], r["check"])] = r
    ok_all = True
    print(f"{'airport':7}{'usable':>8}{'rec_use':>8}{'a':>5}{'b':>5}{'c':>6}{'a_eq':>6}{'b_eq':>6}{'c_eq':>6}{'untB':>6}{'rec':>6}{'pairs':>6}{'rec':>6}  gate")
    for ic in s115.AIRPORTS:
        vals, fl = data[ic]["vals"], data[ic]["fl"]
        usable = sum(1 for v in vals if v is not None)
        rec_usable = int(cnt[(ic, "a")]["usable_hours"])
        eq = {}
        for c in CHECKS:
            mine = {tstr(FIRST_VALID + k * HOUR) for k in range(N_HOURS) if fl[c][k]}
            eq[c] = mine == rec.get((ic, c), set())
        unt_ok = (fl["unt_b"]["either"] == int(cnt[(ic, "b")]["untested_hours"])
                  and fl["unt_pairs"] == int(cnt[(ic, "b")]["untested_pairs"]))
        ok = usable == rec_usable and all(eq.values()) and unt_ok
        ok_all = ok_all and ok
        print(f"{ic:7}{usable:8d}{rec_usable:8d}{sum(fl['a']):5d}{sum(fl['b']):5d}{sum(fl['c']):6d}"
              f"{'yes' if eq['a'] else 'NO':>6}{'yes' if eq['b'] else 'NO':>6}{'yes' if eq['c'] else 'NO':>6}"
              f"{fl['unt_b']['either']:6d}{int(cnt[(ic, 'b')]['untested_hours']):6d}{fl['unt_pairs']:6d}"
              f"{int(cnt[(ic, 'b')]['untested_pairs']):6d}  {'PASS' if ok else 'FAIL'}")
    print("GATE PASSED at 12 of 12 airports" if ok_all else "GATE FAILED: STOP")
    return ok_all


# ------------------------------------------------------------------ the tables: valid time, lead and observation only

def target_rows_from_lines(lines):
    """From a table's text lines, the rows' (valid time, lead, observation or None), nothing else. The csv module reads
    each line whole; every other column is discarded unread. A valid time after 2026-07-31T23:00 UTC is refused before
    the row's observation is taken."""
    r = csv.reader(lines)
    header = next(r)
    iv, il, io_ = header.index("valid_utc"), header.index("lead"), header.index("obs_tmpc")
    out = []
    for row in r:
        valid = s97.parse_time(row[iv])
        s97.check_valid(valid)
        out.append((valid, int(row[il]), clean_dew(row[io_])))      # an empty or M observation is None (as the dew point)
    return out


def read_target_rows(path, want_sha):
    if sha256_file(path) != want_sha:
        raise SystemExit(f"STOP: {path.name}'s SHA-256 is not the recorded value")
    with gzip.open(path, "rt", newline="") as f:
        return target_rows_from_lines(f)


def targets_of(info_ic):
    """({hour index: 0 before 2024-08-01, 1 from}, {hour index: rows}) for target rows: leads 3 to 48 with an
    observation (D109.5, as session 115 counted them)."""
    per, nrows = {}, {}
    for path, want in info_ic["tables"]:
        for valid, lead, obs in read_target_rows(path, want):
            if not (s115.GFS_LEAD_MIN <= lead <= s115.GFS_LEAD_MAX) or obs is None:
                continue
            k = hour_index(valid)
            if not (0 <= k < N_HOURS):
                raise SystemExit(f"STOP: a table row has valid time {tstr(valid)} outside the series window")
            per.setdefault(k, 0 if valid < SPLIT else 1)
            nrows[k] = nrows.get(k, 0) + 1
    return per, nrows


def days_of(ic, vals):
    """([(local date, [indices of the hours that set the usable day's maximum])], None), or (None, reason) when the
    airport's local day cannot be computed (a time zone that is not a whole number of hours from UTC, F153)."""
    try:
        local = s115.local_days(ic)
    except SystemExit as e:
        return None, str(e)
    days = []
    for d, hours in local:
        usable, m, setters = s115.day_max(vals, hours)
        if usable:
            days.append((d, [hour_index(h) for h in setters]))
    return days, None


# ------------------------------------------------------------------ outputs

def meta_text(title, out_path, inputs, extra):
    lines = [title, f"output {out_path.name}", f"run {s115.now_utc()}; {s115.versions()}",
             f"script scripts/{Path(__file__).name} SHA-256 {sha256_file(Path(__file__).resolve())}",
             "no network access; nothing valid after 2026-07-31T23:00 UTC read (D110.3); flag and count only (D110.8)",
             "", "inputs:"]
    lines += [f"  {n}  {h}" for n, h in inputs]
    lines += [""] + extra
    return "\n".join(lines) + "\n"


def input_list(order, info, data, with_tables):
    ins = [(f"data/raw/{f.name}", sha256_file(f)) for ic in order for f in data[ic]["files"]]
    ins.append((f"data/processed/{PULL_CSV.name}", sha256_file(PULL_CSV)))
    ins.append((f"data/processed/{S90_CSV.name}", sha256_file(S90_CSV)))
    if with_tables:
        for ic in order:
            for p, want in info[ic]["tables"] or []:
                ins.append((f"{p.parent.name}/{p.name} (recorded {want[:12]}...)", sha256_file(p)))
    ins.append(("scripts/session115_obs_check.py", sha256_file(HERE / "session115_obs_check.py")))
    return ins


def write_out(name, text, title, order, info, data, extra, with_tables=False):
    path = OUT_DIR / name
    s97.write_new(path, text)
    meta = meta_text(title, path, input_list(order, info, data, with_tables), [f"file SHA-256 {sha256_file(path)}"] + extra)
    s97.write_new(OUT_DIR / (name + ".meta.txt"), meta)


def write_csv_out(name, header, rows, title, order, info, data, extra, with_tables=False):
    write_out(name, s97.csv_text(header, rows), title, order, info, data, [f"rows {len(rows)} (header excluded)"] + extra,
              with_tables)


def check_outputs_absent(names):
    for n in names:
        for p in (OUT_DIR / n, OUT_DIR / (n + ".meta.txt")):
            if p.exists():
                raise SystemExit(f"STOP: {p} already exists; not overwriting it")


COMMON = [f"thresholds (D109.4, unchanged): range {s115.RANGE_LOW} to {s115.RANGE_HIGH}; spike {s115.SPIKE_DELTA}; stuck run "
          f"{s115.STUCK_MIN_RUN}; differences rounded to {DECIMALS} decimals before the comparison; check (d) is not run (D110.3)",
          "D110.4 classes: i no dew point (fewer than half the run's hours have a finite dew point); ii dew point varies; "
          "iii saturated (all equal, equal to the run's temperature); iv suspect (all equal, different from the run's temperature)"]


def rate(n, usable):
    return round(10000.0 * n / usable, 4) if usable else ""


def run_flag(order, info):
    check_outputs_absent(["flags.csv", "stuck_runs.csv", "counts.csv"])
    data = load_all(order, info)
    if not run_gate_on(order, info, data):
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    frows, rrows, crows = [], [], []
    tot = {g: {"usable": 0, **{c: 0 for c in ALL_CHECKS}, "unt_b": 0, "pairs": 0, "cls": {k: 0 for k, _ in CLASSES}}
           for g in ("12", "37", "2", "51")}
    gkey = {"claim": "12", "dev": "12", "product": "37", "other": "2"}
    for ic in order:
        d, fl = data[ic], data[ic]["fl"]
        vals, dews = d["vals"], d["dews"]
        grp = info[ic]["group"]
        runs = d["runs"]
        run_of = {}
        for r in runs:
            for k in range(r["i"], r["j"] + 1):
                run_of[k] = r
        usable = sum(1 for v in vals if v is not None)
        for k in range(N_HOURS):
            if not fl["any"][k]:
                continue
            r = run_of.get(k)
            nb = [fmt(vals[j]) if 0 <= j < N_HOURS else "" for j in (k - 2, k - 1, k + 1, k + 2)]
            frows.append([ic, info[ic]["iem"], grp, tstr(FIRST_VALID + k * HOUR), fmt(vals[k]), fmt(fl["a"][k]), fmt(fl["b"][k]),
                          fmt(fl["c"][k]), fl["b_kind"][k]] + nb + [fmt(dews[k]), r["id"] if r else "",
                                                                     r["length"] if r else "", CLASS_NAME[r["cls"]] if r else ""])
        for r in runs:
            rrows.append([r["id"], ic, info[ic]["iem"], grp, tstr(FIRST_VALID + r["i"] * HOUR), tstr(FIRST_VALID + r["j"] * HOUR),
                          r["length"], fmt(r["temp"]), r["n_present"], len(r["distinct"]),
                          fmt(r["distinct"][0]) if r["distinct"] else "", fmt(r["distinct"][-1]) if r["distinct"] else "",
                          " ".join(fmt(x) for x in r["distinct"]), r["cls"], CLASS_NAME[r["cls"]]])
        n = {c: sum(fl[c]) for c in ALL_CHECKS}
        ncls = {k: sum(1 for r in runs if r["cls"] == k) for k, _ in CLASSES}
        crows += count_rows(ic, grp, usable, n, fl["unt_b"]["either"], fl["unt_pairs"], ncls,
                            f"h-1 missing {fl['unt_b']['prev']}, h+1 missing {fl['unt_b']['next']} (an hour can be in both)")
        for g in (gkey[grp], "51"):
            t = tot[g]
            t["usable"] += usable
            for c in ALL_CHECKS:
                t[c] += n[c]
            t["unt_b"] += fl["unt_b"]["either"]
            t["pairs"] += fl["unt_pairs"]
            for k in ncls:
                t["cls"][k] += ncls[k]
    for g, label, glabel in (("12", "ALL_12", "the 12 of F158"), ("37", "ALL_37", "the 37 product airports"),
                             ("2", "ALL_2", "MMMX and VILK"), ("51", "ALL_51", "all 51")):
        t = tot[g]
        crows += count_rows(label, glabel, t["usable"], {c: t[c] for c in ALL_CHECKS}, t["unt_b"], t["pairs"], t["cls"],
                            "sum over the airports")
    fh = ["airport", "iem_id", "group", "valid_utc", "value_c", "flag_a_out_of_range", "flag_b_spike", "flag_c_stuck", "spike_kind",
          "value_h_minus_2", "value_h_minus_1", "value_h_plus_1", "value_h_plus_2", "dew_point_c", "run_id", "run_length_c",
          "run_class"]
    rh = ["run_id", "airport", "iem_id", "group", "start_utc", "end_utc", "length_hours", "temperature_c", "hours_with_dew_point",
          "distinct_dew_points", "dew_point_min", "dew_point_max", "dew_points_present", "class_id", "class"]
    ch = ["airport", "group", "check", "usable_hours", "untested_hours", "untested_reason", "untested_pairs", "flagged_hours",
          "rate_per_10000_usable_hours", "runs_i_no_dew_point", "runs_ii_dew_point_varies", "runs_iii_saturated", "runs_iv_suspect"]
    write_csv_out("flags.csv", fh, frows, "Session 116 flags.csv: one row per flagged hour, checks (a), (b), (c) (D110.3)",
                  order, info, data, COMMON)
    write_csv_out("stuck_runs.csv", rh, rrows, "Session 116 stuck_runs.csv: one row per stuck run with D110.4's class", order,
                  info, data, COMMON)
    write_csv_out("counts.csv", ch, crows, "Session 116 counts.csv: counts per airport and check, and runs per class", order,
                  info, data, COMMON)
    print(f"flags.csv: {len(frows)} flagged hours (union a, b, c); stuck_runs.csv: {len(rrows)} runs; counts.csv: {len(crows)} rows")
    print(f"{'airport':8}{'group':9}{'usable':>8}{'a':>4}{'b':>4}{'c':>6}{'union':>7}{'rate':>8}   runs i/ii/iii/iv")
    show = {}
    for r in crows:
        show.setdefault(r[0], {})[r[2]] = r
    for ic in order + ["ALL_12", "ALL_37", "ALL_2", "ALL_51"]:
        s = show[ic]
        print(f"{ic:8}{(info[ic]['group'] if ic in info else 'sum'):9}{s['a'][3]:8d}{s['a'][7]:4d}{s['b'][7]:4d}{s['c'][7]:6d}"
              f"{s['any'][7]:7d}{s['any'][8]:8}   {s['c'][9]}/{s['c'][10]}/{s['c'][11]}/{s['c'][12]}")
    return 0


def count_rows(label, group, usable, n, unt_b, pairs, ncls, why_b):
    rows = []
    for c in CHECKS:
        if c == "b":
            unt, why, pr = unt_b, "a neighbour hour (h-1 or h+1) missing or off the series: " + why_b, pairs
        else:
            unt, why, pr = 0, "every hour with a value can be tested", ""
        cls = [ncls[k] for k, _ in CLASSES] if c == "c" else ["", "", "", ""]
        rows.append([label, group, c, usable, unt, why, pr, n[c], rate(n[c], usable)] + cls)
    rows.append([label, group, "any", usable, "", "union of (a), (b) and (c): an hour is counted once", "", n["any"],
                 rate(n["any"], usable), "", "", "", ""])
    return rows


# ------------------------------------------------------------------ the exposure

def exposure_rows(ic, info, d):
    """Rows of exposure.csv for one airport: 'all' (the denominators) and one per check."""
    vals, fl = d["vals"], d["fl"]
    usable = sum(1 for v in vals if v is not None)
    has_tables = bool(info[ic]["tables"])
    per, nrows = targets_of(info[ic]) if has_tables else ({}, {})
    days, why = days_of(ic, vals)
    status = "computed" if days is not None else f"not computed: {why}"
    out = []
    for c in ("all",) + ALL_CHECKS:
        sel = (lambda k: True) if c == "all" else (lambda k, c=c: fl[c][k])
        th, tr, dy = [0, 0], [0, 0], [0, 0]
        for k, p in per.items():
            if sel(k):
                th[p] += 1
                tr[p] += nrows[k]
        for dte, ks in days or []:
            if c == "all" or any(fl[c][k] for k in ks):
                dy[0 if dte < SPLIT.date() else 1] += 1
        flagged = "" if c == "all" else sum(fl[c])
        tab = ("stage C" if info[ic]["group"] in ("claim", "dev") else "product") if has_tables else "none"
        out.append([ic, info[ic]["group"], c, usable, flagged, tab,
                    th[0] if has_tables else "", th[1] if has_tables else "", tr[0] if has_tables else "",
                    tr[1] if has_tables else "", dy[0] if days is not None else "", dy[1] if days is not None else "", status])
    return out


def gate_exposure(xrows):
    """The 12 airports' rows for a, b, c and 'all' equal session 115's exposure.csv (target hours and rows, and the usable
    days whose maximum is set by a flagged hour)."""
    p = S115_DIR / "exposure.csv"
    if sha256_file(p) != meta_file_sha(p):
        print("STOP: session 115's exposure.csv SHA-256 is not the value in its .meta.txt")
        return False
    rec = {}
    with open(p, newline="") as f:
        for r in csv.DictReader(f):
            rec[(r["airport"], r["check"])] = (int(r["target_hours_before_2024_08_01"]), int(r["target_hours_from_2024_08_01"]),
                                               int(r["target_rows_before"]), int(r["target_rows_from"]),
                                               int(r["usable_days_whose_max_hour_is_flagged_before"]),
                                               int(r["usable_days_whose_max_hour_is_flagged_from"]))
    bad = 0
    n = 0
    for r in xrows:
        if r[0] not in s115.AIRPORTS or r[2] == "any":
            continue
        n += 1
        mine = (r[6], r[7], r[8], r[9], r[10], r[11])
        if mine != rec[(r[0], r[2])]:
            bad += 1
            print(f"  exposure differs from session 115: {r[0]} {r[2]} mine {mine} theirs {rec[(r[0], r[2])]}")
    print(f"exposure at the 12 airports against session 115's exposure.csv: {n - bad} of {n} airport/check rows equal"
          f" ({'PASS' if bad == 0 else 'FAIL'})")
    return bad == 0


def run_exposure(order, info):
    names = ["exposure.csv", "listing.txt"]
    check_outputs_absent(names)
    flags_p = OUT_DIR / "flags.csv"
    if not flags_p.exists():
        raise SystemExit("STOP: flags.csv does not exist; run --flag first")
    data = load_all(order, info)
    if not run_gate_on(order, info, data):
        return 1
    rec = {}
    with open(flags_p, newline="") as f:
        for r in csv.DictReader(f):
            rec.setdefault(r["airport"], set()).add(r["valid_utc"])
    for ic in order:
        mine = {tstr(FIRST_VALID + k * HOUR) for k in range(N_HOURS) if data[ic]["fl"]["any"][k]}
        if mine != rec.get(ic, set()):
            print(f"STOP: {ic}: the recomputed flagged hours differ from flags.csv")
            return 1
    print("recomputed flagged hours equal flags.csv at 51 of 51 airports")
    xrows = []
    for ic in order:
        xrows += exposure_rows(ic, info, data[ic])
    if not gate_exposure(xrows):
        return 1
    xh = ["airport", "group", "check", "usable_hours", "flagged_hours", "tables", "target_hours_before_2024_08_01",
          "target_hours_from_2024_08_01", "target_rows_before", "target_rows_from", "usable_days_whose_max_hour_is_flagged_before",
          "usable_days_whose_max_hour_is_flagged_from", "days_status"]
    extra = COMMON + ["check 'all' rows hold the denominators (usable hours; target hours and rows; usable days); the other rows hold "
                      "the flagged counts in the same columns",
                      "target = a table row at leads 3 to 48 with an observation (D109.5 as session 115 counted it); only the valid "
                      "time, the lead and the observation column of a table are used; split by the row's valid time (days: local date)",
                      "usable day = D82.8 (usable hours at least the day's hours minus 2), every local day wholly inside the window; its "
                      "maximum hour(s) = every hour that attains the day's maximum",
                      "tables 'none' = no stage C or product table (MMMX, VILK): target columns blank; days_status says if a day "
                      "could not be computed (blank day columns)"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv_out("exposure.csv", xh, xrows, "Session 116 exposure.csv (D110.5)", order, info, data, extra, with_tables=True)
    write_listing(order, info, data)
    print(f"exposure.csv: {len(xrows)} rows")
    print(f"{'airport':8}{'group':9}{'flagged':>8}{'tgt hrs <':>10}{'tgt hrs >=':>11}{'days <':>7}{'days >=':>8}  days_status")
    for r in xrows:
        if r[2] == "any":
            print(f"{r[0]:8}{r[1]:9}{r[4]:8d}{str(r[6]):>10}{str(r[7]):>11}{str(r[10]):>7}{str(r[11]):>8}  {r[12][:48]}")
    return 0


def write_listing(order, info, data):
    """listing.txt: every out-of-range and spike hour with its neighbours and dew point; every class (iv) run; per airport
    the run counts by class. Descriptive only."""
    L = ["Out-of-range and spike hours (checks (a) and (b)): values at h-2, h-1, [h], h+1, h+2, and the dew point at h"]
    n = 0
    for ic in order:
        d, fl = data[ic], data[ic]["fl"]
        for k in range(N_HOURS):
            if fl["a"][k] or fl["b"][k]:
                n += 1
                nb = [fmt(d["vals"][j]) if 0 <= j < N_HOURS else "" for j in (k - 2, k - 1, k, k + 1, k + 2)]
                L.append(f"  {ic} {tstr(FIRST_VALID + k * HOUR)} flags {'a' if fl['a'][k] else ''}{'b' if fl['b'][k] else ''}"
                         f"{'(' + fl['b_kind'][k] + ')' if fl['b'][k] else ''} values [{', '.join(nb)}] dew {fmt(d['dews'][k])}")
    L.append(f"  {n} hours")
    L.append("")
    L.append("Stuck runs in class (iv) suspect: id, start, end, length, temperature, dew point, hours with a dew point")
    n = 0
    for ic in order:
        for r in data[ic]["runs"]:
            if r["cls"] == "iv":
                n += 1
                L.append(f"  {r['id']} {tstr(FIRST_VALID + r['i'] * HOUR)} to {tstr(FIRST_VALID + r['j'] * HOUR)} {r['length']} h "
                         f"temp {fmt(r['temp'])} dew {' '.join(fmt(x) for x in r['distinct'])} ({r['n_present']} of {r['length']})")
    L.append(f"  {n} runs")
    L.append("")
    L.append("Stuck runs by class, per airport (i no dew point / ii varies / iii saturated / iv suspect), and run lengths")
    for ic in order:
        runs = data[ic]["runs"]
        if not runs:
            continue
        c = {k: sum(1 for r in runs if r["cls"] == k) for k, _ in CLASSES}
        L.append(f"  {ic:5} {info[ic]['group']:8} {c['i']}/{c['ii']}/{c['iii']}/{c['iv']}  runs {len(runs)}, hours {sum(r['length'] for r in runs)},"
                 f" longest {max(r['length'] for r in runs)}")
    write_out("listing.txt", "\n".join(L) + "\n", "Session 116 listing.txt (D110.5, descriptive only)", order, info, data,
              COMMON + ["descriptive only: no score of any kind (D110.8)"])


# ------------------------------------------------------------------ synthetic self-checks

class Checker:
    def __init__(self):
        self.n = 0
        self.fail = 0

    def ok(self, name, cond):
        self.n += 1
        if not cond:
            self.fail += 1
        print(f"  {'PASS' if cond else 'FAIL'}: {name}")


HEAD = "station,valid,tmpc,dwpc,lat,lon,elevation\n"


def run_check():
    c = Checker()
    print("D110.4's four classes")
    t = 5.0
    c.ok("24 hours, every dew point equal to the temperature: saturated (iii)", classify_run(t, [5.0] * 24) == "iii")
    c.ok("24 hours, every dew point 3.0 against a temperature of 5.0: suspect (iv)", classify_run(t, [3.0] * 24) == "iv")
    c.ok("24 hours, dew points differing by one degree (23 at 3.0 and one at 4.0): varies (ii)",
         classify_run(t, [3.0] * 23 + [4.0]) == "ii")
    c.ok("24 hours, dew points 5.0 and 4.0 where one equals the temperature: still varies (ii)",
         classify_run(t, [5.0] * 12 + [4.0] * 12) == "ii")
    c.ok("24 hours, 11 dew points present (under half), all equal to the temperature: no dew point (i)",
         classify_run(t, [5.0] * 11 + [None] * 13) == "i")
    c.ok("24 hours, 11 dew points present and varying: still no dew point (i), the order of the rule",
         classify_run(t, [1.0, 2.0] * 5 + [3.0] + [None] * 13) == "i")
    c.ok("24 hours, no dew point at all: no dew point (i)", classify_run(t, [None] * 24) == "i")
    c.ok("24 hours, exactly 12 present (half is not fewer than half), all equal to the temperature: saturated (iii)",
         classify_run(t, [5.0] * 12 + [None] * 12) == "iii")
    c.ok("24 hours, 13 present of 24 (some missing but over half), all 3.0: suspect (iv)",
         classify_run(t, [3.0] * 13 + [None] * 11) == "iv")
    c.ok("24 hours, 13 present of 24, varying: varies (ii)", classify_run(t, [3.0] * 12 + [4.0] + [None] * 11) == "ii")
    c.ok("25 hours, 12 present is under half (12.5): no dew point (i)", classify_run(t, [5.0] * 12 + [None] * 13) == "i")
    c.ok("a decimal tie, 0.1 + 0.2 against 0.3, counts as equal (saturated)", classify_run(0.3, [0.1 + 0.2] * 24) == "iii")
    print("the dew point is taken from the same report as the hour's temperature")
    rows = ["XXXX,2021-03-24 00:50,11.0,7.0,0,0,0",       # 10 minutes before 01:00
            "XXXX,2021-03-24 01:05,12.0,8.0,0,0,0",       # 5 minutes after: the nearest, so 01:00 takes 12.0 and 8.0
            "XXXX,2021-03-24 01:50,M,9.0,0,0,0",          # nearest to 02:00 but no temperature: skipped (G2)
            "XXXX,2021-03-24 02:10,13.0,10.0,0,0,0",      # so 02:00 takes this report and its 10.0, not 9.0
            "XXXX,2021-03-24 02:55,14.0,M,0,0,0",         # nearest to 03:00 and has a temperature but no dew point
            "XXXX,2021-03-24 03:14,15.0,11.0,0,0,0",      # another report in the window: its dew point must not be used
            "XXXX,2021-03-24 04:00,16.0,12.0,0,0,0",      # a repeated timestamp: the first row is kept, with its dew point
            "XXXX,2021-03-24 04:00,17.0,13.0,0,0,0"]
    text = HEAD + "\n".join(rows) + "\n"
    vals, _ = s115.build_hourly([text], "XXXX")
    dews = dew_series([text], "XXXX", vals)
    c.ok("01:00 takes 12.0 from the 01:05 report and the dew point of that report, 8.0, not the 00:50 report's 7.0",
         vals[1] == 12.0 and dews[1] == 8.0)
    c.ok("02:00 skips the report with no temperature and takes 13.0 with its own dew point 10.0, not 9.0",
         vals[2] == 13.0 and dews[2] == 10.0)
    c.ok("03:00 takes 14.0 whose own dew point is missing: None, not another report's 11.0", vals[3] == 14.0 and dews[3] is None)
    c.ok("a repeated timestamp keeps the first row's temperature and dew point (16.0 and 12.0)",
         vals[4] == 16.0 and dews[4] == 12.0)
    c.ok("an hour with no usable report has no temperature and no dew point", vals[10] is None and dews[10] is None)
    c.ok("clean_dew: M, blank, T, None and nan are missing; 'nan' and 'inf' are not finite",
         all(clean_dew(x) is None for x in ("M", "", "T", "None", "nan", "inf", None)) and clean_dew("-1.00") == -1.0)
    print("stuck-run extraction")
    v = [4.0] + [5.0] * 24 + [6.0] * 24 + [None] + [7.0] * 30
    fl = checks_abc(v)
    runs = stuck_runs(v, fl["c"], fl["run"])
    c.ok("neighbouring flagged runs with different values are separate runs (1-24, 25-48, 50-79)",
         runs == [(1, 24), (25, 48), (50, 79)])
    c.ok("the union is (a) or (b) or (c) only; check (d) is not part of it",
         fl["any"] == [x or y or z for x, y, z in zip(fl["a"], fl["b"], fl["c"])] and "d" not in fl)
    v2 = [10.0 + (i % 2) for i in range(10)]
    v2[3] = 80.0
    f2 = checks_abc(v2)
    c.ok("an hour of 80.0 carries (a) and (b) and not (c); the union counts it once",
         f2["a"][3] and f2["b"][3] and not f2["c"][3] and sum(f2["any"]) == 1)
    print("the three-column table reader")
    lines = ["station,cycle_utc,cycle_hour,lead,valid_utc,temp,obs_tmpc,secret_forecast",
             "XXXX,2021-03-24T00:00Z,0,24,2021-03-24T00:00Z,99.9,,98.7", "XXXX,2021-03-24T00:00Z,0,3,2021-03-24T03:00Z,99.9,1.5,98.7"]
    got = target_rows_from_lines(lines)
    c.ok("only the valid time, the lead and the observation are returned; an empty observation is None",
         got == [(dt.datetime(2021, 3, 24, 0, 0), 24, None), (dt.datetime(2021, 3, 24, 3, 0), 3, 1.5)])
    try:
        target_rows_from_lines(lines + ["XXXX,2026-07-31T23:00Z,0,3,2026-08-01T00:00Z,99.9,5.0,98.7"])
        refused = False
    except GuardError:
        refused = True
    c.ok("a table row valid at 2026-08-01T00:00 is refused", refused)
    print("local days and the date guard")
    days, why = days_of_tz_check()
    c.ok("a half-hour time zone (Asia/Kolkata) gives 'not computed', not a stop", days is None and why is not None)
    try:
        s97.check_valid(dt.datetime(2026, 8, 1, 0, 0))
        refused = False
    except GuardError:
        refused = True
    c.ok("a valid time of 2026-08-01T00:00 is refused", refused)
    try:
        s97.check_valid(LAST_VALID)
        accepted = True
    except GuardError:
        accepted = False
    c.ok("a valid time of 2026-07-31T23:00 is accepted", accepted)
    bad = HEAD + "XXXX,2026-07-31 23:00,10.0,5.0,0,0,0\nXXXX,2026-08-01 00:00,11.0,5.0,0,0,0\n"
    try:
        dew_series([bad], "XXXX", [None] * N_HOURS)
        refused = False
    except GuardError:
        refused = True
    c.ok("the dew point series refuses a file with a report at 2026-08-01T00:00 before reading a dew point", refused)
    print(f"\n{c.n - c.fail} of {c.n} synthetic checks passed")
    print("ALL CHECKS PASSED" if c.fail == 0 else "A CHECK FAILED: STOP")
    return 0 if c.fail == 0 else 1


def days_of_tz_check():
    """days_of on a made-up airport key in a half-hour zone."""
    s115.TZNAME["ZZZZ"] = "Asia/Kolkata"
    return days_of("ZZZZ", [None] * N_HOURS)


def run_gate(order, info):
    data = {ic: None for ic in order}
    for ic in s115.AIRPORTS:
        data[ic] = load_one(ic, info)
        data[ic]["fl"] = checks_abc(data[ic]["vals"])
    ok = run_gate_on(order, info, data)
    have = sum(1 for ic in s115.AIRPORTS for x in data[ic]["dews"] if x is not None)
    tot = sum(1 for ic in s115.AIRPORTS for x in data[ic]["vals"] if x is not None)
    print(f"dew points present at the 12 airports: {have} of {tot} usable hours")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("check", "gate", "flag", "exposure"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    if a.check:
        return run_check()
    order, info = load_airports()
    if a.gate:
        return run_gate(order, info)
    if a.flag:
        return run_flag(order, info)
    return run_exposure(order, info)


if __name__ == "__main__":
    sys.exit(main())
