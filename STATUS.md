# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 16 August 2026 (after session 03b)._

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
- **Session 03 — started, stopped partway, superseded by 03b.** It pulled
  four forecast chunks carrying five variables, then was stopped. It found two
  real problems: the extra variables do not exist across the archive, and
  there is a big gap in the forecast series around the 2023/2024 year end. It
  did make the authorised SPEC 3.2 edit, which stands. Its partial chunks were
  never committed and were discarded before the 03b pull.
- **Session 03b — the full historical pull, temperature-only. Done.**
  - **Owner's decisions recorded (DECISIONS D16–D17):** the model string is
    pinned to `gfs_global`; stage 1 is temperature-only on the forecast side,
    with the extra variables dropped and noted as a possible later
    enhancement for the recent period only.
  - **Forecast series pulled:** Open-Meteo Previous Runs API, `gfs_global`,
    `temperature_2m_previous_day1`, EGLC, 2021-03-24 to 2026-07-31, in six
    yearly chunks. 46,944 hourly rows returned, 46,452 with a value.
  - **Truth series pulled:** IEM ASOS routine `:50` METARs for EGLC over the
    same period, six yearly chunks. 46,919 reports, covering 46,900 hours.
  - Every one of the 24 new raw files has a `.meta.txt` beside it recording
    the pull time and the exact request (SPEC 2.3). `data/raw/` is 3.7 MB.
  - **Full gap map produced** for both series — the session's main deliverable.
    Saved in `notes/session-03b-check-output.txt`.
    - **Forecast: exactly one gap**, 492 hours, 2023-12-30 00:00 to
      2024-01-19 11:00 UTC. All of it falls in the training window; the test
      window has no forecast gap at all. See DECISIONS F8.
    - **Observations: 44 missing hours (0.09%)** in 23 short runs, longest
      8 hours, no run of a day or more. See DECISIONS F9.
    - Nothing was filled. Counts only (SPEC 2.2).
  - **Training-window value ranges checked** and sane, both in Celsius
    (DECISIONS F10). The test window's values were not looked at.
  - **Q7, Q8 and Q9 all closed.**

## In progress

- Nothing. Session 03b is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits session 03b.
2. **Build the stage 1 pipeline.** Join the two series using the D14 pairing
   rule (routine `:50` report to the forecast hour, drop and count anything
   with no report within 15 minutes), pick the fixed hour of the day for the
   stage 1 target (SPEC 4.1), then train the correction model and compare it
   against raw GFS and persistence (SPEC 5).
3. The test window stays sealed until that final comparison.

## Notes

- Open questions still with the owner: **Q10** (the 492-hour forecast gap sits
  entirely in one winter of the training window — dropping it is the default,
  but the loss is concentrated rather than spread), **Q11** (the forecast never
  gets as cold as the station does; expected, and it is the bias we are here to
  correct, but the owner may want a look before modelling).
- Nothing is blocked. The dataset is complete and ready to join.
