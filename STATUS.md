# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 12 September 2026, after session 39._

---

## Session 39 (GRIB build sub-project, step 4a of 4 — lock the 5-feature
recipe, no sealed data touched)

**The lock. Writes the frozen 5-feature GRIB recipe into DECISIONS in full
(D48) and freezes the exact sealed-test script — before any sealed-year
data is seen — mirroring how Reno was handled (D44 locked the recipe in
writing, then F82 tested it once). Touches no sealed-year data, runs no
test, produces no sealed-year figure.** After the owner's review and
commit, the recipe is frozen: session 40 (the sealed test) becomes purely
mechanical, with zero decisions left once sealed data is in view.

**D48 pins down, completely, for all five airports at once:** the features
(the same 5-feature set F91 tested — `forecast_temp_c`, `season_sin`,
`season_cos`, `cloud_cover`, `wind_speed_10m`), the GRIB source and pipeline
(AWS `noaa-gfs-bdp-pds`, the F89 lead convention, bilinear grid→point, the
F90 elevation/lapse-rate correction at 7.429 degC/km — stated as five fixed
per-airport constants, EGLC +0.249 to RNO +2.044 degC), the identical
LightGBM settings (D21.4, unchanged), the training window (2021-03-24 to
2025-07-31, trained in FULL, expected row counts reused from F91's own
join), the sealed test year (2025-08-01 to 2026-07-31, expected scored-day
counts reconciled against each airport's own existing-recipe history), the
frozen qualitative bar (beats raw GFS and persistence, SPEC 5.3/D22,
judged once per airport), and pre-registered expectations from F91 (5-feature
expected to pass at **all five airports**, including LFPG and Reno — a
reversal of Reno's own existing sealed-test failure, F82, under a
different, richer recipe on a different data source, not an erasure of it).

**The frozen script:** `scripts/session39_sealed_test.py`. Verified this
session to parse (`py_compile`) and import cleanly (exercising the same
LightGBM/libomp workaround every session-3x modelling script uses, proven
working) — but **not run against sealed data**, since its sealed-year
feature path (`data/processed/grib_features_sealed_window.csv`) does not
exist yet; producing it is session 40's own job. The script self-guards:
it raises rather than proceeding if any loaded date falls outside its
expected window, if the training-row count per airport does not match
D48.7's reconciled figure, if the sealed feature file is missing, or if it
is run with any command-line argument.

**What this session did not do, on purpose.** No sealed-year data (GRIB or
observation-side) was pulled, loaded, or referenced as data. No sealed-year
figure was computed. No recipe was tuned, changed, or adjusted from F91's
own tested recipe. `SPEC.md`/`RESULTS.md` not modified — the method folds
into SPEC only after it passes its sealed test. Nothing was committed.
Script: `scripts/session39_sealed_test.py`. No new notes/ output file (the
script was verified by import, not by running its `main()`).

**Archive step this session:** none. D48 is the newly-frozen recipe the
sealed test will execute against and stays live by definition; F89, F90 and
F91 all remain live inputs to a still-open sealed test and are not settled
yet.

---

## Session 38 (GRIB build sub-project, step 3 of 4 — richer-features CV on
the full v16 window)

