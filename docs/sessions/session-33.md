# Session 33 — seasonal cross-validation on the 1.5-year window (sealed year NOT opened)

## Scope — one job, then stop

Answer one question the session-32 scout could not: **with a full seasonal cycle in
the training data, is the ~1.5-year feature-complete window enough — or is a deeper
data source mandatory?** The scout fit on only the ~6-month inner-training slice
(Jan–Jul 2024, no autumn/winter), which starved and seasonally-skewed even the proven
3-feature recipe. This session removes that artifact by using **blocked
cross-validation across the whole 1.5-year window**, so every fold trains on ~15 months
spanning all calendar positions.

This is a **diagnostic inside the training window.** It **locks nothing**, and the
**sealed test year (2025-08-01 → 2026-07-31) is never loaded, pulled, joined, or
scored, for any airport or fold.** The result is a green/red light for two branches,
reported for the owner — not a verdict against the frozen bar.

No new data is pulled: this reuses the cloud/wind raw already saved under
`data/raw/features/` (session 32) plus the existing temperature/observation rows.

## The two branches this answers (report, do not decide)

- **Branch A — is the window adequate?** Trained on a full seasonal cycle, does the
  **3-feature recipe recover to beating raw GFS** across the held-out blocks? If yes,
  ~1.5 years is workable and a short-window richer model is worth locking later. If the
  proven recipe **still** can't beat raw GFS even with full seasonal coverage, the
  window is the binding constraint and a deeper source (a real GFS GRIB archive, **not**
  ERA5 reanalysis, which would leak) is mandatory before anything is locked.
- **Branch B — do the features add real out-of-sample value?** Does the **5-feature
  model beat the 3-feature model** out-of-fold, and beat raw GFS? This firms up the
  scout's 3/5 signal across multiple held-out blocks rather than one.

## Standing rules that bind this session (SPEC §2)

- **The sealed test year is untouched.** Every fold's train and test data lies inside
  2024-01-19 → 2025-07-31. Assert this at every data-load point.
- Forecast source `models=gfs_global`, `previous_day1` offset (D16). Same features.
- **Everything fitted uses that fold's training blocks only** — model and mean-bias
  reference. The held-out block is never in any fit (2.1c).
- **No lagged or recent-observation features.** (Beyond the standing rule, this is what
  makes blocked CV leakage-safe here — see the methodology note below. Do not add any.)
- **No hyperparameter tuning**; locked recipe settings unchanged for both models. **Same
  five features at every airport** — no per-airport selection.
- **Drop-count-report, never fill** (2.2). **Raw is immutable** (2.3) — reuse existing
  raw, write no new raw.
- **You never commit.** Prepare changes and a suggested message for the owner.

## Methodology note — why blocked CV is leakage-safe here (put this in the finding)

Blocked leave-one-block-out CV trains on data temporally *surrounding* each held-out
block, which departs from the strict train-earlier/test-later split used for the sealed
test (2.1a). That is acceptable **for this diagnostic, and only because no feature
carries temporal memory**: every feature is a same-day GFS forecast value or a
calendar-position encoding, so a training row dated after a held-out block cannot encode
that block's outcome — there is no autoregressive or lagged channel to leak through. The
sealed test remains strictly train-past-only; this CV is an internal generalization
estimate, not that test. Record this justification explicitly in the DECISIONS finding
so the discipline record stays honest.

## Reference — window, folds, models

**Window (all folds live here):** 2024-01-19 → 2025-07-31 (~18 months, feature-complete).

**Held-out blocks — six contiguous ~3-month blocks (calendar blocks, not named seasons,
so the scheme is hemisphere-agnostic and works uniformly at Dubbo):**

| block | dates |
|---|---|
| A | 2024-01-19 → 2024-04-18 |
| B | 2024-04-19 → 2024-07-18 |
| C | 2024-07-19 → 2024-10-18 |
| D | 2024-10-19 → 2025-01-18 |
| E | 2025-01-19 → 2025-04-18 |
| F | 2025-04-19 → 2025-07-31 |

Each fold holds out one block and trains on the other five (~15 months, spanning the
full calendar cycle). Every calendar month is a held-out test in at least one fold; the
training set always covers all seasons. Run all six folds at all five airports.

