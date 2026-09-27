# RESULTS.md — the project so far, in one place

This file is a standalone technical summary. It draws only on facts already
recorded in `SPEC.md` and `DECISIONS.md` — it computes nothing new. Every
number below is cited to the DECISIONS finding it comes from, so it can be
checked against the original record. Where `SPEC.md` and this file ever
disagree, `SPEC.md` is right (CLAUDE.md, SPEC section 2).

Written after session 30, revised after session 44, revised after session
65, revised after session 79, revised after session 80. As of session 65, the project has **three** independently-tested,
proven methods for correcting GFS's local bias at an airport: a minimal
three-feature method (sections 2–4 below, the project's original result),
a richer five-feature method using a different forecast source (section 5,
"act two"), and a selected-features method built on top of the richer
method by a staged feature-selection programme (section 6, "act three").
The minimal method passes at four of five airports and fails at the fifth,
Reno; both the richer method and the selected-features method pass at all
five, including Reno. A sixth airport, San Francisco (KSFO), has since
passed the selected-features method on two pre-registered looks (DECISIONS
F119, D71). That result is for the recipe at a sea-mixed grid point and is
not directly comparable with the five earlier airports; see section 6.5.
All three results are real and none erases any other
(DECISIONS D48.13, D59.3) — read together, they tell a three-chapter story
about what the minimal method's ceiling was, what first addressed it, and
what a disciplined search for more features added on top. Language is kept
plain; jargon is defined the first time it is used, so this can also serve
as the basis for a plainer-language write-up later without redoing the
work.

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
places, and — since session 44's own act two — how much a richer version
buys once the minimal version hits a wall.)

Concretely, at each airport a model learns the *residual* — observed
temperature minus the forecast temperature — from a small set of inputs, and
never sees the future it is trying to predict. The result is judged against
two honest baselines (raw GFS, and "tomorrow will be the same as today")
under a rehearse-then-single-sealed-test discipline, with a frozen,
qualitative pass/fail bar fixed before any test year is opened. The minimal
method (sections 2–4) passes that bar at four of five airports; the richer
method (section 5; SPEC 7, DECISIONS F94) and the selected-features method
(section 6; SPEC 8, DECISIONS F109) each pass at all five. The one airport
the minimal method fails, Reno, is itself one of this project's findings,
not a flaw in it — and the two later methods' passing results there are
further findings, not corrections of the first.

---

## 2. Method, in brief (the minimal method)

**The target.** The temperature at one fixed hour a day, chosen per airport
so it falls at that airport's own local solar noon (SPEC 4.1). Local noon is
in daylight (catches the daytime heating GFS tends to mis-handle), a stable
well-observed time of day, and clear of dawn/dusk swings. Daylight saving is
deliberately ignored, so each airport's target stays one fixed UTC hour all
year. EGLC and LFPG share 12:00 UTC **by deliberate design**, not by
coincidence of longitude: 12:00 UTC is London's own local noon, and Paris's
local noon is closer to 11:00 UTC, but the two were deliberately run at the
same hour so the comparison between them changes only the location and
nothing else (DECISIONS D26). DSM (18:00 UTC), Dubbo (02:00 UTC) and Reno
(20:00 UTC) each instead take their own local-solar-noon UTC hour, because
12:00 UTC is not their local noon (DECISIONS D27, D33, D37, D42).

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
reported alongside the verdict. **Section 5's richer method uses the
identical bar and the identical discipline, on a different forecast
source** — see section 5 for what changes and what does not.

---

## 3. The five airports — results (the minimal method)

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
4 below. **Reno's raw-GFS figure here (1.414) is Open-Meteo's; section 5
describes a separate, later method, using a different forecast source
(GRIB), that passes at Reno too — see section 5.4's decomposition for the
honest accounting of what changed.**

**Every one of the five airports beats persistence comfortably** (41–58%
better) — the correction is never worse than the laziest possible guess. The
raw-GFS half of the bar is what actually decides each airport's verdict, and
it is the half that finally failed at Reno.

---

