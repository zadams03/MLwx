"""Session 36, Task 3: byte-range pull of GFS 2 m temperature GRIB2 messages
for the pipeline-validation sample.

ONE JOB: fetch the TMP:2 m above ground message needed to reproduce each
airport's previous_day1 value on each sample date, via .idx byte-range
requests only -- never a whole ~500 MB GRIB file. This script pulls
TEMPERATURE ONLY (session 36 scope; cloud/wind come in a later session).

Lead-time convention (derived from SPEC 3.2's description of how Open-Meteo
builds previous_day1, and confirmed empirically by session36_validate.py):
for a target valid hour HH:00 UTC on day D, the run is the one made at cycle
floor(HH/6)*6 UTC on day D-1, forecast hour 24 + (HH mod 6). This is the same
"hours 24-29 of each run, stitched" rule SPEC 3.2 (DECISIONS F5) already
documents.

Sample: a short early stretch (2021-03-24 to 2021-03-28, Open-Meteo's own
archive floor) and a recent two-week stretch (2025-06-01 to 2025-06-14),
both well inside Open-Meteo's era and outside the sealed test year
(2025-08-01 to 2026-07-31, SPEC 2.1a/4.3).

Every extract and its provenance (.meta.txt: exact source URL, byte range,
UTC pull time) is saved under data/raw/diagnostics/session36/.
"""

import sys
import time
import urllib.error
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "diagnostics" / "session36"
OUT.mkdir(parents=True, exist_ok=True)

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station code -> target hour (UTC).
AIRPORTS = {
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

EARLY_SAMPLE = [date(2021, 3, 24) + timedelta(days=i) for i in range(5)]   # ..28
RECENT_SAMPLE = [date(2025, 6, 1) + timedelta(days=i) for i in range(14)]  # ..14
ALL_TARGET_DATES = EARLY_SAMPLE + RECENT_SAMPLE

VARIABLE_LABEL = "TMP:2 m above ground"


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_url(run_date, cycle_hour):
    ymd = run_date.strftime("%Y%m%d")
    # Confirmed by Task 1 probe: the /atmos/ subdirectory path is used from
    # 2021-03-23 onward. Every run_date in this sample is >= 2021-03-23
    # (earliest target date 2021-03-24 => run_date 2021-03-23), so this is
    # the only path form this script needs.
    return f"{BUCKET}/gfs.{ymd}/{cycle_hour:02d}/atmos/gfs.t{cycle_hour:02d}z.pgrb2.0p25"


def _get(url, headers=None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "MLwx/session36"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read()


def fetch_idx(base_url, lead):
    idx_url = f"{base_url}.f{lead:03d}.idx"
    text = _get(idx_url).decode("utf-8")
    return idx_url, text


def find_tmp2m_range(idx_text):
    lines = idx_text.strip().split("\n")
    start = None
    end = None
    for i, line in enumerate(lines):
        parts = line.split(":")
        # format: n:offset:d=...:VAR:level:step:
        if len(parts) >= 5 and parts[3] == "TMP" and parts[4] == "2 m above ground":
            start = int(parts[1])
            if i + 1 < len(lines):
                next_parts = lines[i + 1].split(":")
                end = int(next_parts[1]) - 1
            break
    return start, end


def fetch_message(base_url, lead, start, end_hint):
    grib_url_ = f"{base_url}.f{lead:03d}"
    if end_hint is not None:
        range_hdr = f"bytes={start}-{end_hint}"
    else:
        # last record in file -- no next-offset to bound it; take a generous
        # window (2 MB is far more than one surface-field message needs).
        range_hdr = f"bytes={start}-{start + 2_000_000}"
    headers = {"User-Agent": "MLwx/session36", "Range": range_hdr}
    content = _get(grib_url_, headers=headers)
    return grib_url_, content


def main():
    combos = {}  # (run_date, cycle) -> lead, set of airports using it
    for target_date in ALL_TARGET_DATES:
        run_date = target_date - timedelta(days=1)
        for station, target_hour in AIRPORTS.items():
            cycle, lead = cycle_and_lead(target_hour)
            key = (run_date, cycle, lead)
            combos.setdefault(key, set()).add(station)

    print(f"Total distinct (run_date, cycle, lead) files to fetch: {len(combos)}")

    n_ok = 0
    n_fail = 0
    for (run_date, cycle, lead), stations in sorted(combos.items()):
        base_url = grib_url(run_date, cycle)
        fname_base = f"gfs_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{lead:03d}_tmp2m"
        out_grib = OUT / f"{fname_base}.grib2"
        out_meta = OUT / f"{fname_base}.grib2.meta.txt"
        if out_grib.exists():
            print(f"  SKIP (already saved) {fname_base}  [{','.join(sorted(stations))}]")
            n_ok += 1
            continue
        try:
            idx_url, idx_text = fetch_idx(base_url, lead)
            start, end = find_tmp2m_range(idx_text)
            if start is None:
                raise ValueError(f"'{VARIABLE_LABEL}' not found in {idx_url}")
            grib_url_, content = fetch_message(base_url, lead, start, end)
            out_grib.write_bytes(content)
            pull_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            byte_range = f"{start}-{end}" if end is not None else f"{start}-{start + 2_000_000} (open-ended, trimmed range)"
            out_meta.write_text(
                f"source: {grib_url_}\n"
                f"idx source: {idx_url}\n"
                f"byte range requested: {byte_range}\n"
                f"variable: {VARIABLE_LABEL}, forecast hour f{lead:03d}, cycle {cycle:02d}z, run date {run_date.isoformat()}\n"
                f"used by airports (target hour, cycle+lead convention): {', '.join(sorted(stations))}\n"
                f"pulled (UTC): {pull_time}\n"
                f"bytes saved: {len(content)}\n"
                f"first 4 bytes: {content[:4]!r}  last 4 bytes: {content[-4:]!r}\n"
            )
            magic_ok = content[:4] == b"GRIB" and content[-4:] == b"7777"
            print(f"  OK   {fname_base}  bytes={len(content)}  magic_ok={magic_ok}  [{','.join(sorted(stations))}]")
            n_ok += 1
        except Exception as e:
            print(f"  FAIL {fname_base}: {e}")
            n_fail += 1

    print(f"\nDone. {n_ok} files ok, {n_fail} failed.")
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
