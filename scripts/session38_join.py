"""Session 38, Task 2: join the step-2 GRIB feature dataset to the existing
IEM observations, at each airport's own target hour, over the full v16
window (2021-03-24 to 2025-07-31).

ONE JOB: produce one row per (station, date) carrying the GRIB forecast
features (temperature, cloud cover, wind speed -- already elevation-
corrected and validated, session 37/F90) and the paired IEM observation, with
the residual target (observed minus forecast, SPEC 4.2). Reuses the
established D14 pairing rule (SPEC 4.5: nearest routine report to the target
hour, dropped if more than 15 minutes away) -- the same rule sessions 32/33
used, applied here to the GRIB dataset instead of Open-Meteo's. Nothing is
re-pulled: this reads the already-assembled data/processed/
grib_features_v16_window.csv (session 37) and the existing IEM ASOS chunk
files under data/raw/.

Missing data is dropped and counted, never filled (SPEC 2.2). No sealed-test
date (2025-08-01 onward) is loaded or scored -- asserted below.
"""

import csv
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

WINDOW_START = date(2021, 3, 24)
WINDOW_END = date(2025, 7, 31)
SEALED_FROM = date(2025, 8, 1)

# SPEC 3.4: station -> target hour (UTC).
AIRPORTS = {
    "EGLC": 12,
    "LFPG": 12,
    "DSM": 18,
    "YSDU": 2,
    "RNO": 20,
}

# The yearly IEM chunk files that cover the full v16 window, per airport
# (established naming convention -- sessions 03b/10/14/15/19/20/25/26).
OBS_CHUNKS = [
    ("2021-03-24", "2021-12-31"),
    ("2022-01-01", "2022-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2025-01-01", "2025-12-31"),
]

OUT = ROOT / "notes" / "session-38-join-output.txt"


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
    print("=" * 78)
    print(title)
    print("=" * 78)


def sub(title):
    print()
    print(f"-- {title} --")


def load_grib_features():
    """station -> {date: {fc, cloud, wind}}, restricted to the v16 window."""
    out = {st: {} for st in AIRPORTS}
    with open(PROCESSED / "grib_features_v16_window.csv") as f:
        for r in csv.DictReader(f):
            st = r["station"]
            if st not in out:
                continue
            d = date.fromisoformat(r["target_date"])
            assert WINDOW_START <= d <= WINDOW_END
            assert d < SEALED_FROM, "a sealed-test date is present in the GRIB feature file"
            out[st][d] = {
                "fc": float(r["temperature_grib_c"]),
                "cloud": float(r["cloud_cover_grib_pct"]),
                "wind": float(r["wind_speed_grib_kmh"]),
            }
    return out


def load_obs(station, target_hour):
    """{date: temp} for the target hour, D14 pairing rule (SPEC 4.5): nearest
    routine report, dropped if more than 15 minutes from the hour. Restricted
    to the v16 window; never loads a date on or after SEALED_FROM."""
    series = {}
    outside_15min = 0
    no_temp = 0
    for start, end in OBS_CHUNKS:
        path = RAW / f"iem_asos_{station}_{start}_{end}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != target_hour:
                    continue
                dt = nearest.date()
                if dt < WINDOW_START or dt > WINDOW_END:
                    continue
                if dt >= SEALED_FROM:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    outside_15min += 1
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    no_temp += 1
                    continue
                series[dt] = float(raw)
    return series, outside_15min, no_temp


def all_days(start, end):
    out = []
    d = start
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 38 TASK 2 -- join GRIB features to IEM observations, full "
         "v16 window. SEALED TEST NOT OPENED.")
    print(f"run at        : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"window        : {WINDOW_START} to {WINDOW_END}")
    print(f"sealed test   : {SEALED_FROM} onward -- NOT LOADED")

    grib = load_grib_features()

    all_rows = []
    total_window_days = len(all_days(WINDOW_START, WINDOW_END))

    for station, target_hour in AIRPORTS.items():
        line(f"{station} -- target hour {target_hour:02d}:00 UTC (SPEC 3.4)")

        obs, obs_far, obs_no_temp = load_obs(station, target_hour)
        g = grib[station]

        no_grib_row = 0
        no_obs = 0
        kept = 0
        first_date = last_date = None

        for d in all_days(WINDOW_START, WINDOW_END):
            g_val = g.get(d)
            if g_val is None:
                no_grib_row += 1
                continue
            o_val = obs.get(d)
            if o_val is None:
                no_obs += 1
                continue
            all_rows.append({
                "station": station,
                "target_date": d.isoformat(),
                "target_hour": target_hour,
                "forecast_temp_c": g_val["fc"],
                "cloud_cover": g_val["cloud"],
                "wind_speed_10m": g_val["wind"],
                "obs_temp_c": o_val,
                "resid": round(o_val - g_val["fc"], 4),
            })
            kept += 1
            if first_date is None:
                first_date = d
            last_date = d

        sub("Task 2 -- drop counts")
        print(f"    calendar days in the v16 window: {total_window_days}")
        print(f"    no GRIB feature row for this date "
              f"(session 37's own drops -- idx-mismatch or missing extract): "
              f"{no_grib_row}")
        print(f"    GRIB row present but no usable observation           : {no_obs}")
        print(f"      (of which, obs >15 min from target hour, dropped by D14: "
              f"{obs_far})")
        print(f"      (of which, obs report carried no temperature value): "
              f"{obs_no_temp}")
        print(f"    rows kept: {kept} of {total_window_days}")
        if first_date:
            print(f"    kept date range: {first_date} to {last_date}")

    sub("total across all five airports")
    print(f"    total rows kept: {len(all_rows)} "
          f"(of a possible {total_window_days * len(AIRPORTS)})")

    out_csv = PROCESSED / "session38_joined.csv"
    fieldnames = ["station", "target_date", "target_hour", "forecast_temp_c",
                  "cloud_cover", "wind_speed_10m", "obs_temp_c", "resid"]
    with open(out_csv, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(all_rows)
    print(f"\nWrote joined dataset: {out_csv} ({len(all_rows)} rows)")

    for r in all_rows:
        d = date.fromisoformat(r["target_date"])
        assert d < SEALED_FROM

    line("END")
    print("Raw files untouched (read-only). Nothing was filled (SPEC 2.2). "
          "No forecast or observation date on or after 2025-08-01 was "
          "loaded, joined, or written, for any airport. No model fitted, no "
          "recipe locked. Nothing was committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
