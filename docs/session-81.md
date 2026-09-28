# Session 81 — pre-register the 2026-27 GFS forward test; train and freeze its models

Session 80 recorded the roadmap (D72). D72.5 fixed the design of the
2026-27 forward test and D72.13 set this session to lock it. This session:

1. records the pre-registration, **D73**, before anything else;
2. builds the training set from committed files only;
3. runs a reproduction gate (the new training code must reproduce the
   record exactly);
4. trains and freezes one `B+D,L,R,T` model and one `B` model per airport,
   on all GFS v16 data up to 2026-07-31, and records their SHA-256;
5. records what it did as **F122**, adds one pointer sentence to SPEC 6,
   and does the end-of-session steps.

It writes **no** 2026-27 data-build or scoring script. That is a later
session (D73.8).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 data.** Do not pull, open, read or build any row dated
  2026-08-01 or later. No network calls. The only contact with the two DSM
  files named in D73.10 is a path listing and a SHA-256 of their bytes.
- **The training code refuses any row dated 2026-08-01 or later** (it
  raises, it does not silently drop). This is a guard, not a filter.
- **Do not edit any existing script.** The frozen scripts
  (`session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py`, `session62_reserved_confirm.py`,
  `session77_ksfo_looks.py`) and every other existing script stay as they
  are. You may read them to copy logic into the new script.
- **No tuning, no selection, no variants.** Only the SPEC 8 recipe
  (`B+D,L,R,T`) and plain `B`, with the frozen settings. No other feature
  set, setting, seed or column order.
- **No new score on any year, except the reproduction gate in Step 3**,
  which re-computes recorded figures for verification only and gives no
  verdict. Do not compute any MAE or other error on the frozen models'
  training rows.
- Do not change any earlier verdict or figure.
- Edit `SPEC.md` only as Step 5.2 says. Do not edit `RESULTS.md`,
  `README.md`, `CLAUDE.md` or `PROJECT-INSTRUCTIONS.md`. Write nothing
  under `data/raw/`.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-81.md`. Anything else: stop and report.
2. Read in DECISIONS.md: D62 (in particular D62.7), D71, D72 and F121.
   In DECISIONS-archive.md: D58, F107, F109, D70 and F119.
3. **Find the two A67-15 DSM files** (D62.7): the two tracked DSM files
   covering 2026-08-05..2026-08-15. Use `notes/audit-session-67.md` and
   `git ls-files` to identify them. **Do not open them.** Report each path,
   its size in bytes, its SHA-256, and the commit that added it
   (`git log --diff-filter=A --format=%H -- <path>`). If you cannot find
   exactly two such files, stop and report.
4. Confirm by path check only that `data/models/session81/` does not
   exist, and that no file named `session81_*` exists under `scripts/`,
   `data/processed/` or `notes/`. If any exists, stop and report.

---

## Step 1 — record D73 (before any other edit or any data read)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## 2026-09-27 — Session 81 decision: pre-registration of the 2026-27 GFS forward test (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped. Report the line range you copied.

```
**D73. Owner decision, planning chat (after session 80): the
pre-registration of the 2026-27 GFS forward test (D72.5).** Written at the
start of session 81, before any data was read or any model was fit. No
2026-27 value has been read or scored. Where this entry is more precise
than D72.5, this entry governs; D73.4 amends D72.5's "only file paths may
change".

- **D73.1 What is tested.** SPEC 8's recipe `B+D,L,R,T`, unchanged: the
  same features and transforms (SPEC 8.1), the same column order (SPEC
  8.8 G15), the same frozen LightGBM settings (D21.4/D48.6, lightgbm
  4.7.0, SPEC 8.8 G14, G17), the same target (observation minus
  `temperature_grib_c`, SPEC 8.8 G20). Six airports: EGLC, LFPG, DSM,
  YSDU, RNO and KSFO, each with its own grid point, target hour, lead and
  elevation constant (SPEC 3.4, 4.1, 5.2, 7.2).
