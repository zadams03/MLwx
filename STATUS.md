# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 16 August 2026 (after session 01)._

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
- **Session 01 — first real data pull and the two verify-on-contact checks.**
  - Folders created: `data/raw/` for untouched pulls, `scripts/` for code,
    `notes/` for written summaries.
  - Forecast sample pulled: Open-Meteo Previous Runs API, GFS, 2 m
    temperature at a 1-day offset, EGLC, 1–21 July 2026. 504 hourly rows,
    no missing values.
  - Truth sample pulled: IEM ASOS routine METARs for EGLC over the same
    period. 504 hourly rows, no gaps.
  - Every raw file has a `.meta.txt` beside it recording the pull time and
    the exact request (SPEC 2.3).
  - **Q1 answered — yes, with a correction to the start date.** 1 March 2021
    returns nothing. The archive's first hour is **24 March 2021 00:00 UTC**.
    See DECISIONS F1.
  - **Q2 answered — the observation record is good.** Recent sample: 0 gaps
    in 504 hours. Early-period sample (18 March – 1 April 2021): 3 gaps in
    336 hours (0.89%). See DECISIONS F2.

## In progress

- Nothing. Session 01 is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits session 01.
2. Then: build the stage 1 pipeline (pull forecast, pull truth, join, learn
   the correction, evaluate against the baselines).
3. Before the join, the owner needs to settle Q3 (how to line up an
   observation timed at :50 with a forecast valid on the hour). See
   DECISIONS.

## Notes

- Both verify-on-contact checks (Q1, Q2) are now closed. No decisions are
  blocked.
- Session 01 raised three new open questions for the owner: Q3 (timestamp
  alignment), Q4 (what lead time `previous_day1` really is), Q5 (the model
  grid point sits about 4 km from the airport). None were acted on.