## 4. The findings (the minimal method)

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
fact. **This finding stands unchanged. Section 5 describes a later, separate
method — two more features, a different forecast source, a longer
training window — that was built specifically to test whether Reno's
apparent ceiling was a limit of the minimal feature set rather than a limit
of Reno itself, and passes there (section 5.4 gives the honest accounting of
what that result does and does not mean).**

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
not held to the same one-look discipline as the sealed test. **This same
one-shared-year limitation applies identically to section 5's richer
method, whose sealed test runs on the same twelve months.**

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

## 5. Act two: the richer-features GRIB method

Sections 2–4 describe the project's original, minimal method, and its
results stand exactly as reported above. This section describes a second,
later, more complete method — five features instead of three, a different
forecast source — that was built, validated, locked, and tested once
against the identical frozen bar, and passes at every airport, including
Reno, where the minimal method failed (DECISIONS D48, F85–F94; folded into
`SPEC.md` as section 7 by session 43, DECISIONS D49). **Both results are
real and proven. Neither erases the other** (DECISIONS D48.13).

### 5.1 Motivation and what is different

Finding 4 above named Reno's own shape plainly: a near-constant bias sitting
under large scatter, the kind of error a flexible model can fit tightly
in-sample without gaining anything out-of-sample. This method asks whether
two more pieces of physical information — cloud cover and 10 m wind speed —
give the model enough real structure to do better, at Reno and everywhere
else (DECISIONS F81, F85).

Everything not listed here is unchanged from the minimal method: the same
airports, the same target hour per airport, the same training/test split
dates, the same 15-minute pairing rule, and the same frozen qualitative bar
(SPEC 7.2).

