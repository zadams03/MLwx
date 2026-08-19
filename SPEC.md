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

The same recipe is run **one airport at a time**. What every airport shares is
the split dates, the method, and the frozen bar, judged once on that airport's
own test year. The **target hour is chosen per airport**, so that it falls at
that airport's local midday (section 4.1) — it is a per-airport fact, in the
same way the minute the station reports at is.

The airports so far:

- **London City (ICAO code EGLC)** — stage 1, **passed**.
- **Paris Charles de Gaulle (IATA code CDG, ICAO code LFPG)** — stage 2,
  **passed**.
- **Des Moines, Iowa (IEM station code DSM)** — stage 2, **passed**.
- **Dubbo, Australia (ICAO code YSDU)** — stage 2, **in progress**.

**The list is open-ended and more airports may follow.** Each airport's own
facts — its code, its position, the forecast grid point it maps to, when it
reports, and its target hour — live in the airport table in section 3.4.
Everything else in this file is shared by all of them.

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
no account needed. Each airport is requested by its station code (the first
column of the airport table, section 3.4); the routine report (IEM
`report_type=3`) is the truth observation.

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
(DECISIONS F20) — **and again at DSM**, on another continent, down to the same
hour and with the same all-null answer before it (DECISIONS F33). So the March
2021 floor is a property of the archive itself, not of one place, and the
section 4.3 split dates work at all three airports without adjustment.

The archive is **not continuous** at EGLC. From that start date to 2026-07-31
there is exactly one sizeable gap: **492 hours with no forecast value, from
2023-12-30 00:00 to 2024-01-19 11:00 UTC**. It falls entirely inside the
training window (the test window has no forecast gap at all). Those hours are
dropped and counted, never filled (rule 2.2). See DECISIONS F8, and F11 for the
correction to F1's earlier claim of continuity.

**CDG has the very same gap — verified, hour by hour.** Session 10 mapped every
hour of LFPG's forecast series the way session 03b did for EGLC, and found
**exactly one gap, 492 hours, from 2023-12-30 00:00 to 2024-01-19 11:00 UTC** —
the same first missing hour, the same last missing hour, the same length. It
falls entirely inside the training window at CDG too, and CDG's test window has
no forecast gap at all. So the gap is a property of the archive, not of one
place, in the same way the March 2021 floor is. Those hours are dropped and
counted, never filled (rule 2.2). See DECISIONS F22, which closes Q21.

**DSM has the very same gap too — verified, hour by hour.** Session 15 mapped
every hour of DSM's forecast series the way session 10 did for LFPG, and found
**exactly one gap, the same 492 hours, from 2023-12-30 00:00 to 2024-01-19
11:00 UTC**. Same first missing hour, same last missing hour, same length, and
again entirely inside the training window, with no forecast gap at all in the
test window. Three airports on two continents now share it hour for hour, so
the gap is a property of the Open-Meteo archive and not of any place. Those
hours are dropped and counted, never filled (rule 2.2). See DECISIONS F38.

**3.3 Verify on contact.** Two things can only be checked by pulling real
data, and must be checked on the first pull **for each new airport**:
- that the Previous Runs API actually returns history back to 2021 at that
  location (not just recent months);
- that the airport's observation record is complete enough over the chosen
  period, and at what minute past the hour it reports.

Both were checked for EGLC in session 01 (F1, F2, F3), for CDG in session 08
(F17–F21) and for DSM in session 14 (F31–F37). All three airports passed. At
DSM two further things were checked on contact, because it is the first airport
outside Europe: that the observation temperature field really is in degrees
Celsius, and that a request stamped UTC really is UTC. Both were measured
rather than assumed and both needed no new handling (DECISIONS F35).

The verify-on-contact samples at EGLC, CDG and DSM were pulled from the most
recent weeks available, which happened to fall inside the sealed test year
(2025-08-01 to 2026-07-31). **This is not leakage**: nothing was fitted on
those values, no method or feature choice was drawn from them, and the
accurate claim throughout has always been that **no test-year data influenced
any model, feature, or choice** — not that no test-year value was ever seen.
From Dubbo (session 19) onward, verification samples are drawn from outside
the test year on purpose, closing the wording gap for good (DECISIONS F49,
Q29).

