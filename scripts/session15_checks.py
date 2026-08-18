"""Session 15 part C: the gap map for both DSM series, plus Q27.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

This is session 03b's and session 10's gap map, pointed at the third airport.
It counts rows and maps where the holes are. It does NOT join the two series,
and it does not build or evaluate anything.

The test window stays sealed. For 2025-08-01 onward this script reports only
*structure* - how many rows exist, where the holes are, and how many days a
rule would drop. It never prints a temperature value, a range or an average
from the test window. Value ranges are printed for the training window only,
purely to catch something obviously wrong such as temperatures arriving in
Kelvin instead of Celsius.

Two things here are new, and both come from DSM rather than from the method:

- **The target hour is 18:00 UTC, not 12:00** (DECISIONS D33). That is local
  standard noon at Des Moines; 12:00 UTC there is dawn. Everything that counts
  days at a target hour counts them at 18:00.

- **Q26, the request-boundary artefact.** DSM files its routine report at :54
  (F34), so the report that serves hour H is stamped (H-1):54. The first hour
  of any request window therefore needs a report from before that window. The
  yearly chunks are contiguous, so concatenating them closes that seam at
  every internal boundary; only the very first hour of the whole period is
  genuinely uncovered. This script proves that rather than assuming it: it
  maps each chunk in isolation, then maps the concatenated series, and reports
  the difference. Nothing is filled to cover the artefact.

It also answers Q27: does `gfs_global` return the same data as `gfs_seamless`
at DSM? F6 proved they match at EGLC, but its argument rested on no CONUS-only
NCEP model being able to apply in London. Des Moines is inside CONUS, so the
argument does not carry and the comparison has to be made.

Terms used here:
- "expected hour" = every hour in the period. A perfect record would have one
  usable value for each.
- "gap" = an expected hour with no usable temperature: either no row at all,
  or a row whose value is null (forecast) or marked M (observation).
- "gap run" = gap hours that sit next to each other, reported as one line so a
  long outage does not print as hundreds of separate hours.
- "off-hour report" = a routine METAR stamped more than 15 minutes from any
  whole hour, which the pairing rule D14 refuses.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

STATION = "DSM"
MODEL = "gfs_global"
MODEL_SEAMLESS = "gfs_seamless"

PERIOD_START = datetime(2021, 3, 24, 0, 0)
PERIOD_END = datetime(2026, 7, 31, 23, 0)      # inclusive, hourly

# The split fixed in DECISIONS D13 / SPEC 4.3. Shared by every airport.
TRAIN_END = datetime(2025, 7, 31, 23, 0)       # inclusive
TEST_START = datetime(2025, 8, 1, 0, 0)

# DSM's target hour (DECISIONS D33, SPEC 3.4/4.1). Local standard noon.
TARGET_HOUR = 18

# D14's tolerance: a report more than this many minutes from the hour is
# dropped and counted, never shifted or filled.
D14_TOLERANCE_MIN = 15

CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

Q27_WINDOWS = [
    ("2021-03-24", "2021-04-05", "early, inside the training window"),
    ("2026-08-05", "2026-08-15", "recent, after the project period ends"),
]

# The gap DECISIONS F8 mapped at EGLC and F22 found again at LFPG.
SHARED_GAP_START = datetime(2023, 12, 30, 0, 0)
SHARED_GAP_END = datetime(2024, 1, 19, 11, 0)
SHARED_GAP_HOURS = 492

# What session 14 recorded for DSM, to check the full pull describes the same
# place the samples did (DECISIONS F31).
F31_GRID = (41.52945, -93.63281, 285.0)
F31_STATION_POS = (41.534, -93.6531)


def line(title):
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)


def expected_hours(start, end):
    out = []
    cur = start
    while cur <= end:
        out.append(cur)
        cur += timedelta(hours=1)
    return out


def gap_runs(missing):
    """Turn a sorted list of missing hours into (start, end, count) runs."""
    runs = []
    for h in missing:
        if runs and h - runs[-1][1] == timedelta(hours=1):
            runs[-1][1] = h
            runs[-1][2] += 1
        else:
            runs.append([h, h, 1])
    return [tuple(r) for r in runs]


def print_runs(runs, indent="    ", limit=None):
    if not runs:
        print(f"{indent}(none)")
        return
    shown = runs if limit is None else runs[:limit]
    for start, end, n in shown:
        print(f"{indent}{start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} UTC   "
              f"{n:5d} hour{'s' if n != 1 else ''}")
    if limit is not None and len(runs) > limit:
        print(f"{indent}... and {len(runs) - limit} more run(s)")


def size_summary(runs, indent="    "):
    """Group gap runs by how long they are, so the shape is easy to see."""
    buckets = [("1 hour", 1, 1), ("2-5 hours", 2, 5), ("6-23 hours", 6, 23),
               ("1-7 days", 24, 167), ("over 7 days", 168, 10 ** 9)]
    print(f"{indent}{'run length':<14} {'runs':>6} {'hours':>8}")
    for label, lo, hi in buckets:
        sel = [r for r in runs if lo <= r[2] <= hi]
        if sel:
            print(f"{indent}{label:<14} {len(sel):>6} "
                  f"{sum(r[2] for r in sel):>8}")


def window_split(exp, missing, label_pairs):
    for label, lo, hi in label_pairs:
        win = [h for h in exp if lo <= h <= hi]
        miss = [h for h in missing if lo <= h <= hi]
        print(f"  {label}: {len(win):,} hours expected, "
              f"{len(win) - len(miss):,} usable, {len(miss):,} missing "
              f"({100 * len(miss) / len(win):.2f}%)")


WINDOWS = [
    ("training 2021-03-24..2025-07-31", PERIOD_START, TRAIN_END),
    ("test     2025-08-01..2026-07-31", TEST_START, PERIOD_END),
]


def nearest_hour(t):
    """The whole hour a timestamp is nearest to."""
    return (t + timedelta(minutes=30)).replace(minute=0, second=0,
                                               microsecond=0)


# --------------------------------------------------------- model string check

def model_string_check():
    """Read the model string back out of the saved provenance files.

    D16 pins `gfs_global`. The pull script sets it in one constant, so this is
    not proof against a bug in that script - but it is proof about what was
    actually requested, because the .meta.txt files record the exact URL that
    went to the API (SPEC 2.3).
    """
    line("D16 - was every DSM forecast chunk pulled with gfs_global?")
    ok = True
    for start, end in CHUNKS:
        meta = RAW / (f"openmeteo_previousruns_{MODEL}_{STATION}_"
                      f"{start}_{end}.json.meta.txt")
        text = meta.read_text()
        url_line = next(l for l in text.splitlines()
                        if l.startswith("https://previous-runs-api"))
        has = f"models={MODEL}" in url_line
        seamless = MODEL_SEAMLESS in url_line
        ok = ok and has and not seamless
        print(f"  {start}..{end}  models={MODEL}: "
              f"{'yes' if has else 'NO'}   {MODEL_SEAMLESS} present: "
              f"{'YES - PROBLEM' if seamless else 'no'}")
    print(f"\n  all {len(CHUNKS)} forecast chunks used {MODEL}: "
          f"{'YES' if ok else 'NO'}")


# ------------------------------------------------------------------- Q27

def load_probe(path):
    with open(path) as f:
        d = json.load(f)
    h = d["hourly"]
    times = [datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in h["time"]]
    vals = h["temperature_2m_previous_day1"]
    grid = (d["latitude"], d["longitude"], d["elevation"])
    return dict(zip(times, vals)), grid, d


def q27_compare():
    """Q27: gfs_global versus gfs_seamless at a CONUS point."""
    line(f"Q27 - {MODEL} vs {MODEL_SEAMLESS} at {STATION} (Des Moines is in "
         "CONUS)")
    print("F6 proved the two strings return identical data AT EGLC, but its")
    print("argument was location-specific: no CONUS-only NCEP model (HRRR,")
    print("NAM, NBM) can apply in London, so nothing non-GFS was in the")
    print("seamless set to mix in. Des Moines IS inside CONUS, so that")
    print("argument does not carry and the comparison has to be measured.")
    print()
    print("Neither window touches the sealed test year (2025-08-01 to")
    print("2026-07-31). The recent window sits after the project period ends")
    print("on 2026-07-31, which D13 does not use at all.")

    all_same = True
    for start, end, why in Q27_WINDOWS:
        g_path = RAW / (f"openmeteo_previousruns_{MODEL}_{STATION}_"
                        f"{start}_{end}_q27compare.json")
        s_path = RAW / (f"openmeteo_previousruns_{MODEL_SEAMLESS}_{STATION}_"
                        f"{start}_{end}_q27compare.json")
        g, g_grid, g_raw = load_probe(g_path)
        s, s_grid, s_raw = load_probe(s_path)

        print(f"\n-- window {start} .. {end}  ({why}) --")
        print(f"    {MODEL:<14} grid lat {g_grid[0]}, lon {g_grid[1]}, "
              f"elev {g_grid[2]} m")
        print(f"    {MODEL_SEAMLESS:<14} grid lat {s_grid[0]}, lon {s_grid[1]}, "
              f"elev {s_grid[2]} m")
        print(f"    same grid point : "
              f"{'YES' if g_grid == s_grid else 'NO - a different model'}")

        hours = sorted(set(g) | set(s))
        only_g = [h for h in hours if h not in s]
        only_s = [h for h in hours if h not in g]
        both = [h for h in hours if h in g and h in s]
        diff = [h for h in both if g[h] != s[h]]
        g_null = sum(1 for h in g if g[h] is None)
        s_null = sum(1 for h in s if s[h] is None)

        print(f"    hours in {MODEL:<14}: {len(g):,}   null: {g_null}")
        print(f"    hours in {MODEL_SEAMLESS:<14}: {len(s):,}   null: {s_null}")
        print(f"    hours in one series only    : "
              f"{len(only_g)} / {len(only_s)}")
        print(f"    hours compared              : {len(both):,}")
        print(f"    values that DIFFER          : {len(diff)}")
        if diff:
            all_same = False
            biggest = max(abs((g[h] or 0) - (s[h] or 0)) for h in diff)
            print(f"    largest difference          : {biggest:.4f} degC")
            for h in diff[:20]:
                print(f"      {h:%Y-%m-%d %H:%M}  {MODEL}={g[h]}  "
                      f"{MODEL_SEAMLESS}={s[h]}")
            if len(diff) > 20:
                print(f"      ... and {len(diff) - 20} more")

        # The raw files were byte-compared too - a cheap independent check.
        same_bytes = g_path.read_bytes() == s_path.read_bytes()
        print(f"    raw files byte-identical    : "
              f"{'YES' if same_bytes else 'no'}")
        if not same_bytes:
            for key in ("generationtime_ms", "utc_offset_seconds", "timezone",
                        "timezone_abbreviation"):
                if g_raw.get(key) != s_raw.get(key):
                    print(f"      differs in {key}: {g_raw.get(key)!r} vs "
                          f"{s_raw.get(key)!r}")

    print(f"\n  Q27 VERDICT: at {STATION}, {MODEL} and {MODEL_SEAMLESS} "
          f"return "
          f"{'IDENTICAL values on every hour compared' if all_same else 'DIFFERENT values - see above'}.")
    print(f"  The project pulled with {MODEL} regardless (D16). The pin is")
    print("  what makes 'this is exactly NCEP GFS' true by construction.")


# ---------------------------------------------------------------- forecast

def load_forecast():
    """Return (series, grid) where series is {hour: temperature_or_None}."""
    series = {}
    grid = None
    print(f"{'chunk':<26} {'rows':>7}  date range (UTC)")
    for start, end in CHUNKS:
        path = RAW / (f"openmeteo_previousruns_{MODEL}_{STATION}_"
                      f"{start}_{end}.json")
        with open(path) as f:
            d = json.load(f)
        if grid is None:
            grid = (d["latitude"], d["longitude"], d["elevation"])
        h = d["hourly"]
        times = [datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in h["time"]]
        vals = h["temperature_2m_previous_day1"]
        for t, v in zip(times, vals):
            series[t] = v
        print(f"{start}..{end:<12} {len(times):>7}  "
              f"{times[0]:%Y-%m-%d %H:%M} -> {times[-1]:%Y-%m-%d %H:%M}")
    return series, grid


def forecast_checks():
    line(f"FORECAST SERIES - Open-Meteo Previous Runs, {MODEL}, {STATION}, "
         "temperature only")
    print(f"chunk files: {len(CHUNKS)}\n")
    series, grid = load_forecast()

    print(f"\ngrid point returned : lat {grid[0]}, lon {grid[1]}, "
          f"elevation {grid[2]} m")
    print(f"session 14 (F31) got : lat {F31_GRID[0]}, lon {F31_GRID[1]}, "
          f"elevation {F31_GRID[2]} m")
    print(f"same grid point      : "
          f"{'yes' if grid == F31_GRID else 'NO - check this'}")

    exp = expected_hours(PERIOD_START, PERIOD_END)
    no_row = [h for h in exp if h not in series]
    null_val = [h for h in exp if h in series and series[h] is None]
    missing = sorted(set(no_row) | set(null_val))
    usable = len(exp) - len(missing)

    print(f"\nexpected hours in period : {len(exp):,}")
    print(f"hours with a usable value: {usable:,}")
    print(f"hours missing            : {len(missing):,} "
          f"({100 * len(missing) / len(exp):.2f}% of the period)")
    print(f"  of which no row at all : {len(no_row):,}")
    print(f"  of which row but null  : {len(null_val):,}")
    print(f"rows returned outside the period: "
          f"{len([h for h in series if not PERIOD_START <= h <= PERIOD_END]):,}")

    print("\n-- split across the fixed windows (D13) --")
    window_split(exp, missing, WINDOWS)

    runs = gap_runs(missing)
    print(f"\n-- GAP MAP: every gap run, whole period ({len(runs)} run(s)) --")
    print_runs(runs)

    print("\n-- gap runs by length --")
    size_summary(runs)

    biggest = sorted(runs, key=lambda r: -r[2])
    print("\n-- largest gap runs in order --")
    for start, end, n in biggest[:10]:
        print(f"    {n:6,} hours   {start:%Y-%m-%d %H:%M} -> "
              f"{end:%Y-%m-%d %H:%M} UTC")
    print(f"    runs of 24 hours or more: {len([r for r in runs if r[2] >= 24])}")

    gap_492_answer(runs, missing)

    print("\n-- TRAINING WINDOW ONLY: temperature value range (sanity) --")
    vals = [series[h] for h in exp
            if h <= TRAIN_END and series.get(h) is not None]
    print(f"    n = {len(vals):,}")
    print(f"    min = {min(vals)} degC   max = {max(vals)} degC   "
          f"mean = {sum(vals) / len(vals):.2f} degC")
    print("    (Celsius as expected - Kelvin would show roughly 250-310.)")
    print("\n    the extremes in context, training window only:")
    pairs = sorted(((series[h], h) for h in exp
                    if h <= TRAIN_END and series.get(h) is not None))
    for label, sel in (("coldest 3", pairs[:3]), ("warmest 3", pairs[-3:])):
        shown = ", ".join(f"{v} on {h:%Y-%m-%d %H:%M}" for v, h in sel)
        print(f"      {label}: {shown}")
    print(f"      hours at or below -25 degC: "
          f"{sum(1 for v, h in pairs if v <= -25):,}")
    print(f"      hours at or above +40 degC: "
          f"{sum(1 for v, h in pairs if v >= 40):,}")
    print("      A continental interior swings much further than either")
    print("      European airport did: EGLC -1.7 to 40.7 (F10), LFPG -8.5 to")
    print("      41.2 (F26). Nothing here is out of range for Iowa.")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, usable "
          f"{len(t_hours) - len(t_miss):,}, missing {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ")

    return series, missing


def gap_492_answer(runs, missing):
    """Does DSM's forecast series carry the 492-hour gap F8 and F22 found?"""
    print("\n-- THE 492-HOUR GAP: DOES DSM HAVE IT? (explicit answer) --")
    print(f"    EGLC (F8) and LFPG (F22) both have exactly one gap:")
    print(f"      {SHARED_GAP_START:%Y-%m-%d %H:%M} -> "
          f"{SHARED_GAP_END:%Y-%m-%d %H:%M} UTC, {SHARED_GAP_HOURS} hours")

    if not runs:
        print("\n    DSM: NONE. Every hour of the period carries a forecast "
              "value.")
        print("    ANSWER: none - DSM does NOT share the gap.")
        return

    big = [r for r in runs if r[2] >= 24]
    print(f"\n    DSM: {len(runs)} gap run(s), {len(missing):,} missing hours "
          f"in total,")
    print(f"    of which {len(big)} run(s) of a day or more.")

    matched = False
    for start, end, n in big:
        before = start - timedelta(hours=1)
        after = end + timedelta(hours=1)
        print()
        print(f"    last hour with data       : {before:%Y-%m-%d %H:%M} UTC")
        print(f"    first missing hour        : {start:%Y-%m-%d %H:%M} UTC")
        print(f"    last missing hour         : {end:%Y-%m-%d %H:%M} UTC")
        print(f"    first hour with data again: {after:%Y-%m-%d %H:%M} UTC")
        print(f"    length                    : {n:,} hours "
              f"({n / 24:.1f} days)")
        in_train = PERIOD_START <= start and end <= TRAIN_END
        print(f"    falls entirely in training: "
              f"{'yes' if in_train else 'NO - it touches the test window'}")

        same = (start == SHARED_GAP_START and end == SHARED_GAP_END
                and n == SHARED_GAP_HOURS)
        matched = matched or same
        print(f"    matches the EGLC/LFPG gap : "
              f"{'YES - same start, same end, same length' if same else 'no'}")
        if not same:
            print(f"      EGLC/LFPG: {SHARED_GAP_START:%Y-%m-%d %H:%M} -> "
                  f"{SHARED_GAP_END:%Y-%m-%d %H:%M} UTC, "
                  f"{SHARED_GAP_HOURS} hours")
            print(f"      DSM      : {start:%Y-%m-%d %H:%M} -> "
                  f"{end:%Y-%m-%d %H:%M} UTC, {n} hours")

    print(f"\n    ANSWER: {'SAME WINDOW - DSM has the identical gap' if matched else 'DIFFERENT - see the runs above'}")


