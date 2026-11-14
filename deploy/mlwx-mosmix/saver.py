#!/usr/bin/env python3
"""MOSMIX_L saver: keeps DWD's single-station MOSMIX_L forecast files, because DWD keeps only about two days.

Standard library only. Prints only metadata (names, sizes, SHA-256, issue times, station ids), never a forecast value.

Modes (exactly one):
  --list                                  print, per station, the issues on DWD's server, newest first
  --save OUTDIR --manifest-dir DIR        download every issue the manifest does not hold, check each file,
                                          make one tar per issue, and append the new rows to the manifest
  --check-fresh --manifest-dir DIR        fail if the newest issue held is more than 12 hours older than the
                                          newest issue listed, or if any one station's newest issue held is
                                          more than 12 hours older than it

Options for a trial: --only ICAO,ICAO (a few stations) and --newest N (only each station's newest N issues).

Rules: a file that fails its check is not kept and is reported; a file or tar that already exists is never
overwritten; a station and issue already in the manifest is never downloaded again; any failure makes the
exit code non-zero (the run is still carried on for the other stations, so one bad file does not hide the rest).
"""

import argparse
import csv
import hashlib
import io
import os
import re
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree

sys.dont_write_bytecode = True

BASE = "https://opendata.dwd.de/weather/local_forecasts/mos/MOSMIX_L/single_stations/"
STATIONS_CSV = Path(__file__).resolve().parent / "stations.csv"
USER_AGENT = "mlwx-mosmix-saver (private research archive)"
MANIFEST_COLUMNS = ["station", "icao", "issue", "url", "bytes", "sha256", "saved_utc", "asset", "run_id"]
NAME_RE = re.compile(r"MOSMIX_L_(\d{10})_([A-Za-z0-9]+)\.kmz")      # LATEST has no ten digits, so it never matches
LINE_RE = re.compile(r'<a href="([^"]+)">[^<]*</a>\s+\S+\s+\S+\s+(\d+|-)\s*$')
FRESH_HOURS = 12
RETRIES = 3
BACKOFF_SECONDS = (2, 4, 8)
MAX_DOWNLOAD_BYTES = 50_000_000
MAX_KML_BYTES = 200_000_000


# ---------------------------------------------------------------- the stations

def read_stations(path=STATIONS_CSV):
    """[(icao, station_id)] in file order."""
    with open(path, newline="") as f:
        return [(r["icao"], r["station_id"]) for r in csv.DictReader(f)]


# ---------------------------------------------------------------- the network

class NotFound(Exception):
    """The server says the page does not exist (not retried)."""


def http_get(url, sleep=time.sleep, opener=urllib.request.urlopen):
    """The bytes at url. A failed request is tried 3 times with a back-off; a 404 is not retried."""
    last = None
    for attempt in range(RETRIES):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with opener(req, timeout=60) as resp:
                data = resp.read(MAX_DOWNLOAD_BYTES + 1)
                if len(data) > MAX_DOWNLOAD_BYTES:
                    raise ValueError(f"more than {MAX_DOWNLOAD_BYTES} bytes")
                want = resp.headers.get("Content-Length") if getattr(resp, "headers", None) else None
                if want is not None and want.isdigit() and int(want) != len(data):
                    raise ValueError(f"got {len(data)} bytes, Content-Length said {want}")
                return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise NotFound(url)
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError, ValueError, OSError) as e:
            last = e
        if attempt < RETRIES - 1:
            sleep(BACKOFF_SECONDS[attempt])
    raise RuntimeError(f"{url}: failed after {RETRIES} tries: {last}")


# ---------------------------------------------------------------- the listing

def parse_listing(html, station):
    """{issue datetime (UTC): (file name, size in bytes or None)} for names MOSMIX_L_YYYYMMDDHH_<station>.kmz.
    LATEST and every other name are ignored."""
    out = {}
    for line in html.splitlines():
        m = LINE_RE.search(line)
        if not m:
            m2 = re.search(r'<a href="([^"]+)"', line)
            name, size = (m2.group(1), None) if m2 else (None, None)
        else:
            name, size = m.group(1), (int(m.group(2)) if m.group(2).isdigit() else None)
        if name is None:
            continue
        n = NAME_RE.fullmatch(name)
        if not n or n.group(2) != station:
            continue
        try:
            issue = datetime.strptime(n.group(1), "%Y%m%d%H").replace(tzinfo=timezone.utc)
        except ValueError:
            continue
        out[issue] = (name, size)
    return out


