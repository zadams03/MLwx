# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 19 August 2026, after session 25._

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is in progress.** Four
airports have passed the frozen bar (SPEC 5.3); a fifth, a mountain-valley
airport, was opened this session and verified on contact only (DECISIONS
D40, D41, F66–F73) — no full pull, no join, no model. Stage 3 (pooling) is
not opened. **No SPEC edit was made or authorised this session** — SPEC 3.4
still has no row for the new airport, and adding one is a later session's
job, once the full pull confirms the data (mirroring how DSM and Dubbo's own
rows were added only after their full pulls, D34/D38).

## Airports

Full per-airport facts for the four PASSED airports live in SPEC 3.4; the
full results table is SPEC 5.0. The fifth airport is not yet in SPEC (see
above). Summary:

| airport | stage | status |
|---|---|---|
| EGLC (London City) | 1 | PASSED — sealed test run, single look spent |
| LFPG (Paris CDG) | 2 | PASSED — sealed test run, single look spent |
| DSM (Des Moines) | 2 | PASSED — sealed test run, single look spent |
| YSDU (Dubbo) | 2 | PASSED — sealed test run, single look spent (DECISIONS F64) |
| BZN (Bozeman, Montana) | 2 | IN PROGRESS — verified on contact only (DECISIONS F66–F73) |

All four passed airports beat both raw GFS and persistence on MAE over their
own sealed test year (SPEC 5.3). Margins over raw GFS ranged 3.3%–16.3% on
the sealed test years and 3.5%–16.1% on the rehearsal years — all four test
years fell on the same shared twelve months (SPEC 4.3, D13), so the honest
figure to quote is the range across eight airport-years, roughly 3%–16%, not
the best single result (DECISIONS F48, F65).

**BZN (Bozeman, Montana) — verified on contact this session, DECISIONS D40,
D41, F66–F73.** Chosen over Reno (Nevada) as the clearer "broad, not
pathological" mountain-valley case; both candidates' forecast grid-elevation
mismatch turned out real but small (BZN −16 m, RNO −1 m — smaller than the
session prompt flagged as possible for either). BZN is by far the
highest-elevation airport in the project (1,364 m against DSM's 294 m).
Target hour computed and checked: local standard noon = 19:00 UTC (a fourth
distinct target hour, after 12:00/18:00/02:00). Archive floor, pairing rule,
units and timezone all check out the same way the other four airports did.
The one genuinely new result: `gfs_global` and `gfs_seamless` DIFFER here
more sharply than at DSM (largest difference 16.5 degC against DSM's 12.3
degC) — D16's pin is doing real work at exactly the airport where it matters
most. A rough, informal 21-day out-of-test-year sample gave raw-GFS MAE
~1.23 degC, inside the flat airports' range rather than clearly worse — not
evidence against the terrain hypothesis, since a 21-day June sample cannot
see the winter/cold-air-drainage effects the hypothesis actually rests on
(DECISIONS F73). The full pull and join are what will actually test it.

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
- SPEC is current for all four passed airports: each reads "passed"
  throughout, and the two wording items (Q28, Q29) are closed (D38).
- Session 21: a one-time, authorised documentation restructure — no data,
  model, or pull touched. STATUS.md rewritten as this pure snapshot; SPEC
  3.2's three near-identical per-airport gap paragraphs collapsed into one
  general statement; DECISIONS-archive.md created, holding D1–D12 and four
  settled EGLC-only findings, moved verbatim, with pointers left in
  DECISIONS.md.
- Session 25 (this one): a fifth airport opened — the project's first
  deliberate "hard" case, a genuinely terrain-affected, high-altitude
  mountain-valley US airport, aimed at testing whether the correction wins
  biggest exactly where raw GFS is worst. Bozeman (BZN, Montana) was chosen
  over Reno (RNO, Nevada) after both candidates were verified on contact,
  including — new for this session — a forecast-grid-elevation comparison
  for both before choosing (D40). Its target hour, 19:00 UTC, was computed
  from its own timezone and checked against the timezone database, not
  assumed (D41). Every verify-on-contact check passed the same way it did
  for DSM and Dubbo, with one genuinely new result: `gfs_global` and
  `gfs_seamless` diverge more sharply here than at any airport tested so
  far, which is itself evidence the airport is a real terrain-affected case
  even though the grid's raw elevation mismatch turned out modest (F66–F73).
  **No full pull, no join, no model, no SPEC edit** — this was
  verify-on-contact only, mirroring session 19's shape for Dubbo.

## Next

**The full pull and gap map for BZN, if the owner wants to proceed** —
mirroring session 20's shape for Dubbo (session 15's for DSM): six yearly
forecast and observation chunks, a gap map predicting what the eventual join
should drop, and only then a SPEC 3.4 row added from the real pulled data.
Nothing about BZN's own five steps (verify ✓, pull/map, join and rehearse,
lock, test once) beyond the first is done yet. Q30's other two branches (a
second test year; stage 3, pooling) remain untouched and available as
alternatives, exactly as before this session.

## Open questions (live)

- **Q30 (unchanged).** The owner has already picked its first branch — more
  airports, now specifically "ramp up difficulty" — by opening BZN (D40).
  What comes after BZN's own five steps finish is still the owner's choice:
  another airport; a second test year (the untouched half of the
  F30/F46/F48/F65 caveat — all four passed airports so far share the same
  twelve months); or stage 3, pooling (not opened).

No other open question remains live; everything else has been closed by a
decision or a finding — see DECISIONS.md for the closure record.
