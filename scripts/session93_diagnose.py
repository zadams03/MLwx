"""Session 93: diagnosis of the 2022-11 pull failure (DECISIONS D85). Read only.

Modes (exactly one):
  --release    Step 2. One or more unauthenticated GitHub REST API reads of the
               Release `stagec-grib-pull-v1`: asset names, sizes and states
               against the plan's 65 months. No asset is downloaded.
  --diagnose   Steps 3 to 5. For the five GFS cycles 2022-11-29T18 to
               2022-11-30T18 and forecast hours f000 to f024, on
               noaa-gfs-bdp-pds: each .idx, a HEAD of each GRIB file, and one
               GET of every message session 91 would request. Then the broken
               files in more detail (Step 4), and the same files on the Google
               Cloud mirror (Step 5).

Byte ranges, selectors, the .idx parsing and the body and message checks are
session 91's: imported from scripts/session91_grib_pull.py (not edited), except
the per-message decode checks, which sit inline in its process_file and are
copied below with their line numbers. Each message is fetched once: no retry
loop. Downloaded bytes live in memory only; nothing is written to disk. No
forecast value is printed; values are decoded only where session 91's own
checks decode them (the finiteness check at the grid indices).
"""

import argparse
import datetime as dt
import hashlib
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))

import eccodes as ec  # noqa: E402
import numpy as np  # noqa: E402
import requests  # noqa: E402

import session91_grib_pull as s91  # noqa: E402

S3 = s91.BUCKET
GCS = "https://storage.googleapis.com/global-forecast-system"
API = "https://api.github.com"
REPO, TAG = "zadams03/MLwx", "stagec-grib-pull-v1"
CYCLES = [dt.datetime(2022, 11, 29, 18), dt.datetime(2022, 11, 30, 0), dt.datetime(2022, 11, 30, 6),
          dt.datetime(2022, 11, 30, 12), dt.datetime(2022, 11, 30, 18)]
HOURS = range(0, 25)
WINDOW = 4096

_lock = threading.Lock()
_ec_lock = threading.Lock()
TALLY = {}   # host -> [requests, bytes]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def request(method, url, byte_range=None, headers=None):
    """One request, never retried. Returns (response or None, error text or None)."""
    h = dict(headers or {})
    h["User-Agent"] = "MLwx/session93"
    if byte_range:
        h["Range"] = f"bytes={byte_range}"
    host = urlparse(url).netloc
    try:
        r = requests.request(method, url, headers=h, timeout=(20, 180))
    except requests.RequestException as e:
        with _lock:
            TALLY.setdefault(host, [0, 0])[0] += 1
        return None, f"network error {e!r}"
    with _lock:
        t = TALLY.setdefault(host, [0, 0])
        t[0] += 1
        t[1] += len(r.content) if method == "GET" else 0
    return r, None


def file_url(base, cycle, fh):
    return s91.file_url(cycle, fh).replace(s91.BUCKET, base)


# ------------------------------------------------------------------ Step 2

