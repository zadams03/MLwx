# Session 88: the non-US competitor probe (D78.3), read only

Session 87 wrote and gated the 2026-27 scoring and competitor scripts
(F129); it is reviewed, committed and pushed. While period A runs, the
owner has chosen to run D78.3's read-only probe of non-US post-processed
station forecasts before stage C is opened, because DWD's MOSMIX may be
kept for only about two days on DWD's open data server. This session:

1. records **D80** (the owner's acceptance of F129.8, this choice, the
   probe's rules, the save options left open, and a GFS v17 note),
   before any other edit or any network call;
2. probes **DWD MOSMIX** against a fixed checklist (Step 2), reading only;
3. looks briefly at two other non-US products, only where this is cheap
   (Step 3);
4. records what it found as **F130**, and does the end-of-session steps.

It **chooses nothing**. Whether to save MOSMIX daily, what to save and
where (D72.8, D80.5), and any matching rule for a MOSMIX comparison are
left to the owner.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **Live forecast files: metadata only.** MOSMIX files on DWD's server
  (and any live file in Step 3) hold forecasts valid in 2026-27. You may
  download them, but you may print or record **metadata only**: issue
  time, referenced model runs, product and process names, element names
  and units, station IDs, names, positions and heights, the list of time
  steps, file names, sizes and times. **Never print, record, save or use
  any forecast value.** No value may appear in the output file.
- **No observations.** Do not read any observation file or source.
- **No scores.** Compute no error, MAE, skill or difference against
  anything, on any year.
- **No accounts or credentials.** Do not sign up, sign in, create keys or
  tokens, contact anyone, file any data request, or use any paid tier.
  If a source needs any of these, record exactly what it needs (from its
  documentation) and stop there for that source.
- **No installs.** Use only what is installed (Python's standard library
  `zipfile` and `xml` modules are enough for KMZ files). If a file cannot
  be read with what is installed, record "not decoded" and why.
- **Downloads.** All downloaded files go to one temporary directory
  outside the repo (`mktemp -d`), deleted at the end of the session.
  Size limits: MOSMIX_L single-station files as needed (they are small);
  **do not download a MOSMIX_L all-stations file** (about 80 MB each; a
  listing is enough); **at most one MOSMIX_S all-stations file**, and only
  if the listing shows it is under **200 MB**. Be polite: no bulk
  requests. Report the total number of requests and bytes.
- **Nothing under `data/`.** Write nothing under `data/` and do not touch
  `data/models/`.
- **Do not edit any existing script.** You may write one new helper
  script, `scripts/session88_competitor_probe.py`, for reproducibility. It
  only reads from the network and prints; it writes no data file, and it
  never prints a forecast value.
- Do not edit `SPEC.md`, `RESULTS.md`, `CLAUDE.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- No em-dashes in any new text, including code comments (D76.6).
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0: integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-88.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D79 and F129, and that no
   D80 or F130 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that `scripts/session88_competitor_probe.py` and
   `notes/session-88-output.txt` do not exist. If either exists, stop and
   report.
4. Read D72 (in particular D72.3 and D72.8), D77.1 and D77.2, D78 (in
   particular D78.1 and D78.3), F123 (the earlier source probe, whose
   checklist this session follows), F124 and D76.2, and SPEC 3.4, 4.1 and
   7.2 (the airport table, the target hour and the GFS lead-time
   convention).

---

## Step 1: record D80 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## <run date>: Session 88 decision: F129.8 accepted, the non-US competitor probe first, and its rules (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D80. Owner decisions, planning chat (after session 87): F129.8
accepted, the next step, and the rules of the non-US competitor probe
(D78.3).** Written at the start of session 88, before any other edit or
network call. No 2026-27 value has been read or scored.

- **D80.1 F129.8 accepted.** The owner accepts all eight readings in
  F129.8 as written: the timing guard over all six airports; no draws
  for a void comparison or one with fewer than 7 days; a zero-row
  airport is "no verdict (0 days)"; the season label; the persistence
  margin's day basis; the file names; the MAV projection handling; and
  no size trial in `--fetch`. Neither script changes; F129.7's SHA-256
  values stand.
- **D80.2 Next step: D78.3's probe before stage C.** The owner runs the
  read-only non-US competitor probe before stage C is opened. Reason:
  secondary sources say DWD keeps MOSMIX on its open data server for
  only about two days, so if MOSMIX is to be saved, every day of delay
  is lost for good.
- **D80.3 The probe's rules.** DWD MOSMIX first; other non-US
  post-processed station forecasts only where cheap (documentation and a
  handful of requests, no account). Candidates: the Bureau of
  Meteorology's forecasts at Dubbo and the Met Office's site-specific
  forecasts. Live files may be downloaded, but only their metadata is
  printed or recorded, never a forecast value; nothing is saved under
  `data/`. At most one MOSMIX_S all-stations file is downloaded, and only
  if it is under 200 MB. Recorded as F130.
- **D80.4 Matching is not decided.** The probe records MOSMIX's issue
  times, the model runs each issue is built on, and the leads to each
  target hour, beside D77.2's rule for NBM. Any matching rule for a
  MOSMIX comparison is the owner's later decision.
- **D80.5 Daily saves: options recorded, nothing decided (D72.8).** If
  F130 confirms short retention, the owner chooses later between:
  (A) no saving, so MOSMIX has no history anywhere; (B) MOSMIX_L
  single-station files at a short list (EGLC, LFPG and YSDU now, stage
  C's candidate airports later), all four daily issues, well under 1 MB
  a day; (C) the whole map, about 320 MB a day for MOSMIX_L, or only the
  2 m temperature at all stations. Where a saver would run: the owner's
  laptop (free; misses days it is off), GitHub Actions (free; scheduled
  runs can be late or skipped, and stop after 60 days without repo
  activity; the repo is public), or a small cloud machine or bucket
  (reliable; small cost). A saver is new code and needs its own session.
  A MOSMIX test on 2026-27 could still be pre-registered, since no
  2026-27 value has been scored, but it would cover only saved days.
- **D80.6 GFS v17 (planning-chat web search, 2026-10-01, not checked by
  this session).** Still no Service Change Notice. The newest SCN listed
  is SCN 26-87 (2026-09-22). The only v17 notices are still PNS 26-29
  and PNS 26-30. With 30 days' notice, the earliest go-live is about 31
  October 2026.
- **D80.7 Planning-chat notes on MOSMIX (2026-10-01, not checked by this
  session).** No retention period was found in DWD's MOSMIX pages. A
  listing of DWD's MOSMIX_L all-stations directory showed eight issues,
  28 Sep 21z to 30 Sep 15z, about 80 MB each: about two days. A 2022
  discussion in the wetterdienst project said no historical MOSMIX was
  available; Meteostat said it keeps only the latest forecast; a
  Fraunhofer group was said to sell some; DWD's PAMORE research service
  was said to hold about two years of past predictions, possibly not
  MOSMIX. All secondary; F130 checks them.
- **D80.8 Session 88's plan.** Record this entry; run the probe (D80.3);
  record F130. No SPEC edit. Nothing is chosen.
```

---

## Step 2: the MOSMIX probe

Everything here is read only. Give the URL and access time (UTC) for
every item. Tag every item `verified` (seen in a listing or a file read
this session), `documentation only` (read in official DWD documentation;
give the page), `secondary` (read in a non-DWD source; give it) or
`unknown` (not found). Where sources disagree, record each.

### 2.1 Retention (the main question)

1. **Listings.** List these directories on `opendata.dwd.de` and record,
   for each: the number of issue files, the oldest and newest issue time
   in the file names, each file's server time and size, and the span
   from oldest to newest issue:
   - `weather/local_forecasts/mos/MOSMIX_L/all_stations/kml/`
   - `weather/local_forecasts/mos/MOSMIX_S/all_stations/kml/`
   - `weather/local_forecasts/mos/MOSMIX_L/single_stations/<ID>/kml/`
     for each station found in Step 2.4.
   List the MOSMIX_L all-stations directory a second time at least six
   hours after the first (the next issue should appear and, if retention
   is a fixed count, the oldest should go). If the session cannot wait
   that long, say so and give one listing only.
2. **DWD's documentation.** Read DWD's MOSMIX product page (German and
   English), the MOSMIX procedure documentation (PDF), the KML format
   description, and DWD's open data help pages. Record any statement on
   how long files are kept, quoted exactly with its page, or "no
   statement found".
3. **Archives beyond the rolling window.** Check, by reading pages only:
   - DWD's own: the open data server for any MOSMIX archive folder; the
     Climate Data Center (`opendata.dwd.de/climate_environment/CDC/`)
     for any forecast archive; **PAMORE** (what it holds, whether MOSMIX
     is included, from when, and its terms of access).
   - Third parties: the wetterdienst project (its documentation and
     GitHub discussion 780), Meteostat, Open-Meteo's documentation, and
     any other public archive found by a short search. For each: does it
     hold past MOSMIX issues, from when, at which stations, how often,
     and on what terms.
   Contact nobody and file no request.

### 2.2 Live feed

From the listings and DWD's documentation: issue times per day for
MOSMIX_L and MOSMIX_S; the usual delay from issue time to file time;
file format (KMZ holding KML); and the `LATEST` file names. Read DWD's
change notices on the MOSMIX change page (in particular the newsletter
of 2024-07-01 on delivery times) and record the current issue times.

### 2.3 Fields

From one MOSMIX_L single-station file (and, if the size rule allows, the
one MOSMIX_S file): the element list; for the 2 m temperature element
(expected `TTT`) its definition and units from DWD's element list
(`weather/lib/MetElementDefinition.xml`); the time step; and the forecast
horizon. Metadata only.

### 2.4 Stations

Using DWD's MOSMIX station catalogue (the `.cfg` file on DWD's MOSMIX
page), find the MOSMIX station for **EGLC, LFPG and YSDU** (by ICAO code
where the catalogue has one, otherwise by name and position). For each,
record: ID, name, ICAO code if any, latitude, longitude and height; the
distance from the airport position in SPEC 3.4 and the height
difference; and whether it is a main (development) station or an
interpolation station, if DWD publishes this (look in the procedure
documentation and the product page's station table). If no station lies
within 10 km, record the nearest and stop there for that airport.
Confirm each station's single-station directory exists.

Also record, for DSM, RNO and KSFO only, whether a MOSMIX station exists
(ID and distance only). This is for information; nothing is compared.

### 2.5 Timing

From the KML header of one MOSMIX_L file per station: the issue time,
the referenced model runs (`ReferencedModel`: model names and run
times), and the time steps. Then, for each of EGLC and LFPG (target
12:00 UTC, SPEC 3.4) and YSDU (target 02:00 UTC):
- list every MOSMIX_L issue and every MOSMIX_S issue made on D-1 that
  covers the target hour on day D, with its lead in hours and the model
  runs it is built on;
- beside it, give our GFS cycle and lead for that airport under SPEC 7.2
  and D77.2 (floor(H/6)x6 UTC on D-1; EGLC and LFPG 12z, 24 h; YSDU 00z,
  26 h).
Record whether DWD's documentation says MOSMIX uses recent observations
as predictors, and if so how recent (quote it with its page). This
bears on fairness of any later matching. **Do not choose a matching
rule** (D80.4).

### 2.6 Version history

From DWD's MOSMIX change page: list each change with its date and a
one-line summary (for example coefficient retraining, station list
changes, delivery times, model input changes). This matters if any
saved history is ever used.

---

## Step 3: other non-US products (only where cheap)

For each, use documentation pages, listings and **no more than five
requests** in total per product. No account. Metadata only.

1. **Bureau of Meteorology (Dubbo).** Which public post-processed
   forecast covers Dubbo (for example its town forecasts on BoM's
   anonymous FTP or web feeds); whether it gives an hourly or a 02:00
   UTC temperature or only daily maximum and minimum; issue times;
   retention; any public archive; terms of use.
2. **Met Office site-specific forecasts.** What the product is, whether
   it covers London City, whether it is post-processed, what access needs
   (from its documentation), retention and any archive. If it needs an
   account or key, record that and stop.

Class each product (and MOSMIX) as in F123's checklist: **Deep archive**
(past issues downloadable from 2021-03-24 or earlier), **Shallow
archive** (give the start date), **No archive** (give the retention),
or **Blocked** (say what is needed).

---

## Step 4: records

1. **F130** in DECISIONS.md, after D80, under a dated heading
   `## <run date>: Session 88 finding: the non-US competitor probe`.
   It gives, with real findings only:
   - the Step 0 and Step 1 results;
   - **retention:** both listings' counts and spans, DWD's statement or
     "no statement found", and each archive route checked with its
     answer;
   - one summary table, one row per product: archive, retention, issue
     times, 2 m temperature (element and units), stations at EGLC, LFPG
     and YSDU (ID and distance), class, and the weakest evidence tag in
     the row;
   - the station table (Step 2.4) and the timing table (Step 2.5), with
     the referenced model runs and the observation-predictor statement;
   - the version history (Step 2.6), in brief;
   - the Step 3 results;
   - request and byte totals, and confirmation the temporary directory
     was deleted;
   - a "what this did not do" list: no forecast value printed, recorded
     or saved; no observation; no score; no account or request filed; no
     install; nothing under `data/`; no matching rule, save decision or
     stage C choice; nothing committed.

   Keep F130 compact: full URLs, listings and metadata go in the output
   file, and F130 points to it.
2. Save the full real output of this session, including every URL,
   listing and metadata excerpt (never a forecast value), as
   `notes/session-88-output.txt`. Record the helper script's SHA-256 if
   one was written.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot (pruned, not
   appended). Include:
   - the forward test's state (D73, F122, D77.6, D79) and that all three
     2026-27 scripts exist and passed their gates (F128, F129), unchanged;
   - that F129.8's readings are accepted (D80.1), so that open question
     is removed;
   - the probe's outcome in brief (F130), MOSMIX's retention and class,
     and that the save decision (D80.5) is open;
   - the carried items: **GFS v17 (D80.6)**, still no SCN as of
     2026-10-01, to be re-checked at each planning session; open item
     **D78.2**; and the remaining stage A/B uncertainties from session
     87's STATUS, updated for anything F130 closes.

   It must end with: "**Next planning session:** Review session 88. Then
   decide on MOSMIX daily saves (D80.5) and, if any, plan the saver
   session; otherwise open stage C. Re-check GFS v17 (D80.6)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-88-output.txt`** as well
   as reporting them in chat.
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, D77,
   F127, D78, F128, D79, F129, D80 and F130 stay live. Report what moved
   and why, or that nothing did.
5. Confirm the temporary directory was deleted.
6. Stop and wait for review. Do not commit. Do not write a commit
   message.
