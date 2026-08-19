# Session 22 — Dubbo join and validation rehearsal (test year sealed)

## What this session is

The first modelling session for Dubbo, mirroring session 16 for DSM. It joins
Dubbo's two series at its target hour, looks at Dubbo's bias, and runs the
**already-locked method** — judged on Dubbo's **validation year**. Dubbo's
sealed test year is **not touched**.

The method is locked. For Dubbo, **the location and the target hour change**
(02:00 UTC = local noon, D37) — nothing else. No model, feature or setting is
re-chosen; this applies the recipe to Dubbo.

**What Dubbo tests.** It is the first **Southern Hemisphere** airport —
independent weather region **and flipped seasons** — tested on the **same
twelve months** as the others. So it is independent evidence on the region axis
(and a new hemisphere), but still the same calendar year. Read the result that
way. Like DSM, it changes location and target hour together, so it is not the
controlled location-only comparison EGLC↔CDG make (D33 caveat applies).

**A good result here does NOT mean Dubbo has passed.** It means the recipe is
ready for Dubbo's single sealed-test look, later.

## Scope

Do only what is listed here, then stop. Do **not** touch Dubbo's test year. Do
**not** tune or vary the method. Do **not** declare the frozen bar passed.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full (and
DECISIONS-archive.md only if deep history is needed). Critical rules (SPEC 2)
apply — 2.1 (no leakage), 2.2 (drop-count-report), 2.4 (frozen bar). As earlier
rehearsals did, prove in code that the method matches the locked recipe (only
Dubbo's location and its 02:00 UTC target hour differ).

---

## Part A — join Dubbo's two series at 02:00 UTC

- From each Dubbo series keep only the **02:00 UTC** target hour (Dubbo's local
  midday, D37).
- Pair by D14: Dubbo reports **on the hour** (`:00`), so the 02:00 forecast
  pairs with the 02:00 report — an **exact match, no offset**. If no report
  falls within 15 minutes, drop and count (2.2).
- One row per day: date, forecast, observation, residual (observed − forecast).
- Split by D18: inner-training **2021-03-24 to 2024-07-31**, validation
  **2024-08-01 to 2025-07-31**. Filter the test year (2025-08-01 on) out at load.

**Reconcile the drops against session 20's gap map** (Dubbo does **not** have the
492-hour gap — it has its own scattered forecast gaps, so its drop pattern is
unlike the other three). Read session 20's mapped Dubbo gaps from DECISIONS and
state the expected inner-training and validation drops **before** counting, then
confirm the actual join matches. **A count that does not reconcile is a stop
signal** — stop and flag it.

## Part B — look at Dubbo's bias, inner-training only

On **inner-training only**, show Dubbo's raw bias (observed − forecast):
- overall mean and spread;
- how it varies with forecast temperature (binned) — warm end, cold end, flat?
- how it varies with season.

**Compare to the three prior airports:** EGLC's bias lived at the **warm end**
(F13); CDG's in the **calendar/season** (F28); DSM carried **both** (F43). Where
does Dubbo's sit?

**The flipped-season point (interesting, examine explicitly):** Dubbo is Southern
Hemisphere, so its physical seasons are six months out of phase with the
Northern airports. The season feature is day-of-year, which just encodes calendar
position — so the model can still learn any seasonal bias, it will simply peak in
the opposite half of the year. If Dubbo has a calendar-driven bias like CDG's,
check that it appears **phase-shifted** (e.g. a Southern-summer signal in
Dec–Feb), which would be evidence the model learns local structure rather than a
hemisphere-baked pattern. Keep this to inner-training; do not explore the
validation year's values.

## Part C — run the locked method and evaluate on Dubbo's validation year

**Model:** the locked recipe — LightGBM, `objective=regression_l1`, 300 trees,
lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic; features the
D19 set (forecast temperature + season sin/cos). Fit on Dubbo **inner-training
only**, predicting the residual. Nothing tuned. Confirm two runs byte-identical.

**Evaluate all methods on the same Dubbo validation-year days** (common set: a
paired row plus the previous day's observation for persistence — drop and count
the rest). Report MAE (°C):
- Raw GFS
- Persistence (past only, 2.1d)
- Climatology (Dubbo inner-training only, 2.1c)
- Mean-bias reference (Dubbo inner-training mean bias only)
- ML-corrected

Then state plainly:
- does ML-corrected beat raw GFS on Dubbo's validation MAE, and by how much;
- does it beat persistence;
- does it beat the mean-bias reference (structure, not a constant);
- the per-season breakdown (note the flipped-season phase);
- feature importances (which feature does the model lean on at Dubbo?).

**Compare to the three prior rehearsals:** EGLC 1.165 (~6%), CDG 1.377 (~3.5%),
DSM 1.466 (~16%). Is Dubbo's correction bigger, smaller, differently shaped?
Frame as "how does the recipe travel to a different hemisphere?", reported
straight — any outcome is legitimate and informative.

Frame all of this as a **validation rehearsal**, not the frozen-bar result.

---

## What to report at the end

Paste **real output**:
- confirmation the method matches the lock (only Dubbo's location + 02:00 hour
  differ);
- join counts kept/dropped per period, reconciled against session 20's gap map;
- Dubbo's inner-training bias summary, compared to the three prior airports, and
  the flipped-season check;
- the Dubbo validation-year MAE table for all five methods;
- the plain yes/no on beating raw GFS, persistence, and the mean-bias reference,
  with margins;
- the per-season breakdown and feature importances;
- an explicit Dubbo-vs-others comparison of how the recipe travelled;
- confirmation Dubbo's test year was not touched.

## What NOT to do

- Do not touch, load, evaluate, or explore Dubbo's test year (2025-08-01 on).
- Do not tune or vary the model — apply the locked recipe.
- Do not declare the frozen bar (section 5) passed — that is the later session.
- Do not fill missing data; drop and count (2.2).
- Do not use the validation year or test year to fit anything (inner-training
  only for the model, climatology, and the mean-bias figure).
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the Dubbo rehearsal result, and that the next session is
   Dubbo's method-lock-and-sealed-test (the D35-equivalent for Dubbo), following
   the same two-session split used for CDG and DSM.
2. Append the Dubbo rehearsal result to DECISIONS as a finding (the numbers, the
   comparison to the three prior airports, the bias shape, the flipped-season
   observation).
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
