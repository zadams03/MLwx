# Session 55 — record the E3 verdict (D54); build and validate the E4
(radiation) feature set

Read `CLAUDE.md`, `SPEC.md`, `STATUS.md`, and the live `DECISIONS.md` in full
before starting, per CLAUDE.md's own routine. This session has two tasks.
Task 1 is a documentation-only decision entry, no code. Task 2 is a data
build only — no model is fit, no MAE is computed, and the reserved
2024-08-01..2025-07-31 confirmation year (D51) is never loaded, pulled, or
joined at any point.

Task 2 mirrors the session 49/51/53 build-then-experiment shape exactly,
with one extra design step E1–E3 did not need — a lead-dependent averaging
window that must be resolved to a single consistent feature before the field
is usable.

---

## Task 1 — append DECISIONS D54, the E3 (pressure/synoptic) family verdict

Append the following entry to `DECISIONS.md`, verbatim, at the end of the
live file. Do not edit `SPEC.md` or `RESULTS.md`. Do not fit any model or
compute any new figure — every number is already on record in F101.

```
## 2026-09-20 — Session 55 decision: the E3 (pressure/synoptic) family
verdict, from the owner's review of F101

**D54. Verdict: E3's adopted contribution to the eventual combine-phase
sweep baseline is the single derived feature `pressure_tendency_3h_hpa`
(the `B+T` variant). The two raw pressure fields — `pressure_msl_hpa` and
`pressure_surface_hpa` — are NOT adopted into the sweep, and — unlike E1
and E2 — nothing from this family is parked as a combine-phase candidate
either.**

**Why nothing is parked (the point that distinguishes E3 from E1/E2).**
E1 parked RNO's raw pressure LEVELS and E2 parked relative humidity
because each showed a real, fold-ROBUST standalone signal at some airport,
just not one general enough to adopt. E3's raw fields do not clear that
bar: `B+v` (raw fields alone) is flat-to-negative grand-overall (-0.0%)
and negative at three of five airports (F101), and `B+Tv` does not beat
`B+T` grand-overall (+0.7% vs +0.9%) — the first family in the programme
where adding the raw fields on top of the derived feature does not help at
all. The one bright spot — RNO's `B+Tv` at +2.2% fold-averaged — rests
mainly on the 2025-26 fold, which F101 reports went negative for the WHOLE
pressure family across every airport and variant, and which F96/D52/D53
already flag as the least representative of the three folds. A signal
whose only support sits inside the least-trusted fold is read as
fold-noise, not a durable Reno effect worth carrying forward — the
opposite of E1's RNO raw-levels signal, which was positive in all three
folds. So the raw pressure fields are dropped, not parked.

**Rationale for the adoption itself, kept plain.** `pressure_tendency_3h_
hpa` is the family's own best variant grand-overall (+0.9%, F101), and it
is a single derived feature — consistent with the programme's "lead with
the derived form" principle (the same shape as D52's lapse rate and D53's
dew-point depression). E3 is the weakest family so far (+0.9% max, vs E1
+2.0%, E2 +4.1%), so this is a small adopted contribution — recorded
honestly as such, not inflated.

**This is provisional.** Like every family in the sweep, `pressure_
tendency_3h_hpa` is confirmed only when the single final feature set is
checked on the reserved year once, at the finish line (D51) — not now.

**Measurement baseline is unchanged.** E4 and every later family in the
sweep are measured against the frozen 5-feature baseline B, **not** against
`B+T` or any other adopted feature. Adopted features enter only at the
combine phase. Cites F101.

**What this decision did not do.** Did not touch `SPEC.md` or `RESULTS.md`.
Did not fit any model or compute any new figure. Did not touch the
reserved 2024-08-01..2025-07-31 confirmation year.

---
```

---

## Task 2 — build and validate the E4 (radiation) feature set

Mirrors the session 49 (F98) / 51 (E2) / 53 (E3) build shape: a data build
and validation only, no model. The radiation family is the one F97 flagged
as awkward — its GRIB fields are time-AVERAGED over a window that ends at the
forecast hour, and that window's LENGTH differs by airport purely because of
each airport's own target hour: 6 hours at the lead-24 airports (EGLC, LFPG,
DSM) but only 2 hours at the lead-26 airports (YSDU, RNO), per F97. A raw
averaged field therefore means a different physical thing at different
airports, which breaks the project's "identical feature at every airport"
principle (D52/D53). This session's central job is to resolve that into ONE
consistent feature before the field is used.

**Scope of fields.** Lead with **downward shortwave radiation at the
surface** (`DSWRF:surface`) as the primary radiation feature — it is the
direct "sunshine reaching the ground" signal most relevant to a 2 m
temperature bias at the airports' near-midday-to-afternoon target hours. Do
NOT pull the full eight-field radiation set F97 catalogued; this build is
DSWRF only, to isolate the family's core signal cleanly (the same "lead with
the single most relevant field" discipline E1–E3 used). Any longwave or
top-of-atmosphere field is out of scope this session.

### Step 0 — window-resolution decision (this decides how the rest is built)

Before any bulk pull, settle the averaging-window problem, in this order:

1. **Check for an instantaneous DSWRF variant first.** F97 found that some
   fields (the cloud-layer fields) carry BOTH an averaged and an
   instantaneous form at the same level. Read the real `.idx` inventory at
   two sample dates (the v16 floor 2021-03-24, and one recent date OUTSIDE
   both the sealed year and the reserved 2024-25 year — e.g. 2024-06-15) and
   at all four (cycle, lead) combos, and determine whether an INSTANTANEOUS
   `DSWRF:surface` message exists (not just the "ave fcst" one). Decode a
   real value from it if it does. **If an instantaneous DSWRF exists at every
   combo and both dates, use it** — the window problem disappears entirely,
   and the feature is instantaneous like temperature/moisture/pressure
   already are. Record this as the chosen path.

