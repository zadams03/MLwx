"""Session 95: download and check all 65 months of the stage C GRIB pull
(DECISIONS D87.5).

The Release `stagec-grib-pull-v1` of zadams03/MLwx holds three files per
month (points, manifest, meta) for 2021-03 to 2026-07. This script lists the
Release, downloads the files not yet held locally into MLwx-pull/ (outside
the repo), and checks them. The plan, the field list, the statuses and the
column layout are imported from scripts/session91_grib_pull.py; the D84.4
checks, --ranges and --gate are run by calling scripts/session92_verify_chunk.py
as a subprocess. Neither script is edited, so the plan, the checks and the
gate arithmetic stay identical.

Modes (exactly one):
  --release      Network (GitHub REST API, unauthenticated, read only).
                 Step 2: the Release's assets against the plan.
  --download     Network (the API, then each asset's browser_download_url).
                 Step 3, with --listing <saved --release output>: re-uses
                 that listing if under an hour old, else lists the Release
                 again and requires the same assets and digests. Checks every
                 file already in MLwx-pull/ against its Release size and
                 SHA-256 (any mismatch or non-asset: stop), then downloads
                 every asset not held, to a temporary name, checks size and
                 SHA-256, then gives it its asset name. At most 3 retries
                 (waits 10, 30, 90 s) on a network error, HTTP 5xx or a
                 digest mismatch. Never overwrites or deletes a held file.
  --months       Offline. Step 4: every month's meta, then the verifier (the
                 D84.4 checks) and the verifier with --ranges.
  --totals       Offline. Step 5.1 to 5.4: the union of all months against the
                 full plan, the month of every key, status totals, and the
                 "ok (whole file)" messages against F135.3's 27 broken files.
  --negative     Offline. Step 5.5: (a) a copied file with one byte changed
                 fails the digest check; (b) the totals check with one month's
                 manifest left out fails on the missing keys. Copies only, in
                 one temporary directory, deleted at the end.
  --gate         Offline. Step 6: the verifier's --gate on every month.
  --inventory    Network (one Release listing). Step 7: writes
                 data/processed/session95_pull_inventory.csv and its .meta.txt.
                 Refuses if either exists.

Hard limits: the only hosts are api.github.com and the Release's own download
links (and the host GitHub redirects them to). No GRIB request. No forecast
value is printed except per-field minimum and maximum (--months' ranges and
--totals' Step 5.4) and a gate mismatch, which the verifier prints itself.
"""

import argparse
import ast
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
import session92_verify_chunk as v92  # noqa: E402

ROOT = p91.ROOT
PULL_DIR = ROOT.parent / "MLwx-pull"
VERIFIER = ROOT / "scripts" / "session92_verify_chunk.py"
DECISIONS = p91.DECISIONS_FILE
INVENTORY = ROOT / "data" / "processed" / "session95_pull_inventory.csv"
INVENTORY_META = ROOT / "data" / "processed" / "session95_pull_inventory.csv.meta.txt"

REPO = "zadams03/MLwx"
TAG = "stagec-grib-pull-v1"
API = "https://api.github.com"
HOURS = (0, 24)
HOURS_ARG = "0-24"
PART = ".session95-part"     # suffix of a download's temporary name
DL_WAITS = (10, 30, 90)      # owner's terms after the first attempt: at most 3 retries, these waits (s)
LISTING_MAX_AGE = 3600       # a saved --release output younger than this is re-used (s)
DOWNLOAD_URL = f"https://github.com/{REPO}/releases/download/{TAG}/{{}}"

# The 27 broken files, as the session 95 prompt (Step 5.4) lists them. The
# script also reads them from DECISIONS F135.3 and requires the two to agree.
BROKEN_PROMPT = {
    "2022-11-29T18": [2, 3, 9, 11, 12, 13, 17, 18, 22, 23, 24],
    "2022-11-30T00": [2, 5, 7, 8, 10, 11, 13, 16, 20],
    "2022-11-30T06": [2, 3, 4, 5, 7, 20, 24],
}

# The fields and offsets the verifier's --gate reads, copied from
# session92_verify_chunk.py l.328-330, and its rule that skips dswrf_m2 when
# the radiation window is 2 hours (l.345-346). Used only to say which gated
# station-days use an "ok (whole file)" message (Step 6.3).
GATE_NEED = {"tmp2m": ("t2m", 0), "tcdc": ("tcdc", 0), "ugrd10m": ("u10", 0), "vgrd10m": ("v10", 0),
             "t850": ("t850", 0), "dpt2m": ("d2m", 0), "prmsl": ("prmsl", 0), "prmsl_m3": ("prmsl", -3),
             "dswrf": ("dswrf", 0), "dswrf_m2": ("dswrf", -2)}


class Stop(Exception):
    """A check failed in a way the prompt says to stop on."""


# ------------------------------------------------------------------ small helpers

def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def months():
    return [f"{y}-{m:02d}" for y, m in p91.all_months()]


def asset_names(m):
    return [f"chunk_{m}.meta.txt", f"gfs_points_{m}.csv.gz", f"manifest_{m}.csv.gz"]


def kind_of(name):
    return name.split("_", 1)[0] if not name.startswith("gfs_points") else "points"


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def decisions_text():
    return DECISIONS.read_text()


def recorded_script_shas():
    """F133's final pull-script SHA-256 and F136's, read from DECISIONS.md."""
    t = decisions_text()
    f133 = re.search(r"`scripts/session91_grib_pull\.py` \(new; modes [^)]*; final SHA-256 `([0-9a-f]{64})`", t)
    f136 = re.search(r"`scripts/session91_grib_pull\.py` \(edited; SHA-256 `([0-9a-f]{64})`\)", t)
    if not f133 or not f136:
        raise Stop("F133's or F136's pull-script SHA-256 not found in DECISIONS.md")
    return f133.group(1), f136.group(1)


def f134_files():
    """F134.1's three 2022-01 files: {name: (sha256, bytes)}."""
    t = decisions_text()
    out = {}
    for name, sha, size in re.findall(r"`(\w+_2022-01\.[\w.]+)` `([0-9a-f]{64})`, ([\d,]+)", t):
        out[name] = (sha, int(size.replace(",", "")))
    if set(out) != set(asset_names("2022-01")):
        raise Stop(f"F134.1's three files not found in DECISIONS.md: {sorted(out)}")
    return out


