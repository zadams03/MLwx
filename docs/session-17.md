# Session 17 — write and freeze DSM's method lock (no test yet)

## What this session is

Before DSM's sealed test is opened, DSM needs its own written **method lock** —
the D31-equivalent (which was itself the D21-equivalent for CDG). This mirrors
session 12.

This is the first of two sessions, split on purpose so the lock can be reviewed
**before** the irreversible test look. **This session writes and verifies the
lock and stops. It does not open the test year and runs no model.**

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full — **D31
above all** (CDG's lock), since this mirrors it. Critical rules (SPEC 2) apply.

DECISIONS is append-only. No SPEC edit is authorised.

---

## The principle

For DSM, **the location and the target hour change** (18:00 UTC, D33) — nothing
else. So DSM's lock is D31 with the airport and target hour swapped and nothing
else touched. Every other methodological choice — the model, its settings, the
features, the residual target, the pairing rule, the missing-data rule, the
references, the bar, the one-look rule — is **identical** to D31/D21. Writing it
out separately is so DSM's test session executes a DSM-named record rather than
translating a CDG-named one with the test year open (which D31.11 forbids).

## What to do

**1. Write the DSM method lock as a new DECISIONS entry (suggest D35).** Mirror
D31 point for point. State, for DSM specifically:

- **Target:** temperature at **18:00 UTC** (local standard noon, D33) at **Des
  Moines, Iowa (DSM / `IA_ASOS`)**, coordinates from SPEC 3.4. One row per day.
- **What the model predicts:** the residual (observed − forecast); corrected =
  forecast + predicted residual. Unchanged.
- **Features:** the D19 set — forecast temperature, season sin, season cos.
  Identical.
- **Model and settings:** the exact session-05 settings — LightGBM,
  `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40
  samples/leaf, seed 42, deterministic. Unchanged. Versions pinned per
  requirements.txt.
- **Training data for the test:** the **full D13 window 2021-03-24 to
  2025-07-31** at DSM — inner-training plus the validation year recombined, as
  D21.5/D31.5. State the consequence: the tested model is the same recipe on
  more data than the session-16 rehearsal used, so **the test number will not
  match session 16's 1.466 rehearsal figure and should not be expected to**.
  Expected training rows: **1,206 + 365 = 1,571** (F41), minus none — state it.
- **Test data:** DSM's **2025-08-01 to 2026-07-31** (D13), opened for the first
  time, nothing after.
- **Pairing / missing data:** D14 pairing at the **18:00 UTC** target (DSM
  reports at `:54`, a 6-minute offset, F34), drop-count-report (2.2), nothing
  filled. **Predict the test-year drops before the look**, from session 15's gap
  map (F38/F41): the 492-hour gap is entirely in training, so **0 forecast-gap
  days** in the test year; DSM's observation record lost **0** days at the 18:00
  target across five years, so **0** expected observation-side losses →
  **365 paired rows, 364 scored** once persistence loses the first day. State
  this is an expectation; a count that will not reconcile is a stop signal.
- **Baselines:** raw GFS, persistence (previous day's 18:00 observation —
  2025-08-01's "yesterday" is 2025-07-31, in training, legal), climatology (DSM
  training-window only), mean-bias reference (DSM training-window only). All
  fitted references fitted on DSM's training window only (2.1c). Note from F46
  that at DSM **persistence is far weaker and raw GFS is the binding half of the
  bar**.
- **The bar:** corrected MAE beats **raw GFS and persistence** over DSM's test
  year (qualitative, D22, SPEC 5.3). Climatology and mean-bias informative only.
- **One look only** (mirror D31.10): opened once, run once, result stands.
- **Deviation is a stop signal** (mirror D31.11).

**2. Record the warm-end watch-item explicitly (inside D35 or beside it).** F44
found DSM's forecast overshoots at the warm extreme (≥40 °C forecast vs 38.33 °C
observed, large negative bias on ~5 days), real at the target hour. This is
**not** a reason to change the method — it stays locked — but record that if the
test result behaves oddly, this handful of extreme days is the first place to
look. Pre-recording it keeps any post-test inspection honest.

**3. Verify the lock is a faithful D31 copy.** Produce a point-by-point
correspondence check: for each D31 sub-point, show D35 is identical **except**
the location (LFPG→DSM, its coordinates, `:00`→`:54` reporting) **and the target
hour** (12:00→18:00 UTC, per D33). Confirm **no other methodological choice
differs**. If anything else differs, stop and flag it — do not smooth it over.
Note this is the first lock where the target hour is among the intended
differences (D33), unlike D31 which was location-only.

**4. Stop.** Do not open DSM's test year. Do not run any model.

---

## What to report at the end

- the full D35 lock text;
- the point-by-point D31↔D35 correspondence check, showing only location and
  target hour differ;
- the warm-end watch-item as recorded;
- explicit confirmation that no model was run and DSM's test year was not
  touched.

## What NOT to do

- Do not open, load, or evaluate DSM's test year.
- Do not run, fit, or refit any model.
- Do not change any methodological choice from D31 — location and target hour
  only.
- Do not edit SPEC. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: DSM's method is locked (point to D35); the next session is
   DSM's single sealed-test evaluation, executing D35.
2. Ensure DECISIONS carries D35 and the warm-end watch-item.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
