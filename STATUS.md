# STATUS.md — where the project is right now

_This file is a snapshot, overwritten each session — it is not an
accumulating log. History of every earlier STATUS.md is in git._

_Last updated: 20 September 2026, after session 54._

---

## Session 54 (the staged E3 pressure/synoptic experiment — a reading, not
a verdict; the reserved year was never touched)

**Fits four feature variants (B, B+T, B+Tv, B+v — see DECISIONS F101) on
the three non-reserved `EXPERIMENT_FOLDS` (D51) to read whether the
pressure/synoptic family (session 53's own build) adds skill on top of the
frozen 5-feature GRIB baseline. This is a LEARNING experiment: it reports
a grid, not a pass/fail verdict — the family call is made by the owner in
review, next session, mirroring sessions 50 and 52's own E1/E2 shape
exactly. The reserved 2024-08-01..2025-07-31 confirmation year was never
read, at all, this session.** Full account: DECISIONS F101. Script:
`scripts/session54_e3_experiment.py` (new). Full real output: `notes/
session-54-e3-experiment-output.txt`. Tables: `data/processed/
session54_e3_experiment_grid.csv` (60 rows: 5 airports x 3 folds x 4
variants) and `data/processed/session54_e3_experiment_summary.csv` (36
rows: fold-averaged-per-airport, airport-averaged-per-fold, and grand
overall).

**Both sanity checks, both PASS, run before any model was fit.** (1)
`pressure_tendency_3h_hpa == round(pressure_msl_hpa -
pressure_msl_lead_minus3_hpa, 3)` checked on EVERY row of both session53
output files (7,952 rows, not a spot check) — exact match everywhere (max
abs diff 0.0) at all five airports, matching session 53's own already-
passed check. (2) All three `EXPERIMENT_FOLDS` entries cleared
`assert_reserved_year_excluded()` before any data was loaded, plus a
defensive per-row scan (0 hits) confirmed no reserved-year rows in the
loaded data.

**A strong internal-consistency signal, the same check F99/F100 ran:** the
`2025-26` fold's `B` variant (the refit 5-feature baseline) reproduces
F94/F96/F99/F100's own raw-GFS and persistence MAE and row counts almost
exactly at every airport (e.g. EGLC raw 1.2536 vs F94's 1.254, n=364 vs
364; RNO raw 1.5116 vs 1.512, n=365 vs 365) — confirming this session's
pipeline is a correct reproduction, not an independent re-implementation
that happens to look similar.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, 15
airport-folds each):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+T       1.273      -0.011      +0.9%
B+Tv      1.274      -0.009      +0.7%
B+v       1.284      +0.000      -0.0%
```

**The staged question, answered plainly.** (a) `pressure_tendency_3h_hpa`
alone (B+T) already captures the bulk of the family's own grand-overall
benefit — and, unlike E1 and E2, it is the family's OWN BEST variant
(+0.9% vs B+Tv's +0.7%). (b) Adding the raw fields on top of the tendency
(B+Tv) does not add further skill grand-overall — a small reversal of the
"raw-on-top-of-derived never hurts" pattern both E1 (F99) and E2 (F100)
showed. (c) The raw fields alone (B+v, -0.0%) are flat grand-overall — the
family's clearly weakest single addition. **This is by far the smallest
maximum grand-overall skill of the three families explored so far** (E1's
+2.0%, F99; E2's +4.1%, F100; E3's own maximum, B+T, +0.9%).

**DSM, the diagnostic (F96: most headroom): the one airport where adding
the raw fields on top of the derived feature makes things worse, not
better.** B+T +0.7%, but B+Tv -0.3% and B+v -1.0% — DSM is the only
airport where both raw-field variants underperform the frozen baseline
outright, a reversal of the pattern both E1 and E2 showed for DSM
specifically (where the raw-plus-derived variant beat the derived-alone
variant).

**RNO, pre-registered to possibly NOT show an anomaly (PRMSL is
sea-level-normalised, unlike the below-ground upper-air extrapolation,
F98/F99) — the prediction held, cleanly.** RNO shows the strongest
fold-averaged result of any airport in this family: B+T +1.6%, B+Tv +2.2%
(RNO's own best variant, and the single best airport-variant combination
anywhere in the fold-averaged grid). RNO ran with the identical feature
set as every other airport throughout. Unlike upper-air's below-ground
anomaly at RNO (F98/F99), pressure/synoptic shows no RNO-specific
degradation at all.

**A real per-fold reversal, project-wide, in the most recent (2025-26)
fold — flagged as fold-quality, not family weakness, per F96/D52/D53's own
established pattern.** The whole family is positive in 2022-23 and mildly
positive in 2023-24 (airport-averaged), but turns negative across all
three variants in 2025-26 — the only one of the three E-families whose
airport-averaged fold reading is negative for every added-feature variant
simultaneously in the most recent fold. Driven mainly by EGLC (2025-26
B+Tv -5.2%, the family's single worst fold-airport reading) and RNO
(2025-26 B+T -3.1%); DSM and LFPG stay positive or flat in the same fold.

**Feature importances (gain-based, per airport, averaged across the three
folds) — B+T and B+v, per the session prompt's own instruction.**
`pressure_tendency_3h_hpa` sits in the 14.7%-18.1% range at every airport
in B+T — real but not dominant. In B+v, `pressure_msl_hpa` outweighs
`pressure_surface_hpa` at four of five airports, but the two are nearly
equal at RNO (11.8% vs 11.7%) — `pressure_surface_hpa`'s importance is
markedly higher at RNO than anywhere else (11.7% vs 5.6-8.1% elsewhere),
consistent with RNO's own much lower absolute surface pressure (D48.3/F90)
making it a more separable signal there.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — enforced by session53's own output files already excluding it,
plus this session's own defensive per-row scan (0 hits) and the guard
check on all three folds before any data was loaded. Did not compute any
pass/fail verdict — the four-variant grid is reported, the family call is
left to review. Did not do any per-airport feature selection — identical
features at every airport, in every variant, RNO included. Did not add
`lapse_rate_t2_t850` (D52) or `dewpoint_depression_t2m_floored` (D53) to
B — B stays the frozen 5-feature set only. Did not touch any E4/E5 family
(radiation, precipitation). Did not re-pull or re-derive any pressure
field — reused session 53's own output files unchanged. Did not modify
`SPEC.md` or `RESULTS.md`. Nothing was committed.

**Archive step this session:** none — F101 is brand new and obviously
live; D51/D52/D53/F96-F100 all remain live inputs to a still-open
feature-selection programme; nothing else in `DECISIONS.md` became newly
settled this session.

---

## Session 53 (record the E2 verdict, D53, from the owner's review of
session 52's F100 grid; build and validate the E3 pressure/synoptic feature
set — data build only, no model fit)

**Two tasks. Task 1 records the owner's E2 family verdict from review of
session 52's F100 grid as a new decision entry (DECISIONS D53) — no code, no
SPEC/RESULTS edit. Task 2 builds and validates the E3 (pressure/synoptic)
feature set — PRMSL and PRES:surface at each airport's own standard
forecast lead, plus PRMSL at lead-3 (same run) to derive a 3-hour pressure
tendency — mirroring session 49/51's own build-then-experiment shape
exactly. No model was fit anywhere this session; the reserved
2024-08-01..2025-07-31 year was never loaded, pulled, or joined.**

**Task 1 — DECISIONS D53, the E2 family verdict.**
`dewpoint_depression_t2m_floored` (the `B+D` variant) is adopted into the
eventual combine-phase sweep baseline; the three raw moisture fields
(`relative_humidity_2m`/`specific_humidity_2m`/`dew_point_2m`) are NOT
adopted into the sweep, on the same parsimony grounds as D52's E1 call
(`B+D` captures +4.0% of the +4.1% maximum grand-overall skill, F100, on
one feature instead of three). Unlike E1, the raw fields trail the derived
form by only 0.2 points (B+v +3.8% vs B+D +4.0%) and tie or beat it at two
airports (LFPG, DSM) — `relative_humidity_2m` specifically is parked as the
strongest combine-phase candidate (12.7-23.4% of B+v's own gain, F100's
importance breakdown). This is provisional, like every family in the sweep,
confirmed only when the single final feature set is checked on the reserved
year once, at the finish line (D51). E3 and every later family are measured
against the frozen baseline B, not against `B+D` — `B+D` enters only at the
combine phase.

**Task 2 — the E3 (pressure/synoptic) feature build, mirroring session
49/51 exactly.** Pulled `PRMSL` (mean sea level pressure) and
`PRES:surface` at each airport's own standard forecast lead, plus `PRMSL`
at lead-3 from the SAME run, for every date the existing 5-feature GRIB
dataset carries outside the reserved 2024-25 year, and derived
`pressure_tendency_3h_hpa = pressure_msl_hpa - pressure_msl_lead_minus3_hpa`.
Script: `scripts/session53_pressure_pull.py` (new). Full real output:
`notes/session-53-pressure-output.txt`. Outputs: `data/processed/
session53_v16_window_with_pressure.csv` (6,128 rows incl. header),
`data/processed/session53_sealed_window_with_pressure.csv` (1,826 rows
incl. header), `data/processed/session53_pressure_join_drops.csv` (0
rows), `data/raw/diagnostics/session53/session53_pull_manifest.csv`
(19,083 rows), `data/raw/diagnostics/session53/
session53_availability_check.csv` (8 rows).

**Four design decisions confirmed and printed before any pull ran.** (1)
The tendency is a SAME-RUN, two-lead-time difference (lead vs lead-3, one
run made on day D-1) — leakage-safe the same way every other feature in
the project already is (SPEC 2.1b), not a cross-run comparison. (2) Raw
companion fields (`pressure_msl_hpa`, `pressure_surface_hpa`) are pulled
at the standard lead, mirroring E1's raw pressure levels and E2's raw
moisture fields. (3) No elevation correction is applied to any of the
three new fields — PRMSL is mean-sea-level by definition (already
elevation-normalized); PRES:surface and the tendency get bilinear
horizontal interpolation only, the same convention cloud/wind (F91),
upper-air (F98) and moisture (E2) already use. (4) Units converted from
GRIB's native Pa to hPa (divide by 100) for every new column.

**Step 0 — availability check, PASS at every combo, both sample dates.**
Before any bulk pull: confirmed `PRMSL` present, correctly labelled, and
decoding to a real value at the lead-3 offset (f021, f023) at both the v16
floor (2021-03-24) and a recent non-reserved date (2024-06-15), at all
four distinct (cycle, lead) combos the five airports select. Every one of
the 8 checks (4 combos x 2 dates) confirmed presence and a decoded value
landing at the exact expected valid time — including YSDU's own
calendar-day wraparound (cycle 00z, lead 26 -> lead-3=f023 valid the
PREVIOUS calendar day, 23:00 UTC, computed from absolute time rather than
assumed, and confirmed exactly).

**Pull and join: complete, zero failures, zero drops, zero blanks.** 6,361
distinct (run_date, cycle, lead) combos, 19,083 message fetches (3 fields
x 6,361: PRMSL@lead, PRES:surface@lead, PRMSL@lead-3), **0 FAIL rows** in
the manifest, 96.1 minutes at 48-way concurrency (slower than E1/E2's
~56-64 minutes, since each combo now needs 2 idx fetches instead of 1 —
31,805 total requests against E1/E2's ~25,444). Join drops: 0 at every
airport, both spans (row counts match the existing 5-feature dataset
exactly: EGLC/LFPG 1,226/365, DSM/YSDU/RNO 1,225/365). Every one of the
four new columns is null-free at every airport, both spans (n=7,952 total
rows). The derived-tendency arithmetic (`pressure_tendency_3h_hpa ==
round(pressure_msl_hpa - pressure_msl_lead_minus3_hpa, 3)`) was checked on
EVERY row, not a spot check — 0 mismatches across all 7,952 rows. Free
disk space fell from 11.32 to 9.87 GiB (a larger drop than E1/E2's own
~0.02 GiB, from the scratch-file churn of twice as many idx fetches per
combo — no raw bytes were kept, per the fetch-decode-discard pattern; the
drop is attributable to scratch-file overhead during the pull, not a
retained cache).

**Validation: every sanity range holds; RNO's elevation signature
confirmed exactly where expected.** `pressure_msl_hpa` ranges 962-1049 hPa
across all five airports (means 1014.3-1016.9 hPa), inside the expected
950-1050 hPa sea-level band. `pressure_surface_hpa` sits visibly lower at
RNO than everywhere else, as expected from its 1,345 m elevation (SPEC
3.4's highest by a wide margin): RNO's own mean is 837.7 hPa against
980.4-1010.4 hPa at the other four — RNO's own mean surface pressure is
confirmed the LOWEST of the five, reported not corrected, per design
decision 3. `pressure_tendency_3h_hpa` stays well inside the -15..+15
hPa/3h sanity band at every airport (max magnitude 8.987 hPa at EGLC),
zero outliers anywhere.

**Open-Meteo cross-check on `pressure_msl_hpa`, non-reserved overlap
only: close agreement at four airports, a real and larger gap at RNO.**
Mean|diff| ranges 0.044-0.421 hPa at EGLC/LFPG/DSM/YSDU; RNO's own gap is
2.659 hPa (max 7.799 hPa) — real and larger, consistent with RNO's own
already-known grid/elevation complications (D48.3/F90's own largest
elevation-correction constant), though PRMSL is a different physical
quantity (already sea-level-normalized) than E1's below-ground
extrapolation (F98) or E2's moisture gap (F91), so the three RNO figures
are reported separately, not scaled against one another, per design
decision 3's own instruction.

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, skill, or CV. Did not read, load, or join a single row of
the reserved 2024-08-01..2025-07-31 confirmation year (D51) — enforced by
the shared guard function plus a defensive per-date scan (0 hits) before
any pull request was made. Did not pull radiation or precipitation (the
remaining E4/E5 families). Did not do any per-airport feature selection —
identical fields and handling at all five airports throughout. Did not
modify `SPEC.md` or `RESULTS.md`. Nothing was committed.

**Archive step this session:** none — D53 is brand new and live
(provisional pending the finish-line reserved-year check); D51/D52/F96-F100
all remain live inputs to a still-open feature-selection programme;
nothing else in `DECISIONS.md` became newly settled this session.

---

## Session 52 (the E2 moisture experiment — fit the moisture variants on the
three non-reserved folds and read the result; a reading, not a verdict)

**Fits four moisture feature variants (B, B+D, B+Dv, B+v) on the three
non-reserved `EXPERIMENT_FOLDS` (D51) at all five airports, mirroring
session 50/F99's own E1 shape exactly. This is a LEARNING experiment: it
reports a grid, not a pass/fail verdict — the E2 family call is made in
review, next session. The reserved 2024-08-01..2025-07-31 confirmation
year was never read, at all, this session.** Full account: DECISIONS F100.
Script: `scripts/session52_e2_experiment.py` (new). Full real output:
`notes/session-52-e2-experiment-output.txt`. Tables: `data/processed/
session52_e2_experiment_grid.csv` (60 rows: 5 airports x 3 folds x 4
variants) and `data/processed/session52_e2_experiment_summary.csv` (36
rows: fold-averaged-per-airport, airport-averaged-per-fold, and grand
overall).

**Three sanity checks, all PASS, run before any model was fit.** (1) The
reserved-year guard cleared on all three `EXPERIMENT_FOLDS` entries before
any data was loaded. (2) `dewpoint_depression_t2m == round(t2m_raw -
dew_point_2m, 3)` checked on EVERY row of both session51 output files
(7,952 rows, not a spot check) — exact match everywhere (max abs diff
0.0), zero null fields in `relative_humidity_2m`, `dew_point_2m` or
`specific_humidity_2m`. (3) The depression floor
(`dewpoint_depression_t2m_floored = max(dewpoint_depression_t2m, 0)`)
changed exactly 1 of 7,952 rows — DSM 2024-01-26, -0.003 -> 0.000, the
same saturation-boundary row session 51 already flagged — the original
column kept intact, the floor applied only in the feature matrix.

**A strong internal-consistency signal, the same check F99 ran:** the
`2025-26` fold's `B` variant (the refit 5-feature baseline) reproduces
F94/F96's own raw-GFS and persistence MAE and row counts almost exactly at
every airport (e.g. EGLC raw 1.2536 vs F94's 1.254, n=364 vs 364; RNO raw
1.5116 vs 1.512, n=365 vs 365) — confirming this session's pipeline is a
correct reproduction, not an independent re-implementation that happens to
look similar.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, 15
airport-folds each):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+D       1.233      -0.051      +4.0%
B+Dv      1.231      -0.053      +4.1%
B+v       1.235      -0.049      +3.8%
```

