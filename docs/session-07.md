# Session 07 — the sealed-test evaluation (one look)

## What this session is

This is the single, final test of stage 1. It opens the held-out test year
(2025-08-01 to 2026-07-31) for the **first and only time**, runs the method
**exactly as locked in DECISIONS D21**, and reports the result — pass or fail,
whatever it is.

**This session executes a written recipe. It decides nothing.** Every choice
was already made in D21, with the test year unseen. Read D21 in full and follow
it to the letter.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — D21 above
all. Critical rules (SPEC 2) apply, especially 2.1 (no leakage), 2.2
(drop-count-report), 2.4 (the bar is frozen; a failure is an honest finding,
not something to fix).

---

## What to do — execute D21 exactly

**1. Refit the locked model on the full training window (D21.5).** Train on
**2021-03-24 to 2025-07-31** — inner-training plus the validation year
recombined. Same locked settings (D21.4): LightGBM, `objective=regression_l1`,
300 trees, lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic.
Same three features (D21.3): forecast temperature, season sin, season cos.
Predict the residual (observed − forecast); the corrected forecast is forecast
plus predicted residual (D21.2).

**2. Fit the two fitted references on the training window only** (D21.8,
SPEC 2.1c): climatology (day-of-year seasonal average of observed temperature,
training window only) and the mean-bias figure (mean training-window bias).

**3. Open the test year and pair it** (D21.6, D21.7). Open the 2026 raw chunks
for the first time. Build the test rows for 2025-08-01 to 2026-07-31 using the
D14 pairing rule (routine `:50` report as truth, nearest to the 12:00 forecast,
drop and count anything with no report within 15 minutes). Nothing after
2026-07-31. Nothing filled. Report the test-year drop count.

**4. Score all five methods on the same common set of test days** (D21.8):
raw GFS, persistence (previous day's 12:00 observation — note the 2025-08-01
"yesterday" is 2025-07-31, legal per D21.8), climatology, mean-bias reference,
and the ML-corrected forecast. MAE in °C (D21.9).

**5. Judge the bar (D21.9).** Stage 1 **passes if the corrected forecast has a
lower MAE than both raw GFS and persistence** over the test year. Qualitative,
no numeric margin (D22). Climatology and mean-bias are reported but do not
decide pass or fail.

**6. Report the full picture** — the MAE table for all five methods, the
pass/fail verdict stated plainly, the per-season breakdown, the test-year drop
count, and how the test number compares to the session-05 validation number
(expected to differ, per D21.5). Feature importances as a sanity check.

---

## The rules of this session (D21.10, D21.11)

- **One look.** The test year is opened once, the locked method runs once, and
  the result stands.
- **A failure is a result.** If the corrected forecast does not beat the bar,
  report it straight. Do **not** tune, re-fit, swap features, or re-run to
  chase a pass. Do **not** open the test year a second time.
- **Deviation is a stop signal.** If anything does not fit the D21 record — a
  missing file, a count that will not reconcile, a setting that errors, a
  tempting adjustment — **stop and raise it with the owner.** Do not decide on
  the fly with the test year open.
- Do **not** commit anything.

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the model, features, settings and training window match D21;
- the test-year drop count (D21.7);
- the test-year MAE table for all five methods;
- the **plain pass/fail verdict** against raw GFS and persistence;
- the per-season breakdown;
- the test number vs the session-05 validation number, with a note that a
  difference is expected (D21.5);
- feature importances.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md with the outcome: stage 1 passed or did not, and the
   result. If it **passed**, note that stage 2 (a second airport, CDG) is the
   next stage to open, per SPEC section 6 — but do not start it. If it did
   **not** pass, note that the next step is an owner decision, logged in
   DECISIONS, not a re-run.
2. Append the test result to DECISIONS as a finding (the numbers, the verdict,
   the seasonal breakdown). This is the stage 1 result of record.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
