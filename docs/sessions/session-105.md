# Session 105: two daily-maximum challengers (D99)

Suggested model in Claude Code: Opus (model fitting, scoring and gates). Follow
CLAUDE.md's guardrails: a checkpoint line after each step; stop rather than
work around a failed check; after any compaction, re-read CLAUDE.md, this
prompt and your checkpoints before going on.

## Purpose

Record D99, which accepts F147 and fixes every choice of this session before
any score. Reproduce F147.6's daily-maximum scores. Then judge two
daily-maximum challengers, in a fixed order, against the incumbent under
D89.6 on D98.10's metric: first a daily-maximum model of its own; then a
daily drift correction on top of whichever method is best after the first
test. Add tests, record F148, and archive five settled entries.

Every score here is a build-choice score, never a result (SPEC 2.5). No
2026-27 value is read. No non-development airport's data is read. No
network. The hourly curve is not refitted and not changed.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 (including 2.5) and section 8.8
  (G15, G19, G20).
- `DECISIONS.md` (live) in full.
- Scripts, as needed for the step you are on: `scripts/session104_curve_cv.py`
  (Steps 2 to 4; its `day_cycle`, `local_day`, `usable_day`, `fold_of`, `TZ`,
  `table25_hashes`, `load_table25`), and in `scripts/session97_stagec_cv.py`
  only `load_table`, `fit_predict`, `fold_role`, `mae`, `mean_error`,
  `csv_text`, `fmt`, `write_new`, `FOLDS`, `LGB_PARAMS`, `G15`. In
  `scripts/session100_structure_cv.py` only `print_test`.
- `notes/session-104-output.txt`: only the daily-maximum section (search for
  `DAILY MAXIMUM (D98.10)`), for its full-precision headline line.

## Files this session may create or edit (scope list)

- New script: `scripts/session105_dailymax_cv.py`.
- New data files: `data/processed/session105_dailymax_cv_days.csv`,
  `data/processed/session105_dailymax_cv.meta.txt`.
- New: `notes/session-105-output.txt`.
- Edited: `tests/test_stagec.py` (new cases added; existing cases unchanged),
  `DECISIONS.md`, `DECISIONS-archive.md` (archive script only), `STATUS.md`.
- Untracked already: `docs/sessions/session-105.md` (this file; do not edit).
- Read only: `MLwx-stagec/` (F138's and F147's table files),
  `data/processed/session104_dailymax_days.csv`.

Any other changed or new file is a scope breach: report it, do not hide it.
No existing script is edited; frozen scripts (D62.3(a), D93.8) never. SPEC.md,
RESULTS.md, CLAUDE.md, README.md and `docs/PROJECT-INSTRUCTIONS.md` are not
edited.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-105.md`.
- The last entries in DECISIONS.md are D98 and F147; no D99 or F148 exists in
  either file. None of the new files in the scope list exists.
- SHA-256 equal to F147: `scripts/session104_curve_cv.py`
  (`6dcd8727...`, F147's header), `data/processed/session104_dailymax_days.csv`
  (`65cb6d75...`, F147.7), `data/processed/session104_curve_cv_scores.csv`
  (`69ec86bf...`, F147.7), `data/processed/session104_stagec_f025_048_table.meta.txt`
  (`27622ada...`, F147.2). Compare full values, not these short forms.
- Importing `session104_curve_cv` runs nothing (it checks its own imports'
  SHA-256 at import; that is expected).
- **Archive survey (for D99.13).** Search `scripts/` and `.github/` for any
  code that looks up D47, D73, D77, D79 or F139 by text in a DECISIONS file.
  For each hit report the script, the mode it is reached from, and whether
  it reads DECISIONS.md only or both files. Report in the output file. If a
  hit reads DECISIONS.md only and is reached from stage B's `--build` or
  scoring path (sessions 86 and 87's scripts) or from the pull workflow's
  verify step, stop and report before Step 1: the archive set would break it.
  A hit reached only from a gate that has already passed is reported and
  does not stop the session (D96.3, D98.2).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: all
  pass. Report the count.
- Stop if any of this differs.

## Step 1: record D99

Copy the block between `<<<D99-START>>>` and `<<<D99-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Then make
D99.13's Live index change, except F148's line, which is added at the end of
the session. (DECISIONS.md will be above 80,000 bytes until the archive step;
that is expected.)

