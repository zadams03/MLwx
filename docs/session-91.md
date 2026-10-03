# Session 91: D83, the stage C GRIB pull (script and GitHub Actions workflow) and its local test chunk

Session 90 checked the 47 airports and drew the claim batch (F132); it is
reviewed, committed and pushed. In the planning chat the owner accepted
F132, set the pull list at 51 airports, fixed the grid positions, and
settled the pull's design. This session:

1. records **D83** (the owner's decisions), before any other edit or any
   network call;
2. surveys the GFS index lines for the ten fields (Step 2);
3. writes the **pull script** and the **positions file** (Steps 3 and 4);
4. writes the **GitHub Actions workflow** that runs the script in
   monthly chunks (Step 5);
5. runs a **local test chunk** of three days and puts it through the
   **gate** against the committed values (Step 6);
6. records what it found as **F133**, and does the end-of-session steps.

It does not run the full pull, push anything, trigger the workflow or
create a GitHub Release. The owner does that after review (D83.8).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full, and SPEC 8.7's build requirements for
  new code.
- **Nothing from 2026-27.** Never request a GFS cycle after
  2026-07-31T18:00 UTC or any message valid after 2026-07-31T23:00 UTC.
  The script must refuse such a request in code, not only by its
  arguments.
- **No observations.** This session reads no observation file and no
  IEM data.
- **No scores.** Compute no error, MAE, bias or skill of anything. The
  gate compares GFS values with committed GFS-derived values only.
- **No forecast value printed** beyond what the gate needs to report a
  mismatch (if one occurs: print that row's new and committed values in
  full; otherwise print counts only).
- **No accounts or credentials.** No sign-up, keys, tokens, paid tiers,
  contact or data requests. The session does not use any GitHub token.
- **No installs.** Use what is installed.
- **No push, no workflow run, no Release.** Do not run `git push`, `gh`,
  or anything that talks to GitHub.
- **Writes.** Only these new files:
  `scripts/session91_grib_pull.py`,
  `.github/workflows/stagec-grib-pull.yml`,
  `.github/grib-pull-requirements.txt`,
  `data/processed/session91_pull_airports.csv` and its `.meta.txt`,
  `notes/session-91-output.txt`, plus the DECISIONS.md and STATUS.md
  edits the steps give. **Do not modify or overwrite any committed
  file** under `data/`. Do not touch `data/models/`.
- **Temporary files** (test-chunk outputs, any GRIB message) go in one
  temporary directory outside the repo (`mktemp -d`), deleted at the end.
- **Download budget:** at most 4.5 x 10^9 bytes in total this session.
  The script stops cleanly at the budget and prints what it read.
- **Do not edit any existing script.** Functions may be **copied** from
  record scripts (cite file and lines), not imported from them.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop
  and report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-91.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D82 and F132, and that no
   D83 or F133 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that none of the new files listed in the scope
   guard exist. Report whether a `.github/` folder exists at all and
   list anything in it. If any of the new files exists, stop and report.
4. Read: D47, D62, D82, F128, F131 and F132 in DECISIONS.md; SPEC 3.4,
   7.2, 8.2, 8.7 and 8.8 (G4 to G7); `scripts/session86_forward_build.py`
   in full (its `find_range`, `bilinear_from_gid`, `decode`,
   `field_plan` and `derive`, F128.3); and
   `data/processed/session90_airports.csv` with its `.meta.txt`.
5. Check SHA-256 of `data/processed/session81_training_set.csv` against
   F122.3 and of `data/processed/session90_airports.csv` against F132.
   Any difference: stop and report.
6. Print the installed versions of Python, eccodes (the Python package
   and the ecCodes library it reports), numpy and requests, and
   `pip show eccodes` (its `Requires` line).

---

## Step 1: record D83 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 91 decision: F132 accepted, the 51-airport pull list, grid positions, and the pull's design (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D83. Owner decisions, planning chat (after session 90): F132
accepted, the pull list, grid positions, an open item, and the design
of the stage C GRIB pull.** Written at the start of session 91, before
any other edit or network call. No 2026-27 value has been read or
scored.

- **D83.1 F132 accepted.** The owner accepts F132 and all twelve F132.8
  readings.
- **D83.2 The pull list is 51 airports:** D82.6's 47 plus LFPG, DSM,
  YSDU and RNO. Build choices use all six development airports (D82.6),
  so the pull must include them. Each global field serves every
  airport, so the extra cost is negligible. The four added airports are
  also product airports: the product list is now these 51 (D82.6's 47
  plus LFPG, DSM, YSDU and RNO). They remain development airports, so
  they are never in a claim batch.
- **D83.3 Grid positions.** The six development airports (EGLC, LFPG,
  DSM, YSDU, RNO, KSFO) use SPEC 3.4's grid points: the gate needs
  them, and they keep the record consistent. The 45 new airports use
  IEM's airport position, as F132 did. The raw values at the four grid
  points are kept, so the interpolation choice stays open.
- **D83.4 Open item: MMMX.** It reports at scattered minutes (mostly
  :40 to :50), so under the 15-minute rule (SPEC 8.8 G3) it has almost
  no usable observations (5.32 percent of local days, F132.6). It needs
  its own handling or to be dropped. That is a later decision. It stays
  in the pull.
- **D83.5 The pull's design (completes D82.4).**
  (a) Forecast hours are a setting of the script. The real pull uses
  f000 to f024 (D82.3). The local test chunk uses f000 to f026, so the
  gate reaches the lead-26 airports (YSDU, RNO, KSFO) as well as the
  lead-24 ones. The later f025 to f048 pull reuses the same script.
  (b) A chunk is one calendar month of GFS cycles, by the cycle's
  initialisation date. The first cycle is 2021-03-23T00 (its f024 is
  valid at 2021-03-24T00); the last is 2026-07-31T18. A forecast hour
  whose valid time lies outside 2021-03-24T00 to 2026-07-31T23 UTC is
  not requested.
  (c) Values are kept exactly as decoded, with no rounding and no unit
  conversion, written in a form that reads back to the identical
  number. The kept size may exceed D82.4's 1.5 GB estimate; this is
  accepted.
  (d) Each chunk writes one data file, one per-message manifest and one
  metadata file. A chunk is published as GitHub Release files only if
  it completed. A rerun skips months already published, so the pull is
  resumable.
  (e) A field that GFS does not provide at a forecast hour (for example
  an average or maximum at f000) is recorded as absent by design. A
  missing index file or a message that fails its identity or validity
  check is recorded and left empty. Neither is ever filled (SPEC 2.2).
  A download that still fails after its retries fails the chunk, so
  nothing partial is published.
  (f) On GitHub Actions, at most four months run at once.
  (g) The owner's first Actions run is one month. It measures real
  speed and size. Session 92 checks it before the rest is started. The
  local test chunk checks correctness only; its speed is limited by the
  owner's connection.
- **D83.6 The local test chunk.** Three cycle dates, 2022-01-12,
  2023-07-12 and 2024-04-12, all four cycles, f000 to f026, all 51
  airports. The gate compares, at each development airport's target
  hour, cycle and lead, the GRIB-derived values rebuilt from the new
  extract with the committed values in
  `data/processed/session81_training_set.csv`, on target dates
  2022-01-13, 2023-07-13 and 2024-04-13: 18 station-days, exact
  equality, no tolerance.
- **D83.7 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-03, not checked by this session).** Still no Service Change
  Notice. The newest SCN listed is still SCN 26-87 (2026-09-22). With 30
  days' notice, the earliest go-live is about 2 November 2026.
