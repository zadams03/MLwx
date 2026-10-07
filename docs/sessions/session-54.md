# Session 54 — the staged E3 (pressure/synoptic) experiment

Read `CLAUDE.md`, `SPEC.md`, `STATUS.md`, and the live `DECISIONS.md` in full
before starting, per CLAUDE.md's own routine. This session runs the staged
E3 experiment: it mirrors session 50's E1 experiment (F99) and session 52's
E2 experiment (F100) **exactly** in shape — a LEARNING experiment that
reports a four-variant grid, **not** a pass/fail verdict. The family call
(what E3 contributes to the eventual combine-phase baseline) is made by the
owner in review afterwards, exactly as D52 and D53 were.

**This is a modelling session, but a strictly bounded one.** Models are fit
only on the three non-reserved `EXPERIMENT_FOLDS` (D51). The reserved
2024-08-01..2025-07-31 confirmation year must never be loaded, joined, or
scored — enforced the same way sessions 50/52 enforced it.

---

## Inputs

Use session 53's own join outputs unchanged — do not re-pull or re-derive
any pressure field:
- `data/processed/session53_v16_window_with_pressure.csv`
- `data/processed/session53_sealed_window_with_pressure.csv`

These already carry the frozen 5-feature baseline columns plus the E3
fields: `pressure_msl_hpa`, `pressure_surface_hpa`,
`pressure_msl_lead_minus3_hpa`, and the derived `pressure_tendency_3h_hpa`.

---

## The four variants

All on D21.4/D48.6's unchanged LightGBM settings. **Identical features at
every airport — no per-airport feature selection, RNO included**, exactly as
F99/F100 required.

- **B** — the frozen 5-feature set (`temp`, `season_sin`, `season_cos`,
  `cloud_cover`, `wind_speed_10m`), REFIT on these three folds (not a reuse
  of F94/F96/F99/F100 — refit here so every variant shares one baseline).
- **B+T** — B plus `pressure_tendency_3h_hpa` (one added feature — the
  derived form, led with, per the programme's derived-first rule).
- **B+Tv** — B+T plus the two raw pressure fields `pressure_msl_hpa` and
  `pressure_surface_hpa` (three added features total).
- **B+v** — B plus the two raw pressure fields, WITHOUT the derived tendency.

(Naming mirrors E1's B/B+L/B+Lv/B+v and E2's B/B+D/B+Dv/B+v. Do NOT include
`pressure_msl_lead_minus3_hpa` as a model feature in any variant — it is the
tendency's raw ingredient, kept in the dataset for transparency only, the
same way `t2m_raw` and `dew_point_2m` were kept but the model used the
derived depression.)

---

## Sanity checks before any model is fit (both must PASS, mirroring F99)

1. **Tendency arithmetic, on every row (not a spot check).** Verify
   `pressure_tendency_3h_hpa == round(pressure_msl_hpa -
   pressure_msl_lead_minus3_hpa, N)` across all rows of both session 53
   output files, at every airport, matching session 53's own already-passed
   check. Report the max absolute difference per airport. If any row
   mismatches, STOP and report — do not fit.
2. **Reserved-year guard.** Run `assert_reserved_year_excluded()` on all
   three `EXPERIMENT_FOLDS` before any data is loaded, plus a defensive
   per-row scan confirming zero reserved-year rows present in the loaded
   data. If either trips, STOP.

Also report, unprompted, the same internal-consistency signal F99 found: does
the `2025-26` fold's `B` variant reproduce F94/F96/F99's own raw-GFS and
persistence MAE and row counts per airport? Report the comparison — it
confirms the refit baseline is a correct reproduction of the frozen recipe.

---

## Output — mirror F99/F100 exactly

Fit all four variants on all three folds at all five airports (5 × 3 × 4 =
60 airport-fold-variant fits). Report:

1. **Grand overall** — mean MAE across all 5 airports × 3 folds (n=15
   airport-folds per variant), with delta vs B and skill % vs B, in the same
   table shape as F99/F100.
2. **Fold-averaged per airport** — mean across the three folds, skill vs B,
   for B+T / B+Tv / B+v per airport, same shape as F99/F100.
3. **Feature importances** — gain-based, percent of each variant's own
   total, for the added E3 features, so the review can see (as with E1's
   raw levels and E2's relative humidity) which raw field, if any, carries
   the signal — in particular whether `pressure_tendency_3h_hpa` or one of
   the raw levels dominates, and whether RNO differs from the other four.

Write the grid and summary to CSVs mirroring session 50/52's naming:
`data/processed/session54_e3_experiment_grid.csv` (60 rows) and
`data/processed/session54_e3_experiment_summary.csv`.

**Read the result plainly, the way F99/F100 did** — but do NOT issue a
verdict or recommend adoption. State: how much of the family's grand-overall
skill the derived tendency alone (B+T) captures; whether the raw fields add
anything on top (B+Tv vs B+T); whether the raw fields alone (B+v) hold up;
and call out DSM specifically (the diagnostic airport, most headroom per
F96) and RNO specifically (does pressure behave oddly there the way the
below-ground upper-air levels did in F98/F99, or cleanly — PRMSL is
sea-level-normalised, so it may be the one family that does NOT show an RNO
anomaly). Flag any per-fold instability (e.g. a benefit that reverses in the
thin 2022-23 fold or the truncated 2025-26 fold) as fold-quality, not
family weakness, consistent with F96/D52/D53.

---

## What this session must not do

Fit any model on, load, or score the reserved 2024-08-01..2025-07-31
confirmation year. Issue a pass/fail verdict or adopt any feature (the E3
family call is the owner's, in review). Do any per-airport feature
selection. Re-pull or re-derive any pressure field (use session 53's outputs
as-is). Touch any E4/E5 family (radiation, precipitation). Modify `SPEC.md`
or `RESULTS.md`. Commit anything — prepare changes and a suggested commit
message, then stop.

---

## End of session

1. Paste the real output (actual MAE grid and summary numbers), not a
   description of them.
2. Run the standard three-file consistency check (SPEC/STATUS/DECISIONS) and
   report anything that disagrees — do not fix silently.
3. Archive step: check whether anything in the live `DECISIONS.md` is now
   settled per the archive criterion; move it mechanically if so, else
   report "none."
4. Record the experiment as the next `DECISIONS.md` finding (`F101`) —
   a reading, not a verdict, in the same shape as F99/F100. Then overwrite
   `STATUS.md` to reflect this session, ending with a **"Next planning
   session"** line naming session 55's job: the owner records the E3 family
   verdict (D54, from review of F101's grid), and the session then builds
   and validates the E4 (radiation) feature set — noting E4's known
   awkwardness (the lead-dependent averaging window, F97: 6h average at
   lead 24 vs 2h at lead 26) must be normalised to a same-meaning feature
   across airports before it can be used.

Script name: `scripts/session54_e3_experiment.py`.