**Step 3 of 4. Diagnoses the session-37 cloud-cover tail, joins the
validated GRIB feature dataset (session 37) to the existing IEM
observations over the full v16 window, re-runs the richer-features blocked
seasonal CV on that full ~4.4-year window (GRIB source throughout, instead
of the 1.5-year Open-Meteo window F87 used), and sanity-checks the source
swap. Opens no sealed year, locks nothing.** Verdict (DECISIONS F91):
**cloud-cover tail diagnosed BENIGN-DEFINITIONAL** (sane 0-100 GRIB values,
no concentrated-date artifact, disagreement worst in the genuinely
ambiguous partly-cloudy mid-range rather than at the clear/overcast
extremes, no systematic direction) — GRIB cloud used as-is, not corrected
toward Open-Meteo; **join kept 7,928 of a possible 7,955 rows (99.7%)**;
**on the full window, 3-feature beats raw GFS (GRIB) at 5 of 5 airports
(F87's 1.5-year window: 4 of 5) and 5-feature beats both 3-feature and raw
GFS at 5 of 5 (F87: 4 of 5 on both)** — **LFPG, the one airport that never
beat raw GFS on the shorter window, now beats it at both rungs (+3.3%/
+5.3%)**, and **Reno's richer-features rescue signal not only holds but
strengthens (5-feature +12.7% skill vs raw GFS, against 3-feature's
+6.2%)**; the **source-swap sanity check passes** (GRIB-vs-Open-Meteo raw
MAE differs by at most 0.062 degC on identical rows, an order of magnitude
below any skill margin above).

**Flagged for the owner, not decided this session:** the step-4 lock
question — lock the richer (5-feature) method, and on which window (this
session's full ~4.4-year GRIB window, or something else) — now has
materially stronger evidence behind it than either the scout (F86) or the
1.5-year CV (F87) produced: every airport, including the two previously
unresolved or modest cases (LFPG, Reno), now shows a positive result on
both counts.

**What this session did not do, on purpose.** No sealed-test date
(2025-08-01 onward) loaded, joined, or scored — asserted in code in every
script. No recipe locked. No hyperparameter tuned, no per-airport feature
selection. No lagged/recent-observation feature added, no terrain/elevation
feature added (kept the clean 3-vs-5 comparison). No "correction" applied
to GRIB cloud toward Open-Meteo. `SPEC.md`/`RESULTS.md` not modified. No
new raw data pulled — only small processed tables written under
`data/processed/`. Scripts: `scripts/session38_cloud_diagnostic.py`,
`scripts/session38_join.py`, `scripts/session38_cv.py`,
`scripts/session38_sanity.py`. Full real output: `notes/
session-38-cloud-diagnostic-output.txt`, `notes/session-38-join-output.txt`,
`notes/session-38-cv-output.txt`, `notes/session-38-sanity-output.txt`.
Processed tables: `data/processed/session38_joined.csv`, `data/processed/
session38_cv_summary.csv`.

**Archive step this session:** F88 (session 35's GRIB feasibility probe,
GO-COSTLY) moved to `DECISIONS-archive.md` — its own question is now
settled by the completed build and this session's result; no live open
question needs its specific wording. See DECISIONS.md's pointer note where
F88 used to sit.

---

## Session 37 (GRIB build sub-project, step 2 of 4 — RNO elevation fix,
v16-only bulk pull, cloud/wind validated, feature dataset assembled)

**Step 2 of 4. Fixes RNO's elevation gap (session 36's own finding), pulls
the full feature set (temperature, cloud cover, 10 m wind) over the
v16-only training window at all five airports, validates cloud/wind
against Open-Meteo where a reference exists, and assembles a validated
GRIB feature dataset. Joins nothing to observations, fits no model, opens
no sealed year, locks nothing.** Verdict (DECISIONS F90): **RNO fixed —
the reproduction gate now PASSES at all five airports** (was 4 of 5);
**bulk pull essentially complete** (25,444 of 25,456 messages fetched
cleanly across 6,364 files, ~20 GB, 11.2 minutes; the 12 failures traced to
a real, verified upstream idx/file-size mismatch on 3 specific dates, not
a script bug — dropped and counted, not worked around); **wind speed
validates tightly against Open-Meteo, cloud cover matches well at the
median (1.3 pct) but has a real, heavy tail (p99 88 pct)** on the
2024-01-19..2025-07-31 overlap; **7,952-row feature dataset assembled**
(3 rows dropped, matching the 3 idx-mismatch dates).

**The elevation fix.** Model terrain (HGT:surface) was bilinear-
interpolated to each airport's established grid point, the same way
temperature is, giving each airport's own static grid-orography-vs-
Open-Meteo-grid-elevation gap. A lapse rate fit to exactly zero out RNO's
own measured bias (7.429 degC/km, close to the standard 6.5 degC/km
figure) brings RNO from FAIL (mean|diff| 2.044 degC) to PASS (0.146 degC)
without breaking the four airports that already passed (their own small
gaps produce proportionately small corrections, -0.17 to +0.25 degC). A
notable, unplanned cross-check: EGLC's own independent bias-to-gap ratio
(7.41 degC/km) lands almost exactly on RNO's fitted rate, informal evidence
this is one genuine physical effect rather than an RNO-specific patch.

