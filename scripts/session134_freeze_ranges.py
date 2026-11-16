"""Session 134: freeze the 80 % ranges at the 12 airports (DECISIONS D129.2 to D129.4).
Offline. A build step (SPEC 2.5, D72.2): these are build values, never results. Nothing valid after
2026-07-31T23:00 UTC is read or used; nothing from MLwx-live is opened; no network call is made.

What is frozen. For each airport of D103.4 and each output, one pair (P10, P90): numpy's default
(linear) 10th and 90th percentiles of past out-of-sample errors.
  hourly, range (T1):        e = obs - curve, over the airport's rows with status `scored` in session
                             112's prediction file, all leads 3 to 48 together.
  hourly, reference (RT1):   e = obs - raw_gfs, on the same rows.
  daily_max, range (M1):     e = obs_max - curve_max, over the days with `common` true.
  daily_max, reference (RM1): e = obs_max - raw_gfs_max, on the same days.
Development airports (EGLC, LFPG, KDSM, YSDU, KRNO, KSFO): the test years 2023-24, 2024-25 and
2025-26; days from data/processed/session104_dailymax_days.csv. Claim airports (EDDM, KORD, CYYZ,
ZGSZ, ZUCK, NZWN): looks A and B; days from data/processed/session107_claim_days.csv.

Modes (one per run):
  --gate    (a) with this script's own row loaders and session 133's build_table, rebuild at the six
            development airports the tables session 133 used for scoring period 2025-26 (built from
            2023-24 and 2024-25) for T1, RT1, M1 and RM1: all 24 rows must equal
            data/processed/session133_ranges/tables.csv's p10, p90 and n at full precision.
            (b) at each airport the `scored` rows used equal meta.txt's per-period counts summed; the
            `common` days used per airport are reported; every e is finite.
            (c) no row or day used is valid after 2026-07-31T23:00 UTC.
            Writes nothing.
  --freeze  the gate again, then writes src/mlwx/data/gfs_ranges.csv (48 rows; refuses to overwrite)
            and data/processed/session134_ranges/meta.txt. Run once.
  --detail FILE  with either mode: also append the full tables to FILE.

Imported read only, each after its SHA-256 is checked equal to HEAD's blob at ff8c074 (D116.10;
session 134's Step 1): scripts/session133_ranges.py (build_table, PCT, EARLIER, TEST_YEARS,
LAST_VALID, LAST_DAY, fast_time, sha256_file, now_utc, versions) and scripts/session112_analysis.py
(DEV_ICAO, CLAIM_ICAO, STATION, GROUP, PRED_DIR, PRED_META, PRED_COLUMNS, load_pred_rows and its
SHA-256 check against meta.txt, S104_DAYS, S107_DAYS and their recorded SHA-256). No function of
theirs is changed or copied.

Readings fixed here (D129 leaves them open):
  1. A day is "valid" at its last hour: its cycle plus its last lead (D98.10(a)). Check (c) uses
     that time for days, and the valid time for hourly rows.
  2. A claim airport's station code is checked three ways: session 112's STATION, the prediction
     file's `station` column, and session 107's days file's `station` column (KORD is `ORD`).
  3. The file's floats are written by `repr`, so they read back to the same number.
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# Session 134's Step 1: each equal to HEAD's blob at ff8c074. Checked before any import.
IMPORTED_SHA256 = {
    "session133_ranges.py": "4bbe4ceaec5c72057bba0ad8f6f744b7a634016e6fcd935412db3436d28875b2",
    "session112_analysis.py": "bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab",
}
for _name, _want in IMPORTED_SHA256.items():
    if _sha256(HERE / _name) != _want:
        raise SystemExit(f"STOP: scripts/{_name}'s SHA-256 is not session 134's recorded value")
sys.path.insert(0, str(HERE))
import session133_ranges as s133  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import io  # noqa: E402
import time  # noqa: E402

import numpy as np  # noqa: E402

s112 = s133.s112
for _mod, _name in ((s133, "session133_ranges.py"), (s112, "session112_analysis.py")):
    if Path(_mod.__file__).resolve() != HERE / _name:
        raise SystemExit(f"STOP: {_name} was imported from {_mod.__file__}")

# ------------------------------------------------------------------ constants

# D103.4's order (D129.2). Checked against session 112's lists below.
AIRPORTS = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]
DEV = list(s112.DEV_ICAO)
CLAIM = list(s112.CLAIM_ICAO)
if AIRPORTS != DEV + CLAIM:
    raise SystemExit("STOP: the 12 airports are not session 112's development then claim airports")
STATION = {ic: s112.STATION[ic] for ic in AIRPORTS}      # ICAO -> the files' station code
if len(set(STATION.values())) != len(AIRPORTS):
    raise SystemExit("STOP: two airports share a station code")
DEV_PERIODS = tuple(s133.TEST_YEARS)                     # 2023-24, 2024-25, 2025-26
CLAIM_PERIODS = ("A", "B")                               # looks A and B (2024-25, 2025-26)
PERIODS = {ic: (DEV_PERIODS if ic in DEV else CLAIM_PERIODS) for ic in AIRPORTS}
LAST_VALID = s133.LAST_VALID                             # 2026-07-31T23:00 UTC
if LAST_VALID != dt.datetime(2026, 7, 31, 23, 0):
    raise SystemExit("STOP: LAST_VALID is not 2026-07-31T23:00")
LAST_DAY = s133.LAST_DAY
OUTPUTS = ("hourly", "daily_max")                        # the file's order
KINDS = ("range", "reference")
COLUMNS = ["airport", "output", "kind", "p10", "p90", "n"]
N_ROWS = len(AIRPORTS) * len(OUTPUTS) * len(KINDS)       # 48

# Session 134's Step 1 values; session 112 records the same two.
DAYS_FILES = {
    "dev": (s112.S104_DAYS, "65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3"),
    "claim": (s112.S107_DAYS, "3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297"),
}
if DAYS_FILES["dev"][1] != s112.S104_DAYS_SHA256 or DAYS_FILES["claim"][1] != s112.S107_DAYS_SHA256:
    raise SystemExit("STOP: a days file's SHA-256 here is not session 112's")

S133_TABLES = ROOT / "data" / "processed" / "session133_ranges" / "tables.csv"
GATE_PERIOD = "2025-26"
GATE_CANDIDATES = {("hourly", "range"): "T1", ("hourly", "reference"): "RT1",
                   ("daily_max", "range"): "M1", ("daily_max", "reference"): "RM1"}

OUT_CSV = ROOT / "src" / "mlwx" / "data" / "gfs_ranges.csv"
META_DIR = ROOT / "data" / "processed" / "session134_ranges"
META = META_DIR / "meta.txt"


# ------------------------------------------------------------------ pure pieces (tested)

def pair(e, period=None, use=None):
    """(p10, p90, n) of the errors whose period is in `use` (all of them if `use` is None), by
    session 133's build_table: numpy's default (linear) 10th and 90th percentiles (D128.5)."""
    e = np.asarray(e, dtype=float)
    if period is None:
        period, use = np.zeros(len(e), dtype=int), (0,)
    table = s133.build_table(e, np.zeros(len(e), dtype=int), period, use)
    if set(table) != {0}:
        raise SystemExit("STOP: no error to build a pair from")
    return table[0]


def freeze_rows(errors):
    """The file's rows from {airport: {output: {kind: errors}}}: one (airport, output, kind, p10, p90,
    n) per airport of `errors` in its own order, hourly before daily_max, range before reference."""
    rows = []
    for ic, by_output in errors.items():
        for output in OUTPUTS:
            for kind in KINDS:
                e = np.asarray(by_output[output][kind], dtype=float)
                if not np.all(np.isfinite(e)):
                    raise SystemExit(f"STOP: {ic} {output} {kind} has an error that is not finite")
                p10, p90, n = pair(e)
                rows.append((ic, output, kind, p10, p90, n))
    return rows


def ranges_csv_text(rows):
    """The file's text: the header, then one line per row, floats by repr."""
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(COLUMNS)
    for ic, output, kind, p10, p90, n in rows:
        w.writerow([ic, output, kind, repr(float(p10)), repr(float(p90)), int(n)])
    return out.getvalue()