- **D73.2 The frozen models.** One `B+D,L,R,T` model per airport, trained
  once on every complete-case row dated 2021-03-24 to 2026-07-31 (all
  GFS v16), in ascending date order (G19), from committed processed files
  only. It is saved as a LightGBM text model file and its SHA-256 is
  recorded in F122. It is never refit. Also frozen, as descriptive rungs
  only: one plain `B` model per airport, trained the same way on the same
  rows; and one mean-bias constant per airport, mean(observation minus
  raw GFS (GRIB)) over the same rows. The training rows keep the
  historical observation pairing (SPEC 4.5's note); new 2026-27 code
  pairs explicitly to the nearest report (SPEC 8.7).
- **D73.3 The test year and its split.** The test year is 2026-08-01 to
  2027-07-31. A target day is in period B if the GFS cycle that forecasts
  it (SPEC 7.2's lead convention) is an operational GFS v17 cycle, and in
  period A otherwise. Any v16.x cycle is period A. The boundary is the
  first operational v17 cycle, taken from NCEP's Service Change Notice and
  confirmed in the archive. Parallel ("para") data is never used. If no
  operational v17 cycle has forecast any day by 2027-07-31, period A is
  the whole year and period B is not run. If anything other than one
  clean switch happens (a rollback, a second version change, mixed
  cycles), stop: the owner decides in writing before any value is scored.
- **D73.4 Inputs after v17 (amends D72.5).** 2026-27 features are built
  with the same logic as the record pipelines, with only their date
  ranges extended (as F107 did for the reserved year); the code itself is
  new (D73.8). For v17 inputs, file paths may change. How a field is
  fetched (message name, level specification, which accumulation window
  is read) may also change, but only if the physical quantity is
  identical: the same variable, level, time window ending at the target
  hour, units and transform. The owner approves each such change. It is
  decided from v17's documentation and the fields themselves, never from
  any 2026-27 error or score. Each change is written into DECISIONS, with
  its evidence, before any period-B value is scored. If any input to `B+D,L,R,T` or to raw GFS
  (GRIB) cannot be built this way, or the 0.25° GRIB2 grid is no longer
  offered, period B is recorded as void (not run). A void period is not
  a fail. The elevation constants (SPEC 5.2) stay frozen, even though
  v17's terrain differs; they apply to raw GFS and the model alike. The
  grid points (SPEC 3.4) and interpolation (SPEC 8.8 G6) are unchanged.
  Nothing is refit, retuned or reselected.
- **D73.5 The bar and the rungs.** The bar is SPEC 5.3, applied per
  airport per period: the frozen `B+D,L,R,T` model's MAE must be lower
  than both raw GFS (GRIB, elevation-adjusted, SPEC 5.2) and persistence.
  Descriptive rungs, never part of the bar: the frozen `B` model and the
  mean-bias reference. The day basis is SPEC 8.5's: raw GFS and the
  models on every complete-case test day; persistence on test days that
  also have a previous-day observation. Missing forecasts or observations
  are dropped and counted (SPEC 2.2). There is no minimum day count. Each
  period's row count is reported against its full expected count; a
  shortfall is reported and does not block the verdict.
- **D73.6 Verdicts.** Each airport gets one PASS or FAIL per period,
  labelled with the period's dates and season. The two periods answer
  different questions (A: does the recipe hold on a new year; B: does the
  v16-trained model survive v17), so they are not combined, and D71.6's
  every-look-must-pass rule does not apply. Nothing is averaged across
  airports (SPEC 5.0). KSFO carries D71.5's framing. The write-up leads,
  in each period, with the smallest bar margin across the six airports.
  No earlier verdict changes.
- **D73.7 Expectations, stated before any value is seen.** Period A:
  `B+D,L,R,T` passes at all six airports. Period B: no expectation is
  stated. Period A will probably be short (a few months of autumn); its
  verdict stands whatever its length, labelled with its dates and season.
- **D73.8 When it is scored.** No 2026-27 value (model prediction error,
  raw-GFS error or persistence error) is computed until its period has
  ended and its observations are in. **Hold rule:** period A is not
  scored until the owner has decided, in writing, whether to pre-register
  a comparison against NBM/NWS MOS on 2026-27 (stage A, D72.7). Once any
  part of 2026-27 is scored, no new test may be pre-registered on it
  (SPEC 2.5). The 2026-27 data-build and scoring scripts are written in a
  later session and committed before any 2026-27 row is built. They
  implement this entry exactly, and SPEC 8.7's build requirements apply
  to them. Until each period is scored, its data is held out for claims
  and no build choice may use it (SPEC 2.5).
- **D73.9 A consequence, accepted.** Period B's data is held out until it
  is scored, after 2027-07-31. So stage F (upgrade policy) cannot use
  live v17 data for any build choice before then without spending period
  B. Before then, its only v17 training data would be NOAA's v17
  retrospective runs, if they are public (D72.3). The design is not
  changed for this.
- **D73.10 The two DSM A67-15 files** (D62.7): the two tracked DSM files
  for 2026-08-05..2026-08-15. Their paths and SHA-256 are recorded in
  F122. They were not opened in session 81. They are not used to build
  or score anything; period A's data is fetched fresh.
- **D73.11 Session 81's plan.** Record this entry; build the training set
  from committed files; pass a reproduction gate (the new training code
  must reproduce F109's and KSFO look B's recorded MAEs exactly); train
  and freeze the models; record F122.
- **D73.12 GFS v17 (planning-chat web search, 2026-09-27, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The SCN is due 30 days before go-live, so
  the earliest go-live is about late October 2026.
```

---

## Step 2 — build the training set (committed files only)

Write one new script, `scripts/session81_freeze_forward_models.py`. Steps
2 to 4 all run from it, with modes (for example `--build`, `--gate`,
`--freeze`). It must follow SPEC 8.7's build requirements where they
apply (reject non-finite values at load and count them; never overwrite
a committed file).

For each airport, assemble every row dated 2021-03-24 to 2026-07-31 with
the G15 columns, the observation and `temperature_grib_c`:
- **EGLC, LFPG, DSM, YSDU, RNO:** stitch the committed processed files the
  record used: the `B` files (sessions 37/40), the v16-window and
  sealed-window feature files (SPEC 8.1), and the reserved-year feature
  files (`session63_reserved_window_with_*`, SPEC 8.1, F107). Take the
  loading and joining logic from `session62_reserved_confirm.py`.
- **KSFO:** `data/processed/session76_ksfo_features.csv` and
  `data/processed/session76_ksfo_observations.csv`, joined as
  `session77_ksfo_looks.py` does. Check their SHA-256 against D70.2
  (`f228301e…c5e9` and `b987dd4f…736c`; full values in
  `docs/session-78.md` Step 0). Mismatch: stop.

Apply D's floor transform (SPEC 8.1) and the complete-case rule (SPEC
8.3). Report, per airport:
- every input file's path and SHA-256;
- the first and last date; confirm the last is on or before 2026-07-31;
- rows per year (Aug–Jul), duplicate dates (must be 0), non-finite values
  rejected, and complete-case rows dropped;
- the calendar days in 2021-03-24..2026-07-31 with no row, as a count,
  with the dates listed if there are 20 or fewer.

Do not fill any gap. Save the assembled set as
`data/processed/session81_training_set.csv` (one file, with a station
column), and report its SHA-256 and row count.

---

## Step 3 — the reproduction gate

Using the **same code path** as Step 4, with only the dates changed, fit
and predict on two recorded folds:
- **F109 fold** (five airports): train 2021-03-24..2024-07-31, test
  2024-08-01..2025-07-31.
- **KSFO look B fold:** train 2021-03-24..2025-07-31, test
  2025-08-01..2026-07-31.

Compute only the `B` and `B+D,L,R,T` MAEs. Compare each, at full
precision, with the recorded values in
`data/processed/session63_reserved_confirm_grid.csv` (F109) and
`data/processed/session78_ksfo_looks_grid.csv` (F119). Print them side
by side. For reference, at 4 dp (SPEC 8.5):

| airport | B | B+D,L,R,T |
|---|---|---|
| EGLC | 1.0861 | 1.0008 |
| LFPG | 1.3285 | 1.2369 |
| DSM | 1.4402 | 1.4123 |
| YSDU | 1.3030 | 1.2643 |
| RNO | 1.4272 | 1.2742 |
| KSFO (look B) | 1.4654 | 1.3830 |

**Pass: all twelve values equal the recorded values exactly.** If any
value differs at all, **stop. Do not run Step 4.** Report what differs
and what you think the cause is, but do not change anything to force a
match. The owner decides.

This gate re-computes recorded figures for verification only (as in
sessions 68a and 73). It gives no verdict and changes none.

---

## Step 4 — train and freeze (only if Step 3 passed)

For each airport, on all its Step 2 rows, fit once:
- the `B+D,L,R,T` model (G15 columns, in order);
- the plain `B` model (the first five G15 columns, in order);
- the mean-bias constant: mean(observation minus `temperature_grib_c`)
  over the same rows, at full precision.

Save under `data/models/session81/`:
- `<AIRPORT>_bdlrt.txt` and `<AIRPORT>_b.txt`, via the booster's
  `save_model` (LightGBM text format);
- `manifest.json`: per airport, the training date range, the row count,
  the mean-bias constant, each model file's SHA-256, the SHA-256 of
  `session81_training_set.csv`, the column list, the settings passed, and
  the Python, numpy and lightgbm versions.

**Reload check:** reload each saved model and confirm its predictions on
its own training rows equal the in-memory model's exactly (maximum
absolute difference 0). Report only that difference, not any error or
MAE.

Report every SHA-256 and the manifest's SHA-256.

---

## Step 5 — records

1. **F122** in DECISIONS.md, after D73, under a dated heading
   `## 2026-09-27 — Session 81 finding: the 2026-27 forward test's frozen models`.
   It records, with real numbers only: Step 0 (git status, the two A67-15
   files' paths, sizes, SHA-256 and adding commits); Step 1 (the D73 line
   range copied); Step 2's per-airport table; Step 3's side-by-side table
   and the gate result; Step 4's SHA-256 values, row counts, mean-bias
   constants, versions and the reload check; and a "what this did not do"
   list (no 2026-27 data, no score beyond the gate, no verdict changed, no
   scoring script written, nothing committed).
2. **SPEC 6, stage B bullet.** Add one sentence at its end: "The 2026-27
   forward test is pre-registered in DECISIONS D73, and its models are
   frozen (F122)." Nothing else in SPEC changes.
3. Save the full real output of this session as
   `notes/session-81-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot. Include: the
   forward test is pre-registered (D73) and its models are frozen (F122);
   the hold rule (D73.8); the GFS v17 carried item (D73.12; re-check each
   planning session); the stage A/B uncertainties still open. It must end
   with: "**Next planning session:** Review session 81. Then draft session
   82: stage A's read-only source probe (D72.13)."
3. Consistency check: re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only.
4. Archive step, per the criterion in CLAUDE.md. Likely candidates: F120
   and F121. D62, D71, D72, D73 and F122 stay live. Report what moved and
   why.
5. Stop and wait for review. Do not commit. Do not write a commit message.
