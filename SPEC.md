# SPEC.md — how this project should work

This file is the source of truth for *how the project should work*. If the
code and this file ever disagree, this file is right and the code is wrong.

Some terms are defined the first time they appear. Keep language plain.

---

## 1. What the project does

Big weather models (like the one called **GFS**) are good, but at any one
place they tend to make the *same small mistakes over and over*. That
repeated, predictable error is called **bias**.

This project learns GFS's bias at one specific airport from past data, and
corrects for it — so the corrected forecast lands closer to what actually
happened than raw GFS did.

The airport is **London City (ICAO code EGLC)**, at latitude 51.505,
longitude 0.055.

The long-term aim is a live daily tool that shows a corrected temperature
forecast for the day ahead. That is the destination, not the starting point.
See section 6 for the staged build order.

---

## 2. Critical rules (non-negotiable, apply to every session)

These rules protect the honesty of the result. They apply whether or not a
session prompt repeats them. Breaking any of them can make a result *look*
fine while being quietly invalid.

**2.1 No look-ahead leakage.** The model must never, directly or indirectly,
see information from the future it is trying to predict. Specifically:

- **2.1a Time-based split only.** When splitting data into training and test
  sets, split by *time* (train on earlier dates, test on later dates). Never
  split randomly. A random split lets the model learn from days that come
  after the days it is tested on.
- **2.1b Correct forecast source.** Use Open-Meteo's **Previous Runs API**
  for past forecasts. Do **not** use its **Historical Forecast API**. The
  Historical Forecast API stitches together the freshest slice of many runs,
  which effectively already contains the answer. (See DECISIONS for the full
  reasoning.)
- **2.1c Climatology from training data only.** The climatology baseline
  (section 5) must be computed using only the training period. If it is
  averaged over all years including the test period, that is leakage too.
- **2.1d Persistence uses past only.** The persistence baseline and any
  persistence-style feature may use only observations from *before* the time
  being predicted.

**2.2 Never silently fill missing data.** Weather records have gaps. When a
forecast or an observation is missing so a pair cannot be formed:

- Drop that row.
- Count how many rows were dropped.
- Report the count as part of the output.

Never estimate, interpolate, or invent a value to fill a gap. Filled data is
invented data. If gaps turn out frequent enough to matter, log it in
DECISIONS as a finding for the owner to decide on — do not auto-patch.

**2.3 Raw data is immutable.** Never change raw downloaded data in place.
Keep raw pulls untouched in `data/raw/` and work on copies. Because the data
sources are live services that can revise or backfill, record the pull date
and the exact query alongside each raw file, and treat it as a fixed
snapshot.

**2.4 The evaluation bar is frozen before running.** The success bar in
section 5 is fixed *before* the model is run, and is not changed afterwards
to fit the result. A result that fails the bar is an honest finding, not a
failure.

---

## 3. Data sources

**3.1 Truth data (what actually happened).** Official hourly airport weather
observations for EGLC, in the METAR format (the standard coded format
airports report in). Source: the Iowa Environmental Mesonet (IEM) ASOS
download service. Free, no account needed.

**3.2 Forecast data (what GFS predicted).** Past GFS forecasts for the EGLC
location. Source: Open-Meteo **Previous Runs API**, model string
**`gfs_global`** (see DECISIONS D16). Free, no account needed.

The lead time is the API's 1-day offset (`previous_day1`). This is a
**nominal** 24-hour lead, not an exact one. GFS runs every 6 hours, and
Open-Meteo builds the series by taking hours 24–29 of each run and stitching
them together, so the true lead sweeps between about **24 and 30 hours**
across the day and then resets (see DECISIONS F5).

Every value is nonetheless a genuine forecast made **at least 24 hours before
its valid time**, so the no-look-ahead rule (2.1b) still holds.

Confirmed available back to **24 March 2021**. (A request for 1 March 2021
returns HTTP 200 with every value null; the first hour carrying a real value
is 2021-03-24 00:00 UTC. See DECISIONS F1.)

**3.3 Verify on contact.** Two things can only be checked by pulling real
data, and must be checked on the first pull:
- that the Previous Runs API actually returns history back to 2021 (not just
  recent months);
