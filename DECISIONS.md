# DECISIONS.md — the project's memory of *why*

This is the live log. New entries are added at the bottom, and no entry is
ever edited or deleted. Entries outside the Live index move verbatim to
DECISIONS-archive.md (D93.8). Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- D103: F151 accepted, and stage G's design (the live product v1, GFS only).
- D104: F152 accepted, the deployment, the runner fix, and onboarding the remaining airports.
- F153: session 110's finding (the runner fix, the onboarding tool and its gate, 49 airports, the combined models, a dry run).
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

## 2026-10-13: Session 110 decision: F152 accepted, the deployment, the runner fix, and onboarding (owner, planning chat)

**D104. Owner decisions, planning chat (after session 109's commit and the hand deployment): F152 accepted, the deployment recorded, the runner fix, and onboarding the remaining airports.** Written at the start of session 110, before any other edit. No value on or after 2026-08-01 has been scored.

- **D104.1 F152 accepted,** with all eight F152.11 readings as written, including reading 8: errors older than 7 days are not applied to the tracker.
- **D104.2 The deployment (owner, by hand, 2026-10-12, not by a session).** Repo: public `zadams03/MLwx-live`, root commit `6cfb0d3`, files copied from `deploy/mlwx-live/`. Workflow values: `MLWX_COMMIT` `0f89f0157ded0e26e12c3985ff80dd5eb504d197` (session 109's commit), `MODELS_TAG` `gfs-models-12`. Models: Release `gfs-models-12`, asset `gfs-models.tar`, 306,082,816 bytes, 50 tar entries, no `._` entries, tar SHA-256 `5d61a693b1966672e5ce583ba8d0139b79a05573980f44112c48cbda1366ba78`, built from `../MLwx-live-build/models/`; its manifest SHA-256 was checked equal to F152.5's before upload. Pages: source GitHub Actions, https://zadams03.github.io/MLwx-live/.
- **D104.3 The first runs.** (a) By hand, latest cycle only, about 20:00 UTC on 2026-10-12: issued 2026-10-12 12z, green; 06z not issued by design (older than the newest logged cycle, F152.8). (b) Scheduled, cron 22:10 UTC, started 02:58 UTC on 2026-10-13: issued 18z and published the page, but the job was red: the runner exited with code 3 because it counted the 06z tracker-order skip as a cycle that issued nothing. (c) The 00z cron (04:10 UTC) had not started by about 08:20 UTC; the owner ran the workflow by hand and it was green. GitHub's scheduled runs can start hours late or not at all; the 24-hour catch-up recovers the missed cycles. No change in v1; adding cron times is a session 111 decision. The Node.js 20 deprecation warning is noted; no change.
- **D104.4 The runner fix.** A cycle not issued because a later cycle is already in the log is shown on the page and in the run output as now, but does not set a failing exit code. Code 3 stays for a cycle that should have issued and did not (a guard stop, or a fetch that never succeeded); code 2 for a fetch still waiting (under 12 hours old). The workflow is unchanged. The fix goes live at the next redeploy (session 111).
- **D104.5 The template.** `deploy/mlwx-live/.github/workflows/live.yml` keeps placeholders, since a commit cannot hold its own hash: the marker becomes `SET-AT-DEPLOY` and the header comment says the values are set at each deploy. The deployed values are recorded in DECISIONS (D104.2 for the first deploy). MLwx-live's copy is the deployed one; the owner copies the comment fix there at the next redeploy.
- **D104.6 The onboarding tool.** One script, `python -m mlwx.onboard`, adds an airport of D83.2's 51 to the product. Its row of `gfs_airports.csv`: station as the IEM id, grid points and weights from `data/processed/session91_pull_airports.csv` (D83.3), time zone from `data/processed/session90_airports.csv`, and correction round(7.429 x `height_diff_m` / 1000, 4) from the same file (D100.3(b)). Its tables are built by the package from the pull's extracts and the saved IEM files; its models are fitted by D103.5 unchanged. Its trackers start at b = 0 at its first live cycle (D103.6); existing tracker cells are unchanged. Gate, before any new airport is opened: the tool run on NZWN and ORD as if new reproduces their rows, their tables (F149.2) and their model files byte for byte. The remaining 39 airports are then run through it.
- **D104.7 Inclusion rule (fixed before any of the 39 airports' data is opened).** An airport is onboarded only if every one of its 184 model cells (4 cycle hours x leads 3 to 48) has at least 1,200 complete-case rows valid up to 2026-07-31. Why 1,200: it is about the smallest training set behind stage C's passing look-A year (about 1,207 rows per cell, F139.2), so every included airport has at least as much data as a setup shown to work; the 12 current airports have 1,925 to 1,956. Counts only: no value is summarised. An airport that fails is left out and listed with its smallest count. MMMX is decided by this rule, which closes D83.4. The rule does not check how rows spread over the seasons; that is accepted.
- **D104.8 No held-out year is spent.** Fitting product models computes no error. The new airports' years from 2024-08-01 stay unscored, and a later claim batch there fits its own models on earlier data, as stage C did. D82.6 and D72.2 are unchanged.
- **D104.9 Model storage.** One combined set for all onboarded airports, in `../MLwx-live-build/models-<N>/`, as one Release asset `gfs-models.tar` under a new tag `gfs-models-<N>` (N = 12 plus the airports onboarded). The 48 current files are copied, byte-identical to `gfs-models-12`'s. The new manifest SHA-256 is held as `baseline.MANIFEST_SHA256` (D98.2) and recorded in F153. The tar must be under 2 GiB. `gfs-models-12` stays as it is. The owner uploads in session 111.
- **D104.10 Plan.** Session 110: this entry; the runner fix; the template; the onboarding tool and its gate; the 39 airports; the combined models and tar; one dry run with all N airports; F153. Session 111: the owner redeploys (new commit, new tag); Claude Code checks the live runs; decisions on a pre-registered test of the live forecasts (window from 12 October 2026, handling of v17 rows, locked before any 2026-27 scoring including stage B's), an observation snapshot alongside the log, and extra cron times.
- **D104.11 Live index.** Removed (archived): F152, which is accepted. Added: D104 and F153. After session 110: D93, D103, D104, F153.

---

## 2026-10-13: Session 110 finding: the runner fix, the onboarding tool and its gate, 37 airports onboarded, the combined models and a dry run

**F153. D104 was recorded first. The runner fix and the template change were made, the onboarding tool was written and passed its gate, 37 of the 39 remaining airports were onboarded (N = 49), the combined model set and its tar were built, and one dry run was made with all 49 airports. Nothing was scored: no error, MAE or mean error at any airport (D104.8). Network only in Step 7, only to the AWS GFS archive. Full real output: `notes/session-110-output.txt`. Tool: `src/mlwx/onboard.py` (new, `7aa22e73aee1b8e9486ad7ce48e016e77d0d83e04f86cf0aefe2a6ba653c36e2`). Run 2026-10-13. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0, eccodes 2.48.0.**

- **F153.1 D104.** Recorded first, byte-equal to the prompt's block (13 lines, `diff` and `cmp`), 0 em-dashes.
- **F153.2 The runner fix (D104.4).** Before it, the tracker-order skip went into the "stopped" list and so gave exit code 3; codes 2 and 3 otherwise meant what D104.4 says. The skip is now its own outcome: still in the state's stop list, so the page shows it as before, and in the run output, but it sets no failing code. Tests through `runner.main`: last night's case (12z logged, then 18z issued and 06z listed as not issued, exit 0); a guard stop exits 3; a fetch that never succeeded exits 3; a waiting fetch exits 2.
- **F153.3 The template (D104.5).** `live.yml`'s two values and the guard's pattern are `SET-AT-DEPLOY`; the header says they are set at each deploy and recorded in DECISIONS. Still parses as YAML. The README's count is now 49 airports.
- **F153.4 The tool and its gate (D104.6).** Ported from session 109's Gate A table build. The rows come from the D104.6 sources, and the role is "claim" for the pull's "claim batch" and "new" for its "new". Tables are built from the pull folders, each checked against its inventory, and from the IEM files, each checked against its `.meta.txt`. The counts are of complete-case rows per model cell. Models are fitted only if D104.7 passes. Counting check: the 12 current airports give 1,925 to 1,956 rows (F152.5), and all 2,208 cells equal session 109's `train_rows.csv`. Gate: on NZWN and ORD as if new, the two rows were byte-equal to the current rows, the four tables equal to F149.2's SHA-256, and the eight model files byte-equal to the frozen ones.
- **F153.5 Owner's ruling at a stop (Step 4).** The 51-airport runner test failed. VILK's time zone (Asia/Kolkata, UTC+5:30) is not a whole number of hours from UTC, so `dailymax.local_day` refuses its days and the page cannot be built. That file is not in scope. Ruling (owner): VILK is left out of v1. A second fixed rule applies with D104.7: an airport is onboarded only if its time zone is a whole number of hours from UTC on every day from 2021-03-01 to 2027-12-31, checked before any of its data is opened. VILK fails it and is listed with that reason. No table or count was made for it, and `dailymax.py` was not edited. The tool applies this rule in every mode (tested). Of the 47 airports in `session90_airports.csv`, only VILK fails it.
- **F153.6 The 38 airports (D104.7 unchanged).** 76 tables (195,600 and 187,768 rows per airport, equal to the plan), 602 MB, in `../MLwx-live-build/tables/`. Counts: `data/processed/session110_onboard_counts.csv` (`7149245a287b122f51c10451cb221f0a1d264a208b9f812a17b9fa46efdaa101`), counts only. 37 pass and 1 fails: **MMMX, smallest cell 767** (60 of 184 cells under 1,200), which closes D83.4. The smallest passing airport is OPKC with 1,456; RCSS has 1,790 and FACT 1,864; the rest have 1,917 or more. **N = 49.** The 148 new model files were fitted in 315 s. OPKC was fitted again in a separate process, with identical files. The 37 rows were appended to `gfs_airports.csv`, and its first 2,705 bytes (the header and the 12 rows) are unchanged.
- **F153.7 The combined models (D104.9).** `../MLwx-live-build/models-49/` holds the 48 current files (each SHA-256 equal to `gfs-models-12`'s manifest) and the 148 new ones: 196 files, 1,248,606,063 bytes, and `manifest.txt` in the same format. **Manifest SHA-256 `484590bf6c877bb153446dc87f57c0f00270ad689066ea1791a60cea71baeea4`**, held as `baseline.MANIFEST_SHA256` and checked by a test. **Tar `../MLwx-live-build/gfs-models-49.tar`: 1,248,979,968 bytes (under 2 GiB), 198 entries, no `._` entries, SHA-256 `e30f8fb99e275fd410bcc37a41686deb26bf61ccb658cb0acbb419da9769f284`**. Extracted, it equals the folder. Nothing was uploaded.
- **F153.8 Dry run.** Cycle 2026-10-13 06z, fresh state, 49 airports, into `/tmp/mlwx-dryrun.nm4b4V` (kept). One log file of 2,254 rows (49 x 46), b = 0 everywhere, v16, the new manifest SHA-256 in every row, and the page built with 49 sections. Exit 0, run time 120 s. IEM was not called. No value was compared with an observation.
- **F153.9 Readings for the owner.** (1) D104.6 names no role for new airports; the tool writes "new". (2) With 49 airports configured, `scripts/session109_gates.py` (Gate A) and `python -m mlwx.refit` without an airport list would stop at a new airport, because they look up recorded table SHA-256 values that only the 12 have. Neither was edited (out of scope). The test of the gates script's constants now covers the 12 only. (3) The model asset grows from 306 MB to 1.25 GB, so each uncached run downloads 1.25 GB; the Actions cache is keyed by tag. (4) Once trackers have errors, each run makes one IEM request per airport (49, not 12), with a 1.5 s pause between requests. (5) OPKC (1,456), RCSS and FACT have fewer rows than the 12, though all are above D104.7's bar. (6) The new airports' years from 2024-08-01 stay unscored (D104.8). (7) MLwx-live's deployed workflow still has the old comment; the owner copies the fix at the redeploy (D104.5). (8) The workflow downloads the asset named `gfs-models.tar` (`MODELS_FILE`, D104.9), so `gfs-models-49.tar` is uploaded under that asset name, or `MODELS_FILE` is changed at the redeploy.
- **F153.10 What was not done.** No score or accuracy figure of any kind, and no retraining of the 48 current files. `dailymax.py`, `records.py`, `refit.py`, `tables.py`, the other listed modules, SPEC.md, RESULTS.md, README.md, CLAUDE.md, and the existing scripts and data files were not edited. `../MLwx-live-build/models/` and the stage C folders are unchanged. No upload, push, deploy or commit, and no commit message written.
