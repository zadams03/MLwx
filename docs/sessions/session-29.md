# Session 29 — Reno's sealed-test evaluation (one look)

## What this session is

The final test of Reno. It opens Reno's held-out test year
(2025-08-01 to 2026-07-31) for the **first and only time**, runs the method
**exactly as locked in DECISIONS D44**, and reports the result — pass or fail,
whatever it is.

**Reno's rehearsal did not beat raw GFS (F80), so a sealed-test failure is an
expected, legitimate outcome — recorded in advance (D44, D44.12).** It would be
a genuine finding about the method's edge, not a bug. Report it straight either
way. Do not tune, refit, or change anything to chase a pass.

**This session executes a written recipe. It decides nothing.** Every choice was
made in D44, with the test year unseen. Read D44 in full and follow it exactly.

Before starting, read SPEC.md, STATUS.md, DECISIONS.md in full — **D44 above
all**. Critical rules (SPEC 2) apply, especially 2.1 (no leakage), 2.2
(drop-count-report), 2.4 (a failure is an honest finding, not something to fix).

---

## What to do — execute D44 exactly

**1. Refit the locked model on Reno's full training window (D44.5).** Train on
Reno **2021-03-24 to 2025-07-31** — inner-training plus validation recombined
(expected **1,568 rows**: 1,203 + 365). Same locked settings (D44.4): LightGBM,
`objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40 samples/leaf,
seed 42, deterministic. Same three features (D44.3): forecast temperature (read
at **20:00 UTC**), season sin, season cos. Predict the residual; corrected =
forecast + predicted residual.

**2. Fit the two fitted references on Reno's training window only** (D44.8,
2.1c): climatology (day-of-year seasonal average, ±7.5 days circular, training
window only) and the mean-bias figure (mean training-window bias).

**3. Open Reno's test year and pair it** (D44.6, D44.7). Open the 2026 Reno raw
chunks for the first time. Build the test rows for 2025-08-01 to 2026-07-31 at
the **20:00 UTC** target using D14 (Reno reports at `:55`, 5-minute offset; drop
and count anything with no report within 15 minutes). Nothing after 2026-07-31.
Nothing filled.

**Reconcile the drops against D44.7's prediction:** expected **365/365 paired
and scored, 0 dropped either side** (the cleanest test-year prediction of any
airport). Report actual counts and confirm they match. **If they do not
reconcile, that is a stop signal (D44.11)** — stop and raise it.

**4. Score all five methods on the same common set of test days** (D44.8):
raw GFS, persistence, climatology, mean-bias reference, ML-corrected. MAE in °C.

**5. Judge the bar (D44.9).** Reno **passes if the corrected forecast has a lower
MAE than both raw GFS and persistence** over Reno's test year. Qualitative, no
numeric margin (D22); state the margin prominently. **Raw GFS is the half most
likely to fail (D44); report the corrected-vs-raw-GFS margin especially clearly,
with its sign.** Climatology and mean-bias are reported but do not decide pass
or fail.

**6. Report the full picture** — the MAE table for all five methods, the
pass/fail verdict stated plainly (including which half of the bar failed, if
either), the per-season breakdown, the reconciled drop counts, and how the test
number compares to session 27's 1.499 rehearsal (expected to differ, D44.5).
Feature importances. Compare to the four passed airports: Reno is the terrain/
near-constant-bias case, so frame how it differs, reported straight.

**7. Honour the watch-item (D44.12).** If the correction fails to beat raw GFS,
D44.12's near-constant-bias/overfit pattern is the pre-recorded expected reason,
and winter the first place to look — as a description, never licence to re-run.

---

## The rules of this session (D44.10, D44.11)

- **One look.** Opened once, run once, result stands.
- **A failure is a result — and an expected one here.** If the corrected
  forecast does not beat the bar, report it straight. Do **not** tune, re-fit,
  swap or add features, or re-run to chase a pass. Do **not** open the test year
  a second time. Reno failing is a legitimate, valuable data point about the
  method's limits (D44, D44.12).
- **Deviation is a stop signal.** Anything that does not fit D44 — a missing
  file, a count that will not reconcile, a setting that errors, a tempting
  adjustment — **stop and raise it with the owner.**
- Do **not** commit anything.

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the model, features, settings and training window match D44;
- the test-year drop count, reconciled against D44.7 (expected 365/365);
- the test-year MAE table for all five methods;
- the **plain pass/fail verdict** against raw GFS and persistence, the
  corrected-vs-raw-GFS margin and its sign stated prominently;
- the per-season breakdown;
- the test number vs session 27's 1.499 rehearsal (a difference is expected);
- feature importances; the comparison to the four passed airports.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md with the outcome: Reno passed or did not (state which half
   of the bar, if it failed), and the result. Note that a Reno failure is the
   project's first, was expected (D44.12), and is a legitimate result of record
   — the method's edge, not a defect. Note the owner intends a planning session
   next on when to add richer features (Reno being the motivating case), and
   that SPEC §3.4/§5.0 will need Reno's verdict recorded (pending, next SPEC
   session). Do not start any of that.
2. Append Reno's test result to DECISIONS as a finding — numbers, verdict, which
   half failed if any, seasonal breakdown, the comparison to the four passes.
   This is Reno's result of record.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
