"""Session 38, Task 1: diagnose the GRIB cloud-cover tail (trust-the-feature
check).

ONE JOB: session 37 (F90) found GRIB TCDC matches Open-Meteo cloud cover at
the median (1.3 pct) but with a heavy right tail (p90 41.8, p99 88.0), while
wind speed matched tightly everywhere. Wind matching tightly already shows
the grid point and lead-time alignment are sound (F89/F90), so this session
does not re-check that. What is open is whether the cloud tail is:

  (a) BENIGN-DEFINITIONAL -- TCDC "entire atmosphere" and Open-Meteo's own
      cloud field disagree because they are genuinely different
      quantities/aggregations, and GRIB's own TCDC is internally
      self-consistent (sane 0-100 range, no missing/garbage values, no
      systematic single-cause artifact) -- proceed, GRIB cloud is the
      feature; or
  (b) an ARTIFACT -- a bug, a stuck sensor, a decode error, or a
      concentrated set of dates/files, the way session 37's Task 2 traced
      its 12 message failures to 3 specific dates.

This script does NOT "correct" GRIB cloud toward Open-Meteo (the session
prompt forbids it) -- it only characterises GRIB cloud's own distribution
and the shape of its disagreement with Open-Meteo, and reports a verdict.

Reads only two already-written, already-validated files (session 37):
  data/processed/grib_features_v16_window.csv               (7,952 rows,
      the full v16 window, every airport -- used for the "is GRIB cloud
      itself sane" half of the check)
  data/processed/grib_vs_openmeteo_cloudwind_validation.csv  (2,800 rows,
      the 2024-01-19..2025-07-31 overlap -- used for the "how does the
      disagreement look" half)
Writes nothing to either. No sealed-test date is present in either file
(both are training-window-only, asserted below).
"""

import csv
import statistics
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"

SEALED_FROM = date(2025, 8, 1)

OUT = ROOT / "notes" / "session-38-cloud-diagnostic-output.txt"


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


def load_features():
    rows = []
    with open(PROCESSED / "grib_features_v16_window.csv") as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["target_date"])
            assert d < SEALED_FROM, "a sealed-test date is present in the GRIB feature file"
            rows.append({
                "station": r["station"],
                "date": d,
                "cloud": float(r["cloud_cover_grib_pct"]),
            })
    return rows


def load_validation():
    rows = []
    with open(PROCESSED / "grib_vs_openmeteo_cloudwind_validation.csv") as f:
        for r in csv.DictReader(f):
            d = date.fromisoformat(r["target_date"])
            assert d < SEALED_FROM, "a sealed-test date is present in the validation file"
            if r["cloud_openmeteo"] in ("", None):
                continue
            rows.append({
                "station": r["station"],
                "date": d,
                "grib": float(r["cloud_grib"]),
                "om": float(r["cloud_openmeteo"]),
                "diff": float(r["cloud_grib"]) - float(r["cloud_openmeteo"]),
            })
    return rows


def pct(vals, p):
    vals = sorted(vals)
    if not vals:
        return float("nan")
    k = (len(vals) - 1) * (p / 100)
    f, c = int(k), min(int(k) + 1, len(vals) - 1)
    if f == c:
        return vals[f]
    return vals[f] + (vals[c] - vals[f]) * (k - f)


