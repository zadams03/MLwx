# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 16 August 2026 (after session 02)._

---

## Current stage

**Stage 1 — one model, one airport, one fixed hour.** (See SPEC section 6.)

## Done

- Project aim agreed and written to SPEC.
- Data sources chosen and checked to exist:
  - Truth: IEM ASOS/METAR for EGLC — confirmed live and free.
  - Forecast: Open-Meteo Previous Runs API, GFS, 24h offset — confirmed back
    to 24 March 2021.
- Evaluation bar agreed and frozen (SPEC section 5): beat raw GFS and
  persistence on MAE, over a held-out 12-month test period. Numeric margin
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
- **Session 02 — decisions locked, documentation verified, `.gitignore`
  added.** No data was pulled for the dataset; nothing was built or joined.
  - **Owner's decisions recorded (DECISIONS D13–D15):** the train/test split
    is now fixed dates (train 2021-03-24 to 2025-07-31, test 2025-08-01 to
    2026-07-31); the observation-to-forecast pairing rule is written down;
    raw data is committed to version control.
  - **SPEC edited, only where authorised:** 3.2 now says 24 March 2021; 4.3
    carries the fixed split dates; a new 4.5 records the pairing rule; 5.3
    notes the split date is fixed, with the bar itself untouched.
  - **Q3 closed** by D14 (pairing rule). **Q5 closed** and accepted (the 4 km
    grid offset is the kind of local error the project exists to learn).
    **Q6 closed** by D15 (raw data is committed).
  - **Q4 answered, with a caveat (DECISIONS F5).** `previous_day1` is a
    *nominal* 24-hour lead, not an exact one: each 6-hourly GFS run supplies
    its hours 24–29, so the real lead sweeps between about 24 and 30 hours
    through the day. Every value is still a genuine forecast made at least
    24 hours ahead, so there is no leakage.
  - **Model string checked (DECISIONS F6).** At EGLC, `gfs_seamless` is
    purely NCEP GFS — the other NCEP models are United-States-only — and it
    returns data identical to the explicit `gfs_global` string over both a
    2026 and a 2021 window. `gfs_global` is recommended for the session 3
    pull, awaiting the owner's confirmation.
  - `.gitignore` added at the project root: macOS and Python clutter ignored,
    `data/raw/` deliberately not ignored.

## In progress

- Nothing. Session 02 is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits session 02.
2. **Owner confirms Q8 — the model string for the full pull** (`gfs_global`
   is recommended; `gfs_seamless` is the session 01 status quo). This must be
   settled before session 3, because it is baked into every raw file.
3. **Session 3 — the full historical pull.** Pull the forecast series and the
   observation series across the whole period (2021-03-24 to 2026-07-31),
   into `data/raw/` with `.meta.txt` beside each file. Still no joining, no
   model.
4. Then: build the stage 1 pipeline (join, learn the correction, evaluate
   against the baselines).

## Notes

- Open questions still with the owner: **Q7** (should SPEC's "24-hour lead"
  wording be made more precise, given F5?), **Q8** (which model string),
  **Q9** (`.DS_Store` is already tracked, so the new ignore rule cannot
  remove it without a `git rm --cached`).
- Nothing is blocked except the session 3 pull, which waits on Q8.
