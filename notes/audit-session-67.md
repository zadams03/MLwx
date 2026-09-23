# Session 67 — Repo and code audit (read-only)

Scope: the git repository itself and all 67 tracked Python scripts under
`scripts/`, plus a fresh-environment check in a clean clone. This is part two
of the three-part audit ordered by DECISIONS D60.1. Session 66 audited the
documents (`notes/audit-session-66.md`). Session 68 audits correctness.

This session reports and fixes nothing. Every "suggested fix" below is for a
later fix session. Any fix that touches a **frozen** script (the four named in
`notes/audit-session-66.md` section 3: `session39_sealed_test.py`,
`session48_reserved_year.py`, `session60_combine_design.py`,
`session62_reserved_confirm.py`) is marked "frozen — owner decision".

How the checks were run. Every check is a throwaway script under
`/tmp/audit67/`, outside the repo. `ruff` was installed into a separate
throwaway environment, `/tmp/audit67/toolsvenv`. Nothing was installed into the
project's own `.venv`. Python bytecode from the compile check was written
under `/tmp` too, so no `__pycache__` landed in the repo. The only run of
project code was Step 3, inside a clean clone at `/tmp/audit67/clone`. No model
was fitted in the repo. No MAE was produced for 2024-25 or 2025-26. (Step 3's
preflight fits models on the 2023-24 experiment fold only, which is the one
run the session prompt allows.) The full source of every check script is in
the Appendix. Note that `/tmp` is temporary: the full raw outputs named there
will not survive a reboot, so every output that matters is copied into the
Appendix.

---

## 1. Summary

- must-fix: 0
- should-fix: 6
- cosmetic: 6
- uncertain: 3
- total: 15

**Headline results.**

- **Fresh environment: reproducible.** A clean clone, set up only from the
  instructions in `requirements.txt`, installed all 19 pinned packages
  exactly (`pip freeze` equals the pins). All 67 scripts compiled. The
  no-argument preflight of `session62_reserved_confirm.py` ran first time,
  and its 2023-24 machinery dry-run table **matches F109's recorded table to
  the fourth decimal place at all five airports**: raw, persistence, B,
  B+D,L,R,T, skill versus B, n_train, n_test and no_prev. Its whole output
  differs from the committed `notes/session-64-preflight-output.txt` only in
  the "run at" timestamp. The clean clone has no `data/raw/grib/` (the 25 GB
  cache that D47 keeps out of git), and the preflight did not need it.
- **No compile errors. No undefined names (F821) and no redefinitions
  (F811)** anywhere in the 67 scripts.
- **Every path named in the docs exists**, once line-wrapped names and
  wildcard patterns are allowed for.
- **Every committed pull manifest matches its documented row count, with 0
  FAIL rows. No processed file has a duplicate key or an all-null column**,
  except the one table in A67-06 that has no station column.
- **The observation pairing rule (D14, SPEC 4.5) is written the same way in
  every script that uses it**, in both the minimal method and the GRIB
  methods. The minimal-method test logic is identical across all five
  airports' test scripts, apart from print text and bookkeeping.

The findings below are about provenance, fixed output paths, stale printed
text, and missing setup docs. None of them is a wrong number.

---

## 2. Findings

A67-01 | should-fix | scripts/session37_grib_pull.py:47–49, scripts/session40_grib_pull.py:41 (output folder `data/raw/grib/`, gitignored at .gitignore:36)
evidence: D47 says that for the large GRIB pull, "the provenance manifest (exact queries, URLs, byte-ranges, and the drop log)" is committed and only the raw bytes are gitignored. For the core pull behind `grib_features_v16_window.csv` and `grib_features_sealed_window.csv` (the `B` data under F94 and F109), all of that provenance sits **inside** the gitignored cache: 31,284 per-file `.grib2.meta.txt` sidecars (each holds the URL, `.idx` URL, byte range, pull time and bytes saved), plus `session37_pull_failures.csv` (24 rows) and `session40_pull_failures.csv` (0 rows). `git ls-files data/raw/grib/` returns 0 files. The later pulls did it the D47 way: sessions 49, 51, 53, 55, 57 and 63 each committed a `*_pull_manifest.csv` under `data/raw/diagnostics/`. Only the processed drop logs (`grib_features_*_drops.csv`, 3 and 0 rows) are tracked for the core pull. The archive already describes the sidecars as gitignored (DECISIONS-archive.md:10648), so this is a known layout, but it does not meet D47's own wording. If the "disposable" cache (D47) is deleted, the byte ranges and the pull-failure log for the project's core `B` data are lost. The URLs themselves can still be rebuilt from the script, so the data stays re-fetchable. That is why this is should-fix, not must-fix.
suggested fix: build one manifest CSV per pull from the existing sidecars (one row per file: URL, byte range, pulled-at time, bytes). Commit it with the two failure CSVs under `data/raw/diagnostics/session37/` and `session40/`. This touches no frozen script and no data value.

A67-02 | should-fix | scripts/session39_sealed_test.py:153–154 (frozen)
evidence: the frozen F94 script hard-codes its outputs as `notes/session40-sealed-test-output.txt` (`OUT`, written by `Tee` at :443) and `data/processed/session40_sealed_test_summary.csv` (`SUMMARY_CSV`, written at :475). Both names carry a different session number from the script's own, and both are committed files. Any re-run overwrites the committed record of F94. That includes the one-time recompute that D60.2 allows in session 68. This is the same `OUT_PREFLIGHT` pattern that F109 found.
suggested fix: frozen — owner decision. The simplest option that needs no edit: session 68 runs the recompute inside a clean clone, as Step 3 did here, so the committed files cannot be touched.

A67-03 | should-fix | scripts/session62_reserved_confirm.py:186–187 (frozen)
evidence: `OUT_PREFLIGHT = notes/session-62-preflight-output.txt` (written at :410) and `GRID_CSV_CONFIRM = data/processed/session63_reserved_confirm_grid.csv` (written at :722 by `--confirm`). The grid file's name says session 63, but `--confirm` actually ran in session 64 (F109). Any preflight run overwrites session 62's committed preflight record. **This was reproduced this session inside the clone**: the no-argument run changed `notes/session-62-preflight-output.txt` in exactly the two kinds of change session 64 reported (F109): the timestamp, and every "rows loaded" and "of N total" count rising from 7952 to 9777 (9 lines in all). A `--confirm` re-run (D60.2) would overwrite `session63_reserved_confirm_grid.csv` in the same way.
suggested fix: frozen — owner decision. Same workaround as A67-02: run only inside a clone.

A67-04 | should-fix | scripts/session62_reserved_confirm.py:414, 515–518, 575, 634 (frozen)
evidence: the preflight's printed text is stale since F107 wired in the reserved-year family files. It prints "No reserved-year row is read anywhere in this function" (header, :414) and "No row of the reserved 2024-08-01..2025-07-31 confirmation year was read anywhere in this function" (end, :634). In the same run it prints `rows loaded=9777` for each of L, D, T and R. That is 7,952 + 1,825, and the 1,825 are the reserved-year rows that `load_family()`'s second loop reads from `RESERVED_FAMILY_FILES`. The `reserved-year hits=0` counters (:515–518) and the "RESERVED-YEAR FEATURE-DATA GAP … RESULT: ZERO … a genuine blocker for session 63" block (:575) count the first loop only, so they still describe the pre-F107 state. F109 already explains the gap block and the count rise. It does not flag that the "no row is read" sentences are now untrue. No leakage follows from this: the rows are loaded but not used on the preflight path, and the dry-run figures match F109 exactly. But a reader of the output could be misled, and session 68 reviews this script.
suggested fix: frozen — owner decision. At minimum, record in DECISIONS that these printed lines are stale after F107, so session 68 does not read them as true.

A67-05 | should-fix | requirements.txt:7–9 (no README anywhere in the repo)
evidence: the only setup instructions are three comment lines inside `requirements.txt` ("Python 3.12.2 on macOS … python3 -m venv .venv … .venv/bin/python -m pip install -r requirements.txt"). There is no README, no `.python-version`, no `pyproject.toml`. The Python version is recorded only in that comment. The scripts only work with the `.venv` interpreter: with the system `python3`, `import lightgbm` fails with `ModuleNotFoundError: No module named 'lightgbm'` (checked this session). That is the kind of "wrong interpreter" stumble F109 records from session 64. Following the comment exactly did work in Step 3.
suggested fix: add a short README (or a `docs/` setup note) giving the Python version, the two setup commands, "always run scripts with `.venv/bin/python`", the libomp note, and the fact that `data/raw/grib/` is not in git (D47).

A67-06 | should-fix | data/processed/session46_fold_table.csv:1 (written by scripts/session46_backtest.py:347)
evidence: the file has 50 rows but only 10 distinct `(feature_set, fold)` pairs. Each pair appears 5 times, once per airport, with different `train_rows`/`test_rows` (for example "3-feature, 2022-23" appears with train_rows 495 and 493). There is **no station column**, so a row cannot be matched to its airport except by file order. `run_fold()` appends to `fold_table_rows` without the station. The file is cited in live DECISIONS F96 (DECISIONS.md:650).
suggested fix: add a `station` column. This needs a re-run of `session46_backtest.py` or a small post-hoc rebuild. Owner decides whether it is worth it. The script is not frozen.

A67-07 | cosmetic | requirements.txt:14, 36
evidence: the comments say numpy is imported by "session04_model.py, session05_model.py" and that the libomp workaround "sits at the top of scripts/session04_model.py and scripts/session05_model.py". Today 24 scripts import numpy and LightGBM, and 23 scripts carry the libomp restart block.
suggested fix: reword the comments to "the modelling scripts" when the setup docs (A67-05) are written.

A67-08 | cosmetic | .gitignore:1–5, 36
evidence: (a) the header says "Raw data is NOT ignored", but line 36, `data/raw/grib/`, ignores the GRIB cache (D47) with no comment giving the reason. (b) `.claude/` (it holds `settings.local.json`) is ignored only by the owner's machine-wide git ignore file (`~/.config/git/ignore`), not by the project's `.gitignore`. A clone on another machine would show it as untracked. (c) Six pull scripts (sessions 47, 49, 51, 53, 55, 57) write a temporary `_scratch_*.grib2` file into a tracked `data/raw/diagnostics/sessionNN/` folder and delete it in a `finally:` block. A hard kill mid-pull would leave an unignored ~1 MB GRIB file behind. None exists today.
suggested fix: add a one-line D47 comment above line 36, and add ignore rules for `.claude/` and `data/raw/diagnostics/**/_scratch_*.grib2`.

A67-09 | cosmetic | scripts/session01_checks.py, scripts/session03_checks.py, scripts/session03_pull.py, notes/session-01-check-output.txt, notes/session-53-pressure-output.txt
evidence: these 5 tracked files are named in no doc (the archive was checked by grep) and used by no other script. The other 179 tracked files in `scripts/`, `data/processed/` and `notes/` are all referenced. (Four `session63_*_join_drops.csv` files are not named literally anywhere, but `session63_reserved_year_build.py:504` builds their names with an f-string, so they are referenced. `scripts/session47_availability_probe.py` is also referenced: DECISIONS-archive.md:10969 names it with a line break inside the name.)
suggested fix: none needed. Optionally cite them where their session's findings are recorded.

A67-10 | cosmetic | scripts/ (134 ruff findings)
evidence: `ruff --select E4,E7,E9,F`: 102 F541 (f-string with no placeholders), 16 E741 (variable named `l`), 9 F401 (unused imports, in 6 scripts), 7 F841 (unused local variables). **0 F821, 0 F811.** Each F841 was opened and is harmless: 4 are `except … as err` in the pull scripts' retry helpers, plus `synth` (session38_cv.py:512), `extremes` (session38_cloud_diagnostic.py:243) and `any_present` (session31_checks.py:203). The two unused module imports in `session63_join_equivalence_check.py:52–53` (s53, s55) are harmless: pressure and radiation need no elevation correction, which is all the other two imports are used for.
suggested fix: none needed for correctness. A fix session could run `ruff --fix` on non-frozen scripts only.

A67-11 | cosmetic | scripts/ (duplicated functions)
evidence: 57 (name, body) groups are byte-identical in 3 or more scripts (ignoring comments and docstrings). The largest: `Tee` x30, `sub` x30, `year_fraction` x23, `all_days` x21, `mae` x15 and x8, `line` x16/x14, `cycle_and_lead` x13, `load_obs_all` x7, `features_matrix` x7. Copying functions script-to-script, rather than importing a shared module, is how the project keeps each frozen script self-contained. The minimal-method test scripts even check their own function source against `session05_model.py` character by character.
suggested fix: none now. A shared module is an option for future (non-frozen) work only.

A67-12 | cosmetic | scripts/session62_reserved_confirm.py:321–344, scripts/session39_sealed_test.py:250, scripts/session18_test.py:366 (and every copy of `load_obs_all` / `load_obs_target_hour` / `load_obs_12z`)
evidence: SPEC 4.5 says the observation is "the station's **nearest** routine report" within 15 minutes. The code keeps the **last** qualifying report in the file (`series[dt] = float(raw)` overwrites). The two differ only when 2+ usable routine reports fall within 15 minutes of the target hour on the same day. Counted directly over all routine files, 2021-03-24..2026-07-31, at all five airports (`check_pairing_ties.py`): **1 such day in the whole record (YSDU), with equal temperatures, and 0 days where the last report is not also the nearest.** So no recorded figure is affected. It is a latent gap between the words and the code only.
suggested fix: none needed now. If new airports are added, re-run the count, or make the code pick the nearest report explicitly (non-frozen scripts only).

