# Session 26 (corrected) — record the Bozeman→Reno switch, then onboard Reno

## Why this session opens by fixing the record

Session 25 verified **two** candidates (Bozeman and Reno) and its DECISIONS
entry (D40) and STATUS recorded **Bozeman (BZN)** as the chosen fifth airport.
After reviewing session 25's results, the owner **switched the choice to Reno
(KRNO)**. That switch was made in discussion and has **not yet been written into
DECISIONS or STATUS** — so the record still says Bozeman while the work should
proceed on Reno. A previous version of this prompt jumped straight to Reno and
the files-vs-prompt disagreement was correctly caught. This corrected session
**records the switch first**, then proceeds.

DECISIONS is append-only: **D40 stays exactly as written** (it is the honest
history — Bozeman was chosen at that moment). The switch is a **new** dated
decision that supersedes it, not an edit.

Before starting, read SPEC.md, STATUS.md, DECISIONS.md in full (and
DECISIONS-archive.md only if needed). Critical rules (SPEC 2) apply. The frozen
bar's meaning (section 5) must not change. Authorised SPEC edits are enumerated
below; make those and only those.

---

## Task 0 — record the Bozeman→Reno switch (do this first)

**D42 (or next free number) — fifth airport switched from Bozeman to Reno.**
Append a new decision recording:
- Session 25 (D40) chose Bozeman (BZN) as the fifth airport; on reviewing the
  verification the owner switched to **Reno (KRNO)**.
- **Why:** the fifth airport's job is a genuine *terrain-hard* test — does the
  correction deliver its biggest wins where GFS is worst. Bozeman's grid
  elevation mismatch was only −16 m and it sits in a **wide, grid-resolved
  valley**, so raw GFS handles it about as well as a flat airport — it is
  "high-altitude flat", not a terrain test. Reno sits in a valley **against the
  steep Sierra Nevada front** (foehn, downslope warming, cold-air drainage):
  its difficulty is **horizontal terrain complexity**, which the small vertical
  elevation mismatch (−1 m) does not capture, so it is the genuine terrain test
  even though its mismatch number also looks benign. Its true difficulty is
  only knowable by running it.
- D40 stands as the record of the earlier choice; this supersedes it. Bozeman
  is set aside (its verification, F66–F73, remains on record and could be
  revisited later if ever wanted).

Update STATUS to show the fifth airport is **Reno (KRNO)**, superseding
Bozeman.

---

## Reno's verified facts (from session 25, F66–F73 — read the recorded values)

Session 25 verified Reno alongside Bozeman. Use the values it actually recorded,
read from the session-25 notes / DECISIONS, not from this summary:
- Reno's station code / IEM network (Nevada), position and elevation (~1345 m),
  grid distance (~6 km) and grid elevation mismatch (~−1 m).
- **Target hour:** Reno is **US Pacific** (America/Los_Angeles), standard offset
  **UTC−8**, so local standard noon = **20:00 UTC** (DST ignored, D27/D33).
  **Confirm from the recorded timezone** — D41 computed 19:00 UTC for *Bozeman*
  (Mountain, UTC−7); Reno is Pacific and is one hour further, so **20:00 UTC**,
  not 19:00. Do not inherit Bozeman's hour.
- Report timing (US ASOS, `:53`/`:56`) — use session 25's recorded value;
  confirm the pairing offset at the 20:00 target.
- `gfs_global` vs `gfs_seamless` diverge sharply here (session 25: 258/264
  hours, up to 16.5 °C). Use `gfs_global` for the pull regardless (D16).

**Reno is the first genuinely terrain-hard airport.** Watch the mean-bias
reference at the eventual evaluation (no evaluation this session): beating it
well means terrain-dependent structure was learned; barely beating it means the
bias is mostly a fixed offset. Record this expectation, don't test it here.

## Part A — SPEC edits (authorised only)