**3.4 The airport table.** This is the only place per-airport facts are
written. Everything else in this file is shared. Adding an airport means adding
a row here, filled in from real pulls — never from memory or a map.

The airport, and where it is (position from IEM, section 3.1):

| station code | airport | stage | target hour (UTC) | IEM network | latitude | longitude | elevation |
|---|---|---|---|---|---|---|---|
| EGLC | London City | 1 — passed | 12:00 | `GB__ASOS` | 51.5053 | 0.0553 | 5 m |
| LFPG | Paris Charles de Gaulle (CDG) | 2 — passed | 12:00 | `FR__ASOS` | 49.0153 | 2.5344 | 109 m |
| DSM | Des Moines, Iowa | 2 — passed | 18:00 | `IA_ASOS` | 41.534 | -93.6531 | 294 m |
| YSDU | Dubbo, Australia | 2 — in progress | 02:00 | `AU__ASOS` | -32.2167 | 148.5747 | 275 m |

The forecast grid point it maps to (from Open-Meteo, section 3.2), and when the
station reports:

| station code | grid latitude | grid longitude | grid elevation | distance from airport | height mismatch | reports at | also files at | pairing offset |
|---|---|---|---|---|---|---|---|---|
| EGLC | 51.487137 | 0.0 | 4 m | 4.33 km | 1 m | `:50` | `:20` | 10 minutes |
| LFPG | 49.027008 | 2.578125 | 109 m | 3.44 km | 0 m | `:00` | `:30` | 0 minutes |
| DSM | 41.52945 | -93.63281 | 285 m | 1.76 km | -9 m | `:54` | nothing scheduled | 6 minutes |
| YSDU | -32.274643 | 148.59375 | 279 m | 6.69 km | +4 m | `:00` | `:30` | 0 minutes |

Notes on the table:

- **The code column holds whatever IEM addresses the station by** — resolving
  Q28. For EGLC and LFPG that is the ICAO code. For Des Moines it is IEM's own
  station id, **`DSM`, which is not an ICAO code** — IEM's Iowa listing carries
  no ICAO code for the station at all, in any field (checked in session 15
  against the saved listing). For Dubbo it is **`YSDU`, which is an ICAO
  code**. So the set is genuinely mixed — two ICAO codes, one non-ICAO station
  id, and now a third ICAO code that happens to coincide with IEM's own id —
  and no single word describes every entry correctly. The column heading is
  now **"station code"**, and section 3.1's wording says each airport is
  requested by its station code rather than by its ICAO code.
- **The airport position is IEM's own, not a figure from elsewhere.** IEM's
  record is treated as authoritative, because it is the same source the
  observations come from. For CDG this mattered: IEM's position sits 1.15 km
  from the approximate figure the session prompt carried, and IEM's was used
  (DECISIONS F17). DSM's position came from IEM's Iowa station listing the same
  way, pulled before any forecast request so nothing was typed in from a map
  (DECISIONS F31).
- **The grid point is whatever Open-Meteo returns** for that airport's
  position. A few kilometres of offset is not a fault — it is exactly the kind
  of steady local error this project exists to learn (DECISIONS Q5, F17). DSM's
  is the closest of the three, 1.76 km, and the first with a height mismatch
  worth naming at -9 m; 9 m is well inside the noise of a smoothed grid-cell
  elevation (DECISIONS F31).
- **"Reports at" is the minute past the hour the routine METAR is stamped**,
  and it is what makes the general pairing rule (4.5) concrete for that
  airport. **"Pairing offset"** follows from it: how far the paired observation
  sits from **that airport's own target hour** (4.1). EGLC, LFPG and YSDU also
  file a second scheduled report each hour, which IEM labels "special" although
  it is plainly scheduled; none of them is used as the truth observation
  (DECISIONS F3, F19, F55). **DSM files no such second scheduled report** — its
  "special" reports are spread across dozens of minutes and are genuinely
  unscheduled, which is why its "also files at" cell reads *nothing scheduled*
  (DECISIONS F36).