<<<D99-START>>>
## 2026-10-11: Session 105 decision: F147 accepted, and two daily-maximum challengers (owner, planning chat)

**D99. Owner decisions, planning chat (after session 104): F147 accepted, and
two daily-maximum build choices under D98.10(g), judged in a fixed order,
with every choice fixed before any score.** Written at the start of session
105, before any other edit. No 2026-27 value has been read or scored.

- **D99.1 F147 accepted,** with all seven F147.8 readings: the correction is
  carried at leads 25 to 48 though it does not help EGLC there (reading 1,
  descriptive only, D98.9); the cross-check fix in session 104's own script,
  with a byte-equal re-run (reading 2); the read-off maximum running low at
  YSDU, RNO and KSFO (reading 3), which motivates this entry; one cycle hour
  per airport (reading 4); readings 5 and 6 as written; and reading 7's
  extra 4 rows at b = 0 in 2024-25, accepted untraced.
- **D99.2 What is tested.** Two challengers to the daily maximum, in this
  order: challenger 1, a daily-maximum model of its own (D82.5, using GFS's
  6-hour maximum, D88.5(e)); then challenger 2, a daily drift correction.
  Each is judged by D89.6 on D98.10(e)'s metric. Test 2 is run whatever test
  1 gives.
- **D99.3 Challenger 1: the daily-maximum model.**
  (a) Days, the cycle c, the observed maximum and folds: D98.10(a), (b) and
  (d), unchanged. H is the set of the day's whole UTC hours, all from cycle
  c (leads 4 to 33).
  (b) Inputs, from the development tables (F138's for leads up to 24, F147's
  for 25 to 48), all from cycle c:
  raw_max: the highest `temperature_grib_c` over H, which is D98.10(f)'s raw
  GFS read-off maximum;
  the peak hour p: the hour in H with the highest `temperature_grib_c`; on a
  tie, the earliest;
  gfs_tmax: the highest `tmax2m_c` over H (D88.5(e): bilinear, no elevation
  constant). Each value is GFS's maximum since its last 6-hour reset, so a
  window may begin a few hours before the day; accepted, the same
  everywhere;
  the other eight G15 columns (SPEC 8.8 G15, every column except `temp`) at
  hour p, as the table holds them (the season terms from p's valid time).
  The features, in this order: raw_max, gfs_tmax, then those eight in G15
  order. Ten features.
  (c) Target: observed maximum minus raw_max. Forecast: raw_max plus the
  model's prediction (the record's form, SPEC 8.8 G20).
  (d) Complete case: a day has inputs only if every hour of H has
  `temperature_grib_c` and `tmax2m_c`, and every one of the eight columns at
  p exists. A test day without inputs has no forecast from this method; it
  is counted and leaves the common day set.
  (e) One model per airport and fold, with the record's settings
  (`LGB_PARAMS`, unchanged; D21.4, D48.6). Training days: a usable observed
  maximum, complete inputs, and the day's last hour valid before the fold's
  T0 (D89.3's rule: only observations known when the first test cycle
  starts). Training days in ascending date (G19). Test days: the fold's days
  (D98.10(d)).
  (f) Only GFS values are inputs. The baseline's and the curve's forecasts on
  training days are in-sample, so neither is an input.
  (g) Nothing is tuned. This feature set and these settings are the only
  version scored.
- **D99.4 Test 1.** Incumbent: the curve's read-off maximum (D98.10(g)).
  Challenger: D99.3. D89.6 on D98.10(e)'s metric. The common day set: days
  with a usable observed maximum and a forecast maximum from raw GFS, the
  baseline, the curve and challenger 1. If D89.6 passes, M is challenger 1;
  otherwise M is the curve's read-off maximum.
