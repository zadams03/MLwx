# Session 32 — richer-features scout (validation-year only, sealed test NOT opened)

## Scope — one job, then stop

A **scout experiment**: does adding cloud cover + 10 m wind speed to the 3-feature
model improve the temperature-residual correction, judged **on the validation year
only**, across all five airports? This is the rehearsal stage of the richer-features
method — it **fits and evaluates on the validation year and stops there.**

**The sealed test year (2025-08-01 → 2026-07-31) is NOT opened, touched, pulled, or
evaluated in this session, for any airport.** No recipe is locked. The result here is
directional — a green/red light for whether the richer features are worth a full
locked sealed-test cycle and/or a deeper data source — not a verdict against the
frozen bar.

The design was settled in planning: a **two-tier same-window comparison**. Because
cloud/wind only exist from 2024-01-19 (F85), both the 3-feature model and the richer
model are trained on the **same short window**, so any difference is features, not
window length.

## Standing rules that bind this session (SPEC §2)

- **No look-ahead leakage (2.1).** Time-based splits only. Everything fitted — model,
  mean-bias reference — uses the inner-training window only. The validation year is
  evaluated once per model, never fitted on.
- **The sealed test year is untouched.** Do not pull feature data past 2025-07-31; do
  not compute any figure on 2025-08-01 → 2026-07-31.
- Forecast source pinned to **`models=gfs_global`**, **`previous_day1`** offset (D16).
- **Drop-count-report, never fill** (2.2): any day whose paired feature value is null
  is dropped and counted; report the counts. (The 492 h gap predates this window, so
  it does not arise here.)
- **Raw is immutable, with provenance** (2.3): save the new cloud/wind pulls untouched
  under `data/raw/features/` with a `.meta.txt` (exact query URL + UTC pull time) per
  file.
- **Same feature set at every airport.** No per-airport feature hand-picking (selecting
  features on your own training data is itself overfitting).
- **No hyperparameter tuning.** Use the locked recipe settings unchanged for *both*
  models. Only the feature set (and the necessarily shorter window) change.
- **You never commit.** Prepare changes and a suggested message; the owner reviews and
  commits by hand.

## Reference — windows and features

**Short window (both models train on this):**
- Feature data available from **2024-01-19** (F85). Pull cloud/wind over
  **2024-01-19 → 2025-07-31** only.
- **Inner-training (fit): 2024-01-19 → 2024-07-31.** (~6 months — deliberately thin;
  this is why the result is a scout, not a lock. See "Interpretation".)
- **Validation year (evaluate): 2024-08-01 → 2025-07-31.** Feature-complete.
- **Sealed test 2025-08-01 → 2026-07-31: not opened this session.**

**The two models, identical LightGBM settings (from the locked recipe — do not
change):**
`objective=regression_l1, n_estimators=300, learning_rate=0.05, num_leaves=15,
min_child_samples=40, random_state=42, deterministic=True, n_jobs=1`

- **3-feature (short):** `forecast_temp_c`, `season_sin`, `season_cos`.
- **5-feature (richer):** the above **+ `cloud_cover` + `wind_speed_10m`**, both the
  GFS forecast at the target hour (`_previous_day1`), same valid time as the
  temperature forecast — so both are known ≥24 h ahead (no leakage).

All features are forecast-side or calendar; none is derived from the observation.

Airports and their target hours are in SPEC 3.4 (EGLC 12:00, LFPG 12:00, DSM 18:00,
YSDU 02:00, RNO 20:00 UTC). Positions in SPEC 3.4.

---

## Task 1 — pull and join the two new features

For all five airports, over **2024-01-19 → 2025-07-31 only**:
- Pull `cloud_cover_previous_day1` and `wind_speed_10m_previous_day1` at
  `models=gfs_global`, save raw + `.meta.txt` under `data/raw/features/`.
- Join to the existing temperature+observation rows on the airport's target hour,
  same pairing as temperature (SPEC 4.5). Drop-and-count any day with a null feature
  or missing pair; report the drop counts and the final row counts for inner-training
  and validation per airport.

