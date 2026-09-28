"""Session 81: build the training set, pass the reproduction gate, and train
and freeze the 2026-27 forward test's models (DECISIONS D73).

Modes (run in this order, each once):
  --build   Assembles every row dated 2021-03-24..2026-07-31 at the six
            airports from committed files only, and writes
            data/processed/session81_training_set.csv. Refuses to start if
            that file exists (SPEC 8.7 item 5).
  --gate    Reads the training set and fits and predicts on two recorded
            folds (F109's, and KSFO look B's), with the same code as
            --freeze and only the dates changed. Compares the B and
            B+D,L,R,T MAEs with the recorded values at full precision. It
            re-computes recorded figures for verification only and gives no
            verdict. It writes nothing.
  --freeze  Reads the training set and, per airport, fits the B+D,L,R,T
            model and the plain B model on all rows once, and computes the
            mean-bias constant. Saves both models (LightGBM text format) and
            manifest.json under data/models/session81/. Refuses to start if
            that folder exists. Reload check: each saved model's predictions
            on its own training rows must equal the in-memory model's
            exactly. No error or MAE is computed on the training rows.

Where the logic comes from (copied, not changed):
- the five earlier airports' loading and joining: the record script
  scripts/session62_reserved_confirm.py (load_family, load_base_unfiltered,
  load_obs_all, build_complete_case, join_obs). The observation pairing is
  the record's historical one (SPEC 4.5's note, D73.2). The one addition is
  SPEC 8.7 item 2: a blank or non-finite value is rejected at load and
  counted, never passed on.
- KSFO's loading and joining: scripts/session77_ksfo_looks.py (load,
  windows, rows_for). The two KSFO files' SHA-256 are checked against D70.2.
- the model: LGB_PARAMS, BASE_KEYS, FINAL_FEATURE_KEYS and year_fraction,
  imported read-only from the record script, whose SHA-256 is checked
  first (D70.2). G14, G15, G17, G19 and G20 (SPEC 8.8).

Guard (D73, session 81 scope): any row dated 2026-08-01 or later, in any
input or in the training set, stops the script with an error. It is a
guard, not a filter: nothing is silently dropped.

It does not call, edit or disable the session-48 reserved-year guard. The
record script imports that module for its own definitions; nothing here
refers to it.
"""

import hashlib
import os
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

RECORD_SCRIPT = os.path.join(HERE, "session62_reserved_confirm.py")
RECORD_SCRIPT_SHA256 = \
    "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256(RECORD_SCRIPT) != RECORD_SCRIPT_SHA256:
    raise SystemExit("STOP: the record script's SHA-256 is not D70.2's")

sys.path.insert(0, HERE)
# Importing the record script runs its libomp loader shim (D24), which may
# restart this process; the check above then runs again.
import session62_reserved_confirm as rec  # noqa: E402

import csv  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import platform  # noqa: E402
from datetime import date, datetime, timedelta  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
RAW = os.path.join(ROOT, "data", "raw")
TRAINING_SET = os.path.join(PROCESSED, "session81_training_set.csv")
MODEL_DIR = os.path.join(ROOT, "data", "models", "session81")

FIRST_DAY = date(2021, 3, 24)
LAST_DAY = date(2026, 7, 31)
FORBIDDEN_FROM = date(2026, 8, 1)

# SPEC 3.4: station code -> target hour (UTC). SFO is KSFO's IEM code.
STATIONS = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20,
            "SFO": 20}
RECORD_STATIONS = ["EGLC", "LFPG", "DSM", "YSDU", "RNO"]

G15 = ["temp", "season_sin", "season_cos", "cloud_cover", "wind_speed_10m",
       "dewpoint_depression_t2m_floored", "lapse_rate_t2_t850",
       "dswrf_2h_wm2", "pressure_tendency_3h_hpa"]
B_KEYS = G15[:5]
if list(rec.FINAL_FEATURE_KEYS) != G15 or list(rec.BASE_KEYS) != B_KEYS:
    raise SystemExit("STOP: the record script's columns are not G15")

# The committed files the record used (SPEC 8.1, F107).
B_FILES = [os.path.join(PROCESSED, "grib_features_v16_window.csv"),
           os.path.join(PROCESSED, "grib_features_sealed_window.csv")]
