# Session 87: the 2026-27 scoring script and the NBM and MAV fetch (stage B)

Session 86 wrote the 2026-27 data-build script and passed its gate (F128).
This session writes the other two scripts D78.7 calls for, so that all
three are committed before any 2026-27 row is built (D73.8). This session:

1. records **D79** (clarifications of how D73 and D77.6 are reported, and
   a GFS v17 note), before any other edit, network call or data read;
2. writes **`scripts/session87_forward_competitors.py`**, which fetches
   D77.6's NBM and GFS MOS (MAV) values for 2026-27, and gates it on
   spent-year days;
3. writes **`scripts/session87_forward_score.py`**, which scores D73 and
   D77.6, and gates it by reproducing recorded results;
4. records **F129**, edits SPEC 6, and does the end-of-session steps.

**`--fetch` and `--score` are written but never run in this session.** No
2026-27 value is requested, read, built or scored.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 value from any source.** No request may ask for, and no
  code may read, any NBM message, MOS projection, GRIB message or
  observation valid on or after 2026-08-01T00:00 UTC. Check every valid
  time before reading any value. If one appears, discard it without
  reading its value, report it, and stop that step.
- **Never run `--fetch` or `--score`, in any form, with any arguments.**
  Their guards are tested only through each script's `--guard-check`,
  which makes no network call and reads no data file.
- **Model use.** The only fits allowed are in the scoring gate's step G2:
  DSM and RNO refit by F127.2's route (F109's recorded route,
  `B+D,L,R,T` only), for verification only. The frozen F122 models are
  only loaded and used to predict. **No error, MAE, bias or skill is
  computed on the frozen models' training rows** (F122.6), and nothing is
  computed on any 2026-27 row.
- **Do not edit any existing script, and do not edit, bypass or disable
  any guard in one.** New code may import pure functions from earlier
  scripts read-only (checking the script's SHA-256 first, where DECISIONS
  or a notes output file records one), or copy them. If importing a
  script runs code, copy the function instead. Report every function
  imported or copied, with its source file and lines.
- **Write exactly two new scripts:** `scripts/session87_forward_competitors.py`
  and `scripts/session87_forward_score.py`, with the modes in Steps 2
  and 3.
- **Writes under `data/`: none.** Gate bytes and responses go to a
  temporary directory outside the repo and are deleted when each gate
  ends. Do not touch `data/models/` except to read it. Do not open the
  two A67-15 DSM files (D62.7, D73.10).
- **No installs, no accounts.**
- Edit `SPEC.md` only as Step 5 says. Do not edit `RESULTS.md`,
  `CLAUDE.md`, `README.md` or `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-87.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D78 and F128, and that no
   D79 or F129 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that neither new script nor
   `notes/session-87-output.txt` exists. Confirm that no file named
   `forward2627_*` exists under `data/`. If any exists, stop and report.
4. Check these SHA-256 values. If any differs, stop and report:
   - `data/processed/session81_training_set.csv` and
     `data/models/session81/manifest.json` against F122;
   - the twelve model files under `data/models/session81/` against F122.5;
   - `data/processed/session85_competitor_points.csv` against F127.3;
   - `data/processed/session78_ksfo_looks_predictions.csv` against F119.4;
   - `scripts/session62_reserved_confirm.py` against D70.2;
   - `scripts/session86_forward_build.py` against the value in
     `notes/session-86-output.txt`.
5. Read: D62, D71.5, D73, F122, F125, D77, F127, D78 and F128 in
   DECISIONS.md; D70 and F119 in DECISIONS-archive.md; SPEC 3.4, 5.2,
   5.3, 8.5, 8.7 and 8.8. Read (do not run)
   `scripts/session85_nbm_mos_comparison.py`,
   `scripts/session83_confidence_intervals.py` and
   `scripts/session86_forward_build.py`.

---

## Step 1: record D79 (before any other edit, network call or data read)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 87 decision: how the 2026-27 tests are reported, and the scoring and competitor scripts (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
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
```

---

## Step 2: `scripts/session87_forward_competitors.py`

New code, meeting SPEC 8.7's build requirements where they apply
(non-finite values rejected at load, dropped and counted; each message's
full valid date and hour checked; row counts compared with the expected
full count; no writes to committed files).

### 2.1 What it fetches (D77.1, D77.2)

