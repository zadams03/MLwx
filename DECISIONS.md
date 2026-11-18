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
- D130: F178 accepted, the redeploy, stage D opened on AIFS with its claim on new airports, and the claim airports' rule.
- F179: session 135's finding (stage D's AIFS claim airports drawn, and the AIFS pull built and gated on a test chunk).
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

## 2026-11-17: Session 135 decision: F178 accepted, the redeploy, stage D opened on AIFS with its claim on new airports, and the claim airports' rule (owner, planning chat)

**D130. Owner decisions, planning chat (after session 134's commit): F178 accepted; the owner's redeploy recorded; stage D opened, starting with ECMWF AIFS; where and how its claim is judged; the rule for drawing its claim airports; the AIFS pull; the next sessions; and Live index changes.** Written at the start of session 135, before any other edit. No AIFS value has been read at any airport outside the 12 record airports, and no value valid on or after 2026-08-01 has been scored in any test.

- **D130.1 F178 accepted,** with its readings (F178.8, F178.9) as STATUS lists them.
- **D130.2 The redeploy (owner, by hand, 2026-11-16, not by a session).** MLwx-live commit `afc970b` (00:12Z) sets `MLWX_COMMIT` `9f22ade38e56230ac9d9ff6e6fb13a05da9f262d` (session 134), keeps `MODELS_TAG` `gfs-models-49`, and copies the template README. The scheduled run at 00:18Z (MLwx-live `b7f27ef`) issued 2026-11-15 18z with `code_commit` `9f22ade` on all 2,254 rows. The owner checked the page: the 8-in-10 bands and the "not yet verified" label show at the 12 airports, and there is no "not available" line. The live test treats every row after the redeploy exactly as before it (D129.10).
- **D130.3 Stage D opened (D72.3, D72.8), starting with ECMWF AIFS Single.** Stage D corrects one weather model on its own, from its own fields; GFS is not an input. Combining models is stage E. A GFS v17 notice still goes first (D129.11).
- **D130.4 Where AIFS's claim is judged: new airports (D72.4), one look.** AIFS's operational archive starts on 2025-02-26 (F123.3), so two unseen years per airport cannot exist. Owner's choice: the look is the year 2025-08-01 to 2026-07-31 at six new airports, with each airport's models refit at the start of every calendar month on all earlier data only (an expanding window). The first months are trained on about five months of February to July data; this is stated with any result. AIFS v2 (with IFS 50r1) went live on 2026-05-12, inside the year; it is labelled, not split. No forward test on 2026-27 is pre-registered now.
- **D130.5 What the claim covers (owner's choices).** The hourly curve at AIFS's own 6-hourly steps (leads 6 to 48), against raw AIFS and persistence. The daily maximum is scored descriptively only: taken from four steps a day it runs low, so beating raw AIFS would say little. There is no claim against corrected GFS in stage D: the GFS product models at these airports were fitted on these years (D104.7, F153.6), and combining is stage E's question; any GFS reference in stage D is descriptive. The bar's exact form, the metric, the look script and every remaining detail are fixed at the lock (session 137), before any claim-airport row is scored.
- **D130.6 Framing, recorded now.** The claim airports' observations to 2026-07-31 were used to fit the GFS product models and were counted by session 116's check (D110). They have never been scored for any claim, and no AIFS value has been read there. A result is labelled "new airports for AIFS".
- **D130.7 The claim airports: rules fixed before any check is run.**
  (a) Pool: the 37 airports onboarded in session 110 (F153.6), minus LFPB (D82.7(a)): 36 airports, listed in session 90's table (`data/processed/session90_airports.csv`).
  (b) Eligible: the airport's saved hourly observations (`data/raw/iem_asos_*`) give a usable daily maximum (D82.8) on at least 90 percent of local days in 2025-02-26 to 2026-07-31, and on at least 90 percent of local days in 2025-08-01 to 2026-07-31. A local day counts only if it starts on or after 2025-02-26T00:00 UTC and ends on or before 2026-07-31T23:59 UTC. Counted with session 90's functions, unchanged. Also: the airport's four grid points in `data/processed/session91_pull_airports.csv` must lie on AIFS's 0.25 degree grid (D130.8). Only counts of usable hours are read; no value is read as an error.
  (c) Strata and sizes, in this order, from session 90's `stratum` column: Europe 1; North America 2; Asia 2; South 1.
  (d) Draw: Python's `random.Random(20261117)`, one generator for the whole draw. For each stratum in (c)'s order, `sample` its eligible airports, sorted by ICAO code, for its size. A shortfall is filled as D82.7(d) says. Record the Python version. The draw runs once; neither the seed nor any eligibility result is changed after it.
- **D130.8 Positions and treatment.** Every airport keeps the four grid points and bilinear weights its GFS table uses (`session91_pull_airports.csv`), read on AIFS's 0.25 degree grid, which must hold the same points (longitudes compared modulo 360). Elevation treatment as GFS's (SPEC 5.2, D108.3), with AIFS's own surface geopotential.
- **D130.9 The AIFS pull.** ECMWF open data, `aifs-single/0p25/oper/`, from 2025-02-26 00z; no experimental files. Cycles 00, 06, 12 and 18; steps 0 to 48 every 6 hours; only steps valid on or before 2026-07-31T23:00 UTC. Fields: 2 m temperature, 2 m dewpoint, total cloud cover, 10 m u and v wind, temperature at 850 hPa, mean sea level pressure, surface pressure, surface downward shortwave radiation, and surface geopotential (step 0). Kept unrounded at the four points of 18 airports: the 12 record airports and the six drawn. Whole messages by byte range from the `.index`, each checked against its plan (parameter, level, units, run, step, grid), its SHA-256 recorded; a failed check is a gap with a reason, never a value. The full pull is run by the owner by hand, outside any session, as D108.2 did for IFS; session 135 builds it, runs a test chunk and gate, and estimates its cost. How AIFS's 6-hourly fields map onto `D`, `L`, `R` and `T` (GFS's tendency is over 3 h and its radiation over 2 h) is fixed by an owner ruling in session 136's entry, before any screening.
- **D130.10 The next sessions.** 136: check the owner's pull; the feature mapping; screening by cross-validation at the six development airports (D72.8, D89), the recipe otherwise unchanged. 137: the lock. 138: the look, run once. Opus unless the owner chooses otherwise.
- **D130.11 Live index.** Removed (archived): D129 and F178, which are settled (D129's range test stays binding from the archive and is carried in STATUS; F178 is accepted). Added: D130 and F179 (F179 when it is written). After session 135: D93, D103, D105, D118, D130, F179.

---

## 2026-11-17: Session 135 finding: stage D's AIFS claim airports drawn, and the AIFS pull built and gated on a test chunk

**F179. D130 was recorded first. The six claim airports were drawn by D130.7's rule, and the AIFS pull of D130.9 was written, run on a 16-cycle test chunk and gated. Nothing was scored: no model fitted, no error computed from any AIFS value, no observation read except as usable-hour counts, nothing valid after 2026-07-31T23:00 UTC read. The full pull is the owner's (D130.9). Full output: `notes/session-135-output.txt`. Run 2026-11-17 (UTC). Python 3.12.2, eccodes 2.48.0, numpy 2.5.2, requests 2.34.2.**

- **F179.1 Start and D130.** HEAD 9f22ade, tree clean apart from the prompt; 449 tests OK (1 skipped); SPEC 3.4's span unchanged. D130 appended with `sed`, byte-equal by `diff` and `cmp`, 0 em-dashes.
- **F179.2 Grid and eligibility (D130.7(b), D130.8).** `scripts/session135_aifs_draw.py --eligible`. The AIFS grid of 2025-03-01 00z step 6 (regular 0.25 degrees, 1440 x 721, first longitude 180) holds every point of session 91's table at all 12 record airports and all 36 pool airports (longitudes modulo 360). Pool: session 110's 37 minus LFPB. Every airport has 520 local days in 2025-02-26..2026-07-31 and 364 or 365 in the year from 2025-08-01. Not eligible: **FACT** (85.38 % and 98.90 %) and **RCSS** (69.04 % and 56.44 %). KBKF passes narrowly (92.12 % and 90.11 %). Eligible: Europe 8, North America 9, Asia 15, South 2. `data/processed/session135_draw/eligibility.csv` (SHA-256 `44f3115a...743c`).
- **F179.3 The draw (D130.7(c), (d)), run once.** `random.Random(20261117)`, Python 3.12.2. Europe: sample(8, 1) gave EPWA; North America: sample(9, 2) gave KATL, KDAL; Asia: sample(15, 2) gave RJTT, ZUUU; South: sample(2, 1) gave SBGR. No shortfall. **THE AIFS CLAIM AIRPORTS: EPWA (Warsaw), KATL (Atlanta), KDAL (Dallas Love Field), RJTT (Tokyo Haneda), ZUUU (Chengdu), SBGR (Sao Paulo Guarulhos).** `draw.csv` (SHA-256 `4db7d174...3f13`); its meta file prints the draw and records the draw script's SHA-256 (`600c80f9...924b`), so that script is not edited (D116.10).
- **F179.4 The pull script.** `scripts/session135_aifs_pull.py` (`--plan`, `--pull`, `--verify`, `--gate`), importing session 113's helpers read only. Per chunk: a plan from the cycle's S3 listing and each step's `.index`; each message checked against its plan (parameter, level, units, run, valid time, grid, and every airport's points on that message's own grid geometry); a failed check, missing file or missing point value is a gap with a reason. Values unrounded at the four points of the 18 airports, in session 91's p1 to p4 order; SHA-256 of every message in the manifest.
- **F179.5 Test chunk and gate: PASS.** 2025-03-01, 2026-05-20 and 2026-07-30 00z to 2026-07-31 18z (16 cycles): 988 planned, 988 kept, 0 gaps, 17,784 rows, 709 MB fetched. (a) 2 m temperature equal to session 113's stored values in every bit at the six development airports, 92 of 92 cycle-steps each (same four points); (b) five messages fetched again, SHA-256 equal 5 of 5; (c) kept plus gaps equals planned; (d) all ten fields present in v1 and v2; (e) 0 rows valid after 2026-07-31T23:00Z.
- **F179.6 Cost.** 2,084 cycles, 18 month chunks, 18,720 files, 170,564 messages, about 122 GB transferred, about 115 MB written. About 8 h at 8 workers without throttling (3.5 h fetching at 13.7 messages per second, 4.6 h of serial planning at about 0.8 s per request); 12 to 16 h or more if throttled as on 2026-11-17.
- **F179.7 The owner's command** (from MLwx at the committed version; re-run until "failed chunks none"; finished chunks are skipped): `caffeinate -i .venv/bin/python scripts/session135_aifs_pull.py --pull --months 2025-02..2026-07 --workers 8 --outdir ../MLwx-aifs-pull`, then `.venv/bin/python scripts/session135_aifs_pull.py --verify --outdir ../MLwx-aifs-pull`.
- **F179.8 Readings for the owner.** (1) ECMWF's bucket refused most object reads (S3 "SlowDown", HTTP 503) for about 1 h 45 min; listings still answered. The test chunk needed three runs, the last for one day at 4 workers. The method was not changed. (2) A month chunk holds about 9,500 messages and succeeds or fails whole: one message refused 5 times fails it, and it is fetched again from the start. Under today's throttling a month may fail repeatedly. The script also takes day chunks (`--days 2025-02-26..2026-07-31`, 521 chunks) with the same files; one form per folder only, since `--verify` checks within chunks and not overlaps or coverage. The owner chooses. (3) No field changes at AIFS v2: names, units, level types and levels are identical; only `generatingProcessIdentifier` changes (3 in March 2025, 5 from May 2026). ssrd is accumulated from step 0 (J m**-2); tcc is in %. (4) Session 113's values show a second grid geometry (first longitude 0) on 2026-05-12 06z to 2026-05-13 00z only. The test chunk did not reach it; the pull finds positions for each geometry, and the mapping is unit-tested. (5) Session 90's counting functions take their window from two module constants; the script sets them on the imported module, so the functions' code is unchanged. (6) Planning is serial and is about half the estimated time. (7) Operational files exist from 2025-02-25 06z (F156); D130.9 starts at 2025-02-26 00z, so the three earlier cycles are not pulled.
- **F179.9 Checks.** Tests: 466 run, 1 skipped; before this entry only the citation test failed, on D130's forward citation of F179. Scope and size checks are in the output file.
- **F179.10 Not done.** No full pull (the owner's, D130.9); no feature mapping (session 136's ruling); no screening, fit, error or score; no IEM call; no SPEC, RESULTS, ANALYSIS or README change; no commit.
