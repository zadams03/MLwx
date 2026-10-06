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
the split dates, the method, and the frozen bar. Each airport is judged on
its own held-out data: one look at each of the five earlier airports, two
pre-registered looks at KSFO, and, for any later airport, whatever looks its
lock fixes in writing before any of its held-out values are read (section
5.0). The **target hour is chosen per airport**, so that it falls at
that airport's local midday (section 4.1) — it is a per-airport fact, in the
same way the minute the station reports at is.

The airports so far:

- **London City (ICAO code EGLC)** — stage 1, **passed**.
- **Paris Charles de Gaulle (IATA code CDG, ICAO code LFPG)** — stage 2,
  **passed**.
- **Des Moines, Iowa (IEM station code DSM)** — stage 2, **passed**.
- **Dubbo, Australia (ICAO code YSDU)** — stage 2, **passed**.
- **Reno, Nevada (IEM station code RNO, ICAO code KRNO)** — stage 2,
  **failed the minimal method** (DECISIONS F82); **passes the richer
  5-feature GRIB method** (DECISIONS F94) — see section 7; **also passes
  the selected-features method** (DECISIONS F109) — see section 8. The
  project's first mountain/terrain-affected airport.
- **San Francisco International (IEM station code SFO, ICAO code KSFO)** —
  stage 2, **passes the selected-features method** on both of its
  pre-registered looks (DECISIONS F119, D71) — see section 8. The project's
  first coastal airport. Its GRIB-vs-Open-Meteo reproduction gate failed,
  explained by a difference between the sources (DECISIONS F116, F117,
  D69). Its result is for the recipe at a sea-mixed grid point and is not
  directly comparable with the five airports above (DECISIONS D71.5).

**The list is open-ended and more airports may follow.** Each airport's own
facts — its code, its position, the forecast grid point it maps to, when it
reports, and its target hour — live in the airport table in section 3.4.
Everything else in this file is shared by all of them.

The end goal is a private, live tool for ten or more airports that
corrects every GFS run (four a day), as each run arrives, into an
hourly temperature curve out to the forecast horizon, plus the daily
maximum. The horizon is 24 hours first and 48 hours later. Then come
a choice of which weather model is corrected, plus a blend, and
probabilistic ranges (DECISIONS D72.1, reworded by D82.2). That is
the destination, not the starting point. See section 6 for the
roadmap.

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
  reasoning.) **Section 7's richer method uses a different source (a GFS
  GRIB archive) and satisfies this same rule by a different route**: it
  reads a genuine archived past forecast run at a fixed forecast-hour lead,
  never the freshest run for a given valid time, so no future-stitching is
  possible there either (DECISIONS F89). This does not change what the
  method in sections 1–6 uses — Open-Meteo's Previous Runs API remains its
  source.
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

**2.5 Claims and build choices (DECISIONS D72.2).** Two kinds of
decision are treated differently.

- A **claim** is a stated result, for example "beats raw GFS by X%".
  A claim needs a test on held-out data that nothing else has used,
  with the method, the data and the pass rule fixed in writing first,
  and one look.
- A **build choice** is how the product is made: which inputs, which
  settings, how models are blended. A build choice is made by
  cross-validation (training on some past years and testing on later
  ones, in time order, 2.1a) on data that is not held out for any
  claim. It spends no held-out data and is never quoted as a result.
- Held out for claims, and so never used for build choices: a
  pre-registered test's data until that test is run; 2026-27 or later
  data until its pre-registered test is scored; and a new airport's
  held-out years until its looks are run.
- Once any part of a forward year has been scored, no new test may be
  pre-registered on that year.
- Build choices are made identically at every airport. Choosing
  features or settings per airport is still not allowed.

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
**`gfs_global`** (see DECISIONS D16). Free, no account needed. This section
describes the source for the method in sections 1–6. Section 7 describes a
second, later method with its own forecast source (a GFS GRIB archive); the
rest of this section (lead time, archive floor, the shared gap) is about the
Open-Meteo source only, unless section 7 says otherwise.

The lead time is the API's 1-day offset (`previous_day1`). This is a
**nominal** 24-hour lead, not an exact one. GFS runs every 6 hours, and
Open-Meteo builds the series by taking hours 24–29 of each run and stitching
them together, so the true lead sweeps between about **24 and 30 hours**
across the day and then resets (see DECISIONS F5).

**Which GFS product.** Open-Meteo's documentation (pulled 2026-09-26)
marks `temperature_2m` under this model as coming from GFS's
high-resolution 0.11° product, not the 0.25° product that sections 7 and 8
use (DECISIONS F117.4). The page describes the service on that date. It
does not say which product built the 2021–2024 archive.

Every value is nonetheless a genuine forecast made **at least 24 hours before
its valid time**, so the no-look-ahead rule (2.1b) still holds.

Confirmed available back to **24 March 2021**. (A request for 1 March 2021
returns HTTP 200 with every value null; the first hour carrying a real value
is 2021-03-24 00:00 UTC. See DECISIONS F1.) **The same first hour was found at
CDG** — 2021-03-24 00:00 UTC exactly, with the same all-null answer before it
(DECISIONS F20) — **and again at DSM**, on another continent, down to the same
hour and with the same all-null answer before it (DECISIONS F33). So the March
2021 floor is a property of the archive itself, not of one place, and the
section 4.3 split dates work at every airport pulled so far without
adjustment. Reno's own full pull (session 26) begins exactly at 2021-03-24
00:00 UTC too, with no null values inside the requested period, consistent
with the same floor (DECISIONS F75); the all-null probe *before* that date
was not separately repeated for Reno, since the full pull itself only asks
for dates on or after the floor. KSFO's verify-on-contact probe (session 76)
found the same first hour, 2021-03-24 00:00 UTC, with the same all-null
answer before it (DECISIONS F116).

