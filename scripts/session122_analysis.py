#!/usr/bin/env python3
"""Session 122: session 114's field guide brought up to date with IFS, its two small checks, and the IFS
figures (DECISIONS D116.6 to D116.9; register rows C08, A01, A02, A03, A04).

scripts/session114_comparisons.py is not edited, because session 117 records its SHA-256 (D116.10). This
script imports it, and session 117's IFS text helpers, read only. Offline; nothing scored.

Modes (one per run):
  --verify             ANALYSIS.md's Part 1 and its Part 2 comparisons section against the render below: text
                       identical and every number equal; 0 em-dashes. Also checks the written part1_s122.md
                       and part2_comparisons_s122.md, when present, against the render. Supersedes session
                       114's --verify (D116.6), which stays as written.
  --render             Writes part1_s122.md and part2_comparisons_s122.md, write-once, into
                       data/processed/session114_comparisons/ (or --trial-dir).
  --dailymax-ifs       A03: session 114's --dailymax --source ifs, with subdaily_max checking what its
                       docstring says (every 3-hour window of the run inside the local day present), counting
                       days that fail. Needs --trial-dir; outputs compared with the committed ones.
  --match-ifs          A04: session 114's --match with IFS's cycle counts (F160.3) added to its F156.4 check.
                       Needs --trial-dir; match_counts.csv compared with session 117's committed one.
  --figures            The comparison figures with IFS, into new files ending _s122.svg (D116.7), in
                       figures/analysis/ (or --trial-dir). With --trial-dir it also draws the five figures
                       of session 114 without IFS, to show they are unchanged.

The render: session 114's Part 1 template and Part 2 renderer, then session 117's IFS edits (its render_text
steps, from its committed tables), then session 122's text (D116.8) and figure names (D116.7).

No em-dashes in any text here (D76.6).
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")   # lightgbm loads without the shim (D93.3)

import argparse  # noqa: E402
import hashlib  # noqa: E402
import math  # noqa: E402
import re  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))

import session114_comparisons as s114  # noqa: E402  (checks sessions 112's and 113's SHA-256 itself)
import session117_ifs_guide as s117  # noqa: E402

s112 = s114.s112
ANALYSIS = ROOT / "ANALYSIS.md"
OUT_DIR = s114.OUT_DIR                                   # data/processed/session114_comparisons/
T117 = s117.T117                                         # data/processed/session117_ifs/
PART1_NAME, PART2_NAME = "part1_s122.md", "part2_comparisons_s122.md"
P2_START = "### D107.9 and D108: comparisons (session 114)"
P2_END = "\n---\n\n## Part 3."

# F160.3: IFS cycles with 2 m temperature per test year; the loader must agree (session 114's F156_4 has no
# IFS entry, so its --match skips the check; A04). Development: 1,461 in 2023-24 (less the 3 unlisted cycles),
# then 1,460 and 1,460; claim airports from 2024-25.
IFS_CYCLES = {ic: ({"2023-24": 1461, "2024-25": 1460, "2025-26": 1460} if s114.GROUP[ic] == "dev"
                   else {"2024-25": 1460, "2025-26": 1460}) for ic in s114.AIRPORTS}

# The comparison figures with IFS (D116.7): session 114's name with _s122 before .svg.
FIG_SOURCES_S122 = s114.FIG_SOURCES + ["ifs"]
FIGS_WITH_SOURCES = ["comparison_hourly_mae.svg", "comparison_dailymax_mae.svg", "comparison_skill.svg",
                     "comparison_lead_band.svg"]


def s122_name(name):
    return name[:-len(".svg")] + "_s122.svg"


def rep(text, old, new, count=1):
    if text.count(old) != count:
        raise SystemExit(f"STOP: {old[:70]!r} occurs {text.count(old)} times, expected {count}")
    return text.replace(old, new)


# ------------------------------------------------------------------ the render

def ifs_cold():
    """Airports where IFS's hourly mean error (observed minus forecast, all test years) is positive."""
    T = s117.Tables()
    rows = [s117.one(T.h, icao=ic, test_year="all", forecast="comp") for ic in s114.AIRPORTS]
    return sum(float(r["mean_error"]) > 0 for r in rows), len(rows)


