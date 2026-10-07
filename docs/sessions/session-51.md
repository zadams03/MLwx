# Session 51 — record the E1 verdict, then build and validate the E2 moisture feature set (data build only, no modeling)

Read CLAUDE.md, SPEC.md, STATUS.md and the live DECISIONS.md in full first, as
every session does. This prompt is self-contained; where it cites a rule or a
past result by number (Dxx / Fxx / SPEC 7.x), that citation is the authority —
follow it, and if this prompt and a spec file disagree, stop and flag it rather
than guess.

---

## Context (where the programme is)

The feature-selection programme (roadmap: DECISIONS around D51) adds one physical
feature-family at a time onto the frozen 5-feature GRIB baseline (SPEC 7 — the
proven, sealed-tested method), to learn each family's standalone marginal
contribution before any families are combined. Two firm rules govern it:

1. **Each family is tested against the same frozen 5-feature baseline B**
   (`temp`, `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`),
   individually — never against a baseline that has already absorbed an earlier
   family. This keeps every family's number meaning the same thing and free of
   ordering effects. Combining the winners is a separate, later phase.
2. **The reserved year 2024-08-01..2025-07-31 (D51) is never touched** by any
   experiment — no pull, no load, no join, no score — until one single final
   feature set is confirmed on it once, at the very end.
3. **Same features at every airport, always.** No per-airport feature selection.

**E1 (upper-air) is finished and reviewed.** Session 49 built the E1 features
(F98); session 50 fit the four-variant grid (F99); the owner has now made the E1
family verdict in review. **Task 1 records that verdict.** Then E2 (moisture) is
the next family, and this session does its **data build only** — the same
build-then-experiment split E1 used (F98 built, F99 fit). No model is fit this
session.

---

## Task 1 — Record the E1 family verdict (DECISIONS entry only; no code)

Append one new decision entry to the live DECISIONS.md — the next decision
number (expected **D52**; confirm against the live file). Do not touch SPEC.md or
RESULTS.md: the feature-selection programme is exploratory work building toward a
possible future locked method, not yet folded into the spec. Content:

- **Verdict.** From the session-50 / F99 review, E1's adopted contribution is
  the single derived feature **`lapse_rate_t2_t850`** (the `B+L` variant). The
  three raw pressure-level temperatures **`t850` / `t925` / `t700` are NOT
  adopted** into the sweep baseline.
- **RNO's raw-level signal is parked, not dropped.** In the F99 grid the raw
  pressure levels carry a real, fold-robust skill increment at RNO specifically
  (`B+v` skill vs B was +1.4% / +2.0% / +2.7% across the three folds, while `B+L`
  was flat-to-slightly-negative there). This is recorded as an explicit
  candidate to revisit in the later **combine phase**, where joint value and
  redundancy across families are weighed — not carried into the E-sweep.
- **Rationale (keep it concise, plain language).** (a) `B+L` captures +1.9% of
  the +2.0% maximum grand-overall skill on one added feature instead of four —
  parsimony with near-equal skill. (b) The only fold-robust reason to add the
  raw levels is RNO, and RNO is already carried to about +11% skill by
  cloud/wind in the frozen baseline (F94, stable across all four years in F96),
  so E1 need not also rescue it. (c) The DSM case for the raw levels is a single
  fold (2025-26), the year F96 flagged as unrepresentative — the weakest
  evidence in the grid. Per-fold basis is
  `data/processed/session50_e1_experiment_grid.csv`.
- **This is provisional.** Like every family in the sweep, `lapse_rate_t2_t850`
  is confirmed only when the single final feature set is checked on the reserved
  year once, at the finish line — not now.
- **Measurement baseline is unchanged.** E2 and every later family are measured
  against the frozen 5-feature baseline B, **not** against `B+L`. `B+L` enters
  only at the combine phase. Cite F99.

---

## Task 2 — Build the E2 moisture feature set (mirror session 49 / F98 exactly)

Pull, decode, and join the E2 surface-moisture fields onto the existing
5-feature GRIB dataset, at every date that dataset already carries **outside**
the reserved year (D51). **Data build only: fit no model, compute no MAE or CV,
and never load, pull, or join a single row of 2024-08-01..2025-07-31.**

### Fields to pull (2 m height above ground unless noted)

- **`relative_humidity_2m`** (RH, %)
- **`dew_point_2m`** (DPT)
- **`specific_humidity_2m`** (SPFH, kg/kg)

Resolve the exact eccodes keys the same way session 49 resolved the pressure
levels. Same forecast source and archive (`noaa-gfs-bdp-pds`), same lead
convention (D48.2 / F89), same bilinear interpolation to each airport's already
established grid point (SPEC 3.4). Build the date list from the existing dataset's
own rows (`grib_features_v16_window.csv`, `grib_features_sealed_window.csv`), not
from an assumed calendar; skip any row whose `target_date` is inside the reserved
year at the point of loading, never holding it in memory past that line.

### Derived feature

- **`dewpoint_depression_t2m = t2m_raw − dew_point_2m`**, on a consistent raw
  (grid-elevation) basis (see design decision 1).

### Three design decisions to confirm and print in the script's own output BEFORE any pull runs (mirroring F98's docstring gate)

1. **Which 2 m temperature the depression uses — the RAW one, recovered
   algebraically, no new pull.** Use `t2m_raw`, recovered exactly as session 49
   did (`t2m_raw = temperature_grib_c − correction_c`, each airport's fixed
   D48.3/F90 constant from
   `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`) —
   **not** the elevation-corrected `temperature_grib_c`. Reason: the dew-point
   depression must be a difference of two fields on the same (raw, grid-elevation)
   basis; subtracting a raw dew point from the elevation-corrected temperature
   would leak each airport's correction constant into the depression as a
   spurious offset. No new 2 m-temperature GRIB request is needed.
