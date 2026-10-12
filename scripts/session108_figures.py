"""Session 108: draw stage C's two descriptive figures (DECISIONS D102.6).

Offline. Python standard library only. It reads two committed files from
session 107's look, checks each input's SHA-256 before reading it, and
writes new files only: it refuses to overwrite a figure that exists. It
prints every value it draws. Nothing is averaged across airports.

Figures, written into figures/ at the repo root:
  stagec_headline.svg       per claim airport, MAE of raw GFS and the curve in
                            look A and look B, for the hourly curve (leads 3
                            to 48) and the daily maximum (F150). Source: the
                            raw GFS half of the verdicts file.
  stagec_mae_by_lead.svg    per claim airport, MAE by forecast hour of raw GFS
                            and the curve, look A solid and look B dashed,
                            pooled over the four GFS runs a day. Source: the
                            scores file. Descriptive (D100.8).

Run: .venv/bin/python -B scripts/session108_figures.py [output folder]
With no argument it writes into figures/.
"""

import csv
import hashlib
import io
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_DIR = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / "figures"

PROC = ROOT / "data" / "processed"
SCORES = PROC / "session107_claim_scores.csv"
DAYS = PROC / "session107_claim_days.csv"
VERDICTS = PROC / "session107_claim_verdicts.csv"

# Recorded in DECISIONS F150.4 (checked against the entry by a test, D98.2).
SCORES_SHA256 = "2918fff42ab17ff2fce55260d7d0d757638b989943324ddceb3e1a7ff59488ca"
DAYS_SHA256 = "3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297"
VERDICTS_SHA256 = "0a9c1dc80a1e052c5b98a117b6c42cbd9811c160a944be959dca0e4575e319da"

AIRPORTS = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]  # order fixed by the prompt

# F150.2's margins over raw GFS (percent, 2 decimals): (look A, look B).
# Used only to check what is read.
F150_2_RAW = {
    "hourly": {
        "EDDM": ("24.83", "26.96"), "KORD": ("14.39", "8.22"),
        "CYYZ": ("22.04", "23.48"), "ZGSZ": ("21.63", "23.09"),
        "ZUCK": ("23.91", "27.07"), "NZWN": ("31.71", "32.99"),
    },
    "daily": {
        "EDDM": ("29.14", "31.44"), "KORD": ("9.32", "2.59"),
        "CYYZ": ("23.19", "21.22"), "ZGSZ": ("40.31", "39.63"),
        "ZUCK": ("14.84", "14.14"), "NZWN": ("55.74", "57.21"),
    },
}

FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"
INK = "#1a1a1a"
MUTED = "#555555"
GRIDLINE = "#dddddd"
RAW_COLOUR = "#9aa0a6"
MODEL_COLOUR = "#1f6fb2"
RAW_B_COLOUR = "#cfd3d7"
MODEL_B_COLOUR = "#86b6dd"


def read_checked(path, expected):
    """Return the file's text after checking its SHA-256."""
    data = path.read_bytes()
    found = hashlib.sha256(data).hexdigest()
    if found != expected:
        raise SystemExit(f"STOP: {path.relative_to(ROOT)} SHA-256 {found}, expected {expected}")
    print(f"input {path.relative_to(ROOT)} SHA-256 {found} (as expected)")
    return data.decode("utf-8")


