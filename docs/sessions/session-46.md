# Session 46 — multi-year generalisation backtest of the current models (24h lead)

## Where this sits

The GRIB build is closed. This opens the next phase — the rigorous-accuracy route toward the
eventual deliverable — and its first step is **not** a new feature. It is building the **multi-year
generalisation profile** of the models you already have: how consistently do they beat raw GFS
across *different years' weather*, not just the single 2025–26 sealed year? That profile is the
benchmark every future feature experiment will be measured against, and it directly attacks the
project's biggest open weakness (every verdict so far rests on one shared test year, RESULTS §6).

**This is a descriptive measurement, not a new verdict.** It does not re-open, re-litigate, or
overwrite the sealed-test results — F94 (5-feature) and F16–F82 (minimal method) stand exactly as
reported. It uses the models' **existing frozen recipes unchanged** — nothing is tuned, no feature
is added or selected. Kept deliberately tight: **existing pulled GRIB data only (no new pull), 24h
lead only** (+48h is a separate later step, since it needs a fresh pull).

## The integrity boundary — read this first

Reusing all the data (including the sealed year) is legitimate here *only because this is a profile,
not a pass/fail*:
- The models are the **existing frozen 3-feature and 5-feature recipes** (SPEC §7, D48 / D21.4) —
  refit per fold on each fold's own training window, but **nothing about the recipe changes**: same
  features, same LightGBM settings, same elevation constants. There is nothing to tune, so there is
  no way to tune *toward* the sealed year.
- The output is a year-by-year skill *description*, used to understand robustness and to serve as a
  benchmark — **never** to select features, tune hyperparameters, or declare a new pass/fail.
- **Feature *selection* later will still need its own fresh, untouched test year** — this backtest
  does not substitute for that. It measures what exists; it does not license picking a winner on
  reused data.

State this boundary in the finding so a future session cannot mistake the profile for a verdict.

## Standing rules that bind this session (SPEC §2)

- **Existing data only** — reuse the GRIB features already pulled (2021-03-24 → 2026-07-31, sessions
  37 + 40). No new pull. **24h lead only.**
- **GRIB source throughout**, for both models (so 3-vs-5 stays same-source; note the 3-feature here
  is the GRIB 3-feature, not directly comparable to F16–F82's Open-Meteo numbers).
- **Time-ordered folds only** — train strictly on dates *before* the test year; never test on data
  the fold trained on (SPEC 2.1a). No look-ahead.
- **Frozen recipes, refit only.** Same feature sets, same LightGBM settings, same elevation
  constants — refit per fold, tune nothing, select nothing, add nothing.
- **Drop-count-report, never fill.** Report row/drop counts per fold per airport.
- **You never commit.** Prepare changes and a suggested message.

## Reference — the data spans

- **3-feature** (temp + season): the full span, 2021-03-24 → 2026-07-31.
- **5-feature** (+ cloud + wind): only 2024-01-19 → 2026-07-31 — cloud/wind do not exist earlier
  (F85). So the 5-feature backtest is inherently limited to the most recent folds; report that
  honestly rather than papering over it.
- **Test years** follow the project's Aug 1 → Jul 31 convention (matching the sealed year).

---

## Task 1 — build the rolling-origin folds

Use rolling-origin backtesting: walk the train/test cutoff forward one year at a time, always
training on the past and testing on the next year.

- **3-feature folds** (train → test):
  - 2021-03-24→2022-07-31 → test 2022-23
  - 2021-03-24→2023-07-31 → test 2023-24
  - 2021-03-24→2024-07-31 → test 2024-25
  - 2021-03-24→2025-07-31 → test 2025-26  *(this fold's training window equals the sealed-test one,
    so its 2025-26 numbers should ≈ F94's 3-feature column — a built-in consistency check)*
- **5-feature folds** (only where cloud/wind exist for both train and test):
  - 2024-01-19→2024-07-31 → test 2024-25  *(training ~6 months — pathologically thin, the same
    starved slice session 32 saw; report it but flag heavily)*
  - 2024-01-19→2025-07-31 → test 2025-26  *(training ~1.5yr; should ≈ F94's 5-feature column)*

Report the fold table with each fold's **training-window length and row counts**, and flag the thin
folds (2022-23 ~1.3yr; the 5-feature 2024-25 ~6mo) explicitly — a fold on thin training is a weaker
read, not an equal one.

## Task 2 — run each fold

For every fold and airport, refit the model on the fold's training window and evaluate on its test
year. Report per airport per fold: **MAE, RMSE, bias, skill vs raw GFS, skill vs persistence, n
days**, for each applicable rung (raw GFS, persistence, 3-feature; 5-feature where it exists).

## Task 3 — assemble the generalisation profile

A per-airport, per-test-year table — the benchmark. Confirm the 2025-26 fold reproduces F94's
numbers closely (consistency check); flag any material divergence, as it would signal a pipeline
inconsistency rather than a new result.

## Task 4 — read the profile honestly (report, do not decide)

- Does the 3-feature model **consistently** beat raw GFS across the test years, or was any year
  (e.g. the warm 2025–26 European summer, F48) flattering? How large is the year-to-year variance
  per airport?
- Is any airport's skill fragile across years (wins some, loses others)?
- State plainly that the **5-feature multi-year read is limited** — too few feature-complete years
  to claim multi-year robustness yet; that gap only closes with time (or the deep-history route,
  which was GO-COSTLY).
- One-line synthesis of what the profile says about how much to trust the current models across
  years — as a benchmark for the feature work to come, not a verdict.

---

## What NOT to do

- **Do not pull any new data**, and **do not run +48h** — 24h lead only, existing GRIB features only.
- **Do not tune, select features, or change any recipe** — refit the frozen models only.
- **Do not treat this as a sealed test or a new pass/fail**, and do not re-open or restate F94 /
  F16–F82 as changed — the profile is descriptive.
- **Do not test any fold on data it trained on** — strict time ordering.
- **Do not modify `SPEC.md` or `RESULTS.md`** — this is a measurement; folding a benchmark into the
  docs is a later step if it earns it.
- **Do not commit.**
- **Do not exceed scope** — the backtest profile and its honest read, nothing else.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** the fold table (with training sizes + thin-fold flags), the per-airport per-year
   profile (Tasks 2–3), and the honest read (Task 4).
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail, likely **F96**):
   the backtest design, the generalisation profile, the F94 consistency check, and — explicitly —
   the integrity boundary (descriptive profile, not a verdict; feature selection later still needs a
   fresh test year). Flag nothing for decision; this is a measurement.
3. **Refresh STATUS.md** to record session 46 and that the multi-year benchmark now exists.
4. **Save** the profile tables under `data/processed/` (small — no raw).
5. **Archive step (routine):** move any entry that became settled per the criterion (likely none —
   the F94/build entries were handled in session 45; F94 stays live per the owner's call). Check and
   state.
6. **Consistency check:** new DECISIONS number next-sequential and unique; every fold is
   time-ordered (train strictly before test); the 2025-26 folds reproduce F94; nothing was tuned or
   selected; `SPEC.md`/`RESULTS.md` unmodified; `git status` shows only expected files.
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the body,
   `--` not em-dashes, short body — then **stop and wait for the owner's review.**
