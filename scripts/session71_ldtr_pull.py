"""Session 71 Steps 1 and 2: recover the audit 68a sample, write out the L, D,
T, R recipe, list the GRIB messages, and (without --plan) pull them.

    .venv/bin/python scripts/session71_ldtr_pull.py --plan   # Step 1, no network
    .venv/bin/python scripts/session71_ldtr_pull.py          # Step 2, network

Step 2 saves each message, byte for byte, under data/raw/grib/session71/
(gitignored, DECISIONS D47) with a .meta.txt sidecar, and writes a committed
manifest and failure log to data/raw/diagnostics/session71/. It refuses to
run if the manifest or any cache file already exists, so a re-run never
overwrites a raw file or a committed record (SPEC 2.3, SPEC 8.7 item 5).

A failed fetch gets one retry. A message that still fails is logged and its
values are counted as missing, never filled (SPEC 2.2). Nothing is decoded,
fitted or scored here.
"""

import csv
import hashlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import session71_sample as smp  # noqa: E402

ROOT = smp.ROOT
CACHE = ROOT / "data" / "raw" / "grib" / "session71"
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session71"
MANIFEST = DIAG / "session71_pull_manifest.csv"
FAILURES = DIAG / "session71_pull_failures.csv"

ATTEMPTS = 2  # one fetch plus one retry
TIMEOUT = 60
WORKERS = 8

MANIFEST_COLS = ["file", "url", "byte_range", "idx_url", "idx_sha256", "variable",
                 "level", "idx_step", "run_date", "cycle", "fhour", "station_days",
                 "pulled_utc", "bytes", "sha256"]

# Old manifests that recorded message sizes, for the Step 1 size estimate only.
# (family key in this plan) -> (manifest file, field_key used there)
OLD_SIZE_SOURCES = {
    "t925": "t925", "t850": "t850", "t700": "t700",
    "rh2m": "relative_humidity_2m", "dpt2m": "dew_point_2m",
    "spfh2m": "specific_humidity_2m",
    "prmsl": "pressure_msl_hpa", "pres_sfc": "pressure_surface_hpa",
    "prmsl_m3": "pressure_msl_lead_minus3_hpa",
}
OLD_MANIFESTS = [
    "session49/session49_pull_manifest.csv",
    "session51/session51_pull_manifest.csv",
    "session53/session53_pull_manifest.csv",
    "session63/session63_upper_air_pull_manifest.csv",
    "session63/session63_moisture_pull_manifest.csv",
    "session63/session63_pressure_pull_manifest.csv",
]

