# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 August 2026, after session 24._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have now passed the frozen bar (SPEC 5.3), the fourth being Dubbo,
tested this session (DECISIONS F64). Stage 3 (pooling) is not opened. SPEC
itself was not edited this session (none was authorised) and still reads
Dubbo as "in progress" with no test-year row — flagged below and in this
session's consistency check.

## Airports

Full per-airport facts live in SPEC 3.4; the full results table is SPEC 5.0
(SPEC's own copy is now out of date for Dubbo — see "Open questions" below).
Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |

All four passed airports beat both raw GFS and persistence on MAE over their
own sealed test year (SPEC 5.3). Margins over raw GFS ranged 3.3%–16.3% on
the sealed test years and 3.5%–16.1% on the rehearsal years — all four test
years fell on the same shared twelve months (SPEC 4.3, D13), so the honest
figure to quote is the range across eight airport-years, roughly 3%–16%, not
the best single result (DECISIONS F48, F65).

Dubbo's sealed test (DECISIONS F64): corrected MAE 1.210 degC against raw
GFS 1.251 (3.3% better) and persistence 2.669 (54.7% better) — the narrowest
margin over raw GFS of any airport tested so far, and the thinnest evidence
yet that the correction is structure rather than a constant offset (2.3%
over the mean-bias reference, against 15.7%/13.0%/3.4% at EGLC/CDG/DSM).
D39.12's single-season watch-item, recorded before the look, turned out to
be exactly where the margin eroded: the one season that carried almost the
whole rehearsal win (autumn SON, Dubbo's own local spring, -0.516 degC of
the rehearsal's average improvement) shrank to -0.138 degC on the test year,
which is close to enough on its own to explain the fall from the rehearsal's
8.2% margin to the test's 3.3% (F64).

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
- Session 24: Dubbo's single sealed-test look, executing D39 exactly as
  written. **DUBBO PASSES** — corrected MAE 1.210 degC against raw GFS 1.251
  (3.3% better) and persistence 2.669 (54.7% better), the narrowest raw-GFS
  margin of the four airports (DECISIONS F64). The training refit (1,553
  rows) and the test-year paired-row count (356 of 365) both reconciled
  exactly against D39's advance prediction; the scored-day count (347) could
  not be predicted in advance, as D39.7 said, and every one of the 9
  observation-side drops plus the 9 further scored-day losses they caused
  is now named in DECISIONS for the first time. D39.12's single-season
  watch-item read true: the one season that carried almost the whole
  rehearsal win shrank sharply on the test year, and that shrinkage is close
  to sufficient on its own to explain the fall from an 8.2% rehearsal margin
  to a 3.3% test margin. Two runs were byte-identical apart from the clock.
  F65 records what four passes now establish (the hemisphere/season-cycle
  axis is answered; the year axis is not) and flags that the "structure, not
  offset" claim is now thinnest anywhere (2.3% over the mean-bias
  reference). No SPEC edit was made or authorised this session.

## Next

**An owner decision, not a re-run.** Dubbo's single look is spent (D39.10);
its result stands as reported (F64) regardless of what happens next. Q30's
fork (below) is now fully live with all four of Dubbo's five steps finished.
Two housekeeping items are also outstanding, flagged but not fixed this
session: SPEC 1, 3.4, 5.0 and 6 still describe Dubbo as "in progress" with
no test-year row, and no session has yet been asked to update them.

## Open questions (live)

- **Q30 (fork now fully live).** The owner already picked its first branch —
  more airports — by opening Dubbo (D36). Dubbo's own five steps are now all
  finished (verify ✓, pull/map ✓, join and rehearse ✓, lock ✓, test once ✓,
  DECISIONS F64), so what comes next is entirely the owner's choice, with
  nothing left pending: another airport; a second test year (the untouched
  half of the F30/F46/F48/F65 caveat — all four passes so far share the same
  twelve months); or stage 3, pooling (not opened).

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
