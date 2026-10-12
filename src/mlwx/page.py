"""The static page (DECISIONS D103.2, D103.9).

One HTML file, standard library only. Per airport: the latest cycle's raw GFS and corrected curve (an
inline SVG chart), the daily maxima read off the curve, and a status line: cycle, GFS version, issue
time, any stop, "drift warming up" while a tracker cell has fewer than 50 errors, and "not validated
on v17" when the version is v17. No accuracy figure is shown anywhere (D103.2): the page holds
temperatures, dates and counts of nothing but status.
"""

import datetime as dt
import html
from pathlib import Path

from . import dailymax, prediction_log
from . import state as state_mod

WARMUP_ERRORS = 50          # a cell with fewer errors than this is still warming up
W, H = 720, 260
ML, MR, MT, MB = 46, 12, 12, 40
STYLE = """
:root { --bg:#fbfbf9; --fg:#1d2326; --muted:#5d6a70; --card:#ffffff; --line:#d5dadc; --raw:#6a7a85; --cor:#c2410c; --warn:#92400e; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#15191b; --fg:#e8ecee; --muted:#9aa7ad; --card:#1d2326; --line:#37424a; --raw:#9db0bc; --cor:#fb923c; --warn:#fbbf24; } }
:root[data-theme="dark"] { --bg:#15191b; --fg:#e8ecee; --muted:#9aa7ad; --card:#1d2326; --line:#37424a; --raw:#9db0bc; --cor:#fb923c; --warn:#fbbf24; }
* { box-sizing: border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, sans-serif; }
main { max-width: 800px; margin: 0 auto; padding: 16px; }
h1 { font-size: 1.4rem; margin: 0 0 4px; }
h2 { font-size: 1.1rem; margin: 0; }
p.note, p.foot { color: var(--muted); font-size: .9rem; margin: 4px 0 12px; }
section { background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px; margin:12px 0; }
.status { color:var(--muted); font-size:.9rem; margin:2px 0 8px; }
.status .flag { color:var(--warn); font-weight:600; }
svg { width:100%; height:auto; display:block; }
svg text { fill: var(--muted); font-size: 11px; }
svg .grid { stroke: var(--line); stroke-width: 1; }
svg .raw { fill:none; stroke: var(--raw); stroke-width: 1.6; stroke-dasharray: 4 3; }
svg .cor { fill:none; stroke: var(--cor); stroke-width: 2; }
.legend { font-size:.85rem; color:var(--muted); margin:4px 0; }
.legend b { display:inline-block; width:18px; height:0; border-top:2px solid var(--cor); vertical-align:middle; margin-right:4px; }
.legend b.r { border-top:2px dashed var(--raw); margin-left:12px; }
table { border-collapse: collapse; width:100%; font-size:.9rem; }
th, td { text-align:right; padding:3px 8px; border-bottom:1px solid var(--line); }
th:first-child, td:first-child { text-align:left; }
"""


