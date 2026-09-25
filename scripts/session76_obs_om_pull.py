"""Session 76, Steps 4.2 and 4.3: KSFO's observation pull and its Open-Meteo
pulls. Network. Nothing is fitted or scored. Prints counts and timestamps
only (DECISIONS D67.6).

- 4.2 IEM routine reports (report_type=3), SFO, 2021-03-24..2026-07-31, in
  yearly chunks shaped like every earlier full pull (station code alone,
  tz=UTC, tmpc and dwpc). IEM's end date is exclusive, so the last chunk asks
  for 2026-08-01 and returns nothing dated 2026-08-01 (checked below).
- 4.3 Open-Meteo Previous Runs, gfs_global, temperature_2m_previous_day1 at
  IEM's position, 2021-03-24..2024-07-31 only (the reproduction gate).
- For Step 5.5 (F90's cloud/wind check): cloud_cover_previous_day1 and
  wind_speed_10m_previous_day1 on 2024-01-19..2024-07-31 only, where
  Open-Meteo has them (F85). Nothing on or after 2024-08-01.

Every file goes to data/raw/ (Open-Meteo cloud/wind to data/raw/features/,
like session 37's) with a .meta.txt (SPEC 2.3). A file that already exists is
never overwritten (SPEC 8.7 item 5).
"""

import csv
import datetime as dt
import json
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
FEATURES = RAW / "features"

STATION = "SFO"
LAT, LON = 37.619, -122.3749            # IEM CA_ASOS listing, Step 2.1
HARD_END = dt.date(2026, 8, 1)
HELD_OUT_START = dt.date(2024, 8, 1)
PAUSE_SECONDS = 5
UA = {"User-Agent": "MLwx/session76"}

OBS_CHUNKS = [  # (first day, last day), inclusive
    (dt.date(2021, 3, 24), dt.date(2021, 12, 31)),
    (dt.date(2022, 1, 1), dt.date(2022, 12, 31)),
    (dt.date(2023, 1, 1), dt.date(2023, 12, 31)),
    (dt.date(2024, 1, 1), dt.date(2024, 12, 31)),
    (dt.date(2025, 1, 1), dt.date(2025, 12, 31)),
    (dt.date(2026, 1, 1), dt.date(2026, 7, 31)),
]
OM_CHUNKS = [
    (dt.date(2021, 3, 24), dt.date(2021, 12, 31)),
    (dt.date(2022, 1, 1), dt.date(2022, 12, 31)),
    (dt.date(2023, 1, 1), dt.date(2023, 12, 31)),
    (dt.date(2024, 1, 1), dt.date(2024, 7, 31)),
]
OM_CLOUDWIND = (dt.date(2024, 1, 19), dt.date(2024, 7, 31))


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def get(url):
    for attempt in range(6):
        time.sleep(PAUSE_SECONDS if attempt == 0 else 30 * attempt)
        r = requests.get(url, headers=UA, timeout=300)
        if r.status_code != 429:
            return r
        print(f"  HTTP 429 (too many requests), waiting before retry {attempt + 1}", flush=True)
    return r


def save_new(path, data, meta_lines):
    meta = Path(str(path) + ".meta.txt")
    if path.exists() or meta.exists():
        sys.exit(f"STOP: {path.relative_to(ROOT)} already exists; not overwriting.")
    path.write_bytes(data)
    meta.write_text("Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
                    + "\n".join(meta_lines) + "\n")