A67-13 | uncertain | data/raw/diagnostics/session35/, session36/, session37/, session47/ (94 tracked `.grib2`/`.idx` files, 45.9 MB)
evidence: 94 raw GRIB or GRIB-index files are tracked, 45.9 MB in all. That is about half of `data/`'s 86.6 MB and most of the repo's size. None is over 5 MB (the largest tracked file of any kind is 2.1 MB). They are small diagnostic samples (session 35 probe, session 36's 77-file validation sample, 4 session-37 elevation diagnostics, 8 session-47 `.idx` files), not the bulk pull. D47's wording ("The GRIB pull is ~20 GB … gitignoring the raw bytes") targets the bulk pull. Most of these files predate D47 (session 37), but the session-47 `.idx` files came after it. Unsure: whether D47 was meant to cover small diagnostic samples is the owner's reading, not something the record settles.
suggested fix: owner decides whether small diagnostic GRIB samples stay tracked. If yes, one sentence in D47's spirit (a later DECISIONS note) would settle it.

A67-14 | uncertain | scripts/session62_reserved_confirm.py:231–234 (frozen)
evidence: `make_feature_vector()` reads the four selected features with `r.get(...)`. A missing key would become `None`, then `NaN` in the float array, and LightGBM would treat it as a missing value. So the model would silently run on a gap instead of raising, which is against the spirit of SPEC 2.2. In the F109 path this cannot happen: `build_complete_case()` (:347) only keeps dates present in all four families and always sets all four keys. The `.get` seems to exist so that `B`-only rows (which lack those keys) can share the same function. Unsure whether any path reaches it with a final-set key missing. None was found.
suggested fix: frozen — owner decision. Flagged for session 68's logic review, not for change.

A67-15 | uncertain | data/raw/openmeteo_previousruns_gfs_{global,seamless}_DSM_2026-08-05_2026-08-15_q27compare.json (tracked)
evidence: two tracked raw files hold Open-Meteo **forecast** values for 2026-08-05..2026-08-15 at DSM. They were pulled in session 15 to settle Q27 (the `gfs_global` versus `gfs_seamless` comparison). Those dates fall inside the 2026-27 year that D59.5 names as Q30's possible forward-looking test year. D59.5 / F110 Step 0 found "no row anywhere under `data/processed/` reaches or exceeds 2026-08-01". That statement is correct as written, because it covers `data/processed/` only. These are raw forecasts only: no observations, nothing scored, nothing fitted. Unsure whether this matters for a future 2026-27 pre-registration. It is recorded so the owner can decide with the fact in hand.
suggested fix: if Q30 branch (i) is chosen, mention these two files in its pre-registration.

---

## 3. The core pipeline map (for session 68)

Built from the docs (DECISIONS/archive by grep), the scripts' own
constants, and their imports. Session 68 should review exactly this set.

### 3.1 Minimal method (SPEC sections 1–6) — F16, F30, F47, F64, F82

One standalone script per airport's sealed test. No script imports another.
Each copies the same functions and checks its own copies against
`session05_model.py` character by character (`func_source`, `PREV_SCRIPT`).

- `scripts/session07_test.py` → EGLC sealed test, 12:00 UTC → **F16** (output `notes/session-07-check-output.txt`; EGLC is hard-coded, no `STATION` constant)
- `scripts/session13_test.py` → LFPG sealed test, 12:00 UTC → **F30** (`notes/session-13-check-output.txt`)
- `scripts/session18_test.py` → DSM sealed test, 18:00 UTC → **F47** (`notes/session-18-check-output.txt`)
- `scripts/session24_test.py` → YSDU sealed test, 02:00 UTC → **F64** (`notes/session-24-check-output.txt`)
- `scripts/session29_test.py` → RNO sealed test, 20:00 UTC → **F82** (`notes/session-29-check-output.txt`)
- Rehearsal scripts (validation-year only, not a verdict): `session04/05_model.py` (EGLC, F14/F15), `session11_model.py` (LFPG), `session16_model.py` (DSM), `session22_model.py` (YSDU), `session27_model.py` (RNO).

Inputs (all tracked): `data/raw/openmeteo_previousruns_gfs_global_{ST}_{chunk}.json` and `data/raw/iem_asos_{ST}_{chunk}_routine.csv`, six chunks each, 2021-03-24..2026-07-31.

Shared code paths, the same logic in all five test scripts:
- forecast load: `load_forecast_12z` (EGLC, LFPG) / `load_forecast_target_hour` (DSM, YSDU, RNO). Takes the `previous_day1` value at the target hour and counts rows after the hard end.
- pairing (D14, SPEC 4.5): `load_obs_12z` / `load_obs_target_hour`. Round each routine report to its nearest hour; keep it if that is the target hour and it is within 15 minutes; drop and count missing `tmpc` (see A67-12).
- join and split: `join`. Pairs forecast and observation per day; builds train 2021-03-24..2025-07-31 and test 2025-08-01..2026-07-31 (plus inner/validation); counts drops by cause; asserts the expected row counts.
- fit: `fit_on_training`. LightGBM on the residual (obs − forecast), features temp, season_sin, season_cos (D21.4 settings).
- score and persistence: `score_test_year`. Raw GFS, persistence (the previous calendar day's paired observation, SPEC 2.1d), climatology (`climatology_from_training`, training years only), mean-bias reference, and the model, on a common day set.
- Drift found: with print text removed, `fit_on_training` is identical in all five test scripts, and `score_test_year` differs only by one bookkeeping flag in session29 (`ok_scored`). `join` differs between test scripts only in drop-cause bookkeeping and the expected-count checks.

### 3.2 Richer 5-feature GRIB method (SPEC 7) — F94

- data chain, training window: `session37_grib_pull.py` (raw GRIB into gitignored `data/raw/grib/`, see A67-01) → `session37_elevation_fix.py` (writes `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`) → `session37_decode.py` (bilinear interpolation, elevation constant, → `data/processed/grib_features_v16_window.csv` + `_drops.csv`).
- data chain, sealed year: `session40_grib_pull.py` → `session40_decode.py` (same elevation constants) → `data/processed/grib_features_sealed_window.csv` + `_drops.csv`.
- scoring: **`session39_sealed_test.py` (frozen)** → **F94**. Functions: `load_grib_features` (D48 window self-guard), `load_obs_all` (D14 pairing, window-filtered), `join_rows`, `features_3` / `features_5`, LightGBM fit, persistence. Outputs `notes/session40-sealed-test-output.txt`, `data/processed/session40_sealed_test_summary.csv` (see A67-02).
- checks that import it as a library: `session41_verify.py`, `session42_scoring_check.py` (F94 Task 2, the persistence day-set check).
- independent reproduction: `session46_backtest.py` (F96) copies `join_rows` identically. Its `load_grib_features` / `load_obs_all` differ only in window constants and extra blank/duplicate checks. It reproduced F94 within 0.0005 °C.

### 3.3 Selected-features GRIB method (SPEC 8) — F109

- `B` inputs: `grib_features_v16_window.csv` and `grib_features_sealed_window.csv` (`B_ONLY_PATHS`, :148).
- L, D, T, R, training window: `session49_upper_air_pull.py`, `session51_moisture_pull.py`, `session53_pressure_pull.py`, `session55_radiation_pull.py` → `data/processed/session{49,51,53,55}_{v16,sealed}_window_with_*.csv` (manifests committed, 0 FAIL).
- L, D, T, R, reserved year: `session63_reserved_year_build.py` (imports the four pull modules' helpers; its `join_*` copies were proven exact by `session63_join_equivalence_check.py`, F108) → `data/processed/session63_reserved_window_with_*.csv`.
- selection (feeds the lock, not the look): `session60_combine_design.py` (frozen; `CANDIDATE_FEATURES` is imported by session 62), `session61_combine_sweep.py` (F106).
- guard: `session48_reserved_year.py` (frozen).
- the look: **`session62_reserved_confirm.py --confirm` (frozen)**, run once in session 64 → **F109**. Functions: `load_family`, `load_base_unfiltered`, `load_obs_all` (D14 pairing; this copy has **no date filter**, the callers choose dates), `build_complete_case`, `join_obs`, `fit_and_score`, `raw_persist`. Outputs `data/processed/session63_reserved_confirm_grid.csv` and `notes/session-64-confirm-output.txt` (see A67-03, A67-04).

### 3.4 Points for session 68's attention (already known, not new findings)

- Persistence is scored on a subset of test days: those with a previous-day observation. The model and raw GFS use all test days. F94 Task 2 checked this for session 39 (verdict unchanged). F109 records the subset (`n_persist = n_final − no_prev`: EGLC 1 day, YSDU 5 days).
- A67-12 (last-wins pairing, no effect), A67-14 (`r.get`), A67-04 (stale preflight text).
- The D60.2 recompute should run inside a clean clone, because of A67-02/A67-03.

### 3.5 Tests and guards (Step 2.7)

**Automated tests: none.** No `tests/` folder, no `test_*.py`, no pytest or
CI config. (`session*_test.py` are the sealed-test scripts, not unit tests.)
The nearest thing is `session48_reserved_year.py`'s own self-check: run on its
own, it proves that the guard passes the three experiment folds and raises on
three reserved-year-touching folds (D51). It was **not** run this session,
because the prompt allows only the Step 3 run. The same guard checks were
seen passing inside Step 3's preflight output.

Guards and where each is called:
- `assert_reserved_year_excluded()` (defined `session48_reserved_year.py:52`, frozen). Called by: the pull scripts 49, 51, 53, 55, 57 (train and sealed spans, before writing); the experiment scripts 50, 52, 54, 56, 58 (`sanity_check_guard()`, on every fold, before any load or fit); `session60_combine_design.py:203`; `session61_combine_sweep.py:335`; `session62_reserved_confirm.py:462/480/489` (preflight: dry-run fold passes, three bad folds and the confirmation fold must raise). Deliberately **not** called on `CONFIRMATION_FOLD` inside `run_confirm()` (D51/D58 exception, :167). Not called by `session46_backtest.py`, which predates D51.
- `assert_all_inside_reserved_year()` (`session63_reserved_year_build.py:125`): every built reserved-year row must fall inside 2024-08-01..2025-07-31.
- F94 self-guards in `session39_sealed_test.py`: missing-file and out-of-window refusal in `load_grib_features`, training-row reconciliation (D48.7), sealed-row ceiling (D48.8/F93), in-window date assertions.
- Minimal-method test scripts: `assert max(fc) <= HARD_END`, `assert max(obs) <= HARD_END`, and expected train/inner/validation/test row counts (for example "row counts do not match F12 - STOP").
- `session46_backtest.py`: per-fold `train_end < test_start` and per-row window assertions.
- Experiment scripts 52–58: `sanity_check_*` integrity checks (moisture floor, tendency arithmetic, radiation window, precip integrity).

---

## 4. Clean checks

Each of these was checked and came back clean:

- **Step 0.** `git status --porcelain` at start: only `?? docs/session-67.md`.
- **Step 1.1.** 877 tracked files: root 8 files 0.9 MB; `data/` 664 files 86.6 MB; `docs/` 69 files 0.5 MB; `notes/` 69 files 1.0 MB; `scripts/` 67 files 1.7 MB. **No tracked file is over 5 MB** (the largest is `session53_pull_manifest.csv`, 2.1 MB). **No file under `data/raw/grib/` is tracked** (the bulk GRIB cache, D47). (The session prompt's "68 files in `scripts/`" counts the ignored `__pycache__` folder; there are 67 tracked `.py` files.)
- **Step 1.2.** The only untracked, non-ignored file is `docs/session-67.md`. Ignored items: `.DS_Store` files, `.claude/`, `.venv/`, `data/raw/grib/`, `scripts/__pycache__/`. All expected (for `.claude/`, see A67-08).
- **Step 1.3.** 195 distinct repo paths named in CLAUDE, SPEC, RESULTS, STATUS, live DECISIONS, `docs/*.md` and the archive (by grep) all resolve. The 6 apparent misses were checked by hand: 3 are prose words after a line-wrapped folder name ("data/processed/ show", "session31/ files", "session36/ with"); `notes/DECISIONS` is prose ("the session-19 notes/DECISIONS"); `notes/session-07/13/24-check-output.txt` is shorthand for three files that all exist; `notes/audit-session-67.md` is this report. The one gitignored-by-design path cited is `data/raw/grib/` (3 citations). 6 wildcard patterns were not checked as paths.
- **Step 1.4.** 179 of 184 tracked files in `scripts/`, `data/processed/` and `notes/` are referenced (the 5 exceptions are A67-09).
- **Step 1.5.** All 9 committed pull manifests have 0 duplicate request keys and every row `OK`: session49 19,083 (stated 19,083); session51 19,083; session53 19,083; session55 9,542 (stated 9,542); session57 6,361 (stated 6,361); session63 upper-air, moisture and pressure 4,380 each, radiation 2,190 (stated 4,380/4,380/4,380/2,190). Every tracked raw data file has its D15 `.meta.txt` sidecar, except 16 derived CSVs (manifests and diagnostic tables), which are provenance themselves. No sidecar is missing its data file. In the gitignored cache, all 31,284 `.grib2` files have sidecars and none is orphaned.
- **Step 1.6.** 48 processed CSVs: no ragged rows, no all-null column, no duplicate `(station, target_date)` or other natural key, except A67-06. Every per-day file's `target_date` sits exactly inside its intended window: v16 windows 2021-03-24..2025-07-31 (7,952 rows) or 2021-03-24..2024-07-31 for the session-49–57 family files (6,127 rows, reserved year excluded per D51); sealed windows 2025-08-01..2026-07-31 (1,825 rows, 365 per airport); reserved windows 2024-08-01..2025-07-31 (1,825 rows). The earliest `run_date` (2021-03-23) is the forecast issue day before the first target day, as expected. No processed row is dated after 2026-07-31.
- **Step 2.1.** `py_compile`: 0 failures of 67, both in the working repo and in the clean clone.
- **Step 2.2.** 0 F821, 0 F811.
- **Step 2.3.** 0 absolute paths (`/Users/`, `/home/`, `/tmp/`, `/private/`, `C:\`) in any script. All scripts build paths from `Path(__file__)`. Cross-session **write** targets exist in exactly the two frozen scripts in A67-02 and A67-03. The other 96 constants that name another session's files are reads or print text. The one "two scripts write the same file" hit (`session63_reserved_window_with_moisture.csv`) is a false positive: `session63_join_equivalence_check.py:304` only reads it, and the tool matched its `Tee` class's `open(path, "w")`.
- **Step 2.4.** `requirements.txt` exists; all 19 entries are pinned with `==`. Every third-party import (by AST) is listed: `numpy`, `lightgbm` (24 scripts each), `eccodes` (10), `requests` (8). The 15 listed but never imported directly are their dependencies, plus scikit-learn (kept for the libomp dylib, as the file explains). Nothing imported is missing from the list.
- **Step 2.5.** No drifting function changes the pairing rule, the split, the fit settings or the MAE formula. Where bodies differ, the differences are window constants, drop-count bookkeeping, extra self-guards, or which feature columns a row carries. The three `mae` variants all compute a plain mean absolute error; they differ only in empty-list handling.
- **Step 3.** Fresh clone, documented setup, all pins installed, all scripts compile, preflight matches F109 exactly (details in section 1 and Appendix 5.13). **The libomp behaviour seen in session 64 did not recur**: with the clone's own `.venv/bin/python`, the restart shim found `sklearn/.dylibs/libomp.dylib` and LightGBM loaded first time. Run from a clean clone, the preflight finished in about 23 s (wall clock).

---

## 5. Appendix — check scripts and raw output

All scripts live in `/tmp/audit67/`. They read the repo and never write to it.
Raw outputs are in the same folder under the names shown.

### 5.1 `shell_steps.sh` — Steps 0–1.2, 2.1–2.2 and 3: shell commands

````bash
# Session 67 -- shell steps, run from the repo root unless noted. Read-only.
# Step 0
git status --porcelain
# Step 1.1 inventory
git ls-files | wc -l
git ls-files -z | xargs -0 stat -f "%z %N" > /tmp/audit67/tracked_sizes.txt
awk '{split($2,a,"/"); d=(index($2,"/")?a[1]:"(root)"); c[d]++; s[d]+=$1} END{for(k in c) printf "%-12s %5d files %12d bytes (%.1f MB)\n",k,c[k],s[k],s[k]/1048576}' /tmp/audit67/tracked_sizes.txt | sort
sort -rn /tmp/audit67/tracked_sizes.txt | head -20
awk '$1>5242880' /tmp/audit67/tracked_sizes.txt
git ls-files | grep -iE '\.grib2?$|\.idx$' > /tmp/audit67/tracked_grib.txt
# Step 1.2 ignored / untracked
git status --porcelain --ignored
git check-ignore -v .claude/ ; cat ~/.config/git/ignore
# Step 2.1 compile (bytecode to /tmp so no __pycache__ lands in the repo)
for f in scripts/*.py; do python3 -c "import py_compile,sys,tempfile,os; py_compile.compile(sys.argv[1], cfile=os.path.join(tempfile.mkdtemp(dir='/tmp/audit67'),'x.pyc'), doraise=True)" "$f"; done
# Step 2.2 lint (ruff installed in /tmp/audit67/toolsvenv, not the project .venv)
python3 -m venv /tmp/audit67/toolsvenv && /tmp/audit67/toolsvenv/bin/pip install -q ruff
/tmp/audit67/toolsvenv/bin/ruff check --isolated --no-cache --select E4,E7,E9,F --output-format concise scripts/
/tmp/audit67/toolsvenv/bin/ruff check --isolated --no-cache --select E4,E7,E9,F --statistics scripts/
# Step 3 fresh environment (in /tmp/audit67/clone)
git clone -q "/Users/zacharyadams/Coding Projects/MLwx" /tmp/audit67/clone
cd /tmp/audit67/clone
python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pip freeze   # compared with requirements.txt pins
for f in scripts/*.py; do .venv/bin/python -c "...same py_compile call..." "$f"; done
.venv/bin/python scripts/session62_reserved_confirm.py   # NO arguments: preflight() only
git diff --stat; git diff notes/session-62-preflight-output.txt
diff "/Users/zacharyadams/Coding Projects/MLwx/notes/session-64-preflight-output.txt" notes/session-62-preflight-output.txt
python3 -c "import lightgbm"   # system interpreter, for the session-64 note
````

### 5.2 `check_doc_paths.py` — Step 1.3: paths named in the docs

````python
#!/usr/bin/env python3
"""Session 67, Step 1.3: every repo path named in the docs must exist.

Read-only. Scans CLAUDE.md, SPEC.md, RESULTS.md, STATUS.md, live
DECISIONS.md and docs/*.md in full. DECISIONS-archive.md is scanned by a
grep (subprocess) only, never read by this script.
A path counts as found if it is in `git ls-files` or exists on disk.
Paths that are gitignored by design (data/raw/grib/, D47) are listed apart.
"""
import glob
import os
import re
import subprocess

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)

DOCS = ["CLAUDE.md", "SPEC.md", "RESULTS.md", "STATUS.md", "DECISIONS.md"] + sorted(glob.glob("docs/*.md"))
PATH_RE = re.compile(r"(?<![A-Za-z0-9_/.])((?:scripts|data|notes|docs)/[A-Za-z0-9_./{}*<>,-]+)")

tracked = set(subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n"))
tracked_dirs = set()
for t in tracked:
    parts = t.split("/")
    for i in range(1, len(parts)):
        tracked_dirs.add("/".join(parts[:i]))


def is_ignored(p):
    return subprocess.run(["git", "check-ignore", "-q", p]).returncode == 0


def clean(p):
    p = p.rstrip(".,;:)`'\"")
    return p


def classify(p):
    if any(c in p for c in "*{}<>"):
        return "pattern"
    if p.endswith("_") or p.endswith("-"):
        return "wrapped"  # name broken across a line in the source text
    q = p.rstrip("/")
    if q in tracked or q in tracked_dirs:
        return "ok"
    if os.path.exists(q):
        return "ignored-by-design" if is_ignored(q) else "on-disk-untracked"
    if is_ignored(q):
        return "ignored-by-design-missing"
    return "MISSING"


def scan(label, lines):
    results = []
    for line_no, line in lines:
        for m in PATH_RE.finditer(line):
            p = clean(m.group(1))
            results.append((label, line_no, p, classify(p)))
    return results


WRAP_RE = re.compile(r"((?:scripts|data|notes|docs)/[A-Za-z0-9_./-]*[/_])\n[ \t]*([A-Za-z0-9_./{}*<>,-]+)")


def unwrap(lines):
    """Join a path that the source text broke across a line (after '/' or '_').
    Returns (line_no, text) pairs; the joined path is reported at its first line."""
    out = []
    for i, (n, txt) in enumerate(lines):
        nxt = lines[i + 1][1] if i + 1 < len(lines) and lines[i + 1][0] == n + 1 else None
        if nxt is not None:
            m = re.search(r"((?:scripts|data|notes|docs)/[A-Za-z0-9_./-]*[/_])$", txt.rstrip("`"))
            if m:
                cont = re.match(r"[ \t]*`?([A-Za-z0-9_./{}*<>,-]+)", nxt)
                if cont:
                    txt = txt.rstrip("`")[: m.start()] + m.group(1) + cont.group(1)
        out.append((n, txt))
    return out


all_results = []
for d in DOCS:
    with open(d, encoding="utf-8") as f:
        all_results += scan(d, unwrap(list(enumerate(f.read().split("\n"), 1))))

# archive: grep only
# -A1 brings the next line along so a path broken across a line can be joined.
g = subprocess.run(["grep", "-n", "-A1", "-E", r"(scripts|data|notes|docs)/", "DECISIONS-archive.md"],
                   capture_output=True, text=True).stdout
arch = {}
for row in g.splitlines():
    m = re.match(r"^(\d+)[:-](.*)$", row)
    if m:
        arch[int(m.group(1))] = m.group(2)
arch_lines = sorted(arch.items())
hit_lines = {n for n, t in arch_lines if re.search(r"(scripts|data|notes|docs)/", t)}
all_results += [r for r in scan("DECISIONS-archive.md(grep)", unwrap(arch_lines)) if r[1] in hit_lines]

from collections import Counter, defaultdict
print("=== counts by class (mentions) ===")
for k, v in Counter(r[3] for r in all_results).most_common():
    print(f"{k:28s} {v}")
uniq = defaultdict(list)
for label, n, p, c in all_results:
    uniq[(p, c)].append(f"{label}:{n}")
print("\n=== distinct paths by class ===")
for k, v in Counter(c for (p, c) in uniq).most_common():
    print(f"{k:28s} {v}")
for cls in ["MISSING", "ignored-by-design", "ignored-by-design-missing", "on-disk-untracked", "wrapped", "pattern"]:
    print(f"\n=== {cls} ===")
    for (p, c), where in sorted(uniq.items()):
        if c == cls:
            print(f"{p}\n    cited at: {', '.join(where[:6])}{' ...(+%d)' % (len(where)-6) if len(where) > 6 else ''}")
````

**Raw output** (`/tmp/audit67/check_doc_paths_output.txt`, 57 lines):

````
=== counts by class (mentions) ===
ok                           425
pattern                      9
MISSING                      9
ignored-by-design            3
on-disk-untracked            1
wrapped                      1

=== distinct paths by class ===
ok                           195
pattern                      6
MISSING                      6
ignored-by-design            1
on-disk-untracked            1
wrapped                      1

=== MISSING ===
data/processed/show
    cited at: docs/session-64.md:32
data/raw/diagnostics/session31/files
    cited at: docs/session-31.md:143
data/raw/diagnostics/session36/with
    cited at: docs/session-36.md:143, DECISIONS-archive.md(grep):9797
notes/DECISIONS
    cited at: docs/session-20.md:38
notes/audit-session-67.md
    cited at: docs/session-67.md:27, docs/session-67.md:163, docs/session-67.md:204
notes/session-07/13/24-check-output.txt
    cited at: DECISIONS-archive.md(grep):10866

=== ignored-by-design ===
data/raw/grib/
    cited at: docs/session-37.md:44, DECISIONS-archive.md(grep):10061, DECISIONS-archive.md(grep):10648

=== ignored-by-design-missing ===

=== on-disk-untracked ===
docs/session-67.md
    cited at: docs/session-67.md:58

=== wrapped ===
notes/session63-join-equivalence-check-
    cited at: DECISIONS-archive.md(grep):13364

=== pattern ===
data/processed/*.csv
    cited at: DECISIONS-archive.md(grep):13468
data/processed/session63_reserved_window_with_*.csv
    cited at: DECISIONS-archive.md(grep):13378
data/processed/session63_reserved_window_with_{upper_air,moisture,pressure,radiation}.csv
    cited at: docs/session-64.md:39
data/raw/features/*.json
    cited at: DECISIONS-archive.md(grep):10183
data/raw/iem_asos_RNO_*_routine.csv
    cited at: DECISIONS-archive.md(grep):8953
docs/*.md
    cited at: STATUS.md:20, docs/session-66.md:101, docs/session-66.md:128, docs/session-67.md:73
````

### 5.3 `check_orphans.py` — Step 1.4: orphans

````python
#!/usr/bin/env python3
"""Session 67, Step 1.4: orphan check.

For every tracked file in scripts/, data/processed/ and notes/, look for its
basename (a) in any doc (CLAUDE, SPEC, RESULTS, STATUS, live DECISIONS,
docs/*.md, read in full), (b) in DECISIONS-archive.md by grep only, or
(c) in any other tracked script. Doc text is also searched with line
breaks after '_', '-' or '/' removed, since long names are often wrapped.
The file's own text never counts as a reference to itself.
Read-only.
"""
import glob
import os
import re
import subprocess

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)

tracked = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n")
targets = [t for t in tracked if t.startswith(("scripts/", "data/processed/", "notes/"))]

DOCS = ["CLAUDE.md", "SPEC.md", "RESULTS.md", "STATUS.md", "DECISIONS.md"] + sorted(glob.glob("docs/*.md"))
SCRIPTS = [t for t in tracked if t.startswith("scripts/") and t.endswith(".py")]


def read(p):
    with open(p, encoding="utf-8", errors="replace") as f:
        return f.read()


def joined(text):
    return re.sub(r"([_/-])\n[ \t>]*`?", r"\1", text)


doc_text = {d: read(d) for d in DOCS}
doc_join = {d: joined(t) for d, t in doc_text.items()}
script_text = {s: read(s) for s in SCRIPTS}


def archive_hits(name):
    r = subprocess.run(["grep", "-c", "-F", name, "DECISIONS-archive.md"], capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


orphans = []
summary = {"scripts/": [0, 0], "data/processed/": [0, 0], "notes/": [0, 0]}
for t in targets:
    base = os.path.basename(t)
    stem = os.path.splitext(base)[0]
    where = []
    for d in DOCS:
        if base in doc_text[d] or base in doc_join[d]:
            where.append(d)
    if archive_hits(base):
        where.append("DECISIONS-archive.md")
    for s, txt in script_text.items():
        if s == t:
            continue
        # a script may be imported as a module (stem) or name a file (basename)
        if base in txt or (t.endswith(".py") and re.search(rf"\b(import|from)\s+{re.escape(stem)}\b", txt)):
            where.append(s)
    key = next(k for k in summary if t.startswith(k))
    summary[key][0] += 1
    if not where:
        summary[key][1] += 1
        orphans.append(t)

print("=== totals (tracked files checked / unreferenced) ===")
for k, (n, o) in summary.items():
    print(f"{k:18s} {n:4d} checked, {o:3d} unreferenced")
print("\n=== unreferenced files (basename found in no doc, not in the archive by grep, not in another script) ===")
for o in orphans:
    print(o)
````

**Raw output** (`/tmp/audit67/check_orphans_output.txt`, 16 lines):

````
=== totals (tracked files checked / unreferenced) ===
scripts/             67 checked,   4 unreferenced
data/processed/      48 checked,   4 unreferenced
notes/               69 checked,   2 unreferenced

=== unreferenced files (basename found in no doc, not in the archive by grep, not in another script) ===
data/processed/session63_moisture_join_drops.csv
data/processed/session63_pressure_join_drops.csv
data/processed/session63_radiation_join_drops.csv
data/processed/session63_upper_air_join_drops.csv
notes/session-01-check-output.txt
notes/session-53-pressure-output.txt
scripts/session01_checks.py
scripts/session03_checks.py
scripts/session03_pull.py
scripts/session47_availability_probe.py
````

### 5.4 `check_manifests.py` — Step 1.5: manifests and provenance

````python
#!/usr/bin/env python3
"""Session 67, Step 1.5: manifests and provenance (D15, D47). Read-only.

1. Every committed GRIB pull manifest (data/raw/diagnostics/session*/
   *_pull_manifest.csv): data-row count, status counts, duplicate request
   keys, and the row/FAIL count the docs state (from DECISIONS-archive.md,
   by grep, typed in below with its line number).
2. Every tracked raw file under data/raw/ that is not itself a .meta.txt:
   does it have its .meta.txt sidecar (D15), and does every sidecar have its
   data file?
3. The gitignored core GRIB cache (data/raw/grib/): sidecar pairing and the
   failure logs, plus whether any of that provenance is tracked in git.
"""
import csv
import glob
import os
import subprocess
from collections import Counter

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
tracked = [t for t in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n") if t]

# stated counts, copied from DECISIONS-archive.md (grep line numbers in brackets)
STATED_ROWS = {
    "session49_pull_manifest.csv": 19083,          # archive:11127, 0 FAIL archive:11185
    "session55_pull_manifest.csv": 9542,           # archive:11852, 0 FAIL archive:11927
    "session57_pull_manifest.csv": 6361,           # archive:12285, 0 FAIL archive:12375
    "session63_upper_air_pull_manifest.csv": 4380,  # archive:13272 (order: see below)
    "session63_moisture_pull_manifest.csv": 4380,
    "session63_pressure_pull_manifest.csv": 4380,
    "session63_radiation_pull_manifest.csv": 2190,
}

print("=== 1. committed pull manifests ===")
print(f"{'manifest':42s} {'rows':>6s} {'stated':>7s} {'status counts':30s} dup_keys")
for m in sorted(glob.glob("data/raw/diagnostics/session*/*_pull_manifest.csv")):
    with open(m, newline="") as f:
        rows = list(csv.DictReader(f))
    keycol = "field_key" if "field_key" in rows[0] else "level_key"
    keys = Counter((r["run_date"], r["cycle"], r["lead"], r[keycol]) for r in rows)
    dups = sum(1 for k, v in keys.items() if v > 1)
    st = dict(Counter(r["status"] for r in rows))
    stated = STATED_ROWS.get(os.path.basename(m), "-")
    flag = "" if stated == "-" or stated == len(rows) else "  <-- MISMATCH"
    print(f"{os.path.basename(m):42s} {len(rows):6d} {str(stated):>7s} {str(st):30s} {dups}{flag}")
    tr = m in tracked
    if not tr:
        print(f"   NOT TRACKED: {m}")

print("\n=== 2. D15 sidecars for tracked raw files ===")
raw = [t for t in tracked if t.startswith("data/raw/")]
metas = {t for t in raw if t.endswith(".meta.txt")}
datas = [t for t in raw if not t.endswith(".meta.txt")]
no_meta = [d for d in datas if d + ".meta.txt" not in metas]
no_data = [m for m in metas if m[: -len(".meta.txt")] not in set(datas)]
print(f"tracked raw data files: {len(datas)}, tracked .meta.txt: {len(metas)}")
print(f"data files without a .meta.txt sidecar: {len(no_meta)}")
by_dir = Counter(os.path.dirname(d) for d in no_meta)
for d, n in sorted(by_dir.items()):
    print(f"   {d}: {n}")
for d in no_meta:
    if not d.endswith((".grib2", ".idx")):
        print(f"   - {d}")
print(f"sidecars without a data file: {len(no_data)}")
for m in no_data:
    print(f"   - {m}")

print("\n=== 3. gitignored core GRIB cache, data/raw/grib/ (sessions 37 and 40) ===")
g = "data/raw/grib"
files = os.listdir(g)
gribs = {f for f in files if f.endswith(".grib2")}
gm = {f for f in files if f.endswith(".grib2.meta.txt")}
print(f".grib2 files: {len(gribs)}, .grib2.meta.txt: {len(gm)}")
print(f"grib2 without sidecar: {len([x for x in gribs if x + '.meta.txt' not in gm])}")
print(f"sidecar without grib2: {len([x for x in gm if x[:-9] not in gribs])}")
for fl in sorted(f for f in files if f.endswith(".csv")):
    with open(os.path.join(g, fl), newline="") as f:
        n = sum(1 for _ in csv.DictReader(f))
    print(f"{fl}: {n} data rows")
print(f"files under data/raw/grib/ tracked in git: {sum(1 for t in tracked if t.startswith('data/raw/grib/'))}")
````

**Raw output** (`/tmp/audit67/check_manifests_output.txt`, 49 lines):

````
=== 1. committed pull manifests ===
manifest                                     rows  stated status counts                  dup_keys
session49_pull_manifest.csv                 19083   19083 {'OK': 19083}                  0
session51_pull_manifest.csv                 19083       - {'OK': 19083}                  0
session53_pull_manifest.csv                 19083       - {'OK': 19083}                  0
session55_pull_manifest.csv                  9542    9542 {'OK': 9542}                   0
session57_pull_manifest.csv                  6361    6361 {'OK': 6361}                   0
session63_moisture_pull_manifest.csv         4380    4380 {'OK': 4380}                   0
session63_pressure_pull_manifest.csv         4380    4380 {'OK': 4380}                   0
session63_radiation_pull_manifest.csv        2190    2190 {'OK': 2190}                   0
session63_upper_air_pull_manifest.csv        4380    4380 {'OK': 4380}                   0

=== 2. D15 sidecars for tracked raw files ===
tracked raw data files: 316, tracked .meta.txt: 300
data files without a .meta.txt sidecar: 16
   data/raw/diagnostics/session36: 1
   data/raw/diagnostics/session37: 1
   data/raw/diagnostics/session47: 2
   data/raw/diagnostics/session49: 1
   data/raw/diagnostics/session51: 1
   data/raw/diagnostics/session53: 2
   data/raw/diagnostics/session55: 2
   data/raw/diagnostics/session57: 2
   data/raw/diagnostics/session63: 4
   - data/raw/diagnostics/session36/session36_grib_vs_openmeteo_comparison.csv
   - data/raw/diagnostics/session37/session37_elevation_correction_params.csv
   - data/raw/diagnostics/session47/session47_availability_map.csv
   - data/raw/diagnostics/session47/session47_precip_rno_spotcheck.csv
   - data/raw/diagnostics/session49/session49_pull_manifest.csv
   - data/raw/diagnostics/session51/session51_pull_manifest.csv
   - data/raw/diagnostics/session53/session53_availability_check.csv
   - data/raw/diagnostics/session53/session53_pull_manifest.csv
   - data/raw/diagnostics/session55/session55_pull_manifest.csv
   - data/raw/diagnostics/session55/session55_window_resolution.csv
   - data/raw/diagnostics/session57/session57_pull_manifest.csv
   - data/raw/diagnostics/session57/session57_window_resolution.csv
   - data/raw/diagnostics/session63/session63_moisture_pull_manifest.csv
   - data/raw/diagnostics/session63/session63_pressure_pull_manifest.csv
   - data/raw/diagnostics/session63/session63_radiation_pull_manifest.csv
   - data/raw/diagnostics/session63/session63_upper_air_pull_manifest.csv
sidecars without a data file: 0

=== 3. gitignored core GRIB cache, data/raw/grib/ (sessions 37 and 40) ===
.grib2 files: 31284, .grib2.meta.txt: 31284
grib2 without sidecar: 0
sidecar without grib2: 0
session37_pull_failures.csv: 24 data rows
session40_pull_failures.csv: 0 data rows
files under data/raw/grib/ tracked in git: 0
````

### 5.5 `check_processed.py` — Step 1.6: processed data shape

````python
#!/usr/bin/env python3
"""Session 67, Step 1.6: shape check of every CSV in data/processed/.
Read-only, standard library only. Counts rows and columns, reports min/max
of every date-like column, duplicate natural-key rows, and all-null columns.
Nothing is scored: no MAE or other metric is computed from any value.
"""
import csv
import glob
import os
import re
from collections import Counter

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}")


def natural_key(cols):
    """The file's natural key, chosen from its own header."""
    if cols[0] == "feature":
        return ["feature"]
    if cols[0] == "level":
        return ["level", "station", "fold", "variant"]
    if cols[:2] == ["feature_set", "fold"]:
        return ["feature_set", "fold"]
    if "rung" in cols:
        return ["station", "feature_set", "fold", "rung"]
    if "variant" in cols:
        return ["station", "fold", "variant"]
    if "fold" in cols:
        return ["station", "fold"]
    if "target_date" in cols:
        k = ["station", "target_date"]
        if "span" in cols:
            k.append("span")
        return k
    return ["station"]


def is_null(v):
    return v is None or v.strip() == "" or v.strip().lower() in ("nan", "none", "null", "na")


print(f"{'file':50s} {'rows':>6s} {'cols':>4s}  date range                 key                          dup_keys  all_null_cols")
issues = []
for path in sorted(glob.glob("data/processed/*.csv")):
    with open(path, newline="") as f:
        rdr = csv.reader(f)
        cols = next(rdr)
        rows = list(rdr)
    bad_width = sum(1 for r in rows if len(r) != len(cols))
    key = natural_key(cols)
    idx = [cols.index(k) for k in key]
    dup = sum(v - 1 for v in Counter(tuple(r[i] for i in idx) for r in rows).values() if v > 1)
    null_cols = [c for j, c in enumerate(cols) if rows and all(is_null(r[j]) for r in rows)]
    dates = []
    for j, c in enumerate(cols):
        if "date" in c or c.endswith(("_start", "_end")):
            vals = [r[j][:10] for r in rows if DATE_RE.match(r[j] or "")]
            dates += vals
    dr = f"{min(dates)}..{max(dates)}" if dates else "(no date column)"
    print(f"{os.path.basename(path):50s} {len(rows):6d} {len(cols):4d}  {dr:26s} {'+'.join(key):28s} {dup:8d}  {null_cols if null_cols else '-'}")
    if bad_width:
        print(f"    !! {bad_width} rows with the wrong number of fields")
    if dup or null_cols or bad_width:
        issues.append(path)
    if "station" in cols:
        st = Counter(r[cols.index("station")] for r in rows)
        print(f"    stations: {dict(sorted(st.items()))}")

print("\nfiles with a duplicate key, an all-null column, or a ragged row:", issues if issues else "none")
````

**Raw output** (`/tmp/audit67/check_processed_output.txt`, 97 lines):

````
file                                                 rows cols  date range                 key                          dup_keys  all_null_cols
grib_features_sealed_window.csv                      1825    9  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
grib_features_sealed_window_drops.csv                   0    3  (no date column)           station+target_date                 0  -
    stations: {}
grib_features_v16_window.csv                         7952    9  2021-03-23..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 1590, 'EGLC': 1591, 'LFPG': 1591, 'RNO': 1590, 'YSDU': 1590}
grib_features_v16_window_drops.csv                      3    3  2022-11-30..2022-12-01     station+target_date                 0  -
    stations: {'DSM': 1, 'RNO': 1, 'YSDU': 1}
grib_vs_openmeteo_cloudwind_validation.csv           2800    6  2024-01-19..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 560, 'EGLC': 560, 'LFPG': 560, 'RNO': 560, 'YSDU': 560}
session38_cv_summary.csv                                5   13  (no date column)           station                             0  -
    stations: {'DSM': 1, 'EGLC': 1, 'LFPG': 1, 'RNO': 1, 'YSDU': 1}
session38_joined.csv                                 7928    8  2021-03-24..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 1590, 'EGLC': 1589, 'LFPG': 1589, 'RNO': 1587, 'YSDU': 1573}
session40_sealed_test_summary.csv                       5   10  (no date column)           station                             0  -
    stations: {'DSM': 1, 'EGLC': 1, 'LFPG': 1, 'RNO': 1, 'YSDU': 1}
session46_backtest_profile.csv                        150   16  2021-03-24..2026-07-31     station+feature_set+fold+rung        0  -
    stations: {'DSM': 30, 'EGLC': 30, 'LFPG': 30, 'RNO': 30, 'YSDU': 30}
session46_fold_table.csv                               50   11  2021-03-24..2026-07-31     feature_set+fold                   40  -
session49_sealed_window_with_upper_air.csv           1825   14  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session49_upper_air_join_drops.csv                      0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session49_v16_window_with_upper_air.csv              6127   14  2021-03-23..2024-07-31     station+target_date                 0  -
    stations: {'DSM': 1225, 'EGLC': 1226, 'LFPG': 1226, 'RNO': 1225, 'YSDU': 1225}
session50_e1_experiment_grid.csv                       60   10  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 12, 'EGLC': 12, 'LFPG': 12, 'RNO': 12, 'YSDU': 12}
session50_e1_experiment_summary.csv                    36    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 16, 'DSM': 4, 'EGLC': 4, 'LFPG': 4, 'RNO': 4, 'YSDU': 4}
session51_moisture_join_drops.csv                       0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session51_sealed_window_with_moisture.csv            1825   14  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session51_v16_window_with_moisture.csv               6127   14  2021-03-23..2024-07-31     station+target_date                 0  -
    stations: {'DSM': 1225, 'EGLC': 1226, 'LFPG': 1226, 'RNO': 1225, 'YSDU': 1225}
