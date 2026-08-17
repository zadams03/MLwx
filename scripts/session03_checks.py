"""Session 03b part C: the gap map for both series.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

This counts rows and maps where the holes are. It does NOT join the two
series, and it does not build or evaluate anything.

The test window stays sealed. For 2025-08-01 onward this script reports only
*structure* - how many rows exist and where the holes are. It never prints a
value, a range or an average from the test window. Value ranges are printed
for the training window only, purely to catch something obviously wrong such
as temperatures arriving in Kelvin instead of Celsius.

Terms used here:
- "expected hour" = every hour in the period. A perfect record would have one
  usable value for each.
- "gap" = an expected hour with no usable temperature: either no row at all,
  or a row whose value is null (forecast) or marked M (observation).
- "gap run" = gap hours that sit next to each other, reported as one line so a
  long outage does not print as hundreds of separate hours.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

PERIOD_START = datetime(2021, 3, 24, 0, 0)
PERIOD_END = datetime(2026, 7, 31, 23, 0)      # inclusive, hourly

# The split fixed in DECISIONS D13 / SPEC 4.3.
TRAIN_END = datetime(2025, 7, 31, 23, 0)       # inclusive
TEST_START = datetime(2025, 8, 1, 0, 0)

CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]


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


def print_runs(runs, indent="    "):
    if not runs:
        print(f"{indent}(none)")
        return
    for start, end, n in runs:
        print(f"{indent}{start:%Y-%m-%d %H:%M} -> {end:%Y-%m-%d %H:%M} UTC   "
              f"{n:5d} hour{'s' if n != 1 else ''}")


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


# ---------------------------------------------------------------- forecast

def load_forecast():
    """Return {hour: temperature_or_None}."""
    series = {}
    print(f"{'chunk':<26} {'rows':>7}  date range (UTC)")
    for start, end in CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_EGLC_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        times = [datetime.strptime(t, "%Y-%m-%dT%H:%M") for t in h["time"]]
        vals = h["temperature_2m_previous_day1"]
        for t, v in zip(times, vals):
            series[t] = v
        print(f"{start}..{end:<12} {len(times):>7}  "
              f"{times[0]:%Y-%m-%d %H:%M} -> {times[-1]:%Y-%m-%d %H:%M}")
    return series


def forecast_checks():
    line("FORECAST SERIES - Open-Meteo Previous Runs, gfs_global, "
         "temperature only")
    print(f"chunk files: {len(CHUNKS)}\n")
    series = load_forecast()

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

    # The aborted session 03 saw 444 null hours inside the 2024 file and
    # called this an "early 2024" gap. It is really a run that starts in
    # December 2023, so it is found here by size, not by month.
    print("\n-- the big gap around the 2023/2024 boundary, pinned down --")
    big = [r for r in runs if r[2] >= 24]
    if not big:
        print("    no gap run of 24 hours or more")
    for start, end, n in big:
        before = start - timedelta(hours=1)
        after = end + timedelta(hours=1)
        in_2023 = sum(1 for h in range(n)
                      if (start + timedelta(hours=h)).year == 2023)
        print(f"    last hour with data       : {before:%Y-%m-%d %H:%M} UTC")
        print(f"    first missing hour        : {start:%Y-%m-%d %H:%M} UTC")
        print(f"    last missing hour         : {end:%Y-%m-%d %H:%M} UTC")
        print(f"    first hour with data again: {after:%Y-%m-%d %H:%M} UTC")
        print(f"    length                    : {n:,} hours "
              f"({n / 24:.1f} days)")
        print(f"    split across the year end : {in_2023:,} hours in 2023, "
              f"{n - in_2023:,} hours in 2024")
        print("    (the 2024-only count of 444 seen in the aborted session 03")
        print("     was this same gap, counted from 1 January only.)")

    biggest = sorted(runs, key=lambda r: -r[2])
    print("\n-- is it the only sizeable gap? largest runs in order --")
    for start, end, n in biggest[:10]:
        print(f"    {n:6,} hours   {start:%Y-%m-%d %H:%M} -> "
              f"{end:%Y-%m-%d %H:%M} UTC")
    over_24 = [r for r in runs if r[2] >= 24]
    print(f"    runs of 24 hours or more: {len(over_24)}")

    print("\n-- TRAINING WINDOW ONLY: temperature value range (sanity) --")
    vals = [series[h] for h in exp
            if h <= TRAIN_END and series.get(h) is not None]
    print(f"    n = {len(vals):,}")
    print(f"    min = {min(vals)} degC   max = {max(vals)} degC   "
          f"mean = {sum(vals) / len(vals):.2f} degC")
    print("    (Celsius as expected - Kelvin would show roughly 250-310.)")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, usable "
          f"{len(t_hours) - len(t_miss):,}, missing {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ")


# --------------------------------------------------------------------- obs

def load_obs():
    """Return {hour: temperature} using the routine :50 report (D14).

    An observation is matched to the hour it is nearest to, and only if it is
    within 15 minutes of it (D14). In practice EGLC's :50 report belongs to
    the hour ten minutes after it.
    """
    by_hour = {}
    rows_total = 0
    minute_counts = {}
    no_temp_rows = 0
    outside_15 = 0

    print(f"{'chunk':<26} {'rows':>7}  date range (UTC)")
    for start, end in CHUNKS:
        path = RAW / f"iem_asos_EGLC_{start}_{end}_routine.csv"
        first = last = None
        n = 0
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                n += 1
                rows_total += 1
                minute_counts[t.minute] = minute_counts.get(t.minute, 0) + 1
                first = first or t
                last = t

                raw = (r.get("tmpc") or "").strip()
                val = None if raw in ("M", "", "T", "None") else float(raw)
                if val is None:
                    no_temp_rows += 1

                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15 += 1
                    continue
                if val is not None:
                    by_hour[nearest] = val
        print(f"{start}..{end:<12} {n:>7}  "
              f"{first:%Y-%m-%d %H:%M} -> {last:%Y-%m-%d %H:%M}")

    return by_hour, rows_total, minute_counts, no_temp_rows, outside_15


def obs_checks():
    line("TRUTH SERIES - IEM ASOS routine METARs, EGLC")
    print(f"chunk files: {len(CHUNKS)}\n")
    by_hour, rows_total, minutes, no_temp, outside_15 = load_obs()

    exp = expected_hours(PERIOD_START, PERIOD_END)
    print(f"\nreports in files           : {rows_total:,}")
    print("minute-past-hour spread    : "
          + ", ".join(f":{m:02d} x{c:,}" for m, c in sorted(minutes.items())))
    print(f"reports with no temperature: {no_temp:,}")
    print(f"reports >15 min from any hour, dropped (D14): {outside_15:,}")

    missing = sorted(h for h in exp if h not in by_hour)
    print(f"\nexpected hours in period : {len(exp):,}")
    print(f"hours with an observation: {len(exp) - len(missing):,}")
    print(f"hours missing            : {len(missing):,} "
          f"({100 * len(missing) / len(exp):.2f}% of the period)")

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

    print("\n-- TRAINING WINDOW ONLY: observed temperature range (sanity) --")
    vals = [by_hour[h] for h in exp if h <= TRAIN_END and h in by_hour]
    print(f"    n = {len(vals):,}")
    print(f"    min = {min(vals)} degC   max = {max(vals)} degC   "
          f"mean = {sum(vals) / len(vals):.2f} degC")
    print("    (Celsius as expected.)")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, with an observation "
          f"{len(t_hours) - len(t_miss):,}, missing {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ")


forecast_checks()
obs_checks()
print()
print("=" * 76)
print("Nothing was joined, filled or modelled. Raw files untouched.")
print("=" * 76)
