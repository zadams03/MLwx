# Session 12 — write and freeze CDG's method lock (no test yet)

## What this session is

Before CDG's sealed test is opened, CDG needs its own written **method lock** —
the D21-equivalent — so nothing is chosen with the test year open. D21 names
London City throughout; this session writes the CDG version, closing Q23.

This is the first of two sessions, split on purpose so the lock can be reviewed
**before** the irreversible test look. **This session writes and verifies the
lock and stops. It does not open the test year and runs no model.**

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D21
above all**, since this mirrors it. Critical rules (SPEC 2) apply.

DECISIONS is append-only. No SPEC edit is authorised.

---

## The principle

CDG changes **only the location** (D26). So CDG's lock is D21 with the airport
swapped and nothing else touched. Every methodological choice — model, settings,
features, target hour, pairing, missing-data handling, the bar, the one-look
rule — is **identical** to D21. The point of writing it out separately is not to
re-decide anything; it is so CDG's test session executes a written record rather
than reaching back to an EGLC-named one.

## What to do

**1. Write the CDG method lock as a new DECISIONS entry (suggest D31).** Mirror
D21's structure point for point. It must state, for CDG specifically:

- **Target:** temperature at **12:00 UTC** at **Paris Charles de Gaulle
  (LFPG)**, coordinates from SPEC 3.4. One row per day.
- **What the model predicts:** the residual (observed − forecast); corrected =
  forecast + predicted residual (D21.2, unchanged).
- **Features:** the D19 minimal set — forecast temperature, season sin, season
  cos. Identical to D21.3.
- **Model and settings:** the exact D21.4 / session-05 settings — LightGBM,
  `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40 samples/leaf,
  seed 42, deterministic. Unchanged.
- **Training data for the test:** the **full D13 training window
  2021-03-24 to 2025-07-31** — inner-training plus the validation year
  recombined, exactly as D21.5 did for EGLC. State the consequence plainly: the
  tested model is the same recipe on more data than the session-11 rehearsal
  used, so **the test number will not match the 1.377 rehearsal figure and
  should not be expected to**.
- **Test data:** CDG's **2025-08-01 to 2026-07-31** (D13), opened for the first
  time, nothing after it.
- **Pairing / missing data:** D14 pairing (CDG reports on the hour, exact match,
  F18), drop-count-report (2.2), nothing filled. The expected test-year drops
  from the gap map: **0 forecast-gap days** (the gap is entirely in training,
  F22) and any off-hour days per F25 (the test year had **1** such day,
  2026-07-08). Report the actual test-year drop count.
- **Baselines on the test year:** raw GFS, persistence (previous day's 12:00
  observation — note the 2025-08-01 "yesterday" is 2025-07-31, in training,
  legal per D21.8), climatology (CDG training-window only), mean-bias reference
  (CDG training-window only). All fitted references fitted on CDG's training
  window only (2.1c).
- **The bar:** corrected MAE beats **raw GFS and persistence** over CDG's test
  year (qualitative, D22, SPEC 5.3). Climatology and mean-bias are informative
  only.
- **One look only** (mirror D21.10): the test year is opened once, the locked
  method runs once, the result stands — pass or fail, reported straight.
- **Deviation is a stop signal** (mirror D21.11): any departure from this record
  in the test session is a red flag to stop and raise with the owner.

**2. Verify the lock is a faithful D21 copy.** After writing D31, produce a
point-by-point correspondence check: for each D21 sub-point, show that D31 is
identical **except** the location (EGLC→LFPG, its coordinates, its report timing
`:00` vs `:50`, and its expected drop counts). Confirm **no methodological
choice differs**. If anything other than the location differs, stop and flag it
— do not smooth it over.

**3. Stop.** Do not open CDG's test year. Do not run any model. The test is the
next session, after the owner has reviewed this lock.

---

## What to report at the end

- the full D31 lock text;
- the point-by-point D21↔D31 correspondence check, showing only the location
  differs;
- explicit confirmation that no model was run and CDG's test year was not
  touched.

## What NOT to do

- Do not open, load, or evaluate CDG's test year.
- Do not run, fit, or refit any model.
- Do not change any methodological choice from D21 — location only.
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: CDG's method is locked (point to D31, Q23 closed); the next
   session is CDG's single sealed-test evaluation, executing D31.
2. Ensure DECISIONS carries D31 and marks Q23 closed.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
