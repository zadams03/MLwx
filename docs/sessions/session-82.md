# Session 82 — stage A's read-only source probe

Session 81 pre-registered the 2026-27 GFS forward test (D73) and froze its
models (F122). D72.13 sets this session to run stage A's read-only probe
of the other data sources. This session:

1. records **D74** (two housekeeping changes) before anything else;
2. makes the two edits D74 names: one sentence in SPEC 4.3, and one
   sentence in CLAUDE.md's end-of-session step 3;
3. probes each source against a fixed checklist (Step 3), reading only;
4. records what it found as **F123**, and does the end-of-session steps.

It **chooses nothing**. Which sources go forward (stage D/E), where or
whether to save any source (D72.8, session 83), and the NBM/MOS outcome
rule (D72.7) are all left to the owner.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 value from any source.** Do not download, open or decode
  any file, message or record dated 2026-08-01 or later, from any source
  (GFS, NBM, MOS or any other). For live feeds, a directory or bucket
  **listing** (file names, sizes, times) is allowed; nothing more.
- **No observations.** Do not read any observation file or source.
- **No scores.** Compute no error, MAE, skill or difference against
  anything, on any year.
- **No accounts or credentials.** Do not sign up, sign in, create keys or
  tokens, or use any paid tier. If a source needs any of these, record
  exactly what it needs (from its documentation) and stop there for that
  source.
- **No installs.** Do not install packages. If a file cannot be decoded
  with what is already installed, record "not decoded" and why.
- **Nothing under `data/`.** Write nothing under `data/` (raw or
  processed) and do not touch `data/models/`.
- **Do not edit any existing script.** You may write one new helper
  script, `scripts/session82_source_probe.py`, for reproducibility. It
  must only read from the network and print; it writes no data file.
- Edit `SPEC.md` and `CLAUDE.md` only as Step 2 says. Do not edit
  `RESULTS.md`, `README.md` or `PROJECT-INSTRUCTIONS.md`.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-82.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D73 and F122, and that
   no D74 or F123 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that `scripts/session82_source_probe.py` and
   `notes/session-82-output.txt` do not exist. If either exists, stop
   and report.
4. Read D72 (in particular D72.3, D72.7, D72.8), D73 (in particular
   D73.3, D73.8, D73.9), SPEC 8.1 and, in DECISIONS-archive.md, F85,
   F88 and F89 (the earlier source findings).

---

## Step 1 — record D74 (before any other edit or any network call)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## 2026-09-28 — Session 82 decision: SPEC 4.3 wording and the consistency-check rule (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped. Report the line range you copied.

```
**D74. Owner decision, planning chat (after session 81): two
housekeeping changes, and session 82's plan.** Written at the start of
session 82, before any network call.

- **D74.1 SPEC 4.3 clarified.** Its sentence "Data after 2026-07-31 is
  not used, which keeps the test set exactly one calendar year." is
  replaced by: "For the record's methods (sections 4, 7 and 8), data
  after 2026-07-31 is not used, which keeps the test set exactly one
  calendar year. The 2026-27 forward year is governed by DECISIONS D73."
  Why: the old sentence read as a ban on all later data, which D73's
  forward test contradicts. No method, date, figure or verdict changes.
- **D74.2 Consistency-check findings go into the output file.** From
  session 82 on, the end-of-session consistency check's findings are
  written into the session's output file (`notes/session-NN-output.txt`)
  as well as reported in chat. CLAUDE.md's end-of-session step 3 is
  amended to say so.
- **D74.3 Session 82's plan.** Stage A's read-only source probe
  (D72.3, D72.13): ECMWF (IFS open data and AIFS), ICON (global), GFS's
  ensemble GEFS, Google's WeatherNext, NBM and NWS MOS, plus whether GFS
  v17 retrospective runs are public, and Open-Meteo's Previous Runs API
  as a second route for each model. Read only; no 2026-27 value, no
  observation, no score, no account. Recorded as F123. It chooses
  nothing: which sources go forward, where to save (D72.8) and the
  NBM/MOS outcome rule (D72.7) stay with the owner.
- **D74.4 GFS v17 (planning-chat web search, 2026-09-28, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The SCN is due 30 days before go-live,
  so the earliest go-live is about late October 2026.
```