2. **If there is NO instantaneous variant, de-accumulate to a common
   window.** GRIB shortwave is stored as an accumulation/average from the
   forecast start (or from the nearest preceding 6-hour synoptic mark); a
   shorter, common window can be recovered algebraically by differencing two
   accumulation endpoints. Derive a **common 2-hour window ending at the
   target hour** at ALL five airports (2 h because that is the shorter of the
   two native windows, so every airport can reach it — the 6-h airports
   de-accumulate down to their final 2 h; the 2-h airports already are 2 h).
   State the exact messages/leads differenced to obtain the 2-h increment at
   each airport in the script's own printed output before pulling in bulk,
   and confirm on a sample date that the recovered 2-h increment is
   non-negative and physically sane (shortwave averages are >= 0).

3. **Do NOT use per-airport statistical standardisation** or any other
   scheme that leaves the underlying physical window inconsistent across
   airports. Consistency must be physical (same window or instantaneous), not
   cosmetic.

Print which path (instantaneous, or 2-h de-accumulation) was chosen and why,
before any bulk pull runs. If Step 0's inventory reading is ambiguous or the
field is absent at any combo/date, STOP and report for review rather than
guessing a substitute.

### Steps 1–4 — pull, join, derive, validate (same shape as E1–E3)

- **Guard + date list (Step 1).** Build the date list from the existing
  5-feature GRIB dataset's own dates. Run `assert_reserved_year_excluded()`
  on the span plus a defensive per-date scan (0 reserved-year dates) before
  any pull request. Expect the same train span (2021-03-24..2024-07-31, 1,226
  dates) and sealed span (2025-08-01..2026-07-31, 365 dates) as E1–E3.
- **Pull (Step 2).** Fetch-decode-discard, no raw GRIB2 bytes kept on disk
  (disk-space precedent F98/E2/E3). Log every request to a per-request
  manifest (run_date, cycle, lead, field, station, status, detail — no
  bytes). Note: the de-accumulation path (if chosen) needs TWO leads per
  airport-combo (the two accumulation endpoints), like E3's tendency needed
  lead and lead-3 — the instantaneous path needs one. Report the real combo
  count, message count, fail count, and wall time.
- **Join + derive (Step 3).** Join by the same keys E1–E3 used; report drop
  count per airport per span (expect 0, matching the existing dataset's row
  counts exactly). Produce the single resolved feature column
  (`dswrf_surface_wm2` for the instantaneous path, or
  `dswrf_2h_wm2` for the de-accumulated path — name it for what it actually
  is). If de-accumulating, keep both raw accumulation endpoints as their own
  columns too, for transparency (the project's convention — cf E3 keeping
  `pressure_msl_lead_minus3_hpa`).
- **Validate (Step 4).** Per airport, per span: null count (expect 0);
  min/mean/max of the resolved feature (shortwave >= 0 everywhere; day-time
  target-hour means should be visibly positive and vary sensibly by latitude
  and season — YSDU's own 02:00 target hour is NIGHT, so its shortwave should
  be at or near zero, a useful correctness check; RNO's 20:00 is also near/
  after sunset for much of the year — report whether these two low-sun
  airports read appropriately low, do not correct). Cross-check against
  Open-Meteo's own `shortwave_radiation` over the non-reserved overlap only
  (the two windows E2/E3's cross-checks used), reporting mean|diff| per
  airport, and note plainly that Open-Meteo's own radiation may carry its own
  averaging convention — a real, expected reason for a larger gap than the
  temperature/pressure cross-checks showed, to be reported, not chased this
  session.

### What this session must not do

Fit any model or compute any MAE/skill/CV. Read, load, or join any row of the
reserved 2024-08-01..2025-07-31 confirmation year. Pull any radiation field
beyond `DSWRF:surface`, or any precipitation (E5) field. Use per-airport
statistical standardisation to paper over the window mismatch. Do per-airport
feature selection — identical handling at all five airports. Modify
`SPEC.md` or `RESULTS.md`. Commit anything.

### End of session

1. Paste the real output (actual Step-0 decision, pull/join/validation
   numbers), not a description of them.
2. Run the standard three-file consistency check (SPEC/STATUS/DECISIONS) and
   report anything that disagrees — do not fix silently.
3. Archive step: check whether anything in the live `DECISIONS.md` is now
   settled per the archive criterion; move it mechanically if so, otherwise
   report "none."
4. Record the build as a new DECISIONS finding (the next F-number), same
   shape as F98's E1 build finding — including the Step-0 window decision and
   its reasoning as part of the entry. Overwrite `STATUS.md` to reflect this
   session, ending with a **"Next planning session"** line naming session
   56's job: the staged E4 experiment (four variants — B, B+R, B+Rv, B+v,
   using `R` for the radiation feature — on the three `EXPERIMENT_FOLDS`),
   mirroring session 50/52/54's own experiment shape. Note in that line that
   E4's expected payoff is uncertain because cloud cover — already in the
   frozen baseline B — proxies much of shortwave (F97), so the experiment is
   specifically a test of whether radiation adds anything BEYOND the cloud
   feature already present.

Script name: `scripts/session55_radiation_pull.py`. Outputs:
`data/processed/session55_v16_window_with_radiation.csv`,
`data/processed/session55_sealed_window_with_radiation.csv`,
`data/processed/session55_radiation_join_drops.csv`,
`data/raw/diagnostics/session55/session55_pull_manifest.csv`,
`data/raw/diagnostics/session55/session55_window_resolution.csv`.
