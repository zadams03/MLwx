# Session 122: health check, fix session 1 (code, and session 114's outputs)

Recommended model: Opus (code edits with reproduction checks).

This is the first fix session of the health check (D114.3, D115.7). It
records D116, then fixes groups (1) and (2) of F163.10 and F164.9: small
code fixes, the D98.2 constants, the citation check's file list, session
114's outputs and three ANALYSIS.md text rows. It records F165. Nothing is
scored.

## Read first

- `STATUS.md` and SPEC section 2 (always, D93.16).
- `DECISIONS.md`, the live file, in full (this session records D116 and F165).
- `notes/session-120-register.csv` in full (55 rows).
- From `notes/session-121-register.csv`: rows CI13, AN02, AN03 and AN05 only
  (find them with `grep -n`).
- Archived entries, one at a time by line range (D93.12): D98.2, F122.3,
  F156.4, F160.3, F160.4, F162.8.

Every other file is read in the step that needs it, and only as far as that
step needs. `ANALYSIS.md` (about 164 KB) is never read in full: read only the
lines a step names or finds with `grep -n`.

## Limits

- No network. No GRIB cache. No 2026-27 value is read or scored, no MLwx-live
  file is read, no error is computed on any row valid on or after 2026-08-01
  (D105.6).
- Frozen scripts (D62.3(a), D70.6, D80.1) are never edited, and are not run in
  this session. Their bytes are only hashed (Step 3).
- No number in `ANALYSIS.md` is changed. Step 6 adds sentences and fixes one
  note; every existing number stays as it is.
- No existing file under `data/processed/` or `figures/` is edited, moved or
  deleted. Write-once files stay write-once: new outputs go to new names.
- Nothing in `src/mlwx/` and nothing under `deploy/` is edited. MLwx-live is
  untouched; its pinned commit (D113.2) does not change.
- Trial runs that write output go into a `mktemp -d` folder, never into the
  repo, unless the step names a repo path.
- Scripts print short summaries; full lists go to the output file (D93.12).

## Scope (files this session may create or edit)

