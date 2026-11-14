"""Session 131: is stage B's build accepted? (DECISIONS D125.5(b); register row SB07.)

`scripts/session86_forward_build.py --build` (frozen) records a GRIB request that failed after its three
tries as a failure of that field, drops the station-day as "no GRIB message", and goes on; its outputs are
written once. D125.5(b): the build is accepted only if no station-day was dropped for a fetch failure. A
field absent from the archive is a real absence and stays a counted drop. Otherwise the build's outputs are
moved aside and kept, and the build is run again before any score. This script says which. It reads only
the drop log and the GRIB manifest that session 86 wrote (station, date, field, status and the failure's
text; no value), and writes nothing.

How a drop is classed. Session 86's drop log names only the fields of a "no GRIB message" drop, so the
reason is read from the manifest's FAIL rows for that station and day (its `pull_station_day`):
  absent  the archive does not hold it: an HTTP 404 on the .idx or the message, or an .idx with no line
          for the field ("expected 1 idx line for ..., found 0");
  data    the bytes arrived but are not usable: a decode failure, or an .idx with two or more lines for
          the field or the wrong run stamp (a layout question for the owner, not a network one);
  fetch   every other failure of an .idx or message request (a network error, an HTTP 5xx after three
          tries, a short body, bad GRIB markers, an .idx that is not an .idx), and any text this script
          does not recognise (it never passes a build on a doubt).
A station-day is a fetch drop if any of its failed fields is. PASS needs: no fetch drop; every "no GRIB
message" drop matched by FAIL rows and every FAIL row matched by such a drop.

Usage:
  python3 scripts/session131_stageb_build_check.py                  # session 86's own output paths
  python3 scripts/session131_stageb_build_check.py --drops P --manifest Q
Exit code 0 for PASS, 1 for FAIL (the build is not accepted), 2 if a file is missing or not in session 86's
form.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
# session 86's output paths and columns (session86_forward_build.py l.104-105, l.553-554, l.792), held
# here so that this check needs none of session 86's packages; a test checks them equal to session 86's.
DEFAULT_DROPS = ROOT / "data/raw/diagnostics/forward2627/periodA_drop_log.csv"
DEFAULT_MANIFEST = ROOT / "data/raw/diagnostics/forward2627/periodA_grib_manifest.csv"
DROP_COLS = ["station", "target_date", "reason", "detail"]
MAN_COLS = ["station", "target_date", "field", "run_date", "cycle", "fhour", "variable", "level", "idx_step",
            "url", "byte_range", "idx_url", "idx_sha256", "pulled_utc", "bytes", "sha256", "status", "detail"]
GRIB_DROP = "no GRIB message"

ABSENT_IDX_LINE = re.compile(r"^RuntimeError\('expected 1 idx line for .*, found 0'\)$")
LAYOUT = re.compile(r"^RuntimeError\('(expected 1 idx line for .*, found [2-9]\d*|idx run stamp .* does not match "
                    r"the run)'\)$")


class FormError(Exception):
    """A file is missing or is not in session 86's form."""


def classify(detail):
    """'absent', 'data' or 'fetch' for one manifest FAIL row's detail text."""
    if detail.startswith(("idx: ", "fetch: ")):
        return "absent" if "HTTP 404" in detail else "fetch"
    if detail.startswith("decode: "):
        return "data"
    if ABSENT_IDX_LINE.match(detail):
        return "absent"
    if LAYOUT.match(detail):
        return "data"
    return "fetch"


def read_csv(path, cols):
    path = Path(path)
    if not path.exists():
        raise FormError(f"{path} does not exist")
    with open(path, newline="") as f:
        rd = csv.DictReader(f)
        if rd.fieldnames != cols:
            raise FormError(f"{path}: its columns are not session 86's")
        return list(rd)


def check(drops_path, manifest_path):
    """A dict of counts, the station-days by class, and the verdict ('PASS' or 'FAIL')."""
    drops = read_csv(drops_path, DROP_COLS)
    man = read_csv(manifest_path, MAN_COLS)
    by_reason = {}
    for r in drops:
        by_reason[r["reason"]] = by_reason.get(r["reason"], 0) + 1
    grib_days = {(r["station"], r["target_date"]) for r in drops if r["reason"] == GRIB_DROP}
    fails, row_classes = {}, {"absent": 0, "data": 0, "fetch": 0}
    for r in man:
        if r["status"] == "FAIL":
            c = classify(r["detail"])
            row_classes[c] += 1
            fails.setdefault((r["station"], r["target_date"]), set()).add(c)
        elif r["status"] != "OK":
            raise FormError(f"{manifest_path}: a status {r['status']!r} that is neither OK nor FAIL")
    day_class = {}
    for k, cs in fails.items():
        day_class[k] = "fetch" if "fetch" in cs else "data" if "data" in cs else "absent"
    unmatched_drops = sorted(grib_days - set(fails))
    unmatched_fails = sorted(set(fails) - grib_days)
    by_class = {c: sorted(k for k in grib_days if day_class.get(k) == c) for c in ("absent", "data", "fetch")}
    ok = not by_class["fetch"] and not unmatched_drops and not unmatched_fails
    return {"drops": len(drops), "by_reason": by_reason, "manifest_rows": len(man),
            "fail_rows": sum(row_classes.values()), "fail_rows_by_class": row_classes, "by_class": by_class,
            "unmatched_drops": unmatched_drops, "unmatched_fails": unmatched_fails,
            "verdict": "PASS" if ok else "FAIL"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--drops", default=str(DEFAULT_DROPS), help="session 86's drop log")
    ap.add_argument("--manifest", default=str(DEFAULT_MANIFEST), help="session 86's GRIB manifest")
    a = ap.parse_args(argv)
    try:
        r = check(a.drops, a.manifest)
    except FormError as e:
        print(f"STOP: {e}")
        return 2
    print(f"drop log {a.drops}: {r['drops']} station-days dropped; by reason {r['by_reason'] or 'none'}")
    print(f"GRIB manifest {a.manifest}: {r['manifest_rows']} rows, {r['fail_rows']} FAIL "
          f"(absent {r['fail_rows_by_class']['absent']}, data {r['fail_rows_by_class']['data']}, "
          f"fetch {r['fail_rows_by_class']['fetch']})")
    print(f"'{GRIB_DROP}' station-days: absent from the archive {len(r['by_class']['absent'])}, "
          f"data {len(r['by_class']['data'])}, fetch failure {len(r['by_class']['fetch'])}")
    for k in r["by_class"]["fetch"][:20]:
        print(f"  fetch failure: {k[0]} {k[1]}")
    for k in r["by_class"]["data"][:20]:
        print(f"  data (for the owner): {k[0]} {k[1]}")
    if r["unmatched_drops"] or r["unmatched_fails"]:
        print(f"drops with no FAIL row: {len(r['unmatched_drops'])}; FAIL rows with no drop: "
              f"{len(r['unmatched_fails'])} (the two files do not agree)")
    if r["verdict"] == "PASS":
        print("BUILD CHECK: PASS. No station-day was dropped for a fetch failure (D125.5(b)): the build is accepted.")
        return 0
    print("BUILD CHECK: FAIL. The build is not accepted (D125.5(b)): move its outputs aside and keep them, "
          "then run the build again before any score.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
