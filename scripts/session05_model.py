"""Session 05: the objective fix (Q15). ONE change only.

Session 04 fitted the model with LightGBM's default squared-error objective but
judged it on mean absolute error (SPEC 5.1). That is a mismatch: the model
should be trained on the same thing it is measured on. This script makes that
single change - objective="regression_l1" - and re-runs the session 04
validation rehearsal unchanged, so the effect of that one fix can be seen on
its own.

This is a correctness fix, not tuning. Nothing else was touched: same split
(DECISIONS D18), same features (D19), same tree settings, same seed, same
deterministic run. PART 0 below proves that rather than just claiming it - it
reads scripts/session04_model.py and compares it with this file.

Reads only from data/raw/. Never writes to data/raw/. Fills nothing (SPEC 2.2).

THE TEST YEAR IS SEALED. The test window (2025-08-01 to 2026-07-31, DECISIONS
D13) is filtered out at load time: the 2026 raw chunk files are never opened at
all, and the 2025 chunk is cut off at 2025-07-31. No test-year value is loaded,
printed, averaged or fitted on.

The three periods used here (DECISIONS D18):
- inner-training : 2021-03-24 to 2024-07-31. Everything is fitted on this and
                   only this - the model, the climatology, the mean bias.
- validation     : 2024-08-01 to 2025-07-31. A practice stand-in for the sealed
                   test year, same August-to-July shape. Judged on, not
                   explored.
- test           : 2025-08-01 to 2026-07-31. Not touched this session.

Terms used here:
- "residual" = observed minus forecast. This is what the model learns
  (SPEC 4.2). The corrected forecast is forecast + predicted residual.
- "bias"     = the same quantity looked at as a summary rather than a target.
  A positive bias means the station was warmer than GFS said.
- "MAE"      = mean absolute error, the average size of the miss in degrees
  Celsius. Lower is better (SPEC 5.1).
- "objective" = the quantity the model tries to make small while it is being
  fitted. "regression" is squared error (big misses count much more than small
  ones); "regression_l1" is absolute error (every degree of miss counts the
  same), which is what SPEC 5.1 measures.
"""

import ast
import csv
import difflib
import json
import math
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# --- making LightGBM importable on this machine -------------------------------
# LightGBM's macOS build needs the OpenMP runtime library (libomp.dylib), which
# is not installed system-wide here and has no Homebrew to install it from.
# scikit-learn's macOS wheel ships its own copy, so we point the dynamic loader
# at that copy and restart the interpreter once. This changes nothing about the
# model - it only lets the library load. (DECISIONS Q16.)
_SENTINEL = "MLWX_LIBOMP_PATH_SET"
if _SENTINEL not in os.environ:
    _omp = Path(sys.prefix) / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" \
        / "site-packages" / "sklearn" / ".dylibs"
    if (_omp / "libomp.dylib").exists():
        os.environ[_SENTINEL] = "1"
        os.environ["DYLD_LIBRARY_PATH"] = \
            str(_omp) + os.pathsep + os.environ.get("DYLD_LIBRARY_PATH", "")
        os.execv(sys.executable, [sys.executable] + sys.argv)

import numpy as np                                        # noqa: E402
import lightgbm as lgb                                    # noqa: E402


# ------------------------------------------------------------------ constants

TARGET_HOUR = 12                      # 12:00 UTC (SPEC 4.1, session 04 P-1)

INNER_START = date(2021, 3, 24)       # DECISIONS D18
INNER_END = date(2024, 7, 31)
VALID_START = date(2024, 8, 1)
VALID_END = date(2025, 7, 31)

# Hard wall. Nothing at or after this date is loaded (DECISIONS D13).
SEALED_FROM = date(2025, 8, 1)

# Only the chunks that hold data before the sealed test year. The two 2026
# files are deliberately absent from this list - they are entirely test year.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),     # cut off at 2025-07-31 on load
]

# The one gap in the forecast series (DECISIONS F8), for reporting only.
GAP_START = date(2023, 12, 30)
GAP_END = date(2024, 1, 19)

# The model. Identical to session 04 EXCEPT the objective, which is the whole
# point of this session (DECISIONS Q15 -> D20). Nothing was retuned to suit the
# new objective; that would be fishing, and this session's scope forbids it.
LGB_PARAMS = dict(
    objective="regression_l1",        # absolute error - THE ONE CHANGE
    n_estimators=300,
    learning_rate=0.05,
    num_leaves=15,
    min_child_samples=40,
    subsample=1.0,
    colsample_bytree=1.0,
    reg_alpha=0.0,
    reg_lambda=0.0,
    random_state=42,
    n_jobs=1,
    deterministic=True,
    force_row_wise=True,
    verbose=-1,
)

