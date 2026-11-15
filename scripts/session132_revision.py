#!/usr/bin/env python3
"""Session 132: does the curve's correction predict GFS's next revision? (DECISIONS D127.6, D115.6.)

Descriptive only (D107.2): nothing is selected, tuned or changed because of it; any use needs its own entry.
No observation is used. Offline. Nothing valid after 2026-07-31T23:00 UTC is used.

Rows (D127.6(a)): every row of session 112's regenerated predictions (../MLwx-stagec/analysis112/
pred_<ICAO>.csv.gz, each checked against the SHA-256 held here and in meta.txt) at the 12 airports whose status is
`scored` or `extra`, valid at or before 2026-07-31T23:00 UTC.

Pairing (D127.6(b)): a row (airport, cycle c, lead L, valid v) pairs with the row of the same airport at cycle
c + 6 h, lead L - 6, the same v, when that row is also in the rows and has the same period. Rows that do not pair
are counted by reason, in this order of tests: "lead 3 to 8 (the next lead would be below 3)"; "no next cycle in
the file" (no row at all at cycle c + 6 h); "next row not in the file" (cycle c + 6 h is there but has no row at
lead L - 6); "next row not in (a)" (it exists but its status is not scored or extra, or it is valid after the
limit); "a different period".

Quantities (D127.6(c)): k = curve - raw_gfs at c; r = raw_gfs(c + 6 h, v) - raw_gfs(c, v); k_base = baseline -
raw_gfs at c; b = curve - baseline at c (so k = k_base + b).

Statistics (D127.6(d)), in this order: n; Pearson's correlation of k and r; Spearman's correlation of k and r
(average ranks for ties); the ordinary least squares slope and intercept of r on k; the sign agreement share over
pairs with k and r both non-zero (zero counts reported); mean |r| (raw GFS at c as a forecast of the next raw
GFS), mean |r - k| (the curve at c as that forecast) and their ratio mean |r - k| / mean |r|; Spearman's
correlation of r with k_base and of r with b. Per airport, pooled over its periods and per period.

Intervals (D127.6(e)): 95 % percentile intervals (numpy.percentile, 2.5 and 97.5, linear) by a block bootstrap
over cycle UTC dates: each resample draws the airport's dates with replacement, as many as it has, and every pair
whose cycle falls on a drawn date comes in with it (as often as the date is drawn). 2,000 resamples, one generator
numpy.random.default_rng(132), airports in session 112's order (AIRPORTS); within an airport, the pooled set and
then each period in time order, one draw of 2,000 resamples per set, shared by all statistics, which are computed
on it in (d)'s order. A resampled Spearman correlation ranks the resampled values (ties, including a row drawn
twice, take average ranks).

Breakdowns (D127.6(f)), point values only, pooled over periods: the lead at c (9 to 24, 25 to 48); the cycle
hour; the tercile of |k|, edges at that airport's own |k| values' 1/3 and 2/3 quantiles (numpy.quantile, linear),
bins |k| <= e1, e1 < |k| <= e2, |k| > e2.

Reading (D127.6(g)), fixed in D127 before any value: at an airport the correction points the way GFS next
revises when the interval of Spearman's correlation of k and r (pooled) lies wholly above 0. Counted of 12;
"most airports" is at least 7 of 12.

Modes, run in this order:
  --check    Synthetic data only: the pairing across cycles, across a period boundary and with a missing next
             row; the sign share with zeros; the bootstrap's blocks; the weighted Spearman against scipy.
  --pairs    Counts only, by reason, per airport; no statistic. Writes pair_counts.csv.
  --stats    The statistics, intervals and breakdowns; the count of (g). Writes stats.csv, breakdowns.csv and
             meta.txt.

Outputs in data/processed/session132_revision/, each written once. No em-dashes in any text here (D76.6).
"""

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import io
import os
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PRED_DIR = ROOT.parent / "MLwx-stagec" / "analysis112"
OUT = ROOT / "data" / "processed" / "session132_revision"

LIMIT = dt.datetime(2026, 7, 31, 23, 0)                 # nothing valid after this (D127.6(a))
SEED = 132                                               # D127.6(e)
REPS = 2000                                              # D127.6(e)
KEEP_STATUS = ("scored", "extra")                        # D127.6(a)
STEP = dt.timedelta(hours=6)

