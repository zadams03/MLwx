"""Session 63: the reserved-year feature build (closes DECISIONS D58 item
11). Produces real L, D, T, R feature values for the reserved 2024-08-01 to
2025-07-31 confirmation year, so session 64 can run the already-frozen
`scripts/session62_reserved_confirm.py --confirm` once, unchanged, on that
year (D51). B is NOT rebuilt -- the base 5-feature GRIB dataset
(`data/processed/grib_features_v16_window.csv`) already carries the reserved
year's rows (it was built before D51's reservation existed).

THIS IS AN OUTCOME-ORTHOGONAL DATA BUILD. No model is fit. No MAE, skill, or
CV is computed anywhere in this script. Nothing is scored, selected, tuned,
or ranked. `run_confirm()` (in session62_reserved_confirm.py) is never
called, imported for execution, or invoked here.

Why touching the reserved year is allowed here, when D51 otherwise forbids
it (D58 item 11's own reasoning, not a loosening of D51): pulling raw GRIB
data for the reserved year's dates and applying only the already-pinned
transforms is not a feature experiment -- no model is fit, no result is
read, nothing is selected on it. The final feature set is already locked
(D58: B + D, L, R, T), so there is no selection left to bias.

Step 0 determination (read scripts/session62_reserved_confirm.py first,
per the session prompt): `run_confirm()` locates L/D/T/R values through
`load_family()`, which reads exactly the two files named in
`session60_combine_design.CANDIDATE_FEATURES[code]` ("v16_file",
"sealed_file") -- i.e. the sessions 49/51/53/55 committed family files --
and explicitly SKIPS (and counts as a "hit", then raises in run_confirm())
any row whose date falls inside the reserved year. There is no third,
per-family reserved-year source file already referenced anywhere in the
frozen script or in CANDIDATE_FEATURES -- so Step 0 CASE (A) does not hold.
This is CASE (B): a minimal, one-line-shaped source-path addition is needed
so the frozen script can see new reserved-year files. That wiring change is
made by this session to `scripts/session62_reserved_confirm.py`'s own
`load_family()` function only (documented in this module's own
`WIRING_CHANGE` docstring below and applied via a separate, reviewable
diff) -- `session60_combine_design.py`'s `CANDIDATE_FEATURES` dict (which
session 61 already used and completed with) is left untouched, so nothing
about session 61's own already-reported result changes.

Reuses, does not redefine or re-derive: the frozen pull/decode/derive
functions from scripts/session49_upper_air_pull.py (L),
scripts/session51_moisture_pull.py (D), scripts/session53_pressure_pull.py
(T), and scripts/session55_radiation_pull.py (R) -- imported directly.
Only the JOIN step is re-written here (not imported), because each family's
own `build_joined()` hard-codes "skip any date inside the reserved year";
this session needs the opposite filter (keep ONLY dates inside the reserved
year). The arithmetic in each of this module's own `join_*` functions below
is copied verbatim from that family's own `build_joined()` -- no window,
constant, or formula is re-derived or changed.
"""

import csv
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
DIAG = ROOT / "data" / "raw" / "diagnostics" / "session63"
DIAG.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(Path(__file__).resolve().parent))
from session48_reserved_year import RESERVED_YEAR_START, RESERVED_YEAR_END  # noqa: E402

import session49_upper_air_pull as s49  # noqa: E402
import session51_moisture_pull as s51  # noqa: E402
import session53_pressure_pull as s53  # noqa: E402
import session55_radiation_pull as s55  # noqa: E402

