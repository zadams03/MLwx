# Session 131: fixes from the code review, and stage B's preparation

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session fixes what session 130's review found (F173,
`notes/session-130-register.csv`), in the order the review proposed:
first protect the live test, then fix the live tool and its workflow
(one redeploy after the commit), then the MOSMIX template, then stage
B's preparation by new scripts only, then two speed-ups that change no
output. Recommended model: Opus.

## Read first

- STATUS.md in full; SPEC section 2; the live DECISIONS.md in full.
- `notes/session-130-output.txt`: the summary, section A (the critical
  and major findings), section B (GFS v17) and section H (the grouping),
  by line range.
- `notes/session-130-register.csv`: the rows named in each step below
  (by `grep`), not the whole file.
- Archived, by line range: D73.3 to D73.8, D79.6, D97.4 to D97.7,
  D103.6 to D103.10, D105.9, D112.4, D116.10, D117.5 to D117.7, D118.2,
  D123.2, D123.5, F122.3, F122.5, F128, F152.8, F166.6, F172.2, F172.7.
- The files each step edits, in full; `src/mlwx/observations.py` and
  `src/mlwx/prediction_log.py` in full but read only.

## Rules for this session

- **Pinned files (D125.4).** `src/mlwx/observations.py`, `dailymax.py`,
  `prediction_log.py`, `config.py`, `records.py`,
  `src/mlwx/data/gfs_airports.csv` and
  `data/processed/session111_new_tables.csv` are not edited. Step 3's
  test pins them at their bytes at `3bf156f` before any other file under
  `src/` is touched.
- **Frozen scripts** (`tests/test_frozen_scripts.py`'s list, plus both
  session 129 scripts) are never edited. Stage B's fixes are new scripts.
- **No live observation.** Nothing valid on or after 2026-10-12 is
  fetched from IEM or opened from MLwx-live's `obs/`. No error involving
  a live forecast is computed. `session129_live_score.py --score` is
  never run.
- **Network:** GitHub (fresh clones of public repositories); and for
  Step 7's rehearsal only, NOAA's GFS archive on AWS
  (`noaa-gfs-bdp-pds`) and IEM, for valid times on or before
  2026-07-31T23:00 only. Nothing else. No GRIB file is kept (D47).
- No logged value of an issued row is changed by any edit. Which cycles
  can be issued after a fetch problem changes (D125.2, D125.3), and so
  does `code_commit` at the redeploy; D125.8 records this under
  D105.5(k) before it goes live.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md;
src/mlwx/runner.py; deploy/mlwx-live/.github/workflows/live.yml,
deploy/mlwx-live/.gitignore, deploy/mlwx-live/README.md;
deploy/mlwx-mosmix/saver.py, deploy/mlwx-mosmix/.github/workflows/save.yml,
deploy/mlwx-mosmix/README.md;
tests/test_frozen_scripts.py, tests/test_pinned_files.py (new),
tests/test_live.py, tests/test_live_template.py, tests/test_onboard.py,
tests/test_mosmix_saver.py, tests/test_stageb_rules.py (new),
tests/test_session131_stageb.py (new), tests/README.md;
scripts/session131_stageb_build_check.py (new),
scripts/session131_stageb_rehearsal.py (new),
scripts/session131_stageb_score.py (new), scripts/README.md (one bullet);
data/processed/session131_rehearsal/ (new; small result files only);
notes/session-131-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `3856264`; the tree is clean apart from
this prompt. Tests: 333 OK (1 skipped). SPEC 3.4's span SHA-256
`a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9`.
Record the SHA-256 of the seven pinned files of the rules above, and
check each equals its bytes at `3bf156f` (`git show 3bf156f:<path> |
shasum -a 256`). Stop if any check fails.

**Step 2. Record D125.** Append the block below to DECISIONS.md with
`sed`, exactly, and check it byte-equal by `diff` and `cmp`; 0
em-dashes.