- that EGLC's observation record is complete enough over the chosen period.

---

## 4. The target and the method

**4.1 Target (stage 1).** The temperature at **one fixed hour of the day**.
This is deliberately the simplest clean target — the honest test of whether
the whole idea works at all. Widening to more hours comes later (section 6).

**4.2 What the model learns.** The model does **not** predict the temperature
directly. It predicts the *gap* between what actually happened and what GFS
forecast (observation minus forecast). The final corrected forecast is then
GFS's forecast plus the predicted correction. This keeps the physics model
doing the hard work and the correction doing only the local clean-up.

**4.3 Training window (fixed dates).** Train on **2021-03-24 to 2025-07-31**
(inclusive). Hold out **2025-08-01 to 2026-07-31** (inclusive) as an untouched
test period — a clean 12 months, so the result is judged across all four
seasons. Data after 2026-07-31 is not used, which keeps the test set exactly
one calendar year. These dates are fixed before any model runs (see
DECISIONS D13).

**4.4 Model type.** A gradient-boosted tree model (a standard model for
table-shaped data). This runs on a normal laptop CPU; no GPU is needed.

**4.5 Lining up observation and forecast in time.** Each forecast valid at
`HH:00` is paired with the nearest observation, which in practice is the
routine `:50` report ten minutes earlier. If no report falls within 15 minutes
of the hour, that hour is dropped and counted (rule 2.2). See DECISIONS D14.

---

## 5. Evaluation protocol (FROZEN — do not change after seeing results)

**5.1 Metric.** Mean absolute error (MAE) — the average size of the gap
between forecast and what actually happened, in degrees Celsius. Lower is
better.

**5.2 Baselines to beat.** The corrected forecast is compared against:
- **Raw GFS** — the uncorrected forecast. Beating this is the core claim of
  the project.
- **Persistence** — the lazy guess "tomorrow will be the same as today".
  Beating this proves the model beats the simplest possible predictor.
- **Climatology** (optional third check) — the seasonal average for that date,
  computed from the training period only (see rule 2.1c).

**5.3 Success bar (qualitative, frozen before running).** Stage 1 succeeds
if the corrected forecast has a lower MAE than **both raw GFS and
persistence**, over the held-out test period. The bar itself is unchanged; the
only thing now made concrete is that the test period is the fixed window
2025-08-01 to 2026-07-31, set before any model runs (section 4.3, DECISIONS
D13).

The exact numeric margin is deliberately left qualitative for now. A specific
figure (for example, a minimum percent improvement over raw GFS) may be fixed
just before the model is run — but still *before* seeing any results, and
recorded in DECISIONS at that point.

**5.4 Deeper evaluation (parked).** More thorough checks — expressing results
as a skill score, testing whether the win holds across seasons, statistical
significance — are parked until stage 1 passes. Do not fold them into stage 1.

---

## 6. Build order (each stage opens only when the previous one passes)

Stage 1 is fully specified above. The stages below are intentionally left as
short descriptions only. Do **not** write out their detailed design until the
project reaches them and the owner opens the stage. If a session tries to
fill in a later stage early, treat it as a warning sign and stop.

- **Stage 1 — one model, one airport, one fixed hour.** (Specified above.)
  Prove the correction beats the baselines.
- **Stage 2 — second airport (Charles de Gaulle, CDG).** Re-run the same
  recipe at a second location to prove stage 1 was not a fluke.
- **Stage 3 — pool airports.** Combine airports into one model with
  location-describing features, so locations learn from each other.
- **Stage 4 — add models and blend.** Bring in other forecasts (ECMWF, ICON,
  and the Google WeatherNext AI model) and combine them. See the WeatherNext
  notes in DECISIONS.
- **Stage 5 — widen the target.** Move from one fixed hour to a full hourly
  temperature curve across the day ahead (the daily maximum then falls out as
  the peak of the curve). Add the 48-hour lead time alongside 24-hour.
- **Stage 6 — live product.** Point the proven model at today's fresh
  forecast, run it daily, and display a corrected temperature forecast for
  the day ahead, updated continuously.

*(Sections for stages 2–6 are intentionally empty until opened.)*
