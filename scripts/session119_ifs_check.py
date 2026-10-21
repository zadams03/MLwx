#!/usr/bin/env python3
"""Session 119: is IFS's cold error a reading fault? (D113.6, descriptive, D107.2.)

Modes, run in this order:
  --gate     Step 2. Builds IFS's hourly rows with and without the elevation treatment (D108.3), raw GFS's and
             AIFS's on the same rows, and the observations, by session 114's loaders (imported read-only). Gate:
             per airport and test year, IFS's n, MAE and mean error equal the committed
             data/processed/session114_comparisons/hourly_ifs.csv exactly; row counts equal F160.3's.
  --decode   Step 3 (network: byte-range fetches from ifs_manifest.csv.gz's URLs only, at most 24 messages).
             T5 (D113.6(e)).
  --tests    Step 4. T1 to T4 (D113.6(a) to (d)).

Every rule below was fixed in this file before any T1 to T5 value was computed. Where D113.6 leaves a detail
open, the choice is written here and reported to the owner as a session choice:

  Rows. "F160.4's rows": the curve's scored rows (session 112's loader) where IFS, read as D108.3 (positions set
    of D108.3, elevation treatment where IFS terrain exists), has a value. Mean error e = observation minus
    forecast (positive is cold). Raw GFS is the loader's raw_gfs (elevation-adjusted, SPEC 5.2). AIFS (from
    2025-02-25T06Z) on the subset of those rows where it has a value.
  T1 (a). (i) IFS's mean error without the treatment on the same rows: |ME| <= 0.2 C at >= 7 of 12.
    (ii) Spearman's rho across the 12 airports between IFS's mean error (with treatment) and its mean elevation
    adjustment over the same rows (0 C on rows with no treatment): |rho| >= 0.7. (iii) IFS terrain height,
    interpolated with the same four weights, against GFS's terrain height at the same position (the record's
    value for the position D108.3 uses; at the development airports' iem set, session90_airports.csv's
    model_height_m where a row exists, else "not recorded"): any |difference| > 300 m.
  T2 (b). Development airports. Rows: F160.4's rows where IFS at the iem set (same treatment, same station
    elevation) also has a value. Mark at an airport: |ME gfs set| - |ME iem set| >= 0.3 C. Shown at >= 4 of 6.
  T3 (c). Shift rows: F160.4's rows whose observations at v - 3 h and v + 3 h both exist and are valid at or
    before 2026-07-31T23:00 UTC. MAE(0), MAE(+3) (observation at v + 3 h), MAE(-3), all on these rows. Mark
    part 1: MAE(+3) < MAE(0) at >= 7 of 12, or MAE(-3) < MAE(0) at >= 7 of 12. Trend rows: F160.4's rows with
    observations at v - 1 h and v + 1 h (same limit); trend = (obs(v+1) - obs(v-1)) / 2 C per hour; slope =
    ordinary least squares of e on trend with an intercept. Mark part 2: |slope IFS| >= 2 |slope raw GFS| on
    the same rows at >= 7 of 12. Raw GFS on the same rows; AIFS on the AIFS subset (with IFS and raw GFS
    rescored on that subset beside it). Mean error by local hour: no mark.
  T4 (d). Window: 20 days of cycles on each side of a date B ([B - 20 d, B) and [B, B + 20 d), by cycle time
    UTC; 20 days is the gap from the 49r1 date to the 2024-12-03 boundary, so no window crosses another date).
    step = ME(after) - ME(before), IFS with treatment, F160.4's rows. Calendar control: the same calendar
    date in each other test year where the airport has rows on both sides; adjusted step = step - mean of
    those. An airport with no control year, or no rows on one side of B, is not counted. Reading boundaries
    2024-02-01 (development airports only, so 4 of 6) and 2024-12-03 (7 of 12, or of those with data).
    Model-version dates 2024-11-13 (49r1) and 2026-05-13 (50r1). Mark: |adjusted step| >= 0.5 C at "most
    airports" at a reading boundary, and at no version date at "most airports". The count of airports with
    a step of that size at each version date is also printed, so the owner can read "no step" literally.
  T5 (e). For each grid label: the 2t message at step 24 of the 00z cycle on the first, middle (index
    (n - 1) // 2 of the sorted dates) and last date with any message on that label. Checks: bytes' SHA-256
    against the manifest; shortName 2t, units K, dataDate and dataTime the cycle, step 24 (endStep), the grid
    label recomputed by session 113's grid_label; the four values at each airport and position set from the
    positions file, bit-equal (float64) to every stored row of that message. A fetch that fails twice is
    counted. Bytes are written under /tmp/session119_ifs_grib/ and deleted at the end.

Nothing valid after 2026-07-31T23:00 UTC, no 2026-27 file, MLwx-live and none of the 37 airports of F153.6 is
read. Scripts imported read-only, never edited. No em-dashes in any text here (D76.6).
"""