```
---

## 2026-11-14: Session 131 decision: F173 accepted, rulings on the review's findings, the scheduler kept, and session 131's fixes (owner, planning chat)

**D125. Owner decisions, planning chat (after session 130's commit): F173 accepted; rulings on the critical and major findings (LT09, WF05, LT14, LT16, LS09 to LS12, SB07, SB10, SB11); the outside scheduler decided (D124.3); session 131's scope; the order of the next sessions; and Live index changes.** Written at the start of session 131, before any other edit. No 2026-27 value has been read or scored, and no observation valid on or after 2026-10-12 has been read.

- **D125.1 F173 accepted,** with its register and readings. Correction to D124.3 and F172: three cycles have been issued more than 12 h after their cycle (2026-11-02 06z 12.37 h, 2026-11-05 00z 12.33 h, 2026-11-09 06z 12.82 h; SC04).
- **D125.2 When a cycle is given up (LT09; amends F152.8's 12 h rule).** A fetch problem (GFS or IEM) makes a cycle wait, and it is tried again at every run, until the cycle is 20 h old; from then on the problem is a final stop for that cycle. A waiting cycle still blocks later cycles (F152.8), so a later cycle is issued in time order once the earlier one is issued or stopped. A guard stop (D103.10) stays final at once. D112.4's sentence then holds with 20 h: a cycle is lost only if no run succeeds between cycle + 4 h 10 min and cycle + 20 h.
- **D125.3 The workflow's failure rule (WF05) and an empty observation reply (LT14).** The job fails on any runner exit code other than 0 (issued or nothing due) and 2 (waiting), after the commit step as now. In `runner.py` only, an IEM reply without the expected header is an observation fetch error (D125.2 applies), and each run prints the count of tracker lookups that found no report. `observations.py` is not edited (D125.4).
- **D125.4 What the frozen scoring script depends on (LS09, LS10, LS12).** Until both looks of D105.5 are run, the files `session129_live_score.py` imports or reads are held at their bytes at `3bf156f`, checked by a test: `src/mlwx/observations.py`, `dailymax.py`, `prediction_log.py`, `config.py`, `records.py`, `src/mlwx/data/gfs_airports.csv` and `data/processed/session111_new_tables.csv`. A change to any of them (the v17 row in `config.py`, D125.6, is the one foreseen) is recorded in DECISIONS first, the test's value is updated in the same session, and `session129_live_score.py --gate` is run again and must pass. The log's columns and time format do not change before both looks; all 49 rows of `gfs_airports.csv` stay. Both session 129 scripts are added to `tests/test_frozen_scripts.py` (TE02).
- **D125.5 A one-shot run that fails part-way (LS11, SB07, SB11).** (a) The live test's look: if `--score` stops before any score file is written, its partial output folders are moved aside, kept, and named with the stop time, and `--score` is run again unchanged; any other stop is for the owner. (b) Stage B's build: it is accepted only if no station-day is dropped for a fetch failure (a field absent from the archive is a real absence and stays a counted drop); otherwise its outputs are moved aside and kept, and the build is run again before any score. `scripts/session131_stageb_build_check.py` says which. (c) Stage B's competitor fetch: the session that fetches first runs `session87_forward_competitors.py --gate` and it must pass; if NBM's or the MOS archive's layout has changed, the fetch stops and the owner rules (a new fetch script under D116.10). (d) Stage B's scoring: `scripts/session131_stageb_score.py` runs `session87_forward_score.py` with F122.5's manifest SHA-256 and model table held as constants checked by a test (SB10), as D123.5 did for session 86.
- **D125.6 The GFS version label (LT16).** The guard cannot see which GFS version made a file. Accepted: cycles between v17's go-live and the redeploy that adds the v17 row may be logged as v16. When the Service Change Notice gives the first v17 cycle, a session adds the row to `config.py` (D125.4's route) and the owner redeploys; the entry that records the first operational v17 cycle (D103.10) also lists every logged cycle whose label is wrong. Neither the live test's periods nor stage B's use the label (D105.5(e), D73.3).
- **D125.7 The outside scheduler (D124.3): kept as it is.** No outside trigger is built. Lateness changes no issued value and is counted by the live test, never excluded (D105.5(h)); with D125.2 a cycle is lost only after about 20 h with no successful run (longest gap so far 10.84 h, SC03). The owner may start a run by hand when he wants a fresh page, never between :35 and :55 past the hour (D112.8, D118.2). D118.4's rule is replaced: the scheduler is reopened, by a new entry, if any cycle is lost or any issue lag exceeds 18 h.
- **D125.8 Session 131's scope.** Session 130's groups 1, 2, 5, 6 and 7 (F173): the pin test and frozen-script list; `runner.py` and the live workflow template (D125.2, D125.3, `.gitignore` for partial files, the pip cache), then one redeploy by the owner with `MLWX_COMMIT` set to session 131's commit and `MODELS_TAG` unchanged; the MOSMIX template's fixes, then the owner copies them to `zadams03/MLwx-mosmix`; stage B's three new scripts and a rehearsal of session 86's `--build` path on a spent window (SB09); tests for stage B's rules (TE05); a shared test fixture (EF01). Under D105.5(k): no issued row's value is changed by the code; from the redeploy, a cycle that would have been stopped at 12 h may be issued later, and an empty IEM reply makes a cycle wait instead of being issued without updates. The live test treats every row after the redeploy exactly as before it: all scored, lateness counted.
- **D125.9 The next sessions (amends D122.2).** 132: Gates C and D (F154.9(4)), the iem-position rows for AIFS and the NBM grid at the development airports, and D115.6's question, each with its rules fixed in that session's entry first. 133: stage H's design and build choices. The owner chooses each session's model; the strongest is used only where he judges it worth its cost. A GFS v17 notice goes ahead of any of these.
- **D125.10 Live index.** Removed (archived): D124 and F173, which are settled (D124.2's deployment is carried in STATUS; F173's register stays in `notes/`). Added: D125 and F174 (F174 when it is written). After session 131: D93, D103, D105, D118, D125, F174.
```

