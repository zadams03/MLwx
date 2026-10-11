# Session 106: stage C's lock, the claim airports' tables and the look script (D100)

Suggested model in Claude Code: Opus (a lock, a new table builder, a
scoring script and gates). A long session: follow CLAUDE.md's guardrails (a
checkpoint line after each step; stop rather than work around a failed
check; after any compaction, re-read CLAUDE.md, this prompt and your
checkpoints before going on).

## Purpose

Record D100, which freezes stage C's method and pre-registers its claim test
on the six claim airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN), before any of
their held-out data is read. Then build and check those airports' tables,
write the look script and gate it at the development airports, add tests,
write SPEC section 9, update SPEC 6 and RESULTS 7, and record F149.

**The look is not run in this session.** No claim airport's error, MAE,
mean error or any other statistic of a value is computed or printed for any
row or day from 2024-08-01 onward. The only statistics at claim airports are
D100.9(b)'s, on training rows (valid before 2024-08-01). Counts are allowed.
No 2026-27 value is read. No network.

## Read first

- `STATUS.md` in full; `SPEC.md` section 2 (including 2.5), 5.0, 5.2, 7.2's
  elevation bullet, and 8.8 (G2 to G7, G15, G19, G20, G24).
- `DECISIONS.md` (live) in full.
- Archived, by number (`grep -n '^\*\*F133\. '` and so on, then that entry
  only, by line range): F132 (F132.3, F132.4 only), F133.3, D97 (D97.4 to
  D97.7).
- Scripts, as needed for the step you are on: `scripts/session104_stagec_table_f025_048.py`
  and the parts of `scripts/session96_stagec_table.py` it uses (Step 2);
  `scripts/session104_curve_cv.py` (Step 3).

## Files this session may create or edit (scope list)

- New scripts: `scripts/session106_claim_table.py`,
  `scripts/session106_claim_look.py`.
- New data files: `data/processed/session106_claim_table.meta.txt`,
  `data/processed/session106_claim_counts.csv`.
- New: `notes/session-106-output.txt`.
- Edited: `tests/test_stagec.py` (new cases added; existing cases unchanged),
  `DECISIONS.md`, `DECISIONS-archive.md` (archive script only), `SPEC.md`
  and `RESULTS.md` (Step 5 only), `STATUS.md`.
- Untracked already: `docs/sessions/session-106.md` (this file; do not edit).
- Outside the repository: twelve new files in `MLwx-stagec/` (Step 2).
  `MLwx-pull/`, `MLwx-pull-f025-048/` and the existing files in
  `MLwx-stagec/` are read only.

Any other changed or new file is a scope breach: report it, do not hide it.
No existing script or data file is edited; frozen scripts (D62.3(a), D93.8)
never. CLAUDE.md, README.md and `docs/PROJECT-INSTRUCTIONS.md` not edited.

---

## Step 0: preflight

- `git status --porcelain` shows only `?? docs/sessions/session-106.md`.
- The last entries in DECISIONS.md are D99 and F148; no D100 or F149 in
  either file. None of the new files in the scope list exists, and no
  `MLwx-stagec/stagec_claim_*` file exists.
- SHA-256 equal to the record: `scripts/session104_curve_cv.py` (F147),
  `scripts/session104_stagec_table_f025_048.py` (F147),
  `scripts/session96_stagec_table.py` (F138), `data/processed/session90_airports.csv`
  (F132, `b53b689f...`), `data/processed/session104_curve_cv_scores.csv` and
  `data/processed/session104_dailymax_days.csv` (F147.7). Full values.
- The claim airports' observation files from session 90 (F132.4: six yearly
  pieces each, under `data/raw/`, with `.meta.txt`): list them; each file's
  SHA-256 equal to its `.meta.txt`. Report how they are named (IEM id: ORD
  for KORD). Do not open their values.
- The six claim rows of `session90_airports.csv`: print icao, iem_id,
  time_zone, height_diff_m and the elevation constant 7.429 x height_diff_m
  / 1000 (D100.3(b)). Check the formula: SPEC 3.4's KSFO model height 94.47
  m minus its elevation gives SPEC 5.2's +0.6944 at 4 decimals. Each claim
  airport is in the pull's positions file (F133.3) with the same four grid
  points and weights as `session90_airports.csv` (as sets).
- Free disk space: report it; stop if under 4 GB.
- Tests: all pass. Report the count.
- Stop if any of this differs.