**The staged question, answered plainly.** (a) `dewpoint_depression_t2m_
floored` alone (B+D) already captures nearly all of the family's
grand-overall benefit: +4.0% of the +4.1% maximum (B+Dv), on one added
feature. (b) Adding the raw fields on top (B+Dv) adds almost nothing
further (+4.1%, a 0.1-point gain over B+D) — the same shape E1's B+Lv
showed over B+L. (c) **Unlike E1, the raw fields alone (B+v, +3.8%) trail
the derived form (B+D, +4.0%) by only 0.2 points grand-overall** — not the
clear-weakest-addition shape F99 found for E1's raw pressure levels — and
at two airports (LFPG, DSM) B+v ties or beats B+D outright.

**DSM, the diagnostic (F96: most headroom; F99: upper-air did help there):
the moisture family's strongest and most fold-robust result.** DSM leads
every airport under every variant (B+D +6.2%, B+Dv +6.4%, B+v +6.4%) and
is the only airport whose three per-fold readings are all positive and
close together (+5.7%/+6.9%/+5.9% for B+D) — a fold-robust result, not one
fold carrying the average.

**Per-fold caution — two airports where the fold average hides a real
split.** **EGLC's B+D fold average (+2.9%) is carried entirely by the two
earlier folds and reverses in the most recent one**: 2022-23 +5.8%,
2023-24 +4.2%, 2025-26 -1.6% (all three moisture variants lose to B at
EGLC in the 2025-26 fold specifically). **RNO's B+D is flat-to-slightly-
negative in the thinnest fold** (2022-23 -0.2%) but strong in the other
two (2023-24 +7.0%, 2025-26 +7.7%) — the same thin-fold weak-read pattern
already named for 2022-23 generally (F96, D52), not a new concern. LFPG,
DSM and YSDU are positive in all three folds under every variant.

**Feature importances (gain-based, per airport, averaged across the three
folds) — B+D and B+v, per the session prompt's own instruction.**
`dewpoint_depression_t2m_floored` is B+D's leading or near-leading feature
at every airport (17.8% at RNO to 27.3% at EGLC) — real signal, not noise.
In B+v, `relative_humidity_2m` is the clear leading raw moisture field at
every airport (12.7%-23.4%), well ahead of `specific_humidity_2m`
(7.3-8.8%) and `dew_point_2m` (4.3-7.9%). One citation inaccuracy in the
session prompt, noted plainly, not a SPEC/DECISIONS conflict: it describes
this diagnostic as "the same diagnostic F99 reported," but F99's own
script and output contain no feature-importance section — the instruction
itself was followed regardless.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — enforced by session51's own output files already excluding it,
plus this session's own defensive per-row scan (0 hits) and the guard
check on all three folds before any data was loaded. Did not compute any
pass/fail verdict — the four-variant grid is reported, the family call is
left to review. Did not do any per-airport feature selection — identical
features at every airport, in every variant. Did not add
`lapse_rate_t2_t850` (E1's own adopted feature, D52) to B — B stays the
frozen 5-feature set only, per D52's own "measurement baseline is
unchanged" rule. Did not touch any E3+ family (pressure, radiation,
precipitation). Did not pull any new data — reused session 51's own output
files unchanged. Did not modify `SPEC.md` or `RESULTS.md`. Nothing was
committed.

**Archive step this session:** none — F100 is brand new and obviously
live; D51/D52/F97/F98/F99 all remain live inputs to a still-open
feature-selection programme; nothing else in `DECISIONS.md` became newly
settled this session.

---

## Session 51 (record the E1 family verdict; build and validate the E2
moisture feature set — data build only, no modeling)

**Two tasks. Task 1 records the owner's E1 family verdict from review of
session 50's F99 grid as a new decision entry (DECISIONS D52) — no code, no
SPEC/RESULTS edit. Task 2/3 build and validate the E2 (moisture) feature
set — RH, DPT and SPFH at 2 m, plus a derived dew-point-depression feature
— mirroring session 49/F98's build-then-experiment shape exactly. No model
was fit anywhere this session; the reserved 2024-08-01..2025-07-31 year was
never loaded, pulled, or joined.**

**Task 1 — DECISIONS D52, the E1 family verdict.** `lapse_rate_t2_t850`
(the `B+L` variant) is adopted into the eventual combine-phase sweep
baseline; the three raw pressure-level temperatures (`t850`/`t925`/`t700`)
are NOT adopted into the sweep, on parsimony grounds (`B+L` captures +1.9%
of the +2.0% maximum grand-overall skill, F99, on one feature instead of
four). RNO's own real, fold-robust raw-level skill increment (`B+v` +1.4%/
+2.0%/+2.7% across the three folds, F99) is parked as an explicit
combine-phase candidate, not carried into the sweep now — RNO is already
carried to about +11% skill by cloud/wind in the frozen baseline (F94,
F96), and the DSM case for the raw levels rests on a single fold (2025-26,
the year F96 flagged unrepresentative). This is provisional, like every
family in the sweep: confirmed only when the single final feature set is
checked on the reserved year once, at the finish line (D51). E2 and every
later family are measured against the frozen baseline B, not against
`B+L` — `B+L` enters only at the combine phase.

**Task 2/3 — the E2 (moisture) feature build, mirroring session 49/F98
exactly.** Pulled `relative_humidity_2m` (RH), `dew_point_2m` (DPT) and
`specific_humidity_2m` (SPFH), all at 2 m, for every date the existing
5-feature GRIB dataset carries outside the reserved 2024-25 year, and
derived `dewpoint_depression_t2m = t2m_raw - dew_point_2m` on the raw
(grid-elevation) basis, per the session prompt's own design decision.
Script: `scripts/session51_moisture_pull.py` (new). Full real output:
`notes/session-51-moisture-output.txt`. Outputs: `data/processed/
session51_v16_window_with_moisture.csv` (6,128 rows incl. header),
`data/processed/session51_sealed_window_with_moisture.csv` (1,826 rows
incl. header), `data/processed/session51_moisture_join_drops.csv` (0
rows), `data/raw/diagnostics/session51/session51_pull_manifest.csv`
(19,083 rows).

**Three design decisions confirmed and printed before any pull ran.** (1)
The depression uses `t2m_raw` (recovered algebraically from
`temperature_grib_c` and each airport's own D48.3/F90 correction constant,
no new 2 m-temperature pull), not the elevation-corrected
`temperature_grib_c` — a same-basis-difference requirement, not a style
choice. (2) No elevation/lapse-rate correction applied to RH, DPT or SPFH
— bilinear horizontal interpolation only, the same convention cloud
cover/wind speed (F91) and the upper-air levels (F98) already use. (3) No
raw GRIB2 bytes kept on disk (disk-space-forced, ~11.3 GiB free at session
start) — fetch-decode-discard, a per-request manifest standing in as the
provenance record, same pattern as F98.

**Pull and join: complete, zero failures, zero drops, zero blanks.**
6,361 distinct (run_date, cycle, lead) combos, 19,083 message fetches
(3 fields x 6,361), **0 FAIL rows** in the manifest, 63.4 minutes at
48-way concurrency. Join drops: 0 at every airport, both spans (row counts
match the existing 5-feature dataset exactly). Every one of the five new
columns is null-free at every airport, both spans (n=7,952 total rows).
Free disk space essentially unchanged after the pull (11.30 to 11.28 GiB),
confirming no bytes leaked past the decode-then-discard step.

**Validation: one real, isolated, verdict-irrelevant physical-sanity
finding; otherwise clean.** `dew_point_2m <= t2m_raw` holds at 7,951 of
7,952 rows; the single exception (DSM, 2024-01-26: dew_point_2m 1.113 vs
t2m_raw 1.110, RH reported exactly 100.0%) is a 0.003 degC crossing at the
saturation boundary, not a systematic basis or decode error — dew point
and 2 m temperature/RH are independently bilinear-interpolated fields, and
a thousandth-of-a-degree divergence at RH=100% is ordinary
interpolation/rounding noise, reported rather than clipped or dropped, per
instruction. `relative_humidity_2m` in [0, 100] and `specific_humidity_2m`
>= 0 hold at every one of the 7,952 rows, no exception. The Magnus
internal-consistency self-check (recomputing RH from `t2m_raw` and
`dew_point_2m`) agrees closely everywhere (mean|diff| 0.124-0.359 pct);
DSM's own max|diff| (17.4 pct) is a single-row artifact of the same
near-saturation boundary case above, where the Magnus relation's
exponential is most sensitive to small input differences — not a
systematic DSM issue.

**Cross-check against Open-Meteo (the non-reserved portion of the overlap
only): agreement is close at four airports, real and larger but still
modest at RNO.** A new small Open-Meteo pull (dew_point_2m,
relative_humidity_2m, Previous Runs API, `_previous_day1`) covered exactly
the two non-reserved windows — 2024-01-19..2024-07-31 (before the
reservation starts) and 2025-08-01..2026-07-31 (the sealed span, entirely
after it ends) — saved under `data/raw/diagnostics/session51/` with
`.meta.txt` provenance per file. Dew point mean|diff| ranges 0.153-0.208
degC at EGLC/LFPG/DSM/YSDU, 0.809 degC at RNO (max 2.406 degC); RH
mean|diff| ranges 0.460-0.885 pct at the same four, 1.969 pct at RNO (max
13.1 pct). RNO's larger gap is consistent with its own already-known
grid/elevation complications (D48.3/F90's own largest elevation-correction
constant, +2.044 degC) and is reported plainly, not investigated further —
out of this session's data-build-only scope.

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, skill, or CV — data build and validation only. Did not
read, load, join, or score a single row of the reserved
2024-08-01..2025-07-31 confirmation year (D51) — enforced by the shared
guard function plus a defensive per-date scan (0 hits) before any pull
request was made. Did not pull moisture, pressure, radiation or
precipitation beyond the three E2 fields named in the session prompt. Did
not modify `SPEC.md` or `RESULTS.md`. Did not do any per-airport feature
selection — identical fields and handling at all five airports throughout,
including the Open-Meteo cross-check pull. Nothing was committed.