def write_once(path, text):
    """Write a new file; stop if it exists (the freeze is never overwritten)."""
    path = Path(path)
    if path.exists():
        raise SystemExit(f"STOP: {path} already exists; the freeze is not overwritten")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="") as f:
        f.write(text)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ------------------------------------------------------------------ reading

def meta_counts():
    """{(ICAO, period): scored rows} for the 12 prediction files, from session 112's meta.txt."""
    out, cur = {}, None
    for line in s112.PRED_META.read_text().splitlines():
        p = line.split()
        if p and p[0].startswith("pred_") and p[0].endswith(".csv.gz"):
            cur = p[0][5:-7]
            continue
        if cur is not None and line.startswith("    "):
            for part in line.strip().split("; "):
                per, status, n = part.split()
                if status == "scored":
                    out[(cur, per)] = int(n.replace(",", ""))
    return out


def load_hourly(ic):
    """One airport's scored rows in its periods: period, e = obs - curve, e_ref = obs - raw_gfs, and
    the latest valid time used. Session 112's loader checks the file against meta.txt's SHA-256."""
    rows = s112.load_pred_rows(ic)
    ix = {c: i for i, c in enumerate(s112.PRED_COLUMNS)}
    period, obs, curve, raw, last = [], [], [], [], None
    for r in rows:
        if r[ix["icao"]] != ic or r[ix["station"]] != STATION[ic] or r[ix["group"]] != s112.GROUP[ic]:
            raise SystemExit(f"STOP: {ic} a row names another airport, station or group")
        if r[ix["status"]] != "scored":
            continue
        if r[ix["period"]] not in PERIODS[ic]:
            raise SystemExit(f"STOP: {ic} scored row in period {r[ix['period']]}")
        lead = int(r[ix["lead"]])
        if not 3 <= lead <= 48:
            raise SystemExit(f"STOP: {ic} scored row at lead {lead}")
        val = s133.fast_time(r[ix["valid_utc"]])
        if val != s133.fast_time(r[ix["cycle_utc"]]) + dt.timedelta(hours=lead):
            raise SystemExit(f"STOP: {ic} valid time is not cycle plus lead")
        if val > LAST_VALID:
            raise SystemExit(f"STOP: {ic} row valid at {val} is after {LAST_VALID}")
        last = val if last is None or val > last else last
        period.append(r[ix["period"]])
        obs.append(float(r[ix["obs"]]))
        curve.append(float(r[ix["curve"]]))
        raw.append(float(r[ix["raw_gfs"]]))
    del rows
    obs, curve, raw = np.array(obs), np.array(curve), np.array(raw)
    return {"period": np.array(period), "e": obs - curve, "e_ref": obs - raw, "last_valid": last}