**Flagged for the owner, not decided this session (see "Next" below):**
whether the cloud-cover validation tail is acceptable to carry into step 3
as-is, and the disk-space/repo-size cost of the ~20 GB this session pulled
(free space fell from 35 GiB to 14 GiB; SPEC 2.3/D15 commits raw pulls, so
this enters the repo's history once committed — a step-change in repo
size versus every prior session).

**What this session did not do, on purpose.** No data before 2021-03-24
(v16-only, by design). No date inside the sealed test year
(2025-08-01 onward) fetched, decoded, or touched — asserted in code. No
join to observations, no model fitted, nothing locked. No whole GRIB file
downloaded — byte-range only. No existing Open-Meteo data modified or
overwritten — read-only for comparison. `SPEC.md`/`RESULTS.md` not
modified. Scripts: `scripts/session37_elevation_fix.py`,
`scripts/session37_grib_pull.py`, `scripts/session37_decode.py`. Full real
output: `notes/session-37-elevation-output.txt`,
`notes/session-37-pull-output.txt`, `notes/session-37-decode-output.txt`.
Raw extracts: `data/raw/grib/` (~20 GB) and
`data/raw/diagnostics/session37/`. Assembled dataset:
`data/processed/grib_features_v16_window.csv` and its companion drop/
validation CSVs.

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
airports opened so far — four pass, one fails; none of that changed this
session. The GRIB-build sub-project (docs/session-36.md through
docs/session-39.md) is now 4a of 4 steps in: step 1 confirmed the
back-extent and validated the GRIB→point pipeline; step 2 fixed RNO's
pipeline gap, pulled the full v16-only feature set, and validated cloud/
wind; step 3 diagnosed the cloud tail, joined the GRIB features to
observations, and re-ran the richer-features blocked CV on the full
~4.4-year window; step 4a (this session) locked the 5-feature recipe in
full (DECISIONS D48) and froze the sealed-test script
(`scripts/session39_sealed_test.py`), with no sealed-year data touched.**
The recipe is now frozen — the sealed test (session 40, step 4b) is purely
mechanical, with zero decisions left to make once the sealed year is
opened.

Step 3, the session before, found (DECISIONS F91): cloud tail diagnosed
benign-definitional; join kept 7,928 of 7,955 rows; **on the full window,
5-feature beats both 3-feature and raw GFS at all five airports — including
LFPG (which never won on the shorter 1.5-year window, F87) and Reno (whose
richer-features rescue signal strengthens rather than merely holding)**;
the source-swap sanity check confirms the GRIB/Open-Meteo baseline shift is
negligible (≤0.062 degC on identical rows). No sealed year opened, no
recipe locked — that is step 4, not yet started.

Step 2, the session before, fixed RNO's elevation gap (DECISIONS F90): the
reproduction gate now **PASSES at all five airports** (RNO fixed via an
elevation/lapse-rate correction, 7.429 degC/km); the bulk pull fetched
25,444 of 25,456 targeted messages cleanly (~20 GB, 6,364 files, 11.2
minutes; the 12 failures trace to a verified upstream idx/file-size
mismatch on 3 dates, dropped and counted); wind speed validated tightly
against Open-Meteo on the 2024-01-19..2025-07-31 overlap, cloud cover
matched well at the median but had a real heavy tail (this session's Task 1
diagnosed that tail); the assembled dataset held 7,952 rows.