# --------------------------------------------------------------------- obs

def load_obs():
    """Return the routine reports and the hour each one pairs to under D14.

    An observation is matched to the hour it is nearest to, and only if it is
    within 15 minutes of it (D14). DSM reports at :54 (F34), so the report
    that serves hour H is stamped (H-1):54 and the pairing offset is six
    minutes.
    """
    by_hour = {}
    by_chunk_hours = []    # hours each chunk covers ON ITS OWN (for Q26)
    rows_all = []          # (timestamp, value_or_None) for every routine report
    rows_total = 0
    minute_counts = {}
    no_temp_rows = 0
    outside_15 = 0
    position = None

    print(f"{'chunk':<26} {'rows':>7}  date range (UTC)")
    for start, end in CHUNKS:
        path = RAW / f"iem_asos_{STATION}_{start}_{end}_routine.csv"
        first = last = None
        n = 0
        chunk_hours = set()
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                n += 1
                rows_total += 1
                minute_counts[t.minute] = minute_counts.get(t.minute, 0) + 1
                first = first or t
                last = t
                if position is None:
                    position = (float(r["lat"]), float(r["lon"]),
                                float(r["elevation"]))

                raw = (r.get("tmpc") or "").strip()
                val = None if raw in ("M", "", "T", "None") else float(raw)
                if val is None:
                    no_temp_rows += 1
                rows_all.append((t, val))

                nearest = nearest_hour(t)
                if abs((t - nearest).total_seconds()) > D14_TOLERANCE_MIN * 60:
                    outside_15 += 1
                    continue
                if val is not None:
                    by_hour[nearest] = val
                    chunk_hours.add(nearest)
        by_chunk_hours.append((start, end, chunk_hours))
        print(f"{start}..{end:<12} {n:>7}  "
              f"{first:%Y-%m-%d %H:%M} -> {last:%Y-%m-%d %H:%M}")

    return (by_hour, by_chunk_hours, rows_all, rows_total, minute_counts,
            no_temp_rows, outside_15, position)


