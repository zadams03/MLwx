# Session 100: the curve's model structure, alternatives A and B (D94)

Suggested model in Claude Code: Opus (model fitting and a build choice).

## Purpose

Record D94, which fixes the open choices of D93.6 before any score. Check
that the baseline still reproduces F139 exactly. Fit and score alternative A
(one model per lead, with the cycle hour as an input) and alternative B (one
model per airport, with lead and cycle hour as inputs) against the baseline
under D89.6, apply D94's rules, and record F143. Also make the small wording
fixes left by session 99 (F142.6).

Every score here is a build-choice score, never a result (SPEC 2.5). No
2026-27 value is read. No non-development airport's data is read.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 (including 2.5) and sections 8.1
  to 8.3 and 8.8 (the recipe, settings, column order G15 and row order G19).
- `DECISIONS.md` (live) in full. It holds D82, D88, D89, F139 and D93, which
  this session depends on.
- `scripts/session97_stagec_cv.py` in full (this session imports from it).
- Archived entries only if a step needs one (for example D70.1, G15's
  written list): find the opening line with `grep -n '^\*\*D70\. '` and read
  only that entry.

## Files this session may create or edit (scope list)

- New: `scripts/session100_structure_cv.py`,
  `data/processed/session100_structure_cv_scores.csv`,
  `data/processed/session100_structure_cv.meta.txt`,
  `notes/session-100-output.txt`.
- Edited: `DECISIONS.md`, `DECISIONS-archive.md` (by the archive script, and
  the one note in Step 2), `docs/PROJECT-INSTRUCTIONS.md` (Step 2 only),
  `STATUS.md`.
- Untracked already: `docs/sessions/session-100.md` (this file; do not edit).

Any other changed or new file is a scope breach: report it, do not hide it.
`MLwx-stagec/` and `MLwx-pull/` are read only.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-100.md`.
- The last entries in DECISIONS.md are D93 and F142; no D94 or F143 exists in
  either file (`grep -c '^\*\*D94\. '` and the same for F143). None of the
  new files exists.
- SHA-256 equal to the record: `scripts/session97_stagec_cv.py`
  (`987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91`),
  `data/processed/session97_stagec_cv_scores.csv`
  (`5604ccd16118fe772cd24a7be83b36ee62e500c78b3ed5bf55c76ed4e78d9d76`),
  and the six table files in `MLwx-stagec/` (F138.4, also listed in
  `data/processed/session96_stagec_dev_table.meta.txt`).
- Read `scripts/session97_stagec_cv.py`: confirm that importing it runs
  nothing (its work sits behind `if __name__ == "__main__"`), and note the
  names of its table loader, fold builder, baseline fit and scoring
  functions, and where `LGB_PARAMS` and the G15 order come from. If importing
  it would run anything, stop and report.
- Stop if any of this differs.

## Step 1: record D94

Copy the block between `<<<D94-START>>>` and `<<<D94-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Then add
`- D94: the model-structure comparison rules (A, B and the baseline).` to
the Live index after the F142 line.

<<<D94-START>>>
## 2026-10-09: Session 100 decision: the model-structure comparisons (owner, planning chat)

**D94. Owner decisions, planning chat (after session 99): F142 accepted,
and the rules for D82.5's two model-structure alternatives, fixed before
any score.** Written at the start of session 100, before any other edit. No
2026-27 value has been read or scored.

- **D94.1 F142 accepted,** with its six readings. The wording it found out
  of date is fixed in session 100 (Step 2).
- **D94.2 Both alternatives in one session.** D89.10's "one at a time"
  means each alternative is compared with the baseline on its own, under
  D89.6. Both are run in session 100, because every rule for choosing
  between them is fixed here first.
- **D94.3 The alternatives.** The baseline is D88.4's (one model per
  airport, fold, cycle hour and lead; F139); it is the incumbent for both
  (D89.7). Alternative A: one model per airport, fold and lead (3 to 24),
  trained on all four cycle hours' rows at that lead, with the cycle hour
  as an extra input. Alternative B: one model per airport and fold, trained
  on all cycle hours and leads 3 to 24, with the lead and the cycle hour as
  extra inputs. Same folds and training windows (D89.3), same complete-case
  rule, same metric and common row set (D89.5).