CLIM_HALF_WINDOW_DAYS = 7.5           # climatology smoothing window, +/- days

PREV_SCRIPT = ROOT / "scripts" / "session04_model.py"

# Session 04's published results, copied from notes/session-04-check-output.txt
# and DECISIONS F14, for a side-by-side comparison. The four non-ML rows should
# come out identical this session; if they do not, the harness has drifted.
S04_MAE = {
    "Raw GFS":             dict(mae=1.239, bias=-0.278, rmse=1.630, worst=4.90),
    "Persistence":         dict(mae=2.226, bias=-0.017, rmse=2.928, worst=12.00),
    "Climatology":         dict(mae=2.865, bias=+0.020, rmse=3.656, worst=11.65),
    "Mean-bias reference": dict(mae=1.231, bias=-0.170, rmse=1.615, worst=4.79),
    "ML-corrected":        dict(mae=1.190, bias=-0.166, rmse=1.580, worst=5.76),
}
S04_SEASON = {                        # season -> (days, raw GFS MAE, ML MAE)
    "winter DJF": (90, 0.972, 1.068),
    "spring MAM": (92, 1.337, 1.363),
    "summer JJA": (90, 1.498, 1.204),
    "autumn SON": (91, 1.147, 1.121),
}
S04_IMPORTANCE = {                    # feature -> (gain, gain share %, splits)
    "forecast_temp_c": (7056.8, 51.8, 1651),
    "season_sin":      (3085.0, 22.6, 1141),
    "season_cos":      (3483.1, 25.6, 1408),
}
S04_INSAMPLE_ML = 0.857               # inner-training MAE, session 04

OUT = ROOT / "notes" / "session-05-check-output.txt"


class Tee:
    """Print to the screen and to the notes file at the same time."""

    def __init__(self, path):
        self.f = open(path, "w")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def line(title):
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ loading

def load_forecast_12z():
    """Return {date: forecast_temp_or_None} for 12:00 UTC, before the seal."""
    series = {}
    rows_seen = 0
    rows_sealed = 0
    for start, end in CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_EGLC_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        for t_str, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
            if t.hour != TARGET_HOUR:
                continue
            rows_seen += 1
            if t.date() >= SEALED_FROM:
                rows_sealed += 1
                continue
            series[t.date()] = v
    return series, rows_seen, rows_sealed


def load_obs_12z():
    """Return {date: observed_temp} for the 12:00 UTC hour, before the seal.

    The D14 pairing rule: the routine :50 report belongs to the hour it is
    nearest to, and only if it is within 15 minutes of it. So EGLC's 11:50
    report is the observation for 12:00. Anything further off is dropped and
    counted.
    """
    series = {}
    reports_at_12 = 0
    reports_sealed = 0
    no_temp = 0
    outside_15min = 0

    for start, end in CHUNKS:
        path = RAW / f"iem_asos_EGLC_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != TARGET_HOUR:
                    continue
                reports_at_12 += 1
                if nearest.date() >= SEALED_FROM:
                    reports_sealed += 1
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[nearest.date()] = float(raw)

    return series, reports_at_12, reports_sealed, no_temp, outside_15min


def all_days(start, end):
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


# ------------------------------------------------------------------ features

def year_fraction(d):
    """Where in the year this date sits, 0.0 to 1.0. Leap-year safe."""
    year_days = 366 if (d.year % 4 == 0 and (d.year % 100 != 0
                                             or d.year % 400 == 0)) else 365
    return (d.timetuple().tm_yday - 1) / year_days


def features(rows):
    """The D19 feature set: forecast temperature, and season as sin/cos.

    Season is encoded as the sine and cosine of the position in the year so
    that 31 December sits next to 1 January instead of at the opposite end of
    a number line. Hour of day is not a feature - the hour is fixed at 12:00.
    """
    x = []
    for r in rows:
        a = 2 * math.pi * year_fraction(r["date"])
        x.append([r["fc"], math.sin(a), math.cos(a)])
    return np.array(x, dtype=float)


FEATURE_NAMES = ["forecast_temp_c", "season_sin", "season_cos"]


# ------------------------------------------------------------------ helpers

def mae(errors):
    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))


