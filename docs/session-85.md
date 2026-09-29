# Session 85: the NBM/MOS comparison and its outcome rule (stage A)

Stage A's last item is a comparison against operational post-processed
forecasts: the National Blend of Models (NBM) and NWS MOS, at DSM, RNO and
KSFO (D72.3). Its outcome rule must be fixed in writing before the
comparison is looked at (D72.7). The owner has also decided the carried
F123.9 question and whether 2026-27 gets a pre-registered NBM/MOS test
(D73.8). This session:

1. records **D77** (the outcome rule, the F123.9 decision and the 2026-27
   pre-registration), before any network call or data read;
2. runs a **reproduction gate** on the recorded predictions it will use;
3. **pulls** NBM and GFS MOS point forecasts for the spent years only;
4. runs the **comparison** and applies D77's outcome rule;
5. records **F127**, makes two small SPEC edits, and does the
   end-of-session steps.

It **changes no verdict**. It **decides no direction**: if the rule's
band is "mixed" or "lose", the owner decides in writing after review
(D77.4). It **writes no 2026-27 code** and reads no 2026-27 value.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 value from any source.** No request may ask for, and no
  script may keep, any value valid on or after 2026-08-01. Check every
  valid time before reading any value. If any valid time after
  2026-07-31T23:00 UTC appears, discard it without reading its value,
  report that it happened, and stop that sub-step.
- **Recorded predictions only.** The model predictions compared are
  F109's `B+D,L,R,T` predictions at DSM and RNO (2024-25) and F119's
  saved KSFO predictions (looks A and B). Nothing is refit differently,
  retuned, reselected or re-locked. No other year and no other airport.
- **Do not edit, bypass or disable the reserved-year guard (D51) or any
  other guard in any existing script.** New code may import functions
  from existing scripts but must not change them. If refitting needs a
  guarded path that cannot be used without changing it, stop and report.
- **Do not edit any existing script.** Write exactly one new script:
  `scripts/session85_nbm_mos_comparison.py`, with three modes, `--gate`,
  `--pull` and `--compare`, each run once (a `--pull` re-run after a
  network failure is allowed and must be reported).
- **Writes under `data/` are limited to exactly these new paths:**
  - `data/raw/iem_mos/session85/` (raw MOS responses, unchanged, plus a
    `.meta.txt` with each exact query and the pull time);
  - `data/processed/session85_competitor_points.csv` and its
    `data/processed/session85_competitor_points.meta.txt`.

  No GRIB file is kept. NBM GRIB bytes go to a temporary directory
  outside the repo and are deleted after each value is extracted. Do not
  touch `data/models/`.
- **No installs, no accounts.** Use only what is installed (eccodes is
  already used by the GRIB pipeline).
- Edit `SPEC.md` only as Step 5 says. Do not edit `CLAUDE.md`,
  `RESULTS.md`, `README.md` or `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-85.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D76 and F126, and that no
   D77 or F127 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that none of these exist:
   `scripts/session85_nbm_mos_comparison.py`,
   `data/raw/iem_mos/session85/`,
   `data/processed/session85_competitor_points.csv`,
   `notes/session-85-output.txt`. If any exists, stop and report.
4. Read: D71 (D71.5), D72 (D72.3, D72.7, D72.8), D73, F122, F123
   (F123.2 to F123.4, F123.9), F125 (F125.1, F125.2, F125.6, F125.7) and
   D76 in DECISIONS.md. In DECISIONS-archive.md: F5 and F89 (lead
   convention), D58 item 6, D70, F109 and F119. SPEC 3.4, 5, 8.5 and
   8.7. Read, without running or editing,
   `scripts/session82_source_probe.py` (for the NBM bucket layout and the
   IEM MOS endpoint it used) and `scripts/session83_confidence_intervals.py`
   (for how F125 refit F109 and read KSFO's saved predictions).

---

## Step 1: record D77 (before any other edit, network call or data read)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 85 decision: the NBM/MOS comparison, its outcome rule and the 2026-27 NBM/MOS test (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
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
```

---

## Step 2: the reproduction gate (`--gate`, offline)

