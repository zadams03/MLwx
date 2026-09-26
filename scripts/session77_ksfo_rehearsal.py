"""Session 77: KSFO rehearsal, column-order band, and look counts (D67.4,
D67.5, D69).

The rehearsal is NOT a gate (D67.4). The only stop is a bug, and a bug is
fixed in the pipeline, never in the recipe.

KSFO's held-out years (2024-08-01..2026-07-31) stay closed. Every feature
and observation row dated 2024-08-01 or later is dropped as it is read,
before any value in it is parsed, and only the number removed is printed.
After the drop, the KSFO rehearsal guard asserts that no row is dated
2024-08-01 or later. The one exception is --counts (Step 3), which reads
only dates, the station, the complete-case flag and the pairing status of
every row, and never a value.

Recipe (SPEC 8), reused read-only by import from the record script
(scripts/session62_reserved_confirm.py): LGB_PARAMS, BASE_KEYS,
FINAL_FEATURE_KEYS (the G15 order), features_matrix (which rebuilds
season_sin and season_cos from the date, as the record does) and mae (G24).
The fit is the record's call (G14): LGBMRegressor(**LGB_PARAMS).fit(x, y)
on a float64 array with no column names. Rows are in ascending date order
(G19). The target is obs - temperature_grib_c, unrounded (G20). The
prediction is temperature_grib_c + the predicted residual.

Folds: `2022-23` and `2023-24` of D51's EXPERIMENT_FOLDS, each passed
through assert_reserved_year_excluded() (both imported read-only from
scripts/session48_reserved_year.py).

Usage (offline):
  python scripts/session77_ksfo_rehearsal.py --rehearse   Step 2: load,
                                                          checks, 2a, 2b, 2c
  python scripts/session77_ksfo_rehearsal.py --repeat     determinism:
                                                          record-order
                                                          B+D,L,R,T again,
                                                          in its own process
  python scripts/session77_ksfo_rehearsal.py --counts     Step 3: look
                                                          counts, dates only

Every output path is new; the script refuses to overwrite (SPEC 8.7
item 5). Outputs go to data/rebuild/session77/. Printed output is appended
to notes/session-77-output.txt.
"""

import sys

sys.dont_write_bytecode = True
import os  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Importing the record script runs its libomp loader shim (D24) first.
import session62_reserved_confirm as rec  # noqa: E402
from session48_reserved_year import (  # noqa: E402
    EXPERIMENT_FOLDS,
    assert_reserved_year_excluded,
)

import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
from datetime import date, timedelta  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm  # noqa: E402

ROOT = str(rec.ROOT)
PROCESSED = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
OUT_DIR = os.path.join(ROOT, "data", "rebuild", "session77")
RUN2_DIR = os.path.join(OUT_DIR, "run2")
LOG_PATH = os.path.join(ROOT, "notes", "session-77-output.txt")

FEATURES = os.path.join(PROCESSED, "session76_ksfo_features.csv")
OBS = os.path.join(PROCESSED, "session76_ksfo_observations.csv")
ORDERINGS = os.path.join(ROOT, "data", "rebuild", "session75", "orderings.csv")
OM_TEMP = [os.path.join(RAW, n) for n in [
    "openmeteo_previousruns_gfs_global_SFO_2021-03-24_2021-12-31.json",
    "openmeteo_previousruns_gfs_global_SFO_2022-01-01_2022-12-31.json",
    "openmeteo_previousruns_gfs_global_SFO_2023-01-01_2023-12-31.json",
    "openmeteo_previousruns_gfs_global_SFO_2024-01-01_2024-07-31.json"]]

STATION = "SFO"
TARGET_HOUR = 20
CUTOFF = date(2024, 8, 1)       # KSFO held-out years start here (D67.6)
LAST_DAY = date(2026, 7, 31)    # no row after this may exist (D67.6)

# SPEC 8.8 G15, written out so it can be checked against the record script
# and the KSFO file.
G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850",
       "dswrf_2h_wm2", "pressure_tendency_3h_hpa"]
RECORD_ORDER = list(rec.FINAL_FEATURE_KEYS)
B_CANONICAL = list(rec.BASE_KEYS)

