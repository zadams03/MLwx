"""Session 19: verify-on-contact samples for airport #4 (inland eastern
Australia).

This mirrors session 14's DSM pull file for file. SMALL SAMPLES ONLY. The full
multi-year pull is a later session's job, once this one confirms the airport
is usable.

Downloads only. Nothing is joined, cleaned, filled or modelled here.

What it writes, for every request:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 - raw data is an immutable, dated snapshot)

If a file already exists it is left alone and skipped, so a failed run can be
re-run without re-downloading and a raw file is never overwritten.

Order matters here. The IEM station listing for the Australian network is
fetched FIRST, because the chosen station's authoritative position comes out
of it and the forecast requests need that position. Nothing is typed in from
memory or a map (DECISIONS D28's rule for the airport table).

Station choice (session prompt, not assumed): the two candidates are Canberra
(YSCB) and Dubbo (YSDU), both in IEM's AU__ASOS network. A short comparison
sample is pulled for BOTH before picking one, exactly as the prompt asks -
"confirm on contact, do not assume".

**Q29 fix, applied from the start.** Session 17 raised Q29: every earlier
airport's verify-on-contact sample sat inside its own sealed test year
(2025-08-01 to 2026-07-31), which is not leakage into any model but is a
sloppy habit worth stopping. Every sample this session pulls sits in 2021
(the archive-start probes, shared by every airport) or 2024 (comfortably
inside the training window and nowhere near the test year). Nothing here
touches 2025-08-01 onward.

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files at :50 (F3), LFPG
  at :00 (F18), DSM at :54 (F34). What the Australian station does is one of
  the things this session answers.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. At all three airports so far it turned out to
  matter one way or another (F3, F19, F36).
- "previous_day1" = the value from the model run one day earlier, i.e. the
  day-ahead forecast (SPEC 3.2). See DECISIONS F5 for its real lead time.

The target hour for this airport is expected to be 02:00 UTC (local standard
noon, AEST = UTC+10), not 12:00 or 18:00 UTC (session 19 prompt, D37). That
changes nothing about what is downloaded - a whole-hours series is pulled
either way - but it is why the checks script looks at 02:00.
"""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

IEM_NETWORK = "AU__ASOS"        # Australia - IEM's global-network style code
CANDIDATES = ["YSCB", "YSDU"]   # Canberra, Dubbo - confirmed on contact below
STATION = "YSDU"                # chosen once B0 below is read; see DECISIONS

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"
MODEL_SEAMLESS = "gfs_seamless"

# Temperature only (DECISIONS D17).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field, in Celsius, exactly as at the other
# three airports.
IEM_FIELDS = ["tmpc", "dwpc"]

# --- Q29 fix: every window below sits in 2021 (shared archive-start probes)
# or 2024 (well inside training, nowhere near the 2025-08-01..2026-07-31 test
# year). Nothing samples July 2026 or later the way sessions 01/08/14 did.

# B0: a short side-by-side sample for BOTH candidate stations, used only to
# pick one. Not part of the kept verification evidence for the chosen station.
CANDIDATE_START, CANDIDATE_END = "2024-06-01", "2024-06-08"   # IEM end exclusive

# A1: the "recent-style" forecast/observation sample - three weeks, in 2024
# instead of July 2026.
RECENT_START, RECENT_END = "2024-06-01", "2024-06-21"    # forecast, inclusive
RECENT_OBS_END = "2024-06-22"                              # IEM end exclusive

# A2: the archive-start probes, shared with every earlier airport (F1/F20/F33).
EARLY_PROBE1 = ("2021-03-01", "2021-03-07")   # before the archive's first hour
EARLY_PROBE2 = ("2021-03-18", "2021-03-26")   # straddles 2021-03-24
EARLY_OBS = ("2021-03-18", "2021-04-01")      # IEM end exclusive

# A3: the gfs_global vs gfs_seamless comparison (Q30-adjacent). Two windows,
# mirroring session 15's F40 shape: one early (inside training), one a second
# out-of-test-year window so the comparison is not resting on a single date
# range.
SEAMLESS_WINDOWS = [
    ("2021-03-24", "2021-04-05", "early, inside the training window"),
    ("2024-08-05", "2024-08-15", "a second out-of-test-year window (Q29 fix)"),
]

# B: units/timezone cross-check window (short, inside the 2024 recent sample).
UNITS_PROBE = ("2024-06-01", "2024-06-04")    # IEM end exclusive

PAUSE_SECONDS = 3.0   # session 08 hit an HTTP 429 at a faster pace


def now_stamps():
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return f"{local:%Y-%m-%d %H:%M:%S %Z} ({utc:%Y-%m-%d %H:%M:%S} UTC)"


