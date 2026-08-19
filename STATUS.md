# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 August 2026, after session 23._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Three
airports have passed the frozen bar (SPEC 5.3); a fourth, Dubbo, has been
rehearsed on its validation year and its method is now locked (DECISIONS
D39). Its single sealed-test look has not yet run. Stage 3 (pooling) is not
opened.

## Airports

Full per-airport facts live in SPEC 3.4; the full results table is SPEC 5.0.
Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | IN PROGRESS — verified on contact, pulled and gap-mapped, joined and rehearsed on its validation year, method locked (D39); sealed test not yet run |

All three passed airports beat both raw GFS and persistence on MAE over
their own sealed test year (SPEC 5.3). Margins ranged 6.3%–16.3% over raw
GFS on the sealed test years and 3.5%–16.1% on the rehearsal years — all
three test years fell on the same shared twelve months (SPEC 4.3, D13), so
the honest figure to quote is the range across six airport-years, roughly
3%–16%, not the best single result (DECISIONS F48).

Dubbo's own validation rehearsal (not yet a pass/fail result — SPEC 5.3 is
judged once, on the sealed test year, in a later session) beat all four
references: corrected MAE 1.283 degC against raw GFS 1.397 (8.2% better),
persistence 2.577 (50.2%), the mean-bias reference 1.368 (6.3%) and
climatology 2.888 (55.6%) — DECISIONS F62.

## Done

Full session-by-session history is in git (every prior version of this
file) and in DECISIONS.md / DECISIONS-archive.md. High points only:

- Stage 1 (EGLC) passed (session 07, DECISIONS F16).
- Stage 2 opened at CDG (D26) and passed (session 13, F30).
- A third airport, DSM, opened (D32) and passed (session 18, F47, F48) — the
  first non-European airport and the first with a target hour other than
  12:00 UTC (D33).
- A fourth airport, Dubbo (YSDU), opened (D36, D37) — the project's first
  Southern Hemisphere airport — verified on contact (session 19, F49–F56)
  and fully pulled and gap-mapped (session 20, F57–F59).
- SPEC is current: every passed airport reads "passed" throughout, Dubbo has
  its own row, and the two outstanding wording items (Q28, Q29) are closed
  (D38).
- Session 21: a one-time, authorised documentation restructure — no data,
  model, or pull touched. STATUS.md rewritten as this pure snapshot; SPEC
  3.2's three near-identical per-airport gap paragraphs collapsed into one
  general statement; DECISIONS-archive.md created, holding D1–D12 and four
  settled EGLC-only findings (F1, F4's block, F6, F11), moved verbatim, with
  pointers left in DECISIONS.md.
- Session 22: Dubbo's join and validation rehearsal, mirroring session 16
  (DSM). The join reconciled exactly against session 20's F59 drop
  predictions (1,193 / 360 kept rows for inner-training / validation; Dubbo
  loses one more day than the other three to the shared forecast gap
  because its 02:00 UTC target falls before the gap's last missing hour, and
  loses real observation-side days the other airports mostly did not).
  Dubbo's bias is a fourth distinct shape — CDG's calendar-driven structure,
  but concentrated into one local season — and the explicit flipped-season
  check found the largest bias sitting in Dubbo's own summer (Dec–Feb), not
  copying a Northern shape. The locked recipe, applied unchanged, beat all
  four references on Dubbo's validation year (F60–F63).
- Session 23 (this one): Dubbo's method lock, written and verified before
  the test year opens — the D35-equivalent for Dubbo, mirroring the
  two-session split used for CDG (D31/F30) and DSM (D35/F47). No model was
  run and Dubbo's test year was not touched. The lock (DECISIONS D39) is
  D35 with the airport and target hour swapped; a point-by-point
  correspondence check against D35 confirms no methodological choice
  differs beyond location and target hour, plus one genuine structural
  difference the check names explicitly: unlike DSM's zero, Dubbo's
  test-year drop prediction (356 of 365 paired rows, from F59's gap map) is
  not a clean single number for the final scored-day count, because 9
  scattered observation-side losses interact with persistence's
  day-before dependency in a way only the test session's actual dates can
  resolve. A single-season-concentration watch-item was recorded in advance
  (D39.12), mirroring D35.12's warm-end watch-item. SPEC §6's Dubbo bullet
  was updated to reflect all five steps completed so far except the test
  (the only SPEC edit authorised this session). One numbering note: the
  session prompt suggested D38 for this lock, but session 20 already used
  D38 for its own entry, so this lock is D39 instead — flagged explicitly
  in the DECISIONS entry.

## Next

**Dubbo's single sealed-test look**, executing D39 exactly as written.
Dubbo's test year (2025-08-01 to 2026-07-31) remains sealed and untouched.
The test session must name every date it drops on the observation side
(D39.7) rather than only reporting a count, since D39 could not predict the
exact scored-day figure in advance the way every earlier lock could.

## Open questions (live)

- **Q30 (partially closed).** The owner already picked its first branch —
  more airports — by opening Dubbo (D36). What remains open is what comes
  *after* Dubbo's own five steps finish (verify ✓, pull/map ✓, join and
  rehearse ✓, lock ✓, test once): another airport; a second test year (the
  untouched half of the F30/F46/F48 caveat — all three passes so far share
  the same twelve months); or stage 3, pooling (not opened).

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
