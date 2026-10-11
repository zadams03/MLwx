# Session 104: the f025 to f048 pull checked, the curve extended to 48 hours, and the daily maximum scored (D98)

Suggested model in Claude Code: Opus (model fitting, scoring and gates). A
long session: follow CLAUDE.md's guardrails (a checkpoint line after each
step; stop rather than work around a failed check; after any compaction,
re-read CLAUDE.md, this prompt and your checkpoints before going on).

## Purpose

Record D98, which fixes every choice of this session before any score.
Download and check the f025 to f048 Release. Build the development table for
leads 25 to 48 and gate it at the three lead-26 airports. Refit the curve at
leads 3 to 24 (it must reproduce F139 and F146 exactly), fit it at leads 25
to 48 (gated against F109), and score it. Score the daily maximum under
D98.10's metric. Add tests, update SPEC section 6 and RESULTS section 7, and
record F147.

Every score here is a build-choice score, never a result (SPEC 2.5). No
2026-27 value is read. No non-development airport's data is read, except the
pull checks of Step 2, which print only per-field minimum and maximum, as
session 95 did. Network only in Step 2.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 (including 2.5), sections 8.1 to
  8.3 and 8.8, and section 6's stage C bullet.
- `DECISIONS.md` (live) in full.
- Archived, by number (`grep -n '^\*\*F137\. '` and so on, then that entry
  only, by line range): F134, F137, F138, F145, F146.
- Scripts, as needed for the step you are on (do not read them all at the
  start): `scripts/session95_check_release.py` (Step 2's model),
  `scripts/session96_stagec_table.py` (Step 3), and
  `scripts/session97_stagec_cv.py`, `scripts/session100_structure_cv.py`,
  `scripts/session103_bias_drift_cv.py` (Steps 4 and 5). Read
  `scripts/session90_airport_check.py` only its `hour_of` and
  `local_day_counts` (about l.437 to 512).

## Files this session may create or edit (scope list)

- New scripts: `scripts/session104_pull_check.py`,
  `scripts/session104_stagec_table_f025_048.py`,
  `scripts/session104_curve_cv.py`.
- New data files: `data/processed/session104_pull_f025_048_inventory.csv`
  and its `.meta.txt`; `data/processed/session104_stagec_f025_048_counts.csv`;
  `data/processed/session104_stagec_f025_048_table.meta.txt`;
  `data/processed/session104_curve_cv_scores.csv`;
  `data/processed/session104_dailymax_days.csv`;
  `data/processed/session104_curve_cv.meta.txt`.
- New test file: `tests/test_stagec.py`.
- New: `notes/session-104-output.txt`.
- Edited: `DECISIONS.md`, `DECISIONS-archive.md` (archive script only),
  `SPEC.md` (Step 7 only), `RESULTS.md` (Step 7 only), `STATUS.md`.
- Untracked already: `docs/sessions/session-104.md` (this file; do not edit).
- Outside the repository: `MLwx-pull-f025-048/` (Step 2 writes the 195
  Release files there) and six new files in `MLwx-stagec/` (Step 3).
  `MLwx-pull/` and F138's six table files in `MLwx-stagec/` are read only.

Any other changed or new file is a scope breach: report it, do not hide it.
No existing script is edited; frozen scripts (D62.3(a), D93.8) never.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-104.md`.
- The last entries in DECISIONS.md are D97 and F146; no D98 or F147 exists
  in either file. None of the new files in the scope list exists.
- SHA-256 equal to the record: `session91_grib_pull.py` (F145, `557e8832...`),
  `.github/workflows/stagec-grib-pull.yml` (F145, `4e0e73cb...`),
  `session92_verify_chunk.py` (its value in F134 or F137; report which),
  `session96_stagec_table.py` (F138), `session97_stagec_cv.py` (F139),
  `session100_structure_cv.py` (F143, `67e709ea...`),
  `session103_bias_drift_cv.py` (F146), `session95_pull_inventory.csv` (F137),
  `session97_stagec_cv_scores.csv` (F139), `session103_bias_drift_cv_scores.csv`
  (F146), and F138's six table files (the values in `session97_stagec_cv.py`'s
  `TABLES`). Compare full values, not the short forms here.
- Importing `session96_stagec_table`, `session97_stagec_cv`,
  `session100_structure_cv` and `session103_bias_drift_cv` runs nothing.
- `MLwx-pull-f025-048/` beside the repo: report whether it exists and what it
  holds. If it holds any file, stop and report (Step 2 expects it absent or
  empty).
- Free disk space on the volume: report it. Stop if under 8 GB (the
  f025 to f048 files and the new table need a few GB at most).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 24
  of 24 pass.
- Stop if any of this differs.

## Step 1: record D98

Copy the block between `<<<D98-START>>>` and `<<<D98-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Then
make D98.14's Live index change, except F147's line, which is added at the
end of the session.

<<<D98-START>>>
## 2026-10-11: Session 104 decision: F146 accepted, D97.1 closed, the f025 to f048 checks, the curve to 48 hours, and the daily maximum's metric (owner, planning chat)

**D98. Owner decisions, planning chat (after session 103): F146 accepted,
D97.1's open item closed, the download and checks of the f025 to f048 pull,
the curve extended to lead 48, the hourly metric over the whole horizon, and
the daily maximum's metric (D89.8), all fixed before any score.** Written at
the start of session 104, before any other edit. No 2026-27 value has been
read or scored.

- **D98.1 F146 accepted,** with its seven readings. Reading 2's wording was
  corrected at the review, before the commit: the gain at KSFO is
  "consistent with D78.2 and D71.4 (KSFO's bias shifting between years)".
- **D98.2 D97.1 closed: scripts that find entries by text.**
  `session92_verify_chunk.py --gate` (local only) and
  `session95_check_release.py` are not edited. Their checks ran and passed
  (F134, F137) and stand. F122 and F133 to F136 are now archived, so those
  lookups no longer resolve and those modes cannot be re-run as they stand.
  This is recorded, not fixed, as D96.3 did for session 86. Session 92's
  other modes, which the workflow's verify step uses, read no DECISIONS
  entry and are unaffected. From now on a script never finds a recorded
  value by searching DECISIONS text: it holds the value as a constant, and a
  test in `tests/` checks the constant against the entry in either
  DECISIONS file.
- **D98.3 The download and checks.** A new script downloads the Release
  `stagec-grib-pull-f025-048` once into `MLwx-pull-f025-048/` beside the
  repository (D95.6) and checks, as session 95 did for the f000 to f024 pull
  (D87, F137): every file equal to its Release size and SHA-256; every
  month's meta as expected, with the pull script's SHA-256 equal to F145's;
  session 92's verifier with `--hours 25-48` (its D84.4 checks, then with
  `--ranges`) on every month; the union of all months equal to the 25-48
  plan (187,768 (cycle, hour) keys, F145.1), with no key in two months;
  status totals, including any "ok (whole file)" messages; a negative test;
  and an inventory file committed. Network only to GitHub's API and the
  Release's download links (and the host they redirect to). The pull-level
  `--gate` is not run (D98.2); D98.4's table gate checks the same values
  and more.
