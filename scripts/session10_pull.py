"""Session 10: pull the full history for both sources at LFPG (Paris CDG).

This is session 03b's pull, pointed at the stage 2 airport. Downloads only.
Nothing is joined, cleaned, filled, or modelled here.

Only the location changed (DECISIONS D26). Same period, same yearly chunks,
same model string (`gfs_global`, D16), same temperature-only forecast variable
(D17), same IEM request shape as stage 1's pull. The one thing that differs is
the station code and its coordinates.

What it writes, for every chunk:
- the raw response exactly as it arrived, in data/raw/
- a ".meta.txt" beside it recording the pull time and the exact request
  (SPEC 2.3 - raw data is an immutable, dated snapshot)

If a chunk file already exists, it is left alone and skipped. That way a
failed run can be re-run without re-downloading, and an existing raw file is
never overwritten.

It also makes one small IEM metadata request for the United Kingdom network,
to settle Q22: EGLC's network code has never come back from IEM in this
project, and SPEC 3.4 carries it marked unverified.

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
# window (SPEC 4.3, DECISIONS D13). The same dates as stage 1 - CDG's forecast
# archive begins on the same hour as EGLC's (DECISIONS F20), so nothing moves.
PERIOD_START = "2021-03-24"
PERIOD_END = "2026-07-31"

# LFPG, Paris Charles de Gaulle (SPEC 3.4). The position is IEM's own, from
# the FR__ASOS station metadata pulled in session 08 (DECISIONS F17), not an
# approximate figure from elsewhere.
STATION = "LFPG"
LAT = "49.0153"
LON = "2.5344"

# Pinned explicitly rather than "gfs_seamless" (DECISIONS D16).
MODEL = "gfs_global"

# Temperature only (DECISIONS D17, which applies per airport).
FORECAST_VARS = ["temperature_2m"]

# Air temperature is the truth field. Dew point comes along in the same
# response and is kept for the record.
IEM_FIELDS = ["tmpc", "dwpc"]

# One (start, end) pair per chunk. Both ends inclusive. Identical to the
# stage 1 chunking, so the two airports' raw files line up file for file.
CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
    ("2026-01-01", "2026-07-31"),
]

PAUSE_SECONDS = 3.0  # gentle on both services; three quick IEM calls in
                     # session 08 hit an HTTP 429, so this is longer than
                     # session 03b's 2.0 seconds

# Q22: EGLC's network code, written into SPEC 3.4 marked unverified because
# every EGLC request this project ever made used the station code alone.
UK_NETWORK = "GB__ASOS"


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
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session10"})
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
        "purpose     : session 10, part B1 - full history forecast chunk for",
        "              LFPG (Paris Charles de Gaulle), the stage 2 airport",
        f"pulled at   : {pulled_at}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical "
        "Forecast API)",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  latitude   = {LAT}        (LFPG, Paris Charles de Gaulle)",
        f"  longitude  = {LON}         (LFPG, Paris Charles de Gaulle)",
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
        "- The coordinates are IEM's own record for LFPG (DECISIONS F17), the",
        "  same figures session 08's samples used, not an approximate position.",
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
        "purpose     : session 10, part B2 - full history truth chunk for LFPG",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download "
        "service",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {STATION}   (Paris Charles de Gaulle)",
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
        "- LFPG's routine report is stamped ON THE HOUR, :00, not at :50 like",
        "  EGLC (DECISIONS F18). It is the hourly truth observation (D14).",
        "- LFPG also files a second scheduled report at :30, which IEM labels",
        "  'special' (DECISIONS F19). It is NOT in this file, because",
        "  report_type=3 asks for routine reports only.",
        "- No network parameter is sent. Stage 1's EGLC pulls addressed the",
        "  station by code alone, and this pull is deliberately the same shape",
        "  so that only the location differs (D26). LFPG's network is FR__ASOS",
        "  (DECISIONS F17) and a probe with and without the parameter returned",
        "  identical rows.",
        "- Air temperature (tmpc) is the designated truth field. Dew point",
        "  (dwpc) arrives in the same response and is kept for the record.",
        f"- HTTP status {status}.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def pull_uk_network_metadata():
    """Q22: ask IEM which network EGLC sits in, and what position it holds.

    SPEC 3.4 carries EGLC's network as `GB__ASOS (unverified)`, because every
    EGLC request this project made used the station code alone. This is the
    same call session 08 made for France, pointed at the United Kingdom.
    """
    url = f"https://mesonet.agron.iastate.edu/geojson/network/{UK_NETWORK}.geojson"
    name = f"iem_station_metadata_{UK_NETWORK}.geojson"
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
        "purpose     : session 10, part B3 - settle Q22. EGLC's IEM network",
        "              code has never come back from IEM in this project, so",
        "              SPEC 3.4 carries it marked unverified. This is the same",
        "              network listing session 08 pulled for France, pointed at",
        "              the United Kingdom.",
        f"pulled at   : {pulled_at}",
        "source      : Iowa Environmental Mesonet (IEM) network station listing",
        "tool        : python urllib",
        "",
        "exact URL requested:",
        url,
        "",
        "notes:",
        "- The whole network file is kept rather than just the EGLC entry,",
        "  because it is the actual response and SPEC 2.3 says to keep raw",
        "  pulls untouched.",
        "- What IEM returned for EGLC is reported by scripts/session10_checks.py",
        "  and written up in DECISIONS.",
        f"- HTTP status {status}.",
        "",
    ]
    write_once(path.with_suffix(path.suffix + ".meta.txt"), "\n".join(meta))


def main():
    print(f"Airport: {STATION} (Paris Charles de Gaulle), "
          f"lat {LAT}, lon {LON}", flush=True)
    print(f"Period : {PERIOD_START} to {PERIOD_END}   chunks: {len(CHUNKS)}",
          flush=True)
    print(f"Forecast variables: {', '.join(FORECAST_VARS)} (D17)", flush=True)
    print(f"Model string      : {MODEL} (D16)", flush=True)

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

    print(f"\n=== B3  IEM station metadata for the {UK_NETWORK} network (Q22) ===",
          flush=True)
    pull_uk_network_metadata()

    print("\nDone.", flush=True)


if __name__ == "__main__":
    main()