- Edit: `DECISIONS.md`, `DECISIONS-archive.md` (archive step only),
  `STATUS.md` (overwrite), `.gitignore` (one comment line), `requirements.txt`,
  `tests/README.md`, `tests/test_record.py`, `scripts/archive_decisions.py`,
  `scripts/session92_verify_chunk.py`, `scripts/session117_ifs_guide.py`
  (only under D116.6's condition), `ANALYSIS.md`.
- Never edited (D116.10): `scripts/session96_stagec_table.py`,
  `scripts/session114_comparisons.py`, and any other script whose SHA-256 is
  recorded by another script or test.
- Create: `tests/test_frozen_scripts.py`; `scripts/session122_gates.py`;
  `scripts/session122_analysis.py`;
  `data/processed/session114_comparisons/part1_s122.md`,
  `data/processed/session114_comparisons/part2_comparisons_s122.md`,
  `data/processed/session114_comparisons/SUPERSEDED.md`; new IFS figure files
  in `figures/analysis/` (names ending `_s122.svg`);
  `notes/session-122-output.txt`.
- Nothing else. `docs/sessions/session-122.md` is the only untracked file
  expected at the start.

---

## Step 0. Start

Check: `git log -1 --format=%s` equals the first line of
`docs/commits/commit-121.txt`; the tree is clean apart from the untracked
`docs/sessions/session-122.md`; `.venv/bin/python -m unittest discover -s
tests` runs OK (record the count; 181 expected). Report the byte size of
`DECISIONS.md` and record HEAD's hash.

Stop if the commit subject differs, the tree has other changes, or a test
fails.

## Step 1. Record D116

Append the text between the two marker lines below to the end of
`DECISIONS.md`, copied with `sed` (CLAUDE.md), with one blank line and `---`
before it as for every entry. Do not change the Live index yet.

Check: the appended block is byte-equal to the source (`diff` and `cmp`),
and has 0 em-dashes.

Stop on any difference.

<!-- D116 start -->
## 2026-10-22: Session 122 decision: F164 accepted, the rulings for fix groups 1 and 2, and session 122's scope (owner, planning chat)

**D116. Owner decisions, planning chat (after session 121's commit): F164 accepted; the rulings that fix groups (1) and (2) need; session 122's scope; and Live index changes.** Written at the start of session 122, before any other edit. No 2026-27 value has been read or scored.

- **D116.1 F164 accepted,** with its readings (F164.10) and its grouping (F164.9). Group (8) is done: the owner re-uploaded SPEC and RESULTS and kept PROJECT-INSTRUCTIONS and CLAUDE after comparing sizes (PK05 to PK08). F164.8's one network request is accepted; it changed nothing.
- **D116.2 Tests (T02; owner).** The suite stays on unittest. pytest is not installed. The command is `.venv/bin/python -m unittest discover -s tests`, stated in `tests/README.md`. CLAUDE.md gets the same line in the record-text fix session (CL05).
- **D116.3 The gate constants (C06, C07; owner).** The `--gate` modes of sessions 92, 95 and 96 searched DECISIONS text for F122.3's SHA-256. None of the three scripts is edited (D116.10): session 92's SHA-256 is listed in three stage C table meta files, and sessions 104 and 106 record session 96's. A new `scripts/session122_gates.py` runs each of the three gates with the value held as a constant in `session91_grib_pull.py` (`TRAINING_SET_SHA256`, already checked by a test) in place of the DECISIONS lookup, swapped at run time; the frozen session 86 is unchanged. Session 92's verify path, which the pull workflow uses, does not change.
- **D116.4 Frozen scripts' SHA-256 (S03, S04; owner).** The SHA-256 of `session39_sealed_test.py`, `session48_reserved_year.py` and `session60_combine_design.py` are recorded as constants in a new test, `tests/test_frozen_scripts.py`, beside the five frozen scripts' recorded values (F163.4), so all eight are checked by the suite. The scripts are not edited.
- **D116.5 The citation check (CI13; owner).** `scripts/archive_decisions.py --citations` also checks `ANALYSIS.md`, the READMEs in the root, `scripts/`, `data/`, `docs/`, `notes/` and `tests/`, and `docs/PROJECT-INSTRUCTIONS.md`, by entry number.
- **D116.6 Session 114's outputs (A01, C08; owner).** `part1.md` and `part2_comparisons.md` stay as written (write-once). `session114_comparisons.py` is not edited, because session 117 records its SHA-256 (D116.10). A new `scripts/session122_analysis.py` imports session 114's code, adds IFS from session 117's committed tables, and writes `part1_s122.md` and `part2_comparisons_s122.md` beside the old files; `SUPERSEDED.md` in the same folder says which files replace which, and why. Its `--verify` checks `ANALYSIS.md` against the new render and supersedes session 114's `--verify`, which stays as written. Session 117's `--verify` re-renders from session 117's parent commit instead of HEAD (C09): by an edit to `session117_ifs_guide.py` only if no script, test or meta file records its SHA-256; otherwise in `session122_analysis.py`.
- **D116.7 The IFS figure (A02; owner).** IFS is drawn by `session122_analysis.py` in new figure files ending `_s122.svg`; the five existing `figures/analysis/comparison_*.svg` stay byte-equal. `ANALYSIS.md` points to the new files where it names the comparison figures.
- **D116.8 ANALYSIS.md text (AN02, AN03, AN05; owner).** Three text fixes, no number changed: the note on which files Part 1 and Part 2 are rendered from (AN02); one sentence naming the NBM grid in Part 1 item 1, with item 4's figures (AN03); one sentence in Part 1 item 4 and the IFS note saying IFS reads cold at 10 of 12 airports (F160.4) and the reading check found no fault, so the cold error is the model's own (F162.8) (AN05).
- **D116.9 Session 122's scope.** D116.2 to D116.8, and the group (1) rows needing no ruling: L09 (the `.gitignore` comment), T03 (pin matplotlib's nine dependencies), T04 (`tests/README.md`), A03 (`subdaily_max`'s window count check) and A04 (IFS's cycle counts against F160.3), both done in `session122_analysis.py`. Deferred: C11 to the README update (it is a `scripts/README.md` note, RM07's file); T05's optional tests. Not in scope: groups (3) to (7) and (9), and the other group (5) rulings (S06, the outside scheduler, SP05, SP07, SP08, PI07, DE03). No logged value, model, live file or frozen script changes, so D105.5(k) is not engaged.
- **D116.10 Recorded fingerprints (owner).** A script whose SHA-256 is recorded by another script, a test, or a data file's meta file is not edited; a fix to it goes in a new script that imports it. Session 122 found that sessions 104 and 106 record session 96's SHA-256 (F138), session 117 records session 114's, and three stage C table meta files (sessions 96, 104 and 106) record session 92's. Editing such a script would break the record of what produced those results. An audit inventory that lists every script's SHA-256 at one commit (`data/processed/session120_audit/scripts.csv`) is a snapshot, not such a record.
- **D116.11 Live index.** Removed: none. Added: D116 and F165 (F165 when it is written). After session 122: D93, D103, D105, D112, D114, D115, D116, F163, F164, F165.
<!-- D116 end -->

## Step 2. Small fixes (L09, T02, T03, T04)

(a) `.gitignore`: the comment that says the GFS GRIB cache is about 20 GB
says about 39 GB (D102.3). No rule line changes.

(b) `requirements.txt`: pin matplotlib's nine dependencies (contourpy,
cycler, fonttools, kiwisolver, packaging, pillow, pyparsing,
python-dateutil, six) at the versions in `.venv` (`pip freeze`), under a
heading that says they come with matplotlib. Fix the heading that lists
matplotlib under requests. Nothing is installed or upgraded.

(c) `tests/README.md`: say the suite runs with unittest, give the command
(D116.2), and say it takes under a minute.

Check: `git diff --stat` for these three files only; `requirements.txt`
equals `pip freeze` at every pinned line (report pinned count, 0
differences); `git check-ignore` gives the same result as before for
`data/raw/grib`.

Stop on any version difference.

## Step 3. Frozen scripts' SHA-256 (S03, S04, D116.4)

Create `tests/test_frozen_scripts.py`: one constant per frozen script (the
eight of F163.4) and a test that each file's SHA-256 equals it. Take the
five already recorded from their recorded places (F163.4's row S02), and
session 39's from `notes/session-83-output.txt` line 160. For sessions 48
and 60, compute the value now and confirm `git log --format=%h --
<file>` shows one commit each (74e7077, 0e29835), so the file is unchanged
since added.

Check: 8 of 8 equal; the new test passes; the frozen scripts are not in
`git status`.

Stop if any recorded value differs from the file's hash.

## Step 4. The gate constants (C06, C07, D116.3)

Edit only the `--gate` code path of `session92_verify_chunk.py` (near
l.285 to 288) to use `TRAINING_SET_SHA256` from `session91_grib_pull.py`;
first confirm no script or test records session 92's SHA-256. Do not edit
`session95_check_release.py` or `session96_stagec_table.py`. Create
`scripts/session122_gates.py`, which runs session 96's gate with that
constant in place of session 86's `expected_hash_from_decisions` (for
example by patching the lookup at run time), leaving both files
byte-equal.
First confirm that constant equals F122.3's value (read F122.3 by line
range). Add one test to `tests/test_record.py` that session 92's gate and
`session122_gates.py` use that constant and read no DECISIONS text (for
example, no `DECISIONS` path in the gate path, or a small import check).

