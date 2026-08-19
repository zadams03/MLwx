"""Session 20 part B: pull the full history for both sources at Dubbo (YSDU).

This is session 03b's, session 10's and session 15's pull, pointed at the
fourth airport. Downloads only. Nothing is joined, cleaned, filled, or
modelled here.

The same period, the same yearly chunks, the same model string (`gfs_global`,
D16), the same temperature-only forecast variable (D17) and the same IEM
request shape as the three earlier full pulls. What differs is the station,
its coordinates, and the target hour used in commentary only (02:00 UTC, D37) -
the pull itself downloads a whole-hours series regardless of any target hour.

The `gfs_global` vs `gfs_seamless` comparison was already settled at this
airport in session 19 (DECISIONS F52: identical in both windows tested), so it
is not repeated here.

What it writes, for every chunk:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 - raw data is an immutable, dated snapshot)

If a file already exists it is left alone and skipped. A failed run can then be
re-run without re-downloading, and an existing raw file is never overwritten.

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
# window (SPEC 4.3, DECISIONS D13). The same dates as every earlier airport -
# Dubbo's forecast archive begins on the same hour as the other three
# (DECISIONS F51), so nothing moves.
PERIOD_START = "2021-03-24"
PERIOD_END = "2026-07-31"

# YSDU, Dubbo, New South Wales, Australia (SPEC 3.4). The position is IEM's
# own, from the AU__ASOS station metadata pulled in session 19 (DECISIONS
# F49), not an approximate figure from elsewhere.
STATION = "YSDU"
LAT = "-32.2167"
LON = "148.5747"
IEM_NETWORK = "AU__ASOS"

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# Temperature only (DECISIONS D17, which applies per airport).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field. Dew point comes along in the same
# response and is kept for the record.
IEM_FIELDS = ["tmpc", "dwpc"]

# One (start, end) pair per chunk. Both ends inclusive. Identical to every
# earlier airport's chunking, so all four airports' raw files line up file for
# file.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
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
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session20"})
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
        "purpose     : session 20, part B1 - full history forecast chunk for",
        "              Dubbo (YSDU), New South Wales, Australia, the fourth",
        "              airport",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}       (YSDU, Dubbo, IEM's own position, F49)",
        f"  longitude  = {LON}",
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
        "(DECISIONS D16). At this airport the two strings were already found",
        "  identical in both windows tested (DECISIONS F52), so the pin",
        "  changes nothing here in practice, but is used regardless for the",
        "  same reason it is used everywhere else in the project.",
        "- Temperature only, no extra variables (DECISIONS D17).",
        "- The coordinates are IEM's own record for YSDU (DECISIONS F49), the",
        "  same figures session 19's samples used, not a position from a map.",
        "- Dubbo's target hour is 02:00 UTC, not 12:00 or 18:00 UTC (DECISIONS",
        "  D37). That changes nothing about what is downloaded - a whole-hours",
        "  series is pulled either way.",
        f"- HTTP status {status}.",
        "- Nulls in this file are left exactly as the API returned them. "
        "Nothing",
        "  was filled in (SPEC 2.2).",
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
        "purpose     : session 20, part B2 - full history truth chunk for",
        "              Dubbo (YSDU)",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {STATION}   (Dubbo, New South Wales, Australia)",
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
        "- YSDU's routine report is stamped on the hour, :00 (DECISIONS F53),",
        "  the same shape as LFPG. At Dubbo's 02:00 UTC target (D37) the 02:00",
        "  report is the paired observation - an exact match, no offset.",
        "- YSDU files a second SCHEDULED report each hour, at :30 (DECISIONS",
        "  F55), the same pattern as EGLC and LFPG rather than DSM's genuinely",
        "  unscheduled 'special' stream. report_type=3 asks for routine",
        "  reports only, so none of the :30 reports are in this file.",
        "- No network parameter is sent. Every earlier airport's full pull",
        "  addressed its station by code alone, and this pull is deliberately",
        "  the same shape. YSDU's network is AU__ASOS (DECISIONS F49).",
        "- Air temperature (tmpc) is the designated truth field, and at Dubbo",
        "  it is natively whole-degree Celsius - session 19 checked it against",
        "  the Fahrenheit field and the two agree to the limits of",
        "  floating-point (DECISIONS F54). No unit conversion is applied",
        "  anywhere.",
        "- tz=UTC really is UTC at this station: session 19 pulled the same",
        "  days in local time and they line up at a clean 100% at the AEST",
        "  standard offset (DECISIONS F54).",
        f"- HTTP status {status}.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def main():
    print(f"Airport: {STATION} (Dubbo, New South Wales, Australia), "
          f"lat {LAT}, lon {LON}", flush=True)
    print(f"Period : {PERIOD_START} to {PERIOD_END}   chunks: {len(CHUNKS)}",
          flush=True)
    print(f"Forecast variables: {', '.join(FORECAST_VARS)} (D17)", flush=True)
    print(f"Model string      : {MODEL} (D16)", flush=True)
    print("Target hour       : 02:00 UTC (D37) - does not affect the pull",
          flush=True)
    print("gfs_global vs gfs_seamless: already settled at this airport in "
          "session 19 (F52) - not repeated here.", flush=True)

    print(f"\n=== B1  forecast (Open-Meteo Previous Runs, {MODEL}, {STATION}) ===",
          flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_forecast(start, end)
        time.sleep(PAUSE_SECONDS)

    print(f"\n=== B2  truth (IEM ASOS routine METARs, {STATION}) ===", flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_obs(start, end)
        time.sleep(PAUSE_SECONDS)

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
