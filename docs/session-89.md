# Session 89: D81 (MOSMIX saves chosen, stage C opened) and a read-only stage C scoping probe

Session 88 probed DWD MOSMIX and other non-US competitors (F130); it is
reviewed, committed and pushed. The owner has made the save choice that
D80.5 left open, and opens stage C (D72.3). Stage C widens the target
(an hourly temperature curve, the daily maximum, the 48-hour lead) on GFS
only. Its data need is large: a planning-chat estimate puts the GRIB
route at about 750 GB of downloads. So before stage C is designed, this
session measures what the data would cost by two routes. This session:

1. records **D81** (the owner's decisions), before any other edit or any
   network call;
2. makes **one SPEC 6 edit** (Step 2);
3. runs a **read-only stage C scoping probe** (Step 3): first the
   dynamical.org GFS forecast archive, with a reproduction check against
   GRIB values already committed; then the cost of the GRIB route; then
   hourly observation coverage and daily-maximum sources;
4. records what it found as **F131**, and does the end-of-session steps.

It **chooses nothing**. The data route, the daily-maximum definition,
the new airports and every other stage C design choice are the owner's,
in a later session (D81.11).

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **Nothing from 2026-27.** Do not request, read or receive any forecast
  valid after **2026-07-31T23:00 UTC**, or any observation after that
  time. Restrict every query so this cannot happen (for forecasts, use
  init times no later than 2026-07-29T18:00 UTC). If a response holds
  anything later, do not print it, discard it, and record that it
  happened.
- **No scores.** Compute no error, MAE or skill of any forecast against
  observations, on any year. The only comparisons allowed are between
  **two copies of the same GFS forecast** (Step 3.1.3), on spent-year
  dates.
- **Observations: counts only.** In Step 3.3 you may count reports. Do
  not print, summarise or record any observed temperature value.
- **Forecast values.** In Step 3.1.3 you may compute differences between
  the two copies and print only summary statistics of those differences
  (count, mean of the absolute difference, largest absolute difference,
  number of exact matches). Do not print raw forecast values, except at
  most three example rows per field for debugging, all from 2021 to 2023.
- **No accounts or credentials.** No sign-up, sign-in, keys, tokens, paid
  tiers, contact or data requests. dynamical.org's optional email query
  parameter is **not** used.
- **Installs.** You may install packages needed to read the dynamical.org
  archive (for example `xarray`, `zarr`, `icechunk`, `dynamical-catalog`)
  **only into a throwaway virtual environment inside the temporary
  directory** below. Do not touch the project's environment or
  `requirements.txt`. Record every package and version installed.
- **Downloads.** Everything downloaded goes into one temporary directory
  outside the repo (`mktemp -d`), deleted at the end of the session.
  Limits: dynamical.org reads, at most **5 GB** in total; the GRIB trial
  (Step 3.2), at most **500 MB**. Be polite: no parallel bulk requests
  beyond what the client library does by default. Report the total
  requests (where countable) and bytes for each route.
- **Nothing under `data/`.** Write nothing under `data/` and do not touch
  `data/models/`. Committed files under `data/` may be **read**.
- **Do not edit any existing script.** You may write one new helper
  script, `scripts/session89_stage_c_scoping.py`. It reads from the
  network and from committed files, prints, and writes no data file.
- The only SPEC edit is Step 2's. Do not edit `RESULTS.md`, `CLAUDE.md`,
  `README.md` or `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-89.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D80 and F130, and that no
   D81 or F131 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that `scripts/session89_stage_c_scoping.py` and
   `notes/session-89-output.txt` do not exist. If either exists, stop and
   report.
4. Read D72 (in particular D72.2, D72.3 and D72.8), D73.8, D78.2, D80.5,
   F130, and SPEC 3.4, 4.1, 4.5, 6, 7.2 and 8 (in particular 8.1, 8.2 and
   8.8). From DECISIONS-archive.md where they have moved, read the
   findings that define each SPEC 8 field's source and form: F89, F90,
   F97, F98, F100, F101, F102, F107 and F116. You need these to know
   exactly which GRIB fields, levels and averaging windows the committed
   values come from.

---

## Step 1: record D81 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 89 decision: F130.9 accepted, MOSMIX saves, stage C opened and its scoping probe (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D81. Owner decisions, planning chat (after session 88): F130.9
accepted, MOSMIX daily saves chosen, stage C opened, and the plan for a
read-only stage C scoping probe.** Written at the start of session 89,
before any other edit or network call. No 2026-27 value has been read or
scored.

- **D81.1 F130.9 accepted.** The owner accepts F130.9's four readings as
  written. F130.8 (one MOSMIX_S file downloaded three times) is noted;
  no action.
- **D81.2 MOSMIX saves: option B (D80.5).** MOSMIX_L single-station
  files, all four daily issues, saved unchanged as downloaded, at:
  EGLC (P0478), LFPG (07157), DSM (72546), RNO (72488) and KSFO (72494)
  (F130.4). Stage C's new airports are added when they are chosen, where
  a MOSMIX station exists.
- **D81.3 YSDU is not on the list.** It has no MOSMIX station within 10
  km; the nearest is 221.75 km away (F130.4).
- **D81.4 Where the saver runs.** GitHub Actions, committing to a
  separate private repository, not the public project repository.
  Because about eight MOSMIX_L issues stay on DWD's server (F130.2), the
  saver may run several times a day and save any issue it does not yet
  hold; a late or skipped run then loses nothing unless the gap is longer
  than about 40 hours. The details are the saver session's.
- **D81.5 Timing.** Not urgent. The saver is new code and gets its own
  session when the owner chooses. Days before it starts are lost, and
  this is accepted. No MOSMIX test is pre-registered.
- **D81.6 EGLC position note (planning chat, not checked by this
  session).** DWD's cfg places P0478 at 0 deg 03 min W; London City
  airport is at about 0 deg 03 min E. If DWD's sign is wrong, the
  station is about 2.5 km from the airport, not 7.7 km. This matters
  only for a later MOSMIX comparison at EGLC. F130 is unchanged.
- **D81.7 GFS v17 (planning-chat check of the NWS notices page,
  2026-10-02, not checked by this session).** Still no Service Change
  Notice. The newest SCN listed is SCN 26-87 (2026-09-22). With 30 days'
  notice, the earliest go-live is about 1 November 2026.
- **D81.8 SPEC 6.** Stage B's bullet gets one sentence citing D78.3,
  F130 and D81 (session 89, Step 2).
- **D81.9 Stage C is opened.** Its claim is judged on new airports only
  (D72.8), chosen before stage C's lock and not scored before it. Stage
  C makes no claim on 2026-27: that year stays for D73 and D77.6, and
  once period A is scored no new test may be pre-registered on it
  (D72.2(a)).
- **D81.10 Stage C defaults.** (a) The daily-maximum definition is
  decided after F131. (b) Bias drift (D78.2) is tested only after the
  curve's baseline exists, as one change at a time (D72.2(b)), by
  time-ordered cross-validation, identically at every airport. (c) New
  candidate airports are chosen in stage C's design session, and added
  to the MOSMIX list where a station exists (D81.2).
- **D81.11 The data route is not decided.** A planning-chat estimate
  (not checked): the hourly curve at both leads needs about 24 GRIB
  files a day per lead, about 10 fields each, over about 1,950 days, so
  about 470,000 byte-range requests and about 370 GB of downloads per
  lead, about 750 GB for both. Downloads are decoded and discarded, not
  stored. Session 89 therefore probes, read only: first, the
  dynamical.org GFS forecast archive, which serves point time series
  without whole global fields (planning-chat web search, 2026-10-02,
  secondary: global, 25 variables, 0.25 deg, leads 0 to 384 h, inits
  every 6 h, CC BY 4.0, processed from NOAA's Open Data Dissemination
  archive), with a reproduction check against committed GRIB values on
  spent-year dates; second, the measured cost of the GRIB route. Scope
  cuts (fewer target hours, the 24-hour lead first, fewer years) and
  running the GRIB pull inside AWS are options for later. Nothing is
  chosen.
- **D81.12 Session 89's plan.** Record this entry; the SPEC 6 edit; the
  probe; record F131. Nothing from 2026-27 is read. Nothing is chosen.
```

---

## Step 2: the SPEC 6 edit

In SPEC section 6, in the **Stage B** bullet, after its last sentence,
which ends "their gates (DECISIONS D79, F129)." (it wraps across two
lines; at the time of writing, SPEC.md line 746), add this sentence,
wrapped to the bullet's width, and change nothing else:

```
The non-US competitor probe (DECISIONS D78.3) found that DWD's MOSMIX
keeps only about two days of issues (F130); daily saves of MOSMIX_L
single-station files are chosen in DECISIONS D81.
```

If that sentence cannot be found exactly, stop and report. Show the
before and after with `git diff -- SPEC.md`.

---

## Step 3: the stage C scoping probe (read only)

Give the URL (or dataset identifier) and access time (UTC) for every
item. Tag every item `verified` (seen in data or a listing read this
session), `documentation only` (read in the provider's documentation;
give the page), `secondary` (another source; give it) or `unknown`.

### 3.1 The dynamical.org GFS forecast archive (first)

**3.1.1 Metadata.** From dynamical.org's catalog page and the dataset's
own metadata, record:
- the dataset identifier, its access route (Icechunk via
  `dynamical-catalog`, or any other route it documents), the version,
  and the licence;
- the **first and last init time**, the init times per day, and any
  missing inits in 2021-03-24..2026-07-29 (count them; list them if
  fewer than 50);
- the **lead-time steps**: whether every hour from 24 h to 53 h is
  present, and the step size beyond;
- the grid (resolution, latitude and longitude convention) and the
  chunk layout along time, lead and space;
- the full variable list. For each, the name, units, level and its
  stated definition, in particular whether a field is instantaneous or
  an average or accumulation, and over what window;
- any statement on how values are stored (for example rounding or
  bit-trimming to save space), and on how and when the archive is
  updated or corrected.

**3.1.2 Field match to SPEC 8.** For each field behind SPEC 8's recipe
(2 m temperature; total cloud cover; 10 m wind, as u and v or speed;
2 m dew point; 850 hPa temperature; downward shortwave radiation at the
surface; the pressure field behind `pressure_tendency_3h_hpa`), say
whether the archive has it, at the same level, and with the same
definition (instantaneous, or the same averaging window) as the
committed values (F97, F98, F100, F101, F102). Give one row per field:
present or absent, same definition or different (say how). Also record
whether the archive holds 6-hour maximum and minimum 2 m temperature
(useful for the daily maximum), and their definition.

**3.1.3 Reproduction check (spent years only).** For each of the six
airports, on these dates: **the 1st of every month** from the archive's
first full month through **2026-07-01**, at the airport's own target
hour, cycle and lead under SPEC 7.2 (EGLC and LFPG 12z on D-1, lead 24
h; DSM 18z, lead 24 h; YSDU 00z, lead 26 h; RNO and KSFO 18z, lead 26
h; check each against SPEC 3.4 and 7.2 and use what they say if it
differs from this list):
- read the archive's value of each field that is present with the same
  definition (3.1.2);
- form the point value **the same way the record does** (SPEC 8.8 G6:
  bilinear from the four surrounding grid points, longitudes shifted by
  +360 where negative), with no elevation correction, so it is
  comparable with the committed raw values (for 2 m temperature,
  `t2m_raw`; for the others, the committed column before any transform,
  and for wind the speed from u and v in km/h as the record forms it);
- compare it with the committed value on that date in the committed
  processed files (SPEC 8.1's tables, and the B files and KSFO files
  named in F90 and F116). Use only dates whose valid time is on or
  before 2026-07-31.

For each airport and field, print: rows compared, rows missing from
either side, mean absolute difference, largest absolute difference, and
the number of exact matches at the committed precision (3 decimals).
Report only. **Do not judge pass or fail**; no threshold is set.

Also run the same comparison for 2 m temperature only at **one other
cycle and lead** per airport on the same dates, choosing leads 48 to 53
h where the committed data allow it. If no committed values exist at
other leads, say so and skip it.

**3.1.4 Speed and size.** Time one full read: the 2 m temperature series
at one airport (the four surrounding grid points), every init from the
archive's start to 2026-07-29T18:00 and every lead from 24 h to 53 h.
Report the wall time, the bytes transferred (if the library reports
them, otherwise estimate from chunk sizes and say so), and the rows read.
Then extrapolate, showing the arithmetic, to: all SPEC 8 fields present
in the archive, both leads, all six airports. Label this an estimate.

### 3.2 The GRIB route's cost (second)

Using the same source as the record (`noaa-gfs-bdp-pds`, SPEC 7.2), with
byte-range requests as the record does:
1. For **one spent-year day** (choose 2024-03-15), confirm by `.idx`
   listing that the 0.25 deg files exist for every forecast hour from
   f024 to f053 for all four cycles of the day before, and that each
   SPEC 8 field is present in each. Note any forecast hour where a field
   is missing or its averaging window differs (F97's radiation window
   point applies).
2. Fetch the SPEC 8 fields for the **24-hour lead only** (the 24 files
   f024..f029 of the four cycles on 2024-03-14), timing each request and
   recording its size. Decode nothing beyond what is needed to confirm
   the message is readable. Stay under the 500 MB limit; if it would be
   exceeded, stop at the limit and extrapolate from what was fetched.
3. Extrapolate, showing the arithmetic, to all 24 target hours, both
   leads, 2021-03-24..2026-07-31: total requests, total bytes and total
   wall time at the measured rate. Note that one global field serves all
   airports. Label this an estimate, and compare it with D81.11's
   planning figure.

### 3.3 Hourly observations (counts only)

For each of the six airports, from the **committed** raw observation
files (SPEC 3, 4.5), report: the date range held; whether the files hold
every report of the day or only reports near the target hour; and, if
every report, the number of days in 2021-03-24..2026-07-31 that have at
least one usable temperature report within 15 minutes of each whole hour
(SPEC 4.5 and 8.8 G2 and G3's rule), as a 24-row count per airport (the
hour, the number of days). Also report the usual minute past the hour of
routine reports at each airport. If the committed files hold only reports
near the target hour, say so, name the source and query that would give
all hours (from F-entries and the files' `.meta.txt`), and **do not
fetch anything**.

### 3.4 Daily-maximum sources (documentation, and counts only)

For each airport, record which of these exist, from documentation and,
where already committed, from the files (counts only, no values):
- maximum temperature groups in the METARs (the US 6-hour and 24-hour
  maximum groups; say whether they appear in the committed reports and
  how often, as a count);
- an official daily climate maximum (for example the NWS CLI product at
  the US airports, SYNOP 12-hour maximum `Tx` elsewhere), its day window
  (local midnight to midnight, a fixed UTC window, or other), and a
  public archive for it, from documentation only;
- the alternative of the maximum of the hourly reports, with the day
  window it would need at each airport.

Fetch nothing new for this step. Choose nothing.

---

## Step 4: records

1. **F131** in DECISIONS.md, after D81, under a dated heading
   `## <run date>: Session 89 finding: the stage C scoping probe`. It
   gives, with real findings only:
   - the Step 0, 1 and 2 results;
   - the dynamical.org metadata (3.1.1) in brief, and the field-match
     table (3.1.2);
   - the reproduction table (3.1.3): one row per airport and field;
   - the speed and size results and both extrapolations (3.1.4, 3.2),
     side by side, labelled estimates;
   - the hourly observation counts (3.3) in brief, and the daily-maximum
     sources table (3.4);
   - every reading made where this prompt is silent, listed for the
     owner to confirm;
   - packages installed and their versions; requests and bytes per
     route; confirmation that the temporary directory and virtual
     environment were deleted;
   - a "what this did not do" list: nothing from 2026-27 read; no score;
     no observed value printed; no account; nothing under `data/`; no
     existing script edited; no choice of data route, daily-maximum
     definition or airport; nothing committed.

   Keep F131 compact: full metadata, listings and per-request timings go
   in the output file, and F131 points to it.
2. Save the full real output of this session as
   `notes/session-89-output.txt`. Record the helper script's SHA-256.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include:
   - the forward test's state (D73, F122, D77.6, D79), unchanged, and
     that all three 2026-27 scripts exist and passed their gates (F128,
     F129), never run;
   - MOSMIX: F130 in brief, and the save choice (D81.2 to D81.5), with
     the saver session not yet run;
   - stage C: opened (D81.9, D81.10), and F131's outcome in brief, with
     the data route open (D81.11);
   - the carried items: **GFS v17 (D81.7)**, to be re-checked at each
     planning session; the EGLC position note (D81.6); MOSMIX matching
     (D80.4); and the remaining stage A/B uncertainties from session 88's
     STATUS.

   F130.9's readings are accepted (D81.1), so that open question is
   removed. STATUS must end with: "**Next planning session:** Review
   session 89. Then design stage C from F131: the data route, the
   daily-maximum definition and the new airports, for the next session
   to record. Re-check GFS v17 (D81.7)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-89-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79, F129, D80, F130, D81 and F131 stay live. Report
   what moved and why, or that nothing did.
5. Confirm the temporary directory and the virtual environment were
   deleted.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
