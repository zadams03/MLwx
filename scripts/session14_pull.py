"""Session 14: verify-on-contact samples for DSM (Des Moines, Iowa).

This is the stage-3-airport opening pull, and it mirrors session 08's CDG pull
file for file. SMALL SAMPLES ONLY. The full multi-year pull is a later
session's job (session 14 scope).

Downloads only. Nothing is joined, cleaned, filled or modelled here.

What it writes, for every request:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 - raw data is an immutable, dated snapshot)

If a file already exists it is left alone and skipped, so a failed run can be
re-run without re-downloading and a raw file is never overwritten.

Order matters here. The IEM station listing for the Iowa network is fetched
FIRST, because DSM's authoritative position comes out of it and the forecast
requests need that position. Nothing is typed in from memory or a map
(DECISIONS D28's rule for the airport table).

Terms used here:
- "routine METAR" = the scheduled airport report. EGLC files at :50, LFPG at
  :00. What DSM does is one of the things this session answers, because the
  pairing rule D14 has a 15-minute tolerance around the target hour.
- IEM's "special" (SPECI) report type = an extra report, normally filed when
  the weather changes fast. At both EGLC (F3) and LFPG (F19) it turned out to
  be a second scheduled report, so it is worth a look here too.
- "previous_day1" = the value from the model run one day earlier, i.e. the
  day-ahead forecast (SPEC 3.2). See DECISIONS F5 for its real lead time.

The target hour for DSM is 18:00 UTC, not 12:00 UTC (DECISIONS D33). That
changes nothing about what is downloaded - a whole-hours series is pulled
either way - but it is why the checks script looks at 18:00.
"""

import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

STATION = "DSM"                 # IEM station id (Des Moines International)
IEM_NETWORK = "IA_ASOS"         # Iowa - IEM's home network

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# Temperature only (DECISIONS D17).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field, in Celsius, exactly as at EGLC and LFPG.
IEM_FIELDS = ["tmpc", "dwpc"]

# The same windows session 08 used at LFPG, so the two verification sessions
# line up sample for sample.
RECENT_START, RECENT_END = "2026-07-01", "2026-07-21"   # forecast, inclusive
RECENT_OBS_END = "2026-07-22"                            # IEM end is exclusive
EARLY_PROBE1 = ("2021-03-01", "2021-03-07")   # before the archive's first hour
EARLY_PROBE2 = ("2021-03-18", "2021-03-26")   # straddles 2021-03-24
EARLY_OBS = ("2021-03-18", "2021-04-01")      # IEM end exclusive

# One short window for the two US-specific checks the session prompt asks for:
# that the temperature field and its units need no new handling, and that the
# timestamps really are UTC.
UNITS_PROBE = ("2026-07-01", "2026-07-04")    # IEM end exclusive

PAUSE_SECONDS = 3.0   # session 08 hit an HTTP 429 at a faster pace


def now_stamps():
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return f"{local:%Y-%m-%d %H:%M:%S %Z} ({utc:%Y-%m-%d %H:%M:%S} UTC)"


def fetch(url, attempts=5):
    """Return (http_status, body_text), retrying on a slow or dropped link."""
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session14"})
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
    """IEM's own listing for the Iowa network - DSM's authoritative position.

    Same call session 08 made for France and session 10 for the United
    Kingdom, pointed at Iowa.
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
        "purpose     : session 14, part 0 - the authoritative station position",
        "              for DSM (Des Moines, Iowa), used to set the coordinates",
        "              for the Open-Meteo forecast requests below. Nothing is",
        "              typed in from memory or a map.",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) network station listing",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "notes:",
        "- The whole network file is kept rather than just the DSM entry,",
        "  because it is the actual response and SPEC 2.3 says to keep raw",
        "  pulls untouched.",
        "- What IEM returned for DSM is reported by",
        "  scripts/session14_checks.py and written up in DECISIONS.",
        f"- HTTP status {status}.",
        "",
    ])


def dsm_position():
    """Read DSM's lat/lon/elevation straight out of the saved IEM listing."""
    path = RAW / f"iem_station_metadata_{IEM_NETWORK}.geojson"
    d = json.loads(path.read_text())
    for feat in d["features"]:
        if feat["id"] == STATION:
            lon, lat = feat["geometry"]["coordinates"]
            return lat, lon, feat["properties"]
    raise SystemExit(f"{STATION} not found in {path.name} - stopping (D31.11 "
                     f"style stop signal: do not guess a position)")


