# Session 125: fix group (4), the cache checks

Planning chat, 1 November 2026. One session (D117.2, D115.7). Recommended
model: Sonnet (a read-only run of three scripts and the record).

## Read first

- STATUS.md and SPEC section 2 (always).
- The live DECISIONS.md in full (this session records an entry).
- Register row C12 of `notes/session-120-register.csv` and line 29 of
  `notes/session-120-output.txt` (session 120's clone method). Only those.
- The recorded results the runs are compared with, by lines only:
  `notes/session-71-output.txt` l.2835 to 2850; `notes/session-76b-output.txt`
  l.160 to 315.
- Archived entries only if a step needs one (D102.3, D114.6, D116.10), one
  at a time (CLAUDE.md).

## Limits

- Read-only. No script, test, data file, README, SPEC, RESULTS, ANALYSIS or
  CLAUDE edit. No new script in the repo: any helper code runs inline or
  lives in the temporary folder.
- The three scripts run only in a temporary clone (Step 2), never from the
  repo. The GRIB cache on the drive is read, never written.
- No network. No 2026-27 value is read or scored. Checked in planning: the
  session 71 manifest's latest valid time is 2026-07-31 20z; session 76b's
  two checks filter every row to dates before 2024-08-01 as it is read; the
  four Open-Meteo files check B reads end 2024-07-31. Nothing valid on or
  after 2026-08-01 is read. Session 71's sample includes reserved and
  sealed dates (spent years); the check compares byte ranges and decoded
  values only, no error or score, so nothing is re-scored.
- None of the three scripts is frozen (not in `tests/test_frozen_scripts.py`)
  and none has a SHA-256 in the record (D116.10); their only recorded hashes
  are in session 120's inventory `scripts.csv`, which is not a record
  (F165.11). Record each script's SHA-256 before and after: they must not
  change.
- No em-dash in new text (D76.6). SPEC 3.4's span stays byte-equal
  (`a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`,
  2,050 bytes; S05, D115.4).
- Any single run over 30 minutes is stopped and reported "not run: over 30
  min".

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
`notes/session-125-output.txt`. This prompt file is already present,
untracked. Outside the repo: one temporary folder (`mktemp -d`), deleted at
the end.

## Steps

### Step 0. Start checks

HEAD is c29c488 and the tree is clean apart from this file. Run
`.venv/bin/python -m unittest discover -s tests`: 195 OK. Check SPEC 3.4's
span as above. Record Python, numpy and eccodes versions from `.venv`.
Record the SHA-256 of the three scripts:
`session71_original_functions_check.py` dd3635b0...,
`session76b_check_a.py` 63add241..., `session76b_check_b.py` c497d35d...
(prefixes as session 120 listed them). Stop if any check fails.

### Step 1. Record D119

Append the block between the two marker lines below (markers not
included) to the end of DECISIONS.md with `sed`, preceded by the usual
`---` separator. Check it byte-equal with `diff` and `cmp` against this
file's block; 0 em-dashes. Stop if either fails.

<!-- D119-start -->
## 2026-11-01: Session 125 decision: F167 accepted, fix group 4's run, and fix group 6's scope (owner, planning chat)

**D119. Owner decisions, planning chat (after session 124's commit): F167 accepted; how fix group (4) runs the three cache checks; and the scope of fix group (6), the README update.** Written at the start of session 125, before any other edit. No 2026-27 value has been read or scored.

- **D119.1 F167 accepted,** with its readings (F167.8). (1) ECMWF's service-agreement clause concerns ECMWF's services, not the use of the open data under CC BY 4.0; no action. (2) The prominent attribution goes into group (6) (D119.4). (3) to (5) stand as written.
- **D119.2 Fix group (4): the cache checks (C12, D114.3, D114.6).** The drive is attached at `/Volumes/MY PASSPORT/MLwx-grib-cache/` (D102.3). Session 125 runs `session71_original_functions_check.py`, `session76b_check_a.py` and `session76b_check_b.py` as session 120 ran its checks (F163.5): from the root of a temporary clone of HEAD, outside the repo, with the venv's Python, the sibling folders linked beside it, and `data/raw/grib` in the clone a link to the drive, so any write lands in the clone. Offline. A check passes when it exits 0, every file it writes is byte-equal to its committed copy, and its printed counts equal the recorded ones (session 71 Step 5; session 76b Checks A and B). Otherwise it fails, with the first differing line and the cause if found.
- **D119.3 A failing check is reported, not fixed.** A fix, if the owner wants one, goes in a later session and in a new script (D116.10); the three scripts and their committed outputs are not edited.
- **D119.4 Fix group (6), the README update, last (D115.7).** Its scope: F164.9's README rows RM01, RM03, RM04, RM07, RM09, RM10, RM11; README line 19's goal wording without "private" (D118.5, RM02); C11 (a note in `scripts/README.md` that session 63's two check scripts are run only in a clone, D116.9); and one ECMWF credit line in `ANALYSIS.md` (F167.8(2)), with the IFS and AIFS figures left byte-equal.
- **D119.5 Live index.** Removed (archived): F167, settled (its readings carried by D119.1 and D119.4). Added: D119 and F168 (F168 when it is written). After session 125: D93, D103, D105, D114, D115, D118, D119, F163, F164, F168.
<!-- D119-end -->

### Step 2. Set up the clone (D119.2)

1. `mktemp -d` outside the repo; `git clone` the local repo into it and
   check out c29c488. Link `MLwx-pull`, `MLwx-pull-f025-048`,
   `MLwx-stagec` and `MLwx-live-build` beside the clone, as session 120
   did.
2. Check the drive: `/Volumes/MY PASSPORT/MLwx-grib-cache/` exists and has
   `session71/` and `session72/`. In the clone, make `data/raw/grib` a
   symlink to it; check `git -C <clone> status --porcelain --ignored`
   shows the link only as ignored.
3. Count, with inline Python in the temporary folder, the cache files the
   checks will open: session 71's 378 messages (`smp.cache_name`) and their
   `.idx` files (`smp.idx_cache_name`) under `session71/`; session 76's
   manifest rows dated before 2024-08-01 with status OK (17,150 expected,
   14 FAIL) at the paths `session76b_cache.CACHE` gives. Report present
   and missing per folder. Do not hash here (the scripts do).
4. Touch a start marker file in the temporary folder.

Stop if the drive is absent, a folder is missing, or any expected file is
missing: report the count and do not run Step 3.

### Step 3. Run the three checks (D119.2)

From the clone's root, one at a time, with the repo's `.venv/bin/python`
by absolute path, saving stdout, stderr, exit code and seconds to the
temporary folder:

1. `scripts/session71_original_functions_check.py`. Recorded: (a) 378 of
   378, (b) 477 of 477, (c) 477 of 477 (session 71 output l.2841 to 2843);
   it writes nothing.
2. `scripts/session76b_check_a.py`. Recorded: 17,150 cached messages used,
   14 skipped, Check A PASS (session 76b output l.166 to 225). Writes
   `data/rebuild/session76b/check_a_rno_decoded_values.csv` and
   `check_a_rno_compare.csv`.
3. `scripts/session76b_check_b.py`. Recorded: Check B tables (session 76b
   output l.254 to 312). Writes `check_b_ksfo_point_temps.csv` and
   `check_b_ksfo_monthly.csv`.

After each: `git -C <clone> status --porcelain` and, for any changed file,
`git -C <clone> diff --stat` and the first differing lines. Compare the
printed counts and tables with the recorded lines (a `diff` of the
matching block; the `$` command lines and wall-clock lines are not
compared). Give each check PASS or FAIL by D119.2's rule.

Check: three results, each with its evidence. A FAIL is reported with its
first differing line and cause, not fixed (D119.3). Stop after Step 3 if
anything wrote outside the clone (Step 4 checks).

### Step 4. Nothing written outside the clone

Files newer than the start marker: 0 in the four sibling folders; 0 on
the drive (`find "/Volumes/MY PASSPORT/MLwx-grib-cache" -newer <marker>`).
The repo: `git status --porcelain` shows only this session's scope-list
files. The three scripts' SHA-256 equal Step 0's. Then delete the
temporary folder (the drive and siblings are untouched; the links are
inside the folder).

### Step 5. Tests and F168

Run the suite: 195 OK expected. Write F168 (at most about 25 lines,
D93.10): HEAD and versions; the drive path and file counts (Step 2);
per check PASS or FAIL with its counts, seconds and the clone's status;
Step 4's zero counts and unchanged hashes; readings for the owner; what
was not done (no fix, no edit to a script or committed output, group (6)).
C12 is answered by F168; the register file is not edited.

## End-of-session steps (CLAUDE.md)

1. Real output: paste the checks' real numbers.
2. Overwrite STATUS.md as a current-only snapshot: group (4) done with its
   three results (F168); D119.1's readings closed; group (6)'s scope as
   D119.4 (drop the separate open question on F167.8 and the "(4) when the
   drive is attached" wording); everything else as now. Tests 195. End
   with: "**Next planning session:** Review session 125 and commit; the
   planning chat syncs Project knowledge (D118.8); then plan fix group
   (6), the README update, last (D119.4)."
3. Archive step: make D119.5's index changes, add F168, then
   `python3 scripts/archive_decisions.py --apply --session 125`.
4. Checks: `--citations`; re-read only what changed; DECISIONS.md byte
   size (above 80,000 is a finding); SPEC 3.4's span unchanged; the
   scope-list check with `git status --porcelain`.
5. Output file `notes/session-125-output.txt`, summary first (at most 30
   lines), then checkpoints and detail. Report the summary in chat. Then
   stop and wait for review. Do not commit.
