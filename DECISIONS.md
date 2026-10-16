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
- D106: F154 accepted, and a fixed plan for a descriptive analysis of the stage C curve and its daily maximum.
- D107: F155 accepted with two rulings, the comparison sources and their pull on spent years, and session 114's comparison rules.
- F156: session 113's finding (the comparison sources probed, gated and pulled on spent years, and the official daily maximum).
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

## 2026-10-14: Session 112 decision: F154 accepted, and a fixed plan for a descriptive analysis of the stage C curve and its daily maximum (owner, planning chat)

**D106. Owner decisions, planning chat (after session 111's commit and the owner's redeploy): F154 accepted, and a plan for a descriptive statistical analysis of the stage C curve and its daily maximum on spent data, fixed before any of its numbers is computed (D105.10).** Written at the start of session 112, before any other edit. No value on or after 2026-08-01 has been scored.

- **D106.1 F154 accepted,** with its F154.9 readings as written. Reading (4) stays open: Gates C and D are not changed or run.
- **D106.2 Status.** Descriptive only (SPEC 2.5, as F96). It changes no verdict, model, setting, rule, bar or table, and nothing in D73, D77.6 or D105.5. It is not stage C's look: the look script's `--look` mode is not run (D101.2); the claim airports' frozen models are refitted by the look's route only to regenerate predictions already scored, and must reproduce F150 exactly. Nothing is selected or tuned on it. Ideas go into a "candidates for later" list with their evidence; any change to the product is a later build choice judged by D89 on the development airports. The owner chooses later which statistics to put first; the appendix keeps every statistic planned here, and any item picked after the results were seen is labelled so.
- **D106.3 Data.** The 12 airports of D103.4 only; nothing from the 37 of F153.6 (D104.8). Development airports: out-of-fold predictions for D89.3's three test years (2023-24, 2024-25, 2025-26) by F147's route, each tracker starting at b = 0 at its fold's T0 (D97.7). Claim airports: looks A and B by F150's route (models trained before 2024-08-01 and frozen; trackers from 2024-08-01 through both looks). All cycle hours, leads 3 to 48. Nothing valid after 2026-07-31T23:00 UTC. Training-period rows give context only (climatology, constant bias, linear MOS, bin edges), never an accuracy figure. Development airports' figures carry a flag that their build choices used these folds; the claim airports lead every summary.
- **D106.4 Forecasts compared** (references, never deployed). Raw GFS (elevation-adjusted, SPEC 5.2); persistence (D100.5); climatology (the mean training observation at the same airport and valid UTC hour, within 15 days of the same day of year); constant bias (raw GFS plus the mean training residual per airport, cycle hour and lead); linear MOS (ordinary least squares with an intercept on SPEC 8's features, predicting the residual, per airport, cycle hour and lead, on the baseline's own training rows; no drift correction); the baseline (D88.4); the curve (D97). Each forecast's daily maximum is read off its own curve by D98.10; persistence's is the latest observed daily maximum known at the run (D100.5).
- **D106.5 Metrics.** Error e = observed minus forecast. MAE, mean error, RMSE, the median and 90th and 95th percentiles of |e|, the share of |e| at most 1 and at most 2 degrees C, and skill 1 - MAE / MAE(reference). Distributions as box plots, histograms and ECDFs. Conditional bias: mean e per decile of the forecast value (decile edges per airport from training rows) and the slope of observed on forecast.
- **D106.6 Breakdowns.** Primary, known when the run is issued: airport; lead, and lead bands 3 to 12, 13 to 24, 25 to 36 and 37 to 48; cycle hour; local hour; month, and seasons named by months (Dec-Feb, Mar-May, Jun-Aug, Sep-Nov); forecast cloud cover; forecast 10 m wind; raw GFS's diurnal range over the local day; raw GFS's 24 h change at leads 24 to 48 (raw at that lead minus raw at the lead 24 hours earlier, same cycle); |b|; the curve minus raw GFS. Secondary, known only afterwards: the observed diurnal range and the observed 24 h change. Each continuous condition is cut into terciles per airport from training rows (per fold at the development airports), before any test value is read. No other bin edges are tried.
- **D106.7 The daily maximum (the main section).** Definitions as D82.8 and D98.10, unchanged. (a) Scored days: every metric of D106.5 on D98.10's days (one cycle per day), reproducing F147.6 and F150. (b) Every cycle: for each cycle, every local day wholly inside leads 3 to 48, labelled day 1 or day 2 by its order in that run, and by cycle hour. (c) Extremes: the hottest and coldest 10 % of days per airport, by forecast maximum (primary) and by observed maximum (secondary). (d) Why it reads low (F147.8(3)): e_max = [observed maximum - forecast at the observed peak hour] - [forecast maximum - forecast at the observed peak hour]; the means of both terms (peak level and timing). (e) Peak hour: forecast minus observed, in hours. (f) Edge-of-day days: the raw, corrected or observed maximum in the first or last local hour; counts, two-by-two tables, and errors on those days (D105.5(i)'s quantity, on spent data). (g) Ranges: the 5th, 10th, 25th, 50th, 75th, 90th and 95th percentiles of e_max per airport, season and day 1 or 2; and of hourly e per airport and single lead (3 to 48), all seasons together, and per airport, single lead and season, each with its n; lead bands are a summary of these.
- **D106.8 Curve shape and consistency.** Per local day, from D98.10's cycle: forecast against observed diurnal range, and peak hour. Smoothness: the mean |second difference| over consecutive leads within a cycle, for raw GFS, the curve and the observations, on hours where all three exist. Run-to-run change: |forecast for valid time v from cycle c minus that from cycle c - 6 h|, for raw GFS and the curve, per lead; and the same for the daily maximum between successive cycles.
- **D106.9 Drift.** MAE and mean error of the curve and the baseline by days since the tracker started (0 to 30, 31 to 90, 91 to 180, 181 to 365, over 365); b over time per airport.
- **D106.10 Model internals.** LightGBM's own feature contributions (`pred_contrib=True`, no new package) on test rows at leads 6, 12, 18, 24, 36 and 48, all cycle hours: the share of mean |contribution| per feature, and the contribution against forecast temperature and cloud cover. Read for physical sense only.
- **D106.11 Limits.** The share of whole-degree observations per airport, and the rounding floor (rounding to whole degrees alone gives a mean |error| of 0.25 degrees C); the airports with sea in the grid box (KSFO, CYYZ, ZGSZ, NZWN) read separately; the spread across test years shown beside each interval.
- **D106.12 Uncertainty.** 95 % intervals by moving-block bootstrap of 7 consecutive days (F125.3's method) on daily aggregates, seed 112: 10,000 resamples for each airport and test year's headline figures, 2,000 for breakdown cells. Formal tests per airport, its test years pooled: Diebold-Mariano on the daily mean of |e_A| - |e_B|, with a Newey-West variance at 7 lags and a two-sided normal p-value, in four families: (1) the curve against raw GFS, hourly; (2) the curve against raw GFS, daily maximum; (3) the curve against linear MOS, hourly; (4) the curve against the baseline, hourly. Benjamini-Hochberg at 0.05 across the 12 airports within each family. Everything else is descriptive.
- **D106.13 The ZUCK case.** Cycle 2026-10-13 06z's logged forecast at ZUCK (MLwx-live, forecast columns only) is plotted with its local days, as a case study placed beside D106.7(f)'s spent-data figures. No observation, error or snapshot (`obs/`) valid on or after 2026-08-01 is read (D105.6).
- **D106.14 Outputs.** `ANALYSIS.md` at the repo root: a draft field guide first, then an appendix with every statistic and figure planned here, and the candidates for later. Figures in `figures/analysis/`; tables in `data/processed/session112_analysis/`; the regenerated predictions outside the repo, with SHA-256 in a meta file; one script; F155.
- **D106.15 Later sessions (tentative, each fixed in its own entry before its data is scored).** Session 113: a read-only probe and a pull, on spent years only, of comparison forecasts: ECMWF IFS (first), ECMWF AIFS, NBM on the full curve (D72.8), GFS MOS (MAV), WeatherNext if the owner's access request is granted, and the official daily maximum at DSM, RNO, KSFO and KORD. Session 114: the comparisons, with the same four-point interpolation and elevation treatment, the same cycles, common valid times and common windows, raw GFS beside each raw competitor, and our maximum also sampled at each competitor's time step; then the field guide finished.
- **D106.16 Live index.** Removed (archived): F154, which is settled. Added: D106 and F155. After session 112: D93, D103, D105, D106, F155.

---

## 2026-10-15: Session 113 decision: F155 accepted, the comparison sources and their pull on spent years, and session 114's comparison rules fixed before any score (owner, planning chat)

**D107. Owner decisions, planning chat (after session 112's commit): F155 accepted with two rulings; the sources, windows and pull rules for the probe and pull of comparison forecasts and the official daily maximum on spent years (D106.15); and the rules for session 114's comparisons, fixed before any competitor value is scored.** Written at the start of session 113, before any other edit or network call. No competitor value has been read, and no value on or after 2026-08-01 has been scored.

- **D107.1 F155 accepted,** with its F155.7 readings. Two are owner rulings. (a) A run (leads 3 to 48) never holds a whole second local day, so D106.7's "day 1 or day 2" is replaced by the cycle hour, which fixes how far ahead a local day lies. D106.15's plan for session 114 is read the same way, and no later entry uses "day 2" for a run of leads 3 to 48. (b) The tercile edges for |b| and for the curve minus raw GFS come from the test period's forecast values (forecast side only), because neither quantity has a training value.
- **D107.2 Status.** Session 113 probes and pulls; it scores nothing. It computes no error, and compares no competitor value, official maximum or forecast with an observation, with our forecasts or with another source, except D107.8's agreement count between the two official sources. Session 114's comparisons are descriptive (D106.2): no verdict, model, setting, rule, bar or table changes, and nothing is selected or tuned on them. Ideas go to `ANALYSIS.md`'s candidates for later.
- **D107.3 What seeing these years costs (D72.6).** Once session 114 scores a competitor at an airport and test year, that year counts as used for that model at that airport, and a later stage D spent-year test of that model there may not use it. Every test year is pulled, so no spent-year test of ECMWF IFS or AIFS remains at these 12 airports; claims for those models come from new airports or forward years (D72.4). The 37 airports of F153.6 are not touched. D107.9's rules are fixed here, before any score, and are not changed after one.
- **D107.4 Sources, in this order.** ECMWF IFS open data (AWS `ecmwf-forecasts`); ECMWF AIFS Single (same bucket); NBM CONUS (the `core` grid on AWS, and the NBS station text from IEM's MOS archive); GFS MOS (MAV, IEM's MOS archive); the official daily maximum (D107.8). WeatherNext is deferred: the owner has no access yet; once access is granted it gets its own probe and pull under D107.5 to D107.10, and D107.3 applies to it in the same way. ICON is dropped: the official archive keeps 24 hours (F123.3); the third-party copy needs an account and accepted conditions, and its completeness is unknown; and its icosahedral grid cannot take D106.15's four-point interpolation. D76.2 stands.
- **D107.5 Airports and windows.** ECMWF at the 12 airports of D103.4. NBM and MAV at DSM, RNO, KSFO and KORD; NBM also at CYYZ if the probe finds it inside the CONUS grid (grid) or listed as an NBS station (text). Each airport's own test periods: development airports, cycles 2023-08-01T00 to 2026-07-31T18 (D89.3's test years); claim airports, cycles 2024-08-01T00 to 2026-07-31T18 (D100.4). All four cycles (00, 06, 12, 18 UTC) where a source has them; a cycle a source lacks is counted, never filled. Leads 3 to 48 at each source's own steps. Nothing valid after 2026-07-31T23:00 UTC, and no maximum whose window ends after it. IFS's 0.4 degree months (to 2024-01-31) are kept and labelled, as are IFS's cycle changes (48r1, 49r1, 50r1), AIFS's versions and NBM's (v4.2, v4.3, v5.0, v5.0.14; D77.7 with F127.7's corrections).
- **D107.6 What is kept per value.** Gridded sources: 2 m temperature at the four grid points around IEM's airport position (D83.3), with bilinear weights computed as session 76's `bilinear_from_gid` (the GFS route), the nearest point marked, and each point's model terrain height where the source carries an orography field (recorded as absent otherwise). Text sources (MAV, NBS): values as issued in whole degrees F, also converted to degrees C exactly. Each source's own maximum field where it exists (ECMWF's maximum 2 m temperature parameter, NBM's TMAX grid, NBS's TXN, MAV's X), with its window in UTC and its stated definition. Point values only, as gzipped CSVs under `data/processed/session113/`, each under 50 MB, with a manifest of every URL, byte range and index line; no GRIB file is kept (D47).
- **D107.7 Cost gate.** Before each gridded pull, the probe measures the bytes and time per message on spent dates and estimates the source's total. A source whose estimate exceeds 250 GB of downloads or 24 hours of wall time is not pulled; its estimate is reported and the owner decides. NBS is pulled whatever the NBM grid estimate is. At most 8 requests run at once.
- **D107.8 The official daily maximum.** At DSM, RNO, KSFO and KORD: the NWS daily climate report (CLI) maximum from IEM's archive (primary) and GHCN-Daily TMAX from NCEI (cross-check), each station's identity checked by its metadata. The climate days of each airport's test periods whose window ends on or before 2026-07-31T23:00 UTC. The climate day runs midnight to midnight local standard time; this is recorded, not adjusted. Session 113 reports how many days the two sources agree on after exact conversion, and nothing else about their values.
- **D107.9 Session 114's comparison rules.** (a) Primary: same cycle. Each competitor's run at the same nominal cycle as our GFS cycle. Each source's arrival latency (D107.10) is reported beside it and not adjusted for. (b) Hourly: common valid times at the competitor's own steps and a common window (the leads where both have values); raw GFS beside each raw competitor; gridded values with the same four-point interpolation and elevation treatment as GFS (D106.15) where the source's terrain heights exist, otherwise labelled; MAV and NBS as issued. (c) The daily maximum: ours read off the curve (D98.10) and also sampled at each competitor's time step (D106.15); each competitor's own maximum field where it exists, labelled with its definition (its window and UTC span); otherwise read off its own steps. Days are grouped by cycle hour (D107.1(a)). (d) Truth: our hourly-report maximum (D82.8) for every comparison. At the four US airports, the official maximum as a second truth: to measure its gap from our hourly-report maximum on the same days, and to score NBM's and MAV's maxima, and ours, against the truth NBM and MAV forecast. Each window difference (civil local day, local standard time day, daytime windows) is labelled. (e) Metrics and uncertainty as D106.5 and D106.12: 7-day moving-block bootstrap, seed 114, 10,000 resamples for headline figures and 2,000 for breakdown cells; Diebold-Mariano on the daily mean of |e_A| - |e_B| with a Newey-West variance at 7 lags, the curve against each competitor, one family per competitor and output (hourly, daily maximum), Benjamini-Hochberg at 0.05 across the airports in each family. Everything else is descriptive. (f) Claim airports lead; development airports carry D106.3's flag. Version segments are labelled and descriptive only.
- **D107.10 Latency.** For GFS (`noaa-gfs-bdp-pds`), ECMWF and the NBM grid: the time each cycle's 48 h file was written to the archive, from listing timestamps on spent dates, minus the cycle time, per cycle hour (median and range), labelled "archive write time" (it may be later than public release). For MAV and NBS: the issuance time in the product header where IEM keeps it, otherwise the documented time, labelled as such.
- **D107.11 Live index.** Removed (archived): F155, which is settled. Added: D107 and F156. After session 113: D93, D103, D105, D106, D107, F156.

