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
- D112: F160 accepted, the order of the next work, and an audit of MLwx-live's runs with three workflow fixes.
- D114: F162 accepted, the layout baseline, and the project health check's plan and audit limits.
- D115: F163 accepted, the Project-knowledge sync made a hand upload, and the record audit's scope.
- D116: F164 accepted, the rulings for fix groups 1 and 2 (recorded fingerprints, D116.10), and session 122's scope.
- D117: F165 accepted, fix group 3 for MLwx-live (template changes, the last_run.at skip) and the issue-lag re-measure.
- F163: session 120's finding (the health check's code audit: 55 register rows, none wrong or blocking; 16 stale items grouped into fix sessions).
- F164: session 121's finding (the health check's record audit: 109 register rows, one wrong (README's data credits), none blocking; grouped into fix sessions).
- F165: session 122's finding (fix groups 1 and 2 done: gates, frozen-script hashes, citation check, session 114's outputs and IFS figures via new scripts).
- F166: session 123's finding (issue lag re-measured: median 5.70 h, 12 % of slots run; six actions on Node.js 24; Python 3.12.15 pinned; the last_run.at skip).
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

---

## 2026-10-21: Session 121 decision: F163 accepted, the Project-knowledge sync, and the record audit's scope (owner, planning chat)

**D115. Owner decisions, planning chat (after session 120's commit): F163 accepted; the hand upload made the standard for Project knowledge; the archive's place there; session 121's scope; a candidate for the longer-term plan; and Live index changes.** Written at the start of session 121, before any other edit. No 2026-27 value has been read or scored.

- **D115.1 F163 accepted,** with its review correction (F163.5 reads "every other stage C gate passes"), its readings (F163.11) and its grouping of fixes (F163.10), which stay open for the fix sessions.
- **D115.2 Project knowledge (owner; amends D93.15(b)).** The hand upload is the standard. After the owner commits and pushes a reviewed session, the planning chat lists each changed file that Project knowledge holds, with its byte size in the repo; the owner uploads each by hand and checks its size. Why: the staging tool that `docs/PROJECT-INSTRUCTIONS.md` section 5 relies on was missing from the planning chats after sessions 119 and 120, and reading the files through the Filesystem extension would put their contents into the chat. `ANALYSIS.md` is one of the files Project knowledge holds; section 5's list omits it, and the copy there dated from 2026-10-14 until the owner re-uploaded it on 2026-10-21. Section 5 is edited in a fix session.
- **D115.3 The archive's place.** Project knowledge holds `DECISIONS-archive.md` at its root, not at `claude/DECISIONS-archive.md` as section 5 says. Section 5's text is corrected in a fix session; the file is not moved.
- **D115.4 Session 121's scope (D114.3; read-only under D114.4).** The record: SPEC, STATUS, DECISIONS (the archive by script and by entry, never read in full, D93.12), RESULTS, ANALYSIS (its text against DECISIONS only; its numbers are register rows C08 and C09's), the root README and the READMEs in `scripts/`, `data/`, `docs/` and `notes/`, CLAUDE, `docs/PROJECT-INSTRUCTIONS.md`, every citation in them, and the sync. SPEC 3.4's two markers and its table format are recorded as fixed for every later edit (register S05). The register follows D114.7. No network, no GRIB cache, and no frozen script beyond stage B's `--guard-check` modes.
- **D115.5 What the planning chat saw in Project knowledge (2026-10-21).** Eight documents at its root, with these listed dates: ANALYSIS.md, DECISIONS.md and STATUS.md 2026-10-21; DECISIONS-archive.md 2026-10-18; PROJECT-INSTRUCTIONS.md, SPEC.md and CLAUDE.md 2026-10-07; RESULTS.md 2026-09-29. The archive's copy is 1,497,010 bytes, the same as the repo's, although its listed date is older than the repo's last change to it, so a listed date does not show whether a copy is current. The reported knowledge size was 657,869 after ANALYSIS.md's upload, below the archive's own byte count, so it is not a byte count.
- **D115.6 A candidate for the longer-term plan (D112.2 item 5; owner).** Does the curve's correction (curve minus raw GFS) for a valid hour predict the direction and size of raw GFS's revision for that same hour in the next cycle (the next cycle's raw GFS minus this cycle's)? Descriptive first, on spent stage C rows (D107.2's terms), with its rows, pairing and statistics fixed in its own entry before any value is computed. Nothing is read for it in session 121.
- **D115.7 Plan.** Session 121: this entry, the record audit, F164. Then fix sessions planned from both registers (F163.10's grouping with F164's additions), each with its own entry; the README update last (D112.2 item 4). The issue lag after the redeploy is re-measured in the MLwx-live fix session (F163.8).
- **D115.8 Live index.** Removed (archived): D108, D111, D113, F157, F160, F161 and F162, which are settled (IFS is closed by D113 and F162; the comparisons and the live-run audit are recorded and accepted). Added: D115 and F164 (F164 when it is written). After session 121: D93, D103, D105, D112, D114, D115, F163, F164.

---

## 2026-10-21: Session 121 finding: the project health check, audit part 2 (the record)

**F164. D115 was recorded first. The record was audited read-only under D114.4 and D115.4: every citation in 12 files, SPEC (with stage B's 3.4 span), STATUS, DECISIONS (the archive by script and by entry), RESULTS, ANALYSIS (text only), the READMEs, CLAUDE, `docs/PROJECT-INSTRUCTIONS.md` and the Project-knowledge sync. Nothing was fixed. No 2026-27 value, MLwx-live file or GRIB cache was read and no error was computed (D105.6). One read-only network request was made in breach of the prompt (F164.8). Full output: `notes/session-121-output.txt`; register `notes/session-121-register.csv`. Run 2026-10-21. Python 3.12.2.**

- **F164.1 Start and D115.** HEAD b4d3eb5, tree clean; 181 tests OK. D115 appended byte-equal (12 lines, `diff` and `cmp`), 0 em-dashes.
- **F164.2 The register.** 109 rows: OK 63, cosmetic 17, stale 28, wrong 1, blocks 0. Owner ruling on 17. No proposed fix edits a frozen script or a record file, or touches the live test.
- **F164.3 Citations.** 1,754 references in 12 files (811 to a sub-item or letter): 1,749 resolve to the entry, item label and letter; 5 are F164 in D115, which resolve now. `archive_decisions.py --citations` covers 5 of the 12 files and entry numbers only (CI13).
- **F164.4 SPEC.** 3.4's markers appear once each; the span is l.252 to l.283, 2,050 bytes, SHA-256 a02cbe9e03b52d881fab01c7ec3c9612effdaa5d049e97cd0e0ba369803e9ef9, both tables parse (6 rows; 8 and 9 columns); stage B's three `--guard-check` modes pass. Section 9 matches D100 to D102. SPEC cites nothing after D102 and F150: section 1's airports and end goal (SP04, SP05), stage G's bullet and the "only stage C has a section" note (SP06, SP07) are stale.
- **F164.5 STATUS and DECISIONS.** Every STATUS statement traces; all 9 open questions are still open. Live file: index and entries agree (D115 is added at the archive step), in order, no duplicates. Both files: D1 to D115 and F1 to F163 each once, none missing. The archive is in archiving order, not date order, by design (DE03). D93.4's open item was closed by D95.2.
- **F164.6 The one wrong item (RM05).** README section 9 says ECMWF IFS and AIFS were "probed only, no data committed", but `data/processed/session113/` commits their values at 12 airports, with the NBM grid, NBS, MAV, CLI and GHCN-Daily, about 101 MB. Only NBM's AWS grid and MAV at DSM are credited, and no session has read ECMWF's or IEM's terms. The repo is public (D90.4).
- **F164.7 Other headline findings.** RESULTS 7, README 1 and 5 still say stage G "comes next" (RE01, RM01). README's map lacks src/, deploy/, ANALYSIS.md, figures/analysis/ (RM03); scripts/README stops at session 98b (RM07). ANALYSIS does not state IFS's cold reading or F162's outcome (AN05). PROJECT-INSTRUCTIONS section 5 is stale on all four counts D115.2 and D115.3 name (PI04 to PI07); section 4's Filesystem reach (PI02); section 9 lacks D105.5 and D105.6 (PI12); its invocation equals D93.16 (PI03). Sync: ANALYSIS, DECISIONS and STATUS current; the archive equal by size (D115.5); PROJECT-INSTRUCTIONS, SPEC, CLAUDE and RESULTS changed after their listed dates (PK05 to PK08). The eight files total 1,898,480 bytes at HEAD.
- **F164.8 Limits breach.** In Step 6, `gh repo view zadams03/MLwx --json visibility` was run (one read-only request; it returned PUBLIC). The prompt allowed no network. Nothing was changed; RM05 cites D90.4, not that call.
- **F164.9 Proposed grouping** (F163.10's groups, with this register's rows). (1) Code: add CI13. (2) Session 114's outputs: add AN02, AN03 and AN05 (ANALYSIS text, after C08). (3) MLwx-live and (4) cache checks: nothing added. (5) Rulings only: add SP05, ST02, RM02 (is the goal still "private"), SP07 (a stage G section), SP08, PI07 and PK10 (the size rule's unit), CL05 (after T02), DE03. (6) README last: add RM01, RM03, RM04, RM07, RM09, RM10, RM11. New (7) the record text, one session: SPEC SP04, SP06, SP10, SP11 (keeping F164.4's span hash); RESULTS RE01, RE02, RE04, RE05; CLAUDE CL03, CL04, CL07; PROJECT-INSTRUCTIONS PI01, PI02, PI04, PI05, PI06, PI08, PI12 (with PK09 and PK11); STATUS ST10, ST11 at each overwrite. New (8) owner only, no session: compare the Project copies' sizes for PK05, PK06, PK07 and PK08 and re-upload any that differ. New (9) data credits (RM05): read each source's terms in a session allowed the network, then credit them; ahead of (6), because the repo is public.
- **F164.10 Readings for the owner.** (1) Nothing blocks. RM05 is the only wrong row, and it is about terms, not results. (2) Most stale rows have one cause: SPEC, RESULTS, the READMEs and CLAUDE were last edited in sessions 99 to 108, before stage G went live. (3) DECISIONS.md reached 79,037 bytes with D115 before the archive step; one more long entry in a session that archives nothing would pass D93.9's limit. (4) The archive is 79 % of the eight files' bytes and grows each session, so section 5's size rule matters more over time.
- **F164.11 What was not done.** No fix, and no edit to any existing tracked file except DECISIONS.md, DECISIONS-archive.md (archive step) and STATUS.md. No number in ANALYSIS re-checked. Pointers: `scripts/session121_audit.py` (--citations, --spec, --archive, --paths, --sync); `data/processed/session121_audit/`.

---

## 2026-10-22: Session 122 decision: F164 accepted, the rulings for fix groups 1 and 2, and session 122's scope (owner, planning chat)

**D116. Owner decisions, planning chat (after session 121's commit): F164 accepted; the rulings that fix groups (1) and (2) need; session 122's scope; and Live index changes.** Written at the start of session 122, before any other edit. No 2026-27 value has been read or scored.

- **D116.1 F164 accepted,** with its readings (F164.10) and its grouping (F164.9). Group (8) is done: the owner re-uploaded SPEC and RESULTS and kept PROJECT-INSTRUCTIONS and CLAUDE after comparing sizes (PK05 to PK08). F164.8's one network request is accepted; it changed nothing.
- **D116.2 Tests (T02; owner).** The suite stays on unittest. pytest is not installed. The command is `.venv/bin/python -m unittest discover -s tests`, stated in `tests/README.md`. CLAUDE.md gets the same line in the record-text fix session (CL05).
- **D116.3 The gate constants (C06, C07; owner).** The `--gate` modes of sessions 92, 95 and 96 searched DECISIONS text for F122.3's SHA-256. None of the three scripts is edited (D116.10): session 92's SHA-256 is listed in three stage C table meta files, and sessions 104 and 106 record session 96's. A new `scripts/session122_gates.py` runs each of the three gates with the value held as a constant in `session91_grib_pull.py` (`TRAINING_SET_SHA256`, already checked by a test) in place of the DECISIONS lookup, swapped at run time; the frozen session 86 is unchanged. Session 92's verify path, which the pull workflow uses, does not change.
- **D116.4 Frozen scripts' SHA-256 (S03, S04; owner).** The SHA-256 of `session39_sealed_test.py`, `session48_reserved_year.py` and `session60_combine_design.py` are recorded as constants in a new test, `tests/test_frozen_scripts.py`, beside the five frozen scripts' recorded values (F163.4), so all eight are checked by the suite. The scripts are not edited.
- **D116.5 The citation check (CI13; owner).** `scripts/archive_decisions.py --citations` also checks `ANALYSIS.md`, the READMEs in the root, `scripts/`, `data/`, `docs/`, `notes/` and `tests/`, and `docs/PROJECT-INSTRUCTIONS.md`, by entry number.
- **D116.6 Session 114's outputs (A01, C08; owner).** `part1.md` and `part2_comparisons.md` stay as written (write-once). `session114_comparisons.py` is not edited, because session 117 records its SHA-256 (D116.10). A new `scripts/session122_analysis.py` imports session 114's code, adds IFS from session 117's committed tables, and writes `part1_s122.md` and `part2_comparisons_s122.md` beside the old files; `SUPERSEDED.md` in the same folder says which files replace which, and why. Its `--verify` checks `ANALYSIS.md` against the new render and supersedes session 114's `--verify`, which stays as written. Session 117's `--verify` re-renders from session 117's parent commit instead of HEAD (C09): by an edit to `session117_ifs_guide.py` only if no script, test or meta file records its SHA-256; otherwise in `session122_analysis.py`.
- **D116.7 The IFS figure (A02; owner).** IFS is drawn by `session122_analysis.py` in new figure files ending `_s122.svg`; the five existing `figures/analysis/comparison_*.svg` stay byte-equal. `ANALYSIS.md` points to the new files where it names the comparison figures.
- **D116.8 ANALYSIS.md text (AN02, AN03, AN05; owner).** Three text fixes, no number changed: the note on which files Part 1 and Part 2 are rendered from (AN02); one sentence naming the NBM grid in Part 1 item 1, with item 4's figures (AN03); one sentence in Part 1 item 4 and the IFS note saying IFS reads cold at 10 of 12 airports (F160.4) and the reading check found no fault, so the cold error is the model's own (F162.8) (AN05).
- **D116.9 Session 122's scope.** D116.2 to D116.8, and the group (1) rows needing no ruling: L09 (the `.gitignore` comment), T03 (pin matplotlib's nine dependencies), T04 (`tests/README.md`), A03 (`subdaily_max`'s window count check) and A04 (IFS's cycle counts against F160.3), both done in `session122_analysis.py`. Deferred: C11 to the README update (it is a `scripts/README.md` note, RM07's file); T05's optional tests. Not in scope: groups (3) to (7) and (9), and the other group (5) rulings (S06, the outside scheduler, SP05, SP07, SP08, PI07, DE03). No logged value, model, live file or frozen script changes, so D105.5(k) is not engaged.
- **D116.10 Recorded fingerprints (owner).** A script whose SHA-256 is recorded by another script, a test, or a data file's meta file is not edited; a fix to it goes in a new script that imports it. Session 122 found that sessions 104 and 106 record session 96's SHA-256 (F138), session 117 records session 114's, and three stage C table meta files (sessions 96, 104 and 106) record session 92's. Editing such a script would break the record of what produced those results. An audit inventory that lists every script's SHA-256 at one commit (`data/processed/session120_audit/scripts.csv`) is a snapshot, not such a record.
- **D116.11 Live index.** Removed: none. Added: D116 and F165 (F165 when it is written). After session 122: D93, D103, D105, D112, D114, D115, D116, F163, F164, F165.

---

## 2026-10-22: Session 122 finding: the health check, fix session 1 (code, and session 114's outputs)

**F165. D116 was recorded first, then rewritten before any commit under the owner's ruling that a script whose SHA-256 is recorded elsewhere is not edited (D116.10). Fix groups (1) and (2) of F163.10 and F164.9 were done. Nothing was scored; no 2026-27 value, MLwx-live file, GRIB cache or network was used; no frozen script was edited or run. Full output: `notes/session-122-output.txt`. Run 2026-10-22. Python 3.12.2, numpy 2.5.2, matplotlib 3.11.2.**

- **F165.1 Start and D116.** HEAD ccaad92, tree clean; 181 tests OK; DECISIONS.md 44,140 bytes. The first D116 was appended byte-equal; at Step 4 the suite failed (below), and the owner rewrote D116 (adding D116.10 and D116.11); the first block was removed and the new one appended byte-equal (15 lines, `diff` and `cmp`), 0 em-dashes. At review, before any commit, the owner corrected D116.3, D116.6 and D116.10 to match what was done; the block was replaced in place, byte-equal to the session file (`diff` and `cmp`), 0 em-dashes.
- **F165.2 Why Step 4 stopped.** Editing `session96_stagec_table.py` changed its SHA-256, which `session106_claim_table.py` and `session104_curve_cv.py` hold (F138), so `tests/test_stagec.py` (23 tests) could not load. The edit was reverted. The owner then ruled that a SHA-256 held in a meta file also counts (D116.10): session 92's is listed as an input in three stage C table meta files (sessions 96, 104, 106), so session 92's edit was reverted too.
- **F165.3 Small fixes.** L09: `.gitignore` comment says about 39 GB. T03: matplotlib and its 9 dependencies under their own heading; 29 pins equal `pip freeze`, 0 differences. T02, T04: `tests/README.md` states unittest, D116.2's command, under a minute.
- **F165.4 Frozen scripts (S03, S04).** `tests/test_frozen_scripts.py` holds all 8 SHA-256 values: 6 from their records, sessions 48 and 60 computed (one commit each, 74e7077 and 0e29835); 8 of 8 equal.
- **F165.5 Gates (C06, C07).** `scripts/session122_gates.py` runs sessions 92, 95 and 96's `--gate` with F122.3 from `TRAINING_SET_SHA256` (equal to F122.3), swapping each lookup at run time; sessions 86, 92, 95 and 96 unchanged. Session 92 PASS (2023-01, 0 mismatches); 95 PASS (5,861 compared, 0 mismatches, 101 s); 96 PASS (5,861, 0 failures). Session 92's verify form: 65 of 65 and 65 of 65 months. One test added.
- **F165.6 Citations (CI13).** `archive_decisions.py --citations` covers the 13 files of D116.5: 1,603 references and 213 distinct numbers (before: 5 files, 1,173 and 202); all resolve once F165 exists.
- **F165.7 ANALYSIS.md text (AN02, AN03, AN05).** No existing number changed. Item 1 names the NBM grid (2 of 5 better, 3 worse hourly; 2 of 5 daily maximum; F157.3, F157.4). Item 4 and the IFS note say IFS reads cold at 10 of 12 (F160.4) and the reading check found no fault (F162.8). The header note names the `_s122` renders (D116.6).
- **F165.8 Session 114's outputs (C08, A01, A02).** `scripts/session122_analysis.py` imports session 114 and session 117's IFS helpers. Its `--verify`: Part 1 834 numbers and the Part 2 comparisons section 7,886, 0 mismatches, text identical. It wrote `part1_s122.md`, `part2_comparisons_s122.md` and `SUPERSEDED.md`; the old two are unchanged. Four IFS figures `comparison_*_s122.svg` (hourly MAE, daily maximum MAE, skill, lead band), byte-equal over two runs; the five old figures reproduce byte-equal and are unchanged.
- **F165.9 A03, A04, C09.** A03: the every-window check finds 0 of 3,310 D98.10 days failing; 35 of 12,886 every-cycle days fail, all on the window's last local day (2026-07-31 or 08-01, cut by the limit) and already unpaired; the 5 IFS daily-maximum tables rebuild byte-equal. A04: IFS's cycle counts (F160.3) held as a constant with a test; the loader agrees at 12 of 12; `match_counts.csv` rebuilds byte-equal to session 117's. C09: session 117's SHA-256 is held by no script, test or meta file, so its `--verify` was edited to re-render from 5df783a^ against 5df783a's text: PASS.
- **F165.10 Tests.** 185 OK (181, plus 2 frozen-script tests, the gate test and the IFS-count test). Until F165 was written, the citation test failed only on F165, as the owner accepted.
- **F165.11 Readings for the owner.** (1) D116.10 makes many fixes new scripts rather than edits. Settled: `data/processed/session120_audit/scripts.csv` lists every script's SHA-256, and D116.10 confirms that this audit inventory is a snapshot, not a record. (2) Session 114's trial `--figures` does not reproduce its own repo figures byte-equal (PNG previews change clip-path ids); session 122 switches the preview off for that check. (3) Session 117's `--subset` still stops if session 114 changes, by design. (4) A03's 35 every-cycle days are a count, not a fault.
- **F165.12 Not done.** C11 (to the README update) and T05's optional tests (D116.9); groups (3) to (7) and (9) and the other group (5) rulings. Pointers: `scripts/session122_gates.py`, `scripts/session122_analysis.py`, `tests/test_frozen_scripts.py`.

---

## 2026-10-27: Session 123 decision: F165 accepted, fix group (3) for MLwx-live, and the issue-lag re-measure (owner, planning chat)

**D117. Owner decisions, planning chat (after session 122's commit): F165 accepted; the order of the remaining fix sessions; the issue-lag re-measure; the outside scheduler left open; MLwx-live's template changes and how the live test treats them; session 123's scope; and Live index changes.** Written at the start of session 123, before any other edit. No 2026-27 value has been read or scored.

- **D117.1 F165 accepted,** with its readings (F165.11).
- **D117.2 Order (owner).** Fix group (3) now. Then groups (7) and (9) together in one session, whose planning rules on SP05, SP07, SP08, PI07 with PK10, DE03 and S06. Group (4) when the drive is attached. Group (6), the README, last (D115.7).
- **D117.3 The issue lag (F163.8, D112.6(d)).** Re-measured read-only, from the redeploy's check run 39488813037 (2026-10-20) to the latest cycle available at session 123, by D112.5's method and with F161.8's measures, scheduled and manual runs reported apart. Owner ruling: the 2026-10-21 18z cycle was issued by a manual run and counts as manual; so does any other cycle the run log shows issued by a manual run (2026-10-22 12z, run 39815698496). No error is computed (D105.6).
- **D117.4 The outside scheduler stays open.** The owner rules on it in a later entry, after reading D117.3's figures. Nothing is built for it in session 123.
- **D117.5 Template changes (`deploy/mlwx-live/`).** (a) The six actions of F161.10(4) move to their first major whose `action.yml` runs on Node.js 24, each confirmed from that tag. (b) `setup-python`'s version is pinned to `3.12.15`, the version every run has used (F161.10(5), F163.8). (c) A run whose only change in the tree is the value of `last_run.at` in `state/tracker_gfs.json` commits nothing, pushes nothing and does not publish the page, and exits 0. Any other change (a log or obs file, a stop, a change of `last_run.status`) keeps D112.6(b)'s commit, push, check and page unchanged. Why narrowed: `page.py` reads `last_run.status` to show the "waiting" note, and a stopped cycle is recorded in `state/` only (session 123, Step 3). (d) The template README's stale lines (F163.8) are brought into line with D112.6 and this entry. `MLWX_COMMIT` and `MODELS_TAG` stay as deployed, and nothing under `src/` changes.
- **D117.6 The live test (D105.5(k)).** No model changes, and no code that writes a logged value: the runner and models are those already pinned and Python is the version already used; (c) stops only commits that change `last_run.at` alone, which no code reads (session 123, Step 3). The live test treats every row unchanged. Cost: on a run that skips, the page's build time is not refreshed.
- **D117.7 The redeploy (owner, after session 123's commit).** The owner copies the template's workflow and README into MLwx-live with `MLWX_COMMIT` and `MODELS_TAG` unchanged. The deployed values are recorded in the next session's entry. D112.8's rule on manual runs holds until then.
- **D117.8 Network (session 123).** A fresh clone of MLwx-live into a temporary folder; `gh` run lists and run logs for MLwx-live; read-only `gh api` calls for the six actions' tags and their `action.yml`; one fetch of the public page. Nothing is pushed and no workflow is triggered.
- **D117.9 Plan.** Session 123: this entry, the re-measure, the template changes and their checks, a test of the template, F166. Then the owner's redeploy, then groups (7) and (9).
- **D117.10 Live index.** Removed: none. Added: D117 and F166 (F166 when it is written).

---

## 2026-10-27: Session 123 finding: fix group (3), MLwx-live (the template), and the issue-lag re-measure

**F166. D117 was recorded first, then replaced in place before any commit under the owner's ruling after the Step 3 stop (D117.5(c), D117.6 narrowed; D117.3 adds 2026-10-22 12z as manual). The issue lag was re-measured read-only and MLwx-live's template changed (D117.5). Nothing was pushed, no workflow triggered, nothing installed; no 2026-27 value was read or scored, `obs/` files were counted by lines only, no error computed (D105.6); nothing under `src/` changed. Full output: `notes/session-123-output.txt`. Run 2026-10-27. Python 3.12.2.**

- **F166.1 Start and D117.** HEAD f64bf7a, tree clean (the prompt untracked); 185 tests OK; DECISIONS.md 54,686 bytes. The first D117 was appended byte-equal; Step 3 stopped (F166.3); the owner rewrote D117 and Steps 3 to 5; the first block was replaced in place by the new one, `diff` and `cmp` byte-equal (16 lines), 0 em-dashes.
- **F166.2 The issue lag (D117.3).** Session 118's audit script is not recorded under D116.10 (only in session 120's inventory); it cannot take the window or the :15 slot, so `scripts/session123_live_lag.py` imports it unchanged. Each run log's step lines start with a byte-order mark that its line pattern rejects (the cause of F163.8's hand-read row); the new script strips it before parsing. Fresh clone `a441a86`; run list fetched 2026-10-27T15:41Z; window 2026-10-20T20:03Z on: 41 runs (38 scheduled, 3 manual), all green, all pushed, 41 pages published, 0 stale checkouts, 0 silent push failures, Python 3.12.15 in all 41.
  | measure | F161.8 | F163.8 | session 123 |
  |---|---|---|---|
  | scheduled runs / slots | 39 / 150 (26 %) | 4 / 43 (9 %) | 38 / 328 (12 %): :15 16, :40 22 |
  | delay to latest slot, median / max | 34 / 289 min | 6.0 to 30.9 min | 13.6 / 32.8 min |
  | gaps between runs, median / p90 / max | 3.20 / 5.65 / 6.98 h | 2.43 to 5.79 h | 3.68 / 5.59 / 7.40 h |
  | issue lag, all cycles: median / p90 / min / max | 5.57 / - / 4.47 / 8.98 h (29) | 5.18 to 6.57 h (3) | 5.70 / 8.40 / 4.18 / 9.20 h (27) |
  | issue lag, scheduled-issued | - | - | 5.85 / 8.43 / 4.18 / 9.20 h (25) |
  Per UTC day, 21 to 26 Oct: 5, 6, 6, 7, 6, 4 scheduled runs of 48 slots. Manual-issued: 2026-10-21 18z (4.35 h) and 2026-10-22 12z (4.73 h), as D117.3. Cycles 2026-10-20 18z to 2026-10-27 06z: 27 of 27 logged with leads 3 to 48 complete and a snapshot; 0 lost, 0 issued twice, no stop. Whole-history check: 0 log or obs files modified, deleted or renamed. The cycles table's `snapshot_added_once_never_changed` is False for all 27: session 118's per-file history uses `git log --follow`, which reads each new snapshot as a copy of the one before (status C), as in session 118's own table (20 False); without `--follow` each of the 27 has one add. Page: 2026-10-27 06z issued 10:34 on 49 airport lines, equal to the log's latest.
- **F166.3 What a skipped run changes (Step 3).** 14 of 41 commits touched only `state/`; in all 14 the only path changed is `last_run.at`. At `d6ca3e4`, `page.py:113` reads `last_run.status` (the "waiting" note): the first Step 3 stopped on it. No code reads `last_run.at`; the workflow never names `last_run`. Reading: a skipped run leaves the page's build time and the 24-hour stop-note window as last published.
- **F166.4 The action tags (D117.5(a)), from each tag's `action.yml`.** checkout v5, setup-python v6, cache v5, configure-pages v6, deploy-pages v5 (each previous major node20). upload-artifact runs inside upload-pages-artifact: v3 and v4 pin node20 builds (v4 pins v4.6.2), v5 pins v7.0.0 (node24), so upload-pages-artifact v5. Its new default (hidden files left out) does not matter: `site/` holds only `index.html`.
- **F166.5 The template (D117.5(b) to (d)).** `python-version: "3.12.15"`. A new step after the runner decides, with Python's standard library, whether the tree's only change is `last_run.at` (or nothing); the commit step and the three page steps run only otherwise, their bodies unchanged; the exit code 3 rule unchanged. README: the state file and the workflow line (schedule, skip rule, push check). YAML parses (Ruby Psych 3.1.0; no PyYAML here); the diff holds only (a) to (d); both `SET-AT-DEPLOY` lines kept.
- **F166.6 Push test** (the two steps from the YAML, `bash --noprofile --norc -eo pipefail`, temporary repos): (i) `last_run.at` only: no commit, page skipped; (i-b) status "waiting" and (i-c) a stop added: commit, push, page; (ii) new log: exit 0, HEAD equals the remote (also after one rejected push and a rebase); (iii) conflict: exit 1, rebase aborted; (iv) every push rejected: exit 1 after 3; (v) nothing changed: exit 0, page skipped. All as expected.
- **F166.7 Tests.** `tests/test_live_template.py`, 10 tests (cron, Python, the six majors as constants, the placeholders, the skip condition, and the skip step on synthetic state files). Suite: 195 OK (after F166; before it the citation test failed only on D117.10's forward citation of F166).
- **F166.8 Readings for the owner.** (1) For D117.4: about 6.8 days of :15 and :40 ran 12 % of slots, a median lag of 5.70 h and a max of 9.20 h (earliest possible 4.17 h); the median is no better than F161.8's hourly schedule (5.57 h), though the worst delay to a slot fell from 289 to 33 min. No cycle came near the 24-hour loss limit. (2) The 2026-10-22 manual run started at 16:38Z, inside D112.8's :35 to :55 band; it overlapped no scheduled run. (3) After the redeploy, the page's "Page built" time shows the last run that changed something, not the last run. (4) The job's environment URL comes from the publish step, so a skipped run sets none; how GitHub shows that was not checked.
- **F166.9 Not done.** The redeploy (D117.7, owner). No outside scheduler. Session 118's and 120's scripts unchanged. MLwx-live's deployed README not compared again (it is replaced at the redeploy). Pointers: `scripts/session123_live_lag.py`, `data/processed/session123_runs.csv`, `session123_cycles.csv`, `tests/test_live_template.py`.
