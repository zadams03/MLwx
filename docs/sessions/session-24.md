# Session 24 — Dubbo's sealed-test evaluation (one look)

## What this session is

The final test of Dubbo. It opens Dubbo's held-out test year
(2025-08-01 to 2026-07-31) for the **first and only time**, runs the method
**exactly as locked in DECISIONS D39**, and reports the result — pass or fail,
whatever it is.

**This session executes a written recipe. It decides nothing.** Every choice
was made in D39, with the test year unseen. Read D39 in full and follow it to
the letter.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D39
above all**. Critical rules (SPEC 2) apply, especially 2.1 (no leakage), 2.2
(drop-count-report), 2.4 (a failure is an honest finding, not something to fix).

---

## What to do — execute D39 exactly

**1. Refit the locked model on Dubbo's full training window (D39.5).** Train on
Dubbo **2021-03-24 to 2025-07-31** — inner-training plus the validation year
recombined (1,193 + 360 rows, the figure the session-22 join reconciled). Same
locked settings (D39.4): LightGBM, `objective=regression_l1`, 300 trees,
lr 0.05, 15 leaves, min 40 samples/leaf, seed 42, deterministic. Same three
features (D39.3): forecast temperature (read at **02:00 UTC**), season sin,
season cos. Predict the residual; corrected = forecast + predicted residual.

**2. Fit the two fitted references on Dubbo's training window only** (D39.8,
2.1c): climatology (day-of-year seasonal average, ±7.5 days circular, training
window only) and the mean-bias figure (mean training-window bias).

**3. Open Dubbo's test year and pair it** (D39.6, D39.7). Open the 2026 Dubbo raw
chunks for the first time. Build the test rows for 2025-08-01 to 2026-07-31 at
the **02:00 UTC** target using D14 (Dubbo reports on the hour, exact match; drop
and count anything with no report within 15 minutes). Nothing after 2026-07-31.
Nothing filled.

**Reconcile the drops against D39.7's prediction.** Unlike the other three
airports, Dubbo's test year is **not** predicted to be clean: D39.7 expects
**356 of 365 paired rows**, with scattered observation-side losses (and any
forecast-side gaps the session-20 map found in the test window). Report the
actual forecast-side and observation-side drop counts and confirm they match
D39.7's expectation. **If they do not reconcile, that is a stop signal
(D39.11)** — stop and raise it, do not proceed.

**4. Score all five methods on the same common set of test days** (D39.8):
raw GFS, persistence, climatology, mean-bias reference, ML-corrected. MAE in °C
(D39.9).

**5. Judge the bar (D39.9).** Dubbo **passes if the corrected forecast has a
lower MAE than both raw GFS and persistence** over Dubbo's test year.
Qualitative, no numeric margin (D22); state the margin prominently. Climatology
and mean-bias are reported but do not decide pass or fail.

**6. Report the full picture** — the MAE table for all five methods, the
pass/fail verdict stated plainly, the per-season breakdown, the reconciled drop
counts, and how the test number compares to session 22's 1.283 rehearsal
(expected to differ, D39.5). Feature importances. Compare to EGLC (F16), CDG
(F30), DSM (F47): how the recipe travelled across region, hemisphere and hour,
reported straight.

**7. Honour the watch-item (D39.12).** Session 22 found Dubbo's win concentrated
in one season. If the test result differs markedly from the rehearsal, the
seasonal distribution is the first place to look — as a description only, never
licence to re-run.

---

## The rules of this session (D39.10, D39.11)

- **One look.** Opened once, run once, result stands.
- **A failure is a result.** If the corrected forecast does not beat the bar,
  report it straight. Do **not** tune, re-fit, swap features, or re-run to chase
  a pass. Do **not** open the test year a second time. A single-season-
  concentrated win being fragile against the test year's weather is a genuine,
  informative possible outcome (D39.12).
- **Deviation is a stop signal.** Anything that does not fit D39 — a missing
  file, a count that will not reconcile, a setting that errors, a tempting
  adjustment — **stop and raise it with the owner.**
- Do **not** commit anything.

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the model, features, settings and training window match D39;
- the test-year drop count, reconciled against D39.7 (forecast-side and
  observation-side, expected ~356/365);
- the test-year MAE table for all five methods;
- the **plain pass/fail verdict** against raw GFS and persistence, margin
  prominent;
- the per-season breakdown (note the flipped-season phase);
- the test number vs session 22's 1.283 rehearsal (a difference is expected);
- feature importances; the EGLC/CDG/DSM comparison (how the recipe travelled).

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md with the outcome: Dubbo passed or did not, and the result.
   If it **passed**, note four airports across three continents and two
   hemispheres now pass, and that the owner's next choice is more airports, a
   different test year (the remaining half of the F30 caveat), or opening
   Stage 3 (pooling) — but do not start any of them. If it did **not** pass,
   note the next step is an owner decision logged in DECISIONS, not a re-run.
2. Append the Dubbo test result to DECISIONS as a finding — numbers, verdict,
   seasonal breakdown, the cross-airport comparison. This is Dubbo's result of
   record.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
