"""The daily maximum read off the curve (DECISIONS D98.10, D103.2).

Ported from scripts/session104_curve_cv.py (local_day, usable_day, day_cycle, the forecast side
of daily_max), the reference, never edited. A local calendar day is midnight to midnight in the
airport's own time zone (civil time, daylight saving included). The forecast maximum is the
highest of the curve's hourly values over every whole hour of the day; if any hour has no value,
the day has no maximum (D98.10(c)), never a filled one.

v1 (D103.2): for every cycle, each local day wholly inside leads 3 to 48 gets its maximum read
off that cycle's corrected curve. (The scoring rule of D98.10(b), one run per day, is the
research design's; Gate B uses day_cycle for it.)
"""

import datetime as dt
from zoneinfo import ZoneInfo

HOUR = dt.timedelta(hours=1)


def local_day(d, tzname):
    """The UTC start, the UTC end (exclusive) and the whole UTC hours of local day d."""
    tz = ZoneInfo(tzname)
    utc = dt.timezone.utc
    d2 = d + dt.timedelta(days=1)
    s = dt.datetime(d.year, d.month, d.day, tzinfo=tz).astimezone(utc).replace(tzinfo=None)
    e = dt.datetime(d2.year, d2.month, d2.day, tzinfo=tz).astimezone(utc).replace(tzinfo=None)
    if s.minute or e.minute:
        raise ValueError(f"{tzname} is not a whole number of hours from UTC on {d}")
    hours = [s + dt.timedelta(hours=k) for k in range(int((e - s) / HOUR))]
    if len(hours) not in (23, 24, 25):
        raise ValueError(f"{tzname} local day {d} has {len(hours)} hours")
    return s, e, hours


def usable_day(n_hours, n_usable):
    """D82.8, D98.10(a): usable hours at least the day's hours minus 2."""
    return n_usable >= n_hours - 2


def day_cycle(s, arrival_hours=4):
    """D98.10(b): the latest cycle c (00, 06, 12, 18 UTC) with c + arrival <= the day's start s."""
    t = s - dt.timedelta(hours=arrival_hours)
    return t.replace(hour=6 * (t.hour // 6), minute=0, second=0, microsecond=0)


def read_off(hours, curve):
    """The forecast maximum over the day's hours, or None if any hour has no value.
    curve maps a valid time to a value (or None)."""
    vals = [curve.get(h) for h in hours]
    if any(v is None for v in vals):
        return None
    return max(vals)


def days_inside(cycle, tzname, first_lead=3, last_lead=48):
    """The local dates wholly inside leads first_lead to last_lead of a cycle, with their UTC hours:
    [(date, hours)]."""
    lo, hi = cycle + first_lead * HOUR, cycle + last_lead * HOUR
    tz = ZoneInfo(tzname)
    d = (lo.replace(tzinfo=dt.timezone.utc).astimezone(tz)).date() - dt.timedelta(days=1)
    end = (hi.replace(tzinfo=dt.timezone.utc).astimezone(tz)).date() + dt.timedelta(days=1)
    out = []
    while d <= end:
        _, _, hours = local_day(d, tzname)
        if hours[0] >= lo and hours[-1] <= hi:
            out.append((d, hours))
        d += dt.timedelta(days=1)
    return out


def daily_maxima(cycle, tzname, curve, first_lead=3, last_lead=48):
    """{local date: maximum} for each local day wholly inside the cycle's leads, from curve
    ({valid time: value}). A day with a missing hour is left out."""
    out = {}
    for d, hours in days_inside(cycle, tzname, first_lead, last_lead):
        m = read_off(hours, curve)
        if m is not None:
            out[d] = m
    return out
