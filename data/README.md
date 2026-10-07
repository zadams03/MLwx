# data/: what each folder holds

Raw data is never changed in place (SPEC 2.3). Raw pulls have a
`.meta.txt` beside them that records the pull date and exact query, so
each is a fixed snapshot of a live service.

## raw/

- **IEM observations:** `iem_asos_<station>_<dates>_routine.csv`, the
  hourly airport reports used as the truth data (SPEC 3.1): the six
  development airports' histories and short check samples, the 45
  further airports pulled for stage C (F132.4), and short samples from
  two candidate stations not chosen, YSCB (session 19) and BZN (session
  25).
- **Open-Meteo forecasts:** `openmeteo_previousruns_*.json`, the past GFS
  forecasts behind the minimal method (SPEC 3.2).
- **`features/`:** Open-Meteo cloud cover and wind pulls for the
  richer-features work (sessions 32 and 76).
- **`diagnostics/`:** one folder per session, holding probe samples, GRIB
  pull manifests (the exact URL and byte range of every message) and
  small GRIB2 samples. The samples stay committed; only the bulk cache is left out
  (D47, D62.7).
- **`iem_mos/`:** the raw GFS MOS (MAV) responses for the NBM and MOS
  comparison, saved unchanged (F127.3).
- **`grib`** (not committed): the bulk GRIB cache, about 20 GB. It can be
  fetched again from the manifests in `diagnostics/`, so only they are
  committed (D47).

## processed/

Built tables and result files. Most are named by the session that wrote
them (for example `session63_reserved_confirm_grid.csv`, the F109
results, or `session97_stagec_cv_scores.csv`, stage C's build-choice
scores, F139). The `grib_features_*` files are the richer method's GRIB
feature tables (sessions 37 and 40).

## models/

`session81/`: the frozen models of the 2026-27 forward test, one
`B+D,L,R,T` model and one plain `B` model per airport, with a
`manifest.json` that records each file's SHA-256 (F122). They are never
refit (D73.2).

## rebuild/

Files from checks that rebuilt a recorded result from scratch: the
clean-room rebuild of F109 at RNO and its triage (sessions 72 to 74; D64,
D65, F112 to F114), the column-order spread (session 75, F115), and
KSFO's checks and rehearsal (sessions 76b and 77; F117, F118).

## Stage C's data, outside the repo

Stage C's data is too large for git, so it lives elsewhere and is checked
by SHA-256:

- **The Release `stagec-grib-pull-v1`** of this repository: 195 files, 65
  months of GFS point values for 51 airports (F137). Its inventory is
  committed as `processed/session95_pull_inventory.csv`.
- **`MLwx-pull/`**, a folder beside the repo: the owner's local copy of
  those 195 Release files (F137).
- **`MLwx-stagec/`**, a folder beside the repo: the development table
  built from them, one file per development airport, rebuilt exactly from
  the Release and the committed observations (D88.8, F138). Its files'
  SHA-256 are in `processed/session96_stagec_dev_table.meta.txt`.

The data's sources and terms are in the root README's section 9,
[Data credits and terms](../README.md#9-data-credits-and-terms).