- **All four network codes are now verified by a real pull.** LFPG's
  `FR__ASOS` was checked in session 08 (DECISIONS F17), EGLC's `GB__ASOS` in
  session 10 (DECISIONS F24, which closes Q22), DSM's `IA_ASOS` in session 14
  (DECISIONS F31) and YSDU's `AU__ASOS` in session 19 (DECISIONS F49). In each
  case IEM's own station listing carries the station in that network, at the
  position and elevation this table holds. Nothing in the project uses a
  network code — every request addresses its station by the code in the first
  column — so this closes a bookkeeping gap, not a data one.

---

## 4. The target and the method

**4.1 Target.** The temperature at **one fixed hour of the day**, and that hour
is **chosen per airport, so that it falls at that airport's local midday**. The
hour each airport uses is a per-airport fact and lives in the airport table
(section 3.4). One hour a day is deliberately the simplest clean target — the
honest test of whether the whole idea works at all. Widening to more hours comes
later (section 6).

The hours in use:

- **EGLC and LFPG use 12:00 UTC.** Local standard time in western Europe is
  UTC+0 and UTC+1, so 12:00 UTC is midday to early afternoon at both.
- **DSM uses 18:00 UTC**, which is 12:00 Central Standard Time — local standard
  noon at Des Moines. 12:00 UTC there would be 06:00 local, which is dawn: the
  one part of the day the reasons below rule out. Checked against the timezone
  database rather than assumed (DECISIONS D33, F32).

**Daylight saving is deliberately ignored**, so each airport's target stays a
fixed UTC hour all year round and there is no seasonal jump in the middle of the
data. At 18:00 UTC the clock at Des Moines reads 12:00 in winter and 13:00 in
summer; the sun sits at a comparable height either way.

Why local midday was chosen (decided on principle, before any model was built or
any performance seen):
- It is in daylight, so it catches the daytime heating that GFS tends to
  mis-handle. A night-time hour would test the easier part of the day.
- It is a stable, well-observed time of day — the station reports it reliably
  and the temperature is not moving fast.
- It avoids dawn and dusk, when temperature swings quickest and the pairing
  offset (4.5) would matter most.

**All three reasons are about the local time of day, not about the number
12:00.** That is why the hour moves with the airport instead of staying fixed in
UTC. At the two European airports the two happen to coincide, which is why
stages 1 and 2's first two airports could use a single hour without anyone
having to choose between the two ideas.

**This is the solar-standard-noon convention, brought forward.** DECISIONS D27
wrote that convention down for stage 3, when airports are pooled, and said it
was not applied to stage 1 or stage 2. DSM needed it earlier, for the reason D27
already gave: 12:00 UTC is a different time of day at each location, which is
harmless across the 328 km between London and Paris and wrong across an ocean.
So the convention is in use **from DSM onwards** (DECISIONS D33), and the two
European airports keep 12:00 UTC because that already is their local midday.

**The honest cost, stated plainly.** DECISIONS D26 said stage 2 changes the
**location and nothing else**, so that if a result differs, the location is the
only thing that can explain it. That claim still holds **within western
Europe** — EGLC and LFPG were run at the same hour and differ only in place. It
does **not** hold for DSM: against the European pair, DSM changes the location
**and** the target hour together. A DSM result answers "does the recipe travel
to a different region at a comparable local time", and it must not be quoted as
if it were the same controlled comparison EGLC and LFPG make between them
(DECISIONS D33).

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

The rule names no minute and no hour, because both are per-airport facts and
live in the airport table (3.4). **The hour being paired is each airport's own
target hour (4.1), not one hour shared by all of them.** What the rule means in
practice:

