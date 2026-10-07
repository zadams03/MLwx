"""Session 98b: draw the README's figures as SVG files (DECISIONS D90.10, D91.3).

Offline. Python standard library only. It reads committed files only, checks
each input's SHA-256 before reading it, and writes new files only: it refuses
to overwrite a figure that exists (SPEC 8.7 item 5). It prints every value it
draws. Nothing is computed from the data except figure geometry: every number
drawn is copied from a committed file and checked against the record.

Figures, written into figures/ at the repo root:
  headline_mae.svg     raw GFS MAE and the selected-features method's MAE on
                       the reserved year 2024-08-01 to 2025-07-31, five
                       airports (F109). Source: the F109 grid file.
  skill_intervals.svg  skill with its 95% interval over raw GFS and over
                       persistence, same airports and year (F125.6). Source:
                       the summary table in notes/session-83-output.txt, the
                       saved output F125 cites.

KSFO is left out of both (D71.5: not directly comparable).

Run: .venv/bin/python -B scripts/session98b_figures.py
"""

import csv
import hashlib
import io
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = ROOT / "figures"

GRID = ROOT / "data" / "processed" / "session63_reserved_confirm_grid.csv"
# Recorded in notes/session-85-output.txt (lines 21, 167) and F139.1.
GRID_SHA256 = "0138ba039d0bd077e71b829789a8d3c93175e22493ed115f7503b2baa30f4ed3"

S83_OUT = ROOT / "notes" / "session-83-output.txt"
# No SHA-256 of this file is in the record; this is the committed file's
# value at session 98b (F140).
S83_SHA256 = "d87afdac94582fb598b97518a0b8004575bb140892f386daf1c934cc1c50fb65"

AIRPORTS = [  # order fixed by the session prompt; names from SPEC 3.4
    ("EGLC", "London City"),
    ("LFPG", "Paris CDG"),
    ("DSM", "Des Moines"),
    ("YSDU", "Dubbo"),
    ("RNO", "Reno"),
]

# F109's MAEs at 4 decimals (SPEC 8.5), used only to check what is read.
F109_4DP = {
    "EGLC": ("1.2362", "1.0008"),
    "LFPG": ("1.4091", "1.2369"),
    "DSM": ("1.7043", "1.4123"),
    "YSDU": ("1.4897", "1.2643"),
    "RNO": ("1.6135", "1.2742"),
}

# F125.6's skill (%) and 95% interval, at F125.6's precision, used only to
# check what is read: (raw GFS), (persistence).
F125_6 = {
    "EGLC": (("+19.0", "+12.6", "+24.2"), ("+55.0", "+48.5", "+61.2")),
    "LFPG": (("+12.2", "+6.8", "+17.6"), ("+51.0", "+43.0", "+57.5")),
    "DSM": (("+17.1", "+7.4", "+27.0"), ("+65.6", "+60.8", "+70.3")),
    "YSDU": (("+15.1", "+7.9", "+22.3"), ("+51.7", "+44.9", "+57.9")),
    "RNO": (("+21.0", "+13.2", "+28.5"), ("+53.8", "+46.3", "+60.4")),
}

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK = "#1a1a1a"
MUTED = "#555555"
GRIDLINE = "#dddddd"
RAW_COLOUR = "#9aa0a6"
MODEL_COLOUR = "#1f6fb2"


def read_checked(path, expected):
    """Return the file's bytes after checking its SHA-256."""
    data = path.read_bytes()
    found = hashlib.sha256(data).hexdigest()
    if found != expected:
        raise SystemExit(f"STOP: {path.relative_to(ROOT)} SHA-256 {found}, expected {expected}")
    print(f"input {path.relative_to(ROOT)} SHA-256 {found} (as expected)")
    return data


def write_once(path, text):
    """Write a new file; refuse if it exists."""
    OUT_DIR.mkdir(exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"wrote {path.relative_to(ROOT)}: {len(text.encode('utf-8'))} bytes, SHA-256 {sha}")


def n(x):
    """Geometry number, fixed at 2 decimals so output is repeatable."""
    return f"{x:.2f}"


def svg_open(width, height, title, desc):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc" '
        f'font-family="{FONT}">',
        f'<title id="title">{title}</title>',
        f'<desc id="desc">{desc}</desc>',
        f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>',
    ]


def text(x, y, s, size=12, anchor="start", fill=INK, weight="normal"):
    return (f'<text x="{n(x)}" y="{n(y)}" font-size="{size}" text-anchor="{anchor}" '
            f'fill="{fill}" font-weight="{weight}">{s}</text>')


