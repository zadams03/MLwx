"""Session 76, Step 4.1: pull every GRIB field behind KSFO's nine B+D,L,R,T
columns, 2021-03-24..2026-07-31, and interpolate each to KSFO's grid point.

Network. No model is fit and nothing is scored. Prints counts and
timestamps only; no feature value is printed (DECISIONS D67.6).

The recipe (DECISIONS D48.2, F89, F98, F100-F102; SPEC 7.2, 8.1, 8.2, 8.8):
- target day D, target hour 20:00 UTC: the GFS run of day D-1, cycle 18z
  (floor(20/6)*6), forecast hour f026 (24 + 20 mod 6); f023 for T's lead-3;
- from f026: TMP 2 m, TCDC entire atmosphere, UGRD/VGRD 10 m (B); TMP at
  925/850/700 mb (L); RH, DPT, SPFH at 2 m (D); PRMSL and PRES:surface (T);
  DSWRF:surface 24-26 h average, used directly at lead 26 (R);
- from f023: PRMSL (T's lead-3 value), same run;
- each message by byte range from the file's .idx (exact step match);
- bilinear to SPEC 3.4's grid point with eccodes' codes_grib_find_nearest,
  copied from the record (SPEC 8.8 G6).

Raw bytes are NOT kept (fetch-decode-discard, the F98 precedent; the full set
is ~22 GB and does not fit next to the existing cache). D47 is met by the
committed manifest: URL, byte range, .idx URL and SHA-256, pull time, size
and SHA-256 of every message, so every value can be re-fetched and checked.

SPEC 8.7 build requirements met here:
- item 2: a missing or non-finite grid value is rejected and logged as a
  failure (dropped, counted, never filled);
- item 3: each message's run date and time, and its full validity date AND
  hour, are checked, as are its parameter, level and step;
- item 4: the closing report compares each field's count with the expected
  full count (1,956 days), not with zero;
- item 5: the script writes only its own new session76 files, and refuses to
  start if the final manifest already exists.

Outputs (data/raw/diagnostics/session76/):
- session76_pull_manifest.csv     one row per requested message (OK or FAIL)
- session76_pull_failures.csv     the failed messages, with the reason
- session76_decoded_point_values.csv  one row per OK message: the value at
                                  KSFO's grid point, full precision, in the
                                  GRIB message's own units
While running, rows are appended to *.partial.csv files so an interrupted
pull can resume; they are merged and removed at the end.

Usage:
  .venv/bin/python scripts/session76_grib_pull.py --pull [--workers 32]
"""

import argparse
import csv
import datetime as dt
import hashlib
import math
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import eccodes as ec
import requests

ROOT = Path(__file__).resolve().parent.parent
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session76"
MANIFEST = DIAG / "session76_pull_manifest.csv"
FAILURES = DIAG / "session76_pull_failures.csv"
VALUES = DIAG / "session76_decoded_point_values.csv"
PART_MANIFEST = DIAG / "session76_pull_manifest.partial.csv"
PART_VALUES = DIAG / "session76_decoded_point_values.partial.csv"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
FIRST_TARGET = dt.date(2021, 3, 24)
LAST_TARGET = dt.date(2026, 7, 31)
HARD_END = dt.date(2026, 8, 1)          # nothing on or after this (D67.6)
HELD_OUT = (dt.date(2024, 8, 1), dt.date(2026, 7, 31))
STATION = "SFO"
TARGET_HOUR = 20
CYCLE = 18                              # floor(20/6)*6
LEAD = 26                               # 24 + 20 mod 6
GRID_LAT, GRID_LON = 37.54637, -122.34375   # SPEC 3.4, session 76 Step 2.4

