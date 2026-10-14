# Session 111: D105 (F153 accepted, the redeploy, a pre-registered test of the live forecasts, the observation snapshot), the live-run check, the snapshot, and the refit and Gate A fix

Recommended model: Opus.

## Read first

- STATUS.md and SPEC section 2 (always).
- DECISIONS.md, the live file, in full (this session records a decision).
- Archived entries, one at a time by line range, only when a step needs them: D98.10, D100.5, F152.7, F152.8.
- Files, when the step that uses them starts: `src/mlwx/runner.py`, `src/mlwx/observations.py`, `src/mlwx/prediction_log.py`, `src/mlwx/refit.py`, `src/mlwx/records.py`, `src/mlwx/onboard.py` (only what Step 5 needs), `scripts/session109_gates.py`, `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`.

## What this session is

D105 is recorded first. Then: a read-only check of the live repo's runs; the observation snapshot in the runner, with a dry run that re-issues one real cycle; the refit and Gate A fix (F153.9(2)); the template brought in line with the deployed workflow; F154 and the records.

Nothing is scored. No value on or after 2026-08-01 is compared with an observation, and no error, MAE, mean error, b summary or corrected-minus-baseline figure is computed or printed for any live row (D103.2, D105.5). No model is refitted except Step 5's two gate airports, into a temporary folder. Nothing is pushed to MLwx-live or uploaded.

Network: only Step 2 (a read-only `git clone` of the public `https://github.com/zadams03/MLwx-live`) and Step 4 (the AWS GFS archive and IEM, through the runner).

Write a checkpoint line to `notes/session-111-output.txt` after each step (D93.11). Stop rather than work around a failed check.

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `src/mlwx/runner.py`, `src/mlwx/prediction_log.py` (only if Step 3 reuses its write-once helper), `src/mlwx/refit.py`, `src/mlwx/records.py`
- `scripts/session109_gates.py`
- `tests/test_live.py`, `tests/test_onboard.py`
- `data/processed/session111_new_tables.csv` and its `.meta.txt` (new)
- `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`
- `notes/session-111-output.txt` (new)

Temporary folders outside the repo (the clone, the dry run, the gate refit) are allowed and are kept, not deleted. Everything else is out of scope, including SPEC.md, RESULTS.md, README.md, CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, `page.py`, `dailymax.py`, `tracker.py`, `observations.py`, `onboard.py`, every model folder and every stage C folder.

## Steps

### Step 0: Preflight

`git status` is clean apart from this session file. HEAD is `e37c86d75d8a5f79c3abc236ca7caae0b9fb17c5`. The full test suite passes (172 tests). The Live index lists D93, D103, D104 and F153. Record DECISIONS.md's byte size.

Stop if any check fails.

### Step 1: Record D105

Append the block below to DECISIONS.md, byte-equal (check with `diff` and `cmp` against a copy taken from this file), and add D105 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
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
~~~

### Step 2: The live-run check (read-only, D105.3)

Clone `https://github.com/zadams03/MLwx-live` into a new temporary folder outside the repo. Never commit, push or edit there. Report in the output file, with a short summary in the checkpoint:

1. **History.** The number of commits. `git log --diff-filter=MD --name-only -- log` lists nothing: every log file was added once and never modified or deleted. `obs/` does not exist yet.
2. **Each log file:** cycle, row count, airport count, leads 3 to 48 complete for every airport, and the distinct values of `gfs_version`, `model_sha256`, `code_commit` and the issue time.
   - Expected: files up to and including the last 12-airport cycle have 552 rows, the 12 airports of D103.4, manifest `16485f384c81094247ec745550ad04982e8c3adb255147546bf1190f498641ef` and commit `0f89f0157ded0e26e12c3985ff80dd5eb504d197`. Every later file has 2,254 rows, the 49 airports of `gfs_airports.csv`, manifest `484590bf6c877bb153446dc87f57c0f00270ad689066ea1791a60cea71baeea4` and commit `e37c86d75d8a5f79c3abc236ca7caae0b9fb17c5`. Every row is v16.
   - Name the first 49-airport cycle (D105.5(d)).
3. **Coverage:** every cycle from 2026-10-12 12z to the newest logged one, marked logged or not, with the state file's reason for any not logged.
4. **Issue lag** per cycle (issue time minus cycle), as a table.
5. **The state file:** the airports and cycle hours it holds cells for, and its stop list. Print no b value or summary of b.