def list_station(station, get=http_get):
    """parse_listing of the station's directory on the server. Raises NotFound if there is no directory."""
    url = f"{BASE}{station}/kml/"
    return parse_listing(get(url).decode("utf-8", "replace"), station)


def issue_text(issue):
    return issue.strftime("%Y-%m-%dT%H:%MZ")


# ---------------------------------------------------------------- the file check (D122.4)

class _Limited(io.RawIOBase):
    """Reads at most `limit` bytes from a file object, then fails (guards against a decompression bomb)."""

    def __init__(self, f, limit):
        self.f, self.left = f, limit

    def readable(self):
        return True

    def readinto(self, b):
        data = self.f.read(min(len(b), self.left + 1))
        if len(data) > self.left:
            raise ValueError("the KML is larger than the limit")
        self.left -= len(data)
        b[:len(data)] = data
        return len(data)


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def check_kmz(path, station, issue):
    """(True, "") if the file is a valid zip holding one KML whose issue time and station id equal the
    file name's; otherwise (False, reason). Only the issue time and the station id are read from the KML."""
    path = Path(path)
    if not zipfile.is_zipfile(path):
        return False, "not a zip file"
    try:
        with zipfile.ZipFile(path) as z:
            bad = z.testzip()
            if bad is not None:
                return False, f"zip member {bad} fails its CRC"
            kmls = [i for i in z.infolist() if not i.is_dir() and i.filename.lower().endswith(".kml")]
            if len(kmls) != 1:
                return False, f"the zip holds {len(kmls)} KML files (need exactly 1)"
            issue_times, names, in_placemark = [], [], False
            with z.open(kmls[0]) as raw:
                stream = io.BufferedReader(_Limited(raw, MAX_KML_BYTES))
                for event, el in ElementTree.iterparse(stream, events=("start", "end")):
                    tag = _local(el.tag)
                    if event == "start":
                        if tag == "Placemark":
                            in_placemark = True
                    else:
                        if tag == "IssueTime":
                            issue_times.append((el.text or "").strip())
                        elif tag == "name" and in_placemark:
                            names.append((el.text or "").strip())
                        elif tag == "Placemark":
                            in_placemark = False
                        if tag not in ("Placemark", "Document", "kml"):
                            el.clear()
    except (zipfile.BadZipFile, ElementTree.ParseError, ValueError, OSError) as e:
        return False, f"the file cannot be read: {e}"
    if len(issue_times) != 1:
        return False, f"the KML has {len(issue_times)} IssueTime elements (need exactly 1)"
    try:
        kml_issue = datetime.fromisoformat(issue_times[0].replace("Z", "+00:00"))
    except ValueError:
        return False, f"the KML's issue time {issue_times[0]!r} cannot be read"
    if kml_issue.tzinfo is None:
        kml_issue = kml_issue.replace(tzinfo=timezone.utc)
    if kml_issue != issue:
        return False, f"the KML's issue time {issue_times[0]} differs from the file name's {issue_text(issue)}"
    if names != [station]:
        return False, f"the KML's station ids {names} differ from the file name's {station}"
    return True, ""


# ---------------------------------------------------------------- the manifest

def manifest_path(manifest_dir, issue):
    return Path(manifest_dir) / f"{issue:%Y-%m}.csv"


def read_manifest(manifest_dir):
    """All rows of every manifest/YYYY-MM.csv in the folder."""
    rows = []
    d = Path(manifest_dir)
    if d.is_dir():
        for p in sorted(d.glob("????-??.csv")):
            with open(p, newline="") as f:
                rows.extend(csv.DictReader(f))
    return rows


def held_keys(rows):
    """{(station, issue text)} the manifest already holds."""
    return {(r["station"], r["issue"]) for r in rows}


