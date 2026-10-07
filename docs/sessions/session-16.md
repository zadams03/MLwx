# Session 16 — DSM join and validation rehearsal (test year sealed)

## What this session is

The first modelling session for Des Moines, mirroring session 11 for CDG. It
joins DSM's two series at DSM's target hour, looks at DSM's bias, and runs the
**already-locked method** — judged on DSM's **validation year**. DSM's sealed
test year is **not touched**.

The method is locked. For DSM, **the location and the target hour change**
(18:00 UTC = local noon, D33) — nothing else. No model, feature, or setting is
re-chosen here; this applies the recipe to DSM.

**What DSM tests, precisely.** F30 flagged that EGLC and CDG shared *both* the
same twelve months *and* the same western-European weather region — one weather
year seen twice. DSM is tested on the **same twelve months** but a **different,
uncorrelated weather region** (US interior). So a DSM win is **independent
evidence on the region axis** — it does not rest on western Europe's weather —
but it is **still the same calendar year**, so it does not address "what if a
different year had different luck". Read the result that way: independent region,
same year.

**A good result here does NOT mean DSM has passed.** It means the recipe is
ready for DSM's single sealed-test look, later.

## Scope

Do only what is listed here, then stop. Do **not** touch DSM's test year. Do
**not** tune or vary the method. Do **not** declare the frozen bar passed.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — 2.1 (no leakage), 2.2 (drop-count-report), 2.4 (frozen
bar). As sessions 11/13 did, prove in code that the method matches the locked
recipe (only DSM's location and its 18:00 UTC target hour differ).

---

## Part A — join DSM's two series at 18:00 UTC

- From each DSM series keep only the **18:00 UTC** target hour (DSM's local
  midday, D33 — not 12:00 UTC).
- Pair by D14: DSM reports at `:54`, so the 18:00 forecast pairs with the 17:54
  report — a 6-minute offset, within tolerance (F34). If no report falls within
  15 minutes, drop and count (2.2).
- One row per day: date, forecast, observation, residual (observed − forecast).
- Split by D18: inner-training **2021-03-24 to 2024-07-31**, validation
  **2024-08-01 to 2025-07-31**. Filter the test year (2025-08-01 on) out at load.

**Reconcile the drops against F41's advance prediction** (this is the check
F41 exists for): expected **20** inner-training days dropped (all the shared
492-hour forecast gap, F38), **0** validation days dropped, **0** off-hour or
no-report losses at the 18:00 target. Report actual kept/dropped per period and
confirm they match. **Anything else is a surprise — stop and flag it.**

## Part B — look at DSM's bias, inner-training only

On **inner-training only**, show DSM's raw bias (observed − forecast):
- overall mean and spread;
- how it varies with forecast temperature (binned) — warm end, cold end, or
  flat?
- how it varies with season.

**Compare to both prior airports:** EGLC's bias lived at the **warm end**
(F13); CDG's lived in the **calendar/season** (F28). Where does DSM's sit? DSM
is continental with a much wider temperature range, so a third distinct shape is
possible and is itself a finding.

**Look specifically at the warm-end extrapolation F38 flagged:** DSM's forecast
warm end runs past anything observed (64 hours forecast ≥40 °C vs an observed
max of 38.33 °C in training). Check whether that matters **at the 18:00 target
specifically** — F13 caught F10 mistaking a night-time signal for a target-hour
one, so confirm the effect is real at 18:00 and not carried by other hours.
Keep all of this to inner-training; do not explore the validation year's values.

## Part C — run the locked method and evaluate on DSM's validation year

**Model:** the D21/D31 recipe — LightGBM, `objective=regression_l1`, 300 trees,
lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic; features the
D19 set (forecast temperature + season sin/cos). Fit on DSM **inner-training
only**, predicting the residual. Nothing tuned. Confirm two runs byte-identical.

**Evaluate all methods on the same DSM validation-year days** (common set: a
paired row plus the previous day's observation for persistence — drop and count
the rest). Report MAE (°C):
- Raw GFS
- Persistence (past only, 2.1d)
- Climatology (DSM inner-training only, 2.1c)
- Mean-bias reference (DSM inner-training mean bias only)
- ML-corrected

Then state plainly:
- does ML-corrected beat raw GFS on DSM's validation MAE, and by how much;
- does it beat persistence;
- does it beat the mean-bias reference (structure, not a constant);
- the per-season breakdown;
- feature importances (which feature does the model lean on at DSM?).

**Compare the whole picture to the prior rehearsals:** EGLC validation
ML-corrected 1.165 (~6% over raw GFS, a summer win); CDG 1.377 (~3.5%, spread
across seasons). Is DSM's correction bigger, smaller, differently shaped? Frame
as "how does the recipe travel to a different *region*?", reported straight — a
smaller win, a bigger win, or a different seasonal shape are all legitimate,
informative outcomes.

Frame all of this as a **validation rehearsal**, not the frozen-bar result.

---

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the method matches the lock (only DSM's location + 18:00 hour
  differ);
- join counts kept/dropped per period, reconciled against F41's 20 + 0;
- DSM's inner-training bias summary, compared to EGLC and CDG, and the warm-end
  check at 18:00;
- the DSM validation-year MAE table for all five methods;
- the plain yes/no on beating raw GFS, persistence, and the mean-bias reference,
  with margins;
- the per-season breakdown and feature importances;
- an explicit DSM-vs-EGLC-vs-CDG comparison of how the recipe travelled;
- confirmation DSM's test year was not touched.

## What NOT to do

- Do not touch, load, evaluate, or explore DSM's test year (2025-08-01 on).
- Do not tune or vary the model — apply the locked recipe.
- Do not declare the frozen bar (section 5) passed — that is the later session.
- Do not fill missing data; drop and count (2.2).
- Do not use the validation year or test year to fit anything (inner-training
  only for the model, climatology, and the mean-bias figure).
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the DSM rehearsal result, and that the next session is
   DSM's method-lock-and-sealed-test (the D31-equivalent for DSM), following the
   same two-session split used for CDG.
2. Append the DSM rehearsal result to DECISIONS as a finding (the numbers, the
   EGLC/CDG comparison, the bias shape).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