---

## Step 2 — the two edits D74 names

1. **SPEC 4.3.** Replace exactly this sentence:

   > Data after 2026-07-31 is not used, which keeps the test set exactly one calendar year.

   with:

   > For the record's methods (sections 4, 7 and 8), data after 2026-07-31 is not used, which keeps the test set exactly one calendar year. The 2026-27 forward year is governed by DECISIONS D73.

   (The sentence wraps across lines in the file; keep the file's line
   width.) Nothing else in SPEC changes.

2. **CLAUDE.md, "End of every session", step 3.** At the end of step 3
   (after "The owner decides."), add this sentence:

   > Write the findings into the session's output file (`notes/session-NN-output.txt`) as well as reporting them in chat.

   Nothing else in CLAUDE.md changes.

Show the diff of both edits.

---

## Step 3 — the source probe

### 3.1 What is probed

| # | Source | Product(s) | Airports it could serve |
|---|---|---|---|
| 1 | ECMWF | IFS open data (0.25°); AIFS open data | all six |
| 2 | DWD ICON | ICON global only | all six |
| 3 | NOAA GEFS | GEFS (0.25° and 0.5° where they differ) | all six |
| 4 | Google WeatherNext | the current WeatherNext product(s) | all six |
| 5 | NOAA NBM | National Blend of Models, gridded GRIB2 | DSM, RNO, KSFO (CONUS) |
| 6 | NWS MOS | GFS-based MOS (and any other MOS) at KDSM, KRNO, KSFO | DSM, RNO, KSFO |
| 7 | GFS v17 retrospective runs | whether they are public; if so where | all six |
| 8 | Open-Meteo Previous Runs API | as a **second route** for sources 1–4 | all six |

For source 8: record, per model, whether the Previous Runs API offers
it, from what date, and which fields at which offsets. Recall F85:
pressure-level fields were rejected on every `_previous_dayN` offset for
GFS; check whether the same holds for each model. The Historical
Forecast API is never a route (SPEC 2.1b); do not use it.

### 3.2 The checklist, for every source

**(a) Archive.**
- Where it is held (URL, bucket or service) and how it is accessed
  (anonymous HTTPS/S3, free registration, account, paid).
- The earliest **genuine past forecast run** (a real archived run with a
  known issue time, not reanalysis and not a stitched freshest-run
  product). Confirm the floor with a listing at or near that date, not
  from documentation alone where a listing is possible.
- Cycles per day, and whether the 24-hour and 48-hour leads are covered
  at hourly or coarser steps (give the step).
- Grid resolution and projection.
- **Model-version changes inside the archive**, with dates (for example
  IFS cycle upgrades, NBM v4.x, GEFS v12.3.x). Note any planned change
  that is documented, such as GEFS changing alongside GFS v17.

**(b) Live feed.**
- Where it is, how long files stay available (the retention window),
  and the usual delay after the cycle time.

**(c) Fields.** For each SPEC 8 input, whether the source offers it, its
name, level and time step, and for radiation its averaging or
accumulation window:
2 m temperature; total cloud cover; 10 m wind (u and v, or speed); 2 m
dewpoint (or what it could be derived from); 850 hPa temperature;
surface or mean-sea-level pressure at 3-hourly or finer spacing;
downward shortwave radiation at the surface.

**(d) Coverage.** Which of the six airports it covers.

**(e) Class.** Exactly one of:
- **Deep archive:** genuine past runs downloadable from 2021-03-24 or
  earlier;
- **Shallow archive:** downloadable, but starting later (give the date);
- **No archive:** live feed only (give the retention window). These are
  the candidates for session 83's daily saving;
- **Blocked:** needs an account, credentials or payment (say which).

