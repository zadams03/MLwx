"""Session 88: read-only probe of DWD MOSMIX (D78.3, D80). Reads the network and prints.

It writes no data file. It never prints, records or saves a forecast value:
KML files are read for header fields, element names, station names and
positions only. Downloads go to one temporary directory outside the repo,
which is deleted at the end. At most one MOSMIX_S all-stations file is read,
and only if the listing shows it is under 200 MB. No MOSMIX_L all-stations
file is downloaded.

Run: python3 scripts/session88_competitor_probe.py
"""
import datetime as dt
import io
import math
import re
import shutil
import sys
import tempfile
import time
import zipfile
import xml.etree.ElementTree as ET

import requests

BASE = "https://opendata.dwd.de/weather/local_forecasts/mos"
L_ALL = BASE + "/MOSMIX_L/all_stations/kml/"
S_ALL = BASE + "/MOSMIX_S/all_stations/kml/"
SS = BASE + "/MOSMIX_L/single_stations/"
CFG = "https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/mosmix_stationskatalog.cfg?view=nasPublication"
SPL = "https://www.dwd.de/DE/leistungen/met_verfahren_mosmix/mosmix_stationsparameterliste.xlsx?__blob=publicationFile&v=8"
MET = "https://opendata.dwd.de/weather/lib/MetElementDefinition.xml"
S_LIMIT = 200 * 1024 * 1024
NS_DWD = "{https://opendata.dwd.de/weather/lib/pointforecast_dwd_extension_V1_0.xsd}"

# SPEC 3.4: station code, latitude, longitude, elevation (m), target hour UTC
AIRPORTS = {
    "EGLC": (51.5053, 0.0553, 5, 12),
    "LFPG": (49.0153, 2.5344, 109, 12),
    "DSM": (41.534, -93.6531, 294, 18),
    "YSDU": (-32.2167, 148.5747, 275, 2),
    "RNO": (39.4839, -119.7711, 1345, 20),
    "SFO": (37.619, -122.3749, 5, 20),
}
# SPEC 7.2 and D77.2: our GFS cycle and lead at each target hour
GFS_LEAD = {"EGLC": ("12z", 24), "LFPG": ("12z", 24), "YSDU": ("00z", 26)}

LOG = []  # (utc time, url, status, bytes)
TMP = tempfile.mkdtemp(prefix="s88_")


def now():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def get(url, stream=False):
    for attempt in range(3):
        try:
            r = requests.get(url, timeout=120, stream=stream)
            break
        except requests.RequestException as e:
            if attempt == 2:
                raise
            time.sleep(3)
    n = None if stream else len(r.content)
    LOG.append([now(), url, r.status_code, n])
    time.sleep(0.5)
    return r


def get_checked(url, ok, what):
    """The server sometimes answers 200 with a short body. Retry, and say so."""
    for attempt in range(4):
        r = get(url)
        if ok(r.content):
            return r
        print(f"  note: {what} answered HTTP {r.status_code} with {len(r.content)} bytes that failed the "
              f"check (attempt {attempt + 1}); first bytes {r.content[:60]!r}")
        time.sleep(8)
    raise RuntimeError(f"{what}: no usable answer after 4 tries")


def finish_stream(url, n):
    for row in LOG:
        if row[1] == url and row[3] is None:
            row[3] = n


def hav(a, b, c, d):
    p = math.radians
    x = math.sin(p(c - a) / 2) ** 2 + math.cos(p(a)) * math.cos(p(c)) * math.sin(p(d - b) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(x))


def dm(s):
    """The cfg lists degrees and minutes as DD.MM (DWD procedure doc, FAQ 9.1)."""
    v = float(s)
    sg = -1 if v < 0 else 1
    v = abs(v)
    d = int(v)
    return sg * (d + round((v - d) * 100, 4) / 60)


def listing(url):
    r = get(url)
    out = []
    for m in re.finditer(r'<a href="([^"]+)">[^<]*</a>\s+(\d\d-\w{3}-\d{4} \d\d:\d\d:\d\d)\s+(\S+)', r.text):
        out.append((m.group(1), m.group(2), m.group(3)))
    return r.status_code, out


