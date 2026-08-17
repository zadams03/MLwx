# SPEC.md — how this project should work

This file is the source of truth for *how the project should work*. If the
code and this file ever disagree, this file is right and the code is wrong.

Some terms are defined the first time they appear. Keep language plain.

---

## 1. What the project does

Big weather models (like the one called **GFS**) are good, but at any one
place they tend to make the *same small mistakes over and over*. That
repeated, predictable error is called **bias**.

This project learns GFS's bias at an airport from past data, and corrects for
it — so the corrected forecast lands closer to what actually happened than raw
GFS did.

The same recipe is run **one airport at a time**. Every airport gets the same
treatment: the same target hour, the same split dates, the same method, and the
same frozen bar, judged once on that airport's own test year. The only thing
that changes from one airport to the next is the location.

The airports so far:

- **London City (ICAO code EGLC)** — stage 1, **passed**.
- **Paris Charles de Gaulle (IATA code CDG, ICAO code LFPG)** — stage 2,
  **in progress**.

More airports may follow. Each airport's own facts — its code, its position,
the forecast grid point it maps to, and when it reports — live in the airport
table in section 3.4. Everything else in this file is shared by all of them.

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

Both sources are **shared by every airport**. Only the station code, the
network and the coordinates change from one airport to the next, and those live
in the airport table in section 3.4.

**3.1 Truth data (what actually happened).** Official hourly airport weather
observations, in the METAR format (the standard coded format airports report
in). Source: the Iowa Environmental Mesonet (IEM) ASOS download service. Free,
no account needed. Each airport is requested by its ICAO code; the routine
report (IEM `report_type=3`) is the truth observation.

**3.2 Forecast data (what GFS predicted).** Past GFS forecasts for the
airport's location. Source: Open-Meteo **Previous Runs API**, model string
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
is 2021-03-24 00:00 UTC. See DECISIONS F1.) **The same first hour was found at
CDG** — 2021-03-24 00:00 UTC exactly, with the same all-null answer before it
(DECISIONS F20). So the March 2021 floor is a property of the archive itself,
not of one place, and the section 4.3 split dates work at both airports.

The archive is **not continuous** at EGLC. From that start date to 2026-07-31
there is exactly one sizeable gap: **492 hours with no forecast value, from
2023-12-30 00:00 to 2024-01-19 11:00 UTC**. It falls entirely inside the
training window (the test window has no forecast gap at all). Those hours are
dropped and counted, never filled (rule 2.2). See DECISIONS F8, and F11 for the
correction to F1's earlier claim of continuity.

**Whether CDG has a forecast gap is NOT YET KNOWN — to be verified.** The gap
above was mapped hour by hour at EGLC only. It is likely to be present at CDG
too, since the archive floor is shared, but likely is not checked, and F11's
lesson is exactly that spot checks cannot prove anything about the hours nobody
looked at. The CDG pull session maps every hour of its forecast series the way
session 03b did for EGLC, and the answer is written in here then. Until it is,
this line stands as the marker. See DECISIONS Q21.

**3.3 Verify on contact.** Two things can only be checked by pulling real
data, and must be checked on the first pull **for each new airport**:
- that the Previous Runs API actually returns history back to 2021 at that
  location (not just recent months);
- that the airport's observation record is complete enough over the chosen
  period, and at what minute past the hour it reports.

Both were checked for EGLC in session 01 (F1, F2, F3) and for CDG in session 08
(F17–F21). Both airports passed.

**3.4 The airport table.** This is the only place per-airport facts are
written. Everything else in this file is shared. Adding an airport means adding
a row here, filled in from real pulls — never from memory or a map.

The airport, and where it is (position from IEM, section 3.1):

| ICAO | airport | stage | IEM network | latitude | longitude | elevation |
|---|---|---|---|---|---|---|
| EGLC | London City | 1 — passed | `GB__ASOS` (unverified) | 51.5053 | 0.0553 | 5 m |
| LFPG | Paris Charles de Gaulle (CDG) | 2 — in progress | `FR__ASOS` | 49.0153 | 2.5344 | 109 m |

The forecast grid point it maps to (from Open-Meteo, section 3.2), and when the
station reports:

| ICAO | grid latitude | grid longitude | grid elevation | distance from airport | height mismatch | reports at | also files at | pairing offset |
|---|---|---|---|---|---|---|---|---|
| EGLC | 51.487137 | 0.0 | 4 m | 4.33 km | 1 m | `:50` | `:20` | 10 minutes |
| LFPG | 49.027008 | 2.578125 | 109 m | 3.44 km | 0 m | `:00` | `:30` | 0 minutes |

Notes on the table:

- **The airport position is IEM's own, not a figure from elsewhere.** IEM's
  record is treated as authoritative, because it is the same source the
  observations come from. For CDG this mattered: IEM's position sits 1.15 km
  from the approximate figure the session prompt carried, and IEM's was used
  (DECISIONS F17).
