"""The files the live test's frozen scoring script imports or reads, pinned
(DECISIONS D125.4; register rows LS09, LS10, LS12, TE03).

`scripts/session129_live_score.py` is frozen (D123.2), but it imports
`src/mlwx` as it is on the day of the look. Until both looks of D105.5 are
run, these seven files are held at their bytes at commit 3bf156f. Each
value is held as a constant (D98.2); each was checked equal to
`git show 3bf156f:<path> | shasum -a 256` in session 131, Step 1.

A change to any of them is recorded in DECISIONS first, this file's value
is updated in the same session, and `session129_live_score.py --gate` is
run again and must pass (D125.4). Offline; reads only the seven files.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import csv
import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent

PINNED_SHA256 = {
    "src/mlwx/observations.py":
        "a0d95d515ecf23209c3a4b0f7e79a05299f30717228399067549d65569c6e6dc",
    "src/mlwx/dailymax.py":
        "fce6bd63a8167ebac28c98f60d5cd281140caac1fd1363ca551f266851b6754c",
    "src/mlwx/prediction_log.py":
        "5a47b9b50fb683e5bda2797d080c0d0decae8eb3c329fc9fd4bfcd052c90ae26",
    "src/mlwx/config.py":
        "ad1d8a4e0640be3c471cfb818b6472302e95077108ae88d323ff864b30176bdc",
    "src/mlwx/records.py":
        "73dfa8a856e1915ee8cf097fcbdb32cd89b3860df451fbad9d58491396333112",
    "src/mlwx/data/gfs_airports.csv":
        "d5a132237c7f7361e75b32ad7a82ae03a47a3560b7dc0e425b0fedcf529f26d1",
    "data/processed/session111_new_tables.csv":
        "a8d3d1f6ca6842d170c4bd42fd88ece5d9a63b015d90c003c834322981423933",
}

# D125.4 (LS12): all 49 airports stay in gfs_airports.csv until both looks.
AIRPORT_ROWS = 49


class PinnedFiles(unittest.TestCase):
    """Each pinned file's SHA-256 equals its value at 3bf156f."""

    def test_seven_pinned_files(self):
        self.assertEqual(len(PINNED_SHA256), 7)

    def test_sha256_unchanged(self):
        for path, want in PINNED_SHA256.items():
            with self.subTest(path=path):
                have = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
                self.assertEqual(have, want)

    def test_all_49_airports_kept(self):
        with open(ROOT / "src/mlwx/data/gfs_airports.csv", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(len(rows), AIRPORT_ROWS)


if __name__ == "__main__":
    unittest.main()
