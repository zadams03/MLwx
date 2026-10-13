# Session 110: D104, the runner fix, and onboarding the other 39 airports

## Read first

- STATUS.md and SPEC section 2 (always).
- The live DECISIONS.md in full (D93, D103, F152).
- Archived, one entry at a time by `grep -n` (CLAUDE.md): D82.6, D83.2 to D83.4, D100.3, F139.2, F149.2.
- `src/mlwx/`: `runner.py`, `state.py`, `baseline.py`, `refit.py`, `tables.py`, `records.py` and `data/gfs_airports.csv` in full; other modules only as a step needs.
- `deploy/mlwx-live/` (all four files).
- The header row and two data rows of `data/processed/session90_airports.csv` and `data/processed/session91_pull_airports.csv`.

## Scope

May create or edit only:
- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `src/mlwx/runner.py`, `src/mlwx/page.py` (only if Step 2 needs it), `src/mlwx/baseline.py` (manifest constant only), `src/mlwx/data/gfs_airports.csv`
- `src/mlwx/onboard.py` (new)
- `tests/test_live.py`, `tests/test_onboard.py` (new)
- `deploy/mlwx-live/.github/workflows/live.yml`, `deploy/mlwx-live/README.md`
- `data/processed/session110_onboard_counts.csv` and its `.meta.txt`
- `notes/session-110-output.txt`
- Outside the repo: `../MLwx-live-build/tables/`, `../MLwx-live-build/models-<N>/`, `../MLwx-live-build/gfs-models-<N>.tar`, and one temporary dry-run folder under `/tmp`.

`src/mlwx/` modules not listed (`tables`, `refit`, `features`, `tracker`, `dailymax`, `gfs`, `observations`, `state`, `prediction_log`, `config`) are not edited. If onboarding needs a change in one of them, stop and report (D93.11). `../MLwx-live-build/models/` and the stage C folders are read only.

No error, MAE or mean error of any value is computed or printed at any airport (D103.2, D104.8). Network only in Step 7, only to the AWS GFS archive and IEM.

## Steps

Write a checkpoint line into the output file after each step (D93.11).

### Step 0: state check

`git status --porcelain` shows only `?? docs/sessions/session-110.md`. No D104 or F153 exists in either DECISIONS file. None of the new paths exist. `../MLwx-live-build/models/manifest.txt` has SHA-256 equal to `baseline.MANIFEST_SHA256` (F152.5). Stop on any difference.

### Step 1: record D104

Copy the D104 block below (from its `---` line to the end of D104.11) with `sed` to the bottom of DECISIONS.md, under a heading `## 2026-10-13: Session 110 decision: F152 accepted, the deployment, the runner fix, and onboarding (owner, planning chat)`. Check byte-equal with `diff` and `cmp` before any other edit (CLAUDE.md).

### Step 2: the runner fix (D104.4)

1. Read `runner.py` and list every per-cycle outcome and which exit code it feeds. **Stop and report** if the tracker-order skip does not feed code 3, or if codes 2 and 3 mean anything other than D104.4 says.
2. Make the tracker-order skip its own outcome: shown on the page and in the run output as now, not counted for the exit code.
3. Tests in `tests/test_live.py`: (a) last night's case offline: 12z logged, 06z in the window, 18z new, expect 18z issued, 06z listed as skipped, exit 0; (b) a guard stop still gives 3; (c) a waiting fetch still gives 2.
4. The whole test suite passes.

### Step 3: the template (D104.5)

In `deploy/mlwx-live/.github/workflows/live.yml`: the two placeholder values and the guard's pattern become `SET-AT-DEPLOY`; the header comment says the two values are set at each deploy and the deployed values are recorded in DECISIONS; nothing else changes. Update any airport count or session reference in `deploy/mlwx-live/README.md`. The file still parses as YAML.

### Step 4: the onboarding tool and its gate (D104.6)

1. Write `src/mlwx/onboard.py` (`python -m mlwx.onboard`), built on the package's own table and refit code. For one airport it: makes its `gfs_airports.csv` row (D104.6 sources), builds its two tables, counts complete-case rows per model cell, and, only if it passes D104.7, fits its four model files.
2. Counting check: the count at the 12 current airports gives a minimum of 1,925 and a maximum of 1,956 over all cells (F152.5). Stop on any difference.
3. **Gate.** Run the tool on NZWN and ORD as if new, into a temporary folder. Pass only if all of these are byte-equal: the generated rows to the current rows in `gfs_airports.csv`; the four tables to F149.2's SHA-256 values; the eight model files to the frozen files of the same names in `../MLwx-live-build/models/`. Stop on any difference; no new airport is opened before this passes.
4. Tests in `tests/test_onboard.py`, including: a state file holding only the 12 current airports, read with 51 airports configured, keeps every existing cell unchanged and starts each new cell at b = 0 (D103.6).

### Step 5: the 39 airports (D104.6, D104.7)

1. Build the tables for the 39 airports into `../MLwx-live-build/tables/` and write `data/processed/session110_onboard_counts.csv` (per airport: smallest and largest cell count, cells below 1,200, pass or fail) with a `.meta.txt`. Counts only.
2. Apply D104.7 unchanged. List every airport that fails, with its smallest cell count. N = 12 + the number that pass.
3. Fit the passing airports' models. Fit one new airport twice in separate processes: identical, or stop.
4. Add the passing airports' rows to `gfs_airports.csv` (the 12 existing rows unchanged, byte for byte).

### Step 6: the combined models (D104.9)

1. Make `../MLwx-live-build/models-<N>/`: the 48 current files copied, each SHA-256 equal to the original, plus the new files and a new `manifest.txt` in the same format.
2. Put the new manifest SHA-256 in `baseline.MANIFEST_SHA256`, with its test (D98.2).
3. Make `../MLwx-live-build/gfs-models-<N>.tar` of the folder with no `._` entries (`COPYFILE_DISABLE=1`). Report its size, entry count and SHA-256. Stop if it is 2 GiB or more.

### Step 7: dry run

Run the runner on the latest available cycle, fresh state, all N airports, into a new `/tmp` folder (as F152.9). Report: one log file, rows equal to N x 46, b = 0 everywhere, v16, the page built with N sections, and the run time. No value is compared with an observation.

### Step 8: F153

Record F153 (at most about 40 lines, D93.10): the D104 copy check, the runner fix and its tests, the template change, the gate, the counts summary and the airports left out (MMMX's count named), N, the new manifest SHA-256, the tar's size and SHA-256, the dry run, readings for the owner, and what was not done.

## End of session

CLAUDE.md's end steps, with these specifics:
- STATUS.md: stage G v1 deployed with 12 airports; N airports onboarded and ready; the runner fix not yet live. Its "Next planning session" line: Review session 110 and commit; then plan session 111: the owner uploads `gfs-models-<N>.tar` under tag `gfs-models-<N>`, sets `MLWX_COMMIT` to session 110's commit and `MODELS_TAG` in MLwx-live's workflow and copies the template's comment fix; Claude Code checks the live runs; decide a pre-registered test of the live forecasts (window from 12 October 2026, handling of v17 rows, locked before any 2026-27 scoring including stage B's), whether to save an observation snapshot alongside the log, and whether to add cron times.
- Live index as D104.11.
- The output file's summary also gives the full list of airports onboarded and left out.
- Do not commit; do not write a commit message.

---

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