def write_once(path, text):
    """Write a new file; refuse if it exists."""
    OUT_DIR.mkdir(exist_ok=True)
    with open(path, "x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    sha = hashlib.sha256(text.encode("utf-8")).hexdigest()
    print(f"wrote {path}: {len(text.encode('utf-8'))} bytes, SHA-256 {sha}")


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


def load_verdicts():
    raw = read_checked(VERDICTS, VERDICTS_SHA256)
    rows = list(csv.DictReader(io.StringIO(raw)))
    print("verdicts columns used: icao, output, look, half, n, curve_mae, other_mae, margin_pct")
    return rows


def load_scores():
    raw = read_checked(SCORES, SCORES_SHA256)
    rows = list(csv.DictReader(io.StringIO(raw)))
    print("scores columns used: icao, look, output, method, row_set, cycle_hour, lead, n, mae")
    return rows


def raw_half(verdicts):
    """{(output, icao, look): (n, curve_mae, raw_mae)} from the raw GFS half,
    checked against F150.2."""
    out = {}
    for r in verdicts:
        if r["half"] != "raw_gfs":
            continue
        key = (r["output"], r["icao"], r["look"])
        curve, raw = float(r["curve_mae"]), float(r["other_mae"])
        margin = 100 * (1 - curve / raw)
        want = F150_2_RAW[r["output"]][r["icao"]][0 if r["look"] == "A" else 1]
        if f"{margin:.2f}" != want:
            raise SystemExit(f"STOP: {key} margin {margin:.2f} differs from F150.2 {want}")
        out[key] = (int(r["n"]), curve, raw)
    if len(out) != 24:
        raise SystemExit(f"STOP: expected 24 raw GFS halves, found {len(out)}")
    return out


def headline(half):
    width, height = 760, 860
    left, right = 70, 20
    plot_w = width - left - right
    y_max = 3.0
    top1, ph = 130, 250
    top2 = top1 + ph + 110
    group_w = plot_w / len(AIRPORTS)
    bar_w = 24
    title = "Stage C claim airports: raw GFS and the curve (F150)"
    desc_parts = []
    for output in ("hourly", "daily"):
        for ic in AIRPORTS:
            a, b = half[(output, ic, "A")], half[(output, ic, "B")]
            desc_parts.append(f"{output} {ic}: look A raw GFS {a[2]:.4f}, curve {a[1]:.4f}; "
                              f"look B raw GFS {b[2]:.4f}, curve {b[1]:.4f}")
    desc = ("Grouped bar charts of mean absolute error in degrees C, two panels, hourly curve "
            "and daily maximum. " + "; ".join(desc_parts) + ". Lower is better. Source DECISIONS F150.")
    out = svg_open(width, height, title, desc)
    out.append(text(left, 30, title, size=16, weight="bold"))
    out.append(text(left, 52, "Stage C claim, six new airports, MAE in degrees C (F150). "
                    "Lower is better.", size=12, fill=MUTED))
    entries = [(RAW_COLOUR, "raw GFS, look A"), (MODEL_COLOUR, "curve, look A"),
               (RAW_B_COLOUR, "raw GFS, look B"), (MODEL_B_COLOUR, "curve, look B")]
    for i, (colour, label) in enumerate(entries):
        lx = left + i * 160
        out.append(f'<rect x="{n(lx)}" y="64" width="14" height="14" fill="{colour}"/>')
        out.append(text(lx + 20, 76, label, size=12))
    out.append(text(left, 96, "Look A: runs 2024-08-01 to 2025-07-31. Look B: runs 2025-08-01 to "
                    "2026-07-31. Each airport has its own bars; nothing is averaged.",
                    size=11, fill=MUTED))
    for p_title, output, top in (("Hourly curve, leads 3 to 48", "hourly", top1),
                                 ("Daily maximum", "daily", top2)):
        out.append(text(left, top - 14, p_title, size=14, weight="bold"))

        def y_of(v, top=top):
            return top + ph * (1 - v / y_max)

        for tick in (0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0):
            y = y_of(tick)
            out.append(f'<line x1="{n(left)}" y1="{n(y)}" x2="{n(width - right)}" y2="{n(y)}" '
                       f'stroke="{GRIDLINE}" stroke-width="1"/>')
            out.append(text(left - 8, y + 4, f"{tick:.1f}", size=11, anchor="end", fill=MUTED))
        out.append(f'<line x1="{n(left)}" y1="{n(y_of(0))}" x2="{n(width - right)}" '
                   f'y2="{n(y_of(0))}" stroke="{INK}" stroke-width="1"/>')
        cy = top + ph / 2
        out.append(f'<text x="18" y="{n(cy)}" font-size="12" text-anchor="middle" fill="{INK}" '
                   f'transform="rotate(-90 18 {n(cy)})">MAE (degrees C)</text>')
        print(f"{output}: values drawn (look A raw GFS, curve; look B raw GFS, curve)")
        for i, ic in enumerate(AIRPORTS):
            a, b = half[(output, ic, "A")], half[(output, ic, "B")]
            vals = [(a[2], RAW_COLOUR), (a[1], MODEL_COLOUR),
                    (b[2], RAW_B_COLOUR), (b[1], MODEL_B_COLOUR)]
            print(f"  {ic}: {a[2]!r} {a[1]!r} {b[2]!r} {b[1]!r}")
            if max(v for v, _ in vals) >= y_max:
                raise SystemExit("STOP: a value is off the axis")
            gx = left + group_w * i + group_w / 2
            for j, (v, colour) in enumerate(vals):
                x = gx - 2 * bar_w - 3 + j * (bar_w + 2)
                y = y_of(v)
                out.append(f'<rect x="{n(x)}" y="{n(y)}" width="{bar_w}" height="{n(y_of(0) - y)}" '
                           f'fill="{colour}"/>')
                out.append(text(x + bar_w / 2, y - 5, f"{v:.2f}", size=10, anchor="middle"))
            out.append(text(gx, y_of(0) + 20, ic, size=13, anchor="middle", weight="bold"))
    out.append(text(left, height - 14, "Hourly: all rows at leads 3 to 48. Daily: the day's maximum "
                    "read off the curve (D98.10). Data is GFS v16 (D100.10).", size=11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def pooled_by_lead(scores, half):
    """{(icao, look, method): [MAE at lead 3 .. 48]}, pooled over the four cycle
    hours as sum(n x MAE) / sum(n). Gate: pooling everything reproduces the
    verdicts file's hourly raw GFS half (n exactly, both MAEs within 1e-9)."""
    acc = {}
    for r in scores:
        if r["output"] != "hourly" or r["row_set"] != "common" or r["method"] not in ("raw_gfs", "curve"):
            continue
        key = (r["icao"], r["look"], r["method"], int(r["lead"]))
        cnt, tot = acc.get(key, (0, 0.0))
        acc[key] = (cnt + int(r["n"]), tot + int(r["n"]) * float(r["mae"]))
    leads = list(range(3, 49))
    series = {}
    for ic in AIRPORTS:
        for look in ("A", "B"):
            for method in ("raw_gfs", "curve"):
                vals = []
                for ld in leads:
                    cnt, tot = acc[(ic, look, method, ld)]
                    vals.append(tot / cnt)
                series[(ic, look, method)] = vals
            # gate
            for method, idx in (("curve", 1), ("raw_gfs", 2)):
                cnt = sum(acc[(ic, look, method, ld)][0] for ld in leads)
                tot = sum(acc[(ic, look, method, ld)][1] for ld in leads)
                vn, vcurve, vraw = half[("hourly", ic, look)]
                want = vcurve if method == "curve" else vraw
                if cnt != vn or abs(tot / cnt - want) > 1e-9:
                    raise SystemExit(f"STOP: gate failed at {ic} {look} {method}: "
                                     f"n {cnt} vs {vn}, MAE {tot / cnt!r} vs {want!r}")
    print(f"gate: pooling over all cycle hours and leads reproduces the verdicts file for "
          f"{len(AIRPORTS) * 2} airport-looks x 2 methods (n exact, MAE within 1e-9): PASS")
    return leads, series


def by_lead(leads, series):
    width, height = 760, 740
    cols, rows_n = 2, 3
    left0, top0 = 56, 120
    pw, ph = 290, 140
    gap_x, gap_y = 60, 58
    all_vals = [v for vals in series.values() for v in vals]
    y_max = 0.5 * (int(max(all_vals) / 0.5) + 1)
    y_ticks = [t * 0.5 for t in range(int(y_max / 0.5) + 1)]
    title = "Stage C: MAE by forecast hour, per claim airport"
    desc_parts = []
    for ic in AIRPORTS:
        for look in ("A", "B"):
            r, c = series[(ic, look, "raw_gfs")], series[(ic, look, "curve")]
            desc_parts.append(f"{ic} look {look}: lead 3 raw GFS {r[0]:.3f}, curve {c[0]:.3f}; "
                              f"lead 48 raw GFS {r[-1]:.3f}, curve {c[-1]:.3f}")
    desc = ("Six small line charts, one per airport, of mean absolute error in degrees C against "
            "forecast hour 3 to 48, raw GFS and the curve, look A solid and look B dashed. "
            + "; ".join(desc_parts) + ". Source DECISIONS F150, session 107 scores.")
    out = svg_open(width, height, title, desc)
    out.append(text(20, 30, title, size=16, weight="bold"))
    out.append(text(20, 52, "MAE by forecast hour, per airport, pooled over the four GFS runs a day. "
                    "Descriptive (D100.8).", size=12, fill=MUTED))
    legend = [(RAW_COLOUR, "", "raw GFS, look A"), (RAW_COLOUR, "5 4", "raw GFS, look B"),
              (MODEL_COLOUR, "", "curve, look A"), (MODEL_COLOUR, "5 4", "curve, look B")]
    for i, (colour, dash, label) in enumerate(legend):
        lx = 20 + i * 170
        d = f' stroke-dasharray="{dash}"' if dash else ""
        out.append(f'<line x1="{n(lx)}" y1="78" x2="{n(lx + 28)}" y2="78" stroke="{colour}" '
                   f'stroke-width="2.5"{d}/>')
        out.append(text(lx + 34, 82, label, size=12))
    for idx, ic in enumerate(AIRPORTS):
        r_i, c_i = divmod(idx, cols)
        x0 = left0 + c_i * (pw + gap_x)
        y0 = top0 + r_i * (ph + gap_y)

        def x_of(ld, x0=x0):
            return x0 + pw * (ld - 3) / 45

        def y_of(v, y0=y0):
            return y0 + ph * (1 - v / y_max)

        out.append(text(x0, y0 - 8, ic, size=13, weight="bold"))
        for t in y_ticks:
            y = y_of(t)
            out.append(f'<line x1="{n(x0)}" y1="{n(y)}" x2="{n(x0 + pw)}" y2="{n(y)}" '
                       f'stroke="{GRIDLINE}" stroke-width="1"/>')
            out.append(text(x0 - 6, y + 4, f"{t:.1f}", size=10, anchor="end", fill=MUTED))
        for t in (3, 12, 24, 36, 48):
            out.append(text(x_of(t), y0 + ph + 14, str(t), size=10, anchor="middle", fill=MUTED))
        out.append(f'<line x1="{n(x0)}" y1="{n(y_of(0))}" x2="{n(x0 + pw)}" y2="{n(y_of(0))}" '
                   f'stroke="{INK}" stroke-width="1"/>')
        out.append(text(x0 + pw / 2, y0 + ph + 29, "forecast hour", size=10, anchor="middle", fill=MUTED))
        if c_i == 0:
            cy = y0 + ph / 2
            out.append(f'<text x="14" y="{n(cy)}" font-size="10" text-anchor="middle" fill="{INK}" '
                       f'transform="rotate(-90 14 {n(cy)})">MAE (degrees C)</text>')
        for method, colour in (("raw_gfs", RAW_COLOUR), ("curve", MODEL_COLOUR)):
            for look, dash in (("A", ""), ("B", ' stroke-dasharray="5 4"')):
                vals = series[(ic, look, method)]
                pts = " ".join(f"{n(x_of(ld))},{n(y_of(v))}" for ld, v in zip(leads, vals))
                out.append(f'<polyline points="{pts}" fill="none" stroke="{colour}" '
                           f'stroke-width="2"{dash}/>')
                print(f"  {ic} look {look} {method}: " + " ".join(f"{v:.4f}" for v in vals))
    out.append(text(20, height - 12, "Look A: runs 2024-08-01 to 2025-07-31. Look B: runs 2025-08-01 to "
                    "2026-07-31. Data is GFS v16 (D100.10).", size=11, fill=MUTED))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def main():
    print("session 108 figures (offline, standard library only)")
    print(f"python {sys.version.split()[0]}")
    targets = [OUT_DIR / "stagec_headline.svg", OUT_DIR / "stagec_mae_by_lead.svg"]
    for t in targets:
        if t.exists():
            raise SystemExit(f"STOP: {t} exists; figures are written once")
    verdicts = load_verdicts()
    half = raw_half(verdicts)
    print("checked: 24 raw GFS halves, 100 x (1 - curve / raw) at 2 decimals equals F150.2: PASS")
    scores = load_scores()
    # the days file is an input of the record; its hash is checked, nothing is read from it
    read_checked(DAYS, DAYS_SHA256)
    print("stagec_headline.svg values:")
    svg1 = headline(half)
    leads, series = pooled_by_lead(scores, half)
    print("stagec_mae_by_lead.svg values (MAE at leads 3 to 48):")
    svg2 = by_lead(leads, series)
    for path, svg in zip(targets, (svg1, svg2)):
        if chr(0x2014) in svg:
            raise SystemExit("STOP: em-dash in figure text")
        write_once(path, svg)


if __name__ == "__main__":
    main()
