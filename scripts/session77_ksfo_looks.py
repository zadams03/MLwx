"""Session 77: the frozen script for KSFO's two looks (D67.3, D70).

THIS FILE IS FROZEN BY D70. Session 78 checks its SHA-256, then runs it
once, unchanged, with --run-looks. Session 77 ran only --dry-run.

What it does. The recipe is SPEC 8, applied unchanged (D69.1), exactly as
session 77's rehearsal ran it (scripts/session77_ksfo_rehearsal.py):
- the nine SPEC 8.8 G15 columns, in order;
- LGB_PARAMS, features_matrix (which rebuilds season_sin and season_cos
  from the date) and mae (G24), imported read-only from the record script,
  scripts/session62_reserved_confirm.py;
- the G14 call, LGBMRegressor(**LGB_PARAMS).fit(x, y), on a float64 array
  with no column names, with every other parameter at the lightgbm 4.7.0
  default (G17); rows in ascending date order (G19);
- the G20 target, obs - temperature_grib_c, unrounded;
- prediction = temperature_grib_c + the predicted residual.

The rungs, per look: raw GFS (GRIB) = temperature_grib_c, which already
carries KSFO's +0.6944 degC constant (F116.2); persistence = the previous
day's paired observation; the mean-bias reference = raw GFS + mean(obs -
raw GFS) over that look's training rows; B (canonical order); B+D,L,R,T
(record order). Day basis as D58 item 6: persistence on test days that
have a previous-day observation, every other rung on every test day. Every
rung is also re-scored on that common day set, as a description only.

The bar (SPEC 5.3), per look: B+D,L,R,T has a strictly lower MAE than raw
GFS (GRIB) and than persistence. Overall (D67.3): pass if both looks pass,
split if one does, fail if neither does. The band read (D67.5) is a
secondary read, not part of the bar: margin = canonical B MAE minus
record-order B+D,L,R,T MAE; above +BAND_C "beats B by more than the
column-order spread", below -BAND_C "B beats B+D,L,R,T by more than the
spread", otherwise "within the column-order spread".

Checks, in this order, before any fit:
1. the SHA-256 of both KSFO data files and of the record script, against
   the values below (this runs before the record script is imported);
2. the station is SFO in every row of both files, and the nine model
   columns equal G15 in the features file and in the record script;
3. the KSFO held-out guard, per look: training max date < test min date;
   look A's training ends 2024-07-31 and look B's 2025-07-31; the windows
   are exactly D67.3's; no row in either file is dated 2026-08-01 or later;
   and the training, test and persistence counts equal session 77's Step 3
   values, below (SPEC 8.7 item 4).
Any failure stops the script.

Modes:
  --dry-run (the default). Checks 1-3, using dates, the station, the
      complete-case flag and the pairing status only: no value in a row
      dated 2024-08-01 or later is parsed. Then a self-test: the same
      fit-and-score code on the `2023-24` rehearsal fold (D51), using only
      rows dated before 2024-08-01, must reproduce session 77's Step 2a
      MAEs exactly. It writes nothing.
  --run-looks. Refuses to start if either output file exists (SPEC 8.7
      item 5). Checks 1-3, with every value parsed and non-finite values
      rejected (SPEC 8.7 item 2), then fits and scores both looks and
      writes the two output files below. Output is printed only.

It does not call, edit or disable the session-48 reserved-year guard,
which protects the five earlier airports; KSFO uses its own guard (above).
The record script imports scripts/session48_reserved_year.py for its own
definitions, so that module is loaded; nothing here refers to it.
"""

import hashlib
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

FEATURES = os.path.join(ROOT, "data", "processed", "session76_ksfo_features.csv")
OBS = os.path.join(ROOT, "data", "processed",
                   "session76_ksfo_observations.csv")
RECORD_SCRIPT = os.path.join(HERE, "session62_reserved_confirm.py")

