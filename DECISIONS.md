# DECISIONS.md — the project's memory of *why*

This is the live log. New entries are added at the bottom, and no entry is
ever edited or deleted. Entries outside the Live index move verbatim to
DECISIONS-archive.md (D93.8). Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- D103: F151 accepted, and stage G's design (the live product v1, GFS only).
- D105: F153 accepted, the redeploy, a pre-registered test of the live forecasts, and the observation snapshot.
- D118: F166 accepted, the redeploy, rulings for fix groups 7 and 9, the scheduler closed, and the Project-knowledge sync.
- D125: F173 accepted, rulings on the review's findings, the scheduler kept, and session 131's fixes.
- F174: session 131's finding (the review's fixes, the dry run, stage B's preparation and its rehearsal).
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

## 2026-10-14: Session 111 decision: F153 accepted, the redeploy, a pre-registered test of the live forecasts, and the observation snapshot (owner, planning chat)

**D105. Owner decisions, planning chat (after session 110's commit and the owner's redeploy): F153 accepted, the redeploy recorded, a test of the live forecasts pre-registered, an observation snapshot added to the log, and the refit and Gate A fix.** Written at the start of session 111, before any other edit. No value on or after 2026-08-01 has been scored, in this test or in stage B (D73).

- **D105.1 F153 accepted,** with its eight F153.9 readings as written. Reading (2) is fixed by D105.8; reading (8) was followed (D105.2).
- **D105.2 The redeploy (owner, by hand, 2026-10-13 evening, not by a session).** Release `gfs-models-49` ("Frozen GFS product models, 49 airports"), asset named `gfs-models.tar` (`MODELS_FILE` unchanged); GitHub's SHA-256 of the asset is `e30f8fb99e275fd410bcc37a41686deb26bf61ccb658cb0acbb419da9769f284`, equal to F153.7's tar. MLwx-live's workflow was replaced: `MLWX_COMMIT` `e37c86d75d8a5f79c3abc236ca7caae0b9fb17c5` (session 110's commit, checked on GitHub), `MODELS_TAG` `gfs-models-49`, one schedule `40 * * * *` (every hour at 40 minutes past, UTC) in place of the four, the job failing only on runner exit code 3, and the header comment updated (D104.5). A manual run at about 19:22 UTC was green: the models were downloaded, and nothing new was due.
- **D105.3 The first runs after it.** Scheduled runs started at about 23:24 UTC on 2026-10-13 and about 02:07 and 08:00 UTC on 2026-10-14, all green; the owner saw 49 charts on the page on the morning of 2026-10-14. F154 lists the cycles issued and their issue times from the log.
- **D105.4 Scheduled runs.** The hourly schedule is kept, but GitHub started only three scheduled runs in about 13 hourly slots overnight, so cycles can be issued hours late. Nothing is lost while some run starts within 24 hours of a cycle (the catch-up, D103.9). No external trigger is added in v1. Lateness is counted by the live test (D105.5(h)), not excluded.
- **D105.5 A pre-registered test of the live forecasts.** Locked here, before any value on or after 2026-08-01 is scored. It adds to D72.4, whose 2027-28 claim is kept; it changes nothing in stage B (D73), and neither test's result changes the other. D103.2 stands until each look: no accuracy figure is computed or shown.
  (a) What is scored: the `corrected` column of MLwx-live's log, as issued. Per cycle, the log file named for that cycle as first committed; any later file for the same cycle (a correction, D103.8) is reported, never scored. Before scoring, MLwx-live's history must show every log file added once and never modified or deleted; if not, the scoring session stops.
  (b) Outputs: the hourly curve at leads 3 to 48, and the daily maximum read off the logged `corrected` and `raw_gfs` curves by D98.10(a) to (e) unchanged, in each airport's own time zone.
  (c) The bar: D100.5 unchanged, per airport, per period, per output, at full precision; a tie fails. Raw GFS is the log's `raw_gfs` (the elevation-adjusted `temperature_grib_c`).
  (d) Airports: the 49 live airports. The 12 of D103.4 start at 2026-10-12 12z; the 37 of F153.6 start at their first logged cycle (F154). An airport added later is not in this test.
  (e) Periods: period A, from each airport's first cycle to the last cycle before the first operational GFS v17 cycle recorded in DECISIONS (D103.10), or to 2027-07-31 18z if none is; period B, from that v17 cycle to 2027-07-31 18z. A row or a local day belongs to the period of its cycle. Nothing valid after 2027-07-31T23:00 UTC is used. Each period is judged separately, once; period B exists only if v17 starts in the window.
  (f) Observations: IEM routine reports fetched fresh after the period ends (no sooner than 7 days after its last valid hour), paired by the live rule (D88.7 with F152.7's ruling 2, `ReportSet(live=True)`). The snapshot (D105.7) is not the source; agreement between the two is reported.
  (g) Verdicts and the claim: PASS or FAIL per airport, period and output. The claim is stated per output and per group: "passes at N of 12 airports" and "at N of 37 airports", in period A, as issued live. The write-up leads with the smallest margin as a percentage (D79.1). Nothing is averaged across airports.
  (h) Counted, never excluded: cycles in the window with no log file, with the reason the state file gives; each cycle's issue lag (issue time minus cycle); rows issued after their valid time, by lead (leads 3 and 4 always are, since a cycle is used from cycle + 4 h 10 min, D103.9); rows and days with no observation.
  (i) Descriptive, never part of the bar: the baseline without b; mean errors; leads 3 to 24 and 25 to 48; per cycle hour; per model manifest and code commit; and days on which the raw, corrected or observed maximum falls in the first or last hour of the local day, counted and scored separately (as at ZUCK, cycle 2026-10-13 06z).
  (j) Expectation, stated before any value is seen: in period A, both outputs pass at all 12 airports of D103.4. None is stated for the 37 (no held-out score there, a shorter window, cold trackers), or for period B.
  (k) Changes during the window: any change to the models, or to code that changes a logged value, is recorded in DECISIONS before it goes live, saying how this test treats the rows after it. The snapshot (D105.7) changes no logged value (checked, F154).
  (l) The look: one per period, in a later session whose scoring script is written, gated on spent data or synthetic logs, and committed before it reads any observation valid on or after 2026-10-12.
- **D105.6 The live log as evidence.** MLwx-live's history is the record of what was issued and when. The owner does not compute errors from the log, the snapshot or the page before a look.
- **D105.7 The observation snapshot.** For each issued cycle, the runner also writes `obs/YYYY/MM/gfs_YYYYMMDDHH.csv`, named like that cycle's log file: one row per airport and valid time the tracker looked up for that cycle, with the columns `airport`, `valid_utc`, `obs_c` (empty if no report within 15 minutes) and `report_utc` (empty if none), sorted by airport and valid time. No forecast, baseline, b or error column. Written once, after the log file, by the same write-once rule; a snapshot problem never blocks or changes the log file, and is printed in the run output. A cycle with no lookups gets a header-only file. The workflow commits `obs/` with `log/` and `state/`. It goes live at the next redeploy.
- **D105.8 The refit and Gate A (F153.9(2)).** The SHA-256 of the 37 airports' 74 tables in `../MLwx-live-build/tables/` is recorded in `data/processed/session111_new_tables.csv`, whose own SHA-256 is held as a constant in `records.py` (D98.2) and checked by a test. Gate before recording: `mlwx.refit` fits OPKC and RCSS from those tables into a temporary folder, and every model file is byte-equal to `../MLwx-live-build/models-49/`'s. `mlwx.refit` then reads the new airports' tables from their own folder and, with no airport list, covers all 49. Gate A (`scripts/session109_gates.py`) checks the 12 airports with stage C tables by default, whatever `gfs_airports.csv` holds.
- **D105.9 The template.** `deploy/mlwx-live/.github/workflows/live.yml` matches the deployed workflow (D105.2) apart from the two `SET-AT-DEPLOY` values, and also commits `obs/` (D105.7). At the next redeploy the owner sets `MLWX_COMMIT` to session 111's commit and copies the template's commit line.
- **D105.10 Plan.** Session 111: this entry; the live-run check; the snapshot and a dry run that re-issues one real cycle; the refit and Gate A fix; the template; F154. Then the owner's redeploy (D105.9). Then a dedicated planning chat on deeper statistics of the current models, using only spent data (the 12 airports' development and look years, and training periods); never a 2026-27 value, and never the 37 airports' years from 2024-08-01 unless an owner's entry spends them (D104.8).
- **D105.11 Live index.** Removed (archived): D104 and F153, which are settled. Added: D105 and F154. After session 111: D93, D103, D105, F154.

