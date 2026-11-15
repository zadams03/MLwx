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
- D127: F175 accepted, the redeploy and the models' move recorded, and the rules for Gates C and D, the iem-position rows and D115.6's question.
- F176: session 132's finding (Gates C and D on the 12 record airports, AIFS and the NBM grid at the airport's own position, the correction against GFS's next run).
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

## 2026-11-15: Session 132 decision: F175 accepted, the redeploy and the models' move recorded, and the rules for Gates C and D, the iem-position rows and D115.6's question (owner, planning chat)

**D127. Owner decisions, planning chat (after session 131b's commit and the owner's steps): F175 accepted; the redeploy, the models' move to the private repository and the MOSMIX update recorded; the rules of session 132's three items, fixed before any value is computed; and Live index changes.** Written at the start of session 132, before any other edit. No 2026-27 value has been read or scored.

- **D127.1 F175 accepted,** with its readings. Reading (3) no longer applies: the token has no expiry (D127.2(c)).
- **D127.2 The redeploy and the models' move (owner, by hand, 2026-11-15; covers D125.8, D126.3 and D126.4).** (a) MLwx-live commit `b836748`, pushed at about 16:00Z: the template of session 131b's commit, `MLWX_COMMIT` `dad68db3ccbdfa930b7af6220d6df585a3cea2bd` (session 131), `MODELS_TAG` `gfs-models-49`; the template's `.gitignore` and README copied. Manual run 43733122333, 16:01:36Z to 16:05:04Z: green; every step succeeded, including the empty-token check and the download from the private repository; it issued a cycle and published the page. From this redeploy `code_commit` changes; D125.8 says how the live test treats the rows after it. (b) The private repository `zadams03/MLwx-models` holds Release `gfs-models-49`, whose `gfs-models.tar` has D105.2's SHA-256 (`e30f8fb99e275fd410bcc37a41686deb26bf61ccb658cb0acbb419da9769f284`), checked before upload and again on a fresh download. F175.4's step 1 ("no README") was wrong: a Release cannot be made in an empty repository (HTTP 422, "Repository is empty"), so one README commit was made first. (c) The token: fine-grained, named "MLwx-live models read", Contents read-only on `zadams03/MLwx-models` only, no expiry (owner's choice), stored as MLwx-live's secret `MODELS_TOKEN`. (d) MLwx-live's fork pull request workflows need approval for all outside contributors. (e) Removed after the green run: MLwx-live's Releases `gfs-models-49` and `gfs-models-12` and their tags (the API lists no releases and no tags; the old download URL returns 404), and the cache `gfs-models-gfs-models-49`; the cache `gfs-models-private-gfs-models-49` remains. (f) Public signals on 2026-11-14 as D126.2.
- **D127.3 MLwx-mosmix updated (owner, 2026-11-15).** Session 131's `saver.py`, `save.yml` and `README.md` copied (MLwx-mosmix commit `09418d0`, 16:23:59Z); one manual run, green.
- **D127.4 Gates C and D on the 12 record airports (F154.9(4)).** `session109_gates.py`'s Gates C and D loop over every configured airport (49), but the record's pull extracts and the gates' design cover the 12 airports of D103.4. A new script, `scripts/session132_gates_cd.py`, imports `session109_gates.py` read-only (SHA-256 `8ac5a567fb4356db61136db4db7783eae381500a2f0314ad9d5a08cee726f59b`), sets its module's `AIRPORTS` to its own `RECORD_AIRPORTS` (the 12) at run time, and runs `run_gate_c` and `run_gate_d` unchanged (D116.10). Gate C passes as F152.6: the guard's offline demonstration behaves, and at each of the three cycles every value equals the pull's extract, with no empty pull cell and no status difference. Gate D passes as F152.7 (owner's rulings 1 and 2 at session 109's stop): no pairing difference for any reason other than a repeated timestamp with different values. They test today's `src/mlwx/` (after session 131's changes) against the record. A failure is reported, not fixed; the owner rules. Network: the AWS GFS archive and IEM only.
- **D127.5 AIFS and the NBM grid at the airport's own position (descriptive, D107.2; D121.2(3)).** (a) Everything as D108.3, D108.4 and session 114's code, except one thing: at the six development airports the competitor is read at the `iem` position set (the airport's own position) in place of the `gfs` set. AIFS's elevation treatment uses its terrain at the `iem` points (`aifs_terrain.csv`'s `iem` rows) and the same station elevation; the NBM grid has no treatment, as before. The curve and raw GFS are unchanged: they stay at GFS's own position (SPEC 3.4). (b) Sources: AIFS (six development airports) and the NBM grid (KDSM, KRNO, KSFO); hourly and daily maximum (D98.10's days primary, every cycle descriptive), as session 114's `--hourly` and `--dailymax`. (c) Method: a new script, `scripts/session132_iem_rows.py`, imports `session114_comparisons.py` read-only (SHA-256 `5ff60d328b2a0489de4173c989a5a9a8472b6bdb5ce6cc4c70d7bd543b2ddc52`), sets its `OUT_DIR` and, for the six development airports, its `SET` to `iem` at run time, and runs its `run_hourly` and `run_dailymax` for `aifs` and `nbm` unchanged, seed 114, into `data/processed/session132_iem/`. (d) Gate first: the same four runs with `SET` unchanged, into a temporary folder: every table equals session 114's committed file of the same name byte for byte (18 files). Then, after the `iem` runs: every row for a claim airport equals session 114's committed row, except the Benjamini-Hochberg columns of the `_dm.csv` files, which depend on the whole family. Either check failing stops the session. (e) Summary (`summary.csv`): per development airport, source and output, the competitor's n, MAE and mean error at the `gfs` set (session 114's tables) and at the `iem` set (this session's), the curve's MAE on each set's paired rows, the pooled skill, and the formal test's direction and Benjamini-Hochberg result in each family. (f) Reading, fixed now: the position matters at an airport when the competitor's pooled MAE changes by at least 0.05 C between the sets; counted, never judged. Nothing in ANALYSIS.md's Part 1 or Part 2, or in RESULTS.md, changes in this session; the owner decides later whether their captions change.
- **D127.6 D115.6's question: does the curve's correction predict GFS's next revision? (descriptive, D107.2).** (a) Rows: every row of session 112's regenerated predictions (`../MLwx-stagec/analysis112/pred_<ICAO>.csv.gz`, each equal to `meta.txt`'s SHA-256) at the 12 airports whose `status` is `scored` or `extra` (the curve has a value), valid at or before 2026-07-31T23:00 UTC. No observation is used. (b) Pairing: a row (airport, cycle c, lead L, valid time v) pairs with the row of the same airport at cycle c + 6 h, lead L - 6, the same v, when that row is also in (a) and has the same `period`. So L runs from 9 to 48. Rows that do not pair are counted by reason (no next cycle in the file; next row not in (a); a different period). (c) Quantities: the correction k = curve - raw_gfs at c; the revision r = raw_gfs(c + 6 h, v) - raw_gfs(c, v) (the elevation constant cancels); also k_base = baseline - raw_gfs and b = curve - baseline at c, so k = k_base + b. (d) Statistics per airport, pooled over its periods and per period: n; Pearson's and Spearman's correlation of k and r; the ordinary least squares slope and intercept of r on k; the sign agreement share over pairs with k and r both non-zero (the zero counts reported); mean |r| (raw GFS at c as a forecast of the next raw GFS) against mean |r - k| (the curve at c as that forecast), and their ratio; Spearman's correlation of r with k_base and with b. (e) Intervals: 95 % percentile intervals by a block bootstrap over cycle UTC dates (every pair whose c falls on one UTC date together), 2,000 resamples, one generator `numpy.random.default_rng(132)`, airports in session 112's order (`AIRPORTS`), statistics in (d)'s order. (f) Breakdowns, point values only: the lead at c (9 to 24, 25 to 48); the cycle hour; the tercile of |k|, edges from that airport's own |k| values. (g) Reading, fixed now: at an airport the correction points the way GFS next revises when the interval of Spearman's correlation of k and r lies wholly above 0. Counted of 12; "most airports" is at least 7 of 12. Sizes are described, not judged. Nothing changes because of it; any use (for example as an input in stage E or H) needs its own entry.
- **D127.7 Where results go.** Tables in `data/processed/session132_iem/` and `data/processed/session132_revision/`, each with a meta file (script SHA-256, versions, run time). ANALYSIS.md gains one section appended at its end, "Part 4. Additions after session 114", with D127.5's summary and D127.6's headline table, each labelled descriptive; no existing line of ANALYSIS.md changes.
- **D127.8 Plan.** Session 132: this entry; Gates C and D; the `iem` rows; D115.6's question; tests for the three scripts; ANALYSIS.md's Part 4; F176. Then session 133: stage H's design and build choices (D125.9). A GFS v17 Service Change Notice goes ahead of either.
- **D127.9 Live index.** Removed (archived): D126 and F175, which are settled (the move and redeploy are recorded here and carried in STATUS). Added: D127 and F176 (F176 when it is written). After session 132: D93, D103, D105, D118, D127, F176.

---

## 2026-11-15: Session 132 finding: Gates C and D on the 12 record airports, AIFS and the NBM grid at the airport's own position, and whether the correction predicts GFS's next run

**F176. D127 was recorded first. Gates C and D pass on the 12 record airports with today's `src/mlwx/`; AIFS and the NBM grid were read again at the development airports' own position; D115.6's question was answered on spent rows. Descriptive only (D107.2): no verdict, model, setting, rule, bar, product or live file changed; nothing valid after 2026-07-31T23:00 UTC was used; ANALYSIS.md gained Part 4 only. Network: the AWS GFS archive (Gate C) and IEM (Gate D). Full output: `notes/session-132-output.txt`. Run 2026-11-15. Python 3.12.2, numpy 2.5.2.**

- **F176.1 Start and D127.** HEAD fe53604, tree clean apart from the prompt; 400 tests OK (1 skipped); the three imported scripts and the 12 prediction files equal their SHA-256. D127 appended with `sed`, byte-equal by `diff` and `cmp`, 0 em-dashes.
- **F176.2 Gates C and D (D127.4).** `scripts/session132_gates_cd.py` sets `session109_gates.AIRPORTS` (49) to its 12 record airports at run time. Gate C: guard demonstration 5 of 5 stopped; at 2021-09-15 18z, 2023-03-08 06z and 2026-07-14 12z, 18,768 values each, 0 not equal, 0 empty pull cells, 0 status differences: PASS. Gate D (June 2023): raw rows identical at 12 of 12; pairing equal 8,639 of 8,640, by design 1 (DSM 2023-06-30 11:00), other 0: PASS. Both as F152.6 and F152.7.
- **F176.3 The iem rows (D127.5).** `scripts/session132_iem_rows.py`. Gate: the four runs with SET unchanged give 18 of 18 tables byte-equal to session 114's: PASS. The iem runs: claim-airport rows 1,464 of 1,464 equal (no Benjamini-Hochberg value differed): PASS. n and the curve's MAE are the same in both sets at every airport. Competitor pooled MAE, GFS's point to the airport's own (degrees C): AIFS hourly EGLC 1.129 to 1.108, LFPG 1.107 to 1.105, KDSM 1.083 to 1.082, YSDU 1.121 to 1.114, KRNO 1.602 to 1.658, KSFO 0.944 to 0.933; AIFS daily maximum EGLC 0.981 to 0.983, LFPG 1.448 to 1.430, KDSM 1.431 to 1.424, YSDU 1.478 to 1.441, KRNO 1.397 to 1.461, KSFO 1.453 to 1.776; NBM hourly KDSM 1.208 to 1.156, KRNO 1.444 to 1.470, KSFO 1.404 to 0.920; NBM daily maximum KDSM 1.295 to 1.267, KRNO 0.934 to 0.932, KSFO 1.868 to 1.196. D127.5(f)'s 0.05 C mark: AIFS hourly 1 of 6 (KRNO), AIFS daily maximum 2 of 6 (KRNO, KSFO), NBM hourly 2 of 3 (KDSM, KSFO), NBM daily maximum 1 of 3 (KSFO); 3 of 6 airports in any. Formal test direction changes only for the NBM grid at KSFO: hourly curve better (rejected) to NBM better (rejected); daily maximum curve better (rejected) to NBM better (not rejected). Every other direction and Benjamini-Hochberg result is unchanged; the NBM daily maximum family now rejects 1 of 5 (was 2).
- **F176.4 D115.6's question (D127.6).** `scripts/session132_revision.py`; `--check` 16 of 16 PASS. Pairs: 116,587 per claim airport, 175,107 per development airport; not paired only for lead 3 to 8 (17,517 and 26,301) and a different period (40 and 80); no row outside (a). Pooled Spearman k, r: +0.04 to +0.10 at 11 airports, NZWN -0.014 [-0.026, -0.001]. D127.6(g): interval wholly above 0 at 11 of 12; "most airports" met. Per period: 28 of 30 sets above 0. OLS slope -0.006 (NZWN) to +0.065 (EGLC); sign share 0.501 to 0.540; ratio mean |r - k| / mean |r| 1.94 (KORD) to 6.35 (KRNO). Spearman r with k_base -0.015 to +0.101; with b -0.022 to +0.039 (interval wholly above 0 only at KSFO, wholly below at ZGSZ and YSDU).
- **F176.5 Tests and documents.** `tests/test_session132.py` (9 tests); one line each in `tests/README.md` and `scripts/README.md`'s map; ANALYSIS.md Part 4 (96 lines added, old file a byte-equal prefix).
- **F176.6 Checks.** Tests: see the output file (the citation test fails on D127.9's forward citation until this entry exists). Scope: PASS. Protected folders unchanged: PASS. Em-dashes in added lines: 0.
- **F176.7 Readings for the owner.** (1) Where D127.6 left a choice, the script's docstring fixed it before `--stats` ran: one draw of 2,000 resamples per airport and set (pooled, then each period), shared by every statistic, computed in (d)'s order; intervals for the per-period sets too; breakdowns pooled over periods; tercile edges by `numpy.quantile` (linear); the reason "lead 3 to 8" counted apart from "no next cycle in the file" (a lead of 3 to 8 has no next row by design), and "next row not in the file" added for a next cycle that lacks that lead. (2) r is the plain float difference of the file's raw GFS values; ties in it are broken only by float rounding (r = 0 exactly when the two values are equal). (3) The correction is mostly a steady local bias, so the curve at c is further from the next run than raw GFS is; this measures closeness to the next run, not accuracy. (4) D127.5's summary uses D98.10's days and each competitor's own maximum; the every-cycle tables are in the folder but not summarised. (5) The NBM grid at KSFO read at the airport changes Part 1's picture there; D127.5(f) leaves any caption change to the owner.
- **F176.8 Not done.** No ANALYSIS.md Part 1 or 2 or RESULTS.md change; no model, live file or frozen script touched; no commit.
