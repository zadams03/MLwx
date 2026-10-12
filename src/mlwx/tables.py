"""The stage C table format: one row per (airport, cycle, lead) (DECISIONS D88.4, D88.5, F138.4).

Ported from scripts/session96_stagec_table.py (COLUMNS, fmt, the row line of make_row,
table_bytes) and scripts/session97_stagec_cv.py (load_table), the reference, never
edited. The format is the record's, byte for byte: Gate A rebuilds the recorded tables
with it. Training reads the same files back.
"""

import csv
import datetime as dt
import gzip
import hashlib
import math
import os

from . import features

COLUMNS = (["station", "cycle_utc", "cycle_hour", "lead", "valid_utc"] + features.GRIB_COLS
           + ["obs_tmpc", "obs_time_utc", "uses_whole_file", "complete_case"])
TIME_FORMAT = "%Y-%m-%dT%H:%MZ"


def iso(t):
    return t.strftime(TIME_FORMAT)


def parse_time(s):
    return dt.datetime.strptime(s, TIME_FORMAT)


def fmt(v):
    if v is None:
        return ""
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float):
        return repr(v)
    return str(v)


def table_line(station, cycle, n, out, obs, obs_time, whole):
    """One table row as the record writes it. complete_case: the nine inputs and an observation."""
    valid = cycle + dt.timedelta(hours=n)
    complete = all(out[c] is not None for c in features.G15) and obs is not None
    row = [station, iso(cycle), cycle.hour, n, iso(valid)] + [out[c] for c in features.GRIB_COLS] + \
          [obs, None if obs_time is None else iso(obs_time), whole, complete]
    return ",".join(fmt(v) for v in row), complete


def table_bytes(lines):
    """Equal content gives equal bytes: no file name and a zero timestamp in the gzip header."""
    return gzip.compress(("\n".join(lines) + "\n").encode("ascii"), compresslevel=9, mtime=0)


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_new_file(path, data):
    """Temporary name first, then a hard link to the final name (never overwrites)."""
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    try:
        os.link(tmp, path)
    finally:
        os.unlink(tmp)


def fval(s):
    return float(s) if s != "" else None


def read_table_rows(path, station, leads=None):
    """Rows of one table file, in file order (cycle, then lead). Each row:
    (cycle, valid, cycle_hour, lead, complete, obs, temp, x), where x is the nine G15 values
    (None where empty). complete_case is checked against the nine columns and the observation;
    temp against temperature_grib_c."""
    lead_set = None if leads is None else set(leads)
    rows = []
    with gzip.open(path, "rt", newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        if head != COLUMNS:
            raise ValueError(f"{path}: header is not the table format's")
        ix = {c: i for i, c in enumerate(head)}
        gi = [ix[c] for c in features.G15]
        for r in rd:
            if r[ix["station"]] != station:
                raise ValueError(f"{path} holds a row for station {r[ix['station']]}")
            lead = int(r[ix["lead"]])
            if lead_set is not None and lead not in lead_set:
                continue
            x = [fval(r[i]) for i in gi]
            obs = fval(r[ix["obs_tmpc"]])
            complete = r[ix["complete_case"]] == "true"
            if complete != (all(v is not None for v in x) and obs is not None):
                raise ValueError(f"{path}: complete_case disagrees with its columns at {r[ix['cycle_utc']]} "
                                 f"lead {lead}")
            if x[0] is not None and float(r[ix["temperature_grib_c"]]) != x[0]:
                raise ValueError(f"{path}: temp differs from temperature_grib_c")
            rows.append((parse_time(r[ix["cycle_utc"]]), parse_time(r[ix["valid_utc"]]), int(r[ix["cycle_hour"]]),
                         lead, complete, obs, x[0], x))
    return rows


def isfinite(v):
    return v is not None and math.isfinite(v)
