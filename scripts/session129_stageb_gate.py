"""Session 129: session 86's --gate with its DECISIONS lookups held as constants (DECISIONS D123.5, D118.10).

`scripts/session86_forward_build.py --gate` (F128) reads DECISIONS.md for three recorded values: F122.3's
training-set SHA-256, F122.5's `manifest.json` SHA-256 and F122.5's table of the twelve frozen models'
SHA-256. F122 is archived, so those lookups no longer find anything (D96.3, D98.2). Session 86 is frozen
and is not edited (D62.3(a), D116.10). This script imports it, swaps its `DECISIONS_FILE` at run time for a
stand-in whose text holds only those values, built from constants, and runs its gate unchanged otherwise,
as D116.3 did for sessions 92, 95 and 96. No DECISIONS file is read.

The constants: F122.3's training-set SHA-256 is `TRAINING_SET_SHA256` in scripts/session91_grib_pull.py;
F122.5's values are held here. tests/test_session129_stageb_gate.py checks each against both DECISIONS
files and against the committed files.

Modes (one per run):
  --check   Offline, read only. Runs session 86's own three lookups against the stand-in and checks the
            committed training set, manifest and twelve model files against the values found. No
            network call; nothing is written.
  --gate    Session 86's gate, unchanged apart from the swap. NETWORK: it pulls GRIB messages by byte
            range from NOAA's AWS archive and routine reports from IEM, for 54 spent-year station-days
            (nothing valid on or after 2026-08-01; session 86's own guard). It does not need the GRIB
            drive. It writes nothing under data/ (session 86's temporary folder, deleted at the end).

What session 86's gate needs (read from its `run_gate` and `plumbing`): SPEC.md (the airport table of
3.4), the two elevation params CSVs, data/processed/session81_training_set.csv, data/models/session81/
(manifest.json and twelve model files), the packages eccodes, requests, numpy and lightgbm, and the network
as above (about 0.7 GB of GRIB messages, F128.5).
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")   # lightgbm loads without session 86's restart (D93.3)

import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


S86_SCRIPT_SHA256 = "da2ff50c8baa9a7bcbe1c5a6d4787d02e042de250143d3b067d10fcd27594125"   # D116.4
if sha256_file(HERE / "session86_forward_build.py") != S86_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session86_forward_build.py's SHA-256 is not the recorded one (D116.4)")

import session86_forward_build as s86  # noqa: E402
import session91_grib_pull as p91  # noqa: E402

# F122.5: data/models/session81/manifest.json, and the table of the twelve frozen models:
# the table's airport label -> (rows, `<st>_bdlrt.txt` SHA-256, `<st>_b.txt` SHA-256).
MANIFEST_SHA256 = "03830586c64039814b3d697b414e29ed18a359d9798d87451e8aa3575365c298"
F122_5_MODELS = {
    "EGLC": (1953, "d6a85e45cf948107d45601fca71388102128d1172ddedbf83840f6ee82d15110",
             "fa299dd54908f7d98211bbd1edf2955e8acb493997564c6b30b174522f23a461"),
    "LFPG": (1953, "ed3f90b604c9b48a2a50923fd2a67439b25a21255c77d80ae9ca13789e8c8c8e",
             "257c153fec745954f9f2917fe9f4a51d6c8fd662233f5fb5dcb94c2b8b987022"),
    "DSM": (1955, "260d6187f8efa4850790528027ee0d3f726a0c4c6b679511bfa891f2de4dff3b",
            "e9cb30bacaf38f9a6b0a602cedc3d9bf2fd2b457bf883d5914316b759264fc9c"),
    "YSDU": (1929, "12acbb185d5b927014373a0197b3e6e0ba0be206ff4f434e812bc191976613c3",
             "6e85d56bcead9111f0198b2842ffca8cc308909cc63eea6b36820ead66614a51"),
    "RNO": (1952, "c809ccfe9863741d715e8b7167a172d6826cfe6ea78e47a943779d7a7bcb5819",
            "8ce348a6ca583fd3bf203c993f0c10887212e5968cf4d925d05de2b8baf4cb0d"),
    "KSFO (SFO)": (1952, "c25da039bfbf99db1fd222b171f93a2ea332aaedd828823ed1e09c4d691125f6",
                   "2649548311f3e396de933d1a78650fc6df9001719bab97b929e2002c9af42ca3"),
}
TRAINING_ROWS = 11694                                # F122.3: the training set's data rows


def record_text():
    """The text session 86's three lookups read, built from the constants only, in the forms its
    patterns expect (its l.892, l.895 and `plumbing`)."""
    lines = [f"`session81_training_set.csv`, {TRAINING_ROWS:,} data rows, SHA-256 `{p91.TRAINING_SET_SHA256}`",
             f"`manifest.json`, SHA-256 `{MANIFEST_SHA256}`",
             "**F122.5 (from constants)"]
    lines += [f"| {st} | {rows} | `{bdlrt}` | `{b}` |" for st, (rows, bdlrt, b) in F122_5_MODELS.items()]
    lines.append("**F122.6")
    return "\n".join(lines) + "\n"


class ConstantRecord:
    """Stands in for DECISIONS.md inside session 86: its text holds only F122.3's and F122.5's
    values, from the constants."""

    def read_text(self, *args, **kwargs):
        return record_text()


def swap():
    s86.DECISIONS_FILE = ConstantRecord()


def station_of(label):
    return "SFO" if label.startswith("KSFO") else label


def run_check(args):
    """Offline: session 86's own lookups against the stand-in, and the committed files."""
    swap()
    ok = True
    # the two patterns session 86's run_gate passes, read from its source so they cannot drift
    src = (HERE / "session86_forward_build.py").read_text()
    patterns = [ln.split('expected_hash_from_decisions(r"', 1)[1].rsplit('")', 1)[0]
                for ln in src.splitlines() if 'expected_hash_from_decisions(r"' in ln]
    if len(patterns) != 2:
        raise SystemExit(f"STOP: session 86 has {len(patterns)} lookups by pattern, not 2")
    for label, pattern, path in (("training set (F122.3)", patterns[0], s86.TRAINING_SET),
                                 ("manifest.json (F122.5)", patterns[1], s86.MODEL_DIR / "manifest.json")):
        want, have = s86.expected_hash_from_decisions(pattern), sha256_file(path)
        print(f"{label}: constant {want}; committed file {have}; equal: {want == have}")
        ok = ok and want == have
    manifest = json.loads((s86.MODEL_DIR / "manifest.json").read_text())["airports"]
    for label, (_, bdlrt, b) in F122_5_MODELS.items():
        st = station_of(label)
        for kind, want in (("bdlrt", bdlrt), ("b", b)):
            have = sha256_file(s86.MODEL_DIR / f"{st}_{kind}.txt")
            same = have == want == manifest[st][f"model_{kind}_sha256"]
            print(f"{st}_{kind}.txt: equal to the constant and to manifest.json: {same}")
            ok = ok and same
    print(f"CHECK: {'PASS' if ok else 'FAIL'} (offline; session 86's gate was not run)")
    return 0 if ok else 1


def run_gate(args):
    swap()
    print("SESSION 129: session 86's --gate with constants in place of its DECISIONS lookups (D123.5).")
    print(f"F122.3 from session 91's TRAINING_SET_SHA256 {p91.TRAINING_SET_SHA256}; F122.5's manifest "
          f"{MANIFEST_SHA256} and twelve model SHA-256 held in this script.")
    return s86.run_gate(args)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="offline: the lookups and the committed files")
    g.add_argument("--gate", action="store_true", help="session 86's gate (network: NOAA's AWS archive and IEM)")
    ap.add_argument("--workers", type=int, default=4, help="--gate: as session 86's --workers")
    a = ap.parse_args(argv)
    try:
        return run_check(a) if a.check else run_gate(a)
    except s86.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
