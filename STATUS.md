# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 16 August 2026._

---

## Current stage

**Stage 1 — one model, one airport, one fixed hour.** (See SPEC section 6.)

## Done

- Project aim agreed and written to SPEC.
- Data sources chosen and checked to exist:
  - Truth: IEM ASOS/METAR for EGLC — confirmed live and free.
  - Forecast: Open-Meteo Previous Runs API, GFS, 24h offset — confirmed back
    to March 2021.
- Evaluation bar agreed and frozen (SPEC section 5): beat raw GFS and
  persistence on MAE, over a held-out ~12-month test period. Numeric margin
  left qualitative for now.
- Missing-data rule agreed: drop, count, report — never fill (SPEC 2.2).
- Working-practice files created (SPEC, STATUS, DECISIONS, CLAUDE).

## In progress

- Nothing being built yet. No code written.

## Next

1. First real data pull, and the two verify-on-contact checks (SPEC 3.3):
   - confirm Previous Runs API returns history back to 2021;
   - confirm EGLC's observation record is complete enough over the period.
2. Then: build the stage 1 pipeline (pull forecast, pull truth, join, learn
   the correction, evaluate against the baselines).

## Notes

- No decisions are blocked. The only open items are the two verify-on-contact
  checks above, which by design can only be settled by touching real data.