EXPECTED_SHA256 = {
    FEATURES:
        "f228301edd2c155bf1062dfb57f5e83ef0ce17050151bcdcf5e9983b2bc3e5c9",
    OBS:
        "b987dd4fad6d1baabefd5a15e31df8260e696b4193f4296d31eebb99c027736c",
    RECORD_SCRIPT:
        "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def check_hashes():
    got = {p: sha256(p) for p in EXPECTED_SHA256}
    bad = [p for p in got if got[p] != EXPECTED_SHA256[p]]
    if bad:
        raise SystemExit("STOP: SHA-256 mismatch: " + "; ".join(
            "%s is %s, expected %s" % (os.path.relpath(p, ROOT), got[p],
                                       EXPECTED_SHA256[p]) for p in bad))
    return got


# Check 1 runs before anything else, including the record script's import.
_HASHES = check_hashes()

sys.path.insert(0, HERE)
# Importing the record script runs its libomp loader shim (D24), which may
# restart this process; check 1 then runs again.
import session62_reserved_confirm as rec  # noqa: E402

import csv  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
from datetime import date, timedelta  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm  # noqa: E402

GRID_OUT = os.path.join(ROOT, "data", "processed",
                        "session78_ksfo_looks_grid.csv")
PRED_OUT = os.path.join(ROOT, "data", "processed",
                        "session78_ksfo_looks_predictions.csv")

STATION = "SFO"
TARGET_HOUR = 20
HELD_OUT_START = date(2024, 8, 1)   # D67.6
LAST_DAY = date(2026, 7, 31)        # no row after this may exist (D67.6)

G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850",
       "dswrf_2h_wm2", "pressure_tendency_3h_hpa"]
B_KEYS = G15[:5]

# D67.3. (train_start, train_end, test_start, test_end)
LOOKS = {
    "A": (date(2021, 3, 24), date(2024, 7, 31),
          date(2024, 8, 1), date(2025, 7, 31)),
    "B": (date(2021, 3, 24), date(2025, 7, 31),
          date(2025, 8, 1), date(2026, 7, 31)),
}
# Session 77 Step 3 (dates and row presence only): train, test, persistence
# test days.
EXPECTED_COUNTS = {"A": (1223, 364, 363), "B": (1587, 365, 365)}

# D67.5 band, frozen by D70.5: the largest MAE range across column
# orderings among {B, B+D,L,R,T} x {2022-23, 2023-24} (session 77 Step 2c;
# it came from B+D,L,R,T on 2022-23).
BAND_C = 0.037704595173481126

# Self-test: D51's `2023-24` fold and session 77's Step 2a MAEs on it.
SELFTEST_FOLD = (date(2021, 3, 24), date(2023, 7, 31),
                 date(2023, 8, 1), date(2024, 7, 31))
SELFTEST_COUNTS = (858, 365, 364)
SELFTEST_MAE = {
    "raw_gfs": 1.3061369863013699,
    "persistence": 1.715659340659341,
    "mean_bias": 1.250037292844142,
    "B": 1.2922832710768244,
    "B+D,L,R,T": 1.174587228071113,
}

RUNGS = ["raw_gfs", "persistence", "mean_bias", "B", "B+D,L,R,T"]


def stop(msg):
    raise SystemExit("STOP: " + msg)