def f135_totals():
    t = decisions_text()
    m = re.search(r"Total ([\d,]+) B \(points ([\d,]+); manifests ([\d,]+); meta ([\d,]+)\)", t)
    if not m:
        raise Stop("F135.2's totals not found in DECISIONS.md")
    total, pts, man, meta = (int(x.replace(",", "")) for x in m.groups())
    return {"total": total, "points": pts, "manifest": man, "chunk": meta}


def f135_broken():
    """F135.3's broken files, read from DECISIONS.md: {cycle: [fh, ...]}."""
    t = decisions_text()
    line = next(ln for ln in t.splitlines() if ln.startswith("- **The broken files**"))
    out = {}
    for cyc, hours, n in re.findall(r"(\d{4}-\d{2}-\d{2}T\d{2}) ((?:f\d{3}, )*f\d{3}) \((\d+)\)", line):
        fhs = [int(h[1:]) for h in hours.split(", ")]
        if len(fhs) != int(n):
            raise Stop(f"F135.3 count mismatch at {cyc}")
        out[cyc] = fhs
    return out


# ------------------------------------------------------------------ GitHub REST API (unauthenticated)

class Api:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": "MLwx/session95", "Accept": "application/vnd.github+json",
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
    """Step 2.1 and 2.2. Returns {name: asset}. Raises Stop on any difference."""
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
        problems.append(f"assets not in the plan (another month or another name): {extra}")
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
    say(f"plan months 2021-03 to 2026-07: {len(per_month)}; with exactly 3 files: "
        f"{sum(1 for k in per_month.values() if k == 3)}; missing {len(missing)}; not in plan {len(extra)}; "
        f"state not uploaded {len(not_up)}; without digest {len(no_dig)}")
    if rel["draft"] or rel["prerelease"]:
        problems.append("the Release is a draft or a prerelease")
    # Step 2.2: the three 2022-01 assets against F134.1 and the local files.
    f134 = f134_files()
    for name, (sha, size) in sorted(f134.items()):
        a = by_name.get(name)
        local = PULL_DIR / name
        lsha = p91.sha256_file(local) if local.exists() else None
        lsize = local.stat().st_size if local.exists() else None
        rsha = a["digest"].split(":", 1)[1] if a else None
        ok = a is not None and a["size"] == size == lsize and rsha == sha == lsha
        say(f"  2022-01 {name}: Release {a['size'] if a else None} B {rsha}; F134.1 {size} B {sha}; "
            f"local {lsize} B {lsha}; all equal {ok}")
        if not ok:
            problems.append(f"2022-01 {name} differs from F134.1 or the local file")
    if problems:
        for p in problems:
            say(f"  PROBLEM: {p}")
        raise Stop("the Release differs from the plan: " + "; ".join(problems))
    return by_name


def run_release(args):
    print(f"SESSION 95 --release (GitHub REST API, unauthenticated) at {now_utc()}")
    api = Api()
    rel, assets = api.release()
    by_name = check_release(rel, assets)
    print("Step 2.1 and 2.2: PASS")
    tot = {"points": 0, "manifest": 0, "chunk": 0}
    for n, a in by_name.items():
        tot[kind_of(n)] += a["size"]
    total = sum(tot.values())
    f135 = f135_totals()
    m11 = {kind_of(n): by_name[n]["size"] for n in asset_names("2022-11")}
    print("\nStep 2.3: total size, by file kind (bytes)")
    print(f"  {'kind':9s} {'195 assets':>15s} {'F135.2 (192)':>15s} {'difference':>13s} {'2022-11 asset':>14s}")
    for k, label in (("points", "points"), ("manifest", "manifests"), ("chunk", "meta")):
        print(f"  {label:9s} {tot[k]:>15,} {f135[k]:>15,} {tot[k] - f135[k]:>13,} {m11[k]:>14,}")
    print(f"  {'total':9s} {total:>15,} {f135['total']:>15,} {total - f135['total']:>13,} {sum(m11.values()):>14,}")
    print(f"difference equals the three 2022-11 assets: {total - f135['total'] == sum(m11.values())}")
    print(f"\nasset listing (name, bytes, digest, state, created, updated):")
    for n in sorted(by_name, key=lambda x: (x.split("_")[-1], x)):
        a = by_name[n]
        print(f"  {n:28s} {a['size']:>11,} {a['digest']} {a['state']} {a['created_at']} {a['updated_at']}")
    print(f"\nAPI requests used: {api.requests} ({api.bytes:,} B)")
    return 0


