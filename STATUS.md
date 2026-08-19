# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 August 2026, after session 26._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have passed the frozen bar (SPEC 5.3). The fifth airport is now
**Reno (RNO), not Bozeman** — session 25 opened Bozeman (D40) and verified it
on contact; the owner then switched the choice to Reno, and this session
(26) recorded that switch as DECISIONS D42 (D40 itself stands unedited, as
the append-only rule requires) and pulled Reno's full history and mapped its
gaps (F74–F77). Reno is not yet joined, rehearsed, locked or tested. Stage 3
(pooling) is not opened.

**SPEC is now current for Dubbo's pass and carries Reno.** SPEC 3.4 has a
RNO row (stage `2 — in progress`, target hour 20:00 UTC) added from this
session's own pulled data, and Dubbo's pass (session 24, F64) — which SPEC
had not yet recorded — is now reflected in §1, §3.4, §5.0 and §6 (DECISIONS
D43).

## Airports

Full per-airport facts for the five airports SPEC currently tracks live in
SPEC 3.4; the full results table is SPEC 5.0. Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| RNO (Reno, Nevada) | 2 | IN PROGRESS — pulled and gap-mapped (DECISIONS F74–F77) |

All four passed airports beat both raw GFS and persistence on MAE over their
own sealed test year (SPEC 5.3). Margins over raw GFS ranged 3.3%–16.3% on
the sealed test years and 3.5%–16.1% on the rehearsal years — all four test
years fell on the same shared twelve months (SPEC 4.3, D13), so the honest
figure to quote is the range across eight airport-years, roughly 3%–16%, not
the best single result (DECISIONS F48, F65).

**RNO (Reno, Nevada) — pulled and gap-mapped this session, DECISIONS D42,
D43, F74–F77.** Chosen over Bozeman after review of session 25's results:
Bozeman's -16 m grid-elevation mismatch sits in a wide, grid-resolved valley
("high-altitude flat", not a terrain test), while Reno's -1 m mismatch (even
smaller than Bozeman's) sits against the steep Sierra Nevada front — its
expected difficulty is horizontal terrain complexity, not vertical, which
the small mismatch number cannot rule out (D42). Target hour computed and
checked against the timezone database, not inherited from Bozeman's: local
standard noon at Reno (Pacific, UTC-8) is **20:00 UTC**, one hour later than
Bozeman's 19:00 (D42, F74) — the fourth distinct target hour among the
airports SPEC tracks (the fifth counting Bozeman's own, set aside before it
entered SPEC).
The full six-year pull ran cleanly (no retries, no rate limits) and the gap
map found: the same 492-hour shared archive gap, hour for hour (F75); a
clean observation record (110 missing hours, 0.23%, second-cleanest of the
five airports after DSM; zero off-hour reports in five years, F76); and 3
days lost at the target hour on the observation side (all training, all "no
report near the hour"), 20 lost to the shared forecast gap, expected paired
rows 1,933 of 1,956 (98.8%) — essentially level with EGLC and LFPG (F77). A
structural training-window value-range check found nothing obviously wider
or harder than the flat airports (F75) — expected, since terrain-driven
structure at the 20:00 UTC target specifically, if any, is a question for
the join session, not this one. **Whether Reno's raw-GFS error is actually
large at its target hour — the whole point D42 opened this airport to
test — is unanswered by anything measured so far**; that needs the join.
One open item: whether Reno files a second scheduled report is genuinely
unchecked (Q31) — SPEC 3.4's "also files at" cell for RNO reads "not yet
checked" rather than a guess.

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
  margin of the four airports (F64). D39.12's single-season watch-item read
  true in advance: the one season carrying almost the whole rehearsal win
  shrank sharply on the test year, which is close to sufficient on its own
  to explain the fall from an 8.2% rehearsal margin to 3.3% on test (F64).
  F65 records what four passes now establish (the hemisphere/season-cycle
  axis is answered; the year axis is not) and flags that the "structure, not
  offset" claim is now thinnest anywhere (2.3% over the mean-bias
  reference).
- Session 21: a one-time, authorised documentation restructure — no data,
  model, or pull touched. STATUS.md rewritten as this pure snapshot; SPEC
  3.2's three near-identical per-airport gap paragraphs collapsed into one
  general statement; DECISIONS-archive.md created, holding D1–D12 and four
  settled EGLC-only findings, moved verbatim, with pointers left in
  DECISIONS.md.
- Session 25: a fifth airport opened — the project's first deliberate "hard"
  case, aimed at testing whether the correction wins biggest exactly where
  raw GFS is worst. Two mountain-valley candidates, Bozeman and Reno, were
  both verified on contact, including a forecast-grid-elevation comparison
  for both before choosing; Bozeman was chosen (D40). Its target hour, 19:00
  UTC, was computed and checked against the timezone database (D41).
  **No full pull, no join, no model, no SPEC edit** — verify-on-contact
  only, mirroring session 19's shape for Dubbo.
- Session 26 (this one, a corrected re-run of a prompt that had jumped
  straight to Reno without recording the switch): recorded the
  Bozeman→Reno switch as a new decision, D42, superseding D40 without
  editing it (append-only). Reno's target hour, 20:00 UTC, was confirmed
  against the timezone database directly rather than inherited from
  Bozeman's figure (F74). SPEC was brought up to date (D43): Dubbo's pass
  recorded throughout (an oversight from session 24, now fixed), and a Reno
  row added to SPEC 3.4 from session 25's own recorded pull data. Reno's
  full six-year history was then pulled (both sources) and gap-mapped
  (F75–F77): it shares the identical 492-hour archive gap with all four
  earlier airports, has a clean observation record (second-cleanest of the
  five), and loses only 3 days on the observation side and 20 to the shared
  forecast gap at its own target hour. **No join, no model, no evaluation** —
  this was the pull-and-map step only, mirroring session 20's shape for
  Dubbo (session 15's for DSM).

## Next

**Reno's join and validation rehearsal, if the owner wants to proceed** —
mirroring session 22's shape for Dubbo (session 16's for DSM, session 11's
for CDG): join the two series at the 20:00 UTC target, look at the bias
shape on inner-training only, and rehearse the locked recipe on the
validation year. Reno's own sealed test year (2025-08-01 to 2026-07-31)
stays sealed throughout — nothing about it beyond structural row/gap counts
(F75–F77) has been touched. This is also the session that will start to
answer the question D42 opened Reno to ask: whether raw GFS is genuinely
harder to beat here than at the four flat airports, and whether the
correction's win (if any) is bigger here as a result. Q30's other two
branches (a second test year; stage 3, pooling) remain untouched and
available as alternatives, exactly as before this session. Q31 (whether Reno
files a second scheduled report) is a small, separable item that could be
folded into a future session or answered on its own.

## Open questions (live)

- **Q30 (unchanged).** The owner has already picked its first branch — more
  airports, "ramp up difficulty" — now specifically Reno (D40, superseded by
  D42). What comes after Reno's own five steps finish is still the owner's
  choice: another airport; a second test year (the untouched half of the
  F30/F46/F48/F65 caveat — all four passed airports so far share the same
  twelve months); or stage 3, pooling (not opened).
- **Q31 (new this session).** Whether Reno files a second scheduled report
  (like EGLC/LFPG/Dubbo) or genuinely unscheduled ones (like DSM and
  Bozeman) has not been checked by any session. SPEC 3.4's "also files at"
  cell for RNO reads "not yet checked". Nothing in the pipeline depends on
  it (D30); it is a bookkeeping gap, not a data one.

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
