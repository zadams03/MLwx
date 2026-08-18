"""Session 15 part B: pull the full history for both sources at DSM.

This is session 03b's and session 10's pull, pointed at Des Moines. Downloads
only. Nothing is joined, cleaned, filled, or modelled here.

The same period, the same yearly chunks, the same model string (`gfs_global`,
D16), the same temperature-only forecast variable (D17) and the same IEM
request shape as the EGLC and LFPG pulls. What differs is the station, its
coordinates, and one extra job: settling Q27.

What it writes, for every chunk:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 - raw data is an immutable, dated snapshot)

If a file already exists it is left alone and skipped. A failed run can then be
re-run without re-downloading, and an existing raw file is never overwritten.

Q27 (part B2): `gfs_global` versus `gfs_seamless` at DSM. F6 proved the two
return identical data at EGLC, but its argument was location-specific - it
rested on no CONUS-only NCEP model being able to apply in London. Des Moines is
inside CONUS, so that argument does not carry and the comparison has to be made
rather than assumed. The actual pull uses `gfs_global` regardless; D16 pins it.

Two windows are compared, and neither of them touches the sealed test window:
- an early window inside the training period, 2021-03-24 to 2021-04-05, which
  is exactly the early window F6 used at EGLC;
- a recent window that sits AFTER the project period ends, 2026-08-05 to
  2026-08-15. D13 does not use any data after 2026-07-31, so this window is
  outside both the training and the test sets. A recent window is the one that
  matters for Q27, because a seamless blend is a live, current-behaviour thing
  - but F6's own recent window (July 2026) now falls inside DSM's sealed test
  year, so it is deliberately not used.

Terms used here:
- "chunk" = one calendar year (or the part-year at each end of the period).
  Yearly chunks mean a failure part-way through only costs one year.
- "previous_day1" = the value from the model run one day earlier, i.e. the
  day-ahead forecast (SPEC 3.2). See DECISIONS F5 for what its lead time
  really is.
"""

import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

# The whole period the project uses: training window plus the sealed test
# window (SPEC 4.3, DECISIONS D13). The same dates as stages 1 and 2 - DSM's
# forecast archive begins on the same hour as EGLC's and LFPG's (DECISIONS
# F33), so nothing moves.
PERIOD_START = "2021-03-24"
PERIOD_END = "2026-07-31"

# DSM, Des Moines International, Iowa (SPEC 3.4). The position is IEM's own,
# from the IA_ASOS station metadata pulled in session 14 (DECISIONS F31), not
# an approximate figure from elsewhere.
STATION = "DSM"
LAT = "41.534"
LON = "-93.6531"

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# The other string, compared but never used for the pull (Q27).
MODEL_SEAMLESS = "gfs_seamless"

# Temperature only (DECISIONS D17, which applies per airport).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field. Dew point comes along in the same
# response and is kept for the record.
IEM_FIELDS = ["tmpc", "dwpc"]

# One (start, end) pair per chunk. Both ends inclusive. Identical to the
# stage 1 and stage 2 chunking, so all three airports' raw files line up file
# for file.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

# Q27's two comparison windows. Neither touches the sealed test year.
Q27_WINDOWS = [
    ("2021-03-24", "2021-04-05", "early, inside the training window; F6's own "
                                 "early window at EGLC"),
    ("2026-08-05", "2026-08-15", "recent, AFTER the project period ends "
                                 "2026-07-31, so outside training and test "
                                 "alike (D13)"),
]

PAUSE_SECONDS = 3.0  # gentle on both services; session 08 hit an HTTP 429 at
                     # a faster pace


def now_stamps():
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return (f"{local:%Y-%m-%d %H:%M:%S %Z} "
            f"({utc:%Y-%m-%d %H:%M:%S} UTC)")


def fetch(url, attempts=5):
    """Return (http_status, body_text). Retries on a slow or dropped
    connection, waiting longer each time. A chunk that still fails after all
    attempts raises, and the run stops - re-running picks up where it left
    off, because finished chunks are skipped."""
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session15"})
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
    """Write the file only if it is not already there (never overwrite raw)."""
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return False
    path.write_text(text)
    print(f"  wrote {path.name}  ({path.stat().st_size:,} bytes)", flush=True)
    return True