## Step 1: record D100

Copy the block between `<<<D100-START>>>` and `<<<D100-END>>>` (markers
excluded) to the end of DECISIONS.md with `sed`, after a line `---` and a
blank line. Check byte equality with `diff` and `cmp`. Em-dashes: 0. Then
make D100.13's Live index change, except F149's line, which is added at the
end of the session.

<<<D100-START>>>
## 2026-10-11: Session 106 decision: F148 accepted, and stage C's lock (owner, planning chat)

**D100. Owner decisions, planning chat (after session 105): F148 accepted,
stage C's method frozen, and its claim test pre-registered on the six claim
airports (D82.7), every choice fixed before any of their held-out data is
read.** Written at the start of session 106, before any other edit. No claim
airport's value from 2024-08-01 onward has been read, and no 2026-27 value
has been read or scored. Where this entry restates D88, D97 or D98, it
restates them without change.

- **D100.1 F148 accepted,** with all nine F148.9 readings. The daily
  maximum stays the curve's read-off maximum (F148.6).
- **D100.2 Stage C is locked.** Its build choices are closed for this
  claim: D88.4 (the baseline), D94 (no pooled structure), D97 (the drift
  correction), D98.10 (the daily maximum read off the curve) and F148 (no
  daily-maximum challenger adopted). Nothing in D100.3 to D100.6 changes
  after any claim airport's data is built.
- **D100.3 The frozen method, at each claim airport.**
  (a) Data. Every GFS cycle in the two pulls (F137, F147) and forecast hours
  0 to 48; features by D88.5, the observation by D88.7, the complete-case
  rule as D88.6. Grid positions: IEM's airport position and its four grid
  points and weights in the pull's positions file (D83.3, F133.3).
  (b) Elevation constant. 7.429 degrees C per km (SPEC 7.2) times the
  airport's `height_diff_m` in `data/processed/session90_airports.csv`
  (model height minus station elevation, F132.3), added to temperature
  only, as at every airport (SPEC 5.2, 7.2). It is held in the same form
  (the same number of decimals) as the development airports' constants in
  the record's params files. Fixed now; never refit.
  (c) Models. D88.4's recipe: one LightGBM model per airport, cycle hour
  (00, 06, 12, 18 UTC) and lead 3 to 48 (184 models per airport), with the
  record's settings (`LGB_PARAMS`), the G15 column order and target (SPEC
  8.8 G15, G20). Trained once on the complete-case rows whose valid time is
  before 2024-08-01T00:00 UTC, in ascending cycle time (G19), then frozen
  for both looks. Never refit.
  (d) The curve. The baseline's forecast plus b, D97.4 to D97.7 unchanged:
  w = 0.02, one tracker per airport, cycle hour and lead, b = 0 at
  2024-08-01T00:00, updated by the baseline's own errors on scored rows
  (complete case, with an observation) in ascending valid time, using only
  errors whose valid time is before the forecast's cycle (D97.6, D98.5).
  The trackers run without a break through both looks, as they would live.
  Rows with complete features and no observation are predicted and
  corrected, never scored (D98.7).
  (e) The daily maximum. D98.10(a) to (c): the airport's own time zone
  (`time_zone` in `session90_airports.csv`), the cycle c with c + 4 hours
  at or before the local day's start, the forecast maximum read off the
  curve over the day's whole hours.
- **D100.4 The looks.** Two per airport (D71.6, D82.7(e)), each judged
  separately, each run once:
  look A, cycles 2024-08-01T00 to 2025-07-31T18;
  look B, cycles 2025-08-01T00 to 2026-07-31T18.
  A row or a local day belongs to the look of its cycle. Nothing valid
  after 2026-07-31T23:00 UTC is used.
