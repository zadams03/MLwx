# Session 06 — housekeeping and method lock (before the sealed test)

## What this session is

The model is final (session 05). Before the one sealed-test look, this session
**ties off the loose ends and formally locks the method**, so the test session
can be pristine: it opens the test year, runs the already-locked method once,
and reports — nothing decided on the fly.

**No modelling this session. No test-year contact.** This is documentation,
tidy-up, and a written lock only.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply. SPEC edits are allowed **only where authorised below**;
DECISIONS is append-only.

---

## Part A — resolve the pending SPEC questions

**A-1. Q13 — keep the success bar qualitative (authorised SPEC 5.3 edit).**
Validation results now exist, so a numeric margin can no longer be set
"before seeing any results". The owner's decision: **leave the bar
qualitative** — beat raw GFS and persistence on MAE over the test year, no
numeric threshold. Edit SPEC 5.3 to state plainly that the bar is and stays
qualitative, and that no numeric margin will be introduced (doing so now, after
validation, would not be a clean before-the-fact choice). Record the reasoning
in DECISIONS.

**A-2. Q14 — add the mean-bias reference as a listed baseline (authorised
SPEC 5.2 edit).** It proved to be the most informative check (it separates
"learned real structure" from "found a constant offset"). Add it to the SPEC
5.2 baseline list, described plainly: the forecast plus GFS's average bias
measured on training data only. Note it is an **informative reference**, not
part of the pass/fail bar (the bar stays raw GFS + persistence).

**A-3. The archive-gap clause (authorised SPEC 3.2 edit).** SPEC 3.2 says the
archive is "confirmed available back to 24 March 2021" but never mentions the
492-hour gap (F8), so a reader could assume continuity — the exact mistake F1
made. Add one clause noting the single 492-hour gap (2023-12-30 to
2024-01-19, training window only; see F8), so the record is not misleading.

Make **only** these three edits to SPEC. No other SPEC changes.

## Part B — pin the environment (Q16)

Create a `requirements.txt` recording the exact versions of the Python
packages the project uses (numpy, scikit-learn, lightgbm, and anything else
the scripts import). Note in a short comment that LightGBM needs an OpenMP
runtime (`libomp`) and how it is currently satisfied on this machine (the
session-04 note), so the setup can be reproduced. Do not change any script
behaviour.

## Part C — write the method-lock record (the important part)

Append to DECISIONS a single, explicit **method-lock** entry (suggest **D21**)
that fully specifies what the sealed-test session will run — so nothing is
chosen while looking at the test year. It must state:

- **Target:** temperature at 12:00 UTC at EGLC (SPEC 4.1).
- **Model:** LightGBM, objective `regression_l1`, 300 trees, lr 0.05,
  15 leaves, min 40 samples/leaf, seed 42, deterministic — the exact
  session-05 settings.
- **Features:** forecast temperature + season (sin/cos of day-of-year); the
  D19 minimal set.
- **Training data for the test:** the **full** D13 training window
  (2021-03-24 to 2025-07-31) — i.e. inner-training **plus** the validation
  year recombined, since the method is now locked and validation has done its
  job. (This is the standard move: once the method is fixed, refit on all
  non-test data before the single test.)
- **Pairing / missing data:** D14 pairing, drop-count-report (2.2), nothing
  filled.
- **Baselines on the test year:** raw GFS, persistence, climatology
  (training-only), and the mean-bias reference (training-only).
- **The bar:** corrected MAE beats **raw GFS and persistence** over the test
  year (qualitative, per A-1).
- **One look only:** the test year is opened once, this locked method is run,
  and the result stands — pass or fail, reported straight.

State clearly that any deviation from this record in the test session is a red
flag to stop and raise with the owner.

---

## What to report at the end

- the before/after of each SPEC edit (A-1, A-2, A-3);
- the `requirements.txt` contents;
- the full D21 method-lock text;
- confirmation no model was run and the test year was not touched.

## What NOT to do

- Do not build, run, or refit any model.
- Do not touch, load, or evaluate the test year.
- Do not edit SPEC beyond A-1, A-2, A-3.
- Do not change or delete existing DECISIONS entries (append only).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the method is locked (point to D21); the next session is
   the single sealed-test evaluation.
2. Ensure DECISIONS carries the A-1/A-2/A-3 reasoning and the D21 lock. Mark
   Q13, Q14, Q16 closed.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
