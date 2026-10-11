# Session 103: bias drift, a decaying-average correction against the baseline (D97)

Suggested model in Claude Code: Opus (model fitting and a build choice).

## Purpose

Record D97, which fixes every choice of the bias-drift test before any
score. Check that the baseline still reproduces F139 exactly. Score one
challenger, the baseline plus a decaying-average correction of its own recent
errors, against the baseline under D89.6, and record F146. Also add one line
to `docs/PROJECT-INSTRUCTIONS.md` section 8 (D97.3).

Every score here is a build-choice score, never a result (SPEC 2.5). No
2026-27 value is read. No non-development airport's data is read. No
network call.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 (including 2.5) and sections 8.1
  to 8.3 and 8.8 (the recipe, settings, column order G15 and row order G19).
- `DECISIONS.md` (live) in full. It holds D88, D89, F139, D95 and D96, which
  this session depends on.
- Archived, by number (`grep -n '^\*\*D78\. '` and so on, that entry only):
  D78 (D78.2), D81 (D81.10), F143.
- `scripts/session100_structure_cv.py` in full (this session imports from
  it), and in `scripts/session97_stagec_cv.py` only `load_table`,
  `fold_role`, `fit_predict` and the constants block (about l.60 to 140).

## Files this session may create or edit (scope list)

- New: `scripts/session103_bias_drift_cv.py`,
  `data/processed/session103_bias_drift_cv_scores.csv`,
  `data/processed/session103_bias_drift_cv.meta.txt`,
  `notes/session-103-output.txt`.
- Edited: `DECISIONS.md`, `DECISIONS-archive.md` (archive script only),
  `docs/PROJECT-INSTRUCTIONS.md` (Step 2 only), `STATUS.md`.
