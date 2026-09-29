# MLwx

## 1. What this is

MLwx learns the steady, repeated error (the **bias**) that the GFS weather
model makes in its 2 m air temperature forecast at one airport, then
corrects for it. GFS is the US National Weather Service's global forecast
model. Each airport gets its own LightGBM model (a gradient-boosted tree
model, a standard tool for table-shaped data). The correction is a form of
**Model Output Statistics (MOS)**, the decades-old technique of learning a
model's local error from past forecasts and observations. Each corrected
forecast is judged on held-out years against two references: raw GFS, and
persistence (the lazy guess that tomorrow's temperature equals today's).

This is a research project and a private tool. It is not an operational
forecast, and it must not be used for safety-critical decisions.

## 2. Headline result

The project has three tested methods (section 3). The one to lead with is
the **selected-features method**, `B+D,L,R,T` (SPEC 8), on the reserved
year 2024-08-01 to 2025-07-31, judged once per airport (F109). MAE is the
mean absolute error in degrees Celsius. Skill is `1 - model MAE / reference
MAE`, so positive means the model beats the reference. The brackets are 95%
intervals from a moving-block bootstrap (7-day blocks, 10,000 resamples,
D75.2, F125.6).

| airport | raw GFS MAE (F109) | model MAE (F109) | skill over raw GFS [95%] (F125.6) | skill over persistence [95%] (F125.6) |
|---|---|---|---|---|
| EGLC (London City) | 1.2362 | 1.0008 | +19.0% [+12.6, +24.2] | +55.0% [+48.5, +61.2] |
| LFPG (Paris CDG) | 1.4091 | 1.2369 | +12.2% [+6.8, +17.6] | +51.0% [+43.0, +57.5] |
| DSM (Des Moines) | 1.7043 | 1.4123 | +17.1% [+7.4, +27.0] | +65.6% [+60.8, +70.3] |
| YSDU (Dubbo) | 1.4897 | 1.2643 | +15.1% [+7.9, +22.3] | +51.7% [+44.9, +57.9] |
| RNO (Reno) | 1.6135 | 1.2742 | +21.0% [+13.2, +28.5] | +53.8% [+46.3, +60.4] |

**Every interval lies above zero, against both references, at all five
airports.** "Raw GFS" here is the GFS 2 m temperature after this project's
fixed elevation adjustment (SPEC 5.2, D48.10). Persistence is scored on
test days that have a previous-day observation, so the persistence
column's day count can be a few days smaller than the raw GFS column's
(F125.6, F125.8).

Four things must be read with that table:

- **The minimal method fails at Reno** (-3.1% against raw GFS, F82). Its
  margins over raw GFS at DSM, YSDU and RNO have 95% intervals that
  include zero: DSM +6.3% [-4.2, +14.8], YSDU +3.3% [-4.9, +11.1], RNO
  -3.1% [-13.4, +8.1] (F125.4).
- **KSFO (San Francisco) passes both of its pre-registered looks** (F119,
  D71). Its headline is look A: 1.2576 against 1.4263, +11.83% over raw GFS
  (D71.2). It is **not directly comparable** with the five airports above:
  its grid point is sea-mixed and its check against Open-Meteo failed,
  explained by a difference between the sources (D69, D71.5; RESULTS 6.5).
- **The intervals describe one test year only.** They capture day-to-day
  sampling within that year, not year-to-year variation. The airports share
  each year's weather, so the five intervals are not independent (F125.9).
  The intervals are descriptive and change no verdict (D75.2).
- **Both held-out years are now spent** at every airport (D59.5, D71.1).
  The 2026-27 forward test is pre-registered and its models are frozen
  (D73, F122). It has not been scored (D73.8).

Full tables, caveats and the other two methods' intervals are in
**RESULTS.md**, section 6.6 for the intervals.

## 3. How it works

**Target.** The temperature at one fixed hour a day, chosen for each
airport so that it falls at local solar noon (SPEC 4.1). Daylight saving
is ignored, so the hour stays fixed all year. The correction model learns
the residual: observed temperature minus the GFS forecast (SPEC 4.2). The
corrected forecast is GFS plus that predicted residual.

**Three methods**, each tested against the same frozen pass bar (SPEC 5.3):
the corrected forecast must beat both raw GFS and persistence on MAE over
the held-out period.

