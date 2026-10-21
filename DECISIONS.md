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
- D108: F156 accepted, IFS deferred to the owner's hand pull, and the comparison choices D107.9 left open fixed before any score.
- D111: F159 accepted, no observation cleaning rule, the owner's IFS pull recorded, and IFS's daily maximum rule fixed before any IFS value is read.
- D112: F160 accepted, the order of the next work, and an audit of MLwx-live's runs with three workflow fixes.
- D113: F161 accepted, the redeploy, the mx2t3 rerun dropped, and the IFS reading check fixed before any value is seen.
- D114: F162 accepted, the layout baseline, and the project health check's plan and audit limits.
- F157: session 114's finding (the curve against AIFS, the NBM grid, NBS and MAV on spent years, the official maximum's gap, and the field guide).
- F160: session 117's finding (the owner's IFS pull checked, and the curve against ECMWF IFS on spent years, with the mx2t3 subset).
- F161: session 118's finding (the live runs audited: no cycle lost, one stale checkout on 17 Oct, no silent push failure; and the workflow fixes).
- F162: session 119's finding (the IFS reading check: no fault mark shows at any of five tests, so IFS's cold error is the model's and F160 stands).
- F163: session 120's finding (the health check's code audit: 55 register rows, none wrong or blocking; 16 stale items grouped into fix sessions).
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

## 2026-10-18: Session 117 decision: F159 accepted, no observation cleaning rule, the owner's IFS pull recorded, and IFS's daily maximum rule fixed before any IFS value is read (owner, planning chat)

**D111. Owner decisions, planning chat (after session 116's commit): F159 accepted; no cleaning rule for the historical observations; the owner's IFS hand pull recorded (D108.2); IFS's daily maximum rule fixed, amending D108.4(b) for IFS; and how session 114's script is run for IFS.** Written at the start of session 117, before any other edit. No IFS temperature value has been read or scored. The planning chat read the pull's meta file and gap counts by month and reason (no values) before writing D111.4.

- **D111.1 F159 accepted,** with its readings. Session 116's exposure counts read each table row's lead as a row label to keep D109.5's definition of a target; this is accepted (no forecast value was read).
- **D111.2 No cleaning rule (owner).** The historical observations are accepted as they are: no rule for excluding observations is adopted, and none is proposed now. D109.6 stands, and every table, model and verdict is unchanged. A spike and range guard for live observations comes later, as a stage G fix and in the live test's scoring script, each in its own DECISIONS entry before it acts on any value (D110.7). Whether any rule can apply to stage B's test stays as D110.7 says.
- **D111.3 The IFS pull (owner, by hand, 2026-10-16 to 2026-10-18).** `scripts/session113_comparison_pull.py --pull ifs`, unchanged, at 8 requests at once throughout, with the override text of D108.2, over several runs: the first ended with exit 2 (26 of 36 months done); reruns met HTTP 503 throttling from ECMWF; an overnight run reached 31 of 36; two more finished it, the last with exit 0. One run was stopped by the owner with `pkill`. The meta file was written at 2026-10-18T16:15:52Z. The owner's log (`~/mlwx-ifs-pull.log`, outside the repo) is read only by session 117, for counts. Session 117 checks the pull before any value is read (D108.2).
- **D111.4 IFS's daily maximum (amends D108.4(b) for IFS only).** Primary: the highest of IFS's own 3-hourly 2 m temperature steps inside the local day, labelled "3-hourly steps", as session 114's script does (F157.7(1)). Why: IFS's maximum field (mx2t3) exists for only part of the window. It has no message up to 2024-11, and the pull's identity check rejected it from 2025-02 to 2026-02 (the GRIB short name reads `max_2t`; those values were not kept). A primary on mx2t3 would score a minority of days, in a few seasons, and not the same days at every airport. The steps exist on every pulled day. Second, descriptive: mx2t3, the highest of its 3-hour windows wholly inside the local day, on the days where it exists, with the curve and IFS's steps rescored on exactly those days. The formal test (D108.4(e)) uses the primary. The pull is not rerun for mx2t3; that is a reading for later.
- **D111.5 How it is run.** Session 114's script, unchanged (D108.7, D110.2): `--hourly --source ifs` and `--dailymax --source ifs` write their new IFS files to `data/processed/session114_comparisons/`, seed 114; `--match` is run with `--trial-dir data/processed/session117_ifs/`, because `match_counts.csv` is written once, and its non-IFS rows must equal the committed `match_counts.csv`. D107.9, D108.3 and D108.4 (with D111.4) apply. IFS goes into ANALYSIS.md by a new script that reads only those tables.
- **D111.6 Uses of spent data.** As D107.3: once scored here, IFS's test years at the 12 airports count as used for IFS.
- **D111.7 Next.** After session 117: the owner groups the MLwx folders under one parent folder, by hand, with no renaming and the planning chat's checklist; then the direction brainstorm in a new planning chat.
- **D111.8 Live index.** Removed (archived): D109, F158 and F159, which are settled. Added: D111 and F160. After session 117: D93, D103, D105, D106, D107, D108, D110, D111, F157, F160.

---

## 2026-10-18: Session 117 finding: the owner's IFS pull checked, and the curve against ECMWF IFS on spent years

**F160. D111 was recorded first. The owner's IFS hand pull (D108.2, D111.3) was checked from its meta file, manifest, gap file and the owner's log, with no temperature value read; IFS was then compared with the curve at the 12 airports by session 114's script unchanged (D111.5), the mx2t3 subset was scored on common days by a new script (owner's ruling), and IFS was added to ANALYSIS.md. Descriptive only (D107.2): nothing selected or tuned; nothing valid after 2026-07-31T23:00 UTC read; nothing from the 37 airports of F153.6, MLwx-live or any 2026-27 file read; no network. Full output: `notes/session-117-output.txt`. Run 2026-10-18. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, matplotlib 3.11.2.**