**Archive step this session:** none — D52 and F99 are both brand new and
live (D52 is provisional pending the finish-line reserved-year check; F99
is D52's own citation basis and stays live with it); nothing else in
`DECISIONS.md` became newly settled this session.

---

## Session 50 (the staged E1 upper-air experiment — a reading, not a
verdict; the reserved year was never touched)

**Fits four feature variants (B, B+L, B+Lv, B+v — see DECISIONS F99) on the
three non-reserved `EXPERIMENT_FOLDS` (session 48, D51) to read whether the
upper-air/vertical-structure family (session 49, F98) adds skill on top of
the frozen 5-feature GRIB baseline. This is a LEARNING experiment: it
reports a grid, not a pass/fail verdict — the family call is made in
review. The reserved 2024-08-01..2025-07-31 confirmation year was never
read, at all, this session.** Full account: DECISIONS F99. Script:
`scripts/session50_e1_experiment.py` (new). Full real output: `notes/
session-50-e1-experiment-output.txt`. Tables: `data/processed/
session50_e1_experiment_grid.csv` (60 rows: 5 airports x 3 folds x 4
variants) and `data/processed/session50_e1_experiment_summary.csv` (36
rows: fold-averaged-per-airport, airport-averaged-per-fold, and grand
overall).

**Two sanity checks, both PASS, run before any model was fit.** (1)
`t2m_raw`'s derivation (`t2m_raw == temperature_grib_c - elevation_constant`,
D48.3/F90) checked on EVERY row of both session49 output files (7,952 rows
total, not a spot check) — exact match everywhere, max absolute difference
0.0 at all five airports. (2) All three `EXPERIMENT_FOLDS` entries cleared
`assert_reserved_year_excluded()` before any data was loaded.

**A strong internal-consistency signal, not asked for but worth recording:**
the `2025-26` fold's `B` variant (the refit 5-feature baseline, same
features as F94/F96, though trained on one fewer year — 1,222-1,225 days
vs F94's 1,591, because training may not reach the reserved year)
reproduces F94/F96's own raw-GFS and persistence MAE and row counts almost
exactly at every airport (e.g. EGLC raw 1.2536 vs F94's 1.254, n=364 vs
364; RNO raw 1.5116 vs 1.512, n=365 vs 365) — confirming this session's
pipeline (join, features, model settings) is a correct reproduction, not an
independent re-implementation that happens to look similar.

**Result — grand overall (mean MAE across all 5 airports x 3 folds, 15
airport-folds each):**

```
variant   mean MAE   delta vs B   skill vs B
B         1.284       --           --
B+L       1.260      -0.024       +1.9%
B+Lv      1.258      -0.026       +2.0%
B+v       1.271      -0.013       +1.0%
```

**The staged question, answered plainly.** (a) `lapse_rate_t2_t850` alone
(B+L) already captures nearly all of the family's benefit: +1.9% skill vs
the refit baseline, on one added feature. (b) Adding the raw levels on top
(B+Lv) adds almost nothing further (+2.0%, a 0.1-point gain over B+L) — the
derived form is doing almost all of the work overall. (c) The raw levels
WITHOUT the derived form (B+v) underperform B+L at every fold-averaged
airport except RNO (+1.0% overall, clearly the weakest of the three
additions) — the model does better handed the physically-motivated
difference directly than left to reconstruct it from three raw
temperatures.

**DSM, the diagnostic (F96 flagged it as the airport with the most
headroom, since cloud/wind were marginal-to-slightly-negative there): a
real positive signal, and one of two airports where the raw levels add
something the derived form alone does not.** Fold-averaged skill vs B:
B+L +2.2%, B+Lv +2.7% (DSM's own best variant), B+v -0.1% (flat/negative,
the same shape cloud/wind showed at DSM in F96). So the honest read at DSM
is not "upper-air doesn't help" — lapse rate helps, and the raw levels add
a further real increment on top of it, unlike cloud/wind's own marginal
read there.

**RNO, pre-registered to behave oddly (F98: t925 there is a below-ground
extrapolation, `lapse_rate_t2_t850` partly degenerate) — the prediction
held, with a genuinely interesting twist.** Fold-averaged skill vs B: B+L
+0.0% (flat — the derived lapse-rate feature adds nothing at RNO, exactly
as F98 predicted), but B+Lv +1.8% and B+v +2.0% (RNO's own best variant) —
the RAW pressure-level temperatures still carry real, usable skill at RNO
even though the specific derived difference (`t2m_raw - t850`) does not.
RNO ran with the identical feature set as every other airport throughout
— no exclusion, no RNO-specific feature.

**What this session did not do, on purpose.** Did not read, load, or score
a single row of the reserved 2024-08-01..2025-07-31 confirmation year
(D51) — enforced by session49's own output files already excluding it,
plus this session's own defensive per-row scan (0 hits) and the guard check
on all three folds before any data was loaded. Did not compute any
pass/fail verdict — the four-variant grid is reported, the family call is
left to review. Did not do any per-airport feature selection — identical
features at every airport, in every variant. Did not touch any E2+ family
(moisture, pressure, radiation, precipitation). Did not pull any new data
— reused session 49's own output files unchanged. Did not modify `SPEC.md`
or `RESULTS.md`. Nothing was committed.

**Archive step this session:** none — F99 is brand new and obviously live;
D51/F97/F98 all remain live inputs to a still-open feature-selection
programme; nothing else in `DECISIONS.md` became newly settled this
session.

---

## Session 49 (build and validate the E1 upper-air/vertical-structure
feature set — data build only, no modeling)