For each target day D of a period:
- **NBM** CONUS `core` 2 m temperature at DSM, RNO and KSFO (station code
  `SFO`): the 18z run of D-1, forecast hour 24 at DSM (valid 18:00 UTC on
  D) and 26 at RNO and SFO (valid 20:00 UTC on D). Value at the grid
  point nearest the station's SPEC 3.4 position (eccodes nearest
  neighbour, no interpolation), K converted to degC. Byte range from the
  `.idx`, with the same checks as session 85 (valid time, units K, `2t`,
  `.idx` date).
- **MAV** at DSM only: IEM `api/1/mos.json`, station KDSM, model GFS, the
  18z run of D-1, the projection valid 18:00 UTC on D, `tmp` in whole degF
  used as issued and converted to degC exactly. Matching is on UTC fields,
  checked as session 85 did. Only that one projection is read. Other
  projections in a response are never read, printed or used; the raw
  response is saved unchanged (SPEC 2.3).
- Take the fetch logic from `scripts/session85_nbm_mos_comparison.py`
  (copy or import read-only), and the station positions from SPEC 3.4.
  Report every function copied or imported.

Missing values are dropped and counted by reason (no `.idx`, no file,
no matching `.idx` line, failed check, missing value, no MAV run, no
projection). A failed request is retried at most 3 times, politely
spaced. GRIB bytes go to a temporary directory outside the repo and are
deleted after each value is read.

### 2.2 Periods

Target days per period are computed exactly as
`scripts/session86_forward_build.py` computes them (copy or import its
function): period A starts on 2026-08-01, and each airport's last
period-A day is the last day whose GFS cycle (floor(H/6)x6 UTC on D-1,
SPEC 7.2) is before the first operational v17 cycle. Period B runs from
the next day to 2027-07-31. The competitor days for an airport are that
airport's GFS-defined days (D77.2).

### 2.3 `--guard-check` (offline: no network, no data read)

Calls the guards only and prints each outcome:
- gate date 2026-07-31 allowed; gate date 2026-08-01 refused;
- `--fetch` with neither `--first-v17-cycle` nor `--no-v17`: refused;
- `--fetch --period B --no-v17`: refused;
- `--fetch` whose period's last target day plus 3 days is after the run
  date (UTC): refused (use first v17 cycle 2026-11-15T00, run date
  2026-09-30);
- `--fetch` with any target date on or after 2027-08-01: refused;
- `--fetch` when any of its output files already exists: refused
  (simulate in a temporary directory outside the repo).

### 2.4 `--gate` (spent years only)

Hard-stops on any target date after 2026-07-31.

**Sample (fixed; do not change it):**
- DSM (NBM and MAV) and RNO (NBM): 2024-08-01, 2024-11-12, 2025-02-18,
  2025-05-28, 2025-07-31.
- SFO (NBM): those five dates, plus 2025-08-01, 2025-09-03, 2026-04-22,
  2026-05-06, 2026-07-29 and 2026-07-31.

That is 21 NBM values and 5 MAV values. It covers NBM v4.2, v4.3, v5.0
and v5.0.14 (D77.7, F127.5).