def load_daily():
    """{ICAO: ...} for the 12 airports: the days with common true, their period, e = obs_max -
    curve_max, e_ref = obs_max - raw_gfs_max, and the latest valid hour used. Both files are checked
    against their recorded SHA-256."""
    per = {ic: [] for ic in AIRPORTS}
    icao_of_station = {STATION[ic]: ic for ic in DEV}
    for group, (path, want) in DAYS_FILES.items():
        data = Path(path).read_bytes()
        if hashlib.sha256(data).hexdigest() != want:
            raise SystemExit(f"STOP: {Path(path).name}'s SHA-256 is not the recorded value")
        for r in csv.DictReader(io.StringIO(data.decode())):
            if group == "dev":
                if r["station"] not in icao_of_station:
                    raise SystemExit(f"STOP: session 104's days file has station {r['station']}")
                ic, label = icao_of_station[r["station"]], r["fold"]
            else:
                ic, label = r["icao"], r["look"]
                if ic not in CLAIM or r["station"] != STATION[ic]:
                    raise SystemExit(f"STOP: session 107's days file has {ic} with station {r['station']}")
            if r["common"] not in ("true", "false"):
                raise SystemExit("STOP: a days file's common is not true or false")
            if r["common"] != "true":
                continue
            if label not in PERIODS[ic]:
                raise SystemExit(f"STOP: {ic} common day in period {label}")
            day = dt.date.fromisoformat(r["local_date"])
            last_hour = s133.fast_time(r["cycle"]) + dt.timedelta(hours=int(r["last_lead"]))
            if day > LAST_DAY or last_hour > LAST_VALID:
                raise SystemExit(f"STOP: {ic} day {day} ends at {last_hour}, after {LAST_VALID}")
            per[ic].append((r["local_date"], label, float(r["obs_max"]), float(r["curve_max"]),
                            float(r["raw_gfs_max"]), last_hour))
    out = {}
    for ic, rows in per.items():
        if not rows:
            raise SystemExit(f"STOP: {ic} has no common day")
        rows.sort(key=lambda t: t[0])
        obs = np.array([t[2] for t in rows])
        out[ic] = {"period": np.array([t[1] for t in rows]), "e": obs - np.array([t[3] for t in rows]),
                   "e_ref": obs - np.array([t[4] for t in rows]), "last_valid": max(t[5] for t in rows)}
    return out


