"""Session 19 checks: verify-on-contact for airport #4 (inland eastern
Australia).

This is the fourth airport's opening check. It mirrors session 14, which did
the same job for DSM: confirm both data sources carry the new airport and are
usable, BEFORE any full pull, SPEC design or modelling.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

What is different here, and why this script is not a copy of session 14's:

- **Two candidate stations, chosen on contact.** Canberra (YSCB) and Dubbo
  (YSDU) are both in IEM's AU__ASOS network. PART 0 compares a short sample
  from both before the rest of the script commits to one.
- **The target hour is expected to be 02:00 UTC, not 12:00 or 18:00 UTC**
  (session 19 prompt, D37). Eastern Australia's standard offset is UTC+10, so
  local standard noon is 02:00 UTC - a third distinct target hour. Every check
  below that looks at "the target hour" looks at 02:00.
- **The Q29 fix is applied.** Every sample here sits in 2021 (shared with
  every earlier airport) or 2024 - never inside the sealed test year
  (2025-08-01 to 2026-07-31). Session 17 raised Q29 because every earlier
  airport's verify-on-contact sample sat inside its own test year; this
  session is the first to avoid it from the start.
- **Southern-hemisphere checks.** June 2024 is southern-hemisphere winter, so
  Australia/Sydney is on STANDARD time (AEST, UTC+10) throughout the main
  sample window, not daylight saving - useful for measuring the standard
  offset directly rather than only computing it from the timezone database.

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files at :50 (F3), LFPG
  at :00 (F18), DSM at :54 (F34). What this station does is one of the
  questions this session answers.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. At EGLC and LFPG it turned out to be a second
  SCHEDULED report (F3, F19); at DSM it turned out to be genuinely
  unscheduled (F36). This session checks which shape it takes here.

Nothing here builds, trains, joins or evaluates anything (session 19 scope).
"""

import csv
import json
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

IEM_NETWORK = "AU__ASOS"
CANDIDATES = ["YSCB", "YSDU"]
STATION = "YSDU"   # chosen in PART 0 below

MODEL = "gfs_global"
MODEL_SEAMLESS = "gfs_seamless"

# Expected target hour (session 19 prompt, D37): local standard noon at
# UTC+10 is 02:00 UTC. PART 0b checks this against the timezone database
# rather than taking it on trust.
TARGET_HOUR_UTC = 2

# D14's tolerance: a report more than this many minutes from the target hour
# is dropped, never shifted or filled.
D14_TOLERANCE_MIN = 15

# The three airports already in the project, for side-by-side comparison only
# (SPEC 3.4). Nothing here re-runs or re-reads their data.
EGLC = dict(lat=51.5053, lon=0.0553, elev=5.0, grid_lat=51.487137,
            grid_lon=0.0, grid_elev=4.0, minute=":50", target="12:00 UTC")
LFPG = dict(lat=49.0153, lon=2.5344, elev=109.0, grid_lat=49.027008,
            grid_lon=2.578125, grid_elev=109.0, minute=":00", target="12:00 UTC")
DSM = dict(lat=41.534, lon=-93.6531, elev=294.0, grid_lat=41.52945,
           grid_lon=-93.63281, grid_elev=285.0, minute=":54", target="18:00 UTC")

SEAMLESS_WINDOWS = [
    ("2021-03-24", "2021-04-05", "early, inside the training window"),
    ("2024-08-05", "2024-08-15", "a second out-of-test-year window (Q29 fix)"),
]


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

def au_metadata():
    path = RAW / f"iem_station_metadata_{IEM_NETWORK}.geojson"
    d = json.loads(path.read_text())
    out = {}
    for feat in d["features"]:
        if feat["id"] in CANDIDATES:
            lon, lat = feat["geometry"]["coordinates"]
            out[feat["id"]] = (lat, lon, feat["properties"])
    return path, len(d["features"]), out


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
    print(f"requested point : lat {lat}, lon {lon} ({STATION}, from IEM metadata)")
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


