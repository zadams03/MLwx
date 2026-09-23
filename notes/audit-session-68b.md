# Session 68b — Correctness audit, part 2: logic and leakage review (read-only)

Scope: the last part of the audit ordered by DECISIONS D60.1, as split by
D61.1. Session 68a reproduced the record (163 of 163 figures). This session
checks that what the code does is right: no leakage, and faithful to SPEC.
It covers the headline pipeline only (D61.3): the scripts behind F16, F30,
F47, F64, F82, F94 and F109, and their data builds. The E1–E5 and combine
experiment scripts are out of scope.

This session reports and fixes nothing. Every "suggested fix" is for a
later fix session. A fix that touches a **frozen** script is marked
"frozen — owner decision". The frozen scripts are `session39_sealed_test.py`,
`session48_reserved_year.py`, `session60_combine_design.py` and
`session62_reserved_confirm.py`.

**How the work was run.**
- The code was read function by function, found through the session-67 map
  (`notes/audit-session-67.md` section 3) and grep. For the minimal method,
  `session18_test.py` (DSM) was read in full. The other four were compared
  with it function by function, with docstrings and print calls removed.
- Every data check is a throwaway script under `/tmp/audit68b/`. Project
  code ran only inside a clean clone, `/tmp/audit68b/clone`, at HEAD
  `4e13cd513ac6f4adf7288ecf68f9af6ccc77a81f`. The clone got its own `.venv`,
  built from `requirements.txt` with Python 3.12.2; `pip freeze` equals the
  19 pins. The clone's `data/raw/grib` is a symlink to the working repo's
  gitignored GRIB cache, which the checks only read.
