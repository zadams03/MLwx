# Session 28 — write and freeze Reno's method lock (no test yet)

## What this session is

Before Reno's sealed test, Reno needs its own written **method lock** — the
D39-equivalent. This mirrors session 23.

First of two sessions, split on purpose so the lock can be reviewed **before**
the irreversible test look. **This session writes and verifies the lock and
stops. It does not open the test year and runs no model.**

**Important context — Reno's rehearsal did NOT beat raw GFS** (session 27, F80:
1.499 vs 1.493, −0.4%; it beat persistence and, barely, the mean-bias
reference). Reno's bias is near-constant and its error largely random scatter,
not learnable structure (F79, F81). **The method is locked and is NOT changed to
rescue Reno.** A sealed-test failure at Reno is an **expected, legitimate result
of record** — the honest "the method has an edge, and here it is" data point.
The bar is judged as-is (D22, SPEC 5.3).

Before starting, read SPEC.md, STATUS.md, DECISIONS.md in full — **D39 above
all** (Dubbo's lock), since this mirrors it. Critical rules (SPEC 2) apply.

DECISIONS is append-only. One SPEC edit is authorised (A-2 below); no other.

---

## The principle

For Reno, **the location and the target hour change** (20:00 UTC, D42) — nothing
else, exactly as DSM and Dubbo changed them. Reno's lock is the locked recipe
(D21/D31/D35/D39) with the airport and target hour swapped and nothing else
touched. **Crucially, the poor rehearsal does not change the recipe** — same
model, same features, same settings. Writing it out is so Reno's test executes a
Reno-named record.

## Task A-1 — write the Reno method lock (append to DECISIONS, suggest D44)

Mirror D39 point for point. State, for Reno specifically:

- **Target:** temperature at **20:00 UTC** (local standard noon, Pacific, D42) at
  **Reno, Nevada (KRNO / NV_ASOS)**, coordinates from SPEC 3.4. One row per day.
- **What the model predicts:** the residual (observed − forecast); corrected =
  forecast + predicted residual. Unchanged.
- **Features:** the D19 set — forecast temperature, season sin, season cos.
  Identical. **Not changed despite the rehearsal** (adding features would be
  moving the goalposts; richer features are a separate future direction, not a
  rescue).
- **Model and settings:** the exact session-05 settings — LightGBM,
  `objective=regression_l1`, 300 trees, lr 0.05, 15 leaves, min 40
  samples/leaf, seed 42, deterministic. Unchanged. Versions per requirements.txt.
- **Training data for the test:** the **full D13 window 2021-03-24 to
  2025-07-31** at Reno — inner-training plus validation recombined, as D39.5.
  State the expected training-row count from session 27's join (1,203 inner +
  365 validation = 1,568, confirm) and that the test number will not match
  session 27's 1.499 rehearsal figure.
- **Test data:** Reno's **2025-08-01 to 2026-07-31** (D13), opened for the first
  time, nothing after.
- **Pairing / missing data:** D14 pairing at the **20:00 UTC** target (Reno
  reports at `:55`, a 5-minute offset), drop-count-report (2.2), nothing filled.
  **Predict the test-year drops before the look**, from session 26's gap map
  (F74–F77): the 492-hour gap is entirely in training, so **0 forecast-gap
  days** in the test year; Reno's observation losses at the 20:00 target were
  training-only, so state the expected test-year observation-side count (from
  the gap map) and the resulting paired/scored row prediction. A count that will
  not reconcile is a stop signal.
- **Baselines:** raw GFS, persistence (previous day's 20:00 observation —
  2025-08-01's "yesterday" is 2025-07-31, in training, legal), climatology
  (Reno training-window only), mean-bias reference (Reno training-window only).
- **The bar:** corrected MAE beats **raw GFS and persistence** over Reno's test
  year (qualitative, D22). **Record explicitly that raw GFS is the half most
  likely to fail here**, given the rehearsal — and that failing it is a
  legitimate, honestly-reported outcome, not something to fix.
- **One look only** (mirror D39.10): opened once, run once, result stands.
- **Deviation is a stop signal** (mirror D39.11).

**Record the near-constant-bias / overfit watch-item explicitly (inside D44 or
beside it).** Session 27 found Reno's rehearsal gain was overfitting a
near-constant bias that didn't survive to validation (F81). Record that if the
test also fails to beat raw GFS, this is the expected reason — not a bug to
hunt. Pre-recording it keeps the post-test read honest.

## Task A-2 — clear the stale SPEC Reno entry (authorised)

Session 27's consistency check found SPEC §6's Reno entry still reads "Not yet
joined, rehearsed, locked or tested" — now stale (Reno has been joined and
rehearsed). Update §6's Reno bullet to reflect its actual progress (verified,
pulled/mapped, rehearsed — with the honest note that the rehearsal did not beat
raw GFS; lock and test pending), mirroring the other bullets' style. This is the
only SPEC edit authorised this session. (SPEC §3.4's "in progress" and §5.0's
missing Reno row remain accurate for now — leave them.)

## Task A-3 — verify the lock is a faithful copy

Point-by-point correspondence check against D39: show D44 is identical **except**
the location (YSDU→KRNO, coordinates, `:00`→`:55` reporting) **and the target
hour** (02:00→20:00 UTC). Confirm **no methodological choice differs** — in
particular, confirm the features and settings are unchanged despite the poor
rehearsal. If anything else differs, stop and flag it.

## Task A-4 — stop

Do not open Reno's test year. Do not run any model.

---

## What to report at the end

- the full D44 lock text;
- the correspondence check showing only location and target hour differ (and
  confirming features/settings unchanged despite the rehearsal);
- the near-constant-bias watch-item as recorded;
- the SPEC §6 before/after;
- explicit confirmation no model was run and Reno's test year was not touched.

## What NOT to do

- Do not open, load, or evaluate Reno's test year.
- Do not run, fit, or refit any model.
- Do not change any methodological choice — location and target hour only. In
  particular, do NOT add or change features to improve Reno's odds.
- Do not edit SPEC beyond A-2. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: Reno's method is locked (point to D44); the next session is
   Reno's single sealed-test evaluation, executing D44, with a failure against
   raw GFS an expected and legitimate possible outcome.
2. Ensure DECISIONS carries D44 and the watch-item.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