# Session 112's order (session112_analysis.AIRPORTS: claim airports, then development airports).
AIRPORTS = ["EDDM", "KORD", "CYYZ", "ZGSZ", "ZUCK", "NZWN", "EGLC", "LFPG", "KDSM", "YSDU", "KRNO", "KSFO"]
PERIODS = {"claim": ["A", "B"], "dev": ["2023-24", "2024-25", "2025-26"]}

# meta.txt's SHA-256 of each prediction file (F155; D98.2: held here, checked by tests/test_session132.py).
PRED_SHA256 = {
    "EDDM": "787ad4462fc5af9abf8ea3fccfb9d06ca7df072565e185a8441b4c730899a83f",
    "KORD": "fd0538334adcfb3f0224cb3b9d39e441dba700779a299a97511d77fbc085dece",
    "CYYZ": "44cdd38036e04d0ca73026b6a84b4748b4568f39aace9c9b637cd414906145cd",
    "ZGSZ": "3c0c840a8fc4f30aa673901fa5ddfd636304665ba0b40ab5fa61793c5eb8364e",
    "ZUCK": "71b466a574c923bf937476aee91c48909f6b918b61afc649b37fa41508678b3f",
    "NZWN": "cc1f51923a2347b256341d1b52a70c6265bda841fb921f773ff5e725236b7262",
    "EGLC": "57754dbd9abd8c32aa506f76afca4dcdd282c555de4790bedec911565a2fa4a8",
    "LFPG": "1b3841523365c9c4d2631d257967fa567983e4a9473ac8554d9f71e40e3faffa",
    "KDSM": "08de86bdc63938d13a16ce9bc2391f0b705582562beace3019837bb041862d9e",
    "YSDU": "5061befa0e7f9138e9141b3266af4848ec4c01485c56834208c96bf6c6da4f23",
    "KRNO": "d2a49ecf2f2ea10aa0ed970a25e627525ab9d0eca06386ba80a82d3e8fabb2d8",
    "KSFO": "1a8707bcb1c16ffb0f523e3efe7933d1a0b7ad446ddce39cf918408bb599c777",
}

REASONS = ["lead 3 to 8 (the next lead would be below 3)", "no next cycle in the file", "next row not in the file",
           "next row not in (a)", "a different period"]
STATS = ["pearson_k_r", "spearman_k_r", "ols_slope", "ols_intercept", "sign_share", "mean_abs_r",
         "mean_abs_r_minus_k", "ratio", "spearman_r_kbase", "spearman_r_b"]


def now_utc():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def ptime(s):
    return dt.datetime.strptime(s, "%Y-%m-%dT%H:%MZ")


def fmt(v):
    if isinstance(v, str):
        return v
    if isinstance(v, (bool, np.bool_)):
        return str(bool(v))
    if isinstance(v, (int, np.integer)):
        return str(int(v))
    if v is None or not np.isfinite(v):
        return ""
    return repr(float(v))


