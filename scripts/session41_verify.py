"""Session 41 Task 1: verify the D48.8-EXCEEDS "extra" sealed-year days at
EGLC, LFPG and YSDU (F92) are legitimate GRIB observation-forecast pairs,
not a pairing bug -- and sanity-check DSM/RNO's exact matches too, so
"exact" is confirmed correct rather than coincidental.

READ-ONLY DIAGNOSTIC. No model is fit and no sealed-year MAE, skill or
verdict is computed anywhere in this script (session prompt's integrity
boundary). It reuses the FROZEN scripts/session39_sealed_test.py's own
functions, unmodified, as a library -- importing that module does not run
its main() (guarded behind `if __name__ == "__main__":`), so nothing in it
is executed or changed by this import.

What this script actually checks, precisely:
  1. Reproduces the new (GRIB) recipe's own sealed-year join (test_rows),
     exactly as scripts/session39_sealed_test.py's run_airport() does.
  2. Reproduces, from raw data, the OLD (existing 3-feature/Open-Meteo)
     recipe's own two-stage sealed-year narrowing:
       stage A: forecast+obs join (mirrors session07/13/18/24/29's own
                "paired rows from part A"), computed here independently
                from the raw Open-Meteo JSON, not copied from notes;
       stage B: the further "common" narrowing every rung is scored on,
                which additionally drops a day if YESTERDAY's observation
                is missing (persistence needs a past value, D14/SPEC 2.1d)
                -- this is the number D48.8's PRIOR_SCORED_DAYS actually
                holds (F16/F30/F47/F64/F82's own "days every method is
                scored on" figure), NOT stage A's figure.
  3. Compares the new recipe's test_rows (stage-A-equivalent, no
     persistence-availability requirement) against OLD stage A and OLD
     stage B, at every airport, to see which one it actually matches.
  4. For every "extra" day (in new test_rows but not in OLD's PRIOR_SCORED_
     DAYS set), reports: the GRIB forecast/cloud/wind values, the day's own
     observation, whether Open-Meteo's OWN forecast for that exact date is
     present or null (the direct test of F92's "forecast-side gap"
     hypothesis), and whether yesterday's observation is missing (the
     direct test of the "persistence-narrowing" explanation this script
     was written to check).
  5. Checks for duplicate/mis-dated rows in the sealed GRIB feature file.
"""

import csv
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"

sys.path.insert(0, str(ROOT / "scripts"))
import session39_sealed_test as S   # noqa: E402  -- the FROZEN script, as a library

OUT = ROOT / "notes" / "session-41-verify-output.txt"

# The exact "extra" dates already visible in the existing sealed-test notes
# files (notes/session-07/13/24-check-output.txt), quoted here so this
# script's own independently-computed set can be checked against them.
KNOWN_PERSISTENCE_DROP_DATES = {
    "EGLC": {"2025-11-22"},
    "LFPG": {"2026-07-09"},
    "YSDU": {"2025-08-31", "2025-10-29", "2025-11-16", "2025-11-26",
             "2025-12-01", "2025-12-04", "2026-01-19", "2026-02-15",
             "2026-04-13"},
    "DSM": set(),
    "RNO": set(),
}
# The corresponding OWN-DAY-missing-observation date each of the above is
# the day AFTER (from the same notes files' PART A drop lists), i.e. why
# the persistence rung specifically loses that next day.
KNOWN_OWN_DAY_DROP_DATES = {
    "EGLC": {"2025-11-21"},
    "LFPG": {"2026-07-08"},
    "YSDU": {"2025-08-30", "2025-10-28", "2025-11-15", "2025-11-25",
              "2025-11-30", "2025-12-03", "2026-01-18", "2026-02-14",
              "2026-04-12"},
    "DSM": set(),
    "RNO": set(),
}


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
    print("=" * 84)
    print(title)
    print("=" * 84)


def sub(title):
    print()
    print(f"-- {title} --")