- **D83.8 Sequence.** Session 91: this entry, the script, the
  positions file, the workflow, and the local test chunk through the
  gate. The owner then pushes and runs one month on GitHub Actions
  (D83.5(g)). Session 92: verify that month's extract, speed and size,
  then the owner starts the rest.
```

---

## Step 2: index survey (27 small requests)

From `noaa-gfs-bdp-pds`, read only the `.idx` files of cycle
`gfs.20230712/12` for f000 to f026 (27 requests, no GRIB message). For
each of the ten fields below, print every index line that matches its
variable and level, at every forecast hour.

| short name | variable and level | the record's form |
|---|---|---|
| t2m | `TMP:2 m above ground` | instantaneous |
| tcdc | `TCDC:entire atmosphere` | instantaneous ("N hour fcst"), session 37 |
| u10 | `UGRD:10 m above ground` | instantaneous |
| v10 | `VGRD:10 m above ground` | instantaneous |
| d2m | `DPT:2 m above ground` | instantaneous |
| t850 | `TMP:850 mb` | instantaneous |
| dswrf | `DSWRF:surface` | average over its window (F131.3) |
| prmsl | `PRMSL:mean sea level` | instantaneous |
| tmax2m | `TMAX:2 m above ground` | maximum over its window |
| tmin2m | `TMIN:2 m above ground` | minimum over its window |

Then write the selector rule for each field: the record's form where
`session86_forward_build.py` has one (cite its lines), and for tmax2m
and tmin2m the only matching line. At f000 the index says `anl` for an
analysis; say how the rule handles it. **Each rule must match exactly
one line, or none, at every hour.** If a rule matches more than one
line at any hour, stop and report the lines. Do not choose between them.
A field with no line at an hour is "absent by design" at that hour;
list every such field and hour.

---

## Step 3: the positions file

Write `data/processed/session91_pull_airports.csv`, one row per airport,
51 rows, sorted by ICAO code. Columns: ICAO code, IEM ID, role
(`development`, `claim batch` (F132.6), or `new`), position source,
latitude and longitude used, then for each of the four grid points in
the order eccodes returns them: its index in the 721 x 1440 grid, its
latitude and longitude; and the bilinear weight each point gets at the
position used (SPEC 8.8 G6). Add the grid geometry it was computed on
(Ni, Nj, first and last latitude and longitude, increments).

- **Development airports (6):** SPEC 3.4's grid latitude and longitude
  (as F128.2's table), read from SPEC 3.4 or the record's params files
  by code, never typed in. ICAO codes: EGLC, LFPG, KDSM (IEM `DSM`),
  YSDU, KRNO (IEM `RNO`), KSFO (IEM `SFO`).
- **The other 45:** IEM's latitude and longitude from
  `data/processed/session90_airports.csv`.
- The four points come from `codes_grib_find_nearest` on one decoded
  message (the record's method, G6), computed once. A negative
  longitude is shifted by +360 first (G6).
- Check: at the six development airports the four points equal those
  the record's `bilinear_from_gid` uses (as copied into
  `session86_forward_build.py`). Report.

Give its SHA-256 and a `.meta.txt` beside it (source files and their
SHA-256, the GRIB message used, run time).

---

## Step 4: the pull script

Write `scripts/session91_grib_pull.py`. It must:

1. **Modes.**
   - `--plan`: no network. For every month from 2021-03 to 2026-07,
     print the first and last cycle, the number of cycles, files and
     expected messages (from Step 2's absent-by-design list), and the
     earliest and latest valid time. Confirm no valid time is outside
     the window.
   - `--chunk --month YYYY-MM --hours A-B --out DIR [--workers N]`: the
     pull for one month. Also `--dates D1,D2,...` in place of
     `--month`, for the test chunk.
   - `--gate --extract DIR`: the gate (Step 6) on a finished chunk's
     files.
   - `--guard-check`: no network; exercises every refusal (Step 6.1).
2. **Fetching.** By byte range from the `.idx`, as the record does
   (`find_range` copied from `session86_forward_build.py`). Retries only
   on network errors, HTTP 429 and 5xx, with a growing wait, at most 5
   times. Downloads run in parallel (`--workers`; default 16).
3. **Per message:** check its identity (discipline, category, number,
   level), its run date and time, its forecast step, and its full
   validity date and hour against the request (SPEC 8.7, requirement
   3). Check the grid geometry equals the positions file's. Read the 4
   values per airport by the stored grid index. Record the message's
   step range and statistical-process type. Keep nothing else; delete
   the message.
4. **Output per chunk** (three files, named by the month or `test`):
   - `gfs_points_<chunk>.csv.gz`: one row per cycle, forecast hour and
     airport. Columns: `cycle_utc`, `fhour`, `valid_utc`, `icao`, then
     `<field>_1` to `<field>_4` for the ten fields (point order as the
     positions file). Values are the decoded numbers written with
     Python's `repr`, so they read back identically. Empty where absent
     or not usable.
   - `manifest_<chunk>.csv.gz`: one row per requested message: cycle,
     fhour, field, index line, byte range, bytes, status (`ok`,
     `absent by design`, `idx missing`, `check failed`), step range,
     process type, and the reason for any non-`ok` status.
   - `chunk_<chunk>.meta.txt`: run start and end (UTC), arguments,
     counts per status, bytes downloaded, seconds, the two data files'
     SHA-256, the script's and the positions file's SHA-256, and the
     package versions.
   The script refuses to write if any of the three files exists. If any
   download fails after its retries, it writes nothing and exits with
   an error.
5. **Guards in code:** refuse any cycle after 2026-07-31T18, any
   message valid after 2026-07-31T23:00 or before 2021-03-24T00:00,
   and any `--hours` outside 0 to 48.
6. **No interpolation, no derived field, no rounding** in the chunk
   output. Interpolation and derivation exist only in `--gate`.

---

## Step 5: the GitHub Actions workflow

Write `.github/workflows/stagec-grib-pull.yml` and
`.github/grib-pull-requirements.txt`. The workflow:

- runs only by manual start (`workflow_dispatch`), with one input,
  `months`: one month (`2021-03`) or a range (`2021-03..2021-08`);
- has a first job that expands the range, lists the assets already on
  the Release named `stagec-grib-pull-v1`, and passes on only the
  months not yet published;
- runs one job per remaining month (a matrix), at most four at once
  (`max-parallel: 4`), each with `timeout-minutes: 350`, on
  `ubuntu-latest`, Python 3.12;
- installs only the pinned file. Pin the same versions as Step 0.6,
  including any package the local eccodes requires for its library. If
  you cannot tell which package supplies the ecCodes library on Linux,
  say so in F133 (it is then checked by the owner's first run);
- runs `--chunk --month <m> --hours 0-24 --out <dir> --workers 16`;
- on success only, creates the Release if it does not exist and
  uploads the chunk's three files to it, using the job's built-in
  token (`permissions: contents: write`; no secret is added);
- keeps nothing else: no global field, no cache of GRIB files.

If PyYAML is installed, parse the workflow and report it valid;
otherwise report "not parsed". The workflow is not run.

---

## Step 6: guard check, the local test chunk and the gate

1. **`--guard-check`.** Show each refusal fires: cycle 2026-07-31T18
   with f006 (valid 2026-08-01T00) refused; cycle 2026-08-01T00
   refused; valid time 2021-03-23T23 refused; `--hours 0-49` refused;
   writing over an existing output file refused. Also show allowed:
   cycle 2026-07-31T18 f005; cycle 2021-03-23T00 f024. No network.
2. **`--plan`.** Run it and put its table in the output file.
3. **The test chunk.** Run
   `--chunk --dates 2022-01-12,2023-07-12,2024-04-12 --hours 0-26`
   into the temporary directory, with `--workers 8`. Report requests,
   messages per status, bytes, seconds, and the three files' sizes.
   Also, for one message per field at two new airports, check the
   values read by index equal `codes_grib_find_nearest`'s four values
   (a spot check of the index read).
4. **The gate (`--gate` on the test chunk's files).** From the extract,
   at each development airport's target hour, cycle and lead (F128.2),
   rebuild with the record's arithmetic (copied from
   `session86_forward_build.py`, with the same operation order:
   bilinear (G6), the elevation constant and 3-decimal rounding (G4,
   G5), D's floor, L and D (G7), T from the two rounded pressures, R
   native at lead 26 and de-accumulated at lead 24 (F128.2)) the
   columns `temperature_grib_c`, `cloud_cover`, `wind_speed_10m`,
   `dewpoint_depression_t2m_floored`, `lapse_rate_t2_t850`,
   `pressure_tendency_3h_hpa` and `dswrf_2h_wm2`. Compare with
   `session81_training_set.csv` on target dates 2022-01-13,
   2023-07-13 and 2024-04-13: 6 airports x 3 dates = 18 station-days,
   7 columns, exact equality. Report a pass table by column and by
   airport. If a station-day has no committed row, report it. **If any
   value differs, report it in full and stop: do not change the
   arithmetic to make it pass.**
5. **Projection** (estimates, marked as such): from the test chunk,
   the full f000 to f024 pull's files, messages, bytes downloaded and
   compressed kept size, in total and per month; and time per month at
   the measured rate, noting it is limited by the local connection
   (D83.5(g)).

---

## Step 7: records

1. **F133** in DECISIONS.md, after D83, under a dated heading
   `## <run date>: Session 91 finding: the stage C GRIB pull and its gate`.
   It gives, with real findings only:
   - the Step 0 and 1 results;
   - the index survey: the selector rules and the absent-by-design list;
   - the positions file (SHA-256) and its development-airport check;
   - the script's modes and guards, the workflow, the pinned versions,
     and what about the workflow could not be tested locally;
   - the guard check, the plan table's totals, the test chunk's counts
     and sizes, the spot check, and **the gate result**;
   - the projection, marked as estimates;
   - every reading made where this prompt is silent, listed for the
     owner to confirm;
   - requests and bytes, and confirmation the temporary directory was
     deleted;
   - a "what this did not do" list: no observation read; no score;
     nothing from 2026-27; no forecast value printed beyond any gate
     mismatch; no push, workflow run or Release; no account or token;
     no committed file under `data/` changed; no existing script
     edited; nothing installed; nothing committed.

   Keep F133 compact: full listings go in the output file.
2. Save the full real output as `notes/session-91-output.txt`. Record
   the new script's and the workflow's SHA-256.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include:
   - the end goal (D82.2);
   - the forward test's state (D73, F122, D77.6, D79), unchanged: all
     three 2026-27 scripts exist and passed their gates, never run;
   - MOSMIX (D81.2 to D81.5): the saver session not yet run;
   - stage C: its design (D82.3 to D82.8, D83.2 to D83.5) in brief, the
     claim batch (F132), what is not decided (D82.5), the pull's state
     (built and gated, or not), and the open item MMMX (D83.4);
   - the carried items: GFS v17 (D83.7), to be re-checked at each
     planning session; the EGLC position note (D81.6); MOSMIX matching
     (D80.4); D78.2; and the remaining stage A/B uncertainties from
     session 90's STATUS.

   F132.8's readings are accepted (D83.1), so that open question is
   removed. STATUS must end with: "**Next planning session:** Review
   session 91 and the gate. If it passed, the owner pushes and runs one
   month on GitHub Actions (D83.5(g)); then plan session 92: verify that
   month's extract, speed and size before the rest is started. Re-check
   GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-91-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79, F129, D80, F130, D81, F131, D82, F132, D83 and
   F133 stay live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted, and run
   `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