def write_once(path, data):
    path = Path(path)
    if path.exists():
        raise SystemExit(f"STOP: {path} already exists; not overwriting it")
    tmp = path.with_name(path.name + ".partial")
    with open(tmp, "xb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.link(tmp, path)
    os.unlink(tmp)
    return sha256_bytes(data)


def csv_bytes(header, rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow([fmt(v) for v in r])
    return buf.getvalue().encode()


# ------------------------------------------------------------------ reading and pairing

def meta_sha256():
    out = {}
    for line in (PRED_DIR / "meta.txt").read_text().splitlines():
        p = line.split()
        if len(p) >= 2 and p[0].startswith("pred_") and p[0].endswith(".csv.gz"):
            out[p[0][5:9]] = p[-1]
    return out


def read_rows(ic):
    """The file's rows as dicts keyed by (cycle, lead): (period, status, valid, raw_gfs, baseline, curve)."""
    data = (PRED_DIR / f"pred_{ic}.csv.gz").read_bytes()
    if sha256_bytes(data) != PRED_SHA256[ic]:
        raise SystemExit(f"STOP: pred_{ic}.csv.gz's SHA-256 is not meta.txt's")
    rd = csv.reader(io.StringIO(gzip.decompress(data).decode()))
    head = next(rd)
    c = {k: i for i, k in enumerate(head)}
    rows = {}
    for r in rd:
        if r[c["icao"]] != ic:
            raise SystemExit(f"STOP: pred_{ic}.csv.gz holds a row for {r[c['icao']]}")
        key = (ptime(r[c["cycle_utc"]]), int(r[c["lead"]]))
        rows[key] = (r[c["period"]], r[c["status"]], ptime(r[c["valid_utc"]]), r[c["raw_gfs"]], r[c["baseline"]],
                     r[c["curve"]])
    return rows


def in_a(row):
    """D127.6(a): status scored or extra, valid at or before the limit."""
    return row[1] in KEEP_STATUS and row[2] <= LIMIT


def pair_rows(rows):
    """D127.6(b). rows: {(cycle, lead): (period, status, valid, raw_gfs, baseline, curve)}. Returns (pairs, counts):
    pairs = list of (cycle, lead, period, raw_c, baseline_c, curve_c, raw_next); counts = {reason: n} over the rows
    of (a) that do not pair, plus 'rows in (a)', 'paired', 'rows not in (a)'."""
    counts = {k: 0 for k in ["rows read", "rows not in (a)", "rows in (a)", "paired"] + REASONS}
    cycles = {c for c, _ in rows}
    pairs = []
    for (c, L), row in sorted(rows.items()):
        counts["rows read"] += 1
        if not in_a(row):
            counts["rows not in (a)"] += 1
            continue
        counts["rows in (a)"] += 1
        nxt_key = (c + STEP, L - 6)
        nxt = rows.get(nxt_key)
        if L - 6 < 3:
            counts[REASONS[0]] += 1
        elif c + STEP not in cycles:
            counts[REASONS[1]] += 1
        elif nxt is None:
            counts[REASONS[2]] += 1
        elif not in_a(nxt):
            counts[REASONS[3]] += 1
        elif nxt[0] != row[0]:
            counts[REASONS[4]] += 1
        else:
            if nxt[2] != row[2]:
                raise SystemExit(f"STOP: {c} lead {L}: the next row's valid time differs")
            raw, base, cur = float(row[3]), float(row[4]), float(row[5])
            raw_n = float(nxt[3])
            if not (np.isfinite(raw) and np.isfinite(base) and np.isfinite(cur) and np.isfinite(raw_n)):
                raise SystemExit(f"STOP: {c} lead {L}: a value is missing on a row of (a)")
            pairs.append((c, L, row[0], raw, base, cur, raw_n))
            counts["paired"] += 1
    if counts["rows in (a)"] != counts["paired"] + sum(counts[k] for k in REASONS):
        raise SystemExit("STOP: the pairing counts do not add up")
    return pairs, counts


def arrays(pairs):
    c = np.array([p[0] for p in pairs], dtype="datetime64[m]")
    L = np.array([p[1] for p in pairs], dtype=np.int64)
    per = np.array([p[2] for p in pairs])
    raw, base, cur, raw_n = (np.array([p[i] for p in pairs], dtype=float) for i in (3, 4, 5, 6))
    k = cur - raw
    r = raw_n - raw
    return dict(cycle=c, date=c.astype("datetime64[D]"), lead=L, period=per,
                ch=(c.astype("datetime64[h]").astype(np.int64) % 24), k=k, r=r, kb=base - raw, b=cur - base)


# ------------------------------------------------------------------ statistics (weights: row multiplicities)

class Ranker:
    """Average ranks of x under row weights w (a row with weight m stands for m copies), in O(n)."""

    def __init__(self, x):
        u, self.inv = np.unique(x, return_inverse=True)
        self.ng = len(u)

    def ranks(self, w):
        W = np.bincount(self.inv, weights=w, minlength=self.ng)
        cum = np.cumsum(W)
        return (cum - (W - 1.0) / 2.0)[self.inv]


def wcorr(x, y, w):
    sw = w.sum()
    mx, my = (w @ x) / sw, (w @ y) / sw
    dx, dy = x - mx, y - my
    sxx, syy, sxy = w @ (dx * dx), w @ (dy * dy), w @ (dx * dy)
    if sxx <= 0 or syy <= 0:
        return np.nan
    return float(sxy / np.sqrt(sxx * syy))


class StatSet:
    """All of (d)'s statistics on one set of pairs, for any row weights."""

    def __init__(self, X, m):
        self.k, self.r, self.kb, self.b = X["k"][m], X["r"][m], X["kb"][m], X["b"][m]
        self.ar, self.ark = np.abs(self.r), np.abs(self.r - self.k)
        nz = (self.k != 0) & (self.r != 0)
        self.nz = nz.astype(float)
        self.agree = (nz & (np.sign(self.k) == np.sign(self.r))).astype(float)
        self.rk, self.rr, self.rkb, self.rb = (Ranker(v) for v in (self.k, self.r, self.kb, self.b))

    def stats(self, w):
        k, r = self.k, self.r
        sw = w.sum()
        out = {}
        out["pearson_k_r"] = wcorr(k, r, w)
        rr = self.rr.ranks(w)
        out["spearman_k_r"] = wcorr(self.rk.ranks(w), rr, w)
        mk, mr = (w @ k) / sw, (w @ r) / sw
        sxx = w @ ((k - mk) ** 2)
        slope = float((w @ ((k - mk) * (r - mr))) / sxx) if sxx > 0 else np.nan
        out["ols_slope"] = slope
        out["ols_intercept"] = float(mr - slope * mk)
        nzw = w @ self.nz
        out["sign_share"] = float((w @ self.agree) / nzw) if nzw > 0 else np.nan
        out["mean_abs_r"] = float((w @ self.ar) / sw)
        out["mean_abs_r_minus_k"] = float((w @ self.ark) / sw)
        out["ratio"] = out["mean_abs_r_minus_k"] / out["mean_abs_r"] if out["mean_abs_r"] > 0 else np.nan
        out["spearman_r_kbase"] = wcorr(rr, self.rkb.ranks(w), w)
        out["spearman_r_b"] = wcorr(rr, self.rb.ranks(w), w)
        return out

    def counts(self):
        return dict(n=len(self.k), k_zero=int((self.k == 0).sum()), r_zero=int((self.r == 0).sum()),
                    both_nonzero=int(self.nz.sum()))


def block_weights(rng, date_idx, nd, reps):
    """Row weights for each resample: every pair of a drawn date comes in as often as the date is drawn."""
    draws = rng.integers(0, nd, size=(reps, nd))
    for j in range(reps):
        yield np.bincount(draws[j], minlength=nd)[date_idx].astype(float)


def bootstrap(rng, S, dates, reps=REPS):
    u, idx = np.unique(dates, return_inverse=True)
    vals = {s: np.empty(reps) for s in STATS}
    for j, w in enumerate(block_weights(rng, idx, len(u), reps)):
        st = S.stats(w)
        for s in STATS:
            vals[s][j] = st[s]
    return {s: (float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))) for s, v in vals.items()}, len(u)