---

## 2026-11-01: Session 124 decision: F166 accepted, the redeploy, rulings for fix groups 7 and 9, the scheduler closed, and the Project-knowledge sync (owner, planning chat)

**D118. Owner decisions, planning chat (after session 123's commit and the owner's redeploy): F166 accepted; the redeploy recorded; a planning-chat check of the runs since; the outside scheduler closed for v1; the rulings that fix groups (7) and (9) need (SP05, SP07, SP08, PI07 with PK10, DE03, S06); the Project-knowledge sync returned to the planning chat; session 124's scope; and Live index changes.** Written at the start of session 124, before any other edit. No 2026-27 value has been read or scored.

- **D118.1 F166 accepted,** with its readings (F166.8).
- **D118.2 The redeploy (D117.7; owner, by hand, 2026-10-27).** MLwx-live commit `628df88` copies the template of `bc70489` (session 123's commit). `MLWX_COMMIT` `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb` and `MODELS_TAG` `gfs-models-49`, both unchanged. A manual check run at about 17:59Z was green: it issued 2026-10-27 12z (MLwx-live commit `d39e1fc`), its skip step printed "3 changed path(s): commit, push and publish", and it showed no Node.js 20 warning. D105.9 holds again: the template matches the deployed workflow apart from the two `SET-AT-DEPLOY` values. D112.8's rule on manual runs (none between :35 and :55 past the hour) stays as standing practice.
- **D118.3 Planning-chat check of the runs since (2026-11-01, a fresh clone of MLwx-live; no run log read, no error computed, D105.6).** 19 commits after `628df88`. Every cycle from 2026-10-27 12z to 2026-11-01 00z is logged, none missing. No commit after the redeploy changed only `state/`; before it, 14 of 41 did (F166.3). So the skip appears to work; no run log confirms it. The 2026-11-01 00z cycle was issued at 09:24Z, a lag of about 9.4 h, above F166.2's maximum of 9.20 h.
- **D118.4 The outside scheduler (D112.6(d), D117.4; owner): closed for v1.** None is built. Why: no cycle has come near the 24-hour loss limit (D112.4); late issues are counted by the live test, never excluded (D105.5(h)); and an outside trigger would need a token secret in MLwx-live. It is reopened, by a new entry, only if any cycle's issue lag exceeds 12 h.
- **D118.5 The end goal's wording (SP05, ST02, RM02; owner).** "Private" is dropped. The goal is a live tool for ten or more airports that corrects every GFS run into an hourly curve to 48 hours ahead, plus the daily maximum; version 1 is live and public (D103.9). D82.2's words stand as history. SPEC section 1 and STATUS change in session 124; README line 19 changes in the README update (group 6).
- **D118.6 Stage G in SPEC (SP07, with SP06 and SP11; owner).** No SPEC section for stage G. Section 6's closing note says its design stays in DECISIONS (D103, D105, D112.6, D117). Stage G's bullet gets status sentences, and stage B's names the live test (D105.5) beside D73.
- **D118.7 A pointer to ANALYSIS.md (SP08; owner).** One bullet in SPEC section 6, after stage A: descriptive analysis on spent data, never a source of rules or claims (D107.2).
- **D118.8 Project knowledge (PI07, PK10; owner; amends D115.2, restores D93.15(b) by a new route).** After the owner commits and pushes a reviewed session, the planning chat clones the public MLwx repo fresh from GitHub into its cloud workspace, checks that its HEAD is the pushed commit, and writes each changed file with project_write's `local_path`, so no content enters the chat (tested 2026-11-01: STATUS.md written this way, Project size unchanged). Every file sits at the root under its own name, the archive included (D115.3); ANALYSIS.md is on the list. If a write fails, the planning chat lists the files with their repo byte sizes and the owner uploads by hand (D115.2's route as the fallback). The size rule reads `knowledge_size` and `max_knowledge_size` from project_info, which share one unit that is not bytes (probably tokens, unconfirmed): on 2026-11-01, 668,149 of 2,000,000 for 1,929,457 repo bytes. Above 80 % of the maximum (1,600,000) is an ACTION NEEDED item. Repo byte totals are not used for the rule.
- **D118.9 The archive's order (DE03; owner).** DECISIONS-archive.md's header gets one line saying blocks are in the order they left the live file, not date order (D93.8). The header is not an entry.
- **D118.10 Session 86's gate (S06; owner): deferred.** Nothing is done now. If stage B needs `session86_forward_build.py --gate` before period A is scored, the session that prepares stage B's run builds a wrapper that swaps its DECISIONS lookup at run time for constants checked by a test, as D116.3 did; the frozen script is not edited.
- **D118.11 The planning chat's repo access (PI02).** The Filesystem extension no longer points at the repo. The planning chat asks for access to `~/Coding Projects/MLwx-all` through the linked computer, writes only into `docs/sessions/` and `docs/commits/`, and reads `notes/` only in a review, by the lines it needs.
- **D118.12 Data credits (RM05; group 9).** Session 124 reads each committed source's terms over the network, read-only, and credits each in README section 9 only. If any terms forbid redistributing the committed values in a public repo, the session stops before editing section 9; the owner rules. Any other condition (attribution, non-commercial use) is stated in the credit.
- **D118.13 Session 124's scope.** D118.5 to D118.9 and D118.11 to D118.12, and group (7)'s rows needing no ruling: SPEC SP04, SP06, SP10, SP11; RESULTS RE01, RE02, RE04, RE05; CLAUDE CL03, CL04, CL05 (D116.2's test command), CL07, and D116.10's rule; PROJECT-INSTRUCTIONS PI01, PI02, PI04 to PI08, PI12, PK09 to PK11; STATUS ST02, ST10, ST11 at its overwrite. Not in scope: groups (4) and (6) (the rest of README). No logged value, model, live file or frozen script changes, so D105.5(k) is not engaged.
- **D118.14 Live index.** Removed (archived): D112, D116, D117, F165 and F166, which are settled (D112.8's rule is carried by D118.2; D116.10's by CLAUDE.md and STATUS). Added: D118 and F167 (F167 when it is written). After session 124: D93, D103, D105, D114, D115, D118, F163, F164, F167.

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

---

## 2026-11-14: Session 131 finding: fixes from the code review, and stage B's preparation

**F174. D125 was recorded first. Session 130's groups 1, 2, 5, 6 and 7 (F173.7) are done, by D125's rulings: the live test's imports pinned, the runner's give-up rule and the workflow's failure rule fixed and tested, the MOSMIX template fixed, stage B's build check, scoring wrapper and rules tests written, and session 86's --build path rehearsed on a spent fortnight. No frozen script, pinned file or SPEC line changed. No observation valid on or after 2026-10-12 was read; no obs/ file was opened; no error involving a live forecast was computed; --score was not run. The redeploy and the MOSMIX update wait for the owner. Full output: `notes/session-131-output.txt`. Run 2026-11-14.**

- **F174.1 Start and D125.** HEAD 3856264, tree clean; 333 tests OK (1 skipped); SPEC 3.4's span unchanged (`a02cbe9e...`); the seven pinned files equal their bytes at 3bf156f. D125 appended with `sed`, byte-equal by `diff` and `cmp`, 0 em-dashes.
- **F174.2 Group 1 (LS09, LS10, LS12, TE02, TE03).** `tests/test_pinned_files.py` holds the seven files' SHA-256 at 3bf156f and checks that all 49 airports stay. `tests/test_frozen_scripts.py` now holds ten scripts, with `session129_live_score.py` and `session129_stageb_gate.py`. Done before any edit under `src/`.
- **F174.3 Group 2 (LT09, LT14, WF05, WF07, EF05, TE04, TE06).** `runner.py`: a fetch problem waits and is tried at every run until the cycle is 20 h old, order kept (D125.2); an IEM reply whose first line is not the expected header is an observation fetch problem; each run prints the count of lookups with no report (D125.3). `live.yml`: the job fails on any exit code other than 0 and 2; setup-python's pip cache. `.gitignore`: `*.partial`, `*.tmp`. README in plain words. The new template differs from the deployed workflow (fresh clone `fbfbddf`) only in the two SET-AT-DEPLOY values and these three edits. Tests: 11 new or changed runner tests (all fail on HEAD's runner), the 49 airports' 31 time zones over 2026-10-12 to 2027-07-31, and the exit-code step run from the YAML with codes 0, 1, 2, 3, empty and 137 (only 0 and 2 pass).
- **F174.4 Dry run (Step 4(d)).** Cycle 2026-10-12 12z re-issued from MLwx-live at `bc9f93b^` with session 131's runner, `--now 2026-10-12T20:00 --latest-only`: exit 0, no IEM call; all 552 live rows equal as text in `raw_gfs`, `baseline`, `b` and `corrected`. Time 107.9 s: GFS fetch 100.6 s, the rest 7.3 s (the models load lazily); peak memory 1.34 GB.
- **F174.5 Group 5 (MS04, MS05, MS06, MS08, TE07).** `save.yml` adds `manifest/` only if it exists; `--check-fresh` also fails if any one station's newest issue held is more than 12 h behind the newest listed; README explains leftover assets and the one-week check of the run list. Tests: four for the per-station rule, and the commit step run in a temporary repository with and without `manifest/`.
- **F174.6 Group 6 (SB07, SB09, SB10, TE05).** `scripts/session131_stageb_build_check.py` (SHA-256 `a2504ded...64eb`): PASS only if no "no GRIB message" drop is a fetch failure (a 404 or a missing .idx line is an absence; an unknown failure text counts as a fetch failure). `scripts/session131_stageb_score.py` (`15a5abdf...a5a6`): session 87 with its F122.5 lookups swapped for constants; `--check` PASS. `scripts/session131_stageb_rehearsal.py` (`92f9706d...21c7`). `tests/test_stageb_rules.py` (18 tests) and `tests/test_session131_stageb.py` (20 tests).
- **F174.7 Rehearsal (SB09, SB08).** Session 86's `build_rows` in 'range' mode with the per-cycle guard, 2025-06-01 to 2025-06-14, six airports: 84 of 84 rows, 0 drops; 840 of 840 feature cells, 84 of 84 observations and 84 of 84 previous-day observations equal to the training set exactly; 0 pairing-only differences; build check PASS. 1,434 requests, 1,047,017,651 bytes; 399.1 s; peak memory 0.16 GB. Counts in `data/processed/session131_rehearsal/`.
- **F174.8 Efficiency (EF01).** `test_onboard.py` builds its 49-airport setup once per class: 26.2 s to 14.1 s. Suite: 73.2 s to 61.0 s for 395 tests (52.1 s for 333 at the start; the 62 new tests add time).
- **F174.9 Checks.** Tests after this entry: see the output file. Pinned files, frozen scripts and SPEC unchanged: PASS. Scope: PASS. Em-dashes: 0. Between D125 and this entry the citation test failed on D125.10's forward citation of F174, as F173.8(5) saw.
- **F174.10 For the owner.** Redeploy MLwx-live with `MLWX_COMMIT` set to session 131's commit, `MODELS_TAG` `gfs-models-49`, the new `.gitignore` and README, and one manual run outside :35 to :55; copy `saver.py`, `save.yml` and `README.md` to MLwx-mosmix, push, one manual run. Exact steps in the output file.
- **F174.11 Readings.** (1) At the rehearsal's rate (4.75 s and 12.5 MB a station-day) a full period A of about 2,190 station-days would take about 2.9 h and about 27 GB of transfer. (2) Its peak memory, 0.16 GB on 14 days, does not test SB08's whole-period estimate (the build keeps a copy of the report list per day). (3) The build check counts a decode failure, two or more .idx lines, or a wrong run stamp as "data", reported but not blocking; and a message 404 as an absence. (4) After the redeploy a runner crash makes every run red. (5) `scripts/README.md`'s frozen-scripts table does not list the two session 129 scripts (outside this session's one-bullet scope). (6) The dry run fetched the cycle twice (my first run's printed lines were cut by `tail`).
- **F174.12 Not done.** LT16's config row waits for the v17 notice (D125.6); LS11 and SB11 are rulings applied at their looks (D125.5); the scheduler is kept (D125.7). Register rows outside D125.8's groups were not addressed. No redeploy, no MOSMIX change, no `--build`, `--gate` or `--score` of a frozen script.
