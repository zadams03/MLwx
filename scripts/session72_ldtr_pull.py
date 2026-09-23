"""Session 72: pull the raw GRIB messages behind L, D, T and R at RNO.

Clean-room build (DECISIONS D64.3). Written from SPEC.md, DECISIONS.md and
DECISIONS-archive.md only. It imports no other project script.

What it pulls (DECISIONS D64.6; recipe in notes/session-72-output.txt):
- target days 2021-03-24 .. 2025-07-31 (RNO's train and test windows);
- for target day D: the GFS run of day D-1, cycle 18z (SPEC 7.2, D48.2);
- from f026: TMP at 925/850/700 mb (L), RH/DPT/SPFH at 2 m (D),
  PRMSL and PRES:surface (T), DSWRF:surface 24-26 h average (R);
- from f023: PRMSL (T's lead-3 value).

Each message is fetched by byte range, using the file's .idx inventory, from
noaa-gfs-bdp-pds. Every .idx and every message is saved in the gitignored
cache data/raw/grib/session72/ with a .meta.txt sidecar (URL, byte range,
pull time UTC, size, SHA-256). The pull is resumable: a file whose sidecar
SHA-256 matches is not fetched again. Each failure gets one retry. Failures
are logged, never filled (SPEC 2.2).

Usage:
  .venv/bin/python scripts/session72_ldtr_pull.py --plan   # count + estimate
  .venv/bin/python scripts/session72_ldtr_pull.py --pull   # fetch
  .venv/bin/python scripts/session72_ldtr_pull.py --manifest  # write manifest
"""

import argparse
import csv
import datetime as dt
import hashlib
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "grib" / "session72"
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session72"
MANIFEST = DIAG / "session72_pull_manifest.csv"
FAILURES = DIAG / "session72_pull_failures.csv"
SIZE_SOURCE = ROOT / "data" / "raw" / "diagnostics" / "session71" / "session71_pull_manifest.csv"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
FIRST_TARGET = dt.date(2021, 3, 24)
LAST_TARGET = dt.date(2025, 7, 31)
CYCLE = 18  # floor(20 / 6) * 6, SPEC 7.2

# (forecast hour, idx variable, idx level, idx step, short name for files)
MESSAGES = [
    (26, "TMP", "925 mb", "26 hour fcst", "TMP_925mb"),
    (26, "TMP", "850 mb", "26 hour fcst", "TMP_850mb"),
    (26, "TMP", "700 mb", "26 hour fcst", "TMP_700mb"),
    (26, "RH", "2 m above ground", "26 hour fcst", "RH_2m"),
    (26, "DPT", "2 m above ground", "26 hour fcst", "DPT_2m"),
    (26, "SPFH", "2 m above ground", "26 hour fcst", "SPFH_2m"),
    (26, "PRMSL", "mean sea level", "26 hour fcst", "PRMSL_msl"),
    (26, "PRES", "surface", "26 hour fcst", "PRES_surface"),
    (26, "DSWRF", "surface", "24-26 hour ave fcst", "DSWRF_surface"),
    (23, "PRMSL", "mean sea level", "23 hour fcst", "PRMSL_msl"),
]
FHOURS = sorted({m[0] for m in MESSAGES})

_local = threading.local()
_count_lock = threading.Lock()


def inc(counters, key):
    with _count_lock:
        counters[key] = counters.get(key, 0) + 1


def session():
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
    return _local.s


def target_days():
    d = FIRST_TARGET
    while d <= LAST_TARGET:
        yield d
        d += dt.timedelta(days=1)


def file_url(run_date, fh):
    ymd = run_date.strftime("%Y%m%d")
    return f"{BUCKET}/gfs.{ymd}/{CYCLE:02d}/atmos/gfs.t{CYCLE:02d}z.pgrb2.0p25.f{fh:03d}"


def idx_name(run_date, fh):
    return f"gfs_{run_date:%Y%m%d}_t{CYCLE:02d}z_f{fh:03d}.idx"


def msg_name(run_date, fh, short):
    return f"gfs_{run_date:%Y%m%d}_t{CYCLE:02d}z_f{fh:03d}_{short}.grib2"


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def read_sidecar(path):
    meta = {}
    p = Path(str(path) + ".meta.txt")
    if not p.exists():
        return None
    for line in p.read_text().splitlines():
        if ": " in line:
            k, v = line.split(": ", 1)
            meta[k.strip()] = v.strip()
    return meta


def cached_ok(path):
    """True when the file and its sidecar exist and the SHA-256 agrees."""
    meta = read_sidecar(path)
    if meta is None or not path.exists():
        return False
    return meta.get("sha256") == sha256(path.read_bytes())


