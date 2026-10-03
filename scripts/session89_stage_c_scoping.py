#!/usr/bin/env python3
"""Session 89: the stage C scoping probe. READ ONLY.

It reads from the network and from committed files, prints, and writes no
data file. It chooses nothing (DECISIONS D81.11).

Modes (each is run on its own, so the output can be saved part by part):
  --meta    3.1.1  the dynamical.org GFS forecast archive: metadata
  --docs    3.1.1 and 3.4  documentation pages read (URL, time, key lines)
  --repro   3.1.3  reproduction check against committed GRIB values
  --speed   3.1.4  speed and size of a point time series read
  --grib    3.2    the cost of the GRIB route
  --obs     3.3 and 3.4  hourly observation counts (committed files only)

Hard scope guard (the session prompt):
  * nothing valid after 2026-07-31T23:00 UTC, no init after 2026-07-29T18:00;
  * no score of any forecast against an observation, on any year;
  * observations: counts only, no temperature value is printed;
  * dynamical.org reads: at most 5 GB in total (this script keeps a running
    total of the bytes it estimates from the shard indexes);
  * GRIB trial: at most 500 MB;
  * every download goes into the temporary directory named by S89_TMP.

This script needs xarray, zarr, icechunk, dynamical-catalog, numpy and pandas
(a throwaway virtual environment, not the project's).
"""

import argparse
import asyncio
import csv
import json
import math
import os
import re
import struct
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC_FILE = ROOT / "SPEC.md"
PROCESSED = ROOT / "data" / "processed"
RAW = ROOT / "data" / "raw"

DATASET = "noaa-gfs-forecast"
LAST_INIT = "2026-07-29T18:00"      # latest init this probe may touch
LAST_VALID = "2026-07-31T23:00"     # latest valid time this probe may touch
WINDOW_START = date(2021, 3, 24)
WINDOW_END = date(2026, 7, 31)
DYN_LIMIT_BYTES = 5 * 10 ** 9       # the 5 GB limit, taken as decimal GB
GRIB_LIMIT_BYTES = 500 * 10 ** 6
BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"
UA = "MLwx-session89-probe (read only)"

# Chunk layout from the dataset's own metadata (read again in --meta).
CH_LEAD, CH_LAT, CH_LON = 105, 121, 121
SH_LEAD_CH, SH_LAT_CH, SH_LON_CH = 2, 6, 6     # chunks per shard along each axis
INDEX_BYTES = SH_LEAD_CH * SH_LAT_CH * SH_LON_CH * 16 + 4   # shard index + crc32c


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def say(*a):
    print(*a, flush=True)


def head(title):
    say("")
    say("=" * 78)
    say(f"{title}   [{now()}]")
    say("=" * 78)


# ---------------------------------------------------------------- SPEC 3.4

