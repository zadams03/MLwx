"""Session 104: download and check the f025 to f048 GRIB pull (DECISIONS D98.3).

The Release `stagec-grib-pull-f025-048` of zadams03/MLwx holds three files per
month (points, manifest, meta) for 2021-03 to 2026-07. This script lists the
Release, downloads the files not yet held into MLwx-pull-f025-048/ (outside
the repo, D95.6), and checks them, as session 95 did for the f000 to f024 pull
(D87, F137). It is modelled on scripts/session95_check_release.py, which is
not imported or edited. The plan, fields, statuses and column layout come from
scripts/session91_grib_pull.py (imported). The D84.4 checks and --ranges are
run by calling scripts/session92_verify_chunk.py as a subprocess, with
--hours 25-48; from it only read_gz_csv and BOUNDS are imported.

D98.2: no value is found by searching DECISIONS text. Every recorded value this
script needs is a constant below, with a comment naming its entry; a test in
tests/ checks the constant against the entry.

Modes (exactly one):
  --release    Network (GitHub REST API, unauthenticated, read only). The
               Release's assets against the plan: 195 files, three a month.
  --download   Network (the API, then each asset's download link). Checks
               every file already held against its Release size and SHA-256
               (any mismatch or non-asset: stop), then downloads every asset
               not held, to a temporary name, checks size and SHA-256, then
               links it to its asset name. At most 3 retries (waits 10, 30,
               90 s) on a network error, HTTP 5xx or a digest mismatch; any
               other HTTP status stops at once. Never overwrites or deletes a
               held file.
  --months     Offline. Every month's meta, then the verifier, then the
               verifier with --ranges. One line per month.
  --totals     Offline. The union of all months against the full 25-48 plan;
               no key in two months; status totals.
  --negative   Offline. (a) a copied file with one byte changed fails the
               digest check; (b) the totals check with one month's manifest
               left out fails. Copies only, in one temporary directory,
               deleted at the end.
  --inventory  Network (one Release listing). Writes
               data/processed/session104_pull_f025_048_inventory.csv and its
               .meta.txt. Refuses if either exists.

Hard limits: the only hosts are api.github.com and the Release's download
links (and the host GitHub redirects them to). No GRIB request. No forecast
value is printed except per-field minimum and maximum (--months' ranges).
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np  # noqa: E402
import requests  # noqa: E402

import session91_grib_pull as p91  # noqa: E402
from session92_verify_chunk import BOUNDS, read_gz_csv  # noqa: E402

ROOT = p91.ROOT
PULL_DIR = ROOT.parent / "MLwx-pull-f025-048"
VERIFIER = ROOT / "scripts" / "session92_verify_chunk.py"
INVENTORY = ROOT / "data" / "processed" / "session104_pull_f025_048_inventory.csv"
INVENTORY_META = ROOT / "data" / "processed" / "session104_pull_f025_048_inventory.csv.meta.txt"

REPO = "zadams03/MLwx"
TAG = "stagec-grib-pull-f025-048"     # D95.6
API = "https://api.github.com"
HOURS = (25, 48)
HOURS_ARG = "25-48"
PART = ".session104-part"   # suffix of a download's temporary name
DL_WAITS = (10, 30, 90)     # as session 95's (F137.3): at most 3 retries, these waits (s)

# Recorded values (D98.2), each with its entry.
PULL_SCRIPT_SHA256 = "557e88326aa410b150502619e2c5dd28ab22e89c19a46eb797b90bfe117b1675"   # F145
PLAN_KEYS_F145 = 187_768    # F145.1: (cycle, hour) keys of the 25-48 plan


class Stop(Exception):
    """A check failed in a way the prompt says to stop on."""


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def months():
    return [f"{y}-{m:02d}" for y, m in p91.all_months()]


def asset_names(m):
    return [f"chunk_{m}.meta.txt", f"gfs_points_{m}.csv.gz", f"manifest_{m}.csv.gz"]


def check_digest(path, size, sha):
    """True when the file's size and SHA-256 equal the Release's."""
    return path.stat().st_size == size and p91.sha256_file(path) == sha


# ------------------------------------------------------------------ GitHub REST API (unauthenticated)

class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "MLwx/session104", "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28"})
        self.requests = 0
        self.bytes = 0

    def get(self, url, params=None):
        r = self.s.get(url, params=params, timeout=(20, 120))
        self.requests += 1
        self.bytes += len(r.content)
        if r.status_code != 200:
            raise Stop(f"GitHub API {url} answered HTTP {r.status_code}: {r.text[:200]}")
        return r.json()

    def release(self):
        """The Release and every asset (paged, 100 a page)."""
        rel = self.get(f"{API}/repos/{REPO}/releases/tags/{TAG}")
        assets, page = [], 1
        while True:
            got = self.get(f"{API}/repos/{REPO}/releases/{rel['id']}/assets", {"per_page": 100, "page": page})
            assets += got
            if len(got) < 100:
                break
            page += 1
        return rel, assets


def check_release(rel, assets, quiet=False):
    """The Release against the plan. Returns {name: asset}. Raises Stop on any difference."""
    say = (lambda *a: None) if quiet else print
    say(f"Release: {REPO}, tag {rel['tag_name']}, title {rel['name']!r}, draft {rel['draft']}, "
        f"prerelease {rel['prerelease']}, published {rel['published_at']}; assets {len(assets)} (expected 195)")
    problems = []
    by_name = {}
    for a in assets:
        if a["name"] in by_name:
            problems.append(f"asset name twice: {a['name']}")
        by_name[a["name"]] = a
    want = {n for m in months() for n in asset_names(m)}
    if len(assets) != 195:
        problems.append(f"{len(assets)} assets, not 195")
    missing = sorted(want - set(by_name))
    extra = sorted(set(by_name) - want)
    if missing:
        problems.append(f"missing assets: {missing}")
    if extra:
        problems.append(f"assets not in the plan: {extra}")
    per_month = {m: sum(1 for n in asset_names(m) if n in by_name) for m in months()}
    bad_months = {m: k for m, k in per_month.items() if k != 3}
    if bad_months:
        problems.append(f"months without exactly three files: {bad_months}")
    not_up = sorted(a["name"] for a in assets if a.get("state") != "uploaded")
    no_dig = sorted(a["name"] for a in assets if not str(a.get("digest") or "").startswith("sha256:"))
    if not_up:
        problems.append(f"state not 'uploaded': {not_up}")
    if no_dig:
        problems.append(f"no sha256 digest: {no_dig}")
    if rel["draft"] or rel["prerelease"]:
        problems.append("the Release is a draft or a prerelease")
    say(f"plan months {months()[0]} to {months()[-1]}: {len(per_month)}; with exactly 3 files: "
        f"{sum(1 for k in per_month.values() if k == 3)}; missing {len(missing)}; not in plan {len(extra)}; "
        f"state not uploaded {len(not_up)}; without digest {len(no_dig)}")
    if problems:
        for p in problems:
            say(f"  PROBLEM: {p}")
        raise Stop("the Release differs from the plan: " + "; ".join(problems))
    return by_name


def run_release(args):
    print(f"SESSION 104 --release (GitHub REST API, unauthenticated) at {now_utc()}")
    api = Api()
    rel, assets = api.release()
    by_name = check_release(rel, assets)
    tot = {"points": 0, "manifest": 0, "chunk": 0}
    for n, a in by_name.items():
        tot["points" if n.startswith("gfs_points") else n.split("_", 1)[0]] += a["size"]
    print(f"total bytes {sum(tot.values()):,} (points {tot['points']:,}; manifests {tot['manifest']:,}; "
          f"meta {tot['chunk']:,})")
    up = sorted(a["updated_at"] for a in assets)
    print(f"assets uploaded {up[0]} to {up[-1]}")
    print(f"API requests used: {api.requests} ({api.bytes:,} B)")
    print("RELEASE CHECK: PASS")
    return 0


# ------------------------------------------------------------------ download

def run_download(args):
    print(f"SESSION 104 --download into {PULL_DIR} at {now_utc()}")
    api = Api()
    rel, assets = api.release()
    by_name = check_release(rel, assets, quiet=True)
    print(f"Release listed and checked (195 assets); API requests {api.requests}")
    PULL_DIR.mkdir(exist_ok=True)
    held = sorted(p.name for p in PULL_DIR.iterdir())
    not_asset = [n for n in held if n not in by_name]
    differ = [n for n in held if n in by_name
              and not check_digest(PULL_DIR / n, by_name[n]["size"], by_name[n]["digest"].split(":", 1)[1])]
    print(f"held locally: {len(held)}; not a Release asset {not_asset}; not equal to its size and SHA-256 {differ}")
    if not_asset or differ:
        raise Stop("a file in MLwx-pull-f025-048/ is not a Release asset or differs from its digest")
    todo = [n for n in sorted(by_name) if n not in held]
    print(f"to download: {len(todo)}")
    dl = requests.Session()
    dl.headers.update({"User-Agent": "MLwx/session104", "Accept": "application/octet-stream"})
    t0 = time.time()
    n_bytes, n_req, retries, hosts = 0, 0, 0, set()
    for i, name in enumerate(todo, 1):
        a = by_name[name]
        size, sha = a["size"], a["digest"].split(":", 1)[1]
        target = PULL_DIR / name
        tmp = PULL_DIR / (name + PART)
        if tmp.exists():
            raise Stop(f"temporary name {tmp} already exists")
        last = None
        for attempt in range(len(DL_WAITS) + 1):
            if attempt:
                retries += 1
                print(f"  {name}: try {attempt} failed ({last}); waiting {DL_WAITS[attempt - 1]} s", flush=True)
                time.sleep(DL_WAITS[attempt - 1])
            if target.exists():
                raise Stop(f"{target} exists; not writing over it")
            try:
                h = hashlib.sha256()
                got = 0
                with dl.get(a["browser_download_url"], stream=True, timeout=(20, 300)) as r:
                    n_req += 1
                    hosts.update(x.url.split("/")[2] for x in r.history)
                    hosts.add(r.url.split("/")[2])
                    if 500 <= r.status_code <= 599:
                        last = f"HTTP {r.status_code}"
                        continue
                    if r.status_code != 200:
                        raise Stop(f"{name}: HTTP {r.status_code} (not retried)")
                    with open(tmp, "xb") as fh:
                        for block in r.iter_content(1 << 20):
                            fh.write(block)
                            h.update(block)
                            got += len(block)
            except requests.RequestException as e:
                last = f"network error {e!r}"
                if tmp.exists():
                    tmp.unlink()
                continue
            n_bytes += got
            if got != size or h.hexdigest() != sha or not check_digest(tmp, size, sha):
                last = f"size {got} (Release {size}) or SHA-256 {h.hexdigest()} (Release {sha}) differs"
                tmp.unlink()
                continue
            os.link(tmp, target)     # fails if the target exists: never overwrites
            tmp.unlink()
            last = None
            break
        if last is not None:
            raise Stop(f"{name} failed after {len(DL_WAITS)} retries: {last}")
        if i % 20 == 0 or i == len(todo):
            print(f"  {i}/{len(todo)} downloaded; {n_bytes:,} B; {time.time() - t0:,.0f} s; retries {retries}",
                  flush=True)
    print(f"\ndownloaded {len(todo)} files, {n_bytes:,} B, {time.time() - t0:,.1f} s, {n_req} download requests, "
          f"retries {retries}; hosts reached {sorted(hosts)}")
    print(f"API requests {api.requests} ({api.bytes:,} B)")
    files = sorted(p.name for p in PULL_DIR.iterdir())
    bad = [n for n in sorted(by_name) if not (PULL_DIR / n).exists()
           or not check_digest(PULL_DIR / n, by_name[n]["size"], by_name[n]["digest"].split(":", 1)[1])]
    extra = sorted(set(files) - set(by_name))
    ok = len(files) == 195 and not extra and not bad
    print(f"MLwx-pull-f025-048/: {len(files)} files; not a Release asset {extra}; missing or not equal {bad}")
    print("DOWNLOAD: PASS, 195 assets held, each equal to its Release digest" if ok else "DOWNLOAD: FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ meta and the verifier

META_RX = {
    "start": r"^run start \(UTC\)\s+: (\S+)$",
    "seconds": r"^seconds\s+: ([\d.]+)$",
    "arguments": r"^arguments\s+: (.*)$",
    "requests": r"^requests\s+: (.*)$",
    "script": r"^script sha256\s+: ([0-9a-f]{64}) ",
    "positions": r"^positions sha256\s+: ([0-9a-f]{64}) ",
    "packages": r"^packages\s+: (.*)$",
}


def read_meta(m, d=PULL_DIR):
    text = (d / f"chunk_{m}.meta.txt").read_text()
    out = {}
    for k, rx in META_RX.items():
        g = re.search(rx, text, re.M)
        if not g:
            raise Stop(f"{m}: the meta has no '{k}' line")
        out[k] = g.group(1)
    out["data_sha"] = {n: s for n, s in re.findall(r"^(\S+\.csv\.gz) sha256 ([0-9a-f]{64}) ", text, re.M)}
    return out


def run_verifier(m, extra):
    cmd = [sys.executable, str(VERIFIER), "--dir", str(PULL_DIR), "--month", m, "--hours", HOURS_ARG] + extra
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT / "scripts",
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return r.returncode, r.stdout + r.stderr


def run_months(args):
    print(f"SESSION 104 --months (offline) at {now_utc()}; {PULL_DIR}")
    pos_sha = p91.sha256_file(p91.POSITIONS)
    print(f"pull-script SHA-256 expected (F145): {PULL_SCRIPT_SHA256}; committed positions file {pos_sha}")
    print(f"  {'month':7s} {'meta':4s} {'retr':>4s} {'404':>3s} {'verifier':>9s} {'idx miss':>8s} {'whole':>5s} "
          f"{'ranges':>6s} {'outside':>7s} {'readback':>8s} {'cells':>10s}")
    overall = {f: [None, None, 0, 0] for f in p91.FIELD_NAMES}
    tot = {"cells": 0, "outside": 0, "readback": 0, "idx": 0, "whole": 0, "retries": 0, "404": 0}
    extras, scripts, pkgs = set(), set(), set()
    for m in months():
        mt = read_meta(m)
        names = asset_names(m)
        data_ok = all(mt["data_sha"].get(n) == p91.sha256_file(PULL_DIR / n) for n in names[1:])
        args_want = f"--chunk --month {m} --hours {HOURS_ARG}"
        args_ok = mt["arguments"].startswith(args_want + " ") or mt["arguments"] == args_want
        extras.add(mt["arguments"][len(args_want):].strip())
        scripts.add(mt["script"])
        pkgs.add(mt["packages"])
        rq = re.fullmatch(r"idx (\d+), message (\d+)(?:, whole file (\d+))?; retries (\d+); HTTP 404 (\d+)",
                          mt["requests"])
        if not rq:
            raise Stop(f"{m}: the requests line is not in the expected form: {mt['requests']!r}")
        meta_ok = data_ok and args_ok and mt["script"] == PULL_SCRIPT_SHA256 and mt["positions"] == pos_sha
        tot["retries"] += int(rq.group(4))
        tot["404"] += int(rq.group(5))
        if not meta_ok:
            raise Stop(f"{m}: meta not as expected (data SHA-256 {data_ok}, arguments {args_ok}, "
                       f"script {mt['script'] == PULL_SCRIPT_SHA256}, positions {mt['positions'] == pos_sha})")
        code, out = run_verifier(m, [])
        passed = re.search(r"^checks passed (\d+) of (\d+)", out, re.M)
        idx = re.search(r'"idx missing" messages \(published, left empty, not a fail\): (\d+); '
                        r'"ok \(whole file\)" messages \(published, filled from the whole file, not a fail\): (\d+)',
                        out)
        if code != 0 or not passed or passed.group(1) != "13" or passed.group(2) != "13" or not idx:
            print(out)
            raise Stop(f"{m}: the verifier did not pass 13 of 13 (exit {code})")
        code2, out2 = run_verifier(m, ["--ranges"])
        if code2 != 0:
            print(out2)
            raise Stop(f"{m}: the verifier with --ranges exited {code2}")
        outside_m = 0
        for f in p91.FIELD_NAMES:
            g = re.search(rf"^  {f}\s+(\d+)\s+(\S+)\s+(\S+)\s+\S+ to \S+\s+(\d+)$", out2, re.M)
            if not g:
                raise Stop(f"{m}: no ranges line for {f}")
            n, lo, hi, o = int(g.group(1)), float(g.group(2)), float(g.group(3)), int(g.group(4))
            ov = overall[f]
            ov[0] = lo if ov[0] is None else min(ov[0], lo)
            ov[1] = hi if ov[1] is None else max(ov[1], hi)
            ov[2] += n
            ov[3] += o
            outside_m += o
        rb = re.search(r"^read-back: (\d+) value cells; float then repr gives a different string in (\d+)$",
                       out2, re.M)
        cells, rbm = int(rb.group(1)), int(rb.group(2))
        tot["cells"] += cells
        tot["outside"] += outside_m
        tot["readback"] += rbm
        tot["idx"] += int(idx.group(1))
        tot["whole"] += int(idx.group(2))
        print(f"  {m:7s} {'ok':4s} {rq.group(4):>4s} {rq.group(5):>3s} {'13 of 13':>9s} {idx.group(1):>8s} "
              f"{idx.group(2):>5s} {'exit 0':>6s} {outside_m:>7d} {rbm:>8d} {cells:>10,}", flush=True)
        if outside_m or rbm:
            raise Stop(f"{m}: {outside_m} values outside the bounds, {rbm} read-back mismatches")
    print(f"metas: arguments after '--chunk --month <m> --hours 25-48': {sorted(extras)}; pull-script SHA-256 "
          f"values {sorted(scripts)}; packages {sorted(pkgs)}")
    print(f"sums: retries {tot['retries']}; HTTP 404 {tot['404']}; idx missing {tot['idx']}; ok (whole file) "
          f"{tot['whole']}; value cells {tot['cells']:,}; outside bounds {tot['outside']}; read-back mismatches "
          f"{tot['readback']}")
    print("per field over all 65 months (units as GRIB gives them; bounds from session92_verify_chunk.BOUNDS):")
    print(f"  {'field':7s} {'values':>11s} {'minimum':>22s} {'maximum':>22s} {'bounds':>20s} {'outside':>8s}")
    for f in p91.FIELD_NAMES:
        lo, hi, n, o = overall[f]
        blo, bhi = BOUNDS[f]
        print(f"  {f:7s} {n:>11,} {lo!r:>22s} {hi!r:>22s} {f'{blo:g} to {bhi:g}':>20s} {o:>8d}")
    print("MONTHS: PASS (every meta as expected; verifier 13 of 13 and --ranges clean on all 65 months)")
    return 0


# ------------------------------------------------------------------ totals

CYCLE_BASE = dt.datetime(2021, 1, 1)


def cyc_int(s):
    t = dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")
    return int((t - CYCLE_BASE).total_seconds() // 3600)


def enc(c, fh, sub):
    """A key as one integer: cycle (hours since 2021-01-01), forecast hour, then
    the field or airport index."""
    return (c * 49 + fh) * 64 + sub


def full_plan():
    """The full 25-48 plan for every month, from session 91's own functions."""
    positions, _ = p91.read_positions()
    icaos = [p["icao"] for p in positions]
    fidx = {f: i for i, f in enumerate(p91.FIELD_NAMES)}
    cycles, files, man, msgs, pts = set(), [], [], [], []
    for y, mo in p91.all_months():
        for c, fhs in p91.plan_chunk(p91.month_cycles(y, mo), HOURS):
            ci = cyc_int(p91.iso(c))
            cycles.add(ci)
            for fh in fhs:
                files.append(ci * 49 + fh)
                for name, var, level, kind, ident in p91.FIELDS:
                    k = enc(ci, fh, fidx[name])
                    man.append(k)
                    if p91.selector(kind, fh) is not None:
                        msgs.append(k)
                for j in range(len(icaos)):
                    pts.append(enc(ci, fh, j))
    return {"cycles": np.array(sorted(cycles), dtype=np.int64), "files": np.sort(np.array(files, dtype=np.int64)),
            "manifest": np.sort(np.array(man, dtype=np.int64)), "messages": np.sort(np.array(msgs, dtype=np.int64)),
            "points": np.sort(np.array(pts, dtype=np.int64))}, icaos