- **D100.5 The bar,** per airport, per look, per output, at full precision;
  a tie fails (D79.2). The method's MAE must be lower than both:
  (a) raw GFS (the elevation-adjusted `temperature_grib_c`, SPEC 5.2), on
  the common set: for the hourly curve, the look's scored rows at leads 3
  to 48 (D89.5's common row set, pooled over cycle hours and leads); for the
  daily maximum, the look's days with a usable observed maximum and both
  forecast maxima (D98.10(e));
  (b) persistence, on the subset of that common set where persistence has a
  value, with the method's MAE taken on the same subset.
  Persistence, using only what was observed before the run's cycle c:
  hourly, for valid time v, the table's observation at v - 24k hours, k the
  smallest whole number of days with v - 24k before c (k = 1 at leads 3 to
  23, 2 at leads 24 to 47, 3 at lead 48); daily, the observed maximum
  (D98.10(a)) of the latest local day whose last hour is valid before c. If
  that value is missing, persistence has none for that row or day; no older
  value is used. (Unlike SPEC 8.5's day basis, both sides of (b) use the
  same rows, so the comparison is like for like.)
- **D100.6 Verdicts and the claim.** Per airport and output: PASS if both
  looks pass, SPLIT if one does, FAIL if neither (D71.6). Two outputs, the
  hourly curve and the daily maximum, each with its own verdict. The claim
  is stated per output as "passes at N of 6 new airports in both held-out
  years". Nothing is averaged across airports (SPEC 5.0). The write-up leads
  with the smallest margin, as a percentage (D79.1), over the 6 airports x
  2 looks x 2 bar halves, per output.
- **D100.7 Expectation, stated before any held-out value is seen.** Both
  outputs pass at all six airports in both looks.
- **D100.8 Descriptive, never part of the bar.** The baseline without the
  drift correction; mean errors; leads 3 to 24 and 25 to 48 separately; per
  cycle hour; days and rows counted and dropped by reason. No intervals are
  pre-registered.
- **D100.9 Checks before the look (session 106).** (a) The claim tables'
  builder reproduces F138's and F147's rows exactly at development
  airports. (b) A pipeline check on each claim airport's training rows only
  (valid before 2024-08-01): raw GFS mean error and MAE at leads 3 to 24 are
  printed, and only a gross value (either above 8 degrees C in size, a sign
  of a units or elevation bug) stops the session. Nothing is chosen, tuned
  or changed per airport from these figures. (c) The look script's gate:
  run at the six development airports with look A's windows, it reproduces
  session 104's 2024-25 fold exactly (every hourly cell's n and MAE for raw
  GFS, the baseline and the curve; every 2024-25 day's raw and curve
  maxima). Development airports' look B is run too, as a smoke test on spent
  years, descriptive only. (d) The look mode refuses to run in session 106.
- **D100.10 Caveats carried with the claim.** All data is GFS v16. Build
  choices were made on six other airports (D82.6); CYYZ, ZGSZ and NZWN have
  sea in their grid box (F132.3); MAE of an hourly curve and of a daily
  maximum are not comparable with the record's one-hour results.
- **D100.11 SPEC and RESULTS.** Session 106 writes SPEC section 9 (stage C,
  at its lock, D82.5), updates SPEC 6 and RESULTS 7 for D99, F148 and this
  lock, with the text in its prompt.
- **D100.12 Plan.** Session 106: this entry; the claim tables and their
  checks; the look script and its gate; tests; SPEC and RESULTS; F149.
  Session 107: the look, run once, and its finding.
- **D100.13 Live index.** Removed (archived, still binding by number): D97
  (restated in D100.3(d)), F147, D99 and F148 (settled; F148's outcome is
  restated in D100.1). Added: D100 and F149. After session 106: D82, D88,
  D89, D93, D98, D100, F149.
<<<D100-END>>>

## Step 2: the claim airports' tables (`scripts/session106_claim_table.py`)

It imports `session104_stagec_table_f025_048.py` and `session96_stagec_table.py`
(each after its SHA-256 check) and uses their functions unchanged wherever
they fit (report which). Where they are fixed to the development airports
(station lists, observation file names, elevation constants from the record's
params files), the new script takes the airport's ICAO code, IEM id, positions
and elevation constant as inputs instead; say exactly what was parameterised.
Same columns, column order, rounding, row rules and empty-cell reasons as
F138's files. Output, per claim airport, two files:
`MLwx-stagec/stagec_claim_f000_024_<ICAO>.csv.gz` and
`MLwx-stagec/stagec_claim_f025_048_<ICAO>.csv.gz`, rows in cycle then lead
order, written to a temporary name and linked, never overwriting. Modes, run
in turn, each stopping on a failed check:

- `--equiv`: the new code, given a development airport's own inputs (SPEC
  3.4 grid point, its params-file constant, its committed observation
  files), rebuilds EGLC and RNO for month 2022-01 at hours 0 to 24 and 25 to
  48 in memory: byte-equal to those rows of F138's and F147's files.