1. **DSM and RNO (F109).** Refit exactly as F125.1 did: import functions
   from `scripts/session62_reserved_confirm.py` (check its SHA-256
   against D70.2 first) and follow `run_confirm()` step by step, with its
   guards as it applies them. Refit only DSM and RNO, and only the
   `B+D,L,R,T` model.
2. **KSFO (F119).** Read `data/processed/session78_ksfo_looks_predictions.csv`.
   Check its SHA-256 against F119.4. No refit.
3. **Gate.** For each of the four airport-looks, recompute the model's
   MAE and raw GFS's MAE on the recorded test days and compare with the
   recorded figures: at full precision where
   `session63_reserved_confirm_grid.csv` (F109) or
   `session78_ksfo_looks_grid.csv` (F119) records them, and otherwise at
   the entry's printed precision. Print both, and the day counts. An
   airport-look that fails gets **no comparison**; report it and
   continue with the others.
4. Keep, in memory only for `--compare`, each passing airport-look's
   per-day rows: date, observation, model prediction, raw GFS. (The
   script may recompute them in `--compare` by the same route instead.)
   Write nothing under `data/` in this step.

---

## Step 3: the pull (`--pull`)

### 3.1 NBM

- Source: the AWS bucket `noaa-nbm-grib2-pds`, anonymous HTTPS, using
  the layout session 82's probe used (`blend.YYYYMMDD/HH/core/`,
  `blend.tHHz.core.fFFF.co.grib2` and its `.idx`). Confirm the pattern
  from that script; if it differs, stop and report.
- Files: for each target day D in each airport-look's window, the 18z
  cycle on D-1, at f024 (DSM) or f026 (RNO, KSFO). RNO and KSFO look A
  share files: fetch each file once.
- Message: from the `.idx`, the one line that is exactly
  `TMP:2 m above ground:<lead> hour fcst:` with nothing after it. If
  zero or several lines match, skip that file, count it and report it.
  Fetch that message only, by byte range.
- Checks for every message, before reading its values: valid time equals
  the target (D at the target hour) and is on or before
  2026-07-31T23:00 UTC; units are K.
- Value: the nearest grid point to the station (SPEC 3.4 latitude and
  longitude), via eccodes' nearest-point lookup. Record that grid
  point's latitude, longitude and distance per airport, and report if it
  ever changes across the window.
- **Size trial first.** Fetch 3 messages, report the bytes per message
  and the projected total. If the projected total exceeds 20 GB, stop
  and report.
- Version check: print the `.idx` line count of the f026 18z file on
  2025-05-26 and on 2025-05-28, and report whether anything in the
  message you use differs (name, units, grid). Report only.
- Retry a failed request at most 3 times, politely spaced. A missing
  file is counted, not filled.

### 3.2 GFS MOS (MAV), DSM only

- Source: the IEM MOS endpoint session 82's probe used. Station `KDSM`,
  model GFS (MAV).
- Runs: the 18z run on D-1, for each D in 2024-08-01..2025-07-31. Value:
  the `tmp` projection valid at D 18:00 UTC.
- If IEM has no 18z MAV runs, stop this sub-step and report. Do not
  substitute another cycle.
- Apply the valid-time guard to every returned projection before
  reading any value.
- Save each raw response unchanged under `data/raw/iem_mos/session85/`
  with a `.meta.txt` recording each exact query and the pull time.

### 3.3 The points file

Write `data/processed/session85_competitor_points.csv`, one row per
airport-look and target day: airport, look, target date, competitor
(`nbm` or `mav`), cycle, lead, valid time, value in degC, and, for NBM,
the grid point latitude and longitude. Write its `.meta.txt`: pull
date, bucket, every file URL with its byte range and `.idx` line (or a
pointer to an equivalent listing in the output file), and the counts of
missing files and messages. Print the SHA-256 of the CSV.

---

## Step 4: the comparison (`--compare`, offline)

For each airport-look that passed the gate, in the order DSM, RNO, KSFO
look A, KSFO look B, then MAV at DSM:

1. **Day set:** the recorded model test days on which the competitor
   value is present. Print the recorded day count, the competitor's
   missing count, and n.