def finite_float(s):
    """float(s) if it is a finite number, else None (SPEC 8.7 item 2)."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


# ------------------------------------------------------------------ loading

def check_columns():
    with open(FEATURES) as fh:
        header = next(csv.reader(fh))
    ok = (header[6:15] == G15 and list(rec.FINAL_FEATURE_KEYS) == G15
          and list(rec.BASE_KEYS) == B_KEYS)
    print("model columns in the features file and the record script equal "
          "G15: %s" % ok)
    if not ok:
        stop("the model columns are not G15")


def load(parse_held_out):
    """Reads both KSFO files. A row counts as present when the features
    row is complete-case (flag) and, in --run-looks, every value is finite;
    and when the observation is paired (status) and, in --run-looks, finite.
    When parse_held_out is False, no value in a row dated on or after
    HELD_OUT_START is parsed."""
    data = {"feat": {}, "obs": {}, "feat_present": set(),
            "obs_present": set(), "all_dates": set(), "stations": set(),
            "hours": set(), "feature_non_finite": 0, "obs_non_finite": 0}
    with open(FEATURES) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            data["all_dates"].add(d)
            data["stations"].add(r["station"])
            data["hours"].add(r["target_hour"])
            if r["complete_case"] != "1":
                continue
            if d >= HELD_OUT_START and not parse_held_out:
                data["feat_present"].add(d)
                continue
            vals = {k: finite_float(r[k])
                    for k in G15 + ["temperature_grib_c"]}
            if any(v is None for v in vals.values()):
                data["feature_non_finite"] += 1
                continue
            if vals["temp"] != vals["temperature_grib_c"]:
                stop("temp differs from temperature_grib_c on %s" % d)
            data["feat"][d] = {
                "date": d, "fc": vals["temperature_grib_c"],
                "cloud": vals["cloud_cover"], "wind": vals["wind_speed_10m"],
                "lapse_rate_t2_t850": vals["lapse_rate_t2_t850"],
                "dewpoint_depression_t2m_floored":
                    vals["dewpoint_depression_t2m_floored"],
                "pressure_tendency_3h_hpa": vals["pressure_tendency_3h_hpa"],
                "dswrf_2h_wm2": vals["dswrf_2h_wm2"],
            }
            data["feat_present"].add(d)
    with open(OBS) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            data["all_dates"].add(d)
            data["stations"].add(r["station"])
            data["hours"].add(r["target_hour"])
            if r["pair_status"] != "paired":
                continue
            if d >= HELD_OUT_START and not parse_held_out:
                data["obs_present"].add(d)
                continue
            v = finite_float(r["obs_c"])
            if v is None:
                data["obs_non_finite"] += 1
                continue
            data["obs"][d] = v
            data["obs_present"].add(d)
    print("station(s) in both files: %s; target hour(s): %s" % (
        sorted(data["stations"]), sorted(data["hours"])))
    if data["stations"] != {STATION} or data["hours"] != {str(TARGET_HOUR)}:
        stop("a row is not station SFO at 20 UTC")
    print("non-finite values dropped: features %d, observations %d" % (
        data["feature_non_finite"], data["obs_non_finite"]))
    return data


def windows(data, fold):
    tr_s, tr_e, te_s, te_e = fold
    both = data["feat_present"] & data["obs_present"]
    train = sorted(d for d in both if tr_s <= d <= tr_e)
    test = sorted(d for d in both if te_s <= d <= te_e)
    pers = [d for d in test if d - timedelta(days=1) in data["obs_present"]]
    return train, test, pers


# ------------------------------------------------------------------ the guard

def held_out_guard(data):
    """The KSFO held-out guard (session prompt Step 4 item 4)."""
    print("\nKSFO held-out guard:")
    last = max(data["all_dates"])
    print("  largest date in either file: %s (must be <= %s)" % (last,
                                                                LAST_DAY))
    if last > LAST_DAY:
        stop("a row is dated 2026-08-01 or later")
    if LOOKS != {"A": (date(2021, 3, 24), date(2024, 7, 31),
                       date(2024, 8, 1), date(2025, 7, 31)),
                 "B": (date(2021, 3, 24), date(2025, 7, 31),
                       date(2025, 8, 1), date(2026, 7, 31))}:
        stop("the look windows are not D67.3's")
    if LOOKS["A"][1] != date(2024, 7, 31) or LOOKS["B"][1] != date(2025, 7, 31):
        stop("a look's training does not end where D67.3 says")
    out = {}
    for look, fold in LOOKS.items():
        train, test, pers = windows(data, fold)
        got = (len(train), len(test), len(pers))
        print("  look %s: train %s..%s, test %s..%s; rows train %d, test %d, "
              "persistence days %d (expected %d, %d, %d)" % (
                  look, *fold, *got, *EXPECTED_COUNTS[look]))
        if not (train and test and train[-1] < test[0]):
            stop("look %s: training max date is not before test min date"
                 % look)
        if not (fold[0] <= train[0] and train[-1] <= fold[1]
                and fold[2] <= test[0] and test[-1] <= fold[3]):
            stop("look %s: a row falls outside its window" % look)
        if got != EXPECTED_COUNTS[look]:
            stop("look %s: counts differ from session 77 Step 3" % look)
        out[look] = (train, test)
    print("  passed")
    return out


# ------------------------------------------------------------------ fit/score

def matrix(rows, keys):
    x = rec.features_matrix(rows, keys)
    if x.dtype != np.float64 or x.shape != (len(rows), len(keys)):
        stop("matrix shape or type is wrong")
    if not np.all(np.isfinite(x)):
        stop("non-finite value in a matrix")
    return x


def fit_predict(train, test, keys):
    x_tr = matrix(train, keys)
    y_tr = np.array([r["resid"] for r in train], dtype=float)
    m = rec.lgb.LGBMRegressor(**rec.LGB_PARAMS)
    m.fit(x_tr, y_tr)
    return m.predict(matrix(test, keys))


def rows_for(data, dates):
    out = []
    for d in dates:
        r = dict(data["feat"][d])
        r["obs"] = data["obs"][d]
        r["resid"] = r["obs"] - r["fc"]
        out.append(r)
    return out


def score(data, train_dates, test_dates):
    train = rows_for(data, train_dates)
    test = rows_for(data, test_dates)
    bias = float(np.mean([r["obs"] - r["fc"] for r in train]))
    pred_b = fit_predict(train, test, B_KEYS)
    pred_f = fit_predict(train, test, G15)
    days = []
    for i, r in enumerate(test):
        days.append({"date": r["date"], "obs": r["obs"], "raw_gfs": r["fc"],
                     "persistence": data["obs"].get(
                         r["date"] - timedelta(days=1)),
                     "mean_bias": r["fc"] + bias,
                     "B": r["fc"] + float(pred_b[i]),
                     "B+D,L,R,T": r["fc"] + float(pred_f[i])})
    pdays = [d for d in days if d["persistence"] is not None]
    res = {"n_train": len(train), "n_test": len(test), "n_pers": len(pdays),
           "bias": bias, "days": days, "mae": {}, "common": {}}
    for k in RUNGS:
        use = pdays if k == "persistence" else days
        res["mae"][k] = (rec.mae([d[k] - d["obs"] for d in use]), len(use))
        res["common"][k] = (rec.mae([d[k] - d["obs"] for d in pdays]),
                            len(pdays))
    f = res["mae"]["B+D,L,R,T"][0]
    res["beats_raw"] = f < res["mae"]["raw_gfs"][0]
    res["beats_persistence"] = f < res["mae"]["persistence"][0]
    res["passes"] = res["beats_raw"] and res["beats_persistence"]
    margin = res["mae"]["B"][0] - f
    if margin > BAND_C:
        read = "beats B by more than the column-order spread"
    elif margin < -BAND_C:
        read = "B beats B+D,L,R,T by more than the spread"
    else:
        read = "within the column-order spread"
    res["margin"], res["band_read"] = margin, read
    return res


def report(label, res):
    print("\n%s: train %d, test %d, persistence days %d, training mean bias "
          "(obs - raw GFS) %r" % (label, res["n_train"], res["n_test"],
                                  res["n_pers"], res["bias"]))
    print("  %-10s %5s %22s %8s   %s" % ("rung", "n", "MAE", "4 dp",
                                        "common days (descriptive)"))
    for k in RUNGS:
        m, n = res["mae"][k]
        cm, cn = res["common"][k]
        print("  %-10s %5d %22r %8.4f   n=%d %.4f" % (k, n, m, m, cn, cm))
    print("  bar (SPEC 5.3): B+D,L,R,T beats raw GFS (GRIB): %s; beats "
          "persistence: %s -> %s" % (res["beats_raw"],
                                     res["beats_persistence"],
                                     "PASS" if res["passes"] else "FAIL"))
    print("  band read (D67.5, secondary, not part of the bar): margin "
          "%r (%.4f) against band %.4f -> %s" % (
              res["margin"], res["margin"], BAND_C, res["band_read"]))


def grid_rows(look, res):
    rows = []
    for k in RUNGS:
        m, n = res["mae"][k]
        basis = "persistence_days" if k == "persistence" else "all_test_days"
        rows.append([look, "rung", k, basis, n, repr(m)])
    for k in RUNGS:
        m, n = res["common"][k]
        rows.append([look, "rung_common_days_descriptive", k,
                     "persistence_days", n, repr(m)])
    rows += [[look, "bar", "beats_raw_gfs", "", "", int(res["beats_raw"])],
             [look, "bar", "beats_persistence", "", "",
              int(res["beats_persistence"])],
             [look, "bar", "look_passes", "", "", int(res["passes"])],
             [look, "band", "margin_c", "all_test_days", res["n_test"],
              repr(res["margin"])],
             [look, "band", "band_c", "", "", repr(BAND_C)],
             [look, "band", "band_read", "", "", res["band_read"]],
             [look, "info", "training_mean_bias_c", "", res["n_train"],
              repr(res["bias"])]]
    return rows


def pred_rows(look, res):
    return [[look, d["date"].isoformat(), repr(d["obs"]), repr(d["raw_gfs"]),
             "" if d["persistence"] is None else repr(d["persistence"]),
             repr(d["mean_bias"]), repr(d["B"]), repr(d["B+D,L,R,T"])]
            for d in res["days"]]


GRID_HEADER = ["look", "row_type", "name", "day_basis", "n", "value"]
PRED_HEADER = ["look", "target_date", "obs_c", "raw_gfs_c", "persistence_c",
               "mean_bias_c", "B_c", "BDLRT_c"]


# ------------------------------------------------------------------ modes

def dry_run():
    check_columns()
    data = load(parse_held_out=False)
    held_out_guard(data)
    if any(d >= HELD_OUT_START for d in data["feat"]) or any(
            d >= HELD_OUT_START for d in data["obs"]):
        stop("a held-out value was parsed in --dry-run")
    print("\nno value in a row dated 2024-08-01 or later was parsed")
    train, test, pers = windows(data, SELFTEST_FOLD)
    print("\nself-test on the 2023-24 rehearsal fold (%s..%s train, %s..%s "
          "test): rows %d, %d, persistence days %d (expected %d, %d, %d)"
          % (*SELFTEST_FOLD, len(train), len(test), len(pers),
             *SELFTEST_COUNTS))
    if (len(train), len(test), len(pers)) != SELFTEST_COUNTS:
        stop("self-test counts differ")
    res = score(data, train, test)
    report("self-test, 2023-24 fold (rehearsal data, not a look, not a gate)",
           res)
    ok = True
    for k in RUNGS:
        same = res["mae"][k][0] == SELFTEST_MAE[k]
        ok &= same
        print("  self-test %-10s %r vs Step 2a %r: %s" % (
            k, res["mae"][k][0], SELFTEST_MAE[k],
            "equal" if same else "DIFFERENT"))
    n_grid, n_pred = len(grid_rows("self-test", res)), len(
        pred_rows("self-test", res))
    print("  output rows built for the self-test (not written): grid %d, "
          "predictions %d" % (n_grid, n_pred))
    if not ok:
        stop("self-test does not reproduce Step 2a exactly")
    print("\nDRY RUN PASSED. Nothing was written. --run-looks was not run.")


def run_looks():
    for p in (GRID_OUT, PRED_OUT):
        if os.path.exists(p):
            stop("refusing to start: %s exists" % os.path.relpath(p, ROOT))
    check_columns()
    data = load(parse_held_out=True)
    looks = held_out_guard(data)
    results = {}
    for look, (train, test) in looks.items():
        results[look] = score(data, train, test)
        report("look %s (%s..%s train, %s..%s test)" % (look, *LOOKS[look]),
               results[look])
    n_pass = sum(r["passes"] for r in results.values())
    overall = {2: "pass", 1: "split", 0: "fail"}[n_pass]
    print("\noverall (D67.3): %s (%d of 2 looks pass)" % (overall.upper(),
                                                        n_pass))
    grid = sum((grid_rows(k, r) for k, r in results.items()), [])
    grid.append(["both", "overall", "reading", "", n_pass, overall])
    preds = sum((pred_rows(k, r) for k, r in results.items()), [])
    for path, header, rows in ((GRID_OUT, GRID_HEADER, grid),
                               (PRED_OUT, PRED_HEADER, preds)):
        if os.path.exists(path):
            stop("refusing to overwrite %s" % os.path.relpath(path, ROOT))
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        print("wrote %s (%d rows)" % (os.path.relpath(path, ROOT), len(rows)))


def main():
    args = sys.argv[1:]
    if args not in ([], ["--dry-run"], ["--run-looks"]):
        raise SystemExit("usage: session77_ksfo_looks.py [--dry-run | "
                         "--run-looks]")
    mode = "--run-looks" if args == ["--run-looks"] else "--dry-run"
    print("=" * 78)
    print("session77_ksfo_looks.py %s  python %s  numpy %s  lightgbm %s" % (
        mode, platform.python_version(), np.__version__,
        lightgbm.__version__))
    print("=" * 78)
    print("SHA-256 check (before the record script was imported): passed")
    for p, h in _HASHES.items():
        print("  %s  %s" % (h, os.path.relpath(p, ROOT)))
    if mode == "--run-looks":
        run_looks()
    else:
        dry_run()


if __name__ == "__main__":
    main()
