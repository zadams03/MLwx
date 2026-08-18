# STATUS.md — where the project is right now

Read this to catch up fast. It records what is done, what is in progress, and
what is next.

_Last updated: 18 August 2026 (after session 15)._

---

## Current stage

**A THIRD AIRPORT IS OPEN: Des Moines, Iowa (DSM). Verified, pulled in full,
and gap-mapped. Not yet joined, built or trained.** The owner opened it in
session 14 (DECISIONS **D32**), which is the "more airports first" branch of Q24
rather than stage 3. **Stage 3 is not opened and nothing about it has been
written or started.**

**SPEC now describes an open-ended list of airports with a per-airport target
hour (DECISIONS D34).** Session 15's first job was to generalise it rather than
patch it: the target hour is now a column in the SPEC 3.4 airport table (12:00
UTC for EGLC and LFPG, 18:00 UTC for DSM), section 4.1 states the principle —
one fixed hour per airport, at that airport's local midday — instead of naming
one hour for everybody, and **stage 2 is reframed from "the second airport" to
"individual airports, two or more"**, holding CDG, DSM and any that follow.
**The frozen bar's meaning is unchanged**; only its scope and the hour
convention moved, and that was checked section by section.

**Why DSM.** F30 recorded the honest limit on stages 1 and 2: EGLC and LFPG are
328 km apart and were tested on **the same twelve months**, so the two wins lean
on one western-European weather year seen twice, not on two independent draws.
Des Moines is 6,754 km from EGLC in the flat continental interior of the United
States, where a summer has little to do with a summer in London or Paris. It is
the easy off-continent step — well behaved, GFS-friendly, and on IEM's home
network — taken before harder airports and before any pooling.

**The one thing that is not reused: the target hour (DECISIONS D33).** DSM's
standard-time offset is UTC−6, so 12:00 UTC there is 06:00 local — dawn, exactly
the part of the day SPEC 4.1 chose 12:00 UTC to avoid in Europe. **DSM's target
is local standard noon, 18:00 UTC**, with daylight saving deliberately ignored so
it stays a fixed UTC hour all year. That is D27's convention brought forward.
**The honest consequence is written into D33: DSM changes both the location and
the target hour, so D26's "only the location changed" does not strictly hold for
DSM, and a DSM result must not be quoted as if it were the same controlled
comparison stage 2 was.**

**Session 14 verified DSM on contact and it passed every check** (DECISIONS
**F31–F37**). Both sources carry it, the archive starts on the same hour as at
the two European airports, the pairing rule needs no adapting, and the US-specific
worries — units and timezone — were measured rather than assumed and need no new
handling.

**Session 15 then pulled DSM's full history and mapped every hour** (DECISIONS
**F38–F41**). Three headline answers:

- **DSM's forecast series has the very same 492-hour gap**, 2023-12-30 00:00 to
  2024-01-19 11:00 UTC, hour for hour, entirely inside the training window, with
  no gap at all in the test window. Three airports on two continents now share
  it, so it is a property of the Open-Meteo archive, not of a place (F38).
- **DSM's observation record is the cleanest of the three** — 11 real missing
  hours in five years (0.02%), against LFPG's 140 and EGLC's 44, with a longest
  run of two hours. **It loses no day at all at its 18:00 UTC target**, so all
  20 expected drops are the shared forecast gap (F39, F41).
- **Q27 answered, and D16's pin earned its keep.** At DSM, `gfs_seamless` is
  **not** the same series as `gfs_global`: on recent dates 259 of 264 hours
  differ, by up to 12.3 degC, from a different grid point. On the 2021 window
  the two are identical, so a comparison run only on old data would have
  concluded wrongly. Every DSM chunk was pulled with `gfs_global`, so nothing in
  the project is affected — but had the project used `gfs_seamless`, DSM would
  quietly not have been GFS at all (F40).

