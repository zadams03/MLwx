# docs/session-57.md — session 57

**Two tasks.** Task 1 records the owner's E4 (radiation) family verdict as a new
DECISIONS entry (D55) — a file append only, no code, no SPEC/RESULTS edit. Task 2
builds and validates the E5 (precipitation) feature set — the LAST family in the
feature-selection programme — as a DATA BUILD ONLY: no model is fit, no MAE/skill/CV
is computed, and the reserved 2024-08-01..2025-07-31 confirmation year (D51) is never
loaded, pulled, or joined at any point.

Read CLAUDE.md + SPEC.md + STATUS.md + live DECISIONS.md in full first, as every
session. SPEC section 2 (critical rules) applies whether or not this prompt repeats it.

---

## Task 1 — append DECISIONS D55 (the E4 verdict). No code.

Append the following entry verbatim to the end of the live `DECISIONS.md`. Do not
edit any other entry, `SPEC.md`, or `RESULTS.md`. Do not fit any model or compute any
number — every figure below is copied from and cited to F103.

---
## 2026-09-20 — Session 57 decision: the E4 (radiation) family verdict, from the owner's review of F103

**D55. Verdict: E4's adopted contribution to the eventual combine-phase sweep
baseline is the single resolved feature `dswrf_2h_wm2` (the `B+R` variant) — the
physically-consistent 2-hour-average downward-shortwave rate F102 built. The two raw
de-accumulation-endpoint columns — `dswrf_ave_to_lead_wm2` and
`dswrf_ave_to_lead_minus2_wm2` — are NOT adopted into the sweep, and — as with E3 —
nothing from this family is parked as a combine-phase candidate either.**

**Why nothing is parked (the point that separates E4 from E1/E2).** E1 parked RNO's
raw pressure LEVELS (D52) and E2 parked relative humidity (D53) because each was a
genuinely SEPARATE physical variable carrying a real, fold-robust standalone signal at
some airport. E4's two raw columns are not a separate variable at all: they are the two
accumulation-window averages that `dswrf_2h_wm2` is itself DERIVED FROM (F103). Adopting
them would add no new physical information — it would only let the model re-do the
de-accumulation the resolved feature already performs, maximally redundant with `R` by
construction. They are also unevenly defined: identical to `dswrf_2h_wm2` at the two
lead-26 airports (YSDU, RNO) by construction, so `B+R`, `B+Rv` and `B+v` are the same
model there (F103). A redundant, unevenly-defined pair is not a portable combine-phase
candidate — so it is dropped, not parked.

