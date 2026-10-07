# Session 73 — clean-room rebuild of F109 at RNO, part 2: fit, score, compare (D64)

## Purpose

This is part 2 of the pre-registered clean-room rebuild (DECISIONS D64). Session 72
(F112) rebuilt RNO's observation, feature and persistence tables from the docs alone,
into `data/rebuild/session72/`. This session does four things with those tables:

1. It fits the F109 models from the docs alone.
2. It scores the three rungs and the models.
3. It checks the rebuild's own fit determinism.
4. Only as the final step, it compares every stage with the record under D64.4.

**Standing rules (D64). These are not negotiable:**
- This is a verification only. It cannot change any verdict, claim or figure on record
  (D64.1).
- The reserved year (2024-08-01 to 2025-07-31) stays spent. It is scored only to
  reproduce F109.
- Nothing is tuned, selected, fixed, or re-run to pass (D64.5). Every run in this session
  is declared below, before any comparison.
- A mismatch is reported in full, not fixed. The owner triages it in a later session.
- The clean-room rule (D64.3) holds for Steps 1–4. It lifts only at Step 5.

---

## Allowed inputs, and the file log

**Steps 1–4 (clean room)** may read these files only:
- CLAUDE.md, SPEC.md, STATUS.md, DECISIONS.md, DECISIONS-archive.md.
- The session 72 rebuild tables in `data/rebuild/session72/`, read-only.

They must not read, import or copy anything under `scripts/`, `data/processed/` or
`notes/`. They must not use git to view those paths.

**Step 5 (comparison)** may read anything it needs to find the record.

**File log.** Log every file opened, in every step, with its path and the step number.
Put the log in the output file as two lists: clean room, and comparison.

**No network is needed.** Do not pull any data.

**New code must follow SPEC 8.7's build requirements (D62):**
- Reject non-finite values at load. Drop them and count them.
- Write only to new paths, and refuse to overwrite an existing output file.

---

## Pre-declared runs (fixed now; neither variant is "chosen")

### Variants

- **Variant P (primary).** Use the session 72 tables exactly as built:
  - `t2m_raw` rounded (G4 choice).
  - RNO constant 2.0436 (G5 choice).
  - L and D as stored.
- **Variant G4-alt.** Identical to P in every respect except one: L and D are
  re-derived from `t2m_raw_from_full`.
  - `lapse_rate_t2_t850 = round(t2m_raw_from_full − t850, 3)`
  - `dewpoint_depression_t2m = round(t2m_raw_from_full − dew_point_2m, 3)`
  - The floor at 0 is applied at model time, as in P.
  - Use the stored rounded `t850` and `dew_point_2m`, which is G7's choice.
  - B's forecast temperature, the target, and the raw-GFS rung stay the same as in P.
  - If any column needed for this is missing from the session 72 tables:
    - Record it.
    - Do not run G4-alt.
    - Do not rebuild it from GRIB.

There is **no G5 variant**. G5 is examined only diagnostically, in Step 5.

### Fits

There are three distinct fits. B does not use L or D, so it is the same under both
variants.
- **B**: the 5 columns of SPEC 8.2.
- **B+D,L,R,T, variant P**
- **B+D,L,R,T, variant G4-alt**

Use the train window 2021-03-24 to 2024-07-31 and the test window 2024-08-01 to
2025-07-31. Apply the complete-case rule of SPEC 8.3. F112's expected counts are:
- n_train 1,222
- n_test 365
- persistence n 365

Report the actual counts.

### Rungs

Score these on the test window:
- **Raw GFS**, which is the elevation-adjusted GRIB temperature (SPEC 5.2), on every
  test day.
- **Persistence**, on test days that have a previous-day observation (SPEC 8.5,
  D58 item 6).
- **Each fitted model**, on every test day.

---

## Step 1 — Write down the fit recipe from the docs

From SPEC and DECISIONS / DECISIONS-archive, write out the following. Cite a source
for each item.

- **The LightGBM settings** (D21.4, D48.6). List every parameter. Record the library,
  Python and numpy versions in use.
- **The target and the prediction.**
  - The residual definition (SPEC 4.2, D48.1).
  - How a predicted residual becomes a corrected forecast.
  - What the MAE is computed on.
- **The exact feature columns and their order** for B and for B+D,L,R,T.
- **D's floor.**
- **The complete-case rule.**
- **The MAE definition and rounding.**

**Record each gap as a finding.** Any setting or detail the docs leave unstated is a
gap. Likely examples:
- the random seed
- deterministic or threading flags
- column order
- the number of boosting rounds, if not stated

For each gap:
- Number it, continuing from session 72: G14, G15, and so on.
- State the choice made and the alternatives.
- For an unstated LightGBM parameter, use the library default and say so.
- Do not choose any setting with the record in mind.

Stop only if no reasonable reading exists.

## Step 2 — Fit and score, clean room

Write a new script, `scripts/session73_fit_score.py`. It is offline and imports no
other project script.

**Fitting:**
- Load the session 72 tables. Check their row counts: 1,591 rows each, 1,226 train and
  365 test.
- Apply the complete-case rule and the D floor.
- Fit the three models.

**Outputs.** Write to a new folder, `data/rebuild/session73/`:
- Per-day test predictions for every model, at full precision. Include the
  corrected-forecast column and the residual column.
