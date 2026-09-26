"""Session 76b: shared helper. Selects the cached GRIB copies that stand in
for session 76's discarded raw messages (docs/session-76b.md amendment,
2026-09-26).

A cached file is used only if:
- its target date is before 2024-08-01 (the selection is made from session
  76's manifest rows, filtered by date first; no directory is listed);
- session 76's manifest row for that message is OK; and
- its SHA-256, re-computed at load, equals that manifest row's SHA-256.
Any other file is skipped and reported, never used.

Offline. Reads only; writes nothing.
"""

import csv
import datetime as dt
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "data" / "raw" / "diagnostics" / "session76" / "session76_pull_manifest.csv"
GRIB = ROOT / "data" / "raw" / "grib"
S72 = GRIB / "session72"
CUTOFF = dt.date(2024, 8, 1)   # KSFO's held-out range starts here (D67.6)

# session 76 field -> (cache folder, file-name suffix after gfs_<run>_t18z_)
CACHE = {
    "tmp2m": (GRIB, "f026_tmp2m"), "tcdc": (GRIB, "f026_tcdc"),
    "ugrd10m": (GRIB, "f026_ugrd10m"), "vgrd10m": (GRIB, "f026_vgrd10m"),
    "t925": (S72, "f026_TMP_925mb"), "t850": (S72, "f026_TMP_850mb"), "t700": (S72, "f026_TMP_700mb"),
    "rh2m": (S72, "f026_RH_2m"), "dpt2m": (S72, "f026_DPT_2m"), "spfh2m": (S72, "f026_SPFH_2m"),
    "prmsl": (S72, "f026_PRMSL_msl"), "pres_sfc": (S72, "f026_PRES_surface"),
    "dswrf": (S72, "f026_DSWRF_surface"), "prmsl_m3": (S72, "f023_PRMSL_msl"),
}


def manifest_rows(fields=None):
    """Session 76 manifest rows dated before 2024-08-01 only. The date filter
    runs on each row as it is read, before anything else looks at it."""
    out = []
    with open(MANIFEST) as f:
        for r in csv.DictReader(f):
            if dt.date.fromisoformat(r["target_date"]) >= CUTOFF:
                continue
            if fields is None or r["field"] in fields:
                out.append(r)
    return out


def cached_messages(fields=None):
    """Yield (manifest_row, bytes) for every usable cached message, and
    collect the skipped ones. Returns (list_of_pairs, skipped, counts)."""
    pairs, skipped = [], []
    for r in manifest_rows(fields):
        run = dt.date.fromisoformat(r["run_date"])
        assert run < CUTOFF, run
        folder, suffix = CACHE[r["field"]]
        path = folder / f"gfs_{run:%Y%m%d}_t18z_{suffix}.grib2"
        if r["status"] != "OK":
            skipped.append((r["target_date"], r["field"], "session 76 manifest FAIL",
                            "cache present" if path.exists() else "cache absent"))
            continue
        if not path.exists():
            skipped.append((r["target_date"], r["field"], "cache file missing", str(path.relative_to(ROOT))))
            continue
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != r["sha256"]:
            skipped.append((r["target_date"], r["field"], "SHA-256 does not match manifest",
                            str(path.relative_to(ROOT))))
            continue
        pairs.append((r, data))
    return pairs, skipped