def q26_boundary_check(by_hour, by_chunk_hours):
    """Q26: the :54 reporting artefact at the edge of each request window.

    A station reporting at :54 serves hour H with a report stamped (H-1):54.
    So the first hour of any request window has no report inside that window.
    Mapped chunk by chunk that shows up as six missing hours. Mapped over the
    concatenated series the neighbouring chunk supplies the report, and only
    the very first hour of the whole period is left genuinely uncovered -
    because nothing before 2021-03-24 was requested.

    Counted, named and reported. Nothing is filled (SPEC 2.2).
    """
    line("Q26 - the :54 request-boundary artefact, counted separately")
    print("DSM reports at :54, so the report serving hour H is stamped")
    print("(H-1):54. The first hour of a request window therefore needs a")
    print("report from before that window.")
    print()
    print(f"{'chunk':<26} {'first hour':<20} {'that chunk alone':<18} "
          f"{'all chunks joined'}")
    artefacts = []
    for start, end, hours in by_chunk_hours:
        first_hour = datetime.strptime(start, "%Y-%m-%d")
        alone = first_hour in hours
        joined = first_hour in by_hour
        if not alone:
            artefacts.append((first_hour, joined))
        print(f"{start}..{end:<12} {first_hour:%Y-%m-%d %H:%M}     "
              f"{'covered' if alone else 'MISSING':<18} "
              f"{'covered' if joined else 'MISSING'}")

    unclosed = [h for h, joined in artefacts if not joined]
    print(f"\n  chunk-boundary hours uncovered by their own chunk : "
          f"{len(artefacts)}")
    print(f"  of those, closed by the neighbouring chunk         : "
          f"{len(artefacts) - len(unclosed)}")
    print(f"  of those, still uncovered after joining           : "
          f"{len(unclosed)}")
    for h in unclosed:
        print(f"      {h:%Y-%m-%d %H:%M} UTC - the first hour of the whole "
              f"period;")
        print("      nothing before 2021-03-24 was requested, so no report")
        print("      exists in the data to serve it. A request-boundary")
        print("      artefact, not a hole in the station's record.")
    print("\n  These hours are counted, named and left alone. Nothing was")
    print("  filled (SPEC 2.2). None of them is a target hour: 18:00 UTC is")
    print("  served by the 17:54 report of the same day, inside the same "
          "chunk.")
    return set(h for h, _ in artefacts if not _)


