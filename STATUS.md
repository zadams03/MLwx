# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 20 August 2026, after session 27._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have passed the frozen bar (SPEC 5.3). The fifth, Reno (RNO), is now
**joined and rehearsed** (session 27) but **not locked and not tested** — the
sealed test year has still never been touched beyond the structural row/gap
counts from session 26. Stage 3 (pooling) is not opened.

**Session 27's headline: on the validation rehearsal, Reno's correction does
NOT beat raw GFS — the first airport where that happens.** ML-corrected MAE
1.499 degC against raw GFS 1.493 degC, a loss of 0.006 degC (-0.4%). It still
beats persistence (+45.6%) and climatology (+60.3%), and it edges past the
mean-bias reference (1.524, +1.7%) — the narrowest rehearsal margin over that
reference of any airport so far, meaning the "the model learned structure, not
just an offset" claim is thinnest yet at Reno. This is an honest rehearsal
result, not a pass/fail verdict (SPEC 5.3 is judged once, on the sealed test
year, in a later session) — but it is a real signal that the three simple
features (forecast temperature, season) may not be enough to capture
whatever is driving Reno's bias.

**The terrain hypothesis (D42) is not confirmed by this rehearsal, on the
main measures.** Raw GFS's error at Reno's 20:00 UTC target (1.493) is not the
hardest of the five — DSM's raw-GFS error (1.748) is still clearly the
hardest, and Reno sits between Dubbo (1.397) and CDG (1.426). Reno's inner-
training mean |bias| (1.390) sits inside the four flat airports' own range
(1.172–1.973), not above it. The one piece of evidence that does line up with
the terrain hypothesis: **winter is Reno's own worst season for bias size**
(mean |bias| 1.850 against 1.053–1.484 in the other three seasons) and **winter
is where the correction wins the most** (-0.156 degC change, the only clearly
helped season) — consistent with cold-air-drainage/downslope effects being
real but concentrated in winter, and not large enough the rest of the year to
lift the annual average past raw GFS.

**Reno's bias shape is also qualitatively different from the other four
airports': it is persistently positive.** The station ran warmer than GFS on
67.7% of inner-training days (against 45–52% at the other four), and the mean
bias stayed positive across almost every forecast-temperature band and every
season — a steadier, more constant-like warm offset than the sign-flipping,
band-and-season-dependent shapes EGLC, CDG, DSM and Dubbo each showed. That is
the most likely reason the model's in-sample gain (1.390 → 1.004 MAE, 27.8%)
did not survive to validation (1.493 → 1.499): a fairly constant offset with a
genuine winter component is closer to what the mean-bias reference already
gives away for free, leaving the model less real structure to add.

**Everything else about the join reconciled exactly against session 26's
gap map**, and the method was proved unchanged from the locked D21 recipe
(0 model settings differ, exactly 1 constant differs — TARGET_HOUR, per D42).

## Airports

Full per-airport facts for the five airports SPEC currently tracks live in
SPEC 3.4; the full results table is SPEC 5.0 (unchanged this session — SPEC
was not edited, and Reno has not passed or failed anything). Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| RNO (Reno, Nevada) | 2 | IN PROGRESS — joined and rehearsed, correction did NOT beat raw GFS on validation (DECISIONS F78–F81) |

All four passed airports beat both raw GFS and persistence on MAE over their
own sealed test year (SPEC 5.3). Margins over raw GFS ranged 3.3%–16.3% on
the sealed test years and 3.5%–16.1% on the rehearsal years — all four test
years fell on the same shared twelve months (SPEC 4.3, D13), so the honest
figure to quote is the range across eight airport-years, roughly 3%–16%, not
the best single result (DECISIONS F48, F65). **Reno's rehearsal now sits
outside that range on the low end: -0.4%**, the first rehearsal loss against
raw GFS the project has recorded.

**RNO (Reno, Nevada) — joined and rehearsed this session, DECISIONS
F78–F81.** The join matched session 26's F77 gap map exactly: inner-training
kept 1,203 of 1,226 days (20 lost to the shared 492-hour forecast gap, 3 to
genuine reporting outages, zero to off-hour reports); validation kept all 365
of 365. The pairing offset was a steady -5 minutes on every one of the 1,588
kept days (the 19:55 report serving the 20:00 target), with zero ambiguous
days and zero reports rejected by the D14 15-minute rule — the cleanest
pairing behaviour of any airport so far. Inner-training bias: mean +0.492
degC, mean |bias| 1.390 degC, station warmer than GFS on 67.7% of days.
Validation-year MAE: Raw GFS 1.493, Persistence 2.756, Climatology 3.774,
Mean-bias reference 1.524, ML-corrected 1.499. The correction lost to raw GFS
by 0.006 degC (-0.4%), beat persistence by 1.257 (+45.6%), beat the mean-bias
reference by only 0.025 (+1.7%, the thinnest margin of any airport's
rehearsal), and beat climatology by 2.275 (+60.3%). It helped in 2 of 4
seasons (winter -0.156, spring -0.022; summer +0.112 and autumn +0.086 both
worse), and was closer to the truth than raw GFS on only 172 of 365 days
(47.1%) — the lowest day-by-day win rate of any airport's rehearsal.

