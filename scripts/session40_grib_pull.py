"""Session 40, Task 1 (part 1): bulk byte-range pull of the GRIB feature set
(2 m temperature, total cloud cover, 10 m u/v wind) over the SEALED TEST
YEAR, at all five airports -- the identical pipeline session 37 used for the
training window (DECISIONS F90), restricted to a new date range.

ONE JOB: for every day in 2025-08-01..2026-07-31 (SPEC 4.3's sealed test
year, D48.8), fetch the four GRIB2 messages needed to reproduce each
airport's own target-hour value at the previous_day1-equivalent lead
(TMP:2 m above ground, TCDC:entire atmosphere, UGRD:10 m above ground,
VGRD:10 m above ground), by .idx byte-range request only -- never a whole
GRIB file. No new choices: same source (AWS noaa-gfs-bdp-pds), same F89
lead convention, same variable labels session37_grib_pull.py already
confirmed by direct probe.

This is session 40's OWN pull -- the sealed year has never been fetched
from GRIB before (D48.8: "this is a genuinely new pull for this recipe").
Raw extracts are saved under data/raw/grib/ (gitignored per D47), one
.meta.txt per file (SPEC 2.3), alongside (not overwriting) session 37's
training-window extracts already there -- the two windows use disjoint
run_dates so filenames never collide.

Every date fetched is >= 2025-08-01 and <= 2026-07-31 -- both bounds
asserted before any request is made. This script never reads, modifies, or
overwrites the training-window extracts or any existing Open-Meteo data.
"""

