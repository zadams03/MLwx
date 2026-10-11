# DECISIONS.md — the project's memory of *why*

This is the live log. New entries are added at the bottom, and no entry is
ever edited or deleted. Entries outside the Live index move verbatim to
DECISIONS-archive.md (D93.8). Each entry is dated.

It records choices made, why they were made, open questions, and findings.

## Live index

<!-- live-index-start -->
- D82: stage C's design.
- D88: stage C's development table and the curve's baseline.
- D89: the rules for stage C's build choices.
- D93: the workflow rules (Live index, size limit, finding length, guardrails).
- D97: F145 accepted, the f025 to f048 pull, the commit history, and the bias-drift test.
- D98: F146 accepted, D97.1 closed, the f025 to f048 checks, the curve to 48 hours, and the daily maximum's metric.
- F147: session 104's finding.
- D99: F147 accepted, and two daily-maximum challengers in a fixed order.
- F148: session 105's finding.
<!-- live-index-end -->

Every entry not listed here is in DECISIONS-archive.md, unchanged and still
binding. Entry numbers never change, so every citation resolves in one of the
two files. This list changes only through an owner's DECISIONS entry; a
session adds its own new entries (D93.8).

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

## 2026-10-11: Session 103 decision: F145 accepted, the f025 to f048 pull, the commit history, and the bias-drift test (owner, planning chat)

**D97. Owner decisions, planning chat (after session 102): F145 accepted,
the f025 to f048 pull run, the commit history rewritten, and every choice of
the bias-drift test (D78.2, D81.10(b)), fixed before any score.** Written at
the start of session 103, before any other edit. No 2026-27 value has been
read or scored.

- **D97.1 F145 accepted,** with its three readings. Reading 1 stays open:
  `session92_verify_chunk.py --gate` (local only) and
  `session95_check_release.py` still look up F122.3 and F133 to F136 in
  DECISIONS.md by text, and session 95's script is fixed to the 0-24
  Release. Neither is used by the workflow. Both are dealt with when session
  104, which downloads and checks the f025 to f048 pull, is planned.
- **D97.2 The f025 to f048 pull (D96.5), run by the owner on GitHub
  Actions.** First `hours` = `25-48` for 2022-01 alone: the verify step
  printed `RESULT: PASS`, and the owner checked the new Release
  `stagec-grib-pull-f025-048` (title, notes and three files). Then
  2021-03..2026-07: the Release holds 195 files, three for each of the 65
  months (owner's count, 2026-10-10). The workflow publishes a month only
  after its verify step (D84.4) passes. The files have not been downloaded
  or checked together; that is session 104's.
- **D97.3 Commit history.** Some commit messages (sessions 73, 101 and 102)
  ended with `Co-Authored-By` and `Claude-Session` lines, which GitHub reads
  as a co-author. On 2026-10-09 the owner removed those lines from every
  commit message on `main` (`git filter-branch --msg-filter`) and
  force-pushed. Commit IDs from session 73 onward changed; no file's content
  changed. Commit messages never include such lines; PROJECT-INSTRUCTIONS.md
  section 8 says so from session 103.
- **D97.4 What is tested.** One challenger. For every test row, its forecast
  is the baseline's forecast plus b, where b is a decaying average of the
  baseline's own recent errors (observation minus baseline forecast). After
  each new error e: b = (1 - w) x b + w x e, with w = 0.02. The weight is
  NOAA's operational value for NAEFS bias correction (about a 50-day memory;
  Cui, NCEP, "Decide to use 2% (~ 50 days)"; planning-chat web check
  2026-10-11, not checked by this session). It is fixed in advance, not
  tuned, and no other weight or method is tried.
- **D97.5 One tracker per airport, fold, cycle hour and lead,** the same
  cells as the baseline's models. A tracker is updated only by its own
  cell's test rows that are scored (complete case, with an observation), in
  ascending valid time. A missing day is skipped: the update counts errors,
  not calendar days. Errors are always the baseline's, never the corrected
  forecast's.
- **D97.6 No look-ahead.** The forecast from the cycle starting at time c
  uses only errors whose valid time is before c. The observation is within
  15 minutes of its valid whole hour (D88.7), so it was reported at least 45
  minutes before c. So at lead n, the newest usable error is from the cycle
  one day earlier for n up to 23, and two days earlier for n = 24.
- **D97.7 Start of each test year.** Every tracker starts at b = 0 at its
  fold's T0 (D89.3). Errors on training rows are in-sample and are never
  used. This handicaps the challenger early in each fold; it is accepted.
- **D97.8 The rule.** The incumbent is D88.4's baseline (D89.7, D95.2).
  Metric and rows as D89.5; the challenger's rows are the baseline's,
  exactly. D89.6 decides. If the challenger passes, the curve becomes the
  baseline plus this correction, identically at every airport, cycle hour
  and lead (D89.8). If not, the baseline stays. Either way no other variant
  (weight, window, pooling, latency) is scored in session 103; any later
  variant is a new build choice, fixed in its own entry before its score.