**Evidence tag on every item:** `verified` (seen in a listing or a
decoded message this session), `documentation only` (read in official
documentation; give the page), or `unknown` (not found). Give the URL and
access date for each item. Where documentation and a listing disagree,
record both.

### 3.3 What is allowed

- Reading web pages and official documentation.
- Directory and bucket listings, `.idx` or inventory files, and HTTP HEAD
  requests.
- **Sample decodes**, to confirm a field's name, level, time step, units
  and grid:
  - only files dated **on or before 2026-07-31**;
  - byte-range fetches of single messages where the format allows; at
    most 10 messages per source, none larger than 20 MB;
  - print **metadata only** (name, level, step or window, units, grid
    size and spacing). Do not print, extract or save any value at any
    airport or grid point;
  - write samples only to a temporary directory outside the repo
    (`mktemp -d`), delete it at the end of the session, and report the
    deletion.
- Be polite to every service: no bulk requests.

### 3.4 GFS v17 retrospective runs (source 7)

Record: whether NOAA has published v17 retrospective or reforecast runs;
where; what dates they span; whether they are operational-configuration
(not an older test version); grid and format; which of the 3.2(c) fields
they carry; and access. Use documentation and listings only; no decodes
of v17 data dated after 2026-07-31.

### 3.5 NWS MOS (source 6)

Record: which MOS products exist for KDSM, KRNO and KSFO (for example
GFS MOS short- and extended-range); where they are archived and from
what date; what element gives the 2 m temperature at each airport's
target hour (SPEC 4.1) or the nearest projection time, and at what
projection steps; whether the product changed version inside the
archive; and access. Confirm the stations appear in an archived file
dated on or before 2026-07-31; do not extract or use any forecast value.

### 3.6 Models not probed

Add one line to F123, with no investigation: "Other global models not
probed this session: UK Met Office global, Environment Canada GDPS, JMA
GSM. Recorded only so they stay visible (D74.3)."

---

## Step 4 — records

1. **F123** in DECISIONS.md, after D74, under a dated heading
   `## 2026-09-28 — Session 82 finding: stage A's source probe`.
   It records, with real findings only:
   - Step 0 (git status) and Step 1 (the D74 line range copied);
   - the Step 2 diffs, in one line each;
   - **one summary table**, one row per source and product: archive
     floor, access, 24 h / 48 h lead coverage and step, the seven
     3.2(c) fields present (a compact yes/no per field), airports
     covered, class, and the weakest evidence tag in that row;
   - a short paragraph per source: version changes inside the archive,
     retention window, anything surprising, and anything `unknown`;
   - the Open-Meteo second-route results;
   - the GFS v17 retrospective answer and the MOS answer;
   - **the list of sources classed "No archive"** (the input to session
     83), and the list classed "Blocked";
   - the Step 3.6 line;
   - a "what this did not do" list: no 2026-27 value, no observation, no
     score, no account, no install, nothing under `data/`, no choice of
     source, save location or outcome rule, nothing committed.

   Keep F123 compact: full URLs, listings and decoded metadata go in the
   output file, and F123 points to it.
2. Save the full real output of this session, including every URL,
   listing excerpt and decoded metadata, as `notes/session-82-output.txt`.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot. Include: the
   forward test's state (D73, F122) and the hold rule (D73.8), unchanged;
   the probe's outcome in brief (F123), including the "No archive" and
   "Blocked" lists; the GFS v17 carried item (D74.4; re-check each
   planning session); and which stage A/B uncertainties the probe closed
   and which remain. It must end with: "**Next planning session:** Review
   session 82. Then draft session 83: daily collection for any source
   F123 classes as no-archive; if there is none, stage A's benchmark."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-82-output.txt`** as
   well as reporting them in chat (D74.2).
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122 and F123
   stay live. Report what moved and why.
5. Confirm the temporary sample directory was deleted.
6. Stop and wait for review. Do not commit. Do not write a commit message.
