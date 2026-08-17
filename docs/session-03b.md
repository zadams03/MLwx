# Session 03b — full historical pull, corrected to temperature-only

## Why this session exists

Session 03 was started but stopped partway. It found two real problems:
1. The four extra forecast variables (cloud cover, wind, dew point, pressure)
   only exist for **recent** data, not back through the archive.
2. There is a **real gap in the temperature forecast series in early 2024**
   (about 444 null hours), and the extra variables appear to begin where that
   gap ends — likely an Open-Meteo archive change.

The owner has now decided:
- **Stage 1 is temperature-only** on the forecast side. The extra variables
  are dropped for now (noted as a possible later enhancement, recent-period
  only).
- **Re-pull fresh** — discard the aborted run's partial chunks and pull a
  clean, uniform temperature-only dataset.

This session completes the full pull on that basis, maps every gap in both
series, and writes the record-keeping the aborted session never reached.

## Scope of this session

Do **not** join the two series. Do **not** build, train, or evaluate any
model. Do **not** fill any gaps. Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules in SPEC section 2 apply throughout — especially 2.2 (drop-count-report,
never fill), 2.3 (raw data immutable + provenance), 2.1 (no leakage).

Reminders: DECISIONS.md is append-only; SPEC.md is not edited in this session
(the one SPEC 3.2 edit was already made in the aborted run — just confirm it
is intact, see below).

---

## Preamble — record-keeping and cleanup

**P-1. Confirm the SPEC 3.2 edit is intact.** The aborted run already edited
SPEC 3.2 (pinned `gfs_global`, made the lead-time wording honest). Read
section 3.2 and confirm it reads correctly. Report its current text. Do not
re-edit it. If for any reason it is missing or wrong, stop and flag it rather
than guessing.

**P-2. Write the decisions that were never recorded (append to DECISIONS):**
- **D16 — pin `gfs_global`.** The owner confirmed pinning the explicit model
  string `gfs_global` for all forecast pulls (basis: session 02 F6 showed it
  is identical to `gfs_seamless` at EGLC). Closes Q8.
- **D17 — stage 1 is temperature-only on the forecast side.** The four extra
  candidate variables are available only for recent data (roughly 2024
  onward) and are entangled with the early-2024 discontinuity, so they are
  dropped for stage 1. Note them as a possible later enhancement, recent
  period only. Reason: stage 1 is the simplest clean test; temperature covers
  the whole archive; the extras add complexity and incomplete coverage.

**P-3. Discard the aborted run's partial raw chunks.** The forecast chunks on
disk from the aborted session used the wrong variable set and were never
committed. Remove them and their `.meta.txt` files so the fresh pull is clean
and uniform. Note in DECISIONS that they were discarded and re-pulled
temperature-only (so the record is honest). Do not touch anything already
committed.

---

## Part A — fresh forecast pull (temperature-only)

Source: Open-Meteo **Previous Runs API**, model **`gfs_global`**, at EGLC
(lat 51.505, lon 0.055).

- Variable: **`temperature_2m` at the `previous_day1` offset — this one only.**
- Period: **2021-03-24 to 2026-07-31** (covers training and the sealed test
  window; storing test data is fine, exploring its values is not — see Part C).
- Pull in **yearly chunks**, each saved untouched in `data/raw/` with a
  `.meta.txt` recording pull time and the exact request (SPEC 2.3).
- Be gentle: short pause between calls; the large full-year requests were
  dropping connections in the aborted run, so keep the retry-with-backoff and
  resume-from-disk behaviour.

## Part B — observation pull (never ran in the aborted session)

Source: IEM ASOS/METAR, station **EGLC**.

- Period: same **2021-03-24 to 2026-07-31**, same yearly-chunk approach, each
  chunk saved untouched with its `.meta.txt`.
- Keep the routine **`:50`** report as the hourly truth observation (D14, F3).
  Temperature is the designated truth field; other routine fields arriving in
  the same response may be kept for the record.
- Respect IEM's 1-second per-IP throttle: at least a 1-second pause between
  requests.

## Part C — full gap map (structural; test set stays sealed)

Run the checks script against the complete pull and produce a **complete map
of gaps in both series** — this is the main deliverable of this session.

- For **each series separately**, report: total hourly rows present, total
  missing, and **where the gaps fall** (start/end dates and length of each gap
  run, not just a count).
- **Pin down the early-2024 forecast gap exactly** — its precise start and end
  — and confirm whether it is the **only** gap of real size in the forecast
  series or whether there are others.
- Apply drop-count-report (2.2): count, do not fill. Do **not** join the
  series — count gaps in each one on its own.
- **Keep the test set sealed.** For the test window (**2025-08-01 onward**) do
  only structural checks (row presence, gap locations). Do **not** summarise,
  plot, or explore the actual temperature *values* there. A simple
  value-range sanity check (e.g. spotting Kelvin-vs-Celsius or absurd values)
  is fine for the **training** window only.

---

## What to report at the end of the session

Paste **real output**, not descriptions:
- confirmation the SPEC 3.2 text is intact (P-1), quoted;
- confirmation the aborted partial chunks were removed and re-pulled clean;
- for each series: total rows, date coverage, number of chunk files;
- the **gap map** for each series — every gap run with its dates and length;
- the exact extent of the early-2024 forecast gap, and whether any other
  sizeable gaps exist in either series;
- the training-window-only temperature value-range sanity check for both
  series;
- the new DECISIONS entries (D16, D17, findings, closures).

## What NOT to do

- Do not join the forecast and observation series.
- Do not build, train, or evaluate any model.
- Do not fill, interpolate, or clean away missing data.
- Do not explore or summarise the *values* in the test window (2025-08-01 on).
- Do not pull the extra forecast variables — temperature only (D17).
- Do not edit SPEC in this session (only confirm 3.2 is intact).
- Do not change or delete existing DECISIONS entries (append only).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, do not act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md to reflect what this session did and what is next
   (next: build the stage 1 pipeline — join using the D14 rule, then the
   correction model and the baseline comparison).
2. Ensure DECISIONS carries D16, D17, the variable-availability finding, the
   gap-map findings, and the note that the aborted chunks were re-pulled.
   Mark Q7, Q8, Q9 closed.
3. Run the three-file consistency check and report anything that disagrees —
   report only, do not fix silently.
4. Write out a suggested commit message, then stop for the owner's review.