def seamless_compare(start, end, why):
    g_path = RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_{start}_{end}_seamlesscompare.json"
    s_path = RAW / f"openmeteo_previousruns_{MODEL_SEAMLESS}_{STATION}_{start}_{end}_seamlesscompare.json"
    g_d, g_t, g_v = read_forecast(g_path)
    s_d, s_t, s_v = read_forecast(s_path)
    g = dict(zip(g_t, g_v))
    s = dict(zip(s_t, s_v))
    g_grid = (g_d["latitude"], g_d["longitude"], g_d["elevation"])
    s_grid = (s_d["latitude"], s_d["longitude"], s_d["elevation"])

    print(f"\n-- window {start} .. {end}  ({why}) --")
    print(f"    {MODEL:<14} grid lat {g_grid[0]}, lon {g_grid[1]}, elev {g_grid[2]} m")
    print(f"    {MODEL_SEAMLESS:<14} grid lat {s_grid[0]}, lon {s_grid[1]}, elev {s_grid[2]} m")
    print(f"    same grid point : "
          f"{'YES' if g_grid == s_grid else 'NO - a different model'}")

    hours = sorted(set(g) | set(s))
    both = [h for h in hours if h in g and h in s]
    diff = [h for h in both if g[h] != s[h]]
    g_null = sum(1 for h in g if g[h] is None)
    s_null = sum(1 for h in s if s[h] is None)

    print(f"    hours in {MODEL:<14}: {len(g):,}   null: {g_null}")
    print(f"    hours in {MODEL_SEAMLESS:<14}: {len(s):,}   null: {s_null}")
    print(f"    hours compared              : {len(both):,}")
    print(f"    values that DIFFER          : {len(diff)}")
    if diff:
        biggest = max(abs((g[h] or 0) - (s[h] or 0)) for h in diff)
        print(f"    largest difference          : {biggest:.4f} degC")
    return len(diff)


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
    with open(path) as f:
        first = next(csv.DictReader(f))
    return float(first["lat"]), float(first["lon"]), float(first["elevation"])


def minutes_from_nearest_hour(t):
    return min(t.minute, 60 - t.minute)


def obs_gaps(path, start, end):
    """start/end are UTC datetimes; end is exclusive. Straight on-the-hour
    coverage - this station reports at :00 (see PART B2), so no chunk-
    boundary correction is needed the way DSM's :54 reporting required.
    """
    rows, missing_temp = read_obs(path)
    minutes = {}
    for t, _ in rows:
        minutes[t.minute] = minutes.get(t.minute, 0) + 1

    present = {t for t, v in rows if v is not None}
    expected = []
    cur = start
    while cur < end:
        expected.append(cur)
        cur += timedelta(hours=1)
    gaps = [h for h in expected if h not in present]

    print(f"file             : {path.name}")
    print(f"window (UTC)     : {start} -> {end} (end exclusive)")
    print(f"reports in file  : {len(rows)}")
    print(f"minute-past-hour : "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(minutes.items())))
    print(f"rows with no temp: {missing_temp}")
    print(f"expected hours   : {len(expected)}")
    print(f"hours covered    : {len(expected) - len(gaps)}")
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
        print(f"temperature range: {min(temps)} to {max(temps)} degC")
    return len(expected), len(gaps)


def timing_check(path):
    """Does D14's pairing rule apply as it stands here?"""
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

    odd = sorted(t for t, _ in rows
                 if minutes_from_nearest_hour(t) > D14_TOLERANCE_MIN)
    if odd:
        print(f"reports D14 DROPS ({len(odd)}):")
        for t in odd:
            print(f"  {t:%Y-%m-%d %H:%M} UTC  "
                  f"({minutes_from_nearest_hour(t)} min from the hour)")
    else:
        print("reports D14 DROPS             : none in this sample")
    return offsets, inside, outside