def obs_checks():
    line(f"TRUTH SERIES - IEM ASOS routine METARs, {STATION}")
    print(f"chunk files: {len(CHUNKS)}\n")
    (by_hour, by_chunk_hours, rows_all, rows_total, minutes, no_temp,
     outside_15, position) = load_obs()

    print(f"\nstation position in the files: lat {position[0]}, "
          f"lon {position[1]}, elevation {position[2]} m")
    print(f"SPEC 3.4 holds (F31)         : lat {F31_STATION_POS[0]}, "
          f"lon {F31_STATION_POS[1]}")
    print("  (the CSV rounds latitude to four decimals and IEM's metadata to "
          "three,")
    print("   which is the 11 m difference session 14 already recorded.)")

    exp = expected_hours(PERIOD_START, PERIOD_END)
    print(f"\nreports in files           : {rows_total:,}")
    print("minute-past-hour spread    : "
          + ", ".join(f":{m:02d} x{c:,}" for m, c in sorted(minutes.items())))
    print(f"reports with no temperature: {no_temp:,}")
    print(f"reports >{D14_TOLERANCE_MIN} min from any hour, dropped (D14): "
          f"{outside_15:,}")

    boundary = q26_boundary_check(by_hour, by_chunk_hours)

    missing = sorted(h for h in exp if h not in by_hour)
    real_missing = [h for h in missing if h not in boundary]
    print(f"\nexpected hours in period : {len(exp):,}")
    print(f"hours with an observation: {len(exp) - len(missing):,}")
    print(f"hours missing            : {len(missing):,} "
          f"({100 * len(missing) / len(exp):.2f}% of the period)")
    print(f"  of which Q26 request-boundary artefacts: {len(boundary):,}")
    print(f"  real missing hours                     : {len(real_missing):,} "
          f"({100 * len(real_missing) / len(exp):.2f}%)")

    print("\n-- split across the fixed windows (D13) --")
    print(f"  {'window':<34} {'expected':>9} {'observed':>9} "
          f"{'real gap':>9} {'Q26':>4}")
    for label, lo, hi in WINDOWS:
        win = [h for h in exp if lo <= h <= hi]
        real = [h for h in real_missing if lo <= h <= hi]
        art = [h for h in boundary if lo <= h <= hi]
        print(f"  {label:<34} {len(win):>9,} "
              f"{len(win) - len(real) - len(art):>9,} {len(real):>9,} "
              f"{len(art):>4}")
    print("  ('observed' = expected minus real gaps minus Q26 artefacts, so")
    print("   the row adds up. The Q26 column is the request-boundary hour,")
    print("   not a hole in the station's record.)")

    runs = gap_runs(real_missing)
    print(f"\n-- GAP MAP: every real gap run, whole period ({len(runs)} run(s)) --")
    print_runs(runs, limit=60)

    print("\n-- gap runs by length --")
    size_summary(runs)

    biggest = sorted(runs, key=lambda r: -r[2])
    print("\n-- largest gap runs in order --")
    for start, end, n in biggest[:10]:
        print(f"    {n:6,} hours   {start:%Y-%m-%d %H:%M} -> "
              f"{end:%Y-%m-%d %H:%M} UTC")
    print(f"    runs of 24 hours or more: {len([r for r in runs if r[2] >= 24])}")

    print("\n-- reports carrying no temperature (marked M) --")
    blanks = [t for t, v in rows_all if v is None]
    if not blanks:
        print("    (none)")
    else:
        for t in blanks:
            print(f"    {t:%Y-%m-%d %H:%M} UTC")
        print("    Counted, never filled (SPEC 2.2).")

    print("\n-- TRAINING WINDOW ONLY: observed temperature range (sanity) --")
    vals = [by_hour[h] for h in exp if h <= TRAIN_END and h in by_hour]
    print(f"    n = {len(vals):,}")
    print(f"    min = {min(vals)} degC   max = {max(vals)} degC   "
          f"mean = {sum(vals) / len(vals):.2f} degC")
    print("    (Celsius as expected. F35 checked tmpc against the Fahrenheit")
    print("     field at DSM and the two agree to 0.0044 degC.)")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in real_missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, with an observation "
          f"{len(t_hours) - len(t_miss):,}, real gaps {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ", limit=30)

    return by_hour, rows_all