def _nice_ticks(lo, hi, n=5):
    span = max(hi - lo, 1.0)
    raw = span / n
    step = next(s for s in (1, 2, 5, 10, 20, 50) if s >= raw)
    start = (int(lo // step)) * step
    ticks, t = [], start
    while t <= hi + step:
        ticks.append(t)
        t += step
    return [t for t in ticks if lo - step <= t <= hi + step], step


def chart_svg(rows):
    """Raw GFS and corrected curve against valid time. rows: log rows of one airport, one cycle."""
    rows = sorted(rows, key=lambda r: r["valid"])
    t0, t1 = rows[0]["valid"], rows[-1]["valid"]
    ys = [r["raw_gfs"] for r in rows] + [r["corrected"] for r in rows]
    ticks, step = _nice_ticks(min(ys), max(ys))
    lo, hi = min(ticks), max(ticks)
    span_s = max((t1 - t0).total_seconds(), 1.0)

    def x(t):
        return ML + (W - ML - MR) * (t - t0).total_seconds() / span_s

    def y(v):
        return MT + (H - MT - MB) * (hi - v) / (hi - lo)

    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-label="Raw GFS and corrected 2 m temperature, degrees C">']
    for tk in ticks:
        out.append(f'<line class="grid" x1="{ML}" x2="{W - MR}" y1="{y(tk):.1f}" y2="{y(tk):.1f}"/>'
                   f'<text x="{ML - 6}" y="{y(tk) + 4:.1f}" text-anchor="end">{tk:g}</text>')
    t = t0.replace(minute=0, second=0, microsecond=0)
    while t <= t1:
        if t.hour % 12 == 0 and t >= t0:
            label = f"{t:%m-%d} {t:%H}z" if t.hour == 0 else f"{t:%H}z"
            out.append(f'<line class="grid" x1="{x(t):.1f}" x2="{x(t):.1f}" y1="{MT}" y2="{H - MB}"/>'
                       f'<text x="{x(t):.1f}" y="{H - MB + 14}" text-anchor="middle">{label}</text>')
        t += dt.timedelta(hours=1)
    for cls, key in (("raw", "raw_gfs"), ("cor", "corrected")):
        pts = " ".join(f"{x(r['valid']):.1f},{y(r[key]):.1f}" for r in rows)
        out.append(f'<polyline class="{cls}" points="{pts}"/>')
    out.append(f'<text x="{ML}" y="{H - 6}">valid time, UTC</text><text x="4" y="{MT + 8}">&#176;C</text>')
    out.append("</svg>")
    return "".join(out)


def status_line(a, rows, state, now):
    """The status line of one airport as (text, flags)."""
    r0 = rows[0]
    parts = [f"cycle {r0['cycle']:%Y-%m-%d %H}z", f"GFS {r0['gfs_version']}", f"issued {r0['issued']:%Y-%m-%d %H:%M} UTC"]
    flags = []
    if r0["gfs_version"] == "v17":
        flags.append("not validated on v17")
    cells = [state.cells.get(f"{a.icao}|{r0['cycle'].hour:02d}|{r['lead']}") for r in rows]
    if any(c is None or c.n < WARMUP_ERRORS for c in cells):
        flags.append("drift warming up")
    return ", ".join(parts), flags


def stop_notes(state, latest_cycle, now):
    """Stops worth showing: any newer than the latest issued cycle, or within the past 24 hours."""
    notes = []
    for s in state.stops:
        c = state_mod.parse(s["cycle"])
        if latest_cycle is None or c > latest_cycle or now - c <= dt.timedelta(hours=24):
            notes.append(f"cycle {c:%Y-%m-%d %H}z issued nothing: {s['reason']}")
    if state.last_run and state.last_run.get("status") == "waiting":
        notes.append("the last run could not fetch its data yet and will try again")
    return notes


def build_page(root, model, airports, state, now):
    root = Path(root)
    logs = prediction_log.logged_cycles(root, model.name)
    latest = max(logs) if logs else None
    rows = prediction_log.read_log(logs[latest]) if latest else []
    notes = stop_notes(state, latest, now)
    body = ["<main>", "<h1>MLwx live: corrected GFS temperature</h1>",
            '<p class="note">Version 1, GFS only. For each GFS run, a corrected 2 m temperature for the next 3 to 48 hours '
            "and the daily maximum read off that curve. No accuracy figure is shown for these live forecasts.</p>"]
    if latest:
        body.append(f'<p class="status">Latest cycle issued: {latest:%Y-%m-%d %H}z. Page built {now:%Y-%m-%d %H:%M} UTC.</p>')
    else:
        body.append(f'<p class="status">No cycle has been issued yet. Page built {now:%Y-%m-%d %H:%M} UTC.</p>')
    for n in notes:
        body.append(f'<p class="status"><span class="flag">{html.escape(n)}</span></p>')
    for a in airports:
        mine = [r for r in rows if r["airport"] == a.icao]
        if not mine:
            continue
        text, flags = status_line(a, mine, state, now)
        curve_raw = {r["valid"]: r["raw_gfs"] for r in mine}
        curve_cor = {r["valid"]: r["corrected"] for r in mine}
        first = min(r["lead"] for r in mine)
        last = max(r["lead"] for r in mine)
        mx_raw = dailymax.daily_maxima(latest, a.time_zone, curve_raw, first, last)
        mx_cor = dailymax.daily_maxima(latest, a.time_zone, curve_cor, first, last)
        body.append(f'<section><h2>{html.escape(a.icao)}</h2>')
        flag_html = "".join(f' <span class="flag">{html.escape(f)}.</span>' for f in flags)
        body.append(f'<p class="status">{html.escape(text)}.{flag_html}</p>')
        body.append(chart_svg(mine))
        body.append('<p class="legend"><b></b>corrected<b class="r"></b>raw GFS</p>')
        if mx_cor:
            body.append(f"<table><tr><th>Local day ({html.escape(a.time_zone)})</th><th>Raw GFS max, &#176;C</th>"
                        "<th>Corrected max, &#176;C</th></tr>")
            for d in sorted(mx_cor):
                body.append(f"<tr><td>{d:%Y-%m-%d}</td><td>{mx_raw[d]:.1f}</td><td>{mx_cor[d]:.1f}</td></tr>")
            body.append("</table>")
        else:
            body.append('<p class="status">No local day lies wholly inside this cycle\'s curve.</p>')
        body.append("</section>")
    body.append('<p class="foot">The prediction log is written once per cycle and never edited; a correction is a new file. '
                "Source code: the MLwx repository.</p></main>")
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            "<title>MLwx live</title><style>" + STYLE + "</style></head><body>" + "\n".join(body) + "</body></html>\n")


def write_page(root, model, airports, state, now):
    out = Path(root) / "site" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_text(build_page(root, model, airports, state, now), encoding="utf-8")
    tmp.replace(out)
    return out
