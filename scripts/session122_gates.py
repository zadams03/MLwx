"""Session 122: the --gate modes of sessions 92, 95 and 96 with F122.3 held as a constant (DECISIONS D116.3).

Sessions 92, 95 and 96 found F122.3's training-set SHA-256 by searching DECISIONS.md. F122 is archived, so
that search no longer finds it (D98.2, F163 rows C06 and C07). Their SHA-256 is recorded elsewhere, so they
are not edited (D116.10). This script imports them, swaps the one lookup for the constant
`TRAINING_SET_SHA256` in scripts/session91_grib_pull.py (checked against F122.3 by tests/test_record.py),
and runs each gate unchanged otherwise. No DECISIONS file is read.

Modes (exactly one; all offline, read only, nothing written):
  --gate92 --dir D --month M --hours A-B   session 92's --gate on one month
  --gate95                                 session 95's --gate: --gate92 on every month of MLwx-pull/
  --gate96 [--out DIR]                     session 96's --gate on the stage C tables (default MLwx-stagec/)
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")   # lightgbm loads without the shim (D93.3)

import argparse  # noqa: E402
import subprocess  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import session91_grib_pull as p91  # noqa: E402

TRAINING_SET_LINE = "`session81_training_set.csv`, 0 data rows, SHA-256 `{}`"
# The pattern session 96's gate passes to session 86's expected_hash_from_decisions (its l.615).
S96_PATTERN = r"session81_training_set\.csv`,\s+[\d,]+ data rows,\s+SHA-256 `([0-9a-f]{64})`"


class ConstantRecord:
    """Stands in for DECISIONS.md in session 92's gate: its text holds only F122.3's value, from the
    constant, in the form session 92's pattern reads."""

    def read_text(self, *args, **kwargs):
        return TRAINING_SET_LINE.format(p91.TRAINING_SET_SHA256)


def gate92(args):
    import session92_verify_chunk as v92
    p91.DECISIONS_FILE = ConstantRecord()
    hours = p91.parse_hours(args.hours)
    p91.parse_month(args.month)
    return v92.run_gate(args, hours)


def gate95(args):
    import session95_check_release as v95

    def run_verifier(m, extra):
        if extra != ["--gate"]:
            raise SystemExit(f"STOP: session 95 asked for {extra}; only --gate is run here")
        cmd = [sys.executable, str(Path(__file__).resolve()), "--gate92", "--dir", str(v95.PULL_DIR),
               "--month", m, "--hours", v95.HOURS_ARG]
        r = subprocess.run(cmd, capture_output=True, text=True, cwd=HERE,
                           env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        return r.returncode, r.stdout + r.stderr

    v95.run_verifier = run_verifier
    args.raw = False
    try:
        return v95.run_gate(args)
    except v95.Stop as e:
        print(f"\nSTOP: {e}")
        return 2


def gate96(args):
    import session96_stagec_table as s96

    def expected_hash(p):
        if p != S96_PATTERN:
            raise SystemExit(f"STOP: session 96 asked for an unexpected record: {p}")
        return p91.TRAINING_SET_SHA256

    s96.s86.expected_hash_from_decisions = expected_hash
    if args.out is None:
        args.out = str(s96.OUT_DEFAULT)
    return s96.run_gate(args)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("gate92", "gate95", "gate96"):
        g.add_argument(f"--{m}", action="store_true")
    ap.add_argument("--dir", help="--gate92: the directory holding the chunk's three files")
    ap.add_argument("--month", help="--gate92: YYYY-MM")
    ap.add_argument("--hours", help="--gate92: forecast hours A-B, as the chunk was pulled")
    ap.add_argument("--out", default=None, help="--gate96: the table folder (default MLwx-stagec/ beside the repo)")
    a = ap.parse_args()
    if a.gate92 and not (a.dir and a.month and a.hours):
        ap.error("--gate92 needs --dir, --month and --hours")
    print(f"SESSION 122 gates: F122.3 from session 91's TRAINING_SET_SHA256 {p91.TRAINING_SET_SHA256}")
    try:
        if a.gate92:
            return gate92(a)
        if a.gate95:
            return gate95(a)
        return gate96(a)
    except p91.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
