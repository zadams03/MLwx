# Session 90: D82 (stage C design), the airport metadata check, and the claim batch draw

Session 89 probed the data routes for stage C (F131); it is reviewed,
committed and pushed. In the planning chat the owner settled stage C's
design: the end goal (a corrected curve from every GFS run), the data
route (GRIB on GitHub Actions), the airports (a 47-airport list) and the
daily-maximum definition. This session:

1. records **D82** (the owner's decisions), before any other edit or any
   network call;
2. makes **two SPEC edits** (Step 2);
3. runs a **metadata check of the 47 airports** (Step 3): positions,
   time zones, the GFS grid boxes, MOSMIX stations, and hourly
   observation coverage, by **counts only**. It downloads and saves the
   new airports' hourly observations, but never prints or summarises a
   temperature value;
4. applies **D82.7's eligibility rules and draw**, mechanically, to name
   stage C's claim batch (Step 4);
5. records what it found as **F132**, and does the end-of-session steps.

It builds no GRIB pull. That is session 91 (D82.10).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **Nothing from 2026-27.** Do not request, read or receive any
  observation or forecast valid after **2026-07-31T23:59 UTC**. Restrict
  every query so this cannot happen. If a response holds anything later,
  drop those rows before saving, never print them, and record how many
  were dropped.
- **Observations: counts only.** You may download and save hourly
  observations for the airports in D82.6. You may count reports, hours
  and days. **Never print, summarise, plot or record any temperature or
  dew point value**, nor any statistic of one (no mean, maximum, range,
  difference or error). Not even in debugging output.
- **No scores.** Compute no error, MAE or skill of anything, on any year.
- **GFS: two fields only.** From one spent-year GRIB file, read only the
  land-sea mask and the surface (model terrain) height (Step 3.3). Read
  no temperature or other forecast field.
- **No accounts or credentials.** No sign-up, keys, tokens, paid tiers,
  contact or data requests.
- **No installs.** Use what is installed. The record's own GRIB decoding
  route (session 37's) is enough for Step 3.3. If something cannot be
  read with what is installed, record "not decoded" and why.
- **Writes under `data/`.** Only the new observation files and their
  `.meta.txt` files (Step 3.4), in the same directory and with the same
  naming and `.meta.txt` format as the committed IEM files, and one new
  table, `data/processed/session90_airports.csv` (Step 5). **Do not
  modify or overwrite any committed file** under `data/`. Do not touch
  `data/models/`.
- **Be polite to IEM.** One request at a time, at least 1 second apart.
  Retry only on network errors, HTTP 429 and 5xx, with a growing wait,
  at most 5 times. Report request and byte totals.
- **Temporary files** (the GRIB message, the DWD catalogue) go in one
  temporary directory outside the repo (`mktemp -d`), deleted at the end.
- **Do not edit any existing script.** You may write one new script,
  `scripts/session90_airport_check.py`.
- The only SPEC edits are Step 2's. Do not edit `RESULTS.md`,
  `CLAUDE.md`, `README.md` or `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-90.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D81 and F131, and that no
   D82 or F132 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that `scripts/session90_airport_check.py`,
   `notes/session-90-output.txt` and
   `data/processed/session90_airports.csv` do not exist. If any exists,
   stop and report.
4. Read D72 (in particular D72.1, D72.2, D72.4 and D72.8), D81, F130
   (its station method, F130.4), F131, SPEC 1, 3, 4, 6 and 8.8 (G2, G3
   and G6), and the `.meta.txt` of one committed IEM observation file.

---

## Step 1: record D82 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 90 decision: F131 accepted, the end goal reworded, and stage C's design (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
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
```

---

## Step 2: the SPEC edits

1. **SPEC 1, the end-goal paragraph.** Replace the paragraph that begins
   "The end goal is a private, live daily tool" and ends "See section 6
   for the roadmap." with this text, wrapped to the file's width:

   ```
   The end goal is a private, live tool for ten or more airports that
   corrects every GFS run (four a day), as each run arrives, into an
   hourly temperature curve out to the forecast horizon, plus the daily
   maximum. The horizon is 24 hours first and 48 hours later. Then come
   a choice of which weather model is corrected, plus a blend, and
   probabilistic ranges (DECISIONS D72.1, reworded by D82.2). That is
   the destination, not the starting point. See section 6 for the
   roadmap.
   ```

2. **SPEC 6, the stage C bullet.** Keep its first line's bold title
   exactly as it is. Replace the sentences after the title ("An hourly
   temperature curve, the daily maximum, and the 48-hour lead. Written
   with the weather model as a setting.") with this text, wrapped to the
   bullet's width:

   ```
   Correct every GFS run into an hourly temperature curve, plus the
   daily maximum, for forecast hours 0 to 24 first and to 48 later.
   Written with the weather model as a setting. Opened in DECISIONS D81;
   its design is in DECISIONS D82. Its claim is judged on new airports
   only, drawn by the rule in DECISIONS D82.7.
   ```

If either passage cannot be found exactly, stop and report. Change
nothing else. Show the result with `git diff -- SPEC.md`.

---

## Step 3: the airport metadata check

Give the URL and access time (UTC) for every source. Tag items
`verified`, `documentation only`, `secondary` or `unknown`, as in F130.

### 3.1 Identity and position

For each of the 47 airports in D82.6, from IEM's own station metadata
(its network listings): the IEM station identifier used by its ASOS
download service (for US airports this may be the three-letter code, as
for DSM, RNO and SFO), name, latitude, longitude, elevation and IANA
time zone. If an airport is missing from IEM, or two IEM stations could
match it, record it and do not choose. For EGLC and KSFO, check that IEM
still gives the values in SPEC 3.4; report any difference.

Also give the distance from LFPB to LFPG (SPEC 3.4's position) in km.

### 3.2 GFS grid box

For each airport: the four surrounding 0.25 degree grid points under
SPEC 8.8 G6 (longitudes shifted by +360 where negative), their latitudes
and longitudes, and the bilinear weights.

### 3.3 Land, sea and terrain (two GFS fields, one file)

From one spent-year file, `gfs.20240314/00/atmos/gfs.t00z.pgrb2.0p25.f000`
on `noaa-gfs-bdp-pds` (use `f001` if a field is absent from `f000`, and
say so), read by byte range only two messages: the land-sea mask
(`LAND:surface`) and the surface height (`HGT:surface`). For each
airport give: the mask value at each of the four points, the bilinear
land fraction, the bilinear model surface height, and the difference
between it and the station elevation (3.1). Flag every airport whose
bilinear land fraction is below 1.0 as "sea in the grid box" (as at
KSFO, F116). This is a flag only; it excludes nothing.

### 3.4 Hourly observations (download and save; counts only)

For each of the **45 new airports** (not EGLC or KSFO, whose files are
committed), download IEM's routine hourly reports with the **same
request** as the committed files (from their `.meta.txt`: `data=tmpc`,
`data=dwpc`, `tz=UTC`, `format=onlycomma`, `latlon=yes`, `elev=yes`,
`missing=M`, `trace=T`, `report_type=3`), in the same yearly pieces
(2021-03-24 to 2021-12-31, then each calendar year, then 2026-01-01 to
2026-07-31), saved with the same naming pattern and a `.meta.txt` in the
same format (exact URL, pull time, row count, SHA-256). Then, for every
one of the 47 airports, from its saved files, report counts only:
- rows, first and last report time, rows with no usable temperature;
- the usual minute past the hour, and the share of reports not at that
  minute (to show half-hourly reporting);
- days (UTC) with a usable report within 15 minutes of each whole hour,
  as one 24-row count (SPEC 8.8 G2, G3), and days with all 24 hours;
- **daily-maximum usable local days** (D82.8): the count and percentage
  over 2021-03-24..2026-07-31 and over 2024-08-01..2026-07-31, with the
  number of local days in each window (D82.7(b)'s day rule).

### 3.5 MOSMIX and NBM

- **MOSMIX:** with F130.4's method (DWD's station catalogue `.cfg`), the
  nearest MOSMIX station to each airport, its ID and distance, and
  whether it is within 10 km. Flag any position whose longitude sign
  looks wrong in the catalogue, as D81.6 noted for EGLC.
- **NBM:** for each airport, whether it lies inside an NBM domain, from
  NBM's documentation only (CONUS, Alaska, Hawaii, Puerto Rico, Guam,
  or none). Unknown is acceptable.

---

## Step 4: eligibility and the draw (D82.7, mechanically)

1. Apply D82.7(a) and (b) to the counts from Step 3.4. List every
   airport with its stratum (D82.7(c)), its two percentages, and
   "eligible" or the reason it is not.
2. Run D82.7(d)'s draw exactly as written. Print the Python version, the
   seed, each stratum's sorted eligible list, and what `sample` returned
   for each stratum and for any shortfall fill.
3. Do not rerun the draw, change the seed, or change any eligibility
   result after seeing it. If the rule cannot be applied as written (for
   example, fewer than six eligible airports in total), stop and report.

---

## Step 5: records

1. **`data/processed/session90_airports.csv`**, one row per airport (47
   rows): ICAO, owner's region, stratum, IEM ID, name, latitude,
   longitude, elevation, time zone, the four grid points and weights,
   land fraction, model height, height difference, sea flag, MOSMIX
   station ID and distance, NBM domain, the two daily-maximum
   percentages, eligible or the exclusion reason, and drawn (yes or no).
   No temperature values. Give its SHA-256 and a `.meta.txt` beside it.
2. **F132** in DECISIONS.md, after D82, under a dated heading
   `## <run date>: Session 90 finding: the airport metadata check and the claim batch`.
   It gives, with real findings only:
   - the Step 0, 1 and 2 results;
   - one compact table of the 47 airports (ICAO, IEM ID, sea flag,
     height difference, MOSMIX within 10 km, the two daily-maximum
     percentages, eligible, drawn);
   - **the claim batch** (six airports), with the draw's printed output;
   - airports missing from IEM or ambiguous; the LFPB to LFPG distance;
     the EGLC and KSFO metadata check;
   - every reading made where this prompt is silent, listed for the
     owner to confirm;
   - requests and bytes per source, rows dropped by the 2026-07-31 limit
     (if any), and confirmation the temporary directory was deleted;
   - a "what this did not do" list: no temperature or dew point value
     printed or summarised; no forecast field read beyond the mask and
     surface height; no score; nothing from 2026-27; no account; no
     committed file under `data/` changed; no existing script edited; no
     GRIB pull built; nothing committed.

   Keep F132 compact: full listings go in the output file.
3. Save the full real output as `notes/session-90-output.txt`. Record
   the new script's SHA-256.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include:
   - the end goal as reworded (D82.2);
   - the forward test's state (D73, F122, D77.6, D79), unchanged, and
     that all three 2026-27 scripts exist and passed their gates, never
     run;
   - MOSMIX (D81.2 to D81.5): the saver session not yet run;
   - stage C: its design (D82.3 to D82.8) in brief, the claim batch
     (F132), and what is not decided (D82.5);
   - the carried items: GFS v17 (D81.7), to be re-checked at each
     planning session; the EGLC position note (D81.6); MOSMIX matching
     (D80.4); D78.2; and the remaining stage A/B uncertainties from
     session 89's STATUS.

   F131.9's readings are accepted (D82.1), so that open question is
   removed. STATUS must end with: "**Next planning session:** Review
   session 90 and the claim batch. Then plan session 91: build the
   GitHub Actions GRIB pull and its local test chunk (D82.4, D82.10).
   Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-90-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79, F129, D80, F130, D81, F131, D82 and F132 stay
   live. Report what moved and why, or that nothing did.
5. Confirm the temporary directory was deleted, and run
   `git status --porcelain`.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
