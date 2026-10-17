"""Session 115: a plausibility check of the IEM hourly temperatures at the 12 stage C airports (DECISIONS D109).

Flag and count only (D109.6). No raw or processed file is changed. No value is removed, replaced or
filled. No model is fitted. No error metric is computed with or without the flagged values. Nothing
valid after 2026-07-31T23:00 UTC is read. No network access.

Modes (one per run):
  --check     Synthetic self-checks of D109.4 (a) to (d), the exposure helpers and the date guard. No real
              value is read.
  --gate      Real data, no flag computed. The hourly series built here (the project's own reader, SPEC 8.8
              G2 and G3) must agree with the stage C tables' observations row by row, and with the D82.8
              days already on record (session 104's and session 107's day files), at every airport.
  --flag      D109.4 at the 12 airports (runs the gate first). Writes flags.csv and counts.csv.
  --exposure  D109.5 (runs the gate first, recomputes the flags and checks them against flags.csv). Writes
              exposure.csv, top_residuals.csv, out_of_range.csv and listing.txt.

Imported read only, each after its SHA-256 check (as session 112 does): scripts/session104_curve_cv.py
(F147) and scripts/session106_claim_look.py (F149, F150.4), and through them session 97. From
src/mlwx/observations.py: parse_reports, ReportSet (the nearest usable report within 15 minutes of each
whole hour, the first row of a repeated timestamp kept). From session 97: load_table, check_valid,
check_obs_time, GuardError, write_new, csv_text, parse_time, TABLES, LAST_VALID. From session 104:
load_table25, table25_hashes, local_day, usable_day, TZ. From session 106: tables_of, load_rows, CLAIM,
DEV_ICAO, the day files' paths and SHA-256 constants. New code here (no function existed): the four
checks, the hourly series builder (a loop over ReportSet.nearest), the raw GFS median, the gate's
comparisons, the exposure counts and the outputs.

Every output file is written once and never overwritten.
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


_SHA = {}


def sha256_file(path):
    key = str(path)
    if key not in _SHA:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for block in iter(lambda: f.read(1 << 20), b""):
                h.update(block)
        _SHA[key] = h.hexdigest()
    return _SHA[key]


S104_SCRIPT_SHA256 = "6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb"   # F147
S106_SCRIPT_SHA256 = "5e046acffc6eb28619d1883c8b93b6ff97bc3305addade56be5ab30af169281a"   # F149, F150.4
if sha256_file(HERE / "session104_curve_cv.py") != S104_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session104_curve_cv.py's SHA-256 is not F147's")
if sha256_file(HERE / "session106_claim_look.py") != S106_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session106_claim_look.py's SHA-256 is not F150.4's")
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "src"))
import session106_claim_look as s106  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import io  # noqa: E402

import numpy as np  # noqa: E402

from mlwx.observations import ReportSet, parse_reports, new_stats  # noqa: E402

s104 = s106.s104
s97 = s106.s97

# ------------------------------------------------------------------ constants (D109.4, fixed before any value was looked at)

RANGE_LOW = -60.0            # (a) out of range: below this or
RANGE_HIGH = 60.0            #     above this, degrees C
SPIKE_DELTA = 10.0           # (b) spike: differs by more than this, in the same direction
STUCK_MIN_RUN = 24           # (c) stuck sensor: this many consecutive hours or more with one value
RESIDUAL_LIMIT = 10.0        # (d) extreme residual: |observation minus raw GFS| above this
GFS_LEAD_MIN, GFS_LEAD_MAX = 3, 48     # (d) the stage C rows' leads used for raw GFS
DECIMALS = 6                 # differences are rounded to this many decimals before the comparison with a
#                              threshold, so that float noise cannot decide a tie (20.1 - 10.1 is exactly 10.0)

FIRST_VALID = dt.datetime(2021, 3, 24, 0, 0)      # D109.3
LAST_VALID = dt.datetime(2026, 7, 31, 23, 0)
SPLIT = dt.datetime(2024, 8, 1)                   # D109.5: before 2024-08-01 and from 2024-08-01
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)
N_HOURS = int((LAST_VALID - FIRST_VALID) / HOUR) + 1

OBS_PIECES = ["2021-03-24_2021-12-31", "2022-01-01_2022-12-31", "2023-01-01_2023-12-31",
              "2024-01-01_2024-12-31", "2025-01-01_2025-12-31", "2026-01-01_2026-07-31"]    # as session 96
RAW = ROOT / "data" / "raw"
OUT_DIR = ROOT / "data" / "processed" / "session115_obs_check"

CHECKS = ("a", "b", "c", "d")
CHECK_NAME = {"a": "out of range", "b": "spike", "c": "stuck sensor", "d": "extreme residual", "any": "union"}

# The 12 airports of D103.4: claim airports first, then the development airports (flagged in the group column).
CLAIM_ICAO = list(s106.CLAIM)                                   # EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN
DEV_ST = list(s97.STATIONS)                                     # EGLC, LFPG, DSM, YSDU, RNO, SFO
DEV_ICAO = [s106.DEV_ICAO[s] for s in DEV_ST]                   # EGLC, LFPG, KDSM, YSDU, KRNO, KSFO
AIRPORTS = CLAIM_ICAO + DEV_ICAO
IEM_ID = {**{ic: s106.CLAIM[ic][0] for ic in CLAIM_ICAO}, **{s106.DEV_ICAO[s]: s for s in DEV_ST}}
TZNAME = {**{ic: s106.CLAIM[ic][1] for ic in CLAIM_ICAO}, **{s106.DEV_ICAO[s]: s104.TZ[s] for s in DEV_ST}}
GROUP = {ic: ("claim" if ic in CLAIM_ICAO else "dev") for ic in AIRPORTS}
GuardError = s97.GuardError


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions():
    return f"python {sys.version.split()[0]}; numpy {np.__version__}"


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def tstr(t):
    return t.strftime("%Y-%m-%dT%H:%MZ")


# ------------------------------------------------------------------ the four checks (D109.4), on lists of value-or-None

def _gt(x, limit):
    """x is more than limit, after rounding x to DECIMALS places."""
    return round(x, DECIMALS) > limit


def check_a(vals):
    """(a) Out of range: below RANGE_LOW or above RANGE_HIGH."""
    return [v is not None and (v < RANGE_LOW or v > RANGE_HIGH) for v in vals]


def _at(vals, i):
    return vals[i] if 0 <= i < len(vals) else None


def check_b(vals):
    """(b) Spike. Returns (flag, untested_hours, untested_pairs, kind).

    One hour: hour i differs from both i-1 and i+1 by more than SPIKE_DELTA, in the same direction.
    Two hours: i and i+1 both differ from i-1 and from i+2 by more than SPIKE_DELTA, in the same direction.
    A missing neighbour (or the end of the series) means the test cannot be made: the hour (one-hour test)
    or the pair (two-hour test) is counted as untested and not flagged. untested_hours is a dict of counts:
    'prev' (i-1 missing), 'next' (i+1 missing), 'either' (at least one), for hours that have a value.
    kind[i] is '1h' or '2h' for flagged hours."""
    n = len(vals)
    flag = [False] * n
    kind = [""] * n
    unt = {"prev": 0, "next": 0, "either": 0}
    unt_pairs = 0
    for i in range(n):
        v = vals[i]
        if v is None:
            continue
        p, q = _at(vals, i - 1), _at(vals, i + 1)
        if p is None or q is None:
            unt["either"] += 1
            unt["prev"] += int(p is None)
            unt["next"] += int(q is None)
        else:
            up = _gt(v - p, SPIKE_DELTA) and _gt(v - q, SPIKE_DELTA)
            down = _gt(p - v, SPIKE_DELTA) and _gt(q - v, SPIKE_DELTA)
            if up or down:
                flag[i] = True
                kind[i] = "1h"
        # two-hour spike on the pair (i, i+1)
        w = _at(vals, i + 1)
        if w is None:
            continue
        p, r = _at(vals, i - 1), _at(vals, i + 2)
        if p is None or r is None:
            unt_pairs += 1
            continue
        up = all(_gt(x - y, SPIKE_DELTA) for x in (v, w) for y in (p, r))
        down = all(_gt(y - x, SPIKE_DELTA) for x in (v, w) for y in (p, r))
        if up or down:
            for j in (i, i + 1):
                if not flag[j]:
                    flag[j] = True
                    kind[j] = "2h"
    return flag, unt, unt_pairs, kind


def check_c(vals):
    """(c) Stuck sensor: a run of STUCK_MIN_RUN or more consecutive hours with the same value. A missing hour
    breaks the run. Returns (flag, run_length) where run_length[i] is the length of the run hour i is in
    (0 for a hour with no value)."""
    n = len(vals)
    flag = [False] * n
    run = [0] * n
    i = 0
    while i < n:
        if vals[i] is None:
            i += 1
            continue
        j = i
        while j + 1 < n and vals[j + 1] is not None and vals[j + 1] == vals[i]:
            j += 1
        length = j - i + 1
        for k in range(i, j + 1):
            run[k] = length
            flag[k] = length >= STUCK_MIN_RUN
        i = j + 1
    return flag, run


def gfs_median(values):
    """The median of the raw GFS values valid at one hour; None if there are none."""
    return float(np.median(np.asarray(values, dtype=float))) if values else None


def check_d(vals, gfs):
    """(d) Extreme residual: observation minus raw GFS above RESIDUAL_LIMIT in either direction. gfs[i] is the
    median raw GFS at hour i or None. Returns (flag, residual, untested) where untested counts hours that
    have a value and no raw GFS (counted, not flagged)."""
    n = len(vals)
    flag = [False] * n
    resid = [None] * n
    untested = 0
    for i in range(n):
        if vals[i] is None:
            continue
        if gfs[i] is None:
            untested += 1
            continue
        resid[i] = vals[i] - gfs[i]
        flag[i] = _gt(abs(resid[i]), RESIDUAL_LIMIT)
    return flag, resid, untested


def all_checks(vals, gfs):
    fa = check_a(vals)
    fb, unt_b, unt_pairs, kind = check_b(vals)
    fc, run = check_c(vals)
    fd, resid, unt_d = check_d(vals, gfs)
    union = [x or y or z or w for x, y, z, w in zip(fa, fb, fc, fd)]
    return {"a": fa, "b": fb, "c": fc, "d": fd, "any": union, "b_kind": kind, "run": run, "resid": resid,
            "unt_b": unt_b, "unt_pairs": unt_pairs, "unt_d": unt_d}


# ------------------------------------------------------------------ the hourly series (SPEC 8.8 G2 and G3)

def build_hourly(texts, iem_id):
    """One airport's hourly series, aligned to FIRST_VALID .. LAST_VALID (N_HOURS values, value or None).
    texts: the raw files' text. Every report's time passes the observation guard before any temperature is
    read (as session 96's load_obs); reports are parsed by the project's parse_reports; the value at a whole
    hour is ReportSet.nearest (the nearest usable report within 15 minutes inclusive; the first row of a
    repeated timestamp kept, the record's rule). Returns (values, stats)."""
    stats = new_stats()
    reports = []
    for text in texts:
        for r in csv.DictReader(io.StringIO(text)):
            s97.check_obs_time(dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M"))
        reports.extend(parse_reports(text, iem_id, stats))
    rs = ReportSet(reports, stats, live=False)
    values = []
    for k in range(N_HOURS):
        h = FIRST_VALID + k * HOUR
        s97.check_valid(h)
        values.append(rs.nearest(h)[0])
    return values, stats


def raw_files(iem_id):
    return [RAW / f"iem_asos_{iem_id}_{piece}_routine.csv" for piece in OBS_PIECES]


def load_series(ic):
    files = raw_files(IEM_ID[ic])
    texts = [f.read_text() for f in files]
    vals, stats = build_hourly(texts, IEM_ID[ic])
    return vals, stats, files


def hour_index(h):
    return int((h - FIRST_VALID) / HOUR)


# ------------------------------------------------------------------ the stage C rows

def table_files(ic):
    """[(path, SHA-256)] of the airport's two stage C table files, from the record's own loaders' constants."""
    if GROUP[ic] == "dev":
        st = IEM_ID[ic]
        return [(s97.STAGEC_DIR / s97.TABLES[st][0], s97.TABLES[st][1]),
                (s97.STAGEC_DIR / s104.TABLE25[st], s104.table25_hashes()[st])]
    _, _, tf = s106.tables_of(ic)
    return [(p, h) for p, h, _ in tf]


def table_rows(ic):
    """Both tables' rows (leads 0 to 48) by the record's loaders (the SHA-256 of each file is checked inside),
    reduced to (valid, lead, complete, obs, temp) to save memory. temp is temperature_grib_c, raw GFS after the
    elevation adjustment (SPEC 5.2, 8.8 G4)."""
    if GROUP[ic] == "dev":
        st = IEM_ID[ic]
        full = s97.load_table(st, leads=tuple(range(0, 25))) + s104.load_table25(st, s104.table25_hashes()[st])
    else:
        st, tz, tf = s106.tables_of(ic)
        full = s106.load_rows(*tf[0][:2], st, tf[0][2]) + s106.load_rows(*tf[1][:2], st, tf[1][2])
    return [(r[1], r[3], r[4], r[5], r[6]) for r in full]


def gfs_by_hour(rows):
    """Median elevation-adjusted raw GFS at each valid hour over the rows at leads 3 to 48, as a list aligned
    to the series (None where no row has a raw GFS value), and the count of values behind each median."""
    bucket = {}
    for valid, lead, complete, obs, temp in rows:
        if GFS_LEAD_MIN <= lead <= GFS_LEAD_MAX and temp is not None:
            bucket.setdefault(valid, []).append(temp)
    med = [None] * N_HOURS
    cnt = [0] * N_HOURS
    for valid, vs in bucket.items():
        k = hour_index(valid)
        if 0 <= k < N_HOURS:
            med[k] = gfs_median(vs)
            cnt[k] = len(vs)
    return med, cnt


# ------------------------------------------------------------------ daily maxima (D82.8)

def local_days(ic):
    """(date, UTC hours) of every local day lying wholly inside the series window."""
    out = []
    d = FIRST_VALID.date() - DAY
    while d <= LAST_VALID.date() + DAY:
        _, _, hours = s104.local_day(d, TZNAME[ic])
        if hours[0] >= FIRST_VALID and hours[-1] <= LAST_VALID:
            out.append((d, hours))
        d += DAY
    return out


def day_max(vals, hours):
    """(usable, max or None, the hours that attain it) for one local day (D82.8: usable hours at least the
    day's hours minus 2)."""
    got = [(h, vals[hour_index(h)]) for h in hours if vals[hour_index(h)] is not None]
    if not s104.usable_day(len(hours), len(got)):
        return False, None, []
    m = max(v for _, v in got)
    return True, m, [h for h, v in got if v == m]


# ------------------------------------------------------------------ the gate

def read_day_records():
    """The D82.8 days on record: {(airport key, local_date): obs_max or None}, from session 104's day file
    (development airports, key = station code) and session 107's (claim airports, key = ICAO), each after its
    SHA-256 check."""
    out = {}
    for p, want in ((s106.S104_DAYS, s106.S104_DAYS_SHA256), (s97.PROCESSED / "session107_claim_days.csv",
                                                              "3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297")):
        if sha256_file(p) != want:
            raise SystemExit(f"STOP: {p.name}'s SHA-256 is not the recorded value")
    with open(s106.S104_DAYS, newline="") as f:
        for r in csv.DictReader(f):
            out[(r["station"], r["local_date"])] = float(r["obs_max"]) if r["obs_max"] != "" else None
    with open(s97.PROCESSED / "session107_claim_days.csv", newline="") as f:
        for r in csv.DictReader(f):
            out[(r["icao"], r["local_date"])] = float(r["obs_max"]) if r["obs_max"] != "" else None
    return out


def gate_airport(ic, vals, rows, records):
    """Compare the series with the table rows and the day records. Returns a dict of counts."""
    key = IEM_ID[ic] if GROUP[ic] == "dev" else ic
    cover = {}                        # valid hour -> table obs (None allowed), from every row
    mism_rows = 0
    mism_examples = []
    for valid, lead, complete, obs, temp in rows:
        k = hour_index(valid)
        if not (0 <= k < N_HOURS):
            raise SystemExit(f"STOP: {ic}: a table row has valid time {tstr(valid)} outside the series window")
        if vals[k] != obs:
            mism_rows += 1
            if len(mism_examples) < 3:
                mism_examples.append(f"{tstr(valid)} table {obs} series {vals[k]}")
        cover.setdefault(k, obs)
    covered = set(cover)
    t_usable = sum(1 for k in covered if cover[k] is not None)
    s_usable = sum(1 for v in vals if v is not None)
    s_usable_covered = sum(1 for k in covered if vals[k] is not None)
    s_usable_outside = s_usable - s_usable_covered
    day_cmp = day_mism = day_missing = 0
    day_examples = []
    usable_days_rec = usable_days_ser = 0
    for d, hours in local_days(ic):
        rec_key = (key, d.isoformat())
        if rec_key not in records:
            continue
        ok, m, _ = day_max(vals, hours)
        rec = records[rec_key]
        day_cmp += 1
        usable_days_rec += int(rec is not None)
        usable_days_ser += int(ok)
        if (rec is None) != (not ok) or (rec is not None and rec != m):
            day_mism += 1
            if len(day_examples) < 3:
                day_examples.append(f"{d} record {rec} series {m if ok else None}")
    n_rec = sum(1 for (k, _) in records if k == key)
    day_missing = n_rec - day_cmp       # record days not inside the series window or not built here
    return {"series_hours": N_HOURS, "series_usable": s_usable, "covered_hours": len(covered),
            "table_usable_hours": t_usable, "series_usable_on_covered": s_usable_covered,
            "series_usable_outside": s_usable_outside, "row_mismatches": mism_rows, "row_examples": mism_examples,
            "days_on_record": n_rec, "days_compared": day_cmp, "days_not_compared": day_missing,
            "usable_days_record": usable_days_rec, "usable_days_series": usable_days_ser,
            "day_mismatches": day_mism, "day_examples": day_examples}


def gate_pass(g):
    return (g["row_mismatches"] == 0 and g["table_usable_hours"] == g["series_usable_on_covered"]
            and g["day_mismatches"] == 0 and g["days_not_compared"] == 0
            and g["usable_days_record"] == g["usable_days_series"])


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


def idx(flags):
    return [i for i, f in enumerate(flags) if f]


def run_check(args):
    c = Checker()
    base = [10.0] * 10
    print("(a) out of range")
    v = [0.0, -60.0, 60.0, -60.1, 60.1, None, 59.9]
    c.ok("-60.0 and 60.0 are not flagged; -60.1 and 60.1 are", idx(check_a(v)) == [3, 4])
    print("(b) spike")
    s = list(base); s[5] = 21.0
    fb, ub, up, kind = check_b(s)
    c.ok("a one-hour spike of +11.0 is flagged (that hour only), kind 1h", idx(fb) == [5] and kind[5] == "1h")
    s = list(base); s[5] = 20.0
    c.ok("a one-hour spike of exactly +10.0 is not flagged", idx(check_b(s)[0]) == [])
    s = list(base); s[5] = -1.0
    c.ok("a one-hour dip of -11.0 is flagged", idx(check_b(s)[0]) == [5])
    s = list(base); s[5] = s[6] = 21.0
    fb, ub, up, kind = check_b(s)
    c.ok("a two-hour spike of +11.0 is flagged at both hours, kind 2h", idx(fb) == [5, 6] and kind[5] == kind[6] == "2h")
    s = list(base); s[5] = s[6] = 20.0
    c.ok("a two-hour spike of exactly +10.0 is not flagged", idx(check_b(s)[0]) == [])
    s = list(base); s[5] = s[6] = -1.0
    c.ok("a two-hour dip of -11.0 is flagged at both hours", idx(check_b(s)[0]) == [5, 6])
    s = [10.0] * 5 + [25.0] * 5
    c.ok("a large step that does not reverse is not flagged", idx(check_b(s)[0]) == [])
    s = [10.0] * 4 + [21.0, 21.0, 21.0] + [10.0] * 3
    c.ok("a three-hour excursion is not flagged (the rule covers one or two hours)", idx(check_b(s)[0]) == [])
    s2 = [10.0, 10.0, 21.0, 15.0, 10.0]
    c.ok("a spike whose far neighbour differs by only 6.0 is not flagged (one-hour)", idx(check_b(s2)[0]) == [])
    s = list(base); s[5] = 21.0; s[4] = None
    fb, ub, up, kind = check_b(s)
    c.ok("a spike with a missing neighbour is not flagged and the hour is counted untested",
         idx(fb) == [] and ub["prev"] == 2 and ub["next"] == 2)     # the series ends count too (hours 0 and 9)
    s = [21.0] + [10.0] * 4
    fb, ub, up, kind = check_b(s)
    c.ok("the first hour (no h-1) is counted untested, not flagged", idx(fb) == [] and ub["prev"] == 1)
    s = [10.0, 21.0, 21.0, 10.0]
    c.ok("a pair at the very start of a 4-hour series is testable and flagged",
         idx(check_b(s)[0]) == [1, 2])
    s = [None, 21.0, 21.0, 10.0]
    fb, ub, up, kind = check_b(s)
    c.ok("a pair with h-1 missing, and the pair after it with h+2 off the series, are counted untested (2 pairs), "
         "not flagged", idx(fb) == [] and up == 2)
    s = list(base); s[5] = 20.1 - 0.0
    s[4] = s[6] = 10.1
    c.ok("20.1 against 10.1 is exactly 10.0 and not flagged (decimal-exact tie)", idx(check_b(s)[0]) == [])
    print("(c) stuck sensor")
    f, run = check_c([5.0] * 23)
    c.ok("a 23-hour run is not flagged", idx(f) == [] and run[0] == 23)
    f, run = check_c([5.0] * 24)
    c.ok("a 24-hour run is flagged at every hour, run length 24", idx(f) == list(range(24)) and run[10] == 24)
    f, run = check_c([4.0] + [5.0] * 25 + [6.0])
    c.ok("a 25-hour run among other values: its 25 hours flagged, run length 25",
         idx(f) == list(range(1, 26)) and run[5] == 25)
    f, run = check_c([5.0] * 12 + [None] + [5.0] * 12)
    c.ok("a run broken by a missing hour is not flagged (12 + missing + 12)", idx(f) == [])
    f, run = check_c([5.0] * 24 + [None] + [5.0] * 23)
    c.ok("24 hours then a missing hour then 23: only the first run flagged", idx(f) == list(range(24)))
    f, run = check_c([5.0] * 12 + [5.5] + [5.0] * 12)
    c.ok("a run broken by a different value is not flagged", idx(f) == [])
    print("(d) extreme residual")
    f, r, u = check_d([30.0, 30.001, 10.0, 9.999, None, 20.0], [20.0, 20.0, 20.0, 20.0, 20.0, None])
    c.ok("a residual of exactly +10.0 is not flagged; +10.001 is", not f[0] and f[1] and r[0] == 10.0 and r[1] > 10.0)
    c.ok("a residual of exactly -10.0 is not flagged; -10.001 is", not f[2] and f[3] and r[2] == -10.0)
    c.ok("an hour with a value and no raw GFS is counted untested, not flagged", u == 1 and not f[5])
    c.ok("a missing observation is neither flagged nor counted", f[4] is False and u == 1)
    c.ok("the median of 3 values is the middle one; of 4 is the mean of the middle two; of none is None",
         gfs_median([3.0, 1.0, 2.0]) == 2.0 and gfs_median([1.0, 2.0, 3.0, 10.0]) == 2.5 and gfs_median([]) is None)
    f, r, u = check_d([30.1], [20.1])
    c.ok("30.1 against 20.1 is exactly 10.0 and not flagged (decimal-exact tie)", idx(f) == [])
    print("union and flags together")
    vals = [10.0 + (i % 2) for i in range(30)]       # alternating, so no stuck run
    vals[3] = 80.0
    out = all_checks(vals, [10.0] * 30)
    c.ok("an hour of 80.0 carries (a), (b) and (d); the union counts it once",
         out["a"][3] and out["b"][3] and out["d"][3] and not out["c"][3] and sum(out["any"]) == 1)
    c.ok("union hours = hours with at least one flag", idx(out["any"]) == sorted(set(idx(out["a"])) | set(idx(out["b"]))
                                                                                 | set(idx(out["c"])) | set(idx(out["d"]))))
    print("date guard")
    try:
        s97.check_valid(dt.datetime(2026, 8, 1, 0, 0))
        refused = False
    except GuardError:
        refused = True
    c.ok("a valid time of 2026-08-01T00:00 is refused", refused)
    try:
        s97.check_valid(LAST_VALID)
        passes = True
    except GuardError:
        passes = False
    c.ok("a valid time of 2026-07-31T23:00 is accepted", passes)
    head = "station,valid,tmpc,dwpc,lat,lon,elevation\n"
    good = head + "XXXX,2026-07-31 23:00,10.0,5.0,0,0,0\n"
    bad = head + "XXXX,2026-07-31 23:00,10.0,5.0,0,0,0\nXXXX,2026-08-01 00:00,11.0,5.0,0,0,0\n"
    try:
        build_hourly([good], "XXXX")
        accepted = True
    except GuardError:
        accepted = False
    c.ok("the series builder accepts a file that ends at 2026-07-31T23:00", accepted)
    try:
        build_hourly([bad], "XXXX")
        refused = False
    except GuardError:
        refused = True
    c.ok("the series builder refuses a file with a report at 2026-08-01T00:00 before reading a temperature", refused)
    print("the hourly series on synthetic reports")
    rows = ["XXXX,2021-03-24 00:00,10.0,5.0,0,0,0", "XXXX,2021-03-24 00:50,11.0,5.0,0,0,0",
            "XXXX,2021-03-24 01:55,M,5.0,0,0,0", "XXXX,2021-03-24 02:16,12.0,5.0,0,0,0",
            "XXXX,2021-03-24 03:15,13.0,5.0,0,0,0", "XXXX,2021-03-24 03:15,14.0,5.0,0,0,0"]
    vals, st = build_hourly([head + "\n".join(rows) + "\n"], "XXXX")
    c.ok("a report at :00 is used; at :50 it goes to the next hour (01:00 gets 11.0)", vals[0] == 10.0 and vals[1] == 11.0)
    c.ok("a missing temperature (M) and a report 16 minutes out leave hours 02:00 and 03:00 handled by G2 and G3",
         vals[2] is None and vals[3] == 13.0)
    c.ok("a repeated timestamp keeps the first row, and is counted", vals[3] == 13.0 and st["duplicates"] == 1)
    print("exposure helpers")
    hours = [FIRST_VALID + k * HOUR for k in range(24)]
    series = [None] * N_HOURS
    for k in range(24):
        series[k] = 10.0
    series[7] = 20.0
    series[9] = 20.0
    ok, m, setters = day_max(series, hours)
    c.ok("a usable day's maximum is set by every hour that attains it", ok and m == 20.0 and setters == [hours[7], hours[9]])
    for k in range(3):
        series[k] = None
    ok, m, setters = day_max(series, hours)
    c.ok("a day with 3 hours missing of 24 is not usable (D82.8: at least hours minus 2)", not ok and m is None)
    series[0] = 10.0
    ok, m, setters = day_max(series, hours)
    c.ok("a day with 2 hours missing of 24 is usable", ok and m == 20.0)
    c.ok("hour_index maps the first hour to 0 and the last to N_HOURS - 1",
         hour_index(FIRST_VALID) == 0 and hour_index(LAST_VALID) == N_HOURS - 1)
    print(f"\n{c.n - c.fail} of {c.n} synthetic checks passed")
    print("ALL CHECKS PASSED" if c.fail == 0 else "A CHECK FAILED: STOP")
    return 0 if c.fail == 0 else 1


# ------------------------------------------------------------------ real-data runs

def load_all(want_flags_inputs=True):
    """Series, stats, raw files and table rows for the 12 airports."""
    data = {}
    for ic in AIRPORTS:
        vals, stats, files = load_series(ic)
        rows = table_rows(ic)
        gfs, ngfs = gfs_by_hour(rows)
        data[ic] = {"vals": vals, "stats": stats, "files": files, "rows": rows, "gfs": gfs, "ngfs": ngfs}
    return data


def run_gate_on(data):
    records = read_day_records()
    ok_all = True
    print(f"{'airport':6} {'usable':>7} {'covered':>8} {'t_usable':>8} {'s_on_cov':>8} {'s_outside':>9} {'row_mm':>6} "
          f"{'days':>5} {'rec_use':>7} {'ser_use':>7} {'day_mm':>6}  gate")
    gates = {}
    for ic in AIRPORTS:
        g = gate_airport(ic, data[ic]["vals"], data[ic]["rows"], records)
        gates[ic] = g
        p = gate_pass(g)
        ok_all = ok_all and p
        print(f"{ic:6} {g['series_usable']:7d} {g['covered_hours']:8d} {g['table_usable_hours']:8d} "
              f"{g['series_usable_on_covered']:8d} {g['series_usable_outside']:9d} {g['row_mismatches']:6d} "
              f"{g['days_on_record']:5d} {g['usable_days_record']:7d} {g['usable_days_series']:7d} "
              f"{g['day_mismatches']:6d}  {'PASS' if p else 'FAIL'}")
        for e in g["row_examples"] + g["day_examples"]:
            print(f"        example: {e}")
    print("GATE PASSED at 12 of 12 airports" if ok_all else "GATE FAILED: STOP")
    return ok_all, gates


def flags_of(data):
    return {ic: all_checks(data[ic]["vals"], data[ic]["gfs"]) for ic in AIRPORTS}


def meta_text(title, out_path, inputs, extra, header_rows=None):
    lines = [f"{title}", f"output {out_path.name}", f"run {now_utc()}; {versions()}",
             f"script scripts/{Path(__file__).name} SHA-256 {sha256_file(Path(__file__).resolve())}",
             "no network access; nothing valid after 2026-07-31T23:00 UTC read (D109.3); flag and count only (D109.6)",
             "", "inputs:"]
    lines += [f"  {n}  {h}" for n, h in inputs]
    lines += [""] + extra
    return "\n".join(lines) + "\n"


def input_list(data):
    ins = []
    for ic in AIRPORTS:
        for f in data[ic]["files"]:
            ins.append((f"data/raw/{f.name}", sha256_file(f)))
        for p, h in table_files(ic):
            ins.append((f"MLwx-stagec/{p.name} (SHA-256 checked by the record's loader against {h[:12]}...)", sha256_file(p)))
    return ins


def write_csv_and_meta(name, header, rows, title, data, extra):
    path = OUT_DIR / name
    text = s97.csv_text(header, rows)
    s97.write_new(path, text)
    ins = input_list(data) + []
    meta = meta_text(title, path, ins, [f"rows {len(rows)} (header excluded)", f"file SHA-256 {sha256_file(path)}"] + extra)
    s97.write_new(OUT_DIR / (name + ".meta.txt"), meta)
    return path


def check_outputs_absent(names):
    for n in names:
        for p in (OUT_DIR / n, OUT_DIR / (n + ".meta.txt")):
            if p.exists():
                raise SystemExit(f"STOP: {p} already exists; not overwriting it")


def prep_outdir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def rate(n, usable):
    return round(10000.0 * n / usable, 4) if usable else ""


def run_flag(args):
    check_outputs_absent(["flags.csv", "counts.csv"])
    data = load_all()
    ok, _ = run_gate_on(data)
    if not ok:
        return 1
    fl = flags_of(data)
    prep_outdir()
    frows, crows = [], []
    tot = {k: 0 for k in ("usable", "a", "b", "c", "d", "any", "unt_b", "unt_pairs", "unt_d")}
    for ic in AIRPORTS:
        vals, f = data[ic]["vals"], fl[ic]
        usable = sum(1 for v in vals if v is not None)
        for k in range(N_HOURS):
            if not f["any"][k]:
                continue
            frows.append([ic, IEM_ID[ic], GROUP[ic], tstr(FIRST_VALID + k * HOUR), fmt(vals[k]),
                          fmt(f["a"][k]), fmt(f["b"][k]), fmt(f["c"][k]), fmt(f["d"][k]),
                          f["b_kind"][k], fmt(vals[k - 2] if k >= 2 else None), fmt(vals[k - 1] if k >= 1 else None),
                          fmt(vals[k + 1] if k + 1 < N_HOURS else None), fmt(vals[k + 2] if k + 2 < N_HOURS else None),
                          f["run"][k] if f["c"][k] else "", fmt(data[ic]["gfs"][k]), data[ic]["ngfs"][k] or "",
                          fmt(f["resid"][k])])
        n = {c: sum(f[c]) for c in CHECKS + ("any",)}
        ub = f["unt_b"]
        tot["usable"] += usable
        for c in CHECKS + ("any",):
            tot[c] += n[c]
        tot["unt_b"] += ub["either"]
        tot["unt_pairs"] += f["unt_pairs"]
        tot["unt_d"] += f["unt_d"]
        crows += count_rows(ic, usable, n, f)
    crows += count_rows("ALL12", tot["usable"], {c: tot[c] for c in CHECKS + ("any",)},
                        {"unt_b": {"either": tot["unt_b"], "prev": "", "next": ""}, "unt_pairs": tot["unt_pairs"],
                         "unt_d": tot["unt_d"]})
    fh = ["airport", "iem_id", "group", "valid_utc", "value_c", "flag_a_out_of_range", "flag_b_spike", "flag_c_stuck",
          "flag_d_residual", "spike_kind", "value_h_minus_2", "value_h_minus_1", "value_h_plus_1", "value_h_plus_2",
          "run_length_c", "raw_gfs_median", "n_raw_gfs_values", "residual_obs_minus_gfs"]
    ch = ["airport", "group", "check", "usable_hours", "untested_hours", "untested_reason", "untested_pairs",
          "flagged_hours", "rate_per_10000_usable_hours"]
    common = ["thresholds: " + f"range {RANGE_LOW} to {RANGE_HIGH}; spike {SPIKE_DELTA}; stuck run {STUCK_MIN_RUN}; "
              f"residual {RESIDUAL_LIMIT}; differences rounded to {DECIMALS} decimals before the comparison",
              "development airports' group value is dev: their build choices used these folds (D106.3)"]
    write_csv_and_meta("flags.csv", fh, frows, "Session 115 flags.csv: one row per flagged hour (D109.4)", data, common)
    write_csv_and_meta("counts.csv", ch, crows, "Session 115 counts.csv: counts per airport and check (D109.4)", data, common)
    print(f"flags.csv: {len(frows)} flagged hours (union, 12 airports); counts.csv: {len(crows)} rows")
    print(f"{'airport':7}{'usable':>8}{'a':>6}{'b':>6}{'c':>7}{'d':>6}{'union':>7}")
    show = {}
    for r in crows:
        show.setdefault(r[0], {})[r[2]] = r
    for ic in AIRPORTS + ["ALL12"]:
        s = show[ic]
        print(f"{ic:7}{s['a'][3]:8d}{s['a'][7]:6d}{s['b'][7]:6d}{s['c'][7]:7d}{s['d'][7]:6d}{s['any'][7]:7d}")
    return 0


def count_rows(ic, usable, n, f):
    ub = f["unt_b"]
    reason_b = (f"a neighbour hour (h-1 or h+1) missing or off the series: h-1 {ub['prev']}, h+1 {ub['next']} "
                "(an hour can be in both)") if ub["prev"] != "" else "sum over airports"
    group = GROUP.get(ic, "all")
    rows = []
    for c in CHECKS:
        if c == "b":
            unt, why, pairs = ub["either"], reason_b, f["unt_pairs"]
        elif c == "d":
            unt, why, pairs = f["unt_d"], "no raw GFS value at that hour in the stage C rows at leads 3 to 48", ""
        else:
            unt, why, pairs = 0, "every hour with a value can be tested", ""
        rows.append([ic, group, c, usable, unt, why, pairs, n[c], rate(n[c], usable)])
    rows.append([ic, group, "any", usable, "", "union: an hour is counted once if any check flags it", "",
                 n["any"], rate(n["any"], usable)])
    return rows


def run_exposure(args):
    names = ["exposure.csv", "top_residuals.csv", "out_of_range.csv", "listing.txt"]
    check_outputs_absent(names)
    flags_path = OUT_DIR / "flags.csv"
    if not flags_path.exists():
        raise SystemExit("STOP: flags.csv does not exist; run --flag first")
    data = load_all()
    ok, _ = run_gate_on(data)
    if not ok:
        return 1
    fl = flags_of(data)
    # The recomputed flags must equal flags.csv.
    with open(flags_path, newline="") as fh:
        rec = {}
        for r in csv.DictReader(fh):
            rec.setdefault(r["airport"], set()).add(r["valid_utc"])
    for ic in AIRPORTS:
        mine = {tstr(FIRST_VALID + k * HOUR) for k in range(N_HOURS) if fl[ic]["any"][k]}
        if mine != rec.get(ic, set()):
            print(f"STOP: {ic}: the recomputed flagged hours differ from flags.csv")
            return 1
    print("recomputed flagged hours equal flags.csv at 12 of 12 airports")
    records = read_day_records()
    prep_outdir()
    xrows = []
    for ic in AIRPORTS:
        rows, vals, f = data[ic]["rows"], data[ic]["vals"], fl[ic]
        key = IEM_ID[ic] if GROUP[ic] == "dev" else ic
        tgt_hours, tgt_rows, cc_hours, cc_rows = {}, {}, {}, {}
        for valid, lead, complete, obs, temp in rows:
            if not (GFS_LEAD_MIN <= lead <= GFS_LEAD_MAX) or obs is None:
                continue
            k = hour_index(valid)
            per = 0 if valid < SPLIT else 1
            tgt_hours.setdefault(k, per)
            tgt_rows[k] = tgt_rows.get(k, 0) + 1
            if complete:
                cc_hours.setdefault(k, per)
                cc_rows[k] = cc_rows.get(k, 0) + 1
        days = []
        for d, hours in local_days(ic):
            usable, m, setters = day_max(vals, hours)
            if usable:
                days.append((d, [hour_index(h) for h in setters], (key, d.isoformat()) in records and records[(key, d.isoformat())] is not None))
        per_of_day = lambda d: 0 if d < SPLIT.date() else 1   # noqa: E731
        # denominators
        den = {"th": [0, 0], "tr": [0, 0], "ch": [0, 0], "cr": [0, 0], "d": [0, 0], "rd": [0, 0]}
        for k, per in tgt_hours.items():
            den["th"][per] += 1
            den["tr"][per] += tgt_rows[k]
        for k, per in cc_hours.items():
            den["ch"][per] += 1
            den["cr"][per] += cc_rows[k]
        for d, ks, onrec in days:
            den["d"][per_of_day(d)] += 1
            den["rd"][per_of_day(d)] += int(onrec)
        usable = sum(1 for k in range(N_HOURS) if vals[k] is not None)
        xrows.append(exp_row(ic, "all", usable, "", den))
        for c in CHECKS + ("any",):
            cnt = {"th": [0, 0], "tr": [0, 0], "ch": [0, 0], "cr": [0, 0], "d": [0, 0], "rd": [0, 0]}
            for k, per in tgt_hours.items():
                if f[c][k]:
                    cnt["th"][per] += 1
                    cnt["tr"][per] += tgt_rows[k]
            for k, per in cc_hours.items():
                if f[c][k]:
                    cnt["ch"][per] += 1
                    cnt["cr"][per] += cc_rows[k]
            for d, ks, onrec in days:
                if any(f[c][k] for k in ks):
                    cnt["d"][per_of_day(d)] += 1
                    cnt["rd"][per_of_day(d)] += int(onrec)
            xrows.append(exp_row(ic, c, usable, sum(f[c]), cnt))
    xh = ["airport", "group", "check", "usable_hours", "flagged_hours", "target_hours_before_2024_08_01", "target_hours_from_2024_08_01",
          "target_rows_before", "target_rows_from", "complete_case_target_hours_before", "complete_case_target_hours_from",
          "complete_case_target_rows_before", "complete_case_target_rows_from", "usable_days_whose_max_hour_is_flagged_before",
          "usable_days_whose_max_hour_is_flagged_from", "record_days_whose_max_hour_is_flagged_before",
          "record_days_whose_max_hour_is_flagged_from"]
    common = ["check 'all' rows hold the denominators: usable hours, target hours and rows, usable days, record days; the "
              "other rows hold the flagged counts in the same columns",
              "target = a stage C row at leads 3 to 48 with an observation; split by the row's valid time (days: local date)",
              "complete-case = the row's complete_case is true (it is used in fits and scores)",
              "usable day = D82.8 (usable hours at least the day's hours minus 2), every local day wholly inside the window; "
              "its maximum hour(s) = every hour that attains the day's maximum; record days = the days of session 104's and "
              "session 107's day files with a usable maximum"]
    write_csv_and_meta("exposure.csv", xh, xrows, "Session 115 exposure.csv (D109.5)", data, common)
    write_listing(data, fl)
    print(f"exposure.csv: {len(xrows)} rows")
    print(f"{'airport':7}{'flagged(any)':>13}{'tgt hrs <':>10}{'tgt hrs >=':>11}{'cc rows <':>10}{'cc rows >=':>11}{'days <':>7}{'days >=':>8}")
    for r in xrows:
        if r[2] == "any":
            print(f"{r[0]:7}{r[4]:13d}{r[5]:10d}{r[6]:11d}{r[11]:10d}{r[12]:11d}{r[13]:7d}{r[14]:8d}")
    return 0


def exp_row(ic, check, usable, flagged, cnt):
    return [ic, GROUP[ic], check, usable, flagged, cnt["th"][0], cnt["th"][1], cnt["tr"][0], cnt["tr"][1], cnt["ch"][0],
            cnt["ch"][1], cnt["cr"][0], cnt["cr"][1], cnt["d"][0], cnt["d"][1], cnt["rd"][0], cnt["rd"][1]]


def neighbours(vals, k):
    return [fmt(vals[j]) if 0 <= j < N_HOURS else "" for j in (k - 2, k - 1, k, k + 1, k + 2)]


def write_listing(data, fl):
    """top_residuals.csv (the 10 largest |residual| hours per airport) and out_of_range.csv (every out-of-range
    hour), each with the values at h-2 .. h+2, and listing.txt (the same, as text for the output file)."""
    top_rows, oor_rows, lines = [], [], []
    for ic in AIRPORTS:
        vals, resid, gfs, f = data[ic]["vals"], fl[ic]["resid"], data[ic]["gfs"], fl[ic]
        order = sorted((k for k in range(N_HOURS) if resid[k] is not None), key=lambda k: (-abs(resid[k]), k))[:10]
        lines.append(f"{ic} ({GROUP[ic]}): the 10 largest |residual| hours (obs minus median raw GFS); values at h-2, h-1, h, h+1, h+2")
        for rank, k in enumerate(order, 1):
            nb = neighbours(vals, k)
            flagged = "".join(c for c in CHECKS if f[c][k]) or "-"
            top_rows.append([ic, GROUP[ic], rank, tstr(FIRST_VALID + k * HOUR), fmt(vals[k]), fmt(gfs[k]), fmt(resid[k])] + nb +
                            [flagged])
            lines.append(f"  {rank:2d} {tstr(FIRST_VALID + k * HOUR)} obs {fmt(vals[k]):>7} gfs {gfs[k]:8.3f} resid {resid[k]:+8.3f} "
                         f"nbrs [{', '.join(nb)}] flags {flagged}")
        oor = [k for k in range(N_HOURS) if f["a"][k]]
        lines.append(f"{ic}: out-of-range hours: {len(oor)}")
        for k in oor:
            nb = neighbours(vals, k)
            oor_rows.append([ic, GROUP[ic], tstr(FIRST_VALID + k * HOUR), fmt(vals[k]), fmt(gfs[k]), fmt(resid[k])] + nb)
            lines.append(f"  {tstr(FIRST_VALID + k * HOUR)} obs {fmt(vals[k])} gfs {fmt(gfs[k])} nbrs [{', '.join(nb)}]")
        lines.append("")
    nbh = ["value_h_minus_2", "value_h_minus_1", "value_h", "value_h_plus_1", "value_h_plus_2"]
    common = ["descriptive only: no score of any kind (D109.6)"]
    write_csv_and_meta("top_residuals.csv", ["airport", "group", "rank", "valid_utc", "obs_c", "raw_gfs_median", "residual"]
                       + nbh + ["checks_flagged"], top_rows, "Session 115 top_residuals.csv (D109.5)", data, common)
    write_csv_and_meta("out_of_range.csv", ["airport", "group", "valid_utc", "obs_c", "raw_gfs_median", "residual"] + nbh,
                       oor_rows, "Session 115 out_of_range.csv (D109.5)", data, common)
    path = OUT_DIR / "listing.txt"
    text = "\n".join(lines) + "\n"
    s97.write_new(path, text)
    s97.write_new(OUT_DIR / "listing.txt.meta.txt", meta_text("Session 115 listing.txt (D109.5)", path, input_list(data),
                                                                  [f"file SHA-256 {sha256_file(path)}"] + common))


def run_gate(args):
    data = load_all()
    ok, _ = run_gate_on(data)
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--flag", action="store_true")
    g.add_argument("--exposure", action="store_true")
    a = ap.parse_args()
    if a.check:
        return run_check(a)
    if a.gate:
        return run_gate(a)
    if a.flag:
        return run_flag(a)
    return run_exposure(a)


if __name__ == "__main__":
    sys.exit(main())