BASE_V16_CSV = PROCESSED / "grib_features_v16_window.csv"
BASE_COLS = ["station", "target_date", "target_hour", "run_date", "cycle", "lead",
             "temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]

OUT_LOG = ROOT / "notes" / "session-63-reserved-build-output.txt"


class Tee:
    def __init__(self, path):
        self.f = open(path, "w")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def line(title):
    print()
    print("=" * 90)
    print(title)
    print("=" * 90)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ Step 1

def load_base_reserved_rows():
    """{station: {date: base_row_dict}}, restricted to rows already inside
    the reserved 2024-08-01..2025-07-31 year, read from the BASE 5-feature
    dataset (which already carries this year -- it was built before D51's
    reservation existed). This is both the date list AND the source of the
    base columns (station/target_date/target_hour/run_date/cycle/lead/
    temperature_grib_c/cloud_cover_grib_pct/wind_speed_grib_kmh) for every
    new reserved-year family output file."""
    per_station = {}
    with open(BASE_V16_CSV) as f:
        for row in csv.DictReader(f):
            d = date.fromisoformat(row["target_date"])
            if RESERVED_YEAR_START <= d <= RESERVED_YEAR_END:
                per_station.setdefault(row["station"], {})[d] = row
    return per_station


# ------------------------------------------------------------------ Step 2

def assert_all_inside_reserved_year(label, dates):
    """The INVERSE of assert_reserved_year_excluded (session prompt Step 2):
    every date must be INSIDE the reserved year, none outside it."""
    bad = [d for d in dates if not (RESERVED_YEAR_START <= d <= RESERVED_YEAR_END)]
    if bad:
        raise AssertionError(
            f"{label}: {len(bad)} date(s) OUTSIDE the reserved "
            f"{RESERVED_YEAR_START}..{RESERVED_YEAR_END} year found: {bad[:5]}")
    print(f"    {label}: all {len(dates)} dates confirmed INSIDE "
          f"{RESERVED_YEAR_START}..{RESERVED_YEAR_END} -- PASS")


# ------------------------------------------------------------------ Step 3: pull (imports frozen process_combo/build_combos)

def pull_L(per_station):
    combos = s49.build_combos(per_station)
    n_combos = len(combos)
    decoded = {s: {} for s in s49.AIRPORTS}
    manifest_rows = []
    per_field_counts = {lk: {"requested": 0, "ok": 0} for lk in s49.LEVELS}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=s49.MAX_WORKERS) as ex:
        futures = {ex.submit(s49.process_combo, rd, c, l, st): (rd, st)
                   for (rd, c, l), st in combos.items()}
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            results, rows = fut.result()
            manifest_rows.extend(rows)
            for level_key in s49.LEVELS:
                per_field_counts[level_key]["requested"] += len(stations)
                vals_k = results.get(level_key)
                if vals_k is not None:
                    per_field_counts[level_key]["ok"] += len(stations)
                    for station in stations:
                        decoded[station].setdefault(target_date, {})[level_key] = vals_k[station] - 273.15
    elapsed = time.time() - t0
    return decoded, manifest_rows, per_field_counts, n_combos, elapsed


def pull_D(per_station):
    combos = s51.build_combos(per_station)
    n_combos = len(combos)
    decoded = {s: {} for s in s51.AIRPORTS}
    manifest_rows = []
    per_field_counts = {fk: {"requested": 0, "ok": 0} for fk in s51.LEVELS}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=s51.MAX_WORKERS) as ex:
        futures = {ex.submit(s51.process_combo, rd, c, l, st): (rd, st)
                   for (rd, c, l), st in combos.items()}
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            results, rows = fut.result()
            manifest_rows.extend(rows)
            for field_key in s51.LEVELS:
                per_field_counts[field_key]["requested"] += len(stations)
                vals = results.get(field_key)
                if vals is not None:
                    per_field_counts[field_key]["ok"] += len(stations)
                    for station in stations:
                        v = vals[station]
                        if field_key == "dew_point_2m":
                            v = v - 273.15
                        decoded[station].setdefault(target_date, {})[field_key] = v
    elapsed = time.time() - t0
    return decoded, manifest_rows, per_field_counts, n_combos, elapsed


