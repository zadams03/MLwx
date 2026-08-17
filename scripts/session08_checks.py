"""Session 08 checks: verify-on-contact for CDG / LFPG (Paris Charles de Gaulle).

This is the Stage 2 opening check. It mirrors what session 01 did for EGLC:
confirm both data sources carry the new airport and are usable, BEFORE any
full pull, SPEC design or modelling.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files them at :50 past
  each hour. What LFPG does is the main unknown this session answers, because
  the pairing rule D14 was written around EGLC's :50 habit.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. At EGLC it turned out to be a second scheduled
  report at :20 (DECISIONS F3), so it is worth looking at here too.
- "expected hours" = one observation for every hour in the window, which is
  what a perfect record would look like.

Nothing here builds, trains, joins or evaluates anything (session 08 scope).
"""

import csv
import json
import math
from datetime import datetime, timedelta
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

# The authoritative station position, taken from IEM's own station metadata
# for the FR__ASOS network (saved beside the data as
# iem_station_metadata_FR__ASOS.geojson). The session prompt quoted roughly
# 49.010 N / 2.548 E / 119 m from elsewhere; IEM's own record is used instead
# and the difference is reported below.
LFPG_LAT = 49.0153
LFPG_LON = 2.5344
LFPG_ELEV_M = 109.0

# EGLC's numbers, for side-by-side comparison only (DECISIONS Q5, F6).
EGLC_LAT, EGLC_LON, EGLC_ELEV_M = 51.5053, 0.0553, 5.0
EGLC_GRID_LAT, EGLC_GRID_LON, EGLC_GRID_ELEV_M = 51.487137, 0.0, 4.0

# D14's tolerance: a report more than this many minutes from the hour is
# dropped, never shifted or filled.
D14_TOLERANCE_MIN = 15


def line(title):
    print()
    print("=" * 74)
    print(title)
    print("=" * 74)


