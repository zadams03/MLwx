# Session 114: D108 (F156 accepted, IFS deferred to the owner's hand pull, the open comparison choices fixed before any score), the comparisons, and the field guide

Recommended model: Opus.

## Read first

- STATUS.md and SPEC section 2 (always). SPEC sections 3.4 and 5.2 (positions; the elevation adjustment and its lapse rate).
- DECISIONS.md, the live file, in full (this session records a decision and scores).
- Archived entries, one at a time by line range, only when a step needs them: D82.8, D98.10, D89.3, D100.4, F125.3, D77.7, F127.7.
- `ANALYSIS.md` in full (Step 7 rewrites Part 1 and adds to Part 2).
- Files, when the step that uses them starts, docstrings and the functions used only: `scripts/session112_analysis.py` (loaders, bootstrap, Diebold-Mariano, Benjamini-Hochberg, plotting helpers), `scripts/session113_comparison_pull.py` (column definitions, guards, `f_to_c`, the climate-day window), and in `data/processed/session113/`: every `*_meta.txt`, `probe.csv`, `latency.csv`, `nbs_runs.csv`, the gap files and the positions files.

## What this session is

D108 is recorded first. It accepts F156 and confirms the owner's rulings made during session 113, records the owner's D107.7 override for an IFS pull he runs by hand later, and fixes the comparison choices D107.9 left open, before any competitor value is scored. Then the session compares the curve with AIFS, the NBM grid, NBS and MAV on spent years under D107.9 and D108, measures the official daily maximum's gap from our hourly-report maximum, and rewrites `ANALYSIS.md`'s field guide in the order of D108.6.

Descriptive only (D107.2): no verdict, model, setting, rule, bar or table changes, and nothing is selected or tuned on these results. Nothing valid after 2026-07-31T23:00 UTC is read. Nothing from the 37 airports of F153.6 is read. No IFS value exists yet and none is read. Network: only the NBM text documentation pages of D108.4(c); nothing is installed; if a needed package is missing, stop. For long runs follow D86.5.