- **D97.9 Descriptive figures, not used by the rule.** The mean error
  (observation minus forecast) of raw GFS, the baseline and the challenger
  per airport and fold; each airport's b at the end of each fold (mean,
  minimum and maximum over its 88 cells); and the six-airport MAE per lead
  for each method.
- **D97.10 This is not a claim.** Build-choice scores are never quoted as
  results (SPEC 2.5). No later change to the recipe can be claimed against
  NBM on 2026-27 (D78.4).
- **D97.11 Order of the next steps (replaces D96.5's session numbers).**
  Session 103: this entry and the bias-drift test. Session 104: download and
  check the f025 to f048 pull (with D97.1's open item), extend the
  development table and the curve to leads 25 to 48 (with the bias-drift
  correction if it passed), fix the daily maximum's metric in its own entry
  (D89.8), and score it.
- **D97.12 Live index.** Removed (archived): D96 and F145, which are settled
  (their open parts are restated here). Added: D97 and F146. After session
  103: D47, D73, D77, D79, D82, D88, D89, F139, D93, D95, D97, F146.

---

## 2026-10-11: Session 104 decision: F146 accepted, D97.1 closed, the f025 to f048 checks, the curve to 48 hours, and the daily maximum's metric (owner, planning chat)

**D98. Owner decisions, planning chat (after session 103): F146 accepted,
D97.1's open item closed, the download and checks of the f025 to f048 pull,
the curve extended to lead 48, the hourly metric over the whole horizon, and
the daily maximum's metric (D89.8), all fixed before any score.** Written at
the start of session 104, before any other edit. No 2026-27 value has been
read or scored.

- **D98.1 F146 accepted,** with its seven readings. Reading 2's wording was
  corrected at the review, before the commit: the gain at KSFO is
  "consistent with D78.2 and D71.4 (KSFO's bias shifting between years)".
- **D98.2 D97.1 closed: scripts that find entries by text.**
  `session92_verify_chunk.py --gate` (local only) and
  `session95_check_release.py` are not edited. Their checks ran and passed
  (F134, F137) and stand. F122 and F133 to F136 are now archived, so those
  lookups no longer resolve and those modes cannot be re-run as they stand.
  This is recorded, not fixed, as D96.3 did for session 86. Session 92's
  other modes, which the workflow's verify step uses, read no DECISIONS
  entry and are unaffected. From now on a script never finds a recorded
  value by searching DECISIONS text: it holds the value as a constant, and a
  test in `tests/` checks the constant against the entry in either
  DECISIONS file.
- **D98.3 The download and checks.** A new script downloads the Release
  `stagec-grib-pull-f025-048` once into `MLwx-pull-f025-048/` beside the
  repository (D95.6) and checks, as session 95 did for the f000 to f024 pull
  (D87, F137): every file equal to its Release size and SHA-256; every
  month's meta as expected, with the pull script's SHA-256 equal to F145's;
  session 92's verifier with `--hours 25-48` (its D84.4 checks, then with
  `--ranges`) on every month; the union of all months equal to the 25-48
  plan (187,768 (cycle, hour) keys, F145.1), with no key in two months;
  status totals, including any "ok (whole file)" messages; a negative test;
  and an inventory file committed. Network only to GitHub's API and the
  Release's download links (and the host they redirect to). The pull-level
  `--gate` is not run (D98.2); D98.4's table gate checks the same values
  and more.
- **D98.4 The table for leads 25 to 48.** For each development airport and
  every (cycle, forecast hour) in the 25-48 plan: D88.5's features and
  D88.7's observation, by session 96's code and rules, written as six new
  files in `MLwx-stagec/`. F138's six files are never changed. Inputs before
  forecast hour 25 (T at leads 25 to 27; R at lead 25, which needs A(24) and
  A(23)) come from the f000 to f024 pull (`MLwx-pull/`, F137). Where that
  pull has no such value (cycles before its first), the feature is empty,
  with reason "outside pull window", and counted. The new builder must
  reproduce F138's rows exactly when run on hours 0 to 24 (Step 3's
  equivalence check). Gate: at YSDU (00z, lead 26), RNO and KSFO (18z, lead
  26), every committed station-day of `session81_training_set.csv` equal in
  every shared column, exact equality, as F138 did at lead 24. This is the
  first stage C gate at these three airports. Observation agreement with the
  record's `obs_c` is counted and reported.