1. **Minimal method** (SPEC 1 to 6). Three features: the GFS forecast
   temperature and two season terms. Forecast source: Open-Meteo's Previous
   Runs API. Passes at EGLC, LFPG, DSM and YSDU and fails at RNO (F16, F30,
   F47, F64, F82).
2. **Richer 5-feature method** (SPEC 7). Adds cloud cover and 10 m wind
   speed, and reads GFS 0.25 degree GRIB2 files (the standard binary format
   for gridded weather data) straight from NOAA's public AWS archive.
   Passes at all five airports, Reno included (F94).
3. **Selected-features method** (SPEC 8). The richer method plus four
   features picked by a staged, time-ordered search: moisture, lapse rate
   (how fast temperature falls with height), shortwave radiation and
   pressure tendency. Passes at all five airports on the reserved year
   (F109). It is the project's default recipe (SPEC 8.7). It also passes
   at KSFO on two looks (F119).

**Discipline.**
- Splits are by time only, and every model is trained only on data from
  before its own held-out period (SPEC 2.1a). The windows as recorded:
  - Minimal and richer methods: train 2021-03-24 to 2025-07-31, test the
    sealed year 2025-08-01 to 2026-07-31 (SPEC 4.3, 7.2).
  - Selected method: train 2021-03-24 to 2024-07-31, test the reserved
    year 2024-08-01 to 2025-07-31 (SPEC 8.3, D51).
  - KSFO, two looks: look A trains 2021-03-24 to 2024-07-31 and tests
    2024-25; look B trains 2021-03-24 to 2025-07-31 and tests 2025-26
    (SPEC 8.5, D70.3).
- The bar is fixed in writing before any held-out data is opened, and each
  held-out year gets one look (SPEC 2.4, 5.0).
- Missing data is dropped and counted, never filled (SPEC 2.2).
- The same features and the same model settings are used at every airport.
  Nothing is tuned per airport (SPEC 2.5, D21.4).
- A result is a **claim** only if it comes from held-out data used once.
  Design choices are made by cross-validation on other data (SPEC 2.5).

## 4. How this was built

