# Session 03 — the full historical pull

## Scope of this session

This session **downloads the full historical dataset** for both sources, over
the whole period, and checks it structurally. It also makes three small
confirmations the owner has now settled (preamble below).

Do **not** join the two datasets. Do **not** build, train, or evaluate any
model. Do **not** fill any gaps. Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. The
critical rules in SPEC section 2 apply throughout — especially 2.2
(drop-count-report, never fill), 2.3 (raw data immutable, provenance beside
each file), and 2.1 (no leakage).

Reminders on the working rules:
- **DECISIONS.md is append-only** — new entries at the bottom only.
- **SPEC.md may be edited only where authorised below** (the one Q7 edit).

---

## Preamble — three confirmations the owner has settled

**P-1. Record the model-string decision as D16 (append to DECISIONS).**
The owner has confirmed: pin the explicit model string **`gfs_global`** for
all forecast pulls, rather than `gfs_seamless`. Reason: session 02 (F6) proved
the two return identical data at EGLC over both a 2026 and a 2021 window, so
pinning costs nothing and makes "this is exactly NCEP GFS" true by
construction, protected against any future change to Open-Meteo's blending.
Use `gfs_global` for every forecast request in this session.

**P-2. Make this authorised edit to SPEC section 3.2 (Q7).**
The owner has approved making the lead-time wording honest. Replace the
sentence describing the lead-time offset so that section 3.2 states:
- the source is the Open-Meteo **Previous Runs API**, model **`gfs_global`**;
- the offset is **a nominal 24-hour lead, not an exact one**: because GFS runs
  every 6 hours and Open-Meteo stitches hours 24–29 of each run, the true lead
  sweeps between about **24 and 30 hours** across the day, then resets (see
  DECISIONS F5);
- **every value is nonetheless a genuine forecast made at least 24 hours
  before its valid time, so the no-leakage rule (2.1b) still holds.**
Keep the existing "confirmed back to 24 March 2021" note. Do not change any
other part of SPEC.

**P-3. Note Q9 as closed.** The owner has already run `git rm --cached
.DS_Store` and it is covered by `.gitignore`. Just confirm `.DS_Store` is no
longer tracked and note Q9 closed in DECISIONS/STATUS. No action on the file
itself.

---

## Part A — confirm which forecast variables are available (small probe)

Before the big pull, run a **small** probe (a few days, recent) to confirm
which candidate forecast variables are available at the `previous_day1`
offset for `gfs_global` at EGLC (lat 51.505, lon 0.055). Candidate list:

- `temperature_2m` — **required** (the forecast we correct, and a feature).
- `cloud_cover` — a strong driver of local temperature bias.
- `wind_speed_10m` — calm nights drive big biases.
- `dew_point_2m` — moisture (use `relative_humidity_2m` instead if dew point
  is unavailable at this offset).
- `surface_pressure` — synoptic-state proxy (or `pressure_msl`).

For each, report plainly whether it returns real values at the
`..._previous_day1` offset or comes back missing/rejected. This probe is just
an availability check — do not save it as part of the dataset.

**These extra variables are being acquired now only to avoid re-pulling later;
which (if any) become model features is a later modelling decision, not
settled here.** Temperature is the one that must be present.

## Part B — pull the full history for both sources

Pull the whole period **2021-03-24 to 2026-07-31** (this covers both the
training window and the sealed test window; pulling and storing the test data
is fine — it only must not be explored, see Part C).

**B-1. Forecast series (Open-Meteo Previous Runs API, `gfs_global`).**
- Location: EGLC, lat 51.505, lon 0.055.
- Variables: `temperature_2m` plus every other candidate from Part A that the
  probe confirmed available, all at the `previous_day1` offset, requested
  together in the same calls (so extra variables cost no extra requests).
- Pull in **yearly chunks** (e.g. one file per calendar year, plus the part
  years at each end) so a failure can resume without redoing everything.
- Save each chunk untouched in `data/raw/`, with a `.meta.txt` beside it
  recording the pull time and the exact request URL/parameters (SPEC 2.3).
- Be gentle: a short pause between calls; stay well within fair-use.

**B-2. Truth series (IEM ASOS/METAR, EGLC).**
- Pull the same period, same yearly-chunk approach, each chunk saved untouched
  with its `.meta.txt`.
- Keep the routine `:50` report as the hourly truth observation (D14, F3).
  Temperature is the designated truth field; other routine fields that arrive
  in the same response may be kept for the record.
- Respect IEM's 1-second per-IP throttle: at least a 1-second pause between
  requests.

## Part C — structural verification only (test set stays sealed)

Apply drop-count-report (2.2). For the **whole** period you may report
*structural* coverage — how many hourly rows are present, how many are
missing, and where the gaps fall — for **both** series.

**Keep the test set sealed.** For the test window (**2025-08-01 onward**), do
**only** structural checks (row presence, gap counts). Do **not** summarise,
plot, or explore the actual forecast or observed *values* in the test window —
no value ranges, no means, nothing about what the numbers are. That is saved
for the final evaluation, so the held-out set stays genuinely held out. For
the **training** window (up to 2025-07-31) a simple value-range sanity check
is fine.

Do **not** join the two series and do **not** fill anything — just count and
report gaps in each series separately.

---

## What to report at the end of the session

Paste **real output**, not descriptions:
- the Part A probe result (which variables are available);
- for each series: total rows pulled, date coverage, number of chunk files;
- gap counts per series across the whole period, and where notable gaps fall
  (structural only for the test window);
- a training-window-only value-range sanity check for temperature (both
  series), to catch anything obviously wrong (e.g. Kelvin vs Celsius);
- the exact before/after of the SPEC 3.2 edit;
- the new DECISIONS entries (D16 and any findings).

## What NOT to do

- Do not join the forecast and observation series.
- Do not build, train, or evaluate any model.
- Do not fill, interpolate, or clean away missing data.
- Do not explore or summarise the *values* in the test window (2025-08-01 on).
- Do not change SPEC beyond the authorised P-2 edit.
- Do not change or delete existing DECISIONS entries (append only).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, do not act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md to reflect what this session did and what is next
   (next: build the stage 1 pipeline — join using the D14 rule, then the
   correction model and the baseline comparison).
2. Add findings to DECISIONS.md (D16, the variable-availability result, the
   pull totals and gap findings). Note Q7 and Q9 closed.
3. Run the three-file consistency check and report anything that disagrees —
   report only, do not fix silently.
4. Write out a suggested commit message, then stop for the owner's review.