**This is a rehearsal, not the frozen bar.** The bar (SPEC 5.3) is judged once
per airport, on the sealed test year, in a later session — Reno's test year
remains completely untouched beyond session 26's structural row/gap counts.
A rehearsal loss does not mean Reno will fail its sealed test (D18 exists
because rehearsal and test years can differ, sometimes substantially — see
F16's and F64's own honest readings of how much the weather itself moved each
airport's number between validation and test). It does mean the owner should
weigh, before locking, whether to proceed with the unmodified recipe anyway
(the session-27 prompt's own instruction: proceed to lock/test regardless,
judge the bar as-is) or to treat this as the first concrete sign that richer
features (cloud cover, wind) may eventually be needed for terrain-hard
airports — a SPEC-6/stage-4 question, not a session-27 one.

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
  margin of the four airports (F64).
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
- Session 27 (this one): Reno joined at 20:00 UTC and rehearsed on the
  validation year, mirroring session 22's shape for Dubbo. The join matched
  F77's predicted drops exactly (20 fc-gap + 3 obs-side, all inner-training;
  0 in validation). Reno's bias is persistently positive (mean +0.492 degC,
  station warmer 67.7% of days) and largest in winter (mean |bias| 1.850
  against 1.053–1.484 in the other three seasons) — the one measure that
  lines up with the terrain hypothesis. **The rehearsal correction did NOT
  beat raw GFS** (1.499 against 1.493, -0.4%), the first such result in the
  project; it beat persistence, climatology, and the mean-bias reference by
  the thinnest margin of any airport's rehearsal (+1.7%). Method proved
  unchanged from the D21 lock (0 settings differ, TARGET_HOUR the only
  differing constant, per D42). No lock, no test, no SPEC edit.

## Next

**Reno's method lock (the D39-equivalent), if the owner wants to proceed** —
mirroring session 23's shape for Dubbo (session 17's for DSM, session 12's
for CDG): write down the full locked recipe for Reno with nothing tuned or
varied, matching the pattern every prior airport followed regardless of how
its own rehearsal read. The session-27 prompt's own framing already covers
this: a rehearsal that shows the simple features struggling is a candidate
finding for the owner to weigh (it may eventually motivate richer features —
cloud cover, wind — a stage-4/SPEC-6 question), but the bar is still judged
as-is, on the locked recipe, once, on the sealed test year. **The owner may
also want to explicitly decide, before locking, whether -0.4% on the
rehearsal changes anything about proceeding to test** — nothing in SPEC
requires a rehearsal win before locking (D18's whole point is that the
rehearsal and the sealed test can differ), but this is the first airport
where the rehearsal itself came back negative rather than merely narrow, and
the owner has not been asked that question before. Reno's own sealed test
year (2025-08-01 to 2026-07-31) stays sealed throughout — nothing about it
beyond structural row/gap counts (F75–F77) has been touched. Q30's other two
branches (a second test year; stage 3, pooling) remain untouched and
available as alternatives. Q31 (whether Reno files a second scheduled
report) remains open and unrelated to anything measured this session.

## Open questions (live)

- **Q30 (unchanged).** The owner has already picked its first branch — more
  airports, "ramp up difficulty" — now specifically Reno (D40, superseded by
  D42). What comes after Reno's own five steps finish is still the owner's
  choice: another airport; a second test year (the untouched half of the
  F30/F46/F48/F65 caveat — all four passed airports so far share the same
  twelve months); or stage 3, pooling (not opened).
- **Q31 (unchanged).** Whether Reno files a second scheduled report
  (like EGLC/LFPG/Dubbo) or genuinely unscheduled ones (like DSM and
  Bozeman) has not been checked by any session. SPEC 3.4's "also files at"
  cell for RNO reads "not yet checked". Nothing in the pipeline depends on
  it (D30); it is a bookkeeping gap, not a data one.
- **Q32 (new this session).** Should Reno's rehearsal loss against raw GFS
  (-0.4%, DECISIONS F80) change anything about whether/how the recipe is
  locked and tested at Reno? The session-27 prompt's own instruction is to
  proceed to lock/test regardless and judge the bar as-is, and that
  instruction was followed (no lock was attempted this session — that is a
  separate session's scope). But the owner has not yet been asked, in so
  many words, whether a rehearsal that comes back negative (rather than
  merely narrow, as CDG's 3.4% was) changes their intentions for this
  airport specifically, or for how future terrain-hard airports are
  approached. Nothing was decided; this is recorded for the owner.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
