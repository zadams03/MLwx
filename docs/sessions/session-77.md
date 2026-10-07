# Session 77 — KSFO rehearsal, column-order band, and lock

Session 76b diagnosed KSFO's failed reproduction gate (F117). The owner has
now decided Q34 (D69, below): KSFO proceeds under the unchanged recipe.

This session does four things, in order:
1. records the owner's decision (D69);
2. rehearses KSFO on the `2022-23` and `2023-24` folds, including the
   column-order band (D67.4, D67.5);
3. writes and dry-runs the frozen script for session 78's two looks;
4. writes the lock (D70) and makes the SPEC edits listed in Step 7.

**KSFO's held-out years (2024-08-01..2026-07-31) stay closed.** No model is
fit on them and none of their values is read. Only dates and counts may be
used (D67.6).

---

## Standing rules for this session

- SPEC section 2 applies in full.
- Nothing changes F109, F94, F116.5's gate result, or any verdict, claim or
  figure on record.
- **No row dated 2026-08-01 or later is touched.**
- **KSFO's held-out years:** rows dated 2024-08-01 or later are dropped at
  load, before any matrix is built, and only the number removed is reported.
  Step 3 may count dates. Nothing else may use a held-out row. The
  look script's run mode is **not** executed this session.
- The rehearsal is **not a gate** (D67.4). The only stop is a bug. A bug is
  fixed in the pipeline, never in the recipe, and only after reporting it
  and stopping.
- Existing scripts are never edited, including every `session76_`,
  `session76b_`, `session75_`, `session62_` and `session48_` script. The
  session-48 reserved-year guard is not touched or bypassed. New code goes in
  new `session77_` files. Existing scripts may be imported read-only.
- Nothing under `data/raw/` or `data/processed/` is written or changed.
  Rehearsal outputs go to `data/rebuild/session77/`.
