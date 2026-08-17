# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 17 August 2026 (after session 05)._

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
- **Session 04 — the first modelling session: join, bias look, and a
  validation rehearsal. Done. The test year was not touched.**
  - **The target hour is now named: 12:00 UTC** (SPEC 4.1, the one authorised
    SPEC edit this session). Chosen on principle before any model was built.
  - **Owner's decisions recorded (DECISIONS D18–D19):** the evaluation is
    rehearsed on a validation year taken from inside training
    (inner-training 2021-03-24 to 2024-07-31, validation 2024-08-01 to
    2025-07-31), so the sealed test year is looked at exactly once, later; and
    the stage 1 feature set is minimal — forecast temperature plus season as
    sine/cosine, no hour-of-day, no recent-observation feature.
  - **The two series are joined at 12:00 UTC** using the D14 pairing rule (the
    11:50 routine report is the observation for 12:00). One row per day:
    date, forecast, observation, residual.
    - inner-training: 1,226 days, **1,205 rows kept**, 21 dropped.
    - validation: 365 days, **364 rows kept**, 1 dropped.
    - Every drop is accounted for and nothing was filled (SPEC 2.2). See
      DECISIONS F12.
  - **Q10 addressed.** The 492-hour forecast gap costs **20 days**, not 21 —
    the series resumes at 2024-01-19 12:00 UTC, exactly the target hour, so
    that day survives. Dropped and counted.
  - **Q11 addressed, and the expectation was wrong (DECISIONS F13).** At 12:00
    UTC the *cold* end is not the biased end. The forecast is near-unbiased
    below 10 degC and there is barely a cold tail at all. The bias is at the
    **warm end**: on the hottest days GFS runs about **1.2 degC too warm**.
    F10's cold-end shift came from the night-time hours stage 1 does not
    target. Overall mean bias is only -0.108 degC, so there is almost no
    constant offset to correct — the structure is all in how the bias varies.
  - **F1 corrected (DECISIONS F11).** F1's claim that the forecast archive is
    "continuous from that start" is wrong and is superseded by F8. F1 itself is
    left as written; the log is append-only.
  - **The model was built and rehearsed (DECISIONS F14).** LightGBM
    gradient-boosted trees, fixed settings, fixed seed, fitted on
    inner-training only. Nothing tuned. Two runs byte-identical.
    Validation MAE over the same 363 days:
    ```
    Raw GFS 1.239 | Persistence 2.226 | Climatology 2.865
    Mean-bias reference 1.231 | ML-corrected 1.190 degC
    ```
    It beats all four: raw GFS by 4.0%, persistence by 46.5%, the mean-bias
    reference by 3.3%, climatology by 58.5%. So it is learning structure, not
    just a constant offset. But the total gain over raw GFS is small
    (0.049 degC), and it is essentially a summer win — the correction makes
    winter and spring very slightly worse.
  - **This does not mean stage 1 has passed.** It is a rehearsal. The frozen
    bar (SPEC 5.3) is judged once, on the sealed test year, in a later session.
  - Full real output in `notes/session-04-check-output.txt`; the script is
    `scripts/session04_model.py`.
- **Session 05 — the objective fix (Q15). One change only. Done. The test year
  was not touched.**
  - **Owner's decision recorded (DECISIONS D20):** the model is now fitted on
    **absolute error** (`objective="regression_l1"`) instead of squared error.
    SPEC 5.1 measures absolute error, so the model is now trained on the same
    thing it is judged on. A correctness fix, not tuning.
  - **Nothing else changed**, and the script proves it rather than claiming
    it: `scripts/session05_model.py` reads the session 04 script and compares
    the two setting by setting, constant by constant, and function source
    character by character. Exactly **one setting differs** — the objective.
    Parts A and B of the output (the join, the drop counts, the bias tables)
    are character-identical to session 04's output file. Two consecutive runs
    matched apart from the clock time in the header.
  - **Validation MAE, the same 363 days, same harness:**
    ```
    Raw GFS 1.239 | Persistence 2.226 | Climatology 2.865
    Mean-bias reference 1.231 | ML-corrected 1.165 degC
    ```
    The four non-ML figures are unchanged to three decimals, which is the
    cross-check that the harness is identical. Only the ML row moved.
  - **The fix helped a little: 1.190 → 1.165 degC, 0.025 better (2.1%).** The
    win over raw GFS goes from 4.0% to 6.0% (0.074 degC). It still beats all
    four references, by wider margins than before.
  - **The seasonal picture improved more than the headline did.** Session 04
    was a summer win with winter and spring slightly worse. Now the correction
    helps in **three seasons out of four**: spring flips to slightly better,
    summer and autumn improve further, and winter is still worse than raw GFS
    but by less (+0.096 → +0.087).
  - Read honestly: the gain is real but small, and it did not change the
    character of the result. The model also fits its own training data *less*
    tightly than before (in-sample 0.857 → 0.879) while doing better on
    validation — the ordinary sign of a less over-fitted model. See
    DECISIONS F15.
  - **Q15 closed.** Still a rehearsal — the frozen bar (SPEC 5.3) has not been
    judged and stage 1 has not passed.
  - Full real output in `notes/session-05-check-output.txt`; the script is
    `scripts/session05_model.py`.

## In progress

- Nothing. Session 05 is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits session 05.
2. **Then the owner's judgement call (DECISIONS Q12, now with a better
   number): is the rehearsal good enough to lock the method?** The validation
   win over raw GFS is now 6.0% (0.074 degC) rather than 4.0%, and the
   correction helps in three seasons out of four rather than two.
   - If **yes** → lock the method, do the housekeeping the owner wants first
     (Q13, Q14, Q16 — the numeric margin, the mean-bias baseline, the
     `requirements.txt`), then the **single sealed-test evaluation**. That
     session opens the test year (2025-08-01 to 2026-07-31) for the first and
     only time, re-fits on the full D13 training window, and judges the frozen
     bar (SPEC 5.3). That look happens once, so the method must be locked
     before it starts.
   - If **no** → one more session improving the method against the
     **validation** year, which is allowed as often as needed. The sealed test
     year stays sealed either way.
3. The test year is untouched and stays that way until the owner opens it.

## Notes

- Open questions now with the owner: **Q12** (is the rehearsal — now a 6.0%
  win — enough to lock the method, or is another improvement session worth it
  first?), **Q13** (should SPEC 5.3 gain a numeric margin, given validation
  results now exist?), **Q14** (should the mean-bias reference become a listed
  baseline in SPEC 5.2?), **Q16** (LightGBM needed an OpenMP library this
  machine does not have; the workaround is documented, and there is no
  `requirements.txt` recording the library versions).
- **Q15 is closed** by session 05 (D20, F15).
- **Q10 and Q11 are addressed** by session 04 (F12, F13). Q10 no longer needs
  a decision — the 20 days were dropped and counted, as SPEC 2.2 requires.
- Nothing is blocked.