# ------------------------------------------------------------------ --check (synthetic data only)

def run_check(args):
    print(f"SESSION 132 revision --check (synthetic data only), {now_utc()}")
    ok_all = True

    def check(name, cond):
        nonlocal ok_all
        ok_all &= bool(cond)
        print(f"  {name}: {'PASS' if cond else 'FAIL'}")

    t0 = dt.datetime(2024, 7, 31, 12)
    rows = {}

    def put(c, L, period, status="scored", raw=10.0, base=10.5, cur=11.0):
        rows[(c, L)] = (period, status, c + dt.timedelta(hours=L), repr(raw), repr(base), repr(cur))

    # cycles 12z and 18z of 2024-07-31 in period P1; 00z of 2024-08-01 in P2 (a period boundary); 06z missing.
    for L in range(3, 49):
        put(t0, L, "P1", raw=10.0 + L / 10)
        put(t0 + STEP, L, "P1", raw=10.5 + L / 10)
        put(t0 + 2 * STEP, L, "P2", raw=11.0 + L / 10)
    del rows[(t0 + STEP, 30)]                                   # a missing next row for (t0, 36)
    put(t0 + STEP, 31, "P1", status="incomplete")               # next row not in (a) for (t0, 37)
    pairs, cnt = pair_rows(rows)
    keys = {(p[0], p[1]) for p in pairs}
    check("pairing across cycles: (t0, 9) pairs with (t0 + 6 h, 3)", (t0, 9) in keys)
    check("leads 3 to 8 never pair, counted", cnt[REASONS[0]] == 3 * 6 - 0 and not any(L < 9 for _, L in keys))
    check("a missing next row does not pair, counted", (t0, 36) not in keys and cnt[REASONS[2]] == 1)
    check("a next row not in (a) does not pair, counted", (t0, 37) not in keys and cnt[REASONS[3]] == 1)
    check("across a period boundary nothing pairs, counted", not any(p[0] == t0 + STEP for p in pairs)
          and cnt[REASONS[4]] == 40 - 2)                        # leads 30 and 31 at t0 + 6 h are not in (a)
    check("the last cycle has no next cycle, counted", cnt[REASONS[1]] == 40)
    p = next(x for x in pairs if x[0] == t0 and x[1] == 20)
    check("r = raw next - raw (same valid time)", abs((p[6] - p[3]) - ((10.5 + 1.4) - (10.0 + 2.0))) < 1e-12)
    check("counts add up", cnt["rows in (a)"] == cnt["paired"] + sum(cnt[k] for k in REASONS))

    # sign share with zeros
    X = dict(k=np.array([1.0, -1.0, 0.0, 2.0, -2.0, 0.5]), r=np.array([2.0, -0.5, 1.0, 0.0, 1.0, 0.25]))
    X["kb"], X["b"] = X["k"] * 0.5, X["k"] * 0.5
    S = StatSet(X, np.ones(6, dtype=bool))
    st = S.stats(np.ones(6))
    c = S.counts()
    check("sign share over pairs with both non-zero (3 of 4)", abs(st["sign_share"] - 0.75) < 1e-12)
    check("zero counts (k 1, r 1, both non-zero 4)", c["k_zero"] == 1 and c["r_zero"] == 1 and c["both_nonzero"] == 4)

    # weighted Spearman = Spearman of the expanded data (ties included); point Spearman = scipy's
    from scipy.stats import pearsonr, spearmanr
    rng = np.random.default_rng(0)
    x = np.round(rng.normal(size=200), 1)
    y = np.round(x + rng.normal(size=200), 1)
    w = rng.integers(0, 4, size=200).astype(float)
    rk = Ranker(x)
    a = wcorr(rk.ranks(w), Ranker(y).ranks(w), w)
    rep = np.repeat(np.arange(200), w.astype(int))
    check("weighted Spearman equals Spearman of the expanded rows", abs(a - spearmanr(x[rep], y[rep])[0]) < 1e-12)
    check("Spearman with unit weights equals scipy's", abs(wcorr(rk.ranks(np.ones(200)), Ranker(y).ranks(np.ones(200)),
                                                                 np.ones(200)) - spearmanr(x, y)[0]) < 1e-12)
    check("Pearson equals scipy's", abs(wcorr(x, y, np.ones(200)) - pearsonr(x, y)[0]) < 1e-12)
    sl = np.polyfit(x, y, 1)
    X2 = dict(k=x, r=y, kb=x, b=y)
    st2 = StatSet(X2, np.ones(200, dtype=bool)).stats(np.ones(200))
    check("OLS slope and intercept equal numpy.polyfit's", abs(st2["ols_slope"] - sl[0]) < 1e-10
          and abs(st2["ols_intercept"] - sl[1]) < 1e-10)

    # the bootstrap's blocks: all pairs of one date move together, as often as the date is drawn
    dates = np.array(["2024-01-01"] * 3 + ["2024-01-02"] * 2 + ["2024-01-03"] * 4, dtype="datetime64[D]")
    u, idx = np.unique(dates, return_inverse=True)
    g = np.random.default_rng(5)
    ok_b = True
    for wv in block_weights(g, idx, len(u), 50):
        per_date = [set(wv[idx == d]) for d in range(len(u))]
        ok_b &= all(len(s) == 1 for s in per_date)
        ok_b &= sum(next(iter(s)) for s in per_date) == len(u)
    check("bootstrap blocks: one weight per date, the dates drawn sum to the number of dates", ok_b)
    g1, g2 = np.random.default_rng(132), np.random.default_rng(132)
    w1 = list(block_weights(g1, idx, len(u), 5))
    d2 = g2.integers(0, len(u), size=(5, len(u)))
    check("bootstrap draws are the generator's integers in order", all(
        np.array_equal(w1[j], np.bincount(d2[j], minlength=len(u))[idx]) for j in range(5)))
    print("CHECK: PASS" if ok_all else "CHECK: FAIL")
    return 0 if ok_all else 1