- `--build`: the twelve files. Print per airport and file: rows against the
  plan's count, complete-case rows split into before 2024-08-01 and from
  2024-08-01 (counts only), and empty cells by column and reason.
- `--sanity` (D100.9(b)): per claim airport, on complete-case rows at leads
  3 to 24 whose valid time is before 2024-08-01T00:00 only: n, raw GFS
  (`temperature_grib_c`) mean error (observation minus forecast) and MAE.
  The code must refuse any row valid on or after 2024-08-01T00:00 (test it
  with one such row). Stop if either value is above 8 degrees C in size.
  Nothing is changed because of these figures.
- `--records`: rebuild in memory and check byte-equality with the written
  files; rebuild one airport (NZWN) into a `mktemp -d` directory and check
  it byte-equal, then delete the directory; write
  `data/processed/session106_claim_counts.csv` and
  `data/processed/session106_claim_table.meta.txt` (inputs, elevation
  constants, script and every output with SHA-256).

## Step 3: the look script (`scripts/session106_claim_look.py`)

It checks `session104_curve_cv.py`'s SHA-256 before importing it, and uses
its functions (and session 97's and 103's through it) where they fit:
`fit_predict`, the tracker (`s103.track`), `correct`, `day_cycle`,
`local_day`, `usable_day`, and so on (report which). lightgbm imported
directly; the session-48 guard never imported or called by this script.
Recorded values (the twelve claim tables' SHA-256 from Step 2's meta, the
session 104 files' SHA-256) are constants, each with a comment naming its
entry (D98.2). Outputs written once and refused if present. Bytecode off.

It implements D100.3 to D100.8 exactly: frozen models trained on rows valid
before 2024-08-01T00:00 (184 per airport); trackers from b = 0 at
2024-08-01T00:00 running through both looks; rows with complete features
and no observation predicted and corrected, never scored; looks by cycle;
the daily maximum by D98.10 with each airport's time zone; persistence as
D100.5 (hourly and daily); the bar's two halves per airport, look and
output, strictly lower at full precision; PASS, SPLIT or FAIL per airport
and output; margins as D79.1; the smallest margin per output named first;
D100.8's descriptive figures.

Modes:
- `--gate` (D100.9(c)), on the six development airports only, from F138's
  and F147's tables: (1) the tracker self-check as session 104's gate 1;
  (2) look A reproduces session 104's fold 2024-25 exactly: every (airport,
  cycle hour, lead 3 to 48) cell's n and MAE for raw GFS, the baseline and
  the curve equal to `session104_curve_cv_scores.csv`'s `2024-25` rows, and
  every `2024-25` day of `session104_dailymax_days.csv` with equal cycle,
  observed maximum, raw GFS maximum and curve maximum; (3) look B and both
  looks' bar and persistence figures run as a smoke test and printed,
  labelled "development airports, spent years, descriptive only, not a
  result". Refuses any claim airport. Stop on any mismatch.
- `--look --confirm-look 107`: the claim airports only. **Not run in this
  session, in any form.** It refuses without `--confirm-look 107`, refuses
  any development airport, and refuses if any of its output files exists.
  When run (session 107) it writes `data/processed/session107_claim_scores.csv`
  (per airport, look, output, method, cycle hour and lead where they apply:
  n, MAE, mean error), `data/processed/session107_claim_days.csv` (one row
  per airport and local day) and `data/processed/session107_claim_verdicts.csv`,
  and prints the verdicts.
- `--guard-check`: shows `--look` refusing without the flag and with a
  development airport, and `--gate` refusing a claim airport, with no data
  read.
- `--meta`: writes the gate's meta into the output file only (no data file
  in this session).

Run `--guard-check`, then `--gate`.

## Step 4: tests (`tests/test_stagec.py`, new cases added)

Offline, standard `unittest`, temporary folders only, a few seconds each.

1. Hourly persistence (D100.5): for a cycle at 2024-01-10T00:00, leads 3,
   23, 24, 47 and 48 take the observation 1, 1, 2, 2 and 3 days before the
   valid time; a missing observation gives no persistence, never an older
   one.
2. Daily persistence: EGLC, local day 2024-01-15 (cycle 2024-01-14T18)
   takes the observed maximum of 2024-01-13; DSM, local day 2024-01-15
   (cycle 2024-01-15T00) takes 2024-01-13; an unusable day gives none.
