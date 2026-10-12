"""The drift tracker (DECISIONS D97.4 to D97.7, D103.6).

b is a decaying average of the baseline's own recent errors (observation minus baseline
forecast). After each new error e: b = (1 - w) x b + w x e, with w = 0.02 (D97.4, NOAA's NAEFS
value, fixed in advance). One tracker per airport, cycle hour and lead (D97.5). The forecast
from the cycle starting at c uses only errors whose valid time is before c, applied in
ascending valid time, each once (D97.6). A missing observation is skipped: the update counts
errors, not calendar days. Errors are always the baseline's, never the corrected forecast's.
Every tracker starts at b = 0 (D97.7, D103.6).

Two ways to run the same arithmetic:
  track(rows)       a batch over one cell's rows in ascending cycle time, a port of
                    scripts/session103_bias_drift_cv.py track (the reference, never edited);
                    Gate B uses it to reproduce F146 and F147.
  advance(cell, errors, cycle)
                    the live step: apply the errors that have arrived and are valid before the
                    cycle, and not yet used. A cell remembers the last valid time applied, so
                    no error is used twice and none out of order.
"""

import bisect
import datetime as dt
from dataclasses import dataclass
from typing import Optional

W = 0.02   # D97.4


def update(b, e, w=W):
    return (1 - w) * b + w * e


@dataclass
class Cell:
    """One tracker's state: b, the valid time of the last error applied, and how many were applied."""
    b: float = 0.0
    last_valid: Optional[dt.datetime] = None
    n: int = 0


def advance(cell, errors, cycle, w=W):
    """The live step. errors: [(valid time, error)] of the baseline rows whose observation has
    arrived. Applies, in ascending valid time, each error with last_valid < valid < cycle, and
    returns the number applied. An error at or before the last valid time applied is never used
    (a late observation cannot be applied out of order)."""
    todo = sorted((v, e) for v, e in errors
                  if v < cycle and (cell.last_valid is None or v > cell.last_valid))
    for v, e in todo:
        cell.b = update(cell.b, e, w)
        cell.last_valid = v
        cell.n += 1
    return len(todo)


def track(rows, w=W):
    """One cell's tracker over rows (cycle, lead, obs, baseline forecast), in ascending cycle
    time; a row's valid time is its cycle plus its lead in hours. Before a row from cycle c is
    corrected, every error not yet applied whose valid time is before c is applied, in ascending
    valid time; then the row's own error (obs minus baseline) is queued.

    Returns, per row, the corrected forecast, the number of errors used and the latest valid time
    used (None if none); and b after all the cell's errors are applied (descriptive, D97.9)."""
    cell = Cell()
    pending = []   # (valid time, error), in ascending valid time
    corrected, n_used, latest_used = [], [], []
    prev = None
    for cycle, lead, obs, fc in rows:
        if prev is not None and not prev < cycle:
            raise ValueError("tracker rows are not in ascending cycle time")
        prev = cycle
        while pending and pending[0][0] < cycle:
            valid, e = pending.pop(0)
            cell.b = update(cell.b, e, w)
            cell.n += 1
            cell.last_valid = valid
        corrected.append(fc + cell.b)
        n_used.append(cell.n)
        latest_used.append(cell.last_valid)
        bisect.insort(pending, (cycle + dt.timedelta(hours=lead), obs - fc))
    for _, e in pending:
        cell.b = update(cell.b, e, w)
    return corrected, n_used, latest_used, cell.b