**Stage 2's first airport — Paris Charles de Gaulle (CDG / LFPG). PASSED**
and closed. The owner opened it in session 08 (DECISIONS **D26**, which closes
Q17). Its job was to prove the recipe travels: the same method that worked at
London City, run at a genuinely different location, with **only the location
changed**. The target stayed 12:00 UTC on purpose. The sealed test ran in
session 13 and the corrected forecast beat both raw GFS and persistence.
Nothing about it is to be re-run or revisited.

(**Stage 2 itself is still in progress**, because D34 reframed it as
"individual airports, two or more" rather than "the second airport". CDG is
finished; DSM is the airport now in it.)

**CDG's headline result:** over CDG's held-out year 2025-08-01 to
2026-07-31, on 363 days, mean absolute error in degrees Celsius —

```
Raw GFS 1.396 | Persistence 2.300 | Climatology 3.774
Mean-bias reference 1.389 | ML-corrected 1.208
```

The correction beat raw GFS by 0.188 degC (13.5%) and persistence by 1.092 degC
(47.5%), so the frozen bar (SPEC 5.3, 5.0) is met at CDG too. It also beat the
mean-bias reference by 13.0%, which is what says it learned structure rather
than a constant. See DECISIONS **F30** for the full result and the honest
reading of it — including the caveat that both airports were tested on the
**same twelve months**, so the two test-year margins are largely one weather
year seen twice, not two independent confirmations.

**The recipe travelled, and that is the point of stage 2.** CDG is the harder
problem on every reference — raw GFS 1.396 against EGLC's 1.242, persistence
2.300 against 2.096, climatology 3.774 against 2.972 — and the correction is
worse there in absolute terms (1.208 against 1.040). But **the share of the
error it removes is very nearly the same**: 13.5% against 16.3% on raw GFS, and
47.5% against 50.4% on persistence. Nothing was rebuilt, retuned or adapted for
the second airport.

How the two stages ran, session by session:

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
(45.4%) and the mean-bias reference by 0.058 degC (4.1%). **That was a
rehearsal, not the frozen bar — at that point stage 2 had not passed.** See
DECISIONS **F29**.

Session 12 then **wrote and froze CDG's method lock, DECISIONS D31** — the
D21-equivalent for stage 2, closing **Q23**. No model was run, no data was
loaded, and CDG's test year was not touched. D31 is D21 with the airport swapped
and nothing else: the same target hour, the same three features, the same
LightGBM settings, the same D13 training window refit, the same D14 pairing, the
same four references, the same qualitative bar, the same one-look and
stop-signal rules. It was written out separately rather than by pointing at D21
because D21 names London City throughout, and a test session translating an
EGLC-named record with the test year open would be making a decision (D21.11).

**The lock was verified, point by point.** DECISIONS carries a full D21 ↔ D31
correspondence table covering all 11 sub-points. **No methodological choice
differs.** Everything that differs is the location or follows from it: which
airport it is and where, which files hold its data, that LFPG reports at `:00`
so D14 gives an exact match instead of EGLC's 10-minute offset, and the row and
drop counts that follow from CDG's own record.

**D31 also predicts CDG's test-year drops before the look**, from session 10's
gap map: 0 forecast-gap days, 1 off-hour day (2026-07-08), so 364 paired rows
expected and 363 scored days once persistence loses 2026-07-09. **Session 13
counted them and every line matched** (F30) — which is the strongest single
check in stage 2, because the prediction was written before the look.

Session 13 then **opened CDG's test year, once, and executed D31** (DECISIONS
**F30**). Every one of D31.7's advance drop predictions landed exactly, the
training-window row counts reconciled against session 11's published figures,
and the frozen bar was judged once and met. **CDG's single authorised look has
now been used.**

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