def cold_sentence():
    n, of = ifs_cold()
    return (f"IFS reads cold at {n} of {of} airports (F160.4), and the reading check found no fault, so the cold "
            f"error is the model's own, not the reading's (F162.8).")


def nbm_sentence():
    hb, hw, hn = s114.dm_counts("hourly", "nbm")
    db, _, dn = s114.dm_counts("dailymax", "nbm")
    return (f"Against the NBM grid it is better at {len(hb)} of {hn} hourly and worse at {len(hw)}, and better at "
            f"{len(db)} of {dn} for the daily maximum (item 4; F157.3, F157.4).")


FIGURE_NAMES_S122 = True      # ANALYSIS.md names the new files (D116.7)


def figure_names(text):
    if not FIGURE_NAMES_S122:
        return text
    for name in FIGS_WITH_SOURCES:
        text = text.replace(f"`{name}`", f"`{s122_name(name)}`")
    return text


def render_part1():
    T = s117.Tables()
    text = s114.render_part1()
    # session 117's edits (render_text), on Part 1
    text = rep(text, " " + s117.HEADER_OLD, " " + s117.item1_clause(T))
    for out in ("hourly", "dailymax"):
        lab = "Table 2a. Hourly." if out == "hourly" else "Table 2b. Daily maximum"
        j = text.index(f"**{lab}")
        k = text.index("\n\n", text.index("|---|", j))
        lines = []
        for line in text[j:k].split("\n"):
            if line.endswith(" | pending (D108.2) |"):
                ic = line[2:].split(" ", 1)[0]
                line = line[:-len("pending (D108.2) |")] + T.cell(out, ic) + " |"
            lines.append(line)
        if "pending" in "\n".join(lines):
            raise SystemExit("STOP: a pending cell was left")
        text = text[:j] + "\n".join(lines) + text[k:]
    h_new, d_new = s117.formal_lines(T)
    text = rep(text, s117.H_LINE_OLD, h_new)
    text = rep(text, s117.D_LINE_OLD + "\n", d_new + "\n")
    # session 122's text (D116.8): AN03 in item 1, AN05 in item 4
    text = rep(text, "  station forecast, at 5 of 5. For the daily maximum",
               "  station forecast, at 5 of 5. " + nbm_sentence() + " For the daily maximum")
    text = rep(text, d_new + "\n", d_new + "\n- **ECMWF IFS reads cold:** " + cold_sentence()
               .replace("IFS reads cold at", "its hourly mean error is positive at", 1) + "\n")
    return figure_names(text)


def render_part2():
    T = s117.Tables()
    text = s114.render_part2()
    text = rep(text, s117.P2_OLD, s117.P2_NEW)
    text = rep(text, s117.E9_END, s117.E9_END + s117.part2_tables(T))
    text = rep(text, "Not adjusted for (D108.4(f)).\n", "Not adjusted for (D108.4(f)). " + cold_sentence() + "\n")
    return figure_names(text)


def part1_of(text):
    return s114.part1_of(text)


def part2_of(text):
    i = text.index(P2_START)
    return text[i:text.index(P2_END, i)].rstrip("\n") + "\n"


# ------------------------------------------------------------------ --verify and --render

def compare(label, have, want):
    a, b = s114.NUM.findall(have), s114.NUM.findall(want)
    mism = sum(x != y for x, y in zip(a, b)) + abs(len(a) - len(b))
    ident = have == want
    print(f"  {label}: numbers {len(a)}; re-rendered {len(b)}; mismatches {mism}; text identical {ident}")
    if not ident:
        hl, wl = have.split("\n"), want.split("\n")
        k = next((i for i, (x, y) in enumerate(zip(hl, wl)) if x != y), min(len(hl), len(wl)))
        print(f"    first differing line {k + 1}:\n    have: {hl[k][:150] if k < len(hl) else ''}\n"
              f"    want: {wl[k][:150] if k < len(wl) else ''}")
    return ident and mism == 0, len(a)


