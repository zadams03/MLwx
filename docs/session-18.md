# Session 18 — DSM's sealed-test evaluation (one look)

## What this session is

The final test of Des Moines. It opens DSM's held-out test year
(2025-08-01 to 2026-07-31) for the **first and only time**, runs the method
**exactly as locked in DECISIONS D35**, and reports the result — pass or fail,
whatever it is.

**This session executes a written recipe. It decides nothing.** Every choice
was made in D35, with the test year unseen. Read D35 in full and follow it to
the letter.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D35
above all**. Critical rules (SPEC 2) apply, especially 2.1 (no leakage), 2.2
(drop-count-report), 2.4 (a failure is an honest finding, not something to fix).

---

## What to do — execute D35 exactly

**1. Refit the locked model on DSM's full training window (D35.5).** Train on
DSM **2021-03-24 to 2025-07-31** — inner-training plus the validation year
recombined (expected **1,571 rows**: 1,206 + 365, F42). Same locked settings
(D35.4): LightGBM, `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves,
min 40 samples/leaf, seed 42, deterministic. Same three features (D35.3):
forecast temperature (read at **18:00 UTC**), season sin, season cos. Predict
the residual; corrected = forecast + predicted residual (D35.2).

**2. Fit the two fitted references on DSM's training window only** (D35.8,
2.1c): climatology (day-of-year seasonal average of observed temperature,
±7.5 days circular, training window only) and the mean-bias figure (mean
training-window bias).

**3. Open DSM's test year and pair it** (D35.6, D35.7). Open the 2026 DSM raw
chunks for the first time. Build the test rows for 2025-08-01 to 2026-07-31 at
the **18:00 UTC** target using D14 (DSM reports at `:54`, 6-minute offset; drop
and count anything with no report within 15 minutes). Nothing after 2026-07-31.
Nothing filled.

**Reconcile the drops against D35.7's prediction:** expected **0** forecast-gap
days, **0** observation-side losses → **365 paired rows, 365 scored** (DSM is
the first airport expected to lose no test day; the first day 2025-08-01 keeps
its persistence value because 2025-07-31 is in training, legal per D35.8).
Report actual counts and confirm they match. **If they do not reconcile, that
is a stop signal (D35.11)** — stop and raise it, do not proceed.

**4. Score all five methods on the same common set of test days** (D35.8):
raw GFS, persistence, climatology, mean-bias reference, ML-corrected. MAE in °C
(D35.9). Note from D35.8/F45 that at DSM **raw GFS is the binding half of the
bar** (persistence is far weaker there).

**5. Judge the bar (D35.9).** DSM **passes if the corrected forecast has a lower
MAE than both raw GFS and persistence** over DSM's test year. Qualitative, no
numeric margin (D22); state the margin prominently. Climatology and mean-bias
are reported but do not decide pass or fail.

**6. Report the full picture** — the MAE table for all five methods, the
pass/fail verdict stated plainly, the per-season breakdown, the reconciled drop
counts, and how the test number compares to session 16's 1.466 rehearsal
(expected to differ, D35.5). Feature importances. Compare to EGLC (F16) and CDG
(F30): how the recipe travelled across region and hour, reported straight.

**7. Honour the watch-item and the seamless note (D35.12, D35.13).** If the
result behaves oddly, D35.12's warm-end days (≥40 °C forecast) are the first
place to look — as a description only, never licence to re-run. State that at
DSM `gfs_global` and `gfs_seamless` differ (F40), so this result is genuine GFS
by construction of the D16 pin.

---

## The rules of this session (D35.10, D35.11)

- **One look.** Opened once, run once, result stands.
- **A failure is a result.** If the corrected forecast does not beat the bar,
  report it straight. Do **not** tune, re-fit, swap features, or re-run to chase
  a pass. Do **not** open the test year a second time. DSM's wide rehearsal
  margin is not a reason to expect a pass (D35.10).
- **Deviation is a stop signal.** Anything that does not fit D35 — a missing
  file, a count that will not reconcile, a setting that errors, a tempting
  adjustment — **stop and raise it with the owner.**
- Do **not** commit anything.

## What to report at the end

Paste **real output**, not descriptions:
- confirmation the model, features, settings and training window match D35;
- the test-year drop count, reconciled against D35.7 (expected 365 scored);
- the test-year MAE table for all five methods;
- the **plain pass/fail verdict** against raw GFS and persistence, margin
  prominent;
- the per-season breakdown;
- the test number vs session 16's 1.466 rehearsal (a difference is expected);
- feature importances; the EGLC/CDG comparison (how the recipe travelled).

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md with the outcome: DSM passed or did not, and the result. If
   it **passed**, note three airports across two continents now pass, and that
   the owner's next choice is more airports, a different test year (the
   remaining half of the F30 caveat), or opening Stage 3 (pooling) — but do not
   start any of them. If it did **not** pass, note the next step is an owner
   decision logged in DECISIONS, not a re-run.
2. Append the DSM test result to DECISIONS as a finding — numbers, verdict,
   seasonal breakdown, the EGLC/CDG comparison. This is DSM's result of record.
3. Run the three-file consistency check — report only, don't fix. (The known
   cosmetic items — Q28, Q29 wording, the stale §6 DSM bullet — are for a later
   housekeeping pass, not this session.)
4. Write a suggested commit message, then stop for the owner's review.