- **One deviation from the prompt, stated plainly.** The prompt says "No
  network". Building the clone's `.venv` ran `pip install -r
  requirements.txt`, which downloaded the 19 pinned packages from PyPI.
  That is the documented setup, and 68a did the same, but this prompt does
  not carve it out. Nothing else used the network. No data was fetched, and
  no GRIB, IEM or Open-Meteo service was contacted.
- **No spent-year figure was computed.** No check computed an error, an
  MAE or a skill score on any row, ran a model on real data, or compared a
  forecast with an observation. Checks on 2024-25 and 2025-26 rows read
  date, key and feature columns only. The one check that touches
  observations (item 9) compares observation series with each other, on
  training-window dates only. `run_confirm()`, `preflight()` and every
  script's `main()` were never called. Item 6 uses a bound computed only
  from figures already on record in F109, with no data row read.
- `/tmp` is temporary, so every check script and its full output is copied
  into the Appendix.

---

## 1. Summary

**Checklist verdicts (22 items):**
- OK: 14 (items 1, 2, 3, 4, 5, 8, 9, 12, 15, 16, 17, 18, 19, 21)
- FINDING: 8 (items 6, 7, 10, 11, 13, 14, 20, 22)
- UNCERTAIN: 0

**New findings by severity:**
- must-fix: 0
- should-fix: 3 (A68b-01, A68b-02, A68b-04)
- cosmetic: 4 (A68b-03, A68b-05, A68b-06, A68b-07)
- uncertain: 0
- total: 7

**Headline results.**
- **No leakage found on any headline path.** Every forecast value used
  for target day D comes from a run issued on D−1, at least 24 hours
  before D's target hour. This was checked on every processed row in all
  three windows (0 exceptions in 11,371 or 11,365 rows per airport) and on
  every row of the 8 family pull manifests (0 exceptions).
  No feature is built from an observation. Every fit uses training rows
  only.
- **No wrong number found.** Every derivation matches its rule: pairing,
  split, units, grid interpolation (5 of 5 airports rebuilt exactly from
  the raw GRIB), elevation correction, L, D, T and R (every stored row obeys
  its own identity, in all three windows), season features, LightGBM
  settings, feature order, scoring and the bar.
- **The three findings that matter most for triage:**
  - A68b-02: the "raw GFS (GRIB)" rung in F94 and F109 is the
    **elevation-corrected** GRIB temperature. D48.10 says so, but SPEC 5.2
    defines raw GFS as "the uncorrected forecast", and SPEC sections 7 and
    8 never say the GRIB baseline is corrected.
  - A68b-01: the F109 script's reserved-year guard only stops on **zero**
    test rows, not on a partial year, although its comment says otherwise.
    F107 and this session's check show 365 of 365 rows at every airport,
    so it had no effect.
  - A68b-04: every loader parses values with `float()`, which accepts the
    text `nan` silently. A literal `nan` in a feature or observation file
    would reach the model or the MAE as a silent gap, against SPEC 2.2. No
    such value exists anywhere today (0 in every model input and every
    IEM chunk).
- **Carried items.** A67-04 is confirmed: the printed text is stale, but no
  reserved-year row is used on the preflight path. A67-12 is confirmed:
  the pairing is otherwise faithful, and all three headline paths build
  identical observation series. A67-14 **cannot happen on the F109 path**:
  0 of 9,777 complete-case rows lack a final-set key. The wider fragility
  behind it is A68b-04.

---

## 2. The checklist

Code references are `file:line` in `scripts/`. "Minimal" means the five
minimal-method test scripts (`session07/13/18/24/29_test.py`), cited by the
DSM copy `session18_test.py` unless a difference matters. Item 20 lists
every non-print difference between the five.

### A. Time and leakage

#### Item 1 — Forecast issue time

**The rule.** SPEC 2.1b, Open-Meteo: every value is "a genuine forecast made
at least 24 hours before its valid time", from the `previous_day1` offset
(SPEC 3.2, F5). SPEC 7.2 and D48.2, GRIB: "for a target hour `HH:00 UTC`,
use the run made at cycle `floor(HH/6)*6` UTC on the day before, forecast
hour `24 + (HH mod 6)`".

**The code.**
- Minimal: `session18_test.py:338–363` `load_forecast_target_hour()` reads
  `temperature_2m_previous_day1` at the target hour only. The pull asked for
  `previous_day1` in UTC (`session03_pull.py:106–120`, and the same in the
  other four pull scripts, by their sidecar URLs).
- B, training and sealed: `session37_decode.py:65–68` `cycle_and_lead()`;
  `:131–167` `decode_row()` takes `run_date = target_date − 1 day` and
  **refuses** any message whose GRIB validity date and hour are not the
  target (`:151`). `session40_decode.py:137` is the same.
- L, D: `session49_upper_air_pull.py:208–273`, `session51_moisture_pull.py:215–283`
  `process_combo()`. The lead comes from an exact "N hour fcst" match in the
  `.idx` file. The validity **date** is checked (`:261`, `:269`). The hour
  is not (see A68b-05).
- T: `session53_pressure_pull.py:179–187` `expected_valid_dt()`; the full
  validity datetime is checked for both the lead and the lead−3 message
  (`:388`, `:431`).
- R: `session55_radiation_pull.py:445–466`; the full validity datetime is
  checked (`:463`).
- Reserved year: `session63_reserved_year_build.py:139–255` calls the four
  families' own `build_combos()` and `process_combo()`, imported, not copied.

**The verdict.** OK.

**The evidence.**
- Data check 1 (Appendix 6.1), all processed rows, all windows: for every
  row of every B and family file (v16, sealed, reserved; 16 files),
  `run_date = target_date − 1`, `cycle` and `lead` equal the rule for that
  station's SPEC 3.4 hour, and the run's issue time plus the lead equals
  the valid time. **0 exceptions.** Stored per airport: EGLC and LFPG (12, 12,
  24), DSM (18, 18, 24), YSDU (2, 0, 26), RNO (20, 18, 26). This matches
  D48.2 exactly.
- The family files' `cycle`/`lead` columns are copied from B's file, so
  they do not prove the family's own fetch. The pull manifests do. For every
  row of the 8 family manifests (sessions 49, 51, 53, 55 and the four
  session-63 manifests), the fetched run, cycle and lead give a valid time
  equal to the target hour (standard lead), 3 hours before it (T's lead−3)
  or 2 hours before it (R's lead−2). No fetch is valid after the target.
  Where the manifest records the decoded validity time (L, D, T; 70,389
  rows), it equals the expected time. **0 problems in 82,121 manifest rows.**
- Open-Meteo, data check 2 (Appendix 6.2): all 30 chunks are `timezone=GMT`,
  `utc_offset_seconds=0`, with a continuous hourly axis. The "at least 24
  hours" property rests on the API's own definition of `previous_day1`
  (SPEC 3.2, F5). The stored JSON carries no issue time, so it cannot be
  checked from the data.

#### Item 2 — No feature sees the future or an observation

**The rule.** SPEC 2.1 ("never, directly or indirectly, see information from
the future"). SPEC 4.2: features are forecast inputs; the target is
observed minus forecast.

**The code.**
- Minimal features: `session18_test.py:436–448` `features()`, which uses
  `r["fc"]` and the date.
- F94: `session39_sealed_test.py:190–203` `features_3/5()`, which use `fc`,
  `cloud`, `wind` and the date.
- F109: `session62_reserved_confirm.py:223–236` `make_feature_vector()`, and
  `:347–364` `build_complete_case()`, which fills the row from B and the
  four family files only.
- Each family value is built from forecast fields of the same run: L =
  `t2m_raw − t850` (`session49_upper_air_pull.py:295, 301`); D = `t2m_raw −
  dew_point_2m` (`session51_moisture_pull.py:306, 312`); T = `PRMSL(lead) −
  PRMSL(lead−3)` from the same run (`session53_pressure_pull.py:473–480`);
  R = the DSWRF averages at lead and lead−2 from the same run
  (`session55_radiation_pull.py:545–553`). `t2m_raw` is B's forecast
  temperature minus the fixed elevation constant.

**The verdict.** OK.

**The evidence.**
- No feature function reads `obs`, `resid` or any observation field.
  Observations enter only the target (`resid`) and the scoring. Data check 9
  (Appendix 6.9) builds a feature row with marker values for `obs` and
  `resid`. The markers do not appear in the F109 feature matrix.
- The one fitted constant inside a feature is the elevation correction
  (D48.3). It was fit on `session36_grib_vs_openmeteo_comparison.csv`: 95
  rows of **GRIB forecast against Open-Meteo forecast**, target dates
  2021-03-24..2025-06-14. No observation is in that file, so no truth
  entered it. (Some of those dates fall in the later-reserved 2024-25 year.
  D48 predates D51, and a forecast-against-forecast gap is not target
  information.)

#### Item 3 — Persistence

**The rule.** SPEC 5.2: "tomorrow will be the same as today". SPEC 2.1d:
"only observations from before the time being predicted". D48.9: the first
test day's "yesterday" may be the last training day; that is legal.

**The code.**
- Minimal: `session18_test.py:1062–1071`: `prev =
  obs_all.get(r["date"] − 1 day)`. Days with no D−1 value are removed from
  **every** method (the "common" set).
- F94: `session39_sealed_test.py:381–389`: same lookup. Days with no D−1
  value are removed from persistence **only**.
- F109: `session62_reserved_confirm.py:394–404` `raw_persist()`: same as F94.

**The verdict.** OK.

**The evidence.**
- In every path the value is the paired observation at the airport's own
  target hour on calendar day D−1. That is 24 hours before the target, so
  it is strictly in the past. It is never D itself: the key is always
  `date − 1 day`.
- The observation dictionaries are built by the same D14 rule used for the
  target (item 9). Data check 5 (Appendix 6.5) shows the three paths' series
  are identical on training dates.
- The missing-D−1 handling matches the record: F94 Task 2 documents
  persistence on the `common_persist` subset (EGLC 1, LFPG 1, YSDU 9 days).
  F109 documents `n_persist = n_final − no_prev` (EGLC 1, YSDU 5). Whether
  the pass/fail comparison is affected is item 6.

#### Item 4 — Train/test split

**The rule.** SPEC 4.3: train 2021-03-24..2025-07-31, test
2025-08-01..2026-07-31, both inclusive (minimal and F94). D58 item 4: train
2021-03-24..2024-07-31, test 2024-08-01..2025-07-31 (F109). SPEC 2.1a: split
by time only.

**The code.**
- Minimal: `session18_test.py:101–110` constants; `:810–847` builds each
  period from `all_days(lo, hi)` (inclusive both ends, `:418–424`).
- F94: `session39_sealed_test.py:64–67` constants; `:326–335` joins each
  window with `all_days` and **asserts** every training row is before
  2025-08-01 and every test row is inside the sealed year.
- F109: `session62_reserved_confirm.py:171–175` `CONFIRMATION_FOLD`;
  `:702–705` filters `tr_s <= d <= tr_e` and `ts <= d <= te`.

**The verdict.** OK.

**The evidence.**
- All boundaries equal SPEC 4.3 or D58 item 4 exactly, inclusive at both
  ends. Training ends the day before testing starts on every path, so the
  windows do not overlap.
- Every path filters on `target_date` (minimal: the key of the forecast and
  observation dicts, which is the UTC date of the valid hour). The UTC date
  is also the local date at every airport's target hour: the ±15-minute
  pairing window never crosses midnight, because no target hour is 00 or
  23 UTC.
- A test row can enter training only through its date, and the date
  filters above exclude that. Data check 1 shows the stored `target_date`
  ranges are exactly the intended windows.

#### Item 5 — Fitting touches training rows only

**The rule.** SPEC 2.1c (climatology from training only); SPEC 2.1 in
general.

**The code.**
- Minimal: `session18_test.py:1001–1053` fits the model, the mean bias and
  the climatology on `train` only. `climatology_from_training()`
  (`:978–998`) closes over training fractions and observations only.
- F94: `session39_sealed_test.py:363–370`: both models fit on `train_rows`.
- F109: `session62_reserved_confirm.py:382–391` fits on `train_rows`.

**The verdict.** OK.

**The evidence.**
- There is no scaler, normaliser, imputer or encoder anywhere on these
  paths. LightGBM needs none.
- The only other "fitted" numbers are the frozen elevation constants
  (item 13, fit before any of these tests and not on observations) and D's
  floor (`max(x, 0)`, a fixed rule, not a statistic).
- No feature is derived from the target.

#### Item 6 — Same rows for every compared score

**The rule.** SPEC 5.3: beat raw GFS and persistence "over the held-out test
period". D21.8 (minimal) and D48.10 (F94): all rungs on "the same common set
of days". D58 item 6 (F109): persistence on the subset with a D−1
observation; raw, B and B+D,L,R,T on the full test set; "any mismatch
reported, not hidden".

**The code.**
- Minimal: `session18_test.py:1062–1116`: one `common` list, used for every
  method.
- F94: `session39_sealed_test.py:377–405`: raw, 3-feature and 5-feature use
  `test_rows`; persistence uses `common_persist`; the bar compares
  `f5_mae < persist_mae` across the two sets.
- F109: `session62_reserved_confirm.py:707–712`: the same pattern.

**The verdict.** FINDING (A68b-03, cosmetic).

**The evidence.**
- The minimal method follows D21.8 exactly.
- F94 departs from D48.10's own wording. F94 Task 2 found and reported this,
  and showed the verdict is identical on the common basis at every airport.
- F109 follows D58 item 6, which pre-registered the mixed basis, and F109
  reports it. F109 has no common-basis re-check like F94's Task 2. But one is
  not needed: because every error is ≥ 0, dropping k of n days can raise a
  mean by at most n/(n−k). From recorded figures only (Appendix 6.10): EGLC
  ≤ 1.0036 against persistence 2.2259, and YSDU ≤ 1.2821 against 2.5775. The
  other three have no_prev = 0. So **no F109 verdict against persistence
  can change under a common day set.**
- The raw-GFS half of the bar uses identical rows on every path.
- The finding is documentation only. SPEC 7 and 8 and RESULTS never say
  that the GRIB methods score persistence on a smaller day set than the
  minimal method does (grep: no hit). F94 Task 2 flagged this "for whoever
  eventually folds this recipe into SPEC/RESULTS". Also,
  `session39_sealed_test.py:9` (frozen) says it scores the four rungs "on
  the same common days", which its own code does not do.

#### Item 7 — Guards

**The rule.** D51 and D58 item 11 (reserved-year guard and gap guard); D48.7,
D48.8 and F93 (F94 self-guards); D21.11 and later locks (minimal stop
signals).

**The code.**
- `session48_reserved_year.py:52–72` `assert_reserved_year_excluded()` is
  called before writing, on both spans, by every family build:
  `session49_upper_air_pull.py:340, 342`; `session51_moisture_pull.py:460,
  462`; `session53_pressure_pull.py:607, 609`; `session55_radiation_pull.py:678,
  680`. Each also scans every date. `session62_reserved_confirm.py:462–503`
  (preflight) proves it passes the dry-run fold and raises on the
  confirmation fold. It is deliberately **not** called in `run_confirm()`
  (D51/D58 exception, `:164–170`).
- F109's own guards: `load_family()` counts reserved rows in the v16/sealed
  files and `run_confirm()` stops on any (`:668–671`); the reserved-file
  loader raises on any out-of-range date (`:287–291`); the "gap" guard is at
  `:683–695`.
- `session63_reserved_year_build.py:125–136`
  `assert_all_inside_reserved_year()`.
- F94: `session39_sealed_test.py:223–241` (missing file, out-of-window date),
  `:331–335` (row dates), `:342–346` (training count, D48.7), `:356–360`
  (sealed ceiling, D48.8/F93), `:438–441` (no arguments).
- Minimal: `session18_test.py:780–781` (`max(date) <= HARD_END`),
  `:874–877` and `:961–966` (count reconciliation), `:1599–1607` (stop
  before any fit).

**The verdict.** FINDING (A68b-01, should-fix).

**The evidence.**
- Data check 6 (Appendix 6.6), synthetic dates and synthetic files only:
  **19 of 20 cases behave as intended.** The session-48 guard is inclusive at
  both edges: it raises on a train end of 2024-08-01 and a test start of
  2025-07-31, and passes a train end of 2024-07-31. It raises on the
  confirmation fold and passes all three `EXPERIMENT_FOLDS`. The F94 loader
  raises one day either side of the sealed year, on a missing file and on a
  blank value. The F109 reserved-file loader raises on 2025-08-01.
  `assert_all_inside_reserved_year()` raises on 2024-07-31.
- The 20th case is a literal `nan` string, which the F94 loader accepts
  silently. That is A68b-04, under item 10.
- A68b-01: `run_confirm()`'s gap guard raises only when an airport has
  **zero** complete-case test rows (`if n_test == 0`, `:685`). The comment
  above it says it refuses "if the test window's complete-case row count is
  not what a genuine full year of data would give". So a partial year, for
  example 200 of 365 rows, would pass silently. It had no effect: F107 and
  data check 9 show 365 complete-case rows at every airport, and
  0 B-days in the fold are missing from the complete-case set.
- The guard is not called on the F94 path (the sealed year is a separate,
  earlier boundary with its own D48 self-guards), and that is correct.

### B. Targets and pairing

#### Item 8 — Target hour

**The rule.** SPEC 4.1 and 3.4: a fixed UTC hour per airport (EGLC 12, LFPG
12, DSM 18, YSDU 2, RNO 20). Daylight saving is deliberately ignored.

**The code.**
- `TARGET_HOUR` in each minimal script (item 20 lists them).
- `AIRPORTS` in `session39_sealed_test.py:69–75`,
  `session62_reserved_confirm.py:107–113`, and in every GRIB build script.
- Forecast side: Open-Meteo requested with `timezone=UTC`; GRIB validity
  checked against the hour.
- Observation side: IEM requested with `tz=UTC` (every sidecar URL).
- Persistence reuses the same observation series.

**The verdict.** OK.

**The evidence.**
- Every copy holds the SPEC 3.4 hours.
- Data check 1: the stored `target_hour` equals SPEC 3.4 on every processed
  row.
- Data check 2: the Open-Meteo JSON is UTC with no offset.
- All hours are UTC throughout, with no local-time conversion anywhere, so
  daylight saving cannot enter.
- Forecasts, observations and persistence all use the same hour per
  airport. Persistence reads the same dictionary as the target.

#### Item 9 — Pairing (SPEC 4.5, D14)

**The rule.** SPEC 4.5: "paired with the station's **nearest** routine report
to that hour. If no report falls within 15 minutes of the hour, that hour is
dropped and counted."

**The code.**
- `session18_test.py:366–415` (minimal).
- `session39_sealed_test.py:250–277`.
- `session62_reserved_confirm.py:321–344`.
- Each rounds a report's time to the nearest hour (`t + 30 min`, then
  truncate). It keeps the report if that hour is the target and it is within
  15 minutes. It drops and counts `M`, blank, `T` and `None`.

**The verdict.** OK (A67-12 carried, no new finding).

**The evidence.**
- The rule is otherwise faithful. The rounding makes a report belong to its
  nearest hour. The `abs(...) > 15*60` test drops anything further than 15
  minutes (exactly 15 is kept, which fits "within 15 minutes"). A report at
  :30 rounds up and is then 30 minutes out, so it is dropped.
- Only routine reports are read (`report_type=3` in every sidecar URL).
- The one gap between words and code is A67-12 (last-wins, not nearest).
  Session 67 counted 1 tie day, with equal temperatures.
- Data check 5: the committed loaders of all three headline paths, run
  unchanged, return **identical** observation series on every training date
  at every airport (EGLC 1,225, LFPG 1,224, DSM 1,226, YSDU 1,214, RNO
  1,223 days).

#### Item 10 — Units and missing values

**The rule.** SPEC 2.2: missing values are dropped and counted, never
filled. SPEC 3.3 and F35: IEM `tmpc` is °C.

**The code.**
- Observations: `float(raw)` after excluding `M`, blank, `T` and `None`
  (item 9).
- Open-Meteo nulls: `session18_test.py:833–835` counts a `None` forecast as
  "null fc" and drops the day.
- GRIB: K → °C at `session37_decode.py:154`; wind m/s → km/h (`×3.6`) at
  `:155`; `t850` K → °C at `session49_upper_air_pull.py:384`; dew point
  K → °C at `session51_moisture_pull.py:509–510`; Pa → hPa at
  `session53_pressure_pull.py:473–475`; DSWRF is already W/m².
- The same conversions happen in `session63_reserved_year_build.py:160, 188`
  and `:339–341`.
- Loaders: `float(r[c])` in `session39_sealed_test.py:243–245` and
  `session62_reserved_confirm.py:270, 294, 314–316`.

**The verdict.** FINDING (A68b-04, should-fix).

**The evidence.**
- Units are right on every path. Data check 2: every Open-Meteo chunk says
  `°C`. Data check 4 (Appendix 6.4): `t850`, dew point, MSL pressure and
  DSWRF sit in physically sensible ranges, with near-identical per-airport
  means in the training, sealed and reserved files. For example, RNO `t850`
  has a mean of 15.9, 17.0 and 15.9 °C; MSL pressure has a mean of about
  1015 hPa everywhere. So the reserved-year build converted units exactly
  as the original builds did.
- Missing values are dropped and counted. Data check 2: Open-Meteo nulls at
  the target hour occur only in the shared gap (20 days per airport; 21 at
  YSDU, whose 02:00 hour also falls in the gap on 2024-01-19). Data check 7
  (Appendix 6.7): the only non-numeric `tmpc` token in any IEM chunk is `M`
  (EGLC 10, LFPG 1, DSM 1, YSDU 2, RNO 1), which the code drops.
- A68b-04: Python's `float()` accepts the text `nan` (and `inf`) and returns
  a non-finite number. Data check 6 shows the F94 loader returns
  `{'fc': nan, ...}` for such a row without raising. Downstream, LightGBM
  treats a NaN feature as "missing" silently, and a NaN error makes an MAE
  NaN. A67-14 is one case of this, not the whole of it.
- Today there are **0** such values: data check 7 scanned every model-input
  column of every B and family file, in all windows, and every IEM chunk.

### C. Feature builds

#### Item 11 — Grid and interpolation

**The rule.** SPEC 7.2: "bilinear-interpolated from the surrounding grid
points to the airport's already-established grid point (3.4)".

**The code.**
- `session37_decode.py:80–118` `bilinear_value()`. The same function is in
  `session40_decode.py`. The same arithmetic is in the families'
  `bilinear_from_gid()` (`session49_upper_air_pull.py:148–171` and copies)
  and in `session37_elevation_fix.py:127–162`.
- It converts a negative query longitude to 0–360 (`lon_q`). It sorts the
  two latitudes and two longitudes of the four eccodes neighbours, weights
  them by the fractional distances, and falls back to the nearest point
  only if the neighbours are degenerate.

**The verdict.** FINDING (A68b-07, cosmetic). The GRIB interpolation itself
is correct.

**The evidence.**
- Data check 3 (Appendix 6.3), from the raw GRIB for training date
  2022-11-26:
  - The file grid runs 0.0..359.75 in longitude. DSM (266.367) and RNO
    (240.234) are converted into it correctly.
  - EGLC sits exactly on longitude 0.0. eccodes returns 0.0 and 0.25, so
    `dlon = 0` and the value is a pure north–south interpolation along 0.0,
    which is correct.
  - At all five airports the query point lies inside the four-point cell.
    The weights sum to 1. The largest weight goes to the nearest grid point
    (for example EGLC 0.9485 on (51.5, 0.0)).
  - The committed `bilinear_value()` plus the elevation constant rebuilds
    the stored `temperature_grib_c` exactly at all 5 airports.
- The query points equal SPEC 3.4's grid points in every GRIB script.
  Data check 2 shows the Open-Meteo JSON returned exactly SPEC 3.4's grid
  point in all 30 chunks.
- A68b-07: the EGLC Open-Meteo pull asked for latitude 51.505, longitude
  0.055 (`session03_pull.py:43–44`). SPEC 3.4's airport position is
  51.5053, 0.0553. Open-Meteo returned the SPEC 3.4 grid point anyway, so
  there is no effect.

#### Item 12 — Cycle and lead selection

**The rule.** SPEC 7.2 and D48.2: cycle `floor(HH/6)*6`, lead `24 + (HH mod 6)`.
Lead 24 at EGLC, LFPG and DSM; lead 26 at YSDU and RNO.

**The code.** `cycle_and_lead()`, identical in all 9 GRIB scripts (data
check 8). The families add T's lead−3 (`session53_pressure_pull.py:356`) and
R's lead−2 at the lead-24 airports (`session55_radiation_pull.py:535–549`).

**The verdict.** OK.

**The evidence.**
- Data check 8 (Appendix 6.8): all 9 copies are identical. The B builds
  (37, 40) and all four family builds use the same function body.
  `session63` imports the families' own `build_combos()`.
- Data check 1: stored per airport, EGLC and LFPG (cycle 12, lead 24), DSM
  (18, 24), YSDU (0, 26), RNO (18, 26). The manifests show the same per
  family.

#### Item 13 — Elevation correction (D48.3, F90)

**The rule.** D48.3: "`corrected = raw_grib_temp_c + (orog_interp_m −
grid_elev_m) / 1000 * 7.429`", "applied to temperature only". F98: L uses
"the RAW, uncorrected 2 m forecast temperature".

**The code.**
- `session37_elevation_fix.py:187–255` derives `gap = orog − grid_elev` and
  `correction_c = 7.429/1000 × gap` (`:246–252`).
- `session37_decode.py:71–77, 154` adds `correction_c` to the temperature
  only.
- L and D recover `t2m_raw = round(temperature_grib_c − correction_c, 3)`
  (`session49_upper_air_pull.py:295`, `session51_moisture_pull.py:306`).
- The raw-GFS rung in F94 and F109 is `r["fc"]`, the **corrected** value
  (`session39_sealed_test.py:377`, `session62_reserved_confirm.py:395`).

**The verdict.** FINDING (A68b-02, should-fix).

**The evidence.**
- The formula, sign and constant are right. Where the model's terrain sits
  above the reference elevation (RNO, +275.08 m), the model is too cold, and
  the correction warms it (+2.0436 °C). The committed params CSV holds 7.429
  at every airport, with gaps +33.47, −22.85, −14.89, +33.12 and +275.08 m,
  equal to D48.3's table.
- The terrain height is GFS HGT:surface from one 2025-06-10 run. 68a
  re-interpolated all 5 values exactly from the tracked files.
- The correction is applied to temperature only. Cloud and wind are
  untouched (`:155`).
- L's `t2` is the **uncorrected** value, as F98 says. Data check 4: `t2m_raw
  == round(temperature_grib_c − correction_c, 3)` on every L and D row in all
  three windows (max diff 0.000000).
- A68b-02: SPEC 5.2 defines the raw-GFS baseline as "the uncorrected
  forecast". SPEC 7.2 says the bar is unchanged. The F94 and F109 raw rung is
  the elevation-corrected GRIB temperature. D48.10 says so plainly ("raw GFS
  (GRIB, elevation-corrected)"), and it was fixed before the look. But SPEC 7
  and 8, and RESULTS, label the column only "raw GFS (GRIB)". The only
  "elevation-corrected" mentions in SPEC (`:698`) and RESULTS (`:358`,
  `:376`) describe the model inputs, not the baseline.

#### Item 14 — Each added feature's derivation

**The rule.** D58 item 3 and SPEC 8.1; F98 (L), F100 (D), F101 (T), F102 (R).

**The code and the evidence, per feature.**
- **L = t2 − t850.** `session49_upper_air_pull.py:301`: `t2m_raw − t850`,
  both °C, so a positive value means a warmer surface. Correct sign and
  units. Data check 4: the identity holds on every row, all windows (max
  diff 0.000000).
- **D, dew-point depression.** `session51_moisture_pull.py:312`: `t2m_raw −
  dew_point_2m`, both °C. The floor `max(x, 0)` is applied only in F109's
  `build_complete_case()` (`session62_reserved_confirm.py:360`), as D58
  item 3 says. Data check 4: the identity holds on every row. There is
  exactly 1 negative raw value (training window), which is D58's "1 of
  7,952 rows". There are 0 negatives in the sealed or reserved files.
- **T, 3-hour pressure tendency.** `session53_pressure_pull.py:473–480`:
  `PRMSL(lead)/100 − PRMSL(lead−3)/100`, both from the same run, both mean
  sea level, in hPa. A positive value means rising pressure. The lead−3
  validity time is checked against the absolute time 3 hours before the
  target (`:179–187`, `:431`). Data check 4: the identity holds on every row.
- **R, 2-hour DSWRF.** `session55_radiation_pull.py:137–142`
  `window_start()`, `:535–553`. For lead 24: `(ave(18–24h)×6 −
  ave(18–22h)×4) / 2`. That is the energy over 22–24h, divided by its 2
  hours, which is correct and includes the division by hours. For lead 26:
  the native 24–26h average, used as is.
  - Data check 1: every one of the 9,542 + 2,190 R manifest rows records
    `startStep`/`endStep` of exactly 18–24 at lead 24, 18–22 at lead 22 and
    24–26 at lead 26.
  - Data check 4: the identity holds to 0.002 W/m² (the known rounding of
    the stored inputs, F103/F108). No stored value is negative.

**The verdict.** FINDING (A68b-05, cosmetic). All four derivations are
correct.

**The evidence for the finding.** A68b-05: the L and D fetches check the GRIB
validity **date** only (`session49_upper_air_pull.py:260–262`,
`session51_moisture_pull.py:268–270`). They compute `valid_hour` but never
compare it. B, T and R check the full datetime. It had no effect: the lead is
fixed by the exact `.idx` step match, and data check 1 found the recorded
validity hour equal to the expected hour on all 38,166 + 8,760 L and D
manifest rows.

#### Item 15 — Season features

**The rule.** D48.4: `season_sin/cos = sin/cos(2π · year_fraction(date))`,
`year_fraction = (day_of_year − 1) / 365`, or `/366` in a leap year.

**The code.** `year_fraction()` in all seven scoring scripts and in
`session05_model.py` (for example `session39_sealed_test.py:184–187`), used
at `:193–194, 201–202` and in `session62_reserved_confirm.py:224–228`.

**The verdict.** OK.

**The evidence.**
- Data check 8: all 8 copies are identical. The leap-year rule is the full
  Gregorian one (÷4, not ÷100 unless ÷400). 1 January gives phase 0 and
  cos = 1.
- 68a showed the F94 and F109 paths give identical sin/cos on 9 dates.
- The climatology window in the minimal method (`half = 7.5/365.25`,
  `session18_test.py:989`) mixes a 365.25-day year with `year_fraction`'s
  365/366. The difference is under 0.01 day. It is an informative reference
  only, not part of the bar, so this is noted, not a finding.

#### Item 16 — The reserved-year build

**The rule.** F107: the reserved year was built "reusing the exact,
already-frozen pull/decode/derive code … only extending the date range".
F108 records a proof.

**The code.** `session63_reserved_year_build.py`:
- imports `build_combos`, `process_combo`, `AIRPORTS`, `LEVELS` and
  `window_start` from the four family modules (`:67–70`, `:139–255`);
- copies each family's result-handling loop (`pull_L/D/T/R`) and each
  family's `build_joined` arithmetic (`join_L/D/T/R`, `:258–400`).

**The verdict.** OK.

**The evidence.**
- **What F108's proof covers, and whether its method supports it.** F108 fed
  every row of each family's committed v16 file (the stored, already
  converted intermediate columns) through session 63's own `join_*`
  functions, and compared the result row by row. That method does support
  its claim that the **join and derive arithmetic** is identical: L, D and T
  are exact; R has a 0.002 W/m² residual that F108 correctly traces to the
  rounding of the stored inputs.
- It does **not** cover two things:
  - the `pull_*` loops, where the K → °C conversions for L and D live;
  - `process_combo()` itself.

  `process_combo()` is imported, not copied, so it needs no proof.
- This session closed the loop gap. Data check 8 shows each `pull_*` loop
  is identical to its family's own `main()` loop, apart from the progress
  print. Data check 4 shows the reserved files carry the same units and
  ranges as the training and sealed files, and obey every identity.
- Data check 1 shows the four session-63 manifests (15,330 rows, 0 FAIL)
  follow the same cycle, lead and validity rules.

### D. Model and scoring

#### Item 17 — LightGBM settings

**The rule.** D21.4 and D48.6: `objective=regression_l1, n_estimators=300,
learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0,
colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42,
n_jobs=1, deterministic=True, force_row_wise=True, verbose=-1`.

**The code.** `LGB_PARAMS` in `session07_test.py:116`, `session13_test.py:127`,
`session18_test.py:138`, `session24_test.py:155`, `session29_test.py:164`,
`session39_sealed_test.py:130`, `session62_reserved_confirm.py:131`.

**The verdict.** OK.

**The evidence.**
- Data check 8: all seven dicts equal D21.4/D48.6 exactly, 14 keys each.
- Every `LGBMRegressor` call on these paths is `lgb.LGBMRegressor(**LGB_PARAMS)`,
  and every `.fit` is on training arrays only.
- Seed 42, `deterministic=True`, one thread (`n_jobs=1`), `force_row_wise=True`,
  and no row or column sampling.
- `lightgbm==4.7.0` and `numpy==2.5.2` are pinned. 68a reproduced every
  figure exactly.

#### Item 18 — Feature order and columns

**The rule.** D21.3 and D48.4 (minimal, 3- and 5-feature); D58 items 1 and 3
(B+D,L,R,T).

**The code.**
- Minimal: `session18_test.py:436–451`, `[fc, sin, cos]`, used at fit
  (`:1014`) and predict (`:1105`).
- F94: `session39_sealed_test.py:190–203`, used at `:363–375`.
- F109: `session62_reserved_confirm.py:382–391`. `fit_and_score()` builds
  one `keys` list and uses it for both `x_tr` and `x_te`. `run_confirm()`
  passes `BASE_KEYS` and `FINAL_FEATURE_KEYS` (`:708–709`).

**The verdict.** OK.

**The evidence.** Data check 9 (Appendix 6.9):
- `FINAL_FEATURE_KEYS` = temp, season_sin, season_cos, cloud_cover,
  wind_speed_10m, dewpoint_depression_t2m_floored, lapse_rate_t2_t850,
  dswrf_2h_wm2, pressure_tendency_3h_hpa. That is exactly B plus D, L, R and
  T, and equals the order `fit_and_score` would build from sorted codes.
- A marked synthetic row maps to the 9 columns in exactly that order. Its
  `obs`, `resid`, `date` and `station` markers do not appear.
- Fit and predict use the same list on every path. No stray column can
  enter: every matrix is built from a named key list, never from a whole
  row.

#### Item 19 — Scoring

**The rule.** SPEC 5.1 (MAE); SPEC 5.3 and D58 item 7 (lower MAE than both
raw GFS and persistence, per airport); SPEC 8.5 ("airport-averaged MAE
1.2377 against plain B's 1.3170, a +6.02% skill margin").

**The code.**
- `mae()`: `np.mean(np.abs(errors))` (`session18_test.py:456–457`,
  `session39_sealed_test.py:206–207`, `session62_reserved_confirm.py:243–244`,
  which returns NaN for an empty list).
- Skill: `(ref − ml)/ref` (minimal, `session18_test.py:1167`) or
  `1 − model/ref` (`session39_sealed_test.py:410`). These are the same thing.
- Bar: `ml < raw and ml < persist` (`session18_test.py:1163, 1169`;
  `session39_sealed_test.py:403–405`; `session62_reserved_confirm.py:711–712,
  727`).
- Airport average: `session62_reserved_confirm.py:728–729`.

**The verdict.** OK.

**The evidence.**
- The MAE is a plain mean of absolute errors. The bar is strict "lower
  than" on both halves, so a tie fails, which fits "lower MAE".
- The airport average is the **mean of the five per-airport MAEs**, not a
  MAE pooled over all days. The record calls it "airport-averaged MAE",
  which describes a mean of MAEs, so they agree.
- Appendix 6.10: the mean of F109's five recorded B+D,L,R,T MAEs is
  1.23770, and of B's is 1.31700, equal to the record (arithmetic on
  recorded figures only).
- A NaN persistence MAE would make `f < nan` False, so the result would be
  a FAIL, never a silent pass.

### E. Consistency across copies

#### Item 20 — The five minimal-method scripts

**The rule.** Session 67 claimed they are "identical apart from print text".

**The code.** Data check "diff_minimal" (Appendix 6.11) compares every
method function, with docstrings and print/sub/line calls removed, against
`session18_test.py`.

**The verdict.** FINDING (A68b-06, cosmetic).

**The evidence.** Identical in all five: `all_days`, `year_fraction`,
`features`, `mae`, `climatology_from_training`, `fit_on_training`, and the
constants `TRAIN_*`, `TEST_*`, `HARD_END`, `CHUNKS`, `LGB_PARAMS`,
`CLIM_HALF_WINDOW_DAYS` and `FEATURE_NAMES`. **Every non-print difference:**
1. `STATION`/`TARGET_HOUR`: EGLC has no `STATION` constant and hard-codes
   "EGLC" in both file paths. The hours are 12, 12, 18, 2, 20.
2. The observation loader: EGLC does not build the `near_target` bookkeeping
   list. LFPG builds its own `near_noon` list from reports in hours 11 and 12.
   The pairing lines themselves are identical in all five.
3. `join()`: EGLC checks its training counts with an `assert` (1,569, 1,205,
   364) and has **no** test-year count check. LFPG adds a check that the named
   off-hour drop days match. The bookkeeping labels and constants differ. The
   pairing, split and row-building code is identical.
4. `score_test_year()`: identical except that `session29_test.py:1175` computes
   `ok_scored`.
5. `judge_the_bar()`: the banner text differs. LFPG's informative mean-bias
   note tests `mb > raw` where the others test `mb < raw`, and only a printed
   sentence depends on it.
6. `main()`: EGLC has no "stop if not reconciled" branch (its `assert` stops
   instead). Each script calls its own comparison and watch-item parts,
   which come after the verdict.

A68b-06: the stop checks are uneven.
- The scored-day expectation (`EXPECT_TEST_SCORED_DAYS`) is printed next to
  the result but **never enforced** in any of the five.
- `session29_test.py:1175–1177` prints "SURPRISE (D44.11 stop signal)" but
  does not stop.
- EGLC's script has no test-year count check at all.

68a reproduced every count, so no effect.

#### Item 21 — Copied functions on the headline path

**The rule.** The copies must be identical, or each difference explained.

**The code and the evidence.** Data check 8 (Appendix 6.8):
- **Identical copies:** `cycle_and_lead` ×9, `grib_base_url` ×6,
  `find_message_range` ×5, `build_combos` (B pulls ×2; families L, D, T ×3),
  `bilinear_from_gid` ×4, `decode_row` ×2, `grib_files_for` ×2,
  `year_fraction` ×8, `all_days` ×2, `mae` ×2 (+1 variant), and the
  session-63 `pull_*` loops against the family `main()` loops (only the
  progress print differs).
- **Differences, each harmless:**
  - `process_combo`, 37 against 40: one extra line in the metadata sidecar
    text.
  - `bilinear_value` in `session37_elevation_fix.py`: returns only the value.
    The arithmetic is identical.
  - The family `bilinear_from_gid`: identical arithmetic; only the error
    message differs.
  - `load_elevation_corrections` in 49 and 51: a different path constant
    naming the same file.
  - `mae` in session 62: returns NaN for an empty list.
  - `load_obs_all`, F94 against F109: F109's copy has no date filter; its
    callers choose dates.
- Data check 5 confirms that last point in practice: identical observation
  series on training dates.

**The verdict.** OK.

#### Item 22 — Carried-over items

**The verdict.** FINDING. The carried items stand, and A67-14 is resolved
into A68b-04.

- **A67-04 (stale preflight text).** Confirmed. `notes/session-64-preflight-output.txt`
  prints "No reserved-year row is read anywhere in this function" (line 3)
  and the same at the end (lines 112–113), next to `rows loaded=9777` for L,
  D, T and R (lines 48–51). 9,777 − 7,952 = 1,825 reserved-year rows. No row
  is **used**: the integrity loop keeps only dates inside the training
  window (`session62_reserved_confirm.py:537`), and the dry run keeps only
  2021-03-24..2024-07-31 (`:607–608`). Disposition: stays should-fix as
  A67-04 (printed text only; frozen — owner decision). Nothing new.
- **A67-12 (pairing).** Confirmed as a wording gap only (item 9). The three
  paths produce identical series. Disposition: stays as A67-12, for triage
  alongside the planning chat's "at least should-fix" view (audit-67
  section 6.2).
- **A67-14 (`r.get`).** On the F109 path a missing feature cannot reach the
  model silently:
  - `build_complete_case()` sets all four keys on every row, and only for
    dates present in all four families (`:353–363`).
  - Data check 9: 0 rows with a missing or NaN final-set key, out of 9,777
    complete-case rows (1,956/1,956/1,955/1,955/1,955 per airport). The
    reserved fold has 365 at every airport.
  - A blank value raises in `float()`.

  The one real route to a silent gap is a literal `nan` string, which is
  A68b-04. Disposition: A67-14 is resolved as "cannot happen on the F109
  path", with the wider fragility carried by A68b-04.

---

## 3. Findings

A68b-01 | should-fix | scripts/session62_reserved_confirm.py:679–695 (frozen)
evidence: `run_confirm()`'s reserved-year gap guard raises only `if n_test == 0` (`:685`). The comment above it (`:679–682`) says it refuses "if the test window's complete-case row count is not what a genuine full year of data would give — rather than silently fitting/scoring on zero or partial rows". A partial reserved year (say 200 of 365 rows at one airport) would therefore pass the guard, and the one-look score would run on it. No effect on F109: F107 and data check 9 show 365 complete-case reserved-year rows at every airport and 0 B-days in the fold missing from the complete-case set, and F109 reports n_test 364/365/365/360/365 after the D14 pairing drop.
suggested fix: frozen — owner decision. The look is spent, so this matters only if the script is ever reused, for example as a template for a new airport. A fix would compare n_test with the expected complete-case count per airport (as D48.7 does for F94), not with zero. At minimum, record in DECISIONS that the guard is a zero-only check.

A68b-02 | should-fix | SPEC.md:463 (5.2), SPEC.md:688 and :815 (tables in 7.4 and 8.5); scripts/session39_sealed_test.py:377, scripts/session62_reserved_confirm.py:395 (both frozen)
evidence: SPEC 5.2 defines the raw-GFS baseline as "the uncorrected forecast", and SPEC 7.2 says the bar is unchanged. On the F94 and F109 paths the raw-GFS rung is `r["fc"]`, which is `temperature_grib_c`, the GRIB temperature **after** the D48.3 elevation correction (+2.044 °C at RNO, between −0.17 and +0.25 °C elsewhere). D48.10 pre-registered exactly this ("raw GFS (GRIB, elevation-corrected)"), so the code follows its lock. But SPEC 7 and 8 and RESULTS label the rung only "raw GFS (GRIB)". Their only "elevation-corrected" wording (SPEC :698, RESULTS :358, :376) describes the model inputs. A reader of SPEC alone would take the F94 and F109 margins "vs raw GFS" to be against the uncorrected forecast. How the margins would differ against an uncorrected baseline was not measured: that needs a spent-year score, which this session may not compute. The owner may judge this higher than should-fix at triage.
suggested fix: documentation. State in SPEC 7.2 (and 8.2 by reference) and in RESULTS that the GRIB methods' raw-GFS baseline is the elevation-corrected GRIB temperature (D48.10), and say how that relates to SPEC 5.2's "uncorrected". No code change.

A68b-03 | cosmetic | SPEC.md sections 7.4, 8.3, 8.5; RESULTS.md sections 5 and 6; scripts/session39_sealed_test.py:9 (frozen docstring)
evidence: the minimal method scores every rung on one common day set (D21.8). The GRIB methods score persistence on a smaller set, the days with a D−1 observation, while raw GFS and the models use every test day. F94 found this against D48.10's "same common set of days" wording (Task 2, verdict unchanged). D58 item 6 pre-registered it for F109, and F109 reports it. SPEC and RESULTS never mention it (grep finds no "previous-day", "subset" or "common" day wording in either). F94 Task 2 asked for it to be carried "for whoever eventually folds this recipe into SPEC/RESULTS". The frozen F94 docstring (`:9`) says the four rungs are scored "on the same common days", which its own code (`:381–389`, `:404`) does not do. No verdict depends on it: F94 Task 2 showed identical verdicts on the common basis, and for F109 the bound in item 6 (from recorded figures only) shows the model's MAE on the persistence day set is at most 1.0036 (EGLC) and 1.2821 (YSDU), far below persistence's 2.2259 and 2.5775.
suggested fix: documentation. One sentence in SPEC 7 and 8 (and RESULTS) naming the day basis for persistence. The frozen docstring is left alone, or noted in DECISIONS (frozen — owner decision).

A68b-04 | should-fix | scripts/session39_sealed_test.py:243–245, scripts/session62_reserved_confirm.py:270, 294, 314–316 (both frozen); the observation parse in every loader (e.g. scripts/session18_test.py:409–412)
evidence: every loader turns text into numbers with `float()`, and relies on it raising on bad input. It does raise on a blank. But `float("nan")` and `float("inf")` succeed. Data check 6 fed a synthetic sealed-window row with `temperature_grib_c = nan` to the committed F94 loader, which returned `{'fc': nan, ...}` without raising. On the model paths LightGBM treats a NaN feature as "missing" silently. On the scoring paths a NaN error makes an MAE NaN (a FAIL, not a wrong pass). Either way the gap would not be dropped and counted as SPEC 2.2 requires. A67-14's `r.get` is one case of this. No effect today: data check 7 found 0 non-finite values in every model-input column of every B and family file, in all windows, and no token but `M` in any IEM `tmpc` field.
suggested fix: frozen scripts — owner decision (their looks are spent). For any future or non-frozen code: reject non-finite values at load (`math.isfinite`), and drop and count them as missing. Add a one-line scan for non-finite values to future build checks.

A68b-05 | cosmetic | scripts/session49_upper_air_pull.py:257–262, scripts/session51_moisture_pull.py:265–270
evidence: the L and D fetches compute `valid_hour` from the decoded GRIB message but compare only the validity date with the target date. The hour is never checked. The B decode (`session37_decode.py:151`), T (`session53_pressure_pull.py:388, 431`) and R (`session55_radiation_pull.py:463`) all check the full validity datetime. No effect: the forecast hour is pinned by the exact "N hour fcst" `.idx` match, and data check 1 found the recorded validity hour equal to the expected hour on every L and D manifest row (38,166 training/sealed + 8,760 reserved).
suggested fix: none needed for the record. If these builds are reused for a new airport, check the hour as well (not frozen).

A68b-06 | cosmetic | scripts/session07_test.py:599–601, scripts/session18_test.py:1078–1079, scripts/session29_test.py:1175–1177 (and the matching lines in session13/24_test.py)
evidence: the minimal-method stop checks are not the same in all five scripts. None of the five enforces its scored-day expectation (`EXPECT_TEST_SCORED_DAYS`); it is only printed. `session29_test.py` even prints "SURPRISE (D44.11 stop signal)" without stopping. The EGLC script checks training counts with an `assert` but has no test-year count check at all. The later four stop on any training or test-year drop count that does not reconcile. No effect: 68a reproduced every count and every figure exactly.
suggested fix: none needed; these scripts' looks are spent. Note it at triage so "stop signal" wording in their output is not read as enforced.

A68b-07 | cosmetic | scripts/session03_pull.py:43–44
evidence: the EGLC Open-Meteo pull requested latitude 51.505, longitude 0.055. SPEC 3.4's airport position is 51.5053, 0.0553, and the other four pulls used the SPEC position to four decimals. Open-Meteo returned exactly SPEC 3.4's grid point (51.487137, 0.0, 4 m) in all six EGLC chunks (data check 2), so no value is affected.
suggested fix: none needed. Optionally note in DECISIONS that the EGLC request used a rounded position.

---

## 4. Clean items

These checklist items came back clean, with the evidence in section 2:

- Item 1, forecast issue time: 0 exceptions on every processed row and every manifest row.
- Item 2, no feature sees the future or an observation.
- Item 3, persistence is the D−1 target-hour observation, past-only, handled as the record says.
- Item 4, split boundaries, inclusive at both ends, no overlap, on the UTC `target_date`.
- Item 5, every fit uses training rows only; no scaler, imputer or target-derived feature.
- Item 8, target hour: UTC throughout, the same on the forecast, observation and persistence sides.
- Item 9, pairing, apart from the carried A67-12. The three paths give identical observation series.
- Item 12, cycle and lead, identical in all 9 copies and in every stored row.
- Item 15, season features, identical in all 8 copies.
- Item 16, the reserved-year build: F108's method supports its claim, and the gap it leaves is closed by this session's checks.
- Item 17, LightGBM settings equal D21.4/D48.6 in all 7 scripts, with one thread and a fixed seed.
- Item 18, feature order and columns, the same at fit and predict, with no stray column.
- Item 19, scoring: MAE, skill, strict bar, and the airport average as a mean of MAEs, matching the record.
- Item 21, copied functions are identical or differ harmlessly.

Also clean:
- **Step 0.** `git status --porcelain` at start: only `?? docs/session-68b.md`.
- **Working repo writes.** Only `notes/audit-session-68b.md` (new) and `STATUS.md` (overwritten). Every check ran from `/tmp/audit68b/`. The clone showed only `?? data/raw/grib` (its own symlink; see A68a-06).
- **Consistency of the three files** (CLAUDE.md end-of-session step 3), checked before STATUS.md was rewritten:
  - no duplicated heading in SPEC.md, STATUS.md or DECISIONS.md;
  - all 15 dated `##` headers in DECISIONS.md are in date order;
  - one disagreement between SPEC and code: SPEC 5.2 against the GRIB raw rung (A68b-02).

