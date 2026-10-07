# Session 13 — CDG's sealed-test evaluation (one look)

## What this session is

This is the final test of Stage 2. It opens CDG's held-out test year
(2025-08-01 to 2026-07-31) for the **first and only time**, runs the method
**exactly as locked in DECISIONS D31**, and reports the result — pass or fail,
whatever it is.

**This session executes a written recipe. It decides nothing.** Every choice
was made in D31, with the test year unseen. Read D31 in full and follow it to
the letter.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D31
above all**. Critical rules (SPEC 2) apply, especially 2.1 (no leakage), 2.2
(drop-count-report), 2.4 (a failure is an honest finding, not something to fix).

---

## What to do — execute D31 exactly

**1. Refit the locked model on CDG's full training window (D31.5).** Train on
LFPG **2021-03-24 to 2025-07-31** — inner-training plus the validation year
recombined (expected 1,569 rows before drops). Same locked settings (D31.4):
LightGBM, `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40
samples/leaf, seed 42, deterministic. Same three features (D31.3): forecast
temperature, season sin, season cos. Predict the residual; corrected =
forecast + predicted residual (D31.2).

**2. Fit the two fitted references on CDG's training window only** (D31.8,
2.1c): climatology (day-of-year seasonal average of observed temperature,
±7.5 days circular, training window only) and the mean-bias figure (mean
training-window bias).

**3. Open CDG's test year and pair it** (D31.6, D31.7). Open the 2026 LFPG raw
chunks for the first time. Build the test rows for 2025-08-01 to 2026-07-31
using the D14 pairing rule (CDG reports on the hour, exact match; drop and
count anything with no report within 15 minutes). Nothing after 2026-07-31.
Nothing filled.

**Reconcile the drops against D31.7's prediction** (this is the check the
advance prediction exists for): expected **0** forecast-gap days, **1** off-hour
day (2026-07-08), **0** no-report days, **0** no-temperature days → 364 paired
rows, 363 scored once persistence loses 2026-07-09. Report the actual counts
and confirm they match. **If they do not reconcile, that is a stop signal
(D31.11)** — stop and raise it, do not proceed with the test year open.

**4. Score all five methods on the same common set of test days** (D31.8):
raw GFS, persistence (previous day's 12:00 observation — the 2025-08-01
"yesterday" is 2025-07-31, in training, legal), climatology, mean-bias
reference, and ML-corrected. MAE in °C (D31.9).

**5. Judge the bar (D31.9).** Stage 2 **passes if the corrected forecast has a
lower MAE than both raw GFS and persistence** over CDG's test year.
Qualitative, no numeric margin (D22); state the margin prominently.
Climatology and mean-bias are reported but do not decide pass or fail.

**6. Report the full picture** — the MAE table for all five methods, the
pass/fail verdict stated plainly, the per-season breakdown, the reconciled
drop counts, and how the test number compares to session 11's 1.377 rehearsal
(expected to differ, per D31.5). Feature importances as a sanity check. Where
useful, compare to EGLC's Stage 1 result (F16) — how the recipe travelled,
reported straight.

---

## The rules of this session (D31.10, D31.11)

- **One look.** The test year is opened once, the locked method runs once, and
  the result stands.
- **A failure is a result.** If the corrected forecast does not beat the bar,
  report it straight. Do **not** tune, re-fit, swap features, or re-run to
  chase a pass. Do **not** open the test year a second time. A CDG failure is a
  real, honest outcome about how far the recipe travels (D31.10).
- **Deviation is a stop signal.** If anything does not fit D31 — a missing file,
  a count that will not reconcile, a setting that errors, a tempting
  adjustment — **stop and raise it with the owner.** Do not decide on the fly
  with the test year open.
- Do **not** commit anything.

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the model, features, settings and training window match D31;
- the test-year drop count, reconciled against D31.7's prediction;
- the test-year MAE table for all five methods;
- the **plain pass/fail verdict** against raw GFS and persistence, margin stated
  prominently;
- the per-season breakdown;
- the test number vs session 11's 1.377 rehearsal, with a note that a
  difference is expected (D31.5);
- feature importances; and the EGLC comparison (how the recipe travelled).

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md with the outcome: Stage 2 passed or did not, and the result.
   If it **passed**, note that the roadmap's next stage (SPEC section 6) is
   Stage 3 (pool airports with location features) — but do not start it, and
   note the owner earlier wanted to explore more airports first. If it did
   **not** pass, note that the next step is an owner decision logged in
   DECISIONS, not a re-run.
2. Append the CDG test result to DECISIONS as a finding — the numbers, the
   verdict, the seasonal breakdown, the EGLC comparison. This is the Stage 2
   result of record.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