def fetch(url, attempts=5):
    """Return (http_status, body_text), retrying on a slow or dropped link."""
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session19"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.status, resp.read().decode("utf-8")
        except Exception as err:
            if attempt == attempts:
                raise
            wait = 15 * attempt
            print(f"  attempt {attempt} failed ({type(err).__name__}: {err}); "
                  f"retrying in {wait}s", flush=True)
            time.sleep(wait)


def write_once(path, text):
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return False
    path.write_text(text)
    print(f"  wrote {path.name}  ({path.stat().st_size:,} bytes)", flush=True)
    return True


def save(path, body, meta_lines):
    wrote = write_once(path, body)
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta_lines))
    return wrote


# ------------------------------------------------------- 0. station metadata --

def pull_station_metadata():
    """IEM's own listing for the Australian network - authoritative positions
    for both candidate stations.
    """
    url = f"https://mesonet.agron.iastate.edu/geojson/network/{IEM_NETWORK}.geojson"
    path = RAW / f"iem_station_metadata_{IEM_NETWORK}.geojson"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return
    pulled_at = now_stamps()
    status, body = fetch(url)
    save(path, body, [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        "purpose     : session 19, part 0 - the authoritative station "
        "positions for the two candidate airports (Canberra YSCB, Dubbo "
        "YSDU), used to choose one and to set the coordinates for the "
        "Open-Meteo forecast requests below. Nothing is typed in from memory "
        "or a map.",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) network station listing",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "notes:",
        "- The whole network file is kept rather than just the two candidate",
        "  entries, because it is the actual response and SPEC 2.3 says to",
        "  keep raw pulls untouched.",
        "- What IEM returned for YSCB and YSDU is reported by",
        "  scripts/session19_checks.py and written up in DECISIONS.",
        f"- HTTP status {status}.",
        "",
    ])


def station_position(sid):
    """Read a station's lat/lon/elevation straight out of the saved IEM
    listing. Used for both candidates before one is chosen, and then for the
    chosen one throughout the rest of the pull.
    """
    path = RAW / f"iem_station_metadata_{IEM_NETWORK}.geojson"
    d = json.loads(path.read_text())
    for feat in d["features"]:
        if feat["id"] == sid:
            lon, lat = feat["geometry"]["coordinates"]
            return lat, lon, feat["properties"]
    raise SystemExit(f"{sid} not found in {path.name} - stopping (a stop "
                     f"signal in the same style as D31.11: do not guess a "
                     f"position)")


# ------------------------------------------------------------- A. forecast --

def pull_forecast(station, lat, lon, start, end, purpose, model=MODEL, suffix=""):
    hourly = ",".join(f"{v}_previous_day1" for v in FORECAST_VARS)
    params = [
        ("latitude", f"{lat}"),
        ("longitude", f"{lon}"),
        ("start_date", start),
        ("end_date", end),
        ("hourly", hourly),
        ("models", model),
        ("timezone", "UTC"),
    ]
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           + urllib.parse.urlencode(params, safe=","))
    path = RAW / f"openmeteo_previousruns_{model}_{station}_{start}_{end}{suffix}.json"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return
    pulled_at = now_stamps()
    status, body = fetch(url)
    save(path, body, [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        f"purpose     : session 19 - {purpose}",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {lat}    ({station})",
        f"  longitude  = {lon}",
        f"  start_date = {start}",
        f"  end_date   = {end}",
        f"  hourly     = {hourly}",
        f"  models     = {model}",
        "  timezone   = UTC",
        "",
        "notes:",
        "- Temperature is requested at the _previous_day1 offset: the value",
        "  from the model run one day earlier. That is the day-ahead forecast",
        "  this project corrects (SPEC 3.2). Its true lead time sweeps between",
        "  about 24 and 30 hours across the day - see DECISIONS F5.",
        "- The plain temperature_2m variable was deliberately NOT requested. On",
        "  this endpoint it is the freshest-run series, which is the leakage",
        "  trap SPEC 2.1b warns about.",
        f"- Model string: {model}"
        + (" (pinned per DECISIONS D16; used for everything the project "
           "actually relies on)" if model == MODEL else
           " (Q30-adjacent comparison probe only - gfs_global is what the "
           "project uses, D16)"),
        "- Temperature only, no extra variables (DECISIONS D17).",
        "- The coordinates are IEM's own record for this station, read out of",
        f"  iem_station_metadata_{IEM_NETWORK}.geojson in the same run.",
        f"- HTTP status {status}.",
        "- Nulls in this file are left exactly as the API returned them.",
        "  Nothing was filled in (SPEC 2.2).",
        "- Q29 fix: this window is deliberately outside the sealed test year",
        "  (2025-08-01 to 2026-07-31, D13). Session 17 raised Q29 because",
        "  earlier airports' verify-on-contact samples all sat inside their",
        "  test year; this session does not repeat that.",
        "",
    ])