import sys

sys.dont_write_bytecode = True

import argparse  # noqa: E402
import csv  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import shutil  # noqa: E402
import struct  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import session114_comparisons as s114  # noqa: E402

import numpy as np  # noqa: E402
from scipy.stats import spearmanr  # noqa: E402

s112, s113 = s114.s112, s114.s113
h_of, dt_of = s114.h_of, s114.dt_of

OUT = ROOT / "data" / "processed" / "session119_ifs"
GRIB_TMP = Path("/tmp/session119_ifs_grib")
LIMIT_H = h_of(s114.LIMIT)
AIRPORTS = s114.AIRPORTS
GROUP = s114.GROUP
DEV = [ic for ic in AIRPORTS if GROUP[ic] == "dev"]
MOST, MOST_DEV = 7, 4                                       # D113.6
F160_3 = {"claim": (46568, 46656), "dev": (69520, 70016)}   # paired hourly rows, F160.3
T4_WINDOW_D = 20
READING_DATES = [("2024-02-01", "grid change"), ("2024-12-03", "own terrain")]
VERSION_DATES = [("2024-11-13", "49r1"), ("2026-05-13", "50r1")]
TEST_YEARS = ("2023-24", "2024-25", "2025-26")


def write(name, header, rows):
    OUT.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(["" if v is None else (s112.fmt(s112.plain(v)) if not isinstance(v, str) else v) for v in r])
    data = buf.getvalue().encode()
    (OUT / name).write_bytes(data)
    print(f"  wrote {name}: {len(rows)} rows, SHA-256 {hashlib.sha256(data).hexdigest()}")


# ------------------------------------------------------------------ IFS read both ways (D108.3)

class IFS:
    """IFS 2t at one airport and position set: with[(c_h, v_h)] (as D108.3, equal to session 114's Comp),
    without[(c_h, v_h)] (no elevation treatment), adj[(c_h, v_h)] (the correction added, 0 if none),
    grid[(c_h, v_h)], and terrain[grid] = interpolated IFS terrain height (m)."""

    def __init__(self, ic, pset):
        self.ic, self.pset = ic, pset
        self.with_, self.without, self.adj, self.grid, self.terrain = {}, {}, {}, {}, {}
        stn = s114.station_elevations()[ic]["station_m"]
        terr = {}
        for r in s114.read_s113_dicts("ifs_terrain.csv", lambda d: d["airport"] == ic and d["position_set"] == pset):
            if r["h1_m"] != "":
                terr[r["grid"]] = [float(r[f"h{k}_m"]) for k in range(1, 5)]
        head, rows = s114.read_s113(f"ifs_{ic}.csv.gz")
        col = {c: i for i, c in enumerate(head)}
        pos, corr = {}, {}
        for r in rows:
            if r[col["position_set"]] != pset or r[col["param"]] != "2t":
                continue
            g = r[col["grid"]]
            if g not in pos:
                pr = s114.read_s113_dicts(f"positions_{g}.csv", lambda d: d["airport"] == ic and d["position_set"] == pset)
                pos[g] = np.array([float(pr[0][f"p{k}_weight"]) for k in range(1, 5)])
                if g in terr:
                    hz = float(pos[g] @ np.array(terr[g]))
                    self.terrain[g] = hz
                    corr[g] = s114.elevation_correction(hz, stn)
            v = np.array([float(r[col[f"v{k}"]]) for k in range(1, 5)])
            if not np.all(np.isfinite(v)):
                continue
            c_h = h_of(s114.ptime(r[col["cycle"]]))
            v_h = h_of(s113.guard_valid(s114.ptime(r[col["valid_utc"]])))
            raw = float(pos[g] @ v) - 273.15
            val = raw
            if g in corr:
                val += corr[g]
            self.with_[(c_h, v_h)] = val
            self.without[(c_h, v_h)] = raw
            self.adj[(c_h, v_h)] = corr.get(g, 0.0)
            self.grid[(c_h, v_h)] = g


