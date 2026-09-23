"""Session 70, Task 1 (audit A67-01, DECISIONS D62.4): build committed
provenance manifests for the session 37 and session 40 GRIB pulls.

The provenance for those two pulls (URL, byte range, pull time, bytes saved)
sits only in the per-message `.grib2.meta.txt` sidecars inside the
gitignored cache `data/raw/grib/` (D47). This script copies it, verbatim,
into one committed CSV per pull.

Read-only against every existing file. It reads only the sidecar text files
and the two failure CSVs. It never opens a `.grib2` file (it only checks
that one exists beside each sidecar). No network.

Usage:
    .venv/bin/python scripts/session70_grib_manifests.py
        Inventory and reconcile only. Writes nothing.
    .venv/bin/python scripts/session70_grib_manifests.py --write
        Same checks, then writes the two manifests and copies the two
        failure CSVs byte-for-byte into data/raw/diagnostics/session37/ and
        session40/. Refuses to overwrite any file that already exists.
    .venv/bin/python scripts/session70_grib_manifests.py --write --out-dir DIR
        Same, but writes under DIR instead (used for the re-run check).

Row order in each manifest: sorted by `sidecar_path` (the sidecar's file
name). The name encodes run date, cycle, lead and variable, so this is also
chronological.
"""

import argparse
import csv
import shutil
import sys
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data" / "raw" / "grib"
DIAG = ROOT / "data" / "raw" / "diagnostics"

# The two pull windows, by target (validity) date (SPEC 4.3, D48.8).
WINDOWS = {
    "session37": (date(2021, 3, 24), date(2025, 7, 31)),
    "session40": (date(2025, 8, 1), date(2026, 7, 31)),
}

# Counts recorded in the archive. Copied from DECISIONS-archive.md only.
#   F90 (session 37): 6,364 files, 25,456 messages targeted, 25,444 fetched,
#       12 failed (3 combos x 4 variables), each failing on both the
#       original run and a clean re-run.
#   F92 (session 40): 1,460 files, 5,840 messages, all fetched, 0 failures.
ARCHIVED = {
    "session37": {"files": 6364, "targeted": 25456, "fetched": 25444, "failed": 12},
    "session40": {"files": 1460, "targeted": 5840, "fetched": 5840, "failed": 0},
}

SEALED_NOTE = "sealed test year pull (session 40, D48.8) -- SPEC 4.3"

# The labelled lines every sidecar holds, in order, and their CSV columns.
# `stations` matches the column name the later *_pull_manifest.csv files use.
LINE_KEYS = [
    ("source: ", "source"),
    ("idx source: ", "idx_source"),
    ("byte range requested: ", "byte_range_requested"),
    ("variable: ", None),  # split into four parts below
    ("used by airports (target hour, cycle+lead convention): ", "stations"),
    ("pulled (UTC): ", "pulled_utc"),
    ("bytes saved: ", "bytes_saved"),
    ("first 4 bytes: ", None),  # split into two parts below
]

COLUMNS = [
    "sidecar_path", "source", "idx_source", "byte_range_requested",
    "variable", "lead", "cycle", "run_date", "stations", "pulled_utc",
    "bytes_saved", "first_4_bytes", "last_4_bytes", "note",
]


class Stop(Exception):
    """A mismatch: report it and stop. Nothing is written."""


