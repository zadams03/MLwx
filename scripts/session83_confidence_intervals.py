"""Session 83, Step 3: confidence intervals for every result on record
(SPEC 5.4, DECISIONS D72.3, D75.2). Recorded as F125.

Offline. Reads committed files only. Writes nothing; it prints.

Descriptive only. These intervals change no verdict and are not a new look
(D75.2, SPEC 2.5). Nothing is refit differently, retuned, reselected or
re-locked.

Where the per-day errors come from:
- F16, F30, F47, F64, F82 (minimal method): the record's own sealed-test
  scripts, scripts/session{07,13,18,24,29}_test.py. Each calls main() at
  import time, which would re-run it and overwrite its committed output
  note. So this script parses each file and runs only its imports,
  constants, classes and function definitions (every top-level statement
  except the docstring, the libomp loader shim, which has already run via
  the import below, and the bare main() call). It then calls, in main()'s
  own order, prove_it_matches_the_lock(), join(), fit_on_training() and
  score_test_year(). Their own printed text is suppressed. No file is
  edited; no file is written.
- F94 (richer, 5-feature): functions and constants imported from
  scripts/session39_sealed_test.py (guarded by __main__), following its
  run_airport() step by step, with its guards (the in-window date guard,
  the row assertions, the training-row reconciliation and the sealed-row
  ceiling) applied exactly as it applies them.
- F109 (selected, B+D,L,R,T): functions and constants imported from
  scripts/session62_reserved_confirm.py (guarded by __main__), following
  its run_confirm() step by step, with its two guards applied. Same
  approach as session 81's --gate (F122.4). The session-48 reserved-year
  guard is not called, edited or disabled.
- F119 (KSFO looks A and B): the per-day predictions already saved in
  data/processed/session78_ksfo_looks_predictions.csv (D70.6). No refit.

Reproduction gate (D75.2): every MAE recomputed (model, raw GFS,
persistence) must equal the entry's recorded figure at the entry's printed
precision. A result that fails gets no interval.

Intervals (session 83 prompt, 3.3): paired per-day MAE difference
d = MAE(reference) - MAE(model), in degC, and skill = 1 - MAE(model) /
MAE(reference), in %. Moving-block bootstrap: days ordered by date; blocks
of 7 consecutive entries; block starts uniform on 0..n-7; ceil(n/7)
blocks, truncated to n; the same resampled days for model and reference;
10,000 resamples; numpy.random.default_rng(83), one generator for the whole
run, in the table's order; 95% percentile interval.
"""

import ast
import contextlib
import csv
import hashlib
import io
import math
import os
import subprocess
import sys

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

RECORD_F109 = os.path.join(HERE, "session62_reserved_confirm.py")
RECORD_F109_SHA256 = \
    "9f8af9afa754220ec525481b8640f6f4808f036bcabcfbecadac80331fdc80b4"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


if sha256(RECORD_F109) != RECORD_F109_SHA256:
    raise SystemExit("STOP: session62_reserved_confirm.py's SHA-256 is not "
                     "D70.2's")

# Importing the record script runs its libomp loader shim (D24), which may
# restart this process once; the check above then runs again.
import session62_reserved_confirm as s62  # noqa: E402
import session39_sealed_test as s39  # noqa: E402

from datetime import date, datetime, timedelta  # noqa: E402

import numpy as np  # noqa: E402
import lightgbm as lgb  # noqa: E402

PROCESSED = os.path.join(ROOT, "data", "processed")
KSFO_PRED = os.path.join(PROCESSED, "session78_ksfo_looks_predictions.csv")
FORBIDDEN_FROM = date(2026, 8, 1)

N_BOOT = 10_000
BLOCK = 7
SEED = 83
AIRPORTS5 = ["EGLC", "LFPG", "DSM", "YSDU", "RNO"]
HOURS = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20}

MINIMAL_SCRIPTS = {
    "EGLC": ("F16", "session07_test.py"),
    "LFPG": ("F30", "session13_test.py"),
    "DSM": ("F47", "session18_test.py"),
    "YSDU": ("F64", "session24_test.py"),
    "RNO": ("F82", "session29_test.py"),
}

