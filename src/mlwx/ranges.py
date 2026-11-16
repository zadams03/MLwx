"""The frozen 80 % ranges of the 12 airports, for the page (DECISIONS D129.4, D129.10).

`data/gfs_ranges.csv` was written once by scripts/session134_freeze_ranges.py: per airport and output
(hourly, daily_max), a pair (P10, P90) for the range (around the corrected value) and for the
reference (around raw GFS). They are build values, not results, and are not yet verified.

The file's SHA-256 is held here as a constant (D98.2). `load` returns the table only if the file
exists and has that SHA-256; otherwise it returns None, and the page then shows no range and says
so. It never raises: a problem with this file must never stop a run (D129.10). Standard library
only; reads one file; changes no logged value.
"""

import csv
import hashlib
import io
from pathlib import Path

RANGES_FILE = Path(__file__).resolve().parent / "data" / "gfs_ranges.csv"
# Session 134's freeze (F178). The range test always scores the file at this SHA-256 (D129.4).
RANGES_SHA256 = "e8ab9438b390c3c45de0821c8823a98e2ffa9adc42d6a4f19b396af11e2c9eba"
COLUMNS = ["airport", "output", "kind", "p10", "p90", "n"]


def load(path=None, sha256=RANGES_SHA256):
    """{(airport, output, kind): (p10, p90)} if the file exists and its SHA-256 equals `sha256`,
    else None. `output` is hourly or daily_max; `kind` is range or reference."""
    try:
        data = Path(RANGES_FILE if path is None else path).read_bytes()
        if hashlib.sha256(data).hexdigest() != sha256:
            return None
        rd = csv.DictReader(io.StringIO(data.decode("utf-8")))
        if rd.fieldnames != COLUMNS:
            return None
        return {(r["airport"], r["output"], r["kind"]): (float(r["p10"]), float(r["p90"])) for r in rd}
    except Exception:       # a missing or unreadable file gives no ranges, never a stopped run
        return None