# ------------------------------------------------------------------ --pairs

PAIR_COLS = ["icao", "group", "rows_read", "rows_not_in_a", "rows_in_a", "paired"] + [
    "lead_3_to_8", "no_next_cycle", "next_row_not_in_file", "next_row_not_in_a", "different_period"]


def group_of(ic):
    return "claim" if AIRPORTS.index(ic) < 6 else "dev"


def check_inputs():
    m = meta_sha256()
    if m != PRED_SHA256:
        raise SystemExit("STOP: meta.txt's SHA-256 are not the ones held here")


def run_pairs(args):
    check_inputs()
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"SESSION 132 --pairs (counts only, no statistic), {now_utc()}")
    rows_out = []
    for ic in AIRPORTS:
        _, cnt = pair_rows(read_rows(ic))
        rows_out.append([ic, group_of(ic), cnt["rows read"], cnt["rows not in (a)"], cnt["rows in (a)"], cnt["paired"]]
                        + [cnt[k] for k in REASONS])
        print(f"  {ic}: rows {cnt['rows read']:,}, not in (a) {cnt['rows not in (a)']}, in (a) {cnt['rows in (a)']:,}, "
              f"paired {cnt['paired']:,}; not paired: " + ", ".join(f"{k} {cnt[k]:,}" for k in REASONS))
    h = write_once(OUT / "pair_counts.csv", csv_bytes(PAIR_COLS, rows_out))
    print(f"  pair_counts.csv: {len(rows_out)} rows, SHA-256 {h}")
    return 0


