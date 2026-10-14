"""The product refit (DECISIONS D103.5): a build step, not a test. Nothing is scored.

For each airport of gfs_airports.csv (or the airports named), one model per cycle hour and lead 3
to 48 (184 per airport), by SPEC 9.3's structure and section 8's settings, on every complete-case row
valid up to 2026-07-31 (spent years and the claim airports' look years included). The models are
then frozen: v1 does no retraining. The 12 airports of D103.4 read their stage C tables
(MLwx-stagec/, --tables); the onboarded airports read their own tables (--new-tables, built by
mlwx.onboard), D105.8. Each file is checked against its recorded SHA-256 (records.py) before it is
read. --check-only checks every table and fits nothing.

Output, into a new folder: one file per airport and cycle hour (baseline.pack_bytes), and
manifest.txt (file, SHA-256). The SHA-256 of manifest.txt is the models' one identifier
(baseline.MANIFEST_SHA256). Nothing is written over: the output folder must not exist.

    python -m mlwx.refit --tables ../MLwx-stagec --out ../MLwx-live-build/models
    python -m mlwx.refit --tables ../MLwx-stagec --new-tables ../MLwx-live-build/tables --check-only
"""

import argparse
import datetime as dt
import hashlib
import sys
import time
from pathlib import Path

from . import baseline, config, records, tables

LEADS_A = tuple(range(3, 25))
LEADS_B = tuple(range(25, 49))
HOUR_SETS = (("f000_024", LEADS_A), ("f025_048", LEADS_B))


def table_files(a, table_dir, new_table_dir=None):
    """[(path, station, leads)] of one airport's two tables, each checked against its recorded SHA-256.
    Stage C tables come from table_dir, an onboarded airport's from new_table_dir (D105.8)."""
    folder = table_dir if records.has_stagec_tables(a) else new_table_dir
    if folder is None:
        raise SystemExit(f"STOP: {a.icao} is an onboarded airport; its tables need --new-tables")
    files = []
    for hs, leads in HOUR_SETS:
        path = Path(folder) / records.table_name(a, hs)
        got = tables.sha256_file(path)
        if got != records.recorded_sha(a, hs):
            raise SystemExit(f"STOP: {path.name} SHA-256 {got} is not the recorded {records.recorded_sha(a, hs)}")
        files.append((path, a.station, leads))
    return files


def check_tables(table_dir, new_table_dir=None, airports=None, model=None):
    """Check every table of the airports (default: all of gfs_airports.csv) against its record; fit
    nothing. Returns [(icao, file name)]; stops at the first table that does not match."""
    airports = airports or config.load_airports(model or config.GFS)
    return [(a.icao, p.name) for a in airports for p, _, _ in table_files(a, table_dir, new_table_dir)]


def train_cells(a, table_dir, new_table_dir=None):
    """{(cycle hour, lead): [(cycle, x, temp, obs)]} of one airport's complete-case rows, ascending in cycle."""
    files = table_files(a, table_dir, new_table_dir)
    cells = baseline.training_rows(files)
    for (h, n), rows in cells.items():
        if rows[-1][0] + dt.timedelta(hours=n) > baseline.LAST_TRAIN_VALID:
            raise SystemExit(f"STOP: {a.icao} {h}z lead {n} holds a row valid after 2026-07-31T23:00")
    return cells


def refit(table_dir, out_dir, airports=None, log=print, model=None, new_table_dir=None):
    out = Path(out_dir)
    if out.exists():
        raise SystemExit(f"STOP: {out} already exists; not writing into it")
    model = model or config.GFS
    airports = airports or config.load_airports(model)
    entries, info = {}, []
    out.mkdir(parents=True)
    t0 = time.time()
    for a in airports:
        cells = train_cells(a, table_dir, new_table_dir)
        for h in model.cycle_hours:
            models = {}
            for n in range(model.curve_first_lead, model.last_lead + 1):
                rows = cells.get((h, n))
                if not rows:
                    raise SystemExit(f"STOP: {a.icao} {h}z lead {n}: no training rows")
                models[n] = baseline.fit([(r[1], r[2], r[3]) for r in rows])
                info.append((a.icao, h, n, len(rows)))
            data = baseline.pack_bytes(a.icao, h, models)
            name = baseline.pack_name(model.name, a.icao, h)
            tables.write_new_file(out / name, data)
            entries[name] = hashlib.sha256(data).hexdigest()
        log(f"  {a.icao}: {len(model.cycle_hours)} files, {len(model.cycle_hours) * len(range(model.curve_first_lead, model.last_lead + 1))} models ({time.time() - t0:.0f} s)")
    text = baseline.manifest_text(entries)
    (out / baseline.MANIFEST_NAME).write_text(text)
    return entries, baseline.manifest_sha256(text), info


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fit the frozen product models (D103.5).")
    ap.add_argument("--tables", required=True, help="folder with the stage C tables (MLwx-stagec)")
    ap.add_argument("--new-tables", help="folder with the onboarded airports' tables (D105.8)")
    ap.add_argument("--out", help="new folder for the models and their manifest")
    ap.add_argument("--info", help="optional file for the training-row counts (written once)")
    ap.add_argument("--check-only", action="store_true", help="check every table against its record; fit nothing")
    ap.add_argument("airports", nargs="*", help="ICAO codes (default: every airport of gfs_airports.csv)")
    a = ap.parse_args(argv)
    every = config.load_airports(config.GFS)
    by_icao = {x.icao: x for x in every}
    unknown = [c for c in a.airports if c not in by_icao]
    if unknown:
        raise SystemExit(f"STOP: not in gfs_airports.csv: {' '.join(unknown)}")
    airports = [by_icao[c] for c in a.airports] or every
    if a.check_only:
        checked = check_tables(a.tables, a.new_tables, airports)
        print(f"airports {len(airports)}; tables checked {len(checked)}; all equal to their record")
        return 0
    if not a.out:
        ap.error("--out is needed unless --check-only")
    entries, sha, info = refit(a.tables, a.out, airports, new_table_dir=a.new_tables)
    total = sum((Path(a.out) / n).stat().st_size for n in entries)
    print(f"files {len(entries)}; models {len(info)}; total size {total:,} bytes; manifest SHA-256 {sha}")
    if a.info:
        with open(a.info, "x") as f:
            f.write("airport,cycle_hour,lead,train_rows\n")
            for row in info:
                f.write(",".join(str(x) for x in row) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