session52_e2_experiment_grid.csv                       60   10  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 12, 'EGLC': 12, 'LFPG': 12, 'RNO': 12, 'YSDU': 12}
session52_e2_experiment_summary.csv                    36    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 16, 'DSM': 4, 'EGLC': 4, 'LFPG': 4, 'RNO': 4, 'YSDU': 4}
session53_pressure_join_drops.csv                       0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session53_sealed_window_with_pressure.csv            1825   13  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session53_v16_window_with_pressure.csv               6127   13  2021-03-23..2024-07-31     station+target_date                 0  -
    stations: {'DSM': 1225, 'EGLC': 1226, 'LFPG': 1226, 'RNO': 1225, 'YSDU': 1225}
session54_e3_experiment_grid.csv                       60   10  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 12, 'EGLC': 12, 'LFPG': 12, 'RNO': 12, 'YSDU': 12}
session54_e3_experiment_summary.csv                    36    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 16, 'DSM': 4, 'EGLC': 4, 'LFPG': 4, 'RNO': 4, 'YSDU': 4}
session55_radiation_join_drops.csv                      0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session55_sealed_window_with_radiation.csv           1825   12  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session55_v16_window_with_radiation.csv              6127   12  2021-03-23..2024-07-31     station+target_date                 0  -
    stations: {'DSM': 1225, 'EGLC': 1226, 'LFPG': 1226, 'RNO': 1225, 'YSDU': 1225}
