# scripts/: the project's code

## How the scripts are named and run

A script named `sessionNN_*.py` was written in session NN. That session's
prompt is `session-NN.md` in [../docs/sessions/](../docs/sessions/), and its saved
output is in [../notes/](../notes/README.md). Run a script from the repo
root with the project's own Python:

```
.venv/bin/python scripts/<name>.py
```

The names and paths are kept as they are. The record (DECISIONS, SPEC and
the saved outputs) cites the scripts by path, and later scripts check
earlier ones by SHA-256 (a file fingerprint) before they import them (for
example, `session97_stagec_cv.py` checks `session62_reserved_confirm.py`
against D70.2). Renaming or editing a script would break that chain (D91.2).

## Frozen scripts: never edited

| script | what it is | entry |
|---|---|---|
| `session39_sealed_test.py` | the richer method's sealed test (F94) | D62.3(a) |
| `session48_reserved_year.py` | the reserved-year guard (D51) | D62.3(a) |
| `session60_combine_design.py` | the pre-registered feature-combination sweep design (D57) | D62.3(a) |
| `session62_reserved_confirm.py` | the selected method's confirmation on the reserved year (F109) | D62.3(a) |
| `session77_ksfo_looks.py` | KSFO's two looks (F119) | D70.6 |
| `session86_forward_build.py` | the 2026-27 forward test's data build (F128) | D91.2 |
| `session87_forward_competitors.py` | the 2026-27 NBM and MOS fetch (F129) | D80.1, D91.2 |
| `session87_forward_score.py` | the 2026-27 scoring script (F129) | D80.1, D91.2 |

Some frozen scripts write to fixed, already-committed output files, so any
re-run must happen in a clean clone (D62.3, D62.6).

## Key scripts, by result

| script | what it does | entry |
|---|---|---|
| **Minimal method** | | |
| `session03_pull.py`, `session10_pull.py`, `session15_pull.py`, `session20_pull.py`, `session26_pull.py` | pull the full forecast (Open-Meteo) and observation (IEM) history at EGLC, LFPG, DSM, YSDU and RNO | F8, F22 to F26, F38 to F41, F57 to F59, F74 to F77 |
| `session04_model.py`, `session05_model.py`, `session11_model.py`, `session16_model.py`, `session22_model.py`, `session27_model.py` | join forecasts to observations, look at the bias and rehearse on the validation year (EGLC uses two scripts) | F14, F15, F27 to F29, F42 to F46, F60 to F63, F78 to F81 |
| `session07_test.py`, `session13_test.py`, `session18_test.py`, `session24_test.py`, `session29_test.py` | each airport's one-look sealed test | F16, F30, F47, F64, F82 |
| **Richer method (GRIB)** | | |
| `session37_grib_pull.py`, `session40_grib_pull.py` | byte-range pulls of the GFS GRIB2 fields, training window and sealed year | F90, F92 |
| `session37_decode.py`, `session40_decode.py` | decode the GRIB2 extracts to the airport's grid point | F90, SPEC 8.8 |
| `session37_elevation_fix.py` | fix the elevation (lapse-rate) constants | F90, D48.3 |
| `session38_join.py`, `session38_cv.py` | join the GRIB features to observations; blocked cross-validation | F91 |
| `session39_sealed_test.py` | the sealed test (frozen; written in session 39, its one look run in session 42) | F94 |
| **Selected-features method** | | |
| `session48_reserved_year.py` | reserve 2024-25 and guard it in code (frozen) | D51 |
| `session49_upper_air_pull.py`, `session51_moisture_pull.py`, `session53_pressure_pull.py`, `session55_radiation_pull.py`, `session57_precip_pull.py` | build and validate the five candidate feature families (E1 to E5) | F98 to F105 |
| `session50_e1_experiment.py`, `session52_e2_experiment.py`, `session54_e3_experiment.py`, `session56_e4_experiment.py`, `session58_e5_experiment.py` | test each family against the baseline on the non-reserved folds | F98 to F105, D52 to D56 |
| `session60_combine_design.py`, `session61_combine_sweep.py` | pre-register (frozen) and run the combination sweep | D57, F106 |
| `session63_reserved_year_build.py` | build the reserved year's feature rows | F107 |
| `session62_reserved_confirm.py` | the one look at the reserved year (frozen) | F109 |
| **KSFO** | | |
| `session76_verify.py`, `session76_grib_pull.py`, `session76_obs_om_pull.py`, `session76_build.py` | verify KSFO on contact, pull its data and build its tables | F116 |
| `session77_ksfo_rehearsal.py` | KSFO's rehearsal and column-order band | F118 |
| `session77_ksfo_looks.py` | KSFO's two looks (frozen) | F119 |
| **Stage A** | | |
| `session83_confidence_intervals.py` | 95% intervals for every result on record | F125 |
| `session85_nbm_mos_comparison.py` | the NBM and MOS comparison on the spent years | F127 |
| **Stage B (2026-27 forward test)** | | |
| `session81_freeze_forward_models.py` | build the training set, pass the gate and freeze the models | F122 |
| `session86_forward_build.py` | the data build (frozen; not yet run on 2026-27) | F128 |
| `session87_forward_competitors.py`, `session87_forward_score.py` | the NBM and MOS fetch and the scoring (frozen; not yet run on 2026-27) | F129 |
| **Stage C** | | |
| `session91_grib_pull.py` | the GRIB pull, run on GitHub Actions, with a whole-file fallback | F133, F136 |
| `session92_verify_chunk.py` | the 13-check verifier for one month of the pull | F134, F136 |
| `session95_check_release.py` | download and check all 65 months | F137 |
| `session96_stagec_table.py` | the development table and its gate | F138 |
| `session97_stagec_cv.py` | the cross-validation folds, the fitting-code gate and the baseline | F139 |
| **This README** | | |
| `session98b_figures.py` | draws the SVG figures in `../figures/` | F140 |

## Everything else

- **Sessions 01 to 33:** per-airport checks, pulls, models and sealed tests
  for the minimal method, then the richer-features probe, scout and
  cross-validation on Open-Meteo data (F85 to F87).
- **Sessions 36 to 42:** building and checking the GRIB pipeline, and
  checks around the richer method's sealed test (F89 to F94).
- **Sessions 46 to 47:** a multi-year backtest of the frozen recipes (F96)
  and a probe of which further GRIB fields exist (F97).
- **Sessions 48 to 63:** the feature-selection programme (D51 to D58, F98
  to F109).
- **Sessions 70 to 75:** audit follow-ups (D62), a clean-room rebuild of
  F109 at RNO and its triage (D64, D65, F112 to F114), and how much column
  order alone moves a fit (F115).
- **Sessions 76 to 77:** KSFO (F116 to F119).
- **Sessions 81 to 90:** stages A and B, the source and competitor probes
  (F123, F124, F130) and stage C's scoping and airport check (F131, F132).
- **Sessions 91 to 98b:** stage C's pull, checks, table and
  cross-validation (F133 to F139), and this README's figures (F140).
- `archive_decisions.py`: standing tool. Moves every DECISIONS entry outside the Live index to the archive and checks citations (D93.8). Run at the end of every session.

The GitHub Actions workflow (`../.github/workflows/stagec-grib-pull.yml`)
runs `session91_grib_pull.py` and `session92_verify_chunk.py`.
