# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 17 August 2026 (after session 11)._

---

## Current stage

**Stage 2 — a second airport, Paris Charles de Gaulle (CDG / LFPG). OPEN.** The
owner opened it in session 08 (DECISIONS **D26**, which closes Q17). Its job is
to prove the recipe travels: the same method that worked at London City, run at
a genuinely different location, with **only the location changed**. The target
stays 12:00 UTC on purpose.

Session 08 was the verify-on-contact check, mirroring session 01 for EGLC.
**Both data sources carry CDG and are usable** (DECISIONS F17–F21).

Session 09 then did the stage 2 design, as documentation: **SPEC is now written
per airport rather than for one airport** (DECISIONS D28). Shared rules are
stated once and per-airport facts live in a new airport table (SPEC 3.4) with a
row each for EGLC and LFPG. There is no separate "stage 2 section" and that is
deliberate — opening stage 2 meant adding a row, not adding a design.

Session 10 then pulled **the full CDG history for both sources** and mapped
every gap (DECISIONS **F22–F26**). The dataset is on disk, complete and
provenance-stamped. **CDG's forecast series has exactly the same 492-hour gap as
EGLC's, hour for hour** (F22), and the observation record loses only **three
days** at 12:00 UTC across five years (F25).

Session 11 then did the **CDG join and validation rehearsal**, mirroring session
04/05 (DECISIONS **F27–F29**). The two LFPG series are joined at 12:00 UTC, every
dropped day reconciles exactly against session 10's gap map, and the locked D21
method — applied unchanged, only the location different — **beats all four
references on CDG's validation year**. CDG's test year was not touched.

**The CDG rehearsal headline:** over the validation year 2024-08-01 to
2025-07-31, on 365 days, mean absolute error in degrees Celsius —

```
Raw GFS 1.426 | Persistence 2.523 | Climatology 3.293
Mean-bias reference 1.435 | ML-corrected 1.377
```

The correction beats raw GFS by 0.050 degC (3.5%), persistence by 1.147 degC
(45.4%) and the mean-bias reference by 0.058 degC (4.1%). **This is a rehearsal,
not the frozen bar — stage 2 has NOT passed.** See DECISIONS **F29**.

**CDG's test year has still never been opened.** The sealed-test look comes in a
later session.

**Stage 1 — one model, one airport, one fixed hour. PASSED** and closed. (See
SPEC section 6.) The sealed test ran in session 07 and the corrected forecast
beat both raw GFS and persistence. Nothing about it is to be re-run or revisited.

**The Stage 1 headline result:** over the held-out year 2025-08-01 to
2026-07-31, on 363 days, mean absolute error in degrees Celsius —

```
Raw GFS 1.242 | Persistence 2.096 | Climatology 2.972
Mean-bias reference 1.234 | ML-corrected 1.040
```

The correction beat raw GFS by 0.202 degC (16.3%) and persistence by 1.056 degC
(50.4%), so the frozen bar (SPEC 5.3) is met. See DECISIONS **F16** for the full
result and the honest reading of it.

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

- **Session 06 — housekeeping and the method lock. Done. No model was run and
  the test year was not touched.**
  - **THE METHOD IS LOCKED (DECISIONS D21).** One entry now fully specifies
    what the sealed-test session will run: the target (12:00 UTC at EGLC), the
    exact LightGBM settings from session 05, the D19 three features, the
    training data, the D14 pairing and drop-count rule, the four references,
    the bar, and the rule that the test year is opened once and the result
    stands. It also says that any deviation during the test session is a stop
    signal — raise it with the owner, do not decide with the test year open.
  - **The one substantive choice inside the lock:** the test model is refitted
    on the **full D13 training window (2021-03-24 to 2025-07-31)** — that is
    inner-training plus the validation year recombined. Validation has done its
    job now that the method is fixed. The consequence is recorded openly: the
    tested model is the same recipe on about 20% more data, so the test number
    will not match session 05's validation number, and should not be expected
    to.
  - **Three authorised SPEC edits, and no others:**
    - **5.3 (A-1, Q13):** the success bar is now stated as **qualitative and
      staying that way** — no numeric margin, ever. The old sentence allowing a
      figure to be fixed "just before the model is run" is gone, because
      validation results now exist and no number chosen today could be a clean
      before-the-fact choice (DECISIONS D22).
    - **5.2 (A-2, Q14):** the **mean-bias reference** is now a listed baseline,
      described plainly, and marked **informative only** — the pass/fail bar
      stays raw GFS plus persistence (DECISIONS D23).
    - **3.2 (A-3):** one clause added recording the single **492-hour forecast
      gap** (2023-12-30 to 2024-01-19, training window only), so the archive is
      no longer described in a way that reads as continuous (DECISIONS D25).
  - **`requirements.txt` created (Q16).** Exact versions pinned, with a comment
    explaining the OpenMP (`libomp`) requirement and how it is currently
    satisfied on this machine. No script behaviour changed (DECISIONS D24).
  - **Q13, Q14 and Q16 closed.**

