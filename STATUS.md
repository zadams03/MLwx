# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 20 August 2026, after session 29._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have passed the frozen bar (SPEC 5.3). The fifth, Reno (RNO), has
now completed all five steps — verified on contact, pulled and gap-mapped,
joined and rehearsed, locked, and **tested once (session 29, DECISIONS
F82)** — and **RENO DOES NOT PASS.**

**Session 29's headline: Reno's sealed test ran exactly as locked in D44,
and the corrected forecast does not beat raw GFS over the held-out test
year (1.458 degC against 1.414, a 3.1% loss) — the project's first
failure.** It does beat persistence comfortably (2.490, +41.4%). This is
**the project's first airport that fails the frozen bar**, and it is not a
surprise: session 28's lock (D44, D44.12) named this exact outcome — raw
GFS being the half most likely to fail, and a near-constant-bias / overfit
pattern being the expected reason — *before* the test year was opened.
Nothing about the recipe was changed to chase a pass; the method ran
byte-for-byte as locked (proved in the script's own PART 0, 23 of 23 lock
values matched, and every function compared identical to Dubbo's sealed
test bar the location/hour swap).

**F82 in brief:**
- Verdict: **RENO DOES NOT PASS.** Fails the raw-GFS half of the bar (1.458
  vs 1.414, -3.1%); passes the persistence half (1.458 vs 2.490, +41.4%).
- Training refit: 1,568 of 1,591 calendar days (1,203 inner-training + 365
  validation), reconciled exactly against D44.5's prediction.
- Test year: **365 of 365 paired, 365 of 365 scored, 0 dropped anywhere** —
  D44.7's predicted clean sweep, confirmed exactly. The cleanest test-year
  result of any airport so far.
- Day-by-day win rate: 43.6% (159 of 365 days closer than raw GFS) — the
  only airport below 50%, and lower even than the rehearsal's 47.1%.
