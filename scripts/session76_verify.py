"""Session 76, Step 2: verify San Francisco International (KSFO) on contact.

Network, small samples only. No model is fit and nothing is scored. Every
sample date is before 2024-08-01, outside KSFO's held-out range
(2024-08-01..2026-07-31, DECISIONS D67.6).

What it does (docs/session-76.md, Step 2; F66 is the pattern):
  2.1 pull IEM's CA_ASOS station listing and read San Francisco's entry;
  2.2 check America/Los_Angeles's standard offset in the timezone database;
  2.3 pull a 3-week 2023 observation sample (routine, and routine+special),
      plus 4-day unit (tmpc+tmpf) and timezone (local-time) cross-checks;
  2.4 pull Open-Meteo gfs_global temperature_2m_previous_day1 for
      2021-03-20..2021-03-27 at IEM's position (grid point, archive floor);
  2.5 fetch one HGT:surface message (18z run, f026, run 2024-06-09) and
      compute KSFO's elevation constant the way session37_elevation_fix.py
      does (l.127-162, l.205, l.250-252), with the frozen 7.429 degC/km;
  2.6 report whether a land-mask field was already fetched (no new pull).

Raw files go to data/raw/ (and data/raw/diagnostics/session76/ for the GRIB
sample), each with a .meta.txt (SPEC 2.3). A file that already exists is
never overwritten (SPEC 8.7 item 5): the script stops instead.
"""

import csv
import datetime as dt
import hashlib
import json
import math
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

import eccodes as ec
import requests

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DIAG = RAW / "diagnostics" / "session76"
PARAMS37 = RAW / "diagnostics" / "session37" / "session37_elevation_correction_params.csv"

NETWORK = "CA_ASOS"
LAPSE_C_PER_KM = 7.429          # frozen (SPEC 7.2, D48.3)
TARGET_HOUR_EXPECTED = 20       # D67.1
HELD_OUT_START = dt.date(2024, 8, 1)

OBS_WINDOW = (dt.date(2023, 6, 1), dt.date(2023, 6, 22))    # IEM end date exclusive
PROBE_WINDOW = (dt.date(2023, 6, 1), dt.date(2023, 6, 5))   # 4 days, end exclusive
OM_WINDOW = (dt.date(2021, 3, 20), dt.date(2021, 3, 27))    # Open-Meteo, inclusive
HGT_RUN = dt.date(2024, 6, 9)                                # 18z f026 -> valid 2024-06-10 20:00
HGT_CYCLE, HGT_LEAD = 18, 26

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
UA = {"User-Agent": "MLwx/session76"}
PAUSE_SECONDS = 5


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def save_new(path, data, meta_lines):
    """Write a raw file and its .meta.txt. Refuses to overwrite (SPEC 8.7 item 5)."""
    meta = Path(str(path) + ".meta.txt")
    if path.exists() or meta.exists():
        sys.exit(f"STOP: {path.relative_to(ROOT)} already exists; not overwriting.")
    path.write_bytes(data)
    meta.write_text("Raw pull provenance (SPEC 2.3). Do not edit the data file.\n\n"
                    + "\n".join(meta_lines) + "\n")


def get(url, headers=None):
    """GET with a pause before each request. IEM answers HTTP 429 when asked
    too fast (seen on this session's first run), so a 429 waits and retries,
    up to 5 times. Any other status is returned as is."""
    for attempt in range(6):
        time.sleep(PAUSE_SECONDS if attempt == 0 else 30 * attempt)
        r = requests.get(url, headers={**UA, **(headers or {})}, timeout=120)
        if r.status_code != 429:
            return r
        print(f"  HTTP 429 (too many requests), waiting before retry {attempt + 1}")
    return r


def iem_url(start, end, report_types, fields, tz="UTC", station="SFO"):
    q = [f"station={station}", f"network={NETWORK}"]
    q += [f"data={f}" for f in fields]
    q += [f"year1={start.year}", f"month1={start.month}", f"day1={start.day}",
          f"year2={end.year}", f"month2={end.month}", f"day2={end.day}",
          f"tz={requests.utils.quote(tz, safe='')}", "format=onlycomma", "latlon=yes",
          "elev=yes", "missing=M", "trace=T", "direct=no"]
    q += [f"report_type={t}" for t in report_types]
    return "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?" + "&".join(q)


