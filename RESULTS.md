# RESULTS.md — the project so far, in one place

This file is a standalone technical summary. It draws only on facts already
recorded in `SPEC.md` and `DECISIONS.md` — it computes nothing new. Every
number below is cited to the DECISIONS finding it comes from, so it can be
checked against the original record. Where `SPEC.md` and this file ever
disagree, `SPEC.md` is right (CLAUDE.md, SPEC section 2).

Written after session 30, thirty sessions and five airports into the
project. Language is kept plain; jargon is defined the first time it is
used, so this can also serve as the basis for a plainer-language write-up
later without redoing the work.

---

## 1. What the project is

Big weather models — this project uses **GFS**, the US National Weather
Service's global forecast model — are good at the physics of weather, but at
any one place they tend to make the *same small mistakes over and over*.
That repeated, predictable error is called **bias**. This project is
**MOS-style bias correction**: it learns GFS's bias at a single airport from
several years of past forecasts and observations, then corrects new
forecasts for that same learned error. ("MOS" — Model Output Statistics — is
the standard name for this technique in operational forecasting; it is
decades old and well understood, not a novel idea. What this project tests
is how far a small, minimal version of it travels across very different
places.)

Concretely, at each airport the model learns the *residual* — observed
temperature minus GFS's forecast temperature — from two inputs: the forecast
temperature itself, and the time of year. It never predicts the temperature
directly, and it never sees the future it is trying to predict. The result
is judged against two honest baselines (raw GFS, and "tomorrow will be the
same as today") under a rehearse-then-single-sealed-test discipline, with a
frozen, qualitative pass/fail bar fixed before any test year is opened. Four
of five airports tried so far pass that bar; the fifth does not, and that
failure is itself one of this project's findings, not a flaw in it.

---

## 2. Method, in brief

**The target.** The temperature at one fixed hour a day, chosen per airport
so it falls at that airport's own local solar noon (SPEC 4.1). Local noon is
in daylight (catches the daytime heating GFS tends to mis-handle), a stable
well-observed time of day, and clear of dawn/dusk swings. Daylight saving is
deliberately ignored, so each airport's target stays one fixed UTC hour all
year. The five airports' hours differ — 12:00 UTC (EGLC, LFPG), 18:00 UTC
(DSM), 02:00 UTC (Dubbo), 20:00 UTC (Reno) — because local noon is a
different UTC hour at each longitude (DECISIONS D27, D33, D37, D42).

**What is learned.** A gradient-boosted tree model (LightGBM) predicts the
*residual*: observed temperature minus GFS's forecast temperature for that
day's target hour. The corrected forecast is GFS's forecast plus the
predicted residual (SPEC 4.2). Exactly three features are used, deliberately
minimal (DECISIONS D19):

```
forecast_temp_c   the GFS forecast temperature for that day at the target hour
season_sin        sin(2*pi*year_fraction(date))
season_cos        cos(2*pi*year_fraction(date))
```

No hour-of-day feature (the hour is fixed, so it carries no information) and
no recent-observation feature (kept out on purpose, so the model corrects
*the forecast* rather than quietly becoming a persistence model in
disguise). Model settings are fixed and identical at every airport
(DECISIONS D44.4, tracing back to D21.4):

```
LightGBM, objective=regression_l1, n_estimators=300, learning_rate=0.05,
num_leaves=15, min_child_samples=40, random_state=42, deterministic=True,
n_jobs=1
```

Nothing is tuned per airport. Only the airport's own data and its own target
hour change from one run to the next.

**The split (DECISIONS D13, D18).** All five airports share the same fixed
dates:
- **Training window: 2021-03-24 to 2025-07-31.** Subdivided for rehearsal
  into inner-training (2021-03-24 to 2024-07-31) and a validation year
  (2024-08-01 to 2025-07-31), so the whole method can be tried out once
  without touching the real test year.
- **Test window (sealed): 2025-08-01 to 2026-07-31.** Opened exactly once
  per airport, after the method is locked in writing (DECISIONS D21, D31,
  D35, D39, D44) and never touched before that.

Splitting is always by time — train on earlier dates, test on later ones —
never at random, so the model can never see information from the future it
is being tested on (SPEC 2.1a).

**Pairing observation to forecast (DECISIONS D14).** Each day's forecast,
valid at the target hour, is paired with the airport's nearest scheduled
weather report to that hour. If no report falls within 15 minutes, that day
is dropped and counted — never filled in (SPEC 2.2). The offset is small at
every airport (5–10 minutes) except LFPG and Dubbo, which report exactly on
the hour.

**Data hygiene, shared by every airport:**
- **The archive has one shared gap**, 492 hours, from 2023-12-30 00:00 to
  2024-01-19 11:00 UTC, present at every airport pulled so far and always
  falling inside the training window (never the sealed test year). Dropped
  and counted, never filled (SPEC 3.2).
- **The forecast model string is pinned to `gfs_global`**, the explicit NCEP
  GFS identifier, rather than Open-Meteo's `gfs_seamless` label. At most
  airports the two are provably identical, so the pin costs nothing — but at
  **DSM**, inside the continental United States, the two strings *differ* by
  up to 12.3 degC on some hours, because `gfs_seamless` can silently swap in
  a US-only model (DECISIONS F40, D16). The pin is what makes "this is
  genuine NCEP GFS" true by construction rather than by argument, and DSM is
  the case that shows why it mattered to check rather than assume.
- **The per-airport target-hour convention** (above) means only EGLC and
  LFPG make the clean "only the location changed" comparison SPEC originally
  set out to run (DECISIONS D26). Every airport from DSM onward changes the
  location *and* the target hour together, so their results answer "does the
  recipe travel to a different place at a comparable local time" rather than
  "does it travel with literally nothing else changed."

**The bar (SPEC 5, frozen before any model ran).** An airport passes if its
corrected forecast has a lower mean absolute error (MAE) than *both* raw GFS
and persistence, over that airport's own sealed test year. The bar is
qualitative — no numeric margin, ever (DECISIONS D22) — so a pass by a hair
and a pass by a mile are both passes, and the honest margin is always
reported alongside the verdict.

---

## 3. The five airports — results

**Finding, stated plainly first: the recipe passes at four airports across
three continents and two hemispheres, unmodified — and fails, honestly, at
the fifth, in the way its own advance prediction said it would.**

| airport | region / hemisphere | target hour (UTC) | test days | raw GFS MAE (degC) | corrected MAE (degC) | skill vs raw GFS | skill vs persistence | verdict |
|---|---|---|---|---|---|---|---|---|
| EGLC (London City) | Western Europe, N | 12:00 | 363 | 1.242 | 1.040 | **+16.3%** | +50.4% | **PASS** |
| LFPG (Paris CDG) | Western Europe, N | 12:00 | 363 | 1.396 | 1.208 | **+13.5%** | +47.5% | **PASS** |
| DSM (Des Moines) | N. America interior, N | 18:00 | 365 | 1.815 | 1.700 | **+6.3%** | +57.5% | **PASS** |
| YSDU (Dubbo) | Australia, S | 02:00 | 347 | 1.251 | 1.210 | **+3.3%** | +54.7% | **PASS** |
| RNO (Reno) | N. America mountain, N | 20:00 | 365 | 1.414 | 1.458 | **−3.1%** | +41.4% | **FAIL** |

"Skill" here is the field-standard skill score, `1 − corrected/reference`:
positive means the correction beats that reference, negative means the
reference (raw GFS, for Reno) beats the correction. Sources: EGLC
(DECISIONS F16), CDG (F30), DSM (F47), Dubbo (F64), Reno (F82). All five
test years are the same shared twelve months (2025-08-01 to 2026-07-31,
SPEC 4.3, D13) — this is not five independent draws of weather; see section
4 below.

**Every one of the five airports beats persistence comfortably** (41–58%
better) — the correction is never worse than the laziest possible guess. The
raw-GFS half of the bar is what actually decides each airport's verdict, and
it is the half that finally failed at Reno.

---

## 4. The findings

**1. Four passes across three continents and two hemispheres — the recipe
travels.** The same unmodified method (three features, one model, one
frozen bar) passed at a small European city airport (EGLC), a major European
hub (CDG), a continental-interior US airport with far larger day-to-day
swings (DSM), and a Southern-Hemisphere Australian airport with a flipped
season cycle (Dubbo). Nothing was retuned or added between airports.

**2. Four distinct bias shapes — the model adapts to local structure, not a
template.** Feature-importance shares differ meaningfully airport to
airport (forecast temperature's share of the model's learning: EGLC 51.8%,
CDG 38.2%, DSM 43.4%, Dubbo 45.3%, Reno 39.1% — DECISIONS F16, F30, F47,
F64, F82). EGLC's bias lives mostly in the temperature itself (a "warm-end"
shape); CDG's lives more in the calendar; DSM carries both; Dubbo's is
concentrated in one local season. The same three features are read
differently at each place.