- **Session 07 — THE SEALED-TEST EVALUATION. Done. Stage 1 PASSED.**
  - **The test year was opened for the first and only time** (2025-08-01 to
    2026-07-31). The two 2026 raw chunk files had never been read before this
    session. The locked method (DECISIONS **D21**) was executed exactly as
    written. Nothing was decided, tuned, swapped or re-run.
  - **The script checks itself against the lock before running anything.** All
    22 values D21 fixes matched. The model settings matched session 05's setting
    by setting, with zero differences. The shared code (`all_days`,
    `year_fraction`, `features`, `mae`, `describe`) is character-identical to
    session 05's, and the three functions that do differ have their full diffs
    printed in the output — the lifted seal on both loaders, and the climatology
    function's rename.
  - **Refitted on the full training window** 2021-03-24 to 2025-07-31, which is
    inner-training plus the validation year recombined (D21.5). **1,569 rows**
    out of 1,591 calendar days. That reconciles exactly against the published
    session 04/05 counts (1,205 + 364 = 1,569), which is the check that the
    harness has not drifted.
  - **Test-year drop count: 1 day of 365.** 2025-11-21 had no usable
    observation. Scoring loses one more day, 2025-11-22, because persistence
    needs the previous day's observation. So all five methods are scored on the
    same **363 days**. Nothing was filled (SPEC 2.2).
  - **The verdict, plainly: the bar is met.** MAE in degrees Celsius —
    ```
    Raw GFS 1.242 | Persistence 2.096 | Climatology 2.972
    Mean-bias reference 1.234 | ML-corrected 1.040
    ```
    Beats raw GFS by 0.202 degC (16.3%) and persistence by 1.056 degC (50.4%).
    Also beats the mean-bias reference by 15.7%, which is the comparison that
    shows the model learned real structure rather than a constant offset — the
    constant available to take was only -0.148 degC.
  - **The correction helped in all four seasons**, the first time that has
    happened. Winter is now a dead heat (0.745 against 0.752) instead of a loss.
    Summer carries the result: 1.252 against 1.870, better by 0.618 degC.
    Day by day it was closer than raw GFS on 221 of 363 days (60.9%).
  - **The honest reading of the bigger margin.** Validation gave 6.0%; the test
    gave 16.3%. Most of that gap is the weather, not the model. Raw GFS was
    almost equally hard overall (1.242 against 1.239) but its error sat in a
    different place: test-year summer was harder for GFS (1.870 against 1.498),
    and summer is exactly where the correction works, while test-year winter was
    easier (0.752 against 0.972), so the season the correction used to lose had
    less to lose. The extra 30% of training data helped a little too. Fair
    summary: the method wins on both years, by 6% on one and 16% on the other.
  - **Run once, not repeated.** D21.10 says the method runs once, so no second
    run was made to confirm byte-identical output. Determinism rests on the fixed
    seed, `deterministic=True`, `n_jobs=1`, the pinned versions, and the
    byte-identical repeats already recorded in F14 and F15.
  - **No SPEC edit was made** and none was authorised. The bar was judged as
    written.
  - Full real output in `notes/session-07-check-output.txt`; the script is
    `scripts/session07_test.py`. The result of record is DECISIONS **F16**.