def pull_iem(station, start, end, report_types, fields, tag, purpose, tz="UTC"):
    assert end <= HELD_OUT_START, "sample must lie outside the held-out range"
    url = iem_url(start, end, report_types, fields, tz=tz, station=station)
    pulled = now_utc()
    r = get(url)
    if r.status_code != 200:
        sys.exit(f"STOP: IEM returned HTTP {r.status_code} for {url}")
    name = f"iem_asos_{station}_{start}_{end}_{tag}.csv"
    save_new(RAW / name, r.content, [
        f"file        : {name}",
        f"purpose     : session 76 - Step 2.3 - {purpose}",
        f"pulled at   : {pulled}",
        "source      : Iowa Environmental Mesonet (IEM) ASOS/METAR download service",
        "tool        : python requests",
        "",
        "exact URL requested:",
        url,
        "",
        "parameters:",
        f"  station     = {station}",
        f"  network     = {NETWORK}",
        f"  data        = {', '.join(fields)}",
        f"  date range  = {start} to {end}. IEM treats its end date as exclusive,",
        f"                so the last row is the day before {end}.",
        f"  tz          = {tz}",
        f"  report_type = {', '.join(report_types)}   (3 = routine METAR, 4 = special)",
        "",
        "notes:",
        "- Outside KSFO's held-out range 2024-08-01..2026-07-31 (DECISIONS D67.6).",
        "- Rows marked M are left exactly as they arrived. Nothing was filled in (SPEC 2.2).",
        f"- HTTP status {r.status_code}.",
    ])
    return RAW / name


def read_obs(path, field="tmpc"):
    rows = []
    with open(path) as f:
        for row in csv.DictReader(f):
            rows.append(row)
    return rows


def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371.0088
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def bilinear_from_gid(gid, lat, lon):
    """Copied from session37_elevation_fix.py l.127-162 (SPEC 8.8 G6),
    returning the four neighbours too so they can be reported."""
    neighbours = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
    lats = sorted(set(round(n.lat, 6) for n in neighbours))
    lons = sorted(set(round(n.lon, 6) for n in neighbours))
    lon_q = lon + 360.0 if lon < 0 else lon
    if len(lats) != 2 or len(lons) != 2:
        lat_span = max(n.lat for n in neighbours) - min(n.lat for n in neighbours)
        lon_span = max(n.lon for n in neighbours) - min(n.lon for n in neighbours)
        if lat_span < 1e-6 or lon_span < 1e-6:
            return min(neighbours, key=lambda n: n.distance).value, neighbours
        raise ValueError(f"unexpected neighbour layout: {[(n.lat, n.lon) for n in neighbours]}")
    lat0, lat1 = lats
    lon0, lon1 = lons
    grid = {(round(n.lat, 6), round(n.lon, 6)): n.value for n in neighbours}
    v00, v01 = grid[(lat0, lon0)], grid[(lat0, lon1)]
    v10, v11 = grid[(lat1, lon0)], grid[(lat1, lon1)]
    dlat = (lat - lat0) / (lat1 - lat0)
    dlon = (lon_q - lon0) / (lon1 - lon0)
    value = ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
             + dlat * (1 - dlon) * v10 + dlat * dlon * v11)
    return value, neighbours