- **Session 12 — CDG'S METHOD LOCK. Documentation only. Done.** No code was
  written or run, no data was loaded, no model was built or refitted, and CDG's
  test year was not opened. No file in `data/raw/` was read.
  - **CDG's method is LOCKED (DECISIONS D31), which closes Q23.** One entry now
    fully specifies what CDG's sealed-test session will run: the target (12:00
    UTC at LFPG, IEM's position and the grid point it maps to), the residual as
    what the model predicts, the D19 three features, the exact session 05
    LightGBM settings, the training data, the D14 pairing and drop-count rule,
    the four references, the metric and the bar, the one-look rule, and the rule
    that any deviation during the test session is a stop signal.
  - **It is D21 with the airport swapped and nothing else touched.** It was
    written out separately rather than by pointing at D21 because D21 names
    London City throughout, so the test session would otherwise be translating an
    EGLC-named record with the test year open — and a translation is a decision,
    which D21.11 forbids.
  - **Both halves of Q23 are answered.** The lock **is** written out for CDG as
    its own entry (D31), and CDG's test model **is** refitted on the full D13
    training window 2021-03-24 to 2025-07-31 (D31.5), exactly as D21.5 did for
    EGLC. The consequence is recorded in advance: the tested model is the same
    recipe on CDG's 1,204 inner-training rows plus its 365 validation rows, so
    **the test number will not match session 11's 1.377 rehearsal figure and
    should not be expected to.**
  - **The lock was verified point by point.** DECISIONS carries a D21 ↔ D31
    correspondence table over all 11 sub-points — every setting, date, feature,
    reference, the metric, the bar, the one-look rule and the stop-signal rule.
    **No methodological choice differs.** Everything marked as differing is the
    location or follows from it: the airport and its position, which files hold
    its data, LFPG reporting at `:00` so D14 gives an exact match rather than
    EGLC's 10-minute offset, and the row and drop counts from CDG's own record.
  - **One difference was named rather than smoothed over.** D21.1 carries EGLC's
    approximate pull coordinates (51.505 / 0.055) while D31.1 carries IEM's own
    metadata for LFPG (49.0153 / 2.5344 / 109 m, F17). That is a difference in
    where a number came from, not in method — each airport's pulls were made at
    the position its session used and every file records the exact query — but it
    is written down so "only the location changed" is not read as also meaning
    the two positions were sourced the same way.
  - **D31 predicts the test-year drops before the look**, from session 10's gap
    map: 0 forecast-gap days (F22), 1 day lost to an off-hour-only report
    (2026-07-08, F25), 0 lost to nothing being filed and 0 to a report with no
    temperature. So 364 paired rows are expected, and 363 scored days once
    persistence loses 2026-07-09. D21 could not make this prediction for EGLC;
    CDG's gap map makes it possible, and a prediction made before the look is a
    stronger check than a count made after it.
  - **No SPEC edit was made and none was authorised.** D31 fixes no rule SPEC
    does not already carry — it names, for one airport, what SPEC already says
    per airport.
  - No script and no notes file: there was nothing to run and no number to
    produce, the same as session 09.


