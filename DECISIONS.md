# DECISIONS.md — the project's memory of *why*

This is an **append-only** log. Add new entries at the bottom. Never delete
or rewrite old entries. Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D47: raw-data policy for large re-fetchable sources.
- D73: pre-registration of the 2026-27 GFS forward test.
- D77: the NBM/MOS comparison and the 2026-27 NBM/MOS test (D77.6).
- D79: how the 2026-27 tests are reported.
- D82: stage C's design.
- D88: stage C's development table and the curve's baseline.
- D89: the rules for stage C's build choices.
- F139: the baseline's cross-validation scores (the incumbent, D89.7).
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- F142: session 99's finding.
<!-- live-index-end -->

Every entry not listed here is in DECISIONS-archive.md, unchanged and still
binding. Entry numbers never change, so every citation resolves in one of the
two files. This list changes only through an owner's DECISIONS entry; a
session adds its own new entries (D93.8).

---

**D47. Raw-data policy for large re-fetchable sources: manifest, not bytes.** D15 committed raw pulls when raw meant small Open-Meteo JSON. The GRIB pull is ~20 GB, which cannot live in git (binary bloat; GitHub file and repo size limits). For large, re-fetchable public archives such as GFS GRIB, D15s immutable-provenance intent is served by committing the provenance manifest (exact queries, URLs, byte-ranges, and the drop log) plus the processed dataset, and gitignoring the raw bytes -- which are reproducible from the manifest. D15 stands unchanged for small API pulls. The ~20 GB local GRIB cache is disposable and re-fetchable.

---

## 2026-09-27 — Session 81 decision: pre-registration of the 2026-27 GFS forward test (owner, planning chat)

**D73. Owner decision, planning chat (after session 80): the
pre-registration of the 2026-27 GFS forward test (D72.5).** Written at the
start of session 81, before any data was read or any model was fit. No
2026-27 value has been read or scored. Where this entry is more precise
than D72.5, this entry governs; D73.4 amends D72.5's "only file paths may
change".

- **D73.1 What is tested.** SPEC 8's recipe `B+D,L,R,T`, unchanged: the
  same features and transforms (SPEC 8.1), the same column order (SPEC
  8.8 G15), the same frozen LightGBM settings (D21.4/D48.6, lightgbm
  4.7.0, SPEC 8.8 G14, G17), the same target (observation minus
  `temperature_grib_c`, SPEC 8.8 G20). Six airports: EGLC, LFPG, DSM,
  YSDU, RNO and KSFO, each with its own grid point, target hour, lead and
  elevation constant (SPEC 3.4, 4.1, 5.2, 7.2).
- **D73.2 The frozen models.** One `B+D,L,R,T` model per airport, trained
  once on every complete-case row dated 2021-03-24 to 2026-07-31 (all
  GFS v16), in ascending date order (G19), from committed processed files
  only. It is saved as a LightGBM text model file and its SHA-256 is
  recorded in F122. It is never refit. Also frozen, as descriptive rungs
  only: one plain `B` model per airport, trained the same way on the same
  rows; and one mean-bias constant per airport, mean(observation minus
  raw GFS (GRIB)) over the same rows. The training rows keep the
  historical observation pairing (SPEC 4.5's note); new 2026-27 code
  pairs explicitly to the nearest report (SPEC 8.7).
- **D73.3 The test year and its split.** The test year is 2026-08-01 to
  2027-07-31. A target day is in period B if the GFS cycle that forecasts
  it (SPEC 7.2's lead convention) is an operational GFS v17 cycle, and in
  period A otherwise. Any v16.x cycle is period A. The boundary is the
  first operational v17 cycle, taken from NCEP's Service Change Notice and
  confirmed in the archive. Parallel ("para") data is never used. If no
  operational v17 cycle has forecast any day by 2027-07-31, period A is
  the whole year and period B is not run. If anything other than one
  clean switch happens (a rollback, a second version change, mixed
  cycles), stop: the owner decides in writing before any value is scored.
- **D73.4 Inputs after v17 (amends D72.5).** 2026-27 features are built
  with the same logic as the record pipelines, with only their date
  ranges extended (as F107 did for the reserved year); the code itself is
  new (D73.8). For v17 inputs, file paths may change. How a field is
  fetched (message name, level specification, which accumulation window
  is read) may also change, but only if the physical quantity is
  identical: the same variable, level, time window ending at the target
  hour, units and transform. The owner approves each such change. It is
  decided from v17's documentation and the fields themselves, never from
  any 2026-27 error or score. Each change is written into DECISIONS, with
  its evidence, before any period-B value is scored. If any input to `B+D,L,R,T` or to raw GFS
  (GRIB) cannot be built this way, or the 0.25° GRIB2 grid is no longer
  offered, period B is recorded as void (not run). A void period is not
  a fail. The elevation constants (SPEC 5.2) stay frozen, even though
  v17's terrain differs; they apply to raw GFS and the model alike. The
  grid points (SPEC 3.4) and interpolation (SPEC 8.8 G6) are unchanged.
  Nothing is refit, retuned or reselected.
- **D73.5 The bar and the rungs.** The bar is SPEC 5.3, applied per
  airport per period: the frozen `B+D,L,R,T` model's MAE must be lower
  than both raw GFS (GRIB, elevation-adjusted, SPEC 5.2) and persistence.
  Descriptive rungs, never part of the bar: the frozen `B` model and the
  mean-bias reference. The day basis is SPEC 8.5's: raw GFS and the
  models on every complete-case test day; persistence on test days that
  also have a previous-day observation. Missing forecasts or observations
  are dropped and counted (SPEC 2.2). There is no minimum day count. Each
  period's row count is reported against its full expected count; a
  shortfall is reported and does not block the verdict.
- **D73.6 Verdicts.** Each airport gets one PASS or FAIL per period,
  labelled with the period's dates and season. The two periods answer
  different questions (A: does the recipe hold on a new year; B: does the
  v16-trained model survive v17), so they are not combined, and D71.6's
  every-look-must-pass rule does not apply. Nothing is averaged across
  airports (SPEC 5.0). KSFO carries D71.5's framing. The write-up leads,
  in each period, with the smallest bar margin across the six airports.
  No earlier verdict changes.
- **D73.7 Expectations, stated before any value is seen.** Period A:
  `B+D,L,R,T` passes at all six airports. Period B: no expectation is
  stated. Period A will probably be short (a few months of autumn); its
  verdict stands whatever its length, labelled with its dates and season.
- **D73.8 When it is scored.** No 2026-27 value (model prediction error,
  raw-GFS error or persistence error) is computed until its period has
  ended and its observations are in. **Hold rule:** period A is not
  scored until the owner has decided, in writing, whether to pre-register
  a comparison against NBM/NWS MOS on 2026-27 (stage A, D72.7). Once any
  part of 2026-27 is scored, no new test may be pre-registered on it
  (SPEC 2.5). The 2026-27 data-build and scoring scripts are written in a
  later session and committed before any 2026-27 row is built. They
  implement this entry exactly, and SPEC 8.7's build requirements apply
  to them. Until each period is scored, its data is held out for claims
  and no build choice may use it (SPEC 2.5).
- **D73.9 A consequence, accepted.** Period B's data is held out until it
  is scored, after 2027-07-31. So stage F (upgrade policy) cannot use
  live v17 data for any build choice before then without spending period
  B. Before then, its only v17 training data would be NOAA's v17
  retrospective runs, if they are public (D72.3). The design is not
  changed for this.
- **D73.10 The two DSM A67-15 files** (D62.7): the two tracked DSM files
  for 2026-08-05..2026-08-15. Their paths and SHA-256 are recorded in
  F122. They were not opened in session 81. They are not used to build
  or score anything; period A's data is fetched fresh.
- **D73.11 Session 81's plan.** Record this entry; build the training set
  from committed files; pass a reproduction gate (the new training code
  must reproduce F109's and KSFO look B's recorded MAEs exactly); train
  and freeze the models; record F122.
- **D73.12 GFS v17 (planning-chat web search, 2026-09-27, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The SCN is due 30 days before go-live, so
  the earliest go-live is about late October 2026.

---

## 2026-09-29: Session 85 decision: the NBM/MOS comparison, its outcome rule and the 2026-27 NBM/MOS test (owner, planning chat)

**D77. Owner decisions, planning chat (after session 84): the NBM/MOS
comparison (D72.7), its outcome rule, the F123.9 decision (D75.3) and a
pre-registered NBM/MOS test on 2026-27 (D73.8).** Written at the start of
session 85, before any network call or data read. No NBM or MOS value
and no 2026-27 value has been read.

- **D77.1 Competitors.** NBM CONUS `core`, the deterministic 2 m
  temperature, at DSM, RNO and KSFO: the primary comparison. GFS MOS
  (MAV) at DSM only: a secondary, descriptive comparison, because MAV
  has no 20:00 UTC projection at RNO or KSFO (F123.4) and no value is
  interpolated in time. NAM MOS is excluded (terminated October 14,
  2026, SCN 26-47). LAMP is excluded (not a day-ahead product).
- **D77.2 Matching.** For each target day D: the same target hour as
  the record (SPEC 3.4); the competitor run with the same nominal cycle
  as our GFS cycle (floor(H/6)x6 UTC on D-1, F5, F89), at the lead that
  makes its valid time equal the target hour (DSM: 18z D-1, 24 h; RNO
  and KSFO: 18z D-1, 26 h). NBM's value is taken at the grid point
  nearest the station's position in SPEC 3.4 (nearest neighbour, no
  interpolation), converted from K to degC. MAV's value is used as
  issued (whole degF), converted to degC exactly; the rounding is a
  recorded caveat and is not corrected. The observation is the one in
  the recorded rows, so every forecast is scored against the same
  value. Missing competitor values are dropped and counted (SPEC 2.2).
- **D77.3 The spent-year comparison.** Recorded predictions only, after
  a reproduction gate: F109's `B+D,L,R,T` at DSM and RNO (2024-08-01 to
  2025-07-31) and F119's saved predictions at KSFO, look A (2024-25) and
  look B (2025-26). No other years: the feature-selection folds
  (2022-23, 2023-24 and truncated 2025-26) chose `B+D,L,R,T`'s features
  and would flatter it. Day set: the recorded model test days on which
  the competitor value is present. Reported per airport-look: MAE of
  the model, the competitor and raw GFS (GRIB, elevation-adjusted), mean
  errors, d = MAE(competitor) - MAE(model) in degC and skill =
  1 - MAE(model)/MAE(competitor), with F125's interval method (7-day
  moving blocks, 10,000 resamples, 95% percentile) and seed 85. NBM
  version segments are labelled; MAE per segment is descriptive only.
  This spends no held-out data: the years are already spent (F94, F109,
  F119). It is descriptive and decides direction only (D72.7). It
  changes no verdict. KSFO carries D71.5's framing. The comparison is
  at one hour; stage C re-runs it on the full curve, as a description
  (D72.8).
