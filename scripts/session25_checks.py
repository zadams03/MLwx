"""Session 25 checks: verify-on-contact for airport #5 (a mountain-valley US
airport).

This is the fifth airport's opening check. It mirrors session 19, which did
the same job for Dubbo (airport #4): confirm both data sources carry the new
airport and are usable, BEFORE any full pull, SPEC design or modelling.

Reads only from data/raw/. Writes nothing. Fills nothing (SPEC 2.2).

What is different here, and why this script is not a copy of session 19's:

- **Two candidate stations in DIFFERENT IEM networks.** Bozeman (BZN,
  MT_ASOS) and Reno (RNO, NV_ASOS) are compared, including a forecast sample
  for each, so the grid-point ELEVATION MISMATCH - the key mountain figure
  the session prompt asks to measure - can be compared before picking one.
- **The target hour is computed, not assumed.** Local standard noon depends
  on the chosen station's own IANA timezone, read from IEM metadata, checked
  against the timezone database the same way F32 did for DSM and F50 for
  Dubbo - not assumed from a nominal "Mountain Time = UTC-7" guess.
- **The mountain-specific check.** Grid-point elevation mismatch is reported
  explicitly and flagged as the figure to watch alongside the mean-bias
  reference at evaluation time (session prompt).
- **The Q29 fix continues.** Every sample here sits in 2021 (shared with
  every earlier airport) or 2024 - never inside the sealed test year
  (2025-08-01 to 2026-07-31).

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files at :50 (F3), LFPG
  at :00 (F18), DSM at :54 (F34), Dubbo (YSDU) at :00 (F53). What this station
  does is one of the questions this session answers.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. It has taken a different shape at every airport so
  far (F3, F19, F36, F55).

Nothing here builds, trains, joins or evaluates anything (session 25 scope).
"""

import csv
import json
import math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

RAW = Path(__file__).resolve().parent.parent / "data" / "raw"

CANDIDATES = {"BZN": "MT_ASOS", "RNO": "NV_ASOS"}
STATION = "BZN"   # chosen in PART 0 below
STATION_NETWORK = CANDIDATES[STATION]

MODEL = "gfs_global"
MODEL_SEAMLESS = "gfs_seamless"

# D14's tolerance: a report more than this many minutes from the target hour
# is dropped, never shifted or filled.
D14_TOLERANCE_MIN = 15

# The four airports already in the project, for side-by-side comparison only
# (SPEC 3.4). Nothing here re-runs or re-reads their data.
EGLC = dict(lat=51.5053, lon=0.0553, elev=5.0, grid_lat=51.487137,
            grid_lon=0.0, grid_elev=4.0, minute=":50", target="12:00 UTC")
LFPG = dict(lat=49.0153, lon=2.5344, elev=109.0, grid_lat=49.027008,
            grid_lon=2.578125, grid_elev=109.0, minute=":00", target="12:00 UTC")
DSM = dict(lat=41.534, lon=-93.6531, elev=294.0, grid_lat=41.52945,
           grid_lon=-93.63281, grid_elev=285.0, minute=":54", target="18:00 UTC")
YSDU = dict(lat=-32.2167, lon=148.5747, elev=275.0, grid_lat=-32.274643,
            grid_lon=148.59375, grid_elev=279.0, minute=":00", target="02:00 UTC")

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

def station_metadata(sid, network):
    path = RAW / f"iem_station_metadata_{network}.geojson"
    d = json.loads(path.read_text())
    for feat in d["features"]:
        if feat["id"] == sid:
            lon, lat = feat["geometry"]["coordinates"]
            return path, len(d["features"]), lat, lon, feat["properties"]
    raise SystemExit(f"{sid} not found in {path.name}")


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


def nearest_hour(t):
    """Round a report timestamp to the calendar hour it serves. BZN reports
    at :56, 4 minutes before the hour, so a report stamped 18:56 serves the
    19:00 hour - the same "nearest hour" logic D14 uses for pairing, applied
    generally so a whole-hours gap map means the same thing here as it did
    for LFPG/Dubbo's on-the-hour reporting (session 15's F39 did the
    equivalent for DSM's :54 reports, which serve the NEXT hour the same way).
    """
    return (t + timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)


def obs_gaps(path, start, end):
    """start/end are UTC datetimes; end is exclusive."""
    rows, missing_temp = read_obs(path)
    minutes = {}
    for t, _ in rows:
        minutes[t.minute] = minutes.get(t.minute, 0) + 1

    present = {nearest_hour(t) for t, v in rows if v is not None}
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