RECIPE = """\
The recipe, per feature, from the build scripts (used as the recipe only).

Shared by all four families
  - Source: GFS 0.25 deg GRIB2, s3 bucket noaa-gfs-bdp-pds, file
    gfs.YYYYMMDD/CC/atmos/gfs.tCCz.pgrb2.0p25.fFFF (s49:110-112, s51:117-119,
    s53:115-117, s55:144-146).
  - Run and lead (F89, D48.2): run date = target date - 1 day; cycle =
    floor(HH/6)*6; lead = 24 + HH mod 6, HH = the airport's target hour
    (s49:104-107, s49:197-205). EGLC/LFPG 12z f024, DSM 18z f024,
    YSDU 00z f026, RNO 18z f026.
  - Byte range: from the .idx file; the message's line is matched on
    variable, level and step; the range runs from its start byte to the
    next line's start byte minus 1 (s49:132-145, s51:139-152, s53:137-150).
    The message must begin 'GRIB' and end '7777' (s49:238).
  - Grid value: bilinear interpolation (weighted by distance) from the four
    surrounding 0.25 deg grid points, found with eccodes
    codes_grib_find_nearest(npoints=4), to the SPEC 3.4 grid point
    (s49:148-171; the same function in s51:155, s53:153, s55:182).
  - No elevation correction on any L, D, T or R GRIB field (s49:11-16,
    s51:21-27, s53:25-28).
  - Valid-time check: L and D check the validity date only (s49:259-262,
    s51:267-270); T and R check the full date and hour (s53:179-187,
    388, 431; s55:208-216, 463).
  - The session 63 reserved-year build imports the same process_combo and
    build_combos functions (s63:139-256) and copies each build_joined's
    arithmetic into its own join_L/D/T/R (s63:258-400).

L -- lapse_rate_t2_t850 (session 49; s63 join_L 258-287)
  - Messages: TMP at 925, 850 and 700 mb, step 'LEAD hour fcst' (s49:89-93).
  - t925/t850/t700 = interpolated value in K minus 273.15 (s49:384),
    stored round(., 3) (s49:298-300).
  - t2m_raw is NOT pulled. It is recovered from the committed B column:
    t2m_raw = round(temperature_grib_c - correction_c, 3), correction_c from
    session37_elevation_correction_params.csv (s49:17-26, 295).
  - lapse_rate_t2_t850 = round(t2m_raw - t850_unrounded_C, 3) (s49:301).

D -- dewpoint_depression_t2m (session 51; s63 join_D 289-322)
  - Messages: RH, DPT and SPFH at '2 m above ground', step 'LEAD hour fcst'
    (s51:96-100).
  - dew_point_2m = K minus 273.15 (s51:509-510); RH (%) and SPFH (kg/kg)
    unconverted. Stored round(., 3), SPFH round(., 6) (s51:309-311).
  - t2m_raw as for L (s51:12-20, 306).
  - dewpoint_depression_t2m = round(t2m_raw - dew_point_unrounded_C, 3)
    (s51:312). This is the unfloored column; SPEC 8.1's floor is not applied.

T -- pressure_tendency_3h_hpa (session 53; s63 join_T 324-355)
  - Messages: PRMSL 'mean sea level' and PRES 'surface' at 'LEAD hour fcst',
    and PRMSL at 'LEAD-3 hour fcst' from the same run (s53:91-97, 349-449).
  - Pa / 100 -> hPa, each stored round(., 3) (s53:473-475).
  - pressure_tendency_3h_hpa = round(msl_hpa_rounded - msl_m3_hpa_rounded, 3)
    -- a difference of the two already-rounded values (s53:480).

R -- dswrf_2h_wm2 (session 55; s63 join_R 357-400)
  - Messages: DSWRF 'surface', the only DSWRF:surface line in the idx, an
    average from the last 6-hour reset to the file's forecast hour
    (s55:166-179, 445-467). Reset = 6*((fh-1)//6) (s55:137-141).
  - Lead-26 airports (YSDU, RNO): the f026 message is '24-26 hour ave fcst',
    already a 2-hour window; dswrf_2h = that value; the minus-2 column is
    blank (s55:555-557).
  - Lead-24 airports (EGLC, LFPG, DSM): f024 '18-24 hour ave fcst' (6 h) and
    f022 '18-22 hour ave fcst' (4 h) from the same run;
    dswrf_2h = (ave24*6 - ave22*4) / 2, using the unrounded values
    (s55:544-554).
  - W m-2, no unit change. Stored round(., 3) (s55:554, 560-562).
"""


def fmt_mb(n):
    return f"{n / 1e6:.1f} MB"