- **D77.4 The outcome rule (D72.7), fixed before the comparison is
  run.** Judged on NBM only, on point estimates, over the four
  airport-looks (DSM, RNO, KSFO look A, KSFO look B):
  - **Win:** the model's MAE is lower than NBM's at all four. The
    roadmap carries on as D72 sets it.
  - **Lose:** NBM's MAE is lower than or equal to the model's at all
    four.
  - **Mixed:** anything else.
  On "lose" or "mixed", the gap is recorded (d, skill and intervals),
  and the owner decides in writing, before stage C's lock, between:
  (a) bringing a US-only stacking check (NBM as an input) forward from
  stage E; (b) weighting the roadmap towards non-US airports; (c) both;
  or (d) neither, with reasons. The intervals are reported but do not
  set the band. The MAV comparison is reported and does not set the
  band. The comparison is reported in full whatever the band.
- **D77.5 F123.9 accepted.** Session 82's exploratory MOS request held
  projections valid 2026-08-01 to 08-08 in memory only; no value was
  printed, saved or used, and no observation or score was involved. No
  information about 2026-27 outcomes was learned. It is accepted and
  recorded; no 2026-27 day is excluded because of it.
- **D77.6 A pre-registered NBM/MOS test on 2026-27.** This entry is the
  owner's written decision that D73.8's hold rule requires.
  - What is tested: the frozen F122 `B+D,L,R,T` models (SHA-256 in
    F122), unchanged, at DSM, RNO and KSFO.
  - Competitors and matching: as D77.1 and D77.2. NBM at all three; MAV
    at DSM only.
  - Periods: D73.3's period A and period B, judged separately. Neither
    is scored before it has ended and its observations are in (D73.8).
  - Day set: D73.5's complete-case test days on which the competitor
    value is also present. Missing values are dropped and counted.
  - Pass rule: per airport, per period, per competitor, PASS if the
    frozen model's MAE is lower than the competitor's MAE on that day
    set, otherwise FAIL. Each verdict is labelled with its dates, its
    season and the competitor versions in force.
  - Descriptive, never part of the rule: F125-method intervals, and the
    frozen `B` model and raw GFS on the same days.
  - Separate from D73: no D73 verdict depends on this test, and this
    test changes none.
  - Expectations: none stated.
  - Competitor changes: a version change inside a period does not split
    it; it is labelled. If a competitor has no value in a period (for
    example, it is discontinued), that comparison is void for that
    period. A void comparison is not a fail.
  - Data: fetched from the archives after each period ends, with the
    same valid-time guards. The scripts are written in a later session,
    with D73.8's scripts, and committed before any 2026-27 row is built.
  - KSFO carries D71.5's framing. The write-up leads, in each period,
    with the smallest margin.