- **Session 13 — CDG'S SEALED-TEST EVALUATION. Done. STAGE 2 PASSED.**
  - **CDG's test year was opened for the first and only time** (2025-08-01 to
    2026-07-31). The two 2026 LFPG raw chunk files had never been read before
    this session. The locked method (DECISIONS **D31**) was executed exactly as
    written. Nothing was decided, tuned, swapped or re-run.
  - **The script checks itself against the lock before running anything, three
    ways.** All 23 values D31 fixes matched. The model settings matched session
    05's setting by setting, with zero differences. And the script was compared
    function by function with `scripts/session07_test.py`, EGLC's sealed test:
    **nine functions are character-identical**, all fourteen shared constants
    match, and the three functions that do differ have their full diffs printed
    — the two loaders (the station code in the file names, LFPG's on-the-hour
    reporting, and the near-noon bookkeeping the drop reconciliation needs) and
    `fit_on_training` (printed labels only). So "only the location changed"
    (D26) is checked in code, not argued.
  - **Refitted on CDG's full training window** 2021-03-24 to 2025-07-31, which
    is inner-training plus the validation year recombined (D31.5). **1,569 rows**
    out of 1,591 calendar days. That reconciles exactly against the published
    session 11 counts (1,204 + 365 = 1,569), which is the check that the harness
    has not drifted.
  - **Every one of D31.7's advance drop predictions landed exactly.** 0
    forecast-gap days, 1 off-hour day and it was the one D31.7 named
    (2026-07-08), 0 no-report days, 0 no-temperature days, 364 paired rows, 363
    scored once persistence lost 2026-07-09. A prediction written before the
    look is a stronger check than a count made after it, and it paid off.
    Nothing was filled (SPEC 2.2).
  - **The verdict, plainly: the bar is met.** MAE in degrees Celsius —
    ```
    Raw GFS 1.396 | Persistence 2.300 | Climatology 3.774
    Mean-bias reference 1.389 | ML-corrected 1.208
    ```
    Beats raw GFS by 0.188 degC (13.5%) and persistence by 1.092 degC (47.5%).
    Also beats the mean-bias reference by 13.0% — the constant available was
    only -0.060 degC, so there was almost no offset to take and the win is
    structure.
  - **The correction helped in three seasons of four.** Winter is the one it
    makes worse, by 0.010 degC, which is nothing — winter has been the losing
    season at both airports in every run. Summer carries the result: 1.397
    against 1.924, better by 0.528 degC. Day by day it was closer than raw GFS
    on 213 of 363 days (58.7%), against EGLC's 60.9%.
  - **The honest reading of the bigger margin.** CDG's rehearsal gave 3.5%; the
    test gave 13.5%. Most of that gap is the weather, not the model: test-year
    summer was much harder for GFS at CDG (1.924 against 1.445) and summer is
    where the correction works, while test-year winter was easier (1.188 against
    1.512), so the season the correction loses in had less to lose. About 30%
    more training data helped a little too. **And the caveat that matters most:
    that is exactly the pattern F16 described at EGLC, and both airports were
    tested on the same twelve months — so this is largely one weather year that
    suited the method, seen twice, not two independent confirmations.**
  - **Run once, not repeated.** D31.10 says the method runs once, so no second
    run was made to confirm byte-identical output, exactly as session 07 chose.
  - **No SPEC edit was made** and none was authorised. The bar was judged as
    written. SPEC 5.0's results table, and SPEC 1 and 6, still describe stage 2
    as in progress — flagged in the consistency check for the owner, not changed.
  - Full real output in `notes/session-13-check-output.txt`; the script is
    `scripts/session13_test.py`. The result of record is DECISIONS **F30**.