**Rationale for the adoption itself, kept plain.** `dswrf_2h_wm2` is a single, clean,
physically-resolved feature — an identical real 2-hour shortwave rate at every airport
(F102) — consistent with the programme's "lead with the resolved form" principle (the
same shape as D52's lapse rate, D53's dew-point depression, D54's pressure tendency). It
carries +1.4% grand-overall skill (F103), of the family's +1.9% maximum (`B+Rv`). The
+0.5pp the raw endpoints add on top rests entirely on the two lead-24 airports EGLC and
LFPG, and — being redundant-by-construction — is read as the model re-deriving the
resolution rather than as new signal. E4 is a mid-strength family (+1.4% adopted, +1.9%
max — above E3's +0.9%, below E1's +2.0% and E2's +4.1%), recorded honestly as such.

**On-record observation for the combine phase (NOT a parked candidate).** At EGLC and
LFPG — the only airports where the raw-vs-resolved contrast is both real and non-flat
(DSM is genuinely tested but reads flat: `B+R` -0.2%, `B+Rv` +0.1%, `B+v` +0.0%;
YSDU/RNO are silent by construction) — the raw endpoints add a little further skill on
top of the resolved rate (EGLC `B+Rv` +5.4% vs `B+R` +3.8%; LFPG `B+Rv` +3.2% vs `B+R`
+2.4%, F103). This is logged as an observation for the combine phase to be aware of, NOT
as a formal parked candidate: it is a fold-AVERAGED read only (no per-fold-per-airport
robustness certification, unlike E1's parked RNO signal), and it is
redundant-by-construction with the adopted feature rather than a separate variable.
Grid: `data/processed/session56_e4_experiment_grid.csv`.

**This is provisional.** Like every family in the sweep, `dswrf_2h_wm2` is confirmed
only when the single final feature set is checked on the reserved year once, at the
finish line (D51) — not now.

**Measurement baseline is unchanged.** E5 and any later work in the sweep are measured
against the frozen 5-feature baseline B, NOT against `B+R` or any other adopted feature.
Adopted features enter only at the combine phase. Cites F103.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`. Did not fit
any model or compute any new figure — every number above is copied from and cited to
F103. Did not touch the reserved 2024-08-01..2025-07-31 confirmation year.

---

## Task 2 — build and validate the E5 (precipitation) feature set. Data build only.

Mirror the shape of `scripts/session55_radiation_pull.py` (the E4 build, F102) — same
date-list construction, same non-reserved spans, same guard, same fetch-decode-discard
pattern, same join-and-validate structure. Write a new `scripts/session57_precip_pull.py`.
Do NOT re-run or modify the session-55 script.

The precipitation family is awkward for two reasons F97 already found: (1) `APCP:surface`
carries a lead-dependent accumulation window, and (2) precipitation is mostly zero
(sparse). Both are settled below before any bulk pull — do not re-decide them.

### Step 0 — window handling and sparsity, resolved before any bulk pull

**The chosen field is APCP's cumulative-since-forecast-start accumulation, turned into a
mean rate.** F97 found `APCP:surface` exposes two accumulation windows at each lead: a
short one (matching the ave-field window — 18-24h at lead 24, 24-26h at lead 26) and a
cumulative-since-forecast-start one ("0-1 day" at lead 24, "0-26 hour" at lead 26 — a
day-vs-hour labelling quirk for the same "since hour 0" idea). **Use the cumulative
since-start message**, divided by its window length in hours, to give one mean
precipitation rate in mm/h. This is deliberately the one-message option — it does NOT
de-accumulate and does NOT fetch a second message per airport-date, unlike the E4
radiation build.

Confirm this directly, freshly (do not reuse F97's own idx files — one of F97's two
sample dates, 2025-06-15, now falls inside the reserved year, D51). Enumerate EVERY idx
line matching `APCP:surface` (not just the first) at each forecast-hour file this session
needs — f024 (the lead-24 airports EGLC/LFPG/DSM) and f026 (the lead-26 airports
YSDU/RNO) — at two sample dates: the v16 floor 2021-03-24 and a recent date outside both
the sealed and the reserved years (use 2024-06-15). For the cumulative message, confirm
its exact bounds by real `eccodes` decode (`startStep`/`endStep`), not just the idx label
text: expect start step 0, end step 24 at f024 and end step 26 at f026, at both dates.
Record what you find in `data/raw/diagnostics/session57/session57_window_resolution.csv`.
If the field is NOT present as expected, STOP and report — do not substitute.

**Window definition, per airport (lead convention SPEC 7.2 / D48.2 / F89 — cycle
floor(HH/6)*6 on day D-1, forecast hour 24 + (HH mod 6)):**
- EGLC, LFPG, DSM (lead 24): cumulative window is forecast hour 0..24, i.e. the 24 hours
  ending at the target valid hour. `precip_window_hours = 24`.
- YSDU, RNO (lead 26): cumulative window is forecast hour 0..26, i.e. the 26 hours
  ending at the target valid hour. `precip_window_hours = 26`.

Then: `apcp_cumulative_mm` = the decoded APCP value (GRIB reports APCP in kg m**-2, which
equals mm of water — confirm units by direct decode, no conversion assumed);
`precip_rate_mmh = apcp_cumulative_mm / precip_window_hours`. Keep both
`apcp_cumulative_mm` and `precip_window_hours` as their own transparency columns
alongside the derived `precip_rate_mmh` (E4's own raw-endpoint-transparency convention).

**A design observation to state plainly in the Step-0 summary (not a defect, a
structural consequence of the one-message choice).** Because `precip_window_hours` is a
CONSTANT per airport (24 or 26), `apcp_cumulative_mm` and `precip_rate_mmh` differ only
by a fixed per-airport scale — they are monotone transforms of each other. LightGBM's
tree splits are invariant to a monotone per-feature transform, so within any single
airport's model the raw total and the mean rate are the SAME feature. E5 therefore
carries effectively ONE precipitation feature; the rate is kept as the headline form for
cross-airport interpretability (a common mm/h scale), and the raw total is kept only for
transparency, not as a separate modelling variant. State this in the output so the
session-58 experiment is planned as a clean B vs B+P, not a raw-vs-resolved grid.

**A real cross-airport inconsistency to flag plainly, not paper over.** Unlike E4's
resolved feature (a physically identical 2-hour window at every airport), this since-start
window is 24h at EGLC/LFPG/DSM but 26h at YSDU/RNO — so `precip_rate_mmh` is a mean over
a 24h span at three airports and a 26h span at two. Rate-normalisation handles the
magnitude/scale, but the span difference is a genuine mild inconsistency. Report it
honestly; do NOT claim E4-level physical consistency, and do NOT use any per-airport
statistical standardisation to hide it.

**Sparsity handling.** Use `precip_rate_mmh` as one continuous feature, with NO transform
(no log1p, no binary wet/dry flag) — LightGBM handles a zero-inflated continuous feature
natively via its splits. A decoded zero is a REAL, kept value (a dry forecast), not
missing data: SPEC 2.2's drop-and-count applies only to a genuinely missing message or an
unpaired observation row, never to a legitimate zero. Report the per-airport
zero-fraction (fraction of rows with `apcp_cumulative_mm == 0`) as a diagnostic in its
own right — descriptively, with NO pre-registered expectation of which airport is driest
(F102's own session prompt carried a wrong "which airport reads low" premise; do not
repeat that shape here).

### Step 1 — guard

Build the date list from the existing 5-feature GRIB dataset's own real rows, exactly as
the session-55 build did: the non-reserved train span 2021-03-24..2024-07-31 and the
sealed span 2025-08-01..2026-07-31 — the reserved 2024-08-01..2025-07-31 year is excluded
at build time and never enters. Clear `assert_reserved_year_excluded()` (from
`scripts/session48_reserved_year.py`) on both spans, and run a defensive per-date scan
confirming 0 reserved-year dates, BEFORE any pull request is made. Report both.

### Step 2 — pull

Fetch ONE APCP cumulative-since-start message per airport-date (no de-accumulation, no
second message). Use the fetch-decode-discard pattern (no raw GRIB2 bytes kept on disk),
as E1-E4 did. Write a manifest to
`data/raw/diagnostics/session57/session57_pull_manifest.csv` with any FAIL rows counted
and reported. Report free disk space before and after.

### Step 3 — join and derive

Join onto the existing 5-feature dataset by the established keys, at every airport, both
spans. Report row counts before and after the join at all five airports; any dropped row
goes to `data/processed/session57_precip_join_drops.csv` with its count reported (SPEC
2.2). Derive `precip_rate_mmh` as in Step 0. Write the two output tables:
`data/processed/session57_v16_window_with_precip.csv` and
`data/processed/session57_sealed_window_with_precip.csv`.

### Step 4 — validate

- Null-free check on `precip_rate_mmh` and `apcp_cumulative_mm` at every airport, both
  spans; report n.
- All values non-negative (precip cannot be negative); report min.
- Per-airport min / mean / max of `precip_rate_mmh` (mm/h) and the per-airport
  zero-fraction, both reported as a plain table — descriptive, no pass/fail.
- Open-Meteo cross-check on `precipitation` over the non-reserved overlap only (the same
  non-reserved windows E2/E3/E4's cross-checks used). EXPECT a large magnitude gap: this
  session's since-start 24-26h mean rate and Open-Meteo's `precipitation` use different
  accumulation conventions, so a big difference is anticipated, not a defect. Report the
  gap and, if cheap, the wet-vs-dry co-occurrence agreement (both > 0 vs both == 0); do
  NOT chase the magnitude.

### End-of-session steps

1. Paste the real output (actual numbers, not descriptions) — save the full run to
   `notes/session-57-precip-output.txt`.
2. Consistency check across CLAUDE + SPEC + STATUS + DECISIONS; report disagreements,
   duplicate headings, out-of-order entries — report only, do not fix.
3. Archive step per the criterion (D55 and the new E5 finding are both brand new and
   live; D51/D52/D53/D54/F96-F103 all remain live inputs to a still-open programme — so
   almost certainly no move this session, but run the check and say so).
4. Overwrite `STATUS.md` and **end it with a "Next planning session" line**: session 58 —
   run the staged E5 (precipitation) experiment on the three non-reserved EXPERIMENT_FOLDS
   (D51), a clean **B vs B+P** (one precipitation feature — see Step 0's monotone-
   equivalence observation), reading per-airport with DSM as the diagnostic and the
   reserved year untouched; then, with E5's verdict recorded, the whole E1-E5 family sweep
   is complete and the combine phase / reserved-year finish line is next.

### Discipline for this session (do not relax)

No model fit; no MAE/skill/CV computed. Reserved 2024-08-01..2025-07-31 year never
loaded, pulled, or joined. Only `APCP:surface` pulled — no other precipitation field
(PRATE/SNOD/WEASD) and no radiation field. No per-airport feature selection — identical
handling at all five airports. No per-airport statistical standardisation. `SPEC.md` and
`RESULTS.md` untouched. Nothing committed — prepare changes, write the suggested commit
message, and stop for review.