The owner planned the work, made every decision, wrote every session
prompt and reviewed every change. The code was written by Claude Code
(Anthropic's AI coding tool) under the standing rules in CLAUDE.md, one
scoped session at a time. Every change was reviewed and committed by hand.
The decision record in DECISIONS.md shows the reasoning behind each step.

## 5. Repository layout

**Read these first:**
- **README.md**: this file.
- **RESULTS.md**: the results in one place, each number cited to its entry.
- **SPEC.md**: the source of truth for how the project should work.
- **DECISIONS.md**: the append-only log of choices and findings, with
  numbers such as D76 and F126 that the other files cite.
- `scripts/`: the code, one or more scripts per session, named
  `sessionNN_*.py`.
- `data/`: raw pulls (`data/raw/`), built datasets and result tables
  (`data/processed/`), frozen 2026-27 models (`data/models/`) and a
  rebuild check (`data/rebuild/`).

**Safe to skip.** These are the working record of the planning and
execution loop, kept for audit (D76.5):
- `docs/`: session prompts and commit messages.
- `notes/`: saved script output and audit reports. Some of these files
  contain file paths from the author's own machine (F126.2).
- STATUS.md: a snapshot of where the project is now.
- PROJECT-INSTRUCTIONS.md, CLAUDE.md and DECISIONS-archive.md: the
  planning guide, the coding rules, and settled decisions moved out of
  DECISIONS.md word for word.

## 6. Reproducing

This section lists only what can be checked by reading `requirements.txt`,
the scripts and SPEC. Nothing was run to write it.

- **Python setup.** Python 3.12.2 on macOS (arm64). From the repo root:

  ```
  python3 -m venv .venv
  .venv/bin/python -m pip install -r requirements.txt
  ```

  Versions are pinned in `requirements.txt` (for example lightgbm 4.7.0
  and numpy 2.5.2). The `eccodes` package brings the ecCodes GRIB library
  with it. LightGBM on macOS needs the OpenMP library `libomp.dylib`: run
  `brew install libomp`, or rely on the workaround the modelling scripts
  use (see `requirements.txt`).
- **Run scripts** with `.venv/bin/python scripts/<script>.py`, not a bare
  `python`, because the system Python has no LightGBM.
- **Small raw pulls are committed** under `data/raw/`, each with a
  `.meta.txt` beside it that gives the pull date and exact query (SPEC 2.3).
- **The bulk GRIB cache is not committed.** It is the gitignored folder
  `data/raw/grib` (about 20 GB, D47). The committed pull manifests under
  `data/raw/diagnostics/` (for example `session37/session37_pull_manifest.csv`
  and `session76/session76_pull_manifest.csv`) give the exact URL and byte
  range of each file. The pull scripts (`session37_grib_pull.py`,
  `session40_grib_pull.py`, and the feature pulls such as
  `session49_upper_air_pull.py`) fetch single messages from the public
  bucket `noaa-gfs-bdp-pds` by byte range.
- **Not verifiable from the repo:** the full run order of all the scripts
  is spread across DECISIONS.md and is not written in one place, and no
  session has re-fetched the cache from scratch.
- **Frozen scripts** are never edited: `session39_sealed_test.py`,
  `session48_reserved_year.py`, `session60_combine_design.py` and
  `session62_reserved_confirm.py`. Some write to fixed, already-committed
  output files, so any re-run must happen in a clean clone (D62.3, D62.6).

## 7. Status and roadmap

The roadmap (SPEC 6, D72) runs as stages. Stages A and B run side by side.

- **A. Benchmark and source probe.** Confidence intervals (done, F125), a
  comparison with NWS MOS and the National Blend of Models, and a
  read-only probe of other weather models' data (done, F123, F124).
- **B. Forward test and data collection.** The 2026-27 GFS forward test is
  pre-registered (D73) and its models are frozen (F122).
- **C. Widen the target,** on GFS only: an hourly curve, the daily
  maximum and a 48-hour lead.
- **D. Correct each other weather model** on its own.
- **E. Blend and stack** the corrected models.
- **F. Upgrade policy** for when a weather model changes version, starting
  with GFS v17.
- **G. Live product, version 1:** a daily pipeline, a prediction log that
  is never edited, a simple display and one-script airport onboarding.
- **H. Probabilistic forecasts:** ranges with stated odds.
- **New airports** are an ongoing track. **Pooling** (one model across
  airports) is conditional.

## 8. Data credits and terms

The data is not covered by the code licence. It stays under its sources'
terms. The terms below were read from each source's own page on
2026-09-29 (F126.3).

- **Open-Meteo** (Previous Runs API, `previous-runs-api.open-meteo.com`).
  Supplied past GFS forecasts for the minimal method. Data offered under
  CC BY 4.0: give credit, link to the licence and say if changes were
  made. Terms page: https://open-meteo.com/en/terms. Licence page:
  https://open-meteo.com/en/licence. The free API is for non-commercial
  use only, under 10,000 calls a day. The raw JSON pulls under `data/raw/`
  are Open-Meteo's data unchanged. The processed files built from them
  (under `data/processed/`) are derived, changed values. Weather data by
  [Open-Meteo.com](https://open-meteo.com/).
- **Iowa Environmental Mesonet (IEM), Iowa State University** (ASOS
  observation download, `mesonet.agron.iastate.edu`). Supplied the
  hourly airport observations that are the truth data. Its disclaimer
  page says its materials are in the public domain and may be used for
  any lawful purpose, and that credit to the IEM would be appreciated.
  Page: https://mesonet.agron.iastate.edu/disclaimer.php.
- **NOAA / NCEP GFS** (GRIB2 files from the NOAA Open Data Dissemination
  program, hosted on AWS in the bucket `noaa-gfs-bdp-pds`). Supplied the
  GRIB forecasts for the richer and selected methods. The AWS registry
  page says the data is open and may be used as desired, that NOAA
  requests credit for unaltered data, that you may not state or imply
  NOAA endorses you, and that modified data may not be presented as
  original. Page: https://registry.opendata.aws/noaa-gfs-bdp-pds/. This
  repo's processed files are derived values, and the few small `.grib2`
  samples under `data/raw/diagnostics/` are NOAA data.
- **Probed only, no data committed** (F123, F124.4): ECMWF IFS and AIFS
  open data, DWD ICON, NOAA GEFS, Google WeatherNext, NOAA NBM and NWS
  MOS (through the IEM archive), and Open-Meteo Single Runs. Each was
  checked read-only for archive depth and fields. Their terms were not
  fetched.

## 9. Licence

The code is released under the MIT licence. See `LICENSE`. There is no
warranty. The code and results are for research use and are not for
operational or safety-critical use. The licence does not change the terms
of the data in section 8.