FOLD_LABELS = ["2022-23", "2023-24"]
FOLDS = {f[0]: f for f in EXPERIMENT_FOLDS if f[0] in FOLD_LABELS}
# Pre-registered pipeline check (session prompt Step 2, from F116.4).
EXPECTED_FOLD_ROWS = {"2022-23": (494, 364), "2023-24": (858, 365)}
EXPECTED_REMOVED = {"features": 730, "obs_paired": 729}

# The looks (D67.3). Counted here from dates only (Step 3).
LOOKS = {"A": ((date(2021, 3, 24), date(2024, 7, 31)),
               (date(2024, 8, 1), date(2025, 7, 31))),
         "B": ((date(2021, 3, 24), date(2025, 7, 31)),
               (date(2025, 8, 1), date(2026, 7, 31)))}
EXPECTED_LOOK_ROWS = {"A": (1223, 364), "B": (1587, 365)}

F115_LARGEST_RANGE = 0.0386  # DSM 2022-23, B+D,L,R,T (F115.4); context only

RUNGS = ["raw_gfs", "persistence", "mean_bias", "B", "B+D,L,R,T"]


# ------------------------------------------------------------------ output

class Tee:
    def __init__(self, path):
        self.f = open(path, "a")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def rel(path):
    return os.path.relpath(path, ROOT)


def refuse_existing(path):
    if os.path.exists(path):
        raise SystemExit("refusing to overwrite existing file: %s" % rel(path))