Check: session 92's and session 95's `--gate` and `session122_gates.py`'s
session 96 gate PASS (report time and result); `session96_stagec_table.py`
is byte-equal to HEAD and `tests/test_stagec.py` loads again (its 23 tests
run);
session 92's verify form still passes on every month of both pulls, as F163
row C02 (`MLwx-pull` 65 of 65 and `MLwx-pull-f025-048` 65 of 65), run in a
temporary clone of the working tree if any check writes files; the suite
passes.

Stop if F122.3's value and the constant differ, a gate fails for any reason
other than one this step fixes, or the verify form changes result on any
month.

## Step 5. The citation check (CI13, D116.5)

Add the files of D116.5 to `CITING_FILES` in `scripts/archive_decisions.py`.

Check: `python3 scripts/archive_decisions.py --citations` passes; report
references and distinct numbers per file before and after; 0 unresolved
(F164 row CI03 showed all resolve).

Stop if any reference does not resolve.

## Step 6. ANALYSIS.md text (AN02, AN03, AN05, D116.8)

Make exactly these text edits; no existing number changes.

(a) AN05: in Part 1 item 4 and in the IFS note (near l.1283), one sentence
each: IFS reads cold at 10 of 12 airports (F160.4); the reading check found
no fault, so the cold error is the model's own, not the reading's (F162.8).
Take "10 of 12" from F160.4 as written; stop if it says otherwise.

(b) AN03: in Part 1 item 1, one sentence naming the NBM grid with the same
figures item 4 already gives (hourly 2 better, 3 worse; daily maximum 2 of
5), citing what item 4 cites.

(c) AN02: the note at l.23 to 24 names `part1_s122.md` and
`part2_comparisons_s122.md` as the files Part 1 and the Part 2 comparisons
section are rendered from, and says the earlier two are superseded (D116.6).

Check: `git diff ANALYSIS.md` shows only these lines; every number in the
added text equals its cited entry; 0 em-dashes in added text.

