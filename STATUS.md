# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 11 September 2026, after session 36._

---

## Session 36 (GRIB build sub-project, step 1 of 4 — back-extent + pipeline validation)

**The GRIB-build multi-session sub-project (see docs/session-36.md) opened
this session.** Its four steps: (1 = this session) confirm the fetchable
back-extent and prove the GRIB→point pipeline reproduces Open-Meteo's
temperature; (2) bulk cloud/wind pull; (3) join and re-run the
richer-features experiment on the full window; (4) lock and open the sealed
year. This session built no final pipeline, pulled no bulk history, joined
nothing, fitted nothing, and locked nothing — it is a validation gate only.
Verdict (DECISIONS F89): **back-extent confirmed at 2021-01-01, not
~2015 — flagged prominently; pipeline PROVEN at 4 of 5 airports, FAILS at
RNO with a named, terrain-linked cause.**

**Task 1 — back-extent.** Direct listing (not assumed) shows AWS
`noaa-gfs-bdp-pds`'s true floor is **2021-01-01**, not the hoped-for
~2015 — only ~82 days deeper than Open-Meteo's own 2021-03-24 floor. (One
wrinkle caught in passing: the 0.25° product's path changes from a flat
layout to a `/atmos/` layout on 2021-03-23; an `/atmos/`-only check before
that date would have wrongly read as "unavailable.") NCAR's RDA has now
fully migrated to GDEX (`rda.ucar.edu` redirects its whole root there); the
`ds084.1` GDEX page shows a sign-in gate and no anonymous path was found
this session. **So the confirmed, credential-free, fetchable window is
2021-01-01 onward — essentially the same order of magnitude (~4.4 years) as
the project's existing window, not an ~11-year prize.** This materially
re-weights the still-open build-vs-lock question: the case for the full GRIB
build specifically to reach further back in time is much weaker than
session 35's framing assumed.

**Task 2 — GRIB reader.** `pip install eccodes` (2.48.0) pulled in a
self-contained macOS-arm64 binary wheel (`eccodeslib`) — no Homebrew, no
system library, same shape as the existing libomp workaround. Added to
`requirements.txt`, pinned.