FAMILY_FILES = {
    "L": ("lapse_rate_t2_t850", ["session49_v16_window_with_upper_air.csv",
                                 "session49_sealed_window_with_upper_air.csv",
                                 "session63_reserved_window_with_upper_air.csv"]),
    "D": ("dewpoint_depression_t2m", ["session51_v16_window_with_moisture.csv",
                                      "session51_sealed_window_with_moisture.csv",
                                      "session63_reserved_window_with_moisture.csv"]),
    "T": ("pressure_tendency_3h_hpa", ["session53_v16_window_with_pressure.csv",
                                       "session53_sealed_window_with_pressure.csv",
                                       "session63_reserved_window_with_pressure.csv"]),
    "R": ("dswrf_2h_wm2", ["session55_v16_window_with_radiation.csv",
                           "session55_sealed_window_with_radiation.csv",
                           "session63_reserved_window_with_radiation.csv"]),
}
OBS_CHUNKS = rec.OBS_CHUNKS

KSFO_FEATURES = os.path.join(PROCESSED, "session76_ksfo_features.csv")
KSFO_OBS = os.path.join(PROCESSED, "session76_ksfo_observations.csv")
KSFO_SHA256 = {
    KSFO_FEATURES:
        "f228301edd2c155bf1062dfb57f5e83ef0ce17050151bcdcf5e9983b2bc3e5c9",
    KSFO_OBS:
        "b987dd4fad6d1baabefd5a15e31df8260e696b4193f4296d31eebb99c027736c",
}

# The two recorded folds (F109; D70.3 look B): (train_start, train_end,
# test_start, test_end, stations).
GATE_FOLDS = {
    "F109": (date(2021, 3, 24), date(2024, 7, 31), date(2024, 8, 1),
             date(2025, 7, 31), RECORD_STATIONS),
    "KSFO look B": (date(2021, 3, 24), date(2025, 7, 31), date(2025, 8, 1),
                    date(2026, 7, 31), ["SFO"]),
}
F109_GRID = os.path.join(PROCESSED, "session63_reserved_confirm_grid.csv")
F119_GRID = os.path.join(PROCESSED, "session78_ksfo_looks_grid.csv")

TS_HEADER = ["station", "target_date", "target_hour"] + G15 + [
    "temperature_grib_c", "obs_c"]


def stop(msg):
    raise SystemExit("STOP: " + msg)


def rel(p):
    return os.path.relpath(p, ROOT)