def load_all(log):
    t = time.time()
    hourly = {ic: load_hourly(ic) for ic in AIRPORTS}
    daily = load_daily()
    log(f"read the 12 prediction files and the two days files ({time.time() - t:.0f} s)")
    return {ic: {"hourly": hourly[ic], "daily_max": daily[ic]} for ic in AIRPORTS}


def s133_tables():
    """{(candidate, airport): (p10, p90, n)} of session 133's tables for scoring period 2025-26."""
    out = {}
    with open(S133_TABLES, newline="") as f:
        for r in csv.DictReader(f):
            if r["scoring_period"] == GATE_PERIOD and r["candidate"] in GATE_CANDIDATES.values():
                if r["cell"] != "all" or (r["candidate"], r["airport"]) in out:
                    raise SystemExit("STOP: session 133's tables file is not one row per airport here")
                out[(r["candidate"], r["airport"])] = (float(r["p10"]), float(r["p90"]), int(r["n_earlier"]))
    return out


# ------------------------------------------------------------------ the gate

def run_gate_checks(X, log, detail):
    ok = True

    # (a) session 133's 2025-26 tables, rebuilt with this script's loaders.
    want = s133_tables()
    equal, lines = 0, []
    for ic in DEV:
        for (output, kind), cand in GATE_CANDIDATES.items():
            d = X[ic][output]
            got = pair(d["e" if kind == "range" else "e_ref"], d["period"], s133.EARLIER[GATE_PERIOD])
            same = want.get((cand, ic)) == got
            equal += same
            lines.append(f"  {cand:<3} {ic} {'equal' if same else 'DIFFERENT'}: p10 {got[0]!r} p90 {got[1]!r} n {got[2]}")
    a_ok = equal == 24 and len(want) == 24
    ok &= a_ok
    log(f"gate (a): {equal} of 24 rows equal session 133's tables.csv at full precision: {'PASS' if a_ok else 'FAIL'}")
    detail("Gate (a): session 133's tables for scoring period 2025-26, rebuilt")
    for line in lines:
        detail(line)

    # (b) counts and finite errors.
    counts = meta_counts()
    b_ok, finite = True, True
    detail("Gate (b): scored rows used against meta.txt, and common days used")
    for ic in AIRPORTS:
        h, d = X[ic]["hourly"], X[ic]["daily_max"]
        per = {p: int(np.sum(h["period"] == p)) for p in PERIODS[ic]}
        meta = {p: counts.get((ic, p)) for p in PERIODS[ic]}
        same = per == meta and len(h["e"]) == sum(per.values())
        b_ok &= same
        fin = all(np.all(np.isfinite(v[k])) for v in (h, d) for k in ("e", "e_ref"))
        finite &= bool(fin)
        days = "; ".join(f"{p} {int(np.sum(d['period'] == p))}" for p in PERIODS[ic])
        detail(f"  {ic}: scored rows {len(h['e']):,} ({'; '.join(f'{p} {n:,}' for p, n in per.items())}), "
               f"meta.txt {sum(v or 0 for v in meta.values()):,}: {'equal' if same else 'DIFFERENT'}; "
               f"common days {len(d['e']):,} ({days}); every e finite: {'yes' if fin else 'NO'}")
    ok &= b_ok and finite
    lo = min(len(X[ic]["daily_max"]["e"]) for ic in AIRPORTS)
    hi = max(len(X[ic]["daily_max"]["e"]) for ic in AIRPORTS)
    log(f"gate (b): scored rows equal meta.txt's summed counts at 12 of 12 airports: {'PASS' if b_ok else 'FAIL'}; "
        f"common days per airport {lo:,} to {hi:,}; every e finite: {'PASS' if finite else 'FAIL'}")

    # (c) nothing valid after 2026-07-31T23:00 UTC.
    latest = max(X[ic][o]["last_valid"] for ic in AIRPORTS for o in OUTPUTS)
    c_ok = latest <= LAST_VALID
    ok &= c_ok
    detail("Gate (c): the latest valid time used (hourly row; last hour of a day)")
    for ic in AIRPORTS:
        detail(f"  {ic}: hourly {X[ic]['hourly']['last_valid']:%Y-%m-%dT%H:%MZ}; "
               f"daily_max {X[ic]['daily_max']['last_valid']:%Y-%m-%dT%H:%MZ}")
    log(f"gate (c): latest valid time used {latest:%Y-%m-%dT%H:%MZ}, not after "
        f"{LAST_VALID:%Y-%m-%dT%H:%MZ}: {'PASS' if c_ok else 'FAIL'}")
    return bool(ok)


