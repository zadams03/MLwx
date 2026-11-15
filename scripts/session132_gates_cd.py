#!/usr/bin/env python3
"""Session 132: Gates C and D on the 12 record airports (DECISIONS D127.4, F154.9(4)).

Session 109's Gates C and D loop over every configured airport (now 49), but the record's pull extracts
and the gates' design cover only the 12 airports of D103.4. This wrapper imports
scripts/session109_gates.py read-only, after checking its SHA-256 against D127.4's value (D116.10), sets
that module's AIRPORTS to this file's RECORD_AIRPORTS at run time, and runs run_gate_c and run_gate_d
unchanged. No function of session 109 is changed.

Modes (exactly one):
  --count    Offline. Prints how many airports session109_gates.AIRPORTS holds, and that RECORD_AIRPORTS is
             the 12 of D103.4, by ICAO.
  --gate-c   Network: the AWS GFS archive only. Session 109's Gate C on the 12 airports.
  --gate-d   Network: IEM only. Session 109's Gate D on the 12 airports.

Nothing is written by any mode. No em-dashes in any text here (D76.6).
"""

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent

S109_SHA256 = "8ac5a567fb4356db61136db4db7783eae381500a2f0314ad9d5a08cee726f59b"   # D127.4

# The 12 airports of D103.4: the development airports, then the claim airports.
RECORD_ICAOS = ["EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO", "EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN"]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256_file(HERE / "session109_gates.py") != S109_SHA256:
    raise SystemExit("STOP: scripts/session109_gates.py's SHA-256 is not D127.4's value")
sys.path.insert(0, str(HERE))
import session109_gates as s109  # noqa: E402

CONFIGURED = list(s109.AIRPORTS)                     # every configured airport, kept for --count
RECORD_AIRPORTS = [a for a in CONFIGURED if a.icao in RECORD_ICAOS]
if sorted(a.icao for a in RECORD_AIRPORTS) != sorted(RECORD_ICAOS):
    raise SystemExit("STOP: the configured airports do not hold the 12 record airports")


def use_record_airports():
    """Set session 109's module constant at run time (D127.4); its functions read it when called."""
    s109.AIRPORTS = RECORD_AIRPORTS


def run_count():
    print(f"session109_gates.AIRPORTS holds {len(CONFIGURED)} airports (every configured airport)")
    print(f"RECORD_AIRPORTS holds {len(RECORD_AIRPORTS)}: " + ", ".join(a.icao for a in RECORD_AIRPORTS))
    same = sorted(a.icao for a in RECORD_AIRPORTS) == sorted(RECORD_ICAOS)
    print(f"equal to the 12 of D103.4: {same}")
    also = sorted(a.icao for a in s109.RECORD_AIRPORTS) == sorted(RECORD_ICAOS)
    print(f"equal to session 109's own Gate A list (RECORD_AIRPORTS there): {also}")
    return 0 if same and len(RECORD_AIRPORTS) == 12 else 1


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for name in ("count", "gate-c", "gate-d"):
        g.add_argument("--" + name, action="store_true")
    a = ap.parse_args()
    if a.count:
        return run_count()
    use_record_airports()
    print(f"SESSION 132 wrapper: session109_gates.AIRPORTS set to the {len(s109.AIRPORTS)} record airports")
    if a.gate_c:
        return s109.run_gate_c(a)
    return s109.run_gate_d(a)


if __name__ == "__main__":
    sys.exit(main())
