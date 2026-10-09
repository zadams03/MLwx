# Session 102: fix session 91's gate, run the f021 to f048 test chunk through it (D96)

Suggested model in Claude Code: Sonnet (a small script edit, tests, and a
gated download; no model fit, no design).

## Purpose

Record D96. Make session 91's `--gate` independent of where F122 lives
(a fixed value, checked against the record by a test). Give the 25-48
Release its own notes text. Add tests that guard the record lookups the
pull and stage B depend on. Run D95.7's test chunk and gate. Record F145.

No model is fit and nothing is scored. No 2026-27 value is read. No
non-development airport's observation is read. Nothing is pushed and no
workflow is run. The only network use is Step 5's test chunk.

## Read first

- `STATUS.md` in full.
- `DECISIONS.md` (live) in full.
- Archived, by number (`grep -n '^\*\*F122\. '` and so on, that entry
  only): F122 (F122.3 and F122.5 only), F128 (F128.3), F133 (F133.6 to
  F133.8).
- `scripts/session91_grib_pull.py`: `run_gate` (about l.1167 to 1260),
  the constants block near `DECISIONS_FILE` (l.77), and the docstring.
- `scripts/session87_forward_score.py`: l.70 to 90 and
  `read_decisions_text` / `load_frozen_models` (about l.350 to 380) only.
- `scripts/session86_forward_build.py`: `expected_hash_from_decisions`,
  `run_gate` and `plumbing` (about l.860 to 900 and 1061 to 1085) only.
- `.github/workflows/stagec-grib-pull.yml` in full.
- `tests/README.md`, `tests/test_guards.py`, `tests/test_record.py`.

## Files this session may create or edit (scope list)

- Edited: `scripts/session91_grib_pull.py` (Step 2 only),
  `.github/workflows/stagec-grib-pull.yml` (Step 3 only),
  `tests/test_record.py`, `tests/README.md` (Step 4), `DECISIONS.md`,
  `DECISIONS-archive.md` (archive script only), `STATUS.md`.
- New: `notes/session-102-output.txt`.
- Untracked already: `docs/sessions/session-102.md` (this file; do not
  edit).

Any other changed or new file is a scope breach: report it. The test
chunk's files go to a `mktemp -d` folder outside the repo, deleted at the
end. `MLwx-pull/` and `MLwx-stagec/` are read only. Frozen scripts
(D62.3(a)), including `session86_forward_build.py` and
`session87_forward_score.py`, are never edited.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-102.md`.
- Last entries D95 and F144; no D96 or F145 in either file.
- SHA-256 equal to F144: `scripts/session91_grib_pull.py`
  (`9e7439d7cdb5bcde5ab54d8280199de2490654b5977f41f68c07a1e54f3aaa22`),
  the workflow
  (`4c452428051469f20561670efb2bb895c2fb74e9d220a6464a7442053e01e4dd`),
  `data/processed/session81_training_set.csv`
  (`ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a`).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`:
  21 of 21 pass.
- Stop if any differs.

## Step 1: record D96

Copy the block between `<<<D96-START>>>` and `<<<D96-END>>>` to the end of
DECISIONS.md with `sed`, after `---` and a blank line; `diff` and `cmp`
equal; em-dashes 0. Then make D96.7's Live index change (F145's line is
added at the end of the session).

<<<D96-START>>>
## 2026-10-09: Session 102 decision: F144 accepted, the gate's lookup, session 86's gate, and the order of the next steps (owner, planning chat)

**D96. Owner decisions, planning chat (after session 101): F144 accepted,
how session 91's gate finds F122.3, what session 86's gate can still do,
the 25-48 Release notes, and the order of the next steps.** Written at the
start of session 102, before any other edit. No 2026-27 value has been
read or scored.

- **D96.1 F144 accepted,** with its six readings. Reading 1 is handled by
  D96.2 and D96.3. Reading 5 is handled by D96.4. Readings 2, 3, 4 and 6
  change nothing.