def pull_T(per_station):
    combos = s53.build_combos(per_station)
    n_combos = len(combos)
    decoded = {s: {} for s in s53.AIRPORTS}
    manifest_rows = []
    per_field_counts = {fk: {"requested": 0, "ok": 0} for fk in s53.ALL_FIELD_KEYS}
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=s53.MAX_WORKERS) as ex:
        futures = {ex.submit(s53.process_combo, rd, c, l, st): (rd, st)
                   for (rd, c, l), st in combos.items()}
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            results, rows = fut.result()
            manifest_rows.extend(rows)
            for field_key in s53.ALL_FIELD_KEYS:
                per_field_counts[field_key]["requested"] += len(stations)
                vals = results.get(field_key)
                if vals is not None:
                    per_field_counts[field_key]["ok"] += len(stations)
                    for station in stations:
                        decoded[station].setdefault(target_date, {})[field_key] = vals[station]
    elapsed = time.time() - t0
    return decoded, manifest_rows, per_field_counts, n_combos, elapsed


def pull_R(per_station):
    combos = s55.build_combos(per_station)  # keys: (run_date, cycle, lead, needs_deaccum)
    n_combos = len(combos)
    decoded = {s: {} for s in s55.AIRPORTS}
    manifest_rows = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=s55.MAX_WORKERS) as ex:
        futures = {ex.submit(s55.process_combo, rd, c, l, needs, st): (rd, st)
                   for (rd, c, l, needs), st in combos.items()}
        for fut in as_completed(futures):
            run_date, stations = futures[fut]
            target_date = run_date + timedelta(days=1)
            result, rows = fut.result()
            manifest_rows.extend(rows)
            for station in stations:
                decoded[station].setdefault(target_date, {})
                if result["to_lead"] is not None:
                    decoded[station][target_date]["to_lead"] = result["to_lead"][station]
                if result["to_lead_minus2"] is not None:
                    decoded[station][target_date]["to_lead_minus2"] = result["to_lead_minus2"][station]
    elapsed = time.time() - t0
    field_counts = {"dswrf_to_lead": {"requested": 0, "ok": 0},
                     "dswrf_to_lead_minus2": {"requested": 0, "ok": 0}}
    for (rd, c, l, needs), st in combos.items():
        field_counts["dswrf_to_lead"]["requested"] += len(st)
        if needs:
            field_counts["dswrf_to_lead_minus2"]["requested"] += len(st)
    for station, date_map in decoded.items():
        for d, vals in date_map.items():
            if "to_lead" in vals:
                field_counts["dswrf_to_lead"]["ok"] += 1
            if "to_lead_minus2" in vals:
                field_counts["dswrf_to_lead_minus2"]["ok"] += 1
    return decoded, manifest_rows, field_counts, n_combos, elapsed


# ------------------------------------------------------------------ Step 3: join+derive (formulas copied verbatim from each family's own build_joined)

def join_L(per_station, decoded, elev_corr):
    fieldnames = BASE_COLS + ["t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850"]
    out_rows, drop_log = [], []
    before, after = {}, {}
    for station in sorted(per_station):
        date_map = per_station[station]
        before[station] = len(date_map)
        for d in sorted(date_map):
            row = date_map[d]
            dec = decoded.get(station, {}).get(d)
            missing = [lk for lk in s49.LEVELS if dec is None or dec.get(lk) is None]
            if missing:
                drop_log.append([station, d.isoformat(), "reserved_window", f"missing decoded field(s): {missing}"])
                continue
            t2m_raw = round(float(row["temperature_grib_c"]) - elev_corr[station], 3)
            new_row = {k: row[k] for k in BASE_COLS}
            new_row["t2m_raw"] = t2m_raw
            new_row["t925"] = round(dec["t925"], 3)
            new_row["t850"] = round(dec["t850"], 3)
            new_row["t700"] = round(dec["t700"], 3)
            new_row["lapse_rate_t2_t850"] = round(t2m_raw - dec["t850"], 3)
            out_rows.append(new_row)
            after[station] = after.get(station, 0) + 1
    out_csv = PROCESSED / "session63_reserved_window_with_upper_air.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, before, after, drop_log