def compare(label, got, want, out):
    u, counts = np.unique(got, return_counts=True)
    dup = int((counts > 1).sum())
    missing = np.setdiff1d(want, u, assume_unique=True)
    extra = np.setdiff1d(u, want, assume_unique=True)
    ok = len(got) == len(want) and dup == 0 and len(missing) == 0 and len(extra) == 0
    out.append((label, ok))
    print(f"  [{'PASS' if ok else 'FAIL'}] {label:15s} plan {len(want):>10,}; found {len(got):>10,} rows, "
          f"{len(u):>10,} distinct; keys in more than one row {dup}; plan keys missing {len(missing):,}; "
          f"keys not in plan {len(extra):,}")
    return ok


def totals(man_paths, pts_paths, plan, icaos):
    """The union of all months against the plan. Returns (all passed, status totals)."""
    fidx = {f: i for i, f in enumerate(p91.FIELD_NAMES)}
    iidx = {c: i for i, c in enumerate(icaos)}
    cmap = {}

    def ci(s):
        if s not in cmap:
            cmap[s] = cyc_int(s)
        return cmap[s]

    m_cyc, m_file, m_key, m_msg, p_cyc, p_file, p_key = [], [], [], [], [], [], []
    wrong_month, unknown = [], 0
    status_tot = {s: 0 for s in p91.STATUSES}
    for m in months():
        if m in man_paths:
            head, rows = read_gz_csv(man_paths[m])
            if head != p91.MAN_COLS:
                raise Stop(f"{m}: manifest layout")
            for r in rows:
                c, fh, f, st = r[0], int(r[1]), r[2], r[6]
                if c[:7] != m:
                    wrong_month.append(("manifest", m, c, fh, f))
                if f not in fidx or st not in status_tot:
                    unknown += 1
                    continue
                k = enc(ci(c), fh, fidx[f])
                m_key.append(k)
                m_file.append(ci(c) * 49 + fh)
                if st != "absent by design":
                    m_msg.append(k)
                status_tot[st] += 1
            m_cyc += list({ci(r[0]) for r in rows})
        if m in pts_paths:
            with gzip.open(pts_paths[m], "rt", newline="") as fh_:
                rd = csv.reader(fh_)
                if next(rd) != p91.POINT_COLS:
                    raise Stop(f"{m}: points layout")
                cs = set()
                for r in rd:
                    c, fh, ic = r[0], int(r[1]), r[3]
                    if c[:7] != m:
                        wrong_month.append(("points", m, c, fh, ic))
                    if ic not in iidx:
                        unknown += 1
                        continue
                    p_key.append(enc(ci(c), fh, iidx[ic]))
                    cs.add((ci(c), fh))
            p_cyc += list({x[0] for x in cs})
            p_file += [x[0] * 49 + x[1] for x in cs]
    res = []
    a = np.array
    compare("cycles (manif.)", a(m_cyc, dtype=np.int64), plan["cycles"], res)
    compare("cycles (points)", a(p_cyc, dtype=np.int64), plan["cycles"], res)
    compare("files (manif.)", np.unique(a(m_file, dtype=np.int64)), plan["files"], res)
    compare("files (points)", a(p_file, dtype=np.int64), plan["files"], res)
    compare("manifest rows", a(m_key, dtype=np.int64), plan["manifest"], res)
    compare("messages", a(m_msg, dtype=np.int64), plan["messages"], res)
    compare("points rows", a(p_key, dtype=np.int64), plan["points"], res)
    ok_m = not wrong_month and unknown == 0
    res.append(("month of key", ok_m))
    print(f"  [{'PASS' if ok_m else 'FAIL'}] keys whose cycle is in another month: {len(wrong_month)}; "
          f"rows with an unknown field, airport or status: {unknown} (a key holds its cycle, so a key only in "
          f"its own cycle's month cannot be in two months)")
    return all(ok for _, ok in res), status_tot


