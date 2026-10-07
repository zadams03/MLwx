# Session 86: the direction decision, and the 2026-27 data-build script (stage B)

Session 85 recorded F127: under D77.4's rule the band is MIXED. The owner
has made the direction decision in the planning chat. This session:

1. records **D78** (the direction decision, two open items, the GFS v17
   and NBM notes, and the plan for the 2026-27 scripts), before any other
   edit, network call or data read;
2. reads the record pipelines and writes out their recipe in plain words;
3. writes **one new script**, `scripts/session86_forward_build.py`, which
   builds the 2026-27 inputs of the forward test (D73) with the same logic
   as the record pipelines;
4. checks its date guards offline, then runs a **gate**: it rebuilds a
   fixed sample of spent-year station-days and compares every value with
   the committed training set (F122);
5. records **F128** and does the end-of-session steps.

**The script's 2026-27 mode (`--build`) is written but never run in this
session.** No 2026-27 row is built, requested or read. Nothing is scored.
The scoring script and D77.6's NBM/MAV fetch come in session 87 (D78.7).
Both scripts are committed before any 2026-27 row is built (D73.8).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 value from any source.** No request may ask for, and no
  code may keep, any GRIB message, observation or other value valid on or
  after 2026-08-01T00:00 UTC. Check every valid time before reading any
  value. If one appears, discard it without reading its value, report it,
  and stop that step.
- **Never run `--build`, in any form, with any arguments.** Its guards are
  tested only through `--guard-check` (Step 4), which makes no network call
  and reads no data.
- **No model is fit. No error, MAE, bias, skill or verdict is computed or
  printed, for any period.** Step 5.4 loads the frozen F122 models and
  compares their predictions on two identical sets of inputs; that is
  the only model use allowed.
- **Do not edit any existing script, and do not edit, bypass or disable
  any guard in one.** New code may import pure functions from record
  scripts read-only (checking the script's SHA-256 first, where DECISIONS
  records one), or copy them into the new script. If importing a script
  runs code (for example a bare `main()` call, F125.1), copy the function
  instead. Report every function imported or copied, with its source file
  and lines.
- **Write exactly one new script:** `scripts/session86_forward_build.py`,
  with the modes `--guard-check`, `--gate` and `--build` (Step 3).
- **Writes under `data/`: none.** GRIB bytes and fresh IEM responses in
  the gate go to a temporary directory outside the repo and are deleted
  when the gate ends. Queries and pull times go into the output file.
  Do not touch `data/models/`. Do not open the two A67-15 DSM files
  (D62.7, D73.10).
- **No installs, no accounts.**
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-86.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D77 and F127, and that no
   D78 or F128 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that neither `scripts/session86_forward_build.py`
   nor `notes/session-86-output.txt` exists. If either exists, stop and
   report.
4. Check the SHA-256 of `data/processed/session81_training_set.csv`
   against F122.3 and of `data/models/session81/manifest.json` against
   F122.5. If either differs, stop and report.
5. Read: D62 (D62.3, D62.7), D71.4, D72, D73, F122, F127 and D77 in
   DECISIONS.md. In DECISIONS-archive.md: F5, F89, F90, D48 (items 2, 3,
   7, 8, 10), F98, F100, F101, F102, F107 and F116. SPEC 3.4, 4.5, 5.2,
   7.2, 8.1, 8.2, 8.7 and 8.8.

---

## Step 1: record D78 (before any other edit, network call or data read)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 86 decision: the direction decision, two open items and the 2026-27 scripts (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D78. Owner decisions, planning chat (after session 85): the direction
decision that D77.4 requires, two open items, and the plan for the
2026-27 scripts.** Written at the start of session 86, before any other
edit, network call or data read. No 2026-27 value has been read.

