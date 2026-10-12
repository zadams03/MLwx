# DECISIONS.md — the project's memory of *why*

This is the live log. New entries are added at the bottom, and no entry is
ever edited or deleted. Entries outside the Live index move verbatim to
DECISIONS-archive.md (D93.8). Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- D103: F151 accepted, and stage G's design (the live product v1, GFS only).
- F152: session 109's finding (the live package, its gates, the frozen models, a dry run).
<!-- live-index-end -->

Every entry not listed here is in DECISIONS-archive.md, unchanged and still
binding. Entry numbers never change, so every citation resolves in one of the
two files. This list changes only through an owner's DECISIONS entry; a
session adds its own new entries (D93.8).

---

## 2026-10-09: Session 99 decision: F141 accepted, the session order, and a workflow overhaul (owner, planning chat)

**D93. Owner decisions, planning chat (after session 98c): F141 accepted,
three carried items, GFS v17, the session order, and a workflow overhaul
that cuts the reading cost of each session.** Written at the start of
session 99, before any other edit. No 2026-27 value has been read or
scored.

- **D93.1 F141 accepted,** with all nine F141.7 readings.
- **D93.2 The invocation.** The claude.ai Project instructions and section
  4 of `docs/PROJECT-INSTRUCTIONS.md` both give D92.4's invocation, with
  `docs/sessions/session-NN.md` (planning-chat check, 2026-10-09).
- **D93.3 lightgbm.** From D90.9 and F140.7, new scripts may import
  lightgbm directly, with no libomp shim.
- **D93.4 RESULTS.md section 7.** Its roadmap paragraph is out of date
  (F140, F141). It is fixed once, in the session that closes D82.5's
  model-structure comparisons, so that it is edited with their outcome.
  Until then it stays an open item.
- **D93.5 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-09, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-91 (6 October 2026).
  With 30 days' notice the earliest go-live is about 8 November 2026. Also:
  SCN 26-47 (updated) now ends NAM MOS on 3 November 2026, not 14 October
  as D77.1 and F127's correction give. NAM MOS was already excluded
  (D77.1), so nothing changes.
- **D93.6 Session order (amends D90.3).** Session 99 is this workflow
  overhaul. The first of D82.5's alternatives against the baseline
  (D89.10) moves to session 100. Its open choices (which alternative
  first, the rule if both alternatives beat the baseline, the model
  settings, and how the cycle hour is encoded) are fixed in session 100's
  own entry, before any score. Nothing else in D89 changes.
- **D93.7 Why the archive step stopped working.** DECISIONS.md had grown
  to 343,813 bytes (about 4,100 lines), against 773 lines after D46, and
  the archive was last changed on 2026-09-29. The end-of-session archive
  step existed, but: (a) its criterion kept any entry still cited by
  STATUS or by a live entry, and each new entry cites recent ones, so
  recent entries never became movable; (b) its default was "when in
  doubt, keep live" (D46); (c) Claude Code applied it alone each session,
  often by repeating an earlier session's reasons, and the planning-chat
  review accepted "nothing moved" without checking the file's size; (d)
  finding entries copied full tables already held in the output files.
  The step checked a criterion but never its outcome. D93.8 to D93.10
  replace it with an explicit list and a size limit checked every
  session.
