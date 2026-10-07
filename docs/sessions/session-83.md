# Session 83 — the ICON route check and confidence intervals (stage A)

Session 82 ran stage A's read-only source probe (F123). It classed DWD
ICON global as "No archive" (about 24 h on DWD's server). Before deciding
whether the project saves ICON itself (D72.8), the owner wants three
facts about Open-Meteo's ICON routes checked. Stage A also includes
confidence intervals for the results on record (SPEC 5.4, D72.3). This
session:

1. records **D75** (the plan, written before any network call or data
   read);
2. runs a **read-only ICON route check** against Open-Meteo, printing
   counts only, and records it as **F124**;
3. computes **confidence intervals** for every result on record, after a
   reproduction gate, and records them as **F125**;
4. does the end-of-session steps.

It **decides nothing about ICON**: the owner decides after reviewing F124
(D75.1). The intervals **change no verdict**.

---

## Hard scope guard (read before anything else)

- SPEC section 2 applies in full.
- **No 2026-27 value from any source.** No request may ask for, and no
  script may keep, any value valid on or after 2026-08-01. If a response
  holds any valid time after 2026-07-31T23:00 UTC, discard it without
  reading its values, report that it happened, and stop that sub-check.
- **ICON check (Step 2): no forecast value is printed or saved.** Print
  only HTTP status, error reasons, grid metadata, valid-time ranges,
  present/null counts and match counts. **No observations** are read in
  Step 2, and nothing is scored.
- **Confidence intervals (Step 3):** read **committed files only**; no
  network. Do not change, retune, reselect or re-lock anything. Every
  model is refit exactly as recorded (same features, column order, rows,
  frozen settings), or predictions already saved are reused.
- **Do not edit, bypass or disable the reserved-year guard (D51) or any
  other guard in any existing script.** New code may import functions
  from existing scripts but must not change them. If refitting a result
  needs a guarded path that cannot be used without changing it, stop and
  report for that result.
- **Do not edit any existing script.** You may write exactly two new
  scripts: `scripts/session83_icon_route_check.py` and
  `scripts/session83_confidence_intervals.py`.
- **Nothing under `data/`.** Write nothing under `data/` and do not
  touch `data/models/`.
- **No installs, no accounts.**
- Do not edit `SPEC.md`, `CLAUDE.md`, `RESULTS.md`, `README.md` or
  `PROJECT-INSTRUCTIONS.md`.
- If anything needs a design choice this prompt does not make, **stop and
  report**. Do not choose.

---

## Step 0 — integrity checks

1. `git status --porcelain`. Report it. Expected: only
   `?? docs/session-83.md`. Anything else: stop and report.
2. Confirm that DECISIONS.md's last entries are D74 and F123, and that no
   D75, F124 or F125 exists in DECISIONS.md or DECISIONS-archive.md.
3. Confirm by path check that neither new script and
   `notes/session-83-output.txt` exist. If any exists, stop and report.
4. Read D72 (D72.3, D72.7, D72.8), D73, D74, F122 and F123 (in
   particular F123.5 and F123.7). In DECISIONS-archive.md, read F5, F89,
   and the result entries Step 3 uses: F16, F30, F47, F64, F82 (minimal
   method), F94 (richer method), F109 (selected method) and F119 (KSFO),
   plus D21.8, D58 item 6, D51 and D70.

---

## Step 1 — record D75 (before any other edit, network call or data read)

Append the text in the code block below to the end of `DECISIONS.md`,
under a dated heading
`## 2026-09-29 — Session 83 decision: the ICON route check and confidence intervals (owner, planning chat)`,
with a `---` separator before it as the file's style requires. Copy it
**mechanically** (for example with `sed` on this file's line range), not
retyped, and check it byte-equal with `diff`. Report the line range.

```
**D75. Owner decision, planning chat (after session 82): session 83's
plan.** Written at the start of session 83, before any network call or
data read.

- **D75.1 ICON: checked first, decided after.** F123 classed DWD ICON
  global as "No archive" (about 24 h). The planning chat found two
  Open-Meteo routes in documentation (2026-09-29, not checked by this
  session): Previous Runs (`icon_global`, from 2024-01-19, no 850 hPa
  temperature at any offset, F123.5) and Single Runs (any run by its
  initialisation time, most models from 2026-04-02; its variable list
  includes 850 hPa temperature). Session 83 checks, read-only and on
  valid times no later than 2026-07-31 (F124):
  (a) the first day `shortwave_radiation_previous_day1` and `_day2` are
  present, against `temperature_2m_previous_day1`'s floor;
  (b) whether Single Runs serves `icon_global` from 2026-04-02, with 850
  hPa temperature, and all four cycles (00, 06, 12, 18 UTC);
  (c) whether `temperature_2m_previous_day1` at each hour H equals the
  Single Runs value from the run at floor(H/6)x6 UTC on the day before,
  at lead 24 + (H mod 6): the GFS convention (F5, F89).
  The owner decides whether the project saves ICON (D72.8) after
  reviewing F124. Stated in advance: if 850 hPa temperature is present,
  the project does not save ICON; if it is absent, the owner chooses
  between saving ICON natively (to get 850 hPa temperature) and using
  ICON without feature L.
- **D75.2 Confidence intervals (stage A; SPEC 5.4, D72.3).** For every
  result on record: F16, F30, F47, F64, F82 (minimal method), F94
  (richer method), F109 (selected method) and F119 looks A and B
  (KSFO). Descriptive only: they change no verdict and are not a new
  look. They reuse the spent years (sealed 2025-26, reserved 2024-25)
  descriptively; no verdict, selection or build choice is drawn from
  them (SPEC 2.5). Gate first: every MAE recomputed must equal its
  recorded figure at the entry's precision; a result that fails gets no
  interval. Statistic: the paired per-day MAE difference (reference minus
  model, degC) and skill (1 - model/reference), model against raw GFS
  and against persistence, on the days both have. Method: moving-block
  bootstrap, 7-day blocks, 10,000 resamples, seed 83, 95% percentile
  interval. Recorded as F125.
- **D75.3 Carried.** The owner's decision on session 82's MOS near-miss
  (F123.9) is deferred to the NBM/MOS outcome rule (D72.7, D73.8), and
  is taken when that rule is written.
- **D75.4 GFS v17 (planning-chat web search, 2026-09-29, not checked by
  this session).** Still no Service Change Notice; only the April 2026
  proposals (PNS 26-29, 26-30). The earliest go-live is about late
  October 2026.
```

---

## Step 2 — the ICON route check (F124)

Write `scripts/session83_icon_route_check.py`. It uses `requests` only
(already installed), reads the network and prints; it writes no data
file. Location for every request: EGLC, latitude 51.5053, longitude
0.0553 (SPEC 3.4). Model: `icon_global`. Use the default grid-cell
selection. Endpoints:

- Past runs: `https://previous-runs-api.open-meteo.com/v1/forecast`
- Single runs: `https://single-runs-api.open-meteo.com/v1/forecast`

For every response print: the request URL, HTTP status, any error
reason (first 150 characters), the returned grid latitude, longitude and
elevation, and the first and last valid time. Apply the scope guard's
valid-time rule before reading any value. Retry a failed request at most
3 times, politely spaced.

**2(a) Radiation floor on the past-run route.** Request 2024-01-17 to
2024-01-21, hourly
`shortwave_radiation_previous_day1,shortwave_radiation_previous_day2,temperature_2m_previous_day1`.
For each variable print present/null hour counts and the first present
valid time. If radiation is null through 2024-01-21, widen the window in
steps of one month, up to 2024-12-31, and report its first present day.

**2(b) Single Runs: floor, 850 hPa temperature, 18z cycle.** Request
hourly `temperature_850hPa,temperature_2m,shortwave_radiation` with
`forecast_hours=48` for these runs:
- `run=2026-04-01T18:00` (expected before the archive floor: report
  what comes back);
- `run=2026-04-02T00:00`;
- `run=2026-07-29T18:00`.

For each, print present/null counts per variable.

**2(c) Timing.** Request the past-run
`temperature_2m_previous_day1` for 2026-06-11 (one day, 24 hours), and
Single Runs `temperature_2m` with `forecast_hours=54` for
`run=2026-06-10T00:00`, `T06:00`, `T12:00` and `T18:00`. For each hour H
of 2026-06-11, test whether the past-run value is exactly equal to the
value at the same valid time in the run at floor(H/6)x6 UTC on
2026-06-10 (lead 24 + (H mod 6)). Print the number of hours that match
out of 24. For each hour that does not, print only the hour and which
other 2026-06-10 runs (if any) hold an equal value. Also print present/
null counts for all five responses, so the 06z and 12z cycles' presence
is recorded.

Print no value. Put the full real output in `notes/session-83-output.txt`.

---

## Step 3 — confidence intervals (F125)

Write `scripts/session83_confidence_intervals.py`. No network.

### 3.1 The results

| result | method | airports | test window | day basis (as recorded) |
|---|---|---|---|---|
| F16, F30, F47, F64, F82 | minimal (SPEC 1–6) | EGLC, LFPG, DSM, YSDU, RNO | 2025-08-01..2026-07-31 | one common day set (D21.8) |
| F94 | richer, 5-feature (SPEC 7) | same five | 2025-08-01..2026-07-31 | raw and model on all test days; persistence on days with a previous-day observation |
| F109 | selected, `B+D,L,R,T` (SPEC 8) | same five | 2024-08-01..2025-07-31 | as F94 (D58 item 6) |
| F119 look A / look B | selected (SPEC 8) | KSFO | 2024-25 / 2025-26 | as F94 (D70) |

That is 17 airport-results. For F94 the model is the 5-feature model; for
F109 and F119 it is `B+D,L,R,T`. Intervals are computed only against the
bar's two references: raw GFS (as each entry defines it: Open-Meteo for
the minimal method, elevation-adjusted GRIB for the others) and
persistence.

### 3.2 Per-day errors and the reproduction gate

1. For each result, first look for per-day predictions already saved in
   committed files. Report what you find and use them if they exist.
2. Otherwise refit exactly as the entry records, from committed
   processed files only. Session 81's `--gate` (F122.4) refit F109 and
   KSFO look B this way and reproduced them exactly; follow the same
   approach, importing from existing scripts where possible.
3. **Gate.** Before any interval: recompute each rung's MAE (model, raw
   GFS, persistence) on its recorded day basis and compare with the
   figure recorded in the entry, at the entry's printed precision. Print
   both. If any figure differs, that result gets **no interval**: report
   it and continue with the others. Also report each result's day
   counts against the entry's.