2. **No elevation / lapse-rate correction on the moisture fields.** RH, DPT and
   SPFH are used exactly as GRIB reports them (bilinear horizontal interpolation
   only), the same way cloud cover and wind speed are (SPEC 7.2, F91) and the
   pressure levels were (F98). SPEC 7.2's 7.429 °C/km correction is a
   temperature-only fix for a surface grid-cell elevation mismatch; it does not
   apply to a humidity ratio, a specific humidity, or a dew point used to form a
   depression. State this explicitly in the output before pulling.
3. **No raw GRIB2 bytes kept on disk (disk-space-forced, as in F98).** Use the
   same fetch-decode-discard pattern session 49 used: byte-range-fetch each
   message, decode immediately with eccodes, discard the bytes, and write a
   per-request provenance manifest (run_date, cycle, lead, field, stations,
   status, detail — no bytes) under `data/raw/diagnostics/session51/`. Check free
   disk space before and after and report both.

### Guard checks before any pull request is made (mirror F98)

Run `scripts/session48_reserved_year.py`'s `assert_reserved_year_excluded()` on
both the non-reserved span and the sealed span, plus a defensive per-date scan of
the full date list confirming zero reserved-year dates present. Print the real
result. If either check would touch the reserved year, STOP.

### Outputs

- `data/processed/session51_v16_window_with_moisture.csv`
- `data/processed/session51_sealed_window_with_moisture.csv`
- `data/processed/session51_moisture_join_drops.csv` (expected empty)
- `data/raw/diagnostics/session51/session51_pull_manifest.csv`
- `notes/session-51-moisture-output.txt` (full real output)

---

## Task 3 — Validate the build (still no model fit)

Report real numbers for every check; mark, count and report any gap — never
silently fill or fix (CLAUDE.md).

1. **Join drops = 0 at every airport**, both spans — row counts identical before
   and after the join, logged to the drops CSV.
2. **Availability — zero blanks.** The three pulled fields are fully populated
   (non-null) across the whole v16 window at every airport, the same zero-blank
   check session 46 ran on cloud/wind. Report any nulls with counts and dates.
3. **Physical sanity.** Across every row: `dew_point_2m ≤ t2m_raw` (so
   `dewpoint_depression_t2m ≥ 0`); `relative_humidity_2m` in [0, 100];
   `specific_humidity_2m ≥ 0`. Report the count and dates of any violation; do
   not clip or drop them without instruction — a systematic violation is a decode
   or basis error to diagnose, not to paper over.
4. **Internal-consistency self-check (the E2 analogue of session 49's `t2m_raw`
   derivation check).** Recompute RH from `t2m_raw` and `dew_point_2m` via the
   Magnus relation and compare to the pulled `relative_humidity_2m`; report max
   and mean absolute difference per airport. Close agreement confirms the three
   moisture fields are internally coherent and correctly decoded; a systematic
   gap flags a units/reference-temperature mismatch to diagnose before the fields
   are trusted.
5. **Cross-check against Open-Meteo where overlap exists.** Open-Meteo carries
   `dew_point_2m` and `relative_humidity_2m` from 2024-01-19 (F85). On the
   overlap that falls **outside** the reserved year, compare the GRIB-pulled DPT
   and RH to Open-Meteo's and report agreement (the same kind of cross-check F90/
   F91 ran for temperature and cloud/wind). Note that `specific_humidity_2m` has
   no Open-Meteo counterpart, so it is checked only by 3 and 4 above.

---

## Scope guardrails (hold these)

- **Data build only.** No model is fit; no MAE, skill, or CV is computed this
  session.
- **Reserved year (2024-08-01..2025-07-31) is never touched** — not pulled, not
  loaded, not joined, not scanned into memory.
- **SPEC.md and RESULTS.md are not modified.** Task 1 edits DECISIONS.md only.
- **No per-airport anything** — identical fields and identical handling at all
  five airports.
- **One scope, this scope.** If something outside it looks broken or worth doing,
  log it as an open question in DECISIONS.md; do not act on it.

---

## End-of-session steps (required)

1. Paste the **real output** — actual numbers, not a description.
2. **Consistency check:** re-read CLAUDE.md, SPEC.md, STATUS.md and live
   DECISIONS.md; report any disagreement, duplicated heading, or out-of-order
   entry. Report only — do not fix silently.
3. **Archive step:** move any DECISIONS.md entry that became settled this session
   to DECISIONS-archive.md, per the archive criterion — mechanically, verbatim.
   (F99 and the new D52 are both live inputs to an open programme; expect nothing
   newly archivable this session, but check.)
4. **Overwrite STATUS.md** as the fresh snapshot, and **end it with a "Next
   planning session" line** naming the next action: *session 52 — the E2
   moisture experiment (fit the moisture variants against the frozen 5-feature
   baseline B on the three non-reserved EXPERIMENT_FOLDS, reserved year
   untouched), a reading not a verdict, with the family call made in review.*
5. **Prepare all changes and write out a single suggested commit message**
   (single-quoted body, a title line plus a full multi-paragraph body, no double
   quotes and no apostrophes inside the body, `--` not em-dashes), then **stop
   and wait for review.** Do not commit, add, or push — the owner reviews and
   commits by hand.
