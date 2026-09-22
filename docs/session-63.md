# Session 63 — the reserved-year feature build (closes D58 item 11)

## What this session is

This is an **outcome-orthogonal data build**. Its only job is to produce
real `L`, `D`, `T`, `R` feature values for the **reserved year**
(2024-08-01 to 2025-07-31), so that session 64 can run the already-frozen
confirmation script once on that year. It reuses the already-frozen
pull / decode / derive / join code from sessions 49, 51, 53 and 55,
unchanged, and only runs it over the reserved year's dates instead of
excluding them.

**No model is fit. No MAE, skill, or CV is computed. Nothing is scored,
selected, tuned, or ranked. `run_confirm()` is never called.** The single
authorized look at the reserved year (D51) is session 64's job, not this
session's.

Why touching the reserved year is allowed here, when D51 otherwise forbids
it (this is the exact reasoning in D58 item 11, and it is not a loosening of
D51): pulling raw GRIB data for the reserved year's dates, applying only the
already-pinned transforms, is **not** a feature experiment. No model is fit,
no result is read, nothing is selected on it. And the final feature set is
already **locked** (D58: B + D, L, R, T), so there is no selection left that
could be biased by seeing this data. This is a data-engineering prerequisite
the feature-selection programme's own design did not anticipate needing,
because every session before this one only ever needed the reserved year
**excluded**, never **included**.

---

## Background you need (self-contained — do not rely on memory)