### 3.3 The intervals

For each result and each reference (raw GFS, persistence):

- **Paired day set:** the days on which both the model and that
  reference have an error. For the minimal method this is the common day
  set. For the others, the raw-GFS set is every test day and the
  persistence set is the persistence day set. Print n. On the
  persistence set, also print the point estimates recomputed on that
  set, since they can differ slightly from the recorded figures (which
  use the model's all-day MAE).
- **Statistics:** d = MAE(reference) - MAE(model), in degC, and skill =
  1 - MAE(model)/MAE(reference), in %.
- **Moving-block bootstrap:** order the paired days by date. A block is
  7 consecutive entries of that ordered list. Draw block start positions
  uniformly from 0..n-7, concatenate ceil(n/7) blocks, truncate to n.
  Use the same resampled days for model and reference. 10,000 resamples,
  `numpy.random.default_rng(83)`, one generator for the whole run, with
  results processed in the table's order (3.1), airport order EGLC,
  LFPG, DSM, YSDU, RNO, then raw GFS before persistence.
- **Report:** the point estimate and the 2.5th and 97.5th percentiles of
  d and of skill, and whether the interval for d lies wholly above zero.

Put the full real output in `notes/session-83-output.txt`.

---

## Step 4 — records

1. **F124** in DECISIONS.md, after D75, under a dated heading
   `## 2026-09-29 — Session 83 finding: the ICON route check`. It gives
   the Step 0 and Step 1 results, then answers (a), (b) and (c) each in
   one or two lines with its counts, and adds a "what this did not do"
   list: no value printed or saved, no observation, no score, no valid
   time after 2026-07-31, no ICON decision. Compact; the output file
   holds the detail.
2. **F125** after F124, under a dated heading
   `## 2026-09-29 — Session 83 finding: confidence intervals for the results on record`.
   It gives: the gate result for each of the 17 airport-results; one
   compact table per method, with columns: airport, reference, n, d
   (degC) with its 95% interval, skill (%) with its 95% interval,
   interval for d wholly above zero (yes/no); and these statements,
   verbatim:
   - "These intervals describe day-to-day sampling within one test year
     only. They do not capture year-to-year variation (see F96)."
   - "The five airports in F16–F82, F94 and F109 share each test year's
     weather, so their intervals are not independent."
   - "These intervals change no verdict (D75.2)."

   Then a "what this did not do" list: nothing refit differently,
   retuned, reselected or re-locked; no network; nothing under `data/`;
   no verdict changed.

---

## End-of-session steps (CLAUDE.md)

1. Paste the real output of each step's checks.
2. **Overwrite STATUS.md** as a current-only snapshot. Include: the
   forward test's state (D73, F122) and the hold rule (D73.8),
   unchanged; F123's source table in brief; F124's three answers and
   that the ICON decision is the owner's, pending (D75.1, with its
   stated-in-advance rule); F125 in brief (one line per method); and
   these carried items:
   - **GFS v17 (D75.4).** Still no Service Change Notice as of
     2026-09-29. Re-check at each planning session. The go-live date
     sets period A's length. PNS 26-30's statement that the 0.25 degree
     GRIB2 files remain is to be confirmed against the SCN (D73.4).
   - **Session 82's MOS near-miss (F123.9).** The owner's decision is
     deferred to the NBM/MOS outcome rule (D72.7, D73.8) and is taken
     when that rule is written (D75.3).
   - The remaining stage A/B uncertainties from the session-82 STATUS
     that this session did not close.

   It must end with: "**Next planning session:** Review session 83. Then
   the owner decides whether the project saves ICON, from F124 (D75.1).
   Then design session 84: the NBM/MOS comparison and its outcome rule
   (D72.7), including the carried F123.9 decision and whether 2026-27
   gets a pre-registered NBM/MOS test (D73.8)."
3. **Consistency check:** re-read SPEC, STATUS and DECISIONS; report
   disagreements, duplicated headings and out-of-order entries. Report
   only. **Write the findings into `notes/session-83-output.txt`** as
   well as reporting them in chat (D74.2).
4. Archive step, per the criterion in CLAUDE.md. D72, D73, F122, F123,
   D75, F124 and F125 stay live. Report what moved and why.
5. Stop and wait for review. Do not commit. Do not write a commit
   message.
