"""The prediction log (DECISIONS D103.8).

One file per cycle, for all airports, at log/YYYY/MM/<model>_YYYYMMDDHH.csv, written once and never
edited. A correction is a new file, never an edit; git history is the proof. The writer refuses to
overwrite an existing file: it writes a temporary name and links it to the final name, and a link
onto an existing file fails.

Each row: airport (ICAO), cycle, lead, valid time, raw GFS (the elevation-adjusted 2 m temperature),
baseline, b (the drift tracker's value), corrected value (baseline plus b), the weather model's
version, the product models' manifest SHA-256, the code commit and the issue time. Floats are
written with repr, so they read back as the identical number.
"""

import csv
import datetime as dt
import io
import os
import re
from pathlib import Path

TIME_FORMAT = "%Y-%m-%dT%H:%MZ"
LOG_COLUMNS = ["airport", "cycle_utc", "lead", "valid_utc", "raw_gfs", "baseline", "b", "corrected",
               "gfs_version", "model_sha256", "code_commit", "issued_utc"]
_NAME = re.compile(r"^(?P<model>[a-z0-9]+)_(?P<stamp>\d{10})\.csv$")


class LogExists(Exception):
    """The log file already exists. It is never overwritten."""


def iso(t):
    return t.strftime(TIME_FORMAT)


def parse_time(s):
    return dt.datetime.strptime(s, TIME_FORMAT)


def log_path(root, model, cycle):
    return Path(root) / "log" / f"{cycle:%Y}" / f"{cycle:%m}" / f"{model}_{cycle:%Y%m%d%H}.csv"


def row_values(r):
    """The log row as a list of strings, in column order."""
    return [r["airport"], iso(r["cycle"]), str(r["lead"]), iso(r["valid"]), repr(r["raw_gfs"]), repr(r["baseline"]),
            repr(r["b"]), repr(r["corrected"]), r["gfs_version"], r["model_sha256"], r["code_commit"],
            iso(r["issued"])]


def write_log(path, rows):
    """Write one cycle's rows. Refuses to overwrite (LogExists). The folder is made if needed."""
    path = Path(path)
    if path.exists():
        raise LogExists(str(path))
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(LOG_COLUMNS)
    for r in rows:
        w.writerow(row_values(r))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "x", newline="") as f:
        f.write(buf.getvalue())
        f.flush()
        os.fsync(f.fileno())
    try:
        os.link(tmp, path)
    except FileExistsError as e:
        raise LogExists(str(path)) from e
    finally:
        os.unlink(tmp)


def read_log(path):
    """The rows of one log file, with times and numbers parsed."""
    rows = []
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != LOG_COLUMNS:
            raise ValueError(f"{path}: not the log's columns")
        for r in rd:
            rows.append({"airport": r["airport"], "cycle": parse_time(r["cycle_utc"]), "lead": int(r["lead"]),
                         "valid": parse_time(r["valid_utc"]), "raw_gfs": float(r["raw_gfs"]),
                         "baseline": float(r["baseline"]), "b": float(r["b"]), "corrected": float(r["corrected"]),
                         "gfs_version": r["gfs_version"], "model_sha256": r["model_sha256"],
                         "code_commit": r["code_commit"], "issued": parse_time(r["issued_utc"])})
    return rows


def logged_cycles(root, model):
    """The cycles that have a log file, from the file names."""
    out = {}
    base = Path(root) / "log"
    if not base.exists():
        return out
    for p in base.glob("*/*/*.csv"):
        m = _NAME.match(p.name)
        if m and m.group("model") == model:
            out[dt.datetime.strptime(m.group("stamp"), "%Y%m%d%H")] = p
    return out