def issue_of(name):
    m = re.search(r"_(\d{10})(?:_|\.)", name)
    return dt.datetime.strptime(m.group(1), "%Y%m%d%H").replace(tzinfo=dt.timezone.utc) if m else None


def report_listing(title, url):
    code, rows = listing(url)
    print(f"\n{title}\n  URL {url}  accessed {now()}  HTTP {code}")
    dated = [(n, t, s) for n, t, s in rows if issue_of(n)]
    print(f"  issue files: {len(dated)} (plus {len(rows) - len(dated)} other entries: "
          f"{[n for n, t, s in rows if not issue_of(n)]})")
    if dated:
        first, last = issue_of(dated[0][0]), issue_of(dated[-1][0])
        print(f"  oldest issue {first:%Y-%m-%d %H}Z, newest issue {last:%Y-%m-%d %H}Z, "
              f"span {(last - first).total_seconds() / 3600:.0f} h")
    for n, t, s in rows:
        print(f"    {n:<40} server time {t}   {s} bytes")
    return dated


def local(el):
    return el.tag.rsplit("}", 1)[-1]


def iter_local(root, name):
    return [e for e in root.iter() if local(e) == name]


def kml_header(data):
    """Header fields, element names and the Placemark name, description, coordinates. No values."""
    root = ET.fromstring(data)
    out = {}
    pd = root.find(".//" + "{*}ProductDefinition")
    out["IssueTime"] = pd.find("{*}IssueTime").text.strip()
    out["GeneratingProcess"] = pd.find("{*}GeneratingProcess").text.strip()
    out["ReferencedModel"] = [(m.get(NS_DWD + "name"), m.get(NS_DWD + "referenceTime"))
                              for m in iter_local(pd, "Model")]
    steps = [e.text.strip() for e in iter_local(pd, "TimeStep")]
    out["steps"] = (len(steps), steps[0], steps[1], steps[-1])
    pms = []
    for pm in iter_local(root, "Placemark"):
        names = [f.get(NS_DWD + "elementName") for f in iter_local(pm, "Forecast")]
        pms.append({"id": pm.find("{*}name").text, "description": pm.find("{*}description").text,
                    "coordinates": pm.find(".//{*}coordinates").text, "elements": names})
    out["placemarks"] = pms
    return out


def kmz_header(url):
    r = get(url)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    return kml_header(z.read(z.namelist()[0])), r.status_code, len(r.content)


def parse_cfg():
    r = get_checked(CFG, lambda b: len(b) > 100000, "station catalogue")
    rows = []
    for ln in r.content.decode("latin-1").splitlines()[2:]:
        m = re.match(r"^\s*(\S+)\s+(\S+)\s+(.*?)\s+(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+(-?\d+)\s*$", ln)
        if m:
            rows.append((m.group(1), m.group(2), m.group(3), m.group(4), m.group(5), int(m.group(6))))
    return rows, len(r.content), len(r.content.decode("latin-1").splitlines()) - 2


def parse_spl():
    """Sheet 1 of the station parameter list: ID, name, lon, lat, elev, CofX, TTT, ..."""
    r = get_checked(SPL, lambda b: b[:2] == b"PK", "station parameter list")
    z = zipfile.ZipFile(io.BytesIO(r.content))
    ss = z.read("xl/sharedStrings.xml").decode("utf8")
    strings = [re.sub(r"<[^>]+>", "", m) for m in re.findall(r"<si>(.*?)</si>", ss, re.S)]
    sheet = z.read("xl/worksheets/sheet1.xml").decode("utf8")
    rows = {}
    header = None
    for rm in re.finditer(r"<row [^>]*>(.*?)</row>", sheet, re.S):
        cells = {}
        for cm in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*?)(?:/>|>(.*?)</c>)', rm.group(1), re.S):
            col, attrs, body = cm.group(1), cm.group(2), cm.group(3) or ""
            v = re.search(r"<v>(.*?)</v>", body, re.S)
            if not v:
                continue
            val = strings[int(v.group(1))] if 't="s"' in attrs else v.group(1)
            cells[col] = val
        if not cells:
            continue
        if header is None:
            if cells.get("A") == "ID":
                header = cells
            continue
        rows[cells.get("A")] = cells
    return header, rows, len(r.content)