**3. The flipped-season result: cross-hemisphere generalisation, not a
Northern pattern baked in.** Dubbo's bias peaks in its own local summer
(Southern Hemisphere), not in the Northern-calendar season that would carry
the label "summer" at the other four airports (DECISIONS F61). Because the
season features are encoded as a position in the calendar year rather than
a hardcoded "summer means June–August," the model correctly re-derives which
part of the year matters for a place on the other side of the equator.

**4. The Reno failure, and why it matters: systematic vs. random error.**
Reno's forecast error is close to a **near-constant offset** (the station
runs warmer than GFS on about 68% of training days, versus 45–52% at every
other airport) sitting under **large day-to-day scatter** rather than a
structured, learnable pattern (DECISIONS F79). A tree model fitting that
shape looks good in-sample (25.0% apparent improvement) and adds almost
nothing out-of-sample (−3.1%) — the textbook signature of overfitting a
signal that is mostly noise. This is not a defect in the method; it is what
the method is supposed to do when the truth is "there isn't much learnable
structure here beyond a small constant." The contrast with DSM is the clean
statement of the finding: **DSM is a hard-but-structured airport and passes;
Reno is a moderate-but-mostly-random airport and fails.** Notably, this
outcome was written down *in advance*, before Reno's sealed test year was
opened (DECISIONS D44.12), based on the same signature already visible in
Reno's rehearsal — a failure predicted correctly in writing is a stronger
kind of evidence for the reading above than a failure noticed only after the
fact.