# Recorded figures, as each entry prints them: (model, raw GFS,
# persistence), the printed decimals, and the recorded day counts
# (model/raw days, persistence days).
RECORDED = {
    "minimal": {  # F16, F30, F47, F64, F82: 3 dp, one common day set
        "EGLC": (("1.040", "1.242", "2.096"), 3, 363, 363),
        "LFPG": (("1.208", "1.396", "2.300"), 3, 363, 363),
        "DSM": (("1.700", "1.815", "4.003"), 3, 365, 365),
        "YSDU": (("1.210", "1.251", "2.669"), 3, 347, 347),
        "RNO": (("1.458", "1.414", "2.490"), 3, 365, 365),
    },
    "F94": {  # 5-feature, 3 dp; persistence days from F94 Task 2
        "EGLC": (("1.000", "1.254", "2.096"), 3, 364, 363),
        "LFPG": (("1.156", "1.382", "2.300"), 3, 364, 363),
        "DSM": (("1.636", "1.733", "4.003"), 3, 365, 365),
        "YSDU": (("1.179", "1.317", "2.669"), 3, 356, 347),
        "RNO": (("1.346", "1.512", "2.490"), 3, 365, 365),
    },
    "F109": {  # B+D,L,R,T, 4 dp
        "EGLC": (("1.0008", "1.2362", "2.2259"), 4, 364, 363),
        "LFPG": (("1.2369", "1.4091", "2.5233"), 4, 365, 365),
        "DSM": (("1.4123", "1.7043", "4.1081"), 4, 365, 365),
        "YSDU": (("1.2643", "1.4897", "2.5775"), 4, 360, 355),
        "RNO": (("1.2742", "1.6135", "2.7563"), 4, 365, 365),
    },
    "F119": {  # KSFO, full precision as F119.3 prints it
        "A": (("1.2575770731513778", "1.4262582417582421",
               "1.5112947658402205"), None, 364, 363),
        "B": (("1.3830033790440732", "1.7321205479452053",
               "1.717232876712329"), None, 365, 365),
    },
}


def rel(p):
    return os.path.relpath(p, ROOT)


def fmt(x, dp):
    return repr(float(x)) if dp is None else f"{x:.{dp}f}"


def git_clean(path):
    out = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path],
                         cwd=ROOT)
    return out.returncode == 0


# ------------------------------------------------------------------ loaders

def load_minimal_module(fname):
    """Run a minimal-method test script's definitions without its main().

    Keeps every top-level statement except: the module docstring, the
    libomp shim `if` block (already run by the import above), and the bare
    `main()` call. Returns the namespace."""
    path = os.path.join(HERE, fname)
    src = open(path).read()
    tree = ast.parse(src)
    kept, skipped = [], []
    for i, node in enumerate(tree.body):
        if i == 0 and isinstance(node, ast.Expr) and isinstance(
                getattr(node, "value", None), ast.Constant):
            skipped.append(f"line {node.lineno}: module docstring")
            continue
        if isinstance(node, ast.If) and "_SENTINEL" in ast.unparse(node.test):
            skipped.append(f"line {node.lineno}: libomp loader shim")
            continue
        if (isinstance(node, ast.Expr) and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "main"):
            skipped.append(f"line {node.lineno}: main() call")
            continue
        if not isinstance(node, (ast.Import, ast.ImportFrom, ast.Assign,
                                 ast.AnnAssign, ast.FunctionDef,
                                 ast.ClassDef)):
            raise SystemExit(f"STOP: unexpected top-level statement in "
                             f"{fname} at line {node.lineno}")
        kept.append(node)
    mod = ast.Module(body=kept, type_ignores=[])
    ns = {"__file__": path, "__name__": f"session83_view_{fname[:-3]}"}
    exec(compile(mod, path, "exec"), ns)
    return ns, skipped


