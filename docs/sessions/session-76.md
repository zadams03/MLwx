# Session 76 — KSFO: record the owner's decisions, verify on contact, pull and build

This is session 1 of 3 for a new airport, San Francisco International (KSFO),
under the frozen selected-features recipe `B+D,L,R,T` (SPEC section 8). The
plan is:
- **76 (this session):** record the owner's decisions (D67), verify KSFO on
  contact, pull all data, build all nine features and the paired observations.
- **77:** rehearsal on two past folds, the column-order spread, and the lock.
- **78:** the two looks (2024-25 and 2025-26), run once.

**No model is fit this session. No MAE, bias, residual or any
forecast-minus-observation statistic is computed for any period.**

---

## Standing rules for this session

- SPEC section 2 applies in full.
- Nothing changes F109, F94 or any verdict, claim or figure on record.
- **No row dated 2026-08-01 or later is pulled, built or touched.**
- **At KSFO, 2024-08-01..2026-07-31 is held out** (both look years). Rows in
  that range are pulled and built, but before the lock only **counts and
  timestamps** from it may be read or printed. No temperature (observed or
  forecast), cloud, wind or other feature value from those two years may be
  printed, summarised, plotted or compared, in any output.
- Verify-on-contact samples come from **outside** 2024-08-01..2026-07-31
  (SPEC 3.3's precedent from Dubbo on).
- Frozen scripts are never edited (D62.3). Existing scripts are never edited.
  New code goes in new files with a `session76_` prefix and meets all five
  SPEC 8.7 build requirements.
- The in-code reserved-year guard (`scripts/session48_reserved_year.py`) is not
  touched. It covers the five existing airports. KSFO's looks will need their
  own guard, written in session 77/78, not here.
- Raw GRIB stays gitignored (D47). Commit manifests, drop logs and processed
  files only.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks and read-on-demand (no network)

1. `git status --porcelain`. Report it. Expected: only `?? docs/session-76.md`.
2. Read-only scan of every `.csv` under `data/processed/` for its maximum date.
   Confirm no row reaches 2026-08-01.
3. Read these archived entries from `DECISIONS-archive.md`, by number, as
   needed: **F66** (Reno's candidate verification, the model to follow),
   **F89, F90** (GRIB lead convention, bilinear, elevation correction and the
   Open-Meteo reproduction gate), **D48** (items 2, 3, 7, 8, 10), **F98, F100,
   F101, F102** (how L, D, T and R were pulled and built), **F107** (the
   reserved-year build of L, D, T, R).
4. From the scripts themselves, confirm and report, with file and line:
   - (a) **The elevation constant formula** as used in
     `session37_elevation_fix.py`: exactly how the GRIB model-terrain height at
     a station is obtained (which field, which interpolation), how the constant
     is computed from 7.429 °C/km, and how it is rounded and stored (SPEC 8.8
     G5).
   - (b) **T (pressure tendency, 3 h):** which forecast hours it differences at
     lead 26, so it is certain that the frozen construction applies unchanged
     at a 20:00 UTC target.
   - (c) **R (shortwave, 2 h window):** confirm that at lead 26 the record uses
     the native 24–26 h `DSWRF` average directly (SPEC 8.2), as at RNO.
   - (d) **L and D:** confirm nothing in their construction depends on the
     airport beyond position, grid point and target hour.
   **Stop rule:** if any of (a)–(d) would need more than substituting KSFO's
   position, grid point, target hour and constant, stop here and report.

---

## Step 1 — record the owner's decisions (D67), before any network call

Append this entry to `DECISIONS.md` exactly in substance (plain wording, may be
lightly formatted), dated 2026-09-25, **before** Step 2 starts:

**D67. Owner decisions, planning chat (after session 75): the new airport and
its test design.** Written before any KSFO data was pulled.

- **D67.1 Airport.** San Francisco International (KSFO), Q30 branch (i)
  (D59.5, D66.1), under the frozen `B+D,L,R,T` recipe (SPEC 8), applied
  unchanged. It is a coastal airport, a harder type per D32. Its standard
  offset is UTC−8, so its target hour is 20:00 UTC (local standard noon, D33),
  the same hour and lead (26) as RNO.
- **D67.2 Offset rule (hard filter for new airports under SPEC 8).** R has a
  frozen construction only for lead 24 (target hour a multiple of 6) and lead
  26 (target hour mod 6 = 2) (SPEC 8.2). A new airport keeps the recipe
  unchanged only if its local-standard-noon hour gives one of those two leads,
  i.e. standard offset 0, −2, +4, ±6, −8, +10 or +12.
- **D67.3 Test design: two pre-registered looks.**
  - Look A: train 2021-03-24..2024-07-31 (1,226 days), test
    2024-08-01..2025-07-31. An exact replica of F109's fold.
  - Look B: train 2021-03-24..2025-07-31, test 2025-08-01..2026-07-31.
  - Each year is judged **separately** against the frozen bar (SPEC 5.3):
    beat raw GFS (GRIB, elevation-adjusted with KSFO's own constant) and
    persistence on MAE.
  - "KSFO passes" is claimed only if both looks pass. If one passes and one
    fails, it is recorded as a split. Nothing is re-run or adjusted.
  - Both looks are frozen in one script before either year is opened, and run
    once, together, in session 78.
  - Pre-registered expectation (to be restated in the lock): pass in both
    years.
- **D67.4 Rehearsal (session 77).** On the `2022-23` and `2023-24` folds of
  D51's `EXPERIMENT_FOLDS` only (the truncated `2025-26` fold is excluded: it
  tests a KSFO held-out year). Purpose: a pipeline check and the column-order
  spread (D67.5). It is **not a gate**: a poor rehearsal does not stop the lock
  (D44 precedent). The only stop is a bug, and any fix is to the pipeline,
  never to the recipe.
- **D67.5 The vs-B band (column-order wobble, F115).** In rehearsal, KSFO's
  column-order spread is measured with F115's method and F115's own orderings
  (`data/rebuild/session75/orderings.csv`: the 102 `B+D,L,R,T` orderings; all
  120 `B` orderings). **Band = the largest MAE range (max − min across
  orderings) among the four sets {B, B+D,L,R,T} × {2022-23, 2023-24}.** It is
  frozen in the lock. For each look, the record-order `B+D,L,R,T` margin over
  canonical-order `B`: above +band → "beats B by more than the column-order
  spread"; below −band → "B beats B+D,L,R,T by more than the spread";
  otherwise → "within the column-order spread". This is a secondary read, not
  part of the bar. F115's largest range (0.0386 °C) is quoted beside it as
  context only.
- **D67.6 Held-out handling at KSFO.** 2024-08-01..2026-07-31 is held out.
  Before the lock, only counts and timestamps from it are read.
  Verify-on-contact samples are drawn from outside it. No row dated
  2026-08-01 or later is used.
- **D67.7 Session plan.** 76 verify, pull and build; 77 rehearsal, spread and
  lock; 78 the two looks.
- **D67.8 GFS v17 (planning-chat research, 2026-09-25, not checked by this
  session).** The NWS notice list shows no GFS v17 Service Change Notice; the
  latest SCN is SCN26-87 (22 Sep 2026). An SCN comes 30 days before go-live,
  so the earliest possible go-live is late October 2026. KSFO is unaffected:
  all its data (2021-03-24..2026-07-31) is v16. Re-check at each planning
  session (D66.2).

---

## Step 2 — verify on contact (network, small samples)

Follow F66's pattern. Record every query and pull date (SPEC 2.3). Raw files go
to `data/raw/`, each with a `.meta.txt`.

1. **Station.** From IEM's own `CA_ASOS` station listing (saved to
   `data/raw/`), find San Francisco International. Record exactly the station
   code IEM uses, its latitude, longitude and elevation. Nothing typed from a
   map. Note whether the code is an ICAO code (SPEC 3.4 notes).
2. **Target hour.** Check `America/Los_Angeles` in the timezone database:
   confirm the standard offset is UTC−8, so local standard noon is 20:00 UTC.
   Stop if not.
3. **Report minute and units.** A short observation sample (a few weeks) from
   **2023** (outside the held-out range). Report: the routine report's minute
   (`report_type=3`), whether a second scheduled report exists (SPEC 3.4's
   "also files at"), that temperature is in °C, and that a UTC-stamped request
   returns UTC (F35's check). Compute the pairing offset to 20:00 UTC.
4. **Open-Meteo grid point and archive floor.** Request `gfs_global`,
   `temperature_2m` at `previous_day1` for 2021-03-20..2021-03-27 at IEM's
   position. Report the returned grid latitude, longitude and elevation,
   distance from the station, the height mismatch, and whether the first
   non-null hour is 2021-03-24 00:00 UTC (F1, F20, F33).
5. **GRIB elevation and constant.** Using the method confirmed in Step 0(a),
   get the GRIB model-terrain height at KSFO's grid point and compute KSFO's
   elevation constant with the frozen 7.429 °C/km. Report the unrounded value
   and the stored (rounded) value. Use one GRIB file from before 2024-08-01.
6. **Land/sea (descriptive, optional).** If a land-mask field is present in a
   file already fetched in 2.5, report the land fraction at the four
   surrounding grid points. Do not make a new pull just for this.

**Stop rule:** stop and report if the station is not in the listing, the
offset is not UTC−8, the routine minute is unclear, the Open-Meteo floor is not
2021-03-24, or anything needs a choice this prompt does not make.

---

## Step 3 — SPEC edits (from Step 2's real output only)

1. **SPEC 3.4:** add a KSFO row to both tables, filled from Step 2, stage
   "2 — verified, not yet tested". Add a short note on the KSFO GRIB elevation
   constant, with its DECISIONS citation (F116).
2. **SPEC 1:** add KSFO to the airport list: "stage 2 — verified on contact
   (session 76); not yet tested."
3. **SPEC 6:** add a KSFO bullet under stage 2 citing D67 and F116.
4. **SPEC 3.2:** replace "all four airports pulled so far" with wording that
   does not carry a count, and add KSFO to the floor sentence if Step 2.4
   confirmed 2021-03-24.
5. **SPEC 3.3:** one sentence recording KSFO's verify on contact (F116).
6. **SPEC 7.2 (carried item):** after "weighted by distance", clarify in one
   line that this is standard bilinear interpolation (weights from the
   fractional position along latitude and longitude), not inverse-distance
   weighting (SPEC 8.8 G6).

Do **not** edit SPEC section 5 (including 5.2's list of elevation constants).
That is left to the lock session.

---

## Step 4 — the full pull (network)

Window: **2021-03-24..2026-07-31** at KSFO, target 20:00 UTC, lead 26.

1. **GRIB:** every field needed for all nine columns of `B+D,L,R,T` (SPEC 8.1,
   8.2; section 7 for B), with the frozen lead convention, byte ranges and
   bilinear interpolation. New `session76_` scripts may import pure functions
   from the record scripts read-only, or copy them, but must meet SPEC 8.7
   (explicit nearest report, reject non-finite at load, check each message's
   full validity date **and hour**, gap guard against the expected full count,
   no writes to committed record files).
2. **Observations:** the full IEM routine-report pull for the window, raw, with
   `.meta.txt`.
3. **Open-Meteo (reproduction gate only):** `temperature_2m`,
   `previous_day1`, 2021-03-24..**2024-07-31** only.
4. **Manifests (D47):** committed manifest of every GRIB request (URL, byte
   range, pull time) and a drop log.

Expected calendar-day counts: **1,956** days in the whole window; **1,226**
before 2024-08-01; **365** in each held-out year. Report the counts actually
pulled per field against these. Drops are counted, never filled (SPEC 2.2).

---

## Step 5 — build and checks

1. **Feature table.** One processed KSFO file with a date column, the nine
   model columns in the record order (SPEC 8.8 G15) and their underlying
   columns (`t2m_raw`, `t850`, `dew_point_2m`, etc.), with the stored
   precision and rounding order of SPEC 8.8 G4, G5 and G7, and D's floor
   transform.
2. **Paired observations.** One processed file: the observation paired to
   20:00 UTC per day, by the nearest routine report within 15 minutes
   (SPEC 4.5, 8.7 item 1). Report tie days and dropped days.
3. **Counts (all years, counts only).** Per year and per held-out window:
   feature rows, complete-case rows over all nine columns' underlying
   columns, paired-observation days, and days with both. Also the counts for
   D51's two rehearsal folds.
4. **Reproduction gate (before 2024-08-01 only).** Compare KSFO's
   elevation-adjusted GRIB temperature with Open-Meteo's on identical rows,
   using F89/F90's own gate criterion. Report mean |diff| and signed mean
   diff. **If it fails, stop after reporting. Do not change the constant or the
   pipeline.**
5. **Feature sanity (before 2024-08-01 only).** Per column: count, min, max,
   and the number of non-finite values dropped. Also cloud and wind against
   Open-Meteo where both exist, as F90 did (2024-01-19..2024-07-31).

No model fit. No MAE. No forecast-minus-observation statistic, for any
period.

---

## Step 6 — record the finding (F116)

Append **F116** to `DECISIONS.md`: what was verified (Step 2's facts), the
Step 0 confirmations (a)–(d), the elevation constant, the pull and drop counts
against the expected counts, the reproduction gate result, the feature sanity
table, the held-out handling actually followed, the new files, and a "What this
did not do" list. It changes no verdict, claim or figure. F109 stands.

---

## End-of-session steps (CLAUDE.md)

1. Paste the **real output** of every step.
2. **Archive:** move **D63** and **F111** to `DECISIONS-archive.md`,
   mechanically and verbatim (settled; session 75 flagged both as meeting the
   D46 criterion). Move any other entry that this session settled, per D46.
   D67 and F116 stay live. F115 stays live (session 77 cites it). Report
   before/after line counts.
3. **Overwrite STATUS.md** as a current-only snapshot. Remove the two carried
   SPEC items if Step 3 did them. Keep the GFS v17 re-check item. End with a
   **"Next planning session"** line: review session 76; then draft session 77
   (KSFO rehearsal on the 2022-23 and 2023-24 folds, the column-order band per
   D67.5, and the lock, including SPEC 5.2's KSFO constant and a KSFO-specific
   held-out guard for session 78).
4. **Consistency check:** re-read CLAUDE, SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings, and out-of-order entries. Report only.
5. Write the suggested commit message. **Do not commit.** Stop and wait for the
   owner's review.