def run_release():
    print(f"SESSION 93 --release (unauthenticated GitHub REST API; {now_utc()})")
    r, err = request("GET", f"{API}/repos/{REPO}/releases/tags/{TAG}", headers={"Accept": "application/vnd.github+json"})
    if err or r.status_code != 200:
        print(f"STOP: release read failed: {err or r.status_code}")
        return 1
    rel = r.json()
    print(f"release id {rel['id']}; tag {rel['tag_name']}; name {rel['name']!r}; draft {rel['draft']}; "
          f"prerelease {rel['prerelease']}; published {rel['published_at']}; assets in this response "
          f"{len(rel['assets'])}")
    assets, page = [], 1
    while True:
        r, err = request("GET", f"{API}/repos/{REPO}/releases/{rel['id']}/assets?per_page=100&page={page}",
                         headers={"Accept": "application/vnd.github+json"})
        if err or r.status_code != 200:
            print(f"STOP: asset list page {page} failed: {err or r.status_code}")
            return 1
        got = r.json()
        if not got:
            break
        assets += got
        page += 1
    print(f"asset pages read: {page - 1} (100 per page); assets listed: {len(assets)}")
    months = [f"{y}-{m:02d}" for y, m in s91.all_months()]
    names = {a["name"]: a for a in assets}
    kinds = [("gfs_points_{}.csv.gz", "points"), ("manifest_{}.csv.gz", "manifest"), ("chunk_{}.meta.txt", "meta")]
    expected = {k.format(mo) for mo in months for k, _ in kinds}
    print(f"\nplan months: {len(months)} ({months[0]} to {months[-1]}); expected assets {len(expected)}")
    print("\nper month (y = present):")
    missing_months, partial = [], []
    for mo in months:
        have = [k.format(mo) in names for k, _ in kinds]
        print(f"  {mo}  points {'y' if have[0] else '-'}  manifest {'y' if have[1] else '-'}  "
              f"meta {'y' if have[2] else '-'}")
        if not any(have):
            missing_months.append(mo)
        elif not all(have):
            partial.append(mo)
    extra = sorted(set(names) - expected)
    not_up = [(a["name"], a["state"]) for a in assets if a["state"] != "uploaded"]
    print(f"\nasset count: {len(assets)} (expected 192 = 64 months x 3 if only 2022-11 is missing)")
    print(f"months with no file: {len(missing_months)} {missing_months}")
    print(f"months with some but not all three files: {len(partial)} {partial}")
    print(f"assets not named for a plan month: {len(extra)} {extra}")
    print(f"assets whose state is not 'uploaded': {len(not_up)} {not_up}")
    print("\nassets (name, size in bytes, state, digest, created, updated):")
    for a in sorted(assets, key=lambda a: a["name"]):
        print(f"  {a['name']:30s} {a['size']:>12,d} {a['state']:9s} {a.get('digest')} {a['created_at']} "
              f"{a['updated_at']}")
    tot = {}
    for a in assets:
        for k, kind in kinds:
            if a["name"].startswith(k.split("{}")[0]):
                tot[kind] = tot.get(kind, 0) + a["size"]
    print(f"\ntotal size by kind: {tot}; all {sum(tot.values()):,} bytes")
    print(f"requests: {TALLY}")
    return 0


# ------------------------------------------------------------------ Step 3

def body_kind(body, exp):
    """Session 91's body checks (Fetcher.get, l.347-352), all three reported."""
    bad = []
    if exp is not None and len(body) != exp:
        bad.append(f"short body {len(body)} of {exp} bytes")
    if body[:4] != b"GRIB":
        bad.append("no GRIB at the start")
    if body[-4:] != b"7777":
        bad.append("no 7777 at the end")
    return bad