**The archive is not continuous.** From the start date to 2026-07-31 there is
exactly one sizeable gap: **492 hours with no forecast value, from 2023-12-30
00:00 to 2024-01-19 11:00 UTC**. It falls entirely inside the training window
(no airport's test window has a forecast gap). Those hours are dropped and
counted, never filled (rule 2.2). It has now been verified **hour by hour, at
every airport pulled so far — EGLC, CDG, DSM, Dubbo, Reno and KSFO — same
start hour, same end hour, same length, across Europe, North America and
Australia** (DECISIONS
F8, and F11 for the correction to F1's earlier claim of continuity; F22,
closing Q21; F38; F57; F75; F116). It is a property of the Open-Meteo archive
itself, not of any one place. See each airport's own DECISIONS finding for
the hour-by-hour specifics.

**3.3 Verify on contact.** Two things can only be checked by pulling real
data, and must be checked on the first pull **for each new airport**:
- that the Previous Runs API actually returns history back to 2021 at that
  location (not just recent months);
- that the airport's observation record is complete enough over the chosen
  period, and at what minute past the hour it reports.

Both were checked for EGLC in session 01 (F1, F2, F3), for CDG in session 08
(F17–F21), for DSM in session 14 (F31–F37) and for Dubbo in session 19
(F49–F56). All four airports passed. At DSM two further things were checked
on contact, because it is the first airport outside Europe: that the
observation temperature field really is in degrees Celsius, and that a
request stamped UTC really is UTC. Both were measured rather than assumed and
both needed no new handling (DECISIONS F35).

**Reno's verify-on-contact was done in two steps, across two sessions, and is
honestly a partial case.** Session 25 checked Reno alongside Bozeman as
mountain-valley candidates, but only to candidate-comparison depth — station
position, grid point, grid-elevation mismatch, and reporting minute on a
short sample (DECISIONS F66) — before choosing Bozeman. The owner then
switched the fifth airport to Reno (DECISIONS D42, superseding D40). Session
26's full six-year pull confirmed the archive floor and the shared 492-hour
gap at Reno (DECISIONS F75) and mapped the target-hour pairing across the
whole period (DECISIONS F76, F77), which is deeper than a verify-on-contact
sample but does not include Bozeman's full checklist — in particular, whether
Reno files a second scheduled report (SPEC 3.4's "also files at" column) has
not been checked by any session (see SPEC 3.4's notes).

The verify-on-contact samples at EGLC, CDG and DSM were pulled from the most
recent weeks available, which happened to fall inside the sealed test year
(2025-08-01 to 2026-07-31). **This is not leakage**: nothing was fitted on
those values, no method or feature choice was drawn from them, and the
accurate claim throughout has always been that **no test-year data influenced
any model, feature, or choice** — not that no test-year value was ever seen.
From Dubbo (session 19) onward, verification samples are drawn from outside
the test year on purpose, closing the wording gap for good (DECISIONS F49,
Q29).

**KSFO was verified on contact in session 76**, from samples outside its
held-out range 2024-08-01..2026-07-31: station position, target hour,
reporting minute and second report, units, UTC stamps, grid point, archive
floor, and its GRIB elevation constant (DECISIONS F116). The reproduction
gate that checks its GRIB temperature and constant against Open-Meteo
failed (DECISIONS F116). The owner recorded it as failed, explained by a
difference between the sources, with no override (DECISIONS F117, D69).

**3.4 The airport table.** This is the only place per-airport facts are
written. Everything else in this file is shared. Adding an airport means adding
a row here, filled in from real pulls — never from memory or a map.

The airport, and where it is (position from IEM, section 3.1):

| station code | airport | stage | target hour (UTC) | IEM network | latitude | longitude | elevation |
|---|---|---|---|---|---|---|---|
| EGLC | London City | 1 — passed | 12:00 | `GB__ASOS` | 51.5053 | 0.0553 | 5 m |
| LFPG | Paris Charles de Gaulle (CDG) | 2 — passed | 12:00 | `FR__ASOS` | 49.0153 | 2.5344 | 109 m |
| DSM | Des Moines, Iowa | 2 — passed | 18:00 | `IA_ASOS` | 41.534 | -93.6531 | 294 m |
| YSDU | Dubbo, Australia | 2 — passed | 02:00 | `AU__ASOS` | -32.2167 | 148.5747 | 275 m |
| RNO | Reno, Nevada | 2 — failed (minimal method)\* | 20:00 | `NV_ASOS` | 39.4839 | -119.7711 | 1345 m |
| SFO | San Francisco International (KSFO) | 2 — passed (selected-features method) | 20:00 | `CA_ASOS` | 37.619 | -122.3749 | 5 m |

\* Reno failed the minimal method (DECISIONS F82). It passes the richer
method (section 7, DECISIONS F94) and the selected method (section 8,
DECISIONS F109).

The forecast grid point it maps to (from Open-Meteo, section 3.2), and when the
station reports:

| station code | grid latitude | grid longitude | grid elevation | distance from airport | height mismatch | reports at | also files at | pairing offset |
|---|---|---|---|---|---|---|---|---|
| EGLC | 51.487137 | 0.0 | 4 m | 4.33 km | 1 m | `:50` | `:20` | 10 minutes |
| LFPG | 49.027008 | 2.578125 | 109 m | 3.44 km | 0 m | `:00` | `:30` | 0 minutes |
| DSM | 41.52945 | -93.63281 | 285 m | 1.76 km | -9 m | `:54` | nothing scheduled | 6 minutes |
| YSDU | -32.274643 | 148.59375 | 279 m | 6.69 km | +4 m | `:00` | `:30` | 0 minutes |
| RNO | 39.537918 | -119.765625 | 1344 m | 6.02 km | -1 m | `:55` | not yet checked | 5 minutes |
| SFO | 37.54637 | -122.34375 | 1 m | 8.53 km | -4 m | `:56` | nothing scheduled | 4 minutes |

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
  requested by its station code rather than by its ICAO code. For Reno it is
  **`RNO`, also not an ICAO code** — Reno's ICAO code is `KRNO` (DECISIONS
  F66), the same non-ICAO-station-id situation as DSM.
- **The airport position is IEM's own, not a figure from elsewhere.** IEM's
  record is treated as authoritative, because it is the same source the
  observations come from. For CDG this mattered: IEM's position sits 1.15 km
  from the approximate figure the session prompt carried, and IEM's was used
  (DECISIONS F17). DSM's position came from IEM's Iowa station listing the same
  way, pulled before any forecast request so nothing was typed in from a map
  (DECISIONS F31). Reno's position came from IEM's Nevada (`NV_ASOS`) station
  listing the same way, pulled in session 25 before any forecast request for
  it was made (DECISIONS F66).
- **The grid point is whatever Open-Meteo returns** for that airport's
  position. A few kilometres of offset is not a fault — it is exactly the kind
  of steady local error this project exists to learn (DECISIONS Q5, F17). DSM's
  is the closest of the six, 1.76 km, and the first with a height mismatch
  worth naming at -9 m; 9 m is well inside the noise of a smoothed grid-cell
  elevation (DECISIONS F31). **Reno is by far the highest-elevation airport in
  the project (1,345 m), yet its grid-elevation mismatch is the smallest of
  any airport so far, -1 m** — real but negligible (DECISIONS F66). Reno's
  difficulty as a terrain test, if any, is expected to come from horizontal
  terrain complexity (the nearby Sierra Nevada front), not from this vertical
  mismatch — see DECISIONS D42.
- **"Reports at" is the minute past the hour the routine METAR is stamped**,
  and it is what makes the general pairing rule (4.5) concrete for that
  airport. **"Pairing offset"** follows from it: how far the paired observation
  sits from **that airport's own target hour** (4.1). EGLC, LFPG and YSDU also
  file a second scheduled report each hour, which IEM labels "special" although
  it is plainly scheduled; none of them is used as the truth observation
  (DECISIONS F3, F19, F55). **DSM files no such second scheduled report** — its
  "special" reports are spread across dozens of minutes and are genuinely
  unscheduled, which is why its "also files at" cell reads *nothing scheduled*
  (DECISIONS F36). **Reno's "also files at" cell reads "not yet checked"** —
  session 25's verification of Reno went only as deep as the candidate
  comparison against Bozeman (position, grid, elevation mismatch, reporting
  minute on a short sample); whether Reno files a second scheduled report has
  not been pulled or checked by any session, and the question was closed as
  immaterial rather than pursued further (DECISIONS F83) — nothing in the
  project's pipeline uses the "special" stream as the truth observation at
  any airport (D30), so the cell stays an honest "not yet checked" rather
  than a guess.
- **KSFO (session 76, DECISIONS F116).** IEM's code is **`SFO`, not an
  ICAO code** (the ICAO code is KSFO), the same situation as DSM and RNO.
  Its position came from IEM's `CA_ASOS` listing. Its grid point is the
  farthest from its airport so far, 8.53 km. Its "special" reports are
  spread across many minutes, so its "also files at" cell reads *nothing
  scheduled*, as at DSM. **KSFO's GRIB elevation constant is +0.6944 °C**:
  the GRIB model terrain at its grid point is 94.47 m against the grid
  elevation of 1 m, a gap of 93.47 m, times the frozen 7.429 °C/km (7.2).
  It is in 5.2's list (DECISIONS D70). Its four surrounding 0.25° GRIB
  points are two sea points (weight 0.375) and two land points (0.625)
  (DECISIONS F117). Its reproduction gate failed, explained by a
  difference between the sources (DECISIONS F116, F117, D69).
- **All six network codes are now verified by a real pull.** LFPG's
  `FR__ASOS` was checked in session 08 (DECISIONS F17), EGLC's `GB__ASOS` in
  session 10 (DECISIONS F24, which closes Q22), DSM's `IA_ASOS` in session 14
  (DECISIONS F31), YSDU's `AU__ASOS` in session 19 (DECISIONS F49), RNO's
  `NV_ASOS` in session 25 (DECISIONS F66) and SFO's `CA_ASOS` in session 76
  (DECISIONS F116). In each case IEM's own station
  listing carries the station in that network, at the position and elevation
  this table holds. Nothing in the project uses a network code — every
  request addresses its station by the code in the first column — so this
  closes a bookkeeping gap, not a data one.

---

## 4. The target and the method

**4.1 Target.** The temperature at **one fixed hour of the day**, and that hour
is **chosen per airport, so that it falls at that airport's local midday**. The
hour each airport uses is a per-airport fact and lives in the airport table
(section 3.4). One hour a day is deliberately the simplest clean target — the
honest test of whether the whole idea works at all. Widening to more hours comes
later (section 6).

**For illustration, not as a second source of truth** (section 3.4's table is
the only place the hours themselves are recorded): EGLC and LFPG both land on
12:00 UTC because that already is local midday in western Europe (UTC+0 and
UTC+1). DSM does not: its standard-time offset is UTC−6, so 12:00 UTC there
is 06:00 local — dawn, the one part of the day the reasons below rule out —
which is why DSM instead uses 18:00 UTC (local standard noon), checked
against the timezone database rather than assumed (DECISIONS D33, F32).
Dubbo (02:00 UTC, DECISIONS D37) and Reno (20:00 UTC, DECISIONS D42) follow
the same local-standard-noon principle, each checked against the timezone
database in its own session before being used.

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
seasons. For the record's methods (sections 1–6, 7 and 8), data after
2026-07-31 is not used, which keeps the test set exactly one calendar year.
The 2026-27 forward year is governed by DECISIONS D73. These dates are fixed
before any model runs (see DECISIONS D13).

**These dates are shared by every airport.** They are not re-chosen per
location. CDG's forecast archive begins on the same hour as EGLC's, 2021-03-24
00:00 UTC (section 3.2, DECISIONS F20), so the dates need no adjusting for it.
Each airport has its own train and test *rows* on those shared dates, and its
own held-out data, looked at only as section 5.0 sets out: one look at each
of the five earlier airports, two pre-registered looks at KSFO (DECISIONS
D67.3), and, for any later airport, whatever its lock fixes in writing.

Inside the training window there is a further subdivision used for rehearsal —
inner-training 2021-03-24 to 2024-07-31 and a validation year 2024-08-01 to
2025-07-31 — so the method can be tried out without touching the sealed test
year. The test model is then refitted on the whole training window. This
applies per airport too. See DECISIONS D18 and D21.5. **KSFO is the
exception:** its rehearsal used the `2022-23` and `2023-24` folds of
DECISIONS D51's `EXPERIMENT_FOLDS` instead, because 2024-25 was one of its
looks (DECISIONS D67.4).

**4.4 Model type.** A gradient-boosted tree model (a standard model for
table-shaped data). This runs on a normal laptop CPU; no GPU is needed.

**4.5 Lining up observation and forecast in time.** Each forecast valid at
`HH:00` is paired with the station's **nearest routine report to that hour**.
If no report falls within 15 minutes of the hour, that hour is dropped and
counted (rule 2.2). See DECISIONS D14.

**What the historical code actually does (DECISIONS D62).** The scripts
behind every recorded result keep the **last** qualifying report in the
file, not explicitly the nearest. The two rules differ only when two or
more usable reports fall within the 15-minute window on the same day. That
happened on 1 day in the whole record (YSDU), with equal temperatures, so
no recorded figure is affected (audit-67 A67-12, audit-68b item 9). New
code must select the nearest report explicitly (8.7).

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
- its own rehearsal (4.3), then its own look or looks at held-out data:
  **one** look at its own sealed test year at each of the five earlier
  airports; **two** pre-registered looks at KSFO, each judged separately
  (DECISIONS D67.3, D70.3, D70.4); and, for any later airport, the number
  of looks, their windows and how their verdicts combine, fixed in writing
  in its lock before any of its held-out values are read (DECISIONS D71.6);
- the same bar, judged **once per look**.

**When an airport has more than one look, it passes only if every look
passes; anything else is recorded as a split or a fail** (DECISIONS D71.6).
This records existing practice. It changes no earlier result.

An airport passes or fails on its own result. Nothing is pooled, averaged
across airports, or re-judged; a later airport's result does not change an
earlier one's, and an earlier pass does not excuse a later failure.

**Results so far:**

| airport | verdict | MAE degC: corrected vs raw GFS vs persistence |
|---|---|---|
| EGLC | **PASSED** (stage 1, 363 test days) | 1.040 vs 1.242 vs 2.096 |
| LFPG | **PASSED** (stage 2, 363 test days) | 1.208 vs 1.396 vs 2.300 |
| DSM | **PASSED** (stage 2, 365 test days) | 1.700 vs 1.815 vs 4.003 |
| YSDU | **PASSED** (stage 2, 347 test days) | 1.210 vs 1.251 vs 2.669 |
| RNO | **FAILED** (stage 2, 365 test days) | 1.458 vs 1.414 vs 2.490 |

EGLC's figures are the stage 1 record (DECISIONS F16), LFPG's the stage 2
record for its airport (DECISIONS F30), DSM's the stage 2 record for its
airport (DECISIONS F47), YSDU's (Dubbo's) the stage 2 record for its
airport (DECISIONS F64), and RNO's (Reno's) the stage 2 record for its
airport (DECISIONS F82). All five airports' single authorised looks are now
spent, and all five fell on **the same twelve months**, so the margins are
not five independent draws of weather — see F30's, F48's and F65's closing
readings. DSM, Dubbo and Reno each changed their target hour against the
European pair (4.1), so none of their results is the same controlled
comparison EGLC and LFPG make between them.