import csv
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "grib"
OUT.mkdir(parents=True, exist_ok=True)
FAILURES_CSV = OUT / "session40_pull_failures.csv"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station code -> target hour (UTC).
AIRPORTS = {
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

WINDOW_START = date(2025, 8, 1)    # D48.8: sealed test year start (SPEC 4.3)
WINDOW_END = date(2026, 7, 31)     # D48.8: sealed test year end (SPEC 4.3)

# Identical to session37_grib_pull.py's VARIABLES (confirmed by direct probe
# at both an early-2021 and a recent date that session; the sealed window is
# entirely "recent" relative to that probe, so no re-confirmation is needed).
VARIABLES = {
    "tmp2m": ("TMP", "2 m above ground"),
    "tcdc": ("TCDC", "entire atmosphere"),
    "ugrd10m": ("UGRD", "10 m above ground"),
    "vgrd10m": ("VGRD", "10 m above ground"),
}

MAX_WORKERS = 48
DISK_FREE_FLOOR_BYTES = 3 * 1024 ** 3  # abort if free space drops below 3 GiB
REQUEST_TIMEOUT = 60
MAX_RETRIES = 3

_session = requests.Session()
_session.mount("https://", HTTPAdapter(pool_connections=MAX_WORKERS, pool_maxsize=MAX_WORKERS))
_session.headers.update({"User-Agent": "MLwx/session40"})


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_base_url(run_date, cycle_hour):
    ymd = run_date.strftime("%Y%m%d")
    # /atmos/ path form applies from 2021-03-23 onward (session 36 Task 1) --
    # covers every run_date this window needs (earliest = 2025-07-31).
    return f"{BUCKET}/gfs.{ymd}/{cycle_hour:02d}/atmos/gfs.t{cycle_hour:02d}z.pgrb2.0p25"


def _get_with_retries(url, headers=None):
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = _session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (200, 206):
                return resp.content
            if resp.status_code == 404:
                raise FileNotFoundError(f"404 {url}")
            last_exc = RuntimeError(f"HTTP {resp.status_code} {url}")
        except Exception as e:
            last_exc = e
        if attempt < MAX_RETRIES:
            time.sleep(0.5 * attempt)
    raise last_exc


def find_message_range(idx_text, var_code, level, lead):
    """Exact-match the message whose step field is 'N hour fcst' -- disambiguates
    TCDC:entire atmosphere from the .idx's separate 'N-M hour ave fcst' entry
    (confirmed by session 37's own direct idx inspection)."""
    lines = idx_text.strip().split("\n")
    wanted_step = f"{lead} hour fcst"
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 6 and parts[3] == var_code and parts[4] == level and parts[5] == wanted_step:
            start = int(parts[1])
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
            return start, end
    return None, None


def build_combos():
    combos = {}  # (run_date, cycle, lead) -> set of stations
    d = WINDOW_START
    while d <= WINDOW_END:
        run_date = d - timedelta(days=1)
        for station, target_hour in AIRPORTS.items():
            cycle, lead = cycle_and_lead(target_hour)
            combos.setdefault((run_date, cycle, lead), set()).add(station)
        d += timedelta(days=1)
    return combos


def process_combo(run_date, cycle, lead, stations):
    """Fetch all 4 variables for one (run_date, cycle, lead) file. Returns
    (n_ok, n_fail, failure_rows)."""
    base_url = grib_base_url(run_date, cycle)
    fname_prefix = f"gfs_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{lead:03d}"
    stations_str = ",".join(sorted(stations))

    needed = {}
    for var_key, (var_code, level) in VARIABLES.items():
        out_grib = OUT / f"{fname_prefix}_{var_key}.grib2"
        if not out_grib.exists():
            needed[var_key] = (var_code, level)
    if not needed:
        return 4, 0, []

    idx_url = f"{base_url}.f{lead:03d}.idx"
    n_ok, n_fail = 4 - len(needed), 0
    failure_rows = []
    try:
        idx_text = _get_with_retries(idx_url).decode("utf-8")
    except Exception as e:
        for var_key in needed:
            failure_rows.append([run_date.isoformat(), cycle, lead, var_key, stations_str, f"idx fetch failed: {e}"])
        return n_ok, len(needed), failure_rows

    for var_key, (var_code, level) in needed.items():
        try:
            start, end = find_message_range(idx_text, var_code, level, lead)
            if start is None:
                raise ValueError(f"'{var_code}:{level}:{lead} hour fcst' not found in {idx_url}")
            grib_url_ = f"{base_url}.f{lead:03d}"
            range_hdr = f"bytes={start}-{end}" if end is not None else f"bytes={start}-{start + 2_000_000}"
            content = _get_with_retries(grib_url_, headers={"Range": range_hdr})
            if content[:4] != b"GRIB" or content[-4:] != b"7777":
                raise ValueError("bad magic markers (not a complete GRIB2 message)")

            out_grib = OUT / f"{fname_prefix}_{var_key}.grib2"
            out_meta = OUT / f"{fname_prefix}_{var_key}.grib2.meta.txt"
            out_grib.write_bytes(content)
            pull_time = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            byte_range = f"{start}-{end}" if end is not None else f"{start}-{start + 2_000_000} (open-ended, trimmed range)"
            out_meta.write_text(
                f"source: {grib_url_}\n"
                f"idx source: {idx_url}\n"
                f"byte range requested: {byte_range}\n"
                f"variable: {var_code}:{level}, forecast hour f{lead:03d}, cycle {cycle:02d}z, "
                f"run date {run_date.isoformat()}\n"
                f"used by airports (target hour, cycle+lead convention): {stations_str}\n"
                f"pulled (UTC): {pull_time}\n"
                f"bytes saved: {len(content)}\n"
                f"first 4 bytes: {content[:4]!r}  last 4 bytes: {content[-4:]!r}\n"
                f"sealed test year pull (session 40, D48.8) -- SPEC 4.3\n"
            )
            n_ok += 1
        except Exception as e:
            n_fail += 1
            failure_rows.append([run_date.isoformat(), cycle, lead, var_key, stations_str, str(e)])

    return n_ok, n_fail, failure_rows


def main():
    assert WINDOW_START == date(2025, 8, 1), "sealed test year start does not match D48.8/SPEC 4.3"
    assert WINDOW_END == date(2026, 7, 31), "sealed test year end does not match D48.8/SPEC 4.3"

    combos = build_combos()
    n_combos = len(combos)
    n_days = (WINDOW_END - WINDOW_START).days + 1
    print(f"Window: {WINDOW_START} .. {WINDOW_END} ({n_days} days) -- SEALED TEST YEAR (D48.8)")
    print(f"Distinct (run_date, cycle, lead) files needed: {n_combos}")
    print(f"Variables per file: {len(VARIABLES)}  ->  up to {n_combos * len(VARIABLES)} messages, "
          f"{n_combos + n_combos * len(VARIABLES)} requests (idx + range-gets)")
    print(f"Concurrency: {MAX_WORKERS} threads; disk-free floor: {DISK_FREE_FLOOR_BYTES / 1024**3:.0f} GiB\n")

    failure_log_rows = []
    total_ok = total_fail = 0
    n_done = 0
    t0 = time.time()
    aborted_low_disk = False

    items = sorted(combos.items())
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futures = {}
        submitted = 0
        it = iter(items)

        def submit_next():
            nonlocal submitted
            try:
                (run_date, cycle, lead), stations = next(it)
            except StopIteration:
                return False
            fut = ex.submit(process_combo, run_date, cycle, lead, stations)
            futures[fut] = (run_date, cycle, lead)
            submitted += 1
            return True

        for _ in range(MAX_WORKERS * 2):
            if not submit_next():
                break

        while futures:
            free = shutil.disk_usage(ROOT).free
            if free < DISK_FREE_FLOOR_BYTES and not aborted_low_disk:
                print(f"\nABORTING: free disk space {free / 1024**3:.2f} GiB below "
                      f"{DISK_FREE_FLOOR_BYTES / 1024**3:.0f} GiB floor. "
                      f"Completed {n_done}/{n_combos} combos; not submitting any more.")
                aborted_low_disk = True

            done_fut = next(as_completed(list(futures.keys())))
            run_date, cycle, lead = futures.pop(done_fut)
            try:
                n_ok, n_fail, rows = done_fut.result()
            except Exception as e:
                n_ok, n_fail, rows = 0, len(VARIABLES), [
                    [run_date.isoformat(), cycle, lead, "ALL", "?", f"combo-level exception: {e}"]
                ]
            total_ok += n_ok
            total_fail += n_fail
            failure_log_rows.extend(rows)
            n_done += 1

            if not aborted_low_disk:
                submit_next()

            if n_done % 100 == 0 or n_done == n_combos:
                elapsed = time.time() - t0
                rate = n_done / elapsed if elapsed > 0 else 0
                eta_s = (n_combos - n_done) / rate if rate > 0 else float("inf")
                print(f"  {n_done}/{n_combos} combos  ok_msgs={total_ok} fail_msgs={total_fail}  "
                      f"elapsed={elapsed/60:.1f}min  rate={rate:.2f} combos/s  eta={eta_s/60:.1f}min",
                      flush=True)

    with open(FAILURES_CSV, "a", newline="") as f:
        w = csv.writer(f)
        if f.tell() == 0:
            w.writerow(["run_date", "cycle", "lead", "variable", "stations", "reason"])
        w.writerows(failure_log_rows)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed/60:.1f} min. combos processed: {n_done}/{n_combos}")
    print(f"messages ok: {total_ok}  messages failed: {total_fail}")
    print(f"failure manifest: {FAILURES_CSV} ({len(failure_log_rows)} new rows this run)")
    if aborted_low_disk:
        print("ABORTED EARLY due to low disk space -- re-run this script to resume "
              "(already-saved files are skipped).")
        sys.exit(2)
    if n_done < n_combos:
        print("INCOMPLETE -- re-run this script to resume.")
        sys.exit(1)


if __name__ == "__main__":
    main()