**The two models — identical locked LightGBM settings (do not change):**
`objective=regression_l1, n_estimators=300, learning_rate=0.05, num_leaves=15,
min_child_samples=40, random_state=42, deterministic=True, n_jobs=1`
- **3-feature:** `forecast_temp_c`, `season_sin`, `season_cos`.
- **5-feature:** the above **+ `cloud_cover` + `wind_speed_10m`** (`_previous_day1`).

---

## Task 1 — run the six-fold CV per airport

For each airport, for each of the four rungs — **raw GFS** (no fit), **+mean-bias** (fit
on the fold's training blocks only), **3-feature**, **5-feature** — produce an
**out-of-fold prediction for every day** in the window (each day predicted exactly once,
by the fold in which it was held out). Report per-airport row counts and drop counts.

## Task 2 — pooled and per-fold results

Per airport, report:
- **Pooled out-of-fold MAE (°C) and skill vs raw GFS** (`1 − model/rawGFS`) for each
  rung — this is the headline number, full-cycle coverage, every day held out once.
- **Per-fold MAE** for the four rungs, so fold-to-fold variance is visible (does the
  recipe win in some seasons and lose in others?).
- **Persistence** MAE per airport for context.

## Task 3 — overfit diagnostic

For the 3-feature and 5-feature models, report the **in-sample (training-fold) MAE vs
out-of-fold MAE gap**, pooled. Report the **5-feature feature importances**. A rich
model that only wins in-sample is still fitting noise — same check as the scout, now on
a full seasonal training set.

## Task 4 — the two branch reads (report, do not decide)

State plainly, per airport and overall:
- **Branch A:** trained on a full cycle, does 3-feature now beat raw GFS (pooled
  out-of-fold)? At how many of the five airports? Is that a clear recovery from the
  scout's 4/5-losing 6-month result, or does the recipe still fail even with full
  seasonal coverage?
- **Branch B:** does 5-feature beat 3-feature out-of-fold? Does it beat raw GFS? Is the
  overfit gap sane? How does Reno look specifically?
- A one-line synthesis: **does this point to "1.5-year short window is workable" or
  "deeper source needed"** — flagged as the owner's decision, not taken here.

---

## What NOT to do

- **Do not open, load, pull, join, or score the sealed test year (2025-08-01 →
  2026-07-31)** for any airport or fold. Every fold stays inside 2024-01-19 →
  2025-07-31. This is the hard line.
- **Do not lock any recipe** — this is a diagnostic, not a rehearsal-then-lock.
- **Do not tune hyperparameters** or change settings between the two models.
- **Do not add any lagged or recent-observation feature** — it would break the
  blocked-CV leakage-safety argument and the project rule.
- **Do not hand-pick features per airport** — same five everywhere.
- **Do not use ERA5/reanalysis or any second source**, and do not pull new raw — reuse
  session 32's `data/raw/features/`.
- **Do not fill nulls** — drop and count.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not decide the branch questions** (window-workable vs deep-source, go/no-go on a
  locked cycle) — report and flag for the owner.
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Tasks 2–4: pooled and per-fold tables per airport, the overfit gaps, the
   5-feature importances, row/drop counts, and the two branch reads.
2. **Append one DECISIONS finding** (append-only; check the tail of DECISIONS.md for the
   next sequential number — likely **F87**). Record the CV design, the
   **leakage-safety justification** for blocked CV (from the methodology note above), the
   pooled and per-fold results, the overfit diagnostic, and the two branch reads. **Flag
   — do not decide — the owner questions:** (a) is the 1.5-year window workable or is a
   deeper GFS GRIB source needed; (b) go/no-go on a full locked sealed-test cycle for the
   richer features. State that the sealed year was not opened.
3. **Refresh STATUS.md** to record session 33 and its result.
4. **No new raw files** should appear (reuse only). New code/notes are fine.
5. **Consistency check** before stopping: the new DECISIONS number is next-sequential and
   unique; every reported figure traces to a fitted fold in this session; **no figure was
   computed on the sealed test year** (verify the date bounds in code); STATUS and
   DECISIONS agree; `SPEC.md` and `RESULTS.md` are unmodified (`git status` to confirm
   only the expected files changed).
6. **Write a suggested commit message** — title line plus multi-paragraph body, no
   AI-attribution trailers (match the session 30–32 house style) — then **stop and wait
   for the owner's review.** Commit commands come only after review.
