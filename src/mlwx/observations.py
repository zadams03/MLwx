"""Observations: IEM routine reports and the pairing rule (DECISIONS D88.7, D103.6).

Ported from scripts/session86_forward_build.py (iem_query, parse_reports,
pair_nearest) and scripts/session96_stagec_table.py (nearest_obs), which are
the reference and are never edited.

The observation for a valid whole hour is the nearest usable routine report
within 15 minutes of it, inclusive (SPEC 4.5, 8.8 G2, G3). A report whose
temperature is M, blank, T or None is skipped; a non-finite one is rejected and
counted. A tie keeps the earlier report. Nothing is ever filled (SPEC 2.2).
"""

import bisect
import csv
import datetime as dt
import io
import math
import time
import urllib.error
import urllib.request

IEM_URL = "https://mesonet.agron.iastate.edu/cgi-bin/request/asos.py"
TOL_MIN = 15                      # SPEC 4.5, inclusive (8.8 G3)
TOL = dt.timedelta(minutes=TOL_MIN)
USER_AGENT = "MLwx-live/1.0"
IEM_PAUSE_S = 1.5                 # between requests, as the record's fetch


class ObsFetchError(Exception):
    """An IEM request failed after its tries."""


def iem_query(station, first_day, last_day):
    """The record's query form (see any data/raw/iem_asos_*.meta.txt): report_type=3 (routine),
    UTC, and an exclusive end date, so the request ends after last_day."""
    end = last_day + dt.timedelta(days=1)
    return (f"{IEM_URL}?station={station}&data=tmpc&data=dwpc"
            f"&year1={first_day.year}&month1={first_day.month}&day1={first_day.day}"
            f"&year2={end.year}&month2={end.month}&day2={end.day}"
            "&tz=UTC&format=onlycomma&latlon=yes&elev=yes&missing=M&trace=T&direct=no&report_type=3")


def fetch_reports(station, first_day, last_day, sleep=time.sleep, tries=3, timeout=120):
    """One IEM request, as text. At most 3 tries, spaced; raises ObsFetchError."""
    url = iem_query(station, first_day, last_day)
    last = None
    for attempt in range(1, tries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                if r.status == 200:
                    text = r.read().decode("utf-8")
                    sleep(IEM_PAUSE_S)
                    return text
                last = f"HTTP {r.status}"
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}"
            if e.code not in (429, 500, 502, 503, 504):
                break
        except (urllib.error.URLError, OSError, UnicodeDecodeError) as e:
            last = repr(e)
        if attempt < tries:
            sleep(2.0 * attempt)
    raise ObsFetchError(f"{url}: failed: {last}")


def finite_float(s):
    """None for a missing or non-finite value (SPEC 8.7 item 2)."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def new_stats():
    return {"rows": 0, "no_temp": 0, "nonfinite": 0, "duplicates": 0, "ties": 0}


def parse_reports(text, station, stats):
    """Reports in file order: (time, value or None). A non-finite tmpc is rejected and counted; a
    missing tmpc (M, blank, T, None) is unusable (G2) and kept with value None."""
    out = []
    for r in csv.DictReader(io.StringIO(text)):
        if r["station"] != station:
            raise RuntimeError(f"unexpected station {r['station']}")
        t = dt.datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
        raw = (r.get("tmpc") or "").strip()
        v = None
        if raw not in ("M", "", "T", "None"):
            v = finite_float(raw)
            if v is None:
                stats["nonfinite"] += 1
        if v is None:
            stats["no_temp"] += 1
        out.append((t, v))
        stats["rows"] += 1
    return out


def pair_nearest(reports, target_dt):
    """The NEAREST report with a usable finite tmpc within 15 minutes of the target hour,
    inclusive. A tie keeps the earlier report and is flagged."""
    cands = sorted((abs((t - target_dt).total_seconds()) / 60.0, t, v) for t, v in reports
                   if abs((t - target_dt).total_seconds()) <= TOL_MIN * 60)
    usable = [c for c in cands if c[2] is not None]
    res = {"n_in_window": len(cands), "n_usable": len(usable), "tie": 0, "obs": None,
           "report_time": None, "status": "paired"}
    if usable:
        best = usable[0]
        res["obs"], res["report_time"] = best[2], best[1]
        if len(usable) > 1 and usable[1][0] == best[0]:
            res["tie"] = 1
        return res
    res["status"] = ("no routine report within 15 min" if not cands else "no usable temperature within 15 min")
    return res


class ReportSet:
    """One airport's reports, deduplicated by time, sorted, with the pairing for any valid hour.

    Repeated timestamps. The record's rule (the tables and the training pairing, F138.8 item 6) keeps
    the FIRST row; that is the default (live=False). The order of rows with one timestamp is not stable
    between IEM downloads (session 109, Gate D), so the live pairing uses the owner's ruling instead
    (live=True): when two or more rows share a timestamp and their values differ (one missing counts as
    different), that timestamp is ignored and the nearest other report within 15 minutes is used (D88.7);
    rows with the same value are one report."""

    def __init__(self, reports, stats=None, live=False):
        self.stats = stats if stats is not None else new_stats()
        self.live = live
        self.stats.setdefault("ambiguous", 0)
        by_time, order = {}, {}
        for t, v in reports:
            if t in by_time:
                self.stats["duplicates"] += 1
                order[t].append(v)
                continue
            by_time[t] = v
            order[t] = [v]
        if live:
            for t, vals in order.items():
                if len(set(vals)) > 1:
                    del by_time[t]
                    self.stats["ambiguous"] += 1
        self.times = sorted(by_time)
        self.vals = [by_time[t] for t in self.times]
        self.cache = {}

    @classmethod
    def from_text(cls, text, station, live=False):
        stats = new_stats()
        return cls(parse_reports(text, station, stats), stats, live)

    def nearest(self, valid):
        """(observation or None, report time or None) for a valid whole hour (D88.7)."""
        if valid in self.cache:
            return self.cache[valid]
        i, j = bisect.bisect_left(self.times, valid - TOL), bisect.bisect_right(self.times, valid + TOL)
        res = pair_nearest(list(zip(self.times[i:j], self.vals[i:j])), valid)
        self.stats["ties"] += res["tie"]
        self.cache[valid] = (res["obs"], res["report_time"])
        return self.cache[valid]