def minimal_result(station):
    """Per-day errors for one minimal-method airport, from its record
    script's own functions, called in its main()'s order."""
    entry, fname = MINIMAL_SCRIPTS[station]
    ns, skipped = load_minimal_module(fname)
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink):
        ns["prove_it_matches_the_lock"]()
        joined = ns["join"]()
        if len(joined) == 4:
            train, test, obs_all, reconciled = joined
        else:
            (train, test, obs_all), reconciled = joined, True
        model, mean_bias, clim, x_tr, y_tr = ns["fit_on_training"](train)
        common, methods, pred_resid = ns["score_test_year"](
            test, obs_all, model, mean_bias, clim)
    dates = [r["date"] for r in common]
    for d in dates:
        if d >= FORBIDDEN_FROM:
            raise SystemExit("STOP: a date on or after 2026-08-01")
    info = dict(script=fname, skipped=skipped, reconciled=reconciled,
                n_train=len(train), n_test_paired=len(test),
                lock_check="passed (assertions did not trip)",
                suppressed_chars=len(sink.getvalue()))
    e_model = np.abs(np.array(methods["ML-corrected"], dtype=float))
    e_raw = np.abs(np.array(methods["Raw GFS"], dtype=float))
    e_per = np.abs(np.array(methods["Persistence"], dtype=float))
    # One common day set (D21.8): every rung on the same days.
    return dict(entry=entry, info=info,
                model_dates=dates, e_model=e_model,
                raw=(dates, e_raw), persist=(dates, e_per))


def f94_result(station):
    """Per-day errors for F94 at one airport, following
    session39_sealed_test.run_airport() step by step."""
    th = s39.AIRPORTS[station]
    obs_full, _, _ = s39.load_obs_all(station, th)
    train_grib = s39.load_grib_features(
        s39.TRAIN_GRIB_PATH, s39.TRAIN_START, s39.TRAIN_END,
        refuse_outside_window=True)[station]
    sealed_grib = s39.load_grib_features(
        s39.SEALED_GRIB_PATH, s39.SEALED_FROM, s39.SEALED_UNTIL,
        refuse_outside_window=True)[station]
    train_rows, _, _ = s39.join_rows(train_grib, obs_full,
                                     s39.TRAIN_START, s39.TRAIN_END)
    test_rows, _, _ = s39.join_rows(sealed_grib, obs_full,
                                    s39.SEALED_FROM, s39.SEALED_UNTIL)
    for r in train_rows:
        assert r["date"] < s39.SEALED_FROM, \
            "D48 self-guard: a training row is inside the sealed year"
    for r in test_rows:
        assert s39.SEALED_FROM <= r["date"] <= s39.SEALED_UNTIL, \
            "D48 self-guard: a test row is outside the sealed year"
    if len(train_rows) != s39.EXPECTED_TRAIN_ROWS[station]:
        raise AssertionError(f"D48.12 STOP SIGNAL: {station} training rows")
    if len(test_rows) > s39.SEALED_ROW_CEILING[station]:
        raise AssertionError(f"D48.12 STOP SIGNAL: {station} sealed rows")

    y_tr = np.array([r["resid"] for r in train_rows], dtype=float)
    m5 = lgb.LGBMRegressor(**s39.LGB_PARAMS)
    m5.fit(s39.features_5(train_rows), y_tr)
    pred5 = m5.predict(s39.features_5(test_rows))

    dates = [r["date"] for r in test_rows]
    e_model = np.abs(np.array(
        [(r["fc"] + float(pred5[i])) - r["obs"]
         for i, r in enumerate(test_rows)], dtype=float))
    e_raw = np.abs(np.array([r["fc"] - r["obs"] for r in test_rows],
                            dtype=float))
    p_dates, p_err = [], []
    for r in test_rows:
        prev = obs_full.get(r["date"] - timedelta(days=1))
        if prev is None:
            continue
        p_dates.append(r["date"])
        p_err.append(float(prev) - r["obs"])
    info = dict(n_train=len(train_rows), n_test=len(test_rows),
                expected_train=s39.EXPECTED_TRAIN_ROWS[station],
                sealed_ceiling=s39.SEALED_ROW_CEILING[station])
    return dict(entry="F94", info=info, model_dates=dates, e_model=e_model,
                raw=(dates, e_raw),
                persist=(p_dates, np.abs(np.array(p_err, dtype=float))))