**A-1. Record Dubbo's PASS everywhere it still says "in progress".** Dubbo's
sealed test ran in session 24 and passed (DECISIONS F64: corrected 1.210 vs raw
GFS 1.251 vs persistence 2.669, 347 scored test days). Update:
- **§1 airport list** — Dubbo bullet to **passed**.
- **§3.4 first table** — YSDU stage cell `2 — in progress` → `2 — passed`.
- **§5.0 results table** — add a YSDU row: `PASSED (stage 2, 347 test days) |
  1.210 vs 1.251 vs 2.669`. Update the paragraph beneath if it implies Dubbo's
  look is untaken.
- **§6 build order** — Dubbo bullet to **PASSED**, citing F49–F56, F57–F59,
  F60–F63, D39, F64, mirroring the DSM bullet.

**A-2. §3.4 airport table — add Reno, both sub-tables** (stage `2 — in
progress`, target hour **20:00**, network, position/grid values from session 25).

**A-3. §1 airport list — add Reno (KRNO) — stage 2, in progress**, noting it is
the first mountain/terrain-affected airport.

**A-4. §3.2 / §3.3 — add Reno to the verify-on-contact list** (its checks were
session 25). Leave a "gap pattern to be verified in this session" marker for the
492-hour question rather than assuming it; don't claim Reno's gap pattern before
Part C maps it.

Make only edits A-1 to A-4 (plus the Task 0 STATUS update). Anything else → log
as an open question.

## Part B — pull Reno's full history (mirror session 20)

Pull **2021-03-24 to 2026-07-31**, both sources, temperature-only (D17).

**B-1. Forecast** (Open-Meteo Previous Runs, `gfs_global`, Reno): yearly chunks,
each saved untouched in `data/raw/` with a `.meta.txt` (2.3), gentle,
retry/resume.

**B-2. Truth** (IEM ASOS, Reno, its network): same period, yearly chunks,
provenance each, routine on-the-hour report as truth, 1-second throttle,
Celsius conversion as the pipeline already does.

## Part C — full gap map (structural; test set sealed)

- for each series: total rows, total missing, **where gaps fall** (dates +
  length per run);
- **does Reno's forecast series have the 492-hour gap** (2023-12-30 to
  2024-01-19)? Answer explicitly — same window, its own scattered gaps like
  Dubbo, or none.
- days lost at the **20:00 UTC** target (drop-count, 2.2, nothing filled);
- **test set sealed:** 2025-08-01 onward — structural checks only, no value
  summaries. Training-window value-range sanity check (Celsius), and note
  whether Reno's training-window raw range looks wider/harder than the flat
  airports (structural observation, not a test-year figure).

---

## What to report at the end

- the D42 switch entry and STATUS update;
- the before/after of each SPEC edit (A-1 to A-4), both sub-tables as written;
- confirmation the frozen bar's meaning is unchanged;
- for each Reno series: total rows, date coverage, chunk count;
- the gap map and the explicit 492-hour answer for Reno;
- days lost at 20:00 UTC; the training-window value-range check;
- the new DECISIONS entries.

## What NOT to do

- Do not join, build, train, or evaluate anything (next session).
- Do not change the frozen bar's meaning.
- Do not explore the *values* in the test window (2025-08-01 on).
- Do not edit SPEC beyond A-1 to A-4; do not edit D40 (append the switch as D42).
- Do not commit anything.
- Anything else worth doing → log in DECISIONS, don't act.

## End-of-session steps (from CLAUDE.md)

1. Update STATUS.md: fifth airport is Reno (switch recorded); SPEC records
   Dubbo's pass and carries Reno; Reno pulled and gap-mapped; next is Reno's
   join + validation rehearsal (mirroring session 22), test year sealed.
2. Append to DECISIONS: D42 (the switch), the SPEC updates, the pull totals, the
   gap-map findings, Reno's target-hour confirmation.
3. Run the three-file consistency check — report only, don't fix.
4. Write a suggested commit message, then stop for the owner's review.