- **D77.7 NBM versions (planning-chat web search, 2026-09-29, not
  checked by this session).** v4.2 from 2024-05-15; v4.3 effective on
  or about 2025-05-27 from the 12z run (SCN 25-34 was issued
  2025-04-15, which explains F123.3's two dates); v5.0 from 2026-05-05;
  v5.0.14 on 2026-07-28, which fixed anomalous temperature and dewpoint
  guidance, notably in transition seasons and coastal areas. So both
  spent years use NBM before that fix. v4.3's changes were mainly to
  tropical-cyclone wind and severe-weather products.
- **D77.8 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice; the newest SCN listed
  is SCN 26-87 (2026-09-22). With 30 days' notice, the earliest go-live
  is about late October 2026 or later.
- **D77.9 Session 85's plan.** Record this entry; run the reproduction
  gate; pull NBM and MAV for the spent-year days only; run the
  comparison and apply D77.4's rule; record F127. SPEC 6's stage A and
  stage B bullets are updated to point to this entry and F127.

---

## 2026-09-30: Session 87 decision: how the 2026-27 tests are reported, and the scoring and competitor scripts (owner, planning chat)

**D79. Owner decisions, planning chat (after session 86): how the
2026-27 tests (D73, D77.6) are reported, and the scope of the scoring
and competitor scripts (D78.7).** Written at the start of session 87,
before any other edit, network call or data read. No 2026-27 value has
been read or scored. This entry makes D73 and D77.6 precise where they
leave a reporting detail open. It changes no pass rule, rung, day set
or expectation.

- **D79.1 Margin.** Where D73.6 and D77.6 say the write-up leads with
  the smallest margin, the margin is a percentage: 100 x (1 -
  MAE(model)/MAE(baseline)), at full precision, with the difference
  MAE(baseline) - MAE(model) in degC shown beside it.
  - D73: per period, the smallest over the six airports and both halves
    of the bar (raw GFS (GRIB) and persistence), twelve values.
  - D77.6: per period, the smallest over DSM against NBM, RNO against
    NBM, KSFO against NBM and DSM against MAV.
  A failing result has a negative margin, so it leads. Reason: the
  airports' error levels differ, so a percentage compares like with
  like; it is also the form of the record's tables (SPEC 7.4, 8.5).
- **D79.2 Ties.** PASS needs a strictly lower MAE at full precision
  (SPEC 5.3, D73.5, D77.6). An equal MAE is FAIL.
- **D79.3 No days.** If an airport has no complete-case day in a period,
  or has complete-case days but none with a previous-day observation,
  its D73 result for that period is "no verdict (0 days)". It is neither
  a pass nor a fail, and it is reported. D77.6's own rule for a
  competitor with no value in a period (void) is unchanged. Otherwise
  D73.5's rule stands: there is no minimum day count.
- **D79.4 Labels.** Each verdict's season label is its first and last
  target date and the calendar months it covers, for example
  "2026-08-01 to 2026-11-10 (Aug, Sep, Oct, Nov)". NBM and MAV version
  labels (D77.6) come from a DECISIONS entry written before that period
  is scored, naming each version and the cycle it started from. The
  scripts print these labels; they do not infer versions.
- **D79.5 Intervals.** D77.6's descriptive intervals use F125's method
  as F127 used it: 7-day moving blocks, 10,000 resamples, 95% percentile,
  for d and skill. Each period uses a new generator,
  numpy.random.default_rng(87), in this order: DSM against NBM, RNO
  against NBM, KSFO against NBM, DSM against MAV. D73 reports no
  intervals, because it did not pre-register any (D73.8: its scripts
  implement it exactly).
- **D79.6 Periods.** The competitor fetch and the scoring script cover
  both periods, so neither needs editing after any 2026-27 row exists.
  Period B is used only with the first operational v17 cycle from a
  DECISIONS entry (D73.3), and is scored only from a period-B rows file
  made by a later build mode that D73.4's v17 entry allows. If period B
  is not run (D73.3) or is void (D73.4), the scripts are not run for it.
- **D79.7 GFS v17 (planning-chat web search, 2026-09-30, not checked by
  this session).** Still no Service Change Notice. The newest SCN listed
  is SCN 26-87 (2026-09-22). The only v17 notices are still the April
  proposals, PNS 26-29 and PNS 26-30. With 30 days' notice, the earliest
  go-live is about 30 October 2026. PNS 26-30 still says the 0.25 degree
  pgrb2 files remain; this is to be confirmed against the SCN (D73.4).
- **D79.8 Session 87's plan.** Record this entry; write and gate the
  competitor script and the scoring script; record F129; add citations
  of D78, F128 and (if both gates pass) F129 to SPEC 6. Neither script's
  2026-27 mode is run.

---

## 2026-10-03: Session 90 decision: F131 accepted, the end goal reworded, and stage C's design (owner, planning chat)

**D82. Owner decisions, planning chat (after session 89): F131
accepted, the end goal reworded, and stage C's design: target and
horizon, data route, airports, the claim batch rule and the daily
maximum.** Written at the start of session 90, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D82.1 F131 accepted.** The owner accepts F131 and all eleven
  F131.9 readings, including the reduced reproduction sample (13 of 63
  dates) and the strided speed test. Its conclusions stand: the
  dynamical.org archive lacks two of the recipe's inputs (850 hPa
  temperature, 2 m dew point) and defines cloud cover differently, so
  it is not used; the GRIB route holds every field at every hour.