- **Session 14 — DSM OPENED AND VERIFIED ON CONTACT. Done. Small samples only;
  nothing was pulled in full, joined, built or trained, and nothing from EGLC or
  CDG was touched or re-run.**
  - **Owner's decisions recorded (DECISIONS D32–D33).** **D32 opens a third
    airport, Des Moines, Iowa (IEM station `DSM`, network `IA_ASOS`)** — flat
    continental US interior, GFS-reliable, IEM's home network, and a weather
    region whose summers have nothing to do with western Europe's. That is the
    direct attack on F30's caveat. **D33 sets DSM's target hour to local standard
    noon, 18:00 UTC**, not 12:00 UTC, and records openly that this gives up
    D26's "only the location changed" claim for DSM.
  - **Ten raw files pulled**, each with a `.meta.txt` beside it recording the
    pull time and the exact request (SPEC 2.3): the IEM `IA_ASOS` station
    listing, three Open-Meteo forecast samples, three IEM observation samples,
    and three small side-files used only as checks. `data/raw/` is now 96 files,
    7.8 MB. No retry fired and no rate limit was hit.
  - **The station position used, from IEM's own metadata (F31):** lat 41.534,
    lon -93.6531, elevation 294 m, timezone `America/Chicago`. Nothing was typed
    in from a map. DSM is **6,754 km from EGLC and 7,051 km from LFPG**, and
    289 m / 185 m higher — a genuinely different setting, which is the point.
  - **Forecast source verified (F31, F33).** The grid point returned is lat
    41.52945, lon -93.63281, elevation 285 m — **1.76 km from the airport**, the
    closest of the three, with a −9 m height difference, the first worth naming.
    The recent sample is 504 rows with 0 missing. The archive begins at
    **2021-03-24 00:00 UTC, the very same hour as EGLC and LFPG**, with
    1–7 March 2021 coming back all-null exactly as F1 and F20 found. **So the
    D13 split dates carry over to DSM unchanged.**
  - **The target hour checked, not assumed (F32).** `America/Chicago`'s
    standard-time offset is UTC−6, so local standard noon is **18:00 UTC**
    year-round, which is what D33 says. At 18:00 UTC the local clock reads 12:00
    CST in winter and 13:00 CDT in summer. **12:00 UTC would have been 06:00 /
    07:00 local — dawn.**
  - **Truth source verified, and the timing question answered (F34).** **DSM
    reports at `:54`, on every single report in both samples** — 504 of 504
    recently and 336 of 336 in 2021, with IEM's own `METAR_RESET_MINUTE`
    attribute saying `54` as well. That is 6 minutes from the target hour, inside
    D14's 15-minute tolerance, so **D14 applies as written**: the 17:54 report is
    the observation for 18:00 UTC. Pairing offsets across the three airports are
    10 min (EGLC), 0 min (LFPG) and 6 min (DSM). **Not one report in either
    sample falls outside the tolerance**, so on this evidence DSM loses no day to
    off-hour reporting, where LFPG loses three across five years (F25).
  - **Gap counts, nothing filled (SPEC 2.2).** Recent sample: 504 hours expected,
    503 covered, 1 missing. Early sample: 336 expected, 335 covered, 1 missing.
    **Both missing hours are the first hour of their window** — because DSM
    reports at `:54`, the report covering hour `H` is stamped `(H-1):54`, so the
    first hour needs a report from the day before the request. A boundary
    artefact, not a hole, and it does not touch the target hour. See Q26.
  - **The two US-specific worries measured, not assumed (F35).** `tmpc` is
    degrees Celsius at DSM, agreeing with the Fahrenheit field to **0.0044 degC**
    across 72 rows, so no unit conversion is needed anywhere. And the `tz=UTC`
    request really is UTC: the same three days pulled again in local time line up
    at a clean **100% at a +5 hour shift**, which is July's UTC−5 daylight-saving
    offset. `tz=UTC` and `tz=Etc/UTC` return **byte-for-byte identical** files.
  - **F36 — DSM does NOT file a second scheduled report.** Its 54 "special" rows
    in three weeks are spread across 38 different minutes, none used more than
    four times: genuinely unscheduled, unlike EGLC's `:20` (F3) and LFPG's `:30`
    (F19). So D30's fallback question cannot even arise at DSM.
  - **Plain verdict (F37): yes, DSM is usable for the recipe the same way EGLC
    and CDG were.** Every verify-on-contact check passed and nothing found here
    justifies changing any stage 1 or stage 2 decision.
  - **Three new open questions, all the owner's (Q25–Q27):** the SPEC edits D33
    now requires, including making the target hour a per-airport column in the
    3.4 table and deciding what a third airport is *called*; the chunk-boundary
    effect DSM's `:54` reporting will have on a whole-hours gap map; and
    **`gfs_global` versus `gfs_seamless` at DSM, where F6's Europe-specific
    reasoning does NOT carry** — Des Moines is inside CONUS, so `gfs_seamless`
    may prefer a higher-resolution non-GFS model there. The D16 pin protects the
    project; this is the first time D16's stated reason has had real work to do.
  - **No SPEC edit was made and none was authorised.** DSM's SPEC design is
    deliberately not written yet — it comes after verification, which is what
    this session was.
  - Full real output in `notes/session-14-check-output.txt`; the pull log is
    `notes/session-14-pull-output.txt`. The scripts are
    `scripts/session14_pull.py` and `scripts/session14_checks.py`. Two
    consecutive runs of the checks script produced identical output.