- **The grid point is whatever Open-Meteo returns** for that airport's
  position. A few kilometres of offset is not a fault — it is exactly the kind
  of steady local error this project exists to learn (DECISIONS Q5, F17).
- **"Reports at" is the minute past the hour the routine METAR is stamped**,
  and it is what makes the general pairing rule (4.5) concrete for that
  airport. **"Pairing offset"** follows from it: how far the paired observation
  sits from 12:00 UTC. Both stations also file a second scheduled report each
  hour, which IEM labels "special" although it is plainly scheduled; neither is
  used as the truth observation (DECISIONS F3, F19).
- **EGLC's network code is not verified.** Every EGLC request was made by
  station code alone, with no network parameter, so `GB__ASOS` has never come
  back from IEM in this project — it is carried here from the session 09 prompt
  and marked unverified rather than written as a checked fact. LFPG's
  `FR__ASOS` was verified by a real pull (DECISIONS F17). See DECISIONS Q22.

---

## 4. The target and the method

**4.1 Target.** The temperature at **one fixed hour of the day**, and that hour
is **12:00 UTC**. This is deliberately the simplest clean target — the honest
test of whether the whole idea works at all. Widening to more hours comes later
(section 6).

**The same hour, 12:00 UTC, is used at every airport.** That is a deliberate
choice, not a convenience: stage 2 changes the **location and nothing else**, so
if the result at a second airport differs, the location is the only thing that
can explain it (DECISIONS D26).

**This convention changes at stage 3, and only there.** When airports are pooled
into one model, the target moves to each airport's **solar standard noon** —
local standard-time noon, with daylight saving deliberately ignored, so the
target stays a fixed UTC hour for that airport all year round. The reason is
that 12:00 UTC is a different time of day at each location, which is harmless
when airports are modelled separately and wrong when they are pooled. Noted here
so it is not a surprise; it is **not** applied to stage 1 or stage 2 (DECISIONS
D27).

Why 12:00 UTC was chosen (decided on principle, before any model was built or
any performance seen):
- It is in daylight, so it catches the daytime heating that GFS tends to
  mis-handle. A night-time hour would test the easier part of the day.
- It is a stable, well-observed time of day — the station reports it reliably
  and the temperature is not moving fast.
- It avoids dawn and dusk, when temperature swings quickest and the ten-minute
  offset in the pairing rule (4.5) would matter most.

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

**These dates are shared by every airport.** They are not re-chosen per
location. CDG's forecast archive begins on the same hour as EGLC's, 2021-03-24
00:00 UTC (section 3.2, DECISIONS F20), so the dates need no adjusting for it.
Each airport has its own train and test *rows* on those shared dates, and its
own sealed test year, judged once.

Inside the training window there is a further subdivision used for rehearsal —
inner-training 2021-03-24 to 2024-07-31 and a validation year 2024-08-01 to
2025-07-31 — so the method can be tried out without touching the sealed test
year. The test model is then refitted on the whole training window. This
applies per airport too. See DECISIONS D18 and D21.5.

**4.4 Model type.** A gradient-boosted tree model (a standard model for
table-shaped data). This runs on a normal laptop CPU; no GPU is needed.

**4.5 Lining up observation and forecast in time.** Each forecast valid at
`HH:00` is paired with the station's **nearest routine report to that hour**.
If no report falls within 15 minutes of the hour, that hour is dropped and
counted (rule 2.2). See DECISIONS D14.

The rule names no minute, because the minute is a per-airport fact and lives in
the airport table (3.4). What it means in practice:

- At **EGLC**, which reports at `:50`, the observation for 12:00 UTC is the
  11:50 report — ten minutes earlier. Ten minutes is a negligible gap for
  temperature, which is the argument D14 rests on.
- At **LFPG**, which reports at `:00`, the observation for 12:00 UTC is the
  12:00 report — an **exact match, no offset at all**. So the rule fits CDG
  better than it fits EGLC, and needs no adapting for it (DECISIONS F18).

**The same rule is used at every airport, including where it costs days.** CDG
files an off-hour routine report more often than EGLC does — about 0.60% of
reports against 0.017% on the samples measured so far — and D14 correctly
refuses any report more than 15 minutes out, so those days are dropped and
counted. Widening the tolerance for one airport would mean stage 2 ran a
different pairing rule from stage 1, which would weaken the "only the location
changed" claim the whole comparison rests on. The drops are taken instead. See
DECISIONS Q19 and D30.

---

## 5. Evaluation protocol (FROZEN — do not change after seeing results)

**5.0 Scope: this protocol applies per airport.** The metric, the baselines and
the bar below are unchanged in meaning — this section says only *how widely*
they apply. Every airport is evaluated the same way, on its own data:

- its own rows on the shared split dates (4.3);
- its own rehearsal on the validation year, then **one** look at its own sealed
  test year;