- **Session 08 — STAGE 2 OPENS: CDG verified on contact. Done. Small samples
  only; nothing was pulled in full, joined, built or trained, and nothing from
  stage 1 was touched or re-run.**
  - **Owner's decisions recorded (DECISIONS D26–D27).** **D26 opens stage 2 at
    Paris Charles de Gaulle (CDG / LFPG)** — same target hour (12:00 UTC), same
    model and settings, same D19 features, same D13 split dates, same D14
    pairing rule, same frozen bar, with **only the location changed**, so that
    if the result differs the location is the only thing that can explain it.
    **Q17 is closed.** **D27** records, without acting on it, that stage 3's
    pooled target hour will be **solar standard noon** with daylight saving
    deliberately ignored.
  - **Six raw files pulled**, each with a `.meta.txt` beside it recording the
    pull time and the exact request (SPEC 2.3): three Open-Meteo forecast
    samples, two IEM observation samples, one IEM observation side-file, plus
    the IEM station metadata the coordinates came from.
  - **The station position used, from IEM's own metadata (F17):** lat 49.0153,
    lon 2.5344, elevation 109 m. The session prompt's approximate figure
    (49.010, 2.548, ~119 m) sits 1.15 km away and 10 m higher; IEM's was used,
    as the prompt asked. LFPG is **328 km from EGLC and 104 m higher** — a
    genuinely different setting, which is the point.
  - **Forecast source verified (F17, F20).** The grid point returned is lat
    49.027008, lon 2.578125, elevation 109 m — **3.44 km from the airport with
    no height mismatch**, slightly better than EGLC's 4.33 km. The recent
    sample is 504 rows with 0 missing. The archive begins at **2021-03-24 00:00
    UTC, the very same hour as EGLC**, with 1–7 March 2021 coming back all-null
    exactly as F1 found. **So the D13 split dates carry over to CDG unchanged.**
  - **Truth source verified, and the key CDG unknown answered (F18).**
    **LFPG reports ON THE HOUR (`:00`), not at `:50` like EGLC.** That holds at
    both ends of the period, five years apart: 501 of 504 recent reports and
    334 of 334 early reports are stamped `:00`. **The D14 pairing rule therefore
    needs no adapting — it applies as written and fits CDG better than EGLC**,
    giving an exact 0-minute match instead of a 10-minute offset.
  - **The one qualification worth carrying forward (F18, Q19).** Three recent
    routine reports came in at `:30` instead of `:00`, and D14 correctly drops
    all three. One of them was in the noon hour (2026-07-08, only report 12:30),
    so that day is lost at the target hour: 20 of 21 recent days kept, 14 of 14
    early days kept. The off-hour rate is about **0.60% against EGLC's 0.017%**
    — roughly 35 times higher, though on a three-week sample. Held across the
    whole period that would cost about 12 days at 12:00 UTC, against **none at
    all** at EGLC, where every lost day came from the forecast gap or a missing
    observation instead. Only the full pull can say what the real rate is.
  - **Gap counts, nothing filled (SPEC 2.2).** Recent observation sample: 504
    hours expected, 504 covered, **0 missing**. Early sample: 336 expected, 334
    covered, **2 missing** (2021-03-20 07:00 and 2021-03-30 16:00 UTC).
  - **F19 — LFPG files a scheduled half-hourly report at `:30`** which IEM
    labels "special", the same pattern EGLC shows at `:20` (F3). Recorded, not
    acted on; stage 2 reuses the routine report as the truth observation.
  - **Plain verdict (F21): yes, CDG's data is usable for stage 2 the same way
    EGLC's was.** Every verify-on-contact check passed and nothing found here
    justifies changing any stage 1 decision.
  - **Three new open questions, all the owner's (Q19–Q21):** the off-hour report
    rate and whether D14 should be adapted for CDG (**default: change nothing
    and take the drops**); `gfs_global` versus `gfs_seamless` not re-checked at
    LFPG as F6 said it should be; and whether the 492-hour forecast gap F8 found
    at EGLC is present at LFPG too.
  - **No SPEC edit was made and none was authorised.** The stage 2 SPEC design
    is deliberately not written yet — it comes after verification, which is what
    this session was.
  - Full real output in `notes/session-08-check-output.txt`; the script is
    `scripts/session08_checks.py`.

