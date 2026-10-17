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
- D108: F156 accepted, IFS deferred to the owner's hand pull, and the comparison choices D107.9 left open fixed before any score.
- D109: an observation plausibility check at the 12 stage C airports before IFS; IFS moves to session 116.
- D110: F158 accepted, the observation check extended to all 51 airports with a dew point cross-check, the live log left out, and IFS moved to session 117.
- F157: session 114's finding (the curve against AIFS, the NBM grid, NBS and MAV on spent years, the official maximum's gap, and the field guide).
- F158: session 115's finding (the observation plausibility check at the 12 stage C airports: flags, rates and exposure).
- F159: session 116's finding (the observation plausibility check at all 51 airports: flags, rates, dew point classes of the stuck runs and exposure).
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

## 2026-10-16: Session 114 decision: F156 accepted, IFS deferred to the owner's hand pull, and the comparison choices D107.9 left open fixed before any score (owner, planning chat)

**D108. Owner decisions, planning chat (after session 113's commit): F156 accepted and its rulings confirmed; the IFS pull deferred and run by hand by the owner; the comparison choices D107.9 left open; the field guide's order; and session 115.** Written at the start of session 114, before any other edit. No competitor value has been scored, and no value on or after 2026-08-01 has been scored.

- **D108.1 F156 accepted,** with its F156.9 readings and the review correction to F156.4 (the 2026-07-31T18 MAV and NBS cycle is a run with no projection on or before the limit). The rulings and corrections of F156.2 (1) to (8) are confirmed as owner rulings.
- **D108.2 IFS.** Not compared in session 114. The owner's D107.7 override of the 24-hour limit is granted for IFS. The owner runs, by hand and outside any Claude Code session, `scripts/session113_comparison_pull.py --pull ifs` unchanged, at 8 requests at once, with a temporary folder outside the repo and an `--override` text naming this entry, rerunning until every chunk is done (finished chunks are skipped), then deletes the temporary folder. Nothing else is run. Session 115 first checks the script's own checks and meta file and records them; no IFS value is read before that. D107.3 applies to IFS as written.
- **D108.3 Positions and elevation.** Every comparison uses the same position raw GFS uses at each airport: the positions file's `gfs` set at the development airports, IEM's position at the claim airports (F156.2(1)). The `iem` set at the development airports is kept and not used here. Elevation treatment as GFS's (SPEC 5.2): forecast plus 7.429 degrees C per km times (model terrain height minus station elevation), the terrain height interpolated with the same four bilinear weights, and the station elevation the one the record uses for GFS's own adjustment. AIFS: its surface geopotential divided by 9.80665, each grid label with its own terrain. NBM grid: no terrain field, used as issued and labelled "no elevation treatment". MAV and NBS: as issued (station forecasts). For IFS (session 115): the 2024-12-03 terrain applies back to 2024-02-03 on the same grid geometry, labelled "terrain from a later date"; days on the 0.4 degree and Ni 1439 grids have no elevation treatment, labelled.
- **D108.4 Choices D107.9 left open.** (a) Rows: the curve's scored rows of F155 (the regenerated predictions, observations and references of session 112), matched to each competitor by valid time; a pair exists where both have a value. NBS runs at 01/07/13/19 UTC pair with the nominal cycle one hour earlier (F156.2(4)), labelled "one hour more data", and are not adjusted. Each competitor's figures cover its own window (AIFS from 2025-02-25T06; NBM, NBS and MAV the full windows), and the curve and raw GFS are rescored on exactly the same rows beside it. (b) Daily maximum. Primary: D98.10's days, one cycle per day. Descriptive: every cycle, each local day wholly inside leads 3 to 48, grouped by cycle hour (D107.1(a)). A competitor's own maximum field is taken from the same run, the window whose start falls on that local date and that lies inside the run's leads 3 to 48; if none does, the day has no value for it and is counted. AIFS has no maximum field: its maximum is the highest of its own steps inside the local day, labelled "6-hourly steps". NBM grid also, descriptive: the highest of its own steps inside the local day, beside TMAX. (c) NBS TXN before v5.0: the session reads the NBM text documentation for each NBM version in the window (documentation pages only) and labels each version's TXN window; a version whose definition is not found is labelled "definition not found" and its days are reported separately. (d) Official maximum at the four US airports: CLI is the truth (D107.8); every score against it is also given on the days where CLI and GHCN-Daily agree after exact conversion (|difference| below 0.05 degrees C), as a check. The gap of the official maximum from our hourly-report maximum is given per airport and test year (mean, MAE, percentiles, share equal), and again with our hourly-report maximum taken over the local standard time day, to separate the window from the measurement. (e) Formal tests (D107.9(e)): one family per competitor and output. Hourly: the curve against the competitor on the paired rows. Daily maximum: the curve's D98.10 maximum against the competitor's maximum (its own field where it exists), both against our hourly-report maximum. Benjamini-Hochberg at 0.05 across the airports in each family. Everything else, including every score against the official maximum, raw GFS against each competitor, version segments and the sampled maxima, is descriptive. (f) Latency from `latency.csv` is printed beside each competitor's figures and not adjusted for.
- **D108.5 Uses of spent data.** As D107.3: once scored here, AIFS's test years at the 12 airports and NBM's, NBS's and MAV's at their airports count as used for those models.
- **D108.6 The field guide.** `ANALYSIS.md` Part 1 is rewritten in this order, chosen by the owner after session 112's results were seen (labelled so, D106.2): (1) the short version (five lines: typical hourly error, daily maximum error, growth with lead, gain over raw GFS, standing against the competitors); (2) how accurate it is x hours out (per airport: hourly MAE and the 10th to 90th percentile range per lead band 3-12, 13-24, 25-36, 37-48; the daily maximum's MAE and range by cycle hour, with the lead at which the day starts); (3) the daily maximum (accuracy, the low reading, the hottest days, and the official-maximum gap at the four US airports); (4) how it compares (one table per output: the curve, raw GFS, AIFS, NBM, NBS and MAV, with IFS shown as "pending (D108.2)"; linear MOS as the yardstick; the formal tests' outcome; at the four US airports the scores against the official maximum); (5) when to trust it less (as now); (6) what limits accuracy (short). Model internals and drift by days since start move to the appendix only. Claim airports first and development airports flagged throughout; figures as ranges across the claim airports, per-airport detail in item 2's table; about two pages.
- **D108.7 Session 115 (tentative, fixed in its own entry before IFS is scored).** Check the owner's IFS pull, then compare IFS under D107.9 and D108.3 to D108.4 with session 114's script, and add IFS to the field guide.
- **D108.8 Live index.** Removed (archived): F156, which is settled. Added: D108 and F157. After session 114: D93, D103, D105, D106, D107, D108, F157.

---

## 2026-10-16: Session 114 finding: the curve against AIFS, the NBM grid, NBS and MAV on spent years, the official maximum's gap, and the field guide

**F157. D108 was recorded first. The comparisons of D107.9 and D108 were run on spent years: AIFS (12 airports, from 2025-02-25), the NBM grid and NBS (KORD, CYYZ, KDSM, KRNO, KSFO) and MAV (KORD, KDSM, KRNO, KSFO); the official maximum (CLI) at the four US airports; ANALYSIS.md's field guide rewritten in D108.6's order. Descriptive only (D107.2): nothing selected or tuned; no value valid after 2026-07-31T23:00 UTC read; nothing from the 37 airports of F153.6 read; no IFS value exists or was read. Full output: `notes/session-114-output.txt`. Run 2026-10-16. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, matplotlib 3.11.2.**

- **F157.1 D108 and the self-checks.** D108 appended byte-equal (14 lines, `diff` and `cmp`), 0 em-dashes. `--check` 20 of 20 PASS. `--gate`: (1) the loader reproduces session 112's curve and raw GFS n and MAE, hourly and daily maximum, per test year and pooled, at 12 of 12 airports (168 cells); (2) dm_tests.csv's family 1 row at EDDM and EGLC, 7 of 7 fields each, by replaying session 112's seed-112 generator through every earlier draw; (3) the elevation formula reproduces the 12 constants within the record's rounding (claim airports exact at 4 decimals; LFPG and YSDU give -0.1698 and +0.2460 from the record's 2-decimal heights against -0.1697 and +0.2461, within 0.000087). Loader cycle counts equal F156.4 at 26 of 26 source, airport and test-year cells.
- **F157.2 Pairs (`match_counts.csv`), claim airports first.** Hourly rows per airport: AIFS 16,492 to 16,660; NBM grid 113,382 (KORD), 113,513 (CYYZ), 169,095 to 169,194 (dev); NBS 43,609 to 43,624 and 65,577 to 65,591; MAV 43,594 and 65,592 to 65,621. D98.10 days: AIFS 515 to 521; NBM 726 to 728 and 1,093 to 1,095; NBS 724 to 726 and 1,091 to 1,093 (2 v5.0.14 days each apart); MAV 724 and 1,091 to 1,093. Every unpaired row and day counted by reason (before AIFS's first run, not on the source's steps, no run, observed maximum not usable, day ending after the limit); none filled.
- **F157.3 Hourly (skill of the curve against the competitor, pooled, 1 - MAE curve / MAE competitor).** AIFS: claim EDDM -5.5 %, KORD -12.8, CYYZ -0.7, ZGSZ +6.9, ZUCK -3.5, NZWN +25.1; dev EGLC +22.5, LFPG +13.8, KDSM -24.3, YSDU -6.1, KRNO +31.4, KSFO -2.0; BH rejects 7 of 12 (curve better at NZWN, EGLC, LFPG, KRNO; AIFS at KORD, KDSM, YSDU). NBM grid: -10.6, -6.8, -5.1, +17.7, +29.5; 5 of 5 (NBM better at KORD, CYYZ, KDSM). NBS: -13.8, -7.7, -13.6, -5.0, -10.3; 5 of 5, NBS better at all. MAV: +11.4, +8.6, -5.9 (KRNO), +5.0; 4 of 4. Raw GFS's MAE is above every competitor's except AIFS at EGLC (raw GFS +3.8 % better, interval spans 0), MAV at KORD (+0.2 %, spans 0) and the NBM grid at KSFO (+9.0 %).
- **F157.4 Daily maximum (D98.10's days; truth our hourly-report maximum).** Curve against AIFS (highest of its 6-hourly steps): +6.9 % to +59.8 % at the claim airports, +7.6 to +41.5 dev; BH 9 of 12, all for the curve. NBM TMAX: +4.4, +14.0, +5.5, -1.5, +35.3; 2 of 5 (CYYZ, KSFO). NBS TXN: +2.5, +9.9, +0.4, +2.0, -1.1; 0 of 5. MAV X: +25.8, +22.0, +15.7, +14.2; 4 of 4. The curve is worse than no competitor by any test.
- **F157.5 The official maximum (descriptive).** CLI minus our hourly-report maximum, all test years: KORD +0.27 (MAE 0.33), KDSM +0.30 (0.36), KRNO +0.50 (0.50), KSFO +0.48 (0.48); over the local standard time day +0.29, +0.33, +0.50, +0.48, so the window explains little. Equal within 0.05 C on 30 % (KRNO) to 52 % (KORD) of days. MAE against CLI (curve, raw GFS, NBM TMAX, NBS TXN, MAV X): KORD 1.15, 1.22, 1.10, 1.08, 1.40; KDSM 1.28, 1.83, 1.27, 1.22, 1.50; KRNO 1.13, 1.95, 1.10, 0.83, 0.95; KSFO 1.35, 1.91, 1.62, 1.15, 1.31. On CLI and GHCN agreement days the order is unchanged at 4 of 4.
- **F157.6 TXN windows (`--docs`, D108.4(c)).** NBM text cards v4.1, v4.2, v4.3 and v5.0 (each page titled with its version) all define TXN's maximum as 12Z (current day) to 06Z (next day). No v5.0.14 card (HTTP 404): "definition not found", its days (2 per airport) reported separately.
- **F157.7 Readings for the owner.** (1) Choices the plan left open, made by the session: where both NBS run sets exist (20 nominal cycles) the same cycle's run is used (D107.9(a)); one-hour-later NBS runs' windows and steps are placed by leads from the nominal cycle; the elevation correction is held at 4 decimals like GFS's; "share equal" in the gap is |gap| < 0.05 C (D108.4(d)'s tolerance); for IFS (session 115) the script takes the highest 3-hourly 2 m step as the primary maximum and mx2t3's 3-hour windows inside the local day as a second, both untested on real IFS data, for session 115's entry to confirm or change. (2) AIFS's daily-maximum result rests partly on its 6-hourly sampling: the curve sampled at the same steps is worse than AIFS at 6 of 12 (-41 % EDDM to +46 % NZWN at the claim airports). (3) At the development airports both AIFS and the NBM grid are read at GFS's position (D108.3), not the airport's; that position's distance from the airport (gfs set against IEM's position, positions files): AIFS EGLC 4.3 km, LFPG 3.4, KDSM 1.8, YSDU 6.7, KRNO 6.0, KSFO 8.5; NBM grid KDSM 1.8, KRNO 6.0, KSFO 8.5. This likely explains the NBM grid's weak KRNO and KSFO scores, and may weigh on AIFS there too (the `iem` set exists, unused). (4) NBS beats the curve hourly everywhere it exists; MAV's X and NBS's TXN windows differ from the civil day (labelled). (5) ANALYSIS.md Part 2's Table D1 (session 112) had printed "not rejected" in all 48 rows while dm_tests.csv has 39 rejections (families 12, 12, 11, 4); its BH column was re-rendered from dm_tests.csv at session 114's review, with a note under the table; nothing else in it changed. (6) Run order: NBS's daily maximum ran after Step 6's `--docs`, because D108.4(c) needs the TXN labels first. Nothing blocks session 115.
- **F157.8 What was not done.** No IFS comparison (D108.2). No change to SPEC, RESULTS, README, CLAUDE, any existing script, table, figure, model folder, `src/mlwx/` or `tests/`.
- **F157.9 Pointers.** `scripts/session114_comparisons.py`; `data/processed/session114_comparisons/` (match_counts, hourly_ and dailymax_<source> with _skill, _breakdown, _dm, _every_cycle, txn_windows, official_gap, official_scores, part1.md, part2_comparisons.md); `figures/analysis/comparison_*.svg`; ANALYSIS.md Part 1, Part 2 (Tables E1 to E9), Part 3 items 6 and 7; `notes/session-114-output.txt`.

---

## 2026-10-17: Session 115 decision: an observation plausibility check at the 12 stage C airports before IFS; IFS moves to session 116 (owner, planning chat)

**D109. Owner decisions, planning chat (after session 114's commit): a read-only plausibility check of the IEM hourly temperatures at the 12 airports with stage C tables, run as session 115 before the IFS comparisons; its checks and thresholds fixed here before any value is looked at; IFS moved to session 116.** Written at the start of session 115, before any other edit. No observation has been examined for this check.

- **D109.1 Why.** A read-only search (17 October 2026, planning chat) found no plausibility check of the observations anywhere in the project: the readers reject non-finite and missing values (SPEC 8.7 build rule 2, G2) and handle repeated timestamps (F138.8 item 6, F152.7), but any finite `tmpc` value is used as reported. Observations are the truth for every target, the daily maximum (D82.8) and the live drift tracker.
- **D109.2 Session numbers.** Session 115 is this check. The IFS work of D108.7 becomes session 116, unchanged; D108.2 stands.
- **D109.3 Data.** The committed raw IEM routine files (`data/raw/iem_asos_<id>_*_routine.csv`) for EGLC, LFPG, DSM, YSDU, RNO, KSFO, EDDM, KORD, CYYZ, ZGSZ, ZUCK and NZWN, valid 2021-03-24T00:00 to 2026-07-31T23:00 UTC. Reports are read with the project's own reader and assigned to hours by SPEC 8.8 G2 and G3, so the series checked is the hourly series the stage C rows use. Nothing valid later is read (D73.8, D105).
- **D109.4 The checks, fixed before any value is looked at.** On each airport's hourly series:
  (a) **Out of range:** a value below -60.0 or above 60.0 degrees C.
  (b) **Spike:** an hour h whose value differs from both h-1 and h+1 by more than 10.0 degrees C in the same direction; or two consecutive hours h and h+1 that both differ from h-1 and from h+2 by more than 10.0 degrees C in the same direction. A missing neighbour means the test cannot be made at that hour; such hours are counted, not flagged.
  (c) **Stuck sensor:** a run of 24 or more consecutive hours with the same value; a missing hour breaks the run. Every hour in such a run is flagged.
  (d) **Extreme residual:** observation minus raw GFS greater than 10.0 degrees C in either direction, where raw GFS is the median of every elevation-adjusted raw GFS value (SPEC 5.2) valid at that hour in the stage C rows, leads 3 to 48. An hour with no raw GFS value is counted, not flagged.
  A value may carry several flags; each check is counted separately, and the union is counted once.
- **D109.5 Exposure.** For each airport and check, and for the union: flagged hours that are a target in the stage C rows (development table or claim table), split before 2024-08-01 and from 2024-08-01; and flagged hours that set a usable day's daily maximum under D82.8.
- **D109.6 Limits.** Flag and count only. No file in `data/raw/` or any existing processed file is changed; no value is removed, replaced or filled; no model is fitted; no error metric is computed with or without the flagged values. Any rule for excluding observations comes later, in its own entry, as a D89 build choice made on the development airports, and is not chosen by its effect on any spent year's score. Thresholds are not changed after the values are seen; a reading that a threshold looks wrong goes to the owner as a reading.
- **D109.7 Next.** If the flags are rare and explained, the 51-airport check is planned without urgency. If they are frequent, or reach many targets or daily maxima, the check of all 51 airports (all are trained on) comes before session 116. The owner decides at review.
- **D109.8 Note for the project health check (owner).** The repo uses a root layout (`docs/`, `notes/`, DECISIONS at the root), not the `research/` and `audit/` layout recorded in D90.5. Recorded here so it is not lost; it is examined in the planned health-check session, not here.
- **D109.9 Live index.** Removed: none. Added: D109 and F158. After session 115: D93, D103, D105, D106, D107, D108, D109, F157, F158.

---

## 2026-10-17: Session 115 finding: an observation plausibility check at the 12 stage C airports

**F158. D109 was recorded first. D109.4's four checks were run on the hourly IEM temperatures at the 12 airports with stage C tables (2021-03-24T00 to 2026-07-31T23 UTC, 562,232 usable hours), and their exposure to stage C targets and daily maxima counted (D109.5). Flag and count only: no file in `data/raw/` or any existing processed file changed, no value removed, replaced or filled, no model fitted, no error metric computed. No value valid after 2026-07-31T23:00 UTC read; no network; the owner's IFS hand pull and the 37 other airports not touched. Full output: `notes/session-115-output.txt`. Run 2026-10-17. Python 3.12.2, numpy 2.5.2.**

- **F158.1 D109 and the self-checks.** D109 appended byte-equal (20 lines, `diff` and `cmp`), 0 em-dashes. `--check` 40 of 40 PASS (two of my own test set-ups were wrong on the first run and were corrected; no check was changed). One rule added: differences are rounded to 6 decimals before a threshold test, so a tie such as 20.1 - 10.1 is not flagged by float noise. Gate at 12 of 12: the series built with the project's reader (G2, G3) equals every stage C table row's observation (0 mismatches), has the same usable hours (46,467 at YSDU to 46,932 at KDSM) and the same usable D82.8 days as session 104's and 107's day files.
- **F158.2 Flagged hours, claim airports first (a out of range / b spike / c stuck / d residual / union; union rate per 10,000 usable hours).** EDDM 0/0/118/6/124 (26.4); KORD 0/0/0/10/10 (2.1); CYYZ 0/1/24/3/27 (5.8); ZGSZ 0/0/24/0/24 (5.1); ZUCK 0/0/283/1/284 (60.5); NZWN 0/0/80/0/80 (17.1); development airports (flagged): EGLC 0/0/108/0/108 (23.0); LFPG 0/0/29/0/29 (6.2); KDSM 0/0/0/25/25 (5.3); YSDU 0/0/0/25/25 (5.4); KRNO 0/0/0/36/36 (7.7); KSFO 0 (0). All 12: 0/1/666/106/772 (13.7). No hour is out of range. Not testable for (b): 1,130 hours with a missing neighbour (YSDU 565, LFPG 171, KORD 74) and 1,098 pairs; for (d): 0.
- **F158.3 Exposure (union).** Flagged hours that are stage C target hours: 327 before and 445 from 2024-08-01 (0.09 % and 0.21 % of target hours). Complete-case target rows: 2,507 and 3,409 (0.09 % and 0.21 %). Usable days whose maximum-setting hour is flagged: 8 before and 14 from 2024-08-01 (0.05 % and 0.16 %), of them 14 of 8,735 days on the record (session 104 and 107 day files). By check: (c) 7 and 12 days, (d) 1 and 2, (b) 0 and 1 (a day can carry more than one). Largest: ZUCK 7 days and 2,178 complete-case rows, EGLC 4 days.
- **F158.4 Reading (not a ruling).** (a) and (b) are clear-cut and rare: 1 hour in 562,232. That hour is CYYZ 2025-04-28T01:00Z, 27.0 C between 15.0 and 11.0 (residual +17.2); it looks like a bad report, and it is the maximum of the local day 2025-04-27, a claim-look-A day on the record, so that day's observed maximum is probably too high. Its effect on any score was not computed (D109.6). (c) all 24 runs (24 to 40 hours) are at airports that report whole degrees (EDDM, CYYZ, ZGSZ, ZUCK, NZWN, EGLC, LFPG); none at KORD, KDSM, KRNO, KSFO or YSDU. Most are cool, damp spells (for example 0.0 C at EDDM for 36 hours in December 2025); ZGSZ has 28.0 C for 24 hours in July. They look like slow weather read in whole degrees more than sensor faults, but these data cannot confirm it. (d) 106 hours in 58 short episodes, 92 with the observation below raw GFS: KRNO mornings in Nov to Jan (cold air in the basin), YSDU mostly 03 to 07 UTC (local afternoon, a cool change), KORD and KDSM on the same two dates (2025-03-19, 2026-03-15; fronts). They look like real weather that the model misses. The 10.0 thresholds of (c) and (d) look low for whole-degree airports and for fronts and cold pools, but D109.6 says they are not changed.
- **F158.5 Readings for the owner, and D109.7.** (1) Flags are rare overall (0.14 % of hours; 22 of 23,392 usable days' maxima), so D109.7's first branch ("rare") fits; "explained" holds for (a), (b) and (d), not shown for (c) at ZUCK, EDDM and EGLC. (2) One clear fault reached a claim-look daily maximum, which D109.7 does not cover. (3) Any exclusion rule built on (c) or (d) as set would remove real weather, mostly cold hours; a rule from (a) and (b) alone would act on one hour in 12 airports. (4) The raw files also carry `dwpc`; a stuck sensor would show a dew point that does not move, real weather would not. It was not used (D109.4 does not name it). (5) The 51-airport check could run (a) and (b) and a dew point cross-check cheaply; the owner decides at review.
- **F158.6 What was not done.** No exclusion rule, no score with or without any flagged value, no change to any table, day file, model or live product. The 37 airports of F153.6 were not checked. No change to SPEC, RESULTS, README, CLAUDE, any existing script, `src/mlwx/` or `tests/`.
- **F158.7 Pointers.** `scripts/session115_obs_check.py`; `data/processed/session115_obs_check/` (flags, counts, exposure, top_residuals, out_of_range, listing, each with a .meta.txt); `notes/session-115-output.txt`.

---

## 2026-10-17: Session 116 decision: F158 accepted, the observation check extended to all 51 airports with a dew point cross-check, the live log left out, and IFS moved to session 117 (owner, planning chat)

**D110. Owner decisions, planning chat (after session 115's commit): F158 accepted; D109.4's checks (a), (b) and (c) run at all 51 airports of D83, with a dew point cross-check of every stuck run fixed here before any value is looked at; the live observation log left out; IFS moved to session 117.** Written at the start of session 116, before any other edit. No observation has been examined for this check outside the 12 airports of F158.

- **D110.1 F158 accepted,** with its readings. The owner's reading: one clear bad value (CYYZ 2025-04-28T01:00Z) sets a claim-look-A daily maximum; it cannot change CYYZ's verdict or margin materially, and stage C's verdicts stand (D101.2). The 6-decimal rounding rule for threshold ties and the extra `--gate` mode in `scripts/session115_obs_check.py` are accepted. The stuck-run and residual flags read as likely real weather; the dew point cross-check of D110.4 tests that for stuck runs.
- **D110.2 Session numbers.** Session 116 is this check. The IFS work of D108.7 (moved by D109.2) becomes session 117, unchanged; D108.2 stands. Session 116 replaces D109.7's choice: the 51-airport check runs before IFS.
- **D110.3 Data and checks.** The committed raw IEM routine files of all 51 airports, valid 2021-03-24T00:00 to 2026-07-31T23:00 UTC, read and assigned to hours exactly as D109.3. D109.4's checks (a) out of range, (b) spike and (c) stuck sensor, with their thresholds unchanged. Check (d) is not run: it needs stage C rows, which exist only at the 12 airports of F158.
- **D110.4 Dew point cross-check, fixed before any value is looked at.** For every stuck run of D109.4(c) at all 51 airports (the 12 of F158 included), the dew point (`dwpc`) of the report used for each hour of the run, read and assigned exactly as the temperature, is put in one class, in this order:
  (i) **no dew point:** fewer than half the run's hours have a finite dew point;
  (ii) **dew point varies:** the dew points present are not all equal; read as likely weather;
  (iii) **saturated:** the dew points present are all equal and equal the run's temperature; read as fog or a fault, not told apart;
  (iv) **suspect:** the dew points present are all equal and differ from the run's temperature; read as a possible stuck sensor.
  Each run's class, length, value and dew point are written out; nothing is removed.
- **D110.5 Exposure.** For each airport and check, and for the union of (a), (b) and (c): flagged hours that are a target in the stage C rows at the 12 airports (as D109.5) or in the product tables at the 37 other product airports (`../MLwx-live-build/tables/`, D105.8), split before 2024-08-01 and from 2024-08-01; and usable D82.8 days whose maximum-setting hour is flagged. From the tables, only valid times and the observation or target column are read; no forecast value. MMMX and VILK have no tables: hours and days only. If D82.8's day cannot be computed at an airport (for example VILK's time zone, F153), its days are reported as not computed, not stopped on.
- **D110.6 The 39 new airports (D82.6).** Their counts show only how large the problem is. They inform no build choice: any rule for excluding observations is chosen later, in its own entry, on the six development airports, as D109.6 says, and applied identically everywhere. No forecast, error or score is read or computed at these airports.
- **D110.7 The live observation log is left out.** MLwx-live's `obs/` snapshots and any observation valid on or after 2026-08-01 are not read. D105.5(l) requires the live test's scoring script to be committed before any observation valid on or after 2026-10-12 is read. If a cleaning rule is adopted, it is applied to the live test only through that scoring script, written into its own DECISIONS entry before the script reads any observation. Whether any rule can apply to stage B's pre-registered test (D73, D77.6) is decided in its own entry before that test is scored.
- **D110.8 Limits.** As D109.6: flag and count only; thresholds and classes are not changed after the values are seen; a reading that one looks wrong goes to the owner as a reading.
- **D110.9 Live index.** Removed: none. Added: D110 and F159. After session 116: D93, D103, D105, D106, D107, D108, D109, D110, F157, F158, F159.

---

## 2026-10-17: Session 116 finding: the observation plausibility check at all 51 airports, with a dew point cross-check

**F159. D110 was recorded first. D109.4's checks (a) out of range, (b) spike and (c) stuck sensor were run on the hourly IEM temperatures at all 51 airports of D83 (2021-03-24T00 to 2026-07-31T23 UTC, 2,357,664 usable hours), every stuck run was put in one of D110.4's four dew point classes, and the exposure of the flags to targets and daily maxima was counted (D110.5). Flag and count only: no raw or existing processed file changed, no value removed, replaced or filled, no model fitted, no error metric computed, nothing scored. No forecast value read (tables: valid time, lead and observation column only). Nothing valid after 2026-07-31T23:00 UTC read; no network; MLwx-live and the owner's IFS hand pull not touched. Full output: `notes/session-116-output.txt`. Run 2026-10-17. Python 3.12.2, numpy 2.5.2.**

- **F159.1 D110 and the checks.** D110 appended byte-equal (20 lines, `diff` and `cmp`), 0 em-dashes. Preflight: 306 of 306 raw files present; 270 match the SHA-256 in their `.meta.txt`, 36 (the six development airports) record none; session 115's script, its flags.csv and the 74 product table files match their recorded SHA-256. `--check` 27 of 27 PASS. Gate at the 12 airports of F158: checks (a), (b), (c) give exactly session 115's hours, usable hours and untested counts (12 of 12 PASS); exposure at the 12 equals session 115's exposure.csv (48 of 48 rows).
- **F159.2 Flagged hours, 12 of F158 first (a / b / c / union; union per 10,000 usable hours).** EDDM 0/0/118/118 (25.1); KORD 0; CYYZ 0/1/24/25 (5.3); ZGSZ 0/0/24/24 (5.1); ZUCK 0/0/283/283 (60.3); NZWN 0/0/80/80 (17.1); EGLC 0/0/108/108 (23.0); LFPG 0/0/29/29 (6.2); KDSM, YSDU, KRNO, KSFO 0. All 12: 0/1/666/667 (11.9). The 37 product airports: 0/4/1,800/1,804 (10.5); 21 have no flag; of 16 with one, 13 are stuck-run airports (5.1 to 91.9). Well above the rest: UUWW 431 h (91.9), EFHK 307 (65.4), ZUCK (60.3), EPWA 240 (51.2), ZHHH 178 (37.9), EHAM 170 (36.3). MMMX and VILK 0 (usable 28,950 and 42,284). All 51: 0/5/2,466/2,471 (10.5). 28 of 51 airports have no flag. (a) never fired.
- **F159.3 Every spike hour (b), values at h-2, h-1, h, h+1, h+2, dew point at h.** CYYZ 2025-04-28T01Z 17.0, 15.0, **27.0**, 11.0, 11.0, dew -4.0 (F158). KHOU 2026-04-23T15Z 21.67, 23.33, **2.5**, 26.11, 27.22, dew 2.11. RKPK 2021-09-13T03Z 27.0, 27.0, **11.0**, 27.0, 27.0, dew 5.0. RKPK 2022-03-03T07Z 14.0, 15.0, **1.0**, 13.0, 12.0, dew -10.0. SAEZ 2021-08-25T01Z 8.0, 9.0, **58.0**, 4.0, 7.0, dew 4.0. Not testable for (b): see counts.csv (a missing neighbour).
- **F159.4 Stuck runs by D110.4 class.** 87 runs, 2,466 hours: (i) no dew point 0; (ii) dew point varies 78 runs, 2,236 h (91 % of hours; the dew points span 1.0 to 5.0 degrees, median 2.0); (iii) saturated 7 runs, 179 h (CYYZ 9.0 C; ZUCK 15.0, 4.0 and 9.0 C; LIMC 10.0; RKSI 18.0; ZHHH 10.0); (iv) suspect 2 runs, 51 h: EGLC 2021-12-17T19Z to 2021-12-18T21Z (27 h, 8.0 C, dew 7.0 all 27 h) and RCSS 2021-10-24T01Z to 2021-10-25T00Z (24 h, 21.0 C, dew 18.0 all 24 h). 22 runs are exactly 24 h; the longest is 48 h (EFHK, ZHHH). 79 of 87 start between October and March; 44 run at 5.0 C or lower.
- **F159.5 Exposure (union of a, b, c).** All 2,471 flagged hours at the 49 airports with tables are target hours: 1,469 before and 1,002 from 2024-08-01 (0.10 % and 0.12 % of target hours). Usable days whose maximum-setting hour is flagged: 12 airports 7 before and 13 from 2024-08-01 (of 14,653 and 8,739); 37 airports 38 and 31 (of 44,766 and 26,620); MMMX 0 of 104; VILK not computed (Asia/Kolkata, F153). 89 of 94,882 days (0.09 %). Largest: UUWW 11 and 13 days, EFHK 9 and 4, EPWA 4 and 3, ZUCK 2 and 5. Two daily maxima are set by a spike: CYYZ 2025-04-27 and SAEZ 2021-08-24 (58.0 C).
- **F159.6 Reading (not a ruling).** (b): SAEZ 58.0 C is a bad value (it passed (a), whose bound is 60.0, and it sets a day's maximum). CYYZ 27.0, RKPK 11.0 and 1.0 and KHOU 2.5 also look like bad single reports; KHOU's dew point (2.11) is as low as its temperature, so that whole report may be wrong. (c): 38 of 51 airports report whole degrees (an ad hoc count, not scripted); all stuck hours are at 20 of them, none at the 13 US airports. The dew point moved during 91 % of the stuck hours, which reads as slow cool damp weather in whole degrees, not a fault. The 7 saturated runs read as fog or mist, which is also steady real weather. The 2 suspect runs (a steady 1 to 3 degrees of spread, in 2021) look like weather too, but are not told apart from a stuck sensor by these data.
- **F159.7 Readings for the owner.** (1) Faults are rare: five spike hours in 2.36 million, none out of range. (b) is the only check that fired on likely faults. (2) (c) as set acts on 2,466 hours that read mostly as real weather: a rule on (c) alone would remove them from cold humid whole-degree airports (UUWW, EFHK, EPWA, ZUCK, EHAM), not from the US airports. With the dew point, (c) restricted to class (iv) would act on 51 hours. (3) A bound of 60.0 missed 58.0 at SAEZ; any (a)-type bound is a build choice for later. (4) No check here can find a bad value that sits inside a normal range with normal neighbours. (5) Whether any cleaning rule is worth proposing is the owner's decision; if one is, D109.6 and D110.6 require it to be chosen on the six development airports only (where the flags are: EGLC (c) 108 h, LFPG 29 h, none of (a) or (b)) and applied the same everywhere. The 39 new airports' counts here inform no build choice (D110.6).
- **F159.8 What was not done.** Check (d) at the 39 (no stage C rows, D110.3). The live observation log and any 2026-27 value (D110.7). No exclusion rule, no score with or without any flagged value, no change to a table, day file, model or live product. MMMX's low coverage (28,950 usable hours, 104 usable days) was seen and not examined.
- **F159.9 Pointers.** `scripts/session116_obs_check51.py`; `data/processed/session116_obs_check/` (flags, stuck_runs, counts, exposure, listing, each with a .meta.txt); `notes/session-116-output.txt`.
