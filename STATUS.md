# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 September 2026, after session 33._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is complete for the five
airports opened so far — four pass, one fails. Session 33 was a blocked
six-fold cross-validation across the whole ~1.5-year feature-complete
window (2024-01-19 to 2025-07-31), answering the question session 32's
scout could not: with a full seasonal cycle in training, does the recipe
recover? No recipe was locked and no airport's sealed test year was
touched.** The headline (DECISIONS F87): **with a full seasonal cycle in
training, 3-feature beats raw GFS at 4 of 5 airports** (EGLC, DSM, YSDU,
RNO — only LFPG still loses), a clear recovery from the scout's 1-of-5 on
the 6-month window (F86). **5-feature beats 3-feature at 4 of 5 airports
and beats raw GFS at 4 of 5** (all but LFPG), including a real, if modest,
positive result at Reno specifically (5-feature 1.318 vs 3-feature 1.369
vs raw GFS 1.423 — a result the scout's short window could not cleanly
show). Overfit gaps (pooled in-sample vs out-of-fold MAE) are positive but
modest at every airport, for both models. LFPG is the one unresolved case:
neither model beats raw GFS on this 1.5-year window, and this session's
own tools cannot explain why. Two questions are flagged for the owner, not
decided (F87): (a) is the 1.5-year window workable, or is a deeper GFS
GRIB source mandatory — this session's own answer leans toward "workable
at most airports," with LFPG the open exception; (b) go/no-go on a full
locked sealed-test cycle for the richer features, given the diagnostic now
gives a firmer multi-fold version of the scout's marginal-improvement
signal.

Session 32, the session before, was the richer-features scout: a two-tier
same-window comparison of a 3-feature and a 5-feature (+ cloud cover, wind
speed) model, fitted on an identical short window (2024-01-19 to
2024-07-31, ~6 months, missing August through December entirely) and
judged once on the validation year, at all five airports. Its headline
(DECISIONS F86) was that the short window itself, not the two extra
features, dominated almost every number: the freshly-refitted 3-feature
model on that six-month window lost to raw GFS at 4 of 5 airports, where
the same recipe on the full multi-year window beats raw GFS at all five.
Session 33 exists to test whether that reading was right, by removing the
short-window artefact — and it was: see F87 above.

Session 31, before that, was a pure data-availability probe for the
richer-features phase (DECISIONS F85): cloud cover, wind speed, dew point
and relative humidity all start at exactly 2024-01-19 12:00 UTC at every
airport (one hour after the shared 492-hour forecast-gap's last missing
hour); upper-air (925/850 hPa) temperature is not available in any
leakage-safe form on this API/offset, at any date or airport.

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
both sit outside that range, on the losing side.** This is recorded in SPEC
5.0 itself, not only in DECISIONS. None of the above changed this session —
session 33 is a diagnostic inside the training window only, and touches no
airport's sealed-test verdict.

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
  written as a standalone technical summary of all five airports (F84).
- Session 31: a pure data-availability probe for the richer-features
  phase, confirming and extending F7/D17 (DECISIONS F85). No model built,
  no join, no fit, no forecast. Data saved under
  `data/raw/diagnostics/session31/`.
- Session 32: the richer-features scout — the first actual feature-set
  experiment, validation-year only, sealed test NOT opened. A two-tier
  same-window comparison of a 3-feature and a 5-feature (+ cloud_cover,
  wind_speed_10m) model on the short 2024-01-19..2024-07-31 window,
  judged on the 2024-08-01..2025-07-31 validation year (DECISIONS F86).
  5-feature beat 3-feature at 3 of 5 airports and raw GFS at only 2 of 5;
  the short window itself was the dominant effect almost everywhere. New
  raw data (cloud cover, wind speed forecasts, 2024-01-19 to 2025-07-31,
  all five airports) saved under `data/raw/features/`.
- **Session 33 (this one): blocked six-fold cross-validation across the
  whole ~1.5-year feature-complete window, sealed test NOT opened.** Six
  contiguous ~3-month calendar blocks, each fold training on the other
  five (~15 months spanning a full seasonal cycle) and testing on the
  held-out block, for four rungs (raw GFS, +mean-bias, 3-feature,
  5-feature) at all five airports (DECISIONS F87). **3-feature recovers to
  beating raw GFS at 4 of 5 airports** (up from 1 of 5 on the scout's
  6-month window); **5-feature beats 3-feature at 4 of 5 and beats raw GFS
  at 4 of 5**, including a real positive result at Reno. LFPG is the one
  airport where neither model beats raw GFS on this window. Overfit gaps
  are positive but modest everywhere. No recipe was locked, no new raw
  data was pulled (reused session 32's `data/raw/features/` pull and the
  existing `data/raw/` chunks).

## Next

**Two questions remain on the owner's desk, sharpened rather than settled
by session 33's own finding (F87):**
1. **Is the 1.5-year window workable, or is a deeper GFS GRIB source
   mandatory?** F87 leans toward "workable at most airports" — the proven
   3-feature recipe recovers to beating raw GFS at 4 of 5 airports once a
   full seasonal cycle is in training. It does not resolve LFPG, where
   even full-cycle CV still loses to raw GFS; whether that is a property
   of the 1.5-year window specifically or something the locked recipe's
   own longer training window already handles better was not tested this
   session.
2. **Go/no-go on a full locked sealed-test cycle for the richer
   features.** F87 gives a firmer, multi-fold version of the scout's
   signal — 5-feature beats 3-feature at 4 of 5 airports and beats raw GFS
   at 4 of 5, with sane overfit gaps everywhere — a stronger case than the
   scout's single-year read gave. Whether that is now enough evidence to
   justify a full lock-and-test cycle, given the richer-feature window is
   still capped at ~1.5 years against the locked recipe's ~4.3, and given
   LFPG's unresolved loss, needs the owner's word before any further
   richer-features session starts.

Neither question was decided this session (session 33 scope forbids it).
**Turning either answer into an actual feature-set design and a written
lock is still not started.**

**Whatever the owner decides about richer features or a further airport,
Reno's own result stands as reported (D44.10, D44.11) — no re-run, no
retroactive adjustment.** Q30's other branches (a second test year; stage 3,
pooling) remain untouched and available, now alongside the richer-features
questions F82/F85/F86/F87 raise.

## Open questions (live)

- **Q30 (unchanged in substance, now joined by two richer-features
  diagnostics).** The owner picked its first branch — more airports, "ramp
  up difficulty" — and Reno's own five steps are finished, ending in a
  failure. The richer-features branch of that intent has now taken two
  concrete steps: session 32's scout (DECISIONS F86) found a real but
  short-window-confounded signal, and session 33's blocked CV (F87)
  removed most of that confound and found the recipe recovers at 4 of 5
  airports, with LFPG the unresolved exception. What comes next is still
  the owner's choice: settle the two richer-features questions above; open
  another airport; open a second test year (the untouched half of the
  F30/F46/F48/F65 caveat); or open stage 3, pooling.
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

**Q31 is no longer live — closed as immaterial (DECISIONS F83), not
answered.** See "Done" above.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
