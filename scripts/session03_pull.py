"""Session 03b: pull the full history for both sources, in yearly chunks.

Downloads only. Nothing is joined, cleaned, filled, or modelled here.

Session 03 was started and stopped partway. It pulled four extra forecast
variables alongside temperature and found they only exist for recent data.
The owner's decision (DECISIONS D17) is that stage 1 is temperature-only on
the forecast side, so those partial chunks were discarded and this script
pulls temperature and nothing else.

What it writes, for every chunk:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 — raw data is an immutable, dated snapshot)

If a chunk file already exists, it is left alone and skipped. That way a
failed run can be re-run without re-downloading, and an existing raw file is
never overwritten.

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
# window (SPEC 4.3, DECISIONS D13).
PERIOD_START = "2021-03-24"
PERIOD_END = "2026-07-31"

# EGLC, London City (SPEC 1).
LAT = "51.505"
LON = "0.055"

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# Temperature only (DECISIONS D17). The extra candidate variables tried in the
# aborted session 03 are deliberately not requested.
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field. Dew point comes along in the same
# response and is kept for the record.
IEM_FIELDS = ["tmpc", "dwpc"]

# One (start, end) pair per chunk. Both ends inclusive.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

PAUSE_SECONDS = 2.0  # gentle on both services; IEM asks for at least 1 second


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
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session03b"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.status, resp.read().decode("utf-8")
        except Exception as err:
            if attempt == attempts:
                raise
            wait = 10 * attempt
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


def pull_forecast(start, end):
    hourly = ",".join(f"{v}_previous_day1" for v in FORECAST_VARS)
    params = [
        ("latitude", LAT),
        ("longitude", LON),
        ("start_date", start),
        ("end_date", end),
        ("hourly", hourly),
        ("models", MODEL),
        ("timezone", "UTC"),
    ]
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           + urllib.parse.urlencode(params, safe=","))

    name = f"openmeteo_previousruns_{MODEL}_EGLC_{start}_{end}.json"
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
        "purpose     : session 03b, part A - full history forecast chunk",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}          (EGLC, London City)",
        f"  longitude  = {LON}           (EGLC, London City)",
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

    params = [("station", "EGLC")]
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
        ("report_type", "3"),  # routine METAR only - the scheduled report (F3)
    ]
    url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
           + urllib.parse.urlencode(params))

    name = f"iem_asos_EGLC_{start}_{end}_routine.csv"
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
        "purpose     : session 03b, part B - full history truth chunk",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        "  station     = EGLC",
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
        "- The routine :50 report is the hourly truth observation "
        "(DECISIONS D14, F3).",
        "- EGLC also files a second report at :20 past the hour. It is NOT in",
        "  this file, because report_type=3 asks for routine reports only.",
        "- Air temperature (tmpc) is the designated truth field. Dew point",
        "  (dwpc) arrives in the same response and is kept for the record.",
        f"- HTTP status {status}.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def main():
    print(f"Period: {PERIOD_START} to {PERIOD_END}   chunks: {len(CHUNKS)}",
          flush=True)
    print(f"Forecast variables: {', '.join(FORECAST_VARS)} (D17)", flush=True)

    print(f"\n=== A  forecast (Open-Meteo Previous Runs, {MODEL}) ===",
          flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_forecast(start, end)
        time.sleep(PAUSE_SECONDS)

    print("\n=== B  truth (IEM ASOS routine METARs, EGLC) ===", flush=True)
    for start, end in CHUNKS:
        print(f"{start} -> {end}", flush=True)
        pull_obs(start, end)
        time.sleep(PAUSE_SECONDS)

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