def write_sidecar(path, fields):
    lines = [f"{k}: {v}" for k, v in fields.items()]
    Path(str(path) + ".meta.txt").write_text("\n".join(lines) + "\n")


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(url, byte_range=None):
    headers = {"Range": f"bytes={byte_range}"} if byte_range else {}
    r = session().get(url, headers=headers, timeout=120)
    if byte_range and r.status_code != 206:
        raise RuntimeError(f"HTTP {r.status_code} for range {byte_range}")
    if not byte_range and r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    return r.content


def with_one_retry(fn, counters, key):
    try:
        return fn()
    except Exception as first:  # noqa: BLE001 - every failure gets one retry
        inc(counters, key)
        time.sleep(2)
        try:
            return fn()
        except Exception as second:  # noqa: BLE001
            raise RuntimeError(f"failed twice: first={first!r}; second={second!r}")


def get_idx(run_date, fh, counters):
    path = CACHE / idx_name(run_date, fh)
    if cached_ok(path):
        return path.read_text()
    url = file_url(run_date, fh) + ".idx"

    def go():
        data = fetch(url)
        text = data.decode("ascii")
        if not text.startswith("1:0:"):
            raise RuntimeError("idx does not start with '1:0:'")
        return data

    data = with_one_retry(go, counters, "idx_retries")
    path.write_bytes(data)
    write_sidecar(path, {
        "url": url,
        "byte_range": "whole file",
        "pulled_utc": now_utc(),
        "bytes": len(data),
        "sha256": sha256(data),
    })
    return data.decode("ascii")


def parse_idx(text):
    rows = []
    for line in text.strip().splitlines():
        parts = line.split(":")
        rows.append({"n": int(parts[0]), "offset": int(parts[1]), "d": parts[2],
                     "var": parts[3], "level": parts[4], "step": parts[5]})
    return rows


def find_range(rows, var, level, step, run_date):
    hits = [i for i, r in enumerate(rows)
            if r["var"] == var and r["level"] == level and r["step"] == step]
    if len(hits) != 1:
        raise RuntimeError(f"expected 1 idx line for {var}:{level}:{step}, found {len(hits)}")
    i = hits[0]
    if rows[i]["d"] != f"d={run_date:%Y%m%d}{CYCLE:02d}":
        raise RuntimeError(f"idx run stamp {rows[i]['d']} does not match run date")
    start = rows[i]["offset"]
    if i + 1 < len(rows):
        return f"{start}-{rows[i + 1]['offset'] - 1}", rows[i + 1]["offset"] - start
    return f"{start}-", None


def pull_run(run_date, target_date, counters, failures):
    idx_text = {}
    for fh in FHOURS:
        try:
            idx_text[fh] = parse_idx(get_idx(run_date, fh, counters))
        except Exception as e:  # noqa: BLE001
            idx_text[fh] = None
            with _count_lock:
                failures.append([f"{run_date}", CYCLE, fh, "idx", "", f"{target_date}", repr(e)])
    for fh, var, level, step, short in MESSAGES:
        path = CACHE / msg_name(run_date, fh, short)
        if cached_ok(path):
            inc(counters, "skipped_cached")
            continue
        if idx_text[fh] is None:
            with _count_lock:
                failures.append([f"{run_date}", CYCLE, fh, var, level, f"{target_date}", "no idx"])
            continue
        url = file_url(run_date, fh)
        try:
            byte_range, expected = find_range(idx_text[fh], var, level, step, run_date)

            def go():
                data = fetch(url, byte_range)
                if expected is not None and len(data) != expected:
                    raise RuntimeError(f"got {len(data)} bytes, expected {expected}")
                if data[:4] != b"GRIB" or data[-4:] != b"7777":
                    raise RuntimeError("bad magic markers (not a complete GRIB2 message)")
                return data

            data = with_one_retry(go, counters, "msg_retries")
        except Exception as e:  # noqa: BLE001
            with _count_lock:
                failures.append([f"{run_date}", CYCLE, fh, var, level, f"{target_date}", repr(e)])
            continue
        path.write_bytes(data)
        idx_path = CACHE / idx_name(run_date, fh)
        write_sidecar(path, {
            "url": url,
            "byte_range": byte_range,
            "idx_url": url + ".idx",
            "idx_sha256": sha256(idx_path.read_bytes()),
            "variable": var,
            "level": level,
            "idx_step": step,
            "run_date": f"{run_date}",
            "cycle": CYCLE,
            "fhour": fh,
            "station_day": f"RNO:{target_date}",
            "pulled_utc": now_utc(),
            "bytes": len(data),
            "sha256": sha256(data),
        })
        inc(counters, "fetched")