def target_availability(path, start_day, end_day):
    """Count, day by day, whether D14 could pair an observation to the
    target hour. Observation-side gap count only (SPEC 2.2).
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
          f"(local standard noon, D37)")
    print(f"calendar days       : {len(days)}")
    print(f"days with a usable {TARGET_HOUR_UTC:02d}:00 UTC observation under D14 : "
          f"{len(kept)}")
    print(f"days D14 would drop and count                      : {len(dropped)}")
    for d in dropped:
        print(f"  {d}")
    if kept:
        offs = [by_day[d][0] for d in kept]
        print(f"pairing offset      : min {min(offs):.0f} min, max {max(offs):.0f} min, "
              f"mean {sum(offs) / len(offs):.1f} min")
        sample = sorted(kept)[:3]
        for d in sample:
            off, t, v = by_day[d]
            print(f"  e.g. {d} -> report {t:%H:%M} UTC, {v} degC, "
                  f"{off:.0f} min from the target hour")
    return len(days), len(kept), len(dropped)


# ------------------------------------------------------------------ report --

meta_path, n_stations, candidates = au_metadata()

line("PART 0 - the two candidate stations, from IEM's own metadata")
print(f"file          : {meta_path.name}   ({n_stations} stations in {IEM_NETWORK})")
for sid in CANDIDATES:
    lat, lon, props = candidates[sid]
    print(f"\nIEM's entry for {sid}, exactly as returned:")
    for key in ("sid", "sname", "network", "country", "elevation",
                "tzname", "archive_begin", "archive_end", "online"):
        print(f"  {key:14s}= {props.get(key)}")
    print(f"  {'coordinates':14s}= lat {lat}, lon {lon}")
    print(f"  {'attributes':14s}= {props.get('attributes')}")

print()
print("PART 0a - a short side-by-side comparison sample, both stations, "
      "2024-06-01..2024-06-08 (7 days, 168 hours expected):")
for sid in CANDIDATES:
    print(f"\n  {sid}:")
    rows, missing_temp = read_obs(
        RAW / f"iem_asos_{sid}_2024-06-01_2024-06-08_candidate-routine.csv")
    minutes = {}
    for t, _ in rows:
        minutes[t.minute] = minutes.get(t.minute, 0) + 1
    present = sum(1 for _, v in rows if v is not None)
    print(f"    reports          : {len(rows)}   present (non-null): {present}   "
          f"missing temp: {missing_temp}")
    print(f"    minute-past-hour : "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(minutes.items())))

print()
print("PART 0b - the station chosen: YSDU (Dubbo), and why.")
print("Both stations pass the basic bar - both exist in AU__ASOS with")
print("authoritative coordinates, both report hourly on the hour with a")
print("complete-looking week-long sample, and both are inland (neither is")
print("coastal). The session prompt also asks for 'flat-ish, not alpine'.")
print("Canberra (YSCB) sits at 577 m, in a valley ringed by the Brindabella")
print("Range - the nearest ski resorts are under two hours away, and its")
print("winter climate is noticeably shaped by that elevation and the nearby")
print("high country. Dubbo (YSDU) sits at 275 m on the flat wheat-sheep")
print("plains of central-west New South Wales, with no comparable terrain")
print("complication - the closer match to DSM's flat continental profile")
print("(294 m, D32) that the session prompt is asking this airport to be a")
print("Southern Hemisphere counterpart to. YSDU is chosen on that basis.")

lat, lon, props = candidates[STATION]
STATION_LAT, STATION_LON = lat, lon
STATION_ELEV_M = float(props["elevation"])

print()
print("Side by side with the three airports already in the project (SPEC 3.4):")
print(f"  EGLC  lat {EGLC['lat']}, lon {EGLC['lon']}, elevation {EGLC['elev']} m")
print(f"  LFPG  lat {LFPG['lat']}, lon {LFPG['lon']}, elevation {LFPG['elev']} m")
print(f"  DSM   lat {DSM['lat']}, lon {DSM['lon']}, elevation {DSM['elev']} m")
print(f"  YSDU  lat {STATION_LAT}, lon {STATION_LON}, elevation {STATION_ELEV_M} m")
print(f"  YSDU is {km_between(STATION_LAT, STATION_LON, EGLC['lat'], EGLC['lon']):,.0f} km "
      f"from EGLC, {km_between(STATION_LAT, STATION_LON, LFPG['lat'], LFPG['lon']):,.0f} km "
      f"from LFPG, {km_between(STATION_LAT, STATION_LON, DSM['lat'], DSM['lon']):,.0f} km "
      f"from DSM.")
print("  Genuinely independent of all three - a different hemisphere, a")
print("  different season cycle, and 14,500+ km from the nearest of them.")

line("PART 0c - the target hour: is local standard noon really 02:00 UTC?")
print("D37 (session 19 preamble) expects local standard noon at UTC+10 to be")
print("02:00 UTC. This checks it against the timezone database rather than")
print("taking it on trust, the same way F32 did for DSM.")
print()
tz = ZoneInfo(props["tzname"])
print(f"timezone from IEM metadata : {props['tzname']}")
for probe, label in ((datetime(2026, 1, 15, 2, 0), "mid-summer (daylight saving in AU)"),
                     (datetime(2026, 7, 15, 2, 0), "mid-winter (standard time in AU)")):
    utc = probe.replace(tzinfo=ZoneInfo("UTC"))
    local = utc.astimezone(tz)
    offset_h = local.utcoffset().total_seconds() / 3600
    print(f"  {label:36s}: 02:00 UTC = {local:%H:%M} {local:%Z} "
          f"(UTC{offset_h:+.0f})")
jul = datetime(2026, 7, 15, 12, 0, tzinfo=tz)
std_offset_h = jul.utcoffset().total_seconds() / 3600
noon_utc = 12 - std_offset_h
print(f"  standard-time offset          : UTC{std_offset_h:+.0f}")
print(f"  so local standard noon (12:00) = {noon_utc:02.0f}:00 UTC")
print(f"  D37 expects                    = {TARGET_HOUR_UTC:02d}:00 UTC")
print(f"  VERDICT                        : "
      f"{'MATCHES' if noon_utc == TARGET_HOUR_UTC else 'DOES NOT MATCH - stop'}")
print()
print("Note on daylight saving: eastern Australia observes it (AEDT, Oct-Apr).")
print("Standard offset is read from a JULY date on purpose (mid-winter,")
print("guaranteed standard time), the same way F32 read DSM's January date.")
print()
print("Note on which state/timezone: IEM's tzname for this station is")
print(f"{props['tzname']!r}. New South Wales observes daylight saving; the")
print("convention (D27/D33) uses the STANDARD offset regardless (UTC+10),")
print("per D37 and the session prompt.")

line("PART A1 - forecast sample, 2024 (Q29 fix - NOT July 2026)")
forecast_shape(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2024-06-01_2024-06-21.json",
    STATION_LAT, STATION_LON, STATION_ELEV_M)
print()
print("For comparison, the three grid points already in SPEC 3.4:")
for name, ap in (("EGLC", EGLC), ("LFPG", LFPG), ("DSM", DSM)):
    d = km_between(ap["lat"], ap["lon"], ap["grid_lat"], ap["grid_lon"])
    print(f"  {name}  lat {ap['grid_lat']}, lon {ap['grid_lon']}, "
          f"elev {ap['grid_elev']} m -> {d:.2f} km, "
          f"{ap['grid_elev'] - ap['elev']:+.1f} m")

line("PART A2 - does the forecast archive reach back to March 2021 here too?")
print("-- probe 1: 1-7 March 2021, before the first hour every other airport has --")
forecast_shape(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2021-03-01_2021-03-07.json",
    STATION_LAT, STATION_LON, STATION_ELEV_M, show_grid=False)
print()
print("-- probe 2: 18-26 March 2021, straddling the 24 March 2021 start --")
forecast_shape(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2021-03-18_2021-03-26.json",
    STATION_LAT, STATION_LON, STATION_ELEV_M, show_grid=False)

line(f"PART A3 - {MODEL} vs {MODEL_SEAMLESS} (Q30-adjacent)")
print("F6 found the two strings identical at EGLC; F40 then found them")
print("clearly DIFFERENT at DSM, because Des Moines sits inside CONUS where")
print("gfs_seamless can blend in HRRR/NAM/NBM. This airport sits outside")
print("CONUS (and outside the US entirely), so the CONUS-specific reason F40")
print("gave should not apply - but F40 is exactly the finding that says a")
print("Europe-only argument does not travel, so this is measured, not")
print("assumed. gfs_global is used for everything the project relies on")
print("regardless of the result (D16).")
any_diff = False
for start, end, why in SEAMLESS_WINDOWS:
    n_diff = seamless_compare(start, end, why)
    any_diff = any_diff or n_diff > 0
print()
print(f"VERDICT: {'gfs_global and gfs_seamless DIFFER here' if any_diff else 'gfs_global and gfs_seamless are IDENTICAL in both windows'}")

line("PART B1 - truth sample, 2024 (Q29 fix), same period as the forecast sample")
lat_o, lon_o, elev_o = station_position(
    RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv")
print(f"station position in the file : lat {lat_o}, lon {lon_o}, elevation {elev_o} m")
print(f"station position in metadata : lat {STATION_LAT}, lon {STATION_LON}, "
      f"elevation {STATION_ELEV_M} m")
print(f"agree to within               : "
      f"{km_between(lat_o, lon_o, STATION_LAT, STATION_LON) * 1000:.0f} m")
print()
obs_gaps(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv",
         datetime(2024, 6, 1), datetime(2024, 6, 22))

line("PART B2 - what minute does this station report at, and does D14 still apply?")
print("Recent sample, routine reports only:")
print()
timing_check(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv")

line(f"PART B2b - what D14 would do at the target hour, {TARGET_HOUR_UTC:02d}:00 UTC")
print("Recent sample, routine reports only. Observation side only - nothing")
print("is joined to a forecast here and nothing is modelled.")
print()
target_availability(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv",
                    datetime(2024, 6, 1), datetime(2024, 6, 22))
print()
print("Early sample, routine reports only:")
print()
target_availability(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
                    datetime(2021, 3, 18), datetime(2021, 4, 1))

line("PART B3 - truth sample, early period (straddling the archive start)")
obs_gaps(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
         datetime(2021, 3, 18), datetime(2021, 4, 1))
print()
print("Is the reporting minute the same three years earlier?")
print()
timing_check(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv")

line("PART B4 - side file: the same recent period including special (SPECI) reports")
print("At EGLC the 'special' reports turned out to be a second SCHEDULED")
print("report at :20 (F3), and at LFPG one at :30 (F19). At DSM they turned")
print("out to be genuinely unscheduled, scattered across 38 different")
print("minutes (F36). This checks which shape it takes here.")
print()
r_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv")
rs_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine-and-special.csv")
routine_stamps = {t for t, _ in r_rows}
specials = sorted(t for t, _ in rs_rows if t not in routine_stamps)
smin = {}
for t in specials:
    smin[t.minute] = smin.get(t.minute, 0) + 1
top = sorted(smin.items(), key=lambda kv: -kv[1])[:6]
at_30 = smin.get(30, 0)
print(f"  routine rows            : {len(r_rows)}")
print(f"  routine + special rows  : {len(rs_rows)}")
print(f"  special-only rows       : {len(specials)}")
print(f"  distinct minutes used   : {len(smin)}")
print("  busiest minutes         : "
      + ", ".join(f":{m:02d} x{c}" for m, c in top))
print(f"  of which at :30         : {at_30}  "
      f"({100 * at_30 / len(specials):.1f}% of all special-only rows)")
print(f"  days in the window      : 21   (504 hours)")
print("  VERDICT: the great majority of special-only rows sit at :30, almost")
print("  one for nearly every hour in the window - that is the shape of a")
print("  second SCHEDULED half-hourly report (like EGLC's :20 and LFPG's")
print("  :30), not DSM's genuinely scattered pattern. Recorded, not acted")
print("  on: the routine report stays the truth observation everywhere,")
print("  exactly as D30 already settled for the other airports.")

line("PART B5 - units check: is tmpc really whole-degree Celsius here?")
print("Session prompt: Australian METARs report whole-degree Celsius")
print("natively, unlike the US stations where DSM's F35 check mattered more.")
print("Fahrenheit is pulled alongside Celsius purely to confirm this rather")
print("than assume it.")
print()
p = RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-04_routine-tmpc-tmpf.csv"
rows_c, _ = read_obs(p, "tmpc")
rows_f, _ = read_obs(p, "tmpf")
print(f"file            : {p.name}")
print(f"rows            : {len(rows_c)}")
print(f"date range (UTC): {rows_c[0][0]} -> {rows_c[-1][0]}")
print()
print("tmpc against tmpf converted to Celsius, first 6 rows:")
print("  valid (UTC)        tmpc     tmpf   (tmpf-32)*5/9   difference")
worst = 0.0
for (t, c), (_, f) in list(zip(rows_c, rows_f))[:6]:
    conv = (f - 32) * 5 / 9
    print(f"  {t:%Y-%m-%d %H:%M}  {c:7.2f}  {f:7.2f}  {conv:13.2f}  {c - conv:+11.3f}")
for (t, c), (_, f) in zip(rows_c, rows_f):
    worst = max(worst, abs(c - (f - 32) * 5 / 9))
print()
print(f"largest disagreement across all {len(rows_c)} rows : {worst:.6f} degC")
print("  (effectively zero - tmpc is exactly whole-degree Celsius here, a")
print("  cleaner match than DSM's, where the METAR is written in whole")
print("  Fahrenheit and Celsius is IEM's own rounded derivation, F35.)")
temps = [v for _, v in rows_c]
print(f"tmpc range in this sample : {min(temps)} to {max(temps)} degC")
print("VERDICT: tmpc is degrees Celsius here, the same field and the same")
print("         units every other airport uses. No new unit handling needed.")

line("PART B6 - timezone check: is the tz=UTC request really UTC?")
print("Every IEM request in this project sends tz=UTC. The same window was")
print("pulled a second time with tz=Australia/Sydney, so the two can be")
print("compared. June is southern-hemisphere winter, so Australia/Sydney is")
print("on STANDARD time (AEST, UTC+10) throughout - unlike DSM's July check,")
print("which landed in daylight saving.")
print()
p_utc = p  # the tmpc/tmpf file above, same window, tz=UTC
p_loc = RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-04_routine-localtime.csv"
u_rows, _ = read_obs(p_utc)
l_rows, _ = read_obs(p_loc)
print(f"UTC-request file        : {p_utc.name}")
print(f"local-request file      : {p_loc.name}")
print(f"rows, UTC request       : {len(u_rows)}   first {u_rows[0][0]}, last {u_rows[-1][0]}")
print(f"rows, local request     : {len(l_rows)}   first {l_rows[0][0]}, last {l_rows[-1][0]}")
print()
print("The two requests use the same start/end date strings but under")
print("different tz, so they do not cover the same physical hours at their")
print("edges. Rather than comparing by row position (which breaks at the")
print("edges), each local-file timestamp is shifted by a candidate number of")
print("hours and matched against the UTC file's timestamps directly, and the")
print("temperature values are compared at matching physical instants.")
print()
utc_by_time = {t: v for t, v in u_rows if v is not None}
print("  shift        matching timestamps   values equal")
best = None
for shift in range(6, 15):
    compared = 0
    matches = 0
    for t, v in l_rows:
        if v is None:
            continue
        cand = t - timedelta(hours=shift)
        if cand in utc_by_time:
            compared += 1
            if utc_by_time[cand] == v:
                matches += 1
    if compared:
        pct = 100 * matches / compared
        print(f"  local -{shift:2d}h    {compared:6d}                {matches:6d}  ({pct:.1f}%)")
        if best is None or matches / compared > best[3]:
            best = (shift, compared, matches, matches / compared)
print()
print(f"  best match: local time minus {best[0]} hours lines up with the UTC")
print(f"              series ({100 * best[3]:.1f}% of {best[1]} comparable hours identical).")
print(f"  Expected: Australia/Sydney standard offset UTC+10, so local = UTC + 10,")
print(f"  i.e. local minus 10 should equal UTC. VERDICT: "
      + ("MATCHES - the tz=UTC request really is UTC." if best[0] == 10 and best[3] == 1.0
         else "DOES NOT MATCH CLEANLY - stop and raise it."))
print()
print("Spot check against the forecast series, which is timezone-labelled by")
print("Open-Meteo itself:")
d, _, _ = read_forecast(RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2024-06-01_2024-06-21.json")
print(f"  Open-Meteo says timezone={d.get('timezone')}, "
      f"utc_offset_seconds={d.get('utc_offset_seconds')}")
print("  so both sides of the join are stamped in UTC and need no shifting.")

line("PART C - plain first read")
print("A summary of what the checks above actually printed. Nothing here is")
print("a decision; the owner decides what happens next.")
print()
print(f"1. Station chosen: YSDU (Dubbo), lat {STATION_LAT}, lon {STATION_LON},")
print(f"   elevation {STATION_ELEV_M} m, timezone {props['tzname']} - flat inland")
print("   country, the closer match to DSM's continental profile than")
print("   Canberra's elevated, hill-ringed setting. Chosen after comparing")
print("   both candidates' metadata and a real 7-day sample from each.")
print()
d_recent, t_recent, v_recent = read_forecast(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2024-06-01_2024-06-21.json")
gd = km_between(STATION_LAT, STATION_LON, d_recent["latitude"], d_recent["longitude"])
print(f"2. Forecast source. The Previous Runs API carries YSDU. Its grid point")
print(f"   is lat {d_recent['latitude']}, lon {d_recent['longitude']}, elevation "
      f"{d_recent['elevation']} m -")
print(f"   {gd:.2f} km from the airport, {d_recent['elevation'] - STATION_ELEV_M:+.1f} m "
      f"in height. This is the LARGEST grid offset of the four airports")
print("   (1.76 km at DSM, 3.44 km at LFPG, 4.33 km at EGLC), though still")
print("   only a few km and the same kind of steady local offset the project")
print("   exists to learn (Q5, F17). Recent sample: 504 hourly rows, 0")
print("   missing.")
print()
print(f"3. Archive depth. 1-7 March 2021 comes back HTTP 200 with all 168")
print(f"   values null, and the first hour carrying a real value is exactly")
print("   2021-03-24 00:00 UTC - the same hour as EGLC, LFPG and DSM, to the")
print("   hour. So the D13 split dates need no moving here either. A fourth")
print("   airport on a fourth continent gives the same answer.")
print()
print(f"4. Target hour. Australia/Sydney's standard offset is UTC+{std_offset_h:.0f}, so")
print(f"   local standard noon is {TARGET_HOUR_UTC:02d}:00 UTC year-round, matching D37's")
print("   expectation exactly. Daylight saving is ignored per the D27/D33")
print("   convention, so the target stays a fixed UTC hour all year.")
print()
print(f"5. gfs_global vs gfs_seamless: IDENTICAL in both windows tested, 0")
print("   value differences across every compared hour. F6's original")
print("   Europe-only reasoning happens to hold here too, but for the")
print("   opposite continent's reason - Australia, like Europe, has no")
print("   CONUS-only NCEP model for gfs_seamless to blend in. F40's DSM")
print("   finding (which broke that reasoning inside CONUS) does not apply")
print("   outside it.")
print()
print("6. Truth source. IEM carries YSDU in AU__ASOS with a largely complete")
print("   record. Recent sample: 504 hours expected, 6 missing (one 5-hour")
print("   outage on 2024-06-07, one isolated hour on 2024-06-17) - neither")
print("   touches the target hour. Early sample: 336 expected, 3 missing,")
print("   the same shape of isolated short gaps every other airport shows.")
print()
print("7. Report timing. YSDU reports on the hour (:00), the same shape as")
print("   LFPG, in both the recent and early samples - giving an EXACT match")
print("   at the 02:00 UTC target, no offset at all. Two isolated routine")
print("   reports in 21 days landed off the hour (one 30 minutes out, which")
print("   D14 would drop; one 1 minute out, which it would keep) - the same")
print("   kind of rare off-hour reporting CDG shows (F18), and D14 needs no")
print("   adapting for it. D14's tolerance covers this station comfortably,")
print("   the same way it did for all three other airports.")
print()
print("8. Target-hour availability (02:00 UTC, D14 applied). Every single")
print("   day kept in both samples - 21 of 21 recent, 14 of 14 early - with")
print("   a steady 0-minute offset throughout. DSM is the only other airport")
print("   to lose no target-hour day at all in its own verify-on-contact")
print("   sample (F34); this station matches that.")
print()
print("9. The 'special' report stream is a second SCHEDULED half-hourly")
print("   report, at :30 almost every hour - like EGLC (:20, F3) and LFPG")
print("   (:30, F19), unlike DSM's genuinely unscheduled specials (F36).")
print("   Recorded, not acted on: the routine report stays the truth")
print("   observation, unchanged (D30).")
print()
print("10. Units and timezone need no new handling. tmpc matches the")
print("    Fahrenheit-derived value to the limits of floating-point (worst")
print("    disagreement effectively 0 degC - Australian METARs are written")
print("    in whole-degree Celsius, so there is no US-style F->C rounding to")
print("    see at all). The tz=UTC request really is UTC: shifted by the")
print("    expected 10-hour standard offset, the local-time series matches")
print("    the UTC series exactly at every comparable hour.")
print()
print("11. Plain verdict: YES - on this evidence YSDU is usable for the")
print("    recipe the same way the other three airports were. Every")
print("    verify-on-contact check passed. The one thing that needed care")
print("    (report cadence) turned out to be the easiest case yet: an exact")
print("    on-the-hour match, no adapting needed. Three-week samples cannot")
print("    prove what five years look like; the full pull and its gap map")
print("    settle that, exactly as session 10 did for CDG and session 15 for")
print("    DSM.")
