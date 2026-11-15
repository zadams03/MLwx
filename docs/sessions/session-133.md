# Session 133: stage H's first build choice, a central 80 % range for each forecast

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
Stage H is opened on GFS. This session records D128, then compares
candidate range methods on the six development airports by a rule fixed
in D128 before any value is computed, and picks one method per output.
Build-choice scores only, never results (SPEC 2.5). No model, product,
live file or record of any earlier result changes. Offline. Recommended
model: Opus.

## Read first

- STATUS.md in full; SPEC 2.5, 6 (stage H's bullet) and 9; the live
  DECISIONS.md in full.
- Archived, by line range: D88.4, D88.7, D89.3, D89.5, D89.6, D95.2,
  D97.5 to D97.7, D98.10, D106.12, F125.3, F148 (its opening only),
  D121.2, D125.4, D125.9.
- `scripts/session97_stagec_cv.py`: the docstring, the module constants,
  `fold_role`, `fit_predict` and the table loaders.
- `scripts/session104_curve_cv.py`: the docstring, the module constants,
  `load_table25`, `score_part` and `split_rows_leads`.
- `scripts/session112_analysis.py`: `SEED`, `BLOCK`, `block_weights`,
  `BANDS`, `SEASON_OF`, `SEASONS`, and how `--regen` wrote the
  prediction files.
- `../MLwx-stagec/analysis112/meta.txt` in full; the header line of
  `data/processed/session104_dailymax_days.csv`.

## Rules for this session

- **Writes:** only the scope list below, and temporary folders under
  `$TMPDIR` (kept, paths printed). Nothing is written under `src/`,
  `deploy/`, `figures/`, `../MLwx-stagec/` or any other MLwx-all folder.
- **Network:** none. Before running a mode, read the code path it runs
  (including what it imports from sessions 97, 104 and 112) and confirm
  it makes no network call and writes only where it should; note this
  in the checkpoint.
- **Imported scripts are never edited.** `session97_stagec_cv.py`,
  `session104_curve_cv.py` and `session112_analysis.py` are imported
  read-only, each after its SHA-256 is checked equal to HEAD's blob
  (D116.10). Use their loaders and constants; do not copy and change
  their code. A wrapper may set a module constant at run time; it never
  changes a function.
- **Spent data and development airports only.** Nothing valid after
  2026-07-31T23:00 UTC is read or used; no 2026-27 value; nothing from
  MLwx-live's log, `obs/` or page; no prediction file or table of the
  six claim airports or the 37 other live airports is opened.
- **Stop rules.** Any failed check or gate stops the session at that
  step; report and wait. Do not work around it. D128.8's own stop (the
  first candidate fails coverage) is reported as a finding, not fixed.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
scripts/session133_ranges.py, scripts/README.md,
tests/test_session133.py, tests/README.md,
data/processed/session133_ranges/ (new folder),
notes/session-133-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `38cf1b7` (title starts "Session
132:"); the tree is clean apart from this prompt. Tests:
`.venv/bin/python -m unittest discover -s tests`, all OK (STATUS says
409, 1 skipped; report the count). SHA-256 at HEAD:
`session97_stagec_cv.py` `987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91`,
`session104_curve_cv.py` `6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb`,
`session112_analysis.py` `bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab`.
The six development airports' prediction files equal `meta.txt`'s
SHA-256; `data/processed/session104_dailymax_days.csv` is unchanged from
HEAD; the development tables session 104 reads match its meta hashes.
Stop if any check fails.

**Step 2. Record D128.** Append the block below to DECISIONS.md with
`sed`, exactly, after its last line with one blank line before the
heading, and check it byte-equal by `diff` and `cmp`; 0 em-dashes.

```
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
```

**Step 3. The script and its gate.** Write `scripts/session133_ranges.py`
with modes `--gate` and `--score`. `--gate`: (a) with the script's own
training-row loader, refit the baseline (`LGB_PARAMS` unchanged) at each
development airport, fold 2025-26, cycle hour 12, leads 24 and 36; its
predictions on that cell's test rows must equal the prediction file's
`baseline` at full precision, row for row. This proves Q's rows, inputs
and order. (b) Every scored row of the six files in the three test years
has finite `obs`, `curve`, `raw_gfs` and `b`; report counts per airport
and period, which must equal `meta.txt`'s. (c) The daily-maximum file's
`common` rows per airport and fold, reported. Stop if (a) or (b) fails.

**Step 4. The comparison (D128.5 to D128.9).** Run `--score` once. Fit
Q only for folds 2024-25 and 2025-26 (about 4,400 models; report the
run time and the swap count per airport). Apply D128.8 for each output
and report every step of the ladder with its four parts. Write the
tables to `data/processed/session133_ranges/` with the meta file. If
D128.8's first candidate fails (iv) for an output, record that and carry
on with the descriptive figures; do not choose.

**Step 5. Tests and documents.** `tests/test_session133.py`: the
interval score on made-up values (inside, below, above, on an edge);
table percentiles built only from earlier periods; the ladder on
made-up scores (each of the four parts failing alone); the swap; tercile
edges from earlier periods only; the three imported scripts' SHA-256
equal Step 1's. `tests/README.md` and `scripts/README.md`'s per-session
map gain one line each (plain words, D121.4).

**Step 6. Final checks.** All tests OK (report the count); scope list
against `git status --porcelain`; nothing under the folders the rules
name changed; 0 em-dashes in added lines; nothing read valid after
2026-07-31T23:00 UTC; no claim-airport or live file opened.

## End of session (CLAUDE.md)

1. **F177**, at most about 40 lines (D93.10): the gate with PASS or
   FAIL; each output's ladder (headline interval score, airports lower,
   per-period result, pooled coverage) and its winner, or that no
   choice was made; Q's swap count and run time; the descriptive
   figures a decision needs (the winner's coverage per airport and
   period with its interval, raw GFS's ranges beside it, the tercile
   splits in a few lines); readings for the owner (anything D128 left
   open and how it was read); what was not done; and the pointer to the
   output file. Labelled build-choice scores, never results.
2. **Overwrite STATUS.md** (current only, pruned): stage H opened; the
   range test chosen in outline (D128.3); session 133's outcome in a few
   lines; F176's open caption question carried. End with:
   `**Next planning session:** Review session 133 and commit; then plan
   session 134: freeze each output's winning range method at the 12
   airports, record the 2026-27 range test's pre-registration (D128.3),
   and add the ranges to the live tool (D128.11).`
3. **Archive step:** make D128.12's index changes, add F177, then
   `python3 scripts/archive_decisions.py --apply --session 133`.
4. **Checks:** `--citations`; byte size of DECISIONS.md (under 80,000);
   scope list against `git status --porcelain`.
5. **Output file** `notes/session-133-output.txt` starts with a summary
   of at most 30 lines and a checkpoint line per step; report it in
   chat. Then stop and wait for review. Do not commit.