- **D96.2 Session 91's gate.** It stops looking for F122.3 in
  DECISIONS.md. It holds F122.3's training-set SHA-256 as a fixed value
  in the script (as `session87_forward_score.py` already does), and a test
  checks that value against the record in both DECISIONS files. So the
  script no longer depends on where an entry lives, and a disagreement
  between script and record fails the test suite. Nothing else in the
  script changes; its plans for hours 0-24 and 25-48 stay byte-for-byte
  as F144 recorded.
- **D96.3 Session 86's gate.** A survey at session 101's review found
  three scripts that read a DECISIONS file: `session87_forward_score.py`
  reads both files (unaffected); `session91_grib_pull.py` (D96.2); and
  `session86_forward_build.py`, which reads DECISIONS.md alone, for
  F122.3 and F122.5, only inside its `--gate` mode (`run_gate` and
  `plumbing`). Its `--build` mode, the one stage B uses, reads neither
  file. Session 86 is frozen (D62.3(a)) and is not edited. So its
  `--gate`, which passed once (F128), can no longer be re-run as it
  stands. This loses no check stage B needs. A test guards the lookups
  stage B does use (session 87's).
- **D96.4 The 25-48 Release notes.** For `hours` = `25-48` the Release
  notes say "Raw GFS values at forecast hours 25 to 48, at the four grid
  points around each pull airport (DECISIONS D82.4, D83, D95). One month
  per set of three files." For `0-24` nothing changes.
- **D96.5 Order of the next steps (replaces D95.4's session numbers).**
  Session 102: this entry, the gate fix, and D95.7's test chunk and gate.
  If the gate passes, the owner runs the workflow with `hours` = `25-48`
  for 2022-01 alone, then for 2021-03..2026-07 once that month's verify
  step has passed. Session 103: bias drift (D78.2, D81.10(b)), as a build
  choice against the baseline. Session 104: download and verify the 25-48
  pull, extend the development table and the baseline to leads 25 to 48,
  fix the daily maximum's metric in its own entry (D89.8), and score it.
- **D96.6 Unchanged:** D95.5 to D95.8.
- **D96.7 Live index.** Removed (archived): F144, which is settled. Added:
  D96 and F145. D95 stays (D95.5 to D95.8 are in force). After session
  102: D47, D73, D77, D79, D82, D88, D89, F139, D93, D95, D96, F145.
<<<D96-END>>>

## Step 2: session 91's gate (D96.2)

Before editing, save to the temporary folder: `--plan --hours 0-24` and
`--plan --hours 25-48` output, and the full (cycle, hour) key list for
each, hashed as session 101 did (F144: 0-24 key list SHA-256
`17eeb3cf7135408e051de1931b94538d54eb0d37d76ea89c6244aa733f919443`, 25-48
`5b91a41ef11d5a6b7912d7fd78e015386a8079be131f65b9e9e8527630254489`).
Stop if either hash differs from F144's.

Edit `scripts/session91_grib_pull.py`:
- add a constant `TRAINING_SET_SHA256 =
  "ab8f25f2f2368b8a8bf7b96eb0adc74a0c23bd089fa22ea4791fb9a28ca28d4a"` with
  the comment `# F122.3`;
- in `run_gate`, compare the training set's SHA-256 with that constant
  instead of the regex search; keep the printed line's meaning (have,
  F122.3's value, equal) and the STOP;
- remove `DECISIONS_FILE` only if nothing else in the script uses it
  (check with `grep`; report).

Change nothing else. Checks, all in the output file:
- both `--plan` outputs and both key-list hashes are byte-equal before and
  after;
- `--guard-check` passes (12 of 12);
- the gate on a dummy extract (as session 101 made it: an empty points
  file and a meta holding only the positions SHA-256, in `mktemp -d`) now
  gets past the training-set check and stops later for the expected
  reason (no rows), not with an `AttributeError`;
- `git diff -- scripts/session91_grib_pull.py` and its new SHA-256.

## Step 3: the workflow's Release notes (D96.4)

Edit `.github/workflows/stagec-grib-pull.yml`: add `RELEASE_NOTES` to the
top-level `env`, in the same `inputs.hours == '25-48' && ... || ...` form
as `RELEASE_TITLE`, with D96.4's text for `25-48` and the current notes
string, character for character, for `0-24`. Use `--notes "$RELEASE_NOTES"`
in the publish step. Change nothing else.

Checks: the diff in the output file; confirm line by line that for `0-24`
every command and string is unchanged; new SHA-256. Untested locally: YAML
parsing, GitHub expressions, `gh`, Actions.

## Step 4: tests (D96.2, D96.3)

Add to `tests/test_record.py` (standard library plus installed packages,
offline, no writes inside the repo, import behaviour checked first as in
session 101, `MLWX_LIBOMP_PATH_SET` set before importing a script with the
libomp shim):
- **session 91's fixed value:** `session91_grib_pull.TRAINING_SET_SHA256`
  equals the SHA-256 that F122.3 records (found by text in the two
  DECISIONS files read together) and equals the committed training set's
  SHA-256;
- **session 87's lookups** (the ones stage B uses): with
  `session87_forward_score.read_decisions_text()`, the `manifest.json`
  pattern from `load_frozen_models` finds exactly F122.5's value and it
  equals `data/models/session81/manifest.json`'s SHA-256; the text between
  `**F122.5` and `**F122.6` exists and its table has all six airports. If
  session 87 cannot be imported with no side effect, read its two patterns
  from the source instead and say so; do not skip silently.

Update `tests/README.md` to mention these in one or two lines. Run the
suite: all pass (expected 24 of 24 if three tests are added), or stop and
report. Put the summary in the output file.

## Step 5: the test chunk and the gate (D95.7)

Into a `mktemp -d` folder:

```
python3 scripts/session91_grib_pull.py --chunk --dates 2022-01-12,2023-07-12,2024-04-12 --hours 21-48 --out "$TMP" --workers 8
python3 scripts/session91_grib_pull.py --gate --extract "$TMP"
```

The gate uses leads 24 to 29 with inputs from f021, so this chunk covers
every input it needs. It must print `GATE PASSED`: 18 of 18 station-days,
every column of `GATE_COLS` equal with no tolerance, no row missing, none
not rebuilt. Report requests, bytes, run time, and statuses (ok, ok (whole
file), absent by design, idx missing, check failed) from the chunk's meta,
and the gate's full output.

If the chunk fails or the gate does not pass exactly, stop and report:
the 25-48 pull is not ready. Do not retry with other settings. Delete the
temporary folder at the end and record that it is gone.

## End of session

Follow CLAUDE.md's end-of-session steps:

- **F145** (at most about 30 lines): the gate change and its checks; the
  Release notes change; the tests (count, pass, time); the test chunk and
  the gate; SHA-256 of the edited script and workflow; readings for the
  owner; what was not done. Then add `- F145: session 102's finding.` to
  the Live index after D96.
- **Archive step:** `--apply --session 102`. F144 should move; report
  what moved.
- **STATUS.md:** current-only. Carry stage B, the claim batch, MOSMIX and
  MMMX. Note D96.3 (session 86's `--gate` cannot be re-run; `--build`
  unaffected). **Next planning session:** if the gate passed: review
  session 102; the owner commits and pushes
  (`git commit -F docs/commits/commit-102.txt`), the planning chat syncs
  Project knowledge, and the owner runs the workflow with `hours` =
  `25-48` for 2022-01 alone, then 2021-03..2026-07 once that month's
  verify step has passed; then plan session 103, bias drift (D96.5). If
  the gate did not pass: review session 102 and decide the fix.
- Run the test suite once more at the very end; it must pass.
- Size, citations and scope checks.

## What this session must not do

No push, workflow run, Release change or `gh` call. No model fit, build
choice or score. Nothing from 2026-27. No non-development airport's
observations. No script edited except `session91_grib_pull.py` as in
Step 2. No frozen script edited (D62.3(a)). SPEC.md, RESULTS.md, README.md
and CLAUDE.md not edited. Nothing installed. Nothing committed and no
commit message written.