session56_e4_experiment_grid.csv                       60   10  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 12, 'EGLC': 12, 'LFPG': 12, 'RNO': 12, 'YSDU': 12}
session56_e4_experiment_summary.csv                    36    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 16, 'DSM': 4, 'EGLC': 4, 'LFPG': 4, 'RNO': 4, 'YSDU': 4}
session57_precip_join_drops.csv                         0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session57_sealed_window_with_precip.csv              1825   12  2025-07-31..2026-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session57_v16_window_with_precip.csv                 6127   12  2021-03-23..2024-07-31     station+target_date                 0  -
    stations: {'DSM': 1225, 'EGLC': 1226, 'LFPG': 1226, 'RNO': 1225, 'YSDU': 1225}
session58_e5_experiment_grid.csv                       30   10  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 6, 'EGLC': 6, 'LFPG': 6, 'RNO': 6, 'YSDU': 6}
session58_e5_experiment_summary.csv                    18    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 8, 'DSM': 2, 'EGLC': 2, 'LFPG': 2, 'RNO': 2, 'YSDU': 2}
session61_combine_sweep_grid.csv                      210   12  (no date column)           station+fold+variant                0  -
    stations: {'DSM': 42, 'EGLC': 42, 'LFPG': 42, 'RNO': 42, 'YSDU': 42}
session61_combine_sweep_summary.csv                   126    7  (no date column)           level+station+fold+variant          0  -
    stations: {'': 56, 'DSM': 14, 'EGLC': 14, 'LFPG': 14, 'RNO': 14, 'YSDU': 14}
session61_correlation_matrix.csv                        9   10  (no date column)           feature                             0  -
session61_row_cost_guard.csv                           15    6  (no date column)           station+fold                        0  -
    stations: {'DSM': 3, 'EGLC': 3, 'LFPG': 3, 'RNO': 3, 'YSDU': 3}
session63_moisture_join_drops.csv                       0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session63_pressure_join_drops.csv                       0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session63_radiation_join_drops.csv                      0    4  (no date column)           station+target_date+span            0  -
    stations: {}
session63_reserved_confirm_grid.csv                     5    9  (no date column)           station                             0  -
    stations: {'DSM': 1, 'EGLC': 1, 'LFPG': 1, 'RNO': 1, 'YSDU': 1}
session63_reserved_window_with_moisture.csv          1825   14  2024-07-31..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session63_reserved_window_with_pressure.csv          1825   13  2024-07-31..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session63_reserved_window_with_radiation.csv         1825   12  2024-07-31..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session63_reserved_window_with_upper_air.csv         1825   14  2024-07-31..2025-07-31     station+target_date                 0  -
    stations: {'DSM': 365, 'EGLC': 365, 'LFPG': 365, 'RNO': 365, 'YSDU': 365}
session63_upper_air_join_drops.csv                      0    4  (no date column)           station+target_date+span            0  -
    stations: {}

files with a duplicate key, an all-null column, or a ragged row: ['data/processed/session46_fold_table.csv']
````

### 5.6 `check_paths_in_code.py` — Step 2.3: hard-coded paths

````python
#!/usr/bin/env python3
"""Session 67, Step 2.3: hard-coded paths in scripts. Read-only.

(a) absolute paths (/Users/, /home/, /tmp/, /private/, C:\\) in any string;
(b) string constants that name a DIFFERENT session number from the
    script's own (sessionNN / session-NN), with the line of code, and
    whether that line looks like a write target (the OUT_PREFLIGHT pattern).
A line counts as a write target if the name it is assigned to starts with
OUT or ends in _LOG/_CSV/_OUT/_PATH/_TXT and the file is later opened for
writing, or the constant appears inside an open(..., "w"/"a") / write_text /
to_csv / csv.writer call on the same line. Every hit is also listed so it
can be checked by eye.
"""
import ast
import glob
import os
import re

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
ABS_RE = re.compile(r"(/Users/|/home/|/tmp/|/private/|[A-Z]:\\\\)")
SESS_RE = re.compile(r"session[-_]?(\d{2})(?!\d)")


def consts(tree):
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value


print("=== (a) absolute paths in string constants ===")
n_abs = 0
for p in sorted(glob.glob("scripts/*.py")):
    src = open(p, encoding="utf-8").read()
    tree = ast.parse(src)
    for ln, v in consts(tree):
        if ABS_RE.search(v):
            n_abs += 1
            print(f"{p}:{ln}: {v[:120]!r}")
print(f"total: {n_abs}")

print("\n=== (b) constants naming another session's number, with assignment target ===")
for p in sorted(glob.glob("scripts/*.py")):
    own = re.match(r"scripts/session(\d{2})", p).group(1)
    src = open(p, encoding="utf-8").read()
    lines = src.split("\n")
    tree = ast.parse(src)
    # map constant line -> assigned name (top-level or any Assign whose value contains it)
    assigned = {}
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = [t.id for t in targets if isinstance(t, ast.Name)]
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    assigned.setdefault(sub.lineno, names)
    for ln, v in consts(tree):
        for m in SESS_RE.finditer(v):
            if m.group(1) != own and ("." in v or "/" in v) and len(v) < 200:
                names = assigned.get(ln, [])
                code = lines[ln - 1].strip()
                is_out = any(re.match(r"^(OUT|.*_(LOG|OUT|TXT)$)", n) for n in names) or \
                    re.search(r"open\([^)]*[\"'][wa][\"']|write_text|to_csv|csv\.writer", code)
                print(f"{p}:{ln} own={own} names={names or '-'} {'WRITE?' if is_out else 'read '} {v!r}")
                break
````

**Raw output** (`/tmp/audit67/check_paths_in_code_output.txt`, 101 lines, first 12 shown):

````
=== (a) absolute paths in string constants ===
total: 0

=== (b) constants naming another session's number, with assignment target ===
scripts/session05_model.py:124 own=05 names=['PREV_SCRIPT'] read  'session04_model.py'
scripts/session05_model.py:390 own=05 names=- read  '    the session-04 comparison. It changes no calculation.'
scripts/session05_model.py:778 own=05 names=- read  "Session 04's figures are quoted from notes/session-04-check-output.txt"
scripts/session07_test.py:135 own=07 names=['PREV_SCRIPT'] read  'session05_model.py'
scripts/session07_test.py:905 own=07 names=- read  'notes/session-05-check-output.txt and DECISIONS F15.'
scripts/session11_model.py:127 own=11 names=['PREV_SCRIPT'] read  'session05_model.py'
scripts/session11_model.py:917 own=11 names=- read  'quoted from notes/session-05-check-output.txt. The two airports are'
scripts/session13_test.py:149 own=13 names=['PREV_SCRIPT'] read  'session05_model.py'
````

### 5.7 `check_write_targets.py` — Step 2.3: write targets

````python
#!/usr/bin/env python3
"""Session 67, Step 2.3 (part 2): which committed files can each script
overwrite? Read-only.

For each script, find calls that write a file -- open(X, "w"/"a"),
Tee(X), X.write_text(...), X.write_bytes(...) -- and resolve X back to the
string constant(s) of the module-level (or function-level) assignment that
built it. Report: every write target that is a tracked file, whether its
name carries a different session number from the script's own, and every
tracked file that more than one script can write.
"""
import ast
import glob
import os
import re
import subprocess
from collections import defaultdict

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
tracked = set(t for t in subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout.split("\n") if t)
tracked_by_base = defaultdict(list)
for t in tracked:
    tracked_by_base[os.path.basename(t)].append(t)
SESS_RE = re.compile(r"session[-_]?(\d{2})(?!\d)")


def strs(node):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
        elif isinstance(sub, ast.JoinedStr):
            out.append("".join(v.value if isinstance(v, ast.Constant) else "{}" for v in sub.values))
    return out


writers = defaultdict(set)
rows = []
for p in sorted(glob.glob("scripts/*.py")):
    own = re.match(r"scripts/session(\d{2})", p).group(1)
    tree = ast.parse(open(p, encoding="utf-8").read())
    env = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    env.setdefault(t.id, []).extend(strs(node.value))
    targets = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        arg = None
        if isinstance(f, ast.Name) and f.id == "open" and node.args:
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and mode.value[:1] in "wa":
                arg = node.args[0]
        elif isinstance(f, ast.Name) and f.id == "Tee" and node.args:
            arg = node.args[0]
        elif isinstance(f, ast.Attribute) and f.attr in ("write_text", "write_bytes"):
            arg = f.value
        if arg is None:
            continue
        cands = strs(arg)
        for sub in ast.walk(arg):
            if isinstance(sub, ast.Name) and sub.id in env:
                cands += env[sub.id]
        names = [c for c in cands if re.search(r"\.(csv|txt|json|md|grib2)$", c)]
        targets.append((node.lineno, names))
    for ln, names in targets:
        for n in names:
            base = os.path.basename(n)
            hits = tracked_by_base.get(base, [])
            other = [m.group(1) for m in SESS_RE.finditer(base) if m.group(1) != own]
            for h in hits:
                writers[h].add(p)
            if hits or other:
                rows.append((p, ln, base, bool(hits), other))