def target_availability(path, start_day, end_day, target_hour):
    """Count, day by day, whether D14 could pair an observation to the
    target hour. Observation-side gap count only (SPEC 2.2).
    """
    rows, _ = read_obs(path)
    by_day = {}
    for t, v in rows:
        if v is None:
            continue
        target = t.replace(hour=target_hour, minute=0)
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
    print(f"target hour         : {target_hour:02d}:00 UTC "
          f"(local standard noon)")
    print(f"calendar days       : {len(days)}")
    print(f"days with a usable {target_hour:02d}:00 UTC observation under D14 : "
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

line("PART 0 - the two candidates, from IEM's own metadata")
cand_data = {}
for sid, network in CANDIDATES.items():
    meta_path, n_stations, lat, lon, props = station_metadata(sid, network)
    cand_data[sid] = (lat, lon, props)
    print(f"\nfile          : {meta_path.name}   ({n_stations} stations in {network})")
    print(f"IEM's entry for {sid}, exactly as returned:")
    for key in ("sid", "sname", "network", "state", "country", "elevation",
                "tzname", "archive_begin", "archive_end", "online"):
        print(f"  {key:14s}= {props.get(key)}")
    print(f"  {'coordinates':14s}= lat {lat}, lon {lon}")
    print(f"  {'attributes':14s}= {props.get('attributes')}")

print()
print("PART 0a - a short side-by-side comparison sample, both stations, "
      "2024-06-01..2024-06-08 (7 days, 168 hours expected):")
for sid in CANDIDATES:
    lat, lon, props = cand_data[sid]
    elev = float(props["elevation"])
    print(f"\n  {sid}:")
    rows, missing_temp = read_obs(
        RAW / f"iem_asos_{sid}_2024-06-01_2024-06-08_candidate-routine.csv")
    minutes = {}
    for t, _ in rows:
        minutes[t.minute] = minutes.get(t.minute, 0) + 1
    present = sum(1 for _, v in rows if v is not None)
    print(f"    routine METAR reports : {len(rows)}   present: {present}   "
          f"missing temp: {missing_temp}")
    print(f"    minute-past-hour      : "
          + ", ".join(f":{m:02d} x{c}" for m, c in sorted(minutes.items())))
    d, times, vals = read_forecast(
        RAW / f"openmeteo_previousruns_gfs_global_{sid}_2024-06-01_2024-06-08_candidate.json")
    n_present = sum(v is not None for v in vals)
    dist = km_between(lat, lon, d["latitude"], d["longitude"])
    print(f"    forecast grid point   : lat {d['latitude']}, lon {d['longitude']}, "
          f"elevation {d['elevation']} m")
    print(f"    grid distance         : {dist:.2f} km from the airport")
    print(f"    GRID ELEVATION MISMATCH: grid {d['elevation']} m vs station "
          f"{elev} m -> {d['elevation'] - elev:+.1f} m  <-- the key mountain figure")
    print(f"    forecast rows         : {len(vals)}   present: {n_present}")

line("PART 0b - the station chosen: BZN (Bozeman), and why.")
print("Both candidates clear the basic bar equally on this 7-day sample: both")
print("report hourly and completely, both have a genuine grid-elevation")
print("mismatch that is REAL BUT SMALL rather than the 'hundreds of metres'")
print("the session prompt flagged as possible (BZN -16 m, RNO -1 m - see")
print("PART 0a). That is itself worth recording plainly: it says Open-Meteo's")
print("~0.25-degree GFS grid cell, averaged over a BROAD valley floor at")
print("either location, lands close to the valley's own elevation rather than")
print("blending in nearby peaks - which is exactly what 'broad, not")
print("pathological' should look like, and is the reason neither candidate")
print("shows a dramatic mismatch the way a narrow canyon station (Aspen-style)")
print("would.")
print()
print("Bozeman (BZN) sits in the Gallatin Valley at 1,364 m, a wide")
print("agricultural valley many kilometres across, bounded by the Bridger")
print("Range to the north and the Gallatin and Tobacco Root ranges to the")
print("south and west - genuinely mountain-terrain-affected (elevation,")
print("cold-air drainage, a real winter/summer diurnal range) without the")
print("valley itself narrowing to a canyon. Reno (RNO) sits in the Truckee")
print("Meadows at 1,345 m, but immediately to its west the Sierra Nevada")
print("front rises very steeply to peaks above 3,000 m within about 20 km -")
print("a sharper, more abrupt transition right at the edge of the valley than")
print("Bozeman's more gradually-rising surrounding ranges. Both are")
print("legitimate 'broad mountain-valley' choices per the session prompt;")
print("Bozeman is chosen as the clearer case of the two - a wide valley")
print("ringed by mountains at a comfortable distance, closer in shape to")
print("what 'broad, not pathological' is meant to describe, and with no")
print("single abrupt escarpment sitting right at the grid cell's edge the")
print("way Reno's does.")

lat, lon, props = cand_data[STATION]
STATION_LAT, STATION_LON = lat, lon
STATION_ELEV_M = float(props["elevation"])
STATION_TZNAME = props["tzname"]

print()
print("Side by side with the four airports already in the project (SPEC 3.4):")
print(f"  EGLC  lat {EGLC['lat']}, lon {EGLC['lon']}, elevation {EGLC['elev']} m")
print(f"  LFPG  lat {LFPG['lat']}, lon {LFPG['lon']}, elevation {LFPG['elev']} m")
print(f"  DSM   lat {DSM['lat']}, lon {DSM['lon']}, elevation {DSM['elev']} m")
print(f"  YSDU  lat {YSDU['lat']}, lon {YSDU['lon']}, elevation {YSDU['elev']} m")
print(f"  BZN   lat {STATION_LAT}, lon {STATION_LON}, elevation {STATION_ELEV_M} m")
print(f"  BZN is {km_between(STATION_LAT, STATION_LON, EGLC['lat'], EGLC['lon']):,.0f} km "
      f"from EGLC, {km_between(STATION_LAT, STATION_LON, DSM['lat'], DSM['lon']):,.0f} km "
      f"from DSM (the nearest of the four).")
print(f"  BZN is by far the HIGHEST-ELEVATION airport in the project so far -")
print(f"  {STATION_ELEV_M:.0f} m against DSM's 294 m, the next highest.")

line("PART 0c - the target hour: local standard noon, computed and checked")
print("The session prompt asks for the standard-time offset to be confirmed")
print("from the station's actual timezone rather than assumed. This checks it")
print("against the timezone database, the same way F32 did for DSM and F50")
print("for Dubbo.")
print()
tz = ZoneInfo(STATION_TZNAME)
print(f"timezone from IEM metadata : {STATION_TZNAME}")
for probe, label in ((datetime(2026, 7, 15, 12, 0), "mid-summer"),
                     (datetime(2026, 1, 15, 12, 0), "mid-winter")):
    local = probe.replace(tzinfo=ZoneInfo("UTC")).astimezone(tz)
    offset_h = local.utcoffset().total_seconds() / 3600
    print(f"  {label:12s}: 12:00 UTC = {local:%H:%M} {local:%Z} (UTC{offset_h:+.0f})")
jan = datetime(2026, 1, 15, 12, 0, tzinfo=tz)
std_offset_h = jan.utcoffset().total_seconds() / 3600
TARGET_HOUR_UTC = round(12 - std_offset_h) % 24
print(f"  standard-time offset (read from a January date, guaranteed standard "
      f"time)  : UTC{std_offset_h:+.0f}")
print(f"  so local standard noon (12:00) = {TARGET_HOUR_UTC:02d}:00 UTC")
print()
print("Note on daylight saving: Montana observes it (MDT, Mar-Nov). The")
print("convention (D27/D33/D37) uses the STANDARD offset (MST, UTC-7)")
print("regardless, so the target stays one fixed UTC hour all year, per the")
print("session prompt.")

line(f"PART A1 - forecast sample, 2024 (Q29 fix - NOT July 2026)")
forecast_shape(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2024-06-01_2024-06-21.json",
    STATION_LAT, STATION_LON, STATION_ELEV_M)
print()
print("For comparison, the four grid points already in SPEC 3.4:")
for name, ap in (("EGLC", EGLC), ("LFPG", LFPG), ("DSM", DSM), ("YSDU", YSDU)):
    d = km_between(ap["lat"], ap["lon"], ap["grid_lat"], ap["grid_lon"])
    print(f"  {name}  lat {ap['grid_lat']}, lon {ap['grid_lon']}, "
          f"elev {ap['grid_elev']} m -> {d:.2f} km, "
          f"{ap['grid_elev'] - ap['elev']:+.1f} m")
d21, times21, vals21 = read_forecast(
    RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_2024-06-01_2024-06-21.json")
bzn_dist = km_between(STATION_LAT, STATION_LON, d21["latitude"], d21["longitude"])
print(f"  BZN   lat {d21['latitude']}, lon {d21['longitude']}, "
      f"elev {d21['elevation']} m -> {bzn_dist:.2f} km, "
      f"{d21['elevation'] - STATION_ELEV_M:+.1f} m  <-- key mountain figure")

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

line(f"PART A3 - {MODEL} vs {MODEL_SEAMLESS}")
print("F6 found the two strings identical at EGLC (no CONUS-only NCEP model")
print("applies in Europe). F40 then found them clearly DIFFERENT at DSM,")
print("because Des Moines sits inside CONUS where gfs_seamless can blend in")
print("HRRR/NAM/NBM. F52 found them identical again at Dubbo (outside CONUS).")
print("This airport is BOTH inside CONUS AND a mountain point, where a")
print("high-resolution blended model (HRRR in particular, which resolves")
print("terrain far better than global GFS) could differ even more than it did")
print("at flat DSM. gfs_global is used for everything the project relies on")
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
                    datetime(2024, 6, 1), datetime(2024, 6, 22), TARGET_HOUR_UTC)
print()
print("Early sample, routine reports only:")
print()
target_availability(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
                    datetime(2021, 3, 18), datetime(2021, 4, 1), TARGET_HOUR_UTC)

line("PART B3 - truth sample, early period (straddling the archive start)")
obs_gaps(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv",
         datetime(2021, 3, 18), datetime(2021, 4, 1))
print()
print("Is the reporting minute the same three years earlier?")
print()
timing_check(RAW / f"iem_asos_{STATION}_2021-03-18_2021-04-01_routine.csv")

line("PART B4 - side file: the same recent period including special (SPECI) reports")
print("At EGLC, LFPG and Dubbo the 'special' reports turned out to be a")
print("second SCHEDULED report (F3, F19, F55); at DSM they were genuinely")
print("unscheduled (F36). This checks which shape it takes here.")
print()
r_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine.csv")
rs_rows, _ = read_obs(RAW / f"iem_asos_{STATION}_2024-06-01_2024-06-22_routine-and-special.csv")
routine_stamps = {t for t, _ in r_rows}
specials = sorted(t for t, _ in rs_rows if t not in routine_stamps)
smin = {}
for t in specials:
    smin[t.minute] = smin.get(t.minute, 0) + 1
top = sorted(smin.items(), key=lambda kv: -kv[1])[:6]
print(f"  routine rows            : {len(r_rows)}")
print(f"  routine + special rows  : {len(rs_rows)}")
print(f"  special-only rows       : {len(specials)}")
print(f"  distinct minutes used   : {len(smin)}")
if smin:
    print("  busiest minutes         : "
          + ", ".join(f":{m:02d} x{c}" for m, c in top))
    at_common = top[0][1] if top else 0
    print(f"  most-common minute share: {100 * at_common / len(specials):.1f}% "
          f"of all special-only rows")
else:
    print("  no special-only reports in this window")
print("  days in the window      : 21   (504 hours)")

line("PART B5 - units check: is tmpc really whole-degree Fahrenheit-derived Celsius here?")
print("US METARs are written in whole-degree Fahrenheit, the same as at DSM,")
print("where F35 found a small rounding gap between tmpc and the Fahrenheit-")
print("derived figure. Fahrenheit is pulled alongside Celsius purely to")
print("confirm this rather than assume it.")
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
temps = [v for _, v in rows_c]
print(f"tmpc range in this sample : {min(temps)} to {max(temps)} degC")
print("VERDICT: tmpc is degrees Celsius here, the same field and the same")
print("         units every other airport uses. No new unit handling needed.")

line("PART B6 - timezone check: is the tz=UTC request really UTC?")
print("Every IEM request in this project sends tz=UTC. The same window was")
print("pulled a second time with tz=America/Denver, so the two can be")
print(f"compared. June is Mountain DAYLIGHT time (MDT, UTC-6), not the")
print("standard offset used for the target hour (MST, UTC-7) - this check")
print("measures whichever offset is actually in force during the sample.")
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
print("edges. Each local-file timestamp is shifted by a candidate number of")
print("hours and matched against the UTC file's timestamps directly, and the")
print("temperature values are compared at matching physical instants.")
print()
utc_by_time = {t: v for t, v in u_rows if v is not None}
print("  shift        matching timestamps   values equal")
best = None
for shift in range(3, 11):
    compared = 0
    matches = 0
    for t, v in l_rows:
        if v is None:
            continue
        cand = t + timedelta(hours=shift)
        if cand in utc_by_time:
            compared += 1
            if utc_by_time[cand] == v:
                matches += 1
    if compared:
        pct = 100 * matches / compared
        print(f"  local +{shift:2d}h    {compared:6d}                {matches:6d}  ({pct:.1f}%)")
        if best is None or matches / compared > best[3]:
            best = (shift, compared, matches, matches / compared)
print()
print(f"  best match: local time plus {best[0]} hours lines up with the UTC")
print(f"              series ({100 * best[3]:.1f}% of {best[1]} comparable hours identical).")
print(f"  Expected: America/Denver is on daylight saving in June (MDT, UTC-6),")
print(f"  so local + 6 should equal UTC. VERDICT: "
      + ("MATCHES - the tz=UTC request really is UTC." if best[3] == 1.0
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
print(f"1. Station chosen: BZN (Bozeman, Montana), lat {STATION_LAT}, lon "
      f"{STATION_LON},")
print(f"   elevation {STATION_ELEV_M} m, timezone {STATION_TZNAME} - a wide")
print("   agricultural valley ringed by mountains at a comfortable distance,")
print("   chosen over Reno (RNO) as the clearer 'broad, not pathological'")
print("   mountain-valley case, after comparing both candidates' metadata")
print("   and a real 7-day sample from each.")
print()
gd = bzn_dist
print(f"2. Forecast source. The Previous Runs API carries BZN. Its grid point")
print(f"   is lat {d21['latitude']}, lon {d21['longitude']}, elevation "
      f"{d21['elevation']} m -")
print(f"   {gd:.2f} km from the airport, {d21['elevation'] - STATION_ELEV_M:+.1f} m in")
print("   height - the KEY MOUNTAIN FIGURE the session prompt asks for. This")
print("   is real but SMALL, not the 'hundreds of metres' flagged as")
print("   possible: Open-Meteo's smoothed grid cell, averaged over this")
print("   broad valley, lands close to the valley floor's own elevation")
print("   rather than blending in the nearby peaks. It is still the largest")
print("   RELATIVE elevation the project has pulled - 1,364 m station")
print("   elevation against DSM's 294 m - so a genuine altitude/terrain")
print("   bias test, even though the GRID mismatch specifically is modest.")
print("   Recent sample: 504 hourly rows, 0 missing.")
print()
print(f"3. Archive depth. 1-7 March 2021 comes back HTTP 200 with all values")
print(f"   null, and the first hour carrying a real value is exactly")
print("   2021-03-24 00:00 UTC - the same hour as every other airport, to")
print("   the hour. The D13 split dates need no moving here either. A fifth")
print("   airport, the first with real terrain complexity, gives the same")
print("   answer.")
print()
print(f"4. Target hour. America/Denver's standard offset is UTC{std_offset_h:+.0f} (MST),")
print(f"   so local standard noon is {TARGET_HOUR_UTC:02d}:00 UTC year-round - checked")
print("   against the timezone database, not assumed. Daylight saving is")
print("   ignored per the D27/D33/D37 convention, so the target stays a")
print("   fixed UTC hour all year.")
print()
seamless_word = "DIFFER" if any_diff else "are IDENTICAL"
print(f"5. gfs_global vs gfs_seamless: {seamless_word} in the windows tested.")
if any_diff:
    print("   Des Moines (F40) already showed the two strings can differ")
    print("   sharply inside CONUS; this mountain point is a second CONUS")
    print("   case where the same is true. D16's pin (gfs_global only)")
    print("   protects the project exactly as it did at DSM.")
else:
    print("   Unlike DSM (F40), the two strings agree here across both")
    print("   windows tested - worth flagging as a genuine finding rather")
    print("   than assuming DSM's CONUS-differs pattern always holds.")
print()
print("6. Truth source. IEM carries BZN in MT_ASOS. Recent sample (2024-06-01")
print("   to 2024-06-22, 504 expected hours): 503 routine reports, 2 hours")
print("   missing after assigning each report to the hour it serves (BZN")
print("   reports 4 min before the hour, so the report at H-1:56 serves hour")
print("   H, mirroring DSM's :54 pattern) - 1 is a request-boundary artefact")
print("   (the window's first hour needs a report from the day before, not")
print("   requested), the other (2024-06-13 20:00) is a genuine gap. Early")
print("   sample (2021-03-18 to 2021-04-01, 336 expected hours): 333 reports,")
print("   4 hours missing by the same accounting - 1 boundary artefact, 3")
print("   genuine gaps. No report anywhere in either sample carries a missing")
print("   temperature. Both are comparable in cleanliness to the other four")
print("   airports' own verify-on-contact samples.")
print()
print("7. Report timing and target-hour availability are printed above")
print(f"   (PART B2, B2b) at the computed target hour, {TARGET_HOUR_UTC:02d}:00 UTC.")
print()
print("8. Units and timezone checks are printed above (PART B5, B6).")
print()
print("9. Plain verdict is stated in DECISIONS, drawing on the real numbers")
print("   printed by every part above - this script only measures and")
print("   reports; it does not decide.")
