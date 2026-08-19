# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 August 2026, after session 22._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Three
airports have passed the frozen bar (SPEC 5.3); a fourth, Dubbo, has been
rehearsed on its validation year and is ready for its method lock and single
sealed-test look. Stage 3 (pooling) is not opened.

## Airports

Full per-airport facts live in SPEC 3.4; the full results table is SPEC 5.0.
Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | IN PROGRESS — verified on contact, pulled and gap-mapped, joined and rehearsed on its validation year; method lock and sealed test not yet run |

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
- Session 22 (this one): Dubbo's join and validation rehearsal, mirroring
  session 16 (DSM). The join reconciled exactly against session 20's F59
  drop predictions (1,193 / 360 kept rows for inner-training / validation;
  Dubbo loses one more day than the other three to the shared forecast gap
  because its 02:00 UTC target falls before the gap's last missing hour, and
  loses real observation-side days the other airports mostly did not).
  Dubbo's bias is a fourth distinct shape — CDG's calendar-driven structure,
  but concentrated into one local season — and the explicit flipped-season
  check found the largest bias sitting in Dubbo's own summer (Dec–Feb), not
  copying a Northern shape. The locked recipe, applied unchanged, beat all
  four references on Dubbo's validation year (F60–F63).

## Next

**Dubbo's method lock and single sealed-test look**, the D35-equivalent for
Dubbo, following the same two-session split used for CDG (D31/F30) and DSM
(D35/F47). Dubbo's test year (2025-08-01 to 2026-07-31) remains sealed and
untouched; the lock should be written before it is opened.

## Open questions (live)

- **Q30 (partially closed).** The owner already picked its first branch —
  more airports — by opening Dubbo (D36). What remains open is what comes
  *after* Dubbo's own five steps finish (verify ✓, pull/map ✓, join and
  rehearse ✓, lock, test once): another airport; a second test year (the
  untouched half of the F30/F46/F48 caveat — all three passes so far share
  the same twelve months); or stage 3, pooling (not opened).

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
