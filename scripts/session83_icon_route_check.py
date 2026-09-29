"""Session 83, Step 2: a read-only check of Open-Meteo's ICON routes
(DECISIONS D75.1). Recorded as F124.

It reads the network and prints. It writes no data file.

Three questions, all at EGLC (SPEC 3.4), model `icon_global`, with the
default grid-cell selection:
  (a) On the past-run route (Previous Runs API): the first day
      `shortwave_radiation_previous_day1` and `_day2` are present, against
      `temperature_2m_previous_day1`'s floor.
  (b) On the Single Runs API: does it serve `icon_global` from 2026-04-02,
      with 850 hPa temperature, and the 18z cycle?
  (c) Timing: does `temperature_2m_previous_day1` at hour H equal the
      Single Runs value from the run at floor(H/6)x6 UTC on the day before,
      at lead 24 + (H mod 6)? (The GFS convention, DECISIONS F5, F89.)

Scope (session 83 prompt, hard scope guard):
- No forecast value is printed or saved. Only HTTP status, error reasons,
  grid metadata, valid-time ranges, present/null counts and match counts.
- No observation is read, and nothing is scored.
- No request asks for a valid time after 2026-07-31. If a response holds
  any valid time after 2026-07-31T23:00 UTC anyway, it is discarded before
  any value is read, that fact is printed, and that sub-check stops.
"""

import sys
import time
from datetime import date, datetime, timedelta

import requests

PAST_RUNS = "https://previous-runs-api.open-meteo.com/v1/forecast"
SINGLE_RUNS = "https://single-runs-api.open-meteo.com/v1/forecast"

LAT, LON = 51.5053, 0.0553          # EGLC, SPEC 3.4
MODEL = "icon_global"
LAST_ALLOWED = "2026-07-31T23:00"   # scope guard: no valid time after this

RETRIES = 3                          # at most 3 retries per request
RETRY_WAIT = [5, 15, 30]             # seconds, politely spaced
PAUSE = 1.0                          # seconds between requests


class OutOfScope(Exception):
    """A response held a valid time after 2026-07-31T23:00."""


def get(url, params):
    """GET with at most RETRIES retries. Returns (response or None, note)."""
    last_note = ""
    for attempt in range(RETRIES + 1):
        if attempt:
            time.sleep(RETRY_WAIT[attempt - 1])
        try:
            r = requests.get(url, params=params, timeout=60)
        except requests.RequestException as e:
            last_note = f"request error: {type(e).__name__}: {str(e)[:150]}"
            print(f"    attempt {attempt + 1}: {last_note}")
            continue
        if r.status_code >= 500 or r.status_code == 429:
            last_note = f"HTTP {r.status_code}"
            print(f"    attempt {attempt + 1}: HTTP {r.status_code}, will retry")
            continue
        time.sleep(PAUSE)
        return r, ""
    return None, last_note


def fetch(label, url, params):
    """Make one request and print its metadata. Applies the valid-time rule
    before any value is touched. Returns the parsed `hourly` block, or None."""
    print(f"\n  [{label}]")
    r, note = get(url, params)
    if r is None:
        print(f"    FAILED after {RETRIES} retries: {note}")
        return None
    print(f"    URL    : {r.url}")
    print(f"    status : HTTP {r.status_code}")
    try:
        js = r.json()
    except ValueError:
        print(f"    reason : response is not JSON: {r.text[:150]!r}")
        return None
    if js.get("error") or r.status_code != 200:
        print(f"    reason : {str(js.get('reason', ''))[:150]}")
        return None
    print(f"    grid   : latitude {js.get('latitude')}, longitude "
          f"{js.get('longitude')}, elevation {js.get('elevation')} m")
    hourly = js.get("hourly") or {}
    times = hourly.get("time") or []
    if not times:
        print("    valid times: none returned")
        return hourly
    print(f"    valid times: {times[0]} .. {times[-1]}  ({len(times)} hours)")
    # Scope guard, before any value is read.
    if max(times) > LAST_ALLOWED:
        del js, hourly
        print(f"    SCOPE GUARD: this response holds a valid time after "
              f"{LAST_ALLOWED}. It was discarded without reading any value.")
        raise OutOfScope(label)
    return hourly


def counts(hourly, var):
    """(present, null) hour counts for one variable, or None if absent."""
    if var not in hourly:
        return None
    vals = hourly[var]
    present = sum(1 for v in vals if v is not None)
    return present, len(vals) - present


def first_present(hourly, var):
    for t, v in zip(hourly.get("time", []), hourly.get(var, [])):
        if v is not None:
            return t
    return None


def print_counts(hourly, variables):
    for var in variables:
        c = counts(hourly, var)
        if c is None:
            print(f"    {var:<40} not in response")
        else:
            print(f"    {var:<40} present {c[0]:>5}, null {c[1]:>5}")


# ------------------------------------------------------------------ (a)