_F109_CACHE = {}


def f109_merged():
    if not _F109_CACHE:
        l_all, hl = s62.load_family("L", ["lapse_rate_t2_t850"])
        d_all, hd = s62.load_family("D", ["dewpoint_depression_t2m"])
        t_all, ht = s62.load_family("T", ["pressure_tendency_3h_hpa"])
        r_all, hr = s62.load_family("R", ["dswrf_2h_wm2"])
        if hl or hd or ht or hr:  # run_confirm()'s first guard
            raise AssertionError("STOP: reserved-year rows found inside the "
                                 "L/D/T/R source files themselves (D51).")
        base_all = s62.load_base_unfiltered()
        _F109_CACHE["merged"] = s62.build_complete_case(
            base_all, l_all, d_all, t_all, r_all)
    return _F109_CACHE["merged"]


def f109_result(station):
    """Per-day errors for F109 at one airport, following
    session62_reserved_confirm.run_confirm() step by step."""
    merged = f109_merged()
    fold = s62.CONFIRMATION_FOLD
    ts, te = fold["test_start"], fold["test_end"]
    tr_s, tr_e = fold["train_start"], fold["train_end"]
    # run_confirm()'s second guard.
    if sum(1 for d in merged[station] if ts <= d <= te) == 0:
        raise RuntimeError(f"STOP (D58 reserved-year feature-data gap): "
                           f"{station}")
    obs_all, _, _ = s62.load_obs_all(station, s62.AIRPORTS[station])
    train_raw = {d: r for d, r in merged[station].items()
                 if tr_s <= d <= tr_e}
    test_raw = {d: r for d, r in merged[station].items() if ts <= d <= te}
    train_rows, _ = s62.join_obs(station, train_raw, obs_all)
    test_rows, no_obs = s62.join_obs(station, test_raw, obs_all)
    for r in test_rows:
        if r["date"] >= FORBIDDEN_FROM:
            raise SystemExit("STOP: a date on or after 2026-08-01")
    _, e_model = s62.fit_and_score(set(s62.FINAL_CODES),
                                   s62.FINAL_FEATURE_KEYS,
                                   train_rows, test_rows)
    dates = [r["date"] for r in test_rows]
    e_raw = np.abs(np.array([r["fc"] - r["obs"] for r in test_rows],
                            dtype=float))
    p_dates, p_err = [], []
    for r in test_rows:
        prev = obs_all.get(r["date"] - timedelta(days=1))
        if prev is None:
            continue
        p_dates.append(r["date"])
        p_err.append(float(prev) - r["obs"])
    info = dict(n_train=len(train_rows), n_test=len(test_rows),
                no_obs_dropped=no_obs)
    return dict(entry="F109", info=info, model_dates=dates,
                e_model=np.abs(np.array(e_model, dtype=float)),
                raw=(dates, e_raw),
                persist=(p_dates, np.abs(np.array(p_err, dtype=float))))


def f119_result(look):
    """Per-day errors for KSFO look A or B, from the saved predictions."""
    rows = []
    with open(KSFO_PRED) as f:
        for r in csv.DictReader(f):
            if r["look"] == look:
                rows.append(r)
    rows.sort(key=lambda r: r["target_date"])
    dates = [date.fromisoformat(r["target_date"]) for r in rows]
    for d in dates:
        if d >= FORBIDDEN_FROM:
            raise SystemExit("STOP: a date on or after 2026-08-01")
    obs = np.array([float(r["obs_c"]) for r in rows])
    e_model = np.abs(np.array([float(r["BDLRT_c"]) for r in rows]) - obs)
    e_raw = np.abs(np.array([float(r["raw_gfs_c"]) for r in rows]) - obs)
    p_dates, p_err = [], []
    for d, r, o in zip(dates, rows, obs):
        if r["persistence_c"].strip() == "":
            continue
        p_dates.append(d)
        p_err.append(float(r["persistence_c"]) - o)
    info = dict(n_test=len(rows), source=rel(KSFO_PRED))
    return dict(entry="F119", info=info, model_dates=dates, e_model=e_model,
                raw=(dates, e_raw),
                persist=(p_dates, np.abs(np.array(p_err, dtype=float))))