Fetch each with the Step 2.1 code, into the temporary directory. Compare
with the same row of `data/processed/session85_competitor_points.csv`:
the value, **exact equality at its stored precision**, and the NBM grid
point (F127.3's table). Also report, per NBM file read, the number of
`.idx` lines and the 2 m temperature message's name, units, level, grid
and packing, as F127.3's version check did.

If there is a mismatch from a bug in the new script, fix it and re-run
the whole gate; report every run. Do not change the sample or the pass
rule. If a mismatch cannot be traced to a bug (for example the archived
bytes differ), stop and report.

**Writer exercise.** In a temporary directory outside the repo, the
`--fetch` writers write the gate's points, manifest and raw MAV
responses. Read the points back and check they equal the fetched values.
Check that a second write is refused. Delete the directory.

### 2.5 `--fetch` (written, never run this session)

- Arguments: `--period A` or `--period B`; one of `--first-v17-cycle
  YYYY-MM-DDTHH` or `--no-v17` (period A only); `--decision <entry>`,
  printed in the output.
- Refuses to run until the run date (UTC) is at least 3 days after the
  period's last target day at every airport.
- Writes only these new files, and refuses to run if any exists:
  - `data/processed/forward2627_period{A,B}_competitor_points.csv` and its
    `.meta.txt` (pull date, bucket, every NBM URL with its byte range and
    `.idx` line, every MAV query, and the counts);
  - `data/raw/diagnostics/forward2627/period{A,B}_nbm_manifest.csv` and
    `period{A,B}_competitor_drop_log.csv`;
  - `data/raw/iem_mos/forward2627/period{A,B}/` (raw MAV responses,
    unchanged, each with a `.meta.txt` giving the query and pull time).
- Prints counts only: values per airport and competitor against the
  expected full count, drops by reason, and the NBM grid point per
  station. **It never prints a 2026-27 value.**

---

## Step 3: `scripts/session87_forward_score.py`

### 3.1 What it computes (D73.5, D73.6, D77.6, D79)

Inputs for a period: the rows file written by the build script
(`data/processed/forward2627_period{A,B}_rows.csv`), the competitor
points file (Step 2.5), and the frozen F122 models and mean-bias
constants.

- **Predictions.** The model's target is the observation minus
  `temperature_grib_c` (SPEC 8.8 G20). So a model's forecast is
  `temperature_grib_c` plus its prediction, where the prediction is made
  on a float64 array of the G15 columns in order (the first five for `B`),
  with no column names (G14, G15). Raw GFS (GRIB) is
  `temperature_grib_c`. The mean-bias reference is `temperature_grib_c`
  plus the airport's F122.5 constant. Persistence is the previous-day
  observation.
- **D73.** Per airport and period, with D73.5's day basis: complete-case
  rows for the models, raw GFS and the mean-bias reference; the subset
  with a previous-day observation for persistence. Report row counts
  against the period's full expected count. The verdict is PASS if the
  `B+D,L,R,T` MAE is strictly lower than both raw GFS's and persistence's
  (D79.2), otherwise FAIL, or "no verdict (0 days)" (D79.3). Report both
  bar margins (D79.1), and lead with the smallest. The `B` model and the
  mean-bias reference are descriptive rungs only.
- **D77.6.** DSM, RNO and SFO against NBM; DSM against MAV. Day set: D73's
  complete-case days on which the competitor value is present. PASS if
  the frozen `B+D,L,R,T` MAE is strictly lower than the competitor's,
  otherwise FAIL; void if the competitor has no value in the period.
  Descriptive, on the same days: `B` and raw GFS MAE, mean errors, d,
  skill, and D79.5's intervals. Lead with the smallest margin (D79.1).
- **Labels (D79.4).** Each verdict carries its first and last date and
  its months. `--nbm-versions` and `--mav-versions` take label text
  copied from the DECISIONS entry, and the script prints it verbatim.
- MAE is the numpy mean at full precision, printed to 4 decimals and
  stored unrounded (SPEC 8.8 G24).

### 3.2 Integrity checks inside `--score`

It stops before computing anything if any of the following is true:
- any of the twelve model files or `manifest.json` differs from F122.5;
- the rows file's or points file's SHA-256 differs from the value passed
  in `--rows-sha256` or `--points-sha256` (taken from the finding that
  recorded that build or fetch);
- any row's date is outside the period or in the wrong period for its
  airport;
- a station or column is missing.

### 3.3 `--guard-check` (offline: no network, no data read)

Calls the guards only and prints each outcome:
- `--score` with neither `--first-v17-cycle` nor `--no-v17`: refused;
- `--score --period B --no-v17`: refused;
- `--score --period B` when the period-B rows file does not exist:
  refused;
- `--score` whose period's last target day plus 3 days is after the run
  date: refused (first v17 cycle 2026-11-15T00, run date 2026-09-30);
- any target date on or after 2027-08-01: refused;
- an output file already exists: refused (temporary directory);
- a rows file whose SHA-256 differs from `--rows-sha256`: refused (a
  small temporary file).

### 3.4 `--gate` (recorded results only)

**G1. F119.3 (KSFO, both looks).** From
`data/processed/session78_ksfo_looks_predictions.csv` (saved predictions,
as F125.1 used them), plus whatever the scoring core needs from the files
`session77_ksfo_looks.py` reads, run the new D73 scoring core. Compare
with `data/processed/session78_ksfo_looks_grid.csv` at full precision:
every MAE the grid records (raw GFS, persistence, `B`, `B+D,L,R,T`, and
the mean-bias reference if recorded), and every day count (364/363 and
365/365). Also check both verdicts are PASS and the margins equal
F119.3's percentages to 2 decimals. Report the source of every column
used.

**G2. F127.4 (all five rows).** Run the new D77.6 core and interval
function on F127's inputs: KSFO looks A and B from saved predictions;
DSM and RNO refit by F127.2's route (F125.1's F109 route: functions
imported from `session62_reserved_confirm.py` after its SHA-256 check,
`run_confirm()`'s steps and both guards, `B+D,L,R,T` only); competitor
values from `session85_competitor_points.csv`. Use
`numpy.random.default_rng(85)` in F127's table order. Compare n, the
model, competitor and raw GFS MAEs, d with its interval, and skill with
its interval against the highest precision recorded (in
`notes/session-85-output.txt` or any committed file session 85 wrote).
Report the precision used for each figure.

**G3. Frozen-model plumbing (no error computed).** For the 54 station-days
of F128's gate sample, take the committed rows from
`session81_training_set.csv`. Predict with the scoring script's own
predict path, and separately with `lightgbm.Booster(model_file=...)
.predict` on the same G15 array. Report the maximum absolute difference
per airport and model. Expected: 0.0. Do not compute any error against
the observation.

**G4. Writer exercise.** In a temporary directory outside the repo, the
`--score` writers write G1's and G2's figures as a stand-in grid and
predictions file. Read them back and check they are equal. Check that a
second write is refused. Delete the directory.

If a mismatch comes from a bug in the new script, fix it and re-run the
whole gate; report every run. If it cannot be traced to a bug, stop and
report.

### 3.5 `--score` (written, never run this session)

- Arguments: `--period A` or `--period B`; one of `--first-v17-cycle` or
  `--no-v17` (period A only); `--rows-sha256`; `--points-sha256`;
  `--nbm-versions`; `--mav-versions`; `--decision <entry>`, printed.
- Same timing guard as `--fetch`.
- Writes only these new files, and refuses to run if any exists. This is
  what makes each period a single look:
  - `data/processed/forward2627_period{A,B}_predictions.csv` (per row:
    station, date, each rung's forecast, the competitor values, the
    observation and the previous-day observation);
  - `data/processed/forward2627_period{A,B}_scores.csv` and its
    `.meta.txt` (input SHA-256s, arguments, versions, run time).
- Prints the full D73 and D77.6 tables, the labels, and the smallest
  margin first in each.

Put the full real output of Steps 2 and 3 (every guard-check case, every
gate run, every URL with its pull time, and every SHA-256) in
`notes/session-87-output.txt`, with each script's final SHA-256.

---

## Step 4: record F129

Append **F129** to DECISIONS.md, after D79, under a dated heading
`## <run date>: Session 87 finding: the 2026-27 scoring and competitor scripts and their gates`.
It gives:
- the Step 0 and Step 1 results;
- every function imported or copied, with its source and lines;
- both `--guard-check` results;
- the competitor gate: request and byte counts, 21 of 21 NBM and 5 of 5
  MAV (or the mismatches), grid points, the version check, and the number
  of runs;
- the scoring gate: G1 to G4, with the precision used for each figure,
  and the number of runs;
- the paths `--fetch` and `--score` will write, and their arguments;
- both scripts' SHA-256;
- a "what this did not do" list: no 2026-27 value requested or read; no
  `--fetch` or `--score` run; no fit except G2's verification refit; no
  error on the frozen models' training rows; nothing written under
  `data/`; no existing script edited; nothing committed.

---

## Step 5: SPEC 6 edit (after F129)

Make exactly these edits in SPEC 6's roadmap list, and nothing else.

At the end of the **Stage A** bullet, after "...and the comparison on
the spent years is recorded in F127.", add:

"The direction decision is recorded in DECISIONS D78.1: option (d),
neither; the roadmap carries on as D72 sets it."

At the end of the **Stage B** bullet, after "...on 2026-27 is
pre-registered in DECISIONS D77.6.", add:

"Its data-build script exists and passed its gate (DECISIONS D78.7,
F128)."

**Only if both gates in F129 passed**, add after that sentence:

"Its scoring script and the NBM and MAV fetch exist and passed their
gates (DECISIONS D79, F129)."

Report the edited lines before and after.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include:
   - the forward test's state (D73, F122, D77.6, D79);
   - that all three 2026-27 scripts exist and passed their gates (F128,
     F129), and that each 2026-27 mode runs only after its period has
     ended, in the order build, fetch, score, with the first v17 cycle
     and the version labels taken from DECISIONS entries;
   - the carried items: **GFS v17 (D79.7)**, still no SCN as of
     2026-09-30, to be re-checked at each planning session; open items
     **D78.2** and **D78.3**; and the remaining stage A/B uncertainties
     from session 86's STATUS.

   It must end with: "**Next planning session:** Review session 87. Then
   choose the next step while period A runs: open stage C, or run D78.3's
   non-US competitor probe first. Re-check GFS v17 (D79.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-87-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79 and F129 stay live. Report what moved and why, or
   that nothing did.
5. Stop and wait for review. Do not commit. Do not write a commit
   message.
