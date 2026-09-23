"""Session 70, Task 2 (audit A67-06): add a `station` column to
data/processed/session46_fold_table.csv, without refitting anything.

The fold table has 50 rows (5 airports x 10 folds) but no station column.
scripts/session46_backtest.py (read-only here, not edited) writes the rows
in this order: for each airport in AIRPORTS order (EGLC, LFPG, DSM, YSDU,
RNO), the 4 FOLDS_3 folds, then the 6 FOLDS_5 folds.

Each row's station is confirmed two ways before anything is written:
  1. the write order above;
  2. an exact string match, on every column the two files share, against
     data/processed/session46_backtest_profile.csv (150 rows). The match
     must name exactly one station, and it must agree with (1).
  Exception (owner ruling, session 70): 14 rows are 7 pairs of
  byte-identical rows, so the profile names two stations for each. Those
  are assigned by write order alone (see the tie rule in main()).

Usage:
    .venv/bin/python scripts/session70_fold_table_station.py
        Check only. Writes nothing.
    .venv/bin/python scripts/session70_fold_table_station.py --write
        Same checks, then adds `station` as the first column, in place.
        Every other byte of the file is kept: row order, values, quoting,
        line endings and the trailing newline. Refuses to run if the file
        already has a station column.
"""

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLD_TABLE = ROOT / "data" / "processed" / "session46_fold_table.csv"
PROFILE = ROOT / "data" / "processed" / "session46_backtest_profile.csv"

# From scripts/session46_backtest.py: AIRPORTS order, 4 FOLDS_3, 6 FOLDS_5.
STATIONS = ["EGLC", "LFPG", "DSM", "YSDU", "RNO"]
ROWS_PER_STATION = 10


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    raw = FOLD_TABLE.read_bytes()
    with open(FOLD_TABLE, newline="") as f:
        fold_header, *fold_rows = list(csv.reader(f))
    with open(PROFILE, newline="") as f:
        profile = list(csv.DictReader(f))

    if "station" in fold_header:
        print("STOP: fold table already has a station column")
        sys.exit(1)
    shared = [c for c in fold_header if c in profile[0]]
    print(f"fold table rows: {len(fold_rows)}  profile rows: {len(profile)}")
    print(f"shared columns ({len(shared)}): {shared}")
    if len(fold_rows) != len(STATIONS) * ROWS_PER_STATION:
        print("STOP: row count is not 50")
        sys.exit(1)

    # Owner ruling (session 70): a row that matches more than one station is
    # assigned by write order alone only if (a) the write-order station is
    # among its matches, and (b) the row is byte-identical to another row in
    # the file whose write-order station is the other match. The fold table
    # holds no error metric, so such rows differ only in their station.
    problems = 0
    by_write_order_alone = []
    derived = []
    for i, row in enumerate(fold_rows):
        d = dict(zip(fold_header, row))
        by_order = STATIONS[i // ROWS_PER_STATION]
        matches = sorted({p["station"] for p in profile
                          if all(p[c] == d[c] for c in shared)})
        twins = {STATIONS[j // ROWS_PER_STATION] for j, other in enumerate(fold_rows)
                 if j != i and other == row}
        if matches == [by_order]:
            status = "OK"
        elif by_order in matches and set(matches) == {by_order} | twins:
            status = "OK (tie: byte-identical rows, assigned by write order)"
            by_write_order_alone.append(i + 1)
        else:
            status = "PROBLEM"
            problems += 1
        derived.append(by_order)
        print(f"  row {i + 1:2d}  {d['feature_set']:9s} {d['fold']:12s} "
              f"train_rows={d['train_rows']:>4s} test_rows={d['test_rows']:>3s}  "
              f"write order={by_order:4s}  profile match={matches}  {status}")

    if problems:
        print(f"\nSTOP: {problems} row(s) not confirmed; file not written")
        sys.exit(1)
    print(f"\nAll 50 rows confirmed. {50 - len(by_write_order_alone)} match exactly "
          f"one profile station, agreeing with the write order. "
          f"{len(by_write_order_alone)} are ties assigned by write order alone: "
          f"rows {by_write_order_alone}.")

    if not args.write:
        print("Check mode: nothing written.")
        return

    # Prepend "station," to each line of the original bytes, so nothing
    # else changes. The file has no quoted field containing a newline
    # (checked: the csv reader's row count equals the line count).
    lines = raw.split(b"\r\n")
    if lines[-1] != b"" or len(lines) - 1 != len(fold_rows) + 1:
        print("STOP: unexpected line structure; file not written")
        sys.exit(1)
    labels = [b"station"] + [s.encode() for s in derived]
    new = b"\r\n".join(lab + b"," + line for lab, line in zip(labels, lines[:-1])) + b"\r\n"
    FOLD_TABLE.write_bytes(new)
    print(f"Wrote {FOLD_TABLE.relative_to(ROOT)} with station as the first column.")


if __name__ == "__main__":
    main()
