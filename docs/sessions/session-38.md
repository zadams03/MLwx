# Session 38 — GRIB build, step 3: join to obs + richer-features CV on the full v16 window

## Where this sits

Step 3 of the GRIB build sub-project, and the payoff. Steps 1–2 (sessions 36–37) built and
validated a GRIB feature dataset (temperature + cloud cover + 10 m wind speed) over the v16
window, all five airports passing the temperature reproduction gate. This session joins those
features to the observations and **re-runs the richer-features experiment on the full
~4.4-year v16 window** — the thing session 33 could only do on 1.5 years. It answers, on real
full-window data: does adding cloud/wind beat the 3-feature model, does LFPG recover, and does
Reno's short-window rescue signal hold?

**This session opens no sealed year, locks nothing.** It is the out-of-sample evidence that
informs the step-4 lock decision. Evaluation is by cross-validation inside the training
window, exactly as session 33 did — just on the full window now, and on GRIB features.

## Scope — four things, then stop

1. **Diagnose the cloud-cover tail** (from session 37) enough to trust cloud as a feature.
2. **Join** the GRIB features to the existing IEM observations.
3. **Run the richer-features CV** — 3-feature vs 5-feature, blocked seasonal CV, on the full
   v16 window.
4. **Sanity-check the source swap** — confirm the GRIB 3-feature model behaves consistently
   with the established Open-Meteo 3-feature results (the source change didn't degrade things).

Report the reads and stop for review.

## Standing rules that bind this session (SPEC §2)

- **Sealed test year untouched.** The GRIB dataset is training-window-only (≤ 2025-07-31, step
  2), so no sealed data is present — assert this at load, and compute no figure on
  2025-08-01 → 2026-07-31.
- **Same feature set at every airport, no per-airport selection, no hyperparameter tuning.**
  Locked LightGBM settings unchanged for both models (`objective=regression_l1,
  n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40,
  random_state=42, deterministic=True, n_jobs=1`).
- **No lagged / recent-observation features** — beyond the standing rule, this is what keeps
  blocked CV leakage-safe (F87's justification): every feature is a same-day GRIB forecast
  value or a calendar encoding, so training rows around a held-out block can't leak its answer.
- **GRIB source throughout.** Both models use GRIB-derived temperature (with the step-2
  elevation correction), so the 3-vs-5 comparison is features-only, same source. Read existing
  Open-Meteo data only for the source-swap sanity check.
- **Drop-count-report, never fill** (2.2). **Raw is immutable** — this session writes only
  processed results/tables, no new bulk raw (no 20 GB concern; D47 applies only to raw GRIB).
- **You never commit.** Prepare changes and a suggested message.

## Reference — models, target, window

- **Target:** residual = observed temperature − GRIB forecast temperature, at each airport's
  target hour (SPEC 3.4 / 4.5), paired to the IEM observation as usual (±15 min).
- **3-feature:** `forecast_temp_c` (GRIB, elevation-corrected), `season_sin`, `season_cos`.
- **5-feature:** the above **+ `cloud_cover` + `wind_speed_10m`** (GRIB).
- **Window:** 2021-03-24 → 2025-07-31 (v16 only). Sealed year excluded.

---

## Task 1 — diagnose the cloud-cover tail (trust-the-feature check)

Session 37 found GRIB `TCDC` matches Open-Meteo cloud at the median (1.3%) but with a heavy
tail (p90 41.8, p99 88.0). Wind matched tightly, so the grid/lead alignment is sound — the
tail is most likely a **definitional** difference (`TCDC` "entire atmosphere" vs Open-Meteo's
cloud field), which is benign as long as GRIB cloud is **self-consistent** across the dataset.
Confirm which it is: inspect the high-difference days (systematic offset vs random artifact),
check GRIB `TCDC` has no missing/garbage values and a sane 0–100 distribution over the full
window. Conclude **benign-definitional (proceed, GRIB cloud is the feature) or artifact (name
the cause)**. Do not "correct" GRIB cloud toward Open-Meteo — GRIB is the one consistent source
the whole build exists to provide; the point is only to confirm it's trustworthy on its own
terms.

## Task 2 — join GRIB features to observations

Join the step-2 GRIB feature rows to the existing IEM observation for each airport-day at the
target hour (reuse the established pairing; do not re-pull observations). Compute the residual
target. Drop-count-report any airport-day with a missing observation or a null feature. Report
final row counts per airport.

## Task 3 — richer-features CV on the full window

Blocked seasonal cross-validation, exactly as F87/session 33 but over the full window:
- Tile 2021-03-24 → 2025-07-31 into contiguous ~3-month blocks (~17–18 blocks). Leave-one-
  block-out: hold out one block, train on all the others (~4 years, all seasons), predict the
  held-out block. Every day is predicted out-of-fold exactly once.
- For each airport, produce pooled out-of-fold predictions for four rungs — **raw GFS**,
  **+mean-bias** (fit on each fold's training blocks only), **3-feature**, **5-feature** — and
  report **pooled MAE and skill vs raw GFS** for each, plus **persistence** for context.
- Report **per-block** MAE too, so fold-to-fold variance is visible.
- Report the **in-sample vs out-of-fold gap** for the 3- and 5-feature models (overfit check)
  and the **5-feature feature importances** (does it lean on cloud/wind?).

## Task 4 — source-swap sanity check

Confirm the GRIB 3-feature model behaves consistently with the established Open-Meteo 3-feature
results — i.e. the switch from Open-Meteo to GRIB temperature didn't change the baseline. Since
GRIB temperature reproduced Open-Meteo at 5/5 (session 37), the GRIB 3-feature CV should land
at a similar performance level to the known Open-Meteo 3-feature behaviour. Report whether it
does; flag any material divergence.

## Task 5 — the headline reads (report, do not decide)

State plainly, per airport and overall:
- Does **5-feature beat 3-feature** out-of-fold on the full window? At how many airports?
- Does **5-feature beat raw GFS**? Are the overfit gaps sane?
- **LFPG:** does the full window recover it (it failed on the short window, F86/F87, but passes
  on the full Open-Meteo window)? Does 5-feature help or hurt there?
- **Reno:** does the short-window rescue signal (F87: 5-feat beat 3-feat and raw GFS in CV)
  **hold on the full window**? This is the headline question for the whole richer-features phase.
- A one-line synthesis: does this support locking the richer method (step 4), and on which
  window — flagged as the owner's decision, not taken here.

---

## What NOT to do

- **Do not open, load, or score the sealed test year** (2025-08-01 → 2026-07-31) — the dataset
  ends 2025-07-31; assert it.
- **Do not lock any recipe** — this is CV evidence, not the sealed test.
- **Do not tune hyperparameters** or change settings between the two models.
- **Do not add lagged/recent-obs features**, and do not add a terrain/elevation feature this
  session — keep the clean 3-vs-5 comparison; a terrain descriptor for Reno is a separate later
  experiment if cloud/wind don't rescue it.
- **Do not hand-pick features per airport.**
- **Do not "correct" GRIB cloud toward Open-Meteo** — GRIB is the source; only confirm it's
  self-consistent.
- **Do not modify `SPEC.md` or `RESULTS.md`.**
- **Do not commit.**
- **Do not exceed scope** — log anything else as a question.

## End-of-session steps (prepare for review; do NOT commit)

1. **Report** Task 1 (cloud verdict), Task 3 (pooled + per-block CV tables per airport, overfit
   gaps, importances), Task 4 (source-swap check), and Task 5 (headline reads).
2. **Append one DECISIONS finding** (append-only; next sequential — check the tail of live
   DECISIONS.md, likely **F91**): the cloud diagnostic verdict, the full-window CV results, the
   source-swap check, and the LFPG/Reno reads. **Flag — do not decide — the owner's step-4
   lock question** (lock the richer method, and on which window).
3. **Refresh STATUS.md** to record session 38 and the full-window result.
4. **Save** the join, CV results, and companion tables under `data/processed/` (small — no raw).
5. **Archive step (routine):** move any entry that became settled this session to
   `DECISIONS-archive.md` per the criterion — F88 (GRIB feasibility, GO-COSTLY) may now be
   settled and superseded by the completed build; check whether it's still cited live, and move
   it if not. State what moved.
6. **Consistency check:** new DECISIONS number next-sequential and unique; every figure traces
   to a fitted fold or table in this session; **no figure computed on the sealed test year**
   (verify date bounds in code); STATUS and DECISIONS agree; `SPEC.md`/`RESULTS.md` unmodified;
   `git status` shows only the expected (small) files.
7. **Write a suggested commit message** — single-quoted, no double quotes or apostrophes in the
   body, `--` not em-dashes, short body (detail in F91) — then **stop and wait for the owner's
   review.**