def finite_float(s):
    """float(s) if it is a finite number, else None (SPEC 8.7 item 2)."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def guard_date(d, where):
    if d >= FORBIDDEN_FROM:
        stop("a row dated %s (on or after 2026-08-01) is in %s" % (d, where))


def season_year(d):
    """The Aug-Jul year a date falls in, e.g. 2021-03-24 -> '2020-21'."""
    y = d.year if d.month >= 8 else d.year - 1
    return "%d-%02d" % (y, (y + 1) % 100)


# ------------------------------------------------------------------ build

def load_b(counts):
    """The B files (sessions 37/40), as rec.load_base_unfiltered, with
    non-finite values rejected and counted."""
    out = {st: {} for st in RECORD_STATIONS}
    for path in B_FILES:
        with open(path) as fh:
            for r in csv.DictReader(fh):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                guard_date(d, rel(path))
                vals = [finite_float(r[c]) for c in (
                    "temperature_grib_c", "cloud_cover_grib_pct",
                    "wind_speed_grib_kmh")]
                if any(v is None for v in vals):
                    counts[st]["non_finite"] += 1
                    continue
                if d in out[st]:
                    stop("duplicate B row %s %s" % (st, d))
                out[st][d] = {"fc": vals[0], "cloud": vals[1],
                              "wind": vals[2]}
    return out


def load_family(code, counts):
    """One family's v16, sealed and reserved-year files, as rec.load_family
    with its F107 wiring, with non-finite values rejected and counted."""
    col, names = FAMILY_FILES[code]
    out = {st: {} for st in RECORD_STATIONS}
    for name in names:
        path = os.path.join(PROCESSED, name)
        with open(path) as fh:
            for r in csv.DictReader(fh):
                st = r["station"]
                if st not in out:
                    continue
                d = date.fromisoformat(r["target_date"])
                guard_date(d, name)
                v = finite_float(r[col])
                if v is None:
                    counts[st]["non_finite"] += 1
                    continue
                if d in out[st]:
                    stop("duplicate %s row %s %s" % (code, st, d))
                out[st][d] = v
    return out


def load_obs(station, target_hour):
    """rec.load_obs_all's pairing (the record's historical pairing, SPEC
    4.5's note; G1-G3), with a non-finite temperature rejected and counted.
    Returns ({date: obs}, non_finite)."""
    series, non_finite = {}, 0
    for start, end in OBS_CHUNKS:
        path = os.path.join(RAW, "iem_asos_%s_%s_%s_routine.csv" % (
            station, start, end))
        with open(path) as fh:
            for r in csv.DictReader(fh):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(
                    minute=0, second=0, microsecond=0)
                if nearest.hour != target_hour:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    continue
                v = finite_float(raw)
                if v is None:
                    non_finite += 1
                    continue
                series[nearest.date()] = v
    for d in series:
        guard_date(d, "the %s observations" % station)
    return series, non_finite


def build_record_airports(counts):
    b_all = load_b(counts)
    fam = {c: load_family(c, counts) for c in FAMILY_FILES}
    rows = {}
    for st in RECORD_STATIONS:
        obs, obs_nf = load_obs(st, STATIONS[st])
        counts[st]["non_finite"] += obs_nf
        rows[st] = []
        for d in sorted(b_all[st]):
            if not FIRST_DAY <= d <= LAST_DAY:
                stop("%s B row %s is outside %s..%s" % (st, d, FIRST_DAY,
                                                        LAST_DAY))
            if not all(d in fam[c][st] for c in FAMILY_FILES):
                counts[st]["cc_dropped"] += 1
                continue
            if d not in obs:
                counts[st]["no_obs"] += 1
                continue
            b = b_all[st][d]
            rows[st].append({
                "date": d, "fc": b["fc"], "cloud": b["cloud"],
                "wind": b["wind"],
                # SPEC 8.1: D's floor transform.
                "dewpoint_depression_t2m_floored": max(fam["D"][st][d], 0.0),
                "lapse_rate_t2_t850": fam["L"][st][d],
                "dswrf_2h_wm2": fam["R"][st][d],
                "pressure_tendency_3h_hpa": fam["T"][st][d],
                "obs": obs[d],
            })
        counts[st]["base_rows"] = len(b_all[st])
    return rows


def build_ksfo(counts):
    """session77_ksfo_looks.load (with every value parsed) and windows."""
    c = counts["SFO"]
    feat, obs, obs_present = {}, {}, set()
    base_rows = 0
    with open(KSFO_FEATURES) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            guard_date(d, rel(KSFO_FEATURES))
            if r["station"] != "SFO" or r["target_hour"] != "20":
                stop("a KSFO features row is not SFO at 20 UTC")
            base_rows += 1
            if r["complete_case"] != "1":
                c["cc_dropped"] += 1
                continue
            vals = {k: finite_float(r[k])
                    for k in G15 + ["temperature_grib_c"]}
            if any(v is None for v in vals.values()):
                c["non_finite"] += 1
                c["cc_dropped"] += 1
                continue
            if vals["temp"] != vals["temperature_grib_c"]:
                stop("KSFO temp differs from temperature_grib_c on %s" % d)
            if d in feat:
                stop("duplicate KSFO features row %s" % d)
            feat[d] = {
                "date": d, "fc": vals["temperature_grib_c"],
                "cloud": vals["cloud_cover"], "wind": vals["wind_speed_10m"],
                "dewpoint_depression_t2m_floored":
                    vals["dewpoint_depression_t2m_floored"],
                "lapse_rate_t2_t850": vals["lapse_rate_t2_t850"],
                "dswrf_2h_wm2": vals["dswrf_2h_wm2"],
                "pressure_tendency_3h_hpa": vals["pressure_tendency_3h_hpa"],
            }
    with open(KSFO_OBS) as fh:
        for r in csv.DictReader(fh):
            d = date.fromisoformat(r["target_date"])
            guard_date(d, rel(KSFO_OBS))
            if r["station"] != "SFO" or r["target_hour"] != "20":
                stop("a KSFO observations row is not SFO at 20 UTC")
            if r["pair_status"] != "paired":
                continue
            v = finite_float(r["obs_c"])
            if v is None:
                c["non_finite"] += 1
                continue
            if d in obs:
                stop("duplicate KSFO observation %s" % d)
            obs[d] = v
            obs_present.add(d)
    rows = []
    for d in sorted(feat):
        if not FIRST_DAY <= d <= LAST_DAY:
            stop("KSFO row %s is outside %s..%s" % (d, FIRST_DAY, LAST_DAY))
        if d not in obs_present:
            c["no_obs"] += 1
            continue
        rows.append({**feat[d], "obs": obs[d]})
    c["base_rows"] = base_rows
    return rows


def season_values(d):
    a = 2 * math.pi * rec.year_fraction(d)
    return math.sin(a), math.cos(a)


def to_csv_row(st, r):
    s, co = season_values(r["date"])
    vals = [r["fc"], s, co, r["cloud"], r["wind"],
            r["dewpoint_depression_t2m_floored"], r["lapse_rate_t2_t850"],
            r["dswrf_2h_wm2"], r["pressure_tendency_3h_hpa"], r["fc"],
            r["obs"]]
    return [st, r["date"].isoformat(), STATIONS[st]] + [repr(v) for v in vals]


def build():
    if os.path.exists(TRAINING_SET):
        stop("refusing to start: %s exists" % rel(TRAINING_SET))
    for p, h in KSFO_SHA256.items():
        got = sha256(p)
        print("%s  %s  (D70.2: %s)" % (got, rel(p),
                                        "equal" if got == h else "DIFFERENT"))
        if got != h:
            stop("KSFO file SHA-256 mismatch")

    print("\nInput files, SHA-256:")
    inputs = [RECORD_SCRIPT] + B_FILES + [
        os.path.join(PROCESSED, n) for c in FAMILY_FILES
        for n in FAMILY_FILES[c][1]]
    inputs += [os.path.join(RAW, "iem_asos_%s_%s_%s_routine.csv" % (
        st, a, b)) for st in RECORD_STATIONS for a, b in OBS_CHUNKS]
    inputs += [KSFO_FEATURES, KSFO_OBS]
    for p in inputs:
        print("  %s  %s" % (sha256(p), rel(p)))

    counts = {st: {"non_finite": 0, "cc_dropped": 0, "no_obs": 0,
                   "base_rows": 0} for st in STATIONS}
    rows = build_record_airports(counts)
    rows["SFO"] = build_ksfo(counts)

    print("\nPer airport (rows are complete-case and paired; D floored):")
    all_days = [FIRST_DAY + timedelta(days=i)
                for i in range((LAST_DAY - FIRST_DAY).days + 1)]
    for st in STATIONS:
        rs = rows[st]
        dates = [r["date"] for r in rs]
        dup = len(dates) - len(set(dates))
        if dup:
            stop("%s has %d duplicate dates" % (st, dup))
        if dates != sorted(dates):
            stop("%s rows are not in ascending date order" % st)
        if dates[-1] > LAST_DAY:
            stop("%s last date %s is after %s" % (st, dates[-1], LAST_DAY))
        per_year = {}
        for d in dates:
            per_year[season_year(d)] = per_year.get(season_year(d), 0) + 1
        missing = [d for d in all_days if d not in set(dates)]
        c = counts[st]
        print("\n%s (target hour %02d UTC)" % (st, STATIONS[st]))
        print("  rows %d; first %s; last %s (on or before 2026-07-31: %s)" % (
            len(rs), dates[0], dates[-1], dates[-1] <= LAST_DAY))
        print("  rows per Aug-Jul year: " + ", ".join(
            "%s %d" % kv for kv in sorted(per_year.items())))
        print("  duplicate dates: %d" % dup)
        print("  base feature rows read: %d; non-finite values rejected: %d; "
              "complete-case rows dropped: %d; rows dropped for no paired "
              "observation: %d" % (c["base_rows"], c["non_finite"],
                                   c["cc_dropped"], c["no_obs"]))
        print("  calendar days in %s..%s with no row: %d" % (
            FIRST_DAY, LAST_DAY, len(missing)))
        if len(missing) <= 20:
            for d in missing:
                print("    %s" % d)

    n = 0
    with open(TRAINING_SET, "x", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(TS_HEADER)
        for st in STATIONS:
            for r in rows[st]:
                w.writerow(to_csv_row(st, r))
                n += 1
    print("\nwrote %s: %d data rows; SHA-256 %s" % (
        rel(TRAINING_SET), n, sha256(TRAINING_SET)))


# ------------------------------------------------------------------ shared by --gate and --freeze

def load_training_set():
    """station -> list of rows, ascending date (G19). Every value is
    finite and every date is on or before 2026-07-31, or the script stops."""
    out = {st: [] for st in STATIONS}
    with open(TRAINING_SET) as fh:
        reader = csv.reader(fh)
        if next(reader) != TS_HEADER:
            stop("the training set header is not as written by --build")
        for rec_row in reader:
            st, d = rec_row[0], date.fromisoformat(rec_row[1])
            guard_date(d, rel(TRAINING_SET))
            if st not in STATIONS or int(rec_row[2]) != STATIONS[st]:
                stop("unexpected station or hour in the training set")
            vals = [finite_float(v) for v in rec_row[3:]]
            if any(v is None for v in vals):
                stop("non-finite value in the training set at %s %s" % (st, d))
            row = dict(zip(G15 + ["temperature_grib_c", "obs_c"], vals))
            if (row["season_sin"], row["season_cos"]) != season_values(d):
                stop("stored season values differ from the record's formula")
            if row["temp"] != row["temperature_grib_c"]:
                stop("temp differs from temperature_grib_c")
            row["date"] = d
            out[st].append(row)
    for st, rs in out.items():
        ds = [r["date"] for r in rs]
        if ds != sorted(set(ds)):
            stop("%s rows are not unique and ascending" % st)
    return out


def matrix(rows, keys):
    """G15 (or its first five) as a float64 array, no column names (G15)."""
    x = np.array([[r[k] for k in keys] for r in rows], dtype=np.float64)
    if x.shape != (len(rows), len(keys)) or not np.all(np.isfinite(x)):
        stop("matrix shape is wrong or it holds a non-finite value")
    return x


def target(rows):
    """G20: obs - temperature_grib_c, unrounded."""
    return np.array([r["obs_c"] - r["temperature_grib_c"] for r in rows],
                    dtype=np.float64)


def fit(rows, keys):
    """G14: LGBMRegressor(**LGB_PARAMS).fit(x, y), nothing else (G17)."""
    m = rec.lgb.LGBMRegressor(**rec.LGB_PARAMS)
    m.fit(matrix(rows, keys), target(rows))
    return m


def print_env():
    print("python %s  numpy %s  lightgbm %s" % (
        platform.python_version(), np.__version__, lightgbm.__version__))
    print("training set %s  SHA-256 %s" % (rel(TRAINING_SET),
                                           sha256(TRAINING_SET)))


# ------------------------------------------------------------------ gate

def recorded_values():
    rec_vals = {}
    with open(F109_GRID) as fh:
        for r in csv.DictReader(fh):
            rec_vals[(r["station"], "B")] = float(r["b_mae"])
            rec_vals[(r["station"], "B+D,L,R,T")] = float(r["final_mae"])
    with open(F119_GRID) as fh:
        for r in csv.DictReader(fh):
            if (r["look"] == "B" and r["row_type"] == "rung"
                    and r["name"] in ("B", "B+D,L,R,T")):
                rec_vals[("SFO", r["name"])] = float(r["value"])
    return rec_vals


def gate():
    print_env()
    data = load_training_set()
    recorded = recorded_values()
    print("\nReproduction gate (verification only; no verdict):")
    print("%-12s %-5s %-10s %6s %6s %22s %22s %s" % (
        "fold", "stn", "model", "train", "test", "recomputed", "recorded",
        "equal"))
    all_equal = True
    for fold, (tr_s, tr_e, te_s, te_e, stations) in GATE_FOLDS.items():
        for st in stations:
            train = [r for r in data[st] if tr_s <= r["date"] <= tr_e]
            test = [r for r in data[st] if te_s <= r["date"] <= te_e]
            if not (train and test and train[-1]["date"] < test[0]["date"]):
                stop("fold %s %s: training is not before test" % (fold, st))
            for name, keys in (("B", B_KEYS), ("B+D,L,R,T", G15)):
                m = fit(train, keys)
                pred = m.predict(matrix(test, keys))
                errs = [(r["temperature_grib_c"] + float(pred[i])) - r["obs_c"]
                        for i, r in enumerate(test)]
                got = rec.mae(errs)
                want = recorded[(st, name)]
                eq = got == want
                all_equal &= eq
                print("%-12s %-5s %-10s %6d %6d %22r %22r %s" % (
                    fold, st, name, len(train), len(test), got, want,
                    "yes" if eq else "NO"))
    print("\nGATE: %s (%s)" % ("PASS" if all_equal else "FAIL",
                               "all twelve values equal the record exactly"
                               if all_equal else "a value differs"))
    if not all_equal:
        raise SystemExit(1)


# ------------------------------------------------------------------ freeze

def freeze():
    if os.path.exists(MODEL_DIR):
        stop("refusing to start: %s exists" % rel(MODEL_DIR))
    print_env()
    ts_sha = sha256(TRAINING_SET)
    data = load_training_set()
    os.makedirs(MODEL_DIR)
    manifest = {
        "description": "Session 81 frozen models for the 2026-27 GFS forward "
                       "test (DECISIONS D73, F122). Never refit.",
        "training_set": rel(TRAINING_SET),
        "training_set_sha256": ts_sha,
        "columns_bdlrt": G15,
        "columns_b": B_KEYS,
        "target": "obs_c - temperature_grib_c (G20)",
        "prediction": "temperature_grib_c + model prediction",
        "lgb_params": rec.LGB_PARAMS,
        "api": "lightgbm.LGBMRegressor(**lgb_params).fit(x, y); x float64, "
               "no column names; rows in ascending date order",
        "python": platform.python_version(),
        "numpy": np.__version__,
        "lightgbm": lightgbm.__version__,
        "airports": {},
    }
    print("\nFrozen models:")
    for st, rows in data.items():
        entry = {"target_hour_utc": STATIONS[st],
                 "train_start": rows[0]["date"].isoformat(),
                 "train_end": rows[-1]["date"].isoformat(),
                 "n_rows": len(rows)}
        # D73.2: mean(observation minus raw GFS (GRIB)) over the same rows.
        entry["mean_bias_c"] = float(np.mean(
            [r["obs_c"] - r["temperature_grib_c"] for r in rows]))
        for tag, keys in (("bdlrt", G15), ("b", B_KEYS)):
            m = fit(rows, keys)
            path = os.path.join(MODEL_DIR, "%s_%s.txt" % (st, tag))
            if os.path.exists(path):
                stop("refusing to overwrite %s" % rel(path))
            m.booster_.save_model(path)
            x = matrix(rows, keys)
            reloaded = lightgbm.Booster(model_file=path)
            diff = float(np.max(np.abs(reloaded.predict(x) - m.predict(x))))
            h = sha256(path)
            entry["model_%s_file" % tag] = os.path.basename(path)
            entry["model_%s_sha256" % tag] = h
            print("  %-4s %-5s rows %d  %s  %s  reload max |diff| %r" % (
                st, tag, len(rows), h, rel(path), diff))
            if diff != 0.0:
                stop("reloaded %s predicts differently" % rel(path))
        print("  %-4s mean-bias constant %r (%s..%s, %d rows)" % (
            st, entry["mean_bias_c"], entry["train_start"],
            entry["train_end"], entry["n_rows"]))
        manifest["airports"][st] = entry
    mpath = os.path.join(MODEL_DIR, "manifest.json")
    with open(mpath, "x") as fh:
        json.dump(manifest, fh, indent=2)
        fh.write("\n")
    print("\nwrote %s  SHA-256 %s" % (rel(mpath), sha256(mpath)))


def main():
    args = sys.argv[1:]
    modes = {"--build": build, "--gate": gate, "--freeze": freeze}
    if len(args) != 1 or args[0] not in modes:
        raise SystemExit("usage: session81_freeze_forward_models.py "
                         "--build | --gate | --freeze")
    print("=" * 78)
    print("session81_freeze_forward_models.py %s" % args[0])
    print("=" * 78)
    modes[args[0]]()


if __name__ == "__main__":
    main()