- **D78.1 Direction: option (d), neither.** F127's band is mixed. The
  owner chooses neither (a) nor (b), for these reasons:
  - (i) F127 is the expected result of a correction of one weather
    model, trained once on a fixed window, against NBM, a blend of many
    models whose bias correction is updated continuously. The gap is
    not uniform: the model's MAE is lower at RNO, and KSFO look B's
    interval spans zero.
  - (ii) NBM as an input is already stage E (D72.3). Bringing it
    forward would break D72.2(b), one input first. NBM also changed
    version several times inside the training window (F123.3, D77.7).
  - (iii) Option (b) rests on an untested premise. Stage A probed no
    non-US post-processed forecast, and some exist (for example DWD's
    MOSMIX, and the Bureau of Meteorology's forecasts at Dubbo).
  - (iv) The lever F127 points to (D78.2) applies at every airport, US
    or not.
  The roadmap carries on as D72 sets it.
- **D78.2 Open item: bias drift.** In F127 the model's mean error is
  warm at all four airport-looks (+0.333 to +0.708 degC). At RNO and
  KSFO look A it is warmer than raw GFS's. The correction learned in
  training was carried into test years in which GFS's own bias had
  shifted, as D71.4 found at KSFO. Planning-chat arithmetic on F127's
  summary figures, assuming normally distributed errors and using each
  test year's own mean (hindsight, insight only, not a finding): with
  both biases removed, NBM's MAE would still be lower at DSM, KSFO look
  A and KSFO look B, so the band would still be mixed. A correction
  that adapts to recent bias is recorded as a candidate build choice
  for stage C. If taken up, it is tested by time-ordered
  cross-validation, identically at every airport (SPEC 2.5). Nothing is
  decided on it now.
- **D78.3 Open item: non-US competitors.** Before stage C's new
  airports are chosen (D72.8), a read-only probe of non-US
  post-processed station forecasts (for example DWD's MOSMIX): archive
  depth, live feed and station coverage. Nothing is chosen on it now.
- **D78.4 A consequence, recorded.** D77.6's 2026-27 test uses the
  frozen F122 models. No later change to the recipe can be claimed
  against NBM on 2026-27. Such a claim would need new airports or the
  2027-28 forward year.
- **D78.5 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice. The newest SCN
  listed is SCN 26-87 (2026-09-22). With 30 days' notice, the earliest
  go-live is about 29 October 2026.
- **D78.6 NBM v5.0.15 (planning-chat web search, 2026-09-29, not
  checked by this session).** SCN 26-74 (2026-08-26) upgraded NBM to
  v5.0.15, effective immediately, to fix its use of gridded tropical
  cyclone data in the Hawaii domain. It falls inside 2026-27 period A,
  so D77.6's labels for period A name it. Its effect on CONUS
  temperature is not known.
- **D78.7 The 2026-27 scripts (D73.8, D77.6), in two sessions.**
  Session 86: the data-build script
  (`scripts/session86_forward_build.py`), with a gate on spent-year
  station-days; its 2026-27 mode is written but not run. Session 87:
  the scoring script and D77.6's NBM and MAV fetch. Both are committed
  before any 2026-27 row is built. The build script's 2026-27 mode:
  - builds period A only, with GFS v16 file paths. Period B needs
    D73.4's v17 entry first;
  - runs only after period A has ended and its observations are in,
    with the first operational v17 cycle taken from a DECISIONS entry
    (D73.3);
  - prints counts only, never a 2026-27 value;
  - writes only new files, and refuses to overwrite any file.
```

---

## Step 2: the recipe (read only, no network)

Read the record pipelines and write out, in plain words, the recipe for
each column the forward test needs, with the file and line numbers each
part came from:

- `B`: `temperature_grib_c` (GRIB 2 m temperature plus the elevation
  constant), `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`
  (`session37_decode.py`, `session40_decode.py`; the elevation constants
  from the two params CSVs named in SPEC 5.2);
- L, D, T and R (`session49_upper_air_pull.py`, `session51_moisture_pull.py`,
  `session53_pressure_pull.py`, the session 55 radiation script, and
  `session63_reserved_year_build.py`; SPEC 8.1, 8.2, F107);
- KSFO's build (the `session76_` scripts, F116);
- the observation pairing and the previous-day observation used for
  persistence (`session62_reserved_confirm.py`, SPEC 4.5, 8.5).

For each, state: the GRIB fields, levels, cycles and forecast hours; the
lead convention (SPEC 7.2) at each airport's target hour; the grid point
and bilinear interpolation (SPEC 8.8 G6); rounding and stored precision
(G4, G5, G7); D's floor transform; R's native window at the lead-26
airports and its de-accumulation at the lead-24 airports (F102). Take
each airport's station code, target hour, grid point and elevation
constant from committed files (SPEC 3.4 tables and the params CSVs),
never typed from memory. Print a per-airport parameter table.

**Stop rule:** if any part of the recipe is ambiguous, or differs between
the v16-window, sealed-window, reserved-year and KSFO scripts in a way
that changes a value, stop and report.

---

## Step 3: write `scripts/session86_forward_build.py`

New code, meeting all five SPEC 8.7 build requirements: nearest report
chosen explicitly; non-finite values rejected at load, dropped and
counted; each GRIB message's full validity date **and hour** checked;
every gap guard compares the row count with the expected full count;
no writes to committed record files. Rows are in ascending date order
and carry the nine G15 columns in the record order, plus
`temperature_grib_c` and the observation.

### 3.1 Shared build function

One function builds rows for a given airport and list of target dates:
the nine G15 columns, `temperature_grib_c`, the paired observation, and
the previous day's paired observation (for persistence). It fetches GRIB
messages by byte range from `noaa-gfs-bdp-pds` via the `.idx` files, as
the record scripts do, and observations from IEM (report_type=3, the
record's query form). Missing values are dropped and counted by reason
(no GRIB message, non-finite value, no report within 15 minutes, and so
on), never filled (SPEC 2.2). A failed request is retried at most 3
times, politely spaced.

### 3.2 `--guard-check` (offline: no network, no data read)

Calls the date guards only, with these cases, and prints each outcome:
- gate date 2026-07-31: allowed;
- gate date 2026-08-01: refused;
- `--build` with no first-v17-cycle argument and no `--no-v17`: refused;
- `--build` for period B: refused;
- `--build` whose last period-A target day plus 3 days is after the run
  date (UTC): refused;
- `--build` with any date on or after 2027-08-01: refused.

### 3.3 `--gate` (spent years only)

Hard-stops on any target date after 2026-07-31. Runs Step 5.

### 3.4 `--build` (2026-27 period A; written, never run this session)

- Arguments: `--period A`, and either `--first-v17-cycle YYYY-MM-DDTHH`
  (from the DECISIONS entry that records it, D73.3) or `--no-v17` (only
  when no operational v17 cycle has forecast any day by 2027-07-31), and
  `--decision <entry number>`, which is printed in the output.
- Period A starts on 2026-08-01. For each airport, its last period-A
  target day is the last day D whose forecasting cycle (floor(H/6)x6 UTC
  on D-1, SPEC 7.2) is before the first v17 cycle. The code computes this
  per airport and prints it.
- Refuses to run unless the run date (UTC) is at least 3 days after the
  latest of those last days. Refuses `--period B` outright ("period B
  needs D73.4's v17 entry first").
- v16 file paths only. A file that is absent is counted as missing, not
  searched for elsewhere. Parallel ("para") data is never requested.
- Writes only these new files, and refuses to run if any exists:
  - `data/processed/forward2627_periodA_rows.csv` (one row per airport and
    target day) and its `.meta.txt`;
  - `data/raw/diagnostics/forward2627/periodA_grib_manifest.csv` (every
    GRIB URL, byte range and pull time, D47) and
    `periodA_drop_log.csv`;
  - `data/raw/iem/forward2627/` (raw IEM responses, unchanged, each with
    a `.meta.txt` holding the exact query and pull time, SPEC 2.3).
- GRIB bytes go to a temporary directory outside the repo and are
  deleted after decoding.
- Prints counts only: rows per airport against the expected full count,
  and drops by reason. **It never prints a 2026-27 feature, forecast or
  observation value.**

---

## Step 4: run `--guard-check`

Run it once. Every case must behave as Step 3.2 says. If any does not,
fix the new script, re-run, and report both runs.

---

## Step 5: the gate (`--gate`, network, spent years only)

### 5.1 The sample (fixed; do not change it)

All six airports (EGLC, LFPG, DSM, YSDU, RNO and KSFO as `SFO`), on
these nine target dates, 54 station-days in all:

| date | window it sits in | season |
|---|---|---|
| 2021-04-15 | v16 window | spring |
| 2022-01-10 | v16 window | winter |
| 2023-07-20 | v16 window | summer |
| 2023-10-05 | v16 window | autumn |
| 2024-11-12 | reserved year | autumn |
| 2025-02-18 | reserved year | winter |
| 2025-09-03 | sealed year | late summer |
| 2026-04-22 | sealed year | spring |
| 2026-07-31 | sealed year, last day | summer |

If a station-day has no row in `session81_training_set.csv`, report it
as "no committed row" and do not replace it.

### 5.2 Size trial

List the GRIB messages the sample needs and fetch 3. Report bytes per
message and the projected total. If the projected total exceeds 5 GB,
stop and report.

### 5.3 Rebuild and compare

Rebuild each sampled station-day with the Step 3.1 function, from fresh
GRIB and IEM pulls. Compare with the same station-day in
`data/processed/session81_training_set.csv`:
- the nine G15 columns and `temperature_grib_c`: **exact equality** at
  the stored precision (no tolerance);
- the observation (`obs_c`): exact equality. The training set keeps the
  historical pairing (last qualifying report, SPEC 4.5's note); the new
  code picks the nearest. A difference caused only by that is listed
  separately (station, date, both reports, both values), and is not
  counted as a failure;
- the previous-day observation: exact equality with the training set's
  `obs_c` for day D-1, where that row exists.

Report pass counts per column and per airport (for example "L: 54 of
54"), and for every mismatch: station, date, column, committed value,
rebuilt value and difference.

**If there is a mismatch:** if it comes from a bug in the new script, fix
the script and re-run the whole gate; report every run. Do not change the
sample or the pass rule. If a mismatch cannot be traced to a bug in the
new script (for example, the archived bytes differ), stop and report.

### 5.4 Frozen-model plumbing check (no error computed)

Load the twelve F122 model files after checking each SHA-256 against
F122.5. For each sampled station-day that has both a committed row and a
rebuilt row, predict with the frozen `B+D,L,R,T` and `B` models on each
of the two rows. Report the maximum absolute difference between the two
predictions, per airport and model. Expected: 0.0 everywhere. Do not
print or compute any error against the observation.

Put the full real output of Steps 2, 4 and 5, including every URL
queried and its pull time, in `notes/session-86-output.txt`.

---

## Step 6: record F128

Append **F128** to DECISIONS.md, after D78, under a dated heading
`## <run date>: Session 86 finding: the 2026-27 data-build script and its gate`.
It gives:
- the Step 0 and Step 1 results;
- the recipe summary (Step 2), with the per-airport parameter table;
- every function imported or copied, with its source and lines;
- the `--guard-check` result;
- the gate: request and byte counts, pass counts per column and airport,
  the pairing differences, every mismatch, the number of gate runs, and
  the plumbing check;
- the paths `--build` will write;
- a "what this did not do" list: no 2026-27 value requested or read; no
  `--build` run; no model fit; no error or score computed; nothing written
  under `data/`; no existing script edited; nothing committed.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include: the forward test's state (D73, F122, D77.6) and
   that the build script exists and passed its gate (F128); the
   direction decision in one line (D78.1); and these carried items:
   - **GFS v17 (D78.5).** Still no Service Change Notice as of
     2026-09-29. Re-check at each planning session. The go-live date sets
     period A's length. PNS 26-30's statement that the 0.25 degree GRIB2
     files remain is to be confirmed against the SCN (D73.4).
   - **Open items D78.2 (bias drift) and D78.3 (non-US competitors).**
   - The remaining stage A/B uncertainties from session 85's STATUS.

   It must end with: "**Next planning session:** Review session 86. Then
   design session 87: the 2026-27 scoring script and D77.6's NBM and MAV
   fetch (D78.7). Re-check GFS v17 (D78.5)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-86-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78 and F128 stay live. Report what moved and why, or that
   nothing did.
5. Stop and wait for review. Do not commit. Do not write a commit
   message.