print("=== write targets that are tracked files, or that name another session ===")
for p, ln, base, is_tracked, other in rows:
    print(f"{p}:{ln}  writes {base}  tracked={'yes' if is_tracked else 'no'}  "
          f"{'OTHER-SESSION ' + ','.join(sorted(set(other))) if other else ''}")

print("\n=== tracked files that more than one script can write ===")
multi = {f: s for f, s in writers.items() if len(s) > 1}
for f, s in sorted(multi.items()):
    print(f"{f}: {sorted(s)}")
if not multi:
    print("(none)")
print(f"\ntracked files writable by some script: {len(writers)}")
````

**Raw output** (`/tmp/audit67/check_write_targets_output.txt`, 98 lines):

````
=== write targets that are tracked files, or that name another session ===
scripts/session04_model.py:633  writes session-04-check-output.txt  tracked=yes  
scripts/session05_model.py:864  writes session-05-check-output.txt  tracked=yes  
scripts/session07_test.py:982  writes session-07-check-output.txt  tracked=yes  
scripts/session11_model.py:996  writes session-11-check-output.txt  tracked=yes  
scripts/session13_test.py:1312  writes session-13-check-output.txt  tracked=yes  
scripts/session16_model.py:1356  writes session-16-check-output.txt  tracked=yes  
scripts/session18_test.py:1573  writes session-18-check-output.txt  tracked=yes  
scripts/session22_model.py:1395  writes session-22-check-output.txt  tracked=yes  
scripts/session24_test.py:1665  writes session-24-check-output.txt  tracked=yes  
scripts/session27_model.py:1526  writes session-27-check-output.txt  tracked=yes  
scripts/session29_test.py:1734  writes session-29-check-output.txt  tracked=yes  
scripts/session32_scout.py:538  writes session-32-check-output.txt  tracked=yes  
scripts/session33_cv.py:583  writes session-33-check-output.txt  tracked=yes  
scripts/session36_validate.py:186  writes session36_grib_vs_openmeteo_comparison.csv  tracked=yes  
scripts/session37_decode.py:216  writes grib_features_v16_window.csv  tracked=yes  
scripts/session37_decode.py:223  writes grib_features_v16_window_drops.csv  tracked=yes  
scripts/session37_decode.py:279  writes grib_vs_openmeteo_cloudwind_validation.csv  tracked=yes  
scripts/session37_elevation_fix.py:246  writes session37_elevation_correction_params.csv  tracked=yes  
scripts/session38_cloud_diagnostic.py:119  writes session-38-cloud-diagnostic-output.txt  tracked=yes  
scripts/session38_cv.py:490  writes session-38-cv-output.txt  tracked=yes  
scripts/session38_cv.py:516  writes session38_cv_summary.csv  tracked=yes  
scripts/session38_join.py:141  writes session-38-join-output.txt  tracked=yes  
scripts/session38_join.py:211  writes session38_joined.csv  tracked=yes  
scripts/session38_sanity.py:150  writes session-38-sanity-output.txt  tracked=yes  
scripts/session39_sealed_test.py:443  writes session40-sealed-test-output.txt  tracked=yes  OTHER-SESSION 40
scripts/session39_sealed_test.py:475  writes session40_sealed_test_summary.csv  tracked=yes  OTHER-SESSION 40
scripts/session40_decode.py:190  writes grib_features_sealed_window.csv  tracked=yes  
scripts/session40_decode.py:197  writes grib_features_sealed_window_drops.csv  tracked=yes  
scripts/session41_verify.py:284  writes session-41-verify-output.txt  tracked=yes  
scripts/session46_backtest.py:427  writes session-46-backtest-output.txt  tracked=yes  
scripts/session46_backtest.py:541  writes session46_backtest_profile.csv  tracked=yes  
scripts/session46_backtest.py:550  writes session46_fold_table.csv  tracked=yes  
scripts/session47_availability_probe.py:332  writes session47_availability_map.csv  tracked=yes  
scripts/session47_availability_probe.py:340  writes session47_precip_rno_spotcheck.csv  tracked=yes  
scripts/session49_upper_air_pull.py:405  writes session49_pull_manifest.csv  tracked=yes  
scripts/session49_upper_air_pull.py:440  writes session49_upper_air_join_drops.csv  tracked=yes  
scripts/session50_e1_experiment.py:421  writes session-50-e1-experiment-output.txt  tracked=yes  
scripts/session50_e1_experiment.py:475  writes session50_e1_experiment_grid.csv  tracked=yes  
scripts/session50_e1_experiment.py:552  writes session50_e1_experiment_summary.csv  tracked=yes  
scripts/session51_moisture_pull.py:531  writes session51_pull_manifest.csv  tracked=yes  
scripts/session51_moisture_pull.py:570  writes session51_moisture_join_drops.csv  tracked=yes  
scripts/session52_e2_experiment.py:479  writes session-52-e2-experiment-output.txt  tracked=yes  
scripts/session52_e2_experiment.py:538  writes session52_e2_experiment_grid.csv  tracked=yes  
scripts/session52_e2_experiment.py:615  writes session52_e2_experiment_summary.csv  tracked=yes  
scripts/session53_pressure_pull.py:304  writes session53_availability_check.csv  tracked=yes  
scripts/session53_pressure_pull.py:485  writes session53_availability_check.csv  tracked=yes  
scripts/session53_pressure_pull.py:671  writes session53_pull_manifest.csv  tracked=yes  
scripts/session53_pressure_pull.py:704  writes session53_pressure_join_drops.csv  tracked=yes  
scripts/session54_e3_experiment.py:432  writes session-54-e3-experiment-output.txt  tracked=yes  
scripts/session54_e3_experiment.py:490  writes session54_e3_experiment_grid.csv  tracked=yes  
scripts/session54_e3_experiment.py:567  writes session54_e3_experiment_summary.csv  tracked=yes  
scripts/session55_radiation_pull.py:368  writes session55_window_resolution.csv  tracked=yes  
scripts/session55_radiation_pull.py:567  writes session55_window_resolution.csv  tracked=yes  
scripts/session55_radiation_pull.py:753  writes session55_pull_manifest.csv  tracked=yes  
scripts/session55_radiation_pull.py:786  writes session55_radiation_join_drops.csv  tracked=yes  
scripts/session56_e4_experiment.py:472  writes session-56-e4-experiment-output.txt  tracked=yes  
scripts/session56_e4_experiment.py:547  writes session56_e4_experiment_grid.csv  tracked=yes  
scripts/session56_e4_experiment.py:626  writes session56_e4_experiment_summary.csv  tracked=yes  
scripts/session57_precip_pull.py:390  writes session57_window_resolution.csv  tracked=yes  
scripts/session57_precip_pull.py:537  writes session57_window_resolution.csv  tracked=yes  
scripts/session57_precip_pull.py:699  writes session57_pull_manifest.csv  tracked=yes  
scripts/session57_precip_pull.py:732  writes session57_precip_join_drops.csv  tracked=yes  
scripts/session58_e5_experiment.py:415  writes session-58-e5-experiment-output.txt  tracked=yes  
scripts/session58_e5_experiment.py:480  writes session58_e5_experiment_grid.csv  tracked=yes  
scripts/session58_e5_experiment.py:559  writes session58_e5_experiment_summary.csv  tracked=yes  
scripts/session61_combine_sweep.py:305  writes session-61-combine-sweep-output.txt  tracked=yes  
scripts/session61_combine_sweep.py:448  writes session61_row_cost_guard.csv  tracked=yes  
scripts/session61_combine_sweep.py:479  writes session61_correlation_matrix.csv  tracked=yes  
scripts/session61_combine_sweep.py:599  writes session61_combine_sweep_grid.csv  tracked=yes  
scripts/session61_combine_sweep.py:655  writes session61_combine_sweep_summary.csv  tracked=yes  
scripts/session62_reserved_confirm.py:410  writes session-62-preflight-output.txt  tracked=yes  
scripts/session62_reserved_confirm.py:722  writes session63_reserved_confirm_grid.csv  tracked=yes  OTHER-SESSION 63
scripts/session63_join_equivalence_check.py:324  writes session63-join-equivalence-check-output.txt  tracked=yes  
scripts/session63_join_equivalence_check.py:62  writes session63_reserved_window_with_moisture.csv  tracked=yes  
scripts/session63_reserved_year_build.py:416  writes session-63-reserved-build-output.txt  tracked=yes  
scripts/session63_reserved_year_build.py:282  writes session63_reserved_window_with_upper_air.csv  tracked=yes  
scripts/session63_reserved_year_build.py:282  writes session63_reserved_window_with_moisture.csv  tracked=yes  
scripts/session63_reserved_year_build.py:282  writes session63_reserved_window_with_pressure.csv  tracked=yes  
scripts/session63_reserved_year_build.py:282  writes session63_reserved_window_with_radiation.csv  tracked=yes  
scripts/session63_reserved_year_build.py:317  writes session63_reserved_window_with_upper_air.csv  tracked=yes  
scripts/session63_reserved_year_build.py:317  writes session63_reserved_window_with_moisture.csv  tracked=yes  
scripts/session63_reserved_year_build.py:317  writes session63_reserved_window_with_pressure.csv  tracked=yes  
scripts/session63_reserved_year_build.py:317  writes session63_reserved_window_with_radiation.csv  tracked=yes  
scripts/session63_reserved_year_build.py:350  writes session63_reserved_window_with_upper_air.csv  tracked=yes  
scripts/session63_reserved_year_build.py:350  writes session63_reserved_window_with_moisture.csv  tracked=yes  
scripts/session63_reserved_year_build.py:350  writes session63_reserved_window_with_pressure.csv  tracked=yes  
scripts/session63_reserved_year_build.py:350  writes session63_reserved_window_with_radiation.csv  tracked=yes  
scripts/session63_reserved_year_build.py:394  writes session63_reserved_window_with_upper_air.csv  tracked=yes  
scripts/session63_reserved_year_build.py:394  writes session63_reserved_window_with_moisture.csv  tracked=yes  
scripts/session63_reserved_year_build.py:394  writes session63_reserved_window_with_pressure.csv  tracked=yes  
scripts/session63_reserved_year_build.py:394  writes session63_reserved_window_with_radiation.csv  tracked=yes  
scripts/session63_wiring_scratch_check.py:183  writes session63-wiring-scratch-check-output.txt  tracked=yes  

=== tracked files that more than one script can write ===
data/processed/session63_reserved_window_with_moisture.csv: ['scripts/session63_join_equivalence_check.py', 'scripts/session63_reserved_year_build.py']

tracked files writable by some script: 76
````

### 5.8 `check_imports.py` — Step 2.4: imports vs requirements

````python
#!/usr/bin/env python3
"""Session 67, Step 2.4: third-party imports vs requirements.txt. Read-only.
Every import in every script is parsed (AST). Standard-library modules are
removed with sys.stdlib_module_names; the project's own sessionNN_* modules
are removed too. What is left is compared with requirements.txt.
"""
import ast
import glob
import os
import re
import sys
from collections import defaultdict

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
IMPORT_NAME_TO_DIST = {"sklearn": "scikit-learn", "gribapi": "eccodes"}

used = defaultdict(set)
for p in sorted(glob.glob("scripts/*.py")):
    tree = ast.parse(open(p, encoding="utf-8").read())
    for node in ast.walk(tree):
        mods = []
        if isinstance(node, ast.Import):
            mods = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            mods = [node.module]
        for m in mods:
            top = m.split(".")[0]
            if top in sys.stdlib_module_names or re.match(r"session\d{2}_", top):
                continue
            used[IMPORT_NAME_TO_DIST.get(top, top)].add(os.path.basename(p))

req = {}
for line in open("requirements.txt"):
    line = line.split("#")[0].strip()
    if line:
        name, _, ver = line.partition("==")
        req[name.strip().lower()] = ver.strip()

print("=== third-party imports found (distribution: scripts) ===")
for d, s in sorted(used.items()):
    print(f"{d}: {len(s)} scripts  {'(in requirements ==' + req[d.lower()] + ')' if d.lower() in req else 'NOT IN requirements.txt'}")
    print(f"    {sorted(s)}")
print("\n=== requirements.txt entries ===")
unpinned = [n for n, v in req.items() if not v]
print(f"{len(req)} entries; unpinned: {unpinned or 'none'}")
never = sorted(n for n in req if n not in {d.lower() for d in used})
print(f"listed but never imported directly by a script: {never}")
print("\nPython version recorded in: ", end="")
hits = [f for f in ["requirements.txt", ".python-version", "pyproject.toml", "runtime.txt", "setup.cfg"] if os.path.exists(f)]
print(hits)
````

**Raw output** (`/tmp/audit67/check_imports_output.txt`, 15 lines):

````
=== third-party imports found (distribution: scripts) ===
eccodes: 10 scripts  (in requirements ==2.48.0)
    ['session36_validate.py', 'session37_decode.py', 'session37_elevation_fix.py', 'session40_decode.py', 'session47_availability_probe.py', 'session49_upper_air_pull.py', 'session51_moisture_pull.py', 'session53_pressure_pull.py', 'session55_radiation_pull.py', 'session57_precip_pull.py']
lightgbm: 24 scripts  (in requirements ==4.7.0)
    ['session04_model.py', 'session05_model.py', 'session07_test.py', 'session11_model.py', 'session13_test.py', 'session16_model.py', 'session18_test.py', 'session22_model.py', 'session24_test.py', 'session27_model.py', 'session29_test.py', 'session32_scout.py', 'session33_cv.py', 'session38_cv.py', 'session39_sealed_test.py', 'session42_scoring_check.py', 'session46_backtest.py', 'session50_e1_experiment.py', 'session52_e2_experiment.py', 'session54_e3_experiment.py', 'session56_e4_experiment.py', 'session58_e5_experiment.py', 'session61_combine_sweep.py', 'session62_reserved_confirm.py']
numpy: 24 scripts  (in requirements ==2.5.2)
    ['session04_model.py', 'session05_model.py', 'session07_test.py', 'session11_model.py', 'session13_test.py', 'session16_model.py', 'session18_test.py', 'session22_model.py', 'session24_test.py', 'session27_model.py', 'session29_test.py', 'session32_scout.py', 'session33_cv.py', 'session38_cv.py', 'session39_sealed_test.py', 'session42_scoring_check.py', 'session46_backtest.py', 'session50_e1_experiment.py', 'session52_e2_experiment.py', 'session54_e3_experiment.py', 'session56_e4_experiment.py', 'session58_e5_experiment.py', 'session61_combine_sweep.py', 'session62_reserved_confirm.py']
requests: 8 scripts  (in requirements ==2.34.2)
    ['session37_grib_pull.py', 'session40_grib_pull.py', 'session47_availability_probe.py', 'session49_upper_air_pull.py', 'session51_moisture_pull.py', 'session53_pressure_pull.py', 'session55_radiation_pull.py', 'session57_precip_pull.py']

=== requirements.txt entries ===
19 entries; unpinned: none
listed but never imported directly by a script: ['attrs', 'certifi', 'cffi', 'charset-normalizer', 'eccodeslib', 'eckitlib', 'findlibs', 'idna', 'joblib', 'narwhals', 'pycparser', 'scikit-learn', 'scipy', 'threadpoolctl', 'urllib3']

Python version recorded in: ['requirements.txt']
````

### 5.9 `check_functions.py` — Step 2.5: duplicated and drifting functions

````python
#!/usr/bin/env python3
"""Session 67, Step 2.5: duplicated and drifting function definitions.
Read-only.

Every top-level function (and every method, as Class.method) in every
script is parsed. A body is compared by its AST dump with the docstring
removed, so comments, blank lines and docstrings do not count as a
difference; a changed constant, name or statement does.

Reports:
 (1) bodies identical in 3+ scripts (duplication);
 (2) names defined in 2+ scripts with 2+ different bodies (drift), with the
     core-risk names (load/pair/join/persist/split/fold/fit/train/score/mae/
     predict/obs/guard) listed first, and each variant's scripts.
"""
import ast
import glob
import hashlib
import os
import re
from collections import defaultdict

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
RISK_RE = re.compile(r"load|pair|join|persist|split|fold|fit|train|score|mae|predict|obs|guard|assert|season|feature", re.I)


