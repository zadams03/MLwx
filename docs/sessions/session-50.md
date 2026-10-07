# Session 50 — E1 upper-air experiment (staged reading, no reserved-year
contact)

**Read `CLAUDE.md`, `SPEC.md`, `STATUS.md`, and live `DECISIONS.md` in full
before starting, per the standing rule.** This session runs the first
feature experiment of the programme: does the upper-air/vertical-structure
family add skill on top of the frozen 5-feature GRIB baseline? It is a
LEARNING experiment, not a pass/fail gate, and it never touches the reserved
year.

---

## Context (why this session, in one paragraph)

Session 49 (F98) built and validated the upper-air dataset: `t925`, `t850`,
`t700`, plus `t2m_raw` and the derived `lapse_rate_t2_t850` (= `t2m_raw −
t850`), joined onto the existing 5-feature GRIB dataset for every date
outside the reserved 2024-25 year. This session fits models on that data to
read the family's contribution. The experiment runs ONLY on the three
non-reserved folds defined in `scripts/session48_reserved_year.py`
(`EXPERIMENT_FOLDS`: 2022-23, 2023-24, and truncated 2025-26). The reserved
2024-25 year (D51) is not read, at all, in this session — the guard exists
to enforce that.

---

## First: two sanity checks before any model is fit

1. **Verify `t2m_raw`'s derivation.** Session 49 derived `t2m_raw` by backing
   the frozen per-airport elevation constant out of the corrected `temp`
   feature, not by a new pull. Assert, per airport, that
   `t2m_raw == temp_corrected − elevation_constant` (correct sign; RNO's
   constant is the large one, +2.044 °C). If this does not hold exactly at
   any airport, STOP and report — the lapse-rate feature is built on
   `t2m_raw`, so a sign or offset error there invalidates the whole
   experiment.
2. **Confirm the guard.** Run every fold's train and test window through
   `assert_reserved_year_excluded()` before fitting anything. All three
   `EXPERIMENT_FOLDS` must pass; if any raises, STOP.

---

## The experiment — fit four variants, read them as a staged progression

Same LightGBM settings as the frozen baseline (D21.4), unchanged. Same
features at every airport — no per-airport feature selection. For each of
the three `EXPERIMENT_FOLDS`, fit and score these four variants:

- **B — baseline (refit).** The frozen 5-feature set (`temp`, `season_sin`,
  `season_cos`, `cloud_cover`, `wind_speed_10m`), REFIT on these exact three
  folds. This is the honest apples-to-apples reference — do NOT reuse F94 or
  F96 numbers, which were fit on different windows.
- **B+L — baseline plus lapse rate.** B plus `lapse_rate_t2_t850` (one added
  feature).
- **B+Lv — baseline plus lapse rate plus raw levels.** B+L plus `t850`,
  `t925`, `t700` (four added features total).
- **B+v — baseline plus raw levels only.** B plus `t850`, `t925`, `t700`,
  WITHOUT the derived lapse rate. (This isolates whether the derived form
  adds anything the raw levels don't already give the model.)

Report, per airport, per fold, and fold-averaged: MAE for each variant, and
each variant's delta vs. B (the refit baseline). Do not compute any
pass/fail verdict — this session reports the grid; the family call is made
in review.

## How to read it (framing for the output — state these explicitly)

- **The staged question is a READING, not an execution gate.** Report all
  four variants; do not stop early. The point is to see (a) does
  `lapse_rate` alone help on top of cloud+wind, and (b) do the raw levels
  add anything beyond the derived lapse rate.
- **DSM is the diagnostic.** Cloud/wind were marginal-to-slightly-negative
  at DSM (F96), so it has the most headroom to distinguish genuinely-new
  signal from piling-on. Read DSM's deltas with that in mind — but the
  primary criterion remains lower MAE across airports (average and
  per-airport), which is the deliverable's real goal.
- **RNO is expected to behave oddly, and that is pre-registered (F98).**
  Reno's 925 hPa surface sits below the station, so `t925` there is a
  below-ground extrapolation and `lapse_rate_t2_t850` is partly degenerate.
  RNO stays in the experiment with the SAME features as every other airport
  — no exclusion, no RNO-specific feature (that would be per-airport
  selection bias and would break "the recipe travels"). Report RNO
  separately and read a small, null, or negative upper-air effect there as
  EXPECTED, not as a failure of the family. Whether the extrapolated value
  still carries usable signal is a genuine empirical question this
  experiment answers.

## Explicitly out of scope — do not do these

- **No reserved-year (2024-08-01→2025-07-31) data read, fit, or scored**,
  ever, this session.
- **No sealed-test-style verdict, no confirmation-year run.** The reserved
  year's one look is the END of the whole programme, not this session.
- **No per-airport feature selection**, no dropping/swapping features for
  RNO or any airport.
- **No E2+ families** (moisture, pressure, radiation, precipitation).
- **No new data pull** — session 49 built everything this needs.
- **No edits to `SPEC.md` or `RESULTS.md`.**
- **Nothing committed.** Prepare everything, write the suggested commit
  message, then stop.

## End-of-session steps

1. Run the experiment script and paste the **real output** — the full
   per-airport / per-fold / fold-averaged MAE grid, actual numbers.
2. Run the standard consistency check across `SPEC.md`, `STATUS.md`, and
   live `DECISIONS.md`; report only.
3. Add a `DECISIONS.md` finding (next F-number) recording the four-variant
   grid, the two sanity-check results, and a plain-language read of what the
   upper-air family did per airport — leading with the number you can
   defend, honest about DSM and RNO. State that no model saw the reserved
   year.
4. Archive step: check whether anything is now settled; if not, say so.
5. **Overwrite `STATUS.md` and end it with a "Next planning session" line.**
   Name the likely next step (family verdict + whether E1 moves to a
   cumulative combine or to E2 moisture) as an open question for review, not
   a decided direction.

---

## One-line invocation for Claude Code

> Read CLAUDE.md, then SPEC.md, STATUS.md, and DECISIONS.md in full. Then
> carry out the session defined in docs/session-50.md, staying strictly
> within its scope. Stop at the end-of-session steps and wait for my review
> -- do not commit anything.