# field -> (fhour, idx var, idx level, idx step,
#           (discipline, category, number, typeOfFirstFixedSurface, level,
#            stepType, startStep, endStep))
# Identity codes as verified at RNO in session 72 (same files); DSWRF is
# NCEP's local 0/4/192 (F111.4).
FIELDS = {
    "tmp2m":    (26, "TMP", "2 m above ground", "26 hour fcst", (0, 0, 0, 103, 2, "instant", 26, 26)),
    "tcdc":     (26, "TCDC", "entire atmosphere", "26 hour fcst", (0, 6, 1, 10, 0, "instant", 26, 26)),
    "ugrd10m":  (26, "UGRD", "10 m above ground", "26 hour fcst", (0, 2, 2, 103, 10, "instant", 26, 26)),
    "vgrd10m":  (26, "VGRD", "10 m above ground", "26 hour fcst", (0, 2, 3, 103, 10, "instant", 26, 26)),
    "t925":     (26, "TMP", "925 mb", "26 hour fcst", (0, 0, 0, 100, 925, "instant", 26, 26)),
    "t850":     (26, "TMP", "850 mb", "26 hour fcst", (0, 0, 0, 100, 850, "instant", 26, 26)),
    "t700":     (26, "TMP", "700 mb", "26 hour fcst", (0, 0, 0, 100, 700, "instant", 26, 26)),
    "rh2m":     (26, "RH", "2 m above ground", "26 hour fcst", (0, 1, 1, 103, 2, "instant", 26, 26)),
    "dpt2m":    (26, "DPT", "2 m above ground", "26 hour fcst", (0, 0, 6, 103, 2, "instant", 26, 26)),
    "spfh2m":   (26, "SPFH", "2 m above ground", "26 hour fcst", (0, 1, 0, 103, 2, "instant", 26, 26)),
    "prmsl":    (26, "PRMSL", "mean sea level", "26 hour fcst", (0, 3, 1, 101, 0, "instant", 26, 26)),
    "pres_sfc": (26, "PRES", "surface", "26 hour fcst", (0, 3, 0, 1, 0, "instant", 26, 26)),
    "dswrf":    (26, "DSWRF", "surface", "24-26 hour ave fcst", (0, 4, 192, 1, 0, "avg", 24, 26)),
    "prmsl_m3": (23, "PRMSL", "mean sea level", "23 hour fcst", (0, 3, 1, 101, 0, "instant", 23, 23)),
}
FHOURS = sorted({v[0] for v in FIELDS.values()})

MAN_COLS = ["target_date", "field", "run_date", "cycle", "fhour", "variable", "level", "idx_step",
            "url", "byte_range", "idx_url", "idx_sha256", "pulled_utc", "bytes", "sha256",
            "status", "detail"]
VAL_COLS = ["station", "target_date", "field", "value", "units", "validity"]

_local = threading.local()
_lock = threading.Lock()


def http():
    if not hasattr(_local, "s"):
        _local.s = requests.Session()
        _local.s.headers.update({"User-Agent": "MLwx/session76"})
    return _local.s


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def target_days():
    d = FIRST_TARGET
    while d <= LAST_TARGET:
        yield d
        d += dt.timedelta(days=1)


def file_url(run_date, fh):
    return (f"{BUCKET}/gfs.{run_date:%Y%m%d}/{CYCLE:02d}/atmos/"
            f"gfs.t{CYCLE:02d}z.pgrb2.0p25.f{fh:03d}")


def fetch(url, byte_range=None):
    headers = {"Range": f"bytes={byte_range}"} if byte_range else {}
    r = http().get(url, headers=headers, timeout=120)
    if byte_range and r.status_code != 206:
        raise RuntimeError(f"HTTP {r.status_code} for range {byte_range}")
    if not byte_range and r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}")
    return r.content


def with_one_retry(fn):
    try:
        return fn()
    except Exception as first:  # noqa: BLE001 - every failure gets one retry
        time.sleep(2)
        try:
            return fn()
        except Exception as second:  # noqa: BLE001
            raise RuntimeError(f"failed twice: first={first!r}; second={second!r}")


def parse_idx(text, run_date):
    rows = []
    for line in text.strip().splitlines():
        p = line.split(":")
        rows.append({"offset": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5]})
    return rows


def find_range(rows, var, level, step, run_date):
    hits = [i for i, r in enumerate(rows) if r["var"] == var and r["level"] == level and r["step"] == step]
    if len(hits) != 1:
        raise RuntimeError(f"expected 1 idx line for {var}:{level}:{step}, found {len(hits)}")
    i = hits[0]
    if rows[i]["d"] != f"d={run_date:%Y%m%d}{CYCLE:02d}":
        raise RuntimeError(f"idx run stamp {rows[i]['d']} does not match the run")
    start = rows[i]["offset"]
    if i + 1 < len(rows):
        return f"{start}-{rows[i + 1]['offset'] - 1}", rows[i + 1]["offset"] - start
    return f"{start}-", None