**The gap being closed (D58 item 11).** The four adopted families were each
built with the reserved year deliberately excluded (sessions 49/51/53/55,
under D51's rule at the time). Every one of their eight committed files
(`v16_window` + `sealed_window` per family) has **zero rows** inside
2024-08-01..2025-07-31. The frozen confirmation script's fold is:

```
train  2021-03-24 .. 2024-07-31
test   2024-08-01 .. 2025-07-31   (the reserved year — session 64's one look)
```

The **training** window is already fully covered by the existing family
files. The **test** window (the reserved year itself) currently has no L, D,
T, or R value at any airport, for any date. `run_confirm()` has a hard guard
that stops with a clear error rather than score on missing data, so it
cannot run until this gap is closed. This session closes it.

**The base 5-feature dataset already covers the reserved year.** The base
GRIB feature files `data/processed/grib_features_v16_window.csv` (span
2021-03-24..2025-07-31) and `grib_features_sealed_window.csv` already carry
the base features **B** (`temperature_grib_c`, `cloud_cover_grib_pct`,
`wind_speed_grib_kmh`, `season_sin`, `season_cos`) for the reserved year's
rows — the reserved year is simply the portion of `v16_window` from
2024-08-01 onward. So **B is not rebuilt this session.** Only L, D, T, R are
missing for the reserved year, and only those four are built.

**The four families, their committed columns, source files, and the pinned
transform (from D58's own resolution table). Do not change any of this:**

| code | family | derived/committed column | build session / script | transform |
|---|---|---|---|---|
| L | upper-air / lapse rate | `lapse_rate_t2_t850` | 49 / `scripts/session49_upper_air_pull.py` | none |
| D | moisture | `dewpoint_depression_t2m` | 51 / (moisture build script) | **none in the build** — store the raw column; D53/F100's floor `max(x,0)` is applied downstream by the confirmation script, not here |
| T | pressure / synoptic | `pressure_tendency_3h_hpa` | 53 / (pressure build script) | none |
| R | radiation | `dswrf_2h_wm2` | 55 / `scripts/session55_radiation_pull.py` | none |

The existing family output files follow the pattern
`sessionNN_v16_window_with_<family>.csv` and
`sessionNN_sealed_window_with_<family>.csv` (e.g.
`session49_v16_window_with_upper_air.csv`,
`session55_v16_window_with_radiation.csv`). Locate the exact moisture (51)
and pressure (53) script and file names in the repo — do not assume them.

**Reuse the frozen code, do not re-implement it.** Each of sessions
49/51/53/55 pinned real decisions inside its own build (e.g. session 49
recovers `t2m_raw` algebraically as `temperature_grib_c - correction_c`
using each airport's fixed D48.3/F90 constant and applies no
elevation/lapse correction to the pressure-level temps; session 55 resolves
DSWRF to a common 2-hour window ending at each airport's target hour, with
energy subtraction for the lead-24 airports EGLC/LFPG/DSM). **Reuse those
frozen functions by import, feeding them the reserved-year date list — do
not copy, re-derive, or re-decide any window, constant, or formula.** The
whole point is that the reserved year's features are produced by
byte-identical code to the training and sealed windows.

---

## Steps

### Step 0 — read first, decide the output target

Read `scripts/session62_reserved_confirm.py` and determine **exactly how
`run_confirm()` locates and loads the reserved-year (test-window) feature
values** for each of D, L, R, T. Record, per family, the file path and
column format it expects. One of three cases holds:

- **(a) The script already references a per-family reserved-year source file
  (a path, constant, or naming convention) that simply does not exist yet.**
  Then produce **exactly those files, in exactly that format and column
  layout.** No edit to the frozen script. This is the expected case, and it
  keeps session 64's promise that the confirmation runs *unchanged*.
- **(b) The script builds test-window features by filtering the existing
  `v16_window`/`sealed_window` family files to the reserved-year dates**
  (which yields zero rows). Then a **one-line source-path addition** is
  needed so the script can see the new reserved-year files. This is an
  outcome-orthogonal wiring change — it affects only which rows load, before
  any model is fit, the same class of change as the F92/F93 pre-look guard
  fix. If this case holds: make that change **minimally**, document it in
  full in the finding, **but still stop before any `run_confirm()` call** —
  session 64 takes the look. Flag it prominently for owner review.
- **(c) Anything unclear, or neither of the above.** **Stop and flag it**
  (CLAUDE.md: stop and report rather than silently resolve). Do not guess.

If the file paths are left to convention (case a with no fixed name), use
this naming, mirroring the existing pattern:
`data/processed/session63_reserved_window_with_upper_air.csv`,
`..._with_moisture.csv`, `..._with_pressure.csv`, `..._with_radiation.csv`,
plus per-family `session63_<family>_join_drops.csv` and manifests under
`data/raw/diagnostics/session63/`.

### Step 1 — build the reserved-year date list from the base dataset

Build the date list from the base dataset's own reserved-year rows: filter
`data/processed/grib_features_v16_window.csv` to `target_date` in
2024-08-01..2025-07-31, per airport. **Do not assume a continuous
calendar** — use the base file's real dates, exactly as sessions 49/51/53/55
built their lists from the base file (this preserves the per-airport
idx-mismatch day pattern, F90, so the later join is exact). Record the exact
per-airport reserved-year date count and report it.

### Step 2 — invert the reserved-year guard

Sessions 49/51/53/55 called `assert_reserved_year_excluded()` to confirm
their pulls **excluded** the reserved year. This session is the opposite:
every date must be **inside** 2024-08-01..2025-07-31. **Do not run the
exclusion guard on these dates — it would raise on every one.** Instead
assert the inverse before any pull: every date in the list is inside the
reserved year, and none is outside it. Print the check result. (Leave
`scripts/session48_reserved_year.py` and its `RESERVED_YEAR_START/END`
constants untouched — read them, do not edit them.)

### Step 3 — run the four frozen pipelines over the reserved year

For each family L, D, T, R: import and run the frozen pull / decode / derive
/ join functions from that family's build script (sessions 49/51/53/55),
over the reserved-year date list, joining onto the base dataset's
reserved-year rows. Follow the same operational discipline those sessions
used:

- **Fetch-decode-discard** — no raw GRIB2 bytes kept on disk (disk is
  tight). Write a per-family pull manifest (run_date, cycle, lead, level/
  field, stations, status, detail — no bytes) under
  `data/raw/diagnostics/session63/`, recording pull date and the exact
  query, as the provenance record (SPEC 2.3, D47).
- **Raw data immutable** (SPEC 2.3) — do not modify the base dataset or any
  existing committed family file. Write only new reserved-year outputs.
- **Never silently fill gaps** (SPEC 2.2) — if any forecast/observation is
  missing so a row cannot be formed, drop it, count it, report it. Do not
  interpolate or invent.
- **D: store the raw `dewpoint_depression_t2m` column** (the floor is a
  downstream step in the confirmation script — do not apply it here).
- **R: reuse session 55's frozen window-resolution / de-accumulation logic
  unchanged** (2-hour window ending at each airport's target hour; energy
  subtraction for EGLC/LFPG/DSM). Do not re-resolve or re-check windows.

### Step 4 — verify (mirror the original builds' own checks)

Report **real numbers**, not descriptions:

- **Join drops: expect 0** at every airport, every family (the
  `session63_<family>_join_drops.csv` logs empty).
- **Row counts:** per airport, per family, the reserved-year output row
  count **equals the base dataset's own reserved-year row count** (derive
  both and show they match). Report the exact counts.
- **Nulls: expect 0** in each derived/committed column at every airport.
- **Manifests: expect 0 FAIL rows**; report per-field decoded_ok / requested
  counts.
- **Spot-check** one or two decoded values per family for physical
  plausibility (e.g. a lapse rate colder with height where expected; note
  that RNO's upper-air ordering inverts for a real elevation reason, F98 —
  not a defect).

### Step 5 — confirm the test-window B matrix is complete (read-only)

A quick, read-only safety check that de-risks session 64: confirm the base
dataset's reserved-year rows carry complete, **non-null** B features
(`temperature_grib_c`, `cloud_cover_grib_pct`, `wind_speed_grib_kmh`,
`season_sin`, `season_cos`) at every airport. Report the null counts (expect
all zero). **No model, no score — a column read only.** If any B column has
nulls in the reserved year, stop and flag it (it would block session 64).

---

## End-of-session steps

1. Paste the **real output** — actual numbers from Steps 1–5, not a summary
   of them.
2. **Append a DECISIONS.md finding, F107**, recording: the reserved year was
   opened **for data only** (no fit, no score, no selection); the four
   reserved-year family files produced, with their exact row counts, zero
   join drops, zero nulls, and manifest results; that D58 item 11's gap is
   now closed; and — if Step 0 case (b) held — the exact one-line wiring
   change made to `scripts/session62_reserved_confirm.py` and why it is
   outcome-orthogonal and pre-look. State plainly what was **not** done: no
   model fit, no MAE/skill/CV anywhere, `run_confirm()` never called, the
   sealed year (F94) never touched, no existing frozen file rewritten, no
   P / rh / plev built, no per-airport anything, SPEC/RESULTS untouched.
3. **Overwrite STATUS.md** — **prune it to a current-only snapshot** (present
   state, immediate next action, live open questions only; do **not** append
   this session's write-up to a log — its history lives in git and
   DECISIONS). Its **"Next planning session" line must name session 64**: run
   `scripts/session62_reserved_confirm.py --confirm` once, unchanged, on the
   2024-25 fold — the single authorized look (D51) — and report the verdict
   against D58's pre-registered expectations (bar: B+D,L,R,T beats both raw
   GFS and persistence at all five airports; secondary: beats plain B on
   airport-averaged MAE).