def plan():
    days = list(target_days())
    n_msg = len(days) * len(MESSAGES)
    n_idx = len(days) * len(FHOURS)
    print(f"target days: {days[0]} .. {days[-1]} = {len(days)}")
    print(f"messages per day: {len(MESSAGES)}  ->  total messages: {n_msg:,}")
    print(f".idx files per day: {len(FHOURS)}  ->  total .idx files: {n_idx:,}")
    # Size estimate from the sizes session 71 recorded for the same RNO messages.
    sizes = {}
    with open(SIZE_SOURCE) as f:
        for r in csv.DictReader(f):
            if "RNO" in r["station_days"]:
                sizes.setdefault((r["variable"], r["level"], r["idx_step"]), []).append(int(r["bytes"]))
    total = 0
    print("average message size at RNO (session 71 manifest, 9 samples each):")
    for fh, var, level, step, short in MESSAGES:
        s = sizes[(var, level, step)]
        avg = sum(s) / len(s)
        total += avg * len(days)
        print(f"  f{fh:03d} {var:6s} {level:18s} {step:20s} {avg:12,.0f} bytes")
    print(f"estimated message bytes: {total:,.0f}  (~{total / 1e9:.2f} GB)")
    print("expected by the session prompt: ~15,000 messages, ~13 GB")
    print(f"difference: messages {100 * (n_msg - 15000) / 15000:+.1f}%, "
          f"bytes {100 * (total / 1e9 - 13) / 13:+.1f}%")


def pull(workers):
    CACHE.mkdir(parents=True, exist_ok=True)
    DIAG.mkdir(parents=True, exist_ok=True)
    counters, failures = {}, []
    lock = threading.Lock()
    t0 = time.time()
    print(f"pull start (UTC): {now_utc()}")
    days = list(target_days())
    done = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(pull_run, d - dt.timedelta(days=1), d, counters, failures): d for d in days}
        for fut in as_completed(futs):
            fut.result()
            with lock:
                done += 1
                if done % 100 == 0 or done == len(days):
                    print(f"  {done}/{len(days)} days  fetched={counters.get('fetched', 0)} "
                          f"cached={counters.get('skipped_cached', 0)} failures={len(failures)} "
                          f"elapsed={time.time() - t0:.0f}s", flush=True)
    print(f"pull end (UTC): {now_utc()}")
    print(f"counters: {counters}")
    failures.sort()
    with open(FAILURES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run_date", "cycle", "fhour", "variable", "level", "target_date", "reason"])
        w.writerows(failures)
    print(f"failures logged: {len(failures)} -> {FAILURES.relative_to(ROOT)}")


def manifest():
    rows = []
    for p in sorted(CACHE.glob("*.grib2")):
        meta = read_sidecar(p)
        if meta is None:
            print(f"NO SIDECAR: {p.name}")
            continue
        ok = meta["sha256"] == sha256(p.read_bytes()) and int(meta["bytes"]) == p.stat().st_size
        if not ok:
            print(f"SHA/SIZE MISMATCH: {p.name}")
            continue
        rows.append([p.name, meta["url"], meta["byte_range"], meta["idx_url"], meta["idx_sha256"],
                     meta["variable"], meta["level"], meta["idx_step"], meta["run_date"],
                     meta["cycle"], meta["fhour"], meta["station_day"], meta["pulled_utc"],
                     meta["bytes"], meta["sha256"]])
    with open(MANIFEST, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "url", "byte_range", "idx_url", "idx_sha256", "variable", "level",
                    "idx_step", "run_date", "cycle", "fhour", "station_day", "pulled_utc",
                    "bytes", "sha256"])
        w.writerows(rows)
    n_idx = len(list(CACHE.glob("*.idx")))
    total = sum(int(r[13]) for r in rows)
    pulled = sorted(r[12] for r in rows)
    print(f"manifest rows (messages): {len(rows):,}  bytes: {total:,}  .idx files: {n_idx:,}")
    if pulled:
        print(f"pull times (UTC): {pulled[0]} .. {pulled[-1]}")
    per = {}
    for r in rows:
        per[(r[10], r[5], r[6])] = per.get((r[10], r[5], r[6]), 0) + 1
    for k in sorted(per):
        print(f"  f{int(k[0]):03d} {k[1]:6s} {k[2]:18s} {per[k]:,}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--plan", action="store_true")
    g.add_argument("--pull", action="store_true")
    g.add_argument("--manifest", action="store_true")
    ap.add_argument("--workers", type=int, default=32)
    a = ap.parse_args()
    if a.plan:
        plan()
    elif a.pull:
        pull(a.workers)
    else:
        manifest()
    sys.exit(0)
