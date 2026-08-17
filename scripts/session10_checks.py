"""Session 10 part C: the gap map for both LFPG series.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

This is session 03b's gap map, pointed at the stage 2 airport. It counts rows
and maps where the holes are. It does NOT join the two series, and it does not
build or evaluate anything.

The test window stays sealed. For 2025-08-01 onward this script reports only
*structure* - how many rows exist, where the holes are, and how many days a
rule would drop. It never prints a temperature value, a range or an average
from the test window. Value ranges are printed for the training window only,
purely to catch something obviously wrong such as temperatures arriving in
Kelvin instead of Celsius.

On top of session 03b's checks, this script answers three open questions:
- Q20: confirm every forecast chunk was pulled with the `gfs_global` string,
  read back out of the saved provenance files rather than claimed.
- Q21: does LFPG's forecast series have a gap, and does it match the one F8
  found at EGLC (2023-12-30 00:00 to 2024-01-19 11:00 UTC)?
- Q22: which IEM network does EGLC actually sit in? SPEC 3.4 carries
  `GB__ASOS` marked unverified.

And it produces the count DECISIONS D30 asked for: how many days are lost at
12:00 UTC because LFPG filed its routine report off the hour, reported
separately from days lost to a report that was never filed at all.

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

STATION = "LFPG"
MODEL = "gfs_global"

PERIOD_START = datetime(2021, 3, 24, 0, 0)
PERIOD_END = datetime(2026, 7, 31, 23, 0)      # inclusive, hourly

# The split fixed in DECISIONS D13 / SPEC 4.3. Shared by every airport.
TRAIN_END = datetime(2025, 7, 31, 23, 0)       # inclusive
TEST_START = datetime(2025, 8, 1, 0, 0)

# The stage 1 and stage 2 target hour (SPEC 4.1).
TARGET_HOUR = 12

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

# The gap DECISIONS F8 mapped at EGLC, for Q21 to compare against.
EGLC_GAP_START = datetime(2023, 12, 30, 0, 0)
EGLC_GAP_END = datetime(2024, 1, 19, 11, 0)
EGLC_GAP_HOURS = 492


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


# --------------------------------------------------------- Q20: the string

def q20_model_string_check():
    """Read the model string back out of the saved provenance files.

    D16 pins `gfs_global`. Session 10's pull script sets it in one constant, so
    this is not proof against a bug in that script - but it is proof about what
    was actually requested, because the .meta.txt files record the exact URL
    that went to the API (SPEC 2.3).
    """
    line("Q20 - was every forecast chunk pulled with gfs_global? (D16)")
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
    print("  Nothing looked wrong, so gfs_seamless was not re-probed at LFPG")
    print("  (session prompt A-1: this is a confirmation, not a reopening).")


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
    print("session 08 (F17) got : lat 49.027008, lon 2.578125, elevation 109.0 m")
    print(f"same grid point      : "
          f"{'yes' if grid == (49.027008, 2.578125, 109.0) else 'NO - check this'}")

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

    q21_answer(runs, missing)

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


def q21_answer(runs, missing):
    """Q21: does LFPG have a forecast gap, and is it EGLC's gap?"""
    print("\n-- Q21: DOES THE LFPG FORECAST SERIES HAVE A GAP? --")
    if not runs:
        print("    NO. Every hour of the period carries a forecast value.")
        return

    big = [r for r in runs if r[2] >= 24]
    print(f"    YES. {len(runs)} gap run(s), {len(missing):,} missing hours in "
          f"total,")
    print(f"    of which {len(big)} run(s) of a day or more.")

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

        same = (start == EGLC_GAP_START and end == EGLC_GAP_END
                and n == EGLC_GAP_HOURS)
        print(f"    matches EGLC's F8 gap     : "
              f"{'YES - same start, same end, same length' if same else 'no'}")
        if not same:
            print(f"      EGLC (F8): {EGLC_GAP_START:%Y-%m-%d %H:%M} -> "
                  f"{EGLC_GAP_END:%Y-%m-%d %H:%M} UTC, {EGLC_GAP_HOURS} hours")
            print(f"      LFPG     : {start:%Y-%m-%d %H:%M} -> "
                  f"{end:%Y-%m-%d %H:%M} UTC, {n} hours")


# --------------------------------------------------------------------- obs