def make_detail(path):
    if path is None:
        return lambda line: None

    def detail(line):
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    return detail


def run_gate(args):
    print(f"SESSION 134 --gate (offline), start {s133.now_utc()}; {s133.versions()}")
    X = load_all(print)
    ok = run_gate_checks(X, print, make_detail(args.detail))
    print(f"GATE: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------------------------------------ the freeze

def run_freeze(args):
    t = time.time()
    print(f"SESSION 134 --freeze (offline), start {s133.now_utc()}; {s133.versions()}")
    print("BUILD VALUES, NEVER RESULTS (SPEC 2.5, D129.2).")
    for p in (OUT_CSV, META):
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists; the freeze is not overwritten")
    detail = make_detail(args.detail)
    X = load_all(print)
    if not run_gate_checks(X, print, detail):
        print("GATE: FAIL; nothing written")
        return 1
    print("GATE: PASS")
    errors = {ic: {o: {"range": X[ic][o]["e"], "reference": X[ic][o]["e_ref"]} for o in OUTPUTS}
              for ic in AIRPORTS}
    rows = freeze_rows(errors)
    if len(rows) != N_ROWS or any(not r[3] < r[4] for r in rows):
        raise SystemExit("STOP: the table is not 48 rows with p10 < p90")
    sha = write_once(OUT_CSV, ranges_csv_text(rows))
    if _sha256(OUT_CSV) != sha:
        raise SystemExit("STOP: the file on disk is not the text written")

    detail("The frozen file's 48 rows (build values, never results); width = p90 - p10, degrees C")
    detail("  airport output    kind      p10                     p90                     n        width")
    for ic, output, kind, p10, p90, n in rows:
        detail(f"  {ic:<7} {output:<9} {kind:<9} {p10!r:<23} {p90!r:<23} {n:<8} {p90 - p10:.4f}")

    here = Path(__file__).resolve()
    lines = [
        "Session 134: the frozen 80 % ranges at the 12 airports (D129.2 to D129.4). Build values, never results.",
        f"written by scripts/{here.name} --freeze",
        f"run {s133.now_utc()}; run time {time.time() - t:.0f} s; {s133.versions()}",
        f"script SHA-256 {_sha256(here)}",
        f"output src/mlwx/data/{OUT_CSV.name}  rows {len(rows)}  sha256 {sha}",
        "gate: PASS ((a) 24 of 24 rows equal session 133's tables.csv; (b) scored rows equal meta.txt; (c) nothing "
        f"valid after {LAST_VALID:%Y-%m-%dT%H:%MZ})",
        "percentiles: numpy.percentile(e, [10, 90]), linear, by session 133's build_table",
        "inputs (SHA-256):",
    ]
    for name, want in IMPORTED_SHA256.items():
        lines.append(f"  scripts/{name}  {want}")
    lines.append(f"  ../MLwx-stagec/analysis112/meta.txt  {_sha256(s112.PRED_META)}")
    hashes = s112.pred_hashes()
    for ic in AIRPORTS:
        lines.append(f"  ../MLwx-stagec/analysis112/pred_{ic}.csv.gz  {hashes[f'pred_{ic}.csv.gz']}")
    for path, want in DAYS_FILES.values():
        lines.append(f"  data/processed/{Path(path).name}  {want}")
    lines.append(f"  data/processed/session133_ranges/tables.csv  {_sha256(S133_TABLES)}  (gate (a) only)")
    lines.append("rows used (scored hourly rows; common days):")
    for ic in AIRPORTS:
        lines.append(f"  {ic}  periods {', '.join(PERIODS[ic])}  hourly {len(X[ic]['hourly']['e'])}  "
                     f"daily_max {len(X[ic]['daily_max']['e'])}")
    write_once(META, "\n".join(lines) + "\n")

    width = {(o, k): [r[4] - r[3] for r in rows if r[1] == o and r[2] == k] for o in OUTPUTS for k in KINDS}
    for (o, k), w in width.items():
        print(f"{o} {k}: width {min(w):.3f} to {max(w):.3f} C over the 12 airports")
    print(f"wrote {OUT_CSV.relative_to(ROOT)} ({len(rows)} rows, sha256 {sha}) and {META.relative_to(ROOT)}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--gate", action="store_true")
    g.add_argument("--freeze", action="store_true")
    ap.add_argument("--detail", help="also append the full tables to this file")
    args = ap.parse_args()
    return run_gate(args) if args.gate else run_freeze(args)


if __name__ == "__main__":
    sys.exit(main())