**Pulls, decodes, and joins the three E1 upper-air fields (TMP at 925, 850,
and 700 hPa, session 47's own confirmed labels, F97) onto the existing
5-feature GRIB dataset, at every date that dataset already carries OUTSIDE
the reserved 2024-25 confirmation year (D51). Data-build-only: no model
was fit, no MAE or CV was computed, and the reserved year was never
loaded, pulled, or joined.** Full account: DECISIONS F98. Script:
`scripts/session49_upper_air_pull.py` (new). Full real output: `notes/
session-49-upper-air-output.txt`. Outputs: `data/processed/
session49_v16_window_with_upper_air.csv` (6,128 rows), `data/processed/
session49_sealed_window_with_upper_air.csv` (1,826 rows), `data/processed/
session49_upper_air_join_drops.csv` (0 rows), `data/raw/diagnostics/
session49/session49_pull_manifest.csv` (19,083 rows, provenance only — no
raw GRIB2 bytes kept, see below).

**Two design points confirmed before any pull ran.** (1) 925/850/700 hPa
are fixed pressure surfaces, not surface-terrain-tied — SPEC 7.2's 7.429
degC/km elevation correction was correctly NOT applied to them, bilinear
horizontal interpolation only. (2) The lapse-rate feature's raw 2 m
temperature (`t2m_raw`) needed no new GRIB pull at all — it was recovered
algebraically from the existing elevation-corrected `temperature_grib_c`
and each airport's own fixed D48.3/F90 correction constant
(`t2m_raw = temperature_grib_c − correction_c`).

**A third decision, forced by disk space (~11 GiB free at session start,
session 37's own ~20 GB raw cache already on this disk): no raw GRIB2
bytes were kept for this pull.** Each message was byte-range-fetched,
decoded immediately with eccodes, and discarded — the same
fetch-decode-discard pattern session 47's own probe used, extended here to
a full multi-year pull — with a per-request manifest (no bytes) standing
in as the provenance record, per D47's "manifest, not bytes" policy taken
one step further. Free space was still ~12 GiB after the pull, confirming
no bytes leaked to disk.

**Guard check (D51).** The date list was built from the existing dataset's
own real rows (not an assumed continuous calendar), giving a train span of
2021-03-24..2024-07-31 (1,226 dates) and a sealed span of
2025-08-01..2026-07-31 (365 dates) — 1,591 dates total, with the reserved
year's ~365 days simply absent. Checked with `scripts/
session48_reserved_year.py`'s own `assert_reserved_year_excluded()` on both
spans (passed) plus a defensive per-date scan of all 1,591 dates (0
reserved dates found) before any pull request was made.

**Pull and join: complete, zero failures, zero drops.** 6,361 distinct
(run_date, cycle, lead) combos, 19,083 message fetches, **0 FAIL rows** in
the manifest (56.4 minutes at 48-way concurrency). The join onto the
existing dataset matched row counts exactly at all five airports in both
spans (v16_window: EGLC/LFPG 1,226, DSM/YSDU/RNO 1,225; sealed_window: all
five 365) — `session49_upper_air_join_drops.csv` is empty.

**Validation: sanity ranges hold at four of five airports; a real,
reportable anomaly at RNO.** Every new column is null-free everywhere, and
all 19,083 messages decoded successfully (this is a data-character finding,
not a decode failure). At EGLC, LFPG, DSM, and YSDU, mean temperature
falls with height as expected (t2m_raw > t925 > t850 > t700). **At RNO the
ordering inverts**: mean t925 (20.79 degC) is warmer than mean surface
temperature (16.18 degC), and mean t850 (16.13 degC) sits almost exactly
level with the surface (mean `lapse_rate_t2_t850` = 0.05 degC, against
8-12 degC at the other four airports). The likely cause, stated as a
plausible explanation and not investigated further this session (out of
scope): RNO's own airport elevation (1,345 m, SPEC 3.4's highest by a wide
margin) sits at or above the standard-atmosphere altitude of the 925 hPa
(~760 m) and even 850 hPa (~1,460 m) pressure surfaces, so those
fixed-pressure fields are likely extrapolated below-ground at Reno rather
than measuring a real atmospheric layer. **Flagged plainly for session 50**:
an E1 lapse-rate feature may behave very differently at RNO than elsewhere,
for a real physical reason tied to Reno's own terrain, not a data-quality
problem.

**Spot-check.** F97's own decoded-value sample date (2025-06-15) now falls
*inside* the reserved year (D51 postdates F97) and was correctly never
touched by this session. The spot-check instead used F97's other confirmed
date, the v16 floor (2021-03-24) — this session's own EGLC row there
decodes to t925=3.07, t850=0.251, t700=-7.742 degC, physically plausible
and correctly colder with height.

**What this session did not do, on purpose.** Did not fit any model,
compute any MAE, or run any CV — session 50's job. Did not load, pull, or
join a single row of the reserved 2024-08-01..2025-07-31 year (D51). Did
not pull moisture, pressure, or any other E2+ family. Did not touch the
frozen 5-feature sealed-test script. Did not apply the surface elevation
correction to any of the three new fields. Did not modify `SPEC.md` or
`RESULTS.md`. Nothing was committed.

**Archive step this session:** none — F98 is brand new and obviously live;
nothing else in `DECISIONS.md` became newly settled this session.

---

## Session 48 (reserve the 2024-25 confirmation year — setup only, no
experiments)

**A small discipline-setup session, run before any feature experiment.
Formally reserves 2024-08-01 to 2025-07-31 as an untouchable confirmation
year for the upcoming feature-selection programme, and enforces the
reservation in code so no later experiment can accidentally touch it. Runs
no experiment, fits no feature model, and reads no result on the reserved
year.** Full account: DECISIONS D51. Script: `scripts/
session48_reserved_year.py` (new, date-arithmetic only — no data loaded, no
model fit). Full real output: `notes/session-48-guard-check-output.txt`.

**Why now.** F96 (session 46) already used every year 2022-2026
descriptively for the existing frozen recipes — legitimate there only
because nothing was tuned. A feature-selection programme chooses between
feature sets on held-out performance, which is itself a form of fitting to
data, so it needs its own fresh, never-touched year or it has no honest
finish line. The owner chose 2024-25: feature-complete for every candidate
family (F97) and a solid middle year, distinct from the 2025-26 sealed year
(F94).

**The rule (D51).** No feature experiment — train or test, any feature set
— may touch 2024-08-01..2025-07-31 until a single pre-chosen final feature
set is confirmed on it once, at the end of the programme, and that result
stands as reported. It does not disturb the 2025-26 sealed year (F94) or any
existing minimal-method verdict.

**The harness change.** `scripts/session48_reserved_year.py` defines the
reservation and a guard, `assert_reserved_year_excluded()`, that raises if a
proposed fold's training or test window overlaps the reserved year. It also
defines `EXPERIMENT_FOLDS` — three folds for a future feature-experiment
session to build from (F96's rolling-origin list minus the fold testing
2024-25, with the fold testing 2025-26 truncated so training stops at
2024-07-31, before the reserved year, so it never enters an experiment's
training pool either):

```
label      train                    test
2022-23    2021-03-24..2022-07-31   2022-08-01..2023-07-31
2023-24    2021-03-24..2023-07-31   2023-08-01..2024-07-31
2025-26    2021-03-24..2024-07-31   2025-08-01..2026-07-31   (train truncated)
```

**Verified by construction only.** All three `EXPERIMENT_FOLDS` entries pass
the guard; three deliberately reserved-year-touching folds (one mirroring
F96's own original, unreserved "2025-26" fold; one testing the reserved year
directly; one training into it) all raise `ValueError` as expected. No
model was fit and no data was loaded anywhere in the verification — pure
date-range checks.

**The honest cost.** The "2025-26" experiment fold loses 365 days (1.00
years) of training data versus F96's own equivalent fold (1,591 to 1,226
days), because training may not reach into the reserved year. The
feature-selection programme now works from three folds instead of F96's
four; the "2022-23" fold (495 days, thinnest) is unaffected, since it never
reached 2024-25 in the first place.

**What this session did not do, on purpose.** Did not run any feature
experiment, fit any feature model, or compute any result on 2024-25 or any
other year. Did not pull any new data. Did not touch the 2025-26 sealed year
or restate any existing verdict. Did not choose or lock a feature-experiment
ordering — that is a later, separate session's job, using the F97
availability map (session 47). Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed.

**Archive step this session:** none — D51 is brand new and obviously live;
nothing else in `DECISIONS.md` became newly settled this session.

---

## Session 47 (feature-family availability probe — radiation, upper-air,
moisture, pressure, precipitation; a map, not an experiment)

**A cheap availability probe, the same shape as sessions 31 and 35: finds
out which new GRIB feature families exist, under what exact label/level, at
the project's own forecast lead, and how far back — so a later session can
plan feature-experiment ordering on facts rather than guesses. Builds
nothing, models nothing, pulls no bulk data, derives no feature, and picks
no ordering.** Full account: DECISIONS F97. Script:
`scripts/session47_availability_probe.py` (new). Raw idx extracts + `.meta.txt`
provenance: `data/raw/diagnostics/session47/` (8 files). Summary tables:
`data/raw/diagnostics/session47/session47_availability_map.csv` (27 rows)
and `session47_precip_rno_spotcheck.csv` (4 rows).

**Result: all 27 candidate variables across all five families (radiation,
upper-air, moisture, pressure, precipitation) are present, identically
labelled, at both the v16 floor (2021-03-24) and a recent date (2025-06-15),
at the airports' own forecast lead, and decode to a real, non-null value.**
No candidate was found absent at either date. **The headline: upper-air /
vertical structure (TMP at 925/850/700 mb, HGT at 500/850 mb, UGRD/VGRD/RH
at 850 mb) is confirmed genuinely available, instantaneous, and clean at the
forecast lead — with no caveat** — this is exactly the family DECISIONS F85
found blocked on Open-Meteo ("not available in any leakage-safe form... at
any date or airport"), and the family the GRIB build was specifically
expected to unlock. Moisture (RH/DPT/SPFH:2m, PWAT) and pressure (PRMSL,
PRES:surface) are likewise available and clean. Radiation and precipitation
are both available but awkward: the "averaged"/"accumulated" fields
(DSWRF/USWRF/DLWRF/ULWRF, APCP, PRATE's averaged variant) carry a window
that depends on each airport's own forecast lead — a genuine 6-hour average
at EGLC/LFPG/DSM (lead 24) but only a 2-hour average at YSDU/RNO (lead 26) —
a real cross-airport inconsistency to design around, not a missing-data
problem. A Reno-specific spot-check of the precipitation family (RNO's own
grid point) returned zero for all four fields on the sample date — a real
dry/snow-free reading (each field's own grid-wide maximum is well above
zero on the same message), not a decode failure.

**What this session did not do, on purpose.** Did not pull any bulk or
date-range data — 8 idx inventories and 31 small byte-range spot-check
messages only. Did not use any date before 2021-03-24 (v15 excluded,
D48.7). Did not decide a feature-experiment ordering, or which family to
try first — that is a separate, later planning step, done with this map in
hand. Did not derive any feature (dew-point spread, pressure tendency) from
the confirmed ingredients. Did not modify `SPEC.md` or `RESULTS.md`.
Nothing was committed.

**Archive step this session:** none — F97 is brand new and obviously live;
nothing else in `DECISIONS.md` became newly settled this session.

---

## Session 46 (multi-year generalisation backtest of the current models,
24h lead — a descriptive profile, not a new verdict)

**Opens the next phase after the GRIB build's close (session 45): the
multi-year robustness profile of the EXISTING FROZEN 3-feature and
5-feature GRIB recipes, walking the train/test cutoff forward one year at
a time and refitting each recipe, unchanged, on each fold's own training
window. This is a descriptive measurement, benchmarked against F94, not a
new sealed test — it decides no pass/fail and does not re-open, re-tune, or
overwrite F94 or F16–F82, which stand exactly as reported.** Full account:
DECISIONS F96. Script: `scripts/session46_backtest.py` (new). Full real
output: `notes/session-46-backtest-output.txt`. Tables:
`data/processed/session46_backtest_profile.csv` (150 rows) and
`data/processed/session46_fold_table.csv` (50 rows).

**Mid-session correction, owner-confirmed before Task 1 was built.** The
session prompt (docs/session-46.md) restricted the 5-feature folds to
training windows starting no earlier than 2024-01-19, citing F85 (cloud
cover/wind speed unavailable earlier). That citation holds for
**Open-Meteo**, the source F85 actually tested — it does not hold for the
**GRIB** source this session uses, which the GRIB build (sessions 36–38,
F90/F91, archived) specifically pulled across the full v16 window
(2021-03-24 onward) to close that exact gap (SPEC §7.2). Checked directly
before use: `grib_features_v16_window.csv` carries real, non-null cloud
cover and wind speed values back to 2021-03-24, zero blanks across 7,952 +
1,825 rows. Flagged to the owner mid-session (CLAUDE.md: stop and flag a
session-prompt/SPEC disagreement) rather than resolved unilaterally; the
owner confirmed widening the 5-feature folds to match 3-feature's four
training starts, subject to the non-null check (enforced in code) and
never crossing the 2021-03-24 v16 floor (D48.7, a model-version boundary,
not a data-availability one). The two original thin 2024-01-19-start folds
were kept alongside the widened ones, not replaced.

**The fold design.** 3-feature: four rolling folds, training from
2021-03-24 through 2022-07-31/2023-07-31/2024-07-31/2025-07-31, each
testing the following Aug 1–Jul 31 year (2022-23, 2023-24, 2024-25,
2025-26). 5-feature: the same four full-window folds plus the two original
thin folds (training from 2024-01-19). The 2022-23 fold (~1.35yr training)
and both thin folds are explicitly flagged THIN — a weaker read, not an
equal one.

**The profile — 3-feature beats raw GFS (GRIB) at 18 of 20 airport-years;
5-feature at 19 of 20; 5-feature beats 3-feature at 17 of 20 full-window
airport-years (not all 20 — see below).** The only raw-GFS losses (EGLC
-0.6%, YSDU -4.6%/-5.3%) fall in the single thinnest fold, 2022-23 — a
thin-training-window effect, not an airport-fragility one: DSM, LFPG and
RNO win against raw GFS at every one of their four full-window years,
under both feature sets. The two thin 5-feature folds fare markedly worse
(2024-25-thin: only 2 of 5 airports beat raw GFS, closely reproducing
session 32's scout finding, F86, that a starved window — not the extra
features — was the dominant effect). **The 5-vs-3-feature comparison is
more nuanced than a clean sweep**: cloud cover and wind speed reliably
help at EGLC, LFPG and RNO (4/4 years each), help variably at YSDU (3/4),
and are marginal to slightly negative at DSM (5-feature loses to 3-feature
in 2 of 4 years) — DSM's three-feature model already appears to capture
most of its own learnable bias, leaving little room for the extra
features to add.

**Consistency check: exact reproduction of F94.** The `2025-26` fold (both
feature sets) uses exactly D48's own training and sealed-test windows —
every row count matches F94 exactly and every MAE matches to within 0.0005
degC, confirming the backtest pipeline correctly reproduces the frozen
recipe rather than approximating it.

**The honest read (Task 4, report only).** Whether 2025-26 was a
flattering test year has no single project-wide answer: EGLC and LFPG's
sealed-year margins are clearly the largest of their own four years
(supporting F48's concern), while DSM's sealed-year margin is clearly its
*weakest* of the four — the opposite pattern. **RNO's 5-feature skill vs
raw GFS is remarkably stable across all four years (+10.2% to +11.5%)** —
the tightest band of any airport in the profile, and the strongest
evidence yet that Reno's richer-features rescue (F94, reversing the
existing recipe's own sealed-test failure, F82) is a real, repeatable
effect rather than a single-year artifact. The 5-feature multi-year read
is less limited than the original session prompt expected, now that GRIB's
own cloud/wind coverage is confirmed back to 2021-03-24 — it covers the
same four years as 3-feature, not just two — though all four years still
come from one continuous, overlapping weather record, not independent
climate samples, and the profile is GRIB-source-only (it says nothing new
about the existing 3-feature/Open-Meteo recipe's own robustness).

**What this session did not do, on purpose.** Did not pull any new data —
reused the existing GRIB feature files and IEM chunks, read-only. Did not
run +48h lead. Did not tune, select, or add any feature or hyperparameter
— both recipes are refit-only. Did not test any fold on a date it trained
on (asserted in code). Did not treat this as a sealed test or compute any
pass/fail verdict. Did not re-open, re-litigate, or restate F94 or F16–F82
as changed. Did not modify `SPEC.md` or `RESULTS.md`. Nothing was
committed.

**Archive step this session:** none. Nothing newly settled this session
that a live open question or STATUS.md's own "Next" section does not still
need in full — F96 is brand new and obviously live; nothing else in
`DECISIONS.md` changed status.

---

## Session 45 (close out the build — archive settled GRIB-build findings,
one RESULTS wording fix; documentation only)

**The last session of the GRIB build. Two tasks, both documentation only —
no code, model, data, or figure touched.** Full account: DECISIONS D50.

**Task 1 — RESULTS.md §5.5 fix.** The sentence "3-feature −7.7%,
5-feature −2.1%, on the scout and the follow-up CV respectively (DECISIONS
F86, F87)" mis-paired the two figures with their sources — both numbers are
actually the follow-up CV's own LFPG figures (F87); the scout (F86) gives
LFPG a different pair (−25.7% / −13.5%). Reworded to the neutral form that
avoids the mis-pairing: "both models stayed negative across the scout and
the follow-up CV (DECISIONS F86, F87)." No figure anywhere else in
`RESULTS.md` was touched.

**Task 2 — the archive pass.** Applied the D46 criterion (settled, and no
live open question or `STATUS.md`'s own "Next" section needs the specific
wording, only the headline) to every build-era `DECISIONS.md` entry,
session 31 onward. **Moved: F85, F86, F87, F89, F90, F91, F92, F93, D48**
(1,797 lines, byte-exact, mechanical line-range extraction — `sed`, not
hand-reproduced) to a new dated section in `DECISIONS-archive.md`,
`## Moved by session 45 (2026-09-12)`, with a pointer to `SPEC.md` §7 /
`RESULTS.md` §5 for the headlines. F88 was already archived in session 38.
**Kept live:** D46 (the archiving-workflow decision itself, not build-era),
the existing F88 pointer note, D47 (a standing rule, split out of the same
session-37 entry F90 sat in), D49 and F95 (fresh consolidation records
`STATUS.md` still cites directly), and Q30/Q32/the parked items/D17/F7 (all
pre-build-era, untouched). **F94 (the headline sealed-test pass) meets the
same MOVE criterion but was deliberately flagged rather than moved** — it
is very fresh, and the owner may prefer to keep it live a little longer;
it stays in `DECISIONS.md` pending that call. `DECISIONS.md` falls from
2,359 to 636 live lines. No entry was edited, reworded, renumbered, or
deleted — every `(Dxx)`/`(Fxx)` citation resolves exactly as before, now
into `DECISIONS-archive.md` for the moved set.

**What this session did not do, on purpose.** Did not edit, reword, or
delete any moved entry — verbatim relocation only. Did not renumber
anything or rewrite any citation. Did not touch `SPEC.md`, and touched
`RESULTS.md` only for the §5.5 clause. Did not touch any code, data,
model, or figure. Nothing was committed.

**With this session, the GRIB-build sub-project (docs/session-36.md
through docs/session-45.md) is fully closed**: built (steps 1–4, sessions
36–39), tested once (sessions 40–42, DECISIONS F94), folded into `SPEC.md`
and `RESULTS.md` (sessions 43–44, D49/F95), and now archived (session 45,
D50). Nothing further is expected from this sub-project unless the owner
reopens it.

**Archive step this session: the archive pass itself (Task 2 above) — the
sub-project's own detailed evidence base moved out of the live file, per
`CLAUDE.md`'s routine end-of-session step, batched here because the whole
sub-project came due at once.**

---

## Session 44 (consolidation part 2 — rewrite RESULTS.md to cover both
methods; documentation only)

**Rewrites `RESULTS.md` — the standalone technical summary — so it tells
the whole story: the minimal method (four passes, Reno fails) and the
proven richer 5-feature GRIB method (five passes, Reno passes), with the
honest framing SPEC deliberately deferred to this file. Documentation
only — no code, model, data, or figure touched.** Full account: DECISIONS
F95.

**What changed.** The intro was re-dated and now states the project has
two proven methods. Sections 2–4 (the minimal method's own method
description, five-airport results table, and six findings) are left
substantially intact, with three forward pointers added so a reader lands
on the new section 5 at the right moment (the section-2 intro, a note
under the section-3 table, and a closing sentence on finding 4 — the Reno
failure). A new **section 5, "Act two: the richer-features GRIB method,"**
covers what differs from the minimal method, pre-sealed-test validation,
the lock and sealed test with the F94 results table in full, and three
centrepieces: **the honest Reno decomposition** (leads with the 5-vs-3
margin, +7.5%, not the +11.0% vs-raw-GFS margin; states plainly that
Reno's GRIB raw-GFS baseline, 1.512, is measurably weaker than the
Open-Meteo baseline the minimal method faced, 1.414, F82; and shows the
pass is robust to that difference, a recomputed ~+4.8% margin against an
Open-Meteo-quality baseline); **the LFPG window story** (failed the richer
features on the 1.5-year window, passes on the full 4.4-year window and
the sealed test — a "more data was the fix" finding); and a closing
synthesis on honest magnitude and the non-comparability of the two
methods' raw-GFS baselines. Section 6 (formerly section 5, "Limitations
and open directions") was updated: the richer-features-at-Reno parked item
is marked done with what it showed; the single-shared-test-year
limitation now covers both methods; a new cross-method-comparability
caveat was added; the completed item was removed from the parked list.

**What this session did not do, on purpose.** Did not touch `SPEC.md`. Did
not alter any minimal-method verdict, figure, or finding. Did not
recompute anything — every number in the new section is cited to D48/
F85–F94; the two small derived percentages (the ~+4.8% Reno recomputation)
show their own arithmetic from numbers already on record. Did not run the
archive pass — session 45's job, per this session's own prompt, once
`RESULTS.md` also carries the headline. Nothing was committed.

**Archive step this session:** none — per the session prompt, the archive
pass is session 45's job.

---

## Session 43 (consolidation part 1 — fold the proven 5-feature GRIB method
into SPEC.md; documentation only)