def s_file_scan(url, size):
    """Stream one MOSMIX_S all-stations KMZ. Header, station count, and the named stations'
    metadata only. Every forecast value is skipped."""
    r = get(url, stream=True)
    path = f"{TMP}/s_file.kmz"
    n = 0
    with open(path, "wb") as f:
        for chunk in r.iter_content(1 << 20):
            f.write(chunk)
            n += len(chunk)
    finish_stream(url, n)
    z = zipfile.ZipFile(path)
    name = z.namelist()[0]
    info = z.getinfo(name)
    head = b""
    count = 0
    tail = b""
    wanted = {}
    ids = [b"P0478", b"07157", b"72546", b"72488", b"72494"]
    with z.open(name) as f:
        buf = b""
        while True:
            chunk = f.read(1 << 22)
            if not chunk:
                break
            buf = tail + chunk
            if not head:
                i = buf.find(b"<kml:Placemark")
                if i >= 0:
                    head = buf[:i]
            count += buf.count(b"<kml:Placemark>") - tail.count(b"<kml:Placemark>")
            for sid in ids:
                if sid in wanted:
                    continue
                k = buf.find(b"<kml:name>" + sid + b"</kml:name>")
                if k >= 0:
                    e = buf.find(b"</kml:Placemark>", k)
                    if e >= 0:
                        wanted[sid] = buf[k:e]
            tail = buf[-60:]
    # header text: take ProductDefinition by regex (no placemark is parsed as a whole)
    hd = head.decode("utf8", "replace")
    out = {"compressed": n, "uncompressed": info.file_size, "placemarks": count}
    out["IssueTime"] = re.search(r"<dwd:IssueTime>(.*?)</dwd:IssueTime>", hd).group(1)
    out["ReferencedModel"] = re.findall(r'<dwd:Model dwd:name="([^"]+)" dwd:referenceTime="([^"]+)"', hd)
    steps = re.findall(r"<dwd:TimeStep>(.*?)</dwd:TimeStep>", hd)
    out["steps"] = (len(steps), steps[0], steps[1], steps[-1])
    st = {}
    for sid, blob in wanted.items():
        t = blob.decode("utf8", "replace")
        st[sid.decode()] = {
            "description": re.search(r"<kml:description>(.*?)</kml:description>", t).group(1),
            "coordinates": re.search(r"<kml:coordinates>(.*?)</kml:coordinates>", t).group(1),
            "elements": re.findall(r'dwd:elementName="([^"]+)"', t),
        }
    out["stations"] = st
    return out