- **Features.** `forecast_temp_c`, `season_sin`, `season_cos` (the minimal
  method's three) plus `cloud_cover` (total cloud cover) and
  `wind_speed_10m` (10 m wind speed). Two model variants are fitted and
  compared at every airport — a 3-feature model (the minimal method's own
  feature set, refit on the new source) and the 5-feature model — so the
  effect of the two extra features can be read cleanly against an
  otherwise-identical baseline (DECISIONS D48.4).
- **Forecast source.** GFS 0.25° GRIB2 files, pulled directly from the
  public AWS archive `noaa-gfs-bdp-pds`, not Open-Meteo — a genuine
  archived past forecast at a fixed forecast-hour lead, satisfying the
  no-look-ahead rule the same way Open-Meteo's Previous Runs API does
  (SPEC 2.1b, DECISIONS F89). Each value is bilinear-interpolated to the
  airport's already-established grid point.
- **Elevation correction.** GFS's own model terrain, at 0.25° resolution,
  can sit well above or below an airport's real elevation — negligible at
  four airports but 275 m at Reno, in mountainous terrain. A fixed
  lapse-rate correction (7.429 °C/km, fit once and never refit) is applied
  to temperature only, as a constant per airport (DECISIONS D48.3, F90).
  Cloud cover and wind speed are used exactly as GRIB reports them,
  uncorrected (DECISIONS F91). **This is a different grid than the one
  Open-Meteo's own downscaled point uses (SPEC 3.4), so this 275 m gap and
  SPEC 3.4's own 1 m Reno grid-elevation figure describe two different
  things, not a contradiction** (DECISIONS D49).
- **Training window.** 2021-03-24 to 2025-07-31, restricted to GFS's v16
  model version, so a bias-correction model never crosses a model-version
  boundary (DECISIONS D48.7, F89).
- **Model.** The same LightGBM settings as the minimal method (DECISIONS
  D21.4), unchanged — nothing tuned per airport, nothing tuned between the
  3-feature and 5-feature variants.

### 5.2 Validation before the sealed test

Before any sealed-year data was touched: the GRIB-based pipeline was
checked against the trusted Open-Meteo temperature series and matched it
closely at every airport once the elevation correction was applied (within
0.062 °C on identical rows — DECISIONS F89, F90); cloud cover and wind
speed were checked against Open-Meteo's own values over the period both
exist and matched well, with a real but explainable disagreement in cloud
cover during genuinely fast-changing partly-cloudy conditions (DECISIONS
F90, F91); and a blocked cross-validation across the whole training window
showed the 5-feature model beating the 3-feature model, and both beating
raw GFS, at every one of the five airports — including the two previously
weak cases, LFPG and Reno (DECISIONS F86, F87, F91).

### 5.3 The lock and the sealed test

The complete recipe — features, source, pipeline, elevation constants,
model settings, training window, and pre-registered expectations — was
written down and frozen before the sealed year was opened (DECISIONS D48),
the same discipline the minimal method's own locks followed. A row-count
guard tripped on its first run and was traced to a guard-specification
error, not a data problem, and corrected before any model was fit or any
sealed-year result was seen (DECISIONS F92, F93). The frozen script was
then run once, unchanged (DECISIONS D48.13).

**Result: the 5-feature model passes the frozen bar at all five airports**
(DECISIONS F94):

| airport | 5-feature MAE | raw GFS (GRIB) MAE | persistence MAE | 3-feature MAE | vs raw GFS (GRIB) | vs persistence | vs 3-feature | n days | verdict |
|---|---|---|---|---|---|---|---|---|---|
| EGLC | 1.000 | 1.254 | 2.096 | 1.037 | **+20.2%** | +52.3% | +3.5% | 364 | **PASS** |
| LFPG | 1.156 | 1.382 | 2.300 | 1.177 | **+16.4%** | +49.7% | +1.8% | 364 | **PASS** |
| DSM  | 1.636 | 1.733 | 4.003 | 1.694 | **+5.6%**  | +59.1% | +3.4% | 365 | **PASS** |
| YSDU | 1.179 | 1.317 | 2.669 | 1.283 | **+10.5%** | +55.8% | +8.2% | 356 | **PASS** |
| RNO  | 1.346 | 1.512 | 2.490 | 1.455 | **+11.0%** | +45.9% | +7.5% | 365 | **PASS** |

"Raw GFS (GRIB)" here is the elevation-adjusted GRIB temperature (SPEC 5.2,
DECISIONS D48.10).

Persistence is scored only on test days that have a previous-day
observation, while raw GFS and the models use every test day. DECISIONS F94
Task 2 re-scored every rung on that common day set and found the verdicts
identical at all five airports. The minimal method, by contrast, scores
every rung on one common day set (DECISIONS D21.8).

The clearest, source-independent evidence that the two extra features
genuinely help is the last comparison column: the 5-feature and 3-feature
models are trained and tested on the identical elevation-corrected GRIB
temperature, so they differ *only* in whether cloud cover and wind speed
are included — and the 5-feature model wins at every airport (DECISIONS
F94).

### 5.4 The honest Reno decomposition

Reno is the headline of this method, and getting its framing right matters
more than any other single number in this file.

- **The 5-feature model passes Reno** on the sealed year: 1.346 vs raw GFS
  (GRIB) 1.512, a **+11.0%** skill margin, and it beats persistence
  (2.490) by 45.9%. This is real, and it matches the pre-registered
  expectation written down before the sealed year was opened (DECISIONS
  D48.12, F94).
- **The clean, source-independent evidence that cloud cover and wind speed
  genuinely help is the 5-vs-3 comparison, not the vs-raw-GFS number.** The
  5-feature and 3-feature models are trained and tested on identical
  elevation-corrected GRIB temperature, so they differ only in whether
  cloud and wind are included: Reno's 5-feature MAE (1.346) beats its own
  3-feature MAE (1.455) by **+7.5%**. This is the number to lead with for
  "richer features help at Reno" (DECISIONS F94).
- **The +11.0% vs-raw-GFS margin is somewhat flattered, and that needs
  saying plainly.** The GRIB raw-GFS baseline at Reno (1.512) is
  measurably worse than the Open-Meteo raw-GFS baseline the minimal method
  faced (1.414, F82) — GRIB's single fixed-constant elevation correction
  is evidently a shade less accurate at Reno's own terrain than
  Open-Meteo's own downscaling (SPEC 7.2, DECISIONS F89, F90). So part of
  the +11.0% margin reflects a slightly weaker raw comparator, not only a
  better correction.
- **The pass is nonetheless robust to that baseline difference.** Measured
  against an Open-Meteo-quality raw baseline (1.414) instead of GRIB's own
  (1.512), the 5-feature model's MAE (1.346) still represents roughly a
  **+4.8%** margin (1 − 1.346/1.414) — smaller, but still a genuine pass,
  not an artifact that a fairer baseline would erase.
- **The GRIB pipeline and the 3-feature model did not "rescue" Reno on
  their own — the two extra features did.** The 3-feature model's own
  apparent Reno pass (MAE 1.455, +3.8% vs GRIB raw GFS) is largely the same
  baseline artifact described above: 1.455 is essentially unchanged from
  the minimal method's own failing corrected value (1.458, F82) — the
  learned correction at Reno is still close to unhelpful under three
  features, exactly as findings F79/F82 already established. **What
  changed at Reno is the two extra features**, shown cleanly by the 5-vs-3
  column (+7.5%), not the change of forecast source by itself.
- **The other four airports carry no such caveat.** Their own GRIB
  elevation constants are all under half a degree (EGLC +0.249, LFPG
  −0.170, DSM −0.111, YSDU +0.246 — DECISIONS D48.3), so their richer-method
  margins are clean as reported, with no baseline-quality asterisk.

**The one-sentence honest version:** cloud and wind add genuine skill at
Reno — +7.5% over the three-feature model on identical temperature — and
the five-feature model passes the bar there; Reno's original failure was a
real limit of the minimal feature set, now addressed by richer information,
not by the change of data source alone.

### 5.5 The LFPG window story: more data was the fix

LFPG is the other airport worth telling a full story about, because its own
path through this method is a clean illustration of *why* the GRIB build
was worth doing at all. On the short 1.5-year feature-complete window that
Open-Meteo alone could supply, LFPG's richer-features result never beat raw
GFS — both models stayed negative across the scout and the follow-up CV
(DECISIONS F86, F87). Once the GRIB source made the full
~4.4-year training window available with cloud cover and wind speed
included throughout, LFPG's own result flipped: 3-feature +3.3%, 5-feature
+5.3% on the full-window cross-validation (DECISIONS F91), and now +16.4%
(5-feature) / a real +1.8% 5-vs-3 margin on the sealed test itself
(DECISIONS F94). **The short window, not the richer features, was the
binding constraint at LFPG all along** — a concrete, falsifiable "more data
was the fix" finding, and the specific justification for building the GRIB
pipeline rather than staying on Open-Meteo's shorter feature-complete
history.

### 5.6 The method-and-discipline arc, and honest magnitude

The minimal method has a real ceiling — Reno (finding 4). Richer
information (cloud cover, wind speed) plus a longer, GRIB-sourced training
window breaks that ceiling: 5 of 5 airports now pass under one recipe, the
project's first such result (DECISIONS F94). This was done under the same
frozen-bar discipline as every earlier lock: pre-registered expectations
were written down before the sealed year was opened (DECISIONS D48.12) and
every one of them was matched exactly, with no exception (DECISIONS F94) —
including a guard mis-specification caught and corrected before any
sealed-year result was seen (DECISIONS F92, F93), the same "stop and report
rather than work around" discipline the project has followed throughout.

**Honest magnitude.** The two extra features add a modest, real
improvement over the three-feature model on identical GRIB temperature:
the 5-vs-3 margin ranges from **+1.8% (LFPG) to +8.2% (YSDU)** across all
five airports (DECISIONS F94) — largest where there is real structure left
to capture (YSDU, Reno), slight where three features already suffice
(LFPG). This is the same "calibrated understanding of where it helps" the
minimal method's own findings established, not a claim that more features
always help by a lot. **Raw GFS (GRIB) is not the same series as raw GFS
(Open-Meteo)** — the two sources agree closely but are not identical
(section 5.2), and they also differ in how elevation is handled: the
minimal method's baseline carries no project-applied adjustment (it is
Open-Meteo's served value), while this method's baseline carries the
project's fixed lapse-rate adjustment (SPEC 5.2, DECISIONS D48.10) — so
this section's vs-raw-GFS margins are not directly
comparable, airport for airport, to section 3's minimal-method margins; the
5-vs-3 column, computed entirely within this method on one identical
source, is the fair basis for judging what the two extra features bought.

---

## 6. Act three: the selected-features method

Sections 2–5 describe the project's first two proven methods, and their
results stand exactly as reported above. This section describes a third,
later method: five candidate physical-variable feature families tested one
at a time on top of section 5's own 5-feature GRIB baseline, all five of
them contributing an adopted feature, swept together by a mechanical
selection rule, locked once, and confirmed once on a separate, reserved
held-out
year — passing the frozen bar at all five airports, including Reno
(DECISIONS D51–D59; folded into `SPEC.md` as section 8 by session 65,
DECISIONS D59.3). **All three results are real and proven. None erases
any other** (DECISIONS D48.13, D59.3).

### 6.1 Why the programme was run

Section 5's own five-feature GRIB method (act two) passes at every
airport, but it was built from only two extra pieces of physical
information (cloud cover, wind speed) chosen ahead of time, not from a
systematic search of what else the GRIB archive can offer. A cheap
availability probe found 27 candidate variables, across five further
physical-variable families, genuinely present in the archive at the
project's own forecast lead, back to the v16 floor — radiation,
upper-air/vertical structure, moisture, pressure/synoptic and
precipitation (DECISIONS F97). This programme tests, one family at a time
and then together, whether any
of them add real skill on top of the already-proven baseline, and combines
the winners into one final, locked recipe.

### 6.2 The protocol: reserve, then select, then one look

Before any feature experiment ran, a full year — 2024-08-01 to
2025-07-31 — was reserved and locked out of every feature experiment in
code, so the eventual final set's own confirmation would be genuinely
out-of-sample (DECISIONS D51). Every family was then tested only on three
other, non-reserved training/test folds: each candidate family's own
derived feature and its raw physical fields were fit against the frozen
baseline and read for skill, robustness across folds, and a diagnostic
read at DSM (DECISIONS F98–F105); the owner reviewed each family's own
grid and decided, one family at a time, what to adopt (DECISIONS
D52–D56). All five families' own derived feature was adopted — moisture
(dew-point depression), lapse rate, shortwave radiation, pressure
tendency and precipitation (DECISIONS D52–D56). Two raw physical
variables were separately parked as candidates without being adopted
(Reno's own raw pressure-level temperatures, and relative humidity —
DECISIONS D52, D53). These seven candidates — the five adopted features
together with the two parked raw-variable options — were then swept
together on a pre-registered ladder of variants, using a mechanical
leave-one-out selection rule with a correlated-feature safeguard and a
joint sanity check (DECISIONS D57), which produced one candidate set: the
baseline plus moisture, lapse rate, radiation and pressure tendency — the
sweep's own mechanical rule dropped precipitation from the final set, and
neither parked option was adopted (DECISIONS F106, confirmed in DECISIONS
D58). The owner reviewed the full grid and selection trace and confirmed
that set unchanged (DECISIONS D58). The confirmed set was then run once, and only
once, against the reserved year (DECISIONS D58, F109) — the single
authorised look for this entire programme.

### 6.3 Result

**The confirmed set, B+D,L,R,T, passes the frozen bar at all five
airports** — it beats both raw GFS and persistence on MAE everywhere, with
no exception, on the reserved year (2024-08-01 to 2025-07-31, DECISIONS
F109):

| airport | raw GFS (GRIB) MAE | persistence MAE | B (5-feature) MAE | selected-features MAE | vs raw GFS | vs persistence | vs B |
|---|---|---|---|---|---|---|---|
| EGLC | 1.2362 | 2.2259 | 1.0861 | 1.0008 | **+19.04%** | +55.04% | +7.85% |
| LFPG | 1.4091 | 2.5233 | 1.3285 | 1.2369 | **+12.22%** | +50.98% | +6.89% |
| DSM  | 1.7043 | 4.1081 | 1.4402 | 1.4123 | **+17.13%** | +65.62% | +1.94% |
| YSDU | 1.4897 | 2.5775 | 1.3030 | 1.2643 | **+15.13%** | +50.95% | +2.97% |
| RNO  | 1.6135 | 2.7563 | 1.4272 | 1.2742 | **+21.03%** | +53.77% | +10.72% |

"Raw GFS (GRIB)" here is the elevation-adjusted GRIB temperature (SPEC 5.2,
DECISIONS D48.10).

Persistence is scored only on test days that have a previous-day
observation, while raw GFS and the models use every test day. This day
basis was pre-registered (DECISIONS D58 item 6) and is reported in
DECISIONS F109: EGLC is missing 1 day and YSDU 5 (audit-68b item 3). The
minimal method, by contrast, scores every rung on one common day set
(DECISIONS D21.8).

The secondary read also holds: airport-averaged MAE 1.2377 against plain
`B`'s own 1.3170, a **+6.02%** skill margin (DECISIONS F109). No ranking
among airports is claimed; DSM's own margin over `B` (+1.94%) was the
expected weaker case going in (DECISIONS D58 item 7's own pre-registered
expectation, drawing on F96 and F106's own DSM diagnostic), and RNO's own
margin over `B` (+10.72%) was not pre-registered.

### 6.4 Caveats — required reading before quoting this result

(DECISIONS D59.3, stated plainly, not softened):

- **(a) One year only.** Like every sealed or confirmed result in this
  project, this is a single held-out year, judged once (SPEC 5.3).
- **(b) First look at the selected set, not a first look at the
  baseline.** This is the first time the *selected* feature set
  (B+D,L,R,T) was scored on 2024-25 — but plain `B` alone was already
  scored on that same year descriptively, in an earlier, separate
  multi-year study (DECISIONS F96, D58 item 8). The feature-selection
  choices themselves (which families to add) never touched 2024-25.
- **(c) Different years — do not compare margins side by side.** This
  section's own margins are measured on the reserved year, 2024-25;
  section 5's own margins are measured on the sealed year, 2025-26. The
  two are not a like-for-like comparison.
- **(d) DSM's margin over `B` is small** (+1.94%).
- **(e) RNO's margin over `B`** (+10.72%) **was not pre-registered** and is
  descriptive only.

This method is now the project's **default recipe** for any future airport
work or pooling work (DECISIONS D59.3) — every new airport still needs its
own lock and its own test, with its looks fixed in writing in that lock
before any of its held-out values are read (SPEC 5.0, 6; DECISIONS D71.6).

### 6.5 A sixth airport: San Francisco (KSFO)

**Why KSFO.** The owner chose to test the selected-features recipe, frozen
and unchanged, at a new airport (DECISIONS D66.1, D67.1). At a new airport
neither 2024-25 nor 2025-26 had ever been scored, and the recipe was chosen
without it, so this was the cheapest truly out-of-sample test left
(DECISIONS D59.5). KSFO is the project's first coastal airport, a harder
type (DECISIONS D67.1). Its target hour, 20:00 UTC, is its local standard
noon, the same hour and lead as Reno's.

**The gate failed, and the owner kept the recipe.** Before any model is
fit, the GRIB temperature is checked against Open-Meteo's (section 5.2). At
KSFO this check failed: after the elevation adjustment, GRIB ran 3.326 °C
colder than Open-Meteo on average, most in summer, against a bar of under
1.0 °C (DECISIONS F116). A follow-up check found three things (DECISIONS
F117). The pipeline is exact: pointed at Reno, KSFO's code rebuilt Reno's
record with no difference. 37.5% of the 0.25° blend's weight at KSFO sits
on two sea points, which run much colder than the land points in summer.
And Open-Meteo documents its temperature as coming from a finer, 0.11° GFS
product, not the 0.25° product used here. The owner recorded the gate as
failed, explained by a difference between the sources, with no override,
and kept the recipe unchanged (DECISIONS D69).

**Rehearsal and lock.** KSFO was rehearsed on the 2022-23 and 2023-24
folds, not on 2024-25, because 2024-25 was one of its looks (DECISIONS
D67.4). The rehearsal was a pipeline check, not a gate. Every check
passed, and `B+D,L,R,T` beat raw GFS and persistence on both folds
(DECISIONS F118). It also fixed the column-order band at 0.0377 °C: how
far the MAE moves when only the order of the input columns changes
(DECISIONS F118.7). The recipe, the looks, the bar, the band and the
frozen script were then locked in writing, before any held-out value was
read (DECISIONS D70).

**Two looks, not one.** The five earlier airports each had one look per
method. KSFO had two pre-registered looks, each judged separately against
the frozen bar (DECISIONS D67.3). Look A trains on 2021-03-24..2024-07-31
and tests 2024-25, an exact replica of F109's fold. Look B trains on
2021-03-24..2025-07-31 and tests 2025-26; its training includes 2024-25,
by design (DECISIONS D70.3). "KSFO passes" was to be claimed only if both
looks passed. Both were run once, together (DECISIONS F119).

**Result.** MAE in °C (DECISIONS F119.3):

| look | n test | raw GFS (GRIB) MAE | persistence MAE | B MAE | selected-features MAE | vs raw GFS | vs persistence | vs B |
|---|---|---|---|---|---|---|---|---|
| A (2024-25) | 364 | 1.4263 | 1.5113 | 1.3534 | 1.2576 | **+11.83%** | +16.79% | +7.08% |
| B (2025-26) | 365 | 1.7321 | 1.7172 | 1.4654 | 1.3830 | **+20.16%** | +19.46% | +5.62% |

"Raw GFS (GRIB)" is the elevation-adjusted GRIB temperature (+0.6944 °C,
SPEC 5.2). Persistence is scored on test days with a previous-day
observation: 363 of 364 in look A, 365 of 365 in look B (DECISIONS D70.4,
F119.3).

**Both looks pass.** The overall reading is PASS, which matches the
pre-registered expectation, "pass in both years" (DECISIONS D70.8, F119).
The owner accepted it (DECISIONS D71.1). The margin over `B` is above the
column-order band in both looks: 0.0958 and 0.0824 °C against 0.0377
(DECISIONS D70.5, F119.3).

**How to read it** (DECISIONS D71.2–D71.4):
- **The headline is look A's +11.83% over raw GFS** (1.2576 vs 1.4263). It
  is the smallest of the four bar margins (DECISIONS D71.2).
- **Look B's raw-GFS year was unusually poor.** Raw GFS scored 1.7321 in
  look B, well above look A's 1.4263 and the two rehearsal folds' 1.4423
  and 1.3061 (DECISIONS F118.5). In look B, persistence (1.7172) edged raw
  GFS, so persistence was the binding half of the bar there: a margin of
  0.3342 °C (+19.46%), against 0.3491 °C (+20.16%) over raw GFS. So look
  B's +20.16% is always quoted with this point (DECISIONS D71.3).
- **KSFO's bias is not stable from year to year.** The mean-bias
  reference (raw GFS plus its average training-period bias) was worse
  than raw GFS in both looks (A 1.5000 vs 1.4263; B 1.7747 vs 1.7321),
  though it beat raw GFS on both rehearsal folds (1.3833 vs 1.4423; 1.2500
  vs 1.3061; DECISIONS F118.5, F119.3). The two looks' training means
  (look A +0.3638 °C over 1,223 rows; look B +0.1847 °C over 1,587 rows)
  imply a 2024-25 mean(obs − raw GFS) of about −0.42 °C, against about
  +0.36 °C before it. This is arithmetic on recorded values, not a new
  score. `B+D,L,R,T` still beat raw GFS in both looks. It is insight only:
  nothing was selected, tuned or changed on it (DECISIONS D71.4).

**Framing, carried by every write-up** (DECISIONS D71.5). KSFO's result is
for the recipe at a sea-mixed grid point (37.5% sea weight, DECISIONS
F117.3). It is not directly comparable with the five earlier airports,
whose reproduction gates passed. KSFO's gate is recorded as failed,
explained by a difference between the sources (DECISIONS D69). Look B's
training includes 2024-25, by design (DECISIONS D70.3). KSFO's margins are
not added to section 6.3's five-airport table or to its +6.02%
airport-averaged read.

---

## 7. Limitations and open directions

These are stated as the current honest edges of the work, not as failures.
They now apply to a project with three proven methods, not one.

- **The richer-features question at Reno is now answered, not parked, and
  upper-air information has since been tried.** The minimal method's
  finding 4 named a real ceiling: three features (forecast temperature,
  season) were not enough to beat raw GFS at an airport whose bias is
  close to a constant under large scatter. Section 5 tested whether cloud
  cover, wind speed, and a longer GRIB-sourced training window could do
  better, and they do — the 5-feature model passes at Reno, with the
  honest caveat (section 5.4) that part of its headline margin reflects a
  slightly weaker raw-GFS baseline under GRIB, and the pass remains real
  even correcting for that. What was still open at that point: whether a
  further richer feature set — a genuine terrain descriptor, upper-air
  information — would help Reno or any other airport more. **Upper-air
  information has since been tried and partly adopted**: the
  feature-selection programme (section 6) tested five candidate families,
  including upper-air/vertical temperature structure alongside moisture,
  pressure and radiation (DECISIONS F98); the single derived feature
  `lapse_rate_t2_t850` was adopted into the project's now-default recipe,
  while the three raw pressure-level temperatures were tested and not
  adopted (DECISIONS D52, D57, D58). A genuine terrain descriptor beyond
  the fixed lapse-rate elevation correction (section 5.1) remains
  untested. A terrain descriptor is now parked (DECISIONS D72.9).
- **At the five earlier airports each method rests on one year; KSFO had
  two looks — and, together, no untouched year now remains at any of the
  six airports.** The minimal and richer methods' sealed tests (sections 3 and
  5) both ran on 2025-08-01 to 2026-07-31, the sealed test year fixed by
  the project's own split dates (SPEC 4.3, finding 5, section 4). The
  selected-features method (section 6) was instead confirmed on a
  separate year, 2024-08-01 to 2025-07-31 — not part of SPEC 4.3's own
  split, but carved out of the training window and reserved specifically
  for this programme so its own single look would be genuinely
  out-of-sample (DECISIONS D51). **No untouched held-out year now remains
  at any of the five airports** (DECISIONS D59.5): the sealed test year
  has been used for the richer method's own sealed test (F94), and the
  reserved year has been used for the selected-features method's own
  confirmation (F109). KSFO's two held-out years (2024-08-01 to
  2026-07-31) are now also used, by its two looks (section 6.5; DECISIONS
  D71.1), so no untouched held-out year remains at any of the six
  airports. A further independent test year is therefore not a
  matter of re-splitting existing data — it needs either a new airport
  (never scored on either year) or a live, forward-looking year not yet
  elapsed (2026-27, DECISIONS D59.5).