- **D94.4 Inputs.** The cycle hour is a plain number (0, 6, 12 or 18) and
  the lead a plain number (3 to 24), added after the 15 recipe columns in
  G15's order: A uses G15 plus `cycle_hour`; B uses G15 plus `cycle_hour`
  then `lead`. Neither is a categorical feature.
- **D94.5 Settings.** The record's LightGBM settings, unchanged (`LGB_PARAMS`,
  D21.4/D48.6), so that only the structure changes. Pooled models see more
  and more varied rows with the same model size, which may handicap them,
  most of all B. If B does not beat the baseline, whether a later session
  tests larger settings for pooled models is the owner's decision after
  review; any such test is its own build choice, fixed in its own entry
  before its score.
- **D94.6 The choice.** A is compared with the baseline under D89.6, and B
  with the baseline under D89.6. If neither passes, the baseline stays. If
  exactly one passes, it replaces the baseline. If both pass, B (fewer
  models) becomes the incumbent, and A replaces it only if A passes D89.6
  against B. Whatever the outcome, the A-against-B figures are reported,
  labelled descriptive when this rule does not use them.
- **D94.7 What is not decided here.** The daily maximum, bias drift
  (D81.10(b)) and stage C's claim design stay as D89.10 and D82.5 set them.
  RESULTS.md section 7 stays an open item (D93.4).
- **D94.8 Live index.** D94 and F143 are added. Nothing else changes.
<<<D94-END>>>

## Step 2: wording fixes (F142.6)

Each target must be found exactly once; if not, stop and report. Put the
`git diff` of each file in the output file.

(a) `docs/PROJECT-INSTRUCTIONS.md`, section 3, step 2: replace
`Stop and tell Zac to re-upload the current files` with
`Stop and sync Project knowledge (section 5), or ask Zac to upload the current files if the sync fails,`.

(b) `docs/PROJECT-INSTRUCTIONS.md`, the closing italic line: replace
`update it and re-upload it.` with `update it; the planning chat syncs it to Project knowledge.`
If the phrase differs, report its exact text and leave it.

(c) `docs/PROJECT-INSTRUCTIONS.md`, section 5, the "Which files" bullet.
Its second and third lines currently read (shown indented here; in the file
each starts with two spaces, and the replacement keeps that indent):

    (kept in Project knowledge as `PROJECT-INSTRUCTIONS.md`) only when the
    session edited them.

Replace those two lines with:

    (kept in Project knowledge as `PROJECT-INSTRUCTIONS.md`) only when the
    session edited them. `DECISIONS-archive.md` is kept in Project knowledge
    as `claude/DECISIONS-archive.md`.

(d) `DECISIONS.md` header: replace the two lines
`This is an **append-only** log. Add new entries at the bottom. Never delete`
`or rewrite old entries. Each entry is dated.`
with
`This is the live log. New entries are added at the bottom, and no entry is`
`ever edited or deleted. Entries outside the Live index move verbatim to`
`DECISIONS-archive.md (D93.8). Each entry is dated.`

(e) `DECISIONS-archive.md` header: find the first line that is exactly `---`
(the end of its header note). Insert immediately before it, after one blank
line:
`**Note added by session 100 (D94.1):** since session 99, entries move here by DECISIONS.md's Live index (D93.8), not by the criterion described above (D46).`
Check that the archive's bytes after the insertion point are unchanged
(compare with `tail -c` against a copy taken first).

## Step 3: the script and the baseline gate

Write `scripts/session100_structure_cv.py`. It imports the table loader, the
fold builder, `LGB_PARAMS`, the G15 order and the baseline fit from
`scripts/session97_stagec_cv.py` (read only, after its SHA-256 check), and
lightgbm directly (D93.3). It never imports or calls the session-48 guard
itself (D90.1). The 2026-27 guard, the table SHA-256 checks and the
`complete_case` checks of session 97 run on load.

Modes: `--gate`, `--score`, `--meta`. Output files are written once and
refused if present (SPEC 8.7 item 5). Bytecode writing off.