def main():
    print(f"Session 88 MOSMIX probe. Started {now()}. Python {sys.version.split()[0]}, requests {requests.__version__}")
    print("Metadata only: no forecast value is printed, recorded or saved.")

    # ---- 2.1 listings
    print("\n===== 2.1 Listings =====")
    l_dated = report_listing("MOSMIX_L all stations (first listing)", L_ALL)
    s_dated = report_listing("MOSMIX_S all stations", S_ALL)

    # ---- 2.4 station catalogue
    print("\n===== 2.4 Stations =====")
    rows, nbytes, nlines = parse_cfg()
    print(f"Catalogue {CFG}\n  accessed {now()}, {nbytes} bytes, {nlines} data lines, {len(rows)} parsed")
    print("  The cfg gives latitude and longitude as degrees.minutes (DWD procedure doc 9.1); converted here.")
    near = {}
    for k, (la, lo, el, h) in AIRPORTS.items():
        c = sorted((hav(la, lo, dm(r[3]), dm(r[4])), r) for r in rows)[:3]
        near[k] = c
        print(f"  {k}: airport {la}, {lo}, {el} m")
        for d, r in c:
            print(f"     {d:8.2f} km  ID {r[0]}  ICAO {r[1]}  {r[2]}  cfg {r[3]},{r[4]} (= {dm(r[3]):.4f},{dm(r[4]):.4f})  "
                  f"{r[5]} m  height difference {r[5] - el:+d} m")
    # Step 2.4: confirm single-station directories
    chosen = {"EGLC": "P0478", "LFPG": "07157", "DSM": "72546", "RNO": "72488", "SFO": "72494"}
    print("  YSDU: no station within 10 km (nearest above); no single-station directory to check.")
    print("\nSingle-station directories:")
    code, idx = listing(SS)
    idset = {n.strip("/") for n, t, s in idx}
    print(f"  {SS} HTTP {code}, {len(idx)} station directories listed")
    ss_dated = {}
    for k, sid in chosen.items():
        d = report_listing(f"single station {sid} ({k}), in {'the index' if sid in idset else 'NOT in the index'}",
                           f"{SS}{sid}/kml/")
        ss_dated[sid] = d

    # ---- 2.3 / 2.5 headers
    print("\n===== 2.3 / 2.5 KML headers (names, times, positions only) =====")
    hdrs = {}
    for k, sid in chosen.items():
        files = [n for n, t, s in ss_dated[sid] if issue_of(n)]
        use = files if k in ("EGLC", "LFPG") else files[-1:]
        for n in use:
            h, code, nb = kmz_header(f"{SS}{sid}/kml/{n}")
            hdrs[(sid, n)] = h
            pm = h["placemarks"][0]
            print(f"\n  {n}  HTTP {code}  {nb} bytes\n    IssueTime {h['IssueTime']}  process '{h['GeneratingProcess']}'")
            print(f"    ReferencedModel {h['ReferencedModel']}")
            print(f"    time steps {h['steps'][0]}: first {h['steps'][1]}, second {h['steps'][2]}, last {h['steps'][3]}")
            print(f"    placemark {pm['id']} '{pm['description']}' coordinates (lon,lat,elev) {pm['coordinates']}")
            print(f"    elements {len(pm['elements'])}; TTT present: {'TTT' in pm['elements']}")
    # distances from the KML positions
    print("\n  Distance from the SPEC 3.4 airport position, using the KML position (decimal degrees):")
    for k, sid in chosen.items():
        h = [v for (s, n), v in hdrs.items() if s == sid][-1]
        lon, lat, el = [float(x) for x in h["placemarks"][0]["coordinates"].split(",")]
        la, lo, ael, th = AIRPORTS[k]
        print(f"    {k} -> {sid}: {hav(la, lo, lat, lon):.2f} km, height difference {el - ael:+.0f} m")
    first = [v for (s, n), v in hdrs.items() if s == "P0478"][-1]["placemarks"][0]["elements"]
    print(f"\n  Element list of one MOSMIX_L file ({len(first)} names): {', '.join(first)}")

    # ---- 2.3 MetElementDefinition
    print("\n===== 2.3 MetElementDefinition.xml: TTT =====")
    r = get(MET)
    txt = r.text
    print(f"  {MET} accessed {now()} HTTP {r.status_code} {len(r.content)} bytes")
    for el in ET.fromstring(r.content).iter("MetElement"):
        if (el.findtext("ShortName") or "").strip() in ("TTT", "E_TTT"):
            print("  ", {c.tag: (c.text or "").strip() for c in el})

    # ---- 2.4 main or interpolation station
    print("\n===== 2.4 Station parameter list (main or interpolation) =====")
    hdr, srows, nb = parse_spl()
    print(f"  {SPL} accessed {now()} {nb} bytes; sheet 'MOSMIX-Stationen ab 06-2026'")
    print("  Legend (procedure documentation, Annex A, table A.2): +++ nearly hourly forecasts from MOS equations;")
    print("  ++ nearly 3-hourly from MOS equations; ooo nearly hourly from interpolated equations; ++o nearly hourly,")
    print("  of which nearly 3-hourly from MOS equations (the rest interpolated); empty = element not forecast.")
    print(f"  Columns: {hdr}")
    for k, sid in chosen.items():
        row = srows.get(sid)
        if row is None:
            print(f"  {k} {sid}: NOT in sheet 1")
            continue
        ttt = row.get("H", "")
        others = sorted({row.get(c, "") for c in "IJKLMNOPQRSTUVW"} - {""})
        print(f"  {k} {sid} '{row.get('B')}': changed since previous version = {row.get('F')}; "
              f"TTT symbol '{ttt}'; symbols across the other 15 elements {others}")

    # ---- 2.3 MOSMIX_S one file
    print("\n===== 2.2 / 2.3 MOSMIX_S, one all-stations file =====")
    pick = s_dated[-1]
    size = int(pick[2])
    print(f"  newest dated file {pick[0]} server time {pick[1]} size {size} bytes (limit {S_LIMIT})")
    if size < S_LIMIT:
        sres = s_file_scan(S_ALL + pick[0], size)
        print(f"  downloaded {sres['compressed']} bytes; KML {sres['uncompressed']} bytes; placemarks {sres['placemarks']}")
        print(f"  IssueTime {sres['IssueTime']}; ReferencedModel {sres['ReferencedModel']}")
        print(f"  time steps {sres['steps'][0]}: first {sres['steps'][1]}, second {sres['steps'][2]}, last {sres['steps'][3]}")
        for sid, v in sres["stations"].items():
            print(f"  station {sid} '{v['description']}' coordinates {v['coordinates']}; {len(v['elements'])} elements; "
                  f"TTT present: {'TTT' in v['elements']}")
        any_el = next(iter(sres["stations"].values()))["elements"]
        print(f"  MOSMIX_S element list ({len(any_el)}): {', '.join(any_el)}")
    else:
        print("  not downloaded: over the size limit")

    # ---- 2.5 timing
    print("\n===== 2.5 Timing =====")
    print("  Illustration day D = 2026-10-01 (all four MOSMIX_L issues of D-1 = 2026-09-30 are on the server).")
    l_hdr = {issue_of(n): v for (s, n), v in hdrs.items() if s == "P0478"}
    for k in ("EGLC", "LFPG", "YSDU"):
        la, lo, el, th = AIRPORTS[k]
        tgt = dt.datetime(2026, 10, 1, th, tzinfo=dt.timezone.utc)
        cyc = GFS_LEAD[k]
        print(f"\n  {k}: target {tgt:%Y-%m-%d %H}Z. Our GFS (SPEC 7.2, D77.2): {cyc[0]} on D-1, lead {cyc[1]} h.")
        if k == "YSDU":
            print("    No MOSMIX station within 10 km, so no MOSMIX issue is listed for it.")
            print("    (Timing for a MOSMIX station would follow the same rule: every issue on D-1 with lead = target - issue.)")
            continue
        print("    MOSMIX_L issues on D-1 (lead = target minus issue time; models are the header's ReferencedModel):")
        for it in sorted(l_hdr):
            if it.date() == dt.date(2026, 9, 30):
                lead = (tgt - it).total_seconds() / 3600
                print(f"      issue {it:%Y-%m-%d %H}Z  lead {lead:.0f} h  models {l_hdr[it]['ReferencedModel']}")
        print("    MOSMIX_S issues on D-1: hourly, 00Z to 23Z, one per hour (listing above); "
              f"leads {(tgt - dt.datetime(2026, 9, 30, 23, tzinfo=dt.timezone.utc)).total_seconds() / 3600:.0f} h "
              f"(23Z) to {(tgt - dt.datetime(2026, 9, 30, 0, tzinfo=dt.timezone.utc)).total_seconds() / 3600:.0f} h (00Z).")
        print("    MOSMIX_S models: only the one S header read above is available; older S files were not downloaded.")

    # ---- 2.1 second listing
    print("\n===== 2.1 MOSMIX_L all stations, second listing =====")
    report_listing("MOSMIX_L all stations (second listing)", L_ALL)

    # ---- totals
    tot = sum(r[3] or 0 for r in LOG)
    print(f"\n===== Totals (this script only) =====\n  requests {len(LOG)}, bytes {tot}")
    for row in LOG:
        print("  ", *row)
    shutil.rmtree(TMP, ignore_errors=True)
    print(f"  temporary directory {TMP} deleted: {not __import__('os').path.exists(TMP)}")
    print(f"Finished {now()}")


if __name__ == "__main__":
    main()