- Already modified, not by this session: `docs/commits/commit-102.txt` (the
  planning chat removed two lines after session 102's commit; do not edit).
- Untracked already: `docs/sessions/session-103.md` (this file; do not edit).

Any other changed or new file is a scope breach: report it, do not hide it.
`MLwx-stagec/`, `MLwx-pull/` and `MLwx-pull-f025-048/` are read only. Frozen
scripts (D62.3(a)) are never edited, and no existing script is edited.

---

## Step 0: preflight

- `git status --porcelain` shows only ` M docs/commits/commit-102.txt` and
  `?? docs/sessions/session-103.md`.
- The last entries in DECISIONS.md are D96 and F145; no D97 or F146 exists
  in either file (`grep -c '^\*\*D97\. '` and the same for F146). None of the
  new files exists.
- SHA-256 equal to the record: `scripts/session97_stagec_cv.py`
  (`987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91`, F139),
  `scripts/session100_structure_cv.py`
  (`67e709ea0925d84b4e257c44c5a95211f46a5ff5443408d7c526dbffb28d6957`, F143),
  `data/processed/session97_stagec_cv_scores.csv`
  (`5604ccd16118fe772cd24a7be83b36ee62e500c78b3ed5bf55c76ed4e78d9d76`).
- Confirm that importing `session100_structure_cv` runs nothing (its work
  sits behind `if __name__ == "__main__"`), and that its `score_airport(st,
  ["baseline"], timer)` returns, per (fold, cycle hour, lead) cell, `obs`,
  `raw`, `cycles` and `baseline` lists in ascending cycle time. If either is
  not so, stop and report.
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 24 of
  24 pass.
- Stop if any of this differs.

## Step 1: record D97

Copy the block between `<<<D97-START>>>` and `<<<D97-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Then
make D97.12's Live index change, except F146's line, which is added at the
end of the session.

<<<D97-START>>>
## 2026-10-11: Session 103 decision: F145 accepted, the f025 to f048 pull, the commit history, and the bias-drift test (owner, planning chat)

**D97. Owner decisions, planning chat (after session 102): F145 accepted,
the f025 to f048 pull run, the commit history rewritten, and every choice of
the bias-drift test (D78.2, D81.10(b)), fixed before any score.** Written at
the start of session 103, before any other edit. No 2026-27 value has been
read or scored.

- **D97.1 F145 accepted,** with its three readings. Reading 1 stays open:
  `session92_verify_chunk.py --gate` (local only) and
  `session95_check_release.py` still look up F122.3 and F133 to F136 in
  DECISIONS.md by text, and session 95's script is fixed to the 0-24
  Release. Neither is used by the workflow. Both are dealt with when session
  104, which downloads and checks the f025 to f048 pull, is planned.
- **D97.2 The f025 to f048 pull (D96.5), run by the owner on GitHub
  Actions.** First `hours` = `25-48` for 2022-01 alone: the verify step
  printed `RESULT: PASS`, and the owner checked the new Release
  `stagec-grib-pull-f025-048` (title, notes and three files). Then
  2021-03..2026-07: the Release holds 195 files, three for each of the 65
  months (owner's count, 2026-10-10). The workflow publishes a month only
  after its verify step (D84.4) passes. The files have not been downloaded
  or checked together; that is session 104's.
- **D97.3 Commit history.** Some commit messages (sessions 73, 101 and 102)
  ended with `Co-Authored-By` and `Claude-Session` lines, which GitHub reads
  as a co-author. On 2026-10-09 the owner removed those lines from every
  commit message on `main` (`git filter-branch --msg-filter`) and
  force-pushed. Commit IDs from session 73 onward changed; no file's content
  changed. Commit messages never include such lines; PROJECT-INSTRUCTIONS.md
  section 8 says so from session 103.
- **D97.4 What is tested.** One challenger. For every test row, its forecast
  is the baseline's forecast plus b, where b is a decaying average of the
  baseline's own recent errors (observation minus baseline forecast). After
  each new error e: b = (1 - w) x b + w x e, with w = 0.02. The weight is
  NOAA's operational value for NAEFS bias correction (about a 50-day memory;
  Cui, NCEP, "Decide to use 2% (~ 50 days)"; planning-chat web check
  2026-10-11, not checked by this session). It is fixed in advance, not
  tuned, and no other weight or method is tried.
- **D97.5 One tracker per airport, fold, cycle hour and lead,** the same
  cells as the baseline's models. A tracker is updated only by its own
  cell's test rows that are scored (complete case, with an observation), in
  ascending valid time. A missing day is skipped: the update counts errors,
  not calendar days. Errors are always the baseline's, never the corrected
  forecast's.
- **D97.6 No look-ahead.** The forecast from the cycle starting at time c
  uses only errors whose valid time is before c. The observation is within
  15 minutes of its valid whole hour (D88.7), so it was reported at least 45
  minutes before c. So at lead n, the newest usable error is from the cycle
  one day earlier for n up to 23, and two days earlier for n = 24.
- **D97.7 Start of each test year.** Every tracker starts at b = 0 at its
  fold's T0 (D89.3). Errors on training rows are in-sample and are never
  used. This handicaps the challenger early in each fold; it is accepted.
- **D97.8 The rule.** The incumbent is D88.4's baseline (D89.7, D95.2).
  Metric and rows as D89.5; the challenger's rows are the baseline's,
  exactly. D89.6 decides. If the challenger passes, the curve becomes the
  baseline plus this correction, identically at every airport, cycle hour
  and lead (D89.8). If not, the baseline stays. Either way no other variant
  (weight, window, pooling, latency) is scored in session 103; any later
  variant is a new build choice, fixed in its own entry before its score.
- **D97.9 Descriptive figures, not used by the rule.** The mean error
  (observation minus forecast) of raw GFS, the baseline and the challenger
  per airport and fold; each airport's b at the end of each fold (mean,
  minimum and maximum over its 88 cells); and the six-airport MAE per lead
  for each method.
- **D97.10 This is not a claim.** Build-choice scores are never quoted as
  results (SPEC 2.5). No later change to the recipe can be claimed against
  NBM on 2026-27 (D78.4).
- **D97.11 Order of the next steps (replaces D96.5's session numbers).**
  Session 103: this entry and the bias-drift test. Session 104: download and
  check the f025 to f048 pull (with D97.1's open item), extend the
  development table and the curve to leads 25 to 48 (with the bias-drift
  correction if it passed), fix the daily maximum's metric in its own entry
  (D89.8), and score it.
- **D97.12 Live index.** Removed (archived): D96 and F145, which are settled
  (their open parts are restated here). Added: D97 and F146. After session
  103: D47, D73, D77, D79, D82, D88, D89, F139, D93, D95, D97, F146.
<<<D97-END>>>

## Step 2: PROJECT-INSTRUCTIONS.md section 8 (D97.3)

In `docs/PROJECT-INSTRUCTIONS.md`, the line (exactly once; if not, stop and
report)

`  line, a blank line, then a full multi-paragraph body. Any punctuation is fine.`

is replaced by the two lines

`  line, a blank line, then a full multi-paragraph body. Any punctuation is fine.`
`  It never includes a Co-Authored-By or Claude-Session line (D97.3).`

Nothing else in the file changes. Put the `git diff` in the output file.

## Step 3: the script, its self-check and the baseline gate

Write `scripts/session103_bias_drift_cv.py`. It imports
`scripts/session100_structure_cv.py` read only, after checking its SHA-256
against F143 (that script checks session 97's itself), and uses its
`score_airport(st, ["baseline"], timer)`, `errors`, `check_against_s97` and
`d89_6` (or their equivalents if a name differs; report which). lightgbm is
imported directly (D93.3). It never imports or calls the session-48 guard
itself (D90.1). Output files are written once and refused if present (SPEC
8.7 item 5). Bytecode writing off.

**The tracker** is one small function used by both the self-check and the
score: given a cell's rows in ascending cycle time (cycle, lead, obs,
baseline forecast), it returns the corrected forecasts and, per row, the
number of errors used and the latest valid time used. Each row's valid time
is its cycle plus its lead in hours. Before a row from cycle c is corrected,
every not yet applied error with valid time before c is applied, in
ascending valid time (D97.6). The row's own error is then queued.

Modes:

**`--check`** (no table read). The tracker on hand-made cells, each with an
expected answer computed by hand in the code:
- daily cycles, lead 3, errors 1.0, 1.0, 1.0, 1.0: corrections 0, 0.02,
  0.0396, 0.058808 (to 1e-12);
- daily cycles, lead 24, errors 1.0, 1.0, 1.0: corrections 0, 0, 0.02 (the
  error of day k is first used on day k + 2);
- a missing day: daily cycles at lead 3 on days 1, 2 and 4: day 4 uses both
  earlier errors;
- for every row, the latest valid time used is before its cycle.
Print PASS or FAIL per case. Stop on any FAIL.

**`--gate`**: refit the baseline as session 100's `--gate` does (1,584 fits)
and check every cell's n and MAE, the headline and the per-airport n
against F139, exact equality. Print PASS or FAIL with counts only. **If any
value differs, stop: nothing is scored.**

## Step 4: score the challenger (`--score`)

- Fit the baseline (1,584 fits) and check its headline equals F139's again
  (1.049777501605027); stop if not.
- For each airport, fold, cycle hour and lead, run the tracker over the
  cell's test rows (D97.5 to D97.7) to get the challenger's forecasts. Assert
  for every row that the latest valid time used is before its cycle, and
  count rows corrected with b = 0 (no error yet).
- Methods: `raw_gfs`, `baseline`, `drift`. Compute, from per-row absolute
  errors pooled as F139.6 item 5: per airport MAE; headline; fold-level MAE;
  and per (airport, fold, cycle hour, lead) cell MAE, n and mean error. Write
  one row per (method, airport, fold, cycle hour, lead) to
  `data/processed/session103_bias_drift_cv_scores.csv`, with session 100's
  scores-file columns plus `mean_error`.
- Apply D89.6, `drift` against `baseline`, printing its three parts: (a)
  headline reduction and whether above 0.01; (b) airports lower, of 6; (c)
  folds lower, of 3. Ties keep the incumbent. Print the outcome under D97.8.
- D97.9's descriptive tables, labelled descriptive.

`--meta` writes `data/processed/session103_bias_drift_cv.meta.txt`: inputs,
script and outputs with SHA-256, `LGB_PARAMS` as passed, w, fit counts, run
times and versions.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **F146** (at most about 40 lines, D93.10): the self-check and gate
  results; the three methods' headline, per-airport and fold-level MAEs (one
  compact table); the D89.6 test with its three parts; the outcome under
  D97.8; the mean-error table in brief; rows corrected with b = 0; fit
  counts and run times; script and output SHA-256; readings for the owner;
  what was not done. State that these are build-choice scores, not results
  (SPEC 2.5). Then add `- F146: session 103's finding.` to the Live index
  after D97.
- **Archive step:** `python3 scripts/archive_decisions.py --apply --session
  103`. D96 and F145 should move; report what moved.
- **Tests:** run the suite at the end; all must pass.
- **STATUS.md:** current-only snapshot. State the outcome and that it is a
  build choice; that the f025 to f048 Release holds 195 files, not yet
  downloaded (D97.2); the history rewrite in one line (D97.3); D97.1's open
  item. Carry stage B, the claim batch, MOSMIX and MMMX. **Next planning
  session:** Review session 103. The owner commits and pushes (`git commit
  -F docs/commits/commit-103.txt`) and the planning chat syncs Project
  knowledge. Then plan session 104 (D97.11).
- Size check (DECISIONS.md under 80,000 bytes), citations check, scope
  check.

## What this session must not do

No other weight, window, pooling, latency or method tried; no tuning or
selection of anything else; no change to the record's settings, features or
folds; no model saved; nothing from 2026-27; no non-development airport's
data; no network call; nothing installed; no existing script or data file
edited; SPEC.md, RESULTS.md, CLAUDE.md, README.md not edited. Nothing
committed and no commit message written.