def join_D(per_station, decoded, elev_corr):
    fieldnames = BASE_COLS + ["t2m_raw", "relative_humidity_2m", "dew_point_2m",
                               "specific_humidity_2m", "dewpoint_depression_t2m"]
    out_rows, drop_log = [], []
    before, after = {}, {}
    for station in sorted(per_station):
        date_map = per_station[station]
        before[station] = len(date_map)
        for d in sorted(date_map):
            row = date_map[d]
            dec = decoded.get(station, {}).get(d)
            missing = [fk for fk in s51.LEVELS if dec is None or dec.get(fk) is None]
            if missing:
                drop_log.append([station, d.isoformat(), "reserved_window", f"missing decoded field(s): {missing}"])
                continue
            t2m_raw = round(float(row["temperature_grib_c"]) - elev_corr[station], 3)
            new_row = {k: row[k] for k in BASE_COLS}
            new_row["t2m_raw"] = t2m_raw
            new_row["relative_humidity_2m"] = round(dec["relative_humidity_2m"], 3)
            new_row["dew_point_2m"] = round(dec["dew_point_2m"], 3)
            new_row["specific_humidity_2m"] = round(dec["specific_humidity_2m"], 6)
            # Session prompt Step 3: store the RAW column. D53/F100's floor
            # (max(x, 0)) is applied downstream by the confirmation script,
            # not here.
            new_row["dewpoint_depression_t2m"] = round(t2m_raw - dec["dew_point_2m"], 3)
            out_rows.append(new_row)
            after[station] = after.get(station, 0) + 1
    out_csv = PROCESSED / "session63_reserved_window_with_moisture.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, before, after, drop_log


def join_T(per_station, decoded):
    fieldnames = BASE_COLS + ["pressure_msl_hpa", "pressure_surface_hpa",
                               "pressure_msl_lead_minus3_hpa", "pressure_tendency_3h_hpa"]
    out_rows, drop_log = [], []
    before, after = {}, {}
    for station in sorted(per_station):
        date_map = per_station[station]
        before[station] = len(date_map)
        for d in sorted(date_map):
            row = date_map[d]
            dec = decoded.get(station, {}).get(d)
            missing = [fk for fk in s53.ALL_FIELD_KEYS if dec is None or dec.get(fk) is None]
            if missing:
                drop_log.append([station, d.isoformat(), "reserved_window", f"missing decoded field(s): {missing}"])
                continue
            msl_hpa = round(dec["pressure_msl_hpa"] / 100.0, 3)
            sfc_hpa = round(dec["pressure_surface_hpa"] / 100.0, 3)
            msl_m3_hpa = round(dec["pressure_msl_lead_minus3_hpa"] / 100.0, 3)
            new_row = {k: row[k] for k in BASE_COLS}
            new_row["pressure_msl_hpa"] = msl_hpa
            new_row["pressure_surface_hpa"] = sfc_hpa
            new_row["pressure_msl_lead_minus3_hpa"] = msl_m3_hpa
            new_row["pressure_tendency_3h_hpa"] = round(msl_hpa - msl_m3_hpa, 3)
            out_rows.append(new_row)
            after[station] = after.get(station, 0) + 1
    out_csv = PROCESSED / "session63_reserved_window_with_pressure.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, before, after, drop_log


def join_R(per_station, decoded):
    fieldnames = BASE_COLS + ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"]
    out_rows, drop_log = [], []
    before, after = {}, {}
    for station in sorted(per_station):
        date_map = per_station[station]
        before[station] = len(date_map)
        target_hour = s55.AIRPORTS[station][0]
        _, lead = s55.cycle_and_lead(target_hour)
        needs_deaccum = (lead - s55.window_start(lead)) != 2
        for d in sorted(date_map):
            row = date_map[d]
            dec = decoded.get(station, {}).get(d)
            if dec is None or dec.get("to_lead") is None:
                drop_log.append([station, d.isoformat(), "reserved_window", "missing decoded dswrf_to_lead value"])
                continue
            to_lead = dec["to_lead"]
            if needs_deaccum:
                if dec.get("to_lead_minus2") is None:
                    drop_log.append([station, d.isoformat(), "reserved_window", "missing decoded dswrf_to_lead_minus2 value"])
                    continue
                to_lead_m2 = dec["to_lead_minus2"]
                dur_full = lead - s55.window_start(lead)
                dur_partial = (lead - 2) - s55.window_start(lead - 2)
                energy_2h = to_lead * dur_full - to_lead_m2 * dur_partial
                dswrf_2h = energy_2h / 2.0
                to_lead_m2_out = round(to_lead_m2, 3)
            else:
                dswrf_2h = to_lead
                to_lead_m2_out = ""
            new_row = {k: row[k] for k in BASE_COLS}
            new_row["dswrf_ave_to_lead_wm2"] = round(to_lead, 3)
            new_row["dswrf_ave_to_lead_minus2_wm2"] = to_lead_m2_out
            new_row["dswrf_2h_wm2"] = round(dswrf_2h, 3)
            out_rows.append(new_row)
            after[station] = after.get(station, 0) + 1
    out_csv = PROCESSED / "session63_reserved_window_with_radiation.csv"
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)
    return out_csv, before, after, drop_log