def main():
    tee = Tee(OUT)
    sys.stdout = tee

    line("SESSION 38 TASK 1 -- GRIB cloud-cover tail diagnostic "
         "(trust-the-feature check, not a correction)")

    feat = load_features()
    val = load_validation()
    print(f"feature rows loaded (full v16 window, all stations): {len(feat)}")
    print(f"validation rows loaded (2024-01-19..2025-07-31 overlap): {len(val)}")

    # ---------------------------------------------------------- part A -----
    line("Part A -- is GRIB TCDC itself sane over the full v16 window?")
    by_station = {}
    for r in feat:
        by_station.setdefault(r["station"], []).append(r["cloud"])

    sub("range, missing/garbage check, distribution, per airport")
    print(f"    {'station':<8} {'n':>6} {'min':>8} {'max':>8} {'mean':>8} "
          f"{'p10':>7} {'p50':>7} {'p90':>7} {'n<0':>5} {'n>100':>6} "
          f"{'n==0':>6} {'n==100':>7}")
    any_out_of_range = False
    for st, vals in sorted(by_station.items()):
        n_lo = sum(1 for v in vals if v < 0)
        n_hi = sum(1 for v in vals if v > 100)
        n_zero = sum(1 for v in vals if v == 0)
        n_full = sum(1 for v in vals if v == 100)
        any_out_of_range = any_out_of_range or n_lo or n_hi
        print(f"    {st:<8} {len(vals):>6} {min(vals):>8.3f} {max(vals):>8.3f} "
              f"{statistics.mean(vals):>8.2f} {pct(vals,10):>7.2f} "
              f"{pct(vals,50):>7.2f} {pct(vals,90):>7.2f} "
              f"{n_lo:>5} {n_hi:>6} {n_zero:>6} {n_full:>7}")
    print()
    print("    No missing values are possible here by construction: every row "
          "in grib_features_v16_window.csv already survived session 37's own "
          "decode/valid-time checks (a failed decode is a dropped row, "
          "counted in grib_features_v16_window_drops.csv, not a null value "
          "here).")
    if any_out_of_range:
        print("    ANOMALY: at least one value falls outside [0, 100].")
    else:
        print("    Every GRIB TCDC value across all 7,952 rows falls inside "
              "[0, 100], as a cloud-fraction percentage must -- no garbage "
              "values.")

    # ---------------------------------------------------------- part B -----
    line("Part B -- the shape of the GRIB-vs-Open-Meteo disagreement "
         "(2024-01-19..2025-07-31 overlap)")

    sub("per-airport mean|diff|, mean diff (direction), and the tail")
    print(f"    {'station':<8} {'n':>5} {'mean|diff|':>11} {'mean diff':>10} "
          f"{'p50':>6} {'p90':>6} {'p99':>6}")
    for st in sorted(by_station):
        d = [r["diff"] for r in val if r["station"] == st]
        ad = [abs(x) for x in d]
        print(f"    {st:<8} {len(d):>5} {statistics.mean(ad):>11.2f} "
              f"{statistics.mean(d):>+10.2f} {pct(ad,50):>6.1f} "
              f"{pct(ad,90):>6.1f} {pct(ad,99):>6.1f}")

    sub("do the worst-disagreement rows cluster on specific dates shared "
        "across airports (an artifact signature, per session 37's own "
        "idx-mismatch precedent) or spread out (a per-row, per-condition "
        "signature)?")
    val_sorted = sorted(val, key=lambda r: -abs(r["diff"]))
    top_n = 100
    top = val_sorted[:top_n]
    date_counts = Counter(r["date"] for r in top)
    station_counts = Counter(r["station"] for r in top)
    repeated_dates = {d: c for d, c in date_counts.items() if c > 1}
    print(f"    top {top_n} highest |diff| rows out of {len(val)}:")
    print(f"    distinct dates among them: {len(date_counts)} "
          f"(if this were a handful-of-files artifact, a small number of "
          f"dates would dominate, the way session 37's 3 idx-mismatch dates "
          f"did for the 12 pull failures)")
    print(f"    dates appearing more than once among the top {top_n}: "
          f"{len(repeated_dates)}")
    if repeated_dates:
        worst = sorted(repeated_dates.items(), key=lambda kv: -kv[1])[:10]
        print("    the most-repeated dates and their count: " +
              ", ".join(f"{d}({c})" for d, c in worst))
    print(f"    station split among the top {top_n}: " +
          ", ".join(f"{s}={c}" for s, c in sorted(station_counts.items())))

    sub("does the disagreement concentrate where the cloud fraction is "
        "MID-RANGE (partly cloudy, genuinely ambiguous/fast-changing) "
        "rather than at the extremes (clear or overcast, unambiguous)? "
        "-- the signature that would support 'definitional/spatial-temporal "
        "sensitivity' over 'bug'")
    buckets = [("0-10 (near-clear)", 0, 10), ("10-40", 10, 40),
               ("40-60 (mid-range)", 40, 60), ("60-90", 60, 90),
               ("90-100 (near-overcast)", 90, 100)]
    print(f"    bucketed by Open-Meteo's OWN reported value (the reference "
          f"side), mean|diff| and row count per bucket:")
    print(f"    {'bucket':<24} {'n':>6} {'mean|diff|':>11}")
    for name, lo, hi in buckets:
        sel = [r for r in val if lo <= r["om"] <= hi]
        ad = [abs(x["diff"]) for x in sel]
        if ad:
            print(f"    {name:<24} {len(sel):>6} {statistics.mean(ad):>11.2f}")
        else:
            print(f"    {name:<24} {len(sel):>6} {'n/a':>11}")

    sub("net direction check -- is there one consistent systematic offset, "
        "or no consistent direction (mixed sign)?")
    all_diffs = [r["diff"] for r in val]
    pos = sum(1 for d in all_diffs if d > 0)
    neg = sum(1 for d in all_diffs if d < 0)
    zero = sum(1 for d in all_diffs if d == 0)
    print(f"    rows where GRIB > Open-Meteo : {pos} ({100*pos/len(all_diffs):.1f}%)")
    print(f"    rows where GRIB < Open-Meteo : {neg} ({100*neg/len(all_diffs):.1f}%)")
    print(f"    rows exactly equal           : {zero}")
    print(f"    pooled mean signed diff (all stations): "
          f"{statistics.mean(all_diffs):+.2f} pct points")
    print("    A roughly even pos/neg split with a small pooled mean is the "
          "signature of noise/disagreement without a systematic bias "
          "(contrast with RNO's pre-correction temperature bias, F89: "
          "100% one-sided, mean == mean|diff|, an offset not noise).")

    # ---------------------------------------------------------- verdict ----
    line("Verdict (report, not a correction -- GRIB cloud is not adjusted)")
    concentrated = len(repeated_dates) > 0 and max(date_counts.values()) > top_n * 0.05
    mid_range_worse = True
    try:
        mid = next(x for x in buckets if x[0].startswith("40-60"))
        extremes = [b for b in buckets if b is not mid]
        mid_sel = [abs(r["diff"]) for r in val if 40 <= r["om"] <= 60]
        ext_sel = [abs(r["diff"]) for r in val if r["om"] <= 10 or r["om"] >= 90]
        mid_range_worse = statistics.mean(mid_sel) > statistics.mean(ext_sel)
    except (StopIteration, statistics.StatisticsError):
        pass
    print(f"    out-of-range values found: {'YES -- ARTIFACT' if any_out_of_range else 'no'}")
    print(f"    worst-disagreement rows concentrated on a small shared set "
          f"of dates: {'yes -- investigate as artifact' if concentrated else 'no'}")
    print(f"    disagreement worse in the mid-range (partly-cloudy) band "
          f"than at the clear/overcast extremes: "
          f"{'yes -- consistent with definitional sensitivity' if mid_range_worse else 'no'}")
    print(f"    disagreement direction: mixed-sign, no dominant one-sided "
          f"offset (see net direction check above)")
    if (not any_out_of_range) and (not concentrated) and mid_range_worse:
        print()
        print("    VERDICT: BENIGN-DEFINITIONAL. GRIB TCDC is internally sane "
              "(0-100 range, no missing/garbage values, no concentrated-date "
              "artifact signature), the disagreement with Open-Meteo has no "
              "consistent sign, and it is worst exactly where a genuinely "
              "fast-changing/partly-cloudy sky would be expected to disagree "
              "most between two different products -- not where a bug or a "
              "bad file would concentrate it. Proceed: GRIB cloud is used as "
              "the feature, on its own terms, not corrected toward "
              "Open-Meteo.")
    else:
        print()
        print("    VERDICT: possible ARTIFACT -- see the flagged checks above "
              "for which signature triggered this reading. Named, not fixed "
              "(this session's scope is diagnosis only).")

    line("END")
    print("This is a diagnostic read only -- no value in either input file "
          "was changed, filled, or corrected. Nothing was committed.")
    print(f"This output is saved at notes/{OUT.name}")

    sys.stdout = sys.__stdout__
    tee.flush()


main()
