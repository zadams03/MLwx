# Session 49 — Build and validate the upper-air/vertical-structure feature
set (E1, data build only — no modeling)

**Read `CLAUDE.md`, `SPEC.md`, `STATUS.md`, and live `DECISIONS.md` in full
before starting, per the standing rule.** This session is scoped narrowly on
purpose: it builds and validates a dataset. It does not run a model, compute
an MAE, or touch the reserved year. That comes in session 50.

---

## Context (why this session, in one paragraph)

The feature-selection programme (agreed after session 48, see DECISIONS)
runs experiments E1–E5 against the frozen 5-feature GRIB baseline (SPEC
7.2). E1 is upper-air/vertical structure — the family session 47's
availability probe (F97) confirmed is present, identically labelled, and
clean at the forecast lead, back to the v16 floor. This session pulls those
fields for real, joins them to the existing dataset, and validates the
join. Session 50 will run the actual staged experiment (baseline refit,
then lapse-rate-alone, then — only if needed — the full family) on the
dataset this session produces.

---

## Scope — do exactly this, nothing more

1. **Pull three new fields** for every airport, at the airport's own
   already-established grid point and forecast lead: `TMP` at 850, 925, and
   700 hPa. Use the exact GRIB level identifiers F97 already confirmed
   (session 47's availability map — reuse those labels verbatim, do not
   re-derive them).
2. **Reuse the existing pipeline unchanged**: same lead-time convention
   (cycle `floor(HH/6)*6` UTC the day before, forecast hour `24 + (HH mod
   6)` — D48.2/F89), same bilinear horizontal interpolation to each
   airport's established grid point, same source (`noaa-gfs-bdp-pds`).
3. **Do NOT apply the surface elevation lapse-rate correction (7.429
   °C/km) to these three fields.** That correction exists because GFS's
   *surface* grid cell sits at the wrong elevation versus the airport
   (7.2). 850/925/700 hPa are fixed pressure surfaces, not tied to surface
   terrain — they need bilinear interpolation only, no elevation
   adjustment. Confirm this understanding in the session's own output
   before writing code, since applying the correction here would be a real
   error, not a style choice.
4. **Derive the lapse-rate feature using the RAW, uncorrected GFS 2 m
   forecast temperature** — not the elevation-corrected value already used
   as the 5-feature model's `temp` feature. Physically, 850 hPa temperature
   is a raw model output; pairing it with the elevation-adjusted surface
   value would mix a real atmospheric quantity with a downscaling patch.
   Name columns so this is unambiguous, e.g. `t2m_raw`, `t850`, `t925`,
   `t700`, `lapse_rate_t2_t850` (= `t2m_raw − t850`). Keep the existing
   elevation-corrected `temp` feature untouched and separate.
5. **Date range: every date already in the existing 5-feature dataset that
   falls OUTSIDE the reserved year (2024-08-01 to 2025-07-31).** In
   practice this is the continuous 2021-03-24→2024-07-31 span plus the
   already-pulled 2025-08-01→2026-07-31 sealed-year span. Before pulling
   anything, build the date list and run it through
   `scripts/session48_reserved_year.py`'s `assert_reserved_year_excluded()`
   (or an equivalent per-date check using its constants) — if any reserved
   date is in the list, stop and report it; do not pull.
6. **Join** the three new raw fields (plus the derived lapse rate) onto the
   existing 5-feature dataset by (airport, date/valid-time). Do not touch
   or overwrite any existing column.
7. **Validate, and report real numbers**:
   - Messages requested vs. successfully decoded, per field per airport —
     any drop gets a reason (per SPEC 2.2), not a silent skip.
   - Row counts before and after the join, per airport — flag any airport
     where the join drops rows versus the existing dataset (that would mean
     a date the 5-feature dataset has but upper-air doesn't, worth knowing
     before session 50).
   - Basic sanity ranges per new column (min/max/mean/null count) — 850/925/
     700 hPa temperatures should look like real atmospheric values (roughly
     -40 °C to +25 °C depending on level and season) and should average
     colder with height; flag anything that doesn't.
   - Spot-check at least one row per airport against F97's own confirmed
     sample values or ranges, if F97 recorded specific figures to check
     against.

## Explicitly out of scope — do not do these

- **No model fit, no MAE, no CV, no comparison to the 5-feature baseline.**
  That is session 50.
- **No reserved-year (2024-08-01→2025-07-31) data pulled or touched, at
  all**, even just to inspect it.
- **No moisture, pressure, or other E2+ features.** Upper-air only.
- **No refitting or re-running the frozen 5-feature sealed-test script.**
- **No edits to `SPEC.md` or `RESULTS.md`.**
- **Nothing committed.** Prepare everything, write the suggested commit
  message, then stop, per `CLAUDE.md`.

## End-of-session steps (standard, plus one addition)

1. Run the build/validation script and paste the **real output** — actual
   counts and ranges, not a description of them.
2. Run the standard consistency check across `SPEC.md`, `STATUS.md`, and
   live `DECISIONS.md`; report only, do not fix silently.
3. Add a `DECISIONS.md` finding (next F-number) documenting: what was
   pulled, the exact date range and guard check performed, the join result
   and row counts, and the validation numbers above. State plainly that no
   model was fit and the reserved year was never touched.
4. Archive step: check whether anything in live `DECISIONS.md` is now
   settled per the usual criterion; if not, say so explicitly (as sessions
   47/48 did).
5. **Overwrite `STATUS.md` and end it with an explicit "Next planning
   session" line** naming session 50 (the staged E1 experiment: refit the
   5-feature baseline on the three `EXPERIMENT_FOLDS`, then test
   `lapse_rate_t2_t850` alone against it, then — only if that doesn't
   fully capture the family's contribution — add `t850`/`t925`/`t700`
   directly, all per-airport with DSM as the diagnostic, reserved year
   untouched). This closes the documentation gap noted at the end of
   session 48.

---

## One-line invocation for Claude Code

> Read CLAUDE.md, SPEC.md, STATUS.md, and DECISIONS.md, then execute
> docs/session-49.md in full — this is a data-build-only session, no
> modeling.