- Per season: helped in winter (-0.175) and autumn (-0.024), hurt in spring
  (+0.195, the year's worst) and summer (+0.176). Winter — the one season
  D44.12 named in advance as lining up with the terrain hypothesis — stayed
  a win and grew slightly stronger, the one measure that continued to line
  up. Spring and autumn swapped which one helps versus the rehearsal.
- The near-constant-bias / overfit signature named in advance (D44.12)
  persisted on the full refit: 25.0% in-sample "improvement" over raw GFS
  collapsed to a -3.1% out-of-sample loss, and the mean training-window
  bias is +0.3746 degC — still the only positive (station-runs-warmer)
  constant of the five airports.
- **This is a legitimate, honestly-reported result of the method's edge
  (SPEC 2.4), not a defect in the project.** It does not reopen or call
  into question EGLC's, CDG's, DSM's or Dubbo's passes (SPEC 5.0 — each
  airport is judged once, on its own data, and nothing is pooled or
  re-judged).
- **The owner intends a planning session next, on when and how to add
  richer features (cloud cover, wind, a genuine terrain descriptor) to the
  recipe, with Reno as the motivating case.** That planning has not started
  — this session only ran the locked recipe and reported the result.
- **SPEC 3.4 and SPEC 5.0 both need Reno's verdict recorded** — SPEC 3.4's
  "in progress" cell for Reno and SPEC 5.0's missing Reno row are both still
  stale as of this session. No SPEC edit was made this session (out of
  scope); that is pending a future session, per the same discipline that
  left CDG's, DSM's and Dubbo's own SPEC updates to a dedicated session.

## Airports

Full per-airport facts for the five airports SPEC currently tracks live in
SPEC 3.4; the full results table is SPEC 5.0 (unchanged this session — the
Reno row is not yet added, see above). Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| RNO (Reno, Nevada) | 2 | **DID NOT PASS** — sealed test run, single look spent (DECISIONS F82) |

The four passed airports beat both raw GFS and persistence on MAE over
their own sealed test year (SPEC 5.3). Margins over raw GFS ranged
3.3%–16.3% on the sealed test years and 3.5%–16.1% on the rehearsal years —
all four test years fell on the same shared twelve months (SPEC 4.3, D13),
so the honest figure to quote for them is the range across eight
airport-years, roughly 3%–16%, not the best single result (DECISIONS F48,
F65). **Reno's rehearsal (-0.4%, F80) and Reno's sealed test (-3.1%, F82)
both sit outside that range, on the losing side — the margin widened from
rehearsal to test rather than narrowing, unlike anything the four passed
airports showed.**

**RNO (Reno, Nevada) — tested this session, DECISIONS F82.** The test ran
exactly as D44 locked it: same three features, same LightGBM settings, same
20:00 UTC target, refit on the full training window, one look at the sealed
test year. It is the project's first mountain/terrain-affected airport, the
third whose target hour is not 12:00 UTC (D42, SPEC 4.1), and now the
**first airport to fail the frozen bar (SPEC 5.3)**. Full detail is in F82
above and in DECISIONS.md directly.

## Done

Full session-by-session history is in git (every prior version of this
file) and in DECISIONS.md / DECISIONS-archive.md. High points only:

- Stage 1 (EGLC) passed (session 07, DECISIONS F16).
- Stage 2 opened at CDG (D26) and passed (session 13, F30).
- A third airport, DSM, opened (D32) and passed (session 18, F47, F48) — the
  first non-European airport and the first with a target hour other than
  12:00 UTC (D33).
- A fourth airport, Dubbo (YSDU), opened (D36, D37) — the project's first
  Southern Hemisphere airport — verified on contact (session 19, F49–F56),
  fully pulled and gap-mapped (session 20, F57–F59), joined and rehearsed
  (session 22, F60–F63), locked (session 23, D39) and tested once (session
  24). **DUBBO PASSES** — corrected MAE 1.210 degC against raw GFS 1.251
  (3.3% better) and persistence 2.669 (54.7% better), the narrowest raw-GFS
  margin of the four passed airports (F64).
- Session 21: a one-time, authorised documentation restructure — no data,
  model, or pull touched.
- Session 25: a fifth airport opened — the project's first deliberate "hard"
  case. Two mountain-valley candidates, Bozeman and Reno, were both verified
  on contact; Bozeman was chosen initially (D40).
- Session 26 (a corrected re-run): recorded the Bozeman→Reno switch as D42
  (superseding D40 without editing it). Reno's target hour, 20:00 UTC,
  confirmed against the timezone database (F74). SPEC brought up to date
  (D43): Dubbo's pass recorded throughout, and a Reno row added to SPEC 3.4.
  Reno's full six-year history pulled and gap-mapped (F75–F77): identical
  492-hour archive gap, second-cleanest observation record of the five
  (110 missing hours, 0.23%, zero off-hour reports), 20 days lost to the
  shared forecast gap and 3 to observation-side outages at the target hour,
  expected 1,933 of 1,956 paired rows (98.8%).
- Session 27: Reno joined at 20:00 UTC and rehearsed on the validation year,
  mirroring session 22's shape for Dubbo. The join matched F77's predicted
  drops exactly (20 fc-gap + 3 obs-side, all inner-training; 0 in
  validation). Reno's bias is persistently positive (mean +0.492 degC,
  station warmer 67.7% of days) and largest in winter (mean |bias| 1.850
  against 1.053–1.484 in the other three seasons) — the one measure that
  lines up with the terrain hypothesis. **The rehearsal correction did NOT
  beat raw GFS** (1.499 against 1.493, -0.4%), the first such result in the
  project; it beat persistence, climatology, and the mean-bias reference by
  the thinnest margin of any airport's rehearsal (+1.7%). Method proved
  unchanged from the D21 lock (0 settings differ, TARGET_HOUR the only
  differing constant, per D42). No lock, no test, no SPEC edit.