**5. The weather-year caveat: all five airports share one test year, and it
was not neutral everywhere.** SPEC's split dates are fixed for every
airport, so all five sealed tests fall on the identical twelve months
(2025-08-01 to 2026-07-31) — this is not five independent draws of weather
(DECISIONS F46, F48, F65). Climatology's own bias against the training
average makes this concrete: a positive climatology bias means the test
year ran warmer at the target hour than the 2021–2025 training average for
the same dates. That bias is large at both European airports (+0.773 degC
at EGLC, +0.918 at CDG) but close to neutral at DSM (+0.172) — so the test
year was a warm one specifically in western Europe, not everywhere
(DECISIONS F48). The two European margins in particular were flattered by
one warm European summer, not by a universally easier year. Each airport's
rehearsal (a *different* year, the validation year) and its sealed test both
being positive at the four passing airports is partial, two-year evidence
that the wins are not purely one lucky year — but it is not a fully
independent second test year, since the rehearsal year and methodology are
not held to the same one-look discipline as the sealed test.

**6. Honest magnitude.** Across the four passes, the margin over raw GFS
on the sealed test year ranges from **3.3% to 16.3%** (skill score
0.033–0.163), and the margin over the mean-bias reference — the check that
separates "the model learned real structure" from "the model just found a
constant to subtract" — ranges from **2.3% to 15.7%**, falling at every
successive airport tested (EGLC 15.7% → CDG 13.0% → DSM 3.4% → Dubbo 2.3%,
DECISIONS F16, F30, F47, F64). These are real, repeatable wins, but they are
modest ones. The project's honest value so far is a **calibrated
understanding of where the method works** — structured, non-random local
bias — rather than a large universal gain everywhere GFS is used.

---

## 5. Limitations and open directions

These are stated as the current honest edges of the work, not as failures:

- **The feature set is deliberately minimal** — forecast temperature and
  season only. No cloud cover, wind, humidity, or terrain descriptor is
  used anywhere. Reno's failure is the clearest evidence yet that this
  minimal set has a ceiling: where the bias is close to a constant plus
  noise, three features may simply not carry enough information to do
  better than they already do.
- **One shared test year across all five airports.** Every sealed-test
  result so far is drawn from the same twelve months. A second, independent
  test year — at any airport — would be the strongest single piece of
  further evidence about how much of the passing margins is model and how
  much is one year's weather.
- **Parked directions, not started:** richer features at Reno specifically,
  as the diagnostic case (cloud cover, wind, a genuine terrain descriptor);
  blending in other forecast models (ECMWF, ICON, Google's WeatherNext AI
  model — SPEC stage 4); widening the target from one fixed hour to a full
  daily temperature curve (SPEC stage 5); and the eventual live daily
  product (SPEC stage 6). None of these has begun. The next planned session
  is scoping the richer-features question, with Reno as the motivating
  case — that is a design discussion, not yet a change to the method.

---

*All figures in this file are cited to their DECISIONS.md source and were
checked against it when this file was written (session 30). SPEC.md remains
the source of truth for how the project works; this file is a read-only
summary of results already on record there.*
