"""The frozen scripts' SHA-256 (DECISIONS D116.4; F163.4, register rows S02 to S04).
Offline; reads only the eight frozen scripts.

The scripts are never edited (D62.3(a), D70.6, D80.1); this test shows they
have not changed. Each value is held as a constant (D98.2), with where it is
recorded.

Run from the repo root: .venv/bin/python -m unittest discover -s tests
"""

import hashlib
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

FROZEN_SHA256 = {
    # notes/session-83-output.txt l.160
    "session39_sealed_test.py":
        "375e4eb69bb06c006a97a4474abce0a6027670123093dc0df3cb5bc0c9da5fca",
    # D116.4: computed in session 122; one git commit (74e7077), unchanged since added
    "session48_reserved_year.py":
        "df36fa5af79b60911fb489e65f9d04c747241a1ab130ff2f1d5ce25edaf131e0",
    # D116.4: computed in session 122; one git commit (0e29835), unchanged since added
    "session60_combine_design.py":
        "0328d08063b618922ce99704f604ff8abdae0c812fab2dd09f02c8f53e66cc7b",
    # D70.2, F109, F118, F119
    "session62_reserved_confirm.py":
        "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4",
    # D70.6, F118, F119
    "session77_ksfo_looks.py":
        "e4ec113b0dcbc936550b382ffbcdd55d3049878c8b13d74cd83e867a6b3247c1",
    # notes/session-86-output.txt l.149
    "session86_forward_build.py":
        "da2ff50c8baa9a7bcbe1c5a6d4787d02e042de250143d3b067d10fcd27594125",
    # F129.7
    "session87_forward_competitors.py":
        "8f176562954b5b43bdf110bc292f5b04d6d728d2295df9a178d5a5ff5b23d55c",
    # F129.7
    "session87_forward_score.py":
        "5a6f32c505a5c0a39577a05f2ac82bfac31994f600fe6edbba3f1e936171de6a",
}


class FrozenScripts(unittest.TestCase):
    """Each frozen script's SHA-256 equals its recorded value."""

    def test_eight_frozen_scripts(self):
        self.assertEqual(len(FROZEN_SHA256), 8)

    def test_sha256_unchanged(self):
        for name, want in FROZEN_SHA256.items():
            with self.subTest(script=name):
                have = hashlib.sha256((SCRIPTS / name).read_bytes()).hexdigest()
                self.assertEqual(have, want)


if __name__ == "__main__":
    unittest.main()