- **D99.5 Challenger 2: daily drift.** M plus b, where b is a decaying
  average of M's own daily-maximum errors (observed maximum minus M's
  forecast): after each new error e, b = (1 - w) x b + w x e, w = 0.02
  (D97.4's value, not tuned). One tracker per airport and fold, starting at
  b = 0 at the fold's T0 (D97.7). It is updated by each test day of its fold
  with a usable observed maximum and a forecast from M, in ascending local
  date; a missing day is skipped. No look-ahead: the forecast for a day whose
  cycle is c uses only errors of days whose last hour is valid before c. So
  the newest usable error is normally two days earlier.
- **D99.6 Test 2.** Incumbent: M. Challenger: D99.5. D89.6 on the same common
  day set as test 1. If D89.6 passes, the daily maximum is M plus D99.5's
  correction; otherwise it is M.
- **D99.7 Nothing else.** No other feature set, setting, weight or method is
  scored in session 105. Any later variant is a new build choice, fixed in
  its own entry before its score.
- **D99.8 Reproduction first.** Before any fit: from
  `session104_dailymax_days.csv` (SHA-256 as F147.7), F147.6's per-airport
  MAEs and headline for raw GFS, the baseline and the curve, exactly. Then
  this session's day list (station, local date, cycle, fold, observed
  maximum) equals that file's, and raw_max equals its `raw_gfs_max` on every
  day where both exist. The curve's and the baseline's daily maxima are taken
  from that file; the hourly models are not refitted.
- **D99.9 Accepted consequence.** If challenger 1 is adopted, the daily
  maximum is no longer the highest hour of the curve, so the two can differ.
  This is accepted; the product shows both.
- **D99.10 Descriptive figures, not used by the rules.** Mean error per
  method and airport; challenger 1's training days per airport and fold and
  test days lost for missing inputs; challenger 2's b at the end of each fold
  per airport; MAE per method on F147.6's own day set beside the new common
  set.
- **D99.11 This is not a claim.** Every score here is a build-choice score
  (SPEC 2.5). Nothing from 2026-27 is read.
- **D99.12 Session 105's plan.** This entry; the reproduction; test 1; test
  2; tests; F148; the archive step. SPEC and RESULTS are not edited; the
  daily maximum's outcome goes into them with the next session that edits
  them.
- **D99.13 Live index.** Removed (archived), each settled and still binding
  by number: D47 (raw-data policy), D73, D77 and D79 (stage B's
  pre-registrations and reporting; frozen and gated, F128, F129), and F139
  (no longer the incumbent: D98.8; reproduced by F147.4). Added: D99 and
  F148. After session 105: D82, D88, D89, D93, D97, D98, F147, D99, F148.
<<<D99-END>>>

## Step 2: the reproduction (`scripts/session105_dailymax_cv.py --gate`)

Write `scripts/session105_dailymax_cv.py`. It checks the SHA-256 of
`session104_curve_cv.py` before importing it and uses its functions and those
it exposes from session 97 where they fit (report which). lightgbm is imported
directly (D93.3); the session-48 guard is never imported or called by this
script. Recorded values are constants with a comment naming their entry
(D98.2). Output files are written once and refused if present. Bytecode
writing off.

Inputs: `session104_dailymax_days.csv` (SHA-256 checked); F138's table files
for leads 0 to 24 (`load_table`, SHA-256 checked as session 97 does) and
F147's for 25 to 48 (`load_table25` with `table25_hashes`). `tmax2m_c` is not
in those loaders' output: read it from the same files (after the same SHA-256
check), keyed by (cycle, lead), and say how.

`--gate` runs, in order, and stops on any failure:
1. From the days file alone: per airport and headline MAE of `raw_gfs`,
   `baseline` and `curve` on its common days, equal to F147.6 at 4 decimals,
   and the headline equal at full precision to the line in
   `notes/session-104-output.txt`.
2. Rebuild the day list with session 104's `day_cycle`, `local_day`,
   `usable_day` and `fold_of` from the tables' observations: equal to the
   file's (station, local date, cycle, fold, observed maximum) on every day.
3. raw_max equal to the file's `raw_gfs_max` on every day where both exist,
   exact.

Print counts compared and mismatches (must be 0).

## Step 3: challenger 1 and test 1 (`--score`, first part)

`--score` repeats Step 2's gate first (stop if it fails), then:

- Build challenger 1's inputs (D99.3) for every candidate day from the first
  pull cycle to 2026-07-31. Print per airport: days with complete inputs,
  days without (by reason), and peak-hour ties broken.
- Fit one model per airport and fold (18 fits) with `fit_predict` if it takes
  a general feature vector with the record's target convention; otherwise
  call lightgbm with the same `LGB_PARAMS` and the same target convention,
  and say which. Assert that every training day's last hour is valid before
  T0. Print training days per airport and fold.
