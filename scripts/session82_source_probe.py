"""Session 82: stage A's read-only source probe (DECISIONS D74.3, F123).

Reads from the network and prints. It writes no data file, and nothing
under data/. What it does, per source:

- lists buckets, folders and inventory (.idx / .index) files;
- finds when a folder layout or a field first appears, by bisecting over
  dates with listings or inventories;
- decodes a few single GRIB2 messages (byte-range fetches, at most 10 per
  source, none over 20 MB, all dated on or before 2026-07-31) and prints
  their metadata only: name, level, step or window, units, grid. No value
  at any airport or grid point is printed, extracted or saved;
- asks the MOS archive and Open-Meteo's Previous Runs API only for row or
  hour counts, projection times and grid metadata, never printing a value.

Sample bytes go to a temporary directory made with tempfile.mkdtemp()
outside the repo, which is deleted at the end of the run.

Hard limit: nothing dated (or valid) 2026-08-01 or later is opened or
decoded. For live feeds, only a listing of names, sizes and times is read.

Usage: python scripts/session82_source_probe.py [section ...]
Sections: ecmwf gefs nbm mos icon openmeteo v17 weathernext (default: all)
"""

import datetime as dt
import json
import os
import re
import shutil
import sys
import tempfile
import time

import eccodes
import requests

LAST_OK = dt.date(2026, 7, 31)          # nothing dated after this is opened
MAX_MSG_BYTES = 20 * 1024 * 1024        # sample-decode size limit
PAUSE = 0.4                             # seconds between requests (politeness)
TMP = tempfile.mkdtemp(prefix="session82_probe_")
MSG_COUNT = {}                          # decoded messages per source

ECMWF = "https://ecmwf-forecasts.s3.eu-central-1.amazonaws.com/"
GEFS = "https://noaa-gefs-pds.s3.amazonaws.com/"
NBM = "https://noaa-nbm-grib2-pds.s3.amazonaws.com/"

# EGLC's position (SPEC 3.4), used only for Open-Meteo grid metadata and
# present/null counts.
EGLC = (51.5053, 0.0553)


# ---------------------------------------------------------------- helpers

def say(*a):
    print(*a, flush=True)


def get(url, **kw):
    """HTTP GET with retries on throttling or a dropped connection, and a
    polite pause."""
    for i in range(7):
        try:
            r = requests.get(url, timeout=(10, 60), **kw)
        except requests.exceptions.ConnectionError:
            if i == 6:
                raise
            time.sleep(5 * (i + 1))
            continue
        if r.status_code not in (429, 500, 502, 503):
            break
        time.sleep(5 * (i + 1))
    time.sleep(PAUSE)
    return r


def s3list(base, prefix="", delim="/", maxpages=20):
    """Anonymous S3 ListObjectsV2 over HTTPS: (prefixes, [(key, size, time)])."""
    pre, keys, token = [], [], None
    for _ in range(maxpages):
        p = {"list-type": "2", "prefix": prefix}
        if delim:
            p["delimiter"] = delim
        if token:
            p["continuation-token"] = token
        t = get(base, params=p).text
        pre += re.findall(r"<CommonPrefixes><Prefix>([^<]*)</Prefix>", t)
        for c in re.findall(r"<Contents>(.*?)</Contents>", t, re.S):
            keys.append((re.search(r"<Key>([^<]*)", c).group(1),
                         int(re.search(r"<Size>(\d+)", c).group(1)),
                         re.search(r"<LastModified>([^<]*)", c).group(1)))
        m = re.search(r"<NextContinuationToken>([^<]*)", t)
        if not m:
            break
        token = m.group(1)
    return pre, keys


def dates_between(a, b):
    return [a + dt.timedelta(i) for i in range((b - a).days + 1)]


def ymd(d):
    return d.strftime("%Y%m%d")


