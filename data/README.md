# data/: what each folder holds

Raw data is never changed in place. Raw pulls have a `.meta.txt` beside them that records
the pull date and the exact query, so each is a fixed snapshot of a live service.

"Stage C" below is the project's name for the hourly curve and daily maximum.

## raw/

- **IEM observations:** `iem_asos_<station>_<dates>_routine.csv`, the hourly airport
  reports used as the truth data. They cover the six development airports' histories and
  short check samples, the 45 further airports pulled for stage C, and short samples from
  two candidate stations that were not chosen: YSCB (session 19) and BZN (session 25).
- **Open-Meteo forecasts:** `openmeteo_previousruns_*.json`, the past GFS forecasts behind
  the minimal method.
- **`features/`:** Open-Meteo cloud cover and wind pulls for the richer-features work
  (sessions 32 and 76).
- **`diagnostics/`:** one folder per session, holding probe samples, GRIB pull manifests
  (the exact URL and byte range of every message) and small GRIB2 samples. The samples stay
  committed; only the bulk cache is left out.
- **`iem_mos/`:** the raw GFS MOS (MAV) responses for the NBM and MOS comparison, saved
  unchanged.
- **`grib`** (not committed): the bulk GRIB cache, about 39 GB. It was moved off the laptop
  to an external drive. Only finished scripts from sessions 37 to 89 read it, so they need
  the drive to re-run. Its manifests in `diagnostics/` stay committed.

## processed/

Built tables and result files. Most are named by the session that wrote them (for example
`session63_reserved_confirm_grid.csv`, the best one-hour method's results, or
`session97_stagec_cv_scores.csv`, stage C's build-choice scores). The `grib_features_*`
files are the richer method's GRIB feature tables (sessions 37 and 40). Folders named by
session hold one piece of work's outputs:

- `session112_analysis/` and `session114_comparisons/`: the tables behind
  [ANALYSIS.md](../ANALYSIS.md).
- `session113/`: the comparison forecasts and official daily maximums on spent years,
  credited in the root README's data credits section.
- `session120_audit/` and `session121_audit/`: the health check.

## models/

`session81/`: the frozen models of the 2026-27 forward test, one `B+D,L,R,T` model (the
best one-hour method) and one plain `B` model (the five-input version) per airport, with a
`manifest.json` that records each file's SHA-256 (a file fingerprint). They are never refit.

## rebuild/

Files from checks that rebuilt a recorded result from scratch: the clean-room rebuild of the
best one-hour method's result at Reno and its triage (sessions 72 to 74), the column-order
spread (session 75), and San Francisco's checks and rehearsal (sessions 76b and 77).

## Stage C's data, outside the repo

Stage C's data is too large for git, so it lives elsewhere and is checked by SHA-256:

- **The Release `stagec-grib-pull-v1`** of this repository: 195 files, 65 months of GFS point
  values for 51 airports. Its inventory is committed as
  `processed/session95_pull_inventory.csv`.
- **`MLwx-pull/`**, a folder beside the repo: the owner's local copy of those 195 Release
  files.
- **`MLwx-stagec/`**, a folder beside the repo: the development table built from them, one
  file per development airport, rebuilt exactly from the Release and the committed
  observations. Its files' SHA-256 are in
  `processed/session96_stagec_dev_table.meta.txt`.
- **`MLwx-pull-f025-048/`**, a folder beside the repo: the owner's local copy of the Release
  for forecast hours 25 to 48.
- **The claim airports' tables**, also in `MLwx-stagec/`: twelve files, two per claim airport
  (hours 0 to 24 and 25 to 48), built for stage C's claim test.

The data's sources and terms are in the root README's data credits section,
[Data credits and terms](../README.md#data-credits-and-terms).

## Where these facts come from

"D" and "F" numbers are entries in [../DECISIONS.md](../DECISIONS.md) or its
[archive](../DECISIONS-archive.md); "SPEC" is [../SPEC.md](../SPEC.md).

| fact in this file | where it is recorded |
|---|---|
| Raw data is never changed in place; each raw pull has its pull date and query | SPEC 2.3 |
| IEM observations are the truth data; the 45 further airports | SPEC 3.1; F132.4 |
| Open-Meteo forecasts behind the minimal method | SPEC 3.2 |
| The bulk GRIB cache: not committed, the external drive, sessions 37 to 89 | D47, D62.7, D102.3 |
| The raw MAV responses | F127.3 |
| The best one-hour method's results file; stage C's build-choice scores | F109; F139 |
| The frozen models of the 2026-27 forward test; never refit | F122; D73.2 |
| The rebuild checks | D64, D65, F112 to F114 (Reno); F115 (column order); F117, F118 (San Francisco) |
| The Release `stagec-grib-pull-v1` and `MLwx-pull/` | F137 |
| `MLwx-stagec/` and its SHA-256 file | D88.8, F138 |
| `MLwx-pull-f025-048/` | D98, F147 |
| The claim airports' tables | D100, F149 |