def cycle_and_lead(target_hour):
    return (target_hour // 6) * 6, 24 + (target_hour % 6)


def load_airports():
    """SPEC 3.4's two tables: station code, target hour, grid point."""
    text = SPEC_FILE.read_text()
    block = text[text.index("**3.4 The airport table.**"):text.index("Notes on the table:")]
    header, t1, t2 = None, {}, {}
    for ln in block.splitlines():
        if not ln.startswith("|"):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        if cells[0] == "station code":
            header = cells
            continue
        if set(cells[0]) <= set("-") or header is None:
            continue
        row = dict(zip(header, cells))
        (t1 if "target hour (UTC)" in header else t2)[cells[0]] = row
    out = {}
    for st in t1:
        hour = int(t1[st]["target hour (UTC)"].split(":")[0])
        cyc, lead = cycle_and_lead(hour)
        out[st] = {"station": st, "target_hour": hour, "cycle": cyc, "lead": lead,
                   "grid_lat": float(t2[st]["grid latitude"]),
                   "grid_lon": float(t2[st]["grid longitude"]),
                   "latitude": float(t1[st]["latitude"]),
                   "longitude": float(t1[st]["longitude"]),
                   "reports_at": t2[st]["reports at"]}
    if list(out) != ["EGLC", "LFPG", "DSM", "YSDU", "RNO", "SFO"]:
        raise SystemExit(f"STOP: unexpected airport set {list(out)}")
    # The session prompt's own list of cycle and lead (checked, not assumed).
    expect = {"EGLC": (12, 24), "LFPG": (12, 24), "DSM": (18, 24),
              "YSDU": (0, 26), "RNO": (18, 26), "SFO": (18, 26)}
    for st, (c, l) in expect.items():
        if (out[st]["cycle"], out[st]["lead"]) != (c, l):
            raise SystemExit(f"STOP: {st} cycle/lead differ from the prompt's list")
    return out


# ------------------------------------------------------------ the archive

class BudgetExceeded(Exception):
    pass


class Archive:
    """Read-only handle on the dynamical.org GFS forecast archive, with a
    running estimate of the bytes read (from the shard indexes: the library
    does not report bytes)."""

    def __init__(self):
        import numpy as np
        import xarray as xr
        import zarr
        import dynamical_catalog as dc
        from zarr.abc.store import SuffixByteRequest
        from zarr.core.buffer import default_buffer_prototype
        self.np, self.xr, self.zarr, self.dc = np, xr, zarr, dc
        self._suffix = SuffixByteRequest
        self._proto = default_buffer_prototype
        self.store = dc.get_store(DATASET)
        self.ds = xr.open_zarr(self.store, consolidated=False, chunks=None)
        self.init = self.ds.init_time.values
        self.lat = self.ds.latitude.values
        self.lon = self.ds.longitude.values
        self.lead_h = (self.ds.lead_time.values / np.timedelta64(1, "h")).astype(int)
        self._index = {}
        self.bytes = 0          # estimated compressed chunk bytes read
        self.index_bytes = 0    # shard-index bytes read
        self.chunk_reads = 0
        self.index_reads = 0
        self.errors = 0
        assert self.lead_h[24] == 24 and self.lead_h[53] == 53 and self.lead_h[120] == 120

    def init_index(self, ts):
        np = self.np
        t = np.datetime64(ts)
        pos = int(np.searchsorted(self.init, t))
        if pos < len(self.init) and self.init[pos] == t:
            return pos
        return None

    def nodes(self, lat, lon):
        """Indexes of the 2 x 2 box round (lat, lon): north, south, west, east."""
        ia = int(math.floor((90.0 - lat) / 0.25))
        ja = int(math.floor((lon + 180.0) / 0.25))
        ib, jb = ia + 1, ja + 1
        assert self.lat[ia] >= lat >= self.lat[ib] and self.lon[ja] <= lon <= self.lon[jb]
        return ia, ib, ja, jb

    def _shard_index(self, var, i, c_lead, c_lat, c_lon):
        key = f"{var}/c/{i}/{c_lead // SH_LEAD_CH}/{c_lat // SH_LAT_CH}/{c_lon // SH_LON_CH}"
        if key in self._index:
            return self._index[key]
        last = None
        for attempt in range(3):
            try:
                buf = asyncio.run(self.store.get(key, self._proto(), byte_range=self._suffix(INDEX_BYTES)))
                break
            except Exception as e:   # network error: retry
                last = e
                time.sleep(2 * (attempt + 1))
        else:
            raise last
        if buf is None:
            self._index[key] = None
            return None
        raw = buf.to_bytes()
        arr = self.np.frombuffer(raw[:-4], dtype="<u8").reshape(-1, 2)
        self._index[key] = arr
        self.index_reads += 1
        self.index_bytes += len(raw)
        return arr

    def chunk_bytes(self, var, i, lead_idx, lat_idx, lon_idx, count=True):
        """Compressed bytes of the inner chunks a read touches (the shard
        index gives each one's size). The 'empty chunk' marker is 2**64-1."""
        touched = {(l // CH_LEAD, a // CH_LAT, o // CH_LON)
                   for l in lead_idx for a in lat_idx for o in lon_idx}
        total = 0
        for (cl, ca, co) in touched:
            arr = self._shard_index(var, i, cl, ca, co)
            if arr is None:
                continue
            flat = ((cl % SH_LEAD_CH) * SH_LAT_CH + (ca % SH_LAT_CH)) * SH_LON_CH + (co % SH_LON_CH)
            nb = int(arr[flat, 1])
            if nb != 2 ** 64 - 1:
                total += nb
        if count:
            self.bytes += total
            self.chunk_reads += len(touched)
        return total

    def read(self, var, i, leads, ia, ib, ja, jb):
        """Values at the 2 x 2 box for the given lead hours: (lead, 2, 2)."""
        if self.bytes + self.index_bytes > DYN_LIMIT_BYTES:
            raise BudgetExceeded("the byte budget for dynamical.org reads would be exceeded")
        lead_idx = [int(h) for h in leads]
        self.chunk_bytes(var, i, lead_idx, [ia, ib], [ja, jb])
        last = None
        for attempt in range(3):
            try:
                a = self.ds[var].isel(init_time=i, lead_time=lead_idx,
                                      latitude=[ia, ib], longitude=[ja, jb]).values
                return a.astype("float64")
            except Exception as e:
                last = e
                self.errors += 1
                time.sleep(2 * (attempt + 1))
        raise last

    def bilinear(self, box, lat, lon):
        """The record's bilinear rule (SPEC 8.8 G6): weights from the
        fractional position along latitude and along longitude, longitudes
        shifted by +360 where negative. box is (2 north/south, 2 west/east)."""
        ia, ib, ja, jb = box["idx"]
        lat1, lat0 = float(self.lat[ia]), float(self.lat[ib])       # north, south
        lon0, lon1 = float(self.lon[ja]), float(self.lon[jb])       # west, east
        q = lon + 360.0 if lon < 0 else lon
        lon0 = lon0 + 360.0 if lon0 < 0 else lon0
        lon1 = lon1 + 360.0 if lon1 < 0 else lon1
        dlat = (lat - lat0) / (lat1 - lat0)
        dlon = (q - lon0) / (lon1 - lon0)
        v = box["vals"]            # (north/south, west/east) = (ia,ib) x (ja,jb)
        v10, v11 = v[0, 0], v[0, 1]     # north row: lat1
        v00, v01 = v[1, 0], v[1, 1]     # south row: lat0
        return ((1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01
                + dlat * (1 - dlon) * v10 + dlat * dlon * v11)


# ------------------------------------------------------------- 3.1.1 meta

def mode_meta():
    import numpy as np
    import dynamical_catalog as dc
    head("3.1.1 dynamical.org GFS forecast archive: metadata")
    say("Access time (UTC):", now(), "| route: dynamical-catalog (icechunk, anonymous) | tag: verified")
    say("dynamical-catalog", dc.__version__)
    cat = dc.load_catalog()
    for k in ("noaa-gfs-forecast", "noaa-gfs-forecast-virtual"):
        say(f"catalog entry {k}:", json.dumps(cat[k]))
    say("The 'virtual' dataset holds byte-range references into NOAA's own bucket "
        "(s3://noaa-gfs-bdp-pds/). It is listed here and NOT read in this session.")
    a = Archive()
    ds = a.ds
    say("")
    say("dataset attributes (tag: verified, from the dataset's own metadata):")
    for k, v in ds.attrs.items():
        say(f"  {k} = {v}")
    say("dims:", dict(ds.sizes))
    say("grid: latitude", float(a.lat[0]), "to", float(a.lat[-1]), "step", float(a.lat[0] - a.lat[1]),
        "(north to south) | longitude", float(a.lon[0]), "to", float(a.lon[-1]),
        "step", float(a.lon[1] - a.lon[0]), "(-180..179.75; the record's GRIB uses 0..359.75, same nodes)")
    first = a.ds["temperature_2m"]
    say("chunks", first.encoding.get("chunks"), "shards", first.encoding.get("shards"),
        "(init_time, lead_time, latitude, longitude); compressor",
        str(first.encoding.get("compressors"))[:130])
    say("inner chunk = 1 init x 105 leads x 121 x 121 cells (30.25 deg x 30.25 deg), 5.9 MiB uncompressed")

    say("")
    say("--- init times (axis labels only; no forecast value is read here) ---")
    init = a.init
    say("first init:", str(init[0]), "| last init in the archive (axis label):", str(init[-1]),
        "| total inits on the axis:", len(init))
    lim = np.datetime64(LAST_INIT)
    exp = np.arange(np.datetime64("2021-05-01T00:00"), lim + np.timedelta64(6, "h"), np.timedelta64(6, "h"))
    present = np.isin(exp, init)
    missing = exp[~present]
    say(f"expected inits every 6 h, 2021-05-01T00 to {LAST_INIT}: {len(exp)}; on the axis: {int(present.sum())}; "
        f"missing from the axis: {len(missing)}")
    if len(missing) < 50:
        say("  missing:", [str(m)[:16] for m in missing])
    per_day = {}
    for t in init[init <= lim]:
        per_day[str(t)[:10]] = per_day.get(str(t)[:10], 0) + 1
    say("inits per day (2021-05-01 on):", {n: sum(1 for v in per_day.values() if v == n) for n in sorted(set(per_day.values()))},
        "(count of days with that many inits)")
    span = np.diff(init[init <= lim]).astype("timedelta64[h]").astype(int)
    say("steps between consecutive inits (hours): counts", {int(s): int((span == s).sum()) for s in sorted(set(span))})
    inb = init <= lim
    ing_all = ds.ingested_forecast_length.values[inb]
    exp_all = ds.expected_forecast_length.values[inb]
    n_nat = int(np.isnat(ing_all).sum())
    say(f"ingested_forecast_length: NaT (empty) for {n_nat} of {len(ing_all)} inits up to the limit, so this "
        "coordinate cannot show per-init completeness here; per-init completeness is taken from the validation "
        "report instead (--docs).")
    exp_h = (exp_all / np.timedelta64(1, "h")).astype(float)
    say("expected_forecast_length (hours): distinct values", {float(v): int((exp_h == v).sum()) for v in sorted(set(exp_h))})
    if n_nat < len(ing_all):
        ing_h = (ing_all / np.timedelta64(1, "h")).astype(float)
        say("ingested_forecast_length (hours), non-NaT: distinct values",
            {float(v): int((ing_h == v).sum()) for v in sorted(set(ing_h[~np.isnan(ing_h)]))})
    say("record coverage: the archive's first init is", str(init[0]),
        "| the record's first target day is", WINDOW_START, "(init the day before). Target days whose init "
        "would fall before the archive's first init cannot be read from it:")
    # first target day an airport can have: init D-1 at its cycle >= first init
    for st, ap in load_airports().items():
        d = WINDOW_START
        while True:
            t = np.datetime64(f"{d - timedelta(days=1)}T{ap['cycle']:02d}:00")
            if t >= init[0]:
                break
            d += timedelta(days=1)
        say(f"  {st}: first target day with an init in the archive: {d}; target days from {WINDOW_START} "
            f"before it: {(d - WINDOW_START).days}")

    say("")
    say("--- lead times ---")
    lh = a.lead_h
    say("lead steps (hours): first 5", lh[:5].tolist(), "... around 120:", lh[119:125].tolist(),
        "... last", lh[-3:].tolist(), "| count", len(lh))
    say("step sizes: hourly 0..120 (count of 1 h steps)", int((np.diff(lh[lh <= 120]) == 1).sum()),
        "| beyond 120 h:", sorted(set(np.diff(lh[lh >= 120]).tolist())), "h")
    have = [h for h in range(24, 54) if h in set(lh.tolist())]
    say("every hour from 24 h to 53 h present on the lead axis:", len(have) == 30, f"({len(have)} of 30)")
    say("the lead-24 and lead-48..53 values sit in lead chunk 0 (indexes 0..104), the same chunk as every hour "
        "from 0 to 104")

    say("")
    say("--- variables (25), with the dataset's own attributes ---")
    for name, v in ds.data_vars.items():
        at = v.attrs
        say(f"{name}: units={at.get('units')} step_type={at.get('step_type')} short_name={at.get('short_name')}")
        if at.get("comment"):
            say(f"    comment: {at['comment']}")
    say("level for each variable is in its name (2m, 10m, surface, atmosphere, mean sea level, ...). "
        "There is NO pressure-level variable (no 850 hPa temperature) and NO 2 m dew point in the 25.")
    say("variable names:", sorted(ds.data_vars))
    say("")
    say("Probe finished. Nothing was read except metadata and axis labels.")


# ------------------------------------------------------------- docs (3.1.1, 3.4)

def fetch_text(url, maxbytes=3_000_000):
    t0 = time.time()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            body = r.read(maxbytes)
            return r.status, body, time.time() - t0, r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        return e.code, b"", time.time() - t0, ""
    except Exception as e:
        return 0, str(e).encode(), time.time() - t0, ""


def plain(html_bytes):
    import html
    t = html_bytes.decode("utf-8", errors="ignore")
    t = re.sub(r"(?s)<script.*?</script>|<style.*?</style>", "", t)
    t = html.unescape(re.sub(r"<[^>]+>", " ", t))
    return re.sub(r"\s+", " ", t)


def show(url, tag, pattern=None, width=330, limit=6, as_json=False):
    st, body, dt, ctype = fetch_text(url)
    say(f"URL: {url}\n  accessed {now()} | HTTP {st} | {len(body)} bytes | {dt:.1f}s | tag: {tag}")
    if st != 200:
        say("  not read:", body[:120])
        return None
    text = body.decode("utf-8", errors="ignore") if as_json else plain(body)
    if pattern:
        n = 0
        for m in re.finditer(pattern, text):
            s, e = max(0, m.start() - 100), min(len(text), m.end() + width)
            say("  ...", text[s:e])
            n += 1
            if n >= limit:
                break
        if n == 0:
            say("  no line matched", pattern)
    return text


def mode_docs():
    head("Documentation pages read (3.1.1 and 3.4). Pages only: no data is requested.")
    say("--- 3.1.1: dynamical.org ---")
    t = show("https://stac.dynamical.org/noaa-gfs-forecast/collection.json", "documentation only", as_json=True)
    if t:
        d = json.loads(t)
        say("  version:", d.get("version"), "| license:", d.get("license"))
        det = d.get("description_details", "")
        i = det.find("### Compression")
        say("  Compression paragraph:", re.sub(r"\s+", " ", det[i:i + 480]))
        i = det.find("### Source")
        say("  Source paragraph:", re.sub(r"\s+", " ", det[i:i + 420]))
    t = show("https://dynamical.org/catalog/noaa-gfs-forecast/validation/", "documentation only",
             pattern=r"Report generation start time|Review notes", width=1500, limit=2)
    if t:
        say("  availability rows (complete positions, incomplete %, first and last incomplete init) for the "
            "variables this probe uses:")
        for v in ("temperature_2m", "wind_u_10m", "wind_v_10m", "relative_humidity_2m",
                  "pressure_reduced_to_mean_sea_level", "downward_short_wave_radiation_flux_surface",
                  "total_cloud_cover_atmosphere", "maximum_temperature_2m", "minimum_temperature_2m"):
            m = re.search(re.escape(v) + r" (\d+/\d+ [\d.]+% \S+ \S+)", t)
            say(f"    {v}: {m.group(1) if m else 'not found'}")
    t2 = show("https://dynamical.org/updates/", "documentation only", pattern=r"GFS", width=260, limit=4)
    say("")
    say("Storage rounding (reformatters source, GitHub; documentation only):")
    st, body, dt, _ = fetch_text("https://raw.githubusercontent.com/dynamical-org/reformatters/main/"
                                 "src/reformatters/noaa/gfs/template_config.py")
    say(f"URL: https://raw.githubusercontent.com/dynamical-org/reformatters/main/src/reformatters/noaa/gfs/"
        f"template_config.py\n  accessed {now()} | HTTP {st} | {len(body)} bytes")
    if st == 200:
        src = body.decode()
        dflt = re.search(r"default_keep_mantissa_bits\s*=\s*(\d+)", src)
        say("  default_keep_mantissa_bits =", dflt.group(1) if dflt else "?")
        for blk in re.split(r"\n\s*NoaaDataVar\(", src)[1:]:
            n = re.search(r'name="([^"]+)"', blk)
            k = re.search(r"keep_mantissa_bits=([A-Za-z_0-9]+)", blk)
            s = re.search(r'step_type="([^"]+)"', blk)
            e = re.search(r'grib_element="([^"]+)"', blk)
            lv = re.search(r'grib_index_level="([^"]+)"', blk)
            kk = k.group(1) if k else "(not stated)"
            if kk == "default_keep_mantissa_bits" and dflt:
                kk = dflt.group(1)
            say(f"  {n.group(1) if n else '?':45s} mantissa bits kept={kk:12s} step={s.group(1) if s else '?':8s} "
                f"GRIB element={e.group(1) if e else '?':8s} level={lv.group(1) if lv else '?'}")
        say("  What the bits mean (arithmetic, not from the page): with m mantissa bits, a value in [2^e, 2^(e+1)) "
            "is stored on a grid of spacing 2^e / 2^m. At 7 bits, 2 m temperature 16..32 C is stored at 0.125 C and "
            "8..16 C at 0.0625 C; PRMSL at about 101,300 Pa with 10 bits is stored at 64 Pa (0.64 hPa); "
            "DSWRF 512..1024 W/m2 with 7 bits at 4 W/m2; 10 m wind 8..16 m/s with 6 bits at 0.125 m/s.")

    say("")
    head("3.4 daily-maximum sources: documentation read")
    say("1) METAR max-temperature groups")
    show("https://en.wikipedia.org/wiki/METAR", "secondary (Wikipedia)",
         pattern=r"6-hour maximum temperature", width=420, limit=1)
    show("https://mesonet.agron.iastate.edu/request/download.phtml", "documentation only (IEM)",
         pattern=r"Ice Accretion 1 Hour", width=520, limit=1)
    say("2) SYNOP maximum temperature (Tx)")
    show("https://en.wikipedia.org/wiki/SYNOP", "secondary (Wikipedia)",
         pattern=r"Maximum temperature over the past day", width=240, limit=1)
    say("3) Official daily climate products (NWS CLI; non-US national services)")
    say("   The NWS directive (https://www.weather.gov/media/directives/010_pdfs/pd01010004curr.pdf) returned a PDF; "
        "no PDF text tool is installed and none may be installed here, so its day-window wording was NOT read: unknown.")
    say("   No page was read for Meteo-France, the UK Met Office, or the Bureau of Meteorology daily climate "
        "maxima: unknown. They are named in F131 as items for the owner, not as findings.")
    show("https://mesonet.agron.iastate.edu/info/datasets/cli.html", "documentation only (IEM)",
         pattern=r"(?i)climate (day|report)|local standard|midnight", width=300, limit=3)


# ------------------------------------------------------ committed values

def load_committed():
    """The committed GRIB-derived values, one dict per (station, date)."""
    import pandas as pd
    fams = [
        (["grib_features_v16_window", "grib_features_sealed_window"], ["wind_speed_grib_kmh"]),
        (["session49_v16_window_with_upper_air", "session49_sealed_window_with_upper_air",
          "session63_reserved_window_with_upper_air"], ["t2m_raw"]),
        (["session51_v16_window_with_moisture", "session51_sealed_window_with_moisture",
          "session63_reserved_window_with_moisture"], ["relative_humidity_2m"]),
        (["session53_v16_window_with_pressure", "session53_sealed_window_with_pressure",
          "session63_reserved_window_with_pressure"],
         ["pressure_msl_hpa", "pressure_msl_lead_minus3_hpa", "pressure_tendency_3h_hpa"]),
        (["session55_v16_window_with_radiation", "session55_sealed_window_with_radiation",
          "session63_reserved_window_with_radiation"],
         ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"]),
    ]
    out = {}
    leads = {}
    for names, cols in fams:
        for nm in names:
            d = pd.read_csv(PROCESSED / f"{nm}.csv")
            for st, lead in d.groupby("station")["lead"].unique().items():
                leads.setdefault(st, set()).update(int(x) for x in lead)
            for r in d[["station", "target_date"] + cols].itertuples(index=False):
                rec = out.setdefault((r[0], r[1]), {})
                for c, v in zip(cols, r[2:]):
                    rec[c] = float(v)
    k = pd.read_csv(PROCESSED / "session76_ksfo_features.csv")
    cols = ["t2m_raw", "wind_speed_grib_kmh", "relative_humidity_2m", "pressure_msl_hpa",
            "pressure_msl_lead_minus3_hpa", "pressure_tendency_3h_hpa", "dswrf_ave_to_lead_wm2",
            "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"]
    for st, lead in k.groupby("station")["lead"].unique().items():
        leads.setdefault(st, set()).update(int(x) for x in lead)
    for r in k[["station", "target_date"] + cols].itertuples(index=False):
        rec = out.setdefault((r[0], r[1]), {})
        for c, v in zip(cols, r[2:]):
            rec[c] = float(v)
    return out, leads


# (name, committed column, same definition?, note)
REPRO_FIELDS = [
    ("t2m", "t2m_raw", "2 m temperature, C, before the elevation constant"),
    ("wind_kmh", "wind_speed_grib_kmh", "10 m wind speed from u and v, km/h"),
    ("rh2m", "relative_humidity_2m", "2 m relative humidity, % (extra row: the recipe uses dew point, absent)"),
    ("msl_hpa", "pressure_msl_hpa", "PRMSL at the lead, hPa"),
    ("msl_m3_hpa", "pressure_msl_lead_minus3_hpa", "PRMSL at the lead minus 3 h, hPa"),
    ("tend", "pressure_tendency_3h_hpa", "3 h pressure tendency, hPa"),
    ("dswrf_lead", "dswrf_ave_to_lead_wm2", "DSWRF average to the lead (record: native window), W/m2"),
    ("dswrf_m2", "dswrf_ave_to_lead_minus2_wm2", "DSWRF average to lead minus 2 h (lead-24 airports only)"),
    ("dswrf_2h", "dswrf_2h_wm2", "DSWRF 2 h window ending at the target hour, W/m2"),
]


def first_of_month_dates():
    d, out = date(2021, 5, 1), []
    while d <= date(2026, 7, 1):
        out.append(d)
        d = date(d.year + (d.month == 12), d.month % 12 + 1, 1)
    return out


def mode_repro(budget_gb, limit_dates=0, date_step=1):
    import numpy as np
    head("3.1.3 Reproduction check (spent years only). Differences between two copies of the same GFS forecast.")
    airports = load_airports()
    committed, leads_seen = load_committed()
    say("committed values loaded:", len(committed), "station-days")
    say("leads present in the committed GRIB files, per station:", {k: sorted(v) for k, v in sorted(leads_seen.items())})
    a = Archive()
    dates = first_of_month_dates()
    if limit_dates:
        dates = dates[1:1 + limit_dates]      # trial run only
    if date_step > 1:
        dates = dates[1::date_step]           # every Nth monthly date (byte budget)
    say(f"dates per airport: the 1st of every month, {dates[0]} .. {dates[-1]} ({len(dates)} dates); "
        f"(step {date_step}; 2021-05-01 would need an init before the archive's first init)")
    global DYN_LIMIT_BYTES
    DYN_LIMIT_BYTES = int(budget_gb * 10 ** 9)
    say(f"byte budget for this part: {budget_gb} GB (of the 5 GB total)")
    var_of = {"t2m": "temperature_2m", "u": "wind_u_10m", "v": "wind_v_10m", "rh": "relative_humidity_2m",
              "prmsl": "pressure_reduced_to_mean_sea_level", "dswrf": "downward_short_wave_radiation_flux_surface"}
    results = {}      # (station, field) -> dict
    t_start = time.time()
    meta = {}
    for st, ap in airports.items():
        L = ap["lead"]
        meta[st] = {"box": a.nodes(ap["grid_lat"], ap["grid_lon"]), "deacc": L == 24}
        ia, ib, ja, jb = meta[st]["box"]
        say(f"{st}: cycle {ap['cycle']:02d}z lead {L} h, grid point {ap['grid_lat']}, {ap['grid_lon']}; "
            f"archive nodes lat {a.lat[ia]}/{a.lat[ib]}, lon {a.lon[ja]}/{a.lon[jb]}")
        for f, col, _ in REPRO_FIELDS:
            if f == "dswrf_m2" and not meta[st]["deacc"]:
                continue
            results[(st, f)] = {"diff": [], "miss_arch": 0, "miss_comm": 0, "exact": 0, "rows": 0}
    stopped = None
    done_dates = 0
    for d in dates:
        for st, ap in airports.items():
            L, cyc = ap["lead"], ap["cycle"]
            box_idx = meta[st]["box"]
            ia, ib, ja, jb = box_idx
            deacc = meta[st]["deacc"]
            init_ts = f"{d - timedelta(days=1)}T{cyc:02d}:00"
            valid = np.datetime64(init_ts) + np.timedelta64(L, "h")
            assert np.datetime64(init_ts) <= np.datetime64(LAST_INIT) and valid <= np.datetime64(LAST_VALID)
            i = a.init_index(init_ts)
            comm = committed.get((st, d.isoformat()))
            vals = {}
            if i is not None:
                def pt(var, hrs):
                    arr = a.read(var_of[var], i, hrs, ia, ib, ja, jb)      # (lead, 2, 2)
                    return [a.bilinear({"idx": box_idx, "vals": arr[k]}, ap["grid_lat"], ap["grid_lon"])
                            for k in range(len(hrs))]
                try:
                    t2 = pt("t2m", [L])[0]
                    u = pt("u", [L])[0]
                    v = pt("v", [L])[0]
                    rh = pt("rh", [L])[0]
                    pm3, pm = pt("prmsl", [L - 3, L])
                    if deacc:
                        d22, d24 = pt("dswrf", [L - 2, L])
                    else:
                        d26 = pt("dswrf", [L])[0]
                except BudgetExceeded as e:
                    stopped = f"{e}; stopped before {st} {d}"
                    break
                vals["t2m"] = t2
                vals["wind_kmh"] = math.sqrt(u * u + v * v) * 3.6
                vals["rh2m"] = rh
                vals["msl_hpa"] = pm / 100.0
                vals["msl_m3_hpa"] = pm3 / 100.0
                vals["tend"] = (pm - pm3) / 100.0
                if deacc:
                    vals["dswrf_lead"] = d24
                    vals["dswrf_m2"] = d22
                    vals["dswrf_2h"] = (6.0 * d24 - 4.0 * d22) / 2.0
                else:
                    vals["dswrf_lead"] = d26
                    vals["dswrf_2h"] = d26
            for f, col, _ in REPRO_FIELDS:
                if (st, f) not in results:
                    continue
                r = results[(st, f)]
                av = vals.get(f)
                cv = None if comm is None else comm.get(col)
                if cv is not None and not math.isfinite(cv):
                    cv = None
                if av is None or not math.isfinite(av):
                    r["miss_arch"] += 1
                    continue
                if cv is None:
                    r["miss_comm"] += 1
                    continue
                r["rows"] += 1
                r["diff"].append(abs(av - cv))
                if abs(round(av, 3) - cv) < 1e-9:
                    r["exact"] += 1
        if stopped:
            break
        done_dates += 1
        if done_dates % 3 == 0 or done_dates == len(dates):
            say(f"  dates done {done_dates}/{len(dates)} ({d}): {time.time() - t_start:.0f} s, chunk reads {a.chunk_reads}, "
                f"estimated bytes {a.bytes / 1e6:.0f} MB (+{a.index_bytes / 1e6:.1f} MB indexes), errors {a.errors}")
    if stopped:
        say("STOPPED EARLY:", stopped, f"| dates completed for all airports: {done_dates} of {len(dates)}")
    say("")
    say("--- Reproduction table (|archive - committed|, archive formed as the record forms its value, "
        "no elevation correction; report only, no pass or fail) ---")
    say(f"{'airport':6s} {'field':11s} {'rows':>5s} {'miss_arch':>9s} {'miss_comm':>9s} {'mean_abs':>10s} "
        f"{'max_abs':>10s} {'exact_3dp':>9s}   committed column")
    cols = {f: c for f, c, _ in REPRO_FIELDS}
    for (st, f), r in results.items():
        dd = np.array(r["diff"])
        mean = f"{dd.mean():.4f}" if len(dd) else "n/a"
        mx = f"{dd.max():.4f}" if len(dd) else "n/a"
        say(f"{st:6s} {f:11s} {r['rows']:5d} {r['miss_arch']:9d} {r['miss_comm']:9d} {mean:>10s} {mx:>10s} "
            f"{r['exact']:9d}   {cols[f]}")
    say("")
    say("Fields NOT compared, with the reason (3.1.2): total cloud cover (the archive's is a 1-6 hour average, the "
        "record's is the instantaneous field: different definition); 2 m dew point and 850 hPa temperature (absent "
        "from the archive).")
    say("Second cycle and lead (2 m temperature, leads 48 to 53 h): committed GRIB values exist only at each "
        "airport's one cycle and lead (the leads present are printed above, one per airport). So there is nothing "
        "committed to compare at another cycle or lead: skipped, as the prompt directs.")
    say(f"Totals: chunk reads {a.chunk_reads}; shard-index reads {a.index_reads}; estimated chunk bytes "
        f"{a.bytes / 1e9:.3f} GB; shard-index bytes {a.index_bytes / 1e6:.2f} MB; read errors retried {a.errors}; "
        f"wall time {time.time() - t_start:.0f} s")
    say("BYTES_USED_REPRO", a.bytes + a.index_bytes)


# ------------------------------------------------------------ 3.1.4 speed

def mode_speed(stride, spent_gb):
    import numpy as np
    head("3.1.4 Speed and size: a point time series of 2 m temperature at one airport")
    airports = load_airports()
    ap = airports["EGLC"]
    a = Archive()
    ia, ib, ja, jb = a.nodes(ap["grid_lat"], ap["grid_lon"])
    lim = np.datetime64(LAST_INIT)
    inits_all = np.where(a.init <= lim)[0]
    n_all = len(inits_all)
    say(f"airport EGLC, grid point {ap['grid_lat']}, {ap['grid_lon']}; archive nodes {a.lat[ia]}/{a.lat[ib]}, "
        f"{a.lon[ja]}/{a.lon[jb]}")
    say(f"inits from {a.init[inits_all[0]]} to {a.init[inits_all[-1]]} (<= {LAST_INIT}): {n_all}; "
        f"leads 24..53 h (30 leads); 4 surrounding grid points")
    global DYN_LIMIT_BYTES
    DYN_LIMIT_BYTES = int((5.0 - spent_gb) * 10 ** 9)
    say(f"byte budget for this part: {(5.0 - spent_gb):.2f} GB (5 GB minus {spent_gb:.2f} GB already used)")
    # a full read would be n_all chunk reads of about the compressed chunk size: size it from the shard
    # indexes of a spread sample first (cheap), then read a strided subset.
    pick = inits_all[::stride]
    say(f"strided read: every {stride}th init: {len(pick)} inits (the full read would be {n_all})")
    sizes = []
    for i in inits_all[:: max(1, n_all // 60)]:
        sizes.append(a.chunk_bytes("temperature_2m", int(i), [24], [ia, ib], [ja, jb], count=False))
    sizes = np.array(sizes, dtype=float)
    say(f"compressed size of the chunk this read touches, {len(sizes)} inits spread over the archive: "
        f"mean {sizes.mean() / 1e6:.3f} MB, min {sizes.min() / 1e6:.3f}, max {sizes.max() / 1e6:.3f}")
    est_full_bytes = sizes.mean() * n_all
    say(f"=> the full read (every init, one chunk each) would be about {est_full_bytes / 1e9:.1f} GB of compressed "
        f"chunks: {'ABOVE' if est_full_bytes > DYN_LIMIT_BYTES else 'within'} this part's budget")
    a.bytes = 0
    a.chunk_reads = 0
    leads = list(range(24, 54))
    rows = 0
    t0 = time.time()
    for n, i in enumerate(pick):
        arr = a.read("temperature_2m", int(i), leads, ia, ib, ja, jb)
        rows += arr.size
        if (n + 1) % 100 == 0:
            say(f"  {n + 1}/{len(pick)} inits, {time.time() - t0:.0f} s, {a.bytes / 1e6:.0f} MB")
    wall = time.time() - t0
    say("")
    say(f"strided read done: {len(pick)} inits, {rows} values (inits x 30 leads x 4 points), wall time {wall:.1f} s "
        f"({wall / len(pick):.3f} s per init), estimated bytes {a.bytes / 1e6:.0f} MB from the shard indexes "
        f"(the library does not report bytes), chunk reads {a.chunk_reads}, errors retried {a.errors}")
    scale = n_all / len(pick)
    say(f"extrapolation to the full read of this one series (x{scale:.2f}): wall time about {wall * scale / 60:.1f} min, "
        f"bytes about {a.bytes * scale / 1e9:.1f} GB, rows about {int(rows * scale)}. ESTIMATE.")
    per_read = wall / max(1, a.chunk_reads)
    say(f"seconds per chunk read: {per_read:.3f}; mean compressed bytes per chunk read: "
        f"{a.bytes / max(1, a.chunk_reads) / 1e6:.3f} MB")

    # ---- the all-fields, both-leads, six-airport extrapolation
    say("")
    say("--- Extrapolation: all SPEC 8 fields present in the archive, both leads, all six airports (ESTIMATE) ---")
    boxes, spatial = {}, set()
    for st, p in airports.items():
        b = a.nodes(p["grid_lat"], p["grid_lon"])
        boxes[st] = b
        spatial.add((b[0] // CH_LAT, b[1] // CH_LAT, b[2] // CH_LON, b[3] // CH_LON))
    chunks_per_airport = {}
    allchunks = set()
    for st, (ia_, ib_, ja_, jb_) in boxes.items():
        cs = {(x // CH_LAT, y // CH_LON) for x in (ia_, ib_) for y in (ja_, jb_)}
        chunks_per_airport[st] = sorted(cs)
        allchunks |= cs
    say("spatial chunks (latitude chunk, longitude chunk) touched by each airport's 2 x 2 box:")
    for st, cs in chunks_per_airport.items():
        say(f"  {st}: {cs}")
    say(f"distinct spatial chunks over the six airports: {len(allchunks)} (an airport whose box straddles two chunks "
        "needs both)")
    recipe = {"temperature_2m": "2 m temperature", "wind_u_10m": "10 m wind u", "wind_v_10m": "10 m wind v",
              "pressure_reduced_to_mean_sea_level": "PRMSL (pressure tendency)",
              "downward_short_wave_radiation_flux_surface": "DSWRF",
              "total_cloud_cover_atmosphere": "total cloud (different definition; costed for completeness)"}
    sample_inits = inits_all[:: max(1, n_all // 24)]
    say(f"mean compressed bytes of one inner chunk, per variable, over {len(sample_inits)} inits x the "
        f"{len(allchunks)} spatial chunks (from the shard indexes):")
    tot_bytes, tot_reads = 0.0, 0
    for var, label in recipe.items():
        szs = []
        for i in sample_inits:
            for (ca, co) in sorted(allchunks):
                szs.append(a.chunk_bytes(var, int(i), [24], [ca * CH_LAT], [co * CH_LON], count=False))
        m = float(np.mean(szs))
        vb = m * n_all * len(allchunks)
        say(f"  {var:44s} mean {m / 1e6:6.3f} MB per chunk; all {n_all} inits x {len(allchunks)} chunks = "
            f"{n_all * len(allchunks)} reads, {vb / 1e9:7.1f} GB   ({label})")
        tot_bytes += vb
        tot_reads += n_all * len(allchunks)
    say(f"  total, six variables: {tot_reads} chunk reads, about {tot_bytes / 1e9:.0f} GB compressed. The archive "
        "holds every hour and both leads in the same chunk (lead chunk 0 covers hours 0..104), so the hourly curve "
        "at both leads costs the same as one hour at one lead. ESTIMATE; if the strided time per read holds, "
        f"sequential wall time is about {tot_reads * per_read / 3600:.1f} h.")
    say("BYTES_USED_SPEED", a.bytes + a.index_bytes)


# --------------------------------------------------------------- 3.2 GRIB

def http_get(url, headers=None, timeout=60, tries=3):
    last = None
    for attempt in range(1, tries + 1):
        t0 = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
                return r.status, body, time.time() - t0
        except urllib.error.HTTPError as e:
            if e.code in (404, 403):
                return e.code, b"", time.time() - t0
            last = e
        except Exception as e:
            last = e
        time.sleep(1.0 * attempt)
    return 0, str(last).encode(), 0.0


def parse_idx(text):
    rows = []
    for ln in text.strip().split("\n"):
        p = ln.split(":")
        if len(p) >= 7:
            rows.append({"n": int(p[0]), "off": int(p[1]), "d": p[2], "var": p[3], "level": p[4], "step": p[5]})
    for k, r in enumerate(rows):
        r["end"] = rows[k + 1]["off"] - 1 if k + 1 < len(rows) else None
    return rows


def find_row(rows, var, level, fh, kind):
    """kind 'instant': step '<fh> hour fcst'; kind 'avg': an 'ave fcst' step ending at fh."""
    for r in rows:
        if r["var"] == var and r["level"] == level:
            if kind == "instant" and r["step"] == f"{fh} hour fcst":
                return r
            if kind == "avg" and r["step"].endswith("hour ave fcst") and r["step"].split(" ")[0].split("-")[-1] == str(fh):
                return r
    return None


GRIB_FIELDS = [   # (key, GRIB var, level, kind): the fields behind SPEC 8, as the record names them
    ("tmp2m", "TMP", "2 m above ground", "instant"),
    ("tcdc", "TCDC", "entire atmosphere", "instant"),
    ("ugrd10m", "UGRD", "10 m above ground", "instant"),
    ("vgrd10m", "VGRD", "10 m above ground", "instant"),
    ("dpt2m", "DPT", "2 m above ground", "instant"),
    ("t850", "TMP", "850 mb", "instant"),
    ("dswrf", "DSWRF", "surface", "avg"),
    ("prmsl", "PRMSL", "mean sea level", "instant"),
]


def mode_grib():
    head("3.2 The GRIB route's cost (noaa-gfs-bdp-pds, byte ranges, as the record does)")
    tmp = os.environ.get("S89_TMP")
    if not tmp:
        raise SystemExit("STOP: S89_TMP (the temporary directory) is not set")
    tdir = Path(tmp) / "grib"
    tdir.mkdir(parents=True, exist_ok=True)
    target_day = date(2024, 3, 15)
    run_date = target_day - timedelta(days=1)
    ymd = run_date.strftime("%Y%m%d")
    say(f"spent-year day {target_day}; run day {run_date}; four cycles; source {BUCKET}; tag: verified")
    base = lambda cyc: f"{BUCKET}/gfs.{ymd}/{cyc:02d}/atmos/gfs.t{cyc:02d}z.pgrb2.0p25"
    req_log = []       # (kind, secs, bytes)

    # ---- 1. idx listing for f021..f053, four cycles
    say("")
    say("--- 1. .idx listing: every forecast hour f021..f053 (f024..f053 asked; f021..f023 are the lead-3 "
        "hours the pressure tendency needs), all four cycles ---")
    idx = {}
    t_start = time.time()
    for cyc in (0, 6, 12, 18):
        for fh in range(21, 54):
            url = f"{base(cyc)}.f{fh:03d}.idx"
            st, body, dt = http_get(url)
            req_log.append(("idx", dt, len(body)))
            idx[(cyc, fh)] = parse_idx(body.decode()) if st == 200 else None
            if st != 200:
                say(f"  .idx f{fh:03d} cycle {cyc:02d}z: HTTP {st}")
    ok = sum(1 for v in idx.values() if v is not None)
    say(f".idx files answered 200: {ok} of {len(idx)} ({time.time() - t_start:.0f} s); "
        f"bytes {sum(b for k, _, b in req_log if k == 'idx') / 1e6:.2f} MB")
    say("")
    say("field presence per forecast hour (count of the 4 cycles where the message is present), "
        "f024..f053 for the 8 fields; a '.' means all four present:")
    miss_any = []
    for fh in range(24, 54):
        cells = []
        for key, var, lvl, kind in GRIB_FIELDS:
            n = sum(1 for cyc in (0, 6, 12, 18) if idx[(cyc, fh)] and find_row(idx[(cyc, fh)], var, lvl, fh, kind))
            cells.append("." if n == 4 else str(n))
            if n != 4:
                miss_any.append((fh, key, n))
        say(f"  f{fh:03d}: " + " ".join(f"{k}={c}" for (k, *_), c in zip(GRIB_FIELDS, cells)))
    say("forecast hours where a field is missing in some cycle:", miss_any if miss_any else "none")
    say("PRMSL present at f021..f023 (the lead-3 hours):",
        {fh: sum(1 for cyc in (0, 6, 12, 18) if idx[(cyc, fh)] and find_row(idx[(cyc, fh)], "PRMSL", "mean sea level", fh, "instant"))
         for fh in (21, 22, 23)})
    say("DSWRF at f022 (window label, per cycle):",
        [find_row(idx[(c, 22)], "DSWRF", "surface", 22, "avg")["step"] if idx[(c, 22)] and find_row(idx[(c, 22)], "DSWRF", "surface", 22, "avg") else None for c in (0, 6, 12, 18)])
    say("")
    say("DSWRF averaging window by forecast hour (the label, same in all four cycles?):")
    labels = {}
    for fh in range(21, 54):
        labs = []
        for cyc in (0, 6, 12, 18):
            r = idx[(cyc, fh)] and find_row(idx[(cyc, fh)], "DSWRF", "surface", fh, "avg")
            labs.append(r["step"] if r else None)
        labels[fh] = labs
        same = len(set(labs)) == 1
        w = labs[0].split(" ")[0] if labs[0] else "?"
        lo, hi = (int(w.split("-")[0]), int(w.split("-")[1])) if "-" in w else (0, 0)
        say(f"  f{fh:03d}: {labs[0]}   window {hi - lo} h   same in all cycles: {same}")
    say("(The window resets every 6 h: a 6 h average at f024, f030, f036, f042, f048; a 2 h average at f026 and "
        "f032 ... The window is NOT constant across forecast hours, as F97 and F102 found.)")

    # ---- 2. the fetch: 24-hour lead (f024..f029) and its extra hours
    say("")
    say("--- 2. Fetch: the SPEC 8 fields for the 24-hour lead on the run day ---")
    plan = []     # (cyc, fh, key, row)
    for cyc in (0, 6, 12, 18):
        for fh in range(24, 30):
            for key, var, lvl, kind in GRIB_FIELDS:
                plan.append((cyc, fh, key, find_row(idx[(cyc, fh)], var, lvl, fh, kind)))
        for fh in (21, 22, 23):
            plan.append((cyc, fh, "prmsl_m3", find_row(idx[(cyc, fh)], "PRMSL", "mean sea level", fh, "instant")))
        plan.append((cyc, 22, "dswrf_f022", find_row(idx[(cyc, 22)], "DSWRF", "surface", 22, "avg")))
    plan = [p for p in plan if p[3] is not None]
    say(f"messages planned: {len(plan)} (24 files x 8 fields = 192; PRMSL at f021..f023 x 4 cycles = 12; "
        f"DSWRF at f022 x 4 cycles = 4)")
    got_bytes, per_msg = 0, []
    t_fetch = time.time()
    stopped = False
    for n, (cyc, fh, key, r) in enumerate(plan):
        if got_bytes > GRIB_LIMIT_BYTES - 2_000_000:
            say(f"  STOP at the {GRIB_LIMIT_BYTES / 1e6:.0f} MB limit after {n} messages")
            stopped = True
            break
        rng = f"bytes={r['off']}-{'' if r['end'] is None else r['end']}"
        st, body, dt = http_get(f"{base(cyc)}.f{fh:03d}", headers={"Range": rng})
        ok_msg = False
        if st in (200, 206) and len(body) >= 16:
            ok_msg = (body[:4] == b"GRIB" and body[-4:] == b"7777" and body[7] == 2
                      and struct.unpack(">Q", body[8:16])[0] == len(body))
        per_msg.append((cyc, fh, key, dt, len(body), ok_msg, st))
        req_log.append(("msg", dt, len(body)))
        got_bytes += len(body)
        (tdir / f"t{cyc:02d}_f{fh:03d}_{key}.grib2").write_bytes(body)    # kept in the temp dir only
        if (n + 1) % 40 == 0:
            say(f"  {n + 1}/{len(plan)} messages, {got_bytes / 1e6:.0f} MB, {time.time() - t_fetch:.0f} s")
    wall = time.time() - t_fetch
    nok = sum(1 for p in per_msg if p[5])
    say(f"fetched {len(per_msg)} messages in {wall:.0f} s: {nok} well-formed (GRIB marker, edition 2, length field "
        f"equals bytes, end marker 7777); bytes {got_bytes / 1e6:.1f} MB (limit {GRIB_LIMIT_BYTES / 1e6:.0f} MB)")
    sizes = [p[4] for p in per_msg]
    say(f"message size: mean {sum(sizes) / len(sizes) / 1e3:.0f} kB, min {min(sizes) / 1e3:.0f} kB, "
        f"max {max(sizes) / 1e3:.0f} kB; seconds per message request: mean {sum(p[3] for p in per_msg) / len(per_msg):.3f}, "
        f"max {max(p[3] for p in per_msg):.2f}")
    by_key = {}
    for p in per_msg:
        by_key.setdefault(p[2], []).append(p[4])
    for k, v in by_key.items():
        say(f"  {k:11s} n={len(v):3d} mean {sum(v) / len(v) / 1e3:7.0f} kB")
    bad = [p for p in per_msg if not p[5]]
    if bad:
        say("messages that did not check out:", bad[:10])
    idx_secs = [dt for k, dt, b in req_log if k == "idx"]
    say(f"timing detail: .idx requests {len(idx_secs)}, mean {sum(idx_secs) / len(idx_secs):.3f} s; "
        f"message requests {len(per_msg)}, mean {sum(p[3] for p in per_msg) / len(per_msg):.3f} s")
    say("Per-request timing (cycle, fhour, field, seconds, bytes) in the first 12 and last 3 requests:")
    for p in per_msg[:12] + per_msg[-3:]:
        say(f"  {p[0]:02d}z f{p[1]:03d} {p[2]:11s} {p[3]:.3f} s {p[4]} B")

    # ---- 3. extrapolation
    say("")
    say("--- 3. Extrapolation (ESTIMATE), one global field serves all airports ---")
    msgs_day_lead = len(per_msg) if not stopped else len(plan)
    files_day_lead = 24 + 12            # f024..f029 and f021..f023, four cycles
    days = (WINDOW_END - WINDOW_START).days + 1
    mean_b = sum(sizes) / len(sizes)
    mean_t_msg = sum(p[3] for p in per_msg) / len(per_msg)
    mean_t_idx = sum(idx_secs) / len(idx_secs)
    two = 2
    tot_msgs = msgs_day_lead * days * two
    tot_idx = files_day_lead * days * two
    tot_bytes = tot_msgs * mean_b
    tot_secs = tot_msgs * mean_t_msg + tot_idx * mean_t_idx
    say(f"days {WINDOW_START} .. {WINDOW_END}: {days}; leads 24 h and 48..53 h: x2 (the 48 h lead has the same "
        f"file structure, f048..f053 with f045..f047 and f046)")
    say(f"messages per day per lead: {msgs_day_lead}; .idx files per day per lead: {files_day_lead}")
    say(f"total message requests: {msgs_day_lead} x {days} x 2 = {tot_msgs:,}; total .idx requests: "
        f"{files_day_lead} x {days} x 2 = {tot_idx:,}; total requests {tot_msgs + tot_idx:,}")
    say(f"total bytes: {tot_msgs:,} x {mean_b / 1e3:.0f} kB = {tot_bytes / 1e9:.0f} GB "
        f"(per lead {tot_bytes / 2e9:.0f} GB)")
    say(f"total wall time at the measured sequential rate: {tot_msgs:,} x {mean_t_msg:.3f} s + {tot_idx:,} x "
        f"{mean_t_idx:.3f} s = {tot_secs / 3600:.0f} h ({tot_secs / 86400:.1f} days). With the 48-way concurrency "
        f"F90 used, divide by up to about 48 (not measured here).")
    say("Compare D81.11's planning figure (not checked): about 470,000 byte-range requests and about 370 GB per "
        "lead, about 750 GB for both. This estimate counts every field the record's recipe fetches for each "
        "target hour, including the lead-3 pressure hours and the f022 radiation hour.")
    say("The record's own pulls fetched 14 to 15 messages per station-day (F128.2), which includes fields the "
        "model does not use (925 and 700 hPa temperature, RH, specific humidity, surface pressure).")
    # delete the downloaded bytes
    n = 0
    for f in tdir.glob("*.grib2"):
        f.unlink()
        n += 1
    say(f"deleted {n} downloaded message files from the temporary directory")
    say("BYTES_GRIB", got_bytes + sum(b for k, _, b in req_log if k == "idx"))


# ---------------------------------------------------- 3.3 and 3.4 (offline)

def mode_obs():
    import pandas as pd
    from zoneinfo import ZoneInfo
    head("3.3 Hourly observations (counts only; no temperature value is printed)")
    airports = load_airports()
    pat = re.compile(r"iem_asos_(?P<st>[A-Z]+)_(?P<a>\d{4}-\d\d-\d\d)_(?P<b>\d{4}-\d\d-\d\d)_routine\.csv$")
    days_all = [WINDOW_START + timedelta(days=k) for k in range((WINDOW_END - WINDOW_START).days + 1)]
    say(f"days in {WINDOW_START}..{WINDOW_END}: {len(days_all)}")
    hdrs = {}
    for f in sorted(RAW.glob("iem_asos_*.csv")):
        with open(f) as fh:
            hdrs.setdefault(fh.readline().strip(), []).append(f.name)
    say("column sets of every committed IEM observation file:")
    for h, names in hdrs.items():
        say(f"  {h}   ({len(names)} files)")
    say("No committed file has a raw METAR text column or any maximum-temperature column.")
    summary = {}
    for st in airports:
        files = []
        for f in sorted(RAW.glob(f"iem_asos_{st}_*_routine.csv")):
            m = pat.search(f.name)
            if not m:
                continue
            a, b = date.fromisoformat(m["a"]), date.fromisoformat(m["b"])
            if a >= WINDOW_START and (b - a).days > 100:
                files.append(f)
        frames = [pd.read_csv(f, dtype=str) for f in files]
        df = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["valid"])
        df["ts"] = pd.to_datetime(df["valid"], utc=True)
        ok = df["tmpc"].notna() & ~df["tmpc"].isin(["M", "", "T", "None"])
        val = pd.to_numeric(df["tmpc"].where(ok), errors="coerce")
        usable = df[ok & val.map(lambda x: x == x and abs(x) != float("inf"))].copy()
        mins = df["ts"].dt.minute
        usable["hour_ts"] = usable["ts"].dt.floor("h") + pd.to_timedelta((usable["ts"].dt.minute >= 30).astype(int), unit="h")
        usable["off_min"] = (usable["ts"] - usable["hour_ts"]).abs().dt.total_seconds() / 60.0
        near = usable[usable["off_min"] <= 15.0]       # inclusive, as the record (8.8 G3)
        near = near[(near["hour_ts"].dt.date >= WINDOW_START) & (near["hour_ts"].dt.date <= WINDOW_END)]
        have = near.drop_duplicates(subset=["hour_ts"])
        per_hour = have.groupby(have["hour_ts"].dt.hour).size()
        full_days = have.groupby(have["hour_ts"].dt.date).size()
        top_min = mins.value_counts().head(4)
        say("")
        say(f"{st}: files {[f.name for f in files]}")
        say(f"  rows {len(df)}; first report {df['ts'].min()}; last report {df['ts'].max()}; "
            f"distinct hours of the day with a report: {sorted(df['ts'].dt.hour.unique().tolist()) == list(range(24))} "
            f"({df['ts'].dt.hour.nunique()} of 24)")
        say(f"  rows with no usable temperature (M, blank, T, None, non-finite): {int((~(ok & val.notna())).sum())}")
        say(f"  usual minute past the hour of the routine reports (minute: rows): "
            f"{ {int(k): int(v) for k, v in top_min.items()} }")
        say(f"  routine reports per day: median {int(df.groupby(df['ts'].dt.date).size().median())}")
        say(f"  days (of {len(days_all)}) with a usable report within 15 min of each whole hour (hour: days):")
        say("   " + "  ".join(f"{h:02d}:{int(per_hour.get(h, 0))}" for h in range(24)))
        say(f"  days with all 24 hours usable: {int((full_days == 24).sum())}; "
            f"days with none: {len(days_all) - len(full_days)}")
        summary[st] = (len(df),)
    say("")
    say("Query that gave these files (from each .meta.txt: the first 'exact URL requested', and the pull time):")
    for st in airports:
        f = sorted(RAW.glob(f"iem_asos_{st}_2022-01-01_2022-12-31_routine.csv.meta.txt"))
        if f:
            txt = f[0].read_text().splitlines()
            url = next((l.strip() for l in txt if l.startswith("https://")), "?")
            pulled = next((l for l in txt if l.startswith("pulled at")), "?")
            say(f"  {st}: {pulled.strip()}\n      {url}")
    say("Every file is the routine report only (report_type=3), UTC, data = tmpc and dwpc: it holds every hour of "
        "the day, so hourly truth for a stage C curve is already committed. Nothing was fetched.")

    head("3.4 Daily-maximum sources: counts from committed files, and the day window each airport needs")
    say("METAR maximum-temperature groups (US 6-hour '1xxxx' and 24-hour '4xxxxxxxx'): the committed files carry "
        "no raw METAR text, so they cannot be counted from them. To count them, the same IEM request needs the "
        "'metar' field added (IEM's download page lists 'Raw METAR'; its variable list has no 6-hour or 24-hour "
        "maximum-temperature field). Not fetched.")
    tz = {}
    for gj in RAW.glob("iem_station_metadata_*.geojson"):
        try:
            d = json.loads(gj.read_text())
        except Exception:
            continue
        for ft in d["features"]:
            sid = ft["properties"]["sid"]
            if sid in airports and ft["properties"]["network"].startswith(("GB__", "FR__", "IA_", "AU__", "NV_", "CA_")):
                tz[sid] = ft["properties"]["tzname"]
    say("time zone from IEM's own station listing (committed):", tz)
    say("")
    say("Day window a maximum of the hourly reports would need, by the local STANDARD-time day (no daylight "
        "saving), as a UTC window; standard offset read from the time zone database:")
    for st, name in tz.items():
        z = ZoneInfo(name)
        jan = datetime(2024, 1, 15, 12, tzinfo=z).utcoffset()
        jul = datetime(2024, 7, 15, 12, tzinfo=z).utcoffset()
        std = min(jan, jul)
        h = -std.total_seconds() / 3600
        a = (h % 24)
        say(f"  {st:5s} {name:22s} standard offset UTC{std.total_seconds() / 3600:+.0f}; local-standard-time day = "
            f"{a:02.0f}:00 UTC to {a:02.0f}:00 UTC next day; target hour {airports[st]['target_hour']:02d}:00 UTC; "
            f"civil (daylight-saving) offsets {jan.total_seconds() / 3600:+.0f} / {jul.total_seconds() / 3600:+.0f}")
    say("A day window is a stage C choice (not made here). The target hour is the local standard noon, so the "
        "afternoon peak falls in the second half of the window.")


# ------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--meta", action="store_true")
    g.add_argument("--docs", action="store_true")
    g.add_argument("--repro", action="store_true")
    g.add_argument("--speed", action="store_true")
    g.add_argument("--grib", action="store_true")
    g.add_argument("--obs", action="store_true")
    ap.add_argument("--budget-gb", type=float, default=3.6, help="byte budget for --repro")
    ap.add_argument("--limit-dates", type=int, default=0, help="--repro: trial run on the first N usable dates")
    ap.add_argument("--date-step", type=int, default=1, help="--repro: use every Nth monthly date")
    ap.add_argument("--stride", type=int, default=16, help="--speed: read every Nth init")
    ap.add_argument("--spent-gb", type=float, default=0.0, help="--speed: GB already used by --repro")
    a = ap.parse_args()
    if a.meta:
        mode_meta()
    elif a.docs:
        mode_docs()
    elif a.repro:
        mode_repro(a.budget_gb, a.limit_dates, a.date_step)
    elif a.speed:
        mode_speed(a.stride, a.spent_gb)
    elif a.grib:
        mode_grib()
    elif a.obs:
        mode_obs()


if __name__ == "__main__":
    main()
