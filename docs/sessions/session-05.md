# Session 05 — the objective fix (Q15), one change only

## What this session is

Session 04's model is trained on **squared error** but judged on **absolute
error (MAE)**. That is a mismatch: the model should be trained on the same
thing it is measured on. This session makes that single change — the
**absolute-error (L1 / MAE) training objective** — and re-runs the validation
rehearsal, so we can see the effect of that one fix in isolation.

This is a **principled correctness fix**, not tuning: it is the right change
regardless of whether the number improves. That is exactly why it is allowed
and variant-hunting is not.

**Still a rehearsal.** The sealed test year (2025-08-01 to 2026-07-31) is
**not touched**. Stage 1 has not passed. The frozen bar is judged once, on the
test year, in a later session.

## Scope — one change, nothing else

Change **only the training objective**. Keep everything else identical to
session 04: same D18 split (inner-training 2021-03-24 to 2024-07-31,
validation 2024-08-01 to 2025-07-31), same D19 features (forecast temperature +
season sin/cos), same tree settings (300 trees, lr 0.05, 15 leaves, min 40
samples/leaf), same seed 42, same deterministic run.

Do **not**:
- retune any setting to suit the new objective (if L1 behaves differently under
  the session-04 settings, that is an honest finding — report it, do not
  compensate by tuning);
- try any other objective, model type, or feature (that would be fishing);
- touch, load, or evaluate the test year;
- declare the frozen bar passed.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — especially 2.1 (no leakage), 2.2 (drop-count-report),
2.4 (frozen bar).

---

## What to do

**1. Refit the model with the absolute-error objective.** Switch the LightGBM
objective to L1 / MAE (e.g. `objective="regression_l1"`). Fit on
inner-training only, predicting the residual (observed − forecast) from the
D19 features. Confirm two consecutive runs are byte-identical (as in
session 04).

**2. Re-run the validation rehearsal**, exactly as session 04 did, on the same
common set of validation-year days (days with a paired row and the previous
day's observation for persistence — drop and count the rest). Report MAE (°C)
for all five methods:
- Raw GFS
- Persistence (past only, 2.1d)
- Climatology (inner-training only, 2.1c)
- Mean-bias reference (inner-training mean bias only)
- ML-corrected (now L1-trained)

Note: the four non-ML baselines are unchanged from session 04 — only the
ML-corrected row should differ. Report them anyway as a cross-check that the
harness is identical.

**3. Compare directly to session 04.** State plainly:
- ML-corrected validation MAE now vs session 04's **1.190 °C** — better,
  worse, or essentially unchanged, and by how much;
- whether it still beats raw GFS, persistence, and the mean-bias reference,
  with margins;
- the **per-season breakdown** again (session 04 found the win was essentially
  summer, with winter/spring very slightly worse) — did training on absolute
  error change that picture?
- feature importances (sanity check they are still sane).

**4. Honest framing.** The objective fix will likely move the number only a
little. Report whatever it does without spin. A tiny or even neutral change is
a fine result — the point was to make the model *correct*, not to inflate the
win.

---

## What to report at the end

Paste **real output**, not descriptions:
- confirmation only the objective changed (settings/features/split/seed
  identical to session 04);
- the validation-year MAE table for all five methods;
- ML-corrected now vs session 04 (1.190), with margin;
- the per-season breakdown;
- feature importances;
- confirmation the test year was not touched.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: what changed, the new validation number, and that the
   next step is the owner's call — lock the method and go to the housekeeping-
   then-sealed-test sessions, or not.
2. Append to DECISIONS: record the objective change (suggest **D20**) with its
   rationale, and the result as a finding (suggest **F15**). Mark **Q15
   closed**. Append-only — do not alter existing entries.
3. Run the three-file consistency check — report only, do not fix.
4. Write a suggested commit message, then stop for the owner's review. Do not
   commit.
