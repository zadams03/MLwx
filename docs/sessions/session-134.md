# Session 134: freeze the 80 % ranges at the 12 airports, pre-register their 2026-27 test, and show them on the live page

Plain words, British spelling, no em-dashes in any new text (CLAUDE.md).
This session records D129, which makes the range test of D128.3 binding
with the owner's three rulings; freezes stage H's winners (T1 hourly, M1
daily maximum) and their raw-GFS references at the 12 airports from
spent out-of-sample errors; and adds the ranges to the live page,
labelled "not yet verified". No logged value, log column, model or
pinned file changes. Offline. No 2026-27 value is read or scored.
Recommended model: Fable.

## Read first

- STATUS.md in full; SPEC 2.5, 6 (stage H's bullet) and 9; the live
  DECISIONS.md in full (D103.4, D105.5 and D128 above all).
- Archived, by line range: D98.10, F125.3 (its opening), D116.10,
  D125.4, D125.8, D127.2.
- `scripts/session133_ranges.py`: the docstring, the module constants,
  `interval_score`, `inside`, `build_table`, `apply_table`,
  `day_coverage_interval`, `load_hourly` and `load_daily`.
- `scripts/session112_analysis.py`: `DEV_ICAO`, `STATION`, `PRED_DIR`
  and how the claim airports' files label their periods.
- `../MLwx-stagec/analysis112/meta.txt` in full; the header lines of
  `data/processed/session104_dailymax_days.csv` and
  `data/processed/session107_claim_days.csv`.
- `src/mlwx/page.py` in full; `tests/test_live.py`'s `PageTests`;
  `tests/test_pinned_files.py`; `deploy/mlwx-live/README.md`'s section
  on the page.

## Rules for this session

- **Writes:** only the scope list below, and temporary folders under
  `$TMPDIR` (kept, paths printed). Nothing under `deploy/` other than
  its README, `figures/`, `../MLwx-stagec/`, `../MLwx-live/` or any
  other MLwx-all folder.
- **Network:** none. Before running a mode, read the code path it runs
  and confirm it makes no network call and writes only where it should;
  note this in the checkpoint.
- **Imported scripts are never edited.** `session133_ranges.py` and
  `session112_analysis.py` are imported read-only, each after its
  SHA-256 is checked equal to HEAD's blob (D116.10). Use their functions
  and constants; do not copy and change their code.
- **Pinned files (D125.4) are not touched:** `observations.py`,
  `dailymax.py`, `prediction_log.py`, `config.py`, `records.py`,
  `data/gfs_airports.csv`, `session111_new_tables.csv`. Nor is
  `runner.py`. `tests/test_pinned_files.py` must pass unchanged.
- **Spent data only.** Nothing valid after 2026-07-31T23:00 UTC is read
  or used. Nothing from MLwx-live's log, `obs/` or page is opened (D105.6);
  the page is tested on made-up logs only.
- **Stop rules.** Any failed check or gate stops the session at that
  step; report and wait. Do not work around it.

## Scope list (files this session may create or edit)

DECISIONS.md, DECISIONS-archive.md, STATUS.md,
scripts/session134_freeze_ranges.py, scripts/README.md,
src/mlwx/ranges.py (new), src/mlwx/page.py,
src/mlwx/data/gfs_ranges.csv (new),
data/processed/session134_ranges/ (new folder),
tests/test_session134.py, tests/README.md,
deploy/mlwx-live/README.md, notes/session-134-output.txt.

## Steps

**Step 1. Start checks.** HEAD is `ff8c074` (title starts "Session
133:"); the tree is clean apart from this prompt. Tests:
`.venv/bin/python -m unittest discover -s tests`, all OK (STATUS says
426, 1 skipped; report the count). SHA-256 at HEAD:
`session133_ranges.py` `4bbe4ceaec5c72057bba0ad8f6f744b7a634016e6fcd935412db3436d28875b2`,
`session112_analysis.py` `bf1fadbfe434264a76c48eb79120f6d684c540263edf423387d6e715c0a71aab`,
`data/processed/session104_dailymax_days.csv` `65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3`,
`data/processed/session107_claim_days.csv` `3ef112935585e03245238dedbdc521063db81e486e61c55021f7026a03f8a297`,
`src/mlwx/page.py` `da5da1830538638e71621bb4af0a5fa6e5d8c77b63d28d3fd5dd065781635561`.
The 12 prediction files in `../MLwx-stagec/analysis112/` equal
`meta.txt`'s SHA-256. Stop if any check fails.

**Step 2. Record D129.** Append the block below to DECISIONS.md with
`sed`, exactly, after its last line. The block starts with its own
blank line, `---` line and blank line, so the archive tool can split
it from F177. Check it byte-equal by `diff` and `cmp`; 0 em-dashes.

```

---

## 2026-11-15: Session 134 decision: F177 accepted, the 2026-27 range test pre-registered, the ranges frozen at the 12 airports and shown on the live page (owner, planning chat)

**D129. Owner decisions, planning chat (after session 133's commit): F177 accepted; D128.3's range test pre-registered and made binding, with the owner's three rulings; how the ranges are frozen at the 12 airports; how they are shown live, under D105.5(k); and Live index changes.** Written at the start of session 134, before any other edit. No value valid on or after 2026-08-01 has been scored, in this test, in the live test (D105.5) or in stage B (D73).

- **D129.1 F177 accepted,** with its readings (F177.11) as written. The winners stand: T1 for the hourly curve, M1 for the daily maximum (D128.8).
- **D129.2 What is frozen (a build step, D72.2).** For each airport of D103.4 (EGLC, LFPG, KDSM, YSDU, KRNO, KSFO, EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN) and each output, one pair (P10, P90): numpy's default (linear) 10th and 90th percentiles of past out-of-sample errors (D128.5). Hourly (T1): e = obs - curve over the airport's rows with status `scored` in session 112's prediction file (`../MLwx-stagec/analysis112/pred_<ICAO>.csv.gz`, equal to `meta.txt`'s SHA-256), all leads 3 to 48 together: at the development airports the test years 2023-24, 2024-25 and 2025-26; at the claim airports looks A and B (2024-25 and 2025-26). Daily maximum (M1): e = obs_max - curve_max over the days with `common` true, from `data/processed/session104_dailymax_days.csv` (all three years) at the development airports and `data/processed/session107_claim_days.csv` (looks A and B) at the claim airports. The range is [centre + P10, centre + P90], the centre being the logged `corrected` value, or the daily maximum read off the logged `corrected` curve. Nothing valid after 2026-07-31T23:00 UTC is used.
- **D129.3 The reference (owner's ruling).** Built the same way from raw GFS's own errors on the same rows and days (RT1: e = obs - raw_gfs; RM1: e = obs_max - raw_gfs_max), and centred on the logged `raw_gfs`, or on the daily maximum read off the logged `raw_gfs` curve.
- **D129.4 The file.** Both sets are in `src/mlwx/data/gfs_ranges.csv`: 48 rows (12 airports, 2 outputs, range and reference). Its SHA-256 is recorded in F178 and held as a constant (D98.2) in `src/mlwx/ranges.py` and by a test. It is not changed before this test's looks; any change is recorded in DECISIONS first, and the test always scores session 134's file at that SHA-256, whatever the page showed.
- **D129.5 The test (binding; replaces D128.3's outline).** The 12 airports; both outputs; D105.5(e)'s periods. Rows and days: exactly those D105.5(a), (b) and (h) define for these airports from 2026-10-12 12z, the ranges applied to the log as issued (owner's ruling: every forecast since then, not only those issued after the page showed ranges); observations by D105.5(f). Per airport, period and output, two parts, both needed to pass: (a) honest odds (owner's ruling: a tolerance): coverage is the share of rows (or days) with l <= y <= u; its 95 % interval by F125.3's method, computed as session 133's `day_coverage_interval` does (blocks of 7 days; the day is the cycle's UTC date for the hourly curve and the local day for the daily maximum; coverage is the sum inside over the sum of rows on the drawn days; 10,000 resamples; 2.5th and 97.5th percentiles), must overlap 0.75 to 0.85: its upper end is at least 0.75 and its lower end at most 0.85. (b) useful: its mean interval score (D128.5) is lower than the reference's (D129.3) on the same rows or days, at full precision; a tie fails.
- **D129.6 Verdicts and the claim.** PASS or FAIL per airport, period and output, with each part's result shown. The claim, per output and period: "passes at N of 12 airports", as issued live. The write-up leads with the smallest margin in part (b) as a percentage, and the coverage interval nearest to falling outside 0.75 to 0.85. Nothing is averaged across airports. One generator, numpy.random.default_rng(134), drawn in D103.4's order of airports, the hourly curve before the daily maximum, period A before period B.
- **D129.7 Expectation, stated before any value is seen.** Part (b) passes at all 12 airports in period A, for both outputs. None is stated for part (a), or for period B.
- **D129.8 Descriptive, never part of a verdict.** Coverage, mean width and interval score by lead band (3 to 12, 13 to 24, 25 to 36, 37 to 48) and cycle hour, and before and after the redeploy that first shows the ranges; the reference's coverage; rows and days with no observation, counted.
- **D129.9 The look.** One per period, in a later session whose scoring script is written, gated on spent data or synthetic logs, and committed before it reads any observation valid on or after 2026-10-12 and before the first look of D73 or D105.5.
- **D129.10 Shown live, under D105.5(k).** The page draws each of the 12 airports' hourly range as a band around the corrected curve and adds the daily maximum's range to its table, labelled "not yet verified" until this test's look. The 37 other airports show no range. Only `src/mlwx/page.py`, the new `src/mlwx/ranges.py` and the new data file change: no logged value, log column or log file changes, none of D125.4's pinned files changes, and `runner.py` does not change. If the data file is missing or its SHA-256 differs, the page shows no range and says so; a run is never stopped by it. The live test (D105.5) treats every row after the redeploy exactly as before it. The owner redeploys with `MLWX_COMMIT` set to session 134's commit; `MODELS_TAG` unchanged.
- **D129.11 Plan.** Session 134: this entry, the freeze, the page, F178; then the owner's redeploy. The range test's scoring script comes in a later session (D129.9), possibly with the GFS v17 session. Then stage D, starting with AIFS, then stage E (D121.2); GEFS ranges as a challenger later (D128.11). A GFS v17 Service Change Notice goes ahead of all of these.
- **D129.12 Live index.** Removed (archived): D128 and F177, which are settled (D128.3 is replaced by D129.5; F177 is accepted). Added: D129 and F178 (F178 when it is written). After session 134: D93, D103, D105, D118, D129, F178.
```

**Step 3. The freeze script and its gate.** Write
`scripts/session134_freeze_ranges.py` with modes `--gate` and
`--freeze`, importing `build_table` and the loaders' constants from
session 133 (station codes by session 112's `STATION`; session 107's
file names KORD `ORD`; check every mapping). `--gate`: (a) with the
script's own row loaders and `build_table`, rebuild at the six
development airports the tables session 133 used for scoring period
2025-26 (built from 2023-24 and 2024-25) for T1, RT1, M1 and RM1; all
24 rows equal `data/processed/session133_ranges/tables.csv`'s p10, p90
and n at full precision. (b) Row counts: at each airport the `scored`
rows used equal `meta.txt`'s per-period counts summed (three years at
the development airports, A and B at the claim airports); the `common`
days used per airport are reported, and every e is finite. (c) No row
or day used is valid after 2026-07-31T23:00 UTC. Stop if any fails.
`--freeze` (once): write `src/mlwx/data/gfs_ranges.csv` with columns
`airport,output,kind,p10,p90,n` (`output` hourly or daily_max; `kind`
range or reference; floats by `repr`; rows in D103.4's airport order,
hourly before daily_max, range before reference; 48 rows), refusing to
overwrite; and `data/processed/session134_ranges/meta.txt` (script and
input SHA-256, versions, run time, the file's SHA-256). Report all 48
rows and each pair's width in the output file. These are build values,
never results.

**Step 4. The page.** `src/mlwx/ranges.py`: `RANGES_SHA256` (Step 3's
value) and a loader that returns the table only if the file exists and
its SHA-256 equals the constant, else `None`. `src/mlwx/page.py`, at
the 12 airports with a table only: a shaded band from corrected + P10
to corrected + P90 behind the corrected curve (drawn before the lines,
in light and dark themes); the y-axis range takes in the band; the
legend gains "80 % range (not yet verified)"; the daily maximum table
gains a column "80 % range, &#176;C" showing "l to u" to one decimal
place. One plain sentence in the page's top note: the shaded band shows
where the temperature is expected to fall about 8 times in 10, built
from the method's past errors; it is being tested on this season's
forecasts and is not yet verified. If the loader returns `None`, no
band or column anywhere and one status line says the ranges are not
available. The 37 other airports' sections are unchanged. Nothing else
in `src/mlwx/` changes. Build the page from a made-up log in a
temporary folder and keep the HTML (print its path).

**Step 5. Tests and documents.** `tests/test_session134.py`: the
CSV's SHA-256 equals `RANGES_SHA256` and Step 3's meta; 48 rows, the
12 airports, `p10 < p90` in every row; the freeze on made-up errors
(percentiles, row order, refusing to overwrite); on a made-up log, the
band's ends equal corrected + P10 and + P90 for a range airport, and
the daily maximum column equals the maximum read off the curve plus
the pair; no band or column at a non-range airport; a missing or
altered file gives no band, the status line, and no exception; the
"not yet verified" label is present; session 133's and session 112's
SHA-256 equal Step 1's. Existing `PageTests` and
`tests/test_pinned_files.py` pass unchanged. One line each in
`tests/README.md` and `scripts/README.md`'s per-session map; one short
paragraph in `deploy/mlwx-live/README.md`'s page section (plain words,
no D numbers, D121.4).

**Step 6. Final checks.** All tests OK (report the count); scope list
against `git status --porcelain`; the pinned files and `runner.py`
unchanged from HEAD; 0 em-dashes in added lines; nothing read valid
after 2026-07-31T23:00 UTC; nothing from MLwx-live opened.

## End of session (CLAUDE.md)

1. **F178**, at most about 40 lines (D93.10): the gate with PASS or
   FAIL; the file's SHA-256 and row count; the 12 airports' range and
   reference pairs, briefly (widths, and the smallest and largest);
   the page change and its fallback; tests; readings for the owner
   (anything D129 left open and how it was read; anything about
   applying spent-data tables to live forecasts, such as the live
   trackers' cold start, that the look should know); what was not
   done; the pointer to the output file. Build values, never results.
2. **Overwrite STATUS.md** (current only, pruned): the range test
   pre-registered (D129) and its parts in two or three lines; the
   ranges frozen and on the page, waiting for the owner's redeploy;
   F176's caption question carried. End with:
   `**Next planning session:** Review session 134 and commit; the
   owner redeploys MLwx-live with MLWX_COMMIT set to session 134's
   commit and checks the page; then plan the next session: stage D,
   starting with AIFS (D121.2), unless a GFS v17 notice has arrived,
   which goes first and may carry the range test's scoring script
   (D129.9).`
3. **Archive step:** make D129.12's index changes, add F178, then
   `python3 scripts/archive_decisions.py --apply --session 134`.
4. **Checks:** `--citations`; byte size of DECISIONS.md (under 80,000);
   scope list against `git status --porcelain`.
5. **Output file** `notes/session-134-output.txt` starts with a summary
   of at most 30 lines and a checkpoint line per step; report it in
   chat. Then stop and wait for review. Do not commit.