def step1():
    print("=" * 78)
    print("SESSION 71 STEP 1 -- sample, recipe and message list (no network)")
    print("=" * 78)

    sample = smp.recover_sample()
    print(f"\nSample recovered: {len(sample)} station-days. The audit 68a rule")
    print("(section 2.2: first, middle, last day of each window) gives exactly the")
    print("45 station-days audit 68a printed in its section 4.2, in the same order.")
    print("Audit 68a section 4.1 records no substitutions.\n")

    held = {}
    for fam, files in smp.FAMILY_FILES.items():
        for window, name in files.items():
            with open(smp.PROCESSED / name) as f:
                for row in csv.DictReader(f):
                    held.setdefault((row["station"], row["target_date"]), []).append(name)
    print(f"{'window':9s} {'station':7s} {'target date':11s} committed file(s) holding the row")
    for window, station, d in sample:
        files = held.get((station, d.isoformat()), [])
        print(f"{window:9s} {station:7s} {d.isoformat():11s} {len(files)} files: {', '.join(files)}")

    print("\n" + RECIPE)

    plan = smp.build_plan(sample)
    sizes = {}
    for rel in OLD_MANIFESTS:
        with open(ROOT / "data" / "raw" / "diagnostics" / rel) as f:
            for row in csv.DictReader(f):
                if row["status"] != "OK" or "bytes=" not in row["detail"]:
                    continue
                key = row.get("level_key") or row.get("field_key")
                n = int(row["detail"].split("bytes=")[1].split()[0])
                sizes[(row["run_date"], int(row["cycle"]), int(row["lead"]), key)] = n

    print("GRIB messages needed (one row per unique message; shared messages such")
    print("as EGLC+LFPG at 12z f024 are fetched once):")
    print(f"{'file':52s} {'var':5s} {'level':17s} {'idx step':22s} {'old size':>10s}")
    known, n_known = 0, 0
    idx_files = set()
    per_family = {}
    for mid, (m, users) in plan.items():
        idx_files.add((m["run_date"], m["cycle"], m["fhour"]))
        per_family[m["family"]] = per_family.get(m["family"], 0) + 1
        old = sizes.get((m["run_date"].isoformat(), m["cycle"], m["fhour"],
                         OLD_SIZE_SOURCES.get(m["key"])))
        if old:
            known += old
            n_known += 1
        print(f"{smp.cache_name(m):52s} {m['var']:5s} {m['level']:17s} {m['idx_step']:22s} "
              f"{old if old else '-':>10}")
        print(f"    url {smp.file_url(m['run_date'], m['cycle'], m['fhour'])}  "
              f"(byte range from its .idx)  used by {', '.join(users)}")
    n = len(plan)
    mean = known / n_known if n_known else 0
    est = known + mean * (n - n_known)
    print(f"\nTotal: {n} GRIB messages ({', '.join(f'{k} {v}' for k, v in sorted(per_family.items()))}),"
          f" from {len(idx_files)} .idx files.")
    print(f"Size: {n_known} of {n} messages have a size in an earlier manifest, "
          f"{fmt_mb(known)} in all; the other {n - n_known} (DSWRF has no size on "
          f"record) are estimated at the mean, {fmt_mb(mean)} each.")
    print(f"Estimated download: about {fmt_mb(est)} plus {len(idx_files)} small .idx files.")
    return sample, plan


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(session, url, headers=None):
    """Two attempts. Returns (bytes, None) or (None, reason)."""
    reasons = []
    for attempt in range(1, ATTEMPTS + 1):
        try:
            r = session.get(url, headers=headers, timeout=TIMEOUT)
            if r.status_code in (200, 206):
                return r.content, None
            reasons.append(f"attempt {attempt}: HTTP {r.status_code}")
        except Exception as e:
            reasons.append(f"attempt {attempt}: {e}")
        if attempt < ATTEMPTS:
            time.sleep(2)
    return None, "; ".join(reasons)


def find_range(idx_text, var, level, step):
    """(start, end_inclusive, n_matches). end is None for the last line."""
    lines = idx_text.strip().split("\n")
    hits = []
    for i, line in enumerate(lines):
        p = line.split(":")
        if len(p) >= 6 and p[3] == var and p[4] == level and p[5] == step:
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
            hits.append((int(p[1]), end))
    if len(hits) != 1:
        return None, None, len(hits)
    return hits[0][0], hits[0][1], 1