def bisect(lo, hi, test):
    """lo: test False, hi: test True. Returns (last False, first True).
    test() may return None (missing); the next day is then tried."""
    while (hi - lo).days > 1:
        mid = lo + dt.timedelta((hi - lo).days // 2)
        v = test(mid)
        while v is None and mid < hi - dt.timedelta(1):
            mid += dt.timedelta(1)
            v = test(mid)
        if v:
            hi = mid
        else:
            lo = mid
    return lo, hi


def check_date(d):
    if d > LAST_OK:
        raise SystemExit(f"STOP: {d} is after {LAST_OK}; not opened (scope guard)")


def decode_meta(source, url, offset, length, file_date):
    """Byte-range fetch one GRIB message and print its metadata only."""
    check_date(file_date)
    if length > MAX_MSG_BYTES:
        say(f"    SKIP (message {length} B > 20 MB): {url}")
        return
    n = MSG_COUNT.get(source, 0)
    if n >= 10:
        raise SystemExit(f"STOP: 10-message limit reached for {source}")
    r = get(url, headers={"Range": f"bytes={offset}-{offset + length - 1}"})
    path = os.path.join(TMP, f"{source}_{n}.grib2")
    with open(path, "wb") as f:
        f.write(r.content)
    MSG_COUNT[source] = n + 1
    with open(path, "rb") as f:
        h = eccodes.codes_grib_new_from_file(f)
        k = {}
        for key in ["shortName", "name", "typeOfLevel", "level", "stepType",
                    "stepRange", "units", "gridType", "Ni", "Nj", "Nx", "Ny",
                    "iDirectionIncrementInDegrees", "jDirectionIncrementInDegrees",
                    "DxInMetres", "DyInMetres", "dataDate", "dataTime",
                    "numberOfDataPoints", "edition", "centre"]:
            try:
                k[key] = eccodes.codes_get(h, key)
            except Exception:
                pass
        eccodes.codes_release(h)
    say(f"    decoded [{source} #{n + 1}] {len(r.content)} B: "
        + ", ".join(f"{a}={b}" for a, b in k.items()))


def idx_lines(url):
    """NOAA .idx inventory: list of (msgno, offset, 'VAR:LEVEL:STEP:extra')."""
    r = get(url)
    if r.status_code != 200:
        return None
    out = []
    for line in r.text.splitlines():
        f = line.split(":")
        out.append((int(f[0]), int(f[1]), ":".join(f[3:])))
    return out


def idx_ranges(lines, total_size):
    """Byte (offset, length) of each idx line; last one runs to file end."""
    res = []
    for i, (_, off, desc) in enumerate(lines):
        end = lines[i + 1][1] if i + 1 < len(lines) else total_size
        res.append((desc, off, end - off))
    return res


def head_size(url):
    r = requests.head(url, timeout=(10, 60))
    time.sleep(PAUSE)
    return int(r.headers.get("Content-Length", 0)), r.status_code


FIELDS = ["2m temperature", "total cloud cover", "10 m wind",
          "2 m dewpoint", "850 hPa temperature", "sfc/MSL pressure",
          "downward SW at surface"]


def field_row(label, flags):
    say(f"  {label}: " + "; ".join(f"{n}={'yes' if f else 'NO'}"
                                   for n, f in zip(FIELDS, flags)))


# ------------------------------------------------------------------ ECMWF

def ecmwf_index(path):
    r = get(ECMWF + path)
    if r.status_code != 200:
        return None
    return [json.loads(x) for x in r.text.splitlines() if x.strip().startswith("{")]


def ecmwf_path(d, model="ifs", step=24, cyc="00", stream="oper"):
    s = ymd(d)
    fn = f"{s}{cyc}0000-{step}h-{stream}-fc"
    if d < dt.date(2024, 2, 1):
        return f"{s}/{cyc}z/0p4-beta/{stream}/{fn}"
    if d < dt.date(2024, 2, 29):
        return f"{s}/{cyc}z/0p25/{stream}/{fn}"
    if model == "aifs-single" and d < dt.date(2025, 2, 26):
        return f"{s}/{cyc}z/aifs-single/0p25/experimental/{stream}/{fn}"
    return f"{s}/{cyc}z/{model}/0p25/{stream}/{fn}"


def ecmwf_flags(L):
    sfc = {x["param"] for x in L if x.get("levtype") == "sfc"}
    t850 = any(x["param"] == "t" and x.get("levelist") == "850" for x in L)
    return [("2t" in sfc), ("tcc" in sfc), ({"10u", "10v"} <= sfc),
            ("2d" in sfc), t850, bool({"msl", "sp"} & sfc), ("ssrd" in sfc)]


def section_ecmwf():
    say("\n==================== 1. ECMWF open data (IFS, AIFS) ====================")
    say(f"bucket: {ECMWF} (anonymous HTTPS S3 listing)")
    pre, keys = s3list(ECMWF)
    ds = sorted(p.strip("/") for p in pre if re.fullmatch(r"\d{8}/", p))
    say(f"top-level non-date prefixes: {[p for p in pre if not re.fullmatch(r'\d{8}/', p)]}")
    say(f"date folders: {len(ds)}, first {ds[0]}, last {ds[-1]} (listing only)")
    d0 = dt.datetime.strptime(ds[0], "%Y%m%d").date()
    d1 = dt.datetime.strptime(ds[-1], "%Y%m%d").date()
    miss = [ymd(d) for d in dates_between(d0, d1) if ymd(d) not in set(ds)]
    say(f"missing date folders between first and last: {len(miss)} {miss}")
    say(f"first folder's cycles: {[p.split('/')[-2] for p in s3list(ECMWF, ds[0] + '/')[0]]}")

    say("\nlayout under <date>/00z/ at key dates:")
    for d in ["20230118", "20240131", "20240201", "20240228", "20240229",
              "20250209", "20250210", "20250225", "20250226", "20250701",
              "20250702", "20260731"]:
        say(f"  {d}: {[p.split('/')[-2] for p in s3list(ECMWF, d + '/00z/')[0]]}")

    say("\nforecast steps (hours) in oper folders:")
    for pfx in ["20230118/00z/0p4-beta/oper/", "20240201/00z/0p25/oper/",
                "20260731/00z/ifs/0p25/oper/", "20260731/06z/ifs/0p25/oper/",
                "20260731/12z/ifs/0p25/oper/", "20260731/00z/aifs-single/0p25/oper/"]:
        _, k = s3list(ECMWF, pfx)
        steps = sorted({int(m.group(1)) for x in k
                        if x[0].endswith(".grib2") and (m := re.search(r"-(\d+)h-", x[0]))})
        say(f"  {pfx}: {len(steps)} steps: {steps[:20]} ... {steps[-3:]}")

    say("\nfields in the 00z step-24 oper .index (the seven SPEC 8 inputs):")
    for d, model in [(dt.date(2023, 1, 18), "ifs"), (dt.date(2024, 2, 1), "ifs"),
                     (dt.date(2024, 3, 5), "ifs"), (dt.date(2024, 3, 6), "ifs"),
                     (dt.date(2025, 11, 20), "ifs"), (dt.date(2025, 11, 21), "ifs"),
                     (dt.date(2026, 7, 31), "ifs"), (dt.date(2024, 2, 29), "aifs"),
                     (dt.date(2025, 2, 10), "aifs-single"),
                     (dt.date(2026, 7, 31), "aifs-single")]:
        p = ecmwf_path(d, model) + ".index"
        L = ecmwf_index(p)
        if L is None:
            say(f"  {p}: not found")
            continue
        field_row(f"{model} {d} ({len(L)} msgs; {p})", ecmwf_flags(L))
        levs = sorted({int(x["levelist"]) for x in L if x.get("levtype") == "pl"})
        say(f"      pressure levels: {levs}")

    say("\nbisections (00z, step 24, IFS oper):")

    def has_sfc(p):
        def t(d):
            L = ecmwf_index(ecmwf_path(d) + ".index")
            return None if L is None else any(
                x["param"] == p and x.get("levtype") == "sfc" for x in L)
        return t
    for p in ["2d", "ssrd", "tcc"]:
        say(f"  {p}: last absent / first present = "
            f"{bisect(dt.date(2024, 2, 1), dt.date(2026, 7, 31), has_sfc(p))}")

    def has_sub(name):
        return lambda d: any(x.endswith(f"/{name}/") for x in s3list(ECMWF, ymd(d) + "/00z/")[0])
    say(f"  aifs-single folder: {bisect(dt.date(2024, 2, 29), dt.date(2025, 2, 25), has_sub('aifs-single'))}")
    say(f"  aifs-ens folder: {bisect(dt.date(2025, 2, 25), dt.date(2026, 1, 1), has_sub('aifs-ens'))}")
    say(f"  'aifs' (pre-operational) folder gone: "
        f"{bisect(dt.date(2025, 2, 25), dt.date(2025, 7, 1), lambda d: not has_sub('aifs')(d))}")

    def aifs_oper(d):
        return any(x.endswith("/oper/") for x in s3list(ECMWF, ymd(d) + "/00z/aifs-single/0p25/")[0])
    say(f"  aifs-single 0p25/experimental/ -> 0p25/oper/: "
        f"{bisect(dt.date(2025, 2, 10), dt.date(2025, 9, 1), aifs_oper)}")

    say("\nlive feed: data.ecmwf.int/forecasts/ listing (names only):")
    r = get("https://data.ecmwf.int/forecasts/")
    live = sorted(set(re.findall(r'href="[^"]*?(\d{8})/"', r.text)))
    say(f"  HTTP {r.status_code}; date folders listed: {live}")
    say("  latest AWS folder and its file times (listing only):")
    _, k = s3list(ECMWF, f"{ds[-1]}/00z/ifs/0p25/oper/")
    t = sorted(x[2] for x in k)
    if t:
        say(f"    {ds[-1]}/00z/ifs/0p25/oper/: {len(k)} objects, LastModified {t[0]} .. {t[-1]}")

    say("\nsample decodes (metadata only), 2025-12-01 00z, step 24 (<= 2026-07-31):")
    d = dt.date(2025, 12, 1)
    for model, want in [("ifs", [("2t", None), ("tcc", None), ("10u", None), ("2d", None),
                                 ("t", "850"), ("msl", None), ("ssrd", None)]),
                        ("aifs-single", [("2t", None), ("tcc", None), ("ssrd", None)])]:
        p = ecmwf_path(d, model)
        L = ecmwf_index(p + ".index")
        for param, lev in want:
            m = [x for x in L if x["param"] == param and (lev is None or x.get("levelist") == lev)]
            decode_meta("ECMWF", ECMWF + p + ".grib2", m[0]["_offset"], m[0]["_length"], d)


# ------------------------------------------------------------------- GEFS

def section_gefs():
    say("\n==================== 3. NOAA GEFS (AWS noaa-gefs-pds) ====================")
    say(f"bucket: {GEFS} (anonymous HTTPS S3 listing)")
    pre, _ = s3list(GEFS)
    ds = sorted(p[5:13] for p in pre if p.startswith("gefs."))
    say(f"date folders: {len(ds)}, first {ds[0]}, last {ds[-1]}")
    d0 = dt.datetime.strptime(ds[0], "%Y%m%d").date()
    d1 = dt.datetime.strptime(ds[-1], "%Y%m%d").date()
    miss = [ymd(d) for d in dates_between(d0, d1) if ymd(d) not in set(ds)]
    say(f"missing date folders: {len(miss)} {miss[:30]}")
    for d in ["20200922", "20200923", "20210324", "20260731"]:
        say(f"  gefs.{d}/00/: {[p.split('/')[-2] for p in s3list(GEFS, f'gefs.{d}/00/')[0]]}")
    say(f"  gefs.20260731/00/atmos/: "
        f"{[p.split('/')[-2] for p in s3list(GEFS, 'gefs.20260731/00/atmos/')[0]]}")

    say("\nmembers and forecast hours (control member gec00):")
    for d, cyc, sub in [("20210324", "00", "pgrb2sp25"), ("20210324", "00", "pgrb2ap5"),
                        ("20260731", "00", "pgrb2sp25"), ("20260731", "00", "pgrb2ap5"),
                        ("20260731", "06", "pgrb2sp25"), ("20260731", "06", "pgrb2ap5")]:
        _, k = s3list(GEFS, f"gefs.{d}/{cyc}/atmos/{sub}/")
        n = [x[0].split("/")[-1] for x in k]
        mem = sorted({x.split(".")[0] for x in n})
        fh = sorted({int(x.split(".f")[-1]) for x in n if x.startswith("gec00") and not x.endswith(".idx")})
        say(f"  {d} {cyc}z {sub}: {len(mem)} members ({mem[0]}..{mem[-1]}); "
            f"gec00 f-hours {fh[:12]} ... {fh[-3:]} ({len(fh)})")

    def flags(sp, ap):
        s = {x[2].rsplit(":", 1)[0] if x[2].endswith(":") else x[2] for x in sp}
        a = {x[2] for x in ap}
        both = s | a
        return [any(x.startswith("TMP:2 m above ground") for x in s),
                any(x.startswith("TCDC:entire atmosphere") for x in s),
                any(x.startswith("UGRD:10 m") for x in s) and any(x.startswith("VGRD:10 m") for x in s),
                any(x.startswith("DPT:2 m above ground") for x in s),
                any(x.startswith("TMP:850 mb") for x in both),
                any(x.startswith("PRES:surface") or x.startswith("PRMSL:") for x in s),
                any(x.startswith("DSWRF:surface") for x in s)]

    say("\nfields at f024 (sp25 = 0.25 deg 'pgrb2s'; ap5 = 0.5 deg 'pgrb2a'):")
    for d in ["20210324", "20260731"]:
        sp = idx_lines(f"{GEFS}gefs.{d}/00/atmos/pgrb2sp25/gec00.t00z.pgrb2s.0p25.f024.idx")
        ap = idx_lines(f"{GEFS}gefs.{d}/00/atmos/pgrb2ap5/gec00.t00z.pgrb2a.0p50.f024.idx")
        field_row(f"gec00 {d} 00z f024 (sp25 {len(sp)} msgs, ap5 {len(ap)} msgs)", flags(sp, ap))
        say(f"      850 hPa TMP in sp25: {any('TMP:850 mb' in x[2] for x in sp)}; "
            f"in ap5: {any('TMP:850 mb' in x[2] for x in ap)}")
        say(f"      sp25 cloud/SW lines: {[x[2] for x in sp if x[2].startswith(('TCDC', 'DSWRF'))]}")
        if d == "20210324":
            base = {x[2].split(':')[0] + ':' + x[2].split(':')[1] for x in sp}
        else:
            new = {x[2].split(':')[0] + ':' + x[2].split(':')[1] for x in sp}
            say(f"  sp25 fields added 2021-03-24 -> 2026-07-31: {sorted(new - base)}; removed: {sorted(base - new)}")
    sp21 = idx_lines(f"{GEFS}gefs.20210324/00/atmos/pgrb2sp25/gec00.t00z.pgrb2s.0p25.f027.idx")
    say(f"  f027 window check (sp25 2021-03-24): {[x[2] for x in sp21 if x[2].startswith(('TCDC', 'DSWRF'))]}")

    def has_vis(d):
        L = idx_lines(f"{GEFS}gefs.{ymd(d)}/00/atmos/pgrb2sp25/gec00.t00z.pgrb2s.0p25.f024.idx")
        return None if L is None else any(x[2].startswith("VIS:surface") for x in L)
    say(f"  sp25 VIS:surface first appears (field-set change marker): "
        f"{bisect(dt.date(2021, 3, 24), dt.date(2026, 7, 31), has_vis)}")

    say("\nsample decodes (metadata only), 2026-07-01 00z gec00 f024:")
    d = dt.date(2026, 7, 1)
    u = f"{GEFS}gefs.20260701/00/atmos/pgrb2sp25/gec00.t00z.pgrb2s.0p25.f024"
    size, _ = head_size(u)
    rng = idx_ranges(idx_lines(u + ".idx"), size)
    for want in ["TMP:2 m above ground", "DPT:2 m above ground", "TCDC:entire atmosphere",
                 "UGRD:10 m above ground", "PRES:surface", "PRMSL:mean sea level",
                 "DSWRF:surface"]:
        m = [x for x in rng if x[0].startswith(want)][0]
        decode_meta("GEFS", u, m[1], m[2], d)
    u = f"{GEFS}gefs.20260701/00/atmos/pgrb2ap5/gec00.t00z.pgrb2a.0p50.f024"
    size, _ = head_size(u)
    m = [x for x in idx_ranges(idx_lines(u + ".idx"), size) if x[0].startswith("TMP:850 mb")][0]
    decode_meta("GEFS", u, m[1], m[2], d)


# -------------------------------------------------------------------- NBM

def section_nbm():
    say("\n==================== 5. NOAA NBM (AWS noaa-nbm-grib2-pds) ====================")
    say(f"bucket: {NBM} (anonymous HTTPS S3 listing)")
    pre, _ = s3list(NBM)
    ds = sorted(p[6:14] for p in pre if p.startswith("blend."))
    say(f"date folders: {len(ds)}, first {ds[0]}, last {ds[-1]}")
    d0 = dt.datetime.strptime(ds[0], "%Y%m%d").date()
    d1 = dt.datetime.strptime(ds[-1], "%Y%m%d").date()
    miss = [d.isoformat() for d in dates_between(d0, d1) if ymd(d) not in set(ds)]
    say(f"missing date folders: {len(miss)} {miss}")
    for d in ["20200518", "20210324", "20260731"]:
        cyc = [p.split('/')[-2] for p in s3list(NBM, f"blend.{d}/")[0]]
        say(f"  blend.{d}/: {len(cyc)} cycles; 00/: "
            f"{[p.split('/')[-2] for p in s3list(NBM, f'blend.{d}/00/')[0]]}")
    other = "https://noaa-nbm-pds.s3.amazonaws.com/"
    p, _ = s3list(other)
    say(f"  second bucket {other}: prefixes {p}")
    for q in p[:2] + p[-1:]:
        p2, k2 = s3list(other, q)
        say(f"    {q}: {p2[:6]} {[x[0] for x in k2][:4]}")

    def co_hours(d):
        _, k = s3list(NBM, f"blend.{ymd(d)}/00/core/")
        return sorted({int(m.group(1)) for x in k if ".co.grib2" in x[0] and not x[0].endswith("idx")
                       and (m := re.search(r"\.f(\d{3})\.", x[0]))})

    say("\nCONUS ('co') forecast hours, 00z:")
    for d in [dt.date(2021, 3, 24), dt.date(2026, 7, 31)]:
        h = co_hours(d)
        say(f"  {d}: {h[:50]} ... {h[-3:]} ({len(h)})")

    def core_layout(d):
        return any(x.endswith("/core/") for x in s3list(NBM, f"blend.{ymd(d)}/00/")[0])
    say(f"  grib2/ -> core/ layout: {bisect(dt.date(2020, 5, 18), dt.date(2021, 3, 24), core_layout)}")
    say(f"  CONUS hourly steps extended past f036 (f037 present): "
        f"{bisect(dt.date(2021, 3, 24), dt.date(2026, 7, 31), lambda d: 37 in co_hours(d))}")

    def has_global(d):
        _, k = s3list(NBM, f"blend.{ymd(d)}/00/core/")
        return any(".global.grib2" in x[0] for x in k)
    say(f"  'global' domain appears: {bisect(dt.date(2021, 3, 24), dt.date(2026, 7, 31), has_global)}")

    def flags(L):
        s = {x[2] for x in L}
        return [any(x.startswith("TMP:2 m above ground") for x in s),
                any(x.startswith("TCDC:surface") for x in s),
                any(x.startswith("WIND:10 m above ground") for x in s),
                any(x.startswith("DPT:2 m above ground") for x in s),
                any(x.startswith("TMP:850 mb") for x in s),
                any(x.startswith(("PRES:surface", "PRMSL", "MSLMA", "PRES:mean sea level")) for x in s),
                any(x.startswith("DSWRF:surface") for x in s)]

    say("\nfields at f024, 00z:")
    for d, dom in [("20210324", "co"), ("20260731", "co"), ("20260731", "global")]:
        L = idx_lines(f"{NBM}blend.{d}/00/core/blend.t00z.core.f024.{dom}.grib2.idx")
        field_row(f"{dom} {d} ({len(L)} msgs)", flags(L))
        if dom == "co":
            say(f"      lines: {[x[2] for x in L if x[2].startswith(('TMP:2 m', 'TCDC:surface', 'WIND:10 m', 'DPT:2 m', 'DSWRF'))]}")
        else:
            say(f"      variables: {sorted({':'.join(x[2].split(':')[:2]) for x in L})}")
    say(f"  text bulletins, blend.20260731/00/text/: "
        f"{[(x[0].split('/')[-1], x[1]) for x in s3list(NBM, 'blend.20260731/00/text/')[1]]}")

    say("\nsample decodes (metadata only), 2026-07-01 00z co f024:")
    d = dt.date(2026, 7, 1)
    u = f"{NBM}blend.20260701/00/core/blend.t00z.core.f024.co.grib2"
    size, _ = head_size(u)
    rng = idx_ranges(idx_lines(u + ".idx"), size)
    for want in ["TMP:2 m above ground:24 hour fcst:", "DPT:2 m above ground:24 hour fcst:",
                 "TCDC:surface:24 hour fcst:", "WIND:10 m above ground:24 hour fcst:",
                 "DSWRF:surface:24 hour fcst:"]:
        m = [x for x in rng if x[0] == want][0]
        decode_meta("NBM", u, m[1], m[2], d)


# -------------------------------------------------------------------- MOS

def section_mos():
    say("\n==================== 6. NWS MOS (IEM archive API) ====================")
    u = "https://mesonet.agron.iastate.edu/api/1/mos.json"
    say(f"endpoint: {u} (anonymous). Printed: HTTP status, row count, projection")
    say("times (ftime, UTC) and whether a 'tmp' column exists. No value is printed.")
    say("Runtimes are chosen so every projection is valid on or before 2026-07-31.")
    runs = [("GFS", "2021-03-24 00:00"), ("GFS", "2021-03-24 12:00"), ("GFS", "2026-07-28 00:00"),
            ("GFS", "2026-07-28 12:00"), ("MEX", "2021-03-24 00:00"), ("MEX", "2026-07-23 00:00"),
            ("NAM", "2026-07-28 00:00"), ("LAV", "2026-07-30 00:00"),
            ("NBS", "2021-03-24 01:00"), ("NBS", "2026-07-28 00:00"), ("NBE", "2026-07-20 00:00")]
    for st in ["KDSM", "KRNO", "KSFO"]:
        for model, rt in runs:
            r = get(u, params={"station": st, "model": model, "runtime": rt + "Z"})
            rows = r.json().get("data", []) if r.status_code == 200 else []
            ft = [x["ftime"][:16] for x in rows]
            if ft and dt.date.fromisoformat(ft[-1][:10]) > LAST_OK:
                raise SystemExit("STOP: a projection is valid after 2026-07-31")
            say(f"  {st} {model} run {rt}Z: HTTP {r.status_code}, {len(rows)} projections, "
                f"tmp column: {bool(rows) and 'tmp' in rows[0]}; ftimes: "
                + (", ".join(x[5:] for x in ft) if st == "KDSM" else f"{ft[:1]}..{ft[-1:]}"))
            rows = None  # values are not kept


# ------------------------------------------------------------------- ICON

def section_icon():
    say("\n==================== 2. DWD ICON global (opendata.dwd.de) ====================")
    base = "https://opendata.dwd.de/weather/nwp/icon/grib/"

    def hrefs(url):
        r = get(url)
        return [h for h in re.findall(r'href="([^"]*)"', r.text) if h != "../"]
    say(f"{base}: {hrefs(base)}")
    v = hrefs(base + "00/")
    want = ["t_2m/", "clct/", "u_10m/", "v_10m/", "td_2m/", "t/", "pmsl/", "ps/",
            "asob_s/", "aswdir_s/", "aswdifd_s/"]
    say(f"00/ variable folders: {len(v)}; SPEC-8-relevant present: "
        f"{ {w: (w in v) for w in want} }")
    for cyc in ["00", "06", "12", "18"]:
        f = hrefs(f"{base}{cyc}/t_2m/")
        runs = sorted({m.group(1) for x in f if (m := re.search(r"_(\d{10})_", x))})
        steps = sorted({int(m.group(1)) for x in f if (m := re.search(r"_\d{10}_(\d{3})_", x))})
        say(f"  {cyc}/t_2m: {len(f)} files, run(s) {runs}, steps {steps[:5]}..{steps[-3:]} "
            f"({len(steps)}); hourly to {max(s for s in steps if s < 100 and all(t in steps for t in range(s + 1)))}")
    f = hrefs(base + "00/t/")
    say(f"  00/t: {len(f)} files; step-024 850 hPa file present: "
        f"{any('_024_850_T' in x for x in f)}; example {f[0] if f else None}")
    f = hrefs(base + "00/aswdir_s/")
    say(f"  00/aswdir_s example names: {f[:2]}")
    say("  not decoded: every file on the server is from the current run (after 2026-07-31).")
    say("third-party archive (listing only): Hugging Face openclimatefix/dwd-icon-global")
    r = get("https://huggingface.co/api/datasets/openclimatefix/dwd-icon-global/tree/main")
    try:
        say(f"  HTTP {r.status_code}: {[x.get('path') for x in r.json()][:20]}")
    except Exception:
        say(f"  HTTP {r.status_code}: {r.text[:200]}")
    r = get("https://huggingface.co/api/datasets/openclimatefix/dwd-icon-global/tree/main/data")
    try:
        say(f"  data/: {[x.get('path') for x in r.json()][:20]}")
    except Exception:
        say(f"  data/: HTTP {r.status_code}")


# -------------------------------------------------------------- Open-Meteo

def section_openmeteo():
    say("\n==================== 8. Open-Meteo Previous Runs API (second route) ====================")
    u = "https://previous-runs-api.open-meteo.com/v1/forecast"
    say(f"endpoint: {u}. Printed: HTTP status, grid metadata, and per-variable")
    say("present/null hour counts. No value is printed. Location: EGLC (SPEC 3.4).")
    base_vars = ["temperature_2m", "cloud_cover", "wind_speed_10m", "dew_point_2m",
                 "pressure_msl", "surface_pressure", "shortwave_radiation"]

    def call(model, vars_, start, end):
        r = get(u, params={"latitude": EGLC[0], "longitude": EGLC[1], "models": model,
                           "hourly": ",".join(vars_), "start_date": start, "end_date": end,
                           "timezone": "GMT"})
        return r

    def counts(j, v):
        a = j.get("hourly", {}).get(v)
        if a is None:
            return None
        return sum(x is not None for x in a), sum(x is None for x in a)

    models = ["gfs_global", "ecmwf_ifs025", "ecmwf_aifs025_single", "icon_global",
              "ncep_gefs025", "gfs025_ensemble", "ncep_hgefs025_ensemble_mean"]
    for model in models:
        vs = [f"{v}_previous_day{n}" for v in base_vars for n in (1, 2)]
        r = call(model, vs, "2025-06-10", "2025-06-12")
        if r.status_code != 200:
            say(f"  {model}: HTTP {r.status_code} {r.text[:160]}")
            continue
        j = r.json()
        say(f"  {model}: grid lat {j.get('latitude')} lon {j.get('longitude')} "
            f"elev {j.get('elevation')}")
        say("     2025-06-10..12 present/null: " + "; ".join(
            f"{v}={counts(j, v)}" for v in vs))
        for pv in ["temperature_850hPa_previous_day1"]:
            r2 = call(model, [pv], "2025-06-10", "2025-06-12")
            say(f"     {pv}: HTTP {r2.status_code} "
                + (str(counts(r2.json(), pv)) if r2.status_code == 200 else r2.text[:200]))

        def has_t2m(d):
            r3 = call(model, ["temperature_2m_previous_day1"], d.isoformat(), d.isoformat())
            if r3.status_code != 200:
                return None
            c = counts(r3.json(), "temperature_2m_previous_day1")
            return bool(c and c[0] > 0)

        def has_cloud(d):
            r3 = call(model, ["cloud_cover_previous_day1"], d.isoformat(), d.isoformat())
            if r3.status_code != 200:
                return None
            c = counts(r3.json(), "cloud_cover_previous_day1")
            return bool(c and c[0] > 0)
        lo = dt.date(2021, 1, 1)
        if has_t2m(lo):
            say(f"     temperature_2m_previous_day1 already present on {lo}")
        else:
            say(f"     temperature_2m_previous_day1 floor (last null day, first present day): "
                f"{bisect(lo, dt.date(2025, 6, 10), has_t2m)}")
        if has_cloud(lo):
            say(f"     cloud_cover_previous_day1 already present on {lo}")
        else:
            say(f"     cloud_cover_previous_day1 floor (last null day, first present day): "
                f"{bisect(lo, dt.date(2025, 6, 10), has_cloud)}")


# -------------------------------------------------------------- GFS v17

def section_v17():
    say("\n==================== 7. GFS v17 retrospective runs ====================")
    say("anonymous S3 listing attempts on candidate bucket names (HTTP code only):")
    for b in ["noaa-nws-gfsv17-retro-pds", "noaa-gfsv17-retro-pds", "noaa-ufs-gfsv17-pds",
              "noaa-gfs-v17-pds", "noaa-nws-gefsv13-reforecast-pds", "noaa-gfs-retro-pds",
              "noaa-ufs-gefsv13replay-pds", "noaa-gefs-retrospective"]:
        r = get(f"https://{b}.s3.amazonaws.com/", params={"list-type": "2", "delimiter": "/",
                                                          "max-keys": "1000"})
        pre = re.findall(r"<CommonPrefixes><Prefix>([^<]*)</Prefix>", r.text)
        code = re.findall(r"<Code>([^<]*)", r.text)
        say(f"  {b}: HTTP {r.status_code} {code} prefixes: {pre[:4]} .. {pre[-6:]}")
    p, _ = s3list("https://noaa-gefs-retrospective.s3.amazonaws.com/", "GEFSv12/reforecast/")
    say(f"  noaa-gefs-retrospective GEFSv12/reforecast/: {p[:2]} .. {p[-2:]}")
    say("  NOMADS para listing (names only):")
    for url in ["https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/para/",
                "https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/v17.0/"]:
        r = get(url)
        say(f"    {url}: HTTP {r.status_code} "
            f"{re.findall(r'href=\"([^\"]*)\"', r.text)[:10] if r.status_code == 200 else ''}")


# ------------------------------------------------------------ WeatherNext

def section_weathernext():
    say("\n==================== 4. Google WeatherNext ====================")
    say("anonymous listing attempt on the documented GCS bucket (no sign-in):")
    for url in ["https://storage.googleapis.com/weathernext?prefix=&delimiter=/",
                "https://storage.googleapis.com/storage/v1/b/weathernext/o?delimiter=/&maxResults=5"]:
        r = get(url)
        say(f"  {url}: HTTP {r.status_code} {re.sub(r'\s+', ' ', r.text)[:200]}")


SECTIONS = {"ecmwf": section_ecmwf, "icon": section_icon, "gefs": section_gefs,
            "weathernext": section_weathernext, "nbm": section_nbm, "mos": section_mos,
            "v17": section_v17, "openmeteo": section_openmeteo}

if __name__ == "__main__":
    want = sys.argv[1:] or list(SECTIONS)
    say(f"session82_source_probe.py run at {dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')} "
        f"UTC; eccodes {eccodes.__version__}; requests {requests.__version__}")
    say(f"temporary sample directory: {TMP}")
    try:
        for s in want:
            SECTIONS[s]()
    finally:
        shutil.rmtree(TMP)
        say(f"\ndecoded messages per source: {MSG_COUNT}")
        say(f"temporary sample directory deleted: {TMP} exists now = {os.path.exists(TMP)}")