- **Session 09 — SPEC generalised to many airports. Documentation only. Done.**
  No data was pulled, no code was written or run, nothing was joined, built or
  trained, and no result changed.
  - **SPEC now describes a per-airport project (DECISIONS D28).** Shared things
    are stated once — the two data sources, the method, the D13 split dates, the
    D14 pairing rule, the missing-data rule, the metric, the baselines and the
    bar. Per-airport things live in a new **airport table at SPEC 3.4** holding
    ICAO code, IEM network, the airport's own position, the forecast grid point
    it maps to, distance and height mismatch, and the minute the station reports
    at. Adding an airport is adding a row.
  - **Nine authorised SPEC edits and no others (E-1 to E-9):** section 1 (the
    project is per-airport, EGLC passed and CDG in progress); 3.1/3.2/3.3 (the
    sources are shared, CDG's archive starts on the same hour, verify-on-contact
    applies to each new airport); the new 3.4 (the table); 4.1 (12:00 UTC at
    every airport, with the stage 3 solar-noon switch noted, D27); 4.3 (the
    split dates are shared, and the D18 rehearsal subdivision is written in);
    4.5 (the pairing rule now names no minute — the minute is a table fact);
    the new 5.0 (the protocol applies per airport, with a results table); 5.3
    (the bar is judged once per airport); 5.4 (the deeper evaluation is now
    optional rather than parked); and 6 (stage 1 done, stage 2 in progress).
  - **The frozen bar's meaning is unchanged — only its scope was generalised.**
    "Stage 1 succeeds if…" became "An airport succeeds if…", over that airport's
    test period. The metric, the four references, the qualitative
    no-numeric-margin rule (D22) and rule 2.4 are all untouched. Nothing was
    added that a result must now clear and nothing was removed.
  - **Two questions closed by owner's decisions.** **Q18 closed by D29:** the
    parked SPEC 5.4 work (skill score, significance, formal season testing) is
    **optional and blocks nothing** — stage 1 passed cleanly and a second
    airport is the stronger robustness check. **Q19 closed by D30:** at CDG the
    off-hour report drops are **taken, and D14 is not adapted for one airport**,
    because a different pairing rule would break the "only the location changed"
    claim stage 2 rests on. The pull session must still count them.
  - **One new open question, Q22.** EGLC's IEM network code `GB__ASOS` came from
    the session 09 prompt and has never come back from IEM — every EGLC request
    this project ever made used `station=EGLC` with no network parameter. It is
    written into the table **marked unverified** rather than stated as fact.
    Nothing depends on it; no request or script uses a network code.
  - No script and no notes file: there was nothing to run and no number to
    produce.

- **Session 10 — THE FULL CDG PULL AND GAP MAP. Done. Nothing was joined,
  built, trained or evaluated, and the test year was not opened.**
  - **The full LFPG history was pulled**, 2021-03-24 to 2026-07-31, both
    sources, six yearly chunks each, mirroring session 03b file for file. 26 new
    files in `data/raw/` — 13 data files with a `.meta.txt` beside every one
    (SPEC 2.3), plus the IEM United Kingdom network listing. `data/raw/` is now
    76 files, 7.6 MB. No retry fired and no rate limit was hit.
    - Forecast: Open-Meteo Previous Runs, `gfs_global`,
      `temperature_2m_previous_day1`, at LFPG's IEM coordinates. **46,944 hourly
      rows returned, 46,452 with a value.**
    - Truth: IEM ASOS routine `:00` METARs for LFPG. **46,903 reports, covering
      46,804 hours.**
  - **Full gap map produced for both series — the session's main deliverable.**
    Saved in `notes/session-10-check-output.txt`; the pull log is
    `notes/session-10-pull-output.txt`. Nothing was filled, counts only
    (SPEC 2.2).
  - **Q21 answered, and the answer is exact (DECISIONS F22). CDG's forecast
    series has EXACTLY the same single gap as EGLC's** — 492 hours,
    2023-12-30 00:00 to 2024-01-19 11:00 UTC, same first missing hour, same last,
    same length, entirely inside the training window, with no gap at all in the
    test window. Every one of the six headline totals matches EGLC's. So the gap
    is a property of the archive, not of a place — the same conclusion F20 reached
    about the March 2021 floor. It should cost 20 days at 12:00 UTC, not 21,
    because the series resumes at exactly the target hour.
  - **Observations: 140 missing hours (0.30%)** in 85 runs, against EGLC's 44
    (0.09%) in 23 (DECISIONS F23). Longest run 32 hours. **The two longest runs
    are not absent data** — on 2022-07-23 and 2022-07-25 the station filed its
    reports at `:30` instead of `:00`, so D14 refuses them and they read as holes.
  - **The D30 count: three days lost at 12:00 UTC to off-hour reporting**, across
    1,956 days — two in training, one in the test year (DECISIONS F25). **F18's
    three-week extrapolation of ~12 days was four times too high.** The real
    off-hour rate is 0.207% (97 of 46,903), not 0.60%, and 40% of those reports
    come from one two-day episode. Crucially, **off-hour reports do not cluster at
    midday** — that was F18's open worry and the five-year data says it was bad
    luck, not a pattern. Every day CDG loses on the observation side is lost to
    this one cause: there is no day in five years with nothing filed in the noon
    hour, and exactly one report in 46,903 carries no temperature. **D30 stands
    unchanged** — the drops are taken.
  - **Q20 closed (DECISIONS F22).** All six chunks were pulled with
    `models=gfs_global` (D16), read back out of the saved `.meta.txt` URLs rather
    than claimed. Noted honestly: the pin is confirmed as *used*, but F6's
    value-by-value `gfs_seamless` equivalence check was **not** re-run at LFPG,
    as the session prompt directed.
  - **Q22 closed (DECISIONS F24).** IEM's United Kingdom listing returns EGLC in
    network **`GB__ASOS`**, at 51.5053 / 0.0553 / 5 m — matching what SPEC 3.4
    already held. The guess was right and is now a checked fact.
  - **Training-window value ranges checked and sane, both in Celsius**
    (DECISIONS F26). The test window's values were not looked at.
  - **Two authorised SPEC edits and no others**, both from the prompt's B-3:
    3.2's "whether CDG has a forecast gap is NOT YET KNOWN" marker replaced by
    the verified answer; 3.4's EGLC network cell drops "(unverified)", with the
    note beneath the table rewritten to match it.
  - Scripts: `scripts/session10_pull.py` and `scripts/session10_checks.py`.