def body_key(fn):
    body = fn.body
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant) \
            and isinstance(body[0].value.value, str):
        body = body[1:]
    sig = ast.dump(fn.args, annotate_fields=False)
    dump = sig + "|" + "".join(ast.dump(s, annotate_fields=False) for s in body)
    return hashlib.sha1(dump.encode()).hexdigest()[:10], len(body)


defs = defaultdict(lambda: defaultdict(list))  # name -> hash -> [script]
for p in sorted(glob.glob("scripts/*.py")):
    tree = ast.parse(open(p, encoding="utf-8").read())
    base = os.path.basename(p)[:-3]
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            h, n = body_key(node)
            defs[node.name][h].append((base, node.lineno, n))
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    h, n = body_key(sub)
                    defs[f"{node.name}.{sub.name}"][h].append((base, sub.lineno, n))

print("=== (1) identical bodies in 3+ scripts (duplication) ===")
dup_count = 0
for name in sorted(defs):
    for h, where in defs[name].items():
        if len(where) >= 3:
            dup_count += 1
            print(f"{name} [{h}] x{len(where)}: {', '.join(w[0] for w in where)}")
print(f"total duplicated (name, body) groups: {dup_count}")

print("\n=== (2) same name, different bodies across 2+ scripts (drift) ===")
drift = {n: v for n, v in defs.items() if len(v) > 1 and sum(len(w) for w in v.values()) > 1}
risk = sorted(n for n in drift if RISK_RE.search(n))
other = sorted(n for n in drift if not RISK_RE.search(n))
print(f"drifting names: {len(drift)} ({len(risk)} with a core-risk word, {len(other)} other)")
for group, names in (("core-risk names", risk), ("other names", other)):
    print(f"\n--- {group} ---")
    for n in names:
        vs = drift[n]
        print(f"{n}: {len(vs)} variants across {sum(len(w) for w in vs.values())} scripts")
        for h, where in sorted(vs.items(), key=lambda kv: kv[1][0][0]):
            print(f"    [{h}] {', '.join(f'{w[0]}:{w[1]}' for w in where)}")
````

**Raw output** (`/tmp/audit67/check_functions_output.txt`, 425 lines, first 175 shown):

````
=== (1) identical bodies in 3+ scripts (duplication) ===
Tee.__init__ [28dbd5afd8] x30: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cloud_diagnostic, session38_cv, session38_join, session38_sanity, session39_sealed_test, session41_verify, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm, session63_join_equivalence_check, session63_reserved_year_build, session63_wiring_scratch_check
Tee.flush [c5fa78043d] x30: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cloud_diagnostic, session38_cv, session38_join, session38_sanity, session39_sealed_test, session41_verify, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm, session63_join_equivalence_check, session63_reserved_year_build, session63_wiring_scratch_check
Tee.write [0c900a7c8f] x30: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cloud_diagnostic, session38_cv, session38_join, session38_sanity, session39_sealed_test, session41_verify, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm, session63_join_equivalence_check, session63_reserved_year_build, session63_wiring_scratch_check
_get_with_retries [4616754208] x7: session37_grib_pull, session40_grib_pull, session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session55_radiation_pull, session57_precip_pull
_literal [f152a4a3db] x10: session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
all_days [2d126f40af] x21: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_join, session39_sealed_test, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment
bilinear_from_gid [ea8bfe1d2b] x5: session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session55_radiation_pull, session57_precip_pull
build_combos [44e338d111] x4: session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session57_precip_pull
climatology_from_inner [6c8d269d5b] x6: session04_model, session05_model, session11_model, session16_model, session22_model, session27_model
climatology_from_training [098128deeb] x5: session07_test, session13_test, session18_test, session24_test, session29_test
cycle_and_lead [e8754ad5b5] x13: session36_grib_pull, session36_validate, session37_decode, session37_elevation_fix, session37_grib_pull, session40_decode, session40_grib_pull, session47_availability_probe, session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session55_radiation_pull, session57_precip_pull
daterange [33d4753033] x3: session37_decode, session40_decode, session51_moisture_pull
decoded_valid_dt [77790633f9] x3: session53_pressure_pull, session55_radiation_pull, session57_precip_pull
describe [2c66db2677] x11: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
expected_hours [59b54c11e8] x5: session03_checks, session10_checks, session15_checks, session20_checks, session26_checks
expected_valid_dt [ce22bb7169] x3: session53_pressure_pull, session55_radiation_pull, session57_precip_pull
features [300ed55ecc] x11: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
features_3 [300ed55ecc] x5: session32_scout, session33_cv, session38_cv, session39_sealed_test, session46_backtest
features_5 [f1a9de8a48] x5: session32_scout, session33_cv, session38_cv, session39_sealed_test, session46_backtest
features_matrix [70ad046fa6] x7: session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm
find_message_range [09930a0299] x5: session37_grib_pull, session40_grib_pull, session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull
forecast_url [f8d9b7926a] x3: session15_pull, session20_pull, session26_pull
func_code_shape [7fa31b7282] x6: session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
func_source [4d14028696] x10: session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
gap_runs [33ce809754] x5: session03_checks, session10_checks, session15_checks, session20_checks, session26_checks
grib_base_url [2b08b81b16] x8: session37_grib_pull, session40_grib_pull, session47_availability_probe, session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session55_radiation_pull, session57_precip_pull
km_between [63bd763dab] x4: session08_checks, session14_checks, session19_checks, session25_checks
line [e067f2e9ed] x16: session03_checks, session04_model, session05_model, session07_test, session10_checks, session11_model, session13_test, session15_checks, session16_model, session18_test, session20_checks, session22_model, session24_test, session26_checks, session27_model, session29_test
line [93b002a98b] x4: session08_checks, session14_checks, session19_checks, session25_checks
line [10b711b6d5] x14: session31_checks, session32_scout, session33_cv, session38_cloud_diagnostic, session38_cv, session38_join, session38_sanity, session39_sealed_test, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment
line [15ee137800] x5: session61_combine_sweep, session62_reserved_confirm, session63_join_equivalence_check, session63_reserved_year_build, session63_wiring_scratch_check
load_elevation_corrections [4c45ac0105] x3: session49_upper_air_pull, session50_e1_experiment, session51_moisture_pull
load_existing_dates [45289698e5] x5: session49_upper_air_pull, session51_moisture_pull, session53_pressure_pull, session55_radiation_pull, session57_precip_pull
load_forecast [fa518735c0] x4: session10_checks, session15_checks, session20_checks, session26_checks
load_forecast_target_hour [1bfedd8982] x3: session16_model, session22_model, session27_model
load_forecast_target_hour [25ac0ce9e0] x3: session18_test, session24_test, session29_test
load_obs_all [e5afea2e3a] x7: session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm
load_obs_target_hour [f62cebf198] x3: session16_model, session22_model, session27_model
load_obs_target_hour [2094ce4a80] x3: session18_test, session24_test, session29_test
mae [a988d60128] x15: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cv, session39_sealed_test
mae [41aeff3ec3] x8: session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm
minutes_from_nearest_hour [e015a9d702] x4: session08_checks, session14_checks, session19_checks, session25_checks
nearest_hour [ea9709df4d] x4: session15_checks, session20_checks, session25_checks, session26_checks
now_stamps [a11c5f8e00] x10: session03_pull, session10_pull, session14_pull, session15_pull, session19_pull, session20_pull, session25_pull, session26_pull, session31_pull, session32_pull
print_runs [f0840adb7b] x4: session10_checks, session15_checks, session20_checks, session26_checks
read_forecast [35c458d13e] x5: session01_checks, session08_checks, session14_checks, session19_checks, session25_checks
read_obs [2ec3647644] x3: session14_checks, session19_checks, session25_checks
run_fold [1d4bed0892] x3: session50_e1_experiment, session56_e4_experiment, session58_e5_experiment
sanity_check_guard [ef06e17994] x5: session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment
save [ef8dfa4346] x4: session14_pull, session19_pull, session25_pull, session31_pull
size_summary [7373d4f3bc] x5: session03_checks, session10_checks, session15_checks, session20_checks, session26_checks
station_position [d5bf93136b] x4: session08_checks, session14_checks, session19_checks, session25_checks
sub [05f022db63] x30: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cloud_diagnostic, session38_cv, session38_join, session38_sanity, session39_sealed_test, session41_verify, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm, session63_join_equivalence_check, session63_reserved_year_build, session63_wiring_scratch_check
top_level [fa4ed53a60] x10: session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test
window_split [94129f6d2f] x5: session03_checks, session10_checks, session15_checks, session20_checks, session26_checks
write_once [8129af39e4] x10: session03_pull, session10_pull, session14_pull, session15_pull, session19_pull, session20_pull, session25_pull, session26_pull, session31_pull, session32_pull
year_fraction [a3c5d30e67] x23: session04_model, session05_model, session07_test, session11_model, session13_test, session16_model, session18_test, session22_model, session24_test, session27_model, session29_test, session32_scout, session33_cv, session38_cv, session39_sealed_test, session46_backtest, session50_e1_experiment, session52_e2_experiment, session54_e3_experiment, session56_e4_experiment, session58_e5_experiment, session61_combine_sweep, session62_reserved_confirm
total duplicated (name, body) groups: 57

=== (2) same name, different bodies across 2+ scripts (drift) ===
drifting names: 64 (26 with a core-risk word, 38 other)

--- core-risk names ---
build_joined: 5 variants across 5 scripts
    [6f5dc2b605] session49_upper_air_pull:276
    [de6530f175] session51_moisture_pull:285
    [511dbe70a3] session53_pressure_pull:452
    [45b70e3c4a] session55_radiation_pull:517
    [1855df4bba] session57_precip_pull:504
fit_on_training: 5 variants across 5 scripts
    [6b194cd0e1] session07_test:663
    [a89a8c16d3] session13_test:868
    [b39bd98ebf] session18_test:1001
    [0bfdec3fb5] session24_test:1065
    [9d5415d3f1] session29_test:1095
join: 10 variants across 11 scripts
    [525db48cdf] session04_model:256, session05_model:396
    [b9e4a32f91] session07_test:503
    [6675c275f3] session11_model:442
    [3d6d0c2376] session13_test:632
    [6510eea5b5] session16_model:623
    [7e7a5b8865] session18_test:742
    [9121240ffe] session22_model:634
    [261f2661ea] session24_test:793
    [a75c0be5c3] session27_model:693
    [afa7217508] session29_test:826
join_airport: 2 variants across 2 scripts
    [d5ad3af88e] session32_scout:284
    [4734a94349] session33_cv:297
join_rows: 6 variants across 7 scripts
    [87684ecc58] session39_sealed_test:289, session46_backtest:302
    [2a0ecf1272] session50_e1_experiment:325
    [4b9f053e11] session52_e2_experiment:376
    [b4a874874f] session54_e3_experiment:330
    [3cfe7bb648] session56_e4_experiment:376
    [5acb606e1f] session58_e5_experiment:320
load_cloud_wind: 2 variants across 2 scripts
    [78c0483089] session32_scout:191
    [8b8068b2fa] session33_cv:204
load_elevation_corrections: 2 variants across 5 scripts
    [8ab1429cec] session37_decode:71, session40_decode:55
    [4c45ac0105] session49_upper_air_pull:189, session50_e1_experiment:193, session51_moisture_pull:196
load_family: 2 variants across 2 scripts
    [06829d4e88] session62_reserved_confirm:249
    [d2e24a23bb] session63_wiring_scratch_check:102
load_forecast: 2 variants across 5 scripts
    [4fb7f3edfe] session03_checks:114
    [fa518735c0] session10_checks:178, session15_checks:286, session20_checks:186, session26_checks:239
load_forecast_12z: 4 variants across 5 scripts
    [c4bb760f54] session04_model:137, session05_model:181
    [1239b99992] session07_test:226
    [1bfedd8982] session11_model:212
    [25ac0ce9e0] session13_test:289
load_forecast_target_hour: 2 variants across 6 scripts
    [1bfedd8982] session16_model:282, session22_model:336, session27_model:396
    [25ac0ce9e0] session18_test:338, session24_test:397, session29_test:433
load_forecast_temp: 2 variants across 2 scripts
    [82725e4f23] session32_scout:170
    [bec4cd5f2f] session33_cv:183
load_grib_features: 3 variants across 3 scripts
    [5016f05500] session38_join:80
    [d4d79f2731] session39_sealed_test:212
    [7703b955f8] session46_backtest:223
load_joined: 2 variants across 2 scripts
    [590115cc73] session38_cv:177
    [4958e337c6] session38_sanity:135
load_obs: 6 variants across 8 scripts
    [d2fae50581] session03_checks:213
    [632a5c41f7] session10_checks:302
    [a3400808e0] session15_checks:437
    [a1fe3b1f2d] session20_checks:333, session26_checks:388
    [1989716be1] session32_scout:213
    [0aeebcc668] session33_cv:226, session38_join:99
load_obs_12z: 4 variants across 5 scripts
    [b719855b78] session04_model:159, session05_model:203
    [4db9aedecf] session07_test:254
    [9a050f7009] session11_model:234
    [45da6874e9] session13_test:317
load_obs_all: 4 variants across 10 scripts
    [02fdf30a09] session38_cv:198
    [32f6dc3790] session39_sealed_test:250
    [0e791f64cd] session46_backtest:263
    [e5afea2e3a] session50_e1_experiment:290, session52_e2_experiment:341, session54_e3_experiment:295, session56_e4_experiment:341, session58_e5_experiment:285, session61_combine_sweep:273, session62_reserved_confirm:321
load_obs_target_hour: 2 variants across 6 scripts
    [f62cebf198] session16_model:304, session22_model:358, session27_model:418
    [2094ce4a80] session18_test:366, session24_test:425, session29_test:461
mae: 3 variants across 24 scripts
    [a988d60128] session04_model:235, session05_model:279, session07_test:330, session11_model:316, session13_test:410, session16_model:428, session18_test:456, session22_model:443, session24_test:515, session27_model:503, session29_test:551, session32_scout:278, session33_cv:291, session38_cv:248, session39_sealed_test:206
    [43e96b12e5] session38_sanity:109
    [41aeff3ec3] session46_backtest:209, session50_e1_experiment:187, session52_e2_experiment:204, session54_e3_experiment:201, session56_e4_experiment:217, session58_e5_experiment:187, session61_combine_sweep:205, session62_reserved_confirm:243
make_feature_vector: 7 variants across 7 scripts
    [ae26596ecf] session50_e1_experiment:167
    [5c312eb171] session52_e2_experiment:184
    [8afa173e5e] session54_e3_experiment:182
    [9924a81bc7] session56_e4_experiment:198
    [5193b95255] session58_e5_experiment:170
    [2836c6d68b] session61_combine_sweep:182
    [2254186f39] session62_reserved_confirm:223
obs_checks: 5 variants across 5 scripts
    [4d4d7bcf5b] session03_checks:258
    [783e9b448c] session10_checks:354
    [7b3c1fab05] session15_checks:543
    [383f55813b] session20_checks:419
    [7493f6bfab] session26_checks:485
obs_gaps: 5 variants across 5 scripts
    [d0351f86be] session01_checks:77
    [6cbe1b1e91] session08_checks:133
    [2f6c0ca383] session14_checks:162
    [869134ec19] session19_checks:212
    [e04f5aaba4] session25_checks:216
pull_obs: 8 variants across 8 scripts
    [397612d8c8] session03_pull:172
    [5333e6684c] session10_pull:189
    [3597cb033c] session14_pull:252
````

### 5.10 `diff_functions.py` — Step 2.5 helper: diff a drifting function's variants

````python
#!/usr/bin/env python3
"""Session 67, Step 2.5 helper: show how each variant of a drifting function
differs from the previous variant (in script order). Bodies are compared as
ast.unparse() output with the docstring removed, so comments and docstrings
never show up as a difference. Read-only.
Usage: diff_functions.py [--noprint] NAME [NAME ...]
--noprint drops every bare call to print/line/sub/tee (report text only)
before comparing, so only logic differences remain.
"""
import ast
import difflib
import glob
import os
import sys

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)