**RNO (Reno) is the first airport not to beat raw GFS** — it fails the
raw-GFS half of the bar (1.458 vs 1.414, -3.1%) while still beating
persistence by a wide margin (1.458 vs 2.490, +41.4%). The failure was named
in advance, before the test year was opened, as the expected outcome if the
method's minimal features proved insufficient there (DECISIONS D44.12):
Reno's bias is close to a constant offset, and the correctable structure left
over is small relative to random day-to-day scatter, so a flexible model
fitting it tightly in-sample adds little out-of-sample. See DECISIONS F82.

**A separate, richer-feature method has since been tested against this same
frozen bar, with its own results table — see section 7.** It does not
replace or re-judge anything in the table above; the results above are the
record of the method described in sections 1–6, and they stand unchanged
(DECISIONS D48.13).

**5.1 Metric.** Mean absolute error (MAE) — the average size of the gap
between forecast and what actually happened, in degrees Celsius. Lower is
better.

**5.2 Baselines to beat.** The corrected forecast is compared against:
- **Raw GFS** — the GFS forecast *before this project's model corrects
  it*. Beating this is the core claim of the project. What "raw" means
  depends on the method (DECISIONS D62):
  - **Minimal method (sections 1–6):** the GFS value as Open-Meteo serves
    it, with no adjustment by this project.
  - **GRIB methods (sections 7 and 8):** the GRIB 2 m temperature after
    this project's fixed per-airport elevation adjustment (DECISIONS
    D48.3). This was pre-registered as the baseline in DECISIONS D48.10.
    The adjustments, in °C: EGLC +0.2486, LFPG −0.1697, DSM −0.1106, YSDU
    +0.2461, RNO +2.0436 (`correction_c` in
    `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`),
    and KSFO +0.6944
    (`data/raw/diagnostics/session76/session76_elevation_correction_params.csv`;
    DECISIONS F116, D70).

  The margins of the GRIB methods against a fully unadjusted GRIB baseline
  were never measured. At the five earlier airports they cannot be
  measured now, because both held-out years are spent there (DECISIONS
  D59.5). At KSFO no unadjusted rung was registered in its lock (DECISIONS
  D70), so it was not measured there either.
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
DECISIONS D13), and that the bar is applied once per look (5.0). (Scope:
the test period named here is the sealed year used by the minimal and
richer methods. The selected-features method's confirmation year and
KSFO's looks are set out in 8.3 and 8.5.) Stage 1
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

**They were scheduled as part of roadmap stage A** (section 6,
DECISIONS D72.3). The confidence intervals for the results on record are
done (DECISIONS F125; RESULTS 6.6). The comparison against operational
post-processed forecasts is recorded in DECISIONS F127 (outcome rule
D77.4). They change
no earlier verdict. Stage A's own gate (DECISIONS D72.7) decides the
project's direction, not any airport's pass or fail.

The stronger robustness check is running the same recipe at a second airport,
which is what stage 2 is.

---

## 6. Build order and roadmap (DECISIONS D72)

Stages 1 and 2 are fully specified above — the sections are written per
airport, so one set of rules covers every airport in either of them. **The
roadmap stages after stage 2 are intentionally left as short descriptions
only** (DECISIONS D72). Do **not** write out their detailed design until the
owner opens each one. If a session tries to fill in a later stage early, treat
it as a warning sign and stop.

- **Stage 1 — one model, one airport, one fixed hour. DONE — PASSED.** EGLC.
  The correction beat both raw GFS and persistence on the sealed test year
  (5.0, DECISIONS F16).
- **Stage 2 — individual airports, two or more. ONGOING (the new-airports
  track, DECISIONS D72.3).** Re-run the same
  recipe at further locations, one airport at a time, each judged on its own
  held-out data, in the look or looks its lock fixes (5.0), to prove stage
  1 was not a fluke and to find out how far
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
  - **Dubbo (YSDU) — PASSED.** Opened by D36, verified on contact (F49–F56),
    pulled and mapped (F57–F59), joined and rehearsed (F60–F63), locked (D39)
    and tested once (F64). It is the project's first Southern Hemisphere
    airport, and the second whose target hour is not 12:00 UTC (D37, 4.1).
  - **Reno (RNO) — FAILED (tested once, F82).** Session 25 verified two
    mountain-valley candidates, Bozeman and Reno, and initially chose Bozeman
    (D40); the owner then switched the choice to Reno (D42, superseding
    D40). Reno's candidate-comparison checks are recorded in F66, its full
    pull and gap map are in F74–F77, and it was joined and rehearsed in
    session 27 (F78–F81) — the rehearsal correction did **not** beat raw GFS
    (1.499 vs 1.493, -0.4%), the first such rehearsal result in the project,
    though it still beat persistence and, narrowly, the mean-bias reference.
    Its method lock, mirroring D39's, is **D44** (session 28) — the recipe
    is unchanged despite the rehearsal loss, and D44.12 named the
    near-constant-bias / overfit pattern as the expected explanation if the
    sealed test also failed. Session 29 opened the sealed test once: **RNO
    DOES NOT PASS** — the corrected forecast does not beat raw GFS (1.458 vs
    1.414, -3.1%), though it beats persistence by a wide margin (+41.4%,
    F82). It is the project's first airport to fail the frozen bar, the
    project's first mountain/terrain-affected airport, and the third whose
    target hour is not 12:00 UTC (D42, 4.1). **A separate, richer 5-feature
    GRIB method (section 7) was built and tested later, and passes at Reno
    too (DECISIONS F94)** — this does not change or erase the record above;
    both results stand (D48.13). **The selected-features method (section
    8) also passes at Reno (DECISIONS F109).**
  - **San Francisco International (SFO/KSFO) — passed (selected-features
    method).**
    Opened by D67 under the default recipe (8.7), with two pre-registered
    looks, 2024-25 and 2025-26, each judged separately (D67.3). Verified on
    contact, pulled and built in session 76 (F116). **Its GRIB-vs-Open-
    Meteo reproduction gate (F89/F90) failed** (F116): the elevation-
    adjusted GRIB temperature runs 3.3 °C colder than Open-Meteo on
    average, most in summer. The owner recorded the gate as failed,
    explained by a difference between the sources, and kept the recipe
    unchanged (DECISIONS D69). Rehearsed and locked in session 77
    (DECISIONS F118, D70). Its two looks were run once, in session 78, and
    **both pass** (DECISIONS F119). The owner accepted the result as a
    PASS (DECISIONS D71). The headline is look A's margin over raw GFS
    (GRIB): 1.2576 vs 1.4263 °C, +11.83% (8.5, 8.6(f)). It is
    the project's first coastal airport. Its target
    hour, 20:00 UTC, and its lead are Reno's.
  - **Further airports may follow at any point in the roadmap**, on the
    same five steps: verify on contact, pull and map, join and rehearse,
    lock, test. The lock fixes in writing how many looks there are, their
    windows and how their verdicts combine, before any held-out value is
    read, and each look is run once (5.0, DECISIONS D71.6). Each uses the
    project's default recipe (8.7). From stage G, adding an airport should
    take one script plus a checklist, and the script downloads its history
    (DECISIONS D72.2).

**The roadmap after stage 2 (DECISIONS D72).** The end goal is set out
in section 1. Stages run in this order. Stages A and B run side by
side, because both are time-critical.

- **Stage A — benchmark and source probe.** Confidence intervals for
  the results on record (5.4). A comparison against operational
  post-processed forecasts (NWS MOS and the National Blend of Models,
  NBM) at DSM, RNO and SFO; its outcome rule is fixed in writing before
  it is looked at (DECISIONS D72.7). A read-only probe of each other
  source (ECMWF, ICON, WeatherNext, NBM, GEFS): archive depth, live
  feed, and which fields it offers. The confidence intervals (F125) and
  the source probe (F123, F124) are done. The outcome rule is fixed in
  DECISIONS D77, and the comparison on the spent years is recorded in
  F127. The direction decision is recorded in DECISIONS D78.1: option (d),
  neither; the roadmap carries on as D72 sets it.
- **Stage B — forward test and data collection.** Pre-register the
  2026-27 forward test of section 8's recipe on GFS, split at the GFS
  v17 go-live date (DECISIONS D72.5). For any source with no
  downloadable archive, start saving its daily forecasts, all hours and
  both leads; where to save is decided then (DECISIONS D72.8). The
  2026-27 forward test is pre-registered in DECISIONS D73, and its models
  are frozen (F122). A comparison of those frozen models against NBM, and
  against GFS MOS at DSM, on 2026-27 is pre-registered in DECISIONS D77.6.
  Its data-build script exists and passed its gate (DECISIONS D78.7,
  F128). Its scoring script and the NBM and MAV fetch exist and passed
  their gates (DECISIONS D79, F129). The non-US competitor probe
  (DECISIONS D78.3) found that DWD's MOSMIX keeps only about two days of
  issues (F130); daily saves of MOSMIX_L single-station files are chosen
  in DECISIONS D81.
- **Stage C — widen the target, on GFS only.** Correct every GFS run
  into an hourly temperature curve, plus the daily maximum, for
  forecast hours 0 to 24 first and to 48 later. Written with the
  weather model as a setting. Opened in DECISIONS D81; its design is in
  DECISIONS D82 and D83. Its GRIB pull for forecast hours 0 to 24 is
  complete and checked (DECISIONS D87, F137). Its next steps are in
  DECISIONS D88. Its claim is judged on new airports only, drawn by the
  rule in DECISIONS D82.7.
- **Stage D — correct each other weather model on its own,** on the
  full curve, screening each at a few hours first.
- **Stage E — blend and stack.** Combine the corrected models, with NBM
  as an input where it exists. This chooses which inputs go forward.
- **Stage F — upgrade policy.** What happens when any weather model
  changes version, starting with GFS v17.
- **Stage G — live product, version 1.** A daily pipeline, a
  prediction log that is never edited, a simple display, and
  one-script airport onboarding.
- **Stage H — probabilistic forecasts.** Ranges with stated odds,
  judged against their own bar, fixed before running.
- **Pooling (conditional).** Combining airports into one model with
  location-describing features. Opened only if the number of airports
  makes it worthwhile. It inherits the solar-standard-noon target hour
  already in use (4.1, DECISIONS D27, D33).

The former stages 3 to 6 are replaced (DECISIONS D72.10): former stage
3 (pooling) is the conditional step; former stage 4 (add models and
blend) is stages D and E; former stage 5 (widen the target, and the
48-hour lead) is stage C; former stage 6 (live product) is stage G.

*(The roadmap stages have no sections of their own yet, and will not
until the owner opens them. Stage 2 needs no section of its own,
however many airports it comes to hold: the sections above are written
per airport, so opening one means adding a row to the airport table,
not adding a design.)*

---

## 7. The richer-features GRIB method (a second, proven method)

Sections 1–6 describe the project's original, minimal method: three
features, Open-Meteo as the forecast source. That method is unchanged by
this section, and its results (section 5.0) stand exactly as reported. This
section describes a second, later, more complete method — five features, a
different forecast source — that was built, locked and tested once, and
passed at every one of this section's five airports (EGLC, LFPG, DSM, YSDU
and RNO), including Reno, where the minimal method failed. KSFO was added
later and judged under section 8 only (8.5).
**Both methods are real, proven results. Neither erases the other**
(DECISIONS D48.13).

