# RESULTS.md — the project so far, in one place

This file is a standalone technical summary. It draws only on facts already
recorded in `SPEC.md` and `DECISIONS.md` — it computes nothing new. Every
number below is cited to the DECISIONS finding it comes from, so it can be
checked against the original record. Where `SPEC.md` and this file ever
disagree, `SPEC.md` is right (CLAUDE.md, SPEC section 2).

Written after session 30, revised after session 44. As of session 44, the
project has **two** independently-tested, proven methods for correcting
GFS's local bias at an airport: a minimal three-feature method (sections
2–4 below, the project's original result) and a richer five-feature method
using a different forecast source (section 5, "act two"). The minimal
method passes at four of five airports and fails at the fifth, Reno; the
richer method passes at all five, including Reno. Both results are real
and neither erases the other (DECISIONS D48.13) — read together, they tell
a two-chapter story about what the minimal method's ceiling was and what
addressed it. Language is kept plain; jargon is defined the first time it
is used, so this can also serve as the basis for a plainer-language
write-up later without redoing the work.

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
method (section 5) passes at all five. The one airport the minimal method
fails, Reno, is itself one of this project's findings, not a flaw in it —
and the richer method's own passing result there is a second finding, not a
correction of the first.

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
(section 5.2) — so this section's vs-raw-GFS margins are not directly
comparable, airport for airport, to section 3's minimal-method margins; the
5-vs-3 column, computed entirely within this method on one identical
source, is the fair basis for judging what the two extra features bought.

---

## 6. Limitations and open directions

These are stated as the current honest edges of the work, not as failures.
They now apply to a project with two proven methods, not one.

- **The richer-features question at Reno is now answered, not parked.**
  The minimal method's finding 4 named a real ceiling: three features
  (forecast temperature, season) were not enough to beat raw GFS at an
  airport whose bias is close to a constant under large scatter. Section 5
  tested whether cloud cover, wind speed, and a longer GRIB-sourced
  training window could do better, and they do — the 5-feature model
  passes at Reno, with the honest caveat (section 5.4) that part of its
  headline margin reflects a slightly weaker raw-GFS baseline under GRIB,
  and the pass remains real even correcting for that. What is not yet
  known: whether a *further* richer feature set (a genuine terrain
  descriptor, upper-air information) would help Reno or any other airport
  more — that remains untested, not because it looks unpromising but
  because it has not been tried.
- **One shared test year, for both methods.** Every sealed-test result so
  far — under either recipe, at any airport — is drawn from the same
  twelve months (2025-08-01 to 2026-07-31). A second, independent test
  year — at any airport, under either method — would be the strongest
  single piece of further evidence about how much of the passing margins
  is model and how much is one year's weather (finding 5, section 4).
- **Cross-method margin comparisons need care.** The minimal method's
  vs-raw-GFS margins (section 3) and the richer method's vs-raw-GFS margins
  (section 5) are computed against two different raw-GFS series
  (Open-Meteo vs. GRIB) that agree closely but are not identical (section
  5.2). Reno is the one airport where this actually matters in practice
  (section 5.4's decomposition); at the other four airports the two raw
  baselines are close enough that the caveat is a formality.
- **Parked directions, not started:** blending in other forecast models
  (ECMWF, ICON, Google's WeatherNext AI model — SPEC stage 4); widening the
  target from one fixed hour to a full daily temperature curve (SPEC stage
  5); the eventual live daily product (SPEC stage 6); a further airport, or
  a genuinely second test year (SPEC's open Q30 branches). None of these
  has begun.

---

*All figures in this file are cited to their DECISIONS.md/SPEC.md source
and were checked against it when this file was written (session 30) and
revised (session 44, DECISIONS F95). SPEC.md remains the source of truth
for how the project works; this file is a read-only summary of results
already on record there.*