# ------------------------------------------------------------------ gate

def gate(label, key, res):
    """Compare recomputed MAEs with the entry's recorded figures at the
    entry's printed precision. Returns True if all equal."""
    rec_vals, dp, n_rec, np_rec = RECORDED[label][key]
    mae_model = float(np.mean(res["e_model"]))
    mae_raw = float(np.mean(res["raw"][1]))
    mae_per = float(np.mean(res["persist"][1]))
    n = len(res["model_dates"])
    n_p = len(res["persist"][0])
    ok = True
    prec = "full precision (repr)" if dp is None else f"{dp} dp"
    print(f"    {key}: gate at {prec}")
    for name, got, want in (("model", mae_model, rec_vals[0]),
                            ("raw GFS", mae_raw, rec_vals[1]),
                            ("persistence", mae_per, rec_vals[2])):
        g = fmt(got, dp)
        eq = g == want
        ok &= eq
        print(f"      {name:<12} recomputed {g:<20} recorded {want:<20} "
              f"{'equal' if eq else 'DIFFERS'}   (full: {got!r})")
    days_ok = (n == n_rec) and (n_p == np_rec)
    print(f"      days: model/raw {n} (entry {n_rec}), persistence {n_p} "
          f"(entry {np_rec})  {'equal' if days_ok else 'DIFFER'}")
    print(f"      GATE: {'PASSED' if ok else 'FAILED -> no interval'}")
    return ok, days_ok


# ------------------------------------------------------------------ bootstrap

def paired(res, ref):
    """Paired day set for the model against a reference: days on which
    both have an error, ordered by date."""
    m = dict(zip(res["model_dates"], res["e_model"]))
    r_dates, r_err = res[ref]
    pairs = sorted((d, m[d], e) for d, e in zip(r_dates, r_err) if d in m)
    dates = [p[0] for p in pairs]
    assert dates == sorted(set(dates)), "paired days not unique and ordered"
    return (dates, np.array([p[1] for p in pairs]),
            np.array([p[2] for p in pairs]))


def bootstrap(rng, em, er):
    n = len(em)
    k = math.ceil(n / BLOCK)
    starts = rng.integers(0, n - BLOCK + 1, size=(N_BOOT, k))
    idx = (starts[:, :, None] + np.arange(BLOCK)).reshape(N_BOOT, k * BLOCK)
    idx = idx[:, :n]
    mm = em[idx].mean(axis=1)
    mr = er[idx].mean(axis=1)
    d = mr - mm
    skill = 100.0 * (1.0 - mm / mr)
    return (np.percentile(d, [2.5, 97.5]), np.percentile(skill, [2.5, 97.5]))