def decode_checks(data, cycle, fh, ident, kind, positions, geom):
    """Session 91's message checks, copied from session91_grib_pull.py
    process_file l.656-690. Returns '' if all pass, else the reason. No value is
    returned or printed: the values at the grid indices are only tested for
    being present and finite, as there."""
    valid = cycle + dt.timedelta(hours=fh)
    stype, s0, s1 = s91.expected_steps(kind, fh)
    with _ec_lock:
        gid = ec.codes_new_from_message(data)
        try:
            got = (tuple(ec.codes_get_long(gid, k) for k in ("discipline", "parameterCategory", "parameterNumber",
                                                              "typeOfFirstFixedSurface", "level"))
                   + (ec.codes_get_string(gid, "stepType"), ec.codes_get_long(gid, "startStep"),
                      ec.codes_get_long(gid, "endStep")))
            vd, vt = ec.codes_get_long(gid, "validityDate"), ec.codes_get_long(gid, "validityTime")
            if got != ident + (stype, s0, s1):
                raise ValueError(f"identity {got} != expected {ident + (stype, s0, s1)}")
            if (ec.codes_get_long(gid, "dataDate") != int(f"{cycle:%Y%m%d}")
                    or ec.codes_get_long(gid, "dataTime") != cycle.hour * 100):
                raise ValueError("run date or time mismatch")
            if vd != int(f"{valid:%Y%m%d}") or vt != valid.hour * 100:
                raise ValueError(f"validity {vd} {vt:04d} != expected {valid:%Y%m%d %H%M}")
            s91.check_valid(dt.datetime(vd // 10000, (vd // 100) % 100, vd % 100, vt // 100, vt % 100))
            g = s91.msg_geometry(gid)
            if g != geom or ec.codes_get_string(gid, "gridType") != "regular_ll":
                raise ValueError(f"grid geometry {g} differs from the positions file")
            values = ec.codes_get_values(gid)
            missing = ec.codes_get_double(gid, "missingValue")
            bitmap = ec.codes_get_long(gid, "bitmapPresent")
            for p in positions:
                for i in p["indices"]:
                    v = float(values[i])
                    if not np.isfinite(v) or (bitmap and v == missing):
                        raise ValueError(f"missing or non-finite value at grid index {i} ({p['icao']})")
            return ""
        except s91.GuardError:
            raise
        except Exception as e:  # noqa: BLE001
            return repr(e)
        finally:
            ec.codes_release(gid)


def head_marker(body):
    """Edition and total length from the first 16 bytes, if they start with GRIB."""
    if body[:4] != b"GRIB" or len(body) < 16:
        return None
    ed = body[7]
    total = int.from_bytes(body[8:16], "big") if ed == 2 else int.from_bytes(body[4:7], "big")
    return ed, total


def all_offsets(body, marker):
    out, i = [], body.find(marker)
    while i != -1:
        out.append(i)
        i = body.find(marker, i + 1)
    return out


def fetch_message(base, cycle, fh, field, rng, exp, positions, geom):
    """One GET, session 91's checks. Returns a result dict (no body kept)."""
    name, var, level, kind, ident = field
    r, err = request("GET", file_url(base, cycle, fh), rng)
    res = {"range": rng, "exp": exp}
    if err:
        res.update(cls="error", how=err)
        return res
    if r.status_code != 206:
        res.update(cls="error", how=f"HTTP {r.status_code}", got=len(r.content))
        return res
    body = r.content
    res["got"] = len(body)
    res["sha"] = hashlib.sha256(body).hexdigest()
    bad = body_kind(body, exp)
    if bad:
        res.update(cls="broken", how="; ".join(bad), first16=body[:16].hex(), last16=body[-16:].hex(),
                   head=head_marker(body), grib_at=all_offsets(body, b"GRIB"))
        return res
    why = decode_checks(body, cycle, fh, ident, kind, positions, geom)
    res.update(cls="ok" if not why else "check failed", how=why)
    return res


def survey_file(base, cycle, fh, positions, geom):
    """The .idx, a HEAD, and every message session 91 would request, for one file."""
    s91.check_request(cycle, fh)
    url = file_url(base, cycle, fh)
    out = {"cycle": cycle, "fh": fh, "msgs": {}}
    r, err = request("GET", url + ".idx")
    if err or r.status_code != 200:
        out["idx"] = None
        out["idx_err"] = err or f"HTTP {r.status_code}"
    else:
        out["idx"] = r.content
        try:
            out["rows"] = s91.parse_idx(r.content.decode("ascii"))
        except (ValueError, IndexError, UnicodeDecodeError) as e:
            out["rows"] = None
            out["idx_err"] = f"unreadable idx: {e!r}"
    h, err = request("HEAD", url)
    out["cl"] = int(h.headers["Content-Length"]) if (h is not None and h.status_code == 200) else None
    out["head_err"] = None if out["cl"] is not None else (err or f"HTTP {h.status_code}")
    rows = out.get("rows")
    for field in s91.FIELDS:
        name, var, level, kind, _ = field
        step = s91.selector(kind, fh)
        if step is None:
            out["msgs"][name] = {"cls": "absent by design"}
            continue
        if rows is None:
            out["msgs"][name] = {"cls": "idx missing" if out.get("idx") is None else "check failed (idx)",
                                 "how": out.get("idx_err")}
            continue
        try:
            rng, exp, line = s91.find_range(rows, var, level, step, cycle)
        except ValueError as e:
            out["msgs"][name] = {"cls": "check failed (idx)", "how": str(e)}
            continue
        start = int(rng.split("-")[0])
        end = start + exp - 1 if exp is not None else (out["cl"] - 1 if out["cl"] else None)
        beyond = out["cl"] is not None and end is not None and end > out["cl"] - 1
        res = fetch_message(base, cycle, fh, field, rng, exp, positions, geom)
        res.update(start=start, end=end, beyond=beyond, line=line)
        out["msgs"][name] = res
    return out


def survey(base, label, positions, geom, workers=8):
    units = [(c, fh) for c in CYCLES for fh in HOURS]
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {u: ex.submit(survey_file, base, u[0], u[1], positions, geom) for u in units}
        res = {u: f.result() for u, f in futs.items()}
    print(f"{label}: {len(units)} files surveyed in {time.time() - t0:,.0f} s")
    return res


def iso(t):
    return s91.iso(t)


def run_diagnose():
    print(f"SESSION 93 --diagnose ({now_utc()})")
    print(f"cycles: {', '.join(iso(c) for c in CYCLES)}; hours f000 to f024; S3 {S3}; mirror {GCS}")
    positions, geom = s91.read_positions()
    print(f"positions file SHA-256 {s91.sha256_file(s91.POSITIONS)}; airports {len(positions)}")

    # ---------------- Step 3
    print("\n================ STEP 3: which messages are broken (S3)")
    res = survey(S3, "S3", positions, geom)
    classes = ["ok", "broken", "check failed", "check failed (idx)", "error", "absent by design", "idx missing"]
    print("\n3.1 .idx and HEAD, per file (idx lines, idx bytes, Content-Length):")
    for c in CYCLES:
        for fh in HOURS:
            f = res[(c, fh)]
            nl = len(f["rows"]) if f.get("rows") else None
            print(f"  {iso(c)} f{fh:03d}  idx {'MISSING ' + f['idx_err'] if f.get('idx') is None else 'ok'}"
                  f"  lines {nl}  idx bytes {len(f['idx']) if f.get('idx') else '-'}"
                  f"  Content-Length {f['cl'] if f['cl'] is not None else 'MISSING ' + str(f['head_err'])}")
    print("\n3.2 ranges whose end is beyond the file's Content-Length:")
    n_beyond = 0
    for (c, fh), f in res.items():
        for name, m in f["msgs"].items():
            if m.get("beyond"):
                n_beyond += 1
                print(f"  {iso(c)} f{fh:03d} {name} {m['range']} end {m['end']} >= Content-Length {f['cl']}")
    print(f"  total: {n_beyond}")
    print("\n3.5 per cycle and hour (" + " / ".join(classes) + "):")
    tot = {k: 0 for k in classes}
    for c in CYCLES:
        ctot = {k: 0 for k in classes}
        for fh in HOURS:
            cnt = {k: 0 for k in classes}
            for m in res[(c, fh)]["msgs"].values():
                cnt[m["cls"]] += 1
            for k in classes:
                ctot[k] += cnt[k]
            print(f"  {iso(c)} f{fh:03d}  " + "  ".join(f"{cnt[k]}" for k in classes))
        print(f"  {iso(c)} total " + "  ".join(f"{k} {ctot[k]}" for k in classes))
        for k in classes:
            tot[k] += ctot[k]
    print("  ALL CYCLES: " + "; ".join(f"{k} {tot[k]}" for k in classes))
    broken = [((c, fh), name, m) for (c, fh), f in sorted(res.items()) for name, m in f["msgs"].items()
              if m["cls"] in ("broken", "error", "check failed", "check failed (idx)")]
    print(f"\n3.5 every message that is not ok and not absent by design ({len(broken)}):")
    for (c, fh), name, m in broken:
        print(f"  {iso(c)} f{fh:03d} {name:6s} range {m.get('range')} expected {m.get('exp')} received "
              f"{m.get('got')}: {m['cls']}: {m.get('how')}")
    print("\n3.4 each broken message: first and last 16 bytes (hex); edition and total length from the first 16 "
          "bytes if they start with GRIB; offsets of 'GRIB' inside the body:")
    for (c, fh), name, m in broken:
        if m["cls"] != "broken":
            continue
        print(f"  {iso(c)} f{fh:03d} {name} {m['range']}")
        print(f"    first16 {m['first16']}")
        print(f"    last16  {m['last16']}")
        print(f"    header  {('edition %d, total length %d' % m['head']) if m['head'] else 'does not start with GRIB'}")
        print(f"    'GRIB' in body at offsets {m['grib_at'] if m['grib_at'] else 'none'}")
    nb = sum(1 for *_, m in broken if m["cls"] == "broken")
    print(f"\nbroken messages: {nb}; at 5 retries each, {nb * 5} retries (D85.3 reports 85 retries in each run)")
    known = {(dt.datetime(2022, 11, 29, 18), 3): "417821939-418699246", (dt.datetime(2022, 11, 29, 18), 2): "419336616-420214434"}
    for (c, fh), rng in known.items():
        hit = [name for name, m in res[(c, fh)]["msgs"].items() if m.get("range") == rng]
        print(f"D85.3 range {iso(c)} f{fh:03d} {rng}: field {hit or 'not among the requested ranges'}; "
              f"class {[res[(c, fh)]['msgs'][h]['cls'] for h in hit]}")
    print("\n3.x every requested message (cycle, hour, field, range, bytes received, class, sha256):")
    for (c, fh), f in sorted(res.items()):
        for name, m in f["msgs"].items():
            if "range" in m:
                print(f"  {iso(c)} f{fh:03d} {name:6s} {m['range']:>21s} {str(m.get('got')):>8s} {m['cls']:12s} "
                      f"{m.get('sha', '')}")

    # ---------------- Step 4
    print("\n================ STEP 4: the broken files in more detail")
    bfiles = sorted({u for u, name, m in broken if m["cls"] == "broken"})
    print(f"broken files: {[(iso(c), fh) for c, fh in bfiles]}")
    for c, fh in bfiles:
        f = res[(c, fh)]
        rows, cl = f["rows"], f["cl"]
        print(f"\n--- {iso(c)} f{fh:03d} (Content-Length {cl})")
        counts = {h: (len(res[(c, h)]["rows"]) if res[(c, h)].get("rows") else None) for h in HOURS}
        print(f"4.1 idx line counts, this cycle, f000 to f024: {counts}")
        print(f"    this file {counts[fh]}; other hours f001 to f024 (f000 is the analysis): "
              f"{sorted(set(v for h, v in counts.items() if h not in (0, fh)))}")
        offs = [r["offset"] for r in rows]
        inc = all(b > a for a, b in zip(offs, offs[1:]))
        print(f"4.2 idx offsets: first {offs[0]}; last {offs[-1]}; strictly increasing {inc}; "
              f"last offset below Content-Length {offs[-1] < cl}; last message's implied length {cl - offs[-1]}")
        healthy = [h for h in HOURS if h not in (0, fh) and (c, h) not in bfiles and res[(c, h)].get("rows")]
        compare = [("this file", c, fh)] + ([("healthy file", c, healthy[0])] if healthy else [])
        for label, cc, hh in compare:
            ff = res[(cc, hh)]
            r, err = request("GET", file_url(S3, cc, hh), f"{ff['cl'] - 4}-{ff['cl'] - 1}")
            tail = r.content if (r is not None and r.status_code == 206) else None
            r2, err2 = request("GET", file_url(S3, cc, hh), f"{ff['rows'][-1]['offset']}-{ff['rows'][-1]['offset'] + 3}")
            last_head = r2.content if (r2 is not None and r2.status_code == 206) else None
            print(f"    {label} f{hh:03d}: last 4 bytes of the file {tail!r} ({err or r.status_code}); "
                  f"4 bytes at the last idx offset {last_head!r} ({err2 or r2.status_code})")
        first_bad = next(name for name, m in f["msgs"].items() if m["cls"] == "broken")
        m = f["msgs"][first_bad]
        lo = max(0, m["start"] - WINDOW // 2)
        hi = lo + WINDOW - 1
        r, err = request("GET", file_url(S3, c, fh), f"{lo}-{hi}")
        if r is None or r.status_code != 206:
            print(f"4.3 window for {first_bad}: request failed: {err or r.status_code}")
            continue
        w = r.content
        g = [lo + i - m["start"] for i in all_offsets(w, b"GRIB")]
        s = [lo + i - m["start"] for i in all_offsets(w, b"7777")]
        print(f"4.3 window around {first_bad}'s start (idx offset {m['start']}): bytes {lo}-{hi} "
              f"({len(w)} received); offsets relative to the idx offset: 'GRIB' at {g}; '7777' at {s} "
              f"(a '7777' at -4 and a 'GRIB' at 0 is what a healthy boundary looks like)")
        prev = [r_ for r_ in rows if r_["offset"] < m["start"]]
        if prev:
            print(f"    previous idx line: {prev[-1]['line']}")
        print(f"    this idx line:     {m['line']}")

    # ---------------- Step 5
    print("\n================ STEP 5: the Google Cloud mirror")
    if not bfiles:
        print("no broken file on S3, nothing to check")
        return 0
    c0, h0 = bfiles[0]
    r, err = request("GET", file_url(GCS, c0, h0) + ".idx")
    if err or r.status_code != 200:
        print(f"mirror path {file_url(GCS, c0, h0)}.idx: {err or 'HTTP ' + str(r.status_code)}. Step stopped.")
        return 0
    print(f"mirror reachable: {file_url(GCS, c0, h0)}.idx HTTP 200")
    ok_by_cycle = {}
    for (c, fh), f in sorted(res.items()):
        for name, m in f["msgs"].items():
            if m["cls"] == "ok":
                ok_by_cycle.setdefault(c, []).append((fh, name, m))
    for c, fh in bfiles:
        f = res[(c, fh)]
        r, err = request("GET", file_url(GCS, c, fh) + ".idx")
        if err or r.status_code != 200:
            print(f"\n--- {iso(c)} f{fh:03d}: mirror .idx {err or 'HTTP ' + str(r.status_code)}")
            continue
        g_idx = r.content
        g_rows = s91.parse_idx(g_idx.decode("ascii"))
        h, err = request("HEAD", file_url(GCS, c, fh))
        g_cl = int(h.headers["Content-Length"]) if (h is not None and h.status_code == 200) else None
        print(f"\n--- {iso(c)} f{fh:03d}")
        print(f"5.1 mirror .idx byte-identical to S3's: {g_idx == f['idx']} (S3 {len(f['idx'])} B, "
              f"{len(f['rows'])} lines; mirror {len(g_idx)} B, {len(g_rows)} lines; sha256 S3 "
              f"{hashlib.sha256(f['idx']).hexdigest()}, mirror {hashlib.sha256(g_idx).hexdigest()})")
        print(f"    Content-Length: S3 {f['cl']}; mirror {g_cl if g_cl is not None else err or h.status_code}; "
              f"equal {g_cl == f['cl']}")
        print("5.2 messages broken on S3, fetched once from the mirror with the mirror's own .idx ranges:")
        for field in s91.FIELDS:
            name = field[0]
            if f["msgs"][name]["cls"] != "broken":
                continue
            try:
                rng, exp, _ = s91.find_range(g_rows, field[1], field[2], s91.selector(field[3], fh), c)
            except ValueError as e:
                print(f"    {name}: mirror idx check failed: {e}")
                continue
            m = fetch_message(GCS, c, fh, field, rng, exp, positions, geom)
            print(f"    {name:6s} S3 {f['msgs'][name]['range']}  mirror {rng} ({exp} B): {m['cls']}"
                  f"{': ' + m['how'] if m.get('how') else ''}; mirror sha256 {m.get('sha')}")
        print("5.3 three messages ok on S3 in this cycle, same byte ranges on the mirror, SHA-256 compared:")
        own = [x for x in ok_by_cycle.get(c, []) if x[0] == fh]
        rest = [x for x in ok_by_cycle.get(c, []) if x[0] != fh]
        for hh, name, m in (own + rest)[:3]:
            r, err = request("GET", file_url(GCS, c, hh), m["range"])
            if err or r.status_code != 206:
                print(f"    f{hh:03d} {name} {m['range']}: mirror {err or 'HTTP ' + str(r.status_code)}")
                continue
            gs = hashlib.sha256(r.content).hexdigest()
            print(f"    f{hh:03d} {name:6s} {m['range']}: S3 {m['sha']}  mirror {gs}  identical {gs == m['sha']}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--release", action="store_true")
    g.add_argument("--diagnose", action="store_true")
    a = ap.parse_args()
    print(f"python {sys.version.split()[0]}; numpy {np.__version__}; requests {requests.__version__}; "
          f"eccodes {ec.__version__} (library {ec.codes_get_api_version()}); session91 script sha256 "
          f"{s91.sha256_file(Path(s91.__file__))}")
    t0 = time.time()
    try:
        rc = run_release() if a.release else run_diagnose()
    finally:
        print(f"\nrequests and bytes per host: " + "; ".join(f"{h}: {n} requests, {b:,} bytes"
                                                          for h, (n, b) in sorted(TALLY.items())))
        print(f"seconds {time.time() - t0:,.0f}; finished {now_utc()}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
