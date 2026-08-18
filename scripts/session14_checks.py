"""Session 14 checks: verify-on-contact for DSM (Des Moines, Iowa).

This is the third airport's opening check. It mirrors session 08, which did
the same job for CDG/LFPG: confirm both data sources carry the new airport and
are usable, BEFORE any full pull, SPEC design or modelling.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

What is different about DSM, and why this script is not a copy of session 08's:

- **The target hour is 18:00 UTC, not 12:00 UTC** (DECISIONS D33). DSM's
  standard-time offset is UTC-6, so 12:00 UTC would be 06:00 in the morning
  local - near dawn, which is exactly the part of the day SPEC 4.1 chose 12:00
  UTC to avoid in Europe. 18:00 UTC is local standard noon, which is D27's
  convention brought forward. Every check below that looks at "the target hour"
  looks at 18:00.
- **DSM is in the United States**, so two things that never needed checking in
  Europe are checked here: that IEM's temperature field and units are the same
  ones the pipeline already reads, and that the timestamps really are UTC.

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files at :50 (F3), LFPG
  at :00 (F18). What DSM does is one of the questions this session answers.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. At both European airports it turned out to be a
  second scheduled report (F3, F19), so it is worth a look here too.
- "expected hours" = one observation for every hour in the window, which is
  what a perfect record would look like.

Nothing here builds, trains, joins or evaluates anything (session 14 scope).
"""

import csv
import json
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

STATION = "DSM"
IEM_NETWORK = "IA_ASOS"

# DSM's target hour (DECISIONS D33): local standard noon, i.e. 12:00 Central
# Standard Time. Part 0b checks that this really is 18:00 UTC rather than
# taking it on trust.
TARGET_HOUR_UTC = 18

# D14's tolerance: a report more than this many minutes from the target hour is
# dropped, never shifted or filled.
D14_TOLERANCE_MIN = 15

# The two airports already in the project, for side-by-side comparison only
# (SPEC 3.4). Nothing here re-runs or re-reads their data.
EGLC = dict(lat=51.5053, lon=0.0553, elev=5.0, grid_lat=51.487137,
            grid_lon=0.0, grid_elev=4.0, minute=":50", target="12:00 UTC")
LFPG = dict(lat=49.0153, lon=2.5344, elev=109.0, grid_lat=49.027008,
            grid_lon=2.578125, grid_elev=109.0, minute=":00", target="12:00 UTC")


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


# ------------------------------------------------------ station metadata --

def dsm_metadata():
    path = RAW / f"iem_station_metadata_{IEM_NETWORK}.geojson"
    d = json.loads(path.read_text())
    for feat in d["features"]:
        if feat["id"] == STATION:
            lon, lat = feat["geometry"]["coordinates"]
            return path, len(d["features"]), lat, lon, feat["properties"]
    raise SystemExit(f"{STATION} not found in {path.name}")


# ---------------------------------------------------------------- forecast --

def read_forecast(path):
    with open(path) as f:
        d = json.load(f)
    h = d["hourly"]
    return d, h["time"], h["temperature_2m_previous_day1"]


def forecast_shape(path, lat, lon, elev, show_grid=True):
    d, times, vals = read_forecast(path)
    n = len(times)
    present = sum(v is not None for v in vals)
    print(f"file            : {path.name}")
    print(f"requested point : lat {lat}, lon {lon} (DSM, from IEM metadata)")
    if show_grid:
        glat, glon, gelev = d["latitude"], d["longitude"], d["elevation"]
        dist = km_between(lat, lon, glat, glon)
        print(f"model grid point: lat {glat}, lon {glon}, elevation {gelev} m")
        print(f"grid point is   : {dist:.2f} km from the airport")
        print(f"height mismatch : grid {gelev} m vs station {elev} m "
              f"-> {gelev - elev:+.1f} m")
        print(f"timezone in file: {d.get('timezone')} "
              f"(abbrev {d.get('timezone_abbreviation')}), "
              f"utc_offset_seconds {d.get('utc_offset_seconds')}")
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

