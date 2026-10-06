# Session 97: D89, the cross-validation rules, and the curve's baseline scored

Session 96 (the stage C development table and its gate, F138) is
reviewed, committed and pushed. Before any cross-validation score is
computed, D88.9 requires a DECISIONS entry that fixes the folds, the
metric and the decision rule. This session writes that entry, then fits
the curve's baseline (D88.4) and scores it and raw GFS per airport,
fold, cycle hour and lead. It makes no build choice: there is only one
option so far. It:

1. records **D89** (the owner's decisions), before any other edit
   (Step 1);
2. counts the fold rows, with no fit (Step 2);
3. **gates** the fitting code by reproducing F109's recorded MAEs
   exactly at EGLC, LFPG and DSM (Step 3);
4. **fits and scores** the baseline and raw GFS by D89's folds (Step 4);
5. checks the scoring is repeatable (Step 5);
6. records what it found as **F139**, and does the end-of-session steps.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **No network at all.**
- **Nothing from 2026-27.** No row valid after 2026-07-31T23:00 UTC is
  read or scored. The table holds none; a guard in code still refuses
  one.
- **Development airports only:** EGLC, LFPG, DSM, YSDU, RNO, KSFO, from
  the six table files in `MLwx-stagec/`. No other airport's data is
  read.
- **Read only:** `MLwx-stagec/` (`/Users/zacharyadams/Coding Projects/MLwx-stagec/`)
  and `MLwx-pull/`. Change nothing in either.
- **Scores here are build-choice scores, not results (SPEC 2.5).** They
  may be printed and recorded, always labelled as such. No claim, pass
  or fail is made from them.
- **No build choice is made.** No setting, feature, parameter or
  structure is changed, tuned or selected. Only D88.4's baseline is fit,
  with the record's settings.
- **Writes.** Only: the new script `scripts/session97_stagec_cv.py`;
  the new files `data/processed/session97_stagec_cv_scores.csv`,
  `data/processed/session97_stagec_cv_folds.csv` and
  `data/processed/session97_stagec_cv.meta.txt`;
  `notes/session-97-output.txt`; and the DECISIONS.md and STATUS.md
  edits the steps give. No model file is saved. Do not touch
  `data/models/`. No other file under `data/` is created or changed.
- **Do not edit any existing script.** Import, read only, from
  `scripts/session62_reserved_confirm.py`: `LGB_PARAMS` and the G15
  column order (as session 81 did, F122.2). Check its SHA-256 first.
  Read the table files directly; do not rebuild them.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- **No installs.** Use what is installed (lightgbm 4.7.0 is pinned in
  `requirements.txt`; if the installed version differs, stop and
  report).
- Keep the laptop awake for long steps (D86.5), for example with
  `caffeinate -i`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-97.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D88 and F138, and that
   no D89 or F139 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm the new script and the three new `data/processed/` files do
   not exist.
4. Check SHA-256, against the value on record. Any difference: stop and
   report.
   - The six table files in `MLwx-stagec/` (F138.4).
   - `data/processed/session96_stagec_dev_table.meta.txt`
     (`eace666a0f1ab2b65614c340899b849eb0e97c25cf49eaaa45eb83747ce89463`)
     and `data/processed/session96_stagec_dev_counts.csv`
     (`304d25a6689b1442ca0b184244a93bc031e9a9157e313cb4b96a04ce22383dfb`).
   - `scripts/session96_stagec_table.py`
     (`40b63d006a3de4b4b796476c6b2408700bc9200a508feda804a187531b666eee`).
   - `scripts/session62_reserved_confirm.py` (D70.2, `9f8af9af...80b4`;
     the full value is in D70.2 in DECISIONS-archive.md).
   - `data/processed/session81_training_set.csv` (F122.3,
     `ab8f25f2...8d4a`).
   - `data/processed/session63_reserved_confirm_grid.csv`: report its
     SHA-256 and where it is recorded, if it is.
5. Read: D70, D71, D72, D82, D88, F109, F122, F138 (archive entries in
   DECISIONS-archive.md); SPEC 2.5, 5, 8.1 to 8.3, 8.5 and 8.8;
   `scripts/session62_reserved_confirm.py` in full.
6. Print the Python, numpy and lightgbm versions used.

---

## Step 1: record D89 (before any other edit)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 97 decision: F138 accepted, GFS v17, and the rules for stage C's build choices (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D89. Owner decisions, planning chat (after session 96): F138
accepted, GFS v17, and the rules for stage C's build choices: folds,
metric and decision rule (D88.9).** Written at the start of session 97,
before any other edit and before any cross-validation score. No
2026-27 value has been read or scored.

- **D89.1 F138 accepted.** The owner accepts F138 and all thirteen
  F138.8 readings, including: both `temp` and `temperature_grib_c`
  kept as columns; the instantaneous columns taken from session 91's
  `derive` with placeholder R and T inputs that never reach the table;
  and the fourth empty reason, "outside pull window" (7 R and 10 T
  cells per airport in the first cycles).
- **D89.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is still SCN 26-89 (2
  October 2026). The earliest go-live stays about 5 November 2026.
- **D89.3 Folds.** Three time-ordered folds, each with an expanding
  training window. A test year runs 1 August to 31 July:
  fold 2023-24: test cycles 2023-08-01T00 to 2024-07-31T18;
  fold 2024-25: test cycles 2024-08-01T00 to 2025-07-31T18;
  fold 2025-26: test cycles 2025-08-01T00 to 2026-07-31T18.
  With T0 the test year's start (1 August, 00:00 UTC): training rows
  are those with valid time before T0; test rows are those whose cycle
  starts on or after T0 and before the next 1 August. A row whose cycle
  is before T0 and whose valid time is on or after T0 is in neither,
  and is counted. Training thus uses only observations already known
  when the first test cycle starts. The 2022-23 fold is not used: its
  training window (about 1.4 years) is far shorter than the product's
  or the claim airports' (about 3.4 years, D82.7(e)), and would
  unfairly penalise options that fit many small models.
- **D89.4 The spent years.** 2024-25 and 2025-26 are spent at every
  development airport (F94, F109, F119; D71.1), so they may be used
  for build choices (D72.2(a), SPEC 2.5). The session-48 reserved-year
  guard stays unchanged in its own script and is not imported here.
  Nothing from 2026-27 is used.
- **D89.5 Metric.** Mean absolute error (MAE) of the hourly
  temperature, degrees C, full precision (SPEC 8.8 G24), on leads 3 to
  24. Rows: the common row set, meaning test rows that have an
  observation and are complete for every option compared (for the
  baseline, the table's `complete_case`). Per airport: one MAE over all
  its test rows, pooled across the three folds, four cycle hours and
  leads 3 to 24. Headline: the unweighted mean of the six airport
  MAEs. Fold level: per fold, the unweighted mean of the six airports'
  MAEs over that fold's rows.
- **D89.6 Decision rule.** The challenger replaces the incumbent only
  if all three hold: (a) the headline MAE is lower by more than 1
  percent of the incumbent's headline, that is (incumbent - challenger)
  / incumbent > 0.01; (b) the airport MAE is lower at 4 or more of the
  6 airports; (c) the fold-level MAE is lower in at least 2 of the 3
  folds. Otherwise the incumbent stays. A tie keeps the incumbent.
- **D89.7 The incumbent.** For D82.5's model-structure comparisons, the
  incumbent is D88.4's baseline (the proven recipe, unchanged, D72.2(b)),
  even though the alternatives use fewer models. Every later
  comparison names its incumbent in its own DECISIONS entry before it
  is scored.
- **D89.8 Scope of the rule.** It applies to every stage C build choice
  on the hourly curve. A choice is applied to the whole curve and to
  every airport identically: never per airport, cycle hour or lead.
  The daily maximum's metric is fixed in its own entry before any
  daily-maximum score. Changing these rules needs a new DECISIONS entry
  written before the affected score. Build-choice scores are never
  quoted as results (SPEC 2.5).
- **D89.9 The fitting code's gate.** Before any fold is scored, the new
  fitting code reproduces F109's recorded raw GFS and `B+D,L,R,T` MAEs
  at EGLC and LFPG (12z, lead 24) and DSM (18z, lead 24), exactly, from
  the table's rows on the record's days. This is a code check against
  numbers already on record. It is not a new look and decides nothing.
- **D89.10 Sequence.** Session 97: this entry, the fold counts, the gate,
  then the baseline and raw GFS scored per airport, fold, cycle hour
  and lead. No build choice is made. Then, planned: D82.5's
  alternatives, each against the baseline under D89.6, one at a time;
  then the daily maximum and bias drift (D81.10(b)). Stage C's claim
  design is fixed at its lock.
```

---

## Step 2: the fold rows (no fit)

`scripts/session97_stagec_cv.py --folds`, reading the six table files:

1. Apply D89.3 exactly. T0 values: 2023-08-01T00:00Z, 2024-08-01T00:00Z,
   2025-08-01T00:00Z. Fold ends are the next 1 August, 00:00 UTC.
2. Write `data/processed/session97_stagec_cv_folds.csv`: one row per
   airport, fold, cycle hour (0, 6, 12, 18) and lead (3 to 24):
   training rows (complete case), test rows (complete case), test rows
   dropped as not complete case, and rows in neither (the boundary
   rule). Equal content, equal bytes.
3. Report, per airport and fold: total training rows, total test rows,
   boundary rows, and the smallest training count of any single model.
   Check that the three folds' test rows never overlap and that every
   training row's valid time is before its fold's T0. A failure: stop
   and report.

---

## Step 3: the gate (D89.9)

`scripts/session97_stagec_cv.py --gate`:

1. For EGLC and LFPG at cycle hour 12, lead 24, and DSM at cycle hour
   18, lead 24: take the table rows whose (station, valid date) appears
   in `data/processed/session81_training_set.csv`. Training: valid dates
   2021-03-24 to 2024-07-31. Test: valid dates 2024-08-01 to 2025-07-31.
   This is F109's fold, chosen by valid date as the record does (not
   D89.3's rule).
2. Fit exactly as the record: G15 columns in order, float64, no column
   names; target `obs_tmpc - temp` unrounded (G20); training rows in
   ascending date (G19); `lgb.LGBMRegressor(**LGB_PARAMS).fit(x, y)`
   (G14, G17). Prediction is `temp` plus the model's output.
3. Compare, **exact equality, no tolerance**, with F109's stored
   unrounded values in `data/processed/session63_reserved_confirm_grid.csv`:
   its `final_mae` (`B+D,L,R,T`) and `raw_mae` (raw GFS, GRIB) columns.
   Report each value from both sources in full. (F109 at 4 decimals:
   EGLC 1.0008 and 1.2362; LFPG 1.2369 and 1.4091; DSM 1.4123 and
   1.7043.) The grid holds no test-row count: report the gate's
   test-row count per airport and compare it with the count F109
   records (DECISIONS-archive.md), allowing for the grid's `no_obs`
   column; a difference there is reported, and is a stop only if an MAE
   also differs.
4. If any value differs: report it, and stop. Do not change the fitting
   code to make it pass. If the stored grid does not hold a value
   needed, stop and report.

---

## Step 4: fit and score

`scripts/session97_stagec_cv.py --score`, only after Step 3 passed:

1. For each airport, fold, cycle hour and lead 3 to 24: fit one baseline
   model on that model's training rows (Step 2), exactly as Step 3.2
   fits. 6 x 3 x 4 x 22 = 1,584 fits. Predict its test rows.
2. Score both methods on the same rows (the common row set, D89.5):
   `raw_gfs` (forecast = `temp`, the elevation-adjusted GRIB
   temperature) and `baseline` (`temp` plus the model's output). Error
   is `obs_tmpc - forecast`.
3. Write `data/processed/session97_stagec_cv_scores.csv`: one row per
   airport, fold, cycle hour, lead and method (3,168 rows), with n, MAE
   and mean error, at full precision. Equal content, equal bytes. Check
   that the two methods' n are equal in every cell.
4. In the output file, report at 4 decimals, for both methods:
   - the headline (D89.5) and each airport's pooled MAE;
   - the fold-level MAE (D89.5) and each airport's MAE per fold;
   - the six-airport mean MAE per lead (3 to 24), pooled over folds and
     cycle hours, and the same per cycle hour;
   - for each airport, the leads where the baseline's MAE is not below
     raw GFS's (pooled over folds and cycle hours), if any.
   These are build-choice scores (SPEC 2.5). Do not describe any of them
   as a result, a pass or a fail.
5. Report run time.

---

## Step 5: repeatability and meta

1. Rerun `--score` for EGLC alone into a temporary directory
   (`mktemp -d`) and confirm its rows are byte-equal to EGLC's rows in
   the scores file. Delete the temporary directory. If not equal,
   report it; do not change anything to make it equal.
2. Confirm the 2026-27 guard refuses a valid time of 2026-08-01T00:00
   (no data needed).
3. Write `data/processed/session97_stagec_cv.meta.txt`: what the files
   are; D89's folds, metric and rule (by reference); the input files
   and their SHA-256 (six table files, the training set, the stored
   grid, `session62_reserved_confirm.py`); the script and its SHA-256;
   the two output files' SHA-256; `LGB_PARAMS` as passed; and the
   versions used.

---

## Step 6: records

1. **F139** in DECISIONS.md, after D89, under
   `## <run date>: Session 97 finding: the cross-validation folds, the gate, and the baseline scored`.
   Real findings only: Step 0; D89's line range; the fold counts; **the
   gate result**; the headline, per-airport and fold-level MAEs for
   both methods, and any airport-lead where the baseline is not below
   raw GFS; repeatability; files and SHA-256; the script's SHA-256;
   readings made where this prompt is silent, listed for the owner;
   and a "what this did not do" list (no network; no build choice; no
   setting tuned; no model saved; nothing from 2026-27; no
   non-development airport read; `MLwx-stagec/` and `MLwx-pull/`
   unchanged; no existing script edited; nothing installed; SPEC and
   RESULTS not edited; nothing committed). State in F139's first line
   that its scores are build-choice scores, not results (SPEC 2.5).
   Keep it compact; full tables go in the output file.
2. Save the full real output as `notes/session-97-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended), keeping session 96's structure, updated: D89 fixes the
   folds, metric and rule; the baseline is fit and scored by
   cross-validation (or not), with the gate result; D82.5's choices
   still open, next under D89.6 with the baseline as incumbent;
   F138.8's readings accepted (D89.1), so that open question is
   removed; GFS v17: D89.2 replaces D88.2 as the latest check. STATUS
   must end with: "**Next planning session:** Review session 97. If it
   passed, the owner commits and pushes; then plan session 98: the
   first of D82.5's alternatives against the baseline, under D89.6.
   Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only, in chat and in `notes/session-97-output.txt`.
4. Archive step, per CLAUDE.md. D72, D73, F122, D77 to D89 and F127 to
   F139 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted, and that `MLwx-stagec/`
   and `MLwx-pull/` are unchanged (SHA-256 as F138.4 and the
   inventory). Run `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