- Per-day raw-GFS and persistence values.
- A metadata file containing:
  - the settings
  - the versions
  - the feature order
  - the row counts
  - the dropped-row dates with a reason for each
- An MAE table giving each MAE unrounded and at 4 decimals.

## Step 3 — Fit determinism, clean room

Fit each of the three models a second time, in a separate process run of the script.

Compare the two runs' test predictions for exact float equality. Report:
- the number of rows that are identical
- the maximum absolute difference

This check is pre-declared. It is not a re-run to pass. Both runs are reported whatever
they show.

## Step 4 — Seal the rebuild results

Before opening any record file:
- Print the full MAE table for the three rungs and three models, unrounded and at
  4 decimals.
- Print the SHA-256 of every file in `data/rebuild/session73/`.

These numbers are fixed from this point on.

Do not interpret the MAEs. Do not state skill, margins, or anything about the bar.

## Step 5 — Compare with the record (the clean room lifts here)

Write a new script, `scripts/session73_compare.py`. It is the only code in this session
that opens `scripts/`, `data/processed/` or `notes/`.

**First**, re-check the SHA-256 of every Step 4 file and confirm that none has changed.

### What to compare

Find the committed record files behind F109 at RNO, and name each file used.

Compare the stages of D64.4, **all of them, even after a mismatch**:

1. Observations and targets: the per-day observed value, report time and residual.
2. Pairing and the day set.
3. Each feature column:
   - B's five columns.
   - L, D, T and R.
   - Where recorded: their inputs `t2m_raw`, `t850`, `dew_point_2m`, the PRMSL and
     PRES values, and DSWRF.
4. The complete-case row set and counts.
5. Raw-GFS values and persistence values.
6. Model predictions, where recorded.
7. Each MAE, against F109's figures: raw GFS 1.6135, persistence 2.7563, B 1.4272,
   B+D,L,R,T 1.2742.

Stages 3 and 7 are run for Variant P and for Variant G4-alt separately. B is shared by
both variants.

### Match rule

The match rule is exact at the recorded precision, with no tolerance:
- Round the rebuild value to the record's stored precision, then test for equality.
- If the rebuild stores fewer decimals than the record, compare at the coarser of the
  two and say so.

### What to report for each stage

- n compared
- n matched
- n mismatched
- the maximum absolute difference
- the first 20 mismatches, printed with their dates

Write every mismatch to a CSV under `data/rebuild/session73/comparison/`.

### Categorise each mismatch

- **Data**: an input to that stage differs.
- **Fit determinism**: every input to that fit matches, but the output does not
  (D64.4).
- **Not comparable**: no record exists for it, or the precision differs, or the span
  differs.

### Diagnostics (report only — do not fix, re-run or adopt)

- **G4.** For any L or D mismatch, do the mismatched rows fall on the 655 rows where
  the two `t2m_raw` variants differ? State which variant, if either, matches the
  record. This is a fact about the record, not a choice.
- **G5.** For any mismatch in B's temperature, the target, or raw GFS, is it
  consistent with 2.0436 against 2.04356932? That is, does it look like a shift of
  about 0.00003 before rounding? Show the check.
- **Session 72's clean room.** Search `notes/session-72-output.txt`'s read log for
  any path under `scripts/`, `data/processed/` or `notes/`. Check specifically for
  any params CSV. Report the result, and give the params CSV's path if it was read.
  A breach is recorded as a finding, not fixed.

---

## Scope limits

Do **not**:
- Edit SPEC.md, RESULTS.md, README.md or CLAUDE.md.
- Change any existing file under `data/raw/`, `data/processed/`, `scripts/` or
  `data/rebuild/session72/`.
- Delete any file.
- Pull any data.
- Fill in any value.

The new files are:
- the two scripts
- `data/rebuild/session73/`
- `notes/session-73-output.txt`

The only existing files edited are DECISIONS.md and STATUS.md.

Anything else that looks wrong is logged as an open question, not fixed.

Do not paste full tables into chat. Summarise them, and point to the files.

---

## End-of-session steps

1. **Output file.** Write the full real output of Steps 1–5 to
   `notes/session-73-output.txt`. Include the file log and every gap. Paste the key
   real numbers into chat: counts, the sealed MAE table, determinism, and the
   per-stage comparison summary.
2. **F113.** Append **F113** to DECISIONS.md, structured like F112:
   - F113.1: the recipe and gaps G14 onward.
   - F113.2: the sealed rebuild results.
   - F113.3: determinism.
   - F113.4: the stage-by-stage comparison, for both variants.
   - F113.5: the G4 and G5 diagnostics.
   - F113.6: the clean-room log, including the session 72 read-log check.
   - F113.7: what this did not do.

   State plainly that F113 changes no verdict, claim or figure (D64.1). Use no verdict
   or skill language.
3. **STATUS.md.** Overwrite STATUS.md as a pruned, current-only snapshot. End it with a
   "Next planning session" line:
   - If there is any mismatch or breach: review F113, and the owner triages the
     mismatches under D64.5.
   - If there is none: review F113, close D64, and return to Q30.
4. **Consistency check.** Re-read SPEC, STATUS and DECISIONS. Report any disagreement,
   any duplicated heading, and any entry out of order. Report only; do not fix.
5. **Archive step.** Do not archive D64, F112 or F113; they stay live until the owner
   triages. Apply the normal criterion to anything else.
6. **Commit message.** Write out a suggested commit message. **Do not commit, add or
   push.** Stop and wait for review.