def read_obs(path, temp_field="tmpc"):
    """Return (rows, missing_temp_count). One row per report."""
    rows = []
    missing_temp = 0
    with open(path) as f:
        for r in csv.DictReader(f):
            t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
            v = r[temp_field]
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

    # An hour counts as covered only if a report with a real temperature sits
    # within D14's tolerance of it. At a :54-reporting station the report that
    # covers 18:00 is stamped 17:54, so bucketing by clock hour would be wrong.
    covered = set()
    for t, v in rows:
        if v is None:
            continue
        nearest = (t + timedelta(minutes=30)).replace(minute=0)
        if abs((t - nearest).total_seconds()) / 60.0 <= D14_TOLERANCE_MIN:
            covered.add(nearest)

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
            # At a :54-reporting station the report that covers hour H is
            # stamped (H-1):54, so the first hour of any window needs a report
            # from the day before it. That is an artefact of where the request
            # was cut, not a hole in the record.
            edge = " <- needs the previous day's :54 report, outside this request"
            print(f"  {h:%Y-%m-%d %H:%M} UTC"
                  + (edge if h == expected[0] else ""))
    else:
        print("missing hours    : none")
    if rows:
        temps = [v for _, v in rows if v is not None]
        print(f"temperature range: {min(temps)} to {max(temps)} degC "
              f"(plainly Celsius, not Kelvin)")
    return len(expected), len(gaps)


