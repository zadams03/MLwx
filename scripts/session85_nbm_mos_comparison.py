"""Session 85: the NBM/MOS comparison on the spent years (DECISIONS D77).

Three modes, each run once:

  --gate     Offline. The reproduction gate (session prompt, Step 2).
             DSM and RNO: F109's B+D,L,R,T refit, following
             session62_reserved_confirm.run_confirm() step by step, with its
             guards as it applies them (as F125.1 did). KSFO looks A and B:
             F119's saved predictions, no refit. Each airport-look's model
             MAE and raw GFS MAE are compared at full precision with the
             recorded grid files. Writes nothing.
  --pull     Network. NBM CONUS core 2 m temperature (AWS
             noaa-nbm-grib2-pds) at DSM, RNO and KSFO, and GFS MOS (MAV)
             at KDSM (IEM mos.json), for the spent-year target days only
             (D77.1, D77.2). Writes only:
               data/raw/iem_mos/session85/  (raw MAV responses + .meta.txt)
               data/processed/session85_competitor_points.csv (+ .meta.txt)
             NBM GRIB bytes go to a temporary directory outside the repo
             and each message is deleted after its value is read.
  --compare  Offline. Re-runs the gate by the same route, then the
             comparison (Step 4) and D77.4's outcome band. Writes nothing.

Hard limit: no value valid after 2026-07-31T23:00 UTC is read. Every
valid time is checked before any value is read.

This is descriptive and decides direction only (D72.7, D77.3). It changes
no verdict. Nothing is refit differently, retuned, reselected or re-locked.
No existing script is edited; functions are imported read-only.
"""

import csv
import hashlib
import json
import math
import os
import shutil
import sys
import tempfile
import time
from datetime import date, datetime, timedelta, timezone

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MODES = ("--gate", "--pull", "--compare")
if len(sys.argv) != 2 or sys.argv[1] not in MODES:
    raise SystemExit(f"usage: python {os.path.basename(__file__)} "
                     f"{{{'|'.join(MODES)}}}")
MODE = sys.argv[1]

RECORD_F109 = os.path.join(HERE, "session62_reserved_confirm.py")
RECORD_F109_SHA256 = \
    "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4"
PROCESSED = os.path.join(ROOT, "data", "processed")
KSFO_PRED = os.path.join(PROCESSED, "session78_ksfo_looks_predictions.csv")
KSFO_PRED_SHA256 = \
    "b4b46adc266ecb5475f253e5b20d02c6505d02af2bd578426095d6ef7f8ad78e"
F109_GRID = os.path.join(PROCESSED, "session63_reserved_confirm_grid.csv")
F119_GRID = os.path.join(PROCESSED, "session78_ksfo_looks_grid.csv")
POINTS_CSV = os.path.join(PROCESSED, "session85_competitor_points.csv")
POINTS_META = POINTS_CSV[:-4] + ".meta.txt"
MOS_DIR = os.path.join(ROOT, "data", "raw", "iem_mos", "session85")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if MODE in ("--gate", "--compare"):
    if sha256(RECORD_F109) != RECORD_F109_SHA256:
        raise SystemExit("STOP: session62_reserved_confirm.py's SHA-256 is "
                         "not D70.2's")
    # Importing the record script runs its libomp loader shim (D24), which
    # may restart this process once; the check above then runs again.
    import session62_reserved_confirm as s62  # noqa: E402
    import lightgbm as lgb  # noqa: E402

import numpy as np  # noqa: E402

# ------------------------------------------------------------------ constants

LIMIT_VALID = datetime(2026, 7, 31, 23, 0)   # nothing valid after this
FORBIDDEN_FROM = date(2026, 8, 1)

# SPEC 3.4: station code -> (latitude, longitude, target hour UTC).
STATIONS = {
    "DSM": (41.534, -93.6531, 18),
    "RNO": (39.4839, -119.7711, 20),
    "SFO": (37.619, -122.3749, 20),
}

# The four airport-looks (D77.3), in the comparison's order.
LOOKS = [
    ("DSM", "F109", date(2024, 8, 1), date(2025, 7, 31)),
    ("RNO", "F109", date(2024, 8, 1), date(2025, 7, 31)),
    ("SFO", "A", date(2024, 8, 1), date(2025, 7, 31)),
    ("SFO", "B", date(2025, 8, 1), date(2026, 7, 31)),
]
MAV_LOOK = ("DSM", "F109", date(2024, 8, 1), date(2025, 7, 31))


def look_name(st, lk):
    return f"{st} ({lk})" if st != "SFO" else f"KSFO look {lk}"