def run_verify(args):
    print("SESSION 122 --verify (ANALYSIS.md Part 1 and the Part 2 comparisons section against the render)")
    text = ANALYSIS.read_text(encoding="utf-8")
    p1, p2 = render_part1(), render_part2()
    ok1, n1 = compare("Part 1", part1_of(text), p1.rstrip("\n") + "\n")
    ok2, n2 = compare("Part 2 comparisons section", part2_of(text), p2)
    ok = ok1 and ok2
    folder = Path(args.trial_dir) if args.trial_dir else OUT_DIR
    for name, want in ((PART1_NAME, p1), (PART2_NAME, p2)):
        f = folder / name
        if f.exists():
            same = f.read_text(encoding="utf-8") == want
            print(f"  {f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}: equal to the render {same}")
            ok = ok and same
        else:
            print(f"  {name}: not written yet")
    em = part1_of(text).count("—") + part2_of(text).count("—")
    print(f"  numbers compared: {n1 + n2}; em-dashes in the two parts: {em}")
    ok = ok and em == 0
    print(f"--verify: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


def run_render(args):
    folder = Path(args.trial_dir) if args.trial_dir else OUT_DIR
    for name, text in ((PART1_NAME, render_part1()), (PART2_NAME, render_part2())):
        s112.write_once_bytes(folder / name, text.encode())
        print(f"  {name}: {len(text.splitlines())} lines, SHA-256 {hashlib.sha256(text.encode()).hexdigest()}")
    return 0


# ------------------------------------------------------------------ A03: subdaily_max's window check

WINDOW_CHECK = {"checked": 0, "failed": 0}
_CYCLE_H = []
# Per day set ("scored": D98.10's days; "every": every cycle): days checked, days failing, and failing days that
# would otherwise have been paired (the primary maximum present), so that the check changes a result.
BY_SET = {w: {"checked": 0, "failed": 0, "failed_else_paired": 0} for w in ("scored", "every")}
_WHICH = []


def checked_subdaily_max(windows, hh):
    """subdaily_max as its docstring says: the highest of the 3-hour windows wholly inside the local day, and
    the day must hold every such window of the run (windows k = 1 to 16 of the cycle, as session 117 counts
    them). A day that fails is counted and left without a value."""
    if windows is None:
        return None, None, "no run at this cycle"
    c_h = _CYCLE_H[-1]
    s, e = hh[0], hh[-1] + 1
    inside = [w for w in windows if w[0] >= s and w[1] <= e]
    if not inside:
        return None, None, "no 3-hour window inside the local day"
    want = [k for k in range(1, 17) if c_h + 3 * k - 3 >= s and c_h + 3 * k <= e]
    WINDOW_CHECK["checked"] += 1
    if len(inside) != len(want):
        WINDOW_CHECK["failed"] += 1
        return None, None, "a 3-hour window inside the local day is missing from the run"
    return max(w[2] for w in inside), "mx2t3", None


def trial_folder(args):
    if not args.trial_dir:
        raise SystemExit("STOP: this mode writes tables; give --trial-dir (a temporary folder)")
    d = Path(args.trial_dir)
    if d.resolve().is_relative_to(ROOT.resolve()):
        raise SystemExit("STOP: --trial-dir must be outside the repo")
    return d


def compare_files(folder, committed, names):
    bad = 0
    for name in names:
        a, b = (folder / name).read_bytes(), (committed / name).read_bytes()
        same = a == b
        bad += not same
        print(f"  {name}: {len(a):,} bytes, byte-equal to the committed one {same}")
    return bad


def run_dailymax_ifs(args):
    folder = trial_folder(args)
    s114.OUT_DIR = folder
    orig_day = s114.comp_day

    orig_records = s114.daily_records

    def comp_day(src, ours, comp, r):
        _CYCLE_H.append(s114.h_of(r["cycle"]))
        checked, failed = WINDOW_CHECK["checked"], WINDOW_CHECK["failed"]
        out = orig_day(src, ours, comp, r)
        b = BY_SET[_WHICH[-1]]
        b["checked"] += WINDOW_CHECK["checked"] - checked
        if WINDOW_CHECK["failed"] > failed:
            b["failed"] += 1
            b["failed_else_paired"] += not math.isnan(out["comp"])
        return out

    def daily_records(src, ours, comp, which):
        _WHICH.append(which)
        return orig_records(src, ours, comp, which)

    s114.comp_day = comp_day
    s114.daily_records = daily_records
    s114.subdaily_max = checked_subdaily_max
    code = s114.run_dailymax(argparse.Namespace(source="ifs", trial_dir=str(folder)))
    print(f"A03: day records with an mx2t3 window inside the local day: {WINDOW_CHECK['checked']:,}; failing the "
          f"every-window check: {WINDOW_CHECK['failed']}")
    for w, b in BY_SET.items():
        print(f"  {'D98.10 days' if w == 'scored' else 'every-cycle days'}: checked {b['checked']:,}, failing "
              f"{b['failed']}, of them otherwise paired (the primary maximum present) {b['failed_else_paired']}")
    names = [f"dailymax_ifs{x}.csv" for x in ("", "_skill", "_breakdown", "_dm", "_every_cycle")]
    bad = compare_files(folder, OUT_DIR, names)
    # F160.6 counts D98.10's days. An every-cycle day that fails is reported; it fails the check only if it
    # would otherwise have been paired, so that the check changes a result.
    ok = (code == 0 and BY_SET["scored"]["failed"] == 0 and BY_SET["every"]["failed_else_paired"] == 0
          and bad == 0)
    print(f"--dailymax-ifs: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


def run_match_ifs(args):
    folder = trial_folder(args)
    s114.OUT_DIR = folder
    if "ifs" in s114.F156_4:
        raise SystemExit("STOP: session 114's F156_4 already has an IFS entry")
    s114.F156_4["ifs"] = IFS_CYCLES
    code = s114.run_match(argparse.Namespace(trial_dir=str(folder)))
    print(f"A04: IFS cycle counts checked against F160.3 at {len(IFS_CYCLES)} airports (session 114 prints a STOP "
          f"line for any difference); --match exit {code}")
    bad = compare_files(folder, T117, ["match_counts.csv"])
    ok = code == 0 and bad == 0
    print(f"--match-ifs: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 2


# ------------------------------------------------------------------ the figures with IFS (D116.7)

def mae_panels(plt, np, out, title, fname, fcs, labels):
    """Session 114's mae_panels with an ECMWF IFS panel under AIFS's."""
    fig, axd = plt.subplot_mosaic([["aifs", "aifs", "aifs"], ["ifs", "ifs", "ifs"], ["nbm", "nbs", "mav"]],
                                  figsize=(10, 10.6), constrained_layout=True,
                                  gridspec_kw={"width_ratios": [5, 5, 4]})
    for src in FIG_SOURCES_S122:
        ax = axd[src]
        rows = {(r["icao"], r["forecast"]): r for r in s114.read_table(f"{out}_{src}.csv") if r["test_year"] == "all"}
        aps = s114.SOURCES[src]["airports"]
        x = np.arange(len(aps))
        wdt = 0.8 / len(fcs)
        for k, f in enumerate(fcs):
            v = np.array([float(rows[(ic, f)]["mae"]) for ic in aps])
            lo = np.array([float(rows[(ic, f)]["mae_lo"]) for ic in aps])
            hi = np.array([float(rows[(ic, f)]["mae_hi"]) for ic in aps])
            ax.bar(x + (k - (len(fcs) - 1) / 2) * wdt, v, wdt * 0.9, color=s114.FIG_COLOR[f], label=labels[f],
                   yerr=[v - lo, hi - v], error_kw={"elinewidth": 0.8, "ecolor": s112.INK2, "capsize": 0})
        ax.set_xticks(x)
        ax.set_xticklabels([ic + ("" if s114.GROUP[ic] == "claim" else "\n(dev)") for ic in aps], fontsize=7)
        ax.set_title(f"against {s114.SOURCES[src]['name']}", loc="left")
        ax.set_ylabel("MAE, degrees C")
        ax.grid(axis="x", visible=False)
    h, l_ = axd["aifs"].get_legend_handles_labels()
    fig.legend(h, l_, loc="outside lower center", ncol=len(fcs), fontsize=7.5)
    s114.suptitle(fig, title + ". Each panel on that source's own paired rows or days, so the curve's bars differ "
                  "between panels; lines show 95 % intervals (7-day blocks). (dev) = " + s114.DEV_FLAG)
    s114.save(fig, fname)


def skill_figure(plt):
    """Session 114's skill figure with ECMWF IFS's 12 airports added."""
    fig, axes = plt.subplots(1, 2, figsize=(10, 10.0), constrained_layout=True, sharey=True)
    for ax, out, ttl in zip(axes, ("hourly", "dailymax"), ("Hourly", "Daily maximum (curve's D98.10 maximum)")):
        ylab, y = [], 0
        for src in FIG_SOURCES_S122:
            rows = {r["icao"]: r for r in s114.read_table(f"{out}_{src}_skill.csv")
                    if r["test_year"] == "all" and r["a"] == "curve" and r["b"] == "comp"}
            for ic in s114.SOURCES[src]["airports"]:
                r = rows[ic]
                v, lo, hi = (100 * float(r[k]) for k in ("skill_a_vs_b", "lo", "hi"))
                ax.plot([lo, hi], [y, y], color=s114.FIG_COLOR["curve"], lw=1.6)
                ax.plot([v], [y], "o", color=s114.FIG_COLOR["curve"], ms=4)
                ylab.append(f"{s114.SOURCES[src]['name']}  {ic}" + ("" if s114.GROUP[ic] == "claim" else " (dev)"))
                y += 1
            y += 0.6
        ax.axvline(0, color=s112.INK, lw=0.8)
        ax.set_title(ttl, loc="left")
        ax.set_xlabel("skill of the curve against the competitor, % (positive: the curve's MAE is smaller)")
        ax.grid(axis="y", visible=False)
    ys, y = [], 0
    for src in FIG_SOURCES_S122:
        for ic in s114.SOURCES[src]["airports"]:
            ys.append(y)
            y += 1
        y += 0.6
    axes[0].set_yticks(ys)
    axes[0].set_yticklabels(ylab, fontsize=6.5)
    axes[0].invert_yaxis()
    fig.suptitle("The curve against each competitor: pooled skill with 95 % intervals. Descriptive (D107.2); "
                 "formal tests in the _dm tables.\n(dev) = " + s114.DEV_FLAG, fontsize=8.5, x=0.01, ha="left")
    s114.save(fig, s122_name("comparison_skill.svg"))


def lead_band_figure(plt):
    """Session 114's lead-band figure with a third panel against ECMWF IFS."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), constrained_layout=True, sharey=True)
    bands = [f"{lo}-{hi}" for lo, hi in s112.BANDS]
    for ax, src in zip(axes, ("aifs", "nbm", "ifs")):
        rows = [r for r in s114.read_table(f"hourly_{src}_breakdown.csv") if r["condition"] == "lead_band" and
                r["forecast"] == "comp"]
        ends = []
        for ic in s114.SOURCES[src]["airports"]:
            v = [100 * float(next(r for r in rows if r["icao"] == ic and r["bin"] == b)["skill_curve_vs_competitor"])
                 for b in bands]
            ls = "-" if s114.GROUP[ic] == "claim" else "--"
            ax.plot(range(4), v, ls, color=s112.INK2 if s114.GROUP[ic] == "dev" else s114.FIG_COLOR["curve"], lw=1.2)
            ends.append([v[-1], ic])
        ends.sort()
        for k in range(1, len(ends)):                      # keep end labels at least 2.4 points apart
            ends[k][0] = max(ends[k][0], ends[k - 1][0] + 2.4)
        for y_, ic in ends:
            ax.annotate(ic + ("" if s114.GROUP[ic] == "claim" else " (dev)"), (3.05, y_), fontsize=6.5,
                        va="center", color=s112.INK)
        ax.axhline(0, color=s112.INK, lw=0.8)
        ax.set_xticks(range(4))
        ax.set_xticklabels(bands)
        ax.set_xlim(-0.2, 3.75)
        ax.set_xlabel("lead band, hours")
        ax.set_title(f"against {s114.SOURCES[src]['name']}", loc="left")
    axes[0].set_ylabel("skill of the curve, %")
    fig.suptitle("Hourly skill of the curve by lead band (positive: the curve is better). Blue solid: claim airports; "
                 "grey dashed: development airports (dev). Descriptive.", fontsize=8.5, x=0.01, ha="left")
    s114.save(fig, s122_name("comparison_lead_band.svg"))


class NoPreview(list):
    """Stands in for session 114's PREVIEW list: empty, and stays empty."""

    def append(self, x):
        pass


def run_figures(args):
    import numpy as np
    if args.trial_dir:
        folder = trial_folder(args)
        s114.FIG_DIR = s112.FIG_DIR = folder
        # session 114's five figures, without IFS, to show they are unchanged; its run_figures also renders
        # part1.md and part2_comparisons.md into the trial folder. Its trial runs first save a PNG preview of
        # each figure, which moves the clip boxes by rounding and so changes the SVG's clip-path ids; its repo
        # run saved none, so the preview is switched off here.
        s114.PREVIEW = NoPreview()
        s114.run_figures(argparse.Namespace(trial_dir=str(folder)))
        old = sorted(n for n, _, _ in s114._FIGS)
        print(f"  session 114's five figures: {len(old)}")
        bad = compare_files(folder, ROOT / "figures" / "analysis", old)
        if bad:
            print("STOP: a session 114 figure differs from the committed one")
            return 2
        s114._FIGS.clear()
    plt = s112.plt_setup()
    s112.FIG_DIR.mkdir(parents=True, exist_ok=True)
    mae_panels(plt, np, "hourly", "Hourly MAE: each competitor, the curve and raw GFS, all test years pooled",
               s122_name("comparison_hourly_mae.svg"), ["comp", "curve", "raw_gfs"],
               {"comp": "the competitor", "curve": "curve", "raw_gfs": "raw GFS"})
    mae_panels(plt, np, "dailymax", "Daily maximum MAE (D98.10's days; truth: our hourly-report maximum)",
               s122_name("comparison_dailymax_mae.svg"), ["comp", "curve", "curve_at", "raw_gfs"],
               {"comp": "the competitor's maximum (AIFS: its 6-hourly steps; ECMWF IFS: its 3-hourly steps; NBM: "
                        "TMAX; NBS: TXN; MAV: X)",
                "curve": "curve (D98.10)", "curve_at": "curve sampled at the competitor's steps",
                "raw_gfs": "raw GFS"})
    skill_figure(plt)
    lead_band_figure(plt)
    for name, n, h_ in s114._FIGS:
        print(f"  {name}: {n:,} bytes, SHA-256 {h_}")
    return 0


# ------------------------------------------------------------------ main

MODES = ("verify", "render", "dailymax-ifs", "match-ifs", "figures")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in MODES:
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--trial-dir", default=None, help="a folder outside the repo for trial outputs")
    a = ap.parse_args()
    mode = next(m for m in MODES if getattr(a, m.replace("-", "_")))
    try:
        return globals()[f"run_{mode.replace('-', '_')}"](a)
    except s114.s113.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