- Session 28: Reno's method lock written and verified as DECISIONS D44 — a
  faithful copy of D39 (Dubbo's lock) with only the location and the target
  hour changed, confirmed by a point-by-point correspondence check inside
  D44. The features and model settings are explicitly unchanged despite
  session 27's rehearsal loss — nothing was added or tuned to improve
  Reno's odds. The lock recorded, in advance, that raw GFS is the half of
  the bar most likely to fail, and named Reno's near-constant bias / overfit
  pattern (D44.12) as the expected explanation if the sealed test also came
  back negative. §6's stale Reno bullet was corrected (the one authorised
  SPEC edit). No test year opened, no model run, no other SPEC edit.
- Session 29 (this one): Reno's sealed test executed exactly as D44 locked
  it, one look, opened once. **RENO DOES NOT PASS** — corrected MAE 1.458
  degC against raw GFS 1.414 (-3.1%, NOT beaten) and persistence 2.490
  (+41.4%, beaten). The project's first failed airport. Training refit
  (1,568 rows) and test-year join (365/365 paired and scored, 0 dropped)
  both reconciled exactly against D44's advance predictions. D44.12's
  near-constant-bias / overfit watch-item was borne out: 25.0% in-sample
  improvement collapsed to -3.1% out-of-sample, and winter — the one season
  the watch-item flagged as consistent with the terrain hypothesis —
  remained the correction's clearest win. Result appended to DECISIONS as
  F82. No SPEC edit this session (out of scope, pending a future session).

## Next

**A planning session on richer features, with Reno as the motivating
case — not started, not scoped, and not this session's job.** Reno's own
five steps (verify, pull, join/rehearse, lock, test) are now complete, and
its sealed test failed the frozen bar. D44.12 and F82 both name the same
mechanism: Reno's bias is unusually close to a persistent, near-constant
offset that the current three features (forecast temperature, season
sin/cos) cannot turn into more than a thin, overfit-prone signal. F81
already named cloud cover, wind, and a genuine terrain descriptor as the
kind of information that might be needed. None of that work has begun —
this session only ran the locked recipe once and reported the result
straight, per its own scope.

**SPEC 3.4 and SPEC 5.0 need Reno's verdict recorded — pending a future,
dedicated SPEC session**, the same discipline CDG's, DSM's and Dubbo's own
SPEC updates each received. SPEC 3.4's "stage 2 — in progress" cell for RNO
and SPEC 5.0's results table (which has no Reno row at all) are both stale
as of this session. Section 6's Reno bullet (updated last session, D44) will
also need its "not yet tested" clause replaced with the verdict.

**Whatever the owner decides about richer features or a further airport,
Reno's own result stands as reported (D44.10, D44.11) — no re-run, no
retroactive adjustment.** Q30's other branches (a second test year; stage 3,
pooling) remain untouched and available, now alongside the richer-features
question F82 raises. Q31 (whether Reno files a second scheduled report)
remains open and unrelated to anything this session changed.

## Open questions (live)

- **Q30 (unchanged in substance, Reno's own branch now complete).** The
  owner picked its first branch — more airports, "ramp up difficulty" — and
  Reno's own five steps are now finished, ending in a failure. What comes
  next is still the owner's choice: richer features at Reno specifically
  (the owner's stated intent for the next planning session, per this
  session's prompt); another airport; a second test year (the untouched
  half of the F30/F46/F48/F65 caveat); or stage 3, pooling (not opened).
- **Q31 (unchanged).** Whether Reno files a second scheduled report
  (like EGLC/LFPG/Dubbo) or genuinely unscheduled ones (like DSM and
  Bozeman) has not been checked by any session. SPEC 3.4's "also files at"
  cell for RNO reads "not yet checked". Nothing in the pipeline depends on
  it (D30); it is a bookkeeping gap, not a data one.
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

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