def bilinear_from_gid(gid, lat, lon):
    """Copied from the record (session49_upper_air_pull.py l.148-171, SPEC 8.8
    G6), with SPEC 8.7 item 2 added: each of the four neighbour values must
    be finite and not the message's missing value."""
    neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    missing = ec.codes_get_double(gid, "missingValue")
    bitmap = ec.codes_get_long(gid, "bitmapPresent")
    for n in neighbours:
        if not math.isfinite(n.value) or (bitmap and n.value == missing):
            raise ValueError("missing or non-finite grid value")
    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        lat_span = max(n.lat for n in neighbours) - min(n.lat for n in neighbours)
        lon_span = max(n.lon for n in neighbours) - min(n.lon for n in neighbours)
        if lat_span < 1e-6 or lon_span < 1e-6:
            return min(neighbours, key=lambda n: n.distance).value
        raise ValueError(f"unexpected neighbour layout: {[(n.lat, n.lon) for n in neighbours]}")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    return ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
            + dlat * (1 - dlon) * v10 + dlat * dlon * v11)


def decode(data, identity, run_date, fh):
    """Check the message's identity, run, and full validity date and hour
    (SPEC 8.7 item 3), then interpolate. Returns (value, units, validity)."""
    gid = ec.codes_new_from_message(data)
    try:
        got = (ec.codes_get_long(gid, "discipline"), ec.codes_get_long(gid, "parameterCategory"),
               ec.codes_get_long(gid, "parameterNumber"), ec.codes_get_long(gid, "typeOfFirstFixedSurface"),
               ec.codes_get_long(gid, "level"), ec.codes_get_string(gid, "stepType"),
               ec.codes_get_long(gid, "startStep"), ec.codes_get_long(gid, "endStep"))
        if got != identity:
            raise ValueError(f"identity {got} != expected {identity}")
        if (ec.codes_get_long(gid, "dataDate") != int(f"{run_date:%Y%m%d}")
                or ec.codes_get_long(gid, "dataTime") != CYCLE * 100):
            raise ValueError("run date/time mismatch")
        valid = dt.datetime(run_date.year, run_date.month, run_date.day, CYCLE) + dt.timedelta(hours=fh)
        vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
        if vd != int(f"{valid:%Y%m%d}") or vt != valid.hour * 100:
            raise ValueError(f"validity {vd} {vt:04d} != expected {valid:%Y%m%d %H%M}")
        value = bilinear_from_gid(gid, GRID_LAT, GRID_LON)
        if not math.isfinite(value):
            raise ValueError("non-finite interpolated value")
        return value, ec.codes_get_string(gid, "units"), f"{vd} {vt:04d}"
    finally:
        ec.codes_release(gid)


def pull_day(target_date):
    """Fetch, check and decode all 14 messages for one target day. Returns
    (manifest_rows, value_rows). Nothing is kept on disk here."""
    run_date = target_date - dt.timedelta(days=1)
    man, vals = [], []
    idx = {}
    for fh in FHOURS:
        url = file_url(run_date, fh) + ".idx"
        try:
            raw = with_one_retry(lambda: fetch(url))
            text = raw.decode("ascii")
            if not text.startswith("1:0:"):
                raise RuntimeError("idx does not start with '1:0:'")
            idx[fh] = (parse_idx(text, run_date), sha256(raw), url)
        except Exception as e:  # noqa: BLE001
            idx[fh] = (None, "", url, repr(e))
    for field, (fh, var, level, step, identity) in FIELDS.items():
        url = file_url(run_date, fh)
        base = [target_date.isoformat(), field, run_date.isoformat(), CYCLE, fh, var, level, step, url]
        rows, idx_sha, idx_url = idx[fh][0], idx[fh][1], idx[fh][2]
        if rows is None:
            man.append(base + ["", idx_url, "", now_utc(), "", "", "FAIL", f"idx: {idx[fh][3]}"])
            continue
        try:
            byte_range, expected = find_range(rows, var, level, step, run_date)
        except Exception as e:  # noqa: BLE001
            man.append(base + ["", idx_url, idx_sha, now_utc(), "", "", "FAIL", repr(e)])
            continue
        pulled = now_utc()
        try:
            def go():
                data = fetch(url, byte_range)
                if expected is not None and len(data) != expected:
                    raise RuntimeError(f"got {len(data)} bytes, expected {expected}")
                if data[:4] != b"GRIB" or data[-4:] != b"7777":
                    raise RuntimeError("bad magic markers (not a complete GRIB2 message)")
                return data
            data = with_one_retry(go)
        except Exception as e:  # noqa: BLE001
            man.append(base + [byte_range, idx_url, idx_sha, pulled, "", "", "FAIL", repr(e)])
            continue
        digest = sha256(data)
        try:
            value, units, validity = decode(data, identity, run_date, fh)
        except Exception as e:  # noqa: BLE001
            man.append(base + [byte_range, idx_url, idx_sha, pulled, len(data), digest, "FAIL",
                               f"decode: {e!r}"])
            continue
        man.append(base + [byte_range, idx_url, idx_sha, pulled, len(data), digest, "OK", ""])
        vals.append([STATION, target_date.isoformat(), field, repr(value), units, validity])
    return man, vals