2. **On that day set:** MAE of the model, the competitor and raw GFS;
   mean error (forecast minus observation) of each.
3. **d and skill against the competitor,** with F125's moving-block
   bootstrap: order days by date; blocks of 7 consecutive entries;
   starts uniform on 0..n-7; ceil(n/7) blocks truncated to n; the same
   resampled days for model and competitor; 10,000 resamples;
   `numpy.random.default_rng(85)`, one generator for the whole run, in
   the order above. Report the point estimates and the 2.5th and 97.5th
   percentiles, and whether d's interval lies wholly above zero.
4. **NBM version segments** (D77.7 dates): MAE of the model and of NBM
   per segment, with n. Point estimates only.
5. **Outcome band:** apply D77.4 to the four NBM point estimates and
   print the band (win, mixed or lose), with the four comparisons it
   rests on.

Put the full real output of Steps 2 to 4 in `notes/session-85-output.txt`.

---

## Step 5: records and SPEC

1. **F127** in DECISIONS.md, after D77, under a dated heading
   `## <run date>: Session 85 finding: the NBM/MOS comparison on the spent years`.
   It gives: the Step 0 and Step 1 results; the gate result per
   airport-look; the pull counts (files, messages, missing, bytes), the
   NBM grid points and the version check; one compact table with
   columns: airport-look, competitor, n, MAE model, MAE competitor, MAE
   raw GFS, d (degC) with its 95% interval, skill (%) with its 95%
   interval, d wholly above zero (yes/no); the per-segment table; the
   band under D77.4; and these statements, verbatim:
   - "This comparison uses spent years and recorded predictions. It is
     descriptive and decides direction only (D72.7, D77.3). It changes no
     verdict."
   - "These intervals describe day-to-day sampling within one test year
     only. They do not capture year-to-year variation."
   - "MAV values are whole degrees F, used as issued; the rounding is not
     corrected (D77.2)."
   - "Both years use NBM before its 2026-07-28 temperature fix (v5.0.14,
     D77.7)."

   Then a "what this did not do" list: no refit other than F109's
   recorded route, no retune, reselect or re-lock; no 2026-27 value; no
   GRIB kept; no direction decided; no verdict changed; nothing
   committed.
2. **SPEC 6, stage A bullet.** Replace the sentence
   "The comparison and its outcome rule are still to come (D72.7,
   D76.3)." (in SPEC it runs across a line break; match it that way)
   with: "The outcome rule is fixed in DECISIONS D77, and the
   comparison on the spent years is recorded in F127."
3. **SPEC 6, stage B bullet.** After its last sentence ("... and its
   models are frozen (F122)."), add: "A comparison of those frozen models
   against NBM, and against GFS MOS at DSM, on 2026-27 is pre-registered
   in DECISIONS D77.6."

Nothing else in SPEC changes.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include: the forward test's state (D73, F122) and that
   D73.8's hold-rule condition is now met by D77.6; the 2026-27 NBM/MOS
   test in one or two lines (D77.6); F127 in brief (the table's key
   figures and the band); and these carried items:
   - **GFS v17 (D77.8).** Still no Service Change Notice as of
     2026-09-29. Re-check at each planning session. The go-live date
     sets period A's length. PNS 26-30's statement that the 0.25 degree
     GRIB2 files remain is to be confirmed against the SCN (D73.4).
   - **Direction decision (D77.4)**, only if the band is "mixed" or
     "lose": the owner's written choice, due before stage C's lock.
   - The remaining stage A/B uncertainties from session 84's STATUS that
     this session did not close. The NBM v4.3 date disagreement is
     closed by D77.7.

   It must end with: "**Next planning session:** Review session 85. If
   F127's band is mixed or lose, the owner records the direction decision
   (D77.4). Then design session 86: the next step in stage B or C (the
   2026-27 data-build and scoring scripts, or stage C's start)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-85-output.txt`** as
   well as reporting them in chat (D74.2).
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, F123,
   D76, D77 and F127 stay live. Report what moved and why.
5. Stop and wait for review. Do not commit. Do not write a commit
   message.