- **D98.4 The table for leads 25 to 48.** For each development airport and
  every (cycle, forecast hour) in the 25-48 plan: D88.5's features and
  D88.7's observation, by session 96's code and rules, written as six new
  files in `MLwx-stagec/`. F138's six files are never changed. Inputs before
  forecast hour 25 (T at leads 25 to 27; R at lead 25, which needs A(24) and
  A(23)) come from the f000 to f024 pull (`MLwx-pull/`, F137). Where that
  pull has no such value (cycles before its first), the feature is empty,
  with reason "outside pull window", and counted. The new builder must
  reproduce F138's rows exactly when run on hours 0 to 24 (Step 3's
  equivalence check). Gate: at YSDU (00z, lead 26), RNO and KSFO (18z, lead
  26), every committed station-day of `session81_training_set.csv` equal in
  every shared column, exact equality, as F138 did at lead 24. This is the
  first stage C gate at these three airports. Observation agreement with the
  record's `obs_c` is counted and reported.
- **D98.5 The curve at leads 25 to 48.** As at leads 3 to 24: D88.4's
  baseline (one model per airport, cycle hour and lead) plus D97's
  correction, with D97.4 to D97.7 unchanged. A tracker uses only errors
  whose valid time is before the forecast's cycle (D97.6). So the newest
  usable error is two days old at leads 25 to 47 and three days old at lead
  48. Folds and rows as D89.3. The fitting code's gate (extends D89.9): from
  the table's rows, F109's raw GFS and `B+D,L,R,T` MAEs at YSDU (00z, lead
  26) and RNO (18z, lead 26), reproduced exactly, as F139.3 did at the other
  three airports. If either differs, and the only difference is in the
  observations (the table's pairing against the record's, SPEC 4.5's
  note), the gate is run again with the record's observations and both
  results are reported; any other difference stops the session. KSFO is not
  in this gate: F109 has no KSFO row, and D98.4 gates its features.