def on_rows(A, d):
    """d[(cycle, valid)] on every row of A (nan where none)."""
    return np.array([d.get((int(c), int(v)), np.nan) for c, v in zip(A["cycle"], A["valid"])])


class Site:
    """Everything one airport needs: our rows, IFS both ways, raw GFS, AIFS, observations."""

    def __init__(self, ic):
        self.ic = ic
        ours = s114.Ours(ic)
        A = ours.A
        comp = s114.Comp("ifs", ic)
        val, _, _ = s114.pair_hourly("ifs", ours, comp)
        ifs = IFS(ic, s114.SET[ic])
        if set(ifs.with_) != set(comp.hv) or any(ifs.with_[k] != comp.hv[k] for k in comp.hv):
            raise SystemExit(f"STOP: {ic}: IFS with treatment differs from session 114's Comp")
        P = A["scored"] & np.isfinite(val)
        ix = np.nonzero(P)[0]
        self.n_all = len(ix)
        self.cyc, self.valid = A["cycle"][ix].astype(np.int64), A["valid"][ix].astype(np.int64)
        self.obs = A["obs"][ix]
        self.ty = np.array([s114.TEST_YEAR[p] for p in A["period"][ix]])
        self.lhour = A["lhour"][ix]
        sub = {k: A[k][ix] for k in ("cycle", "valid")}
        self.ifs = val[ix]
        if not np.array_equal(on_rows(sub, ifs.with_), self.ifs):
            raise SystemExit(f"STOP: {ic}: IFS rows differ from pair_hourly's")
        self.ifs_raw = on_rows(sub, ifs.without)
        self.adj = on_rows(sub, ifs.adj)
        self.raw_gfs = A["raw_gfs"][ix]
        self.curve = A["curve"][ix]
        ac = s114.Comp("aifs", ic)
        aval, _, _ = s114.pair_hourly("aifs", ours, ac)
        self.aifs = aval[ix]
        self.terrain = {s114.SET[ic]: ifs.terrain}
        self.ifs_iem = None
        if GROUP[ic] == "dev":
            iem = IFS(ic, "iem")
            self.ifs_iem = on_rows(sub, iem.with_)
            self.terrain["iem"] = iem.terrain
        self.obs_d = {}
        for t, o in ours.obs.items():
            h = h_of(t)
            if h <= LIMIT_H and o is not None:
                self.obs_d[h] = o
        for i in range(len(ix)):
            if self.obs_d.get(int(self.valid[i])) != self.obs[i]:
                raise SystemExit(f"STOP: {ic}: the observation series differs from the row's observation")

    def obs_at(self, hours):
        out = np.full(len(hours), np.nan)
        for i, h in enumerate(hours):
            h = int(h)
            if h > LIMIT_H:
                continue                                     # never read past the limit (counted by the caller)
            o = self.obs_d.get(h)
            if o is not None:
                out[i] = o
        return out


