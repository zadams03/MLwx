"""Session 26 part B: pull the full history for both sources at Reno (RNO).

This is session 03b's, session 10's, session 15's and session 20's pull,
pointed at the fifth airport - Reno, Nevada, not Bozeman. Session 25 verified
two mountain-valley candidates (Bozeman BZN and Reno RNO); after reviewing
session 25's results the owner switched the fifth airport from Bozeman to
Reno (DECISIONS D42, superseding D40). Downloads only. Nothing is joined,
cleaned, filled, or modelled here.

The same period, the same yearly chunks, the same model string (`gfs_global`,
D16), the same temperature-only forecast variable (D17) and the same IEM
request shape as the four earlier full pulls. What differs is the station,
its coordinates, and the target hour used in commentary only (20:00 UTC,
D42/local standard noon at Reno) - the pull itself downloads a whole-hours
series regardless of any target hour.

The `gfs_global` vs `gfs_seamless` comparison was already run at this airport
in session 25 (DECISIONS F69, recorded for Bozeman; the candidate-only sample
at Reno itself was not run to that same depth - see D42 and the session 26
checks script, which computes Reno's own timezone offset directly rather than
assuming it carries over from Bozeman's). It is not repeated here; every
chunk below is pulled with `gfs_global` regardless (D16).

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
# session 25 confirmed the forecast archive starts at BZN on the same hour as
# every other airport (F68); the same probe is repeated for Reno in this
# session's own checks script rather than assumed.
PERIOD_START = "2021-03-24"
PERIOD_END = "2026-07-31"

# RNO, Reno, Nevada, USA (DECISIONS D42, superseding D40's Bozeman choice).
# The position is IEM's own, from the NV_ASOS station metadata pulled in
# session 25 (DECISIONS F66), not an approximate figure from elsewhere.
STATION = "RNO"
LAT = "39.4839"
LON = "-119.7711"
IEM_NETWORK = "NV_ASOS"

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# Temperature only (DECISIONS D17, which applies per airport).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field. Dew point comes along in the same
# response and is kept for the record.
IEM_FIELDS = ["tmpc", "dwpc"]

# One (start, end) pair per chunk. Both ends inclusive. Identical to every
# earlier airport's chunking, so all five airports' raw files line up file
# for file.
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
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session26"})
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
        "purpose     : session 26, part B1 - full history forecast chunk for",
        "              Reno (RNO), Nevada, USA, the fifth airport (switched",
        "              from Bozeman, DECISIONS D42, superseding D40)",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}       (RNO, Reno, IEM's own position, F66)",
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
        "(DECISIONS D16). At this airport session 25's candidate sample and",
        "  Bozeman's own full comparison (F69) both found the two strings",
        "  DIFFER sharply on recent dates, so the pin is doing real work here.",
        "- Temperature only, no extra variables (DECISIONS D17).",
        "- The coordinates are IEM's own record for RNO (DECISIONS F66), the",
        "  same figures session 25's candidate-comparison sample used, not a",
        "  position from a map.",
        "- Reno's target hour is 20:00 UTC (local standard noon, Pacific",
        "  standard time UTC-8), not 12:00, 18:00, 02:00 or 19:00 UTC",
        "  (DECISIONS D42). That changes nothing about what is downloaded - a",
        "  whole-hours series is pulled either way.",
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
        "purpose     : session 26, part B2 - full history truth chunk for",
        "              Reno (RNO)",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {STATION}   (Reno, Nevada, USA)",
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
        "- RNO's routine report is stamped at :55, five minutes before the",
        "  hour (session 25's candidate sample, IEM's own METAR_RESET_MINUTE",
        "  attribute = 55). At Reno's 20:00 UTC target (D42) the 19:55 report",
        "  is the paired observation under D14 - a 5-minute offset.",
        "- No network parameter is sent. Every earlier airport's full pull",
        "  addressed its station by code alone, and this pull is deliberately",
        "  the same shape. RNO's network is NV_ASOS (DECISIONS F66).",
        "- Air temperature (tmpc) is the designated truth field. US METARs",
        "  are written in whole-degree Fahrenheit, so a small",
        "  Fahrenheit-derived rounding gap is expected, the same pattern DSM",
        "  (F35) and Bozeman (session 25) both showed. No unit conversion is",
        "  applied anywhere.",
        f"- HTTP status {status}.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def main():
    print(f"Airport: {STATION} (Reno, Nevada, USA), lat {LAT}, lon {LON}",
          flush=True)
    print("Switched from Bozeman (BZN) to Reno (RNO) - DECISIONS D42, "
          "superseding D40.", flush=True)
    print(f"Period : {PERIOD_START} to {PERIOD_END}   chunks: {len(CHUNKS)}",
          flush=True)
    print(f"Forecast variables: {', '.join(FORECAST_VARS)} (D17)", flush=True)
    print(f"Model string      : {MODEL} (D16)", flush=True)
    print("Target hour       : 20:00 UTC (D42) - does not affect the pull",
          flush=True)
    print("gfs_global vs gfs_seamless: diverges sharply at this station "
          "(session 25 candidate sample; F69 for Bozeman) - gfs_global used "
          "regardless (D16).", flush=True)

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