## Task 2 — the baseline ladder, on the validation year

For each airport, fit on the inner-training window and evaluate on the validation year,
reporting **MAE (°C)** and **skill vs raw GFS (`1 − model/rawGFS`)** for each rung:

1. **Raw GFS** (no fit).
2. **+ mean-bias** — raw GFS plus the single constant mean(obs − forecast) measured on
   the **inner-training window only** (2.1c).
3. **3-feature (short)** — retrained on the short inner-training window. **Do NOT reuse
   the existing locked 3-feature numbers** — those were trained on the full 2021→2024
   window and would confound features with window length.
4. **5-feature (richer).**

Also report **persistence** MAE per airport for context (the eventual bar includes it).

## Task 3 — the overfitting diagnostic (the point of the scout)

For the 3-feature (short) and 5-feature models, at each airport, report the
**in-sample (inner-training) MAE vs validation MAE gap**. A richer model that looks
much better in-sample but not on validation is fitting noise on ~6 months of data —
exactly the risk this scout exists to catch. Also report the **5-feature model's
feature importances** (does it actually lean on cloud/wind, or ignore them?).

## Task 4 — headline read (report, do not decide)

State plainly, per airport and overall:
- Does **5-feature beat 3-feature (short)** on the validation year?
- Does **5-feature beat raw GFS** on the validation year?
- Is the in-sample/validation gap sane, or blown out?
- **Reno specifically:** any sign cloud/wind add structure there, or is its error still
  flat? (Reno's target is local noon; the clear-calm cold-pool effect cloud/wind
  capture is largely nocturnal, so a null here would be expected, not surprising.)

Do **not** decide the go/no-go or the deep-source question — flag the read for the
owner in the DECISIONS finding.

---

## What NOT to do

- **Do not open, pull, join, or evaluate the sealed test year (2025-08-01 →
  2026-07-31)** for any airport or variable. This is the hard line of the session.
- **Do not lock any recipe.** This is the rehearsal/scout stage only.
- **Do not reuse the existing locked 3-feature validation figures** as the comparison —
  retrain the 3-feature model on the identical short inner-training window.
- **Do not tune hyperparameters** or change model settings between the two models.
- **Do not hand-pick features per airport** — same five features everywhere.
- **Do not use ERA5/reanalysis or any second data source.** Cloud/wind come from the
  same Open-Meteo Previous Runs API, `gfs_global`, `previous_day1`. (Reanalysis
  assimilates observations and would leak — it is explicitly excluded.)
- **Do not fill nulls** — drop and count.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not decide the design** (deep-source vs short-window, terrain proxy for Reno) —
  report the scout read and flag it for the owner.
- **Do not commit.**
- **Do not exceed scope** — anything else worth doing gets logged as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Tasks 2–4 clearly: the ladder table per airport (validation-year MAE +
   skill for all rungs, plus persistence), the in-sample/validation gaps, the
   5-feature importances, row counts and drop counts, and the headline read.
2. **Append one DECISIONS finding** (append-only; check the tail of DECISIONS.md for
   the next sequential number — likely **F86**). Record the scout design, the
   validation-year results, the overfitting diagnostic, and the headline read.
   **Flag — do not decide — the two owner questions:** (a) go/no-go on a full locked
   sealed-test cycle for the richer features; (b) whether the result justifies chasing
   a deeper cloud/wind source (a real GFS GRIB archive, not reanalysis). State clearly
   that the sealed test year was not opened.
3. **Refresh STATUS.md** to record session 32 and its result.
4. **Save** the new raw pulls under `data/raw/features/` with `.meta.txt` provenance.
5. **Consistency check** before stopping: the new DECISIONS number is next-sequential
   and unique; every figure reported traces to a saved artifact or a fitted model in
   this session; no figure was computed on the sealed test year; STATUS and DECISIONS
   agree; `SPEC.md` and `RESULTS.md` are unmodified (`git status` to confirm only the
   expected files changed).
6. **Write a suggested commit message** (do not run it), then **stop and wait for the
   owner's review.** Commit commands come only after review.
