#!/usr/bin/env python3
"""Session 114: the curve against AIFS, the NBM grid, NBS and MAV on spent years, the official daily
maximum's gap, and the field guide (DECISIONS D107.9, D108). Offline except --docs.

Descriptive only (D107.2, D106.2): no verdict, model, setting, rule, bar or table changes, and nothing is
selected or tuned on these results. Nothing valid after 2026-07-31T23:00 UTC is read: every competitor valid
time and maximum window end passes session 113's guards on reading. Nothing from the 37 airports of F153.6
is read: every airport file is filtered to the 12 airports of D103.4 on reading. No IFS value exists yet
(D108.2); `--source ifs` stops until the owner's pull is there, and then runs unchanged (D108.7).

Modes (one per run; docs/sessions/session-114.md):
  --check            Step 2. Synthetic data only: pairing by valid time (NBS's one-hour-later runs too), the
                     civil local day and the local standard time day in summer and winter, the maximum-window
                     choice of D108.4(b) on made-up runs at each cycle hour, the elevation formula's sign and
                     size, F to C exact, the date guard, Benjamini-Hochberg.
  --gate             Step 2. Real data, no competitor value: (1) the loader reproduces session 112's curve and
                     raw GFS n and MAE, hourly and daily maximum, at 12 of 12 airports; (2) the bootstrap and
                     Diebold-Mariano functions, seed 112, reproduce dm_tests.csv's family 1 row at EDDM and EGLC
                     (session 112's generator is replayed draw by draw); (3) the elevation formula on GFS's own
                     recorded heights reproduces each airport's elevation constant to the record's 4 decimals.
  --match            Step 3. Paired rows and days per source, airport, test year, cycle hour and version;
                     unpaired ones counted by reason; cycle counts checked against F156.4. No error computed.
  --hourly --source S    Step 4. Hourly comparisons on the paired rows.
  --dailymax --source S  Step 5. Daily maximum comparisons (D98.10's days primary; every cycle descriptive).
  --docs             Step 6. Reads the NBM text documentation pages (the only network use) and records each
                     NBM version's TXN window in txn_windows.csv; fills match_counts.csv's TXN labels.
  --official         Step 6. The official maximum (CLI) at the four US airports (D108.4(d)).
  --figures          Step 7. The comparison figures, and Part 1 of ANALYSIS.md rendered from the tables.
  --verify           Step 7. Every number in ANALYSIS.md's Part 1 against its table (mismatches must be 0), and
                     no em-dash in Part 1. (Added to the prompt's list: the check needs its own run.)
S is aifs, nbm, nbs, mav or ifs.

Imported read only, each after its SHA-256 check: scripts/session112_analysis.py (F155) and
scripts/session113_comparison_pull.py (F156), and through session 112 sessions 104, 106 and 97. Used from
session 112: load_edges, load_airport, DayBuilder, scored_days, every_cycle_days, days_arrays, local_of, h_of,
dt_of, Sums, block_weights, ratio_interval, skill_interval, dm_test, benjamini_hochberg, metrics, plt_setup,
COLOR, INK, INK2, BANDS, SEASONS, SEASON_OF, PCTS, AIRPORTS, GROUP, TZNAME, STATION, SEA, DEV_FLAG, periods,
PRED_DIR, read_gz_csv, write_once_bytes, plain, fmt; from session 104 (through 112): local_day, usable_day,
day_cycle; from session 113: guard_valid, guard_window_end, climate_day_window, guard_climate_day, f_to_c,
test_year, get, LIMIT, OUT. New code (no function existed): the session 113 file readers with their SHA-256
checks, the competitor loaders and their elevation treatment, version labels, the step schedules, pairing by
valid time, the maximum-window choice, the comparison scoring and tables, the official-maximum gap, the
documentation reader for TXN, the gates' replay of session 112's generator, the figures and the Part 1
renderer and checker.

Random numbers: one generator, numpy default_rng(114), per run, used in a fixed order (airports in claim-first
order; within one, the headline per test year then pooled, then the breakdown cells, then the formal test).
Every output file is written once and never overwritten, except match_counts.csv's TXN label column, which
--docs fills (Step 3's "pending" labels, as the prompt asks).

No em-dashes in any text here (D76.6).
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


S112_SCRIPT_SHA256 = "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab"   # session 112's commit (F155)
S113_SCRIPT_SHA256 = "2023b0b017ffdfea63013924e43bdeae897f358cba5a4bd516f9663914dbb958"   # session 113's commit (F156)
if sha256_file(HERE / "session112_analysis.py") != S112_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session112_analysis.py's SHA-256 is not session 112's committed one")
if sha256_file(HERE / "session113_comparison_pull.py") != S113_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session113_comparison_pull.py's SHA-256 is not session 113's committed one")
sys.path.insert(0, str(HERE))
import session112_analysis as s112  # noqa: E402
import session113_comparison_pull as s113  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import html  # noqa: E402
import io  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

s104 = s112.s104
s106 = s112.s106
s97 = s112.s97

# ------------------------------------------------------------------ constants

PROCESSED = ROOT / "data" / "processed"
OUT_DIR = PROCESSED / "session114_comparisons"
FIG_DIR = s112.FIG_DIR                                   # figures/analysis/ (new files comparison_*.svg only)
S113 = s113.OUT                                          # data/processed/session113/ (read only)
S112_TABLES = PROCESSED / "session112_analysis"          # read only
ANALYSIS = ROOT / "ANALYSIS.md"

SEED = 114                                               # D107.9(e)
REPS_HEAD, REPS_CELL = s112.REPS_HEAD, s112.REPS_CELL    # 10,000 and 2,000
LAPSE_C_PER_KM = 7.429                                   # SPEC 5.2, 7.2 (frozen)
G0 = 9.80665                                             # geopotential to metres (D108.3)
LIMIT = s113.LIMIT                                       # 2026-07-31T23:00 UTC
HOUR = dt.timedelta(hours=1)
DAY = dt.timedelta(days=1)

AIRPORTS = s112.AIRPORTS                                 # claim airports first (D107.9(f))
GROUP = s112.GROUP
TZNAME = s112.TZNAME
SEA = s112.SEA
DEV_FLAG = s112.DEV_FLAG
SET = {ic: ("gfs" if GROUP[ic] == "dev" else "iem") for ic in AIRPORTS}     # D108.3: raw GFS's own position
TEST_YEAR = {"A": "2024-25", "B": "2025-26", "2023-24": "2023-24", "2024-25": "2024-25", "2025-26": "2025-26"}
US4 = ["KORD", "KDSM", "KRNO", "KSFO"]                   # claim airport first
NBM5 = ["KORD", "CYYZ", "KDSM", "KRNO", "KSFO"]


def tag(ic):
    return ic + ("" if GROUP[ic] == "claim" else " (dev)") + (" (sea)" if ic in SEA else "")


# Versions (labels only; descriptive segments, D107.5, D107.9(f)). Each entry: (label, first run time or None).
NBM_VERSIONS = [("v4.1", None), ("v4.2", dt.datetime(2024, 5, 15, 0)), ("v4.3", dt.datetime(2025, 5, 27, 12)),
                ("v5.0", dt.datetime(2026, 4, 30, 13)), ("v5.0.14", dt.datetime(2026, 7, 28, 12))]   # D77.7, F127.7
AIFS_VERSIONS = [("gpi 3", None), ("gpi 4", dt.datetime(2025, 8, 28, 0)), ("gpi 5", dt.datetime(2026, 5, 13, 0))]
IFS_VERSIONS = [("48r1", None), ("49r1", dt.datetime(2024, 11, 13, 0)), ("50r1", dt.datetime(2026, 5, 13, 0))]
MAV_VERSIONS = [("MAV", None)]

# Each source (D107.4, D107.5, D108.3, D108.4(b)).
SOURCES = {
    "aifs": dict(name="AIFS", kind="grid", airports=list(AIRPORTS), tparam="2t", maxparam=None,
                 first=dt.datetime(2025, 2, 25, 6), versions=AIFS_VERSIONS, daily="steps",
                 daily_label="highest of its own 6-hourly steps inside the local day (6-hourly steps; no maximum "
                             "field)", latency="aifs"),
    "ifs": dict(name="ECMWF IFS", kind="grid", airports=list(AIRPORTS), tparam="2t", maxparam="mx2t3",
                first=None, versions=IFS_VERSIONS, daily="steps",
                daily_label="highest of its own 3-hourly steps inside the local day (3-hourly steps)",
                second_label="mx2t3: highest of its 3-hour windows wholly inside the local day", latency="ifs"),
    "nbm": dict(name="NBM grid", kind="grid", airports=list(NBM5), tparam="TMP", maxparam="TMAX", first=None,
                versions=NBM_VERSIONS, daily="window",
                daily_label="TMAX: its 12-hour maximum, 12z to 00z UTC, from the same run",
                second_label="highest of its own steps inside the local day", latency="nbm"),
    "nbs": dict(name="NBS", kind="text", airports=list(NBM5), tparam="TMP", maxparam="TXN", first=None,
                versions=NBM_VERSIONS, daily="window",
                daily_label="TXN: its maximum, window per NBM version (txn_windows.csv)", latency="nbs"),
    "mav": dict(name="MAV", kind="text", airports=list(US4), tparam="TMP", maxparam="X", first=None,
                versions=MAV_VERSIONS, daily="window",
                daily_label="X: daytime maximum, 7 a.m. to 7 p.m. local standard time (MDL)", latency="mav"),
}
ORDER = ["aifs", "nbm", "nbs", "mav", "ifs"]

# F156.4: cycles with 2 m temperature kept per test year (2023-24, 2024-25, 2025-26); the loader must agree.
F156_4 = {
    "aifs": {ic: {"2024-25": 627, "2025-26": 1459} for ic in AIRPORTS},
    "nbm": {"KORD": {"2024-25": 1460, "2025-26": 1460}, "CYYZ": {"2024-25": 1460, "2025-26": 1460},
            **{ic: {"2023-24": 1464, "2024-25": 1460, "2025-26": 1460} for ic in ("KDSM", "KRNO", "KSFO")}},
    "nbs": {"KORD": {"2024-25": 1458, "2025-26": 1458}, "CYYZ": {"2024-25": 1458, "2025-26": 1456},
            "KDSM": {"2023-24": 1463, "2024-25": 1458, "2025-26": 1456},
            "KRNO": {"2023-24": 1462, "2024-25": 1458, "2025-26": 1458},
            "KSFO": {"2023-24": 1462, "2024-25": 1458, "2025-26": 1457}},
    "mav": {"KORD": {"2024-25": 1457, "2025-26": 1458},
            **{ic: {"2023-24": 1464, "2024-25": 1457, "2025-26": 1458} for ic in ("KDSM", "KRNO", "KSFO")}},
}

SAME_RUN = "same cycle"
LATER_RUN = "one hour more data"                          # D108.4(a): NBS 01/07/13/19 UTC runs, not adjusted
TXN_PENDING = "pending (Step 6)"


# ------------------------------------------------------------------ small helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def versions_text():
    import lightgbm
    import matplotlib
    return (f"python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lightgbm.__version__}; "
            f"matplotlib {matplotlib.__version__}")


def ptime(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")


h_of, dt_of, local_of = s112.h_of, s112.dt_of, s112.local_of


def version_of(table, run_time):
    lab = table[0][0]
    for v, t0 in table[1:]:
        if run_time >= t0:
            lab = v
    return lab


def elevation_correction(terrain_m, station_m):
    """D108.3, SPEC 5.2: 7.429 degrees C per km times (model terrain minus station elevation), held at 4
    decimals like GFS's own constant (D100.3(b))."""
    return round(LAPSE_C_PER_KM * (terrain_m - station_m) / 1000.0, 4)


def guard_valid_h(h):
    s113.guard_valid(dt_of(h))
    return h


_TABLES = []          # (name, rows, sha256) written this run


def write_table(name, header, rows):
    text = s97.csv_text(header, [[v if isinstance(v, str) else s112.fmt(s112.plain(v)) for v in r] for r in rows])
    s112.write_once_bytes(OUT_DIR / name, text.encode())
    _TABLES.append((name, len(rows), hashlib.sha256(text.encode()).hexdigest()))