Stop and report if item 1 lists anything, or any row differs from item 2's expectation in airport set, row count, manifest or commit. Do not compare any value with an observation, and do not summarise `b`, `corrected` or `baseline`.

### Step 3: The observation snapshot (D105.7)

Implement it in `runner.py`, reusing `prediction_log.py`'s write-once helper if it fits (the only reason to edit that file). The snapshot holds exactly the (airport, valid time) pairs that `bring_trackers_up` looked up for the cycle, with the value and report time `ReportSet.nearest` gave. Read `observations.py` for what `nearest` returns; do not edit it.

Tests in `tests/test_live.py`, through `runner.run` with fake fetches:
- the snapshot's rows equal the pairs used and their values;
- a cycle with no lookups gives a header-only file;
- the log file is byte-identical whether the snapshot write succeeds or is forced to fail, and a failure is printed and does not change the exit code;
- an existing snapshot file is never overwritten.

Check: the full suite passes. Report the test count.

### Step 4: Dry run that re-issues one real cycle (D105.7)

In the Step 2 clone, find the newest commit that added exactly one log file. Take that cycle C, and copy `log/` and `state/` from the commit's parent into a new temporary folder. Run:

`python -m mlwx.runner --root <tmp> --models ../MLwx-live-build/models-49 --now <C + 4 h 10 min> --latest-only --commit session111-dryrun`

Checks, and the stop condition:
- Exactly cycle C is issued. Report the number of IEM requests and errors applied (counts only).
- Every row of the dry-run log file has `raw_gfs` and `baseline` equal, as text, to the live file for C. Stop if any differs.
- For `b` and `corrected`, report only the number of rows that differ from the live file. A late IEM report can change a pairing, so a nonzero count is a reading, not a stop.
- The snapshot file exists, with D105.7's columns in that order. Report its row count, airport count, and rows with an empty `obs_c`. Print no observed value.

### Step 5: The refit and Gate A (D105.8)

1. Compute the SHA-256 of the 74 tables of the 37 airports in `../MLwx-live-build/tables/`. If `notes/session-110-output.txt` lists them, check that they are equal. Write `data/processed/session111_new_tables.csv` (`airport`, `hour_set`, `file`, `sha256`) and a `.meta.txt` in the project's usual form.
2. **Gate, before any record is written into `records.py`:** with the new code, refit OPKC and RCSS from those tables into a new temporary folder. Every model file must be byte-equal to the same file in `../MLwx-live-build/models-49/`. Stop if any differs.
3. Hold the CSV's SHA-256 as a constant in `records.py`, with a test. Make `mlwx.refit` take the new airports' table folder as its own argument and check each new table against the CSV. Add a check-only path (or test) showing that a 49-airport refit's table checks all pass, without fitting.
4. Make Gate A in `scripts/session109_gates.py` default to the 12 airports with stage C tables.

Check: the full suite passes. Report the new SHA-256 of `refit.py`, `records.py` and `scripts/session109_gates.py`.

### Step 6: The template (D105.9)

Edit `deploy/mlwx-live/.github/workflows/live.yml` to match the clone's `.github/workflows/live.yml` (the deployed one), with three differences only:
- the two values are `SET-AT-DEPLOY`;
- the commit step's `git add log state` becomes `git add log state obs`;
- header item 5 names the observation snapshot.

Update `deploy/mlwx-live/README.md` to match: hourly schedule, the snapshot, failing only on code 3.

Checks: the YAML parses. `diff` against the deployed file shows only those three changes; report the diff in the output file.

### Step 7: Records

- **F154** (at most about 40 lines, D93.10): what was done, the numbers above, readings for the owner, what was not done, and a pointer to the output file. Add it to the Live index.
- **STATUS.md:** a current-only snapshot. Its last line is the "Next planning session" line, saying:
  - the owner's redeploy (D105.9): `MLWX_COMMIT` set to session 111's commit, and the template's commit line copied;
  - then a dedicated planning chat on deeper statistics of the current models (D105.10).
- **Archive:** run `scripts/archive_decisions.py` per the Live index (D104 and F153 move). Check that every citation still resolves. Report DECISIONS.md's byte size; it must be under 80,000.

## End of session

Do CLAUDE.md's end-of-session steps. Write the consistency-check findings and the scope check (`git status` against the scope list above) into `notes/session-111-output.txt`, under a summary of at most 30 lines. Then stop and wait for review. Do not commit, and do not write a commit message.
