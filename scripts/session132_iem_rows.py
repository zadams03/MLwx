#!/usr/bin/env python3
"""Session 132: AIFS and the NBM grid read at the airport's own position (the `iem` set) at the development
airports (DECISIONS D127.5). Descriptive only (D107.2): no verdict, model, setting, rule, bar or table changes.

Everything is as D108.3, D108.4 and session 114's code, except one thing: at the six development airports the
competitor is read at the `iem` position set in place of the `gfs` set. The curve and raw GFS stay at GFS's own
position (SPEC 3.4). AIFS's elevation treatment uses its terrain at the `iem` points and the same station
elevation (session 114's Comp does this when SET is `iem`); the NBM grid has no treatment, as before.

Method (D127.5(c)): scripts/session114_comparisons.py is imported read-only after its SHA-256 is checked against
D127.5's value (it checks sessions 112 and 113 itself). This script sets that module's OUT_DIR and, for the six
development airports, its SET to `iem` at run time, and runs its run_hourly and run_dailymax for `aifs` and `nbm`
unchanged, seed 114. No function of session 114 is changed.

Modes, run in this order:
  --gate      D127.5(d) first check. The four runs with SET unchanged, into a new temporary folder under $TMPDIR
              (kept, path printed): every table equals session 114's committed file of the same name byte for
              byte (18 files).
  --run       The four `iem` runs into data/processed/session132_iem/, then D127.5(d)'s second check: every row
              for a claim airport equals session 114's committed row, except the Benjamini-Hochberg column
              (bh_reject_q005) of the _dm.csv files, which depends on the whole family. Writes meta.txt.
  --summary   summary.csv (D127.5(e)) and the count of D127.5(f), from the two sets of tables. Writes
              summary_meta.txt.

Network: none. Nothing valid after 2026-07-31T23:00 UTC is read (session 113's guards, applied by session 114's
loaders). Nothing from the 37 airports of F153.6 is read. No em-dashes in any text here (D76.6).
"""

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

S114_SHA256 = "5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52"   # D127.5(c)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256_file(HERE / "session114_comparisons.py") != S114_SHA256:
    raise SystemExit("STOP: scripts/session114_comparisons.py's SHA-256 is not D127.5's value")
sys.path.insert(0, str(HERE))
import session114_comparisons as s114  # noqa: E402

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import os  # noqa: E402
import tempfile  # noqa: E402
import time  # noqa: E402

PROCESSED = ROOT / "data" / "processed"
S114_DIR = PROCESSED / "session114_comparisons"          # read only
OUT = PROCESSED / "session132_iem"
SOURCES = ("aifs", "nbm")
OUTPUTS = ("hourly", "dailymax")
SEED = 114
MARK_C = 0.05                                            # D127.5(f): position matters when |change| >= 0.05 C

DEV = [ic for ic in s114.AIRPORTS if s114.GROUP[ic] == "dev"]
CLAIM = [ic for ic in s114.AIRPORTS if s114.GROUP[ic] == "claim"]
GFS_SET = dict(s114.SET)                                 # session 114's sets, kept before any change
IEM_SET = {ic: ("iem" if ic in DEV else GFS_SET[ic]) for ic in s114.AIRPORTS}

TABLE_SUFFIXES = {"hourly": ("", "_skill", "_breakdown", "_dm"),
                  "dailymax": ("", "_skill", "_breakdown", "_dm", "_every_cycle")}
BH_COL = "bh_reject_q005"


def table_names():
    return [f"{o}_{s}{x}.csv" for s in SOURCES for o in OUTPUTS for x in TABLE_SUFFIXES[o]]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def check_sets():
    if GFS_SET != {ic: ("gfs" if s114.GROUP[ic] == "dev" else "iem") for ic in s114.AIRPORTS}:
        raise SystemExit("STOP: session 114's SET is not D108.3's")
    if len(DEV) != 6 or len(CLAIM) != 6:
        raise SystemExit("STOP: not six development and six claim airports")


def run_four(out_dir, sets):
    """Session 114's run_hourly and run_dailymax for aifs and nbm, unchanged, into out_dir with the given sets."""
    s114.OUT_DIR = Path(out_dir)
    s114.SET = dict(sets)
    for src in SOURCES:
        for out in OUTPUTS:
            del s114._TABLES[:]                          # its print list only; one run's tables each time
            fn = s114.run_hourly if out == "hourly" else s114.run_dailymax
            rc = fn(argparse.Namespace(source=src))
            if rc != 0:
                raise SystemExit(f"STOP: {out} {src} returned {rc}")


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# ------------------------------------------------------------------ --gate