- **D93.8 The live file (replaces D46's criterion).** DECISIONS.md opens
  with a Live index: the entries in force for current work. The owner
  changes the index only through a DECISIONS entry; a session adds its own
  new entries to it. At the end of every session, every entry not in the
  index moves verbatim to DECISIONS-archive.md, by
  `scripts/archive_decisions.py`. Being cited elsewhere is not a reason to
  keep an entry live: a citation resolves by number in either file, and an
  archived entry is still binding. The index after session 99: D47, D73,
  D77, D79, D82, D88, D89, F139, D93 and F142. D62 is archived; its rule
  that frozen scripts are never edited (D62.3(a)) stands, restated here:
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py` and `session62_reserved_confirm.py` are
  never edited.
- **D93.9 Size limit.** Every session reports the byte size of
  DECISIONS.md after its archive step. Above 80,000 bytes is a
  consistency finding that the next planning session must act on.
- **D93.10 Finding entries.** A finding is at most about 40 lines: what
  was done, the numbers a decision needs, readings for the owner, what was
  not done, and a pointer to the output file. Full tables, lists and logs
  stay in `notes/session-NN-output.txt`, which begins with a summary of at
  most 30 lines.
- **D93.11 Long sessions and their guardrails.** Sessions may be longer
  and cover more, so that fewer sessions pay the start-up reading. In
  return each prompt lists the files the session may create or edit,
  checked against `git status` before the end steps; Claude Code writes a
  checkpoint line after each step, stops rather than works around a failed
  check, and after any mid-session compaction re-reads CLAUDE.md, the
  prompt and its checkpoints before going on.
- **D93.12 Keeping context small.** Claude Code does not print large files
  or outputs into the conversation; scripts print short summaries and
  write full tables to files; the archive is never read in full, only one
  entry at a time by line range.
- **D93.13 The planning side** (`docs/PROJECT-INSTRUCTIONS.md`). The
  planning chat reads its guide and STATUS in full; SPEC, CLAUDE and
  DECISIONS by targeted search unless the session being planned edits
  them; DECISIONS-archive.md is uploaded to Project knowledge for search
  only; the GFS v17 check is the weekly task of D93.15; reviews start
  from the output file's summary and checkpoints.
  Related work is combined into fewer, fuller sessions, and the planning
  chat recommends a Claude Code model for each.
- **D93.14 Session 99's plan.** Record this entry; replace CLAUDE.md; edit
  `docs/PROJECT-INSTRUCTIONS.md`; add the Live index; move every entry
  outside it to the archive with a checked script; check that every
  citation still resolves; record F142. No model, data file or existing
  script is touched.
- **D93.15 Two planning-side automations.** (a) A weekly scheduled task
  (Mondays, 08:57 London time) searches for a GFS v17 Service Change
  Notice and alerts the owner only when it finds one. Planning chats no
  longer re-check v17; a D entry mentions v17 only when the task has
  found a notice. (b) After the owner commits and pushes a reviewed
  session, the planning chat copies the changed files into claude.ai
  Project knowledge itself, from the linked computer, without their
  contents entering the chat (`docs/PROJECT-INSTRUCTIONS.md` section 5).
  The owner no longer re-uploads by hand, except when the planning chat
  reports that a sync failed.
- **D93.16 What each session reads, and the invocation (replaces
  D92.4's).** Each session prompt begins with a Read first section that
  lists what Claude Code reads before the steps: files in full, SPEC
  sections, and DECISIONS entries by number, live or archived. STATUS.md
  and SPEC section 2 are always read. With no list, the default is
  STATUS.md, SPEC section 2 and the live DECISIONS.md in full. A step
  that needs something not read reads just that part and notes it in its
  checkpoint. CLAUDE.md is loaded automatically and is not read again. So
  the invocation is fixed: "Carry out the session defined in
  docs/sessions/session-NN.md: first read what its Read first section
  lists, then do its steps, staying strictly within its scope. Stop at
  the end-of-session steps and wait for my review. Do not commit
  anything." Each session starts in a fresh Claude Code conversation (a
  new terminal or `/clear`): carrying a finished session's context into
  the next costs more than the short start-up read and blurs the review
  boundary.

---

## 2026-10-12: Session 109 decision: F151 accepted, and stage G's design (owner, planning chat)

**D103. Owner decisions, planning chat (after session 108): F151
accepted, and stage G's design (D102.4), recorded before any build.**
Written at the start of session 109, before any other edit. No value on
or after 2026-08-01 has been scored. Stage G makes no claim (D102.5).

- **D103.1 F151 accepted,** with its four F151.8 readings as written.
- **D103.2 What v1 is.** For every GFS cycle, a corrected 2 m
  temperature curve at leads 3 to 48 and, for each local calendar day
  wholly inside those leads, its maximum read off the curve, by SPEC
  9.3's method unchanged. GFS only. No accuracy figure is computed or
  shown for any period until a test on it is pre-registered (D102.5).
  The drift tracker's errors are an input, not a score.
- **D103.3 The weather model is a setting.** The code is a package,
  `src/mlwx/`, in this repo (D90.12), with a config per weather model:
  data source and fetch, field map, cycle hours, leads and a version
  table. v1 has only `gfs`. A new model adds a config and an adapter,
  not a rebuild.
- **D103.4 Airports.** v1 runs the 12 airports with stage C tables: the
  development airports (EGLC, LFPG, DSM, YSDU, RNO, KSFO) and the claim
  airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN). The rest of D83's
  product list is added later by a one-script onboarding tool.
- **D103.5 Product models.** Refit once at each v1 airport by SPEC 9.3's
  structure and section 8's settings, on every complete-case row valid
  up to 2026-07-31, spent years and the claim airports' look years
  included. This is a build step, not a test: nothing is scored, and
  stage C's look is not run again (D101.2). The models are then frozen;
  v1 does no retraining. Storage: if the whole set is under 50 MB, it is
  committed to the live repo; otherwise it is one Release asset there.
  Either way its SHA-256 is held as a constant (D98.2), and every log
  row cites it.
- **D103.6 Drift tracker.** As D97.5 and D97.6: per airport, cycle hour
  and lead, weight 0.02, updated only by the baseline's own errors whose
  observation is valid before the cycle starts, in ascending valid time,
  each error once. Every tracker starts at b = 0 at the first live cycle
  (D97.7's rule), so early forecasts equal the baseline. Observations:
  IEM routine reports, the nearest within 15 minutes of the valid hour
  (D88.7).
- **D103.7 Live data.** GFS from the same AWS archive, by the same
  byte-range method and at the same four grid points and weights per
  airport as the pull (D82.4); observations from IEM. On any fetch error
  or missing field, that cycle issues nothing, and the page says so.
- **D103.8 The prediction log.** One file per cycle, for all airports,
  written once and never edited. Each row: airport, cycle, lead, valid
  time, raw GFS, baseline, b, corrected value, GFS version, model
  SHA-256, code commit and issue time. A correction is a new file, never
  an edit. Git history is the proof.
- **D103.9 Where it runs.** A separate public repo, zadams03/MLwx-live.
  A GitHub Actions workflow runs four times a day after each cycle lands
  and also catches up any cycle of the past 24 hours missing from the
  log. It checks out this repo's code at a pinned commit, commits the
  log and tracker state, and publishes a static page with GitHub Pages:
  the curve and daily maxima per airport, the GFS version and a status
  line. Public because, on the free plan, public repos get unlimited
  Actions minutes and Pages, and a timestamped, never-edited log is
  forward evidence. This repo receives no automated commits.
- **D103.10 GFS v17 (owner's choice: continue under narrow mapping).**
  Every row carries the GFS version from the config's version table: v16
  until the first operational v17 cycle is recorded in a DECISIONS
  entry. Before a cycle is used, a guard checks every GRIB message's
  identity keys and the grid against the field map; any mismatch stops
  that cycle (D103.7). After v17 starts, the pipeline keeps running only
  under D73's narrow mapping: a fetch may change only if the physical
  quantity is identical, recorded in DECISIONS first. The models are not
  retrained, and the page marks v17 forecasts as not validated.
  Retraining and upgrade policy stay in stage F (D102.4). A 2027-28
  claim (D72.4) would then be on v17; stage F decides how it is framed.
- **D103.11 Plan.** Session 109: this entry; the package; gates that
  reproduce stage C's tables and F147's scores at the development
  airports; the product refit; live GFS and observation adapters, gated
  against committed data; the log, tracker state, page and runner; one
  dry run on the latest real cycle into a temporary folder; the live
  repo's files, written but not deployed; F152. Session 110: the owner
  creates MLwx-live; deployment; the first live runs checked; the
  onboarding script and the remaining airports.
- **D103.12 Live index.** Removed (archived): D102 and F151, which are
  settled. Added: D103 and F152. After session 109: D93, D103, F152.

---

## 2026-10-12: Session 109 finding: the live package, its gates, the frozen models and a dry run

**F152. D103 was recorded first. The package `src/mlwx/` was built and gated against the record, the 2,208 product models were fitted and frozen, the live GFS and observation adapters were gated, the log, tracker state, page and runner were built, one dry run was made into a temporary folder, and the live repo's files were written, not deployed. Nothing was scored: no error, MAE or mean error on any row valid on or after 2026-08-01. Network only in Steps 5, 6 and 8, only to the AWS GFS archive and IEM. Full real output: `notes/session-109-output.txt`. Gates script: `scripts/session109_gates.py` (`b08311554757fa999e0edf93a1f79a84cb33adf11dbbfefa435746f7269a9aff`). Run 2026-10-12. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, eccodes 2.48.0.**

- **F152.1 D103.** Recorded first, byte-equal to the prompt's block (78 lines, `diff` and `cmp`), 0 em-dashes. Step 0: every stage C input equal to its recorded SHA-256 (24 tables, both pull folders, the positions file, 72 observation files, the record scripts and files).
- **F152.2 The package (Step 2).** `src/mlwx/`: config per weather model (only `gfs`: bucket, field map with each message's identity keys, cycle hours, leads 0 to 48, grid, a version table with v16 only), `gfs` (byte-range fetch and the guard), `features` (four-point bilinear, D88.5 arithmetic), `observations`, `tables`, `baseline`, `tracker`, `dailymax`, `prediction_log`, `state`, `page`, `runner`, `refit`, `records`; 12 airports in `data/gfs_airports.csv`. Standard library, numpy, lightgbm and eccodes (all in `requirements.txt`, which was not edited). Tests: `tests/test_live.py`, 99 offline tests; whole suite 150 tests, all pass.
- **F152.3 Gate A.** The package rebuilt the 12 development tables (hours 0 to 24 and 25 to 48) and the 12 claim tables: 24 of 24 equal to the record by SHA-256 (F138.4, the session 104 meta, F149.2).
- **F152.4 Gate B.** The package's fit, tracker and daily-maximum read-off reproduce F147 at the six development airports: 3,312 fits; 9,936 of 9,936 hourly cells and 6,570 of 6,570 days equal; the rebuilt scores and days texts have F147.7's SHA-256; per-airport and headline MAE equal F147.5 and F147.6 at 4 decimals; curve headline at 3 to 48 equal to 1.0891748115841342. A build-choice reproduction (SPEC 2.5); the claim look was not run (D101.2). Gates A and B were run twice, the second time on the final script, with the same result.
- **F152.5 Product models (D103.5).** 2,208 models (12 airports x 4 cycle hours x leads 3 to 48) on every complete-case row valid up to 2026-07-31 (1,925 to 1,956 rows each, 4,310,207 in all). Fitted twice in separate processes: identical. Saved in `../MLwx-live-build/models/` (48 files and `manifest.txt`). **Manifest SHA-256 `16485f384c81094247ec745550ad04982e8c3adb255147546bf1190f498641ef`**, held as `baseline.MANIFEST_SHA256`, checked by a test against this entry. Total 305,986,723 bytes, over the 50 MB limit: **the set is one Release asset in the live repo** (a tar of the folder), not committed. Nothing was uploaded.
- **F152.6 Gate C (Step 5).** Three live cycles from the AWS archive (2021-09-15 18z, 2023-03-08 06z, 2026-07-14 12z), 12 airports, leads 0 to 48: 18,768 values each, all equal to the pull's extract. The guard stops on every altered key in the tests (13 keys, a missing value, a wrong field, a missing idx line, a wrong run stamp) and on 5 of 5 in the gate's offline demonstration.
- **F152.7 Gate D (Step 6) and the owner's rulings at a stop.** The first run stopped: raw rows identical at all 12 airports, but the pairing differed in 7 of 8,640 hour-airport cases. Six were the first hour of the month (the request began on 1 June, the committed pairing used reports from 31 May). One was DSM 2023-06-30 11:00: two rows share the timestamp 10:50 (21.67 and M), and IEM lists them in a different order from the committed file, so the record's first-row rule gave a different value. Rulings (owner, planning chat): (1) re-run with the request starting one day earlier, comparing the 720 hours of June 2023; (2) live pairing only: when rows share a timestamp and their values differ (one missing counts), that timestamp is ignored and the nearest other report within 15 minutes is used (D88.7); the record's tables and training pairing are unchanged. Implemented as `ReportSet(live=True)`, used by the runner, with tests. Re-run: raw rows identical; pairing equal at 8,639 of 8,640, the one difference being DSM 2023-06-30 11:00, by design under ruling 2; no other difference.
- **F152.8 Log, state, page, runner (Step 7).** Log: `log/YYYY/MM/gfs_YYYYMMDDHH.csv`, one file per cycle for all airports, written once (a temporary name, then a hard link; an existing file is never overwritten). State: one JSON file, each cell holds b, the last valid time applied and a count, starting at b = 0. Page: one standard-library HTML file, no accuracy figure. Runner: every cycle of the past 24 hours that has arrived (cycle + 4 h 10 min) and is not logged, in time order. A cycle older than the newest logged one is never issued (no tracker holds an error from after a forecast it helped make). A guard stop is final for that cycle and later cycles go on; a fetch problem waits, and blocks later cycles, until the cycle is 12 hours old.
- **F152.9 Dry run (Step 8).** Latest cycle 2026-10-12 06z, fresh state, into `/tmp/mlwx-dryrun.R8jNkG` (kept): one log file, 552 rows (12 airports, leads 3 to 48), b = 0 everywhere, v16, the page built. The table of raw GFS and corrected values at leads 3, 24 and 48 is in the output file. IEM was not called (no earlier log row, so no error to take).
- **F152.10 Live repo files (Step 9).** `deploy/mlwx-live/`: workflow (four crons at cycle + 4 h 10 min, manual trigger, pinned MLwx commit as a placeholder, models from a Release asset, commits log and state, publishes the page), `requirements.txt`, `README.md`, `.gitignore`. The workflow parses as YAML. No remote repo was created and nothing was pushed.
- **F152.11 Readings for the owner.** (1) The models are 306 MB, so each run downloads them unless the Actions cache holds them (the workflow caches by tag). (2) The workflow and the Linux install of `requirements.txt` are untested (no network to PyPI or GitHub was allowed): run it by hand first in session 110. (3) `code_commit` in the dry run is the repo HEAD plus "-dirty", because the work is not committed; in the live repo it is the pinned commit. (4) The whole-file fallback of D86.2 is not ported: a live cycle with a wrong .idx issues nothing. (5) The 2 m maximum and minimum are not fetched live (not features). (6) In the dry run the baseline moved GFS by up to about 3.4 degrees (EDDM lead 24); nothing was compared with an observation. (7) The first live runs will have b = 0 and the page says "drift warming up" until each cell holds 50 errors. (8) Errors older than 7 days in the log are not used by the tracker (a longer gap is skipped like a missing observation).
- **F152.12 What was not done.** No look, score or accuracy figure of any kind; no retraining; no change to D103 or to any existing script, data file, figure or `MLwx-*` folder; SPEC.md, RESULTS.md, README.md and CLAUDE.md not edited; no remote repo, push, upload or commit; no commit message written.