def describe(vals, label, indent="    "):
    a = np.asarray(vals, dtype=float)
    print(f"{indent}{label}")
    print(f"{indent}  n      = {len(a):,}")
    print(f"{indent}  mean   = {a.mean():+.3f} degC")
    print(f"{indent}  median = {np.median(a):+.3f} degC")
    print(f"{indent}  st dev = {a.std(ddof=1):.3f} degC")
    print(f"{indent}  min    = {a.min():+.1f} degC   max = {a.max():+.1f} degC")
    print(f"{indent}  5th pct = {np.percentile(a, 5):+.2f}   "
          f"25th = {np.percentile(a, 25):+.2f}   "
          f"75th = {np.percentile(a, 75):+.2f}   "
          f"95th = {np.percentile(a, 95):+.2f}")
    print(f"{indent}  mean absolute size = {np.abs(a).mean():.3f} degC")


# ------------------------------------------------------------------ part 0

def _literal(node):
    """Read a constant out of the parsed source.

    Handles plain literals and the two call shapes these scripts use for
    constants: date(y, m, d) and dict(...).
    """
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "date":
        return date(*[ast.literal_eval(a) for a in node.args])
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "dict":
        return {k.arg: ast.literal_eval(k.value) for k in node.keywords}
    return ast.literal_eval(node)


