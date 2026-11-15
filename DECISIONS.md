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
- D128: F176 accepted, stage H opened on GFS, a range test on 2026-27 chosen in outline, and the rules of stage H's first build choice.
- F177: session 133's finding (stage H's first build choice: a central 80 % range for each output, T1 hourly and M1 daily maximum).
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

## 2026-11-15: Session 133 decision: F176 accepted, stage H opened on GFS, a range test on 2026-27 chosen in outline, and the rules of stage H's first build choice (owner, planning chat)

**D128. Owner decisions, planning chat (after session 132's commit): F176 accepted; stage H opened on GFS; a pre-registered range test on 2026-27 chosen, in outline; the rules of stage H's first build choice, fixed before any value is computed; and Live index changes.** Written at the start of session 133, before any other edit. No 2026-27 value has been read or scored.

- **D128.1 F176 accepted,** with its readings (F176.7). Whether ANALYSIS.md Part 1's captions and RESULTS change because of the airport-position rows (D127.5) stays with the owner.
- **D128.2 Stage H is opened, on GFS (D121.2(4), SPEC 6).** Its first product: one central 80 % range with each forecast, for both outputs (the hourly curve at leads 3 to 48, and the daily maximum of D98.10), at the 12 airports of D103.4. The central forecast does not change. All data used is GFS v16.
- **D128.3 A range test on 2026-27 will be pre-registered (owner, 2026-11-15).** Outline only; it becomes binding in session 134's entry, which is written before any 2026-27 value is scored and before the first look of D73 or D105.5. The 12 airports; both outputs; D105.5(e)'s periods; the ranges as frozen in session 134, applied to the live forecasts as logged. Per airport, period and output, two parts, both needed to pass: (a) honest odds: the share of observations inside the range has a 95 % interval by F125.3's method that contains 0.80; (b) useful: its interval score (D128.5) is lower than that of a reference range on raw GFS built from raw GFS's own past errors; a tie fails. Expectation: part (b) passes at all 12 airports in period A; none is stated for part (a). Left to session 134's entry: the reference's exact construction, and how ranges are obtained for forecasts issued before the ranges go live (the log carries no model inputs and its columns are pinned, D125.4).
- **D128.4 The build choice: data (D89, SPEC 2.5).** The six development airports only (EGLC, LFPG, KDSM, YSDU, KRNO, KSFO). Hourly: the rows of session 112's predictions (`../MLwx-stagec/analysis112/pred_<ICAO>.csv.gz`, each equal to `meta.txt`'s SHA-256) whose `status` is `scored`, in D89.3's test years 2023-24, 2024-25 and 2025-26; these are out of sample. Daily maximum: the rows of `data/processed/session104_dailymax_days.csv` with `common` true (D98.10's days). Training rows for the quantile models: D89.3's, read with session 97's and session 104's loaders. Nothing valid after 2026-07-31T23:00 UTC; nothing at the claim airports.
- **D128.5 Ranges, metric and scoring periods.** A range is [l, u] and y is the observation (`obs`, or `obs_max`). Coverage is the share of rows with l <= y <= u. The interval score at 80 % is (u - l), plus 10 (l - y) when y < l, plus 10 (y - u) when y > u; lower is better. Per airport: the mean over its rows; the headline: the mean of the six airports' values (as D89.5). Scoring periods: 2024-25 and 2025-26, so that every table has an earlier out-of-sample year to be built from; 2023-24 only feeds tables. Percentiles: numpy's default (linear) 10th and 90th.
- **D128.6 Hourly candidates.** e = obs - curve, from the scored rows of the same airport in the test years before the scoring period. T1: l = curve + P10(e), u = curve + P90(e), one pair per airport. T2: one pair per airport and lead band (3 to 12, 13 to 24, 25 to 36, 37 to 48). T3: one pair per airport, lead band and season (Dec to Feb, Mar to May, Jun to Aug, Sep to Nov, by the month of `local_date`). Q: for each airport, fold, cycle hour and lead (D95.2's cells), two LightGBM models on that fold's training rows (D89.3), with the 15 recipe inputs in G15's order and the baseline's target, and `LGB_PARAMS` unchanged except objective `quantile` with alpha 0.1 and 0.9; l = raw_gfs + q0.1 + b and u = raw_gfs + q0.9 + b, with b the row's own `b` (curve minus baseline). Where q0.1 > q0.9 the two are swapped, and counted.
- **D128.7 Daily-maximum candidates.** e = obs_max - curve_max, from the same airport's days in the periods before the scoring period. M1: one pair per airport. M2: one pair per airport and season (by `local_date`). No model of its own (F148).
- **D128.8 The rule (as D89.6, for ranges).** For each output the candidates are taken in order (T1, T2, T3, Q; M1, M2); the first is the incumbent. A challenger replaces the incumbent only if all four hold: (i) its headline interval score over both scoring periods together is more than 1 % lower; (ii) it is lower at 4 or more of the 6 airports (both periods pooled); (iii) its headline is lower in each scoring period; (iv) its coverage, pooled over the six airports, is between 0.75 and 0.85 in each scoring period. If the first candidate fails (iv), no choice is made for that output and the finding goes to the owner. Each output's winner goes to session 134. These are build-choice scores, never results (SPEC 2.5).
- **D128.9 Descriptive, never used by the rule.** For every candidate: coverage, mean width and interval score per airport and scoring period, and by lead band, season and cycle hour; and by tercile of cloud cover and of GFS's run-to-run change (|raw_gfs from cycle c minus raw_gfs from cycle c - 6 h, same valid time|; rows with no earlier partner are counted and left out), with tercile edges per airport from the earlier periods' rows. Ranges on raw GFS built as T1 to T3 and M1 to M2 from raw GFS's own errors (obs - raw_gfs; obs_max - raw_gfs_max), with the same figures. For each output's winner, per airport and scoring period: coverage with its 95 % interval by F125.3's method (seed 133), and whether it contains 0.80.
- **D128.10 Where results go.** `scripts/session133_ranges.py`; tables in `data/processed/session133_ranges/` with a meta file (script SHA-256, input SHA-256, versions, run time). Nothing in the live tool, `src/`, `deploy/`, SPEC, RESULTS or ANALYSIS changes.
- **D128.11 Plan.** Session 133: this entry, the comparison, F177. Session 134: freeze each output's winner at the 12 airports (built from each airport's out-of-sample errors; for Q, refit on all data to 2026-07-31 as the live models were), record the test's pre-registration (D128.3), and add the ranges to the live tool, then the owner redeploys; the page labels the ranges as not yet verified until the test's look. The test's scoring script is written and gated in a later session, before the first look of D73 or D105.5. Later: ranges from GFS's ensemble (GEFS) as a challenger, once GEFS's next version is out, with any claim for it on 2027-28 or on new airports. A GFS v17 Service Change Notice goes ahead of all of these.
- **D128.12 Live index.** Removed (archived): D127 and F176, which are settled (F176 is accepted; the open caption question is carried in STATUS). Added: D128 and F177 (F177 when it is written). After session 133: D93, D103, D105, D118, D128, F177.