- **Session 11 — THE CDG JOIN AND VALIDATION REHEARSAL. Done. CDG's test year
  was not touched and the frozen bar was not judged.**
  - **The method was reused, not re-chosen.** PART 0 of the script reads
    `scripts/session05_model.py` and compares it with this session's script:
    **0 model settings differ and 0 constants differ**, and six shared functions
    are character-identical. The two loaders differ, with their full diffs
    printed — the station code in the file names and the labels that carry it.
    Two consecutive runs produced identical output apart from the clock time.
  - **The join at 12:00 UTC (DECISIONS F27).** One row per day: date, forecast,
    observation, residual.
    ```
                                             days   kept   drop  no fc  null fc  no obs
    inner-training 2021-03-24..2024-07-31   1,226  1,204     22      0       20       2
    validation     2024-08-01..2025-07-31     365    365      0      0        0       0
    ```
  - **Every drop reconciles exactly against session 10's gap map**, which is the
    check this session existed to make: the forecast gap cost **20 days** (F22
    predicted 20), off-hour reports cost **2 days** — 2022-07-23 and 2022-07-25,
    the two F25 named — and **nothing else was dropped at all**. Both off-hour
    reports exist and carry a temperature; D14 refuses them at 30 minutes out and
    D30 says the drops are taken. Nothing was filled (SPEC 2.2). **CDG's
    validation year loses no day at all**, where EGLC's lost one.
  - **CDG's bias has a different shape from EGLC's (DECISIONS F28).** The same
    near-zero average — mean bias **+0.050 degC** against EGLC's -0.108, so there
    is no constant offset worth taking at either airport — but the structure sits
    somewhere else. EGLC's bias tracked forecast temperature (warm end, ~1.2 degC
    too warm on the hottest days). **CDG's tracks the calendar**: spring +0.614,
    autumn -0.401, a swing of over a degree through the year, with a weaker
    warm-end bias (-0.772) and a cold end that is biased where EGLC's was not
    (-0.687 in the 0–5 degC band). GFS is also simply harder to beat at CDG —
    mean |bias| 1.248 against 1.172.
  - **The rehearsal result (DECISIONS F29).** All five methods on the same 365
    validation days:
    ```
    Raw GFS 1.426 | Persistence 2.523 | Climatology 3.293
    Mean-bias reference 1.435 | ML-corrected 1.377 degC
    ```
    It beats all four: raw GFS by 3.5% (0.050 degC), persistence by 45.4%, the
    mean-bias reference by 4.1%, climatology by 58.2%.
  - **The recipe travels, on a smaller margin.** EGLC's rehearsal won by 6.0%,
    CDG's by 3.5%. CDG is the harder problem on every reference. **The mean-bias
    reference is worse than raw GFS at CDG** (1.435 against 1.426) — the constant
    available is +0.050 degC and applying it hurts slightly, so there is no offset
    for the model to be quietly finding instead of structure.
  - **The seasonal picture is flatter than EGLC's.** The correction helps in
    three seasons of four at both airports, and at both the season it hurts is
    winter — by less at CDG (+0.025) than at EGLC (+0.087). EGLC's win was
    essentially a summer win; CDG's is spread across spring, summer and autumn.
    Day by day it was closer than raw GFS on 202 of 365 days (55.3%).
  - **The feature importances confirm F28 from another direction.** At EGLC
    forecast temperature carried the most gain (44.3%); **at CDG `season_sin`
    overtakes it** (39.9% against 35.9%). Given the same three features and no
    guidance, the model leant on the calendar at the airport whose bias lives in
    the calendar.
  - **This is a rehearsal, not a verdict.** The frozen bar (SPEC 5.3) is judged
    once per airport (SPEC 5.0), on CDG's own sealed test year, later.
  - **No SPEC edit was made and none was authorised.**
  - Full real output in `notes/session-11-check-output.txt`; the script is
    `scripts/session11_model.py`.