# ------------------------------------------------------------------ main

FAMILIES = ["L", "D", "T", "R"]
FAMILY_LABEL = {"L": "upper_air", "D": "moisture", "T": "pressure", "R": "radiation"}
FAMILY_NEW_COLS = {
    "L": ["t2m_raw", "t925", "t850", "t700", "lapse_rate_t2_t850"],
    "D": ["t2m_raw", "relative_humidity_2m", "dew_point_2m", "specific_humidity_2m",
          "dewpoint_depression_t2m"],
    "T": ["pressure_msl_hpa", "pressure_surface_hpa", "pressure_msl_lead_minus3_hpa",
          "pressure_tendency_3h_hpa"],
    "R": ["dswrf_ave_to_lead_wm2", "dswrf_ave_to_lead_minus2_wm2", "dswrf_2h_wm2"],
}


def main():
    tee = Tee(OUT_LOG)
    sys.stdout = tee

    line("SESSION 63 -- reserved-year feature build (closes DECISIONS D58 "
         "item 11). Data build only. No model fit. No MAE/skill/CV anywhere. "
         "run_confirm() is never called.")
    print(f"run at: {time.strftime('%Y-%m-%d %H:%M:%S')} local")

    line("STEP 0 -- wiring determination (see this module's own docstring "
         "for the full reasoning)")
    print("    CASE (B) holds: scripts/session62_reserved_confirm.py's "
          "load_family() reads only the two files named in "
          "session60_combine_design.CANDIDATE_FEATURES (the sessions "
          "49/51/53/55 committed family files) and treats any reserved-year "
          "row found there as a 'hit' that stops the run. No third, "
          "per-family reserved-year source file is referenced anywhere in "
          "the frozen script today. A minimal wiring addition to "
          "load_family() (reading a new, explicit RESERVED_FAMILY_FILES map, "
          "added to session62_reserved_confirm.py only -- NOT to "
          "session60_combine_design.py's CANDIDATE_FEATURES) is applied "
          "separately from this data-build script, documented in full in "
          "this session's own DECISIONS finding (F107). This script produces "
          "the four files that wiring will point at. run_confirm() is not "
          "called by this script or by that edit.")

    line("STEP 1 -- reserved-year date list, built from the base dataset's "
         "own rows (data/processed/grib_features_v16_window.csv)")
    per_station = load_base_reserved_rows()
    for st in sorted(per_station):
        dates = sorted(per_station[st])
        print(f"    {st:<6} n_dates={len(dates):<4} {dates[0]} .. {dates[-1]}")

    line("STEP 2 -- invert the reserved-year guard: every date must be "
         "INSIDE the reserved year (the exclusion guard would raise on "
         "every one of these, so it is never called here)")
    for st in sorted(per_station):
        assert_all_inside_reserved_year(st, sorted(per_station[st]))

    line("STEP 3 -- run the four frozen pipelines over the reserved year")

    elev_corr = s49.load_elevation_corrections()
    print(f"\n    Elevation corrections (D48.3/F90, unchanged, reused by import): "
          f"{elev_corr}")

    results = {}
    total, used, free_before = shutil.disk_usage(ROOT)
    print(f"\n    Free disk space BEFORE any pull: {free_before / (1024**3):.2f} GiB")

    for code, pull_fn, join_args in [
        ("L", pull_L, ()),
        ("D", pull_D, ()),
        ("T", pull_T, ()),
        ("R", pull_R, ()),
    ]:
        label = FAMILY_LABEL[code]
        sub(f"family {code} ({label}) -- pull")
        decoded, manifest_rows, per_field_counts, n_combos, elapsed = pull_fn(per_station)
        print(f"    combos={n_combos}  elapsed={elapsed/60:.2f} min")
        for fk, counts in per_field_counts.items():
            failed = counts["requested"] - counts["ok"]
            print(f"    {fk:<26} requested={counts['requested']:<6} "
                  f"decoded_ok={counts['ok']:<6} failed={failed}")
        manifest_csv = DIAG / f"session63_{label}_pull_manifest.csv"
        with open(manifest_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["run_date", "cycle", "lead", "field_key", "stations", "status", "detail"])
            w.writerows(manifest_rows)
        n_fail = sum(1 for r in manifest_rows if r[5] == "FAIL")
        print(f"    manifest -> {manifest_csv} ({len(manifest_rows)} rows, {n_fail} FAIL)")
        if n_fail:
            for r in manifest_rows:
                if r[5] == "FAIL":
                    print(f"      FAIL: {r}")

        sub(f"family {code} ({label}) -- join + derive")
        if code == "L":
            out_csv, before, after, drops = join_L(per_station, decoded, elev_corr)
        elif code == "D":
            out_csv, before, after, drops = join_D(per_station, decoded, elev_corr)
        elif code == "T":
            out_csv, before, after, drops = join_T(per_station, decoded)
        else:
            out_csv, before, after, drops = join_R(per_station, decoded)
        print(f"    output -> {out_csv}")
        for st in sorted(per_station):
            b, a = before.get(st, 0), after.get(st, 0)
            flag = "  <-- JOIN DROPPED ROWS" if a < b else ""
            print(f"    {st:<6} before={b:<4} after={a:<4}{flag}")
        drops_csv = PROCESSED / f"session63_{label}_join_drops.csv"
        with open(drops_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["station", "target_date", "span", "reason"])
            w.writerows(drops)
        print(f"    join-drop log -> {drops_csv} ({len(drops)} rows)")
        results[code] = dict(out_csv=out_csv, before=before, after=after,
                              drops=drops, manifest_rows=manifest_rows, n_fail=n_fail)

    total, used, free_after = shutil.disk_usage(ROOT)
    print(f"\n    Free disk space AFTER all four pulls: {free_after / (1024**3):.2f} GiB "
          f"(before: {free_before / (1024**3):.2f} GiB)")

    line("STEP 4 -- verify (real numbers)")

    base_counts = {st: len(per_station[st]) for st in per_station}
    print(f"\n    Base dataset's own reserved-year row counts, per airport: {base_counts}")

    for code in FAMILIES:
        label = FAMILY_LABEL[code]
        r = results[code]
        sub(f"family {code} ({label})")
        print(f"    join drops: {len(r['drops'])} (expect 0)")
        print(f"    manifest FAIL rows: {r['n_fail']} (expect 0)")
        out_rows = list(csv.DictReader(open(r["out_csv"])))
        for st in sorted(per_station):
            out_n = sum(1 for row in out_rows if row["station"] == st)
            base_n = base_counts[st]
            match = "MATCH" if out_n == base_n else "MISMATCH"
            print(f"    {st:<6} output_rows={out_n:<5} base_reserved_rows={base_n:<5} {match}")
        print(f"    null counts in derived columns (expect 0):")
        for col in FAMILY_NEW_COLS[code]:
            n_null = sum(1 for row in out_rows if row[col] in ("", None))
            print(f"      {col:<32} n_null={n_null}")

    sub("spot-check: physical plausibility")
    l_rows = list(csv.DictReader(open(results["L"]["out_csv"])))
    l_eglc = next((r for r in l_rows if r["station"] == "EGLC"), None)
    if l_eglc:
        print(f"    L / EGLC {l_eglc['target_date']}: t2m_raw={l_eglc['t2m_raw']} "
              f"t925={l_eglc['t925']} t850={l_eglc['t850']} t700={l_eglc['t700']} "
              f"lapse_rate_t2_t850={l_eglc['lapse_rate_t2_t850']}")
        colder = float(l_eglc['t2m_raw']) > float(l_eglc['t925']) > float(l_eglc['t850']) > float(l_eglc['t700'])
        print(f"    colder-with-height (t2m_raw > t925 > t850 > t700): {'YES' if colder else 'NO -- FLAG'}")
    l_rno = [r for r in l_rows if r["station"] == "RNO"]
    if l_rno:
        import statistics
        mean_t2m = statistics.mean(float(r["t2m_raw"]) for r in l_rno)
        mean_t925 = statistics.mean(float(r["t925"]) for r in l_rno)
        print(f"    L / RNO reserved-year means: t2m_raw={mean_t2m:.2f} t925={mean_t925:.2f} "
              f"-- RNO's surface-to-925hPa inversion (F98, a real elevation effect, "
              f"not a defect) expected to reproduce here too: "
              f"{'t925 warmer than surface, as F98 found' if mean_t925 > mean_t2m else 'NOT reproduced -- note'}")

    r_rows = list(csv.DictReader(open(results["R"]["out_csv"])))
    r_eglc = [r for r in r_rows if r["station"] == "EGLC"]
    if r_eglc:
        import statistics
        mean_dswrf = statistics.mean(float(r["dswrf_2h_wm2"]) for r in r_eglc)
        n_neg = sum(1 for r in r_eglc if float(r["dswrf_2h_wm2"]) < 0)
        print(f"    R / EGLC reserved-year mean dswrf_2h_wm2={mean_dswrf:.2f} W/m2, "
              f"negative_values={n_neg} (expect 0)")

    t_rows = list(csv.DictReader(open(results["T"]["out_csv"])))
    t_eglc = [r for r in t_rows if r["station"] == "EGLC"]
    if t_eglc:
        import statistics
        mean_tend = statistics.mean(float(r["pressure_tendency_3h_hpa"]) for r in t_eglc)
        print(f"    T / EGLC reserved-year mean pressure_tendency_3h_hpa={mean_tend:.3f} hPa "
              f"(sanity range roughly -15..+15)")

    d_rows = list(csv.DictReader(open(results["D"]["out_csv"])))
    d_eglc = [r for r in d_rows if r["station"] == "EGLC"]
    if d_eglc:
        viol = sum(1 for r in d_eglc if float(r["dew_point_2m"]) > float(r["t2m_raw"]))
        print(f"    D / EGLC reserved-year dew_point_2m > t2m_raw violations: {viol} (expect 0)")

    line("STEP 5 -- confirm the test-window B matrix is complete (read-only, "
         "no model, no score)")
    b_cols = ["temperature_grib_c", "cloud_cover_grib_pct", "wind_speed_grib_kmh"]
    any_b_null = False
    for st in sorted(per_station):
        rows = list(per_station[st].values())
        for col in b_cols:
            n_null = sum(1 for row in rows if row[col] in ("", None))
            if n_null:
                any_b_null = True
            print(f"    {st:<6} {col:<26} n_null={n_null} (n_rows={len(rows)})")
    print(f"\n    B-completeness: {'PASS -- 0 nulls throughout' if not any_b_null else 'FAIL -- see above, this would block session 64'}")

    line("END OF SESSION 63 DATA BUILD")
    print("No model was fit anywhere in this script. No MAE, skill, or CV was")
    print("computed. run_confirm() was never called. The sealed year")
    print("(2025-08-01..2026-07-31, F94) was never touched. No existing")
    print("committed file was rewritten -- only new session63_reserved_window_")
    print("with_*.csv files and new diagnostic manifests were written.")
    print(f"\nThis output is saved at {OUT_LOG}")

    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