# ------------------------------------------------------------- A. forecast --

def pull_forecast(lat, lon, start, end, purpose):
    hourly = ",".join(f"{v}_previous_day1" for v in FORECAST_VARS)
    params = [
        ("latitude", f"{lat}"),
        ("longitude", f"{lon}"),
        ("start_date", start),
        ("end_date", end),
        ("hourly", hourly),
        ("models", MODEL),
        ("timezone", "UTC"),
    ]
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           + urllib.parse.urlencode(params, safe=","))
    path = RAW / f"openmeteo_previousruns_{MODEL}_{STATION}_{start}_{end}.json"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return
    pulled_at = now_stamps()
    status, body = fetch(url)
    save(path, body, [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        f"purpose     : session 14 - {purpose}",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {lat}    (DSM, Des Moines International, Iowa)",
        f"  longitude  = {lon}",
        f"  start_date = {start}",
        f"  end_date   = {end}",
        f"  hourly     = {hourly}",
        f"  models     = {MODEL}",
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
        f"- Model string pinned to {MODEL} rather than gfs_seamless "
        "(DECISIONS D16).",
        "- Temperature only, no extra variables (DECISIONS D17).",
        "- The coordinates are IEM's own record for DSM, read out of",
        f"  iem_station_metadata_{IEM_NETWORK}.geojson in the same run.",
        f"- HTTP status {status}.",
        "- Nulls in this file are left exactly as the API returned them.",
        "  Nothing was filled in (SPEC 2.2).",
        "",
    ])


# --------------------------------------------------------- B. observations --

def iem_url(start, end, report_types, fields, tz="UTC", network=IEM_NETWORK):
    """`end` is the exclusive day IEM is asked for, exactly as at LFPG."""
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    params = [("station", STATION), ("network", network)]
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


def pull_obs(start, end, report_types, suffix, purpose, fields=None,
             tz="UTC", extra_notes=()):
    fields = list(fields or IEM_FIELDS)
    url = iem_url(start, end, report_types, fields, tz=tz)
    path = RAW / f"iem_asos_{STATION}_{start}_{end}_{suffix}.csv"
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
        f"purpose     : session 14 - {purpose}",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {STATION}   (Des Moines International, Iowa)",
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
        "  same units stage 1 and stage 2 used at EGLC and LFPG. No unit",
        "  conversion happens anywhere in this project.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        f"- HTTP status {status}.",
        "",
    ])