**7.1 Motivation.** The minimal method beats both baselines at four of five
airports but fails at Reno (section 5.0, DECISIONS F82). Reno's own error
looks like a near-constant offset sitting under large day-to-day scatter,
rather than a learnable pattern (DECISIONS F79) — the kind of shape a model
can fit tightly in-sample without gaining anything out-of-sample. This
method asks whether adding two more pieces of physical information, cloud
cover and wind speed, gives the model enough real structure to do better —
at Reno, and everywhere else.

**7.2 What is different from the minimal method.** Everything not listed
here is unchanged from sections 1–6: the same airports, the same target
hour per airport (4.1), the same training/test split dates (4.3), the same
pairing rule (4.5), and the same frozen bar (5.3).

- **Features.** The minimal method's three features (GFS forecast
  temperature, `season_sin`, `season_cos`) plus two more: `cloud_cover`
  (total cloud cover) and `wind_speed_10m` (10 m wind speed). Two model
  variants are fitted and compared at every airport — a 3-feature model
  (the same feature set as the minimal method, refit on the new source) and
  the 5-feature model (all five) — so the effect of the two extra features
  can be read cleanly against an otherwise-identical baseline (DECISIONS
  D48.4).
- **Forecast source.** GFS 0.25° GRIB2 files, pulled directly from the
  public AWS archive `noaa-gfs-bdp-pds`, not Open-Meteo. This is a genuine
  archived past forecast at a fixed forecast-hour lead — never the freshest
  run for a given valid time — so it satisfies the no-look-ahead rule the
  same way Open-Meteo's Previous Runs API does (2.1b, DECISIONS F89). Each
  value is bilinear-interpolated (estimated from the four surrounding grid
  points) to the
  airport's already-established grid point (3.4). This is standard
  bilinear interpolation (weights from the fractional position along
  latitude and along longitude), not inverse-distance weighting (8.8 G6).
  The lead-time convention: for a target hour `HH:00 UTC`, use the run made at cycle
  `floor(HH/6)*6` UTC on the day before, forecast hour `24 + (HH mod 6)`
  (DECISIONS D48.2, F89).