---

## 5. Archive candidates (listed only; no move made, per the prompt)

By the D46 criterion:
- **D49, F95 and D50** (the session 43–45 consolidation records). 68a
  listed them. Their headlines are in SPEC §7 and RESULTS §5, and no live
  question needs their wording.
- **F94.** This session used its Task 2 wording (A68b-03). It becomes a
  candidate once triage has ruled on A68b-03.
- **D60 and D61.** They define the audit. Both become candidates once the
  triage entry records the audit's outcome.
- Stay live: D17 and F7 (D46), D46 and D47 (standing rules), D51 and F96
  (D59.4), D59 and F110 (Q30), Q30, Q32, and P1–P3.

---

## 6. Appendix — data-check sources and raw outputs

Every script lives in `/tmp/audit68b/` and never writes to the working repo. Scripts marked "run from the clone" use the clone's `.venv` and import committed modules from `/tmp/audit68b/clone/scripts`; the rest use only the standard library. Outputs are pasted exactly as printed.

### 6.1 `dc1_issue_time.py` — items 1, 12: issue time, cycle and lead

````python
#!/usr/bin/env python3
"""68b item 1 (and 12): forecast issue time, cycle and lead, per airport.
Reads ONLY date/key columns (station, target_date, target_hour, run_date,
cycle, lead) of processed files, and the run/cycle/lead/detail columns of
the committed pull manifests. No feature value, no observation, no score."""
import csv, glob, os, re
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
ROOT = "/tmp/audit68b/clone"
SPEC_HOUR = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20}   # SPEC 3.4
def rule(th):  # SPEC 7.2 / D48.2
    return (th // 6) * 6, 24 + th % 6
FILES = ["grib_features_v16_window.csv", "grib_features_sealed_window.csv"] + \
    sorted(os.path.basename(p) for p in glob.glob(ROOT + "/data/processed/session*_window_with_*.csv"))
print("== A. processed per-day files: run_date/cycle/lead/target_hour vs the rule ==")
print(f"{'file':52s} {'rows':>5s} {'bad_th':>6s} {'bad_run':>7s} {'bad_cyc':>7s} {'bad_lead':>8s} {'issue<=target-24h':>17s}  target_date range")
for fn in FILES:
    rows = list(csv.DictReader(open(f"{ROOT}/data/processed/{fn}")))
    bt = br = bc = bl = 0; early = 0
    ds = []
    for r in rows:
        st = r["station"]; th = int(r["target_hour"]); td = date.fromisoformat(r["target_date"])
        rd = date.fromisoformat(r["run_date"]); cy = int(r["cycle"]); ld = int(r["lead"])
        ds.append(td)
        bt += th != SPEC_HOUR[st]
        br += rd != td - timedelta(days=1)
        c, l = rule(SPEC_HOUR[st])
        bc += cy != c; bl += ld != l
        issue = datetime(rd.year, rd.month, rd.day, cy)
        valid = datetime(td.year, td.month, td.day, th)
        early += (valid - issue) >= timedelta(hours=24) and issue + timedelta(hours=ld) == valid
    print(f"{fn:52s} {len(rows):5d} {bt:6d} {br:7d} {bc:7d} {bl:8d} {early:>10d}/{len(rows):<6d}  {min(ds)}..{max(ds)}")
print("\n   per airport, the (cycle, lead) actually stored (all files):")
seen = defaultdict(Counter)
for fn in FILES:
    for r in csv.DictReader(open(f"{ROOT}/data/processed/{fn}")):
        seen[r["station"]][(r["target_hour"], r["cycle"], r["lead"])] += 1
for st in SPEC_HOUR:
    print(f"   {st:5s} expected (th,cycle,lead)=({SPEC_HOUR[st]},{rule(SPEC_HOUR[st])[0]},{rule(SPEC_HOUR[st])[1]})  stored: {dict(seen[st])}")

print("\n== B. family pull manifests: the family's OWN fetch (run, cycle, lead, valid time) ==")
MAN = sorted(glob.glob(ROOT + "/data/raw/diagnostics/session4[9]/*_pull_manifest.csv") +
             glob.glob(ROOT + "/data/raw/diagnostics/session5[135]/*_pull_manifest.csv") +
             glob.glob(ROOT + "/data/raw/diagnostics/session63/*_pull_manifest.csv"))
VALID_RE = re.compile(r"valid=(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})")
STEP_RE = re.compile(r"startStep=(\d+) endStep=(\d+)")
for m in MAN:
    rows = list(csv.DictReader(open(m)))
    fk = "field_key" if "field_key" in rows[0] else "level_key"
    stats = Counter(); bad = []
    for r in rows:
        rd = date.fromisoformat(r["run_date"]); cy = int(r["cycle"]); ld = int(r["lead"])
        sts = r["stations"].split(",")
        for st in sts:
            c, l = rule(SPEC_HOUR[st])
            if cy != c: bad.append(("cycle", r)); break
        std_lead = rule(SPEC_HOUR[sts[0]])[1]
        offset = std_lead - ld          # 0 = standard lead, 3 = T's lead-3, 2 = R's lead-2
        stats[(r[fk], offset)] += 1
        issue = datetime(rd.year, rd.month, rd.day, cy)
        exp_valid = issue + timedelta(hours=ld)
        target = datetime(rd.year, rd.month, rd.day) + timedelta(days=1, hours=SPEC_HOUR[sts[0]])
        if exp_valid != target - timedelta(hours=offset): bad.append(("lead/target", r))
        if exp_valid > target: bad.append(("valid after target", r))
        mv = VALID_RE.search(r.get("detail", "") or r.get("note", "") or "")
        if mv:
            got = datetime.fromisoformat(f"{mv.group(1)}T{mv.group(2)}:{mv.group(3)}")
            stats[("valid-time checked", "")] += 1
            if got != exp_valid: bad.append(("valid mismatch", r))
        ms = STEP_RE.search(r.get("detail", "") or "")
        if ms:
            stats[(f"steps {ms.group(1)}-{ms.group(2)} at lead {ld}", "")] += 1
    rel = os.path.relpath(m, ROOT)
    print(f"\n   {rel}: {len(rows)} rows, problems: {len(bad)}")
    for k, v in sorted(stats.items(), key=str):
        print(f"      {k}: {v}")
    for b in bad[:5]: print("      BAD", b)
print("\n   manifest columns:", list(csv.DictReader(open(MAN[0])).fieldnames))
````

**Raw output** (`/tmp/audit68b/dc1_output.txt`):

````
== A. processed per-day files: run_date/cycle/lead/target_hour vs the rule ==
file                                                  rows bad_th bad_run bad_cyc bad_lead issue<=target-24h  target_date range
grib_features_v16_window.csv                          7952      0       0       0        0       7952/7952    2021-03-24..2025-07-31
grib_features_sealed_window.csv                       1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session49_sealed_window_with_upper_air.csv            1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session49_v16_window_with_upper_air.csv               6127      0       0       0        0       6127/6127    2021-03-24..2024-07-31
session51_sealed_window_with_moisture.csv             1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session51_v16_window_with_moisture.csv                6127      0       0       0        0       6127/6127    2021-03-24..2024-07-31
session53_sealed_window_with_pressure.csv             1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session53_v16_window_with_pressure.csv                6127      0       0       0        0       6127/6127    2021-03-24..2024-07-31
session55_sealed_window_with_radiation.csv            1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session55_v16_window_with_radiation.csv               6127      0       0       0        0       6127/6127    2021-03-24..2024-07-31
session57_sealed_window_with_precip.csv               1825      0       0       0        0       1825/1825    2025-08-01..2026-07-31
session57_v16_window_with_precip.csv                  6127      0       0       0        0       6127/6127    2021-03-24..2024-07-31
session63_reserved_window_with_moisture.csv           1825      0       0       0        0       1825/1825    2024-08-01..2025-07-31
session63_reserved_window_with_pressure.csv           1825      0       0       0        0       1825/1825    2024-08-01..2025-07-31
session63_reserved_window_with_radiation.csv          1825      0       0       0        0       1825/1825    2024-08-01..2025-07-31
session63_reserved_window_with_upper_air.csv          1825      0       0       0        0       1825/1825    2024-08-01..2025-07-31

   per airport, the (cycle, lead) actually stored (all files):
   EGLC  expected (th,cycle,lead)=(12,12,24)  stored: {('12', '12', '24'): 11371}
   LFPG  expected (th,cycle,lead)=(12,12,24)  stored: {('12', '12', '24'): 11371}
   DSM   expected (th,cycle,lead)=(18,18,24)  stored: {('18', '18', '24'): 11365}
   YSDU  expected (th,cycle,lead)=(2,0,26)  stored: {('2', '0', '26'): 11365}
   RNO   expected (th,cycle,lead)=(20,18,26)  stored: {('20', '18', '26'): 11365}

== B. family pull manifests: the family's OWN fetch (run, cycle, lead, valid time) ==

   data/raw/diagnostics/session49/session49_pull_manifest.csv: 19083 rows, problems: 0
      ('t700', 0): 6361
      ('t850', 0): 6361
      ('t925', 0): 6361
      ('valid-time checked', ''): 19083

   data/raw/diagnostics/session51/session51_pull_manifest.csv: 19083 rows, problems: 0
      ('dew_point_2m', 0): 6361
      ('relative_humidity_2m', 0): 6361
      ('specific_humidity_2m', 0): 6361
      ('valid-time checked', ''): 19083

   data/raw/diagnostics/session53/session53_pull_manifest.csv: 19083 rows, problems: 0
      ('pressure_msl_hpa', 0): 6361
      ('pressure_msl_lead_minus3_hpa', 3): 6361
      ('pressure_surface_hpa', 0): 6361
      ('valid-time checked', ''): 19083

   data/raw/diagnostics/session55/session55_pull_manifest.csv: 9542 rows, problems: 0
      ('dswrf_to_lead', 0): 6361
      ('dswrf_to_lead_minus2', 2): 3181
      ('steps 18-22 at lead 22', ''): 3181
      ('steps 18-24 at lead 24', ''): 3181
      ('steps 24-26 at lead 26', ''): 3180

   data/raw/diagnostics/session63/session63_moisture_pull_manifest.csv: 4380 rows, problems: 0
      ('dew_point_2m', 0): 1460
      ('relative_humidity_2m', 0): 1460
      ('specific_humidity_2m', 0): 1460
      ('valid-time checked', ''): 4380

   data/raw/diagnostics/session63/session63_pressure_pull_manifest.csv: 4380 rows, problems: 0
      ('pressure_msl_hpa', 0): 1460
      ('pressure_msl_lead_minus3_hpa', 3): 1460
      ('pressure_surface_hpa', 0): 1460
      ('valid-time checked', ''): 4380

   data/raw/diagnostics/session63/session63_radiation_pull_manifest.csv: 2190 rows, problems: 0
      ('dswrf_to_lead', 0): 1460
      ('dswrf_to_lead_minus2', 2): 730
      ('steps 18-22 at lead 22', ''): 730
      ('steps 18-24 at lead 24', ''): 730
      ('steps 24-26 at lead 26', ''): 730

   data/raw/diagnostics/session63/session63_upper_air_pull_manifest.csv: 4380 rows, problems: 0
      ('t700', 0): 1460
      ('t850', 0): 1460
      ('t925', 0): 1460
      ('valid-time checked', ''): 4380

   manifest columns: ['run_date', 'cycle', 'lead', 'level_key', 'stations', 'status', 'detail']
````

### 6.2 `dc2_openmeteo_meta.py` — items 1, 8, 10, 11: Open-Meteo metadata

````python
#!/usr/bin/env python3
"""68b items 1, 8, 10: metadata of the tracked Open-Meteo chunks the minimal
method reads. Reads only the JSON header fields, the time axis, and a count
of null values at each airport's target hour. No value is compared with an
observation."""
import json
from datetime import datetime
ROOT = "/tmp/audit68b/clone/data/raw/"
SPEC = {  # SPEC 3.4: target hour, grid lat, grid lon, grid elev
    "EGLC": (12, 51.487137, 0.0, 4), "LFPG": (12, 49.027008, 2.578125, 109),
    "DSM": (18, 41.52945, -93.63281, 285), "YSDU": (2, -32.274643, 148.59375, 279),
    "RNO": (20, 39.537918, -119.765625, 1344)}
CHUNKS = [("2021-03-24", "2021-12-31"), ("2022-01-01", "2022-12-31"), ("2023-01-01", "2023-12-31"),
          ("2024-01-01", "2024-12-31"), ("2025-01-01", "2025-12-31"), ("2026-01-01", "2026-07-31")]
for st, (th, glat, glon, gel) in SPEC.items():
    for s, e in CHUNKS:
        d = json.load(open(f"{ROOT}openmeteo_previousruns_gfs_global_{st}_{s}_{e}.json"))
        h = d["hourly"]; t = h["time"]; v = h["temperature_2m_previous_day1"]
        step_ok = all((datetime.fromisoformat(b) - datetime.fromisoformat(a)).total_seconds() == 3600 for a, b in zip(t, t[1:]))
        at_th = [x for tt, x in zip(t, v) if int(tt[11:13]) == th]
        print(f"{st:5s} {s}..{e} tz={d.get('timezone')} off={d.get('utc_offset_seconds')} "
              f"unit={d['hourly_units'].get('temperature_2m_previous_day1')} "
              f"grid=({d['latitude']},{d['longitude']},{d.get('elevation')}) "
              f"spec_match={abs(d['latitude']-glat)<1e-5 and abs(d['longitude']-glon)<1e-5} "
              f"first={t[0]} last={t[-1]} hourly_steps_ok={step_ok} "
              f"target_hour_values={len(at_th)} nulls={sum(x is None for x in at_th)}")
````

**Raw output** (`/tmp/audit68b/dc2_output.txt`):

````
EGLC  2021-03-24..2021-12-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2021-03-24T00:00 last=2021-12-31T23:00 hourly_steps_ok=True target_hour_values=283 nulls=0
EGLC  2022-01-01..2022-12-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2022-01-01T00:00 last=2022-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
EGLC  2023-01-01..2023-12-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2023-01-01T00:00 last=2023-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=2
EGLC  2024-01-01..2024-12-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2024-01-01T00:00 last=2024-12-31T23:00 hourly_steps_ok=True target_hour_values=366 nulls=18
EGLC  2025-01-01..2025-12-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2025-01-01T00:00 last=2025-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
EGLC  2026-01-01..2026-07-31 tz=GMT off=0 unit=°C grid=(51.487137,0.0,4.0) spec_match=True first=2026-01-01T00:00 last=2026-07-31T23:00 hourly_steps_ok=True target_hour_values=212 nulls=0
LFPG  2021-03-24..2021-12-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2021-03-24T00:00 last=2021-12-31T23:00 hourly_steps_ok=True target_hour_values=283 nulls=0
LFPG  2022-01-01..2022-12-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2022-01-01T00:00 last=2022-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
LFPG  2023-01-01..2023-12-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2023-01-01T00:00 last=2023-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=2
LFPG  2024-01-01..2024-12-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2024-01-01T00:00 last=2024-12-31T23:00 hourly_steps_ok=True target_hour_values=366 nulls=18
LFPG  2025-01-01..2025-12-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2025-01-01T00:00 last=2025-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
LFPG  2026-01-01..2026-07-31 tz=GMT off=0 unit=°C grid=(49.027008,2.578125,109.0) spec_match=True first=2026-01-01T00:00 last=2026-07-31T23:00 hourly_steps_ok=True target_hour_values=212 nulls=0
DSM   2021-03-24..2021-12-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2021-03-24T00:00 last=2021-12-31T23:00 hourly_steps_ok=True target_hour_values=283 nulls=0
DSM   2022-01-01..2022-12-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2022-01-01T00:00 last=2022-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
DSM   2023-01-01..2023-12-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2023-01-01T00:00 last=2023-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=2
DSM   2024-01-01..2024-12-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2024-01-01T00:00 last=2024-12-31T23:00 hourly_steps_ok=True target_hour_values=366 nulls=18
DSM   2025-01-01..2025-12-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2025-01-01T00:00 last=2025-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
DSM   2026-01-01..2026-07-31 tz=GMT off=0 unit=°C grid=(41.52945,-93.63281,285.0) spec_match=True first=2026-01-01T00:00 last=2026-07-31T23:00 hourly_steps_ok=True target_hour_values=212 nulls=0
YSDU  2021-03-24..2021-12-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2021-03-24T00:00 last=2021-12-31T23:00 hourly_steps_ok=True target_hour_values=283 nulls=0
YSDU  2022-01-01..2022-12-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2022-01-01T00:00 last=2022-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
YSDU  2023-01-01..2023-12-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2023-01-01T00:00 last=2023-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=2
YSDU  2024-01-01..2024-12-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2024-01-01T00:00 last=2024-12-31T23:00 hourly_steps_ok=True target_hour_values=366 nulls=19
YSDU  2025-01-01..2025-12-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2025-01-01T00:00 last=2025-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
YSDU  2026-01-01..2026-07-31 tz=GMT off=0 unit=°C grid=(-32.274643,148.59375,279.0) spec_match=True first=2026-01-01T00:00 last=2026-07-31T23:00 hourly_steps_ok=True target_hour_values=212 nulls=0
RNO   2021-03-24..2021-12-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2021-03-24T00:00 last=2021-12-31T23:00 hourly_steps_ok=True target_hour_values=283 nulls=0
RNO   2022-01-01..2022-12-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2022-01-01T00:00 last=2022-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
RNO   2023-01-01..2023-12-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2023-01-01T00:00 last=2023-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=2
RNO   2024-01-01..2024-12-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2024-01-01T00:00 last=2024-12-31T23:00 hourly_steps_ok=True target_hour_values=366 nulls=18
RNO   2025-01-01..2025-12-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2025-01-01T00:00 last=2025-12-31T23:00 hourly_steps_ok=True target_hour_values=365 nulls=0
RNO   2026-01-01..2026-07-31 tz=GMT off=0 unit=°C grid=(39.537918,-119.765625,1344.0) spec_match=True first=2026-01-01T00:00 last=2026-07-31T23:00 hourly_steps_ok=True target_hour_values=212 nulls=0
````

### 6.3 `dc3_grid_weights.py` — item 11: grid neighbours and weights (run from the clone)

````python
#!/usr/bin/env python3
"""68b item 11: for each airport, on one TRAINING date (2022-11-26), print
the four GRIB grid points eccodes returns, the bilinear weights the committed
code uses, and the value the committed bilinear_value() returns, against the
stored processed CSV value (forecast vs stored forecast; no observation).
Reads the gitignored GRIB cache read-only, through the clone's symlink."""
import csv, sys
from datetime import date
sys.path.insert(0, "/tmp/audit68b/clone/scripts")
import eccodes as ec
import session37_decode as s37
TD = date(2022, 11, 26)
stored = {r["station"]: r for r in csv.DictReader(open("/tmp/audit68b/clone/data/processed/grib_features_v16_window.csv")) if r["target_date"] == TD.isoformat()}
corr = s37.load_elevation_corrections()
for st, (th, lat, lon) in s37.AIRPORTS.items():
    cyc, lead = s37.cycle_and_lead(th)
    files = s37.grib_files_for(TD.fromordinal(TD.toordinal() - 1), cyc, lead)
    with open(files["tmp2m"], "rb") as f:
        gid = ec.codes_grib_new_from_file(f)
        nb = ec.codes_grib_find_nearest(gid, lat, lon, npoints=4)
        lon_first = ec.codes_get(gid, "longitudeOfFirstGridPointInDegrees")
        lon_last = ec.codes_get(gid, "longitudeOfLastGridPointInDegrees")
        lat_first = ec.codes_get(gid, "latitudeOfFirstGridPointInDegrees")
        lat_last = ec.codes_get(gid, "latitudeOfLastGridPointInDegrees")
        ec.codes_release(gid)
    lats = sorted(set(round(n.lat, 6) for n in nb)); lons = sorted(set(round(n.lon, 6) for n in nb))
    lon_q = lon + 360.0 if lon < 0 else lon
    lat0, lat1 = lats; lon0, lon1 = lons
    dlat = (lat - lat0) / (lat1 - lat0); dlon = (lon_q - lon0) / (lon1 - lon0)
    w = {(lat0, lon0): (1-dlat)*(1-dlon), (lat0, lon1): (1-dlat)*dlon, (lat1, lon0): dlat*(1-dlon), (lat1, lon1): dlat*dlon}
    print(f"{st}: file grid lat {lat_first}..{lat_last}, lon {lon_first}..{lon_last} (0-360 convention)")
    print(f"   query (lat, lon)=({lat}, {lon}) -> lon used {lon_q}; dlat={dlat:.6f} dlon={dlon:.6f}; "
          f"inside cell: {lat0 <= lat <= lat1 and lon0 <= lon_q <= lon1}")
    for n in sorted(nb, key=lambda n: (n.lat, n.lon)):
        k = (round(n.lat, 6), round(n.lon, 6))
        print(f"   neighbour lat={n.lat:9.3f} lon={n.lon:8.3f} value={n.value - 273.15:8.3f} C  weight={w[k]:.6f}")
    print(f"   weights sum={sum(w.values()):.9f}")
    val, vd, vt = s37.bilinear_value(files["tmp2m"], lat, lon, "2t")
    rebuilt = round(val - 273.15 + corr[st], 3)
    print(f"   committed bilinear_value -> {val - 273.15:.4f} C, + elevation corr {corr[st]:+.4f} = {rebuilt}; "
          f"stored temperature_grib_c = {stored[st]['temperature_grib_c']}  match={rebuilt == float(stored[st]['temperature_grib_c'])}; valid {vd} {vt:04d}")
````

**Raw output** (`/tmp/audit68b/dc3_output.txt`):

````
EGLC: file grid lat 90.0..-90.0, lon 0.0..359.75 (0-360 convention)
   query (lat, lon)=(51.487137, 0.0) -> lon used 0.0; dlat=0.948548 dlon=0.000000; inside cell: True
   neighbour lat=   51.250 lon=   0.000 value=  11.141 C  weight=0.051452
   neighbour lat=   51.250 lon=   0.250 value=  11.461 C  weight=0.000000
   neighbour lat=   51.500 lon=   0.000 value=  11.951 C  weight=0.948548
   neighbour lat=   51.500 lon=   0.250 value=  12.031 C  weight=0.000000
   weights sum=1.000000000
   committed bilinear_value -> 11.9092 C, + elevation corr +0.2486 = 12.158; stored temperature_grib_c = 12.158  match=True; valid 20221126 1200
LFPG: file grid lat 90.0..-90.0, lon 0.0..359.75 (0-360 convention)
   query (lat, lon)=(49.027008, 2.578125) -> lon used 2.578125; dlat=0.108032 dlon=0.312500; inside cell: True
   neighbour lat=   49.000 lon=   2.500 value=  10.051 C  weight=0.613228
   neighbour lat=   49.000 lon=   2.750 value=   9.901 C  weight=0.278740
   neighbour lat=   49.250 lon=   2.500 value=  10.101 C  weight=0.074272
   neighbour lat=   49.250 lon=   2.750 value=  10.011 C  weight=0.033760
   weights sum=1.000000000
   committed bilinear_value -> 10.0114 C, + elevation corr -0.1697 = 9.842; stored temperature_grib_c = 9.842  match=True; valid 20221126 1200
DSM: file grid lat 90.0..-90.0, lon 0.0..359.75 (0-360 convention)
   query (lat, lon)=(41.52945, -93.63281) -> lon used 266.36719; dlat=0.117800 dlon=0.468760; inside cell: True
   neighbour lat=   41.500 lon= 266.250 value=  10.686 C  weight=0.468660
   neighbour lat=   41.500 lon= 266.500 value=  10.256 C  weight=0.413540
   neighbour lat=   41.750 lon= 266.250 value=  10.776 C  weight=0.062580
   neighbour lat=   41.750 lon= 266.500 value=  10.336 C  weight=0.055220
   weights sum=1.000000000
   committed bilinear_value -> 10.4941 C, + elevation corr -0.1106 = 10.384; stored temperature_grib_c = 10.384  match=True; valid 20221126 1800
YSDU: file grid lat 90.0..-90.0, lon 0.0..359.75 (0-360 convention)
   query (lat, lon)=(-32.274643, 148.59375) -> lon used 148.59375; dlat=0.901428 dlon=0.375000; inside cell: True
   neighbour lat=  -32.500 lon= 148.500 value=  26.622 C  weight=0.061607
   neighbour lat=  -32.500 lon= 148.750 value=  26.252 C  weight=0.036964
   neighbour lat=  -32.250 lon= 148.500 value=  28.312 C  weight=0.563393
   neighbour lat=  -32.250 lon= 148.750 value=  26.592 C  weight=0.338036
   weights sum=1.000000000
   committed bilinear_value -> 27.5507 C, + elevation corr +0.2461 = 27.797; stored temperature_grib_c = 27.797  match=True; valid 20221126 0200
RNO: file grid lat 90.0..-90.0, lon 0.0..359.75 (0-360 convention)
   query (lat, lon)=(39.537918, -119.765625) -> lon used 240.234375; dlat=0.151672 dlon=0.937500; inside cell: True
   neighbour lat=   39.500 lon= 240.000 value=   6.153 C  weight=0.053021
   neighbour lat=   39.500 lon= 240.250 value=   7.203 C  weight=0.795308
   neighbour lat=   39.750 lon= 240.000 value=   6.473 C  weight=0.009479
   neighbour lat=   39.750 lon= 240.250 value=   7.333 C  weight=0.142192
   weights sum=1.000000000
   committed bilinear_value -> 7.1589 C, + elevation corr +2.0436 = 9.203; stored temperature_grib_c = 9.203  match=True; valid 20221126 2000
````

### 6.4 `dc4_family_columns.py` — items 10, 13, 14, 16: family identities, units, blanks

````python
#!/usr/bin/env python3
"""68b items 10, 13, 14, 16, 22 (A67-14): arithmetic identities, units and
blanks in the L, D, T, R family files, all three windows. Reads FEATURE
columns only (no observation, no target, no model, no score)."""
import csv, math
from collections import defaultdict
P = "/tmp/audit68b/clone/data/processed/"
corr = {r["station"]: float(r["correction_c"]) for r in csv.DictReader(open("/tmp/audit68b/clone/data/raw/diagnostics/session37/session37_elevation_correction_params.csv"))}
FAM = {
 "L": ("session49_v16_window_with_upper_air.csv", "session49_sealed_window_with_upper_air.csv", "session63_reserved_window_with_upper_air.csv"),
 "D": ("session51_v16_window_with_moisture.csv", "session51_sealed_window_with_moisture.csv", "session63_reserved_window_with_moisture.csv"),
 "T": ("session53_v16_window_with_pressure.csv", "session53_sealed_window_with_pressure.csv", "session63_reserved_window_with_pressure.csv"),
 "R": ("session55_v16_window_with_radiation.csv", "session55_sealed_window_with_radiation.csv", "session63_reserved_window_with_radiation.csv"),
}
FINAL = {"L": "lapse_rate_t2_t850", "D": "dewpoint_depression_t2m", "T": "pressure_tendency_3h_hpa", "R": "dswrf_2h_wm2"}
UNITCOL = {"L": "t850", "D": "dew_point_2m", "T": "pressure_msl_hpa", "R": "dswrf_2h_wm2"}
def isbad(s):
    if s is None or s.strip() == "": return True
    try: return math.isnan(float(s)) or math.isinf(float(s))
    except ValueError: return True
print(f"{'fam':3s} {'window':9s} {'rows':>5s} {'blank/NaN final col':>19s} {'identity max|diff|':>18s} {'t2m_raw id':>10s}   {UNITCOL['L']+'/..':>8s} per airport: min..max (mean)")
for fam, files in FAM.items():
    for win, fn in zip(("v16", "sealed", "reserved"), files):
        rows = list(csv.DictReader(open(P + fn)))
        bad = sum(isbad(r[FINAL[fam]]) for r in rows)
        idmax = 0.0; t2max = 0.0; neg = 0
        stat = defaultdict(list)
        for r in rows:
            st = r["station"]
            if fam in ("L", "D"):
                t2 = round(float(r["temperature_grib_c"]) - corr[st], 3)
                t2max = max(t2max, abs(t2 - float(r["t2m_raw"])))
            if fam == "L":
                idmax = max(idmax, abs(round(float(r["t2m_raw"]) - float(r["t850"]), 3) - float(r[FINAL[fam]])))
            elif fam == "D":
                idmax = max(idmax, abs(round(float(r["t2m_raw"]) - float(r["dew_point_2m"]), 3) - float(r[FINAL[fam]])))
                neg += float(r[FINAL[fam]]) < 0
            elif fam == "T":
                idmax = max(idmax, abs(round(float(r["pressure_msl_hpa"]) - float(r["pressure_msl_lead_minus3_hpa"]), 3) - float(r[FINAL[fam]])))
            elif fam == "R":
                a = float(r["dswrf_ave_to_lead_wm2"]); b = r["dswrf_ave_to_lead_minus2_wm2"]
                exp = (a * 6 - float(b) * 4) / 2 if b != "" else a
                idmax = max(idmax, abs(exp - float(r[FINAL[fam]])))
                neg += float(r[FINAL[fam]]) < 0
            stat[st].append(float(r[UNITCOL[fam]]))
        summ = "  ".join(f"{st} {min(v):.1f}..{max(v):.1f} ({sum(v)/len(v):.1f})" for st, v in sorted(stat.items()))
        extra = f" negatives={neg}" if fam in ("D", "R") else ""
        print(f"{fam:3s} {win:9s} {len(rows):5d} {bad:19d} {idmax:18.6f} {t2max if fam in 'LD' else float('nan'):10.6f}   [{UNITCOL[fam]}] {summ}{extra}")
````

**Raw output** (`/tmp/audit68b/dc4_output.txt`):

````
fam window     rows blank/NaN final col identity max|diff| t2m_raw id    t850/.. per airport: min..max (mean)
L   v16        6127                   0           0.000000   0.000000   [t850] DSM -24.4..28.1 (7.1)  EGLC -10.6..22.8 (3.7)  LFPG -10.2..23.2 (5.0)  RNO -6.6..35.5 (15.9)  YSDU -3.8..24.3 (9.4)
L   sealed     1825                   0           0.000000   0.000000   [t850] DSM -22.8..26.9 (7.4)  EGLC -9.7..20.9 (4.3)  LFPG -9.7..21.9 (5.6)  RNO -2.4..32.9 (17.0)  YSDU -3.5..28.3 (11.2)
L   reserved   1825                   0           0.000000   0.000000   [t850] DSM -26.5..26.3 (6.6)  EGLC -7.7..19.5 (4.2)  LFPG -6.6..21.1 (5.4)  RNO -2.8..33.5 (15.9)  YSDU -1.5..23.7 (11.2)
D   v16        6127                   0           0.000000   0.000000   [dew_point_2m] DSM -27.2..24.0 (5.6)  EGLC -11.2..18.0 (6.7)  LFPG -13.4..19.9 (6.9)  RNO -20.8..10.1 (-3.8)  YSDU -5.5..20.7 (7.9) negatives=1
D   sealed     1825                   0           0.000000   0.000000   [dew_point_2m] DSM -34.5..24.5 (5.5)  EGLC -9.3..17.8 (6.6)  LFPG -8.5..17.0 (6.3)  RNO -17.7..10.4 (-2.9)  YSDU -7.7..17.5 (7.0) negatives=0
D   reserved   1825                   0           0.000000   0.000000   [dew_point_2m] DSM -31.1..25.0 (4.9)  EGLC -6.2..17.9 (6.5)  LFPG -8.4..19.0 (6.9)  RNO -19.3..7.8 (-4.6)  YSDU -8.2..19.4 (7.9) negatives=0
T   v16        6127                   0           0.000000        nan   [pressure_msl_hpa] DSM 991.0..1041.9 (1015.5)  EGLC 962.2..1046.0 (1015.2)  LFPG 976.3..1042.4 (1016.6)  RNO 998.1..1035.5 (1014.2)  YSDU 996.8..1034.7 (1017.0)
T   sealed     1825                   0           0.000000        nan   [pressure_msl_hpa] DSM 991.6..1048.7 (1016.5)  EGLC 983.3..1034.2 (1014.2)  LFPG 986.7..1032.0 (1015.6)  RNO 1000.3..1037.1 (1014.7)  YSDU 997.9..1033.7 (1016.6)
T   reserved   1825                   0           0.000000        nan   [pressure_msl_hpa] DSM 987.6..1042.7 (1016.8)  EGLC 980.6..1042.7 (1017.0)  LFPG 985.2..1040.0 (1017.8)  RNO 1000.0..1034.1 (1014.7)  YSDU 998.2..1032.1 (1016.4)
R   v16        6127                   0           0.002000        nan   [dswrf_2h_wm2] DSM 8.3..964.5 (571.0)  EGLC 4.1..888.5 (426.9)  LFPG 3.5..910.3 (464.0)  RNO 47.4..1031.1 (726.3)  YSDU 11.9..1106.5 (674.4) negatives=0
R   sealed     1825                   0           0.002000        nan   [dswrf_2h_wm2] DSM 11.1..947.0 (553.9)  EGLC 4.8..867.0 (428.8)  LFPG 8.6..898.0 (466.9)  RNO 40.7..1015.9 (695.9)  YSDU 43.5..1090.7 (714.6) negatives=0
R   reserved   1825                   0           0.002000        nan   [dswrf_2h_wm2] DSM 10.0..932.4 (554.4)  EGLC 7.0..875.6 (415.0)  LFPG 6.9..905.6 (465.5)  RNO 25.6..1023.7 (712.6)  YSDU 22.9..1088.3 (707.2) negatives=0
````

### 6.5 `dc5_obs_paths.py` — items 3, 8, 9, 21: observation series across the three paths

````python
#!/usr/bin/env python3
"""68b items 3, 8, 9, 21: the committed observation loaders of all seven
headline scripts, run unchanged (extracted by AST and exec'd, because the
minimal-method scripts call main() at import), compared with each other on
TRAINING-WINDOW dates only (2021-03-24..2024-07-31, the part every path's
training covers). Observations only: no forecast, no model, no score."""
import ast, csv
from datetime import date, datetime, timedelta
from pathlib import Path
ROOT = Path("/tmp/audit68b/clone"); S = ROOT / "scripts"
LO, HI = date(2021, 3, 24), date(2024, 7, 31)
MIN = {"EGLC": ("session07_test.py", "load_obs_12z"), "LFPG": ("session13_test.py", "load_obs_12z"),
       "DSM": ("session18_test.py", "load_obs_target_hour"), "YSDU": ("session24_test.py", "load_obs_target_hour"),
       "RNO": ("session29_test.py", "load_obs_target_hour")}
HOUR = {"EGLC": 12, "LFPG": 12, "DSM": 18, "YSDU": 2, "RNO": 20}
def extract(fname, func, names):
    tree = ast.parse((S / fname).read_text())
    ns = {"csv": csv, "datetime": datetime, "timedelta": timedelta, "date": date, "RAW": ROOT / "data" / "raw", "ROOT": ROOT}
    keep = [n for n in tree.body if (isinstance(n, ast.FunctionDef) and n.name == func) or
            (isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id in names)]
    exec(compile(ast.Module(body=keep, type_ignores=[]), fname, "exec"), ns)
    return ns[func]
CONSTS = ["STATION", "TARGET_HOUR", "HARD_END", "TEST_END", "CHUNKS", "OBS_CHUNKS", "TRAIN_START", "SEALED_UNTIL"]
print(f"{'st':5s} {'minimal':>8s} {'s39(F94)':>8s} {'s62(F109)':>9s}  all three equal on training dates?  days with obs(D) but not obs(D-1)")
for st, (fn, func) in MIN.items():
    f_min = extract(fn, func, ["STATION", "TARGET_HOUR", "TEST_END", "HARD_END", "CHUNKS"])
    a = f_min()[0]
    f39 = extract("session39_sealed_test.py", "load_obs_all", ["OBS_CHUNKS", "TRAIN_START", "SEALED_UNTIL"])
    b = f39(st, HOUR[st])[0]
    f62 = extract("session62_reserved_confirm.py", "load_obs_all", ["OBS_CHUNKS"])
    c = f62(st, HOUR[st])[0]
    win = lambda s: {d: v for d, v in s.items() if LO <= d <= HI}
    A, B, C = win(a), win(b), win(c)
    no_prev = sum(1 for d in A if d - timedelta(days=1) not in a and d > LO)
    print(f"{st:5s} {len(A):8d} {len(B):8d} {len(C):9d}  {A == B == C}   {no_prev}")
````

**Raw output** (`/tmp/audit68b/dc5_output.txt`):

````
st     minimal s39(F94) s62(F109)  all three equal on training dates?  days with obs(D) but not obs(D-1)
EGLC      1225     1225      1225  True   1
LFPG      1224     1224      1224  True   2
DSM       1226     1226      1226  True   0
YSDU      1214     1214      1214  True   9
RNO       1223     1223      1223  True   2
````

### 6.6 `dc6_guards.py` — item 7: guards on synthetic dates (run from the clone)

````python
#!/usr/bin/env python3
"""68b item 7: the committed guards, called on SYNTHETIC dates and synthetic
CSV files written under /tmp/audit68b/synth/. No real spent-year row is read.
No model is fit (session39/session62 are imported for their functions only;
their main() is never called)."""
import csv, sys, traceback
from datetime import date
from pathlib import Path
sys.path.insert(0, "/tmp/audit68b/clone/scripts")
SY = Path("/tmp/audit68b/synth"); SY.mkdir(exist_ok=True)
import session48_reserved_year as g
import session39_sealed_test as s39
import session62_reserved_confirm as s62
import session63_reserved_year_build as s63
def expect(label, fn, should_raise):
    try:
        fn(); raised = None
    except Exception as e:
        raised = f"{type(e).__name__}: {str(e)[:110]}"
    ok = (raised is not None) == should_raise
    print(f"  [{'OK ' if ok else 'BAD'}] {label:70s} -> {'raised ' + raised if raised else 'did not raise'}")
    return ok
res = []
print("A. assert_reserved_year_excluded (session48), inclusive edges")
A = g.assert_reserved_year_excluded
res.append(expect("train ends 2024-07-31, test 2025-08-01..2026-07-31", lambda: A("t", date(2021,3,24), date(2024,7,31), date(2025,8,1), date(2026,7,31)), False))
res.append(expect("train ends 2024-08-01 (first reserved day)", lambda: A("t", date(2021,3,24), date(2024,8,1), date(2025,8,1), date(2026,7,31)), True))
res.append(expect("test starts 2025-07-31 (last reserved day)", lambda: A("t", date(2021,3,24), date(2024,7,31), date(2025,7,31), date(2026,7,31)), True))
res.append(expect("train wholly after reserved year 2025-08-01..2025-12-31", lambda: A("t", date(2025,8,1), date(2025,12,31), date(2026,1,1), date(2026,7,31)), False))
res.append(expect("train surrounds reserved year 2021..2026", lambda: A("t", date(2021,3,24), date(2026,7,31), date(2026,8,1), date(2026,8,2)), True))
res.append(expect("CONFIRMATION_FOLD itself (must raise: why run_confirm never calls it)", lambda: A("c", **{k: s62.CONFIRMATION_FOLD[k] for k in ("train_start","train_end","test_start","test_end")}) if False else A("c", s62.CONFIRMATION_FOLD["train_start"], s62.CONFIRMATION_FOLD["train_end"], s62.CONFIRMATION_FOLD["test_start"], s62.CONFIRMATION_FOLD["test_end"]), True))
for lbl, a, b, c, d in g.EXPERIMENT_FOLDS:
    res.append(expect(f"EXPERIMENT_FOLDS {lbl}", lambda a=a, b=b, c=c, d=d: A(lbl, a, b, c, d), False))
print("\nB. session39 load_grib_features D48 self-guard (synthetic CSV)")
hdr = ["station","target_date","target_hour","run_date","cycle","lead","temperature_grib_c","cloud_cover_grib_pct","wind_speed_grib_kmh"]
def write(name, rows):
    p = SY / name
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
    return p
ok_p = write("in_window.csv", [["EGLC","2025-08-01",12,"2025-07-31",12,24,"1.0","2.0","3.0"], ["EGLC","2026-07-31",12,"2026-07-30",12,24,"1.0","2.0","3.0"]])
bad_hi = write("after_window.csv", [["EGLC","2026-08-01",12,"2026-07-31",12,24,"1.0","2.0","3.0"]])
bad_lo = write("before_window.csv", [["RNO","2025-07-31",20,"2025-07-30",18,26,"1.0","2.0","3.0"]])
blank = write("blank_value.csv", [["DSM","2025-09-01",18,"2025-08-31",18,24,"","2.0","3.0"]])
nan = write("nan_value.csv", [["DSM","2025-09-01",18,"2025-08-31",18,24,"nan","2.0","3.0"]])
L = s39.load_grib_features
res.append(expect("in-window edges 2025-08-01 and 2026-07-31", lambda: L(ok_p, s39.SEALED_FROM, s39.SEALED_UNTIL, True), False))
res.append(expect("row dated 2026-08-01 (one day after)", lambda: L(bad_hi, s39.SEALED_FROM, s39.SEALED_UNTIL, True), True))
res.append(expect("row dated 2025-07-31 in the sealed file (one day before)", lambda: L(bad_lo, s39.SEALED_FROM, s39.SEALED_UNTIL, True), True))
res.append(expect("missing file", lambda: L(SY / "nope.csv", s39.SEALED_FROM, s39.SEALED_UNTIL, True), True))
res.append(expect("blank temperature value (must not become 0 or NaN)", lambda: L(blank, s39.SEALED_FROM, s39.SEALED_UNTIL, True), True))
got = {}
res.append(expect("literal 'nan' temperature string (informative: parsed silently?)", lambda: got.update(v=L(nan, s39.SEALED_FROM, s39.SEALED_UNTIL, True)["DSM"]), True))
print(f"      -> loader returned for the 'nan' row: {got.get('v')}")
print("\nC. session62 load_family: out-of-range row in a reserved-year family file (synthetic)")
fam_hdr = ["station","target_date","lapse_rate_t2_t850"]
def famfile(name, rows):
    p = SY / name
    with open(p, "w", newline="") as f:
        w = csv.writer(f); w.writerow(fam_hdr); w.writerows(rows)
    return p
v16 = famfile("fam_v16.csv", [["EGLC","2022-01-01","5.0"]]); sealed = famfile("fam_sealed.csv", [["EGLC","2025-09-01","5.0"]])
res_ok = famfile("fam_res_ok.csv", [["EGLC","2024-08-01","5.0"], ["EGLC","2025-07-31","5.0"]])
res_bad = famfile("fam_res_bad.csv", [["EGLC","2025-08-01","5.0"]])
leak = famfile("fam_v16_leak.csv", [["EGLC","2024-12-01","5.0"]])
saved_cf = dict(s62.CANDIDATE_FEATURES["L"]); saved_rf = dict(s62.RESERVED_FAMILY_FILES)
try:
    s62.CANDIDATE_FEATURES["L"] = dict(saved_cf, v16_file=v16, sealed_file=sealed)
    s62.RESERVED_FAMILY_FILES["L"] = res_ok
    out = {}
    res.append(expect("reserved file with rows on 2024-08-01 and 2025-07-31", lambda: out.update(r=s62.load_family("L", ["lapse_rate_t2_t850"])), False))
    print(f"      -> rows loaded EGLC: {sorted(out['r'][0]['EGLC'])}, reserved hits in v16/sealed: {out['r'][1]}")
    s62.RESERVED_FAMILY_FILES["L"] = res_bad
    res.append(expect("reserved file with a row dated 2025-08-01", lambda: s62.load_family("L", ["lapse_rate_t2_t850"]), True))
    s62.CANDIDATE_FEATURES["L"] = dict(saved_cf, v16_file=leak, sealed_file=sealed); s62.RESERVED_FAMILY_FILES["L"] = res_ok
    out2 = {}
    res.append(expect("v16 family file carrying a reserved-year row (counted, not raised here)", lambda: out2.update(r=s62.load_family("L", ["lapse_rate_t2_t850"])), False))
    print(f"      -> reserved_hits returned: {out2['r'][1]} (run_confirm raises on any nonzero hit count, :668-671)")
finally:
    s62.CANDIDATE_FEATURES["L"] = saved_cf; s62.RESERVED_FAMILY_FILES.clear(); s62.RESERVED_FAMILY_FILES.update(saved_rf)
print("\nD. session63 assert_all_inside_reserved_year")
res.append(expect("dates 2024-08-01, 2025-07-31", lambda: s63.assert_all_inside_reserved_year("x", [date(2024,8,1), date(2025,7,31)]), False))
res.append(expect("date 2024-07-31", lambda: s63.assert_all_inside_reserved_year("x", [date(2024,7,31)]), True))
print(f"\nTOTAL: {sum(res)} as expected, {len(res) - sum(res)} not as expected")
````

**Raw output** (`/tmp/audit68b/dc6_output.txt`):

````
A. assert_reserved_year_excluded (session48), inclusive edges
  [OK ] train ends 2024-07-31, test 2025-08-01..2026-07-31                     -> did not raise
  [OK ] train ends 2024-08-01 (first reserved day)                             -> raised ValueError: t: training window 2021-03-24..2024-08-01 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- re
  [OK ] test starts 2025-07-31 (last reserved day)                             -> raised ValueError: t: test window 2025-07-31..2026-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusi
  [OK ] train wholly after reserved year 2025-08-01..2025-12-31                -> did not raise
  [OK ] train surrounds reserved year 2021..2026                               -> raised ValueError: t: training window 2021-03-24..2026-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- re
  [OK ] CONFIRMATION_FOLD itself (must raise: why run_confirm never calls it)  -> raised ValueError: c: test window 2024-08-01..2025-07-31 overlaps the reserved confirmation year 2024-08-01..2025-07-31 -- refusi
  [OK ] EXPERIMENT_FOLDS 2022-23                                               -> did not raise
  [OK ] EXPERIMENT_FOLDS 2023-24                                               -> did not raise
  [OK ] EXPERIMENT_FOLDS 2025-26                                               -> did not raise

B. session39 load_grib_features D48 self-guard (synthetic CSV)
  [OK ] in-window edges 2025-08-01 and 2026-07-31                              -> did not raise
  [OK ] row dated 2026-08-01 (one day after)                                   -> raised ValueError: D48 self-guard: after_window.csv contains a date outside the expected window [2025-08-01, 2026-07-31]: EGLC 20
  [OK ] row dated 2025-07-31 in the sealed file (one day before)               -> raised ValueError: D48 self-guard: before_window.csv contains a date outside the expected window [2025-08-01, 2026-07-31]: RNO 20
  [OK ] missing file                                                           -> raised FileNotFoundError: D48 self-guard: expected GRIB feature file not found: /tmp/audit68b/synth/nope.csv
This is expected as of sess
  [OK ] blank temperature value (must not become 0 or NaN)                     -> raised ValueError: could not convert string to float: ''
  [BAD] literal 'nan' temperature string (informative: parsed silently?)       -> did not raise
      -> loader returned for the 'nan' row: {datetime.date(2025, 9, 1): {'fc': nan, 'cloud': 2.0, 'wind': 3.0}}

C. session62 load_family: out-of-range row in a reserved-year family file (synthetic)
  [OK ] reserved file with rows on 2024-08-01 and 2025-07-31                   -> did not raise
      -> rows loaded EGLC: [datetime.date(2022, 1, 1), datetime.date(2024, 8, 1), datetime.date(2025, 7, 31), datetime.date(2025, 9, 1)], reserved hits in v16/sealed: 0
  [OK ] reserved file with a row dated 2025-08-01                              -> raised AssertionError: session63 reserved-year file fam_res_bad.csv contains an out-of-range date 2025-08-01 for station EGLC -- refu
  [OK ] v16 family file carrying a reserved-year row (counted, not raised here) -> did not raise
      -> reserved_hits returned: 1 (run_confirm raises on any nonzero hit count, :668-671)

D. session63 assert_all_inside_reserved_year
    x: all 2 dates confirmed INSIDE 2024-08-01..2025-07-31 -- PASS
  [OK ] dates 2024-08-01, 2025-07-31                                           -> did not raise
  [OK ] date 2024-07-31                                                        -> raised AssertionError: x: 1 date(s) OUTSIDE the reserved 2024-08-01..2025-07-31 year found: [datetime.date(2024, 7, 31)]

TOTAL: 19 as expected, 1 not as expected
````

### 6.7 `dc7_nan_scan.py` — items 10, 22: non-finite values in inputs

````python
#!/usr/bin/env python3
"""68b items 10, 22: scan for values float() would accept silently as a gap
('nan', 'inf') in every column the headline models read, all windows, and
list the non-numeric tmpc tokens in every IEM routine chunk. Feature and raw
observation fields are only classified as numeric / non-numeric; nothing is
paired, compared or scored."""
import csv, glob, math, os
from collections import Counter
C = "/tmp/audit68b/clone/"
cols = {"grib_features_v16_window.csv": ["temperature_grib_c","cloud_cover_grib_pct","wind_speed_grib_kmh"],
        "grib_features_sealed_window.csv": ["temperature_grib_c","cloud_cover_grib_pct","wind_speed_grib_kmh"]}
for p in glob.glob(C + "data/processed/session*_window_with_*.csv"):
    if "session57" in p: continue
    cols[os.path.basename(p)] = [c for c in ("lapse_rate_t2_t850","dewpoint_depression_t2m","pressure_tendency_3h_hpa","dswrf_2h_wm2") if c in open(p).readline()]
tot = 0
for fn, cs in sorted(cols.items()):
    bad = Counter()
    for r in csv.DictReader(open(C + "data/processed/" + fn)):
        for c in cs:
            s = r[c].strip()
            try:
                v = float(s)
                if math.isnan(v) or math.isinf(v): bad[(c, s)] += 1
            except ValueError:
                bad[(c, s)] += 1
    tot += sum(bad.values())
    print(f"{fn:48s} cols={cs}  non-finite or non-numeric: {dict(bad) or 0}")
print(f"TOTAL processed non-finite/non-numeric model-input values: {tot}")
print("\nIEM routine chunks: tmpc tokens that are not plain numbers, per station")
for st in ["EGLC","LFPG","DSM","YSDU","RNO"]:
    toks = Counter(); n = 0
    for p in sorted(glob.glob(f"{C}data/raw/iem_asos_{st}_20??-??-??_20??-??-??_routine.csv")):
        if "2026-07-01" in p or "2021-03-18" in p: continue
        for r in csv.DictReader(open(p)):
            n += 1
            s = (r.get("tmpc") or "").strip()
            try:
                v = float(s)
                if math.isnan(v) or math.isinf(v): toks[s] += 1
            except ValueError:
                toks[s] += 1
    print(f"  {st}: {n} rows; non-numeric/non-finite tokens: {dict(toks)}")
````

**Raw output** (`/tmp/audit68b/dc7_output.txt`):

````
grib_features_sealed_window.csv                  cols=['temperature_grib_c', 'cloud_cover_grib_pct', 'wind_speed_grib_kmh']  non-finite or non-numeric: 0
grib_features_v16_window.csv                     cols=['temperature_grib_c', 'cloud_cover_grib_pct', 'wind_speed_grib_kmh']  non-finite or non-numeric: 0
session49_sealed_window_with_upper_air.csv       cols=['lapse_rate_t2_t850']  non-finite or non-numeric: 0
session49_v16_window_with_upper_air.csv          cols=['lapse_rate_t2_t850']  non-finite or non-numeric: 0
session51_sealed_window_with_moisture.csv        cols=['dewpoint_depression_t2m']  non-finite or non-numeric: 0
session51_v16_window_with_moisture.csv           cols=['dewpoint_depression_t2m']  non-finite or non-numeric: 0
session53_sealed_window_with_pressure.csv        cols=['pressure_tendency_3h_hpa']  non-finite or non-numeric: 0
session53_v16_window_with_pressure.csv           cols=['pressure_tendency_3h_hpa']  non-finite or non-numeric: 0
session55_sealed_window_with_radiation.csv       cols=['dswrf_2h_wm2']  non-finite or non-numeric: 0
session55_v16_window_with_radiation.csv          cols=['dswrf_2h_wm2']  non-finite or non-numeric: 0
session63_reserved_window_with_moisture.csv      cols=['dewpoint_depression_t2m']  non-finite or non-numeric: 0
session63_reserved_window_with_pressure.csv      cols=['pressure_tendency_3h_hpa']  non-finite or non-numeric: 0
session63_reserved_window_with_radiation.csv     cols=['dswrf_2h_wm2']  non-finite or non-numeric: 0
session63_reserved_window_with_upper_air.csv     cols=['lapse_rate_t2_t850']  non-finite or non-numeric: 0
TOTAL processed non-finite/non-numeric model-input values: 0

IEM routine chunks: tmpc tokens that are not plain numbers, per station
  EGLC: 46919 rows; non-numeric/non-finite tokens: {'M': 10}
  LFPG: 46903 rows; non-numeric/non-finite tokens: {'M': 1}
  DSM: 46938 rows; non-numeric/non-finite tokens: {'M': 1}
  YSDU: 47234 rows; non-numeric/non-finite tokens: {'M': 2}
  RNO: 46836 rows; non-numeric/non-finite tokens: {'M': 1}
````

### 6.8 `dc8_copies.py` — items 12, 15, 17, 21: copied functions and LightGBM settings

````python
#!/usr/bin/env python3
"""68b items 12, 15, 17, 21: compare every function copied between headline
scripts (docstrings and comments removed; AST unparse), and the LightGBM
settings dict in all seven scoring scripts. Source reading only."""
import ast, difflib
from pathlib import Path
S = Path("/tmp/audit68b/clone/scripts")
def tree(f): return ast.parse((S / f).read_text())
def strip_doc(fn):
    fn = ast.parse(ast.unparse(fn)).body[0]
    for node in ast.walk(fn):
        b = getattr(node, "body", None)
        if isinstance(b, list) and b and isinstance(b[0], ast.Expr) and isinstance(b[0].value, ast.Constant) and isinstance(b[0].value.value, str):
            node.body = b[1:] or [ast.Pass()]
    return ast.unparse(fn)
def func(f, name):
    for n in tree(f).body:
        if isinstance(n, ast.FunctionDef) and n.name == name: return strip_doc(n)
def const(f, name):
    for n in tree(f).body:
        if isinstance(n, ast.Assign) and isinstance(n.targets[0], ast.Name) and n.targets[0].id == name:
            return ast.literal_eval(n.value) if not isinstance(n.value, ast.Call) else {k.arg: ast.literal_eval(k.value) for k in n.value.keywords}
def group(label, pairs, rename=None):
    srcs = {f"{f}:{n}": func(f, n) for f, n in pairs}
    ref_k, ref = next(iter(srcs.items()))
    if rename: srcs = {k: (v.replace(rename[0], rename[1]) if v else v) for k, v in srcs.items()}; ref = srcs[ref_k]
    same = [k for k, v in srcs.items() if v == ref]; diff = [k for k, v in srcs.items() if v != ref]
    print(f"\n== {label}: {len(same)} identical to {ref_k}" + (f"; DIFFERENT: {diff}" if diff else ""))
    for k in diff:
        v = srcs[k]
        if v is None: print(f"   {k}: MISSING"); continue
        for l in [l for l in difflib.unified_diff(ref.splitlines(), v.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))][:40]:
            print("     " + l)