# ------------------------------- days lost at the 18:00 UTC target, by cause

def target_hour_day_loss(by_hour, series, rows_all):
    """How many days does each series cost at DSM's 18:00 UTC target?

    Observation side, each calendar day falls into exactly one bucket:
      kept           a routine report with a real temperature within 15 min of
                     18:00 UTC - at DSM that is the 17:54 report
      lost off-hour  no such report, but a routine report carrying a real
                     temperature does sit near 18:00 (within 30 minutes),
                     filed too far out for D14 to accept
      lost no temp   a report sits within 15 min of 18:00 but carries no
                     temperature (marked M)
      lost no report nothing at all near the 18:00 hour

    "Near" means the report's nearest whole hour is 18:00. That is the right
    neighbourhood for a :54 station: the 17:54 report belongs to hour 18, not
    hour 17, so grouping by clock hour the way session 10 could at LFPG would
    count the wrong reports here.

    This is a count of report timing and of forecast row presence, not of
    temperature values, so it is a structural check and safe to run across the
    test window too. Nothing is joined and nothing is filled (SPEC 2.2).
    """
    line("DAYS LOST AT THE 18:00 UTC TARGET, BY CAUSE (D33's target hour)")
    print("Structural counts only - no temperature value from the test window")
    print("is printed. The two series are NOT joined; that is the next")
    print("session's job. These counts are what that join should reconcile")
    print("against, the way session 11 reconciled CDG's join against F22/F25.")

    days = []
    cur = PERIOD_START
    while cur <= PERIOD_END:
        days.append(cur.date())
        cur += timedelta(days=1)

    # Group every routine report by the target hour it is nearest to.
    near_target = {}
    for t, v in rows_all:
        nh = nearest_hour(t)
        if nh.hour == TARGET_HOUR:
            near_target.setdefault(nh.date(), []).append((t, v))

    buckets = {"kept": [], "off-hour": [], "no temp": [], "no report": []}
    for d in days:
        target = datetime(d.year, d.month, d.day, TARGET_HOUR, 0)
        here = near_target.get(d, [])
        inside = [(t, v) for t, v in here
                  if abs((t - target).total_seconds()) <= D14_TOLERANCE_MIN * 60]
        if any(v is not None for t, v in inside):
            buckets["kept"].append(d)
        elif inside:
            buckets["no temp"].append(d)
        elif any(v is not None for t, v in here):
            buckets["off-hour"].append(d)
        else:
            buckets["no report"].append(d)

    def window_of(d):
        return "training" if datetime(d.year, d.month, d.day) <= TRAIN_END \
            else "test"

    print(f"\ncalendar days in the period : {len(days):,}")
    print("\n-- OBSERVATION SIDE --")
    print(f"{'cause':<36} {'days':>6} {'training':>9} {'test':>6}")
    order = [("kept", "kept - usable 18:00 observation"),
             ("off-hour", "LOST: only an off-hour report"),
             ("no temp", "LOST: report in place, no temperature"),
             ("no report", "LOST: no report near the 18:00 hour")]
    for key, label in order:
        sel = buckets[key]
        tr = sum(1 for d in sel if window_of(d) == "training")
        te = len(sel) - tr
        print(f"{label:<36} {len(sel):>6} {tr:>9} {te:>6}")

    obs_lost = sorted(set(days) - set(buckets["kept"]))
    print(f"\ntotal days lost at 18:00 UTC (observation side): {len(obs_lost):,}"
          f" of {len(days):,} ({100 * len(obs_lost) / len(days):.2f}%)")

    for key, label in order[1:]:
        sel = buckets[key]
        if not sel:
            continue
        print(f"\n-- {label} ({len(sel)} day(s)) --")
        for d in sel[:40]:
            here = sorted(near_target.get(d, []))
            detail = ", ".join(
                f"{t:%H:%M}{'' if v is not None else ' (no temp)'}"
                for t, v in here) or "no routine report near the 18:00 hour"
            print(f"    {d}  [{window_of(d)}]  reports: {detail}")
        if len(sel) > 40:
            print(f"    ... and {len(sel) - 40} more")

    # Forecast side.
    print("\n-- FORECAST SIDE --")
    fc_lost = []
    for d in days:
        t = datetime(d.year, d.month, d.day, TARGET_HOUR, 0)
        if series.get(t) is None:
            fc_lost.append(d)
    fc_tr = sum(1 for d in fc_lost if window_of(d) == "training")
    print(f"days with no 18:00 UTC forecast value : {len(fc_lost):,} "
          f"(training {fc_tr}, test {len(fc_lost) - fc_tr})")
    if fc_lost:
        runs = gap_runs([datetime(d.year, d.month, d.day) for d in fc_lost])
        print("  as date runs:")
        for s, e, n in runs:
            print(f"    {s:%Y-%m-%d} -> {e:%Y-%m-%d}   {n} day(s)")

    # Combined - what the join session should expect to drop.
    print("\n-- BOTH SIDES TOGETHER: what the join should expect to drop --")
    lost = sorted(set(obs_lost) | set(fc_lost))
    overlap = sorted(set(obs_lost) & set(fc_lost))
    kept = len(days) - len(lost)
    lost_tr = sum(1 for d in lost if window_of(d) == "training")
    print(f"    calendar days in the period : {len(days):,}")
    print(f"    days lost, either side      : {len(lost):,} "
          f"(training {lost_tr}, test {len(lost) - lost_tr})")
    print(f"    days lost on BOTH sides     : {len(overlap):,}")
    print(f"    paired rows expected        : {kept:,}")

    for label, lo, hi in [("inner-training 2021-03-24..2024-07-31",
                           PERIOD_START, datetime(2024, 7, 31, 23, 0)),
                          ("validation     2024-08-01..2025-07-31",
                           datetime(2024, 8, 1, 0, 0), TRAIN_END),
                          ("test           2025-08-01..2026-07-31",
                           TEST_START, PERIOD_END)]:
        win = [d for d in days if lo <= datetime(d.year, d.month, d.day) <= hi]
        wl = [d for d in lost if lo <= datetime(d.year, d.month, d.day) <= hi]
        wo = [d for d in obs_lost if lo <= datetime(d.year, d.month, d.day) <= hi]
        wf = [d for d in fc_lost if lo <= datetime(d.year, d.month, d.day) <= hi]
        print(f"    {label}: {len(win):,} days, "
              f"{len(win) - len(wl):,} expected rows, {len(wl):,} dropped "
              f"(forecast {len(wf)}, observation {len(wo)})")

    print("\n    Nothing was filled and nothing was joined (SPEC 2.2). These")
    print("    are counts of row presence and report timing only.")

    offhour_episodes(rows_all)


