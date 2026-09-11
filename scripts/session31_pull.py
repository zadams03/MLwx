"""Session 31: data-availability probe for the richer-features phase.

Confirms and extends F7/D17 (which found that cloud cover, wind speed, dew
point, relative humidity and surface pressure exist only for recent data on
the Previous Runs API, not across the whole archive) across all five airports
now in the project, and makes the project's FIRST-EVER probe of upper-air
(pressure-level) temperature on this API/offset.

Downloads only. Nothing is joined, cleaned, filled, built, fitted or
evaluated here (session 31 scope). Every response is saved untouched under
data/raw/diagnostics/session31/, with a .meta.txt beside it recording the
exact query URL and the UTC pull time (SPEC 2.3).

**Sample-date discipline (SPEC 3.3, from-Dubbo-onward convention, F49).**
Every probe date used here is <= 2025-07-31 -- outside the sealed test year
(2025-08-01 to 2026-07-31, D13). Nothing in this session opens any airport's
test year.

**Model pin.** Every request uses models=gfs_global (D16). The offset
requested is always _previous_day1.

Three jobs, each producing its own saved files:

1. Pin the cloud/wind archive start date to the day at EGLC (bracket then
   step day by day across 2023-12-20 -> 2024-02-01), and a targeted check a
   few days either side of EGLC's own answer at the other four airports.
   dew_point_2m and relative_humidity_2m are co-probed in the same requests
   (wave-two features, informational only this session).
2. The first-ever probe of 925/850 hPa temperature: several candidate
   variable spellings at EGLC first, then (for whichever spelling returns
   real values) a date ladder at all five airports.
3. A five-airport availability table at one recent pre-test anchor
   (2025-06-10 to 2025-06-12), for temperature_2m (control), cloud_cover,
   wind_speed_10m, dew_point_2m, relative_humidity_2m, and the upper-air
   variables.

If a file already exists it is left alone and skipped, so a failed run can be
re-run without re-downloading and a raw file is never overwritten.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "diagnostics" / "session31"
RAW.mkdir(parents=True, exist_ok=True)

MODEL = "gfs_global"   # pinned, DECISIONS D16

# SPEC 3.4 positions, IEM's own metadata (F31, F49, F66; EGLC/LFPG session 08
# and earlier).
AIRPORTS = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

# Known grid points already established for the flat/mountain airports under
# the gfs_global pin (F17, F31, F49, F66), used by the checks script to
# confirm any upper-air response sits at the SAME grid point, i.e. is
# genuinely GFS and not a silent CONUS-model swap under the pin.
KNOWN_GRID = {
    "EGLC": (51.487137, 0.0, 4.0),
    "LFPG": (49.027008, 2.578125, 109.0),
    "DSM": (41.52945, -93.63281, 285.0),
    "YSDU": (-32.274643, 148.59375, 279.0),
    "RNO": (39.537918, -119.765625, 1344.0),
}

PAUSE_SECONDS = 3.0   # session 08 hit an HTTP 429 at a faster pace

KNOWN_VARS = [
    "temperature_2m", "cloud_cover", "wind_speed_10m", "dew_point_2m",
    "relative_humidity_2m",
]


def now_stamps():
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return f"{local:%Y-%m-%d %H:%M:%S %Z} ({utc:%Y-%m-%d %H:%M:%S} UTC)"


def fetch(url, attempts=3):
    """Return (http_status, body_text). Retries only on transient
    connection failures, NOT on an HTTP error status such as 400 -- an
    invalid variable name is a real, repeatable answer, not something to
    retry into exhaustion (this matters for the spelling probes in job 2).
    """
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session31"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as err:
            # A real HTTP error response (e.g. 400 Bad Request for an unknown
            # variable name). Open-Meteo returns a JSON body explaining why.
            # This is a repeatable answer, not a transient failure: return it
            # immediately rather than retrying.
            body = err.read().decode("utf-8", errors="replace")
            return err.code, body
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


def pull_forecast(tag, station, start, end, variables, purpose,
                   model=MODEL):
    """One Previous Runs API request. `variables` is a list of bare variable
    names; `_previous_day1` is appended to each (SPEC 3.2, D16). `tag`
    distinguishes the file from an ordinary full-history pull.
    """
    lat, lon = AIRPORTS[station]
    hourly = ",".join(f"{v}_previous_day1" for v in variables)
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
    path = RAW / f"openmeteo_previousruns_{model}_{station}_{start}_{end}_{tag}.json"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return path
    pulled_at = now_stamps()
    status, body = fetch(url)
    save(path, body, [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        f"purpose     : session 31 - {purpose}",
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
        f"  models     = {model}  (pinned per DECISIONS D16)",
        "  timezone   = UTC",
        "",
        f"HTTP status {status}.",
        "",
        "notes:",
        "- This is a data-availability probe only (session 31 scope). Nothing",
        "  here is joined, filled, fitted or evaluated. A null in this file",
        "  is left exactly as the API returned it (SPEC 2.2).",
        "- Sample-date discipline: every date this session probes is",
        "  <= 2025-07-31, outside the sealed test year (D13, from-Dubbo-",
        "  onward convention, F49). Nothing here opens any airport's test",
        "  year.",
        "",
    ])
    time.sleep(PAUSE_SECONDS)
    return path


def main():
    print("=" * 78)
    print("SESSION 31 PULL -- data-availability probe for richer features")
    print("=" * 78)

    # ---------------------------------------------------------------
    # Job 1a. Pin the cloud/wind start date to the day, at EGLC, by
    # bracketing 2023-12-20 -> 2024-02-01. dew_point_2m and
    # relative_humidity_2m are co-probed in the same request (wave-two
    # features, informational only -- the scan is free).
    # ---------------------------------------------------------------
    print("\n--- Job 1a: EGLC cloud/wind/dewpoint/humidity bracket ---")
    pull_forecast(
        "cloudwind_bracket", "EGLC", "2023-12-20", "2024-02-01",
        ["cloud_cover", "wind_speed_10m", "dew_point_2m",
         "relative_humidity_2m"],
        "Task 1 -- pin cloud_cover/wind_speed_10m's first real hour to the "
        "day at EGLC, bracketing the ~2024-01-19 hypothesis (F7/D17). "
        "dew_point_2m and relative_humidity_2m co-probed as wave-two "
        "features -- informational only, gates nothing this phase.",
    )

    # ---------------------------------------------------------------
    # Job 1b. Targeted check a few days either side of EGLC's own
    # bracket window, at the other four airports (not a full re-scan).
    # ---------------------------------------------------------------
    print("\n--- Job 1b: targeted check at the other four airports ---")
    for station in ["LFPG", "DSM", "YSDU", "RNO"]:
        pull_forecast(
            "cloudwind_targeted", station, "2024-01-14", "2024-01-24",
            ["cloud_cover", "wind_speed_10m", "dew_point_2m",
             "relative_humidity_2m"],
            f"Task 1 -- targeted check of {station}'s own cloud/wind first "
            "real hour against EGLC's bracket result, a few days either "
            "side of the shared archive-gap-end hypothesis "
            "(2024-01-19 12:00 UTC, F8/F22/F38/F57/F75), not a full re-scan.",
        )

    # ---------------------------------------------------------------
    # Job 2a. Upper-air spelling probe, at EGLC, recent short window.
    # One request combines the two primary candidate spellings (the
    # capitalisation Open-Meteo's own docs use elsewhere); three more
    # requests test casing/unit variants individually, since an unknown
    # variable name can fail the whole request.
    # ---------------------------------------------------------------
    print("\n--- Job 2a: upper-air spelling probe at EGLC ---")
    pull_forecast(
        "upperair_primary", "EGLC", "2025-06-15", "2025-06-16",
        ["temperature_925hPa", "temperature_850hPa"],
        "Task 2 -- first-ever probe of upper-air temperature on this "
        "API/offset. Primary candidate spelling (Open-Meteo's own docs "
        "casing convention for pressure-level variables elsewhere on the "
        "platform).",
    )
    pull_forecast(
        "upperair_lowercase", "EGLC", "2025-06-15", "2025-06-16",
        ["temperature_925hpa"],
        "Task 2 -- upper-air spelling variant: lowercase 'hpa'.",
    )
    pull_forecast(
        "upperair_uppercase", "EGLC", "2025-06-15", "2025-06-16",
        ["temperature_925HPA"],
        "Task 2 -- upper-air spelling variant: uppercase 'HPA'.",
    )
    pull_forecast(
        "upperair_mb", "EGLC", "2025-06-15", "2025-06-16",
        ["temperature_925mb"],
        "Task 2 -- upper-air spelling variant: 'mb' (millibar) unit suffix "
        "instead of 'hPa'.",
    )

    # Addendum, added after the four spelling probes above all rejected the
    # SAME way: isolate whether the _previous_dayN offset mechanism applies
    # to pressure-level variables at all, or is rejected regardless of which
    # day is requested. Uses pull_forecast's variables list mechanism but
    # bypasses its automatic "_previous_day1" suffix for probe A, so a
    # second small helper is used instead.
    def pull_forecast_raw_varname(tag, station, start, end, varname, purpose):
        lat, lon = AIRPORTS[station]
        params = [
            ("latitude", f"{lat}"), ("longitude", f"{lon}"),
            ("start_date", start), ("end_date", end),
            ("hourly", varname), ("models", MODEL), ("timezone", "UTC"),
        ]
        url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
               + urllib.parse.urlencode(params, safe=","))
        path = RAW / f"openmeteo_previousruns_{MODEL}_{station}_{start}_{end}_{tag}.json"
        if path.exists():
            print(f"  SKIP (already present): {path.name}", flush=True)
            return
        pulled_at = now_stamps()
        status, body = fetch(url)
        save(path, body, [
            "Raw pull provenance (SPEC 2.3). Do not edit the data file.", "",
            f"file        : {path.name}",
            f"purpose     : session 31 - {purpose}",
            f"pulled at   : {pulled_at}",
            "source      : Open-Meteo Previous Runs API (NOT the Historical "
            "Forecast API)",
            "tool        : python urllib", "",
            "exact URL requested:", url, "",
            "parameters:",
            f"  latitude   = {lat}    ({station})",
            f"  longitude  = {lon}",
            f"  start_date = {start}",
            f"  end_date   = {end}",
            f"  hourly     = {varname}",
            f"  models     = {MODEL}  (pinned per DECISIONS D16)",
            "  timezone   = UTC", "",
            f"HTTP status {status}.", "",
        ])
        time.sleep(PAUSE_SECONDS)

    pull_forecast_raw_varname(
        "upperair_bare_no_offset", "EGLC", "2025-06-15", "2025-06-16",
        "temperature_925hPa",
        "Task 2 addendum -- bare variable name, NO previous_day offset "
        "suffix at all, to test whether pressure-level variables are "
        "accepted on this endpoint's grammar outright (isolates whether "
        "the spelling probes' rejection was about the offset suffix "
        "specifically).",
    )
    pull_forecast_raw_varname(
        "upperair_day0suffix", "EGLC", "2025-06-15", "2025-06-16",
        "temperature_925hPa_previous_day0",
        "Task 2 addendum -- explicit _previous_day0 suffix (should be "
        "equivalent to the bare form if the offset mechanism works at all "
        "for this variable class).",
    )
    for station in ["DSM", "RNO"]:
        pull_forecast_raw_varname(
            "upperair_bare_no_offset", station, "2025-06-15", "2025-06-16",
            "temperature_925hPa,temperature_850hPa",
            f"Task 2 addendum -- confirm the bare (no-offset) pressure-"
            f"level request also works at {station} (a CONUS site) and "
            "returns the SAME grid point as the project's already-"
            "established gfs_global data (F31/F66), i.e. is genuinely GFS "
            "and not a silent CONUS-model swap.",
        )

    # ---------------------------------------------------------------
    # Job 2b. Date ladder for the primary spelling, at ALL FIVE airports
    # (2021-03-24, 2023-07-01, 2024-07-01; the 2025-06-10..12 anchor date
    # doubles as the ladder's most-recent point and as job 3's anchor).
    # ---------------------------------------------------------------
    print("\n--- Job 2b: upper-air date ladder, all five airports ---")
    ladder_dates = ["2021-03-24", "2023-07-01", "2024-07-01"]
    for station in AIRPORTS:
        for d in ladder_dates:
            pull_forecast(
                "upperair_ladder", station, d, d,
                ["temperature_925hPa", "temperature_850hPa"],
                f"Task 2 -- how far back upper-air temperature reaches at "
                f"{station}, date-ladder point {d}. Primary spelling "
                "(temperature_925hPa/850hPa_previous_day1).",
            )

    # ---------------------------------------------------------------
    # Job 3. Five-airport availability table at one recent pre-test
    # anchor, 2025-06-10 -> 2025-06-12. Known-good variables and the
    # upper-air variables are requested separately, so an upper-air
    # rejection (if any) cannot take the known-good variables down with it.
    # This same anchor date also serves as job 2b's most-recent ladder
    # point.
    # ---------------------------------------------------------------
    print("\n--- Job 3: five-airport availability table, recent anchor ---")
    for station in AIRPORTS:
        pull_forecast(
            "anchor_known", station, "2025-06-10", "2025-06-12",
            KNOWN_VARS,
            "Task 3 -- five-airport availability table, recent pre-test "
            "anchor: temperature_2m (control), cloud_cover, wind_speed_10m, "
            "dew_point_2m, relative_humidity_2m.",
        )
        pull_forecast(
            "anchor_upperair", station, "2025-06-10", "2025-06-12",
            ["temperature_925hPa", "temperature_850hPa"],
            "Task 3 -- five-airport availability table, recent pre-test "
            "anchor: temperature_925hPa, temperature_850hPa.",
        )

    print("\nDone. All responses saved under data/raw/diagnostics/session31/.")


if __name__ == "__main__":
    main()