- At **EGLC**, which reports at `:50`, the observation for 12:00 UTC is the
  11:50 report — ten minutes earlier. Ten minutes is a negligible gap for
  temperature, which is the argument D14 rests on.
- At **LFPG**, which reports at `:00`, the observation for 12:00 UTC is the
  12:00 report — an **exact match, no offset at all**. So the rule fits CDG
  better than it fits EGLC, and needs no adapting for it (DECISIONS F18).
- At **DSM**, which reports at `:54`, the observation for its 18:00 UTC target
  is the **17:54 report — six minutes earlier**. The next report, 18:54, is 54
  minutes out, so the rule picks 17:54 without ambiguity. Six minutes is a
  smaller gap than EGLC's ten, so D14's argument covers it comfortably and the
  rule again needs no adapting (DECISIONS F34).

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
| LFPG | **PASSED** (stage 2, 363 test days) | 1.208 vs 1.396 vs 2.300 |
| DSM | **PASSED** (stage 2, 365 test days) | 1.700 vs 1.815 vs 4.003 |

EGLC's figures are the stage 1 record (DECISIONS F16), LFPG's the stage 2
record for its airport (DECISIONS F30), and DSM's the stage 2 record for its
airport (DECISIONS F47). All three airports' single authorised looks are now
spent, and all three fell on **the same twelve months**, so the three margins
are not three independent draws of weather — see F30's and F48's closing
readings. DSM also changed its target hour against the European pair (4.1), so
its result is not the same controlled comparison EGLC and LFPG make between
them.

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
is EGLC passing this bar; stage 2 is **each further individual airport put to
the same bar, one at a time** — CDG, then DSM, then any that follow. The bar
does not change from one airport to the next, and neither does what it
requires.

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
airport, so one set of rules covers every airport in either of them. **Stages 3
to 6 are intentionally left as short descriptions only.** Do **not** write out their detailed design
until the project reaches them and the owner opens the stage. If a session tries
to fill in a later stage early, treat it as a warning sign and stop.

- **Stage 1 — one model, one airport, one fixed hour. DONE — PASSED.** EGLC.
  The correction beat both raw GFS and persistence on the sealed test year
  (5.0, DECISIONS F16).
- **Stage 2 — individual airports, two or more. IN PROGRESS.** Re-run the same
  recipe at further locations, one airport at a time, each judged on its own
  sealed test year, to prove stage 1 was not a fluke and to find out how far
  the recipe travels. Opened at Charles de Gaulle by DECISIONS D26 and widened
  to an open-ended list of airports by D32. There is no separate stage 2
  section and that is the point: sections 1, 3, 4 and 5 are written per airport,
  so opening an airport means adding a row to the table (3.4), not adding a
  design.
  - **CDG (LFPG) — PASSED.** Verified on contact (F17–F21), pulled and mapped
    (F22–F26), rehearsed (F27–F29), locked (D31) and tested once (F30).
  - **Des Moines (DSM) — PASSED.** Opened by D32, verified on contact
    (F31–F37), pulled and mapped (F38–F41), joined and rehearsed (F42–F46),
    locked (D35) and tested once (F47). It is the first airport outside
    western Europe, and the first whose target hour is not 12:00 UTC (D33,
    4.1).
  - **Dubbo (YSDU) — IN PROGRESS.** Opened by D36, verified on contact
    (F49–F56). It is the project's first Southern Hemisphere airport, and the
    second whose target hour is not 12:00 UTC (D37, 4.1).
  - **Further airports may follow before stage 3**, on the same five steps:
    verify on contact, pull and map, join and rehearse, lock, test once.
- **Stage 3 — pool airports.** Combine airports into one model with
  location-describing features, so locations learn from each other. **The
  solar-standard-noon target hour this stage was going to introduce is already
  in use, from DSM onwards** (4.1, DECISIONS D27, D33), so stage 3 inherits it
  rather than switching to it.
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
opens them. Stage 2 needs no section of its own, however many airports it comes
to hold: the sections above are written per airport, so opening one means
adding a row to the airport table, not adding a design.)*