NOPRINT = "--noprint" in sys.argv


class _StripPrints(ast.NodeTransformer):
    def visit_Expr(self, node):
        c = node.value
        if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in ("print", "line", "sub", "tee"):
            return None
        return node


def find(name):
    out = []
    for p in sorted(glob.glob("scripts/*.py")):
        tree = ast.parse(open(p, encoding="utf-8").read())
        nodes = list(tree.body)
        for c in tree.body:
            if isinstance(c, ast.ClassDef):
                nodes += [s for s in c.body]
        for node in nodes:
            if isinstance(node, ast.FunctionDef) and node.name == name:
                b = node.body
                if b and isinstance(b[0], ast.Expr) and isinstance(getattr(b[0], "value", None), ast.Constant) \
                        and isinstance(b[0].value.value, str):
                    node.body = b[1:] or [ast.Pass()]
                if NOPRINT:
                    node = ast.fix_missing_locations(_StripPrints().visit(node))
                out.append((os.path.basename(p), node.lineno, ast.unparse(node)))
    return out


for name in [a for a in sys.argv[1:] if not a.startswith("--")]:
    variants = find(name)
    print(f"\n################ {name} ({len(variants)} definitions) ################")
    seen = {}
    prev = None
    for script, ln, src in variants:
        if src in seen:
            print(f"== {script}:{ln} identical to {seen[src]}")
            continue
        seen[src] = f"{script}:{ln}"
        if prev is None:
            print(f"== {script}:{ln} (first variant, {len(src.splitlines())} lines)")
        else:
            d = list(difflib.unified_diff(prev[2].splitlines(), src.splitlines(),
                                          f"{prev[0]}:{prev[1]}", f"{script}:{ln}", n=0, lineterm=""))
            print(f"== {script}:{ln} vs {prev[0]}:{prev[1]}  ({len(d)} diff lines)")
            for line in d[:60]:
                print("   " + line[:220])
            if len(d) > 60:
                print(f"   ... ({len(d) - 60} more)")
        prev = (script, ln, src)
````

### 5.11 `diff_subset.py` — Step 2.5 helper: diff across a chosen subset of scripts

````python
#!/usr/bin/env python3
"""Session 67 helper: diff one function across a chosen subset of scripts
(print/line/sub calls stripped, docstrings dropped). Read-only.
Usage: diff_subset.py NAME script1 script2 ...  (script names without .py)"""
import sys, difflib
sys.argv.insert(1, "--noprint")
name, scripts = sys.argv[2], sys.argv[3:]
sys.argv = [sys.argv[0], "--noprint"]
import importlib.util
spec = importlib.util.spec_from_file_location("df", "/tmp/audit67/diff_functions.py")
df = importlib.util.module_from_spec(spec); spec.loader.exec_module(df)
vs = [v for v in df.find(name) if v[0][:-3] in scripts]
for a, b in zip(vs, vs[1:]):
    d = [l for l in difflib.unified_diff(a[2].splitlines(), b[2].splitlines(), a[0], b[0], n=0, lineterm="")]
    print(f"== {a[0]} -> {b[0]}: {len(d)} diff lines")
    for l in d[2:]:
        print("   " + l[:200])
````

### 5.12 `check_pairing_ties.py` — Step 2.5 follow-up: pairing ties

````python
#!/usr/bin/env python3
"""Session 67, Step 2.5 follow-up: how often does the D14 pairing code's
"last report in the file wins" behaviour differ from SPEC 4.5's "nearest
routine report"? Read-only, counts only -- no forecast is read, nothing is
scored.

Reproduces the loop shared by load_obs_all (sessions 39-62) and
load_obs_target_hour (sessions 16-29): round each routine report to its
nearest whole hour, keep it if that hour is the airport's target hour and
it is within 15 minutes and has a usable tmpc; later rows overwrite earlier
ones. For each (station, date) with 2+ kept reports, report whether the
kept (last) one is also the nearest, and whether the temperatures differ.
"""
import csv
import glob
import os
from datetime import datetime, timedelta