- Test 1 (D99.4): print per airport and headline MAE of the four methods on
  the common day set, fold level, mean error, and D89.6's three parts for
  challenger 1 against the curve with `print_test`. Print M.

## Step 4: challenger 2 and test 2 (`--score`, second part)

- Write the daily tracker (D99.5) new, with D97.4's update. Assert that no
  forecast used an error from a day whose last hour is not valid before its
  cycle; count days corrected with b = 0. Print each airport's b at the end
  of each fold.
- Test 2 (D99.6): per airport and headline MAE of M and M plus b on the same
  common day set, fold level, mean error, and D89.6's three parts. Print the
  daily maximum's incumbent after session 105.
- Write `data/processed/session105_dailymax_cv_days.csv`: one row per
  (airport, local day) in a test fold: station, fold, local date, cycle,
  observed maximum, raw_max, gfs_tmax, peak hour's lead, the curve's maximum,
  challenger 1's forecast (or why none), M's forecast, b, challenger 2's
  forecast, and whether the day is in the common set.
- Also print D99.10's descriptive figures.

`--meta` writes `data/processed/session105_dailymax_cv.meta.txt`: inputs,
script and outputs with SHA-256, `LGB_PARAMS` as passed, the feature order,
w, fit counts, run times and versions.

## Step 5: tests (`tests/test_stagec.py`, new cases added)

Offline, standard `unittest`, temporary folders only, a few seconds each.

1. The new script's constants for `session104_dailymax_days.csv`'s and
   `session104_curve_cv.py`'s SHA-256 equal the values in F147, found in
   either DECISIONS file (D98.2).
2. The peak hour on a made-up day: a tie between two hours gives the
   earlier; gfs_tmax is the highest `tmax2m_c` over the hours, not the
   value at the peak hour.
3. Training-day rule: with T0 = 2024-08-01T00:00, a day whose last hour is
   valid at 2024-07-31T23:00 is a training day, and one valid at
   2024-08-01T00:00 is not.
4. The daily tracker on made-up days with error 1.0 each day and daily
   cycles at 18z the evening before each day (EGLC in winter): corrections
   0, 0, 0.02, 0.0396 for the first four days, and the error of the day
   before is never used.

Run the whole suite; all must pass. Report the new total.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **`notes/session-105-output.txt`** begins with a summary of at most 30
  lines, then the checkpoints, then the full output. The end-of-session
  consistency findings go in it too.
- **F148** (at most about 40 lines, D93.10): the reproduction; challenger 1's
  inputs (days with and without inputs) and training days in brief; test 1
  (per airport and headline MAE of the four methods, fold level, D89.6's
  three parts, M); test 2 (MAE of M and M plus b, D89.6's three parts, the
  outcome); the daily maximum's incumbent after session 105; mean error in
  brief; fit count and run time; scripts' and outputs' SHA-256; readings for
  the owner; what was not done. State that these are build-choice scores,
  not results (SPEC 2.5). Then add `- F148: session 105's finding.` to the
  Live index after D99.
- **Archive step:** `python3 scripts/archive_decisions.py --apply --session
  105`. D47, D73, D77, D79 and F139 should move, with any section headings
  that belong to them; report what moved.
- **Size check:** DECISIONS.md under 80,000 bytes; report its size.
  Citations check, scope check.
- **Tests:** run the suite at the end; all must pass.
- **STATUS.md:** current-only snapshot. State the two tests' outcomes and
  the daily maximum's incumbent in one or two lines each, as build-choice
  scores. Hourly incumbent unchanged (the curve). Carry stage B, the claim
  batch, MOSMIX, MMMX, and a new carried item: SPEC 6 and RESULTS 7 get the
  daily maximum's outcome with the next session that edits them (D99.12).
  **Next planning session:** Review session 105. The owner commits and
  pushes (`git commit -F docs/commits/commit-105.txt`) and the planning chat
  syncs Project knowledge. Then plan session 106, the next stage C step.

## What this session must not do

No other daily-maximum variant, feature, setting or weight; no hourly refit
and no hourly build choice; no model saved; nothing from 2026-27; no
non-development airport's data; no network; nothing installed; no existing
script or data file edited; `MLwx-stagec/` and `MLwx-pull*/` unchanged;
SPEC.md, RESULTS.md, CLAUDE.md, README.md and `docs/PROJECT-INSTRUCTIONS.md`
not edited. Nothing committed and no commit message written.
