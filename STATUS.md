# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 September 2026, after session 31._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is complete for the five
airports opened so far — four pass, one fails. Session 31 was a pure
data-availability probe for the next, not-yet-scoped richer-features phase:
no code was joined, built, fitted or evaluated, and no airport's test year
was touched.** It settled three things (DECISIONS F85):

1. **Cloud cover, wind speed, dew point and relative humidity all start at
   exactly the same hour, at all five airports: 2024-01-19 12:00 UTC** —
   one hour after the shared 492-hour forecast-gap's last missing hour
   (F8/F22/F38/F57/F75). This confirms and sharpens F7/D17's earlier,
   coarser dating ("absent 2023-07-01, present 2024-07-01") down to the
   hour, and shows it is the same underlying archive-build fact at every
   airport, not a per-location coincidence.
2. **Upper-air (925/850 hPa) temperature is NOT available in any
   leakage-safe form.** Every `_previous_dayN`-suffixed spelling tried
   (four casings/units at day 1, plus an explicit day-0 probe) was
   HTTP-rejected with the same error; only the bare, no-offset form is
   accepted, and that is the freshest-run series — the same leakage trap
   D17 already named for plain `temperature_2m`. This is categorically
   unavailable via the offset mechanism the project depends on for
   leakage safety, at every date tried and at every airport, not merely a
   recency floor the way cloud/wind is. Verdict: effectively
   separate-source — a genuine day-ahead upper-air forecast would need a
   different mechanism entirely.
3. **A five-airport availability table** at a recent pre-test anchor
   (2025-06-10 to 2025-06-12) confirms every wave-one/wave-two variable
   fully present everywhere, and upper-air uniformly rejected everywhere.

**A design question this raises for the owner, flagged rather than
decided:** since cloud/wind-family features are free only from
2024-01-19 onward, using them means a two-tier training window; since
upper-air isn't available at all in a leakage-safe form, it is not a
candidate for that design without a separate data-source effort. Nothing
about the richer-features design was decided this session.

Session 30, the session before, was documentation-only: no code was
touched, no model was run, and no new figure was computed anywhere. It did
three things:

1. **Cleared SPEC's remaining Reno-related staleness (A-1 to A-4).** SPEC
   3.4's airport table, SPEC 5.0's results table, and SPEC 6's build-order
   bullet now all say plainly that **Reno failed** (DECISIONS F82: corrected
   1.458 vs raw GFS 1.414 vs persistence 2.490, -3.1%/+41.4%). SPEC 4.1's
   long-stale "hours in use" list — which had named only EGLC, LFPG and DSM
   since session 15, flagged but not fixed at session 26 — was replaced with
   a short illustrative paragraph that points at the SPEC 3.4 table as the
   single source for every airport's target hour. See DECISIONS D45 for the
   full before/after of each edit.
2. **Closed Q31 as immaterial (A-5), not answered.** Whether Reno files a
   second scheduled report cannot be checked from data already on hand —
   session 26's raw pull requested routine reports (`report_type=3`) only —
   and answering it would need a new IEM pull, outside this session's
   documentation-only scope. Since D30 already established that the
   "special" stream is never used as the truth observation anywhere in the
   project, the answer cannot change anything once known, so the question is
   closed rather than left open indefinitely. SPEC 3.4's "also files at"
   cell for RNO is unchanged and still honestly reads "not yet checked" —
   that is a different, still-true statement from "immaterial". See
   DECISIONS F83.
3. **Wrote `RESULTS.md`** — a new, standalone, self-contained technical
   summary of all five airports at the project root, for anyone who wants
   the whole story in one place without reading five sessions' worth of
   DECISIONS entries. Every figure in it is cited to and was checked against
   its DECISIONS source; it computes nothing new and does not supersede SPEC
   as the source of truth. See DECISIONS F84.

**No richer-features work happened this session, on purpose.** That planning
is next (see Next, below) and was deliberately kept out of this session's
scope.

## Airports

Full per-airport facts live in SPEC 3.4; the full results table is now SPEC
5.0, complete for all five airports and matching `RESULTS.md`'s own table.
Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| RNO (Reno, Nevada) | 2 | **FAILED** — sealed test run, single look spent (DECISIONS F82) |

The four passed airports beat both raw GFS and persistence on MAE over
their own sealed test year (SPEC 5.3). Margins over raw GFS ranged
3.3%–16.3% on the sealed test years and 3.5%–16.1% on the rehearsal years —
all five test years fell on the same shared twelve months (SPEC 4.3, D13),
so the honest figure to quote for the four passes is the range across eight
airport-years, roughly 3%–16%, not the best single result (DECISIONS F48,
F65). **Reno's rehearsal (-0.4%, F80) and Reno's sealed test (-3.1%, F82)
both sit outside that range, on the losing side — the margin widened from
rehearsal to test rather than narrowing, unlike anything the four passed
airports showed.** This is now recorded in SPEC 5.0 itself, not only in
DECISIONS.