def headline():
    raw = read_checked(GRID, GRID_SHA256).decode("utf-8")
    rows = {r["station"]: r for r in csv.DictReader(io.StringIO(raw))}
    values = []
    for code, name in AIRPORTS:
        r = rows[code]
        raw_mae, model_mae = float(r["raw_mae"]), float(r["final_mae"])
        got = (f"{raw_mae:.4f}", f"{model_mae:.4f}")
        if got != F109_4DP[code]:
            raise SystemExit(f"STOP: {code} grid values {got} differ from F109 {F109_4DP[code]}")
        values.append((code, name, raw_mae, model_mae))
        print(f"  {code}: raw GFS {raw_mae!r} drawn as {got[0]}; "
              f"selected-features {model_mae!r} drawn as {got[1]}")

    width, height = 760, 460
    left, right, top, bottom = 70, 20, 92, 92
    plot_w, plot_h = width - left - right, height - top - bottom
    y_max = 2.0
    group_w = plot_w / len(values)
    bar_w = 46

    def y_of(v):
        return top + plot_h * (1 - v / y_max)

    title = "Selected-features method vs raw GFS, reserved year 2024-25 (F109)"
    desc = ("Grouped bar chart of mean absolute error in degrees C on the reserved year "
            "2024-08-01 to 2025-07-31. " + "; ".join(
                f"{c}: raw GFS {r:.4f}, selected-features {m:.4f}" for c, _, r, m in values)
            + ". Lower is better. Source DECISIONS F109.")
    out = svg_open(width, height, title, desc)
    out.append(text(left, 30, title, size=16, weight="bold"))
    out.append(text(left, 52, "Mean absolute error at each airport's target hour. Lower is better.",
                    size=12, fill=MUTED))
    # legend
    lx = left
    out.append(f'<rect x="{n(lx)}" y="64" width="14" height="14" fill="{RAW_COLOUR}"/>')
    out.append(text(lx + 20, 76, "raw GFS (elevation-adjusted GRIB, SPEC 5.2)", size=12))
    lx += 300
    out.append(f'<rect x="{n(lx)}" y="64" width="14" height="14" fill="{MODEL_COLOUR}"/>')
    out.append(text(lx + 20, 76, "selected-features method, B+D,L,R,T (SPEC 8)", size=12))
    # axis and grid
    for tick in (0.0, 0.5, 1.0, 1.5, 2.0):
        y = y_of(tick)
        out.append(f'<line x1="{n(left)}" y1="{n(y)}" x2="{n(width - right)}" y2="{n(y)}" '
                   f'stroke="{GRIDLINE}" stroke-width="1"/>')
        out.append(text(left - 8, y + 4, f"{tick:.1f}", size=11, anchor="end", fill=MUTED))
    out.append(f'<line x1="{n(left)}" y1="{n(y_of(0))}" x2="{n(width - right)}" y2="{n(y_of(0))}" '
               f'stroke="{INK}" stroke-width="1"/>')
    cy = top + plot_h / 2
    out.append(f'<text x="18" y="{n(cy)}" font-size="12" text-anchor="middle" fill="{INK}" '
               f'transform="rotate(-90 18 {n(cy)})">MAE (degrees C)</text>')
    # bars
    for i, (code, name, raw_mae, model_mae) in enumerate(values):
        gx = left + group_w * i + group_w / 2
        for j, (v, colour) in enumerate(((raw_mae, RAW_COLOUR), (model_mae, MODEL_COLOUR))):
            x = gx - bar_w - 2 if j == 0 else gx + 2
            y = y_of(v)
            out.append(f'<rect x="{n(x)}" y="{n(y)}" width="{bar_w}" height="{n(y_of(0) - y)}" '
                       f'fill="{colour}"/>')
            out.append(text(x + bar_w / 2, y - 6, f"{v:.4f}", size=11, anchor="middle"))
        out.append(text(gx, y_of(0) + 20, code, size=13, anchor="middle", weight="bold"))
        out.append(text(gx, y_of(0) + 36, name, size=11, anchor="middle", fill=MUTED))
    out.append(text(left, height - 14,
                    "One look per airport on the reserved year 2024-08-01 to 2025-07-31. "
                    "KSFO is not shown (D71.5).", size=11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out) + "\n"


ROW_RE = re.compile(
    r"^\s+F109\s+(\S+)\s+(raw GFS|persistence)\s+(\d+)\s+"
    r"(\S+) \[(\S+), (\S+)\]\s+(\S+) \[(\S+), (\S+)\]\s+(yes|no)\s*$")


def skill_intervals():
    raw = read_checked(S83_OUT, S83_SHA256).decode("utf-8")
    start = raw.index("Summary table")
    found = {}
    for line in raw[start:].splitlines():
        m = ROW_RE.match(line)
        if m:
            code, ref = m.group(1), m.group(2)
            found[(code, ref)] = (m.group(7), m.group(8), m.group(9), int(m.group(3)))
    values = []
    for code, name in AIRPORTS:
        pair = []
        for k, ref in enumerate(("raw GFS", "persistence")):
            if (code, ref) not in found:
                raise SystemExit(f"STOP: no F109 {code} {ref} row in the summary table")
            s, lo, hi, count = found[(code, ref)]
            if (s, lo, hi) != F125_6[code][k]:
                raise SystemExit(f"STOP: {code} {ref} {(s, lo, hi)} differs from F125.6 {F125_6[code][k]}")
            pair.append((float(s), float(lo), float(hi), count))
            print(f"  {code} vs {ref}: skill {s}% [{lo}, {hi}], n {count} (equal to F125.6)")
        values.append((code, name, pair))

    width, height = 760, 440
    top, bottom = 100, 70
    label_w = 110
    gap = 40
    panel_w = (width - label_w - gap - 30) / 2
    panels = [
        ("Skill over raw GFS (%)", -5.0, 35.0, (0, 10, 20, 30), label_w),
        ("Skill over persistence (%)", -10.0, 80.0, (0, 20, 40, 60, 80), label_w + panel_w + gap),
    ]
    row_h = (height - top - bottom) / len(values)

    title = "Skill with 95% intervals, reserved year 2024-25 (F125.6)"
    parts = []
    for code, _, pair in values:
        parts.append(f"{code}: over raw GFS {pair[0][0]:+.1f}% [{pair[0][1]:+.1f}, {pair[0][2]:+.1f}], "
                     f"over persistence {pair[1][0]:+.1f}% [{pair[1][1]:+.1f}, {pair[1][2]:+.1f}]")
    desc = ("Two dot plots with horizontal 95% interval bars and a line at zero. "
            + "; ".join(parts) + ". Every interval lies above zero. Source DECISIONS F125.6.")
    out = svg_open(width, height, title, desc)
    out.append(text(20, 30, title, size=16, weight="bold"))
    out.append(text(20, 52, "Skill = 1 - model MAE / reference MAE. Point: the estimate. "
                    "Bar: 95% moving-block bootstrap interval (F125.3).", size=12, fill=MUTED))
    for p_title, lo_d, hi_d, ticks, x0 in panels:
        def x_of(v, lo_d=lo_d, hi_d=hi_d, x0=x0):
            return x0 + panel_w * (v - lo_d) / (hi_d - lo_d)
        out.append(text(x0 + panel_w / 2, top - 22, p_title, size=13, anchor="middle", weight="bold"))
        for t in ticks:
            x = x_of(t)
            out.append(f'<line x1="{n(x)}" y1="{n(top - 8)}" x2="{n(x)}" y2="{n(height - bottom)}" '
                       f'stroke="{GRIDLINE}" stroke-width="1"/>')
            out.append(text(x, height - bottom + 18, f"{t}", size=11, anchor="middle", fill=MUTED))
        xz = x_of(0)
        out.append(f'<line x1="{n(xz)}" y1="{n(top - 8)}" x2="{n(xz)}" y2="{n(height - bottom)}" '
                   f'stroke="{INK}" stroke-width="1.5"/>')
    for i, (code, name, pair) in enumerate(values):
        cy = top + row_h * i + row_h / 2
        out.append(text(20, cy, code, size=13, weight="bold"))
        out.append(text(20, cy + 15, name, size=11, fill=MUTED))
        for (p_title, lo_d, hi_d, ticks, x0), (s, lo, hi, _) in zip(panels, pair):
            def x_of(v, lo_d=lo_d, hi_d=hi_d, x0=x0):
                return x0 + panel_w * (v - lo_d) / (hi_d - lo_d)
            out.append(f'<line x1="{n(x_of(lo))}" y1="{n(cy)}" x2="{n(x_of(hi))}" y2="{n(cy)}" '
                       f'stroke="{MODEL_COLOUR}" stroke-width="3"/>')
            out.append(f'<circle cx="{n(x_of(s))}" cy="{n(cy)}" r="5" fill="{MODEL_COLOUR}"/>')
            out.append(text(x_of(s), cy - 10, f"{s:+.1f} [{lo:+.1f}, {hi:+.1f}]", size=11, anchor="middle"))
    out.append(text(20, height - 30, "The intervals describe day-to-day sampling within one year only, "
                    "and the airports share that year's weather (F125.9).", size=11, fill=MUTED))
    out.append(text(20, height - 14, "KSFO is not shown (D71.5).", size=11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    print("session 98b figures (offline, standard library only)")
    print(f"python {sys.version.split()[0]}")
    targets = [OUT_DIR / "headline_mae.svg", OUT_DIR / "skill_intervals.svg"]
    for t in targets:
        if t.exists():
            raise SystemExit(f"STOP: {t.relative_to(ROOT)} exists; figures are written once")
    print("headline_mae.svg values (F109):")
    svg1 = headline()
    print("skill_intervals.svg values (F125.6):")
    svg2 = skill_intervals()
    for text_, svg in ((targets[0], svg1), (targets[1], svg2)):
        if chr(0x2014) in svg:
            raise SystemExit("STOP: em-dash in figure text")
        write_once(text_, svg)


if __name__ == "__main__":
    main()