- **Elevation correction.** GFS's own model terrain, at the resolution of a
  0.25° grid, can sit well above or below an airport's real elevation —
  negligible at four of this section's five airports but 275 m at Reno, in
  mountainous terrain. (At KSFO, added later under section 8, the gap is
  93.47 m; see 3.4.)
  This 0.25° grid cell is the raw GRIB model's own terrain, coarser than
  and different from the Open-Meteo grid point section 3.4 already
  established (whose elevation sits within 1 m of Reno's own) — the two
  methods interpolate onto different grids, so the two elevation-mismatch
  figures describe two different things and are not in conflict. A fixed
  lapse-rate correction (the lapse rate is how fast temperature drops with
  height; 7.429 °C/km, fit once and never refit) is applied
  to temperature only, as a constant per airport (DECISIONS D48.3, F90).
  Cloud cover and wind speed are used exactly as GRIB reports them,
  uncorrected (DECISIONS F91).
- **Raw-GFS baseline.** The "raw GFS (GRIB)" baseline is the GRIB 2 m
  temperature *after* this fixed elevation adjustment, not before it
  (DECISIONS D48.10, D62). See 5.2 for what "raw GFS" means in each method,
  the adjustment sizes, and the fact that margins against a fully
  unadjusted GRIB baseline were never measured.
- **Training window.** 2021-03-24 to 2025-07-31, restricted to GFS's v16
  model version (v16 went operational 2021-03-22; using an earlier model
  version inside the same training window would mix two different physical
  models, so the roughly 82 days before 2021-03-24 that the raw archive
  could otherwise reach are deliberately excluded). The sealed test year is
  the same 2025-08-01 to 2026-07-31 window every airport already uses
  (4.3). See DECISIONS D48.7, D48.8.
- **Model.** The same LightGBM settings as the minimal method (DECISIONS
  D21.4), unchanged — nothing tuned per airport, nothing tuned between the
  3-feature and 5-feature variants.

**7.3 Validation done before the sealed test.** Before any sealed-year data
was touched: the GRIB-based pipeline was checked against the trusted
Open-Meteo temperature series and matched it closely at each of this
section's five airports once the elevation correction was applied (within
0.062 °C on identical rows —
DECISIONS F89, F90); cloud cover and wind speed were checked against
Open-Meteo's own values over the period both exist and matched well, with a
real but explainable disagreement in cloud cover during genuinely
fast-changing partly-cloudy conditions (DECISIONS F90, F91); and a blocked
cross-validation across the whole training window showed the 5-feature
model beating the 3-feature model, and both beating raw GFS, at every one
of the five airports — including the two previously weak cases, LFPG and
Reno (DECISIONS F86, F87, F91). The Open-Meteo series used as this check is
documented as coming from GFS's 0.11° product, not the 0.25° product used
here (DECISIONS F117.4). The check passed at all five airports anyway. At
KSFO, added later under section 8, it failed, explained by a difference
between the sources (DECISIONS F116, F117, D69).