Stop if an edit would change an existing number.

## Step 7. Session 114's renderer and outputs (C08, A01, C09, A03, A04, D116.6)

Do this in `scripts/session122_analysis.py`, which imports session 114's
code; `session114_comparisons.py` stays byte-equal (D116.10).

(a) Build an up-to-date Part 1 template and Part 2 renderer: add
IFS from session 117's committed tables (the `*_ifs*.csv` files in
`data/processed/session114_comparisons/` and session 117's folder), and the
text of Step 6, so the render equals `ANALYSIS.md`'s Part 1 and its Part 2
comparisons section (l.1282 to 1599 included) byte for byte. Write the
render to `part1_s122.md` and `part2_comparisons_s122.md` by the script's
write-once function. Give the new script a `--verify` that checks
`ANALYSIS.md` against the new render.

(b) Write `SUPERSEDED.md` in that folder: which files the two new ones
replace, why (IFS was added to ANALYSIS.md by session 117 after these were
written; D116.6), and that the old ones are kept unchanged.

(c) A03: the new script checks what `subdaily_max`'s docstring (near l.587
to 597) describes (every window present), counting days that fail, and
recomputes the IFS daily maximum into a `mktemp -d` folder: 0 failing days and
every output byte-equal to the committed one (F160.6: 0 of 3,301 days lack
a window).

(d) A04: the new script holds IFS's cycle counts from F160.3 (development
1,461 / 1,460 / 1,460; claim 1,460 / 1,460; confirm against F160.3) as a
constant, with a test, and runs the loader check for IFS that `F156_4`
(near l.161 to 172) skips. Any rerun output goes into a `mktemp -d` folder
and is byte-equal to the committed one.

(e) C09: session 117's `--verify` re-renders from session 117's parent
commit (`5df783a^`) instead of HEAD. First check whether any script or test
records session 117's SHA-256: if none, edit `session117_ifs_guide.py`; if
one does, do it in the new script instead (D116.6).

Check: `session122_analysis.py --verify` PASS (report numbers compared and
0 mismatches); session 117's verify PASS; `session114_comparisons.py`
byte-equal; `part1.md` and
`part2_comparisons.md` unchanged (`git status`); the suite passes.

Stop if any number in `ANALYSIS.md` cannot be reproduced from the committed
tables: report it and change nothing in `ANALYSIS.md` to make it match.

## Step 8. The IFS figure (A02, D116.7)

In `session122_analysis.py`, draw the comparison figures with IFS into new
files ending `_s122.svg` in `figures/analysis/`, keeping the existing five
byte-equal. Make the SVGs reproducible (fixed metadata and
hash salt), so two runs are byte-equal. Update `ANALYSIS.md`'s figure
references to the new files, and make the same change in Step 7's render so
`--verify` still passes.

Check: two runs into `mktemp -d` folders byte-equal; the five old files
unchanged; `session122_analysis.py --verify` PASS again; report each new file's name
and SHA-256.

Stop if adding IFS would change any of the five existing figures.

## Step 9. F165

Write F165 (D93.10, at most about 40 lines): what was done per register row
(L09, S03, S04, C06, C07, C08, C09, T02, T03, T04, A01, A02, A03, A04,
CI13, AN02, AN03, AN05), each check's result, the test count, readings for
the owner, what was not done (C11, T05, the other groups), and pointers.

Check: F165 cites every row id above; 0 em-dashes.

## End of session (CLAUDE.md)

1. Real output: every check above with its real numbers.
2. Overwrite STATUS.md as a current-only snapshot. Mark fix groups (1) and
   (2) done (D116, F165); keep groups (3), (4), (6), (7) and (9) and the
   other group (5) rulings open. Keep ST10 and ST11's fixes, already in
   session 121's STATUS (the MMMX line without "(of about 49,000)"; the
   longer-term-plan items under D112.2 item 5). It ends: "**Next planning session:** Review
   session 122 and commit; then plan the next fix session (groups 3, 7 or
   9)."
3. Archive step: add F165 to the Live index and apply D116.11, then run
   `python3 scripts/archive_decisions.py --apply --session 122`.
4. Checks: `--citations`; re-read only what this session changed in STATUS
   and DECISIONS; DECISIONS.md's byte size (above 80,000 is a finding); the
   scope-list check against `git status`; the suite. Report only.
5. Output file `notes/session-122-output.txt`: a summary of at most 30 lines
   first (including the consistency-check findings), then the checkpoints
   and detail. Report the same summary in chat. Stop and wait for review.
   Do not commit.