- No network calls.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks (no network)

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-77.md`, since session 76b is committed.
2. Report the SHA-256 of:
   - `data/processed/session76_ksfo_features.csv`;
   - `data/processed/session76_ksfo_observations.csv`;
   - `data/rebuild/session75/orderings.csv`;
   - `scripts/session62_reserved_confirm.py`.
3. Confirm that `session76_ksfo_features.csv` holds the nine model columns in
   SPEC 8.8 G15's record order, and that its largest date is 2026-07-31.
4. Read D67, F115, F116, F117 and Q34 in `DECISIONS.md`, and D58 (item 6)
   and D51 in `DECISIONS-archive.md` if they are not live.
5. Read `session75_order_spread.py` and `orderings.csv`. Report how the 102
   `B+D,L,R,T` orderings are stored and how the 120 `B` orderings were made.
   **Stop rule:** if the orderings cannot be mapped to KSFO's columns by
   name, without ambiguity, stop and report.

---

## Step 1 — record the owner's decision (D69), before any fit

Append to `DECISIONS.md`, dated 2026-09-26:

**D69. Owner decision, planning chat (after session 76b): Q34 is decided and
closed. KSFO proceeds under the unchanged `B+D,L,R,T` recipe.**

- **D69.1** KSFO continues under SPEC 8, applied unchanged. Nothing about the
  recipe, the constant (+0.6944 °C) or the pipeline changes.
- **D69.2** The gate result (F116.5) is recorded as **"failed, explained by a
  difference between the sources (F117)"**. There is no override. F116.5
  stands as a FAIL.
- **D69.3 Reasons.** (a) Check A verified the pipeline exactly (F117.2).
  (b) The sea-mixed 0.25° blend is genuine GFS output (F117.3). (c) KSFO is
  the coastal test D32 asked for. (d) The bar's raw-GFS baseline is the same
  GRIB value the model corrects, so the tests stay internally consistent.
- **D69.4** Q34 is closed.
- **D69.5 Session plan.** 77 rehearsal, band and lock; 78 the two looks,
  run once (D67.7, D68.3).
- **D69.6 GFS v17 (planning-chat research, 2026-09-26, not checked by this
  session).** The NWS notice list shows no GFS v17 Service Change Notice.
  The latest SCN is still SCN26-87 (22 Sep 2026). The earliest possible
  go-live is late October 2026. KSFO is unaffected: all its data is v16.

---

## Step 2 — rehearsal (offline, before 2024-08-01 only)

New script: `scripts/session77_ksfo_rehearsal.py`. Outputs to
`data/rebuild/session77/`.

**Data.** `session76_ksfo_features.csv` and `session76_ksfo_observations.csv`.
Drop every row dated 2024-08-01 or later at load and report the counts
removed. Expected: 730 feature rows and 729 observation rows. After the drop,
assert that no row is dated 2024-08-01 or later (the **KSFO rehearsal
guard**). Reject non-finite values at load (SPEC 8.7 item 2) and report the
count.

**Folds.** D51's `EXPERIMENT_FOLDS`, `2022-23` and `2023-24` only. Each must
pass `assert_reserved_year_excluded()`, imported read-only.

**Recipe.** Exactly SPEC 8:
- the G15 column order;
- `LGB_PARAMS`, imported read-only from `session62_reserved_confirm.py`;
- the G14 API, G17 defaults and G19 row order;
- the G20 target: `obs − temperature_grib_c`, unrounded.

Prediction = `temperature_grib_c` + the predicted residual.

**Pipeline checks, pre-registered.** Any failure is a bug: stop and report.
- **Rows (complete and paired, from F116.4).**
  - `2022-23`: train 494, test 364.
  - `2023-24`: train 858, test 365.
- **Columns.** Each matrix has exactly the G15 column list and no non-finite
  value.
- **Determinism.** Record-order `B+D,L,R,T` repeated in a separate process
  gives equal predictions on every test day.

**2a. Rungs, per fold.** MAE (G24) for each of:
- raw GFS (GRIB) = `temperature_grib_c`;
- persistence = the previous day's paired observation;
- mean-bias reference = raw GFS + mean(obs − raw GFS) over that fold's
  training rows;
- `B` (canonical order);
- `B+D,L,R,T` (record order).

**Day basis (as D58 item 6).** Persistence is scored on test days that have a
previous-day observation. The other rungs are scored on every test day.
Report the persistence day count. Also report every rung re-scored on the
common day set, labelled as descriptive.

Say, per fold, whether `B+D,L,R,T` beats raw GFS and persistence. Label this
"rehearsal, not a gate".

**2b. Bias, descriptive only.** On all complete, paired rows before
2024-08-01, report the following per calendar month and per year:
- n;
- mean obs;
- mean(obs − raw GFS);
- mean |obs − raw GFS|;
- mean(obs − Open-Meteo) and its n, where Open-Meteo is session 76's raw
  `temperature_2m_previous_day1` at 20:00 UTC, on days where it exists.

Nothing is selected or tuned on this.

**2c. Column-order spread and band (D67.5, F115's method).**
- Run F115's 102 `B+D,L,R,T` orderings and all 120 `B` orderings on both
  folds.
- Report, per model and fold: min, max, range, standard deviation (`numpy.std`,
  ddof 0), and the win share. Use the definitions in F115 (strict "lower").
- Report the record-order margin: canonical `B` MAE minus record-order
  `B+D,L,R,T` MAE, in °C and %.
- **Band = the largest range among the four sets** {B, B+D,L,R,T} ×
  {2022-23, 2023-24}. Report it at full precision and at 4 dp, and say which
  set gave it.
- Quote F115's largest range (0.0386 °C) beside it, as context only.

---

## Step 3 — expected counts for the looks (dates only)

Using dates and row presence only, and no values, count the following for
each look (D67.3):
- **Look A:** train 2021-03-24..2024-07-31, test 2024-08-01..2025-07-31.
- **Look B:** train 2021-03-24..2025-07-31, test 2025-08-01..2026-07-31.

Count:
- training rows (complete and paired);
- test rows (complete and paired);
- persistence test days (a paired observation exists on the day and on the
  day before).

Expected from F116.4:
- Look A: train 1,223, test 364.
- Look B: train 1,587, test 365.

Report persistence days as found. If any count differs from the expected
value, stop and report.

---

## Step 4 — the frozen look script (written and dry-run, not run)

Write `scripts/session77_ksfo_looks.py`. Session 78 runs it once, unchanged.

**It must:**
1. Take the recipe from Step 2 exactly (same imports, G14–G24).
2. Before anything else, check the SHA-256 of both KSFO data files and of
   `session62_reserved_confirm.py` against values written into the script.
   On a mismatch, it stops.
3. Assert that the station is `SFO`, and that the nine columns equal the
   G15 list.
4. **The KSFO held-out guard.** For each look, it asserts:
   - training max date < test min date;
   - look A's training ends 2024-07-31;
   - look B's training ends 2025-07-31;
   - test windows are exactly as D67.3 gives them;
   - no row anywhere is dated 2026-08-01 or later;
   - training, test and persistence counts equal Step 3's values, written
     into the script (SPEC 8.7 item 4).

   Any failure stops the script before any fit.
5. Have two modes:
   - `--dry-run` (the default). This runs checks 2–4 using dates and counts
     only. Then it runs a **self-test**: the same fit-and-score code on the
     `2023-24` fold must reproduce Step 2a's five MAEs exactly. It reads
     nothing else.
   - `--run-looks`. This refuses to start if either output file exists
     (SPEC 8.7 item 5). It fits and scores both looks. It writes
     `data/processed/session78_ksfo_looks_grid.csv` (all rungs, both looks,
     both day bases, band reads) and
     `data/processed/session78_ksfo_looks_predictions.csv`.
6. In `--run-looks` mode, print for each look:
   - the five rungs;
   - pass or fail against SPEC 5.3;
   - the D67.5 band read (margin against the frozen band);
   - the common-day re-score, labelled as descriptive.

   Then print the overall reading from D67.3: **pass** (both looks pass),
   **split** (one passes, one fails), or **fail** (neither passes).
7. Not import, call, edit or disable the session-48 reserved-year guard.
   That guard protects the five earlier airports. KSFO uses its own guard.

Run `--dry-run` once. Report its full output, including the self-test.
**Do not run `--run-looks`.** Then report the script's SHA-256.

---

## Step 5 — record the rehearsal (F118)

Append **F118** to `DECISIONS.md`. It records:
- Step 0;
- the rehearsal data, guard and removed counts;
- the pipeline checks;
- the 2a table and day bases;
- the 2b bias tables;
- the 2c spread tables, win shares, margins and the band;
- Step 3's counts;
- Step 4's dry-run and self-test;
- the new files;
- a "What this did not do" list.

It changes no verdict, claim or figure. F109 stands.

---

## Step 6 — the lock (D70)

Append **D70**, dated 2026-09-26: **"KSFO lock: frozen before either held-out
year is opened."** It states:

- **D70.1 Recipe.** SPEC 8 unchanged:
  - the nine G15 columns, in order;
  - `LGB_PARAMS`;
  - G14, G17, G19, G20 and G24;
  - no per-airport choice.
- **D70.2 Source and constant.**
  - Data files and their SHA-256 values (Step 0).
  - Elevation constant **+0.6944 °C**, from
    `data/raw/diagnostics/session76/session76_elevation_correction_params.csv`
    (F116.2), already applied in `temperature_grib_c`.
- **D70.3 Looks.** Windows as D67.3. Look B's training includes 2024-25, by
  design. Expected counts from Step 3.
- **D70.4 Bar.** SPEC 5.3: beat raw GFS (GRIB, elevation-adjusted) **and**
  persistence on MAE, judged separately for each look.
  - The day basis is as D58 item 6.
  - "KSFO passes" only if both looks pass. One pass and one fail is recorded
    as a split. Nothing is re-run or adjusted.
  - The common-day re-score and the mean-bias reference are informative
    only.
- **D70.5 Band.** The frozen band value (full precision and 4 dp) and the
  D67.5 reading rule. It is a secondary read, not part of the bar.
- **D70.6 Frozen script.** `scripts/session77_ksfo_looks.py`, with its
  SHA-256. Session 78 checks the hash, then runs `--run-looks` once,
  unchanged.
- **D70.7 KSFO held-out guard.** Summarise Step 4 item 4.
- **D70.8 Pre-registered expectation.** "Pass in both years" (D67.3),
  restated. **No expectation is registered about raw GFS at KSFO, about which
  half of the bar binds, or about the size of any margin.** Rehearsal's
  measured bias (F118) is context only. Raw GFS at KSFO is known only to run
  colder than Open-Meteo (F116.5), and Open-Meteo may itself be warm at SFO.
- **D70.9 Framing (must be carried by any write-up).** KSFO's result is for
  the recipe at a sea-mixed grid point: 37.5% of the 0.25° blend's weight is
  on sea points (F117.3). **It is not directly comparable with the five
  earlier airports, whose reproduction gates passed.** The gate is recorded
  as failed, explained by a difference between the sources (D69).
- **D70.10 SPEC edits made this session.** List each Step 7 edit.

---

## Step 7 — SPEC edits (authorised here, and only these)

1. **SPEC 1, KSFO bullet.** Replace "stage 2 — verified on contact (session
   76); not yet tested. The project's first coastal airport (DECISIONS D67,
   F116)." with: "stage 2 — rehearsed and locked (session 77, DECISIONS D70);
   not yet tested. The project's first coastal airport. Its GRIB-vs-Open-Meteo
   reproduction gate failed, explained by a difference between the sources
   (DECISIONS F116, F117, D69)."
2. **SPEC 3.2.** After the paragraph that ends "(see DECISIONS F5)." and
   before the paragraph beginning "Every value is nonetheless", add:
   "**Which GFS product.** Open-Meteo's documentation (pulled 2026-09-26)
   marks `temperature_2m` under this model as coming from GFS's
   high-resolution 0.11° product, not the 0.25° product that sections 7 and 8
   use (DECISIONS F117.4). The page describes the service on that date. It
   does not say which product built the 2021–2024 archive."
3. **SPEC 3.3, the KSFO paragraph.** Append: "The reproduction gate that
   checks its GRIB temperature and constant against Open-Meteo failed
   (DECISIONS F116). The owner recorded it as failed, explained by a
   difference between the sources, with no override (DECISIONS F117, D69)."
4. **SPEC 3.4.**
   - In the first table, change SFO's stage cell to "2 — locked, not yet
     tested".
   - In the KSFO note, replace "It is not yet in 5.2's list; the lock session
     adds it. KSFO's reproduction gate failed in session 76 (F116, Q34)."
     with: "It is in 5.2's list (DECISIONS D70). Its four surrounding 0.25°
     GRIB points are two sea points (weight 0.375) and two land points
     (0.625) (DECISIONS F117). Its reproduction gate failed, explained by a
     difference between the sources (DECISIONS F116, F117, D69)."
   - Replace "DSM's is the closest of the five" with "DSM's is the closest of
     the six".
   - Replace "**All five network codes are now verified by a real pull.**"
     with "**All six network codes are now verified by a real pull.**". In
     the same note, replace "and RNO's `NV_ASOS` in session 25 (DECISIONS
     F66)" with "RNO's `NV_ASOS` in session 25 (DECISIONS F66) and SFO's
     `CA_ASOS` in session 76 (DECISIONS F116)".
5. **SPEC 5.2.** Replace "The five adjustments, in °C (`correction_c` in
   `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`):
   EGLC +0.2486, LFPG −0.1697, DSM −0.1106, YSDU +0.2461, RNO +2.0436." with:
   "The adjustments, in °C: EGLC +0.2486, LFPG −0.1697, DSM −0.1106, YSDU
   +0.2461, RNO +2.0436 (`correction_c` in
   `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`),
   and KSFO +0.6944 (`data/raw/diagnostics/session76/session76_elevation_correction_params.csv`;
   DECISIONS F116, D70)." Nothing else in section 5 changes.
6. **SPEC 6, the KSFO bullet.**
   - Change "— verified, not yet tested." to "— locked, not yet tested."
   - Replace "Rehearsal and lock wait for the owner's decision (Q34)." with:
     "The owner recorded the gate as failed, explained by a difference between
     the sources, and kept the recipe unchanged (DECISIONS D69). Rehearsed and
     locked in session 77 (DECISIONS F118, D70). Its two looks run once, in
     session 78."
7. **SPEC 7.2.**
   - Delete ", weighted by distance" from "(estimated from the four
     surrounding grid points, weighted by distance)". Nothing else in that
     sentence changes.
   - In the raw-GFS bullet, change "the five adjustment sizes" to "the
     adjustment sizes".
8. **SPEC 7.3.** Replace "matched it closely at every airport once the
   elevation correction was applied" with "matched it closely at each of this
   section's five airports once the elevation correction was applied". At the
   end of that paragraph, add: "The Open-Meteo series used as this check is
   documented as coming from GFS's 0.11° product, not the 0.25° product used
   here (DECISIONS F117.4). The check passed at all five airports anyway. At
   KSFO, added later under section 8, it failed, explained by a difference
   between the sources (DECISIONS F116, F117, D69)."

If any quoted text is not found exactly once, stop and report. Do not
improvise wording. Do not edit RESULTS.md, README.md or CLAUDE.md.

---

## End-of-session steps (CLAUDE.md)

1. Write the **real output** of every step to `notes/session-77-output.txt`.
2. **Archive:** move Q34 and D68 (both settled by D69) to
   `DECISIONS-archive.md`, verbatim, per D46. D67, D69, D70, F115, F116, F117
   and F118 stay live. Report the before and after line counts.
3. **Overwrite STATUS.md** as a current-only snapshot:
   - Record that KSFO is rehearsed and locked, with the band and the frozen
     script.
   - Q34 is closed. Q30 and Q32 stay open, unchanged.
   - Carried: the GFS v17 re-check, updated to D69.6.
   - **Delete** the old note "raw GFS at KSFO is heavily biased relative to
     Open-Meteo ... persistence is the binding part of the bar". D70.8
     replaces it.
   - Delete session 76's SPEC wording items 1–4. They are fixed by Step 7.
   - End with a **"Next planning session"** line: "Review session 77. If it is
     committed, session 78 checks the look script's hash and runs
     `scripts/session77_ksfo_looks.py --run-looks` once, unchanged. After the
     KSFO verdict, hold the roadmap planning session (D66.1)."
4. **Consistency check:** re-read CLAUDE, SPEC, STATUS and DECISIONS. Report
   disagreements, duplicated headings, out-of-order entries and unresolved
   citations. Report only.
5. **Do not write a commit message file, and do not commit.** The planning
   chat writes `docs/commit-77.txt` after review. Stop and wait for the
   owner's review.