## Done

Full session-by-session history is in git (every prior version of this
file) and in DECISIONS.md / DECISIONS-archive.md. High points only:

- Stage 1 (EGLC) passed (session 07, DECISIONS F16).
- Stage 2 opened at CDG (D26) and passed (session 13, F30).
- A third airport, DSM, opened (D32) and passed (session 18, F47, F48) — the
  first non-European airport and the first with a target hour other than
  12:00 UTC (D33).
- A fourth airport, Dubbo (YSDU), opened (D36, D37) — the project's first
  Southern Hemisphere airport — and passed (session 24, F64, F65).
- A fifth airport, Reno (RNO) — the project's first deliberate "hard" case
  and first mountain/terrain-affected airport — was opened (D40, then
  switched from Bozeman by D42), pulled and gap-mapped (session 26, F74–F77),
  joined and rehearsed with the first negative rehearsal margin in the
  project (session 27, F78–F81), locked unmodified despite that loss
  (session 28, D44, naming the near-constant-bias / overfit pattern as the
  expected failure mode in advance), and tested once (session 29, F82):
  **RENO DOES NOT PASS** — the project's first airport to fail the frozen
  bar, in exactly the way D44.12 predicted before the test year opened.
- Session 21: a one-time, authorised documentation restructure (settled
  material moved to DECISIONS-archive.md, nothing deleted or altered).
- Session 30: a documentation-only consolidation. SPEC's remaining Reno
  staleness cleared (D45); Q31 closed as immaterial (F83); `RESULTS.md`
  written as a standalone technical summary of all five airports (F84). No
  code touched, no model run, no new figure computed.
- **Session 31 (this one): a pure data-availability probe for the
  richer-features phase, confirming and extending F7/D17.** Cloud
  cover/wind speed/dew point/relative humidity all start at exactly
  2024-01-19 12:00 UTC at every airport; upper-air (925/850 hPa)
  temperature is not available in any leakage-safe form on this
  API/offset at any date or airport (DECISIONS F85). No model built, no
  join, no fit, no forecast. Data saved under
  `data/raw/diagnostics/session31/`.

## Next

**A planning session on richer features, with Reno as the motivating
case.** Not started, not scoped, and not this session's job. Reno's own
five steps (verify, pull, join/rehearse, lock, test) are complete, and its
sealed test failed the frozen bar. D44.12 and F82 both name the same
mechanism: Reno's bias is unusually close to a persistent, near-constant
offset that the current three features (forecast temperature, season
sin/cos) cannot turn into more than a thin, overfit-prone signal. F81
already named cloud cover, wind, and a genuine terrain descriptor as the
kind of information that might be needed. Session 31 has now settled *what
data exists and how far back* (F85): cloud cover, wind speed, dew point and
relative humidity are free from 2024-01-19 12:00 UTC onward at every
airport (implying a two-tier training window if used); upper-air
temperature is not available in any leakage-safe form at all, so it is not
a candidate for that design without a separate data-source effort or a
static terrain-mismatch feature computed from metadata already on hand.
**Still not started: turning this into an actual feature-set / experiment
design.**

**One item flagged in session 30 is now stale, not a live to-do.** Session
30's own "Next" note said SPEC section 1's airport list still read "Reno
... stage 2, in progress" and needed "failed". Checked this session: SPEC
section 1 (line 33) already reads "stage 2, **failed**" — the fix has
already happened (by the owner's hand, or a change this file did not track)
and nothing further is needed here.

**Whatever the owner decides about richer features or a further airport,
Reno's own result stands as reported (D44.10, D44.11) — no re-run, no
retroactive adjustment.** Q30's other branches (a second test year; stage 3,
pooling) remain untouched and available, now alongside the richer-features
question F82/F85 raise.

## Open questions (live)

- **Q30 (unchanged in substance, Reno's own branch now complete).** The
  owner picked its first branch — more airports, "ramp up difficulty" — and
  Reno's own five steps are now finished, ending in a failure. What comes
  next is still the owner's choice: richer features at Reno specifically
  (the stated intent for the next session); another airport; a second test
  year (the untouched half of the F30/F46/F48/F65 caveat); or stage 3,
  pooling (not opened).
- **Q32 (effectively answered by events, left on record rather than
  formally closed).** Session 27 asked whether Reno's rehearsal loss should
  change anything about locking/testing Reno; the session-28 and session-29
  prompts both instructed proceeding regardless, and that is what happened
  — Reno was locked unmodified (D44) and tested unmodified (F82), and it
  failed. The owner has still not been asked, in so many words, whether a
  failed sealed test (as opposed to just a negative rehearsal) changes their
  intentions for future terrain-hard airports generally — though the
  planning-session intent noted above (richer features) is the owner's
  first practical answer for Reno specifically.

**Q31 is no longer live — closed this session as immaterial (DECISIONS
F83), not answered.** See "Done" above.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