- **D98.6 Reproduction at leads 3 to 24, before any new score.** The refit
  reproduces F139 exactly (every cell's n and MAE, the headline, the
  per-airport n) and F146's correction exactly (every drift cell's n and MAE
  equal to session 103's scores file; headline 1.019044682206963).
- **D98.7 Forecasts on rows with no observation.** Each model also predicts
  test rows whose features are complete but which have no observation; the
  daily maximum needs them (D98.10(c)). Such rows never enter an hourly
  score and never update a tracker (D97.5), and every correction is applied
  to them too. No hourly score changes.
- **D98.8 The hourly metric (amends D89.5).** From this entry, D89.5's
  metric is taken over leads 3 to 48, the product's horizon (D82.2): per
  airport, one MAE pooled over folds, cycle hours and leads 3 to 48; the
  headline and fold level as D89.5. Leads 3 to 24 and 25 to 48 are also
  reported. D89.6 and D89.8 are unchanged. The incumbent for the next hourly
  build choice is the curve, the baseline plus D97's correction (D97.8); its
  scores at leads 3 to 48 are F147's.
- **D98.9 The correction at leads 25 to 48 is carried as decided** (D97.8:
  identically at every lead). Its scores there, with D89.6's three parts
  against the baseline, are descriptive only. If its 25 to 48 headline is
  not lower than the baseline's, that is a reading for the owner; nothing
  changes in session 104.