**7.4 Lock and sealed test.** The complete recipe — features, source,
pipeline, elevation constants, model settings, training window, and
pre-registered expectations — was written down and frozen before the
sealed year was opened (DECISIONS D48), the same discipline the minimal
method's own locks followed (DECISIONS D21, D31, D35, D39, D44). The sealed
test year was then opened once. A row-count guard tripped on its first run
and was traced to a guard-specification error, not a data problem, and
corrected before any model was fit or any sealed-year result was seen
(DECISIONS F92, F93). The frozen script was then run once, unchanged
(DECISIONS D48.13) (one later verification re-run, in session 68a,
reproduced every figure exactly and changed no verdict — DECISIONS D61.4,
D62).

**Result: the 5-feature model passes the frozen bar (5.3) at all five
airports** (DECISIONS F94):

| airport | 5-feature MAE | vs raw GFS (GRIB) | vs persistence | vs 3-feature |
|---|---|---|---|---|
| EGLC | 1.000 | +20.2% | +52.3% | +3.5% |
| LFPG | 1.156 | +16.4% | +49.7% | +1.8% |
| DSM  | 1.636 | +5.6%  | +59.1% | +3.4% |
| YSDU | 1.179 | +10.5% | +55.8% | +8.2% |
| RNO  | 1.346 | +11.0% | +45.9% | +7.5% |

"Raw GFS (GRIB)" here is the elevation-adjusted GRIB temperature (5.2).

Persistence is scored only on test days that have a previous-day
observation, while raw GFS and the models use every test day. DECISIONS
F94 Task 2 re-scored every rung on that common day set and found the
verdicts identical at all five airports. The minimal method, by contrast,
scores every rung on one common day set (DECISIONS D21.8).

The clearest, source-independent evidence that the two extra features
genuinely help is the last column: the 5-feature and 3-feature models are
trained and tested on the identical elevation-corrected GRIB temperature,
so they differ *only* in whether cloud cover and wind speed are included —
and the 5-feature model wins at every airport.

**7.5 What this does and does not mean.** This is a separate, additional,
independently-tested result under a different recipe (GRIB source, richer
features). It does **not** re-open, re-test, or overwrite any airport's
existing sealed-test verdict under the minimal method (section 5.0) — EGLC
(F16), LFPG (F30), DSM (F47), YSDU (F64) and RNO (F82) all stand exactly as
reported. **Reno in particular failed the minimal method (F82) and passes
this richer method (F94) — both are true, and neither erases the other**
(DECISIONS D48.13). At EGLC, LFPG, DSM and YSDU all three methods pass
(F16/F30/F47/F64, F94, F109). Reno fails the minimal method (F82) and
passes the richer and selected methods (F94, F109). Raw GFS (GRIB) is not
the same series as raw GFS (Open-Meteo) — the two sources agree closely but
are not identical (7.3), and they also differ in how elevation is handled:
Open-Meteo's own processing on one side, this project's fixed adjustment on
the other (5.2) — so the margins above are not directly comparable,
airport for airport, to section 5.0's minimal-method margins; a fuller
discussion of that comparison belongs in RESULTS.md, not here.

---

## 8. The selected-features GRIB method (a third, proven method)

Sections 1–6 describe the project's original, minimal method. Section 7
describes the richer 5-feature GRIB method. This section describes a
third, later method, built by a staged feature-selection programme on top
of section 7's own 5-feature baseline, locked once, and confirmed once on
a separate held-out year. **All three methods are real, proven results.
None of the three erases any other** (same spirit as DECISIONS D48.13).

**8.1 What it is.** Section 7's 5-feature GRIB baseline (`B`) plus four
selected features: moisture (`D`), lapse rate (`L`), shortwave radiation
(`R`) and pressure tendency (`T`) — written `B+D,L,R,T`. Precipitation
(`P`), relative humidity (`rh`) and the raw pressure-level temperatures
(`plev`) were tested and excluded (DECISIONS D58 item 1). The exact
columns, source files and transform for each added feature (DECISIONS D58
item 3):

| code | feature | committed column | source files | transform |
|---|---|---|---|---|
| L | lapse rate | `lapse_rate_t2_t850` | `session49_v16_window_with_upper_air.csv` / `session49_sealed_window_with_upper_air.csv` | none |
| D | moisture (dew-point depression) | `dewpoint_depression_t2m` | `session51_v16_window_with_moisture.csv` / `session51_sealed_window_with_moisture.csv` | `dewpoint_depression_t2m_floored = max(dewpoint_depression_t2m, 0)` |
| T | pressure tendency | `pressure_tendency_3h_hpa` | `session53_v16_window_with_pressure.csv` / `session53_sealed_window_with_pressure.csv` | none |
| R | shortwave radiation | `dswrf_2h_wm2` | `session55_v16_window_with_radiation.csv` / `session55_sealed_window_with_radiation.csv` | none |

D's transform changes exactly 1 of 7,952 rows — the v16 and sealed windows
combined, not the training window alone (DECISIONS D58 item 3). Reserved-
year test values for L, D, T and R come from `session63_reserved_window_
with_{upper_air,moisture,pressure,radiation}.csv` — the same four frozen
pipelines, with only the date range extended to cover the reserved year
(DECISIONS F107).

**8.2 What is unchanged from section 7.** Everything not listed here is
unchanged from section 7: the same `B` baseline (the 5-feature GRIB
recipe — forecast temperature, `season_sin`, `season_cos`, `cloud_cover`,
`wind_speed_10m`), the same GFS 0.25° GRIB2 source
(`noaa-gfs-bdp-pds`, 7.2), the same lead-time convention (7.2, DECISIONS
D48.2/F89), the same elevation/lapse-rate correction on surface
temperature (7.2, DECISIONS D48.3/F90), the same airports, target hour per
airport (4.1), pairing rule (4.5), frozen bar (5.3), and the same
raw-GFS baseline (5.2, 7.2). Each added
feature's own source and lead, as its own DECISIONS finding states it:
- **L (lapse rate).** DECISIONS F98: pulled from the same GRIB archive
  "onto the existing 5-feature GRIB dataset, at every date that dataset
  already carries" — the same source and dates as `B`. No elevation/
  lapse-rate correction is applied to the three pressure-level
  temperatures themselves (`t925`, `t850`, `t700`) — they are fixed
  pressure surfaces, not tied to surface terrain — only bilinear
  horizontal interpolation, the same as `B`'s own fields (F98).
- **D (moisture).** DECISIONS F100 states the moisture family was "built
  and validated in session 51" onto the same frozen 5-feature GRIB
  baseline `B` is refit against; F100 itself does not restate the source
  archive or lead-time formula beyond that.
- **T (pressure tendency).** DECISIONS F101 states the pressure family
  was "built and validated in session 53, from F97's own availability
  map"; F101 itself does not restate the source archive or lead-time
  formula beyond that.
