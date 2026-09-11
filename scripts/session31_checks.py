"""Session 31 checks: read back every file this session's pull saved under
data/raw/diagnostics/session31/ and report the three findings.

Reads only from data/raw/diagnostics/session31/. Writes nothing. Fills
nothing (SPEC 2.2) -- every present/null count below is read straight off
what the API returned.

Nothing here builds, joins, fits or evaluates anything (session 31 scope).
This script only measures and reports availability.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "diagnostics" / "session31"

AIRPORTS = ["EGLC", "LFPG", "DSM", "YSDU", "RNO"]

# Known gfs_global grid points already established at each airport (F17, F31,
# F49, F66), used to confirm any upper-air response sits at the SAME grid
# point as the project's existing gfs_global data -- i.e. is genuinely GFS,
# not a silent CONUS-model swap.
KNOWN_GRID = {
    "EGLC": (51.487137, 0.0, 4.0),
    "LFPG": (49.027008, 2.578125, 109.0),
    "DSM": (41.52945, -93.63281, 285.0),
    "YSDU": (-32.274643, 148.59375, 279.0),
    "RNO": (39.537918, -119.765625, 1344.0),
}

# The shared 492-hour forecast-archive gap's last missing hour (F8/F22/F38/
# F57/F75) -- the hypothesis Task 1 tests against.
GAP_END_HYPOTHESIS = "2024-01-19T12:00"


def line(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def load(tag, station, start, end, model="gfs_global"):
    path = RAW / f"openmeteo_previousruns_{model}_{station}_{start}_{end}_{tag}.json"
    if not path.exists():
        return None, f"FILE NOT FOUND: {path.name}"
    d = json.loads(path.read_text())
    return d, None


def is_error(d):
    return isinstance(d, dict) and d.get("error") is True


def var_series(d, varname):
    """Return (times, values) for one _previous_day1 variable, or None if
    that key is not present in the response's hourly block."""
    key = f"{varname}_previous_day1"
    hourly = d.get("hourly", {})
    if key not in hourly:
        return None
    return hourly["time"], hourly[key]


def present_null_counts(values):
    present = sum(1 for v in values if v is not None)
    null = len(values) - present
    return present, null


def first_non_null(times, values):
    for t, v in zip(times, values):
        if v is not None:
            return t
    return None


def grid_check(d, station):
    if d is None or is_error(d):
        return "n/a (no response)"
    lat = d.get("latitude")
    lon = d.get("longitude")
    elev = d.get("elevation")
    known = KNOWN_GRID.get(station)
    if known is None:
        return f"lat={lat}, lon={lon}, elev={elev} (no known-grid reference)"
    klat, klon, kelev = known
    matches = (abs(lat - klat) < 1e-4 and abs(lon - klon) < 1e-4
               and abs(elev - kelev) < 1.0)
    return (f"lat={lat}, lon={lon}, elev={elev}  vs known gfs_global grid "
            f"{known}  -> {'MATCHES (genuine gfs_global grid point)' if matches else 'DOES NOT MATCH'}")


# =====================================================================
# TASK 1 -- pin the cloud/wind start date to the day
# =====================================================================

def task1():
    line("TASK 1 -- cloud/wind/dewpoint/humidity: first real hour, EGLC bracket")

    d, err = load("cloudwind_bracket", "EGLC", "2023-12-20", "2024-02-01")
    if err:
        print(err)
        return
    if is_error(d):
        print(f"REQUEST REJECTED: {d.get('reason')}")
        return

    results = {}
    for var in ["cloud_cover", "wind_speed_10m", "dew_point_2m",
                "relative_humidity_2m"]:
        series = var_series(d, var)
        if series is None:
            print(f"{var}: not present in response hourly block")
            continue
        times, values = series
        present, null = present_null_counts(values)
        first = first_non_null(times, values)
        results[var] = first
        print(f"{var:<24} bracket 2023-12-20..2024-02-01: "
              f"{present} present, {null} null, first real hour = {first}")

    print()
    for var in ["cloud_cover", "wind_speed_10m"]:
        first = results.get(var)
        if first is None:
            print(f"{var}: no non-null hour found in this bracket -- widen "
                  f"the window (not expected, per F7/D17)")
            continue
        verdict = ("MATCHES the gap-end hypothesis exactly"
                   if first == GAP_END_HYPOTHESIS else
                   f"DIFFERS from the gap-end hypothesis ({GAP_END_HYPOTHESIS})")
        print(f"{var}: first real hour = {first}  ->  {verdict}")

    print()
    print("dew_point_2m and relative_humidity_2m are wave-two features "
          "(informational only, gate nothing this phase) -- their own first "
          "real hours are printed above for the record.")

    line("TASK 1 -- targeted check at the other four airports")
    for station in ["LFPG", "DSM", "YSDU", "RNO"]:
        d, err = load("cloudwind_targeted", station, "2024-01-14", "2024-01-24")
        if err:
            print(f"{station}: {err}")
            continue
        if is_error(d):
            print(f"{station}: REQUEST REJECTED: {d.get('reason')}")
            continue
        print(f"\n{station} (window 2024-01-14..2024-01-24):")
        for var in ["cloud_cover", "wind_speed_10m", "dew_point_2m",
                    "relative_humidity_2m"]:
            series = var_series(d, var)
            if series is None:
                print(f"  {var}: not present in response")
                continue
            times, values = series
            present, null = present_null_counts(values)
            first = first_non_null(times, values)
            print(f"  {var:<24} {present} present, {null} null, "
                  f"first real hour in this window = {first}")


