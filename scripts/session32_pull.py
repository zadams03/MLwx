"""Session 32: pull cloud_cover and wind_speed_10m for the richer-features
scout, at all five airports, over 2024-01-19 -> 2025-07-31 only.

This is the ONLY new data this session touches. It downloads, saves raw with
provenance (SPEC 2.3), and does nothing else -- no joining, filling, fitting or
evaluating happens in this file (that is scripts/session32_scout.py).

Window (session 32 prompt, "Reference -- windows and features"):
- cloud_cover / wind_speed_10m are free only from 2024-01-19 12:00 UTC onward
  (DECISIONS F85). Pulling from 2024-01-19 is the earliest date that can carry
  any real value; the last date needed is 2025-07-31, the end of the
  short-window's validation year (D18's VALID_END, shared by every airport).
- The sealed test year (2025-08-01 -> 2026-07-31) is NOT requested here, for
  any airport. This is the hard line of the session.

Model pin: every request uses models=gfs_global (D16), offset
_previous_day1 (SPEC 3.2).

If a file already exists it is left alone and skipped, so a failed run can be
re-run without re-downloading and a raw file is never overwritten.
"""

import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "features"
RAW.mkdir(parents=True, exist_ok=True)

MODEL = "gfs_global"          # pinned, DECISIONS D16
START = "2024-01-19"          # first hour cloud/wind can carry a value (F85)
END = "2025-07-31"            # end of the short window's validation year (D18)

# SPEC 3.4 positions, IEM's own metadata (F17, F31, F49, F66).
AIRPORTS = {
    "EGLC": (51.5053, 0.0553),
    "LFPG": (49.0153, 2.5344),
    "DSM": (41.534, -93.6531),
    "YSDU": (-32.2167, 148.5747),
    "RNO": (39.4839, -119.7711),
}

PAUSE_SECONDS = 3.0            # session 08 hit an HTTP 429 at a faster pace


def now_stamps():
    local = datetime.now().astimezone()
    utc = datetime.now(timezone.utc)
    return f"{local:%Y-%m-%d %H:%M:%S %Z} ({utc:%Y-%m-%d %H:%M:%S} UTC)"


def fetch(url, attempts=3):
    req = urllib.request.Request(url, headers={"User-Agent": "MLwx/session32"})
    for attempt in range(1, attempts + 1):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                return resp.status, resp.read().decode("utf-8")
        except urllib.error.HTTPError as err:
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


def pull(station):
    lat, lon = AIRPORTS[station]
    variables = ["cloud_cover", "wind_speed_10m"]
    hourly = ",".join(f"{v}_previous_day1" for v in variables)
    params = [
        ("latitude", f"{lat}"),
        ("longitude", f"{lon}"),
        ("start_date", START),
        ("end_date", END),
        ("hourly", hourly),
        ("models", MODEL),
        ("timezone", "UTC"),
    ]
    url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
           + urllib.parse.urlencode(params, safe=","))
    path = RAW / f"openmeteo_previousruns_{MODEL}_{station}_{START}_{END}_cloudwind.json"
    if path.exists():
        print(f"  SKIP (already present): {path.name}", flush=True)
        return path

    pulled_at = now_stamps()
    status, body = fetch(url)
    if status != 200:
        raise SystemExit(
            f"HTTP {status} pulling {station}: {body[:500]}")

    write_once(path, body)
    meta = path.with_suffix(path.suffix + ".meta.txt")
    write_once(meta, "\n".join([
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"file        : {path.name}",
        "purpose     : session 32 - richer-features scout (validation-year "
        "only). cloud_cover and wind_speed_10m forecast, joined to the "
        "existing temperature+observation rows at each airport's target "
        "hour (SPEC 4.5) to test whether a 5-feature model beats the "
        "existing 3-feature recipe on a short, feature-complete window.",
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
        f"  start_date = {START}",
        f"  end_date   = {END}",
        f"  hourly     = {hourly}",
        f"  models     = {MODEL}  (pinned per DECISIONS D16)",
        "  timezone   = UTC",
        "",
        f"HTTP status {status}.",
        "",
        "notes:",
        "- START is 2024-01-19, the first hour cloud_cover/wind_speed_10m",
        "  can carry a real value at any airport (DECISIONS F85). END is",
        "  2025-07-31, the end of the shared D18 validation year -- the",
        "  sealed test year (2025-08-01 onward, D13) is NOT requested.",
        "- A null in this file (if any remains inside the requested range)",
        "  is left exactly as the API returned it; nothing is filled",
        "  (SPEC 2.2). The join in scripts/session32_scout.py drops and",
        "  counts any null rather than estimating one.",
        "",
    ]))
    time.sleep(PAUSE_SECONDS)
    return path


def main():
    print("=" * 78)
    print("SESSION 32 PULL -- cloud_cover + wind_speed_10m, five airports, "
          f"{START} to {END}")
    print("=" * 78)
    for station in AIRPORTS:
        print(f"\n--- {station} ---")
        pull(station)
    print("\nDone. All responses saved under data/raw/features/.")


if __name__ == "__main__":
    main()