def main():
    print(f"Airport: {STATION} (Des Moines International, Iowa), "
          f"IEM network {IEM_NETWORK}", flush=True)
    print("Small verification samples only - this is NOT the full pull.",
          flush=True)

    print(f"\n=== 0  IEM station metadata for the {IEM_NETWORK} network ===",
          flush=True)
    pull_station_metadata()
    lat, lon, props = dsm_position()
    print(f"  DSM position from IEM: lat {lat}, lon {lon}, "
          f"elevation {props.get('elevation')} m, tz {props.get('tzname')}",
          flush=True)
    time.sleep(PAUSE_SECONDS)

    print(f"\n=== A  forecast (Open-Meteo Previous Runs, {MODEL}, {STATION}) ===",
          flush=True)
    print(f"A1 recent sample {RECENT_START} -> {RECENT_END}", flush=True)
    pull_forecast(lat, lon, RECENT_START, RECENT_END,
                  "part A1 - recent forecast sample, to confirm the Previous "
                  "Runs API carries DSM and to see the grid point returned")
    time.sleep(PAUSE_SECONDS)

    print(f"A2 archive probe 1 {EARLY_PROBE1[0]} -> {EARLY_PROBE1[1]}", flush=True)
    pull_forecast(lat, lon, *EARLY_PROBE1,
                  "part A2 probe 1 - before the archive's first hour at EGLC "
                  "and LFPG (F1, F20 both found all-null answers here)")
    time.sleep(PAUSE_SECONDS)

    print(f"A2 archive probe 2 {EARLY_PROBE2[0]} -> {EARLY_PROBE2[1]}", flush=True)
    pull_forecast(lat, lon, *EARLY_PROBE2,
                  "part A2 probe 2 - straddles 2021-03-24, the first hour with "
                  "a real value at both EGLC (F1) and LFPG (F20)")
    time.sleep(PAUSE_SECONDS)

    print(f"\n=== B  truth (IEM ASOS METARs, {STATION}) ===", flush=True)
    print(f"B1 recent routine {RECENT_START} -> {RECENT_OBS_END}", flush=True)
    pull_obs(RECENT_START, RECENT_OBS_END, ["3"], "routine",
             "part B1/B2 - recent truth sample over the same period as the "
             "forecast sample, and the file that answers what minute past the "
             "hour DSM reports at")
    time.sleep(PAUSE_SECONDS)

    print(f"B3 early routine {EARLY_OBS[0]} -> {EARLY_OBS[1]}", flush=True)
    pull_obs(*EARLY_OBS, ["3"], "routine",
             "part B3 - early truth sample, five years before the recent one, "
             "to check the reporting habit holds at both ends of the period")
    time.sleep(PAUSE_SECONDS)

    print(f"B4 recent routine+special {RECENT_START} -> {RECENT_OBS_END}",
          flush=True)
    pull_obs(RECENT_START, RECENT_OBS_END, ["3", "4"], "routine-and-special",
             "part B4 - the same recent window including IEM's 'special' "
             "(SPECI) reports, to see whether DSM files a second scheduled "
             "report the way EGLC (F3) and LFPG (F19) do")
    time.sleep(PAUSE_SECONDS)

    print(f"B5 units cross-check {UNITS_PROBE[0]} -> {UNITS_PROBE[1]}", flush=True)
    pull_obs(*UNITS_PROBE, ["3"], "routine-tmpc-tmpf",
             "part B5 - units cross-check. Fahrenheit is requested ALONGSIDE "
             "Celsius purely so the two can be compared; tmpc stays the truth "
             "field everywhere else",
             fields=["tmpc", "tmpf", "dwpc"],
             extra_notes=(
                 "- This file is a CHECK, not part of the dataset. It exists so",
                 "  'tmpc really is Celsius at a US station' is a measured fact",
                 "  rather than an assumption. The pipeline reads tmpc only.",
             ))
    time.sleep(PAUSE_SECONDS)

    print(f"B6 timezone cross-check {UNITS_PROBE[0]} -> {UNITS_PROBE[1]} "
          f"(tz=America/Chicago)", flush=True)
    pull_obs(*UNITS_PROBE, ["3"], "routine-localtime",
             "part B6 - timezone cross-check. The same rows requested in DSM's "
             "own local timezone, so the UTC request can be shown to really be "
             "UTC rather than local time wearing a UTC label",
             tz="America/Chicago",
             extra_notes=(
                 "- This file is a CHECK, not part of the dataset. Every real",
                 "  request in this project uses tz=UTC. This one asks for",
                 "  America/Chicago so the offset between the two can be",
                 "  measured at a US station, where it matters and where it did",
                 "  not need checking in Europe.",
             ))
    time.sleep(PAUSE_SECONDS)

    print(f"B7 tz spelling cross-check {UNITS_PROBE[0]} -> {UNITS_PROBE[1]} "
          f"(tz=Etc/UTC)", flush=True)
    pull_obs(*UNITS_PROBE, ["3"], "routine-etc-utc",
             "part B7 - tz spelling cross-check. The session 14 prompt "
             "describes the existing request approach as tz=Etc/UTC, while "
             "every request this project has actually made uses tz=UTC. This "
             "pulls the same rows the other way so the two spellings can be "
             "compared row by row",
             tz="Etc/UTC",
             extra_notes=(
                 "- This file is a CHECK, not part of the dataset. It settles a",
                 "  wording difference between the session prompt and the",
                 "  project's own request shape; it changes nothing.",
             ))

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