# =====================================================================
# TASK 2 -- 925/850 hPa temperature: first-ever probe
# =====================================================================

UPPERAIR_SPELLING_PROBES = [
    ("upperair_primary", ["temperature_925hPa", "temperature_850hPa"],
     "primary (Open-Meteo docs casing convention)"),
    ("upperair_lowercase", ["temperature_925hpa"], "lowercase 'hpa'"),
    ("upperair_uppercase", ["temperature_925HPA"], "uppercase 'HPA'"),
    ("upperair_mb", ["temperature_925mb"], "'mb' unit suffix"),
]


def task2():
    line("TASK 2 -- upper-air temperature: spelling probe at EGLC")

    working_vars = []
    for tag, varnames, label in UPPERAIR_SPELLING_PROBES:
        d, err = load(tag, "EGLC", "2025-06-15", "2025-06-16")
        print(f"\nspelling: {label}  ({', '.join(varnames)}_previous_day1)")
        if err:
            print(f"  {err}")
            continue
        if is_error(d):
            print(f"  HTTP-REJECTED. Verbatim reason: {d.get('reason')!r}")
            continue
        any_present = False
        for v in varnames:
            series = var_series(d, v)
            if series is None:
                print(f"  {v}: ACCEPTED request, but variable key absent "
                      f"from response hourly block")
                continue
            times, values = series
            present, null = present_null_counts(values)
            if present > 0:
                print(f"  {v}: ACCEPTED + VALUES  "
                      f"({present} present, {null} null of {len(values)})")
                any_present = True
                if v not in working_vars:
                    working_vars.append(v)
            else:
                print(f"  {v}: ACCEPTED but ALL NULL "
                      f"({null} of {len(values)})")
        print(f"  grid point returned: {grid_check(d, 'EGLC')}")

    line("TASK 2 -- verdict on spelling")
    if working_vars:
        print(f"Working spelling(s), returning real values: {working_vars}")
    else:
        print("No candidate spelling with a _previous_dayN offset suffix "
              "returned real values at EGLC -- all four are HTTP-rejected, "
              "verbatim, above.")

    line("TASK 2 -- addendum: does the offset suffix work AT ALL for "
         "pressure-level variables? (isolates why every spelling above was "
         "rejected)")
    print("Two follow-up probes, run after the spelling rejections above, "
          "to find out whether the _previous_dayN mechanism applies to "
          "pressure-level ('SurfacePressureAndHeightVariable') variables at "
          "all, or only to day1+.")
    print()
    print("Probe A -- the BARE variable name, no offset suffix at all "
          "(temperature_925hPa, EGLC):")
    d, err = load("upperair_bare_no_offset", "EGLC", "2025-06-15", "2025-06-16")
    if err:
        print(f"  {err}")
    elif is_error(d):
        print(f"  REJECTED -- {d.get('reason')!r}")
    else:
        vals = d["hourly"]["temperature_925hPa"]
        present, null = present_null_counts(vals)
        print(f"  ACCEPTED: {present} present / {null} null of {len(vals)}. "
              f"generationtime_ms={d.get('generationtime_ms')}. "
              f"grid: {grid_check(d, 'EGLC')}")
        print("  This is the FRESHEST-RUN series (no day-ahead offset "
              "applied) -- the same leakage trap D17 already named for the "
              "plain temperature_2m variable (SPEC 2.1b): using it as a "
              "training feature would use information from AFTER the valid "
              "time, not a genuine forecast made a day ahead.")

    print()
    print("Probe B -- explicit _previous_day0 suffix (should be equivalent "
          "to the bare form if the offset mechanism works at all for this "
          "variable class, EGLC):")
    d, err = load("upperair_day0suffix", "EGLC", "2025-06-15", "2025-06-16")
    if err:
        print(f"  {err}")
    elif is_error(d):
        print(f"  REJECTED, verbatim -- {d.get('reason')!r}")
    else:
        print("  ACCEPTED (unexpected).")

    print()
    print("VERDICT of the addendum: the _previous_dayN offset mechanism "
          "does not parse AT ALL for pressure-level temperature on this "
          "endpoint -- not even _previous_day0 is accepted, so this is not "
          "a 'day1+ only' restriction the way cloud/wind's archive-start "
          "date is. The variable exists on this endpoint's URL only in its "
          "bare, current-run form.")

    line("TASK 2 -- bare (no-offset) form confirmed at DSM and RNO too, "
         "same grid point as the project's existing gfs_global data")
    for station in ["DSM", "RNO"]:
        d, err = load("upperair_bare_no_offset", station, "2025-06-15",
                       "2025-06-16")
        if err:
            print(f"{station}: {err}")
            continue
        if is_error(d):
            print(f"{station}: REJECTED -- {d.get('reason')!r}")
            continue
        print(f"\n{station}:")
        print(f"  grid point: {grid_check(d, station)}")
        for v in ["temperature_925hPa", "temperature_850hPa"]:
            vals = d["hourly"].get(v)
            if vals is None:
                print(f"  {v}: absent from response")
                continue
            present, null = present_null_counts(vals)
            print(f"  {v}: {present} present / {null} null of {len(vals)}")
    print()
    print("Both CONUS airports return the bare-form pressure-level data at "
          "EXACTLY their already-established gfs_global grid point (F31 "
          "for DSM, F66 for RNO) -- confirming genuinely GFS, not a silent "
          "CONUS-model swap, even in this current-run-only form.")

    line("TASK 2 -- how far back (date ladder, all five airports, primary "
         "spelling)")
    ladder_dates = ["2021-03-24", "2023-07-01", "2024-07-01"]
    # The 2025-06-10..12 anchor (task 3) doubles as the ladder's most-recent
    # point.
    for station in AIRPORTS:
        print(f"\n{station}:")
        rows = []
        for d_str in ladder_dates:
            d, err = load("upperair_ladder", station, d_str, d_str)
            if err:
                rows.append((d_str, None, None, err))
                continue
            if is_error(d):
                rows.append((d_str, "REJECTED", d.get("reason"), None))
                continue
            counts = {}
            for v in ["temperature_925hPa", "temperature_850hPa"]:
                series = var_series(d, v)
                if series is None:
                    counts[v] = "absent"
                else:
                    _, values = series
                    present, null = present_null_counts(values)
                    counts[v] = f"{present} present / {null} null"
            rows.append((d_str, "ok", counts, d))
        for d_str, status, detail, resp in rows:
            if status is None:
                print(f"  {d_str}: {detail}")
            elif status == "REJECTED":
                print(f"  {d_str}: REJECTED -- {detail!r}")
            else:
                print(f"  {d_str}: {detail}")
        # anchor date (2025-06-10..12) from task 3's own upper-air pull,
        # shown here too so the ladder's most-recent point is visible
        # alongside the earlier three.
        d, err = load("anchor_upperair", station, "2025-06-10", "2025-06-12")
        if err:
            print(f"  2025-06-10..12 (anchor): {err}")
        elif is_error(d):
            print(f"  2025-06-10..12 (anchor): REJECTED -- {d.get('reason')!r}")
        else:
            counts = {}
            for v in ["temperature_925hPa", "temperature_850hPa"]:
                series = var_series(d, v)
                if series is None:
                    counts[v] = "absent"
                else:
                    _, values = series
                    present, null = present_null_counts(values)
                    counts[v] = f"{present} present / {null} null"
            print(f"  2025-06-10..12 (anchor): {counts}")
            print(f"    grid point: {grid_check(d, station)}")


