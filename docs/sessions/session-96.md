# Session 96: D88, the stage C development table and its gate

Session 95 (all 65 months downloaded and checked, F137) is reviewed,
committed and pushed. Stage C's open build choices (D82.5) are made by
time-ordered cross-validation on the six development airports, and
none can be tested until a table exists that holds the record's
features at every cycle and every forecast hour, paired with the hourly
observation. This session builds that table. It fits no model and
computes no score. It:

1. records **D88** (the owner's decisions), before any other edit;
2. makes one small **SPEC 6** edit (Step 2);
3. checks every input against its recorded SHA-256 (Step 3);
4. tests the new radiation (R) and pressure tendency (T) arithmetic on
   its own (Step 4);
5. **builds the development table**: six airports, every cycle, forecast
   hours 0 to 24, the record's features rebuilt from the stored grid
   values, and the hourly observation (Step 5);
6. **gates** it against the committed record at EGLC, LFPG and DSM, lead
   24 (Step 6);
7. writes counts and checks that the build is repeatable (Step 7);
8. records what it found as **F138**, and does the end-of-session steps.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **No network at all.** No GRIB, IEM, GitHub or any other request.
- **Nothing from 2026-27.** Nothing valid after 2026-07-31T23:00 UTC is
  built, and no observation after 2026-07-31T23:59 UTC is read. A guard
  in code refuses both.
- **No model fit and no scores.** No LightGBM call. Compute no error,
  MAE, bias, skill, mean, spread or other statistic of any forecast or
  observation value. Counts only.
- **No value printed**, except: in a gate mismatch, that row's new and
  committed values in full; and in Step 4's tests, the synthetic
  numbers the test itself makes up.
- **Development airports only:** EGLC, LFPG, DSM, YSDU, RNO, KSFO. Read
  no row for any other airport from the points files, and no other
  airport's observation file (D82.6: new airports stay clean).
- **`MLwx-pull/`** (`/Users/zacharyadams/Coding Projects/MLwx-pull/`) is
  read only. Change nothing there.
- **The table** is written to a new folder
  `/Users/zacharyadams/Coding Projects/MLwx-stagec/` (outside the repo,
  beside `MLwx-pull/`). If it already exists, stop and report. Write
  each file to a temporary name there and rename it only when complete;
  never overwrite.
- **Writes.** Only: the new script `scripts/session96_stagec_table.py`;
  the files in `MLwx-stagec/`; the new files
  `data/processed/session96_stagec_dev_table.meta.txt` and
  `data/processed/session96_stagec_dev_counts.csv`;
  `notes/session-96-output.txt`; the SPEC.md edit in Step 2; and the
  DECISIONS.md and STATUS.md edits the steps give. No other file under
  `data/` is created or changed. Do not touch `data/models/`.
- **Do not edit any existing script.** The new script imports from
  `scripts/session86_forward_build.py` and
  `scripts/session92_verify_chunk.py` wherever the arithmetic or
  pairing already exists there (bilinear on the four stored values,
  `derive`, `year_fraction`, `pair_nearest`, `pair_historical`, the
  parsing of SPEC 3.4 and the params CSVs), so it stays identical to
  the gated record code. Only R and T at leads the record never used
  are written new (Step 4).
- Do not edit `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`. Edit `SPEC.md` only as Step 2 says.
- **No installs.** Use what is installed.
- Keep the laptop awake for long steps (D86.5), for example with
  `caffeinate -i`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-96.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D87 and F137, and that
   no D88 or F138 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm `scripts/session96_stagec_table.py`, both new `data/processed/`
   files and the folder `MLwx-stagec/` do not exist. Check SHA-256 of:
   `scripts/session92_verify_chunk.py` (F136), `scripts/session95_check_release.py`
   and `data/processed/session95_pull_inventory.csv` (F137),
   `data/processed/session91_pull_airports.csv` (F133),
   `data/processed/session81_training_set.csv` (F122.3), and
   `scripts/session86_forward_build.py` (F128). Any difference: stop and
   report.
4. Read: D82, D83, D87, F128, F133, F134, F137 in DECISIONS.md; SPEC 3.4,
   4.5, 6, 7.2, 8.1 to 8.3, 8.7 and 8.8; `scripts/session86_forward_build.py`
   and `scripts/session92_verify_chunk.py` in full. Locate (do not yet
   read) the committed hourly observation files and their `.meta.txt`
   for the six development airports under `data/raw/` (the files F131.6
   and F128 used). List them with SHA-256. Report whether, together,
   they cover 2021-03-24T00:00 to 2026-07-31T23:59 UTC at every airport.
   If an airport's files do not cover that window, stop and report.
5. Report free disk space on the volume holding `MLwx-pull/`. Under
   5 GB: stop and report.
6. Print the installed Python and package versions you use.

---

## Step 1: record D88 (before any other edit)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 96 decision: F137 accepted, GFS v17, and the stage C development table (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D88. Owner decisions, planning chat (after session 95): F137
accepted, GFS v17, and the first step on stage C's build choices: the
development table, the curve's baseline, and the rules for features at
every lead.** Written at the start of session 96, before any other
edit. No 2026-27 value has been read or scored.

- **D88.1 F137 accepted.** The owner accepts F137 and all nine F137.11
  readings, including the change to the download step (F137.3).
  Reading 9 (2022-11's 135 retries equal 27 x 5) is the script's
  arithmetic inference; the meta does not record it.
- **D88.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-89 (2 October
  2026, model changes for the RRFS implementation). Correction to
  D87.6: SCN 26-89 was posted on the same day as SCN 26-88, so 26-88
  was not the newest. With 30 days' notice, the earliest go-live is
  about 5 November 2026. PNS 26-29's proposed October 2026 date can no
  longer be met.
- **D88.3 What comes first.** D82.5's build choices need a development
  table: for each development airport (EGLC, LFPG, DSM, YSDU, RNO,
  KSFO), every GFS cycle in the pull and every forecast hour 0 to 24,
  the record's features rebuilt from the stored grid values, and the
  hourly observation at the valid time. Session 96 builds it and gates
  it against the committed record. It fits no model and computes no
  score.
- **D88.4 The curve's baseline.** SPEC 8's recipe `B+D,L,R,T`, applied
  unchanged at each cycle hour and lead: one model per airport, cycle
  hour (00, 06, 12, 18 UTC) and lead, so 100 models per airport, with
  the record's settings, column order and complete-case rule. This is
  the proven method applied at every hour, one well-understood input
  first (D72.2(b)). It is recorded now and fitted later. D82.5's
  alternatives (one model per lead with the cycle hour as an input; one
  model with lead and hour as inputs) are each compared against it by
  time-ordered cross-validation.
- **D88.5 Features at every lead.** The record's definitions, extended:
  (a) Instantaneous fields (temperature, cloud cover, 10 m wind, dew
  point, 850 hPa temperature, sea level pressure) at every lead,
  including f000 (the analysis), by the record's arithmetic
  (bilinear, elevation constant on temperature only, rounding as SPEC
  8.8 G4 and G7).
  (b) R is the mean downward shortwave radiation over the 2 hours
  ending at the valid time. GFS gives A(N), the average over (W, N],
  W = 6 x floor((N-1)/6). If N - W >= 2: R = ((N - W) x A(N) -
  (N - 2 - W) x A(N - 2)) / 2, where the second term is zero when
  N - 2 = W (so R = A(N) at leads 2, 8, 14, 20). This is the record's
  de-accumulation at lead 24. If N - W = 1 (leads 7, 13, 19): R =
  (A(N) + 6 x A(W) - 5 x A(W - 1)) / 2, adding the last hour of the
  previous 6-hour window. R does not exist at leads 0 and 1.
  (c) T is the sea level pressure at lead N minus that at lead N - 3,
  same cycle, in hPa, from the two rounded pressures as the record
  does. At lead 3 it uses the f000 analysis. T does not exist at
  leads 0 to 2.
  (d) Season terms from the valid date, by the record's
  `year_fraction`.
  (e) GFS's 6-hour maximum and minimum 2 m temperature are kept as
  raw columns (bilinear, degrees C, rounded to 3 decimals, no
  elevation constant) for the later daily maximum work. They are not
  features of the baseline.
- **D88.6 Leads 0 to 2.** The complete-case rule stands. Rows at leads
  0 to 2 stay in the table, marked incomplete and counted, never
  filled. A GFS run arrives about 3.5 to 4 hours after its start time,
  so these leads are already in the past when it lands.
- **D88.7 The observation.** At every valid whole hour: the nearest
  usable report within 15 minutes, inclusive (SPEC 4.5, 8.8 G2 and G3,
  the record's `pair_nearest`; a tie keeps the earlier report). The
  same at every airport.
- **D88.8 Where the table lives.** About 1.17 million rows, so it is
  kept outside the repository, in `MLwx-stagec/` beside `MLwx-pull/`.
  The repository holds the script, a meta file with every table file's
  SHA-256, and a counts file. The table is rebuilt exactly from the
  Release and the committed observation files.
- **D88.9 Rules for build choices.** Before any cross-validation score
  is computed, a DECISIONS entry fixes the folds, the metric, and a
  rule of the form "keep the simpler option unless the other wins by
  more than a stated margin". Build choices are never quoted as
  results (SPEC 2.5).
- **D88.10 SPEC 6.** The stage C bullet records that the pull is
  complete and checked (D87, F137), and points to this entry (session
  96, Step 2).
- **D88.11 Sequence.** Session 96: this entry, the SPEC edit, the
  table and its gate. Then, planned: session 97 writes D88.9's entry
  before any score, then fits the baseline and scores raw GFS and the
  baseline per lead by cross-validation. D82.5's comparisons, the daily
  maximum, and bias drift (D81.10(b)) follow, one change at a time.
  Stage C's claim design is fixed at its lock.
```

---

## Step 2: SPEC 6

In SPEC.md section 6, in the stage C bullet, replace exactly

```
Opened in DECISIONS D81; its design is in
  DECISIONS D82.
```

with

```
Opened in DECISIONS D81; its design is in
  DECISIONS D82 and D83. Its GRIB pull for forecast hours 0 to 24 is
  complete and checked (DECISIONS D87, F137). Its next steps are in
  DECISIONS D88.
```

If the old text is not found exactly once, stop and report. Change
nothing else in SPEC. Report `git diff -- SPEC.md`.

---

## Step 3: inputs

1. Check every one of the 195 files in `MLwx-pull/` against
   `data/processed/session95_pull_inventory.csv` (name, bytes,
   SHA-256). Any difference: stop and report.
2. Check the observation files listed in Step 0.4 against the SHA-256
   their `.meta.txt` records, where it does. Report any that records
   none.
3. Read the six development airports' grid points and weights from
   `data/processed/session91_pull_airports.csv`, as the verifier's
   `--gate` does.

---

## Step 4: R and T on their own

Before building, test the new R and T code:

1. **Record leads.** At lead 24 (W = 18) the new R must be the record's
   formula; at lead 26 (native window) it must be A(26). Show that the
   new function's arithmetic, given the same inputs, returns the same
   float as `derive` (F128.3) at lead 24, on a few made-up inputs.
2. **Exact algebra.** Make up a synthetic hourly radiation series for
   one cycle (hours 1 to 24), form each A(N) from it as GFS defines it,
   and check, using exact fractions, that D88.5(b) recovers the true
   2-hour mean at every lead 2 to 24. Also check R is reported missing
   at leads 0 and 1, and T at leads 0 to 2.
3. **T.** On made-up pressures, T at lead 24 equals `derive`'s result.
4. Report each test. A failure: stop and report.

---

## Step 5: build the table

`scripts/session96_stagec_table.py --build`:

1. **Rows.** For each development airport, every (cycle, lead) in the
   pull's plan (imported from `session91_grib_pull.py`, not typed in):
   expected 195,600 rows per airport, 1,173,600 in all. Row order:
   cycle, then lead.
2. **Columns.** `station`, `cycle_utc`, `cycle_hour`, `lead`,
   `valid_utc`; then the GRIB-derived columns with the record's names
   from `session81_training_set.csv` wherever the column exists there
   (temperature, `t2m_raw`, cloud cover, wind speed, dew point, `t850`,
   `dewpoint_depression_t2m_floored`, `lapse_rate_t2_t850`,
   `dswrf_2h_wm2`, `pressure_tendency_3h_hpa`, `season_sin`,
   `season_cos`), plus `tmax2m_c` and `tmin2m_c` (D88.5(e)); then the
   observation `obs_tmpc` (as the record parses it, `float(tmpc)`) and
   `obs_time_utc`; then `uses_whole_file` (true if any message used has
   status "ok (whole file)") and `complete_case` (true only if every
   one of the nine SPEC 8.8 G15 columns and the observation is present).
   Report the full column list and which names came from the record.
3. **Arithmetic.** D88.5. Elevation constants and grid points as the
   record (F128.2), read by the imported parsing, not typed in.
   Rounding as the record. A message whose status is not "ok" or "ok
   (whole file)" gives an empty value; nothing is filled (SPEC 2.2).
4. **Observations.** D88.7, for every valid hour, at every airport,
   from the files of Step 0.4. Non-finite or missing temperatures are
   skipped before the choice (G2). No usable report within 15 minutes:
   empty, counted.
5. **Files.** One gzip file per airport in `MLwx-stagec/`,
   `stagec_dev_<ICAO>.csv.gz`, written so equal content gives equal
   bytes (zero gzip timestamp). Floats written so they read back to the
   identical number. Report each file's rows, bytes and SHA-256.
6. Report the run time.

---

## Step 6: the gate

From the new table (not by recomputing), compare with
`data/processed/session81_training_set.csv` at EGLC and LFPG 12z lead 24
and DSM 18z lead 24, every committed row in the window: every column
the committed set holds that the table also holds. **Exact equality, no
tolerance.**

- For the observation only: the five earlier airports' record used the
  last qualifying report (`pair_historical`, F128.2), not the nearest.
  So for the gate, pair each gated row by the imported `pair_historical`
  and compare that with the committed value. Separately, count the
  gated station-days where the nearest report (the table's value)
  differs from the record's choice. Count only.
- Report per airport and per column: compared, equal, mismatched; and
  committed rows with no table row and the reverse. F137.8 found 5,861
  station-days at lead 24; report against it.
- YSDU, RNO and KSFO use lead 26 in the record, which this table does
  not hold, so they are not gated. Their rows come from the same code.
- **If any value differs, report it in full and stop. Do not change the
  arithmetic to make it pass.**

---

## Step 7: counts and repeatability

1. Write `data/processed/session96_stagec_dev_counts.csv`: one row per
   airport and lead (150 rows), with: rows; rows with each
   GRIB-derived column empty, split by reason (absent by design, lead
   too short for R or T, message not ok); rows with no observation;
   rows using a whole-file message; complete-case rows. Equal content,
   equal bytes. Summarise it in the output file, including complete-case
   rows per airport over leads 3 to 24.
2. Write `data/processed/session96_stagec_dev_table.meta.txt` in the
   style of the positions file's meta: what the table is, where it
   lives, each file's name, rows, bytes and SHA-256, the column list,
   the input files and their SHA-256 (inventory, positions, observation
   files), the script and its SHA-256, and the versions used.
3. **Repeatability.** Rebuild the EGLC file into a temporary directory
   (`mktemp -d`) and confirm it is byte-equal to the one in
   `MLwx-stagec/`. Delete the temporary directory.
4. Confirm the 2026-27 guard: a valid time after 2026-07-31T23 and an
   observation after 2026-07-31T23:59 are each refused (no data needed).

---

## Step 8: records

1. **F138** in DECISIONS.md, after D88, under
   `## <run date>: Session 96 finding: the stage C development table and its gate`.
   Real findings only: Step 0; the SPEC edit; the inputs check; the R
   and T tests; the table (rows, columns, files, SHA-256); **the gate
   result**, and what is not gated; the counts summary; repeatability;
   the new script's SHA-256; readings made where this prompt is silent,
   listed for the owner; and a "what this did not do" list (no network;
   no model fit; no score or statistic; nothing from 2026-27; no value
   printed beyond any gate mismatch and the synthetic tests; no
   non-development airport read; nothing in `MLwx-pull/` changed; no
   file under `data/` changed except the two new files; no existing
   script edited; nothing installed; nothing committed). Keep it
   compact; full listings go in the output file.
2. Save the full real output as `notes/session-96-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended), keeping session 95's structure, updated: stage C's
   development table is built and gated (or not), where it lives, and
   the baseline and feature rules of D88; D82.5's choices still open,
   next after D88.9's entry; F137.11's readings accepted (D88.1), so
   that open question is removed; GFS v17: D88.2 replaces D87.6 as the
   latest check; the SPEC 6 carried note is done. STATUS must end with:
   "**Next planning session:** Review session 96. If it passed, the
   owner commits and pushes; then plan session 97: D88.9's
   cross-validation entry (folds, metric, decision rule) written before
   any score, then the baseline fit and raw GFS per lead. Re-check GFS
   v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only, in chat and in `notes/session-96-output.txt`.
4. Archive step, per CLAUDE.md. D72, D73, F122, D77 to D88 and F127 to
   F138 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted, that `MLwx-pull/` is
   unchanged (195 files, SHA-256 as the inventory), and list
   `MLwx-stagec/`. Run `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
