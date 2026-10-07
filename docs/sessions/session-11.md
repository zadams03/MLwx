# Session 11 — CDG join and validation rehearsal (test year sealed)

## What this session is

This is the first modelling session for CDG, mirroring session 04 for EGLC. It
joins CDG's two series, looks at CDG's bias in the training data, and runs the
**already-locked method** (D21) — judged on CDG's **validation year**, taken
from inside training. CDG's sealed test year is **not touched** this session.

The method is locked. D26 says only the **location** changes for Stage 2, so
**nothing about the model, features, or settings is chosen again here** — this
session applies D21's recipe to CDG, it does not redesign anything.

**A good result here does NOT mean Stage 2 has passed.** It means the recipe
travels and is ready for CDG's single sealed-test look, in a later session.
CDG passing the frozen bar is judged once, on CDG's test year, later.

## Scope

Do only what is listed here, then stop. Do **not** touch CDG's test year. Do
**not** tune or vary the method. Do **not** declare the frozen bar passed.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — 2.1 (no leakage), 2.2 (drop-count-report), 2.4 (frozen
bar).

---

## Part A — join CDG's two series at 12:00 UTC

- From each CDG series keep only the **12:00 UTC** target hour.
- Pair by D14: CDG reports **on the hour** (`:00`), so the 12:00 forecast pairs
  with the 12:00 report — an **exact match, no offset** (F18). If no report
  falls within 15 minutes, drop that day and count it (2.2).
- One row per day: date, forecast, observation, residual (observed − forecast).
- Split by D18: inner-training **2021-03-24 to 2024-07-31**, validation
  **2024-08-01 to 2025-07-31**. Filter out the test year (2025-08-01 onward)
  entirely at load time.

**Reconcile the drops against the gap map (do not just accept them).** STATUS
and F22/F25 predict the drops, so check them:
- the 492-hour forecast gap should cost **20 days** at 12:00 UTC (it resumes at
  the target hour), all in inner-training;
- off-hour reports should cost **2 days** in the training window
  (2022-07-23 and 2022-07-25), both inner-training.
Report the actual kept/dropped counts per period and confirm they match these
expectations. **Anything else is a surprise — stop and flag it** rather than
proceeding.

## Part B — look at CDG's bias, inner-training only

On **inner-training only**, show how CDG's raw bias (observed − forecast)
behaves, the same look session 04 did for EGLC:
- overall mean and spread;
- how it varies with forecast temperature (binned averages) — where does CDG's
  bias sit, warm end or cold end?
- how it varies with season.
Keep this to inner-training. Do **not** explore the validation year's values
(it stands in for the sealed test — judge the model on it, don't mine it), and
never the test year.

**Compare to EGLC (F13):** at EGLC the warm end was biased (~1.2 °C too warm on
the hottest days), the cold end near-unbiased, overall mean bias only −0.108 °C.
State plainly how CDG's bias picture is similar or different. CDG is inland,
higher, more continental, so a different shape is entirely possible and is
itself a finding — not a problem.

## Part C — run the locked method and evaluate on CDG's validation year

**Model:** exactly the D21 recipe — LightGBM, `objective=regression_l1`, 300
trees, lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic;
features the D19 set (forecast temperature + season sin/cos). Fit on CDG's
**inner-training only**, predicting the residual. Nothing tuned or varied.
Confirm two runs are byte-identical.

**Evaluate all methods on the same CDG validation-year days** (common set: a
paired row plus the previous day's observation for persistence — drop and count
the rest). Report MAE (°C):
- Raw GFS
- Persistence (past only, 2.1d)
- Climatology (CDG inner-training only, 2.1c)
- Mean-bias reference (CDG inner-training mean bias only)
- ML-corrected

Then state plainly:
- does ML-corrected beat raw GFS on CDG's validation MAE, and by how much;
- does it beat persistence;
- does it beat the mean-bias reference (learning structure, not a constant);
- the per-season breakdown;
- feature importances (sanity check).

**Compare the whole picture to EGLC's rehearsal (F14/F15):** EGLC's validation
ML-corrected was 1.165 °C, ~6% over raw GFS, essentially a summer win. Is CDG's
correction bigger, smaller, differently distributed across seasons? Frame this
as "how does the recipe travel?", reported straight — a smaller win, a bigger
win, or a different seasonal shape are all legitimate, informative outcomes.

Frame all of this as a **validation rehearsal**, not the frozen-bar result.

---

## What to report at the end

Paste **real output**, not descriptions:
- join counts kept/dropped per period, reconciled against the 20 + 2 expected;
- CDG's inner-training bias summary, compared to EGLC's;
- the CDG validation-year MAE table for all five methods;
- the plain yes/no on beating raw GFS, persistence, and the mean-bias reference,
  with margins;
- the per-season breakdown and feature importances;
- an explicit CDG-vs-EGLC comparison of how the recipe travelled;
- confirmation CDG's test year was not touched.

## What NOT to do

- Do not touch, load, evaluate, or explore CDG's test year (2025-08-01 on).
- Do not tune or vary the model — apply the locked D21 recipe.
- Do not declare the frozen bar (SPEC 5) passed — that is the later session.
- Do not fill missing data; drop and count (2.2).
- Do not use the validation year or test year to fit anything (inner-training
  only for the model, climatology, and the mean-bias figure).
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the CDG rehearsal result, and that the next session is
   CDG's **method-lock-and-sealed-test** — the D21-equivalent for CDG (STATUS
   already flagged CDG has no written test lock yet), then the single test look.
2. Append the CDG rehearsal result to DECISIONS as a finding (the numbers, the
   EGLC comparison).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