def main():
    DIAG.mkdir(parents=True, exist_ok=True)
    stops = []
    print("=" * 78)
    print("SESSION 76 - Step 2: verify KSFO on contact (network, small samples)")
    print(f"run at {now_utc()}")
    print("=" * 78)

    # ---- 2.1 station listing ------------------------------------------------
    print("\n--- 2.1 IEM CA_ASOS station listing ---")
    url = f"https://mesonet.agron.iastate.edu/geojson/network/{NETWORK}.geojson"
    pulled = now_utc()
    r = get(url)
    if r.status_code != 200:
        sys.exit(f"STOP: HTTP {r.status_code} for {url}")
    name = f"iem_station_metadata_{NETWORK}.geojson"
    save_new(RAW / name, r.content, [
        f"file        : {name}",
        "purpose     : session 76 - Step 2.1 - the authoritative station position for",
        "              San Francisco International (KSFO). Nothing is typed in from",
        "              memory or a map.",
        f"pulled at   : {pulled}",
        "source      : Iowa Environmental Mesonet (IEM) network station listing",
        "tool        : python requests",
        "",
        "exact URL requested:",
        url,
        "",
        "notes:",
        "- The whole network file is kept, as returned (SPEC 2.3).",
        f"- HTTP status {r.status_code}.",
    ])
    gj = json.loads(r.content)
    hits = [f for f in gj["features"]
            if "SAN FRANCISCO" in str(f["properties"].get("sname", "")).upper()
            or f["properties"].get("sid") in ("SFO", "KSFO")]
    print(f"features in listing: {len(gj['features'])}")
    print("entries matching 'SAN FRANCISCO' or sid SFO/KSFO:")
    for f in hits:
        p = f["properties"]
        print(f"  sid={p.get('sid')!r} sname={p.get('sname')!r} network={p.get('network')!r} "
              f"elevation={p.get('elevation')} tzname={p.get('tzname')!r} "
              f"archive_begin={p.get('archive_begin')} coords={f['geometry']['coordinates']}")
    sfo = [f for f in hits if f["properties"].get("sid") == "SFO"]
    if len(sfo) != 1:
        print("STOP: San Francisco International (sid SFO) not found exactly once.")
        sys.exit(1)
    p = sfo[0]["properties"]
    lon_s, lat_s = sfo[0]["geometry"]["coordinates"][:2]
    elev_s = float(p["elevation"])
    print("\nchosen entry (all properties, as returned):")
    for k in sorted(p):
        print(f"  {k}: {p[k]}")
    print(f"\nstation code IEM uses : {p['sid']}")
    print(f"latitude              : {lat_s}")
    print(f"longitude             : {lon_s}")
    print(f"elevation             : {elev_s} m")
    print(f"is the code an ICAO code? {'yes' if len(p['sid']) == 4 else 'no'} "
          f"({p['sid']!r} has {len(p['sid'])} letters; the ICAO code is KSFO)")

    # ---- 2.2 timezone --------------------------------------------------------
    print("\n--- 2.2 target hour from the timezone database ---")
    tzname = p.get("tzname")
    print(f"timezone from IEM metadata : {tzname}")
    tz = ZoneInfo("America/Los_Angeles")
    jan = dt.datetime(2023, 1, 15, 12, tzinfo=dt.timezone.utc).astimezone(tz)
    jul = dt.datetime(2023, 7, 15, 12, tzinfo=dt.timezone.utc).astimezone(tz)
    std = jan.utcoffset().total_seconds() / 3600
    dst = jul.utcoffset().total_seconds() / 3600
    noon_utc = int((12 - std) % 24)
    print(f"mid-winter : 12:00 UTC = {jan:%H:%M} {jan.tzname()} (UTC{std:+.0f})")
    print(f"mid-summer : 12:00 UTC = {jul:%H:%M} {jul.tzname()} (UTC{dst:+.0f})")
    print(f"standard-time offset (read from a January date) : UTC{std:+.0f}")
    print(f"so local standard noon = {noon_utc:02d}:00 UTC; D67.1 expects "
          f"{TARGET_HOUR_EXPECTED:02d}:00 UTC -> "
          f"{'MATCHES' if noon_utc == TARGET_HOUR_EXPECTED and std == -8 else 'DOES NOT MATCH'}")
    if std != -8 or noon_utc != TARGET_HOUR_EXPECTED or tzname != "America/Los_Angeles":
        stops.append("timezone")
    cycle = (TARGET_HOUR_EXPECTED // 6) * 6
    lead = 24 + TARGET_HOUR_EXPECTED % 6
    print(f"cycle floor(20/6)*6 = {cycle:02d}z, lead 24 + 20 mod 6 = {lead} "
          f"(D67.2: lead 26 has a frozen R construction)")

    # ---- 2.3 observations ------------------------------------------------------
    print("\n--- 2.3 observation sample (2023, outside the held-out range) ---")
    code = p["sid"]
    f_rout = pull_iem(code, *OBS_WINDOW, ["3"], ["tmpc", "dwpc"], "routine",
                      "3-week routine sample: reporting minute and completeness")
    f_both = pull_iem(code, *OBS_WINDOW, ["3", "4"], ["tmpc", "dwpc"], "routine-and-special",
                      "the same window with special reports, to see whether a second "
                      "scheduled report exists (SPEC 3.4 'also files at')")
    f_units = pull_iem(code, *PROBE_WINDOW, ["3"], ["tmpc", "tmpf", "dwpc"], "routine-tmpc-tmpf",
                       "units check: tmpc against tmpf (F35's method)")
    f_local = pull_iem(code, *PROBE_WINDOW, ["3"], ["tmpc", "tmpf", "dwpc"], "routine-localtime",
                       "timezone check: the same rows requested in local time (F35's method)",
                       tz="America/Los_Angeles")

    rout = read_obs(f_rout)
    minutes = {}
    for r_ in rout:
        m = int(r_["valid"][14:16])
        minutes[m] = minutes.get(m, 0) + 1
    n_days = (OBS_WINDOW[1] - OBS_WINDOW[0]).days
    print(f"routine sample {OBS_WINDOW[0]}..{OBS_WINDOW[1] - dt.timedelta(days=1)} "
          f"({n_days} days, {n_days * 24} hours): {len(rout)} rows")
    print("routine report minute counts:", dict(sorted(minutes.items(), key=lambda kv: -kv[1])))
    top_min = max(minutes, key=minutes.get)
    print(f"routine minute: :{top_min:02d} ({minutes[top_min]} of {len(rout)} rows, "
          f"{100 * minutes[top_min] / len(rout):.1f}%)")
    n_m = sum(1 for r_ in rout if r_["tmpc"] in ("M", "", "T", "None"))
    print(f"routine rows with no usable tmpc: {n_m}")
    if minutes[top_min] / len(rout) < 0.95:
        stops.append("routine minute unclear")

    both = read_obs(f_both)
    rout_set = {(r_["valid"]) for r_ in rout}
    special = [r_ for r_ in both if r_["valid"] not in rout_set]
    smin = {}
    for r_ in special:
        m = int(r_["valid"][14:16])
        smin[m] = smin.get(m, 0) + 1
    print(f"routine+special rows: {len(both)}; rows not in the routine file: {len(special)}")
    print("special-report minute counts (top 15):",
          dict(sorted(smin.items(), key=lambda kv: -kv[1])[:15]))
    if special:
        top_s = max(smin, key=smin.get)
        print(f"most common special minute: :{top_s:02d} with {smin[top_s]} rows "
              f"over {n_days * 24} hours ({100 * smin[top_s] / (n_days * 24):.1f}% of hours)")

    # pairing offset to 20:00 UTC
    offs = {}
    for r_ in rout:
        t = dt.datetime.strptime(r_["valid"], "%Y-%m-%d %H:%M")
        target = t.replace(minute=0) + (dt.timedelta(hours=1) if t.minute >= 30 else dt.timedelta())
        if target.hour == TARGET_HOUR_EXPECTED:
            off = abs((t - target).total_seconds()) / 60
            offs[off] = offs.get(off, 0) + 1
    print(f"reports assigned to 20:00 UTC, by offset in minutes: {dict(sorted(offs.items()))}")

    units = read_obs(f_units)
    worst = 0.0
    print("units: tmpc against (tmpf-32)*5/9, first 6 rows")
    for i, r_ in enumerate(units):
        if r_["tmpc"] in ("M", "") or r_["tmpf"] in ("M", ""):
            continue
        c, fdeg = float(r_["tmpc"]), float(r_["tmpf"])
        d = c - (fdeg - 32) * 5 / 9
        worst = max(worst, abs(d))
        if i < 6:
            print(f"  {r_['valid']}  tmpc {c:6.2f}  tmpf {fdeg:6.2f}  diff {d:+.4f}")
    print(f"rows: {len(units)}; largest |tmpc - (tmpf-32)*5/9| = {worst:.4f} degC")

    local = read_obs(f_local)
    u_map = {r_["valid"]: r_["tmpf"] for r_ in units}
    print("timezone: slide the local-time series against the UTC series")
    print("  shift (hours)   rows compared   tmpf equal")
    best = None
    for shift in range(-10, 11):
        n = eq = 0
        for r_ in local:
            t = dt.datetime.strptime(r_["valid"], "%Y-%m-%d %H:%M") + dt.timedelta(hours=shift)
            k = t.strftime("%Y-%m-%d %H:%M")
            if k in u_map:
                n += 1
                eq += (u_map[k] == r_["tmpf"])
        if n:
            if best is None or eq / n > best[2]:
                best = (shift, n, eq / n)
            if shift in (0, 6, 7, 8, 9) or eq == n:
                print(f"  {shift:+4d}            {n:5d}          {eq:4d} ({100 * eq / n:.1f}%)")
    print(f"best shift: {best[0]:+d} h ({100 * best[2]:.1f}% equal). Early June is PDT, UTC-7, "
          f"so a +7 h shift at 100% means the tz=UTC request really is UTC.")
    if best[0] != 7 or best[2] < 1.0:
        stops.append("utc check")

    # ---- 2.4 Open-Meteo ------------------------------------------------------
    print("\n--- 2.4 Open-Meteo gfs_global grid point and archive floor ---")
    om_url = ("https://previous-runs-api.open-meteo.com/v1/forecast?"
              f"latitude={lat_s}&longitude={lon_s}&start_date={OM_WINDOW[0]}&end_date={OM_WINDOW[1]}"
              "&hourly=temperature_2m_previous_day1&models=gfs_global&timezone=UTC")
    pulled = now_utc()
    r = get(om_url)
    if r.status_code != 200:
        sys.exit(f"STOP: HTTP {r.status_code} for {om_url}")
    name = f"openmeteo_previousruns_gfs_global_{code}_{OM_WINDOW[0]}_{OM_WINDOW[1]}.json"
    save_new(RAW / name, r.content, [
        f"file        : {name}",
        "purpose     : session 76 - Step 2.4 - KSFO's Open-Meteo grid point and the",
        "              archive floor (F1, F20, F33)",
        f"pulled at   : {pulled}",
        "source      : Open-Meteo Previous Runs API (NOT the Historical Forecast API)",
        "tool        : python requests",
        "",
        "exact URL requested:",
        om_url,
        "",
        "notes:",
        "- temperature_2m_previous_day1 only (SPEC 3.2, 2.1b); model gfs_global (D16).",
        "- The coordinates are IEM's own record for SFO (Step 2.1, same run).",
        "- Nulls are left exactly as the API returned them (SPEC 2.2).",
        f"- HTTP status {r.status_code}.",
    ])
    om = json.loads(r.content)
    g_lat, g_lon, g_elev = om["latitude"], om["longitude"], om["elevation"]
    times, vals = om["hourly"]["time"], om["hourly"]["temperature_2m_previous_day1"]
    nonnull = [t for t, v in zip(times, vals) if v is not None]
    first = nonnull[0] if nonnull else None
    dist = haversine_km(lat_s, lon_s, g_lat, g_lon)
    print(f"returned: latitude {g_lat}, longitude {g_lon}, elevation {g_elev} m, "
          f"utc_offset_seconds {om.get('utc_offset_seconds')}, timezone {om.get('timezone')}")
    print(f"rows {len(vals)}, with a value {len(nonnull)}, null {len(vals) - len(nonnull)}")
    print(f"first non-null hour: {first}")
    print(f"distance station -> grid point: {dist:.2f} km")
    print(f"height mismatch (grid - station): {g_elev - elev_s:+.1f} m")
    floor_ok = first == "2021-03-24T00:00" and all(v is None for t, v in zip(times, vals)
                                                     if t < "2021-03-24T00:00")
    print(f"archive floor 2021-03-24 00:00 UTC, all null before: {'YES' if floor_ok else 'NO'}")
    if not floor_ok:
        stops.append("open-meteo floor")

    # ---- 2.5 GRIB model terrain and the elevation constant --------------------
    print("\n--- 2.5 GRIB model terrain (HGT:surface) and KSFO's elevation constant ---")
    assert HGT_RUN + dt.timedelta(days=1) < HELD_OUT_START
    base = (f"{BUCKET}/gfs.{HGT_RUN:%Y%m%d}/{HGT_CYCLE:02d}/atmos/"
            f"gfs.t{HGT_CYCLE:02d}z.pgrb2.0p25.f{HGT_LEAD:03d}")
    idx_text = get(base + ".idx").text
    lines = idx_text.strip().split("\n")
    start = end = None
    land_lines = []
    for i, line in enumerate(lines):
        parts = line.split(":")
        if len(parts) >= 5 and parts[3] == "HGT" and parts[4] == "surface":
            start = int(parts[1])
            end = int(lines[i + 1].split(":")[1]) - 1 if i + 1 < len(lines) else None
        if len(parts) >= 5 and parts[3] == "LAND":
            land_lines.append(line)
    if start is None:
        sys.exit("STOP: HGT:surface not in idx")
    pulled = now_utc()
    rr = get(base, headers={"Range": f"bytes={start}-{end}"})
    data = rr.content
    if data[:4] != b"GRIB" or data[-4:] != b"7777":
        sys.exit("STOP: HGT message has bad magic markers")
    gname = f"gfs_{HGT_RUN:%Y%m%d}_t{HGT_CYCLE:02d}z_f{HGT_LEAD:03d}_hgt_surface_SFO_diagnostic.grib2"
    save_new(DIAG / gname, data, [
        f"source: {base}",
        f"idx source: {base}.idx",
        f"byte range requested: {start}-{end}",
        f"variable: HGT:surface (model terrain elevation), forecast hour f{HGT_LEAD:03d}, "
        f"cycle {HGT_CYCLE:02d}z, run date {HGT_RUN:%Y%m%d}",
        "purpose: session 76 Step 2.5 - one static-terrain sample for KSFO, to compute its",
        "  elevation constant the way session37_elevation_fix.py does. Run date chosen",
        "  before 2024-08-01 (KSFO's held-out range starts there).",
        f"pulled (UTC): {pulled}",
        f"HTTP status: {rr.status_code}",
        f"bytes saved: {len(data)}",
        f"sha256: {hashlib.sha256(data).hexdigest()}",
        f"first 4 bytes: {data[:4]!r}  last 4 bytes: {data[-4:]!r}",
    ])
    gid = ec.codes_new_from_message(data)
    short = ec.codes_get(gid, "shortName")
    vdate, vtime = ec.codes_get(gid, "validityDate"), ec.codes_get(gid, "validityTime")
    orog, neigh = bilinear_from_gid(gid, g_lat, g_lon)
    ec.codes_release(gid)
    print(f"message: shortName={short} validity={vdate} {vtime:04d} bytes={len(data)}")
    if short != "orog":
        stops.append("hgt shortName")
    print("four surrounding GRIB grid points (lat, lon 0-360, model terrain m, distance km):")
    for n in sorted(neigh, key=lambda n: (n.lat, n.lon)):
        print(f"  {n.lat:9.3f} {n.lon:9.3f} {n.value:9.2f} {n.distance:7.2f}")
    gap = orog - g_elev
    corr = LAPSE_C_PER_KM / 1000.0 * gap
    # The record's own lapse rate is the unrounded RNO fit (l.222-223), stored
    # rounded to 4 dp as 7.429. Recover the unrounded fit from RNO's own row to
    # show whether the choice matters at the stored precision.
    with open(PARAMS37) as f:
        rno = [r_ for r_ in csv.DictReader(f) if r_["station"] == "RNO"][0]
    print(f"orog_interp_m (bilinear to the Open-Meteo grid point {g_lat}, {g_lon}): {orog:.4f}")
    print(f"om_grid_elev_m (Open-Meteo grid elevation, Step 2.4): {g_elev}")
    print(f"gap_m = orog_interp_m - om_grid_elev_m = {gap:.4f}")
    print(f"correction_c = 7.429 / 1000 * gap = {corr!r}  (unrounded)")
    print(f"correction_c stored (round 4, session37_elevation_fix.py l.252) = {round(corr, 4)}")
    print(f"RNO row of the record params file, for reference: {dict(rno)}")
    print(f"SPEC 8.8 G5: RNO's unrounded formula value is 2.04356932; the unrounded "
          f"RNO-fit lapse rate is therefore 2043.56932 / RNO gap.")

    out = DIAG / "session76_elevation_correction_params.csv"
    if out.exists():
        sys.exit(f"STOP: {out.relative_to(ROOT)} already exists; not overwriting.")
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["station", "orog_interp_m", "om_grid_elev_m", "gap_m", "lapse_c_per_km", "correction_c"])
        w.writerow([code, round(orog, 2), g_elev, round(gap, 2), LAPSE_C_PER_KM, round(corr, 4)])
    print(f"wrote {out.relative_to(ROOT)} (same columns and rounding as the session 37 file)")

    # ---- 2.6 land mask ----------------------------------------------------------
    print("\n--- 2.6 land/sea (descriptive, optional) ---")
    print("LAND lines listed in the f026 .idx:", land_lines if land_lines else "none")
    print("Only the HGT:surface message was fetched in 2.5, so no land-mask field is in a")
    print("file already fetched. No new pull was made for this (Step 2.6). Not reported.")

    print("\n--- Step 2 stop checks ---")
    print("stops triggered:", stops if stops else "none")
    return 1 if stops else 0


if __name__ == "__main__":
    sys.exit(main())