Write a checkpoint line to `notes/session-114-output.txt` after each step (D93.11). Stop rather than work around a failed check. Scripts print short summaries; full tables go to files (D93.12).

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`, `ANALYSIS.md`
- `scripts/session114_comparisons.py` (new)
- `data/processed/session114_comparisons/` (new folder and files)
- `figures/analysis/`: new files only, each named `comparison_*.svg`
- `notes/session-114-output.txt` (new)

Everything else is out of scope, including SPEC.md, RESULTS.md, README.md, CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, every existing script, every existing file in `data/processed/` (including `session113/` and `session112_analysis/`, read only), every existing figure, the files in `../MLwx-stagec/` (read only), every model folder, `src/mlwx/`, `tests/` and `requirements.txt`. Anything worth changing there is reported as an open item.

## Steps

### Step 0: Preflight

- `git status` is clean apart from this session file. HEAD is session 113's commit (its title is the first line of `docs/commits/commit-113.txt`).
- The Live index lists D93, D103, D105, D106, D107 and F156. No D108 or F157 exists in either DECISIONS file. None of this session's new paths exists.
- Every file this session reads from `data/processed/session113/` and from `../MLwx-stagec/analysis112/` matches the SHA-256 in its meta file. Stop on any mismatch.
- `numpy`, `lightgbm` and `matplotlib` import; record their versions. Record DECISIONS.md's byte size.

Stop if any check fails.

### Step 1: Record D108

Append the block below to DECISIONS.md, byte-equal (copy it with `sed` from this file, then check with `diff` and `cmp`), and add D108 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
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
~~~

Stop if the block is not byte-equal.

### Step 2: The script, its gates and self-checks

Write `scripts/session114_comparisons.py` with modes `--check`, `--gate`, `--match`, `--hourly`, `--dailymax`, `--official`, `--docs` and `--figures`, and a `--source` argument that takes `aifs`, `nbm`, `nbs`, `mav` and also `ifs` (session 115 runs it unchanged). Import, read only, from sessions 112 and 113; write new code only where no function exists, and say which in the checkpoint.

- `--check` (synthetic, no real value): pairing by valid time, including NBS's one-hour-later runs; the local-day and local-standard-time-day windows in summer and winter; the maximum-window choice of D108.4(b) on made-up runs at each cycle hour; the elevation formula's sign and size; F to C exact; the guard refusing any valid time after 2026-07-31T23:00 UTC; Benjamini-Hochberg on a made-up p-value list.
- `--gate` (real data, no competitor value): (1) the loader reproduces session 112's curve and raw GFS figures exactly, n and MAE, hourly and daily maximum, at 12 of 12 airports (`hourly_headline.csv`, `dailymax_headline.csv`); (2) the bootstrap and Diebold-Mariano functions, run with seed 112, reproduce `dm_tests.csv`'s family 1 row at one claim and one development airport exactly; (3) the elevation formula applied to GFS's own recorded height difference reproduces the record's elevation constant at 12 of 12 airports to the record's rounding (stop if any airport has no station elevation or constant).

Stop if any check or gate fails.

### Step 3: Matching (`--match`, D108.4(a) and (b))

Per source and airport: paired hourly rows and paired days (D98.10's days and every cycle), by test year and cycle hour, against what the coverage of F156.4 allows; rows and days without a pair counted by reason. The TXN windows per NBM version (Step 6 fills the documentation part; until then labelled "pending"). No error is computed. Write `match_counts.csv`. Stop if any source has no pairs at an airport where F156.4 shows coverage.

### Step 4: Hourly comparisons (`--hourly --source <s>`, each of aifs, nbm, nbs, mav)

On the paired rows: MAE, mean error, RMSE and skill of the curve against the competitor, and the same for raw GFS against the competitor; by lead band, cycle hour and season, and by version segment (descriptive). Intervals and tests as D107.9(e) and D108.4(e): seed 114, 10,000 resamples for each airport and test year's headline figures, 2,000 for breakdown cells; one Diebold-Mariano family per source, Benjamini-Hochberg across its airports. Latency beside (D108.4(f)). Tables to `data/processed/session114_comparisons/hourly_<source>*.csv`.

### Step 5: Daily maximum comparisons (`--dailymax --source <s>`)

As D107.9(c) and D108.4(b): the curve's D98.10 maximum and its maximum sampled at the competitor's steps; the competitor's own maximum field (or its steps, labelled); raw GFS's beside. Truth: our hourly-report maximum (D82.8). D98.10's days primary with the family test; every cycle by cycle hour descriptive. Same metrics, intervals and labels as Step 4. Tables to `dailymax_<source>*.csv`.

### Step 6: The official maximum (`--docs`, then `--official`)

`--docs`: read the NBM text documentation for each NBM version inside the window (documentation pages only); record each version's TXN window and its source URL in `txn_windows.csv`; update Step 3's labels.

`--official` (D108.4(d)): at KDSM, KRNO, KSFO and KORD, the gap of CLI's maximum from our hourly-report maximum (civil local day, and local standard time day); then the curve's, NBM's (TMAX and its steps), NBS's and MAV's maxima scored against CLI, by test year, with NBS's version labels; everything again on the CLI and GHCN agreement days. Descriptive only. Tables to `official_*.csv`.

### Step 7: Figures and `ANALYSIS.md` (`--figures`)

- At most 6 new figures, each `figures/analysis/comparison_*.svg`, in session 112's style: hourly MAE per airport (curve, raw GFS, each competitor); daily maximum MAE per airport; MAE by lead band, curve against AIFS and NBM; the official-maximum gap.
- `ANALYSIS.md`: update the status paragraph to cover D107 and D108. Rewrite Part 1 in D108.6's order, using F155's tables and this session's; every number in Part 1 is checked against its table file by a script (mismatches: 0), and Part 1 is checked to hold no em-dash. Add a Part 2 section "D107.9 and D108: comparisons (session 114)" with every table of Steps 3 to 6 (claim airports first, development airports flagged, IFS marked pending), and move model internals and drift by days since start under Part 2 only. Part 3 may gain candidates, each with its evidence and the line "seen after the comparisons; any test is a D89 build choice".

### Step 8: F157

Record F157 (at most about 40 lines, D93.10): D108 recorded; the self-checks and gates; per source the paired rows and days by airport and test year (claim airports first); the hourly and daily-maximum results (MAE, skill and intervals in ranges across airports, each family's Benjamini-Hochberg outcome); the official-maximum gap and the scores against CLI, with the agreement-day check; the TXN windows found; readings for the owner (anything the plan left open that the session had to decide, anything that blocks session 115); what was not done (IFS); pointers.

## End of session

As CLAUDE.md, with:

- STATUS.md overwritten as a current-only snapshot. Its last line: "**Next planning session:** Review session 114 and commit. Then the owner runs the IFS pull by hand (D108.2) when the laptop can stay on power and wifi, and the next planning chat plans session 115 (D108.7): the IFS comparisons and the field guide's IFS lines."
- The archive step with D108.8's Live index, `--citations`, DECISIONS.md's byte size, and the scope-list check against this file's scope.
- `notes/session-114-output.txt` begins with the summary of at most 30 lines, then the checkpoints and full detail, including the end-of-session consistency checks.

Do not commit anything. Stop and wait for review.