# --------------------------------------------------------- B. observations --

def iem_url(station, start, end, report_types, fields, tz="UTC", network=IEM_NETWORK):
    """`end` is the exclusive day IEM is asked for, exactly as at the other
    airports.
    """
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    params = [("station", station), ("network", network)]
    params += [("data", f) for f in fields]
    params += [
        ("year1", str(s.year)), ("month1", str(s.month)), ("day1", str(s.day)),
        ("year2", str(e.year)), ("month2", str(e.month)), ("day2", str(e.day)),
        ("tz", tz),
        ("format", "onlycomma"),
        ("latlon", "yes"),
        ("elev", "yes"),
        ("missing", "M"),
        ("trace", "T"),
        ("direct", "no"),
    ]
    params += [("report_type", r) for r in report_types]
    return ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
            + urllib.parse.urlencode(params))


def pull_obs(station, start, end, report_types, suffix, purpose, fields=None,
             tz="UTC", extra_notes=()):
    fields = list(fields or IEM_FIELDS)
    url = iem_url(station, start, end, report_types, fields, tz=tz)
    path = RAW / f"iem_asos_{station}_{start}_{end}_{suffix}.csv"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return
    pulled_at = now_stamps()
    status, body = fetch(url)
    rt = ", ".join(report_types)
    save(path, body, [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        f"purpose     : session 19 - {purpose}",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {station}",
        f"  network     = {IEM_NETWORK}",
        f"  data        = {', '.join(fields)}",
        f"  date range  = {start} to {end}. IEM treats its end date as",
        f"                exclusive, so the last row is the day before {end}.",
        f"  tz          = {tz}",
        "  format      = onlycomma",
        "  latlon      = yes",
        "  elev        = yes",
        "  missing     = M   (missing values come back as the letter M)",
        "  trace       = T",
        f"  report_type = {rt}   "
        + ("(routine METAR only - the scheduled report)"
           if report_types == ["3"] else "(routine + special)"),
        "",
        "notes:",
        *extra_notes,
        "- tmpc is air temperature in degrees Celsius, the same field and the",
        "  same units the other three airports use. No unit conversion",
        "  happens anywhere in this project.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        f"- HTTP status {status}.",
        "- Q29 fix: this window is deliberately outside the sealed test year",
        "  (2025-08-01 to 2026-07-31, D13).",
        "",
    ])