def offhour_episodes(rows_all):
    """Where do the off-hour reports sit? Bunched, or spread out?

    Session 14 saw not one off-hour report in five weeks of samples (F34), so
    this is the first look at DSM's whole record. It matters for reading the
    observation gap map: a stretch where a station shifts its reporting minute
    shows up as missing hours even though reports were filed, which is what
    F23 found at LFPG.
    """
    off = sorted(t for t, v in rows_all
                 if min(t.minute, 60 - t.minute) > D14_TOLERANCE_MIN)
    print("\n-- where the off-hour reports sit (are they bunched?) --")
    if not off:
        print("    none at all: every routine report in the five years sits")
        print("    within 15 minutes of a whole hour, so D14 refuses none of")
        print("    them. EGLC had 8 (F9), LFPG 97 (F23).")
        return

    by_day = {}
    for t in off:
        by_day.setdefault(t.date(), []).append(t)

    episodes = []
    for d in sorted(by_day):
        if episodes and (d - episodes[-1][-1]).days <= 2:
            episodes[-1].append(d)
        else:
            episodes.append([d])

    print(f"    off-hour reports : {len(off):,} on {len(by_day)} day(s), "
          f"in {len(episodes)} episode(s)")
    multi = [e for e in episodes if sum(len(by_day[d]) for d in e) >= 5]
    print(f"    episodes of 5 or more reports: {len(multi)}")
    for e in multi[:10]:
        n = sum(len(by_day[d]) for d in e)
        print(f"      {e[0]} .. {e[-1]}   {n} reports over {len(e)} day(s)")
    lone = sum(sum(len(by_day[d]) for d in e)
               for e in episodes if sum(len(by_day[d]) for d in e) < 5)
    singles = sum(1 for e in episodes if sum(len(by_day[d]) for d in e) < 5)
    print(f"    the remaining {lone} report(s) are scattered singles across "
          f"{singles} episode(s)")
    counts = {}
    for t in off:
        counts[t.minute] = counts.get(t.minute, 0) + 1
    print("    minute stamps across all off-hour reports: "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(counts.items())))
    print("\n    against the other two airports:")
    print(f"      EGLC   8 of 46,919 (0.017%, F9)")
    print(f"      LFPG  97 of 46,903 (0.207%, F23)")
    print(f"      DSM  {len(off):,} of {len(rows_all):,} "
          f"({100 * len(off) / len(rows_all):.3f}%)")


# ------------------------------------------------------------------- report

model_string_check()
q27_compare()
series, fc_missing = forecast_checks()
by_hour, rows_all = obs_checks()
target_hour_day_loss(by_hour, series, rows_all)

print()
print("=" * 76)
print("Nothing was joined, filled or modelled. Raw files untouched.")
print("No temperature value from the test window was printed.")
print("=" * 76)