GRIB = ["session37_grib_pull.py", "session37_decode.py", "session37_elevation_fix.py", "session40_grib_pull.py", "session40_decode.py",
        "session49_upper_air_pull.py", "session51_moisture_pull.py", "session53_pressure_pull.py", "session55_radiation_pull.py"]
group("cycle_and_lead", [(f, "cycle_and_lead") for f in GRIB])
group("grib_base_url", [(f, "grib_base_url") for f in ["session37_grib_pull.py", "session40_grib_pull.py", "session49_upper_air_pull.py", "session51_moisture_pull.py", "session53_pressure_pull.py", "session55_radiation_pull.py"]])
group("find_message_range", [(f, "find_message_range") for f in ["session37_grib_pull.py", "session40_grib_pull.py", "session49_upper_air_pull.py", "session51_moisture_pull.py", "session53_pressure_pull.py"]])
group("process_combo (B pulls)", [(f, "process_combo") for f in ["session37_grib_pull.py", "session40_grib_pull.py"]])
group("build_combos (B pulls)", [(f, "build_combos") for f in ["session37_grib_pull.py", "session40_grib_pull.py"]])
group("bilinear_value (B decode + elevation fix)", [(f, "bilinear_value") for f in ["session37_decode.py", "session40_decode.py", "session37_elevation_fix.py"]])
group("bilinear_from_gid (families)", [(f, "bilinear_from_gid") for f in ["session49_upper_air_pull.py", "session51_moisture_pull.py", "session53_pressure_pull.py", "session55_radiation_pull.py"]])
group("decode_row", [(f, "decode_row") for f in ["session37_decode.py", "session40_decode.py"]])
group("grib_files_for", [(f, "grib_files_for") for f in ["session37_decode.py", "session40_decode.py"]])
group("load_elevation_corrections", [(f, "load_elevation_corrections") for f in ["session37_decode.py", "session40_decode.py", "session49_upper_air_pull.py", "session51_moisture_pull.py"]])
group("build_combos (families L, D, T)", [(f, "build_combos") for f in ["session49_upper_air_pull.py", "session51_moisture_pull.py", "session53_pressure_pull.py"]])
group("year_fraction", [(f, "year_fraction") for f in ["session07_test.py", "session13_test.py", "session18_test.py", "session24_test.py", "session29_test.py", "session39_sealed_test.py", "session62_reserved_confirm.py", "session05_model.py"]])
group("mae", [(f, "mae") for f in ["session18_test.py", "session39_sealed_test.py", "session62_reserved_confirm.py"]])
group("load_obs_all (F94 vs F109)", [(f, "load_obs_all") for f in ["session39_sealed_test.py", "session62_reserved_confirm.py"]])
group("all_days", [(f, "all_days") for f in ["session18_test.py", "session39_sealed_test.py"]])
# the bilinear arithmetic core: compare the part of bilinear_value after decoding with bilinear_from_gid
b37 = func("session37_decode.py", "bilinear_value"); b49 = func("session49_upper_air_pull.py", "bilinear_from_gid")
core = lambda s: s[s.index("lats = sorted"):]
c37 = core(b37).replace("return (best.value, valid_date, valid_time)", "X").replace("best = min(neighbours, key=lambda n: n.distance)\n            X", "return min(neighbours, key=lambda n: n.distance).value")
c37 = c37.replace("value = (1 - dlat)", "return (1 - dlat)").replace("\n    return (value, valid_date, valid_time)", "")
print("\n== bilinear arithmetic core, s37 decode vs s49 family (after normalising the return statements):", "identical" if c37 == core(b49) else "DIFFERENT")
if c37 != core(b49):
    for l in difflib.unified_diff(c37.splitlines(), core(b49).splitlines(), lineterm="", n=0): print("     " + l)