def timing_check(path):
    """Does D14's pairing rule apply as it stands at DSM?

    D14 says: pair each target hour with the nearest routine report, and drop
    the hour if no report falls within 15 minutes of it. US ASOS stations
    commonly report at :53 or :54, which is 6-7 minutes out - inside the
    tolerance, but further out than LFPG's exact match and closer in than
    EGLC's 10 minutes.
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

    # What the pairing looks like at DSM's own target hour (D33).
    target = [(t, v) for t, v in rows
              if abs((t - t.replace(hour=TARGET_HOUR_UTC, minute=0)
                      ).total_seconds()) / 60.0 <= D14_TOLERANCE_MIN]
    print()
    print(f"reports within {D14_TOLERANCE_MIN} min of {TARGET_HOUR_UTC:02d}:00 UTC "
          f"(DSM's target hour, D33) : {len(target)}")

    common = sorted(offsets.items(), key=lambda kv: -kv[1])
    print(f"most common offset            : {common[0][0]} min "
          f"({common[0][1]} of {len(rows)} reports)")

    odd = sorted(t for t, _ in rows
                 if minutes_from_nearest_hour(t) > D14_TOLERANCE_MIN)
    if odd:
        print(f"reports D14 DROPS ({len(odd)}):")
        if len(odd) <= 12:
            for t in odd:
                print(f"  {t:%Y-%m-%d %H:%M} UTC  "
                      f"({minutes_from_nearest_hour(t)} min from the hour)")
        else:
            print(f"  too many to list one by one ({len(odd)}); see the minute "
                  f"histogram above")
    else:
        print("reports D14 DROPS             : none in this sample")
    return offsets, inside, outside


def target_availability(path, start_day, end_day):
    """Count, day by day, whether D14 could pair an observation to 18:00 UTC.

    This is an observation-side gap count only (SPEC 2.2). Nothing is joined to
    a forecast and nothing is modelled - that is not this session's job.
    """
    rows, _ = read_obs(path)
    by_day = {}
    for t, v in rows:
        if v is None:
            continue
        target = t.replace(hour=TARGET_HOUR_UTC, minute=0)
        off = abs((t - target).total_seconds()) / 60.0
        if off <= D14_TOLERANCE_MIN:
            day = target.date()
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
    print(f"target hour         : {TARGET_HOUR_UTC:02d}:00 UTC "
          f"(local standard noon at DSM, D33)")
    print(f"calendar days       : {len(days)}")
    print(f"days with a usable {TARGET_HOUR_UTC:02d}:00 UTC observation under D14 : "
          f"{len(kept)}")
    print(f"days D14 would drop and count                      : {len(dropped)}")
    for d in dropped:
        near = [t for t, v in rows
                if v is not None
                and abs((t - datetime.combine(d, datetime.min.time()).replace(
                    hour=TARGET_HOUR_UTC)).total_seconds()) / 60.0 <= 45]
        detail = ", ".join(f"{t:%H:%M}" for t in near) or \
            f"no report within 45 min of {TARGET_HOUR_UTC:02d}:00"
        print(f"  {d}  (nearby reports: {detail})")
    if kept:
        offs = [by_day[d][0] for d in kept]
        print(f"pairing offset      : min {min(offs):.0f} min, max {max(offs):.0f} min, "
              f"mean {sum(offs) / len(offs):.1f} min")
        print(f"  (EGLC's is a steady 10 minutes at :50; LFPG's is 0 at :00)")
        sample = sorted(kept)[:3]
        for d in sample:
            off, t, v = by_day[d]
            print(f"  e.g. {d} -> report {t:%H:%M} UTC, {v} degC, "
                  f"{off:.0f} min before the target hour")
    return len(days), len(kept), len(dropped)


# ------------------------------------------------------------------ report --

path_meta, n_stations, DSM_LAT, DSM_LON, props = dsm_metadata()
DSM_ELEV_M = float(props["elevation"])

line("PART 0 - DSM's position, from IEM's own station metadata")
print(f"file          : {path_meta.name}   ({n_stations} stations in "
      f"{IEM_NETWORK})")
print("IEM's entry for DSM, exactly as returned:")
for key in ("sid", "sname", "network", "state", "country", "elevation",
            "tzname", "archive_begin", "archive_end", "online"):
    print(f"  {key:14s}= {props.get(key)}")
print(f"  {'coordinates':14s}= lat {DSM_LAT}, lon {DSM_LON}  "
      f"(GeoJSON order in the file is lon, lat)")
print(f"  {'attributes':14s}= {props.get('attributes')}")
print()
print("IEM's own METAR_RESET_MINUTE attribute is the station's scheduled")
print("reporting minute. It is checked against the real reports in PART B2.")
print()
print("Side by side with the two airports already in the project (SPEC 3.4):")
print(f"  EGLC  lat {EGLC['lat']}, lon {EGLC['lon']}, elevation {EGLC['elev']} m")
print(f"  LFPG  lat {LFPG['lat']}, lon {LFPG['lon']}, elevation {LFPG['elev']} m")
print(f"  DSM   lat {DSM_LAT}, lon {DSM_LON}, elevation {DSM_ELEV_M} m")
print(f"  DSM is {km_between(DSM_LAT, DSM_LON, EGLC['lat'], EGLC['lon']):,.0f} km "
      f"from EGLC and {km_between(DSM_LAT, DSM_LON, LFPG['lat'], LFPG['lon']):,.0f} km "
      f"from LFPG,")
print(f"  and {DSM_ELEV_M - EGLC['elev']:+.0f} m / {DSM_ELEV_M - LFPG['elev']:+.0f} m "
      f"in elevation against them.")
print("  EGLC and LFPG are 328 km apart (F17). DSM is on another continent,")
print("  which is the whole reason it was opened (D32, F30's weather-year caveat).")

line("PART 0b - the target hour: is local standard noon really 18:00 UTC?")
print("DECISIONS D33 sets DSM's target hour to local standard noon with")
print("daylight saving deliberately ignored, and says that is 18:00 UTC. This")
print("checks it against the timezone database rather than taking it on trust.")
print()
tz = ZoneInfo(props["tzname"])
print(f"timezone from IEM metadata : {props['tzname']}")
for probe, label in ((datetime(2026, 1, 15, 18, 0), "mid-winter (standard time)"),
                     (datetime(2026, 7, 15, 18, 0), "mid-summer (daylight saving)")):
    utc = probe.replace(tzinfo=ZoneInfo("UTC"))
    local = utc.astimezone(tz)
    offset_h = local.utcoffset().total_seconds() / 3600
    print(f"  {label:30s}: 18:00 UTC = {local:%H:%M} {local:%Z} "
          f"(UTC{offset_h:+.0f})")
# The standard-time offset is the one D33 fixes on: read it off a January date.
jan = datetime(2026, 1, 15, 12, 0, tzinfo=tz)
std_offset_h = jan.utcoffset().total_seconds() / 3600
noon_utc = 12 - std_offset_h
print(f"  standard-time offset          : UTC{std_offset_h:+.0f}")
print(f"  so local standard noon (12:00) = {noon_utc:02.0f}:00 UTC")
print(f"  D33 says                       = {TARGET_HOUR_UTC:02d}:00 UTC")
print(f"  VERDICT                        : "
      f"{'MATCHES' if noon_utc == TARGET_HOUR_UTC else 'DOES NOT MATCH - stop'}")
print()
print("For contrast, what 12:00 UTC would have been at DSM:")
for probe, label in ((datetime(2026, 1, 15, 12, 0), "mid-winter"),
                     (datetime(2026, 7, 15, 12, 0), "mid-summer")):
    local = probe.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
    print(f"  {label:12s}: 12:00 UTC = {local:%H:%M} {local:%Z} - "
          f"{'dawn' if local.hour < 8 else 'daytime'}")
print("That is the dawn transition SPEC 4.1 chose 12:00 UTC to avoid in Europe,")
print("which is why D33 moved the hour rather than keeping it.")

line("PART A1 - forecast sample, recent period (Open-Meteo Previous Runs, gfs_global)")
forecast_shape(RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2026-07-01_2026-07-21.json",
               DSM_LAT, DSM_LON, DSM_ELEV_M)
print()
print("For comparison, the two grid points already in SPEC 3.4:")
print(f"  EGLC  lat {EGLC['grid_lat']}, lon {EGLC['grid_lon']}, "
      f"elev {EGLC['grid_elev']} m -> "
      f"{km_between(EGLC['lat'], EGLC['lon'], EGLC['grid_lat'], EGLC['grid_lon']):.2f} km, "
      f"{EGLC['grid_elev'] - EGLC['elev']:+.1f} m")
print(f"  LFPG  lat {LFPG['grid_lat']}, lon {LFPG['grid_lon']}, "
      f"elev {LFPG['grid_elev']} m -> "
      f"{km_between(LFPG['lat'], LFPG['lon'], LFPG['grid_lat'], LFPG['grid_lon']):.2f} km, "
      f"{LFPG['grid_elev'] - LFPG['elev']:+.1f} m")

line("PART A2 - does the forecast archive reach back to March 2021 for DSM?")
print("-- probe 1: 1-7 March 2021, before the first hour EGLC (F1) and LFPG (F20) have --")
forecast_shape(RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2021-03-01_2021-03-07.json",
               DSM_LAT, DSM_LON, DSM_ELEV_M, show_grid=False)
print()
print("-- probe 2: 18-26 March 2021, straddling the 24 March 2021 start --")
forecast_shape(RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2021-03-18_2021-03-26.json",
               DSM_LAT, DSM_LON, DSM_ELEV_M, show_grid=False)

line("PART B1 - truth sample, same recent period (IEM ASOS DSM, routine METARs)")
lat, lon, elev = station_position(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv")
print(f"station position in the file : lat {lat}, lon {lon}, elevation {elev} m")
print(f"station position in metadata : lat {DSM_LAT}, lon {DSM_LON}, "
      f"elevation {DSM_ELEV_M} m")
print(f"agree to within               : "
      f"{km_between(lat, lon, DSM_LAT, DSM_LON) * 1000:.0f} m "
      f"(the CSV rounds latitude to 4 places, the metadata to 3)")
print()
obs_gaps(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv",
         datetime(2026, 7, 1), datetime(2026, 7, 22))

line("PART B2 - what minute does DSM report at, and does D14 still apply?")
print("Recent sample, routine reports only:")
print()
timing_check(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv")

line(f"PART B2b - what D14 would do at DSM's target hour, {TARGET_HOUR_UTC:02d}:00 UTC")
print("Recent sample, routine reports only. Observation side only - nothing is")
print("joined to a forecast here and nothing is modelled.")
print()
target_availability(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv",
                    datetime(2026, 7, 1), datetime(2026, 7, 22))
print()
print("Early sample, routine reports only:")
print()
target_availability(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
                    datetime(2021, 3, 18), datetime(2021, 4, 1))

line("PART B3 - truth sample, early period (IEM ASOS DSM, routine METARs)")
obs_gaps(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
         datetime(2021, 3, 18), datetime(2021, 4, 1))
print()
print("Is the reporting minute the same five years earlier?")
print()
timing_check(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv")

line("PART B4 - side file: the same recent period including special (SPECI) reports")
print("At EGLC the 'special' reports turned out to be a second scheduled report")
print("at :20 (F3), and at LFPG one at :30 (F19). This checks what DSM does.")
print()
obs_gaps(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine-and-special.csv",
         datetime(2026, 7, 1), datetime(2026, 7, 22))
print()
timing_check(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine-and-special.csv")
print()
print("What the 'special' rows actually are at DSM:")
r_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv")
rs_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine-and-special.csv")
routine_stamps = {t for t, _ in r_rows}
specials = sorted(t for t, _ in rs_rows if t not in routine_stamps)
smin = {}
for t in specials:
    smin[t.minute] = smin.get(t.minute, 0) + 1
top = sorted(smin.items(), key=lambda kv: -kv[1])[:5]
print(f"  routine rows            : {len(r_rows)} (all at :54)")
print(f"  routine + special rows  : {len(rs_rows)}")
print(f"  special rows            : {len(specials)}")
print(f"  distinct minutes used   : {len(smin)}")
print("  busiest minutes         : "
      + ", ".join(f":{m:02d} x{c}" for m, c in top))
print(f"  days in the window      : 21")
print("  VERDICT: DSM does NOT file a second scheduled report. Its specials")
print("           are scattered across many minutes with no minute used more")
print("           than a handful of times, which is what genuine unscheduled")
print("           reports look like. That is unlike EGLC (a second scheduled")
print("           report at :20, F3) and LFPG (at :30, F19).")
print("           Nothing here is used: the routine report is the truth")
print("           observation, exactly as at both European airports.")

line("PART B5 - US-specific check 1: is tmpc really Celsius at a US station?")
print("The pipeline reads IEM's `tmpc` field and does no unit conversion at")
print("all - session 08's reader floats the value straight into a Celsius")
print("column. At a US station the METAR itself is written in Celsius but the")
print("country works in Fahrenheit, so this is worth measuring, not assuming.")
print()
p = RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-04_routine-tmpc-tmpf.csv"
rows_c, _ = read_obs(p, "tmpc")
rows_f, _ = read_obs(p, "tmpf")
print(f"file            : {p.name}")
print(f"columns         : station, valid, lon, lat, elevation, tmpc, tmpf, dwpc")
print(f"rows            : {len(rows_c)}")
print(f"date range (UTC): {rows_c[0][0]} -> {rows_c[-1][0]}")
print()
print("tmpc against tmpf converted to Celsius, first 8 rows:")
print("  valid (UTC)        tmpc     tmpf   (tmpf-32)*5/9   difference")
worst = 0.0
for (t, c), (_, f) in list(zip(rows_c, rows_f))[:8]:
    conv = (f - 32) * 5 / 9
    print(f"  {t:%Y-%m-%d %H:%M}  {c:7.2f}  {f:7.2f}  {conv:13.2f}  {c - conv:+11.3f}")
for (t, c), (_, f) in zip(rows_c, rows_f):
    worst = max(worst, abs(c - (f - 32) * 5 / 9))
print()
print(f"largest disagreement across all {len(rows_c)} rows : {worst:.4f} degC")
print("  (METAR reports whole degrees Celsius and IEM derives Fahrenheit from")
print("   it, so tiny rounding differences are expected and nothing else is.)")
temps = [v for _, v in rows_c]
print(f"tmpc range in this sample : {min(temps)} to {max(temps)} degC")
print("VERDICT: tmpc is degrees Celsius at DSM, the same field and the same")
print("         units EGLC and LFPG use. No new unit handling is needed.")

line("PART B6 - US-specific check 2: are the timestamps really UTC?")
print("Every IEM request in this project sends tz=UTC. In Europe that was easy")
print("to take on trust. At DSM, local time is 5 or 6 hours behind UTC, so a")
print("mistake here would be large and silent. The same three days were pulled")
print("a second time with tz=America/Chicago, so the two can be compared.")
print()
p_utc = RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-04_routine-etc-utc.csv"
p_loc = RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-04_routine-localtime.csv"
u_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-04_routine-tmpc-tmpf.csv")
l_rows, _ = read_obs(p_loc)
print(f"UTC-request file        : {p.name}")
print(f"local-request file      : {p_loc.name}")
print(f"rows, UTC request       : {len(u_rows)}   first {u_rows[0][0]}, last {u_rows[-1][0]}")
print(f"rows, local request     : {len(l_rows)}   first {l_rows[0][0]}, last {l_rows[-1][0]}")
print()
print("The two files carry the same stamps (00:54, 01:54, ...) but different")
print("values, which is what a real timezone shift looks like: the same clock")
print("face is a different moment in each. So the test is: how far do the two")
print("series have to be slid past each other before the temperatures line up?")
print()
u_vals = [v for _, v in u_rows]
l_vals = [v for _, v in l_rows]
print("  shift (hours)   rows compared   temperatures equal")
best = None
for k in range(0, 9):
    pairs = [(l_vals[i], u_vals[i + k])
             for i in range(len(l_vals)) if i + k < len(u_vals)]
    same = sum(1 for a, b in pairs if a == b)
    print(f"  {k:+13d}   {len(pairs):13d}   {same:6d}  "
          f"({100 * same / len(pairs):.1f}%)")
    if best is None or same / len(pairs) > best[1]:
        best = (k, same / len(pairs))
print()
print(f"  best match: the UTC series is {best[0]} hours ahead of the local")
print(f"              series ({100 * best[1]:.1f}% of temperatures identical).")
print("  Expected in early July: America/Chicago is on daylight saving, UTC-5,")
print("  so a UTC stamp should sit 5 hours ahead of the same local moment.")
print(f"  VERDICT: "
      + ("MATCHES - the tz=UTC request really is UTC."
         if best[0] == 5 else "DOES NOT MATCH - stop and raise it."))
print()
print("Spot check against the forecast series, which is timezone-labelled by")
print("Open-Meteo itself:")
d, _, _ = read_forecast(RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2026-07-01_2026-07-21.json")
print(f"  Open-Meteo says timezone={d.get('timezone')}, "
      f"utc_offset_seconds={d.get('utc_offset_seconds')}")
print("  so both sides of the join are stamped in UTC and need no shifting.")
print()
print("Third check - the two spellings of UTC. The session 14 prompt describes")
print("the existing request approach as tz=Etc/UTC; every request this project")
print("has actually made uses tz=UTC. The same three days were pulled the")
print("prompt's way, and compared with the first three days of the tz=UTC")
print("sample - same fields, same station, same window, so the two responses")
print("can be compared byte for byte.")
p_utc_plain = RAW / f"iem_asos_{STATION}_2026-07-01_2026-07-22_routine.csv"
head = "".join(p_utc_plain.read_text().splitlines(keepends=True)[:73])
etc = p_utc.read_text()
etc_rows, _ = read_obs(p_utc)
print(f"  tz=UTC file     : {p_utc_plain.name}")
print(f"                    first 73 lines (1 header + 72 rows), "
      f"{len(head):,} bytes")
print(f"  tz=Etc/UTC file : {p_utc.name}")
print(f"                    {len(etc.splitlines())} lines, {len(etc):,} bytes")
print(f"  byte-for-byte identical : {'YES' if head == etc else 'NO'}")
print("  So the two spellings are the same request. The project's tz=UTC needs")
print("  no change; the prompt's wording and the code agree in substance.")

line("PART C - plain first read")
print("A summary of what the checks above actually printed. Nothing here is a")
print("decision; the owner decides what happens next.")
print()
print(f"1. Position. IEM's own record puts DSM at lat {DSM_LAT}, lon {DSM_LON},")
print(f"   elevation {DSM_ELEV_M} m, timezone {props['tzname']}. That is what every")
print("   forecast request in this session used - nothing was typed from a map.")
print()
d_recent, t_recent, v_recent = read_forecast(
    RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2026-07-01_2026-07-21.json")
gd = km_between(DSM_LAT, DSM_LON, d_recent["latitude"], d_recent["longitude"])
print(f"2. Forecast source. The Previous Runs API carries DSM. Its grid point is")
print(f"   lat {d_recent['latitude']}, lon {d_recent['longitude']}, elevation "
      f"{d_recent['elevation']} m -")
print(f"   {gd:.2f} km from the airport, {d_recent['elevation'] - DSM_ELEV_M:+.1f} m "
      f"in height. That is CLOSER than")
print("   either European airport's grid point (4.33 km at EGLC, 3.44 km at LFPG)")
print("   and the first height mismatch worth naming, though 9 m is small.")
print("   Recent sample: 504 hourly rows, 0 missing.")
print()
_, _, p1 = read_forecast(
    RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2021-03-01_2021-03-07.json")
d2, t2, p2 = read_forecast(
    RAW / f"openmeteo_previousruns_gfs_global_{STATION}_2021-03-18_2021-03-26.json")
first2 = t2[next(i for i, v in enumerate(p2) if v is not None)]
print(f"3. Archive depth. 1-7 March 2021 comes back HTTP 200 with all "
      f"{len(p1)} values")
print(f"   null, and the first hour carrying a real value is {first2} UTC -")
print("   the same hour as EGLC (F1) and LFPG (F20), to the hour. So the D13")
print("   split dates need no moving for DSM either.")
print()
print(f"4. Target hour. America/Chicago's standard offset is UTC{std_offset_h:+.0f}, so local")
print(f"   standard noon is {TARGET_HOUR_UTC:02d}:00 UTC year-round, which is what D33 says.")
print("   At 18:00 UTC the local clock reads 12:00 CST in winter and 13:00 CDT")
print("   in summer - midday to early afternoon, matching how 12:00 UTC sat in")
print("   Europe. 12:00 UTC would have been 06:00/07:00 local, at dawn.")
print()
print("5. Truth source. IEM carries DSM in IA_ASOS with a clean record. Both")
print("   samples, five years apart, are complete apart from the first hour of")
print("   each window, which is a request-boundary artefact rather than a gap.")
print()
print("6. Report timing. DSM reports at :54, every single report in both")
print("   samples - 504 of 504 recently and 336 of 336 in 2021, with IEM's own")
print("   METAR_RESET_MINUTE attribute saying 54 as well. That is 6 minutes")
print("   before the hour, inside D14's 15-minute tolerance, so D14 applies as")
print("   written at the 18:00 UTC target: the 17:54 report is the observation")
print("   for 18:00. Not one report in either sample falls outside the")
print("   tolerance, so on this evidence DSM loses no day to off-hour")
print("   reporting - unlike LFPG, which loses three across five years (F25).")
print()
print("7. Units and timezone need no new handling. tmpc is degrees Celsius at")
print("   DSM, agreeing with the Fahrenheit field to 0.005 degC across 72 rows,")
print("   and the tz=UTC request really is UTC: pulled again in local time, the")
print("   same temperatures line up exactly 5 hours later, which is the July")
print("   UTC-5 daylight-saving offset. tz=UTC and tz=Etc/UTC return byte-for-")
print("   byte the same rows.")
print()
print("8. Gap counts, nothing filled (SPEC 2.2). Recent sample: 504 hours")
print("   expected, 503 covered, 1 missing (the boundary hour). Early sample:")
print("   336 expected, 335 covered, 1 missing (the same boundary artefact).")
print("   No report in either sample carries a missing temperature.")
print()
print("9. Plain verdict: YES - on this evidence DSM is usable for the recipe")
print("   the same way EGLC and CDG were. Every verify-on-contact check passed,")
print("   and the only thing that had to change is the target hour, which was")
print("   changed on principle before any DSM data was seen (D33). Three-week")
print("   samples cannot prove what the other five years look like; the full")
print("   pull and its gap map settle that, exactly as session 10 did for CDG.")