**Folds the now-proven 5-feature GRIB method (F94, 5/5 pass) into
`SPEC.md`, alongside the original minimal method, without disturbing the
minimal method's own text or results. Documentation only — no code, model,
data, or figure touched.** Full account: DECISIONS D49.

**What changed.** A new `## 7. The richer-features GRIB method` section was
added (placed after section 6, so sections 5/6 need no renumbering),
covering motivation, what differs from the minimal method (features, GRIB
source and lead convention, the elevation correction, the v16-only
training window, the unchanged model settings), pre-sealed-test validation,
the lock and sealed test, the F94 results table, and a closing paragraph on
what the result does and does not mean (D48.13) — including that GRIB's
raw-GFS baseline is not the same series as Open-Meteo's, so section 7's
margins are not directly comparable to section 5.0's. Five light pointer/
status edits were made to the existing sections: §1's Reno bullet ("failed"
→ "failed the minimal method (F82); passes the richer method (F94) — see
§7"), §2.1b (a sentence on the GRIB source's own leakage-safety), §3.2 (a
pointer that it describes the minimal method's source only), §5.0 (a
pointer to section 7's own results table), and §6's Reno bullet (a sentence
noting the later richer-method pass). The minimal method's own sections and
results are otherwise untouched.

**What this session did not do, on purpose.** Did not touch `RESULTS.md` —
that is session 44's job. Did not run the archive pass — also session 44,
once both `SPEC.md` and `RESULTS.md` carry the headlines. Did not change
any DECISIONS finding, verdict, or the frozen bar. Did not recompute any
figure — every number in the new section is copied from and cited to D48/
F85–F94. Nothing was committed.

**Archive step this session:** none — per the session prompt, the archive
pass is session 44's job, once RESULTS.md also carries the headline.

---

## Session 42 (the sealed test, clean run — D48's one authorised look,
taken. VERDICT: 5-feature GRIB recipe PASSES at all five airports)

**The verdict, for real this time. Runs the frozen `scripts/
session39_sealed_test.py` once, unchanged, against session 40's
already-pulled sealed-year GRIB feature set and the corrected D48.8
ceiling (session 41, F93). It completed cleanly — no self-guard tripped —
and every one of the five airports PASSES the frozen bar, exactly matching
the D48.12 pre-registration with no exception. Full account: DECISIONS
F94.** Script run: `scripts/session39_sealed_test.py` (confirmed unchanged
since the F93 commit, `git diff HEAD` empty, before and after running).
Full real output: `notes/session40-sealed-test-output.txt` (the file name
is the frozen script's own; this is session 42's real, complete run).
Summary table: `data/processed/session40_sealed_test_summary.csv`.

**Task 1 — sealed-year MAE, four rungs, all five airports:**

```
airport  Raw GFS (GRIB)  Persistence  3-feature  5-feature  n
EGLC          1.254          2.096       1.037       1.000    364
LFPG          1.382          2.300       1.177       1.156    364
DSM           1.733          4.003       1.694       1.636    365
YSDU          1.317          2.669       1.283       1.179    356
RNO           1.512          2.490       1.455       1.346    365
```

**D48.11 bar: 5 of 5 airports PASS** — 5-feature beats both raw GFS (GRIB)
and persistence at every airport, with the narrowest raw-GFS margin at DSM
(+5.6%) and the narrowest persistence margin at RNO (+45.9%). **This is
the project's first result where every opened airport passes under one
recipe** — including LFPG and RNO, whose results under the *existing*
3-feature/Open-Meteo recipe were, respectively, a pass that never showed a
clean multi-window win (F30, contrast F87's own 1.5-year diagnostic where
LFPG lost) and an outright sealed-test failure (RNO, F82). **5-feature
also beats 3-feature at all five airports** (EGLC +3.5%, LFPG +1.8%, DSM
+3.4%, YSDU +8.2%, RNO +7.5%).

**Task 2 — scoring-consistency check: one real, minor, verdict-irrelevant
finding.** The frozen script compares `f5_mae` (all `test_rows`) against
`persist_mae` (the narrower `common_persist` subset, days with a usable
previous-day observation) — a day-set mismatch wherever `no_prev > 0`
(EGLC 1 day, LFPG 1 day, YSDU 9 days; DSM and RNO have none). A read-only
diagnostic (`scripts/session42_scoring_check.py`, importing the frozen
script unmodified, same pattern as session 41's verifier) recomputed
5-feature MAE restricted to exactly the common-persist day set and
compared both bases directly: **all five airports give the identical PASS
verdict under both day bases** — the largest shift is YSDU's, 1.179 to
1.165 on 9 of 356 days, nowhere near closing a 55.8%-skill margin. Full
output: `notes/session-42-scoring-check-output.txt`.

**Task 3 — comparison against D48.12's pre-registration: exact match, no
divergence, at every airport.** All four pre-registered predictions came
true with no exception: 5-feature beats both raw GFS and persistence
everywhere; 5-feature beats 3-feature everywhere; LFPG passes; RNO passes
(a reversal of RNO's *existing* recipe's sealed-test failure, F82 — a
separate finding about a different, richer recipe on a different data
source, not an erasure of F82, per D48.13).

**What this does not change.** Per D48.13, this new recipe's results do
not re-open, re-test, or overwrite any airport's existing sealed-test
verdict under the existing 3-feature/Open-Meteo recipe — EGLC F16, LFPG
F30, DSM F47, YSDU F64 and RNO F82 all stand exactly as before. Whether/how
to fold the 5-feature GRIB recipe into `SPEC.md`/`RESULTS.md` is a later,
separate consolidation session's decision — not made here.

**What this session did not do, on purpose.** Did not modify
`scripts/session39_sealed_test.py` at all (confirmed by `git diff`, empty,
both before and after running it). Did not re-run, re-tune, or adjust
anything after seeing the results. Did not pull any new data — reused
session 40's sealed feature file and the existing sealed-year IEM chunks,
read-only. Did not touch any date outside the training/sealed windows —
enforced by the frozen script's own assertions, none of which raised. Did
not modify `SPEC.md` or `RESULTS.md`. Did not re-open or adjust any
existing airport's sealed-test verdict. Nothing was committed. Scripts:
`scripts/session39_sealed_test.py` (unmodified, run as-is),
`scripts/session42_scoring_check.py` (new, read-only diagnostic).

**Archive step this session:** none taken — F89/F90/F91 (the GRIB build's
own evidence base) and D48/F92/F93 (the lock and the guard correction)
all stay live until the consolidation session folds this recipe's proven
result into `SPEC.md`/`RESULTS.md`; this session's own new finding, F94,
is obviously live. Nothing else in `DECISIONS.md` became newly settled
this session.

---

## Session 41 (verify the F92 "EXCEEDS" days, then correct the D48.8 guard
— no model fit, sealed test still not run)

