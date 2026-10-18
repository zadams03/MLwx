#!/usr/bin/env python3
"""Session 117: ECMWF IFS in the field guide (DECISIONS D111, finding F160).

Modes (docs/sessions/session-117.md, Steps 4 and 5):
  --subset   The mx2t3 subset of D111.4 on common days (owner's ruling in session 117's Step 4: session
             114's tables are aggregates, so IFS's 3-hourly steps cannot be rescored on the mx2t3 days from
             them). Imports scripts/session114_comparisons.py read only, after its SHA-256 check, and rebuilds
             the D98.10 day records with that script's own functions. Gate first, before anything new is
             scored: at every airport and test year the rebuilt records must give exactly the days, MAE and
             mean error of mx2t3 and the skill of the curve against mx2t3 (so the curve's MAE on those days)
             that session 114's script wrote to dailymax_ifs.csv and dailymax_ifs_skill.csv; any mismatch
             stops. Then mx2t3, IFS's 3-hourly steps, the curve, the curve at IFS's steps and raw GFS are
             scored on exactly the same days. Descriptive only: 7-day block bootstrap, seed 117, 10,000
             resamples; no formal test. Writes data/processed/session117_ifs/dailymax_ifs_mx2t3_subset.csv,
             dailymax_ifs_mx2t3_subset_skill.csv and subset_meta.txt.
  --render   Edits ANALYSIS.md from the tables only: the IFS tables of Steps 2 to 4
             (session117_ifs/match_counts.csv's IFS rows, session114_comparisons/{hourly,dailymax}_ifs*.csv)
             and the --subset tables. Changed: the header's and item 1's "ECMWF IFS is pending (D108.2)"
             sentences, the 24 "pending (D108.2)" cells of Tables 2a and 2b, item 4's two formal-test lines,
             Part 2's "ECMWF IFS: pending (D108.2), not pulled yet." phrase (line 5 and that phrase by the
             owner's ruling), and new Tables E10 onward after Table E9. Runs only on the committed text.
  --verify   Re-renders from the committed ANALYSIS.md (git HEAD) and compares with the file (text identical,
             number tokens equal); checks each IFS cell of Tables 2a and 2b and each pooled row of Tables E11
             and E13 against its table independently; counts em-dashes in the edited text; lists every
             changed line of the diff against HEAD by kind and fails on any other change.

No figure is made (session 114's figures exclude IFS). No em-dashes in any text here (D76.6).
"""

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import difflib  # noqa: E402
import hashlib  # noqa: E402
import importlib.util  # noqa: E402
import io  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
ANALYSIS = ROOT / "ANALYSIS.md"
T114 = ROOT / "data" / "processed" / "session114_comparisons"
T117 = ROOT / "data" / "processed" / "session117_ifs"
S114_SCRIPT = HERE / "session114_comparisons.py"
S114_SCRIPT_SHA256 = "5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52"   # session 114's commit (F157)
SEED = 117

AIRPORTS = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN", "EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO"]
DEV = {"EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO"}
SEA = {"CYYZ", "ZGSZ", "NZWN", "KSFO"}                     # D106.11
YEARS = ("2023-24", "2024-25", "2025-26")
NAME = "ECMWF IFS"

SUB_COLS = ["icao", "group", "test_year", "forecast", "label", "n", "mae", "mae_lo", "mae_hi", "mean_error", "me_lo",
            "me_hi"]
SUB_SKILL_COLS = ["icao", "group", "test_year", "a", "b", "n", "skill_a_vs_b", "lo", "hi"]
SUB_LABEL = {"comp2": "mx2t3: highest of its 3-hour windows wholly inside the local day",
             "comp": "IFS: highest of its 3-hourly steps inside the local day (3-hourly steps, D111.4 primary)",
             "curve": "the curve (D98.10)", "curve_at": "the curve sampled at IFS's 3-hourly steps",
             "raw_gfs": "raw GFS (D98.10)"}
SUB_PAIRS = [("curve", "comp2"), ("comp", "comp2"), ("curve", "comp"), ("curve_at", "comp2"), ("raw_gfs", "comp2")]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    return sha256_bytes(Path(p).read_bytes())


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def lab_ic(ic):
    return ic + (" (dev)" if ic in DEV else "") + (" (sea)" if ic in SEA else "")