def cycle_and_lead(d, hour):
    """SPEC 7.2 / F5 / F89: run at floor(H/6)x6 UTC on D-1, lead
    24 + (H mod 6). Returns (cycle datetime, lead hours, valid datetime)."""
    cyc = datetime.combine(d - timedelta(days=1), datetime.min.time()) \
        + timedelta(hours=(hour // 6) * 6)
    lead = 24 + hour % 6
    valid = cyc + timedelta(hours=lead)
    assert valid == datetime.combine(d, datetime.min.time()) \
        + timedelta(hours=hour)
    return cyc, lead, valid


def days(a, b):
    return [a + timedelta(i) for i in range((b - a).days + 1)]


# ======================================================================
# Step 2: the reproduction gate (shared by --gate and --compare)
# ======================================================================

def read_recorded():
    """Recorded full-precision MAEs and day counts."""
    rec = {}
    with open(F109_GRID) as f:
        for r in csv.DictReader(f):
            if r["station"] in ("DSM", "RNO"):
                # F109: 365 test days at both (F109, F122.4, F125.2).
                rec[(r["station"], "F109")] = dict(
                    model=r["final_mae"], raw=r["raw_mae"], n=365)
    with open(F119_GRID) as f:
        for r in csv.DictReader(f):
            if r["row_type"] != "rung":
                continue
            k = ("SFO", r["look"])
            rec.setdefault(k, {})
            if r["name"] == "B+D,L,R,T":
                rec[k]["model"] = r["value"]
                rec[k]["n"] = int(r["n"])
            elif r["name"] == "raw_gfs":
                rec[k]["raw"] = r["value"]
    return rec


def f109_rows(stations):
    """DSM and RNO per-day rows, following run_confirm() step by step."""
    l_all, hits_l = s62.load_family("L", ["lapse_rate_t2_t850"])
    d_all, hits_d = s62.load_family("D", ["dewpoint_depression_t2m"])
    t_all, hits_t = s62.load_family("T", ["pressure_tendency_3h_hpa"])
    r_all, hits_r = s62.load_family("R", ["dswrf_2h_wm2"])
    if hits_l or hits_d or hits_t or hits_r:  # run_confirm()'s first guard
        raise AssertionError("STOP: reserved-year rows found inside the "
                             "L/D/T/R source files themselves (D51).")
    base_all = s62.load_base_unfiltered()
    merged = s62.build_complete_case(base_all, l_all, d_all, t_all, r_all)
    fold = s62.CONFIRMATION_FOLD
    ts, te = fold["test_start"], fold["test_end"]
    tr_s, tr_e = fold["train_start"], fold["train_end"]
    for st in s62.AIRPORTS:  # run_confirm()'s second guard, all airports
        if sum(1 for d in merged[st] if ts <= d <= te) == 0:
            raise RuntimeError(f"STOP (D58 reserved-year feature-data gap): "
                               f"{st}")
    out = {}
    for st in stations:
        obs_all, _, _ = s62.load_obs_all(st, s62.AIRPORTS[st])
        train_raw = {d: r for d, r in merged[st].items() if tr_s <= d <= tr_e}
        test_raw = {d: r for d, r in merged[st].items() if ts <= d <= te}
        train_rows, _ = s62.join_obs(st, train_raw, obs_all)
        test_rows, no_obs = s62.join_obs(st, test_raw, obs_all)
        for r in test_rows:
            if r["date"] >= FORBIDDEN_FROM:
                raise SystemExit("STOP: a date on or after 2026-08-01")
        _, e_model = s62.fit_and_score(set(s62.FINAL_CODES),
                                       s62.FINAL_FEATURE_KEYS,
                                       train_rows, test_rows)
        rows = []
        for r, em in zip(test_rows, e_model):
            rows.append(dict(date=r["date"], obs=r["obs"],
                             pred=r["obs"] + em, raw=r["fc"],
                             e_model=em, e_raw=r["fc"] - r["obs"]))
        out[(st, "F109")] = dict(rows=rows, n_train=len(train_rows),
                                 no_obs_dropped=no_obs,
                                 mae_model=s62.mae(e_model),
                                 mae_raw=s62.mae([x["e_raw"] for x in rows]))
    return out


def f119_rows():
    """KSFO looks A and B per-day rows from the saved predictions."""
    out = {}
    for lk in "AB":
        rows = []
        with open(KSFO_PRED) as f:
            for r in csv.DictReader(f):
                if r["look"] != lk:
                    continue
                d = date.fromisoformat(r["target_date"])
                if d >= FORBIDDEN_FROM:
                    raise SystemExit("STOP: a date on or after 2026-08-01")
                obs = float(r["obs_c"])
                pred = float(r["BDLRT_c"])
                raw = float(r["raw_gfs_c"])
                rows.append(dict(date=d, obs=obs, pred=pred, raw=raw,
                                 e_model=pred - obs, e_raw=raw - obs))
        rows.sort(key=lambda x: x["date"])
        e_m = np.array([x["e_model"] for x in rows])
        e_r = np.array([x["e_raw"] for x in rows])
        out[("SFO", lk)] = dict(rows=rows,
                                mae_model=float(np.mean(np.abs(e_m))),
                                mae_raw=float(np.mean(np.abs(e_r))))
    return out


def run_gate():
    print("=" * 78)
    print("Step 2: the reproduction gate")
    print("=" * 78)
    print(f"  {os.path.relpath(RECORD_F109, ROOT)} SHA-256 "
          f"{sha256(RECORD_F109)} (D70.2: equal)")
    kp = sha256(KSFO_PRED)
    if kp != KSFO_PRED_SHA256:
        raise SystemExit("STOP: KSFO predictions SHA-256 is not F119.4's")
    print(f"  {os.path.relpath(KSFO_PRED, ROOT)} SHA-256 {kp} (F119.4: equal)")
    print(f"  {os.path.relpath(F109_GRID, ROOT)} SHA-256 {sha256(F109_GRID)}")
    print(f"  {os.path.relpath(F119_GRID, ROOT)} SHA-256 {sha256(F119_GRID)}")
    rec = read_recorded()
    res = {}
    res.update(f109_rows(["DSM", "RNO"]))
    res.update(f119_rows())
    passed = {}
    for st, lk, _, _ in LOOKS:
        k = (st, lk)
        r, want = res[k], rec[k]
        n = len(r["rows"])
        print(f"\n  {look_name(st, lk)}")
        if st != "SFO":
            print(f"    route: F109 refit (run_confirm() steps), n_train "
                  f"{r['n_train']}, no-obs dropped {r['no_obs_dropped']}")
        else:
            print("    route: F119 saved predictions, no refit")
        ok = True
        for name, got, w in (("model B+D,L,R,T", r["mae_model"], want["model"]),
                             ("raw GFS (GRIB)", r["mae_raw"], want["raw"])):
            eq = repr(float(got)) == repr(float(w))
            ok &= eq
            print(f"    {name:<16} recomputed {got!r:<22} recorded {w:<22} "
                  f"{'equal' if eq else 'DIFFERS'}")
        dok = n == want["n"]
        ok &= dok
        print(f"    days: {n} (recorded {want['n']})  "
              f"{'equal' if dok else 'DIFFER'}")
        print(f"    GATE: {'PASSED' if ok else 'FAILED -> no comparison'}")
        passed[k] = ok
    print(f"\n  gate passed: {sum(passed.values())} of {len(passed)} "
          f"airport-looks")
    return res, passed


# ======================================================================
# Step 3: the pull
# ======================================================================

NBM = "https://noaa-nbm-grib2-pds.s3.amazonaws.com/"
MOS_URL = "https://mesonet.agron.iastate.edu/api/1/mos.json"
SIZE_LIMIT = 20 * 10**9
RETRIES = 3
PAUSE = 0.2


class Missing(Exception):
    pass


def get(url, **kw):
    """GET with at most 3 retries, politely spaced. 404/403 -> Missing.
    Returns (response, tries)."""
    import requests
    last = None
    for i in range(RETRIES + 1):
        try:
            r = requests.get(url, timeout=(10, 120), **kw)
            if r.status_code in (403, 404):
                time.sleep(PAUSE)
                raise Missing(f"HTTP {r.status_code}")
            if r.status_code in (200, 206):
                time.sleep(PAUSE)
                return r, i + 1
            last = f"HTTP {r.status_code}"
        except requests.exceptions.RequestException as e:
            last = f"{type(e).__name__}: {e}"
        if i < RETRIES:
            time.sleep(5 * (i + 1))
    raise RuntimeError(f"request failed after {RETRIES} retries: {url} "
                       f"({last})")


def nbm_url(cyc, lead):
    return (f"{NBM}blend.{cyc:%Y%m%d}/{cyc:%H}/core/"
            f"blend.t{cyc:%H}z.core.f{lead:03d}.co.grib2")


META_KEYS = ["shortName", "name", "units", "typeOfLevel", "level",
             "stepType", "stepRange", "dataDate", "dataTime",
             "validityDate", "validityTime", "gridType", "Nx", "Ny",
             "DxInMetres", "DyInMetres", "latitudeOfFirstGridPointInDegrees",
             "longitudeOfFirstGridPointInDegrees", "LoVInDegrees",
             "Latin1InDegrees", "Latin2InDegrees", "packingType",
             "numberOfDataPoints", "discipline", "parameterCategory",
             "parameterNumber", "missingValue"]


def grib_meta(gid):
    import eccodes
    k = {}
    for key in META_KEYS:
        try:
            k[key] = eccodes.codes_get(gid, key)
        except Exception:
            k[key] = None
    return k


def pull_nbm(tmpdir):
    import eccodes
    print("=" * 78)
    print("Step 3.1: NBM CONUS core, 2 m temperature (deterministic)")
    print("=" * 78)
    print(f"  bucket: {NBM} (anonymous HTTPS)")
    print("  layout (as scripts/session82_source_probe.py): "
          "blend.YYYYMMDD/HH/core/blend.tHHz.core.fFFF.co.grib2 (+ .idx)")
    # The plan: (cycle, lead) -> [(station, look, target day)].
    plan = {}
    for st, lk, a, b in LOOKS:
        hour = STATIONS[st][2]
        for d in days(a, b):
            cyc, lead, valid = cycle_and_lead(d, hour)
            if valid > LIMIT_VALID:
                raise SystemExit(f"STOP: planned valid time {valid} is after "
                                 f"{LIMIT_VALID}; nothing requested")
            plan.setdefault((cyc, lead), []).append((st, lk, d, valid))
    keys = sorted(plan)
    n_targets = sum(len(v) for v in plan.values())
    print(f"  planned: {len(keys)} files for {n_targets} airport-look target "
          f"days (RNO and KSFO look A share files)")
    print(f"  latest planned valid time: "
          f"{max(v[3] for vs in plan.values() for v in vs)}")

    points, manifest = [], []
    counts = dict(files_ok=0, files_missing=0, idx_missing=0,
                  msg_zero_match=0, msg_multi_match=0, msg_check_failed=0,
                  value_missing=0, bytes=0, retried=0)
    missing_list = []
    gridpts = {st: {} for st in STATIONS}
    vcheck = {}
    t0 = time.time()
    for i, (cyc, lead) in enumerate(keys):
        url = nbm_url(cyc, lead)
        want = f"TMP:2 m above ground:{lead} hour fcst:"
        try:
            r, tries = get(url + ".idx")
            counts["retried"] += tries - 1
        except Missing as e:
            counts["idx_missing"] += 1
            missing_list.append((url + ".idx", str(e)))
            continue
        lines = r.text.splitlines()
        parsed = []
        for ln in lines:
            f = ln.split(":")
            parsed.append((int(f[0]), int(f[1]), f[2], ":".join(f[3:]), ln))
        if cyc.strftime("%Y-%m-%d %H") in ("2025-05-26 18", "2025-05-28 18") \
                and lead == 26:
            vcheck[cyc] = dict(idx_lines=len(lines))
        hits = [j for j, p in enumerate(parsed) if p[3] == want]
        if len(hits) != 1:
            key = "msg_zero_match" if not hits else "msg_multi_match"
            counts[key] += 1
            missing_list.append((url, f"{len(hits)} idx lines match"))
            continue
        j = hits[0]
        if parsed[j][2] != f"d={cyc:%Y%m%d%H}":
            counts["msg_check_failed"] += 1
            missing_list.append((url, f"idx date {parsed[j][2]}"))
            continue
        off = parsed[j][1]
        if j + 1 < len(parsed):
            end = parsed[j + 1][1] - 1
        else:
            import requests
            end = int(requests.head(url, timeout=(10, 60))
                      .headers["Content-Length"]) - 1
        try:
            r, tries = get(url, headers={"Range": f"bytes={off}-{end}"})
            counts["retried"] += tries - 1
        except Missing as e:
            counts["files_missing"] += 1
            missing_list.append((url, str(e)))
            continue
        if len(r.content) != end - off + 1:
            raise SystemExit(f"STOP: short read {len(r.content)} B for {url}")
        counts["bytes"] += len(r.content)
        path = os.path.join(tmpdir, "msg.grib2")
        with open(path, "wb") as fh:
            fh.write(r.content)
        with open(path, "rb") as fh:
            gid = eccodes.codes_grib_new_from_file(fh)
            meta = grib_meta(gid)
            vd, vt = meta["validityDate"], meta["validityTime"]
            valid = datetime.strptime(f"{vd}{int(vt):04d}", "%Y%m%d%H%M")
            if valid > LIMIT_VALID:
                eccodes.codes_release(gid)
                os.remove(path)
                print(f"  STOP NBM sub-step: message valid {valid} is after "
                      f"{LIMIT_VALID}; discarded without reading its value "
                      f"({url})")
                return None
            exp_valid = plan[(cyc, lead)][0][3]
            ok = (valid == exp_valid and meta["units"] == "K"
                  and meta["shortName"] == "2t")
            if not ok:
                eccodes.codes_release(gid)
                os.remove(path)
                counts["msg_check_failed"] += 1
                missing_list.append((url, f"check failed: valid {valid}, "
                                     f"units {meta['units']}, shortName "
                                     f"{meta['shortName']}"))
                continue
            if cyc in vcheck:
                vcheck[cyc]["meta"] = meta
            for st, lk, d, v in plan[(cyc, lead)]:
                lat, lon, _ = STATIONS[st]
                nn = eccodes.codes_grib_find_nearest(gid, lat, lon)[0]
                val = float(nn.value)
                if not math.isfinite(val) or val == meta["missingValue"]:
                    counts["value_missing"] += 1
                    missing_list.append((url, f"{st} {lk} {d}: missing value"))
                    continue
                gp = (round(nn.lat, 6), round(nn.lon, 6))
                gridpts[st].setdefault(gp, [0, nn.distance])
                gridpts[st][gp][0] += 1
                points.append(dict(airport=st, look=lk,
                                   target_date=d.isoformat(),
                                   competitor="nbm",
                                   cycle=cyc.strftime("%Y-%m-%dT%H:%MZ"),
                                   lead=lead,
                                   valid_time=v.strftime("%Y-%m-%dT%H:%MZ"),
                                   value_c=repr(val - 273.15),
                                   grid_lat=repr(nn.lat),
                                   grid_lon=repr(nn.lon)))
            eccodes.codes_release(gid)
        os.remove(path)
        counts["files_ok"] += 1
        manifest.append(f"{url} bytes={off}-{end} idx: {parsed[j][4]}")
        if counts["files_ok"] == 3:
            per = counts["bytes"] / 3
            proj = per * len(keys)
            print(f"\n  SIZE TRIAL: 3 messages, {counts['bytes']:,} B "
                  f"({per:,.0f} B per message); projected total for "
                  f"{len(keys)} files: {proj:,.0f} B ({proj / 1e9:.2f} GB)")
            if proj > SIZE_LIMIT:
                print("  STOP: projected total exceeds 20 GB")
                return None
            print("  projected total is under 20 GB; continuing\n")
        if (i + 1) % 100 == 0:
            print(f"  progress: {i + 1}/{len(keys)} files, "
                  f"{counts['bytes'] / 1e9:.2f} GB, "
                  f"{time.time() - t0:.0f} s", flush=True)

    print(f"\n  files: {len(keys)} planned; {counts['files_ok']} read; "
          f"idx missing {counts['idx_missing']}; file missing "
          f"{counts['files_missing']}; zero idx match "
          f"{counts['msg_zero_match']}; several idx matches "
          f"{counts['msg_multi_match']}; check failed "
          f"{counts['msg_check_failed']}; missing values "
          f"{counts['value_missing']}")
    print(f"  bytes fetched (messages): {counts['bytes']:,} "
          f"({counts['bytes'] / 1e9:.2f} GB); requests retried: "
          f"{counts['retried']}; time {time.time() - t0:.0f} s")
    for u, why in missing_list:
        print(f"    missing: {u}  ({why})")
    print("\n  NBM grid points (nearest neighbour, eccodes):")
    for st, g in gridpts.items():
        for (la, lo), (n, dist) in g.items():
            print(f"    {st}: grid point {la}, {lo}, distance {dist:.3f} km, "
                  f"used {n} times")
        print(f"    {st}: {'unchanged across the window' if len(g) == 1 else 'CHANGES across the window'}"
              f" ({len(g)} distinct)")
    print("\n  version check (report only): f026 18z .idx line counts and the "
          "TMP 2 m message")
    ks = sorted(vcheck)
    for c in ks:
        print(f"    {c:%Y-%m-%d %H}z f026: {vcheck[c]['idx_lines']} idx lines")
        print(f"      message: {vcheck[c].get('meta')}")
    if len(ks) == 2 and all("meta" in vcheck[c] for c in ks):
        a, b = vcheck[ks[0]]["meta"], vcheck[ks[1]]["meta"]
        skip = {"dataDate", "dataTime", "validityDate", "validityTime"}
        diff = [k for k in META_KEYS if k not in skip and a[k] != b[k]]
        print(f"    differing keys (dates excluded): {diff or 'none'}")
    return dict(points=points, manifest=manifest, counts=counts,
                missing=missing_list, gridpts=gridpts, n_files=len(keys))


def pull_mav():
    print("\n" + "=" * 78)
    print("Step 3.2: GFS MOS (MAV) at KDSM, IEM archive")
    print("=" * 78)
    print(f"  endpoint: {MOS_URL} (as scripts/session82_source_probe.py), "
          f"station KDSM, model GFS")
    st, lk, a, b = MAV_LOOK
    hour = STATIONS[st][2]
    got, points, missing = [], [], []
    for n, d in enumerate(days(a, b)):
        cyc, lead, valid = cycle_and_lead(d, hour)
        rt = cyc.strftime("%Y-%m-%d %H:%MZ")
        params = {"station": "KDSM", "model": "GFS", "runtime": rt}
        pulled = datetime.now(timezone.utc)
        try:
            r, _ = get(MOS_URL, params=params)
        except Missing as e:
            missing.append((d, f"HTTP {e}"))
            continue
        body = r.content
        rows = json.loads(body).get("data", [])
        fts = []
        for x in rows:
            s = str(x["ftime"]).replace("T", " ").rstrip("Z")[:16]
            fts.append(datetime.strptime(s, "%Y-%m-%d %H:%M"))
        if any(t > LIMIT_VALID for t in fts):
            print(f"  STOP MAV sub-step: run {rt} has a projection valid "
                  f"after {LIMIT_VALID}; discarded without reading values")
            return None
        if not rows:
            missing.append((d, "no rows"))
            if n == 2 and len(missing) == 3:
                print("  STOP MAV sub-step: the first three 18z runs returned "
                      "no rows (IEM has no 18z MAV runs?)")
                return None
            got.append(dict(runtime=rt, url=r.url, pulled=pulled, body=body,
                            n_rows=0))
            continue
        got.append(dict(runtime=rt, url=r.url, pulled=pulled, body=body,
                        n_rows=len(rows)))
        rts = {str(x.get("runtime", "")) for x in rows} - {""}
        if any(not t.startswith(cyc.strftime("%Y-%m-%d")) or
               cyc.strftime("%H:%M") not in t for t in rts):
            missing.append((d, f"runtime field {sorted(rts)} is not {rt}"))
            continue
        match = [x for x, t in zip(rows, fts) if t == valid]
        if len(match) != 1 or match[0].get("tmp") in (None, "", "M"):
            missing.append((d, f"{len(match)} rows at {valid}"))
            continue
        tmp_f = float(match[0]["tmp"])
        points.append(dict(airport=st, look=lk, target_date=d.isoformat(),
                           competitor="mav",
                           cycle=cyc.strftime("%Y-%m-%dT%H:%MZ"), lead=lead,
                           valid_time=valid.strftime("%Y-%m-%dT%H:%MZ"),
                           value_c=repr((tmp_f - 32.0) * 5.0 / 9.0),
                           grid_lat="", grid_lon=""))
        if n == 0:
            print(f"  first response: {len(rows)} projections, runtime field "
                  f"{sorted(rts)}, keys {sorted(rows[0].keys())}")
    print(f"  runs requested: {len(days(a, b))}; responses with rows: "
          f"{sum(1 for g in got if g['n_rows'])}; values: {len(points)}; "
          f"missing: {len(missing)}")
    for d, why in missing:
        print(f"    missing: {d} ({why})")
    return dict(got=got, points=points, missing=missing)


def run_pull():
    print("Session 85, --pull (DECISIONS D77.1, D77.2)")
    print(f"run at {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
          f" UTC")
    import eccodes
    import requests
    print(f"python {sys.version.split()[0]}, eccodes {eccodes.__version__}, "
          f"requests {requests.__version__}")
    for p in (MOS_DIR, POINTS_CSV, POINTS_META):
        if os.path.exists(p):
            raise SystemExit(f"STOP: {os.path.relpath(p, ROOT)} exists")
    tmpdir = tempfile.mkdtemp(prefix="session85_nbm_")
    print(f"temporary GRIB directory (outside the repo): {tmpdir}")
    try:
        nbm = pull_nbm(tmpdir)
    finally:
        shutil.rmtree(tmpdir)
        print(f"temporary directory deleted: exists now = "
              f"{os.path.exists(tmpdir)}")
    mav = pull_mav()

    print("\n" + "=" * 78)
    print("Step 3.3: writing files")
    print("=" * 78)
    if mav is not None:
        os.makedirs(MOS_DIR)
        lines = [
            "Session 85 raw GFS MOS (MAV) responses, IEM archive, saved "
            "unchanged (SPEC 2.3).",
            f"endpoint: {MOS_URL}",
            "one file per run: KDSM_GFS_<YYYYMMDD>T18Z.json; each exact "
            "query and its pull time (UTC) below.",
            "",
        ]
        for g in mav["got"]:
            fn = f"KDSM_GFS_{g['runtime'][:10].replace('-', '')}T18Z.json"
            with open(os.path.join(MOS_DIR, fn), "wb") as fh:
                fh.write(g["body"])
            lines.append(f"{fn}  pulled {g['pulled'].isoformat(timespec='seconds')}"
                         f"  query {g['url']}")
        with open(os.path.join(MOS_DIR, "session85_mav.meta.txt"), "w") as fh:
            fh.write("\n".join(lines) + "\n")
        print(f"  wrote {len(mav['got'])} raw MAV responses and "
              f"session85_mav.meta.txt under "
              f"{os.path.relpath(MOS_DIR, ROOT)}/")
    pts = (nbm["points"] if nbm else []) + (mav["points"] if mav else [])
    cols = ["airport", "look", "target_date", "competitor", "cycle", "lead",
            "valid_time", "value_c", "grid_lat", "grid_lon"]
    with open(POINTS_CSV, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(pts)
    meta = [
        "session85_competitor_points.csv: NBM and MAV point forecasts for "
        "the spent-year comparison (DECISIONS D77).",
        f"pull date (UTC): {datetime.now(timezone.utc).date().isoformat()}",
        f"NBM bucket: {NBM} (anonymous HTTPS)",
        "NBM message: the one .idx line exactly 'TMP:2 m above ground:<lead> "
        "hour fcst:'; value at the nearest grid point to the SPEC 3.4 "
        "station position (eccodes codes_grib_find_nearest), K - 273.15.",
        f"MAV: {MOS_URL}, station KDSM, model GFS, 18z runs; raw responses "
        f"in data/raw/iem_mos/session85/ (queries in session85_mav.meta.txt);"
        " tmp in whole degF, (F - 32) * 5 / 9.",
        "",
    ]
    if nbm:
        c = nbm["counts"]
        meta += [f"NBM counts: {nbm['n_files']} files planned, "
                 f"{c['files_ok']} read, idx missing {c['idx_missing']}, "
                 f"file missing {c['files_missing']}, zero idx match "
                 f"{c['msg_zero_match']}, several idx matches "
                 f"{c['msg_multi_match']}, check failed "
                 f"{c['msg_check_failed']}, missing values "
                 f"{c['value_missing']}, bytes {c['bytes']}"]
        meta += [f"NBM missing: {u} ({why})" for u, why in nbm["missing"]]
    else:
        meta += ["NBM sub-step stopped; no NBM rows."]
    if mav:
        meta += [f"MAV counts: {len(mav['got'])} responses, "
                 f"{len(mav['points'])} values, {len(mav['missing'])} "
                 f"missing"]
        meta += [f"MAV missing: {d} ({why})" for d, why in mav["missing"]]
    else:
        meta += ["MAV sub-step stopped; no MAV rows."]
    if nbm:
        meta += ["", "NBM files read (URL, byte range, .idx line):"]
        meta += nbm["manifest"]
    with open(POINTS_META, "w") as fh:
        fh.write("\n".join(meta) + "\n")
    n_by = {}
    for p in pts:
        k = (p["airport"], p["look"], p["competitor"])
        n_by[k] = n_by.get(k, 0) + 1
    print(f"  wrote {os.path.relpath(POINTS_CSV, ROOT)}: {len(pts)} rows "
          f"{dict(sorted(n_by.items()))}")
    print(f"  wrote {os.path.relpath(POINTS_META, ROOT)}")
    print(f"  SHA-256 {os.path.relpath(POINTS_CSV, ROOT)}: "
          f"{sha256(POINTS_CSV)}")


# ======================================================================
# Step 4: the comparison
# ======================================================================

N_BOOT = 10_000
BLOCK = 7
SEED = 85

# D77.7 version starts, by NBM cycle time. The hour of v5.0 and v5.0.14 is
# not given; 00z is assumed (only matters if the switch came after 18z).
NBM_SEGMENTS = [
    ("v4.2", datetime(2024, 5, 15, 0)),
    ("v4.3", datetime(2025, 5, 27, 12)),
    ("v5.0", datetime(2026, 5, 5, 0)),
    ("v5.0.14", datetime(2026, 7, 28, 0)),
]


def segment(cyc):
    name = None
    for nm, start in NBM_SEGMENTS:
        if cyc >= start:
            name = nm
    return name


def bootstrap(rng, em, er):
    """F125's moving-block bootstrap (D75.2), unchanged."""
    n = len(em)
    k = math.ceil(n / BLOCK)
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, k))
    idx = (starts[:, :, None] + np.arange(BLOCK)).reshape(N_BOOT, k * BLOCK)
    idx = idx[:, :n]
    mm = em[idx].mean(axis=1)
    mr = er[idx].mean(axis=1)
    d = mr - mm
    skill = 100.0 * (1.0 - mm / mr)
    return (np.percentile(d, [2.5, 97.5]), np.percentile(skill, [2.5, 97.5]))


def run_compare():
    print(f"Session 85, --compare (DECISIONS D77.3, D77.4)")
    print(f"run at {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python {sys.version.split()[0]}, numpy {np.__version__}, "
          f"lightgbm {lgb.__version__}")
    print(f"bootstrap: moving block, block {BLOCK}, {N_BOOT:,} resamples, "
          f"numpy.random.default_rng({SEED}), 95% percentile interval")
    res, passed = run_gate()

    print("\n" + "=" * 78)
    print("Step 4: the comparison")
    print("=" * 78)
    print(f"  points file: {os.path.relpath(POINTS_CSV, ROOT)} SHA-256 "
          f"{sha256(POINTS_CSV)}")
    comp = {}
    with open(POINTS_CSV) as f:
        for r in csv.DictReader(f):
            vt = datetime.strptime(r["valid_time"], "%Y-%m-%dT%H:%MZ")
            if vt > LIMIT_VALID:
                raise SystemExit("STOP: a points row is valid after the limit")
            k = (r["airport"], r["look"], r["competitor"])
            comp.setdefault(k, {})[date.fromisoformat(r["target_date"])] = (
                float(r["value_c"]),
                datetime.strptime(r["cycle"], "%Y-%m-%dT%H:%MZ"))

    rng = np.random.default_rng(SEED)
    plan = [(st, lk, "nbm") for st, lk, _, _ in LOOKS] + \
        [(MAV_LOOK[0], MAV_LOOK[1], "mav")]
    table, segs, band_in = [], [], {}
    for st, lk, cp in plan:
        name = f"{look_name(st, lk)} vs {cp.upper()}"
        print(f"\n  {name}")
        if not passed[(st, lk)]:
            print("    gate FAILED: no comparison")
            continue
        rows = res[(st, lk)]["rows"]
        cv = comp.get((st, lk, cp), {})
        use = [(r, cv[r["date"]]) for r in rows if r["date"] in cv]
        use.sort(key=lambda x: x[0]["date"])
        n_rec, n = len(rows), len(use)
        print(f"    recorded test days {n_rec}; competitor missing on "
              f"{n_rec - n}; n = {n}")
        em = np.array([u[0]["e_model"] for u in use])
        er = np.array([u[0]["e_raw"] for u in use])
        ec = np.array([u[1][0] - u[0]["obs"] for u in use])
        am, ac, ar = (float(np.mean(np.abs(x))) for x in (em, ec, er))
        print(f"    MAE  model {am:.4f}  {cp.upper()} {ac:.4f}  raw GFS "
              f"{ar:.4f}")
        print(f"    mean error (forecast - obs)  model {em.mean():+.4f}  "
              f"{cp.upper()} {ec.mean():+.4f}  raw GFS {er.mean():+.4f}")
        d_pt = ac - am
        s_pt = 100.0 * (1.0 - am / ac)
        (dl, dh), (sl, sh) = bootstrap(rng, np.abs(em), np.abs(ec))
        above = dl > 0
        print(f"    d     = MAE({cp.upper()}) - MAE(model) = {d_pt:+.4f} degC"
              f"   95% [{dl:+.4f}, {dh:+.4f}]   wholly above zero: "
              f"{'yes' if above else 'no'}")
        print(f"    skill = 1 - model/{cp.upper()} = {s_pt:+.2f}%   95% "
              f"[{sl:+.2f}%, {sh:+.2f}%]")
        table.append((name, cp, n, am, ac, ar, d_pt, dl, dh, s_pt, sl, sh,
                      above))
        if cp == "nbm":
            band_in[(st, lk)] = (am, ac)
            by = {}
            for u in use:
                sg = segment(u[1][1])
                by.setdefault(sg, []).append((abs(u[0]["e_model"]),
                                              abs(u[1][0] - u[0]["obs"]),
                                              u[0]["date"]))
            print("    NBM version segments (by NBM cycle; D77.7; "
                  "descriptive only):")
            for sg, _ in NBM_SEGMENTS:
                if sg not in by:
                    continue
                v = by[sg]
                mm = float(np.mean([x[0] for x in v]))
                mc = float(np.mean([x[1] for x in v]))
                print(f"      {sg:<8} n={len(v):<4} ({v[0][2]}..{v[-1][2]})  "
                      f"MAE model {mm:.4f}  NBM {mc:.4f}")
                segs.append((look_name(st, lk), sg, len(v), v[0][2],
                             v[-1][2], mm, mc))

    print("\n" + "=" * 78)
    print("Summary table")
    print("=" * 78)
    print(f"  {'airport-look vs competitor':<30} {'n':>4} {'MAE mod':>8} "
          f"{'MAE comp':>9} {'MAE raw':>8}  {'d degC [95%]':<26} "
          f"{'skill % [95%]':<24} d>0")
    for (nm, cp, n, am, ac, ar, d, dl, dh, s, sl, sh, ab) in table:
        print(f"  {nm:<30} {n:>4} {am:>8.4f} {ac:>9.4f} {ar:>8.4f}  "
              f"{d:+.3f} [{dl:+.3f}, {dh:+.3f}]{'':<5} "
              f"{s:+.1f} [{sl:+.1f}, {sh:+.1f}]{'':<6} "
              f"{'yes' if ab else 'no'}")
    print("\n  NBM version segments")
    for (nm, sg, n, a, b, mm, mc) in segs:
        print(f"    {nm:<16} {sg:<8} n={n:<4} {a}..{b}  model {mm:.4f}  "
              f"NBM {mc:.4f}")

    print("\n" + "=" * 78)
    print("Outcome band (D77.4): NBM only, point estimates, four airport-looks")
    print("=" * 78)
    if len(band_in) != 4:
        print(f"  only {len(band_in)} of 4 airport-looks compared: the band "
              f"cannot be applied as written; reported, not decided")
        return
    wins = 0
    for (st, lk), (am, ac) in band_in.items():
        w = am < ac
        wins += w
        print(f"    {look_name(st, lk):<16} model {am:.4f} vs NBM {ac:.4f}: "
              f"{'model lower' if w else 'NBM lower or equal'}")
    band = "win" if wins == 4 else ("lose" if wins == 0 else "mixed")
    print(f"  BAND: {band} (model lower at {wins} of 4)")
    print("\nEND. Nothing was written. Descriptive only; no verdict changes "
          "(D77.3).")


if __name__ == "__main__":
    if MODE == "--gate":
        print("Session 85, --gate (offline; writes nothing)")
        print(f"run at {datetime.now():%Y-%m-%d %H:%M:%S} local")
        print(f"python {sys.version.split()[0]}, numpy {np.__version__}, "
              f"lightgbm {lgb.__version__}")
        run_gate()
        print("\nEND. Nothing was written.")
    elif MODE == "--pull":
        run_pull()
    else:
        run_compare()