Step 1, the session before, confirmed the back-extent at **2021-01-01, not
~2015** — only ~82 days deeper than Open-Meteo's own floor, materially
weakening the case for the GRIB build as a way to reach further back in
time (DECISIONS F89) — and proved the GRIB→point temperature pipeline at
4 of 5 airports before session 37 fixed the fifth (RNO).

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
- **Session 37: GRIB build step 2 of 4 -- RNO elevation fix, v16-only bulk
  pull, cloud/wind validated, feature dataset assembled.** No join, no fit,
  no lock. Verdict (DECISIONS F90): an elevation/lapse-rate correction
  (7.429 degC/km, fit to RNO, cross-checked against EGLC's own independent
  ratio) brings the reproduction gate to **PASS at all five airports**
  (was 4 of 5). The v16-only bulk pull (2021-03-24..2025-07-31, excluding
  the ~82 pre-v16 AWS-only days on purpose) fetched 25,444 of 25,456
  targeted GRIB2 messages (temperature, cloud cover, 10 m wind) across
  6,364 files, ~20 GB, in 11.2 minutes; the 12 failures (3 dates) trace to
  a verified upstream idx/file-size mismatch, dropped and counted per SPEC
  2.2, not a script bug. Cloud/wind validated against Open-Meteo on the
  2024-01-19..2025-07-31 overlap: wind speed matches tightly (sub-2 km/h
  mean absolute difference everywhere); cloud cover matches well at the
  median (1.3 pct) but has a real, heavy tail (p99 88 pct), flagged for the
  owner rather than resolved. Assembled dataset: 7,952 rows (3 dropped,
  matching the idx-mismatch dates), saved under `data/processed/`,
  separate from the raw extracts (`data/raw/grib/`) and the existing
  Open-Meteo files. Disk space fell from 35 GiB to 14 GiB free -- flagged
  for the owner given SPEC 2.3/D15 commits raw pulls to version control.
- **Session 38: GRIB build step 3 of 4 -- richer-features CV on the full
  v16 window.** No sealed year opened, no lock. Verdict (DECISIONS F91):
  the session-37 cloud-cover tail diagnosed **BENIGN-DEFINITIONAL** (sane
  GRIB values, no concentrated-date artifact, disagreement worst in the
  genuinely ambiguous mid-range rather than at the clear/overcast extremes,
  no systematic direction) -- used as-is, not corrected. The GRIB feature
  dataset joined to IEM observations over the full v16 window, keeping
  7,928 of a possible 7,955 rows (99.7%). Blocked seasonal CV (17
  ~93-94-day blocks) on the full ~4.4-year window, GRIB source throughout:
  **3-feature beats raw GFS (GRIB) at 5 of 5 airports** (F87's 1.5-year
  window: 4 of 5) and **5-feature beats both 3-feature and raw GFS at 5 of
  5** (F87: 4 of 5 on both) -- **LFPG (never a winner on the shorter
  window) now beats raw GFS at both rungs, and Reno's richer-features
  rescue strengthens (5-feature +12.7% skill vs raw GFS, from +6.2% at
  3-feature)**. Source-swap sanity check passed: GRIB-vs-Open-Meteo raw MAE
  differs by at most 0.062 degC on identical rows. F88 (GRIB feasibility
  probe, GO-COSTLY) archived to `DECISIONS-archive.md` this session, its
  own question now settled by the completed build. Step-4 lock question
  (which window, whether to proceed) flagged for the owner, not decided.