def append_rows(manifest_dir, new_rows):
    """Append rows to their month's file (created with a header if missing). Never rewrites a row."""
    Path(manifest_dir).mkdir(parents=True, exist_ok=True)
    held = held_keys(read_manifest(manifest_dir))
    for r in new_rows:
        if (r["station"], r["issue"]) in held:
            raise RuntimeError(f"{r['station']} {r['issue']} is already in the manifest; not added twice")
    for r in new_rows:
        issue = datetime.strptime(r["issue"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        p = manifest_path(manifest_dir, issue)
        new_file = not p.exists()
        with open(p, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS, lineterminator="\n")
            if new_file:
                w.writeheader()
            w.writerow(r)


# ---------------------------------------------------------------- saving

def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path, data):
    """Write bytes to a path that must not exist (never overwrites)."""
    with open(path, "xb") as f:
        f.write(data)


def plan_downloads(stations, manifest_dir, newest=None, get=http_get, log=print):
    """({issue: [(icao, station, name, size)]}, failures). Lists each station and keeps the issues not held."""
    held = held_keys(read_manifest(manifest_dir))
    todo, failures = {}, []
    for icao, station in stations:
        try:
            issues = list_station(station, get)
        except NotFound:
            failures.append(f"{icao} {station}: no directory on the server")
            continue
        except Exception as e:
            failures.append(f"{icao} {station}: listing failed: {e}")
            continue
        newest_issues = sorted(issues, reverse=True)[:newest] if newest else sorted(issues, reverse=True)
        for issue in newest_issues:
            if (station, issue_text(issue)) in held:
                continue
            name, size = issues[issue]
            todo.setdefault(issue, []).append((icao, station, name, size))
    return todo, failures


def save(stations, outdir, manifest_dir, run_id, newest=None, get=http_get, log=print, now=None):
    """Download, check, tar and record every issue not yet held. Returns (failures, new_tars)."""
    outdir = Path(outdir)
    todo, failures = plan_downloads(stations, manifest_dir, newest, get, log)
    tars = []
    for issue in sorted(todo):
        tag = f"{issue:%Y%m%d%H}"
        kmz_dir = outdir / "kmz" / tag
        kmz_dir.mkdir(parents=True, exist_ok=True)
        kept = []
        for icao, station, name, size in sorted(todo[issue]):
            url = f"{BASE}{station}/kml/{name}"
            dest = kmz_dir / name
            part = kmz_dir / (name + ".part")
            try:
                if dest.exists():
                    raise RuntimeError("the file already exists in the output folder; not overwritten")
                data = get(url)
                if size is not None and len(data) != size:
                    raise RuntimeError(f"got {len(data)} bytes, the listing said {size}")
                part.unlink(missing_ok=True)             # a leftover half-file from an earlier crash
                write_new(part, data)
                ok, reason = check_kmz(part, station, issue)
                if not ok:
                    part.unlink()
                    raise RuntimeError(f"failed the check ({reason}); not kept")
                os.link(part, dest)                      # fails if dest exists: never overwrites
                part.unlink()
            except NotFound:
                failures.append(f"{icao} {station} {tag}: the file is gone from the server")
                continue
            except Exception as e:
                failures.append(f"{icao} {station} {tag}: {e}")
                continue
            kept.append((icao, station, name, dest, url))
            log(f"saved  {name}  {dest.stat().st_size} bytes  sha256 {sha256_of(dest)}  checks passed")
        if not kept:
            continue
        run = run_id
        tar_name = f"MOSMIX_L_{tag}_run{run}.tar"
        tar_dir = outdir / "tars"
        tar_dir.mkdir(parents=True, exist_ok=True)
        tar_path = tar_dir / tar_name
        if tar_path.exists():
            failures.append(f"{tag}: the tar {tar_name} already exists; not overwritten, no rows written")
            continue
        try:
            with tarfile.open(tar_path, "x") as t:       # uncompressed, and refuses an existing file
                for _, _, name, dest, _ in kept:
                    t.add(dest, arcname=name)
        except Exception as e:
            failures.append(f"{tag}: could not make the tar: {e}")
            continue
        saved = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = [{"station": station, "icao": icao, "issue": issue_text(issue), "url": url,
                 "bytes": dest.stat().st_size, "sha256": sha256_of(dest), "saved_utc": saved,
                 "asset": tar_name, "run_id": run_id}
                for icao, station, _, dest, url in kept]
        append_rows(manifest_dir, rows)
        tars.append(tar_name)
        log(f"tar    {tar_name}  {tar_path.stat().st_size} bytes  {len(kept)} files")
    return failures, tars


# ---------------------------------------------------------------- the freshness rule (D122.6)

def newest_held(rows):
    issues = [datetime.strptime(r["issue"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc) for r in rows]
    return max(issues) if issues else None


def fresh_ok(held, listed, hours=FRESH_HOURS):
    """True if the newest issue held is no more than `hours` older than the newest issue listed.
    Nothing listed means nothing to be late for (the listing failing is reported by the caller)."""
    if listed is None:
        return True
    if held is None:
        return False
    return listed - held <= timedelta(hours=hours)


def stale_stations(rows, stations, listed, hours=FRESH_HOURS):
    """[(icao, station, newest held or None)] for each station whose own newest issue held is more than
    `hours` older than the newest issue listed over all stations (MS06: one station that stops getting
    new issues while its directory stays). Nothing listed means nothing to be late for."""
    if listed is None:
        return []
    newest = {}
    for r in rows:
        t = datetime.strptime(r["issue"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc)
        if r["station"] not in newest or t > newest[r["station"]]:
            newest[r["station"]] = t
    return [(icao, station, newest.get(station)) for icao, station in stations
            if not fresh_ok(newest.get(station), listed, hours)]


def check_fresh(stations, manifest_dir, get=http_get, log=print):
    """(ok, failures): D122.6's rule against the newest issue listed over `stations`, overall and for
    each station (MS06)."""
    failures, listed = [], None
    for icao, station in stations:
        try:
            issues = list_station(station, get)
        except NotFound:
            failures.append(f"{icao} {station}: no directory on the server")
            continue
        except Exception as e:
            failures.append(f"{icao} {station}: listing failed: {e}")
            continue
        if issues:
            top = max(issues)
            listed = top if listed is None or top > listed else listed
    rows = read_manifest(manifest_dir)
    held = newest_held(rows)
    overall = fresh_ok(held, listed)
    stale = stale_stations(rows, stations, listed)
    log(f"newest issue listed: {issue_text(listed) if listed else 'none'}; "
        f"newest issue held: {issue_text(held) if held else 'none'}; "
        f"rule: held no more than {FRESH_HOURS} h behind listed: {'PASS' if overall else 'FAIL'}")
    for icao, station, h in stale:
        log(f"{icao} {station}: newest issue held {issue_text(h) if h else 'none'}, more than {FRESH_HOURS} h "
            "behind the newest issue listed")
    log(f"stations more than {FRESH_HOURS} h behind: {len(stale)} of {len(stations)}: "
        f"{'PASS' if not stale else 'FAIL'}")
    return overall and not stale, failures


# ---------------------------------------------------------------- the command line

def select(stations, only):
    if not only:
        return stations
    want = {x.strip().upper() for x in only.split(",") if x.strip()}
    chosen = [s for s in stations if s[0] in want]
    missing = want - {s[0] for s in chosen}
    if missing:
        raise SystemExit(f"not in stations.csv: {sorted(missing)}")
    return chosen


def main(argv=None, get=http_get, log=print):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--list", action="store_true")
    mode.add_argument("--save", metavar="OUTDIR")
    mode.add_argument("--check-fresh", action="store_true")
    ap.add_argument("--manifest-dir", metavar="DIR")
    ap.add_argument("--only", metavar="ICAO,ICAO")
    ap.add_argument("--newest", type=int, metavar="N")
    ap.add_argument("--run-id", default=None)
    ap.add_argument("--stations", default=str(STATIONS_CSV))
    a = ap.parse_args(argv)
    if (a.save or a.check_fresh) and not a.manifest_dir:
        ap.error("--manifest-dir is needed with --save and --check-fresh")
    stations = select(read_stations(a.stations), a.only)

    if a.list:
        failures = []
        for icao, station in stations:
            try:
                issues = sorted(list_station(station, get), reverse=True)
            except NotFound:
                failures.append(f"{icao} {station}: no directory on the server")
                log(f"{icao} {station}: NO DIRECTORY")
                continue
            except Exception as e:
                failures.append(f"{icao} {station}: listing failed: {e}")
                log(f"{icao} {station}: LISTING FAILED")
                continue
            log(f"{icao} {station}: {len(issues)} issues: " + " ".join(f"{i:%Y%m%d%H}" for i in issues))
    elif a.save:
        run_id = a.run_id or os.environ.get("GITHUB_RUN_ID")
        if run_id and os.environ.get("GITHUB_RUN_ATTEMPT"):
            run_id = f"{run_id}-{os.environ['GITHUB_RUN_ATTEMPT']}"
        run_id = run_id or "local" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        failures, tars = save(stations, a.save, a.manifest_dir, run_id, a.newest, get, log)
        log(f"new tars: {len(tars)}")
        out = os.environ.get("GITHUB_OUTPUT")
        if out:
            with open(out, "a") as f:
                f.write(f"new_tars={len(tars)}\n")
    else:
        ok, failures = check_fresh(stations, a.manifest_dir, get, log)
        if not ok:
            failures.append("the freshness rule failed")
    for f in failures:
        log("FAILED: " + f)
    log("FAIL" if failures else "OK")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