**Step 3. Group 1: protect the live test (LS09, LS10, LS12, TE02,
TE03).** Write `tests/test_pinned_files.py`: the seven files' SHA-256
at `3bf156f`, held as constants, each checked; a comment cites D125.4.
Add `session129_live_score.py` and `session129_stageb_gate.py` to
`tests/test_frozen_scripts.py` with their recorded SHA-256 (F172.2,
F172.7); the count test becomes ten. Tests pass. This step comes before
any edit under `src/`.

**Step 4. Group 2: the runner and the live workflow (LT09, WF05, LT14,
WF07, EF05, TE04, TE06).**
(a) `src/mlwx/runner.py`: D125.2 (the give-up age 20 h in place of 12 h;
a waiting cycle tried again at every run; order kept) and D125.3's
runner part. Show the diff in the output file.
(b) `deploy/mlwx-live/.github/workflows/live.yml`: fail on any exit
code other than 0 and 2 (D125.3); setup-python's pip cache (EF05).
`.gitignore`: `*.partial` and `*.tmp` (WF07). README: the new rules in
plain words. The template still matches the deployed workflow apart
from the two `SET-AT-DEPLOY` values and these edits (D105.9); list them.
(c) Tests in `tests/test_live.py`: a first try after 12 h that fails is
tried again at the next run and issued; a cycle 20 h old with a fetch
problem is stopped; order is kept while one waits; an IEM body that is
not CSV makes the cycle wait; the lookups-with-no-report count is
printed; the daily maximum's local day for all 49 time zones over
2026-10-12 to 2027-07-31, clock changes included (as session 130's
`lt_checks.py`). In `tests/test_live_template.py`: run the exit-code
step from the YAML in a temporary repository with exit codes 0, 1, 2
and 3 (only 1 and 3 fail).
(d) A dry run, as F154.4: re-issue cycle **2026-10-12 12z** (it has no
tracker lookups, so IEM is not called) from a fresh clone of MLwx-live
at that cycle's commit into a `mktemp -d` folder, `--latest-only` with
`--now` its issue time. GFS is fetched from NOAA's archive (allowed for
this one cycle). Every row's `raw_gfs`, `baseline`, `b` and `corrected`
must equal the live log file's as text. Report the run time by part
(fetch, model load, the rest). Delete the folder.

**Step 5. Group 5: the MOSMIX template (MS04, MS05, MS06, TE07).**
`save.yml`: `if [ -d manifest ]; then git add manifest; fi` (MS05).
`saver.py --check-fresh`: also fail if any one station's newest issue
held is more than 12 h older than the newest issue listed overall
(MS06). README: an asset with no manifest row is a leftover of a failed
run (MS04); MS08's advice (read the run list after a week). Tests:
MS06's rule; the commit step run in a temporary repository with and
without `manifest/` (TE07).

