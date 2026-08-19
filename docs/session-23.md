# Session 23 — write and freeze Dubbo's method lock (no test yet)

## What this session is

Before Dubbo's sealed test is opened, Dubbo needs its own written **method
lock** — the D35-equivalent (which mirrored D31/D21). This mirrors session 17.

First of two sessions, split on purpose so the lock can be reviewed **before**
the irreversible test look. **This session writes and verifies the lock and
stops. It does not open the test year and runs no model.**

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D35
above all** (DSM's lock), since this mirrors it. Critical rules (SPEC 2) apply.

DECISIONS is append-only. One small SPEC edit is authorised (A-2 below); no
other.

---

## The principle

For Dubbo, **the location and the target hour change** (02:00 UTC, D37) —
nothing else, exactly as DSM changed them. So Dubbo's lock is D35 with the
airport and target hour swapped and nothing else touched. Every other
methodological choice is **identical** to D35/D31/D21. Writing it out separately
is so Dubbo's test session executes a Dubbo-named record rather than translating
a DSM-named one with the test year open.

## Task A-1 — write the Dubbo method lock (append to DECISIONS, suggest D38)

Mirror D35 point for point. State, for Dubbo specifically:

- **Target:** temperature at **02:00 UTC** (local standard noon, D37) at
  **Dubbo, Australia (YSDU / `AU__ASOS`)**, coordinates from SPEC 3.4. One row
  per day.
- **What the model predicts:** the residual (observed − forecast); corrected =
  forecast + predicted residual. Unchanged.
- **Features:** the D19 set — forecast temperature, season sin, season cos.
  Identical.
- **Model and settings:** the exact session-05 settings — LightGBM,
  `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40
  samples/leaf, seed 42, deterministic. Unchanged. Versions per requirements.txt.
- **Training data for the test:** the **full D13 window 2021-03-24 to
  2025-07-31** at Dubbo — inner-training plus the validation year recombined, as
  D35.5. State the consequence: the tested model is the same recipe on more data
  than the session-22 rehearsal used, so **the test number will not match
  session 22's 1.283 rehearsal figure and should not be expected to**. State the
  expected training-row count from session 22's join (1,193 inner-training +
  360 validation, minus none = the figure the rehearsal reconciled — confirm it).
- **Test data:** Dubbo's **2025-08-01 to 2026-07-31** (D13), opened for the
  first time, nothing after.
- **Pairing / missing data:** D14 pairing at the **02:00 UTC** target (Dubbo
  reports on the hour, exact match), drop-count-report (2.2), nothing filled.
  **Predict the test-year drops before the look**, from session 20's gap map
  (F57–F59). **Important — Dubbo is unlike the other three here:** it does not
  have the 492-hour gap; it has its own scattered forecast gaps, and unlike
  EGLC/CDG/DSM it **may have forecast or observation gaps inside the test year**.
  Read session 20's mapped Dubbo gaps for the test window and state the expected
  test-year drop count explicitly (forecast-side and observation-side). This is
  an expectation; a count that will not reconcile is a stop signal.
- **Baselines:** raw GFS, persistence (previous day's 02:00 observation —
  2025-08-01's "yesterday" is 2025-07-31, in training, legal), climatology
  (Dubbo training-window only), mean-bias reference (Dubbo training-window only).
  All fitted references fitted on Dubbo's training window only (2.1c).
- **The bar:** corrected MAE beats **raw GFS and persistence** over Dubbo's test
  year (qualitative, D22, SPEC 5.3). Climatology and mean-bias informative only.
- **One look only** (mirror D35.10): opened once, run once, result stands.
- **Deviation is a stop signal** (mirror D35.11).

**Record the watch-item explicitly (inside D38 or beside it).** Session 22
found Dubbo's validation win is **concentrated in one season** — the narrowest
seasonal spread of any airport (F63). This is **not** a reason to change the
method; it stays locked. But record that a single-season-concentrated win is
more exposed to the test year's weather than a broad one, so if the test result
differs markedly from the rehearsal, the seasonal distribution is the first
place to look. Pre-recording it keeps any post-test inspection honest.

## Task A-2 — clear the SPEC §6 Dubbo-bullet staleness (authorised)

SPEC §6's Dubbo bullet cites only the verify-on-contact findings (F49–F56). It
predates the pull/gap-map (F57–F59) and the join/rehearsal (F60–F63). Update the
bullet so it reflects Dubbo's actual progress through the five steps (verified,
pulled/mapped, rehearsed; lock and test pending), mirroring how the CDG and DSM
bullets read. This is the only SPEC edit authorised this session.

## Task A-3 — verify the lock is a faithful D35 copy

Produce a point-by-point correspondence check: for each D35 sub-point, show D38
is identical **except** the location (DSM→YSDU, its coordinates, `:54`→`:00`
reporting) **and the target hour** (18:00→02:00 UTC). Confirm **no other
methodological choice differs**. Note the one genuine structural difference to
call out clearly: Dubbo's test-year drop prediction is not "zero" like DSM's —
it must reflect Dubbo's own scattered gaps. If anything methodological differs
beyond location and hour, stop and flag it.

## Task A-4 — stop

Do not open Dubbo's test year. Do not run any model.

---

## What to report at the end

- the full D38 lock text;
- the point-by-point D35↔D38 correspondence check, showing only location and
  target hour differ (plus the drop-prediction difference, which is data not
  method);
- the watch-item as recorded;
- the SPEC §6 before/after;
- explicit confirmation that no model was run and Dubbo's test year was not
  touched.

## What NOT to do

- Do not open, load, or evaluate Dubbo's test year.
- Do not run, fit, or refit any model.
- Do not change any methodological choice from D35 — location and target hour
  only.
- Do not edit SPEC beyond A-2. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: Dubbo's method is locked (point to D38); the next session
   is Dubbo's single sealed-test evaluation, executing D38.
2. Ensure DECISIONS carries D38 and the watch-item.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