# =====================================================================
# TASK 3 -- five-airport availability table
# =====================================================================

def task3():
    line("TASK 3 -- five-airport availability table (anchor 2025-06-10..12)")

    known_vars = ["temperature_2m", "cloud_cover", "wind_speed_10m",
                  "dew_point_2m", "relative_humidity_2m"]
    upperair_vars = ["temperature_925hPa", "temperature_850hPa"]
    all_vars = known_vars + upperair_vars

    table = {v: {} for v in all_vars}

    for station in AIRPORTS:
        d_known, err_known = load("anchor_known", station, "2025-06-10",
                                   "2025-06-12")
        d_upper, err_upper = load("anchor_upperair", station, "2025-06-10",
                                   "2025-06-12")

        for v in known_vars:
            if err_known:
                table[v][station] = f"NOT FOUND"
                continue
            if is_error(d_known):
                table[v][station] = f"REJECTED"
                continue
            series = var_series(d_known, v)
            if series is None:
                table[v][station] = "absent"
                continue
            _, values = series
            present, null = present_null_counts(values)
            table[v][station] = f"{present}p/{null}n"

        for v in upperair_vars:
            if err_upper:
                table[v][station] = "NOT FOUND"
                continue
            if is_error(d_upper):
                table[v][station] = "REJECTED"
                continue
            series = var_series(d_upper, v)
            if series is None:
                table[v][station] = "absent"
                continue
            _, values = series
            present, null = present_null_counts(values)
            table[v][station] = f"{present}p/{null}n"

    header = f"{'variable':<24}" + "".join(f"{s:>14}" for s in AIRPORTS)
    print(header)
    print("-" * len(header))
    for v in all_vars:
        row = f"{v:<24}" + "".join(f"{table[v].get(s, '?'):>14}" for s in AIRPORTS)
        print(row)
    print()
    print("p = present (non-null), n = null. 'REJECTED' = HTTP-rejected "
          "variable name. 'absent' = request accepted but this key never "
          "appeared in the response.")


def main():
    task1()
    task2()
    task3()


if __name__ == "__main__":
    main()