def top_level(tree, name):
    """The value assigned to a module-level constant, or a marker if absent."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == name:
                    return _literal(node.value)
    return "<not found>"


def func_source(src, tree, name):
    """The exact source text of a top-level function, or None."""
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(src, node)
    return None


def prove_one_change():
    """Compare this script with session 04's, and show what differs."""
    line("PART 0 - proving ONE thing changed (the objective, and nothing else)")
    print("This does not just claim the change is isolated. It reads")
    print(f"{PREV_SCRIPT.relative_to(ROOT)} and compares it with this file.")

    old_src = PREV_SCRIPT.read_text()
    new_src = Path(__file__).read_text()
    old = ast.parse(old_src)
    new = ast.parse(new_src)

    sub("model settings, session 04 against session 05")
    old_p = top_level(old, "LGB_PARAMS")
    new_p = top_level(new, "LGB_PARAMS")
    keys = list(old_p) + [k for k in new_p if k not in old_p]
    print(f"    {'setting':<20} {'session 04':<22} {'session 05':<22} same?")
    n_diff = 0
    for k in keys:
        a = old_p.get(k, "<absent>")
        b = new_p.get(k, "<absent>")
        same = a == b
        if not same:
            n_diff += 1
        print(f"    {k:<20} {str(a):<22} {str(b):<22} "
              f"{'yes' if same else 'NO - CHANGED'}")
    print(f"    settings that differ: {n_diff}")

    sub("everything else that must be identical")
    consts = ["TARGET_HOUR", "INNER_START", "INNER_END", "VALID_START",
              "VALID_END", "SEALED_FROM", "CHUNKS", "GAP_START", "GAP_END",
              "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]
    print(f"    {'constant':<24} {'session 04':<34} same?")
    for c in consts:
        a = top_level(old, c)
        b = top_level(new, c)
        print(f"    {c:<24} {str(a):<34} {'yes' if a == b else 'NO - CHANGED'}")

    sub("the code that builds the data, the features and the baselines")
    print("    Compared character for character between the two scripts.")
    same_funcs = ["load_forecast_12z", "load_obs_12z", "all_days",
                  "year_fraction", "features", "mae", "describe", "join",
                  "bias_look", "climatology_from_inner"]
    for name in same_funcs:
        a = func_source(old_src, old, name)
        b = func_source(new_src, new, name)
        verdict = "identical" if a == b else "DIFFERS"
        print(f"    {name + '()':<26} {verdict}")

    sub("the one function that does differ, shown in full")
    a = func_source(old_src, old, "model_and_evaluate").splitlines()
    b = func_source(new_src, new, "model_and_evaluate").splitlines()
    diff = list(difflib.unified_diff(a, b, "session04", "session05", lineterm="",
                                     n=1))
    if not diff:
        print("    identical")
    for d in diff:
        print(f"    {d}")
    print()
    print("    The added line only hands the results back so PART D can print")
    print("    the session-04 comparison. It changes no calculation.")
    print("    (PART D itself and this PART 0 are new output-only code.)")


# ------------------------------------------------------------------ part A

def join():
    line("PART A - join the two series at 12:00 UTC")

    print(f"target hour: {TARGET_HOUR:02d}:00 UTC (SPEC 4.1)")
    print("pairing rule: the routine :50 report nearest the hour, and only if")
    print("              within 15 minutes of it (DECISIONS D14). In practice")
    print("              the 11:50 report is the observation for 12:00.")

    fc, fc_rows, fc_sealed = load_forecast_12z()
    obs, ob_rows, ob_sealed, ob_no_temp, ob_far = load_obs_12z()

    sub("the seal on the test year")
    print(f"    forecast chunk files opened : {len(CHUNKS)} "
          f"(the two 2026 files were not opened at all)")
    print(f"    forecast 12:00 rows seen    : {fc_rows:,}")
    print(f"    of those, dropped as sealed : {fc_sealed:,} "
          f"(dated {SEALED_FROM} or later)")
    print(f"    forecast 12:00 rows kept    : {len(fc):,}")
    print(f"    observation 12:00 reports seen   : {ob_rows:,}")
    print(f"    of those, dropped as sealed      : {ob_sealed:,}")
    print(f"    observation 12:00 reports kept   : {len(obs):,}")

    sub("observation reports rejected by the rules (not sealed, just unusable)")
    print(f"    reports more than 15 min from the hour, dropped (D14): {ob_far:,}")
    print(f"    reports carrying no temperature (M), dropped (2.2)   : {ob_no_temp:,}")

    periods = [
        ("inner-training 2021-03-24..2024-07-31", INNER_START, INNER_END),
        ("validation     2024-08-01..2025-07-31", VALID_START, VALID_END),
    ]

    built = {}
    sub("rows kept and dropped, by period")
    header = (f"    {'period':<38} {'days':>6} {'kept':>6} {'drop':>6} "
              f"{'no fc':>6} {'null fc':>8} {'no obs':>7}")
    print(header)
    for label, lo, hi in periods:
        rows = []
        n_no_fc = n_null_fc = n_no_obs = 0
        for d in all_days(lo, hi):
            f_val = fc.get(d, "absent")
            o_val = obs.get(d)
            bad = False
            if f_val == "absent":
                n_no_fc += 1
                bad = True
            elif f_val is None:
                n_null_fc += 1
                bad = True
            if o_val is None:
                n_no_obs += 1
                bad = True
            if bad:
                continue
            rows.append({"date": d, "fc": float(f_val), "obs": float(o_val),
                         "resid": float(o_val) - float(f_val)})
        days = len(all_days(lo, hi))
        dropped = days - len(rows)
        print(f"    {label:<38} {days:>6,} {len(rows):>6,} {dropped:>6,} "
              f"{n_no_fc:>6,} {n_null_fc:>8,} {n_no_obs:>7,}")
        built[label.split()[0]] = rows

    print()
    print("    columns: days = calendar days in the period; kept = paired rows;")
    print("             drop = days with no usable pair; then the reasons.")
    print("             'no fc'    = the forecast series had no row for 12:00;")
    print("             'null fc'  = it had a row but the value was null;")
    print("             'no obs'   = no usable :50 observation within 15 min.")
    print("             A day can fail on more than one reason, so the reason")
    print("             columns can add up to more than 'drop'.")
    print("    Nothing was filled in (SPEC 2.2).")

    inner, valid = built["inner-training"], built["validation"]

    # Prove the seal held rather than just asserting it in prose.
    assert max(fc) < SEALED_FROM, "a sealed forecast date got through"
    assert max(obs) < SEALED_FROM, "a sealed observation date got through"
    assert max(r["date"] for r in valid) < SEALED_FROM

    sub("where the dropped inner-training days sit (Q10 - the F8 forecast gap)")
    gap_days = [d for d in all_days(INNER_START, INNER_END)
                if GAP_START <= d <= GAP_END]
    kept_dates = {r["date"] for r in inner}
    in_gap_dropped = [d for d in gap_days if d not in kept_dates]
    other_dropped = [d for d in all_days(INNER_START, INNER_END)
                     if d not in kept_dates and not (GAP_START <= d <= GAP_END)]
    print(f"    the F8 forecast gap covers {len(gap_days)} calendar days "
          f"({GAP_START} to {GAP_END})")
    print(f"    of those, days dropped here: {len(in_gap_dropped)}")
    print(f"    inner-training days dropped for any other reason: "
          f"{len(other_dropped)}")
    if other_dropped:
        print("    those other dropped days:")
        for d in other_dropped:
            why = []
            if d not in fc:
                why.append("no forecast row")
            elif fc[d] is None:
                why.append("forecast null")
            if d not in obs:
                why.append("no usable observation")
            print(f"      {d}  ({', '.join(why)})")

    sub("the dropped validation days, named")
    v_kept = {r["date"] for r in valid}
    v_dropped = [d for d in all_days(VALID_START, VALID_END) if d not in v_kept]
    if not v_dropped:
        print("    (none)")
    for d in v_dropped:
        why = []
        if d not in fc:
            why.append("no forecast row")
        elif fc[d] is None:
            why.append("forecast null")
        if d not in obs:
            why.append("no usable observation")
        print(f"    {d}  ({', '.join(why)})")

    sub("first and last kept rows of each period (a shape check)")
    for label, rows in (("inner-training", inner), ("validation", valid)):
        print(f"    {label:<15} {rows[0]['date']} -> {rows[-1]['date']}   "
              f"{len(rows):,} rows")

    return inner, valid, obs


# ------------------------------------------------------------------ part B

def bias_look(inner):
    line("PART B - the raw bias, INNER-TRAINING ONLY (addresses Q11)")
    print("bias = observed minus forecast. Positive means the station was")
    print("warmer than GFS predicted. Inner-training days only; the validation")
    print("year's values are not looked at here, and the test year not at all.")

    resid = [r["resid"] for r in inner]

    sub("overall")
    describe(resid, "bias (observed - forecast), inner-training")

    print()
    print(f"    raw GFS MAE on inner-training (in sample): "
          f"{mae(resid):.3f} degC")
    warm = sum(1 for v in resid if v > 0)
    print(f"    days the station was warmer than the forecast: {warm:,} "
          f"of {len(resid):,} ({100 * warm / len(resid):.1f}%)")

    sub("bias against forecast temperature (is the cold tail worse?)")
    edges = [-10, 0, 5, 10, 15, 20, 25, 45]
    print(f"    {'forecast band (degC)':<22} {'days':>6} {'mean bias':>10} "
          f"{'st dev':>8} {'mean |bias|':>12}")
    for lo, hi in zip(edges[:-1], edges[1:]):
        sel = [r["resid"] for r in inner if lo <= r["fc"] < hi]
        if not sel:
            continue
        a = np.array(sel)
        label = f"{lo} to {hi}"
        print(f"    {label:<22} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{(a.std(ddof=1) if len(a) > 1 else float('nan')):>8.3f} "
              f"{np.abs(a).mean():>12.3f}")

    print()
    print("    the coldest and warmest tenths of forecast days, side by side:")
    by_fc = sorted(inner, key=lambda r: r["fc"])
    tenth = max(1, len(by_fc) // 10)
    for label, sel in (("coldest 10% of forecasts", by_fc[:tenth]),
                       ("warmest 10% of forecasts", by_fc[-tenth:])):
        a = np.array([r["resid"] for r in sel])
        f = np.array([r["fc"] for r in sel])
        print(f"      {label:<26} n={len(sel):>4,}  forecast "
              f"{f.min():+.1f} to {f.max():+.1f} degC   "
              f"mean bias {a.mean():+.3f}   mean |bias| {np.abs(a).mean():.3f}")

    sub("bias by month (season)")
    print(f"    {'month':<8} {'days':>6} {'mean bias':>10} {'st dev':>8} "
          f"{'mean |bias|':>12} {'mean forecast':>14}")
    names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    for m in range(1, 13):
        sel = [r for r in inner if r["date"].month == m]
        if not sel:
            continue
        a = np.array([r["resid"] for r in sel])
        f = np.array([r["fc"] for r in sel])
        print(f"    {names[m - 1]:<8} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{a.std(ddof=1):>8.3f} {np.abs(a).mean():>12.3f} "
              f"{f.mean():>+14.2f}")

    sub("bias by season (three-month groups)")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    print(f"    {'season':<12} {'days':>6} {'mean bias':>10} {'st dev':>8} "
          f"{'mean |bias|':>12}")
    for label, months in groups:
        sel = [r["resid"] for r in inner if r["date"].month in months]
        a = np.array(sel)
        print(f"    {label:<12} {len(sel):>6,} {a.mean():>+10.3f} "
              f"{a.std(ddof=1):>8.3f} {np.abs(a).mean():>12.3f}")

    return float(np.mean(resid))


# ------------------------------------------------------------------ part C

def climatology_from_inner(inner):
    """Day-of-year seasonal average of the OBSERVED temperature.

    Built from inner-training days only (SPEC 2.1c). For a given position in
    the year it averages every inner-training observation within +/- 7.5 days
    of that position, measured around the circle so that late December and
    early January are neighbours. The window smooths what would otherwise be
    three or four noisy days per date.
    """
    fracs = np.array([year_fraction(r["date"]) for r in inner])
    obs = np.array([r["obs"] for r in inner])
    half = CLIM_HALF_WINDOW_DAYS / 365.25

    def predict(d):
        f = year_fraction(d)
        dist = np.abs(fracs - f)
        dist = np.minimum(dist, 1.0 - dist)        # go round the circle
        sel = dist <= half
        return float(obs[sel].mean()), int(sel.sum())

    return predict


def model_and_evaluate(inner, valid, obs_all, inner_mean_bias):
    line("PART C - build the model, then rehearse the evaluation")

    # ---------------------------------------------------------------- the model
    sub("the model (fitted on inner-training only)")
    x_in = features(inner)
    y_in = np.array([r["resid"] for r in inner], dtype=float)
    print(f"    rows fitted on : {len(x_in):,}  "
          f"({inner[0]['date']} to {inner[-1]['date']})")
    print(f"    features       : {', '.join(FEATURE_NAMES)}  (DECISIONS D19)")
    print("    target         : residual, observed minus forecast (SPEC 4.2)")
    print("    settings (fixed before running, not tuned this session):")
    for k, v in LGB_PARAMS.items():
        print(f"      {k} = {v}")

    model = lgb.LGBMRegressor(**LGB_PARAMS)
    model.fit(x_in, y_in)
    print(f"    trees actually built: {model.booster_.num_trees():,}")

    # ------------------------------------------------- the common validation set
    sub("the common validation set (every method judged on the same days)")
    common = []
    no_prev = []
    for r in valid:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            no_prev.append(r["date"])
            continue
        row = dict(r)
        row["persist"] = float(prev)
        common.append(row)

    print(f"    paired validation rows from part A           : {len(valid):,}")
    print(f"    dropped: no previous-day 12:00 observation   : {len(no_prev):,}"
          + (f"  ({', '.join(str(d) for d in no_prev)})" if no_prev else ""))
    print(f"    days every method is scored on               : {len(common):,}")
    print(f"    date range                                   : "
          f"{common[0]['date']} to {common[-1]['date']}")
    print("    Persistence needs yesterday's observation, which is a past-only")
    print("    value (SPEC 2.1d). Nothing was filled in (SPEC 2.2).")

    # ------------------------------------------------------------- the methods
    clim = climatology_from_inner(inner)
    clim_counts = []
    for r in common:
        c, n = clim(r["date"])
        r["clim"] = c
        clim_counts.append(n)
    print(f"    climatology: built from inner-training only (SPEC 2.1c), "
          f"+/-{CLIM_HALF_WINDOW_DAYS:.1f} days")
    print(f"                 inner-training days behind each value: "
          f"min {min(clim_counts)}, max {max(clim_counts)}, "
          f"mean {np.mean(clim_counts):.1f}")

    print(f"    mean-bias reference: forecast + {inner_mean_bias:+.4f} degC, "
          f"that figure being the")
    print("                 mean inner-training bias and nothing else.")

    x_va = features(common)
    pred_resid = model.predict(x_va)

    methods = {}
    for r, pr in zip(common, pred_resid):
        methods.setdefault("Raw GFS", []).append(r["fc"] - r["obs"])
        methods.setdefault("Persistence", []).append(r["persist"] - r["obs"])
        methods.setdefault("Climatology", []).append(r["clim"] - r["obs"])
        methods.setdefault("Mean-bias reference", []).append(
            r["fc"] + inner_mean_bias - r["obs"])
        methods.setdefault("ML-corrected", []).append(
            r["fc"] + float(pr) - r["obs"])

    order = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference",
             "ML-corrected"]

    sub(f"VALIDATION-YEAR MAE, {len(common):,} common days "
        f"({VALID_START} to {VALID_END})")
    print(f"    {'method':<22} {'MAE degC':>9} {'bias degC':>10} "
          f"{'RMSE degC':>10} {'worst miss':>11}")
    for name in order:
        e = np.array(methods[name])
        print(f"    {name:<22} {np.abs(e).mean():>9.3f} {(-e.mean()):>+10.3f} "
              f"{math.sqrt((e ** 2).mean()):>10.3f} "
              f"{np.abs(e).max():>11.2f}")
    print()
    print("    MAE  = average size of the miss. Lower is better (SPEC 5.1).")
    print("    bias = mean of (observed - method), so a positive figure means")
    print("           the method ran cold. Shown for information only.")

    # ------------------------------------------------------------ the verdicts
    ml = mae(methods["ML-corrected"])

    sub("does the correction beat each reference on validation MAE?")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference"]:
        ref = mae(methods[name])
        won = ml < ref
        print(f"    vs {name:<22} {'YES' if won else 'NO ':<4} "
              f"{ml:.3f} against {ref:.3f}  -> "
              f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)")
    ref = mae(methods["Climatology"])
    print(f"    vs {'Climatology':<22} {'YES' if ml < ref else 'NO ':<4} "
          f"{ml:.3f} against {ref:.3f}  -> "
          f"{ref - ml:+.3f} degC ({100 * (ref - ml) / ref:+.1f}%)   "
          f"(optional third check, SPEC 5.2)")

    print()
    print("    This is a VALIDATION REHEARSAL, not the frozen bar (SPEC 5.3).")
    print("    The frozen bar is judged once, on the sealed test year, in a")
    print("    later session. A good number here means the method is ready for")
    print("    that single look - it does not mean stage 1 has passed.")

    # ---------------------------------------------------- what the model used
    sub("what the model used (feature importances, a sanity check)")
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'gain':>14} {'gain share':>11} {'splits':>8}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        print(f"    {n:<18} {g:>14.1f} {share:>10.1f}% {s:>8,}")

    sub("in-sample check only (inner-training, NOT a result)")
    in_pred = model.predict(x_in)
    print(f"    raw GFS MAE on inner-training      : {mae(y_in):.3f} degC")
    print(f"    ML-corrected MAE on inner-training : "
          f"{mae(y_in - in_pred):.3f} degC")
    print("    Shown only to confirm the fit did something. A model always")
    print("    looks better on the data it was fitted to, so this number")
    print("    proves nothing about performance.")

    sub("how the correction behaved across the validation year, by season")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'ML-corr':>9} "
          f"{'change':>9}")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    for label, months in groups:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw = np.array([methods["Raw GFS"][i] for i in idx])
        mlv = np.array([methods["ML-corrected"][i] for i in idx])
        print(f"    {label:<12} {len(idx):>6,} {np.abs(raw).mean():>9.3f} "
              f"{np.abs(mlv).mean():>9.3f} "
              f"{np.abs(mlv).mean() - np.abs(raw).mean():>+9.3f}")
    print("    (A per-season breakdown of the rehearsal. SPEC 5.4 parks")
    print("     season-by-season testing as a deeper check for later; this is")
    print("     here only to show the win is not one freak month.)")

    sub("the predicted correction itself, validation year")
    describe(pred_resid, "predicted residual applied to the forecast")

    return dict(common=common, methods=methods, model=model,
                in_sample_ml=mae(y_in - in_pred))