- **D98.10 The daily maximum's metric (D89.8),** fixed before any
  daily-maximum score.
  (a) The observed maximum, as D82.8. Hourly values by D88.7 (the table's
  pairing) at every whole UTC hour of the local day; the day is usable if
  its usable hours are at least its hours minus 2. Time zones: EGLC
  Europe/London, LFPG Europe/Paris, DSM America/Chicago, YSDU
  Australia/Sydney, RNO and KSFO America/Los_Angeles. A day is used only if
  its last hour is valid on or before 2026-07-31T23:00 UTC.
  (b) Which run. For the local day D starting at UTC time s, the cycle is
  the latest GFS cycle c (00, 06, 12 or 18 UTC) with c + 4 hours <= s; a run
  arrives about 3.5 to 4 hours after it starts (D88.6). So every hour of D
  lies at lead 4 to 33, and each day has one forecast: the "tomorrow's
  maximum" a user would see the evening before. Forecasts for the same day
  from later runs (partly observed already) are a later question.
  (c) The forecast maximum: the highest of the method's hourly forecasts
  from cycle c over every whole hour of D. If any hour has no forecast, the
  day is dropped for that method and counted.
  (d) Folds: a day belongs to the fold of its cycle (D89.3's test rule). A
  day whose cycle is before its fold's T0 is in neither, and counted.
  (e) Metric: MAE of the daily maximum, degrees C, full precision, on the
  common day set (a usable observed maximum and a forecast maximum from
  every method compared). Per airport, pooled over folds; the headline is
  the unweighted mean of the six; fold level as D89.5.
  (f) Methods scored in session 104: raw GFS (`temperature_grib_c`), the
  baseline, and the curve (the baseline plus D97's correction), each read
  off its hourly values. Mean error (observation minus forecast) and the
  cycle hours used are descriptive.
  (g) Later daily-maximum build choices: D89.6 on this metric. The
  incumbent is the curve's read-off maximum. Each challenger (for example a
  model of its own, D82.5, or one using GFS's 6-hour maximum, D88.5(e)) is
  fixed in its own entry before its score. Session 104 makes no
  daily-maximum build choice.
  (h) Hourly values miss a peak between reports, on both sides alike
  (D82.8).
- **D98.11 This is not a claim.** Every score here is a build-choice score
  (SPEC 2.5). Nothing from 2026-27 is read.
- **D98.12 SPEC and RESULTS.** Session 104 updates SPEC 6's stage C bullet
  and RESULTS section 7's roadmap paragraph, with the text in its prompt.
- **D98.13 Session 104's plan.** This entry; the download and checks; the
  table and its gate; the curve's gates and scores; the daily maximum;
  tests; the SPEC and RESULTS edits; F147. The next step is chosen at
  session 105's planning.
- **D98.14 Live index.** Removed (archived): D95 (its work is done; the
  structure it closed is restated in D98.8) and F146 (reproduced and
  restated by F147, D98.6). Added: D98 and F147. After session 104: D47,
  D73, D77, D79, D82, D88, D89, F139, D93, D97, D98, F147.
<<<D98-END>>>

## Step 2: download and check the f025 to f048 pull (D98.3)

Write `scripts/session104_pull_check.py`, modelled on
`session95_check_release.py` (read it; do not edit or import its
DECISIONS-reading functions). It imports `session91_grib_pull.py` (plan,
fields, statuses, `plan_chunk`, `month_cycles`, `expected_messages`) and
calls `session92_verify_chunk.py` as a subprocess, with `--hours 25-48`.
Recorded values it needs (F145's pull-script SHA-256, and anything else) are
constants in the script, each with a comment naming its entry (D98.2).
Modes, each run in turn:

- `--release` (network): the Release's assets against the plan: 195 files,
  three per month (points, manifest, meta) for 2021-03 to 2026-07.
- `--download` (network): as session 95's, into `MLwx-pull-f025-048/`; never
  overwrites or deletes a held file; retries as session 95's.
- `--months` (offline): every month's meta (its arguments and its pull
  script SHA-256 equal to F145's), then the verifier, then the verifier with
  `--ranges`, on every month. Print one line per month, not the verifier's
  full output.
- `--totals` (offline): the union of all months against the full 25-48 plan
  (cycles from 2021-03-22T12, D95.5): 187,768 (cycle, hour) keys; no key in
  two months; status totals (ok, ok (whole file), absent by design, idx
  missing, check failed). Any "check failed" or "idx missing": stop and
  report.
- `--negative` (offline): one copied file with one byte changed fails the
  digest check; the totals check with one month's manifest left out fails.
  Copies only, in one temporary directory, deleted at the end.
- `--inventory`: writes `data/processed/session104_pull_f025_048_inventory.csv`
  (one row per asset: name, bytes, SHA-256) and its `.meta.txt`. Refuses if
  either exists.

Stop on any failed check. If a download fails three times, stop and report
(the owner may resume it); do not change the script's network terms.

## Step 3: the table for leads 25 to 48 (D98.4)

Write `scripts/session104_stagec_table_f025_048.py`. It imports
`session96_stagec_table.py` and uses its functions unchanged wherever they
fit (`r_inputs`, `r_value`, `t_inputs`, `t_value`, `load_obs`,
`nearest_obs`, `fmt`, the column lists, the reasons, the guards, and so on;
report which). It reads the six development airports' rows only, from
`MLwx-pull-f025-048/` and, for inputs before forecast hour 25, from
`MLwx-pull/`. Same columns, same column order and same row rules as F138's
files; rows in cycle, then lead order. Output names
`stagec_dev_f025_048_<ICAO>.csv.gz` (ICAO as in F138's names), written to
a temporary name and linked, never overwriting. SHA-256 of F138's six files
checked before and after the build. Modes:

- `--inputs`: every 25-48 pull file against the new inventory, and every
  f000 to f024 file read against session 95's inventory.
- `--equiv`: the new builder, run on hours 0 to 24 for EGLC and RNO, month
  2022-01, in memory, gives rows byte-equal to those rows of F138's files.
  If not, stop.
- `--build`: the six files. Print per airport: rows (against the plan's
  count), complete-case rows, and empty cells by column and reason.
- `--gate`: at YSDU 00z lead 26, RNO and KSFO 18z lead 26, every committed
  station-day of `session81_training_set.csv` (by station and target date)
  equal in every shared column, exact equality. Print counts compared,
  mismatches (must be 0) and rows not found. Count the days where the
  table's observation differs from `obs_c`. If any feature mismatch: stop.
- `--records`: rebuild in memory and check byte-equality with the written
  files; rebuild one airport (DSM) into a `mktemp -d` directory and check it
  byte-equal, then delete the directory; write the counts file and the meta
  file (inputs, script and every output with SHA-256).

## Step 4: the curve's gates (`scripts/session104_curve_cv.py --gate`)

Write `scripts/session104_curve_cv.py`. It checks the SHA-256 of sessions
97, 100 and 103's scripts before importing them, and uses their functions
where they fit (`fit_predict`, `fold_role`, `LGB_PARAMS`, the tracker from
session 103, `d89_6`, and so on; report which). lightgbm is imported
directly (D93.3); the session-48 guard is never imported or called by this
script (D90.1). Output files are written once and refused if present. Bytecode
writing off. It loads F138's table (leads 3 to 24) and the new table (leads
25 to 48), each file checked against its SHA-256 (F138.4; the new files
against this session's meta).

The tracker is session 103's, unchanged; its self-check is extended: daily
cycles, errors 1.0 each day: at lead 47 corrections 0, 0, 0.02, 0.0396; at
lead 48 corrections 0, 0, 0, 0.02.

`--gate` runs, in order, and stops on any failure:
1. The tracker's self-check (session 103's four cases plus the two above).
2. D98.6: fit the baseline at leads 3 to 24 (1,584 fits) and the
   correction; F139 exact (cells 3,168 of 3,168, headline 2 of 2, n 6 of 6);
   F146 exact (every drift cell's n and MAE equal to session 103's file,
   headline 1.019044682206963).
3. D98.5's fitting gate at YSDU and RNO, with session 97's gate windows
   (`GATE_TRAIN`, `GATE_TEST`) on the training set's (station, target date)
   keys: raw GFS and `B+D,L,R,T` MAE equal to
   `session63_reserved_confirm_grid.csv`'s `raw_mae` and `final_mae`, exact.
   Follow D98.5 if either differs.

## Step 5: score the curve and the daily maximum (`--score`, `--meta`)

`--score` repeats Step 4's gates 1 and 2 first (stop if either fails), then:

- Fit the baseline at leads 25 to 48 (1,728 fits), predicting every test row
  with complete features (D98.7). Run the trackers (D98.5). Assert that no
  row used an error whose valid time is not before its cycle, and count rows
  corrected with b = 0.
- Hourly scores, methods `raw_gfs`, `baseline`, `curve` (the corrected
  forecast; it is session 103's `drift`), leads 3 to 48: per (method,
  airport, fold, cycle hour, lead) cell n, MAE and mean error, written to
  `data/processed/session104_curve_cv_scores.csv` with session 103's
  columns. Print per airport MAE and the headline for leads 3 to 48, 3 to 24
  and 25 to 48, and fold level for 3 to 48. Print D89.6's three parts for
  the curve against the baseline at leads 25 to 48, labelled descriptive
  (D98.9). Print the six-airport MAE per lead 25 to 48 for each method.
- The daily maximum (D98.10): for each airport and local day in a test fold,
  the observed maximum (or why none), its cycle, and each method's forecast
  maximum (or why none). Write one row per (airport, local day) to
  `data/processed/session104_dailymax_days.csv`: station, fold, local date,
  hours in the day, usable hours, observed maximum, cycle, the three
  forecast maxima, and whether the day is in the common day set. Cross-check:
  each airport's usable-day count over its local days, computed again with
  session 90's `hour_of` and `local_day_counts` rule on the same reports,
  must agree; if session 90 cannot be imported offline, reproduce that rule
  in the script and say so. Print, per airport and headline: days in the
  common set, MAE of the three methods, fold level, mean error, and the
  cycle hours used (counts). Days dropped, by reason.
- No build choice is made. Print D98.10(g)'s incumbent.

`--meta` writes `data/processed/session104_curve_cv.meta.txt`: inputs,
script and outputs with SHA-256, `LGB_PARAMS` as passed, w, fit counts, run
times and versions.

## Step 6: tests (`tests/test_stagec.py`)

Offline, standard `unittest`, writing only to temporary folders, a few
seconds each (D95.8). Cases:

1. `session104_pull_check.py`'s F145 pull-script constant equals the value
   in F145, found in either DECISIONS file (D98.2).
2. D98.10(b)'s run for a local day, by hand: EGLC 2024-01-15: cycle
   2024-01-14T18, leads 6 to 29. EGLC 2024-07-15: cycle 2024-07-14T18, leads
   5 to 28. EGLC 2024-03-31 (23 hours): cycle 2024-03-30T18, leads 6 to 28.
   EGLC 2024-10-27 (25 hours): cycle 2024-10-26T18, leads 5 to 29. DSM
   2024-01-15: cycle 2024-01-15T00, leads 6 to 29. YSDU 2024-01-15: cycle
   2024-01-14T06, leads 7 to 30. RNO 2024-01-15: cycle 2024-01-15T00, leads
   8 to 31.
3. D98.10(a)'s usable rule: a 24-hour day with 22 usable hours is usable and
   with 21 is not; a 23-hour day needs 21; a 25-hour day needs 23.
4. The tracker at leads 47 and 48 (Step 4's two cases).

Run the whole suite; all must pass. Report the new total.

## Step 7: SPEC section 6 and RESULTS section 7 (D98.12)

In `SPEC.md`, section 6's stage C bullet, these four lines (exactly once; if
not, stop and report)

```
  complete and checked (DECISIONS D87, F137). Its development table and
  baseline are set in DECISIONS D88, and the rules for its build choices
  in DECISIONS D89. Its claim is judged on new airports only, drawn by
  the rule in DECISIONS D82.7.
```

are replaced by

```
  complete and checked (DECISIONS D87, F137). Its development table and
  baseline are set in DECISIONS D88, and the rules for its build choices
  in DECISIONS D89. Its structure is the baseline, one model per airport,
  cycle hour and lead (DECISIONS D95.2), plus a correction for drifting
  bias (DECISIONS D97, F146). Its pull for forecast hours 25 to 48 is
  complete and checked, the curve runs to 48 hours, and the daily
  maximum's metric is fixed (DECISIONS D98, F147). Its claim is judged
  on new airports only, drawn by the rule in DECISIONS D82.7.
```

In `RESULTS.md`, section 7's roadmap paragraph, these four lines (exactly
once)

```
  quoted as results (SPEC 2.5). So far the curve keeps the proven recipe
  as one model per airport, run time and lead; two pooled structures were
  tested and not adopted (DECISIONS D94, F143). Next come forecast hours
  25 to 48, a correction for drifting bias, and the daily maximum. Stage
```

are replaced by

```
  quoted as results (SPEC 2.5). The curve keeps the proven recipe as one
  model per airport, run time and lead; two pooled structures were tested
  and not adopted (DECISIONS D94, F143). A correction for drifting bias, a
  running average of the curve's own recent errors, was adopted (DECISIONS
  D97, F146). The curve now runs to 48 hours ahead, and the daily maximum,
  read off the curve, has a fixed way of being scored (DECISIONS D98,
  F147). Stage
```

and, in the closing note, `and after session 101 (DECISIONS D95).` becomes
`and after session 101 (DECISIONS D95) and after session 104 (DECISIONS
D98).` (on one line, as the original). Nothing else in either file changes.
Do this step after F147 is recorded. Put both `git diff`s in the output file.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **F147** (at most about 40 lines, D93.10): the pull checks (files, plan
  keys, status totals, inventory SHA-256); the table (rows, complete-case
  rows, the equivalence check, the gate and observation agreement, the six
  files' SHA-256 in brief or by pointer to the meta); the gates of Step 4;
  one compact hourly table (per airport and headline for leads 3 to 48, 3
  to 24 and 25 to 48, three methods); D89.6's three parts at 25 to 48
  (descriptive); the daily maximum (days per airport, MAE of the three
  methods per airport and headline, fold level, mean error in brief, days
  dropped); fit counts and run times; scripts' and outputs' SHA-256; readings
  for the owner; what was not done. State that these are build-choice
  scores, not results (SPEC 2.5). Then add `- F147: session 104's finding.`
  to the Live index after D98.
- **Archive step:** `python3 scripts/archive_decisions.py --apply --session
  104`. D95 and F146 should move; report what moved.
- **Tests:** run the suite at the end; all must pass.
- **STATUS.md:** current-only snapshot. State what was checked and built,
  the curve's scores at leads 3 to 48 and the daily maximum's in one or two
  lines each, as build-choice scores; that D97.1 is closed (D98.2); that the
  incumbents are the curve (hourly) and its read-off maximum (daily). Carry
  stage B, the claim batch, MOSMIX and MMMX. **Next planning session:**
  Review session 104. The owner commits and pushes (`git commit -F
  docs/commits/commit-104.txt`) and the planning chat syncs Project
  knowledge. Then plan session 105, the next stage C step (D98.13).
- Size check (DECISIONS.md under 80,000 bytes), citations check, scope
  check. Report the sizes of `MLwx-pull-f025-048/` and the six new table
  files.

## What this session must not do

No build choice: no other weight, structure, feature, setting or daily-
maximum method tried or selected; no model saved; nothing from 2026-27; no
non-development airport's observation; no network outside Step 2, and no
GRIB request at all; nothing installed; no existing script or data file
edited (sessions 92 and 95's scripts included, D98.2); F138's table and
`MLwx-pull/` unchanged; SPEC.md and RESULTS.md edited only as Step 7 says;
CLAUDE.md, README.md and `docs/PROJECT-INSTRUCTIONS.md` not edited. Nothing
committed and no commit message written.
