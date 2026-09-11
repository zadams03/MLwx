"""Session 37, Task 2: bulk byte-range pull of the GRIB feature set (2 m
temperature, total cloud cover, 10 m u/v wind) over the v16-only training
window, at all five airports.

ONE JOB: for every day in 2021-03-24..2025-07-31 (SPEC 4.3's training
window, restricted to the v16-only floor this sub-project adopted -- see
DECISIONS F89/F90), fetch the four GRIB2 messages needed to reproduce each
airport's own target-hour value at the previous_day1-equivalent lead
(TMP:2 m above ground, TCDC:entire atmosphere, UGRD:10 m above ground,
VGRD:10 m above ground), by .idx byte-range request only -- never a whole
~500-550 MB GRIB file.

Lead-time convention (session 36, DECISIONS F89, confirmed empirically):
for a target valid hour HH:00 UTC on day D, use the run made at cycle
floor(HH/6)*6 UTC on day D-1, forecast hour 24 + (HH mod 6). Every airport's
run_date is therefore D-1; up to 4 distinct (cycle, lead) files are needed
per calendar day (EGLC/LFPG share one, DSM/RNO/YSDU each need their own),
matching the estimate DECISIONS F88 gave in advance.

This is a real multi-year pull (order 10^3-10^4 requests, ~20 GB), run with
bounded concurrency (a pooled requests.Session, a thread pool) and full
resume support: every (run_date, cycle, lead, variable) target is skipped
if its file already exists on disk, so an interrupted run costs nothing to
restart. A disk-space guard aborts cleanly (not mid-file) if free space
drops below a safety floor, and every fetch failure (not just successes) is
recorded in a manifest and counted -- nothing is silently dropped (SPEC 2.2).

Every date fetched is <= 2025-07-31 and >= 2021-03-24 -- both bounds are
asserted before any request is made. Raw extracts are saved under
data/raw/grib/ with one .meta.txt per file (SPEC 2.3), separate from the
existing Open-Meteo data, which this script never reads, modifies, or
overwrites.
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
FAILURES_CSV = OUT / "session37_pull_failures.csv"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station code -> target hour (UTC).
AIRPORTS = {
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

WINDOW_START = date(2021, 3, 24)   # v16-only floor, matches Open-Meteo (SPEC 3.2)
WINDOW_END = date(2025, 7, 31)     # end of training window (SPEC 4.3); sealed
                                    # test year (2025-08-01 onward) is never
                                    # touched by this script.

# variable -> (GRIB var code, level string) exactly as they appear in the
# .idx text, confirmed by direct probe this session (both a recent date and
# an early-2021 date gave the identical labels/line numbers -- session
# prompt's own "confirm exact GRIB labels on contact").
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
_session.headers.update({"User-Agent": "MLwx/session37"})


def cycle_and_lead(target_hour):
    cycle = (target_hour // 6) * 6
    lead = 24 + (target_hour % 6)
    return cycle, lead


def grib_base_url(run_date, cycle_hour):
    ymd = run_date.strftime("%Y%m%d")
    # Confirmed by session 36 Task 1: the /atmos/ path form applies from
    # 2021-03-23 onward, which covers every run_date this window needs
    # (earliest run_date = WINDOW_START - 1 day = 2021-03-23 exactly).
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
    """Exact-match the message whose step field is 'N hour fcst' -- this
    disambiguates TCDC:entire atmosphere, which the .idx also carries as a
    separate '24-26 hour ave fcst' aggregate entry that is not the
    instantaneous field wanted here (confirmed by direct idx inspection
    this session, both a recent and an early-2021 date)."""
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
            )
            n_ok += 1
        except Exception as e:
            n_fail += 1
            failure_rows.append([run_date.isoformat(), cycle, lead, var_key, stations_str, str(e)])

    return n_ok, n_fail, failure_rows


def main():
    assert WINDOW_START >= date(2021, 3, 24), "window start before the v16/Open-Meteo floor"
    assert WINDOW_END <= date(2025, 7, 31), "window end reaches into the sealed test year"

    combos = build_combos()
    n_combos = len(combos)
    n_days = (WINDOW_END - WINDOW_START).days + 1
    print(f"Window: {WINDOW_START} .. {WINDOW_END} ({n_days} days)")
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

        # keep roughly MAX_WORKERS*2 in flight
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
                # let in-flight futures finish, but stop submitting new ones.

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