def load_sites():
    t0 = time.time()
    sites = {}
    for ic in AIRPORTS:
        sites[ic] = Site(ic)
        print(f"  loaded {ic}: {sites[ic].n_all:,} IFS rows ({time.time() - t0:.0f} s)")
    return sites


# ------------------------------------------------------------------ Step 2: --gate

def run_gate(args):
    print("SESSION 119 --gate (Step 2)")
    sites = load_sites()
    committed = {(r["icao"], r["test_year"], r["forecast"]): r
                 for r in s114.read_table("hourly_ifs.csv")}
    rows, bad = [], 0
    for ic, S in sites.items():
        E = {"comp": S.obs - S.ifs, "raw_gfs": S.obs - S.raw_gfs, "curve": S.obs - S.curve}
        for ty in TEST_YEARS + ("all",):
            m = np.ones(len(S.obs), bool) if ty == "all" else S.ty == ty
            if not m.any():
                continue
            for f in ("comp", "raw_gfs", "curve"):
                mt = s112.metrics(E[f][m])
                c = committed.get((ic, ty, f))
                got = [str(mt["n"]), s112.fmt(mt["mae"]), s112.fmt(mt["me"])]
                want = [c["n"], c["mae"], c["mean_error"]] if c else [None] * 3
                ok = got == want
                bad += not ok
                rows.append([ic, ty, f, mt["n"], mt["mae"], mt["me"], c["n"] if c else "", c["mae"] if c else "",
                             c["mean_error"] if c else "", "equal" if ok else "DIFFERS"])
    write("gate.csv", ["icao", "test_year", "forecast", "n", "mae", "mean_error", "file_n", "file_mae",
                       "file_mean_error", "result"], rows)
    mc = {}
    with open(ROOT / "data/processed/session117_ifs/match_counts.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["source"] == "ifs" and r["output"] == "hourly" and r["item"] == "paired":
                mc[r["icao"]] = mc.get(r["icao"], 0) + int(r["count"])
    cbad = 0
    for g in ("claim", "dev"):
        ns = [sites[ic].n_all for ic in AIRPORTS if GROUP[ic] == g]
        ok = (min(ns), max(ns)) == F160_3[g]
        cbad += not ok
        print(f"  {g}: rows {min(ns):,} to {max(ns):,}; F160.3 {F160_3[g][0]:,} to {F160_3[g][1]:,}: "
              f"{'equal' if ok else 'DIFFERS'}")
    for ic in AIRPORTS:
        if mc.get(ic) != sites[ic].n_all:
            cbad += 1
            print(f"  {ic}: rows {sites[ic].n_all} against match_counts paired {mc.get(ic)}: DIFFERS")
    sgn = [np.sign(np.mean(sites[ic].obs - sites[ic].ifs)) == np.sign(float(committed[(ic, 'all', 'comp')]['mean_error']))
           for ic in AIRPORTS]
    print(f"  cells compared {len(rows)}, differing {bad}; row counts differing {cbad}; mean error as observation "
          f"minus forecast has the file's sign at {sum(sgn)} of 12")
    ok = bad == 0 and cbad == 0 and all(sgn)
    print(f"--gate: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ------------------------------------------------------------------ Step 3: --decode (T5)

def run_decode(args):
    import eccodes as ec
    print("SESSION 119 --decode (Step 3, T5; network: byte ranges from the manifest)")
    head, man = s114.read_s113("ifs_manifest.csv.gz")
    col = {c: i for i, c in enumerate(head)}
    dates = {}
    for r in man:
        dates.setdefault(r[col["grid"]], set()).add(r[col["cycle"]][:10])
    chosen, short = [], []
    for g in sorted(dates):
        ds = sorted(dates[g])
        pick = sorted({ds[0], ds[(len(ds) - 1) // 2], ds[-1]})
        if len(pick) < 3:
            short.append(f"{g}: {len(ds)} dates, {len(pick)} distinct picks")
        for d in pick:
            hit = [r for r in man if r[col["grid"]] == g and r[col["cycle"]] == f"{d}T00:00Z"
                   and r[col["step"]] == "24" and r[col["param"]] == "2t"]
            if len(hit) != 1:
                short.append(f"{g} {d}: {len(hit)} 2t step-24 00z messages")
                continue
            chosen.append(hit[0])
    if len(chosen) > 24:
        raise SystemExit(f"STOP: {len(chosen)} messages chosen, more than 24 (D113.7)")
    print(f"  chosen {len(chosen)} messages; short: {short or 'none'}")
    stored = {}
    for ic in AIRPORTS:
        h, rows = s114.read_s113(f"ifs_{ic}.csv.gz")
        c = {k: i for i, k in enumerate(h)}
        want = {r[col["msg"]] for r in chosen}
        for r in rows:
            if r[c["msg"]] in want:
                stored.setdefault(r[c["msg"]], []).append((r[c["airport"]], r[c["position_set"]], r[c["grid"]],
                                                           r[c["cycle"]], r[c["step"]], r[c["param"]],
                                                           [r[c[f"v{k}"]] for k in range(1, 5)], r[c["units"]]))
    GRIB_TMP.mkdir(parents=True, exist_ok=True)
    out, failed_fetch, nbad = [], 0, 0
    for r in chosen:
        mid, g, cyc, url = r[col["msg"]], r[col["grid"]], r[col["cycle"]], r[col["url"]]
        a, b = (int(x) for x in r[col["byte_range"]].split("-"))
        s113.guard_valid(s114.ptime(cyc) + dt.timedelta(hours=24))
        data = None
        try:
            data = s113.get(url, byte_range=(a, b), tries=2).content
        except Exception as e:  # noqa: BLE001 - counted, not guessed
            failed_fetch += 1
            out.append([mid, g, cyc, "24", "", "", "", "", "", "", 0, 0, f"fetch failed twice: {e}"])
            print(f"  {mid} {g} {cyc}: fetch failed twice ({e})")
            continue
        path = GRIB_TMP / f"{mid}.grib2"
        path.write_bytes(data)
        sha_ok = hashlib.sha256(data).hexdigest() == r[col["sha256"]]
        gid = ec.codes_new_from_message(data)
        try:
            m = s113.grib_meta(gid)
            vals = ec.codes_get_values(gid)
        finally:
            ec.codes_release(gid)
        cdt = s114.ptime(cyc)
        meta_ok = (m["shortName"] == "2t" and m["units"] == "K" and int(m["dataDate"]) == int(f"{cdt:%Y%m%d}")
                   and int(m["dataTime"]) == 0 and int(m["endStep"]) == 24 and s113.grid_label("ifs", m) == g)
        posr = {(p["airport"], p["position_set"]): [int(p[f"p{k}_index"]) for k in range(1, 5)]
                for p in s114.read_s113_dicts(f"positions_{g}.csv")}
        nrow, nval_ok, why = 0, 0, []
        for (ap, ps, rg, rc, rs, rp, vs, un) in stored.get(mid, []):
            nrow += 1
            if (rg, rc, rs, rp, un) != (g, cyc, "24", "2t", "K"):
                why.append(f"{ap} {ps} row keys")
                continue
            dec = [float(vals[k]) for k in posr[(ap, ps)]]
            same = all(struct.pack("<d", x) == struct.pack("<d", float(y)) for x, y in zip(dec, vs))
            nval_ok += same
            if not same:
                why.append(f"{ap} {ps} values")
        ok = sha_ok and meta_ok and nrow > 0 and nval_ok == nrow
        nbad += not ok
        out.append([mid, g, cyc, "24", r[col["byte_range"]], "equal" if sha_ok else "DIFFERS",
                    f"{m['shortName']} {m['units']} {m['dataDate']} {int(m['dataTime']):04d} {m['endStep']}",
                    s113.grid_label("ifs", m), "equal" if meta_ok else "DIFFERS", len(data), nrow, nval_ok,
                    "PASS" if ok else "FAIL: " + "; ".join(why or ["sha or meta"])])
        print(f"  {mid} {g} {cyc}: sha {'ok' if sha_ok else 'DIFFERS'}, meta {'ok' if meta_ok else 'DIFFERS'}, "
              f"rows {nval_ok}/{nrow} bit-equal: {'PASS' if ok else 'FAIL'}")
    write("t5_decode.csv", ["msg", "grid", "cycle", "step", "byte_range", "sha256", "decoded", "grid_label_decoded",
                            "meta", "bytes", "stored_rows", "rows_bit_equal", "result"], out)
    files = sorted(p.name for p in GRIB_TMP.iterdir())
    shutil.rmtree(GRIB_TMP)
    print(f"  deleted {len(files)} files under {GRIB_TMP}: {', '.join(files)}; exists after: {GRIB_TMP.exists()}")
    print(f"  T5: messages {len(chosen)}, failed fetches {failed_fetch}, failing checks {nbad}; mark "
          f"{'SHOWN' if nbad else 'NOT SHOWN'}" + (" (fetch failures counted, not a mark)" if failed_fetch else ""))
    return 0


# ------------------------------------------------------------------ Step 4: --tests (T1 to T4)

def me(e):
    return float(np.mean(e)) if len(e) else None


def mae(e):
    return float(np.mean(np.abs(e))) if len(e) else None


def slope(e, x):
    X = np.column_stack([np.ones(len(x)), x])
    return float(np.linalg.lstsq(X, e, rcond=None)[0][1])


def gfs_terrain_at(ic, pset, st):
    if pset == s114.SET[ic]:
        return st["terrain_m"], st["source"]
    with open(ROOT / "data/processed/session90_airports.csv", newline="") as f:
        for r in csv.DictReader(f):
            if r["icao"] == ic and r["model_height_m"] != "":
                return float(r["model_height_m"]), "data/processed/session90_airports.csv model_height_m"
    return None, "not recorded"


def t1(sites):
    print("T1 height (D113.6(a))")
    rows, me_w, adj_m = [], [], []
    n_within = 0
    for ic, S in sites.items():
        ew, eo = S.obs - S.ifs, S.obs - S.ifs_raw
        a, b = me(ew), me(eo)
        within = abs(b) <= 0.2
        n_within += within
        me_w.append(a)
        adj_m.append(float(np.mean(S.adj)))
        rows.append([ic, GROUP[ic], len(ew), a, mae(ew), b, mae(eo), float(np.mean(S.adj)),
                     int((S.adj != 0).sum()), "yes" if within else "no"])
    rho = float(spearmanr(me_w, adj_m).statistic)
    write("t1_height.csv", ["icao", "group", "n", "me_with_treatment", "mae_with", "me_without_treatment",
                            "mae_without", "mean_adjustment_c", "rows_treated", "abs_me_without_le_0.2"], rows)
    st = s114.station_elevations()
    trows, nbig = [], 0
    for ic, S in sites.items():
        for pset, tg in S.terrain.items():
            gt, src = gfs_terrain_at(ic, pset, st[ic])
            for g, hz in tg.items():
                d = None if gt is None else hz - gt
                big = d is not None and abs(d) > 300
                nbig += big
                trows.append([ic, pset, g, hz, gt, d, src, "yes" if big else "no"])
    write("t1_terrain.csv", ["icao", "position_set", "grid", "ifs_terrain_m", "gfs_terrain_m", "difference_m",
                             "gfs_terrain_source", "abs_diff_gt_300"], trows)
    shown = n_within >= MOST or abs(rho) >= 0.7 or nbig > 0
    print(f"  (i) |ME without| <= 0.2 at {n_within} of 12 (needs 7); (ii) Spearman rho {rho:+.3f} (needs |rho| >= "
          f"0.7); (iii) terrain differences > 300 m: {nbig} of {sum(r[4] is not None for r in trows)} compared "
          f"({sum(r[4] is None for r in trows)} not recorded); T1 mark {'SHOWN' if shown else 'NOT SHOWN'}")
    return shown


def t2(sites):
    print("T2 position (D113.6(b))")
    rows, n = [], 0
    for ic in DEV:
        S = sites[ic]
        m = np.isfinite(S.ifs_iem)
        a, b = me(S.obs[m] - S.ifs[m]), me(S.obs[m] - S.ifs_iem[m])
        nearer = abs(a) - abs(b)
        hit = nearer >= 0.3
        n += hit
        rows.append([ic, int(m.sum()), a, mae(S.obs[m] - S.ifs[m]), b, mae(S.obs[m] - S.ifs_iem[m]), nearer,
                     "yes" if hit else "no"])
    write("t2_position.csv", ["icao", "n", "me_gfs_set", "mae_gfs_set", "me_iem_set", "mae_iem_set",
                              "abs_me_gfs_minus_abs_me_iem", "nearer_by_ge_0.3"], rows)
    shown = n >= MOST_DEV
    print(f"  iem set at least 0.3 C nearer zero at {n} of 6 (needs 4); T2 mark {'SHOWN' if shown else 'NOT SHOWN'}")
    return shown


def t3(sites):
    print("T3 timing (D113.6(c))")
    rows, lrows = [], []
    n_p3 = n_m3 = n_sl = 0
    for ic, S in sites.items():
        v = S.valid
        o_p3, o_m3 = S.obs_at(v + 3), S.obs_at(v - 3)
        o_p1, o_m1 = S.obs_at(v + 1), S.obs_at(v - 1)
        past = int(((v + 3) > LIMIT_H).sum())
        ms = np.isfinite(o_p3) & np.isfinite(o_m3)
        mt = np.isfinite(o_p1) & np.isfinite(o_m1)
        trend = (o_p1 - o_m1) / 2.0
        fc = {"ifs": S.ifs, "raw_gfs": S.raw_gfs, "aifs": S.aifs}
        sl = {}
        for f, x in fc.items():
            for subset, base in (("ifs rows", np.ones(len(v), bool)), ("aifs rows", np.isfinite(S.aifs))):
                if f == "aifs" and subset == "ifs rows":
                    continue
                m1, m2 = ms & base, mt & base
                e0, ep, em = S.obs[m1] - x[m1], o_p3[m1] - x[m1], o_m3[m1] - x[m1]
                s_ = slope(S.obs[m2] - x[m2], trend[m2]) if m2.sum() > 2 else None
                sl[(f, subset)] = s_
                rows.append([ic, f, subset, int(m1.sum()), mae(e0), mae(ep), mae(em),
                             "yes" if mae(ep) < mae(e0) else "no", "yes" if mae(em) < mae(e0) else "no",
                             int(m2.sum()), s_, past])
        n_p3 += mae(o_p3[ms] - S.ifs[ms]) < mae(S.obs[ms] - S.ifs[ms])
        n_m3 += mae(o_m3[ms] - S.ifs[ms]) < mae(S.obs[ms] - S.ifs[ms])
        n_sl += abs(sl[("ifs", "ifs rows")]) >= 2 * abs(sl[("raw_gfs", "ifs rows")])
        for f, x in fc.items():
            for lh in range(24):
                m = (S.lhour == lh) & np.isfinite(x)
                if m.any():
                    lrows.append([ic, f, lh, int(m.sum()), me(S.obs[m] - x[m]), mae(S.obs[m] - x[m])])
    write("t3_timing.csv", ["icao", "forecast", "row_set", "n_shift", "mae_0", "mae_obs_plus3", "mae_obs_minus3",
                            "plus3_lower", "minus3_lower", "n_trend", "slope_e_on_trend", "rows_with_plus3_after_limit"],
          rows)
    write("t3_local_hour.csv", ["icao", "forecast", "local_hour", "n", "mean_error", "mae"], lrows)
    shown = n_p3 >= MOST or n_m3 >= MOST or n_sl >= MOST
    print(f"  IFS MAE lower with obs +3 h at {n_p3} of 12, with obs -3 h at {n_m3} of 12 (needs 7); |slope IFS| >= "
          f"2 |slope raw GFS| at {n_sl} of 12 (needs 7); T3 mark {'SHOWN' if shown else 'NOT SHOWN'}")
    return shown


def step_at(S, B):
    b = h_of(B)
    w = T4_WINDOW_D * 24
    before = (S.cyc >= b - w) & (S.cyc < b)
    after = (S.cyc >= b) & (S.cyc < b + w)
    if not before.any() or not after.any():
        return None, int(before.sum()), int(after.sum()), None, None
    e = S.obs - S.ifs
    mb, ma = me(e[before]), me(e[after])
    return ma - mb, int(before.sum()), int(after.sum()), mb, ma


def t4(sites):
    print("T4 product changes (D113.6(d))")
    rows, summary = [], {}
    for date, label in READING_DATES + VERSION_DATES:
        B = dt.datetime.strptime(date, "%Y-%m-%d")
        kind = "reading boundary" if (date, label) in READING_DATES else "model version"
        nbig = nbase = 0
        for ic, S in sites.items():
            st, nb, na, mb, ma = step_at(S, B)
            ctrl = []
            for dy in (-2, -1, 1, 2):
                Bo = B.replace(year=B.year + dy)
                so = step_at(S, Bo)
                if so[0] is not None:
                    ctrl.append(so[0])
                    rows.append([ic, date, label, kind, "control", f"{Bo:%Y-%m-%d}", so[1], so[2], so[3], so[4], so[0],
                                 "", ""])
            adj = None if st is None or not ctrl else st - float(np.mean(ctrl))
            big = adj is not None and abs(adj) >= 0.5
            if adj is not None:
                nbase += 1
                nbig += big
            rows.append([ic, date, label, kind, "boundary", date, nb, na, mb, ma, st, adj,
                         "" if adj is None else ("yes" if big else "no")])
        need = MOST_DEV if nbase <= 6 else MOST
        summary[date] = (kind, label, nbig, nbase, need, nbig >= need)
        print(f"  {date} {label} ({kind}): |adjusted step| >= 0.5 at {nbig} of {nbase} airports with data and a "
              f"control (most = {need})")
    write("t4_steps.csv", ["icao", "date", "label", "kind", "role", "date_used", "n_before", "n_after", "me_before",
                           "me_after", "step", "adjusted_step", "abs_adjusted_ge_0.5"], rows)
    reading = any(v[5] for v in summary.values() if v[0] == "reading boundary")
    version_most = any(v[5] for v in summary.values() if v[0] == "model version")
    version_any = any(v[2] > 0 for v in summary.values() if v[0] == "model version")
    shown = reading and not version_most
    print(f"  reading boundary step at most airports: {reading}; version-date step at most airports: "
          f"{version_most} (at any airport: {version_any}); T4 mark {'SHOWN' if shown else 'NOT SHOWN'}"
          + ("" if not reading else f"; under the literal 'no step at any airport' reading: "
             f"{'SHOWN' if not version_any else 'NOT SHOWN'}"))
    return shown


def run_tests(args):
    print("SESSION 119 --tests (Step 4, T1 to T4; descriptive, D107.2)")
    sites = load_sites()
    res = {"T1": t1(sites), "T2": t2(sites), "T3": t3(sites), "T4": t4(sites)}
    print("  marks: " + ", ".join(f"{k} {'SHOWN' if v else 'NOT SHOWN'}" for k, v in res.items()))
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--gate", action="store_true")
    g.add_argument("--decode", action="store_true")
    g.add_argument("--tests", action="store_true")
    a = p.parse_args()
    t0 = time.time()
    rc = run_gate(a) if a.gate else run_decode(a) if a.decode else run_tests(a)
    print(f"done in {time.time() - t0:.0f} s")
    return rc


if __name__ == "__main__":
    sys.exit(main())