---

## 2026-10-16: Session 113 finding: the comparison sources probed, gated and pulled on spent years, and the official daily maximum

**F156. D107 was recorded first. Each comparison source was probed on spent dates, the cost gate was applied, and AIFS, the NBM grid (owner's override), NBS, MAV and the official daily maximum were pulled at each airport's own test periods; IFS was not pulled (gate, after the owner's re-measurement). Nothing was scored (D107.2): no error, no observation file, stage C table or prediction file opened; no value valid after 2026-07-31T23:00 UTC kept or used; nothing from the 37 airports of F153.6 read; no GRIB kept. Full real output: `notes/session-113-output.txt`. Run 2026-10-15 to 2026-10-16. Python 3.12.2, eccodes 2.48.0, numpy 2.5.2, requests 2.34.2.**

- **F156.1 D107 and the self-checks.** D107 appended byte-equal (17 lines, `diff` and `cmp`), 0 em-dashes. `--check` 13 of 13 PASS: the weights function reproduces every airport's four GFS points and weights exactly (12 of 12; IEM set at the development airports 6 of 6); made-up regular and Lambert grids (with alternate row scanning) give weights summing to 1 and the right corners; guards 8 of 8 plus the CLI filter case; F to C exact 7 of 7; cycle lists 12 of 12 (development 4,384, claim 2,920).
- **F156.2 Owner rulings and corrections made during the session (asked in chat).** (1) A correction to D107.6's wording: at the six development airports the four points and weights are kept around both the positions file's lat_used/lon_used (GFS's point, SPEC 3.4) and IEM's position, each labelled, with terrain heights for both where the source has them; the claim airports use IEM's position only (also GFS's). D107 stays byte-equal. (2) Time zones from D98.10(a) (development) and `session90_airports.csv` (claim), 12 of 12 equal to `src/mlwx/data/gfs_airports.csv`; IEM positions of LFPG, KDSM, YSDU, KRNO from SPEC 3.4's first table; `height_diff_m` recorded as absent there, labelled (the constants are in `session37_elevation_correction_params.csv`, and KSFO's per F116 and F117.3). (3) A correction to D107.5's "requested" wording, citing F123.9 and F127.3: IEM's CLI service takes only a whole year, so 2026 was requested whole, each record filtered on its date field alone in memory before any other field, climate days ending after the limit dropped unread (76 per station), the raw 2026 response never written or printed. (4) A correction to D107.5 and Step 7: NBS keeps both run sets, 00/06/12/18 and 01/07/13/19 UTC, each labelled with its own cycle hour and a nominal-cycle column (01 to 00, 07 to 06, 13 to 12, 19 to 18); the later runs are labelled "one hour later than the nominal cycle", not counted as lacking; matching by valid time, never by lead. (5) IEM holds the NBS run of 2025-10-14T07 twice: identical copies at KRNO and KORD (one kept); differing at KDSM (TXN at 2025-10-16T00, lead 41), KSFO (TMP at 2025-10-15T15, lead 32) and CYYZ (TMP at 2025-10-14T12, lead 5), so there the run is a gap, "issued twice with differing values"; IEM gives no issuance time to order the copies. (6) In three NBM files of 2024-05-15T00 (f026, f027, f031) the .idx offset for TMP 2 m holds no GRIB message (.idx rewritten 2024-05-16): counted as gaps, "index offset does not match the file". (7) IFS re-measured at 16 and 32 requests at once (override of the 8-request limit for this only). (8) An override of D107.7 for the NBM grid: pulled in this session (estimate 266.6 GB transferred, none stored), NBS kept as well.
- **F156.3 Cost gate (D107.7; 60 spent-date files per source, 8 at once).** IFS 65.6 GB, 26.51 h: over (hours). AIFS 9.6 GB, 4.71 h: PASS. NBM grid 266.6 GB, 6.72 h: over (bytes), pulled under ruling (8): 267.14 GB and 7.80 h measured, plus 7.04 GB for one rerun chunk. IFS at 16 at once: stopped on repeated HTTP 503 (throttling), no figure; at 32: 67.1 GB, 65.80 h. Neither is under 24 h, so IFS was not pulled (Step 5 not done). ECMWF's bucket gave about 0.7 MB/s and throttles more as concurrency rises; NOAA's about 11 MB/s.
- **F156.4 Coverage, cycles with 2 m temperature kept per test year (2023-24/2024-25/2025-26), claim airports first.** AIFS, all 12 airports alike: -/627/1,459 (from its first operational run, 2025-02-25T06; the 2026-07-31T18 run has no step on or before the limit), 16,660 messages, 0 gaps. NBM grid: KORD, CYYZ -/1,460/1,460; KDSM, KRNO, KSFO 1,464/1,460/1,460; 176,888 messages, 5 message gaps (the three of F156.2(6) and 2026-05-05T00 steps 6 and 34, no index line). NBS (nominal cycles with a kept run): KORD -/1,458/1,458; CYYZ -/1,458/1,456; KDSM 1,463/1,458/1,456; KRNO 1,462/1,458/1,458; KSFO 1,462/1,458/1,457 (at each station one of these, 2026-07-31T18, is a run with no projection on or before the limit, not an archive gap; mav_gaps.csv and nbs_gaps.csv label it "no run paired"). MAV: KORD -/1,457/1,458; KDSM, KRNO, KSFO 1,464/1,457/1,458 (at each station one of these, 2026-07-31T18, is a run with no projection on or before the limit, not an archive gap; mav_gaps.csv and nbs_gaps.csv label it "no run paired"). IFS (probe listing only): development 4,381 of 4,384 cycles (3 missing, one day in 2024-02), claim 2,920 of 2,920. Every pull's checks passed: rows per airport, set and cycle hour equal expected minus gaps; latest valid time and maximum window end on or before the limit; 0 values outside -70 to 60 C; 20 of 20 re-fetches identical.
- **F156.5 Versions and run sets.** IFS: 0.4 degree grid to 2024-01-31; a Ni 1439 0.25 degree grid on 2024-02-01 and 02-02; Ni 1440 after; 06/18 UTC under `scda` to 2026-05-11, `oper` from 2026-05-12; generatingProcessIdentifier 154 to 158 at 2024-11-13 00z (49r1), 158 to 161 at 2026-05-13 00z (50r1). AIFS: 3 to 4 at 2025-08-28 00z, 4 to 5 at 2026-05-13 00z. NBM grid: steps hourly 3 to 36 then 3-hourly to 48 until 2026-05-04, hourly 3 to 48 from 2026-05-05. NBS: 01/07/13/19 UTC runs only to 2026-04-30T06, both sets for 20 nominal cycles (2026-04-30T12 to 2026-05-05T06), 00/06/12/18 only from 2026-05-05T12.
- **F156.6 Maximum fields and terrain.** IFS mx2t3 (the 3 hours ending at the step, UTC; stepType max) from 2024-11-12/13 (49r1), absent on the 0.4 degree grid. AIFS: no maximum field. NBM grid TMAX: 12-hour windows ending at the step, each 12z to 00z UTC (00z run: 12-24 and 36-48). NBS TXN: v5.0 card, 12Z to 06Z the next day, at 00Z (earlier versions' cards not read). MAV X: daytime 7 a.m. to 7 p.m. LST (MDL). Terrain: IFS z at step 0 only from 2024-12-03 (absent on the 0.4 and Ni 1439 grids); AIFS z present; NBM grid none.
- **F156.7 The official maximum (D107.8).** CLI (IEM): KDSM DES MOINES, KRNO RENO/CANNON INTL, KSFO SAN FRANCISCO INTL, KORD CHICAGO O HARE (3.07 km from IEM's ORD position). GHCN-Daily: USW00014933, USW00023185, USW00023234, USW00094846 (0.01 to 3.06 km). Days with both, and agreeing after exact conversion: KDSM 366, 349; 363, 321; 364, 364. KRNO 366, 364; 362, 362; 364, 364. KSFO 365, 365; 362, 362; 362, 362. KORD -; 365, 327; 364, 364. Nothing else about the values was computed.
- **F156.8 Latency (D107.10), archive write time of the 48 h file minus the cycle, median over the four cycle hours (range).** GFS 3.74 to 3.81 h (3.67 to 7.46). IFS 7.21 to 7.92 h (6.45 to 37.31). AIFS 5.14 to 5.27 h (5.07 to 30.93). NBM grid 0.81 to 1.07 h (0.62 to 44.77). MAV and NBS: documented time only; IEM keeps no product header for them.
- **F156.9 Readings for the owner.** (1) IFS is not pulled, so D107.9's ECMWF IFS comparisons cannot run in session 114 until a follow-up session pulls it. At 8 at once the estimate is 26.51 h, so that session needs the owner's D107.7 override of the hours; `--override` now lifts the gate for IFS as well as the NBM grid, and without it `--pull ifs` stops (checked). (2) Session 114: the NBS 01/07/13/19 UTC runs hold one hour more data than the GFS cycle they pair with. (3) NBM grid terrain is absent, so its elevation treatment (D107.9(b)) is labelled. Also absent: IFS terrain before 2024-12-03 and mx2t3 before 49r1. (4) NBM's alternate row scanning is handled (the positions file maps odd rows; eccodes' nearest-point call was already right, so sessions 85 and 87 are unaffected). (5) The NBS TXN definition of versions before v5.0 was not read. (6) The official sources agree on fewer days in 2024-25 at KDSM (321 of 363) and KORD (327 of 365) than in the other airport-years (349 of 366 to all days); no cause was looked for. (7) KORD's CLI site is 3.07 km from IEM's ORD position. (8) Retry handling was changed in the new script only: longer back-off on HTTP 503 and a 5-minute pause between chunk attempts. ECMWF throttling cost the AIFS pull three chunk reruns.
- **F156.10 What was not done.** Step 5 (IFS pull). No score, error or comparison beyond F156.7's count. No change to SPEC, RESULTS, README, CLAUDE, ANALYSIS, any existing script, table, model folder, `src/mlwx/` or `tests/`. Session 87's script was not run; session 85's was read only.
- **F156.11 Pointers.** `scripts/session113_comparison_pull.py`; `data/processed/session113/` (probe.csv, cost.csv, cost_ifs_w32.csv, latency.csv, listings, positions files, and per source `<source>_<airport>.csv.gz` with manifest or queries, gaps and meta files; nbs_runs.csv, nbs_duplicates.csv, official_agreement.csv); `notes/session-113-output.txt`.