def parse_sidecar(path):
    """Return one manifest row, every value a verbatim substring of the file."""
    text = path.read_text()
    if not text.endswith("\n"):
        raise Stop(f"{path.name}: no trailing newline")
    lines = text[:-1].split("\n")
    if len(lines) not in (8, 9):
        raise Stop(f"{path.name}: {len(lines)} lines, expected 8 or 9")
    row = {"sidecar_path": path.name}
    for (prefix, col), line in zip(LINE_KEYS, lines):
        if not line.startswith(prefix):
            raise Stop(f"{path.name}: line {line!r} does not start {prefix!r}")
        value = line[len(prefix):]
        if col is not None:
            row[col] = value
        elif prefix == "variable: ":
            # "<var>, forecast hour fNNN, cycle HHz, run date YYYY-MM-DD"
            parts = value.split(", ")
            if (len(parts) != 4 or not parts[1].startswith("forecast hour ")
                    or not parts[2].startswith("cycle ")
                    or not parts[3].startswith("run date ")):
                raise Stop(f"{path.name}: unexpected variable line {line!r}")
            row["variable"] = parts[0]
            row["lead"] = parts[1][len("forecast hour "):]
            row["cycle"] = parts[2][len("cycle "):]
            row["run_date"] = parts[3][len("run date "):]
            rebuilt = (f"{row['variable']}, forecast hour {row['lead']}, "
                       f"cycle {row['cycle']}, run date {row['run_date']}")
            if rebuilt != value:
                raise Stop(f"{path.name}: variable line does not round-trip")
        else:
            # "b'GRIB'  last 4 bytes: b'7777'"
            first, sep, last = value.partition("  last 4 bytes: ")
            if not sep:
                raise Stop(f"{path.name}: unexpected bytes line {line!r}")
            row["first_4_bytes"], row["last_4_bytes"] = first, last
            if f"{first}  last 4 bytes: {last}" != value:
                raise Stop(f"{path.name}: bytes line does not round-trip")
    row["note"] = lines[8] if len(lines) == 9 else ""
    if row["note"] not in ("", SEALED_NOTE):
        raise Stop(f"{path.name}: unexpected 9th line {row['note']!r}")
    return row


def validity_date(row):
    """Target (validity) date = run date + cycle hours + lead hours."""
    run = datetime.strptime(row["run_date"], "%Y-%m-%d")
    cycle = int(row["cycle"].rstrip("z"))
    lead = int(row["lead"].lstrip("f"))
    return (run + timedelta(hours=cycle + lead)).date()


def assign(row):
    """Assign a sidecar to one pull by its validity date, then cross-check
    against the sealed-year note line. Stop if ambiguous or inconsistent."""
    vd = validity_date(row)
    hits = [p for p, (a, b) in WINDOWS.items() if a <= vd <= b]
    if len(hits) != 1:
        raise Stop(f"{row['sidecar_path']}: validity date {vd} fits {len(hits)} windows")
    pull = hits[0]
    has_note = row["note"] == SEALED_NOTE
    if has_note != (pull == "session40"):
        raise Stop(f"{row['sidecar_path']}: sealed-year note does not match window {pull}")
    return pull


