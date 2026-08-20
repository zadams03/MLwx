# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 20 August 2026, after session 28._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have passed the frozen bar (SPEC 5.3). The fifth, Reno (RNO), is now
**joined, rehearsed and locked** (session 28, DECISIONS D44) but **not
tested** — the sealed test year has still never been touched beyond the
structural row/gap counts from session 26 (F75–F77).

**Session 28's headline: Reno's method lock, D44, is written and verified —
the D39-equivalent (Dubbo's lock) with only the airport and the target hour
swapped.** Nothing about the recipe changed because of session 27's negative
rehearsal (F80: ML-corrected 1.499 vs raw GFS 1.493, -0.4%). The same three
features (forecast temperature, season sin/cos) and the same LightGBM
settings that were used at every prior airport are locked for Reno too — no
feature added, no setting tuned, no tolerance widened to try to turn the
rehearsal loss into a pass before the test runs. This session did **not**
open Reno's test year and ran no model — it is purely a documentation
session, mirroring session 23's shape for Dubbo.

**D44 in brief:**
- Target: temperature at 20:00 UTC at Reno (KRNO/RNO, NV_ASOS), one row/day.
- Predicts the residual (observed − forecast); features, model and settings
  identical to D21/D31/D35/D39.
- Training data for the test: the full D13 window, 2021-03-24 to 2025-07-31,
  refit on 1,568 of 1,591 calendar days (1,203 inner-training + 365
  validation rows, exactly as session 27's F78 join gave; 23 days dropped,
  all reconciled — 20 to the shared forecast gap, 3 to genuine observation
  outages).
- Test data: Reno's 2025-08-01 to 2026-07-31, never opened. Predicted paired
  rows: **365 of 365, 0 dropped on either side** — the cleanest test-year
  prediction of any airport so far (F75, F77), unlike Dubbo's bounded-but-
  unnamed 9-day observation loss (D39.7).
- Bar: beat raw GFS and persistence, qualitative, judged once. **Recorded in
  advance: raw GFS is the half of the bar most likely to fail**, given the
  rehearsal loss — a failure there would be a legitimate, honestly-reported
  outcome, not a bug.
- **D44.12 watch-item, recorded before the look:** session 27 found Reno's
  bias is unusually close to a constant (positive in 67.7% of inner-training
  days and in almost every band/season, F79) and that the model's large
  in-sample gain (27.8%) collapsed on validation (-0.4%, F80/F81) — the
  signature of overfitting a near-constant signal. **If the sealed test also
  fails to beat raw GFS, this is the expected reason, recorded here in
  advance, not a surprise to explain after the fact.** Winter — Reno's
  worst-bias season and the rehearsal's only clear winning season — is named
  as the first place to look if the test result behaves oddly either way.
- Correspondence check against D39: every point matches except those
  following from LOCATION or the target HOUR (D44.1, .3's read-hour, .5's
  row counts, .7's reporting minute/offset/drop prediction, .8's "fitted on"
  window). Features (D44.3) and model settings (D44.4) are confirmed
  byte-for-byte identical to D39/D35/D31/D21, explicitly despite the
  rehearsal loss.

## Airports

Full per-airport facts for the five airports SPEC currently tracks live in
SPEC 3.4; the full results table is SPEC 5.0 (unchanged this session — Reno
has not passed or failed anything yet). Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| RNO (Reno, Nevada) | 2 | IN PROGRESS — joined, rehearsed and **locked** (DECISIONS D44); sealed test not yet run |

All four passed airports beat both raw GFS and persistence on MAE over their
own sealed test year (SPEC 5.3). Margins over raw GFS ranged 3.3%–16.3% on
the sealed test years and 3.5%–16.1% on the rehearsal years — all four test
years fell on the same shared twelve months (SPEC 4.3, D13), so the honest
figure to quote is the range across eight airport-years, roughly 3%–16%, not
the best single result (DECISIONS F48, F65). Reno's rehearsal (session 27)
sits outside that range, at -0.4% — the project's first negative rehearsal.
**Reno's sealed test is the next session's job, not this one's.**

**RNO (Reno, Nevada) — locked this session, DECISIONS D44.** The lock is a
faithful, point-by-point copy of D39 (Dubbo's lock) with only the airport and
the target hour changed, per the correspondence check inside D44 itself. No
methodological choice was varied because of session 27's rehearsal loss.
Full detail is in D44 above and in DECISIONS.md directly; the one authorised
SPEC edit this session updated §6's Reno bullet to say the airport is now
joined, rehearsed and locked (rehearsal did not beat raw GFS) rather than
"not yet joined, rehearsed, locked or tested". §3.4's "in progress" cell and
§5.0's missing Reno row are left as they are, per the session prompt — they
become accurate once Reno is tested.

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
- Session 28 (this one): Reno's method lock written and verified as
  DECISIONS D44 — a faithful copy of D39 (Dubbo's lock) with only the
  location and the target hour changed, confirmed by a point-by-point
  correspondence check inside D44. The features and model settings are
  explicitly unchanged despite session 27's rehearsal loss — nothing was
  added or tuned to improve Reno's odds. The lock records, in advance, that
  raw GFS is the half of the bar most likely to fail, and names Reno's
  near-constant bias / overfit pattern (D44.12) as the expected explanation
  if the sealed test also comes back negative. §6's stale Reno bullet was
  corrected (the one authorised SPEC edit). No test year opened, no model
  run, no other SPEC edit.

## Next

**Reno's single sealed-test evaluation — executing D44 exactly as written.**
This mirrors session 24's shape for Dubbo (session 18's for DSM, session 13's
for CDG): open Reno's test year once, run the D44 recipe once, report the
result straight — pass or fail, with the seasonal breakdown and drop counts,
reconciled against D44.5's and D44.7's predicted row counts (1,568 of 1,591
training rows; 365 of 365 test rows, 0 dropped either side).

**A failure against raw GFS is an expected, legitimate possible outcome of
this test, not a bug to chase.** Session 27's rehearsal loss (-0.4%) and
D44.12's near-constant-bias / overfit watch-item are both on record in
advance, precisely so a negative test result reads as confirmation of an
already-named pattern rather than a surprise requiring explanation after the
fact. Equally, a positive test result is possible and would not be
suspicious — D18 exists because rehearsal and test years can differ, and
every one of the four passed airports' own numbers moved between validation
and test (sometimes by more than the gap between any two rehearsal margins
seen so far).

Whatever the result, per D44.10/D44.11 it stands as reported: no re-run, no
adjustment, no second look. Q30's other two branches (a second test year;
stage 3, pooling) remain untouched and available as alternatives once Reno's
five steps are complete. Q31 (whether Reno files a second scheduled report)
and Q32 (whether the owner wants to weigh in on proceeding given the
rehearsal loss — answered implicitly this session by proceeding to lock
per the session-28 prompt's own instruction, but never explicitly asked)
remain open and unrelated to anything this session changed.

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
- **Q32 (unchanged, still live).** Should Reno's rehearsal loss against raw
  GFS (-0.4%, DECISIONS F80) change anything about whether/how the recipe is
  locked and tested at Reno? Session 28's prompt instructed proceeding to
  lock regardless and judging the bar as-is, and that instruction was
  followed (D44 is unmodified from D39's pattern). The owner has still not
  been asked, in so many words, whether a rehearsal that came back negative
  changes their intentions for Reno specifically or for how future
  terrain-hard airports are approached — that question remains open,
  unchanged from session 27, and is not resolved by locking the recipe.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
