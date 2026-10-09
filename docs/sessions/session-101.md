# Session 101: close the structure question, tests/, and prepare the f025 to f048 pull (D95)

Suggested model in Claude Code: Opus (a pull script edit with a gate, and a
test suite).

## Purpose

Record D95. Update RESULTS.md section 7's roadmap bullet (D93.4). Add the
`tests/` folder (D90.12). Prepare the additive pull of forecast hours 25 to 48
(D82.3, D84.2): a cycle floor in the pull script, an `hours` input and a
separate Release in the workflow, and a local test chunk through the gate.
Record F144.

No model is fit for a build choice. No 2026-27 value is read. No
non-development airport's observation is read. Nothing is pushed and no
workflow is run.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 and section 6's stage C bullet.
- `DECISIONS.md` (live) in full.
- Archived, by number (`grep -n '^\*\*D83\. '` and so on, that entry only):
  D83 (the pull's design, D83.5 and D83.6), D84 (D84.2 and D84.4), F133
  (F133.5 to F133.9), F136 (the whole-file fallback).
- `scripts/session91_grib_pull.py` and `scripts/session92_verify_chunk.py`:
  the plan functions (`month_cycles`, `plan_chunk`, `expected_messages`,
  `check_valid` and the guards), the `--gate` mode, and where the first and
  last cycles are set. Read other parts only if a step needs them.
- `.github/workflows/stagec-grib-pull.yml` in full.
- `RESULTS.md` section 7 only.

## Files this session may create or edit (scope list)

- New: `tests/README.md`, `tests/test_guards.py`, `tests/test_record.py`,
  `notes/session-101-output.txt`.
- Edited: `scripts/session91_grib_pull.py` (Step 4 only),
  `.github/workflows/stagec-grib-pull.yml` (Step 5 only), `RESULTS.md`
  (Step 2 only), `README.md` (one line, Step 3), `DECISIONS.md`,
  `DECISIONS-archive.md` (archive script only), `STATUS.md`.
- Untracked already: `docs/sessions/session-101.md` (this file; do not edit).

Any other changed or new file is a scope breach: report it. The test chunk's
files go to a `mktemp -d` directory outside the repo, deleted at the end.
`MLwx-pull/` and `MLwx-stagec/` are read only.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-101.md`.
- Last entries D94 and F143; no D95 or F144 in either file. `tests/` does not
  exist.
- SHA-256 equal to the record: `scripts/session91_grib_pull.py`
  (`b52ffc2ee741853079aa8cb7b63850645fb93974a6e4f39d7f20fb212a432f1f`, F136),
  `scripts/session92_verify_chunk.py`
  (`7b59a5c2cfd1b15c8e8c1e769b5b1336735adef151b43eb4487c302a4a18af6a`),
  the workflow (`804b6d35b863e07f2da1a559958cb2710e889d4439438c68c9c6109544ce02a6`),
  `data/processed/session81_training_set.csv`
  (`ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a`).
- Stop if any differs.

## Step 1: record D95

Copy the block between `<<<D95-START>>>` and `<<<D95-END>>>` to the end of
DECISIONS.md with `sed`, after `---` and a blank line; `diff` and `cmp`
equal; em-dashes 0. Then make D95.9's Live index change.

<<<D95-START>>>
## 2026-10-09: Session 101 decision: the structure question closed, the order of the next steps, tests, and the f025 to f048 pull (owner, planning chat)

**D95. Owner decisions, planning chat (after session 100): F143 accepted,
the model-structure question closed, the order of the next steps, the
tests folder, and the design of the f025 to f048 pull.** Written at the
start of session 101, before any other edit. No 2026-27 value has been
read or scored.

- **D95.1 F143 accepted,** with its five readings. Reading 3 (the
  descriptive A-against-B line prints "PASS") changes nothing.
- **D95.2 The structure question is closed.** No larger-settings test for
  pooled models is run (D94.5). The curve's structure is the baseline
  (D88.4): one model per airport, cycle hour and lead. This closes D82.5's
  model-structure comparisons, so RESULTS.md section 7 is updated now
  (D93.4).
- **D95.3 Why the daily maximum waits.** One GFS run's usable leads (3 to
  24) cover at most 22 hours, so no single run made the day before covers
  a whole local day. The forecast daily maximum needs leads beyond 24
  hours. So the f025 to f048 pull (D82.3) comes first.
- **D95.4 Order of the next steps.** Session 101: this entry, RESULTS
  section 7, the tests folder, and the f025 to f048 pull prepared and
  gated locally. The owner then runs the pull on GitHub Actions: one month
  first (2022-01), then the rest. Session 102: bias drift (D78.2,
  D81.10(b)), as a build choice against the baseline, needing no new
  data. Session 103: verify the f025 to f048 pull, extend the development
  table and the baseline to leads 25 to 48, fix the daily maximum's metric
  in its own entry (D89.8), and score it.
- **D95.5 The f025 to f048 pull.** Same script, same fields, same grid
  points, same checks as the f000 to f024 pull (D83.5, D84.4, F136).
  Cycles from 2021-03-22T12 (D84.2), the first GFS v16 run; earlier cycles
  are never requested, whatever their valid time. Valid times stay within
  2021-03-24T00 to 2026-07-31T23. The pull script gains this cycle floor,
  and nothing else; the f000 to f024 plan must be unchanged by it.
- **D95.6 Its Release.** Published to a separate Release,
  `stagec-grib-pull-f025-048`, with the same file names per month. The
  f000 to f024 Release `stagec-grib-pull-v1` is never touched. The
  workflow gains an `hours` input, `0-24` (the default, which keeps the
  current behaviour exactly) or `25-48`, which sets the pull's and the
  verifier's hours and the Release. Locally, its files go to a separate
  folder, `MLwx-pull-f025-048/`, beside the repo.
- **D95.7 Its gate.** A local test chunk on D83.6's three dates
  (2022-01-12, 2023-07-12, 2024-04-12), all four cycles, forecast hours 21
  to 48 (so that the lead-24 airports' R and T inputs, at f021 and f022,
  are inside it), through session 91's `--gate`: 18 station-days, exact
  equality with `session81_training_set.csv`, as F133.7.
- **D95.8 The tests folder (D90.12).** Python's standard `unittest`, no new
  package. Tests run offline, write only to temporary folders, and finish
  in a few minutes. They cover the leakage guards, the archive tool, and
  reproductions of recorded figures from committed files.
- **D95.9 Live index.** Removed (archived): F142, D94 and F143, which are
  settled. Added: D95 and F144. After session 101: D47, D73, D77, D79,
  D82, D88, D89, F139, D93, D95, F144.
<<<D95-END>>>

## Step 2: RESULTS.md section 7

In section 7, find the bullet that starts `- **The roadmap` (found once, or
stop). Replace that whole bullet (up to the next line that starts `- ` or
the next heading) with the block below. Then update the footer's revision
list by adding `and after session 101 (DECISIONS D95)` in the same style as
its earlier entries. Put `git diff -- RESULTS.md` in the output file. Nothing
else in RESULTS.md changes.

<<<R7-START>>>
- **The roadmap** (DECISIONS D72, D82; SPEC 6). Stage A is done: a source
  probe, confidence intervals for the results on record, and a comparison
  with the National Blend of Models and NWS MOS (DECISIONS F127, D78.1).
  Stage B runs: the 2026-27 GFS forward test is pre-registered, its models
  are frozen, and its scripts are written and gated; it is scored only
  after each of its periods ends (DECISIONS D73, D77.6, D79). Stage C is
  open: it widens the target from one hour a day to an hourly curve from
  every GFS run, plus the daily maximum, at 51 airports. Its GFS archive
  pull to 24 hours ahead is complete, and its build choices are made by
  time-ordered cross-validation on the six development airports, never
  quoted as results (SPEC 2.5). So far the curve keeps the proven recipe
  as one model per airport, run time and lead; two pooled structures were
  tested and not adopted (DECISIONS D94, F143). Next come forecast hours
  25 to 48, a correction for drifting bias, and the daily maximum. Stage
  C's claim will be judged on six new airports (EDDM, KORD, CYYZ, ZGSZ,
  ZUCK, NZWN), fixed before any of their held-out data is read. Stages D
  to H (other weather models, blending, upgrade policy, the live tool and
  probabilistic ranges) follow; pooling is conditional.
<<<R7-END>>>

## Step 3: the tests folder

Create `tests/` with `unittest` tests (standard library plus the project's
installed packages; nothing new installed). Run them with
`python3 -m unittest discover -s tests -v` from the repo root. Tests must
not write inside the repo (use `tempfile`), make no network call, and must
never import a record script that runs work on import (for example
`session07_test.py` to `session29_test.py`, which call `main()`); check each
module's import behaviour before using it. Bytecode writing off
(`PYTHONDONTWRITEBYTECODE=1`).

`tests/test_guards.py`:
- the 2026-27 guards used by `session97_stagec_cv.py` (or the module it
  takes them from) refuse a valid time of 2026-08-01T00:00 and allow
  2026-07-31T23:00;
- `session86_forward_build.check_gate_date` refuses 2026-08-01 and allows
  2026-07-31 (F128.4);
- the session-48 reserved-year guard (`assert_reserved_year_excluded`)
  raises for a fold that trains or tests inside 2024-08-01..2025-07-31 and
  passes for `EXPERIMENT_FOLDS` (D51);
- the pull script's guards refuse a cycle after 2026-07-31T18, a valid
  time after 2026-07-31T23, and (after Step 4) any cycle before
  2021-03-22T12 at hours 25 to 48.

`tests/test_record.py`:
- the archive tool: on a temporary copy of both DECISIONS files, `--plan`
  passes and `--apply` rebuilds the original byte for byte (its own
  checks), and `--citations` on the real files reports 0 unresolved;
  DECISIONS.md is under 80,000 bytes;
- F139's headline from the committed scores
  (`session97_stagec_cv_scores.csv`): the n-weighted mean of each airport's
  baseline cell MAEs gives the airport MAE, and their mean equals
  1.049777501605027 within 1e-12 (raw GFS 1.4616990883475995 likewise);
- `session100_structure_cv_scores.csv`'s baseline rows equal session 97's
  rows (first eight columns), as F143.6 states;
- F122.4's gate for EGLC: refit `B+D,L,R,T` on F109's training rows from
  `session81_training_set.csv` with the record's settings and get
  1.0007550363323212 exactly, by calling the existing function in
  `session81_freeze_forward_models.py` if one can be called with no side
  effect; if not, skip this test with a clear reason (report it).

`tests/README.md`: what the tests cover and how to run them, in plain words.
Add one line to the root `README.md`'s repository map for `tests/`, in its
existing style.

Run the suite. All tests pass, or stop and report (a failing test is a
finding, not something to work around). Put the run's summary in the output
file.

## Step 4: the pull script's cycle floor (D95.5)

Before editing, save the plan's output for hours 0-24 across all months
(`--plan`, and a full list of every planned (cycle, hour) key, hashed) and
for hours 25-48 to the temporary folder.

Edit `scripts/session91_grib_pull.py` so that no cycle before 2021-03-22T12
is ever planned or requested, at any hours, and so that `--guard-check`
covers it (add cases: refuse cycle 2021-03-22T06 at f042; allow
2021-03-22T12 at f036). Change nothing else.

Checks, all in the output file:
- **0-24 unchanged:** the plan's counts (65 months, 7,828 cycles, 195,600
  files, 1,932,528 messages, F133.5) and the hashed key list are identical
  before and after the edit.
- **25-48 plan:** print counts per month and in total (cycles, files,
  messages, valid range); the first cycle is 2021-03-22T12; no valid time
  outside 2021-03-24T00 to 2026-07-31T23; no cycle after 2026-07-31T18. The
  messages count has no "absent by design" (those are f000 only).
- `--guard-check`: all cases as specified.
- The verifier, which imports the plan, reports for 25-48 the same counts
  as the plan (run its plan-reading part only, or `--help`, as available).
- `git diff -- scripts/session91_grib_pull.py` and its new SHA-256.

## Step 5: the workflow (D95.6)

Edit `.github/workflows/stagec-grib-pull.yml`:
- add a `workflow_dispatch` input `hours` with options `0-24` (default) and
  `25-48`;
- set the Release tag from it: `stagec-grib-pull-v1` for `0-24`,
  `stagec-grib-pull-f025-048` for `25-48`;
- pass the hours to the pull step and the verify step;
- the Release title for `25-48`: "Stage C GRIB pull, forecast hours 25 to 48".

For `0-24` the workflow must do exactly what it does today. Show the diff in
the output file and confirm that line by line. Also update the header comment
and the publish step's name so they mention the verify step (D85.1's
cosmetic note). The workflow cannot be run locally; run its month-expansion
code on the same six inputs F133.4 used, and say what is untested.

## Step 6: the local test chunk and the gate (D95.7)

Run the edited script, `--chunk` on the three dates (or `--dates`, as the
script provides), all four cycles, `--hours 21-48`, 8 workers, into a
`mktemp -d` folder. Then session 91's `--gate` on it: 18 station-days at the
six development airports, every column, exact equality with
`session81_training_set.csv`. Also run the verifier's checks that apply to a
dates chunk, if any. Report requests, bytes, run time, statuses
(ok, ok (whole file), absent by design, idx missing, check failed).

If the gate does not pass exactly, stop and report: nothing about the 25-48
pull is ready until it does. Delete the temporary folder at the end (record
that it is gone).

## End of session

Follow CLAUDE.md's end-of-session steps:

- **F144** (at most about 40 lines): RESULTS section 7 updated; the tests
  (count, pass, time, any skipped and why); the cycle floor and its checks;
  the 25-48 plan's totals; the workflow change; the gate; SHA-256 of the
  edited script and workflow; readings for the owner; what was not done.
  Then add `- F144: session 101's finding.` to the Live index after D95.
- **Archive step:** `--apply --session 101`. F142, D94 and F143 should move;
  report what moved.
- **STATUS.md:** current-only. Carry the stage B items, the claim batch and
  MMMX. **Next planning session:** Review session 101. If it passed, the
  owner commits and pushes (`git commit -F docs/commits/commit-101.txt`),
  the planning chat syncs Project knowledge, and the owner runs the
  workflow with `hours` = `25-48` for month 2022-01 alone, then for
  2021-03..2026-07 once that month's verify step has passed. Plan session
  102: bias drift (D95.4).
- Run the test suite once more at the very end; it must pass.
- Size, citations and scope checks.

## What this session must not do

No push, workflow run, Release change or `gh` call. No build choice and no
score. Nothing from 2026-27. No non-development airport's observations. No
edit to any script except `session91_grib_pull.py`'s cycle floor, and no
change to its behaviour for hours 0-24. No frozen script edited (D62.3(a)).
SPEC.md and CLAUDE.md not edited. Nothing installed. Nothing committed and no
commit message written.