**`--gate`:** refit the baseline exactly as session 97 does (1,584 fits) and
check, at full precision: every (airport, fold, cycle hour, lead) cell's n
and MAE equal the matching row of `session97_stagec_cv_scores.csv`; the
headline equals F139 (raw GFS 1.4616990883475995, baseline
1.049777501605027); the six per-airport n equal F139.4's table. Print PASS
or FAIL with counts only. **If any value differs, stop: nothing is scored.**

## Step 4: score A and B (`--score`)

For each fold (D89.3), airport and model:

- **Rows.** Training rows: complete-case rows at leads 3 to 24 whose valid
  time is before the fold's T0, as session 97 selects them. Test rows: the
  fold's test rows, as session 97 selects them. A's model for lead L uses
  rows of all four cycle hours at lead L; B's model uses all cycle hours and
  leads 3 to 24. Row order within each model: ascending cycle time, then
  lead (G19).
- **Inputs (D94.4).** A: G15 then `cycle_hour`. B: G15, `cycle_hour`, `lead`.
- **Settings (D94.5).** `LGB_PARAMS` as passed in session 97, unchanged.
- **Common row set.** Check that, in every (airport, fold, cycle hour, lead)
  cell, A's and B's test rows are exactly the baseline's (same count and
  same cycle times). Stop if not.

Fits: A 396 (6 x 3 x 22), B 18 (6 x 3), plus the baseline refit for paired
errors. No model is saved.

Compute for the baseline, A and B, from the per-row absolute errors (D89.5,
pooled as F139.6 item 5 does): per airport MAE; headline (unweighted mean of
the six); per fold, the unweighted mean of the six airports' fold MAEs; and
per airport, fold, cycle hour and lead cell MAE and n. Write one row per
(model, airport, fold, cycle hour, lead) to
`data/processed/session100_structure_cv_scores.csv`, with the same columns as
session 97's scores file plus `model`.

Then apply D94.6 exactly, printing each D89.6 test with its three parts:
(a) headline reduction (incumbent minus challenger, over incumbent) and
whether it is above 0.01; (b) airports where the challenger's MAE is lower,
out of 6; (c) folds where the challenger's fold-level MAE is lower, out of 3.
Ties keep the incumbent. Comparisons: A against baseline; B against
baseline; A against B (applied as the rule only if both pass; otherwise
labelled descriptive). Print the chosen structure.

`--meta` writes `data/processed/session100_structure_cv.meta.txt`: inputs,
script and outputs with SHA-256, `LGB_PARAMS` as passed, fit counts, run
times and versions.

Output file detail: the three methods' per-airport and per-fold tables, the
per-lead table (six-airport mean per lead, each method), and each model's
smallest training count.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **F143** (at most about 40 lines, D93.10): the gate result; the three
  methods' headline, per-airport and fold-level MAEs (one compact table);
  the three D89.6 tests with their parts; the chosen structure under D94.6;
  fit counts and run times; the script and output SHA-256; readings for the
  owner; what was not done. State that these are build-choice scores, not
  results (SPEC 2.5). Add `- F143: session 100's finding.` to the Live index
  after D94.
- **Archive step:** `python3 scripts/archive_decisions.py --apply --session
  100`. The index after this session: D47, D73, D77, D79, D82, D88, D89,
  F139, D93, F142, D94, F143. Nothing should move; report the result.
- **STATUS.md:** current-only snapshot. State the chosen structure and that
  it is a build choice. **Next planning session:** Review session 100. If it
  passed, the owner commits and pushes (`git commit -F
  docs/commits/commit-100.txt`) and the planning chat syncs Project
  knowledge. Then plan the next stage C step: the owner decides D94.5's
  follow-up if B did not pass; then the daily maximum (its metric fixed in
  its own entry first, D89.8) and the `tests/` folder (D90.12).
- Size check (DECISIONS.md under 80,000 bytes), citations check, scope check.

## What this session must not do

No change to the record's settings, features or folds beyond D94; no other
structure, setting or feature tried; no tuning or selection of anything else;
no model saved; nothing from 2026-27; no non-development airport's data; no
network call; nothing installed; no existing script or data file edited;
SPEC.md, RESULTS.md, CLAUDE.md, README.md not edited. Nothing committed and
no commit message written.
