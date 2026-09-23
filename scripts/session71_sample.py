"""Session 71: the audit 68a sample and the GRIB message plan for L, D, T, R.

Shared by session71_ldtr_pull.py and session71_ldtr_rebuild.py. Pure: it
reads committed files only, makes no network call and writes nothing.

The sample is audit 68a's own pre-registered rule (notes/audit-session-68a.md
section 2.2): the first, middle and last day of each of three windows, at all
five airports. "Middle" is day index floor((N-1)/2) from the window's first
day. Audit 68a used no substitutions (its section 4.1). recover_sample()
rebuilds the list from the rule and then checks it, line for line, against
the 45 station-days audit 68a printed in its section 4.2.

The message plan is the recipe of the L, D, T and R build scripts, written
out as data (session 71 Step 1). Line numbers refer to those scripts.
"""

import re
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
AUDIT_68A = ROOT / "notes" / "audit-session-68a.md"

BUCKET = "https://noaa-gfs-bdp-pds.s3.amazonaws.com"

# SPEC 3.4: station -> (target hour UTC, grid latitude, grid longitude).
# Same values as every GRIB build script's AIRPORTS table.
AIRPORTS = {
    "EGLC": (12, 51.487137, 0.0),
    "LFPG": (12, 49.027008, 2.578125),
    "DSM":  (18, 41.52945, -93.63281),
    "YSDU": (2, -32.274643, 148.59375),
    "RNO":  (20, 39.537918, -119.765625),
}

# Audit 68a section 2.2: the three windows the sample is drawn from.
WINDOWS = [
    ("training", date(2021, 3, 24), date(2024, 7, 31)),
    ("reserved", date(2024, 8, 1), date(2025, 7, 31)),
    ("sealed", date(2025, 8, 1), date(2026, 7, 31)),
]

# The committed files that hold each window's L, D, T, R values (SPEC 8.1).
FAMILY_FILES = {
    "L": {"training": "session49_v16_window_with_upper_air.csv",
          "reserved": "session63_reserved_window_with_upper_air.csv",
          "sealed": "session49_sealed_window_with_upper_air.csv"},
    "D": {"training": "session51_v16_window_with_moisture.csv",
          "reserved": "session63_reserved_window_with_moisture.csv",
          "sealed": "session51_sealed_window_with_moisture.csv"},
    "T": {"training": "session53_v16_window_with_pressure.csv",
          "reserved": "session63_reserved_window_with_pressure.csv",
          "sealed": "session53_sealed_window_with_pressure.csv"},
    "R": {"training": "session55_v16_window_with_radiation.csv",
          "reserved": "session63_reserved_window_with_radiation.csv",
          "sealed": "session55_sealed_window_with_radiation.csv"},
}

# The base B files the L and D recipes read temperature_grib_c from
# (session49 line 295, session51 line 306, session63 lines 272 and 304).
BASE_FILES = {
    "training": "grib_features_v16_window.csv",
    "reserved": "grib_features_v16_window.csv",
    "sealed": "grib_features_sealed_window.csv",
}

# One entry per GRIB message kind: (key, family, GRIB var, idx level,
# forecast-hour offset from the airport's lead, step kind).
# step kind "inst" = idx step "<fh> hour fcst"; "ave" = "<a>-<fh> hour ave fcst".
MESSAGE_KINDS = [
    ("t925", "L", "TMP", "925 mb", 0, "inst"),
    ("t850", "L", "TMP", "850 mb", 0, "inst"),
    ("t700", "L", "TMP", "700 mb", 0, "inst"),
    ("rh2m", "D", "RH", "2 m above ground", 0, "inst"),
    ("dpt2m", "D", "DPT", "2 m above ground", 0, "inst"),
    ("spfh2m", "D", "SPFH", "2 m above ground", 0, "inst"),
    ("prmsl", "T", "PRMSL", "mean sea level", 0, "inst"),
    ("pres_sfc", "T", "PRES", "surface", 0, "inst"),
    ("prmsl_m3", "T", "PRMSL", "mean sea level", -3, "inst"),
    ("dswrf", "R", "DSWRF", "surface", 0, "ave"),
    ("dswrf_m2", "R", "DSWRF", "surface", -2, "ave"),  # lead-24 airports only
]