def check_a():
    print("\n" + "=" * 78)
    print("2(a) Radiation floor on the past-run route (Previous Runs API)")
    print("=" * 78)
    variables = ["shortwave_radiation_previous_day1",
                 "shortwave_radiation_previous_day2",
                 "temperature_2m_previous_day1"]
    base = dict(latitude=LAT, longitude=LON, models=MODEL,
                hourly=",".join(variables), start_date="2024-01-17")

    end = date(2024, 1, 21)
    cap = date(2024, 12, 31)
    step = 0
    while True:
        params = dict(base, end_date=end.isoformat())
        hourly = fetch(f"2(a) window 2024-01-17..{end}", PAST_RUNS, params)
        if hourly is None:
            print("    sub-check (a) stopped: no usable response.")
            return
        print_counts(hourly, variables)
        firsts = {v: first_present(hourly, v) for v in variables}
        for v in variables:
            print(f"    first present valid time, {v:<34}: {firsts[v]}")
        rad_found = all(firsts[v] is not None for v in variables[:2])
        if rad_found or end >= cap:
            break
        # Widen the window by one month, up to 2024-12-31.
        step += 1
        m = end.month + 1
        y = end.year + (m > 12)
        m = (m - 1) % 12 + 1
        end = min(date(y, m, 21), cap)
        print(f"    radiation not yet present in both offsets; widening "
              f"(step {step}) to end {end}")

    print("\n  2(a) answer (counts only):")
    for v in variables:
        print(f"    {v:<40} first present: {firsts[v]}")
    if not rad_found:
        print("    radiation still not present in both offsets through "
              f"{end}.")


# ------------------------------------------------------------------ (b)

def check_b():
    print("\n" + "=" * 78)
    print("2(b) Single Runs: floor, 850 hPa temperature, 18z cycle")
    print("=" * 78)
    variables = ["temperature_850hPa", "temperature_2m", "shortwave_radiation"]
    for run in ["2026-04-01T18:00", "2026-04-02T00:00", "2026-07-29T18:00"]:
        params = dict(latitude=LAT, longitude=LON, models=MODEL, run=run,
                      hourly=",".join(variables), forecast_hours=48)
        try:
            hourly = fetch(f"2(b) run={run}", SINGLE_RUNS, params)
        except OutOfScope:
            print("    sub-check (b) stopped for this run (scope guard).")
            continue
        if hourly is None:
            continue
        print_counts(hourly, variables)


# ------------------------------------------------------------------ (c)

def check_c():
    print("\n" + "=" * 78)
    print("2(c) Timing: past-run previous_day1 against Single Runs, 2026-06-11")
    print("=" * 78)
    past_var = "temperature_2m_previous_day1"
    past = fetch("2(c) past run, 2026-06-11", PAST_RUNS,
                 dict(latitude=LAT, longitude=LON, models=MODEL,
                      hourly=past_var, start_date="2026-06-11",
                      end_date="2026-06-11"))
    if past is None:
        print("    sub-check (c) stopped: no usable past-run response.")
        return
    print_counts(past, [past_var])

    runs = {}
    for cyc in (0, 6, 12, 18):
        run = f"2026-06-10T{cyc:02d}:00"
        hourly = fetch(f"2(c) single run={run}", SINGLE_RUNS,
                       dict(latitude=LAT, longitude=LON, models=MODEL,
                            run=run, hourly="temperature_2m",
                            forecast_hours=54))
        if hourly is None:
            print(f"    run {run}: no usable response")
            runs[cyc] = None
            continue
        print_counts(hourly, ["temperature_2m"])
        runs[cyc] = dict(zip(hourly["time"], hourly["temperature_2m"]))

    past_by_time = dict(zip(past["time"], past[past_var]))
    matches = 0
    mismatches = []
    for h in range(24):
        vt = f"2026-06-11T{h:02d}:00"
        pv = past_by_time.get(vt)
        cyc = (h // 6) * 6
        run_vals = runs.get(cyc)
        sv = run_vals.get(vt) if run_vals else None
        # Lead of this valid time in the run at `cyc` on 2026-06-10.
        lead = int((datetime.fromisoformat(vt)
                    - datetime(2026, 6, 10, cyc)).total_seconds() // 3600)
        assert lead == 24 + (h % 6)
        if pv is not None and sv is not None and pv == sv:
            matches += 1
        else:
            others = [f"{c:02d}z" for c in (0, 6, 12, 18)
                      if c != cyc and runs.get(c)
                      and pv is not None and runs[c].get(vt) == pv]
            mismatches.append((h, pv is None, sv is None, others))

    print(f"\n  2(c) answer: {matches} of 24 hours match the run at "
          f"floor(H/6)x6 UTC on 2026-06-10, lead 24 + (H mod 6).")
    for h, pnull, snull, others in mismatches:
        why = []
        if pnull:
            why.append("past-run value null")
        if snull:
            why.append("expected run's value null or missing")
        print(f"    hour {h:02d}: no match"
              + (f" ({'; '.join(why)})" if why else "")
              + f"; equal in other 2026-06-10 runs: "
              + (", ".join(others) if others else "none"))


def main():
    print("Session 83, Step 2: ICON route check (DECISIONS D75.1)")
    print(f"run at   : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python   : {sys.version.split()[0]}, requests {requests.__version__}")
    print(f"location : EGLC, latitude {LAT}, longitude {LON} (SPEC 3.4); "
          f"model {MODEL}; default grid-cell selection")
    print(f"scope    : no valid time after {LAST_ALLOWED}; no value printed")
    check_a()
    check_b()
    try:
        check_c()
    except OutOfScope:
        print("    sub-check (c) stopped (scope guard).")
    print("\nEND. No value was printed or saved. No observation was read.")


if __name__ == "__main__":
    main()