3. Look assignment: cycles 2024-07-31T18, 2024-08-01T00, 2025-07-31T18,
   2025-08-01T00 and 2026-07-31T18 go to none, A, A, B and B.
4. The bar: a tie fails; a lower MAE on the raw GFS half with a higher MAE
   on the persistence half fails; PASS, SPLIT and FAIL from two looks.
5. The claim table constants in the look script equal the values in F149,
   found in either DECISIONS file (D98.2). (F149 is written at the end;
   this test passes only then, as F148's did.)
6. The elevation constant: 7.429 x 93.47 / 1000 gives 0.6944 at 4 decimals,
   and the six claim constants equal those in the table meta.

Run the whole suite; all must pass at the end. Report the new total.

## Step 5: SPEC and RESULTS (D100.11)

Do this step after F149 is recorded. Put the `git diff`s in the output file.

In `SPEC.md`:
(a) Section 6's stage C bullet: the two lines (exactly once; otherwise stop)

```
  maximum's metric is fixed (DECISIONS D98, F147). Its claim is judged
  on new airports only, drawn by the rule in DECISIONS D82.7.
```

become

```
  maximum's metric is fixed (DECISIONS D98, F147). The daily maximum is
  read off the curve: two challengers were not adopted (DECISIONS D99,
  F148). Stage C is locked, and its claim is pre-registered on the six
  new airports drawn by the rule in DECISIONS D82.7 (DECISIONS D100);
  its design is section 9.
```

(b) The two lines (exactly once)

```
*(The roadmap stages have no sections of their own yet, and will not
until the owner opens them. Stage 2 needs no section of its own,
```

become

```
*(Of the roadmap stages, only stage C has a section of its own (9),
written at its lock (DECISIONS D82.5, D100); the others will not until
the owner opens them. Stage 2 needs no section of its own,
```

(c) At the end of the file, after a blank line, a line `---` and a blank
line, the block between `<<<SPEC9-START>>>` and `<<<SPEC9-END>>>` (markers
excluded), copied with `sed` and checked byte-equal.

<<<SPEC9-START>>>
## 9. Stage C: the corrected curve and daily maximum (locked)

This section is stage C's design, written at its lock (DECISIONS D82.5,
D100). Stage C widens the target from one hour a day to every GFS run.

**9.1 What it forecasts.** From every GFS cycle (00, 06, 12 and 18 UTC), a
corrected 2 m temperature for every whole hour from 3 to 48 hours ahead (the
hourly curve), plus the daily maximum: the highest value of the curve over
the airport's local calendar day, from the latest run that has arrived
before the day starts (a run is taken to arrive 4 hours after its start).
Leads 0 to 2 are not forecast: they are already in the past when a run
arrives (DECISIONS D82, D88.6, D98.10).

**9.2 Data.** NOAA's GFS 0.25 degree GRIB archive, read by byte range at the
four grid points around each airport, for every cycle whose valid times lie
in 2021-03-24 to 2026-07-31 (all GFS v16), in two pulls: forecast hours 0 to
24 and 25 to 48 (DECISIONS D82.4, D87, F137, D98, F147). Features are the
recipe's (section 8) at every lead, with radiation and pressure tendency
defined for any lead (DECISIONS D88.5). The observation is the nearest
routine report within 15 minutes of the valid hour (DECISIONS D88.7).

**9.3 The method.** One model per airport, run hour and lead, with section
8's recipe and settings unchanged (the baseline, DECISIONS D88.4), plus a
correction for drifting bias: a running average of the baseline's own
recent errors, weight 0.02 per new error, using only errors observed before
the run starts (DECISIONS D97, F146). The daily maximum is read off this
curve (DECISIONS D98.10).

**9.4 How it was chosen.** By time-ordered cross-validation on the six
development airports (EGLC, LFPG, DSM, YSDU, RNO, KSFO), three test years
2023-24 to 2025-26, with a fixed rule: a challenger replaces the incumbent
only if its average MAE is more than 1 percent lower, and lower at 4 of 6
airports and in 2 of 3 years (DECISIONS D89). Tried and not adopted: two
pooled model structures (DECISIONS D94, F143), a daily-maximum model of its
own and a daily drift correction on the maximum (DECISIONS D99, F148).
Adopted: the drift correction on the curve (DECISIONS D97, F146). These are
build choices, never results (2.5).