def read_table(name, folder=None):
    with open((folder or OUT_DIR) / name, newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ session 113's files, with their SHA-256

_S113_HASH = {}


def s113_hashes():
    if not _S113_HASH:
        for meta in sorted(S113.glob("*_meta.txt")):
            for line in meta.read_text().splitlines():
                m = re.match(r"\s+(\S+\.(?:csv\.gz|csv))\s+([0-9a-f]{64})", line)
                if m:
                    _S113_HASH[m.group(1)] = m.group(2)
    return _S113_HASH


def read_s113(name):
    """Header and rows of a session 113 file. A file listed in a meta file must match its SHA-256; the
    positions files, probe.csv and latency.csv have none recorded (checked tracked and unchanged by git)."""
    p = S113 / name
    data = p.read_bytes()
    want = s113_hashes().get(name)
    if want is not None and hashlib.sha256(data).hexdigest() != want:
        raise SystemExit(f"STOP: {name}'s SHA-256 is not its meta file's")
    if name.endswith(".gz"):
        data = gzip.decompress(data)
    rd = csv.reader(io.StringIO(data.decode()))
    head = next(rd)
    return head, list(rd)


def read_s113_dicts(name, keep=None):
    head, rows = read_s113(name)
    out = []
    for r in rows:
        d = dict(zip(head, r))
        if keep is None or keep(d):
            out.append(d)
    return out


# ------------------------------------------------------------------ station elevations (D108.3)

def station_elevations():
    """Per airport: (station elevation the record uses for GFS's adjustment, GFS's model terrain there, the
    record's constant, where from). Development: Open-Meteo grid elevation and the interpolated GFS orography
    (session37/session76 params). Claim: IEM's elevation and model_height_m (session90_airports.csv)."""
    out = {}
    code = {s112.STATION[ic]: ic for ic in AIRPORTS if GROUP[ic] == "dev"}
    for f in ("data/raw/diagnostics/session37/session37_elevation_correction_params.csv",
              "data/raw/diagnostics/session76/session76_elevation_correction_params.csv"):
        with open(ROOT / f, newline="") as fh:
            for r in csv.DictReader(fh):
                ic = code[r["station"]]
                out[ic] = dict(station_m=float(r["om_grid_elev_m"]), terrain_m=float(r["orog_interp_m"]),
                               constant=float(r["correction_c"]), source=f)
    with open(PROCESSED / "session90_airports.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["icao"] in AIRPORTS and GROUP[r["icao"]] == "claim":      # filtered to the 12 on reading
                out[r["icao"]] = dict(station_m=float(r["elevation_m"]), terrain_m=float(r["model_height_m"]),
                                      height_diff_m=float(r["height_diff_m"]), constant=None,
                                      source="data/processed/session90_airports.csv")
    with open(ROOT / "src" / "mlwx" / "data" / "gfs_airports.csv", newline="") as fh:
        for r in csv.DictReader(fh):
            if r["icao"] in AIRPORTS:                                      # filtered to the 12 on reading
                out[r["icao"]]["config_constant"] = float(r["correction_c"])
    for ic in AIRPORTS:
        if out[ic]["constant"] is None:
            out[ic]["constant"] = out[ic]["config_constant"]
    return out


# ------------------------------------------------------------------ step schedules (expected steps per run)

def on_schedule(src, cyc_h, lead):
    """Is lead (hours from the nominal cycle) one of the source's own steps in leads 3 to 48?"""
    if not 3 <= lead <= 48:
        return False
    if src == "aifs":
        return lead % 6 == 0
    if src == "ifs":
        return lead % 3 == 0
    if src == "nbm":                                        # F156.5
        return lead <= 36 or lead % 3 == 0 or dt_of(cyc_h) >= dt.datetime(2026, 5, 5)
    return lead >= 6 and lead % 3 == 0                      # NBS and MAV: 3-hourly from 6 (probe.csv)


# ------------------------------------------------------------------ competitor loaders

class Comp:
    """One source at one airport. hv[(nominal cycle h, valid h)] = degrees C; cyc[nominal cycle h] =
    (run set, run time h, version, elevation label); mx and mx2 [nominal cycle h] = [(window start h,
    window end h, degrees C, definition)]; notes = counts from reading."""

    def __init__(self, src, ic):
        self.src, self.ic = src, ic
        self.hv, self.cyc, self.mx, self.mx2, self.notes = {}, {}, {}, {}, {}
        cfg = SOURCES[src]
        name = f"{src}_{ic}.csv.gz"
        if not (S113 / name).exists():
            raise SystemExit(f"STOP: {name} does not exist" + (": no IFS value exists yet; the owner's pull comes "
                                                                 "first (D108.2)" if src == "ifs" else ""))
        if cfg["kind"] == "grid":
            self._grid(cfg, name)
        else:
            self._text(cfg, name)

    def note(self, k, n=1):
        self.notes[k] = self.notes.get(k, 0) + n

    def _grid(self, cfg, name):
        src, ic = self.src, self.ic
        head, rows = read_s113(name)
        col = {c: i for i, c in enumerate(head)}
        pos = {}
        terr = {}
        if (S113 / f"{src}_terrain.csv").exists():
            for r in read_s113_dicts(f"{src}_terrain.csv", lambda d: d["airport"] == ic and d["position_set"] == SET[ic]):
                if r["h1_m"] != "":
                    terr[r["grid"]] = (ptime(r["cycle"]), [float(r[f"h{k}_m"]) for k in range(1, 5)])
        stn = station_elevations()[ic]["station_m"]
        elev = {}
        for r in rows:
            if r[col["position_set"]] != SET[ic]:
                continue
            grid = r[col["grid"]]
            if grid not in pos:
                pr = read_s113_dicts(f"positions_{grid}.csv",
                                     lambda d: d["airport"] == ic and d["position_set"] == SET[ic])
                if len(pr) != 1:
                    raise SystemExit(f"STOP: positions_{grid}.csv has {len(pr)} rows for {ic} {SET[ic]}")
                w = np.array([float(pr[0][f"p{k}_weight"]) for k in range(1, 5)])
                if abs(w.sum() - 1.0) > 1e-9:
                    raise SystemExit(f"STOP: {grid} {ic}: weights sum to {w.sum()}")
                pos[grid] = w
                if grid in terr:
                    hz = float(w @ np.array(terr[grid][1]))
                    elev[grid] = (elevation_correction(hz, stn), terr[grid][0], hz)
            w = pos[grid]
            cyc = ptime(r[col["cycle"]])
            valid = s113.guard_valid(ptime(r[col["valid_utc"]]))
            if r[col["units"]] != "K":
                raise SystemExit(f"STOP: {name}: units {r[col['units']]}, expected K")
            v = np.array([float(r[col[f"v{k}"]]) for k in range(1, 5)])
            if not np.all(np.isfinite(v)):
                self.note("value missing")
                continue
            val = float(w @ v) - 273.15
            if grid in elev:
                corr, tcyc, _ = elev[grid]
                val += corr
                elab = "elevation-adjusted" + (", terrain from a later date" if src == "ifs" and cyc < tcyc else "")
            else:
                elab = "no elevation treatment"
            c_h, v_h = h_of(cyc), h_of(valid)
            param = r[col["param"]]
            if c_h not in self.cyc:
                self.cyc[c_h] = (SAME_RUN, c_h, version_of(cfg["versions"], cyc), elab)
            if param == cfg["tparam"]:
                if (c_h, v_h) in self.hv:
                    raise SystemExit(f"STOP: {name}: two values at {cyc} {valid}")
                self.hv[(c_h, v_h)] = val
                self.note("2 m temperature values")
            elif param == cfg["maxparam"]:
                ws = ptime(r[col["window_start_utc"]])
                we = s113.guard_window_end(ptime(r[col["window_end_utc"]]))
                target = self.mx if src != "ifs" else self.mx2
                target.setdefault(c_h, []).append((h_of(ws), h_of(we), val, f"{param} {r[col['window_start_utc']]} "
                                                                             f"to {r[col['window_end_utc']]}"))
                self.note("maximum field values")
            else:
                self.note(f"other param {param}")
        self.elev_detail = {g: e for g, e in elev.items()}

    def _text(self, cfg, name):
        ic = self.ic
        head, rows = read_s113(name)
        col = {c: i for i, c in enumerate(head)}
        runs = {}
        for r in rows:
            runs.setdefault(r[col["nominal_cycle"]], set()).add((r[col["cycle"]], r[col["cycle_label"]]))
        keep = {}
        for nom, rs in runs.items():
            same = [x for x in rs if x[1] == "nominal"]
            if len(rs) > 1 and len(same) != 1:
                raise SystemExit(f"STOP: {name}: runs {sorted(rs)} for nominal cycle {nom}")
            keep[nom] = same[0][0] if same else next(iter(rs))[0]      # D107.9(a): the same cycle's run first
            if len(rs) > 1:
                self.note("nominal cycles with both runs: the same cycle's run used")
        for r in rows:
            nom = r[col["nominal_cycle"]]
            if r[col["cycle"]] != keep[nom]:
                self.note("values of a one-hour-later run not used (the same cycle's run exists)")
                continue
            c_h = h_of(ptime(nom))
            run = ptime(r[col["cycle"]])
            valid = s113.guard_valid(ptime(r[col["ftime_utc"]]))
            if r[col["value_c"]] == "":
                self.note("value missing")
                continue
            val = float(r[col["value_c"]])
            if val != s113.f_to_c(r[col["value_f"]]):
                raise SystemExit(f"STOP: {name}: value_c is not value_f converted exactly")
            if c_h not in self.cyc:
                self.cyc[c_h] = (SAME_RUN if run == ptime(nom) else LATER_RUN, h_of(run),
                                 version_of(cfg["versions"], run), "as issued (station forecast)")
            el = r[col["element"]]
            if el == cfg["tparam"]:
                self.hv[(c_h, h_of(valid))] = val
                self.note("2 m temperature values")
            elif el == cfg["maxparam"]:
                we = s113.guard_window_end(ptime(r[col["window_end_utc"]]))
                self.mx.setdefault(c_h, []).append((h_of(ptime(r[col["window_start_utc"]])), h_of(we), val,
                                                    r[col["definition"]]))
                self.note("maximum field values")
            else:
                self.note(f"other element {el}")

    def cycles_per_year(self):
        out = {}
        for c_h in self.cyc:
            if any((c_h, v) in self.hv for v in range(c_h + 3, c_h + 49)):
                ty = s113.test_year(dt_of(c_h))
                out[ty] = out.get(ty, 0) + 1
        return out


# ------------------------------------------------------------------ our side (session 112's loader)

_EDGES = []


class Ours:
    """One airport's regenerated predictions, references and observations (F155), by session 112's loader."""

    def __init__(self, ic):
        if not _EDGES:
            _EDGES.append(s112.load_edges())
        self.ic = ic
        self.A, _, self.obs = s112.load_airport(ic, _EDGES[0])
        self.S = self.A["scored"]
        self.db = s112.DayBuilder(ic, self.A, self.obs)
        self.ix = self.db.ix
        self._sd = self._ed = None
        if np.nanmax(self.A["valid"]) > h_of(LIMIT):
            raise SystemExit(f"STOP: {ic}: a prediction row is valid after {LIMIT}")

    @property
    def sdays(self):
        if self._sd is None:
            self._sd = s112.scored_days(self.ic, self.A, self.db)
        return self._sd

    @property
    def edays(self):
        if self._ed is None:
            self._ed = s112.every_cycle_days(self.ic, self.A, self.db)
        return self._ed

    def curve_at(self, c_h, hours, f="curve"):
        """Our forecast f from cycle c_h at the given valid hours (nan where none)."""
        vals = self.A[f]
        return [vals[self.ix[(c_h, h - c_h)]] if (c_h, h - c_h) in self.ix else math.nan for h in hours]


# ------------------------------------------------------------------ pairing (D108.4(a))

def pair_hourly(src, ours, comp):
    """Competitor value on every scored row of ours (nan if none), with the reason for each scored row without
    one, and the reason for each competitor value without a scored row of ours."""
    A, S = ours.A, ours.S
    n = len(A["cycle"])
    val = np.full(n, np.nan)
    why = np.full(n, "", dtype=object)
    first = SOURCES[src]["first"]
    first_h = h_of(first) if first else None
    for i in np.nonzero(S)[0]:
        c, v = int(A["cycle"][i]), int(A["valid"][i])
        x = comp.hv.get((c, v))
        if x is not None:
            val[i] = x
        elif first_h is not None and c < first_h:
            why[i] = "cycle before the source's first run"
        elif c not in comp.cyc:
            why[i] = "no run at this cycle"
        elif not on_schedule(src, c, v - c):
            why[i] = "valid time not one of the source's steps"
        else:
            why[i] = "step missing from the run"
    cwhy = {}
    for (c, v) in comp.hv:
        i = ours.ix.get((c, v - c))
        if i is None:
            k = "no row of ours at this cycle and lead (lead outside 3 to 48 or cycle outside the test years)"
        elif S[i]:
            continue
        else:
            k = "our row not scored (no observation or incomplete features)"
        cwhy[k] = cwhy.get(k, 0) + 1
    return val, why, cwhy


def choose_window(windows, d, tzname, c_h):
    """D108.4(b): the window (from the same run) whose start falls on local date d and that lies inside the
    run's leads 3 to 48. Returns (value, definition, None) or (None, None, reason)."""
    if windows is None:
        return None, None, "no run at this cycle"
    cand = [w for w in windows if local_of(dt_of(w[0]), tzname)[0] == d and w[0] - c_h >= 3 and w[1] - c_h <= 48]
    if not cand:
        return None, None, "no maximum window starting on this local date inside leads 3 to 48"
    if len(cand) > 1:
        return None, None, "more than one window starting on this local date"
    return cand[0][2], cand[0][3], None


def day_hours(ours, d):
    s, hours, hh = ours.db.local_day(d)
    return hh


def comp_day(src, ours, comp, r):
    """For one local day record r of session 112's DayBuilder (date, cycle): the competitor's maximum
    (primary), its second maximum, our curve sampled at its steps, its run set and version, and reasons."""
    d, c_h = r["date"], h_of(r["cycle"])
    hh = day_hours(ours, d)
    out = {"comp": math.nan, "comp2": math.nan, "curve_at": math.nan, "why": "", "why2": "", "def": "",
           "run": "", "version": "", "elab": "", "last_h": hh[-1]}
    info = comp.cyc.get(c_h)
    if info is not None:
        out["run"], out["version"], out["elab"] = info[0], info[2], info[3]
    steps = [h for h in hh if on_schedule(src, c_h, h - c_h)]
    have = [comp.hv.get((c_h, h)) for h in steps]
    steps_ok = info is not None and steps and all(x is not None for x in have)
    steps_max = max(have) if steps_ok else math.nan
    if steps:
        ca = ours.curve_at(c_h, steps)
        if steps_ok and all(np.isfinite(ca)):
            out["curve_at"] = max(ca)
    cfg = SOURCES[src]
    steps_reason = ("no run at this cycle" if info is None else "a step inside the day is missing from the run"
                    if steps else "no step inside the day")
    if cfg["daily"] == "steps":
        out["comp"] = steps_max
        out["why"] = "" if steps_ok else steps_reason
        if src == "ifs":
            v, dfn, why = subdaily_max(comp.mx2.get(c_h), hh)
            out["comp2"], out["why2"] = (v, "") if v is not None else (math.nan, why)
    else:
        v, dfn, why = choose_window(comp.mx.get(c_h), d, TZNAME[ours.ic], c_h)
        out["comp"], out["why"], out["def"] = (v, "", dfn) if v is not None else (math.nan, why, "")
        if src == "nbm":
            out["comp2"] = steps_max
            out["why2"] = "" if steps_ok else steps_reason
    return out


def subdaily_max(windows, hh):
    """IFS mx2t3 (descriptive): the highest of the 3-hour windows wholly inside the local day; the day must hold
    every such window of the run."""
    if windows is None:
        return None, None, "no run at this cycle"
    s, e = hh[0], hh[-1] + 1
    inside = [w for w in windows if w[0] >= s and w[1] <= e]
    if not inside:
        return None, None, "no 3-hour window inside the local day"
    return max(w[2] for w in inside), "mx2t3", None


def daily_records(src, ours, comp, which):
    """Day records (session 112's DayBuilder) for D98.10's days ('scored') or every cycle ('every'), each with
    the competitor's side added."""
    days = ours.sdays if which == "scored" else ours.edays
    out = []
    for r in days:
        x = dict(r)
        x.update(comp_day(src, ours, comp, r))
        out.append(x)
    return out


# ------------------------------------------------------------------ Step 2: --check (synthetic data only)

class FakeComp:
    """A made-up competitor for the self-checks."""

    def __init__(self, hv, cyc, mx=None):
        self.hv, self.cyc, self.mx, self.mx2 = hv, cyc, mx or {}, {}


class FakeOurs:
    """Made-up rows of ours: every cycle given, leads 3 to 48, all scored."""

    def __init__(self, cycles):
        cyc, lead = [], []
        for c in cycles:
            for n in range(3, 49):
                cyc.append(h_of(c))
                lead.append(n)
        cyc, lead = np.array(cyc), np.array(lead)
        self.A = {"cycle": cyc, "valid": cyc + lead, "lead": lead}
        self.S = np.ones(len(cyc), dtype=bool)
        self.ix = {(int(c), int(n)): i for i, (c, n) in enumerate(zip(cyc, lead))}


def run_check(args):
    print(f"SESSION 114 --check (synthetic data only; no table, prediction or competitor file read), start {now_utc()}")
    res = []

    def rec(name, ok, detail=""):
        res.append((name, bool(ok)))
        print(f"  {'PASS' if ok else 'FAIL'}  {name}" + (f": {detail}" if detail else ""))

    # (1) pairing by valid time, NBS's one-hour-later runs included
    c0 = dt.datetime(2025, 3, 1, 0)
    ours = FakeOurs([c0, c0 + 6 * HOUR])
    c0h = h_of(c0)
    hv = {(c0h, c0h + 6): 10.0, (c0h, c0h + 9): 11.0, (c0h, c0h + 49): 12.0}        # a later run (01z) on nominal 00z
    comp = FakeComp(hv, {c0h: (LATER_RUN, c0h + 1, "v4.2", "as issued")})
    val, why, cwhy = pair_hourly("nbs", ours, comp)
    i6, i5, i9 = ours.ix[(c0h, 6)], ours.ix[(c0h, 5)], ours.ix[(c0h, 9)]
    j6 = ours.ix[(c0h + 6, 6)]
    rec("pairing: a one-hour-later NBS run pairs by valid time with the nominal cycle",
        val[i6] == 10.0 and val[i9] == 11.0)
    rec("pairing: our lead 5 has no NBS step (3-hourly from 6) and is counted",
        np.isnan(val[i5]) and why[i5] == "valid time not one of the source's steps")
    rec("pairing: a cycle with no run is counted, not filled", np.isnan(val[j6]) and why[j6] == "no run at this cycle")
    rec("pairing: a competitor value at lead 49 has no row of ours and is counted",
        sum(cwhy.values()) == 1 and next(iter(cwhy)).startswith("no row of ours"))
    hv2 = {(c0h, c0h + 6): 1.0}
    val2, why2, _ = pair_hourly("nbs", ours, FakeComp(hv2, {c0h: (SAME_RUN, c0h, "v4.2", "")}))
    rec("pairing: a scheduled step absent from the run is counted as missing",
        why2[ours.ix[(c0h, 12)]] == "step missing from the run")
    # (2) local day and local standard time day, summer and winter
    s, e, hrs = s104.local_day(dt.date(2025, 7, 1), "America/Chicago")
    ls, le = s113.climate_day_window(dt.date(2025, 7, 1), "America/Chicago")
    rec("civil local day, summer (Chicago, CDT): 05Z to 05Z, 24 hours", s == dt.datetime(2025, 7, 1, 5) and len(hrs) == 24)
    rec("local standard time day, summer (Chicago): 06Z to 06Z", ls == dt.datetime(2025, 7, 1, 6) and le - ls == DAY)
    s, e, hrs = s104.local_day(dt.date(2025, 1, 15), "America/Chicago")
    ls, le = s113.climate_day_window(dt.date(2025, 1, 15), "America/Chicago")
    rec("winter (Chicago, CST): civil and standard days both 06Z to 06Z",
        s == ls == dt.datetime(2025, 1, 15, 6) and len(hrs) == 24)
    s, e, hrs = s104.local_day(dt.date(2025, 3, 9), "America/Chicago")
    ls, le = s113.climate_day_window(dt.date(2025, 3, 9), "America/Chicago")
    rec("clock-change day (Chicago, 2025-03-09): civil day 23 hours, standard day 24", len(hrs) == 23 and le - ls == DAY)
    s, e, hrs = s104.local_day(dt.date(2025, 7, 1), "America/Los_Angeles")
    ls, le = s113.climate_day_window(dt.date(2025, 7, 1), "America/Los_Angeles")
    rec("summer (Los Angeles, PDT): civil 07Z, standard 08Z", s == dt.datetime(2025, 7, 1, 7) and
        ls == dt.datetime(2025, 7, 1, 8))
    # (3) the maximum-window choice on made-up NBM-style runs at each cycle hour (KDSM, America/Chicago)
    tz = "America/Chicago"
    d0 = dt.date(2025, 7, 1)
    windows = {0: [(12, 24), (36, 48)], 6: [(6, 18), (30, 42)], 12: [(0, 12), (24, 36)], 18: [(18, 30)]}
    want = {(0, 0): 1, (0, 1): 2, (6, 0): 1, (6, 1): 2, (12, 0): None, (12, 1): 2, (18, 0): None, (18, 1): 1}
    ok = True
    detail = []
    for ch, ws in windows.items():
        c = dt.datetime(2025, 7, 1, ch)
        ch_h = h_of(c)
        runw = [(ch_h + a, ch_h + b, float(k + 1), f"w{k + 1}") for k, (a, b) in enumerate(ws)]
        for dd in (0, 1):
            v, dfn, why = choose_window(runw, d0 + dd * DAY, tz, ch_h)
            ok &= (v == want[(ch, dd)])
            detail.append(f"{ch:02d}z day+{dd}: {v if v is not None else why[:24]}")
    v, dfn, why = choose_window(None, d0, tz, h_of(dt.datetime(2025, 7, 1)))
    ok &= v is None and why == "no run at this cycle"
    rec("maximum window: start on the local date, inside leads 3 to 48, at each cycle hour", ok, "; ".join(detail))
    c18 = h_of(dt.datetime(2025, 7, 1, 18))
    mav = [(h_of(dt.datetime(2025, 7, 2, 13)), h_of(dt.datetime(2025, 7, 3, 1)), 30.0, "X")]
    v, _, _ = choose_window(mav, dt.date(2025, 7, 2), tz, c18)
    v2, _, why2 = choose_window(mav, dt.date(2025, 7, 2), tz, c18 + 6)
    rec("maximum window: a MAV X window (13Z to 01Z) is chosen from the 18z run and from the next 00z run",
        v == 30.0 and v2 == 30.0)
    late = [(c18 + 40, c18 + 52, 1.0, "X")]
    v3, _, why3 = choose_window(late, dt.date(2025, 7, 3), tz, c18)
    rec("maximum window: a window ending after lead 48 is not used, and counted", v3 is None and why3.startswith("no maximum"))
    # (4) the elevation formula: sign and size
    rec("elevation: terrain above the station warms (KRNO record: 1619.08 m over 1344 m gives +2.0436)",
        elevation_correction(1619.08, 1344.0) == 2.0436)
    rec("elevation: terrain below the station cools (100 m under 200 m gives -0.7429)",
        elevation_correction(100.0, 200.0) == -0.7429)
    rec("elevation: 1 km of difference gives 7.429 degrees C", elevation_correction(1000.0, 0.0) == 7.429)
    # (5) F to C exact
    pairs = [(32, 0.0), (212, 100.0), (-40, -40.0), (50, 10.0), (0, -160 / 9), (98, 330 / 9)]
    rec("F to C exact", all(s113.f_to_c(f) == c for f, c in pairs))
    # (6) the guard
    try:
        s113.guard_valid(LIMIT)
        guard_ok = True
    except s113.GuardError:
        guard_ok = False
    try:
        guard_valid_h(h_of(LIMIT) + 1)
        guard_ok = False
    except s113.GuardError:
        pass
    try:
        s113.guard_window_end(LIMIT + HOUR)
        guard_ok = False
    except s113.GuardError:
        pass
    rec("guard: 2026-07-31T23:00 accepted; 2026-08-01T00:00 refused (valid time and window end)", guard_ok)
    # (7) Benjamini-Hochberg
    r1 = s112.benjamini_hochberg([0.01, 0.04, 0.03, 0.005])
    r2 = s112.benjamini_hochberg([0.02, 0.03, 0.2])
    r3 = s112.benjamini_hochberg([0.04, 0.06, 0.5, 0.9])
    rec("Benjamini-Hochberg at 0.05: all four; step-up rejects 0.02 with 0.03; none of 0.04/0.06/0.5/0.9",
        list(r1) == [True] * 4 and list(r2) == [True, True, False] and not r3.any())
    # (8) version labels
    rec("versions: NBM v5.0 from the 13z run of 2026-04-30; the 12z run is v4.3",
        version_of(NBM_VERSIONS, dt.datetime(2026, 4, 30, 13)) == "v5.0" and
        version_of(NBM_VERSIONS, dt.datetime(2026, 4, 30, 12)) == "v4.3" and
        version_of(NBM_VERSIONS, dt.datetime(2024, 5, 14, 18)) == "v4.1")
    n_ok = sum(ok for _, ok in res)
    print(f"--check: {n_ok} of {len(res)} PASS")
    return 0 if n_ok == len(res) else 2


# ------------------------------------------------------------------ Step 2: --gate (real data, no competitor value)

def s112_draws(ours):
    """Every block_weights call session 112's --analyse made for one airport, in order: (n, reps, what).
    Restated from run_analyse (its loop is not a function); only the sizes matter for the generator."""
    ic, A, S = ours.ic, ours.A, ours.S
    E = {f: A["obs"] - A[f] for f in s112.FORECASTS}
    days_u, day_idx = np.unique(A["day"][S], return_inverse=True)
    nD = len(days_u)
    di = np.full(len(S), -1)
    di[np.nonzero(S)[0]] = day_idx
    plist = [p for p, _, _, _ in s112.periods(ic)]
    calls = []
    for p in plist + ["all"]:
        mp = S & ((A["period"] == p) if p != "all" else True)
        calls.append((len(np.unique(di[mp])), REPS_HEAD, f"hourly {p}"))
    calls.append((nD, REPS_CELL, "hourly breakdowns"))
    for fam, a, b in ((1, "curve", "raw_gfs"), (3, "curve", "linear_mos"), (4, "curve", "baseline")):
        m = S & np.isfinite(E[a]) & np.isfinite(E[b])
        keep = np.bincount(di[m], minlength=nD) > 0
        if not keep.all():
            calls.append((int(keep.sum()), REPS_HEAD, f"dm family {fam}"))
    D = s112.days_arrays(ours.sdays)
    common = np.isfinite(D["obs_max"]) & np.isfinite(D["raw_gfs"]) & np.isfinite(D["baseline"]) & \
        np.isfinite(D["curve"])
    dper = np.array(D["period"])
    for p in plist + ["all"]:
        mp = common & ((dper == p) if p != "all" else True)
        calls.append((int(mp.sum()), REPS_HEAD, f"daily {p}"))
    calls.append((int(common.sum()), REPS_CELL, "daily cells"))
    V = s112.days_arrays(ours.edays)
    vok = np.isfinite(V["obs_max"]) & np.isfinite(V["curve"]) & np.isfinite(V["raw_gfs"])
    vdates = np.unique(np.array([d.toordinal() for d in V["date"]])[vok])
    calls.append((len(vdates), REPS_CELL, "every cycle"))
    return calls, di, nD, E


def family1_row(ours, w_all, di, nD, E):
    S = ours.S
    m = S & np.isfinite(E["curve"]) & np.isfinite(E["raw_gfs"])
    dd = np.abs(E["curve"][m]) - np.abs(E["raw_gfs"][m])
    ds = np.bincount(di[m], weights=dd, minlength=nD)
    dc = np.bincount(di[m], minlength=nD)
    keep = dc > 0
    series = ds[keep] / dc[keep]
    z, pv = s112.dm_test(series)
    lo, hi = s112.ratio_interval(w_all, series[:, None], np.ones((nD, 1)))
    return [int(keep.sum()), int(m.sum()), float(series.mean()), float(lo[0]), float(hi[0]), z, pv]


def run_gate(args):
    t0 = time.time()
    print(f"SESSION 114 --gate (real data; no competitor value read), start {now_utc()}; {versions_text()}")
    hh = {(r["icao"], r["period"], r["forecast"]): r for r in read_table("hourly_headline.csv", S112_TABLES)}
    dh = {(r["icao"], r["period"], r["forecast"]): r for r in read_table("dailymax_headline.csv", S112_TABLES)}
    dm = {r["icao"]: r for r in read_table("dm_tests.csv", S112_TABLES) if r["family"] == "1"}
    ok1 = 0
    lines = []
    rng = np.random.default_rng(s112.SEED)
    targets = {"EDDM", "EGLC"}
    g2 = {}
    for ic in AIRPORTS:
        ours = Ours(ic)
        A, S = ours.A, ours.S
        good = True
        cells = 0
        plist = [p for p, _, _, _ in s112.periods(ic)]
        for p in plist + ["all"]:
            mp = S & ((A["period"] == p) if p != "all" else True)
            for f in ("curve", "raw_gfs"):
                e = (A["obs"] - A[f])[mp & np.isfinite(A[f])]
                mt = s112.metrics(e)
                rec = hh[(ic, p, f)]
                good &= rec["n"] == str(mt["n"]) and rec["mae"] == repr(mt["mae"])
                cells += 1
        D = s112.days_arrays(ours.sdays)
        common = np.isfinite(D["obs_max"]) & np.isfinite(D["raw_gfs"]) & np.isfinite(D["baseline"]) & \
            np.isfinite(D["curve"])
        dper = np.array(D["period"])
        for p in plist + ["all"]:
            mp = common & ((dper == p) if p != "all" else True)
            for f in ("curve", "raw_gfs"):
                e = (D["obs_max"] - D[f])[mp & np.isfinite(D[f])]
                mt = s112.metrics(e)
                rec = dh[(ic, p, f)]
                good &= rec["n"] == str(mt["n"]) and rec["mae"] == repr(mt["mae"])
                cells += 1
        ok1 += good
        lines.append(f"  gate 1 {tag(ic)}: {cells} cells (curve and raw GFS, n and MAE, hourly and daily maximum, per "
                     f"test year and pooled): {'equal' if good else 'DIFFERENT'}")
        # gate 2: replay session 112's generator through this airport's draws
        calls, di, nD, E = s112_draws(ours)
        for n, reps, what in calls:
            w = s112.block_weights(rng, n, reps)
            if ic in targets and what == "hourly all":
                got = family1_row(ours, w, di, nD, E)
                want = dm[ic]
                keys = ["days", "rows", "mean_daily_diff", "lo", "hi", "dm_stat", "p_value"]
                eq = [want[k] == (str(v) if isinstance(v, int) else repr(float(v))) for k, v in zip(keys, got)]
                g2[ic] = (all(eq), dict(zip(keys, got)), [k for k, e in zip(keys, eq) if not e])
        print(f"  {ic}: loaded and checked ({time.time() - t0:.0f} s)")
    for ln in lines:
        print(ln)
    print(f"gate 1: {ok1} of 12 airports reproduce session 112 exactly: {'PASS' if ok1 == 12 else 'FAIL'}")
    for ic in sorted(g2, key=AIRPORTS.index):
        eq, got, bad = g2[ic]
        print(f"gate 2 {tag(ic)}: dm_tests.csv family 1: days {got['days']}, rows {got['rows']}, mean daily difference "
              f"{got['mean_daily_diff']:+.6f} [{got['lo']:+.6f}, {got['hi']:+.6f}], DM {got['dm_stat']:.4f}, p "
              f"{got['p_value']:.3e}: {'all 7 fields equal' if eq else 'DIFFERENT: ' + ', '.join(bad)}")
    g2ok = len(g2) == 2 and all(v[0] for v in g2.values())
    print(f"gate 2: {'PASS' if g2ok else 'FAIL'} (seed 112, session 112's draws replayed in order)")
    el = station_elevations()
    ok3 = 0
    for ic in AIRPORTS:
        e = el[ic]
        if e.get("station_m") is None or e.get("constant") is None:
            raise SystemExit(f"STOP: {ic} has no station elevation or constant")
        got = elevation_correction(e["terrain_m"], e["station_m"])
        raw = LAPSE_C_PER_KM * (e["terrain_m"] - e["station_m"]) / 1000.0
        # The record's rounding: the constant is held at 4 decimals; at the development airports the record keeps
        # the model terrain at 2 decimals only (the constant was made from the unrounded value; the station
        # elevation is a whole number), so their gap carries up to 0.005 m of rounding. Claim airports' heights
        # are at full precision, so there the 4-decimal constant must be equal.
        tol = 0.5e-4 + (LAPSE_C_PER_KM * 0.005 / 1000.0 if GROUP[ic] == "dev" else 0.0)
        good = abs(raw - e["constant"]) <= tol + 1e-12 and e["constant"] == e["config_constant"] and \
            (GROUP[ic] == "dev" or got == e["constant"])
        ok3 += good
        print(f"  gate 3 {tag(ic)}: terrain {e['terrain_m']:.4f} m, station {e['station_m']:.2f} m -> {raw:+.6f} "
              f"({got:+.4f} at 4 decimals); record {e['constant']:+.4f}, config {e['config_constant']:+.4f}; "
              f"|difference| {abs(raw - e['constant']):.6f} within {tol:.6f}: {'yes' if good else 'NO'}")
    print(f"gate 3: {ok3} of 12 airports: {'PASS' if ok3 == 12 else 'FAIL'}")
    allok = ok1 == 12 and g2ok and ok3 == 12
    print(f"--gate: {'PASS' if allok else 'FAIL'} ({time.time() - t0:.0f} s)")
    return 0 if allok else 2


# ------------------------------------------------------------------ Step 3: --match (no error computed)

MATCH_COLS = ["source", "icao", "group", "test_year", "cycle_hour", "version", "run_set", "output", "item", "count",
              "txn_window"]


def day_reason(src, x):
    """Why a day record has no pair (or '' if paired)."""
    first = SOURCES[src]["first"]
    if x["last_h"] > h_of(LIMIT):
        return "day ends after 2026-07-31T23:00 UTC (nothing after it is read)"
    if not np.isfinite(x["comp"]):
        if first is not None and x["cycle"] < first:
            return "cycle before the source's first run"
        return x["why"] or "no value"
    if x["obs_max"] is None:
        return "observed maximum not usable (D82.8)"
    if x["curve"] is None or x["raw_gfs"] is None:
        return "curve or raw GFS maximum missing"
    return ""


def is_paired_day(x):
    return np.isfinite(x["comp"]) and x["obs_max"] is not None and x["curve"] is not None and \
        x["raw_gfs"] is not None


def run_match(args):
    t0 = time.time()
    print(f"SESSION 114 --match (pairs counted; no error computed), start {now_utc()}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    srcs = [s_ for s_ in ORDER if s_ != "ifs" or (S113 / "ifs_meta.txt").exists()]
    counts = {}
    loaded = {}
    stops = []
    summary = []
    notes = []

    def add(key, n=1):
        counts[key] = counts.get(key, 0) + n

    ours_cache = {}
    for src in srcs:
        cfg = SOURCES[src]
        for ic in cfg["airports"]:
            ours = ours_cache.get(ic) or ours_cache.setdefault(ic, Ours(ic))
            comp = Comp(src, ic)
            cy = comp.cycles_per_year()
            want = F156_4.get(src, {}).get(ic)
            if want is not None and cy != want:
                stops.append(f"{src} {ic}: cycles per test year {cy} differ from F156.4's {want}")
            notes.append(f"{src} {ic}: cycles with 2 m temperature per test year {cy} (F156.4: {want}); "
                         f"read: {comp.notes}")
            A, S = ours.A, ours.S
            val, why, cwhy = pair_hourly(src, ours, comp)
            ty = np.array([TEST_YEAR[p_] for p_ in A["period"]])
            for i in np.nonzero(S)[0]:
                c = int(A["cycle"][i])
                info = comp.cyc.get(c)
                ver = info[2] if info else ""
                run = info[0] if info else ""
                item = "paired" if np.isfinite(val[i]) else "unpaired: " + why[i]
                add((src, ic, GROUP[ic], ty[i], int(A["ch"][i]), ver, run, "hourly", item))
            for k, n in cwhy.items():
                add((src, ic, GROUP[ic], "", "", "", "", "hourly", "competitor value unpaired: " + k), n)
            n_pairs = int(np.isfinite(val).sum())
            dd = {}
            for which, label in (("scored", "daily max, D98.10 days"), ("every", "daily max, every cycle")):
                recs = daily_records(src, ours, comp, which)
                np_ = 0
                for x in recs:
                    rs = day_reason(src, x)
                    np_ += rs == ""
                    add((src, ic, GROUP[ic], TEST_YEAR[x["period"]], x["cycle"].hour, x["version"], x["run"], label,
                         "paired" if rs == "" else "unpaired: " + rs))
                dd[which] = np_
            # F156.4 shows coverage in these test years: pairs must exist in each
            for ty_, ncy in (want or cy).items():
                if ncy > 0:
                    got = sum(v for k, v in counts.items() if k[0] == src and k[1] == ic and k[3] == ty_ and
                              k[7] == "hourly" and k[8] == "paired")
                    gotd = sum(v for k, v in counts.items() if k[0] == src and k[1] == ic and k[3] == ty_ and
                               k[7] == "daily max, D98.10 days" and k[8] == "paired")
                    if got == 0 or gotd == 0:
                        stops.append(f"{src} {ic} {ty_}: F156.4 shows {ncy} cycles but paired rows {got}, days {gotd}")
            summary.append(f"  {src:4s} {tag(ic):18s} paired hourly rows {n_pairs:7,d}; paired days: D98.10 "
                           f"{dd['scored']:5,d}, every cycle {dd['every']:5,d}")
            print(summary[-1] + f"  ({time.time() - t0:.0f} s)")
    rows = []
    for k in sorted(counts, key=lambda k: (ORDER.index(k[0]), AIRPORTS.index(k[1]), k[3], str(k[4]), k[5], k[6],
                                           k[7], k[8])):
        txn = TXN_PENDING if k[0] == "nbs" and k[7].startswith("daily") else ""
        rows.append(list(k[:4]) + [str(k[4]), k[5], k[6], k[7], k[8], counts[k], txn])
    write_table("match_counts.csv", MATCH_COLS, rows)
    for n_ in notes:
        print("  " + n_)
    for st in stops:
        print("STOP: " + st)
    print(f"match_counts.csv: {len(rows)} rows; {_TABLES[-1][2]}")
    print(f"--match: {'PASS' if not stops else 'FAIL'} ({time.time() - t0:.0f} s)")
    return 0 if not stops else 2


# ------------------------------------------------------------------ scoring (D106.5, D106.12, D107.9(e), D108.4(e))

HEAD_COLS = ["source", "icao", "group", "test_year", "forecast", "n", "mae", "mae_lo", "mae_hi", "mean_error", "me_lo",
             "me_hi", "rmse", "share_abs_le1", "share_abs_le2", "latency"]
SKILL_COLS = ["source", "icao", "group", "test_year", "a", "b", "n", "skill_a_vs_b", "lo", "hi"]
BRK_COLS = ["source", "icao", "group", "condition", "bin", "forecast", "n", "mae", "mae_lo", "mae_hi", "mean_error",
            "me_lo", "me_hi", "skill_curve_vs_competitor", "skill_lo", "skill_hi"]
DM_COLS = ["source", "family", "icao", "group", "a", "b", "output", "days", "units", "mean_daily_diff", "lo", "hi",
           "dm_stat", "p_value", "bh_reject_q005"]


def boot_block(rng, day_keys, union, reps, cells, pairs):
    """One block bootstrap (F125.3's method, 7-day blocks) over the days present in `union`. cells: [(key, mask,
    err)] -> MAE and mean error intervals; pairs: [(key, mask, err_a, err_b)] -> skill 1 - MAE_a / MAE_b
    intervals, a and b resampled together."""
    u, inv = np.unique(day_keys[union], return_inverse=True)
    idx = np.zeros(len(day_keys), dtype=np.int64)
    idx[np.nonzero(union)[0]] = inv
    nd = len(u)
    if nd == 0:
        return {}, 0, None
    sm = s112.Sums(idx, nd)
    for k, m, e in cells:
        sm.add(("f",) + k, m, e)
    for k, m, ea, eb in pairs:
        sm.add(("a",) + k, m, ea)
        sm.add(("b",) + k, m, eb)
    w = s112.block_weights(rng, nd, reps)
    ma, me, mc = sm.mats()
    lo_a, hi_a = s112.ratio_interval(w, ma, mc)
    lo_e, hi_e = s112.ratio_interval(w, me, mc)
    K = {k: j for j, k in enumerate(sm.keys)}
    res = {}
    for k, m, e in cells:
        j = K[("f",) + k]
        res[("f",) + k] = (float(lo_a[j]), float(hi_a[j]), float(lo_e[j]), float(hi_e[j]))
    for k, m, ea, eb in pairs:
        a, b = K[("a",) + k], K[("b",) + k]
        lo, hi = s112.skill_interval(w, ma[:, [a]], ma[:, [b]])
        res[("s",) + k] = (float(lo[0]), float(hi[0]))
    return res, nd, (w, u)


def skill_of(ea, eb):
    return 1.0 - float(np.mean(np.abs(ea))) / float(np.mean(np.abs(eb)))


def score_set(src, ic, rng, X, forecasts, pairs, conds, dm_pair, latency):
    """Headline per test year and pooled (10,000 resamples), breakdown cells (2,000) and the formal test's daily
    series, on the paired set X["P"]. X: day (bootstrap unit key), ty (test year), P (paired), E (errors)."""
    E, P = X["E"], X["P"]
    head, skill, brk = [], [], []
    tys = [t for t in ("2023-24", "2024-25", "2025-26") if (P & (X["ty"] == t)).any()]
    w_all = None
    for ty in tys + ["all"]:
        U = P & ((X["ty"] == ty) if ty != "all" else True)
        cells = [((f,), U & np.isfinite(E[f]), E[f]) for f in forecasts]
        prs = [((a, b), U & np.isfinite(E[a]) & np.isfinite(E[b]), E[a], E[b]) for a, b in pairs]
        res, nd, wu = boot_block(rng, X["day"], U, REPS_HEAD, cells, prs)
        for f in forecasts:
            m = U & np.isfinite(E[f])
            mt = s112.metrics(E[f][m])
            lo_a, hi_a, lo_e, hi_e = res.get(("f", f), (None,) * 4)
            head.append([src, ic, GROUP[ic], ty, f, mt["n"], mt["mae"], lo_a, hi_a, mt["me"], lo_e, hi_e, mt["rmse"],
                         mt["le1"], mt["le2"], latency])
        for a, b in pairs:
            m = U & np.isfinite(E[a]) & np.isfinite(E[b])
            sk = skill_of(E[a][m], E[b][m]) if m.any() else None
            lo, hi = res.get(("s", a, b), (None, None))
            skill.append([src, ic, GROUP[ic], ty, a, b, int(m.sum()), sk, lo, hi])
        if ty == "all":
            w_all = wu
    cells, prs, order = [], [], []
    for cond, (lab, bins) in conds.items():
        for b in bins:
            mb = P & (lab == b)
            if not mb.any():
                continue
            order.append((cond, b))
            for f in forecasts:
                cells.append(((cond, b, f), mb & np.isfinite(E[f]), E[f]))
            prs.append(((cond, b), mb & np.isfinite(E["curve"]) & np.isfinite(E["comp"]), E["curve"], E["comp"]))
    res = boot_block(rng, X["day"], P, REPS_CELL, cells, prs)[0] if cells else {}
    for cond, b in order:
        mb = P & (conds[cond][0] == b)
        mp = mb & np.isfinite(E["curve"]) & np.isfinite(E["comp"])
        sk = skill_of(E["curve"][mp], E["comp"][mp]) if mp.any() else None
        slo, shi = res.get(("s", cond, b), (None, None))
        for f in forecasts:
            m = mb & np.isfinite(E[f])
            if not m.any():
                continue
            lo_a, hi_a, lo_e, hi_e = res[("f", cond, b, f)]
            brk.append([src, ic, GROUP[ic], cond, b, f, int(m.sum()), float(np.mean(np.abs(E[f][m]))), lo_a, hi_a,
                        float(np.mean(E[f][m])), lo_e, hi_e, sk if f == "comp" else "", slo if f == "comp" else "",
                        shi if f == "comp" else ""])
    a, b = dm_pair
    m = P & np.isfinite(E[a]) & np.isfinite(E[b])
    dd = np.abs(E[a][m]) - np.abs(E[b][m])
    u, inv = np.unique(X["day"][m], return_inverse=True)
    series = np.bincount(inv, weights=dd) / np.bincount(inv)
    z, pv = s112.dm_test(series)
    w, uw = w_all
    if len(uw) == len(u) and np.array_equal(uw, u):
        lo, hi = s112.ratio_interval(w, series[:, None], np.ones((len(u), 1)))
    else:
        ww = s112.block_weights(rng, len(u), REPS_HEAD)
        lo, hi = s112.ratio_interval(ww, series[:, None], np.ones((len(u), 1)))
    dm = [len(u), int(m.sum()), float(series.mean()), float(lo[0]), float(hi[0]), z, pv]
    return head, skill, brk, dm


def latency_text(src):
    rows = read_s113_dicts("latency.csv")
    by = {}
    for r in rows:
        by.setdefault(r["source"], []).append(r)
    key = {"aifs": "aifs", "ifs": "ifs", "nbm": "nbm", "nbs": "nbs", "mav": "mav"}[src]

    def one(k):
        rs = by.get(k, [])
        med = [float(r["median_h"]) for r in rs if r["median_h"]]
        if not med:
            return rs[0]["label"] if rs else "not recorded"
        return (f"archive write time minus cycle, median {min(med):.2f} to {max(med):.2f} h over the cycle hours "
                f"(range {min(float(r['min_h']) for r in rs):.2f} to {max(float(r['max_h']) for r in rs):.2f}); "
                f"may be later than public release")
    return f"{SOURCES[src]['name']}: {one(key)}. GFS: {one('gfs')}. Not adjusted for (D108.4(f))"


def finish_family(rows):
    """Benjamini-Hochberg at 0.05 across the airports of one family (D108.4(e))."""
    rej = s112.benjamini_hochberg([r[-1] for r in rows])
    return [r + [bool(x)] for r, x in zip(rows, rej)]


def cond_bins(src):
    vers = [v for v, _ in SOURCES[src]["versions"]]
    return vers


# ------------------------------------------------------------------ Step 4: --hourly

H_FORECASTS = ["comp", "curve", "raw_gfs", "linear_mos"]
H_PAIRS = [("curve", "comp"), ("raw_gfs", "comp"), ("linear_mos", "comp"), ("comp", "raw_gfs")]


def run_hourly(args):
    src = args.source
    t0 = time.time()
    cfg = SOURCES[src]
    print(f"SESSION 114 --hourly --source {src} ({cfg['name']}; descriptive, D107.2), start {now_utc()}; "
          f"{versions_text()}; seed {SEED}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    lat = latency_text(src)
    print("  latency: " + lat)
    H, SK, BR, DMR = [], [], [], []
    for ic in cfg["airports"]:
        ours = Ours(ic)
        comp = Comp(src, ic)
        val, why, _ = pair_hourly(src, ours, comp)
        A, S = ours.A, ours.S
        ix = np.nonzero(S)[0]
        obs = A["obs"][ix]
        cyc = A["cycle"][ix].astype(np.int64)
        info = [comp.cyc.get(int(c)) for c in cyc]
        X = {"day": A["day"][ix].astype(np.int64), "ty": np.array([TEST_YEAR[p_] for p_ in A["period"][ix]]),
             "P": np.isfinite(val[ix]),
             "E": {"comp": obs - val[ix], "curve": obs - A["curve"][ix], "raw_gfs": obs - A["raw_gfs"][ix],
                   "linear_mos": obs - A["linear_mos"][ix]}}
        lead = A["lead"][ix]
        band = np.select([lead <= hi for _, hi in s112.BANDS], [f"{lo}-{hi}" for lo, hi in s112.BANDS], "")
        conds = {"lead_band": (band, [f"{lo}-{hi}" for lo, hi in s112.BANDS]),
                 "cycle_hour": (np.array([f"{h:02d}z" for h in A["ch"][ix]]), ["00z", "06z", "12z", "18z"]),
                 "season": (np.array([s112.SEASONS[k] for k in A["season"][ix]]), list(s112.SEASONS)),
                 "version": (np.array([x[2] if x else "" for x in info]), cond_bins(src))}
        if src == "nbs":
            conds["run_set"] = (np.array([x[0] if x else "" for x in info]), [SAME_RUN, LATER_RUN])
        if src == "ifs":
            el = np.array([x[3] if x else "" for x in info])
            conds["elevation"] = (el, sorted(set(el) - {""}))
        h, sk, br, dm = score_set(src, ic, rng, X, H_FORECASTS, H_PAIRS, conds, ("curve", "comp"), lat)
        H += h
        SK += sk
        BR += br
        DMR.append([src, f"{src} hourly", ic, GROUP[ic], "curve", cfg["name"], "hourly"] + dm)
        hm = {r[4]: r for r in h if r[3] == "all"}
        skc = next(r for r in sk if r[3] == "all" and r[4] == "curve" and r[5] == "comp")
        print(f"  {tag(ic):18s} n {hm['comp'][5]:7,d}  MAE {cfg['name']} {hm['comp'][6]:.3f}  curve {hm['curve'][6]:.3f}  "
              f"raw GFS {hm['raw_gfs'][6]:.3f}  skill curve vs {cfg['name']} {100 * skc[7]:+.1f} % "
              f"[{100 * skc[8]:+.1f}, {100 * skc[9]:+.1f}]  DM p {dm[-1]:.2e}  ({time.time() - t0:.0f} s)")
    DMR = finish_family(DMR)
    nrej = sum(r[-1] for r in DMR)
    print(f"  family {src} hourly (curve against {cfg['name']}): Benjamini-Hochberg at 0.05 rejects {nrej} of "
          f"{len(DMR)}: " + ", ".join(f"{r[2]} {r[9]:+.3f} {'rej' if r[-1] else 'not'}" for r in DMR))
    write_table(f"hourly_{src}.csv", HEAD_COLS, H)
    write_table(f"hourly_{src}_skill.csv", SKILL_COLS, SK)
    write_table(f"hourly_{src}_breakdown.csv", BRK_COLS, BR)
    write_table(f"hourly_{src}_dm.csv", DM_COLS, DMR)
    for name, n, h_ in _TABLES:
        print(f"  {name}: {n} rows, SHA-256 {h_}")
    print(f"--hourly --source {src}: done ({time.time() - t0:.0f} s)")
    return 0


# ------------------------------------------------------------------ Step 6 (first part): --docs (TXN windows)

NBM_DOC_INDEX = "https://vlab.noaa.gov/web/mdl/nbm-versions"
TXN_COLS = ["version", "first_run", "last_run", "status", "window_utc", "definition_text", "source_url", "page_title",
            "tried"]


def page_text(url):
    t = s113.get(url, tries=2).text
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", " ", t)
    return t, re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t)))


def txn_definition(text):
    """The TXN element's text and its maximum window, if the page states them."""
    m = re.search(r"TXN\s*=\s*(.{0,420})", text)
    if not m:
        return None, None
    seg = m.group(1)
    w = re.search(r"[Mm]ax(?:imum)?\s+is\s+between\s+(\d{1,2})\s*[zZ]\s*\(?current day\)?\s*-\s*(\d{1,2})\s*[zZ]\s*"
                  r"\(?next day\)?", seg)
    win = f"{int(w.group(1)):02d}Z (current day) to {int(w.group(2)):02d}Z (next day)" if w else None
    return seg[:300].strip(), win


def run_docs(args):
    print(f"SESSION 114 --docs (NBM text documentation pages only), start {now_utc()}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    links = {}
    try:
        raw, _ = page_text(NBM_DOC_INDEX)
        for href in re.findall(r'href="([^"]+)"', raw):
            if re.search(r"(?i)text-?card", href):
                u = html.unescape(href)
                u = u if u.startswith("http") else "https://vlab.noaa.gov" + u
                mv = re.search(r"(?i)v(\d)\.?(\d)(?:\.(\d+))?", u)
                if mv:
                    links.setdefault("v" + ".".join(x for x in mv.groups() if x), set()).add(u.split("?")[0])
        print(f"  {NBM_DOC_INDEX}: read; text-card links found for {sorted(links)}")
    except Exception as e:  # noqa: BLE001
        print(f"  {NBM_DOC_INDEX}: not read ({e})")
    rows = []
    vers = NBM_VERSIONS
    for k, (v, t0) in enumerate(vers):
        t1 = vers[k + 1][1] if k + 1 < len(vers) else None
        cands = sorted(links.get(v, set())) + [f"https://vlab.noaa.gov/web/mdl/nbm-textcard-{v}"]
        tried, found = [], None
        for u in dict.fromkeys(cands):
            try:
                raw, text = page_text(u)
                mt = re.search(r"(?is)<title>(.*?)</title>", raw)
                title = re.sub(r"\s+", " ", html.unescape(mt.group(1))).strip() if mt else ""
                own = re.search(r"(?i)\b" + re.escape(v) + r"\b", title) is not None
                dfn, win = txn_definition(text)
                tried.append(f"{u}: read, title '{title}'" + ("" if dfn else " (no TXN definition on the page)") +
                             ("" if own else " (the title does not name this version)"))
                if dfn and own:
                    found = (u, dfn, win, title)
                    break
            except Exception as e:  # noqa: BLE001
                tried.append(f"{u}: {str(e)[:80]}")
        if found and found[2]:
            status = "definition found"
        elif found:
            status = "TXN text found, window not stated"
        else:
            status = "definition not found"
        rows.append([v, s113.iso(t0) if t0 else "before the window", s113.iso(t1) if t1 else "end of the window",
                     status, found[2] if found and found[2] else "", found[1] if found else "", found[0] if found else "",
                     found[3] if found else "", " | ".join(tried)])
        print(f"  {v}: {status}" + (f": {found[2]} ({found[0]})" if found and found[2] else "") + f"; tried {len(tried)}")
    write_table("txn_windows.csv", TXN_COLS, rows)
    # Step 3's labels: match_counts.csv's TXN column, by version (the one file this script rewrites)
    lab = {r[0]: (f"{r[0]}: {r[4]} (documentation)" if r[3] == "definition found" else f"{r[0]}: {r[3]}") for r in rows}
    mc = OUT_DIR / "match_counts.csv"
    with open(mc, newline="") as f:
        rd = list(csv.reader(f))
    head, body = rd[0], rd[1:]
    jv, jt, js, jo = head.index("version"), head.index("txn_window"), head.index("source"), head.index("output")
    n = 0
    for r in body:
        if r[js] == "nbs" and r[jo].startswith("daily"):
            r[jt] = lab.get(r[jv], "no run")
            n += 1
    text = s97.csv_text(head, body)
    tmp = mc.with_name(mc.name + ".partial")
    tmp.write_text(text)
    tmp.replace(mc)
    print(f"  match_counts.csv: {n} TXN labels filled; SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    for name, k, h_ in _TABLES:
        print(f"  {name}: {k} rows, SHA-256 {h_}")
    return 0


def txn_status():
    p = OUT_DIR / "txn_windows.csv"
    if not p.exists():
        raise SystemExit("STOP: txn_windows.csv is missing; run --docs first (D108.4(c))")
    return {r["version"]: r for r in read_table("txn_windows.csv")}


# ------------------------------------------------------------------ Step 5: --dailymax

D_HEAD_COLS = HEAD_COLS + ["definition"]
EV_COLS = ["source", "icao", "group", "cycle_hour", "first_lead_min", "first_lead_max", "forecast", "n", "mae",
           "mae_lo", "mae_hi", "mean_error", "me_lo", "me_hi", "skill_curve_vs_competitor", "skill_lo", "skill_hi"]


def day_arrays(recs, txn=None):
    obs = np.array([np.nan if x["obs_max"] is None else x["obs_max"] for x in recs])

    def col(k):
        return np.array([np.nan if (x.get(k) is None or (isinstance(x.get(k), float) and math.isnan(x.get(k))))
                         else float(x[k]) for x in recs])
    X = {"day": np.array([x["date"].toordinal() for x in recs], dtype=np.int64),
         "ty": np.array([TEST_YEAR[x["period"]] for x in recs]),
         "P": np.array([is_paired_day(x) for x in recs], dtype=bool),
         "E": {"comp": obs - col("comp"), "comp2": obs - col("comp2"), "curve": obs - col("curve"),
               "curve_at": obs - col("curve_at"), "raw_gfs": obs - col("raw_gfs"),
               "linear_mos": obs - col("linear_mos")},
         "version": np.array([x["version"] for x in recs]), "run": np.array([x["run"] for x in recs]),
         "ch": np.array([f"{x['cycle'].hour:02d}z" for x in recs]),
         "season": np.array([s112.SEASON_OF[x["date"].month] for x in recs]),
         "first_lead": np.array([x.get("first_lead", -1) for x in recs])}
    if txn is not None:
        X["found"] = np.array([txn.get(v, {}).get("status") == "definition found" for v in X["version"]])
    return X


def run_dailymax(args):
    src = args.source
    t0 = time.time()
    cfg = SOURCES[src]
    print(f"SESSION 114 --dailymax --source {src} ({cfg['name']}; descriptive, D107.2), start {now_utc()}; "
          f"{versions_text()}; seed {SEED}")
    print(f"  {cfg['name']}'s maximum: {cfg['daily_label']}" + (f"; also {cfg['second_label']}" if
                                                                  cfg.get("second_label") else ""))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    txn = txn_status() if src == "nbs" else None
    rng = np.random.default_rng(SEED)
    lat = latency_text(src)
    fc = ["comp"] + (["comp2"] if cfg.get("second_label") else []) + ["curve", "curve_at", "raw_gfs", "linear_mos"]
    prs = [("curve", "comp"), ("raw_gfs", "comp"), ("curve_at", "comp"), ("linear_mos", "comp"), ("comp", "raw_gfs")]
    if cfg.get("second_label"):
        prs.append(("curve", "comp2"))
    H, SK, BR, DMR, EV, NF = [], [], [], [], [], []
    for ic in cfg["airports"]:
        ours = Ours(ic)
        comp = Comp(src, ic)
        recs = daily_records(src, ours, comp, "scored")
        X = day_arrays(recs, txn)
        if src == "nbs":
            nf = X["P"] & ~X["found"]
            X["P"] = X["P"] & X["found"]
        conds = {"season": (X["season"], list(s112.SEASONS)), "version": (X["version"], cond_bins(src)),
                 "cycle_hour": (X["ch"], ["00z", "06z", "12z", "18z"])}
        if src == "nbs":
            conds["run_set"] = (X["run"], [SAME_RUN, LATER_RUN])
        h, sk, br, dm = score_set(src, ic, rng, X, fc, prs, conds, ("curve", "comp"), lat)
        if src == "nbs":
            dfn = "; ".join(f"{v}: {r['window_utc'] or r['status']}" for v, r in txn.items())
            dfn = f"TXN, versions with a found definition only ({dfn})"
        else:
            dfn = cfg["daily_label"]
        H += [r + [dfn] for r in h]
        SK += sk
        BR += br
        DMR.append([src, f"{src} daily maximum", ic, GROUP[ic], "curve (D98.10)", cfg["name"], "daily maximum"] + dm)
        if src == "nbs" and nf.any():
            Y = dict(X)
            Y["P"] = nf
            hn, skn, _, _ = score_set(src, ic, rng, Y, fc, prs, {}, ("curve", "comp"), lat)
            NF += [r + ["TXN, versions whose definition was not found (D108.4(c)): reported separately"] for r in hn]
        # every cycle, by cycle hour (descriptive, 2,000 resamples)
        er = daily_records(src, ours, comp, "every")
        V = day_arrays(er, txn)
        if src == "nbs":
            V["P"] = V["P"] & V["found"]
        cells, pp, order = [], [], []
        for ch in ("00z", "06z", "12z", "18z"):
            mb = V["P"] & (V["ch"] == ch)
            if not mb.any():
                continue
            order.append(ch)
            for f in fc:
                cells.append(((ch, f), mb & np.isfinite(V["E"][f]), V["E"][f]))
            pp.append(((ch,), mb & np.isfinite(V["E"]["curve"]), V["E"]["curve"], V["E"]["comp"]))
        res, nd, _ = boot_block(rng, V["day"], V["P"], REPS_CELL, cells, pp)
        for ch in order:
            mb = V["P"] & (V["ch"] == ch)
            fl_ = V["first_lead"][V["ch"] == ch]
            sk_ = skill_of(V["E"]["curve"][mb], V["E"]["comp"][mb])
            slo, shi = res[("s", ch)]
            for f in fc:
                m = mb & np.isfinite(V["E"][f])
                if not m.any():
                    continue
                lo_a, hi_a, lo_e, hi_e = res[("f", ch, f)]
                EV.append([src, ic, GROUP[ic], ch, int(fl_.min()), int(fl_.max()), f, int(m.sum()),
                           float(np.mean(np.abs(V["E"][f][m]))), lo_a, hi_a, float(np.mean(V["E"][f][m])), lo_e, hi_e,
                           sk_ if f == "comp" else "", slo if f == "comp" else "", shi if f == "comp" else ""])
        hm = {r[4]: r for r in h if r[3] == "all"}
        skc = next(r for r in sk if r[3] == "all" and r[4] == "curve" and r[5] == "comp")
        print(f"  {tag(ic):18s} days {hm['comp'][5]:5,d}  MAE {cfg['name']} {hm['comp'][6]:.3f}  curve {hm['curve'][6]:.3f}"
              f"  curve at its steps {hm['curve_at'][6]:.3f}  raw GFS {hm['raw_gfs'][6]:.3f}  skill curve vs "
              f"{cfg['name']} {100 * skc[7]:+.1f} % [{100 * skc[8]:+.1f}, {100 * skc[9]:+.1f}]  DM p {dm[-1]:.2e}"
              + (f"  (not-found TXN days {int(nf.sum())})" if src == "nbs" else "") + f"  ({time.time() - t0:.0f} s)")
    DMR = finish_family(DMR)
    nrej = sum(r[-1] for r in DMR)
    print(f"  family {src} daily maximum (the curve's D98.10 maximum against {cfg['name']}'s): Benjamini-Hochberg at "
          f"0.05 rejects {nrej} of {len(DMR)}: " + ", ".join(f"{r[2]} {r[9]:+.3f} {'rej' if r[-1] else 'not'}"
                                                             for r in DMR))
    write_table(f"dailymax_{src}.csv", D_HEAD_COLS, H)
    write_table(f"dailymax_{src}_skill.csv", SKILL_COLS, SK)
    write_table(f"dailymax_{src}_breakdown.csv", BRK_COLS, BR)
    write_table(f"dailymax_{src}_dm.csv", DM_COLS, DMR)
    write_table(f"dailymax_{src}_every_cycle.csv", EV_COLS, EV)
    if src == "nbs":
        write_table("dailymax_nbs_txn_not_found.csv", D_HEAD_COLS, NF)
    for name, n, h_ in _TABLES:
        print(f"  {name}: {n} rows, SHA-256 {h_}")
    print(f"--dailymax --source {src}: done ({time.time() - t0:.0f} s)")
    return 0


# ------------------------------------------------------------------ Step 6: --official (D108.4(d); descriptive only)

GAP_COLS = ["icao", "group", "test_year", "day_set", "our_window", "n", "mean_gap", "mae", "p5", "p10", "p25", "p50",
            "p75", "p90", "p95", "share_equal_lt_0p05c", "share_within_1f", "label"]
OSC_COLS = ["icao", "group", "test_year", "day_set", "pair_set", "version", "forecast", "n", "mae", "mean_error",
            "rmse", "label"]
AGREE_C = 0.05                                           # D108.4(d), F156.7: |CLI - GHCN| below 0.05 degrees C


def hourly_max(ours, hh):
    """D82.8's maximum over the given UTC hours (usable if usable hours >= hours - 2), else None."""
    if hh[-1] > h_of(LIMIT) or not all(h in ours.db.obs_h for h in hh):
        return None
    vals = [ours.db.obs_h[h] for h in hh if ours.db.obs_h[h] is not None]
    return max(vals) if s104.usable_day(len(hh), len(vals)) else None


def run_official(args):
    t0 = time.time()
    print(f"SESSION 114 --official (descriptive only, D108.4(d)), start {now_utc()}")
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    cli = read_s113_dicts("official_cli.csv.gz", lambda d: d["airport"] in US4)
    ghcn = read_s113_dicts("official_ghcn.csv.gz", lambda d: d["airport"] in US4)
    gmap = {(r["airport"], r["date"]): float(r["tmax_c"]) for r in ghcn if r["tmax_c"] != ""}
    txn = txn_status()
    GAP, OSC = [], []
    for ic in US4:
        ours = Ours(ic)
        tz = TZNAME[ic]
        C = {}
        for r in cli:
            if r["airport"] != ic or r["high_c"] == "":
                continue
            d = dt.date.fromisoformat(r["climate_day"])
            s_, e_ = s113.guard_climate_day(d, tz)
            if (ptime(r["window_start_utc"]), ptime(r["window_end_utc"])) != (s_, e_):
                raise SystemExit(f"STOP: {ic} {d}: CLI window differs from the local standard time day")
            hc = float(r["high_c"])
            if hc != s113.f_to_c(r["high_f"]):
                raise SystemExit(f"STOP: {ic} {d}: high_c is not high_f converted exactly")
            g = gmap.get((ic, r["climate_day"]))
            C[d] = (hc, g is not None and abs(hc - g) < AGREE_C)
        # the gap of the official maximum from our hourly-report maximum (civil day; local standard time day)
        gaps = []
        for d, (hc, agree) in sorted(C.items()):
            civ = hourly_max(ours, day_hours(ours, d))
            s_, e_ = s113.climate_day_window(d, tz)
            lst = hourly_max(ours, [h_of(s_) + k for k in range(24)])
            gaps.append((d, s113.test_year(dt.datetime(d.year, d.month, d.day)), agree, hc, civ, lst))
        for win, k in (("civil local day (D82.8)", 4), ("local standard time day (the climate day's own window)", 5)):
            for dset in ("all days with CLI", "CLI and GHCN-Daily agree"):
                for ty in sorted({g[1] for g in gaps}) + ["all"]:
                    sel = [g for g in gaps if g[k] is not None and (ty == "all" or g[1] == ty) and
                           (dset.startswith("all") or g[2])]
                    gp = np.array([g[3] - g[k] for g in sel])
                    if not len(gp):
                        continue
                    GAP.append([ic, GROUP[ic], ty, dset, win, len(gp), float(gp.mean()), float(np.abs(gp).mean())] +
                               [float(x) for x in np.percentile(gp, s112.PCTS)] +
                               [float(np.mean(np.abs(gp) < AGREE_C)), float(np.mean(np.abs(gp) <= 5 / 9 + 1e-12)),
                                "gap = CLI maximum minus our hourly-report maximum; CLI is continuous, ours hourly"])
        # forecasts against CLI, on D98.10's days (the forecast's civil day = the climate day's date)
        comps = {}
        for src in ("nbm", "nbs", "mav"):
            if ic in SOURCES[src]["airports"]:
                comps[src] = {x["date"]: x for x in daily_records(src, ours, Comp(src, ic), "scored")}
        days = [x for x in ours.sdays if x["date"] in C and x["curve"] is not None and x["raw_gfs"] is not None]

        def add_rows(pair_set, recs, fcs, version="all"):
            for dset in ("all days with CLI", "CLI and GHCN-Daily agree"):
                for ty in ("2023-24", "2024-25", "2025-26", "all"):
                    sel = [r for r in recs if (ty == "all" or TEST_YEAR[r["period"]] == ty) and
                           (dset.startswith("all") or C[r["date"]][1])]
                    if not sel:
                        continue
                    for f, get_ in fcs:
                        e = np.array([C[r["date"]][0] - get_(r) for r in sel if np.isfinite(get_(r))])
                        if not len(e):
                            continue
                        OSC.append([ic, GROUP[ic], ty, dset, pair_set, version, f, len(e), float(np.abs(e).mean()),
                                    float(e.mean()), float(np.sqrt((e * e).mean())),
                                    "truth: CLI (midnight to midnight local standard time); forecasts for the civil "
                                    "local day; windows as labelled"])
        add_rows("curve and raw GFS (D98.10 days with CLI)", days,
                 [("curve", lambda r: r["curve"]), ("raw_gfs", lambda r: r["raw_gfs"]),
                  ("our hourly-report maximum", lambda r: r["obs_max"] if r["obs_max"] is not None else math.nan)])
        for src, cm in comps.items():
            name = SOURCES[src]["name"]
            recs = [r for r in days if r["date"] in cm and np.isfinite(cm[r["date"]]["comp"])]
            if src == "nbs":
                recs_f = [r for r in recs if txn.get(cm[r["date"]]["version"], {}).get("status") == "definition found"]
            else:
                recs_f = recs
            fcs = [(f"{src} ({SOURCES[src]['daily_label'].split(':')[0]})", lambda r, cm=cm: cm[r["date"]]["comp"]),
                   ("curve", lambda r: r["curve"]), ("raw_gfs", lambda r: r["raw_gfs"])]
            if src == "nbm":
                fcs.insert(1, ("nbm (its own steps)", lambda r, cm=cm: cm[r["date"]]["comp2"]))
            add_rows(f"{name} pairs", recs_f, fcs)
            if src == "nbs":
                for v, _ in NBM_VERSIONS:
                    rv = [r for r in recs if cm[r["date"]]["version"] == v]
                    if rv:
                        st = txn.get(v, {}).get("status", "")
                        add_rows(f"{name} pairs", rv, fcs, version=f"{v} ({st})")
        a = [g for g in GAP if g[0] == ic and g[2] == "all" and g[3] == "all days with CLI"]
        print(f"  {tag(ic):14s} CLI days {len(C)}; agree with GHCN {sum(v[1] for v in C.values())}; gap (CLI minus ours), "
              + "; ".join(f"{g[4].split(' (')[0]}: n {g[5]}, mean {g[6]:+.2f}, MAE {g[7]:.2f}, equal {100 * g[15]:.0f} %"
                          for g in a) + f"  ({time.time() - t0:.0f} s)")
        for r in OSC:
            if r[0] == ic and r[2] == "all" and r[3] == "all days with CLI" and r[5] == "all":
                print(f"      {r[4]:42s} {r[6]:28s} n {r[7]:5d}  MAE {r[8]:.3f}  mean error {r[9]:+.3f}")
    write_table("official_gap.csv", GAP_COLS, GAP)
    write_table("official_scores.csv", OSC_COLS, OSC)
    for name, n, h_ in _TABLES:
        print(f"  {name}: {n} rows, SHA-256 {h_}")
    print(f"--official: done ({time.time() - t0:.0f} s)")
    return 0


# ------------------------------------------------------------------ Step 7: --figures

FIG_COLOR = {"curve": "#2a78d6", "raw_gfs": "#eb6834", "comp": "#1baf7a", "curve_at": "#6250d6"}   # validated order
FIG_SOURCES = ["aifs", "nbm", "nbs", "mav"]
_FIGS = []


def save(fig, name):
    if PREVIEW:
        fig.savefig(PREVIEW[0] / (name + ".png"), dpi=100)
    s112.save_fig(fig, name, _FIGS)


PREVIEW = []


def suptitle(fig, text):
    import textwrap
    fig.suptitle("\n".join(textwrap.wrap(text, 150)), fontsize=8.5, x=0.01, ha="left")


def mae_panels(plt, out, title, fname, fcs, labels):
    fig, axd = plt.subplot_mosaic([["aifs", "aifs", "aifs"], ["nbm", "nbs", "mav"]], figsize=(10, 7.8),
                                  constrained_layout=True, gridspec_kw={"width_ratios": [5, 5, 4]})
    for src in FIG_SOURCES:
        ax = axd[src]
        rows = {(r["icao"], r["forecast"]): r for r in read_table(f"{out}_{src}.csv") if r["test_year"] == "all"}
        aps = SOURCES[src]["airports"]
        x = np.arange(len(aps))
        wdt = 0.8 / len(fcs)
        for k, f in enumerate(fcs):
            v = np.array([float(rows[(ic, f)]["mae"]) for ic in aps])
            lo = np.array([float(rows[(ic, f)]["mae_lo"]) for ic in aps])
            hi = np.array([float(rows[(ic, f)]["mae_hi"]) for ic in aps])
            ax.bar(x + (k - (len(fcs) - 1) / 2) * wdt, v, wdt * 0.9, color=FIG_COLOR[f], label=labels[f],
                   yerr=[v - lo, hi - v], error_kw={"elinewidth": 0.8, "ecolor": s112.INK2, "capsize": 0})
        ax.set_xticks(x)
        ax.set_xticklabels([ic + ("" if GROUP[ic] == "claim" else "\n(dev)") for ic in aps], fontsize=7)
        ax.set_title(f"against {SOURCES[src]['name']}", loc="left")
        ax.set_ylabel("MAE, degrees C")
        ax.grid(axis="x", visible=False)
    h, l_ = axd["aifs"].get_legend_handles_labels()
    fig.legend(h, l_, loc="outside lower center", ncol=len(fcs), fontsize=7.5)
    suptitle(fig, title + ". Each panel on that source's own paired rows or days, so the curve's bars differ between "
             "panels; lines show 95 % intervals (7-day blocks). (dev) = " + DEV_FLAG)
    save(fig, fname)


def run_figures(args):
    t0 = time.time()
    print(f"SESSION 114 --figures, start {now_utc()}")
    plt = s112.plt_setup()
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    if args.trial_dir:
        PREVIEW.append(Path(args.trial_dir))
    mae_panels(plt, "hourly", "Hourly MAE: each competitor, the curve and raw GFS, all test years pooled",
               "comparison_hourly_mae.svg", ["comp", "curve", "raw_gfs"],
               {"comp": "the competitor", "curve": "curve", "raw_gfs": "raw GFS"})
    mae_panels(plt, "dailymax", "Daily maximum MAE (D98.10's days; truth: our hourly-report maximum)",
               "comparison_dailymax_mae.svg", ["comp", "curve", "curve_at", "raw_gfs"],
               {"comp": "the competitor's maximum (AIFS: its 6-hourly steps; NBM: TMAX; NBS: TXN; MAV: X)",
                "curve": "curve (D98.10)", "curve_at": "curve sampled at the competitor's steps",
                "raw_gfs": "raw GFS"})
    # skill of the curve against each competitor, with intervals
    fig, axes = plt.subplots(1, 2, figsize=(10, 7.5), constrained_layout=True, sharey=True)
    for ax, out, ttl in zip(axes, ("hourly", "dailymax"), ("Hourly", "Daily maximum (curve's D98.10 maximum)")):
        ylab, y = [], 0
        for src in FIG_SOURCES:
            rows = {r["icao"]: r for r in read_table(f"{out}_{src}_skill.csv")
                    if r["test_year"] == "all" and r["a"] == "curve" and r["b"] == "comp"}
            for ic in SOURCES[src]["airports"]:
                r = rows[ic]
                v, lo, hi = (100 * float(r[k]) for k in ("skill_a_vs_b", "lo", "hi"))
                ax.plot([lo, hi], [y, y], color=FIG_COLOR["curve"], lw=1.6)
                ax.plot([v], [y], "o", color=FIG_COLOR["curve"], ms=4)
                ylab.append(f"{SOURCES[src]['name']}  {ic}" + ("" if GROUP[ic] == "claim" else " (dev)"))
                y += 1
            y += 0.6
        ax.axvline(0, color=s112.INK, lw=0.8)
        ax.set_title(ttl, loc="left")
        ax.set_xlabel("skill of the curve against the competitor, % (positive: the curve's MAE is smaller)")
        ax.grid(axis="y", visible=False)
    ys = []
    y = 0
    for src in FIG_SOURCES:
        for ic in SOURCES[src]["airports"]:
            ys.append(y)
            y += 1
        y += 0.6
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels(ylab, fontsize=6.5)
    axes[0].invert_yaxis()
    fig.suptitle("The curve against each competitor: pooled skill with 95 % intervals. Descriptive (D107.2); "
                 "formal tests in the _dm tables.\n(dev) = " + DEV_FLAG, fontsize=8.5, x=0.01, ha="left")
    save(fig, "comparison_skill.svg")
    # skill by lead band against AIFS and the NBM grid
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), constrained_layout=True, sharey=True)
    bands = [f"{lo}-{hi}" for lo, hi in s112.BANDS]
    for ax, src in zip(axes, ("aifs", "nbm")):
        rows = [r for r in read_table(f"hourly_{src}_breakdown.csv") if r["condition"] == "lead_band" and
                r["forecast"] == "comp"]
        ends = []
        for ic in SOURCES[src]["airports"]:
            v = [100 * float(next(r for r in rows if r["icao"] == ic and r["bin"] == b)["skill_curve_vs_competitor"])
                 for b in bands]
            ls = "-" if GROUP[ic] == "claim" else "--"
            ax.plot(range(4), v, ls, color=s112.INK2 if GROUP[ic] == "dev" else FIG_COLOR["curve"], lw=1.2)
            ends.append([v[-1], ic])
        ends.sort()
        for k in range(1, len(ends)):                      # keep end labels at least 2.4 points apart
            ends[k][0] = max(ends[k][0], ends[k - 1][0] + 2.4)
        for y_, ic in ends:
            ax.annotate(ic + ("" if GROUP[ic] == "claim" else " (dev)"), (3.05, y_), fontsize=6.5, va="center",
                        color=s112.INK)
        ax.axhline(0, color=s112.INK, lw=0.8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(bands)
        ax.set_xlim(-0.2, 3.75)
        ax.set_xlabel("lead band, hours")
        ax.set_title(f"against {SOURCES[src]['name']}", loc="left")
    axes[0].set_ylabel("skill of the curve, %")
    fig.suptitle("Hourly skill of the curve by lead band (positive: the curve is better). Blue solid: claim airports; "
                 "grey dashed: development airports (dev). Descriptive.", fontsize=8.5, x=0.01, ha="left")
    save(fig, "comparison_lead_band.svg")
    # the official maximum's gap
    rows = [r for r in read_table("official_gap.csv") if r["day_set"] == "all days with CLI"]
    fig, ax = plt.subplots(figsize=(8, 4.6), constrained_layout=True)
    y = 0
    labs = []
    for ic in US4:
        for ty in ("2023-24", "2024-25", "2025-26", "all"):
            civ = [r for r in rows if r["icao"] == ic and r["test_year"] == ty and r["our_window"].startswith("civil")]
            lst = [r for r in rows if r["icao"] == ic and r["test_year"] == ty and r["our_window"].startswith("local")]
            if not civ:
                continue
            r = civ[0]
            ax.plot([float(r["p10"]), float(r["p90"])], [y, y], color=FIG_COLOR["comp"], lw=1.4)
            ax.plot([float(r["p25"]), float(r["p75"])], [y, y], color=FIG_COLOR["comp"], lw=4.5, solid_capstyle="round")
            ax.plot([float(r["mean_gap"])], [y], "o", color=FIG_COLOR["curve"], ms=4.5,
                    label="mean, civil local day" if y == 0 else None)
            ax.plot([float(lst[0]["mean_gap"])], [y], "o", mfc="none", mec=FIG_COLOR["raw_gfs"], ms=7,
                    label="mean, local standard time day" if y == 0 else None)
            labs.append(f"{ic}{'' if GROUP[ic] == 'claim' else ' (dev)'} {ty}")
            y += 1
        y += 0.5
    ys, yy = [], 0
    for ic in US4:
        n = len({r["test_year"] for r in rows if r["icao"] == ic})
        ys += [yy + k for k in range(n)]
        yy += n + 0.5
    ax.set_yticks(ys)
    ax.set_yticklabels(labs, fontsize=7)
    ax.invert_yaxis()
    ax.axvline(0, color=s112.INK, lw=0.8)
    ax.set_xlabel("CLI maximum minus our hourly-report maximum, degrees C (thin: 10th to 90th percentile; thick: "
                  "25th to 75th)")
    ax.legend(loc="lower right", fontsize=7)
    ax.grid(axis="y", visible=False)
    fig.suptitle("The official daily maximum (CLI) against our hourly-report maximum (D82.8), per test year",
                 fontsize=8.5, x=0.01, ha="left")
    save(fig, "comparison_official_gap.svg")
    for name, n, h_ in _FIGS:
        print(f"  {name}: {n:,} bytes, SHA-256 {h_}")
    if "render_part1" in globals():
        part1 = render_part1()
        tgt = Path(args.trial_dir) if args.trial_dir else OUT_DIR
        s112.write_once_bytes(tgt / "part1.md", part1.encode())
        print(f"  part1.md: {len(part1.splitlines())} lines, SHA-256 {hashlib.sha256(part1.encode()).hexdigest()}")
        part2 = render_part2()
        s112.write_once_bytes(tgt / "part2_comparisons.md", part2.encode())
        print(f"  part2_comparisons.md: {len(part2.splitlines())} lines, SHA-256 "
              f"{hashlib.sha256(part2.encode()).hexdigest()}")
    print(f"--figures: done ({time.time() - t0:.0f} s)")
    return 0


# ------------------------------------------------------------------ Step 7: ANALYSIS.md Part 1 and the Part 2 section

_TC = {}


def T(name, folder=None):
    k = (name, folder)
    if k not in _TC:
        _TC[k] = read_table(name, folder)
    return _TC[k]


def T112(name):
    return T(name, S112_TABLES)


CLAIM = [ic for ic in AIRPORTS if GROUP[ic] == "claim"]


def f2(x):
    return f"{x:.2f}"


def sg2(x):
    return f"{x:+.2f}"


def sg1(x):
    return f"{x:+.1f}"


def pc0(x):
    return f"{100 * x:.0f} %"


def spc0(x):
    return f"{100 * x:+.0f} %"


def spc1(x):
    return f"{100 * x:+.1f} %"


def rng_of(vals, fmt, unit_last=False):
    """'fmt(min) (IC) to fmt(max) (IC)' over a dict airport -> value."""
    lo = min(vals, key=lambda k: (vals[k], AIRPORTS.index(k)))
    hi = max(vals, key=lambda k: (vals[k], -AIRPORTS.index(k)))
    return f"{fmt(vals[lo])} ({lo}) to {fmt(vals[hi])} ({hi})"


def one(rows, **kw):
    sel = [r for r in rows if all(r[k] == v for k, v in kw.items())]
    if len(sel) != 1:
        raise SystemExit(f"STOP: Part 1 lookup {kw} found {len(sel)} rows")
    return sel[0]


def fl_(r, k):
    return float(r[k])


def dm_counts(out, src):
    rows = T(f"{out}_{src}_dm.csv")
    better = [r["icao"] for r in rows if r["bh_reject_q005"] == "True" and float(r["mean_daily_diff"]) < 0]
    worse = [r["icao"] for r in rows if r["bh_reject_q005"] == "True" and float(r["mean_daily_diff"]) > 0]
    return better, worse, len(rows)


def names(lst):
    return ", ".join(lst) if lst else "none"


def part1_values():
    V = {}
    hh, dh = T112("hourly_headline.csv"), T112("dailymax_headline.csv")
    hmae = {ic: fl_(one(hh, icao=ic, period="all", forecast="curve"), "mae") for ic in AIRPORTS}
    dmae = {ic: fl_(one(dh, icao=ic, period="all", forecast="curve"), "mae") for ic in AIRPORTS}
    dme = {ic: fl_(one(dh, icao=ic, period="all", forecast="curve"), "mean_error") for ic in AIRPORTS}
    V["h_mae"] = rng_of({k: hmae[k] for k in CLAIM}, f2)
    V["d_mae"] = rng_of({k: dmae[k] for k in CLAIM}, f2)
    V["d_me"] = rng_of({k: dme[k] for k in CLAIM}, sg2)
    br = T112("hourly_breakdowns.csv")
    band = {(ic, b): fl_(one(br, icao=ic, condition="lead_band", bin=b, forecast="curve"), "mae")
            for ic in AIRPORTS for b in ("3-12", "13-24", "25-36", "37-48")}
    V["growth"] = rng_of({ic: band[(ic, "37-48")] / band[(ic, "3-12")] - 1 for ic in CLAIM}, pc0)
    hs, ds = T112("hourly_curve_skill.csv"), T112("dailymax_curve_skill.csv")
    V["gain_h"] = rng_of({ic: fl_(one(hs, icao=ic, period="all", reference="raw_gfs"), "skill") for ic in CLAIM}, pc0)
    V["gain_d"] = rng_of({ic: fl_(one(ds, icao=ic, period="all", reference="raw_gfs"), "skill") for ic in CLAIM}, pc0)
    V["lmos_h"] = rng_of({ic: fl_(one(hs, icao=ic, period="all", reference="linear_mos"), "skill") for ic in CLAIM},
                         spc1)
    for out in ("hourly", "dailymax"):
        for src in FIG_SOURCES:
            b, w, n = dm_counts(out, src)
            V[f"{out}_{src}_b"], V[f"{out}_{src}_w"], V[f"{out}_{src}_n"] = len(b), len(w), n
            V[f"{out}_{src}_bn"], V[f"{out}_{src}_wn"] = names(b), names(w)
            V[f"{out}_{src}_nr"] = n - len(b) - len(w)
    V["dailymax_worse"] = sum(V[f"dailymax_{src}_w"] for src in FIG_SOURCES)
    V["dailymax_worse_text"] = ("worse than no competitor at any airport" if V["dailymax_worse"] == 0 else
                                f"worse than a competitor at {V['dailymax_worse']} airport and competitor pairs")
    b, w, _ = dm_counts("hourly", "aifs")
    for grp, lab in (("claim", "c"), ("dev", "d")):
        aps = [ic for ic in AIRPORTS if GROUP[ic] == grp]
        V[f"aifs_h_{lab}b"] = names([ic for ic in aps if ic in b])
        V[f"aifs_h_{lab}w"] = names([ic for ic in aps if ic in w])
        V[f"aifs_h_{lab}n"] = sum(ic not in b and ic not in w for ic in aps)
    # item 2: per-airport accuracy tables
    hr = T112("hourly_ranges.csv")
    rows = []
    for ic in AIRPORTS:
        cells = []
        for b in ("3-12", "13-24", "25-36", "37-48"):
            r = one(hr, icao=ic, forecast="curve", lead=f"band {b}", season="all")
            cells.append(f"{f2(band[(ic, b)])} ({sg1(fl_(r, 'p10'))} to {sg1(fl_(r, 'p90'))})")
        rows.append(f"| {lab_ic(ic)} | " + " | ".join(cells) + " |")
    V["table_hourly"] = "\n".join(rows)
    ev, dr, wl = T112("dailymax_every_cycle.csv"), T112("dailymax_ranges.csv"), T112("dailymax_whole_day_leads.csv")
    rows = []
    for ic in AIRPORTS:
        cells = []
        for ch in ("0", "6", "12", "18"):
            r = [x for x in ev if x["icao"] == ic and x["cycle_hour"] == ch and x["day"] == "1" and x["forecast"] == "curve"]
            if not r:
                cells.append("no whole day")
                continue
            q = one(dr, icao=ic, forecast="curve", season="all", day="1", cycle_hour=ch)
            w = one(wl, icao=ic, cycle_hour=ch)
            ld = w["first_lead_min"] if w["first_lead_min"] == w["first_lead_max"] else \
                f"{w['first_lead_min']}-{w['first_lead_max']}"
            cells.append(f"{f2(fl_(r[0], 'mae'))} ({sg1(fl_(q, 'p10'))} to {sg1(fl_(q, 'p90'))}), lead {ld}")
        rows.append(f"| {lab_ic(ic)} | " + " | ".join(cells) + " |")
    V["table_daily"] = "\n".join(rows)
    # item 3: the daily maximum
    dec = T112("dailymax_decomposition.csv")
    V["level"] = rng_of({ic: fl_(one(dec, icao=ic, forecast="curve"), "mean_peak_level") for ic in CLAIM}, f2)
    V["timing"] = rng_of({ic: fl_(one(dec, icao=ic, forecast="curve"), "mean_timing") for ic in CLAIM}, f2)
    ex = T112("dailymax_extremes.csv")
    V["hot_obs"] = rng_of({ic: fl_(one(ex, icao=ic, selected_by="observed maximum", tail="hottest 10 %",
                                         forecast="curve"), "mean_error") for ic in CLAIM}, sg2)
    V["hot_fc_max"] = sg2(max(fl_(one(ex, icao=ic, selected_by="forecast maximum (curve)", tail="hottest 10 %",
                                       forecast="curve"), "mean_error") for ic in CLAIM))
    V["hot_ksfo"] = sg2(fl_(one(ex, icao="KSFO", selected_by="observed maximum", tail="hottest 10 %",
                               forecast="curve"), "mean_error"))
    gap = T("official_gap.csv")
    g = {ic: one(gap, icao=ic, test_year="all", day_set="all days with CLI", our_window="civil local day (D82.8)")
         for ic in US4}
    gl = {ic: one(gap, icao=ic, test_year="all", day_set="all days with CLI",
                  our_window="local standard time day (the climate day's own window)") for ic in US4}
    V["gap"] = "; ".join(f"{lab_ic(ic)} {sg2(fl_(g[ic], 'mean_gap'))}" for ic in US4)
    V["gap_lst"] = "; ".join(f"{ic} {sg2(fl_(gl[ic], 'mean_gap'))}" for ic in US4)
    V["gap_eq"] = rng_of({ic: fl_(g[ic], "share_equal_lt_0p05c") for ic in US4}, pc0)
    V["gap_p90"] = rng_of({ic: fl_(g[ic], "p90") for ic in US4}, sg2)
    # item 4: comparison tables
    V["table_cmp_h"] = cmp_table("hourly", hh, "mae")
    V["table_cmp_d"] = cmp_table("dailymax", dh, "mae")
    sk = T("dailymax_aifs_skill.csv")
    V["aifs_like"] = rng_of({ic: fl_(one(sk, icao=ic, test_year="all", a="curve_at", b="comp"), "skill_a_vs_b")
                             for ic in CLAIM}, spc0)
    V["aifs_like_worse"] = sum(fl_(one(sk, icao=ic, test_year="all", a="curve_at", b="comp"), "skill_a_vs_b") < 0
                               for ic in AIRPORTS)
    for key, src, files in (("dist_aifs", "aifs", ("positions_aifs_0p25_344b2a77.csv", "positions_aifs_0p25_d0b88101.csv")),
                            ("dist_nbm", "nbm", ("positions_nbm_lambert_ae588f24.csv",))):
        per = []
        for f in files:
            pos = read_s113_dicts(f)
            d_ = []
            for ic in SOURCES[src]["airports"]:
                if GROUP[ic] != "dev":
                    continue
                a = next(r for r in pos if r["airport"] == ic and r["position_set"] == "gfs")
                b = next(r for r in pos if r["airport"] == ic and r["position_set"] == "iem")
                d_.append(f"{ic} {s113.haversine_km(float(a['lat']), float(a['lon']), float(b['lat']), float(b['lon'])):.1f}")
            per.append(", ".join(d_))
        if len(set(per)) != 1:
            raise SystemExit(f"STOP: {key}: the positions files disagree")
        V[key] = per[0]
    osc = T("official_scores.csv")
    rows, same = [], 0
    for ic in US4:
        def m(ps, f, ds="all days with CLI"):
            return fl_(one(osc, icao=ic, test_year="all", day_set=ds, pair_set=ps, version="all", forecast=f), "mae")
        sets = [("curve and raw GFS (D98.10 days with CLI)", "curve"), ("curve and raw GFS (D98.10 days with CLI)",
                "raw_gfs"), ("NBM grid pairs", "nbm (TMAX)"), ("NBS pairs", "nbs (TXN)"), ("MAV pairs", "mav (X)")]
        rows.append(f"| {lab_ic(ic)} | " + " | ".join(f2(m(ps, f)) for ps, f in sets) + " |")
        order_all = sorted(range(len(sets)), key=lambda k: m(*sets[k]))
        order_agree = sorted(range(len(sets)), key=lambda k: m(*sets[k], ds="CLI and GHCN-Daily agree"))
        same += order_all == order_agree
    V["table_cli"] = "\n".join(rows)
    V["cli_same"] = same
    cme = {ic: fl_(one(osc, icao=ic, test_year="all", day_set="all days with CLI",
                       pair_set="curve and raw GFS (D98.10 days with CLI)", version="all", forecast="curve"),
                   "mean_error") for ic in US4}
    V["cli_curve_me"] = rng_of(cme, sg2)
    # item 5: when to trust it less
    V["eddm_p5"] = ", ".join(sg1(fl_(one(dr, icao="EDDM", forecast="curve", season=se, day="1", cycle_hour="all"), "p5"))
                             for se in ("Sep-Nov", "Dec-Feb", "Mar-May"))
    for ic in ("KORD", "CYYZ"):
        V[f"season_{ic}"] = " against ".join(
            f2(fl_(one(br, icao=ic, condition="season", bin=se, forecast="curve"), "mae")) for se in ("Mar-May", "Sep-Nov"))
    absb = {ic: fl_(one(br, icao=ic, condition="abs_b", bin="high", forecast="curve"), "mae") -
            fl_(one(br, icao=ic, condition="abs_b", bin="low", forecast="curve"), "mae") for ic in AIRPORTS}
    V["absb"] = rng_of(absb, f2)
    V["absb_n"] = sum(v > 0 for v in absb.values())
    cl = {ic: fl_(one(br, icao=ic, condition="cloud_cover", bin="high", forecast="curve"), "mae") -
          fl_(one(br, icao=ic, condition="cloud_cover", bin="low", forecast="curve"), "mae") for ic in AIRPORTS}
    V["cloud_up"] = names([ic for ic in AIRPORTS if cl[ic] > 0])
    V["cloud_down"] = names([ic for ic in AIRPORTS if cl[ic] < 0])
    top = max(cl, key=cl.get)
    V["cloud_max"] = f"{f2(cl[top])} at {top}"
    ed = T112("dailymax_edge.csv")
    V["edge_obs"] = rng_of({ic: int(one(ed, icao=ic, day_set="scored days")["obs_edge"]) /
                            int(one(ed, icao=ic, day_set="scored days")["days"]) for ic in CLAIM}, pc0)
    z = one(ed, icao="ZUCK", day_set="scored days")
    V["zuck_raw"], V["zuck_obs"] = pc0(int(z["raw_edge"]) / int(z["days"])), pc0(int(z["obs_edge"]) / int(z["days"]))
    # item 6: limits
    lim = T112("limits.csv")
    V["whole_n"] = sum(fl_(r, "share_whole_degree_obs") == 1.0 for r in lim)
    V["floor"] = f2(fl_(lim[0], "rounding_floor_c"))
    sm = T112("smoothness.csv")
    V["jag"] = rng_of({r["icao"]: fl_(r, "curve") / fl_(r, "raw_gfs") for r in sm}, lambda x: f"{x:.1f} times")
    V["sea_raw"] = " and ".join(sg2(fl_(one(dec, icao=ic, forecast="raw_gfs"), "mean_e_max")) for ic in ("NZWN", "ZGSZ"))
    return V


def lab_ic(ic):
    return ic + (" (dev)" if GROUP[ic] == "dev" else "") + (" (sea)" if ic in SEA else "")


def cmp_table(out, s112_head, col):
    """One row per airport: the curve, raw GFS and linear MOS on all scored rows or days (F155), then each
    competitor as 'competitor / curve on the same rows', * where the formal test rejects (BH at 0.05)."""
    rows = []
    for ic in AIRPORTS:
        base = [f2(fl_(one(s112_head, icao=ic, period="all", forecast=f), col)) for f in ("curve", "raw_gfs", "linear_mos")]
        cells = []
        for src in FIG_SOURCES:
            if ic not in SOURCES[src]["airports"]:
                cells.append("-")
                continue
            h = T(f"{out}_{src}.csv")
            c = fl_(one(h, icao=ic, test_year="all", forecast="comp"), "mae")
            u = fl_(one(h, icao=ic, test_year="all", forecast="curve"), "mae")
            d = one(T(f"{out}_{src}_dm.csv"), icao=ic)
            cells.append(f"{f2(c)} / {f2(u)}" + (" *" if d["bh_reject_q005"] == "True" else ""))
        rows.append(f"| {lab_ic(ic)} | " + " | ".join(base + cells) + " | pending (D108.2) |")
    return "\n".join(rows)


PART1_TEMPLATE = """## Part 1. Field guide (order chosen by the owner after session 112's results were seen, D108.6, D106.2)

All figures are from spent test years (nothing valid on or after 2026-08-01). Claim airports come first; (dev)
marks the development airports, whose build choices used these years, so their figures flatter the method
slightly. Ranges run across the six claim airports unless named. Per-airport detail is in item 2's tables.

### 1. The short version

- **Hourly:** the curve's typical error (MAE) is {h_mae} degrees C.
- **Daily maximum:** {d_mae} degrees C, and it reads a little low (mean error {d_me}).
- **Further ahead:** the hourly MAE grows by {growth} from leads 3-12 to leads 37-48.
- **Against raw GFS:** {gain_h} smaller hourly MAE, {gain_d} for the daily maximum.
- **Against other forecasts (formal tests, item 4):** hourly, against AIFS the curve is better at {aifs_h_cb}, worse
  at {aifs_h_cw} and not separated at the other {aifs_h_cn} claim airports; at the development airports better at
  {aifs_h_db} and worse at {aifs_h_dw}. It beats MAV at {hourly_mav_b} of {hourly_mav_n} and loses to NBS, the NBM
  station forecast, at {hourly_nbs_w} of {hourly_nbs_n}. For the daily maximum it beats AIFS at {dailymax_aifs_b} of
  {dailymax_aifs_n} (AIFS's maximum is the highest of four 6-hourly values; read at the same steps the curve's is
  worse at {aifs_like_worse} of 12) and MAV at {dailymax_mav_b} of {dailymax_mav_n}, and no test separates it from
  NBS at {dailymax_nbs_nr} of {dailymax_nbs_n}. ECMWF IFS is pending (D108.2).

### 2. How accurate it is x hours out

**Table 1a. Hourly MAE by lead band, degrees C (80 % of errors fall in the range shown, 10th to 90th
percentile; error = observed minus forecast).**

| airport | leads 3-12 | 13-24 | 25-36 | 37-48 |
|---|---|---|---|---|
{table_hourly}

**Table 1b. Daily maximum MAE by the run's cycle hour, every cycle (80 % range; the lead at which the local day
starts).** The later the day starts after the run, the larger the error.

| airport | 00z run | 06z run | 12z run | 18z run |
|---|---|---|---|---|
{table_daily}

*Sources: `hourly_breakdowns.csv`, `hourly_ranges.csv`, `dailymax_every_cycle.csv`, `dailymax_ranges.csv`,
`dailymax_whole_day_leads.csv` (session 112); figures `hourly_ranges_fan.svg`, `dailymax_by_cycle_hour.svg`.*

### 3. The daily maximum

- **Accuracy.** On the day after the evening's run (D98.10) the MAE is {d_mae} degrees C at the claim airports.
- **It reads low.** The mean error is {d_me}: the real maximum is on average a little warmer than shown. The
  curve's value at the observed peak hour is {level} degrees C below the observed maximum; taking the curve's own
  highest hour wins back {timing}. This fits a selection effect (the observed maximum is the highest of about 24
  noisy readings), but the split does not rule out some damping of the forecast peak (Table B4).
- **The hottest days.** On the observed hottest 10 % of days the curve reads low by {hot_obs} degrees C ({hot_ksfo}
  at KSFO (dev)); picked by the forecast instead, its mean error on the hot tail is at most {hot_fc_max} at the
  claim airports. Days picked by the observation always look like this, partly by selection (Table B3).
- **The official maximum.** At the four US airports the NWS climate report's maximum (CLI) is above our
  hourly-report maximum on average by: {gap}. Over the local standard time day it is {gap_lst}, so the window
  explains little: the rest is a continuous reading against hourly ones. The two agree within 0.05 degrees C on
  {gap_eq} of days; 90 % of gaps are at most {gap_p90}. Against CLI the curve's mean error is {cli_curve_me}
  (it is built to forecast the hourly maximum). Scores against CLI are in item 4.

### 4. How it compares

Each competitor is scored on its own paired rows or days (D108.4(a)), with the curve rescored on exactly the same
ones: a cell gives "competitor / curve" MAE in degrees C. * marks a formal test (Diebold-Mariano, Benjamini-Hochberg
at 0.05 across the airports) that rejects equal accuracy. The first three columns are on all scored rows or days
(F155). Linear MOS, a straight-line correction fitted on the same rows as the model, is the yardstick: the curve
beats it by {lmos_h} hourly at the claim airports. AIFS covers 2025-02-25 on; NBM, NBS and MAV the full test years.

**Table 2a. Hourly.**

| airport | curve | raw GFS | linear MOS | AIFS | NBM grid | NBS | MAV | ECMWF IFS |
|---|---|---|---|---|---|---|---|---|
{table_cmp_h}

**Table 2b. Daily maximum** (D98.10's days; truth our hourly-report maximum; each competitor's own maximum: AIFS the
highest of its 6-hourly steps, NBM TMAX, NBS TXN, MAV X, windows as labelled in Part 2).

| airport | curve | raw GFS | linear MOS | AIFS | NBM grid | NBS | MAV | ECMWF IFS |
|---|---|---|---|---|---|---|---|---|
{table_cmp_d}

- **Formal tests, hourly:** the curve is better than AIFS at {hourly_aifs_b} of {hourly_aifs_n} airports
  ({hourly_aifs_bn}) and worse at {hourly_aifs_w} ({hourly_aifs_wn}); better than the NBM grid at {hourly_nbm_b}
  ({hourly_nbm_bn}) and worse at {hourly_nbm_w} ({hourly_nbm_wn}); worse than NBS at {hourly_nbs_w} of
  {hourly_nbs_n}; better than MAV at {hourly_mav_b} ({hourly_mav_bn}) and worse at {hourly_mav_w}
  ({hourly_mav_wn}).
- **Formal tests, daily maximum:** better than AIFS at {dailymax_aifs_b} of {dailymax_aifs_n}, the NBM grid at
  {dailymax_nbm_b} of {dailymax_nbm_n} ({dailymax_nbm_bn}), NBS at {dailymax_nbs_b} of {dailymax_nbs_n}, MAV at
  {dailymax_mav_b} of {dailymax_mav_n}; {dailymax_worse_text}.
- **Read with care.** AIFS's maximum comes from 6-hourly steps; sampled at the same steps the curve's maximum is
  {aifs_like} against AIFS at the claim airports (worse at {aifs_like_worse} of 12). At the development
  airports both AIFS and the NBM grid are read at GFS's own position (D108.3), not the airport's; that position's
  distance from the airport (km, positions files): AIFS {dist_aifs}; NBM grid {dist_nbm}. NBS, a station forecast, does not
  have that handicap. NBS's 01/07/13/19 UTC runs hold one
  hour more data than our cycle.

**Table 2c. The four US airports against the official maximum (CLI), daily maximum MAE, all test years.** Each
competitor on its own paired days; the curve's and raw GFS's on all D98.10 days with CLI.

| airport | curve | raw GFS | NBM TMAX | NBS TXN | MAV X |
|---|---|---|---|---|---|
{table_cli}

On the days where CLI and GHCN-Daily agree (D108.4(d)'s check), the order of the five is unchanged at {cli_same}
of 4 airports.

### 5. When to trust it less

- **Further ahead.** See item 2; the spread widens steadily with lead at every airport.
- **Season.** At EDDM the daily maximum's 5th percentile error is {eddm_p5} degrees C in Sep-Nov, Dec-Feb and
  Mar-May (the shown maximum far too warm in autumn and winter). Hourly MAE in Mar-May against Sep-Nov: KORD
  {season_KORD}; CYYZ {season_CYYZ}.
- **When the drift tracker is working hard.** In the top third of |b| the curve's MAE is higher than in the bottom
  third at {absb_n} of 12 airports (by {absb}). Large |b| may coincide with harder seasons or weather.
- **Cloud.** The MAE rises from the clearest to the cloudiest third of hours at {cloud_up} (by up to
  {cloud_max}); it falls at {cloud_down}.
- **A maximum at the edge of the day.** On {edge_obs} of days at the claim airports the observed maximum falls in
  the first or last local hour (a warm night or a front). Raw GFS puts it there on {zuck_raw} of days at ZUCK
  against {zuck_obs} observed, the case seen live in cycle 2026-10-13 06z (Part 2, D106.13).

### 6. What limits the accuracy

- **Rounded observations.** {whole_n} of the 12 airports report whole degrees; against them even a perfect
  forecast would show an MAE of about {floor} degrees C.
- **The curve is jagged.** Each lead has its own model, so it moves more from hour to hour than raw GFS
  ({jag} raw GFS's mean |second difference|).
- **Sea in the grid box.** At NZWN and ZGSZ raw GFS's daily maximum reads low by {sea_raw} degrees C; the curve
  fixes most of it.
- **What the comparisons add.** The NBM station forecast (NBS) has the smaller hourly error at {hourly_nbs_w} of
  the {hourly_nbs_n} airports it covers, so local station guidance holds information the curve does not use
  (Part 3). Figures: `comparison_hourly_mae.svg`, `comparison_dailymax_mae.svg`, `comparison_skill.svg`,
  `comparison_lead_band.svg`, `comparison_official_gap.svg`.
"""


def render_part1():
    return PART1_TEMPLATE.format_map(part1_values())



def ci(r, a, b, fmt=f2, mult=1.0):
    if r[a] in ("", None) or r[b] in ("", None):
        return ""
    return f"[{fmt(mult * float(r[a]))}, {fmt(mult * float(r[b]))}]"


def p1(x):
    return f"{100 * x:+.1f}"


def render_part2():
    L = []
    A = L.append
    A("### D107.9 and D108: comparisons (session 114)")
    A("")
    A("Descriptive only (D107.2). Rules fixed before any score in D107.9 and D108. Positions: raw GFS's own (the "
      "positions file's `gfs` set at the development airports, IEM's at the claim airports). AIFS adjusted for "
      "height as GFS is (7.429 degrees C per km, its own terrain with the same four weights); the NBM grid has no "
      "terrain field (no elevation treatment); NBS and MAV as issued. Pairs by valid time; NBS 01/07/13/19 UTC runs "
      "pair with the cycle one hour earlier (one hour more data), and where both run sets exist the same cycle's "
      "run is used. Truth: our hourly-report maximum (D82.8). Intervals: 7-day block bootstrap, seed 114 (10,000 "
      "resamples headline, 2,000 cells). Formal tests: Diebold-Mariano, one family per competitor and output, "
      "Benjamini-Hochberg at 0.05 across its airports. ECMWF IFS: pending (D108.2), not pulled yet. Script "
      "`scripts/session114_comparisons.py`; tables `data/processed/session114_comparisons/`; full log "
      "`notes/session-114-output.txt`. Latency (not adjusted for, D108.4(f)): " + latency_text("aifs") + "; NBM "
      "grid " + latency_text("nbm").split(". GFS")[0].split(": ", 1)[1] + "; NBS and MAV: documented time only.")
    A("")
    # E1 matching
    mc = T("match_counts.csv")
    A("**Table E1. Paired rows and days per source, airport and test year** (`match_counts.csv`, which also has every "
      "unpaired row and day by reason, cycle hour, version and run set).")
    A("")
    A("| source | airport | test year | paired hourly rows | paired D98.10 days | paired every-cycle days |")
    A("|---|---|---|---|---|---|")
    for src in FIG_SOURCES:
        for ic in SOURCES[src]["airports"]:
            for ty in ("2023-24", "2024-25", "2025-26"):
                def cnt(out):
                    return sum(int(r["count"]) for r in mc if r["source"] == src and r["icao"] == ic and
                               r["test_year"] == ty and r["output"] == out and r["item"] == "paired")
                h = cnt("hourly")
                if h == 0 and cnt("daily max, D98.10 days") == 0:
                    continue
                A(f"| {SOURCES[src]['name']} | {lab_ic(ic)} | {ty} | {h:,} | {cnt('daily max, D98.10 days'):,} | "
                  f"{cnt('daily max, every cycle'):,} |")
    A("")
    why = {}
    for r in mc:
        if r["item"] != "paired":
            k = (r["source"], r["output"], r["item"])
            why[k] = why.get(k, 0) + int(r["count"])
    A("Unpaired, all airports together: " + "; ".join(
        f"{SOURCES[k[0]]['name']} {k[1]}, {k[2].replace('unpaired: ', '')}: {v:,}" for k, v in sorted(
            why.items(), key=lambda kv: (FIG_SOURCES.index(kv[0][0]), kv[0][1], kv[0][2]))) + ".")
    A("")
    # E2 / E4 headline per source
    for out, tname, extra in (("hourly", "E2", ""), ("dailymax", "E4", " (D98.10's days)")):
        A(f"**Table {tname}. {'Hourly' if out == 'hourly' else 'Daily maximum'}{extra}: MAE [95 %] on each source's "
          f"paired {'rows' if out == 'hourly' else 'days'}, per test year and pooled** (`{out}_<source>.csv`, "
          f"`{out}_<source>_skill.csv`; breakdowns by "
          f"{'lead band, cycle hour' if out == 'hourly' else 'cycle hour'}, season, version and NBS run set in "
          f"`{out}_<source>_breakdown.csv`). Skill = 1 - MAE(a) / MAE(b), percent.")
        A("")
        if out == "hourly":
            A("| source | airport | test year | n | competitor | curve | raw GFS | linear MOS | skill curve vs it [95 %] "
              "| skill raw GFS vs it |")
            A("|---|---|---|---|---|---|---|---|---|---|")
        else:
            A("| source | airport | test year | days | competitor's maximum | curve (D98.10) | curve at its steps | "
              "raw GFS | skill curve vs it [95 %] | skill curve at its steps vs it |")
            A("|---|---|---|---|---|---|---|---|---|---|")
        for src in FIG_SOURCES:
            H, SK = T(f"{out}_{src}.csv"), T(f"{out}_{src}_skill.csv")
            for ic in SOURCES[src]["airports"]:
                for ty in ("2023-24", "2024-25", "2025-26", "all"):
                    rr = {r["forecast"]: r for r in H if r["icao"] == ic and r["test_year"] == ty}
                    if not rr:
                        continue
                    sk = {(r["a"], r["b"]): r for r in SK if r["icao"] == ic and r["test_year"] == ty}
                    c = rr["comp"]
                    cell = lambda f: f"{f2(fl_(rr[f], 'mae'))} {ci(rr[f], 'mae_lo', 'mae_hi')}"
                    s1 = sk[("curve", "comp")]
                    if out == "hourly":
                        s2 = sk[("raw_gfs", "comp")]
                        A(f"| {SOURCES[src]['name']} | {lab_ic(ic)} | {ty} | {int(c['n']):,} | {cell('comp')} | "
                          f"{cell('curve')} | {f2(fl_(rr['raw_gfs'], 'mae'))} | {f2(fl_(rr['linear_mos'], 'mae'))} | "
                          f"{p1(fl_(s1, 'skill_a_vs_b'))} {ci(s1, 'lo', 'hi', p1)} | {p1(fl_(s2, 'skill_a_vs_b'))} |")
                    else:
                        s2 = sk[("curve_at", "comp")]
                        A(f"| {SOURCES[src]['name']} | {lab_ic(ic)} | {ty} | {int(c['n']):,} | {cell('comp')} | "
                          f"{cell('curve')} | {f2(fl_(rr['curve_at'], 'mae'))} | {f2(fl_(rr['raw_gfs'], 'mae'))} | "
                          f"{p1(fl_(s1, 'skill_a_vs_b'))} {ci(s1, 'lo', 'hi', p1)} | {p1(fl_(s2, 'skill_a_vs_b'))} |")
        A("")
        if out == "hourly":
            A("**Table E2b. Hourly skill of the curve against the competitor by lead band, percent [95 %]** "
              "(`hourly_<source>_breakdown.csv`; `comparison_lead_band.svg`).")
            A("")
            A("| source | airport | 3-12 | 13-24 | 25-36 | 37-48 |")
            A("|---|---|---|---|---|---|")
            for src in FIG_SOURCES:
                br = [r for r in T(f"hourly_{src}_breakdown.csv") if r["condition"] == "lead_band" and r["forecast"] == "comp"]
                for ic in SOURCES[src]["airports"]:
                    cells = []
                    for b in ("3-12", "13-24", "25-36", "37-48"):
                        r = [x for x in br if x["icao"] == ic and x["bin"] == b]
                        cells.append(f"{p1(fl_(r[0], 'skill_curve_vs_competitor'))} {ci(r[0], 'skill_lo', 'skill_hi', p1)}"
                                     if r else "-")
                    A(f"| {SOURCES[src]['name']} | {lab_ic(ic)} | " + " | ".join(cells) + " |")
            A("")
        if out == "dailymax":
            A("NBM's maximum from its own steps (descriptive, beside TMAX), MAE pooled: " + "; ".join(
                f"{ic} {f2(fl_(one(T('dailymax_nbm.csv'), icao=ic, test_year='all', forecast='comp2'), 'mae'))}"
                for ic in SOURCES["nbm"]["airports"]) + ". NBS days of versions whose TXN definition was not found "
                "(v5.0.14), reported separately (`dailymax_nbs_txn_not_found.csv`): " + "; ".join(
                f"{r['icao']} {r['n']} days, NBS {f2(fl_(r, 'mae'))}" for r in T("dailymax_nbs_txn_not_found.csv")
                if r["test_year"] == "all" and r["forecast"] == "comp") + ".")
            A("")
        tn = "E3" if out == "hourly" else "E5"
        A(f"**Table {tn}. Formal tests, {'hourly' if out == 'hourly' else 'daily maximum'}** (`{out}_<source>_dm.csv`). "
          "Daily mean of |e_curve| - |e_competitor| (negative: the curve's errors are smaller), Newey-West at 7 lags.")
        A("")
        A("| family | airport | days | mean daily difference [95 %] | DM statistic | p-value | BH at 0.05 |")
        A("|---|---|---|---|---|---|---|")
        for src in FIG_SOURCES:
            for r in T(f"{out}_{src}_dm.csv"):
                A(f"| {r['family']} | {lab_ic(r['icao'])} | {int(r['days']):,} | {fl_(r, 'mean_daily_diff'):+.3f} "
                  f"{ci(r, 'lo', 'hi', lambda x: f'{x:+.3f}')} | {fl_(r, 'dm_stat'):+.2f} | {fl_(r, 'p_value'):.1e} | "
                  f"{'rejected' if r['bh_reject_q005'] == 'True' else 'not rejected'} |")
        A("")
    # E6 every cycle
    A("**Table E6. Daily maximum from every cycle, by cycle hour: competitor / curve MAE (first lead of the local "
      "day)** (`dailymax_<source>_every_cycle.csv`, with intervals and the curve sampled at the competitor's steps).")
    A("")
    A("| source | airport | 00z | 06z | 12z | 18z |")
    A("|---|---|---|---|---|---|")
    for src in FIG_SOURCES:
        ev = T(f"dailymax_{src}_every_cycle.csv")
        for ic in SOURCES[src]["airports"]:
            cells = []
            for ch in ("00z", "06z", "12z", "18z"):
                rr = {r["forecast"]: r for r in ev if r["icao"] == ic and r["cycle_hour"] == ch}
                if not rr:
                    cells.append("-")
                    continue
                fl0, fl1 = rr["comp"]["first_lead_min"], rr["comp"]["first_lead_max"]
                cells.append(f"{f2(fl_(rr['comp'], 'mae'))} / {f2(fl_(rr['curve'], 'mae'))} (lead "
                             f"{fl0 if fl0 == fl1 else fl0 + '-' + fl1})")
            A(f"| {SOURCES[src]['name']} | {lab_ic(ic)} | " + " | ".join(cells) + " |")
    A("")
    # E7 TXN
    A("**Table E7. NBS TXN window per NBM version (D108.4(c))** (`txn_windows.csv`, with the text and every URL tried).")
    A("")
    A("| version | first run | status | maximum window (UTC) | page |")
    A("|---|---|---|---|---|")
    for r in T("txn_windows.csv"):
        A(f"| {r['version']} | {r['first_run']} | {r['status']} | {r['window_utc'] or '-'} | {r['source_url'] or '-'} |")
    A("")
    A("Maximum fields and their windows: AIFS none (highest of its 6-hourly steps, labelled \"6-hourly steps\"); NBM "
      "TMAX 12z to 00z UTC from the same run; NBS TXN as above, reported at 00Z; MAV X daytime 7 a.m. to 7 p.m. local "
      "standard time. Each is taken from the same run, the window starting on the local date inside leads 3 to 48.")
    A("")
    # E8 official gap
    A("**Table E8. The official maximum's gap: CLI minus our hourly-report maximum, degrees C** (`official_gap.csv`, "
      "with every percentile).")
    A("")
    A("| airport | test year | days (civil / agree) | civil day: mean, MAE | 10th to 90th pct | share equal (< 0.05) "
      "| standard time day: mean, MAE | on agreement days: mean, MAE |")
    A("|---|---|---|---|---|---|---|---|")
    gap = T("official_gap.csv")
    for ic in US4:
        for ty in ("2023-24", "2024-25", "2025-26", "all"):
            cv = [r for r in gap if r["icao"] == ic and r["test_year"] == ty and r["our_window"].startswith("civil")]
            if not cv:
                continue
            a_ = next(r for r in cv if r["day_set"].startswith("all"))
            g_ = next(r for r in cv if r["day_set"].startswith("CLI"))
            l_ = next(r for r in gap if r["icao"] == ic and r["test_year"] == ty and r["day_set"].startswith("all") and
                      r["our_window"].startswith("local"))
            A(f"| {lab_ic(ic)} | {ty} | {a_['n']} / {g_['n']} | {sg2(fl_(a_, 'mean_gap'))}, {f2(fl_(a_, 'mae'))} | "
              f"{sg2(fl_(a_, 'p10'))} to {sg2(fl_(a_, 'p90'))} | {pc0(fl_(a_, 'share_equal_lt_0p05c'))} | "
              f"{sg2(fl_(l_, 'mean_gap'))}, {f2(fl_(l_, 'mae'))} | {sg2(fl_(g_, 'mean_gap'))}, {f2(fl_(g_, 'mae'))} |")
    A("")
    # E9 official scores
    A("**Table E9. Daily maximum scored against CLI: MAE and mean error, all test years** (`official_scores.csv`, which "
      "has each test year and NBS by version). Each pair set on its own days.")
    A("")
    A("| airport | pair set | forecast | all days: n, MAE, mean error | CLI and GHCN agree: n, MAE |")
    A("|---|---|---|---|---|")
    osc = T("official_scores.csv")
    for ic in US4:
        for r in osc:
            if r["icao"] == ic and r["test_year"] == "all" and r["day_set"] == "all days with CLI" and r["version"] == "all":
                g = [x for x in osc if x["icao"] == ic and x["test_year"] == "all" and x["day_set"].startswith("CLI") and
                     x["version"] == "all" and x["pair_set"] == r["pair_set"] and x["forecast"] == r["forecast"]]
                gg = f"{g[0]['n']}, {f2(fl_(g[0], 'mae'))}" if g else "-"
                A(f"| {lab_ic(ic)} | {r['pair_set']} | {r['forecast']} | {r['n']}, {f2(fl_(r, 'mae'))}, "
                  f"{sg2(fl_(r, 'mean_error'))} | {gg} |")
    A("")
    A("Truth windows: CLI is midnight to midnight local standard time from continuous readings; the forecasts are for "
      "the civil local day. Every score against CLI is descriptive.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ Step 7: --verify

NUM = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def part1_of(text):
    i = text.index("## Part 1.")
    j = text.index("\n---\n\n## Part 2.", i)
    return text[i:j].rstrip("\n") + "\n"


def run_verify(args):
    print(f"SESSION 114 --verify (ANALYSIS.md Part 1 against the tables), start {now_utc()}")
    have = part1_of(ANALYSIS.read_text(encoding="utf-8"))
    want = render_part1().rstrip("\n") + "\n"
    a, b = NUM.findall(have), NUM.findall(want)
    mism = sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
    lit = re.sub(r"\{[a-zA-Z0-9_]+\}", " ", PART1_TEMPLATE)
    literal = NUM.findall(lit)
    nplace = len(re.findall(r"\{[a-zA-Z0-9_]+\}", PART1_TEMPLATE))
    print(f"  numbers in Part 1: {len(a)}; re-rendered from the tables: {len(b)}; mismatches: {mism}; text identical: "
          f"{have == want}")
    print(f"  placeholders in the template: {nplace} (each filled from a table file); literal numbers in the template "
          f"(structural: lead bands, percentiles, entry numbers, dates, constants): {len(literal)}: "
          f"{' '.join(sorted(set(literal), key=literal.index))}")
    em = have.count("\u2014")
    print(f"  em-dashes in Part 1: {em}")
    ok = mism == 0 and have == want and em == 0
    print(f"--verify: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


# ------------------------------------------------------------------ main

MODES = ("check", "gate", "match", "hourly", "dailymax", "docs", "official", "figures", "verify")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in MODES:
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--source", choices=ORDER, default=None)
    ap.add_argument("--trial-dir", default=None, help="write tables and figures to this folder instead (trials)")
    a = ap.parse_args()
    if a.trial_dir:
        global FIG_DIR
        FIG_DIR = Path(a.trial_dir)
        s112.FIG_DIR = FIG_DIR
        if not a.figures:
            global OUT_DIR
            OUT_DIR = FIG_DIR
    if (a.hourly or a.dailymax) and not a.source:
        ap.error("--hourly and --dailymax need --source")
    mode = next(m for m in MODES if getattr(a, m))
    try:
        return globals()[f"run_{mode}"](a)
    except s113.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
