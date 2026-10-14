# Session 112: D106 (F154 accepted, and a fixed plan for a descriptive analysis of the stage C curve and its daily maximum), and the GFS-only analysis

Recommended model: Opus.

## Read first

- STATUS.md and SPEC section 2 (always). SPEC sections 5.2 and 9.
- DECISIONS.md, the live file, in full (this session records a decision).
- Archived entries, one at a time by line range, only when a step needs them: D82.8, D88.4, D88.7, D89.3, D97.4 to D97.7, D98.10, D100.4, D100.5, D101.2, F125.3, F147.6, F147.7, F149.2, F150.2, F150.4.
- Files, when the step that uses them starts: the docstrings, constants and the functions a step imports from `scripts/session104_curve_cv.py` and `scripts/session106_claim_look.py` (and, through them, session 97's), never the whole files unless a step needs it.

## What this session is

D106 is recorded first. It fixes, before any number is computed, what this analysis looks at and how. Then the session regenerates the stage C predictions at the 12 airports of D103.4 on spent data, checks that they reproduce the record exactly, and runs the GFS-only analysis that D106 sets out, with the daily maximum as its main section. It writes `ANALYSIS.md` (a draft field guide, then an appendix with every planned statistic), figures and tables, and F155.

Everything is descriptive (D106.2). No verdict, model, setting, rule, bar or table changes. Stage C's look is not run again: the look script's `--look` mode is never called (D101.2); the claim airports' frozen models are refitted by the look's route only to regenerate predictions already scored. No value valid on or after 2026-08-01 is scored. Nothing from the 37 airports of F153.6 is read.

Network: Step 0's `pip install matplotlib` into `.venv` (owner's ruling after the first run stopped at Step 0) and Step 9 (one public file from MLwx-live). Everything else is offline. Nothing else is installed.

Write a checkpoint line to `notes/session-112-output.txt` after each step (D93.11). Stop rather than work around a failed check. Scripts print short summaries; full tables go to files (D93.12).

## Scope: the only files this session may create or edit

- `DECISIONS.md`, `DECISIONS-archive.md`, `STATUS.md`
- `scripts/session112_analysis.py` (new)
- `ANALYSIS.md` (new, at the repo root)
- `figures/analysis/` (new folder and files)
- `data/processed/session112_analysis/` (new folder and files)
- `notes/session-112-output.txt` (it exists from the first run, which stopped at Step 0; keep its content and add to it)
- `requirements.txt` (one added line: matplotlib at the exact installed version)
- `.venv/` (the matplotlib install and its dependencies only)
- Outside the repo: a new folder `analysis112/` inside session 97's `STAGEC_DIR`, for the regenerated predictions, and a temporary folder for Step 9's download.

Everything else is out of scope, including SPEC.md, RESULTS.md, README.md, CLAUDE.md, `docs/PROJECT-INSTRUCTIONS.md`, `figures/README` files if any, every existing script (frozen or not), every existing table and data file, every model folder, `src/mlwx/` and `tests/`. Anything worth changing there is reported as an open item.

## Steps

### Step 0: Preflight

- `git status` is clean apart from this session file and `notes/session-112-output.txt`. HEAD is session 111's commit, `d6ca3e4e9bd79d55ffbdfd1cc7a9a5d6e21747bb`.
- The Live index lists D93, D103, D105 and F154. No D106 or F155 exists in either DECISIONS file. None of this session's new paths exists, except `notes/session-112-output.txt` from the first run, which stopped at Step 0 because matplotlib was not installed. Keep that file; add a line saying this is the second run, after the owner's ruling.
- `scripts/session104_curve_cv.py`'s SHA-256 equals F147's (the constant in `session106_claim_look.py`), and `scripts/session106_claim_look.py`'s equals F149's (F150.4).
- `session104_curve_cv_scores.csv` and `session104_dailymax_days.csv` equal F147.7's SHA-256; the three `session107_claim_*.csv` files equal F150.4's.
- The 12 development tables (hours 0 to 24 and 25 to 48) and the 12 claim tables equal the SHA-256 values those scripts hold.
- `numpy` and `lightgbm` import, at the versions the record uses (2.5.2 and 4.7.0).
- Owner's ruling: install matplotlib into the project's `.venv` with `.venv/bin/python -m pip install matplotlib`. Then check that numpy and lightgbm are still 2.5.2 and 4.7.0 (stop if pip changed either), that `import matplotlib` works with the `Agg` backend, and record matplotlib's version and every package pip added in the output file. Add one line to `requirements.txt`: `matplotlib==<installed version>`. If the install fails, stop.
- Record DECISIONS.md's byte size.

Stop if any check fails.

### Step 1: Record D106

Append the block below to DECISIONS.md, byte-equal (copy it with `sed` from this file, then check with `diff` and `cmp`), and add D106 to the Live index. Count em-dashes in the block: must be 0.

~~~markdown
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
~~~

Stop if the block is not byte-equal.

### Step 2: Regenerate the predictions, and the reproduction gates

Write `scripts/session112_analysis.py`. Import, read only, from session 104 and session 106 (and through them session 97); never call session 106's `--look`, never write a `session107_*` file. Write new code only where no function exists, and say which in the checkpoint.