print("\n== LightGBM settings (LGB_PARAMS) in the seven scoring scripts, against D21.4/D48.6")
D21_4 = dict(objective="regression_l1", n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0,
             colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1, deterministic=True, force_row_wise=True, verbose=-1)
for f in ["session07_test.py", "session13_test.py", "session18_test.py", "session24_test.py", "session29_test.py", "session39_sealed_test.py", "session62_reserved_confirm.py"]:
    p = const(f, "LGB_PARAMS")
    print(f"   {f:32s} equal to D21.4/D48.6: {p == D21_4}   keys={len(p)}")
# LGBMRegressor calls: are they all given exactly **LGB_PARAMS?
print("\n== every LGBMRegressor(...) call on the headline scoring paths")
for f in ["session07_test.py", "session13_test.py", "session18_test.py", "session24_test.py", "session29_test.py", "session39_sealed_test.py", "session62_reserved_confirm.py"]:
    calls = [ast.unparse(n) for n in ast.walk(tree(f)) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("LGBMRegressor")]
    fits = [ast.unparse(n) for n in ast.walk(tree(f)) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith(".fit")]
    print(f"   {f:32s} {calls}  fit calls: {fits}")
# session63 pull loops vs the family main loops
def loop_of(f, fname):
    for n in tree(f).body:
        if isinstance(n, ast.FunctionDef) and n.name == fname:
            for x in ast.walk(n):
                if isinstance(x, ast.For) and "as_completed" in ast.unparse(x.iter):
                    return ast.unparse(ast.parse(ast.unparse(x)))