- **Cross-method margin comparisons need care.** The minimal method's
  vs-raw-GFS margins (section 3) and the richer method's vs-raw-GFS margins
  (section 5) are computed against two different raw-GFS series
  (Open-Meteo vs. GRIB) that agree closely but are not identical (section
  5.2). They also differ in elevation handling as well as in source: the
  minimal method's baseline carries no project-applied adjustment (it is
  Open-Meteo's served value), while the GRIB methods' baseline carries the
  project's fixed lapse-rate adjustment (SPEC 5.2, DECISIONS D48.10).
  Reno is the one airport where this actually matters in practice
  (section 5.4's decomposition); at the other four airports the two raw
  baselines are close enough that the caveat is a formality. The
  selected-features method's own margins (section 6) add a second reason
  for care: they are measured on a different year from sections 3 and 5's
  own margins (section 6.4(c)).
- **The roadmap.** The owner has set a roadmap to a private, live daily
  tool (DECISIONS D72; SPEC 6). Next are a comparison against
  operational post-processed forecasts and a probe of other weather
  models' data (stage A), and a pre-registered forward test of the
  selected-features recipe on 2026-27, split at the GFS v17 go-live
  date (stage B). Widening the target to a full daily curve and the
  48-hour lead, correcting and blending other weather models, and the
  live product itself are later stages (C–G). Probabilistic forecasts
  follow (H). Pooling is conditional.

---

*All figures in this file are cited to their DECISIONS.md/SPEC.md source
and were checked against it when this file was written (session 30),
revised (session 44, DECISIONS F95), revised again (session 65,
DECISIONS F110), and revised after session 79 (DECISIONS F120) and after session 80 (DECISIONS F121). SPEC.md remains the source of truth for how the project
works; this file is a read-only summary of results already on record
there.*
