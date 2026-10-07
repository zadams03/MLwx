# Session 10 — the full CDG (LFPG) pull and gap map

## What this session is

CDG's data was verified on contact (session 08). This session **pulls the full
CDG history** for both sources and maps every gap — the same job session 03b
did for EGLC, pointed at LFPG. It also settles three small open questions
(Q20, Q21, Q22).

Do **not** join the two series. Do **not** build, train, or evaluate any
model. Do **not** fill any gaps. Do only what is listed here, then stop.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply — especially 2.2 (drop-count-report, never fill), 2.3
(raw data immutable + provenance), 2.1 (no leakage).

DECISIONS is append-only. No SPEC edit is authorised **except B-3 below** (the
airport table's CDG gap marker and the EGLC network cell, once the facts are in
hand). Reminder from SPEC 3.4: table cells are filled from real pulls, never
from memory.

## The locked facts to use (from SPEC 3.4, session 08)

- Airport: **LFPG**, IEM network **`FR__ASOS`**, position **49.0153 N,
  2.5344 E**, elevation 109 m.
- Forecast: Open-Meteo **Previous Runs API**, model **`gfs_global`**,
  `temperature_2m` at the `previous_day1` offset — **temperature only** (D17
  applies per airport: stage 2 is the same temperature-only recipe).
- Target hour 12:00 UTC; pairing by D14; split dates D13.

---

## Part A — settle the two forecast questions while pulling (Q20, Q21)

**A-1. Q20 — confirm `gfs_global` at LFPG.** Session 08 already pulled
`gfs_global` samples for CDG successfully, so this is a confirmation, not a
reopening: use `gfs_global` for the full pull (D16, per-airport). No need to
re-probe `gfs_seamless` unless something looks wrong; if it does, stop and
flag rather than switching strings mid-pull. Note Q20 closed.

**A-2. Q21 — map whether CDG has a forecast gap.** This is answered by the gap
map in Part C, not assumed. EGLC had one 492-hour gap (F8); CDG may have the
same, a different one, or none. The pull must reveal it, hour by hour.

## Part B — pull the full history for both sources (mirror session 03b)

Pull the whole period **2021-03-24 to 2026-07-31** (training + sealed test;
storing the test data is fine — it only must not be explored, see Part C).

**B-1. Forecast series (Open-Meteo Previous Runs, `gfs_global`, LFPG).**
`temperature_2m` at `previous_day1`, at LFPG's coordinates. Pull in **yearly
chunks**, each saved untouched in `data/raw/` with a `.meta.txt` recording pull
time and the exact request (SPEC 2.3). Be gentle: short pause between calls,
keep the retry-with-backoff and resume-from-disk behaviour from 03b.

**B-2. Truth series (IEM ASOS, LFPG, `FR__ASOS`).** Same period, same
yearly-chunk approach, each chunk saved untouched with its `.meta.txt`. Keep
the routine on-the-hour (`:00`) report as the truth observation (F18); other
routine fields arriving in the response may be kept for the record. Respect
IEM's 1-second per-IP throttle.

**B-3. Settle Q22 while you are talking to IEM.** Make one small IEM metadata
request to confirm LFPG's network is `FR__ASOS` (already used) **and** to find
EGLC's true network code, so the airport-table cell currently marked
`GB__ASOS (unverified)` can be either verified or corrected. If confirmed,
update that one SPEC 3.4 cell to drop the "unverified" marker; if IEM returns
something else, correct it. This is the only authorised SPEC edit. Report what
IEM actually returned. Note Q22 closed.

## Part C — full gap map (structural; test set stays sealed)

Run the checks and produce a **complete map of gaps in both CDG series** — the
main deliverable, same shape as session 03b.

- For **each series separately**: total hourly rows present, total missing, and
  **where the gaps fall** (start/end dates and length of each gap run).
- **Answer Q21 explicitly:** does the CDG forecast series have a gap? If so,
  give its exact extent and whether it matches EGLC's 2023-12-30 to 2024-01-19
  window or differs. If none, say so plainly.
- Also report, for the observation series, **how many days are lost at 12:00
  UTC specifically to CDG's off-hour reporting** (the D30 concern — CDG's
  higher off-hour rate). This is the count SPEC 4.5 / D30 asked to be tracked
  separately.
- Apply drop-count-report (2.2): count, never fill. Do **not** join the series.
- **Keep the test set sealed.** For the test window (**2025-08-01 onward**), do
  only structural checks (row presence, gap locations). Do **not** summarise,
  plot, or explore the actual temperature *values* there. A training-window-only
  value-range sanity check (Celsius, nothing absurd) is fine.

---

## What to report at the end

Paste **real output**, not descriptions:
- confirmation `gfs_global` was used (Q20);
- for each series: total rows, date coverage, number of chunk files;
- the **gap map** for each series — every gap run with dates and length;
- the explicit Q21 answer (CDG forecast gap: yes/no, and where);
- days lost at 12:00 UTC to CDG's off-hour reporting (D30 count);
- what IEM returned for the network codes, and the SPEC 3.4 cell before/after
  (Q22);
- the training-window value-range sanity check.

## What NOT to do

- Do not join the forecast and observation series.
- Do not build, train, or evaluate any model.
- Do not fill, interpolate, or clean away missing data.
- Do not explore or summarise the *values* in the test window (2025-08-01 on).
- Do not edit SPEC beyond the single B-3 airport-table cell.
- Do not change or delete existing DECISIONS entries (append only).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: the CDG dataset is pulled and gap-mapped; next is the CDG
   join + validation rehearsal (mirroring session 04), with the test year
   sealed.
2. Append to DECISIONS: the pull totals, the gap-map findings (the Q21 answer),
   the D30 off-hour day-loss count, and the Q22 resolution. Mark Q20, Q21, Q22
   closed.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