# ------------------------------------------------------------------ --stats

STAT_COLS = (["icao", "group", "set", "n", "k_zero", "r_zero", "both_nonzero", "dates"]
             + [c for s in STATS for c in (s, s + "_lo", s + "_hi")])
BRK_COLS = ["icao", "group", "breakdown", "bin", "edges", "n", "k_zero", "r_zero", "both_nonzero"] + STATS


def run_stats(args):
    check_inputs()
    if not (OUT / "pair_counts.csv").exists():
        raise SystemExit("STOP: run --pairs first")
    t0 = time.time()
    start = now_utc()
    print(f"SESSION 132 --stats (D127.6; descriptive, D107.2), {start}; python {sys.version.split()[0]}; numpy "
          f"{np.__version__}; seed {SEED}, {REPS} resamples")
    rng = np.random.default_rng(SEED)
    srows, brows, head = [], [], []
    for ic in AIRPORTS:
        pairs, _ = pair_rows(read_rows(ic))
        X = arrays(pairs)
        grp = group_of(ic)
        present = set(X["period"])
        if not present <= set(PERIODS[grp]):
            raise SystemExit(f"STOP: {ic}: periods {sorted(present)}")
        for setname in ["pooled"] + [p for p in PERIODS[grp] if p in present]:
            m = np.ones(len(X["k"]), dtype=bool) if setname == "pooled" else (X["period"] == setname)
            S = StatSet(X, m)
            pt = S.stats(np.ones(int(m.sum())))
            ci, nd = bootstrap(rng, S, X["date"][m])
            cn = S.counts()
            srows.append([ic, grp, setname, cn["n"], cn["k_zero"], cn["r_zero"], cn["both_nonzero"], nd]
                         + [v for s in STATS for v in (pt[s], ci[s][0], ci[s][1])])
            if setname == "pooled":
                head.append((ic, cn["n"], pt, ci))
        # breakdowns, point values only, pooled over periods
        ak = np.abs(X["k"])
        e1, e2 = (float(v) for v in np.quantile(ak, [1 / 3, 2 / 3]))
        bins = [("lead_at_c", "9-24", "", (X["lead"] >= 9) & (X["lead"] <= 24)),
                ("lead_at_c", "25-48", "", (X["lead"] >= 25) & (X["lead"] <= 48))]
        bins += [("cycle_hour", f"{h:02d}z", "", X["ch"] == h) for h in (0, 6, 12, 18)]
        bins += [("abs_k_tercile", "1", f"|k| <= {e1!r}", ak <= e1),
                 ("abs_k_tercile", "2", f"{e1!r} < |k| <= {e2!r}", (ak > e1) & (ak <= e2)),
                 ("abs_k_tercile", "3", f"|k| > {e2!r}", ak > e2)]
        for brk, b, edges, m in bins:
            if not m.any():
                continue
            S = StatSet(X, m)
            pt = S.stats(np.ones(int(m.sum())))
            cn = S.counts()
            brows.append([ic, grp, brk, b, edges, cn["n"], cn["k_zero"], cn["r_zero"], cn["both_nonzero"]]
                         + [pt[s] for s in STATS])
        n, pt, ci = head[-1][1], head[-1][2], head[-1][3]
        lo, hi = ci["spearman_k_r"]
        print(f"  {ic:4s} n {n:7,d}  Spearman k,r {pt['spearman_k_r']:+.3f} [{lo:+.3f}, {hi:+.3f}]  slope "
              f"{pt['ols_slope']:+.3f}  sign share {pt['sign_share']:.3f}  mean |r| {pt['mean_abs_r']:.3f}  mean |r - k| "
              f"{pt['mean_abs_r_minus_k']:.3f} (ratio {pt['ratio']:.3f})  ({time.time() - t0:.0f} s)")
    above = [ic for ic, _, _, ci in head if ci["spearman_k_r"][0] > 0]
    below = [ic for ic, _, _, ci in head if ci["spearman_k_r"][1] < 0]
    print(f"D127.6(g): Spearman's interval wholly above 0 at {len(above)} of 12"
          + (f" ({', '.join(above)})" if above else "") + f"; 'most airports' is at least 7 of 12: "
          + ("met" if len(above) >= 7 else "not met") + f". Wholly below 0 at {len(below)} of 12"
          + (f" ({', '.join(below)})" if below else "") + " (described only).")
    files = {}
    files["stats.csv"] = (len(srows), write_once(OUT / "stats.csv", csv_bytes(STAT_COLS, srows)))
    files["breakdowns.csv"] = (len(brows), write_once(OUT / "breakdowns.csv", csv_bytes(BRK_COLS, brows)))
    pc = (OUT / "pair_counts.csv").read_bytes()
    files["pair_counts.csv"] = (pc.count(b"\n") - 1, sha256_bytes(pc))
    meta = ["Session 132 D115.6's question (D127.6), written by scripts/session132_revision.py (--pairs, --stats).",
            f"stats run {start}; run time {time.time() - t0:.0f} s; python {sys.version.split()[0]}; numpy "
            f"{np.__version__}; seed {SEED}; {REPS} resamples",
            f"script SHA-256 {sha256_bytes(Path(__file__).read_bytes())}",
            "inputs: ../MLwx-stagec/analysis112/pred_<ICAO>.csv.gz, each equal to meta.txt's SHA-256; no observation "
            "used; nothing valid after 2026-07-31T23:00 UTC.",
            "k = curve - raw_gfs; r = raw_gfs(c + 6 h) - raw_gfs(c); k_base = baseline - raw_gfs; b = curve - baseline.",
            "ratio = mean_abs_r_minus_k / mean_abs_r; _lo and _hi: 95 % percentile block bootstrap over cycle UTC "
            "dates.",
            f"D127.6(g): Spearman k,r interval wholly above 0 at {len(above)} of 12 ({', '.join(above) or 'none'}).",
            "files:"]
    for n, (rows_n, h) in files.items():
        meta.append(f"  {n}  rows {rows_n}  sha256 {h}")
    write_once(OUT / "meta.txt", ("\n".join(meta) + "\n").encode())
    for n, (rows_n, h) in files.items():
        print(f"  {n}: {rows_n} rows, SHA-256 {h}")
    print(f"--stats: done ({time.time() - t0:.0f} s)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = ap.add_mutually_exclusive_group(required=True)
    for m in ("check", "pairs", "stats"):
        g.add_argument(f"--{m}", action="store_true")
    a = ap.parse_args()
    if a.check:
        return run_check(a)
    if a.pairs:
        return run_pairs(a)
    return run_stats(a)


if __name__ == "__main__":
    sys.exit(main())