def run_gate(args):
    check_sets()
    tmp = Path(tempfile.mkdtemp(prefix="session132_iem_gate_", dir=os.environ.get("TMPDIR")))
    print(f"SESSION 132 --gate (D127.5(d), first check), {now_utc()}; {s114.versions_text()}; seed {SEED}")
    print(f"  temporary folder (kept): {tmp}")
    run_four(tmp, GFS_SET)
    names = table_names()
    written = sorted(p.name for p in tmp.iterdir() if p.suffix == ".csv")
    equal = 0
    for n in names:
        same = (tmp / n).read_bytes() == (S114_DIR / n).read_bytes()
        equal += same
        print(f"  {n}: {'byte-equal' if same else 'DIFFERENT'} to session 114's committed file")
    extra = sorted(set(written) - set(names))
    ok = equal == len(names) == 18 and not extra
    print(f"  tables byte-equal {equal} of {len(names)}; other files written {extra or 'none'}")
    print("GATE (D127.5(d), first check): PASS" if ok else "GATE (D127.5(d), first check): FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ --run

def claim_check(folder):
    """D127.5(d)'s second check. Returns (rows compared, rows different, BH values different, tables)."""
    n_cmp = n_bad = n_bh = 0
    for n in table_names():
        new = [r for r in read_rows(folder / n) if r["icao"] in CLAIM]
        old = [r for r in read_rows(S114_DIR / n) if r["icao"] in CLAIM]
        bad = 0
        if len(new) != len(old):
            bad += abs(len(new) - len(old))
        for a, b in zip(new, old):
            if n.endswith("_dm.csv"):
                n_bh += a[BH_COL] != b[BH_COL]
                a = {k: v for k, v in a.items() if k != BH_COL}
                b = {k: v for k, v in b.items() if k != BH_COL}
            bad += a != b
        n_cmp += len(old)
        n_bad += bad
        print(f"  {n}: claim-airport rows {len(old)}, equal {len(old) - bad if len(new) == len(old) else 'n/a'}, "
              f"different {bad}")
    return n_cmp, n_bad, n_bh


def run_run(args):
    check_sets()
    if OUT.exists():
        raise SystemExit(f"STOP: {OUT} already exists; tables are written once")
    t0 = time.time()
    start = now_utc()
    print(f"SESSION 132 --run (D127.5; descriptive, D107.2), {start}; {s114.versions_text()}; seed {SEED}")
    print("  sets: " + ", ".join(f"{ic} {IEM_SET[ic]}" for ic in s114.AIRPORTS))
    OUT.mkdir(parents=True)
    run_four(OUT, IEM_SET)
    print("D127.5(d), second check (claim airports' rows against session 114's):")
    n_cmp, n_bad, n_bh = claim_check(OUT)
    ok = n_bad == 0 and n_cmp > 0
    print(f"  claim-airport rows compared {n_cmp}, different {n_bad}; Benjamini-Hochberg values that differ "
          f"(excluded by D127.5(d)) {n_bh}")
    lines = [f"Session 132 iem-position tables (D127.5), written by scripts/session132_iem_rows.py --run.",
             f"run {start}; run time {time.time() - t0:.0f} s; {s114.versions_text()}; seed {SEED}",
             f"script SHA-256 {sha256_file(Path(__file__))}",
             f"session114_comparisons.py SHA-256 {S114_SHA256} (imported read-only; OUT_DIR and SET set at run time)",
             "sets: development airports iem (the airport's own position), claim airports iem (unchanged, D108.3)",
             f"claim-airport check (D127.5(d)): rows compared {n_cmp}, different {n_bad}: "
             + ("PASS" if ok else "FAIL"),
             "files:"]
    for n in table_names():
        p = OUT / n
        lines.append(f"  {n}  rows {len(read_rows(p))}  sha256 {sha256_file(p)}")
    s114.s112.write_once_bytes(OUT / "meta.txt", ("\n".join(lines) + "\n").encode())
    print(f"  meta.txt written; run time {time.time() - t0:.0f} s")
    print("CLAIM-AIRPORT CHECK (D127.5(d), second check): PASS" if ok else
          "CLAIM-AIRPORT CHECK (D127.5(d), second check): FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ --summary

SUM_COLS = ["icao", "source", "output", "n_gfs", "mae_comp_gfs", "me_comp_gfs", "mae_curve_gfs", "skill_gfs",
            "n_iem", "mae_comp_iem", "me_comp_iem", "mae_curve_iem", "skill_iem", "mae_comp_change",
            "position_matters", "dm_diff_gfs", "dm_dir_gfs", "bh_gfs", "dm_diff_iem", "dm_dir_iem", "bh_iem"]


def one(rows, **kw):
    out = [r for r in rows if all(r[k] == v for k, v in kw.items())]
    if len(out) != 1:
        raise SystemExit(f"STOP: {len(out)} rows for {kw}")
    return out[0]


def side(folder, src, out, ic):
    head = read_rows(folder / f"{out}_{src}.csv")
    skill = read_rows(folder / f"{out}_{src}_skill.csv")
    dm = read_rows(folder / f"{out}_{src}_dm.csv")
    c = one(head, icao=ic, test_year="all", forecast="comp")
    k = one(head, icao=ic, test_year="all", forecast="curve")
    s = one(skill, icao=ic, test_year="all", a="curve", b="comp")
    d = one(dm, icao=ic)
    diff = float(d["mean_daily_diff"])
    direction = "curve better" if diff < 0 else ("competitor better" if diff > 0 else "equal")
    return dict(n=int(c["n"]), mae=float(c["mae"]), me=float(c["mean_error"]), curve=float(k["mae"]),
                skill=float(s["skill_a_vs_b"]), diff=diff, dir=direction, bh=d[BH_COL])


def run_summary(args):
    if not (OUT / "meta.txt").exists():
        raise SystemExit("STOP: run --run first")
    print(f"SESSION 132 --summary (D127.5(e), (f); descriptive), {now_utc()}")
    rows, marks = [], {}
    for src in SOURCES:
        airports = [ic for ic in s114.SOURCES[src]["airports"] if ic in DEV]
        for out in OUTPUTS:
            for ic in airports:
                g, i = side(S114_DIR, src, out, ic), side(OUT, src, out, ic)
                change = i["mae"] - g["mae"]
                matters = abs(change) >= MARK_C
                marks.setdefault((src, out), []).append((ic, matters))
                rows.append([ic, src, out, g["n"], g["mae"], g["me"], g["curve"], g["skill"], i["n"], i["mae"],
                             i["me"], i["curve"], i["skill"], change, matters, g["diff"], g["dir"], g["bh"],
                             i["diff"], i["dir"], i["bh"]])
                print(f"  {ic} {src:4s} {out:8s} n {g['n']:6d} -> {i['n']:6d}  MAE comp {g['mae']:.3f} -> {i['mae']:.3f} "
                      f"({change:+.3f}{' MARK' if matters else ''})  ME comp {g['me']:+.3f} -> {i['me']:+.3f}  "
                      f"curve {g['curve']:.3f} -> {i['curve']:.3f}  skill {100 * g['skill']:+.1f} -> "
                      f"{100 * i['skill']:+.1f} %  DM {g['dir']} (BH {g['bh']}) -> {i['dir']} (BH {i['bh']})")
    text = s114.s97.csv_text(SUM_COLS, [[v if isinstance(v, str) else s114.s112.fmt(s114.s112.plain(v)) for v in r]
                                        for r in rows])
    s114.s112.write_once_bytes(OUT / "summary.csv", text.encode())
    print("D127.5(f): the competitor's pooled MAE changes by at least 0.05 C between the sets (counted, never judged):")
    any_mark = set()
    for (src, out), lst in marks.items():
        hit = [ic for ic, m in lst if m]
        any_mark |= set(hit)
        print(f"  {src} {out}: {len(hit)} of {len(lst)}" + (f" ({', '.join(hit)})" if hit else ""))
    print(f"  airports with the mark in any source or output: {len(any_mark)} of 6"
          + (f" ({', '.join(sorted(any_mark))})" if any_mark else ""))
    meta = [f"Session 132 summary (D127.5(e), (f)), written by scripts/session132_iem_rows.py --summary.",
            f"run {now_utc()}; {s114.versions_text()}",
            f"script SHA-256 {sha256_file(Path(__file__))}",
            "gfs-set values from data/processed/session114_comparisons/ (session 114's committed tables); iem-set "
            "values from this folder. Pooled rows (test_year all); daily maximum: D98.10's days (primary), the "
            "competitor's primary maximum (forecast comp).",
            "dm_diff: mean daily difference of |curve error| minus |competitor error|; negative is the curve better.",
            f"position_matters: |mae_comp_change| >= {MARK_C} C (D127.5(f)).",
            f"summary.csv  rows {len(rows)}  sha256 {hashlib.sha256(text.encode()).hexdigest()}"]
    s114.s112.write_once_bytes(OUT / "summary_meta.txt", ("\n".join(meta) + "\n").encode())
    print(f"  summary.csv: {len(rows)} rows, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("gate", "run", "summary"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    try:
        if a.gate:
            return run_gate(a)
        if a.run:
            return run_run(a)
        return run_summary(a)
    except s114.s113.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