- **D98.5 The curve at leads 25 to 48.** As at leads 3 to 24: D88.4's
  baseline (one model per airport, cycle hour and lead) plus D97's
  correction, with D97.4 to D97.7 unchanged. A tracker uses only errors
  whose valid time is before the forecast's cycle (D97.6). So the newest
  usable error is two days old at leads 25 to 47 and three days old at lead
  48. Folds and rows as D89.3. The fitting code's gate (extends D89.9): from
  the table's rows, F109's raw GFS and `B+D,L,R,T` MAEs at YSDU (00z, lead
  26) and RNO (18z, lead 26), reproduced exactly, as F139.3 did at the other
  three airports. If either differs, and the only difference is in the
  observations (the table's pairing against the record's, SPEC 4.5's
  note), the gate is run again with the record's observations and both
  results are reported; any other difference stops the session. KSFO is not
  in this gate: F109 has no KSFO row, and D98.4 gates its features.
- **D98.6 Reproduction at leads 3 to 24, before any new score.** The refit
  reproduces F139 exactly (every cell's n and MAE, the headline, the
  per-airport n) and F146's correction exactly (every drift cell's n and MAE
  equal to session 103's scores file; headline 1.019044682206963).
- **D98.7 Forecasts on rows with no observation.** Each model also predicts
  test rows whose features are complete but which have no observation; the
  daily maximum needs them (D98.10(c)). Such rows never enter an hourly
  score and never update a tracker (D97.5), and every correction is applied
  to them too. No hourly score changes.
- **D98.8 The hourly metric (amends D89.5).** From this entry, D89.5's
  metric is taken over leads 3 to 48, the product's horizon (D82.2): per
  airport, one MAE pooled over folds, cycle hours and leads 3 to 48; the
  headline and fold level as D89.5. Leads 3 to 24 and 25 to 48 are also
  reported. D89.6 and D89.8 are unchanged. The incumbent for the next hourly
  build choice is the curve, the baseline plus D97's correction (D97.8); its
  scores at leads 3 to 48 are F147's.
- **D98.9 The correction at leads 25 to 48 is carried as decided** (D97.8:
  identically at every lead). Its scores there, with D89.6's three parts
  against the baseline, are descriptive only. If its 25 to 48 headline is
  not lower than the baseline's, that is a reading for the owner; nothing
  changes in session 104.