## In progress

- Nothing. Session 11 is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits sessions 08, 09, 10 and 11.
2. **CDG's method lock, then its single sealed test** — the D21-equivalent for
   CDG, followed by the one look. There is **no written test lock for CDG yet**:
   D21 names London City throughout, and D26 says only the location changes, but
   nothing in the log yet says "this is what CDG's sealed-test session will run".
   That is DECISIONS **Q23**, and it is the owner's to answer. Two things it has
   to settle before the test year is opened:
   - whether the lock is written out for CDG as its own entry, the way D21 was
     written before stage 1's test, so no choice is made with the test year open
     (D21.11);
   - whether CDG's test model is refitted on the **full D13 training window**
     (inner-training plus the validation year recombined), as D21.5 did for
     EGLC. If it is, the test number will not match this session's 1.377
     rehearsal figure and should not be expected to.
3. Nothing is pre-committed beyond that.

## Notes

- **Q12 no longer needs a separate answer.** It asked whether to improve the
  method further or go straight to the sealed test. The owner chose to lock and
  test: session 06 wrote D21, so the question is answered by that act.
- **Q13, Q14 and Q16 are closed** by session 06 (D22, D23, D24).
- **Q15 is closed** by session 05 (D20, F15).
- **Q10 and Q11 are addressed** by session 04 (F12, F13). Q10 no longer needs
  a decision — the 20 days were dropped and counted, as SPEC 2.2 requires.
- **Q17 is closed** by session 08 (D26): stage 2 opened, at CDG/LFPG.
- **Q18 and Q19 are closed** by session 09 (D29, D30).
- **Q20, Q21 and Q22 are closed** by session 10 (F22, F24). One honest limit is
  carried rather than left as a question: Q20
  confirms `gfs_global` was the string used, but F6's value-by-value comparison
  against `gfs_seamless` still has not been run at LFPG, so stage 2 cannot make
  that particular by-construction claim the way stage 1 can.
- **Q23 is open**, raised by session 11: CDG has no written test lock, and the
  D21.5 refit question has to be answered for it. It is the owner's to decide,
  and it is what the next session is for.
- **EGLC's test year has been opened, exactly once, in session 07** — the one
  authorised look (D21.10). It was never loaded, printed, averaged or fitted on
  in any earlier session. It is not a held-out set any more, so it must not be
  used to judge any future change to the method. Anything measured on it from
  here on is measured on data the method has been compared against once already.
- **CDG's test year is still sealed, and is now on disk.** The dates are the same
  (2025-08-01 to 2026-07-31, D13) but the data is a different airport's, and it
  has never been looked at. Session 10 pulled it and counted only its structure —
  row presence, gap locations, report timing — never a temperature value, exactly
  as session 03b held EGLC's. **Session 11 did not open it either**: the two 2026
  LFPG chunk files were never read, the 2025 chunk was cut off at 2025-07-31 on
  load, and the script asserts no date on or after 2025-08-01 reached any table.
  Each airport gets its own single look (SPEC 5.0).