def pull_obs(first, last):
    end_excl = last + dt.timedelta(days=1)
    assert end_excl <= HARD_END
    url = ("https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
           f"station={STATION}&data=tmpc&data=dwpc&year1={first.year}&month1={first.month}"
           f"&day1={first.day}&year2={end_excl.year}&month2={end_excl.month}&day2={end_excl.day}"
           "&tz=UTC&format=onlycomma&latlon=yes&elev=yes&missing=M&trace=T&direct=no&report_type=3")
    pulled = now_utc()
    r = get(url)
    if r.status_code != 200:
        sys.exit(f"STOP: HTTP {r.status_code} for {url}")
    name = f"iem_asos_{STATION}_{first}_{last}_routine.csv"
    save_new(RAW / name, r.content, [
        f"file        : {name}",
        "purpose     : session 76, Step 4.2 - full history truth chunk for",
        "              San Francisco International (SFO / KSFO)",
        f"pulled at   : {pulled}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download service",
        "tool        : python requests",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        "  station     = SFO   (San Francisco International, California, USA)",
        "  data        = tmpc, dwpc  (tmpc = air temperature degC, dwpc = dew point degC)",
        f"  date range  = {first} to {last} inclusive. IEM treats its end date",
        f"                as exclusive, so the request asks for {end_excl}.",
        "  tz          = UTC",
        "  report_type = 3   (routine METAR only - the scheduled hourly report)",
        "",
        "notes:",
        "- SFO's routine report is stamped at :56 (session 76 Step 2.3; IEM's",
        "  METAR_RESET_MINUTE = 56). At the 20:00 UTC target (D67.1) the 19:56",
        "  report is the paired observation - a 4-minute offset.",
        "- No network parameter is sent, the same shape as every earlier",
        "  airport's full pull. SFO's network is CA_ASOS (Step 2.1).",
        "- Rows from 2024-08-01 on are KSFO's held-out range (D67.6): pulled and",
        "  kept, but before the lock only their counts and timestamps are read.",
        "- Rows marked M are left exactly as they arrived. Nothing was filled",
        "  in (SPEC 2.2).",
        f"- HTTP status {r.status_code}.",
    ])
    rows = list(csv.DictReader(open(RAW / name)))
    stations = {x["station"] for x in rows}
    times = sorted(x["valid"] for x in rows)
    print(f"  {name}: {len(rows)} rows, stations {sorted(stations)}, "
          f"first {times[0] if times else None}, last {times[-1] if times else None}")
    if stations != {STATION} or (times and times[-1] >= HARD_END.isoformat()):
        sys.exit("STOP: unexpected station or a row on/after 2026-08-01")
    return len(rows)


def pull_om(first, last, hourly, tag, folder, purpose):
    assert last < HELD_OUT_START
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           f"latitude={LAT}&longitude={LON}&start_date={first}&end_date={last}"
           f"&hourly={hourly}&models=gfs_global&timezone=UTC")
    pulled = now_utc()
    r = get(url)
    if r.status_code != 200:
        sys.exit(f"STOP: HTTP {r.status_code} for {url}")
    name = f"openmeteo_previousruns_gfs_global_{STATION}_{first}_{last}{tag}.json"
    save_new(folder / name, r.content, [
        f"file        : {name}",
        f"purpose     : {purpose}",
        f"pulled at   : {pulled}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical Forecast API)",
        "tool        : python requests",
        "",
        "exact URL requested:",
        url,
        "",
        "notes:",
        "- *_previous_day1 only (SPEC 3.2, 2.1b); model gfs_global (D16).",
        "- The coordinates are IEM's own record for SFO (Step 2.1).",
        "- Before 2024-08-01 only: nothing from KSFO's held-out range (D67.6).",
        "- Nulls are left exactly as the API returned them (SPEC 2.2).",
        f"- HTTP status {r.status_code}.",
    ])
    d = json.loads(r.content)
    h = d["hourly"]
    n = len(h["time"])
    nulls = {k: sum(1 for v in h[k] if v is None) for k in h if k != "time"}
    print(f"  {name}: grid {d['latitude']}, {d['longitude']}, elev {d['elevation']}; "
          f"{n} hours {h['time'][0]} .. {h['time'][-1]}; nulls {nulls}")
    return d


def main():
    print(f"=== Step 4.2 IEM routine reports, SFO (run at {now_utc()}) ===")
    total = sum(pull_obs(a, b) for a, b in OBS_CHUNKS)
    print(f"total routine rows: {total}")

    print(f"\n=== Step 4.3 Open-Meteo temperature_2m_previous_day1, 2021-03-24..2024-07-31 ===")
    for a, b in OM_CHUNKS:
        pull_om(a, b, "temperature_2m_previous_day1", "", RAW,
                "session 76, Step 4.3 - KSFO's GRIB-vs-Open-Meteo reproduction gate (F89/F90)")

    print(f"\n=== Step 5.5 input: Open-Meteo cloud cover and wind, {OM_CLOUDWIND[0]}..{OM_CLOUDWIND[1]} ===")
    pull_om(*OM_CLOUDWIND, "cloud_cover_previous_day1,wind_speed_10m_previous_day1", "_cloudwind",
            FEATURES, "session 76, Step 5.5 - cloud cover and wind against GRIB, as F90 did")


if __name__ == "__main__":
    main()