- **Session 39: GRIB build step 4a of 4 -- lock the 5-feature recipe, no
  sealed data touched.** The owner's answer to session 38's flagged
  question: lock the richer method and proceed. DECISIONS D48 specifies the
  5-feature GRIB recipe completely -- features, source/pipeline (including
  five fixed per-airport elevation-correction constants, F90), model
  settings (D21.4, unchanged), the full training window with expected
  per-airport row counts (reused from F91's own join), the sealed test year
  with expected scored-day counts to reconcile, the frozen qualitative bar,
  and pre-registered expectations (pass at all five airports, from F91).
  The sealed-test script (`scripts/session39_sealed_test.py`) was written
  and frozen, verified this session to parse and import cleanly but not run
  against sealed data (its sealed-year feature file does not exist yet).
  No sealed-year data of any kind was pulled, loaded, or referenced.
  `SPEC.md`/`RESULTS.md` not modified. Nothing was committed.

## Next

**The GRIB-build sub-project (docs/session-36.md through docs/session-39.md)
is now 4a of 4 steps done -- step 4b, the sealed test itself, is the only
step left.** The recipe is now frozen (DECISIONS D48) and the test script is
frozen (`scripts/session39_sealed_test.py`, verified but not run). Step 4b's
own job: pull the sealed-year GRIB feature set (2025-08-01 to 2026-07-31,
following the same byte-range/decode pipeline as session 37, applying the
same five fixed D48.3 elevation corrections) at all five airports, save it
as `data/processed/grib_features_sealed_window.csv` in the same column
layout as the training file, then run `scripts/session39_sealed_test.py`
exactly as written -- no code change, no re-tuning, one look per airport.
Step 4b's own session prompt does not exist yet.

**Pre-registered expectations, recorded in D48 before any sealed data is
seen (from F91):** 5-feature beats both raw GFS and persistence at all five
airports; 5-feature beats 3-feature at all five; LFPG passes (recovered on
the full window, F91); Reno passes (the rescue signal strengthened to
+12.7% skill on the full window, F91) -- a reversal of Reno's own existing
sealed-test failure under the different, existing 3-feature/Open-Meteo
recipe (F82), not an erasure of it (D48.13).

**Two things carried forward from session 37, not resolved by this
session:**
1. **Disk space and repo size.** Session 37's ~20 GB GRIB pull (25,444
   small files) took free space from 35 GiB to 14 GiB; session 38 and this
   session added no new raw bytes (only small `data/processed/` tables and
   a frozen script), so the figure is unchanged. SPEC 2.3/D15 (as qualified
   by D47 for large re-fetchable sources) still means this ~20 GB enters the
   repository's history once committed. Step 4b's sealed-year pull (a
   smaller, ~1-year slice) will add somewhat more on top. Not decided here.
2. The cloud-cover tail question is resolved (F91, BENIGN-DEFINITIONAL) --
   carried forward only as a settled fact behind D48.3/D48.5, not as an open
   item.

**Whatever step 4b finds, Reno's own EXISTING sealed-test result (under the
3-feature/Open-Meteo recipe) stands as reported (D44.10, D44.11, F82) -- no
re-run, no retroactive adjustment.** Q30's other branches (a further
airport; a second test year; stage 3, pooling) remain untouched and
available once step 4b concludes.

## Open questions (live)

- **Q30 (unchanged in substance, now joined by seven richer-features
  diagnostics, and its richer-features branch is one step from resolving on
  its own).** The owner picked its first branch -- more airports, "ramp up
  difficulty" -- and Reno's own five steps are finished, ending in a
  failure. The richer-features branch of that intent has now taken seven
  concrete steps: session 32's scout (DECISIONS F86) found a real but
  short-window-confounded signal; session 33's blocked CV (F87) removed
  most of that confound and found the recipe recovers at 4 of 5 airports,
  with LFPG the unresolved exception; session 35's GRIB feasibility probe
  (F88, since archived -- DECISIONS-archive.md) found a deeper source is
  available but costly; session 36's GRIB build step 1 (F89) found the
  source is not materially deeper in time than the existing window after
  all, and validated the GRIB->point pipeline at 4 of 5 airports (RNO
  needing an elevation-correction fix); session 37's GRIB build step 2
  (F90) fixed RNO's pipeline gap (all five now PASS), bulk-pulled the
  v16-only feature set, validated cloud/wind against Open-Meteo (wind
  tight, cloud cover with a real tail), and assembled a 7,952-row feature
  dataset; session 38's GRIB build step 3 (F91) diagnosed that cloud tail
  as benign, joined the dataset to observations, and found 5-feature beats
  both 3-feature and raw GFS **at all five airports** on the full ~4.4-year
  window -- LFPG and Reno, the branch's two previously weak cases, both now
  show a clear positive result; and session 39's GRIB build step 4a (D48)
  locked the 5-feature recipe completely and froze the sealed-test script,
  with no sealed data touched. **The only step left is step 4b: run the
  frozen script on the sealed test year.** That result (pass or fail, per
  airport) is what will actually settle the richer-features branch of Q30;
  Q30's other branches (a further airport, a second test year, stage 3
  pooling) remain open regardless of how step 4b turns out.
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