- **Development airports (D106.3).** Refit by F147's route, all three folds, all cycle hours, leads 3 to 48, with the tracker. Keep per row: station, fold, cycle, cycle hour, lead, valid time, local date and hour, the observation, raw GFS, the baseline, b, the curve, and the features.
- **Claim airports (D106.3).** Refit by F150's route (frozen fit before 2024-08-01, tracker from 2024-08-01 through both looks), with the same columns and the look in place of the fold.
- **Gate D (development).** Every cell's n and MAE for raw GFS, the baseline and the curve equal `session104_curve_cv_scores.csv` at full precision; every day's cycle and observed, raw GFS and curve maxima equal `session104_dailymax_days.csv`.
- **Gate C (claim).** Every n and MAE in `session107_claim_scores.csv` and every day's cycle and maxima in `session107_claim_days.csv` equal, at full precision.

Stop if either gate differs anywhere. Then write the predictions, gzipped, to `analysis112/` outside the repo, with a meta file (row counts, columns, SHA-256 per file, run time, versions), and print only counts.

### Step 3: The references (D106.4)

Build climatology, constant bias and linear MOS from each fold's or look's own training rows only, and persistence by D100.5. Checks: every reference row's training data is valid before its fold's or look's T0; linear MOS uses exactly the baseline's training rows per cell (count equal); no reference has a missing value on a scored row without it being counted. Write the tercile and decile edges (D106.5, D106.6) to `data/processed/session112_analysis/bin_edges.csv` before any test error is computed, and record its SHA-256 in the checkpoint.

### Step 4: Self-checks

A `--check` mode, run on synthetic data only: the bootstrap reproduces a known mean's interval width within tolerance; Diebold-Mariano gives p about 0.5 to 1 on two identical-error series and p below 0.01 on a series with a large constant gap; Benjamini-Hochberg matches a hand-worked example; the D106.7(d) decomposition sums to e_max exactly on a made-up curve; the peak-hour and edge-of-day rules handle ties (first hour wins) and a 23-hour or 25-hour local day if the time zone has one. Stop on any failure.

### Step 5: The hourly analysis (D106.5, D106.6, D106.9, D106.11)

For every forecast of D106.4, per airport and fold or look, and per breakdown: the D106.5 metrics, with D106.12's intervals. Figures (SVG, in `figures/analysis/`, small multiples per airport where it helps): error box plots and ECDFs; MAE and mean error by lead, local hour and month; conditional bias; the regime terciles with intervals; drift by days since start, and b over time. Noise floor and the sea-grid split as D106.11.

### Step 6: The daily maximum (D106.7)

All of D106.7 (a) to (g), with D106.12's intervals. Figures at least: error box plots and histograms per airport; error by day 1 or 2 and cycle hour; extremes; the decomposition (peak level and timing) per airport; peak-hour error histograms; edge-of-day counts and errors; the ranges as a table and a fan-style figure, including the hourly ranges against each single lead per airport.

### Step 7: Curve shape, consistency and model internals (D106.8, D106.10)

Diurnal range and peak hour; smoothness; run-to-run change for the curve and the maximum. Feature-contribution shares per airport and lead, and the two contribution plots.

### Step 8: The formal tests (D106.12)

The four families, per airport, with each p-value, the Benjamini-Hochberg result, and the mean daily difference with its interval. Write them to `data/processed/session112_analysis/dm_tests.csv`.

### Step 9: The ZUCK case (D106.13)

Download only `https://raw.githubusercontent.com/zadams03/MLwx-live/main/log/2026/10/gfs_2026101306.csv` into a temporary folder; record its SHA-256 and byte size. Read only ZUCK's rows and only the forecast columns (cycle, lead, valid time, raw GFS, baseline, b, corrected). Plot raw GFS and the curve with the local days (Asia/Chongqing) shaded, mark each day's maximum and its hour, and put beside it the spent-data edge-of-day figures from Step 6. Nothing under `obs/` is opened; no error is computed. If the download fails, record it and go on: this step is not a stop condition.

### Step 10: ANALYSIS.md

Plain words, jargon defined once, no em-dashes.

- **Part 1, the draft field guide** (about two pages). How to read a number on the page: typical ranges for the hourly curve and for the daily maximum by airport, season, lead or day ahead; when to trust it less (the regimes that matter most); what the correction does compared with raw GFS, constant bias and linear MOS; what limits the accuracy. Claim airports first. Numbers, not adjectives, each citing its appendix table or figure. Marked "draft: the owner chooses what goes first".
- **Part 2, the appendix.** Every statistic and figure of D106.5 to D106.13, in D106's order, each with a one-line note on how to read it. Development airports' figures carry D106.3's flag.
- **Part 3, candidates for later.** Each with its evidence and the build-choice test (D89) it would need. Nothing is changed.
- A short header with D106.2's status statement and where the files are.

### Step 11: F155

Record F155 (at most about 40 lines, D93.10): what was done; both gates; the headline per airport for the curve and the daily maximum against raw GFS, linear MOS and the baseline, claim airports first; the maximum's decomposition in one line per airport group; the formal tests' outcome per family (how many airports pass Benjamini-Hochberg); readings for the owner (anything surprising, anything that disagrees with F147 or F150's descriptive figures, and any choice the plan left open that the session had to make); what was not done; pointers to the output file, ANALYSIS.md and the predictions' meta file.

## End of session

As CLAUDE.md, with:

- STATUS.md overwritten as a current-only snapshot. Its last line: "**Next planning session:** Review session 112 and commit; then plan session 113 (D106.15): the read-only probe and pull of comparison forecasts on spent years, and the official daily maximum at the four US airports. The owner's WeatherNext access request is pending."
- The archive step with D106.16's Live index, `--citations`, DECISIONS.md's byte size, and the scope-list check against this file's scope.
- `notes/session-112-output.txt` begins with the summary of at most 30 lines, then the checkpoints and full detail.

Do not commit anything. Stop and wait for review.