def run_totals(args):
    print(f"SESSION 104 --totals (offline) at {now_utc()}; {PULL_DIR}")
    t0 = time.time()
    plan, icaos = full_plan()
    first = min(c for y, mo in p91.all_months() for c, _ in p91.plan_chunk(p91.month_cycles(y, mo), HOURS))
    print(f"full plan (session 91: all_months, month_cycles, plan_chunk, FIELDS, selector; hours 25-48; first "
          f"cycle {p91.iso(first)}): {len(plan['cycles']):,} cycles, {len(plan['files']):,} (cycle, hour) keys, "
          f"{len(plan['manifest']):,} manifest rows, {len(plan['messages']):,} messages, "
          f"{len(plan['points']):,} points rows ({len(icaos)} airports)")
    keys_ok = len(plan["files"]) == PLAN_KEYS_F145 and p91.iso(first) == "2021-03-22T12:00Z"
    print(f"(cycle, hour) keys equal F145.1's {PLAN_KEYS_F145:,} and first cycle 2021-03-22T12 (D95.5): {keys_ok}")
    man = {m: PULL_DIR / f"manifest_{m}.csv.gz" for m in months()}
    pts = {m: PULL_DIR / f"gfs_points_{m}.csv.gz" for m in months()}
    ok, st_tot = totals(man, pts, plan, icaos)
    print("status totals across all months:")
    for s in p91.STATUSES:
        print(f"  {s!r:20s} {st_tot[s]:>10,}")
    print(f"  total               {sum(st_tot.values()):>10,}")
    bad = st_tot["check failed"] or st_tot["idx missing"]
    print(f"seconds {time.time() - t0:,.1f}")
    if bad:
        raise Stop(f"check failed {st_tot['check failed']}, idx missing {st_tot['idx missing']}")
    ok &= keys_ok
    print("TOTALS: PASS" if ok else "TOTALS: FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ negative tests

def run_negative(args):
    print(f"SESSION 104 --negative (offline) at {now_utc()}")
    tmp = Path(tempfile.mkdtemp(prefix="session104_neg_"))
    print(f"temporary directory {tmp}")
    before = {p.name: p91.sha256_file(p) for p in sorted(PULL_DIR.iterdir())}
    results = []
    try:
        src = PULL_DIR / "chunk_2021-03.meta.txt"
        size, sha = src.stat().st_size, before[src.name]
        cp = tmp / src.name
        shutil.copyfile(src, cp)
        ctrl = check_digest(cp, size, sha)
        b = bytearray(cp.read_bytes())
        b[100] ^= 0x01
        cp.write_bytes(bytes(b))
        bad = check_digest(cp, size, sha)
        print(f"(a) {src.name}: untouched copy passes the digest check {ctrl}; with byte 100 changed (size "
              f"{cp.stat().st_size}, unchanged) it passes {bad}")
        results.append(("(a) one byte changed fails the digest check", ctrl and not bad))
        left_out = "2023-06"
        man, pts = {}, {}
        for m in months():
            pts[m] = tmp / f"gfs_points_{m}.csv.gz"
            shutil.copyfile(PULL_DIR / pts[m].name, pts[m])
            if m != left_out:
                man[m] = tmp / f"manifest_{m}.csv.gz"
                shutil.copyfile(PULL_DIR / man[m].name, man[m])
        print(f"(b) copied {len(pts)} points files and {len(man)} manifests (manifest_{left_out}.csv.gz left out)")
        plan, icaos = full_plan()
        ok, _ = totals(man, pts, plan, icaos)
        y, mo = p91.parse_month(left_out)
        units = [(c, fh) for c, fhs in p91.plan_chunk(p91.month_cycles(y, mo), HOURS) for fh in fhs]
        print(f"    plan for {left_out}: {len(units)} files, {len(units) * 10} manifest rows, "
              f"{sum(p91.expected_messages(fh) for _, fh in units)} messages")
        print(f"    totals check result: {'PASS' if ok else 'FAIL'} (expected FAIL, on the missing keys)")
        results.append(("(b) one manifest left out fails the totals check", not ok))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = {p.name: p91.sha256_file(p) for p in sorted(PULL_DIR.iterdir())}
    print(f"temporary directory deleted: {not tmp.exists()}; MLwx-pull-f025-048/ unchanged (SHA-256 of all "
          f"{len(after)} files): {before == after}")
    for label, good in results:
        print(f"  [{'OK ' if good else 'BAD'}] {label}")
    ok = all(g for _, g in results) and before == after and not tmp.exists()
    print("NEGATIVE TESTS: AS SPECIFIED" if ok else "NEGATIVE TESTS: NOT AS SPECIFIED")
    return 0 if ok else 1


# ------------------------------------------------------------------ the inventory

def run_inventory(args):
    print(f"SESSION 104 --inventory at {now_utc()}")
    p91.check_out_free([INVENTORY, INVENTORY_META])
    api = Api()
    read_at = now_utc()
    rel, assets = api.release()
    by_name = check_release(rel, assets, quiet=True)
    print(f"Release read at {read_at}: {len(by_name)} assets; API requests {api.requests}")
    rows = []
    for m in months():
        mt = read_meta(m)
        for n in sorted(asset_names(m)):
            a = by_name[n]
            local = PULL_DIR / n
            dig = a["digest"].split(":", 1)[1]
            if p91.sha256_file(local) != dig or local.stat().st_size != a["size"]:
                raise Stop(f"{n}: the local file differs from the Release")
            rows.append([m, n, a["size"], dig, mt["script"], mt["start"]])
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(["month", "asset", "bytes", "sha256", "script_sha256", "run_start_utc"])
    w.writerows(rows)
    with open(INVENTORY, "x", newline="") as fh:
        fh.write(buf.getvalue())
    sha = p91.sha256_file(INVENTORY)
    me = p91.sha256_file(Path(__file__))
    meta = ["Provenance (SPEC 2.3). Do not edit the data file.", "",
            f"file        : {INVENTORY.name}",
            "purpose     : session 104 (DECISIONS D98.3): an inventory of the f025 to f048 GRIB pull's GitHub",
            "              Release: one row per Release asset (65 months x 3 files), with its size, its SHA-256",
            "              (equal to the Release digest and to the local copy), and, from that month's meta, the",
            "              pull script's SHA-256 and the run start.",
            f"written at  : {now_utc()}",
            "written by  : scripts/session104_pull_check.py --inventory",
            f"script sha256: {me}",
            f"rows        : {len(rows)}",
            f"sha256      : {sha}", "",
            f"release     : {REPO}, tag {TAG}, title {rel['name']!r}, published {rel['published_at']}",
            f"release read: {read_at} (GitHub REST API, unauthenticated, {api.requests} requests)",
            "columns     : month (YYYY-MM, by cycle initialisation date); asset (file name); bytes; sha256 (hex);",
            "              script_sha256 and run_start_utc (from chunk_<month>.meta.txt)",
            "sort        : by month, then asset name. Written with '\\n' line ends and no timestamp, so equal",
            "              content gives equal bytes.",
            "local copy  : MLwx-pull-f025-048/ beside the repository (not tracked); every file's SHA-256 equals its row."]
    with open(INVENTORY_META, "x") as fh:
        fh.write("\n".join(meta) + "\n")
    print(f"wrote {INVENTORY.relative_to(ROOT)} ({len(rows)} rows), SHA-256 {sha}")
    print(f"wrote {INVENTORY_META.relative_to(ROOT)}, SHA-256 {p91.sha256_file(INVENTORY_META)}")
    print(f"this script's SHA-256 {me}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for mode in ("release", "download", "months", "totals", "negative", "inventory"):
        g.add_argument(f"--{mode}", action="store_true")
    a = ap.parse_args()
    fn = {"release": run_release, "download": run_download, "months": run_months, "totals": run_totals,
          "negative": run_negative, "inventory": run_inventory}
    mode = next(k for k in fn if getattr(a, k))
    try:
        return fn[mode](a)
    except (Stop, p91.GuardError) as e:
        print(f"\nSTOP: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