**Verifies the three airports (EGLC, LFPG, YSDU) that tripped session 40's
D48.8 self-guard, and sanity-checks the two exact matches (DSM, RNO).
Verdict: BENIGN — but the true mechanism is more precise than session 40's
own hypothesis. No model was fit and no sealed-year MAE, skill, or verdict
was computed anywhere this session.** Full account: DECISIONS F93. Script:
`scripts/session41_verify.py` (a read-only diagnostic, imports session
39's frozen script as an unmodified library). Full real output:
`notes/session-41-verify-output.txt`.

**What was actually found.** Session 40 (F92) guessed the GRIB sealed-year
pull might simply have a cleaner forecast-side record than Open-Meteo's
own series. This session rebuilt Open-Meteo's sealed-year forecast series
directly from the real archive files and found that guess is **false**:
Open-Meteo's own coverage is 365 of 365, zero gaps, at every airport — as
clean as GRIB's. **The real cause: the D48.8 ceiling compared two
different stages of the same pipeline.** Every prior airport's own sealed
test computes row counts in two stages — stage A (plain forecast+
observation join) and stage B (stage A further narrowed to days where
YESTERDAY's observation is also available, because persistence needs a
past value). The old `PRIOR_SCORED_DAYS` ceiling held stage-B numbers
(363/363/365/347/365, from F16/F30/F47/F64/F82's own "days every method is
scored on" figure), but the new recipe's `join_rows()` — the function the
guard actually checks — only performs stage A. Comparing a stage-A count
against a stage-B ceiling is what produced the apparent "EXCEEDS" — not
any GRIB-vs-Open-Meteo coverage difference. This session independently
rebuilt both stages, from raw data, at every airport: both reconcile
**exactly** (5 of 5 airports, stage A matches the new recipe's own count,
stage B matches the old ceiling). Every one of the 11 individual "extra"
days (EGLC 1, LFPG 1, YSDU 9) was checked and is a genuine, correctly
paired GRIB+observation row, with Open-Meteo's own forecast for that exact
date also present and non-null (directly refuting the forecast-side-gap
guess) and yesterday's observation confirmed missing (the real, verified
reason). No pairing bug, no double-count, no mis-dated row, at any
airport.

**The D48.8 guard is corrected — a guard-only change.** In
`scripts/session39_sealed_test.py`, `PRIOR_SCORED_DAYS` (old recipe
stage-B figures) is replaced with `SEALED_ROW_CEILING` (this session's own
verified stage-A, GRIB+obs availability figures: **EGLC 364, LFPG 364, DSM
365, YSDU 356, RNO 365**). Features, model settings, training window,
elevation constants (D48.3), the bar (D48.11), and every other self-guard
are unchanged — confirmed by `git diff` and reported in full in DECISIONS
F93. The script still parses and imports cleanly after the edit
(`py_compile` + a clean import, `main()` not invoked).

**What this session did not do, on purpose.** Did not fit any model or
compute any sealed-year MAE/skill/verdict anywhere. Did not touch the
features, model settings, training window, elevation constants, or the
bar — only the D48.8 ceiling values and the block that reads them. Did not
pull any new data — reused session 40's already-decoded sealed feature
file and the existing sealed-year observation/forecast files, all
read-only. Did not take D48's authorised look (D48.13) — that is session
42's job now, against the corrected ceiling. `SPEC.md`/`RESULTS.md` not
modified. Nothing was committed.

**Archive step this session: none.** The sealed test is still open and
unresolved (session 42's job); D48, F91, F92 and this session's own F93
all remain live — F93 documents a correction to a guard session 42 is
about to exercise, and stays needed word-for-word until that session runs.

---

## Session 40 (GRIB build sub-project, step 4b of 4 attempted — the sealed
pull and decode completed cleanly, but the frozen script's own D48.12
self-guard stopped the run before any model was fit, at any airport)

**Step 4b, attempted. Opens the sealed test year (D48.8) for the 5-feature
GRIB recipe for the first time. Task 1 (pull + decode the sealed-year GRIB
feature set) completed cleanly at all five airports. Task 3 (run the
frozen `scripts/session39_sealed_test.py` exactly as written) tripped its
own D48.12 self-guard at the first airport it reaches, EGLC, before
fitting any model — and, per the session prompt's explicit instruction,
was NOT worked around.** No sealed-year MAE was computed and no PASS/FAIL
verdict was reached, at EGLC or any other airport. Full account: DECISIONS
F92.

**Task 1 — the sealed-year GRIB pull and decode: complete, clean, zero
drops anywhere.** `scripts/session40_grib_pull.py` (mirroring
`scripts/session37_grib_pull.py` exactly, restricted to
2025-08-01..2026-07-31) fetched all 5,840 targeted messages (1,460 distinct
run_date/cycle/lead files x 4 variables) cleanly in one pass, zero
failures, 3.5 minutes, ~4.62 GiB. `scripts/session40_decode.py` (mirroring
`scripts/session37_decode.py`'s Task 4 assembly, applying the five FROZEN
D48.3 elevation constants unchanged, not refit) decoded **365 of 365 window
days at every one of the five airports, zero drops** — cleaner than the
training window's own 3-drop record (F90). Output:
`data/processed/grib_features_sealed_window.csv` (1,825 rows). Task 2
(sealed-year observations) needed no new pull: the existing IEM chunks for
2025-08-01..2026-07-31, already on disk from each airport's own completed
3-feature/Open-Meteo sealed test, were reused unchanged.

**Task 3 — the frozen script's own D48.12 stop signal tripped, at EGLC,
before any model was fit.** EGLC's sealed-year row count (364) exceeded the
D48.8 ceiling (363, the existing-recipe's own published scored-day count),
and the script raised rather than proceeding — exactly as D48.12 designed
it to. A read-only diagnostic (reusing the frozen script's own functions
as an unmodified library, no guard bypassed, no model fit) checked all five
airports at once, to give the owner the full scope in one pass:

```
station   sealed rows kept   D48.8 ceiling   status
EGLC            364               363        EXCEEDS
LFPG            364               363        EXCEEDS
DSM             365               365        within bound (exact match)
YSDU            356               347        EXCEEDS
RNO             365               365        within bound (exact match)
```

**Three of five airports (EGLC, LFPG, YSDU) exceed their own ceiling; DSM
and RNO land exactly on it.** A hypothesis, not verified further this
session (F92): the GRIB sealed-year pull had zero missing days at every
airport, a cleaner forecast-side record than the existing Open-Meteo
recipe's own sealed test apparently had at three of the five — a direction
of difference the D48.8 ceiling rule's own reasoning did not anticipate
(it assumed a new source could only match or lose ground, never gain).

**What this leaves standing.** D48's one authorised look (D48.13) has not
been taken at any airport — the year was opened but the script never
reached model-fitting anywhere, so there is no MAE, no PASS/FAIL, and
nothing yet to compare against D48.12's pre-registered expectations.
Nothing about any earlier result changes — EGLC F16, LFPG F30, DSM F47,
YSDU F64 and RNO F82 all stand exactly as reported.

**Flagged for the owner, not decided this session.** How to proceed: (a)
decide the D48.8 ceiling rule itself was too strict as written and revise
it in a new, written DECISIONS entry before re-opening the sealed year
under a corrected rule; (b) trace the specific dates behind the divergence
before trusting either recipe's coverage; or (c) another path the owner
sees that this session does not. D48.13's "one look, and it stands" means
the sealed year should not simply be re-opened under today's unmodified
ceiling rule expecting a different result — the rule, not the data, needs
a decision first.

**What this session did not do, on purpose.** Did not modify
`scripts/session39_sealed_test.py` or any part of the D48 recipe (features,
model, window, elevation constants, or the D48.8 ceiling rule itself). Did
not work around, retry, or patch the tripped self-guard. Did not fit any
model or compute any sealed-year MAE, at any airport. Did not touch any
date outside 2025-08-01..2026-07-31 for the sealed pull (asserted in both
new scripts before use). Did not commit the raw sealed-year GRIB extracts
(gitignored, D47) — only the processed feature file, drop log, and
provenance are candidates for commit. `SPEC.md`/`RESULTS.md` not modified.
Nothing was committed. Scripts: `scripts/session40_grib_pull.py`,
`scripts/session40_decode.py`. Full real output:
`notes/session-40-pull-output.txt`, `notes/session-40-decode-output.txt`,
`notes/session40-sealed-test-output.txt` (partial, through the point of the
stop).

**Archive step this session:** none. D48 and F89–F91 all remain live —
the sealed test they feed into is still open and unresolved, not settled
by this session.

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

**Session 54 (this file's own latest entry, above) ran the staged E3
(pressure/synoptic) experiment — a reading, not a verdict (DECISIONS
F101).** Four feature variants (B, B+T, B+Tv, B+v) were fit on the three
non-reserved `EXPERIMENT_FOLDS` (D51) at all five airports, mirroring
sessions 50/52's own E1/E2 shape exactly; both sanity checks (the tendency
arithmetic, checked on every one of 7,952 rows; the reserved-year guard,
on every fold) PASS; the reserved 2024-25 year was never read. Headline:
`pressure_tendency_3h_hpa` alone (B+T) is the family's own best variant
grand-overall (+0.9% skill vs the refit baseline) — unlike E1 and E2,
adding the raw fields on top (B+Tv, +0.7%) does not add further skill, and
this is by far the smallest maximum grand-overall skill of the three
families explored so far (E1 +2.0%, E2 +4.1%). DSM is, uniquely among the
three families, the one airport where adding the raw fields on top of the
derived feature makes things worse rather than better. RNO shows no
below-ground-style anomaly (PRMSL is sea-level-normalised) and instead
posts the family's single strongest fold-averaged result (B+Tv +2.2%).
The whole family reverses to negative, across every added-feature variant,
in the most recent (2025-26) fold specifically — flagged as fold-quality,
consistent with F96/D52/D53. No pass/fail verdict was computed; the E3
family call is for review next session.

**Session 53, the session before, recorded the E2 family
verdict (DECISIONS D53) and built the E3 (pressure/synoptic) feature set —
data build only.** `dewpoint_depression_t2m_floored` is adopted into the
eventual combine-phase sweep baseline; the three raw moisture fields are
not, though `relative_humidity_2m` specifically is parked as the strongest
combine-phase candidate. E3's own build (PRMSL and PRES:surface at each
airport's own lead, plus PRMSL at lead-3 to derive a same-run 3-hour
pressure tendency) is complete and validated: 0 pull failures across
19,083 messages, 0 join drops, 0 blanks, the tendency derivation checked
exact on every one of 7,952 rows, and RNO's own elevation signature
confirmed exactly where physically expected (its mean surface pressure the
lowest of the five airports). No model was fit; the reserved 2024-25 year
was never touched.

**Session 52, the session before, ran the staged E2
(moisture) experiment — a reading, not a verdict (DECISIONS F100).** Four
feature variants (B, B+D, B+Dv, B+v) were fit on the three non-reserved
`EXPERIMENT_FOLDS` (D51) at all five airports, mirroring session 50/F99's
own E1 shape exactly; all three sanity checks (the reserved-year guard;
the `dewpoint_depression_t2m` reconstruction, checked on every row; the
depression floor, changing exactly 1 of 7,952 rows) PASS; the reserved
2024-25 year was never read. Headline: `dewpoint_depression_t2m_floored`
alone (B+D) already captures nearly all of the family's grand-overall
benefit (+4.0% skill vs the refit baseline, against a +4.1% maximum for
B+Dv) — the same shape E1 showed — but **unlike E1, the raw moisture
fields alone (B+v, +3.8%) trail the derived form by only 0.2 points, not a
clear-weakest-addition gap**. DSM is again the standout and, uniquely
among the five airports, fold-robust (all three per-fold readings
positive and close together). Two airports show a real per-fold split
worth reading directly rather than only fold-averaged: EGLC's B+D benefit
reverses to a loss in the most recent (2025-26) fold, and RNO's is
flat-to-slightly-negative in the thinnest (2022-23) fold. Feature
importances confirm the derived depression and, among the raw fields,
relative humidity specifically, carry real signal at every airport. No
pass/fail verdict was computed; the E2 family call — adopt the derived
depression, add the raw fields too, or neither — is for review next
session.

**Session 51, the session before, recorded the E1 family
verdict and built the E2 (moisture) feature set — data build only.**
DECISIONS D52: `lapse_rate_t2_t850` is adopted into the eventual
combine-phase sweep baseline; the raw pressure-level temperatures
(`t850`/`t925`/`t700`) are not, though RNO's own real raw-level skill
increment is parked as a combine-phase candidate. This is provisional
until the reserved-year finish-line check (D51). E2's own build (RH, DPT,
SPFH at 2 m, plus `dewpoint_depression_t2m`) is complete and validated: 0
pull failures across 19,083 messages, 0 join drops, 0 blanks, one isolated
saturation-boundary physical-sanity finding (DSM, single row), and a
Magnus internal-consistency check and an Open-Meteo cross-check both
passing at four airports with a real but modest, RNO-consistent gap at the
fifth. No model was fit; the reserved 2024-25 year was never touched.