def read_csv(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def write_once(path, text):
    path = Path(path)
    if path.exists():
        raise SystemExit(f"STOP: {path} already exists; not overwriting it")
    with open(path, "x", newline="") as f:
        f.write(text)


def csv_text(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return buf.getvalue()


# ------------------------------------------------------------------ --subset (owner's ruling, Step 4)

def load_s114():
    if sha256_file(S114_SCRIPT) != S114_SCRIPT_SHA256:
        raise SystemExit("STOP: scripts/session114_comparisons.py's SHA-256 is not session 114's committed one")
    sys.path.insert(0, str(HERE))
    spec = importlib.util.spec_from_file_location("session114_comparisons", S114_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_subset(args):
    t0 = time.time()
    print(f"SESSION 117 --subset (mx2t3 days, descriptive, D111.4; owner's ruling), start {now_utc()}")
    outs = [T117 / "dailymax_ifs_mx2t3_subset.csv", T117 / "dailymax_ifs_mx2t3_subset_skill.csv",
            T117 / "subset_meta.txt"]
    for p in outs:
        if p.exists():
            raise SystemExit(f"STOP: {p} already exists")
    s114 = load_s114()
    s112 = s114.s112
    import numpy as np
    if list(s114.AIRPORTS) != AIRPORTS:
        raise SystemExit("STOP: airport order differs from session 114's")
    fmt = lambda v: s112.fmt(s112.plain(v))                  # noqa: E731  (the tables' own number format)
    H114, S114 = read_csv(T114 / "dailymax_ifs.csv"), read_csv(T114 / "dailymax_ifs_skill.csv")
    inputs = {f"session114_comparisons/{n}": sha256_file(T114 / n) for n in ("dailymax_ifs.csv", "dailymax_ifs_skill.csv")}

    # 1. rebuild every airport's D98.10 day records with session 114's own functions
    data = {}
    for ic in AIRPORTS:
        ours = s114.Ours(ic)
        comp = s114.Comp("ifs", ic)
        recs = s114.daily_records("ifs", ours, comp, "scored")
        data[ic] = (ours, comp, recs, s114.day_arrays(recs))
    print(f"  rebuilt the D98.10 day records at 12 airports ({time.time() - t0:.0f} s)")

    # 2. gate: reproduce session 114's mx2t3 rows exactly, before anything new is scored
    checks, bad = 0, []
    for ic in AIRPORTS:
        X = data[ic][3]
        E, P = X["E"], X["P"]
        for ty in YEARS + ("all",):
            rows = [r for r in H114 if r["icao"] == ic and r["test_year"] == ty]
            if not rows:
                continue
            U = P & ((X["ty"] == ty) if ty != "all" else True)
            m2 = U & np.isfinite(E["comp2"])
            mt = s112.metrics(E["comp2"][m2])
            r2 = next(r for r in rows if r["forecast"] == "comp2")
            ms = U & np.isfinite(E["curve"]) & np.isfinite(E["comp2"])
            sk = s114.skill_of(E["curve"][ms], E["comp2"][ms]) if ms.any() else None
            rs = next(r for r in S114 if r["icao"] == ic and r["test_year"] == ty and r["a"] == "curve" and
                      r["b"] == "comp2")
            m1 = U & np.isfinite(E["comp"])
            mt1 = s112.metrics(E["comp"][m1])
            r1 = next(r for r in rows if r["forecast"] == "comp")
            for what, got, want in (("mx2t3 days", fmt(mt["n"]), r2["n"]), ("mx2t3 MAE", fmt(mt["mae"]), r2["mae"]),
                                    ("mx2t3 mean error", fmt(mt["me"]), r2["mean_error"]),
                                    ("curve vs mx2t3 days", fmt(int(ms.sum())), rs["n"]),
                                    ("curve vs mx2t3 skill", fmt(sk), rs["skill_a_vs_b"]),
                                    ("IFS steps days", fmt(mt1["n"]), r1["n"]),
                                    ("IFS steps MAE", fmt(mt1["mae"]), r1["mae"])):
                checks += 1
                if got != want:
                    bad.append(f"{ic} {ty} {what}: rebuilt {got}, table {want}")
    print(f"  gate: {checks - len(bad)} of {checks} values equal session 114's dailymax_ifs.csv and "
          f"dailymax_ifs_skill.csv exactly (mx2t3 days, MAE, mean error; curve vs mx2t3 days and skill; IFS steps "
          f"days and MAE; per airport and test year)")
    for b in bad[:20]:
        print("    MISMATCH " + b)
    if bad:
        print("--subset: FAIL (gate); nothing scored or written")
        return 2

    # 3. window coverage on the mx2t3 days (session 114's subdaily_max takes the windows present)
    partial, ndays = {}, {}
    for ic in AIRPORTS:
        ours, comp, recs, X = data[ic]
        n_p = n_d = 0
        for x, ok in zip(recs, X["P"] & np.isfinite(X["E"]["comp2"])):
            if not ok:
                continue
            hh = s114.day_hours(ours, x["date"])
            c_h = s114.h_of(x["cycle"])
            s, e = hh[0], hh[-1] + 1
            inside = [w for w in comp.mx2[c_h] if w[0] >= s and w[1] <= e]
            want = [k for k in range(1, 17) if c_h + 3 * k - 3 >= s and c_h + 3 * k <= e]
            n_d += 1
            n_p += len(inside) != len(want)
        partial[ic], ndays[ic] = n_p, n_d
    print("  mx2t3 days whose local day lacks one of the run's 3-hour windows that fit inside it: " +
          ", ".join(f"{ic} {partial[ic]} of {ndays[ic]}" for ic in AIRPORTS))

    # 4. score on the common days (descriptive)
    rng = np.random.default_rng(SEED)
    fc = ["comp2", "comp", "curve", "curve_at", "raw_gfs"]
    SUB, SSK = [], []
    for ic in AIRPORTS:
        X = data[ic][3]
        E, P = X["E"], X["P"]
        C = P.copy()
        for f in fc:
            C &= np.isfinite(E[f])
        n2 = int((P & np.isfinite(E["comp2"])).sum())
        if int(C.sum()) != n2:
            print(f"  note {ic}: {n2 - int(C.sum())} mx2t3 days lack another forecast and are left out")
        grp = "dev" if ic in DEV else "claim"
        for ty in YEARS + ("all",):
            U = C & ((X["ty"] == ty) if ty != "all" else True)
            if not U.any():
                continue
            cells = [((f,), U, E[f]) for f in fc]
            prs = [((a, b), U, E[a], E[b]) for a, b in SUB_PAIRS]
            res, nd, _ = s114.boot_block(rng, X["day"], U, s114.REPS_HEAD, cells, prs)
            for f in fc:
                mt = s112.metrics(E[f][U])
                lo_a, hi_a, lo_e, hi_e = res[("f", f)]
                SUB.append([ic, grp, ty, f, SUB_LABEL[f], mt["n"], mt["mae"], lo_a, hi_a, mt["me"], lo_e, hi_e])
            for a, b in SUB_PAIRS:
                lo, hi = res[("s", a, b)]
                SSK.append([ic, grp, ty, a, b, int(U.sum()), s114.skill_of(E[a][U], E[b][U]), lo, hi])
        r = {x[3]: x for x in SUB if x[0] == ic and x[2] == "all"}
        print(f"  {lab_ic(ic):18s} days {r['comp2'][5]:4d}  MAE mx2t3 {r['comp2'][6]:.3f}  IFS steps {r['comp'][6]:.3f}  "
              f"curve {r['curve'][6]:.3f}  curve at steps {r['curve_at'][6]:.3f}  raw GFS {r['raw_gfs'][6]:.3f}")
    t1 = csv_text(SUB_COLS, [[fmt(v) if not isinstance(v, str) else v for v in r] for r in SUB])
    t2 = csv_text(SUB_SKILL_COLS, [[fmt(v) if not isinstance(v, str) else v for v in r] for r in SSK])
    write_once(outs[0], t1)
    write_once(outs[1], t2)
    import lightgbm
    import matplotlib
    meta = ["Session 117 --subset (scripts/session117_ifs_guide.py): the mx2t3 subset of D111.4 on common days.",
            "Computed by this script, not by session 114's script (owner's ruling, session 117 Step 4). Descriptive",
            "only: no formal test. 7-day block bootstrap (F125.3), seed 117, 10,000 resamples, airports claim first.",
            "Days: D98.10's days paired for IFS (session 114's day records) that also have an mx2t3 value and every",
            "other forecast scored here. Truth: our hourly-report maximum (D82.8).",
            "",
            f"written at  : {now_utc()}",
            f"packages    : python {sys.version.split()[0]}; numpy {np.__version__}; lightgbm {lightgbm.__version__}; "
            f"matplotlib {matplotlib.__version__}",
            f"session 114 script SHA-256 : {S114_SCRIPT_SHA256} (checked before import)",
            f"gate        : {checks} of {checks} values equal session 114's tables exactly",
            "window coverage: " + ", ".join(f"{ic} {partial[ic]} of {ndays[ic]} days lack a window" for ic in AIRPORTS),
            "inputs (SHA-256):"] + [f"  {k}  {v}" for k, v in inputs.items()] + [
            "outputs (SHA-256, rows):",
            f"  {outs[0].name}  {sha256_bytes(t1.encode())}  {len(SUB)}",
            f"  {outs[1].name}  {sha256_bytes(t2.encode())}  {len(SSK)}"]
    write_once(outs[2], "\n".join(meta) + "\n")
    for line in meta[-3:]:
        print("  " + line.strip())
    print(f"--subset: PASS ({time.time() - t0:.0f} s)")
    return 0


# ------------------------------------------------------------------ number formats (as session 114's Part 1 and 2)

def f2(x):
    return f"{float(x):.2f}"


def sg2(x):
    return f"{float(x):+.2f}"


def p1(x):
    return f"{100 * float(x):+.1f}"


def ci(r, a, b, fmt=f2):
    if r[a] in ("", None, "nan") or r[b] in ("", None, "nan"):
        return ""
    return f"[{fmt(r[a])}, {fmt(r[b])}]"


def one(rows, **kw):
    sel = [r for r in rows if all(r[k] == v for k, v in kw.items())]
    if len(sel) != 1:
        raise SystemExit(f"STOP: lookup {kw} found {len(sel)} rows")
    return sel[0]


def names(lst):
    return ", ".join(lst) if lst else "none"


# ------------------------------------------------------------------ --render

class Tables:
    """The IFS tables, read only."""

    def __init__(self):
        self.mc = [r for r in read_csv(T117 / "match_counts.csv") if r["source"] == "ifs"]
        self.h = read_csv(T114 / "hourly_ifs.csv")
        self.hs = read_csv(T114 / "hourly_ifs_skill.csv")
        self.hb = read_csv(T114 / "hourly_ifs_breakdown.csv")
        self.hd = read_csv(T114 / "hourly_ifs_dm.csv")
        self.d = read_csv(T114 / "dailymax_ifs.csv")
        self.ds = read_csv(T114 / "dailymax_ifs_skill.csv")
        self.dd = read_csv(T114 / "dailymax_ifs_dm.csv")
        self.ev = read_csv(T114 / "dailymax_ifs_every_cycle.csv")
        self.sub = read_csv(T117 / "dailymax_ifs_mx2t3_subset.csv")
        self.subs = read_csv(T117 / "dailymax_ifs_mx2t3_subset_skill.csv")

    def files(self):
        return ([T117 / "match_counts.csv"] + [T114 / f"{o}_ifs{x}.csv" for o, xs in
                (("hourly", ("", "_skill", "_breakdown", "_dm")), ("dailymax", ("", "_skill", "_breakdown", "_dm",
                                                                                "_every_cycle"))) for x in xs] +
                [T117 / "dailymax_ifs_mx2t3_subset.csv", T117 / "dailymax_ifs_mx2t3_subset_skill.csv"])

    def dm(self, out):
        rows = self.hd if out == "hourly" else self.dd
        b = [r["icao"] for r in rows if r["bh_reject_q005"] == "True" and float(r["mean_daily_diff"]) < 0]
        w = [r["icao"] for r in rows if r["bh_reject_q005"] == "True" and float(r["mean_daily_diff"]) > 0]
        return b, w, len(rows)

    def cell(self, out, ic):
        h = self.h if out == "hourly" else self.d
        dmr = self.hd if out == "hourly" else self.dd
        c = float(one(h, icao=ic, test_year="all", forecast="comp")["mae"])
        u = float(one(h, icao=ic, test_year="all", forecast="curve")["mae"])
        return f"{f2(c)} / {f2(u)}" + (" *" if one(dmr, icao=ic)["bh_reject_q005"] == "True" else "")


HEADER_OLD = "ECMWF IFS is pending (D108.2)."
HEADER_NEW = "ECMWF IFS was added by session 117 (D111, finding F160), from the owner's pull (D108.2)."
P2_OLD = "ECMWF IFS: pending (D108.2), not pulled yet."
P2_NEW = "ECMWF IFS: Tables E10 to E16 (session 117, D111)."
H_LINE_OLD = "  (KRNO).\n- **Formal tests, daily maximum:**"
D_LINE_OLD = "  4 of 4; worse than no competitor at any airport."
E9_END = ("Truth windows: CLI is midnight to midnight local standard time from continuous readings; the forecasts are for "
          "the civil local day. Every score against CLI is descriptive.\n")


def item1_clause(T):
    hb, hw, hn = T.dm("hourly")
    db, dw, dn = T.dm("dailymax")
    worse = lambda w: f" and worse at {len(w)} ({names(w)})" if w else ""      # noqa: E731
    return (f"Against ECMWF IFS it is better at {len(hb)} of {hn} hourly{worse(hw)} and at {len(db)} of {dn} for the "
            f"daily maximum{worse(dw)} (IFS's maximum: the highest of its 3-hourly steps, D111.4).")


def formal_lines(T):
    hb, hw, hn = T.dm("hourly")
    db, dw, dn = T.dm("dailymax")
    hnames = f" ({names(hb)})" if 0 < len(hb) < hn else ""
    h = f"  (KRNO); better than ECMWF IFS at {len(hb)} of {hn}{hnames}" + (
        f" and worse at {len(hw)} ({names(hw)})" if hw else "") + ".\n- **Formal tests, daily maximum:**"
    dnames = f" ({names(db)})" if 0 < len(db) < dn else ""
    tail = "worse than no competitor at any airport." if not dw else (
        f"worse than ECMWF IFS at {len(dw)} ({names(dw)}) and than no other competitor.")
    d = f"  4 of 4, ECMWF IFS (the highest of its 3-hourly steps, D111.4) at {len(db)} of {dn}{dnames}; {tail}"
    return h, d


def part2_tables(T):
    L = []
    A = L.append
    lat = one(T.h, icao="EDDM", test_year="all", forecast="comp")["latency"]
    A("")
    A("**ECMWF IFS (session 117, D111).** Pulled by the owner by hand (D108.2, D111.3) and checked before any value was "
      "read (F160). Compared by session 114's script unchanged (D108.7, D111.5): `--match` in "
      "`data/processed/session117_ifs/`, `--hourly` and `--dailymax` in `data/processed/session114_comparisons/` "
      "(`*_ifs*.csv`), seed 114; the mx2t3 subset (Table E16) by `scripts/session117_ifs_guide.py --subset`, seed 117. "
      "Positions as raw GFS's (D108.3). Grids: 0.4 degree to 2024-01-31 and a 0.25 degree grid with Ni 1439 on "
      "2024-02-01 and 02-02, both with no elevation treatment (development airports only, labelled \"no elevation "
      "treatment\"); 0.25 degree from 2024-02-03, adjusted for height as GFS is with IFS's 2024-12-03 terrain "
      "(labelled \"terrain from a later date\" from 2024-02-03 to 2024-12-02, \"elevation-adjusted\" after). Versions "
      "48r1, 49r1 (from 2024-11-13), 50r1 (from 2026-05-13). Daily maximum (D111.4): primary the highest of IFS's "
      "3-hourly steps inside the local day (\"3-hourly steps\"); mx2t3, the highest of its 3-hour windows wholly "
      "inside the local day, is descriptive and exists only from 2024-11-12 to 2025-02-25 and from 2026-02-11 (plus "
      "six cycles on 2024-09-17 and 18). Scoring IFS here spends its test years at these 12 airports (D111.6). "
      f"Latency: {lat}.")
    A("")
    # E10
    A("**Table E10. ECMWF IFS: paired rows and days per airport and test year** "
      "(`data/processed/session117_ifs/match_counts.csv`, IFS rows; every unpaired row and day by reason, cycle hour "
      "and version).")
    A("")
    A("| airport | test year | paired hourly rows | paired D98.10 days | paired every-cycle days |")
    A("|---|---|---|---|---|")
    for ic in AIRPORTS:
        for ty in YEARS:
            def cnt(out):
                return sum(int(r["count"]) for r in T.mc if r["icao"] == ic and r["test_year"] == ty and
                           r["output"] == out and r["item"] == "paired")
            h = cnt("hourly")
            if h == 0 and cnt("daily max, D98.10 days") == 0:
                continue
            A(f"| {lab_ic(ic)} | {ty} | {h:,} | {cnt('daily max, D98.10 days'):,} | {cnt('daily max, every cycle'):,} |")
    A("")
    why = {}
    for r in T.mc:
        if r["item"] != "paired":
            k = (r["output"], r["item"].replace("unpaired: ", ""))
            why[k] = why.get(k, 0) + int(r["count"])
    A("Unpaired, all airports together: " + "; ".join(f"{k[0]}, {k[1]}: {v:,}" for k, v in sorted(why.items())) + ".")
    A("")
    # E11 hourly
    A("**Table E11. ECMWF IFS, hourly: MAE [95 %] on IFS's paired rows, per test year and pooled** "
      "(`hourly_ifs.csv`, `hourly_ifs_skill.csv`; breakdowns in `hourly_ifs_breakdown.csv`). Skill = 1 - MAE(a) / "
      "MAE(b), percent.")
    A("")
    A("| airport | test year | n | IFS | curve | raw GFS | linear MOS | skill curve vs IFS [95 %] | skill raw GFS vs IFS |")
    A("|---|---|---|---|---|---|---|---|---|")
    for ic in AIRPORTS:
        for ty in YEARS + ("all",):
            rr = {r["forecast"]: r for r in T.h if r["icao"] == ic and r["test_year"] == ty}
            if not rr:
                continue
            sk = {(r["a"], r["b"]): r for r in T.hs if r["icao"] == ic and r["test_year"] == ty}
            cell = lambda f: f"{f2(rr[f]['mae'])} {ci(rr[f], 'mae_lo', 'mae_hi')}"      # noqa: E731
            s1, s2 = sk[("curve", "comp")], sk[("raw_gfs", "comp")]
            A(f"| {lab_ic(ic)} | {ty} | {int(rr['comp']['n']):,} | {cell('comp')} | {cell('curve')} | "
              f"{f2(rr['raw_gfs']['mae'])} | {f2(rr['linear_mos']['mae'])} | {p1(s1['skill_a_vs_b'])} "
              f"{ci(s1, 'lo', 'hi', p1)} | {p1(s2['skill_a_vs_b'])} |")
    A("")
    A("**Table E11b. ECMWF IFS, hourly, by grid and elevation label and by IFS version: rows, MAE of IFS / the curve / "
      "raw GFS, IFS's mean error, and the curve's skill against IFS, percent [95 %]** (`hourly_ifs_breakdown.csv`, "
      "conditions `elevation` and `version`). The table does not split the 0.4 degree grid from the 8 cycles on the "
      "Ni 1439 grid; both are \"no elevation treatment\".")
    A("")
    A("| airport | segment | rows | IFS / curve / raw GFS | IFS mean error | skill curve vs IFS [95 %] |")
    A("|---|---|---|---|---|---|")
    segs = [("elevation", "no elevation treatment", "0.4 degree and Ni 1439 grids, no elevation treatment"),
            ("elevation", "elevation-adjusted, terrain from a later date",
             "0.25 degree, elevation-adjusted, terrain from a later date"),
            ("elevation", "elevation-adjusted", "0.25 degree, elevation-adjusted"),
            ("version", "48r1", "48r1"), ("version", "49r1", "49r1"), ("version", "50r1", "50r1")]
    for ic in AIRPORTS:
        for cond, b, lab in segs:
            rr = {r["forecast"]: r for r in T.hb if r["icao"] == ic and r["condition"] == cond and r["bin"] == b}
            if not rr:
                continue
            c = rr["comp"]
            A(f"| {lab_ic(ic)} | {lab} | {int(c['n']):,} | {f2(c['mae'])} / {f2(rr['curve']['mae'])} / "
              f"{f2(rr['raw_gfs']['mae'])} | {sg2(c['mean_error'])} | {p1(c['skill_curve_vs_competitor'])} "
              f"{ci(c, 'skill_lo', 'skill_hi', p1)} |")
    A("")
    A("**Table E11c. ECMWF IFS, hourly skill of the curve against IFS by lead band, percent [95 %]** "
      "(`hourly_ifs_breakdown.csv`).")
    A("")
    A("| airport | 3-12 | 13-24 | 25-36 | 37-48 |")
    A("|---|---|---|---|---|")
    for ic in AIRPORTS:
        cells = []
        for b in ("3-12", "13-24", "25-36", "37-48"):
            r = one(T.hb, icao=ic, condition="lead_band", bin=b, forecast="comp")
            cells.append(f"{p1(r['skill_curve_vs_competitor'])} {ci(r, 'skill_lo', 'skill_hi', p1)}")
        A(f"| {lab_ic(ic)} | " + " | ".join(cells) + " |")
    A("")
    # E12, E14 formal tests
    def dm_table(tn, out, rows):
        A(f"**Table {tn}. ECMWF IFS, formal tests, {'hourly' if out == 'hourly' else 'daily maximum'}** "
          f"(`{out}_ifs_dm.csv`). Daily mean of |e_curve| - |e_IFS| (negative: the curve's errors are smaller), "
          "Newey-West at 7 lags; Benjamini-Hochberg at 0.05 across the 12 airports." +
          (" IFS's maximum: the highest of its 3-hourly steps (D111.4)." if out != "hourly" else ""))
        A("")
        A("| family | airport | days | mean daily difference [95 %] | DM statistic | p-value | BH at 0.05 |")
        A("|---|---|---|---|---|---|---|")
        for r in rows:
            A(f"| {r['family']} | {lab_ic(r['icao'])} | {int(r['days']):,} | {float(r['mean_daily_diff']):+.3f} "
              f"{ci(r, 'lo', 'hi', lambda x: f'{float(x):+.3f}')} | {float(r['dm_stat']):+.2f} | "
              f"{float(r['p_value']):.1e} | {'rejected' if r['bh_reject_q005'] == 'True' else 'not rejected'} |")
        A("")
    dm_table("E12", "hourly", T.hd)
    # E13 daily maximum
    A("**Table E13. ECMWF IFS, daily maximum (D98.10's days): MAE [95 %] on IFS's paired days, per test year and "
      "pooled** (`dailymax_ifs.csv`, `dailymax_ifs_skill.csv`; breakdowns by cycle hour, season and version in "
      "`dailymax_ifs_breakdown.csv`). IFS's maximum: the highest of its 3-hourly steps inside the local day "
      "(\"3-hourly steps\", D111.4). Skill = 1 - MAE(a) / MAE(b), percent.")
    A("")
    A("| airport | test year | days | IFS's maximum (3-hourly steps) | curve (D98.10) | curve at IFS's steps | raw GFS | "
      "skill curve vs IFS [95 %] | skill curve at IFS's steps vs IFS [95 %] |")
    A("|---|---|---|---|---|---|---|---|---|")
    for ic in AIRPORTS:
        for ty in YEARS + ("all",):
            rr = {r["forecast"]: r for r in T.d if r["icao"] == ic and r["test_year"] == ty}
            if not rr:
                continue
            sk = {(r["a"], r["b"]): r for r in T.ds if r["icao"] == ic and r["test_year"] == ty}
            cell = lambda f: f"{f2(rr[f]['mae'])} {ci(rr[f], 'mae_lo', 'mae_hi')}"      # noqa: E731
            s1, s2 = sk[("curve", "comp")], sk[("curve_at", "comp")]
            A(f"| {lab_ic(ic)} | {ty} | {int(rr['comp']['n']):,} | {cell('comp')} | {cell('curve')} | "
              f"{f2(rr['curve_at']['mae'])} | {f2(rr['raw_gfs']['mae'])} | {p1(s1['skill_a_vs_b'])} "
              f"{ci(s1, 'lo', 'hi', p1)} | {p1(s2['skill_a_vs_b'])} {ci(s2, 'lo', 'hi', p1)} |")
    A("")
    dm_table("E14", "dailymax", T.dd)
    # E15 every cycle
    A("**Table E15. ECMWF IFS, daily maximum from every cycle, by cycle hour: IFS / curve MAE (first lead of the local "
      "day)** (`dailymax_ifs_every_cycle.csv`, with intervals and the curve sampled at IFS's steps). IFS's maximum: "
      "3-hourly steps (D111.4).")
    A("")
    A("| airport | 00z | 06z | 12z | 18z |")
    A("|---|---|---|---|---|")
    for ic in AIRPORTS:
        cells = []
        for ch in ("00z", "06z", "12z", "18z"):
            rr = {r["forecast"]: r for r in T.ev if r["icao"] == ic and r["cycle_hour"] == ch}
            if not rr:
                cells.append("-")
                continue
            l0, l1 = rr["comp"]["first_lead_min"], rr["comp"]["first_lead_max"]
            cells.append(f"{f2(rr['comp']['mae'])} / {f2(rr['curve']['mae'])} (lead {l0 if l0 == l1 else l0 + '-' + l1})")
        A(f"| {lab_ic(ic)} | " + " | ".join(cells) + " |")
    A("")
    # E16 mx2t3 subset
    A("**Table E16. ECMWF IFS's mx2t3 maximum on its own days (descriptive, D111.4): MAE on exactly the same days** "
      "(`data/processed/session117_ifs/dailymax_ifs_mx2t3_subset.csv` and `_skill.csv`, computed by "
      "`scripts/session117_ifs_guide.py --subset`, not by session 114's script; seed 117; no formal test). Days: "
      "D98.10's days paired for IFS that have an mx2t3 value (none in 2023-24). mx2t3: the highest of its 3-hour "
      "windows wholly inside the local day. Skill = 1 - MAE(a) / MAE(b), percent.")
    A("")
    A("| airport | test year | days | mx2t3 | IFS (3-hourly steps) | curve (D98.10) | curve at IFS's steps | raw GFS | "
      "skill curve vs mx2t3 [95 %] | skill IFS steps vs mx2t3 [95 %] |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for ic in AIRPORTS:
        for ty in YEARS + ("all",):
            rr = {r["forecast"]: r for r in T.sub if r["icao"] == ic and r["test_year"] == ty}
            if not rr:
                continue
            sk = {(r["a"], r["b"]): r for r in T.subs if r["icao"] == ic and r["test_year"] == ty}
            cell = lambda f: f"{f2(rr[f]['mae'])} {ci(rr[f], 'mae_lo', 'mae_hi')}"      # noqa: E731
            s1, s2 = sk[("curve", "comp2")], sk[("comp", "comp2")]
            A(f"| {lab_ic(ic)} | {ty} | {int(rr['comp2']['n']):,} | {cell('comp2')} | {f2(rr['comp']['mae'])} | "
              f"{f2(rr['curve']['mae'])} | {f2(rr['curve_at']['mae'])} | {f2(rr['raw_gfs']['mae'])} | "
              f"{p1(s1['skill_a_vs_b'])} {ci(s1, 'lo', 'hi', p1)} | {p1(s2['skill_a_vs_b'])} {ci(s2, 'lo', 'hi', p1)} |")
    A("")
    A("The mx2t3 days and their mx2t3 and curve figures equal session 114's tables exactly (`--subset`'s gate, "
      "`subset_meta.txt`); IFS's steps, the curve at IFS's steps and raw GFS are rescored on the same days here.")
    return "\n".join(L) + "\n"


def render_text(base, T):
    """The committed ANALYSIS.md with IFS's edits applied."""
    def rep(text, old, new, count=1):
        if text.count(old) != count:
            raise SystemExit(f"STOP: {old[:60]!r} occurs {text.count(old)} times, expected {count}")
        return text.replace(old, new)

    i1 = base.index("### 1. The short version")
    head, rest = base[:i1], base[i1:]
    head = rep(head, HEADER_OLD, HEADER_NEW)
    rest = rep(rest, " " + HEADER_OLD, " " + item1_clause(T))
    for out in ("hourly", "dailymax"):
        lab = "Table 2a. Hourly." if out == "hourly" else "Table 2b. Daily maximum"
        j = rest.index(f"**{lab}")
        k = rest.index("\n\n", rest.index("|---|", j))
        block = rest[j:k]
        new = []
        for line in block.split("\n"):
            if line.endswith(" | pending (D108.2) |"):
                ic = line[2:].split(" ", 1)[0]
                line = line[:-len("pending (D108.2) |")] + T.cell(out, ic) + " |"
            new.append(line)
        if "pending" in "\n".join(new):
            raise SystemExit("STOP: a pending cell was left")
        rest = rest[:j] + "\n".join(new) + rest[k:]
    h_new, d_new = formal_lines(T)
    rest = rep(rest, H_LINE_OLD, h_new)
    rest = rep(rest, D_LINE_OLD + "\n", d_new + "\n")
    rest = rep(rest, P2_OLD, P2_NEW)
    rest = rep(rest, E9_END, E9_END + part2_tables(T))
    return head + rest


def git_head_analysis():
    return subprocess.run(["git", "show", "HEAD:ANALYSIS.md"], cwd=ROOT, check=True, capture_output=True).stdout.decode()


def run_render(args):
    print(f"SESSION 117 --render (ANALYSIS.md from the IFS tables), start {now_utc()}")
    base = git_head_analysis()
    cur = ANALYSIS.read_text(encoding="utf-8")
    if cur != base:
        raise SystemExit("STOP: ANALYSIS.md differs from the committed text; --render runs once, on HEAD's text")
    T = Tables()
    new = render_text(base, T)
    ANALYSIS.write_text(new, encoding="utf-8")
    for p in T.files():
        print(f"  read {p.relative_to(ROOT)}  {sha256_file(p)}")
    print(f"  ANALYSIS.md: {len(base.splitlines())} lines before, {len(new.splitlines())} after; SHA-256 {sha256_bytes(new.encode())}")
    print("--render: done; run --verify")
    return 0


# ------------------------------------------------------------------ --verify

NUM = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?")


def run_verify(args):
    print(f"SESSION 117 --verify (ANALYSIS.md's IFS edits against the tables and HEAD), start {now_utc()}")
    base = git_head_analysis()
    have = ANALYSIS.read_text(encoding="utf-8")
    T = Tables()
    want = render_text(base, T)
    a, b = NUM.findall(have), NUM.findall(want)
    mism = sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
    ident = have == want
    print(f"  (1) re-rendered from HEAD's ANALYSIS.md and the tables: text identical {ident}; number tokens in the "
          f"file {len(a)}, re-rendered {len(b)}, mismatches {mism}")

    # (2) independent cell checks
    bad, n = [], 0
    for out, lab in (("hourly", "**Table 2a. Hourly.**"), ("dailymax", "**Table 2b. Daily maximum")):
        j = have.index(lab)
        for line in have[j:have.index("\n\n", have.index("|---|", j))].split("\n"):
            if not line.startswith("| ") or line.startswith("| airport "):
                continue
            cells = [c.strip() for c in line.strip("|").split("|")]
            ic = cells[0].split(" ")[0]
            h = T.h if out == "hourly" else T.d
            dmr = T.hd if out == "hourly" else T.dd
            m = re.fullmatch(r"(\d+\.\d\d) / (\d+\.\d\d)( \*)?", cells[-1])
            n += 1
            if not m:
                bad.append(f"{lab} {ic}: cell {cells[-1]!r}")
                continue
            exp = (f2(one(h, icao=ic, test_year="all", forecast="comp")["mae"]),
                   f2(one(h, icao=ic, test_year="all", forecast="curve")["mae"]),
                   one(dmr, icao=ic)["bh_reject_q005"] == "True")
            if (m.group(1), m.group(2), bool(m.group(3))) != exp:
                bad.append(f"{lab} {ic}: {cells[-1]} against {exp}")
    for tn, h in (("E11", T.h), ("E13", T.d)):
        j = have.index(f"**Table {tn}.")
        rows = have[j:have.index("\n\n", have.index("|---|", j))].split("\n")[2:]
        for ic in AIRPORTS:
            r = [x for x in rows if x.startswith(f"| {lab_ic(ic)} | all |")]
            n += 1
            if len(r) != 1:
                bad.append(f"{tn} {ic}: {len(r)} pooled rows")
                continue
            cells = [c.strip() for c in r[0].strip("|").split("|")]
            exp_n = f"{int(one(h, icao=ic, test_year='all', forecast='comp')['n']):,}"
            exp_c = f2(one(h, icao=ic, test_year="all", forecast="comp")["mae"])
            exp_u = f2(one(h, icao=ic, test_year="all", forecast="curve")["mae"])
            if cells[2] != exp_n or cells[3].split(" ")[0] != exp_c or cells[4].split(" ")[0] != exp_u:
                bad.append(f"{tn} {ic}: {cells[2:5]} against {exp_n}, {exp_c}, {exp_u}")
    print(f"  (2) independent checks: Tables 2a and 2b IFS cells and Tables E11 and E13 pooled rows: {n - len(bad)} of "
          f"{n} equal their tables")
    for x in bad[:10]:
        print("      MISMATCH " + x)

    # (3) the diff against HEAD, by kind; (4) em-dashes in the edited text
    bl, hl = base.split("\n"), have.split("\n")
    kinds, other, edited = {}, [], []
    sm = difflib.SequenceMatcher(a=bl, b=hl, autojunk=False)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        edited += hl[j1:j2]
        olds = bl[i1:i2]
        e9 = E9_END.rstrip("\n")
        if tag == "insert" and i1 > 1 and (bl[i1 - 1] == e9 or (bl[i1 - 1] == "" and bl[i1 - 2] == e9)):
            k = "new tables E10 onward (inserted after Table E9)"
        elif tag == "replace" and len(olds) == len(hl[j1:j2]):
            ks = set()
            for o in olds:
                if o.endswith(HEADER_OLD) and not o.startswith("  "):
                    ks.add("header sentence (line 5)")
                elif o.endswith(" " + HEADER_OLD):
                    ks.add("item 1 sentence")
                elif o.endswith(" | pending (D108.2) |"):
                    ks.add("Tables 2a and 2b pending cells")
                elif o == "  (KRNO)." or o == D_LINE_OLD:
                    ks.add("item 4 formal-test lines")
                elif P2_OLD in o:
                    ks.add("Part 2 intro phrase (line 812)")
                else:
                    ks.add("other")
            k = ks.pop() if len(ks) == 1 else "other"
        else:
            k = "other"
        n_lines = max(i2 - i1, j2 - j1)
        if k == "other":
            other.append((tag, i1 + 1, i2, j1 + 1, j2))
        kinds[k] = kinds.get(k, 0) + n_lines
    print("  (3) diff against HEAD, changed or inserted lines by kind: " + "; ".join(f"{k}: {v}" for k, v in sorted(kinds.items())))
    exp_kinds = {"header sentence (line 5)": 1, "item 1 sentence": 1, "Tables 2a and 2b pending cells": 24,
                 "item 4 formal-test lines": 2, "Part 2 intro phrase (line 812)": 1}
    diff_ok = not other and all(kinds.get(k) == v for k, v in exp_kinds.items()) and \
        "new tables E10 onward (inserted after Table E9)" in kinds
    if other:
        print(f"      other changes: {other[:10]}")
    em = sum(x.count(chr(0x2014)) for x in edited)
    print(f"  (4) em-dashes in the {len(edited)} edited or inserted lines: {em}; in the whole file {have.count(chr(0x2014))} "
          f"(HEAD {base.count(chr(0x2014))})")
    ok = ident and mism == 0 and not bad and diff_ok and em == 0
    print(f"--verify: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


MODES = ("subset", "render", "verify")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in MODES:
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    mode = next(m for m in MODES if getattr(a, m))
    return globals()[f"run_{mode}"](a)


if __name__ == "__main__":
    sys.exit(main())