def step2(plan):
    print("\n" + "=" * 78)
    print("SESSION 71 STEP 2 -- pull (network)")
    print("=" * 78)
    if MANIFEST.exists() or FAILURES.exists():
        sys.exit(f"STOP: {MANIFEST.name} or {FAILURES.name} already exists -- refusing to overwrite.")
    CACHE.mkdir(parents=True, exist_ok=True)
    existing = sorted(CACHE.iterdir())
    if existing:
        sys.exit(f"STOP: {CACHE} already holds {len(existing)} files -- refusing to overwrite raw data.")
    DIAG.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "MLwx/session71"})

    # 1. every .idx file, saved beside the messages
    idx_keys = sorted({(m["run_date"], m["cycle"], m["fhour"]) for m, _ in plan.values()})
    idx_text, idx_sha, failures = {}, {}, []

    def get_idx(key):
        url = smp.file_url(*key) + ".idx"
        body, err = fetch(session, url)
        return key, url, body, err, utc_now()

    with ThreadPoolExecutor(WORKERS) as ex:
        for key, url, body, err, when in ex.map(get_idx, idx_keys):
            if body is None:
                failures.append([smp.idx_cache_name(*key), url, "", when, err])
                continue
            path = CACHE / smp.idx_cache_name(*key)
            path.write_bytes(body)
            sha = hashlib.sha256(body).hexdigest()
            Path(str(path) + ".meta.txt").write_text(
                f"source: {url}\n"
                f"byte range requested: whole file\n"
                f"pulled (UTC): {when}\n"
                f"bytes saved: {len(body)}\n"
                f"sha256: {sha}\n")
            idx_text[key], idx_sha[key] = body.decode("utf-8"), sha
    print(f".idx files: {len(idx_keys)} requested, {len(idx_text)} saved, "
          f"{len(idx_keys) - len(idx_text)} failed")

    # 2. every message, by byte range
    def get_msg(item):
        m, users = item
        key = (m["run_date"], m["cycle"], m["fhour"])
        url = smp.file_url(*key)
        name = smp.cache_name(m)
        if key not in idx_text:
            return m, users, url, "", None, "its .idx file failed", utc_now()
        start, end, n = find_range(idx_text[key], m["var"], m["level"], m["idx_step"])
        if start is None:
            return m, users, url, "", None, f"{n} idx lines match '{m['var']}:{m['level']}:{m['idx_step']}'", utc_now()
        rng = f"{start}-{end}" if end is not None else f"{start}-"
        body, err = fetch(session, url, headers={"Range": f"bytes={rng}"})
        when = utc_now()
        if body is None:
            return m, users, url, rng, None, err, when
        if body[:4] != b"GRIB" or body[-4:] != b"7777":
            return m, users, url, rng, None, "not a complete GRIB2 message (magic markers)", when
        return m, users, url, rng, body, None, when

    rows = []
    with ThreadPoolExecutor(WORKERS) as ex:
        for m, users, url, rng, body, err, when in ex.map(get_msg, plan.values()):
            name = smp.cache_name(m)
            if body is None:
                failures.append([name, url, rng, when, err])
                continue
            path = CACHE / name
            path.write_bytes(body)
            sha = hashlib.sha256(body).hexdigest()
            key = (m["run_date"], m["cycle"], m["fhour"])
            Path(str(path) + ".meta.txt").write_text(
                f"source: {url}\n"
                f"idx source: {url}.idx (sha256 {idx_sha[key]})\n"
                f"byte range requested: {rng}\n"
                f"variable: {m['var']}:{m['level']}:{m['idx_step']}, forecast hour "
                f"f{m['fhour']:03d}, cycle {m['cycle']:02d}z, run date {m['run_date'].isoformat()}\n"
                f"used by station-days: {', '.join(users)}\n"
                f"pulled (UTC): {when}\n"
                f"bytes saved: {len(body)}\n"
                f"sha256: {sha}\n")
            rows.append([name, url, rng, url + ".idx", idx_sha[key], m["var"], m["level"],
                         m["idx_step"], m["run_date"].isoformat(), m["cycle"], m["fhour"],
                         " ".join(users), when, len(body), sha])

    rows.sort(key=lambda r: r[0])
    with open(MANIFEST, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(MANIFEST_COLS)
        w.writerows(rows)
    failures.sort(key=lambda r: r[0])
    with open(FAILURES, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["file", "url", "byte_range", "failed_utc", "reason"])
        w.writerows(failures)

    total = sum(r[13] for r in rows)
    times = sorted(r[12] for r in rows)
    print(f"messages: {len(plan)} requested, {len(rows)} saved, "
          f"{len(plan) - len(rows)} failed after one retry")
    print(f"bytes saved: {total} ({fmt_mb(total)})")
    if times:
        print(f"pull time (UTC): {times[0]} .. {times[-1]}")
    print(f"manifest: {MANIFEST.relative_to(ROOT)} ({len(rows)} rows)")
    print(f"failure log: {FAILURES.relative_to(ROOT)} ({len(failures)} rows)")
    for fl in failures:
        print(f"  FAILED {fl[0]}: {fl[4]}")


def main():
    sample, plan = step1()
    if "--plan" in sys.argv:
        return
    step2(plan)


if __name__ == "__main__":
    main()