Session 50, the session before that, ran the staged E1 upper-air experiment — a
reading, not a verdict (DECISIONS F99). Four
feature variants (B, B+L, B+Lv, B+v) were fit on the three non-reserved
`EXPERIMENT_FOLDS` (D51) at all five airports; both sanity checks (the
`t2m_raw` derivation, checked on every row; the reserved-year guard, on
every fold) PASS; the reserved 2024-25 year was never read. Headline:
`lapse_rate_t2_t850` alone (B+L) already captures nearly all of the
family's grand-overall benefit (+1.9% skill vs the refit baseline); adding
the raw levels on top (B+Lv) adds almost nothing further (+2.0%); the raw
levels without the derived form (B+v) are clearly the weakest addition
(+1.0%) at every airport but RNO. DSM (F96's own diagnostic) shows a real
positive signal from upper-air, unlike cloud/wind's marginal read there.
RNO behaved exactly as pre-registered — the derived lapse-rate feature is
flat there (+0.0%) — but with a genuine twist: the raw pressure-level
temperatures still carry real skill at RNO (B+v +2.0%, RNO's own best
variant) even though the specific derived difference does not. No pass/
fail verdict was computed; the family call — keep lapse rate, add the raw
levels too, or neither — is for review.

**Session 49, the session before, built and validated the E1
(upper-air/vertical-structure) feature set — TMP at 925/850/700 hPa,
plus a derived lapse-rate feature — for every date the existing 5-feature
GRIB dataset already carries outside the reserved 2024-25 confirmation year
(DECISIONS D51, F98). Data build only: 0 pull failures across 19,083
messages, 0 join drops at any airport, and the reserved year was never
loaded, pulled, or joined. One real, reportable data-character finding
surfaced there (not a decode failure): at RNO, and only at RNO, mean
temperature does not fall monotonically with height across 925/850/700
hPa, plausibly because Reno's own 1,345 m elevation sits at or above the
standard-atmosphere altitude of those pressure surfaces — this session
(50, above) confirmed the predicted effect directly: RNO's own derived
lapse-rate feature is flat, exactly as expected.**

**Stage 2 (individual airports, SPEC section 6) is complete for the five
airports opened so far under the EXISTING 3-feature/Open-Meteo recipe —
four pass, one fails; none of that changed this session (D48.13).
The GRIB-build sub-project (docs/session-36.md through docs/session-42.md)
has now run its full four-step build and its one authorised look: step 1
confirmed the back-extent and validated the GRIB→point pipeline; step 2
fixed RNO's pipeline gap, pulled the full v16-only feature set, and
validated cloud/wind; step 3 diagnosed the cloud tail, joined the GRIB
features to observations, and re-ran the richer-features blocked CV on
the full ~4.4-year window; step 4a locked the 5-feature recipe in full
(DECISIONS D48) and froze the sealed-test script; step 4b's first attempt
(session 40) pulled and decoded the sealed-year GRIB feature set cleanly,
then tripped the frozen script's own D48.12 self-guard before fitting any
model, because three of five airports' sealed-year row counts exceeded
their own D48.8 scored-day ceiling (DECISIONS F92); session 41 verified
those "extra" days are BENIGN — a guard mis-specification, not a data
problem — and corrected the D48.8 ceiling in the frozen script accordingly
(DECISIONS F93). **Session 42 then took D48's one authorised look: the
frozen script ran cleanly, no guard tripped, and the 5-feature GRIB recipe
PASSES the frozen bar at all five airports — EGLC, LFPG, DSM, YSDU and
RNO — exactly matching the D48.12 pre-registration with no exception
(DECISIONS F94).** This is a separate, additional result under a different
recipe (GRIB source, richer features); it does not alter any airport's
existing sealed-test verdict under the existing recipe (D48.13). **Session
43 folded this proven method into `SPEC.md` as a new section 7, documentation
only (DECISIONS D49). Session 44 then rewrote `RESULTS.md` to cover both
methods, also documentation only (DECISIONS F95). Session 45 (this file's
own latest entry, above) then ran the archive pass, moving F85–F93 and D48
to `DECISIONS-archive.md` (DECISIONS D50) — every citation above still
resolves by number, now into the archive for the moved set; F94 stays live,
flagged rather than moved.** The GRIB-build sub-project is now fully
closed — built, tested, folded into SPEC/RESULTS, and archived.

**Session 48 (this file's own latest entry, above) reserved 2024-25 as the
feature-selection programme's untouchable confirmation year and enforced it
in code (DECISIONS D51).** No feature experiment, backtest, or model fit —
setup only. `scripts/session48_reserved_year.py` carries the reservation, a
guard (`assert_reserved_year_excluded()`) that raises on any fold touching
2024-08-01..2025-07-31, and `EXPERIMENT_FOLDS`, the three-fold list (F96's
rolling-origin folds minus 2024-25, with the fold nearest the sealed year
truncated so training never reaches the reserved year either) a future
feature-experiment session should build from. Verified by construction only
— no data loaded, no result computed on any year.

Session 47, the session before, built a feature-family availability map —
radiation, upper-air, moisture, pressure, precipitation — across the GRIB
archive (DECISIONS F97). This is a probe, not an experiment: it decides no
ordering and builds no feature. All 27 candidate variables are present and
decode to real values at both the v16 floor and a recent date; the headline
is that upper-air/vertical structure — the family blocked on Open-Meteo
(F85) and the one the GRIB build was meant to unlock — is confirmed
genuinely available, clean and instantaneous at the forecast lead.
Radiation and precipitation are available but carry a lead-dependent
averaging/accumulation window that differs across airports. This map, and
now session 48's reserved year and guard, is what future feature-experiment
planning works from.

Session 46, the session before, opened a different next phase: a multi-year
rolling-origin generalisation backtest of the existing frozen 3-feature and
5-feature GRIB recipes, 24h lead, existing data only (DECISIONS F96). This
is a descriptive profile, not a new sealed test —
it decides no pass/fail and does not touch F94 or F16–F82. Walking the
train/test cutoff forward one year at a time and refitting each frozen
recipe unchanged: **3-feature beats raw GFS (GRIB) at 18 of 20
airport-years and 5-feature at 19 of 20** (the only losses fall in the
single thinnest training fold); **5-feature beats 3-feature at 17 of 20
full-window airport-years** — reliably at EGLC/LFPG/RNO, variably at
YSDU, marginal-to-slightly-negative at DSM (where three features already
capture most of the learnable bias); the `2025-26` fold reproduces F94 to
within 0.0005 degC at every airport, confirming the backtest pipeline is a
correct reproduction of the frozen recipe. The headline read: **RNO's
5-feature skill vs raw GFS is stable across all four independent years
(+10.2% to +11.5%)**, the tightest band of any airport — strong evidence
Reno's richer-features rescue (F94) is a repeatable effect, not a
single-year artifact. A mid-session correction (owner-confirmed) widened
the 5-feature folds beyond the session prompt's own original 2024-01-19
floor, once this session's own data check showed the prompt's stated
reason (F85) does not apply to the GRIB source — see F96 for the full
account. This is now the benchmark future feature-selection work will be
measured against; that work still needs its own fresh, untouched test
year, and is not started by this session.

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

Full per-airport facts live in SPEC 3.4; the full results table is still
SPEC 5.0, complete for all five airports and matching `RESULTS.md`'s own
table — **this table is the minimal 3-feature/Open-Meteo method only,
unchanged by session 42, 43 or 44 (D48.13).** The separate 5-feature GRIB
method's own sealed-test result (session 42, DECISIONS F94: PASS at all
five airports) has its own results table in **SPEC section 7**, folded
in by session 43 (DECISIONS D49), and is now also folded into `RESULTS.md`
as its own "act two" section by session 44 (DECISIONS F95). Summary
(minimal method):

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
- **Session 40: GRIB build step 4b attempted -- sealed pull/decode clean,
  frozen script self-guard stopped the run before any model was fit.** The
  sealed-year GRIB feature set was pulled and decoded cleanly at all five
  airports (5,840/5,840 messages, 0 pull failures; 365/365 days decoded per
  airport, 0 drops). Running `scripts/session39_sealed_test.py` unchanged
  tripped its own D48.12 stop signal at the first airport, EGLC (sealed-year
  row count 364 exceeds the D48.8 ceiling of 363); a read-only diagnostic
  found the same condition at LFPG (364 vs 363) and YSDU (356 vs 347), with
  DSM and RNO landing exactly on their own ceiling (365 = 365). Per the
  session's own instruction, this was not worked around. No model was fit
  and no sealed-year MAE was computed at any airport -- D48's one
  authorised look has not been taken anywhere (DECISIONS F92). Nothing
  about any earlier airport result changed. `SPEC.md`/`RESULTS.md` not
  modified. Nothing was committed.
- **Session 41: verified session 40's "EXCEEDS" days are BENIGN and
  corrected the D48.8 guard -- no model fit, sealed test still not run.**
  Independently rebuilt Open-Meteo's own sealed-year forecast series from
  the real archive files and found it, too, is 365/365 present at every
  airport -- refuting session 40's own "GRIB is cleaner" hypothesis. The
  real cause: D48.8's ceiling compared the new recipe's pre-persistence
  row count against the old recipe's post-persistence "scored day" count
  -- two different stages of the same pipeline, both independently
  rebuilt and reconciled exactly (5 of 5 airports) this session. Every one
  of the 11 individual extra days (EGLC 1, LFPG 1, YSDU 9) checked and
  confirmed a genuine, correctly-paired row, exactly matching the dates
  already named in each airport's own existing sealed-test notes.
  `scripts/session39_sealed_test.py`'s D48.8 constant was corrected
  (`PRIOR_SCORED_DAYS` -> `SEALED_ROW_CEILING`, values 364/364/365/356/
  365) -- a guard-only change, confirmed by diff to touch nothing else
  (features, model, window, elevation constants, bar, other guards all
  unchanged) and made with no model fit and no sealed-year result seen
  (DECISIONS F93). `SPEC.md`/`RESULTS.md` not modified. Nothing was
  committed.
- **Session 42: the sealed test, clean run -- D48's one authorised look,
  taken.** The frozen `scripts/session39_sealed_test.py` (confirmed
  unchanged since the F93 commit) was run once, unchanged, against
  session 40's already-pulled sealed-year GRIB feature set: no self-guard
  tripped, no error. **Verdict (DECISIONS F94): the 5-feature GRIB recipe
  PASSES the frozen bar at all five airports** -- EGLC (+20.2% skill vs
  raw GFS), LFPG (+16.4%), DSM (+5.6%), YSDU (+10.5%), RNO (+11.0%) --
  and beats persistence by 45.9-59.1% everywhere; 5-feature beats
  3-feature at all five airports too (+1.8% to +8.2%). This is the
  project's first result where every opened airport passes under one
  recipe, and it matches the D48.12 pre-registration exactly, with no
  divergence at any airport. A read-only scoring-consistency check
  (`scripts/session42_scoring_check.py`) confirmed a real but
  verdict-irrelevant day-set mismatch in the frozen script's own
  5-vs-persistence comparison at three airports (EGLC, LFPG, YSDU) --
  recomputed on a fair, apples-to-apples day basis, all five verdicts are
  unchanged. Per D48.13, this is a separate, additional result under a
  different recipe and does not alter any airport's existing sealed-test
  verdict (EGLC F16, LFPG F30, DSM F47, YSDU F64, RNO F82 all stand
  exactly as before). `SPEC.md`/`RESULTS.md` not modified -- folding this
  recipe in is a later consolidation session's job. Nothing was
  committed.
- **Session 43: consolidation part 1 -- folded the proven 5-feature GRIB
  method into `SPEC.md` as a new section 7, documentation only.**
  Sections 1-6 (the minimal method) were preserved untouched except for
  five pointed edits: §1's Reno bullet reworded ("failed" -> "failed the
  minimal method (F82); passes the richer method (F94) -- see §7"), §2.1b
  (a sentence on the GRIB source's own leakage-safety), §3.2 (a pointer
  that it describes the minimal method's source only), §5.0 (a pointer to
  §7's own results table), and §6's Reno bullet (a sentence noting the
  later richer-method pass). The new §7 covers motivation, what differs
  from the minimal method, pre-sealed-test validation, the lock and sealed
  test, the F94 results table, and what the result does and does not mean
  (D48.13) -- placed after §6 (not as a mid-document "4A") so §5/§6's
  existing numbering never shifts. Every figure is copied from and cited to its
  DECISIONS source (D48, F85-F94); nothing was recomputed. `RESULTS.md` not
  touched (session 44's job). Recorded as DECISIONS D49. Nothing was
  committed.
- **Session 44: consolidation part 2 -- rewrote `RESULTS.md` to cover both
  methods, documentation only.** The minimal method's own sections
  (method, five-airport results table, six findings) were preserved
  substantially intact, with three forward pointers added to the new
  section. A new section 5, "Act two: the richer-features GRIB method,"
  covers what differs from the minimal method, pre-sealed-test validation,
  the lock and sealed test with the F94 results table in full, the honest
  Reno decomposition (leads with the 5-vs-3 margin, +7.5%, states the
  GRIB-raw-baseline caveat plainly, and shows the pass is robust to it),
  the LFPG window story ("more data was the fix"), and a synthesis on
  honest magnitude and cross-method baseline non-comparability. The former
  section 5 ("Limitations and open directions") became section 6, updated
  to mark the richer-features-at-Reno item done and add a
  cross-method-comparability caveat. Every figure is copied from and cited
  to its DECISIONS/SPEC source; nothing was recomputed. `SPEC.md` not
  touched. Recorded as DECISIONS F95. Nothing was committed.
- **Session 45: the archive pass, plus one RESULTS.md wording fix,
  documentation only.** Fixed a mis-paired LFPG figure in RESULTS §5.5
  (DECISIONS D50). Applied the D46 criterion to every build-era DECISIONS
  entry and moved F85, F86, F87, F89, F90, F91, F92, F93 and D48 to
  `DECISIONS-archive.md` (1,797 lines, byte-exact) under a new "Moved by
  session 45" section; D47 (a standing rule) was split out of the same
  entry F90 sat in and kept live; D49 and F95 stay live as fresh
  consolidation records; F94 meets the same criterion but was flagged for
  the owner rather than moved, since it is the very fresh headline result.
  `DECISIONS.md` falls from 2,359 to 636 live lines. This closes the
  GRIB-build sub-project (docs/session-36.md through docs/session-45.md)
  for good. Nothing was committed.
- **Session 46: multi-year rolling-origin generalisation backtest of the
  existing frozen recipes, 24h lead, GRIB source (DECISIONS F96).** A
  descriptive profile, not a new sealed test. 3-feature beats raw GFS
  (GRIB) at 18 of 20 airport-years, 5-feature at 19 of 20; 5-feature beats
  3-feature at 17 of 20 full-window airport-years. RNO's 5-feature skill is
  stable across all four years (+10.2% to +11.5%), the strongest evidence
  yet its richer-features rescue (F94) is repeatable. The `2025-26` fold
  reproduces F94 to within 0.0005 degC at every airport. Now the benchmark
  future feature work is measured against. Nothing was committed.
- **Session 47: feature-family availability probe — radiation, upper-air,
  moisture, pressure, precipitation (DECISIONS F97).** A map, not an
  experiment. All 27 candidate variables present and decode cleanly at both
  the v16 floor and a recent date; upper-air/vertical structure (the family
  blocked on Open-Meteo, F85) confirmed genuinely unlocked with no caveat;
  radiation and precipitation available but carry a lead-dependent
  averaging/accumulation window. Nothing was committed.
- **Session 48: reserved 2024-25 as the feature-selection programme's
  confirmation year, enforced in code (DECISIONS D51).** Setup only — no
  feature experiment run, no model fit, no result computed on 2024-25 or
  any other year. `scripts/session48_reserved_year.py` (new) carries the
  reservation, a guard that raises on any fold touching the reserved year,
  and the three-fold `EXPERIMENT_FOLDS` list a future feature-experiment
  session should build from. Verified by construction only. Nothing was
  committed.
- **Session 49: built and validated the E1 upper-air/vertical-structure
  feature set — data build only, no model fit (DECISIONS F98).** Pulled
  TMP at 925/850/700 hPa for every date the existing 5-feature dataset
  carries outside the reserved 2024-25 year (D51), derived `t2m_raw` and
  `lapse_rate_t2_t850` without any new 2 m-temperature pull, and joined
  the result onto the existing dataset with 0 messages failed (of 19,083)
  and 0 join drops at any airport. No raw GRIB2 bytes were kept on disk
  (a disk-space-forced design choice, not the session prompt's own
  requirement) — a per-request manifest stands in as the provenance
  record instead. Flagged a real, unfixed anomaly: RNO's own mean
  temperature does not fall monotonically with height across
  925/850/700 hPa, plausibly a below-ground-extrapolation effect of
  Reno's 1,345 m elevation relative to those pressure surfaces' own
  standard-atmosphere altitudes. Reserved year never touched. Nothing was
  committed.
- **Session 50: the staged E1 upper-air experiment — a reading, not a
  verdict (DECISIONS F99).** Fit four feature variants (B, B+L, B+Lv, B+v)
  on the three non-reserved `EXPERIMENT_FOLDS` (D51), all five airports.
  Both sanity checks passed (the `t2m_raw` derivation, checked on every row
  of 7,952; the reserved-year guard, on every fold). `lapse_rate_t2_t850`
  alone (B+L) captures nearly all of the family's grand-overall skill
  (+1.9%); the raw levels add almost nothing further on top of it (+2.0%
  for B+Lv) and are clearly weakest alone (+1.0% for B+v) at every airport
  but RNO. DSM shows a real positive upper-air signal (unlike cloud/wind's
  marginal read there, F96); RNO's derived lapse-rate feature is flat
  (+0.0%, exactly as pre-registered, F98) but the raw levels alone still
  carry real skill there (+2.0%, RNO's own best variant). No pass/fail
  verdict computed — the family call is for review. Reserved year never
  touched. Nothing was committed.
- **Session 51: recorded the E1 family verdict (DECISIONS D52) and built
  the E2 moisture feature set — data build only.** `lapse_rate_t2_t850` is
  adopted into the eventual combine-phase sweep baseline; the raw
  pressure-level temperatures are not, though RNO's own raw-level skill
  increment is parked as a combine-phase candidate — provisional until the
  reserved-year finish-line check. The E2 build (RH, DPT, SPFH at 2 m,
  plus `dewpoint_depression_t2m`) pulled cleanly (0 of 19,083 messages
  failed, 0 join drops, 0 blanks) and validated cleanly except one isolated
  saturation-boundary row at DSM, reported not fixed. A Magnus
  internal-consistency check and a new small Open-Meteo cross-check pull
  (non-reserved overlap only) both agree closely at four airports, with a
  real but modest, RNO-consistent gap at the fifth. No model fit. Reserved
  year never touched. Nothing was committed.
- **Session 52: ran the staged E2 (moisture) experiment (DECISIONS F100) —
  a reading, not a verdict.** Fit four feature variants (B, B+D, B+Dv, B+v)
  on the three non-reserved `EXPERIMENT_FOLDS` (D51), all five airports,
  mirroring session 50/F99's own E1 shape. All three sanity checks passed
  (reserved-year guard; the depression reconstruction, checked on every row
  of 7,952; the depression floor, changing exactly 1 row). Grand-overall:
  `dewpoint_depression_t2m_floored` alone (B+D) captures +4.0% of the +4.1%
  maximum (B+Dv); unlike E1, the raw fields alone (B+v, +3.8%) trail the
  derived form by only 0.2 points, not a clear-weakest gap. DSM is the
  strongest and only fold-robust airport; EGLC's benefit reverses in the
  most recent fold and RNO's is flat in the thinnest fold — both reported
  explicitly, not hidden in the fold average. No pass/fail verdict
  computed — the family call is for review. Reserved year never touched.
  Nothing was committed.
- **Session 53: recorded the E2 family verdict (DECISIONS D53) and built
  the E3 pressure/synoptic feature set — data build only.**
  `dewpoint_depression_t2m_floored` adopted into the eventual combine-phase
  sweep baseline; the raw moisture fields are not, though relative
  humidity is parked as the strongest combine-phase candidate. The E3
  build (PRMSL, PRES:surface, plus a same-run 3-hour PRMSL tendency at
  lead-3) pulled cleanly (0 of 19,083 messages failed, 0 join drops, 0
  blanks) and validated cleanly — RNO's own mean surface pressure
  confirmed the lowest of the five airports, as elevation predicts; the
  Open-Meteo cross-check agrees closely at four airports with a real,
  RNO-consistent larger gap at the fifth. No model fit. Reserved year
  never touched. Nothing was committed.
- **Session 54: ran the staged E3 (pressure/synoptic) experiment
  (DECISIONS F101) — a reading, not a verdict.** Fit four feature variants
  (B, B+T, B+Tv, B+v) on the three non-reserved `EXPERIMENT_FOLDS` (D51),
  all five airports, mirroring session 50/52's own E1/E2 shape. Both
  sanity checks passed (tendency arithmetic, checked on every row of
  7,952; the reserved-year guard, on every fold). `pressure_tendency_3h_
  hpa` alone (B+T) is the family's own best variant grand-overall (+0.9%),
  unlike E1/E2 where adding raw fields on top of the derived feature never
  hurt — here it does (B+Tv +0.7%); the raw fields alone are flat (B+v,
  -0.0%). By far the smallest maximum grand-overall skill of the three
  families so far. DSM is the one airport where the raw-plus-derived
  combination underperforms the derived feature alone. RNO shows no
  below-ground-style anomaly (PRMSL is sea-level-normalised) and instead
  posts the family's single strongest fold-averaged result. The whole
  family reverses to negative in the most recent (2025-26) fold across
  every variant — reported as fold-quality, not family weakness. No
  pass/fail verdict computed — the family call is for review. Reserved
  year never touched. Nothing was committed.

## Next

**Next planning session: session 55 — the owner records the E3 family
verdict (DECISIONS D54, from review of session 54's own F101 grid), then
the session builds and validates the E4 (radiation) feature set.** E4's
own known awkwardness (F97): the averaging window is lead-dependent — a
genuine 6-hour average at EGLC/LFPG/DSM (lead 24) but only a 2-hour
average at YSDU/RNO (lead 26) — and must be normalised to a same-meaning
feature across airports before it can be used as a model input; that
normalisation choice is session 55's own job, not decided here.

**The E3 (pressure/synoptic) experiment is now run (DECISIONS F101, this
file's own latest entry, above) — a reading, not a verdict.** Four
variants (`B`, `B+T`, `B+Tv`, `B+v`) were fit on the three non-reserved
`EXPERIMENT_FOLDS` at all five airports; both sanity checks (the tendency
arithmetic, checked on every one of 7,952 rows; the reserved-year guard,
on every fold) PASS. Headline: `pressure_tendency_3h_hpa` alone (B+T) is
the family's own best variant grand-overall (+0.9%) — unlike E1 (F99) and
E2 (F100), where adding the raw fields on top of the derived feature never
hurt, here it does (B+Tv, +0.7%); the raw fields alone are flat (B+v,
-0.0%). This is by far the smallest maximum grand-overall skill of the
three families explored so far (E1 +2.0%, E2 +4.1%, E3 +0.9%). DSM is the
one airport, uniquely across all three families, where the raw-plus-
derived combination underperforms the derived feature alone. RNO shows no
below-ground-style anomaly — PRMSL is sea-level-normalised, unlike the
upper-air family's extrapolation issue (F98/F99) — and instead posts the
family's single strongest fold-averaged result (B+Tv +2.2%). The whole
family reverses to negative, across every added-feature variant, in the
most recent (2025-26) fold specifically — reported as fold-quality per
F96/D52/D53's own established pattern, not family weakness. No pass/fail
verdict was computed; the family call (adopt the tendency, add the raw
fields too, or neither) is for review, session 55.

**If E3 is adopted into the combine-phase sweep baseline, the E4
(radiation) build follows in the same session, per the session-54 prompt's
own instruction.** F97's own availability map leaves radiation and
precipitation as the two remaining candidate families (moisture, upper-air
and pressure are now all closed out — E1, E2, E3) — both flagged
"available but awkward" for the same lead-dependent-window reason.

The reserved 2024-25 confirmation year (D51) stays untouched until a
single, pre-chosen final feature set is confirmed on it once, at the very
end of the whole feature-selection programme — not before, and not by
session 54's own experiment, session 55's own verdict or E4 build, or any
session before the finish line.

Session 47 built the feature-family availability map (DECISIONS F97) that
feature-experiment planning needs. All five candidate families (radiation,
upper-air, moisture, pressure, precipitation) are confirmed available back
to the v16 floor; upper-air is the clean headline unlock, radiation and
precipitation both need a deliberate choice of which averaging/accumulation
window to use before either can become a feature.

Session 46 (the session before) built the multi-year generalisation
benchmark (DECISIONS F96) that the previous phase's own opening
(docs/session-46.md) called for — a descriptive rolling-origin profile of
the existing frozen GRIB recipes, not a new verdict. It stands as the
benchmark future feature work is measured against. **Feature-selection work
(adding, removing, or trying new features) still needs its own fresh,
untouched test year** — session 46's backtest reused the sealed year
legitimately only because it tuned nothing; a future session that wants to
try a new feature cannot simply read that profile and pick a winner. A
+48h-lead version of that same backtest is a separate, later step (its own
session prompt kept it out of scope, since it needs a fresh pull). Q30's own
remaining branches (below) are otherwise unaffected and still open.

**The GRIB-build sub-project (docs/session-36.md through docs/session-45.md)
is now fully closed.** It completed its full four-step build and its one
authorised look (session 42, DECISIONS F94: 5-feature GRIB recipe PASSES
the frozen bar at all five airports, exactly matching the D48.12
pre-registration); sessions 43-44 folded that proven result into both
`SPEC.md` (new section 7, DECISIONS D49) and `RESULTS.md` (new section 5,
"act two," DECISIONS F95); and session 45 ran the archive pass, moving the
sub-project's own settled evidence base (F85, F86, F87, F89, F90, F91, F92,
F93, D48) to `DECISIONS-archive.md` under a new "Moved by session 45"
section (DECISIONS D50). Per D48.13 ("one look, and it stands"), the F94
result itself is final and unmodifiable -- no re-run, no re-tune, whatever
a later session might wish were different. **F94 stays live in
`DECISIONS.md`, deliberately not archived yet** -- it met the same D46
criterion but was flagged for the owner rather than moved silently, since
it is the headline five-of-five-airports result and very fresh; a future
session may archive it once the owner says so. The minor scoring-basis
note from session 42's Task 2 (a real but verdict-irrelevant day-set
mismatch in the frozen script's own 5-vs-persistence comparison at three
airports, F94) stays on record in DECISIONS; it was never surfaced in
`RESULTS.md` itself, since no session's prompt asked for that.

**What is genuinely next is now Q30's own remaining branches (see "Open
questions" below), unblocked by anything GRIB-build-related.** Nothing in
the sub-project's own scope is outstanding.

**Disk space and repo size, still relevant for a future session.**
Session 37's ~20 GB GRIB pull took free space from 35 GiB to 14 GiB;
session 40's sealed-year pull added a further ~4.62 GiB (5,840 small
files), free space ~13 GiB after that. Sessions 49 and 51 (E1 upper-air
and E2 moisture) each used the fetch-decode-discard pattern instead
(D47's "manifest, not bytes" policy taken one step further, no disposable
local cache kept), so free space was essentially unchanged by either —
session 51 measured 11.30 GiB before its own pull and 11.28 GiB after.
**Session 53 (E3 pressure) used the same pattern but needed two idx
fetches per combo instead of one (the lead file and the lead-3 file), and
free space fell further, from 11.32 GiB before to 9.87 GiB after** — still
no raw bytes retained; the larger drop is attributable to scratch-file
churn during the pull, not a retained cache. SPEC 2.3/D15 (as qualified by
D47 for large re-fetchable sources) means the session-37/40 raw pulls
enter the repository's history once committed; the session-49/51/53 pulls
leave no raw bytes to commit at all, only their manifests -- not decided
here.

**Reno's own EXISTING sealed-test result (under the 3-feature/Open-Meteo
recipe) stands exactly as reported (D44.10, D44.11, F82) -- no re-run, no
retroactive adjustment**, even though the separate, richer GRIB recipe now
passes at Reno too (F94) -- two independent findings about two different
recipes, not one overwriting the other (D48.13). Q30's other branches (a
further airport; a second test year; stage 3, pooling) remain untouched
and are now fully available, since the richer-features branch itself is
resolved (see "Open questions" below).

## Open questions (live)

- **Q30 (its richer-features branch is now RESOLVED by session 42; the
  question itself stays open because its other two branches remain the
  owner's choice).** The owner picked its first branch -- more airports,
  "ramp up difficulty" -- and Reno's own five steps are finished, ending
  in a failure under the existing recipe. The richer-features branch of
  that intent took nine concrete steps and has now reached its answer:
  session 32's scout (DECISIONS F86) found a real but
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
  show a clear positive result; session 39's GRIB build step 4a (D48)
  locked the 5-feature recipe completely and froze the sealed-test script,
  with no sealed data touched; session 40's GRIB build step 4b attempt
  (F92) opened the sealed test year for the first time -- the pull and
  decode completed cleanly at all five airports, but the frozen script's
  own D48.12 self-guard stopped it before any model was fit, because three
  of five airports' sealed-year row counts exceeded their own D48.8
  scored-day ceiling; session 41 (F93) verified those extra days are
  BENIGN -- a guard mis-specification, not a real GRIB-vs-Open-Meteo
  coverage difference -- and corrected the D48.8 guard, again with no
  model fit and no sealed-year result seen; and **session 42 (F94) took
  D48's one authorised look: the 5-feature GRIB recipe PASSES the frozen
  bar at all five airports, exactly matching the D48.12 pre-registration
  with no exception.** The richer-features branch is now answered as far
  as a sealed-test result can answer it, and its documentation follow-up is
  also done -- session 43 folded the proven recipe into `SPEC.md` (D49),
  session 44 folded it into `RESULTS.md` (F95), and session 45 archived
  the sub-project's own settled evidence base (D50) -- the richer-features
  branch, and the GRIB-build sub-project it took nine sessions to run, are
  now fully closed. **Q30's other two branches -- a further
  airport, and a second test year (the remaining half of the F30/F48
  caveat) -- and stage 3 (pooling) remain fully open and are the owner's
  choice**, unaffected by how the richer-features branch resolved.
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
