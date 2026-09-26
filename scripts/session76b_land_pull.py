"""Session 76b, Check B.2: fetch the single LAND:surface message from the
same run as session 76's HGT diagnostic (20240609 18z f026), by byte range.

Network: one .idx request and one byte-range request. Saves the message to
data/raw/diagnostics/session76b/ with a .meta.txt (SPEC 2.3). Refuses to
overwrite. Run date 2024-06-09 is before KSFO's held-out range.
"""

import datetime as dt
import hashlib
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "raw" / "diagnostics" / "session76b"
RUN, CYCLE, LEAD = dt.date(2024, 6, 9), 18, 26
URL = (f"https://noaa-gfs-bdp-pds.s3.amazonaws.com/gfs.{RUN:%Y%m%d}/{CYCLE:02d}/atmos/"
       f"gfs.t{CYCLE:02d}z.pgrb2.0p25.f{LEAD:03d}")
NAME = f"gfs_{RUN:%Y%m%d}_t{CYCLE:02d}z_f{LEAD:03d}_land_surface_SFO_diagnostic.grib2"


def main():
    assert RUN + dt.timedelta(days=1) < dt.date(2024, 8, 1)
    path = OUT / NAME
    if path.exists():
        sys.exit(f"STOP: {path.relative_to(ROOT)} exists; not overwriting.")
    OUT.mkdir(parents=True, exist_ok=True)
    s = requests.Session()
    s.headers.update({"User-Agent": "MLwx/session76b"})
    r = s.get(URL + ".idx", timeout=60)
    if r.status_code != 200:
        sys.exit(f"STOP: idx HTTP {r.status_code}")
    idx_sha = hashlib.sha256(r.content).hexdigest()
    lines = r.text.strip().splitlines()
    hits = [i for i, ln in enumerate(lines) if ln.split(":")[3:5] == ["LAND", "surface"]]
    print("LAND lines in idx:", [lines[i] for i in hits])
    if len(hits) != 1:
        sys.exit(f"STOP: expected one LAND:surface line, found {len(hits)}")
    i = hits[0]
    start = int(lines[i].split(":")[1])
    end = int(lines[i + 1].split(":")[1]) - 1
    rng = f"{start}-{end}"
    pulled = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    g = s.get(URL, headers={"Range": f"bytes={rng}"}, timeout=120)
    if g.status_code != 206:
        sys.exit(f"STOP: HTTP {g.status_code}")
    data = g.content
    if data[:4] != b"GRIB" or data[-4:] != b"7777" or len(data) != end - start + 1:
        sys.exit("STOP: incomplete message")
    path.write_bytes(data)
    meta = [
        "Raw pull provenance (SPEC 2.3). Do not edit the data file.",
        "",
        f"source: {URL}",
        f"idx source: {URL}.idx",
        f"idx sha256: {idx_sha}",
        f"idx line: {lines[i]}",
        f"byte range requested: {rng}",
        f"variable: LAND:surface (land cover, 1 = land, 0 = sea), forecast hour f{LEAD:03d}, "
        f"cycle {CYCLE:02d}z, run date {RUN:%Y%m%d}",
        "purpose: session 76b Check B.2 - land/sea value at the four 0.25 degree points around",
        "  KSFO's Open-Meteo grid point. Same run as session 76's HGT diagnostic.",
        f"pulled (UTC): {pulled}",
        f"HTTP status: {g.status_code}",
        f"bytes saved: {len(data)}",
        f"sha256: {hashlib.sha256(data).hexdigest()}",
        f"first 4 bytes: {data[:4]!r}  last 4 bytes: {data[-4:]!r}",
    ]
    (OUT / (NAME + ".meta.txt")).write_text("\n".join(meta) + "\n")
    print("\n".join(meta))


if __name__ == "__main__":
    main()