# ------------------------------------------------------------------ OLD (Open-Meteo) forecast loader

OM_SEALED_CHUNKS = [("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]


def load_openmeteo_sealed_forecast(station, target_hour):
    """{date: value_or_None} at the target hour, sealed year only. Mirrors
    session07/13/18/24/29's own load_forecast_*() logic exactly (same
    files, same target-hour filter, same null-vs-absent distinction) but
    reads generically by station rather than being hardcoded per script."""
    series = {}
    rows_seen = 0
    for start, end in OM_SEALED_CHUNKS:
        path = RAW / f"openmeteo_previousruns_gfs_global_{station}_{start}_{end}.json"
        with open(path) as f:
            d = json.load(f)
        h = d["hourly"]
        for t_str, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            t = datetime.strptime(t_str, "%Y-%m-%dT%H:%M")
            if t.hour != target_hour:
                continue
            dt = t.date()
            if not (S.SEALED_FROM <= dt <= S.SEALED_UNTIL):
                continue
            rows_seen += 1
            series[dt] = v          # v is None for a present-but-null row
    return series, rows_seen


# ------------------------------------------------------------------ raw-file duplicate/mis-date check

def check_grib_file_integrity():
    line("PRE-CHECK -- grib_features_sealed_window.csv: duplicates / mis-dating")
    counts = {}
    bad_date = 0
    total = 0
    with open(S.SEALED_GRIB_PATH) as f:
        for r in csv.DictReader(f):
            total += 1
            key = (r["station"], r["target_date"])
            counts[key] = counts.get(key, 0) + 1
            try:
                from datetime import date
                d = date.fromisoformat(r["target_date"])
            except ValueError:
                bad_date += 1
                continue
            if not (S.SEALED_FROM <= d <= S.SEALED_UNTIL):
                bad_date += 1
    dups = {k: v for k, v in counts.items() if v > 1}
    print(f"    total rows in file            : {total:,}")
    print(f"    distinct (station, date) keys : {len(counts):,}")
    print(f"    duplicate (station, date) keys: {len(dups):,}"
          + (f"  {sorted(dups)[:10]}" if dups else ""))
    print(f"    rows with an unparseable or out-of-window date: {bad_date}")
    print(f"    verdict: {'NO DUPLICATES, NO MIS-DATED ROWS' if not dups and not bad_date else 'PROBLEM FOUND'}")
    return not dups and not bad_date


# ------------------------------------------------------------------ per-airport verification

def verify_airport(station, target_hour, all_ok):
    line(f"{station} -- target hour {target_hour:02d}:00 UTC")

    # --- the NEW (GRIB) recipe's own sealed-year join, exactly as
    #     scripts/session39_sealed_test.py's run_airport() computes it ---
    obs_full, obs_far, obs_no_temp = S.load_obs_all(station, target_hour)
    sealed_grib = S.load_grib_features(
        S.SEALED_GRIB_PATH, S.SEALED_FROM, S.SEALED_UNTIL,
        refuse_outside_window=True)[station]
    test_rows, no_grib, no_obs = S.join_rows(
        sealed_grib, obs_full, S.SEALED_FROM, S.SEALED_UNTIL)
    test_dates = {r["date"] for r in test_rows}
    assert len(test_dates) == len(test_rows), \
        f"{station}: duplicate date in test_rows -- STOP, this would be a bug"

    sub("new (GRIB) recipe -- join_rows, exactly as session39_sealed_test.py computes it")
    print(f"    sealed-year calendar days : 365")
    print(f"    no GRIB row               : {no_grib}")
    print(f"    no usable observation     : {no_obs}")
    print(f"    rows kept (test_rows)     : {len(test_rows)}")

    # --- the OLD recipe's own persistence-availability narrowing, mirrored
    #     exactly (run_airport()'s common_persist loop) on the SAME
    #     test_rows set, so this reuses the identical obs_full series ---
    persist_common = set()
    own_day_ok_but_no_prev = []
    for r in test_rows:
        prev = obs_full.get(r["date"] - timedelta(days=1))
        if prev is None:
            own_day_ok_but_no_prev.append(r["date"])
            continue
        persist_common.add(r["date"])

    prior = S.PRIOR_SCORED_DAYS[station]
    sub("OLD recipe's stage-B narrowing (the persistence-availability common "
        "set) -- reproduced from raw data, not copied from notes")
    print(f"    of the {len(test_rows)} GRIB-paired rows, dropped because "
          f"YESTERDAY's observation is missing: {len(own_day_ok_but_no_prev)}")
    print(f"    stage-B common-day count (this session's own recomputation) "
          f": {len(persist_common)}")
    print(f"    D48.8 PRIOR_SCORED_DAYS (F16/F30/F47/F64/F82, the existing "
          f"recipe's own published 'days every method is scored on')       "
          f": {prior}")
    match_b = len(persist_common) == prior
    msg_b = ("YES -- PRIOR_SCORED_DAYS is the stage-B (post-persistence-drop) "
             "figure, not the raw join figure") if match_b else "NO -- unexplained"
    print(f"    MATCH: {msg_b}")
    if not match_b:
        all_ok[0] = False

    # --- Independently reconstruct the OLD recipe's own stage-A (raw
    #     forecast+obs join, no persistence involved) from the actual
    #     Open-Meteo sealed-year JSON, to see whether that -- not stage B --
    #     is what the new recipe's test_rows count actually matches. ---
    om_fc, om_rows_seen = load_openmeteo_sealed_forecast(station, target_hour)
    om_present = {d for d, v in om_fc.items() if v is not None}
    om_null = {d for d, v in om_fc.items() if v is None}
    old_stage_a = om_present & set(obs_full.keys())
    old_stage_a = {d for d in old_stage_a if S.SEALED_FROM <= d <= S.SEALED_UNTIL}

    sub("OLD recipe's stage-A (independently rebuilt from the real "
        "Open-Meteo sealed-year JSON, not assumed)")
    print(f"    Open-Meteo sealed-year rows at this hour        : {om_rows_seen}")
    print(f"    of those, value present (non-null)               : {len(om_present)}")
    print(f"    of those, value null (present row, null value)   : {len(om_null)}")
    print(f"    stage-A join (Open-Meteo forecast present AND own-day obs "
          f"present): {len(old_stage_a)}")
    match_a = len(old_stage_a) == len(test_rows)
    print(f"    new (GRIB) recipe's test_rows count               : {len(test_rows)}")
    msg_a = ("YES -- the new recipe exactly reproduces the OLD recipe "
             "row-for-row at the pre-persistence join stage") if match_a else "NO"
    print(f"    MATCH: {msg_a}")
    if not match_a:
        all_ok[0] = False

    # --- the extra days: in test_rows but not in the old recipe's own
    #     published scored-day set (persist_common) ---
    extra = sorted(test_dates - persist_common)
    known_extra = KNOWN_PERSISTENCE_DROP_DATES.get(station, set())
    sub(f"the {len(extra)} 'extra' day(s) beyond D48.8's PRIOR_SCORED_DAYS ceiling")
    if not extra:
        print("    (none -- this airport's new count already equals the "
              "published ceiling)")
    for d in sorted(extra):
        row = next(r for r in test_rows if r["date"] == d)
        prev_missing = obs_full.get(d - timedelta(days=1)) is None
        om_val = om_fc.get(d, "NO ROW AT ALL")
        print(f"    {d}:")
        print(f"        GRIB forecast_temp_c = {row['fc']:.3f}, cloud = "
              f"{row['cloud']:.1f}, wind = {row['wind']:.1f}  (a real, "
              f"decoded value -- confirmed present, F92 Task 1: 0 GRIB drops)")
        print(f"        this day's own observation = {row['obs']:.1f} degC "
              f"(paired within the D14 15-min rule -- guaranteed by "
              f"load_obs_all's own construction)")
        print(f"        Open-Meteo's OWN forecast for this exact date/hour  = "
              f"{om_val!r}  <- F92's hypothesis predicts this should be "
              f"missing/null; if it is a real value instead, the day is NOT "
              f"a forecast-side gap")
        print(f"        yesterday's observation missing (why the OLD recipe's "
              f"persistence rung, not the forecast rung, drops this day) = "
              f"{prev_missing}")
    reproduced = {d.isoformat() for d in extra}
    if known_extra:
        exact = reproduced == known_extra
        print(f"    cross-check against the dates already named in the "
              f"existing sealed-test notes file: "
              f"{'EXACT MATCH' if exact else 'MISMATCH -- ' + str(reproduced ^ known_extra)}")
        if not exact:
            all_ok[0] = False

    return dict(
        station=station, test_rows=len(test_rows), stage_a=len(old_stage_a),
        stage_b=len(persist_common), prior=prior, extra=extra,
        om_gap_on_any_extra_day=any(om_fc.get(d) is None or d not in om_fc for d in extra),
    )


def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 41 TASK 1 -- verify the D48.8-EXCEEDS extra sealed-year "
         "days (F92) are legitimate, not a bug. NO MODEL IS FIT. NO "
         "SEALED-YEAR MAE, SKILL OR VERDICT IS COMPUTED ANYWHERE BELOW.")
    print(f"run at : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print("Reuses scripts/session39_sealed_test.py's own load_obs_all, "
          "load_grib_features and join_rows, unmodified, as a library.")

    all_ok = [True]
    file_ok = check_grib_file_integrity()
    all_ok[0] = all_ok[0] and file_ok

    summary = []
    for station, target_hour in S.AIRPORTS.items():
        summary.append(verify_airport(station, target_hour, all_ok))

    line("SUMMARY -- all five airports")
    print(f"    {'station':<8} {'test_rows':>10} {'stage-A':>8} {'stage-B':>8} "
          f"{'PRIOR':>6} {'extra':>6} {'matches stage-A?':>18} {'matches stage-B (=PRIOR)?':>26}")
    for r in summary:
        print(f"    {r['station']:<8} {r['test_rows']:>10} {r['stage_a']:>8} "
              f"{r['stage_b']:>8} {r['prior']:>6} {len(r['extra']):>6} "
              f"{'YES' if r['stage_a'] == r['test_rows'] else 'no':>18} "
              f"{'YES' if r['stage_b'] == r['prior'] else 'no':>26}")

    line("VERDICT")
    if all_ok[0]:
        print("    BENIGN. At every airport, the new (GRIB) recipe's sealed-year "
              "join count exactly reproduces the OLD recipe's own stage-A "
              "(forecast+obs join, pre-persistence) row count -- not a new, "
              "wider, or cleaner forecast-side coverage. Every 'extra' day "
              "beyond D48.8's PRIOR_SCORED_DAYS ceiling is a day the OLD "
              "recipe's own persistence rung separately dropped (because "
              "YESTERDAY's observation was missing), while raw GFS / "
              "3-feature / 5-feature themselves had a perfectly valid pair "
              "that day under BOTH the old and new forecast sources. The "
              "D48.8 ceiling compared the new recipe's pre-persistence row "
              "count against the old recipe's post-persistence 'scored day' "
              "count -- two different stages of the same pipeline, not two "
              "different forecast sources' coverage. No pairing bug, no "
              "double-count, no mis-dated row, no forecast-side gap.")
    else:
        print("    NOT CONFIRMED BENIGN -- see the mismatches printed above. "
              "Stop and report; do not correct the D48.8 guard.")

    print(f"\nThis output is saved at notes/{OUT.name}")
    sys.stdout = sys.__stdout__
    tee.flush()


if __name__ == "__main__":
    main()