---

## 2026-11-15: Session 133 finding: stage H's first build choice, a central 80 % range for each output, on the six development airports

**F177. D128 was recorded first. The comparison of D128.6's candidates ran on the six development airports' spent out-of-sample errors, offline. Build-choice scores, never results (SPEC 2.5): no 2026-27 value, nothing valid after 2026-07-31T23:00 UTC, nothing from MLwx-live, and no claim-airport or live-airport file was used. Winners: T1 for the hourly curve, M1 for the daily maximum. Full output: `notes/session-133-output.txt`; tables in `data/processed/session133_ranges/`. Run 2026-11-15. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

- **F177.1 Start and D128.** HEAD 38cf1b7, tree clean apart from the prompt; 409 tests OK (1 skipped); the three imported scripts, the six development prediction files, the days file and the 12 development tables equal their recorded SHA-256. D128 appended with `sed`, byte-equal by `diff` and `cmp`, 0 em-dashes.
- **F177.2 Gate (D128.7): PASS.** `scripts/session133_ranges.py --gate`: (a) the baseline refit equals the prediction files row for row in 12 of 12 cells; (b) 18 of 18 row counts equal `meta.txt`, every scored row finite; (c) 1,085 to 1,095 common days per airport.
- **F177.3 Q (D128.6).** 4,416 quantile models, fit 324 s (`--score` 434 s in all). Ends swapped where q0.1 > q0.9: 10 rows (KDSM 7, KSFO 2, KRNO 1).
- **F177.4 Hourly ladder (D128.8).** Headline interval score, mean of six airports over both periods (lower is better). T1 (incumbent) 5.3148; pooled coverage 0.7934 (2024-25), 0.8105 (2025-26), so (iv) holds. T2 5.2966, 0.34 % lower, lower at 6 of 6, lower in both periods, coverage 0.7931 / 0.8103: fails (i) only. T3 5.3133, 0.03 % lower, 4 of 6, higher in 2025-26: fails (i) and (iii). Q 5.3433, 0.54 % higher, 1 of 6, higher in 2024-25, coverage 0.6472 / 0.6844: fails all four. **Winner T1.**
- **F177.5 Daily maximum ladder.** M1 (incumbent) 5.0707; coverage 0.7810 / 0.8139, (iv) holds. M2 5.1081, 0.74 % higher, 2 of 6, higher in 2024-25, coverage 0.7471 / 0.8051: fails all four. **Winner M1.**
- **F177.6 The winners' coverage (D128.9, descriptive).** Coverage with its 95 % interval, 2024-25 then 2025-26; raw GFS's twin (RT1, RM1) after "raw". T1: EGLC 0.767 [0.745, 0.789], 0.800 [0.777, 0.824], raw 0.760, 0.799; LFPG 0.758 [0.734, 0.779], 0.821 [0.803, 0.837], raw 0.763, 0.787; KDSM 0.825 [0.810, 0.844], 0.791 [0.765, 0.813], raw 0.829, 0.811; YSDU 0.810, 0.815, raw 0.802, 0.802; KRNO 0.808, 0.827, raw 0.736, 0.800; KSFO 0.792, 0.809, raw 0.762, 0.771. The interval contains 0.80 in 8 of 12 (not EGLC 2024-25, LFPG both, KDSM 2024-25). M1: EGLC 0.767, 0.791; LFPG 0.721 [0.668, 0.764], 0.854 [0.815, 0.890]; KDSM 0.773, 0.775 (raw 0.896, 0.860); YSDU 0.766, 0.844 [0.802, 0.883]; KRNO 0.830, 0.846; KSFO 0.830, 0.774. Contains 0.80 in 9 of 12 (not LFPG both, YSDU 2025-26).
- **F177.7 Against raw GFS (mean of six, both periods).** T1 coverage 0.802, mean width 3.42 C, score 5.315; RT1 0.785, 4.67 C, 7.165. M1 0.797, 3.20 C, 5.071; RM1 0.789, 3.82 C, 6.201. The winner's score is lower than its raw twin's in 24 of 24 airport-periods.
- **F177.8 Splits (hourly T1, descriptive).** Coverage falls with lead: 0.833, 0.805, 0.781, 0.761 by band in 2024-25 (0.851, 0.825, 0.797, 0.775 in 2025-26). Run-to-run change tercile: low 0.828 / 0.849, high 0.754 / 0.765. Cloud cover tercile (2024-25): low 0.809, middle 0.787, high 0.781. Rows with no earlier partner: about 8,630 to 8,760 per airport and period, left out of the change split.
- **F177.9 Tests and documents.** `tests/test_session133.py` (17 tests); one entry each in `tests/README.md` and `scripts/README.md`'s map.
- **F177.10 Checks.** Tests: 426 run, 1 skipped; before this entry, only the citation test failed, on D128.12's forward citation of F177. Scope: PASS. Protected folders unchanged: PASS. Em-dashes in added lines: 0.
- **F177.11 Readings for the owner.** (1) The prompt's D128 block had no `---` line before its heading, so the archive tool could not split F176 from D128 (two test failures). By the owner's ruling, one `---` line and one blank line were inserted between F176's last line and D128's heading; `diff` shows only those two lines added, and D128's text is unchanged. (2) D128.6 says "15 recipe inputs"; G15's recipe has nine. The nine were used, and gate (a) shows they equal the baseline's. (3) The cloud-cover tercile tie rule was changed after a rehearsal with Q stubbed (into a temporary folder) and before the real `--score` run: the top edge was 100 %, the earlier maximum, which left the "high" tercile empty at EGLC and LFPG; now "high" is v >= the edge when the edge equals the earlier maximum. It changes only descriptive figures. (4) Pooled coverage for (iv) is read as all six airports' rows pooled. (5) Other choices D128 left open were fixed in the script's docstring before `--score` ran: strict comparisons in (i) to (iii), (iv) inclusive; seasons by `local_date`'s month; tables by `numpy.percentile` (linear) from earlier periods only; terciles for the hourly output only; the change partner is cycle c - 6 h at lead L + 6 of any status; bootstrap seed 133, 10,000 resamples, day as the resampled unit. (6) Q's ranges were far too narrow (coverage 0.65 to 0.68).
- **F177.12 Not done.** No range frozen at the 12 airports, no pre-registration and no live, `src/`, `deploy/`, SPEC, RESULTS or ANALYSIS change (D128.10, D128.11); no commit.