**Step 6. Group 6a: stage B's scripts (SB07, SB10, SB11, TE05).**
(a) `scripts/session131_stageb_build_check.py`: reads session 86's drop
log and manifest after a `--build` and prints PASS only if no
station-day was dropped for a fetch failure (D125.5(b)); tested on
made-up drop logs.
(b) `scripts/session131_stageb_score.py`: runs `session87_forward_score.py`
with its DECISIONS lookups for F122.5 swapped at run time for constants,
each checked by a test against both DECISIONS files (D125.5(d));
`--check` mode as session 129's wrapper has.
(c) `tests/test_stageb_rules.py` (TE05): import the frozen scripts and
check on made-up arrays: a tie fails (D79.2); the day basis, persistence
on days with a previous-day observation (D73.5); "no verdict (0 days)"
(D79.3); the period split at a first v17 cycle (D73.3); the rows file's
date check; and that the three `--guard-check` modes exit 0.
(d) `tests/test_session131_stageb.py` for (a) and (b).

**Step 7. Group 6b: the rehearsal of session 86's `--build` path
(SB09, SB08).** `scripts/session131_stageb_rehearsal.py` imports session
86 (unedited) and calls its build in the observation mode `--build`
uses (one IEM request per airport for the whole window, the per-cycle
guard) on a short spent window: **2025-06-01 to 2025-06-14**, at the six
airports, with outputs into a `mktemp -d` folder, never session 86's own
output paths. Compare every row with `data/processed/session81_training_set.csv`
on the shared columns, exact equality as F128 did; report counts, any
difference with its first ten cells, the requests and bytes, the run
time and the peak memory (SB08). Run `session131_stageb_build_check.py`
on its drop log. Write a small result file to
`data/processed/session131_rehearsal/`. If a difference is found, stop
and report; do not adjust. If the window's rows are not in the
training set for some airport, report and use the nearest whole
fortnight that is, before 2025-07-31.

**Step 8. Group 7: efficiency (EF01).** `tests/test_onboard.py`: build
the 49-airport setup once per class (`setUpClass`), with every test's
assertions unchanged. Report the suite's time before and after.

**Step 9. READMEs.** `tests/README.md`: lines for the new test files and
`test_mosmix_saver.py`. `scripts/README.md`: one plain bullet for
session 131's three scripts.

**Step 10. Final checks.** Tests: all OK (report the count). The seven
pinned files and every frozen script unchanged (their tests pass, and
`git diff --stat` shows none of them). SPEC.md unchanged; 3.4's span
hash unchanged. No file outside the scope list changed. 0 em-dashes in
added lines and new files. No observation valid on or after 2026-10-12
read; no `obs/` file opened. Write into the output file the exact
redeploy steps for the owner (MLwx-live's workflow file from the
template, `MLWX_COMMIT` to session 131's commit once it exists,
`MODELS_TAG` unchanged, `.gitignore`, a manual run outside :35 to :55)
and the MOSMIX steps (copy `saver.py`, `save.yml` and `README.md` to
`zadams03/MLwx-mosmix`, push, one manual run).

## End of session (CLAUDE.md)

1. **F174**, at most about 40 lines: each finding fixed (id, what
   changed, its test); the dry run's equality and timings; the
   rehearsal's result, counts, run time and memory; the suite's time
   before and after; every check with PASS or FAIL; the redeploy and
   MOSMIX steps in brief; readings for the owner; what was not done
   (any register row left open, with why); pointer to
   `notes/session-131-output.txt`.
2. **Overwrite STATUS.md** as a current snapshot: the review's fixes
   (D125); the redeploy waiting for the owner; the scheduler kept
   (D125.7); stage B's preparation; the order of D125.9. End with:
   `**Next planning session:** Review session 131 and commit; the
   owner redeploys MLwx-live and updates MLwx-mosmix; the planning chat
   syncs Project knowledge (D118.8); then session 132 (D125.9).`
3. **Archive step:** make D125.10's index changes, add F174, then
   `python3 scripts/archive_decisions.py --apply --session 131`.
4. **Checks:** `--citations`; byte size of DECISIONS.md; scope list
   against `git status --porcelain`.
5. **Output file** starts with a summary of at most 30 lines; report the
   same summary in chat. Then stop and wait for review. Do not commit.