def write_csv(path, header, rows):
    refuse_existing(path)
    with open(path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def stop(msg):
    raise SystemExit("STOP (bug, session prompt Step 2): " + msg)


# ------------------------------------------------------------------ loading

def finite_float(s):
    """float(s) if it is a finite number, else None (SPEC 8.7 item 2)."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def check_header():
    with open(FEATURES) as fh:
        header = next(csv.reader(fh))
    model_cols = header[6:15]
    print("G15 written in this script == record FINAL_FEATURE_KEYS: %s"
          % (G15 == RECORD_ORDER))
    print("KSFO features file model columns (header positions 7-15) == G15: "
          "%s" % (model_cols == G15))
    if G15 != RECORD_ORDER or model_cols != G15:
        stop("column list is not G15")


def load():
    """Rows before CUTOFF only. Returns (joined rows, paired obs dict,
    counts)."""
    c = {"feature_rows_read": 0, "feature_rows_removed_held_out": 0,
         "feature_rows_not_complete_case": 0, "feature_non_finite_dropped": 0,
         "feature_rows_kept": 0,
         "obs_rows_read": 0, "obs_rows_removed_held_out": 0,
         "obs_paired_rows_removed_held_out": 0, "obs_rows_not_paired": 0,
         "obs_non_finite_dropped": 0, "obs_rows_kept": 0,
         "season_recomputed_differs": 0, "temp_ne_temperature_grib_c": 0}
    feats = {}
    with open(FEATURES) as fh:
        for r in csv.DictReader(fh):
            c["feature_rows_read"] += 1
            if r["station"] != STATION or int(r["target_hour"]) != TARGET_HOUR:
                stop("unexpected station or hour in the features file")
            d = date.fromisoformat(r["target_date"])
            if d >= CUTOFF:
                c["feature_rows_removed_held_out"] += 1
                continue
            if r["complete_case"] != "1":
                c["feature_rows_not_complete_case"] += 1
                continue
            vals = {k: finite_float(r[k]) for k in G15 + ["temperature_grib_c"]}
            if any(v is None for v in vals.values()):
                c["feature_non_finite_dropped"] += 1
                continue
            if vals["temp"] != vals["temperature_grib_c"]:
                c["temp_ne_temperature_grib_c"] += 1
            a = 2 * math.pi * rec.year_fraction(d)
            if (math.sin(a) != vals["season_sin"]
                    or math.cos(a) != vals["season_cos"]):
                c["season_recomputed_differs"] += 1
            feats[d] = {
                "date": d, "fc": vals["temperature_grib_c"],
                "cloud": vals["cloud_cover"], "wind": vals["wind_speed_10m"],
                "lapse_rate_t2_t850": vals["lapse_rate_t2_t850"],
                "dewpoint_depression_t2m_floored":
                    vals["dewpoint_depression_t2m_floored"],
                "pressure_tendency_3h_hpa": vals["pressure_tendency_3h_hpa"],
                "dswrf_2h_wm2": vals["dswrf_2h_wm2"],
            }
            c["feature_rows_kept"] += 1
    obs = {}
    with open(OBS) as fh:
        for r in csv.DictReader(fh):
            c["obs_rows_read"] += 1
            if r["station"] != STATION:
                stop("unexpected station in the observations file")
            d = date.fromisoformat(r["target_date"])
            if d >= CUTOFF:
                c["obs_rows_removed_held_out"] += 1
                if r["pair_status"] == "paired":
                    c["obs_paired_rows_removed_held_out"] += 1
                continue
            if r["pair_status"] != "paired":
                c["obs_rows_not_paired"] += 1
                continue
            v = finite_float(r["obs_c"])
            if v is None:
                c["obs_non_finite_dropped"] += 1
                continue
            obs[d] = v
            c["obs_rows_kept"] += 1
    # The KSFO rehearsal guard.
    assert all(d < CUTOFF for d in feats), "held-out feature row kept"
    assert all(d < CUTOFF for d in obs), "held-out observation row kept"
    joined = []
    for d in sorted(feats):
        if d in obs:
            row = dict(feats[d])
            row["obs"] = obs[d]
            row["resid"] = obs[d] - row["fc"]
            joined.append(row)
    c["joined_rows"] = len(joined)
    assert all(r["date"] < CUTOFF for r in joined)
    return joined, obs, c


def print_load(c):
    print("\nload (rows dated 2024-08-01 or later dropped as read):")
    for k, v in c.items():
        print("  %-38s %d" % (k, v))
    print("KSFO rehearsal guard: no kept feature, observation or joined row "
          "is dated 2024-08-01 or later: passed")
    ok = (c["feature_rows_removed_held_out"] == EXPECTED_REMOVED["features"]
          and c["obs_paired_rows_removed_held_out"]
          == EXPECTED_REMOVED["obs_paired"])
    print("removed counts equal the expected 730 feature rows and 729 paired "
          "observation rows: %s" % ok)
    if not ok:
        stop("held-out removal counts differ from the expected values")
    if c["temp_ne_temperature_grib_c"] or c["season_recomputed_differs"]:
        stop("stored temp or season columns differ from the record's")


def check_folds():
    for label in FOLD_LABELS:
        assert_reserved_year_excluded(*FOLDS[label])
        _, a, b, c_, d = FOLDS[label]
        print("fold %s: train %s..%s, test %s..%s; "
              "assert_reserved_year_excluded: no raise" % (label, a, b, c_, d))


def fold_rows(joined, label):
    _, tr_s, tr_e, te_s, te_e = FOLDS[label]
    assert tr_e < te_s and te_e < CUTOFF
    train = [r for r in joined if tr_s <= r["date"] <= tr_e]
    test = [r for r in joined if te_s <= r["date"] <= te_e]
    exp = EXPECTED_FOLD_ROWS[label]
    print("fold %s rows: train %d (expected %d), test %d (expected %d)" % (
        label, len(train), exp[0], len(test), exp[1]))
    if (len(train), len(test)) != exp:
        stop("fold %s row counts differ from F116.4" % label)
    assert [r["date"] for r in train] == sorted(r["date"] for r in train)
    return train, test


# ------------------------------------------------------------------ fitting

def matrix(rows, keys):
    x = rec.features_matrix(rows, keys)
    if x.dtype != np.float64 or x.shape != (len(rows), len(keys)):
        stop("matrix shape or type is wrong")
    if not np.all(np.isfinite(x)):
        stop("non-finite value in a matrix")
    return x


def fit_predict(train, test, keys):
    """The record's fit (G14) on the G20 target. Returns predicted
    residuals."""
    x_tr = matrix(train, keys)
    y_tr = np.array([r["resid"] for r in train], dtype=float)
    m = rec.lgb.LGBMRegressor(**rec.LGB_PARAMS)
    m.fit(x_tr, y_tr)
    return m.predict(matrix(test, keys))


def score(train, test, obs):
    """All five rungs on one fold. Returns (per-day forecasts, persistence
    day flags, record-order predictions)."""
    if RECORD_ORDER != G15:
        stop("record order is not G15")
    bias = float(np.mean([r["obs"] - r["fc"] for r in train]))
    pred_b = fit_predict(train, test, B_CANONICAL)
    pred_f = fit_predict(train, test, RECORD_ORDER)
    days = []
    for i, r in enumerate(test):
        prev = obs.get(r["date"] - timedelta(days=1))
        days.append({"date": r["date"], "obs": r["obs"],
                     "raw_gfs": r["fc"], "persistence": prev,
                     "mean_bias": r["fc"] + bias,
                     "B": r["fc"] + float(pred_b[i]),
                     "B+D,L,R,T": r["fc"] + float(pred_f[i]),
                     "resid_B": float(pred_b[i]),
                     "resid_BDLRT": float(pred_f[i])})
    return days, bias


def rung_maes(days, basis):
    """basis 'record': persistence on days with a previous-day observation,
    the rest on every test day (D58 item 6). basis 'common': every rung on
    the persistence days."""
    pdays = [d for d in days if d["persistence"] is not None]
    out = {}
    for k in RUNGS:
        use = pdays if (k == "persistence" or basis == "common") else days
        out[k] = (rec.mae([d[k] - d["obs"] for d in use]), len(use))
    return out


# ------------------------------------------------------------------ 2b

def load_om():
    om = {}
    for path in OM_TEMP:
        with open(path) as fh:
            h = json.load(fh)["hourly"]
        for t, v in zip(h["time"], h["temperature_2m_previous_day1"]):
            if t.endswith("T%02d:00" % TARGET_HOUR) and v is not None:
                d = date.fromisoformat(t[:10])
                assert d < CUTOFF
                om[d] = float(v)
    return om


def bias_tables(joined):
    om = load_om()
    out = []
    for kind, keyf, keys in (
            ("month", lambda d: d.month, list(range(1, 13))),
            ("year", lambda d: d.year, sorted({r["date"].year
                                               for r in joined}))):
        print("\n2b bias by %s (descriptive only; obs - raw GFS (GRIB) and "
              "obs - Open-Meteo, deg C):" % kind)
        print("  %-5s %5s %9s %11s %12s %11s %6s" % (
            kind, "n", "mean obs", "mean(o-raw)", "mean|o-raw|",
            "mean(o-OM)", "n_OM"))
        groups = [(k, [r for r in joined if keyf(r["date"]) == k])
                  for k in keys]
        groups.append(("all", joined))
        for k, rows in groups:
            o = np.array([r["obs"] for r in rows])
            e = np.array([r["obs"] - r["fc"] for r in rows])
            eo = np.array([r["obs"] - om[r["date"]] for r in rows
                           if r["date"] in om])
            row = [kind, k, len(rows), float(o.mean()), float(e.mean()),
                   float(np.abs(e).mean()), float(eo.mean()), len(eo)]
            out.append(row)
            print("  %-5s %5d %9.2f %+11.2f %12.2f %+11.2f %6d" % (
                str(k), row[2], row[3], row[4], row[5], row[6], row[7]))
    return out


# ------------------------------------------------------------------ 2c

def load_orderings():
    bd, bo = [], []
    with open(ORDERINGS) as fh:
        for r in csv.DictReader(fh):
            cols = r["columns"].split("|")
            (bd if r["model"] == "B+D,L,R,T" else bo).append(
                (r["ordering"], cols))
    ok = (len(bd) == 102 and len(bo) == 120
          and all(sorted(c) == sorted(G15) and len(c) == 9 for _, c in bd)
          and all(sorted(c) == sorted(B_CANONICAL) and len(c) == 5
                  for _, c in bo)
          and len({tuple(c) for _, c in bd}) == 102
          and len({tuple(c) for _, c in bo}) == 120
          and bd[0] == ("record", G15) and bo[0] == ("canonical", B_CANONICAL))
    print("orderings: B+D,L,R,T %d, B %d; every ordering is a permutation of "
          "the G15 (or B) column names, all distinct, anchors first: %s"
          % (len(bd), len(bo), ok))
    if not ok:
        raise SystemExit("STOP (Step 0.5 stop rule): the orderings cannot be "
                         "mapped to KSFO's columns by name without ambiguity")
    return bd, bo


def spread(joined, anchors):
    bd, bo = load_orderings()
    maes = {}
    rows = []
    for label in FOLD_LABELS:
        train, test = fold_rows(joined, label)
        for model, orders in (("B+D,L,R,T", bd), ("B", bo)):
            for name, keys in orders:
                pred = fit_predict(train, test, keys)
                m = rec.mae([(r["fc"] + float(pred[i])) - r["obs"]
                             for i, r in enumerate(test)])
                maes.setdefault((label, model), {})[name] = m
                rows.append([label, model, name, len(train), len(test),
                             repr(m)])
    for label in FOLD_LABELS:
        if (maes[(label, "B+D,L,R,T")]["record"] != anchors[(label, "B+D,L,R,T")]
                or maes[(label, "B")]["canonical"] != anchors[(label, "B")]):
            stop("spread anchor fit differs from the 2a fit")
    print("the spread's anchor fits equal the 2a fits exactly (4 of 4)")
    return maes, rows


def spread_report(maes):
    summary = []
    print("\n2c column-order spread. MAE in deg C. '%' columns are relative "
          "to that model's record-order MAE (B: canonical order).")
    for model, ref in (("B", "canonical"), ("B+D,L,R,T", "record")):
        print("\n%s (%d orderings)" % (model, 120 if model == "B" else 102))
        print("  %-7s %8s %8s %8s %8s %8s %8s %8s %8s %8s" % (
            "fold", "rec", "min", "max", "range", "sd", "min%", "max%",
            "range%", "sd%"))
        for label in FOLD_LABELS:
            v = maes[(label, model)]
            a = np.array(list(v.values()))
            r0 = v[ref]
            lo, hi, sd = float(a.min()), float(a.max()), float(a.std())
            print("  %-7s %8.4f %8.4f %8.4f %8.4f %8.4f %+7.2f%% %+7.2f%% "
                  "%7.2f%% %7.2f%%" % (
                      label, r0, lo, hi, hi - lo, sd, 100 * (lo - r0) / r0,
                      100 * (hi - r0) / r0, 100 * (hi - lo) / r0,
                      100 * sd / r0))
            summary.append([label, model, len(a), repr(r0), repr(lo),
                            repr(hi), repr(hi - lo), repr(sd)])
    print("\nwin share (strict 'lower') and record-order margin = canonical B "
          "MAE minus record-order B+D,L,R,T MAE:")
    print("  %-7s %13s %9s %10s %8s" % ("fold", "wins", "share", "margin",
                                        "margin%"))
    wins_out = []
    for label in FOLD_LABELS:
        bd = np.array(list(maes[(label, "B+D,L,R,T")].values()))
        b = np.array(list(maes[(label, "B")].values()))
        wins = int((bd[:, None] < b[None, :]).sum())
        pairs = bd.size * b.size
        b0 = maes[(label, "B")]["canonical"]
        f0 = maes[(label, "B+D,L,R,T")]["record"]
        print("  %-7s %6d/%6d %8.2f%% %10.4f %+7.2f%%" % (
            label, wins, pairs, 100 * wins / pairs, b0 - f0,
            100 * (b0 - f0) / b0))
        wins_out.append([label, wins, pairs, repr(wins / pairs),
                         repr(b0 - f0), repr(100 * (b0 - f0) / b0)])
    ranges = {(s[0], s[1]): float(s[6]) for s in summary}
    (bl, bm), band = max(ranges.items(), key=lambda kv: kv[1])
    print("\nBAND = the largest range among {B, B+D,L,R,T} x {2022-23, "
          "2023-24} (D67.5):")
    for (label, model), v in sorted(ranges.items()):
        print("  %-9s %s  range %r" % (model, label, v))
    print("  band = %r deg C (%.4f at 4 dp), from %s, %s" % (band, band, bm,
                                                              bl))
    print("  context only: F115's largest range, 0.0386 deg C (DSM 2022-23, "
          "B+D,L,R,T)")
    return summary, wins_out, {"band_c": band, "band_c_4dp": "%.4f" % band,
                               "set": {"model": bm, "fold": bl},
                               "ranges": {"%s %s" % k: v
                                          for k, v in ranges.items()},
                               "f115_largest_range_context": F115_LARGEST_RANGE}


# ------------------------------------------------------------------ modes

def header(mode):
    print("\n" + "=" * 78)
    print("session 77 rehearsal %s  python %s  numpy %s  lightgbm %s" % (
        mode, platform.python_version(), np.__version__,
        lightgbm.__version__))
    print("=" * 78)


def rehearse():
    os.makedirs(OUT_DIR, exist_ok=False)
    check_header()
    check_folds()
    joined, obs, counts = load()
    print_load(counts)
    print("\n2a rungs (rehearsal, not a gate). MAE in deg C (G24).")
    rung_rows, common_rows, pred_rows, anchors = [], [], [], {}
    for label in FOLD_LABELS:
        train, test = fold_rows(joined, label)
        days, bias = score(train, test, obs)
        rec_m = rung_maes(days, "record")
        com_m = rung_maes(days, "common")
        anchors[(label, "B")] = rec_m["B"][0]
        anchors[(label, "B+D,L,R,T")] = rec_m["B+D,L,R,T"][0]
        n_p = rec_m["persistence"][1]
        print("\nfold %s: train %d, test %d, persistence days %d, "
              "training mean bias (obs - raw GFS) %r" % (
                  label, len(train), len(test), n_p, bias))
        print("  %-10s %6s %22s %8s   %s" % ("rung", "n", "MAE", "4 dp",
                                            "common days (descriptive)"))
        for k in RUNGS:
            m, n = rec_m[k]
            cm, cn = com_m[k]
            print("  %-10s %6d %22r %8.4f   n=%d %.4f" % (k, n, m, m, cn, cm))
            rung_rows.append([label, k, "D58 item 6", n, repr(m)])
            common_rows.append([label, k, "common days (descriptive)", cn,
                                repr(cm)])
        f = rec_m["B+D,L,R,T"][0]
        print("  rehearsal, not a gate: B+D,L,R,T beats raw GFS: %s; beats "
              "persistence: %s" % (f < rec_m["raw_gfs"][0],
                                   f < rec_m["persistence"][0]))
        for d in days:
            pred_rows.append([label, d["date"].isoformat(), repr(d["obs"]),
                              repr(d["raw_gfs"]), repr(d["persistence"])
                              if d["persistence"] is not None else "",
                              repr(d["mean_bias"]), repr(d["resid_B"]),
                              repr(d["resid_BDLRT"])])
    write_csv(os.path.join(OUT_DIR, "rungs.csv"),
              ["fold", "rung", "day_basis", "n_days", "mae"],
              rung_rows + common_rows)
    write_csv(os.path.join(OUT_DIR, "predictions.csv"),
              ["fold", "target_date", "obs_c", "raw_gfs_c", "persistence_c",
               "mean_bias_c", "resid_B_canonical", "resid_BDLRT_record"],
              pred_rows)
    bias = bias_tables(joined)
    write_csv(os.path.join(OUT_DIR, "bias.csv"),
              ["group", "key", "n", "mean_obs", "mean_obs_minus_raw",
               "mean_abs_obs_minus_raw", "mean_obs_minus_om", "n_om"], bias)
    maes, spread_rows = spread(joined, anchors)
    write_csv(os.path.join(OUT_DIR, "spread_mae.csv"),
              ["fold", "model", "ordering", "n_train", "n_test", "mae"],
              spread_rows)
    summary, wins, band = spread_report(maes)
    write_csv(os.path.join(OUT_DIR, "spread_summary.csv"),
              ["fold", "model", "n_orderings", "record_order_mae", "min",
               "max", "range", "sd"], summary)
    write_csv(os.path.join(OUT_DIR, "win_share.csv"),
              ["fold", "wins", "pairs", "win_share", "margin_c",
               "margin_pct"], wins)
    path = os.path.join(OUT_DIR, "band.json")
    refuse_existing(path)
    with open(path, "w") as fh:
        json.dump(band, fh, indent=1)
    meta = {"session": 77, "purpose": "KSFO rehearsal, not a gate (D67.4)",
            "versions": {"python": platform.python_version(),
                         "numpy": np.__version__,
                         "lightgbm": lightgbm.__version__},
            "lgb_params": rec.LGB_PARAMS, "cutoff": str(CUTOFF),
            "folds": {k: [str(x) for x in v[1:]] for k, v in FOLDS.items()},
            "load_counts": counts,
            "fits": 4 + 2 * (102 + 120)}
    path = os.path.join(OUT_DIR, "metadata.json")
    refuse_existing(path)
    with open(path, "w") as fh:
        json.dump(meta, fh, indent=1)
    print("\nfits run: %d. wrote data/rebuild/session77/ (rungs.csv, "
          "predictions.csv, bias.csv, spread_mae.csv, spread_summary.csv, "
          "win_share.csv, band.json, metadata.json)" % meta["fits"])


def repeat():
    os.makedirs(RUN2_DIR, exist_ok=False)
    joined, obs, counts = load()
    print_load(counts)
    rows = []
    for label in FOLD_LABELS:
        train, test = fold_rows(joined, label)
        pred = fit_predict(train, test, RECORD_ORDER)
        rows += [[label, r["date"].isoformat(), repr(float(p))]
                 for r, p in zip(test, pred)]
    write_csv(os.path.join(RUN2_DIR, "predictions.csv"),
              ["fold", "target_date", "resid_BDLRT_record"], rows)
    with open(os.path.join(OUT_DIR, "predictions.csv")) as fh:
        run1 = {(r["fold"], r["target_date"]): float(r["resid_BDLRT_record"])
                for r in csv.DictReader(fh)}
    print("\ndeterminism: record-order B+D,L,R,T, run 1 against run 2 "
          "(separate process):")
    for label in FOLD_LABELS:
        mine = [(k, float(v)) for f, k, v in rows if f == label]
        equal = sum(1 for k, v in mine if run1[(label, k)] == v)
        diff = max(abs(run1[(label, k)] - v) for k, v in mine)
        print("  %s  %d of %d predictions equal, max abs diff %r" % (
            label, equal, len(mine), diff))
        if equal != len(mine):
            stop("record-order predictions differ between processes")


def counts():
    """Step 3: dates, station, complete-case flag and pairing status only.
    No value is parsed."""
    feat, paired, last = set(), set(), date.min
    with open(FEATURES) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            last = max(last, d)
            if r["station"] == STATION and r["complete_case"] == "1":
                feat.add(d)
    with open(OBS) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            last = max(last, d)
            if r["station"] == STATION and r["pair_status"] == "paired":
                paired.add(d)
    print("\nStep 3: look counts from dates and row presence only (no value "
          "read). Largest date in either file: %s" % last)
    both = feat & paired
    rows = []
    for look, ((tr_s, tr_e), (te_s, te_e)) in LOOKS.items():
        train = [d for d in both if tr_s <= d <= tr_e]
        test = [d for d in both if te_s <= d <= te_e]
        pers = [d for d in test if d - timedelta(days=1) in paired]
        exp = EXPECTED_LOOK_ROWS[look]
        print("  look %s: train %s..%s %d (expected %d); test %s..%s %d "
              "(expected %d); persistence test days %d" % (
                  look, tr_s, tr_e, len(train), exp[0], te_s, te_e,
                  len(test), exp[1], len(pers)))
        rows.append([look, str(tr_s), str(tr_e), str(te_s), str(te_e),
                     len(train), len(test), len(pers)])
        if (len(train), len(test)) != exp:
            raise SystemExit("STOP (session prompt Step 3): look %s count "
                             "differs from the expected value" % look)
    write_csv(os.path.join(OUT_DIR, "look_counts.csv"),
              ["look", "train_start", "train_end", "test_start", "test_end",
               "train_rows", "test_rows", "persistence_test_days"], rows)
    print("wrote data/rebuild/session77/look_counts.csv")


def main():
    modes = {"--rehearse": rehearse, "--repeat": repeat, "--counts": counts}
    if len(sys.argv) != 2 or sys.argv[1] not in modes:
        raise SystemExit("usage: session77_ksfo_rehearsal.py "
                         "--rehearse | --repeat | --counts")
    sys.stdout = Tee(LOG_PATH)
    header(sys.argv[1])
    modes[sys.argv[1]]()
    sys.stdout.flush()
    sys.stdout = sys.__stdout__


if __name__ == "__main__":
    main()