def parse_release_output(path):
    """Reads a saved --release output (read only): its time, the Release's
    header fields and every asset's name, size, digest and state. Returns
    (read time, rel, assets) in the API's shape; each download link is the
    Release's standard form, DOWNLOAD_URL."""
    text = Path(path).read_text()
    t = re.search(r"^SESSION 95 --release .* at (\S+Z)$", text, re.M)
    h = re.search(r"^Release: (\S+), tag (\S+), title '(.*)', draft (\w+), prerelease (\w+), published (\S+); "
                  r"assets (\d+)", text, re.M)
    if not t or not h or h.group(1) != REPO or h.group(2) != TAG:
        raise Stop(f"{path} is not a --release output for {REPO} {TAG}")
    rel = {"tag_name": h.group(2), "name": h.group(3), "draft": h.group(4) == "True",
           "prerelease": h.group(5) == "True", "published_at": h.group(6)}
    assets = [{"name": n, "size": int(z.replace(",", "")), "digest": d, "state": st,
               "browser_download_url": DOWNLOAD_URL.format(n)}
              for n, z, d, st in re.findall(r"^  (\S+)\s+([\d,]+) (sha256:[0-9a-f]{64}) (\S+) ", text, re.M)]
    if len(assets) != int(h.group(7)):
        raise Stop(f"{path}: {len(assets)} asset lines, header says {h.group(7)}")
    when = dt.datetime.strptime(t.group(1), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    return when, rel, assets


# ------------------------------------------------------------------ Step 3: download

def check_digest(path, size, sha):
    """True when the file's size and SHA-256 equal the Release's."""
    return path.stat().st_size == size and p91.sha256_file(path) == sha


def run_download(args):
    print(f"SESSION 95 --download into {PULL_DIR} at {now_utc()}")
    api = Api()
    # The Release listing: a saved --release output under an hour old is
    # re-used; otherwise the Release is listed again and must give the same
    # 195 assets, sizes and digests as that output (owner's terms, item 3).
    when, s_rel, s_assets = parse_release_output(args.listing)
    age = (dt.datetime.now(dt.timezone.utc) - when).total_seconds()
    saved = {a["name"]: (a["size"], a["digest"]) for a in s_assets}
    if age < LISTING_MAX_AGE:
        rel, assets = s_rel, s_assets
        print(f"Release listing re-used from {args.listing} (read {when:%Y-%m-%dT%H:%M:%SZ}, {age:,.0f} s old)")
    else:
        rel, assets = api.release()
        now = {a["name"]: (a["size"], a["digest"]) for a in assets}
        print(f"saved listing is {age:,.0f} s old; Release listed again; same 195 assets, sizes and digests: "
              f"{now == saved}")
        if now != saved:
            raise Stop("the Release no longer gives the same assets, sizes and digests as Step 2")
        bad_url = [a["name"] for a in assets if a["browser_download_url"] != DOWNLOAD_URL.format(a["name"])]
        if bad_url:
            raise Stop(f"download links not in the expected form: {bad_url}")
    by_name = check_release(rel, assets, quiet=True)
    print(f"Release checked (Step 2.1, 2.2: PASS); API requests {api.requests}")
    # Every file already held must be a Release asset equal to its size and SHA-256.
    held = sorted(p.name for p in PULL_DIR.iterdir())
    not_asset = [n for n in held if n not in by_name]
    differ = [n for n in held if n in by_name
              and not check_digest(PULL_DIR / n, by_name[n]["size"], by_name[n]["digest"].split(":", 1)[1])]
    print(f"held locally: {len(held)}; not a Release asset {not_asset}; not equal to its size and SHA-256 {differ}")
    if not_asset or differ:
        raise Stop("a file in MLwx-pull/ is not a Release asset or differs from its digest")
    todo = [n for n in sorted(by_name) if n not in held]
    print(f"all {len(held)} held files equal their Release digest; to download: {len(todo)}")
    dl = requests.Session()
    dl.headers.update({"User-Agent": "MLwx/session95", "Accept": "application/octet-stream"})
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
            # Give it its asset name without ever overwriting: link fails if the
            # target exists; then drop the temporary name.
            os.link(tmp, target)
            tmp.unlink()
            last = None
            break
        if last is not None:
            raise Stop(f"{name} failed after {len(DL_WAITS)} retries: {last}")
        if i % 20 == 0 or i == len(todo):
            print(f"  {i}/{len(todo)} downloaded; {n_bytes:,} B; {time.time() - t0:,.0f} s; retries {retries}",
                  flush=True)
    secs = time.time() - t0
    print(f"\ndownloaded {len(todo)} files, {n_bytes:,} B, {secs:,.1f} s, {n_req} download requests, "
          f"retries {retries}; hosts reached {sorted(hosts)}")
    print(f"API requests {api.requests} ({api.bytes:,} B)")
    return final_listing(by_name)


def final_listing(by_name):
    """Step 3.3: MLwx-pull/ holds exactly the 195 assets, each equal to its digest,
    and no temporary file."""
    files = sorted(p.name for p in PULL_DIR.iterdir())
    parts = [f for f in files if f.endswith(PART)]
    for f in parts:      # only this script's own temporary names
        (PULL_DIR / f).unlink()
    files = sorted(p.name for p in PULL_DIR.iterdir())
    bad = [n for n in sorted(by_name) if not (PULL_DIR / n).exists()
           or not check_digest(PULL_DIR / n, by_name[n]["size"], by_name[n]["digest"].split(":", 1)[1])]
    extra = sorted(set(files) - set(by_name))
    print(f"\nMLwx-pull/: {len(files)} files; temporary files found and deleted {len(parts)}; "
          f"files not a Release asset {extra}; assets missing or not equal to their digest {bad}")
    ok = len(files) == 195 and not extra and not bad and not any(f.endswith(PART) for f in files)
    print("MLwx-pull/ holds exactly the 195 assets, each SHA-256 equal to its Release digest: " + str(ok))
    return 0 if ok else 1


# ------------------------------------------------------------------ Step 4: meta and the verifier

META_RX = {
    "start": r"^run start \(UTC\)\s+: (\S+)$",
    "end": r"^run end \(UTC\)\s+: (\S+)$",
    "seconds": r"^seconds\s+: ([\d.]+)$",
    "arguments": r"^arguments\s+: (.*)$",
    "requests": r"^requests\s+: (.*)$",
    "bytes": r"^bytes downloaded\s+: (.*)$",
    "script": r"^script sha256\s+: ([0-9a-f]{64}) ",
    "positions": r"^positions sha256\s+: ([0-9a-f]{64}) ",
    "packages": r"^packages\s+: (.*)$",
}


def read_meta(m):
    text = (PULL_DIR / f"chunk_{m}.meta.txt").read_text()
    out = {}
    for k, rx in META_RX.items():
        g = re.search(rx, text, re.M)
        if not g:
            raise Stop(f"{m}: the meta has no '{k}' line")
        out[k] = g.group(1)
    out["data_sha"] = {n: s for n, s in re.findall(r"^(\S+\.csv\.gz) sha256 ([0-9a-f]{64}) ", text, re.M)}
    out["fallback_lines"] = re.findall(r"^  fallback .*$", text, re.M)
    out["whole_line"] = (re.findall(r"^whole-file fallback \(D86\.2\): (.*)$", text, re.M) or [""])[0]
    return out


def run_verifier(m, extra):
    cmd = [sys.executable, str(VERIFIER), "--dir", str(PULL_DIR), "--month", m, "--hours", HOURS_ARG] + extra
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT / "scripts",
                       env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
    return r.returncode, r.stdout + r.stderr


def run_months(args):
    print(f"SESSION 95 --months (offline) at {now_utc()}; {PULL_DIR}")
    sha_f133, sha_f136 = recorded_script_shas()
    pos_sha = p91.sha256_file(p91.POSITIONS)
    print(f"recorded pull-script SHA-256: F133 {sha_f133}; F136 {sha_f136}; committed positions file {pos_sha}")

    # 4.1 the meta
    print("\nStep 4.1: every month's meta")
    rows, problems = [], []
    for m in months():
        mt = read_meta(m)
        names = asset_names(m)
        data_ok = all(mt["data_sha"].get(n) == p91.sha256_file(PULL_DIR / n) for n in names[1:])
        pos_ok = mt["positions"] == pos_sha
        args_want = f"--chunk --month {m} --hours {HOURS_ARG}"
        a = mt["arguments"].split()
        args_ok = mt["arguments"].startswith(args_want + " ") or mt["arguments"] == args_want
        workers = a[a.index("--workers") + 1] if "--workers" in a else "default"
        script_want = sha_f136 if m == "2022-11" else sha_f133
        script_ok = mt["script"] == script_want
        rq = re.fullmatch(r"idx (\d+), message (\d+)(?:, whole file (\d+))?; retries (\d+); HTTP 404 (\d+)",
                          mt["requests"])
        by = re.fullmatch(r"idx ([\d,]+), message ([\d,]+)(?:, whole file ([\d,]+))?, total ([\d,]+)", mt["bytes"])
        pk = re.fullmatch(r"python (\S+); eccodes \(Python\) (\S+); ecCodes library (\S+); numpy (\S+); "
                          r"requests (\S+)", mt["packages"])
        if not (rq and by and pk):
            raise Stop(f"{m}: a requests, bytes or packages line is not in the expected form")
        rows.append({"month": m, "start": mt["start"], "end": mt["end"], "seconds": mt["seconds"],
                     "workers": workers, "retries": rq.group(4), "http404": rq.group(5),
                     "bytes": by.group(4), "whole_req": rq.group(3) or "not recorded",
                     "whole_bytes": by.group(3) or "not recorded", "python": pk.group(1), "eccodes": pk.group(2),
                     "eclib": pk.group(3), "script": mt["script"], "extra_args": mt["arguments"][len(args_want):].strip(),
                     "data_ok": data_ok, "pos_ok": pos_ok, "args_ok": args_ok, "script_ok": script_ok,
                     "whole_line": mt["whole_line"], "fallback_lines": mt["fallback_lines"]})
        for flag, what in ((data_ok, "data-file SHA-256"), (pos_ok, "positions SHA-256"),
                           (args_ok, "arguments"), (script_ok, "script SHA-256")):
            if not flag:
                problems.append(f"{m}: {what} not as expected")
    print(f"  {'month':7s} {'data sha':8s} {'pos sha':7s} {'args':5s} {'script sha256':16s} {'run start':20s} "
          f"{'run end':20s} {'seconds':>8s} {'wkr':>3s} {'retries':>7s} {'404':>4s} {'bytes downloaded':>17s} "
          f"{'whole req':>12s} {'whole bytes':>14s} {'python':>8s} {'eccodes':>7s} {'ecCodes':>7s}")
    for r in rows:
        print(f"  {r['month']:7s} {str(r['data_ok']):8s} {str(r['pos_ok']):7s} {str(r['args_ok']):5s} "
              f"{r['script'][:8] + '...' + r['script'][-4:]:16s} {r['start']:20s} {r['end']:20s} {r['seconds']:>8s} "
              f"{r['workers']:>3s} {r['retries']:>7s} {r['http404']:>4s} {r['bytes']:>17s} {r['whole_req']:>12s} "
              f"{r['whole_bytes']:>14s} {r['python']:>8s} {r['eccodes']:>7s} {r['eclib']:>7s}")
    extra = sorted({r["extra_args"] for r in rows})
    print(f"arguments after '--chunk --month <m> --hours 0-24' (all months): {extra}")
    by_script = {}
    for r in rows:
        by_script.setdefault(r["script"], []).append(r["month"])
    for s, ms in by_script.items():
        print(f"script SHA-256 {s}: {len(ms)} months ({ms[0]} .. {ms[-1]}{'' if len(ms) > 1 else ''})")
    r11 = next(r for r in rows if r["month"] == "2022-11")
    print(f"2022-11 meta whole-file line: {r11['whole_line']}")
    for ln in r11["fallback_lines"]:
        print(f"  {ln.strip()}")
    print(f"versions over all months: python {sorted({r['python'] for r in rows})}; eccodes "
          f"{sorted({r['eccodes'] for r in rows})}; ecCodes library {sorted({r['eclib'] for r in rows})}")
    tot_b = sum(int(r["bytes"].replace(",", "")) for r in rows)
    tot_s = sum(float(r["seconds"]) for r in rows)
    print(f"sums over the 65 metas: bytes downloaded {tot_b:,}; chunk seconds {tot_s:,.1f}; retries "
          f"{sum(int(r['retries']) for r in rows)}; HTTP 404 {sum(int(r['http404']) for r in rows)}")
    if problems:
        for p in problems:
            print(f"  PROBLEM: {p}")
        raise Stop("a meta is not as expected")
    print("Step 4.1: every meta as expected")

    # 4.2 the verifier
    print("\nStep 4.2: session92_verify_chunk.py --dir <MLwx-pull> --month <m> --hours 0-24, every month")
    vrows = []
    raw42 = []
    for m in months():
        code, out = run_verifier(m, [])
        raw42.append((m, out))
        passed = re.search(r"^checks passed (\d+) of (\d+)", out, re.M)
        idx = re.search(r'"idx missing" messages \(published, left empty, not a fail\): (\d+); '
                        r'"ok \(whole file\)" messages \(published, filled from the whole file, not a fail\): (\d+)',
                        out)
        vrows.append((m, code, passed.group(1) if passed else "?", passed.group(2) if passed else "?",
                      idx.group(1) if idx else "?", idx.group(2) if idx else "?"))
        if code != 0 or not passed or passed.group(1) != "13" or passed.group(2) != "13":
            print(out)
            raise Stop(f"{m}: the verifier did not pass 13 of 13 (exit {code})")
    print(f"  {'month':7s} {'exit':>4s} {'checks':>8s} {'idx missing':>11s} {'ok (whole file)':>15s}")
    for m, code, a, b, i, w in vrows:
        print(f"  {m:7s} {code:>4d} {a + ' of ' + b:>8s} {i:>11s} {w:>15s}")
    print(f"months passing 13 of 13: {sum(1 for v in vrows if v[1] == 0)} of {len(vrows)}; idx missing total "
          f"{sum(int(v[4]) for v in vrows)}; ok (whole file) total {sum(int(v[5]) for v in vrows)}")

    # 4.3 ranges
    print("\nStep 4.3: the same with --ranges, every month (out of bounds and read-back mismatches)")
    overall = {f: [None, None, 0, 0] for f in p91.FIELD_NAMES}   # min, max, values, outside
    rrows, raw43 = [], []
    for m in months():
        code, out = run_verifier(m, ["--ranges"])
        raw43.append((m, out))
        if code != 0:
            print(out)
            raise Stop(f"{m}: the verifier with --ranges exited {code}")
        outside_m = 0
        for f in p91.FIELD_NAMES:
            g = re.search(rf"^  {f}\s+(\d+)\s+(\S+)\s+(\S+)\s+\S+ to \S+\s+(\d+)$", out, re.M)
            if not g:
                raise Stop(f"{m}: no ranges line for {f}")
            n, lo, hi, o = int(g.group(1)), float(g.group(2)), float(g.group(3)), int(g.group(4))
            ov = overall[f]
            ov[0] = lo if ov[0] is None else min(ov[0], lo)
            ov[1] = hi if ov[1] is None else max(ov[1], hi)
            ov[2] += n
            ov[3] += o
            outside_m += o
        rb = re.search(r"^read-back: (\d+) value cells; float then repr gives a different string in (\d+)$", out, re.M)
        rrows.append((m, outside_m, int(rb.group(1)), int(rb.group(2))))
        if outside_m or int(rb.group(2)):
            print(out)
            raise Stop(f"{m}: {outside_m} values outside the bounds, {rb.group(2)} read-back mismatches")
    print(f"  {'month':7s} {'outside bounds':>14s} {'value cells':>12s} {'read-back mismatches':>20s}")
    for m, o, n, rb in rrows:
        print(f"  {m:7s} {o:>14d} {n:>12d} {rb:>20d}")
    print(f"all months: outside bounds {sum(r[1] for r in rrows)}; value cells {sum(r[2] for r in rrows):,}; "
          f"read-back mismatches {sum(r[3] for r in rrows)}")
    print("per field over all 65 months (units as GRIB gives them; bounds from session92_verify_chunk.BOUNDS):")
    print(f"  {'field':7s} {'values':>11s} {'minimum':>22s} {'maximum':>22s} {'bounds':>20s} {'outside':>8s}")
    for f in p91.FIELD_NAMES:
        lo, hi, n, o = overall[f]
        blo, bhi = v92.BOUNDS[f]
        print(f"  {f:7s} {n:>11,} {lo!r:>22s} {hi!r:>22s} {f'{blo:g} to {bhi:g}':>20s} {o:>8d}")
    print("Step 4: PASS")
    if args.raw:
        print("\n==== raw verifier output, Step 4.2 (every month) ====")
        for m, out in raw42:
            print(f"---- {m} ----\n{out.rstrip()}")
        print("\n==== raw verifier output, Step 4.3 --ranges (every month) ====")
        for m, out in raw43:
            print(f"---- {m} ----\n{out.rstrip()}")
    return 0


# ------------------------------------------------------------------ Step 5: totals

CYCLE_BASE = dt.datetime(2021, 1, 1)


def cyc_int(s):
    t = dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")
    return int((t - CYCLE_BASE).total_seconds() // 3600)


def enc(c, fh, sub):
    """A key as one integer: cycle (hours since 2021-01-01), forecast hour, then
    the field or airport index."""
    return (c * 49 + fh) * 64 + sub


def full_plan():
    """The full plan for every month, from session 91's own functions."""
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
    """Union of the months' keys against the plan, by key set and by count."""
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


def totals(man_paths, pts_paths, plan, icaos, detail=True):
    """Step 5.1 to 5.3. man_paths, pts_paths: {month: path}. Returns (all passed,
    status totals, per-month status counts)."""
    say = print if detail else (lambda *a: None)
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
    status_month = {}
    for m in months():
        sm = {s: 0 for s in p91.STATUSES}
        if m in man_paths:
            head, rows = v92.read_gz_csv(man_paths[m])
            if head != p91.MAN_COLS:
                raise Stop(f"{m}: manifest layout")
            for r in rows:
                c, fh, f, st = r[0], int(r[1]), r[2], r[6]
                if c[:7] != m:
                    wrong_month.append(("manifest", m, c, fh, f))
                if f not in fidx or st not in sm:
                    unknown += 1
                    continue
                k = enc(ci(c), fh, fidx[f])
                m_key.append(k)
                m_file.append(ci(c) * 49 + fh)
                if st != "absent by design":
                    m_msg.append(k)
                sm[st] += 1
            m_cyc += list({ci(r[0]) for r in rows})
        status_month[m] = sm
        for s in sm:
            status_tot[s] += sm[s]
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
    say("Step 5.1: the union over all months against the full plan (session 91's plan, imported)")
    a = np.array
    compare("cycles (manif.)", a(m_cyc, dtype=np.int64), plan["cycles"], res)
    compare("cycles (points)", a(p_cyc, dtype=np.int64), plan["cycles"], res)
    compare("files (manif.)", np.unique(a(m_file, dtype=np.int64)), plan["files"], res)
    compare("files (points)", a(p_file, dtype=np.int64), plan["files"], res)
    compare("manifest rows", a(m_key, dtype=np.int64), plan["manifest"], res)
    compare("messages", a(m_msg, dtype=np.int64), plan["messages"], res)
    compare("points rows", a(p_key, dtype=np.int64), plan["points"], res)
    say("Step 5.2: every key in the month of its cycle's initialisation date")
    ok52 = not wrong_month and unknown == 0
    res.append(("month of key", ok52))
    say(f"  [{'PASS' if ok52 else 'FAIL'}] keys whose cycle is in another month: {len(wrong_month)}; "
        f"rows with an unknown field or airport or status: {unknown}")
    for w in wrong_month[:10]:
        say(f"      {w}")
    say("  (a key holds its cycle, so a key that sits only in its own cycle's month cannot sit in two months; "
        "the union check above also finds no key in more than one row)")
    return all(ok for _, ok in res), status_tot, status_month


def run_totals(args):
    print(f"SESSION 95 --totals (offline) at {now_utc()}; {PULL_DIR}")
    t0 = time.time()
    plan, icaos = full_plan()
    print(f"full plan (session91_grib_pull: all_months, month_cycles, plan_chunk, FIELDS, selector; hours 0-24): "
          f"{len(plan['cycles']):,} cycles, {len(plan['files']):,} files, {len(plan['manifest']):,} manifest rows, "
          f"{len(plan['messages']):,} messages, {len(plan['points']):,} points rows ({len(icaos)} airports)")
    print(f"against F133.5 and the prompt: cycles 7,828 {len(plan['cycles']) == 7828}; files 195,600 "
          f"{len(plan['files']) == 195600}; messages 1,932,528 {len(plan['messages']) == 1932528}; points rows "
          f"9,975,600 {len(plan['points']) == 9975600}")
    man = {m: PULL_DIR / f"manifest_{m}.csv.gz" for m in months()}
    pts = {m: PULL_DIR / f"gfs_points_{m}.csv.gz" for m in months()}
    ok, st_tot, st_month = totals(man, pts, plan, icaos)
    print("\nStep 5.3: status totals across all months")
    for s in p91.STATUSES:
        print(f"  {s!r:20s} {st_tot[s]:>10,}")
    print(f"  total               {sum(st_tot.values()):>10,}")
    print("  months with any status other than ok and absent by design: "
          + str({m: {s: n for s, n in c.items() if s not in ('ok', 'absent by design') and n}
                 for m, c in st_month.items() if any(n for s, n in c.items()
                                                     if s not in ('ok', 'absent by design'))}))
    ok53 = st_tot[p91.STATUS_WHOLE] == 270 and st_tot["check failed"] == 0
    print(f"  [{'PASS' if ok53 else 'FAIL'}] ok (whole file) exactly 270 ({st_tot[p91.STATUS_WHOLE]}); "
          f"check failed 0 ({st_tot['check failed']})")
    ok &= ok53

    print("\nStep 5.4: the whole-file messages")
    broken_d = f135_broken()
    print(f"F135.3's broken files (read from DECISIONS.md): "
          + "; ".join(f"{c} {', '.join(f'f{h:03d}' for h in fhs)} ({len(fhs)})" for c, fhs in broken_d.items()))
    print(f"equal to the prompt's list: {broken_d == BROKEN_PROMPT}")
    if broken_d != BROKEN_PROMPT:
        raise Stop("F135.3 and the prompt's list differ")
    expect = {(f"{c[:10]}T{c[11:13]}:00Z", fh) for c, fhs in BROKEN_PROMPT.items() for fh in fhs}
    whole_by_file, whole_other = {}, []
    t12 = {}
    for m in months():
        _, rows = v92.read_gz_csv(man[m])
        for r in rows:
            k = (r[0], int(r[1]))
            if r[6] == p91.STATUS_WHOLE:
                whole_by_file.setdefault(k, []).append(r[2])
            if r[0].startswith("2022-11-29T12"):
                t12[r[6]] = t12.get(r[6], 0) + 1
    got = set(whole_by_file)
    all_ten = all(sorted(v) == sorted(p91.FIELD_NAMES) for v in whole_by_file.values())
    n_whole = sum(len(v) for v in whole_by_file.values())
    ok54 = got == expect and all_ten and n_whole == 270
    print(f"  files with any ok (whole file) message: {len(got)}; equal to the 27: {got == expect}; "
          f"missing {sorted(expect - got)}; extra {sorted(got - expect)}")
    print(f"  each of these files has all ten fields ok (whole file): {all_ten}; ok (whole file) messages "
          f"anywhere: {n_whole} (all inside these files: {n_whole == 270 and got <= expect})")
    n12 = sum(p91.expected_messages(fh) for fh in range(HOURS[0], HOURS[1] + 1))
    ok12 = set(t12) <= {"ok", "absent by design"} and t12.get("ok", 0) == n12
    print(f"  2022-11-29T12 statuses: {t12}; planned messages {n12}; every message ok: {ok12}")
    ok54 &= ok12
    print(f"  [{'PASS' if ok54 else 'FAIL'}] whole-file messages are exactly F135.3's 27 files, ten fields each")
    ok &= ok54
    # whole-file values against 2022-11's normal ok values, per field
    _, mrows = v92.read_gz_csv(man["2022-11"])
    st = {(r[0], int(r[1]), r[2]): r[6] for r in mrows}
    p_head, p_rows = v92.read_gz_csv(pts["2022-11"])
    pc = {c: i for i, c in enumerate(p_head)}
    print("  per field, 2022-11 (units as GRIB gives them; bounds from session92_verify_chunk.BOUNDS):")
    print(f"  {'field':7s} {'whole n':>8s} {'whole min':>20s} {'whole max':>20s} {'out':>4s}   "
          f"{'ok n':>8s} {'ok min':>20s} {'ok max':>20s} {'out':>4s}")
    out_tot = 0
    for f in p91.FIELD_NAMES:
        lo_b, hi_b = v92.BOUNDS[f]
        acc = {"w": [0, None, None, 0], "o": [0, None, None, 0]}
        cols = [pc[f"{f}_{j}"] for j in (1, 2, 3, 4)]
        for r in p_rows:
            s = st[(r[0], int(r[1]), f)]
            key = "w" if s == p91.STATUS_WHOLE else "o" if s == "ok" else None
            if key is None:
                continue
            a = acc[key]
            for i in cols:
                v = float(r[i])
                a[0] += 1
                a[1] = v if a[1] is None else min(a[1], v)
                a[2] = v if a[2] is None else max(a[2], v)
                a[3] += not (lo_b <= v <= hi_b)
        w, o = acc["w"], acc["o"]
        out_tot += w[3] + o[3]
        print(f"  {f:7s} {w[0]:>8d} {w[1]!r:>20s} {w[2]!r:>20s} {w[3]:>4d}   {o[0]:>8d} {o[1]!r:>20s} "
              f"{o[2]!r:>20s} {o[3]:>4d}")
    print(f"  values outside the bounds (whole file and ok together): {out_tot} (expected 0)")
    ok &= out_tot == 0
    print(f"\nseconds {time.time() - t0:,.1f}")
    print("STEP 5.1 TO 5.4: PASS" if ok else "STEP 5.1 TO 5.4: FAIL")
    return 0 if ok else 1


# ------------------------------------------------------------------ Step 5.5: negative tests

def run_negative(args):
    print(f"SESSION 95 --negative (offline) at {now_utc()}")
    # The digest to test against is the local file's own SHA-256, which Step 3
    # checked equal to the Release's.
    tmp = Path(tempfile.mkdtemp(prefix="session95_neg_"))
    print(f"temporary directory {tmp}")
    before = {p.name: p91.sha256_file(p) for p in sorted(PULL_DIR.iterdir())}
    results = []
    try:
        # (a) one byte changed in a copied file must fail the digest check.
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
        # (b) the totals check with one month's manifest left out.
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
        ok, st_tot, _ = totals(man, pts, plan, icaos)
        y, mo = p91.parse_month(left_out)
        units = [(c, fh) for c, fhs in p91.plan_chunk(p91.month_cycles(y, mo), HOURS) for fh in fhs]
        print(f"    plan for {left_out}: {len(units)} files, {len(units) * 10} manifest rows, "
              f"{sum(p91.expected_messages(fh) for _, fh in units)} messages")
        print(f"    totals check result: {'PASS' if ok else 'FAIL'} (expected FAIL, on the missing keys)")
        results.append(("(b) one manifest left out fails the totals check", not ok))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    after = {p.name: p91.sha256_file(p) for p in sorted(PULL_DIR.iterdir())}
    print(f"temporary directory deleted: {not tmp.exists()}; MLwx-pull/ unchanged (SHA-256 of all "
          f"{len(after)} files): {before == after}")
    for label, good in results:
        print(f"  [{'OK ' if good else 'BAD'}] {label}")
    ok = all(g for _, g in results) and before == after and not tmp.exists()
    print("NEGATIVE TESTS: AS SPECIFIED" if ok else "NEGATIVE TESTS: NOT AS SPECIFIED")
    return 0 if ok else 1


# ------------------------------------------------------------------ Step 6: the extended gate

def run_gate(args):
    print(f"SESSION 95 --gate (offline) at {now_utc()}: session92_verify_chunk.py --gate on every month")
    airports = p91.load_airports()
    gated = [st for st, a in airports.items() if a["lead"] <= HOURS[1]]
    print(f"gated: {[(st, a['cycle'], a['lead']) for st, a in airports.items() if st in gated]}; "
          f"not gated (lead outside 0-24): {[(st, a['lead']) for st, a in airports.items() if st not in gated]}")
    tot = {"days": 0, "compared": 0, "equal": 0, "mism": 0, "no_row": [], "not_built": []}
    col_tot = {c: {st: [0, 0] for st in gated} for c in p91.GATE_COLS}
    ap_tot = {st: [0, 0, 0, 0] for st in gated}   # rebuilt, all 7 equal, values ok, values n
    rows, raw, whole_used = [], [], []
    for m in months():
        code, out = run_verifier(m, ["--gate"])
        raw.append((m, out))
        g_try = re.search(r"^station-days in the month: (\d+); rebuilt and compared (\d+)$", out, re.M)
        g_no = re.search(r"^station-days with no committed row \(not a failure\): (\d+) ?(.*)$", out, re.M)
        g_nb = re.search(r"^station-days not rebuilt \(a needed message not ok or ok \(whole file\)\): (\d+) ?(.*)$",
                         out, re.M)
        g_mm = re.search(r"^mismatches: (\d+)$", out, re.M)
        if not (g_try and g_no and g_nb and g_mm):
            print(out)
            raise Stop(f"{m}: the gate output is not in the expected form (exit {code})")
        no_row = ast.literal_eval(g_no.group(2)) if g_no.group(2) else []
        not_built = ast.literal_eval(g_nb.group(2)) if g_nb.group(2) else []
        n_mm = int(g_mm.group(1))
        eq_days = 0
        for st in gated:
            g = re.search(rf"^  {st}\s+\(\S+\): station-days rebuilt (\d+), all 7 columns equal (\d+); "
                          rf"values (\d+) of (\d+)$", out, re.M)
            vals = [int(x) for x in g.groups()]
            for i in range(4):
                ap_tot[st][i] += vals[i]
            eq_days += vals[1]
        for c in p91.GATE_COLS:
            g = re.search(rf"^  {c}\s+(.*)$", out, re.M)
            pairs = re.findall(r"(\d+) / (\d+)", g.group(1))
            for st, (a, b) in zip(gated, pairs[:len(gated)]):
                col_tot[c][st][0] += int(a)
                col_tot[c][st][1] += int(b)
        rows.append((m, int(g_try.group(1)), int(g_try.group(2)), eq_days, n_mm, len(no_row), len(not_built), code))
        tot["days"] += int(g_try.group(1))
        tot["compared"] += int(g_try.group(2))
        tot["equal"] += eq_days
        tot["mism"] += n_mm
        tot["no_row"] += [(m,) + tuple(x) for x in no_row]
        tot["not_built"] += [(m,) + tuple(x) for x in not_built]
        if n_mm:
            print(out)
            raise Stop(f"{m}: the gate found {n_mm} mismatches (printed above in full)")
        # Step 6.3: does any gated station-day use an "ok (whole file)" message?
        _, mrows = v92.read_gz_csv(PULL_DIR / f"manifest_{m}.csv.gz")
        st_of = {(r[0], int(r[1]), r[2]): r[6] for r in mrows}
        y, mo = p91.parse_month(m)
        cyc = {c for c, _ in p91.plan_chunk(p91.month_cycles(y, mo), HOURS)}
        for st in gated:
            a = airports[st]
            for c in sorted(x for x in cyc if x.hour == a["cycle"]):
                used = []
                for key, (fname, off) in GATE_NEED.items():
                    if key == "dswrf_m2" and a["lead"] - p91.window_start(a["lead"]) == 2:
                        continue
                    k = (p91.iso(c), a["lead"] + off, fname)
                    if st_of.get(k) == p91.STATUS_WHOLE:
                        used.append(f"{fname} f{a['lead'] + off:03d}")
                if used:
                    tgt = (c + dt.timedelta(days=1)).date().isoformat()
                    whole_used.append((st, tgt, p91.iso(c), used))
    print(f"\nper month: station-days in the month, compared, all 7 columns equal, mismatched, "
          f"no committed row, not rebuilt, verifier exit")
    print(f"  {'month':7s} {'days':>5s} {'compared':>8s} {'equal':>6s} {'mism':>5s} {'no row':>6s} "
          f"{'not built':>9s} {'exit':>4s}")
    for m, d, c, e, mm, nr, nb, code in rows:
        print(f"  {m:7s} {d:>5d} {c:>8d} {e:>6d} {mm:>5d} {nr:>6d} {nb:>9d} {code:>4d}")
    print(f"  {'total':7s} {tot['days']:>5d} {tot['compared']:>8d} {tot['equal']:>6d} {tot['mism']:>5d} "
          f"{len(tot['no_row']):>6d} {len(tot['not_built']):>9d}")
    print("\npass table by column, all months (exact equality, no tolerance):")
    print(f"  {'column':34s} " + " ".join(f"{st:>13s}" for st in gated) + f" {'all':>13s}")
    for c in p91.GATE_COLS:
        print(f"  {c:34s} " + " ".join(f"{col_tot[c][st][0]:>6d} / {col_tot[c][st][1]:<4d}" for st in gated)
              + f" {sum(col_tot[c][s][0] for s in gated):>6d} / {sum(col_tot[c][s][1] for s in gated)}")
    print("pass table by airport, all months:")
    for st in gated:
        r, e, vo, vn = ap_tot[st]
        print(f"  {st:5s}: station-days rebuilt {r}, all 7 columns equal {e}; values {vo} of {vn}")
    # Step 6.2: not rebuilt
    outside = [x for x in tot["not_built"] if x[0] == "2026-07" and x[2] == "2026-08-01"]
    other_nb = [x for x in tot["not_built"] if x not in outside]
    print(f"\nnot rebuilt: {len(tot['not_built'])}; of them 2026-07 with target 2026-08-01 (outside the window): "
          f"{len(outside)} {outside}; any other: {len(other_nb)} {other_nb}")
    # Step 6.3: no committed row
    print(f"no committed row (not a failure): {len(tot['no_row'])}")
    for st in gated:
        ds = [x[2] for x in tot["no_row"] if x[1] == st]
        print(f"  {st}: {len(ds)} {ds}")
    beyond = [x for x in tot["no_row"] if x[2] > "2026-07-31"]
    print(f"  of these, target dates after 2026-07-31 (outside the window and the training set): "
          f"{len(beyond)} {beyond}")
    print(f"gated station-days that use an ok (whole file) message: {len(whole_used)}")
    no_row_set = {(x[1], x[2]) for x in tot["no_row"]}
    for st, tgt, c, used in whole_used:
        print(f"  {st} target {tgt} (cycle {c}): {', '.join(used)}; committed row: {(st, tgt) not in no_row_set}")
    ok = tot["mism"] == 0 and not other_nb
    print("\nEXTENDED GATE OVER ALL MONTHS: PASSED" if ok else "\nEXTENDED GATE OVER ALL MONTHS: NOT PASSED")
    if other_nb:
        raise Stop(f"station-days not rebuilt for another reason: {other_nb}")
    if args.raw:
        print("\n==== raw verifier --gate output (every month) ====")
        for m, out in raw:
            print(f"---- {m} ----\n{out.rstrip()}")
    return 0 if ok else 1


# ------------------------------------------------------------------ Step 7: the inventory

def run_inventory(args):
    print(f"SESSION 95 --inventory at {now_utc()}")
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
            lsha = p91.sha256_file(local)
            if lsha != dig or local.stat().st_size != a["size"]:
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
            "purpose     : session 95, Step 7 - an inventory of the stage C GRIB pull's GitHub Release (DECISIONS",
            "              D87.5): one row per Release asset (65 months x 3 files), with its size, its SHA-256 (equal",
            "              to the Release digest and to the local copy), and, from that month's meta, the pull",
            "              script's SHA-256 and the run start.",
            f"written at  : {now_utc()}",
            "written by  : scripts/session95_check_release.py --inventory",
            f"script sha256: {me}",
            f"rows        : {len(rows)}",
            f"sha256      : {sha}", "",
            f"release     : {REPO}, tag {TAG}, title {rel['name']!r}, published {rel['published_at']}",
            f"release read: {read_at} (GitHub REST API, unauthenticated, {api.requests} requests)",
            "columns     : month (YYYY-MM, by cycle initialisation date); asset (file name); bytes; sha256 (hex);",
            "              script_sha256 and run_start_utc (from chunk_<month>.meta.txt)",
            "sort        : by month, then asset name. Written with '\\n' line ends and no timestamp, so equal",
            "              content gives equal bytes.",
            "local copy  : MLwx-pull/ beside the repository (not tracked); every file's SHA-256 equals its row."]
    with open(INVENTORY_META, "x") as fh:
        fh.write("\n".join(meta) + "\n")
    print(f"wrote {INVENTORY.relative_to(ROOT)} ({len(rows)} rows), SHA-256 {sha}")
    print(f"wrote {INVENTORY_META.relative_to(ROOT)}, SHA-256 {p91.sha256_file(INVENTORY_META)}")
    print(f"this script's SHA-256 {me}")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for mode in ("release", "download", "months", "totals", "negative", "gate", "inventory"):
        g.add_argument(f"--{mode}", action="store_true")
    ap.add_argument("--raw", action="store_true", help="--months, --gate: also print every verifier output")
    ap.add_argument("--listing", help="--download: a saved --release output (re-used if under an hour old)")
    a = ap.parse_args()
    fn = {"release": run_release, "download": run_download, "months": run_months, "totals": run_totals,
          "negative": run_negative, "gate": run_gate, "inventory": run_inventory}
    mode = next(k for k in fn if getattr(a, k))
    try:
        return fn[mode](a)
    except (Stop, p91.GuardError) as e:
        print(f"\nSTOP: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