# ------------------------------------------------------------------ part D

def compare_with_session04(res):
    """Session 05 beside session 04, on the same validation days."""
    line("PART D - session 05 beside session 04 (the effect of the one change)")
    print("Session 04's figures are quoted from notes/session-04-check-output.txt")
    print("(DECISIONS F14). Only the ML-corrected row should have moved. The")
    print("other four are a cross-check that the harness is unchanged.")

    common, methods = res["common"], res["methods"]
    order = ["Raw GFS", "Persistence", "Climatology", "Mean-bias reference",
             "ML-corrected"]

    sub(f"validation MAE, same {len(common):,} common days")
    print(f"    {'method':<22} {'s04 MAE':>9} {'s05 MAE':>9} {'change':>9}  note")
    for name in order:
        now = mae(methods[name])
        then = S04_MAE[name]["mae"]
        note = ("expected to move (this is the change)" if name == "ML-corrected"
                else ("unchanged" if abs(now - then) < 0.0005
                      else "DRIFTED - the harness is not identical"))
        print(f"    {name:<22} {then:>9.3f} {now:>9.3f} {now - then:>+9.3f}  "
              f"{note}")

    sub("the headline: the objective fix on its own")
    now = mae(methods["ML-corrected"])
    then = S04_MAE["ML-corrected"]["mae"]
    print(f"    session 04, squared-error objective : {then:.3f} degC")
    print(f"    session 05, absolute-error objective: {now:.3f} degC")
    print(f"    change                              : {now - then:+.3f} degC "
          f"({100 * (now - then) / then:+.1f}%)")
    if now < then:
        print("    -> lower MAE, so the fix helped.")
    elif now > then:
        print("    -> higher MAE, so the fix cost something on this year.")
    else:
        print("    -> no change at all.")
    print("    Either way the change was made because it is correct: the model")
    print("    is now fitted on the same quantity SPEC 5.1 measures.")

    sub("margins over the references, session 04 -> session 05")
    print(f"    {'vs':<22} {'s04 margin':>12} {'s05 margin':>12} {'still wins?':>12}")
    for name in ["Raw GFS", "Persistence", "Mean-bias reference", "Climatology"]:
        ref_now = mae(methods[name])
        ref_then = S04_MAE[name]["mae"]
        m_then = ref_then - then
        m_now = ref_now - now
        print(f"    {name:<22} {m_then:>+12.3f} {m_now:>+12.3f} "
              f"{('YES' if now < ref_now else 'NO'):>12}")
    print("    Margins are degC of MAE saved. Positive means the correction is")
    print("    ahead of that reference.")

    sub("per-season, session 04 -> session 05 (did the summer-only picture change?)")
    print(f"    {'season':<12} {'days':>6} {'raw GFS':>9} {'s04 ML':>9} "
          f"{'s05 ML':>9} {'s04 chg':>9} {'s05 chg':>9}")
    groups = [("winter DJF", (12, 1, 2)), ("spring MAM", (3, 4, 5)),
              ("summer JJA", (6, 7, 8)), ("autumn SON", (9, 10, 11))]
    for label, months in groups:
        idx = [i for i, r in enumerate(common) if r["date"].month in months]
        raw = float(np.abs(np.array([methods["Raw GFS"][i] for i in idx])).mean())
        mlv = float(np.abs(np.array([methods["ML-corrected"][i] for i in idx])).mean())
        s04_days, s04_raw, s04_ml = S04_SEASON[label]
        print(f"    {label:<12} {len(idx):>6,} {raw:>9.3f} {s04_ml:>9.3f} "
              f"{mlv:>9.3f} {s04_ml - s04_raw:>+9.3f} {mlv - raw:>+9.3f}")
    print("    'chg' is the ML-corrected MAE minus raw GFS MAE for that season.")
    print("    Negative is better than raw GFS; positive is worse.")

    sub("feature importances, session 04 -> session 05")
    model = res["model"]
    gain = model.booster_.feature_importance(importance_type="gain")
    split = model.booster_.feature_importance(importance_type="split")
    print(f"    {'feature':<18} {'s04 gain %':>11} {'s05 gain %':>11} "
          f"{'s04 splits':>11} {'s05 splits':>11}")
    for n, g, s in zip(FEATURE_NAMES, gain, split):
        share = 100 * g / gain.sum() if gain.sum() else float("nan")
        s04_gain, s04_share, s04_splits = S04_IMPORTANCE[n]
        print(f"    {n:<18} {s04_share:>10.1f}% {share:>10.1f}% "
              f"{s04_splits:>11,} {s:>11,}")
    print("    Gain is on a different scale under an absolute-error objective,")
    print("    so only the shares and the split counts compare meaningfully.")

    sub("in-sample, for the record only (NOT a result)")
    print(f"    session 04 ML-corrected on inner-training: {S04_INSAMPLE_ML:.3f} degC")
    print(f"    session 05 ML-corrected on inner-training: "
          f"{res['in_sample_ml']:.3f} degC")
    print("    A model always looks better on the data it was fitted to.")