- **R (shortwave radiation).** DECISIONS F102: `DSWRF:surface` (downward
  shortwave at the surface) is resolved to a physically consistent
  2-hour window ending at each airport's own target hour — the native
  24–26h window used directly at the lead-26 airports (YSDU, RNO and
  KSFO; DECISIONS F116.1, D67.1), and a de-accumulation from the 18–24h
  and 18–22h windows at the lead-24 airports (EGLC, LFPG, DSM) — from the
  same GRIB source as `B`.

**8.3 Training window, fold, settings, complete-case rule.** The
confirmation fold (DECISIONS D58 item 4): train 2021-03-24 to 2024-07-31,
test 2024-08-01 to 2025-07-31 — the reserved year set aside for this
programme (DECISIONS D51). All five airports, the same frozen LightGBM
settings as every other method in this project (DECISIONS D21.4/D48.6),
identical features at every airport, no per-airport feature selection
(DECISIONS D58 item 4). The complete-case row set (a row is used only if
every relevant column has a value) is built over only the
final four features' own underlying columns; DECISIONS D58 items 5 and 9
pre-registered and verified that this drops zero rows against a `B`-only
mask on the training window, at every airport. DECISIONS F107 separately
confirmed 365 of 365 complete-case reserved-year feature rows at every
airport, once the reserved-year build closed the gap D58 item 11 flagged.

**8.4 How it was chosen.** A staged feature-selection programme, run only
on three non-reserved training/test folds that never touch the reserved
year (DECISIONS D51's own `EXPERIMENT_FOLDS`): five candidate feature
families were tested one at a time against the frozen `B` baseline, each
contributing one adopted feature (DECISIONS F98–F105, D52–D56). Two raw
physical variables were separately parked as candidates without being
adopted — the raw pressure-level temperatures (`plev`, on Reno's own
fold-robust signal) and relative humidity (`rh`) — DECISIONS D52, D53.
These seven candidates were then swept together on a pre-registered
ladder of variants and a mechanical leave-one-out selection rule with a
correlated-feature safeguard and a joint backstop check (DECISIONS D57,
F106); the sweep's own mechanical rule dropped precipitation from the
final set, confirmed in DECISIONS D58. The owner reviewed and confirmed
that set unchanged (DECISIONS D58). The confirmed set was then run once,
and only once (one later verification re-run, in session 68a, reproduced
every figure exactly and changed no verdict — DECISIONS D61.4, D62),
against the reserved year (DECISIONS D58, F109) — the single authorised
look.

**8.5 Result.** The single authorised look at the reserved year
(2024-08-01 to 2025-07-31), per airport (DECISIONS F109):

| airport | raw GFS (GRIB) MAE | persistence MAE | B MAE | B+D,L,R,T MAE | vs raw GFS | vs persistence | vs B |
|---|---|---|---|---|---|---|---|
| EGLC | 1.2362 | 2.2259 | 1.0861 | 1.0008 | +19.04% | +55.04% | +7.85% |
| LFPG | 1.4091 | 2.5233 | 1.3285 | 1.2369 | +12.22% | +50.98% | +6.89% |
| DSM  | 1.7043 | 4.1081 | 1.4402 | 1.4123 | +17.13% | +65.62% | +1.94% |
| YSDU | 1.4897 | 2.5775 | 1.3030 | 1.2643 | +15.13% | +50.95% | +2.97% |
| RNO  | 1.6135 | 2.7563 | 1.4272 | 1.2742 | +21.03% | +53.77% | +10.72% |

"Raw GFS (GRIB)" here is the elevation-adjusted GRIB temperature (5.2).

Persistence is scored only on test days that have a previous-day
observation, while raw GFS and the models use every test day. This day
basis was pre-registered (DECISIONS D58 item 6) and is reported in
DECISIONS F109: EGLC is missing 1 day and YSDU 5 (audit-68b item 3). The
minimal method, by contrast, scores every rung on one common day set
(DECISIONS D21.8).

**B+D,L,R,T passes the frozen bar (5.3) at all five airports** — it beats
both raw GFS and persistence on MAE everywhere, with no exception. The
secondary read also holds: airport-averaged MAE 1.2377 against plain `B`'s
1.3170, a +6.02% skill margin (DECISIONS F109). No ranking among airports
is claimed.

**KSFO (added later; DECISIONS F119, D71).** KSFO was run under this
recipe, unchanged, with two pre-registered looks, each judged separately
against the frozen bar (DECISIONS D67.3, D70.3, D70.4). Look A trains on
2021-03-24..2024-07-31 and tests 2024-25. Look B trains on
2021-03-24..2025-07-31 and tests 2025-26. MAE in °C (DECISIONS F119.3):

| look | n test | raw GFS (GRIB) MAE | persistence MAE | B MAE | B+D,L,R,T MAE | vs raw GFS | vs persistence | vs B |
|---|---|---|---|---|---|---|---|---|
| A (2024-25) | 364 | 1.4263 | 1.5113 | 1.3534 | 1.2576 | +11.83% | +16.79% | +7.08% |
| B (2025-26) | 365 | 1.7321 | 1.7172 | 1.4654 | 1.3830 | +20.16% | +19.46% | +5.62% |

"Raw GFS (GRIB)" is the elevation-adjusted GRIB temperature (+0.6944 °C,
5.2). The day basis is the same as above: persistence is scored on test
days with a previous-day observation (363 of 364 in look A, 365 of 365 in
look B), and every other rung on every test day (DECISIONS D70.4, F119.3).

**Both looks pass**: `B+D,L,R,T` beats raw GFS and persistence in each.
The overall reading is **PASS**, as pre-registered ("pass in both years",
DECISIONS D70.8). The secondary band read (DECISIONS D70.5) holds in both
looks: the margin over `B`, 0.0958 °C in look A and 0.0824 °C in look B,
is above the column-order band of 0.0377 °C, so each reads "beats B by
more than the column-order spread" (DECISIONS F119.3). **These two rows
are not part of the five-airport table above, and not part of its +6.02%
airport-averaged secondary read.** Caveat (f) in 8.6 applies.

**8.6 Caveats (DECISIONS D59.3; (f) from D71).** Any use or write-up of
this result must carry these caveats:
- (a) This is one year only — one look per airport, the same discipline
  the five earlier airports' tests followed under every method (5.0, 5.3),
  not a multi-year robustness claim. KSFO, under this same method, had two
  pre-registered looks (5.0, caveat (f)).
- (b) This is the first look at the *selected* feature set on 2024-25, but
  `B` alone was already scored on that same year descriptively, in a
  different, earlier study (DECISIONS F96, D58 item 8) — the
  feature-selection choices themselves never touched 2024-25.
- (c) This section's own margins (reserved year, 2024-25) and section 7's
  own margins (sealed year, 2025-26) come from **different years** and
  must not be set side by side as like-for-like.
- (d) DSM's margin over `B` is small (+1.94%).
- (e) RNO's margin over `B` (+10.72%) was not pre-registered and is
  descriptive only.
- (f) **KSFO (DECISIONS D71.2–D71.5).** The headline is look A's margin
  over raw GFS (GRIB), +11.83% (1.2576 vs 1.4263 °C). Look B's +20.16%
  over raw GFS is always quoted with the next point. Look B's raw-GFS year
  was unusually poor (MAE 1.7321 °C, against 1.4263 in look A and 1.4423
  and 1.3061 in rehearsal), and persistence (1.7172) was the binding half
  of the bar there (+19.46%). KSFO's mean bias changed sign between years:
  the mean-bias reference was worse than raw GFS in both looks, and the
  training means imply a 2024-25 mean(obs − raw GFS) of about −0.42 °C,
  against about +0.36 °C before it. This is insight only; nothing was
  changed on it. The result is for the recipe at a sea-mixed grid point
  (37.5% sea weight, DECISIONS F117.3), whose reproduction gate is
  recorded as failed, explained by a difference between the sources
  (DECISIONS D69). It is not directly comparable with the five earlier
  airports. Look B's training includes 2024-25, by design (DECISIONS
  D70.3).

