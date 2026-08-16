"""Session 01 checks: shape of the two raw samples, and the gap count for EGLC.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

Terms used here:
- "routine METAR" = the scheduled hourly airport report. EGLC files them at
  :50 past each hour.
- IEM's "special" (SPECI) report type. Normally this means an extra
  unscheduled report filed when the weather changes fast. At EGLC it turns
  out to be a second regular report at :20 past every hour (see the side-file
  output at the bottom: exactly one per hour, never missing). So EGLC really
  reports twice an hour. This session counts only the :50 routine report as
  the hourly observation.
- "expected hours" = one observation for every hour in the window, which is
  what a perfect record would look like.
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"


def line(title):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)


def read_forecast(path):
    with open(path) as f:
        d = json.load(f)
    h = d["hourly"]
    return d, h["time"], h["temperature_2m_previous_day1"]


def forecast_shape(path):
    d, times, vals = read_forecast(path)
    n = len(times)
    present = sum(v is not None for v in vals)
    print(f"file            : {path.name}")
    print(f"requested point : lat 51.505, lon 0.055 (EGLC)")
    print(f"model grid point: lat {d['latitude']}, lon {d['longitude']}, "
          f"elevation {d['elevation']} m")
    print(f"columns         : time, temperature_2m_previous_day1 "
          f"({d['hourly_units']['temperature_2m_previous_day1']})")
    print(f"rows            : {n}")
    print(f"date range (UTC): {times[0]} -> {times[-1]}")
    print(f"values present  : {present}   missing (null): {n - present}")
    if present:
        got = [v for v in vals if v is not None]
        print(f"value range     : {min(got)} to {max(got)} degC")
        first = next(i for i, v in enumerate(vals) if v is not None)
        print(f"first non-null  : {times[first]}")
    return n, present


def read_obs(path):
    """Return (rows, missing_temp_count). One row per report."""
    rows = []
    missing_temp = 0
    with open(path) as f:
        for r in csv.DictReader(f):
            t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
            v = r["tmpc"]
            if v in ("M", "", "T"):
                missing_temp += 1
                rows.append((t, None))
            else:
                rows.append((t, float(v)))
    return rows, missing_temp


def obs_gaps(path, start, end):
    """start/end are UTC datetimes; end is exclusive."""
    rows, missing_temp = read_obs(path)
    minutes = {}
    for t, _ in rows:
        minutes[t.minute] = minutes.get(t.minute, 0) + 1

    # An hour counts as covered only if it has a report with a real temperature.
    covered = {t.replace(minute=0) for t, v in rows if v is not None}

    expected = []
    cur = start
    while cur < end:
        expected.append(cur)
        cur += timedelta(hours=1)

    gaps = [h for h in expected if h not in covered]

    print(f"file             : {path.name}")
    print(f"window (UTC)     : {start} -> {end} (end exclusive)")
    print(f"reports in file  : {len(rows)}")
    print(f"minute-past-hour : "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(minutes.items())))
    print(f"rows with no temp: {missing_temp}")
    print(f"expected hours   : {len(expected)}")
    print(f"hours covered    : {len(covered & set(expected))}")
    print(f"hours MISSING    : {len(gaps)}   "
          f"({100 * len(gaps) / len(expected):.2f}% of the window)")
    if gaps:
        print("missing hours    :")
        for h in gaps:
            print(f"  {h:%Y-%m-%d %H:%M} UTC")
    return len(expected), len(gaps)


line("STEP 2 - forecast sample, recent period (Open-Meteo Previous Runs, GFS)")
forecast_shape(RAW / "openmeteo_previousruns_gfs_EGLC_2026-07-01_2026-07-21.json")

line("STEP 3 / Q1 - forecast archive at the early date (March 2021)")
forecast_shape(RAW / "openmeteo_previousruns_gfs_EGLC_2021-03-01_2021-03-07.json")
print()
print("-- boundary probe --")
forecast_shape(RAW / "openmeteo_previousruns_gfs_EGLC_2021-03-18_2021-03-26.json")

line("STEP 4 / Q2 - truth sample, same recent period (IEM ASOS, routine METARs)")
obs_gaps(
    RAW / "iem_asos_EGLC_2026-07-01_2026-07-22_routine.csv",
    datetime(2026, 7, 1), datetime(2026, 7, 22),
)

line("STEP 5 / Q2 - truth sample, early period (IEM ASOS, routine METARs)")
obs_gaps(
    RAW / "iem_asos_EGLC_2021-03-18_2021-04-01_routine.csv",
    datetime(2021, 3, 18), datetime(2021, 4, 1),
)

line("SIDE FILE - same recent period including special (SPECI) reports")
obs_gaps(
    RAW / "iem_asos_EGLC_2026-07-01_2026-07-22_routine-and-special.csv",
    datetime(2026, 7, 1), datetime(2026, 7, 22),
)