def km_between(lat1, lon1, lat2, lon2):
    """Great-circle distance in km. Plain haversine, earth radius 6371 km."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------------------------------------------------------------- forecast --

def read_forecast(path):
    with open(path) as f:
        d = json.load(f)
    h = d["hourly"]
    return d, h["time"], h["temperature_2m_previous_day1"]


def forecast_shape(path, show_grid=True):
    d, times, vals = read_forecast(path)
    n = len(times)
    present = sum(v is not None for v in vals)
    print(f"file            : {path.name}")
    print(f"requested point : lat {LFPG_LAT}, lon {LFPG_LON} (LFPG, from IEM metadata)")
    if show_grid:
        glat, glon, gelev = d["latitude"], d["longitude"], d["elevation"]
        dist = km_between(LFPG_LAT, LFPG_LON, glat, glon)
        print(f"model grid point: lat {glat}, lon {glon}, elevation {gelev} m")
        print(f"grid point is   : {dist:.2f} km from the airport")
        print(f"height mismatch : grid {gelev} m vs station {LFPG_ELEV_M} m "
              f"-> {gelev - LFPG_ELEV_M:+.1f} m")
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
    else:
        print("value range     : n/a - every value came back null")
        print("first non-null  : none in this window")
    return n, present


# ------------------------------------------------------------ observations --

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


def station_position(path):
    """The lat/lon/elevation IEM puts in the file itself."""
    with open(path) as f:
        first = next(csv.DictReader(f))
    return float(first["lat"]), float(first["lon"]), float(first["elevation"])


def minutes_from_nearest_hour(t):
    """How far this report sits from the nearest whole hour, in minutes."""
    return min(t.minute, 60 - t.minute)


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
    else:
        print("missing hours    : none")
    if rows:
        temps = [v for _, v in rows if v is not None]
        print(f"temperature range: {min(temps)} to {max(temps)} degC "
              f"(plainly Celsius, not Kelvin)")
    return len(expected), len(gaps)


def timing_check(path):
    """The CDG-specific unknown: does D14's pairing rule apply as it stands?

    D14 says: pair each HH:00 forecast with the nearest report, and drop the
    hour if no report falls within 15 minutes of it. That rule was written for
    a station that reports at :50. This checks what it does at LFPG.
    """
    rows, _ = read_obs(path)
    offsets = {}
    for t, _ in rows:
        off = minutes_from_nearest_hour(t)
        offsets[off] = offsets.get(off, 0) + 1

    inside = sum(c for o, c in offsets.items() if o <= D14_TOLERANCE_MIN)
    outside = sum(c for o, c in offsets.items() if o > D14_TOLERANCE_MIN)

    print(f"file                          : {path.name}")
    print(f"reports                       : {len(rows)}")
    print("distance from the nearest hour:")
    for off, count in sorted(offsets.items()):
        print(f"  {off:2d} min  x{count}")
    print(f"within D14's {D14_TOLERANCE_MIN}-minute window : {inside}")
    print(f"outside it, so D14 drops them : {outside}")

    # What the pairing would actually look like at the stage 1 target hour.
    noon = [(t, v) for t, v in rows if t.hour == 12]
    exact_noon = [t for t, _ in noon if t.minute == 0]
    print()
    print(f"reports in the 12:00 UTC hour : {len(noon)}")
    print(f"  of those, stamped exactly 12:00 : {len(exact_noon)}")

    # Every report that is not exactly on the hour, named individually, so the
    # exceptions are facts rather than a count.
    odd = sorted(t for t, _ in rows if t.minute != 0)
    if odd:
        print(f"reports NOT stamped on the hour: {len(odd)}")
        if len(odd) <= 12:
            for t in odd:
                keep = "kept by D14" if minutes_from_nearest_hour(t) <= D14_TOLERANCE_MIN \
                    else "DROPPED by D14"
                print(f"  {t:%Y-%m-%d %H:%M} UTC  ({keep})")
        else:
            print(f"  too many to list one by one ({len(odd)}); see the minute "
                  f"histogram above")
    return offsets, inside, outside


def noon_availability(path, start_day, end_day):
    """Count, day by day, whether D14 could pair an observation to 12:00 UTC.

    This is an observation-side gap count only (SPEC 2.2). Nothing is joined to
    a forecast and nothing is modelled - that is not this session's job.
    """
    rows, _ = read_obs(path)
    by_day = {}
    for t, v in rows:
        if v is None:
            continue
        target = t.replace(hour=12, minute=0)
        off = abs((t - target).total_seconds()) / 60.0
        if off <= D14_TOLERANCE_MIN:
            day = t.date()
            # D14 pairs with the NEAREST report inside the window.
            if day not in by_day or off < by_day[day][0]:
                by_day[day] = (off, t, v)

    days = []
    cur = start_day
    while cur < end_day:
        days.append(cur.date())
        cur += timedelta(days=1)

    kept = [d for d in days if d in by_day]
    dropped = [d for d in days if d not in by_day]

    print(f"file                : {path.name}")
    print(f"calendar days       : {len(days)}")
    print(f"days with a usable 12:00 UTC observation under D14 : {len(kept)}")
    print(f"days D14 would drop and count                      : {len(dropped)}")
    for d in dropped:
        near = [t for t, v in rows if t.date() == d and t.hour == 12 and v is not None]
        detail = ", ".join(f"{t:%H:%M}" for t in near) or "no report in the 12:00 hour"
        print(f"  {d}  (reports in the 12:00 hour: {detail})")
    if kept:
        offs = [by_day[d][0] for d in kept]
        print(f"pairing offset      : min {min(offs):.0f} min, max {max(offs):.0f} min, "
              f"mean {sum(offs) / len(offs):.1f} min")
        print("  (EGLC's equivalent under D14 is a steady 10 minutes, because it "
              "reports at :50)")
    return len(days), len(kept), len(dropped)


# ------------------------------------------------------------------- report --

line("PART 0 - the station position used, and how it compares with EGLC")
print("LFPG position, from IEM's own FR__ASOS station metadata (authoritative):")
print(f"  lat {LFPG_LAT}, lon {LFPG_LON}, elevation {LFPG_ELEV_M} m")
print()
print("The session prompt quoted approx 49.010 N, 2.548 E, ~119 m. IEM's own")
print("record differs slightly and is what was used for the forecast pull:")
print(f"  latitude   IEM {LFPG_LAT} vs prompt 49.010  -> "
      f"{(LFPG_LAT - 49.010) * 111.32:+.2f} km north/south")
print(f"  longitude  IEM {LFPG_LON} vs prompt 2.548   -> "
      f"{(LFPG_LON - 2.548) * 111.32 * math.cos(math.radians(LFPG_LAT)):+.2f} km east/west")
print(f"  elevation  IEM {LFPG_ELEV_M} m vs prompt 119 m -> "
      f"{LFPG_ELEV_M - 119:+.1f} m")
print(f"  the two positions are {km_between(LFPG_LAT, LFPG_LON, 49.010, 2.548):.2f} km apart")
print()
print("Side by side with stage 1's airport:")
print(f"  EGLC  lat {EGLC_LAT}, lon {EGLC_LON}, elevation {EGLC_ELEV_M} m")
print(f"  LFPG  lat {LFPG_LAT}, lon {LFPG_LON}, elevation {LFPG_ELEV_M} m")
print(f"  distance apart : {km_between(EGLC_LAT, EGLC_LON, LFPG_LAT, LFPG_LON):.0f} km")
print(f"  height apart   : {LFPG_ELEV_M - EGLC_ELEV_M:+.0f} m")

line("PART A1 - forecast sample, recent period (Open-Meteo Previous Runs, gfs_global)")
forecast_shape(RAW / "openmeteo_previousruns_gfs_global_LFPG_2026-07-01_2026-07-21.json")
print()
print("For comparison, EGLC's grid point (DECISIONS Q5):")
print(f"  lat {EGLC_GRID_LAT}, lon {EGLC_GRID_LON}, elevation {EGLC_GRID_ELEV_M} m")
print(f"  {km_between(EGLC_LAT, EGLC_LON, EGLC_GRID_LAT, EGLC_GRID_LON):.2f} km from the airport, "
      f"{EGLC_GRID_ELEV_M - EGLC_ELEV_M:+.1f} m height mismatch")

line("PART A2 - does the forecast archive reach back to March 2021 for LFPG?")
print("-- probe 1: 1-7 March 2021, before EGLC's first hour (F1 found all nulls there) --")
forecast_shape(RAW / "openmeteo_previousruns_gfs_global_LFPG_2021-03-01_2021-03-07.json",
               show_grid=False)
print()
print("-- probe 2: 18-26 March 2021, straddling EGLC's 24 March 2021 start --")
forecast_shape(RAW / "openmeteo_previousruns_gfs_global_LFPG_2021-03-18_2021-03-26.json",
               show_grid=False)

line("PART B1 - truth sample, same recent period (IEM ASOS LFPG, routine METARs)")
lat, lon, elev = station_position(RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine.csv")
print(f"station position in the file : lat {lat}, lon {lon}, elevation {elev} m")
print(f"matches the metadata used    : "
      f"{'yes' if (lat, lon) == (LFPG_LAT, LFPG_LON) else 'NO - check this'}")
print()
obs_gaps(
    RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine.csv",
    datetime(2026, 7, 1), datetime(2026, 7, 22),
)

line("PART B2 - THE KEY CDG UNKNOWN: what minute does LFPG report at?")
print("Recent sample, routine reports only:")
print()
timing_check(RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine.csv")

line("PART B2b - what D14 would do at the stage 1 target hour, 12:00 UTC")
print("Recent sample, routine reports only. Observation side only - nothing is")
print("joined to a forecast here and nothing is modelled.")
print()
noon_availability(RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine.csv",
                  datetime(2026, 7, 1), datetime(2026, 7, 22))
print()
print("Early sample, routine reports only:")
print()
noon_availability(RAW / "iem_asos_LFPG_2021-03-18_2021-04-01_routine.csv",
                  datetime(2021, 3, 18), datetime(2021, 4, 1))

line("PART B3 - truth sample, early period (IEM ASOS LFPG, routine METARs)")
obs_gaps(
    RAW / "iem_asos_LFPG_2021-03-18_2021-04-01_routine.csv",
    datetime(2021, 3, 18), datetime(2021, 4, 1),
)
print()
print("Is the reporting minute the same five years earlier?")
print()
timing_check(RAW / "iem_asos_LFPG_2021-03-18_2021-04-01_routine.csv")

line("PART B4 - side file: the same recent period including special (SPECI) reports")
print("At EGLC the 'special' reports turned out to be a second scheduled report")
print("at :20 (F3). This checks whether LFPG does anything similar.")
print()
obs_gaps(
    RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine-and-special.csv",
    datetime(2026, 7, 1), datetime(2026, 7, 22),
)
print()
timing_check(RAW / "iem_asos_LFPG_2026-07-01_2026-07-22_routine-and-special.csv")