def read_csv(path):
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def append(path, cols, rows):
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(cols)
        w.writerows(rows)


def window(d):
    if d < HELD_OUT[0]:
        return "before 2024-08-01"
    if d <= dt.date(2025, 7, 31):
        return "held-out 2024-25"
    return "held-out 2025-26"


def main(workers):
    if MANIFEST.exists():
        sys.exit(f"STOP: {MANIFEST.relative_to(ROOT)} already exists; not overwriting (SPEC 8.7 item 5).")
    DIAG.mkdir(parents=True, exist_ok=True)
    days = list(target_days())
    assert days[0] == FIRST_TARGET and days[-1] == LAST_TARGET and max(days) < HARD_END
    assert len(days) == 1956, len(days)

    done = {}
    for r in read_csv(PART_MANIFEST):
        done[r["target_date"]] = done.get(r["target_date"], 0) + 1
    finished = {d for d, n in done.items() if n == len(FIELDS)}
    partial_days = {d for d, n in done.items() if n != len(FIELDS)}
    if partial_days:
        sys.exit(f"STOP: partial manifest has incomplete days {sorted(partial_days)[:5]}")
    todo = [d for d in days if d.isoformat() not in finished]
    print(f"pull start (UTC): {now_utc()}")
    print(f"target days {days[0]} .. {days[-1]} = {len(days)}; fields per day {len(FIELDS)}; "
          f"messages {len(days) * len(FIELDS):,}; already done {len(finished)} days; to do {len(todo)}")
    t0 = time.time()
    n = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(pull_day, d): d for d in todo}
        for fut in as_completed(futs):
            man, vals = fut.result()
            with _lock:
                append(PART_MANIFEST, MAN_COLS, man)
                append(PART_VALUES, VAL_COLS, vals)
                n += 1
                if n % 100 == 0 or n == len(todo):
                    print(f"  {n}/{len(todo)} days  elapsed={time.time() - t0:.0f}s", flush=True)
    print(f"pull end (UTC): {now_utc()}")

    man = read_csv(PART_MANIFEST)
    vals = read_csv(PART_VALUES)
    man.sort(key=lambda r: (r["target_date"], r["field"]))
    vals.sort(key=lambda r: (r["target_date"], r["field"]))
    with open(MANIFEST, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MAN_COLS)
        w.writeheader()
        w.writerows(man)
    fails = [r for r in man if r["status"] != "OK"]
    with open(FAILURES, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=MAN_COLS)
        w.writeheader()
        w.writerows(fails)
    with open(VALUES, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=VAL_COLS)
        w.writeheader()
        w.writerows(vals)
    PART_MANIFEST.unlink()
    PART_VALUES.unlink()

    # ---- counts only (SPEC 8.7 item 4: against the full expected count) ----
    ok = [r for r in man if r["status"] == "OK"]
    print(f"\nmanifest rows {len(man):,} (expected {len(days) * len(FIELDS):,}); OK {len(ok):,}; "
          f"FAIL {len(fails)}; value rows {len(vals):,}")
    print(f"bytes fetched (OK messages): {sum(int(r['bytes']) for r in ok):,}")
    pulls = sorted(r["pulled_utc"] for r in man if r["pulled_utc"])
    print(f"pull times (UTC): {pulls[0]} .. {pulls[-1]}")
    expected = {"before 2024-08-01": 1226, "held-out 2024-25": 365, "held-out 2025-26": 365}
    print("\nOK messages per field, per window, against the expected full count:")
    print(f"{'field':10s} " + " ".join(f"{w:>20s}" for w in expected) + f" {'total':>12s}")
    for field in FIELDS:
        per = {w: 0 for w in expected}
        for r in ok:
            if r["field"] == field:
                per[window(dt.date.fromisoformat(r["target_date"]))] += 1
        cells = " ".join(f"{per[w]:>9d} of {expected[w]:>5d}   " for w in expected)
        print(f"{field:10s} {cells} {sum(per.values()):>5d} of 1956")
    if fails:
        print("\nfailures (target_date, field, reason):")
        for r in fails:
            print(f"  {r['target_date']} {r['field']:9s} {r['detail'][:150]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", action="store_true", required=True)
    ap.add_argument("--workers", type=int, default=32)
    a = ap.parse_args()
    main(a.workers)