- the same bar, judged **once per airport**.

An airport passes or fails on its own result. Nothing is pooled, averaged
across airports, or re-judged; a later airport's result does not change an
earlier one's, and an earlier pass does not excuse a later failure.

**Results so far:**

| airport | verdict | MAE degC: corrected vs raw GFS vs persistence |
|---|---|---|
| EGLC | **PASSED** (stage 1, 363 test days) | 1.040 vs 1.242 vs 2.096 |
| LFPG | pending — not yet run | — |

EGLC's figures are the stage 1 record: DECISIONS F16.

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
- **Mean-bias reference** (informative check, not part of the bar) — the raw
  GFS forecast plus one fixed number: GFS's average bias (observation minus
  forecast) measured on the training period only. It is the simplest possible
  correction — a single constant offset, no learning. Its job is to separate
  two very different results: a model that learned real structure in the bias
  beats it, while a model that merely found a constant offset does not. It is
  listed here because it proved the most informative of the comparisons (see
  DECISIONS F14).

The pass/fail bar is **raw GFS and persistence only** (section 5.3).
Climatology and the mean-bias reference are reported alongside because they
explain the result; they do not decide it. See DECISIONS D23.

**5.3 Success bar (qualitative, frozen before running).** An airport succeeds
if the corrected forecast has a lower MAE than **both raw GFS and
persistence**, over the held-out test period at that airport. The bar itself is
unchanged; the only things now made concrete are that the test period is the
fixed window 2025-08-01 to 2026-07-31, set before any model runs (section 4.3,
DECISIONS D13), and that the bar is applied once per airport (5.0). Stage 1
is EGLC passing this bar; stage 2 is CDG being put to the same one.

**The bar is qualitative, and it stays that way.** There is no numeric margin —
no minimum percent improvement, no minimum number of degrees. Beating raw GFS
and persistence on MAE over the test year is the whole of it.

An earlier version of this section left the door open to fixing a numeric
figure "just before the model is run". That door is now closed. Validation
results exist (DECISIONS F14, F15), so any number chosen now would be chosen in
the knowledge of what validation gave — which is not a clean before-the-fact
choice, and rule 2.4 exists precisely to stop bars being set to fit results.
Leaving the bar qualitative is the honest option. See DECISIONS D22.

**5.4 Deeper evaluation (available, optional, not a gate).** More thorough
checks — expressing results as a skill score, testing statistical significance,
testing formally whether the win holds across seasons — were parked until stage
1 passed. **Stage 1 has passed** (5.0, DECISIONS F16), so they are now
available.

They are **optional and block nothing.** Stage 1 passed cleanly rather than by
a hair, and its season-by-season breakdown already gives partial evidence that
the win is not carried by one lucky stretch of weather. So no later stage waits
on this work, and no session has to do it. If the owner asks for it, it is a
session of its own. See DECISIONS D29.

The stronger robustness check is running the same recipe at a second airport,
which is what stage 2 is.

---

## 6. Build order (each stage opens only when the previous one passes)

Stages 1 and 2 are fully specified above — the sections are written per
airport, so one set of rules covers both. **Stages 3 to 6 are intentionally
left as short descriptions only.** Do **not** write out their detailed design
until the project reaches them and the owner opens the stage. If a session tries
to fill in a later stage early, treat it as a warning sign and stop.

- **Stage 1 — one model, one airport, one fixed hour. DONE — PASSED.** EGLC.
  The correction beat both raw GFS and persistence on the sealed test year
  (5.0, DECISIONS F16).
- **Stage 2 — second airport (Charles de Gaulle, CDG / LFPG). IN PROGRESS.**
  Re-run the same recipe at a second location to prove stage 1 was not a fluke.
  Opened by DECISIONS D26. Its data was verified on contact (F17–F21) and its
  design is the per-airport wording in sections 1, 3, 4 and 5 above, plus its
  row in the airport table (3.4) — there is no separate stage 2 section, and
  that is the point: only the location changes.
- **Stage 3 — pool airports.** Combine airports into one model with
  location-describing features, so locations learn from each other. The target
  hour switches to solar standard noon here (4.1, DECISIONS D27).
- **Stage 4 — add models and blend.** Bring in other forecasts (ECMWF, ICON,
  and the Google WeatherNext AI model) and combine them. See the WeatherNext
  notes in DECISIONS.
- **Stage 5 — widen the target.** Move from one fixed hour to a full hourly
  temperature curve across the day ahead (the daily maximum then falls out as
  the peak of the curve). Add the 48-hour lead time alongside 24-hour.
- **Stage 6 — live product.** Point the proven model at today's fresh
  forecast, run it daily, and display a corrected temperature forecast for
  the day ahead, updated continuously.

*(Stages 3–6 have no sections of their own yet, and will not until the owner
opens them. Stage 2 needed no section: the sections above are written per
airport, so opening it meant adding a row to the airport table, not adding a
design.)*