def cycle_and_lead(target_hour):
    """F89 / D48.2: run at floor(HH/6)*6 UTC the day before, lead 24 + HH mod 6."""
    return (target_hour // 6) * 6, 24 + (target_hour % 6)


def radiation_reset(fhour):
    """GFS resets its radiation averages every 6 forecast hours. The average
    in the file at forecast hour fh starts at the last reset before fh
    (session55 lines 137-141: 24->18, 22->18, 26->24)."""
    return 6 * ((fhour - 1) // 6)


def needs_deaccumulation(lead):
    return lead - radiation_reset(lead) != 2


def middle_day(start, end):
    n = (end - start).days + 1
    return start + timedelta(days=(n - 1) // 2)


def sample_from_rule():
    """[(window, station, target_date)] in audit 68a's own print order:
    window, then date, then station."""
    out = []
    for window, start, end in WINDOWS:
        for d in (start, middle_day(start, end), end):
            for station in AIRPORTS:
                out.append((window, station, d))
    return out


def sample_from_audit():
    """The 45 station-days audit 68a printed under '== target_hour' in 4.2."""
    text = AUDIT_68A.read_text()
    block = text.split("== target_hour (45 station-days) ==", 1)[1].split("==", 1)[0]
    pat = re.compile(r"^\s+(training|reserved|sealed)\s+(\w+)\s+(\d{4}-\d{2}-\d{2})\s", re.M)
    return [(w, s, date.fromisoformat(d)) for w, s, d in pat.findall(block)]


def recover_sample():
    rule = sample_from_rule()
    audit = sample_from_audit()
    if rule != audit:
        raise SystemExit(f"STOP: sample rule ({len(rule)}) and audit 68a's printed "
                         f"list ({len(audit)}) differ -- the sample cannot be recovered exactly.")
    return rule


def messages_for(station, target_date):
    """The GRIB messages one station-day needs, as dicts."""
    target_hour = AIRPORTS[station][0]
    cycle, lead = cycle_and_lead(target_hour)
    run_date = target_date - timedelta(days=1)
    out = []
    for key, family, var, level, offset, kind in MESSAGE_KINDS:
        if key == "dswrf_m2" and not needs_deaccumulation(lead):
            continue
        fh = lead + offset
        if kind == "inst":
            step = f"{fh} hour fcst"
        else:
            step = f"{radiation_reset(fh)}-{fh} hour ave fcst"
        out.append({"key": key, "family": family, "var": var, "level": level,
                    "run_date": run_date, "cycle": cycle, "fhour": fh,
                    "idx_step": step})
    return out


def message_id(m):
    return (m["run_date"], m["cycle"], m["fhour"], m["var"], m["level"])


def file_url(run_date, cycle, fhour):
    ymd = run_date.strftime("%Y%m%d")
    return f"{BUCKET}/gfs.{ymd}/{cycle:02d}/atmos/gfs.t{cycle:02d}z.pgrb2.0p25.f{fhour:03d}"


def cache_name(m):
    """File name in data/raw/grib/session71/ for one message."""
    lvl = m["level"].replace(" ", "")
    return (f"gfs_{m['run_date'].strftime('%Y%m%d')}_t{m['cycle']:02d}z_"
            f"f{m['fhour']:03d}_{m['var']}_{lvl}.grib2")


def idx_cache_name(run_date, cycle, fhour):
    return f"gfs_{run_date.strftime('%Y%m%d')}_t{cycle:02d}z_f{fhour:03d}.idx"


def build_plan(sample):
    """Unique messages across the sample -> {message_id: (message, [stations])}."""
    plan = {}
    for _, station, d in sample:
        for m in messages_for(station, d):
            mid = message_id(m)
            if mid not in plan:
                plan[mid] = (m, [])
            plan[mid][1].append(f"{station}:{d.isoformat()}")
    return dict(sorted(plan.items(), key=lambda kv: cache_name(kv[1][0])))