def forecast_url(start, end, model):
    hourly = ",".join(f"{v}_previous_day1" for v in FORECAST_VARS)
    params = [
        ("latitude", LAT),
        ("longitude", LON),
        ("start_date", start),
        ("end_date", end),
        ("hourly", hourly),
        ("models", model),
        ("timezone", "UTC"),
    ]
    return ("https://previous-runs-api.open-meteo.com/v1/forecast?"
            + urllib.parse.urlencode(params, safe=",")), hourly


def pull_forecast(start, end):
    url, hourly = forecast_url(start, end, MODEL)

    name = f"openmeteo_previousruns_{MODEL}_{STATION}_{start}_{end}.json"
    path = RAW / name
    if path.exists():
        print(f"  SKIP (already present): {name}", flush=True)
        return

    pulled_at = now_stamps()
    status, body = fetch(url)
    write_once(path, body)

    meta = [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {name}",
        "purpose     : session 15, part B1 - full history forecast chunk for",
        "              DSM (Des Moines, Iowa), the third airport",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}         (DSM, Des Moines International, Iowa)",
        f"  longitude  = {LON}       (DSM, Des Moines International, Iowa)",
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
        "  That pin matters more here than it ever did in Europe: Des Moines is",
        "  inside CONUS, so gfs_seamless could in principle prefer a",
        "  higher-resolution non-GFS model there (Q27). Pinning gfs_global",
        "  makes the series NCEP GFS by construction wherever the airport is.",
        "- Temperature only, no extra variables (DECISIONS D17).",
        "- The coordinates are IEM's own record for DSM (DECISIONS F31), the",
        "  same figures session 14's samples used, not a position from a map.",
        "- DSM's target hour is 18:00 UTC, not 12:00 UTC (DECISIONS D33). That",
        "  changes nothing about what is downloaded - a whole-hours series is",
        "  pulled either way.",
        f"- HTTP status {status}.",
        "- Nulls in this file are left exactly as the API returned them. "
        "Nothing",
        "  was filled in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def pull_q27_compare(start, end, why, model):
    """One window, one model string, saved for the Q27 comparison."""
    url, hourly = forecast_url(start, end, model)

    name = (f"openmeteo_previousruns_{model}_{STATION}_"
            f"{start}_{end}_q27compare.json")
    path = RAW / name
    if path.exists():
        print(f"  SKIP (already present): {name}", flush=True)
        return

    pulled_at = now_stamps()
    status, body = fetch(url)
    write_once(path, body)

    meta = [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {name}",
        "purpose     : session 15, part B2 - settle Q27. One half of a",
        f"              value-by-value comparison of {MODEL} against",
        f"              {MODEL_SEAMLESS} at DSM, the way F6 compared them at",
        "              EGLC. F6's argument was location-specific - it rested",
        "              on no CONUS-only NCEP model being able to apply in",
        "              London - and Des Moines is inside CONUS, so the",
        "              comparison has to be made rather than assumed.",
        f"window      : {start} to {end}",
        f"why this window: {why}",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}         (DSM, IEM's own position, F31)",
        f"  longitude  = {LON}",
        f"  start_date = {start}",
        f"  end_date   = {end}",
        f"  hourly     = {hourly}",
        f"  models     = {model}",
        "  timezone   = UTC",
        "",
        "notes:",
        "- This file is for the Q27 comparison only. The project's own DSM",
        f"  series is the yearly {MODEL} chunks; D16 pins that string and this",
        "  comparison does not change it.",
        "- Neither comparison window touches the sealed test year",
        "  (2025-08-01 to 2026-07-31). The recent window sits after the",
        "  project period ends on 2026-07-31, which D13 does not use at all.",
        f"- HTTP status {status}.",
        "- Nulls are left exactly as the API returned them (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def pull_obs(start, end):
    """IEM's end date behaves as exclusive, so ask for the day after `end`."""
    s = datetime.strptime(start, "%Y-%m-%d")
    e = datetime.strptime(end, "%Y-%m-%d")
    e_req = e + timedelta(days=1)

    params = [("station", STATION)]
    params += [("data", f) for f in IEM_FIELDS]
    params += [
        ("year1", str(s.year)), ("month1", str(s.month)), ("day1", str(s.day)),
        ("year2", str(e_req.year)), ("month2", str(e_req.month)),
        ("day2", str(e_req.day)),
        ("tz", "UTC"),
        ("format", "onlycomma"),
        ("latlon", "yes"),
        ("elev", "yes"),
        ("missing", "M"),
        ("trace", "T"),
        ("direct", "no"),
        ("report_type", "3"),  # routine METAR only - the scheduled report
    ]
    url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
           + urllib.parse.urlencode(params))

    name = f"iem_asos_{STATION}_{start}_{end}_routine.csv"
    path = RAW / name
    if path.exists():
        print(f"  SKIP (already present): {name}", flush=True)
        return

    pulled_at = now_stamps()
    status, body = fetch(url)
    write_once(path, body)

    meta = [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {name}",
        "purpose     : session 15, part B3 - full history truth chunk for DSM",
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
        f"  data        = {', '.join(IEM_FIELDS)}  "
        "(tmpc = air temperature degC, dwpc = dew point degC)",
        f"  date range  = {start} to {end} inclusive. IEM treats its end date",
        f"                as exclusive, so the request asks for "
        f"{e_req:%Y-%m-%d}.",
        "  tz          = UTC",
        "  format      = onlycomma",
        "  latlon      = yes",
        "  elev        = yes",
        "  missing     = M   (missing values come back as the letter M)",
        "  trace       = T",
        "  report_type = 3   (routine METAR only - the scheduled hourly "
        "report)",
        "",
        "notes:",
        "- DSM's routine report is stamped at :54, not at :50 like EGLC or on",
        "  the hour like LFPG (DECISIONS F34). It is the hourly truth",
        "  observation (D14). At DSM's 18:00 UTC target (D33) the 17:54 report",
        "  is the paired observation, six minutes out.",
        "- Because the report covering hour H is stamped (H-1):54, the FIRST",
        "  hour of a request window has no report inside that window. The",
        "  chunks here are contiguous, so concatenating them closes that seam",
        "  everywhere except the very first hour of the whole period",
        "  (2021-03-24 00:00 UTC). That is a request-boundary artefact, not a",
        "  hole in the record, and the gap map counts it separately (Q26).",
        "  Nothing is filled to cover it (SPEC 2.2).",
        "- DSM does NOT file a second scheduled report; its 'special' reports",
        "  are genuinely unscheduled (DECISIONS F36). report_type=3 asks for",
        "  routine reports only, so none of them are in this file.",
        "- No network parameter is sent. The EGLC and LFPG pulls addressed",
        "  their stations by code alone, and this pull is deliberately the",
        "  same shape. DSM's network is IA_ASOS (DECISIONS F31).",
        "- Air temperature (tmpc) is the designated truth field, and at DSM it",
        "  really is degrees Celsius - session 14 checked it against the",
        "  Fahrenheit field and the two agree to 0.0044 degC (DECISIONS F35).",
        "  No unit conversion is applied anywhere.",
        "- tz=UTC really is UTC at this station: session 14 pulled the same",
        "  days in local time and they line up at a clean 100% at the expected",
        "  daylight-saving offset (DECISIONS F35).",
        f"- HTTP status {status}.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def main():
    print(f"Airport: {STATION} (Des Moines, Iowa), lat {LAT}, lon {LON}",
          flush=True)
    print(f"Period : {PERIOD_START} to {PERIOD_END}   chunks: {len(CHUNKS)}",
          flush=True)
    print(f"Forecast variables: {', '.join(FORECAST_VARS)} (D17)", flush=True)
    print(f"Model string      : {MODEL} (D16)", flush=True)
    print("Target hour       : 18:00 UTC (D33) - does not affect the pull",
          flush=True)

    print(f"\n=== B1  forecast (Open-Meteo Previous Runs, {MODEL}, {STATION}) ===",
          flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_forecast(start, end)
        time.sleep(PAUSE_SECONDS)

    print(f"\n=== B2  Q27: {MODEL} vs {MODEL_SEAMLESS} at {STATION} ===",
          flush=True)
    for start, end, why in Q27_WINDOWS:
        print(f"{start} -> {end}   ({why})", flush=True)
        for model in (MODEL, MODEL_SEAMLESS):
            pull_q27_compare(start, end, why, model)
            time.sleep(PAUSE_SECONDS)

    print(f"\n=== B3  truth (IEM ASOS routine METARs, {STATION}) ===", flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_obs(start, end)
        time.sleep(PAUSE_SECONDS)

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
