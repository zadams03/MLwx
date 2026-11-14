"""Session 131: stage B's scoring script with its DECISIONS lookups held as constants (DECISIONS D125.5(d);
register row SB10; D98.2, D116.10).

`scripts/session87_forward_score.py` (frozen) finds F122.5's values by searching the text of DECISIONS.md
and DECISIONS-archive.md: the SHA-256 of `data/models/session81/manifest.json`, and the table of the
twelve frozen models' SHA-256 with each airport's mean-bias constant (its `load_frozen_models`). A later
entry whose text matched first would stop `--score`. Session 87 is frozen and is not edited (D62.3(a),
D116.10). This script imports it, swaps its `read_decisions_text` at run time for a stand-in whose text
holds only F122.5's values, built from the constants below, and runs it unchanged otherwise, as
`session129_stageb_gate.py` does for session 86 (D123.5). No DECISIONS file is read.

tests/test_session131_stageb.py checks each constant against both DECISIONS files, against
`session129_stageb_gate.py`'s constants, and against the committed manifest and model files.

Modes (one per run):
  --check        Offline, read only. Runs session 87's own `load_frozen_models` against the stand-in: the
                 manifest and the twelve model files are checked against the constants and against
                 manifest.json, and the boosters are loaded. No error is computed; nothing is written.
  --guard-check  Session 87's --guard-check, unchanged (it reads no DECISIONS text).
  --gate         Session 87's --gate with the swap (offline, recorded results only, writes nothing
                 under data/).
  --score        Session 87's --score with the swap, with its own arguments, unchanged: --period,
                 --first-v17-cycle or --no-v17, --rows-sha256, --points-sha256, --nbm-versions,
                 --mav-versions and --decision. Its guards and its write-once outputs are session 87's.
                 It is run only at stage B's look (D73.8, D125.5(d)).
"""

import os
import sys

sys.dont_write_bytecode = True
os.environ.setdefault("MLWX_LIBOMP_PATH_SET", "1")   # lightgbm loads without session 87's restart (D93.3)

import argparse  # noqa: E402
import hashlib  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


S87_SCRIPT_SHA256 = "5a6f32c505a5c0a39577a05f2ac82bfac31994f600fe6edbba3f1e936171de6a"   # F129.7, D116.4
if sha256_file(HERE / "session87_forward_score.py") != S87_SCRIPT_SHA256:
    raise SystemExit("STOP: scripts/session87_forward_score.py's SHA-256 is not the recorded one (F129.7)")

import session87_forward_score as s87  # noqa: E402

# F122.5: data/models/session81/manifest.json, and the table of the twelve frozen models:
# the table's airport label -> (rows, `<st>_bdlrt.txt` SHA-256, `<st>_b.txt` SHA-256, mean-bias constant as
# written in the table). The constant is kept as text so that session 87's float() reads exactly the value
# the record holds.
MANIFEST_SHA256 = "03830586c64039814b3d697b414e29ed18a359d9798d87451e8aa3575365c298"
F122_5_TABLE = {
    "EGLC": (1953, "d6a85e45cf948107d45601fca71388102128d1172ddedbf83840f6ee82d15110",
             "fa299dd54908f7d98211bbd1edf2955e8acb493997564c6b30b174522f23a461", "-0.21434203789042497"),
    "LFPG": (1953, "ed3f90b604c9b48a2a50923fd2a67439b25a21255c77d80ae9ca13789e8c8c8e",
             "257c153fec745954f9f2917fe9f4a51d6c8fd662233f5fb5dcb94c2b8b987022", "-0.16713876088069635"),
    "DSM": (1955, "260d6187f8efa4850790528027ee0d3f726a0c4c6b679511bfa891f2de4dff3b",
            "e9cb30bacaf38f9a6b0a602cedc3d9bf2fd2b457bf883d5914316b759264fc9c", "-0.29022710997442464"),
    "YSDU": (1929, "12acbb185d5b927014373a0197b3e6e0ba0be206ff4f434e812bc191976613c3",
             "6e85d56bcead9111f0198b2842ffca8cc308909cc63eea6b36820ead66614a51", "-0.3155987558320373"),
    "RNO": (1952, "c809ccfe9863741d715e8b7167a172d6826cfe6ea78e47a943779d7a7bcb5819",
            "8ce348a6ca583fd3bf203c993f0c10887212e5968cf4d925d05de2b8baf4cb0d", "0.11086936475409828"),
    "KSFO (SFO)": (1952, "c25da039bfbf99db1fd222b171f93a2ea332aaedd828823ed1e09c4d691125f6",
                   "2649548311f3e396de933d1a78650fc6df9001719bab97b929e2002c9af42ca3", "0.02647489754098368"),
}


def record_text():
    """The text session 87's `load_frozen_models` reads, built from the constants only, in the forms its
    two patterns expect (its l.361 and l.367-368)."""
    lines = [f"`manifest.json`, SHA-256 `{MANIFEST_SHA256}`", "**F122.5 (from constants)"]
    lines += [f"| {label} | {rows} | `{bdlrt}` | `{b}` | {mb} |"
              for label, (rows, bdlrt, b, mb) in F122_5_TABLE.items()]
    lines.append("**F122.6")
    return "\n".join(lines) + "\n"


def swap():
    """Session 87 calls read_decisions_text() through its module, so this replaces every lookup."""
    s87.read_decisions_text = record_text


def run_check():
    swap()
    try:
        models, mean_bias, hashes = s87.load_frozen_models()
    except s87.GuardError as e:
        print(f"CHECK: FAIL ({e})")
        return 1
    print(f"manifest.json SHA-256 {hashes['manifest.json']} equal to the constant (F122.5)")
    print(f"model files checked against the constants and manifest.json: {len(hashes) - 1}; boosters loaded: "
          f"{len(models)}; mean-bias constants equal to manifest.json: {len(mean_bias)}")
    ok = len(models) == 12 and len(hashes) == 13 and len(mean_bias) == 6
    print(f"CHECK: {'PASS' if ok else 'FAIL'} (offline; no error computed; nothing written)")
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="offline: the constants against the committed models")
    g.add_argument("--guard-check", action="store_true")
    g.add_argument("--gate", action="store_true")
    g.add_argument("--score", action="store_true")
    # session 87's --score arguments, passed through unchanged
    ap.add_argument("--period", default=None)
    ap.add_argument("--first-v17-cycle", default=None)
    ap.add_argument("--no-v17", action="store_true")
    ap.add_argument("--rows-sha256", default=None)
    ap.add_argument("--points-sha256", default=None)
    ap.add_argument("--nbm-versions", default=None)
    ap.add_argument("--mav-versions", default=None)
    ap.add_argument("--decision", default=None)
    a = ap.parse_args(argv)
    try:
        if a.check:
            return run_check()
        if a.guard_check:
            return s87.guard_check()
        swap()
        print("SESSION 131: session 87 with constants in place of its F122.5 lookups (D125.5(d)).")
        return s87.run_gate(a) if a.gate else s87.run_score(a)
    except s87.GuardError as e:
        print(f"GUARD STOP: {e}")
        return 3


if __name__ == "__main__":
    sys.exit(main())