- **D98.10 The daily maximum's metric (D89.8),** fixed before any
  daily-maximum score.
  (a) The observed maximum, as D82.8. Hourly values by D88.7 (the table's
  pairing) at every whole UTC hour of the local day; the day is usable if
  its usable hours are at least its hours minus 2. Time zones: EGLC
  Europe/London, LFPG Europe/Paris, DSM America/Chicago, YSDU
  Australia/Sydney, RNO and KSFO America/Los_Angeles. A day is used only if
  its last hour is valid on or before 2026-07-31T23:00 UTC.
  (b) Which run. For the local day D starting at UTC time s, the cycle is
  the latest GFS cycle c (00, 06, 12 or 18 UTC) with c + 4 hours <= s; a run
  arrives about 3.5 to 4 hours after it starts (D88.6). So every hour of D
  lies at lead 4 to 33, and each day has one forecast: the "tomorrow's
  maximum" a user would see the evening before. Forecasts for the same day
  from later runs (partly observed already) are a later question.
  (c) The forecast maximum: the highest of the method's hourly forecasts
  from cycle c over every whole hour of D. If any hour has no forecast, the
  day is dropped for that method and counted.
  (d) Folds: a day belongs to the fold of its cycle (D89.3's test rule). A
  day whose cycle is before its fold's T0 is in neither, and counted.
  (e) Metric: MAE of the daily maximum, degrees C, full precision, on the
  common day set (a usable observed maximum and a forecast maximum from
  every method compared). Per airport, pooled over folds; the headline is
  the unweighted mean of the six; fold level as D89.5.
  (f) Methods scored in session 104: raw GFS (`temperature_grib_c`), the
  baseline, and the curve (the baseline plus D97's correction), each read
  off its hourly values. Mean error (observation minus forecast) and the
  cycle hours used are descriptive.
  (g) Later daily-maximum build choices: D89.6 on this metric. The
  incumbent is the curve's read-off maximum. Each challenger (for example a
  model of its own, D82.5, or one using GFS's 6-hour maximum, D88.5(e)) is
  fixed in its own entry before its score. Session 104 makes no
  daily-maximum build choice.
  (h) Hourly values miss a peak between reports, on both sides alike
  (D82.8).
- **D98.11 This is not a claim.** Every score here is a build-choice score
  (SPEC 2.5). Nothing from 2026-27 is read.
- **D98.12 SPEC and RESULTS.** Session 104 updates SPEC 6's stage C bullet
  and RESULTS section 7's roadmap paragraph, with the text in its prompt.
- **D98.13 Session 104's plan.** This entry; the download and checks; the
  table and its gate; the curve's gates and scores; the daily maximum;
  tests; the SPEC and RESULTS edits; F147. The next step is chosen at
  session 105's planning.
- **D98.14 Live index.** Removed (archived): D95 (its work is done; the
  structure it closed is restated in D98.8) and F146 (reproduced and
  restated by F147, D98.6). Added: D98 and F147. After session 104: D47,
  D73, D77, D79, D82, D88, D89, F139, D93, D97, D98, F147.

---

## 2026-10-11: Session 104 finding: the f025 to f048 pull checked, the table and curve to 48 hours, and the daily maximum scored

**F147. Every score in this entry is a build-choice score, not a result (SPEC 2.5); none is a claim. D98 was recorded first. The f025 to f048 pull was downloaded and passed every check; the development table for leads 25 to 48 was built and gated (with one cell accepted by an owner ruling at a stop); the curve's gates reproduced F139, F146 and F109 (YSDU, RNO at lead 26) exactly; the curve was scored at leads 3 to 48 and the daily maximum under D98.10. No build choice was made. Scripts (new): `scripts/session104_pull_check.py` (`fabd0cbeddc97029e4ea46e2247aad3f42edaf9d57bddb0fff9c5c132669b19f`), `scripts/session104_stagec_table_f025_048.py` (`77457e262aae6388495ebebac64c730bc82d82675a3802d89fbd5f7f09fc2222`), `scripts/session104_curve_cv.py` (`6dcd872791463bf58f6578da35e577441a444562b398385c775749bf5890d4cb`). Full real output: `notes/session-104-output.txt`. Run 2026-10-11. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

- **F147.1 The pull (D98.3).** 195 files, 1,217,250,028 B, each equal to its Release digest (0 retries, 1,130 s), in `MLwx-pull-f025-048/`. Every meta as expected, pull script `557e8832...7b1675` (F145) in all 65. Verifier 13 of 13 and `--ranges` clean on all 65 months. Union equals the 25-48 plan: 187,768 (cycle, hour) keys (F145.1), 1,877,680 messages, 9,576,168 points rows; no key twice. Statuses: ok 1,877,380; ok (whole file) 300 (30 files in F135's three 2022-11 cycles); idx missing 0; check failed 0. Negative tests as specified. Inventory `data/processed/session104_pull_f025_048_inventory.csv` (195 rows, `5b6cd6f99dcadd0df5bbc313988514495d906126738df6f45944e2ce9208f9d1`).
- **F147.2 The table (D98.4).** 187,768 rows per airport (1,126,608), in `MLwx-stagec/stagec_dev_f025_048_<ICAO>.csv.gz` (SHA-256 in `data/processed/session104_stagec_f025_048_table.meta.txt`, `27622ada...5859`; counts `ca9b2dee...96f2`). Complete-case rows: EGLC 187,588, LFPG 187,200, DSM 187,716, YSDU 185,852, RNO 187,335, KSFO 187,620. Empty cells only "outside pull window" (R 5, T 8 per airport). Equivalence: rebuilt hours 0 to 24 (EGLC, RNO, 2022-01) byte-equal to F138's. F138's six files unchanged.
- **F147.3 The stop and the owner ruling (planning chat, 2026-10-11).** The first `--gate` stopped on one mismatch: YSDU 2021-03-24 `pressure_tendency_3h_hpa`, committed -0.921, table empty, since its input (PRMSL at f023 of cycle 2021-03-23T00, valid 2021-03-23T23:00) lies before the pull window (D82.4). Ruling: (1) accepted as the case D98.4 names; the cell stays empty and the table is unchanged; (2) the gate accepts a difference only where the cell is empty "outside pull window" with its input valid before 2021-03-24T00:00, listed and counted; (3) Step 4's YSDU fitting gate uses -0.921 for that cell, gate only, never in any fit or score; (4) carry on. D98 is not edited. Re-run: GATE PASSED, 1 accepted cell, all else equal: YSDU 1,929, RNO 1,952, KSFO 1,952 station-days, 10 columns, 0 mismatches. The table's observation equals `obs_c` on every day.
- **F147.4 The curve's gates (D98.5, D98.6).** Tracker self-check 6 of 6 (lead 47: 0, 0, 0.02, 0.0396; lead 48: 0, 0, 0, 0.02). Refit at 3 to 24: F139 cells 3,168 of 3,168, headline 2 of 2, n 6 of 6; F146 drift cells 1,584 of 1,584, headline 1.019044682206963. Lead 26, table's own observations, exact: YSDU B+D,L,R,T 1.2642703316294652, raw 1.4896583333333335; RNO 1.2741517803385958, 1.6134575342465751.
- **F147.5 Hourly scores (D98.8; MAE, degrees C; headline = mean of six).**

| leads | method | EGLC | LFPG | DSM | YSDU | RNO | KSFO | headline |
|---|---|---|---|---|---|---|---|---|
| 3-48 | raw GFS / baseline / curve | 1.0425 / 0.8375 / 0.8386 | 1.2336 / 0.9596 / 0.9544 | 1.8795 / 1.3231 / 1.3000 | 1.5226 / 1.2631 / 1.2304 | 2.2187 / 1.2284 / 1.2079 | 1.2923 / 1.0848 / 1.0037 | 1.5315 / 1.1161 / 1.0892 |
| 3-24 | same | 0.9725 / 0.7742 / 0.7742 | 1.1596 / 0.8937 / 0.8865 | 1.7582 / 1.2034 / 1.1775 | 1.4633 / 1.2149 / 1.1792 | 2.1717 / 1.1735 / 1.1474 | 1.2449 / 1.0390 / 0.9495 | 1.4617 / 1.0498 / 1.0190 |
| 25-48 | same | 1.1066 / 0.8957 / 0.8978 | 1.3015 / 1.0200 / 1.0167 | 1.9907 / 1.4329 / 1.4123 | 1.5769 / 1.3073 / 1.2775 | 2.2619 / 1.2788 / 1.2634 | 1.3357 / 1.1267 / 1.0535 | 1.5956 / 1.1769 / 1.1535 |

  Curve headline at 3 to 48, full precision: 1.0891748115841342. Fold level 3 to 48 (raw / baseline / curve): 2023-24 1.5231 / 1.1204 / 1.0910; 2024-25 1.5417 / 1.1294 / 1.1031; 2025-26 1.5297 / 1.0984 / 1.0734. D89.6's parts, curve against baseline at 25 to 48, descriptive only (D98.9): 1.985 percent lower; lower at 5 of 6 airports (not EGLC); 3 of 3 folds.
- **F147.6 Daily maximum (D98.10; common day set).** Days: EGLC 1,095, LFPG 1,094, DSM 1,095, YSDU 1,085, RNO 1,093, KSFO 1,093. MAE raw / baseline / curve: EGLC 0.9460 / 0.8479 / 0.8410; LFPG 1.1968 / 0.9780 / 0.9558; DSM 1.7297 / 1.2543 / 1.2240; YSDU 1.0861 / 1.0475 / 1.0268; RNO 1.5511 / 0.9490 / 0.9477; KSFO 1.6635 / 1.2489 / 1.2076; headline 1.3622 / 1.0543 / 1.0338. Fold level: 2023-24 1.4509 / 1.0508 / 1.0212; 2024-25 1.3405 / 1.0857 / 1.0630; 2025-26 1.2947 / 1.0260 / 1.0171. Curve mean error (obs minus forecast) from -0.031 (DSM) to +0.228 (KSFO); raw GFS +0.068 to +1.230. One cycle hour per airport (EGLC, LFPG 18z; DSM, RNO, KSFO 00z; YSDU 06z). Dropped: 15 days with too few usable hours (LFPG 1, YSDU 10, RNO 2, KSFO 2); 3 days whose cycle is before T0; 6 whose last hour is after 2026-07-31T23:00. Session 90's rule agrees with the table's usable days at all six airports. Incumbent (D98.10(g)): the curve's read-off maximum.
- **F147.7 Fits and outputs.** Fits: `--gate` 1,584 + 2; `--score` 3,312 (1,584 + 1,728), run twice (F147.8, item 2); fit time 227 s, run 282.9 s. Scores `data/processed/session104_curve_cv_scores.csv` (9,936 rows, `69ec86bf600fcb2c5b8ad0f8ec0cb8ed69adb314813e9ab1ee4b578f0fffa35e`); days `data/processed/session104_dailymax_days.csv` (6,570 rows, `65cb6d75d42ed8f1017c0117b1703f835c66ae5b1df1947f3535974112c37dd3`); meta `data/processed/session104_curve_cv.meta.txt` (`cb7950ae906d86a44fa64ded318b91abdc79d89c50030935ca208cf30d7ea398`). Predicted and corrected but never scored rows (D98.7): 2,490; rows using an error not before their cycle: 0.
- **F147.8 Readings for the owner.**
  1. At 25 to 48 the correction helps at five airports but not EGLC (0.8978 against 0.8957); at 3 to 48 too (0.8386 against 0.8375). Descriptive only (D98.9).
  2. The first `--score` run stopped at the daily-maximum cross-check: my new script gave session 90's rule every report as usable, but session 86's `parse_reports` also returns unusable ones. Fixed in this session's script only; the re-run's scores file is byte-equal to the first run's.
  3. The curve's daily maximum has a lower MAE than the baseline's at all six airports, but a larger positive mean error at YSDU, RNO and KSFO (+0.144, +0.156, +0.228): the read-off maximum runs low there.
  4. D98.10(b) gives one cycle hour per airport all year (the 4-hour arrival rule never crosses a cycle boundary at these six), so each airport's daily maximum is scored from a single run hour.
  5. Each model predicts its scored and no-observation rows in one call; F139 and F146 still reproduce exactly.
  6. The days file adds the first and last lead and a reason column for each maximum.
  7. Rows corrected with b = 0 at 25 to 48: 1,176, 1,180, 1,176 by fold (2 per cell at leads 25 to 47, 3 at 48); 2024-25's extra 4 not traced.
- **F147.9 What this did not do.** No build choice; no other weight, structure, feature, setting or daily-maximum method; no model saved; nothing from 2026-27; no non-development airport's observation; no network outside Step 2, no GRIB request; nothing installed; no existing script or data file edited; F138's table and `MLwx-pull/` unchanged. Nothing committed and no commit message written.

---

## 2026-10-11: Session 105 decision: F147 accepted, and two daily-maximum challengers (owner, planning chat)

**D99. Owner decisions, planning chat (after session 104): F147 accepted, and
two daily-maximum build choices under D98.10(g), judged in a fixed order,
with every choice fixed before any score.** Written at the start of session
105, before any other edit. No 2026-27 value has been read or scored.

- **D99.1 F147 accepted,** with all seven F147.8 readings: the correction is
  carried at leads 25 to 48 though it does not help EGLC there (reading 1,
  descriptive only, D98.9); the cross-check fix in session 104's own script,
  with a byte-equal re-run (reading 2); the read-off maximum running low at
  YSDU, RNO and KSFO (reading 3), which motivates this entry; one cycle hour
  per airport (reading 4); readings 5 and 6 as written; and reading 7's
  extra 4 rows at b = 0 in 2024-25, accepted untraced.
- **D99.2 What is tested.** Two challengers to the daily maximum, in this
  order: challenger 1, a daily-maximum model of its own (D82.5, using GFS's
  6-hour maximum, D88.5(e)); then challenger 2, a daily drift correction.
  Each is judged by D89.6 on D98.10(e)'s metric. Test 2 is run whatever test
  1 gives.
- **D99.3 Challenger 1: the daily-maximum model.**
  (a) Days, the cycle c, the observed maximum and folds: D98.10(a), (b) and
  (d), unchanged. H is the set of the day's whole UTC hours, all from cycle
  c (leads 4 to 33).
  (b) Inputs, from the development tables (F138's for leads up to 24, F147's
  for 25 to 48), all from cycle c:
  raw_max: the highest `temperature_grib_c` over H, which is D98.10(f)'s raw
  GFS read-off maximum;
  the peak hour p: the hour in H with the highest `temperature_grib_c`; on a
  tie, the earliest;
  gfs_tmax: the highest `tmax2m_c` over H (D88.5(e): bilinear, no elevation
  constant). Each value is GFS's maximum since its last 6-hour reset, so a
  window may begin a few hours before the day; accepted, the same
  everywhere;
  the other eight G15 columns (SPEC 8.8 G15, every column except `temp`) at
  hour p, as the table holds them (the season terms from p's valid time).
  The features, in this order: raw_max, gfs_tmax, then those eight in G15
  order. Ten features.
  (c) Target: observed maximum minus raw_max. Forecast: raw_max plus the
  model's prediction (the record's form, SPEC 8.8 G20).
  (d) Complete case: a day has inputs only if every hour of H has
  `temperature_grib_c` and `tmax2m_c`, and every one of the eight columns at
  p exists. A test day without inputs has no forecast from this method; it
  is counted and leaves the common day set.
  (e) One model per airport and fold, with the record's settings
  (`LGB_PARAMS`, unchanged; D21.4, D48.6). Training days: a usable observed
  maximum, complete inputs, and the day's last hour valid before the fold's
  T0 (D89.3's rule: only observations known when the first test cycle
  starts). Training days in ascending date (G19). Test days: the fold's days
  (D98.10(d)).
  (f) Only GFS values are inputs. The baseline's and the curve's forecasts on
  training days are in-sample, so neither is an input.
  (g) Nothing is tuned. This feature set and these settings are the only
  version scored.
- **D99.4 Test 1.** Incumbent: the curve's read-off maximum (D98.10(g)).
  Challenger: D99.3. D89.6 on D98.10(e)'s metric. The common day set: days
  with a usable observed maximum and a forecast maximum from raw GFS, the
  baseline, the curve and challenger 1. If D89.6 passes, M is challenger 1;
  otherwise M is the curve's read-off maximum.
- **D99.5 Challenger 2: daily drift.** M plus b, where b is a decaying
  average of M's own daily-maximum errors (observed maximum minus M's
  forecast): after each new error e, b = (1 - w) x b + w x e, w = 0.02
  (D97.4's value, not tuned). One tracker per airport and fold, starting at
  b = 0 at the fold's T0 (D97.7). It is updated by each test day of its fold
  with a usable observed maximum and a forecast from M, in ascending local
  date; a missing day is skipped. No look-ahead: the forecast for a day whose
  cycle is c uses only errors of days whose last hour is valid before c. So
  the newest usable error is normally two days earlier.
- **D99.6 Test 2.** Incumbent: M. Challenger: D99.5. D89.6 on the same common
  day set as test 1. If D89.6 passes, the daily maximum is M plus D99.5's
  correction; otherwise it is M.
- **D99.7 Nothing else.** No other feature set, setting, weight or method is
  scored in session 105. Any later variant is a new build choice, fixed in
  its own entry before its score.
- **D99.8 Reproduction first.** Before any fit: from
  `session104_dailymax_days.csv` (SHA-256 as F147.7), F147.6's per-airport
  MAEs and headline for raw GFS, the baseline and the curve, exactly. Then
  this session's day list (station, local date, cycle, fold, observed
  maximum) equals that file's, and raw_max equals its `raw_gfs_max` on every
  day where both exist. The curve's and the baseline's daily maxima are taken
  from that file; the hourly models are not refitted.
- **D99.9 Accepted consequence.** If challenger 1 is adopted, the daily
  maximum is no longer the highest hour of the curve, so the two can differ.
  This is accepted; the product shows both.
- **D99.10 Descriptive figures, not used by the rules.** Mean error per
  method and airport; challenger 1's training days per airport and fold and
  test days lost for missing inputs; challenger 2's b at the end of each fold
  per airport; MAE per method on F147.6's own day set beside the new common
  set.
- **D99.11 This is not a claim.** Every score here is a build-choice score
  (SPEC 2.5). Nothing from 2026-27 is read.
- **D99.12 Session 105's plan.** This entry; the reproduction; test 1; test
  2; tests; F148; the archive step. SPEC and RESULTS are not edited; the
  daily maximum's outcome goes into them with the next session that edits
  them.
- **D99.13 Live index.** Removed (archived), each settled and still binding
  by number: D47 (raw-data policy), D73, D77 and D79 (stage B's
  pre-registrations and reporting; frozen and gated, F128, F129), and F139
  (no longer the incumbent: D98.8; reproduced by F147.4). Added: D99 and
  F148. After session 105: D82, D88, D89, D93, D97, D98, F147, D99, F148.

---

## 2026-10-11: Session 105 finding: the daily maximum reproduced, and two daily-maximum challengers judged

**F148. Every score in this entry is a build-choice score, not a result (SPEC 2.5); none is a claim. D99 was recorded first. F147.6 was reproduced from session 104's days file (with an owner ruling at a stop), the day list and raw GFS maximum were rebuilt from the tables, and both challengers were judged by D89.6 on D98.10(e)'s metric. Neither passed. The daily maximum's incumbent after session 105 is unchanged: the curve's read-off maximum. Script (new): `scripts/session105_dailymax_cv.py` (`90c059ec5dc92d7653cd0e1d57aedc229fe85299bdfbb87c0399e07c9a54ddda`). Full real output: `notes/session-105-output.txt`. Run 2026-10-11. Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0.**

- **F148.1 The stop and the owner ruling (planning chat, 2026-10-11).** Before Step 1: the prompt's full-precision daily-maximum headline line is not in `notes/session-104-output.txt` (only 4 decimals) nor in either DECISIONS file. Ruling: (1) gate 1's full-precision comparison is dropped (the days file is tied to the record by its SHA-256, F147.7); (2) gate 1 checks at 4 decimals against F147.6 the per-airport MAEs of raw GFS, the baseline and the curve, the three headlines, the fold levels and the day counts; (3) the headlines are printed at full precision for this entry; (4) gates 2 and 3 unchanged; D99 not edited.
- **F148.2 The reproduction (D99.8). PASSED.** Gate 1: 36 values compared, 0 mismatches. Full precision: raw GFS 1.362196678488343, baseline 1.054275670219807, curve 1.0338223451337871. Gate 2: the day list rebuilt with session 104's `day_cycle`, `local_day`, `usable_day` and `fold_of` equals the file's (station, local date, cycle, fold, observed maximum) on 6,570 of 6,570 days. Gate 3: raw_max equals `raw_gfs_max` on 6,570 of 6,570 days, exact.
- **F148.3 Challenger 1's inputs and fits (D99.3).** Every local day in the window (1,955 or 1,956 per airport) has complete inputs; peak-hour ties broken 2 to 8 per airport. No test day lost, so D99.4's common day set equals F147.6's (1,085 to 1,095 days per airport). 18 fits with session 97's `fit_predict` (target observed maximum minus raw_max); training days 846 to 859 (2023-24), 1,209 to 1,225 (2024-25), 1,572 to 1,590 (2025-26); every training day's last hour before T0.
- **F148.4 Test 1 (D99.4; MAE, degrees C).**

| method | EGLC | LFPG | DSM | YSDU | RNO | KSFO | headline | folds 23-24 / 24-25 / 25-26 |
|---|---|---|---|---|---|---|---|---|
| raw GFS | 0.9460 | 1.1968 | 1.7297 | 1.0861 | 1.5511 | 1.6635 | 1.3622 | 1.4509 / 1.3405 / 1.2947 |
| baseline | 0.8479 | 0.9780 | 1.2543 | 1.0475 | 0.9490 | 1.2489 | 1.0543 | 1.0508 / 1.0857 / 1.0260 |
| curve | 0.8410 | 0.9558 | 1.2240 | 1.0268 | 0.9477 | 1.2076 | 1.0338 | 1.0212 / 1.0630 / 1.0171 |
| challenger 1 | 0.8424 | 1.0092 | 1.2642 | 1.0528 | 0.9566 | 1.2601 | 1.0642 | 1.0293 / 1.1073 / 1.0559 |

  D89.6, challenger 1 against the curve: (a) -2.940 percent; (b) 0 of 6; (c) 0 of 3. Not passed. **M = the curve's read-off maximum.**
- **F148.5 Test 2 (D99.6).** M plus b (w = 0.02, 18 trackers): EGLC 0.8467, LFPG 0.9570, DSM 1.2299, YSDU 1.0084, RNO 0.9485, KSFO 1.1928; headline 1.0306 (full precision 1.0305687073248007) against M's 1.0338; folds 1.0122 / 1.0588 / 1.0206. D89.6: (a) 0.315 percent; (b) 2 of 6 (YSDU, KSFO); (c) 2 of 3. Not passed. Errors used from a day whose last hour is not before the cycle: 0; common days corrected with b = 0: 36. b at the end of each fold from -0.301 (YSDU 2024-25) to +0.556 (KSFO 2025-26).
- **F148.6 The daily maximum's incumbent after session 105: the curve's read-off maximum** (unchanged, D98.10(g)). The hourly incumbent is unchanged (the curve).
- **F148.7 Mean error (observed minus forecast), descriptive.** Curve -0.031 (DSM) to +0.228 (KSFO); challenger 1 -0.380 (KSFO) to +0.039 (YSDU), negative at five airports; M plus b -0.014 to +0.024 at all six.
- **F148.8 Fits and outputs.** `--gate` 0 fits (54.6 s); `--score` 18 fits, run twice (F148.9, item 4): 50.7 s and 52.8 s, fit time 1.4 s and 1.3 s. Days `data/processed/session105_dailymax_cv_days.csv` (6,570 rows, `4b51d1ec8fc0832c0cddff83a34c7d5736bd820fdbd5f772820c04ec6276806e`); meta `data/processed/session105_dailymax_cv.meta.txt` (`9f38cfa4952f4ce4d8eccb7d44aa6d06c8c5e2103915b20a165d926fd2a20af8`).
- **F148.9 Readings for the owner.**
  1. Challenger 1 is worse than the curve at every airport and fold, and runs high at five airports (largest at KSFO and RNO). Fitting the maximum from one peak hour's inputs and about 850 to 1,600 days does not beat 100 hourly models plus the drift correction.
  2. Challenger 2 removes most of the curve's mean error at all six airports and helps most where the read-off maximum runs low (YSDU, KSFO), but its headline gain (0.315 percent) is far under D89.6's 1 percent, and it is worse at four airports.
  3. "From the first pull cycle" is read as: every local day whose first hour is valid on or after 2021-03-24T00:00 (the pull window's first hour). EGLC's 2021-03-24 uses cycle 2021-03-23T18, whose leads 6 to 29 lie in the window.
  4. The training-day rule was moved into a named function after the first `--score` run, so test 3 could call it; the re-run's days file is byte-equal (`cmp`), and the meta was written again.
  5. The tracker is updated by every fold day with a usable observed maximum and an M forecast; these are exactly the common days here.
  6. As F139.6 item 1: session 97's record-script import loads the session-48 module for its own use; this script never imports or calls the guard.
  7. Archive survey (Step 0): no code looks up D47, D73, D77, D79 or F139 by text; the lookups that exist (sessions 86 and 87) find F122, already archived.
- **F148.10 What this did not do.** No other daily-maximum variant, feature, setting or weight; no hourly refit or build choice; no model saved; nothing from 2026-27; no non-development airport's data; no network; nothing installed; no existing script or data file edited; `MLwx-stagec/` and `MLwx-pull*/` unchanged. SPEC.md and RESULTS.md not edited (D99.12). Nothing committed and no commit message written.