4. **Consistency check** — re-read SPEC / STATUS / DECISIONS, report any
   disagreement, duplicated heading, or out-of-order entry. Report only; do
   not fix silently.
5. **Archive step** — apply the archive criterion. D52–D58 and F106 remain
   **live** (still load-bearing for session 64's confirmation), so they are
   **not** archived. If nothing qualifies, say so.
6. **Do not modify SPEC.md or RESULTS.md.**
7. **Do not commit anything.** Prepare changes, write out a suggested commit
   message, and stop for review.

---

## Scope guard — what this session must NOT do

- **No model fit, no MAE, skill, or CV, anywhere.** This is data only.
- **Never call `run_confirm()`** or run the confirmation. Session 64 owns the
  one look.
- **Do not touch the sealed year** (2025-08-01..2026-07-31, F94) in any way.
- **Do not rewrite, append to, or re-decode any existing committed file** —
  the base dataset, or any `v16_window`/`sealed_window` family file. Produce
  only new reserved-year outputs.
- **Do not build P (precipitation), rh, or plev** — D58 dropped/parked all
  three. L, D, T, R only.
- **No per-airport feature selection or per-airport variation** — identical
  handling at all five airports.
- **Do not re-resolve, re-decide, or re-derive any pinned window, constant,
  or transform** — reuse the frozen 49/51/53/55 code as-is.
- **Do not edit `scripts/session48_reserved_year.py`** or its reserved-year
  constants. The only frozen-script edit permitted is the minimal Step 0
  case-(b) wiring pointer, if and only if that case holds, documented, and
  still stopping before any confirmation run.