def main():
    print("Session 83, Step 3: confidence intervals (DECISIONS D75.2)")
    print(f"run at   : {datetime.now():%Y-%m-%d %H:%M:%S} local")
    print(f"python {sys.version.split()[0]}, numpy {np.__version__}, "
          f"lightgbm {lgb.__version__}")
    print("offline; committed files only; nothing written")
    print(f"bootstrap: moving block, block {BLOCK}, {N_BOOT:,} resamples, "
          f"numpy.random.default_rng({SEED}), 95% percentile interval")

    print("\nScripts used (read-only), SHA-256 and whether unchanged "
          "against HEAD:")
    used = [os.path.join(HERE, f) for _, f in MINIMAL_SCRIPTS.values()] + \
        [os.path.join(HERE, "session39_sealed_test.py"), RECORD_F109]
    for p in used:
        print(f"    {rel(p):<42} {sha256(p)}  "
              f"{'unchanged' if git_clean(p) else 'CHANGED'}")
    print(f"    {rel(KSFO_PRED):<42} {sha256(KSFO_PRED)}  "
          f"{'unchanged' if git_clean(KSFO_PRED) else 'CHANGED'}")

    plan = ([("minimal", st, lambda st=st: minimal_result(st))
             for st in AIRPORTS5]
            + [("F94", st, lambda st=st: f94_result(st)) for st in AIRPORTS5]
            + [("F109", st, lambda st=st: f109_result(st))
               for st in AIRPORTS5]
            + [("F119", lk, lambda lk=lk: f119_result(lk)) for lk in "AB"])

    # Pass 1: per-day errors and the gate, for all 17 airport-results.
    print("\n" + "=" * 78)
    print("3.2 Per-day errors and the reproduction gate")
    print("=" * 78)
    results = []
    for label, key, fn in plan:
        res = fn()
        name = (f"{res['entry']} {key}" if label != "F119"
                else f"F119 look {key} (KSFO)")
        print(f"\n  {name}")
        for k, v in res["info"].items():
            print(f"    {k}: {v}")
        ok, days_ok = gate(label, key, res)
        results.append((label, key, name, res, ok, days_ok))

    # Pass 2: intervals, in the table's order, raw GFS before persistence.
    print("\n" + "=" * 78)
    print("3.3 The intervals (d = MAE(reference) - MAE(model), degC; "
          "skill = 1 - model/reference, %)")
    print("=" * 78)
    rng = np.random.default_rng(SEED)
    table = []
    for label, key, name, res, ok, _ in results:
        if not ok:
            print(f"\n  {name}: gate FAILED, no interval (no draws made)")
            continue
        print(f"\n  {name}")
        for ref, ref_name in (("raw", "raw GFS"),
                              ("persist", "persistence")):
            dates, em, er = paired(res, ref)
            n = len(dates)
            mae_m, mae_r = float(em.mean()), float(er.mean())
            d_pt = mae_r - mae_m
            s_pt = 100.0 * (1.0 - mae_m / mae_r)
            (d_lo, d_hi), (s_lo, s_hi) = bootstrap(rng, em, er)
            above = d_lo > 0
            print(f"    vs {ref_name:<11} n={n:<4} "
                  f"({dates[0]}..{dates[-1]})")
            print(f"      MAE on this set: model {mae_m:.4f}, "
                  f"{ref_name} {mae_r:.4f}")
            print(f"      d     = {d_pt:+.4f} degC   95% [{d_lo:+.4f}, "
                  f"{d_hi:+.4f}]   wholly above zero: "
                  f"{'yes' if above else 'no'}")
            print(f"      skill = {s_pt:+.2f}%        95% [{s_lo:+.2f}%, "
                  f"{s_hi:+.2f}%]")
            table.append((label, key, ref_name, n, d_pt, d_lo, d_hi,
                          s_pt, s_lo, s_hi, above))

    print("\n" + "=" * 78)
    print("Summary table")
    print("=" * 78)
    print(f"  {'result':<8} {'airport':<8} {'reference':<12} {'n':>4}  "
          f"{'d degC [95%]':<28} {'skill % [95%]':<28} above 0")
    for (label, key, ref, n, d, dl, dh, s, sl, sh, ab) in table:
        airport = key if label != "F119" else f"KSFO {key}"
        print(f"  {label:<8} {airport:<8} {ref:<12} {n:>4}  "
              f"{d:+.3f} [{dl:+.3f}, {dh:+.3f}]{'':<5} "
              f"{s:+.1f} [{sl:+.1f}, {sh:+.1f}]{'':<8} "
              f"{'yes' if ab else 'no'}")
    n_gate = sum(1 for r in results if r[4])
    print(f"\n  gate passed: {n_gate} of {len(results)} airport-results")
    print("\nEND. Nothing was written. These intervals change no verdict "
          "(D75.2).")


if __name__ == "__main__":
    main()