**Tasks 3-4 — pull and pipeline.** 76 byte-range GRIB2 temperature extracts
pulled (19 sample dates × up to 4 distinct cycle/lead files/day — matching
session 35's own estimate), zero failures, every magic marker valid. Lead
convention derived from SPEC 3.2 and confirmed empirically: run at cycle
`floor(HH/6)*6` on day D−1, lead `24 + (HH mod 6)`. One real bug found and
fixed by the reproduction check itself: ecCodes returns grid-neighbour
longitudes in 0–360 form regardless of query-longitude sign, which silently
broke the bilinear weights at DSM and RNO (both west of the prime meridian)
until the query longitude was normalised the same way.

**Task 5 — the reproduction gate.** EGLC, LFPG, DSM, YSDU: **PASS** —
sub-degree (0.18-0.25°C mean absolute), mixed-sign differences against the
trusted Open-Meteo series, ordinary rounding/interpolation noise. **RNO:
FAIL** — a clean, one-sided ~-2.04°C bias, every sample day, both eras.
Traced (one small extra `HGT:surface` diagnostic pull) to real local
terrain: the raw GRIB grid points around RNO's own established point carry
model terrain elevations 246-570 m higher than RNO's actual elevation —
enough, at a standard lapse rate, to explain the measured bias. **This is a
missing elevation-correction step, not a pipeline bug** — RNO's own
established character (Sierra Nevada front terrain, D42/F66) shows up again,
now from a completely different data source (raw model terrain height).

**What this session did not do, on purpose.** No cloud or wind pulled
(temperature only). No bulk/multi-year pull (77 small byte-range extracts,
each under ~900 KB). No sealed-test-year date touched (all ≤ 2025-07-31). No
final pipeline, join, fit, or lock. `SPEC.md`/`RESULTS.md` not modified.
Scripts: `scripts/session36_grib_pull.py`, `scripts/session36_validate.py`.
Full real output: `notes/session-36-check-output.txt`. Extracts and the
comparison table: `data/raw/diagnostics/session36/`.

---

## Session 35 (availability-and-cost probe only, no build)

**Question asked:** can a real GFS forecast GRIB archive supply cloud cover
and 10 m wind back to ~2021, closing the ~1.5-year feature gap F85/F87
pinned as the binding constraint on the richer-features result? **Verdict:
GO-COSTLY** (DECISIONS F88). The two variables genuinely exist,
credential-free, on two independent clouds (AWS S3 `noaa-gfs-bdp-pds` and
its Google Cloud Storage mirror), confirmed back to the project's own
2021-03-24 archive floor by direct inventory check and a real decoded-
message check (not just a label) — so a deep source is available. But
three real alignment costs stack up: (1) none of the five airports'
existing `gfs_global` grid points (SPEC 3.4) land on the public GRIB
product's regular 0.25 deg grid, so a raw-GRIB pull would read a *different*
physical point than the temperature series already uses, an unquantified
new offset; (2) two of the five airports' target hours (YSDU 02:00 UTC, RNO
20:00 UTC) don't align with any standard GFS cycle time, so reproducing
Open-Meteo's own 24-30h "previous_day1" lead-time convention from raw GRIB
is a real, unsolved design problem, not automatic; (3) an order-of-magnitude
~17 GB / ~25,000 HTTP requests across ~4.3 years and 5 airports, needing a
GRIB2 decoder this environment does not currently have. A notable side
finding: a secondary source (NCEI's own page) claims the AWS bucket is a
"trailing 30-day window" — this session's direct probe contradicts that for
the bucket actually checked, another instance of this project's own
"verify on contact" discipline (SPEC 3.3) paying off. **The build-vs-lock
decision is flagged for the owner, not made this session.** No pipeline was
built, no bulk data pulled, no join/fit/evaluation of any kind performed.
Script: none (ad hoc `curl`/`grep`/`xxd` checks, all commands and real
output in `notes/session-35-check-output.txt`). Samples saved under
`data/raw/diagnostics/session35/` with `.meta.txt` provenance per file.

---

## Current stage

**Stage 2 (individual airports, SPEC section 6) is complete for the five
airports opened so far — four pass, one fails. The GRIB-build sub-project
(docs/session-36.md) opened this session with step 1 of 4: confirm the
back-extent and validate the GRIB→point pipeline.** Verdict (DECISIONS
F89): back-extent confirmed at **2021-01-01, not ~2015** — only ~82 days
deeper than Open-Meteo's own floor, materially weakening the case for the
GRIB build as a way to reach further back in time; pipeline **PROVEN at 4 of
5 airports** (EGLC, LFPG, DSM, YSDU — sub-degree, unbiased against the
trusted Open-Meteo answer key), **FAILS at RNO** with a named cause (a
missing elevation/lapse-rate correction — the raw grid's own terrain near
RNO's point runs 246–570 m higher than RNO's real elevation, enough to
explain the measured ~-2.04°C bias). No bulk pull, no join, no fit, no lock.

Session 35, before that, was a GFS GRIB source feasibility probe —
availability and cost only, no pipeline built, no data joined or fitted —
answering the first of session 33's two flagged questions: is a deeper
source than Open-Meteo's ~1.5-year feature-complete window even available?
Verdict (DECISIONS F88): **GO-COSTLY.** A
credential-free deep GFS forecast GRIB archive (AWS S3 `noaa-gfs-bdp-pds`,
mirrored on Google Cloud Storage) was confirmed by direct probe to carry
both total cloud cover and 10 m wind back to the project's own 2021-03-24
archive floor — so yes, a deeper source exists. But real alignment costs
were found and quantified where possible: none of the five airports'
established `gfs_global` grid points land on the public GRIB product's
regular 0.25 deg grid, a second, unquantified offset on top of the one SPEC
3.4 already accepts; two of the five target hours (YSDU, RNO) don't align
with any standard GFS cycle, so reproducing Open-Meteo's own 24-30h lead
convention is an unsolved design problem, not automatic; and the
order-of-magnitude estimate for a full 5-airport, ~4.3-year pull is ~17 GB
across ~25,000 HTTP requests, needing a GRIB2 decoder this environment does
not currently have. The build-vs-lock choice is flagged for the owner, not
decided this session.

**Session 33, before that, was a blocked six-fold cross-validation across
the whole ~1.5-year feature-complete window** (2024-01-19 to 2025-07-31),
answering the question session 32's scout could not: with a full seasonal
cycle in training, does the recipe recover? No recipe was locked and no
airport's sealed test year was touched. The headline (DECISIONS F87): **with
a full seasonal cycle in
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
session 36 is a GRIB-pipeline validation gate for a candidate data source
only, and touches no airport's sealed-test verdict.

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
- Session 33: blocked six-fold cross-validation across the whole ~1.5-year
  feature-complete window, sealed test NOT opened. Six contiguous ~3-month
  calendar blocks, each fold training on the other five (~15 months
  spanning a full seasonal cycle) and testing on the held-out block, for
  four rungs (raw GFS, +mean-bias, 3-feature, 5-feature) at all five
  airports (DECISIONS F87). **3-feature recovers to beating raw GFS at 4 of
  5 airports** (up from 1 of 5 on the scout's 6-month window); **5-feature
  beats 3-feature at 4 of 5 and beats raw GFS at 4 of 5**, including a real
  positive result at Reno. LFPG is the one airport where neither model
  beats raw GFS on this window. Overfit gaps are positive but modest
  everywhere. No recipe was locked, no new raw data was pulled (reused
  session 32's `data/raw/features/` pull and the existing `data/raw/`
  chunks).
- **Session 34a: built the DECISIONS.md archive manifest** (a
  `grep`-based header index, never a full read), classifying every entry
  as settled (MOVE, 237 spans) or still-needed-live (KEEP-LIVE, 12 spans),
  plus one BORDERLINE call (the session-21 restructure record) left for
  the owner. No file was changed. Saved as
  `notes/session-34-archive-manifest.md`.
- **Session 34b (this one): executed the archive move and codified the
  workflow.** The owner resolved the borderline to MOVE. 238 spans,
  8,698 lines, moved mechanically (single-pass line partition, byte-exact)
  from `DECISIONS.md` to `DECISIONS-archive.md`, under one new dated
  section with a pointer to the manifest. `DECISIONS.md` falls from 9,471
  to 873 live lines (D17, F7, F85–F87, the two open questions, the parked
  items, and this session's own new record entry, D46, all still live).
  Archiving settled entries is now a routine end-of-session step
  (`CLAUDE.md`, `DECISIONS-archive.md` header, both amended), superseding
  session 21's "one-time exception" framing. One deferred wording fix
  applied to `RESULTS.md` §2 (why EGLC/LFPG share 12:00 UTC by design,
  not coincidence). No code, model, data file, or figure touched; no
  airport's sealed-test verdict changed.
- **Session 35: GFS GRIB source feasibility probe, availability-and-cost
  only — no pipeline, no bulk pull, no join, no fit.** Verdict:
  **GO-COSTLY** (DECISIONS F88). A deep, credential-free GFS forecast GRIB
  archive (AWS S3 `noaa-gfs-bdp-pds`, mirrored on Google Cloud Storage) was
  confirmed by direct probe to carry both cloud cover and 10 m wind back to
  the project's own 2021-03-24 archive floor — answering session 33's
  question (a) that a deeper source does exist. But real alignment costs
  stack: none of the five airports' existing grid points land on the
  public GRIB product's regular 0.25 deg grid (a new, unquantified offset);
  two of the five target hours (YSDU, RNO) don't align with any standard
  GFS cycle, so reproducing Open-Meteo's own lead-time convention is an
  unsolved design problem; and the pull-and-join lift is an order-of-
  magnitude ~17 GB / ~25,000 HTTP requests needing a GRIB2 decoder this
  environment does not have today. Build-vs-lock is flagged for the owner,
  not decided. Samples saved under `data/raw/diagnostics/session35/`.
- **Session 36: GRIB build sub-project, step 1 of 4 — back-extent +
  pipeline validation. No bulk pull, no join, no fit, no lock.** Verdict
  (DECISIONS F89): back-extent confirmed at **2021-01-01** (AWS bucket's own
  true floor, direct-listing confirmed) — only ~82 days deeper than
  Open-Meteo's own floor, **not the ~2015 prize hoped for**; NCAR's RDA has
  fully migrated to GDEX, which gates `ds084.1` behind a sign-in with no
  credential-free path found. `eccodes` (a self-contained binary wheel, no
  Homebrew needed) installed and added to `requirements.txt`. 76 byte-range
  GRIB2 temperature extracts pulled and decoded; the derived lead-time
  convention (cycle `floor(HH/6)*6` on day D−1, lead `24+(HH mod 6)`)
  reproduces the correct valid hour at all five airports. Bilinear
  interpolation to each airport's established Open-Meteo grid point
  reproduces the existing, trusted Open-Meteo temperature to within
  0.18-0.25°C (unbiased) at EGLC, LFPG, DSM and YSDU — **PASS**. RNO —
  **FAIL**: a systematic ~-2.04°C cold bias, traced to real local terrain
  (raw grid points near RNO run 246-570 m higher than RNO's own elevation),
  a missing elevation-correction step, not a pipeline bug. Extracts and
  comparison table saved under `data/raw/diagnostics/session36/`.

## Next

**The GRIB-build sub-project (docs/session-36.md) is now mid-flight — step 1
of 4 done, steps 2-4 not started.** Its own next step, if the owner continues
it, is step 2: the bulk cloud/wind pull, at EGLC/LFPG/DSM/YSDU on the
pipeline as validated, with a decision still needed on RNO (below).

**But session 36's own Task 1 finding re-weights the bigger build-vs-lock
question session 35 first raised, and the owner has not yet been asked to
weigh in on that re-weighting specifically:**
1. **The GRIB route no longer promises materially deeper history.** Session
   35's framing treated the GRIB build partly as a way to reach further back
   than Open-Meteo's ~4.3-year window. Session 36 found the AWS bucket's own
   floor is 2021-01-01 (not ~2015) and NCAR's ds084.1 (now on GDEX) shows no
   credential-free path — so the confirmed window is ~4.4 years, essentially
   the same order of magnitude the project already has. **Whatever case
   remains for building the GRIB pipeline now rests entirely on reaching the
   full ~4.3-year window for the richer features (cloud/wind), not on extra
   depth in time** — a narrower, weaker case than F88's original framing.
2. **Go/no-go on a full locked sealed-test cycle for the richer
   features — still open.** F87's multi-fold signal (5-feature beats
   3-feature at 4 of 5 airports and beats raw GFS at 4 of 5) is unchanged by
   this session. The owner's choice is still three-way: (a) lock the richer
   method on the existing ~1.5-year window and carry LFPG's caveat, (b)
   continue the GRIB build (steps 2-4) to reach the full ~4.3-year window
   first — now a narrower prize than originally framed, per point 1 — or (c)
   decline richer features for now and pursue a different branch of Q30.
3. **New, smaller decision: what to do about RNO's elevation gap before any
   GRIB build reaches step 2 for RNO specifically.** F89 found RNO's raw-GRIB
   temperature needs an elevation/lapse-rate correction Open-Meteo already
   applies but this pipeline does not yet — fixable, but not done. The owner
   can decide this once, when/if step 2 is commissioned, rather than now.

None of this was decided this session (session 36 scope forbids it — report
and flag only). **Turning any answer into an actual feature-set design, a
completed GRIB pipeline, or a written lock is still not started.**

**Whatever the owner decides about richer features or a further airport,
Reno's own sealed-test result stands as reported (D44.10, D44.11) — no
re-run, no retroactive adjustment.** Q30's other branches (a second test
year; stage 3, pooling) remain untouched and available, now alongside the
richer-features questions F82/F85/F86/F87/F88/F89 raise.

## Open questions (live)

- **Q30 (unchanged in substance, now joined by four richer-features
  diagnostics).** The owner picked its first branch — more airports, "ramp
  up difficulty" — and Reno's own five steps are finished, ending in a
  failure. The richer-features branch of that intent has now taken four
  concrete steps: session 32's scout (DECISIONS F86) found a real but
  short-window-confounded signal; session 33's blocked CV (F87) removed
  most of that confound and found the recipe recovers at 4 of 5 airports,
  with LFPG the unresolved exception; session 35's GRIB feasibility probe
  (F88) found a deeper source is available but costly; and session 36's GRIB
  build step 1 (F89) found the source is not materially deeper in time than
  the existing window after all, and validated the GRIB→point pipeline at 4
  of 5 airports (RNO needs an elevation-correction fix first). What comes
  next is still the owner's choice: lock on the short window, continue the
  GRIB build (steps 2-4), open another airport, open a second test year (the
  untouched half of the F30/F46/F48/F65 caveat), or open stage 3, pooling.
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