ROOT = "/Users/zacharyadams/Coding Projects/MLwx"
os.chdir(ROOT)
AIRPORTS = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20}
CHUNKS = [("2021-03-24", "2021-12-31"), ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"),
          ("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]

for st, hr in AIRPORTS.items():
    kept = {}
    for a, b in CHUNKS:
        path = f"data/raw/iem_asos_{st}_{a}_{b}_routine.csv"
        with open(path) as f:
            for r in csv.DictReader(f):
                t = datetime.strptime(r["valid"], "%Y-%m-%d %H:%M")
                nearest = (t + timedelta(minutes=30)).replace(minute=0, second=0, microsecond=0)
                if nearest.hour != hr:
                    continue
                if abs((t - nearest).total_seconds()) > 15 * 60:
                    continue
                raw = (r.get("tmpc") or "").strip()
                if raw in ("M", "", "T", "None"):
                    continue
                kept.setdefault(nearest.date(), []).append((t, nearest, float(raw)))
    multi = {d: v for d, v in kept.items() if len(v) > 1}
    last_not_nearest = []
    temp_differs = 0
    for d, v in sorted(multi.items()):
        last = v[-1]
        best = min(v, key=lambda x: abs((x[0] - x[1]).total_seconds()))
        if len({x[2] for x in v}) > 1:
            temp_differs += 1
        if abs((last[0] - last[1]).total_seconds()) > abs((best[0] - best[1]).total_seconds()):
            last_not_nearest.append((d, [(x[0].strftime('%H:%M'), x[2]) for x in v]))
    print(f"{st}: paired days {len(kept)}, days with 2+ usable reports within 15 min: {len(multi)}, "
          f"of which temps differ: {temp_differs}, last-in-file is NOT the nearest: {len(last_not_nearest)}")
    for d, v in last_not_nearest:
        print(f"    {d} {v}")
````

**Raw output** (`/tmp/audit67/check_pairing_ties_output.txt`, 5 lines):

````
EGLC: paired days 1953, days with 2+ usable reports within 15 min: 0, of which temps differ: 0, last-in-file is NOT the nearest: 0
LFPG: paired days 1953, days with 2+ usable reports within 15 min: 0, of which temps differ: 0, last-in-file is NOT the nearest: 0
DSM: paired days 1956, days with 2+ usable reports within 15 min: 0, of which temps differ: 0, last-in-file is NOT the nearest: 0
YSDU: paired days 1930, days with 2+ usable reports within 15 min: 1, of which temps differ: 0, last-in-file is NOT the nearest: 0
RNO: paired days 1953, days with 2+ usable reports within 15 min: 0, of which temps differ: 0, last-in-file is NOT the nearest: 0
````

### 5.13 `compare_f109.py` — Step 3.4: compare preflight dry-run with F109

````python
#!/usr/bin/env python3
"""Session 67, Step 3.4: compare the clone's preflight 2023-24 dry-run table
with F109's recorded table (typed in from DECISIONS-archive.md:13521-13535,
session-64 rows, identical to sessions 61 and 62). Exact match at 4 dp."""
import re
f109 = {"EGLC": (1.0148, 2.0164, 0.9470, 0.8715, 7.98, 859, 366, 0),
        "LFPG": (1.2234, 2.3689, 1.1606, 1.1221, 3.31, 858, 366, 0),
        "DSM":  (2.0349, 3.6992, 1.5787, 1.4883, 5.73, 859, 366, 0),
        "YSDU": (1.3283, 2.4417, 1.1264, 1.0949, 2.80, 850, 363, 3),
        "RNO":  (1.4541, 2.5962, 1.2972, 1.1458, 11.67, 857, 365, 1)}
txt = open("/tmp/audit67/step3_preflight_stdout.txt").read()
for st, exp in f109.items():
    m = re.search(rf"{st}\s+n_train=(\d+)\s+n_test=(\d+)\s+no_usable_obs_dropped=\d+\s+no_prev=(\d+)\s+raw=([\d.]+)\s+"
                  rf"persist=([\d.]+)\s+B=([\d.]+)\s+B\+DLRT=([\d.]+)\s+skill_vs_B=\+([\d.]+)%", txt)
    got = (float(m[4]), float(m[5]), float(m[6]), float(m[7]), float(m[8]), int(m[1]), int(m[2]), int(m[3]))
    print(st, "MATCH" if got == exp else f"MISMATCH got={got} exp={exp}")
````

**Raw output** (`/tmp/audit67/compare_f109_output.txt`, 5 lines):

````
EGLC MATCH
LFPG MATCH
DSM MATCH
YSDU MATCH
RNO MATCH
````

### 5.14 `assemble_report.py` — report assembler (builds this file)

````python
#!/usr/bin/env python3
"""Session 67: assemble notes/audit-session-67.md from report_body.md plus
the source of every check script and its raw output (copied verbatim)."""
import os
os.chdir("/tmp/audit67")
out = [open("report_body.md").read()]


def block(lang, text):
    return f"\n````{lang}\n{text.rstrip()}\n````\n"


def src(n, title, f):
    return f"\n### 5.{n} `{f}` — {title}\n" + block("python" if f.endswith(".py") else "bash", open(f).read())


def outp(f, head=None):
    lines = open(f).read().rstrip().split("\n")
    s = f"\n**Raw output** (`/tmp/audit67/{f}`, {len(lines)} lines{', first %d shown' % head if head and len(lines) > head else ''}):\n"
    return s + block("", "\n".join(lines[:head] if head else lines))


sections = [
    ("Steps 0–1.2, 2.1–2.2 and 3: shell commands", "shell_steps.sh", [], None),
    ("Step 1.3: paths named in the docs", "check_doc_paths.py", ["check_doc_paths_output.txt"], None),
    ("Step 1.4: orphans", "check_orphans.py", ["check_orphans_output.txt"], None),
    ("Step 1.5: manifests and provenance", "check_manifests.py", ["check_manifests_output.txt"], None),
    ("Step 1.6: processed data shape", "check_processed.py", ["check_processed_output.txt"], None),
    ("Step 2.3: hard-coded paths", "check_paths_in_code.py", ["check_paths_in_code_output.txt"], 12),
    ("Step 2.3: write targets", "check_write_targets.py", ["check_write_targets_output.txt"], None),
    ("Step 2.4: imports vs requirements", "check_imports.py", ["check_imports_output.txt"], None),
    ("Step 2.5: duplicated and drifting functions", "check_functions.py", ["check_functions_output.txt"], 175),
    ("Step 2.5 helper: diff a drifting function's variants", "diff_functions.py", [], None),
    ("Step 2.5 helper: diff across a chosen subset of scripts", "diff_subset.py", [], None),
    ("Step 2.5 follow-up: pairing ties", "check_pairing_ties.py", ["check_pairing_ties_output.txt"], None),
    ("Step 3.4: compare preflight dry-run with F109", "compare_f109.py", ["compare_f109_output.txt"], None),
    ("report assembler (builds this file)", "assemble_report.py", [], None),
]
for i, (title, f, outs, head) in enumerate(sections, 1):
    out.append(src(i, title, f))
    for o in outs:
        out.append(outp(o, head))

out.append(f"\n### 5.{len(sections) + 1} Other raw outputs\n")
out.append("\n**Step 1.1: 20 largest tracked files** (`sort -rn /tmp/audit67/tracked_sizes.txt | head -20`):\n")
rows = sorted((l.split(" ", 1) for l in open("tracked_sizes.txt").read().strip().split("\n")), key=lambda x: -int(x[0]))[:20]
out.append(block("", "\n".join(f"{int(a):>9d}  {b}" for a, b in rows)))
out.append("\n**Step 1.1: tracked GRIB / idx files by folder:** 94 files, 45.87 MB: session35: 5, session36: 77, session37: 4, session47: 8 (list: `/tmp/audit67/tracked_grib.txt`).\n")
out.append("\n**Step 2.2: ruff statistics** (`ruff_stats.txt`):\n" + block("", open("ruff_stats.txt").read()))
f841 = [l for l in open("ruff_output.txt") if " F841 " in l or " F401 " in l]
out.append("\n**Step 2.2: every F401 and F841, listed for the record** (all 134 findings: `/tmp/audit67/ruff_output.txt`):\n" + block("", "".join(f841)))
out.append("\n**Step 2.5: variant diffs** were produced with `diff_functions.py --noprint NAME` and `diff_subset.py`, and read by hand. The one-line summaries are in section 3 and the Step 2.5 clean check. Full diffs: `/tmp/audit67/diff_A.txt` (mae, load_obs_all, load_grib_features, join_rows), `diff_B.txt` (minimal-method obs/forecast loaders), `diff_C.txt`/`diff_C2.txt` (fit_on_training, score_test_year, with and without print text), `diff_D.txt`/`diff_D2.txt` (minimal-method join), `diff_E.txt` (run_fold, make_feature_vector, load_family, load_elevation_corrections), `diff_F.txt` (older loaders).\n")
out.append("\n**Step 3: install summary** (`step3_pip_install.txt`, last line of the install):\n" + block("", [l for l in open("step3_pip_install.txt") if l.startswith("Successfully installed")][0]))
out.append("\n**Step 3: `pip freeze` in the clone** (`step3_freeze.txt`; compared with the `==` lines of requirements.txt, case-insensitive sort: no difference):\n" + block("", open("step3_freeze.txt").read()))
out.append("\n**Step 3: preflight stdout in the clone** (`step3_preflight_stdout.txt`, full):\n" + block("", open("step3_preflight_stdout.txt").read()))
out.append("""
**Step 3: side effect inside the clone** (`git diff --stat` in `/tmp/audit67/clone`):
```
 notes/session-62-preflight-output.txt | 18 +++++++++---------
 1 file changed, 9 insertions(+), 9 deletions(-)
```
The changed lines are the `run at` timestamp and the eight `rows loaded=` / `of N total` counts (7952 → 9777), the same two kinds of change F109 reports for session 64.
`diff notes/session-64-preflight-output.txt <clone>/notes/session-62-preflight-output.txt` shows only:
```
5c5
< run at   : 2026-09-23 01:13:08 local
---
> run at   : 2026-09-23 11:13:34 local
```
System interpreter check: `python3 -c "import lightgbm"` gives `ModuleNotFoundError: No module named 'lightgbm'`.
""")
open("/Users/zacharyadams/Coding Projects/MLwx/notes/audit-session-67.md", "w").write("".join(out))
````

### 5.15 Other raw outputs

**Step 1.1: 20 largest tracked files** (`sort -rn /tmp/audit67/tracked_sizes.txt | head -20`):

````
  2169066  data/raw/diagnostics/session53/session53_pull_manifest.csv
  2035592  data/raw/diagnostics/session51/session51_pull_manifest.csv
  1545795  data/raw/diagnostics/session49/session49_pull_manifest.csv
   984341  data/raw/diagnostics/session35/ugrd10m_sample.grib2
   961389  data/raw/diagnostics/session35/vgrd10m_sample.grib2
   954267  data/raw/diagnostics/session55/session55_pull_manifest.csv
   884710  data/raw/diagnostics/session36/gfs_20210326_t12z_f024_tmp2m.grib2
   883050  data/raw/diagnostics/session36/gfs_20210326_t18z_f024_tmp2m.grib2
   882745  data/raw/diagnostics/session36/gfs_20210327_t18z_f024_tmp2m.grib2
   881150  data/raw/diagnostics/session36/gfs_20210323_t00z_f026_tmp2m.grib2
   880557  data/raw/diagnostics/session36/gfs_20210326_t18z_f026_tmp2m.grib2
   874274  data/raw/diagnostics/session36/gfs_20210325_t00z_f026_tmp2m.grib2
   873826  data/raw/diagnostics/session36/gfs_20210324_t00z_f026_tmp2m.grib2
   872064  data/raw/diagnostics/session36/gfs_20210327_t00z_f026_tmp2m.grib2
   871542  data/raw/diagnostics/session36/gfs_20210326_t00z_f026_tmp2m.grib2
   829229  data/raw/diagnostics/session35/tcdc_sample.grib2
   787181  DECISIONS-archive.md
   604355  data/raw/diagnostics/session57/session57_pull_manifest.csv
   556927  data/processed/session51_v16_window_with_moisture.csv
   540564  data/processed/session49_v16_window_with_upper_air.csv
````

**Step 1.1: tracked GRIB / idx files by folder:** 94 files, 45.87 MB: session35: 5, session36: 77, session37: 4, session47: 8 (list: `/tmp/audit67/tracked_grib.txt`).

**Step 2.2: ruff statistics** (`ruff_stats.txt`):

````
102	F541	[*] f-string-missing-placeholders
 16	E741	[ ] ambiguous-variable-name
  9	F401	[*] unused-import
  7	F841	[-] unused-variable
Found 134 errors.
[*] 115 fixable with the `--fix` option (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
````

**Step 2.2: every F401 and F841, listed for the record** (all 134 findings: `/tmp/audit67/ruff_output.txt`):

````
scripts/session31_checks.py:13:22: F401 [*] `datetime.datetime` imported but unused
scripts/session31_checks.py:13:32: F401 [*] `datetime.timedelta` imported but unused
scripts/session31_checks.py:203:17: F841 Local variable `any_present` is assigned to but never used
scripts/session31_pull.py:41:8: F401 [*] `json` imported but unused
scripts/session32_scout.py:44:8: F401 [*] `ast` imported but unused
scripts/session36_validate.py:19:8: F401 [*] `math` imported but unused
scripts/session38_cloud_diagnostic.py:243:9: F841 Local variable `extremes` is assigned to but never used
scripts/session38_cv.py:512:5: F841 Local variable `synth` is assigned to but never used
scripts/session48_reserved_year.py:32:28: F401 [*] `datetime.timedelta` imported but unused
scripts/session51_moisture_pull.py:347:29: F841 [*] Local variable `err` is assigned to but never used
scripts/session53_pressure_pull.py:512:29: F841 [*] Local variable `err` is assigned to but never used
scripts/session55_radiation_pull.py:594:29: F841 [*] Local variable `err` is assigned to but never used
scripts/session57_precip_pull.py:564:29: F841 [*] Local variable `err` is assigned to but never used
scripts/session63_join_equivalence_check.py:37:8: F401 [*] `shutil` imported but unused
scripts/session63_join_equivalence_check.py:52:35: F401 [*] `session53_pressure_pull` imported but unused
scripts/session63_join_equivalence_check.py:53:36: F401 [*] `session55_radiation_pull` imported but unused
````

**Step 2.5: variant diffs** were produced with `diff_functions.py --noprint NAME` and `diff_subset.py`, and read by hand. The one-line summaries are in section 3 and the Step 2.5 clean check. Full diffs: `/tmp/audit67/diff_A.txt` (mae, load_obs_all, load_grib_features, join_rows), `diff_B.txt` (minimal-method obs/forecast loaders), `diff_C.txt`/`diff_C2.txt` (fit_on_training, score_test_year, with and without print text), `diff_D.txt`/`diff_D2.txt` (minimal-method join), `diff_E.txt` (run_fold, make_feature_vector, load_family, load_elevation_corrections), `diff_F.txt` (older loaders).

**Step 3: install summary** (`step3_pip_install.txt`, last line of the install):

````
Successfully installed attrs-26.1.0 certifi-2026.7.22 cffi-2.1.1 charset-normalizer-3.5.1 eccodes-2.48.0 eccodeslib-2.48.0.26 eckitlib-2.1.1.26 findlibs-0.1.3 idna-3.19 joblib-1.5.3 lightgbm-4.7.0 narwhals-2.24.0 numpy-2.5.2 pycparser-3.0 requests-2.34.2 scikit-learn-1.9.0 scipy-1.18.0 threadpoolctl-3.6.0 urllib3-2.7.0
````

**Step 3: `pip freeze` in the clone** (`step3_freeze.txt`; compared with the `==` lines of requirements.txt, case-insensitive sort: no difference):

````
attrs==26.1.0
certifi==2026.7.22
cffi==2.1.1
charset-normalizer==3.5.1
eccodes==2.48.0
eccodeslib==2.48.0.26
eckitlib==2.1.1.26
findlibs==0.1.3
idna==3.19
joblib==1.5.3
lightgbm==4.7.0
narwhals==2.24.0
numpy==2.5.2
pycparser==3.0
requests==2.34.2
scikit-learn==1.9.0
scipy==1.18.0
threadpoolctl==3.6.0
urllib3==2.7.0
````

**Step 3: preflight stdout in the clone** (`step3_preflight_stdout.txt`, full):

````

==========================================================================================
SESSION 62 -- reserved-year confirmation LOCK, pre-flight only (DECISIONS D58). No reserved-year row is read anywhere in this function. The confirmation fold is NOT run. No 2024-25 MAE is produced.
==========================================================================================
run at   : 2026-09-23 11:13:34 local
python   : 3.12.2
numpy    : 2.5.2
lightgbm : 4.7.0

FINAL SET (D58, confirming D57/F106's mechanical output): B + D+L+R+T  (i.e. B+D,L,R,T)
FINAL_FEATURE_KEYS = ['temp', 'season_sin', 'season_cos', 'cloud_cover', 'wind_speed_10m', 'dewpoint_depression_t2m_floored', 'lapse_rate_t2_t850', 'dswrf_2h_wm2', 'pressure_tendency_3h_hpa']
P, rh, plev are excluded -- confirmed absent from FAMILY_KEYS and FINAL_CODES above.

==========================================================================================
Header / date checks (session prompt pre-flight item 1)
==========================================================================================
    D    v16_file     session51_v16_window_with_moisture.csv               columns=['dewpoint_depression_t2m'] -- PASS
    D    sealed_file  session51_sealed_window_with_moisture.csv            columns=['dewpoint_depression_t2m'] -- PASS
    L    v16_file     session49_v16_window_with_upper_air.csv              columns=['lapse_rate_t2_t850'] -- PASS
    L    sealed_file  session49_sealed_window_with_upper_air.csv           columns=['lapse_rate_t2_t850'] -- PASS
    R    v16_file     session55_v16_window_with_radiation.csv              columns=['dswrf_2h_wm2'] -- PASS
    R    sealed_file  session55_sealed_window_with_radiation.csv           columns=['dswrf_2h_wm2'] -- PASS
    T    v16_file     session53_v16_window_with_pressure.csv               columns=['pressure_tendency_3h_hpa'] -- PASS
    T    sealed_file  session53_sealed_window_with_pressure.csv            columns=['pressure_tendency_3h_hpa'] -- PASS

    CONFIRMATION_FOLD: train=2021-03-24..2024-07-31  test=2024-08-01..2025-07-31
    Dates match D51's own reserved-year bounds and D58's pinned train/test split exactly -- PASS.

==========================================================================================
Guard check (session prompt pre-flight item 1, mirrors D51's own guard-verification pattern): the guard must PASS the dry-run fold, RAISE on three deliberately reserved-year-touching folds, and the confirmation fold must be proven to be the kind of fold the guard WOULD reject -- which is exactly why it is never given to the guard.
==========================================================================================

-- Positive check -- DRY_RUN_FOLD clears the guard --
    2023-24: train=2021-03-24..2023-07-31  test=2023-08-01..2024-07-31  -- PASS (guard did not raise)

-- Negative check -- three deliberately reserved-year-touching folds must raise --
    hypothetical train-crosses-reserved-year fold: raised as expected -- hypothetical train-crosses-reserved-year fold: training window 2021-03-24..2025-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusing (D51).
    hypothetical test-on-reserved-year fold: raised as expected -- hypothetical test-on-reserved-year fold: test window 2024-08-01..2025-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusing (D51).
    hypothetical train-into-reserved-year fold: raised as expected -- hypothetical train-into-reserved-year fold: training window 2021-03-24..2025-01-01 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusing (D51).

-- Proof the CONFIRMATION_FOLD is a genuine, deliberate reserved-year use -- NOT an oversight -- by showing the guard WOULD reject it too --
    CONFIRMATION_FOLD raised as expected -- 2024-25-confirmation (D51/D58 -- THE ONE AUTHORIZED RESERVED-YEAR USE): test window 2024-08-01..2025-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusing (D51).
    This is exactly why run_confirm() NEVER calls assert_reserved_year_excluded() on CONFIRMATION_FOLD: it is the one, named, D51/D58-authorized exception, proven here to be a genuine reserved-year fold rather than a guard bug or a silent bypass.

==========================================================================================
Column-integrity check (session prompt pre-flight item 2, reusing F106's own check): each of L, D, T, R matches its committed source file exactly, checked over every row of the TRAINING window (2021-03-24..2024-07-31 -- the only span currently available; see the reserved-year data-gap finding below for the test window)
==========================================================================================
    L rows loaded=9777  reserved-year hits=0
    D rows loaded=9777  reserved-year hits=0
    T rows loaded=9777  reserved-year hits=0
    R rows loaded=9777  reserved-year hits=0

    PASS -- 0 reserved-year rows found across all four family source files.

    n_checked (training-window complete-case rows) = 6127
    lapse_rate_t2_t850                     max_abs_diff = 0.000000000
    dewpoint_depression_t2m_floored        max_abs_diff = 0.000000000
    pressure_tendency_3h_hpa               max_abs_diff = 0.000000000
    dswrf_2h_wm2                           max_abs_diff = 0.000000000

    PASS -- every final-set feature column matches its committed source (D floor applied exactly per D53/F100) on every training-window row.
    EGLC   complete-case rows in training window: 1226
    LFPG   complete-case rows in training window: 1226
    DSM    complete-case rows in training window: 1225
    YSDU   complete-case rows in training window: 1225
    RNO    complete-case rows in training window: 1225

==========================================================================================
RESERVED-YEAR FEATURE-DATA GAP -- flagged plainly, not worked around (discovered while building this script, verified directly against every committed file, not assumed)
==========================================================================================
    Checked: do the L, D, T, R committed source files contain ANY row
    whose date falls inside the reserved 2024-08-01..2025-07-31 year?
    L: 0 reserved-year rows found (of 9777 total)
    D: 0 reserved-year rows found (of 9777 total)
    T: 0 reserved-year rows found (of 9777 total)
    R: 0 reserved-year rows found (of 9777 total)

    RESULT: ZERO, at every one of the four families. This is expected
    given how sessions 49/51/53/55 built these files (each deliberately
    excluded the reserved year, per D51's own mandate at the time,
    per F98/F100/F101/F102's own date-range description) -- but it
    means the CONFIRMATION_FOLD's test window (the reserved year) has
    NO L, D, T, or R feature value in any committed file, at any airport.

    CONSEQUENCE: run_confirm() cannot assemble a complete-case feature
    matrix for the test window as things stand -- there is nothing to
    assemble. This is a genuine blocker for session 63 as currently
    scoped ('run the frozen script once, unchanged, on the 2024-25
    fold'), reported here and in DECISIONS D58 for the owner to
    resolve BEFORE session 63 runs -- not silently patched around in
    this script. run_confirm() below contains a hard, loud guard that
    refuses to proceed past row assembly if this gap is still open.

==========================================================================================
Machinery dry-run on the 2023-24 EXPERIMENT_FOLD (session prompt pre-flight item 3) -- already used descriptively by every E-session and by F106 itself, so no new look is spent. Proves the fit/score plumbing end-to-end without touching the reserved year.
==========================================================================================
    EGLC   n_train=859    n_test=366    no_usable_obs_dropped=0    no_prev=0    raw=1.0148  persist=2.0164  B=0.9470  B+DLRT=0.8715  skill_vs_B=+7.98%
    LFPG   n_train=858    n_test=366    no_usable_obs_dropped=0    no_prev=0    raw=1.2234  persist=2.3689  B=1.1606  B+DLRT=1.1221  skill_vs_B=+3.31%
    DSM    n_train=859    n_test=366    no_usable_obs_dropped=0    no_prev=0    raw=2.0349  persist=3.6992  B=1.5787  B+DLRT=1.4883  skill_vs_B=+5.73%
    YSDU   n_train=850    n_test=363    no_usable_obs_dropped=3    no_prev=3    raw=1.3283  persist=2.4417  B=1.1264  B+DLRT=1.0949  skill_vs_B=+2.80%
    RNO    n_train=857    n_test=365    no_usable_obs_dropped=1    no_prev=1    raw=1.4541  persist=2.5962  B=1.2972  B+DLRT=1.1458  skill_vs_B=+11.67%

    Airport-averaged (2023-24 dry run): B=1.2220  B+DLRT=1.1445  skill_vs_B=+6.34%
    This reproduces the same date range already scored descriptively
    in F99-F106 (the '2023-24' EXPERIMENT_FOLD) -- a plumbing check,
    not a new look, and not comparable 1:1 to F106's own B+D,L,R,T
    reading there (F106 pooled across three folds; this is 2023-24 alone).

==========================================================================================
END OF PRE-FLIGHT
==========================================================================================
No row of the reserved 2024-08-01..2025-07-31 confirmation year was
read anywhere in this function. run_confirm() was not called. No
2024-25 MAE was produced. The reserved-year feature-data gap above
is the one open item session 63 must have resolved before it can run.
This output is saved at notes/session-62-preflight-output.txt
````

**Step 3: side effect inside the clone** (`git diff --stat` in `/tmp/audit67/clone`):
```
 notes/session-62-preflight-output.txt | 18 +++++++++---------
 1 file changed, 9 insertions(+), 9 deletions(-)
```
The changed lines are the `run at` timestamp and the eight `rows loaded=` / `of N total` counts (7952 → 9777), the same two kinds of change F109 reports for session 64.
`diff notes/session-64-preflight-output.txt <clone>/notes/session-62-preflight-output.txt` shows only:
```
5c5
< run at   : 2026-09-23 01:13:08 local
---
> run at   : 2026-09-23 11:13:34 local
```
System interpreter check: `python3 -c "import lightgbm"` gives `ModuleNotFoundError: No module named 'lightgbm'`.

---

## 6. Owner review notes (session 67, before commit)

These notes were added at the owner's review, before commit. Sections 1–5
above are unchanged. Nothing here reclassifies a finding; triage happens after
session 68 (D60.1).

**6.1 Binding on session 68.**
- The D60.2 verification recompute of F94 and F109 runs **only in a clean
  clone under `/tmp`, never in the working repo**. The reason is A67-02 and
  A67-03: both frozen scripts (`session39_sealed_test.py`,
  `session62_reserved_confirm.py`) write fixed output paths that are
  committed files, so a run in the working repo would overwrite the
  committed record of F94 and F109.
- Session 68 also reviews **A67-04** (stale preflight printed text),
  **A67-12** (last-wins pairing against SPEC 4.5's "nearest") and **A67-14**
  (`r.get()` in `make_feature_vector`) as part of its logic review.

**6.2 Planning-chat severity views, for triage (not reclassified now).**
- **A67-01 is a candidate for must-fix.** D47 is a rule, and the GRIB
  provenance behind F94 and F109 exists only in a gitignored cache.
- **A67-12 is a candidate for at least should-fix.** It is a disagreement
  between SPEC and code (SPEC 4.5 says "nearest"; the code keeps the last
  qualifying report). CLAUDE.md says such a disagreement must be resolved on
  purpose: fix the code or change SPEC and note it in DECISIONS.

**6.3 Dated `##` headers in the live DECISIONS.md: 14, not 15.**
The count, run at this review:

```
$ grep -c "^## 20" DECISIONS.md
14
```

The 14 headers, in file order (`grep -n "^## " DECISIONS.md`; every `##`
header in the file is dated): lines 14 (2026-08-16), 75 (2026-08-18), 111
(2026-08-19), 125 (2026-08-20), 145 (2026-09-11), 261, 418, 506, 563 (all
2026-09-12), 637 (2026-09-18), 854 (2026-09-19), 945, 1033, 1161 (all
2026-09-23).

Why session 66 said 15 and session 67 said 14. It is **not** a change to the
file between sessions: DECISIONS.md is untouched since commit `6bba07c`
(session 66), and session 66's own last addition, D60 (header at line 1161),
is among the 14. Before D60 the file had 13 (`git show 6bba07c^:DECISIONS.md
| grep -c "^## [0-9]\{4\}-"` gives 13). Session 66's raw output
(`notes/audit-session-66.md`, section 4, "3.3a Dated headers in live
DECISIONS.md") lists the same 14 headers, at the same line numbers, as
above. So the "15" in session 66's clean-check prose (section 3, "All 15
dated `##` section headers") is a miscount in that sentence. Its own raw
output shows 14. The ordering result stands either way: all headers are in
non-decreasing date order. This is recorded here only. Session 66's report
is left as committed, for triage.