**9.5 The claim test (pre-registered, DECISIONS D100).** On the six claim
airports drawn by DECISIONS D82.7 (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN),
never used for any build choice. At each, the method is trained once on
data before 2024-08-01 and frozen, and the drift correction runs on through
the test. Two looks, each run once: look A tests runs from 2024-08-01 to
2025-07-31, look B from 2025-08-01 to 2026-07-31. Per look and per output
(hourly curve at leads 3 to 48; daily maximum), the method's MAE must be
lower than raw GFS (elevation-adjusted, 5.2) and lower than persistence
(the latest value at the same hour, or the latest daily maximum, already
observed when the run starts), on the same rows. An airport passes an
output only if both looks pass (5.0). The claim is stated per output as
"passes at N of 6 new airports in both held-out years"; nothing is averaged
across airports. Expected: both outputs pass at all six. The result will be
recorded here and in RESULTS.md once the look is run.

**9.6 Caveats.** All data is GFS v16; GFS v17 is stage B's and stage F's
question. Three claim airports have sea in their grid box (CYYZ, ZGSZ,
NZWN). The MAE of an hourly curve or of a daily maximum is not comparable
with sections 3 to 8's one-hour results.
<<<SPEC9-END>>>

In `RESULTS.md`, section 7's roadmap paragraph, the three lines (exactly
once)

```
  F147). Stage
  C's claim will be judged on six new airports (EDDM, KORD, CYYZ, ZGSZ,
  ZUCK, NZWN), fixed before any of their held-out data is read. Stages D
```

become

```
  F147). Two ways to improve the daily maximum were tested and not
  adopted (DECISIONS D99, F148). Stage C is now locked: its claim test on
  six new airports (EDDM, KORD, CYYZ, ZGSZ, ZUCK, NZWN) is pre-registered,
  before any of their held-out data was read (DECISIONS D100, SPEC 9).
  Stages D
```

and in the closing note, `and after session 104 (DECISIONS D98).` becomes
`and after session 104 (DECISIONS D98) and after session 106 (DECISIONS
D100).` (on one line, as the original). Nothing else in either file changes.

## End of session

Follow CLAUDE.md's end-of-session steps, with these details:

- **`notes/session-106-output.txt`** begins with a summary of at most 30
  lines, then the checkpoints, then the full output of every run (keep the
  full `--gate` log: session 104's was missing, F148.1). The end-of-session
  consistency findings go in it too.
- **F149** (at most about 40 lines, D93.10): the observation files and
  elevation constants; the tables (rows, complete-case counts before and
  from 2024-08-01, empty cells, the equivalence check, the twelve files'
  SHA-256 in full, since the look script holds them as constants); the
  training-row sanity figures; the look script's gate (cells and days
  compared, mismatches) and that the development airports' look B ran as a
  smoke test (its figures are in the output file, not in F149); the guard
  check; that `--look` was not run; scripts' and outputs' SHA-256; readings
  for the owner; what was not done. Then add `- F149: session 106's
  finding.` to the Live index after D100.
- **Archive step:** `python3 scripts/archive_decisions.py --apply --session
  106`. D97, F147, D99 and F148 should move; report what moved.
- **Size check** (DECISIONS.md under 80,000 bytes), citations check, scope
  check. Report the size of the twelve new table files.
- **Tests:** run the suite at the end; all must pass.
- **STATUS.md:** current-only snapshot. Stage C is locked (D100); the claim
  tables are built and checked; the look script is gated and not run; the
  expectation (D100.7). Carry stage B, MOSMIX and MMMX; drop the SPEC/RESULTS
  carried item (done). **Next planning session:** Review session 106. The
  owner commits and pushes (`git commit -F docs/commits/commit-106.txt`) and
  the planning chat syncs Project knowledge. Then plan session 107: stage
  C's look on the six claim airports, run once (D100.12).

## What this session must not do

Run `--look` in any form; compute or print any statistic of a claim
airport's value from 2024-08-01 onward; change anything in D100 or the
method after Step 2's figures; choose, tune or change anything per airport;
save a model; read anything from 2026-27; use the network; install
anything; edit any existing script or data file; change `MLwx-pull*/` or the
existing `MLwx-stagec/` files; edit SPEC.md or RESULTS.md beyond Step 5.
Nothing committed and no commit message written.
