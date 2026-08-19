# Session 20 — Dubbo: SPEC row + housekeeping, then the full pull

## What this session is

Two jobs, in order. First, **update SPEC**: add Dubbo's rows, record that DSM
has now **passed** (its result is in DECISIONS F47 but SPEC still calls it "in
progress"/"pending"), and clear two long-deferred wording items (Q28, Q29).
Second, **pull Dubbo's full history** and gap-map it, mirroring session 15 for
DSM.

The SPEC edits are the careful part and come first, so the pull runs against an
agreed spec. Both are in one session to stay lean; report every SPEC
before/after clearly for review.

Before starting, read SPEC.md, STATUS.md, and DECISIONS.md in full. Critical
rules (SPEC 2) apply. **The meaning of the frozen bar (section 5) must not
change** — only the airport list, DSM's verdict, and two wording items move. If
any edit would alter what the bar requires, stop and flag it.

DECISIONS is append-only. The SPEC edits below are all authorised; make these
and only these.

---

## Dubbo's verified facts (from session 19, F49–F56)

- Code **YSDU**, IEM network **`AU__ASOS`**, position from IEM metadata (use the
  authoritative values session 19 recorded), inland eastern Australia, ~275 m.
- Target hour **02:00 UTC** = local standard noon (AEST, UTC+10; DST ignored,
  D37).
- Reports **on the hour** (`:00`) — exact 0-minute pairing, like LFPG. Files a
  scheduled half-hourly second report like EGLC/LFPG.
- Archive starts **2021-03-24 00:00 UTC** (fourth continent, same floor).
- `gfs_global` vs `gfs_seamless`: **identical** here (unlike DSM).
- Native whole-degree Celsius; `tz=UTC` verified true.

Fill Dubbo's table cells from session 19's actual recorded values, not from this
summary — check the session-19 notes/DECISIONS for the exact coordinates, grid
point, distance and elevations.

## Part A — SPEC edits (authorised only)

**A-1. §5.0 results table — record DSM's pass.** DSM's sealed test ran in
session 18 and **passed** (DECISIONS F47: corrected 1.700 vs raw GFS 1.815 vs
persistence 4.003, 365 test days). The table row currently reads "DSM — pending
— not yet run". Update it to **PASSED** with those figures, matching the format
of the EGLC and LFPG rows. Update the paragraph beneath if it still implies
DSM's look is untaken.

**A-2. §6 build order — record DSM's pass.** The Stage 2 list currently says
"Des Moines (DSM) — IN PROGRESS". Change to **PASSED**, citing its verify/pull/
rehearse/lock/test findings (F31–F37, F38–F41, F42–F46, D35, F47), mirroring how
the CDG line reads.

**A-3. §3.4 airport table — add Dubbo, both sub-tables.**
- First table: add a YSDU row — stage `2 — in progress`, target hour `02:00`,
  network `AU__ASOS`, and Dubbo's lat/lon/elevation from session 19.
- Second table: add a YSDU row — grid lat/lon/elevation, distance, height
  mismatch, `reports at :00`, `also files at` its scheduled half-hourly report,
  pairing offset `0 minutes`.
- Update DSM's stage cell in the first table from `2 — in progress` to
  `2 — passed`.

**A-4. §3.4 notes + §3.1 — resolve Q28 (the "ICAO" heading).** The code column
holds "whatever IEM addresses the station by" — ICAO for EGLC/LFPG, IEM's own id
for DSM, and for Dubbo **YSDU** (which *is* an ICAO code). The column heading
"ICAO" is no longer accurate for a mixed set. Rename the heading to something
accurate such as **`station code`** (or `code`), and adjust §3.1's wording
"requested by its ICAO code" to "requested by its station code (the first
column of the table)". Update the existing Q28 note to record this as resolved,
not pending. This closes Q28.

**A-5. §1 airport list — add Dubbo, mark DSM passed.** Update the bullet list:
DSM now **passed**; add **Dubbo (YSDU) — stage 2, in progress**.

**A-6. §3.3 verify-on-contact — resolve Q29 (the test-year wording).** The
verify-on-contact samples for EGLC/CDG/DSM used weeks inside the sealed test
year (harmless — nothing was fitted on them or any decision drawn from them, so
not leakage). Session 19 fixed this going forward by sampling Dubbo from 2021
and 2024 only. Add a sentence recording this precisely: the accurate claim is
**"no test-year data influenced any model, feature, or choice"**, and from
Dubbo onward verification samples are drawn from outside the test year. This
closes Q29 as an honest-wording item, not a leakage one.

Make **only** edits A-1 to A-6. If another change seems needed, log it as an
open question.

## Part B — pull Dubbo's full history (mirror session 15)

Pull **2021-03-24 to 2026-07-31** for both sources at Dubbo, temperature-only
(D17 per airport).

**B-1. Forecast (Open-Meteo Previous Runs, `gfs_global`, YSDU).**
`temperature_2m_previous_day1` at Dubbo's coordinates, yearly chunks, each saved
untouched in `data/raw/` with a `.meta.txt` (SPEC 2.3). Gentle; keep
retry/resume.

**B-2. Truth (IEM ASOS, YSDU, `AU__ASOS`).** Same period, yearly chunks,
provenance each. Routine on-the-hour report is the truth. Respect the 1-second
throttle. Keep temperature as the designated field; convert to Celsius as the
pipeline already does.

## Part C — full gap map (structural; test set sealed)

Same as session 15:
- for each series, total rows, total missing, **where gaps fall** (dates +
  length of each run);
- **does Dubbo's forecast series have the 492-hour gap** (2023-12-30 to
  2024-01-19)? Answer explicitly — same window, different, or none. (Three
  airports on two continents shared it; Dubbo is a fourth-continent test of
  whether it is truly archive-wide.)
- days lost at the **02:00 UTC** target specifically (drop-count, 2.2, nothing
  filled). Note any non-US report-cadence effect, though session 19 found Dubbo
  reports hourly.
- **Test set sealed:** for 2025-08-01 onward, structural checks only — no value
  summaries, no plots. Training-window value-range sanity check (Celsius) fine.

---

## What to report at the end

- the before/after of each SPEC edit (A-1 to A-6), and both airport sub-tables
  as written;
- confirmation the frozen bar's *meaning* is unchanged;
- for each Dubbo series: total rows, date coverage, chunk count;
- the gap map, and the explicit 492-hour-gap answer for Dubbo;
- days lost at the 02:00 UTC target; the training-window value-range check;
- the new DECISIONS entries.

## What NOT to do

- Do not join the series, build, train, or evaluate anything (that is the next
  session — Dubbo's join and rehearsal).
- Do not change the meaning of the frozen bar (section 5).
- Do not explore or summarise the *values* in the test window (2025-08-01 on).
- Do not edit SPEC beyond A-1 to A-6. Append-only for DECISIONS.
- Do not commit anything.
- Anything else worth doing → log in DECISIONS as an open question, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: SPEC now carries Dubbo and records DSM's pass; Q28/Q29
   resolved; Dubbo's data pulled and gap-mapped; next is Dubbo's join +
   validation rehearsal (mirroring session 16), test year sealed.
2. Append to DECISIONS: the SPEC updates, the pull totals, the gap-map findings
   (the 492-hour answer for Dubbo). Mark Q28, Q29 closed.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