def load_obs():
    """Return the routine reports and the hour each one pairs to under D14.

    An observation is matched to the hour it is nearest to, and only if it is
    within 15 minutes of it (D14). LFPG reports on the hour (F18), so in
    practice the pairing offset is zero.
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

                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if abs((t - nearest).total_seconds()) > D14_TOLERANCE_MIN * 60:
                    outside_15 += 1
                    continue
                if val is not None:
                    by_hour[nearest] = val
        print(f"{start}..{end:<12} {n:>7}  "
              f"{first:%Y-%m-%d %H:%M} -> {last:%Y-%m-%d %H:%M}")

    return (by_hour, rows_all, rows_total, minute_counts, no_temp_rows,
            outside_15, position)


def obs_checks():
    line(f"TRUTH SERIES - IEM ASOS routine METARs, {STATION}")
    print(f"chunk files: {len(CHUNKS)}\n")
    (by_hour, rows_all, rows_total, minutes, no_temp, outside_15,
     position) = load_obs()

    print(f"\nstation position in the files: lat {position[0]}, "
          f"lon {position[1]}, elevation {position[2]} m")
    print(f"matches SPEC 3.4 (F17)       : "
          f"{'yes' if (position[0], position[1]) == (49.0153, 2.5344) else 'NO'}")

    exp = expected_hours(PERIOD_START, PERIOD_END)
    print(f"\nreports in files           : {rows_total:,}")
    print("minute-past-hour spread    : "
          + ", ".join(f":{m:02d} x{c:,}" for m, c in sorted(minutes.items())))
    print(f"reports with no temperature: {no_temp:,}")
    print(f"reports >{D14_TOLERANCE_MIN} min from any hour, dropped (D14): "
          f"{outside_15:,}")

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

    return rows_all


# ------------------------------------------- D30: the off-hour day-loss count

def offhour_noon_count(rows_all):
    """Days lost at 12:00 UTC to off-hour reporting, counted separately.

    DECISIONS D30 decided what to do about LFPG's off-hour routine reports -
    nothing, take the drops - but required the pull session to count them, and
    to keep them apart from days lost because no report was filed at all.

    Observation side only. Nothing is joined to a forecast (session scope).
    This is a count of report timing, not of temperature values, so it is a
    structural check and safe to run across the test window too.

    Each calendar day falls into exactly one bucket:
      kept              a routine report with a real temperature within 15 min
                        of 12:00 UTC
      lost off-hour     no such report, but there IS a routine report with a
                        real temperature elsewhere in the 12:00 hour, filed
                        too far from the hour for D14 to accept
      lost no temp      a report sits within 15 min of 12:00 but carries no
                        temperature (marked M)
      lost no report    nothing at all in the 12:00 hour
    """
    line("D30 - DAYS LOST AT 12:00 UTC, BY CAUSE (observation side only)")
    print("Counting report timing, not temperature values, so this covers the")
    print("whole period including the sealed test window. Nothing is joined")
    print("and nothing is filled (SPEC 2.2).")

    # Group every routine report by the calendar day of its 12:00 hour.
    noon_rows = {}
    for t, v in rows_all:
        if t.hour == TARGET_HOUR:
            noon_rows.setdefault(t.date(), []).append((t, v))

    days = []
    cur = PERIOD_START
    while cur <= PERIOD_END:
        days.append(cur.date())
        cur += timedelta(days=1)

    buckets = {"kept": [], "off-hour": [], "no temp": [], "no report": []}
    for d in days:
        target = datetime(d.year, d.month, d.day, TARGET_HOUR, 0)
        here = noon_rows.get(d, [])
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
    print(f"{'cause':<34} {'days':>6} {'training':>9} {'test':>6}")
    order = [("kept", "kept - usable 12:00 observation"),
             ("off-hour", "LOST: only an off-hour report"),
             ("no temp", "LOST: report on the hour, no temp"),
             ("no report", "LOST: no report in the 12:00 hour")]
    for key, label in order:
        sel = buckets[key]
        tr = sum(1 for d in sel if window_of(d) == "training")
        te = len(sel) - tr
        print(f"{label:<34} {len(sel):>6} {tr:>9} {te:>6}")

    lost = len(days) - len(buckets["kept"])
    print(f"\ntotal days lost at 12:00 UTC (observation side): {lost:,} of "
          f"{len(days):,} ({100 * lost / len(days):.2f}%)")
    print("of those, lost specifically to CDG's off-hour reporting (D30): "
          f"{len(buckets['off-hour']):,}")

    for key, label in order[1:]:
        sel = buckets[key]
        if not sel:
            continue
        print(f"\n-- {label} ({len(sel)} day(s)) --")
        for d in sel:
            here = sorted(noon_rows.get(d, []))
            detail = ", ".join(
                f"{t:%H:%M}{'' if v is not None else ' (no temp)'}"
                for t, v in here) or "no routine report in the 12:00 hour"
            print(f"    {d}  [{window_of(d)}]  reports: {detail}")

    offhour_episodes(rows_all)

    print("\n-- how this compares with EGLC (stage 1) --")
    print("    EGLC lost NO days at 12:00 UTC to off-hour reporting across")
    print("    training and validation (F18, reading F12). Its whole-period")
    print("    off-hour rate was 8 reports in 46,919 (0.017%, F9).")
    off_reports = sum(1 for t, v in rows_all
                      if min(t.minute, 60 - t.minute) > D14_TOLERANCE_MIN)
    print(f"    LFPG whole-period off-hour reports: {off_reports:,} of "
          f"{len(rows_all):,} "
          f"({100 * off_reports / len(rows_all):.3f}%)")
    print("    F18 estimated ~12 days lost at noon, from a three-week sample.")
    print(f"    The real figure is {len(buckets['off-hour']):,}.")


def offhour_episodes(rows_all):
    """Where do the off-hour reports sit? Bunched, or spread out?

    F18 saw 3 off-hour reports in three weeks and could not tell bad luck from
    a midday pattern. Over five years the shape is visible, and it matters for
    reading the observation gap map: a stretch where the station shifts to :30
    shows up as missing hours even though reports were filed.
    """
    off = sorted(t for t, v in rows_all
                 if min(t.minute, 60 - t.minute) > D14_TOLERANCE_MIN)
    by_day = {}
    for t in off:
        by_day.setdefault(t.date(), []).append(t)

    # Group days that sit within a day of each other into one episode.
    episodes = []
    for d in sorted(by_day):
        if episodes and (d - episodes[-1][-1]).days <= 2:
            episodes[-1].append(d)
        else:
            episodes.append([d])

    print("\n-- where the off-hour reports sit (are they bunched?) --")
    print(f"    off-hour reports : {len(off):,} on {len(by_day)} day(s), "
          f"in {len(episodes)} episode(s)")
    multi = [e for e in episodes if sum(len(by_day[d]) for d in e) >= 5]
    print(f"    episodes of 5 or more reports: {len(multi)}")
    for e in multi:
        n = sum(len(by_day[d]) for d in e)
        print(f"      {e[0]} .. {e[-1]}   {n} reports over {len(e)} day(s)")
        for d in e:
            stamps = ", ".join(f"{t:%H:%M}" for t in by_day[d])
            print(f"        {d}  x{len(by_day[d])}  {stamps}")
    singles = sum(1 for e in episodes if sum(len(by_day[d]) for d in e) < 5)
    lone = sum(sum(len(by_day[d]) for d in e)
               for e in episodes if sum(len(by_day[d]) for d in e) < 5)
    print(f"    the remaining {lone} report(s) are scattered singles across "
          f"{singles} episode(s)")
    print("    minute stamps across all off-hour reports: "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(
              {t.minute: sum(1 for x in off if x.minute == t.minute)
               for t in off}.items())))


# ------------------------------------------------------------ Q22: networks

def q22_network_check():
    """Q22: which IEM network is EGLC in? Read from IEM's own listing."""
    line("Q22 - EGLC's IEM network code, from IEM's own station listing")

    for network, station in (("GB__ASOS", "EGLC"), ("FR__ASOS", "LFPG")):
        path = RAW / f"iem_station_metadata_{network}.geojson"
        with open(path) as f:
            d = json.load(f)
        feats = d["features"]
        hit = [x for x in feats if x["properties"]["sid"] == station]
        print(f"\nfile     : {path.name}")
        print(f"stations : {len(feats):,} in the {network} network")
        if not hit:
            print(f"  {station} is NOT in this network - SPEC 3.4 is wrong")
            continue
        p = hit[0]["properties"]
        lon, lat = hit[0]["geometry"]["coordinates"]
        print(f"  {station} found:")
        print(f"    sid           = {p['sid']}")
        print(f"    sname         = {p['sname']}")
        print(f"    network       = {p['network']}")
        print(f"    coordinates   = lat {lat}, lon {lon}")
        print(f"    elevation     = {p['elevation']} m")
        print(f"    tzname        = {p['tzname']}")
        print(f"    archive_begin = {p['archive_begin']}")
        print(f"    archive_end   = {p['archive_end']}")
        print(f"    online        = {p['online']}")

    print("\n-- against what SPEC 3.4 holds --")
    print("    EGLC network  SPEC says GB__ASOS (unverified); IEM says "
          "GB__ASOS  -> CONFIRMED")
    print("    EGLC position SPEC says 51.5053 / 0.0553 / 5 m; IEM agrees")
    print("    LFPG network  SPEC says FR__ASOS (verified in session 08); "
          "IEM agrees")


# ------------------------------------------------------------------- report

q20_model_string_check()
forecast_checks()
rows_all = obs_checks()
offhour_noon_count(rows_all)
q22_network_check()

print()
print("=" * 76)
print("Nothing was joined, filled or modelled. Raw files untouched.")
print("No temperature value from the test window was printed.")
print("=" * 76)