- **F160.1 D111 and the pull check.** D111 appended byte-equal (14 lines, `diff` and `cmp`), 0 em-dashes. 15 of 15 pull files match the meta file's SHA-256 and rows; the override names D108.2; airports and windows are D107.5's. 70,080 cycle-steps expected; kept plus gaps equal expected in 72 of 72 month and parameter cells; 87,696 messages, 0 duplicates by cycle, step and parameter. Log: 9 runs; 87 failed attempts, all HTTP 503; each of the 36 chunks written once; chunk sums equal the merged files; no sign of a run stopped mid-write. Runs 2, 3, 5 and 6 end with no closing line, and the log does not say which was the pkill. Exit codes (not logged, from the script's exit paths): run 1 was 2, run 4 was 1 (a wrong `--workers` value, before any request), runs 7 and 8 were 2, run 9 was 0.
- **F160.2 The owner's three items.** (1) Confirmed: the 48 "not listed" gaps are cycles 2024-02-28T06, 12 and 18Z, 16 steps each. (2) Confirmed from the rows: 12 value rows per message before 2024-08-01 (6 development airports, sets gfs and iem), 18 after (plus the 6 claim airports, set iem). (3) Corrected: in the log, "units" counts a month's (cycle, step) files and "gaps" counts gap rows. Gaps equal units only in the 25 months where every file lost only its mx2t3, not in the 11 months where mx2t3 was kept. What holds in 36 of 36 months: messages + gap rows + "*" rows = 2 x units. mx2t3: no message up to 2024-11-12T00Z, except 6 cycles on 2024-09-17 and 18 (kept); kept 2024-11-12T06Z to 2025-02-25T00Z; failed the check ("shortName max_2t") from exactly 2025-02-25T06Z to 2026-02-11T06Z; kept from 2026-02-11T12Z; 17,664 messages kept. This matches D111.4.
- **F160.3 Match (`--match --trial-dir`).** The 2,103 non-IFS rows equal the committed `match_counts.csv` in every column except `txn_window` (232 NBS rows read "pending (Step 6)" where `--docs` had filled labels). IFS cycles per test year: 1,461 (dev 2023-24, less the 3 unlisted cycles), then 1,460 and 1,460, equal to the pull's. F156.4 has no IFS entry, so the script skips that check. Paired hourly rows: claim 46,568 to 46,656, dev 69,520 to 70,016. D98.10 days: claim 726 to 729, dev 1,084 to 1,095. D98.10 days with an mx2t3 value: 272 to 277 (none in 2023-24).
- **F160.4 Hourly (skill of the curve against IFS, pooled, 1 - MAE curve / MAE IFS).** Claim: EDDM +6.3 %, KORD +15.2, CYYZ +15.5, ZGSZ +32.1, ZUCK +16.9, NZWN +16.6. Dev: EGLC +29.0, LFPG +25.1, KDSM +13.0, YSDU +7.5, KRNO +44.7, KSFO +23.0. BH rejects at 12 of 12, all for the curve. IFS's MAE: claim 0.94 (NZWN) to 1.42 (EDDM), dev 1.17 (EGLC) to 2.20 (KRNO). Raw GFS's MAE is below IFS's at 5 of 12 (KORD, ZGSZ, EGLC, LFPG, KSFO). IFS reads cold: mean error +0.39 to +1.15 C at 10 of 12 (EDDM -0.08, YSDU -0.05).
- **F160.5 Daily maximum (D111.4 primary, "3-hourly steps"; D98.10's days).** Curve against IFS: claim +12.5 % (EDDM) to +50.0 % (NZWN), dev +13.0 % (KDSM) to +61.1 % (KRNO); BH rejects at 12 of 12, all for the curve. Read only at IFS's steps, the curve's maximum still beats IFS's at 12 of 12 (claim +4.8 % EDDM to +46.1 % NZWN). Sampling at the steps raises the curve's MAE by 5 % (KDSM) to 16 % (KRNO). IFS's maximum reads low (mean error +0.50 to +2.32 C). Raw GFS's maximum beats IFS's at 8 of 12. Every cycle: the curve's MAE is below IFS's in 48 of 48 airport and cycle-hour cells.
- **F160.6 mx2t3 on its own days (descriptive; computed by `scripts/session117_ifs_guide.py --subset`, not by session 114's script; seed 117; no formal test).** The gate ran first: 294 of 294 values equal session 114's tables exactly. 0 of 3,301 days lack a window. 272 to 277 days per airport. On the same days, mx2t3's MAE is below IFS's step maximum at 12 of 12 (skill of the steps against mx2t3: -3.4 % ZUCK to -20.8 % ZGSZ). The curve's MAE is below mx2t3's at 10 of 12 (claim +4.6 % KORD to +41.2 % NZWN; KDSM -7.5 %, KSFO -3.4 %). The interval spans 0 at EDDM, KORD, EGLC, KDSM and KSFO.
- **F160.7 Grid and elevation segments (hourly).** "No elevation treatment" (the 0.4 degree grid plus the 8 Ni 1439 cycles; dev only, 11,808 to 11,872 rows): IFS's MAE is 1.12 (LFPG) to 3.32 (KRNO), with mean error up to +2.74 (KRNO) and +1.90 (KSFO). "Terrain from a later date" (2024-02-03 to 2024-12-02): 7,928 to 7,936 rows claim, 19,296 to 19,440 dev. The curve is ahead in 62 of 66 segment and version cells. IFS is ahead (each interval spans 0) only at EDDM 48r1 (-0.1 %) and "terrain from a later date" (-5.4 %), KORD 50r1 (-2.5 %) and YSDU 50r1 (-4.2 %).
- **F160.8 ANALYSIS.md.** New script `scripts/session117_ifs_guide.py`; `--render`, then `--verify`: PASS. Re-rendered from HEAD the text is identical (14,242 numbers, 0 mismatches); 48 of 48 independent cell checks pass; the diff holds only the allowed edits: the header sentence (line 5) and Part 2's phrase (line 812), both beyond the prompt's list by the owner's ruling; item 1's sentence; 24 cells; 2 formal-test lines; and Tables E10 to E16 after E9 (315 lines). 0 em-dashes.
- **F160.9 Readings for the owner (readings, not rulings).** (1) IFS is the weakest competitor in the field guide: the curve beats it at 12 of 12 on both outputs, and raw GFS's MAE is lower than IFS's at 5 of 12 hourly and 8 of 12 for the maximum. IFS changes no standing in item 4: no competitor beats the curve's daily maximum, and hourly the curve still trails only NBS, the NBM grid and AIFS, where F157 says. (2) IFS read this way runs cold at 10 of 12 airports, and its 0.4 degree months with no height treatment are far worse at KRNO and KSFO. Part of IFS's deficit may come from the open-data product and how it is read, not from the model. This was not examined. (3) The mx2t3 rejection: on the days mx2t3 exists it beats IFS's step maximum at 12 of 12, by 3 to 21 %. A rerun that accepts the short name `max_2t` would add about 350 days in 2025-26. That short name starts on the same cycle as AIFS's first run, and whether it is the same quantity was not checked. The rerun could narrow the daily-maximum gap but looks unlikely to reverse it (the curve beats mx2t3 at 10 of 12). It needs its own entry, because it changes session 113's check. (4) Process items: the prompt's preflight did not list the 16 pull files (taken as expected). Session 114's `--verify` now fails on Part 1, because its template still says "pending". Its `part1.md` and `part2_comparisons.md` are out of date. Its `subdaily_max` does not check that every window is present (no effect: 0 of 3,301 days). Its `F156_4` has no IFS entry.
- **F160.10 What was not done.** No figure (session 114's figures exclude IFS). No mx2t3 rerun. No formal test on the mx2t3 subset. No change to SPEC, RESULTS, README, CLAUDE, any existing script or table, `figures/`, `src/mlwx/` or `tests/`.
- **F160.11 Pointers.** `scripts/session117_ifs_guide.py`; `data/processed/session117_ifs/` (match_counts, dailymax_ifs_mx2t3_subset and _skill, subset_meta.txt); `data/processed/session114_comparisons/` (`hourly_ifs*`, `dailymax_ifs*`); ANALYSIS.md Part 1 item 4 and Part 2 Tables E10 to E16; `notes/session-117-output.txt`.

---

## 2026-10-19: Session 118 decision: the order of the next work, and an audit of the live runs with workflow fixes (owner, planning chat)

**D112. Owner decisions, planning chat (direction brainstorm after session 117): the order of the next work, a read-only audit of MLwx-live's runs, and three workflow fixes.** Written at the start of session 118, before any other edit. No 2026-27 value has been read or scored.

- **D112.1 F160 accepted,** with its readings (F160.9), which stay open items.
- **D112.2 The order of the next work.** (1) This session, then the owner's redeploy. (2) IFS close-out: a check of whether IFS's cold error (F160.9) comes from the open-data product or the reading method, and the mx2t3 rerun accepting `max_2t` (F160.9(3)), each in its own entry. (3) The project health check (D109.8): an audit first, then fix sessions, in as many sessions as it needs, covering everything: the layout against D90.5, old paths, every verify and check script, stage B's frozen scripts after the folder move, the tests, consistency of SPEC, STATUS and DECISIONS, the Project-knowledge sync, and session 114's open items (F160.9(4)), the IFS figures included. (4) A README update, last in the health check. (5) Then the longer-term plan: stage B's timing, stages D, E, F and H, ANALYSIS.md's Part 3 candidates 6 and 7, rows at the airport's own position for the gridded sources, Gates C and D, WeatherNext, and whether to build a MOSMIX saver.
- **D112.3 The IFS check (planning chat's note, not fixed).** A difference from AIFS alone does not show a reading fault, since AIFS may remove IFS's own biases. The check looks for a reading fault's marks: error growing with the height gap between grid point and airport; a daily cycle shifted by local hour; a step at the 0.4 to 0.25 degree change. AIFS is a secondary reference only. If a fault is found, whether IFS is re-read and re-scored as an error correction is the owner's ruling, made when that session is planned.
- **D112.4 What a late run costs (runner.py).** The runner issues every cycle of the past 24 hours not yet logged, in time order. A cycle is lost only if no run happens between cycle + 4 h 10 min and cycle + 24 h. A shorter gap delays the page and the issue time only; the issued values do not depend on the run time beyond which observations had arrived.
- **D112.5 The audit (session 118).** Read-only: a fresh clone of MLwx-live and its Actions runs and logs. For every cycle from 2026-10-12 12z to the latest available at the audit: logged once, all leads, issue lag, snapshot present, stop list. For every run: trigger, created and start times, commit checked out against main's head at its start, result, and the cycles its log says it issued. It answers whether any cycle was lost, issued twice, or issued from a stale checkout, and whether any push failed silently. The page's shown cycle is compared with the log's latest. No error is computed (D105.6).
- **D112.6 The workflow fixes (template, `deploy/mlwx-live/.github/workflows/live.yml`).** (a) This repo's checkout takes `ref: main`, so a queued run starts from the latest commit. (b) The commit step fails the job, before the page is published, unless the push landed (local HEAD equals `origin/main` after a fetch); a failed rebase is aborted and also fails the job. (c) The manual run's `latest_only` input is removed; the runner's `--latest-only` flag stays for dry runs. (d) The schedule becomes `15,40 * * * *`: a cycle is available from cycle + 4 h 10 min, and the owner wants the page as fresh as possible. An outside scheduler is considered only if issue lags stay long after the redeploy.
- **D112.7 The live test (D105.5(k)).** None of D112.6 changes a logged forecast value; it can change issue times only. The live test treats every row unchanged. If the audit finds a cycle issued twice, a log file changed after it was first written, or a cycle lost, session 118 records it and the owner decides how D105.5 treats it.
- **D112.8 The redeploy (owner, after session 118's commit).** The owner copies the template into MLwx-live with `MLWX_COMMIT` and `MODELS_TAG` unchanged from the deployed values (no code change). The deployed values are recorded in the next session's entry. Until then: no manual run between :35 and :55 past the hour, and "latest only" left unticked.
- **D112.9 Plan.** Session 118: this entry, the audit, the fixes, F161. Then the redeploy, then D112.2's item 2.
- **D112.10 Live index.** Removed: none. Added: D112 and F161 (F161 when it is written).

---

## 2026-10-19: Session 118 finding: the live runs audited, and the workflow fixes

**F161. D112 was recorded first. MLwx-live's runs from 2026-10-12 to the audit were audited read-only (D112.5) from a fresh clone, `gh` run lists and run logs and one fetch of the public page, by a new script; then the template's workflow was fixed (D112.6) and its commit step tested in scratch repos. No error was computed (D105.6): no observation was compared with any forecast, the snapshots were counted by lines only, and the log was read only for its airport, cycle, lead, issue time, commit, model and version columns. Network: read-only (clone, `gh`, the page); nothing pushed, no workflow triggered. Full output: `notes/session-118-output.txt`. Run 2026-10-19. Python 3.12.2.**

- **F161.1 D112 and the start.** D112 appended byte-equal (16 lines, `diff` and `cmp`), 0 em-dashes. Tests (reading): the prompt's `pytest -q` resolves to Anaconda's pytest without lightgbm, and the venv has no pytest; `python3 -m unittest discover -s tests` in the venv ran 181 tests, OK (accepted by the owner).
- **F161.2 The clone and the template gate.** Clone HEAD `5d61948` (2026-10-19T17:46:30Z), 52 commits. Deployed `MLWX_COMMIT` `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb`, `MODELS_TAG` `gfs-models-49`. The gate stopped the session: besides the two `SET-AT-DEPLOY` lines, the header's item 5 differs (template: "commits the log files, the observation snapshots (obs/, D105.7) and the tracker state (each log and snapshot file is written once and never edited);"; deployed: "commits the log files and the tracker state (the log is written once and never edited);"). **Owner's ruling:** comment-only and harmless; every non-comment line matches, the obs line included; it came from the session 111 redeploy copying the commit line only. The next redeploy copies the whole template.
- **F161.3 Cycles lost: none.** 29 of 29 cycles, 2026-10-12T12z to 2026-10-19T12z, logged; leads 3 to 48 complete for every airport; 552 rows (12 airports) to 2026-10-13T12z, 2254 (49) after. Stop list: only 2026-10-12T06z (tracker order, before the test start).
- **F161.4 Issued twice: one cycle, no trace on main.** 2026-10-17T18z was issued by manual run 39075664773 (pushed `ceddce8`, the file on main) and again by scheduled run 39075798597, whose commit never landed. 0 log or obs files modified, deleted or renamed after being added; each of the 29 log files has one commit.
- **F161.5 Stale checkout: one run, the 17 Oct failure.** Run 39075798597 was created at 22:37:02Z while 39075664773 ran (to 22:37:51Z); its job started 22:37:55Z, its fetch saw main at `ceddce8`, then forced it back to its trigger commit `3635dac`. It re-issued 18z, its push was rejected, `git pull --rebase` hit conflicts in the 18z log file and the state file, and the job failed before the page steps. The only queued run of 50. `gh`'s startedAt equals createdAt for all 50 runs, so only the log shows the real start.
- **F161.6 Silent push failure: none.** 49 of 50 runs pushed on the first try, each commit on main; the one that did not ended red.
- **F161.7 "Latest only": used once,** on the first run (manual 38301336881, 2026-10-12T20:00Z): it issued 12z and passed over 00z and 06z of 12 Oct. The next run marked 06z "tracker order" and exited 3 (the runner before D104.4); 00z left the 24-hour window. Both before the test start. 10 later manual runs had it unticked.
- **F161.8 Cadence and issue lag.** Scheduled runs: 39 of 150 slots to the audit cutoff (2026-10-19T21:29Z), 26 %; 5 to 7 per UTC day on the five full hourly days (14 to 18 Oct, 24 slots each). Delay to the latest slot (a minimum; all 39 follow a slot with no run): median 34 min, max 289 min. Gaps between runs: median 3.20 h, 90th percentile 5.65 h, max 6.98 h; none over 20 h. Issue lag over 29 cycles: median 5.57 h, min 4.47 h, max 8.98 h (the earliest possible is 4.17 h).
- **F161.9 The page matches the log:** latest cycle 2026-10-19 12z, issued 17:44 UTC, on all 49 airport lines.
- **F161.10 Other readings (open questions, not fixed).** (1) GitHub ran about a quarter of the hourly slots; lateness, not loss, is the cost (D112.4). (2) Every run commits, even with no cycle issued (20 of 49 pushes), because the state's `last_run` changes; any two overlapping runs therefore conflict on the state file. (3) On 17 Oct, manual runs at 20:36, 21:28 and 22:01Z came before 18z was available; the 22:35Z run overlapped the 22:40 slot. (4) Every run warns that six actions (checkout, setup-python, cache, configure-pages, upload-artifact, deploy-pages) are forced from Node.js 20 to 24. (5) `setup-python` "3.12" floats: all 50 runs used CPython 3.12.15. (6) As expected: snapshots from 2026-10-14T06z (22 of 29, D105.7); log code commits `0f89f01` (5 cycles), `e37c86d` (2), `d6ca3e4` (22); GFS v16 throughout.
- **F161.11 The template and the push test.** `live.yml`: `ref: main` on this repo's checkout; the push loop aborts a failed rebase and the step exits 1 unless HEAD equals `origin/main` after a fetch, before the page steps; the `latest_only` input and the runner's `--latest-only` argument removed; cron `15,40 * * * *`; header updated. YAML parses (PyYAML 6.0.1); the diff holds only these. Push test, the step run with `bash -e` and with GitHub's flags: (i) non-conflicting push first, exit 0, HEAD equals the remote; (ii) conflicting push first, exit 1, rebase aborted; (iii) every push rejected, exit 1 after 3 tries; (iv) nothing to commit, exit 0. Control: the old step exits 0 in (iii).
- **F161.12 What was not done.** No error, score or snapshot value; no push or workflow run; no change to MLwx-live, `src/`, `tests/` or the owner's `../MLwx-live`; no outside scheduler. Pointers: `scripts/session118_live_audit.py`, `data/processed/session118_runs.csv`, `data/processed/session118_cycles.csv`.

---

## 2026-10-20: Session 119 decision: F161 accepted, the redeploy, the mx2t3 rerun dropped, and the IFS reading check fixed before any value is seen (owner, planning chat)

**D113. Owner decisions, planning chat (after session 118's commit and the redeploy): F161 accepted; the redeploy recorded; a ruling on the doubled 17 Oct cycle; D112.6's amendments named; the mx2t3 rerun dropped; and the IFS reading check, with each test's fault mark fixed before any value is seen.** Written at the start of session 119, before any other edit. No 2026-27 value has been read or scored. No IFS value has been read by the planning chat beyond the pull files' headers.

- **D113.1 F161 accepted,** with its readings (F161.10), which go to the project health check (D112.2).
- **D113.2 The redeploy (D112.8, owner, by hand, 2026-10-20).** MLwx-live commit `0d77fb0`: `.github/workflows/live.yml` copied from the template, with `MLWX_COMMIT` `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb` and `MODELS_TAG` `gfs-models-49` unchanged; `diff` against the template showed only those two lines. Manual run 39488813037 went green at 2026-10-20T20:04Z and its push landed (`0d77fb0..7b4a349`). D112.8's interim rule is lifted.
- **D113.3 The doubled 17 Oct cycle (owner's ruling on D112.7).** 2026-10-17T18z was issued twice, but only the first-issued file exists on main (F161.4). It has no effect on the live test: D105.5 scores the first-issued file only.
- **D113.4 Amendments.** D112.6 amends D105.2 (the job also fails when a push did not land) and D105.4 (the schedule is `15,40 * * * *`).
- **D113.5 The mx2t3 rerun is dropped (owner).** F160.9(3) is closed: descriptive only, unlikely to change any standing (F160.6), and a further hand pull. D111.4 stands.
- **D113.6 The IFS reading check (session 119).** Descriptive (D107.2), on IFS's spent test years (D111.6), on the pull of D111.3 and the rows and pairing of D108.4(a) with D108.3's positions and treatment. Mean error is observation minus forecast (positive is cold). Hourly rows only. Raw GFS (as SPEC 5.2) and AIFS (from 2025-02-25T06Z) are scored on exactly the same rows as references. A count is "at most airports" when it is at least 7 of 12 (or at least 4 of 6 where only the development airports apply). Fault marks, fixed now:
  (a) T1, height. Mark: removing the elevation treatment brings IFS's mean error within 0.2 C of zero at most airports; or, across the 12 airports, the Spearman correlation between IFS's mean error and its mean elevation adjustment (C) is at least 0.7 in size; or any IFS terrain height at a position differs from GFS's terrain height there by more than 300 m.
  (b) T2, position. Mark: at most of the 6 development airports, IFS's mean error at the airport's own position (`iem` set) is at least 0.3 C nearer zero than at GFS's position (`gfs` set).
  (c) T3, timing. Mark: pairing IFS with the observation 3 hours later, or 3 hours earlier, lowers its MAE at most airports; or the slope of IFS's error on the observed temperature trend (the observation at t+1 h minus at t-1 h, per hour) is at least twice the size of raw GFS's at most airports. The same is computed for raw GFS and AIFS as controls. Mean error by local hour is reported without a mark.
  (d) T4, product changes. Mark: IFS's mean error steps by at least 0.5 C, after removing the same calendar step in the other test years, at a reading boundary (2024-02-01 grid change; 2024-12-03 own terrain) at most airports with data on both sides, with no step of that size at the IFS model-version dates.
  (e) T5, decoding. Mark: any fetched message whose SHA-256 differs from the manifest, whose decoded parameter, units, date, time, step or grid differ from its rows, or whose four values at the positions file's points differ from the stored v1 to v4 in any bit.
  If no mark shows, IFS's cold error is recorded as the model's, as read under D108.3, and F160 stands. If a mark shows, it is recorded and the owner rules under D112.3. Nothing is re-scored in session 119 either way.
- **D113.7 Network.** T5 fetches by byte range, from the manifest's URLs, at most 24 messages; nothing else.
- **D113.8 Plan.** Session 119: this entry, the check, F162. Then the project health check's audit (D112.2 item 3).
- **D113.9 Live index.** Removed (archived): D106, D107 and D110, which are settled (D106's and D107's plans are carried out and recorded; D110's check is done and its live guard is restated in D111.2). Added: D113 and F162. After session 119: D93, D103, D105, D108, D111, D112, D113, F157, F160, F161, F162.

---

## 2026-10-20: Session 119 finding: the IFS reading check

**F162. D113 was recorded first. IFS's cold error (F160.4) was checked for a reading fault by D113.6's five tests, each with its mark fixed in D113 and every open detail fixed in the new script before any value was computed. Descriptive only (D107.2): nothing re-scored, selected or tuned; nothing valid after 2026-07-31T23:00 UTC, no 2026-27 file, MLwx-live or the 37 airports of F153.6 read. Network: 6 byte-range GETs from the manifest's URLs (D113.7). Full output: `notes/session-119-output.txt`. Run 2026-10-20. Python 3.12.2, numpy 2.5.2, scipy 1.18.0, eccodes 2.48.0, lightgbm 4.7.0.**

- **F162.1 D113** appended byte-equal (21 lines, `diff` and `cmp`), 0 em-dashes; Live index changed as D113.9. Start: 181 tests OK; 15 of 15 pull files equal `ifs_meta.txt`.
- **F162.2 The gate: PASS.** IFS, raw GFS and the curve: n, MAE and mean error per airport and test year equal `hourly_ifs.csv` in 126 of 126 cells; rows claim 46,568 to 46,656, dev 69,520 to 70,016 (F160.3), and equal `match_counts.csv` at 12 of 12. Mean error is observation minus forecast (positive is cold), the file's sign at 12 of 12.
- **F162.3 T5, decoding: NOT SHOWN.** 6 messages (3 picks short and counted: the main 0.25 degree grid has no 00z step-24 message on its first and last dates, and the Ni 1439 grid covers 2 dates). 6 of 6 SHA-256, metadata and grid labels equal; 78 of 78 stored rows bit-equal; 0 failed fetches; the bytes deleted.
- **F162.4 T1, height: NOT SHOWN.** Without the treatment |ME| <= 0.2 C at 3 of 12 (needs 7); removing it moves ME further from zero at 9 of 12 (KRNO +1.15 to +2.19, NZWN +0.42 to +1.06). Spearman rho between ME and mean adjustment -0.08 (needs 0.7). IFS minus GFS terrain -106 m (KRNO) to +6 m at 14 positions; none over 300 m; 4 iem positions not recorded.
- **F162.5 T2, position: NOT SHOWN.** The iem set's ME is 0.3 C nearer zero at 0 of 6 (|ME gfs| - |ME iem| -0.26 KSFO to +0.04 LFPG).
- **F162.6 T3, timing: NOT SHOWN.** A 3 h shift either way lowers IFS's MAE at 0 of 12 (controls raw GFS and AIFS: 0 of 12). |slope IFS| / |slope raw GFS| on the trend 0.15 (CYYZ) to 1.81 (KORD); at least 2 at 0 of 12.
- **F162.7 T4, product changes: NOT SHOWN.** Calendar-adjusted 20-day steps of at least 0.5 C: 2024-02-01 at 2 of 6 (KDSM -1.39, KRNO -2.89); 2024-12-03 at 1 of 12. Version dates: 49r1 at 5 of 12, 50r1 at 4 of 12.
- **F162.8 Outcome (D113.6).** No mark shows. IFS's cold error is recorded as the model's, as read under D108.3, and F160 stands.
- **F162.9 Readings for the owner (readings, not rulings).** (1) The treatment reduces IFS's cold error; it does not cause it. (2) IFS is coldest in the evening and at night and least cold near local midday (KORD +0.05 at 13h, +1.50 at 18h; KRNO +3.61 at 16h); raw GFS has a similar shape at a lower level at several airports. Not a shift (T3), so it reads as the model's evening boundary layer. (3) KRNO's and KDSM's 2024-02-01 steps are the treatment and the 0.25 degree grid starting together, as F160.7's segments show. (4) Steps of 0.5 C in 20 days are common at the version dates too, so T4's threshold sits near the noise. (5) Session choices where D113.6 was open (T4's 20-day window and its reading of "no step", T5's dates, the T1 mean adjustment over all rows) are listed in the output file; none is near deciding a mark. (6) T5 checked one message on the main grid (75,824 of 87,696 messages); 2 more fetches would cover its first and last 00z dates.
- **F162.10 What was not done.** No re-score, no change to any figure, table, ANALYSIS.md line, SPEC, RESULTS, README, existing script, `src/` or `tests/`. No mx2t3 rerun (D113.5).
- **F162.11 Pointers.** `scripts/session119_ifs_check.py` (`--gate`, `--decode`, `--tests`); `data/processed/session119_ifs/` (gate, t1_height, t1_terrain, t2_position, t3_timing, t3_local_hour, t4_steps, t5_decode); `notes/session-119-output.txt`.

---

## 2026-10-21: Session 120 decision: F162 accepted, the layout baseline, and the project health check's plan and audit limits (owner, planning chat)

**D114. Owner decisions, planning chat (after session 119's commit): F162 accepted; the layout baseline for the health check; the health check's plan; and the audit's limits.** Written at the start of session 120, before any other edit. No 2026-27 value has been read or scored.

- **D114.1 F162 accepted,** with its readings (F162.9). F162.9(6)'s two extra decode fetches are made in session 120.
- **D114.2 The layout baseline (owner).** The health check checks the layout against D91.3, which replaced D90.5 (D91.4), not against D90.5 as D109.8 and D112.2 say. Each folder or root file added after D91.3 is traced to the entry that added it. D109.8 is answered as a reading.
- **D114.3 The health check's plan.** It is a routine check, not a response to a suspected fault. Session 120 audits the code (MLwx and MLwx-live). Session 121 audits the record (SPEC, STATUS, DECISIONS, RESULTS, ANALYSIS, README, CLAUDE, PROJECT-INSTRUCTIONS and the Project-knowledge sync). Fix sessions follow, planned from the two registers, each with its own entry; the README update (D112.2 item 4) is last. Scripts that need the GRIB cache are run in a fix session when the owner attaches the drive.
- **D114.4 The audit's limits.** Read-only: no existing tracked file is fixed or edited, apart from the session's own record steps. Frozen scripts are never edited (D62.3(a)) and are run only in offline guard or gate modes that read no data valid on or after 2026-08-01; their SHA-256 values are checked against the recorded ones. No 2026-27 value is read or scored; no MLwx-live observation snapshot is read beyond line counts; no error is computed (D105.6).
- **D114.5 Network (session 120).** A fresh clone of MLwx-live into a temporary folder; `gh` run lists and run logs for MLwx-live; one fetch of the public page; and two byte-range fetches for F162.9(6), by D113.7's method, judged by D113.6(e)'s mark. Nothing is pushed and no workflow is triggered.
- **D114.6 The GRIB cache.** The drive is not attached for session 120. A script mode that needs the cache is listed as "not run: needs cache".
- **D114.7 The register.** Each audit session writes a register with one row per item checked: id, area, file, what was checked, result, severity (OK, cosmetic, stale, wrong, blocks), proposed fix, and four flags: the fix would touch a record file (never edited, D90.4, D90.6); a frozen script; the live test (D105.5(k)); or needs an owner ruling. Rows that pass are kept as OK.
- **D114.8 Live index.** Removed: none. Added: D114 and F163 (F163 when it is written).

---

## 2026-10-21: Session 120 finding: the project health check, audit part 1 (the code)

**F163. D114 was recorded first. The code of MLwx and MLwx-live was audited read-only under D114.4 to D114.6: layout, old paths, every script's modes, the frozen scripts' SHA-256, every eligible check mode, the tests and environment, session 114's open items, MLwx-live, and T5's two extra fetches. Nothing was fixed. No 2026-27 value was read or scored, no snapshot was read beyond line counts, no error was computed (D105.6). Network only in Steps 8 and 9. Full output: `notes/session-120-output.txt`; register `notes/session-120-register.csv`. Run 2026-10-21. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, eccodes 2.48.0.**

- **F163.1 Start and D114.** HEAD 046c800, tree clean; 181 tests OK. D114 appended byte-equal (14 lines, `diff` and `cmp`), 0 em-dashes.
- **F163.2 The register.** 55 rows: OK 31, cosmetic 8, stale 16, wrong 0, blocks 0. Owner ruling on 14. No proposed fix edits a frozen script or a record file.
- **F163.3 Layout and paths.** 20 tracked top-level items: the 16 of D91.3 and 4 later ones, each traced (src/ D103.3, tests/ D95.8, deploy/ D103.11, ANALYSIS.md D106.14; also docs/sessions/ and docs/commits/ D92.2). Every ignored item is covered by `.gitignore`. Old repo path: 48 files (as expected), 53 with any /Users/ path, all record files and text only; live code has none.
- **F163.4 Scripts.** 145 rows in `data/processed/session120_audit/scripts.csv`. Frozen: 8; SHA-256 equal at 6 of 8, 0 mismatches; `session48_reserved_year.py` and `session60_combine_design.py` have no recorded value (one git commit each), and session 39's sits only in a notes file. Stage B's three frozen scripts and three others read SPEC 3.4's table by two text markers; both are present.
- **F163.5 Checks** (in a temporary clone of HEAD, so writes landed there; 77 modes): PASS 44, FAIL 7, not run 26 (network, cache, 2026-27, frozen or look; none over 30 min). Stage B's three `--guard-check` modes pass after the folder move; session 92's verifier passes on all 130 months of both pulls; every other stage C gate passes, including session 109's Gates A and B. FAILs: session 114 `--verify` (its template still says IFS is pending: 818 numbers against 783, 757 positional mismatches); session 92 and 95 `--gate` (D98.2); new: session 96 `--gate` (same cause, F122.3 searched in DECISIONS.md) and session 117 `--verify` (it rebuilds from HEAD, which now holds its edit); session 63's join check stops as F108 records; session 91 `--gate` needs D83.6's test chunk (the session's month input rebuilt nothing; not a fault).
- **F163.6 Tests and environment.** pytest not in `.venv`; `requirements.txt` equals the venv at 20 of 20 pins, but matplotlib's 9 dependencies are unpinned. No test covers the workflows, ANALYSIS.md's numbers or the scripts of sessions 112 to 119.
- **F163.7 Session 114's items (F160.9(4)), pinned:** `part1.md` (5 IFS places) and `part2_comparisons.md` (ANALYSIS.md l.1282 to 1599 missing); no IFS figure (FIG_SOURCES l.1540); `subdaily_max` l.587 to 597 (no effect); `F156_4` l.161 to 172 has no IFS entry, so the check is skipped.
- **F163.8 MLwx-live** (clone `adc73c3`). The workflow differs from the template only in the two `SET-AT-DEPLOY` lines. Stale text: the template README l.65 to 68 against D112.6, and the deployed README is still session 109's v1 (12 airports). Six actions are forced from Node.js 20; the first Node.js 24 majors are listed. Python 3.12.15 throughout. Since the redeploy: 5 runs, all pushed; 2 committed only `last_run`; 4 scheduled runs in 43 slots (9 %); issue lag 5.18 to 6.57 h. From 2026-10-19T12z: 8 of 8 cycles logged once, 0 lost, 0 issued twice. The page matches the log.
- **F163.9 T5 (F162.9(6)).** 2 fetches on the main 0.25 degree grid (2024-02-03T00z step 24; 2026-07-31T00z step 21, the nearest that exists): SHA-256, metadata and 30 of 30 rows bit-equal; D113.6(e)'s mark not shown.
- **F163.10 Proposed fix sessions** (detail in the output file). (1) Small code fixes and the D98.2 constants (one ruling). (2) Session 114's outputs (rulings on write-once files and figures); can share with (1). (3) MLwx-live: README, actions, a Python pin and no last_run-only commits, with an entry under D105.5(k) and a redeploy. (4) The cache checks, when the drive is attached. (5) Rulings only: pytest, session 86's gate, the outside scheduler. (6) README last.
- **F163.11 Readings for the owner.** (1) Nothing blocks and nothing is wrong; every stale item is a check or text left behind by later work. (2) Session 96's gate and session 117's verify cannot be re-run as they stand; they are not named in D98.2. (3) Only about a day of the :15 and :40 schedule exists, too little to judge the issue lag. (4) Session 63's two scripts rewrite their notes outputs on each run; they should be run only in a clone. (5) Session 109's Gate A took 29.4 min, close to D114's 30-minute limit.
- **F163.12 What was not done.** No fix, and no edit to any existing tracked file except DECISIONS.md and STATUS.md. No cache-, network- or 2026-27-mode run outside Steps 8 and 9. No push and no workflow run. Pointers: `scripts/session120_audit.py`; `data/processed/session120_audit/`.