def read_failures(path):
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    return rows[0], rows[1:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--out-dir", type=Path, default=DIAG)
    args = ap.parse_args()

    # --- Step 1.2: inventory (read-only) ---
    if not CACHE.is_dir():
        raise Stop(f"cache not found: {CACHE}")
    sidecars = sorted(CACHE.glob("*.grib2.meta.txt"))
    print(f"cache: {CACHE.relative_to(ROOT)}")
    print(f"sidecars found: {len(sidecars)}")

    by_pull = {"session37": [], "session40": []}
    missing_grib = 0
    for p in sidecars:
        row = parse_sidecar(p)
        by_pull[assign(row)].append(row)
        if not (CACHE / p.name[: -len(".meta.txt")]).exists():
            missing_grib += 1
    print(f"sidecars with no .grib2 file beside them: {missing_grib}")
    if missing_grib:
        raise Stop("a sidecar has no matching .grib2 file")

    failures = {}
    for pull in by_pull:
        fpath = CACHE / f"{pull}_pull_failures.csv"
        if not fpath.exists():
            raise Stop(f"failure CSV missing: {fpath}")
        header, frows = read_failures(fpath)
        failures[pull] = (fpath, header, frows)

    # --- Step 1.3: reconcile against the archived counts ---
    print("\nAssignment and reconciliation, per pull:")
    ok = True
    for pull, rows in by_pull.items():
        a = ARCHIVED[pull]
        vdates = [validity_date(r) for r in rows]
        files = Counter((r["run_date"], r["cycle"], r["lead"]) for r in rows)
        pulled = sorted(r["pulled_utc"] for r in rows)
        fpath, header, frows = failures[pull]
        fail_keys = Counter((r[0], r[1], r[2], r[3]) for r in frows)
        distinct_fail = len(fail_keys)
        fail_files = {k[:3] for k in fail_keys}
        # A failure must not also have a sidecar (fetched and failed at once).
        sidecar_keys = {(r["run_date"], f"{int(r['cycle'].rstrip('z'))}",
                         f"{int(r['lead'].lstrip('f'))}",
                         r["sidecar_path"].split("_")[-1].split(".")[0]) for r in rows}
        overlap = sum(1 for k in fail_keys if k in sidecar_keys)

        print(f"\n  {pull}  (archived: {'F90' if pull == 'session37' else 'F92'})")
        print(f"    validity dates: {min(vdates)} .. {max(vdates)}  (window {WINDOWS[pull][0]} .. {WINDOWS[pull][1]})")
        print(f"    distinct validity days: {len(set(vdates))}")
        print(f"    pull times: {pulled[0]} .. {pulled[-1]}")
        print(f"    sealed-year note line present: {sum(r['note'] == SEALED_NOTE for r in rows)} of {len(rows)}")
        print(f"    failure CSV: {fpath.name}, header {header}, data rows {len(frows)}")

        # Files where every message failed, so no sidecar exists for them.
        sidecar_files = {k[:3] for k in sidecar_keys}
        wholly_failed = fail_files - sidecar_files
        checks = [
            ("sidecars vs messages fetched", len(rows), a["fetched"]),
            ("distinct failed messages vs messages failed", distinct_fail, a["failed"]),
            ("sidecars + distinct failed vs messages targeted", len(rows) + distinct_fail, a["targeted"]),
            ("files with a sidecar + files with no sidecar (all failed) vs files",
             len(files) + len(wholly_failed), a["files"]),
        ]
        for name, got, want in checks:
            flag = "OK" if got == want else "MISMATCH"
            ok &= got == want
            print(f"    {name}: {got} vs {want}  {flag}")

        per_file = Counter(files.values())
        print(f"    sidecars per file: {dict(sorted(per_file.items()))}")
        if set(per_file) != {4}:
            ok = False
            print("    MISMATCH: some file does not have exactly 4 sidecars")

        times = Counter(fail_keys.values())
        print(f"    failure-log rows: {len(frows)} = {distinct_fail} distinct messages; "
              f"rows per message: {dict(sorted(times.items()))}")
        print(f"    failed messages that also have a sidecar: {overlap}")
        if overlap:
            ok = False
        if frows and set(times) != {2}:
            ok = False
            print("    MISMATCH: failure-log rows are not exactly 2 per failed message")
        if frows:
            reasons = Counter(r[5] for r in frows)
            stations = sorted({r[4] for r in frows})
            print(f"    failure reasons: {dict(reasons)}")
            print(f"    failure stations: {stations}; failing files: {sorted(fail_files)}")

    if not ok:
        raise Stop("counts do not reconcile; no manifest written")
    print("\nAll counts reconcile exactly.")

    if not args.write:
        print("\nCheck mode: nothing written. Re-run with --write to build.")
        return

    # --- Step 1.4: build ---
    for pull, rows in by_pull.items():
        folder = args.out_dir / pull
        manifest = folder / f"{pull}_pull_manifest.csv"
        fail_copy = folder / f"{pull}_pull_failures.csv"
        for target in (manifest, fail_copy):
            if target.exists():
                raise Stop(f"target already exists, not overwriting: {target}")
    for pull, rows in by_pull.items():
        folder = args.out_dir / pull
        folder.mkdir(parents=True, exist_ok=True)
        manifest = folder / f"{pull}_pull_manifest.csv"
        rows = sorted(rows, key=lambda r: r["sidecar_path"])
        with open(manifest, "x", newline="") as f:
            w = csv.DictWriter(f, fieldnames=COLUMNS)
            w.writeheader()
            w.writerows(rows)
        shutil.copyfile(failures[pull][0], folder / f"{pull}_pull_failures.csv")
        blanks = {c: sum(1 for r in rows if r[c] == "") for c in COLUMNS}
        print(f"\nwrote {manifest}  ({len(rows)} rows)")
        print(f"  blank fields per column: {blanks}")
        print(f"copied {failures[pull][0].name} -> {folder / (pull + '_pull_failures.csv')}")


if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print(f"\nSTOP: {e}")
        sys.exit(1)