print("\n== session63 pull_* result-handling loop vs the family's own main() loop (module prefixes removed)")
for fam, (src, fn) in {"L": ("session49_upper_air_pull.py", "pull_L"), "D": ("session51_moisture_pull.py", "pull_D"), "T": ("session53_pressure_pull.py", "pull_T"), "R": ("session55_radiation_pull.py", "pull_R")}.items():
    a = loop_of(src, "main"); b = loop_of("session63_reserved_year_build.py", fn)
    if b: b = b.replace("s49.", "").replace("s51.", "").replace("s53.", "").replace("s55.", "")
    if a is None or b is None:
        print(f"   {fam}: loop not found (main={a is not None}, s63={b is not None})"); continue
    d = [l for l in difflib.unified_diff(a.splitlines(), b.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
    print(f"   {fam}: {'identical' if not d else f'{len(d)} differing lines'}")
    for l in d[:30]: print("     " + l)
````

**Raw output** (`/tmp/audit68b/dc8_output.txt`):

````

== cycle_and_lead: 9 identical to session37_grib_pull.py:cycle_and_lead

== grib_base_url: 6 identical to session37_grib_pull.py:grib_base_url

== find_message_range: 5 identical to session37_grib_pull.py:find_message_range

== process_combo (B pulls): 1 identical to session37_grib_pull.py:process_combo; DIFFERENT: ['session40_grib_pull.py:process_combo']
     -            out_meta.write_text(f'source: {grib_url_}\nidx source: {idx_url}\nbyte range requested: {byte_range}\nvariable: {var_code}:{level}, forecast hour f{lead:03d}, cycle {cycle:02d}z, run date {run_date.isoformat()}\nused by airports (target hour, cycle+lead convention): {stations_str}\npulled (UTC): {pull_time}\nbytes saved: {len(content)}\nfirst 4 bytes: {content[:4]!r}  last 4 bytes: {content[-4:]!r}\n')
     +            out_meta.write_text(f'source: {grib_url_}\nidx source: {idx_url}\nbyte range requested: {byte_range}\nvariable: {var_code}:{level}, forecast hour f{lead:03d}, cycle {cycle:02d}z, run date {run_date.isoformat()}\nused by airports (target hour, cycle+lead convention): {stations_str}\npulled (UTC): {pull_time}\nbytes saved: {len(content)}\nfirst 4 bytes: {content[:4]!r}  last 4 bytes: {content[-4:]!r}\nsealed test year pull (session 40, D48.8) -- SPEC 4.3\n')

== build_combos (B pulls): 2 identical to session37_grib_pull.py:build_combos

== bilinear_value (B decode + elevation fix): 2 identical to session37_decode.py:bilinear_value; DIFFERENT: ['session37_elevation_fix.py:bilinear_value']
     -        valid_date = ec.codes_get(gid, 'validityDate')
     -        valid_time = ec.codes_get(gid, 'validityTime')
     -            return (best.value, valid_date, valid_time)
     +            return best.value
     -    value = (1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01 + dlat * (1 - dlon) * v10 + dlat * dlon * v11
     -    return (value, valid_date, valid_time)
     +    return (1 - dlat) * (1 - dlon) * v00 + (1 - dlat) * dlon * v01 + dlat * (1 - dlon) * v10 + dlat * dlon * v11

== bilinear_from_gid (families): 4 identical to session49_upper_air_pull.py:bilinear_from_gid

== decode_row: 2 identical to session37_decode.py:decode_row

== grib_files_for: 2 identical to session37_decode.py:grib_files_for

== load_elevation_corrections: 2 identical to session37_decode.py:load_elevation_corrections; DIFFERENT: ['session49_upper_air_pull.py:load_elevation_corrections', 'session51_moisture_pull.py:load_elevation_corrections']
     -    path = DIAG37 / 'session37_elevation_correction_params.csv'
     -    with open(path) as f:
     +    with open(ELEV_CORR_CSV) as f:
     -    path = DIAG37 / 'session37_elevation_correction_params.csv'
     -    with open(path) as f:
     +    with open(ELEV_CORR_CSV) as f:

== build_combos (families L, D, T): 3 identical to session49_upper_air_pull.py:build_combos

== year_fraction: 8 identical to session07_test.py:year_fraction

== mae: 2 identical to session18_test.py:mae; DIFFERENT: ['session62_reserved_confirm.py:mae']
     -    return float(np.mean(np.abs(np.asarray(errors, dtype=float))))
     +    return float(np.mean(np.abs(np.asarray(errors, dtype=float)))) if errors else float('nan')

== load_obs_all (F94 vs F109): 1 identical to session39_sealed_test.py:load_obs_all; DIFFERENT: ['session62_reserved_confirm.py:load_obs_all']
     -                if dt < TRAIN_START or dt > SEALED_UNTIL:
     -                    continue

== all_days: 2 identical to session18_test.py:all_days

== bilinear arithmetic core, s37 decode vs s49 family (after normalising the return statements): DIFFERENT
     --- 
     +++ 
     @@ -9 +9 @@
     -        raise ValueError(f'unexpected neighbour layout for {path}: {[(n.lat, n.lon) for n in neighbours]}')
     +        raise ValueError(f'unexpected neighbour layout: {[(n.lat, n.lon) for n in neighbours]}')

== LightGBM settings (LGB_PARAMS) in the seven scoring scripts, against D21.4/D48.6
   session07_test.py                equal to D21.4/D48.6: True   keys=14
   session13_test.py                equal to D21.4/D48.6: True   keys=14
   session18_test.py                equal to D21.4/D48.6: True   keys=14
   session24_test.py                equal to D21.4/D48.6: True   keys=14
   session29_test.py                equal to D21.4/D48.6: True   keys=14
   session39_sealed_test.py         equal to D21.4/D48.6: True   keys=14
   session62_reserved_confirm.py    equal to D21.4/D48.6: True   keys=14

== every LGBMRegressor(...) call on the headline scoring paths
   session07_test.py                ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['model.fit(x_tr, y_tr)']
   session13_test.py                ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['model.fit(x_tr, y_tr)']
   session18_test.py                ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['model.fit(x_tr, y_tr)']
   session24_test.py                ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['model.fit(x_tr, y_tr)']
   session29_test.py                ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['model.fit(x_tr, y_tr)']
   session39_sealed_test.py         ['lgb.LGBMRegressor(**LGB_PARAMS)', 'lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['m3.fit(x3_tr, y_tr)', 'm5.fit(x5_tr, y_tr)']
   session62_reserved_confirm.py    ['lgb.LGBMRegressor(**LGB_PARAMS)']  fit calls: ['m.fit(x_tr, y_tr)']

== session63 pull_* result-handling loop vs the family's own main() loop (module prefixes removed)
   L: 6 differing lines
     -    n_done += 1
     -    if n_done % 500 == 0 or n_done == n_combos:
     -        elapsed = time.time() - t0
     -        rate = n_done / elapsed if elapsed > 0 else 0
     -        eta = (n_combos - n_done) / rate if rate > 0 else float('inf')
     -        print(f'  {n_done}/{n_combos} combos  elapsed={elapsed / 60:.1f}min  rate={rate:.2f}/s  eta={eta / 60:.1f}min', flush=True)
   D: 6 differing lines
     -    n_done += 1
     -    if n_done % 500 == 0 or n_done == n_combos:
     -        elapsed = time.time() - t0
     -        rate = n_done / elapsed if elapsed > 0 else 0
     -        eta = (n_combos - n_done) / rate if rate > 0 else float('inf')
     -        print(f'  {n_done}/{n_combos} combos  elapsed={elapsed / 60:.1f}min  rate={rate:.2f}/s  eta={eta / 60:.1f}min', flush=True)
   T: 6 differing lines
     -    n_done += 1
     -    if n_done % 500 == 0 or n_done == n_combos:
     -        elapsed = time.time() - t0
     -        rate = n_done / elapsed if elapsed > 0 else 0
     -        eta = (n_combos - n_done) / rate if rate > 0 else float('inf')
     -        print(f'  {n_done}/{n_combos} combos  elapsed={elapsed / 60:.1f}min  rate={rate:.2f}/s  eta={eta / 60:.1f}min', flush=True)
   R: 6 differing lines
     -    n_done += 1
     -    if n_done % 500 == 0 or n_done == n_combos:
     -        elapsed = time.time() - t0
     -        rate = n_done / elapsed if elapsed > 0 else 0
     -        eta = (n_combos - n_done) / rate if rate > 0 else float('inf')
     -        print(f'  {n_done}/{n_combos} combos  elapsed={elapsed / 60:.1f}min  rate={rate:.2f}/s  eta={eta / 60:.1f}min', flush=True)
````

### 6.9 `dc9_feature_order.py` — items 18, 22: F109 feature order and A67-14 (run from the clone)

````python
#!/usr/bin/env python3
"""68b items 18, 22 (A67-14): the F109 path's feature list and order, and
whether any row reaching make_feature_vector() can carry a missing final-set
key. Uses the committed session62 loaders (load_family, load_base_unfiltered,
build_complete_case). Reads feature columns only: no observation is loaded,
no model is fit, nothing is scored. run_confirm() and preflight() are NOT
called."""
import math, sys
from datetime import date
sys.path.insert(0, "/tmp/audit68b/clone/scripts")
import session62_reserved_confirm as s62
print("BASE_KEYS         :", s62.BASE_KEYS)
print("FINAL_FEATURE_KEYS:", s62.FINAL_FEATURE_KEYS)
print("keys via fit_and_score's own codes path (sorted codes):", s62.BASE_KEYS + sum((s62.FAMILY_KEYS[c] for c in sorted(s62.FINAL_CODES)), []))
# column order: one synthetic row with distinct marker values
row = {"date": date(2022, 3, 21), "fc": 101.0, "cloud": 102.0, "wind": 103.0, "lapse_rate_t2_t850": 104.0,
       "dewpoint_depression_t2m_floored": 105.0, "pressure_tendency_3h_hpa": 106.0, "dswrf_2h_wm2": 107.0,
       "obs": -999.0, "resid": -888.0, "station": "EGLC"}
x = s62.features_matrix([row], s62.FINAL_FEATURE_KEYS)
print("synthetic row -> matrix row:", [round(v, 4) for v in x[0]], " shape", x.shape)
print("   (obs, resid, date and station markers -999/-888 absent from the matrix:", -999.0 not in x and -888.0 not in x, ")")
xb = s62.features_matrix([row], s62.BASE_KEYS)
print("B-only row -> ", [round(v, 4) for v in xb[0]], " shape", xb.shape)
# A67-14: a row missing a final-set key
bad = dict(row); del bad["dswrf_2h_wm2"]
print("row missing dswrf_2h_wm2 -> ", s62.features_matrix([bad], s62.FINAL_FEATURE_KEYS)[0].tolist(), "(silently NaN: this is A67-14's concern)")
# real rows: every row build_complete_case produces, all windows
l_all, hl = s62.load_family("L", ["lapse_rate_t2_t850"]); d_all, hd = s62.load_family("D", ["dewpoint_depression_t2m"])
t_all, ht = s62.load_family("T", ["pressure_tendency_3h_hpa"]); r_all, hr = s62.load_family("R", ["dswrf_2h_wm2"])
base = s62.load_base_unfiltered()
merged = s62.build_complete_case(base, l_all, d_all, t_all, r_all)
fold = s62.CONFIRMATION_FOLD
print(f"\nreserved-year hits in v16/sealed family files: L={hl} D={hd} T={ht} R={hr}")
print(f"{'st':5s} {'B rows':>7s} {'merged':>7s} {'train win':>9s} {'reserved':>8s} {'sealed':>7s} {'rows with missing/NaN final key':>32s}")
for st in s62.AIRPORTS:
    m = merged[st]
    tr = sum(fold["train_start"] <= d <= fold["train_end"] for d in m)
    te = sum(fold["test_start"] <= d <= fold["test_end"] for d in m)
    se = sum(d >= date(2025, 8, 1) for d in m)
    miss = sum(1 for r in m.values() for k in s62.FINAL_FEATURE_KEYS[3:]
               if (k not in ("cloud_cover", "wind_speed_10m") and (r.get(k) is None or math.isnan(r.get(k)))))
    b_in_fold = sum(fold["train_start"] <= d <= fold["test_end"] for d in base[st])
    b_fold_not_merged = sum(1 for d in base[st] if fold["train_start"] <= d <= fold["test_end"] and d not in m)
    print(f"{st:5s} {len(base[st]):7d} {len(m):7d} {tr:9d} {te:8d} {se:7d} {miss:32d}   B days in fold not in complete-case set: {b_fold_not_merged}")
````

**Raw output** (`/tmp/audit68b/dc9_output.txt`):

````
BASE_KEYS         : ['temp', 'season_sin', 'season_cos', 'cloud_cover', 'wind_speed_10m']
FINAL_FEATURE_KEYS: ['temp', 'season_sin', 'season_cos', 'cloud_cover', 'wind_speed_10m', 'dewpoint_depression_t2m_floored', 'lapse_rate_t2_t850', 'dswrf_2h_wm2', 'pressure_tendency_3h_hpa']
keys via fit_and_score's own codes path (sorted codes): ['temp', 'season_sin', 'season_cos', 'cloud_cover', 'wind_speed_10m', 'dewpoint_depression_t2m_floored', 'lapse_rate_t2_t850', 'dswrf_2h_wm2', 'pressure_tendency_3h_hpa']
synthetic row -> matrix row: [np.float64(101.0), np.float64(0.9778), np.float64(0.2093), np.float64(102.0), np.float64(103.0), np.float64(105.0), np.float64(104.0), np.float64(107.0), np.float64(106.0)]  shape (1, 9)
   (obs, resid, date and station markers -999/-888 absent from the matrix: True )
B-only row ->  [np.float64(101.0), np.float64(0.9778), np.float64(0.2093), np.float64(102.0), np.float64(103.0)]  shape (1, 5)
row missing dswrf_2h_wm2 ->  [101.0, 0.9778483415056568, 0.2093146459630487, 102.0, 103.0, 105.0, 104.0, nan, 106.0] (silently NaN: this is A67-14's concern)

reserved-year hits in v16/sealed family files: L=0 D=0 T=0 R=0
st     B rows  merged train win reserved  sealed  rows with missing/NaN final key
EGLC     1956    1956      1226      365     365                                0   B days in fold not in complete-case set: 0
LFPG     1956    1956      1226      365     365                                0   B days in fold not in complete-case set: 0
DSM      1955    1955      1225      365     365                                0   B days in fold not in complete-case set: 0
YSDU     1955    1955      1225      365     365                                0   B days in fold not in complete-case set: 0
RNO      1955    1955      1225      365     365                                0   B days in fold not in complete-case set: 0
````

### 6.10 `bound_item6.py` — items 6, 19: bound and averages from recorded figures only

````python
#!/usr/bin/env python3
"""68b item 6: an upper bound on the model's MAE over the persistence day
set, computed ONLY from figures already on record in F109 (n_test, no_prev,
B+D,L,R,T MAE, persistence MAE). No data row is read. Because every absolute
error is >= 0, dropping k of n days can raise a mean by at most n/(n-k)."""
F109 = {"EGLC": (364, 1, 1.0008, 2.2259), "LFPG": (365, 0, 1.2369, 2.5233), "DSM": (365, 0, 1.4123, 4.1081),
        "YSDU": (360, 5, 1.2643, 2.5775), "RNO": (365, 0, 1.2742, 2.7563)}
for st, (n, k, m, p) in F109.items():
    bound = m * n / (n - k)
    print(f"{st:5s} n={n} no_prev={k}  recorded B+DLRT MAE {m:.4f}  bound on the persistence day set <= {bound:.4f}  "
          f"recorded persistence MAE {p:.4f}  verdict vs persistence cannot change: {bound < p}")
avg = sum(v[2] for v in F109.values()) / 5
print(f"mean of the five recorded B+D,L,R,T MAEs = {avg:.5f} (record: 1.2377); mean of B MAEs = {(1.0861+1.3285+1.4402+1.3030+1.4272)/5:.5f} (record: 1.3170)")
````

**Raw output** (`/tmp/audit68b/bound_item6_output.txt`):

````
EGLC  n=364 no_prev=1  recorded B+DLRT MAE 1.0008  bound on the persistence day set <= 1.0036  recorded persistence MAE 2.2259  verdict vs persistence cannot change: True
LFPG  n=365 no_prev=0  recorded B+DLRT MAE 1.2369  bound on the persistence day set <= 1.2369  recorded persistence MAE 2.5233  verdict vs persistence cannot change: True
DSM   n=365 no_prev=0  recorded B+DLRT MAE 1.4123  bound on the persistence day set <= 1.4123  recorded persistence MAE 4.1081  verdict vs persistence cannot change: True
YSDU  n=360 no_prev=5  recorded B+DLRT MAE 1.2643  bound on the persistence day set <= 1.2821  recorded persistence MAE 2.5775  verdict vs persistence cannot change: True
RNO   n=365 no_prev=0  recorded B+DLRT MAE 1.2742  bound on the persistence day set <= 1.2742  recorded persistence MAE 2.7563  verdict vs persistence cannot change: True
mean of the five recorded B+D,L,R,T MAEs = 1.23770 (record: 1.2377); mean of B MAEs = 1.31700 (record: 1.3170)
````

### 6.11 `diff_minimal.py` — item 20: the five minimal-method scripts

````python
#!/usr/bin/env python3
"""68b item 20: compare the five minimal-method test scripts function by
function, with docstrings and print/sub/line calls removed. Read-only."""
import ast, difflib, sys
ROOT = "/Users/zacharyadams/Coding Projects/MLwx/scripts/"
FILES = ["session07_test.py", "session13_test.py", "session18_test.py",
         "session24_test.py", "session29_test.py"]
PRINTISH = {"print", "sub", "line", "describe"}

class Strip(ast.NodeTransformer):
    def _body(self, body):
        out = []
        for s in body:
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str):
                continue
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Call) and isinstance(s.value.func, ast.Name) and s.value.func.id in PRINTISH:
                continue
            out.append(self.visit(s))
        return out or [ast.Pass()]
    def generic_visit(self, node):
        for field in ("body", "orelse", "finalbody"):
            if hasattr(node, field) and isinstance(getattr(node, field), list) and getattr(node, field) and isinstance(getattr(node, field)[0], ast.stmt):
                setattr(node, field, self._body(getattr(node, field)))
        return super().generic_visit(node)

def funcs(path):
    tree = ast.parse(open(ROOT + path).read())
    out, consts = {}, {}
    for n in tree.body:
        if isinstance(n, ast.FunctionDef):
            n2 = Strip().visit(ast.parse(ast.unparse(n)).body[0])
            out[n.name] = ast.unparse(n2)
        elif isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
            consts[n.targets[0].id] = ast.unparse(n.value)
    return out, consts

data = {f: funcs(f) for f in FILES}
ref = "session18_test.py"
# functions implementing the method
CORE = [("load_forecast_12z", "load_forecast_target_hour"), ("load_obs_12z", "load_obs_target_hour"),
        ("all_days",), ("year_fraction",), ("features",), ("mae",), ("join",),
        ("climatology_from_training",), ("fit_on_training",), ("score_test_year",), ("judge_the_bar",), ("main",)]
def get(f, names):
    for n in names:
        if n in data[f][0]:
            return n, data[f][0][n]
    return None, None
for names in CORE:
    rn, rsrc = get(ref, names)
    print(f"=== {'/'.join(names)} (reference {ref}:{rn})")
    for f in FILES:
        if f == ref: continue
        n, src = get(f, names)
        if src is None:
            print(f"  {f}: MISSING"); continue
        s1 = rsrc.replace("load_forecast_12z", "load_forecast_target_hour").replace("load_obs_12z", "load_obs_target_hour")
        s2 = src.replace("load_forecast_12z", "load_forecast_target_hour").replace("load_obs_12z", "load_obs_target_hour")
        if s1 == s2:
            print(f"  {f}: identical"); continue
        d = [l for l in difflib.unified_diff(s1.splitlines(), s2.splitlines(), lineterm="", n=0) if not l.startswith(("---", "+++", "@@"))]
        print(f"  {f}: {len(d)} differing lines")
        for l in d[:60]: print("     " + l)
print("\n=== method constants")
KEYS = ["STATION", "TARGET_HOUR", "TRAIN_START", "TRAIN_END", "TEST_START", "TEST_END", "HARD_END", "CHUNKS", "LGB_PARAMS", "CLIM_HALF_WINDOW_DAYS", "FEATURE_NAMES"]
for k in KEYS:
    vals = {f: data[f][1].get(k, "(absent)") for f in FILES}
    print(f"{k}:")
    for f, v in vals.items(): print(f"   {f}: {v.replace(chr(10),' ')[:200]}")
````

**Raw output** (`/tmp/audit68b/diff_minimal_output.txt`):

````
=== load_forecast_12z/load_forecast_target_hour (reference session18_test.py:load_forecast_target_hour)
  session07_test.py: 2 differing lines
     -        path = RAW / f'openmeteo_previousruns_gfs_global_{STATION}_{start}_{end}.json'
     +        path = RAW / f'openmeteo_previousruns_gfs_global_EGLC_{start}_{end}.json'
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== load_obs_12z/load_obs_target_hour (reference session18_test.py:load_obs_target_hour)
  session07_test.py: 13 differing lines
     -    reports_at_target = 0
     +    reports_at_12 = 0
     -    near_target = {}
     -        path = RAW / f'iem_asos_{STATION}_{start}_{end}_routine.csv'
     +        path = RAW / f'iem_asos_EGLC_{start}_{end}_routine.csv'
     -                reports_at_target += 1
     +                reports_at_12 += 1
     -                off = int((t - nearest).total_seconds() // 60)
     -                raw = (r.get('tmpc') or '').strip()
     -                near_target.setdefault(nearest.date(), []).append((off, raw if raw not in ('M', '', 'T', 'None') else None))
     +                raw = (r.get('tmpc') or '').strip()
     -    return (series, reports_at_target, reports_after_end, no_temp, outside_15min, near_target)
     +    return (series, reports_at_12, reports_after_end, no_temp, outside_15min)
  session13_test.py: 18 differing lines
     -    reports_at_target = 0
     +    reports_at_12 = 0
     -    near_target = {}
     +    near_noon = {}
     +                raw = (r.get('tmpc') or '').strip()
     +                has_temp = raw not in ('M', '', 'T', 'None')
     +                if t.hour in (11, TARGET_HOUR) and t.date() <= HARD_END:
     +                    noon = t.replace(hour=TARGET_HOUR, minute=0)
     +                    near_noon.setdefault(t.date(), []).append((int((t - noon).total_seconds() // 60), raw if has_temp else None))
     -                reports_at_target += 1
     +                reports_at_12 += 1
     -                off = int((t - nearest).total_seconds() // 60)
     -                raw = (r.get('tmpc') or '').strip()
     -                near_target.setdefault(nearest.date(), []).append((off, raw if raw not in ('M', '', 'T', 'None') else None))
     -                if raw in ('M', '', 'T', 'None'):
     +                if not has_temp:
     -    return (series, reports_at_target, reports_after_end, no_temp, outside_15min, near_target)
     +    return (series, reports_at_12, reports_after_end, no_temp, outside_15min, near_noon)
  session24_test.py: identical
  session29_test.py: identical
=== all_days (reference session18_test.py:all_days)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== year_fraction (reference session18_test.py:year_fraction)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== features (reference session18_test.py:features)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== mae (reference session18_test.py:mae)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== join (reference session18_test.py:join)
  session07_test.py: 51 differing lines
     -    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_target = load_obs_target_hour()
     +    obs, ob_rows, ob_after, ob_no_temp, ob_far = load_obs_target_hour()
     -    offsets = {}
     -    test_offsets = {}
     -    for d, recs in near_target.items():
     -        if d not in obs:
     -            continue
     -        best = min((r for r in recs if abs(r[0]) <= 15 and r[1] is not None), key=lambda r: abs(r[0]))
     -        offsets[best[0]] = offsets.get(best[0], 0) + 1
     -        if TEST_START <= d <= TEST_END:
     -            test_offsets[best[0]] = test_offsets.get(best[0], 0) + 1
     -    for off in sorted(offsets):
     -        pass
     -    ambiguous = sum((1 for recs in near_target.values() if len([r for r in recs if abs(r[0]) <= 15 and r[1] is not None]) > 1))
     -    ok_train = len(train) == EXPECT_TRAIN_ROWS and len(inner) == EXPECT_INNER_ROWS and (len(valid) == EXPECT_VALID_ROWS)
     -    gap_days = all_days(GAP_START, GAP_END)
     +    ok = len(train) == 1569 and len(inner) == 1205 and (len(valid) == 364)
     +    assert ok, 'training-window row counts do not match F12 - STOP (D21.11)'
     +    gap_days = [d for d in all_days(GAP_START, GAP_END)]
     -    t_days = all_days(TEST_START, TEST_END)
     -    t_dropped = [d for d in t_days if d not in t_kept]
     +    t_dropped = [d for d in all_days(TEST_START, TEST_END) if d not in t_kept]
     -    cause_fcgap = []
     -    cause_offhour = []
     -    cause_noreport = []
     -    cause_notemp = []
     -        no_fc = d not in fc or fc[d] is None
     -        reports = sorted(near_target.get(d, []), key=lambda x: x[0])
     -        within15 = [x for x in reports if abs(x[0]) <= 15]
     -        if no_fc:
     -            cause_fcgap.append(d)
     -        elif within15:
     -            cause_notemp.append(d)
     -        elif reports:
     -            cause_offhour.append(d)
     -        else:
     -            cause_noreport.append(d)
     -        for off, temp in reports:
     -            if abs(off) <= 15:
     -                verdict = f'would pair with {TARGET_HOUR}:00 under D14'
     -            else:
     -                verdict = 'nearest the target hour but >15 min out - dropped'
     -        if not reports:
     -            pass
     -    checks = [('forecast-gap days in the test year (F38)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F41)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 18:00 hour (F41)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature (F41)', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected', EXPECT_TEST_PAIRED_ROWS, len(test))]
     -    ok_test = True
     -    for label, want, got in checks:
     -        good = want == got
     -        ok_test = ok_test and good
     -    return (train, test, obs, ok_train and ok_test)
     +    return (train, test, obs)
  session13_test.py: 33 differing lines
     -    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_target = load_obs_target_hour()
     +    obs, ob_rows, ob_after, ob_no_temp, ob_far, near_noon = load_obs_target_hour()
     -    offsets = {}
     -    test_offsets = {}
     -    for d, recs in near_target.items():
     -        if d not in obs:
     -            continue
     -        best = min((r for r in recs if abs(r[0]) <= 15 and r[1] is not None), key=lambda r: abs(r[0]))
     -        offsets[best[0]] = offsets.get(best[0], 0) + 1
     -        if TEST_START <= d <= TEST_END:
     -            test_offsets[best[0]] = test_offsets.get(best[0], 0) + 1
     -    for off in sorted(offsets):
     -        pass
     -    ambiguous = sum((1 for recs in near_target.values() if len([r for r in recs if abs(r[0]) <= 15 and r[1] is not None]) > 1))
     -        reports = sorted(near_target.get(d, []), key=lambda x: x[0])
     -        within15 = [x for x in reports if abs(x[0]) <= 15]
     +        reports = sorted(near_noon.get(d, []), key=lambda x: x[0])
     +        relevant = [x for x in reports if -30 <= x[0] <= 59]
     +        within15 = [x for x in relevant if abs(x[0]) <= 15]
     -        elif reports:
     +        elif relevant:
     -                verdict = f'would pair with {TARGET_HOUR}:00 under D14'
     +                verdict = 'would pair with 12:00 under D14'
     +            elif -30 <= off <= 59:
     +                verdict = 'in the noon hour but >15 min out - dropped by D14'
     -                verdict = 'nearest the target hour but >15 min out - dropped'
     -        if not reports:
     +                verdict = 'belongs to the 11:00 hour, not the noon hour'
     +        if not relevant:
     -    checks = [('forecast-gap days in the test year (F38)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F41)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 18:00 hour (F41)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature (F41)', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected', EXPECT_TEST_PAIRED_ROWS, len(test))]
     +    checks = [('forecast-gap days in the test year (F22)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F25)', len(EXPECT_TEST_OFFHOUR_DAYS), len(cause_offhour)), ('days lost to no report at all in the noon hour (F25)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report on the hour with no temp (F25)', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected', EXPECT_TEST_PAIRED_ROWS, len(test))]
     +    named_ok = sorted(cause_offhour) == EXPECT_TEST_OFFHOUR_DAYS
     +    ok_test = ok_test and named_ok
  session24_test.py: 4 differing lines
     -    if not t_dropped:
     -        pass
     -    checks = [('forecast-gap days in the test year (F38)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F41)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 18:00 hour (F41)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature (F41)', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected', EXPECT_TEST_PAIRED_ROWS, len(test))]
     +    checks = [('forecast-gap days in the test year (F57, F59)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F59)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 02:00 hour (F59)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected (F59)', EXPECT_TEST_PAIRED_ROWS, len(test))]
  session29_test.py: 6 differing lines
     -    if not t_dropped:
     -        pass
     -    checks = [('forecast-gap days in the test year (F38)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F41)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 18:00 hour (F41)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature (F41)', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected', EXPECT_TEST_PAIRED_ROWS, len(test))]
     +    if not t_dropped:
     +        pass
     +    checks = [('forecast-gap days in the test year (F75, F77)', EXPECT_TEST_FCGAP_DAYS, len(cause_fcgap)), ('days lost to an off-hour-only report (F76, F77)', EXPECT_TEST_OFFHOUR_DAYS, len(cause_offhour)), ('days lost to no report near the 20:00 hour (F77)', EXPECT_TEST_NOREPORT_DAYS, len(cause_noreport)), ('days lost to a report in place with no temperature', EXPECT_TEST_NOTEMP_DAYS, len(cause_notemp)), ('paired rows expected (F77)', EXPECT_TEST_PAIRED_ROWS, len(test))]
=== climatology_from_training (reference session18_test.py:climatology_from_training)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== fit_on_training (reference session18_test.py:fit_on_training)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: identical
=== score_test_year (reference session18_test.py:score_test_year)
  session07_test.py: identical
  session13_test.py: identical
  session24_test.py: identical
  session29_test.py: 1 differing lines
     +    ok_scored = len(common) == EXPECT_TEST_SCORED_DAYS
=== judge_the_bar (reference session18_test.py:judge_the_bar)
  session07_test.py: 8 differing lines
     -        banner = ['DSM PASSES.', 'At Des Moines the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled to a different region, at a', 'different target hour.']
     +        banner = ['STAGE 1 PASSES.', 'The corrected forecast beats both raw GFS and persistence', 'over the held-out test year, on mean absolute error.']
     -        banner = ['DSM DOES NOT PASS.', 'At Des Moines the corrected forecast does not beat both raw', 'GFS and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D35.10), not a reason', 'to re-run or to tune. It is a result about how far the', 'recipe travels, which is what a third airport was for.']
     +        banner = ['STAGE 1 DOES NOT PASS.', 'The corrected forecast does not beat both raw GFS and', 'persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4), not a reason to', 're-run or to tune.']
     -    if mb < raw:
     -        pass
     -    else:
     -        pass
  session13_test.py: 8 differing lines
     -        banner = ['DSM PASSES.', 'At Des Moines the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled to a different region, at a', 'different target hour.']
     +        banner = ['STAGE 2 PASSES.', 'At CDG the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled.']
     -        banner = ['DSM DOES NOT PASS.', 'At Des Moines the corrected forecast does not beat both raw', 'GFS and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D35.10), not a reason', 'to re-run or to tune. It is a result about how far the', 'recipe travels, which is what a third airport was for.']
     +        banner = ['STAGE 2 DOES NOT PASS.', 'At CDG the corrected forecast does not beat both raw GFS', 'and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D31.10), not a reason', 'to re-run or to tune. It is a result about how far the', 'recipe travels, which is what stage 2 was opened to ask.']
     -    if mb < raw:
     -        pass
     -    else:
     +    if mb > raw:
  session24_test.py: 4 differing lines
     -        banner = ['DSM PASSES.', 'At Des Moines the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled to a different region, at a', 'different target hour.']
     +        banner = ['DUBBO PASSES.', 'At Dubbo the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled to a fourth continent, a', 'flipped hemisphere and a flipped season cycle, at a', 'third distinct target hour.']
     -        banner = ['DSM DOES NOT PASS.', 'At Des Moines the corrected forecast does not beat both raw', 'GFS and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D35.10), not a reason', 'to re-run or to tune. It is a result about how far the', 'recipe travels, which is what a third airport was for.']
     +        banner = ['DUBBO DOES NOT PASS.', 'At Dubbo the corrected forecast does not beat both raw', 'GFS and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D39.10), not a reason', 'to re-run or to tune. It is a result about how far the', "recipe travels, and D39.12's single-season watch-item is", 'the first place to look for why - as description only.']
  session29_test.py: 4 differing lines
     -        banner = ['DSM PASSES.', 'At Des Moines the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', 'error. The recipe travelled to a different region, at a', 'different target hour.']
     +        banner = ['RENO PASSES.', 'At Reno the corrected forecast beats both raw GFS and', 'persistence over the held-out test year, on mean absolute', "error. This is despite session 27's negative rehearsal -", 'a difference D18 exists precisely to allow for, and D44.10', 'named as possible without licensing any change either way.']
     -        banner = ['DSM DOES NOT PASS.', 'At Des Moines the corrected forecast does not beat both raw', 'GFS and persistence over the held-out test year.', 'This is an honest finding (SPEC 2.4, D35.10), not a reason', 'to re-run or to tune. It is a result about how far the', 'recipe travels, which is what a third airport was for.']
     +        banner = ['RENO DOES NOT PASS.', 'At Reno the corrected forecast does not beat both raw GFS', 'and persistence over the held-out test year.', 'This is an honest, EXPECTED finding (SPEC 2.4, D44.9,', 'D44.12) - not a bug and not a reason to re-run or tune.', "D44.12's near-constant-bias / overfit pattern is the", 'pre-recorded expected reason; PART G looks at it, as', 'description only.']
=== main (reference session18_test.py:main)
  session07_test.py: 10 differing lines
     -    train, test, obs_all, reconciled = join()
     -    if not reconciled:
     -        sys.stdout = sys.__stdout__
     -        tee.flush()
     -        raise SystemExit(1)
     +    train, test, obs_all = join()
     -    compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr)
     -    compare_with_europe(common, methods, model)
     -    warm_end_watch_item(common, methods, train, pred_resid)
     +    compare_with_session05(common, methods, model, pred_resid, x_tr, y_tr)
  session13_test.py: 5 differing lines
     -    compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr)
     -    compare_with_europe(common, methods, model)
     -    warm_end_watch_item(common, methods, train, pred_resid)
     +    compare_with_session11(common, methods, model, pred_resid, x_tr, y_tr)
     +    compare_with_eglc(common, methods, model, passed)
  session24_test.py: 6 differing lines
     -    compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr)
     -    compare_with_europe(common, methods, model)
     -    warm_end_watch_item(common, methods, train, pred_resid)
     +    compare_with_session22(common, methods, model, pred_resid, x_tr, y_tr)
     +    compare_with_prior_airports(common, methods, model)
     +    single_season_watch_item(common, methods, train)
  session29_test.py: 6 differing lines
     -    compare_with_session16(common, methods, model, pred_resid, x_tr, y_tr)
     -    compare_with_europe(common, methods, model)
     -    warm_end_watch_item(common, methods, train, pred_resid)
     +    compare_with_session27(common, methods, model, pred_resid, x_tr, y_tr)
     +    compare_with_prior_airports(common, methods, model)
     +    near_constant_bias_watch_item(common, methods, train)

=== method constants
STATION:
   session07_test.py: (absent)
   session13_test.py: 'LFPG'
   session18_test.py: 'DSM'
   session24_test.py: 'YSDU'
   session29_test.py: 'RNO'
TARGET_HOUR:
   session07_test.py: 12
   session13_test.py: 12
   session18_test.py: 18
   session24_test.py: 2
   session29_test.py: 20
TRAIN_START:
   session07_test.py: date(2021, 3, 24)
   session13_test.py: date(2021, 3, 24)
   session18_test.py: date(2021, 3, 24)
   session24_test.py: date(2021, 3, 24)
   session29_test.py: date(2021, 3, 24)
TRAIN_END:
   session07_test.py: date(2025, 7, 31)
   session13_test.py: date(2025, 7, 31)
   session18_test.py: date(2025, 7, 31)
   session24_test.py: date(2025, 7, 31)
   session29_test.py: date(2025, 7, 31)
TEST_START:
   session07_test.py: date(2025, 8, 1)
   session13_test.py: date(2025, 8, 1)
   session18_test.py: date(2025, 8, 1)
   session24_test.py: date(2025, 8, 1)
   session29_test.py: date(2025, 8, 1)
TEST_END:
   session07_test.py: date(2026, 7, 31)
   session13_test.py: date(2026, 7, 31)
   session18_test.py: date(2026, 7, 31)
   session24_test.py: date(2026, 7, 31)
   session29_test.py: date(2026, 7, 31)
HARD_END:
   session07_test.py: TEST_END
   session13_test.py: TEST_END
   session18_test.py: TEST_END
   session24_test.py: TEST_END
   session29_test.py: TEST_END
CHUNKS:
   session07_test.py: [('2021-03-24', '2021-12-31'), ('2022-01-01', '2022-12-31'), ('2023-01-01', '2023-12-31'), ('2024-01-01', '2024-12-31'), ('2025-01-01', '2025-12-31'), ('2026-01-01', '2026-07-31')]
   session13_test.py: [('2021-03-24', '2021-12-31'), ('2022-01-01', '2022-12-31'), ('2023-01-01', '2023-12-31'), ('2024-01-01', '2024-12-31'), ('2025-01-01', '2025-12-31'), ('2026-01-01', '2026-07-31')]
   session18_test.py: [('2021-03-24', '2021-12-31'), ('2022-01-01', '2022-12-31'), ('2023-01-01', '2023-12-31'), ('2024-01-01', '2024-12-31'), ('2025-01-01', '2025-12-31'), ('2026-01-01', '2026-07-31')]
   session24_test.py: [('2021-03-24', '2021-12-31'), ('2022-01-01', '2022-12-31'), ('2023-01-01', '2023-12-31'), ('2024-01-01', '2024-12-31'), ('2025-01-01', '2025-12-31'), ('2026-01-01', '2026-07-31')]
   session29_test.py: [('2021-03-24', '2021-12-31'), ('2022-01-01', '2022-12-31'), ('2023-01-01', '2023-12-31'), ('2024-01-01', '2024-12-31'), ('2025-01-01', '2025-12-31'), ('2026-01-01', '2026-07-31')]
LGB_PARAMS:
   session07_test.py: dict(objective='regression_l1', n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0, colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1
   session13_test.py: dict(objective='regression_l1', n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0, colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1
   session18_test.py: dict(objective='regression_l1', n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0, colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1
   session24_test.py: dict(objective='regression_l1', n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0, colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1
   session29_test.py: dict(objective='regression_l1', n_estimators=300, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=1.0, colsample_bytree=1.0, reg_alpha=0.0, reg_lambda=0.0, random_state=42, n_jobs=1
CLIM_HALF_WINDOW_DAYS:
   session07_test.py: 7.5
   session13_test.py: 7.5
   session18_test.py: 7.5
   session24_test.py: 7.5
   session29_test.py: 7.5
FEATURE_NAMES:
   session07_test.py: ['forecast_temp_c', 'season_sin', 'season_cos']
   session13_test.py: ['forecast_temp_c', 'season_sin', 'season_cos']
   session18_test.py: ['forecast_temp_c', 'season_sin', 'season_cos']
   session24_test.py: ['forecast_temp_c', 'season_sin', 'season_cos']
   session29_test.py: ['forecast_temp_c', 'season_sin', 'season_cos']
````

### 6.12 `shell_steps.sh` — Step 0, the clone, and the consistency check

````bash
# Session 68b -- shell steps. Read-only against the working repo.
# Step 0
git status --porcelain                       # -> ?? docs/session-68b.md
# clean clone (project code runs only here)
git clone -q "/Users/zacharyadams/Coding Projects/MLwx" /tmp/audit68b/clone
git -C /tmp/audit68b/clone rev-parse HEAD    # -> 4e13cd513ac6f4adf7288ecf68f9af6ccc77a81f
ln -s "/Users/zacharyadams/Coding Projects/MLwx/data/raw/grib" /tmp/audit68b/clone/data/raw/grib   # read-only use; 62570 entries
cd /tmp/audit68b/clone && python3 -m venv .venv && .venv/bin/python -m pip install -q -r requirements.txt   # PyPI download (see "How the work was run")
diff <(.venv/bin/python -m pip freeze | sort) <(grep -E '^[A-Za-z0-9_.-]+==' requirements.txt | sort)   # -> no output; 19 pins
# data checks (outputs in the Appendix)
python3 /tmp/audit68b/diff_minimal.py            # item 20 (source reading only)
python3 /tmp/audit68b/dc1_issue_time.py          # items 1, 12
python3 /tmp/audit68b/dc2_openmeteo_meta.py      # items 1, 8, 10, 11
DYLD_LIBRARY_PATH= .venv/bin/python /tmp/audit68b/dc3_grid_weights.py   # item 11 (run from the clone)
python3 /tmp/audit68b/dc4_family_columns.py      # items 10, 13, 14, 16
python3 /tmp/audit68b/dc5_obs_paths.py           # items 3, 8, 9, 21
.venv/bin/python /tmp/audit68b/dc6_guards.py     # item 7 (run from the clone)
python3 /tmp/audit68b/dc7_nan_scan.py            # items 10, 22
python3 /tmp/audit68b/dc8_copies.py              # items 12, 15, 17, 21
.venv/bin/python /tmp/audit68b/dc9_feature_order.py   # items 18, 22 (run from the clone)
python3 /tmp/audit68b/bound_item6.py             # item 6 (recorded figures only)
git -C /tmp/audit68b/clone status --porcelain    # -> ?? data/raw/grib   (the symlink only)
# consistency check of the three files (CLAUDE.md end-of-session step 3), working repo, read-only
for f in SPEC.md STATUS.md DECISIONS.md; do grep -E '^#{1,4} ' $f | sort | uniq -d; done   # -> no output
grep -n '^## 20' DECISIONS.md    # 15 dated headers, checked in non-decreasing date order
````