# ------------------------------------------------------------------ main

def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 05 - the objective fix (Q15). ONE change. TEST YEAR SEALED.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python        : {sys.version.split()[0]}")
    print(f"numpy         : {np.__version__}")
    print(f"lightgbm      : {lgb.__version__}")
    print(f"target hour   : {TARGET_HOUR:02d}:00 UTC (SPEC 4.1)")
    print(f"inner-training: {INNER_START} to {INNER_END}   (DECISIONS D18)")
    print(f"validation    : {VALID_START} to {VALID_END}   (DECISIONS D18)")
    print(f"sealed test   : {SEALED_FROM} onward - NOT LOADED THIS SESSION")
    print(f"the one change: objective 'regression' (squared error) -> "
          f"'{LGB_PARAMS['objective']}' (absolute error)")

    prove_one_change()
    inner, valid, obs_all = join()
    inner_mean_bias = bias_look(inner)
    res = model_and_evaluate(inner, valid, obs_all, inner_mean_bias)
    compare_with_session04(res)

    line("END")
    print("Raw files untouched. Nothing was filled (SPEC 2.2). No test-year")
    print("value was loaded, printed or fitted on. Nothing was committed.")
    print("This is a rehearsal on the validation year. The frozen bar")
    print("(SPEC 5.3) has NOT been judged and stage 1 has NOT passed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