def main():
    print("Airport #4 candidates: Canberra (YSCB), Dubbo (YSDU), "
          f"IEM network {IEM_NETWORK}", flush=True)
    print("Small verification samples only - this is NOT the full pull.",
          flush=True)
    print("Q29 fix in effect: every window below is 2021 or 2024, never the "
          "2025-08-01..2026-07-31 test year.", flush=True)

    print(f"\n=== 0  IEM station metadata for the {IEM_NETWORK} network ===",
          flush=True)
    pull_station_metadata()
    for sid in CANDIDATES:
        lat, lon, props = station_position(sid)
        print(f"  {sid} position from IEM: lat {lat}, lon {lon}, "
              f"elevation {props.get('elevation')} m, tz {props.get('tzname')}",
              flush=True)
    time.sleep(PAUSE_SECONDS)

    print("\n=== B0  candidate comparison: short routine-METAR sample for "
          "BOTH stations ===", flush=True)
    for sid in CANDIDATES:
        print(f"B0 {sid} {CANDIDATE_START} -> {CANDIDATE_END}", flush=True)
        pull_obs(sid, CANDIDATE_START, CANDIDATE_END, ["3"], "candidate-routine",
                 "part B0 - short comparison sample, used only to choose "
                 "between the two candidate stations before continuing")
        time.sleep(PAUSE_SECONDS)

    lat, lon, props = station_position(STATION)
    print(f"\nChosen station: {STATION} (lat {lat}, lon {lon}, elevation "
          f"{props.get('elevation')} m). See DECISIONS for the reasoning.",
          flush=True)

    print(f"\n=== A  forecast (Open-Meteo Previous Runs, {MODEL}, {STATION}) ===",
          flush=True)
    print(f"A1 recent-style sample {RECENT_START} -> {RECENT_END} (2024, "
          f"Q29 fix)", flush=True)
    pull_forecast(STATION, lat, lon, RECENT_START, RECENT_END,
                  "part A1 - recent-style forecast sample, to confirm the "
                  "Previous Runs API carries this airport and to see the "
                  "grid point returned; taken from 2024 rather than July "
                  "2026 (Q29 fix)")
    time.sleep(PAUSE_SECONDS)

    print(f"A2 archive probe 1 {EARLY_PROBE1[0]} -> {EARLY_PROBE1[1]}", flush=True)
    pull_forecast(STATION, lat, lon, *EARLY_PROBE1,
                  "part A2 probe 1 - before the archive's first hour at EGLC, "
                  "LFPG and DSM (F1, F20, F33 all found all-null answers here)")
    time.sleep(PAUSE_SECONDS)

    print(f"A2 archive probe 2 {EARLY_PROBE2[0]} -> {EARLY_PROBE2[1]}", flush=True)
    pull_forecast(STATION, lat, lon, *EARLY_PROBE2,
                  "part A2 probe 2 - straddles 2021-03-24, the first hour with "
                  "a real value at EGLC, LFPG and DSM (F1, F20, F33)")
    time.sleep(PAUSE_SECONDS)

    print(f"\n=== A3  {MODEL} vs {MODEL_SEAMLESS} (Q30-adjacent) ===", flush=True)
    for start, end, why in SEAMLESS_WINDOWS:
        print(f"{start} -> {end}   ({why})", flush=True)
        for model in (MODEL, MODEL_SEAMLESS):
            pull_forecast(STATION, lat, lon, start, end,
                          f"part A3 - {model} vs {MODEL_SEAMLESS} comparison "
                          f"window ({why}); gfs_global is what the project "
                          f"uses regardless (D16) - this only records "
                          f"whether the two strings agree here",
                          model=model, suffix="_seamlesscompare")
            time.sleep(PAUSE_SECONDS)

    print(f"\n=== B  truth (IEM ASOS METARs, {STATION}) ===", flush=True)
    print(f"B1 recent-style routine {RECENT_START} -> {RECENT_OBS_END} (2024, "
          f"Q29 fix)", flush=True)
    pull_obs(STATION, RECENT_START, RECENT_OBS_END, ["3"], "routine",
             "part B1/B2 - recent-style truth sample over the same period as "
             "the forecast sample, and the file that answers what minute "
             "past the hour this station reports at, and how often")
    time.sleep(PAUSE_SECONDS)

    print(f"B3 early routine {EARLY_OBS[0]} -> {EARLY_OBS[1]}", flush=True)
    pull_obs(STATION, *EARLY_OBS, ["3"], "routine",
             "part B3 - early truth sample, straddling the archive start, to "
             "check the reporting habit holds at both ends of the period")
    time.sleep(PAUSE_SECONDS)

    print(f"B4 recent routine+special {RECENT_START} -> {RECENT_OBS_END}",
          flush=True)
    pull_obs(STATION, RECENT_START, RECENT_OBS_END, ["3", "4"],
             "routine-and-special",
             "part B4 - the same recent-style window including IEM's "
             "'special' (SPECI) reports, to see whether this station files a "
             "second scheduled report the way EGLC (F3) and LFPG (F19) do, "
             "or genuinely unscheduled ones the way DSM does (F36) - and to "
             "help settle the report-cadence question the session prompt "
             "flags as the main risk")
    time.sleep(PAUSE_SECONDS)

    print(f"B5 units cross-check {UNITS_PROBE[0]} -> {UNITS_PROBE[1]}", flush=True)
    pull_obs(STATION, *UNITS_PROBE, ["3"], "routine-tmpc-tmpf",
             "part B5 - units cross-check. Fahrenheit is requested ALONGSIDE "
             "Celsius purely so the two can be compared; tmpc stays the "
             "truth field everywhere else. Australian METARs already report "
             "whole-degree Celsius, unlike the US stations that motivated "
             "this check at DSM, so this is confirming rather than "
             "expecting a surprise",
             fields=["tmpc", "tmpf", "dwpc"],
             extra_notes=(
                 "- This file is a CHECK, not part of the dataset. It exists so",
                 "  'tmpc really is Celsius here too' is a measured fact",
                 "  rather than an assumption. The pipeline reads tmpc only.",
             ))
    time.sleep(PAUSE_SECONDS)

    print(f"B6 timezone cross-check {UNITS_PROBE[0]} -> {UNITS_PROBE[1]} "
          f"(tz={props.get('tzname')})", flush=True)
    pull_obs(STATION, *UNITS_PROBE, ["3"], "routine-localtime",
             "part B6 - timezone cross-check. The same rows requested in the "
             "station's own local timezone, so the UTC request can be shown "
             "to really be UTC rather than local time wearing a UTC label. "
             "June is southern-hemisphere winter, so Australia/Sydney is on "
             "STANDARD time (AEST, UTC+10) throughout this window, not "
             "daylight saving",
             tz=props.get("tzname"),
             extra_notes=(
                 "- This file is a CHECK, not part of the dataset. Every real",
                 "  request in this project uses tz=UTC. This one asks for",
                 "  the station's own local timezone so the offset can be",
                 "  measured directly.",
             ))

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