**8.7 Status.** This is the project's **default recipe** for any future
airport work or pooling work (the conditional pooling step, 6), applied
unchanged and identically at every airport (DECISIONS D59.3). Every new airport still needs its own
lock and its own test, with its looks fixed in writing in that lock before
any of its held-out values are read (5.0, 6; DECISIONS D71.6). KSFO, the
first airport run under this recipe after F109, had two pre-registered
looks and passed both (8.5; DECISIONS F119, D71). This status does not
change the minimal method's (5.0) or the richer 5-feature method's (7.5)
own standing results — all three stand.

**Build requirements for new-airport code (DECISIONS D62).** Any new code
written for a new airport must:
1. **Pair observations to the nearest report explicitly** (4.5; audit-67
   A67-12).
2. **Reject non-finite values** (`nan`, `inf`) at load, and drop and count
   them as missing (rule 2.2; audit-68b A68b-04).
3. **Check each GRIB message's full validity date and hour**, not the date
   alone (audit-68b A68b-05).
4. **Make a test-year gap guard compare the row count with the expected
   full count**, not with zero (audit-68b A68b-01).
5. **Not write to already-committed record files on a re-run** (audit-67
   A67-02, A67-03).

These apply to **new** code only. The historical and frozen scripts stand
as they are (DECISIONS D62.3).

**8.8 Implementation details (from the record, DECISIONS D65).** The
clean-room rebuild of F109 at RNO (DECISIONS D64, F112, F113, F114) found
details that the other documents did not state. Each row below says what
the record code does. "Record" means the scripts and committed files behind
F109: `session62_reserved_confirm.py` (the frozen F109 script, which also
pairs the observations), `session37_decode.py` / `session40_decode.py` (B),
`session49_upper_air_pull.py` (L), `session51_moisture_pull.py` (D) and
`session63_reserved_year_build.py` (L and D for the reserved year), all
under `scripts/`.

| item | what the record does | source |
|---|---|---|
| G1 report tie-break | If more than one qualifying report falls in the window on a day, the **last one in the file** is kept (each overwrites the one before). This is not an explicit nearest-report choice (4.5). | `session62_reserved_confirm.py` l.321–344 (l.343); DECISIONS D62 |
| G2 nearest usable report | A report whose `tmpc` is `M`, blank, `T` or `None` is skipped **before** the choice, so the day keeps any other qualifying report that has a temperature. Each report is first assigned to its nearest whole hour (a report at `:30` goes to the next hour). | `session62_reserved_confirm.py` l.330–342 |
| G3 the 15-minute edge | A report is dropped only if it is **more than** 15 minutes from the hour, so a report exactly 15 minutes out is kept (inclusive). | `session62_reserved_confirm.py` l.336 |
| G4 stored precision of `temperature_grib_c` | Stored at **3 decimals**, rounded **after** the elevation constant is added. `cloud_cover_grib_pct` and `wind_speed_grib_kmh` are also stored at 3 decimals. `t2m_raw` is built from the stored 3-decimal value: `t2m_raw = round(temperature_grib_c − correction_c, 3)`. | `session37_decode.py` l.154, l.164–166; `session40_decode.py` l.140, l.150–152; `session49_upper_air_pull.py` l.295; `session51_moisture_pull.py` l.306; `session63_reserved_year_build.py` l.272, l.304 |
| G5 the elevation constant as used | RNO uses **2.0436** (°C), read from the params CSV, where it is stored rounded to 4 decimals. It is not the unrounded formula value (2.04356932). Applied as `(K − 273.15) + correction_c`. | `session37_elevation_fix.py` l.250–252; `data/raw/diagnostics/session37/session37_elevation_correction_params.csv`; `session37_decode.py` l.71–77, l.154; DECISIONS F113.5 |
| G6 bilinear interpolation | The 4 grid points nearest the SPEC 3.4 grid point come from eccodes' `codes_grib_find_nearest`. The value is standard bilinear: weights come from the fractional position along latitude and along longitude (not inverse distance). A negative longitude is shifted by +360 first. If the 4 points do not form a 2 × 2 box and have zero span, the nearest point's value is used. | `session37_decode.py` l.80–118; `session40_decode.py` l.66–104; `bilinear_from_gid` in `session49_upper_air_pull.py` l.148 and `session51_moisture_pull.py` l.155 |
| G7 rounding order for L and D | `t850` and `dew_point_2m` are **not** rounded before the subtraction. The record computes `round(t2m_raw − t850, 3)` and `round(t2m_raw − dew_point_2m, 3)` with the full-precision decoded value (K → °C, −273.15). The stored `t850` and `dew_point_2m` columns are rounded to 3 decimals separately. `t2m_raw` already has 3 decimals, so rounding first gives the same stored value except at an exact rounding tie. At RNO it gave the same value on every row (DECISIONS F113). | `session49_upper_air_pull.py` l.299, l.301, l.384; `session51_moisture_pull.py` l.310, l.312, l.510; `session63_reserved_year_build.py` l.278, l.313 |
| G14 API | LightGBM's scikit-learn API: `lgb.LGBMRegressor(**LGB_PARAMS).fit(x, y)`, with no other fit arguments. | `session62_reserved_confirm.py` l.386–387 |
| G15 full column list, in order | `temp` (= `temperature_grib_c`), `season_sin`, `season_cos`, `cloud_cover`, `wind_speed_10m`, then **D, L, R, T**: `dewpoint_depression_t2m_floored`, `lapse_rate_t2_t850`, `dswrf_2h_wm2`, `pressure_tendency_3h_hpa`. Passed as a float64 NumPy array, with no column names. **Column order changes the fit**: at RNO, L, D, T, R order gives 1.2703, and the record's order gives 1.2742 (DECISIONS F114). | `session62_reserved_confirm.py` l.118, l.120–127, l.239–240 |
| G17 unstated parameters | Only the D21.4/D48.6 settings are passed. Every other parameter is left at the **lightgbm 4.7.0** default (pinned in `requirements.txt`; the F109 run's environment printed Python 3.12.2, numpy 2.5.2, lightgbm 4.7.0). The record did not save the resolved parameter list. The rebuild's, from the same version, is in `data/rebuild/session73/rno_fit_metadata.json`. | `session62_reserved_confirm.py` l.131–146; `requirements.txt`; `notes/session-64-preflight-output.txt` l.6–8 |
| G19 training row order | Ascending date. | `session62_reserved_confirm.py` l.355, l.370 |
| G20 target precision | The unrounded residual `obs − fc`, where `obs` is `float(tmpc)` and `fc` is the stored 3-decimal `temperature_grib_c`. At RNO, rounding this target to 3 decimals left every prediction unchanged (DECISIONS F114). | `session62_reserved_confirm.py` l.376 |
| G24 MAE rounding rule | MAE is the NumPy mean of the absolute errors at full precision. It is printed at 4 decimals with Python's `:.4f` format and stored unrounded in `data/processed/session63_reserved_confirm_grid.csv`. | `session62_reserved_confirm.py` l.243–244, l.715, l.722–725 |

These details are recorded for reproducibility. They change no result on
record (DECISIONS D64.1, D65.1).