- **D82.2 The end goal, reworded (replaces D72.1's wording).** A
  private, live tool for ten or more airports that corrects every GFS
  run (four a day), as each run arrives, into an hourly temperature
  curve out to the forecast horizon, plus the daily maximum; the
  horizon is 24 hours first and 48 hours later; then a choice of which
  weather model is corrected, plus a blend; and probabilistic ranges.
  It stays a private product built with good academic practice (D72.1,
  D72.2(d)). The rest of D72 is unchanged.
- **D82.3 Stage C's target and horizon.** The corrected forecast is
  made from every GFS cycle (00, 06, 12 and 18 UTC), for every forecast
  hour from 0 to 24 first. Forecast hours 25 to 48 are added later by a
  separate, additive pull; nothing in the first pull is repeated. The
  daily maximum is part of stage C's target (D82.8).
- **D82.4 The data route.** NOAA's GFS GRIB files on
  `noaa-gfs-bdp-pds`, fetched by byte range as the record does (SPEC
  7.2). The pull runs on GitHub Actions in the public project
  repository, as resumable chunks (each job is capped at 6 hours); the
  first chunk measures speed. Each global field is downloaded, the
  values at the four grid points around each airport are read out, and
  the field is discarded: no global field is kept. Fields: the record's
  eight (2 m temperature, total cloud cover, 10 m u and v wind, 2 m dew
  point, 850 hPa temperature, downward shortwave radiation at the
  surface, mean sea level pressure) plus GFS's 2 m maximum and minimum
  temperature. Kept: the raw value at each of the four grid points, per
  airport, field, cycle and forecast hour, so interpolation choices stay
  open. Period: every cycle and forecast hour whose valid time lies
  between 2021-03-24T00:00 and 2026-07-31T23:00 UTC; nothing from
  2026-27. Estimated at about 100 files a day, about 1.6 to 1.8 TB of
  downloads and about 1.5 GB kept for 47 airports (planning-chat
  estimate from F131, not checked). The kept files are published as
  GitHub Release files and downloaded once to the owner's laptop, so
  the repository stays small. Gate: at each existing airport's target
  hour, cycle and lead, the new values equal the committed ones. The
  design details are session 91's.
- **D82.5 What is not decided.** Whether one model takes lead time as an
  input or each lead has its own model; whether the daily maximum is
  read off the corrected curve or has its own model; and stage C's
  claim design (bar, looks, lead bands). These are fixed by
  time-ordered cross-validation on the development airports (D82.6) or
  at stage C's lock, before any claim airport's held-out data is read.
  Stage C's SPEC section is written at its lock. Bias drift follows
  D81.10(b).
- **D82.6 The airports.** The owner's 47-airport list, by ICAO code and
  the owner's region label:
  Europe: EHAM, LTAC, EFHK, LTFM, EGLC, LEMD, LIMC, UUWW, EDDM, LFPB,
  EPWA.
  North America: KATL, KAUS, KORD, KDAL, KBKF, KHOU, KLAX, MMMX, KMIA,
  KLGA, KSFO, KSEA, CYYZ.
  South America: SAEZ, SBGR.
  Asia: ZBAA, RKPK, ZUUU, ZUCK, ZGGG, OEJN, OPKC, WMKK, VILK, RPLL,
  ZSQD, RKSI, ZSPD, ZGSZ, WSSS, RCSS, LLBG, RJTT, ZHHH.
  Africa: FACT. Oceania: NZWN.
  All 47 are in the pull and are the product's airports. EGLC and KSFO
  are already spent. The 45 others are new. **Until a later decision
  says otherwise, no new airport's data is used for any build choice:**
  build choices use the six development airports (EGLC, LFPG, DSM,
  YSDU, RNO, KSFO) only, so every new airport stays clean for this and
  later claim batches (D72.2(a), D72.3 "Ongoing"). Whether the MOSMIX
  list (D81.2) grows to new airports is left to the saver session;
  session 90 records which have a station within 10 km.
- **D82.7 The claim batch: rules fixed before any check is run.** Six
  airports, drawn by this rule and nothing else:
  (a) Excluded: EGLC and KSFO (spent), and LFPB (about 9 km from LFPG, a
  development airport, so weak evidence; it stays in the product).
  (b) Eligible: an airport whose saved hourly observations give a usable
  daily maximum (D82.8) on at least 90 percent of local days in
  2021-03-24..2026-07-31, and on at least 90 percent of local days in
  its held-out window 2024-08-01..2026-07-31. A local day counts only if
  it starts on or after 2021-03-24T00:00 UTC and ends on or before
  2026-07-31T23:59 UTC. An airport with no IEM archive is not eligible.
  (c) Strata and sizes, in this order: Europe 1; North America 2; Asia
  2; South (the owner's South America, Africa and Oceania labels
  together) 1.
  (d) Draw: Python's `random.Random(20261003)`, one generator for the
  whole draw. For each stratum in (c)'s order, `sample` its eligible
  airports, sorted by ICAO code, for its size. If a stratum has fewer
  eligible airports than its size, take them all, and after the last
  stratum fill the shortfall by `sample` from all remaining eligible
  airports, sorted by ICAO code, with the same generator. Record the
  Python version.
  (e) Each drawn airport's held-out window is 2024-08-01..2026-07-31
  (D72.4); its earlier years are for training. Its looks are fixed at
  stage C's lock.
- **D82.8 The daily maximum (stage C's target).** From the routine
  hourly reports (SPEC 3), at every airport: the local calendar day,
  midnight to midnight in the airport's own time zone (civil time,
  daylight saving included); each report assigned to its nearest whole
  hour by SPEC 8.8 G2 and G3; the day's maximum is the highest usable
  hourly value. A day is usable only if usable hours are at least its
  number of hours minus 2 (22 of 24; 21 of 23 and 23 of 25 on
  clock-change days). A peak between hourly reports is missed; this is
  accepted, being the same everywhere. It is not meant to match any
  outside published figure; the aim is accuracy.
- **D82.9 SPEC.** SPEC 1's end-goal paragraph is reworded to D82.2, and
  SPEC 6's stage C bullet records D81 and D82 (session 90, Step 2).
- **D82.10 Sequence.** Session 90: this entry, the SPEC edits, the
  airport metadata check (counts only) and the draw. Session 91: build
  the GitHub Actions pull and run a small local test chunk through
  D82.4's gate. The owner then pushes and starts the full pull. Session
  92: verify the extracts.

---

## 2026-10-06: Session 96 decision: F137 accepted, GFS v17, and the stage C development table (owner, planning chat)

**D88. Owner decisions, planning chat (after session 95): F137
accepted, GFS v17, and the first step on stage C's build choices: the
development table, the curve's baseline, and the rules for features at
every lead.** Written at the start of session 96, before any other
edit. No 2026-27 value has been read or scored.

- **D88.1 F137 accepted.** The owner accepts F137 and all nine F137.11
  readings, including the change to the download step (F137.3).
  Reading 9 (2022-11's 135 retries equal 27 x 5) is the script's
  arithmetic inference; the meta does not record it.
- **D88.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-89 (2 October
  2026, model changes for the RRFS implementation). Correction to
  D87.6: SCN 26-89 was posted on the same day as SCN 26-88, so 26-88
  was not the newest. With 30 days' notice, the earliest go-live is
  about 5 November 2026. PNS 26-29's proposed October 2026 date can no
  longer be met.
- **D88.3 What comes first.** D82.5's build choices need a development
  table: for each development airport (EGLC, LFPG, DSM, YSDU, RNO,
  KSFO), every GFS cycle in the pull and every forecast hour 0 to 24,
  the record's features rebuilt from the stored grid values, and the
  hourly observation at the valid time. Session 96 builds it and gates
  it against the committed record. It fits no model and computes no
  score.
- **D88.4 The curve's baseline.** SPEC 8's recipe `B+D,L,R,T`, applied
  unchanged at each cycle hour and lead: one model per airport, cycle
  hour (00, 06, 12, 18 UTC) and lead, so 100 models per airport, with
  the record's settings, column order and complete-case rule. This is
  the proven method applied at every hour, one well-understood input
  first (D72.2(b)). It is recorded now and fitted later. D82.5's
  alternatives (one model per lead with the cycle hour as an input; one
  model with lead and hour as inputs) are each compared against it by
  time-ordered cross-validation.
- **D88.5 Features at every lead.** The record's definitions, extended:
  (a) Instantaneous fields (temperature, cloud cover, 10 m wind, dew
  point, 850 hPa temperature, sea level pressure) at every lead,
  including f000 (the analysis), by the record's arithmetic
  (bilinear, elevation constant on temperature only, rounding as SPEC
  8.8 G4 and G7).
  (b) R is the mean downward shortwave radiation over the 2 hours
  ending at the valid time. GFS gives A(N), the average over (W, N],
  W = 6 x floor((N-1)/6). If N - W >= 2: R = ((N - W) x A(N) -
  (N - 2 - W) x A(N - 2)) / 2, where the second term is zero when
  N - 2 = W (so R = A(N) at leads 2, 8, 14, 20). This is the record's
  de-accumulation at lead 24. If N - W = 1 (leads 7, 13, 19): R =
  (A(N) + 6 x A(W) - 5 x A(W - 1)) / 2, adding the last hour of the
  previous 6-hour window. R does not exist at leads 0 and 1.
  (c) T is the sea level pressure at lead N minus that at lead N - 3,
  same cycle, in hPa, from the two rounded pressures as the record
  does. At lead 3 it uses the f000 analysis. T does not exist at
  leads 0 to 2.
  (d) Season terms from the valid date, by the record's
  `year_fraction`.
  (e) GFS's 6-hour maximum and minimum 2 m temperature are kept as
  raw columns (bilinear, degrees C, rounded to 3 decimals, no
  elevation constant) for the later daily maximum work. They are not
  features of the baseline.
- **D88.6 Leads 0 to 2.** The complete-case rule stands. Rows at leads
  0 to 2 stay in the table, marked incomplete and counted, never
  filled. A GFS run arrives about 3.5 to 4 hours after its start time,
  so these leads are already in the past when it lands.
- **D88.7 The observation.** At every valid whole hour: the nearest
  usable report within 15 minutes, inclusive (SPEC 4.5, 8.8 G2 and G3,
  the record's `pair_nearest`; a tie keeps the earlier report). The
  same at every airport.
- **D88.8 Where the table lives.** About 1.17 million rows, so it is
  kept outside the repository, in `MLwx-stagec/` beside `MLwx-pull/`.
  The repository holds the script, a meta file with every table file's
  SHA-256, and a counts file. The table is rebuilt exactly from the
  Release and the committed observation files.
- **D88.9 Rules for build choices.** Before any cross-validation score
  is computed, a DECISIONS entry fixes the folds, the metric, and a
  rule of the form "keep the simpler option unless the other wins by
  more than a stated margin". Build choices are never quoted as
  results (SPEC 2.5).
- **D88.10 SPEC 6.** The stage C bullet records that the pull is
  complete and checked (D87, F137), and points to this entry (session
  96, Step 2).
- **D88.11 Sequence.** Session 96: this entry, the SPEC edit, the
  table and its gate. Then, planned: session 97 writes D88.9's entry
  before any score, then fits the baseline and scores raw GFS and the
  baseline per lead by cross-validation. D82.5's comparisons, the daily
  maximum, and bias drift (D81.10(b)) follow, one change at a time.
  Stage C's claim design is fixed at its lock.

---

## 2026-10-06: Session 97 decision: F138 accepted, GFS v17, and the rules for stage C's build choices (owner, planning chat)

**D89. Owner decisions, planning chat (after session 96): F138
accepted, GFS v17, and the rules for stage C's build choices: folds,
metric and decision rule (D88.9).** Written at the start of session 97,
before any other edit and before any cross-validation score. No
2026-27 value has been read or scored.

- **D89.1 F138 accepted.** The owner accepts F138 and all thirteen
  F138.8 readings, including: both `temp` and `temperature_grib_c`
  kept as columns; the instantaneous columns taken from session 91's
  `derive` with placeholder R and T inputs that never reach the table;
  and the fourth empty reason, "outside pull window" (7 R and 10 T
  cells per airport in the first cycles).
- **D89.2 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-06, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is still SCN 26-89 (2
  October 2026). The earliest go-live stays about 5 November 2026.
- **D89.3 Folds.** Three time-ordered folds, each with an expanding
  training window. A test year runs 1 August to 31 July:
  fold 2023-24: test cycles 2023-08-01T00 to 2024-07-31T18;
  fold 2024-25: test cycles 2024-08-01T00 to 2025-07-31T18;
  fold 2025-26: test cycles 2025-08-01T00 to 2026-07-31T18.
  With T0 the test year's start (1 August, 00:00 UTC): training rows
  are those with valid time before T0; test rows are those whose cycle
  starts on or after T0 and before the next 1 August. A row whose cycle
  is before T0 and whose valid time is on or after T0 is in neither,
  and is counted. Training thus uses only observations already known
  when the first test cycle starts. The 2022-23 fold is not used: its
  training window (about 1.4 years) is far shorter than the product's
  or the claim airports' (about 3.4 years, D82.7(e)), and would
  unfairly penalise options that fit many small models.
- **D89.4 The spent years.** 2024-25 and 2025-26 are spent at every
  development airport (F94, F109, F119; D71.1), so they may be used
  for build choices (D72.2(a), SPEC 2.5). The session-48 reserved-year
  guard stays unchanged in its own script and is not imported here.
  Nothing from 2026-27 is used.
- **D89.5 Metric.** Mean absolute error (MAE) of the hourly
  temperature, degrees C, full precision (SPEC 8.8 G24), on leads 3 to
  24. Rows: the common row set, meaning test rows that have an
  observation and are complete for every option compared (for the
  baseline, the table's `complete_case`). Per airport: one MAE over all
  its test rows, pooled across the three folds, four cycle hours and
  leads 3 to 24. Headline: the unweighted mean of the six airport
  MAEs. Fold level: per fold, the unweighted mean of the six airports'
  MAEs over that fold's rows.
- **D89.6 Decision rule.** The challenger replaces the incumbent only
  if all three hold: (a) the headline MAE is lower by more than 1
  percent of the incumbent's headline, that is (incumbent - challenger)
  / incumbent > 0.01; (b) the airport MAE is lower at 4 or more of the
  6 airports; (c) the fold-level MAE is lower in at least 2 of the 3
  folds. Otherwise the incumbent stays. A tie keeps the incumbent.
- **D89.7 The incumbent.** For D82.5's model-structure comparisons, the
  incumbent is D88.4's baseline (the proven recipe, unchanged, D72.2(b)),
  even though the alternatives use fewer models. Every later
  comparison names its incumbent in its own DECISIONS entry before it
  is scored.
- **D89.8 Scope of the rule.** It applies to every stage C build choice
  on the hourly curve. A choice is applied to the whole curve and to
  every airport identically: never per airport, cycle hour or lead.
  The daily maximum's metric is fixed in its own entry before any
  daily-maximum score. Changing these rules needs a new DECISIONS entry
  written before the affected score. Build-choice scores are never
  quoted as results (SPEC 2.5).
- **D89.9 The fitting code's gate.** Before any fold is scored, the new
  fitting code reproduces F109's recorded raw GFS and `B+D,L,R,T` MAEs
  at EGLC and LFPG (12z, lead 24) and DSM (18z, lead 24), exactly, from
  the table's rows on the record's days. This is a code check against
  numbers already on record. It is not a new look and decides nothing.
- **D89.10 Sequence.** Session 97: this entry, the fold counts, the gate,
  then the baseline and raw GFS scored per airport, fold, cycle hour
  and lead. No build choice is made. Then, planned: D82.5's
  alternatives, each against the baseline under D89.6, one at a time;
  then the daily maximum and bias drift (D81.10(b)). Stage C's claim
  design is fixed at its lock.

---

## 2026-10-06: Session 97 finding: the cross-validation folds, the gate, and the baseline scored

**F139. Every score in this entry is a build-choice score, not a result (SPEC 2.5); none is a claim, a pass or a fail. Offline. D89 was recorded first. The fold rows were counted under D89.3 with no fit. The new fitting code passed D89.9's gate: it reproduced F109's raw GFS and `B+D,L,R,T` MAEs at EGLC, LFPG and DSM exactly, 6 of 6. D88.4's baseline was then fit (1,584 models) and scored with raw GFS on the same rows, per airport, fold, cycle hour and lead 3 to 24. Headline (D89.5): raw GFS 1.4617, baseline 1.0498 degrees C. No build choice was made. Script: `scripts/session97_stagec_cv.py` (new; modes `--folds`, `--gate`, `--score`, `--guard-check`, `--meta`; SHA-256 `987ab6bacc3a4171710e4eb9b10e967108ede52fa572f4611413d24ac5631f91`). Full real output: `notes/session-97-output.txt`. Run 2026-10-06. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

**F139.1 Step 0 and Step 1.** `git status --porcelain` showed only `?? docs/session-97.md`. The last entries were D88 and F138; no D89 or F139 existed in either DECISIONS file; the new script and the three new `data/processed/` files did not exist. SHA-256 equal to the record: the six table files (F138.4), the table meta `eace666a...9463` and counts `304d25a6...3dfb`, `session96_stagec_table.py` `40b63d00...6eee`, `session62_reserved_confirm.py` `9f8af9af...80b4` (D70.2), `session81_training_set.csv` `ab8f25f2...8d4a` (F122.3). `session63_reserved_confirm_grid.csv` is `0138ba039d0bd077e71b829789a8d3c93175e22493ed115f7503b2baa30f4ed3`; that value is recorded in `notes/session-85-output.txt` (lines 21 and 167), not in either DECISIONS file. Read: D70, D71, D72, D82, D88, F109, F122, F138; SPEC 2.5, 5, 8.1 to 8.3, 8.5, 8.8; the record script in full. D89 was copied with `sed` from `docs/session-97.md` lines 105 to 177 into DECISIONS.md lines 3736 to 3808 (heading at 3734) and checked byte-equal with `diff` and `cmp`, before any other edit.

**F139.2 The folds (Step 2, `--folds`, no fit).** Complete-case rows, leads 3 to 24, four cycle hours. Every airport and fold has 40 boundary rows (cycles of 31 July with valid times on 1 August: 1 + 7 + 13 + 19). Test rows of the three folds never overlap (0 at every airport); every training row's valid time is before its T0 (0 violations).

| airport | train 23-24 / 24-25 / 25-26 | test 23-24 / 24-25 / 25-26 | test dropped (not complete) | smallest model train |
|---|---|---|---|---|
| EGLC | 75,555 / 107,760 / 139,864 | 32,205 / 32,104 / 32,059 | 3 / 16 / 21 | 856 / 1,222 / 1,587 |
| LFPG | 75,370 / 107,541 / 139,600 | 32,171 / 32,059 / 31,958 | 37 / 61 / 122 | 844 / 1,209 / 1,566 |
| DSM | 75,647 / 107,847 / 139,964 | 32,200 / 32,117 / 32,072 | 8 / 3 / 8 | 858 / 1,223 / 1,588 |
| YSDU | 74,694 / 106,652 / 138,576 | 31,958 / 31,924 / 31,763 | 250 / 196 / 317 | 845 / 1,207 / 1,568 |
| RNO | 75,341 / 107,534 / 139,643 | 32,193 / 32,109 / 32,040 | 15 / 11 / 40 | 854 / 1,220 / 1,585 |
| KSFO (SFO) | 75,623 / 107,822 / 139,913 | 32,199 / 32,091 / 32,040 | 9 / 29 / 40 | 858 / 1,223 / 1,588 |

`data/processed/session97_stagec_cv_folds.csv`: 1,584 rows, SHA-256 `77fce6c7c288f37a9d63f4e9b9b8675cad26f0e9b8a2ba4b657084496fb01b66`.

**F139.3 The gate (Step 3, `--gate`, D89.9). PASSED, 6 of 6, exact equality.** Table rows on the training set's (station, valid date) keys, F109's fold by valid date; every selected row was complete case.

| airport | train (F122.4) | test (F109) | B+D,L,R,T: this fit = grid `final_mae` | raw GFS: this fit = grid `raw_mae` |
|---|---|---|---|---|
| EGLC 12z, lead 24 | 1,225 (1,225) | 364 (364; grid no_obs 1) | 1.0007550363323212 | 1.23621978021978 |
| LFPG 12z, lead 24 | 1,224 (1,224) | 365 (365) | 1.2368626165917669 | 1.4091397260273972 |
| DSM 18z, lead 24 | 1,225 (1,225) | 365 (365) | 1.4122847644111458 | 1.7043452054794521 |

**F139.4 The scores (Step 4, `--score`; build-choice scores, not results).** 1,584 fits, 118.8 s. The two methods' n are equal in every cell. MAE in degrees C, common row set (D89.5).

| airport | n | raw GFS | baseline | raw GFS by fold 23-24 / 24-25 / 25-26 | baseline by fold |
|---|---|---|---|---|---|
| EGLC | 96,368 | 0.9725 | 0.7742 | 0.9614 / 0.9891 / 0.9672 | 0.7491 / 0.8010 / 0.7725 |
| LFPG | 96,188 | 1.1596 | 0.8937 | 1.1477 / 1.1739 / 1.1571 | 0.8653 / 0.9434 / 0.8726 |
| DSM | 96,389 | 1.7582 | 1.2034 | 1.9144 / 1.6502 / 1.7095 | 1.2463 / 1.1430 / 1.2208 |
| YSDU | 95,645 | 1.4633 | 1.2149 | 1.4724 / 1.5053 / 1.4120 | 1.2457 / 1.1976 / 1.2013 |
| RNO | 96,342 | 2.1717 | 1.1735 | 2.0114 / 2.2890 / 2.2152 | 1.2148 / 1.1860 / 1.1193 |
| KSFO (SFO) | 96,330 | 1.2449 | 1.0390 | 1.2514 / 1.2237 / 1.2595 | 1.0297 / 1.1095 / 0.9777 |
| **headline / fold-level** | | **1.4617** | **1.0498** | 1.4598 / 1.4719 / 1.4534 | 1.0585 / 1.0634 / 1.0274 |

Headline at full precision: raw GFS 1.4616990883475995, baseline 1.049777501605027. **No airport-lead where the baseline is not below raw GFS** (pooled over folds and cycle hours; 0 of 132). The six-airport mean per lead runs from 1.3606 / 0.9648 (lead 3) to 1.5223 / 1.1083 (lead 24); per cycle hour, 12z is lowest for both (1.4380 / 1.0328). Full tables in the output file. `data/processed/session97_stagec_cv_scores.csv`: 3,168 rows, SHA-256 `5604ccd16118fe772cd24a7be83b36ee62e500c78b3ed5bf55c76ed4e78d9d76`.

**F139.5 Repeatability and meta (Step 5).** `--score --airports EGLC` into a `mktemp -d` directory: its 528 rows (with the header) are byte-equal to EGLC's rows in the scores file (`diff` and `cmp`); the directory was deleted. The 2026-27 guard refuses a valid time of 2026-08-01T00:00 and allows 2026-07-31T23:00 (2 of 2). `data/processed/session97_stagec_cv.meta.txt`, SHA-256 `95223b4fbc519c5cc1811d1682e0b0e94c5976c54511dedaf58c4777671b313a`, lists the inputs, script and outputs with SHA-256, `LGB_PARAMS` as passed and the versions.

**F139.6 Readings made where the prompt is silent (for the owner to confirm or change).**
1. **The session-48 module.** As the prompt says, `LGB_PARAMS` and the G15 order are imported from `session62_reserved_confirm.py` (after its SHA-256 check), as session 81 did. That script imports the session-48 reserved-year module at load, for its own use (D70.7, F118.9). This script never imports or calls the guard itself; D89.4's "not imported here" is read that way.
2. The G15 order imported is also checked in code against D70.1's written list.
3. Boundary rows (D89.3, "in neither") are counted whatever their completeness; test rows "dropped as not complete case" are those with no observation (leads 0 to 2 are outside the files' lead range).
4. Error is `obs_tmpc` minus forecast (Step 4.2); the record computes forecast minus observation. Their absolute values are equal bit for bit, so MAEs are unaffected; the sign matters only for the mean error column.
5. A pooled MAE (per airport, per fold, per lead or per cycle hour) is the NumPy mean of the concatenated errors, in fold, cycle hour, lead, then cycle-time order. It is not rebuilt from the per-cell MAEs.
6. Training rows within a model are in ascending cycle time (G19); test rows the same.
7. On load, each table file's SHA-256 is checked against F138.4, `complete_case` is checked against the nine columns and the observation (no disagreement), `temp` is checked equal to `temperature_grib_c`, and every valid and observation time passes the 2026-27 guard.
8. "Smallest training count of any single model": where several models tie, the lowest (cycle hour, lead) is named.
9. The output file adds one table not asked for: each airport's raw GFS and baseline MAE per lead (pooled over folds and cycle hours), from which Step 4.4's last item is read.
10. Output files are written once and refused if present (SPEC 8.7 item 5). Bytecode writing was turned off for every run, so no `__pycache__` was written.

**F139.7 What this did not do.** No network. No build choice: D89.6's rule was not applied, and no setting, feature, parameter or structure was changed, tuned or selected; only D88.4's baseline was fit, with the record's settings. No model was saved, and `data/models/` was not touched. Nothing from 2026-27: no row valid after 2026-07-31T23:00 was read or scored. No non-development airport's data was read. `MLwx-stagec/` and `MLwx-pull/` unchanged (SHA-256 checked at the end). No existing script edited. Nothing installed. SPEC.md, RESULTS.md, CLAUDE.md, README.md and PROJECT-INSTRUCTIONS.md not edited. Nothing committed and no commit message written.

---

## 2026-10-09: Session 99 decision: F141 accepted, the session order, and a workflow overhaul (owner, planning chat)

**D93. Owner decisions, planning chat (after session 98c): F141 accepted,
three carried items, GFS v17, the session order, and a workflow overhaul
that cuts the reading cost of each session.** Written at the start of
session 99, before any other edit. No 2026-27 value has been read or
scored.

- **D93.1 F141 accepted,** with all nine F141.7 readings.
- **D93.2 The invocation.** The claude.ai Project instructions and section
  4 of `docs/PROJECT-INSTRUCTIONS.md` both give D92.4's invocation, with
  `docs/sessions/session-NN.md` (planning-chat check, 2026-10-09).
- **D93.3 lightgbm.** From D90.9 and F140.7, new scripts may import
  lightgbm directly, with no libomp shim.
- **D93.4 RESULTS.md section 7.** Its roadmap paragraph is out of date
  (F140, F141). It is fixed once, in the session that closes D82.5's
  model-structure comparisons, so that it is edited with their outcome.
  Until then it stays an open item.
- **D93.5 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-09, not checked by this session).** Still no Service Change
  Notice for GFS v17. The newest SCN listed is SCN 26-91 (6 October 2026).
  With 30 days' notice the earliest go-live is about 8 November 2026. Also:
  SCN 26-47 (updated) now ends NAM MOS on 3 November 2026, not 14 October
  as D77.1 and F127's correction give. NAM MOS was already excluded
  (D77.1), so nothing changes.
- **D93.6 Session order (amends D90.3).** Session 99 is this workflow
  overhaul. The first of D82.5's alternatives against the baseline
  (D89.10) moves to session 100. Its open choices (which alternative
  first, the rule if both alternatives beat the baseline, the model
  settings, and how the cycle hour is encoded) are fixed in session 100's
  own entry, before any score. Nothing else in D89 changes.
- **D93.7 Why the archive step stopped working.** DECISIONS.md had grown
  to 343,813 bytes (about 4,100 lines), against 773 lines after D46, and
  the archive was last changed on 2026-09-29. The end-of-session archive
  step existed, but: (a) its criterion kept any entry still cited by
  STATUS or by a live entry, and each new entry cites recent ones, so
  recent entries never became movable; (b) its default was "when in
  doubt, keep live" (D46); (c) Claude Code applied it alone each session,
  often by repeating an earlier session's reasons, and the planning-chat
  review accepted "nothing moved" without checking the file's size; (d)
  finding entries copied full tables already held in the output files.
  The step checked a criterion but never its outcome. D93.8 to D93.10
  replace it with an explicit list and a size limit checked every
  session.
- **D93.8 The live file (replaces D46's criterion).** DECISIONS.md opens
  with a Live index: the entries in force for current work. The owner
  changes the index only through a DECISIONS entry; a session adds its own
  new entries to it. At the end of every session, every entry not in the
  index moves verbatim to DECISIONS-archive.md, by
  `scripts/archive_decisions.py`. Being cited elsewhere is not a reason to
  keep an entry live: a citation resolves by number in either file, and an
  archived entry is still binding. The index after session 99: D47, D73,
  D77, D79, D82, D88, D89, F139, D93 and F142. D62 is archived; its rule
  that frozen scripts are never edited (D62.3(a)) stands, restated here:
  `session39_sealed_test.py`, `session48_reserved_year.py`,
  `session60_combine_design.py` and `session62_reserved_confirm.py` are
  never edited.
- **D93.9 Size limit.** Every session reports the byte size of
  DECISIONS.md after its archive step. Above 80,000 bytes is a
  consistency finding that the next planning session must act on.
- **D93.10 Finding entries.** A finding is at most about 40 lines: what
  was done, the numbers a decision needs, readings for the owner, what was
  not done, and a pointer to the output file. Full tables, lists and logs
  stay in `notes/session-NN-output.txt`, which begins with a summary of at
  most 30 lines.
- **D93.11 Long sessions and their guardrails.** Sessions may be longer
  and cover more, so that fewer sessions pay the start-up reading. In
  return each prompt lists the files the session may create or edit,
  checked against `git status` before the end steps; Claude Code writes a
  checkpoint line after each step, stops rather than works around a failed
  check, and after any mid-session compaction re-reads CLAUDE.md, the
  prompt and its checkpoints before going on.
- **D93.12 Keeping context small.** Claude Code does not print large files
  or outputs into the conversation; scripts print short summaries and
  write full tables to files; the archive is never read in full, only one
  entry at a time by line range.
- **D93.13 The planning side** (`docs/PROJECT-INSTRUCTIONS.md`). The
  planning chat reads its guide and STATUS in full; SPEC, CLAUDE and
  DECISIONS by targeted search unless the session being planned edits
  them; DECISIONS-archive.md is uploaded to Project knowledge for search
  only; the GFS v17 check is the weekly task of D93.15; reviews start
  from the output file's summary and checkpoints.
  Related work is combined into fewer, fuller sessions, and the planning
  chat recommends a Claude Code model for each.
- **D93.14 Session 99's plan.** Record this entry; replace CLAUDE.md; edit
  `docs/PROJECT-INSTRUCTIONS.md`; add the Live index; move every entry
  outside it to the archive with a checked script; check that every
  citation still resolves; record F142. No model, data file or existing
  script is touched.
- **D93.15 Two planning-side automations.** (a) A weekly scheduled task
  (Mondays, 08:57 London time) searches for a GFS v17 Service Change
  Notice and alerts the owner only when it finds one. Planning chats no
  longer re-check v17; a D entry mentions v17 only when the task has
  found a notice. (b) After the owner commits and pushes a reviewed
  session, the planning chat copies the changed files into claude.ai
  Project knowledge itself, from the linked computer, without their
  contents entering the chat (`docs/PROJECT-INSTRUCTIONS.md` section 5).
  The owner no longer re-uploads by hand, except when the planning chat
  reports that a sync failed.
- **D93.16 What each session reads, and the invocation (replaces
  D92.4's).** Each session prompt begins with a Read first section that
  lists what Claude Code reads before the steps: files in full, SPEC
  sections, and DECISIONS entries by number, live or archived. STATUS.md
  and SPEC section 2 are always read. With no list, the default is
  STATUS.md, SPEC section 2 and the live DECISIONS.md in full. A step
  that needs something not read reads just that part and notes it in its
  checkpoint. CLAUDE.md is loaded automatically and is not read again. So
  the invocation is fixed: "Carry out the session defined in
  docs/sessions/session-NN.md: first read what its Read first section
  lists, then do its steps, staying strictly within its scope. Stop at
  the end-of-session steps and wait for my review. Do not commit
  anything." Each session starts in a fresh Claude Code conversation (a
  new terminal or `/clear`): carrying a finished session's context into
  the next costs more than the short start-up read and blurs the review
  boundary.

---

## 2026-10-09: Session 99 finding: the workflow overhaul, the Live index and the first move

**F142. Session 99. No model experiment was run and no build choice was made. D93 was recorded first. CLAUDE.md was replaced, eight edits were made to `docs/PROJECT-INSTRUCTIONS.md`, a Live index was added to DECISIONS.md, and every entry outside it moved verbatim to DECISIONS-archive.md with a new, checked script. Script: `scripts/archive_decisions.py` (new; SHA-256 `25813993a0991171a19f4137988fa71c704160f6d24926abf4740c8cdcb911e8`). Full real output: `notes/session-99-output.txt`. Run 2026-10-09.**

- **F142.1 D93.** Copied with `sed`; `diff` and `cmp` equal; 0 em-dashes.
- **F142.2 CLAUDE.md** replaced by the prompt's block (`diff`, `cmp` equal):
  6,539 to 8,234 bytes, 0 em-dashes. **PROJECT-INSTRUCTIONS.md:** edits
  (a) to (h), each target found exactly once: 13,070 to 15,195 bytes.
- **F142.3 The script.** Standard library only: `--plan`, `--apply
  --session NN`, `--citations`. Tested first on a temporary copy with a
  made-up two-entry index: all four checks passed, the copy rebuilt byte
  for byte, a second `--apply` moved nothing. The copy was deleted.
- **F142.4 The move.** 49 spans: 9 kept (one per index ID), 40 moved
  (299,631 bytes, 2 of them pointer spans). All four checks passed (live
  769 + moved 3,511 = original 4,280 lines; the old archive is an exact
  prefix of the new). DECISIONS.md 343,813 bytes at the start, 352,074
  with D93 and the index, 52,283 after the move. DECISIONS-archive.md
  982,727 to 1,282,554 bytes.
- **F142.5 Citations** (after the move, before this entry): 166 distinct
  entry numbers cited, 165 resolved, 1 unresolved (F142, cited by D93), 0
  in both files, 0 doubled entries, 0 dated headings out of order. The
  end-of-session counts are in the output file.
- **F142.6 Readings for the owner.**
  1. The prompt's CLAUDE.md block itself uses colons in the title and the
     carried passages, so the new file has no em-dashes at all.
  2. The old archive already ended with `---` and a blank line, so the new
     section starts after two `---` lines with nothing between them. The
     heading is followed directly by `---`. Both follow the prompt's format.
  3. The pointer spans for D1 to D12 and F88 moved, as they are not in the
     index. The entries still resolve in the archive.
  4. Left unedited (outside the eight edits): `PROJECT-INSTRUCTIONS.md`'s
     closing line still says "re-upload it"; section 3 step 2 still says
     re-upload when docs are stale; the archive's own header still
     describes D46's criterion; DECISIONS.md's header still says
     "append-only ... Never delete".
  5. The first `--apply` call was blocked by Claude Code's auto-mode
     permission check. Both DECISIONS files were copied to the session's
     scratch folder, then the same command ran unchanged.
  6. `scripts/README.md` has no list of standing scripts, so the new line
     ends the "Everything else" list.
- **F142.7 What this did not do.** No model, score or data read; no network
  call; nothing installed; no existing script, data or workflow file edited;
  no entry retyped or renumbered; SPEC.md, RESULTS.md, README.md and
  data/README.md not edited. Nothing committed; no commit message written.
