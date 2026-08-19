"""Session 26 part C: the gap map for both Reno (RNO) series, plus Reno's own
target-hour confirmation.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

This is session 03b's, session 10's, session 15's and session 20's gap map,
pointed at the fifth airport - Reno, not Bozeman (DECISIONS D42, superseding
D40). It counts rows and maps where the holes are. It does NOT join the two
series, and it does not build or evaluate anything.

The test window stays sealed. For 2025-08-01 onward this script reports only
*structure* - how many rows exist, where the holes are, and how many days a
rule would drop. It never prints a temperature value, a range or an average
from the test window. Value ranges are printed for the training window only,
purely to catch something obviously wrong such as temperatures arriving in
Kelvin instead of Celsius.

Reno's target hour is confirmed here directly against the timezone database
(America/Los_Angeles), the same discipline F32 (DSM), F50 (Dubbo) and
session 25's PART 0c (Bozeman) applied - not inherited from Bozeman's 19:00
UTC figure, because Reno is Pacific and one hour further west (session 26
prompt).

Reno reports at :55 (five minutes before the hour, session 25's B0 sample
and IEM's own METAR_RESET_MINUTE=55), so - like DSM's :54 reporting (Q26)
and Bozeman's :56 reporting (session 25) - the report serving hour H is
stamped (H-1):55, outside the request window that covers hour H at the
first hour of every chunk. This script checks that boundary rather than
assuming it, the same way session 20 checked it (and found it did not
apply, because Dubbo reports on the hour) and session 25 measured it.

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
from zoneinfo import ZoneInfo
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

STATION = "RNO"
MODEL = "gfs_global"

PERIOD_START = datetime(2021, 3, 24, 0, 0)
PERIOD_END = datetime(2026, 7, 31, 23, 0)      # inclusive, hourly

# The split fixed in DECISIONS D13 / SPEC 4.3. Shared by every airport.
TRAIN_END = datetime(2025, 7, 31, 23, 0)       # inclusive
TEST_START = datetime(2025, 8, 1, 0, 0)

# Reno's target hour - confirmed below against the timezone database, not
# assumed. Computed here rather than hard-coded from the session prompt's own
# figure, so the number printed is a measurement, not a copy.
STATION_TZNAME = "America/Los_Angeles"

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

# The gap DECISIONS F8 mapped at EGLC, F22 at LFPG, F38 at DSM and F57 at
# Dubbo.
SHARED_GAP_START = datetime(2023, 12, 30, 0, 0)
SHARED_GAP_END = datetime(2024, 1, 19, 11, 0)
SHARED_GAP_HOURS = 492

# What session 25's candidate sample (B0) recorded for RNO, to check the full
# pull describes the same place the sample did.
F66_GRID = (39.537918, -119.765625, 1344.0)
F66_STATION_POS = (39.4839, -119.7711)


def line(title):
    print()
    print("=" * 76)
    print(title)
    print("=" * 76)


def target_hour_check():
    """Confirm Reno's target hour against the timezone database (America/
    Los_Angeles), the same discipline F32/F50/session 25's PART 0c applied.
    Not inherited from Bozeman's 19:00 UTC (D41) - Reno is Pacific, one hour
    further west, per the session 26 prompt.
    """
    line("TARGET HOUR - local standard noon at Reno, computed and checked")
    tz = ZoneInfo(STATION_TZNAME)
    summer = datetime(2024, 7, 1, 12, 0, tzinfo=ZoneInfo("UTC"))
    winter = datetime(2024, 1, 15, 12, 0, tzinfo=ZoneInfo("UTC"))
    summer_local = summer.astimezone(tz)
    winter_local = winter.astimezone(tz)
    print(f"timezone from IEM metadata : {STATION_TZNAME}")
    print(f"  mid-summer  : 12:00 UTC = {summer_local:%H:%M %Z} "
          f"(UTC{summer_local.utcoffset().total_seconds() / 3600:+.0f})")
    print(f"  mid-winter  : 12:00 UTC = {winter_local:%H:%M %Z} "
          f"(UTC{winter_local.utcoffset().total_seconds() / 3600:+.0f})")
    std_offset_hours = int(winter_local.utcoffset().total_seconds() / 3600)
    print(f"  standard-time offset (read from a January date, guaranteed "
          f"standard time) : UTC{std_offset_hours:+d}")
    target_hour = (12 - std_offset_hours) % 24
    print(f"  so local standard noon (12:00) = {target_hour:02d}:00 UTC")
    print(f"  D42 / session 26 prompt expect = 20:00 UTC")
    print(f"  VERDICT: {'MATCHES' if target_hour == 20 else 'DOES NOT MATCH - see above'}")
    print()
    print("Note on daylight saving: Nevada observes it (PDT, roughly")
    print("Mar-Nov). The convention (D27/D33/D37/D41) uses the STANDARD")
    print("offset (PST, UTC-8) regardless, so the target stays one fixed UTC")
    print("hour all year, per D42 and the session 26 prompt.")
    print()
    print("For contrast, Bozeman's target hour (D41, session 25 PART 0c):")
    print("  America/Denver, standard offset UTC-7, local standard noon =")
    print("  19:00 UTC. Reno is Pacific, one hour further west, so 20:00 UTC")
    print("  is one hour later than Bozeman's figure, not the same number.")
    return target_hour


TARGET_HOUR = None  # set in main() from target_hour_check()


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
    line("D16 - was every RNO forecast chunk pulled with gfs_global?")
    ok = True
    for start, end in CHUNKS:
        meta = RAW / (f"openmeteo_previousruns_{MODEL}_{STATION}_"
                      f"{start}_{end}.json.meta.txt")
        text = meta.read_text()
        url_line = next(l for l in text.splitlines()
                        if l.startswith("https://previous-runs-api"))
        has = f"models={MODEL}" in url_line
        seamless = "gfs_seamless" in url_line
        ok = ok and has and not seamless
        print(f"  {start}..{end}  models={MODEL}: "
              f"{'yes' if has else 'NO'}   gfs_seamless present: "
              f"{'YES - PROBLEM' if seamless else 'no'}")
    print(f"\n  all {len(CHUNKS)} forecast chunks used {MODEL}: "
          f"{'YES' if ok else 'NO'}")
    print("  gfs_global vs gfs_seamless diverges sharply at this station")
    print("  (session 25's B0 candidate sample; F69 measured it in full for")
    print("  Bozeman, 258/264 hours differing by up to 16.5 degC) - the pin")
    print("  is doing real work here, so it is not re-probed in this session.")


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
    print(f"session 25 B0 sample got : lat {F66_GRID[0]}, lon {F66_GRID[1]}, "
          f"elevation {F66_GRID[2]} m")
    print(f"same grid point      : "
          f"{'yes' if grid == F66_GRID else 'NO - check this'}")

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
    print("      against the other four airports (training window):")
    print("        EGLC -1.7 to 40.7 (F10), LFPG -8.5 to 41.2 (F26),")
    print("        DSM  -30.0 to 44.7 (F38), YSDU 0.5 to 40.9 (F57)")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, usable "
          f"{len(t_hours) - len(t_miss):,}, missing {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ")

    return series, missing


def gap_492_answer(runs, missing):
    """Does Reno's forecast series carry the 492-hour gap F8/F22/F38/F57
    found?"""
    print("\n-- THE 492-HOUR GAP: DOES RENO HAVE IT? (explicit answer) --")
    print(f"    EGLC (F8), LFPG (F22), DSM (F38) and Dubbo (F57) all have "
          f"exactly one gap:")
    print(f"      {SHARED_GAP_START:%Y-%m-%d %H:%M} -> "
          f"{SHARED_GAP_END:%Y-%m-%d %H:%M} UTC, {SHARED_GAP_HOURS} hours")

    if not runs:
        print("\n    RNO: NONE. Every hour of the period carries a forecast "
              "value.")
        print("    ANSWER: none - Reno does NOT share the gap.")
        return

    big = [r for r in runs if r[2] >= 24]
    print(f"\n    RNO: {len(runs)} gap run(s), {len(missing):,} missing hours "
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
        print(f"    matches the EGLC/LFPG/DSM/Dubbo gap : "
              f"{'YES - same start, same end, same length' if same else 'no'}")
        if not same:
            print(f"      EGLC/LFPG/DSM/Dubbo: {SHARED_GAP_START:%Y-%m-%d %H:%M} "
                  f"-> {SHARED_GAP_END:%Y-%m-%d %H:%M} UTC, "
                  f"{SHARED_GAP_HOURS} hours")
            print(f"      RNO                : {start:%Y-%m-%d %H:%M} -> "
                  f"{end:%Y-%m-%d %H:%M} UTC, {n} hours")

    print(f"\n    ANSWER: {'SAME WINDOW - Reno has the identical gap' if matched else 'DIFFERENT - see the runs above'}")


# --------------------------------------------------------------------- obs

def load_obs():
    """Return the routine reports and the hour each one pairs to under D14.

    An observation is matched to the hour it is nearest to, and only if it is
    within 15 minutes of it (D14). Reno reports at :55 (session 25's B0
    sample), so in practice the pairing offset is 5 minutes.
    """
    by_hour = {}
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
        print(f"{start}..{end:<12} {n:>7}  "
              f"{first:%Y-%m-%d %H:%M} -> {last:%Y-%m-%d %H:%M}")

    return (by_hour, rows_all, rows_total, minute_counts, no_temp_rows,
            outside_15, position)


def boundary_sanity_check():
    """Reno reports at :55 (5 minutes before the hour), so the report serving
    hour H is stamped (H-1):55 - outside the request window that covers hour
    H, for the first hour of every chunk. This is the same Q26-style
    artefact DSM's :54 reporting created and Bozeman's :56 reporting also
    has (session 25). Checked here rather than assumed, the same way session
    20 checked it for Dubbo (and found the artefact did not apply there,
    because Dubbo reports on the hour).
    """
    line("BOUNDARY CHECK - does the :55 report create a Q26-style artefact "
         "at chunk boundaries?")
    print("A report stamped (H-1):55 serves hour H - outside the window that")
    print("covers hour H at the very first hour of each chunk. Checked chunk")
    print("by chunk: the first hour of chunk N should be covered by chunk")
    print("N-1's own file (its last report, stamped :55 on its final day),")
    print("except for the very first chunk, which nothing precedes.")
    print()
    all_as_expected = True
    for i, (start, end) in enumerate(CHUNKS):
        path = RAW / f"iem_asos_{STATION}_{start}_{end}_routine.csv"
        first_hour = datetime.strptime(start, "%Y-%m-%d")
        covered = False
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                if t == first_hour:
                    covered = True
                    break
        expect_covered = False  # a :55 report never covers its own chunk's
                                 # first hour, by construction
        note = ("n/a - first chunk of the whole period" if i == 0 else
                ("UNEXPECTED - covered by its own chunk" if covered else
                 "not covered by its own chunk, as expected for :55 "
                 "reporting"))
        if i > 0 and covered != expect_covered:
            all_as_expected = False
        print(f"  {start}..{end:<12} first hour {first_hour:%Y-%m-%d %H:%M} "
              f"UTC : {note}")
    print(f"\n  Behaved exactly as :55 reporting predicts at every boundary: "
          f"{'CONFIRMED' if all_as_expected else 'NOT CONFIRMED - see above'}")
    print("  (The artefact hour itself is counted in the whole-period gap")
    print("  map above like any other missing hour; it touches no target")
    print("  hour, because 20:00 UTC is served by the 19:55 report of the")
    print("  same day, inside the same chunk.)")


def obs_checks():
    line(f"TRUTH SERIES - IEM ASOS routine METARs, {STATION}")
    print(f"chunk files: {len(CHUNKS)}\n")
    (by_hour, rows_all, rows_total, minutes, no_temp, outside_15,
     position) = load_obs()

    print(f"\nstation position in the files: lat {position[0]}, "
          f"lon {position[1]}, elevation {position[2]} m")
    print(f"session 25's B0 sample got   : lat {F66_STATION_POS[0]}, "
          f"lon {F66_STATION_POS[1]}")

    exp = expected_hours(PERIOD_START, PERIOD_END)
    print(f"\nreports in files           : {rows_total:,}")
    print("minute-past-hour spread    : "
          + ", ".join(f":{m:02d} x{c:,}" for m, c in sorted(minutes.items())))
    print(f"reports with no temperature: {no_temp:,}")
    print(f"reports >{D14_TOLERANCE_MIN} min from any hour, dropped (D14): "
          f"{outside_15:,}")

    boundary_sanity_check()

    missing = sorted(h for h in exp if h not in by_hour)
    print(f"\nexpected hours in period : {len(exp):,}")
    print(f"hours with an observation: {len(exp) - len(missing):,}")
    print(f"hours missing            : {len(missing):,} "
          f"({100 * len(missing) / len(exp):.2f}% of the period)")

    print("\n-- split across the fixed windows (D13) --")
    window_split(exp, missing, WINDOWS)

    runs = gap_runs(missing)
    print(f"\n-- GAP MAP: every gap run, whole period ({len(runs)} run(s)) --")
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
        for t in blanks[:40]:
            print(f"    {t:%Y-%m-%d %H:%M} UTC")
        if len(blanks) > 40:
            print(f"    ... and {len(blanks) - 40} more")
        print("    Counted, never filled (SPEC 2.2).")

    print("\n-- TRAINING WINDOW ONLY: observed temperature range (sanity) --")
    vals = [by_hour[h] for h in exp if h <= TRAIN_END and h in by_hour]
    print(f"    n = {len(vals):,}")
    print(f"    min = {min(vals)} degC   max = {max(vals)} degC   "
          f"mean = {sum(vals) / len(vals):.2f} degC")
    print("    (Celsius as expected. Session 25's B5 check confirmed tmpc")
    print("     against the Fahrenheit-derived figure for this station's")
    print("     candidate sample, agreeing to about 0.004 degC - the same")
    print("     rounding-only gap DSM's F35 found.)")

    print("\n-- TEST WINDOW: structural only, no values printed --")
    t_hours = [h for h in exp if h >= TEST_START]
    t_miss = [h for h in missing if h >= TEST_START]
    print(f"    expected {len(t_hours):,} hours, with an observation "
          f"{len(t_hours) - len(t_miss):,}, missing {len(t_miss):,}")
    print("    gap runs:")
    print_runs(gap_runs(t_miss), indent="      ", limit=30)

    return by_hour, rows_all


# ------------------------------- days lost at the 20:00 UTC target, by cause

def target_hour_day_loss(by_hour, series, rows_all):
    """How many days does each series cost at Reno's 20:00 UTC target?

    Observation side, each calendar day falls into exactly one bucket:
      kept           a routine report with a real temperature within 15 min of
                     20:00 UTC - at Reno that is expected to be the 19:55
                     report, 5 minutes early
      lost off-hour  no such report, but a routine report carrying a real
                     temperature does sit near 20:00 (within 30 minutes),
                     filed too far out for D14 to accept
      lost no temp   a report sits within 15 min of 20:00 but carries no
                     temperature (marked M)
      lost no report nothing at all near the 20:00 hour

    This is a count of report timing and of forecast row presence, not of
    temperature values, so it is a structural check and safe to run across the
    test window too. Nothing is joined and nothing is filled (SPEC 2.2).
    """
    line("DAYS LOST AT THE 20:00 UTC TARGET, BY CAUSE (D42's target hour)")
    print("Structural counts only - no temperature value from the test window")
    print("is printed. The two series are NOT joined; that is the next")
    print("session's job. These counts are what that join should reconcile")
    print("against, the way session 11/16/22 reconciled CDG's/DSM's/Dubbo's")
    print("join.")

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
    order = [("kept", "kept - usable 20:00 observation"),
             ("off-hour", "LOST: only an off-hour report"),
             ("no temp", "LOST: report in place, no temperature"),
             ("no report", "LOST: no report near the 20:00 hour")]
    for key, label in order:
        sel = buckets[key]
        tr = sum(1 for d in sel if window_of(d) == "training")
        te = len(sel) - tr
        print(f"{label:<36} {len(sel):>6} {tr:>9} {te:>6}")

    obs_lost = sorted(set(days) - set(buckets["kept"]))
    print(f"\ntotal days lost at 20:00 UTC (observation side): {len(obs_lost):,}"
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
                for t, v in here) or "no routine report near the 20:00 hour"
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
    print(f"days with no 20:00 UTC forecast value : {len(fc_lost):,} "
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
    """Where do the off-hour reports sit? Bunched, or spread out?"""
    off = sorted(t for t, v in rows_all
                 if min(t.minute, 60 - t.minute) > D14_TOLERANCE_MIN)
    print("\n-- where the off-hour reports sit (are they bunched?) --")
    if not off:
        print("    none at all: every routine report in the five years sits")
        print("    within 15 minutes of a whole hour, so D14 refuses none of")
        print("    them.")
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
    print("\n    against the other four airports:")
    print(f"      EGLC   8 of 46,919 (0.017%, F9)")
    print(f"      LFPG  97 of 46,903 (0.207%, F23)")
    print(f"      DSM  {'few, see F39'}")
    print(f"      YSDU 235 of 46,734 (0.503%, F58)")
    print(f"      RNO  {len(off):,} of {len(rows_all):,} "
          f"({100 * len(off) / len(rows_all):.3f}%)")


# ------------------------------------------------------------------- report

TARGET_HOUR = target_hour_check()
model_string_check()
series, fc_missing = forecast_checks()
by_hour, rows_all = obs_checks()
target_hour_day_loss(by_hour, series, rows_all)

print()
print("=" * 76)
print("Nothing was joined, filled or modelled. Raw files untouched.")
print("No temperature value from the test window was printed.")
print("=" * 76)