- **Session 15 — SPEC GENERALISED FOR PER-AIRPORT HOURS, THEN DSM'S FULL PULL
  AND GAP MAP. Done. Nothing was joined, built, trained or evaluated, and DSM's
  test year was not opened.**
  - **SPEC now describes an open-ended list of airports with a per-airport
    target hour (DECISIONS D34, which closes Q25 and the rest of Q24).** Seven
    authorised edits and no others — A-1 (section 1), A-2 (the 3.4 airport table:
    a new **target hour (UTC)** column, DSM's row in both tables, and the notes
    beneath them), A-3 (3.2 and 3.3), A-4 (4.1), A-5 (4.5), A-6 (5.0 and 5.3)
    and A-7 (section 6). The full before/after of every edit is in
    `notes/session-15-spec-edits.txt`.
  - **The important edit is 4.1.** The target is now **one fixed hour per
    airport, chosen to sit at that airport's local midday**, stored in the
    airport table: 12:00 UTC at EGLC and LFPG, **18:00 UTC at DSM**. The three
    "why noon" reasons are kept and now justify *local* midday rather than the
    number 12:00. D27's solar-standard-noon convention is folded in openly —
    it was planned for stage 3 and DSM brought it forward — and stage 3 now
    inherits it rather than switching to it.
  - **The honest cost is written into SPEC, not left in DECISIONS.** SPEC 4.1
    now says D26's "only the location changed" holds **within western Europe**
    (EGLC↔LFPG, same hour) but **not** for DSM, which changes location and
    target hour together. A DSM result answers "does the recipe travel to a
    different region at a comparable local time".
  - **Stage 2 is reframed** from "the second airport (CDG)" to **"individual
    airports, two or more"**, covering CDG (passed), DSM (in progress) and any
    that follow before pooling. That settles the "what is a third airport
    called?" half of Q25: stage 2 is the shape of the work, not a count.
  - **The frozen bar's meaning is unchanged, checked section by section.** 5.1
    (metric) and 5.2 (which references decide) are untouched. 5.3's only change
    is scope wording — "stage 2 is CDG" became "stage 2 is each further
    individual airport put to the same bar". Rule 2.4 untouched. Nothing was
    added that a result must clear and nothing removed.
  - **The stale wording is resolved.** Section 1, the 3.4 stage cells, the 5.0
    results table and section 6 now record EGLC and LFPG as **passed**, with
    F30's figures in the results table, and DSM as in progress.
  - **The full DSM history was pulled**, 2021-03-24 to 2026-07-31, both sources,
    six yearly chunks each, mirroring sessions 03b and 10 file for file. 32 new
    files in `data/raw/` — 16 data files with a `.meta.txt` beside every one
    (SPEC 2.3), including four small `q27compare` files. `data/raw/` is now 128
    files, 11 MB. No retry fired and no rate limit was hit.
    - Forecast: Open-Meteo Previous Runs, `gfs_global`,
      `temperature_2m_previous_day1`, at DSM's IEM coordinates. **46,944 hourly
      rows returned, 46,452 with a value.**
    - Truth: IEM ASOS routine `:54` METARs for DSM. **46,938 reports, covering
      46,932 hours.**
  - **Full gap map produced for both series — the session's main deliverable.**
    Saved in `notes/session-15-check-output.txt`; the pull log is
    `notes/session-15-pull-output.txt`. Nothing was filled, counts only
    (SPEC 2.2).
  - **The 492-hour gap answer is explicit: the SAME WINDOW (DECISIONS F38).**
    DSM's forecast series has exactly one gap, 492 hours, 2023-12-30 00:00 to
    2024-01-19 11:00 UTC — same first missing hour, same last, same length as
    EGLC's (F8) and LFPG's (F22). All six headline totals match. Entirely inside
    training; **no forecast gap at all in the test window**. Three airports on
    two continents settle it: the gap belongs to the archive, not to a place.
    At DSM's 18:00 target it costs **20 days**, 2023-12-30 to 2024-01-18.
  - **Observations: 11 real missing hours (0.02%) in 10 runs, longest 2 hours**
    (DECISIONS F39) — the cleanest of the three airports, against LFPG's 140
    (0.30%) and EGLC's 44 (0.09%). Only **3 off-hour reports in five years**
    (0.006%, against LFPG's 0.207%), none near a target hour, and exactly **one**
    report with no temperature (2023-06-30 10:50 UTC).
  - **Q26 handled, and it is smaller than feared (F39).** The `:54` artefact is
    real — all six chunks' first hours are uncovered by their own chunk — but the
    chunks are contiguous, so each one's last `:54` report serves the next one's
    first hour. **Five of the six seams close themselves; exactly one artefact
    hour remains, 2021-03-24 00:00 UTC**, the first hour of the whole period. It
    is counted and named separately from the 11 real gaps, it touches no target
    hour, and nothing was filled to cover it. The script proves this by mapping
    each chunk in isolation and then the joined series.
  - **Q27 answered, and the answer matters (DECISIONS F40). At DSM
    `gfs_seamless` is NOT `gfs_global`.** On the recent window 259 of 264 hours
    differ, by up to **12.3 degC**, from a **different grid point** (2 km away)
    and with 200x the server generation time. On the 2021 window the two are
    identical, 312 of 312 — so a comparison run only on old data would have
    concluded wrongly. Every DSM chunk was pulled with `gfs_global` (read back
    out of the saved URLs), so **nothing in the project is affected** — but had
    `gfs_seamless` been used, DSM's recent forecasts would not have been GFS at
    all. **This is the first time a decision in the log (D16) has prevented a
    real error rather than a hypothetical one.**
    - One deliberate departure from F6's method, stated in F40: F6's "recent"
      window (July 2026) now sits inside DSM's sealed test year, so it was not
      used. The recent window here is 2026-08-05 to 2026-08-15, **after the
      project period ends**, which D13 does not use at all. The early window is
      F6's own.
  - **Days lost at the 18:00 UTC target, written down before any join
    (DECISIONS F41).** Observation side: **0 days lost in 1,956**. Forecast
    side: 20, all the shared gap, all consecutive, all in inner-training.
    Expected paired rows **1,206 inner-training / 365 validation / 365 test**.
    These are the counts the join session must reconcile against.
  - **Training-window value ranges checked and sane, both in Celsius**
    (F38): forecast -30.0 to 44.7 (mean 11.95), observed -27.22 to 38.33 (mean
    12.28). About 20 degrees wider at the cold end than either European airport,
    which is what a continental interior means. One thing noted for the join
    session and **not acted on**: the forecast's warm end runs past anything
    observed (64 hours at or above 40 degC against an observed maximum of
    38.33). Whether that matters at 18:00 UTC specifically is the join session's
    question — F13 caught F10 making exactly that mistake.
  - **One inaccuracy flagged rather than fixed: Q28.** SPEC 3.4's first column
    is headed "ICAO" and `DSM` is IEM's station id, not an ICAO code; SPEC 3.1
    has the same wording problem. Neither is among edits A-1 to A-7, so neither
    was changed. A note beneath the table states the position plainly so SPEC
    does not assert something false.
  - Scripts: `scripts/session15_pull.py` and `scripts/session15_checks.py`.

## In progress

- Nothing. Session 15 is finished and awaiting the owner's review.

## Next

1. Owner reviews and commits session 15 — the SPEC generalisation and DSM's
   full pull and gap map. Sessions 08 to 14 are still awaiting review too if
   they have not been committed yet.
2. **DSM's join and validation rehearsal**, mirroring session 11 at CDG. The
   two DSM series are joined at **18:00 UTC** under the D14 pairing rule (the
   17:54 report is the observation), every drop reconciled against session 15's
   gap map, the bias looked at on inner-training only, and the locked method
   applied unchanged. **DSM's test year stays sealed and the frozen bar is not
   judged.** The counts that join must reconcile against are already written
   down (F41): 1,206 inner-training rows, 365 validation rows, 365 test rows,
   20 dropped days and all 20 of them the forecast gap. Anything else is a
   discrepancy to raise, not to explain away.
3. **Then DSM's method lock, then its sealed test** — the same two steps CDG
   took in sessions 12 and 13. The lock will be a D31-equivalent naming DSM and
   its 18:00 UTC target, written before the test year is opened.
4. **Q28 is open and it is the owner's.** SPEC 3.4's first column is headed
   "ICAO" and DSM's code is not an ICAO code; SPEC 3.1 says each airport is
   requested by its ICAO code, which is not true of DSM either. Nothing depends
   on it and nothing was changed — a note beneath the table states the position
   plainly. The repair is one heading and one sentence, and it needs the owner's
   authorisation.
5. **One thing that is available and blocks nothing.** SPEC 5.4's deeper
   evaluation — skill score, statistical significance, formal season testing —
   is optional by D29 and still undone, so no airport's win has a significance
   figure. F6's `gfs_global` versus `gfs_seamless` comparison has now been run
   at DSM (F40) but **still never at LFPG** (Q20's closing note), so stage 2's
   first airport still cannot make the by-construction claim stage 1 can.
6. Nothing is pre-committed beyond that. **Stage 3 is not opened.**

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
- **Q23 is closed** by session 12 (D31): CDG's method lock is written, and the
  D21.5 refit question is answered — CDG's test model is refitted on the full
  D13 training window, as EGLC's was.
- **Q24 is now fully closed.** Its first half — which way next, stage 3's
  pooled model or more airports first? — was answered by **D32**: more airports
  first, at Des Moines. Its second half, the stale SPEC wording, is closed by
  **D34**.
- **Q25, Q26 and Q27 are all closed by session 15.** Q25 by **D34** (the
  per-airport target hour, DSM's table row, and stage 2 reframed as "individual
  airports, two or more"). Q26 by **F39** — the `:54` artefact is real but it is
  **one** hour, not six, because the yearly chunks are contiguous and each one's
  last report serves the next one's first hour; it is counted separately and
  nothing was filled. Q27 by **F40**, with a result rather than a shrug.
- **SPEC no longer contradicts DECISIONS on DSM's target hour.** That conflict
  was flagged by session 14 and settled by D34's authorised edit to SPEC 4.1.
- **Q28 is open, and it is the owner's** (raised by session 15): SPEC 3.4's
  first column is headed "ICAO" but DSM's code is IEM's station id, not an ICAO
  code, and SPEC 3.1's "requested by its ICAO code" wording has the same
  problem. Nothing depends on it; a note beneath the table states the position
  plainly rather than letting SPEC assert something false. **Q28 is the only
  open question.**
- **EGLC's test year has been opened, exactly once, in session 07** — the one
  authorised look (D21.10). It was never loaded, printed, averaged or fitted on
  in any earlier session. It is not a held-out set any more, so it must not be
  used to judge any future change to the method. Anything measured on it from
  here on is measured on data the method has been compared against once already.
- **CDG's test year has been opened, exactly once, in session 13** — the one
  authorised look (D31.10). It was sealed through sessions 10, 11 and 12: session
  10 counted only its structure (row presence, gap locations, report timing) and
  never a temperature value, session 11 cut its load off at 2025-07-31 and
  asserted no date on or after 2025-08-01 reached any table, and session 12
  loaded no data at all. **It is not a held-out set any more**, so, exactly as
  for EGLC, it must not be used to judge any future change to the method.
  Anything measured on it from here on is measured on data the method has been
  compared against once already.
- **Both airports' test years are now spent, and they are the same twelve
  months.** That is worth carrying forward when the next airport or the pooled
  model is judged: 2025-08-01 to 2026-07-31 was a year with a hard summer and an
  easy winter for GFS at both locations, which flattered a correction that works
  best in summer (F16, F30). A future airport on those same dates is not an
  independent draw of weather.
